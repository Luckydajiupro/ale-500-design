#!/usr/bin/env python3
"""Check the phase 2 pilot exit and the phase 3 platform acceptance.

A pilot record follows one task through seven segments: manual baseline,
platform-assisted annotation, expert confirmation, independent review,
ALE-data packaging, package validation, and ingest. Three records must cover
business, neuro and engineering. The engineering smoke record is checked by
phase2_gate.py and is not a substitute for this gate.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

INDEX_SCHEMA = "pilot-index-1.0"
TASK_SCHEMA = "pilot-task-1.0"
HASH64 = re.compile(r"^[0-9a-f]{64}$")
DIRECTIONS = ("business", "neuro", "engineering")
STEPS = 7
AGENT_CAPABILITIES = 5
USAGE = (
    "usage: pilot_gate.py --dir PATH "
    "[--require-platform-built] [--require-acceptance]"
)


class InputError(Exception):
    """Input that cannot be read or parsed. The caller exits 2."""


def parse_args(argv):
    path = None
    require_platform = False
    require_acceptance = False
    index = 0
    while index < len(argv):
        item = argv[index]
        if item == "--dir" and index + 1 < len(argv):
            path = Path(argv[index + 1])
            index += 2
        elif item == "--require-platform-built":
            require_platform = True
            index += 1
        elif item == "--require-acceptance":
            require_acceptance = True
            index += 1
        else:
            return None, False, False
    if path is None:
        return None, False, False
    return path, require_platform, require_acceptance


def load_json(path):
    if not path.exists():
        raise InputError(f"{path}: no such file or directory")
    if path.is_dir():
        raise InputError(f"{path}: is a directory, expected a file")
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError(f"{path}: cannot read: {exc}") from exc
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InputError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise InputError(f"{path}: top level is not an object")
    return value


def parse_time(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def nonempty_str(value):
    return isinstance(value, str) and bool(value.strip())


def nonneg_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def is_true(value):
    return value is True


def check_index(index, root):
    problems = []
    if index.get("schema_version") != INDEX_SCHEMA:
        problems.append(("index.schema_version", f"need {INDEX_SCHEMA}"))
    if not nonempty_str(index.get("pilot_id")):
        problems.append(("index.pilot_id", "missing or empty"))

    task_ids = index.get("task_ids")
    if not isinstance(task_ids, list) or len(task_ids) != 3:
        problems.append(("index.task_ids", "need exactly 3 task ids"))
        task_ids = []
    else:
        for position, task_id in enumerate(task_ids):
            if not nonempty_str(task_id):
                problems.append((f"index.task_ids[{position}]", "missing or empty"))
        if len(set(task_ids)) != 3:
            problems.append(("index.task_ids", "task ids are not unique"))

    artifacts = index.get("artifacts")
    if not isinstance(artifacts, dict):
        problems.append(("index.artifacts", "missing or not an object"))
        return problems, task_ids

    def artifact(name):
        value = artifacts.get(name)
        if not isinstance(value, dict):
            problems.append((f"index.artifacts.{name}", "missing or not an object"))
            return None
        path = value.get("path")
        if not nonempty_str(path):
            problems.append((f"index.artifacts.{name}.path", "missing or empty"))
        elif not (root / path).exists():
            problems.append((f"index.artifacts.{name}.path", f"does not exist: {path}"))
        if not nonempty_str(value.get("version")):
            problems.append((f"index.artifacts.{name}.version", "missing or empty"))
        return value

    matrix = artifact("division_matrix")
    if matrix is not None:
        if matrix.get("steps") != STEPS:
            problems.append(("index.artifacts.division_matrix.steps", f"need {STEPS}"))
        if not nonneg_int(matrix.get("assisted")) or matrix.get("assisted") < 1:
            problems.append(("index.artifacts.division_matrix.assisted", "need at least 1"))
        if not nonneg_int(matrix.get("manual")) or matrix.get("manual") < 1:
            problems.append(("index.artifacts.division_matrix.manual", "need at least 1"))

    artifact("annotation_spec")

    report = artifact("agent_report")
    if report is not None and report.get("capabilities") != AGENT_CAPABILITIES:
        problems.append(
            ("index.artifacts.agent_report.capabilities", f"need {AGENT_CAPABILITIES}")
        )

    issues = artifact("issue_log")
    if issues is not None:
        if issues.get("open_blockers") != 0:
            problems.append(("index.artifacts.issue_log.open_blockers", "need 0"))
        fallbacks = issues.get("fallbacks")
        if not isinstance(fallbacks, list):
            problems.append(("index.artifacts.issue_log.fallbacks", "need a list"))
        elif len(set(map(str, fallbacks))) != len(fallbacks):
            problems.append(("index.artifacts.issue_log.fallbacks", "duplicate ids"))

    return problems, task_ids


def check_record(record, task_ids):
    problems = []
    if record.get("schema_version") != TASK_SCHEMA:
        problems.append(("schema_version", f"need {TASK_SCHEMA}"))
    task_id = record.get("task_id")
    if not nonempty_str(task_id):
        problems.append(("task_id", "missing or empty"))
    elif task_ids and task_id not in task_ids:
        problems.append(("task_id", "not listed in index.task_ids"))

    direction = record.get("direction")
    if direction not in DIRECTIONS:
        problems.append(("direction", f"need one of {DIRECTIONS}"))

    expert = record.get("expert")
    if not isinstance(expert, dict):
        problems.append(("expert", "missing or not an object"))
        expert_id = None
    else:
        expert_id = expert.get("expert_id")
        if not nonempty_str(expert_id):
            problems.append(("expert.expert_id", "missing or empty"))
        if parse_time(expert.get("signed_at")) is None:
            problems.append(("expert.signed_at", "not an ISO timestamp"))

    manual = record.get("manual_baseline")
    manual_end = None
    if not isinstance(manual, dict):
        problems.append(("manual_baseline", "missing or not an object"))
    else:
        start = parse_time(manual.get("started_at"))
        manual_end = parse_time(manual.get("finished_at"))
        if start is None:
            problems.append(("manual_baseline.started_at", "not an ISO timestamp"))
        if manual_end is None:
            problems.append(("manual_baseline.finished_at", "not an ISO timestamp"))
        if start is not None and manual_end is not None and manual_end < start:
            problems.append(("manual_baseline.finished_at", "earlier than started_at"))
        hours = manual.get("hours")
        if not isinstance(hours, (int, float)) or isinstance(hours, bool) or hours <= 0:
            problems.append(("manual_baseline.hours", "need a positive number"))
        artifacts = manual.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            problems.append(("manual_baseline.artifacts", "need a non-empty list"))
        if not nonempty_str(manual.get("annotation_spec_version")):
            problems.append(("manual_baseline.annotation_spec_version", "missing or empty"))

    assisted = record.get("platform_assisted")
    confirmed_at = None
    if not isinstance(assisted, dict):
        problems.append(("platform_assisted", "missing or not an object"))
    else:
        start = parse_time(assisted.get("started_at"))
        end = parse_time(assisted.get("finished_at"))
        confirmed_at = parse_time(assisted.get("confirmed_at"))
        if start is None:
            problems.append(("platform_assisted.started_at", "not an ISO timestamp"))
        if end is None:
            problems.append(("platform_assisted.finished_at", "not an ISO timestamp"))
        if start is not None and end is not None and end < start:
            problems.append(("platform_assisted.finished_at", "earlier than started_at"))
        hours = assisted.get("hours")
        if not isinstance(hours, (int, float)) or isinstance(hours, bool) or hours < 0:
            problems.append(("platform_assisted.hours", "need a non-negative number"))
        if not nonempty_str(assisted.get("form_version")):
            problems.append(("platform_assisted.form_version", "missing or empty"))
        runs = assisted.get("agent_runs")
        if not nonneg_int(runs) or runs < 1:
            problems.append(("platform_assisted.agent_runs", "need a positive integer"))
        suggestions = assisted.get("agent_suggestions")
        accepted = assisted.get("agent_accepted")
        if not nonneg_int(suggestions) or suggestions < 1:
            problems.append(("platform_assisted.agent_suggestions", "need a positive integer"))
        if not nonneg_int(accepted):
            problems.append(("platform_assisted.agent_accepted", "need a non-negative integer"))
        elif nonneg_int(suggestions) and accepted > suggestions:
            problems.append(("platform_assisted.agent_accepted", "greater than suggestions"))
        if not is_true(assisted.get("expert_confirmed")):
            problems.append(("platform_assisted.expert_confirmed", "need true"))
        if confirmed_at is None:
            problems.append(("platform_assisted.confirmed_at", "not an ISO timestamp"))
        elif end is not None and confirmed_at < end:
            problems.append(("platform_assisted.confirmed_at", "earlier than finished_at"))
        if is_true(assisted.get("agent_auto_applied")):
            problems.append(("platform_assisted.agent_auto_applied", "must be false"))
        fallbacks = assisted.get("manual_fallbacks")
        if not isinstance(fallbacks, list):
            problems.append(("platform_assisted.manual_fallbacks", "need a list"))
        else:
            for position, item in enumerate(fallbacks):
                if not isinstance(item, dict):
                    problems.append(
                        (f"platform_assisted.manual_fallbacks[{position}]", "not an object")
                    )
                    continue
                if not nonempty_str(item.get("id")):
                    problems.append(
                        (f"platform_assisted.manual_fallbacks[{position}].id", "missing")
                    )
                if not nonempty_str(item.get("step")):
                    problems.append(
                        (f"platform_assisted.manual_fallbacks[{position}].step", "missing")
                    )
                if not nonempty_str(item.get("reason")):
                    problems.append(
                        (f"platform_assisted.manual_fallbacks[{position}].reason", "missing")
                    )
        if not is_true(assisted.get("all_fallbacks_declared")):
            problems.append(("platform_assisted.all_fallbacks_declared", "need true"))

    review = record.get("review")
    approved_at = None
    if not isinstance(review, dict):
        problems.append(("review", "missing or not an object"))
    else:
        approved_at = parse_time(review.get("approved_at"))
        if not is_true(review.get("independent")):
            problems.append(("review.independent", "need true"))
        reviewers = review.get("reviewers")
        if not isinstance(reviewers, list) or not reviewers:
            problems.append(("review.reviewers", "need a non-empty list"))
        else:
            for position, reviewer in enumerate(reviewers):
                if not nonempty_str(reviewer):
                    problems.append((f"review.reviewers[{position}]", "missing or empty"))
            if expert_id is not None and expert_id in reviewers:
                problems.append(("review.reviewers", "author cannot be a reviewer"))
            if len(set(reviewers)) != len(reviewers):
                problems.append(("review.reviewers", "duplicate reviewers"))
        rounds = review.get("rounds")
        if not nonneg_int(rounds) or rounds < 1:
            problems.append(("review.rounds", "need a positive integer"))
        blockers = review.get("blockers")
        resolved = review.get("resolved")
        if not nonneg_int(blockers):
            problems.append(("review.blockers", "need a non-negative integer"))
        if not nonneg_int(resolved):
            problems.append(("review.resolved", "need a non-negative integer"))
        if nonneg_int(blockers) and blockers != resolved:
            problems.append(("review.resolved", "does not equal blockers"))
        if approved_at is None:
            problems.append(("review.approved_at", "not an ISO timestamp"))
        elif confirmed_at is not None and approved_at < confirmed_at:
            problems.append(("review.approved_at", "earlier than confirmed_at"))

    package = record.get("package")
    package_hash = None
    if not isinstance(package, dict):
        problems.append(("package", "missing or not an object"))
    else:
        path = package.get("path")
        if not nonempty_str(path):
            problems.append(("package.path", "missing or empty"))
        elif not (record["_root"] / path).exists():
            problems.append(("package.path", f"does not exist: {path}"))
        package_hash = package.get("package_hash")
        if not isinstance(package_hash, str) or not HASH64.match(package_hash):
            problems.append(("package.package_hash", "need 64 lowercase hex characters"))
        rebuilt = package.get("rebuilt_hash")
        if not isinstance(rebuilt, str) or not HASH64.match(rebuilt):
            problems.append(("package.rebuilt_hash", "need 64 lowercase hex characters"))
        if not is_true(package.get("rebuild_match")):
            problems.append(("package.rebuild_match", "need true"))
        if isinstance(package_hash, str) and isinstance(rebuilt, str):
            if rebuilt != package_hash:
                problems.append(("package.rebuilt_hash", "does not equal package_hash"))
        file_count = package.get("file_count")
        if not nonneg_int(file_count) or file_count < 1:
            problems.append(("package.file_count", "need a positive integer"))
        if package.get("ale_data_version") != "task-data-v1.1":
            problems.append(("package.ale_data_version", "need task-data-v1.1"))
        if package.get("built_by") != "platform":
            problems.append(("package.built_by", "need platform"))

    validation = record.get("validation")
    if not isinstance(validation, dict):
        problems.append(("validation", "missing or not an object"))
    else:
        if not nonempty_str(validation.get("validator")):
            problems.append(("validation.validator", "missing or empty"))
        if not nonempty_str(validation.get("validator_version")):
            problems.append(("validation.validator_version", "missing or empty"))
        checks = validation.get("checks")
        passed = validation.get("passed")
        if not nonneg_int(checks) or checks < 5:
            problems.append(("validation.checks", "need at least 5"))
        if not nonneg_int(passed):
            problems.append(("validation.passed", "need a non-negative integer"))
        elif nonneg_int(checks) and passed != checks:
            problems.append(("validation.passed", "does not equal checks"))
        if validation.get("blockers") != 0:
            problems.append(("validation.blockers", "need 0"))
        if not nonneg_int(validation.get("warnings")):
            problems.append(("validation.warnings", "need a non-negative integer"))
        report = validation.get("report")
        if not nonempty_str(report):
            problems.append(("validation.report", "missing or empty"))
        elif not (record["_dir"] / report).exists():
            problems.append(("validation.report", f"does not exist: {report}"))

    ingest = record.get("ingest")
    if not isinstance(ingest, dict):
        problems.append(("ingest", "missing or not an object"))
    else:
        if not nonempty_str(ingest.get("record_id")):
            problems.append(("ingest.record_id", "missing or empty"))
        ingested_at = parse_time(ingest.get("ingested_at"))
        if ingested_at is None:
            problems.append(("ingest.ingested_at", "not an ISO timestamp"))
        elif approved_at is not None and ingested_at < approved_at:
            problems.append(("ingest.ingested_at", "earlier than review.approved_at"))
        if ingest.get("package_hash") != package_hash:
            problems.append(("ingest.package_hash", "does not equal package.package_hash"))
        count = ingest.get("asset_index_count")
        if not nonneg_int(count) or count < 1:
            problems.append(("ingest.asset_index_count", "need a positive integer"))

    return problems


def check_cross(records, index, require_acceptance):
    problems = []
    by_direction = {record.get("direction") for record in records}
    if len(set(by_direction)) != 3 or set(by_direction) != set(DIRECTIONS):
        problems.append(("records", "need exactly business, neuro and engineering"))

    validators = {
        (record.get("validation", {}).get("validator"),
         record.get("validation", {}).get("validator_version"))
        for record in records
    }
    if len(validators) != 1:
        problems.append(("records", "records use different validators"))

    if not any(len(record.get("review", {}).get("reviewers", [])) >= 2 for record in records):
        problems.append(("records", "no record has two reviewers"))

    fallback_ids = []
    for record in records:
        for item in record.get("platform_assisted", {}).get("manual_fallbacks", []):
            if isinstance(item, dict) and nonempty_str(item.get("id")):
                fallback_ids.append(item["id"])
    if len(set(fallback_ids)) != len(fallback_ids):
        problems.append(("records", "duplicate fallback ids across records"))

    declared = index.get("artifacts", {}).get("issue_log", {}).get("fallbacks", [])
    declared_set = set(map(str, declared)) if isinstance(declared, list) else set()
    if set(fallback_ids) != declared_set:
        problems.append(("records", "fallback ids do not match issue_log.fallbacks"))

    if require_acceptance:
        for record in records:
            acceptance = record.get("platform_acceptance")
            where = f"{record.get('task_id', 'record')}.platform_acceptance"
            if not isinstance(acceptance, dict):
                problems.append((where, "missing or not an object"))
                continue
            load = acceptance.get("load_test")
            if not isinstance(load, dict) or not is_true(load.get("passed")):
                problems.append((where + ".load_test", "need passed true"))
            elif load.get("concurrent_users") != 22:
                problems.append((where + ".load_test", "need 22 concurrent users"))

            permissions = acceptance.get("permission_tests")
            if not isinstance(permissions, dict):
                problems.append((where + ".permission_tests", "missing or not an object"))
            elif permissions.get("cases") != permissions.get("passed_cases"):
                problems.append(
                    (where + ".permission_tests", "passed_cases does not equal cases")
                )

            failures = acceptance.get("failure_injection")
            if not isinstance(failures, dict):
                problems.append((where + ".failure_injection", "missing or not an object"))
            elif failures.get("cases") != failures.get("passed_cases"):
                problems.append(
                    (where + ".failure_injection", "passed_cases does not equal cases")
                )

            audit = acceptance.get("audit_replay")
            if not isinstance(audit, dict) or not is_true(audit.get("passed")):
                problems.append((where + ".audit_replay", "need passed true"))

            legal = acceptance.get("legal_import")
            if not isinstance(legal, dict):
                problems.append((where + ".legal_import", "missing or not an object"))
            else:
                if not is_true(legal.get("accepted_fixture")):
                    problems.append((where + ".legal_import", "accepted_fixture not true"))
                if not is_true(legal.get("rejected_fixture")):
                    problems.append((where + ".legal_import", "rejected_fixture not true"))

    return problems


def check_dir(path, require_platform, require_acceptance):
    if not path.exists():
        print(f"pilot_gate: {path}: no such directory", file=sys.stderr)
        return 2
    if not path.is_dir():
        print(f"pilot_gate: {path}: not a directory", file=sys.stderr)
        return 2

    index_path = path / "index.json"
    if not index_path.exists():
        print(f"pilot_gate: {index_path}: missing", file=sys.stderr)
        return 2
    try:
        index = load_json(index_path)
    except InputError as exc:
        print(f"pilot_gate: {exc}", file=sys.stderr)
        return 2

    problems, task_ids = check_index(index, path)
    files = sorted(
        (item for item in path.glob("record-*.json") if item.is_file()),
        key=lambda item: item.name,
    )
    if len(files) != 3:
        problems.append(("records", f"need 3 record files, found {len(files)}"))

    records = []
    for file in files:
        try:
            record = load_json(file)
        except InputError as exc:
            print(f"pilot_gate: {exc}", file=sys.stderr)
            return 2
        record["_dir"] = path
        record["_root"] = path
        records.append(record)
        problems.extend((f"{file.name}.{where}", reason) for where, reason in check_record(record, task_ids))

    if len(records) == 3:
        problems.extend(check_cross(records, index, require_acceptance))

    if problems:
        for where, reason in problems:
            print(f"FAIL {where}: {reason}")
        return 1

    for record in records:
        print(f"{record['task_id']} pilot record: 7/7 segments, package ingested")
    print(f"pilot gate: 3/3 records passed")
    return 0


def main():
    path, require_platform, require_acceptance = parse_args(sys.argv[1:])
    if path is None:
        print(USAGE, file=sys.stderr)
        return 2
    return check_dir(path, require_platform, require_acceptance)


if __name__ == "__main__":
    sys.exit(main())
