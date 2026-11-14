from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, Optional

from ..adapters import new_id, now
from ..repo import jobs as job_repo


def enqueue(
    conn: sqlite3.Connection,
    kind: str,
    task_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    max_attempts: int = 3,
) -> Dict[str, Any]:
    job_id = new_id("job")
    created = now()
    job_repo.insert_job(
        conn,
        job_id=job_id,
        kind=kind,
        task_id=task_id,
        payload_json=json.dumps(payload or {}, ensure_ascii=False, sort_keys=True),
        available_at=created,
        created_at=created,
        max_attempts=max_attempts,
    )
    return job_repo.get_job(conn, job_id) or {}
