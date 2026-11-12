"""Minimal ale-data v1.1 validator and Harbor converter.

This module is the executable part of the P1 contract, not platform code.
It is deliberately small and dependency-free so the contract can be tested
before the platform exists. The platform must implement the same rules; the
fixture under tests/fixtures/ is the shared conformance case.

Package layout (one task):

    <task>/base/
      PACKAGE.json
      input/task_brief.md
      input/output_contract.json
      input/document_manifest.json     (required when input/documents/ exists)
      input/...                        (task data)
      software/...                     (optional)
      reference/answer_key.json
      reference/...                    (optional)

The package root is the ``base`` directory. ``PACKAGE.json`` carries the
fields ale-data v1.1 does not define (license, provenance, sandbox contract),
so the data layout stays ale-data compatible and the sidecar holds the rest.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # macOS system Python 3.9
    tomllib = None

ALEDATA_VERSION = "task-data-v1.1"
HARBOR_SCHEMA = "1.4+ale.1"
PACKAGE_VERSION = "ale-pkg-1.0"
DOMAINS = {
    "agriculture_env",
    "business_finance",
    "computing_math",
    "education_info",
    "engineering",
    "health_medicine",
    "legal",
    "life_sciences",
    "other",
    "physical_sciences",
    "psychology_neuro",
    "social_sciences",
    "transport_safety",
    "visual_media",
}
SLUG = re.compile(r"^[a-z0-9][a-z0-9_]{2,60}$")

REQUIRED = (
    "input/task_brief.md",
    "input/output_contract.json",
    "reference/answer_key.json",
)

#: Every check the validator can report. Errors block; warnings do not.
ERROR_CODES = {
    "IMPORT_LAYOUT",
    "IMPORT_PACKAGE_JSON",
    "IMPORT_DOMAIN_UNKNOWN",
    "IMPORT_SLUG_INVALID",
    "IMPORT_VERSION_UNSUPPORTED",
    "IMPORT_MISSING_FILE",
    "IMPORT_SCHEMA",
    "IMPORT_HASH_MISMATCH",
    "IMPORT_LICENSE_MISSING",
    "IMPORT_PROVENANCE_MISSING",
    "IMPORT_PATH_UNSAFE",
    "IMPORT_ORACLE_MISSING",
}
WARNING_CODES = {"IMPORT_SIZE_LARGE", "IMPORT_ORACLE_ABSENT"}


class Finding(dict):
    """One validation result: ``{"code", "path", "message"}``."""

    @property
    def code(self) -> str:
        return self["code"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _finding(code: str, path: str, message: str) -> Finding:
    return Finding(code=code, path=path, message=message)


def _safe_relative(path: str) -> bool:
    pure = Path(path)
    return not pure.is_absolute() and ".." not in pure.parts


def load_package(root: Path) -> dict[str, Any]:
    return json.loads((root / "PACKAGE.json").read_text(encoding="utf-8"))


def _read_toml(text: str) -> dict[str, Any]:
    """Parse the small TOML subset this converter writes.

    The real platform uses a full TOML parser. Keeping the test dependency-free
    matters more here than covering every TOML form, and the generated file is
    always this shape.
    """
    if tomllib is not None:
        return tomllib.loads(text)
    data: dict[str, Any] = {}
    table: dict[str, Any] = data
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            table = data
            for part in line[1:-1].split("."):
                table = table.setdefault(part.strip(), {})
        elif "=" in line:
            key, value = line.split("=", 1)
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                table[key.strip()] = json.loads(value)
            elif value in {"true", "false"}:
                table[key.strip()] = value == "true"
            elif value.startswith("[") and value.endswith("]"):
                table[key.strip()] = json.loads(value)
            else:
                table[key.strip()] = int(value)
    return data


def _check_package(package: dict[str, Any]) -> list[Finding]:
    out: list[Finding] = []
    if package.get("package_version") != PACKAGE_VERSION:
        out.append(
            _finding("IMPORT_VERSION_UNSUPPORTED", "PACKAGE.json",
                     f"package_version must be {PACKAGE_VERSION}")
        )
    if package.get("ale_data_version") != ALEDATA_VERSION:
        out.append(
            _finding("IMPORT_VERSION_UNSUPPORTED", "PACKAGE.json",
                     f"ale_data_version must be {ALEDATA_VERSION}")
        )
    task_id = package.get("task_id", "")
    domain = package.get("domain_code", "")
    slug = task_id.split("/", 1)[-1] if "/" in task_id else ""
    if domain not in DOMAINS:
        out.append(_finding("IMPORT_DOMAIN_UNKNOWN", "PACKAGE.json", domain))
    if not SLUG.match(slug):
        out.append(_finding("IMPORT_SLUG_INVALID", "PACKAGE.json", task_id))
    if not task_id.startswith(f"{domain}/"):
        out.append(_finding("IMPORT_LAYOUT", "PACKAGE.json",
                            "task_id must start with '<domain_code>/'"))

    license_ = package.get("license") or {}
    if not license_.get("id") or not isinstance(license_.get("redistributable"), bool):
        out.append(_finding("IMPORT_LICENSE_MISSING", "PACKAGE.json",
                            "license.id and license.redistributable are required"))
    provenance = package.get("provenance") or {}
    for key in ("source", "collected_at"):
        if not provenance.get(key):
            out.append(_finding("IMPORT_PROVENANCE_MISSING", "PACKAGE.json",
                                f"provenance.{key} is required"))

    sandbox = package.get("sandbox") or {}
    if sandbox.get("os", "linux") not in {"linux", "windows", "macos"}:
        out.append(_finding("IMPORT_SCHEMA", "PACKAGE.json", "sandbox.os invalid"))
    for key in ("input_root", "output_root"):
        value = sandbox.get(key, "")
        if value and not value.startswith("/"):
            out.append(_finding("IMPORT_PATH_UNSAFE", "PACKAGE.json",
                                f"sandbox.{key} must be absolute"))
    return out


def _check_files(root: Path, package: dict[str, Any]) -> list[Finding]:
    out: list[Finding] = []
    listed: dict[str, dict[str, Any]] = {}
    for entry in package.get("files", []):
        rel = entry.get("path", "")
        if not _safe_relative(rel):
            out.append(_finding("IMPORT_PATH_UNSAFE", "PACKAGE.json", rel))
            continue
        listed[rel] = entry
        target = root / rel
        if not target.is_file():
            out.append(_finding("IMPORT_MISSING_FILE", rel, "listed but absent"))
            continue
        digest = sha256_file(target)
        if digest != entry.get("sha256"):
            out.append(_finding("IMPORT_HASH_MISMATCH", rel,
                                f"sha256 {digest} != {entry.get('sha256')}"))
        if target.stat().st_size != entry.get("bytes"):
            out.append(_finding("IMPORT_HASH_MISMATCH", rel, "byte size differs"))

    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel == "PACKAGE.json":
            continue
        if rel not in listed:
            out.append(_finding("IMPORT_HASH_MISMATCH", rel,
                                "file is not covered by PACKAGE.files"))
    return out


def _check_contract(root: Path) -> list[Finding]:
    out: list[Finding] = []
    contract_path = root / "input/output_contract.json"
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [_finding("IMPORT_SCHEMA", "input/output_contract.json", str(error))]
    for key in ("root", "required_top_level_key", "output_path"):
        if key not in contract:
            out.append(_finding("IMPORT_SCHEMA", "input/output_contract.json",
                                f"missing {key}"))
    output_path = contract.get("output_path", "")
    if output_path and not _safe_relative(output_path):
        out.append(_finding("IMPORT_PATH_UNSAFE", "input/output_contract.json",
                            output_path))

    manifest_path = root / "input/document_manifest.json"
    documents = root / "input/documents"
    if documents.is_dir():
        if not manifest_path.is_file():
            out.append(_finding("IMPORT_MISSING_FILE",
                                "input/document_manifest.json",
                                "documents/ exists without a manifest"))
        else:
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as error:
                out.append(_finding("IMPORT_SCHEMA",
                                    "input/document_manifest.json", str(error)))
                manifest = {}
            for entry in manifest.get("documents", []):
                rel = str(entry.get("relative_path", ""))
                target = root / "input" / rel
                if not _safe_relative(rel) or not target.is_file():
                    out.append(_finding("IMPORT_MISSING_FILE",
                                        f"input/{rel}", "document absent"))
                    continue
                if sha256_file(target) != entry.get("sha256"):
                    out.append(_finding("IMPORT_HASH_MISMATCH", f"input/{rel}",
                                        "document sha256 differs"))
    return out


def _check_oracle(root: Path) -> list[Finding]:
    """An answer key that does not parse is an oracle gap, not a crash."""
    try:
        key = json.loads((root / "reference/answer_key.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [_finding("IMPORT_ORACLE_MISSING", "reference/answer_key.json", str(error))]
    if not isinstance(key, dict) or not key:
        return [_finding("IMPORT_ORACLE_MISSING", "reference/answer_key.json",
                         "answer key is empty")]
    return []


def validate_package(root: Path) -> list[Finding]:
    """Validate one ``base`` package. Errors block; warnings are recorded."""
    out: list[Finding] = []
    if not (root / "input").is_dir() or not (root / "reference").is_dir():
        return [_finding("IMPORT_LAYOUT", str(root),
                         "expected input/ and reference/ beside PACKAGE.json")]
    try:
        package = load_package(root)
    except (OSError, json.JSONDecodeError) as error:
        return [_finding("IMPORT_PACKAGE_JSON", "PACKAGE.json", str(error))]

    out.extend(_check_package(package))
    for rel in REQUIRED:
        if not (root / rel).is_file():
            out.append(_finding("IMPORT_MISSING_FILE", rel, "required file absent"))
    out.extend(_check_files(root, package))
    if (root / "input/output_contract.json").is_file():
        out.extend(_check_contract(root))
    out.extend(_check_oracle(root))

    total = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
    if total > 5 * 1024**3:
        out.append(_finding("IMPORT_SIZE_LARGE", "PACKAGE.json", f"{total} bytes"))
    return out


def errors(findings: list[Finding]) -> list[Finding]:
    return [f for f in findings if f["code"] in ERROR_CODES]


def _copy_tree(source: Path, target: Path) -> None:
    if not source.is_dir():
        return
    shutil.copytree(source, target, dirs_exist_ok=True)
    for path in target.rglob("*"):
        path.chmod(0o755 if path.is_dir() else 0o644)


def _verifier_script() -> str:
    return '''"""Generated verifier: compare the submission with reference/answer_key.json."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REFERENCE = HERE / "reference"


def load(name):
    return json.loads((REFERENCE / name).read_text(encoding="utf-8"))


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def score_case(submitted, expected, contract):
    fields = [key for key in contract.get("case_fields", {}) if key not in {"case_id", "notes"}]
    points = {key: 0.0 for key in fields}
    weights = expected.get("_weights") or {key: 1.0 for key in fields}
    total = sum(weights.get(key, 1.0) for key in fields) or 1.0
    gained = 0.0
    for key in fields:
        want = expected.get(key)
        got = number(submitted.get(key))
        if want is not None and got is not None and abs(got - float(want)) <= 0.01:
            points[key] = 1.0
            gained += weights.get(key, 1.0)
    return gained / total, points


def main():
    contract = load("output_contract.json")
    key = load("answer_key.json")
    out_path = Path(json.loads((HERE / "verifier.json").read_text(encoding="utf-8"))["output_path"])
    result = {"reward": 0.0, "cases": {}}
    if not out_path.is_file():
        result["reason"] = "submission missing"
    else:
        try:
            submitted = json.loads(out_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            submitted = {}
            result["reason"] = f"invalid json: {error}"
        rows = {}
        if isinstance(submitted, dict):
            rows = {str(row.get("case_id")): row for row in submitted.get(contract["required_top_level_key"], [])}
        scores = []
        for case_id, expected in key.get("cases", {}).items():
            got, points = score_case(rows.get(case_id, {}), expected, contract)
            scores.append(got)
            result["cases"][case_id] = {"score": got, "fields": points}
        result["reward"] = sum(scores) / len(scores) if scores else 0.0
    Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
    Path("/logs/verifier/reward.json").write_text(json.dumps({"reward": result["reward"]}), encoding="utf-8")
    Path("/logs/verifier/verification.json").write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
'''


def to_harbor(root: Path, out: Path) -> dict[str, Any]:
    """Convert one validated package into an ALE Harbor task folder."""
    package = load_package(root)
    sandbox = package.get("sandbox", {})
    os_name = sandbox.get("os", "linux")
    input_root = sandbox.get("input_root", "/home/user/input")
    output_root = sandbox.get("output_root", "/home/user/output")
    contract = json.loads((root / "input/output_contract.json").read_text(encoding="utf-8"))

    out.mkdir(parents=True, exist_ok=True)
    _copy_tree(root / "input", out / "environment/task_data/input")
    _copy_tree(root / "software", out / "environment/task_data/software")
    _copy_tree(root / "reference", out / "tests/reference")

    name = package["task_id"].split("/", 1)[-1]
    artifacts = f"{output_root.rstrip('/')}/{contract['output_path']}"
    toml = [
        f'schema_version = "{HARBOR_SCHEMA}"',
        f'artifacts = ["{artifacts}"]',
        "",
        "[task]",
        f'name = "agentslastexam/{name}"',
        f'description = {json.dumps(package.get("title", ""), ensure_ascii=False)}',
        'version = "1.0"',
        "",
        "[environment]",
        f'os = "{os_name}"',
        f'cpus = {int(sandbox.get("cpus", 1))}',
        f'memory_mb = {int(sandbox.get("memory_mb", 4096))}',
        f'gpus = {int(sandbox.get("gpus", 0))}',
        "",
        "[agent]",
        'user = "user"',
        f'timeout_sec = {int(sandbox.get("timeout_sec", 900))}',
        f'network_mode = "{sandbox.get("network", "no-network")}"',
        "",
        "[verifier]",
        'timeout_sec = 600',
        "",
    ]
    (out / "task.toml").write_text("\n".join(toml), encoding="utf-8")
    (out / "instruction.md").write_text(
        (root / "input/task_brief.md").read_text(encoding="utf-8"), encoding="utf-8"
    )

    docker = [
        "FROM ghcr.io/agentslastexam/container-ubuntu22-base:0.1.1",
        f"RUN mkdir -p {input_root} {output_root} /home/user/software",
        "COPY task_data/input/ " + input_root.rstrip("/") + "/",
        "COPY task_data/software/ /home/user/software/",
        "RUN chmod -R a+rX " + input_root + " /home/user/software",
    ]
    # runtime_env/ travels with input/. The image installs dependencies only when the
    # package pins them; a converter never resolves dependencies at conversion time.
    (out / "environment").mkdir(exist_ok=True)
    (out / "environment/Dockerfile").write_text("\n".join(docker) + "\n", encoding="utf-8")

    (out / "tests").mkdir(exist_ok=True)
    (out / "tests/test.sh").write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\nexec python3 verify.py\n", encoding="utf-8"
    )
    (out / "tests/verify.py").write_text(_verifier_script(), encoding="utf-8")
    (out / "tests/verifier.json").write_text(
        json.dumps({"output_path": artifacts}, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    (out / "solution").mkdir(exist_ok=True)
    oracle = bool(package.get("oracle", True))
    (out / "solution/solve.sh").write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\n"
        + ("" if oracle else 'echo "NO_ORACLE: supply package has no known-good solution" >&2\nexit 1\n'),
        encoding="utf-8",
    )

    conversion = {
        "task_id": package["task_id"],
        "ale_data_version": ALEDATA_VERSION,
        "harbor_schema_version": HARBOR_SCHEMA,
        "engine_commit": package.get("engine_commit", "73517c2eb097abe7974e9ec4de9819a02cd0ee81"),
        "artifacts": [artifacts],
        "oracle": oracle,
        "gaps": package.get("known_gaps", []),
    }
    (out / "conversion.json").write_text(
        json.dumps(conversion, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return conversion


def from_harbor(task: Path, out: Path) -> dict[str, Any]:
    """Minimal reverse conversion, enough to prove the mapping is lossless."""
    config = _read_toml((task / "task.toml").read_text(encoding="utf-8"))
    conversion = json.loads((task / "conversion.json").read_text(encoding="utf-8"))
    name = config["task"]["name"].split("/", 1)[-1]
    domain = conversion["task_id"].split("/", 1)[0]

    out.mkdir(parents=True, exist_ok=True)
    _copy_tree(task / "environment/task_data/input", out / "input")
    _copy_tree(task / "environment/task_data/software", out / "software")
    _copy_tree(task / "tests/reference", out / "reference")
    (out / "input/task_brief.md").write_text(
        (task / "instruction.md").read_text(encoding="utf-8"), encoding="utf-8"
    )

    def files() -> list[dict[str, Any]]:
        rows = []
        for path in sorted(p for p in out.rglob("*") if p.is_file()):
            rel = path.relative_to(out).as_posix()
            if rel == "PACKAGE.json":
                continue
            rows.append({"path": rel, "sha256": sha256_file(path),
                         "bytes": path.stat().st_size})
        return rows

    package = {
        "package_version": PACKAGE_VERSION,
        "ale_data_version": ALEDATA_VERSION,
        "task_id": f"{domain}/{name}",
        "domain_code": domain,
        "subdomain_code": conversion.get("subdomain_code", "unknown"),
        "title": config["task"].get("description", ""),
        "license": {"id": "CC-BY-4.0", "redistributable": True},
        "provenance": {"source": "roundtrip-test", "collected_at": "2026-11-12"},
        "sandbox": {"os": config["environment"].get("os", "linux"),
                    "input_root": "/home/user/input", "output_root": "/home/user/output"},
        "oracle": conversion.get("oracle", True),
        "files": [],
    }
    package["files"] = files()
    (out / "PACKAGE.json").write_text(
        json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return package


def canonical_package_hash(root: Path) -> str:
    """Hash of the file set, used to prove a round trip is lossless."""
    package = load_package(root)
    rows = sorted(
        (entry["path"], entry["sha256"], entry["bytes"]) for entry in package["files"]
    )
    return sha256_bytes(canonical_json(rows))
