# 10 Phase 0 汇总（R2 修订）

本文件是 Phase 0 最终基线版，继承 R2 修订版（基于 R1 版 f254372e718fa9b6），正文数字与 R2 一致。R2 改动对照见 evidence/history-r2/CHANGELOG_R2.md，继承来源与哈希见 SOURCE_MANIFEST_FINAL.json。

## 项目目标

交付 500 条专家在平台新生产并通过验收的任务。官方任务是研究与对齐参考，不自动计入 500 条交付。两条链路分开。专家生产链路产出交付任务，官方参考链路只用于对齐研究。本轮范围与边界见 evidence/history-r1/EXECUTION_BRIEF_FROM_CHAT.md，产出索引见 00_project_brief.md。

## 四条输入与关系

- 01_agents-last-exam 是旧官方公开 ALE 基准仓，HEAD 2e91edd，28,444 个文件。它承载历史格式与 v1.1 选集。[doc]
- 02_ale 是新引擎仓，HEAD 73517c2，495 个文件。task.toml 1.4+ale.1 格式的契约在这里。[code]
- 03_ale-data 是官方任务数据转储，无 git，79,070 个文件。逻辑字节总量 92,500,607,918（86.15 GiB）。其中 archive/ 39,173,454,217（36.48 GiB），task-data-v1.1/ 53,327,153,701（49.67 GiB）。[cmd: FILE_SHA256SUMS.txt 求和]
- 04_ale-tasks-base 是新任务模板仓，HEAD 492249a，105 个文件。tasks/ 下 demo 与 example_task 两个顶层分组，按 task.toml 计数 11 个任务声明目录。[cmd]

关系链。旧仓定义官方任务的历史格式与选集，是参考输入。数据转储是 v1.1 基准的输入体，是参考输入。新引擎定义目标格式与运行约束。模板仓给出目标仓库形状。专家后续生产 Canonical Task Source，内容来自专家新生产，不是官方 01 与 03 的拷贝。

## 格式版图

- 旧格式是每任务一个目录下的 main.py 加 task_card.json 双文件包，带 scripts/ 评分器。隐藏输入体在 git 之外。[doc: note 01]
- 新格式是 task.toml 加 instruction.md 加 environment 加 tests 加 solution 的目录包。schema_version 为 1.4+ale.1，只强制 schema_version 与任务名。[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:783-800]
- 新格式 TaskConfig 没有 difficulty、subject、cost 这类分类字段。[metadata] 表是自由字典，任意键都不被引擎解释，唯一静态读取是 lint 查 network_justification。分类信息登记在哪一层，由生产管线另定。[code: taskspec.py + evidence/engine_format_evidence.md]
- conversion 的真实方向、输入投递与 artifacts 的语义、metadata 的运行时解释范围都以 07_old_new_format_comparison.md 与 evidence/engine_format_evidence.md 的原文摘录为准。转换器未随引擎发布这一事实不变。[doc + code]

## 任务集口径（修订）

- 官方发布集合 full.txt 共 122 条，13 个类别目录，与任务卡集合、解包数据目录集合的差集见 evidence/set_diff_report.md。[cmd]
- 仓库内任务卡总数与 122 的关系、30 条退休与 57 条修改的说明同见该报告。[doc]
- 历史 153 口径的查证结果见该报告。153 不自动成为新的阶段阻断项。
- computing_math 排除保留为当前统计过滤条件。它与 CS 范围的对应依据记录在该报告，业务范围由负责人确认。
- R1 的 04 清单已扩展为 31 列，逐任务补官方难度及其来源、时间类型及来源、软件与插件、verifier 类型与入口、依赖阶段、工程风险、审核风险、证据位置、源文件 SHA256、当前运行状态。没有证据的写 UNKNOWN，没有运行的写 NOT_RUN，GUI 未知不再等同于无 GUI。

## 类别资产表（bytes 基准）

换算口径 1 GiB = 1073741824 bytes，1 MiB = 1048576 bytes。数据来自 FILE_SHA256SUMS.txt 逐域求和。[cmd]

| 类别 | 逻辑 bytes | 换算 |
| --- | --- | --- |
| business_finance | 1,817,537,137 | 1.69 GiB |
| computing_math | 1,475,401,155 | 1.37 GiB |
| education_info | 575,064 | 0.55 MiB |
| engineering | 1,527,073,733 | 1.42 GiB |
| health_medicine | 17,994,750,542 | 16.76 GiB |
| legal | 1,305,680 | 1.25 MiB |
| life_sciences | 15,585,631,616 | 14.51 GiB |
| other | 204,029,485 | 195 MiB |
| physical_sciences | 1,612,335,450 | 1.50 GiB |
| psychology_neuro | 10,278,407,258 | 9.57 GiB |
| social_sciences | 469,325,814 | 447 MiB |
| transport_safety | 178,376,785 | 170 MiB |
| visual_media | 2,182,403,982 | 2.03 GiB |

第一轮把最大三域写成"1.37 到 16.76 MiB"，实为 GiB 误写。上表已按 bytes 修正。最大三域是 health_medicine、life_sciences、psychology_neuro。[cmd]

最大单文件如下。[cmd: manifest]

- slicer_5.0.3_20221025.simg 8,658,481,183 bytes（8.06 GiB），属 psychology_neuro/scene2_resample。
- tumor_001.tif 3,264,779,514 bytes（3.04 GiB），属 health_medicine/wsi_tumor_localization_1。
- 137.h5 1,615,261,704 bytes（1.50 GiB），属 psychology_neuro/celegans_neuron_tracking。

du 口径约 88.1 GiB 与逻辑字节 87.63 GiB 的差量来自分配块，不是范围冲突。范围拆分见 evidence/sizes_scopes.tsv。

## 500 覆盖与官方参考

- 08 是类别覆盖矩阵草案。12 个非 CS 类别的 proposed_tasks 之和为 500，computing_math 行为 0 并标注排除。[cmd]
- 官方 103 个非 CS 任务是参考候选集，不构成迁移承诺。500 条交付全数来自专家生产链路。[prereq]

## 运行性（修订）

三层严格分开，见 06_runtime_provider_matrix.md 与 evidence/runtime_claim_audit.md。

- 旧版支持名单。官方 selected_tasks 名单与文档配方，只作候选标注。[doc]
- 新引擎代码或文档声明。docker、qemu、daytona、orchard 四个沙箱 provider 是引擎声明的能力。[code]
- 当前主机实际验证。本轮没有运行任何官方任务，全部标 NOT_RUN。[cmd]

补充事实。沙箱 provider 与模型 provider 分开。模型 provider 是 8 个字面量加 ALE_<PROVIDER>_BASE_URL 自定义端点机制。[code: config.py:156 与 .env.example] Docker 例外 8 个任务逐条保留原因，不预设必须 VM。78 个允许名单任务只是候选。GUI 标记 40 个 yes、9 个 unknown、73 个 no，非 CS 范围内 36 yes、8 unknown。外部服务 13 个全部在非 CS 范围，分级 none/staged-local/public-ref/online-required，其中 staged-local 5、online-required 6、public-ref 2。

## P0-9（修订）

P0-9 是决策编号，不是流水线阶段编号。已批 6 项机制。全量自动检查、专家自检、Agent 预审、风险分层人工审核、工程自动验证、项目负责人批次放行。抽样率、风险阈值、审核人数未冻结，相关建议见 09_unknowns_and_decisions.md。

## Windows 与 GPU

- 建议首期先不过度预设。官方 122 个任务的快照分布是 86 Linux 与 36 Windows。排除 computing_math 后，71 个非 CS Linux 任务构成官方参考研究的候选集，不是转换承诺。
- 非 CS 范围内 32 个 Windows 任务整体挂起。当前主机不能内部再虚拟化虚拟机，Windows 在新引擎是 VM 加 PowerShell 路径，落地未验证。
- 3 个 GPU 任务全在 Windows 侧。GPU 预算未提供不等于已决定没有。
- 决定状态 OPEN，由负责人裁决。完整证据见 09 的 Windows 条目与 06。

## 主要风险

- 转换器未随引擎发布，格式转换链路未经真实运行验证。[doc + unknown]
- 专家生产能力与工程验证吞吐的匹配方案未定。[unknown]
- 大资产的存储与传输成本未核算。[cmd]
- 13 个外部服务任务的重新宿主或网络策略未定。[cmd]
- Windows 挂起造成 visual_media 类别的官方参考被削弱。[cmd]
- UNKNOWN 项不自动落入低风险，风险分层参数待校准。[prereq]

## 收尾状态

Phase 0 已完成并验收通过。历史目录已归档并完成清理，归档位置是 /Users/mac/Archives/ALE-Phase0-History-20261110。analysis/phase0-final/ 是当前唯一有效基线。Phase 0 CLOSED。Phase 0 最终基线已验收，历史版本已归档，后续不再修改 Phase 0 内容。最终校验见 FINAL_VALIDATION_REPORT.md。