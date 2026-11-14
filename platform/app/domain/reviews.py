"""Review claim and decision services.

The state machine owns task transitions. This module owns the review row and
the review-item evidence, and it refuses a decision from a reviewer who did not
claim the review or whose role does not match the queue kind.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from ..adapters import new_id, now, now_plus
from ..auth import Principal, ROLE_DOMAIN_REVIEWER, ROLE_QUALITY_REVIEWER, require
from ..errors import conflict, forbidden, not_found
from ..repo import reviews as review_repo
from ..repo import tasks as task_repo
from . import audit
from . import state_machine as sm


def _kind_role(kind: str) -> str:
    return ROLE_DOMAIN_REVIEWER if kind == "domain" else ROLE_QUALITY_REVIEWER


def claim(conn: sqlite3.Connection, principal: Principal, review_id: str) -> Dict[str, Any]:
    require(principal, "review:claim")
    review = review_repo.get_review(conn, review_id)
    if review is None:
        raise not_found("评审")
    if review["state"] != "pending":
        raise conflict("REVIEW_NOT_PENDING", "评审已被领取或已结束")
    if _kind_role(review["kind"]) not in principal.roles:
        raise forbidden("review:claim")
    changed = review_repo.claim_review(conn, review_id, principal.user_id, now())
    if not changed:
        raise conflict("REVIEW_ALREADY_CLAIMED", "评审已被其他审核人领取")
    task = task_repo.get_task(conn, review["task_id"])
    if task is not None and task["state"] == sm.AUTO_CHECKED:
        previous = sm.apply(conn, task, "start_review", "domain_reviewer", now())
        audit.record(conn, principal, "review.claim", "review", review_id, previous, sm.IN_REVIEW, {"kind": review["kind"]})
    else:
        audit.record(conn, principal, "review.claim", "review", review_id, "pending", "in_review", {"kind": review["kind"]})
    return review_repo.get_review(conn, review_id) or {}


def decide(
    conn: sqlite3.Connection,
    principal: Principal,
    review_id: str,
    decision: str,
    reason: str,
    items: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    require(principal, "review:decide")
    review = review_repo.get_review(conn, review_id)
    if review is None:
        raise not_found("评审")
    if review["state"] not in ("pending", "in_review"):
        raise conflict("REVIEW_CLOSED", "评审已结束")
    if review["reviewer_id"] not in (None, principal.user_id):
        raise forbidden("review:decide")
    if _kind_role(review["kind"]) not in principal.roles:
        raise forbidden("review:decide")
    if decision not in ("pass", "return"):
        raise conflict("REVIEW_DECISION", "decision 只能是 pass 或 return")
    if decision == "return" and not reason.strip():
        raise conflict("REVIEW_REASON_REQUIRED", "退回必须填写问题")

    task = task_repo.get_task(conn, review["task_id"])
    if task is None:
        raise not_found("任务")
    if task["state"] != sm.IN_REVIEW:
        raise conflict("TASK_NOT_IN_REVIEW", f"任务状态 {task['state']} 不在评审中")

    if review["state"] == "pending":
        review_repo.claim_review(conn, review_id, principal.user_id, now())

    for item in items or []:
        review_repo.insert_item(
            conn,
            item_id=new_id("ri"),
            review_id=review_id,
            dimension=str(item.get("dimension") or "correctness"),
            field_path=item.get("field_path"),
            severity=str(item.get("severity") or "suggestion"),
            verdict=str(item.get("verdict") or "suggestion"),
            comment=str(item.get("comment") or ""),
            created_at=now(),
        )

    if decision == "return":
        review_repo.decide(conn, review_id, "return", "returned", reason, now())
        event = "return_by_review" if review["kind"] == "domain" else "quality_return"
        role = "domain_reviewer" if review["kind"] == "domain" else "quality_reviewer"
        previous = sm.apply(conn, task, event, role, now())
        audit.record(
            conn,
            principal,
            "review.return",
            "review",
            review_id,
            previous,
            sm.RETURNED,
            {"kind": review["kind"], "reason": reason},
        )
        return {"review_id": review_id, "task_id": task["task_id"], "decision": "return", "task_state": sm.RETURNED}

    review_repo.decide(conn, review_id, "pass", "passed", reason, now())
    if review["kind"] == "domain":
        # Domain pass keeps the task in review and opens the quality queue.
        existing = [
            item
            for item in review_repo.list_reviews(conn, task["task_id"])
            if item["kind"] == "quality" and item["version_no"] == review["version_no"]
        ]
        if not existing:
            review_repo.insert_review(
                conn,
                review_id=new_id("rev"),
                task_id=task["task_id"],
                version_no=review["version_no"],
                kind="quality",
                created_at=now(),
                sla_due_at=now_plus(days=5),
                round_no=review["round_no"],
            )
        audit.record(conn, principal, "review.domain_pass", "review", review_id, sm.IN_REVIEW, sm.IN_REVIEW, {"version_no": review["version_no"]})
        return {"review_id": review_id, "task_id": task["task_id"], "decision": "pass", "task_state": sm.IN_REVIEW}

    previous = sm.apply(conn, task, "quality_pass", "quality_reviewer", now())
    audit.record(conn, principal, "review.quality_pass", "review", review_id, previous, sm.APPROVED, {"version_no": review["version_no"]})
    return {"review_id": review_id, "task_id": task["task_id"], "decision": "pass", "task_state": sm.APPROVED}


def queue_for(conn: sqlite3.Connection, principal: Principal) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if ROLE_DOMAIN_REVIEWER in principal.roles:
        rows.extend(review_repo.queue(conn, kind="domain"))
    if ROLE_QUALITY_REVIEWER in principal.roles:
        rows.extend(review_repo.queue(conn, kind="quality"))
    return rows
