# S1-02C 专家画像准备研究草案

版本：S1-02C-U6.1-P1
整理时间：2026-11-11
状态：研究草案，供专家访谈与试标设计前讨论。不是招聘 JD，不是人员编制方案。不给每个能力组配一位专家，不用 50 个能力组直接推算专家人数。U5 二次勘误已落：P2 资质仅作任务与法域确认线索，P5 职责分工程侧与专业用户侧两类，两类当前都没有真实运行或专家验收证据。U6 三处文档勘误已落：ENG-02 机械命中不写成已确认的平台或许可证事实，P5 来源分三档。

## 0. 用途与边界

- 每个画像对应一条或多条具体 candidate_id，不是能力组本身。
- 画像描述专家能承担的专业工作、经验线索与可接受的能力组合。能力是假设，不是录取条件。
- 一人承担与需要协作，均标明假设，由访谈与试标验证。
- 所有资质都只写在来源证据一栏。凡无来源的资质不写进门槛。
- 工程人员另行负责的环境、格式转换与验证器工作，与专业工作分开列。

## 1. 画像 P1 管网水力建模（水务与市政）

对应候选：eng_civilgeo_wf03（civil_geo，WF-WATER primary）、ag_envwater_wf04（env_water，WF-WATER primary）。专家能力组 ECG-04，其典型资质线索为 PE 水利/环境、注册土木（水利）、HEC/EPANET 实操，仅作线索。

核心专业工作：配水管网 EPANET 建模、参数校准、消防流量、水龄与压力服务符合性判断，并给改善建议。

所需经验：真实管网校准经验，把模型与实测水压或遥测对账的经验。可以接受只做市政设计一侧，也可以接受只做水务运营一侧，也可以接受两侧都做，以访谈与试标结果定组合。

协作假设：假设一人可以承担建模、校准与服务符合性三件事。消防流量与水龄的分析是否要另一人复核是待验证项。

原始资料：网络拓扑、需求、控制设定、观测水压或遥测数据、服务标准清单。

资料授权：S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv 第 5、19 行的授权组列，ag_envwater_wf04 命中 AUTH-06，eng_civilgeo_wf03 无命中，是机械初筛不是结论。这无关原始候选的 expert_raw_materials 字段，S1_02A_EFFECTIVE_CANDIDATES.csv 的两行原始 expert_raw_materials 均为空。管网图与台账是否需要运营方许可，试标前逐条确认。

要验证的问题：能否在没有固定资产台帐的条件下建出可校准的模型。能否说清设计口径与运营校准口径的可验收边界。DC-HYD-DIST 的合并或拆分裁定仍待专家背书，画像研究目前把两端分开访谈，不预设一名专家同时覆盖两侧。

可观察的成功标准：模型节点压力与实测对账在约定容差内，消防流量与水龄结论可复算，改善建议附出处。

待确认：EPANET 结果是否允许用于实际运维决策，谁对结果负责。管径设计结论需要注册执业资格签字的情形，试标前不承诺。

工程侧工作：EPANET 在目标 Linux 环境的运行与版本固定，对应 ENG-01（两端均 NOT_VERIFIED）与 ENG-02（仅 ag_envwater_wf04 命中；ENG-02 机械命中，具体工具许可、平台限制和 Linux 可运行性待工程核实）。输入数据格式转换与回归复算由工程人员负责，不进专家工作。

来源证据：S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv 第 19 行记 eng_civilgeo_wf03 为 E3 industry_standard_complete（source_category=academic），第 5 行记 ag_envwater_wf04 为 E1 tool_existence（source_category=government_tool_page，EPA EPANET 页）。一个来源是行业公开资料级，一个是工具存在级。两端对具体建模操作的支持强弱逐项核对，此前未逐项核对完毕。E3 本身不证明该候选的标准覆盖，不能作为硬门槛依据。

未验证项：两条 Linux 环境均 NOT_VERIFIED。消防流量与水龄分析没有成文标准级来源背书。DC-HYD-DIST 处于 HIGH 未决。

## 2. 画像 P2 建筑节能建模与 M&V

对应候选：eng_energypower_wf03（energy_power，WF-BUILDING-ENERGY 唯一成员）。专家能力组 ECG-07，其定义含能签署节能量核算，但该句是能力组的额外主张，不是候选提出的动作，本画像不以签署为硬门槛。

核心专业工作：按账单或实测数据做整楼能耗模型校准，按 ASHRAE Guideline 14 口径算 NMBE 与 CvRMSE，并给归一化节能量估计。

所需经验：整楼能耗模拟与实测校准。可接受有 M&V 经验者，也接受只有建模与校准经验者，是否具备陈述节能量结果的经验由试标定。

协作假设：假设一人能完成建模加校准加指标计算。节能量核算的复核是否需要第二人，作为待验证项。

原始资料：S1_02A_EFFECTIVE_CANDIDATES.csv 第 17 行 expert_raw_materials 为空，A 批次未记录。建筑描述、分时计量或账单数据、天气数据是候选 task_input 列明的输入。若带逐时电表与分项计量的项目，数据口径由试标确认。

资料授权：建筑计量数据可能含运营信息，S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv 命中 AUTH-03（个人信息与隐私），是机械初筛不是结论，逐条确认。业主同意书中能公开哪些数据不预设。A 批没有 research_ethics 字段，AUTH-04 本轮登记为 0，是字段盲区不是无风险。

要验证的问题：有没有用 ASHRAE G14 完整做过校准并写报告。NMBE 与 CvRMSE 之外，能否接受其他指标口径。是否需要签署节能量核算，按任务与法域再确认。签署是专业与法域的共同约束，不在本文件裁决。

可观察的成功标准：校准后 NMBE 与 CvRMSE 落在约定阈值内，节能量与不确定度带宽讲得出算法依据。

待确认：E4 expert_pending_proposal 表示本轮没有直接 M&V 来源，须专家确认并让任务落地到 ASHRAE G14。签字资格（CMVP、PE、CEM 或其他）与签字对象（M&V 报告还是协议）仅作为任务与法域确认线索，留到任务层逐项确认，本画像不据此设任何硬门槛。

工程侧工作：能耗模拟工具在 Linux 环境的运行，对应 ENG-01，LINUX 为 NOT_VERIFIED。把账单与量表数据转成工具输入格式由工程人员做。AUTH 组的隐私与伦理字段覆盖对 A 不完整，AUTH-04（研究伦理与 IRB）在本轮登记为 0，是字段盲区不是无风险。

来源证据：candidate 行 evidence_kind=expert_pending_proposal，evidence_risk_class=c6，无直接 M&V 来源。本画像的核心工作清单来自候选的 professional_operations 与成功标准，两者都是提案级内容。ECG-07 的 typical_credentials 为 ASHRAE BEMP/BEAP、CMVP、注册暖通，仅为线索。

未验证项：整条工作流没有验证过。任何资质都不能设为硬门槛。

## 3. 画像 P3 法律检索与诉讼支持

对应候选：legal_research_wf01 至 wf04（WF-LEGAL-RESEARCH），legal_litigation_wf01 至 wf04（WF-LITIGATION）。专家能力组 ECG-19，最大组，8 条候选。

核心专业工作：法律检索、备忘起草与引证核验、特权审阅与特权日志、TAR 审阅编码、取证与证人准备。候选人可只认领其中一类，不要求全包。

所需经验：按候选分两侧。legal_research 侧看检索与引证核验，litigation 侧看审阅流程与法庭程序。可以接受仅呈一侧经验者。

协作假设：假设法律检索、诉讼支持与电子取证可以是不同人。是否必须由执业律师签署某类产出，按任务所在法域确认。

原始资料：S1_02A_EFFECTIVE_CANDIDATES.csv 的相关行 expert_raw_materials 为空，A 批次未记录。审阅人群、特权码、待检索问题清单等输入按候选 task_input 列明。真人案卷不可作为试标材料。

资料授权：S1_02C_AUTHORIZATION_RISK_REGISTER.csv 对该类候选命中 AUTH-06（工具许可）与 AUTH-01（判例与数据库内容摘引），是机械初筛不是结论。用合成案卷或公开裁判文书的边界，试标前单独确认。涉特权类材料原则上不能用真实客户文档。

要验证的问题：能否在给定法域内写明报告或意见的引用依据。e-discovery 认证与执业资格中哪些是任务真正需要，哪些只是可选。能否就 TAR 的召回率与采样方法陈述可辩护性。

可观察的成功标准：检索备忘录每句有权威依据，特权内容不进入生产集，TAR 验证指标与流程可复查。

待确认：无来源支持的任务写作不进入本轮画像。是否把三个子能力拆成三个画像特征是专家判断，本画像保留三合一的研究形式，访谈时按能力分问。

工程侧工作：TAR 平台、审阅数据库与特权编码工具的环境与 Linux 侧运行归工程，对应 ENG-02 与 ENG-03（命中见 assignment 第 46 行起；ENG-02 机械命中，具体工具许可、平台限制和 Linux 可运行性待工程核实）。语料转电子表格与导出格式由工程人员做。

来源证据：legal_litigation_wf02、wf03 是 E1 tool_existence（vendor_doc），只证明工具及其厂商描述存在，不能作为审阅流程与特权日志的标准覆盖依据。legal_research_wf01 至 wf04 多为 E3 industry_standard_complete 或 E1 industry_standard_complete。ECG-19 evidence_class_distribution c2=3、c4=5，是证据类别分布不是专业确认。

未验证项：两条 tool_existence 候选的要旨（TAR、特权日志）没逐项核对过来源。执业律师、法务/合规资格、e-discovery 认证不设硬门槛。

## 4. 画像 P4 神经影像数据整理与预处理

对应候选：psy_comp_wf01（comp_neuro，WF-NEUROIMAGING primary，WF-RESEARCH-DATA secondary）。专家能力组 ECG-34，其定义是把 BIDS 预处理与其他方法学工作放在一个组，本画像不套该定义。

核心专业工作：DICOM 转 NIfTI、BIDS 目录组织、bids-validator 校验、跑 fMRIPrep、QC 与来源追溯。任务原文的发布对象是版本化存储或档案。

所需经验：真实扫描数据的 BIDS 整理与 fMRIPrep 预处理。可以接受只做整理侧，也可以接受只做预处理侧，试标定组合。

协作假设：假设一人可覆盖全管线，即整理、预处理、QC 一条链。多模态或病态采集的 QC 由谁复核待验证。

原始资料：DICOM 导出、扫描协议参数表、参与者知情同意书。公共 BIDS 数据如 OpenNeuro 或 HCP 按各数据集许可使用。

资料授权：候选 usage_permissions 写明 HCP 须在线注册并有商业用途与再识别限制，院内影像需机构同意数据共享协议。S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv 该候选命中 AUTH-01、AUTH-02、AUTH-03、AUTH-06，都是机械初筛不是结论。A 批没有 research_ethics 字段，AUTH-04 在本轮登记为 0，是字段盲区不是无风险。

要验证的问题：是否亲手处理过病态或异形序列。对不同 BIDS 版本的兼容与迁移。是否做过公开库入藏与登录号分配，若只有版本化存储经验不算缺失。

可观察的成功标准：官方 bids-validator 报零错，fMRIPrep 全部通过，QC 覆盖所有声明受试者，来源日志列明软件版本。

待确认：是否把公开库入藏、登录号与 DOI 看作沉积任务的独立环节，仅作为待讨论方案。是否引用 REMBI 或 MIRIAM 规范需复核。知情同意书的数据共享层级允许用到哪个水平，试标前确认。

工程侧工作：容器化 fMRIPrep 与 dcm2niix 的 Linux 环境，归工程侧，对应 ENG-01、ENG-02（ENG-02 机械命中，具体工具许可、平台限制和 Linux 可运行性待工程核实）。DICOM 脱敏与序列命名由工程人员与研究者共同定义后，专家按规范执行。

来源证据：BIDS 说明第 1.4 版已验证 200，Gorgolewski 2016 与 Esteban 2019 是搜索确认但获取受阻。evidence_scope 里 dicom_conversion_qc 记为 uncited，即 DICOM 转换的 QC 无来源。source_support_mode 是 uncited_support，仅做说明不设硬门槛。

未验证项：B2 是 effective 文件，该候选在 S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv 记 original_workflow_family_ids 为 fc_neuroimaging_curation,fc_mri_preprocessing，registered，family_assignment_basis 为 prefix_default+secondary。回归为 WF-NEUROIMAGING 主、WF-RESEARCH-DATA 次，都是本轮分析结果。

## 5. 画像 P5 数字内容无障碍整改

对应候选：vm_gra_wf03（graphic_design，WF-A11Y primary）、edu_edt_wf03（educational_technology，WF-A11Y primary）。同族两条，注册为非重复。专家能力组 ECG-46，其定义为 WCAG/508 修复与验证。

核心专业工作：按 WCAG 2.2 AA 做文档与内容整改，覆盖网页、PDF、视频、字幕与辅助技术复测。vm_gra_wf03 对象是品牌站与文档，edu_edt_wf03 对象是课程站与 LMS。两条是 WF-A11Y 同族的两条候选，注册为非重复，画像归一类并保留两端对象差异。

所需经验：WCAG 2.2 条款逐条对照的审计与整改。可以接受只做文档与 PDF/UA 侧，也可以接受只做视频与字幕侧，试标定组合。

协作假设：P5 的职责分两类，不是一类人。工程侧做工具安装、自动扫描、运行环境与结果采集。专业与用户侧做屏幕阅读器实际复测、可用性判断与最终无障碍验收。两侧是否各由一人还是多人承担，都没有真实运行或专家验收证据，是待验证假设。

原始资料：候选 expert_raw_materials 分别写明品牌规范、页面导出、PDF 源文件、音视频素材、审计工具报告，以及课程导出、视频、交互组件与既往整改记录。

资料授权：S1_02B3_WORKFLOW_CANDIDATES.csv 原文写 vm_gra_wf03 要求品牌方授权色彩与组件变化、字体网络授权、字幕类版权与测试参与者同意书，edu_edt_wf03 要求课程材料版权保留、字幕与音乐同步权处理、第三方出版商 PDF 只能换授权副本。S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv 两行命中的授权组见该文件第 151、175 行，是机械初筛不是结论。

要验证的问题：是否并行做过文档与视频字幕两类。先前整改过的对象中是否有第三方嵌入内容如何处理。Section 508 与 WCAG 的差异是否讲得清。

可观察的成功标准：WCAG 2.2 适用条款逐项证据可复查，PDF/UA 预检零错误，视频字幕同步，ACR 每条列明测试方法与工具。

待确认：vm_gra_wf03 与 edu_edt_wf03 的实质重叠是否影响画像，S1_02B3_DUPLICATE_ATTRIBUTION.csv 记 no 并注明两端都依赖屏幕阅读器人工复测。若确认双方可同质化，画像并两段为一类，合并方案另行专家判断。该对两端 expert_endorsement_required=yes 且未背书。

工程侧工作：axe 与 Lighthouse 自动化扫描的安装与重现、NVDA 与 JAWS 的环境与 Linux 可运行性归工程，对应 ENG-02（ENG-02 机械命中，具体工具许可、平台限制和 Linux 可运行性待工程核实）。PDF/UA 检查器与标签工具同样归工程。工程侧当前没有真实运行证据，两端 Linux 环境均 NOT_VERIFIED。

专业与用户侧工作：屏幕阅读器实际复测（NVDA、JAWS、VoiceOver 等）、可用性判断与最终无障碍验收归专业与用户侧。该侧当前没有专家验收证据，辅助技术真实用户复测尚未接入任何实际专家。

来源证据：两端来源均为 E1 industry_standard_complete。来源表述分三档。第一档，已实际读取并逐条核对的 WCAG 条款：仅 vm_gra_wf03 的 source_reference 原文标注 as read 的 §5.2 Conformance Requirements 与 SC 1.1.1、1.2.2、1.2.5、1.4.3。第二档，仅按名称或 URL 引用、未标注已读的：edu_edt_wf03 引用的 WCAG 2.2 条款清单（§5.2、§5.3 与 SC 1.2.2、1.4.3、2.4.11、3.3.8、4.1.2，原文未标注读取状态）、Section 508 标准条款（E101.1、E205.2、E205.4、C203.1、C205.2）、PDF/UA-1（ISO 14289-1，paywalled 未读）、vm_gra_wf03 标注 cited by name 的 SC 2.1.1、2.4.7。第三档，其余 WCAG 成功准则尚未逐条核对。三档不混写，不把按名引用写成全文已读或完整覆盖。S1_02C 该族 conditional_support=2。

未验证项：工程侧的 Linux 环境与工具链均 NOT_VERIFIED，没有真实运行。专业与用户侧的屏幕阅读器复测与最终验收没有专家证据。两行未做任何机器可验证的端到端运行。

## 6. 通用未验证提示

- evidence_level 不是独立复核结果。画像引用的任何 E1 至 E4 均按本报告第 2 节三分口径解读，不把来源支持当作领域专业确认，不把领域确认当作工程验证。
- expert_endorsement_required 的 45 条尚未背书，不是已背书。expert_pending 的 9 条全部在 A，尚未安排。
- 每条画像的工程侧工作均未闭合。ENG-01 的 174/174 NOT_VERIFIED 不是本文件可解。
- 画像 P1 至 P5 的来源证据栏写着各条 candidate 的当前证据状态。没有写进该栏的资质均不作为门槛。
- 原始资料与资料授权两栏写的是候选原文与机械初筛，不是已完成授权的结论。