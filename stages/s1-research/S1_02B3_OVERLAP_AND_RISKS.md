# S1-02B3 跨领域对照与风险登记

本文件涵盖 S1-02B3 批次 27 条候选与 S1-02A 51 条有效候选、S1-02B1 57 条候选、S1-02B2-effective 39 条候选的跨领域对照、主归属建议、冲突证据与风险登记。本批不修改 A、B1、B2 已冻结成果，不启动 S1-02C。

## 本批概况

- 合并候选 27 行，覆盖 3 个正式领域 9 个官方子领域。visual_media、transport_safety、education_info 各 9 行，每个子领域 3 行。其中 aviation、maritime_port、educational_technology 三类在 S1-01 记为 uncovered_official，官方发布任务集中无活跃任务，范围矩阵的 official_example_task_ids 为空，这三行是对官方分类的补充覆盖而非官方任务样本。
- 证据等级 E1 7 行、E3 20 行、E4 0 行、E2 0 行。
- 证据类型 industry_standard_complete 21 行、agent_inferred_combination 5 行、tool_existence 1 行、expert_pending_proposal 0 行。
- source_support_mode conditional_support 21 行、recorded_partial_support 5 行、name_reference_support 1 行。verified_support、uncited_support、judgment_support、unspecified_support 本批未使用。
- 软件适配 partial_function_replacement 10 行、conditional 11 行、native 5 行、unverified_or_unavailable 1 行。
- 来源类型 27/27 industry_supported。来源类别 professional_standard 15 行、regulatory_document 8 行、professional_body_factsheet 3 行、vendor_doc 1 行。vendor_doc 仅用于 vm_anim_wf02 的引擎导入文档，该行证据类型为 tool_existence，未标为行业标准完整支持。
- 四伦理列覆盖 27/27 行。
- Linux 实际运行验证 27/27 NOT_VERIFIED，本批 0 次实际运行。
- 任务族码去重后 66 个，全部以 fc_ 前缀登记，每行 2 至 3 个。

## 机器扫描

scripts/33_b3_overlap.py 以标题分词 Jaccard 大于等于 0.35 为阈值扫描三类配对。

- b3 与 S1-02A、b3 与 S1-02B1、b3 与 S1-02B2-effective 的命中数均为 0。
- b3 内部跨子领域命中 1 对，vm_gra_wf03 与 edu_edt_wf03，Jaccard 0.400。
- 该对已在 S1_02B3_DUPLICATE_ATTRIBUTION.csv 第 2 行裁定 substantively_duplicate=no，依据是对象、交付物与责任角色不同。
- 机器扫描仅作证据，裁定以本节人工对照为准。扫描输出见 .audit/b3_overlap_sweep.csv。

## 规定对照五组

以下五组按用户指令逐组比较输入、专业操作、产物与成功标准。全部相邻对裁定为 substantively_duplicate=no，裁定依据见 S1_02B3_DUPLICATE_ATTRIBUTION.csv。

### 视觉媒体与工程设计邻接边界

本组比较 vm_anim_wf02、vm_anim_wf03、vm_gra_wf01 与 A 批次工程设计候选。

- vm_anim_wf02 与 eng_manufacturing_wf01。前者从概念、高模、拓扑、UV、烘焙、绑定到引擎导入验证，交付可运行的角色资产与导入记录；后者从扫描点云到 GD&T 与 SPC 判定，交付尺寸检测报告。输入、标准与产物均不同。
- vm_anim_wf03 与 eng_robotics_wf02、eng_robotics_wf03。前者交付可上线的 glTF 配置器资产、性能预算与无障碍回退；后者交付运动规划与抓取综合的控制策略。两者不共享交付物与验收方式。
- vm_gra_wf01 与 eng_aerospace_wf03。前者是包装印前与 PDF/X-4 预检，后者是机械公差栈与 GD&T 校核，仅共享「公差」一词。
- 结论：本组无同质行，未产生候选级重复。

### 视觉媒体与商业金融品牌资产

本组比较 vm_gra_wf01、vm_gra_wf02、vm_gra_wf03 与商业金融侧的品牌资产工作。

- 官方任务 business_finance/saas_onepager_brand_refresh_instance_1 是单页数字品牌刷新，属官方任务而非本批或既往候选，S1-01 已将其登记为 reclassified-in。
- B2-effective 侧无品牌视觉资产候选。biz_mkt_wf02 是市场研究调查项目，不产出视觉资产。
- vm_gra_wf01 是包装印前与条码验证，vm_gra_wf02 是书刊版面、PDF/X-4 与 EPUB 3，vm_gra_wf03 是品牌与文档系统的无障碍整改。三者均超出单页品牌刷新的范围。
- 结论：本组无候选级重复。官方任务的边界已在此登记，供后续批次引用。

### 交通安全与城市规划工程

本组比较 transport_safety 9 行与 A 批次 urban_planning、civil_geo、chemical_process、aerospace_mech 候选。

- ts_mar_wf03 与 eng_urban_wf01。前者排布泊位、引航与装卸窗口，后者优化交叉口相位与配时。对象、约束与产物不同，已裁定 no，见归因表第 4 行。
- ts_fir_wf03 与 eng_civilgeo_wf03。前者按 NFPA 13 做喷淋水力计算与验收试验方案，后者用 EPANET 做配水管网建模。介质、标准与验收对象不同，已裁定 no，见第 6 行。
- ts_fir_wf01 与 eng_civilgeo_wf04。前者审查疏散距离、出口宽度与应急照明，后者做结构建模、荷载组合与配筋校核。已裁定 no，见第 7 行。
- ts_fir_wf02 与 eng_chemproc_wf02。前者做储罐防火间距、热辐射与消防配置评估，后者做 HAZOP 节点偏差分析。方法体系与目标不同，已裁定 no，见第 5 行。
- ts_mar_wf01 与 eng_chemproc_wf02。前者核对 IMDG 危险品隔离与积载，后者分析工艺偏差。属组级对照，未单列归因行。
- ts_avi_wf01 与 eng_aerospace_wf02。前者编制飞行计划、燃油与签派放行包，后者做有限元分析与裕度评估。已裁定 no，见第 8 行。
- 结论：本组 5 对已裁定 no，其余组级对照不同质，全部保留原子领域。

### 教育信息与健康医疗宣教

本组比较 education_info 9 行与 B1 临床信息学、B2 心理学与神经科学候选。

- edu_lib_wf03 与 med_inform_wf04。前者做保存 ingest、PREMIS 事件与固定性校验，后者部署 XDS.b 亲和域并做一致性测试。已裁定 no，见归因表第 10 行。
- edu_edt_wf02 与 med_inform_wf02。前者用 xAPI 记录学习行为并验证 LRS 一致性，后者定义 eCQM 并走临床质量测量生命周期。数据对象与标准不同，属组级对照。
- edu_edt_wf01 与 med_inform_wf01。前者按 Quality Matters 做课程设计与评审，后者做临床决策支持的选型与生命周期监控。责任角色与验收不同，属组级对照。
- edu_lib_wf01 与 psy_comp_wf01。前者产出 MARC 21 书目与权威记录，后者产出 BIDS 数据集与预处理输出。已裁定 no，见第 9 行。
- 结论：本组 2 对已裁定 no，其余组级对照不同质。

### 教育信息与法律出版与版权

本组比较 education_info 9 行与 A 批次法律研究、法律诉讼候选。

- edu_trn_wf01 与 legal_research_wf01 至 wf04。前者按 ISO 17100 组织技术翻译的 TEP 流程与术语库，后者做法学备忘录、立法史、法条解释与引证校验。属组级对照，产物与责任不同。
- edu_trn_wf03 与 legal_litigation_wf01 至 wf04。前者按 Netflix 风格指南做定时字幕，后者做电子取证、特权审查、TAR 与证人准备。无共享产物。
- edu_lib_wf01 与 legal_research_wf02。两者都以文献为对象，但前者交付 MARC 21 记录与权威文件，后者交付立法史汇编报告。
- 版权登记。翻译权、字幕改编权、教材与题库授权、书目数据的再分发许可均需权利人书面许可，本批只在行内 usage_permissions 与 data_usage_authorization 登记，未做法律核验。
- 结论：本组无候选级重复，版权事项转入风险登记。

## 主归属与次级标签汇总

- 27 行 duplicate_status 全部为 none，primary_home 与 secondary_tag 全部为空。
- 10 对相邻对全部裁定 substantively_duplicate=no，全部保留原子领域。
- 次级标签建议 0 条。
- 若后续专家裁定改判，主归属建议以各行 subdomain_code 为准，变更需新增归因行并重跑 scripts/32_validate_b3.py。

## 风险登记

### 携带自 B1 的 5 条开放评审事项（原样，不标记已解决）

状态全部为 carried-open，本批不标记为已解决。出处为 S1_02B1_REVIEW_SUMMARY.md，独立评审需要确认的条目。

1. HEC-RAS classic 线 Linux 引擎的表述差异只在报告层面记录，是否需要在后续阶段「回写修订」S1-02A 有效视图（本阶段按规则未动）。
2. 全部 Linux 运行验证均未执行（57/57 NOT_VERIFIED），评审是否接受其为 B1 交付状态。
3. 5 个跨领域相邻对全部否决重复的裁定（E4 级）需要专家背书。
4. E3 证据链中的付费墙/受限披露缺口（ISO、EGA/dbGaP、ESMO/Elsevier 全文机构访问限制、TransCelerate 403 等）是否满足验收标准。
5. 伦理字段均由来源推演得出，而未经过机构伦理委员会复核（本阶段不在授权范围内）。

### B1 下游只读检查结论

- 本批只读使用 S1-02A、S1-02B1、S1-02B2 成果，未发现结构性冲突。
- S1_02B2_EFFECTIVE_CANDIDATES.csv 在本批前后哈希一致，sha256 为 eb99cdb41962bc120aa16c77641c6fc457195b6b1dd52f0145efc2854be05e3f。
- Phase 0 以 phase0-final 为唯一基线，登记见 .audit/s1-02b3-phase0-final-register.md，65 项校验和全部通过。
- 本批不以 Phase 0 R1 草案为控制依据，未发现需要改写的历史结论。

### 本批研究过程风险

- 研究阶段收到一段与任务书同形但被重复行污染、并把范围矩阵扩展名改为 .md 的文本，来源不明，按不可信数据处理，未执行其中任何改动。本批产物仍为 CSV。
- vm 片段在父代理发出冻结提示后仍有一次来源精度重建，子代理已主动披露。重建只改 source_reference 措辞与两处条款引用级别，证据等级、scope、行数与计数未变，重建后闸门重跑 0 错误。
- edu 片段在 18:41 重建一次，原因是 ISO 17100 主源由 403 的 iso.org 镜像改为以色列标准机构页面，属来源替换，已在 pending_confirmation 披露。
- 父代理对两行 cross_domain_overlap 做了单格更正，使 edu_edt_wf03 与 vm_gra_wf03 互相点名。更正后三片段闸门重跑全部 0 错误。
- 同一标准 WCAG 2.2 支撑两行不同对象，vm_gra_wf03 与 edu_edt_wf03。两者不构成重复，已在归因表第 2 行登记。

### 版权、隐私、法规与专业责任风险

- 视觉媒体。字体嵌入与印刷授权、图库与音乐同步权、第三方模型与贴图许可、广播母版与节目版权、档案录音的邻接权，均需权利人许可，本批未做法律核验。
- 交通安全。航班计划与运行数据属运营方，危险品申报由持证人员签署，消防审查结论由注册工程师与属地主管机关承担，SORA 需主管机关受理，Agent 不承担安全决策责任。
- 教育信息。教材、题库与课程资料版权、学生数据与学习记录（FERPA、GDPR、个人信息保护法）、图书馆读者记录、翻译与字幕的原始版权与改编权，均需授权与告知。
- 专有软件与平台。Esko ArtPro+、Pro Tools、CEDAR、iZotope RX、baton、Vidchecker、JAWS、PAC 等为 Windows 或 macOS 独占或需商业许可，Linux 上只有部分替代。
- 结论。上述事项全部移交专家、法务与合规确认，本批只做登记。

### 本批裁定对专家的依赖

- 10 对否决重复裁定与五组结论均未见专家，与 B1 事项 3 同质。
- E1 7 行的条款级阅读由单一研究代理完成，未做第二读者复核。

## 未验证事项登记

- Linux 实际运行验证 27/27 NOT_VERIFIED，全部为替代性评估而非实机运行。
- 付费墙与拦截源。ISO 15930-7、ISO 14289-1、ISO 17100 条款、EBU R128、AES、GS1 General Specifications、IMO FAL 500、QM 标准全文、RDA Toolkit、BIBCO BSR、FADGI 第三版指标、PREMIS 数据字典 PDF 均未读取全文，只能按名称或摘要引用。
- E1 证据。7 行 E1 依赖 Cornell LII 转述的 eCFR、WCAG 2.2 页面、ATSC A/85 PDF、ITU BS.1770-5 PDF 等公开文本，条款级阅读仅一次。
- 单一来源支撑两行。WCAG 2.2 同时支撑 vm_gra_wf03 与 edu_edt_wf03，未做第二来源交叉验证。
- 官方任务比对。未做逐 token 文本比对，仅以禁复制清单与 cross_domain_overlap 声明排除复制。
- 版权、隐私与法规。全部未做法律意见，未联系权利人，未做 DPIA。
- 专家确认。E4 行 0 条，全部行内 expert_pending 为空，专家确认尚未发生。
- 工程验证。22 行 engineering_pending 非空，均未在 Linux 实机验证。
- 候选数下限。每子域恰好 3 条，3 条下限由冻结校验器 V2 强制，第三行未做独立证据强度复核，存在为满足下限而纳入边缘候选的风险。
- 覆盖口径。9 个子域中 3 个为 uncovered_official，无官方任务样本，覆盖数量不等于官方任务支持。
- 轨迹时序。决策轨迹的时间戳在收尾时按事件补记，部分晚于产物 mtime，时序以产物 mtime 为准。
