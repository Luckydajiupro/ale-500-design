"""ALE-data package contract placeholder.

Work line B owns the package contract. Until PACKAGE.json placement, hash
self-reference and the 1.2 field list are signed off, this module only exposes
the layout, the validation code table and *candidate* hash functions. Nothing
here may be quoted as the final package hash outside the platform.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

# Candidate schema version. The wave-1 integration note proposes ale-pkg-1.2.
PACKAGE_SCHEMA_VERSION = "ale-pkg-1.2-draft"
ALE_DATA_VERSION = "task-data-v1.1"
HASH_STATUS = "candidate"

# Layout: <domain_code>/<task_slug>/<task_version>/base/{PACKAGE.json,input,software,reference}
LAYOUT_TEMPLATE = "{domain_code}/{task_slug}/{task_version}/base"
PACKAGE_MANIFEST_NAME = "PACKAGE.json"
SIDECARS: Tuple[str, ...] = (
    "package_manifest.json",
    "materials.json",
    "provenance.json",
    "handoff.json",
)
# Never hashed: it is the report about the package, not part of it.
UNHASHED_NAMES: Tuple[str, ...] = (
    "validation_report.json",
    "SHA256SUMS",
)

# Validation codes. Every finding is returned in one pass; one blocker rejects
# the package, warnings stay in the report.
VALIDATION_CODES: Mapping[str, Tuple[str, ...]] = {
    "L1": ("PKG_LAYOUT", "PKG_PATH_UNSAFE", "PKG_ENTRYPOINT_MISSING"),
    "L2": ("PKG_DOMAIN_UNKNOWN", "PKG_VERSION_UNSUPPORTED", "PKG_CONTRACT_KIND"),
    "L3": ("PKG_HASH_MISMATCH", "PKG_FILE_UNLISTED"),
    "L4": (
        "PKG_LICENSE_MISSING",
        "PKG_PII_HIGH",
        "PKG_ANSWER_LEAK",
        "PKG_AGENT_VIEW_LEAK",
    ),
    "L5": ("PKG_VERSION_CONFLICT", "PKG_SUPERSEDES_MISSING"),
}

BLOCKING_CODES: Tuple[str, ...] = (
    "PKG_LAYOUT",
    "PKG_PATH_UNSAFE",
    "PKG_ENTRYPOINT_MISSING",
    "PKG_VERSION_UNSUPPORTED",
    "PKG_HASH_MISMATCH",
    "PKG_LICENSE_MISSING",
    "PKG_PII_HIGH",
    "PKG_ANSWER_LEAK",
    "PKG_VERSION_CONFLICT",
)


@dataclass
class FileEntry:
    """One file covered by the native hash."""

    path: str
    bytes: int
    mode: str
    role: str
    sha256: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "bytes": self.bytes,
            "mode": self.mode,
            "role": self.role,
            "sha256": self.sha256,
        }


def canonical_json(value: Any) -> str:
    """Stable JSON: sorted keys, no whitespace, UTF-8 kept as characters."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def native_hash(files: Sequence[FileEntry]) -> str:
    """Candidate native hash over the base/ content files.

    Excludes PACKAGE.json, hash fields and validation_report.json. Entries are
    ordered by path so a rebuild on another machine lands on the same digest.
    """

    payload = [entry.as_dict() for entry in sorted(files, key=lambda item: item.path)]
    return sha256_bytes(canonical_json(payload).encode("utf-8"))


def package_hash(
    native_digest: str,
    package_json: Mapping[str, Any],
    sidecars: Mapping[str, str],
) -> str:
    """Candidate package hash.

    Covers the native hash, the canonical projection of PACKAGE.json and the
    four version-level sidecars. The hash field itself is removed before
    hashing, which is the self-reference problem P12 has to settle. Callers
    must store the result in the database and on the receipt, never write it
    back into PACKAGE.json.
    """

    projection = {key: value for key, value in package_json.items() if key != "package_hash"}
    payload = {
        "native_hash": native_digest,
        "package_json": projection,
        "sidecars": {name: sidecars[name] for name in sorted(sidecars) if name in SIDECARS},
        "schema_version": PACKAGE_SCHEMA_VERSION,
    }
    return sha256_bytes(canonical_json(payload).encode("utf-8"))


def is_blocking(code: str) -> bool:
    return code in BLOCKING_CODES


def all_codes() -> List[str]:
    return [code for layer in ("L1", "L2", "L3", "L4", "L5") for code in VALIDATION_CODES[layer]]


def validate_manifest(files: Iterable[FileEntry], entrypoints: Mapping[str, str], declared_native: str) -> List[Tuple[str, str, str]]:
    """Minimal L1/L3 checks used by the skeleton.

    Returns ``(layer, code, message)`` triples. The real packager performs the
    full L1-L5 pass; the skeleton only proves the seam.
    """

    findings: List[Tuple[str, str, str]] = []
    entries = list(files)
    if not entries:
        findings.append(("L1", "PKG_LAYOUT", "包内没有内容文件"))
    for entry in entries:
        if entry.path.startswith("/") or ".." in entry.path.split("/"):
            findings.append(("L1", "PKG_PATH_UNSAFE", f"路径不安全: {entry.path}"))
    for role in ("input", "software"):
        if role in entrypoints and not any(entry.role == role for entry in entries):
            findings.append(("L1", "PKG_ENTRYPOINT_MISSING", f"entrypoint {role} 没有对应文件"))
    recomputed = native_hash(entries)
    if declared_native and recomputed != declared_native:
        findings.append(("L3", "PKG_HASH_MISMATCH", "声明的 native_hash 与重算不一致"))
    return findings
