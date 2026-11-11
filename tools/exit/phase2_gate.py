#!/usr/bin/env python3
"""Check the phase 2 exit condition: one record from snapshot to score.

Phase 2 is technical feasibility, and its exit is a run record proving that one
task went snapshot to convert to run to score. A record is a JSON object with a
task id, the frozen ALE and Harbor commits, and the four stages, each carrying a
status and evidence. The gate passes only when every stage says PASS with
evidence and both commits are full lowercase hex hashes.
"""

import json
import re
import sys
from pathlib import Path

STAGES = ("snapshot", "convert", "run", "score")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
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


def check_stages(record):
    problems = []
    stages = record.get("stages")
    if not isinstance(stages, dict):
        return [("stages", "missing or not an object")]

    for name in STAGES:
        stage = stages.get(name)
        if not isinstance(stage, dict):
            problems.append((f"stages.{name}", "missing"))
            continue
        status = stage.get("status")
        if status != "PASS":
            actual = "missing" if status is None else str(status)
            problems.append((f"stages.{name}.status", f"status is {actual}"))
        evidence = stage.get("evidence")
        if not isinstance(evidence, str) or not evidence.strip():
            problems.append((f"stages.{name}.evidence", "evidence is missing or empty"))
    return problems


def check_target(record):
    problems = []
    target = record.get("target_version")
    if not isinstance(target, dict):
        return [("target_version", "missing or not an object")]

    for key in ("ale_commit", "harbor_commit"):
        value = target.get(key)
        if not isinstance(value, str) or not COMMIT.match(value):
            actual = "missing" if value is None else repr(value)
            problems.append((f"target_version.{key}", f"not 40 lowercase hex characters: {actual}"))
    return problems


def check_task_id(record):
    task_id = record.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        return [("task_id", "missing or empty")]
    return []


def check_record(record):
    problems = []
    problems.extend(check_stages(record))
    problems.extend(check_target(record))
    problems.extend(check_task_id(record))
    return problems


def pass_line(record):
    return f"{record['task_id'].strip()} {len(STAGES)}/{len(STAGES)} stages PASS"


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

    print(f"phase 2 gate: {pass_line(record)}")
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
        print(f"{file.name} phase 2 gate: {pass_line(record)}")

    print(f"phase 2 gate: {passed}/{len(files)} records passed")
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
