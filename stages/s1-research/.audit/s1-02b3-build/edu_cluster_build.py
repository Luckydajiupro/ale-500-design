# -*- coding: utf-8 -*-
"""S1-02B3 edu_cluster builder: 9 workflow candidates (3 per subdomain).

Deliverable: evidence/s1_02b3_research/edu_cluster_candidates.csv (43 columns)
Sidecar:     evidence/s1_02b3_research/edu_cluster.json
Every primary_source_url was fetched with the web tool; see
.audit/s1-02b3-sources-edu_cluster.md for URL, HTTP status, title and the
supporting sentence.
"""
import csv
import json
import os

COLS = [
    "subdomain_code", "subdomain_business_boundary", "subdomain_occupations",
    "candidate_id", "workflow_title", "occupation_scope", "workflow_summary",
    "source_type", "evidence_level", "source_reference", "expert_raw_materials",
    "usage_permissions", "task_input", "professional_operations",
    "expected_deliverable", "success_criteria", "verification_approach",
    "platform_dependencies", "blocking_risks", "expert_capability",
    "cross_domain_overlap", "granularity_check", "pending_confirmation",
    "data_usage_authorization", "privacy_considerations", "research_ethics",
    "reproducibility_assessment", "evidence_kind", "source_category",
    "primary_source_url", "primary_claim", "software_adaptation",
    "linux_verification_state", "expert_pending", "engineering_pending",
    "fragment_path", "duplicate_status", "primary_home", "secondary_tag",
    "source_support_mode", "evidence_scope", "workflow_family_id",
    "process_incident",
]

DERIVED = COLS[32:39]

EDT_COMMON = {
    "subdomain_code": "educational_technology",
    "subdomain_business_boundary": (
        "教育技术（教学设计与学习技术）以课程与学习体验为专业对象，覆盖学习者与情境分析、学习目标与评估对齐、"
        "学习活动与教学媒体设计、学习管理系统（LMS）建课与课程包封装、学习数据埋点与一致性、以及课程质量与可访问性评审。"
        "业务边界排除：学科内容本身的学术审查（属院系学术委员会与同行评议）、校园网络与账号运维（属IT运维）、"
        "教材编辑出版与印前加工（属出版与graphic_design）。签字人：课程负责人（学科教师）与教学设计师共同署名设计说明，"
        "质量评审结论由注册QM评审员或院校教学发展中心签字，开课由院系教学委员会批准。"
    ),
    "subdomain_occupations": (
        "教学设计师（instructional designer）；学习体验设计师（learning experience designer）；"
        "教育技术专员/学习管理系统管理员（educational technologist / LMS administrator）；"
        "课程质量评审员（course quality reviewer, QM peer reviewer）；多媒体教学资源开发员（multimedia learning developer）；"
        "数字可访问性专员（accessibility specialist）；学习分析工程师（learning analytics engineer）；"
        "教师发展顾问（faculty development consultant）。"
    ),
}

LIB_COMMON = {
    "subdomain_code": "library_info",
    "subdomain_business_boundary": (
        "图书馆与情报学以文献与信息资源的描述、组织、保存和提供为专业对象，覆盖原始编目与规范控制、主题分析与分类、"
        "文化遗产数字化与元数据封装、数字保存摄取与长期可用性、以及共享书目数据库的贡献与质量控制。"
        "业务边界排除：商业数据库与订阅销售（属出版与数据商）、档案的行政鉴定与处置（属档案机构，但共享OAIS/PREMIS方法）、"
        "学位论文的学术评价（属院系）。签字人：编目馆员署名记录并对描述准确性负责，编目主管或PCC联络人复核BIBCO级记录；"
        "数字化项目由馆藏主管与馆长共同签署版权状态与发布决定；数字保存摄取由数字保存馆员签署AIP验收单。"
    ),
    "subdomain_occupations": (
        "编目馆员（cataloging librarian）；元数据馆员（metadata librarian）；规范控制馆员（authority control librarian, NACO）；"
        "数字化项目主管（digitization project manager）；影像技术员（imaging technician）；"
        "数字保存馆员（digital preservation librarian）；馆藏发展馆员（collection development librarian）；"
        "图书馆系统馆员（systems librarian）。"
    ),
}

TRN_COMMON = {
    "subdomain_code": "translation",
    "subdomain_business_boundary": (
        "翻译与本地化以跨语言、跨文化的信息转换为专业对象，覆盖笔译生产（翻译—修订—审校，TEP）、术语管理与术语库交换、"
        "软件与文档本地化的文件工程与语言质量评估、以及视听翻译（字幕、 timed text）的计时与交付。"
        "业务边界排除：文学作品的编辑出版与发行（属出版）、口译（ISO 17100:2015 明确不适用于口译）、"
        "机器翻译引擎与语音识别模型研发（属NLP工程）。签字人：本地化项目经理签署交付确认，语言负责人/审校签署语言质量结论，"
        "客户方本地化经理或语言服务采购方验收；涉及认证或法律用途时由具资质的签署译员签字。"
    ),
    "subdomain_occupations": (
        "笔译员（translator）；审校/修订员（reviser）；术语专家（terminologist）；"
        "本地化项目经理（localization project manager）；本地化工程师（localization engineer）；"
        "语言质量评估员（LQA specialist / MQM annotator）；字幕译者（subtitler）；视听翻译质检员（AVT QC reviewer）。"
    ),
}


def row(**kw):
    d = {c: "" for c in COLS}
    d.update(kw)
    for c in DERIVED:
        d[c] = ""
    return d


# ---------------------------------------------------------------- educational_technology
EDT = [
    row(
        **EDT_COMMON,
        candidate_id="edu_edt_wf01",
        workflow_title="Blended Course Instructional Design Package with Quality Matters Review",
        occupation_scope=(
            "教学设计师主导需求分析、目标撰写、评估蓝图与对齐矩阵；学科教师（课程负责人）确认内容准确性、评估效度与学术标准；"
            "多媒体开发员按媒体规格制作视频与交互；教学发展中心的注册QM评审员执行同行评审并签署评审报告；"
            "院系教学委员会据评审结论批准开课。"
        ),
        workflow_summary=(
            "从课程需求与学习者情境分析出发，产出一份学习目标—评估—学习活动—教学材料四向对齐的混合式课程设计包，"
            "并在LMS中建成可运行的课程站点与可移植课程包。随后按Quality Matters高教量规的8项一般标准与44条具体标准做同行评审，"
            "必备（3分）标准全部满足且总分达到85%方可获得认证结论。交付物包括设计说明、对齐矩阵、课程包、QM评审报告与开课审批单。"
        ),
        source_type="industry_supported",
        evidence_level="E3",
        source_reference=(
            "Quality Matters, Higher Ed Course Design Rubric（8 General Standards / 44 Specific Review Standards；"
            "Essential Standards 必过 + 总分≥85% 认证阈值；Alignment 定义见 2.1/2.2、3.1、4.1、5.1、6.1），"
            "https://www.qualitymatters.org/qa-resources/rubric-standards/higher-ed-rubric（2026年访问）；"
            "次要：Quality Matters, QM Rubric（第7版）评分工作簿与同行评审员手册（机构会员资料，未公开获取）；"
            "对齐设计方法参见 Biggs & Tang, Teaching for Quality Learning at University, 4th ed., 2011（constructive alignment）。"
        ),
        expert_raw_materials=(
            "①课程需求书：目标学习者、先修要求、学分学时、交付模式（面授/同步/异步比例）、班级规模；"
            "②学科内容大纲与指定教材/开放教育资源清单（逐项标注版权状态）；③院校课程审批表与学习成果模板；"
            "④LMS课程空壳（Moodle 4.x 或 Canvas 导出包）；⑤既往开课的学生评价汇总与通过率（去标识聚合）；"
            "⑥QM评分工作簿与证据链接模板；⑦无障碍政策与字幕规范。"
        ),
        usage_permissions=(
            "教材与图片：须为已购许可、图书馆授权或CC许可，逐项登记权利人、许可类型与到期日；商业图库、字体与音乐须有网络/印刷授权；"
            "学生评价与成绩数据须去标识并依院校IRB与数据治理政策使用；LMS模板若来自第三方须确认再分发许可；"
            "教师个人讲义与录课视频须取得作者书面同意方可改造与再发布。"
        ),
        task_input=(
            "1门3学分混合式课程：需求书5页PDF、课程大纲DOCX、12个模块讲义PPTX/PDF、38个学习活动草案、评估蓝图XLSX、"
            "LMS导出包（IMSCC，约240 MB）、教材章节扫描件（仅在许可范围内）、既有学生评价聚合表CSV。"
        ),
        professional_operations=(
            "①需求与情境分析（needs_analysis）：访谈课程负责人，核对学习者先修、可用学时与交付模式，形成需求说明；"
            "②学习目标撰写与分类（objectives）：按可观测行为动词编写模块级目标并标注认知层级；"
            "③评估蓝图与对齐矩阵（assessment_blueprint）：为每个目标配置评估任务、权重与评分量规，形成目标-评估-活动-材料四列矩阵；"
            "④学习活动与交互设计（activity_design）：设计异步讨论、形成性测验、同伴互评与协作任务，标注教师投入时长；"
            "⑤教学材料与媒体规格（material_spec）：给出视频时长/字幕/转录要求、图表替代文本、阅读材料版权状态；"
            "⑥LMS建课与课程包导出（lms_build）：在LMS中建立模块、成绩册与完成条件，导出IMSCC并做导入回归；"
            "⑦可访问性与可用性预检（accessibility_precheck）：按WCAG 2.2 A/AA做自动扫描与人工抽查，记录阻断项；"
            "⑧QM同行评审与修订（qm_review）：评审员按44条标准逐条打分并附证据，课程团队修订后复评；"
            "⑨交付与归档（delivery_archive）：冻结版本、归档证据包并提交开课审批。"
        ),
        expected_deliverable=(
            "课程设计说明（DOCX/PDF，含需求分析与对齐矩阵）、评估蓝图（XLSX）、LMS课程包（IMSCC 1.3 或 Common Cartridge 1.3）、"
            "媒体规格与制作清单（CSV）、QM评审报告（44条评分+证据链接+必备标准核对）、修订记录与开课审批单。"
        ),
        success_criteria=(
            "①QM 44条具体标准逐条有证据链接，8项一般标准全覆盖；②所有3分必备标准满足；③总分≥85%（按QM计分口径）；"
            "④对齐矩阵中每个学习目标至少对应1个评估、1个学习活动与1份材料；⑤课程包在目标LMS干净实例导入无错误、内部链接无404；"
            "⑥可访问性预检无Level A阻断项，录播视频100%有同步字幕。"
        ),
        verification_approach=(
            "第三方可用QM评分工作簿独立复评并抽查证据链接；用IMSCC导入器在干净LMS实例重放导入并比对模块数；"
            "用链接检查器扫描全部内部/外部链接；用脚本校验对齐矩阵的三元组完整性（目标→评估→活动→材料）；"
            "核对评审员独立性声明（评审员非本课程教师）与评审日期。"
        ),
        platform_dependencies=(
            "Linux或macOS工作站；LibreOffice/OnlyOffice编辑文档；LMS（Moodle 4.x 或 Canvas）与IMSCC导入；"
            "QM评分工作簿为机构会员在线门户（需注册）；屏幕录制与字幕工具；无需GPU，媒体转码可用CPU。"
        ),
        blocking_risks=(
            "第⑧步QM认证评审须由注册QM评审员通过QM会员门户提交，属会员与服务依赖；"
            "若LMS为学校托管的Canvas云，课程包导入需管理员权限；教材扫描件受版权限制，未获许可不得进入课程包。"
            "残余风险：QM评分含评审员专业判断，复评可能出现±1分差异。"
        ),
        expert_capability=(
            "5年以上高校教学设计师（教育技术/学习科学硕士），熟悉QM量规与同行评审流程；学科教师须有该课程3年以上授课经验；"
            "评审员须完成QM同行评审员培训并保持认证；多媒体开发员须具备字幕与无障碍媒体制作经验。"
        ),
        cross_domain_overlap=(
            "与psy_cluster的psy_exp_wf02（功效论证的实验设计与行为数据分析）不同：psy行关注实验操纵、随机化与统计推断，"
            "本行关注课程设计产品与质量评审门；平面设计域（graphic_design）的教材排版与PDF/UA属另一子域，本批未产出该簇候选、"
            "无法逐行比对，但本行不做印前与PDF/X；与education_info/marc_remediation_folio_overlay、"
            "education_info/yi_manuscript_translation_1无交集；已grep evidence/*/*_candidates.csv 全部11个候选文件，未发现课程设计或质量评审候选。"
        ),
        granularity_check=(
            "覆盖从需求分析到开课审批的完整设计链，含两次评审门（可访问性预检、QM同行评审）与可移植课程包交付；"
            "不是「用Moodle建课」的工具教程，也不是单条QM标准的检查操作。"
        ),
        pending_confirmation=(
            "①QM第7版44条具体标准的条文未逐条获取（annotated rubric为会员制），本行依据公开页面确认的8项一般标准、44条计数、"
            "必备标准与85%阈值表述；②IMSCC 1.3与Common Cartridge 1.3在具体LMS版本的导入兼容性未实测；"
            "③未验证目标院校LMS的完成条件与成绩册同步细节。"
        ),
        data_usage_authorization=(
            "课程材料依院校与教师授权使用；学生数据须聚合去标识，依FERPA（美国）或GDPR第6(1)(f)/6(1)(a)及院校IRB政策处理；"
            "第三方教材依许可协议；无个人数据跨境传输。"
        ),
        privacy_considerations=(
            "学生学习记录（成绩、访问日志、讨论帖）属教育记录：最小化规则为仅取课程级聚合通过率与评价分，不取姓名/学号，"
            "保留期不超过课程改进周期；LMS分析只用汇总口径；学生评价原文不得公开引用；录课视频中的学生影像须单独同意。"
        ),
        research_ethics=(
            "agent负责起草设计说明、对齐矩阵、评审证据清单与修订建议；课程负责人与QM评审员签署最终评审结论，"
            "院系教学委员会签署开课决定；agent不得代替教师作学术内容判断或替代评审员打分。"
        ),
        reproducibility_assessment=(
            "设计与评审过程可复现：输入文件、量规版本与评分工作簿固定后可重放；QM评审员判断与LMS版本差异造成部分不可复现；"
            "会员制评分表限制第三方完全复算，只能复评公开标准部分。"
        ),
        evidence_kind="industry_standard_complete",
        source_category="professional_standard",
        primary_source_url="https://www.qualitymatters.org/qa-resources/rubric-standards/higher-ed-rubric",
        primary_claim=(
            "QM高教课程设计量规以8项一般标准与44条具体标准评审在线与混合课程，必备（3分）标准须全部满足且总分达到85%方可获认证，"
            "并明确学习目标、评估、材料、活动与技术五向对齐（2.1/2.2、3.1、4.1、5.1、6.1）。"
        ),
        software_adaptation="conditional",
        source_support_mode="conditional_support",
        evidence_scope=(
            "needs_analysis=as_recorded;objectives=as_recorded;assessment_blueprint=conditional_E1;"
            "activity_design=as_recorded;material_spec=as_recorded;lms_build=as_recorded;"
            "accessibility_precheck=as_recorded;qm_review=conditional_E1;delivery_archive=as_recorded"
        ),
        workflow_family_id="fc_course_design,fc_quality_review",
        process_incident="none",
    ),
    row(
        **EDT_COMMON,
        candidate_id="edu_edt_wf02",
        workflow_title="xAPI Courseware Instrumentation and Learning Record Store Conformance Package",
        occupation_scope=(
            "教学设计师定义可观测学习行为与能力映射；学习分析工程师设计Statement配置文件并实现埋点；"
            "平台管理员配置LRS端点、认证与传输；数据治理官审批采集目的、保留期与访问权限；"
            "课程负责人确认报表口径与教学解释。"
        ),
        workflow_summary=(
            "从能力模型与学习活动清单出发，设计xAPI Statement配置文件（actor/verb/object/result/context），"
            "在课程包中埋点并把学习事件写入学习记录存储（LRS）。随后用规范校验与一致性测试验证语句合法性、"
            "LRS拒绝规则与报表口径，产出可审计的学习记录数据包与一致性报告。"
        ),
        source_type="industry_supported",
        evidence_level="E3",
        source_reference=(
            "Advanced Distributed Learning (ADL), Experience API (xAPI) Specification, Part Two: Experience API Data"
            "（§2.4 Statement 必备属性 actor/verb/object；§2.6 签名语句；§4.1 扩展键须为IRI；§4.2 语言映射用RFC 5646；"
            "LRS 拒绝规则），https://raw.githubusercontent.com/adlnet/xAPI-Spec/master/xAPI-Data.md（Apache-2.0，2026年访问）；"
            "次要：ADL xAPI LRS Conformance Test Suite（GitHub adlnet/lrs-conformance-test-suite，未下载运行）；"
            "IMS Global, Caliper Analytics 作为对照分析模型（未引用其条款）。"
        ),
        expert_raw_materials=(
            "①课程活动清单与能力框架（competency framework）；②xAPI profile草案：verb IRI清单、activity type、扩展键；"
            "③LMS导出的课程包（SCORM 1.2/2004 或 Common Cartridge）与前端JS埋点位置说明；"
            "④LRS实例（Learning Locker开源版或商业LRS）与端点/凭据；⑤既有报表需求（完成率、尝试次数、时长）；"
            "⑥院校数据分类分级表与保留期政策。"
        ),
        usage_permissions=(
            "课程内容版权归院校/教师，埋点代码为衍生作品须保持原许可；verb与activity type优先使用ADL公开词表与IRI，"
            "自定义扩展键须用本机构可控域名；LRS凭据属机密，不得进入代码库或交付包；"
            "第三方课件若含vendor内容，须确认埋点与再分发许可；学生行为数据依FERPA/GDPR处理。"
        ),
        task_input=(
            "1门在线课程8个模块、约120个学习活动；课程包IMSCC约180 MB；活动-能力映射表XLSX（120行）；"
            "LRS测试实例1套（Docker部署）；埋点清单CSV；报表需求说明2页。"
        ),
        professional_operations=(
            "①能力模型与可观测行为分解（competency_mapping）：把能力项拆成可被事件观测的行为；"
            "②Statement配置文件设计（profile_design）：确定actor标识方式、verb、object activity、result与context字段；"
            "③verb与activity type IRI治理（iri_governance）：登记IRI命名空间、版本与弃用策略；"
            "④埋点实现与课程包构建（instrumentation）：在课件中调用xAPI封装库发送语句，处理离线队列与重试；"
            "⑤LRS接入与传输配置（lrs_config）：配置端点、OAuth凭据、批次与失败重发；"
            "⑥语句校验与拒绝规则测试（statement_validation）：构造空值、类型错误、键名大小写错误等用例验证LRS拒绝行为；"
            "⑦一致性测试与修复（conformance_test）：运行LRS一致性测试套件并修复不通过项；"
            "⑧数据导出与报表核对（report_reconciliation）：导出JSONL语句集，重算报表指标并与LRS查询结果比对。"
        ),
        expected_deliverable=(
            "xAPI profile文档（JSON+PDF）、埋点后的课程包（IMSCC+JS）、statement样本集（JSON Lines）、"
            "LRS一致性测试报告（含测试用例清单与结果）、数据字典（verb/扩展键/保留期）与报表核对表（XLSX）。"
        ),
        success_criteria=(
            "①全部statement含actor/verb/object且通过规范校验器；②≥20条非法语句测试用例中LRS按规范拒绝率100%；"
            "③自定义扩展键100%为合法IRI；④语言映射全部使用RFC 5646标签；⑤报表完成率与LRS计数差异≤0.5%；"
            "⑥同一statement id重复提交不产生重复记录（不可变性与幂等）。"
        ),
        verification_approach=(
            "第三方可运行ADL LRS一致性测试套件重跑；用独立校验脚本对导出的JSONL逐条验证必备字段、IRI格式、时间戳与语言标签；"
            "比对报表与LRS聚合查询；构造重复提交与大小写错误用例验证拒绝行为；核对profile文档与埋点代码的verb清单一致。"
        ),
        platform_dependencies=(
            "Linux + Java 17（一致性测试套件）或 Node.js；LRS（Learning Locker开源版需Docker/MongoDB，或商业LRS）；"
            "浏览器与课程包运行环境；网络需访问LRS端点；无GPU需求。"
        ),
        blocking_risks=(
            "第⑦步依赖ADL一致性测试套件可下载并运行（Java），若机构只用商业LRS则需另建测试实例；"
            "部分LMS只原生支持SCORM 1.2，xAPI需插件或自定义端点（第⑤步）；LRS云服务的凭据与网络策略可能阻断。"
            "残余风险：不同LRS实现对边缘语句行为存在差异。"
        ),
        expert_capability=(
            "3年以上学习分析或教育数据工程经验，熟悉xAPI规范、LRS运维、JSON Schema与前端埋点；"
            "具备FERPA/GDPR数据治理训练；教学设计师须能把能力模型转成可观测行为。"
        ),
        cross_domain_overlap=(
            "与psy_cluster的psy_exp_wf01（JATOS自建在线实验平台）与psy_comp_wf01（BIDS数据集整理）不同：psy行用实验范式与BIDS组织研究数据，"
            "本行是教学产品运行期的xAPI语句规范与LRS一致性验证；与biz_ana_wf01（CRISP-DM客户流失预测）不同：本行不做预测建模，"
            "只做学习事件语句与LRS一致性；与官方任务education_info/marc_remediation_folio_overlay、"
            "education_info/yi_manuscript_translation_1无交集。"
        ),
        granularity_check=(
            "覆盖从能力模型、profile治理、埋点到一致性测试与报表核对的完整数据生产链，含拒绝规则测试这一独立质量门；"
            "不是「安装一个LRS」的教程，也不是单条语句的格式检查。"
        ),
        pending_confirmation=(
            "①ADL一致性测试套件的当前版本、许可证与运行方式未核实（未下载）；②SCORM 2004与xAPI双轨并存的封装方式未验证；"
            "③具体商业LRS对§2.6签名语句与附件的支持未测试；④院校数据分级表中的保留期需由数据治理官确认。"
        ),
        data_usage_authorization=(
            "学习行为数据依院校数据治理政策与FERPA；GDPR下以第6(1)(f)合法利益或明示同意为基础并完成DPIA；"
            "LRS凭据按密钥管理规范保管；数据保留与删除流程须书面约定并留痕。"
        ),
        privacy_considerations=(
            "学习记录含个人标识（actor mbox/account）：最小化规则为只采集教学设计所需的最小verb集，优先使用假名化account，"
            "不采集自由文本、位置与设备指纹；保留期24个月；导出前去标识；学生可请求访问与删除。"
        ),
        research_ethics=(
            "agent起草profile、校验规则、测试用例与报告；数据治理官与课程负责人签署采集目的、保留期与使用边界；"
            "不得绕过同意或告知程序采集可识别行为数据。"
        ),
        reproducibility_assessment=(
            "规范与测试套件公开，环境可用容器固定，端到端可复现；商业LRS实现与课程运行环境差异导致部分不可复现；"
            "埋点代码随课程包版本锁定并记录commit。"
        ),
        evidence_kind="industry_standard_complete",
        source_category="professional_standard",
        primary_source_url="https://raw.githubusercontent.com/adlnet/xAPI-Spec/master/xAPI-Data.md",
        primary_claim=(
            "ADL xAPI规范（Part Two: Experience API Data）规定Statement必须以actor、verb、object为必备属性、Statement不可变更，"
            "并要求LRS拒绝空值、类型错误与键名大小写不符的语句，这是判定课程包埋点是否一致的依据。"
        ),
        software_adaptation="native",
        source_support_mode="conditional_support",
        evidence_scope=(
            "competency_mapping=as_recorded;profile_design=conditional_E1;iri_governance=conditional_E1;"
            "instrumentation=as_recorded;lrs_config=as_recorded;statement_validation=conditional_E1;"
            "conformance_test=conditional_E1;report_reconciliation=as_recorded"
        ),
        workflow_family_id="fc_courseware_packaging,fc_data_conformance",
        process_incident="none",
    ),
    row(
        **EDT_COMMON,
        candidate_id="edu_edt_wf03",
        workflow_title="Digital Course Accessibility Remediation to WCAG 2.2 AA and Section 508",
        occupation_scope=(
            "数字可访问性专员执行审计、缺陷分级与修复方案；多媒体开发员重制字幕、转录与音频描述；"
            "前端/课件工程师修复语义结构、键盘操作与焦点管理；课程负责人确认等价替代与教学效果；"
            "院校可访问性合规官签署符合性报告（ACR/VPAT）。"
        ),
        workflow_summary=(
            "对既有在线课程（HTML页面、PDF讲义、录播视频、交互组件）按WCAG 2.2 AA做自动化与人工审计，"
            "把缺陷逐条映射到成功准则并分级修复，再以辅助技术复测。最终产出逐条证据的可访问性符合性报告（ACR/VPAT）、"
            "修复后的课程包与字幕/转录文件，同时满足院校WCAG 2.2 AA政策与联邦Section 508（其E205.4引用WCAG 2.0 AA）要求。"
        ),
        source_type="industry_supported",
        evidence_level="E1",
        source_reference=(
            "W3C, Web Content Accessibility Guidelines (WCAG) 2.2, W3C Recommendation 12 December 2024"
            "（§5.2 Conformance Requirements 5.2.1–5.2.5；§5.3 Conformance Claims；SC 1.2.2 Captions (Prerecorded) A；"
            "SC 1.4.3 Contrast (Minimum) 4.5:1/3:1；SC 2.4.11 Focus Not Obscured (Minimum) AA；SC 3.3.8；SC 4.1.2），"
            "https://www.w3.org/TR/WCAG22/；次要：U.S. Access Board, Revised 508 Standards and 255 Guidelines, E101.1、E205.2、"
            "E205.4（电子内容符合WCAG 2.0 A/AA）、C203.1、C205.2，https://www.access-board.gov/ict/。"
        ),
        expert_raw_materials=(
            "①课程站点导出（HTML/CSS/JS）与文档原件（PDF/PPTX/DOCX）；②录播视频与音轨（合计约6小时）；"
            "③交互组件源码与第三方嵌入清单；④审计工具基线报告（axe-core、Pa11y、PDF结构检查）；"
            "⑤人工测试脚本与辅助技术清单（NVDA/JAWS/VoiceOver/Orca）；⑥院校可访问性政策、VPAT/ACR模板与既往整改记录。"
        ),
        usage_permissions=(
            "课程材料版权归院校/教师，修复衍生版本须保持原授权范围；视频转录与字幕涉及表演者权利（出镜者、配音）与音乐同步权，"
            "须取得许可或改用已清权素材；第三方出版商PDF不得改写，只能要求出版商提供可访问版本或替换为授权副本；"
            "嵌入字体须允许嵌入与再分发。"
        ),
        task_input=(
            "12个HTML页面、34个PDF讲义、9个视频（合计6小时）、5个JavaScript交互组件；审计基线报告；"
            "合规目标：WCAG 2.2 AA + Section 508（E205.4）；院校可访问性声明模板VPAT 2.5 INT。"
        ),
        professional_operations=(
            "①范围与合规基线确定（scope_baseline）：确定适用页面、文档、媒体与第三方内容，记录排除项与理由；"
            "②自动化扫描与人工审计（audit）：自动工具全量扫描，再按成功准则做键盘、缩放、屏幕阅读器人工走查；"
            "③成功准则映射与缺陷分级（sc_mapping）：每条缺陷映射到SC编号、影响级别与修复优先级；"
            "④文档与PDF修复（document_remediation）：重排阅读顺序、加标签、替代文本与标题结构，必要时提供等价HTML；"
            "⑤多媒体字幕/音频描述/转录（media_remediation）：制作同步字幕、音频描述脚本与全文转录；"
            "⑥语义结构与键盘/焦点修复（code_remediation）：修正标题层级、表单标签、ARIA、焦点顺序与对比度；"
            "⑦辅助技术复测（at_retest）：用屏幕阅读器与键盘复测关键学习任务并记录结果；"
            "⑧可访问性声明与证据归档（conformance_claim）：按§5.2/§5.3撰写ACR与符合性声明，附逐条证据。"
        ),
        expected_deliverable=(
            "修复后的课程站点与文档包、逐条成功准则的审计-修复对照表（XLSX/CSV）、可访问性符合性报告（ACR/VPAT 2.5 INT）、"
            "字幕文件（WebVTT/SRT）、音频描述脚本与转录稿、辅助技术复测记录。"
        ),
        success_criteria=(
            "①WCAG 2.2 全部适用A/AA成功准则通过（逐条有证据）；②正文对比度≥4.5:1、大文本≥3:1（SC 1.4.3）；"
            "③所有预录视频有同步字幕（SC 1.2.2）；④键盘可达且焦点不被遮挡（SC 2.4.11）；"
            "⑤PDF通过结构/标签检查或提供等价可访问HTML；⑥ACR每条准则列明测试方法、工具与证据链接。"
        ),
        verification_approach=(
            "第三方用axe-core/Pa11y重跑自动检查并人工按SC清单复核；用NVDA/JAWS/Orca走查关键任务；用对比度计测量取样点；"
            "抽查ACR证据可追溯性（每条链接可打开且对应该SC）；抽取10%页面做双人独立复核并计算一致率。"
        ),
        platform_dependencies=(
            "Linux审计工具链（axe-core、Pa11y、Lighthouse）；PDF修复可用LibreOffice与Ghostscript/pdfua检查，"
            "完整标签编辑通常需Acrobat Pro（Windows/macOS）；字幕与转录工具；屏幕阅读器Orca可在Linux，NVDA/JAWS需Windows虚拟机；无GPU。"
        ),
        blocking_risks=(
            "第⑦步NVDA/JAWS仅Windows，Linux上只能用Orca替代，覆盖不等价；第④步Acrobat Pro的PDF/UA修复器为Windows/macOS商业软件，"
            "Linux无完整等价替代；音频描述录制需录音棚与配音许可。残余风险：自动化工具通常只覆盖部分成功准则，其余依赖人工判断。"
        ),
        expert_capability=(
            "3年以上数字可访问性经验，熟悉WCAG 2.2、Section 508、PDF/UA、WAI-ARIA与辅助技术；"
            "建议持有IAAP CPACC/WAS或同等认证；多媒体可访问性（字幕、音频描述）实操经验。"
        ),
        cross_domain_overlap=(
            "平面设计域（graphic_design）的品牌文档与PDF/UA修复在课题上相邻，但本批未产出该簇候选、无法逐行比对；对象不同："
            "本行对象是课程站点与教学媒体（含字幕、音频描述与ACR），不做品牌视觉与版式设计；"
            "与edu_edt_wf01的QM评审行不同：本行以WCAG 2.2符合性与辅助技术复测为准，不以课程设计量规评分为准；"
            "已grep evidence/*/*_candidates.csv 全部11个候选文件，未发现其他无障碍修复候选；"
            "与官方任务education_info/marc_remediation_folio_overlay、education_info/yi_manuscript_translation_1无交集。"
        ),
        granularity_check=(
            "从范围界定、审计、分级、修复到符合性声明与辅助技术复测构成完整合规链，含两个独立质量门（人工审计、AT复测）；"
            "不是「跑一次axe」的工具操作，也不是单页修复。"
        ),
        pending_confirmation=(
            "①WCAG 2.2 的A/AA成功准则未逐条抄录（本行核对的是§5.2、§5.3与1.2.2/1.4.3/2.4.11/3.3.8/4.1.2）；"
            "②Section 508 E205.4引用的是WCAG 2.0 AA，与WCAG 2.2 AA的条文差异未逐条比对；③未实测具体PDF/UA检查器版本与判定口径。"
        ),
        data_usage_authorization=(
            "课程材料依院校授权；视频含表演者影像与声音须有肖像/表演许可，学生出镜须单独书面同意；"
            "审计日志与复测记录不含学号；无个人数据跨境传输；修复衍生件沿用原许可。"
        ),
        privacy_considerations=(
            "视频中的学生影像与声音属个人数据：最小化规则为优先使用无学生出镜的教学视频，确需出镜须单独同意并可撤回；"
            "字幕与转录文件不含姓名与学号；审计与复测记录仅保留页面URL与缺陷编号。"
        ),
        research_ethics=(
            "agent执行审计、生成修复建议与ACR草稿并标注未验证项；可访问性合规官与课程负责人签署最终符合性声明；"
            "不得在未复测的情况下声明合规，不得替第三方内容作合规承诺。"
        ),
        reproducibility_assessment=(
            "工具与成功准则公开，自动检查部分可复现；人工AT测试与修复判断存在评估者差异；商业PDF工具与视频重制资源影响完全复现；"
            "需固定工具版本与浏览器/AT版本。"
        ),
        evidence_kind="industry_standard_complete",
        source_category="professional_standard",
        primary_source_url="https://www.w3.org/TR/WCAG22/",
        primary_claim=(
            "W3C WCAG 2.2（2024-12-12推荐标准）以可测试的成功准则定义可访问性，§5.2规定符合性要求（符合级别、完整页面、"
            "完整流程、仅使用可访问支持的方式、非干扰），§5.3规定符合性声明；SC 1.4.3要求正文对比度4.5:1、大文本3:1。"
        ),
        software_adaptation="partial_function_replacement",
        source_support_mode="conditional_support",
        evidence_scope=(
            "scope_baseline=as_recorded;audit=conditional_E1;sc_mapping=conditional_E1;document_remediation=as_recorded;"
            "media_remediation=conditional_E1;code_remediation=conditional_E1;at_retest=as_recorded;"
            "conformance_claim=conditional_E1"
        ),
        workflow_family_id="fc_accessibility_remediation,fc_content_qa",
        process_incident="none",
    ),
]

LIB = [
    row(
        **LIB_COMMON,
        candidate_id="edu_lib_wf01",
        workflow_title="Original Cataloging to RDA and MARC 21 with PCC Authority Control",
        occupation_scope=(
            "编目馆员主导描述编目决策与MARC 21编码；规范控制馆员建立或更新名称与主题规范记录（NACO/SACO）；"
            "学科馆员负责主题分析与分类号赋予；编目主管或PCC联络人复核BIBCO级记录并签署；系统馆员负责ILS导入与索引重建。"
        ),
        workflow_summary=(
            "从新书接收与查重开始，按RDA核心元素转录描述数据、建立检索点并赋予主题与分类号，编码为MARC 21记录；"
            "对每个检索点完成规范控制，经机器校验与BIBCO级复核后导入本地集成图书馆系统并向共享书目库提交。"
            "交付含MARC 21记录、规范记录、编目工作表、校验报告与复核记录。"
        ),
        source_type="industry_supported",
        evidence_level="E3",
        source_reference=(
            "MARC 21 Format for Bibliographic Data（Network Development and MARC Standards Office, Library of Congress），"
            "1999 Edition，Update No. 1（2000年10月）至 Update No. 42（2026年5月），结构含 Leader、Directory、00X控制字段、"
            "1XX主要款目、20X-24X题名、3XX载体形态、4XX丛编、5XX附注、6XX主题检索、70X-75X附加款目、80X-83X丛编附加款目，"
            "附录A控制子字段、附录B完整级记录样例、附录C最低级记录，https://www.loc.gov/marc/bibliographic/（2026年访问）；"
            "次要：Program for Cooperative Cataloging, BIBCO, https://www.loc.gov/aba/pcc/bibco/（“BIBCO records include access "
            "points backed by complete authority work, both descriptive and subject.”）；RDA Toolkit与LC-PCC PS为订阅资源，条款未获取。"
        ),
        expert_raw_materials=(
            "①在版编目（CIP）数据与版权页扫描（300 dpi PDF）；②书名页、封面、目次、索引页图像；③出版者ONIX 3.0元数据XML；"
            "④本地编目政策与BIBCO级必备元素清单；⑤LC Authority File与LC Classification Web检索结果（订阅）；"
            "⑥Koha 24.x或FOLIO工作表单；⑦查重报告（WorldCat/本地目录）。"
        ),
        usage_permissions=(
            "书目事实数据不受版权保护，但封面图像、摘要与目次扫描须有出版者许可或合理使用评估；OCLC WorldCat记录受成员协议约束，"
            "不得再分发；RDA Toolkit与LC-PCC PS为订阅内容不得转载；规范记录依LC/OCLC使用条款；封面与插图版权归原出版者。"
        ),
        task_input=(
            "12种2024-2026年学术专著（含1种多卷本、1种译著、1种会议录）；每种提供PDF预览页与版权页、ONIX XML、查重报告；"
            "本地Koha测试实例；LC MARC Validation Tool；BIBCO级必备元素清单。"
        ),
        professional_operations=(
            "①接收与查重（record_selection）：比对本地库与WorldCat，判定套录或原始编目；"
            "②描述编目决策（description_decision）：确定RDA核心元素集与BIBCO级目标；"
            "③转录与著录（transcription）：题名与责任说明、版本、出版、载体形态、丛编；"
            "④检索点与规范控制（authority_control）：建立1XX/7XX并创建或更新规范记录；"
            "⑤主题分析与分类（subject_analysis）：赋予LCSH与DDC/LCC分类号；"
            "⑥MARC 21编码（marc_encoding）：Leader、006/008、040、043与各字段指示符子字段；"
            "⑦机器校验（machine_validation）：运行MARC Validation Tool并修正错误；"
            "⑧BIBCO复核与共享库提交（bibco_review）：PCC联络人复核并签署提交。"
        ),
        expected_deliverable=(
            "MARC 21记录（.mrc与MARCXML）、规范记录（MARCXML）、编目工作表（DOCX）、MARC校验报告、BIBCO复核清单、"
            "共享书目库提交确认单。"
        ),
        success_criteria=(
            "①Leader/008与资料类型、出版年、语言代码一致；②245$a转录准确、245$c责任说明完整；"
            "③每个1XX/7XX检索点均有已建立或新建的规范记录（100%）；④至少1个6XX LCSH与1个分类号；"
            "⑤MARC Validation Tool报0 error；⑥查重无重复记录；⑦BIBCO级必备元素100%齐全。"
        ),
        verification_approach=(
            "第三方用LC MARC Validation Tool重跑并比对报告；用pymarc脚本核对必备字段与定长字段合法性；"
            "抽取20%记录双人独立编目并计算字段一致率；规范记录与LC Authority File比对；ILS导入后做检索点测试。"
        ),
        platform_dependencies=(
            "Linux + Koha 24.x（Perl/MySQL）或FOLIO（Docker/PostgreSQL）；Java 17运行LC MARC Validation Tool；"
            "Python pymarc；OCLC Connexion客户端仅Windows（可选）；无GPU需求。"
        ),
        blocking_risks=(
            "OCLC Connexion客户端仅Windows，Linux只能经WorldCat API或本地库查重（第①步受限）；"
            "RDA Toolkit与LC-PCC PS为订阅（第②③步）；BIBCO提交需PCC成员资格与联络人（第⑧步）；LCSH/LC Classification Web订阅。"
            "残余风险：编目判断存在合理差异，字段一致率不可能达100%。"
        ),
        expert_capability=(
            "3年以上原始编目经验，图书馆学硕士（MLIS），RDA与MARC 21实操能力；完成NACO/SACO培训；"
            "熟悉BIBCO级要求与本地ILS工作流。"
        ),
        cross_domain_overlap=(
            "官方任务education_info/marc_remediation_folio_overlay是对既有MARC记录做批量修复与overlay，"
            "本行是从零原始编目并含规范控制与BIBCO复核，对象与成功标准不同；"
            "与library_info数字化行的对象（图像与结构元数据）不同；已grep全部evidence/*/*_candidates.csv，未发现其他编目候选。"
        ),
        granularity_check=(
            "覆盖查重→描述→规范→编码→机器校验→BIBCO复核→提交的完整生产链，含机器校验与人工复核两个独立质量门；"
            "不是「填一张MARC模板」的教程。"
        ),
        pending_confirmation=(
            "①RDA Toolkit与LC-PCC PS条款未获取（订阅），本行仅依据MARC 21与BIBCO公开页；"
            "②LC MARC Validation Tool当前版本与Schematron规则集未核实；③BIBCO BSR应用纲要PDF无法抓取（application/pdf）；"
            "④未实测Koha/FOLIO对MARCXML导入的字段映射。"
        ),
        data_usage_authorization=(
            "书目数据来自公开出版信息与出版者ONIX，依许可使用；WorldCat与LC规范库依OCLC/LC条款；不含读者个人数据；"
            "本地ILS数据依机构政策。"
        ),
        privacy_considerations=(
            "书目记录通常不含个人数据；若著录捐赠者、作者或手稿持有人，最小化规则为只记录公开出版信息与必要生卒年，"
            "不记录联系方式、身份证号或住址；查重日志不含读者标识。"
        ),
        research_ethics=(
            "agent起草描述数据、MARC记录与校验报告并标注未核实项；编目馆员署名对描述准确性负责；"
            "编目主管或PCC联络人签署BIBCO复核，agent不得代替其作权威判断。"
        ),
        reproducibility_assessment=(
            "MARC 21与BIBCO要求公开，编码与校验可复现；RDA Toolkit订阅限制完全复现；"
            "编目员判断差异与规范记录时点差异导致部分不可复现。"
        ),
        evidence_kind="agent_inferred_combination",
        source_category="professional_standard",
        primary_source_url="https://www.loc.gov/marc/bibliographic/",
        primary_claim=(
            "MARC 21书目格式（1999年版，更新至Update No. 42，2026年5月）以Leader、Directory、00X控制字段、1XX/20X-24X/3XX/4XX/"
            "5XX/6XX/70X-75X/80X-83X及附录A控制子字段、附录B完整级样例、附录C最低级记录，规定书目记录的字段、指示符与子字段结构。"
        ),
        software_adaptation="partial_function_replacement",
        source_support_mode="recorded_partial_support",
        evidence_scope=(
            "record_selection=as_recorded;description_decision=as_recorded;transcription=as_recorded;"
            "authority_control=as_recorded;subject_analysis=as_recorded;marc_encoding=as_recorded;"
            "machine_validation=as_recorded;bibco_review=as_recorded"
        ),
        workflow_family_id="fc_bibliographic_cataloging,fc_authority_control",
        process_incident="none",
    ),
    row(
        **LIB_COMMON,
        candidate_id="edu_lib_wf02",
        workflow_title="FADGI-Conformant Digitization with METS MODS Metadata and IIIF Delivery",
        occupation_scope=(
            "数字化项目主管制定成像规格与验收标准；影像技术员执行拍摄/扫描与色彩管理；元数据馆员创建METS/MODS与Dublin Core映射；"
            "系统馆员部署IIIF清单与查看器；馆藏主管与馆长共同签署版权状态与发布决定。"
        ),
        workflow_summary=(
            "从对象选择与权利状态评估开始，按FADGI技术指南第三版设定成像参数，并用合规评测靶标与软件验证图像质量，"
            "产出master与access派生；随后创建METS/MODS结构元数据与技术元数据、生成IIIF Presentation 3.0清单并发布；"
            "经抽样质检与元数据校验后移交数字保存。交付含FADGI合规master、METS/MODS XML、IIIF清单、OCR与QC报告。"
        ),
        source_type="industry_supported",
        evidence_level="E3",
        source_reference=(
            "Federal Agencies Digital Guidelines Initiative, Technical Guidelines for Digitizing Cultural Heritage Materials: "
            "Third Edition（Still Image Working Group，2022-2023），https://www.digitizationguidelines.gov/guidelines/digitize-technical.html"
            "（原文：“These guidelines are intended to be used in conjunction with digital image conformance evaluation targets and "
            "software. Together these guidelines and appropriate testing and monitoring systems provide the foundation for a "
            "FADGI-conforming digitization program.”）；次要：IIIF Presentation API 3.0.0, https://iiif.io/api/presentation/3.0/"
            "（Manifest须有label；rights取值须为CC或RightsStatements.org URI）；METS/MODS schema（Library of Congress，PDF未能抓取）。"
        ),
        expert_raw_materials=(
            "①待数字化对象清单与馆藏记录；②版权状态与权利人调查表；③扫描仪/相机与色彩靶标及校准记录；"
            "④FADGI合规评测软件与靶标图像；⑤METS/MODS模板与Dublin Core映射表；⑥Cantaloupe IIIF服务器配置；⑦OCR样张与词典。"
        ),
        usage_permissions=(
            "数字化对象本身可能仍受版权保护：须逐件确认公有领域、权利人许可或机构合理使用立场，并在IIIF rights/requiredStatement中声明；"
            "孤儿作品须做尽职调查并留痕；测试靶标与图卡为厂商版权但可内部使用；不得去除水印以掩盖来源。"
        ),
        task_input=(
            "1个特藏系列（1850-1920年照片与手稿）共420件、约1800个成像面；对象清单CSV；版权调查表；"
            "600 ppi/24-bit TIFF规格；METS/MODS模板；IIIF查看器配置。"
        ),
        professional_operations=(
            "①对象选择与权利评估（rights_clearance）：逐件判定版权状态与可发布范围；"
            "②成像规格与设备校准（imaging_spec）：分辨率、位深、色彩空间与靶标；"
            "③拍摄/扫描与色彩管理（capture）：按ICC流程采集并记录参数；"
            "④图像质量客观评测（fadgi_evaluation）：用评测软件按星级判定；"
            "⑤图像处理与派生（derivatives）：裁切、去噪、JPEG2000/JPEG访问副本；"
            "⑥元数据创建（mets_mods）：结构、描述与技术元数据及Dublin Core映射；"
            "⑦IIIF清单生成与发布（iiif_publish）：Manifest、Canvas、Annotation与权限声明；"
            "⑧质检与移交（qc_handoff）：抽样复检、校验与入藏移交。"
        ),
        expected_deliverable=(
            "FADGI合规TIFF master、JPEG2000/JPEG访问副本、METS/MODS XML、IIIF Presentation 3.0 Manifest JSON、"
            "OCR ALTO XML、QC报告（含FADGI星级）、权利声明与移交清单。"
        ),
        success_criteria=(
            "①全部master达到指定FADGI星级（本行设3星）并由评测软件出具报告；②600 ppi、24-bit、按规格无内容裁切；"
            "③METS/MODS通过XSD校验；④IIIF Manifest通过Presentation 3.0校验，label≥1且每件有rights或requiredStatement；"
            "⑤OCR字符准确率≥98%（抽样）；⑥抽样10%双人质检一致率≥95%。"
        ),
        verification_approach=(
            "第三方用FADGI评测软件对随机10%样本重测星级；用METS/MODS XSD与IIIF校验器重跑；"
            "用脚本核对文件数、命名与checksum清单；OCR以标准样张比对；权利声明抽查可追溯至调查表。"
        ),
        platform_dependencies=(
            "Linux + ImageMagick/OpenJPEG/Tesseract；FADGI评测软件（部分为Windows GUI，Linux需虚拟机或替代工具）；"
            "Cantaloupe（Java/Docker）IIIF服务器；校准显示器与实物靶标；存储≥2 TB；无GPU需求。"
        ),
        blocking_risks=(
            "第④步FADGI官方评测软件部分仅Windows GUI，Linux需虚拟机或替代工具，判定口径可能不同；"
            "第⑦步IIIF服务器部署需Java/Docker与网络；色彩管理依赖色度计等校准硬件；大规模存储与备份成本。"
            "残余风险：不同评测软件对同一图像的星级判定可能有边界差异。"
        ),
        expert_capability=(
            "3年以上文化遗产数字化经验，熟悉FADGI指南、成像评测与色彩管理；元数据馆员需METS/MODS与IIIF实操；"
            "项目须具备版权调查与权利清理能力。"
        ),
        cross_domain_overlap=(
            "与library_info编目行对象不同：本行产出图像与结构元数据，不产书目记录；"
            "与官方任务education_info/marc_remediation_folio_overlay无交集；已grep全部候选CSV，未发现其他数字化/IIIF候选；"
            "与数字保存行是上下游关系，但交付物与成功标准不同（图像质量 vs fixity与PREMIS完整性）。"
        ),
        granularity_check=(
            "覆盖权利评估→成像→客观评测→元数据→IIIF发布→质检移交的完整项目链，含图像质量与元数据两道独立质量门；"
            "不是「扫描一份文件」的教程。"
        ),
        pending_confirmation=(
            "①FADGI第三版PDF无法抓取（application/pdf），星级阈值依据公开页面表述；②METS/MODS schema未下载校验；"
            "③IIIF 3.0校验器与requiredStatement的必填性未逐条核对；④FADGI评测软件在Linux的可用替代未实测。"
        ),
        data_usage_authorization=(
            "数字化对象依版权状态与权利人许可；若含人物肖像或私人信件，依档案法与捐赠协议；"
            "用户访问日志不含个人标识；发布依机构开放数据政策。"
        ),
        privacy_considerations=(
            "手稿与照片可能含可识别个人（信件作者、照片人物）：最小化规则为元数据只记录已公开披露的姓名，"
            "不转录健康、宗教或家庭私密内容；限制访问期内的对象不进入公开IIIF；读者请求记录不保存。"
        ),
        research_ethics=(
            "agent执行成像评测、元数据草稿与QC报告；馆藏主管与馆长签署版权状态与发布决定；"
            "agent不得擅自发布权利状态不明的对象。"
        ),
        reproducibility_assessment=(
            "成像参数与元数据标准公开，可复现；设备、靶标与操作员差异影响星级；版权调查依赖人工判断；"
            "需固定FADGI评测软件版本与ICC配置文件。"
        ),
        evidence_kind="agent_inferred_combination",
        source_category="professional_standard",
        primary_source_url="https://www.digitizationguidelines.gov/guidelines/digitize-technical.html",
        primary_claim=(
            "FADGI数字文化遗产资料技术指南第三版（2022-2023）规定数字化技术参数，并明确须与数字图像合规评测靶标和软件配合使用、"
            "配合测试与监测系统，才构成FADGI合规的数字化项目，即图像质量由靶标与软件客观测量。"
        ),
        software_adaptation="conditional",
        source_support_mode="recorded_partial_support",
        evidence_scope=(
            "rights_clearance=as_recorded;imaging_spec=as_recorded;capture=as_recorded;fadgi_evaluation=as_recorded;"
            "derivatives=as_recorded;mets_mods=as_recorded;iiif_publish=as_recorded;qc_handoff=as_recorded"
        ),
        workflow_family_id="fc_digitization,fc_metadata_packaging",
        process_incident="none",
    ),
    row(
        **LIB_COMMON,
        candidate_id="edu_lib_wf03",
        workflow_title="Digital Preservation Ingest with PREMIS Provenance and Fixity Verification",
        occupation_scope=(
            "数字保存馆员设计SIP/AIP规格与摄取流程；系统馆员运维保存仓库与存储；元数据馆员建立PREMIS实体记录；"
            "数据管理员执行格式识别与病毒扫描；数字保存主管签署AIP验收与年度审计报告。"
        ),
        workflow_summary=(
            "依OAIS信息模型接收移交包，做病毒扫描、格式识别与完整性校验，转换为AIP并写入PREMIS 3.0的object/event/agent/rights记录，"
            "落实多副本异地存储与固定校验；定期导出PREMIS事件史做审计与格式迁移预警。"
            "交付含AIP、PREMIS XML、fixity清单、摄取报告与审计日志。"
        ),
        source_type="industry_supported",
        evidence_level="E3",
        source_reference=(
            "PREMIS（Library of Congress），https://www.loc.gov/standards/premis/（原文：“The PREMIS Data Dictionary for Preservation "
            "Metadata is the international standard for metadata to support the preservation of digital objects and ensure their "
            "long-term usability.”；当前PREMIS Version 3.0，XML Schema 3.0见 /standards/premis/premis.xsd，另有PREMIS with METS与"
            "Preservation Events受控词表）；次要：ISO 14721:2012 OAIS参考模型（条款未获取，仅名称层面）；BagIt RFC 8493（未抓取）。"
        ),
        expert_raw_materials=(
            "①移交协议与SIP规格（目录结构、命名、元数据最低集）；②移交包（BagIt或ZIP，含manifest与checksum）；"
            "③格式识别工具与PRONOM库（DROID/Siegfried）；④保存仓库（Archivematica或自建）配置；"
            "⑤PREMIS 3.0 XSD与受控词表；⑥存储与备份策略；⑦权利与访问声明。"
        ),
        usage_permissions=(
            "移交内容依捐赠/转让协议确定保存与提供访问的权利范围；工具为开源许可（Archivematica AGPL、Siegfried BSD）；"
            "PREMIS文档可自由使用但须注明出处；含第三方商业软件或加密内容须单独许可；不得绕过访问限制提供副本。"
        ),
        task_input=(
            "1批院系研究数据与出版物共1.2 TB（约48000个文件，含PDF、TIFF、CSV、DOCX、视频），BagIt 1.0包；"
            "SIP规格文档；PREMIS 3.0 XSD；Archivematica 1.15（Docker）。"
        ),
        professional_operations=(
            "①移交协议与SIP验收（sip_acceptance）：核对清单、命名与元数据最低集；"
            "②病毒扫描与安全隔离（virus_scan）：隔离命中文件并记录处置；"
            "③格式识别与验证（format_id）：PRONOM PUID识别与文件结构校验；"
            "④规范化与AIP构建（normalization）：按保存策略转换并记录迁移事件；"
            "⑤PREMIS实体与事件记录（premis_record）：object/event/agent/rights；"
            "⑥完整性校验与副本（fixity）：SHA-256清单与多副本异地存储；"
            "⑦访问副本与DIP生成（access_copy）：按权利声明分级生成；"
            "⑧审计、报告与迁移预警（audit_report）：事件史导出与格式风险报告。"
        ),
        expected_deliverable=(
            "AIP包（BagIt/METS封装）、PREMIS 3.0 XML、格式识别报告（CSV）、fixity清单（SHA-256）、摄取报告、"
            "DIP访问副本、年度审计与格式风险报告。"
        ),
        success_criteria=(
            "①100%文件有PRONOM PUID或明确的unknown记录；②摄取前后checksum 100%一致；"
            "③PREMIS记录覆盖每个object的event（ingest、fixity check、normalization）与agent；④PREMIS XML通过3.0 XSD校验；"
            "⑤3份副本分布于2个以上物理位置；⑥随机抽取5个AIP恢复测试100%可读；⑦摄取报告签署。"
        ),
        verification_approach=(
            "第三方重算SHA-256并比对fixity清单；用PREMIS 3.0 XSD校验XML；用Siegfried/DROID重跑格式识别并比对；"
            "做恢复演练（随机AIP还原并打开）；审计日志与PREMIS事件时间线交叉核对。"
        ),
        platform_dependencies=(
            "Linux + Docker（Archivematica 1.15约需16 GB RAM）；Siegfried（Go）或DROID（Java）；BagIt工具；"
            "PostgreSQL/MySQL；存储与异地备份；无GPU需求。"
        ),
        blocking_risks=(
            "Archivematica部署需Docker与大内存，机构若禁用容器需自建流程（第④⑤步）；格式识别库需定期更新（第③步）；"
            "异地副本依赖网络与存储预算；PREMIS XSD与受控词表版本须锁定。"
            "残余风险：规范化可能改变文件行为，需按格式逐一评估。"
        ),
        expert_capability=(
            "3年以上数字保存经验，熟悉OAIS与PREMIS、格式识别与迁移策略；系统馆员需Linux与容器运维能力；"
            "需具备存储、备份与审计管理经验。"
        ),
        cross_domain_overlap=(
            "与library_info数字化行是上下游（本行接收其产物），但本行对象是AIP与保存元数据，成功标准是fixity与PREMIS完整性，"
            "而非图像质量；与官方任务education_info/marc_remediation_folio_overlay无交集；已grep全部候选CSV，无其他数字保存候选。"
        ),
        granularity_check=(
            "覆盖SIP验收→识别→AIP→PREMIS→fixity→审计的完整摄取链，含fixity校验与恢复演练两个独立质量门；"
            "不是「把文件拷到NAS」的操作。"
        ),
        pending_confirmation=(
            "①ISO 14721 OAIS条款未获取（付费），仅按名称与公开描述使用；②Archivematica 1.15的PREMIS输出映射未实测；"
            "③PREMIS 3.0 XSD未下载校验；④BagIt RFC 8493未抓取。"
        ),
        data_usage_authorization=(
            "依捐赠/转让协议与机构保存政策；含个人数据的研究数据须去标识或限定访问；"
            "GDPR下以第6(1)(e)公共任务或协议为基础；访问副本按权利声明分级开放。"
        ),
        privacy_considerations=(
            "研究数据可能含受试者个人数据：最小化规则为摄取时按移交协议过滤直接标识符，敏感数据仅进入受限访问副本；"
            "PREMIS agent只记角色与机构，不记个人联系方式；审计日志按分级访问控制并设保留期。"
        ),
        research_ethics=(
            "agent执行摄取、PREMIS记录草稿与审计报告；数字保存主管签署AIP验收；"
            "数据所有者与伦理委员会确认敏感数据的保存与访问条件。"
        ),
        reproducibility_assessment=(
            "工具与标准公开，流程可用容器复现；格式识别库与规范化工具版本影响结果；"
            "存储介质与组织策略影响长期可复现性；PREMIS事件记录本身提供审计追踪。"
        ),
        evidence_kind="industry_standard_complete",
        source_category="professional_standard",
        primary_source_url="https://www.loc.gov/standards/premis/",
        primary_claim=(
            "PREMIS数据字典是保存元数据的国际标准，用于支持数字对象的长期保存与可用性，当前3.0版由数据字典、XML Schema与配套文档组成，"
            "并在世界范围的数字保存项目及商业与开源工具中实现。"
        ),
        software_adaptation="native",
        source_support_mode="conditional_support",
        evidence_scope=(
            "sip_acceptance=as_recorded;virus_scan=as_recorded;format_id=as_recorded;normalization=as_recorded;"
            "premis_record=conditional_E1;fixity=conditional_E1;access_copy=as_recorded;audit_report=as_recorded"
        ),
        workflow_family_id="fc_digital_preservation,fc_ingest_pipeline",
        process_incident="none",
    ),
]

TRN = [
    row(
        **TRN_COMMON,
        candidate_id="edu_trn_wf01",
        workflow_title="Technical Translation Production with ISO 17100 Processes and TBX Terminology",
        occupation_scope=(
            "笔译员执行翻译；审校/修订员做双语修订；语言负责人做单语审校与放行；术语专家维护术语库并导出TBX；"
            "本地化项目经理确认规格、排期与交付；客户方语言服务采购方验收。"
        ),
        workflow_summary=(
            "从项目规格与参考文件接收开始，做术语提取与翻译记忆分析，按翻译—修订—审校三段式生产，"
            "术语经审批后写入术语库并以TBX交换；最终做格式与完整性验证并签署交付。"
            "交付含译文、TBX术语库、TMX记忆库、LQA报告与交付确认单。"
        ),
        source_type="industry_supported",
        evidence_level="E3",
        source_reference=(
            "Standards Institution of Israel（SII，以色列国家标准机构）ISO 17100:2015专页“ISO 17100: 2015: Translation services - "
            "Requirements for translation services”之“The standard sets”节：“The requirements for the core process (translation) from "
            "the proposal stage through receipt of the order, to submission of the translated material to the customer includes "
            "validation of the translated material”；“Validation of the translation by a second party (not the translator)”；"
            "“Requirement to archive and save the materials used for the translation, obtaining feedback on the quality of the "
            "translation, and confidentiality”；同页载明该标准取代已撤销的BS EN 15038，且“The standard does not apply to translation by "
            "automated software or tools.”，https://www.sii.org.il/en/iso-17100/；标准本体ISO 17100:2015（ISO/TC 37/SC 5，2015-05发布，"
            "Amd 1:2017，ICS 01.020）条款正文付费未获取；次要：TBX（ISO 30042）https://www.tbxinfo.net/（“TBX ... is the international "
            "standard for archiving and exchanging terminological information exported from terminology databases (termbases).”）；"
            "MQM框架 https://www.themqm.org/ 用于抽样质量评估。"
        ),
        expert_raw_materials=(
            "①源文件（DOCX/XLIFF，约42000词）与技术术语表草案；②风格指南与客户术语偏好（CSV）；③翻译记忆库（TMX）与既往项目参考；"
            "④术语库（TBX-Core）；⑤查询表与主题专家联系方式；⑥CAT工具项目包；⑦交付规格（格式、编码、命名）。"
        ),
        usage_permissions=(
            "源文件版权归客户，译文为委托作品，权利归属依合同；术语库与翻译记忆含客户专有信息，不得用于其他客户项目；"
            "TBX/TMX中的第三方术语须标注来源与许可；嵌入字体与对象须允许再分发。"
        ),
        task_input=(
            "1份工业设备技术手册（42000词，DOCX+XLIFF 2.1）、术语表草案（380条）、TMX记忆库（约12万句对）、风格指南PDF、"
            "TBX-Core术语库；交付DOCX+PDF。"
        ),
        professional_operations=(
            "①项目规格与可行性确认（project_spec）：语对、领域、交付格式、截止期与资源；"
            "②预翻译准备（pretranslation）：术语提取、TM分析、参考文件与查询表；"
            "③翻译（translation）：按术语库与风格指南逐句段翻译；"
            "④双语修订（revision）：第二语言专家对照原文修订；"
            "⑤单语审校/校对（review）：目标语可读性、一致性与排版；"
            "⑥术语审批与TBX更新（terminology）：新术语经审批入库并导出；"
            "⑦最终验证与交付（final_verification）：格式、完整性、签字；"
            "⑧项目收尾与LQA抽样（close_out）：抽样评估与经验教训。"
        ),
        expected_deliverable=(
            "目标语译文（DOCX+PDF）、TBX-Core术语库、TMX翻译记忆、双语对照表（XLSX）、LQA报告（MQM口径）、"
            "交付确认单、译者与审校声明。"
        ),
        success_criteria=(
            "①100%句段已翻译且无空段；②术语与已批准TBX一致率100%；③MQM抽样（≥10%字数或≥2000词）无critical错误、"
            "major错误率≤1/1000词；④TBX通过TBX-Core schema校验；⑤翻译与修订由两名不同语言专家完成且角色可审计；"
            "⑥交付格式与命名100%符合规格。"
        ),
        verification_approach=(
            "第三方按MQM重新标注抽样并计算分数与标注者一致性；用TBX validator校验术语库；TMX导入导出往返测试；"
            "用脚本核对句段完整性、数字与单位一致性；审阅译者/审校身份与时间戳。"
        ),
        platform_dependencies=(
            "Linux + OmegaT 5.x（Java）或translate5；TBX/TMX编辑器；LibreOffice；术语提取工具；无GPU需求。"
        ),
        blocking_risks=(
            "商业CAT（Trados Studio、memoQ）主要面向Windows，Linux以OmegaT替代，TBX/TMX兼容性需实测（第②③步）；"
            "ISO 17100认证审核需外部认证机构（第⑦步仅在声明层面）；客户指定工具链时无法替换。"
            "残余风险：语言质量评估存在标注者主观差异。"
        ),
        expert_capability=(
            "5年以上技术笔译经验，目标语母语级，具备工业设备领域主题知识；审校须为第二语言专家；"
            "术语专家熟悉TBX与术语学方法；项目经理熟悉ISO 17100流程。"
        ),
        cross_domain_overlap=(
            "与edu_trn_wf02（软件UI的XLIFF工程与MQM）不同：本行对象是文档笔译与术语管理，不含UI构建与伪本地化；"
            "与官方任务education_info/yi_manuscript_translation_1不同：那是彝文古籍字形翻译；与edu_trn_wf03字幕不同；"
            "已grep全部候选CSV，无其他笔译候选。"
        ),
        granularity_check=(
            "覆盖规格→准备→翻译→修订→审校→术语→验证→收尾的完整TEP链，含修订与审校两个角色分离的质量门；"
            "不是「用CAT翻译一段文字」的教程。"
        ),
        pending_confirmation=(
            "①ISO 17100条款正文付费未获取，且iso.org官网页面在本环境返回HTTP 403（Cloudflare），故改以SII国家标准机构专页为主要证据，"
            "仅支持“标准覆盖面”层级，不能逐条对应条款编号；翻译—修订—审校三段式按行业TEP实践组织；"
            "②ISO 17100处于修订状态（2025-08起，90.92），新版要求未定；③TBX-Core schema未下载校验；"
            "④未实测OmegaT对TBX-Core的支持程度。"
        ),
        data_usage_authorization=(
            "源文件与译文依客户合同；术语库与TM属客户专有，须约定不得复用；若含个人数据（如手册中的联系人），"
            "依GDPR第6(1)(b)合同必要性；第三方术语依其许可。"
        ),
        privacy_considerations=(
            "技术手册通常不含个人数据，但若含客户员工姓名、联系方式或现场照片：最小化规则为译文仅保留必要业务联系人角色，"
            "不扩大个人信息；照片中可识别人物须模糊或取得同意；TM与术语库不得沉淀个人信息。"
        ),
        research_ethics=(
            "agent起草译文、术语条目、LQA报告与交付单；译者与审校签署语言质量结论，项目经理签署交付；"
            "agent不得替代具名译者承担翻译责任。"
        ),
        reproducibility_assessment=(
            "流程与TBX/TMX格式公开，可复现；语言判断与术语决策存在专业差异；商业CAT与客户TM不可获取时复现受限；"
            "需固定术语库与风格指南版本。"
        ),
        evidence_kind="agent_inferred_combination",
        source_category="professional_body_factsheet",
        primary_source_url="https://www.sii.org.il/en/iso-17100/",
        primary_claim=(
            "以色列标准学会（SII）的ISO 17100:2015专页载明：该标准规定从提案、接单到向客户交付译文的翻译核心过程（含译文验证）、"
            "服务提供方译员与审校等角色的最低资质与资源、由第二方（非译者）实施的译文验证，以及材料归档、质量反馈与保密要求；"
            "该标准取代已撤销的BS EN 15038，且不适用于纯自动化软件或工具翻译。"
        ),
        software_adaptation="partial_function_replacement",
        source_support_mode="recorded_partial_support",
        evidence_scope=(
            "project_spec=as_recorded;pretranslation=as_recorded;translation=as_recorded;revision=as_recorded;"
            "review=as_recorded;terminology=as_recorded;final_verification=as_recorded;close_out=as_recorded"
        ),
        workflow_family_id="fc_translation_production,fc_terminology_management",
        process_incident="none",
    ),
    row(
        **TRN_COMMON,
        candidate_id="edu_trn_wf02",
        workflow_title="Software UI Localization with XLIFF 2.1 Exchange and MQM Quality Evaluation",
        occupation_scope=(
            "本地化工程师做源文件抽取、XLIFF生成与回填构建；译员在上下文中翻译；语言质量评估员按MQM标注；"
            "本地化项目经理协调版本与交付；产品负责人验收UI。"
        ),
        workflow_summary=(
            "从源代码与资源文件抽取可本地化字符串，做国际化审查后生成XLIFF 2.1文件（unit/segment、术语与长度约束模块），"
            "译员翻译并做上下文审校，回填构建后跑伪本地化与UI截图比对，最后按MQM三步法（规格—标注—评分）评估语言质量并回归修复。"
            "交付含XLIFF、目标语资源包、MQM报告与构建产物。"
        ),
        source_type="industry_supported",
        evidence_level="E3",
        source_reference=(
            "OASIS, XLIFF Version 2.1, OASIS Standard 13 February 2018（§2 Conformance；§4.2.2 xliff/file/group/unit/segment/source/target；"
            "§5 模块含Glossary、Metadata、Resource Data、Size and Length Restriction、Validation、ITS），"
            "https://docs.oasis-open.org/xliff/xliff-core/v2.1/os/xliff-core-v2.1-os.html；次要：MQM Council框架 https://www.themqm.org/"
            "（三步：定义规格、按错误类型与严重度标注、计算质量分并决定接受/修订/拒绝；对齐ISO 5060）。"
        ),
        expert_raw_materials=(
            "①源代码仓库与资源文件（约18000字符串）；②UI截图与上下文说明；③术语表（TBX）与风格指南；"
            "④XLIFF 2.1 schema与校验器；⑤伪本地化配置；⑥MQM评估规格（字数、严重度、阈值）；⑦缺陷跟踪系统。"
        ),
        usage_permissions=(
            "源代码与资源依客户许可；译文与术语属委托成果；开源组件须遵守其许可（如GPL）不得污染；"
            "字体与图标须允许再分发；截图中的第三方内容须清权。"
        ),
        task_input=(
            "1个桌面与Web双端产品的资源文件（约18000字符串、42个文件）、UI截图120张、TBX术语表（650条）、"
            "XLIFF 2.1 schema、MQM规格。"
        ),
        professional_operations=(
            "①源文件抽取与国际化审查（i18n_review）：硬编码、字符串拼接、占位符与复数规则；"
            "②XLIFF 2.1生成（xliff_authoring）：unit/segment、元数据与长度约束；"
            "③术语与上下文准备（context_prep）：Glossary模块与ITS上下文；"
            "④翻译与上下文审校（translate_review）：在界面语境中翻译并复核；"
            "⑤回填构建与伪本地化（build_pseudo）：构建目标语版本并跑伪本地化；"
            "⑥MQM语言质量评估（mqm_eval）：规格→标注→评分；"
            "⑦缺陷修复与回归（fix_regression）：修复后回归验证；"
            "⑧交付与版本归档（delivery_archive）：资源包、报告与基线归档。"
        ),
        expected_deliverable=(
            "XLIFF 2.1文件集、目标语资源包、术语表（TBX）、MQM评分报告（含错误分布与根因）、缺陷清单与回归记录、"
            "本地化构建产物、交付说明。"
        ),
        success_criteria=(
            "①全部XLIFF通过2.1 schema校验；②100% unit有target且无空译；③占位符与内联标签完整率100%；"
            "④MQM得分达到规格阈值（如≥98/100且critical=0）；⑤伪本地化无截断与乱码，UI截图差异仅限文本区域；"
            "⑥术语一致率100%。"
        ),
        verification_approach=(
            "第三方用OASIS XLIFF 2.1 schema重校验；用脚本比对源/目标占位符与标签；第二位评估员独立MQM标注并计算一致性；"
            "构建后跑UI截图diff；术语一致性脚本比对TBX。"
        ),
        platform_dependencies=(
            "Linux + Java 17（Okapi Framework/Rainbow、translate5）；XLIFF校验器；Node/Python构建脚本；浏览器与截图工具；无GPU需求。"
        ),
        blocking_risks=(
            "部分TMS为云端SaaS需注册与网络（第②④步）；XLIFF 2.1的Size and Length Restriction与ITS模块工具支持不全（第②③步）；"
            "UI截图比对需可运行的产品构建（第⑤步）；商业CAT主要面向Windows。"
            "残余风险：MQM评分受评估者判断影响，需报告一致性系数。"
        ),
        expert_capability=(
            "3年以上本地化工程经验，熟悉XLIFF 2.x、Okapi、构建回填与伪本地化；译员须具备软件UI语境经验；"
            "MQM评估员须完成标注培训并做一致性校准。"
        ),
        cross_domain_overlap=(
            "与edu_trn_wf01文档笔译不同（本行是软件资源文件工程与UI构建）；与edu_trn_wf03字幕不同；"
            "本行是可交付的本地化批次与语言质量结论，不是i18n基础设施搭建；已grep全部候选CSV，无XLIFF/本地化候选。"
        ),
        granularity_check=(
            "覆盖抽取→XLIFF→翻译→构建→MQM→回归→交付的完整本地化批次，含构建验证与MQM评分两道独立质量门；"
            "不是「翻译一个strings文件」的操作。"
        ),
        pending_confirmation=(
            "①XLIFF 2.2的OASIS标准页返回404，故锁定2.1；②Size and Length Restriction模块的具体profile取值未逐条核对；"
            "③MQM与ISO 5060的对应条款未获取（ISO 5060付费）；④未实测Okapi对XLIFF 2.1全部模块的往返保真。"
        ),
        data_usage_authorization=(
            "源代码与字符串依客户合同；字符串中的用户数据样例须脱敏；译文与术语依委托协议；开源组件许可须合规审查。"
        ),
        privacy_considerations=(
            "UI字符串可能含示例个人信息（示例邮箱、姓名）：最小化规则为使用虚构示例数据，真实用户数据不得进入XLIFF或截图；"
            "截图须遮蔽账号与头像；MQM标注不记录译者个人敏感信息。"
        ),
        research_ethics=(
            "agent生成XLIFF、MQM报告草稿与缺陷清单；语言负责人签署质量结论，产品负责人验收UI；"
            "agent不得代替评估员签署质量判定。"
        ),
        reproducibility_assessment=(
            "XLIFF schema与MQM框架公开，流程可复现；构建环境与UI截图依赖产品版本；MQM标注存在评估者差异，需报告一致性系数；"
            "云端TMS不可获取时受限。"
        ),
        evidence_kind="industry_standard_complete",
        source_category="professional_standard",
        primary_source_url="https://docs.oasis-open.org/xliff/xliff-core/v2.1/os/xliff-core-v2.1-os.html",
        primary_claim=(
            "OASIS XLIFF 2.1（2018-02-13 OASIS Standard）定义用于存储可本地化数据并在本地化流程各步骤间传递的双语格式，"
            "其核心结构为xliff/file/group/unit/segment（source/target），并提供术语、元数据、资源数据、长度约束与验证等模块，"
            "是本地化交换与回填的格式依据。"
        ),
        software_adaptation="native",
        source_support_mode="conditional_support",
        evidence_scope=(
            "i18n_review=as_recorded;xliff_authoring=conditional_E1;context_prep=conditional_E1;translate_review=as_recorded;"
            "build_pseudo=as_recorded;mqm_eval=as_recorded;fix_regression=as_recorded;delivery_archive=as_recorded"
        ),
        workflow_family_id="fc_localization_engineering,fc_linguistic_qa",
        process_incident="none",
    ),
    row(
        **TRN_COMMON,
        candidate_id="edu_trn_wf03",
        workflow_title="Timed-Text Subtitling to the Netflix Timed Text Style Guide",
        occupation_scope=(
            "字幕译者做spotting与翻译；字幕质检员做同步、时长、分行与字符集检查；本地化项目经理对接交付规格与KNP/正式度表；"
            "客户方内容运营验收；听障版本另需SDH规范。"
        ),
        workflow_summary=(
            "接收视频、音频与KNP/正式度表，按Netflix TTSG做spotting与翻译（单条5/6秒至7秒、最多2行、仅用Netflix Glyph List字符），"
            "生成符合TTSG的TTML（百分比定位、tts:fontSize 100%），经同步与分行质检后交付并附译者署名事件。"
            "交付含TTML、SRT备份、KNP/正式度表与QC报告。"
        ),
        source_type="industry_supported",
        evidence_level="E3",
        source_reference=(
            "Netflix, Timed Text Style Guide: General Requirements（Partner Help Center），“Any timed text created specifically for "
            "Netflix – Originals or non-Originals – should follow the Netflix Timed Text Style Guide, unless otherwise advised.”；"
            "§1 最短5/6秒、最长7秒；§3 仅可用NETFLIX Glyph List字符；§4 最多2行及断行规则；§6 须建立并使用KNP/正式度表；"
            "§12 译者署名末条且≤5秒；§13 TTML仅用百分比值、tts:fontSize为100%，"
            "https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617-Timed-Text-Style-Guide-General-Requirements；"
            "次要：BBC Subtitle Guidelines（页面正文被截断，未用于条款级引用）。"
        ),
        expert_raw_materials=(
            "①视频与音轨（1集45分钟，24fps）；②英文脚本/对白表；③KNP与正式度表；④术语表与角色名表；"
            "⑤Netflix Glyph List；⑥TTML模板与样式要求；⑦同系列既有字幕参考。"
        ),
        usage_permissions=(
            "影视内容版权归制片方，字幕为委托衍生作品，不得外传；引用既有译文仅限公有领域（“100年”经验法则）或已获权利人有偿许可；"
            "字体与Glyph List依Netflix合作条款；歌词翻译须另获同步许可。"
        ),
        task_input=(
            "1集45分钟剧集（24fps，英语→简体中文）、英文对白表、KNP/正式度表、Glyph List、TTML模板；交付TTML+SRT。"
        ),
        professional_operations=(
            "①素材与技术规格核对（intake_spec）：帧率、时长、Glyph List与KNP；"
            "②spotting与计时（spotting）：5/6秒下限、7秒上限、镜头切换处断分；"
            "③翻译与本地化改写（translation）：含KNP正式度处理；"
            "④分行与字符校验（line_break）：≤2行、按标点/连词断行、Glyph List白名单；"
            "⑤TTML生成与样式（ttml_build）：百分比定位、fontSize 100%；"
            "⑥质检（qc）：同步、阅读速度、重叠、署名；"
            "⑦交付与metadata（delivery）：文件命名、版本与交付说明。"
        ),
        expected_deliverable=(
            "TTML字幕文件、SRT备份、KNP与正式度表、术语/角色名表、QC报告（含时长与分行统计）、译者署名事件。"
        ),
        success_criteria=(
            "①100%事件时长在5/6秒至7秒之间；②每条≤2行且断行符合§4规则；③全部字符在Netflix Glyph List内；"
            "④TTML仅用百分比定位且tts:fontSize=100%；⑤末条为译者署名且≤5秒；⑥抽样同步误差≤1帧、无重叠事件。"
        ),
        verification_approach=(
            "第三方用脚本解析TTML统计时长、行数、字符集与定位单位；用视频比对抽查同步；用Glyph List做字符白名单校验；"
            "人工按§4断行规则复核抽样20条。"
        ),
        platform_dependencies=(
            "Linux + Aegisub 3.2（spotting与字幕编辑）+ FFmpeg；Python pysubs2或TTML解析脚本；字体；无GPU需求。"
        ),
        blocking_risks=(
            "Netflix合作方门户与TTML校验器需Partner账号（第⑤⑥步）；部分字幕工具仅Windows；Glyph List与KNP模板需合作方提供；"
            "若交付SDH还需听障规范补充。残余风险：帧率转换可能导致计时偏移。"
        ),
        expert_capability=(
            "3年以上影视字幕翻译经验，目标语母语级，熟悉TTSG与KNP正式度体系；质检员需帧级同步判断能力；"
            "项目经理熟悉Netflix交付规范。"
        ),
        cross_domain_overlap=(
            "与edu_trn_wf01/wf02不同（文档笔译、软件UI本地化 vs 视听timed text）；"
            "与官方任务education_info/yi_manuscript_translation_1（彝文古籍字形）不同；已grep全部候选CSV，无字幕/AVT候选。"
        ),
        granularity_check=(
            "覆盖规格核对→spotting→翻译→分行→TTML→QC→交付的完整字幕生产链，含分行/Glyph与同步两道质量门；"
            "不是「用播放器加字幕」的教程。"
        ),
        pending_confirmation=(
            "①TTSG为合作方文档，条款可能随版本更新（另有2025年12月更新页未抓取）；②每行字符上限与阅读速度（CPS）的具体数值"
            "未在已抓取页面确认，故成功标准未写死；③SDH/听障版本规范未获取；④TTML校验器未实测。"
        ),
        data_usage_authorization=(
            "影视内容依制片方与Netflix合作条款；字幕不得外传或用于训练；若含真实人物影像，依肖像与公开传播许可；译者署名依合同。"
        ),
        privacy_considerations=(
            "字幕内容可能含剧中人物姓名与虚构个人信息；真实人物纪录片须避免扩散非公开个人信息；"
            "最小化规则为只翻译对白与剧情必需的屏幕文字，不添加未经核实的人物身份信息；QC记录不含译者个人联系方式。"
        ),
        research_ethics=(
            "agent生成字幕草稿、QC统计与交付包；字幕译者与质检员签署质量结论；"
            "agent不得在未获版权许可时复用既有译文。"
        ),
        reproducibility_assessment=(
            "TTSG部分公开但为合作方文档，版本变化影响复现；帧率与片源差异影响计时；脚本化校验可复现，人工断行判断存在差异。"
        ),
        evidence_kind="industry_standard_complete",
        source_category="professional_standard",
        primary_source_url="https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617-Timed-Text-Style-Guide-General-Requirements",
        primary_claim=(
            "Netflix TTSG总则要求为Netflix制作的timed text遵循该指南，并规定单条字幕时长下限5/6秒、上限7秒、最多2行、"
            "仅可使用Netflix Glyph List字符、须建立KNP/正式度表、TTML仅用百分比定位且tts:fontSize为100%。"
        ),
        software_adaptation="partial_function_replacement",
        source_support_mode="conditional_support",
        evidence_scope=(
            "intake_spec=as_recorded;spotting=conditional_E1;translation=as_recorded;line_break=conditional_E1;"
            "ttml_build=conditional_E1;qc=conditional_E1;delivery=as_recorded"
        ),
        workflow_family_id="fc_audiovisual_translation,fc_timed_text_delivery",
        process_incident="none",
    ),
]

ROWS = EDT + LIB + TRN


def main():
    out_dir = os.path.join("evidence", "s1_02b3_research")
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "edu_cluster_candidates.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in ROWS:
            assert set(r) == set(COLS), set(r) ^ set(COLS)
            w.writerow(r)
    counts = {}
    for r in ROWS:
        counts[r["subdomain_code"]] = counts.get(r["subdomain_code"], 0) + 1
    sidecar = {
        "subdomains": [
            {
                "subdomain_code": "educational_technology",
                "candidate_count": counts.get("educational_technology", 0),
                "coverage_notes": (
                    "3 rows: instructional design package with QM review; xAPI instrumentation and LRS conformance; "
                    "WCAG 2.2 AA / Section 508 remediation. Seeds 1-3 used. Learning analytics dashboard (seed 4) and "
                    "virtual lab (seed 5) not used because the three chosen rows each have their own artifact, review gate "
                    "and objectively checkable standard; adding them would duplicate the data-governance and media-production "
                    "content already covered."
                ),
            },
            {
                "subdomain_code": "library_info",
                "candidate_count": counts.get("library_info", 0),
                "coverage_notes": (
                    "3 rows: original cataloging to RDA/MARC 21 with PCC authority control; FADGI digitisation with "
                    "METS/MODS and IIIF delivery; PREMIS-conformant preservation ingest. Seeds 1, 2 and 5 used. "
                    "PRISMA systematic review (seed 4) deliberately excluded to avoid overlap with psy_exp_wf04; "
                    "weeding/deselection (seed 3) excluded because its evidence base is a practitioner manual rather than "
                    "a citable standard, and it would not add a distinct artifact class."
                ),
            },
            {
                "subdomain_code": "translation",
                "candidate_count": counts.get("translation", 0),
                "coverage_notes": (
                    "3 rows: ISO 17100 TEP with TBX terminology; XLIFF 2.1 localisation with MQM QA; Netflix TTSG timed-text "
                    "subtitling. Seeds 1-3 used. MT post-editing (seed 4) and certified/legal translation (seed 5) not used: "
                    "ISO 18587 and sworn-translator rules are paywalled/no free clause access, so they could only be "
                    "name-referenced, and they overlap the TEP row's revision gate."
                ),
            },
        ]
    }
    json_path = os.path.join(out_dir, "edu_cluster.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(sidecar, fh, ensure_ascii=False, indent=2)
    print("rows:", len(ROWS), counts)
    print("wrote", csv_path, json_path)


if __name__ == "__main__":
    main()