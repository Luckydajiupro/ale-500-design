#!/usr/bin/env python3
"""Operational commands for the ALE workbench.

Usage:
    python platform/manage.py migrate
    python platform/manage.py seed
    python platform/manage.py check
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import connect, initialize, is_postgres, run_migrations  # noqa: E402


def database() -> str:
    return os.environ.get("ALE_DB_URL") or os.environ.get("ALE_DB_PATH", str(ROOT / "var" / "platform.db"))


def migrate() -> int:
    conn = connect(database())
    try:
        if is_postgres(conn):
            conn.execute("SELECT pg_advisory_lock(500501)")
            try:
                applied = run_migrations(conn, ROOT / "pg" / "migrations")
            finally:
                conn.execute("SELECT pg_advisory_unlock(500501)")
        else:
            initialize(conn, ROOT / "app" / "schema.sql")
            applied = run_migrations(conn, ROOT / "migrations")
        print("migrations applied:", ", ".join(applied) if applied else "none")
        return 0
    finally:
        conn.close()


def seed() -> int:
    from seed import seed as seed_data

    seed_data(database(), os.environ.get("ALE_SEED_PASSWORD", "AleDemo123!"))
    print("seed complete")
    return 0


def check() -> int:
    conn = connect(database())
    try:
        rows = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()
        tasks = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()
        packages = conn.execute("SELECT COUNT(*) AS n FROM packages").fetchone()
        print("backend:", getattr(conn, "backend", "unknown"))
        print("users:", rows["n"], "tasks:", tasks["n"], "packages:", packages["n"])
        return 0
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["migrate", "seed", "check"])
    args = parser.parse_args()
    return {"migrate": migrate, "seed": seed, "check": check}[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
