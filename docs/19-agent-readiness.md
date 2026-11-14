# 第五波：真实模型接入与试点准入

这份文件记录 ALE 500 第五波在真实模型接入、密钥隔离、成本状态、备份路径、演示账号门禁和专家试点准入方面的实现与验证。它不改变 500 条目标、配额、批次或已批准的阶段基线。

## 1. 范围与结论

第五波不重建 Docker、PostgreSQL、FastAPI、Worker 或 P12 主链。工作集中在现有的 `platform/agent/` Gateway、`compose.yaml`、种子脚本、备份脚本和专家试点材料。

当前结论分为三句。

- 真实 Provider 的配置注入路径已经具备，密钥不会进入 Git、镜像、日志或业务数据库。
- 真实模型尚未调用。没有真实 API Key，因此没有 `LIVE_PASS`，也不能把 Mock 结果写成真实质量。
- 专家 T1 材料可以先行准备；T2 平台辅助必须在真实模型和对应功能验收后启动。

## 2. 安全与部署修复

这一节记录第五波修掉的四类问题。每条都说明改动位置和可复核的证据。

### 2.1 备份不再默认写入 Git 跟踪目录

`tools/wave4/backup.sh` 的默认输出改为 `work/backups/w4-<时间戳>/`。`work/` 已被 Git 忽略。脚本设置 `umask 077`，包含 PostgreSQL custom dump、对象目录、包目录、计数文件和 SHA-256 清单。显式把输出指向 `docs/` 时脚本只给警告，不替使用者判断内容是否敏感。

`tools/wave4/restore_drill.sh` 默认读取 `work/backups/` 下最新的 `w4-*`，也可显式传入备份目录。找不到 `db.dump` 时直接报错退出，不会静默使用空库。

仓库中原有的 `docs/evidence/w4/backup/db.dump` 已移到 `work/backups/`，`docs/evidence/w4/backup/SHA256SUMS` 不再列出该文件。仓库只保留历史计数和校验和，不保留数据库转储。

### 2.2 演示账号只在本地或显式允许时创建

`platform/seed.py` 增加 `demo_seed_allowed(env)`。只有 `ALE_ENV=local` 或 `ALE_ALLOW_DEMO_SEED` 为真时才创建六个演示账号；否则 `seed()` 在打开数据库前抛出 `RuntimeError`。

`platform/web/app.py` 的启动引导只在允许时自动 seed，非本地环境只记录 warning。`platform/manage.py seed` 保留显式 `--allow-demo`，供本地测试使用。

### 2.3 专家材料与当前许可、PII、Agent 功能一致

`docs/20-expert-pilot-handbook.md` 已按当前界面的实际上传字段改写。许可类型为五选一；`synthetic` 只用于合成资料；`proprietary` 和 `internal` 默认不可再分发；可再分发默认“否”；PII 当前只提供 `none`、`low`、`medium`，高危 PII 阻断且界面不提供 `high`。

Agent 段落改为统一 Gateway、默认 Mock、五项能力都可选、真实模型取决于项目配置。审核辅助只提供检查项和证据位置，不替评审做结论。材料中不写内部费用、单价、补贴或付款条件。

### 2.4 成本状态不再把未知计价写成零成本

`platform/agent/gateway.py` 为每次运行记录 `cost_status`。

- Mock 运行：`not_applicable`。
- 非 Mock 且没有配置输入或输出单价：`unknown`。
- 配置了任一单价：`estimated`。

`cost_cents` 仍保留整数，但页面和报告显示状态，不能把 `0` 解释为真实零成本。数据库 `agent_runs.cost_status` 默认 `unknown`，旧库由 `ensure_agent_run_columns` 补列，避免重复迁移。

## 3. 真实 Provider 配置与密钥隔离

`compose.yaml` 通过 Docker secret 把 `model_api_key` 挂载到 `web` 和 `worker` 的 `/run/secrets/model_api_key`。`ALE_MODEL_PROVIDER`、`ALE_MODEL_BASE_URL`、`ALE_MODEL_ID`、`ALE_MODEL_STRUCTURED_OUTPUT`、`ALE_MODEL_PROMPT_VERSION` 从环境注入，密钥文件路径固定为容器内 secret。

本机实测：`docker compose -p ale500 build web` 后运行一次性容器，secret 在容器内为 `0o600`、uid/gid 10001、非 root 进程可读。Compose 对 `uid/gid/mode` 给出“outside Swarm mode ignored”警告，但实际挂载权限正确。`platform/agent/config.py` 也允许 `/run/secrets/` 下 root 拥有的 `0444`，兼容默认 Docker secret 权限。

真实密钥用 `tools/wave5/setup_model_secret.sh --from-file <受保护文件>` 安装到 `.secrets/model_api_key`，文件权限为 0600。脚本不打印密钥内容。`.secrets/` 被 Git 忽略，只有 `README.md` 进入版本库。

密钥仍缺失时，Compose 保持 Mock。调用前 `agent_service` 会检查任务权限、评审分配、字段允许范围和 reference 过滤；模型失败返回降级提示，专家可以继续人工填写。

## 4. 真实模型校准

校准入口是 `tools/wave5/agent_calibration.py`，输入是 `tools/wave5/calibration-task.json`，输出是 `docs/evidence/w5/agent-calibration.json`。

当前报告状态为 `MOCK_FLOW_ONLY`。

- 访谈、追问、结构化、预检、审核辅助五项能力都返回了合法建议。
- 每条建议都有 `field_path`、`value`、`confidence`、`rationale` 和 `evidence`。
- 建议路径落在 Canonical 任务源的合法前缀内。
- 校准任务里的 `reference` 资料在送入模型前被移除，报告记录 `reference_removed_before_prompt=true`。
- 超时、限流、服务不可用三类故障都返回降级提示和人工清单，没有建议写入。
- Markdown 包裹、未知字段、缺少证据三类坏输出都被 Gateway 拒绝。

报告明确 `live_pass=false`。原因不是接口失败，而是没有真实 Provider 调用，也没有独立专家对专业真实性、误报和漏报做裁决。要形成 `LIVE_PASS`，至少需要以下输入和证据。

- 真实 `base_url`、精确 `model_id`、受保护的 API Key。
- 允许容器出站 HTTPS 的网络环境。
- 供应商对 `response_format=json_schema` 或 `json_object` 的兼容性确认。
- 五项能力各一组真实请求，保留模型、Prompt 版本、耗时、Token、结构化输出和错误。
- 专家对建议逐条确认，并记录接受、修改后接受、拒绝和人工修改理由。
- 预检的误报和漏报样本，以及专业事实错误的复核结论。

没有这些证据时，报告只称流程兼容，不称真实 Agent 通过。

## 5. T1 与 T2 试点准入

T1 人工基线可以在平台外先行准备。`docs/20-expert-pilot-handbook.md` 提供专家操作手册，`docs/21-expert-pilot-materials.md` 提供项目说明、原创示范任务、两条不合格示例、专业审核清单、T1 记录模板、T2 记录模板和反馈表。T1 与 T2 使用同一题族的不同实例，间隔至少三个工作日。

T2 平台辅助不能以 Mock 代替真实 Agent 效果。启动 T2 前至少需要完成以下事项。

- 真实模型连通、认证和结构化输出通过。
- 五项能力在真实任务上完成质量校准，专家逐字段确认。
- 专家操作手册按实际页面复核，未实现按钮不写成可用。
- 试点资料授权、发送给模型服务商的数据范围、保留期限和删除方式得到书面确认。
- 三个试点方向的专家、任务族和排期冻结。

当前 T2 状态是“平台流程可演练，真实模型效果未验收”。这不等于 T2 可以启动。

## 6. P12 与持续集成

当前本地测试为 `77 passed`，其中平台测试 38 项、Agent 测试 39 项。CI 还运行哈希 PoC、验证合同自检、P12 固定样本复核和 Agent 校准。

`tools/wave3/verify_package.py` 已加入 CI 固定样本。CI 使用第四波导出的包和回执，重算 `native_hash` 与 `package_hash`，检查 `files[]`、`PACKAGE.json` 位置、路径穿越和 Agent 视图隔离。

`tools/wave5/independent_package_check.py` 是第二份哈希实现。它不导入 `platform.contracts.package_contract`，按同一份书面规则重算固定样本，用来防止平台实现和自测一起漂移。两份实现都得到同一组固定哈希，结果保存在 `docs/evidence/w5/independent-hash-check.json`。

固定样本的包哈希与回执哈希一致，Agent 视图不含 `reference/`、`PACKAGE.json` 和元数据边车。CI 中也保留哈希 PoC、验证合同自检、平台测试和 Agent 测试。

## 7. Docker 与持久化

第五波没有重建或清空 `ale500` 数据。Docker Desktop 29.9.3、Compose 5.7.0、context `desktop-linux`，`ale500-db-1`、`ale500-web-1`、`ale500-worker-1` 仍在运行，Web 为 `127.0.0.1:8088`，PostgreSQL 不发布宿主机端口。

重启数据库、Web 和 Worker 后 `/healthz` 返回 `{"status":"ok","backend":"postgresql"}`，任务、包和入库计数保持不变。备份恢复演练在隔离容器和独立数据库中完成，没有覆盖运行中的 `ale500`。

## 8. 仍未完成

- 真实模型没有调用，没有 `LIVE_PASS`。
- T2 没有启动，专家也没有在真实模型上做质量校准。
- 自动检查仍有五项是 info skip，不能冒充 PASS。
- 备份恢复脚本尚未加入 CI 的容器化回归。
- 大文件分片上传、S3/MinIO、PostgreSQL 在线迁移和云部署未实现。
- 生成式 Agent 的专业事实正确性、引用正确性和预检漏报率没有历史基线。

## 9. 需要项目负责人提供或决定

- Provider 名称、`base_url`、精确 `model_id` 和密钥交付方式。
- 哪些资料允许发送给该 Provider，是否需要额外数据授权。
- 真实模型调用预算、并发和超时上限。
- T2 试点是否可以在真实模型未完成专家校准前做流程演练。
- 是否开放专家 BYOK，还是继续由项目统一配置。
