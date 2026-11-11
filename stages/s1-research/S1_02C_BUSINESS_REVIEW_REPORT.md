# S1-02C 首轮业务复审报告

版本：S1-02C-U6.1（U6 三处文档勘误）
整理时间：2026-11-11
状态：U5 经再次独立复审，本版按三项定向意见修正。不分配配额、不计算专家人数、不启动招募或平台开发。U4 勘误记录见第 9 节，U5 二次勘误记录见第 11 节，U6 三处文档勘误记录见第 13 节。

## 0. 口径

- 数据基线为 S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv 与 S1_02C_WORKFLOW_FAMILY_REGISTRY.csv、S1_02C_EXPERT_CAPABILITY_MATRIX.csv 的当前磁盘版本，引用时写明字段。
- 结论分三档：PASS（与事实一致）、需修订（口径或清单表述不当，但不改候选数据）、UNKNOWN（文件范围内无法得出答案）。
- 本报告的复审问题都是本轮新提出的复审问题，原矩阵 review_question 列 50/50 为空，没有现成问题可引用。
- 本报告不导出未审候选的结论。本轮抽样读的是内容，不是只读标题。

## 1. 全表口径核查

### 1.1 E1 evidence_kind 分布

- 证据：S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv 的 evidence_level 与 evidence_kind 两列。
- 计数：E1 共 83 条。其中 evidence_kind=industry_standard_complete 76 条，tool_existence 7 条（ag_envwater_wf01、ag_envwater_wf04、eng_electronics_wf01、eng_manufacturing_wf01、eng_manufacturing_wf02、legal_litigation_wf02、legal_litigation_wf03）。
- 判断：这 7 条 tool_existence 的 source_category 为 government_tool_page、vendor_doc 或 vendor_blog，只证明工具及其厂商描述存在，不等价于成文标准覆盖。此前清单把 E1 一律写成 standard-complete 是口径错误，本报告第 1.1、2 节已分开陈述。原始候选字段与等级未改。
- 影响：7 条 tool_existence 在专家画像研究中不能归入标准全覆盖样本。画像若引用这些候选，须标明工具存在证据与领域标准证据各自的支持范围。

### 1.2 专家能力矩阵 review_question 列

- 证据：S1_02C_EXPERT_CAPABILITY_MATRIX.csv，review_question 全部 50 行均为空。
- 判断：这是矩阵缺口，不是矩阵已提审。本报告第 3、4 节的问题全部是本轮新提出的复审问题，均非矩阵原本内容。
- 影响：后续专家画像研究不能把已有矩阵问题当作审前已登记的纳管基线。

## 2. 来源支持、领域专业确认、工程运行验证

这是三个不同维度的证据，分别回答不同问题。U4 把 tool_existence 的证据缺口全部归为工程侧问题，本版更正。

### 2.1 来源支持范围

- 来源支持回答一条候选有多少明确依据，取值是 source_support_mode 或 evidence_kind。S1_02C_REVIEW_SUMMARY.md 第 44 行的 source_support_mode 计数为 recorded_full 14、recorded_partial 25、conditional 22、not_recorded_in_batch 108、judgment 1、unspecified 1、uncited 1、name_reference 2，均按 S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv 计数。该计数是证据维度，与领域专业确认、工程运行验证分开看。
- 来源对工作流的支持范围是来源研究问题，按 workflow 逐项核对，不通过工程验证解决。

### 2.2 领域专业确认

- 领域专业确认回答一项专业操作或资质要求是否属实，人选是领域专家。前文 E4 提案、聚类裁决、ECG 分组等事项都归这一类。
- 专业确认不产生可用于交付的生产工程环境。

### 2.3 工程运行验证

- 工程运行验证回答给定的软件栈与官方步骤在 Linux 上能否跑通，对应 S1_02C_ENGINEERING_RISK_REGISTER 与 linux_verification_state 174/174 NOT_VERIFIED。
- tool_existence 只证明工具与厂商描述存在。它不能满足上面的工程验证，也不能满足第 2.2 节的领域专业确认。三个维度分开记录，不交叉归因。
- 影响：画像引用的 7 条 tool_existence 候选，其证据缺口不属于工程问题。来源支持范围是否足够用于画像，是来源侧问题，逐条核对后决定。

## 3. ECG 两条的内容级复查

### 3.1 ECG-19

- 涉及：S1_02C_EXPERT_CAPABILITY_MATRIX.csv 的 ECG-19 及 legal_research_wf01 至 legal_research_wf04、legal_litigation_wf01 至 legal_litigation_wf04。
- 证据：ECG-19 的 definition 为承担法律检索、权威分析与电子取证/诉讼支持，能出具法律意见或审阅决策。typical_credentials 为执业律师、法务/合规资格、e-discovery 认证。evidence_class_distribution c2=3、c4=5。
- 已确认事实：ECG-19 把法律、诉讼支持与电子取证放在一个能力组内，definition 末句是一次聚合型描述。
- 口径澄清：无任何一条候选单行声称一人覆盖全部三项。legal_research 侧候选是检索、备忘与引证核验类任务，litigation 侧候选是证据保全、审阅与证人准备类任务，单行各只覆盖自己一侧。typical_credentials 的执业律师、诉讼经验与 e-discovery 认证是潜在能力或资质线索，不写成各类任务在所有法域都必须具备的条件，也不作为硬门槛写进画像。
- 待确认：该三项是否拆为法律研究、诉讼支持、e-discovery 三组画像特征，属专家判断。若拆分，问卷按能力分问，不设单选法律专家一类。
- 影响：ECG-19 是研究用聚合。画像与研究问卷不得把该组转写为一位成员或一个必备资质包。

### 3.2 ECG-07

- 涉及：eng_energypower_wf03。ECG-07 唯一主组候选，S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv 记 evidence_level=E4、evidence_kind=expert_pending_proposal、evidence_risk_class=c6。候选字段未改。
- 已确认事实：S1_02A_EFFECTIVE_CANDIDATES.csv 该行 professional_operations 是六项，为建模、对比实测、调参、算 NMBE/CvRMSE 与归一化节能量。原始候选没有提出签署动作。
- 判断：ECG-07 definition 里能签署节能量核算是能力组提出的额外主张，不是原始候选已提出的动作。能力组定义是聚合层的表达，不能回写到候选，也不能当成该任务必然要求署名。
- 待确认：是否需要签字、由什么资质签字、签字对象是 M&V 报告还是协议，都按任务与法域逐个确认。这部分是专业与法域共同约束的问题，不在文件内能裁决。evidence 现状是只有 E4 提案级来源，签字事项在此之上没有来源。
- 影响：画像与后续任务设计不得把签署节能量核算默认为硬要求。

## 4. 两个重复对照的内容级复审

25 组重复对照中，本轮做内容级复审的是 2 对：DP-A-02 的 DC-HYD-DIST 与 DP-B3-02 的 vm_gra_wf03、edu_edt_wf03。其余 23 对不在本轮内容级复审范围。

### 4.1 DC-HYD-DIST（HIGH 未决）

- 涉及：eng_civilgeo_wf03（civil_geo）与 ag_envwater_wf04（env_water），DP-A-02。
- 证据：
  - 两端原始候选均围绕 EPANET 配水管网建模。S1_02A_EFFECTIVE_CANDIDATES.csv 中，civil_geo 侧 task_input 是带需求、控制与压力/水质服务标准的配水管网，deliverable 是校准水力模型加服务符合性评估；env_water 侧 task_input 是拓扑、需求、控制与实测压力，deliverable 是校准 EPANET 模型加消防流量、水龄与改善建议报告。
  - S1_02A_DUPLICATE_ATTRIBUTION.csv 记 substantively_duplicate=YES、primary_home=env_water（ag_envwater_wf04）、secondary_tag 建议 civil_geo 改写为新建管网设计（管径 sizing）、difference_basis 为设计语境 vs 运营语境、pending=HIGH，待专家裁决合并或拆分。
- 已确认事实：两候选原始内容均为 EPANET 水力建模。设计 vs 运营的区别是 A 批 secondary_tag 提出的拟议改写口径，不是两候选原始内容里已实现的边界。
- 来源状态分列：
  - S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv 记 eng_civilgeo_wf03=E3 industry_standard_complete（source_category=academic），ag_envwater_wf04=E1 tool_existence（source_category=government_tool_page）。E 级是来源等级记录，industry_standard_complete 与 tool_existence 是证据种类，两个不同维度。
  - civil_geo 侧 E3 是行业公开资料级，说明有一个可追溯来源存在。env_water 侧 E1 是直接观察级，证据种类为工具存在，说明 EPA EPANET 页本质是工具页，本身不构成对配水校准工作流的标准级支持。
  - A 批登记主归属理由是 env_water 有更强来源（E1 EPA page）。该理由比较的是等级与证据种类的标签，不是按工作流支持力逐项比较。本版的结论是两端各自的支持强度均待逐项核对。当前主归属记录 ag_envwater_wf04 没有被来源字段推翻，维持登记，尚不重新裁决。
- 判断：HIGH 成立。不按拟议改写把两个候选当作已分离，也不按 YES 把两者当作已合并。当前状态为保留双工作流、专家未裁定。
- 待确认：合并（env_water 为主、civil_geo 次标签）还是按设计/运营永久拆分。裁定人须给出可验收边界，而不是只投票。
- 影响：两类画像若提前分割为管网设计专家和管网运营专家，会预设一个未裁决的裁定。后续画像问卷应把两个子群分别问卷，并保留可同时做两边的选项，等待本案翻案后收敛。

### 4.2 vm_gra_wf03 与 edu_edt_wf03（同族两条候选，研究性非重复）

- 涉及：S1_02B3_WORKFLOW_CANDIDATES.csv 的 vm_gra_wf03 与 edu_edt_wf03，DP-B3-02。
- 证据：
  - 两端原始候选的输入、操作、产物、成功标准、验证方式逐项对齐。vm_gra_wf03 覆盖 40 页品牌站点加 12 份 PDF 加 3 段带对白视频，操作含对比度、替代文本、媒体替代、键盘焦点、表单错误、PDF/UA 标签与辅助技术复测；edu_edt_wf03 覆盖 12 个 HTML 页面、34 份 PDF、9 个视频、5 个交互组件，操作含扫描审计、成功准则映射、PDF 修复、字幕与音频描述、结构修复与辅助技术复测。
  - S1_02B3_DUPLICATE_ATTRIBUTION.csv 登记 substantively_duplicate=no，difference_basis 逐项注明对象、交付物、成功标准与职业差异。
  - S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv 现有行：两行都是 WF-A11Y 的 primary 成员，expert_capability_group_id=ECG-46。因此记法纠正为同族的两条候选，不是两个工作族。
- 已确认事实：两行都是 WCAG 2.2 AA 整改。两行都涉及网页、PDF、视频、字幕与辅助技术复测。差异一侧在品牌文档系统对象，一侧在课程媒体对象，输入、操作、产物、验收四列都可分别对应。
- 判断：B3 的历史非重复登记维持 no 不动。同日登记实质重叠：同一族、同一能力组、同一 WCAG 2.2 AA 基线、共享字幕与辅助技术复测。是否确有需要把两条候选保留为不同任务，属专家判断，本版不声称已证实非重复。
- 待专家判断：重叠是否足以让画像把两者并为一类特征，还是按对象各留一类特征。两户都依赖屏幕阅读器人工复测，且尚未接入实际专家。是否把 Section 508 校验作为 edu_edt_wf03 的合规口径，也需出具合规意见。
- 影响：WF-A11Y 的画像先按同一族内两条候选处理，不预设合并，也不预设永久分离。

## 5. WF-RESEARCH-DATA 与 WF-NEUROIMAGING 的次归属

- 涉及：psy_comp_wf01。WF-NEUROIMAGING 主归属，WF-RESEARCH-DATA 次归属。
- 证据：
  - S1_02C_WORKFLOW_FAMILY_REGISTRY.csv 的 WF-RESEARCH-DATA definition 为按社区元数据标准整理、校验并沉积研究数据，交付校验包与登录号。
  - 该 registry 的 WF-NEUROIMAGING definition 覆盖 BIDS 预处理、质控与衍生数据组织。
  - S1_02B2_EFFECTIVE_CANDIDATES.csv 的 psy_comp_wf01 professional_operations 为 DICOM 转 NIfTI、BIDS 目录组织、bids-validator 校验、跑 fMRIPrep，并发布带来源追溯的衍生数据到某版本化存储或档案。granularity_check 记原因是单制品链，即每步产物只对下一步有意义，交付物是完整档案。evidence_scope 字段把 bids_layout_validation=verified、dicom_conversion_qc=uncited 分列。
- 已确认事实：psy_comp_wf01 实际覆盖数据整理（格式转换、目录组织、校验）与预处理（fMRIPrep）两端，其发布对象在原文是一种版本化存储或档案。
- 口径澄清：版本化存储或档案不同于公开库入藏与登录号。前者是版本化保存加来源追溯，后者是面向公开库的入藏、账号与 DOI 类登记，两者是不同动作。是否拆出独立沉积任务，仅作为待专家讨论的方案记录。
- 待专家或工程确认：次归属是否足够表达整理侧，还是把公开库沉积单列为 WF-RESEARCH-DATA 的 primary 成员。需要有神经影像与数据仓储背景的专家判断。是否引用 REMBI/MIRIAM 等规范也需复核。
- 影响：后续画像研究若给 WF-RESEARCH-DATA 仅记沉积，会把 psy_comp_wf01 的预处理能力漏掉。若记整条，会高估该族的沉积专长。画像侧如需公开库入藏能力，不应从该候选的原文假设。

## 6. 抽样范围与边界

- 本轮内容级复审 5 个案例：2 个能力组（ECG-07、ECG-19），1 对 HIGH 未决重复（DC-HYD-DIST），1 对非重复登记（vm_gra_wf03、edu_edt_wf03），1 条次归属（psy_comp_wf01）。不为了凑数量扩展开去。
- 以下都不在本轮裁决：computing_math 的 A/B 口径、DC-HYD-DIST 合并或拆分、ECG-07 签署、ECG-19 拆解。
- 25 组是既有重复对照登记，来自四批 DUPLICATE_ATTRIBUTION 文件，不是本轮新做的对照。本轮内容级复审只覆盖其中 2 对（DP-A-02、DP-B3-02），其余 23 对没有在本轮重新核对。25 组的结论不能外推到 129 个未进入对照的候选，后者 duplicate_attribution_role 仍为 none。
- 更正说明：这写进生效报告，不再写回冻结的历史文件。S1_02C_CROSS_BATCH_DEDUP_REPORT.md 的 DP-A-02 行把新建管网设计 vs 既有管网校准写成裁定依据（见该文件第 55 行），附录 A 第 170 行把新建管网设计 vs 既有管网校准写成该组的字段值。两处把 E4 拟议改写口径写成了既有事实。该文件属于历史交付件。两处的准确表述在 S1_02A_DUPLICATE_ATTRIBUTION.csv 的 pending 列：设计语境 vs 运营语境是拟议改写边界，HIGH 未决，合并或拆分待专家裁定。

## 7. 待确认问题清单（按重要度）

1. WF-RESEARCH-DATA 次归属是否需要公开库沉积 primary 成员（专家）。
2. DC-HYD-DIST 需裁定合并或按设计/运营拆分，含来源支持逐项核对（专家）。
3. ECG-07 签字主张是能力组追加的额外主张，是否成立、靠什么资质、什么法域门槛，需专家与法务共同确认。
4. ECG-19 是否拆为法律研究、诉讼支持、e-discovery 三组画像特征（专家）。
5. vm_gra_wf03 与 edu_edt_wf03 同为 WF-A11Y 族，重叠与去留待专家判断。
6. tool_existence 的 7 条各自的来源支持范围是否影响画像样本可选性，逐条核对（来源证据侧）。

## 8. 本轮回答问题（含 U4 勘误项）

- 核对 E1 的 evidence_kind：需修订，已修订清单，7 条 tool_existence 与 76 条 standard-complete 分开陈述。
- review_question 50/50 空：需修订，清单已写本轮新提出的复审问题。
- DC-HYD-DIST 描述：需修订。本版已改为引用 A 批登记 pending 列原文，删除已实现边界的说法，全文不再使用证据方向相反这类表述。E 级与 evidence_kind 两维分列，两端来源支持范围均待逐项核对。
- DC-HYD-DIST 主归属：维持 A 批登记的 env_water 主归属记录，不改写。E1 tool_existence 与 E3 industry_standard_complete 的对比不构成本版的重新裁定依据。
- 174 条逐一实跑：清单已改为风险分层，不预设 174 次独立人工实跑。
- vm_gra_wf03 与 edu_edt_wf03：本版改为同族两条候选的记法，历史 no 登记保留不动。
- ECG-07 签署、ECG-19 资质：本版把签署改为能力组追加的额外主张，资质改为潜在线索，都不是硬门槛。
- psy_comp_wf01 沉积动作：版本化存储/档案与公开库入藏、登录号分开，拆出独立沉积任务仅作为待讨论方案。
- 其余未列问题暂不展开。

## 9. U4 勘误记录

| U4 位置 | 勘误 | 本版处理 |
|---|---|---|
| 第 1.1 节末句 | 把 tool_existence 的缺口全部归为待工程证实 | 拆为来源支持范围、领域专业确认、工程运行验证三个维度，见第 2 节 |
| 第 2 节 | 把版本化存储与公开库沉积混写 | 分列两类动作，见第 5 节 |
| 第 4.1 节 | 把 E 级与证据种类的标签差异判成证据方向矛盾 | 已删。两端来源支持范围均待逐项核对，不暗示方向相反 |
| 第 4.1 节 | 引用拟议改写口径 | 只引 S1_02A_DUPLICATE_ATTRIBUTION.csv 原文，pending=HIGH 未决 |
| 第 4.2 节 | 未能识别同族 WF-A11Y | 改为同族两条候选，见第 4.2 节 |
| 第 3.1 节 | 把资格线索写成所有任务或所有法域的条件 | 改为潜在能力或资质线索 |
| 第 3.2 节 | 签署是候选提出的动作 | 改为能力组定义追加的额外主张，E4 提案级来源 |
| 全文 | 未说明 25 组中只有 2 组做了内容级复审 | 已写入第 4 节开头 |
| 无 | 未给旧历史报告中拟议口径写成既有事实的位置 | 第 6 节给出文件行号与更正说明，不回写历史文件 |

## 10. 剩余问题

- 本次勘误项不改变族、组、候选与风险登记。只改口径。
- 专家画像准备与配额原则的首轮草稿已落盘，为 S1_02C_EXPERT_PERSONA_DRAFTS.md 与 S1_02C_QUOTA_PRINCIPLES_DRAFT.md，与本报告一并等待独立复审。
- 二次复审意见见第 11 节，各自落位后的结果见第 12 节状态说明。

## 11. U5 二次勘误记录

| 位置 | 勘误 | 本版处理 |
|---|---|---|
| 报告第 4.1 节 | 残留方向相反含义的表述 | 删除。两端来源支持范围均待逐项核对，主归属记录未被来源字段推翻，尚不重新裁决 |
| 画像 P5 | 工程与专业用户两类职责未分 | 拆为工程侧与专业用户侧，两类当前都没有真实运行或专家验收证据 |
| 画像 P2 | 资质线索可能被读成硬门槛 | CMVP、PE、CEM 等资质只作为任务与法域确认线索，不设任何硬门槛 |
| 配额草案 | 每族固定条数的试点语 | 改为按资料可用性、专家参与和工程验证能力定样本数，覆盖多个画像与风险层级 |

## 12. 状态说明

- 当前五个画像（S1_02C_EXPERT_PERSONA_DRAFTS.md，现版 U6.1-P1）都是研究草案。
- 当前配额文件（S1_02C_QUOTA_PRINCIPLES_DRAFT.md，现版 U6-P2）是原则草案。
- 画像不是招聘 JD。
- 任务族与能力组不是专家人数。
- 当前仍没有专家背书，仍没有 Linux 实际运行证据。

## 13. U6 三处文档勘误记录（本版）

| 位置 | 原表述 | 本版处理 |
|---|---|---|
| 报告第 6 节 | “25 组重复对照仅基于本轮抽样，未外推到其余候选” | 改为：25 组是四批 DUPLICATE_ATTRIBUTION 的既有对照登记，不是本轮成果；本轮内容级复审只覆盖其中 2 对（DP-A-02、DP-B3-02）；其余 23 对没有在本轮重新核对；25 组结论不能外推到 129 个未进入对照的候选 |
| 画像 P1/P3/P4/P5 的工程侧工具表述（见 S1_02C_EXPERT_PERSONA_DRAFTS.md U6.1-P1） | 把 ENG-02 机械命中写成已确认的“专有或平台限定”“Windows 限定”工具事实 | 统一改为“ENG-02 机械命中，具体工具许可、平台限制和 Linux 可运行性待工程核实”。不把机械风险组命中写成已确认的 Windows-only、专有许可或平台限制事实 |
| 画像 P5 来源证据栏（见 S1_02C_EXPERT_PERSONA_DRAFTS.md U6.1-P1） | “另含 508 标准与 PDF/UA-1（按名引用）、WCAG 条款已读”三态混写 | 改为三档：已实际读取并逐条核对的 WCAG 条款（vm_gra_wf03 原文标注 as read 的各节与 SC）；仅按名称或 URL 引用、未标注已读的 WCAG 条款、Section 508 条款与 PDF/UA-1（ISO 14289-1，paywalled）；尚未逐条核对的其余 WCAG 成功准则。不把按名引用写成全文已读或完整覆盖 |

以上三处只改口径表述，不改证据等级、source_support_mode、候选字段或历史重复裁定。