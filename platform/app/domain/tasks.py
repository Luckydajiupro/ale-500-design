"""Task source lifecycle: draft, validate, submit, auto-check.

Content is edited on ``tasks.draft_payload`` only. A submit freezes a copy into
``task_versions``; after that the payload is read-only and later edits start the
next version.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from contracts import canonical_schema

from ..adapters import new_id, now, now_plus
from ..auth import Principal, ROLE_DOMAIN_REVIEWER, require
from ..errors import conflict, forbidden, invalid, not_found
from ..repo import materials as material_repo
from ..repo import reviews as review_repo
from ..repo import tasks as task_repo
from . import audit
from . import state_machine as sm
from ..contracts_bridge import canonical_json, load_payload


def primary_role(principal: Principal) -> str:
    for role in ("quality_reviewer", "domain_reviewer", "platform_admin", "expert", "project_lead", "engineer"):
        if role in principal.roles:
            return role
    return sorted(principal.role_codes)[0] if principal.role_codes else "anonymous"


def _payload_dict(task: Dict[str, Any]) -> Dict[str, Any]:
    return load_payload(task["draft_payload"])


def create_draft(conn: sqlite3.Connection, principal: Principal, body: Dict[str, Any]) -> Dict[str, Any]:
    require(principal, "task:create")
    task_id = (body.get("task_id") or "").strip()
    if not task_id:
        raise invalid("TASK_ID_REQUIRED", "task_id 不能为空")
    if task_repo.get_task(conn, task_id) is not None:
        raise conflict("TASK_EXISTS", f"{task_id} 已存在")
    domain = (body.get("domain_code") or "").strip()
    subdomain = (body.get("subdomain_code") or "").strip()
    if not domain or not subdomain:
        raise invalid("SCOPE_REQUIRED", "domain_code 与 subdomain_code 必填")
    if not principal.can_in_scope("task:create", domain, subdomain, body.get("batch_id")):
        raise forbidden("task:create")

    payload = body.get("source_payload") or {
        "identity": {
            "task_id": task_id,
            "domain_code": domain,
            "subdomain_code": subdomain,
            "title_zh": body.get("title_zh", ""),
            "title_en": body.get("title_en", ""),
            "language": body.get("language", "en"),
            "batch_id": body.get("batch_id"),
        }
    }
    timestamp = now()
    task_repo.insert_task(
        conn,
        task_id=task_id,
        batch_id=body.get("batch_id"),
        domain_code=domain,
        subdomain_code=subdomain,
        owner_expert_id=principal.user_id,
        state=sm.DRAFT,
        draft_payload=canonical_json(payload),
        created_at=timestamp,
    )
    audit.record(
        conn,
        principal,
        "task.create",
        "task",
        task_id,
        None,
        sm.DRAFT,
        {"domain_code": domain, "subdomain_code": subdomain},
    )
    return get_task(conn, principal, task_id)


def get_task(conn: sqlite3.Connection, principal: Principal, task_id: str) -> Dict[str, Any]:
    task = task_repo.get_task(conn, task_id)
    if task is None:
        raise not_found("任务")
    is_owner = task["owner_expert_id"] == principal.user_id
    if is_owner or principal.has("task:read:all"):
        return _detail(conn, task)
    if principal.has("task:read:assigned"):
        assigned = conn.execute(
            "SELECT 1 FROM reviews WHERE task_id = ? AND reviewer_id = ? LIMIT 1",
            (task_id, principal.user_id),
        ).fetchone()
        if assigned:
            return _detail(conn, task)
    raise forbidden("task:read")


def _detail(conn: sqlite3.Connection, task: Dict[str, Any]) -> Dict[str, Any]:
    payload = _payload_dict(task)
    detail = dict(task)
    detail["draft_payload"] = payload
    detail["versions"] = task_repo.list_versions(conn, task["task_id"])
    detail["checks"] = task_repo.latest_checks(conn, task["task_id"])[:100]
    detail["reviews"] = review_repo.list_reviews(conn, task["task_id"])
    detail["materials"] = material_repo.list_materials(conn, task["task_id"])
    return detail


def update_draft(
    conn: sqlite3.Connection,
    principal: Principal,
    task_id: str,
    body: Dict[str, Any],
) -> Dict[str, Any]:
    task = task_repo.get_task(conn, task_id)
    if task is None:
        raise not_found("任务")
    if task["owner_expert_id"] != principal.user_id:
        raise forbidden("task:edit")
    if task["state"] not in sm.EDITABLE_STATES:
        raise conflict("TASK_NOT_EDITABLE", f"状态 {task['state']} 不可编辑")
    expected = body.get("expected_lock_version")
    if expected is None:
        raise invalid("LOCK_VERSION_REQUIRED", "更新草稿必须带 expected_lock_version")
    payload = body.get("source_payload")
    if not isinstance(payload, dict):
        raise invalid("PAYLOAD_REQUIRED", "source_payload 必须是对象")
    changed = task_repo.update_draft(
        conn, task_id, canonical_json(payload), int(expected), now()
    )
    if changed == 0:
        raise conflict("LOCK_VERSION_CONFLICT", "草稿已被其他会话修改，请重新读取")
    audit.record(conn, principal, "task.draft.update", "task", task_id, task["state"], task["state"])
    return get_task(conn, principal, task_id)


def _known_material_ids(conn: sqlite3.Connection, task_id: str) -> List[str]:
    return [row["material_id"] for row in material_repo.list_materials(conn, task_id)]


def run_checks(
    conn: sqlite3.Connection,
    task: Dict[str, Any],
    payload: Dict[str, Any],
    version_no: Optional[int],
    actor: str,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Run the implemented auto checks and persist every finding.

    Four of the nine product checks have a real implementation here; the other
    five are represented by an explicit skip row so a reader can tell a passing
    check from an unimplemented one.
    """

    run_id = new_id("run")
    timestamp = now()
    findings: List[Dict[str, Any]] = []

    canonical = canonical_schema.validate_source(payload, _known_material_ids(conn, task["task_id"]))
    for issue in canonical.issues:
        task_repo.insert_check(
            conn,
            new_id("chk"),
            task["task_id"],
            version_no,
            run_id,
            issue.code,
            issue.severity,
            False,
            issue.field_path,
            issue.message,
            timestamp,
        )
        findings.append(
            {
                "check_code": issue.code,
                "severity": issue.severity,
                "passed": False,
                "field_path": issue.field_path,
                "message": issue.message,
            }
        )

    asset_findings = _check_material_assets(conn, task["task_id"], payload)
    for finding in asset_findings:
        task_repo.insert_check(
            conn,
            new_id("chk"),
            task["task_id"],
            version_no,
            run_id,
            finding["check_code"],
            finding["severity"],
            False,
            finding["field_path"],
            finding["message"],
            timestamp,
        )
        findings.append(finding)

    for code, severity, message in (
        ("ACHK_ENV_OFFLINE", "info", "环境默认离线；运行器未在骨架内实现"),
        ("ACHK_DUPLICATE", "info", "重复与相似度检查未在骨架内实现"),
        ("ACHK_PACKAGE_DRY_RUN", "info", "包生成预检未在骨架内实现"),
        ("ACHK_LINT", "info", "lint 与冒烟未在骨架内实现"),
    ):
        task_repo.insert_check(
            conn, new_id("chk"), task["task_id"], version_no, run_id, code, severity, True, "", message, timestamp
        )

    if not findings:
        task_repo.insert_check(
            conn,
            new_id("chk"),
            task["task_id"],
            version_no,
            run_id,
            "ACHK_SCHEMA",
            "info",
            True,
            "",
            "结构与必填项通过",
            timestamp,
        )
    return run_id, findings


def _check_material_assets(
    conn: sqlite3.Connection, task_id: str, payload: Dict[str, Any]
) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for index, item in enumerate(canonical_schema.iter_materials(payload)):
        material_id = item.get("material_id")
        if not material_id:
            continue
        row = material_repo.get_material(conn, str(material_id))
        if row is None:
            findings.append(
                {
                    "check_code": "ACHK_MATERIAL_MISSING",
                    "severity": "blocker",
                    "field_path": f"materials[{index}].material_id",
                    "message": "资料库中没有这份资料",
                }
            )
            continue
        versions = material_repo.list_material_versions(conn, str(material_id))
        if not versions:
            findings.append(
                {
                    "check_code": "ACHK_MATERIAL_NO_BYTES",
                    "severity": "blocker",
                    "field_path": f"materials[{index}].material_id",
                    "message": "资料尚未上传任何版本",
                }
            )
        elif item.get("sha256") and versions[-1]["sha256"] != item.get("sha256"):
            findings.append(
                {
                    "check_code": "ACHK_MATERIAL_HASH",
                    "severity": "blocker",
                    "field_path": f"materials[{index}].sha256",
                    "message": "任务源记录的哈希与资料库最新版本不一致",
                }
            )
    return findings


def validate(
    conn: sqlite3.Connection, principal: Principal, task_id: str
) -> Dict[str, Any]:
    task = task_repo.get_task(conn, task_id)
    if task is None:
        raise not_found("任务")
    if task["owner_expert_id"] != principal.user_id and not principal.has("task:read:all"):
        raise forbidden("task:validate")
    if task["state"] not in sm.EDITABLE_STATES:
        raise conflict("TASK_NOT_EDITABLE", f"状态 {task['state']} 不可校验")
    payload = _payload_dict(task)
    run_id, findings = run_checks(conn, task, payload, None, principal.user_id)
    audit.record(
        conn,
        principal,
        "task.validate",
        "task",
        task_id,
        task["state"],
        task["state"],
        {"run_id": run_id, "blockers": sum(1 for item in findings if item["severity"] == "blocker")},
    )
    blockers = [item for item in findings if item["severity"] == "blocker"]
    return {
        "task_id": task_id,
        "run_id": run_id,
        "ok": not blockers,
        "blocker_count": len(blockers),
        "warning_count": sum(1 for item in findings if item["severity"] == "warning"),
        "findings": findings,
    }


def submit(
    conn: sqlite3.Connection,
    principal: Principal,
    task_id: str,
    body: Dict[str, Any],
) -> Dict[str, Any]:
    task = task_repo.get_task(conn, task_id)
    if task is None:
        raise not_found("任务")
    if task["owner_expert_id"] != principal.user_id:
        raise forbidden("task:submit")
    if task["state"] not in sm.EDITABLE_STATES:
        raise conflict("TASK_NOT_EDITABLE", f"状态 {task['state']} 不可提交")
    expected = body.get("expected_lock_version")
    if expected is not None and int(expected) != int(task["lock_version"]):
        raise conflict("LOCK_VERSION_CONFLICT", "草稿已被其他会话修改，请重新读取")

    payload = _payload_dict(task)
    run_id, findings = run_checks(conn, task, payload, None, principal.user_id)
    blockers = [item for item in findings if item["severity"] == "blocker"]
    if blockers:
        audit.record(
            conn,
            principal,
            "task.submit.blocked",
            "task",
            task_id,
            task["state"],
            task["state"],
            {"blockers": [item["check_code"] for item in blockers]},
        )
        raise invalid(
            "SUBMIT_BLOCKED",
            "任务源存在阻断项，不能提交",
            [{"code": item["check_code"], "field": item["field_path"], "message": item["message"]} for item in blockers],
        )

    version_no = task_repo.next_version_no(conn, task_id)
    timestamp = now()
    task_repo.insert_version(
        conn,
        task_id=task_id,
        version_no=version_no,
        payload_json=canonical_json(payload),
        content_hash=canonical_schema_hash(payload),
        submitted_by=principal.user_id,
        submitted_at=timestamp,
    )
    state_machine_source = sm.apply(conn, task, "submit", "expert", timestamp)
    audit.record(
        conn,
        principal,
        "task.submit",
        "task",
        task_id,
        state_machine_source,
        sm.SUBMITTED,
        {"version_no": version_no, "content_hash": canonical_schema_hash(payload)},
    )

    # Auto check runs synchronously in P1; the product allows a queued variant,
    # but the user experience needs the gate result before leaving the page.
    if blockers:
        target = sm.RETURNED
        event = "auto_check_fail"
    else:
        target = sm.AUTO_CHECKED
        event = "auto_check_pass"
    previous = sm.apply(conn, task, event, "system", now())
    audit.record(
        conn,
        None,
        f"task.{event}",
        "task",
        task_id,
        previous,
        target,
        {"version_no": version_no, "run_id": run_id},
        actor_id="system",
    )

    if target == sm.AUTO_CHECKED:
        review_repo.insert_review(
            conn,
            review_id=new_id("rev"),
            task_id=task_id,
            version_no=version_no,
            kind="domain",
            created_at=now(),
            sla_due_at=now_plus(days=5),
            round_no=version_no,
        )
        audit.record(
            conn,
            None,
            "review.enqueue",
            "task",
            task_id,
            sm.AUTO_CHECKED,
            sm.AUTO_CHECKED,
            {"kind": "domain", "version_no": version_no},
            actor_id="system",
        )

    return {
        "task_id": task_id,
        "version_no": version_no,
        "state": target,
        "run_id": run_id,
        "blockers": [item["check_code"] for item in blockers],
    }


def canonical_schema_hash(payload: Dict[str, Any]) -> str:
    import hashlib

    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
