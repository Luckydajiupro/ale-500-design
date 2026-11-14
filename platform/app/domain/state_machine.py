"""The nine main states plus the two side paths.

Every mutation of ``tasks.state`` goes through :func:`apply`. The table below is
the only place that decides which state may follow which, so a reviewer can read
the whole lifecycle in one screen.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..errors import conflict

DRAFT = "draft"
SUBMITTED = "submitted"
AUTO_CHECKED = "auto_checked"
IN_REVIEW = "in_review"
APPROVED = "approved"
FROZEN = "frozen"
PACKAGED = "packaged"
PACKAGE_VALIDATED = "package_validated"
INGESTED = "ingested"
RETURNED = "returned"
VOID = "void"

MAIN_STATES: Tuple[str, ...] = (
    DRAFT,
    SUBMITTED,
    AUTO_CHECKED,
    IN_REVIEW,
    APPROVED,
    FROZEN,
    PACKAGED,
    PACKAGE_VALIDATED,
    INGESTED,
)
SIDE_STATES: Tuple[str, ...] = (RETURNED, VOID)
ALL_STATES: Tuple[str, ...] = MAIN_STATES + SIDE_STATES

EDITABLE_STATES = frozenset({DRAFT, RETURNED})
IMMUTABLE_STATES = frozenset({FROZEN, PACKAGED, PACKAGE_VALIDATED, INGESTED})


@dataclass(frozen=True)
class Transition:
    event: str
    source: Tuple[str, ...]
    target: str
    actors: Tuple[str, ...]
    description: str


TRANSITIONS: Tuple[Transition, ...] = (
    Transition("submit", (DRAFT, RETURNED), SUBMITTED, ("expert",), "专家提交版本"),
    Transition("auto_check_pass", (SUBMITTED,), AUTO_CHECKED, ("system", "expert"), "九项自动检查无阻断"),
    Transition("auto_check_fail", (SUBMITTED,), RETURNED, ("system",), "自动检查有阻断，退回专家"),
    Transition("start_review", (AUTO_CHECKED,), IN_REVIEW, ("domain_reviewer",), "领域评审领取"),
    Transition("return_by_review", (IN_REVIEW,), RETURNED, ("domain_reviewer", "quality_reviewer"), "评审退回"),
    Transition("reject", (IN_REVIEW,), VOID, ("domain_reviewer",), "评审拒收"),
    Transition("domain_pass", (IN_REVIEW,), IN_REVIEW, ("domain_reviewer",), "领域评审通过，进入质量审核"),
    Transition("quality_pass", (IN_REVIEW,), APPROVED, ("quality_reviewer",), "质量审核通过，可冻结"),
    Transition("quality_return", (IN_REVIEW,), RETURNED, ("quality_reviewer",), "质量审核退回"),
    Transition("freeze", (APPROVED,), FROZEN, ("quality_reviewer", "platform_admin", "project_lead"), "冻结快照"),
    Transition("return_by_quality", (APPROVED,), RETURNED, ("quality_reviewer",), "冻结前发现漏项"),
    Transition("void", (DRAFT, SUBMITTED, AUTO_CHECKED, IN_REVIEW, APPROVED), VOID, ("expert", "platform_admin"), "作废（冻结前）"),
    Transition("package", (FROZEN,), PACKAGED, ("platform_admin", "system"), "生成包记录"),
    Transition("package_fail", (PACKAGED,), FROZEN, ("system", "platform_admin"), "组包失败回到冻结"),
    Transition("validate_pass", (PACKAGED,), PACKAGE_VALIDATED, ("system", "platform_admin"), "包校验通过"),
    Transition("validate_fail", (PACKAGED,), FROZEN, ("system", "platform_admin"), "包校验阻断回到冻结"),
    Transition("ingest", (PACKAGE_VALIDATED,), INGESTED, ("platform_admin", "system"), "幂等入库"),
)

_BY_EVENT: Dict[str, List[Transition]] = {}
for _transition in TRANSITIONS:
    _BY_EVENT.setdefault(_transition.event, []).append(_transition)


def find(event: str, source: str) -> Optional[Transition]:
    for transition in _BY_EVENT.get(event, []):
        if source in transition.source:
            return transition
    return None


def assert_can(event: str, source: str, role: str) -> Transition:
    transition = find(event, source)
    if transition is None:
        raise conflict(
            "INVALID_STATE_TRANSITION",
            f"状态 {source} 不能执行 {event}",
            [{"from": source, "event": event}],
        )
    if role not in transition.actors and "system" not in transition.actors:
        raise conflict("TRANSITION_FORBIDDEN", f"{role} 不能执行 {event}")
    return transition


def apply(
    conn: sqlite3.Connection,
    task: Dict,
    event: str,
    actor_role: str,
    updated_at: str,
    **extra: object,
) -> str:
    """Validate, update the row and return the previous state.

    The caller writes the audit event; the state machine never logs on its own so
    a single service action can record one event with its reason.
    """

    from ..repo import tasks as task_repo  # local import keeps the module cycle-free

    source = task["state"]
    transition = assert_can(event, source, actor_role)
    task_repo.set_state(
        conn,
        task["task_id"],
        transition.target,
        updated_at,
        return_count=int(task.get("return_count") or 0) + (1 if transition.target == RETURNED else 0),
        void_reason=str(extra.get("reason")) if transition.target == VOID and extra.get("reason") else None,
    )
    task["state"] = transition.target
    return source


def allowed_events(state: str) -> List[str]:
    return [event for event, transitions in _BY_EVENT.items() if any(state in item.source for item in transitions)]


def describe() -> List[Dict[str, object]]:
    return [
        {
            "event": item.event,
            "from": list(item.source),
            "to": item.target,
            "actors": list(item.actors),
            "description": item.description,
        }
        for item in TRANSITIONS
    ]
