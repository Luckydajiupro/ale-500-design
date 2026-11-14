from __future__ import annotations

import hashlib
import json
import sqlite3
from typing import Any, Dict, List, Optional

GENESIS_HASH = "0" * 64


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def append(
    conn: sqlite3.Connection,
    event_id: str,
    actor_id: str,
    actor_role: str,
    action: str,
    object_type: str,
    object_id: str,
    from_state: Optional[str],
    to_state: Optional[str],
    payload: Dict[str, Any],
    request_id: str,
    created_at: str,
) -> str:
    """Append one event and return its hash.

    The chain covers every field except the hashes themselves, so an offline
    verifier can re-walk the table and detect an edited or reordered row.
    """

    last = conn.execute("SELECT seq, event_hash FROM audit_events ORDER BY seq DESC LIMIT 1").fetchone()
    seq = int(last["seq"]) + 1 if last else 1
    prev_hash = last["event_hash"] if last else GENESIS_HASH
    body = {
        "seq": seq,
        "event_id": event_id,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "action": action,
        "object_type": object_type,
        "object_id": object_id,
        "from_state": from_state,
        "to_state": to_state,
        "payload": payload,
        "request_id": request_id,
        "created_at": created_at,
        "prev_hash": prev_hash,
    }
    event_hash = hashlib.sha256(canonical(body).encode("utf-8")).hexdigest()
    conn.execute(
        """INSERT INTO audit_events
           (event_id, seq, actor_id, actor_role, action, object_type, object_id,
            from_state, to_state, payload_json, request_id, created_at, prev_hash, event_hash)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            event_id,
            seq,
            actor_id,
            actor_role,
            action,
            object_type,
            object_id,
            from_state,
            to_state,
            canonical(payload),
            request_id,
            created_at,
            prev_hash,
            event_hash,
        ),
    )
    return event_hash


def list_events(
    conn: sqlite3.Connection,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    limit: int = 100,
    after_seq: int = 0,
) -> List[Dict[str, Any]]:
    clauses = ["seq > ?"]
    params: List[Any] = [after_seq]
    if object_type:
        clauses.append("object_type = ?")
        params.append(object_type)
    if object_id:
        clauses.append("object_id = ?")
        params.append(object_id)
    params.append(limit)
    rows = conn.execute(
        f"SELECT * FROM audit_events WHERE {' AND '.join(clauses)} ORDER BY seq LIMIT ?", params
    ).fetchall()
    return [dict(row) for row in rows]


def verify(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Re-walk the chain. Returns the first break instead of raising."""

    rows = conn.execute("SELECT * FROM audit_events ORDER BY seq").fetchall()
    prev = GENESIS_HASH
    expected_seq = 1
    for row in rows:
        body = {
            "seq": row["seq"],
            "event_id": row["event_id"],
            "actor_id": row["actor_id"],
            "actor_role": row["actor_role"],
            "action": row["action"],
            "object_type": row["object_type"],
            "object_id": row["object_id"],
            "from_state": row["from_state"],
            "to_state": row["to_state"],
            "payload": json.loads(row["payload_json"]),
            "request_id": row["request_id"],
            "created_at": row["created_at"],
            "prev_hash": prev,
        }
        recomputed = hashlib.sha256(canonical(body).encode("utf-8")).hexdigest()
        if row["seq"] != expected_seq or row["prev_hash"] != prev or recomputed != row["event_hash"]:
            return {
                "ok": False,
                "events": len(rows),
                "broken_at_seq": row["seq"],
                "expected_seq": expected_seq,
            }
        prev = row["event_hash"]
        expected_seq += 1
    return {"ok": True, "events": len(rows), "head_hash": prev}
