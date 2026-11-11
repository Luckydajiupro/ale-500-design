# S1-02A 复审摘要（REVIEW SUMMARY）

目标：复用 S1-01 的完整 Taxonomy 映射，建立 12 个正式非 computing_math 行业簇、47 个候选子领域的覆盖骨架（computing_math 保留 A/B 两套口径，other 单独待归属），并对第一批三簇（Engineering & Architecture、Agriculture & Environment、Legal，共 14 子域）深入产出候选完整工作流。本轮不批准 500 配额、不计算招聘人数、不招募、不启动平台开发或工程转换。完成后停止，等待独立评审。

证据等级：`E1` 本轮直接观察，`E2` 引自 S1-01/R1（待复审），`E3` 行业公开资料，`E4` 项目推断（待专家确认），`U` 未知。

## 1. 已确立事实（本轮）

**覆盖骨架**：

- `S1_02A_SCOPE_MATRIX.csv` 共 55 行 = 47 正式非 CS 子域 + 7 computing_math（A/B 两套口径保留）+ 1 other（sports，单独待归属）。
- computing_math 的 A/B 口径与 quantum 争议状态原样保留自 S1-01，本轮不裁决。
- 第一批 `batch_1` = 14 子域：engineering 10（aerospace_mech、electronics、civil_geo、chemical_process、manufacturing、energy_power、mining_petroleum、semiconductor、urban_planning、robotics）+ agriculture_env 2（env_water、precision_agriculture）+ legal 2（litigation、legal_research）。

**候选工作流**：

- `S1_02A_WORKFLOW_CANDIDATES.csv` 共 51 行、23 列，覆盖全部 14 个 batch_1 子域（无缺失边界）。
- 每子域候选数：engineering 各 3–5（energy_power 4、mining_petroleum 5、civil_geo 4，其余 3）；agriculture_env 中 env_water 4、precision_agriculture 5；legal 各 4。合计 51。

**来源与证据**：

- `source_type`：industry_supported 46、project_proposal 5、official_task_example 0（未复制任何官方任务）。
- `evidence_level`：E1 14、E3 32、E4 5、E2 0、U 0。
- 5 条 E4 全部为 project_proposal（待专家确认），未将 LLM 推断标记为行业事实。

## 2. 关键发现

- 发现 **2 处真实跨簇重复**：civil_geo 水利建模 ≈ env_water 水利建模（HEC-RAS 洪泛区 + EPANET 配水各一对）；electronics DFT ≈ semiconductor DFT（扫描 + ATPG）。均需裁决归属以防双计。
- **Legal 簇与 business_finance/compliance 重度邻接**，官方成员曾跨边界重分类，任务划分需专家裁定。
- 3 个未覆盖官方子域（chemical_process、mining_petroleum、precision_agriculture）边界仅 E3/E4，无 E1。
- Windows-only 专有工具与专有 EDA/行业许可证是主要工程阻断点；开源等价路径已在逐条记录。
- 51 条候选均通过粒度检查：完整工作流，非单一操作或参数替换同质任务；软件名称未作为唯一业务边界。

## 3. 未核实事项（待确认）

- 5 条 E4 候选的专家确认（eng_aerospace_wf03、eng_chemproc_wf03、eng_energypower_wf03、eng_semiconductor_wf03、eng_urban_wf03）。
- E3 摘要级来源的全文核实（逐条见 `S1_02A_WORKFLOW_CANDIDATES.csv` 的 `pending_confirmation`）。
- 2 处真实跨簇重复的归属裁决。
- Legal ↔ business_finance/compliance 边界。
- 3 个未覆盖子域边界的专家确认。

## 4. 交付物与列定义

| 交付物 | 说明 |
|---|---|
| `S1_02A_SCOPE_MATRIX.csv` | 55 行覆盖骨架（47+7+1），列：cohort / cluster_code / cluster_name / subdomain_id / subdomain_code / subdomain_name / coverage_status / active_taxonomy_count / official_example_task_ids / s1_02a_batch / candidate_workflow_count / ab_A_status / ab_B_status / ab_dispute / notes |
| `S1_02A_WORKFLOW_CANDIDATES.csv` | 51 行候选，23 列（见 4.1） |
| `S1_02A_EVIDENCE_AND_RISKS.md` | 来源证据、跨域重叠、粒度、平台依赖、阻断风险、待确认 |
| `S1_02A_REVIEW_SUMMARY.md` | 本文件 |

### 4.1 `S1_02A_WORKFLOW_CANDIDATES.csv` 列定义（23 列）

`subdomain_code` 子域代码；`subdomain_business_boundary` 子域真实职业与专业业务边界；`subdomain_occupations` 子域职业；`candidate_id` 候选编号（按子域前缀约定）；`workflow_title` 工作流标题；`occupation_scope` 职业范围；`workflow_summary` 工作流概述；`source_type` 来源类型（industry_supported / project_proposal）；`evidence_level` 证据等级（E1/E3/E4）；`source_reference` 可追溯来源 URL；`expert_raw_materials` 专家应提供的原始资料；`usage_permissions` 使用权限；`task_input` 任务输入；`professional_operations` 专业操作；`expected_deliverable` 预期产物；`success_criteria` 成功标准；`verification_approach` 工程验证思路；`platform_dependencies` Linux/Windows/GPU/专有软件依赖；`blocking_risks` 阻断风险；`expert_capability` 对应专家专业能力要求；`cross_domain_overlap` 跨领域重叠；`granularity_check` 任务粒度检查；`pending_confirmation` 待专家确认事项。

### 4.2 校验

`scripts/10_validate.py` 全部 13 项 PASS：55 行骨架、47+7+1 构成、14 batch_1、51 候选、无缺失边界、0 官方任务复制、来源/证据等级合规、5 E4 全部 project_proposal、candidate_workflow_count 回填一致、candidate_id 唯一且前缀合规、必填字段非空、23 列。

## 5. 下一步

本批验证了"复用 S1-01 映射 + 分批深入 + 证据纪律 + 跨域去重"的方法可行性。**本轮到此停止**，等待独立评审，再决定是否按同样方法扩展至其余 9 个正式非 CS 簇。评审应重点裁决：2 处真实跨簇重复的归属、Legal 边界、5 条 E4 候选是否进入下一阶段。
