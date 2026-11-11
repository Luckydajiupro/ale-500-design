# S1 阶段一收口交接报告（Phase 1 Handoff Report）

版本：H-1.0
整理时间：2026-11-11
状态：阶段一收口包，等待独立复审。不进入正式配额分配、专家人数计算、招募、试标、平台开发或 P1 工程实现。

## 0. 目标与边界

目标是把 S1 阶段现有研究成果（S1-01 官方类别映射、S1-02A/B1/B2/B3 四批候选、S1-02C 全域统一视图、业务复审、画像草案、配额原则草案）整理为可供主会话更新总体实施方案的阶段性交接包。

边界：本报告不扩展候选、不开始招募或试标、不重新生成任何候选/族/能力组/风险表、不修改任何 CSV、脚本、Phase 0、官方输入或历史研究文件。报告内每个数字都来自当前磁盘文件，逐条标明出处；与模板数字不一致处在本报告注明。

七类条目口径：

- 已确认决策（confirmed decision）：本阶段研究过程中已固定、有文件事实支持的决策。
- 文件支持的事实（file fact）：直接从磁盘文件读出的计数、状态或字段值。
- 研究建议（research recommendation）：研究者提出的建议，非既定结论。
- 条件决策（conditional decision）：以专家访谈、试标证据或其他未来工作为前提才能成立的决策。
- 开放决策（open decision）：本阶段尚无定论、留待后续裁决的决策。
- UNKNOWN：文件范围内无法得出答案的事项，保持缺失，不伪造。
- 尚未验证事项（verification pending）：有明确验证方向的待办，尚未执行。

## 1. S1-02C-U6 最新业务复审状态

文件事实：

- S1_02C_BUSINESS_REVIEW_REPORT.md 当前版本 S1-02C-U6.1，含 U4 勘误记录（第 9 节）、U5 二次勘误记录（第 11 节）、U6 三处文档勘误记录（第 13 节）。
- 结构校验与候选统一视图：scripts/35_validate_s1_02c.py 15 项检查全部 PASS；scripts/36_validate_s1_02c_c16.py 16 项检查全部 PASS；两套 self-test（35 十个负例、36 十三个负例）全部通过。五张统一 CSV 的 SHA-256 与 .audit/s1-02c-fingerprints.txt（含字节数）全部一致。
- 本轮三处文档勘误已完成：见本报告第 2 节。

尚未验证事项：

- 业务判断仍有专家事项待确认：DC-HYD-DIST 合并或拆分、ECG-07 签署主张、ECG-19 是否拆组、WF-RESEARCH-DATA 公开库沉积次归属、vm_gra_wf03 与 edu_edt_wf03 的重叠去留。
- 业务判断仍有工程事项待确认：174 条 Linux NOT_VERIFIED、94 条 ENG-02 命中的工具许可与平台限制。
- U6 的画像文件（S1-02C-U6.1-P1）与配额文件（S1-02C-U6-P2）仍是准备性研究材料，不是最终批准结果。画像不是招聘 JD，配额原则不给 500 条分配数字。

## 2. U6 三处文档勘误（本轮已落）

1. S1_02C_BUSINESS_REVIEW_REPORT.md 第 6 节“25 组重复对照仅基于本轮抽样”改为明确表述：25 组是四批 DUPLICATE_ATTRIBUTION 文件的既有对照登记，不是本轮新做；本轮内容级复审只覆盖其中 2 对（DP-A-02、DP-B3-02）；其余 23 对没有在本轮重新核对；25 组结论不能外推到 129 个未进入对照的候选（duplicate_attribution_role 仍为 none）。
2. S1_02C_EXPERT_PERSONA_DRAFTS.md 全部 ENG-02 工具表述统一为“ENG-02 机械命中，具体工具许可、平台限制和 Linux 可运行性待工程核实”。涉及 P1（EPANET）、P3（TAR 平台、审阅数据库、特权编码工具）、P4（fMRIPrep、dcm2niix）、P5（NVDA、JAWS、PDF/UA 检查器与标签工具）。不再把机械风险组命中写成已确认的 Windows-only、专有许可或平台限制事实。P5 工程侧与专业用户侧职责分开，两侧当前都没有实际运行或专家验收证据。
3. P5 来源证据栏（同文件）三档分开：已实际读取并逐条核对的 WCAG 条款（vm_gra_wf03 原文 as read 标注）；仅按名称或 URL 引用、未标注读取状态的 WCAG 条款、Section 508 条款与 PDF/UA-1；其余尚未逐条核对的成功准则。不把“按名引用”写成“全文已读”或“完整覆盖”。

未修改：证据等级（evidence_level）、source_support_mode、候选字段、历史重复裁定（25 组 YES 3/NO 22 保持原样）。

## 3. 已完成的类别、任务族和专家能力研究

文件事实（全部来自当前磁盘，逐条出处）：

- S1-01 官方类别与子领域映射：S1_01_CATEGORY_MAPPING.csv 55 行，coverage_status 为 active_observed 49、uncovered_official 6（chemical_process、mining_petroleum、precision_agriculture、aviation、maritime_port、educational_technology）。官方 13 命名行业簇 + Other 兜底桶；活动任务观察 14 域 49 子域。文件出处 S1_01_REVIEW_SUMMARY.md 第 1 节。
- 四批候选：A 51 + B1 57 + B2 39 + B3 27 = 174 条研究候选（S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv，验证器 C01/C02）。
- 72 个研究性任务族（S1_02C_WORKFLOW_FAMILY_REGISTRY.csv，规模分布 1:15、2:30、3:14、4:9、5:3、6:1；跨批族 3 个）。
- 50 个专家能力组（S1_02C_EXPERT_CAPABILITY_MATRIX.csv，中位数 3，最大 8（ECG-19），单例 1 个（ECG-07））。
- 9 个授权风险组（S1_02C_AUTHORIZATION_RISK_REGISTER.csv）；7 个工程风险组（S1_02C_ENGINEERING_RISK_REGISTER.csv，ENG-01 覆盖全部 174 条）。
- 25 组既有重复对照：YES 3、NO 22（S1_02C_CROSS_BATCH_DEDUP_REPORT.md；验证器 C11）。3 个 YES 簇均在 A 批。
- 本轮 U5/U6 内容级复审实际只覆盖 2 对（DP-A-02 与 DP-B3-02），其余 23 对没有在本轮重新核对。

口径（已确认决策）：

- 174、72、50 都是研究视图统计，不是正式任务配额、产能或专家人数。不按官方任务比例、174 条候选比例或 72 个任务族比例直接分配 500 条。
- 与模板数字的差异：无差异。模板列的 174、72、50、9、7、25（3 YES/22 NO）与磁盘文件完全一致。

## 4. 配额原则、A/B 情景和 Draft-0 状态

文件事实：

- S1_02C_QUOTA_PRINCIPLES_DRAFT.md 版本 S1-02C-U6-P2，是研究原则草案，不是配额方案。当前没有正式 500 条分配数字，没有专家人数。
- 该文件明确：官方任务数、174 条候选数、72 个任务族数均不直接套比例（原则 P2）；computing_math A/B 并行保留、两套口径配额不可合并计数，quantum 等边界组保持待确认、不通过配额倒推归属（原则 P3）；20–30 条完整链路试点是校准计划，不是生产配额，试点通过不是配额批复（原则 P4）；试点样本数按资料可用性、专家参与和工程验证能力确定，不预设每个任务族固定条数（第 2 节）。
- S1-01 侧 computing_math 相关子域（software_eng、data_analytics、ai_cs_research、math_ops_research、cybersecurity、infra_cloud）ab_A=excluded、ab_B=excluded_cs_subdomain 或 conditional_keep_non_cs_math_or（仅 math_ops_research），exclusion=excluded_awaiting_AB；quantum 的 ab_dispute=quantum_straddles_physics_and_cs，ab_B=dispute_unresolved。并行未裁决状态保持。
- 当前目录不存在 Draft-0 配额方案；不存在 R1 配额草案（Phase 0 的 R1 是运行性基线，待复审，不是 500 条配额方案的批准版本）。目录内唯一含配额字样的是 S1_02C_QUOTA_PRINCIPLES_DRAFT.md 本身。

已确认决策：

- Draft-0 或 R1 都不是批准后的生产计划，除非主会话另行作出正式决策。
- 如果以后出现 Draft-0 或 R1 配额方案文件，需只读登记路径、版本、状态、是否批准、与 U6-P2 的关系；目前无此类文件。

## 5. 专家画像、筛选维度、培训和试标要求

文件事实：S1_02C_EXPERT_PERSONA_DRAFTS.md 版本 S1-02C-U6.1-P1，五份研究画像登记如下。

| 画像 | candidate_id 与任务族 | 核心专业工作 | 一人承担或协作组合 | 原始资料 | 使用权限与隐私限制 | 预期产物 | 工程人员职责 | 专家待确认事项 | 不能直接转为硬门槛的资质线索 |
|---|---|---|---|---|---|---|---|---|---|
| P1 管网水力建模 | eng_civilgeo_wf03、ag_envwater_wf04；WF-WATER；ECG-04 | EPANET 建模、参数校准、消防流量、水龄与压力服务符合性 | 可只做市政设计侧、或只做运营侧、或两侧都做；消防流量与水龄复核待验证 | 拓扑、需求、控制设定、观测水压/遥测、服务标准清单 | 管网图与台账需运营方许可，试标前逐条确认；机械初筛 AUTH-06（仅 ag_envwater_wf04） | 模型与实测对账在约定容差内，结论可复算，建议附出处 | EPANET Linux 运行与版本固定、数据格式转换、回归复算（ENG-01 两端、ENG-02 仅 ag_envwater_wf04） | DC-HYD-DIST 合并或拆分未裁；EPANET 结果能否用于实际运维决策；设计结论需执业签字情形 | PE 水利/环境、注册土木、HEC/EPANET 实操（ECG-04 typical_credentials） |
| P2 建筑节能建模与 M&V | eng_energypower_wf03；WF-BUILDING-ENERGY 唯一成员；ECG-07 | 整楼能耗模型校准、ASHRAE Guideline 14 口径 NMBE 与 CvRMSE、归一化节能量估计 | 一人建模加校准加指标计算；节能量复核待验证 | 建筑描述、分时计量或账单数据、天气数据 | 机械初筛 AUTH-03；业主同意书公开范围不预设；A 批无 research_ethics 字段（AUTH-04=0 是字段盲区不是无风险） | NMBE 与 CvRMSE 落阈值内，节能量与不确定度带宽讲得出算法依据 | 能耗模拟工具 Linux 运行（ENG-01）、账单与量表数据转工具格式 | E4 expert_pending_proposal，须专家确认并落地 ASHRAE G14；签字资格与对象按任务与法域确认 | CMVP、PE、CEM、ASHRAE BEMP/BEAP（仅线索） |
| P3 法律检索与诉讼支持 | legal_research_wf01-04、legal_litigation_wf01-04；WF-LEGAL-RESEARCH、WF-LITIGATION；ECG-19 | 法律检索、备忘与引证核验、特权审阅与特权日志、TAR 审阅编码、取证与证人准备 | 可只认领一类，不要求全包；检索/诉讼/e-discovery 可以是不同人 | 审阅人群、特权码、待检索问题清单；真人案卷不可用作试标材料 | 机械初筛 AUTH-06、AUTH-01；合成案卷或公开裁判文书边界试标前确认；涉特权材料不能用真实客户文档 | 备忘录每句有权威依据，特权内容不进生产集，TAR 指标与流程可复查 | TAR 平台、审阅数据库、特权编码工具 Linux 运行（ENG-02/ENG-03）、语料转格式 | 是否拆为法律研究、诉讼支持、e-discovery 三组画像特征；哪些资格是任务真正需要 | 执业律师、法务/合规资格、e-discovery 认证（ECG-19 typical_credentials） |
| P4 神经影像数据整理与预处理 | psy_comp_wf01；WF-NEUROIMAGING 主、WF-RESEARCH-DATA 次；ECG-34 | DICOM 转 NIfTI、BIDS 目录组织、bids-validator 校验、跑 fMRIPrep、QC 与来源追溯 | 可只做整理侧或只做预处理侧；多模态或病态采集 QC 复核待验证 | DICOM 导出、扫描协议参数表、参与者知情同意书；公共 BIDS 数据按各数据集许可 | HCP 须在线注册且有商业用途与再识别限制；院内影像需机构同意数据共享协议；机械初筛 AUTH-01/02/03/06 | bids-validator 零错，fMRIPrep 全过，QC 覆盖所有声明受试者，来源日志列明软件版本 | 容器化 fMRIPrep 与 dcm2niix 的 Linux 环境（ENG-01/ENG-02）、DICOM 脱敏与序列命名定义 | 公开库入藏与登录号是否独立环节（仅讨论方案）；REMBI/MIRIAM 引用复核；知情同意书共享层级 | 无资质门槛写出；BIDS 定义与工具文档是来源证据 |
| P5 数字内容无障碍整改 | vm_gra_wf03、edu_edt_wf03；WF-A11Y；ECG-46 | WCAG 2.2 AA 文档与内容整改，覆盖网页、PDF、视频、字幕与辅助技术复测 | 工程侧（工具安装、自动扫描、运行环境、结果采集）与专业用户侧（屏幕阅读器实际复测、可用性判断、最终无障碍验收）分立，两侧人数与组合待验证 | 品牌规范、页面导出、PDF 源文件、音视频素材、审计报告；课程导出、视频、交互组件、既往整改记录 | vm_gra 需品牌方授权与测试参与者同意；edu_edt 需课程材料版权保留、字幕与音乐同步权处理、第三方 PDF 换授权副本 | WCAG 适用条款逐项证据可查，PDF/UA 预检零错，字幕同步，ACR 列明测试方法与工具 | axe/Lighthouse 安装与重现、NVDA/JAWS 环境与 Linux 可运行性（ENG-02 机械命中待核实）、PDF/UA 检查器与标签工具 | 两条候选实质重叠去留；Section 508 是否作为 edu_edt_wf03 合规口径（需合规意见） | 无资质门槛写出；来源三档见第 2 节第 3 条 |

筛选维度（研究建议，写进后续访谈与试标设计）：专业工作经历；真实产物和成功标准经验；原始资料可提供性；资料使用权限；法域、伦理、隐私或专业责任；工具和环境经验；是否能配合试标和复核；一人承担与多人协作边界。

培训和试标要求（只写准备性要求，不启动实际试标）：

- 专家先理解任务说明、成功标准和资料授权边界。
- 提交预期产物和判断依据。
- 通过小规模试标验证专业能力。
- 记录回退、争议、修改和复核原因。
- 专家不承担 Docker、ALE 打包、环境部署和验证器实现；工程人员负责格式转换、环境、运行和验证器。

已确认决策：专家负责专业内容、资料、预期产物和成功标准；工程人员负责格式、环境、验证器和评测。五个画像可作为访谈和试标设计起点（条件决策）。画像中的资质线索不能直接转为硬门槛。

## 6. 招募渠道研究现状

文件事实：

- 当前目录没有招募渠道研究材料。S1_02C_QUOTA_PRINCIPLES_DRAFT.md 第 0 节明确“本轮不研究招募渠道，所以本文件不写任何渠道名”。
- 本阶段尚未核实任何平台、地区、语言和合作方式；未联系任何候选人；未发布任何招聘；未作费用、任务量或交付日期承诺。
- 本报告不编造渠道名称、地区、价格或合作模式。

## 7. 已确认决策、条件决策和开放决策

### 7.1 已确认决策

1. Phase 0 final 是只读基线（lifecycle=closed），本阶段只读取，不修改，不把 S1-02C 结论写回 Phase 0。
2. 官方 ALE 任务只作研究和对齐参考，不计入 500 条。
3. 专家负责专业内容、资料、预期产物和成功标准；工程人员负责格式、环境、验证器和评测。
4. 自动化优先，风险分层人工复核；不预设 174 次独立人工实跑。
5. 20–30 条完整链路试点作为扩量前校准；试点不是生产配额，试点不产生可宣称的专家人数。
6. 不把研究候选直接转为配额；174、72、50 是研究视图统计。
7. 不修改 CSV、脚本、Phase 0、官方输入或历史研究文件（本轮核实：C13 61/61 基线哈希匹配，Phase 0 65/65 校验和匹配）。
8. computing_math A/B 并行保留、配额不可合并计数（原样保留自 S1-01）。25 组重复对照里 YES 3/NO 22 的已有裁定不因本轮归并而视为已确认（含 B3 十个非重复裁定）。

### 7.2 条件决策

1. 五个画像（P1–P5）可作为访谈和试标设计起点，需试标验证后修正。
2. 任务族（72）和能力组（50）可作为研究性组织结构，粒度是否合适待专家裁定。
3. P5 两条无障碍候选先保持同族（WF-A11Y）、分别保留对象差异，合并与否待专家判断。
4. DC-HYD-DIST 保持双候选，等待专家裁决（HIGH 未决，25 组中唯一）。
5. P3 是否拆分法律研究、诉讼支持和 e-discovery，等待专家确认。
6. ECG-07 签署主张是能力组追加的额外主张，是否成立待专家与法务按任务与法域确认。

### 7.3 开放决策

1. computing_math A/B 最终口径（不裁决，保留自 S1-01）。
2. quantum 归属（物理或 CS）。
3. uncovered_official 六个子领域的后续处置（分类处理或补采；是否补官方样本或专家判断）。
4. 72 个任务族是否过细，15 个单成员族的合并建议。
5. DC-HYD-DIST 合并或按设计/运营拆分。
6. ECG-07 签字是否有必要、什么资质、什么法域门槛、签字对象。
7. ECG-19 是否拆为三个画像特征。
8. 资料授权和专家合作方式。
9. 地区、语言、预算、合作方式、交付日期。
10. 招募渠道。
11. Linux、Windows 和专有工具的工程可验证性（94 条 ENG-02 命中、174 条 NOT_VERIFIED）。

### 7.4 UNKNOWN 清单

1. B3 时间线部分是事后补记，历史顺序保持 UNKNOWN（.audit/s1-02b3.tsv L18–L27；edu 片段原始字节不可复验）。
2. .audit/u2-pre/ 脚本副本与当前脚本哈希一致，不能作为 U2 前脚本回滚点；本机未找到 20261110-171109 压缩包。
3. 5 个未覆盖子域的精确官方 ID 是编号推断（S1_01，10.1 除外）。
4. 13 处跨域重分类的 rationale 字段缺失。
5. 20261110-171109 压缩包是否存在、位置与内容。
6. 总体方案 v0.5.1 文件是否存在（结论见第 9 节）。

## 8. 当前证据等级、风险和限制

文件事实（与模板数字核对，全部一致）：

- evidence_level 分布：E1=83、E3=87、E4=4（验证器 C03）。
- E1 中 industry_standard_complete=76、tool_existence=7（ag_envwater_wf01、ag_envwater_wf04、eng_electronics_wf01、eng_manufacturing_wf01、eng_manufacturing_wf02、legal_litigation_wf02、legal_litigation_wf03）。E3 另有 tool_existence 5 条；报告口径“7 条 tool_existence”专指 E1 层。
- 174 条 independent_verification_present=no；174 条 linux_verification_state=NOT_VERIFIED；engineering_pending=83（A 21、B1 25、B2 15、B3 22）；uncovered_official=22（A 13 + B3 9）；padding_risk=27（high=9、medium=18，全在 B3）；expert_endorsement_required=45；expert_pending=9（全在 A）。
- 25 组重复对照只覆盖既有登记，不代表全集去重；129 位候选未进入任何对照。同族不等于重复，重复裁定只存在于候选对层。
- B3 的 high padding 是“凑数压力”标记，不是“已凑数”裁定。
- 脚本快照与数据快照的可恢复性分开描述：u2-pre 脚本副本不能回滚，数据快照（五张 CSV 与 stats）可分别核对。
- 数字与模板差异：无。所有数字均从当前磁盘文件与验证器输出核实，无差异。

## 9. 与 Phase 0 final 和总体方案 v0.5.1 的对应关系

### 9.1 Phase 0 final

- 实际目录：/Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108/analysis/phase0-final
- 版本标识：phase=phase0-final、stage=final、created_at=2026-11-10T10:59:28+08:00、lifecycle=closed（SOURCE_MANIFEST_FINAL.json）。
- 校验文件：FINAL_CHECKSUMS.sha256（65 条：12 最终文件 + 47 证据 + 4 脚本 + progress.log + SOURCE_MANIFEST_FINAL.json）。
- 接收报告：FINAL_VALIDATION_REPORT.md（41 项检查 PASS 40 / FAIL 0 / ERROR 0 / SKIP 1，Status: Phase 0 CLOSED）。
- 本轮只读核对：sha256sum -c FINAL_CHECKSUMS.sha256，65/65 OK，exit 0。与 B3 登记（.audit/s1-02b3-phase0-final-register.md）一致。
- 本阶段未修改 Phase 0；S1-02C 研究结论不写回 Phase 0。

### 9.2 总体方案 v0.5.1

- 结论：当前工作目录未找到，未修改，待主会话提供或另行维护。本机在 Workspaces/ale-研究设计 下搜索 v0.5.1、总体方案、master plan 均无命中（仅上游第三方仓库 release note 中出现 v0.5.1 字样，与总体方案无关）。
- 未自行创建或修改任何总体方案文件。

### 9.3 本交接包可以为总体方案更新提供哪些输入

- 类别覆盖：S1-01 的 55 官方子域映射与 6 个 uncovered_official 子域。
- 候选工作流：174 条候选、72 个任务族、3 个跨批族。
- 专家画像：5 份画像草案与筛选维度。
- 授权风险：9 个授权风险组。
- 工程风险：7 个工程风险组。
- 试点测量字段：任务制备耗时、专家处理耗时、资料获取是否受阻、专家回退次数、工程验证通过率、生成物修订轮数。
- 配额调整原则：调整项限于任务难度、耗时、资料权限稀缺度、专家供给限度、工程可验证性。

## 10. 后续进入技术验证、试点和平台 P1 设计的输入

### 10.1 技术验证输入

- 174 条 Linux NOT_VERIFIED 候选；7 个工程风险组（ENG-01 至 ENG-07）。
- 工具、许可证、Windows/Linux/GPU 依赖（94 条 ENG-02 命中为机械筛查，待核实）。
- 可按风险分层共享环境验证；运行日志、版本、输入输出和验证器证据作为记录要求。

### 10.2 专家试点输入

- 五个画像草案；原始资料和权限检查项；预期产物和成功标准；专业复核问题（第 5 节）。
- 20–30 条完整链路试点；记录制备耗时、专家耗时、资料阻塞、回退次数、工程通过率、修订轮数。

### 10.3 平台 P1 输入

- 专家提交专业资料包；资料授权和脱敏状态。
- 任务草案、预期产物和成功标准；Agent 生成记录。
- 审核和争议记录；工程转换、验证器、运行日志。
- 版本、哈希和交付审计。

边界：P1 设计不能把专家变成工程实施者，也不能在平台设计阶段提前批准配额或招聘人数。

## 11. 文件清单、版本、哈希和验证结果

SHA-256 全部从当前磁盘实际计算（shasum -a 256 口径），不复制旧报告中的哈希。`.audit/s1-02c-fingerprints.txt` 的格式是 `<sha256>  <相对路径>  <字节数> bytes`，含有字节数附加字段，不是标准 sha256sum 清单，不能直接用于 sha256sum -c；本轮用解析脚本逐行拆出哈希与字节数，与当前磁盘五个 CSV 全部一致。标准 sha256sum 清单见本节末独立生成口径说明。

| 文件路径 | 用途 | 版本/状态 | SHA-256 | 历史基线 | 本轮修改 | 对后续工作的用途 |
|---|---|---|---|---|---|---|
| （Phase 0，目录略）/analysis/phase0-final/ 全量 65 项 | Phase 0 只读基线 | phase0-final，closed | 见 FINAL_CHECKSUMS.sha256，65/65 OK | 是 | 否 | 官方类别与任务基线引用 |
| S1_01_CATEGORY_MAPPING.csv | 官方类别与子领域映射（55 行） | S1-01 | 961ec1df305eed5b91048f4604692d2bc620dcf91884cd0422abd1af35784df1 | 是 | 否 | 覆盖口径与 A/B 状态 |
| S1_01_REVIEW_SUMMARY.md | S1-01 复审摘要 | S1-01 | c210c3e97a7ccac9cd50d00421f4db3577c5015f5934be759be059c76bbe6a57 | 是 | 否 | 官方映射证据说明 |
| S1_02A_EFFECTIVE_CANDIDATES.csv（及 A 批其余文件） | A 批 51 条候选与证据 | A final | f71c4305e5efd38e980ec7483b7905e28322d10cd26ba6348a83637059987ac9（effective） | 是 | 否 | 候选原始视图 |
| S1_02B1_WORKFLOW_CANDIDATES.csv（及 B1 批其余文件） | B1 批 57 条候选 | B1 final | 2c24f55a6c2a04d21f530df3e6d9b8a49b98be1772ae4b762bd59aa2f14c35c1 | 是 | 否 | 候选原始视图 |
| S1_02B2_EFFECTIVE_CANDIDATES.csv（及 B2 批其余文件） | B2 批 39 条候选 | B2 final | eb99cdb41962bc120aa16c77641c6fc457195b6b1dd52f0145efc2854be05e3f | 是 | 否 | 候选原始视图 |
| S1_02B3_WORKFLOW_CANDIDATES.csv（及 B3 批其余文件） | B3 批 27 条候选 | B3 final | 034911e5da93beefbc757c01e52e582d655f91e6cfb6595eba59ce2bafd6e639 | 是 | 否 | 候选原始视图 |
| S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv | 174 条逐条归属统一视图 | S1-02C-U1 | b335cf9293a8eba3b2869a72dcc913581bdb952d6697a9ab1bc43e69d5d2ac86（272256 bytes，与 fingerprint 一致） | 否 | 否 | 画像、配额、试点抽样主数据 |
| S1_02C_WORKFLOW_FAMILY_REGISTRY.csv | 72 个任务族登记 | S1-02C-U1 | fd6b4d94e97730d471d4414c03619abd5567c8aced9d5e8450f24ee29ebfa45e（31592 bytes，一致） | 否 | 否 | 族级组织结构 |
| S1_02C_EXPERT_CAPABILITY_MATRIX.csv | 50 个专家能力组 | S1-02C-U1 | 76af0f039cc5d1009d44c9918da2de2a17a20afa0626336bb182bcea7de3dbd8（21527 bytes，一致） | 否 | 否 | 画像设计依据 |
| S1_02C_AUTHORIZATION_RISK_REGISTER.csv | 9 个授权风险组 | S1-02C-U1 | e017809dec35233c3a015dd7764ce0195e1f413a2b17a050ba81490d18be2c62（17260 bytes，一致） | 否 | 否 | 资料授权检查项 |
| S1_02C_ENGINEERING_RISK_REGISTER.csv | 7 个工程风险组 | S1-02C-U1 | c1d7a9898fc40d79e70529d3eaea11e1258c25fca30c4b9a57b0165ed949326e（14847 bytes，一致） | 否 | 否 | Linux 验证分层依据 |
| S1_02C_REVIEW_SUMMARY.md | S1-02C 复核摘要 | S1-02C-U1（第三次修订） | bdaf1a8d48c00360861ff326e7cc547370f5bcf9550d9d5e63068a1dce13ac5e | 否 | 否 | 统一视图口径说明 |
| S1_02C_BUSINESS_REVIEW_CHECKLIST.md | 业务复审清单 | S1-02C-U3 | 8f783f277fe0111c148c39cb923f5826735343f13abe2770bbc466d463171213 | 否 | 否 | 复审范围与抽样 |
| S1_02C_BUSINESS_REVIEW_REPORT.md | 首轮业务复审报告 | S1-02C-U6.1（本轮勘误） | 8f0a7b9fff1ddd37b9fba21039e86ff34ba815ae41f612056a9a42bcb3b261f0 | 否 | 是 | 复审结论与勘误记录 |
| S1_02C_EXPERT_PERSONA_DRAFTS.md | 五份画像研究草案 | S1-02C-U6.1-P1（本轮勘误） | d2edac912bd9327040fd284c7e4fa0681052bad2079bc0cb62cdf7b329b865d0 | 否 | 是 | 访谈与试标设计起点 |
| S1_02C_QUOTA_PRINCIPLES_DRAFT.md | 配额研究原则草案 | S1-02C-U6-P2 | 8518db0a3e4648604e4058535f7ffeff9f8be6e40b2f85eeb7df13c90aff3c39 | 否 | 否 | 候选配额方案前置原则 |
| .audit/s1-02c-u4-erratum-decisions.tsv | U4/U5/U6 勘误决策记录 | U6 | 0ac4b8196a15d6a91aaf9bab24952ce014135d42775f0059817fd86bd3971852 | 否 | 否 | 勘误追溯 |
| .audit/s1-02c-fingerprints.txt | 五个 CSV 的 sha256 与字节数 | U1 | 83e64ce989bb393e207bb68b1d5b2d5c3b8d3b295ee882cbcf0c84ee017b56fc（含字节数附加字段的非标准清单） | 否 | 否 | CSV 不变性快速核对 |
| scripts/35_validate_s1_02c.py | 独立校验器（15 项） | U1 revision | a67aef9ce6a7fb7c0c499b32ee627393ca340058472369185ae78f3a94187491 | 否 | 否 | 每轮复核重跑 |
| scripts/36_validate_s1_02c_c16.py | C16 行列对照校验器（16 项） | U1 revision | ad7d5a3cdbd99e9d6acccf25318415eba7fe61f57ea23854250da13003cdba0c | 否 | 否 | 每轮复核重跑 |
| S1_PHASE1_HANDOFF_REPORT.md | 本报告 | H-1.0 | 报告自身哈希在最终收口时另行记录（本节落盘后报告即成为事实快照，自身哈希以收口回报为准） | 否 | 是（新增） | 主会话更新总体方案的输入 |
| S1_PHASE1_HANDOFF_CHECKLIST.csv | 交接清单 | C-1.0 | 清单自身哈希在最终收口时另行记录 | 否 | 是（新增） | 逐项状态与责任跟踪 |

历史文件哈希均取自 .audit/s1-02c-baseline.sha256（C13 本轮 61/61 全部匹配），上表 A/B1/B2/B3 与 S1-01 摘录的哈希即该基线记录值，与当前磁盘一致；完整 61 条历史基线清单以该文件为准。

## 12. 收口验证结果（2026-11-11 实测）

1. python3 -B scripts/35_validate_s1_02c.py：15 checks、0 failed、exit 0。
2. python3 -B scripts/36_validate_s1_02c_c16.py：16 checks、0 failed、exit 0。
3. python3 -B scripts/35_validate_s1_02c.py --self-test：10 mutations caught、pristine control green、exit 0。
4. python3 -B scripts/36_validate_s1_02c_c16.py --self-test：13 mutations caught、pristine control green、exit 0。
5. 五张统一 CSV 的 SHA-256：解析 .audit/s1-02c-fingerprints.txt（格式为 <sha256>  <相对路径>  <字节数> bytes，非标准 sha256sum 清单）逐行核对哈希与字节数，5/5 MATCH。
6. 历史文件哈希：C13 61/61 hash-match（.audit/s1-02c-baseline.sha256）；S1-01、A/B1/B2/B3、B2-effective 未修改。
7. Phase 0 final：sha256sum -c FINAL_CHECKSUMS.sha256 65/65 OK、exit 0，与冻结清单一致。
8. 新增收口文件自查：无正式配额数字、专家人数或招聘承诺（命中的“500 条分配”“已联系”字样都是否定句或验收检查本身的措辞）；candidate_id 全词匹配检查无任何 CSV 外新 id；computing_math A/B 仍并行未裁决；地区、语言、合作方式与预算仍为待确认；无新增对外联系行为。
9. 新增文件哈希（本轮生成后实测）：S1_PHASE1_HANDOFF_REPORT.md 与 S1_PHASE1_HANDOFF_CHECKLIST.csv 见第 13 节。

## 13. 本轮新增与修改文件的最终哈希

| 文件 | 动作 | 版本 | SHA-256 |
|---|---|---|---|
| S1_02C_BUSINESS_REVIEW_REPORT.md | 修改（U6 三处勘误） | S1-02C-U6.1 | 8f0a7b9fff1ddd37b9fba21039e86ff34ba815ae41f612056a9a42bcb3b261f0 |
| S1_02C_EXPERT_PERSONA_DRAFTS.md | 修改（U6 三处勘误） | S1-02C-U6.1-P1 | d2edac912bd9327040fd284c7e4fa0681052bad2079bc0cb62cdf7b329b865d0 |
| S1_PHASE1_HANDOFF_REPORT.md | 新增 | H-1.0 | 见收口回报（本表落盘后实测） |
| S1_PHASE1_HANDOFF_CHECKLIST.csv | 新增 | C-1.0 | 见收口回报（本表落盘后实测） |

## 14. 停止条件核对

- U6 三处残留文档问题已修正（第 2 节与第 13 节勘误记录）。
- 35 与 36 正常校验均通过；两套 self-test 均通过。
- 五张统一 CSV 哈希与 fingerprint 一致（如含字数的非标准清单口径，第 12 节）。
- Phase 0、官方输入、A/B1/B2/B3 历史文件与候选原始表未修改（C13 61/61、Phase 0 65/65）。
- 阶段报告与交接清单已生成（S1_PHASE1_HANDOFF_REPORT.md、S1_PHASE1_HANDOFF_CHECKLIST.csv）。
- 没有新增候选、配额、专家人数或招募承诺（第 12 节第 8 条）。
- 所有 UNKNOWN、条件决策和开放决策均保留，未强行闭合（第 7、8 节与清单 status 列）。

停止，不启动：实际专家招募、专家访谈、专家试标、20–30 条试点、平台开发、P1 工程实现、正式配额分配、专家人数计算。