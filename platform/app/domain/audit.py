"""Audit helper used by every service action."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, Optional

from ..adapters import new_id, now
from ..repo import audit as audit_repo


def record(
    conn: sqlite3.Connection,
    principal: Optional[Any],
    action: str,
    object_type: str,
    object_id: str,
    from_state: Optional[str] = None,
    to_state: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    request_id: str = "",
    actor_id: Optional[str] = None,
    actor_role: Optional[str] = None,
) -> str:
    if principal is not None:
        actor = principal.user_id
        roles = sorted(principal.role_codes)
        role = ",".join(roles) if roles else "anonymous"
    else:
        actor = actor_id or "system"
        role = actor_role or "system"
    return audit_repo.append(
        conn,
        event_id=new_id("evt"),
        actor_id=actor,
        actor_role=role,
        action=action,
        object_type=object_type,
        object_id=object_id,
        from_state=from_state,
        to_state=to_state,
        payload=payload or {},
        request_id=request_id,
        created_at=now(),
    )
