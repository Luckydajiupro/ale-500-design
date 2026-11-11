# S1-02C 全域任务族归并与风险收敛 复核摘要

版本：S1-02C-U1，2026-11-10T22:40+08:00 起草，2026-11-11 经 S1-02C-U1 recovery（S1_02C_U1_RECOVERY_REPORT.md）落盘，2026-11-11 修订修复构建链（34 构建器改为直接从 S1_01_CATEGORY_MAPPING.csv 推导 uncovered_official，不再限 B3），2026-11-11 第三次修订修正 .audit/u2-pre 备份口径并收紧 B3 时间线表述。实质修正是 uncovered_official 从 B3 单批 9 条传播为全域 22 条，并补充 C16 校验。任务族、能力组、授权组、工程组和候选归属未变，历史文件未改。

## 1. 目标与边界

目标是把 A、B1、B2、B3 四批共 174 条研究候选放进同一套只读分析视图，回答九个问题：workflow_family_id、专家能力组、资料与授权风险组、工程环境与验证风险组、跨领域重复及主归属、证据等级与 source_support_mode 风险、uncovered_official、padding risk、Linux NOT_VERIFIED 与工程待办。

边界：不分配 500 条正式配额；不计算最终专家人数；不启动专家招募；不把候选数量、官方任务数量比例转成配额；不把 recorded_full_support 当作独立验证；不清除 UNKNOWN；不把专家背书缺失改成 PASS；不把 Linux NOT_VERIFIED 改成可生产；不修改 Phase 0 final 及 A、B1、B2、B2-effective、B3 历史文件。

## 2. 输入与基线

| 批次 | 候选数 | 输入文件 |
|---|---:|---|
| A | 51 | S1_02A_EFFECTIVE_CANDIDATES.csv（证据字段）；原件用于风险文本 |
| B1 | 57 | S1_02B1_WORKFLOW_CANDIDATES.csv |
| B2 | 39 | S1_02B2_EFFECTIVE_CANDIDATES.csv |
| B3 | 27 | S1_02B3_WORKFLOW_CANDIDATES.csv |
| 合计 | 174 | |

同时读取四批 SOURCE_CLAIM_MAP.csv、DUPLICATE_ATTRIBUTION.csv、REVIEW_SUMMARY.md，S1_02B3_OVERLAP_AND_RISKS.md，以及 .audit/s1-02b3-review-attention.md。历史基线为 61 个文件，逐文件 sha256 记录在 .audit/s1-02c-baseline.sha256；C13 复核 61/61 全部匹配。

## 3. 方法

- 任务族：按 workflow_title 的实质工作对象归入 72 个中层任务族，保留每条候选的原始 candidate_id、source_batch 和原始族字段。
- 专家能力组：50 个能力组，覆盖 13 个能力域；一条候选一个主组。
- 授权风险：9 个组，按字段做机械筛查，候选级取组内最高严重度。它是筛查标记，不是法律结论。
- 工程风险：7 个组，覆盖 Linux/环境、工具链、硬件、数据获取、验证缺口等。
- 重复：沿用四批 DUPLICATE_ATTRIBUTION 的 25 对裁定，聚成 3 个 YES 簇，并保留每对的主归属和差异依据。
- 证据：按 evidence_level、source_type、source_category、source_support_mode、evidence_scope、independent_verification_present 计算 1–6 级证据风险。

## 4. 结果总览

| 维度 | 结果 |
|---|---|
| 任务族 | 72 个；规模 1:15、2:30、3:14、4:9、5:3、6:1 |
| 跨批任务族 | 3 个：WF-METRO-QUALITY（A 4 + B1 1）、WF-NUCLEAR-SAFETY（A 1 + B1 1）、WF-RESEARCH-DATA（B1 2 主 + B2 1 次） |
| 专家能力组 | 50 个；中位数 3，最大 8（ECG-19），单例 1 个（ECG-07） |
| 重复对 | 25 对；YES 3、NO 22；50 个槽位、45 条不同候选；跨批 14 对全部 NO，批内 11 对 |
| YES 簇 | 3 个，均在 A：DC-HYD-FLOOD 主归属 ag_envwater_wf03；DC-HYD-DIST 主归属 ag_envwater_wf04（HIGH，合并未决）；DC-DFT-ATPG 主归属 eng_semiconductor_wf03 |
| 证据等级 | E1 83、E3 87、E4 4 |
| 证据风险级 | 1=14、2=57、3=12、4=72、5=15、6=4 |
| 独立验证 | independent_verification_present=no 174/174 |
| source_support_mode | not_recorded_in_batch 108、recorded_full 14、recorded_partial 25、conditional 22、judgment 1、unspecified 1、uncited 1、name_reference 2 |
| Linux NOT_VERIFIED | 174 |
| engineering_pending | 83（A 21、B1 25、B2 15、B3 22） |
| uncovered_official | 22（A 13、B3 9） |
| padding_risk | 27（B3 全部；high 9、medium 18） |
| expert_endorsement_required | 45 |
| expert_pending | 9（A） |

授权组计数：AUTH-01 27、AUTH-02 45、AUTH-03 96、AUTH-04 40、AUTH-05 40、AUTH-06 101、AUTH-07 14、AUTH-08 16、AUTH-09 1。工程组计数：ENG-01 174、ENG-02 94、ENG-03 30、ENG-04 14、ENG-05 16、ENG-06 83、ENG-07 33。

## 5. 特殊登记

### 5.1 B3 恰好 3 行的 padding 风险

B3 九个批次各恰好 3 行，合计 27 条，全部进入 padding_risk，其中 9 条 high、18 条 medium。依据是 scripts/32_validate_b3.py:122 与 .audit/s1-02b3-research-brief.md:32-33 的“恰好 3 行”筛查，以及三个 uncovered_official 子领域也落在恰好 3 行。它只表示存在凑数压力，不能证明是凑数；27 条不能直接转成配额。

### 5.2 uncovered_official 六个子领域，22 条（U1 修正）

S1_01_CATEGORY_MAPPING.csv 明确标记六个子领域 coverage_status=uncovered_official：chemical_process、mining_petroleum、precision_agriculture、aviation、maritime_port、educational_technology。逐条按 subdomain_code 回填后，A 新增 13 条（3/5/5），B3 保持 9 条（各 3），总数 22。registry 和 matrix 的 uncovered_official_count 合计均为 22。

这 22 条不自动成为 padding_risk；padding 仍是 27 条且只在 B3。uncovered_official=yes 只表示官方分类存在、当前活动任务覆盖为空，不表示官方已有任务样本，也不表示候选质量或专家能力已获验证。详细修正和 C16 见 .audit/s1-02c-uncovered-correction.md。

### 5.3 B3 时间线补记与 edu 重建

.audit/s1-02b3.tsv 的 L18–L27 时间戳是收尾补记，不是写入当值的记录，L28–L35 的 supersede 行与 L36 的文档更正行已如实登记。本节把两个结论分开。

当前产物曾通过相应校验。三片段 gate 与 scripts/32_validate_b3.py 在当前文件上重跑通过，30 gate 14/14、32 校验 14/14。这是关于产物现状的结论，成立。

历史过程时序不可完全复验。L21–L26 声明的 19:16:30–19:17:00 exit-0 运行不可复现，三个脚本在输出已存在时会失败，产物 mtime（merge 19:06:04、matrix 19:06:49、sweep 19:13:01）早于补记时间。L17 记录 edu 片段在 18:37 通过 gate，但 gate 判过的字节随后被重写（现文件 mtime 19:05:29），原始字节已不可复验。因此 B3 部分时间戳为事后补记，edu 当时通过闸门的原始字节无法复验，准确顺序保持 UNKNOWN。历史文件不改写，时间线不编造。

### 5.4 B2 空 workflow_family_id 先例

B2 有 5 条登记了原始族（biz_cmp_wf03、biz_mkt_wf02、biz_quant_wf02、psy_comp_wf01、psy_exp_wf04），34 条 workflow_family_id 为空。空值在本轮统一视图中重新归族，但保留 original_family_registration_status=unregistered_empty，不能把新归族当成原始登记。统计名为 registered_original_family_rows=32，按批为 B2 5、B3 27；不表示 B2 单独有 32 条。

### 5.5 Linux NOT_VERIFIED 与工程待办

174 条全部带 linux_not_verified，B3 的 27 条单独可见。engineering_pending 83 条，按批 A 21、B1 25、B2 15、B3 22。它们都是待验证事项，不是已通过；不能把 Linux NOT_VERIFIED 改成可生产。

### 5.6 专家背书缺失

45 条需要专家背书，9 条 expert_pending（均在 A）。缺失背书保持缺失，不改写为 PASS；B3 的 10 组非重复裁定仍待专家背书。

### 5.7 其他跨批差异

A 的 effective 文件证据等级为 E1 24、E3 23、E4 4，而 S1_02A_REVIEW_SUMMARY.md:23 记录 E1 14、E3 32、E4 5；本轮以 effective 为准，漂移只登记不修补。A 缺少 research_ethics 字段，导致 AUTH-04 在 A 为 0，这是字段盲区，不是无风险。B3 的 fc_ 代码共 72 个 token、66 个唯一值，18 行有 3 个、9 行有 2 个，说明 B3 原始族登记粒度与 A/B1/B2 不同。

## 6. 未做事项

没有分配 500 条配额；没有计算最终专家人数；没有启动招募；没有把候选数或官方任务比例转成配额；没有把 recorded_full_support 当独立验证；没有清除 UNKNOWN；没有把专家背书缺失改成 PASS；没有把 Linux NOT_VERIFIED 改成可生产；没有修改历史文件。

## 7. 校验与自测

- 构建：python3 scripts/34_build_s1_02c.py，exit 0；assignment 174、registry 72、matrix 50、auth 9、eng 7。
- 扩展校验器：python3 scripts/36_validate_s1_02c_c16.py，16 checks、0 failed、exit 0。
- C13：61/61 entries hash-match，0 unsatisfiable。
- C16：先严格检查 assignment.uncovered_official_flag 只能是 yes 或 no，再逐条比较它与 S1_01_CATEGORY_MAPPING.csv 的 coverage_status，并比对 uncovered_official_basis 是否与 flag 一致。所有 subdomain_code 在 mapping 中都有对应行，无需别名回映射。变异一个 A 候选的 yes 为 no，C16 失败。
- 自测：36 校验器 13 mutations caught（新增 maybe 与 yesterday 两个枚举负例），pristine control green；35 校验器 10 mutations caught，pristine control green。
- 原 scripts/35_validate_s1_02c.py 保持 15 项和 61 文件基线不变；C10 的 uncovered 断言从 9（B3）改到 22（A 13 + B3 9），修订记录写在 35 头部与 C10 常量处。C16 在 36_ 扩展校验器中实现，未写入 35。

## 8. 复核问题

1. 72 个任务族是否过细，是否有应合并的同族？
2. 50 个能力组的中位数 3、最大 8、单例 1 个，粒度是否可接受？
3. 只有 3 个跨批任务族，是否说明批次间工作对象重叠被低估？
4. 3 个 YES 簇中 DC-HYD-DIST 为 HIGH 且合并未决，主归属 ag_envwater_wf04 是否成立？
5. 六个 uncovered_official 子领域共 22 条，后续是否需要补官方样本或专家判断？
6. A 新增 13 条 uncovered 标记是否应进入后续抽样设计，而不是直接进入配额？
7. B3 10 组非重复裁定待专家背书，背书前是否应保持 NO？
8. 45 条需要专家背书、9 条 expert_pending，优先级如何排？
9. B2 34 条空 workflow_family_id 的先例是否应推广为统一登记规则？
10. evidence_level E1 83 但 independent_verification_present 全为 no，后续验证应如何补？

## 9. 交付物

| 文件 | 说明 |
|---|---|
| S1_02C_WORKFLOW_FAMILY_REGISTRY.csv | 72 个任务族及成员、跨批、uncovered、证据分布 |
| S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv | 174 条逐条归属、风险、证据、标记 |
| S1_02C_EXPERT_CAPABILITY_MATRIX.csv | 50 个能力组及候选、uncovered、证据分布 |
| S1_02C_AUTHORIZATION_RISK_REGISTER.csv | 9 个授权风险组 |
| S1_02C_ENGINEERING_RISK_REGISTER.csv | 7 个工程风险组 |
| S1_02C_CROSS_BATCH_DEDUP_REPORT.md | 25 对重复、3 个 YES 簇、跨批与同族分析 |
| S1_02C_REVIEW_SUMMARY.md | 本文件 |
| .audit/s1-02c-uncovered-correction.md | U1 传播修正与 C16 说明，含 u2-pre 备份口径更正 |
| S1_02C_BUSINESS_REVIEW_CHECKLIST.md | S1-02C 业务复审清单 |
| S1_02C_BUSINESS_REVIEW_REPORT.md | S1-02C 首轮业务复审报告（本轮新提出问题均以该报告为准） |
| .audit/s1-02c-fingerprints.txt | 本轮五个 CSV 的 sha256 与字节数 |

## 10. 停止状态

S1-02C-U1 已完成本轮修订，等待独立复审。不进入正式配额、专家人数计算、专家招募或平台开发。复审通过前，22 条 uncovered_official 只是分类覆盖标记，不是官方任务样本，也不是配额依据。