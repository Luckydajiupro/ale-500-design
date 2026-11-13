#!/usr/bin/env python3
"""Prove pilot_gate.py rejects bad pilot records.

Every case builds a temporary directory, mutates one field, runs the gate, and
asserts the exit code. The good case is also the positive control.
"""

import copy
import io
import json
import shutil
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pilot_gate


TASKS = (
    ("business", "business_finance/accounting_reconcile_01", "a"),
    ("neuro", "psychology_neuro/dicom_to_bids_01", "b"),
    ("engineering", "engineering/building_energy_baseline_01", "c"),
)


def record(direction, task_id, letter):
    package_hash = letter * 64
    return {
        "schema_version": "pilot-task-1.0",
        "task_id": task_id,
        "direction": direction,
        "expert": {"expert_id": "E-01", "signed_at": "2026-11-18T00:00:00Z"},
        "manual_baseline": {
            "started_at": "2026-11-24T00:00:00Z",
            "finished_at": "2026-11-28T00:00:00Z",
            "hours": 6.5,
            "artifacts": ["manual-notes.md"],
            "issues": [],
            "annotation_spec_version": "annot-1.0",
        },
        "platform_assisted": {
            "started_at": "2026-12-08T00:00:00Z",
            "finished_at": "2026-12-12T00:00:00Z",
            "hours": 3.1,
            "form_version": "form-0.3",
            "agent_runs": 14,
            "agent_suggestions": 52,
            "agent_accepted": 31,
            "expert_confirmed": True,
            "confirmed_at": "2026-12-12T01:00:00Z",
            "manual_fallbacks": [],
            "all_fallbacks_declared": True,
        },
        "review": {
            "reviewers": ["R-01", "R-02"],
            "independent": True,
            "rounds": 2,
            "blockers": 3,
            "resolved": 3,
            "approved_at": "2026-12-18T00:00:00Z",
        },
        "package": {
            "path": f"packages/{direction}/{task_id.split('/')[-1]}",
            "package_hash": package_hash,
            "file_count": 42,
            "ale_data_version": "task-data-v1.1",
            "built_by": "platform",
            "rebuilt_hash": package_hash,
            "rebuild_match": True,
        },
        "validation": {
            "validator": "ale-data-validate",
            "validator_version": "1.0.0",
            "checks": 6,
            "passed": 6,
            "blockers": 0,
            "warnings": 1,
            "report": "validation.json",
        },
        "ingest": {
            "record_id": f"T-20261222-{direction}",
            "ingested_at": "2026-12-22T00:00:00Z",
            "package_hash": package_hash,
            "asset_index_count": 12,
        },
    }


def build(root):
    root = Path(root)
    for direction, task_id, letter in TASKS:
        package = root / "packages" / direction / task_id.split("/")[-1]
        package.mkdir(parents=True)
        (package / "PACKAGE.json").write_text("{}", encoding="utf-8")
        (root / "validation.json").write_text("{}", encoding="utf-8")
        path = root / f"record-{direction}.json"
        path.write_text(json.dumps(record(direction, task_id, letter)), encoding="utf-8")

    index = {
        "schema_version": "pilot-index-1.0",
        "pilot_id": "s2-pilot-2026-11",
        "task_ids": [task[1] for task in TASKS],
        "artifacts": {
            "division_matrix": {
                "path": "division-matrix.json",
                "version": "1.0",
                "steps": 7,
                "assisted": 1,
                "manual": 1,
                "manual_hours": 30.0,
                "platform_hours": 12.0,
            },
            "annotation_spec": {"path": "annotation-spec.json", "version": "1.0"},
            "agent_report": {
                "path": "agent-report.json",
                "version": "1.0",
                "capabilities": 5,
                "details": [
                    {
                        "capability": capability,
                        "sample_size": 3,
                        "success_rate": 0.5,
                        "cost_per_task": 10.0,
                        "failure_modes": ["none observed"],
                    }
                    for capability in pilot_gate.AGENT_CAPABILITY_NAMES
                ],
            },
            "smoke": {
                "path": "smoke.json",
                "version": "1.0",
                "status": "PASS",
            },
            "issue_log": {
                "path": "issues.json",
                "version": "1.0",
                "open_blockers": 0,
                "fallbacks": [],
            },
        },
    }
    (root / "index.json").write_text(json.dumps(index), encoding="utf-8")
    (root / "division-matrix.json").write_text("{}", encoding="utf-8")
    (root / "annotation-spec.json").write_text("{}", encoding="utf-8")
    (root / "agent-report.json").write_text("{}", encoding="utf-8")
    (root / "issues.json").write_text("{}", encoding="utf-8")
    (root / "smoke.json").write_text("{}", encoding="utf-8")


def read(root, name):
    return json.loads((Path(root) / name).read_text(encoding="utf-8"))


def write(root, name, value):
    (Path(root) / name).write_text(json.dumps(value), encoding="utf-8")


def run(root, acceptance=False):
    out = io.StringIO()
    with redirect_stdout(out), redirect_stderr(out):
        code = pilot_gate.check_dir(Path(root), False, acceptance)
    return code, out.getvalue()


def main():
    cases = []

    def case(name, expected, mutate, acceptance=False):
        cases.append((name, expected, mutate, acceptance))

    case("good", 0, lambda root: None)
    case("good with declared fallback", 0, lambda root: declare_fallback(root))
    case("two records", 1, lambda root: (Path(root) / "record-neuro.json").unlink())
    case("four records", 1, lambda root: shutil.copy(Path(root) / "record-business.json", Path(root) / "record-extra.json"))
    case("duplicate direction", 1, lambda root: set_field(root, "record-neuro.json", "direction", "business"))
    case("missing manual baseline", 1, lambda root: drop_field(root, "record-business.json", "manual_baseline"))
    case("expert not confirmed", 1, lambda root: set_nested(root, "record-business.json", "platform_assisted", "expert_confirmed", False))
    case("fallback not declared", 1, lambda root: set_nested(root, "record-business.json", "platform_assisted", "all_fallbacks_declared", False))
    case("fallback missing reason", 1, lambda root: fallback_without_reason(root))
    case("reviewer is author", 1, lambda root: set_nested(root, "record-business.json", "review", "reviewers", ["E-01"]))
    case("short package hash", 1, lambda root: set_nested(root, "record-business.json", "package", "package_hash", "a" * 39))
    case("package built by hand", 1, lambda root: set_nested(root, "record-business.json", "package", "built_by", "manual"))
    case("rebuild mismatch", 1, lambda root: set_nested(root, "record-business.json", "package", "rebuilt_hash", "d" * 64))
    case("validation blocker", 1, lambda root: set_nested(root, "record-business.json", "validation", "blockers", 1))
    case("ingest hash mismatch", 1, lambda root: set_nested(root, "record-business.json", "ingest", "package_hash", "d" * 64))
    case("ingest before approval", 1, lambda root: set_nested(root, "record-business.json", "ingest", "ingested_at", "2026-12-17T00:00:00Z"))
    case("matrix has six steps", 1, lambda root: set_nested(root, "index.json", "artifacts", "division_matrix", {"path": "division-matrix.json", "version": "1.0", "steps": 6, "assisted": 1, "manual": 1}))
    case("agent report has four capabilities", 1, lambda root: set_nested(root, "index.json", "artifacts", "agent_report", {"path": "agent-report.json", "version": "1.0", "capabilities": 4}))
    case("matrix missing hours", 1, lambda root: set_artifact(root, "division_matrix", {"path": "division-matrix.json", "version": "1.0", "steps": 7, "assisted": 1, "manual": 1}))
    case("agent report missing details", 1, lambda root: set_artifact(root, "agent_report", {"path": "agent-report.json", "version": "1.0", "capabilities": 5}))
    case("smoke failed", 1, lambda root: set_artifact(root, "smoke", {"path": "smoke.json", "version": "1.0", "status": "FAIL"}))
    case("smoke skipped without reason", 1, lambda root: set_artifact(root, "smoke", {"path": "smoke.json", "version": "1.0", "status": "SKIP"}))
    case("stage three mode needs acceptance", 1, lambda root: None, acceptance=True)
    case("bad json", 2, lambda root: (Path(root) / "record-business.json").write_text("{", encoding="utf-8"))

    failures = 0
    for name, expected, mutate, acceptance in cases:
        with tempfile.TemporaryDirectory() as tmp:
            build(tmp)
            mutate(tmp)
            code, output = run(tmp, acceptance)
            ok = code == expected
            print(f"{'PASS' if ok else 'FAIL'} {name}: exit {code}, expected {expected}")
            if not ok:
                print(output)
                failures += 1

    print(f"pilot gate selftest: {len(cases) - failures}/{len(cases)} passed")
    return 0 if failures == 0 else 1


def set_field(root, name, field, value):
    data = read(root, name)
    data[field] = value
    write(root, name, data)


def drop_field(root, name, field):
    data = read(root, name)
    data.pop(field, None)
    write(root, name, data)


def set_nested(root, name, parent, field, value):
    data = read(root, name)
    if name == "index.json" and parent == "artifacts":
        key = field
        if isinstance(value, dict):
            data["artifacts"][key] = value
        else:
            data["artifacts"][key][field] = value
    else:
        data[parent][field] = value
    write(root, name, data)


def set_artifact(root, name, value):
    data = read(root, "index.json")
    data["artifacts"][name] = value
    write(root, "index.json", data)


def declare_fallback(root):
    data = read(root, "record-business.json")
    data["platform_assisted"]["manual_fallbacks"] = [
        {"id": "F1", "step": "materials.license", "reason": "not in form yet"}
    ]
    write(root, "record-business.json", data)
    index = read(root, "index.json")
    index["artifacts"]["issue_log"]["fallbacks"] = ["F1"]
    write(root, "index.json", index)


def fallback_without_reason(root):
    data = read(root, "record-business.json")
    data["platform_assisted"]["manual_fallbacks"] = [
        {"id": "F1", "step": "materials.license"}
    ]
    write(root, "record-business.json", data)
    index = read(root, "index.json")
    index["artifacts"]["issue_log"]["fallbacks"] = ["F1"]
    write(root, "index.json", index)


if __name__ == "__main__":
    sys.exit(main())
