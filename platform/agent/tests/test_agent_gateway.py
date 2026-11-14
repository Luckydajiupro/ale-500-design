"""Offline tests for the Agent model gateway.

Everything here runs with ``MockProvider`` or ``httpx.MockTransport``: no test
reaches a real model, no test needs a real API key, and the suite is expected to
pass on Python 3.9.

Run from the repository root:

    PYTHONPATH=platform .venv/bin/python -m pytest platform/agent/tests -q
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import httpx

from agent import config as config_module
from agent.config import (
    ConfigError,
    ModelConfig,
    SecretError,
    load_api_key,
    load_config,
)
from agent.gateway import (
    AgentGateway,
    AgentInputError,
    AgentUnavailableError,
    build_prompts,
    input_hash,
    parse_model_json,
)
from agent.provider import (
    MockProvider,
    ModelProvider,
    ModelResponse,
    OpenAICompatibleProvider,
    ProviderAuthError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from agent.redaction import REDACTED, redact_text, redact_value
from agent.schemas import (
    CAPABILITIES,
    OutputContractError,
    is_block_level_path,
    path_is_canonical,
)

SECRET = "test-secret-key-1234567890"

TASK = {
    "identity": {
        "task_id": "T-001",
        "domain_code": "finance",
        "subdomain_code": "analysis",
        "title_zh": "示例任务",
        "language": "zh-CN",
        "batch_id": "B-001",
        "owner_expert_id": "expert-1",
        "difficulty_rationale": "演示",
    },
    "materials": [
        {
            "material_id": "mat-1",
            "kind": "document",
            "role": "input",
            "path": "inputs/a.xlsx",
            "sha256": "a" * 64,
            "bytes": 128,
            "license": "internal",
            "pii_level": "none",
            "used_by": ["step-1"],
        }
    ],
    "deliverables": [
        {
            "deliverable_id": "del-1",
            "path": "outputs/a.xlsx",
            "format": "xlsx",
            "description": "结果表",
            "produced_by_step": "step-1",
            "mandatory": True,
            "acceptance_ref": "crit-1",
        }
    ],
    "success_criteria": [
        {
            "criterion_id": "crit-1",
            "dimension": "correctness",
            "check_method": "compare",
            "weight": 1,
            "threshold": "exact",
            "evidence_required": ["diff"],
            "critical": True,
        }
    ],
    "environment": {
        "os": "linux",
        "gui_required": False,
        "gpu": False,
        "network": False,
        "resources": {"cpu": 2, "memory_gb": 4, "disk_gb": 10},
        "nested_virt": False,
    },
    "review": {
        "risk_tier": "low",
        "tier_rationale": "演示",
        "required_reviewers": ["reviewer-1"],
        "open_issues": [],
    },
}

PRECHECK_OUTPUT = {
    "suggestions": [
        {
            "field_path": "success_criteria[0].threshold",
            "value": {"finding": "阈值缺少测量方法。", "severity": "warning"},
            "confidence": 0.7,
            "rationale": "预检发现可复现性缺口。",
            "evidence": ["task.success_criteria[0].threshold"],
        }
    ]
}


class StubProvider(ModelProvider):
    """Returns a fixed raw string, so parsing/validation can be tested alone."""

    name = "stub"
    is_mock = True

    def __init__(self, text: str) -> None:
        self.text = text

    def complete(self, **kwargs) -> ModelResponse:
        return ModelResponse(
            text=self.text,
            model="stub-model",
            model_version="stub-v1",
            tokens_in=3,
            tokens_out=4,
            latency_ms=1,
            attempts=1,
        )


def gateway_for(provider: ModelProvider) -> AgentGateway:
    return AgentGateway(provider, ModelConfig(provider="mock"))


class MockCapabilityTests(unittest.TestCase):
    def test_all_five_capabilities_succeed_with_mock(self) -> None:
        gateway = gateway_for(MockProvider())
        for capability in CAPABILITIES:
            with self.subTest(capability=capability):
                result = gateway.generate(capability, TASK)
                self.assertEqual(result.capability, capability)
                self.assertEqual(result.run.status, "success")
                self.assertIsNone(result.run.error_code)
                self.assertTrue(result.mock_only)
                self.assertTrue(result.run.mock_only)
                self.assertTrue(result.suggestions)
                self.assertEqual(result.run.model, "mock-deterministic")
                self.assertEqual(result.run.model_version, "mock-deterministic-v1")
                self.assertEqual(result.run.prompt_version, "agent-v1")
                self.assertEqual(len(result.run.input_hash), 64)
                self.assertEqual(len(result.run.prompt_hash), 64)
                self.assertGreaterEqual(result.run.latency_ms, 0)
                self.assertGreater(result.run.tokens_in, 0)
                self.assertGreater(result.run.tokens_out, 0)
                self.assertEqual(result.run.cost_cents, 0)
                self.assertEqual(result.run.cost_status, "not_applicable")
                json.dumps(result.to_dict(), ensure_ascii=False)

    def test_suggestions_are_legal_canonical_paths(self) -> None:
        gateway = gateway_for(MockProvider())
        required = {
            "field_path",
            "value",
            "confidence",
            "rationale",
            "evidence",
        }
        for capability in CAPABILITIES:
            result = gateway.generate(capability, TASK)
            for suggestion in result.suggestions:
                self.assertEqual(set(suggestion), required)
                self.assertTrue(path_is_canonical(suggestion["field_path"]))
                self.assertFalse(
                    suggestion["field_path"].split(".")[0]
                    in ("verification", "package")
                )
                self.assertGreaterEqual(suggestion["confidence"], 0)
                self.assertLessEqual(suggestion["confidence"], 1)
                if capability == "interview":
                    self.assertTrue(is_block_level_path(suggestion["field_path"]))

    def test_interview_value_shape(self) -> None:
        result = gateway_for(MockProvider()).generate("interview", TASK)
        value = result.suggestions[0]["value"]
        self.assertEqual(set(value), {"question", "why"})

    def test_input_hash_is_stable_and_order_independent(self) -> None:
        gateway = gateway_for(MockProvider())
        first = gateway.generate("followup", TASK)
        reordered = dict(reversed(list(TASK.items())))
        second = gateway.generate("followup", reordered)
        self.assertEqual(first.run.input_hash, second.run.input_hash)
        self.assertEqual(first.run.prompt_hash, second.run.prompt_hash)

        changed = json.loads(json.dumps(TASK))
        changed["identity"]["title_zh"] = "另一个任务"
        third = gateway.generate("followup", changed)
        self.assertNotEqual(first.run.input_hash, third.run.input_hash)

    def test_input_hash_helper_matches_run(self) -> None:
        gateway = gateway_for(MockProvider())
        result = gateway.generate("structuring", TASK)
        self.assertEqual(result.run.input_hash, input_hash("structuring", TASK, None))


class OutputContractTests(unittest.TestCase):
    def test_markdown_fence_is_rejected(self) -> None:
        gateway = gateway_for(MockProvider(fail="malformed"))
        with self.assertRaises(OutputContractError) as ctx:
            gateway.generate("precheck", TASK)
        self.assertEqual(ctx.exception.code, "OUTPUT_MARKDOWN_FENCE")

    def test_prose_is_rejected_as_non_json(self) -> None:
        gateway = gateway_for(StubProvider("Sure, here are some suggestions."))
        with self.assertRaises(OutputContractError) as ctx:
            gateway.generate("precheck", TASK)
        self.assertEqual(ctx.exception.code, "OUTPUT_NOT_JSON")

    def test_unknown_field_is_rejected(self) -> None:
        gateway = gateway_for(MockProvider(fail="unknown_field"))
        with self.assertRaises(OutputContractError) as ctx:
            gateway.generate("precheck", TASK)
        self.assertEqual(ctx.exception.code, "OUTPUT_UNKNOWN_FIELD")

    def test_missing_field_is_rejected(self) -> None:
        gateway = gateway_for(MockProvider(fail="missing_field"))
        with self.assertRaises(OutputContractError) as ctx:
            gateway.generate("precheck", TASK)
        self.assertEqual(ctx.exception.code, "OUTPUT_MISSING_FIELD")

    def test_platform_owned_block_path_is_rejected(self) -> None:
        text = json.dumps(
            {
                "suggestions": [
                    {
                        "field_path": "verification",
                        "value": "ok",
                        "confidence": 0.5,
                        "rationale": "不应写入平台派生块。",
                        "evidence": ["e"],
                    }
                ]
            }
        )
        gateway = gateway_for(StubProvider(text))
        with self.assertRaises(OutputContractError) as ctx:
            gateway.generate("followup", TASK)
        self.assertEqual(ctx.exception.code, "OUTPUT_INVALID_PATH")

    def test_forbidden_action_inside_value_is_rejected(self) -> None:
        text = json.dumps(
            {
                "suggestions": [
                    {
                        "field_path": "identity.title_zh",
                        "value": {"action": "submit"},
                        "confidence": 0.5,
                        "rationale": "越权动作。",
                        "evidence": ["e"],
                    }
                ]
            }
        )
        gateway = gateway_for(StubProvider(text))
        with self.assertRaises(OutputContractError) as ctx:
            gateway.generate("followup", TASK)
        self.assertEqual(ctx.exception.code, "OUTPUT_FORBIDDEN_ACTION")

    def test_parse_model_json_rejects_array(self) -> None:
        with self.assertRaises(OutputContractError) as ctx:
            parse_model_json("[]")
        self.assertEqual(ctx.exception.code, "OUTPUT_NOT_JSON")

    def test_unknown_capability_is_rejected(self) -> None:
        with self.assertRaises(AgentInputError):
            gateway_for(MockProvider()).generate("deploy", TASK)


class DegradationTests(unittest.TestCase):
    def test_mock_timeout_raises_degradable_error(self) -> None:
        gateway = gateway_for(MockProvider(fail="timeout"))
        with self.assertRaises(AgentUnavailableError) as ctx:
            gateway.generate("precheck", TASK)
        error = ctx.exception
        self.assertEqual(error.code, "PROVIDER_TIMEOUT")
        self.assertTrue(error.degradable)
        self.assertTrue(error.retryable)
        self.assertIsNotNone(error.run)
        self.assertEqual(error.run.status, "error")
        self.assertEqual(error.run.error_code, "PROVIDER_TIMEOUT")
        self.assertIn("manual_checklist", error.fallback)
        self.assertTrue(error.fallback["manual_checklist"])

    def test_raise_on_error_false_returns_degraded_result(self) -> None:
        gateway = gateway_for(MockProvider(fail="server"))
        result = gateway.generate("review_assist", TASK, raise_on_error=False)
        self.assertEqual(result.suggestions, [])
        self.assertEqual(result.run.status, "error")
        self.assertEqual(result.run.error_code, "PROVIDER_UNAVAILABLE")
        self.assertTrue(result.run.degraded)
        self.assertTrue(result.fallback["manual_checklist"])
        self.assertIn("模型暂不可用", result.fallback["notice"])

    def test_unknown_provider_exception_is_wrapped(self) -> None:
        class BrokenProvider(ModelProvider):
            is_mock = True

            def complete(self, **kwargs):
                raise RuntimeError("boom")

        with self.assertRaises(AgentUnavailableError) as ctx:
            gateway_for(BrokenProvider()).generate("precheck", TASK)
        self.assertEqual(ctx.exception.code, "AGENT_INTERNAL_ERROR")


class RetryAndHttpTests(unittest.TestCase):
    def _config(self, **overrides) -> ModelConfig:
        values = dict(
            provider="openai_compatible",
            base_url="https://model.example.invalid/v1",
            model_id="test-model-2026",
            timeout=2.0,
            max_retries=2,
            structured_output="json_schema",
        )
        values.update(overrides)
        return ModelConfig(**values)

    def test_429_is_retried_with_retry_after(self) -> None:
        calls = []
        sleeps = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(request)
            if len(calls) == 1:
                return httpx.Response(
                    429,
                    headers={"Retry-After": "0.25"},
                    json={"error": {"message": "slow down"}},
                )
            return httpx.Response(
                200,
                json={
                    "model": "test-model-2026-served",
                    "choices": [
                        {
                            "message": {"content": json.dumps(PRECHECK_OUTPUT)},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 11, "completion_tokens": 7},
                },
            )

        config = self._config()
        provider = OpenAICompatibleProvider(
            config,
            transport=httpx.MockTransport(handler),
            sleeper=sleeps.append,
            api_key=SECRET,
        )
        gateway = AgentGateway(provider, config)
        result = gateway.generate("precheck", TASK)

        self.assertEqual(len(calls), 2)
        self.assertEqual(result.run.attempts, 2)
        self.assertEqual(result.run.tokens_in, 11)
        self.assertEqual(result.run.tokens_out, 7)
        self.assertEqual(sleeps, [0.25])
        sent = json.loads(calls[0].content.decode("utf-8"))
        self.assertEqual(sent["model"], "test-model-2026")
        self.assertEqual(sent["response_format"]["type"], "json_schema")
        self.assertEqual(
            calls[0].url.path, "/v1/chat/completions"
        )

    def test_429_exhausts_retries_and_degrades(self) -> None:
        calls = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(request)
            return httpx.Response(429, json={"error": {"message": "rate limited"}})

        config = self._config()
        provider = OpenAICompatibleProvider(
            config,
            transport=httpx.MockTransport(handler),
            sleeper=lambda _seconds: None,
            api_key=SECRET,
        )
        with self.assertRaises(AgentUnavailableError) as ctx:
            AgentGateway(provider, config).generate("precheck", TASK)
        self.assertEqual(ctx.exception.code, "PROVIDER_RATE_LIMITED")
        self.assertTrue(ctx.exception.retryable)
        self.assertEqual(len(calls), 3)

    def test_timeout_is_retried_then_succeeds(self) -> None:
        calls = []
        sleeps = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(request)
            if len(calls) == 1:
                raise httpx.ReadTimeout("read timed out", request=request)
            return httpx.Response(
                200,
                json={
                    "model": "test-model-2026",
                    "choices": [
                        {
                            "message": {"content": json.dumps(PRECHECK_OUTPUT)},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 2, "completion_tokens": 2},
                },
            )

        config = self._config(max_retries=1)
        provider = OpenAICompatibleProvider(
            config,
            transport=httpx.MockTransport(handler),
            sleeper=sleeps.append,
            api_key=SECRET,
        )
        result = AgentGateway(provider, config).generate("precheck", TASK)
        self.assertEqual(len(calls), 2)
        self.assertEqual(result.run.attempts, 2)
        self.assertEqual(len(sleeps), 1)

    def test_timeout_exhaustion_maps_to_provider_timeout(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("read timed out", request=request)

        config = self._config(max_retries=1)
        provider = OpenAICompatibleProvider(
            config,
            transport=httpx.MockTransport(handler),
            sleeper=lambda _seconds: None,
            api_key=SECRET,
        )
        with self.assertRaises(AgentUnavailableError) as ctx:
            AgentGateway(provider, config).generate("precheck", TASK)
        self.assertEqual(ctx.exception.code, "PROVIDER_TIMEOUT")

    def test_no_retry_on_auth_error(self) -> None:
        calls = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(request)
            return httpx.Response(401, json={"error": {"message": "bad key"}})

        config = self._config(max_retries=3)
        provider = OpenAICompatibleProvider(
            config,
            transport=httpx.MockTransport(handler),
            sleeper=lambda _seconds: None,
            api_key=SECRET,
        )
        with self.assertRaises(AgentUnavailableError) as ctx:
            AgentGateway(provider, config).generate("precheck", TASK)
        self.assertEqual(ctx.exception.code, "PROVIDER_AUTH_FAILED")
        self.assertEqual(len(calls), 1)

    def test_streaming_sse_response_is_parsed(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = (
                'data: {"model":"stream-model","choices":[{"delta":{"content":"{\\"suggestions\\":"}}]}\n\n'
                'data: {"choices":[{"delta":{"content":"[]}"},"finish_reason":"stop"}]}\n\n'
                "data: [DONE]\n\n"
            )
            return httpx.Response(
                200, headers={"Content-Type": "text/event-stream"}, text=body
            )

        config = self._config(stream=True)
        provider = OpenAICompatibleProvider(
            config,
            transport=httpx.MockTransport(handler),
            sleeper=lambda _seconds: None,
            api_key=SECRET,
        )
        result = AgentGateway(provider, config).generate("precheck", TASK)
        self.assertEqual(result.run.status, "success")
        self.assertEqual(result.suggestions, [])
        self.assertEqual(result.run.model, "stream-model")


class SecretSafetyTests(unittest.TestCase):
    def test_api_key_never_appears_in_errors_or_logs(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            # A hostile provider echoes the credential back in the error body.
            return httpx.Response(
                401, text="invalid credential %s" % SECRET
            )

        config = ModelConfig(
            provider="openai_compatible",
            base_url="https://model.example.invalid/v1",
            model_id="m",
            timeout=2.0,
            max_retries=0,
        )
        provider = OpenAICompatibleProvider(
            config,
            transport=httpx.MockTransport(handler),
            api_key=SECRET,
        )
        with mock.patch.dict(os.environ, {"ALE_MODEL_API_KEY": SECRET}, clear=False):
            with self.assertLogs("agent", level=logging.WARNING) as captured:
                with self.assertRaises(AgentUnavailableError) as ctx:
                    AgentGateway(provider, config).generate("precheck", TASK)
        error = ctx.exception
        self.assertNotIn(SECRET, str(error))
        self.assertNotIn(SECRET, json.dumps(error.run.to_dict(), ensure_ascii=False))
        self.assertNotIn(SECRET, json.dumps(error.fallback, ensure_ascii=False))
        self.assertIn(REDACTED, str(error))
        log_text = "\n".join(captured.output)
        self.assertNotIn(SECRET, log_text)

    def test_api_key_is_not_in_the_prompt(self) -> None:
        captured = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = request.content.decode("utf-8")
            return httpx.Response(
                200,
                json={
                    "model": "m",
                    "choices": [
                        {
                            "message": {"content": json.dumps(PRECHECK_OUTPUT)},
                            "finish_reason": "stop",
                        }
                    ],
                },
            )

        config = ModelConfig(
            provider="openai_compatible",
            base_url="https://model.example.invalid/v1",
            model_id="m",
            timeout=2.0,
            max_retries=0,
        )
        provider = OpenAICompatibleProvider(
            config,
            transport=httpx.MockTransport(handler),
            api_key=SECRET,
        )
        AgentGateway(provider, config).generate("precheck", TASK)
        self.assertNotIn(SECRET, captured["body"])

    def test_redaction_filter_and_helpers(self) -> None:
        text = (
            "Authorization: Bearer %s\n"
            "Cookie: session=abc\n"
            "path=/Users/alice/private/key.txt" % SECRET
        )
        cleaned = redact_text(text, SECRET)
        self.assertNotIn(SECRET, cleaned)
        self.assertNotIn("/Users/alice", cleaned)
        self.assertNotIn("session=abc", cleaned)
        nested = redact_value({"api_key": SECRET, "nested": {"token": "abc"}})
        self.assertEqual(nested["api_key"], REDACTED)
        self.assertEqual(nested["nested"]["token"], REDACTED)


class ConfigTests(unittest.TestCase):
    def test_example_config_loads(self) -> None:
        path = Path(__file__).resolve().parents[1] / "config.example.toml"
        config = load_config(path=path, env={})
        self.assertEqual(config.provider, "mock")
        self.assertEqual(config.structured_output, "none")
        self.assertEqual(config.api_key_env, "ALE_MODEL_API_KEY")
        self.assertEqual(config.secret_file, "")

    def test_environment_overrides(self) -> None:
        config = load_config(
            env={
                "ALE_MODEL_PROVIDER": "openai_compatible",
                "ALE_MODEL_BASE_URL": "https://model.example.invalid/v1",
                "ALE_MODEL_ID": "m-1",
                "ALE_MODEL_TIMEOUT": "7.5",
                "ALE_MODEL_MAX_RETRIES": "0",
                "ALE_MODEL_STRUCTURED_OUTPUT": "json_object",
            }
        )
        self.assertEqual(config.provider, "openai_compatible")
        self.assertEqual(config.timeout, 7.5)
        self.assertEqual(config.max_retries, 0)
        self.assertEqual(config.structured_output, "json_object")

    def test_unknown_toml_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "agent.toml"
            path.write_text("[model]\nprovider = \"mock\"\napi_key = \"nope\"\n")
            with self.assertRaises(ConfigError):
                load_config(path=path, env={})

    def test_invalid_provider_is_rejected(self) -> None:
        with self.assertRaises(ConfigError):
            ModelConfig(provider="other")

    def test_simple_toml_fallback_parses_example(self) -> None:
        path = Path(__file__).resolve().parents[1] / "config.example.toml"
        with mock.patch.object(config_module, "_toml", None):
            config = load_config(path=path, env={})
        self.assertEqual(config.provider, "mock")
        self.assertEqual(config.timeout, 30.0)
        self.assertFalse(config.stream)

    def test_secret_file_requires_owner_only_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "key"
            path.write_text(SECRET)
            path.chmod(0o600)
            config = ModelConfig(secret_file=str(path))
            self.assertEqual(load_api_key(config, env={}), SECRET)

            path.chmod(0o644)
            with self.assertRaises(SecretError) as ctx:
                load_api_key(config, env={})
            self.assertNotIn(SECRET, str(ctx.exception))

    def test_container_secret_permissions_allow_read_only_root_secret(self) -> None:
        from agent.config import _secret_permissions_ok

        self.assertTrue(_secret_permissions_ok(0o600, "/tmp/key"))
        self.assertTrue(_secret_permissions_ok(0o444, "/run/secrets/model_api_key"))
        self.assertFalse(_secret_permissions_ok(0o644, "/tmp/key"))
        self.assertFalse(_secret_permissions_ok(0o444, "/tmp/key"))

    def test_secret_file_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "real"
            target.write_text(SECRET)
            target.chmod(0o600)
            link = Path(directory) / "link"
            link.symlink_to(target)
            with self.assertRaises(SecretError):
                load_api_key(ModelConfig(secret_file=str(link)), env={})

    def test_missing_key_raises_without_value(self) -> None:
        config = ModelConfig(api_key_env="ALE_TEST_MISSING_KEY", secret_file="")
        with self.assertRaises(SecretError) as ctx:
            load_api_key(config, env={})
        self.assertIn("ALE_TEST_MISSING_KEY", str(ctx.exception))
        self.assertNotIn(SECRET, str(ctx.exception))

    def test_public_dict_has_no_key_material(self) -> None:
        config = ModelConfig(
            provider="openai_compatible",
            base_url="https://model.example.invalid/v1",
            model_id="m",
            secret_file="/Users/alice/.config/ale/key",
        )
        public = config.public_dict()
        self.assertNotIn("api_key", public)
        self.assertNotIn("/Users/alice", json.dumps(public))

    def test_prompt_builder_is_deterministic(self) -> None:
        first = build_prompts("precheck", TASK, None, "agent-v1")
        second = build_prompts("precheck", TASK, None, "agent-v1")
        self.assertEqual(first, second)
        self.assertIn("suggestions", first[0])
        self.assertIn("agent-v1", first[0])


class ProviderUnitTests(unittest.TestCase):
    def test_rate_limit_error_attributes(self) -> None:
        error = ProviderRateLimitError("limited", retry_after=1.5)
        self.assertTrue(error.retryable)
        self.assertEqual(error.error_code, "PROVIDER_RATE_LIMITED")
        self.assertEqual(error.retry_after, 1.5)

    def test_timeout_error_attributes(self) -> None:
        error = ProviderTimeoutError("timeout")
        self.assertTrue(error.retryable)
        self.assertEqual(error.error_code, "PROVIDER_TIMEOUT")

    def test_auth_error_attributes(self) -> None:
        error = ProviderAuthError("bad key")
        self.assertFalse(error.retryable)
        self.assertEqual(error.error_code, "PROVIDER_AUTH_FAILED")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
