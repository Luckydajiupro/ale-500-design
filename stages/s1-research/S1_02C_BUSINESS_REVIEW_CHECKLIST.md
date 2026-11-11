# S1-02C 业务复审清单

版本：S1-02C-U3
整理时间：2026-11-11
状态：材料就绪，等待独立复审。不进入配额、专家人数计算、招募或平台开发。

## 0. 范围与回顾口径

- 本清单依据 S1-02C 的现有交付物整理，未重新生成 174 条候选，也未新增证据或重新访问来源。
- 174 = A 51 + B1 57 + B2 39 + B3 27。清单中所有计数以 S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv 为准。
- 边界：不把候选数、官方任务数或任务族数换算为 500 条配额；不计算专家人数。
- computing_math 保持 A/B 两套口径，原样保留自 S1-01，本轮不裁决。

## 1. 任务族与专家能力组边界

现状：

- 72 个任务族，按成员数分布：1 条 15 个、2 条 30 个、3 条 14 个、4 条 9 个、5 条 3 个、6 条 1 个。有 15 个单成员族。
- 50 个专家能力组，中位数 3，最大 8（ECG-19），单例 1 个（ECG-07）。
- 族边界不是重复裁定，靠 definition 与 boundary_exclusion 两列固定，复看点见第 5 节。

文件复审可推进：

- 抽 10 个族：中文名、英文名、定义、排除条款与成员候选的 workflow_title 是否一致。重点抽 15 个单成员族与 3 个跨批族（WF-METRO-QUALITY、WF-NUCLEAR-SAFETY、WF-RESEARCH-DATA）。
- 抽 8 个能力组：review_question 列独立核对为 50/50 全空。本轮实际抽取 ECG-19 与 ECG-07 做了内容级复查，见 S1_02C_BUSINESS_REVIEW_REPORT.md。清单中任何抽样问题均为本轮新提出的复审问题，不声称原矩阵已经提供。

必须等专家裁定：

- 15 个单成员族是否过细、72 个族是否应合并，属于专业判断而非文件检查。

## 2. 重复对照与覆盖局限

现状：

- 25 组重复对，YES 3 组、NO 22 组，涉及 45 位候选，全部标记 expert_endorsement_required=yes。
- YES 簇 3 个均在 A：DC-HYD-FLOOD、DC-HYD-DIST、DC-DFT-ATPG。
- DC-HYD-DIST 是 25 组里唯一的 HIGH 未决项。成员 eng_civilgeo_wf03（civil_geo）与 ag_envwater_wf04（env_water）同为 WF-WATER，两端都是 EPANET 水力建模。A 批重复登记 S1_02A_DUPLICATE_ATTRIBUTION.csv 原文记 primary_home=env_water（ag_envwater_wf04），secondary_tag 建议把 civil_geo 改写为“新建管网 design（管径 sizing）”。注意“新建设计 vs 既有运行”是拟议改写口径，两端原始候选工作流里并没有各自实现这一区分，原始边界按工作对象区分，写比较结论时引用 A 批登记本身而不是本清单。合并还是按拟议口径拆分，仍待专家裁定；在专家裁定前，两位候选都保留为独立候选，族内并列。

覆盖局限：

- 25 组不能推断其余候选不存在重复。它是成对对照，不是全集相似度扫描，二者分开登记。
- 129 位候选未进入任何对照，duplicate_attribution_role 为 none。
- 文件复审只能确认 25 对的裁定文本与本轮口径一致，不能把 25 对的结论外推到未对照的候选。

文件复审可推进：

- 核对 25 对与 S1_02C_CROSS_BATCH_DEDUP_REPORT.md 附录 A 一致，重点核查 DC-HYD-DIST 是否仍标 HIGH 未决，且未在文件中被写成已裁定。
- 核对 3 个 YES 簇的主归属是否来自原批次 primary_home，未在本轮被改写。
- 确认 129 位未对照候选保持 none，没有把扫描的 0 命中写成无重复证明。

必须等其他工作：

- 未对照的 129 位是否仍有近似重复，是开放问题，不属于本轮文件复审范围，也不建议现在机械扫描补课。

## 3. 三类标记的不同含义

### 3.1 padding_risk 27 条

- 27 条全部在 B3，high 9 条、medium 18 条。
- 含义是“凑数压力”而非“已凑数”。依据是 B3 九个子域恰好各 3 行，其中 3 个 uncovered_official 子域也在恰好 3 行里。
- 后续判断：按子域逐一复看第三行是否证据驱动。文件复审可做抽检，见第 5 节；成批裁定仍需专家。

### 3.2 uncovered_official_flag 22 条

- 22 = A 13 + B3 9，覆盖 chemical_process 3、mining_petroleum 5、precision_agriculture 5、aviation 3、maritime_port 3、educational_technology 3。
- 含义是官方分类存在但当前活动任务覆盖为空，不是官方任务样本，也不代表候选质量或专家能力已获验证。
- 后续判断：优先复审。文件复审可认定 22 条的分类语义；是否补官方样本或专家判断，那是另一步工作。

### 3.3 expert_endorsement_required 45 条，expert_pending 9 条

- 45 条需要专家背书，expert_pending=yes 的 9 条全部在 A，其中 6 条与背书集合重叠。
- 含义是“待背书”，不是“已背书”。缺失保持缺失，没有改写为 PASS。
- 后续判断：背书的优先级、抽样范围与最终裁决都依赖专家，尚未安排。

## 4. 证据与环境状态，不夸大

- evidence_level 是来源等级记录，不是独立复核结果。E1 共 83 条，其中 evidence_kind=industry_standard_complete 76 条，tool_existence 7 条（ag_envwater_wf01、ag_envwater_wf04、eng_electronics_wf01、eng_manufacturing_wf01、eng_manufacturing_wf02、legal_litigation_wf02、legal_litigation_wf03）。该 7 条的 source_category 为工具页或厂商文档类，只证明工具及其厂商描述存在，不等价于 industry_standard_complete 的成文标准覆盖，二者分开陈述，原始等级和候选字段不改。
- linux_not_verified 174/174，都是待验证，不用“可生产”之类的词。
- 授权 9 组与工程 7 组是字段级机械筛查，只做组内最高严重度，不是法律或工程结论。
- independent_verification_present=no 174/174，本轮也没有刷新任何一条为 yes。

## 5. 文件复审能做什么，不能做什么

文件复审可推进：

- 第 1 节命名的族或组抽样报告。
- 第 2 节命名的 DC-HYD-DIST 与 25 对照一致性核对。
- 第 3 节命名的 27 条 padding 与 22 条 uncovered 的口径核对，确认 marker 语义一致，不与重复标记混用。
- 核对 S1_01 与 A/B1/B2/B3 的历史文件在本轮未被改动。可把下方只读校验作为复读手段。

只读校验建议：

- 重跑 python3 -B scripts/35_validate_s1_02c.py 确认 15 项与 61 文件基线。
- 重跑 python3 -B scripts/36_validate_s1_02c_c16.py 确认 16 项与 uncovered 一致性。
- C13 基线 61 条在 .audit/s1-02c-baseline.sha256。

必须等专家或工程实际验证：

- 3 个 YES 簇，特别是 DC-HYD-DIST 的合并或拆分。
- B3 的 10 组非重复裁定，背书前保持 NO。
- 45 条专家背书与 9 条 expert_pending 的优先级安排。
- 174 条 Linux NOT_VERIFIED 按风险分层推进工程验证，不预设 174 次独立人工实跑。每条候选保留可追溯验证状态，共享环境或自动化验证的适用性由工程方案与实际证据决定。
- 证据链分析判断需要专家审理，文件复审不替代验证。

## 6. 数值口径与未决

- 保持 computing_math A/B 并行，不裁决。
- 候选数 174、官方任务数、任务族数 72 均不直接换算为 500 条配额。
- 难处的数据口径在 22 条 uncovered 上最明显，与 padding 27 条不是同一种标记，不能互换解释。
- 复审通过前，22 条 uncovered_official 只是分类覆盖标记。把它当官方任务样本或配额依据都属于误读。