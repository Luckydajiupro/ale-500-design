"""Model providers for the Agent gateway.

The gateway depends on the small :class:`ModelProvider` protocol, not on HTTP.
That keeps three things possible at once:

* a real OpenAI-compatible endpoint (:class:`OpenAICompatibleProvider`);
* deterministic offline tests and demos (:class:`MockProvider`);
* a future provider (local model, another vendor) without touching the gateway.

Provider failures are normalized into :class:`ProviderError` subclasses. They are
all degradable: the gateway turns them into an ``AgentUnavailableError`` with a
manual fallback checklist, and the Web layer is expected to keep working.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional, Protocol

import httpx

from .config import ModelConfig, SecretError, load_api_key
from .redaction import redact_text, safe_exception_message

logger = logging.getLogger(__name__)


class ProviderError(RuntimeError):
    """A model call failed in a way the gateway can degrade around."""

    code = "PROVIDER_ERROR"
    retryable = False
    degradable = True

    def __init__(
        self, message: str, *, status_code: Optional[int] = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code

    @property
    def error_code(self) -> str:
        return self.code


class ProviderTimeoutError(ProviderError):
    code = "PROVIDER_TIMEOUT"
    retryable = True


class ProviderRateLimitError(ProviderError):
    code = "PROVIDER_RATE_LIMITED"
    retryable = True

    def __init__(
        self,
        message: str,
        *,
        retry_after: Optional[float] = None,
        status_code: int = 429,
    ) -> None:
        super().__init__(message, status_code=status_code)
        self.retry_after = retry_after


class ProviderAuthError(ProviderError):
    code = "PROVIDER_AUTH_FAILED"


class ProviderRequestError(ProviderError):
    code = "PROVIDER_REQUEST_INVALID"


class ProviderServerError(ProviderError):
    code = "PROVIDER_UNAVAILABLE"
    retryable = True


class ProviderOutputError(ProviderError):
    code = "PROVIDER_OUTPUT_INVALID"


@dataclass(frozen=True)
class ModelResponse:
    """One successful model call, with enough metadata for an audit record."""

    text: str
    model: str = ""
    model_version: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0
    attempts: int = 1
    finish_reason: str = ""

    @property
    def cost_relevant_tokens(self) -> tuple:
        return (self.tokens_in, self.tokens_out)


class ModelProvider(Protocol):
    """Structural interface: one deterministic text-completion call."""

    name: str
    is_mock: bool

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: Optional[Mapping[str, Any]] = None,
        capability: str = "",
        prompt_version: str = "",
        temperature: float = 0.0,
    ) -> ModelResponse:
        ...


class _RateLimiter:
    """A small sliding-window limiter; no third-party dependency."""

    def __init__(
        self,
        max_calls: int,
        period: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self._max_calls = max(1, int(max_calls))
        self._period = period
        self._clock = clock
        self._sleep = sleeper
        self._calls = []

    def acquire(self) -> None:
        while True:
            now = self._clock()
            self._calls = [stamp for stamp in self._calls if now - stamp < self._period]
            if len(self._calls) < self._max_calls:
                self._calls.append(now)
                return
            wait = self._period - (now - self._calls[0])
            self._sleep(min(max(wait, 0.01), 5.0))


class OpenAICompatibleProvider(ModelProvider):
    """``POST {base_url}/chat/completions`` with bounded retries.

    ``transport``, ``sleeper`` and ``api_key`` exist for tests. In production
    leave them unset: the key is loaded from ``ALE_MODEL_API_KEY`` or the
    configured 0600 secret file, and is never attached to errors or logs.
    """

    name = "openai_compatible"
    is_mock = False

    def __init__(
        self,
        config: ModelConfig,
        *,
        transport: Optional[httpx.BaseTransport] = None,
        sleeper: Callable[[float], None] = time.sleep,
        api_key: Optional[str] = None,
    ) -> None:
        self.config = config
        self._transport = transport
        self._sleep = sleeper
        self._api_key = api_key
        self._limiter = _RateLimiter(
            config.rate_limit_per_min, sleeper=sleeper
        )
        self._endpoint = self._build_endpoint(config.base_url)

    @staticmethod
    def _build_endpoint(base_url: str) -> str:
        base = base_url.rstrip("/")
        if base.endswith("/chat/completions"):
            return base
        return base + "/chat/completions"

    def _resolve_key(self) -> str:
        if self._api_key:
            return self._api_key
        try:
            key = load_api_key(self.config)
        except SecretError as exc:
            raise ProviderAuthError(redact_text(str(exc))) from exc
        if not key:
            raise ProviderAuthError("未配置模型密钥")
        return key

    def _payload(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Optional[Mapping[str, Any]],
        capability: str,
        temperature: float,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.config.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": self.config.max_output_tokens,
        }
        mode = self.config.structured_output
        if mode == "json_schema":
            if schema is None:
                raise ProviderRequestError(
                    "structured_output=json_schema 需要调用方提供 JSON Schema"
                )
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": (capability or "agent_output") + "_output",
                    "strict": True,
                    "schema": dict(schema),
                },
            }
        elif mode == "json_object":
            payload["response_format"] = {"type": "json_object"}
        if self.config.stream:
            payload["stream"] = True
        return payload

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: Optional[Mapping[str, Any]] = None,
        capability: str = "",
        prompt_version: str = "",
        temperature: float = 0.0,
    ) -> ModelResponse:
        key = self._resolve_key()
        payload = self._payload(
            system_prompt, user_prompt, schema, capability, temperature
        )
        headers = {
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Agent-Prompt-Version": prompt_version or self.config.prompt_version,
        }
        attempts_allowed = self.config.max_retries + 1
        started = time.monotonic()
        last_error: Optional[ProviderError] = None

        for attempt in range(1, attempts_allowed + 1):
            self._limiter.acquire()
            try:
                data = self._send(payload, headers)
                text, finish_reason = self._extract_text(data)
                usage = data.get("usage") or {}
                response = ModelResponse(
                    text=text,
                    model=str(data.get("model") or self.config.model_id),
                    model_version=str(
                        data.get("model") or self.config.model_id
                    ),
                    tokens_in=int(
                        usage.get("prompt_tokens")
                        or usage.get("input_tokens")
                        or 0
                    ),
                    tokens_out=int(
                        usage.get("completion_tokens")
                        or usage.get("output_tokens")
                        or 0
                    ),
                    latency_ms=int((time.monotonic() - started) * 1000),
                    attempts=attempt,
                    finish_reason=finish_reason,
                )
                return response
            except ProviderError as exc:
                last_error = exc
                if not exc.retryable or attempt >= attempts_allowed:
                    break
                delay = self._retry_delay(attempt, exc)
                logger.warning(
                    "model call retry %d/%d after %s",
                    attempt,
                    self.config.max_retries,
                    exc.code,
                )
                self._sleep(delay)

        assert last_error is not None
        error = _redacted_copy(last_error, key)
        error.attempts = attempt
        raise error

    def _retry_delay(self, attempt: int, error: ProviderError) -> float:
        if isinstance(error, ProviderRateLimitError) and error.retry_after:
            return min(max(error.retry_after, 0.0), 8.0)
        return min(0.5 * (2 ** (attempt - 1)), 8.0)

    def _send(self, payload: Mapping[str, Any], headers: Mapping[str, str]) -> Dict[str, Any]:
        timeout = httpx.Timeout(self.config.timeout)
        try:
            with httpx.Client(
                transport=self._transport,
                timeout=timeout,
                follow_redirects=False,
            ) as client:
                if self.config.stream:
                    return self._send_stream(client, payload, headers)
                response = client.post(
                    self._endpoint, json=payload, headers=dict(headers)
                )
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError(
                "模型调用超时（%.1fs）: %s"
                % (self.config.timeout, safe_exception_message(exc))
            ) from exc
        except httpx.TransportError as exc:
            raise ProviderServerError(
                "模型网络错误: %s" % safe_exception_message(exc)
            ) from exc

        return self._check_response(response)

    def _check_response(self, response: httpx.Response) -> Dict[str, Any]:
        status = response.status_code
        if status == 200:
            try:
                data = response.json()
            except ValueError as exc:
                raise ProviderOutputError("模型返回的不是 JSON 响应") from exc
            if not isinstance(data, dict):
                raise ProviderOutputError("模型响应顶层不是 JSON 对象")
            return data

        body = redact_text(self._body_snippet(response))
        if status == 429:
            retry_after = self._retry_after(response.headers.get("Retry-After"))
            raise ProviderRateLimitError(
                "模型服务限流（429）: %s" % body, retry_after=retry_after
            )
        if status in (401, 403):
            raise ProviderAuthError("模型服务拒绝认证（%d）: %s" % (status, body))
        if status in (400, 404, 405, 409, 422):
            raise ProviderRequestError(
                "模型请求被拒绝（%d）: %s" % (status, body), status_code=status
            )
        if status >= 500:
            raise ProviderServerError(
                "模型服务不可用（%d）: %s" % (status, body), status_code=status
            )
        raise ProviderRequestError(
            "模型服务返回异常状态（%d）: %s" % (status, body), status_code=status
        )

    @staticmethod
    def _body_snippet(response: httpx.Response) -> str:
        try:
            text = response.text
        except Exception:  # pragma: no cover - defensive
            return "<unreadable body>"
        return text[:300]

    @staticmethod
    def _retry_after(raw: Optional[str]) -> Optional[float]:
        if not raw:
            return None
        try:
            return float(raw.strip())
        except (TypeError, ValueError):
            return None

    def _send_stream(
        self,
        client: httpx.Client,
        payload: Mapping[str, Any],
        headers: Mapping[str, str],
    ) -> Dict[str, Any]:
        chunks = []
        usage: Dict[str, Any] = {}
        model = ""
        finish_reason = ""
        with client.stream(
            "POST", self._endpoint, json=payload, headers=dict(headers)
        ) as response:
            if response.status_code != 200:
                response.read()
                return self._check_response(response)
            for line in response.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    event = json.loads(data)
                except ValueError:
                    continue
                model = str(event.get("model") or model)
                if isinstance(event.get("usage"), dict):
                    usage = event["usage"]
                for choice in event.get("choices") or []:
                    if choice.get("finish_reason"):
                        finish_reason = str(choice["finish_reason"])
                    delta = choice.get("delta") or {}
                    content = delta.get("content")
                    if isinstance(content, str):
                        chunks.append(content)
        return {
            "model": model or self.config.model_id,
            "choices": [
                {
                    "message": {"content": "".join(chunks)},
                    "finish_reason": finish_reason,
                }
            ],
            "usage": usage,
        }

    @staticmethod
    def _extract_text(data: Mapping[str, Any]) -> tuple:
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            error = data.get("error")
            if isinstance(error, Mapping):
                raise ProviderOutputError(
                    "模型返回错误: %s"
                    % redact_text(str(error.get("message") or error.get("code") or ""))
                )
            raise ProviderOutputError("模型响应缺少 choices")
        choice = choices[0]
        if not isinstance(choice, Mapping):
            raise ProviderOutputError("模型响应 choices[0] 不是对象")
        message = choice.get("message")
        if not isinstance(message, Mapping):
            raise ProviderOutputError("模型响应缺少 message")
        content = message.get("content")
        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, Mapping) and isinstance(part.get("text"), str):
                    parts.append(part["text"])
            content = "".join(parts)
        if not isinstance(content, str) or not content.strip():
            raise ProviderOutputError("模型响应内容为空")
        return content, str(choice.get("finish_reason") or "")


def _redacted_copy(template: ProviderError, secret: Optional[str]) -> ProviderError:
    """Preserve the concrete error class/code while using a redacted message."""

    message = redact_text(str(template), secret)
    cls = type(template)
    if cls is ProviderRateLimitError:
        return ProviderRateLimitError(
            message,
            retry_after=getattr(template, "retry_after", None),
            status_code=template.status_code or 429,
        )
    if cls in (
        ProviderTimeoutError,
        ProviderAuthError,
        ProviderRequestError,
        ProviderServerError,
        ProviderOutputError,
    ):
        return cls(message, status_code=template.status_code)
    return ProviderError(message, status_code=template.status_code)


class MockProvider(ModelProvider):
    """Deterministic, offline provider used by tests and demos.

    ``fail`` injects a specific failure branch:

    * ``"timeout"`` / ``"rate_limit"`` / ``"server"`` raise the matching
      degradable provider error;
    * ``"malformed"`` returns prose wrapped in a markdown fence, which the
      gateway must reject;
    * ``"unknown_field"`` returns an extra suggestion key;
    * ``"missing_field"`` drops an evidence list.

    The successful payload depends only on the capability and is valid against
    :mod:`platform.agent.schemas`, so an offline demo exercises the real parsing
    and validation path.
    """

    name = "mock"
    is_mock = True

    _PAYLOADS: Dict[str, Dict[str, Any]] = {
        "interview": {
            "suggestions": [
                {
                    "field_path": "identity",
                    "value": {
                        "question": "目标用户完成该任务时，最关键的输入与输出分别是什么？",
                        "why": "identity 尚未说明可验证的输入输出边界。",
                    },
                    "confidence": 0.82,
                    "rationale": "身份信息缺少输入输出边界，访谈可先补齐。",
                    "evidence": ["demo:interview-1"],
                }
            ]
        },
        "followup": {
            "suggestions": [
                {
                    "field_path": "identity.batch_id",
                    "value": "batch-demo-001",
                    "confidence": 0.66,
                    "rationale": "沿用当前批次的编号规则。",
                    "evidence": ["demo:followup-1"],
                },
                {
                    "field_path": "materials[0].role",
                    "value": "input",
                    "confidence": 0.7,
                    "rationale": "首条资料是任务输入。",
                    "evidence": ["demo:followup-2"],
                },
            ]
        },
        "structuring": {
            "suggestions": [
                {
                    "field_path": "deliverables[0].format",
                    "value": "xlsx",
                    "confidence": 0.74,
                    "rationale": "交付物需要可计算的表格。",
                    "evidence": ["demo:structuring-1"],
                }
            ]
        },
        "precheck": {
            "suggestions": [
                {
                    "field_path": "success_criteria[0].threshold",
                    "value": {
                        "finding": "阈值缺少可复现的测量方法。",
                        "severity": "warning",
                    },
                    "confidence": 0.61,
                    "rationale": "检查项未说明如何测量阈值。",
                    "evidence": ["demo:precheck-1"],
                }
            ]
        },
        "review_assist": {
            "suggestions": [
                {
                    "field_path": "review.open_issues",
                    "value": {
                        "check": "核对交付物路径与材料引用是否一致。",
                        "evidence_location": "deliverables[0].path",
                    },
                    "confidence": 0.55,
                    "rationale": "路径一致性是评审的机械检查项。",
                    "evidence": ["demo:review-1"],
                }
            ]
        },
    }

    def __init__(self, fail: Optional[str] = None) -> None:
        self.fail = fail
        self.name = "mock"
        self.is_mock = True

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: Optional[Mapping[str, Any]] = None,
        capability: str = "",
        prompt_version: str = "",
        temperature: float = 0.0,
    ) -> ModelResponse:
        if self.fail == "timeout":
            raise ProviderTimeoutError("模拟超时（MockProvider）")
        if self.fail == "rate_limit":
            raise ProviderRateLimitError("模拟限流（MockProvider）", retry_after=0.0)
        if self.fail == "server":
            raise ProviderServerError("模拟模型服务不可用（MockProvider）")
        if capability not in self._PAYLOADS:
            raise ProviderRequestError("MockProvider 不支持能力: %s" % capability)

        if self.fail == "malformed":
            text = "Sure! Here is the JSON you asked for:\n```json\n{}\n```"
        else:
            payload = json.loads(json.dumps(self._PAYLOADS[capability]))
            suggestion = payload["suggestions"][0]
            if self.fail == "unknown_field":
                suggestion["action"] = "submit"
            elif self.fail == "missing_field":
                suggestion.pop("evidence", None)
            text = json.dumps(payload, ensure_ascii=False, sort_keys=True)

        tokens_in = max(1, (len(system_prompt) + len(user_prompt)) // 4)
        tokens_out = max(1, len(text) // 4)
        return ModelResponse(
            text=text,
            model="mock-deterministic",
            model_version="mock-deterministic-v1",
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=1,
            attempts=1,
            finish_reason="stop",
        )
