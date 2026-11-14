from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from .base import row_to_dict, rows_to_dicts


def insert_run(
    conn: sqlite3.Connection,
    run_id: str,
    task_id: str,
    capability: str,
    model: str,
    model_version: str,
    prompt_hash: str,
    input_hash: str,
    status: str,
    latency_ms: int,
    cost_cents: int,
    created_at: str,
) -> None:
    conn.execute(
        """INSERT INTO agent_runs
           (run_id, task_id, capability, model, model_version, prompt_hash, input_hash,
            status, latency_ms, cost_cents, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (run_id, task_id, capability, model, model_version, prompt_hash, input_hash, status, latency_ms, cost_cents, created_at),
    )


def get_run(conn: sqlite3.Connection, run_id: str) -> Optional[Dict[str, Any]]:
    return row_to_dict(conn.execute("SELECT * FROM agent_runs WHERE run_id = ?", (run_id,)).fetchone())


def insert_suggestion(
    conn: sqlite3.Connection,
    suggestion_id: str,
    run_id: str,
    task_id: str,
    field_path: str,
    suggested_value: str,
    confidence: float,
    model: str,
    model_version: str,
    prompt_hash: str,
    input_hash: str,
    created_at: str,
) -> None:
    conn.execute(
        """INSERT INTO agent_suggestions
           (suggestion_id, run_id, task_id, field_path, suggested_value, confidence,
            model, model_version, prompt_hash, input_hash, state, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'proposed', ?)""",
        (
            suggestion_id,
            run_id,
            task_id,
            field_path,
            suggested_value,
            confidence,
            model,
            model_version,
            prompt_hash,
            input_hash,
            created_at,
        ),
    )


def get_suggestion(conn: sqlite3.Connection, suggestion_id: str) -> Optional[Dict[str, Any]]:
    return row_to_dict(
        conn.execute("SELECT * FROM agent_suggestions WHERE suggestion_id = ?", (suggestion_id,)).fetchone()
    )


def list_suggestions(conn: sqlite3.Connection, task_id: str) -> List[Dict[str, Any]]:
    return rows_to_dicts(
        conn.execute(
            "SELECT * FROM agent_suggestions WHERE task_id = ? ORDER BY created_at", (task_id,)
        ).fetchall()
    )


def confirm_suggestion(
    conn: sqlite3.Connection,
    suggestion_id: str,
    decision: str,
    state: str,
    edited_value: Optional[str],
    confirmed_by: str,
    confirmed_at: str,
    applied_version_no: Optional[int],
) -> int:
    cursor = conn.execute(
        """UPDATE agent_suggestions
           SET decision = ?, state = ?, edited_value = ?, confirmed_by = ?, confirmed_at = ?,
               applied_version_no = ?
           WHERE suggestion_id = ? AND state = 'proposed'""",
        (decision, state, edited_value, confirmed_by, confirmed_at, applied_version_no, suggestion_id),
    )
    return cursor.rowcount


def adoption_stats(conn: sqlite3.Connection) -> Dict[str, int]:
    row = conn.execute(
        """SELECT
             COUNT(*) AS total,
             SUM(CASE WHEN decided_by_human = 1 THEN 1 ELSE 0 END) AS decided,
             SUM(CASE WHEN decision IN ('accepted', 'edited') THEN 1 ELSE 0 END) AS adopted,
             SUM(CASE WHEN decision = 'rejected' THEN 1 ELSE 0 END) AS rejected
           FROM (SELECT decision, CASE WHEN decision IS NULL THEN 0 ELSE 1 END AS decided_by_human
                 FROM agent_suggestions)"""
    ).fetchone()
    return {
        "suggestions": int(row["total"] or 0),
        "decided": int(row["decided"] or 0),
        "adopted": int(row["adopted"] or 0),
        "rejected": int(row["rejected"] or 0),
    }
