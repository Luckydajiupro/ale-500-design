"""Repositories: the only modules that know SQL.

Every function takes a connection so the caller controls the transaction. Rows
are returned as dicts to keep services independent of sqlite3.Row.
"""

from __future__ import annotations
