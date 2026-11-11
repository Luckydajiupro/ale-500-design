# S1-01 独立复审后定向修订记录（REVISION LOG）

本文件记录 m00177 独立复审后对 S1-01 研究产物的定向修订。证据等级：`E1` 本轮直接观察，`E2` 引自 Phase 0 R1（待复审），`E3` 推断，`U` 未知。

修订日期：2026-11-09。修订范围仅限当前研究目录 `/Users/mac/Workspaces/ale-研究设计/ale-500-category-research/`。Phase 0、四份官方输入、总方案 v0.4 保持只读未改动。

## 修订 1：Taxonomy 两层口径

问题：旧版把 task_card 观察到的 49 子域当作"官方分类"，未区分完整官方分类与活动任务观察分类。

修订：

- 以论文 Figure 2（arXiv:2606.05405v4 的 `panel_c_subdomain.svg`，OCR 提取）为权威来源，建立 **55 官方子域** 完整名单（`evidence/official_taxonomy_55.tsv`，55 行）。
- 官方分类 = **13 个命名行业簇 + "Other" 兜底桶**。13 个"正式领域"指命名簇，不含 Other 兜底。`other/sports`（14.1）在 Other 兜底内，不属 13 正式领域。
- 活动任务观察分类 = 14 域 / 49 子域。官方 55 − 观察 49 = **6 个未覆盖官方子域**。
- `S1_01_CATEGORY_MAPPING.csv` 改为 55 行两层映射，新增 `coverage_status` 列（`active_observed` / `uncovered_official`）与 `official_domain_name`、`id_source` 列。

6 个未覆盖官方子域（名 + ID + ID 来源）：

| 子域 ID | 名称 | ID 来源 |
|---|---|---|
| 1.4 | Chemical & Process Engineering | inferred（E3，编号顺序推断） |
| 1.7 | Mining, Petroleum & Geological Engineering | inferred（E3） |
| 10.1 | Aviation & Airspace Operations | prev（classifier.previous 确认，E1） |
| 10.2 | Maritime & Port Operations | inferred（E3） |
| 11.1 | Educational Technology | inferred（E3） |
| 12.2 | Precision Agriculture | inferred（E3） |

2 个空 ID 号（编号跳号，非子域）：1.9（engineering）、8.3（visual_media）。

修正旧错误：旧版"7 个缺口 = 1.4/1.7/1.9/8.3/10.1/10.2/11.1"有误——1.9、8.3 是空 ID 非子域，且漏了 12.2 Precision Agriculture。正确为 **6 个未覆盖子域**。

验证：C1=49 观察行、C2=55 官方子域、C3=6 未覆盖，均 PASS。

## 修订 2：13 处跨域重分类证据路径

问题：旧版用重分类后领域的目录通配符作为唯一证据，未给出逐任务真实 `task_id` 与文件路径。

修订：

- 新增 `S1_01_RECLASSIFICATION_EVIDENCE.csv`（13 行，16 列），逐任务记录：真实 `task_id`、`old_directory`、当前 taxonomy（domain/subdomain id/code/name）、`classifier.previous` 历史分类、`reclassification_source`（task_all_workflows.csv）、`applied_at`、`rationale_present`、`task_card_path`（真实文件相对路径）。
- 生成脚本 `scripts/06_reclassification_evidence.py`，按真实 `task_id` 定位，不使用目录通配符。
- 结论：13 张跨域重分类卡全部 **无 `rationale` 字段**（字段缺失，非空值），重分类依据不可核实，标为 UNKNOWN。

验证：C5=13 行、rationale_present=no 于 13/13 行，均 PASS。

## 修订 3：清理评分内容（eval_hardGates）

问题：`evidence/task_archetype_rows.tsv` 的 `eval_hardGates` 字段泄露了 2 条任务的评分规则正文（`engineering/2d_drawings_to_3d_bridge_model`、`engineering/2d_drawings_to_3d_building_model` 的 hardGates 规则）。

修订：

- `scripts/02_archetype_extract.py` 改为只记录 hardGates 的**存在性 + JSON 类型**，删除规则正文 join。
- 新列 `eval_hardGates_present`（yes/no）与 `eval_hardGates_type`（list/str/absent/other），替换旧 `eval_hardGates`。
- 重跑后：2 条记录 present=yes/type=list，133 条 present=no/type=absent，无规则正文残留。

验证：C7（无旧列、无正文泄露）PASS。

## 修订 4：A/B 机器可读三态

问题：旧版把 A/B 状态合并成单字符串（如 `A:exclude-whole-domain; B:exclude (CS subdomain)`），且 `other/sports` 被标为普通非 CS 候选。

修订：

- `S1_01_CATEGORY_MAPPING.csv` 拆为三个独立列 `ab_A_status`、`ab_B_status`、`ab_dispute`。
- computing_math 7 子域：
  - `ab_A_status` = `excluded`（A 方案整类排除，全 7 子域一致）。
  - `ab_B_status`：software_eng / data_analytics / ai_cs_research / cybersecurity / infra_cloud = `excluded_cs_subdomain`；**math_ops_research = `conditional_keep_non_cs_math_or`**（条件保留）；quantum = `dispute_unresolved`。
  - `ab_dispute`：仅 quantum = `quantum_straddles_physics_and_cs`。
- `other/sports` 的 `exclusion_status` 改为 `catch_all_not_auto_approved`，**不**自动作为获批非 CS 配额类别。
- 本轮不裁决 A 还是 B。

## 修订 5：证据等级

问题：旧版把 verifier 实现类当"验证方法"，把工作流/专家能力写成确定性事实。

修订：

- `S1_01_TASK_ARCHETYPE_EVIDENCE.csv` 拆分两列：`verifier_impl_class`（R1 verifier_type 计数，如 `scorer=3`，E2 待复审）与 `verification_method`（由实现类推断的实际验证方法，E3 研究假设，未独立确认）。
- 新增 `research_hypothesis_fields` 列 = `professional_workflow;expertise_clues;verification_method`，明确这三列为研究假设，非领域专家确认事实。
- R1 待复审状态保留（所有 E2 字段继续标"待复审"）。

## 修订 6：版本集合核对（任务 ID 级）

问题：审查称"v1 历史 153 条"，与 122 + 30 = 152 差 1 条。

修订（E1，脚本核对）：

- v1 tag 的 `selected_tasks/full.txt` = **153 行 = 152 任务 + 1 注释行**（首行 `# All tasks from`）。v1 真实任务数 = 152，非 153。
- v1.1（122 活动）与 30 退役的集合关系**精确成立**：v1.1 == v1 − retired，v1.1 ∩ retired = ∅，|v1| = 152 = 122 + 30。
- 结论：无缺失任务、无重命名/合并遗留。审查的"153"是 v1 full.txt 原始行数（含注释行）的误读。
- 物理卡：v1 tag 165 张 = 152 选中 + 13 额外；HEAD 135 张 = 122 活动 + 13 额外。30 退役任务已从 HEAD 的 tasks/ 移除（存于 v1 tag 与 ale-data/archive/）。

## 校验结果

`scripts/07_validate.py` 全部 PASS：

| 检查 | 结果 | 值 |
|---|---|---|
| C1 49 观察行 | PASS | 49 |
| C2 55 官方子域 | PASS | 55 |
| C3 6 未覆盖 | PASS | 6 |
| C4 122 唯一活动任务 | PASS | 122 |
| C5 13 重分类 | PASS | 13 |
| C6 135 卡行 | PASS | 135 |
| C7 eval_hardGates 无泄露 | PASS | leak=0 |
| C8 原型 49 行 / 122 示例 | PASS | 49 / 122 |

## 变更文件清单

| 文件 | 变更 |
|---|---|
| `S1_01_CATEGORY_MAPPING.csv` | 49→55 行两层映射；新增 official_domain_name / id_source / coverage_status / ab_A_status / ab_B_status / ab_dispute；other/sports 改 catch_all_not_auto_approved |
| `S1_01_TASK_ARCHETYPE_EVIDENCE.csv` | 拆分 verifier_impl_class / verification_method；新增 research_hypothesis_fields |
| `S1_01_RECLASSIFICATION_EVIDENCE.csv` | 新增（13 行逐任务重分类证据表） |
| `evidence/task_archetype_rows.tsv` | eval_hardGates → eval_hardGates_present + eval_hardGates_type |
| `evidence/official_taxonomy_55.tsv` | 新增（55 官方子域完整名单，来自论文 Figure 2） |
| `scripts/02_archetype_extract.py` | 修复 hardGates 泄露 |
| `scripts/04_category_mapping.py` | 两层映射 + A/B 三态 |
| `scripts/05_archetype_csv.py` | verifier 实现类/方法拆分 + 假设标注 |
| `scripts/06_reclassification_evidence.py` | 新增（重分类证据表生成） |
| `scripts/07_validate.py` | 新增（8 项校验） |
| `S1_01_REVIEW_SUMMARY.md` / `S1_01_GAPS_AND_RISKS.md` / `S1_01_SOURCE_REGISTER.md` | 同步修订 |
