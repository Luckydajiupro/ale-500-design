"""SQLite connection handling and transaction helpers.

The skeleton targets PostgreSQL but runs on SQLite so nobody needs a server to
exercise the flow. All SQL lives behind repositories, so the PostgreSQL profile
swaps the driver and the DDL types rather than rewriting services.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional


def connect(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(database_path), isolation_level=None, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 15000")
    return conn


def initialize(conn: sqlite3.Connection, schema_path: Path) -> None:
    conn.executescript(schema_path.read_text(encoding="utf-8"))


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """BEGIN IMMEDIATE serialises writers, which is what the state machine wants.

    Review decisions, freezes and ingest are serial per task; a write lock on the
    database is enough at 22 concurrent users and keeps the skeleton honest
    about the ordering guarantees the design promises.
    """

    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except Exception:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")


@contextmanager
def cursor(conn: sqlite3.Connection) -> Iterator[sqlite3.Cursor]:
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()


def is_append_only_violation(error: Exception) -> bool:
    return isinstance(error, sqlite3.IntegrityError) and "append-only" in str(error)
