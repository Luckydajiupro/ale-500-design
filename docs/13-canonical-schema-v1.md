# 13 Canonical Schema 与 ALE-data 包合同 v1

这份文件定义 ALE 500 第二波 A 线的第一版规范任务源字段、官方任务身份映射、平台包 overlay 与候选哈希规则。它服务平台组包、专家表单、审核记录和工程交接的共同数据形状。它不把尚未通过 PoC 的哈希或包布局写成冻结合同。

## 13.1 结论与边界

第一版只冻结五组核心字段，共 41 个必填叶子。身份、资料、交付物、成功标准和环境这五组进入 v1；场景、步骤、审核、来源、交接、验证描述和包元数据仍按草案管理。字段注册表共有 112 个字段，冻结范围小于注册表，避免在官方案例证据不足时锁死全部形状。

平台包是官方 `task-data-v1.1` variant 布局之上的 overlay，不是官方包的原生格式。官方 122 个任务没有包级 `PACKAGE.json`，只有零散的 `reference_manifest.json`、`stage1_manifest.json`、`output_contract.json`、`answer_key.json` 等任务自定文件。平台新增的 `PACKAGE.json` 必须说明自己是 overlay，并保留官方 `source_task_id` 与 `source_variant`。

哈希合同目前是候选 `candidate-v1`。P12 PoC 通过前，文档、数据库和入库回执只能把它标成候选。`package_hash` 的推荐存放位置是数据库与入库回执，不写回被哈希的包内文件。`native_hash` 可以随包分发，用于同源重建比对。

## 13.2 字段模型

字段注册表在 `docs/data/wave2-field-registry.csv`，共 112 行。五个核心块如下。

| 块 | 目的 | v1 状态 | 主要字段 |
| --- | --- | --- | --- |
| identity | 任务是谁、属于哪个域、来自哪里 | 冻结 | task_id、task_version、domain_code、subdomain_code、title、summary、language、source_task_id、source_variant |
| materials | 专家提交哪些资料、许可与哈希 | 冻结 | materials[].path、role、sha256、bytes、license、pii、source |
| deliverables | 被评 Agent 要交什么 | 冻结 | deliverables[].path、kind、description、required |
| success_criteria | 什么算成功、怎样给分 | 冻结 | criteria[].id、weight、verification_mode、oracle_required、tolerance、hard_gates |
| environment | 运行环境意图 | 冻结 | os、gui、network、software、external_services、gpu |

未冻结的块包括 `scenario`、`operations`、`review`、`provenance`、`handoff`、`verification`、`package`。它们已有字段定义和示例，但允许在首批 30 条生产中调整枚举和必填条件。

`schemas/canonical-task-source.schema.json` 是机器可读形状。它要求五个核心块存在，并校验 41 个必填叶子。数组块 `materials`、`operations`、`deliverables`、`success_criteria` 使用数组定义，不要求固定长度。

字段来源分三类。`expert` 表示专家在任务源中填写；`platform` 表示平台从快照、批次或审核记录派生；`derived` 表示组包或校验时计算。`identity.task_version` 与 `identity.owner_expert_id` 由平台写入，专家不可改。

## 13.3 任务身份与版本

规范任务身份用 `<domain_code>/<task_slug>`。`domain_code` 取 13 个官方域加 `unknown`；`task_slug` 使用小写字母、数字、下划线和连字符。官方原始 `task_id` 可能带 `finance/`、`machine_learning/`、`business_finance/` 等各类前缀，因此平台保留 `source_task_id` 原值，不把它当规范主键。

`source_variant` 保留官方 variant 名。官方 122 个任务中 100 个 variant 名为 `base`，22 个是命名 variant，例如 `tsla_fy2023`、`variant_1`、`137`、`ptbxl_2263`。平台新任务统一使用 `base`，官方导入任务保留原 variant，不强行改名为 `base`。

`task_version` 从 1 开始，每次专家提交形成不可变版本。草稿修改不增加版本；提交、审核退回后的再次提交增加版本。冻结快照绑定 `task_id + task_version`。包目录使用 `<task_id>/<task_version>/`，不与官方 `<task>/<variant>/` 混用。

官方 `published_tasks.json` 有 122 条，119 个任务目录名与发布清单一致。三个 variant 名不一致：`other/mota_exploration`、`visual_media/uv_reproduction`、`visual_media/skeletal_animation_reproduction`。导入时以目录名为准，把发布清单差异写入 `import_notes`，不修改官方文件。

## 13.4 官方 variant 兼容矩阵

兼容矩阵在 `docs/data/wave2-official-compat.csv`，逐任务记录 `has_base`、`has_software`、`has_reference`、`import_mode`、`identity_rule`、`blockers` 和 `test_case`。导入模式五值如下。

| import_mode | 条件 | 处理 |
| --- | --- | --- |
| direct_base | 有 base、有 input、有 reference、无阻塞 | 直接按官方 variant 导入，补 overlay 元数据 |
| staged_base | 有 base，但缺 software 或 reference | 先进入暂存区，补边车或人工确认后再入库 |
| direct_named | 命名 variant，内容完整 | 保留 source_variant，按命名 variant 导入 |
| staged_named | 命名 variant，缺文件或有阻塞 | 暂存，人工确认 variant 身份与缺件 |
| external_ref | 单包超过 5 GiB 或有不可搬运资产 | 只登记 external_ref，不复制大资产 |

阻塞码包括 `NO_SOFTWARE`、`NO_BRIEF`、`NO_REFERENCE`、`LARGE_ASSET`、`SYMLINK_RUNTIME_ENV`。16 个任务没有 `software/`，2 个 engineering 任务没有 `reference/`，`cailian_road_highway_alignment_2` 和 `inner_support_elevation_optimization` 属于后者。`software/` 为空是合法状态，L1 只校验声明存在的角色路径。

官方入口文档至少八种文件名，`task_prompt.md` 14 次、`README.md` 12 次、`task_brief.md` 11 次、`TASK_PROMPT.md` 8 次、`problem_spec.md` 7 次。overlay 的 `entrypoints.brief` 必须指向实际文件，不假设统一文件名。

## 13.5 平台包 overlay

推荐布局如下。`base/` 只放官方内容角色，`PACKAGE.json` 与四个边车放在版本层，默认对 Agent 不可见。

```text
packages/<domain_code>/<task_slug>/<task_version>/
  base/
    input/
    software/
    reference/
  PACKAGE.json
  package_manifest.json
  materials.json
  provenance.json
  handoff.json
  validation_report.json
  SHA256SUMS
```

`PACKAGE.json` 的候选 schema 在 `schemas/ale-package.schema.json`。它要求 `schema_version`、`ale_data_version`、`task_id`、`task_version`、域与子域、标题与摘要、入口、交付物、oracle、验证、环境意图、沙箱、许可、PII、来源、文件清单、哈希和包身份。`files[]` 每项带 `path`、`sha256`、`bytes`、`mode`、`role`、`visibility`。`mode` 保留四位八进制，执行位不丢。

`oracle.required=false` 是合法状态，用于无唯一参考解、rubric 或视觉参考族。此时必须有 `approved_without_reference=true` 与 `approval_ref`。官方两个无 reference 的 engineering 任务属于这一类，不能因为缺 reference 直接判为不合格。

`license` 采用 `type + status + scope_exception`。`type` 六值 public_domain、cc_by、cc_by_nc、proprietary、internal、synthetic；`status` 三态 cleared、pending、restricted。`pending` 不得入库为可计数包；`restricted` 可入库但 `counted_in_500=false` 并带 `scope_exception`。官方资料没有统一许可字段，导入时必须补来源与许可证据。

`PACKAGE.json` 若留在 `base/` 内，需要 L4 agent 视图测试。测试必须确认 Agent 看不到 reference 内容、答案键、评分依据、`PACKAGE.json` 的 reference 清单和敏感元数据。测试未通过时，包不得进入 `frozen`。

## 13.6 候选哈希与 PoC

`tools/wave2/hash_poc.py` 用标准库实现候选规则，结果在 `docs/data/wave2-hash-poc-results.csv`，7 项全部通过。规则分三层。

`native_hash` 覆盖 `base/` 内容文件的规范清单，每项含 `path`、`bytes`、`mode`、`role`、`sha256`。按路径排序后做规范 JSON 哈希。排除 `PACKAGE.json`、`validation_report.json`、`SHA256SUMS` 和任何哈希字段。

`package_hash` 覆盖 `native_hash`、`PACKAGE.json` 的稳定投影、四个边车的哈希。稳定投影只取 schema 版本、ALE-data 版本、身份、域与子域、入口、交付物、oracle、验证、许可、PII、来源等语义字段，排除 `built_at`、`built_by`、`package_hash`、`hashes`。边车内容也不能写构建时钟，否则边车哈希会漂移。

入库回执哈希覆盖 `package_hash`、`validation_report` 的哈希、接收时间和接收人。它只写数据库，不写回包内。这样包哈希、校验报告和入库记录形成三段可复算证据链，任何一段被改写都能被发现。

PoC 的七项检查是：native-stable、package-stable、mode-kept、self-reference、content-sensitive、content-sensitive-native、sidecar-clock。self-reference 测试把 `package_hash` 写回包内再重算，摘要会变；sidecar-clock 测试把构建时钟写进边车，摘要也会变。两项都证明当前候选不能把哈希值或时钟写进被哈希字节。

## 13.7 Agent 可见性

Agent 可见的只有 `base/input/` 中声明的输入和 `base/software/` 中声明的软件入口。`base/reference/` 在 solver 停止后才挂载，评分依据、答案键、rubric、judge 配置和 reference render 都不能进入 Agent 视图。

`PACKAGE.json` 默认不进入 Agent 视图。它即使不含答案，也会暴露 reference 文件名、oracle 类型、评分维度和许可信息。若运行框架必须把包目录整体挂载，L4 测试要证明 `PACKAGE.json` 与 `reference/` 被排除，或把 `PACKAGE.json` 移到版本层。

`package_manifest.json` 与 `materials.json` 同样按 platform 可见处理。`handoff.json` 可以带审核结论摘要，但不带专家个人身份、内部评分和 Agent 原始回答。审计记录留在数据库。

## 13.8 校验与测试

`schemas/canonical-task-source.schema.json` 校验任务源结构。`schemas/ale-package.schema.json` 校验包 overlay。`tools/wave2/hash_poc.py` 校验哈希候选。A 线还没有实现完整的包校验器，P12 需要把 PoC 接入组包临时目录和入库回执。

正反测试至少覆盖：官方 base 导入、官方命名 variant 导入、无 software、无 reference、大资产 external_ref、绝对路径、路径穿越、reference 泄漏、哈希自引用、边车时钟、PACKAGE.json 版本层与 base 层两种布局。

## 13.9 未决事项

1. 五组核心 41 个必填叶子是否在首批 30 条前冻结，仍需负责人确认。
2. `PACKAGE.json` 放版本层、base 层还是独立不可见目录，由 P12 与安全测试决定。
3. `package_hash` 是否只存数据库与回执，需组包器和入库器共同确认。
4. 官方 22 个命名 variant 的 overlay 命名规则，需与工程侧导入器对齐。
5. 官方 2 个无 reference 任务的 `oracle.required=false` 审批路径，需领域负责人签字。
6. 许可元数据在官方包中没有位置，导出后可能丢失，需在 overlay 与 `materials.json` 双写。
7. 大资产 external_ref 的 5 GiB 阈值与负责人批准流程，需平台与工程共同定。

## 13.10 证据与复现

字段注册表见 `docs/data/wave2-field-registry.csv`。官方兼容矩阵见 `docs/data/wave2-official-compat.csv`。机器可读形状见 `schemas/canonical-task-source.schema.json` 与 `schemas/ale-package.schema.json`。哈希结果见 `docs/data/wave2-hash-poc-results.csv`。

复现命令：

```bash
python3 tools/wave2/hash_poc.py
python3 -m json.tool schemas/canonical-task-source.schema.json
python3 -m json.tool schemas/ale-package.schema.json
```

本文件的数字来自冻结官方数据树与上述脚本输出。官方 122 个任务、100 个 base、22 个命名 variant、106 个 software、120 个 reference、79,065 个文件是文件事实。五组核心字段与哈希候选是设计决定，仍可在第二波 PoC 后修订。

## 13.11 版本记录

v1 草案，2026-11-14。首版冻结五组核心字段，新增官方 variant 兼容矩阵、包 overlay 草案、候选哈希与 7 项 PoC。未冻结 `PACKAGE.json` 布局、`package_hash` 存放位置和完整包校验器。
