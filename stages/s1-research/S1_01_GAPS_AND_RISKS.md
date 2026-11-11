# S1-01 缺口与风险（GAPS AND RISKS）

本文件记录分类冲突、资料缺口、授权约束与待研究问题（独立复审后修订版）。证据等级：`E1` 本轮直接观察，`E2` 引自 Phase 0 R1（待复审），`E3` 推断，`U` 未知。

## 1. 分类冲突：目录口径 vs 官方 Taxonomy 口径

官方 Taxonomy 以 `task_card.json.taxonomy` 为准，**不等同于**仓库目录（`category`）。R1 的领域统计用目录口径；本轮用官方 taxonomy 口径重算后，122 条活动任务的领域分布发生变化（E1）：

| 官方域 | 目录数 | taxonomy 数 | 差 | 涉及的重分类 |
|---|---|---|---|---|
| agriculture_env | 0 | 1 | +1 | 入：physical_sciences/glm_lake_calibration |
| business_finance | 19 | 18 | −1 | 出：legal_ma_consistency_audit_01→legal、saas_onepager_brand_refresh_instance_1→visual_media；入：legal/agora_governance_classify_instance_1 |
| computing_math | 19 | 18 | −1 | 出：go_game_reconstruction_1→other/sports |
| education_info | 2 | 2 | 0 | — |
| engineering | 16 | 16 | 0 | 出：robotics_blender_tabletop_reconstruction→visual_media；入：transport_safety/abm_hangzhou_metro |
| health_medicine | 19 | 17 | −2 | 出：causal_ihdp_ite_estimation_6a_v1→social、ltmle_targeted_bootstrap_simulation_study→social |
| legal | 2 | 2 | 0 | 出：agora_governance_classify_instance_1→business；入：business_finance/legal_ma_consistency_audit_01 |
| life_sciences | 12 | 14 | +2 | 入：physical_sciences/gillespie_gene_regulatory_network、physical_sciences/lenacapavir_sar_table2_extraction |
| other | 2 | 2 | 0 | 出：mota_exploration→visual_media；入：computing_math/go_game_reconstruction_1 |
| physical_sciences | 14 | 11 | −3 | 出：gillespie→life、glm_lake_calibration→agriculture_env、lenacapavir→life |
| psychology_neuro | 3 | 2 | −1 | 出：reddit_ai_post_codebook_boolean_coding→social |
| social_sciences | 1 | 4 | +3 | 入：causal_ihdp、ltmle、reddit_ai_post |
| transport_safety | 2 | 1 | −1 | 出：abm_hangzhou_metro→engineering/urban_planning |
| visual_media | 11 | 14 | +3 | 入：saas_onepager、robotics_blender、mota_exploration |

共 13 处跨域重分类。逐任务证据见 `S1_01_RECLASSIFICATION_EVIDENCE.csv`（真实 `task_id` + task_card 路径）。13 张卡的 `classifier` 均**无 `rationale` 字段**（字段缺失，非空值），因此重分类**依据无法核实**（U）。

要点：

- `other` 是正式兜底桶（14.1 sports），**不是**自动获批的非 CS 配额类别。目录 other 有 2 个任务，但成员换血（mota_exploration 出、go_game 入），net 仍 2。
- `agriculture_env` 目录 0 任务、2 任务退役，但官方域存在且有 1 个重分类进入的活动任务；其域内"农业"（crop_rotation、ndvi）与"精准农业"（12.2，未覆盖）工作在当前活动集合中**无代表**。
- `social_sciences` 目录只有 1 个任务，但官方 taxonomy 下有 4 个活动任务（3 个从 health/psych 重分类进入），说明目录结构严重滞后于官方分类。

## 2. 资料缺口

- **无权威 Taxonomy 定义文档**：仓库内不存在 `task_all_workflows.csv` 或独立 Taxonomy 定义；`classifier.source` 引用的 `task_all_workflows.csv` 无法定位（四仓均无，E1）。官方 55 子域完整名单来自论文 Figure 2 OCR（E1），但 6 个未覆盖子域中 5 个的**精确 ID 编号**为推断（E3）。
- **6 个未覆盖官方子域**（官方有定义、当前活动任务无，E1/E3）：1.4 Chemical & Process Engineering、1.7 Mining/Petroleum/Geological Engineering、10.1 Aviation & Airspace Operations（ID 经 `classifier.previous` 确认，E1）、10.2 Maritime & Port Operations、11.1 Educational Technology、12.2 Precision Agriculture。
- **2 个空 ID 号**（编号跳号，非子域）：1.9（engineering）、8.3（visual_media）。这些编号在官方 Taxonomy 中预留但无对应子域（E3）。
- **退役任务无 taxonomy 元数据**：30 条退役任务只有 task_id（来自 v1.1-task-review.md），没有 task_card.json 或 taxonomy 字段（已从 HEAD 移除，存于 v1 tag 与 ale-data/archive/），无法按官方域归类（E1）。
- **`other` 的历史子域为空**：mota_exploration 的 `classifier.previous.subdomain` 为 None，说明"other"曾无子域体系，14.1 sports 是后补（E3）。

## 3. 授权与内容约束

- **受限 reference / 隐藏评分 / 敏感资产**：本轮只检查访问限制与元数据（目录、文件名、大小、字段存在性），**不读取、不复制**受限内容到研究成果，也不用于新任务生成。`evidence/task_archetype_rows.tsv` 只保留输入/输出文件名、软件清单、字段存在性/类型，不含任务正文与评分内容。
- **评分内容清理（修订 3）**：`eval_hardGates` 字段已改为只记录存在性（`eval_hardGates_present`）与 JSON 类型（`eval_hardGates_type`），不保留评分规则正文。已核查生成脚本（`scripts/02_archetype_extract.py`）防止再次导出。
- **不修改**：Phase 0 文件、四份官方输入、总方案 v0.4 均只读。本轮所有写入仅限当前研究目录。
- **不裁决**：computing_math 的 A/B 候选口径（见下）本轮不裁决。
- **不执行**：不批准配额、不计算招聘人数、不开发平台、不专家联系/招募、不运行评测、不下载大资产。

## 4. 待研究问题（下一轮 S1-02 或后续）

1. **computing_math A/B 裁决**（本轮不裁决，三态已机器可读记录于 CATEGORY_MAPPING.csv）：A = 整类排除（目录 19 或 taxonomy 18）；B = 按子域排除 6 个 CS 子域（software_eng / data_analytics / ai_cs_research / cybersecurity / infra_cloud / quantum，共 16 条 taxonomy 任务），**条件保留** math_ops_research（数学与运筹，2 条，`conditional_keep_non_cs_math_or`）。需注意 go_game_reconstruction_1 已被官方重分类到 other/sports（非 CS），A 口径下"整类"按目录还是 taxonomy 统计会差 1。
2. **quantum 归属**：量子计算横跨物理与 CS，B 口径下归 CS 还是物理专业工作未定（DISPUTE，E3）。
3. **`other/sports` 不自动获批**：other 是兜底桶，`catch_all_not_auto_approved`，不能作为非 CS 配额类别；新任务设计需尽早定 other 范围控制标准以防范围蔓延（E1）。
4. **agriculture_env 是否纳入 500 候选**：当前活动集合无农业/环境代表，但官方域存在且有 1 个环境任务（glm_lake），另有 2 个未覆盖官方子域（12.2 Precision Agriculture 属此域）。需产品侧决定是否补该域。
5. **非 CS 域中的 CS 型工作**：多域含重软件/CS 工作（engineering 的 EDA/CAD、life_sciences 的生物信息管线、physical_sciences 的计算化学、visual_media 的 GPU 3D）。这些是否影响"非 CS 专业工作"定位需后续界定（E3）。
6. **重分类依据缺失**：13 张卡 `rationale` 字段缺失，官方重分类动机无法核实；若需引用需向官方求证或查分类器 source（E1/U）。
7. **6 个未覆盖子域精确 ID**：5 个（1.4/1.7/10.2/11.1/12.2）的 ID 为编号顺序推断，需官方确认（E3→E1）。
