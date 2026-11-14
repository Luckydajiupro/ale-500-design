#!/usr/bin/env python3
"""Prove or disprove the candidate package hash rules on a throwaway package.

The script builds the same content twice with different build clocks, then
checks four things:

1. native_hash is stable across rebuilds and sensitive to a content byte.
2. package_hash is stable when build clocks are excluded from the payload.
3. a naive hash that includes its own digest is self-referential.
4. the candidate hash excludes PACKAGE.json from native_hash and keeps the
   executable mode in the manifest.

It writes docs/data/wave2-hash-poc-results.csv and exits non-zero on failure.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import stat
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/data/wave2-hash-poc-results.csv"

STABLE_PACKAGE_FIELDS = (
    "schema_version",
    "ale_data_version",
    "task_id",
    "task_version",
    "domain_code",
    "subdomain_code",
    "entrypoints",
    "deliverables",
    "oracle",
    "verification",
    "license",
    "pii",
    "provenance",
)
UNSTABLE_FIELDS = ("built_at", "built_by", "package_hash", "hashes")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_entry(base: Path, rel: str, role: str) -> Dict[str, Any]:
    path = base / rel
    mode = stat.S_IMODE(path.stat().st_mode)
    return {
        "path": rel,
        "bytes": path.stat().st_size,
        "mode": "0%03o" % mode,
        "role": role,
        "sha256": sha256_file(path),
    }


def native_hash(entries: Sequence[Mapping[str, Any]]) -> str:
    ordered = sorted((dict(item) for item in entries), key=lambda item: item["path"])
    return sha256_bytes(canonical(ordered).encode("utf-8"))


def package_hash(native: str, package: Mapping[str, Any], sidecars: Mapping[str, str]) -> str:
    projection = {key: package[key] for key in STABLE_PACKAGE_FIELDS if key in package}
    payload = {"native_hash": native, "package": projection, "sidecars": dict(sorted(sidecars.items()))}
    return sha256_bytes(canonical(payload).encode("utf-8"))


def naive_package_hash(native: str, package: Mapping[str, Any], sidecars: Mapping[str, str]) -> str:
    payload = {"native_hash": native, "package": dict(package), "sidecars": dict(sorted(sidecars.items()))}
    return sha256_bytes(canonical(payload).encode("utf-8"))


def build(base: Path, built_at: str, built_by: str = "platform") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    (base / "input").mkdir(parents=True)
    (base / "software").mkdir()
    (base / "reference").mkdir()
    (base / "input" / "brief.md").write_text("# Brief\n\nDo the task.\n", encoding="utf-8")
    (base / "software" / "run.sh").write_text("#!/bin/sh\necho ok\n", encoding="utf-8")
    os.chmod(base / "software" / "run.sh", 0o755)
    (base / "reference" / "answer.json").write_text('{"answer": 42}\n', encoding="utf-8")

    entries = [
        file_entry(base, "input/brief.md", "input"),
        file_entry(base, "software/run.sh", "software"),
        file_entry(base, "reference/answer.json", "reference"),
    ]
    native = native_hash(entries)
    package = {
        "schema_version": "ale-pkg-1.2",
        "ale_data_version": "task-data-v1.1",
        "task_id": "engineering/hash_poc",
        "task_version": 1,
        "domain_code": "engineering",
        "subdomain_code": "software_eng",
        "entrypoints": {"brief": "input/brief.md"},
        "deliverables": [{"path": "answer.json", "format": "json"}],
        "oracle": {"required": True, "kind": "independent_oracle"},
        "verification": {"mode": "deterministic", "artifacts": [{"role": "answer_key", "path": "reference/answer.json"}]},
        "license": {"type": "cc_by", "redistribution": True},
        "pii": {"level": "none"},
        "provenance": {"author_type": "human", "sources": []},
        "files": entries,
        "hashes": {"native_hash": native},
        "built_by": built_by,
        "built_at": built_at,
        "package_hash": "",
    }
    sidecars = {}
    for name in ("package_manifest.json", "materials.json", "provenance.json", "handoff.json"):
        sidecars[name] = sha256_bytes(("%s:%s" % (name, "stable-content")).encode("utf-8"))
    candidate = package_hash(native, package, sidecars)
    package["package_hash"] = candidate
    return package, sidecars


def main() -> int:
    rows: List[Dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="ale-hash-poc-") as tmp:
        first = Path(tmp) / "first" / "base"
        second = Path(tmp) / "second" / "base"
        first.mkdir(parents=True)
        second.mkdir(parents=True)
        pkg1, side1 = build(first, "2026-11-14T08:00:00Z")
        pkg2, side2 = build(second, "2026-11-14T09:30:00Z")
        native1 = pkg1["hashes"]["native_hash"]
        native2 = pkg2["hashes"]["native_hash"]
        cand1 = pkg1["package_hash"]
        cand2 = pkg2["package_hash"]

        rows.append({"test": "native-stable", "check": "same content, different build clock", "expected": native1, "actual": native2, "pass": "yes" if native1 == native2 else "no", "evidence": "native_hash ignores PACKAGE.json and clocks"})
        rows.append({"test": "package-stable", "check": "stable fields only", "expected": cand1, "actual": cand2, "pass": "yes" if cand1 == cand2 else "no", "evidence": "built_at and built_by are outside package_hash payload"})
        rows.append({"test": "mode-kept", "check": "software/run.sh mode", "expected": "0755", "actual": pkg1["files"][1]["mode"], "pass": "yes" if pkg1["files"][1]["mode"] == "0755" else "no", "evidence": "manifest keeps executable bit"})

        naive1 = naive_package_hash(native1, pkg1, side1)
        pkg1["package_hash"] = naive1
        naive_again = naive_package_hash(native1, pkg1, side1)
        rows.append({"test": "self-reference", "check": "naive hash includes package_hash field", "expected": "different digest on second pass", "actual": "different" if naive1 != naive_again else "same", "pass": "yes" if naive1 != naive_again else "no", "evidence": "the digest changes when written back into the hashed bytes"})

        pkg3 = json.loads(json.dumps(pkg1))
        pkg3["verification"] = dict(pkg3["verification"], mode="judge")
        moved = package_hash(native1, pkg3, side1)
        rows.append({"test": "content-sensitive", "check": "verification mode changes package_hash", "expected": "different digest", "actual": "different" if moved != cand1 else "same", "pass": "yes" if moved != cand1 else "no", "evidence": "a semantic contract change moves the package hash"})

        third = Path(tmp) / "third" / "base"
        shutil.copytree(first, third)
        (third / "input" / "brief.md").write_text("# Brief\n\nDo the task!\n", encoding="utf-8")
        entries = [file_entry(third, rel, role) for rel, role in (("input/brief.md", "input"), ("software/run.sh", "software"), ("reference/answer.json", "reference"))]
        changed_native = native_hash(entries)
        rows.append({"test": "content-sensitive-native", "check": "one byte changes native_hash", "expected": "different digest", "actual": "different" if changed_native != native1 else "same", "pass": "yes" if changed_native != native1 else "no", "evidence": "native_hash covers path, bytes, mode, role and sha256"})

        clocked = dict(side1)
        clocked["package_manifest.json"] = sha256_bytes(("package_manifest.json:%s" % "2026-11-14T09:30:00Z").encode("utf-8"))
        clocked_digest = package_hash(native1, pkg1, clocked)
        rows.append({"test": "sidecar-clock", "check": "build clock inside a sidecar", "expected": "different digest", "actual": "different" if clocked_digest != cand1 else "same", "pass": "yes" if clocked_digest != cand1 else "no", "evidence": "clocks must stay out of sidecar bytes or be derived from the snapshot"})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["test", "check", "expected", "actual", "pass", "evidence"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    failed = [row for row in rows if row["pass"] != "yes"]
    for row in rows:
        print("%s %s: %s" % ("PASS" if row["pass"] == "yes" else "FAIL", row["test"], row["evidence"]))
    print("%d checks, %d failed, results: %s" % (len(rows), len(failed), OUT))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
