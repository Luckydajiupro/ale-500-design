# ALE 专家工作台

这份文件说明 `platform/` 下的专家工作台。它可以在 SQLite 开发模式运行，也可以在 Mac Docker Desktop 的 Compose 集成环境运行。它不是公网生产部署。

## 启动

开发模式使用 SQLite：

```bash
python3 -m venv .venv
.venv/bin/pip install -r platform/requirements.txt
ALE_ENV=local ALE_DB_PATH=$PWD/platform/var/platform.db PYTHONPATH=platform .venv/bin/python platform/run.py
```

打开 `http://127.0.0.1:8000`。本地环境首次启动会建库并写入演示账号；`ALE_ENV` 不是 `local` 时必须显式设置 `ALE_ALLOW_DEMO_SEED=1`，否则不会创建演示账号。

本地集成模式使用 Docker Compose。先准备一个 secret 文件，Mock 模式也需要占位文件才能挂载：

```bash
mkdir -p .secrets
printf '%s' 'mock-placeholder-key' > .secrets/model_api_key
chmod 600 .secrets/model_api_key
docker compose -p ale500 up -d db
docker compose -p ale500 run --rm migrate
docker compose -p ale500 up -d web worker
```

打开 `http://127.0.0.1:8088`，健康检查为 `/healthz`。Web 只绑定本机回环地址，PostgreSQL 不发布宿主机端口。

演示账号的密码统一为 `AleDemo123!`：

| 邮箱 | 角色 |
| --- | --- |
| `expert@ale.local` | 专家（商业会计） |
| `expert2@ale.local` | 专家（工程） |
| `reviewer@ale.local` | 领域评审 |
| `quality@ale.local` | 质量审核 |
| `admin@ale.local` | 平台管理员 |
| `lead@ale.local` | 项目负责人 |

## 已实现的业务动线

专家可以登录、新建任务、编辑结构化任务源、保存草稿、上传资料、运行自动检查、生成并逐条确认 Agent 建议、提交评审。领域评审核验后，质量审核通过；管理员冻结快照、自动组包、运行 L1–L5 校验、幂等入库。

任务源是 Canonical v1 JSON，但专家只看到表单和摘要，不直接改 JSON。Agent 建议写入 `agent_suggestions`，只有专家确认后才写回 `tasks.draft_payload`。

## 存储与数据库

SQLite 开发模式由 `ALE_DB_PATH` 控制，默认 `platform/var/platform.db`。Compose 模式由 `ALE_DB_URL` 指向 PostgreSQL，迁移在 `platform/pg/migrations/`。两种后端共用 domain 与 repo，JSONB 和 SQLite 文本 JSON 由连接层规范化。

文件内容寻址存储在 `ALE_STORAGE_ROOT`，默认 `platform/var/objects`。包输出在 `ALE_PACKAGE_ROOT`，默认 `platform/var/packages`。后台任务写入 PostgreSQL `jobs` 表，由 `platform/worker.py` 消费。

## 安全边界

- 密码使用 PBKDF2-SHA256，会话 cookie 使用 itsdangerous 签名，CSRF 令牌逐表单校验。
- 任务读取校验 owner、`task:read:all` 或实际评审领取记录，不只看角色。
- 上传文件有大小上限，包内路径拒绝绝对路径和 `..`。
- `PACKAGE.json` 在版本层，不在 `base/`，被评 Agent 不可见。
- 这是本地演示配置，cookie 未设 `Secure`。正式外部访问必须启用 HTTPS、`Secure` cookie、生产密钥管理和 PostgreSQL。

## Agent Gateway

Agent 默认使用 `mock` provider，不能计为真实模型质量。Compose 通过 `ALE_MODEL_PROVIDER`、`ALE_MODEL_BASE_URL`、`ALE_MODEL_ID`、`ALE_MODEL_STRUCTURED_OUTPUT` 注入配置；密钥不进入 `.env`、Compose 文件、镜像、日志或数据库，而是由只读 secret 挂载到 `/run/secrets/model_api_key`，容器内非 root 进程 uid 10001 读取。真实密钥用 `tools/wave5/setup_model_secret.sh --from-file <受保护文件>` 安装；未配置真实密钥时保持 `mock`，不得标记 `LIVE_PASS`。成本未配置计价时记录 `cost_status=unknown`，不把零成本当成真实计量。示例配置在 `platform/agent/config.example.toml`。

五项能力入口在任务详情页。建议先写入 `agent_suggestions`，专家确认后才写回草稿。`review_assist` 只允许分配给该任务的评审使用。

## 测试

```bash
PYTHONPATH=platform .venv/bin/python -m pytest platform/tests platform/agent/tests -q
PYTHONPATH=platform .venv/bin/python -m unittest discover -s platform/tests -v
```
