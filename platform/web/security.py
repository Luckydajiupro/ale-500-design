"""Password, session and CSRF helpers for the server-rendered workbench."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from pathlib import Path
from typing import Any, Dict, Optional

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

PBKDF2_ITERATIONS = 240_000
COOKIE_NAME = "ale_session"
SESSION_MAX_AGE = 8 * 60 * 60


def hash_password(password: str, *, salt: Optional[bytes] = None, iterations: int = PBKDF2_ITERATIONS) -> str:
    if not password or len(password) < 10:
        raise ValueError("password must be at least 10 characters")
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256$%d$%s$%s" % (
        iterations,
        salt.hex(),
        digest.hex(),
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def load_secret(path: Path) -> str:
    configured = os.environ.get("ALE_SECRET_KEY")
    if configured:
        return configured
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    value = secrets.token_urlsafe(48)
    path.write_text(value + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return value


class SessionCodec:
    def __init__(self, secret: str) -> None:
        self._serializer = URLSafeTimedSerializer(secret, salt="ale-workbench-session")

    def encode(self, data: Dict[str, Any]) -> str:
        return self._serializer.dumps(data)

    def decode(self, token: Optional[str]) -> Optional[Dict[str, Any]]:
        if not token:
            return None
        try:
            return self._serializer.loads(token, max_age=SESSION_MAX_AGE)
        except (BadSignature, SignatureExpired):
            return None


def csrf_token(session: Dict[str, Any]) -> str:
    token = session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf"] = token
    return token


def check_csrf(session: Dict[str, Any], submitted: Optional[str]) -> bool:
    expected = session.get("csrf")
    return bool(expected and submitted and hmac.compare_digest(str(expected), str(submitted)))
