"""PostgreSQL compatibility connection for the platform repositories.

The repositories intentionally speak a small SQL subset that both SQLite and
PostgreSQL understand: ``?`` placeholders, explicit column lists and standard
``INSERT ... ON CONFLICT``. This adapter translates the placeholders, maps rows
to dictionaries and normalises JSONB values back to the JSON text the domain
services expect.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence


class PgConnection:
    def __init__(self, dsn: str) -> None:
        import psycopg
        from psycopg.rows import dict_row

        self.dsn = dsn
        self._conn = psycopg.connect(dsn, autocommit=True, row_factory=dict_row)
        self.backend = "postgresql"

    def execute(self, sql: str, params: Sequence[Any] = ()) -> Any:
        return self._conn.execute(_translate(sql), tuple(params))

    def executescript(self, script: str) -> None:
        for statement in split_sql(script):
            self._conn.execute(statement)

    def cursor(self) -> Any:
        return self._conn.cursor()

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._conn, name)


def _translate(sql: str) -> str:
    """Translate SQLite qmark placeholders to psycopg's ``%s``.

    The repositories do not embed ``?`` inside string literals, so a direct
    replacement is safe and keeps the adapter small.
    """

    return sql.replace("?", "%s")


def split_sql(script: str) -> List[str]:
    """Split a SQL script on top-level semicolons.

    Handles single/double quoted strings, line comments, block comments and
    PostgreSQL dollar-quoted function bodies. This is deliberately a small
    parser rather than a general SQL parser: the schema is the only caller.
    """

    statements: List[str] = []
    buffer: List[str] = []
    index = 0
    length = len(script)
    quote: Optional[str] = None
    dollar: Optional[str] = None
    line_comment = False
    block_comment = False

    while index < length:
        char = script[index]
        if line_comment:
            if char == "\n":
                line_comment = False
                buffer.append(char)
            index += 1
            continue
        if block_comment:
            if script.startswith("*/", index):
                block_comment = False
                index += 2
            else:
                index += 1
            continue
        if dollar is not None:
            if script.startswith(dollar, index):
                buffer.append(dollar)
                index += len(dollar)
                dollar = None
            else:
                buffer.append(char)
                index += 1
            continue
        if quote is not None:
            buffer.append(char)
            if char == quote:
                if index + 1 < length and script[index + 1] == quote:
                    buffer.append(quote)
                    index += 2
                    continue
                quote = None
            index += 1
            continue

        if script.startswith("--", index):
            line_comment = True
            index += 2
            continue
        if script.startswith("/*", index):
            block_comment = True
            index += 2
            continue
        if char in ("'", '"'):
            quote = char
            buffer.append(char)
            index += 1
            continue
        if char == "$":
            match = re.match(r"\$[A-Za-z_][A-Za-z0-9_]*\$|\$\$", script[index:])
            if match:
                dollar = match.group(0)
                buffer.append(dollar)
                index += len(dollar)
                continue
        if char == ";":
            statement = "".join(buffer).strip()
            if statement:
                statements.append(statement)
            buffer = []
            index += 1
            continue
        buffer.append(char)
        index += 1

    tail = "".join(buffer).strip()
    if tail:
        statements.append(tail)
    return statements


def normalize_json(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return value
