"""Output contracts for the five Agent capabilities.

The gateway never trusts free-form model text. Every capability has one strict
JSON Schema and one semantic pass on top of it:

* the payload must be a single JSON object with exactly one key, ``suggestions``;
* every suggestion has exactly ``field_path``, ``value``, ``confidence``,
  ``rationale`` and ``evidence``;
* ``field_path`` must resolve to a legal prefix of the Canonical task source
  (``schemas/canonical-task-source.schema.json``), and must not point into the
  platform-owned ``verification`` / ``package`` blocks;
* ``confidence`` is a number in ``[0, 1]``;
* no suggestion may carry an action such as submit / approve / freeze / ingest.

The module is intentionally side-effect free: the gateway owns HTTP, retries and
audit records. Keeping the contracts here means the same rules can be reused by
a future validator, a fixture generator or an offline review tool.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping as ABCMapping
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import jsonschema

CAPABILITIES: Tuple[str, ...] = (
    "interview",
    "followup",
    "structuring",
    "precheck",
    "review_assist",
)

# Blocks the platform derives itself. The Agent may talk about them in prose,
# but it may never propose values for them.
PLATFORM_OWNED_BLOCKS: Tuple[str, ...] = ("verification", "package")

# Used only when the canonical schema file cannot be read. The real repository
# always ships the file, so this is a fail-safe, not the normal path.
FALLBACK_BLOCKS: Tuple[str, ...] = (
    "identity",
    "scenario",
    "materials",
    "operations",
    "deliverables",
    "success_criteria",
    "environment",
    "review",
    "provenance",
    "handoff",
)

_TOKEN_RE = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_-]*)(?P<indices>(?:\[\d+\])*)$")
_INDEX_RE = re.compile(r"\[(\d+)\]")
_FIELD_PATH_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_-]*(?:\[\d+\])?"
    r"(?:\.[A-Za-z_][A-Za-z0-9_-]*(?:\[\d+\])?)*$"
)

# Keys that turn a suggestion into an action. Strict schemas already reject
# them at the top level of a suggestion, but ``value`` is free-form for
# followup/structuring, so the semantic pass checks nested mappings too.
ACTION_KEYS = frozenset(
    {
        "action",
        "actions",
        "approve",
        "approved",
        "decision",
        "freeze",
        "frozen",
        "ingest",
        "ingested",
        "publish",
        "submit",
        "submitted",
        "verdict",
    }
)

ACTION_PHRASES: Tuple[str, ...] = (
    "提交任务",
    "提交评审",
    "冻结快照",
    "冻结任务",
    "执行入库",
    "立即入库",
    "组包入库",
    "批准任务",
    "执行审核",
    "审核结论",
    "审核通过",
    "评审结论",
    "评审通过",
    "submit the task",
    "approve the task",
    "freeze the snapshot",
    "ingest the package",
    "publish the task",
)


class OutputContractError(ValueError):
    """A model output that violates the capability contract.

    ``code`` is stable and safe to log; ``message`` is human readable and is
    never built from credentials.
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


# ---------------------------------------------------------------------------
# Canonical path resolution
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _canonical_root() -> Optional[Mapping[str, Any]]:
    path = (
        Path(__file__).resolve().parents[2]
        / "schemas"
        / "canonical-task-source.schema.json"
    )
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, ABCMapping) else None


def canonical_block_names() -> Tuple[str, ...]:
    """Top-level blocks declared by the canonical schema."""

    root = _canonical_root()
    if root is None:
        return FALLBACK_BLOCKS
    properties = root.get("properties")
    if not isinstance(properties, ABCMapping):
        return FALLBACK_BLOCKS
    return tuple(str(name) for name in properties.keys())


def _resolve_property(node: Mapping[str, Any], name: str) -> Optional[Mapping[str, Any]]:
    properties = node.get("properties")
    if isinstance(properties, ABCMapping) and name in properties:
        candidate = properties[name]
        if isinstance(candidate, ABCMapping):
            return candidate
        return None

    patterns = node.get("patternProperties")
    if isinstance(patterns, ABCMapping):
        for pattern, candidate in patterns.items():
            try:
                matched = re.search(str(pattern), name)
            except re.error:
                continue
            if matched and isinstance(candidate, ABCMapping):
                return candidate

    additional = node.get("additionalProperties")
    if isinstance(additional, ABCMapping):
        return additional
    return None


def _array_items(node: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
    items = node.get("items")
    if isinstance(items, ABCMapping):
        return items
    if isinstance(items, Sequence) and not isinstance(items, (str, bytes)) and items:
        first = items[0]
        if isinstance(first, ABCMapping):
            return first
    return None


def path_is_canonical(field_path: str) -> bool:
    """Return True when ``field_path`` is a legal Canonical source prefix.

    Both ``materials[0].path`` and ``materials.path`` are accepted: the second
    form descends through the array item implicitly, matching the dotted paths
    already used by the workbench's suggestion table.
    """

    if not isinstance(field_path, str):
        return False
    if not field_path or len(field_path) > 200:
        return False
    if not _FIELD_PATH_RE.match(field_path):
        return False

    parts = field_path.split(".")
    first_match = _TOKEN_RE.match(parts[0])
    if first_match is None:
        return False
    if first_match.group("name") in PLATFORM_OWNED_BLOCKS:
        return False

    root = _canonical_root()
    if root is None:
        return first_match.group("name") in FALLBACK_BLOCKS

    node: Optional[Mapping[str, Any]] = root
    for position, part in enumerate(parts):
        match = _TOKEN_RE.match(part)
        if match is None or node is None:
            return False
        node = _resolve_property(node, match.group("name"))
        if node is None:
            return False

        indices = _INDEX_RE.findall(match.group("indices"))
        for _ in indices:
            node = _array_items(node)
            if node is None:
                return False

        # ``materials.role`` means "role on a material item"; the workbench
        # stores dotted paths without indices, so descend implicitly.
        if not indices and position < len(parts) - 1:
            if node.get("type") == "array":
                node = _array_items(node)
                if node is None:
                    return False

    return True


def is_block_level_path(field_path: str) -> bool:
    return (
        isinstance(field_path, str)
        and "." not in field_path
        and "[" not in field_path
    )


# ---------------------------------------------------------------------------
# Strict JSON Schema per capability
# ---------------------------------------------------------------------------


def _suggestion_schema(value_schema: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["field_path", "value", "confidence", "rationale", "evidence"],
        "properties": {
            "field_path": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200,
                "pattern": _FIELD_PATH_RE.pattern,
            },
            "value": dict(value_schema),
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "rationale": {"type": "string", "minLength": 1, "maxLength": 1000},
            "evidence": {
                "type": "array",
                "minItems": 1,
                "maxItems": 10,
                "items": {"type": "string", "minLength": 1, "maxLength": 500},
            },
        },
    }


_VALUE_SCHEMAS: Dict[str, Mapping[str, Any]] = {
    # An interview happens before a draft exists: value is the question itself.
    "interview": {
        "type": "object",
        "additionalProperties": False,
        "required": ["question", "why"],
        "properties": {
            "question": {"type": "string", "minLength": 3, "maxLength": 500},
            "why": {"type": "string", "minLength": 3, "maxLength": 500},
        },
    },
    # followup and structuring propose an actual field value; the canonical
    # schema is the source of truth for its type, not this envelope.
    "followup": {},
    "structuring": {},
    "precheck": {
        "type": "object",
        "additionalProperties": False,
        "required": ["finding", "severity"],
        "properties": {
            "finding": {"type": "string", "minLength": 3, "maxLength": 1000},
            "severity": {"type": "string", "enum": ["blocker", "warning", "info"]},
        },
    },
    "review_assist": {
        "type": "object",
        "additionalProperties": False,
        "required": ["check", "evidence_location"],
        "properties": {
            "check": {"type": "string", "minLength": 3, "maxLength": 1000},
            "evidence_location": {"type": "string", "minLength": 1, "maxLength": 300},
        },
    },
}


@lru_cache(maxsize=8)
def output_schema(capability: str) -> Mapping[str, Any]:
    """Return the strict output schema for one capability."""

    if capability not in CAPABILITIES:
        raise OutputContractError(
            "OUTPUT_UNKNOWN_CAPABILITY", "未知 Agent 能力：%s" % capability
        )
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["suggestions"],
        "properties": {
            "suggestions": {
                "type": "array",
                "maxItems": 50,
                "items": _suggestion_schema(_VALUE_SCHEMAS[capability]),
            }
        },
    }


def _schema_error_code(error: jsonschema.ValidationError) -> str:
    if error.validator == "additionalProperties":
        return "OUTPUT_UNKNOWN_FIELD"
    if error.validator == "required":
        return "OUTPUT_MISSING_FIELD"
    return "OUTPUT_SCHEMA_INVALID"


def _iter_strings(value: Any) -> Any:
    if isinstance(value, str):
        yield value
    elif isinstance(value, ABCMapping):
        for item in value.values():
            yield from _iter_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _iter_strings(item)


def _iter_action_keys(value: Any, prefix: str = "") -> Any:
    if isinstance(value, ABCMapping):
        for key, item in value.items():
            path = "%s.%s" % (prefix, key) if prefix else str(key)
            if str(key).strip().lower() in ACTION_KEYS:
                yield path
            else:
                yield from _iter_action_keys(item, path)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            yield from _iter_action_keys(item, "%s[%s]" % (prefix, index))


def _contains_action_phrase(value: str) -> bool:
    lowered = value.casefold()
    return any(phrase.casefold() in lowered for phrase in ACTION_PHRASES)


def validate_output(
    capability: str, payload: Mapping[str, Any]
) -> List[Mapping[str, Any]]:
    """Validate a decoded model payload and return its suggestions.

    Raises :class:`OutputContractError` with a stable ``code``. Never returns
    partially validated data.
    """

    schema = output_schema(capability)
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: "/".join(str(part) for part in error.absolute_path),
    )
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.absolute_path) or "$"
        message = "%s: %s" % (location, first.message[:300])
        raise OutputContractError(_schema_error_code(first), message)

    suggestions = list(payload.get("suggestions") or [])
    for index, suggestion in enumerate(suggestions):
        field_path = suggestion["field_path"]
        if not path_is_canonical(field_path):
            raise OutputContractError(
                "OUTPUT_INVALID_PATH",
                "suggestions[%d].field_path 不是 Canonical 任务源合法路径: %s"
                % (index, field_path),
            )
        if capability == "interview" and not is_block_level_path(field_path):
            raise OutputContractError(
                "OUTPUT_INVALID_PATH",
                "interview 建议只能指向块级路径，收到: %s" % field_path,
            )
        if suggestion.get("value") is None:
            raise OutputContractError(
                "OUTPUT_SCHEMA_INVALID",
                "suggestions[%d].value 不可为 null" % index,
            )

        for action_path in _iter_action_keys(suggestion["value"]):
            raise OutputContractError(
                "OUTPUT_FORBIDDEN_ACTION",
                "suggestions[%d].value 含动作字段: %s" % (index, action_path),
            )
        for text in _iter_strings(suggestion["value"]):
            if _contains_action_phrase(text):
                raise OutputContractError(
                    "OUTPUT_FORBIDDEN_ACTION",
                    "suggestions[%d].value 含动作指令" % index,
                )

    return suggestions
