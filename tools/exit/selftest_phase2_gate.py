#!/usr/bin/env python3
"""Self test for phase2_gate.py using synthetic smoke records."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

GATE = Path(__file__).resolve().parent / "phase2_gate.py"


def good_record():
    return {
        "task_id": "business_finance/accounting_reconcile_01",
        "ale_data_version": "task-data-v1.1",
        "adapter": "harbor",
        "adapter_commit": "a" * 40,
        "stages": {
            name: {"status": "PASS", "evidence": f"{name} evidence line"}
            for name in ("package", "validate", "convert", "run", "score")
        },
    }


def validate_fails():
    record = good_record()
    record["stages"]["validate"]["status"] = "FAIL"
    return record


def skip_without_reason():
    record = good_record()
    record["stages"]["convert"] = {"status": "SKIP"}
    return record


def no_adapter_but_run_passes():
    record = good_record()
    record["adapter"] = "none"
    record["adapter_commit"] = ""
    return record


def convert_fails():
    record = good_record()
    record["stages"]["convert"] = {"status": "FAIL", "blocking": True}
    return record


def convert_fails_nonblocking():
    record = good_record()
    record["stages"]["convert"] = {
        "status": "FAIL",
        "blocking": False,
        "reason": "optional adapter missing",
    }
    return record


def convert_fails_nonblocking_no_reason():
    record = good_record()
    record["stages"]["convert"] = {"status": "FAIL", "blocking": False}
    return record


def write_record(path, record):
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def invoke(mode, path):
    return subprocess.run(
        [sys.executable, str(GATE), mode, str(path)],
        capture_output=True,
        text=True,
    )


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        cases = []

        cases.append(
            ("complete record", "--record", write_record(root / "complete.json", good_record()), 0)
        )

        package_missing = good_record()
        del package_missing["stages"]["package"]
        cases.append(
            ("package stage missing", "--record", write_record(root / "no-package.json", package_missing), 1)
        )
        cases.append(
            ("validate fails", "--record", write_record(root / "validate-fail.json", validate_fails()), 1)
        )
        cases.append(
            ("skip without reason", "--record", write_record(root / "skip-no-reason.json", skip_without_reason()), 1)
        )
        cases.append(
            ("adapter none but run passes", "--record", write_record(root / "none-run.json", no_adapter_but_run_passes()), 1)
        )
        cases.append(
            ("convert blocking fail", "--record", write_record(root / "convert-fail.json", convert_fails()), 1)
        )
        cases.append(
            (
                "convert nonblocking fail",
                "--record",
                write_record(root / "convert-fail-ok.json", convert_fails_nonblocking()),
                0,
            )
        )
        cases.append(
            (
                "convert nonblocking fail no reason",
                "--record",
                write_record(root / "convert-fail-no-reason.json", convert_fails_nonblocking_no_reason()),
                1,
            )
        )

        empty_task = good_record()
        empty_task["task_id"] = ""
        cases.append(
            ("task id empty", "--record", write_record(root / "no-task.json", empty_task), 1)
        )

        wrong_version = good_record()
        wrong_version["ale_data_version"] = "task-data-v1.0"
        cases.append(
            ("wrong ale-data version", "--record", write_record(root / "wrong-version.json", wrong_version), 1)
        )

        malformed = root / "malformed.json"
        malformed.write_text("{not json", encoding="utf-8")
        cases.append(("malformed JSON", "--record", malformed, 2))

        two = root / "two"
        two.mkdir()
        for index in range(2):
            write_record(two / f"{index:02d}-good.json", good_record())
        cases.append(("dir with two records", "--dir", two, 0))

        three = root / "three"
        three.mkdir()
        for index in range(3):
            write_record(three / f"{index:02d}-good.json", good_record())
        cases.append(("dir with three records", "--dir", three, 0))

        four = root / "four"
        four.mkdir()
        for index in range(4):
            write_record(four / f"{index:02d}-good.json", good_record())
        cases.append(("dir with four records", "--dir", four, 1))

        failed = 0
        for name, mode, path, expected in cases:
            result = invoke(mode, path)
            if result.returncode == expected:
                print(f"PASS {name}")
                continue
            failed += 1
            print(f"FAIL {name}: expected exit {expected}, got {result.returncode}")
            if result.stdout.strip():
                print(f"  stdout: {result.stdout.strip()}")
            if result.stderr.strip():
                print(f"  stderr: {result.stderr.strip()}")

        print(f"phase2 gate selftest: {len(cases)} cases, {failed} failed")
        return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
