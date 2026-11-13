#!/usr/bin/env python3
"""Check the phase 2 engineering smoke record.

This is not a stage exit. Phase 2 exits on three pilot records that go from
manual annotation to an ingested ALE-data package; those are checked by
pilot_gate.py. This gate only proves the package can be parsed, the fields can
be mapped, and a small number of formats can be converted.

A smoke record is a JSON object with a task id, an ALE-data version, an adapter
name, and up to five stages. package and validate are required and must PASS
with evidence. convert, run and score are optional: they may PASS, SKIP or FAIL.
FAIL needs a blocking flag; only blocking=true fails the record, and both SKIP
and non-blocking FAIL need a reason. When the adapter is none, run and score
must be SKIP.
"""

import json
import re
import sys
from pathlib import Path

REQUIRED = ("package", "validate")
OPTIONAL = ("convert", "run", "score")
ADAPTERS = ("harbor", "old", "none")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
MAX_RECORDS = 3
USAGE = "usage: phase2_gate.py --record PATH | --dir PATH"


class InputError(Exception):
    """Input that cannot be read or parsed. The caller exits 2."""


def parse_args(argv):
    if len(argv) == 2 and argv[0] in ("--record", "--dir"):
        return argv[0], Path(argv[1])
    return None, None


def load(path):
    if not path.exists():
        raise InputError(f"{path}: no such file or directory")
    if path.is_dir():
        raise InputError(f"{path}: is a directory, expected a record file")
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError(f"{path}: cannot read: {exc}") from exc
    try:
        record = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InputError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(record, dict):
        raise InputError(f"{path}: top level is not an object")
    return record


def check_stages(record, adapter):
    problems = []
    stages = record.get("stages")
    if not isinstance(stages, dict):
        return [("stages", "missing or not an object")]

    for name in REQUIRED:
        stage = stages.get(name)
        if not isinstance(stage, dict):
            problems.append((f"stages.{name}", "missing"))
            continue
        if stage.get("status") != "PASS":
            actual = stage.get("status", "missing")
            problems.append((f"stages.{name}.status", f"status is {actual}, need PASS"))
        evidence = stage.get("evidence")
        if not isinstance(evidence, str) or not evidence.strip():
            problems.append((f"stages.{name}.evidence", "evidence is missing or empty"))

    for name in OPTIONAL:
        stage = stages.get(name)
        if stage is None:
            if adapter == "none" and name in ("run", "score"):
                problems.append((f"stages.{name}", "adapter is none, need SKIP with reason"))
            continue
        if not isinstance(stage, dict):
            problems.append((f"stages.{name}", "not an object"))
            continue
        status = stage.get("status")
        if status == "FAIL":
            blocking = stage.get("blocking")
            if not isinstance(blocking, bool):
                problems.append((f"stages.{name}.blocking", "FAIL needs blocking true or false"))
            elif blocking:
                problems.append((f"stages.{name}.status", "blocking FAIL"))
            else:
                reason = stage.get("reason")
                if not isinstance(reason, str) or not reason.strip():
                    problems.append((f"stages.{name}.reason", "non-blocking FAIL needs a reason"))
            if adapter == "none" and name in ("run", "score"):
                problems.append((f"stages.{name}.status", "adapter is none, need SKIP"))
        elif status == "SKIP":
            reason = stage.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                problems.append((f"stages.{name}.reason", "SKIP needs a non-empty reason"))
            if adapter == "none" and name in ("run", "score"):
                continue
        elif status == "PASS":
            evidence = stage.get("evidence")
            if not isinstance(evidence, str) or not evidence.strip():
                problems.append((f"stages.{name}.evidence", "evidence is missing or empty"))
            if adapter == "none" and name in ("run", "score"):
                problems.append((f"stages.{name}.status", "adapter is none, need SKIP"))
        else:
            actual = "missing" if status is None else str(status)
            problems.append((f"stages.{name}.status", f"status is {actual}"))
    return problems


def check_target(record):
    problems = []
    version = record.get("ale_data_version")
    if version != "task-data-v1.1":
        problems.append(("ale_data_version", f"is {version!r}, need 'task-data-v1.1'"))

    adapter = record.get("adapter")
    if adapter not in ADAPTERS:
        problems.append(("adapter", f"is {adapter!r}, need one of {ADAPTERS}"))
        return problems

    if adapter != "none":
        value = record.get("adapter_commit")
        if not isinstance(value, str) or not COMMIT.match(value):
            actual = "missing" if value is None else repr(value)
            problems.append(("adapter_commit", f"not 40 lowercase hex characters: {actual}"))
    return problems


def check_task_id(record):
    task_id = record.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        return [("task_id", "missing or empty")]
    return []


def check_record(record):
    problems = []
    problems.extend(check_task_id(record))
    problems.extend(check_target(record))
    adapter = record.get("adapter")
    problems.extend(check_stages(record, adapter))
    return problems


def stage_counts(record):
    stages = record.get("stages") if isinstance(record.get("stages"), dict) else {}
    passed = sum(1 for name in REQUIRED if stages.get(name, {}).get("status") == "PASS")
    skipped = sum(
        1
        for name in OPTIONAL
        if stages.get(name, {}).get("status") == "SKIP"
    )
    return passed, skipped


def pass_line(record):
    passed, skipped = stage_counts(record)
    return f"{record['task_id'].strip()} {passed}/{len(REQUIRED)} required PASS, {skipped} SKIP"


def check_one(path):
    try:
        record = load(path)
    except InputError as exc:
        print(f"phase2_gate: {exc}", file=sys.stderr)
        return 2

    problems = check_record(record)
    if problems:
        for where, reason in problems:
            print(f"FAIL {path.name} {where}: {reason}")
        return 1

    print(f"phase 2 smoke: {pass_line(record)}")
    return 0


def check_dir(path):
    if not path.exists():
        print(f"phase2_gate: {path}: no such directory", file=sys.stderr)
        return 2
    if not path.is_dir():
        print(f"phase2_gate: {path}: not a directory", file=sys.stderr)
        return 2

    files = sorted(
        (item for item in path.glob("*.json") if item.is_file()),
        key=lambda item: item.name,
    )
    if not files:
        print("FAIL dir: no record files")
        return 1
    if len(files) > MAX_RECORDS:
        print(f"FAIL dir: {len(files)} record files, need 1 to {MAX_RECORDS}")
        return 1

    passed = 0
    for file in files:
        try:
            record = load(file)
        except InputError as exc:
            print(f"phase2_gate: {exc}", file=sys.stderr)
            return 2

        problems = check_record(record)
        if problems:
            for where, reason in problems:
                print(f"FAIL {file.name} {where}: {reason}")
            continue

        passed += 1
        print(f"{file.name} phase 2 smoke: {pass_line(record)}")

    print(f"phase 2 smoke: {passed}/{len(files)} records passed")
    return 0 if passed == len(files) else 1


def main():
    mode, path = parse_args(sys.argv[1:])
    if mode is None:
        print(USAGE, file=sys.stderr)
        return 2
    if mode == "--record":
        return check_one(path)
    return check_dir(path)


if __name__ == "__main__":
    sys.exit(main())
