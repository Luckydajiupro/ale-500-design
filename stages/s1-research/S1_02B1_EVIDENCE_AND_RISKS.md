# S1-02B1 证据与风险报告

阶段：S1-02B1（physical_sciences 4 子领域 + life_sciences 4 子领域 + health_medicine 5 子领域，共 13）
基线：S1-02A 有效视图 51 条（只读，未修改）
产物：`S1_02B1_WORKFLOW_CANDIDATES.csv`（57 行 × 39 列）、`S1_02B1_SOURCE_CLAIM_MAP.csv`（57 × 10）、`S1_02B1_DUPLICATE_ATTRIBUTION.{csv,md}`、`S1_02B1_BASELINE_CONSISTENCY_REPORT.md`

## 1. 覆盖

- 57 条候选；子领域行数：physics 4、chemistry_materials 4、astronomy 4、earth_atmo 4、biomolecular 5、genomics 4、cell_imaging 4、systems_microbial 5、clinical_diagnostics 5、therapeutic_oncology 5、clinical_informatics 4、public_health 4、clinical_trials 5。
- 全部 13 个目标子领域达到每子领域 3 条的最低门槛（B1 工作规范）。这不是配额，是本轮验证证据数量的自然结果。

## 2. 证据分布

| evidence_kind × evidence_level | 行数 |
| --- | --- |
| industry_standard_complete × E1 | 33 |
| industry_standard_complete × E3 | 3 |
| agent_inferred_combination × E3 | 21 |

- 无 tool_existence 行、无 expert_pending_proposal 行（因此无 E4 候选）：全部候选都建立在可核验的完整工作流或部分开源/已发表来源组合之上。E3 行全部在 `pending_confirmation` 中明确写出缺口与建议的确认路径。
- source_category：professional_standard 20、academic_paper 19、other 10、regulatory_document 6、industry_report 1、vendor_doc 1。vendor_doc 行（1 行）按证据规则只能支撑部分来源组合，作为 agent_inferred_combination/E3 使用，未用于行业标准背书。
- source_type 全为 industry_supported（57/57），无 project_proposal。

## 3. 软件适配（相对 A 基线的工程判读口径）

| software_adaptation | 行数 |
| --- | --- |
| native | 26 |
| partial_function_replacement | 13 |
| conditional | 12 |
| needs_task_redesign | 6 |

- 工程状态的判读沿用了 A 阶段规则：Linux 验证 = NOT_VERIFIED（57/57，本轮没有在服务器上运行任何工具，与阶段权限一致）。
- engineering_pending 按 A 的措辞规则标记：partial_function_replacement / conditional / unverified_or_unavailable 全部标记，native 不标记，该规则由验证器 V5 保证。

## 4. 数据使用授权、隐私、研究伦理、可复现性

- 生命 + 健康（life_/med_）41 行全部填写 4 个伦理字段（data_usage_authorization、privacy_considerations、research_ethics、reproducibility_assessment），全部有来源可查，验证器 V7 保证。
- 研究中的授权/隐私判断来源（在子领域研究文件与字段中标注）：e.g. GDPR 管辖的 EGA/dbGaP 注册页在本轮无法直接抓取（403/404），对应行在 pending_confirmation 中写明管辖与缺口；UniProt 许可页 JS 动态加载；ISO 验证页付费墙；STORMS 清单以引用形式留存未逐条提取。所有缺口均已披露，未把软件/数据库「存在」当作「合规授权」证据。
- phys_ 集群 16 行的 4 个伦理字段全部为空（验证器 V7 反之强制）：物理科学聚类不含人/受试者/可标识生物数据工作流，只涉及观测数据与工程数据。

## 5. 来源核验

- 主来源 URL 分类核验（python urllib HEAD/GET，逐条记录于 `.audit/uN_<stem>_primary_urls.txt`）：
  - phys：13/16 HTTP 200；3 失败为真实 URL 的拦截或瞬时错误（www.iaea.org 403、www.nist.gov 瞬时错误、www.oecd.org 403），与子代理披露一致。
  - med_a：10/10 HTTP 200。
  - med_b：9/13 HTTP 200；4 个 cdc.gov 页面被机器人拦截，独立 web_fetch 确认其中一处返回 200（Field Epi Manual 第 3 章全文匹配其主张）。
  - life：16/18 HTTP 200；2 个 journals.iucr.org 403 为机器人拦截，独立 web_fetch 确认返回 200（CCP4 suite 论文）。
- 本轮未添加任何被 web_fetch 确认不存在的 URL；所有候选行受限于「引用的存在性可核验」+「完整工作流自证」双重约束。

## 6. 与 S1-02A 基线的关系

- S1_02A_EFFECTIVE_CANDIDATES.csv 的 51 行经只读重校验（B0–B4 全部 PASS，脚本 `scripts/15_b1_baseline_check.py` 复跑）。
- HEC-RAS 事实冲突（只报不改）：报告的 A 文本写 classic 线「NO official native Linux」，独立评审已核实 Classic 7.0.2 有 Linux 编译计算引擎（GUI/发行版与引擎的差异）。本阶段文档以评审核实事实为准，未修改 S1-02A 产物。
- 跨领域重复：0 实质性重复；5 相邻对全部裁定独立，详见 `S1_02B1_DUPLICATE_ATTRIBUTION.md`。

## 7. 剩余风险与边界

- Linux 实际运行核验全部待办（NOT_VERIFIED），与本阶段的写权限边界一致。
- 专家级确认待办：本阶段所有E3 行与工程判读都属于「来源可核验但未经领域专家过目」的范围；后续阶段需要专家确认才可作为正式招聘与配额依据。本阶段不产出正式配额、不计算招聘人数、不招募、不开发平台、不启动批量工程评测。B2 由独立评审授权后再启动。
- 机器学习模型的「可复现性」声明仅对工作流步骤（数据版本、代码、报告）成立，不暗示 SOTA 性能复现。
- 子代理间跨聚类命名/口径的轻微漂移由 18/16/17 三套结构检查收敛，不接受人工眼力修订。

## 8. 交付物清单

- `S1_02B1_WORKFLOW_CANDIDATES.csv` — 57 × 39：32 列片段字段 + linux/expert/engineering 根列 + fragment_path + 3 列重复归属标注。
- `S1_02B1_SOURCE_CLAIM_MAP.csv` — 57 × 10：逐候选 来源—主张 映射。
- `S1_02B1_DUPLICATE_ATTRIBUTION.csv` / `.md` — 5 相邻对裁定 + 群组级检查。
- `S1_02B1_BASELINE_CONSISTENCY_REPORT.md` — U1 基线一致性（含 HEC-RAS 冲突报告）。
- `S1_02B1_REVIEW_SUMMARY.md` — 本轮评审摘要与 PASS/FAIL/UNKNOWN 汇总。
- `evidence/s1_02b1_research/` — 4 个聚类的原始研究片段（CSV+JSON）。
- 验证脚本（可复跑）：`scripts/15_b1_baseline_check.py`、`scripts/16_merge_b1.py`、`scripts/17_validate_b1.py`、`scripts/18_check_fragment.py`、`scripts/19_annotate_duplicates.py`。