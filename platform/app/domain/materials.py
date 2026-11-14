"""Material registration, immutable versions and the four-layer read rules.

Bytes are stored once by hash. A second upload of the same filename becomes a new
material version; version 1 keeps its bytes, hash and timestamp.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from contracts import canonical_schema

from ..adapters import LocalObjectStore, new_id, now, sha256_stream
from ..auth import Principal, require
from ..errors import conflict, forbidden, invalid, not_found
from ..repo import materials as material_repo
from ..repo import tasks as task_repo
from . import audit


def _check_enums(kind: str, role: str, layer: str, license_type: str, pii_level: str) -> None:
    if kind not in ("dataset", "document", "image", "code", "url", "template"):
        raise invalid("MATERIAL_KIND", "资料 kind 非法")
    if role not in canonical_schema.MATERIAL_ROLES:
        raise invalid("MATERIAL_ROLE", "资料 role 非法")
    if layer not in canonical_schema.MATERIAL_LAYERS:
        raise invalid("MATERIAL_LAYER", "资料 layer 非法")
    if license_type not in canonical_schema.LICENSE_TYPES:
        raise invalid("MATERIAL_LICENSE", "许可类型非法")
    if pii_level not in canonical_schema.PII_LEVELS:
        raise invalid("MATERIAL_PII", "PII 等级非法")


def register(
    conn: sqlite3.Connection,
    principal: Principal,
    body: Dict[str, Any],
) -> Dict[str, Any]:
    require(principal, "material:write:own")
    task_id = body.get("task_id")
    task = None
    if task_id:
        task = task_repo.get_task(conn, str(task_id))
        if task is None:
            raise not_found("任务")
        if task["owner_expert_id"] != principal.user_id:
            raise forbidden("material:write")
    material_id = (body.get("material_id") or "").strip()
    if not material_id:
        raise invalid("MATERIAL_ID_REQUIRED", "material_id 必填")
    if material_repo.get_material(conn, material_id) is not None:
        raise conflict("MATERIAL_EXISTS", "material_id 已存在")

    kind = str(body.get("kind") or "document")
    role = str(body.get("role") or "input")
    layer = str(body.get("layer") or "raw")
    license_type = str(body.get("license_type") or "")
    pii_level = str(body.get("pii_level") or "none")
    _check_enums(kind, role, layer, license_type, pii_level)

    if pii_level == "high" and not body.get("pii_confirmed"):
        raise invalid("MATERIAL_PII_CONFIRMATION", "高危 PII 需要隐私安全确认后才能登记")

    if layer == "reference" and role == "input":
        raise invalid("MATERIAL_LAYER_ROLE", "reference 层资料不能作为 input")

    material_repo.insert_material(
        conn,
        material_id=material_id,
        task_id=str(task_id) if task_id else None,
        owner_expert_id=principal.user_id,
        kind=kind,
        role=role,
        layer=layer,
        license_type=license_type,
        license_redistribution=bool(body.get("license_redistribution")),
        pii_level=pii_level,
        source_url=body.get("source_url"),
        source_accessed_at=body.get("source_accessed_at"),
        created_at=now(),
    )
    if pii_level == "high" and body.get("pii_confirmed"):
        material_repo.confirm_pii(conn, material_id, principal.user_id)
    audit.record(
        conn,
        principal,
        "material.register",
        "material",
        material_id,
        None,
        "active",
        {"role": role, "layer": layer, "license": license_type, "pii": pii_level},
    )
    return get(conn, principal, material_id)


def upload(
    conn: sqlite3.Connection,
    principal: Principal,
    store: LocalObjectStore,
    material_id: str,
    filename: str,
    data: bytes,
    client_sha256: Optional[str] = None,
) -> Dict[str, Any]:
    material = material_repo.get_material(conn, material_id)
    if material is None:
        raise not_found("资料")
    if material["owner_expert_id"] != principal.user_id:
        raise forbidden("material:write")
    if not data:
        raise invalid("MATERIAL_EMPTY", "文件为空")

    import hashlib

    digest = hashlib.sha256(data).hexdigest()
    if client_sha256 and client_sha256 != digest:
        raise invalid("MATERIAL_HASH_MISMATCH", "客户端哈希与服务端重算不一致")
    stored = store.put_bytes(data)
    version_no = material_repo.next_material_version(conn, material_id)
    material_repo.insert_material_version(
        conn,
        material_version_id=new_id("mv"),
        material_id=material_id,
        version_no=version_no,
        filename=filename,
        size=stored.bytes,
        sha256=stored.sha256,
        storage_key=stored.storage_key,
        created_at=now(),
    )
    audit.record(
        conn,
        principal,
        "material.version.create",
        "material",
        material_id,
        None,
        "active",
        {"version_no": version_no, "sha256": stored.sha256, "bytes": stored.bytes},
    )
    return get(conn, principal, material_id)


def get(conn: sqlite3.Connection, principal: Principal, material_id: str) -> Dict[str, Any]:
    material = material_repo.get_material(conn, material_id)
    if material is None:
        raise not_found("资料")
    assert_readable(conn, principal, material)
    detail = dict(material)
    detail["versions"] = material_repo.list_material_versions(conn, material_id)
    detail["allowed_layers"] = sorted(_layers_for(principal))
    return detail


def list_for_task(conn: sqlite3.Connection, principal: Principal, task_id: str) -> List[Dict[str, Any]]:
    rows = material_repo.list_materials(conn, task_id)
    return [row for row in rows if _layer_visible(conn, principal, row)]


def _layers_for(principal: Principal) -> List[str]:
    from ..auth import LAYER_ACCESS

    allowed = set()
    for role in principal.roles:
        allowed |= LAYER_ACCESS.get(role, frozenset())
    return sorted(allowed)


def _layer_visible(conn: sqlite3.Connection, principal: Principal, material: Dict[str, Any]) -> bool:
    from ..auth import LAYER_ACCESS, ROLE_DOMAIN_REVIEWER, ROLE_EXPERT

    layer = material["layer"]
    if layer not in _layers_for(principal):
        return False
    if material["owner_expert_id"] == principal.user_id:
        return True
    if ROLE_EXPERT in principal.roles and layer == "raw":
        return False
    if material["task_id"] is None:
        return layer != "raw"
    task = task_repo.get_task(conn, material["task_id"])
    if task is None:
        return False
    # reference stays closed to reviewers until the task passes review.
    if layer == "reference" and ROLE_DOMAIN_REVIEWER in principal.roles:
        return task["state"] in ("approved", "frozen", "packaged", "package_validated", "ingested")
    return True


def assert_readable(conn: sqlite3.Connection, principal: Principal, material: Dict[str, Any]) -> None:
    if not _layer_visible(conn, principal, material):
        raise forbidden(f"material:read:{material['layer']}")


def agent_visible(conn: sqlite3.Connection, task_id: str) -> List[Dict[str, Any]]:
    """View used by the agent service account.

    reference is never included; raw is excluded as well, matching the P1 rule
    that the agent sees deidentified/work material only.
    """

    rows = material_repo.list_materials(conn, task_id)
    return [row for row in rows if row["layer"] in ("deidentified", "work") and row["status"] == "active"]
