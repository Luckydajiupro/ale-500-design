#!/usr/bin/env python3
"""Prove pilot_gate.py rejects bad pilot records and fake evidence.

Every case builds a temporary directory with real package files, mutates one
thing, runs the gate, and asserts the exit code. The good case is the positive
control; the fake-evidence cases prove the gate reads files, not just JSON
claims.
"""

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


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def build_package(root, direction, task_id):
    version = root / "packages" / direction / task_id.split("/")[-1] / "v1"
    base = version / "base"
    (base / "input").mkdir(parents=True)
    (base / "reference").mkdir(parents=True)
    files = {
        "input/task_brief.md": f"# {task_id}\n\nDo the task.\n",
        "input/output_contract.json": json.dumps({"root": "output", "required": ["answer.md"]}),
        "reference/answer_key.json": json.dumps({"answer": 42}),
    }
    for relative, content in files.items():
        (base / relative).write_text(content, encoding="utf-8")
    declared = []
    for relative in sorted(files):
        target = base / relative
        declared.append({
            "path": relative,
            "sha256": pilot_gate.sha256_file(target),
            "bytes": target.stat().st_size,
            "mode": "0644",
            "role": "reference" if relative.startswith("reference/") else "input",
        })
    write_json(base / "PACKAGE.json", {
        "schema_version": "ale-pkg-1.2",
        "ale_data_version": "task-data-v1.1",
        "task_id": task_id,
        "task_version": "v1",
        "files": declared,
    })
    write_json(version / "package_manifest.json", {"package_version": "ale-pkg-1.2"})
    write_json(version / "materials.json", {"materials": []})
    write_json(version / "provenance.json", {"source": "test"})
    write_json(version / "handoff.json", {"status": "ready"})
    digest, entries = pilot_gate.package_digest(version)
    return digest, len(entries)


def record(direction, task_id, letter, package_hash, file_count):
    return {
        "schema_version": "pilot-task-1.0",
        "task_id": task_id,
        "direction": direction,
        "expert": {"expert_id": "E-01", "signed_at": "2026-11-18T00:00:00Z"},
        "manual_baseline": {
            "task_id": f"{task_id}_t1",
            "started_at": "2026-11-24T00:00:00Z",
            "finished_at": "2026-11-28T00:00:00Z",
            "hours": 6.5,
            "artifacts": ["manual-notes.md"],
            "issues": [],
            "annotation_spec_version": "annot-1.0",
        },
        "platform_assisted": {
            "task_id": task_id,
            "started_at": "2026-12-08T00:00:00Z",
            "finished_at": "2026-12-12T00:00:00Z",
            "hours": 3.1,
            "form_version": "form-0.3",
            "agent_runs": 14,
            "agent_suggestions": 52,
            "agent_accepted": 0,
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
            "path": f"packages/{direction}/{task_id.split('/')[-1]}/v1",
            "package_hash": package_hash,
            "file_count": file_count,
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
            "warnings": 0,
            "report": f"validation-{direction}.json",
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
        package_hash, file_count = build_package(root, direction, task_id)
        write_json(root / f"record-{direction}.json", record(direction, task_id, letter, package_hash, file_count))
        write_json(root / f"validation-{direction}.json", {
            "validator": "ale-data-validate",
            "validator_version": "1.0.0",
            "checks": [{"code": f"L1-{i}", "status": "PASS"} for i in range(6)],
            "blockers": [],
            "warnings": [],
        })

    steps = [
        {"step": "manual_baseline", "mode": "manual", "hours": 6.5},
        {"step": "platform_assisted", "mode": "assisted", "hours": 3.1},
        {"step": "expert_confirmation", "mode": "manual", "hours": 0.5},
        {"step": "independent_review", "mode": "manual", "hours": 2.0},
        {"step": "package", "mode": "auto", "hours": 0.2},
        {"step": "validate", "mode": "auto", "hours": 0.1},
        {"step": "ingest", "mode": "auto", "hours": 0.1},
    ]
    write_json(root / "division-matrix.json", {"steps": steps})
    write_json(root / "annotation-spec.json", {"version": "1.0", "fields": ["identity", "scenario"]})
    write_json(root / "agent-report.json", {
        "details": [
            {
                "capability": capability,
                "sample_size": 3,
                "success_rate": 0.5,
                "cost_per_task": 10.0,
                "failure_modes": ["none observed"],
            }
            for capability in pilot_gate.AGENT_CAPABILITY_NAMES
        ]
    })
    write_json(root / "issues.json", {"open_blockers": 0, "fallbacks": []})
    write_json(root / "smoke.json", {"status": "PASS"})

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
                "manual": 3,
                "manual_hours": 9.0,
                "platform_hours": 3.5,
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
            "smoke": {"path": "smoke.json", "version": "1.0", "status": "PASS"},
            "issue_log": {
                "path": "issues.json",
                "version": "1.0",
                "open_blockers": 0,
                "fallbacks": [],
            },
        },
    }
    write_json(root / "index.json", index)


def read(root, name):
    return json.loads((Path(root) / name).read_text(encoding="utf-8"))


def write(root, name, value):
    write_json(Path(root) / name, value)


def run(root, acceptance=False):
    out = io.StringIO()
    with redirect_stdout(out), redirect_stderr(out):
        code = pilot_gate.check_dir(Path(root), acceptance)
    return code, out.getvalue()


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
    issues = read(root, "issues.json")
    issues["fallbacks"] = ["F1"]
    write(root, "issues.json", issues)


def fallback_without_reason(root):
    data = read(root, "record-business.json")
    data["platform_assisted"]["manual_fallbacks"] = [
        {"id": "F1", "step": "materials.license"}
    ]
    write(root, "record-business.json", data)
    index = read(root, "index.json")
    index["artifacts"]["issue_log"]["fallbacks"] = ["F1"]
    write(root, "index.json", index)
    issues = read(root, "issues.json")
    issues["fallbacks"] = ["F1"]
    write(root, "issues.json", issues)


def fake_package(root):
    set_nested(root, "record-business.json", "package", "package_hash", "f" * 64)
    set_nested(root, "record-business.json", "package", "rebuilt_hash", "f" * 64)


def empty_package(root):
    (Path(root) / "packages/business/accounting_reconcile_01/v1/base/PACKAGE.json").write_text("{}", encoding="utf-8")


def empty_validation(root):
    (Path(root) / "validation-business.json").write_text("{}", encoding="utf-8")


def failed_validation(root):
    data = read(root, "validation-business.json")
    data["checks"] = [{"code": f"L1-{i}", "status": "FAIL"} for i in range(6)]
    write(root, "validation-business.json", data)


def smoke_file_fails(root):
    write(root, "smoke.json", {"status": "FAIL"})


def missing_sidecar(root):
    (Path(root) / "packages/business/accounting_reconcile_01/v1/handoff.json").unlink()


def annotation_version_mismatch(root):
    data = read(root, "annotation-spec.json")
    data["version"] = "9.9"
    write(root, "annotation-spec.json", data)


def tamper_package(root):
    path = Path(root) / "packages/business/accounting_reconcile_01/v1/base/input/task_brief.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nlate change\n", encoding="utf-8")


def unlisted_file(root):
    path = Path(root) / "packages/business/accounting_reconcile_01/v1/base/input/extra.txt"
    path.write_text("extra", encoding="utf-8")


def empty_matrix(root):
    (Path(root) / "division-matrix.json").write_text("{}", encoding="utf-8")


def agent_report_four(root):
    data = read(root, "agent-report.json")
    data["details"] = data["details"][:4]
    write(root, "agent-report.json", data)


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
    case("T1 and T2 same instance", 1, lambda root: set_nested(root, "record-business.json", "manual_baseline", "task_id", "business_finance/accounting_reconcile_01"))
    case("T2 task id mismatch", 1, lambda root: set_nested(root, "record-business.json", "platform_assisted", "task_id", "business_finance/other_01"))
    case("fake package hash", 1, lambda root: fake_package(root))
    case("empty package manifest", 1, lambda root: empty_package(root))
    case("empty validation report", 1, lambda root: empty_validation(root))
    case("validation checks all failed", 1, lambda root: failed_validation(root))
    case("smoke file contradicts index", 1, lambda root: smoke_file_fails(root))
    case("annotation version mismatch", 1, lambda root: annotation_version_mismatch(root))
    case("missing version sidecar", 1, lambda root: missing_sidecar(root))
    case("agent auto accepted", 1, lambda root: set_nested(root, "record-business.json", "platform_assisted", "agent_accepted", 1))
    case("unlisted file", 1, lambda root: unlisted_file(root))
    case("tampered package file", 1, lambda root: tamper_package(root))
    case("index task ids mismatch", 1, lambda root: set_field(root, "index.json", "task_ids", ["business_finance/other_01", "psychology_neuro/dicom_to_bids_01", "engineering/building_energy_baseline_01"]))
    case("duplicate record task id", 1, lambda root: set_field(root, "record-neuro.json", "task_id", "business_finance/accounting_reconcile_01"))
    case("empty matrix file", 1, lambda root: empty_matrix(root))
    case("agent report file has four", 1, lambda root: agent_report_four(root))
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


if __name__ == "__main__":
    sys.exit(main())
