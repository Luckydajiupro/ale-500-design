"""Runtime settings.

Environment variables are read once at import time of the app factory so tests
can point the skeleton at a temporary directory without touching the repo.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_path: Path
    storage_root: Path
    schema_path: Path
    environment: str = "local"

    @property
    def is_sqlite(self) -> bool:
        return True


def load_settings() -> Settings:
    base = Path(__file__).resolve().parent.parent
    database_path = Path(os.environ.get("ALE_DB_PATH", base / "var" / "platform.db"))
    storage_root = Path(os.environ.get("ALE_STORAGE_ROOT", base / "var" / "objects"))
    return Settings(
        database_path=database_path,
        storage_root=storage_root,
        schema_path=base / "app" / "schema.sql",
        environment=os.environ.get("ALE_ENV", "local"),
    )
