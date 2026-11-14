from __future__ import annotations

import hashlib
import json
import sqlite3
from typing import Any, Callable, Dict, Optional, Tuple


def request_hash(payload: Any) -> str:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def lookup(conn: sqlite3.Connection, actor_id: str, endpoint: str, key: str) -> Optional[Dict[str, Any]]:
    row = conn.execute(
        """SELECT request_hash, status_code, response_json FROM idempotency_keys
           WHERE actor_id = ? AND endpoint = ? AND idem_key = ?""",
        (actor_id, endpoint, key),
    ).fetchone()
    return dict(row) if row else None


def store(
    conn: sqlite3.Connection,
    record_id: str,
    actor_id: str,
    endpoint: str,
    key: str,
    digest: str,
    status_code: int,
    response: Dict[str, Any],
    created_at: str,
) -> None:
    conn.execute(
        """INSERT INTO idempotency_keys
           (id, actor_id, endpoint, idem_key, request_hash, status_code, response_json, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            record_id,
            actor_id,
            endpoint,
            key,
            digest,
            status_code,
            json.dumps(response, ensure_ascii=False, sort_keys=True),
            created_at,
        ),
    )
