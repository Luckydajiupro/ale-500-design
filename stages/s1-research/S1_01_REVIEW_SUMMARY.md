# S1-01 复审摘要（REVIEW SUMMARY）

目标：复用 Phase 0 R1，统一官方任务集合口径，以官方 Taxonomy 为外部映射基线建立类别映射与任务原型证据索引，为后续类别配额与专家招募筹备提供可追溯基线。本轮不裁决 computing_math A/B、不批配额、不招募、不开发。本文件为独立复审后修订版（变更详见 `S1_01_REVISION_LOG.md`）。

证据等级：`E1` 本轮直接观察，`E2` 引自 Phase 0 R1（待复审），`E3` 推断，`U` 未知。

## 1. 已确立事实（本轮）

Taxonomy 两层口径：

- **完整官方分类（Layer 1）**：13 个命名行业簇 + "Other" 兜底桶，共 **55 官方子域**。权威来源为论文 Figure 2（arXiv:2606.05405v4 `panel_c_subdomain.svg`，OCR 提取，E1），与 README（"55 subdomains across 13 industry clusters"）、官网（"55 targeted sub-industries"）一致。
- **活动任务观察分类（Layer 2）**：135 张 task_card.json 观察到 14 域 / **49 子域**（含 other/sports）。`other/sports`（14.1）在 Other 兜底桶内，不属 13 正式领域。
- **6 个未覆盖官方子域**（官方有、当前活动任务无）：1.4 Chemical & Process Engineering、1.7 Mining/Petroleum/Geological Engineering、10.1 Aviation & Airspace Operations、10.2 Maritime & Port Operations、11.1 Educational Technology、12.2 Precision Agriculture。其中 10.1 经 `classifier.previous` 确认（E1），其余 5 个 ID 按编号顺序推断（E3）。
- **2 个空 ID 号**（编号跳号，非子域）：1.9（engineering）、8.3（visual_media）。

集合口径：

- 活动任务 **122 条**：`published_tasks.json`（122 键）== `full.txt` == `full/overall.txt`（E1）。
- 物理 task_card.json **135 张** = 122 活动 + 13 额外（8 demo 无 taxonomy + 4 visual_media + 1 engineering）（E1）。
- 退役 30 条；难度 near-term 45 / full-spectrum 46 / last-exam 36；cpu 119 / gpu 3（并集 122）（E1）。
- **版本核对（修订 6，E1）**：v1 tag 的 `full.txt` = 153 行 = **152 任务 + 1 注释行**。v1 真实任务数 152 = 122 活动 + 30 退役（精确相等，无缺失）。审查所称"v1 历史 153 条"是原始行数（含注释行）的误读。

类别映射：

- 目录（category）与官方域（taxonomy.domain_code）存在 **13 处跨域重分类**（E1）。逐任务证据见 `S1_01_RECLASSIFICATION_EVIDENCE.csv`（真实 task_id + task_card 路径）。
- 13 处重分类的 `classifier` 均**无 `rationale` 字段**（字段缺失），重分类依据不可核实（U）。
- 官方域 `agriculture_env` 目录 0 任务（2 任务退役），仅 1 个重分类进入的活动任务（physical_sciences/glm_lake_calibration）（E1）。
- R1 运行性基线（E2，待复审）：非 CS 域 103 条 retained_for_500；86 Linux / 36 Windows；GPU 3 全 Windows；外部服务 13（staged-local 5、online-required 6、public-ref 2）；GUI 40 yes / 9 unknown / 73 no；Docker 例外 8。

## 2. 推断（E3，需后续确认）

- 目录结构是"历史遗留 + 提交时分类"，官方 taxonomy 是事后由分类器重标注，因此目录滞后于官方分类（尤其 social_sciences / agriculture_env / other）。
- `other` 的 14.1 sports 是后补子域（mota_exploration 历史 subdomain 为 None）。
- 非 CS 域中大量任务含重软件/CS 工作，未来"非 CS 专业工作"定位需按任务而非按域界定。
- 6 个未覆盖子域中 5 个的官方 ID（1.4/1.7/10.2/11.1/12.2）按编号顺序推断，名称来自论文 Figure 2 OCR，ID 映射需官方 `task_all_workflows.csv` 或 Figure 2 原图确认。

## 3. 未核实事项（U / 待确认）

- 5 个未覆盖子域（1.4/1.7/10.2/11.1/12.2）的**精确官方 ID**（名称已确认，编号为推断）。
- `classifier.source` 引用的 `task_all_workflows.csv` 实际位置与内容（四仓均无）。
- 30 条退役任务的官方域归属（无 task_card，无法归类）。
- 13 处跨域重分类的官方动机/依据（rationale 字段缺失）。
- R1 全部结论的最终验收状态（R1 待复审）。
- computing_math A/B 裁决（本轮不裁决）；quantum 的 CS/物理归属；agriculture_env 是否纳入 500 候选；`other` 的范围控制标准。

## 4. 交付物与列定义

| 交付物 | 说明 |
|---|---|
| `S1_01_SOURCE_REGISTER.md` | 来源、版本、证据状态 |
| `S1_01_CATEGORY_MAPPING.csv` | 55 行两层映射（49 观察 + 6 未覆盖），列定义见下 |
| `S1_01_TASK_ARCHETYPE_EVIDENCE.csv` | 49 行（观察子域原型），列定义见下 |
| `S1_01_RECLASSIFICATION_EVIDENCE.csv` | 13 行（逐任务跨域重分类证据），列定义见下 |
| `S1_01_GAPS_AND_RISKS.md` | 分类冲突、资料缺口、授权约束、待研究问题 |
| `S1_01_REVISION_LOG.md` | 独立复审后 6 项修订记录 + 校验结果 |
| `S1_01_REVIEW_SUMMARY.md` | 本文件 |

### `S1_01_CATEGORY_MAPPING.csv` 列定义（19 列）

`domain_id` 官方域编号；`domain_code` 官方域代码（task_card 口径）；`official_domain_name` 官方域完整名（论文 Figure 2）；`subdomain_id` 官方子域编号；`subdomain_code` 官方子域代码；`subdomain_name` 官方子域名称；`id_source` 子域 ID 来源（`taskcard` 直接确认 / `prev` 重分类历史确认 / `inferred` 推断）；`coverage_status` 覆盖状态（`active_observed` 活动观察 / `uncovered_official` 官方有但无活动任务）；`active_taxonomy_count` 该子域活动任务数（taxonomy 口径，未覆盖=0）；`domain_dir_count` 该域目录口径活动任务数；`domain_tax_count` 该域 taxonomy 口径活动任务数；`reclassified_in` 重分类进入该子域的任务（`目录→域/子域`）；`reclassified_out` 重分类离开该域的任务；`mapping_dispute` 映射争议说明；`ab_A_status` A 方案状态（仅 computing_math 填，`excluded`）；`ab_B_status` B 方案状态（`excluded_cs_subdomain` / `conditional_keep_non_cs_math_or` / `dispute_unresolved`）；`ab_dispute` 争议状态（仅 quantum 填）；`exclusion_status` 排除状态（`candidate_non_cs` / `excluded_awaiting_AB` / `catch_all_not_auto_approved`）；`evidence_location` 证据路径。

### `S1_01_TASK_ARCHETYPE_EVIDENCE.csv` 列定义（15 列）

`domain_code` / `subdomain_code` / `subdomain_name` 官方分类；`example_task_ids` 该子域活动任务 id（分号分隔）；`professional_workflow` 专业工作流原型（手写摘要，**研究假设**）；`raw_input_type` 原始输入类型；`expected_deliverable` 预期交付产物；`verifier_impl_class` verifier 实现类（R1 verifier_type 计数，如 `scorer=3`，E2 待复审）；`verification_method` 实际验证方法（由实现类推断，**研究假设**，未独立确认）；`software_environment` 软件清单（分号分隔）；`runtime_environment` 运行环境（vm 机型、Linux/Windows 计数、外部服务）；`expertise_clues` 领域专家能力线索（手写摘要，**研究假设**）；`research_hypothesis_fields` 标为研究假设的字段清单（`professional_workflow;expertise_clues;verification_method`）；`evidence_location` 证据路径；`unconfirmed_items` 未确认事项。

### `S1_01_RECLASSIFICATION_EVIDENCE.csv` 列定义（16 列）

`task_id` 真实任务 id；`old_directory` 旧目录（category）；`current_domain_id` / `current_domain_code` / `current_subdomain_id` / `current_subdomain_code` / `current_subdomain_name` 当前官方 taxonomy；`previous_domain_id` / `previous_domain_code` / `previous_subdomain_id` / `previous_subdomain_code` / `previous_subdomain_name` 重分类前 taxonomy；`reclassification_source` 重分类来源（task_all_workflows.csv）；`applied_at` 应用时间；`rationale_present` 是否含 rationale 字段（13 行全 `no`，字段缺失）；`task_card_path` 真实 task_card.json 路径。

## 5. 下一轮建议

1. 独立审查本轮修订，重点复核：两层映射口径（55 官方 / 49 观察 / 6 未覆盖）、13 处重分类逐任务证据、A/B 三态、证据等级标注。
2. 向官方求证 5 个未覆盖子域的精确 ID（或取得 `task_all_workflows.csv` / Figure 2 原图），将 E3 推断升级为 E1。
3. 就 computing_math A/B、quantum 归属、agriculture_env 纳入与否、`other` 范围控制做产品侧裁决，再进入 S1-02。
4. S1-02 若继续，基于 `S1_01_TASK_ARCHETYPE_EVIDENCE.csv` 的子域原型逐域讨论"新任务类型"设计空间，而不复制官方任务。

（本轮修订到此停止，等待独立审查后再进入 S1-02。）
