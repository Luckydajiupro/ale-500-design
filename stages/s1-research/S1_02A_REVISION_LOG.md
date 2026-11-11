# S1-02A 独立评审后定向修订日志

修订对象：S1-02A 第一轮 51 个候选工作流（3 个首批领域 = 14 个子领域）。
修订依据：独立评审结论——结构化方法可用，但工作流证据 / 跨领域重复 / 软件替代方案需修订；原 13 项自动校验未被独立复核。

本日志按评审要求的 7 项修订任务逐项记录 PASS / FAIL / UNKNOWN，并附未验证项清单。

证据等级：E1=本轮直接观察（全文已读）、E2=引自 S1-01/R1（待复审）、E3=行业公开资料（可追溯 URL）、E4=项目推断（须专家确认）、U=未知。
证据类型（4 分类）：industry_standard_complete=行业标准直接证明的完整工作流 / tool_existence=仅证明工具存在或具备功能 / agent_inferred_combination=LLM 组合推断 / expert_pending_proposal=待专家确认提案。

---

## 修订任务 1：51 个候选证据逐项复核

**状态：PASS**

将原 `source_type=industry_supported` 的 46 项逐项复核，按"证据究竟证明了什么"重新归为 4 类：

| 证据类型 | 数量 | 说明 |
|---|---|---|
| industry_standard_complete | 34 | 非供应商来源直接记录完整 输入→操作→产物→成功标准 工作流 |
| tool_existence | 11 | 来源是供应商文档/博客或政府工具页，仅证明**工具存在**，不证明完整工作流 |
| agent_inferred_combination | 2 | 无单一来源记录完整工作流，由 LLM 组合步骤知识推断 |
| expert_pending_proposal | 4 | 无来源，LLM 假设，须专家确认（原 E4） |

**关键修订：13 项原 `industry_supported` 被降级**（11 → tool_existence，2 → agent_inferred_combination），因为其来源是供应商营销页、政府工具页或仅引用条目，不能作为"行业标准完整工作流"的证据。

被降级为 tool_existence 的 11 项：
`eng_electronics_wf01`（Altium）、`eng_civilgeo_wf02`（HEC-RAS 工具页）、`eng_manufacturing_wf01`（3d-scantech 博客）、`eng_manufacturing_wf02`（Flowfuse 博客，非 SPC 供应商）、`eng_robotics_wf02`（MoveIt 教程）、`legal_litigation_wf02`（Everlaw）、`legal_litigation_wf03`（Lighthouse/Everlaw）、`ag_envwater_wf01`（EPA SWMM 页）、`ag_envwater_wf02`（USGS MODFLOW 页）、`ag_envwater_wf03`（HEC-RAS 手册）、`ag_envwater_wf04`（EPA EPANET 页）。

被降级为 agent_inferred_combination 的 2 项：
`eng_electronics_wf03`（passive-components 片段，仅覆盖电感选择）、`eng_urban_wf02`（仅 Google Scholar 引用条目，无内容）。

4 项 expert_pending_proposal（原 E4，无来源，须专家确认）：
`eng_aerospace_wf03`（GD&T 公差叠加）、`eng_energypower_wf03`（建筑 M&V ASHRAE G14）、`eng_semiconductor_wf03`（DFT/ATPG）、`eng_urban_wf03`（四步出行需求模型）。

**可追溯来源与证据等级逐项映射**见 `S1_02A_SOURCE_CLAIM_MAP.csv`（51 行，含 source_url / source_category / evidence_kind / evidence_level / software_adaptation / correction_note）。

---

## 修订任务 2：跨领域重复（3 组裁定）

**状态：PASS（裁定完成，待专家确认）**

3 组重复对均已完成裁定（唯一主归属 + 次级标签 + 差异依据 + 待确认项），**未删除任何覆盖方向**。详见 `S1_02A_DUPLICATE_ATTRIBUTION.md` 与 `S1_02A_DUPLICATE_ATTRIBUTION.csv`。

| 重复对 | 裁定主归属 | 次级处理 |
|---|---|---|
| HEC-RAS 洪水（civil_geo vs env_water） | env_water | civil_geo 重标为"桥涵/堤防水力设计" |
| EPANET 配水（civil_geo vs env_water） | env_water | civil_geo 重标为"新建管网设计" |
| DFT 扫描/ATPG（electronics vs semiconductor） | semiconductor | electronics 归属错误，重归属或重构为板级 JTAG |

---

## 修订任务 3：软件环境纠偏

**状态：PASS**

4 项关键纠偏（详见 `S1_02A_SOURCE_CLAIM_MAP.csv` 的 correction_note）：

1. **HEC-RAS**：官方仅 Windows（Intel PC）GUI + 64 位计算引擎，**无官方 Linux 原生版**。Linux/无头运行是第三方方案（Docker `rascommander/hec-ras-linux-unsteady_6.6`、Apptainer/Slurm），只跑 2D 非恒定流计算引擎，无 Windows GUI。
2. **Minitab**：Windows 桌面版 + Web App（浏览器），**非 Linux 原生**。
3. **OpenROAD DFT**：有 `src/dft` 扫描插入，但**没有生产级 ATPG**。"Synthesis 有 Yosys，布局布线有 OpenROAD，DFT 什么都没有"（WIOWIZ，开源芯片设计 DFT 缺口）。开源 ATPG（TestVector/Atalanta/Quaigh）**不是** TetraMAX/TestMAX 的已验证完整等价物。
4. **EPANET ≠ HEC-RAS**：EPANET 是承压配水管网（需求驱动，节点/泵/水箱），HEC-RAS 是明渠河流/洪水（重力驱动）。物理不同，**不能互相替代**。

---

## 修订任务 4：软件适配 5 状态分类

**状态：PASS**

对 51 个候选的主依赖软件逐一归类为 5 状态（结果见 `S1_02A_SOURCE_CLAIM_MAP.csv` 的 software_adaptation 列）：

| 适配状态 | 数量 | 含义 |
|---|---|---|
| native（原生支持） | 30 | 目标平台（Linux 自动化）可直接运行 |
| partial_function_replacement（部分功能替代） | 15 | 开源替代只覆盖部分功能，非完整等价 |
| conditional（条件支持） | 4 | 需注册/许可证或仅第三方间接运行 |
| unverified_or_unavailable（未验证/不可用） | 2 | 无验证等价物（OpenROAD ATPG、开源 ATPG） |
| needs_task_redesign（需重设计任务） | 0 | 本轮无触发 |

关键：**"存在开源工具"不等于"工程验证已通过"**。15 项 partial_function_replacement 和 2 项 unverified_or_unavailable 均须在任务工程化前逐项验证功能等价性。

---

## 修订任务 5：3 个缺 E1 子领域的证据补充

**状态：PASS（3/3 子领域均已补充 E1）**

| 子领域 | 状态 |
|---|---|
| chemical_process | **已升级**：`eng_chemproc_wf03`（PFD/P&ID 开发）由 E4→E1。来源 = UBC/BCcampus OER 教材（LibreTexts，"Foundations of Chemical and Biological Engineering I"，CC BY-NC-SA），§1.5–§1.8 完整记录 框图→物料衡算→PFD→P&ID 流程，§1.8"Building a PFD"练习即文字描述→图 的完整任务。 |
| precision_agriculture | **已升级（4/4）**：`ag_precision_wf01`（McGill Manifold Lesson 3 + Cornell #107 + Nebraska EC2005，产量清理→延迟校正→滤波→插值→分类→制图）、`ag_precision_wf02`（Javadi 等 Sensors 2022，CaSP 聚类流程）、`ag_precision_wf03`（McGill Manifold Lesson 5 + ArcGIS Pro 教程，处方图开发）、`ag_precision_wf04`（Win 等 Crop Science 2023，APSIM 校准验证）均 E3→E1（本轮全文已读）。 |
| mining_petroleum | **已升级（5/5）**：`eng_mining_wf01`（whitson+ DCA 手册，Arps 递减→EUR）、`eng_mining_wf02`（whitson+ RTA 手册，物质平衡时间→Bourdet 导数→流态识别）、`eng_mining_wf03`（Carlson 手册，Lerchs-Grossmann 13 步 + 生产排程）、`eng_mining_wf04`（GeoEngineer Bishop 条分法；注意 M-P 变体未具名覆盖）、`eng_mining_wf05`（BRGM/GFZ 压裂设计培训教材）均 E3→E1（本轮全文已读）。 |

---

## 修订任务 6：任务粒度检查

**状态：PASS（无排除，记录 N 项标注）**

对 51 项逐项复核"输入→操作→产物→成功标准"：

- **无**明显单步操作候选（所有 51 项均为多步完整工作流）。
- **无**简单参数替换候选（无"仅换参数"的同质任务）。
- **主产品无法客观验证**的候选共 3 项（法律领域，产物含主观判断，需专家评分作为验证设计，保留但标注）：
  - `legal_litigation_wf04`（证人准备，证词大纲实质主观）
  - `legal_research_wf01`（IRAC 备忘录，实质需专家评分）
  - `legal_research_wf03`（法条解释，结论可争辩）
- **窄单分析工作流** 2 项（保留但标注为窄）：
  - `eng_manufacturing_wf02`（SPC 控制图，单分析）
  - `legal_research_wf04`（引证器查证，单工具）
- **跨领域粒度重叠** 1 组（保留双方，记录差异依据）：`eng_manufacturing_wf03`（生产侧 Cp/Cpk + 公差叠加）vs `eng_aerospace_wf03`（设计侧 GD&T 公差叠加）。

**未为了凑数添加任何任务，未删除任何候选**；原始记录与修订理由均保留。

---

## 修订任务 7：校验扩展（负例校验）

**状态：PASS**

在原有 13 项计数/结构校验（`scripts/10_validate.py`，C1–C13 全 PASS）之外，新增 5 项负例校验（`scripts/12_validate_revision.py`）：

| 校验 | 内容 | 结果 |
|---|---|---|
| N1 missing evidence | 非 E4 候选必须有可追溯来源 URL；E4 候选必须标 expert_pending_proposal | PASS |
| N2 wrong attribution | scan/ATPG 归属 semiconductor（IC 级），eng_electronics_wf02 标错归属 | PASS |
| N3 duplicate candidates | 3 组重复对均有实质裁定 | PASS |
| N4 wrong environment | HEC-RAS=conditional、Minitab 非 Linux 原生、OpenROAD/ATPG=unverified | PASS |
| N5 unsupported equivalence | 无 EPANET=HEC-RAS 或开源 ATPG=商业 ATPG 声明 | PASS |

**重跑结果：`scripts/10_validate.py` 全 PASS，`scripts/12_validate_revision.py` 全 PASS（N1–N5）。**

---

## 未验证项清单（须专家确认或后续验证）

1. 4 项 expert_pending_proposal 候选（`eng_aerospace_wf03`、`eng_energypower_wf03`、`eng_semiconductor_wf03`、`eng_urban_wf03`）——工作流本身待专家确认。
2. 3 组重复裁定的"主/次归属"边界——项目推断（E4），须专家确认。
3. 15 项 partial_function_replacement 的开源替代功能等价性——须逐项工程验证（非"存在即通过"）。
4. 2 项 unverified_or_unavailable（OpenROAD/开源 ATPG）——无验证等价物。
5. `eng_mining_wf04` 的 Morgenstern-Price 变体：E1 来源仅覆盖 Bishop 条分法；M-P（广义版）需单独证据（候选标题含 "Bishop/Morgenstern-Price"）。
6. 3 项法律候选的主产品主观性——需专家评分验证设计。
7. `eng_mining_wf01/wf02/wf03` 的 E1 来源为供应商手册（whitson+ ×2、Carlson ×1）：Arps DCA / RTA / Lerchs-Grossmann 是教科书行业标准，手册完整记录了工作流（非仅工具特性），故归 industry_standard_complete；但来源性质是 vendor_doc，供评审复核。

---

## 结论与是否进入 S1-02B

- 修订任务 1/2/3/4/5/6/7 全部完成（PASS）。证据等级分布：E1=24、E3=23、E4=4（4 项 expert_pending_proposal 待专家确认）。
- **不自证最终验收通过**。本轮修订是否满足独立评审要求，须由评审复核后判定。
- 是否进入 S1-02B（扩展其余 9 个正式领域）：**待独立评审对本次修订复核后再决定**。
