"""Model-backed agent suggestions with an explicit mock fallback.

The gateway owns prompting, provider calls, output validation and run records.
This module adds the platform boundary: task-level authorization, reference
redaction, persistence, and the rule that no suggestion is written into the
task source before a human confirms it.
"""

from __future__ import annotations

import copy
import json
from typing import Any, Dict, List, Optional

from agent import (
    AgentGateway,
    AgentUnavailableError,
    MockProvider,
    OpenAICompatibleProvider,
    OutputContractError,
    load_api_key,
    load_config,
)

from ..adapters import new_id, now
from ..auth import Principal
from ..repo import tasks as task_repo

CAPABILITIES = ("interview", "followup", "structuring", "precheck", "review_assist")


class AgentServiceError(Exception):
    def __init__(self, code: str, message: str, status: int = 422) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


def build_gateway() -> AgentGateway:
    config = load_config()
    if config.provider == "mock":
        provider = MockProvider()
    else:
        provider = OpenAICompatibleProvider(config, api_key=load_api_key(config))
    return AgentGateway(provider, config)


def safe_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Remove evaluator-only material before anything is sent to a model."""

    safe = copy.deepcopy(payload)
    safe["materials"] = [
        item
        for item in safe.get("materials", [])
        if str(item.get("role") or "") != "reference"
        and not str(item.get("path") or "").startswith("reference/")
    ]
    return safe


def _suggestion_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def generate(
    conn: Any,
    principal: Principal,
    task_id: str,
    capability: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if capability not in CAPABILITIES:
        raise AgentServiceError("AGENT_CAPABILITY", "未知 Agent 能力")
    task = task_repo.get_task(conn, task_id)
    if task is None:
        raise AgentServiceError("NOT_FOUND", "任务不存在", 404)
    if capability == "review_assist":
        assigned = conn.execute(
            "SELECT 1 AS present FROM reviews WHERE task_id = ? AND reviewer_id = ? LIMIT 1",
            (task_id, principal.user_id),
        ).fetchone()
        if assigned is None:
            raise AgentServiceError("FORBIDDEN", "只能为分配给自己的评审生成建议", 403)
    elif task["owner_expert_id"] != principal.user_id:
        raise AgentServiceError("FORBIDDEN", "只能为自己的任务生成建议", 403)
    payload = json.loads(task["draft_payload"])
    gateway = build_gateway()
    try:
        result = gateway.generate(capability, safe_payload(payload), context or {}, raise_on_error=False)
    except (OutputContractError, AgentUnavailableError) as exc:
        raise AgentServiceError("AGENT_OUTPUT_INVALID", str(exc), 502)
    run = result.run
    created = now()
    model_name = "%s:%s" % (gateway.config.provider, run.model)
    conn.execute(
        """INSERT INTO agent_runs
           (run_id, task_id, capability, model, model_version, prompt_hash, input_hash, status,
            latency_ms, cost_cents, cost_status, created_at, prompt_version, tokens_in, tokens_out,
            degraded, mock_only, error_code)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            run.run_id, task_id, capability, model_name, str(run.model_version or ""),
            run.prompt_hash, run.input_hash, run.status, int(run.latency_ms or 0),
            int(run.cost_cents or 0), str(run.cost_status or "unknown"), created, gateway.config.prompt_version,
            int(run.tokens_in or 0), int(run.tokens_out or 0),
            1 if run.degraded else 0, 1 if run.mock_only else 0, run.error_code,
        ),
    )
    count = 0
    for suggestion in result.suggestions:
        conn.execute(
            """INSERT INTO agent_suggestions
               (suggestion_id, run_id, task_id, field_path, suggested_value, confidence,
                model, model_version, prompt_hash, input_hash, state, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,'proposed',?)""",
            (
                new_id("sug"), run.run_id, task_id, str(suggestion.get("field_path")),
                _suggestion_value(suggestion.get("value")),
                float(suggestion.get("confidence") or 0.0),
                model_name, str(run.model_version or ""), run.prompt_hash, run.input_hash, created,
            ),
        )
        count += 1
    return {
        "run_id": run.run_id,
        "capability": capability,
        "count": count,
        "degraded": bool(run.degraded),
        "mock_only": bool(run.mock_only),
        "fallback": result.fallback,
        "error_code": run.error_code,
    }
