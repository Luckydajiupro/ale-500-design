#!/usr/bin/env python3
"""Background worker for package builds and long-running platform jobs."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.adapters import LocalObjectStore, now  # noqa: E402
from app.auth import resolve_principal  # noqa: E402
from app.db import connect, transaction  # noqa: E402
from app.domain import delivery as delivery_service  # noqa: E402
from app.repo import jobs as job_repo  # noqa: E402


def database() -> str:
    return os.environ.get("ALE_DB_URL") or os.environ.get("ALE_DB_PATH", str(ROOT / "var" / "platform.db"))


def roots() -> tuple[Path, Path]:
    storage = Path(os.environ.get("ALE_STORAGE_ROOT", str(ROOT / "var" / "objects")))
    packages = Path(os.environ.get("ALE_PACKAGE_ROOT", str(ROOT / "var" / "packages")))
    storage.mkdir(parents=True, exist_ok=True)
    packages.mkdir(parents=True, exist_ok=True)
    return storage, packages


def dispatch(conn, job, store: LocalObjectStore, package_root: Path):
    payload = json.loads(job["payload_json"] or "{}")
    principal = resolve_principal(conn, "u_admin")
    if principal is None:
        raise RuntimeError("worker principal u_admin is missing; run manage.py seed")
    if job["kind"] == "package.build":
        return delivery_service.build_package(conn, principal, job["task_id"], package_root, store)
    if job["kind"] == "package.validate":
        return delivery_service.validate_package(conn, principal, payload["package_id"], package_root)
    if job["kind"] == "package.ingest":
        return delivery_service.ingest_package(conn, principal, payload["package_id"])
    raise RuntimeError("unknown job kind: %s" % job["kind"])


def process_one(conn, worker_id: str, store: LocalObjectStore, package_root: Path) -> bool:
    with transaction(conn):
        job = job_repo.claim_next(conn, worker_id, now())
    if job is None:
        return False
    try:
        with transaction(conn):
            result = dispatch(conn, job, store, package_root)
        with transaction(conn):
            job_repo.finish(conn, job["job_id"], "succeeded", json.dumps(result, ensure_ascii=False, sort_keys=True), None, now())
        print("job %s %s succeeded" % (job["job_id"], job["kind"]), flush=True)
    except Exception as exc:  # noqa: BLE001
        attempts = int(job["attempts"]) + 1
        print("job %s %s failed: %s" % (job["job_id"], job["kind"], exc), file=sys.stderr, flush=True)
        traceback.print_exc()
        with transaction(conn):
            if attempts < int(job["max_attempts"]):
                job_repo.retry(conn, job["job_id"], attempts, now(), str(exc), now())
            else:
                job_repo.finish(conn, job["job_id"], "failed", None, str(exc), now())
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--worker-id", default=os.environ.get("ALE_WORKER_ID", "worker-local"))
    args = parser.parse_args()
    storage, package_root = roots()
    store = LocalObjectStore(storage)
    conn = connect(database())
    try:
        while True:
            worked = process_one(conn, args.worker_id, store, package_root)
            if args.once or not args.loop:
                return 0
            if not worked:
                time.sleep(1)
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
