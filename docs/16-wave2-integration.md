# 16 第二波技术设计整合

这份文件收口第二波三条工作线：Canonical Schema 与 ALE-data 包合同、验证描述与工程交接合同、专家工作台与平台业务骨架。它说明三份合同怎样拼在一起、哪些结论已经有测试证据、哪些仍是候选、平台工程骨架在什么条件下可以进入正式开发。

## 16.1 结论摘要

第二波交付了三份可评审合同和一套可运行骨架。A 线冻结五组核心字段共 41 个必填叶子，注册 112 个字段，给出官方 122 个任务的导入矩阵和候选包哈希。B 线定义十键验证合同，覆盖六个官方案例的五种评分形态，29 项自检全部通过。C 线落成 20 张表、九态状态机、22 个 API 资源动作和 14 项骨架测试。

三份合同的分工是：Canonical 管专家写什么，Package 管文件怎样装、怎样哈希、谁能看，Verification 管怎样判定成功、工程侧接什么。平台负责把三者串成冻结、组包、校验、入库的链路；工程侧负责 Verifier 和运行；合作方负责验收。

当前可以开始平台骨架开发，但不能把候选哈希、`PACKAGE.json` 位置或 41 个字段的冻结说成最终合同。P12 与首批 30 条试点仍是这些候选的验证场。

## 16.2 三条线的交付与证据

| 线 | 主要文件 | 证据 |
| --- | --- | --- |
| A Canonical 与包合同 | `docs/13-canonical-schema-v1.md`、`schemas/canonical-task-source.schema.json`、`schemas/ale-package.schema.json`、`docs/data/wave2-field-registry.csv`、`wave2-official-compat.csv` | 112 字段、41 必填叶子、122 任务矩阵、7 项哈希 PoC 全过 |
| B 验证与交接 | `docs/14-verification-contract.md`、`schemas/verification-contract.schema.json`、`tools/wave2/verify_contract_check.py`、`tools/wave2/fixtures/` | 29 项自检全过，含六案例与两个补充场景 |
| C 平台骨架 | `docs/15-platform-architecture.md`、`platform/app/`、`platform/contracts/`、`platform/tests/test_skeleton.py` | 20 张表、九态状态机、14 项测试全过 |

A 线提交 `d3d9aa6`，B 线提交 `6e04ce4`，C 线提交 `8a2d01f`。三线从 main `f3f11b0` 分出，合并到 `docs/w2-integration` 无冲突。

## 16.3 三份合同怎样拼合

Canonical Task Source 是内容主合同。专家按十块填写，平台只冻结五组核心 41 个叶子，其余字段按版本管理。任务身份用 `<domain_code>/<task_slug>`，官方导入保留 `source_task_id` 与 `source_variant`。资料块记录路径、角色、许可、PII 和哈希。交付物块记录路径、类型和必需性。成功标准块记录维度、检查方式、权重、阈值和硬门。环境块记录操作系统、GUI、网络、软件、外部服务和 GPU。

Package overlay 是文件与分发合同。`base/` 只放 input、software、reference 三类内容，`PACKAGE.json` 和四个边车放版本层。`files[]` 记录每个文件的路径、哈希、字节数、权限位、角色和可见性。`native_hash` 覆盖 base 内容清单，`package_hash` 覆盖 native 加稳定投影与边车，入库回执再覆盖校验报告与接收信息。

Verification contract 是判定与交接合同。它把成功标准展开为 contract_kind、mode、oracle、artifacts、tolerance、scoring、judge、human_review 和 handoff。`artifacts[].path` 指向包内文件，`visibility` 决定 Agent 能否看到，`in_package_hash` 决定是否进入哈希。工程侧按合同实现 Verifier 或 Judge，登记版本、运行时、样例结果和已知限制。

三者的接缝有三处。第一处是 Canonical 的 `success_criteria` 到 Verification 的 `scoring` 与 `oracle`。第二处是 Canonical 的 `materials` 与 `deliverables` 到 Package 的 `files[]`、`role`、`visibility`。第三处是审核冻结记录到 Package 的 `provenance.json`、`handoff.json` 与入库回执。

`docs/data/wave2-common-contract.csv` 逐字段列出这三份合同的对应关系。它不新增字段，只把已有字段的归属、可见性和冻结状态写清。

## 16.4 字段冻结与版本

A 线只冻结五组核心 41 个必填叶子。这个范围是折中：足够让平台表单、包清单和验证合同稳定，又不把 112 个字段全部锁死。场景、步骤、审核、来源、交接、验证和包元数据仍可在首批 30 条中调整枚举与条件必填。

冻结不等于不可改。改字段走版本升级：Canonical 升 `schema_version`，旧版本 payload 原样保留，平台按版本读。任务提交后形成的 `task_versions` 不被回写。包与验证合同通过 `contract_id` 和 `task_version` 关联，不把完整验证合同塞进 `PACKAGE.json` 必填字段。

41 个叶子的冻结仍需要负责人确认。确认前，平台可以按当前 schema 开发表单和校验器，但不能对外宣称字段合同已最终冻结。

## 16.5 官方包与平台包

官方 `task-data-v1.1` 是 `<domain>/<task>/<variant>/{input,software,reference}` 的数据目录。122 个任务中 100 个 variant 名为 `base`，22 个是命名 variant。官方没有包级 `PACKAGE.json`，没有统一版本层，也没有统一 `package_hash` 定义。零散的 reference、stage1、source、evaluator manifest 字段互不一致。

平台包是官方 variant 布局之上的 overlay。它保留官方内容文件与相对路径，新增版本层 `PACKAGE.json`、四个边车、校验报告和哈希。官方 122 条只作回归样本，导入时补边车，不计入 500，不占编号，不进正式库。

这个区别必须在文档、数据库和对外沟通中保持一致。平台包不是官方原生格式，也不是运行包。运行包由工程侧按运行框架转换，平台不转 Harbor、不建镜像、不跑任务、不判分。

## 16.6 哈希与证据链

当前哈希是候选 `candidate-v1`，不是冻结合同。三层定义如下。

`native_hash` 覆盖 `base/` 内容文件的规范清单，每项含 path、bytes、mode、role、sha256。按路径排序后做规范 JSON 哈希。排除 `PACKAGE.json`、`validation_report.json`、`SHA256SUMS` 和任何哈希字段。

`package_hash` 覆盖 native_hash、`PACKAGE.json` 的稳定投影、四个边车的哈希。稳定投影排除 `built_at`、`built_by`、`package_hash` 和 `hashes`。推荐把 `package_hash` 只存数据库与入库回执，不写回包内。若写回包内，会形成自引用，重算摘要漂移。

入库回执哈希覆盖 `package_hash`、`validation_report` 的哈希、接收时间和接收人。它只写数据库。三段哈希形成可复算证据链：包内容、包元数据、校验报告、入库记录任何一段被改写都能被发现。

7 项 PoC 已证明候选规则在稳定重建、权限位保留、内容敏感、边车时钟敏感和自引用五方面符合预期。它没有证明跨机器、跨文件系统、跨压缩工具的一致性，也没有证明组包器与入库器已经按这个规则实现。P12 要补这两类验证。

## 16.7 Agent 可见性与隔离

Agent 只能看到 `base/input/` 中声明的输入和 `base/software/` 中声明的软件入口。`base/reference/` 在 solver 停止后才挂载。答案键、rubric、judge 配置、reference render、`PACKAGE.json` 的 reference 清单和 `materials.json` 的敏感字段都不能进入 Agent 视图。

`PACKAGE.json` 默认放版本层，不放 `base/`。若运行框架必须整体挂载包目录，L4 必须跑 agent 视图测试，确认 reference 与元数据被排除。测试未过，包不得进入 frozen。C 线已把 `PKG_AGENT_VIEW_LEAK` 写进校验码表，B 线把 artifact 的 `visibility` 写进验证合同，A 线把 `files[].visibility` 写进包 schema。三处判断必须一致。

## 16.8 审核、校验与工程的边界

| 环节 | 谁负责 | 输入 | 输出 | 不做什么 |
| --- | --- | --- | --- | --- |
| 内容审核 | 领域评审与质量审核 | 任务源、资料、验证意图 | 通过、退回、拒收、审核记录 | 不写 Docker、不实现 Verifier |
| 自动结构校验 | 平台 | 任务源、资料、包清单 | 阻断与警告 | 不判断专业价值 |
| 包校验 | 平台 | 冻结快照、包 | L1 到 L5 报告 | 不跑任务、不判分 |
| 工程转换 | 工程侧 | 包、验证合同、handoff | 运行包、Verifier、Judge | 不改专家内容、不改包哈希 |
| 运行验证 | 工程侧 | 运行包、运行环境 | 运行记录、样例结果 | 不决定验收 |
| 合作方验收 | 合作方 | 包、运行证据、审核记录 | 验收回执 | 不改生产库 |

平台自动校验只能筛掉明确不合格，不能证明任务专业合格。专业合格由领域评审签字。运行验证由工程侧完成。验收由合作方完成。生产完成是审核通过、包校验通过、入库成功；验收完成是四道门全过。两个计数器分开。

## 16.9 已有充分依据的部分

以下部分已有文件、schema、测试或官方证据支撑，可以进入开发。

1. 112 字段注册表与 41 个必填叶子的结构，有 schema 和注册表。
2. 官方 122 任务的 variant、software、reference 矩阵，有逐任务 CSV。
3. 六个官方案例到五 kind 五 mode 的映射，有 8 个正向案例与 20 个负向案例。
4. 包 overlay 的目录与文件角色，有 `ale-package.schema.json` 与 7 项哈希 PoC。
5. 九态状态机与 returned、void 旁路，有 14 项骨架测试。
6. 20 张表、资料四层、审计追加写、幂等键，有 SQLite DDL 与测试。
7. 22 个 API 资源动作与角色边界，有接口表。
8. 专家手册与内部预算分离，`docs/10` 已移出费用，`docs/07` 保留内部基线。

## 16.10 仍是候选或需要 PoC 的部分

| 项 | 当前状态 | 需要什么证据 | 归属 |
| --- | --- | --- | --- |
| P12 包哈希与自引用 | 候选 | 跨机器重建、组包器与入库器回执联调 | 平台与工程 |
| `PACKAGE.json` 位置 | 默认版本层 | agent 视图泄漏测试、运行框架挂载方式 | 平台与安全 |
| 41 字段冻结 | 待确认 | 首批 30 条表单试用、退回原因统计 | 负责人 |
| `handoff.verifier` 登记 | 设计 | 工程侧登记入口与回滚 | 工程 |
| Judge 校准 | 设计 | 样本集、一致性阈值、人工复核比例 | 领域与工程 |
| 无 reference 任务 | 设计 | 两个官方任务的审批签字 | 负责人 |
| 大资产 external_ref | 设计 | 8.66 GB 镜像与 12 GB 级资产的搬运测试 | 平台 |
| 官方 122 导入 | 设计 | 补边车后的回归导入 | 平台 |
| 22 并发 | 未测 | 压测与锁竞争 | 平台 |
| PostgreSQL | 未实现 | 迁移脚本与类型映射 | 平台 |

## 16.11 平台骨架启动条件

骨架已经能在本地跑，但正式开发要满足六项条件。

第一，Canonical v1 的 41 个叶子有负责人确认，或明确按版本兼容开发。第二，包 overlay 布局与候选哈希被 P12 接受为可测试基线。第三，验证合同 schema 与 handoff 状态被工程侧接受。第四，角色权限、数据库迁移、审计追加写和幂等键有实现方案。第五，HTTP 框架、会话机制和对象存储适配器完成选型。第六，22 并发、备份恢复和审计离线校验有测试计划。

前四项是合同与数据条件，后两项是工程条件。合同未定时可以先做 domain 与 repo 骨架，不能把 API 和数据库写死。合同稳定后，按模块推进，不必等全部技术文档写完。

## 16.12 下一波技术详细设计模块

第一批应做六个模块。

1. Canonical 任务源服务与表单渲染：字段注册表驱动表单，服务端校验，版本化 payload。
2. 包构建器：冻结快照到 overlay，生成四边车，计算候选哈希，跑 L1 到 L5，写入库回执。
3. 验证交接服务：验证合同 CRUD、artifact 可见性检查、handoff 状态机、Verifier 登记。
4. 专家工作台：任务编辑、资料上传、结构检查、提交、退回修改、Agent 建议逐字段确认。
5. 评审与审核：派单、领取、逐项结论、退回、质量审核、冻结。
6. 审计与管理：追加写审计、幂等、生产与验收计数、批次与配额看板。

运行框架、Harbor 转换、Verifier 运行时和正式评分器不在平台第一批模块内。它们属于工程侧，按 handoff 合同另行设计。

## 16.13 需要负责人裁决的事项

以下事项不是常规技术实现，不能由主会话自行决定。

1. 41 个核心字段是否在首批 30 条前冻结，还是先按版本兼容开发。
2. `PACKAGE.json` 最终放版本层、base 层还是独立不可见目录。
3. `package_hash` 是否只存数据库与回执，还是允许写回包内某个不参与哈希的位置。
4. 无唯一参考解任务的审批人、rubric 维度和人工评分阈值。
5. 官方两个无 reference 任务的 `oracle.required=false` 签字人。
6. 法律 42 条 scope_exception 是否已获合作方书面接受。内部配额口径已批准，外部接受仍需确认。
7. 客户材料能否在试点后进入生产，以及授权、脱敏、存储期限和删除承诺的最低标准。
8. Windows 宿主、GUI 任务和大资产 external_ref 是否进入最终 500，以及由谁承担成本。
9. Agent 单条成本上限与试点补贴口径。它属于内部预算，不进入专家手册。
10. 官方 122 条导入时补边车的责任人与验收标准。

运行框架在首批 30 条入库后选型，这个时点已经批准，不需要重新裁决。平台不转 Harbor、不运行、不判分的边界也已经批准。

## 16.14 不做的事

本轮不启动正式专家生产，不改已批准的配额、批次、阶段和交付责任，不修改冻结官方输入，不把官方 122 条计入 500，不把候选哈希说成最终合同，不把内部费用表交给专家，不把平台做成运行框架或评分器。

## 16.15 验证与复现

本文件的事实来自三线提交与以下命令。

```bash
python3 tools/check_docs.py
python3 tools/check_numbers.py
python3 tools/wave2/hash_poc.py
python3 tools/wave2/verify_contract_check.py --selftest
PYTHONPATH=platform python3 -m unittest discover -s platform/tests -v
```

结果：22 份文档 0 失败；24 项数字检查 0 失败；哈希 PoC 7 项全过；验证合同 29 项全过；平台测试 14 项全过。数字检查的基线是 README 与实际 `git ls-files` 一致，新增文档后由主会话统一更新。

## 16.16 版本记录

v1 草案，2026-11-14。首版收口三条线，给出三合同拼合、三处接缝、已有依据、候选清单、骨架启动条件、六个下一波模块和十项待裁决。未冻结哈希、`PACKAGE.json` 位置、41 字段和 Judge 校准。
