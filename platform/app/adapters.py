"""Side-effect adapters: time, identifiers and object storage.

The domain services take these as arguments (or module functions) so tests can
freeze time or swap the local disk store for an S3 adapter without changing
business rules.
"""

from __future__ import annotations

import hashlib
import os
import secrets
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import BinaryIO, Optional


def now() -> str:
    """ISO-8601 UTC with a trailing Z; SQLite stores it as text."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def now_plus(days: int = 0, hours: int = 0) -> str:
    moment = datetime.now(timezone.utc) + timedelta(days=days, hours=hours)
    return moment.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:20]}"


def idempotency_fingerprint(prefix: str = "idem") -> str:
    return f"{prefix}_{secrets.token_urlsafe(16)}"


def sha256_stream(stream: BinaryIO, chunk_size: int = 1024 * 1024) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        digest.update(chunk)
        size += len(chunk)
    return digest.hexdigest(), size


@dataclass
class StoredObject:
    storage_key: str
    sha256: str
    bytes: int


class LocalObjectStore:
    """Content-addressed store on local disk.

    Keys are ``sha256/ab/cd/<digest>`` so identical bytes converge and a
    replaced upload cannot overwrite another material's bytes. The S3 adapter
    implements the same three methods.
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _key(self, digest: str) -> str:
        return f"sha256/{digest[:2]}/{digest[2:4]}/{digest}"

    def put_bytes(self, data: bytes) -> StoredObject:
        digest = hashlib.sha256(data).hexdigest()
        key = self._key(digest)
        target = self.root / key
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_suffix(".part")
            tmp.write_bytes(data)
            os.replace(tmp, target)
        return StoredObject(storage_key=key, sha256=digest, bytes=len(data))

    def put_file(self, source: Path) -> StoredObject:
        with source.open("rb") as handle:
            digest, size = sha256_stream(handle)
        key = self._key(digest)
        target = self.root / key
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_suffix(".part")
            shutil.copyfile(source, tmp)
            os.replace(tmp, target)
        return StoredObject(storage_key=key, sha256=digest, bytes=size)

    def path_for(self, storage_key: str) -> Path:
        candidate = (self.root / storage_key).resolve()
        root = self.root.resolve()
        if root not in candidate.parents and candidate != root:
            raise ValueError("storage key escapes the object root")
        return candidate

    def read_bytes(self, storage_key: str) -> bytes:
        return self.path_for(storage_key).read_bytes()

    def exists(self, storage_key: str) -> bool:
        return self.path_for(storage_key).exists()
