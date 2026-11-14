# 第三波实施记录：可运行工作台与 ALE-data 生产链

这份文件记录第三波从合同与骨架推进到真实可运行平台的结果。范围是专家 Web 工作台、P12 包合同验证、两个验收节点的实际证据，以及仍未完成的部分。所有结论来自本次运行记录，不把设计稿当成已实现。

## 1. 目标与结论

第三波的目标不是再写一份设计，而是让专家能在一个真实 Web 界面里完成任务源、资料、检查、提交、返修和审核，并让审核通过的任务走完冻结、组包、L1–L5、幂等入库和独立复核。

本轮达到的状态。

- 真实 FastAPI + Jinja2 工作台可以启动，使用 SQLite、PBKDF2 口令、签名会话、CSRF 和任务级权限。
- 浏览器完整走通专家提交、领域评审退回、专家重提、领域通过、质量通过、冻结、组包、校验、入库。
- 实际产物是一个包含三个 base 文件的 ALE-data overlay，包哈希与入库回执可被独立脚本复算。
- 平台仍不是 ALE 运行器，也不实现正式评分器；运行框架、Harbor 转换和 Verifier 执行不在本轮范围。

## 2. 架构决策

选择 FastAPI + Jinja2 服务端渲染 + SQLite 本地库，复用第二波的 `platform/app/domain`、`repo`、`contracts`。

理由。

- 业务层已经是 sqlite3 连接和纯函数，FastAPI 只增加 HTTP、会话、模板，改动面最小。
- Django 需要重写现有 ORM 与仓储层，本轮没有收益。
- Dify 和 LangGraph 不进入 P1 关键路径；Agent 先走统一 Python 接口，保留替换能力。
- PostgreSQL、S3、外部后台队列作为目标 profile，不在本轮假装已实现。

当前边界。

- SQLite 用于本地验收；并发写、备份恢复和 PostgreSQL 迁移仍未做真实测试。
- 对象存储是本地内容寻址目录，不是 S3。
- 后台任务同步执行，没有独立 worker。
- 没有 TLS 终止、反向代理和正式部署清单。

## 3. 真实工作台

已实现的页面与动作。

- 登录与退出，六个演示账号，PBKDF2-SHA256 240,000 次，签名 cookie 八小时。
- 专家工作台、新建任务、任务详情、结构化任务源表单、保存草稿、运行检查、提交审核。
- 资料上传，记录文件名、大小、SHA-256、角色、层、许可和 PII 级别。
- 领域评审与质量审核队列、领取、通过、退回、问题项记录。
- 冻结快照、自动组包、L1–L5 校验、幂等入库。
- Agent 建议面板，建议只写 `agent_suggestions`，专家接受、编辑或拒绝后才可能进入任务源。

专家不直接编辑 JSON，不看到 `PACKAGE.json`，不接触 Dockerfile、Verifier 或包哈希。

## 4. P12 包合同

包布局。

```text
packages/<domain_code>/<task_slug>/<version>/
  PACKAGE.json
  SHA256SUMS
  package_manifest.json
  materials.json
  provenance.json
  handoff.json
  validation_report.json
  receipt.json
  base/
    input/
    software/
    reference/
```

`PACKAGE.json` 在版本层，不在 `base/` 内。被评 Agent 只看到 `base/input` 和 `base/software`，看不到 `base/reference`、`PACKAGE.json`、校验报告和回执。

哈希候选合同。

- `native_hash` 覆盖 `base/` 内容文件的规范清单，每项是 path、bytes、mode、role、sha256，按 path 排序；排除 `PACKAGE.json`、`validation_report.json`、`SHA256SUMS` 和哈希字段。
- `package_hash` 覆盖 `native_hash`、`PACKAGE.json` 稳定投影、四个版本级边车哈希；稳定投影排除 `built_at`、`built_by`、`hashes`、`package_hash`；边车排除 `validation_report.json`。
- 入库回执哈希覆盖 `package_hash`、`validation_report` 哈希、接收时间和接收人，只写数据库与 `receipt.json`，不回写包内。
- `package_hash` 不写进 `PACKAGE.json`，避免自引用。
- 七项哈希 PoC 在第二波已通过；本轮的独立脚本再次从目录重算并与回执比对。

L1–L5 校验。

- L1 结构：目录、`PACKAGE.json`、入口文件、路径安全。
- L2 语义：版本、domain、task_id、`PACKAGE.json` 与任务一致。
- L3 完整性：`files[]` 覆盖 base、逐文件哈希、native 与 package 哈希复算。
- L4 安全：许可、PII、reference 泄漏、`PACKAGE.json` 不在 base。
- L5 入库：同任务同版本不同哈希的冲突隔离。

## 5. 节点一证据

浏览器实际完成的动作。

1. 专家登录，新建任务 `business_finance/e2e_reconcile_01`。
2. 填写身份、场景、三个操作步骤、一个交付物、一个成功标准、风险理由和已知缺口。
3. 保存草稿，上传 `M-001`，文件为 `ledger.csv`，30 字节。
4. 运行检查通过，提交审核，版本为 v1。
5. 领域评审领取，退回并记录一条 blocker。
6. 专家修改第三步的预期状态，保存并重提，版本为 v2。
7. 领域评审通过，质量审核通过，任务进入 approved。
8. 管理员冻结、组包、校验、入库，任务进入 ingested。

运行数据。

- 第一轮领域评审：`rev_bf14230c6fe149c1b1cf`，returned。
- 第二轮领域评审：`rev_6d487b5913304821aba4`，passed。
- 质量审核：`rev_72ebd1f4244e43358ed7`，passed。
- 版本：v1 哈希 `ef8294574979…`，v2 哈希 `fda685eb60c4…`。
- 截图记录在 `docs/evidence/w3/01-node1-submitted.png`。

## 6. 节点二证据

实际包。

- 任务：`business_finance/e2e_reconcile_01`，版本 2。
- 包：`pkg_a8820f17d95c491ea689`，状态 ingested。
- 包内文件：`input/ledger.csv`、`input/output_contract.json`、`input/task_brief.md`。
- `native_hash`：`9ccf186eec70f9db5cb7dfd25c541ae5574e55d7dec92e4cf4a580d19bb16252`。
- `package_hash`：`ff48e73e5697c37a972543461f60e1c86011744ca3a5dfcf1b8956d2ef2c346f`。
- 入库回执：`ing_9f8b9081990e48baba1b`，状态 published，接收时间 2026-11-14T09:17:32Z。
- 回执记录 `validation_report_sha256`，与数据库和包内报告一致。

独立复核。

`tools/wave3/verify_package.py` 不读数据库，只读包目录和回执期望值。它重算每个文件的哈希、`native_hash` 和 `package_hash`，并检查 `PACKAGE.json` 不在 base、`files[]` 与 base 一致、路径不是绝对路径。

实际输出记录在 `docs/evidence/w3/independent-verification.json`，六项检查全部为 true，`ok` 为 true。

截图记录在 `docs/evidence/w3/02-node2-ingested.png`。

## 7. 安全与权限

已实现。

- 任务读取不只看角色。领域评审只有存在自己领取记录时才能读任务；专家只能读写自己的任务，管理员按权限读取。
- 所有状态变更走状态机，非法跳步被拒绝。
- 提交生成不可变 `task_versions`，冻结生成不可变 `snapshots`，数据库触发器阻止覆盖。
- 上传文件按内容哈希存储，路径穿越被拒绝。
- 包校验会拒绝 `base/PACKAGE.json`、reference 泄漏到 Agent 视图、绝对路径和哈希错配。
- 审计事件追加写，记录操作者、动作、对象、前后状态和时间。

尚未完成。

- 正式外部访问所需的 TLS、反向代理、密钥托管和多因素认证。
- PostgreSQL 下的并发事务、行锁、迁移和备份恢复。
- 对象存储的并发上传、断点续传和清理策略。
- 管理员的用户生命周期管理和权限变更审批。

## 8. 已实现与未实现

已实现。

- 真实 Web 登录、任务创建、任务源编辑、草稿保存、资料上传、自动检查、提交、评审、返修、审核、冻结、组包、校验、入库。
- Canonical v1 的 41 个核心必填字段校验，以及材料存在性和哈希校验。
- 四类自动检查有真实实现；其余五类以 info skip 明确标记，不伪装为通过。
- 包哈希候选合同、L1–L5、幂等入库、独立复核脚本。
- 20 项平台单元与集成测试，其中 6 项交付与哈希测试。

未实现。

- 九项自动检查中仍有五项是占位跳过：重复与相似、环境与软件依赖、包预检、lint、必要冒烟。
- Agent 建议目前是规则式占位，不调用真实模型；五项能力只做了结构化建议和逐字段确认。
- 版本差异对比页面、批量操作、导出、管理统计报表。
- PostgreSQL、S3、后台队列、正式部署。
- 参考包和中文路径的端到端组包测试；当前只覆盖单文件 CSV 和本地路径。

## 9. 距专家试用与完整生产链的差距

距专家试用。

- 需要真实 TLS、正式账号发放、密码重置、权限变更流程。
- 需要把规则式 Agent 建议替换为可评测的模型接口，并保留人工确认。
- 需要按真实界面写试点操作手册，避免手册描述不存在的按钮。
- 需要准备示范任务、不合格示例、审核清单和培训反馈表。

距完整 ALE-data 生产链。

- 需要补五项自动检查，尤其是重复相似、环境依赖和包预检。
- 需要用含 reference、不同文件类型、中文路径和官方命名 variant 的包做回归。
- 需要 PostgreSQL 迁移与备份恢复的真实演练。
- 需要把独立复核脚本纳入 CI，并固定一份样例包作为回归基线。
- 需要明确 `package_hash` 是否最终写入导出回执之外的第三方清单。

## 10. 下一任务与需要裁决的事项

下一个可自主执行的任务。

1. 把 `tools/wave3/verify_package.py` 接入 CI，生成一个最小样例包并验证六项检查。
2. 补五项自动检查中可确定性实现的部分：包预检、环境清单、lint。
3. 用含 reference 的任务做一次完整组包与 Agent 视图回归，证明 reference 不泄漏。
4. 补 PostgreSQL 迁移脚本和备份恢复测试，保留 SQLite 作为本地开发 profile。

需要项目负责人裁决。

- 是否允许把规则式 Agent 建议作为试点版本，还是必须等真实模型接入。
- 专家试点是否接受当前本地部署形态，还是必须先有正式 TLS 与账号流程。
- `package_hash` 的最终公开位置，只放回执与数据库，还是额外导出到第三方清单。
- 是否把中文路径和官方命名 variant 的兼容测试列为进入试点的硬门槛。

## 11. 版本记录

- v0.1，2026-11-14：第三波实施记录。记录真实工作台、P12 候选合同、两个验收节点、已实现与未实现、差距和待裁决事项。
