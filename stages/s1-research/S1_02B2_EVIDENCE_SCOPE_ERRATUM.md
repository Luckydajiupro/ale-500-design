# S1-02B2 证据范围勘误（S1-02B2 EVIDENCE SCOPE ERRATUM）

- 批次：S1-02B2-effective（有效候选维护批次）
- 生成日期：2026-11-10（Asia/Taipei）
- 修订：r2（2026-11-10）口径修正。source_support_mode 改为独立证据支持状态词汇；未校正行不再复制 software_adaptation
- 只读输入：`S1_02B2_WORKFLOW_CANDIDATES.csv`、`S1_02B2_SOURCE_CLAIM_MAP.csv`、`S1_02B2_DUPLICATE_ATTRIBUTION.csv`、`.audit/s1-02b2.tsv`
- 新增文件：`S1_02B2_EFFECTIVE_CANDIDATES.csv`、本勘误、`scripts/26_b2_effective_generate.py`、`scripts/27_b2_effective_validate.py`、`scripts/b2_effective_corrections_spec.json`
- 数据来源：勘误规格为单一事实源，生成器 26 与校验器 27 同源消费；本勘误逐字复述规格中的 scope 与变更原因（校验器 V12 强制，防文档漂移）

## 目的与范围

对 S1-02B2 成品中五条候选的证据范围进行校正或拆分，并把校正结果写入 EFFECTIVE 视图与本勘误，不覆盖任何历史文件。原 CSV 中记录的 evidence_level、evidence_kind、software_adaptation 等全部 39 列保持原值不变；原始 E1/E3 记录原样保留于原列。校正仅体现于 EFFECTIVE CSV 新增的四列与本文档。

## 新增列定义

| 列 | 取值与语义 | 默认约定 |
| --- | --- | --- |
| `source_support_mode` | 校正后整体证据支持状态。枚举 `recorded_full_support`、`recorded_partial_support`、`verified_support`、`conditional_support`、`name_reference_support`、`uncited_support`、`judgment_support`、`unspecified_support`（七值，与 software_adaptation 三值令牌不相交）。未校正行按冻结 `evidence_level` 映射（E1 记 recorded_full_support，E3 记 recorded_partial_support）；校正行取全部证据块中最弱块的映射值 | 永不复制 `software_adaptation`，也不使用其词汇 |
| `evidence_scope` | 分号连接的证据块枚举，每块形如 `块名=模式_等级(验证状态)`。块名与 B2 冻结行的工作流步骤对应 | 未校正行为 `whole_workflow=as_recorded` |
| `workflow_family_id` | 逗号连接的工作流族标识（`fc_` 前缀）。拆分后的候选按证据块所在的专业工作流族登记 | 未校正行为空，表示未登记族系 |
| `process_incident` | 过程事件引用，`none` 或以 `inc:` 前缀引用审计轨迹中的生成过程事件 | 未发生登记事件的候选为 `none` |

语义边界：`software_adaptation` 表示工具与环境适配态，`source_support_mode` 表示来源证据对该工作流的支持状态，二者是不同维度，词汇令牌互不相交。校验器 27 的 V10 强制该边界（枚举不相交、每行两值不相等、校正行总体值等于最弱块映射值、未校正 E3 行不得显示完整支持）。此前版本允许未校正行复制 software_adaptation，导致 14 条 E3 行显示为 native 完整原生证据，属已废止的口径错误（见修订日志 r1/r2）。

## 五条候选勘误

### 1. psy_comp_wf01（comp_neuro，BIDS 数据集管理与 fMRIPrep 预处理流水线）

原记录（冻结值）：`evidence_level=E1`、`evidence_kind=industry_standard_complete`、`software_adaptation=native`、主来源 BIDS 规范简介页（验证 200）。

发现的问题：行内声称 E1 覆盖 6 步全流程，但主来源只是 BIDS 规范。operations 中点名的 DICOM 转换工具（heudiconv/dcm2niix）与其文档在 `source_reference` 中零出处；组级 QC 报告（运动、配准、脑掩膜）的判定标准同样没有权威来源引用。

校正结论：拆分。有据块为 BIDS 布局与验证、fMRIPrep 预处理；无据块为 DICOM 转换与 QC。

新列取值：

```
source_support_mode = uncited_support
evidence_scope = bids_layout_validation=verified_E1(BIDS_spec_200);fmriprep_preprocessing=verified_E1(fmriprep_docs_200;esteban2019_fetch_interstitial);dicom_conversion_qc=uncited(heudiconv_dcm2niix_mriqc_absent)
workflow_family_id = fc_neuroimaging_curation,fc_mri_preprocessing
process_incident = none
```

变更原因：原行把 BIDS 规范的覆盖隐式扩展为全流程 native。校正为两个有据块加一个无据块：转换工具文档与 QC 标准的来源必须补引，在此之前整体支持模式为 uncited_support。原 recorded evidence_level=E1、evidence_kind=industry_standard_complete、software_adaptation=native 保持原值不动。

待补源：heudiconv / dcm2niix 官方文档，QC 报表面板标准出处（如 MRIQC 或等价来源）。

### 2. psy_exp_wf04（exp_psychology，PRISMA-2020 系统综述与元分析）

原记录（冻结值）：`evidence_level=E1`、`evidence_kind=industry_standard_complete`、`software_adaptation=native`、主来源 prisma-statement.org（验证 200）。

发现的问题：PRISMA 2020 是报告标准，不是统计方法标准。Page 2021 BMJ 抓取 403 仅 citation-level；风险偏倚工具版本（RoB 2 或领域专用工具）与 GRADE 方法来源均未指明；metafor/meta 仅以 R 项目主页兜底，无方法论文献。

校正结论：拆分。报告合规层有据，统计合成层待补源。

新列取值：

```
source_support_mode = conditional_support
evidence_scope = sysrev_reporting=verified_E1(prisma_statement_org_200);meta_analysis_methods=conditional_E1(cochrane_handbook_nav_200;page2021_403_citation_level;rob2_grade_tools_unspecified;metafor_source_absent)
workflow_family_id = fc_systematic_review_reporting,fc_meta_analysis_methods
process_incident = none
```

变更原因：原 E1 ISC 把报告合规与统计合成合并声称。校正为报告层有据、方法层待补源（RoB 2 版本、GRADE 方法出处、metafor 方法论文献）。原 evidence_level=E1 等记录保持原值不动，修正仅落入新列与勘误。

待补源：RoB 2 工具官方文档、GRADE Handbook、metafor（Viechtbauer 2010）方法论文献。

### 3. biz_cmp_wf03（compliance，FinCEN SAR 编制与电子报送）

原记录（冻结值）：`evidence_level=E1`、`evidence_kind=industry_standard_complete`、`software_adaptation=native`、主来源 FinCEN SAR 电子申报说明 PDF（已验证）。

发现的问题：E1 依据的申报说明覆盖填表规范与电子报送技术层。法定依据 31 U.S.C. 5318(g) 与 31 CFR 1020.320 仅为名称引用；五要素事实叙述（何人何时何处何事何额）与调查完整性检查属于说明文本不含盖的专业判断。行内 `pending_confirmation` 也注明 30 天起算时点需合规官确认。

校正结论：收窄。E1 范围限定为申报说明所覆盖的填报与报送技术层。

新列取值：

```
source_support_mode = judgment_support
evidence_scope = sarfiling_form_ops=verified_E1(fincen_instructions_verified);statutory_authority=name_reference(unverified_5318g_1020.320);narrative_investigation=expert_judgment(not_specified_by_instructions)
workflow_family_id = fc_regulatory_filing_operations,fc_aml_investigation_judgment
process_incident = none
```

变更原因：原 E1 evidence 的 scope 须收窄到申报说明所覆盖的填报与报送技术层；法规文本与调查叙述不属说明文本覆盖，须补验法规原文后另行支持。原记录保持原值。

待补源：31 U.S.C. 5318(g)、31 CFR 1020.320 原文验证（law.cornell.edu 或 govinfo.gov）；叙述质量标准（如机构检查手册公开章节）。

### 4. biz_mkt_wf02（sales_marketing，ICC/ESOMAR 市场研究调查项目工作流）

原记录（冻结值）：`evidence_level=E1`、`evidence_kind=industry_standard_complete`、`software_adaptation=native`、主来源 ICC/ESOMAR 准则官方页（urllib 200 重定向）。

发现的问题：仅准则落地页验证 200。行内 `pending_confirmation` 自证三条缺口：准则全文 PDF 未下载核对、最近修订版条款与旧版差异未逐条比对、会员专属附加指南未核对。行为准则规定原则与义务，不规定配额抽样、预测试、陷阱题质量控制与加权的运算规程。

校正结论：拆分。原则与治理层有据，准则文本层待核对，调查运算层准则未规定。

新列取值：

```
source_support_mode = unspecified_support
evidence_scope = conduct_governance=verified_E1(esomar_landing_200);code_text_verification=conditional_E1(full_pdf_unread;revision_diff_unchecked;member_guidance_unchecked);survey_operations=not_specified_by_code(quota_pretest_qc_weighting)
workflow_family_id = fc_market_research_conduct,fc_survey_operations_procedures
process_incident = inc:biz_b1_split_child_death_and_steer(b778e603,3f1b46b5)
```

变更原因：原 E1 ISC 把行为准则当作全流程操作标准。校正为原则与治理层有据、准则文本层待核对、调查运算层准则未规定。原记录保持原值；过程事件登记后文单独说明。

待补源：准则全文 PDF 与修订对照；配额抽样、预测试与质量控制的方法学来源（调查方法论文献）。

### 5. biz_quant_wf02（quant_finance，Deflated Sharpe 回测过拟合校正与绩效披露）

原记录（冻结值）：`evidence_level=E1`、`evidence_kind=industry_standard_complete`、`software_adaptation=native`、主来源 Bailey & López de Prado 论文作者主页 PDF（验证 200）。

发现的问题：DSR 论文对统计校正块是扎实的 verified_E1 来源。但行内把 SEC 206(4)-1 营销规则披露合规并入 E1 声称范围，而 sec.gov 对该页面 403 阻断；行内 `pending_confirmation` 自证“以规则精神表述而非条款引用”。PBO 配套论文仅为名称引用。

校正结论：拆分。统计校正块保持 verified_E1；披露合规块在规则文本验证前不得计入 E1，登记为 conditional_E1。

新列取值：

```
source_support_mode = name_reference_support
evidence_scope = dsr_psr_statistics=verified_E1(bailey_lopez_prado_pdf_200);pbo_companion=name_reference(citation_level_2017);sec_marketing_disclosure=conditional_E1(sec_gov_403_blocked;rule_spirit_only)
workflow_family_id = fc_backtest_statistical_validation,fc_performance_disclosure_compliance
process_incident = none
```

变更原因：原E1的scope被拆分：统计校正块保持verified_E1；SEC 206(4)-1披露合规块在规则文本验证前不得进入E1，登记为conditional_E1。总体源支持模式判为name_reference_support。原记录保持原值。

待补源：SEC 206(4)-1 规则全文（sec.gov 或 eCFR 镜像）；PBO 论文（2017）原文。

## 过程事件登记

biz_b1 片段六行（`biz_hr_wf01`、`biz_hr_wf02`、`biz_hr_wf03`、`biz_mkt_wf01`、`biz_mkt_wf02`、`biz_mkt_wf03`）共享同一生成过程事件：biz_b 片段子代理两度静默死亡后拆分，biz_b1 子代理 b778e603 再度死亡，改由普通子代理 3f1b46b5 承接，其先“完成”但未落盘、后经父进程 send_message 引导才写出文件（审计轨迹 `.audit/s1-02b2.tsv` 第 12 至 18 行）。六行的 `process_incident` 均登记为 `inc:biz_b1_split_child_death_and_steer(b778e603,3f1b46b5)`。其余三十三行无已登记过程事件，值为 `none`。

## 校验重跑结果

本批按要求重跑四类校验。以下为最终状态：

1. 结构校验：`scripts/24_validate_b2.py` 退出 0（V1 至 V13 加 13 条负例自测全绿，含 7 份冻结输入的 sha256 复验）。该脚本未做任何修改。
2. 来源映射校验：`scripts/27_b2_effective_validate.py` 的 V3 验证 EFFECTIVE 视图与 S1_02B2_SOURCE_CLAIM_MAP 的 candidate_id 保持 1:1。
3. 重复归属校验：`scripts/25_b2_overlap.py` 退出 0（B2xA / B2xB1 / B2xB2 三组共 0 对超阈值相似）；27 的 V4 验证重复归属表全部 B2 侧 id 在 EFFECTIVE 视图中全部可解析。
4. 负例校验：24 自带 13 条负例自测全绿；27 自带 n1 至 n8 八条负例（删行、篡改原字段值、篡改 evidence_scope、非法支持态枚举、spec id 缺失、重复 id、V10 复制探测器、V10 最弱块反例）全部按预期翻转。
5. EFFECTIVE 视图自身：27 的 V1 至 V10、V11、V12 全部通过，含 V2 逐字段字节一致（证明 39 列原值零改动）、V10 支持列与软件适配词汇两套语义互不混淆、V11 十二个冻结文件 sha256 与基线快照一致（证明零覆盖）。

过程记录：27 早期版本 V4 用 `candidates` 列按 `|` 拆分导致跨批次配对（如 legal_research_wf03 属 S1-02A）被误判为缺失。已修正为按 `pair` 列拆分并仅校验 B2 侧 id；修正前后输出均保留在本次运行中。27 在批内另修正两处：V12 改为空白归一化比较，勘误与规格的逐字匹配不因排版空格漂移失败；负例自测的探针调用由 2 参数修正为 4 参数，初版 n1–n6 会因参数不齐抛 TypeError 而非触发目标断言。有意未重跑 `21_b2_scope_matrix.py`、`23_merge_b2.py` 与 `15_*`：三者会重写冻结产出文件，即使输出字节相同也违反“不覆盖历史文件”边界；其完整性由 24 的既有校验覆盖。r2 另修正两处口径：此前 27 的编号为 V1–V9、V11、V12（无 V10），本修订补齐真正 V10；此前未校正行复制 software_adaptation 的规则已废止，改为按冻结 evidence_level 映射出 recorded_full_support 或 recorded_partial_support，14 条 E3 行不再显示为 native 完整原生证据。

## 未验证事项登记

本次批量未解决以下事项（一律不标记为已解决）：

- psy_comp_wf01：heudiconv/dcm2niix 文档、QC 面板标准来源待补引。
- psy_exp_wf04：RoB 2 版本、GRADE 方法出处、metafor 方法论文献待补引；Page 2021 全文抓取仍 403。
- biz_cmp_wf03：5318(g)/1020.320 法规原文未验证；30 天起算时点细则待合规官确认。
- biz_mkt_wf02：准则全文 PDF、修订差异、会员附加指南未核对。
- biz_quant_wf02：SEC 206(4)-1 规则全文被 sec.gov 403 阻断，未验证；PBO 2017 为名称引用。
- 39 条候选的 Linux 实际运行验证仍全部为 NOT_VERIFIED（继承自 B2，本批未改变）。
- E1 行块级校正之后，上述补源完成前其整体支持模式取最弱块值（uncited_support / conditional_support / judgment_support / unspecified_support / name_reference_support），这些状态与原始 E1 记录并存，互不覆盖。

## 修订日志

- r1（2026-11-10，首版）：生成 EFFECTIVE 视图与勘误，登记五条证据范围校正与六条 process_incident。source_support_mode 当时沿用软件适配词汇，未校正行原样复制 software_adaptation，导致 14 条 E3 行显示为 native 完整原生证据。
- r2（2026-11-10，口径修正）：source_support_mode 改为独立证据支持状态词汇（七值，与 software_adaptation 三值令牌不相交）。未校正行按冻结 evidence_level 映射（E1 记 recorded_full_support，E3 记 recorded_partial_support）；校正行取全部证据块中最弱块的映射值。27 补齐真正 V10 与负例 n7、n8，编号现为 V1–V10、V11、V12。五条证据范围校正与六条 process_incident 的实质内容保留，仅块状态词汇随语义修订更新（native_E1 改为 verified_E1，conditional 改为 conditional_E1）。冻结文件零改动（sha256 12/12 一致）。

## 边界声明

- 未覆盖任何历史文件。EFFECTIVE CSV 为新增文件，其前 39 列与 S1_02B2_WORKFLOW_CANDIDATES.csv 逐字节一致（27 的 V2 强制）。
- 原始 E1/E3 记录保持不变，变更原因在本文档逐条给出。
- 本批按要求在完成后停止，不启动 B3。