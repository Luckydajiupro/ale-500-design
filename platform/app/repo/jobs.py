from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from .base import row_to_dict, rows_to_dicts


def insert_job(
    conn: sqlite3.Connection,
    job_id: str,
    kind: str,
    task_id: Optional[str],
    payload_json: str,
    available_at: str,
    created_at: str,
    max_attempts: int = 3,
) -> None:
    conn.execute(
        """INSERT INTO jobs
           (job_id, kind, task_id, payload_json, state, attempts, max_attempts,
            available_at, created_at, updated_at)
           VALUES (?, ?, ?, ?, 'queued', 0, ?, ?, ?, ?)""",
        (job_id, kind, task_id, payload_json, max_attempts, available_at, created_at, created_at),
    )


def get_job(conn: sqlite3.Connection, job_id: str) -> Optional[Dict[str, Any]]:
    return row_to_dict(conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone())


def list_jobs(conn: sqlite3.Connection, task_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    if task_id:
        return rows_to_dicts(
            conn.execute(
                "SELECT * FROM jobs WHERE task_id = ? ORDER BY created_at DESC LIMIT ?", (task_id, limit)
            ).fetchall()
        )
    return rows_to_dicts(conn.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall())


def claim_next(conn: sqlite3.Connection, worker_id: str, at: str) -> Optional[Dict[str, Any]]:
    row = conn.execute(
        "SELECT * FROM jobs WHERE state = 'queued' AND available_at <= ? ORDER BY created_at LIMIT 1",
        (at,),
    ).fetchone()
    if row is None:
        return None
    job = dict(row)
    updated = conn.execute(
        "UPDATE jobs SET state = 'running', locked_by = ?, locked_at = ?, updated_at = ? "
        "WHERE job_id = ? AND state = 'queued'",
        (worker_id, at, at, job["job_id"]),
    )
    if updated.rowcount != 1:
        return None
    return get_job(conn, job["job_id"])


def finish(
    conn: sqlite3.Connection,
    job_id: str,
    state: str,
    result_json: Optional[str],
    error: Optional[str],
    at: str,
) -> None:
    conn.execute(
        "UPDATE jobs SET state = ?, result_json = ?, last_error = ?, locked_by = NULL, locked_at = NULL, updated_at = ? "
        "WHERE job_id = ?",
        (state, result_json, error, at, job_id),
    )


def retry(conn: sqlite3.Connection, job_id: str, attempts: int, available_at: str, error: str, at: str) -> None:
    conn.execute(
        "UPDATE jobs SET state = 'queued', attempts = ?, available_at = ?, last_error = ?, "
        "locked_by = NULL, locked_at = NULL, updated_at = ? WHERE job_id = ?",
        (attempts, available_at, error[:2000], at, job_id),
    )
