#!/usr/bin/env python3
"""Run the five Agent capabilities against the configured provider.

The report separates three claims that are easy to conflate:

* flow_compatible: every response parses into the Canonical suggestion contract;
* mock_flow_pass: the offline provider exercises that flow end to end;
* live_pass: a real provider was called and a human adjudicated the suggestions.

Only the last one may be called live quality. Without credentials the script
writes ``NOT_RUN`` and changes nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "platform"))

from agent import (  # noqa: E402
    AgentGateway,
    MockProvider,
    OutputContractError,
    load_api_key,
    load_config,
)
from agent.provider import OpenAICompatibleProvider  # noqa: E402
from app.domain.agent_service import safe_payload  # noqa: E402

CAPABILITIES = ("interview", "followup", "structuring", "precheck", "review_assist")
EXPECTED_PREFIX = {
    "interview": ("identity",),
    "followup": ("identity", "materials"),
    "structuring": ("deliverables",),
    "precheck": ("success_criteria", "environment"),
    "review_assist": ("review",),
}
REQUIRED = {"field_path", "value", "confidence", "rationale", "evidence"}


def _valid_suggestion(item: Dict[str, Any]) -> bool:
    if set(item) != REQUIRED:
        return False
    if not isinstance(item.get("field_path"), str) or not item["field_path"]:
        return False
    if not isinstance(item.get("confidence"), (int, float)) or not 0 <= item["confidence"] <= 1:
        return False
    if not isinstance(item.get("rationale"), str) or not item["rationale"].strip():
        return False
    evidence = item.get("evidence")
    return isinstance(evidence, list) and bool(evidence) and all(
        isinstance(value, str) and value.strip() for value in evidence
    )


def _expected_path(capability: str, suggestions: List[Dict[str, Any]]) -> bool:
    prefixes = EXPECTED_PREFIX[capability]
    return any(
        str(item.get("field_path") or "").startswith(prefix)
        for item in suggestions
        for prefix in prefixes
    )


def _result_row(capability: str, result: Any) -> Dict[str, Any]:
    payload = result.to_dict()
    suggestions = payload["suggestions"]
    valid = [item for item in suggestions if _valid_suggestion(item)]
    return {
        "capability": capability,
        "status": payload["run"]["status"],
        "suggestion_count": len(suggestions),
        "valid_suggestion_count": len(valid),
        "expected_path_hit": _expected_path(capability, suggestions),
        "path_contract_ok": len(valid) == len(suggestions) and bool(suggestions),
        "mock_only": bool(payload["mock_only"]),
        "degraded": bool(payload["run"]["degraded"]),
        "fallback_present": bool(payload.get("fallback")),
        "model": payload["run"]["model"],
        "model_version": payload["run"]["model_version"],
        "prompt_version": payload["run"]["prompt_version"],
        "latency_ms": payload["run"]["latency_ms"],
        "tokens_in": payload["run"]["tokens_in"],
        "tokens_out": payload["run"]["tokens_out"],
        "cost_status": payload["run"]["cost_status"],
        "error_code": payload["run"]["error_code"],
        "suggestions": suggestions,
    }


def _resilience(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for failure in ("timeout", "rate_limit", "server"):
        gateway = AgentGateway(MockProvider(fail=failure), load_config())
        result = gateway.generate("structuring", task, raise_on_error=False)
        rows.append(
            {
                "injected": failure,
                "degraded": bool(result.run.degraded),
                "suggestions": len(result.suggestions),
                "fallback": bool(result.fallback),
                "error_code": result.run.error_code,
                "ok": bool(result.fallback) and not result.suggestions and result.run.degraded,
            }
        )
    for failure in ("malformed", "unknown_field", "missing_field"):
        gateway = AgentGateway(MockProvider(fail=failure), load_config())
        try:
            gateway.generate("structuring", task)
        except OutputContractError as exc:
            rows.append(
                {
                    "injected": failure,
                    "rejected": True,
                    "error_code": getattr(exc, "code", type(exc).__name__),
                    "ok": True,
                }
            )
        else:
            rows.append({"injected": failure, "rejected": False, "ok": False})
    return rows


def run(out: Path, task_path: Path) -> Dict[str, Any]:
    task = safe_payload(json.loads(task_path.read_text(encoding="utf-8")))
    reference_removed = all(
        str(item.get("role") or "") != "reference"
        and not str(item.get("path") or "").startswith("reference/")
        for item in task.get("materials", [])
    )
    config = load_config()
    if config.provider == "mock":
        provider = MockProvider()
    else:
        provider = OpenAICompatibleProvider(config, api_key=load_api_key(config))
    gateway = AgentGateway(provider, config)
    rows = []
    for capability in CAPABILITIES:
        try:
            result = gateway.generate(capability, task, raise_on_error=False)
            rows.append(_result_row(capability, result))
        except Exception as exc:  # a rejected contract is a result, not a crash
            rows.append(
                {
                    "capability": capability,
                    "status": "contract_error",
                    "error_code": getattr(exc, "code", getattr(exc, "error_code", type(exc).__name__)),
                    "suggestion_count": 0,
                    "valid_suggestion_count": 0,
                    "expected_path_hit": False,
                    "path_contract_ok": False,
                    "mock_only": False,
                    "degraded": False,
                    "fallback_present": False,
                }
            )
    resilience = _resilience(task)
    flow_ok = all(
        row.get("path_contract_ok") and row.get("expected_path_hit") and not row.get("degraded")
        for row in rows
    ) and all(row["ok"] for row in resilience)
    mock_only = bool(getattr(provider, "is_mock", False))
    if mock_only:
        status = "MOCK_FLOW_ONLY"
    elif flow_ok:
        status = "LIVE_FLOW_PASS_REQUIRES_ADJUDICATION"
    else:
        status = "LIVE_FAIL"
    report = {
        "status": status,
        "provider": config.provider,
        "model_id": config.model_id,
        "prompt_version": config.prompt_version,
        "structured_output": config.structured_output,
        "mock_only": mock_only,
        "reference_removed_before_prompt": reference_removed,
        "flow_compatible": flow_ok,
        "mock_flow_pass": flow_ok if mock_only else None,
        "live_connectivity_pass": (flow_ok and not mock_only),
        "live_pass": False,
        "live_pass_reason": (
            "未配置真实 Provider，未调用真实模型" if mock_only else
            "真实调用还没有独立专家对专业真实性、误报和漏报做裁决"
        ),
        "capabilities": rows,
        "resilience": resilience,
        "limitations": [
            "confidence 是模型自报，不是质量结论",
            "mock 输出不能当作真实模型效果",
            "未测量专家修改率、专业事实错误、误报与漏报",
            "成本未配置计价时 cost_status=unknown",
        ],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ROOT / "docs/evidence/w5/agent-calibration.json"))
    parser.add_argument("--task", default=str(ROOT / "tools/wave5/calibration-task.json"))
    args = parser.parse_args()
    report = run(Path(args.out), Path(args.task))
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["flow_compatible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
