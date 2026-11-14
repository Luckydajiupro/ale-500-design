"""Database connection handling and transaction helpers.

SQLite remains the zero-server local profile. PostgreSQL is the integration and
deployment profile. Services never branch on the database: they use the same
repositories and the same qmark SQL, and this module supplies the connection,
transaction and init/migration semantics for each backend.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional, Union

from .pg import PgConnection

Database = Union[Path, str]


def is_postgres(conn: Any) -> bool:
    return isinstance(conn, PgConnection)


def connect(database: Database) -> Any:
    if isinstance(database, str) and database.startswith(("postgresql://", "postgres://")):
        return PgConnection(database)
    path = Path(database)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), isolation_level=None, timeout=15, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 15000")
    return conn


def initialize(conn: Any, schema_path: Path) -> None:
    conn.executescript(schema_path.read_text(encoding="utf-8"))


@contextmanager
def transaction(conn: Any) -> Iterator[Any]:
    """Run a short write transaction.

    SQLite uses ``BEGIN IMMEDIATE`` so writers serialise. PostgreSQL uses a
    transaction-scoped advisory lock for the same reason: the platform writes
    one task at a time per decision, and 22 concurrent experts do not justify a
    more granular lock protocol yet.
    """

    if is_postgres(conn):
        with conn._conn.transaction():
            conn.execute("SELECT pg_advisory_xact_lock(500500)")
            yield conn
        return

    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except Exception:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")


@contextmanager
def cursor(conn: Any) -> Iterator[Any]:
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()


def is_append_only_violation(error: Exception) -> bool:
    if isinstance(error, sqlite3.IntegrityError) and "append-only" in str(error):
        return True
    return "append-only" in str(error)


def run_migrations(conn: Any, migration_dir: Path) -> list[str]:
    applied: list[str] = []
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations (migration_id TEXT PRIMARY KEY, applied_at TEXT NOT NULL)"
    )
    for migration in sorted(Path(migration_dir).glob("*.sql")):
        row = conn.execute(
            "SELECT 1 AS present FROM schema_migrations WHERE migration_id = ?", (migration.name,)
        ).fetchone()
        if row is not None:
            continue
        conn.executescript(migration.read_text(encoding="utf-8"))
        from .adapters import now

        conn.execute(
            "INSERT INTO schema_migrations (migration_id, applied_at) VALUES (?, ?)",
            (migration.name, now()),
        )
        applied.append(migration.name)
    return applied
