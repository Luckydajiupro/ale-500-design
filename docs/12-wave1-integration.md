# 第一波研究整合：从官方案例与专家工作流到平台设计基础

这份文件把第一波三条研究线收在一起，回答五个问题：专家标注内容与 Canonical Task Source 字段怎么统一；平台采集的数据怎么对齐目标 ALE-data 包；专业审核、自动校验与工程转换各管什么；哪些技术设计已经有足够依据、哪些还要 PoC；进入技术选型、架构、数据库和 API 设计需要哪些输入。它不替代三份分线文档，也不冻结最终 Schema。

## 0. 结论摘要

三条线都已交付并进入 Git。

| 线 | 交付 | 规模 | 提交 |
|---|---|---|---|
| A 官方案例 | `docs/09-official-task-cases.md`、`docs/data/wave1-case-evidence.csv`、`docs/data/wave1-case-matrix.csv` | 397 行、42 条证据、6 个案例 | `ad02993`，主会话修正 `3841bb5` |
| B 专家规范 | `docs/10-expert-annotation-spec-v0.md`、`docs/data/wave1-task-source-fields.csv`、`wave1-submission-checklist.csv`、`wave1-review-rubric.csv` | 617 行、94 个字段、44 项清单、36 项 rubric | `483878e`，主会话修正 `877203f` |
| C 平台产品 | `docs/11-platform-product-design.md`、`docs/data/wave1-functional-map.csv`、`wave1-page-inventory.csv`、`wave1-agent-touchpoints.csv` | 523 行、91 项功能、25 个页面、10 个 Agent 介入点 | `3694834`，主会话修正 `5404125` |

本轮整合新增四份数据文件和本文件。`docs/data/wave1-canonical-task-source.csv` 是统一字段表，112 行，94 个来自专家规范的字段加 18 个平台派生字段。`wave1-package-contract-crosswalk.csv` 是官方包与平台包的字段对照，44 行。`wave1-contract-conflicts.csv` 是 16 条冲突及处置建议。`wave1-verification-map.csv` 是 8 种验证模式。`wave1-poc-backlog.csv` 是 11 个 PoC。`wave1-open-decisions.csv` 是 11 项待裁决。

五条主要结论。

第一，六个官方案例覆盖 5 种 `contract.kind`，但验证方式至少需要 4 种模式：确定性检查、rubric、Judge、混合。只用 5 个 kind 无法表达官方已有的“硬门加 LLM Judge”“几何硬门加渲染比对”“多答案通道”。

第二，官方 `task-data-v1.1` 没有统一的包级 `PACKAGE.json`。122 个任务、122 个 variant，100 个叫 `base`，22 个是命名 variant；包级 `PACKAGE.json` 为 0，递归命中的 2 个同名文件都是任务内容。平台设计里的 `ale-pkg-1.2` 是新增 overlay，不是官方现状。

第三，专家规范 v0 的十块、94 个字段可以作为 Canonical Task Source 的内容基线，但不能整表立即冻结。建议先冻结身份、资料、交付物、成功标准、环境五组核心，其余字段在试点后版本化。

第四，专业审核、自动校验、工程转换、平台组包与入库、合作方验收是五种不同责任，不能混成一个“审核通过”。专家负责内容与证据，评审人负责专业真假与等价性，自动检查只筛明确不合格，工程负责运行包与验证器实现，平台负责状态、哈希、组包、校验、入库与审计，合作方负责验收与 `counted_in_500`。

第五，下一波技术详细设计应先做三个模块：Canonical Schema 与包合同、验证描述与评分适配器、专家工作台与校验服务。运行框架选型仍等首批 30 条入库后，不在本轮决定。

## 1. 实际拆解了哪些官方案例

六个案例的选择标准是产物类型、验证方式和领域各不同，不是按官方配额抽样。所有事实来自冻结仓库与 ALE-data 的实际文件；没有运行官方任务代码。

| 案例 | 任务与 variant | 产物 | `contract.kind` | 验证方式 | 最强证据 |
|---|---|---|---|---|---|
| C1 | `business_finance/equity_research_summary` / `tsla_fy2023` | xlsx 工作簿 | `tabular_columns` | 结构、固定值、公式扰动、实时标签 | 43 个检查项；reward 是 `score=passed/total`；参考工作簿与提交件 MD5 相同 |
| C2 | `business_finance/taxform_4_1` / `variant_1` | 表单 JSON | `numeric_cases` | 硬门加逐字段等值 | 191 字段；页面印 15,750，主 GT 用 15,000，alt GT 兜底 |
| C3 | `psychology_neuro/scene2_resample` / `base` | NIfTI、PNG、CSV | `artifact_diff` | 几何与统计不变量 | 0.7 重算统计加 0.3 CSV；截图只 `verify()` 不比像素；8.66 GB 镜像 |
| C4 | `engineering/2d_drawings_to_3d_building_model` / `base` | OBJ、BLEND | `artifact_diff` | 几何硬门加 8 问 Judge | 1 mm 双向距离；14 个渲染视图；无参考 OBJ；reward 是 `yes_count/8` |
| C5 | `engineering/chisel_verilog_alignment_seq_1` / `base` | JSON 答案集 | `code_artifact` | 集合等值 | 0.1 格式加 0.1 信号加 0.8 集合；`target_location` 值不校验；反篡改硬门无代码 |
| C6 | `legal/legal_dr_fees_01` / `base` | JSON 数值表 | `document_qa` | Decimal 容差 | 5 案 15 个数；7/7/6 权重；评分器硬编码答案键并丢弃参考文件 |

### 1.1 六个案例的共同发现

验证器不在数据包里。六条案例的评分代码都在旧任务仓库的 `scripts/` 或 `main.py`，ALE-data 包只带输入、软件和 reference。平台如果只做“包校验”，不做验证器登记与哈希，包自包含性就是假的。

oracle 经常不独立。C1 的参考工作簿与提交者原件字节相同；C2 的题面标准扣除与主 GT 冲突；C6 的评分器另有一份硬编码答案键。500 条不能复用官方 reference，也不能只让一位专家既写答案又写标准。

文档声称的硬门可能没有代码。C5 的 task card 写“改文件即 0 分”，评分代码没有哈希校验；`target_location_in_optimized_sv` 只查键存在，不读值。审核必须把“声称的检查”与“实际代码”分开。

部分分与二值通过字段不是一回事。C1 的 `score` 是 43 项通过占比，`passed` 布尔只在 1.0 时为真；C4 的 `score` 是 8 问通过数，`passed` 只是 `>=0.5` 的报告字段。契约必须同时写 `score` 口径与 `passed` 口径，不能拿 `passed` 当 reward。

非确定判定要留原始回答。C4 的 Judge 没有历史判定记录，跨模型稳定性未知；C3 的截图只验证可打开，不验证内容。Judge 任务必须保存问题、模型、原始回答、版本和人工复核样本。

实时外部源不可复现。C1 的 Yahoo Finance 实时字段只校验“是数值”；C3 依赖 8.66 GB 镜像；C4 的参考渲染不可由包内文件重建。500 条默认冻结快照或本地数据，不默认联网。

### 1.2 官方包计数与结构

122 个任务、122 个 variant。104 个有 `input+software+reference` 三件套，16 个只有 `input+reference`，2 个只有 `input+software`，这 2 个都没有 `reference`。包级 `PACKAGE.json` 为 0；递归同名 2 个都是任务内容。文件数中位 16，最少 3，最多 41,775；最大包约 11.8 GB。

这说明“官方包”不是一种统一容器，而是一组按任务自定的目录。平台不能把某一种 manifest 当成官方标准，只能把官方目录当内容基线，再加自己的包级元数据。

## 2. 专家标注规范初稿覆盖了什么、还缺什么

规范初稿的覆盖范围按专家从接单到冻结的实际动作统计，不按文档章节统计。

### 2.1 覆盖

`docs/10-expert-annotation-spec-v0.md` 已经回答专家实际要做什么。

- 项目说明：目标、交付物、不做什么、分层工时、按条计费、付款节点、两轮返修、第三轮小时费、保密、支持、退出。
- 合格任务：六条最低定义、三个官方包作复杂度标尺、10 种不合格形态、一句话判据。
- 任务源十块：身份、场景、资料、步骤、交付物、成功标准、环境、审核、来源、交接。94 个字段，68 个必填、17 个条件必填、9 个可选。
- 流程：方向分配、选题、资料准备、起草、自检、提交、专业审核、返修、冻结九段。
- 资料与授权：六类资料、三类角色、最低资料集、公开/合成/客户材料边界、许可清单、PII 四级、SHA-256、合成件标注。
- 自检：九项自动检查逐项翻译成提交前动作，14 项人工清单，返修、拒收、升级三类处置。
- 专业审核：六维、阻断与非阻断、评审资格与利益冲突、双评与 10% 抽样、5 个工作日 SLA、返修轮次。

规范明确区分“平台承载”与“ALE-data 实际承载”。这一点很重要：十块是平台任务源结构，不是官方包已经存在的字段。

### 2.2 本轮修正

主会话在合并前修了五处。

- 参考解不再是绝对必填。经批准采用 `human_rubric` 且没有唯一参考解时，提交 rubric、至少一份合格样例和一个反例。
- `task_brief.md`、`output_contract.json`、`answer_key.json` 在部分官方任务里已经是内容文件，不再被说成平台统一新增的边车；平台新增的是包级 `PACKAGE.json`。
- 任务身份不再假定所有包都叫 `base`。新建任务用 `base`，官方导入保留原 variant 名。
- `target_format` 的 `harbor` 只作为未来选项记录，P1 不做 Harbor 转换。
- 交付物格式从办公文档扩展到 `nii`、`nii.gz`、`obj`、`blend`、`dta`、`sav`、`rds`、`h5`、`tif` 等领域原生格式。

### 2.3 缺口

55 个子域与 72 个任务族还没有固化成字段枚举。专家选题仍靠领域负责人判断，平台无法只靠下拉框保证分布。

官方包没有统一的包级 manifest，平台边车能否被合作方接受还没有验证。许可元数据在官方包中没有位置，导出后可能丢失。

GUI、视觉、语义任务的 Judge 校准与人工复核比例没有基线。C4 的 8 问 Judge 没有历史稳定性数据，C3 的截图只验证可打开。

大文件、容器镜像、二进制产物的对象存储配额和导出策略没有定。C3 的 8.66 GB 镜像和生命科学的 11.8 GB 包都超过当前 5 GiB 阻断线。

英文任务说明的统一术语表和文体指南没有定。“专业判断”评分的一致性没有历史数据。返修次数、时限和费用在合同中的表述还没有与法务对齐。

## 3. 平台完整功能地图与主要用户流程

`docs/11-platform-product-design.md` 给出 7 类用户、13 段主链、9 个任务主状态、4 个入库状态、11 个模块、91 项功能、25 个页面。

### 3.1 用户与主链

七类用户是专家、领域评审、质量审核、平台管理员、工程接口人、项目负责人、合作方接口人。每日高频是前三类。

主链从方向配额开始，经分配、起草、资料、自检、提交、自动检查、专业评审、质量审核、批准、冻结、组包校验、入库，到对外验收。任务状态是 `draft -> submitted -> auto_checked -> in_review -> approved -> frozen -> packaged -> package_validated -> ingested`，`returned` 是返修旁路，`void` 是冻结前作废。入库侧是 `received -> validating -> validated -> published`，另有 rejected、quarantined、superseded、withdrawn。

生产完成看 `ingested`，计入 500 看 `counted_in_500`。两个计数器分开，前者由平台写入，后者只由合作方验收回执改写。

### 3.2 功能范围

11 个模块是任务与批次、专家与配额、任务源编辑、资料与授权、自动检查、评审与返修、冻结与快照、ALE-data 组包、包校验与入库、Agent 辅助、管理与统计。91 项功能分为 P1 核心 66、P1 加固 15、完整产品 10；优先级是 P0 48、P1 33、P2 10。

25 个页面中 P1 核心 21、P1 加固 4、完整产品 0。页面覆盖专家工作台、任务源表单、资料上传、自检报告、评审队列、审核台、冻结与组包、包校验、入库、Agent 建议面板、管理与统计。

### 3.3 P1 与完整产品的区别

P1 是专家生产与半自动化标注系统。它必须支持专家入驻与权限、十块任务源编辑、资料上传与隔离、自动检查、专业评审与质量审核、冻结快照、从冻结快照自动组包、L1 到 L5 校验、幂等入库、审计，以及 Agent 只写建议。

完整产品在 P1 之外增加合作方验收门户、跨批次分析与配额预测、更多 Agent 自动化、外部供应方接入、更多语言与导出格式、跨库检索与再利用。完整产品不是本轮开发范围。

### 3.4 Agent 的介入位置

Agent 五项能力是访谈、追问、结构化、预检、审核辅助，落在 10 个介入点。硬规则是只写 `agent_suggestions` 与 `agent_runs`，不直接写任务源；专家逐字段确认后才可写入；自动采纳必须为 0。

Agent 不能改许可、PII、IRB，不能提交、冻结、组包、校验、入库，不能改包，不能替评审人签字。试点单条成本上限 60 元，正式建议 120 元；p95 首 token 8 秒、结构化 60 秒、预检 90 秒；阻断级漏报必须为 0。

### 3.5 资料、组包与入库

资料四层是 raw、deidentified、work、reference。单文件上限 20 GiB，分片 64 MiB，重试 3 次；许可类型是 public_domain、cc_by、proprietary、internal、synthetic；PII 四级。P1 用人工加规则脱敏，自动脱敏延后。

组包唯一输入是冻结快照。八步是读快照、按 entrypoints 复制、生成 `PACKAGE.json`、生成四个边车、计算 `native_hash` 与 `package_hash`、临时目录校验、原子移动、幂等返回。大于 5 GiB 阻断，大于 1 GiB 警告，12 GiB 级资产需负责人批准 `external_ref`。

L1 查结构，L2 查语义，L3 查完整性，L4 查安全授权，L5 查入库一致性。L4 的绝对路径检查只查元数据字段，正文命中只警告。

## 4. 统一专家标注内容与 Canonical Task Source

统一的目标是让专家只填一次，平台能派生、导出和审核，不要求专家理解包格式。

### 4.1 统一后的结构

Canonical Task Source 保留十块，不新造第十一块。字段名沿用 B 线，块内用点号命名，例如 `identity.task_id`、`materials.license.type`、`success_criteria.check_method`。

新增两个派生块，只由平台或工程填写，专家不填。

- `verification`：`contract_kind`、`mode`、`artifacts`、`oracle_required`、`tolerance`、`judge_config`、`verifier_entry`、`verifier_sha256`。
- `package`：`schema_version`、`ale_data_version`、`entrypoints`、`files`、`native_hash`、`package_hash`、`built_by`、`built_at`、`counted_in_500`、`scope_exception`。

统一字段表是 `docs/data/wave1-canonical-task-source.csv`，112 行。每行给出块、规范字段、类型、必填、来源、可见性、B 线字段、平台存储、ALE-data 承载、`PACKAGE.json` 字段和备注。

### 4.2 建议冻结的核心

不建议一次冻结 94 个字段。建议先冻结五组核心，共约 40 个字段。

- 身份：`task_id`、`domain_code`、`subdomain_code`、`title_en`、`title_zh`、`language`、`batch_id`、`source_task_id`、`source_variant`。
- 资料：`material_id`、`kind`、`role`、`path`、`sha256`、`bytes`、`license.type`、`license.redistribution`、`pii_level`。
- 交付物：`deliverable_id`、`path`、`format`、`mandatory`、`acceptance_ref`。
- 成功标准：`criterion_id`、`dimension`、`check_method`、`weight`、`threshold`、`critical`。
- 环境：`os`、`gui_required`、`gpu.required`、`software`、`network.mode`、`resources.time_limit_min`。

其余字段保留草案状态，按批次版本化。这样表单、导出与 `PACKAGE.json` 可以先落地，又不会把未经验证的粒度锁死。

### 4.3 三个必须一起冻结的关联

`task_id`、目录名与包内 `task_id` 必须一致。官方 `task_id` 前缀有 `finance/`、`business_finance/`、`machine_learning/` 等多种写法，平台用 canonical `task_id`，另存 `source_task_id` 与 `source_variant`。不能把官方前缀直接当平台主键。

`deliverables.path`、任务说明里的路径、`output_contract` 的路径、运行包 `artifacts` 必须逐字一致。C2 的路径不一致是最常见的工程阻断。

`success_criteria` 的权重合计 100，`critical=true` 至少一条，`check_method` 决定验证模式。权重与验证模式不能在导出后由工程改；要改回任务源版本。

### 4.4 验证模式

`contract.kind` 保留五值：`numeric_cases`、`tabular_columns`、`document_qa`、`artifact_diff`、`code_artifact`。

新增 `verification.mode` 五值：`deterministic`、`rubric`、`judge`、`hybrid`、`human_review`。

新增 `verification.artifacts[]`，每个工件带 `role`：`oracle`、`rubric`、`judge_config`、`fixture`、`reference_render`、`answer_key`、`output_contract`、`verifier`、`sample_good`、`sample_bad`。

六案例的映射是：C1 确定性，C2 确定性，C3 混合，C4 Judge，C5 确定性，C6 确定性。新增两类模式：无唯一参考解的 `human_rubric`，以及多答案通道的 `alt_oracle`。

`oracle.required` 不再一律为真。没有唯一参考解时可以为假，但必须有 rubric、合格样例和反例，并经批准。C4 的官方包没有参考 OBJ，只有 `eval_config.json` 与 14 张参考渲染，这就是合法先例。

### 4.5 分数与通过

契约同时写 `score` 与 `passed`。`score` 是连续分或分项加权，`passed` 是报告布尔。C1 的 reward 是 `score`，C4 的 reward 也是 `score`，不能把 `passed` 当 reward。

硬门必须显式列出：缺文件、格式错、路径不符、几何无效、答案泄漏。硬门失败直接 0，不进入部分分。部分分只在硬门通过后计算。

## 5. 对齐平台采集数据与目标 ALE-data 包

对齐的基准是官方 `task-data-v1.1` 的实际目录与文件，不是设计稿里的理想结构。

### 5.1 官方包与平台包的关系

官方 `task-data-v1.1` 是 `<domain>/<task>/<variant>/{input,software,reference}`。variant 可以是 `base`，也可以是 `tsla_fy2023`、`137`、`variant_1` 这类命名值。没有版本层，没有包级 `PACKAGE.json`，没有统一哈希。

平台包是 `<domain_code>/<task_slug>/<task_version>/base/{PACKAGE.json,input/,software/,reference/}`，外加 `package_manifest.json`、`materials.json`、`provenance.json`、`handoff.json` 四个版本级边车。`validation_report.json` 不进哈希。

这两者不是同一种东西。平台包是官方目录的内容基线加一层平台元数据，不能声称“与官方原生布局一致”。22 个命名 variant 不能强行改成 `base`；导入时保留 `source_variant`，导出时按平台版本层组织。

### 5.2 平台包必须补的字段

官方 `reference_manifest.json` 只有 3 个，且字段不一致；`stage1_manifest.json` 有 23 个，`source_manifest.json` 有 17 个，`evaluator_data_manifest.json` 有 1 个。平台不能假设官方已有统一契约。

`PACKAGE.json` 在现有设计稿基础上补六类字段。

- `source.task_id` 与 `source.variant`：官方导入时保留原身份。
- `agent_visible_inputs[]`：明确哪些文件对 agent 可见；官方 `reference_manifest` 已有样例。
- `required_agent_outputs[]`：明确必须产物；官方 `reference_manifest` 已有样例。
- `verification.mode`、`verification.artifacts[]`、`verification.oracle_required`：表达 Judge、rubric、混合、多答案通道。
- `environment_intent` 扩展：`os`、`gui`、`network`、`external_services`、`gpu`。官方 122 条里 36 条 Windows、40 条 GUI、9 条 GUI 未知、6 条在线必需、5 条 staged-local、2 条 public-ref，不能只写 sandbox。
- `governance`：`risk_tier`、`license`、`pii`、`scope_exception` 与 `counted_in_500` 的判定条件。实际计数不写进包，只写入库记录。

### 5.3 冲突与处置

`docs/data/wave1-contract-conflicts.csv` 列了 16 条冲突。最重要的六条。

C01 官方无版本层，平台有 `version/base/`。处置是保留官方 variant，平台新增版本层，文档改称 overlay。

C02 官方无统一 `PACKAGE.json`。处置是把 `ale-pkg-1.2` 明确为平台新增，不写成官方契约。

C03 `PACKAGE.json` 若随 `base/` 对 agent 可见，会泄漏 reference 文件名。处置是优先放版本层或不可见目录；若必须放 `base/`，L4 增加 agent 视图测试。

C04 五值 `contract.kind` 不能表达 Judge、rubric、混合评分。处置是增加 `verification.mode` 与 `verification.artifacts[]`。

C07 两个 engineering 任务没有 reference。处置是允许 `oracle.required=false`，但必须有 rubric、样例与反例，并经批准。

C15 官方验证器不在 ALE-data 包。处置是平台包只承载数据与验证描述，验证器由工程在运行包实现并登记哈希，平台不跑任务、不判分。

### 5.4 官方包的三类承载

平台字段要落到三类承载，不能假设一个文件全包。

内容承载：`input/`、`software/`、`reference/` 的字节，以及 `task_brief.md`、`output_contract.json`、`answer_key.json` 等任务自定文件。

包级承载：`PACKAGE.json`、四个边车、`SHA256SUMS`、`package_manifest.json`。这里放身份、文件清单、哈希、许可、来源、验证描述、环境意图。

平台库承载：审核记录、签字、评审意见、Agent 运行、快照、批次、`counted_in_500`、验收回执。这些不进包，进数据库与审计日志。

### 5.5 哈希与不可变

`native_hash` 覆盖 `base/` 内容文件，排除 `PACKAGE.json`。`package_hash` 覆盖 `base/` 全部文件、`PACKAGE.json`、四个版本级边车，排除 `validation_report.json`。同源重建的 `native_hash` 与 `package_hash` 必须一致。

`files[]` 只列 `base/` 内容文件，不列 `PACKAGE.json`；每项带 `path`、`sha256`、`bytes`、四位八进制 `mode`、非空 `role`。软件文件保留可执行位。

冻结快照不可变。组包只读快照，不读工作区。入库记录与包哈希不符时不算入库。

## 6. 专业审核、自动校验、工程转换的边界

| 责任 | 做什么 | 不做什么 | 产物 |
|---|---|---|---|
| 专家 | 场景、步骤、资料许可证据、交付物、成功标准、参考解或 rubric | 不写 Dockerfile、`task.toml`、`verify.py`，不做技术选型，不替评审签字 | 任务源、资料、参考解、自检记录 |
| 领域评审 | 判断专业真实性、方法标准、难度、等价解、隐藏要求 | 不代写，不改专业结论，不改许可 | 评审意见、阻断标记、签字 |
| 质量审核 | 判断契约一致、资料可授权、交付物可验证、重复与泄漏 | 不判断专业真假，不实现验证器 | 审核结论、返修单 |
| 自动校验 | Schema、路径、哈希、枚举、权重、许可字段、PII 扫描、包结构、L1 到 L5 | 不证明专业正确，不判断业务价值，不替代人工 | 检查报告、错误码、隔离标记 |
| 工程转换 | 把任务源转成 `task.toml`、Dockerfile、`verify.py`、运行包 artifacts、Judge 实现 | 不改任务内容、不改成功标准、不改许可 | 运行包、验证器、冒烟记录 |
| 平台 | 状态机、权限、存储、快照、组包、校验、入库、审计、统计 | 不跑任务、不判分、不转 Harbor、不决定验收 | 包、入库记录、审计日志、看板 |
| 合作方 | 验收、决定是否计入 500 | 不改平台数据，不替专家写任务 | 验收回执、`counted_in_500` |

四条硬边界。

第一，自动检查只筛明确不合格，不证明合格。九项检查全过，任务仍可能专业错误。

第二，专业审核不做工程实现，工程转换不做专业判断。评审人说“这个标准测不到目标”，工程不能自行改成“文件存在即通过”；要退回任务源。

第三，平台不跑任务、不判分。验证器由工程实现，运行由运行框架执行，平台只登记验证器哈希与验证描述。

第四，合作方验收是 `counted_in_500` 的唯一来源。平台生产完成不等于计入 500。

## 7. 哪些技术设计已有充分依据

已有充分依据、可以进入详细设计的部分。

- 十块任务源与 94 个字段的内容模型。B 线逐字段定义，A 线六个案例给出真实形态，C 线给出页面与状态。
- 五种 `contract.kind` 与六案例的映射。A 线的 42 条证据足以支撑字段与验证描述。
- 平台包是官方内容基线的 overlay。官方 122 条、100 个 base、22 个命名 variant、0 个包级 `PACKAGE.json` 是文件事实。
- `PACKAGE.json` 的必填字段、`files[]` 角色、四边车、`native_hash` 与 `package_hash` 的分工。docs/08 已有 47/47 自检的检查器设计。
- 任务状态机与入库状态机。C 线把 9 个主状态、2 个旁路、4 个入库状态写全。
- 资料四层、许可类型、PII 四级、上传分片与隔离。
- 组包八步、L1 到 L5、5 GiB/1 GiB/12 GiB 阈值。
- 角色与权限、审计事件、批次与配额。
- P1 与完整产品的边界。C 线给出 66/15/10 的功能分层与 21/4/0 的页面分层。
- 评审六维、阻断规则、双评与 10% 抽样、5 个工作日 SLA。docs/03 与 docs/07 已批准。

这些部分可以作为架构、数据库与 API 设计的输入，不需要再等官方案例。

## 8. 哪些技术假设需要 PoC

`docs/data/wave1-poc-backlog.csv` 列了 11 个 PoC。按阻塞程度排序。

P01 是 `PACKAGE.json` 的位置与可见性。它决定答案是否泄漏、`package_hash` 覆盖什么、L4 怎么测。最小测试是一个含 reference 的包在两种布局下的 agent 视图与哈希一致性。

P02 是官方 122 条与 22 个命名 variant 的导入。它决定平台能否做官方回归、能否保留 instruction 相对路径、能否不伪造包级 `PACKAGE.json`。

P03 是验证描述与评分适配器。它决定 `contract.kind` 五值加 `verification.mode` 与 `artifacts[]` 是否覆盖六案例与 Judge/混合评分。

P04 是无唯一参考解的任务。它决定 3D、视觉、合规类任务能不能进入 500，以及 `human_rubric` 的合法条件。

P05 是大资产。8.66 GB Slicer 镜像、11.8 GB H5、5 GiB 阻断线、12 GiB `external_ref` 需要真实重建与成本数据。

P06 是 Agent 结构化建议的可用率、采纳率、误报、漏报与单条成本。它决定 60/120 元假设是否成立。

P07 是 PII 与许可规则的误报率。它决定 L4 会不会把可生产任务大量挡在门外。

P08 是 22 并发、12 GiB 级包、备份与恢复。它决定 W1 的容量。

P09 是审计链离线校验。它决定合作方抽查能否不依赖平台环境。

P10 是官方 122 条回归导入的计数隔离。它决定官方任务不会误计入 500。

P11 是 Windows 36 条、GUI 40 条、online-required 6 条的环境声明与降级。它决定 P1 是否要支持这些形态。

## 9. 进入技术选型、架构、数据库与 API 设计的输入

以下输入只描述数据形状、约束与接口面，不指定框架。

### 9.1 领域模型

最小领域对象是 User、Role、ExpertProfile、Category、Subdomain、Batch、Task、TaskVersion、TaskSource、Material、Deliverable、Criterion、EnvironmentSpec、Review、ReviewItem、Assignment、Snapshot、Package、PackageValidation、IngestRecord、AgentRun、AgentSuggestion、AuditEvent、Handoff、AcceptanceReceipt。

Task 与 TaskVersion 分离。Task 是稳定身份，TaskVersion 是每次提交的不可变版本。冻结快照指向 TaskVersion，包指向快照。

Material 按 `role` 分 input、reference、template，按 `layer` 分 raw、deidentified、work、reference。Deliverable 与 Criterion 多对多，用 `acceptance_ref` 连接。

Package 与 TaskVersion 一对多，`package_hash` 唯一。IngestRecord 与 Package 一对一，`counted_in_500` 只在 AcceptanceReceipt 到达后改写。

### 9.2 API 面

需要七组 API。

- 任务源：草稿读写、字段校验、提交、版本列表、差异比较。
- 资料：上传初始化、分片、完成、哈希复核、许可与 PII 元数据、隔离下载。
- 评审：队列、派单、领取、意见、阻断、返修、签字、SLA。
- 冻结与组包：创建快照、读快照、生成包、查询包、下载包。
- 包校验与入库：L1 到 L5、隔离、重试、幂等入库、回执。
- Agent：建议生成、逐字段确认、运行记录、采纳统计。
- 管理与统计：配额、批次、专家负荷、生产完成、验收完成、审计导出。

所有写操作要幂等键。所有状态迁移要写 AuditEvent。所有包操作要带 `task_id + task_version + package_hash`。

### 9.3 数据库约束

`task_id` 与 `task_version` 唯一。`package_hash` 唯一。冻结快照不可更新。`counted_in_500` 只能由验收回执写入。`agent_suggestions` 没有 `confirmed_by` 不得写入任务源。`materials.role=reference` 不得出现在 agent 可见视图。`review.sign_offs` 四类签字齐全才能冻结。

### 9.4 非功能输入

22 并发上传与组包；单包 5 GiB 阻断、12 GiB 级 external_ref；单文件 20 GiB；分片 64 MiB；重试 3 次；p95 首 token 8 秒、结构化 60 秒、预检 90 秒；审计链离线可校验；RBAC 到域、子域、批次、任务；所有导出带哈希与版本。

这些输入与 Django、FastAPI、Dify、LangGraph 的选型无关。选型可以后置，数据形状与边界不能后置。

## 10. 下一波技术详细设计从哪些模块开始

建议按三个波次。

第一波，先做合同与验证描述。Canonical Schema、`PACKAGE.json` 字段、`verification.mode` 与 `artifacts[]`、官方导入适配器、六案例回归。对应 P01、P02、P03。没有这三个，后面的表单、组包、评分都会返工。

第二波，做专家工作台与包流水线。专家表单、资料上传与许可/PII、自检报告、评审队列、冻结快照、组包八步、L1 到 L5、幂等入库、审计。对应 P05、P07、P08、P09。这一波可以并行拆成“前端工作台”“后端任务源与资料”“组包与入库”三个子模块。

第三波，做审核返修与 Agent。双评、抽样、返修轮次、签字、SLA、Agent 五项建议与逐字段确认、成本与质量看板。对应 P04、P06、P11。Agent 放最后，因为它依赖稳定的任务源与验证描述。

管理与统计横跨三波，但 P1 先做配额、批次、生产完成、验收完成、审计导出五类视图，不做跨批次预测。

## 11. 真正需要项目负责人裁决的事项

`docs/data/wave1-open-decisions.csv` 列了 11 项。最需要先定的六项。

D01 是 v0 字段冻结范围。建议只冻五组核心约 40 个字段，其余版本化。全量冻结会把未验证的粒度锁死，完全不冻会让表单与导出无法开工。

D02 是 `PACKAGE.json` 的位置与可见性。建议放版本层或不可见目录；若必须放 `base/`，接受 L4 可见性测试与泄露风险。

D03 是平台包与官方包的命名关系。建议明确为 overlay，保留 `source_variant`，不声称原生一致。

D04 是无唯一参考解的任务是否允许。建议允许 `human_rubric`，条件是批准、双评、样例外与反例。

D05 是法律 42 条的 `scope_exception` 是否计入 500、是否需要合作方书面接受。建议计入配额但 `counted_in_500` 由回执决定，书面确认前不对外宣称验收。

D06 是客户材料能否在试点后进入生产。建议允许，但必须有书面授权、脱敏方案、存储期限、删除承诺、法务确认五项；缺一项拒收。

其余五项是 Agent 成本与自动采纳、Windows/GUI/大资产范围、运行框架选型时点、`handoff.json` 审核摘要、官方导入边车策略。它们影响详细设计顺序，但不阻塞第一波合同工作。

## 12. 本轮不做什么

不复制官方任务作为 500 条新任务。官方 122 条只作回归样本与复杂度标尺。

不修改冻结输入。`inputs/frozen/` 仍是只读，88 GiB 副本没有改动。

不启动正式专家生产。三条试点与首批 30 条仍按已批准排期，不因本轮研究提前。

不修改已批准的配额、批次、费用和四道门。

不预先决定 Django、FastAPI、Dify 或 LangGraph。本轮只给框架无关的数据形状、边界与 API 面。

不把 `PACKAGE.json` 说成官方已有契约。它是平台 overlay，必须带版本与迁移策略。

不把 `passed` 当 reward，不把自动检查当专业审核，不把生产完成当计入 500。

## 13. 版本记录

| 版本 | 日期 | 变更 | 状态 |
|---|---|---|---|
| v0 | 2026-11-14 | 第一波三线整合：六案例、专家规范、平台产品、Canonical 字段、ALE-data 对齐、边界、PoC、技术设计输入 | 草案，待项目负责人裁决 |
