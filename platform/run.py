#!/usr/bin/env python3
"""Start the local workbench.

The server is for local development and expert acceptance. Production needs an
external TLS terminator, a PostgreSQL profile and a managed secret store.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import uvicorn  # noqa: E402

from web.app import create_app  # noqa: E402

app = create_app()


def main() -> int:
    host = os.environ.get("ALE_HOST", "127.0.0.1")
    port = int(os.environ.get("ALE_PORT", "8000"))
    uvicorn.run(app, host=host, port=port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
