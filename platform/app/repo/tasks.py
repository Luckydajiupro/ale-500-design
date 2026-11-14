from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from .base import row_to_dict, rows_to_dicts


def insert_task(
    conn: sqlite3.Connection,
    task_id: str,
    batch_id: Optional[str],
    domain_code: str,
    subdomain_code: str,
    owner_expert_id: str,
    state: str,
    draft_payload: str,
    created_at: str,
) -> None:
    conn.execute(
        """INSERT INTO tasks
           (task_id, batch_id, domain_code, subdomain_code, owner_expert_id, state,
            draft_payload, current_version_no, lock_version, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, 0, 1, ?, ?)""",
        (task_id, batch_id, domain_code, subdomain_code, owner_expert_id, state, draft_payload, created_at, created_at),
    )


def get_task(conn: sqlite3.Connection, task_id: str) -> Optional[Dict[str, Any]]:
    return row_to_dict(conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone())


def get_task_for_update(conn: sqlite3.Connection, task_id: str) -> Optional[Dict[str, Any]]:
    return get_task(conn, task_id)


def update_draft(
    conn: sqlite3.Connection,
    task_id: str,
    draft_payload: str,
    expected_lock_version: int,
    updated_at: str,
) -> int:
    cursor = conn.execute(
        """UPDATE tasks SET draft_payload = ?, lock_version = lock_version + 1, updated_at = ?
           WHERE task_id = ? AND lock_version = ?""",
        (draft_payload, updated_at, task_id, expected_lock_version),
    )
    return cursor.rowcount


def set_state(
    conn: sqlite3.Connection,
    task_id: str,
    state: str,
    updated_at: str,
    bump_lock: bool = True,
    return_count: Optional[int] = None,
    void_reason: Optional[str] = None,
) -> None:
    assignments = ["state = ?", "updated_at = ?"]
    params: List[Any] = [state, updated_at]
    if bump_lock:
        assignments.append("lock_version = lock_version + 1")
    if return_count is not None:
        assignments.append("return_count = ?")
        params.append(return_count)
    if void_reason is not None:
        assignments.append("void_reason = ?")
        params.append(void_reason)
    params.append(task_id)
    conn.execute(f"UPDATE tasks SET {', '.join(assignments)} WHERE task_id = ?", params)


def insert_version(
    conn: sqlite3.Connection,
    task_id: str,
    version_no: int,
    payload_json: str,
    content_hash: str,
    submitted_by: str,
    submitted_at: str,
) -> None:
    conn.execute(
        """INSERT INTO task_versions
           (task_id, version_no, payload_json, content_hash, submitted_by, submitted_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (task_id, version_no, payload_json, content_hash, submitted_by, submitted_at),
    )
    conn.execute(
        "UPDATE tasks SET current_version_no = ?, updated_at = ? WHERE task_id = ?",
        (version_no, submitted_at, task_id),
    )


def get_version(conn: sqlite3.Connection, task_id: str, version_no: int) -> Optional[Dict[str, Any]]:
    return row_to_dict(
        conn.execute(
            "SELECT * FROM task_versions WHERE task_id = ? AND version_no = ?", (task_id, version_no)
        ).fetchone()
    )


def list_versions(conn: sqlite3.Connection, task_id: str) -> List[Dict[str, Any]]:
    return rows_to_dicts(
        conn.execute(
            "SELECT * FROM task_versions WHERE task_id = ? ORDER BY version_no", (task_id,)
        ).fetchall()
    )


def next_version_no(conn: sqlite3.Connection, task_id: str) -> int:
    row = conn.execute(
        "SELECT COALESCE(MAX(version_no), 0) AS n FROM task_versions WHERE task_id = ?", (task_id,)
    ).fetchone()
    return int(row["n"]) + 1


def insert_check(
    conn: sqlite3.Connection,
    check_id: str,
    task_id: str,
    version_no: Optional[int],
    run_id: str,
    check_code: str,
    severity: str,
    passed: bool,
    field_path: str,
    message: str,
    created_at: str,
) -> None:
    conn.execute(
        """INSERT INTO checks
           (check_id, task_id, version_no, run_id, check_code, severity, passed, field_path, message, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (check_id, task_id, version_no, run_id, check_code, severity, 1 if passed else 0, field_path, message, created_at),
    )


def checks_for_run(conn: sqlite3.Connection, task_id: str, run_id: str) -> List[Dict[str, Any]]:
    return rows_to_dicts(
        conn.execute(
            "SELECT * FROM checks WHERE task_id = ? AND run_id = ? ORDER BY check_id", (task_id, run_id)
        ).fetchall()
    )


def latest_blocking_checks(conn: sqlite3.Connection, task_id: str) -> List[Dict[str, Any]]:
    row = conn.execute(
        "SELECT run_id FROM checks WHERE task_id = ? ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (task_id,),
    ).fetchone()
    if row is None:
        return []
    return rows_to_dicts(
        conn.execute(
            """SELECT * FROM checks
               WHERE task_id = ? AND run_id = ? AND severity = 'blocker' AND passed = 0""",
            (task_id, row["run_id"]),
        ).fetchall()
    )


def list_tasks(
    conn: sqlite3.Connection,
    state: Optional[str] = None,
    owner_expert_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    clauses = []
    params: List[Any] = []
    if state:
        clauses.append("state = ?")
        params.append(state)
    if owner_expert_id:
        clauses.append("owner_expert_id = ?")
        params.append(owner_expert_id)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    params.extend([limit, offset])
    return rows_to_dicts(
        conn.execute(
            f"SELECT * FROM tasks {where} ORDER BY updated_at DESC LIMIT ? OFFSET ?", params
        ).fetchall()
    )
