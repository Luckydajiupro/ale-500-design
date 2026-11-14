from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from .base import row_to_dict, rows_to_dicts


def insert_review(
    conn: sqlite3.Connection,
    review_id: str,
    task_id: str,
    version_no: int,
    kind: str,
    created_at: str,
    sla_due_at: Optional[str] = None,
    round_no: int = 1,
    state: str = "pending",
) -> None:
    conn.execute(
        """INSERT INTO reviews
           (review_id, task_id, version_no, round_no, kind, state, sla_due_at, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (review_id, task_id, version_no, round_no, kind, state, sla_due_at, created_at),
    )


def get_review(conn: sqlite3.Connection, review_id: str) -> Optional[Dict[str, Any]]:
    return row_to_dict(conn.execute("SELECT * FROM reviews WHERE review_id = ?", (review_id,)).fetchone())


def list_reviews(conn: sqlite3.Connection, task_id: str) -> List[Dict[str, Any]]:
    return rows_to_dicts(
        conn.execute(
            "SELECT * FROM reviews WHERE task_id = ? ORDER BY round_no, kind", (task_id,)
        ).fetchall()
    )


def queue(
    conn: sqlite3.Connection,
    kind: Optional[str] = None,
    state: str = "pending",
    limit: int = 50,
) -> List[Dict[str, Any]]:
    clauses = ["r.state = ?"]
    params: List[Any] = [state]
    if kind:
        clauses.append("r.kind = ?")
        params.append(kind)
    params.append(limit)
    return rows_to_dicts(
        conn.execute(
            f"""SELECT r.*, t.domain_code, t.subdomain_code, t.owner_expert_id
                FROM reviews r JOIN tasks t ON t.task_id = r.task_id
                WHERE {' AND '.join(clauses)}
                ORDER BY r.created_at LIMIT ?""",
            params,
        ).fetchall()
    )


def claim_review(conn: sqlite3.Connection, review_id: str, reviewer_id: str, at: str) -> int:
    cursor = conn.execute(
        """UPDATE reviews SET state = 'in_review', reviewer_id = ?, claimed_at = ?
           WHERE review_id = ? AND state = 'pending' AND reviewer_id IS NULL""",
        (reviewer_id, at, review_id),
    )
    return cursor.rowcount


def assign(
    conn: sqlite3.Connection,
    assignment_id: str,
    review_id: str,
    task_id: str,
    reviewer_id: str,
    strategy: str,
    assigned_at: str,
    due_at: Optional[str],
) -> None:
    conn.execute(
        """INSERT OR REPLACE INTO assignments
           (assignment_id, review_id, task_id, reviewer_id, strategy, state, assigned_at, due_at)
           VALUES (?, ?, ?, ?, ?, 'assigned', ?, ?)""",
        (assignment_id, review_id, task_id, reviewer_id, strategy, assigned_at, due_at),
    )


def list_assignments(conn: sqlite3.Connection, task_id: str) -> List[Dict[str, Any]]:
    return rows_to_dicts(
        conn.execute("SELECT * FROM assignments WHERE task_id = ? ORDER BY assigned_at", (task_id,)).fetchall()
    )


def decide(
    conn: sqlite3.Connection,
    review_id: str,
    decision: str,
    state: str,
    reason: str,
    at: str,
) -> None:
    conn.execute(
        """UPDATE reviews SET decision = ?, state = ?, decision_reason = ?, decided_at = ?
           WHERE review_id = ?""",
        (decision, state, reason, at, review_id),
    )


def insert_item(
    conn: sqlite3.Connection,
    item_id: str,
    review_id: str,
    dimension: str,
    field_path: Optional[str],
    severity: str,
    verdict: str,
    comment: str,
    created_at: str,
) -> None:
    conn.execute(
        """INSERT INTO review_items
           (item_id, review_id, dimension, field_path, severity, verdict, comment, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (item_id, review_id, dimension, field_path, severity, verdict, comment, created_at),
    )


def list_items(conn: sqlite3.Connection, review_id: str) -> List[Dict[str, Any]]:
    return rows_to_dicts(
        conn.execute(
            "SELECT * FROM review_items WHERE review_id = ? ORDER BY created_at", (review_id,)
        ).fetchall()
    )
