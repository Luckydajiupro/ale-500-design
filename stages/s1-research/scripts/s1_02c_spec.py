# -*- coding: utf-8 -*-
"""S1-02C 归并与风险收敛规格（纯数据，供 34_build_s1_02c.py 使用）。

本文件只定义裁定规则与人工覆盖项，不读取也不写回任何历史交付物。
所有关键词筛查均为机械初筛（mechanical screening），不是法律意见、不是合规结论、
不是专家背书；命中不等于风险成立，未命中也不等于已清权。
"""

# ---------------------------------------------------------------- 族归属
# 前缀默认族。键为 candidate_id 去掉 _wfNN 后的前缀。
PREFIX_DEFAULT = {
    "eng_aerospace": "WF-STRUCT-FEA",
    "eng_chemproc": "WF-PROCESS-ENG",
    "eng_civilgeo": "WF-WATER",
    "eng_electronics": "WF-ELECTRONICS-HW",
    "eng_energypower": "WF-POWER-SYS",
    "ag_envwater": "WF-WATER",
    "legal_research": "WF-LEGAL-RESEARCH",
    "legal_litigation": "WF-LITIGATION",
    "eng_manufacturing": "WF-METRO-QUALITY",
    "eng_mining": "WF-PETRO",
    "ag_precision": "WF-PRECISION-AG",
    "eng_robotics": "WF-ROBOTICS",
    "eng_semiconductor": "WF-SEMI-EDA",
    "eng_urban": "WF-TRANSPORT",
    "phys_phys": "WF-METRO-QUALITY",
    "phys_chem": "WF-MATERIALS",
    "phys_astro": "WF-ASTRO-OBS",
    "phys_earth": "WF-ATMOS",
    "life_biomol": "WF-STRUCT-BIO",
    "life_genom": "WF-GENOMICS",
    "life_cellimg": "WF-CELL-IMAGING",
    "life_sysmic": "WF-MICROBIOME",
    "med_diag": "WF-DIAG-IMAGING",
    "med_onco": "WF-ONCOLOGY",
    "med_inform": "WF-CLIN-INFORMATICS",
    "med_pubhealth": "WF-PUBLIC-HEALTH",
    "med_trials": "WF-CLIN-TRIALS",
    "psy_comp": "WF-NEUROIMAGING",
    "psy_exp": "WF-BEHAV-RESEARCH",
    "biz_acc": "WF-FIN-REPORT",
    "biz_act": "WF-ACTUARIAL",
    "biz_ana": "WF-PREDICTIVE",
    "biz_cmp": "WF-FINCRIME",
    "biz_hr": "WF-HR-GOV",
    "biz_mkt": "WF-MARKETING",
    "biz_quant": "WF-QUANT-VALID",
    "biz_sup": "WF-TRADE-COMPLIANCE",
    "soc_econ": "WF-SURVEY-STATS",
    "vm_anim": "WF-3D-ANIM",
    "vm_gra": "WF-PRINT",
    "vm_aud": "WF-AUDIO",
    "ts_avi": "WF-AVIATION",
    "ts_mar": "WF-MARITIME",
    "ts_fir": "WF-FIRE",
    "edu_edt": "WF-INSTRUCTION",
    "edu_lib": "WF-LIBRARY",
    "edu_trn": "WF-L10N",
}

# 依据工作对象而不是子领域改判的条目（逐条读过 workflow_title 后确定）。
ID_OVERRIDE = {
    "eng_aerospace_wf01": "WF-THERMAL",
    "eng_aerospace_wf03": "WF-METRO-QUALITY",
    "eng_civilgeo_wf01": "WF-GEOSPATIAL",
    "eng_civilgeo_wf04": "WF-STRUCT-FEA",
    "eng_electronics_wf02": "WF-SEMI-EDA",
    "eng_energypower_wf03": "WF-BUILDING-ENERGY",
    "eng_energypower_wf04": "WF-NUCLEAR-SAFETY",
    "eng_mining_wf03": "WF-MINING",
    "eng_mining_wf04": "WF-MINING",
    "eng_urban_wf02": "WF-GEOSPATIAL",
    "phys_phys_wf01": "WF-MED-PHYSICS",
    "phys_phys_wf03": "WF-RADIATION-PROT",
    "phys_phys_wf04": "WF-NUCLEAR-SAFETY",
    "phys_chem_wf03": "WF-CHEM-REG",
    "phys_astro_wf03": "WF-ASTRO-INFER",
    "phys_astro_wf04": "WF-ASTRO-INFER",
    "phys_earth_wf03": "WF-GEOPHYS",
    "phys_earth_wf04": "WF-GEOPHYS",
    "life_biomol_wf03": "WF-COMP-STRUCT-BIO",
    "life_biomol_wf04": "WF-COMP-STRUCT-BIO",
    "life_biomol_wf05": "WF-COMP-STRUCT-BIO",
    "life_cellimg_wf04": "WF-RESEARCH-DATA",
    "life_sysmic_wf01": "WF-CLIN-MICRO",
    "life_sysmic_wf02": "WF-SYSTEMS-BIO",
    "life_sysmic_wf03": "WF-RESEARCH-DATA",
    "med_diag_wf03": "WF-PATHOLOGY",
    "med_diag_wf04": "WF-PATHOLOGY",
    "med_onco_wf01": "WF-MED-PHYSICS",
    "psy_comp_wf03": "WF-COG-MODEL",
    "psy_exp_wf04": "WF-EVIDENCE-SYNTH",
    "biz_acc_wf02": "WF-AUDIT",
    "biz_acc_wf04": "WF-AUDIT",
    "biz_ana_wf02": "WF-FORECAST",
    "biz_hr_wf01": "WF-DATA-PROTECT",
    "biz_hr_wf02": "WF-PROJECT-MGMT",
    "biz_mkt_wf01": "WF-DATA-PROTECT",
    "biz_quant_wf03": "WF-INVEST-COMPLIANCE",
    "biz_quant_wf04": "WF-DATA-LICENSING",
    "biz_sup_wf02": "WF-FORECAST",
    "biz_sup_wf03": "WF-SUPPLY-CHAIN",
    "soc_econ_wf02": "WF-ECON-EVAL",
    "soc_econ_wf03": "WF-ECON-EVAL",
    "vm_gra_wf03": "WF-A11Y",
    "vm_aud_wf03": "WF-AV-ARCHIVE",
    "edu_edt_wf03": "WF-A11Y",
}

# 第二归属（跨族方法论复用的唯一一例；不重复计入族主计数）。
SECONDARY = {
    "psy_comp_wf01": ["WF-RESEARCH-DATA"],
}

# 跨批次真实重复簇（仅 A 的三对 YES；主归属沿用批次原始裁定，不重新裁决）。
CLUSTERS = [
    {"cluster_id": "DC-HYD-FLOOD",
     "members": ["eng_civilgeo_wf02", "ag_envwater_wf03"],
     "primary": "ag_envwater_wf03",
     "status": "substantively_duplicate_yes_primary_assigned_by_batch_A",
     "note": "同一 HEC-RAS 洪泛区建模工作；civil_geo 侧按 A 批次裁定改为桥梁/涵洞/堤防冲刷与回水的水力设计。"},
    {"cluster_id": "DC-HYD-DIST",
     "members": ["eng_civilgeo_wf03", "ag_envwater_wf04"],
     "primary": "ag_envwater_wf04",
     "status": "substantively_duplicate_yes_high_near_duplicate_merge_undecided",
     "note": "同一 EPANET 配水管网建模工作；A 批次自评 HIGH 近似重复，合并或按“设计 vs 运行”拆分仍待专家裁定。"},
    {"cluster_id": "DC-DFT-ATPG",
     "members": ["eng_electronics_wf02", "eng_semiconductor_wf03"],
     "primary": "eng_semiconductor_wf03",
     "status": "substantively_duplicate_yes_primary_assigned_by_batch_A",
     "note": "扫描链插入与 ATPG 属芯片级 DFT；electronics 侧应改归属半导体或改写为板级 JTAG 边界扫描。"},
]

# ---------------------------------------------------------------- 风险组
# (id, 中文名, 英文名, 严重度, 定义, 机械初筛正则, 彻底解决需要什么, 需要谁回答)
AUTH_GROUPS = [
    ("AUTH-01", "版权与内容再分发", "Copyright and content redistribution", "medium",
     "标准文本、规范、专著、图片、判例与数据库内容的重制、摘引、翻译或再分发权限。",
     [r"copyright", r"all rights reserved", r"redistribut", r"republish", r"fair use",
      r"derivative work", r"版权", r"著作权", r"翻印", r"重制", r"衍生作品"],
     "取得权利人书面许可或确认可依公有领域/合理使用/法定例外使用，并记录许可范围。",
     "该交付物的可再分发范围是否覆盖商业用途与衍生作品？"),
    ("AUTH-02", "数据许可与数据权利", "Data licence and data rights", "medium",
     "数据集、数据库、统计微数据、遥感/交易数据的许可条款、再分发限制与商用限制。",
     [r"(data|dataset|database)[^.;]{0,80}licen", r"data[- ]use", r"\bDUA\b",
      r"data transfer agreement", r"OpenNeuro", r"\bHCP\b", r"CC BY", r"ODbL",
      r"数据使用", r"数据许可", r"数据库", r"使用授权", r"再分发"],
     "逐数据集核对许可与用途，保留 licence ID 与授权凭证；无法确认的按不可用处理。",
     "目标数据集是否允许商业使用、二次分发与模型训练？"),
    ("AUTH-03", "个人信息与隐私", "Personal data and privacy", "high",
     "个人信息、健康信息、影像、声音、肖像与生物特征数据的处理、去标识与最小化。",
     [r"privacy", r"\bPII\b", r"\bPHI\b", r"HIPAA", r"GDPR", r"de-identif", r"anonymi",
      r"personal data", r"个人信息", r"隐私", r"去标识", r"匿名",
      r"肖像", r"生物特征"],
     "完成合法性基础、去标识验证与最小化评估，签署数据处理协议并按留存期限管理。",
     "是否存在可识别个体数据，去标识是否经过独立复核？"),
    ("AUTH-04", "研究伦理与 IRB", "Research ethics and IRB", "high",
     "人体受试者研究、知情同意、生物样本与伦理委员会审查。",
     [r"\bIRB\b", r"ethics (board|approval|committee)", r"informed consent",
      r"human[- ]subjects", r"45 CFR 46", r"伦理委员会", r"伦理审查", r"知情同意", r"受试者"],
     "取得伦理批件与同意范围，确认数据/样本用途在同意范围内。",
     "同意范围是否覆盖本次处理与共享，伦理批件是否仍然有效？"),
    ("AUTH-05", "监管报送与执业签署", "Regulatory submission and professional sign-off", "high",
     "向监管机构报送、法定登记、专业签署与持证执业要求；agent 不能替代签署人。",
     [r"regulatory (submission|filing|approval)", r"accredit", r"professional signature",
      r"professional sign[- ]?off", r"PE stamp", r"stamped by", r"licensed professional",
      r"statutory", r"监管", r"报送", r"执业", r"签署", r"资质", r"注册工程师", r"持证"],
     "明确法定签署人与其资质，把 agent 产出限定为草稿与核查清单。",
     "该交付物是否必须由持证专业人士签署，签署人是谁？"),
    ("AUTH-06", "商业软件与工具许可", "Commercial software and tool licensing", "low_medium",
     "专有软件、Windows/macOS 限定工具、许可证服务器与订阅制工具的使用与替代。",
     [r"proprietary", r"Windows[- ]only", r"Windows[- ]centric", r"Windows GUI",
      r"macOS[- ]only", r"MATLAB", r"\bEULA\b", r"licen[cs]e server",
      r"commercial (software|tool|solver|suite|TPS)", r"专有", r"商业软件",
      r"仅\s*Windows", r"许可服务器"],
     "确认许可证覆盖自动化调用，或替换为开源实现并记录精度差异。",
     "许可证是否允许无 GUI 的批处理调用与结果再分发？"),
    ("AUTH-07", "第三方内容与模型许可", "Third-party content and model licensing", "medium",
     "素材库、字体、音乐同步权/母带权、第三方模型与模型权重、演员肖像与声音授权。",
     [r"stock (footage|photo|image)", r"\bfont\b", r"\btypeface\b", r"\bmusic\b",
      r"sync right", r"master right", r"third[- ]party (model|asset)", r"model weights",
      r"(actor|talent) release", r"素材", r"字体", r"音乐", r"同步权", r"母带",
      r"第三方模型", r"演员"],
     "逐项清权并保留许可证据；无法清权的资产替换或删除。",
     "素材/字体/音乐/模型的授权是否覆盖最终交付形态与地域期限？"),
    ("AUTH-08", "临床与试验数据二次使用", "Clinical and trial data secondary use", "high",
     "临床试验数据、SAE 报告、注册库、EHR 与患者数据的二次使用与披露。",
     [r"clinical trial", r"trial data", r"\bSAE\b", r"\bEHR\b", r"patient data",
      r"临床试验", r"受试者数据", r"病历", r"注册库"],
     "确认二次使用在同意与监管许可范围内，完成去标识与披露审查。",
     "试验数据/病历的二次使用是否已获同意或豁免？"),
    ("AUTH-09", "出口管制与制裁", "Export control and sanctions", "high",
     "出口管制、ITAR/EAR、制裁名单与经济制裁对数据、软件与人员的地域限制。",
     [r"export control", r"\bITAR\b", r"\bEAR\b", r"sanction", r"\bOFAC\b",
      r"出口管制", r"制裁"],
     "做受控物项与人员国籍/地域筛查，必要时申请许可。",
     "交付是否涉及受控技术或受限主体？"),
]

ENG_GROUPS = [
    ("ENG-01", "Linux 生产可用性未验证", "Linux production readiness not verified", "high",
     "四条批次 174/174 均为 NOT_VERIFIED；没有任何候选在 Linux 上完成端到端运行验证。",
     [r"__ALL__"],
     "在 Linux 上端到端跑通并留下可复现日志、输入样例与验收证据。",
     "该工作流在 Linux 上的最小可运行环境是什么，谁来跑首次验证？"),
    ("ENG-02", "专有或 Windows/macOS 限定工具", "Proprietary or Windows/macOS-only tooling", "medium",
     "工作流关键步骤依赖 Windows/macOS 限定或专有商业软件，Linux 侧仅能部分替代。",
     [r"Windows[- ]only", r"Windows[- ]centric", r"macOS[- ]only", r"proprietary",
      r"Abaqus", r"ANSYS", r"MATLAB", r"Eclipse",
      r"ZBrush", r"Maya", r"3ds Max", r"Substance", r"Pro Tools", r"CEDAR", r"iZotope",
      r"baton", r"Vidchecker", r"Esko", r"ArtPro", r"\bJAWS\b", r"\bPAC\b", r"专有",
      r"仅\s*Windows"],
     "取得许可证并保留 Windows 执行节点，或完成开源替代与结果差异评估。",
     "是否接受保留一个 Windows 执行节点，还是必须全 Linux？"),
    ("ENG-03", "GPU 与高性能计算依赖", "GPU and HPC dependency", "low",
     "渲染、训练、仿真或成像重建对 GPU、显存或集群调度的硬性要求。",
     [r"\bGPU\b", r"CUDA", r"\bHPC\b", r"A100", r"RTX", r"显卡", r"显存", r"计算集群"],
     "确认 GPU 型号、显存与驱动版本，或降级到 CPU 路径并记录耗时。",
     "目标环境是否有可调度的同型号 GPU？"),
    ("ENG-04", "专用仪器与硬件", "Specialized instruments and hardware", "medium",
     "测序仪、质谱、显微镜、MRI/MEG、加速器、探测器、机器人与试验台等不可虚拟化硬件。",
     [r"sequencer", r"mass spectrom", r"microscope", r"cytometer", r"flow cytomet",
      r"\bMRI\b", r"\bMEG\b", r"linac", r"accelerator", r"detector", r"robot", r"instrument",
      r"telescope", r"cannot be virtualized", r"hardware[- ]in[- ]the[- ]loop",
      r"仪器", r"风洞", r"试验台", r"开盘机", r"测试带", r"声卡", r"\bLTO\b", r"探测"],
     "确认硬件可得性与排期，或改为公开数据集回放与离线验证。",
     "没有该硬件时，是否接受用公开数据集做离线验收？"),
    ("ENG-05", "权威来源不可达", "Authoritative source unreachable", "medium",
     "标准、监管指引或数据页面返回 403、付费墙、仅摘要，导致条款级核对无法完成。",
     [r"\b403\b", r"paywall", r"paywalled", r"abstract[- ]only", r"not accessible",
      r"could not be (full-text )?read", r"付费", r"无法访问", r"仅摘要", r"未能全文"],
     "通过机构订阅、购买标准或官方公开副本补齐原文，并做条款级复核。",
     "谁提供标准原文或机构订阅，复核由谁签字？"),
    ("ENG-06", "工程闭环未完成", "Engineering closure pending", "medium",
     "批次自身标记 engineering_pending=yes 的候选，环境、脚本或验收尚未闭环。",
     [r"__PENDING__"],
     "按批次 pending 清单逐项闭环并留下证据。",
     "该候选的 pending 项由谁在什么环境闭环？"),
    ("ENG-07", "溯源与重建缺口", "Provenance and rebuild gap", "medium",
     "批次审计链存在补记时间、重建片段或子代理异常，影响结论的可追溯性。",
     [r"__PROVENANCE__"],
     "以产物 mtime 与哈希为准重建时间线，并对受影响片段做独立重跑。",
     "受影响片段的原始字节是否还能取回，谁做独立重跑？"),
]

# A 批次只有 usage_permissions，其余三批有四个授权字段；用于可比性说明。
AUTH_FIELDS_A = ["usage_permissions", "blocking_risks", "platform_dependencies", "verification_approach"]
AUTH_FIELDS_BCD = ["usage_permissions", "data_usage_authorization", "privacy_considerations",
                   "research_ethics", "platform_dependencies", "blocking_risks"]

# 人工覆盖（机械初筛后按逐条阅读修正；每项都要在报告中说明理由）。
AUTH_ADD = {}
AUTH_REMOVE = {}
ENG_ADD = {}
ENG_REMOVE = {}

# uncovered_official：S1-01 无活跃官方任务的子领域清单。
# S1-02C-U1 修订：旧的 UNCOVERED_SUBDOMAINS 只列 B3 三域，且 basis 文案引用
# S1_02B3_SCOPE_MATRIX.csv。构建器现在直接从 S1_01_CATEGORY_MAPPING.csv
# 推导，spec 中这张三域硬编码表已作废，从本文件移除。相关依据见
# .audit/s1-02c-uncovered-correction.md。

# B3 三条恰好 3 行的 padding 风险依据（审计发现，不宣称已证实）。
PADDING_BASIS = (
    "B3 九个官方子领域各恰好 3 行；scripts/32_validate_b3.py:122 对 <3 行硬失败，"
    "而 .audit/s1-02b3-research-brief.md:32-33 允许少于 3 行并附理由，"
    "三个 uncovered_official 子领域也落在恰好 3 行，存在凑数压力；不能证明是凑数。"
)

# B3 溯源事项（写入工程风险与报告，不修改任何历史文件）。
B3_PROVENANCE = {
    "trail_backfill": "S1_02B3 的 .audit/s1-02b3.tsv 末段 L21–L26 时间为收尾补记而非当时记录："
                      "补记的 19:16:30/19:16:40/19:17:00 exit-0 不可复现，因为 "
                      "scripts/31_merge_b3.py:118 在输出已存在时抛 FileExistsError、"
                      "scripts/29_b3_scope_matrix.py:218-220 返回 1、scripts/33_b3_overlap.py:86-87 抛 SystemExit；"
                      "产物 mtime 为 S1_02B3_WORKFLOW_CANDIDATES.csv 19:06:04、"
                      "S1_02B3_SCOPE_MATRIX.csv 19:06:49、.audit/b3_overlap_sweep.csv 19:13:01，时间线以 mtime 为准。",
    "edu_rebuild": "edu 片段在 18:37 冻结门之后于 18:41 重建，evidence/s1_02b3_research/edu_cluster_candidates.csv "
                   "mtime 为 19:05:29、sidecar 为 18:41，被门的原始字节已不可取回；当前文件通过 30_check_fragment_b3.py 14/14。",
    "vm_rebuild": "vm 片段在冻结后按来源精度重建；重建前的字节与重建后不可逐字比对。",
}

EVIDENCE_CLASS_LABEL = {
    1: "E1 + recorded_full_support（仍为记录性支持，非独立验证）",
    2: "E1 + recorded_partial_support，或本批未记录 source_support_mode",
    3: "E1 + 弱支持模式（conditional/judgment/unspecified/uncited/name_reference）",
    4: "E3 + recorded_full/partial，或本批未记录 source_support_mode",
    5: "E3 + 弱支持模式（同上）",
    6: "E4 + 推断性组合证据",
}

# 批次文件与批次标识。
BATCHES = [
    ("A", "S1_02A_EFFECTIVE_CANDIDATES.csv", "S1_02A_WORKFLOW_CANDIDATES.csv",
     "S1_02A_SOURCE_CLAIM_MAP.csv", "S1_02A_DUPLICATE_ATTRIBUTION.csv"),
    ("B1", "S1_02B1_WORKFLOW_CANDIDATES.csv", "S1_02B1_WORKFLOW_CANDIDATES.csv",
     "S1_02B1_SOURCE_CLAIM_MAP.csv", "S1_02B1_DUPLICATE_ATTRIBUTION.csv"),
    ("B2", "S1_02B2_EFFECTIVE_CANDIDATES.csv", "S1_02B2_EFFECTIVE_CANDIDATES.csv",
     "S1_02B2_SOURCE_CLAIM_MAP.csv", "S1_02B2_DUPLICATE_ATTRIBUTION.csv"),
    ("B3", "S1_02B3_WORKFLOW_CANDIDATES.csv", "S1_02B3_WORKFLOW_CANDIDATES.csv",
     "S1_02B3_SOURCE_CLAIM_MAP.csv", "S1_02B3_DUPLICATE_ATTRIBUTION.csv"),
]

# B2 erratum 中五条被更正的行（源支持模式取最弱证据块）。
B2_CORRECTED = {
    "psy_comp_wf01": "uncited_support",
    "psy_exp_wf04": "conditional_support",
    "biz_cmp_wf03": "judgment_support",
    "biz_mkt_wf02": "unspecified_support",
    "biz_quant_wf02": "name_reference_support",
}