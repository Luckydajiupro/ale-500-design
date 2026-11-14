# ALE Agent 模型网关（platform/agent）

把原来的规则式 Agent 占位能力升级为**可配置、可测试、可审计**的模型网关。它只负责"调用模型 → 校验输出 → 返回建议 + 运行记录"，**不接 Web、不写数据库、不改任务源**；集成由主会话完成。

```text
platform/agent/
├── __init__.py
├── config.py            # TOML / 环境变量配置、密钥加载
├── config.example.toml  # 配置模板（敏感值为空）
├── gateway.py           # 五项能力、prompt、校验、AgentResult / AgentRun
├── provider.py          # ModelProvider 协议、OpenAI-compatible、Mock
├── redaction.py         # 日志/错误脱敏
├── schemas.py           # 五项能力的严格 JSON Schema + Canonical 路径校验
├── README.md
└── tests/test_agent_gateway.py
```

## 1. 配置

复制模板到私有位置，**不要把密钥写进 TOML**：

```bash
cp platform/agent/config.example.toml ~/.config/ale/agent.toml
chmod 600 ~/.config/ale/agent.toml
export ALE_AGENT_CONFIG=~/.config/ale/agent.toml
```

关键字段（`[model]` 表）：

| 字段 | 默认 | 说明 |
| --- | --- | --- |
| `provider` | `mock` | `mock` 或 `openai_compatible` |
| `base_url` | 空 | OpenAI-compatible API 根地址，不含 `/chat/completions` |
| `model_id` | `mock-deterministic` | 供应商的精确模型 id |
| `api_key_env` | `ALE_MODEL_API_KEY` | 保存密钥的环境变量名（不是密钥本身） |
| `secret_file` | 空 | 可选的 0600 单行密钥文件；与 env 二选一 |
| `timeout` | `30.0` | 单次 HTTP 超时（秒） |
| `max_retries` | `2` | 429/5xx/超时/网络错误的重试次数 |
| `max_output_tokens` | `2048` | 传给供应商的 `max_tokens` |
| `structured_output` | `none` | `json_schema` / `json_object` / `none` |
| `stream` | `false` | SSE 流式解析 |
| `rate_limit_per_min` | `60` | 客户端滑动窗口限流 |
| `prompt_version` | `agent-v1` | 写入运行记录；改 prompt 模板时递增 |
| `input_cents_per_1k` | `0.0` | 输入计价；0 表示未配置 |
| `output_cents_per_1k` | `0.0` | 输出计价；0 表示未配置 |
| `max_input_chars` | `20000` | 调用前拒绝过长的 user prompt |

环境变量覆盖：`ALE_MODEL_PROVIDER`、`ALE_MODEL_BASE_URL`、`ALE_MODEL_ID`、`ALE_MODEL_API_KEY_ENV`、`ALE_MODEL_SECRET_FILE`、`ALE_MODEL_TIMEOUT`、`ALE_MODEL_MAX_RETRIES`、`ALE_MODEL_MAX_OUTPUT_TOKENS`、`ALE_MODEL_STRUCTURED_OUTPUT`、`ALE_MODEL_STREAM`、`ALE_MODEL_RATE_LIMIT_PER_MIN`、`ALE_MODEL_PROMPT_VERSION`、`ALE_MODEL_INPUT_CENTS_PER_1K`、`ALE_MODEL_OUTPUT_CENTS_PER_1K`、`ALE_MODEL_MAX_INPUT_CHARS`。

密钥只从两处读取：

1. `api_key_env` 指向的环境变量（默认 `ALE_MODEL_API_KEY`）；
2. `secret_file`：必须是普通文件、非符号链接、权限 `0600`、1–4096 字节、单行 UTF-8。

密钥不会进入 `ModelConfig`、`repr`、异常、日志、prompt 或运行记录。`config.public_dict()` 只暴露脱敏后的路径。

## 2. 真实调用前置条件

以下条件全部满足，才建议把 `provider` 从 `mock` 切到 `openai_compatible`：

1. `base_url` 是真实可访问的 OpenAI-compatible 根地址（例如供应商文档给出的 `https://.../v1`），网关会追加 `/chat/completions`；
2. `model_id` 是供应商当前可用的精确 id；
3. 通过 `ALE_MODEL_API_KEY` 或 0600 secret 文件提供密钥；
4. 运行环境允许出站 HTTPS，且 `timeout` / `rate_limit_per_min` 与供应商配额匹配；
5. 若 `structured_output = "json_schema"`，供应商必须支持 `response_format.type=json_schema`；否则用 `json_object` 或 `none`。**无论哪种模式，网关都会本地严格校验**；
6. 需要成本记录时填写 `input_cents_per_1k` / `output_cents_per_1k`；未填写时 `cost_cents=0`，这不代表调用免费；
7. 修改 prompt 模板后递增 `prompt_version`，否则审计记录无法区分模板版本。

## 3. 五项能力

| 能力 | 用途 | `value` 形状 |
| --- | --- | --- |
| `interview` | 生成访谈问题 | `{question, why}`，`field_path` 只能是块级 |
| `followup` | 追问 / 补全缺口 | 字段的建议值 |
| `structuring` | 自由文本 → Canonical 字段 | 字段的建议值 |
| `precheck` | 提交前机械预检 | `{finding, severity}`，severity 为 `blocker/warning/info` |
| `review_assist` | 评审检查项与证据位置 | `{check, evidence_location}` |

每条建议只允许 `field_path`、`value`、`confidence`、`rationale`、`evidence` 五个字段。`field_path` 必须是 `schemas/canonical-task-source.schema.json` 的合法路径前缀，且**禁止** `verification` / `package`（平台派生块）。顶层/嵌套出现 `action`、`decision`、`verdict`、`submit`、`approve`、`freeze`、`ingest`、`publish` 等动作字段，或出现"提交任务/冻结快照/执行入库"等动作短语，都会被拒绝。

网关**不会**提交、审核、批准、冻结、组包、入库或替评审下结论；这些动作不在输出契约里。

## 4. 输出与运行记录

成功时返回 `AgentResult`：

```python
{
  "capability": "precheck",
  "suggestions": [...],
  "run": {
    "run_id": "run_...",
    "capability": "precheck",
    "model": "...",
    "model_version": "...",
    "prompt_version": "agent-v1",
    "prompt_hash": "<sha256>",
    "input_hash": "<sha256>",
    "latency_ms": 123,
    "tokens_in": 100,
    "tokens_out": 40,
    "cost_cents": 0,
    "status": "success",
    "error_code": null,
    "attempts": 1,
    "mock_only": true,
    "degraded": false
  },
  "fallback": null,
  "mock_only": true
}
```

`input_hash` 由 `{capability, task, context}` 的排序 JSON 计算，字典顺序无关、跨进程稳定；`prompt_hash` 由 system + user prompt 计算。`mock_only=true` 表示本次结果来自 `MockProvider`，不是真实模型。

## 5. 失败降级

| 场景 | 错误码 | 行为 |
| --- | --- | --- |
| 超时 | `PROVIDER_TIMEOUT` | 可重试；耗尽后 `AgentUnavailableError` |
| 429 | `PROVIDER_RATE_LIMITED` | 按 `Retry-After`/指数退避重试 |
| 5xx / 网络 | `PROVIDER_UNAVAILABLE` | 可重试 |
| 401/403 | `PROVIDER_AUTH_FAILED` | 不重试，直接降级 |
| 400/404/422 | `PROVIDER_REQUEST_INVALID` | 不重试，直接降级 |
| 模型输出非法 | `OUTPUT_*` | 抛 `OutputContractError`，拒绝写入任何建议 |
| 其他内部错误 | `AGENT_INTERNAL_ERROR` | 降级 |

`AgentGateway.generate(..., raise_on_error=True)`（默认）在模型故障时抛 `AgentUnavailableError`，异常携带：

- `error_code`、`retryable`、`degradable=True`；
- 失败的 `run` 记录（`status="error"`）；
- `fallback`：人工清单 + 模板 + "模型暂不可用"提示。

`raise_on_error=False` 时返回降级的 `AgentResult`（`suggestions=[]`、`run.degraded=true`、带 `fallback`），Web 可据此显示"暂时不可用"，继续用模板/人工清单。

**模型输出非法不会降级为"半条建议"**：`OutputContractError` 直接抛出，因为任何未校验文本都不能进入建议表。

## 6. 用 Mock 跑测试 / 离线演示

```bash
PYTHONPATH=platform .venv/bin/python -m pytest platform/agent/tests -q
```

或直接演示：

```python
from agent import AgentGateway, MockProvider

gateway = AgentGateway(MockProvider())
result = gateway.generate("precheck", task)   # task 为 Canonical 任务 dict
print(result.to_dict())
```

`MockProvider` 对五项能力返回确定性 JSON，覆盖真实的解析与校验路径；`fail=` 可注入 `timeout` / `rate_limit` / `server` / `malformed` / `unknown_field` / `missing_field` 故障。测试还用 `httpx.MockTransport` 覆盖 429 重试、超时重试、认证失败、SSE 流式、密钥不泄漏。

依赖：Python 3.9+、`httpx`、`jsonschema`（均已在 `platform/requirements*.txt`）。TOML 读取优先 `tomllib`（3.11+）/ `tomli`，两者都没有时使用内置的标量 TOML 解析器。

## 7. 真实调用验证状态

**当前状态：`mock_only`。没有对任何真实模型做过调用验证，也没有 `LIVE_PASS`。**

已验证（离线）：

- 五项能力的 Mock 正常路径与严格输出契约；
- 非法 JSON、Markdown 包裹、未知/缺失字段、平台派生块路径、越权动作拒绝；
- 429 / 超时重试与耗尽、认证失败不重试；
- 密钥不进入错误、日志、prompt；
- 输入 hash 稳定、建议字段合法、降级错误可捕获；
- `httpx.MockTransport` 下的 SSE 流式解析。

**尚未真实调用验证：**

- 五项能力在任一真实供应商上的质量与稳定性；
- 真实 `response_format=json_schema` 的供应商兼容性（部分供应商只支持 `json_object`）；
- 真实 token 计量、计价与 `cost_cents`；
- 真实流式响应的分块边界、`usage` 是否随流返回；
- 真实供应商的 429 `Retry-After` 语义与配额；
- 真实 `model_version`（目前记录供应商返回的 `model` 字段，不保证是不可变版本号）。

在完成上述验证并把结果写入独立报告之前，请保持 `provider = "mock"`，不要声称 `LIVE_PASS`。

## 8. 集成边界

本目录**没有**修改 `platform/app`、`platform/web`、`platform/contracts`、`tools`、`inputs` 或文档。主会话集成时需要：

1. 在调用点构造 `ModelConfig` / provider / `AgentGateway`；
2. 把 `result.suggestions` 写入 `agent_suggestions`，把 `result.run` 写入 `agent_runs`（字段已对齐现有表）；
3. 捕获 `AgentUnavailableError` 与 `OutputContractError`，按第 5 节降级；
4. 保持能力开关与成本上限；本网关只执行客户端限流，不做预算持久化。
