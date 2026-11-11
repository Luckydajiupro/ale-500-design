# 09 未知事项与已定决策（R2 修订）

本文件是 Phase 0 最终基线版，继承 R2 修订版（基于 R1 版 394398ef532a3e5e 的 C、D 两项定点修订）。R2 改动对照见 evidence/history-r2/CHANGELOG_R2.md，继承来源与哈希见 SOURCE_MANIFEST_FINAL.json。

证据等级沿用五级。doc 指官方文档明确说明。code 指代码或命令核实。cmd 指命令输出。inference 指结构推断。unknown 指当前无法确认。另加 prereq 指 R1 任务书确认的项目前提，它不是官方数据事实。

## 已确认前提

以下前提来自 R1 任务书，由项目负责人确认。本文件只记录，不改变。

- 最终交付 500 条专家在平台新生产并通过验收的任务。[prereq]
- 官方任务是研究与对齐参考，不自动计入 500 条交付数量。[prereq]
- 不存在"先迁移 103 条官方任务、再补 397 条"的已批准方案。[prereq]
- 当前腾讯云 Linux 服务器不能内部再虚拟化虚拟机。[prereq]
- 沙箱或运行环境 provider 与模型 provider 必须分开。[prereq]
- Windows、GPU 是否采用以及资源预算待后续确认。[prereq]
- 分工已定。平台负责专家资料采集、脱敏、Agent 辅助、校验审核和冻结交接。后端工程负责目标格式转换、运行验证、评测和交付。[prereq]
- P0-9 总体方案已采纳，共 6 项机制。具体抽样率、风险阈值、审核人数尚未冻结。[prereq]
- P1 暂不展开。[prereq]

## 待决事项

1. 转换器未随引擎发布。Harbor 与 ALE 之间的转换契约在官方文档中出现，但本快照没有转换器。转换的真实方向、由谁维护、何时交付都待定。文档原文摘录与方向复核见 07_old_new_format_comparison.md 与 evidence/engine_format_evidence.md。[doc + code] 此问题工程可继续核实事实，交付时间需负责人裁决。
2. 500 条的生产节奏与批次排产。已确认没有"103+397"方案。专家生产链路的能力与工程验证吞吐如何匹配，由负责人排产。[prereq + inference] 需负责人裁决。
3. 难度、学科、成本的分类登记位置。新 TaskConfig 没有 id、difficulty、subject、cost 这类分类字段，[metadata] 表是自由字典，可以承载任意键，但引擎不解释这些键。唯一的静态读取是 lint 查 metadata.network_justification。[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:783-800 + evidence/engine_format_evidence.md] R1 的 04 清单改为按官方 selected_tasks 分级名单补记难度及其来源，见 04 的 official_difficulty 与 difficulty_list_source 两列。分类信息放 metadata 还是放生产管线自己的登记层，待定。此问题事实部分工程可核实，位置取舍需负责人裁决。
4. Windows 是否进入首期。状态 OPEN。证据在本文件 Windows 条目与 06_runtime_provider_matrix.md。
5. 体积口径已说明，不再列为开放问题。逻辑字节求和与 du 分配块计数的差量来自稀疏与块分配。分口径数字见 evidence/sizes_scopes.tsv 与 10_phase0_summary.md 的类别资产表。[cmd]
6. 输出文件数口径。第一轮父任务文本写 13 个文件，实际文件清单为 00 到 10 共 11 个加 parse_progress.log 共 12 个。此差异在 R1 结构里不复现，原轮 12 份产物的前后 SHA256 记录在 evidence/history-r1/SOURCE_MANIFEST_R1.json。[inference]
7. Docker 例外 8 个任务的承载路径。逐条例外原因保留在 06 与 evidence/runtime_claim_audit.md。8 个任务在新引擎下的落地路径未验证，不预设必须 VM。[doc + unknown] 工程可继续核实静态事实，方案需负责人裁决。
8. GPU 3 个任务全部在 Windows 侧。是否采购 GPU 资源、GPU 如何接入 provider 待确认。GPU 任务的逐条归属以冻结 gpu 清单为准，见 evidence/gpu_cross.tsv。[cmd + doc]
9. 外部服务 13 个任务，全部在非 CS 范围。5 个 staged-local 应用需要重新宿主。6 个 online-required 任务的数据获取或校验是任务本体。2 个 public-ref 任务引用在线公开端点。分级方法与逐条依据见 06 与 04 的 external_service 列，方案未定。[cmd]
10. 变体目录映射。122 个任务在数据侧有 100 个 base 与 22 个具名变体目录，wsi_tumor_localization_1 用 center_point。旧变体到新格式单声明目录的映射规则未定。[cmd]
11. feat/tasks-v2 分支取舍。旧仓有未合并的 tasks-v2 分支预览旧到新转换。转换研究会检视它，工程可继续核实。[doc]
12. 资产命名空间拼写不一致。引擎资产默认命名空间 agents-last-exam，任务组织写法 agentslastexam。[code: 02_ale/packages/ale-run/src/ale/run/assets.py:33 与任务模板] 是否统一未定。
13. Windows 静态迁移成本。36 个 Windows 任务里 visual_media 9 个、business_finance 7 个。新引擎 Windows 镜像配方未验证，vm-windows10 是私有种子配方。[code + cmd]
14. @task-params 不存在。在输入树与引擎作者规范中均无命中，保持结论。[cmd]
15. 标题归一化。cp_test_gen_1 的 task_card.json 官方标题含 em dash 字符。R1 的 04 把原始标题与展示标题分成 original_title 与 display_title 两列。归一化只发生在展示列，官方原始标题原样保留。[code + 04]
16. 许可证据。新引擎仓与模板仓的许可证据及未确认项见 evidence/license_evidence.md。不凭文件名有无下法律结论。[unknown]

## P0-9（修订）

- P0-9 是决策编号，不是流水线阶段编号。R1 已删去第一轮把它写成阶段表的表述。[prereq]
- 已批 6 项机制。全量自动检查、专家自检、Agent 预审、风险分层人工审核、工程自动验证、项目负责人批次放行。[prereq]
- 未冻结参数。抽样率、风险阈值、审核人数。1 GiB 资产线、双审配置等都标为建议。[prereq]
- UNKNOWN 不自动落入低风险。[prereq + R1 任务书]

## 风险分层建议

以下全部是建议值，负责人校准后才生效。

- Tier A 高险建议全查。建议入口取其一。资产超过 1 GiB 的任务、GUI 40 个明确任务加 9 个 unknown、外部服务 13 个任务、GPU 3 个任务、Docker 例外 8 个任务。出口建议两名审查者加负责人认可。[suggestion]
- Tier B 域核验建议。入口是验证依赖域正确性的任务，例如临床阈值、法律引用、财务口径、标注正确性。出口建议领域专家加 Agent 复检通过。[suggestion + inference]
- Tier C 常规建议抽查。入口是其余任务。出口建议单名审查者加全自动检查全绿。[suggestion]
- gui_status 为 unknown 的 9 个任务不进入自动低风险通道。04 的 engineering_risk 与 audit_risk 两列对 unknown 且无其他重因子的行写 UNKNOWN（GUI必要性待核实），原有依据的 medium 或 high 保持并补记未知因素。9 条 unknown 全部留待复核，由数据侧清单决定，不由本文件单独分级。[suggestion + 04]

## Windows 条目

证据基座如下。

- 122 个官方任务的快照分布是 86 Linux 与 36 Windows。排除 computing_math 后是 71 Linux 与 32 Windows。[cmd]
- Windows 的 36 个任务里 visual_media 9 个最多，business_finance 7 个次之。[cmd]
- 新引擎跑 Windows 总是 VM 加 PowerShell。[code: 02_ale 引擎快照]
- 当前首期主机不能内部再虚拟化虚拟机，Windows 在首期的落地路径未验证。[prereq + unknown]
- Windows 集内有 3 个 GPU 任务。5 个 staged-local 应用任务的系统归属按逐任务记录聚合是 2 Linux（BPMN 双任务）与 3 Windows（metabase_bi_dashboard_01、odoo、taxform_4_1），不是 5 个都在 Windows。各处数字单源聚合，不手工抄写。见 04_task_inventory.csv 的 external_service 与 os 两列和 evidence/staged_local_os.tsv。[cmd]

结论如下。

- 71 个非 CS Linux 任务构成官方参考研究的候选集，这不是转换承诺，也不自动计入交付。
- 32 个 Windows 任务整体挂起。GPU 预算未提供不等于已决定没有 GPU 预算。
- 决定状态保持 OPEN。决定权在负责人，本文件不做决定。