#!/usr/bin/env python3
"""Self test for phase2_gate.py using synthetic records in a temporary directory.

Each case writes a record, runs the gate as a subprocess with the current
interpreter, and asserts the exit code. The last case exercises --dir with one
good and one bad record so the summary path is covered too.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

GATE = Path(__file__).resolve().parent / "phase2_gate.py"


def good_record():
    return {
        "task_id": "task-001",
        "target_version": {
            "ale_commit": "a" * 40,
            "harbor_commit": "b" * 40,
        },
        "stages": {
            name: {"status": "PASS", "evidence": f"{name} evidence line"}
            for name in ("snapshot", "convert", "run", "score")
        },
    }


def run_stage_not_run():
    record = good_record()
    record["stages"]["run"]["status"] = "NOT_RUN"
    return record


def score_evidence_empty():
    record = good_record()
    record["stages"]["score"]["evidence"] = ""
    return record


def convert_stage_missing():
    record = good_record()
    del record["stages"]["convert"]
    return record


def short_ale_commit():
    record = good_record()
    record["target_version"]["ale_commit"] = "a" * 39
    return record


def empty_task_id():
    record = good_record()
    record["task_id"] = ""
    return record


def write_record(path, record):
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def invoke(mode, path):
    argv = [sys.executable, str(GATE), mode, str(path)]
    return subprocess.run(argv, capture_output=True, text=True)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        cases = [
            ("complete record", "--record", write_record(root / "complete.json", good_record()), 0),
            ("run stage status NOT_RUN", "--record", write_record(root / "not-run.json", run_stage_not_run()), 1),
            ("score stage evidence empty", "--record", write_record(root / "no-evidence.json", score_evidence_empty()), 1),
            ("convert stage missing", "--record", write_record(root / "no-convert.json", convert_stage_missing()), 1),
            ("ale_commit 39 characters", "--record", write_record(root / "short-commit.json", short_ale_commit()), 1),
            ("task_id empty", "--record", write_record(root / "no-task.json", empty_task_id()), 1),
        ]

        malformed = root / "malformed.json"
        malformed.write_text("{not json", encoding="utf-8")
        cases.append(("malformed JSON", "--record", malformed, 2))

        batch = root / "batch"
        batch.mkdir()
        write_record(batch / "01-good.json", good_record())
        write_record(batch / "02-bad.json", run_stage_not_run())
        cases.append(("dir with one good and one bad record", "--dir", batch, 1))

        failed = 0
        for name, mode, path, expected in cases:
            result = invoke(mode, path)
            if result.returncode == expected:
                print(f"PASS {name}")
                continue
            failed += 1
            print(f"FAIL {name}: expected exit {expected}, got {result.returncode}")
            if result.stderr.strip():
                print(f"  stderr: {result.stderr.strip()}")

        print(f"selftest: {len(cases)} cases, {failed} failed")
        return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
