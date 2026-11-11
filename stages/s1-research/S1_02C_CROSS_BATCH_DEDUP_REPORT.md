# S1-02C 跨批次重复归并报告

状态：已完成分析层构建，等待独立评审。本报告不分配配额，不计算专家人数，不启动招募。

## 0. 结论

1. 四批共登记 25 组重复对照，其中实质重复 3 组、非重复 22 组。S1-02C 不重新裁定，只做跨批次归并、主归属保留与风险登记。
2. 3 组实质重复全部落在 A 批次内部，分别是 HEC-RAS 洪泛区、EPANET 配水管网、DFT 扫描链与 ATPG。主归属沿用 A 批次裁定，未改动。
3. 25 组对照里有 14 组跨批次、11 组同批次。14 组跨批次对照的裁定全部为“非重复”，没有任何跨批次合并。
4. 45 位候选进入过至少一组对照，占 50 个配对席位。5 位候选同时出现在两组对照中，因此席位多于人数。
5. 任务族比重复对照更宽。7 组对照的两端落在同一任务族内，其中 3 组是实质重复，4 组仍是明确非重复。同族不等于重复，这是本轮最重要的口径结论。
6. 任务族层面的跨批次收敛只有 3 个族，全部由子领域相邻造成，不由重复裁定造成。

## 1. 输入与口径

输入为四份既有裁定文件，只读：

| 批次 | 文件 | 组数 | 实质重复 | 非重复 |
|---|---|---|---|---|
| A | S1_02A_DUPLICATE_ATTRIBUTION.csv | 3 | 3 | 0 |
| B1 | S1_02B1_DUPLICATE_ATTRIBUTION.csv | 5 | 0 | 5 |
| B2 | S1_02B2_DUPLICATE_ATTRIBUTION.csv | 7 | 0 | 7 |
| B3 | S1_02B3_DUPLICATE_ATTRIBUTION.csv | 10 | 0 | 10 |
| 合计 |  | 25 | 3 | 22 |

口径说明：

- 本轮不重新生成候选，不重新抓取来源，不新增相似度打分，也不做 token 级官方任务比对。
- 对照组编号统一为 DP-{批次}-{序号}，仅用于跨文件引用，不改变原文件行序。
- 主归属只在实质重复组内成立。22 组非重复对照没有主归属，只有各自的子领域归属。
- 任务族归属是本轮新增的分析层，不构成重复裁定。一个族可以容纳多组非重复工作流。

## 2. 三组实质重复

### 2.1 DC-HYD-FLOOD

| 项 | 内容 |
|---|---|
| 对照 | DP-A-01，同批 A |
| 成员 | eng_civilgeo_wf02（civil_geo），ag_envwater_wf03（env_water） |
| 任务族 | 两者均为 WF-WATER |
| 主归属 | ag_envwater_wf03 |
| 裁定依据 | 同一 HEC-RAS 洪泛区建模工作；civil_geo 侧只做设计流量下的结构水力参数，env_water 侧做 HEC-HMS 产汇流加 HEC-RAS 演进加淹没范围制图 |
| 处置 | 保留双工作流，civil_geo 侧按 A 批次建议改写为桥梁、涵洞、堤防的冲刷与回水设计；主归属不变 |
| 未决 | civil_geo 改写后的边界是否仍与 env_water 重叠，待专家确认 |

### 2.2 DC-HYD-DIST

| 项 | 内容 |
|---|---|
| 对照 | DP-A-02，同批 A |
| 成员 | eng_civilgeo_wf03（civil_geo），ag_envwater_wf04（env_water） |
| 任务族 | 两者均为 WF-WATER |
| 主归属 | ag_envwater_wf04 |
| 裁定依据 | 两者都是 EPANET 水力建模；差别只在新建管网设计 sizing 与既有管网校准运行 |
| 处置 | 保留双工作流，主归属不变 |
| 未决 | A 批次自评 HIGH 近似重复。合并，还是按“设计 vs 运行”永久拆分，仍待专家裁定；这是 25 组里唯一被标为 HIGH 的未决项 |

### 2.3 DC-DFT-ATPG

| 项 | 内容 |
|---|---|
| 对照 | DP-A-03，同批 A |
| 成员 | eng_electronics_wf02（electronics），eng_semiconductor_wf03（semiconductor） |
| 任务族 | 两者均为 WF-SEMI-EDA |
| 主归属 | eng_semiconductor_wf03 |
| 裁定依据 | 扫描链插入与 ATPG 属芯片级可测性设计；electronics 侧当前写法是板级视角，属错误归属 |
| 处置 | 保留主归属；electronics 侧要么改归半导体，要么改写为板级 JTAG 边界扫描 |
| 附带问题 | 该组还记录了 OpenROAD 的 ATPG 平台能力声明错误，改写时必须一并修正 |
| 未决 | 改归还是改写，二选一待专家裁定 |

## 3. 二十二组非重复对照

完整清单见附录 A。按差异机制归纳为五类：

1. 生产方与消费方。phys_earth_wf01 生产全球数值天气预报，ag_envwater_wf03 把预报产品当作河流强迫；两边输入输出上下游关系明确，不构成重复。
2. 测量与判定分离。phys_phys_wf01 做患者级 IMRT 剂量验证，med_onco_wf01 做放疗计划与病程复核；一个测剂量，一个做临床判定。
3. 方法名相同但对象不同。phys_chem_wf03 的 QSAR 用于 REACH 监管安全评估，life_biomol_wf04 的分子对接用于药物先导筛选；都用计算化学，任务与交付物不同。
4. 数据源相同但分析目标不同。biz_ana_wf02 与 biz_sup_wf02 共用 FPP3 教材，前者做企业级预测，后者做 SKU 分层协调与 FVA 评估；共享教材不等于共享任务。
5. 交付物与责任主体不同。B3 的 10 组全部属此类，例如动画母版与 5.1 终混、品牌文档无障碍与课程无障碍、载体采集与仓储摄取、港口周转与信号配时、防火间距与 HAZOP、喷淋水力与配水管网、疏散审查与结构分析、飞行计划与有限元、编目与神经影像整理、数字保存与临床文档共享。

其中第 5 类的 DP-B3-02 需要单独说明。vm_gra_wf03 与 edu_edt_wf03 都引用 WCAG 2.2 AA，B3 批次已把两者的 cross_domain_overlap 单元格纠正为互相指名。裁定仍为非重复，理由是品牌文档整改与课程 LMS 整改的对象、交付物、责任角色不同。S1-02C 把两者都归入 WF-A11Y，这是族级收敛，不是重复合并。

## 4. 跨批次维度

14 组跨批次对照全部为非重复：

| 对照 | 成员（批次） | 任务族 | 差异要点 |
|---|---|---|---|
| DP-B1-01 | phys_phys_wf04（B1）, eng_energypower_wf04（A） | 同为 WF-NUCLEAR-SAFETY | 临界安全基准验证 vs 熔盐堆燃料循环与热工水力仿真 |
| DP-B1-02 | phys_earth_wf01（B1）, ag_envwater_wf03（A） | WF-ATMOS vs WF-WATER | 数值天气预报生产 vs 河流洪水消费预报产品 |
| DP-B2-01 | biz_cmp_wf02（B2）, legal_research_wf03（A） | WF-FINCRIME vs WF-LEGAL-RESEARCH | AML 计划评估 vs 成文法解释 |
| DP-B2-04 | psy_exp_wf01（B2）, med_trials_wf01（B1） | WF-BEHAV-RESEARCH vs WF-CLIN-TRIALS | 在线实验部署 vs 临床试验监查 |
| DP-B2-05 | psy_exp_wf03（B2）, med_diag_wf01（B1） | WF-BEHAV-RESEARCH vs WF-DIAG-IMAGING | 心理测验信效度 vs 乳腺影像判读 |
| DP-B2-06 | soc_econ_wf01（B2）, med_pubhealth_wf04（B1） | WF-SURVEY-STATS vs WF-PUBLIC-HEALTH | ACS PUMS 复制权重 vs BRFSS 复杂抽样 |
| DP-B2-07 | soc_econ_wf02（B2）, med_inform_wf03（B1） | WF-ECON-EVAL vs WF-CLIN-INFORMATICS | 政策 DID vs OMOP 观察性研究 |
| DP-B3-04 | ts_mar_wf03（B3）, eng_urban_wf01（A） | WF-MARITIME vs WF-TRANSPORT | 泊位与引航窗口 vs 信号配时 |
| DP-B3-05 | ts_fir_wf02（B3）, eng_chemproc_wf02（A） | WF-FIRE vs WF-PROCESS-ENG | 防火间距与消防配置 vs HAZOP 偏差分析 |
| DP-B3-06 | ts_fir_wf03（B3）, eng_civilgeo_wf03（A） | WF-FIRE vs WF-WATER | 喷淋水力计算 vs EPANET 配水管网 |
| DP-B3-07 | ts_fir_wf01（B3）, eng_civilgeo_wf04（A） | WF-FIRE vs WF-STRUCT-FEA | 疏散合规 vs 结构分析 |
| DP-B3-08 | ts_avi_wf01（B3）, eng_aerospace_wf02（A） | WF-AVIATION vs WF-STRUCT-FEA | 飞行计划与签派 vs 有限元裕度 |
| DP-B3-09 | edu_lib_wf01（B3）, psy_comp_wf01（B2） | WF-LIBRARY vs WF-NEUROIMAGING | RDA 编目 vs BIDS 数据集整理 |
| DP-B3-10 | edu_lib_wf03（B3）, med_inform_wf04（B1） | WF-LIBRARY vs WF-CLIN-INFORMATICS | PREMIS 保存摄取 vs XDS.b 文档共享 |

跨批次对照集中在 B3 对 A、B1、B2 的对照，共 7 组；B2 对 A、B1 共 5 组；B1 对 A 共 2 组。这与 B3 批次设计时指定的五组比较方向一致，属于设计使然，不是随机分布。

11 组同批次对照为 A 3 组、B1 3 组、B2 2 组、B3 3 组。同批次全部为已裁定的成对比较，没有新增。

## 5. 族级重复与主归属

### 5.1 重复簇与任务族

3 组实质重复全部落在两个族内：

- WF-WATER 有 6 位主成员，其中 4 位分属 DC-HYD-FLOOD 与 DC-HYD-DIST 两个簇；另 2 位（ag_envwater_wf01、ag_envwater_wf02）不在任何簇内。
- WF-SEMI-EDA 有 2 位主成员，正好构成 DC-DFT-ATPG 一个簇。

主归属在候选层只写入 6 位簇成员：3 位 primary、3 位 secondary。其余 39 位进入过非重复对照的候选记为 no_duplicate_member，不设主归属；129 位未进入任何对照的候选记为 none。四类合计 174。

### 5.2 同族非重复

7 组对照的两端在同一族内：

| 对照 | 共同族 | 裁定 |
|---|---|---|
| DP-A-01 | WF-WATER | 实质重复 |
| DP-A-02 | WF-WATER | 实质重复，HIGH 未决 |
| DP-A-03 | WF-SEMI-EDA | 实质重复 |
| DP-B1-01 | WF-NUCLEAR-SAFETY | 非重复 |
| DP-B1-03 | WF-MED-PHYSICS | 非重复 |
| DP-B2-03 | WF-FORECAST | 非重复 |
| DP-B3-02 | WF-A11Y | 非重复 |

这张表说明两件事。第一，族是工作家族，不是任务副本。第二，只用族号做去重会误合并 4 组已裁定为非重复的工作流，所以重复裁定必须保留在候选对层，不能上收到族层。

### 5.3 跨批次族

11 个族跨越多于一个子领域，其中只有 3 个跨批次：

| 族 | 批次跨度 | 主成员批次分布 | 次级成员 | 成因 |
|---|---|---|---|---|
| WF-METRO-QUALITY | A;B1 | A 4，B1 1 | 无 | 计量与质量工程同时出现在航空航天、制造与物理计量 |
| WF-NUCLEAR-SAFETY | A;B1 | A 1，B1 1 | 无 | 临界安全与反应堆仿真同族 |
| WF-RESEARCH-DATA | B1;B2 | B1 2，B2 0 | psy_comp_wf01（B2） | 研究数据元数据与沉积，B2 的影像整理以次级成员加入 |

其余 8 个多子领域族都在单批次内：WF-WATER、WF-SEMI-EDA、WF-GEOSPATIAL、WF-STRUCT-FEA、WF-MED-PHYSICS、WF-A11Y、WF-DATA-PROTECT、WF-FORECAST。它们由 A 或 B3 的子领域相邻造成，与重复裁定无关。

## 6. 主归属规则与未决

1. 主归属只来自实质重复裁定，来源是 A 批次文件里的 primary_home 字段。S1-02C 原样保留，不改写、不重排。
2. 非重复对照不产生主归属。B3 文件把“主归属建议”写进 primary_reason 的文本里，本轮不把它提升为重复主归属，只在族层体现工作家族归属。
3. DC-HYD-DIST 的合并与拆分未决，是唯一 HIGH 项。在专家裁定前，两位候选都保留为独立候选，族内并列。
4. DC-DFT-ATPG 的 electronics 侧处置未决。改归半导体或改写为板级 JTAG，两条路都不由本轮决定。
5. B1 复核遗留的 HEC-RAS 措辞问题仍然开放，涉及 DC-HYD-FLOOD 的 civil_geo 侧改写文本。
6. 25 组对照涉及的 45 位候选全部标记 expert_endorsement_required=yes，裁定文本进入 expert_endorsement_basis。B3 的 10 组非重复裁定也在其中，等专家背书，不因本轮归并而视为已确认。
7. 所有裁定沿用原批次的证据基础，本轮没有补充新证据，也没有重新访问来源。任何“非重复”结论都不应被读成已独立验证。

## 7. 局限

1. 本轮不新增相似度扫描。B2 复核已记录，A、B1 标题为英文、B2 标题为中文，机械扫描在 B2 上得到 0 命中，因此不能用扫描结果反证不存在重复。
2. 族归属是分析判断，不是重复裁定。族边界由定义与排除条款固定，见 S1_02C_WORKFLOW_FAMILY_REGISTRY.csv 的 definition 与 boundary_exclusion 两列。
3. 45 位候选的专家背书是待办，不是已完成的确认。把 expert_endorsement_required 读成 PASS 会违背本轮口径。
4. B3 的 10 组对照还叠加了批次级溯源问题，包括时间线补记与 edu 片段重建，详见 S1_02C_REVIEW_SUMMARY.md 第 5 节。这些不影响裁定文本，但影响可追溯性。

## 附录 A：25 组对照全表

| 对照 | 批次关系 | 成员 | 裁定 | 族 | 差异要点 | 主归属 |
|---|---|---|---|---|---|---|
| DP-A-01 | 同批 A | eng_civilgeo_wf02, ag_envwater_wf03 | 是 | WF-WATER | 结构水力参数 vs 全流域洪水制图 | ag_envwater_wf03 |
| DP-A-02 | 同批 A | eng_civilgeo_wf03, ag_envwater_wf04 | 是 | WF-WATER | 新建管网设计 vs 既有管网校准 | ag_envwater_wf04 |
| DP-A-03 | 同批 A | eng_electronics_wf02, eng_semiconductor_wf03 | 是 | WF-SEMI-EDA | 板级视角错置 vs 芯片级 DFT | eng_semiconductor_wf03 |
| DP-B1-01 | 跨批 | phys_phys_wf04, eng_energypower_wf04 | 否 | WF-NUCLEAR-SAFETY | 临界安全基准 vs 反应堆仿真 | 无 |
| DP-B1-02 | 跨批 | phys_earth_wf01, ag_envwater_wf03 | 否 | WF-ATMOS / WF-WATER | 预报生产 vs 洪水消费 | 无 |
| DP-B1-03 | 同批 B1 | phys_phys_wf01, med_onco_wf01 | 否 | WF-MED-PHYSICS | 剂量验证 vs 计划复核 | 无 |
| DP-B1-04 | 同批 B1 | life_sysmic_wf05, med_pubhealth_wf02 | 否 | WF-MICROBIOME / WF-PUBLIC-HEALTH | 研究报告清单 vs 现场流调 | 无 |
| DP-B1-05 | 同批 B1 | phys_chem_wf03, life_biomol_wf04 | 否 | WF-CHEM-REG / WF-COMP-STRUCT-BIO | 监管 QSAR vs 对接筛选 | 无 |
| DP-B2-01 | 跨批 | biz_cmp_wf02, legal_research_wf03 | 否 | WF-FINCRIME / WF-LEGAL-RESEARCH | AML 计划 vs 法条解释 | 无 |
| DP-B2-02 | 同批 B2 | biz_ana_wf02, soc_econ_wf02 | 否 | WF-FORECAST / WF-ECON-EVAL | 经营预测 vs 政策 DID | 无 |
| DP-B2-03 | 同批 B2 | biz_ana_wf02, biz_sup_wf02 | 否 | WF-FORECAST | 企业级预测 vs SKU 分层协调 | 无 |
| DP-B2-04 | 跨批 | psy_exp_wf01, med_trials_wf01 | 否 | WF-BEHAV-RESEARCH / WF-CLIN-TRIALS | 在线实验 vs 临床监查 | 无 |
| DP-B2-05 | 跨批 | psy_exp_wf03, med_diag_wf01 | 否 | WF-BEHAV-RESEARCH / WF-DIAG-IMAGING | 心理测验 vs 乳腺影像 | 无 |
| DP-B2-06 | 跨批 | soc_econ_wf01, med_pubhealth_wf04 | 否 | WF-SURVEY-STATS / WF-PUBLIC-HEALTH | ACS 复制权重 vs BRFSS 设计 | 无 |
| DP-B2-07 | 跨批 | soc_econ_wf02, med_inform_wf03 | 否 | WF-ECON-EVAL / WF-CLIN-INFORMATICS | 政策评估 vs OMOP 研究 | 无 |
| DP-B3-01 | 同批 B3 | vm_anim_wf01, vm_aud_wf02 | 否 | WF-3D-ANIM / WF-AUDIO | 画面母版 vs 5.1 终混 | 无 |
| DP-B3-02 | 同批 B3 | vm_gra_wf03, edu_edt_wf03 | 否 | WF-A11Y | 品牌文档 vs 课程 LMS | 无 |
| DP-B3-03 | 同批 B3 | vm_aud_wf03, edu_lib_wf03 | 否 | WF-AV-ARCHIVE / WF-LIBRARY | 载体采集 vs 仓储摄取 | 无 |
| DP-B3-04 | 跨批 | ts_mar_wf03, eng_urban_wf01 | 否 | WF-MARITIME / WF-TRANSPORT | 泊位引航 vs 信号配时 | 无 |
| DP-B3-05 | 跨批 | ts_fir_wf02, eng_chemproc_wf02 | 否 | WF-FIRE / WF-PROCESS-ENG | 防火间距 vs HAZOP | 无 |
| DP-B3-06 | 跨批 | ts_fir_wf03, eng_civilgeo_wf03 | 否 | WF-FIRE / WF-WATER | 喷淋水力 vs 配水管网 | 无 |
| DP-B3-07 | 跨批 | ts_fir_wf01, eng_civilgeo_wf04 | 否 | WF-FIRE / WF-STRUCT-FEA | 疏散合规 vs 结构分析 | 无 |
| DP-B3-08 | 跨批 | ts_avi_wf01, eng_aerospace_wf02 | 否 | WF-AVIATION / WF-STRUCT-FEA | 飞行计划 vs 有限元 | 无 |
| DP-B3-09 | 跨批 | edu_lib_wf01, psy_comp_wf01 | 否 | WF-LIBRARY / WF-NEUROIMAGING | RDA 编目 vs BIDS 整理 | 无 |
| DP-B3-10 | 跨批 | edu_lib_wf03, med_inform_wf04 | 否 | WF-LIBRARY / WF-CLIN-INFORMATICS | PREMIS 摄取 vs XDS.b 共享 | 无 |

## 附录 B：多次进入对照的候选

| 候选 | 进入的对照 |
|---|---|
| ag_envwater_wf03 | DP-A-01, DP-B1-02 |
| eng_civilgeo_wf03 | DP-A-02, DP-B3-06 |
| biz_ana_wf02 | DP-B2-02, DP-B2-03 |
| soc_econ_wf02 | DP-B2-02, DP-B2-07 |
| edu_lib_wf03 | DP-B3-03, DP-B3-10 |

因此 25 组乘 2 等于 50 个席位，去重后为 45 位候选。