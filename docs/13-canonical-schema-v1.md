# 13 Canonical Schema 与 ALE-data 包合同 v1

这份文件把第一波的字段研究收束为可评审的 Canonical Task Source v1 与平台包合同草案。它的用途是给平台表单、数据库、组包器和工程交接一个共同的字段基线，同时把尚未通过技术验证的部分明确标为候选。文件不修改 `task-data-v1.1` 的官方字节，也不把平台新增的 `PACKAGE.json` 说成官方已有契约。

## 13.1 结论

v1 只冻结五组核心字段，共 41 个必填叶子：`identity`、`materials`、`deliverables`、`success_criteria`、`environment`。`scenario`、`operations`、`review`、`provenance`、`handoff`、`verification`、`package` 七组为扩展块，字段定义可评审，但必填条件和枚举在首批试点校准前不冻结。

`schemas/canonical-task-source.schema.json` 是这五组核心的机器可读定义，`docs/data/wave2-field-registry.csv` 是 112 条字段的完整登记表。两者不是同一层：Schema 管结构与必填，注册表管来源、可见性、平台落点、包落点和官方证据。

平台包是官方 variant 的 overlay。官方路径是 `<domain>/<task>/<variant>/{input,software,reference}`，variant 可以是 `base`，也可以是命名值。平台在 122 条官方任务上新增版本层和元数据层，不重写官方内容文件。

## 13.2 五组核心字段

| 块 | 作用 | 必填叶子 | 主要约束 |
| --- | --- | --- | --- |
| `identity` | 任务身份、批次、负责人 | 8 | `task_id` 为 `<domain_code>/<task_slug>`；`version` 由平台生成；`language` 决定 `title_en` 是否条件必填 |
| `materials` | 专家提交的资料清单 | 9 | 每项有 `material_id`、`kind`、`role`、`path`、`sha256`、`bytes`、`license`、`pii_level`、`used_by` |
| `deliverables` | 被评 Agent 要交的产物 | 7 | 路径必须是 base 相对 POSIX；格式与扩展名一致；每个交付物至少被一个步骤产出 |
| `success_criteria` | 评分维度、权重、阈值、证据 | 8 | 至少一条 `professional_judgment`，至少一条 `critical=true`；不接受“合理”“基本正确”这类阈值 |
| `environment` | 运行意图 | 9 | `os`、`gui_required`、`gpu.required`、`network.mode`、资源、`nested_virt`；`unknown` 不得定低风险 |

`materials.role` 只有 `input`、`reference`、`template` 三值。`reference` 是被评 Agent 不可见的评分依据；`template` 是允许 Agent 读取的起点文件；`input` 是任务输入。官方包里的 `software/` 不进入 `materials`，由 `environment.software` 和包的 `files[].role=software` 承载。

`success_criteria.check_method` 四值与验证合同对接：`auto_script` 和 `artifact_diff` 落到 `deterministic` 或 `hybrid`；`llm_judge` 落到 `judge`；`human_rubric` 落到 `human_review`。字段本身不决定最终评分器，评分器由工程侧交接合同实现。

## 13.3 扩展块与发布条件

`verification` 记录验证意图，不记录可执行评分器。必填四项：`contract_kind`、`mode`、`artifacts`、`oracle_required`。`artifacts[]` 每项至少有 `role`、`path`、`visibility`；`visibility` 为 `agent_visible`、`evaluator_only`、`platform_only` 三值。参考答案、rubric、judge 配置、参考渲染、正反样例只能是后两者。

`package` 记录平台 overlay 的包级字段，包括 `schema_version`、`ale_data_version`、`entrypoints`、`files[]`、`native_hash`、`built_by`、`built_at`、`counted_in_500`、`scope_exception`。`package_hash` 只作为候选字段出现在 Schema 中，不写进被它覆盖的字节。

发布到 ALE-data 前，扩展块按合同逐项升级为必填：`scenario` 和 `operations` 用于内容审核，`review` 用于审核签字，`provenance` 用于来源与相似性检查，`handoff` 用于工程转换，`verification` 用于评分交接，`package` 用于组包。升级规则写在平台校验器，不写死在专家表单的初始必填里。

## 13.4 身份与版本

Canonical `task_id` 由平台生成，格式为 `<domain_code>/<task_slug>`。官方导入时保留三个原值：`source_task_id`、`source_variant`、`source_revision`。这样做是因为官方 `task_id` 前缀不统一，存在 `finance/...`、`business_finance/...`、`machine_learning/...` 等多种写法，不能直接当平台主键。

版本规则：

- `version` 从 1 开始，提交后不可改内容；专家修改产生新版本，旧版本保留。
- 冻结快照绑定 `task_id + version`，组包器只接受冻结快照。
- 同版本重建必须得到同一 `native_hash`；`package_hash` 的稳定性由 13.6 的候选规则约束。
- 官方导入任务保留 `source_variant`，不强行改成 `base`；平台包目录的版本层与官方 variant 层分开表达。

22 个官方任务使用命名 variant，100 个使用 `base`。命名 variant 包括 `tsla_fy2023`、`odoo_compact`、`variant_1`、`137`、`table1`、`crane_flyingsky` 等。导入矩阵见 `docs/data/wave2-official-compat.csv`，每行给出 `source_variant`、`has_base`、`has_software`、`has_reference`、`import_mode`、`blockers` 和 `test_case`。

## 13.5 官方兼容矩阵

122 条官方任务按目录形态分为五类导入模式：

| 模式 | 条件 | 处理 |
| --- | --- | --- |
| `direct_base` | variant 为 `base`，input、software、reference 齐全 | 直接映射版本层，补平台边车 |
| `staged_base` | variant 为 `base`，缺 brief、software 或 reference | 先补入口或工程说明，再补边车 |
| `direct_named` | 命名 variant，三件套齐全 | 保留 `source_variant`，按 variant 路径导入 |
| `staged_named` | 命名 variant，缺入口或软件 | 保留 variant，补平台入口与说明 |
| `external_ref` | 单包超过 1 GiB 或镜像过大 | 只存引用与哈希，不复制大资产 |

兼容矩阵的阻塞码有 `NO_SOFTWARE`、`NO_BRIEF`、`NO_REFERENCE`、`LARGE_ASSET`、`SYMLINK_RUNTIME_ENV`。16 条任务没有 `software/`，2 条任务没有 `reference/`，这些都不是平台可以自动补齐的内容，必须由工程侧在导入前给出处理决定。2 条无 reference 的任务是 `engineering/cailian_road_highway_alignment_2` 与 `engineering/inner_support_elevation_optimization`，只能走人工评审或补参考。

三个官方任务的 variant 名与 `published_tasks.json` 不一致：`other/mota_exploration`、`visual_media/uv_reproduction`、`visual_media/skeletal_animation_reproduction`。导入时以目录实际 variant 为准，同时记录发布清单的原值，不能静默取一个。

## 13.6 包布局

候选布局：

```text
packages/<domain_code>/<task_slug>/<version>/
  PACKAGE.json
  package_manifest.json
  materials.json
  provenance.json
  handoff.json
  base/
    input/
    software/
    reference/
```

`base/` 内只放官方内容或新任务内容，不放平台元数据。`PACKAGE.json` 与四个边车放版本层。这样做的理由有三条：被评 Agent 只挂载 `base/` 的可见部分；哈希覆盖范围与可见范围分开；官方 variant 的 `base/` 名称不再与平台包根混淆。

如果第二波 PoC 证明版本层布局不能兼容现有挂载器，备选是把 `PACKAGE.json` 放 `base/` 但在运行时排除。这个备选必须通过 13.7 的可见性测试，不能只靠约定。默认方案仍是版本层。

`files[]` 只列 `base/` 内容文件，每项有 `path`、`sha256`、`bytes`、`mode`、`role`。`mode` 保留四位八进制，`software/run.sh` 的可执行位必须保留。`PACKAGE.json` 自身不进 `files[]`。`package_manifest.json` 记录文件数与总字节，`materials.json` 记录资料许可与 PII，`provenance.json` 记录来源与相似性检查，`handoff.json` 记录工程交接状态。

## 13.7 Agent 可见性与隔离

被评 Agent 只能读取 `input/` 与声明为 `agent_visible` 的模板。以下内容不可见：

- `reference/` 下的答案、rubric、fixture、参考渲染、正反样例。
- `PACKAGE.json` 中的 `files[]` reference 路径、`oracle` 细节、`verification.artifacts` 的 evaluator 工件。
- `materials.json` 的许可备注、PII 细节、来源 URL 中带签名或凭证的部分。
- `handoff.json` 的工程备注与内部风险。

平台保留完整清单、角色、哈希和验证描述，导出时按可见性裁剪。L4 校验增加 agent 视图测试：用只读挂载构造 Agent 可见树，若出现 `reference/` 内容、答案键、评分脚本或 `PACKAGE.json` 的 evaluator 字段，报 `PKG_AGENT_VIEW_LEAK` 阻断。

`PACKAGE.json` 放版本层是默认隔离手段；放 `base/` 时必须证明挂载器不会把整个 `base/` 暴露给 Agent。这个证明是 P12 的一部分，不是文档承诺。

## 13.8 哈希候选与 PoC

`tools/wave2/hash_poc.py` 用标准库构造一个临时包，连续构建两次并检查七项。当前结果全部通过，明细在 `docs/data/wave2-hash-poc-results.csv`。

候选定义：

- `native_hash` 覆盖 `base/` 内容文件的规范清单，按 `path` 排序，每项含 `path`、`bytes`、`mode`、`role`、`sha256`。不覆盖 `PACKAGE.json`、`validation_report.json`、`SHA256SUMS`。
- `package_hash` 覆盖 `native_hash`、`PACKAGE.json` 的稳定字段投影、四个边车的哈希。稳定字段投影排除 `built_at`、`built_by`、`package_hash`、`hashes`。`validation_report.json` 不进哈希。
- 入库回执哈希覆盖 `package_hash`、校验报告哈希、接收时间、接收人，只写数据库，不写包内文件。

PoC 证明了三件事。第一，`native_hash` 在两次不同构建时钟下相同，改一个字节就变化。第二，`package_hash` 在排除动态字段后稳定，改 `verification.mode` 就变化。第三，如果把 `package_hash` 写回被哈希的字节，第二次计算会得到不同摘要，自引用成立。另一个测试显示，边车里放构建时钟也会让 `package_hash` 漂移。

因此当前只把哈希称为候选。`PACKAGE.json` 不写 `package_hash`；哈希存数据库和入库回执。`built_at` 与 `built_by` 不进入稳定投影。边车字节不得包含构建时钟，或时钟必须由冻结快照派生。P12 通过前，平台不得对外宣称哈希合同已冻结。

## 13.9 校验与测试

`schemas/ale-package.schema.json` 是 `PACKAGE.json` 的草案结构。它要求 `files[]`、`hashes.native_hash`、`license`、`pii`、`provenance`、`oracle`、`verification` 等字段，并禁止绝对路径。它不是最终合同，字段仍可能随 P12 调整。

导入矩阵的测试用例按阻塞码分组：`IMP-BASE`、`IMP-NAMED`、`IMP-NOBRIEF`、`IMP-NOSOFT`、`IMP-NOREF`、`IMP-LARGE`、`IMP-SYMLINK`。每个用例至少检查一条真实官方路径，导入器不得只跑合成样例。

PoC 还缺三项：真实挂载器的 Agent 视图测试、122 条全量导入回归、官方包与平台包的双向重建。前两项放到 P12 和 P13，第三项依赖工程侧确认运行包格式。

## 13.10 未决问题

- 五组核心 41 个必填叶子是否在首批试点前冻结，仍需负责人确认。
- `PACKAGE.json` 放版本层还是 `base/`，由 P12 的挂载测试决定。
- `package_hash` 是否只存数据库，还是允许写进入库回执文件，需与审计链一起定。
- 官方导入的 `source_variant` 是否进入 ALE-data 包元数据，还是只留平台数据库。
- 16 条无 software、2 条无 reference 的官方任务是否进入 500 条之外的回归集。
- 许可元数据在官方包没有独立位置，导出后可能丢失；平台边车能否被合作方接受还未验证。
- `contract.kind` 与 `verification.mode` 的组合是否存在无法表达的官方案例，需 B 线验证器给出反例。

## 13.11 证据与复现

字段来源：`docs/10-expert-annotation-spec-v0.md` 的十块与 94 字段、`docs/12-wave1-integration.md` 的 Canonical 表、`docs/data/wave1-canonical-task-source.csv` 的 112 行。

官方结构证据：`inputs/frozen/03_ale-data/archive/selected-members.jsonl` 的 79,494 条路径、`archive/release-v1.1.json` 的 122 条任务与 79,494 个成员、`stages/s0-baseline/04_task_inventory.csv` 的 122 行库存。

复现命令：

```bash
python3 tools/wave2/hash_poc.py
python3 -c "import json; json.load(open('schemas/canonical-task-source.schema.json')); json.load(open('schemas/ale-package.schema.json'))"
python3 tools/check_docs.py
```

版本记录：v1 初稿，2026-11-14。哈希与包布局为候选，等待 P12。
