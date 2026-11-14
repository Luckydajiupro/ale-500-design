# 第四波：本地集成平台与 P12 生产链

这份文件记录 ALE 500 第四波在 Mac Docker Desktop 上完成的本地集成环境、真实 PostgreSQL 适配、后台 Worker、模型 Agent Gateway、P12 包合同加固和浏览器验收证据。它是实现记录，不是研究报告，也不改变 500 条目标、配额、批次和阶段基线。

## 1. 范围与结论

第四波把第三波的 SQLite 演示工作台升级为可以重复启动的本地集成环境。当前实现包括：

- FastAPI 服务端渲染工作台，真实登录、CSRF、任务级权限、任务源编辑、资料上传、检查、提交、领域评审、质量审核、返修、冻结、组包、L1–L5 校验和幂等入库。
- PostgreSQL 16 作为本地集成数据库，SQLite 继续作为开发与测试后端。
- Docker Compose project `ale500`，包含 `db`、`migrate`、`web`、`worker` 四个服务，Web 只绑定 `127.0.0.1:8088`。
- 独立 Worker 处理 `package.build`、`package.validate`、`package.ingest` 三类后台任务。
- 模型 Agent Gateway、五项能力入口、逐字段人工确认和审计记录；当前默认 `mock` provider，未做真实模型调用。
- P12 候选包合同：版本层 `PACKAGE.json`、四个边车、内容哈希、包哈希、入库回执和独立复核脚本。
- 本地备份脚本与隔离恢复演练。
- 专家试点手册和材料，按实际页面写明可用与不可用功能。

第四波的结论是：本地集成环境可以运行，PostgreSQL 事务和浏览器全链可以通过；P12 合同仍是候选，真实模型质量、真实外部专家试用、云部署和 1,000 条规模验证尚未完成。

## 2. 本地环境实测

| 项目 | 实测值 | 性质 |
|---|---|---|
| 主机架构 | arm64 | 实测 |
| 内存 | 32 GB | 实测 |
| 可用磁盘 | 约 1.6 TiB | 实测 |
| Docker Desktop | 29.9.3 | 实测 |
| Docker Compose | v5.7.0 | 实测 |
| Docker context | `desktop-linux` | 实测 |
| Python | 3.9.6 | 实测 |
| uv | 0.13.7 | 实测 |
| PostgreSQL | 16-alpine 容器 | 实测 |
| Web 端口 | `127.0.0.1:8088` | 实测 |

Dify 容器占用 443、8080、5003 端口和 `docker-*` 资源。ALE 500 使用独立 project `ale500`、独立网络 `ale500_net` 和独立卷 `ale500_pgdata`、`ale500_objects`、`ale500_packages`、`ale500_runtime`，没有复用或删除 Dify 的资源。

本机 Docker 构建需要把 `DOCKER_CONFIG` 指向可写目录。当前使用 `/tmp/ale-docker-config`，其中包含 `config.json`、`contexts/`、`buildx/` 和 `cli-plugins` 软链。该目录是本地构建的临时绕行，不进入仓库。

## 3. 技术选型

| 层 | 选择 | 理由 |
|---|---|---|
| Web | FastAPI + Jinja2 服务端渲染 | 现有业务层是 sqlite3 连接和纯函数，FastAPI 只增加 HTTP、会话和模板 |
| 数据库 | PostgreSQL 16，SQLite 开发后备 | 本地集成使用真实 PG，测试保留轻量 SQLite |
| 迁移 | 手写 SQL + `schema_migrations` | 现有 DDL 与方言差异可控，不引入 ORM |
| 存储 | 本地卷内容寻址 | P1 不依赖云对象存储，保留 S3 适配接口 |
| 后台任务 | PostgreSQL `jobs` 表 + 独立 Worker | 不引入 Celery/Redis，满足状态、重试、超时和重启恢复 |
| Agent | 统一 Python Gateway + Provider Adapter | 可替换 provider，不把 Dify/LangGraph 设为 P1 必需依赖 |
| 部署 | Docker Compose | 本机可重复启动，保留 Linux 云迁移路径 |
| 容器安全 | 非 root 用户 `ale`（uid 10001）、Web 仅绑 `127.0.0.1`、PostgreSQL 不发布宿主机端口 | 降低本地演示的权限面，容器重建不改变数据卷 |

Django、FastAPI、Dify、LangGraph 之中，本波只对 Django 与 FastAPI 做了小范围比较，最终选择 FastAPI。Dify 和 LangGraph 没有进入 P1 关键路径。

## 4. 一键启动

本地集成环境的启动顺序：

```bash
# Mock 模式也必须有一个占位 secret 文件，Compose 才能挂载
printf '%s' 'mock-placeholder-key' > .secrets/model_api_key
chmod 600 .secrets/model_api_key
docker compose -p ale500 up -d db
docker compose -p ale500 run --rm migrate
docker compose -p ale500 up -d web worker
curl http://127.0.0.1:8088/healthz
```

真实密钥用 `tools/wave5/setup_model_secret.sh --from-file <受保护文件>` 安装到 `.secrets/model_api_key`，不要把密钥写进 `.env`、Compose 文件或镜像。

当前健康检查返回：

```json
{"status":"ok","backend":"postgresql"}
```

演示账号由 `platform/seed.py` 幂等创建，默认密码为 `AleDemo123!`。账号包括专家、第二专家、领域评审、质量审核、管理员和项目负责人。种子密码可由 `ALE_SEED_PASSWORD` 覆盖。Compose 显式设置 `ALE_ENV=local` 和 `ALE_ALLOW_DEMO_SEED=1`；非本地环境不设置这两个变量时，启动不会自动创建演示账号，生产环境也不得使用默认密码。

`.env.example` 只包含本地开发占位值，不包含真实密钥。`ALE_MODEL_API_KEY` 不写入仓库、镜像、构建参数、Prompt、日志或测试夹具。

## 5. PostgreSQL 适配

`platform/app/pg.py` 用 psycopg3 包装连接，统一把 `?` 占位符翻译为 `%s`，并把 JSONB 返回值规范化为业务层可读的 JSON 字符串。`platform/app/db.py` 支持 SQLite 路径和 `postgresql://` URL，事务层在 PostgreSQL 下使用 `pg_advisory_xact_lock(500500)`，在 SQLite 下继续使用 `BEGIN IMMEDIATE`。

已处理的方言差异包括：

- `INSERT OR REPLACE` 改为 `INSERT ... ON CONFLICT ... DO UPDATE`。
- `rowid` 排序改为显式时间与主键排序。
- JSONB 列在写入时序列化，在读取时规范化。
- 时间戳统一为 TEXT，避免 SQLite 与 PostgreSQL 的时区类型差异。
- 追加写表使用触发器拒绝 UPDATE 和 DELETE。

`platform/pg/schema.sql` 与 `platform/pg/migrations/001_init.sql` 保存完整模式，`platform/manage.py` 提供 `migrate`、`seed` 和 `check`。迁移容器实测输出：

```text
migrations applied: 001_init.sql, 002_package_state_ingested.sql
```

`manage.py check` 实测输出：

```text
backend: postgresql users: 6 tasks: 0 packages: 0
```

## 6. 存储、包与后台任务

资料对象存放在内容寻址的本地卷中，路径为 `sha256/ab/cd/<digest>`。同一个文件重复上传不会覆盖旧版本，资料版本表保留哈希、字节数、许可和 PII 级别。上传请求限制 20 MiB；大文件分片是后续扩展，不在本波实现。

组包异步模式由 `ALE_ASYNC_PACKAGE=1` 开启。Web 只把 `package.build` 写入 `jobs`，Worker 用管理员 principal 执行组包。Worker 支持 `--loop` 和 `--once`，任务状态、重试次数、最后错误和结果都写入数据库。

实测后台任务：

```text
job_ef842c27bb064dc89e98  package.build  succeeded  0
```

该任务在任务已经入库后重复入队，Worker 走幂等返回，没有重复写包。之前两次失败是因为任务状态不是 `frozen`；修复后，已有包在 `built`、`validated`、`ingested` 状态会先返回，不再被状态门拦住。

## 7. P12 候选包合同

当前包布局：

```text
packages/<task_id>/<version>/
  PACKAGE.json
  package_manifest.json
  materials.json
  provenance.json
  handoff.json
  validation_report.json
  SHA256SUMS
  base/input/
  base/reference/
```

`PACKAGE.json` 放在版本层，不放进 `base/`。被评 Agent 的视图只复制 `base/input` 和 `base/software`，不包含 `base/reference`、`PACKAGE.json`、四个边车、校验报告和入库回执。

当前候选哈希规则：

- `native_hash` 覆盖 `base/` 内容文件的规范清单，字段为 path、bytes、mode、role、sha256。
- `package_hash` 覆盖 `native_hash`、`PACKAGE.json` 的稳定投影、四个边车哈希；排除 `built_at`、`built_by`、`hashes` 和 `package_hash` 自身。
- 入库回执哈希覆盖 `package_hash`、校验报告哈希、接收时间与接收人，只写数据库和回执，不写回包内。

这些规则仍是候选，不是冻结标准。当前 `PACKAGE.json` 的 schema 版本为 `ale-pkg-1.2-draft`。正式冻结需要覆盖更多文件类型、异常中断、并发组包和跨机器重建。

## 8. 浏览器验收

第四波使用 Playwright 在真实浏览器中走完专家与审核流程。演示任务为 `business_finance/pg_e2e_04`，真实 PostgreSQL 存储。流程包括：

1. 专家登录、新建任务、填写三步操作、交付物、成功标准和风险理由。
2. 上传 `M-001` 输入资料和 `M-002` reference 资料。
3. 生成结构化 Agent 建议，专家接受 `deliverables[0].format="xlsx"`。
4. 运行自动检查、提交审核。
5. 领域评审退回 blocker，专家修改第三步并重提为第 2 版。
6. 领域评审通过，质量审核通过。
7. 管理员冻结、组包、L1–L5 校验、幂等入库。

实测结果：

| 项目 | 值 |
|---|---|
| 任务 | `business_finance/pg_e2e_04` |
| 冻结快照 | `snap_6c3aa22c4641458294ba` |
| 包 | `pkg_de57d995499f446cb551` |
| 回执 | `ing_779136cf78c0416a973e` |
| native_hash | `1e7cb980c4d65770718da46ce8df6f1c9a8c6bf7493fc0ffb33d20c07f125c0a` |
| package_hash | `790705df2942ea00bdeea5a0546a8d63251c99760570c53a009bb34c97e59932` |
| 包内文件 | 4 个，含 `reference/answer.csv` |
| 入库状态 | `ingested` / `published` |

截图在 `docs/evidence/w4/screens/`，从 `01-dashboard.png` 到 `14-ingested.png`。浏览器实际页面页脚显示“本地集成环境。所有操作写入真实 PostgreSQL 数据库与审计日志”。

## 9. Agent Gateway

`platform/agent/` 提供 provider 适配、Gateway、结构化输出 schema、密钥配置、脱敏和 39 项单元测试。当前默认 provider 为 `mock`，模型为 `mock-deterministic`，`mock_only=1`。这不是真实模型调用，不能计为真实 Agent 质量通过。

Web 接入层在 `platform/app/domain/agent_service.py`。它先做任务权限检查，`review_assist` 只允许分配给该任务的评审；再把 reference 资料从 payload 中移除；然后调用 Gateway；最后把 `agent_runs` 和 `agent_suggestions` 写入数据库。专家接受、编辑后接受或拒绝，才会修改草稿。

实测记录：

```text
run_617eb3676c3043589cb9b3135acb436a  structuring  mock:mock-deterministic
status=success  mock_only=1  prompt_version=agent-v1  tokens_in=969  tokens_out=40
```

建议记录：

```text
deliverables[0].format  "xlsx"  accepted  u_expert
```

真实模型还缺四项外部输入：供应商精确 `base_url` 和 `model_id`、`ALE_MODEL_API_KEY` 或 0600 secret 文件、允许出站 HTTPS 的运行环境、供应商对 `response_format=json_schema` 的兼容性确认。拿到这些输入后才能做真实请求、质量、延迟、Token 和费用记录。

## 10. 安全与权限

本波补的安全点：

- 任务详情、编辑、资料上传、组包、校验和入库都校验任务 owner 或 `task:read:all`。
- 评审读取必须存在分配给当前用户的 review 记录，不能只凭角色读取任意任务。
- Agent 调用前移除 reference 资料；`review_assist` 只允许对应评审。
- `PACKAGE.json` 默认版本层，被评 Agent 不可见。
- 上传资料必须选择许可类型，许可再分发默认 false，PII 只允许 none/low/medium。
- 组包元数据从任务源和资料登记推导，缺失或不一致直接失败，不使用 demo 默认值。
- 包目录存在时拒绝覆盖，不静默删除。
- 已提交版本和冻结快照由追加写触发器保护。
- 包内路径拒绝绝对路径和 `..`。

HTTP 权限测试覆盖匿名读取跳登录、其他专家读取私有任务返回 403、未分配评审读取私有任务返回 403、owner 读取返回 200。四项均通过。

## 11. 备份与恢复

`tools/wave4/backup.sh` 默认把 PostgreSQL custom dump、对象目录、包目录、计数文件和 SHA-256 清单写到 `work/backups/w4-<时间戳>/`。`work/` 已被 Git 忽略，数据库转储不会进入仓库。需要生成可提交的证据时，显式传入 `docs/evidence/` 下的路径，并自行确认其中不含敏感数据。`docs/evidence/w4/backup/` 只保留历史计数与文件校验和，数据库转储已从 Git 移除。历史备份的计数为：

```text
tasks=2
packages=1
ingests=1
```

`tools/wave4/restore_drill.sh` 启动独立的 `postgres:16-alpine` 容器，创建 `ale500_restore` 数据库，执行 `pg_restore`，再用只读文件卷启动一个临时 Web 容器，检查 `/healthz` 和三类计数。恢复环境与运行中的 `ale500` 容器、数据库、卷分离。

恢复演练通过，计数与备份一致。恢复脚本默认读取 `work/backups/` 下最新的 `w4-*` 目录，也可显式传入备份路径。备份不依赖运行中的容器或卷。

## 12. 独立复核

`tools/wave3/verify_package.py` 不读平台数据库，只读包目录和回执。它重算 `native_hash` 和 `package_hash`，核对 `files[]`、绝对路径、路径穿越、`PACKAGE.json` 位置，以及 Agent 视图是否包含 reference 或元数据边车。

当前复核结果：

```text
agent_view_no_metadata_sidecar true
agent_view_no_package_json true
agent_view_no_reference true
files_list_matches_base true
native_hash_matches_manifest true
native_hash_matches_receipt true
no_absolute_paths true
no_declared_path_traversal true
package_hash_matches_receipt true
package_json_not_under_base true
ok true
```

证据在 `docs/evidence/w4/independent-verification.json`。包、回执和 Agent 视图分别在 `docs/evidence/w4/package/`、`docs/evidence/w4/receipt.json` 和 `docs/evidence/w4/agent-view/`。

## 13. 测试与检查

本地测试：

```bash
PYTHONPATH=platform .venv/bin/python -m pytest platform/tests platform/agent/tests -q
```

第四波提交时为 `70 passed`；第五波加入成本状态、演示账号门禁和校准测试后为 `77 passed`。平台测试覆盖交付链、哈希、篡改、路径穿越、追加写、Unicode 路径、HTTP 权限、种子门禁和成本状态；Agent 测试覆盖 provider、Gateway、结构化输出、超时、限流和脱敏。

公开检查器仍通过：`check_docs.py`、`check_numbers.py`、阶段 2 自检、试点自检、s0 校验和、s1 校验器。CI 增加平台测试命令。

## 14. 未完成与真实边界

以下项目尚未完成，不能写成生产通过：

- 真实模型调用、真实质量评估、Token/费用记录和五项能力的真实稳定性。
- 真实外部专家试用、真实客户资料、许可与 PII 的人工审核。
- 云服务器部署、TLS、域名、对象存储、外部备份和 AMD64 镜像。
- 1,000 条规模的压力、并发、长任务和故障注入。
- 正式运行的 Verifier、Harbor 转换、容器构建和评分。
- 大于 20 MiB 的资料分片上传。
- 自动检查中的重复检测、完整环境/软件清单和专业语义检查。
- 真实 PostgreSQL 的部分方言边界（大对象、复杂锁、连接池）和长时间恢复演练。

当前可以演示的是本地真实 PostgreSQL 环境下的专家工作台、审核返修、P12 组包校验入库和独立复核。它不能被描述为公网可用的生产平台。

## 15. 云迁移条件

迁移到 Linux 云服务器前需要确认：

- AMD64 镜像构建与 Buildx 验证。
- TLS 终止、反向代理、会话密钥和密钥管理。
- 托管 PostgreSQL 或带备份的 PostgreSQL 服务。
- 对象存储与生命周期策略，替代本地卷。
- 外部模型 provider 的出站网络、配额、超时和数据边界。
- 备份恢复演练在云环境重跑，不能只验证本地容器。
- 权限、审计和日志的集中收集。

## 16. 下一步

1. 用用户提供的真实模型配置完成 `LIVE_PASS` 或明确的失败报告。
2. 把 P12 候选合同覆盖到中文路径、异常中断、并发组包和跨机器重建。
3. 补自动检查中的环境/软件清单、重复检测和包预检。
4. 在真实浏览器中验证领域评审、质量审核和返修的负例。
5. 用一条含 reference 的合成任务完成备份、恢复、独立复核和回执的完整证据链。
6. 校对 `docs/20-expert-pilot-handbook.md` 与当前页面的差异，删除未实现功能的操作描述。

## 17. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v0.1 | 2026-11-14 | 第四波本地集成环境、PostgreSQL、Worker、Agent Gateway、P12 加固与验收证据初稿 |
