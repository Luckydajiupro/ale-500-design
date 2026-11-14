"""Configuration and secret loading for the model gateway.

Two sources are supported, with environment variables overriding TOML:

1. a TOML file with a ``[model]`` table (see ``config.example.toml``);
2. ``ALE_MODEL_*`` environment variables.

The API key is *never* a configuration field. It is read lazily from the
environment variable named by ``api_key_env`` or from a permission-restricted
secret file, so a ``ModelConfig`` object, its repr and its audit record cannot
leak it. Secret errors are redacted before they leave this module.

Python 3.9 note: ``tomllib`` only exists from 3.11. The loader prefers
``tomllib``, then ``tomli`` when installed, then a small flat-TOML parser that
covers this module's scalar-only config file.
"""

from __future__ import annotations

import json
import os
import re
import stat
from collections.abc import Mapping as ABCMapping
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from .redaction import redact_text

try:  # Python 3.11+
    import tomllib as _toml  # type: ignore
except ImportError:  # pragma: no cover - exercised on Python 3.9/3.10
    try:
        import tomli as _toml  # type: ignore
    except ImportError:  # pragma: no cover
        _toml = None


PROVIDERS = ("mock", "openai_compatible")
STRUCTURED_OUTPUT_MODES = ("json_schema", "json_object", "none")

_ENV_FIELDS: Dict[str, str] = {
    "provider": "ALE_MODEL_PROVIDER",
    "base_url": "ALE_MODEL_BASE_URL",
    "model_id": "ALE_MODEL_ID",
    "api_key_env": "ALE_MODEL_API_KEY_ENV",
    "secret_file": "ALE_MODEL_SECRET_FILE",
    "timeout": "ALE_MODEL_TIMEOUT",
    "max_retries": "ALE_MODEL_MAX_RETRIES",
    "max_output_tokens": "ALE_MODEL_MAX_OUTPUT_TOKENS",
    "structured_output": "ALE_MODEL_STRUCTURED_OUTPUT",
    "stream": "ALE_MODEL_STREAM",
    "rate_limit_per_min": "ALE_MODEL_RATE_LIMIT_PER_MIN",
    "prompt_version": "ALE_MODEL_PROMPT_VERSION",
    "input_cents_per_1k": "ALE_MODEL_INPUT_CENTS_PER_1K",
    "output_cents_per_1k": "ALE_MODEL_OUTPUT_CENTS_PER_1K",
    "max_input_chars": "ALE_MODEL_MAX_INPUT_CHARS",
}

_TRUTHY = frozenset({"1", "true", "yes", "on"})
_FALSY = frozenset({"0", "false", "no", "off", ""})
_ENV_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class ConfigError(ValueError):
    """Invalid gateway configuration. Never carries a credential value."""


class SecretError(ConfigError):
    """The API key is missing, malformed or stored with unsafe permissions."""


@dataclass(frozen=True)
class ModelConfig:
    """Validated, credential-free gateway configuration."""

    provider: str = "mock"
    base_url: str = ""
    model_id: str = "mock-deterministic"
    api_key_env: str = "ALE_MODEL_API_KEY"
    secret_file: str = ""
    timeout: float = 30.0
    max_retries: int = 2
    max_output_tokens: int = 2048
    structured_output: str = "none"
    stream: bool = False
    rate_limit_per_min: int = 60
    prompt_version: str = "agent-v1"
    # Pricing is configuration, not a claim about a live provider. Zero means
    # "not configured"; the gateway records cost_status=unknown, not a real zero.
    input_cents_per_1k: float = 0.0
    output_cents_per_1k: float = 0.0
    max_input_chars: int = 20000

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider", str(self.provider).strip().lower())
        object.__setattr__(
            self, "structured_output", str(self.structured_output).strip().lower()
        )
        object.__setattr__(self, "api_key_env", str(self.api_key_env).strip())
        object.__setattr__(self, "prompt_version", str(self.prompt_version).strip())

        if self.provider not in PROVIDERS:
            raise ConfigError(
                "provider 必须是 %s 之一，收到 %r"
                % (" / ".join(PROVIDERS), self.provider)
            )
        if self.structured_output not in STRUCTURED_OUTPUT_MODES:
            raise ConfigError(
                "structured_output 必须是 %s 之一，收到 %r"
                % (" / ".join(STRUCTURED_OUTPUT_MODES), self.structured_output)
            )
        if not self.api_key_env or not _ENV_NAME_RE.match(self.api_key_env):
            raise ConfigError("api_key_env 必须是合法的环境变量名")
        if not self.prompt_version:
            raise ConfigError("prompt_version 不能为空")
        if not isinstance(self.timeout, (int, float)) or self.timeout <= 0:
            raise ConfigError("timeout 必须为正数")
        if not isinstance(self.max_retries, int) or not 0 <= self.max_retries <= 10:
            raise ConfigError("max_retries 必须在 0 到 10 之间")
        if not isinstance(self.max_output_tokens, int) or not 1 <= self.max_output_tokens <= 131072:
            raise ConfigError("max_output_tokens 必须在 1 到 131072 之间")
        if not isinstance(self.rate_limit_per_min, int) or not 1 <= self.rate_limit_per_min <= 100000:
            raise ConfigError("rate_limit_per_min 必须在 1 到 100000 之间")
        if not isinstance(self.max_input_chars, int) or not 1000 <= self.max_input_chars <= 1000000:
            raise ConfigError("max_input_chars 必须在 1000 到 1000000 之间")
        if not isinstance(self.stream, bool):
            raise ConfigError("stream 必须是布尔值")
        if self.input_cents_per_1k < 0 or self.output_cents_per_1k < 0:
            raise ConfigError("计价不能为负数")
        if self.provider == "openai_compatible":
            if not self.base_url.startswith(("https://", "http://")):
                raise ConfigError("openai_compatible 需要 http(s) base_url")
            if not self.model_id.strip():
                raise ConfigError("openai_compatible 需要 model_id")

    def public_dict(self) -> Dict[str, Any]:
        """A log-safe view; the secret file path has its home prefix removed."""

        data = asdict(self)
        data["secret_file"] = redact_text(data["secret_file"])
        return data


# ---------------------------------------------------------------------------
# Minimal TOML reader (fallback for Python 3.9 without tomli)
# ---------------------------------------------------------------------------


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_double:
            escaped = True
            continue
        if char == '"' and not in_single:
            in_double = not in_double
        elif char == "'" and not in_double:
            in_single = not in_single
        elif char == "#" and not in_single and not in_double:
            return line[:index]
    return line


def _parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if not raw:
        raise ConfigError("TOML 配置值为空")
    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        try:
            return json.loads(raw)
        except ValueError as exc:
            raise ConfigError("TOML 字符串无法解析") from exc
    if raw.startswith("'") and raw.endswith("'") and len(raw) >= 2:
        return raw[1:-1]
    if raw in ("true", "false"):
        return raw == "true"
    try:
        return int(raw, 10)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    raise ConfigError("TOML 仅支持字符串、数字、布尔等标量值: %r" % raw[:40])


def _parse_simple_toml(text: str) -> Dict[str, Dict[str, Any]]:
    """Flat ``[section]`` + ``key = scalar`` parser for the config file."""

    document: Dict[str, Dict[str, Any]] = {}
    current = "model"
    document[current] = {}
    for line_number, original in enumerate(text.splitlines(), start=1):
        line = _strip_comment(original).strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            if not section or "." in section:
                raise ConfigError("TOML 第 %d 行的 section 不受支持" % line_number)
            current = section
            document.setdefault(current, {})
            continue
        if "=" not in line:
            raise ConfigError("TOML 第 %d 行缺少 = 号" % line_number)
        key, raw = line.split("=", 1)
        key = key.strip()
        if not key or not re.match(r"^[A-Za-z_][A-Za-z0-9_-]*$", key):
            raise ConfigError("TOML 第 %d 行的键名非法" % line_number)
        if key in document[current]:
            raise ConfigError("TOML 第 %d 行重复键 %s" % (line_number, key))
        document[current][key] = _parse_scalar(raw)
    return document


def _read_toml(path: Path) -> Dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError("无法读取配置文件: %s" % redact_text(str(path))) from exc

    if _toml is not None:
        try:
            parsed = _toml.loads(text)
        except Exception as exc:  # tomllib/tomli use different exception types
            raise ConfigError("TOML 解析失败: %s" % redact_text(str(exc))) from exc
    else:
        parsed = _parse_simple_toml(text)

    if not isinstance(parsed, ABCMapping):
        raise ConfigError("TOML 顶层必须是表")
    section = parsed.get("model")
    if isinstance(section, ABCMapping):
        return dict(section)
    # Allow a deliberately flat file, but not arbitrary sections.
    if any(isinstance(value, ABCMapping) for value in parsed.values()):
        raise ConfigError("配置文件必须使用 [model] 表")
    return dict(parsed)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def _coerce(name: str, raw: Any) -> Any:
    if name in ("timeout", "input_cents_per_1k", "output_cents_per_1k"):
        try:
            return float(raw)
        except (TypeError, ValueError) as exc:
            raise ConfigError("%s 必须是数字" % name) from exc
    if name in ("max_retries", "max_output_tokens", "rate_limit_per_min", "max_input_chars"):
        if isinstance(raw, bool):
            raise ConfigError("%s 必须是整数" % name)
        try:
            return int(raw)
        except (TypeError, ValueError) as exc:
            raise ConfigError("%s 必须是整数" % name) from exc
    if name == "stream":
        if isinstance(raw, bool):
            return raw
        value = str(raw).strip().lower()
        if value in _TRUTHY:
            return True
        if value in _FALSY:
            return False
        raise ConfigError("stream 必须是布尔值")
    return str(raw)


def _from_mapping(data: Mapping[str, Any]) -> ModelConfig:
    known = {field.name for field in fields(ModelConfig)}
    unknown = sorted(set(data) - known)
    if unknown:
        raise ConfigError("未知配置项: %s" % ", ".join(unknown))
    values = {key: _coerce(key, value) for key, value in data.items()}
    return ModelConfig(**values)


def load_config(
    path: Optional[os.PathLike[str]] = None,
    env: Optional[Mapping[str, str]] = None,
) -> ModelConfig:
    """Load configuration from TOML and environment variables.

    Environment variables override the file. When ``path`` is omitted,
    ``ALE_AGENT_CONFIG`` selects the file; without either, only defaults and
    environment variables are used (the default provider is ``mock``).
    """

    environment = os.environ if env is None else env
    resolved: Dict[str, Any] = {}

    config_path = path
    if config_path is None:
        configured = environment.get("ALE_AGENT_CONFIG", "").strip()
        config_path = configured or None

    if config_path is not None:
        resolved.update(_read_toml(Path(config_path)))

    for name, env_name in _ENV_FIELDS.items():
        raw = environment.get(env_name)
        if raw is not None:
            resolved[name] = raw

    return _from_mapping(resolved)


CONTAINER_SECRET_ROOT = "/run/secrets"


def _secret_permissions_ok(mode: int, path_text: str) -> bool:
    """0600 on the host; Docker file secrets are root-owned 0444 by design."""

    if not mode & 0o077:
        return True
    normalized = str(Path(path_text))
    return normalized.startswith(CONTAINER_SECRET_ROOT + "/") and mode == 0o444


def _read_secret_file(path_text: str) -> str:
    path = Path(path_text).expanduser()
    safe_path = redact_text(str(path))
    try:
        link_stat = path.lstat()
    except OSError as exc:
        raise SecretError("secret_file 不可读: %s" % safe_path) from exc

    if stat.S_ISLNK(link_stat.st_mode):
        raise SecretError("secret_file 不能是符号链接: %s" % safe_path)
    if not stat.S_ISREG(link_stat.st_mode):
        raise SecretError("secret_file 必须是普通文件: %s" % safe_path)
    if not _secret_permissions_ok(stat.S_IMODE(link_stat.st_mode), str(path)):
        raise SecretError(
            "secret_file 权限过宽，必须仅属主可读写（0600）: %s" % safe_path
        )
    if link_stat.st_size <= 0 or link_stat.st_size > 4096:
        raise SecretError("secret_file 大小必须在 1 到 4096 字节之间: %s" % safe_path)

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(str(path), flags)
    except OSError as exc:
        raise SecretError("secret_file 无法打开: %s" % safe_path) from exc
    try:
        opened = os.fstat(fd)
        if not _secret_permissions_ok(stat.S_IMODE(opened.st_mode), str(path)):
            raise SecretError(
                "secret_file 权限过宽，必须仅属主可读写（0600）: %s" % safe_path
            )
        with os.fdopen(fd, "r", encoding="utf-8", closefd=False) as handle:
            value = handle.read()
    except UnicodeDecodeError as exc:
        raise SecretError("secret_file 不是 UTF-8 文本: %s" % safe_path) from exc
    finally:
        os.close(fd)

    value = value.strip()
    if not value:
        raise SecretError("secret_file 内容为空: %s" % safe_path)
    if "\n" in value or "\r" in value:
        raise SecretError("secret_file 只能包含一行密钥: %s" % safe_path)
    return value


def load_api_key(
    config: ModelConfig,
    env: Optional[Mapping[str, str]] = None,
    require: bool = True,
) -> Optional[str]:
    """Resolve the API key from the configured env var or secret file.

    The returned value is never logged by this package. Errors contain only the
    env variable name or a home-redacted file path.
    """

    environment = os.environ if env is None else env
    raw = environment.get(config.api_key_env, "")
    key = raw.strip() if isinstance(raw, str) else ""
    if key:
        if len(key) < 8 or any(char.isspace() for char in key):
            raise SecretError(
                "环境变量 %s 中的密钥格式无效（至少 8 个字符且不含空白）"
                % config.api_key_env
            )
        return key

    if config.secret_file:
        value = _read_secret_file(config.secret_file)
        if len(value) < 8 or any(char.isspace() for char in value):
            raise SecretError("secret_file 中的密钥格式无效（至少 8 个字符且不含空白）")
        return value

    if require:
        raise SecretError(
            "未配置模型密钥：请设置环境变量 %s，或配置权限为 0600 的 secret_file"
            % config.api_key_env
        )
    return None
