from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from .base import row_to_dict, rows_to_dicts


def create_user(
    conn: sqlite3.Connection,
    user_id: str,
    email: str,
    display_name: str,
    status: str = "active",
    created_at: str = "",
) -> None:
    conn.execute(
        "INSERT INTO users (user_id, email, display_name, status, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, email, display_name, status, created_at),
    )


def get_user(conn: sqlite3.Connection, user_id: str) -> Optional[Dict[str, Any]]:
    return row_to_dict(conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone())


def get_user_by_email(conn: sqlite3.Connection, email: str) -> Optional[Dict[str, Any]]:
    return row_to_dict(conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone())


def disable_user(conn: sqlite3.Connection, user_id: str, at: str) -> None:
    conn.execute(
        "UPDATE users SET status = 'disabled', deactivated_at = ? WHERE user_id = ?", (at, user_id)
    )


def upsert_role(conn: sqlite3.Connection, role_code: str, name_zh: str, description: str = "") -> None:
    conn.execute(
        "INSERT OR REPLACE INTO roles (role_code, name_zh, description) VALUES (?, ?, ?)",
        (role_code, name_zh, description),
    )


def grant_role(
    conn: sqlite3.Connection,
    user_role_id: str,
    user_id: str,
    role_code: str,
    granted_at: str,
    granted_by: str = "seed",
    scope_domain: str = "*",
    scope_subdomain: str = "*",
    scope_batch: str = "*",
) -> None:
    conn.execute(
        """INSERT OR REPLACE INTO user_roles
           (user_role_id, user_id, role_code, scope_domain, scope_subdomain, scope_batch, granted_at, granted_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_role_id, user_id, role_code, scope_domain, scope_subdomain, scope_batch, granted_at, granted_by),
    )


def list_roles(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    return rows_to_dicts(conn.execute("SELECT * FROM roles ORDER BY role_code").fetchall())


def list_users(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    return rows_to_dicts(conn.execute("SELECT * FROM users ORDER BY created_at").fetchall())


def create_batch(
    conn: sqlite3.Connection, batch_id: str, name: str, quota_total: int, state: str = "planned"
) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO batches (batch_id, name, quota_total, state) VALUES (?, ?, ?, ?)",
        (batch_id, name, quota_total, state),
    )


def get_batch(conn: sqlite3.Connection, batch_id: str) -> Optional[Dict[str, Any]]:
    return row_to_dict(conn.execute("SELECT * FROM batches WHERE batch_id = ?", (batch_id,)).fetchone())
