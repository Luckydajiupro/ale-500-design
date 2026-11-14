"""Freeze, package, validate and ingest the ALE-data overlay.

The packager reads a frozen snapshot only. It writes a version-level
``PACKAGE.json`` and four sidecars outside ``base/`` so the evaluated agent does
not see reference paths or package metadata. Hashes are candidate-contract
hashes; ``package_hash`` lives in the database and on the receipt, never inside
the bytes it hashes.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import sqlite3

from contracts import canonical_schema, package_contract

from ..adapters import LocalObjectStore, new_id, now
from ..auth import Principal, require
from ..errors import conflict, invalid, not_found
from ..repo import delivery as delivery_repo
from ..repo import materials as material_repo
from ..repo import tasks as task_repo
from . import audit
from . import state_machine as sm

DOMAINS = {
    "business_finance", "computing_math", "education_info", "engineering",
    "health_medicine", "legal", "life_sciences", "other", "physical_sciences",
    "psychology_neuro", "social_sciences", "transport_safety", "visual_media",
    "agriculture_env",
}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_path(value: str) -> str:
    value = value.replace("\\", "/")
    if value.startswith("/") or ".." in value.split("/") or not value:
        raise invalid("PKG_PATH_UNSAFE", "包内路径不安全")
    return value


def _task_payload(conn: sqlite3.Connection, task_id: str, version_no: int) -> Dict[str, Any]:
    version = task_repo.get_version(conn, task_id, version_no)
    if version is None:
        raise not_found("任务版本")
    return json.loads(version["payload_json"])


def _material_files(conn: sqlite3.Connection, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    files: List[Dict[str, Any]] = []
    for item in canonical_schema.iter_materials(payload):
        material_id = str(item.get("material_id") or "")
        row = material_repo.get_material(conn, material_id)
        if row is None:
            raise invalid("PKG_MATERIAL_MISSING", "任务源引用的资料不存在: %s" % material_id)
        versions = material_repo.list_material_versions(conn, material_id)
        if not versions:
            raise invalid("PKG_MATERIAL_EMPTY", "资料没有文件版本: %s" % material_id)
        latest = versions[-1]
        path = _safe_path(str(item.get("path") or latest["filename"]))
        files.append(
            {
                "material_id": material_id,
                "path": path,
                "role": str(item.get("role") or row["role"]),
                "sha256": latest["sha256"],
                "bytes": int(latest["bytes"]),
                "storage_key": latest["storage_key"],
            }
        )
    return files


def _generated_files(payload: Dict[str, Any]) -> Dict[str, bytes]:
    identity = payload.get("identity") or {}
    scenario = payload.get("scenario") or {}
    operations = payload.get("operations") or payload.get("steps", {}).get("items") or []
    lines = [
        "# %s" % (identity.get("title_en") or identity.get("title_zh") or identity.get("task_id")),
        "",
        "## Context",
        "",
        str(scenario.get("organization_context") or scenario.get("role") or ""),
        "",
        "## Workflow",
        "",
    ]
    for index, step in enumerate(operations, 1):
        lines.append("%d. %s" % (index, step.get("action") or ""))
        if step.get("expected_state"):
            lines.append("   Expected state: %s" % step["expected_state"])
    lines.extend(["", "## Deliverables", ""])
    for item in payload.get("deliverables") or []:
        lines.append("- `%s` (%s)" % (item.get("path"), item.get("format")))
    brief = ("\n".join(lines) + "\n").encode("utf-8")
    contract = {
        "deliverables": payload.get("deliverables") or [],
        "success_criteria": payload.get("success_criteria") or [],
    }
    return {
        "input/task_brief.md": brief,
        "input/output_contract.json": (_canonical(contract) + "\n").encode("utf-8"),
    }


def _entry(path: str, data: bytes, role: str, mode: str = "0644") -> package_contract.FileEntry:
    return package_contract.FileEntry(
        path=path, bytes=len(data), mode=mode, role=role, sha256=hashlib.sha256(data).hexdigest()
    )


def freeze_task(conn: sqlite3.Connection, principal: Principal, task_id: str) -> Dict[str, Any]:
    require(principal, "freeze:create")
    task = task_repo.get_task(conn, task_id)
    if task is None:
        raise not_found("任务")
    if task["state"] != sm.APPROVED:
        raise conflict("TASK_NOT_APPROVED", "只有 approved 任务可以冻结")
    version_no = int(task["current_version_no"])
    payload = _task_payload(conn, task_id, version_no)
    _package_metadata(conn, payload)
    files = _material_files(conn, payload)
    manifest = {
        "task_id": task_id,
        "version_no": version_no,
        "payload_hash": hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest(),
        "files": files,
        "frozen_by": principal.user_id,
    }
    snapshot_id = new_id("snap")
    delivery_repo.insert_snapshot(
        conn,
        snapshot_id=snapshot_id,
        task_id=task_id,
        version_no=version_no,
        payload_json=_canonical(payload),
        manifest_json=_canonical(manifest),
        native_hash="",
        frozen_by=principal.user_id,
        frozen_at=now(),
    )
    previous = sm.apply(conn, task, "freeze", "quality_reviewer", now())
    audit.record(conn, principal, "task.freeze", "snapshot", snapshot_id, previous, sm.FROZEN, {"version_no": version_no})
    return delivery_repo.get_snapshot(conn, snapshot_id) or {}


def _copy_base(
    conn: sqlite3.Connection,
    store: LocalObjectStore,
    payload: Dict[str, Any],
    base: Path,
) -> List[package_contract.FileEntry]:
    entries: List[package_contract.FileEntry] = []
    for rel, data in _generated_files(payload).items():
        target = base / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        entries.append(_entry(rel, data, "input"))
    for item in _material_files(conn, payload):
        data = store.read_bytes(item["storage_key"])
        rel = _safe_path(item["path"])
        target = base / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        entries.append(_entry(rel, data, str(item["role"])))
    entries.sort(key=lambda entry: entry.path)
    return entries


def _write_json(path: Path, value: Any) -> bytes:
    data = (_canonical(value) + "\n").encode("utf-8")
    path.write_bytes(data)
    return data



_PII_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}


def _package_metadata(conn: sqlite3.Connection, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Derive package metadata from the reviewed task source.

    Nothing here is a demo default. Missing or inconsistent material metadata
    stops the build before a package directory is written.
    """
    canonical_materials = list(canonical_schema.iter_materials(payload))
    if not canonical_materials:
        raise invalid("PKG_LICENSE_MISSING", "任务源没有资料，无法确定许可")
    license_types = []
    redistribution = True
    highest_pii = "none"
    material_ids = []
    for item in canonical_materials:
        material_id = str(item.get("material_id") or "")
        row = material_repo.get_material(conn, material_id)
        if row is None:
            raise invalid("PKG_MATERIAL_MISSING", "任务源引用的资料不存在: %s" % material_id)
        declared = item.get("license") or {}
        declared_type = str(declared.get("type") or "")
        if not declared_type or declared_type != row["license_type"]:
            raise invalid("PKG_MATERIAL_MISMATCH", "资料 %s 的许可与登记记录不一致" % material_id)
        declared_pii = str(item.get("pii_level") or "none")
        if declared_pii != row["pii_level"]:
            raise invalid("PKG_MATERIAL_MISMATCH", "资料 %s 的 PII 等级与登记记录不一致" % material_id)
        license_types.append(declared_type)
        redistribution = redistribution and bool(row["license_redistribution"])
        if _PII_ORDER[declared_pii] > _PII_ORDER[highest_pii]:
            highest_pii = declared_pii
        material_ids.append(material_id)
    if highest_pii == "high":
        raise invalid("PKG_PII_HIGH", "高危 PII 未脱敏，不能组包")

    criteria = payload.get("success_criteria") or []
    if not criteria:
        raise invalid("PKG_CRITERIA_MISSING", "任务源没有成功标准，无法确定验证模式")
    methods = {str(item.get("check_method") or "") for item in criteria}
    if methods <= {"auto_script"}:
        mode, oracle = "deterministic", {"required": True, "kind": "recomputed_oracle", "rationale": "确定性检查可由脚本重算"}
    elif "llm_judge" in methods:
        mode, oracle = "judge", {"required": False, "kind": "visual_reference_family", "rationale": "专业判断由校准 Judge 评分"}
    elif "human_rubric" in methods:
        mode, oracle = "human_rubric", {"required": False, "kind": "rubric_only", "rationale": "无唯一参考解，按 rubric 人工评分"}
    elif "artifact_diff" in methods:
        mode, oracle = "hybrid", {"required": True, "kind": "independent_oracle", "rationale": "产物与参考几何/渲染比对"}
    else:
        mode, oracle = "hybrid", {"required": False, "kind": "rubric_only", "rationale": "混合检查无独立 oracle"}

    provenance = payload.get("provenance") or {}
    if not provenance.get("sources"):
        raise invalid("PKG_PROVENANCE_MISSING", "任务源没有来源记录")
    handoff = payload.get("handoff") or {}
    if not handoff.get("target_format"):
        raise invalid("PKG_HANDOFF_MISSING", "任务源没有交接目标格式")
    environment = payload.get("environment") or {}
    license_type = license_types[0] if len(set(license_types)) == 1 else "mixed"
    return {
        "license": {"type": license_type, "redistribution": redistribution, "sources": sorted(set(material_ids))},
        "pii": {"level": highest_pii},
        "oracle": oracle,
        "verification": {"mode": mode, "artifacts": []},
        "provenance": provenance,
        "handoff": handoff,
        "environment_intent": environment,
        "sandbox": {"input_root": "input", "output_root": "output"},
    }

def build_package(
    conn: sqlite3.Connection,
    principal: Principal,
    task_id: str,
    package_root: Path,
    store: LocalObjectStore,
) -> Dict[str, Any]:
    require(principal, "package:create")
    task = task_repo.get_task(conn, task_id)
    if task is None:
        raise not_found("任务")
    existing = delivery_repo.get_package_for_task(conn, task_id, int(task["current_version_no"]))
    if existing and existing["state"] in ("built", "validated", "ingested"):
        return existing
    if task["state"] != sm.FROZEN:
        raise conflict("TASK_NOT_FROZEN", "只有 frozen 任务可以组包")
    snapshot = delivery_repo.get_snapshot_for_task(conn, task_id, int(task["current_version_no"]))
    if snapshot is None:
        raise not_found("冻结快照")

    payload = json.loads(snapshot["payload_json"])
    identity = payload.get("identity") or {}
    domain = str(identity.get("domain_code") or task["domain_code"])
    slug = str(identity.get("task_id") or task_id).split("/")[-1]
    version = int(task["current_version_no"])
    target = package_root / task_id / str(version)
    if target.exists():
        raise conflict("PKG_TARGET_EXISTS", "目标包目录已存在，拒绝覆盖: %s" % target)
    metadata = _package_metadata(conn, payload)
    package_root.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=".build-", dir=str(package_root)))
    try:
        base = tmp / "base"
        base.mkdir(parents=True)
        entries = _copy_base(conn, store, payload, base)
        native = package_contract.native_hash(entries)
        deliverables = payload.get("deliverables") or []
        package_json: Dict[str, Any] = {
            "schema_version": package_contract.PACKAGE_SCHEMA_VERSION,
            "ale_data_version": package_contract.ALE_DATA_VERSION,
            "task_id": str(identity.get("task_id") or task_id),
            "task_version": version,
            "domain_code": domain,
            "subdomain_code": str(identity.get("subdomain_code") or task["subdomain_code"]),
            "title": str(identity.get("title_en") or identity.get("title_zh") or ""),
            "language": str(identity.get("language") or "en"),
            "entrypoints": {"brief": "input/task_brief.md", "contract": "input/output_contract.json"},
            "deliverables": deliverables,
            "oracle": metadata["oracle"],
            "verification": metadata["verification"],
            "license": metadata["license"],
            "pii": metadata["pii"],
            "provenance": metadata["provenance"],
            "environment_intent": metadata["environment_intent"],
            "sandbox": metadata["sandbox"],
            "handoff": metadata["handoff"],
            "files": [entry.as_dict() for entry in entries],
            "hashes": {"native_hash": native, "hash_status": "candidate"},
            "built_by": "platform",
            "built_at": now(),
            "counted_in_500": False,
        }
        _write_json(tmp / "PACKAGE.json", package_json)
        sidecar_values = {
            "package_manifest.json": {
                "snapshot_id": snapshot["snapshot_id"],
                "native_hash": native,
                "files": [entry.as_dict() for entry in entries],
            },
            "materials.json": {
                "materials": [
                    {
                        "material_id": item["material_id"],
                        "path": item["path"],
                        "role": item["role"],
                        "sha256": item["sha256"],
                        "bytes": item["bytes"],
                        "license": next((m.get("license") for m in payload.get("materials", []) if m.get("material_id") == item["material_id"]), None),
                        "pii_level": next((m.get("pii_level") for m in payload.get("materials", []) if m.get("material_id") == item["material_id"]), None),
                    }
                    for item in _material_files(conn, payload)
                ]
            },
            "provenance.json": metadata["provenance"],
            "handoff.json": dict(metadata["handoff"], frozen_snapshot_id=snapshot["snapshot_id"]),
        }
        sidecar_hashes: Dict[str, str] = {}
        for name, value in sidecar_values.items():
            data = _write_json(tmp / name, value)
            sidecar_hashes[name] = hashlib.sha256(data).hexdigest()
        stable = {k: v for k, v in package_json.items() if k not in ("built_at", "built_by", "hashes", "package_hash")}
        candidate = package_contract.package_hash(native, stable, sidecar_hashes)
        (tmp / "SHA256SUMS").write_text(
            "\n".join("%s  %s" % (entry.sha256, entry.path) for entry in entries) + "\n",
            encoding="utf-8",
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise conflict("PKG_TARGET_EXISTS", "目标包目录在构建期间出现，拒绝覆盖")
        os.replace(tmp, target)
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise

    package_id = new_id("pkg")
    delivery_repo.insert_package(
        conn,
        package_id=package_id,
        snapshot_id=snapshot["snapshot_id"],
        task_id=task_id,
        version_no=version,
        state="built",
        built_by="platform",
        created_at=now(),
    )
    delivery_repo.set_package_state(conn, package_id, "built", now(), package_hash=candidate)
    previous = sm.apply(conn, task, "package", "platform_admin", now())
    audit.record(
        conn,
        principal,
        "package.build",
        "package",
        package_id,
        previous,
        sm.PACKAGED,
        {"native_hash": native, "package_hash": candidate, "files": len(entries)},
    )
    return delivery_repo.get_package(conn, package_id) or {}


def _read_package(package_root: Path, package: Dict[str, Any], task: Dict[str, Any]) -> Tuple[Path, Dict[str, Any], List[package_contract.FileEntry]]:
    versions = package_root / package["task_id"] / str(package["version_no"])
    package_json_path = versions / "PACKAGE.json"
    if not package_json_path.exists():
        raise invalid("PKG_LAYOUT", "PACKAGE.json 不在版本层")
    package_json = json.loads(package_json_path.read_text(encoding="utf-8"))
    base = versions / "base"
    entries: List[package_contract.FileEntry] = []
    declared_roles = {item.get("path"): item.get("role") for item in package_json.get("files") or []}
    if base.exists():
        for path in sorted(base.rglob("*")):
            if path.is_file():
                rel = path.relative_to(base).as_posix()
                entries.append(
                    package_contract.FileEntry(
                        path=rel,
                        bytes=path.stat().st_size,
                        mode="0%03o" % (path.stat().st_mode & 0o777),
                        role=str(declared_roles.get(rel) or ("reference" if rel.startswith("reference/") else "software" if rel.startswith("software/") else "input")),
                        sha256=_sha256_file(path),
                    )
                )
    return versions, package_json, entries


def validate_package(
    conn: sqlite3.Connection,
    principal: Principal,
    package_id: str,
    package_root: Path,
) -> Dict[str, Any]:
    require(principal, "package:validate")
    package = delivery_repo.get_package(conn, package_id)
    if package is None:
        raise not_found("包")
    if package["state"] not in ("built", "validated", "failed"):
        raise conflict("PACKAGE_NOT_BUILT", "包尚未构建")
    task = task_repo.get_task(conn, package["task_id"])
    if task is None:
        raise not_found("任务")
    findings: List[Tuple[str, str, str, bool]] = []
    try:
        versions, package_json, entries = _read_package(package_root, package, task)
    except Exception as exc:
        findings.append(("L1", "PKG_LAYOUT", str(exc), False))
        versions = package_root
        package_json = {}
        entries = []

    # L1 layout and entrypoints
    if not entries:
        findings.append(("L1", "PKG_LAYOUT", "base/ 中没有内容文件", False))
    for entry in entries:
        if entry.path.startswith("/") or ".." in entry.path.split("/"):
            findings.append(("L1", "PKG_PATH_UNSAFE", "路径不安全: %s" % entry.path, False))
    for key, rel in (package_json.get("entrypoints") or {}).items():
        if not (versions / "base" / rel).exists():
            findings.append(("L1", "PKG_ENTRYPOINT_MISSING", "entrypoint %s 缺少 %s" % (key, rel), False))

    # L2 semantics
    if package_json.get("schema_version") != package_contract.PACKAGE_SCHEMA_VERSION:
        findings.append(("L2", "PKG_VERSION_UNSUPPORTED", "schema_version 不是候选版本", False))
    if package_json.get("ale_data_version") != package_contract.ALE_DATA_VERSION:
        findings.append(("L2", "PKG_VERSION_UNSUPPORTED", "ale_data_version 不匹配", False))
    if package_json.get("domain_code") not in DOMAINS:
        findings.append(("L2", "PKG_DOMAIN_UNKNOWN", "未知 domain_code", False))
    if package_json.get("task_id") != str((json.loads(task["draft_payload"]).get("identity") or {}).get("task_id") or task["task_id"]):
        findings.append(("L2", "PKG_CONTRACT_KIND", "task_id 与任务身份不一致", False))

    # L3 completeness
    declared = {item["path"]: item for item in package_json.get("files") or []}
    actual = {entry.path: entry for entry in entries}
    if set(declared) != set(actual):
        findings.append(("L3", "PKG_FILE_UNLISTED", "files[] 与实际文件不一致", False))
    for rel, entry in actual.items():
        item = declared.get(rel)
        if item is None:
            continue
        if item.get("sha256") != entry.sha256 or int(item.get("bytes", -1)) != entry.bytes:
            findings.append(("L3", "PKG_HASH_MISMATCH", "文件哈希或大小不一致: %s" % rel, False))
    recomputed = package_contract.native_hash(entries)
    declared_native = (package_json.get("hashes") or {}).get("native_hash")
    if not declared_native or recomputed != declared_native:
        findings.append(("L3", "PKG_HASH_MISMATCH", "native_hash 与重算不一致", False))
    if package.get("package_hash") != package_contract.package_hash(
        recomputed,
        {k: v for k, v in package_json.items() if k not in ("built_at", "built_by", "hashes", "package_hash")},
        {name: _sha256_file(versions / name) for name in package_contract.SIDECARS if (versions / name).exists()},
    ):
        findings.append(("L3", "PKG_HASH_MISMATCH", "package_hash 与重算不一致", False))

    # L4 safety and agent view
    if not package_json.get("license"):
        findings.append(("L4", "PKG_LICENSE_MISSING", "缺少 license", False))
    if (package_json.get("pii") or {}).get("level") == "high":
        findings.append(("L4", "PKG_PII_HIGH", "高危 PII 未脱敏", False))
    reference_paths = {entry.path for entry in entries if entry.role == "reference"}
    input_paths = {entry.path for entry in entries if entry.role == "input"}
    if any(path.startswith("reference/") for path in input_paths):
        findings.append(("L4", "PKG_AGENT_VIEW_LEAK", "input/ 中出现 reference 路径", False))
    reference_names = {Path(path).name for path in reference_paths}
    for path in input_paths:
        data = (versions / "base" / path).read_bytes()
        if any(name.encode("utf-8") in data for name in reference_names if name):
            findings.append(("L4", "PKG_ANSWER_LEAK", "input/ 文件包含 reference 文件名", False))
    if (versions / "base" / "PACKAGE.json").exists():
        findings.append(("L4", "PKG_AGENT_VIEW_LEAK", "PACKAGE.json 位于 Agent 可见的 base/", False))

    # L5 ingest consistency
    other = delivery_repo.get_package_for_task(conn, package["task_id"], package["version_no"])
    if other and other["package_id"] != package_id and other["package_hash"] != package["package_hash"]:
        findings.append(("L5", "PKG_VERSION_CONFLICT", "同一任务版本存在不同 package_hash", False))

    blockers = [item for item in findings if not item[3]]
    for layer, code, message, passed in findings:
        delivery_repo.insert_validation(
            conn,
            validation_id=new_id("val"),
            package_id=package_id,
            layer=layer,
            code=code,
            severity="blocker" if not passed else "info",
            passed=passed,
            message=message,
            report_json="{}",
            created_at=now(),
        )
    report_path = versions / "validation_report.json"
    report_path.write_text(
        json.dumps(
            {
                "package_id": package_id,
                "native_hash": recomputed if entries else None,
                "package_hash": package.get("package_hash"),
                "findings": [
                    {"layer": layer, "code": code, "message": message, "passed": passed}
                    for layer, code, message, passed in findings
                ],
                "ok": not blockers,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    if blockers:
        delivery_repo.set_package_state(conn, package_id, "failed", now(), failure_code=blockers[0][1])
        audit.record(conn, principal, "package.validate_fail", "package", package_id, sm.PACKAGED, sm.FROZEN, {"blockers": [item[1] for item in blockers]})
        return {"package_id": package_id, "ok": False, "blockers": [item[1] for item in blockers], "findings": findings}
    delivery_repo.set_package_state(conn, package_id, "validated", now())
    task = task_repo.get_task(conn, package["task_id"])
    if task is not None and task["state"] == sm.PACKAGED:
        previous = sm.apply(conn, task, "validate_pass", "system", now())
        audit.record(conn, principal, "package.validate_pass", "package", package_id, previous, sm.PACKAGE_VALIDATED, {"native_hash": recomputed})
    return {"package_id": package_id, "ok": True, "blockers": [], "findings": findings}


def ingest_package(
    conn: sqlite3.Connection,
    principal: Principal,
    package_id: str,
    package_root: Path,
) -> Dict[str, Any]:
    require(principal, "ingest:create")
    package = delivery_repo.get_package(conn, package_id)
    if package is None:
        raise not_found("包")
    existing = delivery_repo.get_ingest_by_hash(conn, str(package["package_hash"]))
    if existing:
        return existing
    if package["state"] != "validated":
        raise conflict("PACKAGE_NOT_VALIDATED", "包未通过校验")
    task = task_repo.get_task(conn, package["task_id"])
    if task is None:
        raise not_found("任务")
    versions, package_json, entries = _read_package(package_root, package, task)
    report_path = versions / "validation_report.json"
    report_hash = _sha256_file(report_path)
    receipt = {
        "package_id": package_id,
        "task_id": package["task_id"],
        "task_version": package["version_no"],
        "package_hash": package["package_hash"],
        "native_hash": (package_json.get("hashes") or {}).get("native_hash"),
        "validation_report_sha256": report_hash,
        "file_count": len(entries),
        "received_at": now(),
        "received_by": principal.user_id,
        "state": "published",
    }
    ingest_id = new_id("ing")
    delivery_repo.insert_ingest(
        conn,
        ingest_id=ingest_id,
        package_id=package_id,
        package_hash=str(package["package_hash"]),
        state="published",
        received_at=receipt["received_at"],
        received_by=principal.user_id,
        receipt_json=json.dumps(receipt, ensure_ascii=False, sort_keys=True),
    )
    delivery_repo.set_package_state(conn, package_id, "ingested", now())
    if task["state"] == sm.PACKAGE_VALIDATED:
        previous = sm.apply(conn, task, "ingest", "platform_admin", now())
        audit.record(conn, principal, "package.ingest", "ingest", ingest_id, previous, sm.INGESTED, {"package_hash": package["package_hash"]})
    (versions / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return delivery_repo.get_ingest(conn, ingest_id) or {}


def export_agent_view(
    package_root: Path,
    package: Dict[str, Any],
    task_id: str,
    destination: Path,
) -> Path:
    """Copy only the solver-visible part of a built package.

    The judged agent sees input and software files. Reference material, package
    metadata, validation reports and receipts stay out of this view.
    """
    versions = package_root / task_id / str(package["version_no"])
    if not (versions / "base").is_dir():
        raise not_found("包")
    if destination.exists():
        raise conflict("AGENT_VIEW_EXISTS", "目标目录已存在")
    for role in ("input", "software"):
        source = versions / "base" / role
        if not source.is_dir():
            continue
        shutil.copytree(source, destination / role)
    if not destination.exists():
        destination.mkdir(parents=True)
    return destination
