from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from .base import row_to_dict, rows_to_dicts


def insert_material(
    conn: sqlite3.Connection,
    material_id: str,
    task_id: Optional[str],
    owner_expert_id: str,
    kind: str,
    role: str,
    layer: str,
    license_type: str,
    license_redistribution: bool,
    pii_level: str,
    source_url: Optional[str],
    source_accessed_at: Optional[str],
    created_at: str,
) -> None:
    conn.execute(
        """INSERT INTO materials
           (material_id, task_id, owner_expert_id, kind, role, layer, license_type,
            license_redistribution, pii_level, source_url, source_accessed_at, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            material_id,
            task_id,
            owner_expert_id,
            kind,
            role,
            layer,
            license_type,
            1 if license_redistribution else 0,
            pii_level,
            source_url,
            source_accessed_at,
            created_at,
        ),
    )


def get_material(conn: sqlite3.Connection, material_id: str) -> Optional[Dict[str, Any]]:
    return row_to_dict(
        conn.execute("SELECT * FROM materials WHERE material_id = ?", (material_id,)).fetchone()
    )


def list_materials(conn: sqlite3.Connection, task_id: str) -> List[Dict[str, Any]]:
    return rows_to_dicts(
        conn.execute(
            "SELECT * FROM materials WHERE task_id = ? ORDER BY created_at", (task_id,)
        ).fetchall()
    )


def confirm_pii(conn: sqlite3.Connection, material_id: str, confirmed_by: str) -> None:
    conn.execute(
        "UPDATE materials SET pii_confirmed_by = ? WHERE material_id = ?", (confirmed_by, material_id)
    )


def deactivate_material(conn: sqlite3.Connection, material_id: str) -> None:
    conn.execute("UPDATE materials SET status = 'inactive' WHERE material_id = ?", (material_id,))


def next_material_version(conn: sqlite3.Connection, material_id: str) -> int:
    row = conn.execute(
        "SELECT COALESCE(MAX(version_no), 0) AS n FROM material_versions WHERE material_id = ?",
        (material_id,),
    ).fetchone()
    return int(row["n"]) + 1


def insert_material_version(
    conn: sqlite3.Connection,
    material_version_id: str,
    material_id: str,
    version_no: int,
    filename: str,
    size: int,
    sha256: str,
    storage_key: str,
    created_at: str,
) -> None:
    conn.execute(
        """INSERT INTO material_versions
           (material_version_id, material_id, version_no, filename, bytes, sha256, storage_key, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (material_version_id, material_id, version_no, filename, size, sha256, storage_key, created_at),
    )


def list_material_versions(conn: sqlite3.Connection, material_id: str) -> List[Dict[str, Any]]:
    return rows_to_dicts(
        conn.execute(
            "SELECT * FROM material_versions WHERE material_id = ? ORDER BY version_no",
            (material_id,),
        ).fetchall()
    )
