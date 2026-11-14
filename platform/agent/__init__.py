"""ALE Agent model gateway (provider-agnostic, offline-testable).

Public surface::

    from agent import AgentGateway, MockProvider, load_config

    gateway = AgentGateway(MockProvider())
    result = gateway.generate("precheck", task)

Nothing here is wired into the Web app or the database yet. The gateway only
returns suggestions plus an audit-ready run record.
"""

from .config import (
    ConfigError,
    ModelConfig,
    SecretError,
    load_api_key,
    load_config,
)
from .gateway import (
    AgentError,
    AgentGateway,
    AgentInputError,
    AgentResult,
    AgentRun,
    AgentUnavailableError,
    build_prompts,
    canonical_json,
    fallback_for,
    input_hash,
    parse_model_json,
)
from .provider import (
    MockProvider,
    ModelProvider,
    ModelResponse,
    OpenAICompatibleProvider,
    ProviderAuthError,
    ProviderError,
    ProviderOutputError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderServerError,
    ProviderTimeoutError,
)
from .redaction import REDACTED, redact_text, redact_value, safe_exception_message
from .schemas import (
    CAPABILITIES,
    OutputContractError,
    output_schema,
    path_is_canonical,
    validate_output,
)

__all__ = [
    "AgentError",
    "AgentGateway",
    "AgentInputError",
    "AgentResult",
    "AgentRun",
    "AgentUnavailableError",
    "CAPABILITIES",
    "ConfigError",
    "MockProvider",
    "ModelConfig",
    "ModelProvider",
    "ModelResponse",
    "OpenAICompatibleProvider",
    "OutputContractError",
    "ProviderAuthError",
    "ProviderError",
    "ProviderOutputError",
    "ProviderRateLimitError",
    "ProviderRequestError",
    "ProviderServerError",
    "ProviderTimeoutError",
    "REDACTED",
    "SecretError",
    "build_prompts",
    "canonical_json",
    "fallback_for",
    "input_hash",
    "load_api_key",
    "load_config",
    "output_schema",
    "parse_model_json",
    "path_is_canonical",
    "redact_text",
    "redact_value",
    "safe_exception_message",
    "validate_output",
]
