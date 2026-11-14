# 14 验证描述与工程交接合同 v1

这份文件定义 ALE 500 平台向工程侧交付的验证意图合同。它说明任务怎样判定成功、需要哪些验证工件、哪些工件对 Agent 隐藏、评分是否允许部分分，以及工程侧 Verifier 或 Judge 接收合同时要确认的字段。它不实现正式评分器。

## 14.1 结论与边界

验证合同是平台与工程之间的接口，不是运行包，也不是评分代码。平台负责把专家填写的成功标准、参考答案说明、评分维度和证据整理成合同；工程侧按合同实现 Verifier、Judge、人工评分流程或混合方案。平台不替工程决定具体运行框架，也不替合作方做最终验收。

合同版本为 `verification-contract-1.0`。六个官方案例和两个补充场景已经映射为合同 fixture，校验器 `tools/wave2/verify_contract_check.py` 的 29 项自检全部通过。29 项包含 1 项 schema 一致性检查和 28 个正反案例。

合同只描述可验证意图。它不能证明某个 Verifier 实现正确，也不能替代真实运行。工程侧接收合同后仍需产出 Verifier 实现、样例结果和已知限制，并把这些信息写回 `handoff.verifier`。

## 14.2 合同形状

合同有十个顶层键：`schema_version`、`contract_id`、`task_id`、`contract_kind`、`mode`、`oracle`、`artifacts`、`tolerance`、`scoring`、`handoff`。`judge` 与 `human_review` 按模式出现，`notes` 可选。

| 键 | 作用 | 关键约束 |
| --- | --- | --- |
| contract_kind | 任务产物与评分族 | 五值 numeric_cases、tabular_columns、document_qa、artifact_diff、code_artifact |
| mode | 判定方式 | 五值 deterministic、rubric、judge、hybrid、human_review |
| oracle | 参考答案是否存在、属于哪类 | required=true 时必须是 independent、recomputed 或 equivalence_class |
| artifacts | 验证工件清单 | 每个工件带 role、path、visibility、in_package_hash、required |
| tolerance | 数值、几何或集合容差 | 类型七值；非 none/set_exact/structural 时 value>0 |
| scoring | 分数、部分分、硬门、passed 关系 | 权重和、critical、binary 限制、reward 与 passed 一致 |
| judge | LLM Judge 配置 | 模型族、版本策略、答案格式、校准、原始回答留存 |
| human_review | 人工评分配置 | 至少两名评审、裁决、盲评、批准引用 |
| handoff | 平台到工程的交接状态 | draft、exported、accepted、rejected、registered |

`contract_id` 用 `VC-` 前缀加任务短标识。`handoff_id` 用 `HO-` 前缀。两个 ID 都在平台侧生成，工程侧只读。

## 14.3 五种验证模式

`deterministic` 用于有独立参考答案或可重算 oracle 的任务。评分脚本、几何比较、集合相等、数值容差都属于这一类。它不能出现 `judge` 或 `human_rubric` channel。

`rubric` 用于没有唯一答案、但有明确评分维度和样例的任务。它必须有人工评分 channel，必须有 rubric、合格样例和反例，不能出现 judge。

`judge` 用于需要视觉、文档或专业语义判断的任务。它必须有 judge 配置、校准样本、重复运行和原始回答留存。judge 不能单独决定高风险任务，必须有抽检或人工复核。

`hybrid` 用于确定性检查和语义判断都要用的任务。它至少有两个 channel，至少一个确定性 channel，至少一个 judge、human_rubric、declared_output 或 render_compare。`scoring.composition` 必须是 weighted_sum、gate_then_weighted 或 sequential。

`human_review` 用于专业判断为主、自动评分不可靠的任务。它至少两名评审，支持盲评和第三人裁决。它必须有人工评分 channel 和 rubric，不能出现 judge。

## 14.4 六案例映射

| 案例 | contract_kind | mode | oracle | 关键验证事实 |
| --- | --- | --- | --- | --- |
| C1 equity | tabular_columns | deterministic | independent | 43 个检查项，按通过占比给分，全对才 1.0 |
| C2 taxform | numeric_cases | deterministic | equivalence_class | 主答案与替代答案两通道，金额 0.01 容差 |
| C3 scene2 | artifact_diff | hybrid | recomputed | 0.7 重算统计加 0.3 CSV，截图像素不比较 |
| C4 building | artifact_diff | judge | independent | 1 mm 几何硬门加 8 问 Judge，score=yes/8 |
| C5 chisel | code_artifact | deterministic | independent | 0.1 格式加 0.1 目标信号加 0.8 集合相等 |
| C6 legal | document_qa | deterministic | independent | 15 个金额、7/7/6 权重、0.01 容差 |

补充两个场景。V7 是 `human_review` 加 `rubric_only`，演示无唯一参考解时的审批路径。V8 是 `numeric_cases` 加 `equivalence_class`，演示主答案与替代答案双通道。

## 14.5 Oracle 与多答案

`oracle.required=true` 时，合同必须给出 oracle 类型与理由，并且工件中至少有一个 oracle、answer_key 或 reference_render。`independent_oracle` 表示参考答案独立于提交件；`recomputed_oracle` 表示从输入重算；`equivalence_class` 表示多个可接受答案，需要至少两个 channel 和 answer_key。

`oracle.required=false` 只在三种情况下合法：没有唯一参考解、rubric 为主、视觉参考族。此时必须有 `approved_without_reference=true` 和 `approval_ref`。`deterministic` 模式不能走这条路径。

C2 和 V8 使用主答案加替代答案。C2 的官方页面印 15,750，主答案键用 15,000，替代答案键用 15,750、36,700、4,165.50 等十个字段。合同把两条通道都写成合法等价类，评分器按主通道优先、替代通道兜底。这个案例证明多答案通道不是理论选项，而是官方已经出现的评分事实。

## 14.6 工件与可见性

工件角色十值：oracle、rubric、judge_config、fixture、reference_render、answer_key、output_contract、verifier、sample_good、sample_bad。每个工件带 `path`、`visibility`、`in_package_hash`、`required`。

oracle、rubric、judge_config、reference_render、answer_key、sample_good、sample_bad 必须是 `evaluator_only`。`verifier` 必须是 `platform_only`，且不能进入包哈希。`agent_visible` 路径不得以 `reference/` 开头，防止参考答案或评分依据被 Agent 读取。

`in_package_hash=true` 的工件必须有 64 位 sha256。工程侧 Verifier 不在包哈希内，因为它是运行侧实现，不是任务资料。任务资料的哈希与 Verifier 的哈希分开记录。

## 14.7 容差与评分

容差类型七值。数值任务用 absolute、relative、decimal；表格任务加 structural；几何任务用 geometric；集合任务用 set_exact；不需要容差时用 none。`artifact_diff` 的 deterministic 或 hybrid 不能用 none，否则几何或渲染比较没有判定标准。

评分的 `reward` 可以是 `score` 或 `passed`。如果 reward 是 score，`passed.is_reward` 必须为 false；如果 reward 是 passed，必须为 true。C1 的 reward 是 score，按 43 项通过占比给分；C4 的 reward 也是 score，按 8 个 Judge 问题的 yes 占比给分。`passed` 只是报告字段，不能替代分数。

`partial_credit=true` 时至少两个组件，权重和等于 `weights_total`，至少一个 critical。`partial_credit=false` 时必须是 binary，只允许一个权重 100 的组件。硬门至少一个，每个硬门带 `gate_id`、`condition`、`enforced_by`、`on_fail`、`evidence`。硬门失败可以是 0 分、拒收或任务失败，不能只写在说明文字里。

## 14.8 Judge 与人工评分

Judge 合同必须有模型族、版本策略、答案格式、校准。版本策略二值 pinned 或 rolling_with_record；rolling 必须记录每次模型版本。答案格式三值 YES_NO、LIKERT、JSON。校准必须有样本集引用、一致性阈值、人工复核比例、重复运行次数，且至少两次运行、留存原始回答。

C4 使用 YES_NO 八问，阈值 0.5，score 是 yes 占比。工程侧实现 Judge 时必须保留每次问题的原始回答，不能只留汇总分。Judge 的模型版本变化要记录，否则历史分数不可复现。

人工评分合同至少两名评审，支持盲评和第三人裁决。V7 演示 rubric 为主、无唯一参考解的路径。人工评分的一致性、抽样比例和返修流程由平台审核模块承载，合同只记录最低要求。

## 14.9 工程交接

`handoff.status` 五值。`draft` 是平台内部草稿；`exported` 表示合同已导出给工程；`accepted` 表示工程确认接收；`rejected` 表示工程拒绝，需要写拒绝理由；`registered` 表示 Verifier 已登记并可运行。

`handoff.verifier` 记录 Verifier 的标识、版本、sha256、运行时、入口、已知限制和样例结果。`registered` 时前六项必须非空，样例结果至少一条，`accepted_at` 必须存在。这样平台能追溯某个任务版本由哪个 Verifier 实现、在什么运行时、有哪些已知限制。

平台不把 `handoff.verifier` 写进 ALE-data 包哈希。它属于运行侧登记，不属于任务资料。工程侧接收合同后，先实现 Verifier，再用样例跑通，最后登记 `registered`。登记前任务只能算生产完成，不能算运行验证完成。

## 14.10 校验与测试

`tools/wave2/verify_contract_check.py` 有两个入口。`--check` 校验单个合同或 bundle；`--selftest` 跑 28 个正反案例并写 `docs/data/wave2-verifier-poc-results.csv`。

正向案例覆盖六个官方任务和两个补充场景。负向案例覆盖缺字段、坏枚举、坏角色、绝对路径、路径穿越、确定性无 oracle、oracle 未审批、Judge 无 rubric、Judge 未校准、硬门缺失、硬门执行者不明、答案泄漏、Verifier 进哈希、权重不等于 100、reward 与 passed 不一致、handoff registered 缺字段、rubric 缺反例、数值任务无容差、Judge channel 无 Judge。

自检结果 29 项全过。这个数字是脚本输出，不是人工判断。它证明合同形状和规则自洽，不证明工程侧 Verifier 已经实现。

## 14.11 与包合同的关系

A 线的包合同管文件、角色、哈希和可见性。B 线的验证合同管验证意图、工件角色、评分与交接。两个合同通过 `artifacts[].path`、`visibility`、`in_package_hash` 对齐。

包合同里的 `verification.mode` 与 `verification.artifacts[]` 是验证合同的摘要。完整验证合同以 `contract_id` 关联到任务版本，不塞进 `PACKAGE.json` 的必填字段。这样包格式保持稳定，验证细节可以独立演进。

## 14.12 未决事项

1. `human_rubric` 的审批人、样例数量和一致性阈值，需要首批试点校准。
2. Judge 的模型族与版本策略尚未确定，工程侧只能先按 pinned 设计。
3. 六案例之外的专业判断任务怎样选 rubric 维度，需要领域评审参与。
4. `handoff.verifier` 的登记入口、权限和回滚规则，由 C 线平台骨架承载。
5. 官方两个无 reference 任务的 `approved_without_reference` 签字人，需要负责人确认。
6. 验证合同与包哈希的关联方式，需要 P12 与 A 线共同确认。

## 14.13 证据与复现

复现命令：

```bash
python3 tools/wave2/verify_contract_check.py --selftest
python3 tools/wave2/verify_contract_check.py --check tools/wave2/fixtures/c4-building-judge.json
python3 -m json.tool schemas/verification-contract.schema.json
```

案例事实来自 `docs/09-official-task-cases.md` 与 wave1 证据表。合同规则来自 `tools/wave2/verify_contract_check.py` 的常量与校验函数。映射表在 `docs/data/wave2-verification-map.csv`，工件表在 `docs/data/wave2-verification-artifacts.csv`。

## 14.14 版本记录

v1 草案，2026-11-14。首版定义十键合同、五种模式、十种工件角色、七种容差、Judge 校准和五态交接。29 项自检通过。未冻结 Judge 模型、人工评分阈值和工程侧登记流程。
