from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from .base import row_to_dict, rows_to_dicts


def insert_snapshot(
    conn: sqlite3.Connection,
    snapshot_id: str,
    task_id: str,
    version_no: int,
    payload_json: str,
    manifest_json: str,
    native_hash: str,
    frozen_by: str,
    frozen_at: str,
) -> None:
    conn.execute(
        """INSERT INTO snapshots
           (snapshot_id, task_id, version_no, payload_json, manifest_json, native_hash, hash_status, frozen_by, frozen_at)
           VALUES (?, ?, ?, ?, ?, ?, 'candidate', ?, ?)""",
        (snapshot_id, task_id, version_no, payload_json, manifest_json, native_hash, frozen_by, frozen_at),
    )


def get_snapshot(conn: sqlite3.Connection, snapshot_id: str) -> Optional[Dict[str, Any]]:
    return row_to_dict(
        conn.execute("SELECT * FROM snapshots WHERE snapshot_id = ?", (snapshot_id,)).fetchone()
    )


def get_snapshot_for_task(conn: sqlite3.Connection, task_id: str, version_no: int) -> Optional[Dict[str, Any]]:
    return row_to_dict(
        conn.execute(
            "SELECT * FROM snapshots WHERE task_id = ? AND version_no = ?", (task_id, version_no)
        ).fetchone()
    )


def insert_package(
    conn: sqlite3.Connection,
    package_id: str,
    snapshot_id: str,
    task_id: str,
    version_no: int,
    state: str,
    built_by: str,
    created_at: str,
) -> None:
    conn.execute(
        """INSERT INTO packages
           (package_id, snapshot_id, task_id, version_no, state, built_by, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (package_id, snapshot_id, task_id, version_no, state, built_by, created_at, created_at),
    )


def get_package(conn: sqlite3.Connection, package_id: str) -> Optional[Dict[str, Any]]:
    return row_to_dict(conn.execute("SELECT * FROM packages WHERE package_id = ?", (package_id,)).fetchone())


def get_package_for_task(conn: sqlite3.Connection, task_id: str, version_no: int) -> Optional[Dict[str, Any]]:
    return row_to_dict(
        conn.execute(
            "SELECT * FROM packages WHERE task_id = ? AND version_no = ? ORDER BY created_at DESC LIMIT 1",
            (task_id, version_no),
        ).fetchone()
    )


def list_packages(conn: sqlite3.Connection, state: Optional[str] = None) -> List[Dict[str, Any]]:
    if state:
        rows = conn.execute("SELECT * FROM packages WHERE state = ? ORDER BY created_at", (state,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM packages ORDER BY created_at").fetchall()
    return rows_to_dicts(rows)


def set_package_state(
    conn: sqlite3.Connection,
    package_id: str,
    state: str,
    updated_at: str,
    package_hash: Optional[str] = None,
    failure_code: Optional[str] = None,
) -> None:
    conn.execute(
        """UPDATE packages SET state = ?, updated_at = ?,
           package_hash = COALESCE(?, package_hash), failure_code = COALESCE(?, failure_code)
           WHERE package_id = ?""",
        (state, updated_at, package_hash, failure_code, package_id),
    )


def insert_validation(
    conn: sqlite3.Connection,
    validation_id: str,
    package_id: str,
    layer: str,
    code: str,
    severity: str,
    passed: bool,
    message: str,
    report_json: str,
    created_at: str,
) -> None:
    conn.execute(
        """INSERT INTO package_validations
           (validation_id, package_id, layer, code, severity, passed, message, report_json, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (validation_id, package_id, layer, code, severity, 1 if passed else 0, message, report_json, created_at),
    )


def list_validations(conn: sqlite3.Connection, package_id: str) -> List[Dict[str, Any]]:
    return rows_to_dicts(
        conn.execute(
            "SELECT * FROM package_validations WHERE package_id = ? ORDER BY layer, code", (package_id,)
        ).fetchall()
    )


def insert_ingest(
    conn: sqlite3.Connection,
    ingest_id: str,
    package_id: str,
    package_hash: str,
    state: str,
    received_at: str,
    received_by: str,
    receipt_json: str,
) -> None:
    conn.execute(
        """INSERT INTO ingest_records
           (ingest_id, package_id, package_hash, state, received_at, received_by, receipt_json)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (ingest_id, package_id, package_hash, state, received_at, received_by, receipt_json),
    )


def get_ingest(conn: sqlite3.Connection, ingest_id: str) -> Optional[Dict[str, Any]]:
    return row_to_dict(
        conn.execute("SELECT * FROM ingest_records WHERE ingest_id = ?", (ingest_id,)).fetchone()
    )


def get_ingest_by_hash(conn: sqlite3.Connection, package_hash: str) -> Optional[Dict[str, Any]]:
    return row_to_dict(
        conn.execute("SELECT * FROM ingest_records WHERE package_hash = ?", (package_hash,)).fetchone()
    )


def list_ingests(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    return rows_to_dicts(
        conn.execute("SELECT * FROM ingest_records ORDER BY received_at DESC").fetchall()
    )
