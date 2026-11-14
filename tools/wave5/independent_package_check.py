#!/usr/bin/env python3
"""Independent implementation of the candidate package hash.

This file deliberately does not import ``platform.contracts.package_contract``.
It is a second implementation of the same written rule, used to catch a change
that makes the platform agree with itself but not with the frozen sample.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List

SCHEMA_VERSION = "ale-pkg-1.2-draft"
SIDECARS = ("package_manifest.json", "materials.json", "provenance.json", "handoff.json")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def native_hash(package: Path) -> str:
    manifest = json.loads((package / "PACKAGE.json").read_text(encoding="utf-8"))
    declared = {str(item["path"]): str(item.get("role") or "document") for item in manifest.get("files", [])}
    entries: List[Dict[str, Any]] = []
    for path in sorted((package / "base").rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(package / "base").as_posix()
        stat = path.stat()
        entries.append(
            {
                "path": relative,
                "bytes": stat.st_size,
                "mode": format(os.stat(path).st_mode & 0o777, "04o"),
                "role": declared.get(relative, "document"),
                "sha256": file_digest(path),
            }
        )
    return digest(canonical(entries).encode("utf-8"))


def package_hash(native: str, manifest: Dict[str, Any], package: Path) -> str:
    projection = {
        key: value
        for key, value in manifest.items()
        if key not in ("package_hash", "built_at", "built_by", "hashes")
    }
    sidecars = {
        name: file_digest(package / name)
        for name in SIDECARS
        if (package / name).is_file()
    }
    payload = {
        "native_hash": native,
        "package_json": projection,
        "sidecars": sidecars,
        "schema_version": SCHEMA_VERSION,
    }
    return digest(canonical(payload).encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True)
    parser.add_argument("--expected-native-hash", required=True)
    parser.add_argument("--expected-package-hash", required=True)
    parser.add_argument("--out")
    args = parser.parse_args()
    package = Path(args.package)
    manifest = json.loads((package / "PACKAGE.json").read_text(encoding="utf-8"))
    native = native_hash(package)
    packaged = package_hash(native, manifest, package)
    checks = {
        "native_hash_matches_fixed_vector": native == args.expected_native_hash,
        "package_hash_matches_fixed_vector": packaged == args.expected_package_hash,
        "package_hash_not_in_manifest": "package_hash" not in manifest,
        "package_json_not_under_base": not (package / "base" / "PACKAGE.json").exists(),
    }
    report = {
        "package": str(package),
        "native_hash": native,
        "package_hash": packaged,
        "checks": checks,
        "ok": all(checks.values()),
    }
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
