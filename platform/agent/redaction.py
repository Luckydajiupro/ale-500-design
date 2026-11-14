"""Redaction helpers for logs and error messages.

The model gateway handles credentials, HTTP headers and local secret-file paths.
Nothing in that surface may reach a log line, an exception string or an audit
record. This module is deliberately dependency free so it can be imported before
the rest of the Agent package (and by tests) without side effects.

Covered:

* the concrete API key value passed to :func:`redact_text`;
* ``Authorization`` / ``Proxy-Authorization`` headers and bearer tokens;
* ``Cookie`` / ``Set-Cookie`` headers;
* common key assignments (``api_key=``, ``x-api-key:``, ``token=`` ...);
* OpenAI-style ``sk-`` tokens;
* user home directory prefixes in absolute paths (``/Users/alice/...``).

It is a defence in depth, not a licence to log secrets: callers still must not
put keys into prompts or structured records.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping as ABCMapping
from typing import Any, Mapping, Optional

REDACTED = "[REDACTED]"

_SENSITIVE_KEY_RE = re.compile(
    r"(?i)(api[_-]?key|authorization|proxy[_-]?authorization|cookie|"
    r"set[_-]?cookie|secret|token|password|credential)"
)

_AUTHORIZATION_RE = re.compile(
    r"(?i)\b(authorization|proxy-authorization)\b(\s*[:=]\s*)"
    r"(bearer\s+)?([^\s,;\"'}]+)"
)
_COOKIE_RE = re.compile(r"(?i)\b(set-cookie|cookie)\b(\s*[:=]\s*)([^\r\n]+)")
_KEY_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api[_-]?key|x-api-key|access[_-]?token|refresh[_-]?token|"
    r"client[_-]?secret|password)\b(\s*[:=]\s*)([\"']?)([^\s,\"'}&]+)"
)
_BEARER_RE = re.compile(r"(?i)\bbearer\s+([A-Za-z0-9._~+/=-]{8,})")
_OPENAI_STYLE_RE = re.compile(r"\b(?:sk|rk|pk)-[A-Za-z0-9_-]{8,}\b")

_HOME_DIR_PATTERNS = (
    (re.compile(r"/Users/[^/\s\"'`]+"), "~"),
    (re.compile(r"/home/[^/\s\"'`]+"), "~"),
    (re.compile(r"/root(?=/|\s|$|[\"'])"), "~"),
    (re.compile(r"[A-Za-z]:\\Users\\[^\\\s\"'`]+"), "~"),
)


def redact_text(value: Any, secret: Optional[str] = None) -> str:
    """Return ``value`` as text with credentials and home paths removed."""

    text = value if isinstance(value, str) else str(value)

    if secret and len(secret) >= 4:
        text = text.replace(secret, REDACTED)

    text = _AUTHORIZATION_RE.sub(
        lambda match: "%s%s%s%s"
        % (
            match.group(1),
            match.group(2),
            "Bearer " if match.group(3) else "",
            REDACTED,
        ),
        text,
    )
    text = _COOKIE_RE.sub(
        lambda match: "%s%s%s" % (match.group(1), match.group(2), REDACTED),
        text,
    )
    text = _KEY_ASSIGNMENT_RE.sub(
        lambda match: "%s%s%s%s"
        % (match.group(1), match.group(2), match.group(3), REDACTED),
        text,
    )
    text = _BEARER_RE.sub("Bearer " + REDACTED, text)
    text = _OPENAI_STYLE_RE.sub(REDACTED, text)

    for pattern, replacement in _HOME_DIR_PATTERNS:
        text = pattern.sub(replacement, text)

    return text


def redact_value(value: Any, secret: Optional[str] = None) -> Any:
    """Recursively redact a JSON-like value without mutating the input.

    Mapping keys that look sensitive have their whole value replaced, which
    also covers short or malformed secrets that would be unsafe to substring
    match.
    """

    if isinstance(value, ABCMapping):
        cleaned = {}
        for key, item in value.items():
            if _SENSITIVE_KEY_RE.search(str(key)):
                cleaned[key] = REDACTED
            else:
                cleaned[key] = redact_value(item, secret)
        return cleaned
    if isinstance(value, (list, tuple)):
        return [redact_value(item, secret) for item in value]
    if isinstance(value, str):
        return redact_text(value, secret)
    return value


def safe_exception_message(exc: BaseException, secret: Optional[str] = None) -> str:
    """A one-line, redacted message safe for logs and Agent errors."""

    message = "%s: %s" % (type(exc).__name__, exc)
    return redact_text(message, secret)


class RedactionFilter(logging.Filter):
    """Logging filter that redacts message text and arguments.

    Add it to a handler, not to a logger: filters on a logger do not run for
    records propagated from child loggers.
    """

    def __init__(self, secret: Optional[str] = None) -> None:
        super().__init__()
        self._secret = secret

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_text(record.getMessage(), self._secret)
        record.args = ()
        if record.exc_text:
            record.exc_text = redact_text(record.exc_text, self._secret)
        return True
