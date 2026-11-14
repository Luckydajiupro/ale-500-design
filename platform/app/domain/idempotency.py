"""Idempotency wrapper for write endpoints.

The contract is: a client-generated key plus the request body identify one
logical write. Replaying the same pair returns the first response; reusing the
key with a different body is rejected instead of silently doing something else.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Callable, Dict, Tuple

from ..adapters import new_id, now
from ..errors import conflict, idempotency_required
from ..repo import idempotency as idem_repo


def execute(
    conn: sqlite3.Connection,
    principal: Any,
    endpoint: str,
    key: str,
    payload: Dict[str, Any],
    action: Callable[[], Dict[str, Any]],
) -> Tuple[Dict[str, Any], bool]:
    if not key or not key.strip():
        raise idempotency_required()
    digest = idem_repo.request_hash(payload)
    existing = idem_repo.lookup(conn, principal.user_id, endpoint, key)
    if existing is not None:
        if existing["request_hash"] != digest:
            raise conflict(
                "IDEMPOTENCY_KEY_REUSED",
                "同一个 Idempotency-Key 被用于不同的请求体",
                [{"endpoint": endpoint}],
            )
        return json.loads(existing["response_json"]), True
    response = action()
    idem_repo.store(
        conn,
        record_id=new_id("idem"),
        actor_id=principal.user_id,
        endpoint=endpoint,
        key=key,
        digest=digest,
        status_code=200,
        response=response,
        created_at=now(),
    )
    return response, False
