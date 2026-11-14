from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional


def _normalise(value: Any) -> Any:
    """Keep the domain contract stable across SQLite TEXT and PostgreSQL JSONB."""

    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return value


def row_to_dict(row: Optional[Any]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    return {key: _normalise(value) for key, value in dict(row).items()}


def rows_to_dicts(rows: Iterable[Any]) -> List[Dict[str, Any]]:
    return [row_to_dict(row) for row in rows if row is not None]
