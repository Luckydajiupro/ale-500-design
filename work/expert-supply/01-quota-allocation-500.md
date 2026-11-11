# 01 500 条配额：14 域分配、子域/族覆盖、首批 5 条与分批计划

> 本文回答：500 条任务如何在 14 个 domain_code、48 个非 CS 子域、72 个任务族之间分配；`agriculture_env` 的缺口怎么补；首批 3 个类目 5 条任务选什么；需要多少专家、分几批、每批放行条件是什么。
> 数据源：`stages/s1-research/S1_01_CATEGORY_MAPPING.csv`（14 域权威清单）、`stages/s0-baseline/08_coverage_matrix_draft.csv`（12 类目草案）、`stages/s1-research/S1_02C_*`（174 候选、72 族、50 能力组、9+7 风险组）。
> 结论：配额定为 500；`agriculture_env` 新纳入 16 条，从 education/other/transport/visual 各减 4 条；`computing_math` 保持 0；首批法律 2 条、神经影像 2 条、建筑节能 1 条，共 5 条；产能需 26 人并行、全年签 62 人、9.3 个日历月。

## 1. 先分清六个数字，后面所有推导都只从 500 出发

| 概念 | 数值 | 是什么 | 不是什么 |
|---|---|---|---|
| 交付配额 | 500 | 合作方验收的原创任务总数 | 不是官方 122 条，也不是 174 条候选 |
| 研究候选 | 174 | 阶段 1 从官方 122 条和公开来源整理的可借鉴工作流 | 不是可交付任务，不承诺全部生产 |
| 任务族 | 72 | 阶段 1 的工作流结构，用于去重和配题 | 不是 72 条任务，也不是 72 个专家 |
| 专家能力组 | 50 | 招聘与评审的能力标签（ECG-01..50） | 不是 50 个人，一个人可覆盖多组 |
| 试点任务 | 5 | batch 0 的 5 条，用于校准流程，不计入 500 | 不是配额的一部分，不对外称“首批交付” |
| 专家人数 | 26 并行 / 62 签约 | 由 500 条工时反推的在岗与签约人数 | 不是 174、72、50 中任何一个 |

规则：任何“从 174 推 500”“从 72 族平均分 500”的算法都不成立。本文的 500 先由官方覆盖与项目口径定，再由工时模型反推专家人数。

## 2. 14 个 domain_code 的最终配额

官方域由 13 个命名域加 `Other` 组成，共 14 个 domain_code；`stages/s1-research/S1_01_CATEGORY_MAPPING.csv` 是权威清单。总数为 500，占比按 500 计。`official_count` 是阶段 0 统计的官方目录任务数，只作覆盖参考，不参与加总。

| domain_code | 中文名 | official_count | proposed_tasks | 占比 | 依据 | 资料授权风险 | 工程风险 | 专家供给风险 | 是否首批 |
|---|---|---:|---:|---:|---|---|---|---|---|
| business_finance | 商业与金融 | 19 | 50 | 10.0% | 官方 19、候选 28、15 族；公开报表与合成台账多，工程低；保持草案 50 | 中（AUTH-02/03 客户与员工数据） | 低-中 | 低 | 否 |
| education_info | 教育与信息 | 2 | 32 | 6.4% | 官方仅 2、候选 9、活跃 2 族；草案 36 减 4 支援农业；教育技术零覆盖 | 低（AUTH-01/02 教材与课程版权） | 低 | 中 | 否 |
| engineering | 工程与建筑 | 16 | 50 | 10.0% | 官方 16、候选 34、12 活跃族；工程风险最高，配额不放大；建筑节能试点 1 条、B3 3 条 | 中（AUTH-05/06 规范与软件许可） | 高 | 中 | 是（仅试点 1 条） |
| health_medicine | 健康与医学 | 19 | 60 | 12.0% | 官方 19、候选 23、7 族；临床/影像/试验链最长，配额最高；隐私风险高 | 高（AUTH-03/04/08） | 高 | 中 | 否 |
| legal | 法律 | 2 | 36 | 7.2% | 官方 2、候选 8、2 族；配额远高于官方，因首批需要且公开判决可验证 | 中（AUTH-03/05 案卷与保密） | 低 | 中 | 是（试点 2 条） |
| life_sciences | 生命科学 | 12 | 48 | 9.6% | 官方 12、候选 18、8 族；公开组学与结构数据多；保持草案 48 | 中（AUTH-02/04/08） | 中 | 中 | 否 |
| other | 其他 | 2 | 28 | 5.6% | 官方 2、候选 0、2 个临时族；草案 32 减 4 支援农业；体育 14 + 兜底 14 | 低-中（AUTH-01/03 赛事图像与个人信息） | 低 | 中 | 否 |
| physical_sciences | 自然科学 | 14 | 46 | 9.2% | 官方 14、候选 16、7 族；公开观测与计算数据多；保持草案 46 | 低-中（AUTH-06 软件与仪器数据） | 中 | 中 | 否 |
| psychology_neuro | 心理与神经 | 3 | 34 | 6.8% | 官方 3、候选 7、4 族；神经影像首批 2 条；保持草案 34 | 高（AUTH-03/04/08 影像与知情同意） | 中 | 低 | 是（试点 2 条） |
| social_sciences | 社会科学 | 1 | 34 | 6.8% | 官方 1、候选 4、2 族；经济学单子域，注意同质化；保持草案 34 | 低（AUTH-02/03 调查微观数据） | 低 | 中 | 否 |
| transport_safety | 交通与安全 | 2 | 30 | 6.0% | 官方 2、候选 9、仅消防 1 族；草案 34 减 4；航空/海事零覆盖 | 中（AUTH-05/07 事故报告与第三方） | 中 | 高 | 否 |
| visual_media | 视觉与媒体 | 11 | 36 | 7.2% | 官方 11、候选 9、5 族；草案 40 减 4；B3 为主，版权风险高 | 中（AUTH-01/07 素材、字体、音乐） | 中 | 中 | 否 |
| agriculture_env | 农业与环境 | 0 | 16 | 3.2% | **草案漏项**；官方 0、候选 9、1 族（env_water）；新纳入 16 | 低-中（AUTH-02/04/06 水文数据与机构许可） | 中 | 高 | 否 |
| computing_math | 计算数据数学 | 19 | 0 | 0.0% | **项目口径排除**，非官方口径；官方 19 条留作研究参考 | — | — | — | 否 |
| **合计** | | **122** | **500** | **100.0%** | | | | | |

校验：50+32+50+60+36+48+28+46+34+34+30+36+16+0 = 500。13 个非零域，1 个零域。

### 2.1 与草案的差异只动四刀

草案 12 类目合计 500，但漏了 `agriculture_env`。本表加 16 条，同时从四个“配额高于官方覆盖需要”的域各减 4 条：

| 域 | 草案 | 本表 | 差额 | 理由 |
|---|---:|---:|---:|---|
| education_info | 36 | 32 | -4 | 官方仅 2、活跃 2 族；32 条仍是官方 16 倍 |
| other | 32 | 28 | -4 | 候选为 0，两个临时族；28 条已足够覆盖 |
| transport_safety | 34 | 30 | -4 | 仅消防 1 族可做，航空/海事零覆盖 |
| visual_media | 40 | 36 | -4 | 候选仅 9、B3 占多；36 条仍高于官方 3 倍 |
| agriculture_env | 0 | 16 | +16 | 补上唯一被静默丢掉的有活跃子域的域 |

四个域各减 4，是“减覆盖最薄或最溢出的部分”，不是按比例削。education 与 other 的削减幅度最大，因为它们的草案配额最缺乏候选支撑。

### 2.2 `agriculture_env` 缺口的两种处理

**方案 A：纳入并重分配（推荐）**

- 配额 16，全部落在 `env_water`（环境建模/水），用 `WF-WATER` 一个族承接；`precision_agriculture` 仍为零，作为已知空覆盖登记，不硬凑。
- 代价一：education/other/transport/visual 各少 4 条，其中 transport 只剩消防，视觉只剩 3 个活跃子域，覆盖会更集中。
- 代价二：`env_water` 的 16 条与 engineering 的 `WF-WATER` 5 条同族，去重与评审要合并看，不能各自按 21 条算。
- 代价三：农业环境类专家池最薄（候选 9、无人脉），首批不排，必须提前 8 周启动招募，否则 B3 会卡。
- 收益：13 个非 CS 域都有非零配额，S1 映射里的 `env_water` 不再是有候选却零任务的“纸面覆盖”；配合 `computing_math = 0` 的项目口径，14 域表完整，但不能说“任务全覆盖”。

**方案 B：暂时为零**

- 理由只能写成：官方 0 条、草案未列、无首批需求、专家池未建。
- 代价：`env_water` 的 9 个候选永远不进生产，S1 的 55 子域覆盖表出现一个“有候选、零任务”的洞；合作方若按 14 域验收，会被追问；后续再补要重开配额，已经排好的批次全部顺延。
- 不推荐 B。唯一可接受的 B 变体是“B 只到 2027-03-31，之后必须重开”，这会增加一次配额变更，不如一次定清。

**推荐 A 的理由**：16 条只占 3.2%，四个来源域各让 4 条不伤主线；换来 13 个非 CS 域口径完整和一条可复用的水环境专家线。若项目负责人坚持 B，必须在 00-README 的待决项里写明“13 个非 CS 域口径暂不成立”。

### 2.3 `computing_math = 0` 是项目口径

官方 `computing_math` 有 19 条，与 health、business 并列官方最多。项目把 CS/计算类整体排除在 500 之外，理由是：官方已有 19 条可作参考、团队与专家供给偏工程侧、阶段 2 的验证资源优先给非 CS。这个 0 不是官方统计，也不是“该类目没有任务”，而是**本项目本阶段不做**。

后果要写清：对外不能声称“覆盖 ALE 全部 14 域的任务生产”；`S1_01_CATEGORY_MAPPING.csv` 里 computing_math 的 7 个子域、19 条官方、0 条候选，全部留在研究视图。若后续 A/B 决策改为纳入，500 必须重开，不能从现有 13 域里静默抽走 19 条。

## 3. 子域与任务族：42 个官方活跃子域 + `other` 兜底，6 个零覆盖

非 CS 共 48 个子域。本配额覆盖 42 个官方活跃子域，另有 `other` 兜底 code；零覆盖 6 个：`chemical_process`、`mining_petroleum`、`precision_agriculture`、`aviation`、`maritime_port`、`educational_technology`。computing_math 的 7 个子域不计。

下表的“族（条）”是配额落到族后的结果，括号内为该族任务数；同一族跨两个子域时分行写。

| 域 | 覆盖的子域（条） | 族（条） | 零覆盖子域 | 处理决定 |
|---|---|---|---|---|
| business_finance | accounting 8、actuarial_risk 6、enterprise_analytics 8、compliance 6、hr_pm 7、sales_marketing 3、quant_finance 7、supply_chain 5 | FIN-REPORT 4、AUDIT 4、ACTUARIAL 6、PREDICTIVE 4、FORECAST 4、FINCRIME 6、DATA-PROTECT 3、HR-GOV 2、PROJECT-MGMT 2、MARKETING 3、QUANT-VALID 4、INVEST-COMPLIANCE 2、DATA-LICENSING 1、TRADE-COMPLIANCE 2、SUPPLY-CHAIN 3 | 无 | 15 族全用；DATA-LICENSING 只 1 条，作为观察族，不扩 |
| education_info | library_info 16、translation 16 | LIBRARY 16、L10N 16 | educational_technology | 教育技术不做；图书馆与本地化各 16，注意 L10N 全是 B3 |
| engineering | aerospace_mech 12、manufacturing 3、civil_geo 8、electronics 4、semiconductor 6、robotics 5、urban_planning 2、energy_power 10 | STRUCT-FEA 6、THERMAL 3、METRO-QUALITY 6（aerospace 3 + manufacturing 3）、ELECTRONICS-HW 4、SEMI-EDA 6、ROBOTICS 5、WATER 5、GEOSPATIAL 3、TRANSPORT 2、POWER-SYS 5、BUILDING-ENERGY 3、NUCLEAR-SAFETY 2 | chemical_process、mining_petroleum | 两个零覆盖不补；化工与矿业需要现场/工艺资料，首批不碰 |
| health_medicine | clinical_diagnostics 18、therapeutic_oncology 12、clinical_informatics 10、public_health 11、clinical_trials 9 | DIAG-IMAGING 10、PATHOLOGY 8、ONCOLOGY 10、MED-PHYSICS 2、CLIN-INFORMATICS 10、PUBLIC-HEALTH 11、CLIN-TRIALS 9 | 无 | 5 子域全覆盖；临床数据一律脱敏或合成 |
| legal | legal_research 20、litigation 16 | LEGAL-RESEARCH 20、LITIGATION 16 | 无 | 首批全部；只用公开判决/法规/合成案卷 |
| life_sciences | biomolecular 14、genomics 10、cell_imaging 14、systems_microbial 10 | STRUCT-BIO 6、COMP-STRUCT-BIO 8、GENOMICS 10、CELL-IMAGING 8、RESEARCH-DATA 6、CLIN-MICRO 3、SYSTEMS-BIO 3、MICROBIOME 4 | 无 | 8 族全用；RESEARCH-DATA 跨 batch，注意与神经影像的数据整理别重 |
| other | sports 14、other 14 | OTHER-SPORTS 14、OTHER-CATCHALL 14 | 无 | 两个临时族，必须由负责人逐条批准；catch_all 不得自动放行 |
| physical_sciences | physics 2、chemistry_materials 14、astronomy 14、earth_atmo 16 | RADIATION-PROT 2、MATERIALS 10、CHEM-REG 4、ASTRO-OBS 7、ASTRO-INFER 7、ATMOS 8、GEOPHYS 8 | 无 | physics 只 2 条（辐射防护），说明物理主线薄弱；不硬拉 |
| psychology_neuro | comp_neuro 18、exp_psychology 16 | NEUROIMAGING 12、COG-MODEL 6、BEHAV-RESEARCH 10、EVIDENCE-SYNTH 6 | 无 | 神经影像首批 2 条；行为与证据合成放 B2 |
| social_sciences | economics 34 | SURVEY-STATS 17、ECON-EVAL 17 | 无 | 单子域 34 条，必须用两个族分开，避免同一模板 |
| transport_safety | fire_safety 30 | FIRE 30 | aviation、maritime_port | 只做消防；航空/海事零覆盖，不假装覆盖 |
| visual_media | animation_3d 10、graphic_design 14、audio_music 12 | 3D-ANIM 10、PRINT 8、A11Y 6、AUDIO 8、AV-ARCHIVE 4 | 无 | 5 族全用；A11Y 依赖 Windows 读屏，放 B4 |
| agriculture_env | env_water 16 | WATER 16 | precision_agriculture | 新纳入；精准农业零覆盖 |
| computing_math | 0 | 0 | 全部 7 个 | 项目口径排除 |

### 3.1 为什么不是平均分配

- 官方覆盖是底线：official_count 高的域（health 19、business 19、engineering 16、physical 14、life 12）配额不低于 46；visual 官方 11 但版权风险高，压到 36；官方仅 1-3 条的 legal/psych/social/education/transport 则按“可验证性 + 首批需要”给到 30-36。
- 候选密度是上限：174 条候选里 business 28、engineering 34、health 23，所以这三域拿 50-60；other 候选 0，只给 28；agriculture 候选 9，只给 16。
- 工程风险是折扣：engineering 工程风险 high、health high，配额不再放大；transport 只剩消防，30 条已是单族上限。
- 专家供给是约束：transport/agriculture 供给风险高，配额压低并放后批；legal/psych 供给低，可首批。
- 同质化是隐形上限：social 只有 economics 一个子域，34 条必须两族各 17，不能再多；physics 只有 2 条，不为了“物理看起来重要”硬加。

### 3.2 族的使用规则

- 72 族中 65 族进入本配额，2 个临时族（OTHER-SPORTS、OTHER-CATCHALL）为“other”新增，合计 67 个族 ID 出现在配额表。
- 未进入配额的 7 族全部因零覆盖子域：PROCESS-ENG、PETRO、MINING、PRECISION-AG、AVIATION、MARITIME、INSTRUCTION。它们保留在研究视图，不删。
- 单成员族（15 个）不强行扩成多族；配额落在族内时允许“一族多条”，但同一族内必须至少有两个不同工作流变体，不能 6 条一个模板。
- 跨子域族（WATER、METRO-QUALITY、A11Y）必须在 CSV 里拆行，避免评审时把两个子域算成一个。

## 4. 首批：3 个类目、5 条任务

### 4.1 选法

同时满足五个条件才进首批：

1. Linux + CPU + 离线可完成，无 Windows/GUI/GPU/外部服务。
2. 资料可公开获取或可合成，不需要运营方授权、案卷调取、患者数据。
3. 有现成专家画像（P2/P3/P4），渠道可在两周内触达。
4. 成功标准能用文件级检查表达，不依赖“专家说好”。
5. 工程侧能在一周内做出可运行的最小环境。

按 100 分打分（Linux/CPU 30、资料 25、专家 20、可验证 15、工程 10）：

| 候选类目 | 得分 | 判断 |
|---|---:|---|
| 法律检索 | 94 | 进 |
| 神经影像 | 88 | 进 |
| 建筑节能 | 82 | 进 |
| 商业财务 | 93 | 备选：画像与资料都够，但首批要覆盖“文本/影像/数值”三种链路，财务与法律同属文本，故让位 |
| 图书馆元数据 | 86 | 备选：与法律同属文本，且专家池窄 |
| 消防 | 71 | 不进：规范资料可公开，但验证需要专业判断，工程侧无现成基准 |
| 无障碍 | 63 | 不进：NVDA/JAWS 依赖 Windows，P5 明确放第二批 |
| 管网水力 | 58 | 不进：EPANET 可离线，但网络拓扑与运行数据需运营方授权 |

### 4.2 五条试点任务

| 编号 | 类目 | 子域 | 族 | 专家画像 | 资料 | 交付物 | 主要验证 |
|---|---|---|---|---|---|---|---|
| P1-01 | 法律检索 | legal_research | LEGAL-RESEARCH | P3 法律研究 | 公开法规 + 公开判决 + 3 份合成解除通知 | 检索 memo、引证表、风险清单 | 引证可回溯、法条现行有效、结论与问题对齐 |
| P1-02 | 法律检索 | litigation | LITIGATION | P3 诉讼支持 | 合成案卷（合同、往来函、时间线） | 争点表、证据目录、时间线 | 争点与证据一一对应、日期无矛盾 |
| P1-03 | 神经影像 | comp_neuro | NEUROIMAGING | P4 神经影像 | 合成 DICOM（3 个序列）+ 假名化表格 | BIDS 目录、侧车 JSON、转换日志 | BIDS validator 通过、字段与源表一致 |
| P1-04 | 神经影像 | comp_neuro | NEUROIMAGING | P4 神经影像 | 公开 BIDS（OpenNeuro CC0）+ 合成事件表 | 预处理报告、质控图、异常清单 | 步骤可复现、参数与报告一致 |
| P1-05 | 建筑节能 | energy_power | BUILDING-ENERGY | P2 建筑性能 | EnergyPlus 示例模型 + 公开 TMY3 + 合成账单 | 能耗基线、节能量表、M&V 方案 | 单位/边界一致、节能量可重算 |

5 条全部在 `work/expert-supply/data/pilot-tasks.csv`。试点不计入 500，试点专家产出的任务若要进 500，必须按正式流程重做资料授权与评审，不能直接计数。

### 4.3 首批的停止条件

- 11-21 签不到 3 人：暂停，换渠道组合，延长一周；仍不到 2 人则停 pilot，升级项目负责人。
- 11-28 签不到 5 人：用 4 人跑，砍掉 P1-05；少于 3 人停。
- 12-12 试点验收少于 4/5：不进入 B1 放量，先修模板与环境；连续两轮少于 3/5 则停。
- 5 条里出现 2 条以上“资料无法授权”：说明选题偏了，重选而不是硬做。

## 5. 专家产能模型：500 条需要多少人

### 5.1 公式与结果

- 单条专家工时按域加权：`Σ(配额 × 域工时) / 500 = 16.9 小时/条`。
- 总工时：按域配额加权求和为 `8,452 小时`，均值 `16.9 小时/条`。
- 人月（FTE）：`8,452 / 160 = 52.8 人月`。
- 每人每月可用 40 小时（10 小时/周，v0 区间 8–16 的中位偏低）：`40 / 16.9 = 2.37 条/人月`。
- 并行 26 人：毛生产月 `8,452 / (26 × 40) = 8.1 个月`；乘 1.15 爬坡与返修 = `9.3 个日历月`。
- 4 个 cohort、每个 13 人、每人 4 个月 engagement：`52` 个“专家-批次”席位；按 15% 流失，签约 `ceil(52 / 0.85) = 62` 人。

域工时假设：business 14、education 16、engineering 22、health 20、legal 12、life 18、other 14、physical 18、psych 16、social 14、transport 18、visual 16、agriculture 18。全部标“假设”，来自专业复杂度与资料准备量，不是实测。

### 5.2 五个概念不要混

| 说法 | 数值 | 用法 |
|---|---:|---|
| 配额 | 500 条 | 对外承诺与验收 |
| 并行专家 | 26 人 | 排期与 office hour 容量 |
| 签约专家 | 62 人 | 招聘漏斗目标，含流失替换 |
| 专家-批次席位 | 52 个 | 4 个 cohort × 13 人，每人 4 个月 |
| 试点专家 | 5 人 | batch 0，不进入 500 计算 |

### 5.3 敏感性

| 单条工时 | 总工时 | FTE 人月 | 26 人日历月 |
|---:|---:|---:|---:|
| 12 h | 6,000 | 37.5 | 6.6 |
| 16.9 h | 8,452 | 52.8 | 9.3 |
| 22 h | 11,000 | 68.8 | 12.2 |
| 28 h | 14,000 | 87.5 | 15.5 |

每周投入 6/10/15/20 小时，对应 1.42/2.37/3.55/4.73 条/人月；26 人完成 500 条需 13.5/8.1/5.4/4.1 个月。若合作方要求 6 个月内交付，26 人不够，需要 34–40 人并行，签约数升到 80–95；这是费用与排期的硬约束，必须由项目负责人先定交付日。

### 5.4 每批要多少人

| 批次 | 任务 | 并行专家 | 签约（含流失） | 周期 |
|---|---:|---:|---:|---|
| B0 试点 | 5 | 5 | 5 | 4 周 |
| B1 | 120 | 13 | 16 | 4 个月 |
| B2 | 128 | 13 | 16 | 4 个月（与 B1 并行） |
| B3 | 126 | 13 | 15 | 4 个月（与 B4 并行） |
| B4 | 126 | 13 | 15 | 4 个月 |
| 合计 | 500 | 26 并行 | 62 | 9.3 个月 |

## 6. 分批计划与放行条件

| 批次 | 类目 | 任务 | 专家 | 依赖 | 放行条件 |
|---|---|---:|---:|---|---|
| B0 试点 | 法律、神经影像、建筑节能 | 5 | 3→5 | 任务模板 v1、P1 字段冻结、三份资料包 | 5 条中至少 4 条通过内容评审 + 工程 smoke；专家反馈“模板可独立填写” |
| B1 | legal 36、business 50、social 34 | 120 | 13 | B0 模板修订、法律资料包、财务公开数据清单 | B0 放行；13 人认证通过；首批 10 条预检无阻断 |
| B2 | psych 34、life 48、physical 46 | 128 | 13 | B0 神经影像结论、公开组学/观测数据清单 | B0 放行；13 人认证；影像与组学各 1 条 shadow review 通过 |
| B3 | health 60、engineering 36、agriculture 16、other 14 | 126 | 13 | 临床脱敏流程、工程环境基线、水文资料授权 | B1/B2 至少一批放行；临床数据政策签字；农业专家到岗 |
| B4 | engineering 14、education 32、visual 36、transport 30、other 14 | 126 | 13 | 无障碍 Windows 环境、版权清单、消防规范包 | B3 放行；Windows 决策明确；版权清单逐条 cleared |

批次合计：120 + 128 + 126 + 126 = 500。engineering 50 拆成 B3 36 + B4 14；other 28 拆成 B3 14 + B4 14。以 `data/quota-allocation.csv` 的 `batch` 列为准。

### 6.1 时间表

| 时间 | 动作 | 放行/检查 |
|---|---|---|
| 11-12–11-14 | 冻结模板、资料政策、试点 5 条 brief | 模板 v1 可发给专家 |
| 11-17–11-28 | 试点招募 3→5 人；签 5 | 11-21 检查 3 人；11-28 检查 5 人 |
| 12-01–12-12 | 5 条试点生产、评审、工程 smoke | 12-12 pilot gate，≥4/5 |
| 11-24–12-31 | B1/B2 扩招到 32 签约 | 12-31 检查 26 在岗；不足则 B1 顺延 2 周或减 20 条 |
| 01-05–04-30 | B1+B2 生产 | 每月 10% 抽检；3 月中期 gate |
| 05-03–08-31 | B3+B4 生产 | 6 月中期 gate；8 月全量预检 |
| 09-01–09-10 | 缓冲、返修、交付包 | 500 条全绿才交付 |

### 6.2 放行闸门（每批都过）

1. 该批 100% 任务有 `task_source.json` 十块，字段无空。
2. 资料授权状态逐条为 `cleared` 或 `synthetic`，无 `pending`。
3. 工程预检：环境可构建、依赖可离线、validator 可跑。
4. 评审：高风险 100% 人工，中风险 1 名独立评审，低风险自动 + 10% 抽检。
5. 该批专家认证通过率 ≥ 80%，未通过者只做 shadow。
6. 上一批返修率 ≤ 15%，否则先修模板再开下一批。

## 7. 每域的风险与缓解

| 域 | 主要风险 | 缓解 | 失败信号 |
|---|---|---|---|
| business_finance | 客户数据与员工数据；财务口径争议 | 只用公开报表/合成台账；口径写在 success_criteria | 评审无法重算 |
| education_info | 教材/课程版权；教育技术零覆盖 | 用开放课件或自编材料；不碰教育技术 | 授权链断 |
| engineering | 规范版权、商业软件、Windows 工具 | 公开规范/开源求解器；建筑节能先用示例模型 | 环境构建失败 |
| health_medicine | 患者数据、IRB、临床阈值 | 合成/脱敏；阈值必须有公开指南依据 | 无法说明数据来源 |
| legal | 案卷保密、律师-客户特权 | 公开判决 + 合成案卷；不做真实咨询 | 出现真实当事人信息 |
| life_sciences | 数据库条款、同意范围、再识别 | 公开汇总数据；不使用受控访问数据 | 数据使用条款禁止商用 |
| other | 赛事图像、个人信息；兜底族质量 | 逐条负责人批准；sports 用公开统计 | catch_all 无实质工作流 |
| physical_sciences | 软件许可、仪器原始数据 | 公开观测数据 + 开源工具 | 依赖不可得 |
| psychology_neuro | 影像同意、IRB、再识别 | 合成 DICOM；公开数据集需查条款 | BIDS 字段与源表冲突 |
| social_sciences | 调查微观数据许可；单子域同质化 | 公开聚合数据；两族各 17 条 | 10 条像同一个模板 |
| transport_safety | 事故报告版权；航空/海事零覆盖 | 只做消防；公开 NFPA/国标摘要 | 需要专有报告 |
| visual_media | 素材、字体、音乐版权；Windows 工具 | 开放素材 + 自建；A11Y 放 B4 | 授权无法逐条 cleared |
| agriculture_env | 水文数据机构许可；专家池薄 | 公开流域数据 + 合成监测；提前 8 周招募 | 招不到人 |

## 8. 自检

- 配额求和：13 个非零域合计 500；加 computing_math 0 仍 500。
- 子域：55 个官方子域，去掉 computing_math 的 7 个，剩 48 个非 CS 子域；其中 42 个有配额、6 个零覆盖。`data/quota-allocation.csv` 出现 43 个 subdomain_code，多出的 1 个是 `other` 兜底 code，不是官方子域，CSV 已注明。
- 首批：3 类目 5 条，全部无 Windows/GPU/外部服务。
- 专家：26 并行 × 2.37 条/月 × 8.1 月 ≈ 500（毛月取整）；52 席位 / 0.85 = 62 签约。
- 每域都有画像与资料路径：见 02 与 `data/category-profile-matrix.csv`。
