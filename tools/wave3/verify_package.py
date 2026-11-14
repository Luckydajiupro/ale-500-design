#!/usr/bin/env python3
"""Independently recompute an exported package and its receipt hashes.

This tool does not read the platform database. It is the P12 external check for
a package directory plus an expected receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "platform"))

from contracts.package_contract import FileEntry, native_hash, package_hash  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def role_for(path: str, declared: Dict[str, str]) -> str:
    return declared.get(path, "document")


def verify(package_dir: Path, expected_package_hash: str, expected_native_hash: str) -> Dict[str, Any]:
    manifest = json.loads((package_dir / "PACKAGE.json").read_text(encoding="utf-8"))
    base = package_dir / "base"
    declared = {str(item["path"]): str(item.get("role") or "document") for item in manifest.get("files", [])}
    actual: List[FileEntry] = []
    for path in sorted(p for p in base.rglob("*") if p.is_file()):
        relative = path.relative_to(base).as_posix()
        actual.append(
            FileEntry(
                path=relative,
                bytes=path.stat().st_size,
                mode=format(path.stat().st_mode & 0o777, "04o"),
                role=role_for(relative, declared),
                sha256=sha256_file(path),
            )
        )
    actual_native = native_hash(actual)
    sidecars = {
        name: sha256_file(package_dir / name)
        for name in ("package_manifest.json", "materials.json", "provenance.json", "handoff.json")
        if (package_dir / name).is_file()
    }
    stable = {
        key: value
        for key, value in manifest.items()
        if key not in ("built_at", "built_by", "hashes", "package_hash")
    }
    actual_package = package_hash(actual_native, stable, sidecars)
    checks = {
        "package_json_not_under_base": not (base / "PACKAGE.json").exists(),
        "native_hash_matches_manifest": actual_native == str(manifest.get("hashes", {}).get("native_hash", "")),
        "native_hash_matches_receipt": actual_native == expected_native_hash,
        "package_hash_matches_receipt": actual_package == expected_package_hash,
        "files_list_matches_base": set(declared) == {entry.path for entry in actual},
        "no_absolute_paths": all(not entry.path.startswith("/") for entry in actual),
    }
    return {
        "package_dir": str(package_dir),
        "file_count": len(actual),
        "native_hash": actual_native,
        "package_hash": actual_package,
        "expected_native_hash": expected_native_hash,
        "expected_package_hash": expected_package_hash,
        "checks": checks,
        "ok": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True)
    parser.add_argument("--expected-package-hash", required=True)
    parser.add_argument("--expected-native-hash", required=True)
    parser.add_argument("--out")
    args = parser.parse_args()
    result = verify(Path(args.package), args.expected_package_hash, args.expected_native_hash)
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
