# S1-02B2 跨领域对照与风险登记

本文件涵盖 S1-02B2 批次与 S1-02A 51 条有效候选、S1-02B1 57 条候选的跨领域对照、主归属建议登记、冲突证据与风险登记。本批不修改 A/B1 已冻结成果。

## 本批概况

- 合并候选 39 行，覆盖 3 个领域 11 个官方子领域，每个子领域均达 3 行以上。
- 证据等级 E1 19 行、E3 20 行、E4 0 行、E2 0 行。
- 证据类型 industry_standard_complete 19 行、agent_inferred_combination 20 行、tool_existence 0 行。
- 软件适配 native 24 行、partial_function_replacement 8 行、conditional 7 行。
- 四伦理列覆盖 39/39 行。
- Linux 实际运行验证 39/39 NOT_VERIFIED，本批 0 次实际运行。

## 机器扫描

scripts/25_b2_overlap.py 以标题分词 Jaccard ≥ 0.35 为阈值扫描三类配对。

- B2×A、B2×B1、B2 内部跨子领域配对命中数均为 0。
- 主要原因，B2 商业与社会科学候选标题以中文为主、A/B1 候选标题以英文为主，词表几乎不相交。机器扫描仅作证据，判定以本节人工对照为准。
- 扫描输出见 .audit/b2_overlap_sweep.csv。

## 规定对照五组

以下五组按用户指令与 A/B1 逐组比较输入、专业操作、产物与成功标准，登记主归属建议、次级标签与冲突证据。全部相邻对裁定为 substantively_duplicate=no，裁定依据见 S1_02B2_DUPLICATE_ATTRIBUTION.csv。

### 商业金融与法律合规

A 法律侧 8 行（legal_research_wf01-04、legal_litigation_wf01-04）与 B2 合规侧 4 行（biz_cmp_wf01-04）逐行比对后，输入（个案事实与法条对机构风险画像与监管条款集）、专业操作（先例调查与文本解析对程序映射与独立测试）、产物（备忘录与实际合规计划包）、成功标准（解释一致性对支柱覆盖矩阵）均不同质。

- 最相似对 biz_cmp_wf02|legal_research_wf03 已单独裁定，见 S1_02B2_DUPLICATE_ATTRIBUTION.csv。
- 主归属建议，两侧均保留原子领域。
- 次级标签建议，biz_cmp 各行登记 legal_research_adjacent。
- 冲突证据，S1-01 映射已将 legal/agora_governance_classify_instance_1 从 legal_research reclass-in 至本批 compliance。本批仅登记该事实，不回写 A 的归属。

### 商业分析与社会科学计量

- biz_ana_wf02|soc_econ_wf02 裁定 no，预测建模与因果识别的输入、操作、产物、成功标准全部不同，证据见重归属 CSV。
- biz_ana_wf02|biz_sup_wf02 为本批内部对，共享 FPP3 教科书来源但业务粒度不同，各留原子领域。
- biz_ana_wf01 CRISP-DM 流失建模与 soc_econ 四行无方法交集，仅作组级记录。
- 主归属建议，全部保留原子领域。

### 心理学实验与健康医学研究

- psy_exp_wf01|med_trials_wf01 裁定 no，在线行为实验与临床试验点监测的监管基础完全不同，IRB 心理伦理对 21 CFR 312 与 ICH GCP。
- psy_exp_wf03|med_diag_wf01 裁定 no，心理测验开发验证对影像结构化评估，对象、判读体系、合规时限均不同。
- psy_exp_wf02 的功效与预注册设计与 B1 med_trials_wf03 的安全性报告属不同问题域，组级记录。
- psy_exp_wf04 的 PRISMA 元分析在 B1 医学 23 行中无系统综述行可采用，最小重叠，组级记录。
- 主归属建议，全部保留原子领域。

### 社会科学统计与医学因果推断

- soc_econ_wf01|med_pubhealth_wf04 裁定 no，同属复杂调查加权技术但目的为统计生产对公共卫生监测，权重体系不同。
- soc_econ_wf02|med_inform_wf03 裁定 no，DID 政策评估对 OMOP 观察性队列研究，识别假设与表型校验体系不同。
- 主归属建议，全部保留原子领域。

### 金融运筹与computing_math待裁决边界

- 边界另一侧 computing_math 9.4 math_ops_research 在 A、B1、B2 三批中候选数均为 0，无实体行可配对，此前裁决边界维持未裁决状态。
- B2 侧 biz_quant 4 行方法上与运筹学相邻，biz_quant_wf01 为 FRTB 市场风险统计检验，biz_quant_wf02 为 DSR/PSR 多重检验校正类回测评估。
- 主归属建议，全部保留 quant_finance。
- 次级标签建议，biz_quant_wf01、biz_quant_wf02 登记 math_ops_research_adjacent，供 9.4 激活批次参考。
- 冲突证据，无，对方为零候选空白。

## 主归属与次级标签汇总

见 S1_02B2_DUPLICATE_ATTRIBUTION.csv，共 7 对，全部 substantively_duplicate=no。

## 风险登记

本批新增风险与携带风险如下。

### 携带自 B1 的 5 条开放评审事项（原样，不标记已解决）

1. HEC-RAS classic 线 Linux 引擎的表述差异只在报告层面记录，是否需要在后续阶段「回写修订」S1-02A 有效视图（本阶段按规则未动）。
2. 全部 Linux 运行验证均未执行（57/57 NOT_VERIFIED），评审是否接受其为 B1 交付状态。
3. 5 个跨领域相邻对全部否决重复的裁定（E4 级）需要专家背书。
4. E3 证据链中的付费墙/受限披露缺口（ISO、EGA/dbGaP、ESMO/Elsevier 全文机构访问限制、TransCelerate 403 等）是否满足验收标准。
5. 伦理字段均由来源推演得出，而未经过机构伦理委员会复核（本阶段不在授权范围内）。

### B1 下游只读检查结论

前置检查（scripts/20_b2_precheck.py）对 B1 下游读取执行了结构、重复 ID、专业结论依据、伦理缺漏与敏感信息扫描。

- 结构错误无，重复 ID 无，来源映射缺失无。
- 敏感信息扫描无真实个人敏感数据。电子邮箱命中 2 处，均为 CDC 公共项目联系人（edx@cdc.gov、nssp@cdc.gov）。phone-like 命中共 82 处（workflow 77、source-claim 5），9 位以上连续数字串 0 处。逐条核实全部为 DOI 尾号、arXiv 编号、PMID、页码跨度和页面编号等文献类片段（如 40192-014-0029-1、1811.02042、2404.03002、59774192、76414402），无个人敏感数据。
- 以上结论仍随本文件进入独立评审待确认清单。

### 本批研究过程风险

- biz_b 片段连续两次静默失败后拆分为 biz_b1、biz_b2，其中 biz_b1 经历一次 pstack 失败与一次性 subagent 工具切换，6 行候选最终由受督导的子代理落盘并通过 22 校验器。该片段所有行已按同一标准复核，事件全程记录于 .audit/s1-02b2.tsv。
- ICO 与 ISO 站点 403 拦截，biz_hr_wf01-03 与 biz_mkt_wf01、biz_mkt_wf03 共 5 行因此证据降级为 E3 并登记缺口。
- 本批 20 行 E3 均为多来源组合证据，缺口全部写入各行的 pending_confirmation。

### 本批裁定专家的依赖

- 7 对否决重复裁定与 B1 事项 3 同质，属于未见专家的判断，需要独立专家背书。
- 本批无 E4 行，无 expert_pending_proposal 候选待批复。

## 未验证事项登记

- Linux 实际运行验证，39/39 NOT_VERIFIED，本批设计内未执行任何一次运行。
- 量表版权，psy_exp_wf03 的 MMPI/WAIS 专有评分与常模授权仅按公开表述推断，授权条款未核验。
- 神经影像数据许可，psy_cluster 各行的 BIDS/OpenNeuro 许可措辞未逐条捕获。
- 精算与会计口径，biz_acc_wf03 比率口径、biz_act_wf01 精算假设、biz_act_wf03 折现率口径需执业人员确认。
- 合规执行细节，OFAC 命中处置的司法辖区差异、FinCEN 30 天时钟口径需合规官确认。
- 市场数据许可，biz_quant_wf04 的 CME 政策页 403 未访问正文，许可盘点本身即以授权结果为交付物。
- 受拦截权威源清单，ICO、ISO、PCAOB、FATF、FFIEC、ecfr.gov 正本、otexts.com、sec.gov、CME，共影响 7 行候选的证据等级与 10 个行内 pending 字段。
- 全部 3 个官方示例任务（internal_employee_agent_instance_1、digital_marketing_ab_test_analysis_1、american_option_pricing_ls、odoo 等）未被本批候选复制。