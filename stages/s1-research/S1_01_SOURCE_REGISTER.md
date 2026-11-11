# S1-01 来源登记（SOURCE REGISTER）

本文件登记本轮研究引用的全部来源、版本与证据状态（独立复审后修订版）。S1-01 是"官方证据与类别映射基线研究"，只做来源确认、集合口径统一、类别映射与任务原型证据索引，不批准配额、不招募专家、不开发平台、不运行评测。

证据等级约定：

- `E1` 本轮直接观察（本人打开文件/字段读到）
- `E2` 引自 Phase 0 R1（R1 状态 = "修订完成，待复审"，故带"待复审"标记）
- `E3` 本轮推断（需要后续确认）
- `U` 未知/未核实

复审状态约定：R1 尚未最终验收，所有 E2 结论一律标记"待复审"。E1 结论由本轮直接观察支持，但映射解释仍属基线，等待独立审查。

## 1. 只读输入来源

| 来源 ID | 路径 | 版本 | 性质 | 证据状态 |
|---|---|---|---|---|
| S1 | `/Users/mac/Workspaces/ale-研究设计/agents-last-exam/` | git `2e91edd`（2026-10-27）；tag `v1` = `d9abc07` | 官方基准仓（旧格式）。`tasks/*/task_card.json` 的 `taxonomy` 字段为观察口径；`tasks/published_tasks.json`（122 键）与 `selected_tasks/*.txt` 为活动/名单口径；`docs/releases/v1.md`、`v1.1.md`、`v1.1-task-review.md` 为版本与退役口径；`README.md`（"55 subdomains across 13 industry clusters"）为官方总数口径 | E1 |
| S2 | `/Users/mac/Workspaces/ale-研究设计/ale/` | git `73517c2`（2026-11-06） | 新引擎仓（TaskSpec schema 等） | E1（仅 schema 检查） |
| S3 | `/Users/mac/Workspaces/ale-研究设计/ale-data/` | 无 git（目录） | 任务数据资产（`archive/`、`task-data-v1.1/`）。本轮只读元数据与目录结构，不读取受限 reference/隐藏评分内容 | E1（仅结构/元数据） |
| S4 | `/Users/mac/Workspaces/ale-研究设计/ale-tasks-base/` | git `492249a`（2026-11-03） | 新格式任务基（11 个 `task.toml`） | E1（仅结构检查） |
| S5 | `/Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108/analysis/phase0-official-baseline-r1/` | R1 目录 | Phase 0 R1 成果（04/05/08 CSV、set_diff_report.md、validate_r1.py 等） | E2（待复审） |
| S6 | 论文 arXiv:2606.05405（v4，2026-10-25，"Agents' Last Exam"） | 公开论文 | 官方 Taxonomy 完整名单权威来源：Figure 2（55 子域分布 SVG，`panel_c_subdomain.svg`，OCR 提取）；§B.1.1 "Taxonomy Definition"（51 SOC 锚定 + 4 frontier = 55 子域方法论） | E1（OCR 读取，见下） |
| S7 | 官网 agents-last-exam.org | 公开网页 | "55 targeted sub-industries"、"1,500+ tasks collected" | E1 |

## 2. 官方 Taxonomy 的权威来源判定（两层口径）

官方 Taxonomy 有**两层口径**，不可混用：

- **完整官方分类（Layer 1，权威）**：13 个命名行业簇 + "Other" 兜底桶，共 **55 官方子域**。权威来源为论文 Figure 2（S6，OCR 提取后写入 `evidence/official_taxonomy_55.tsv`），与 S1 README（"55 subdomains across 13 industry clusters"）、S7 官网（"55 targeted sub-industries"）一致。
- **活动任务观察分类（Layer 2，样本）**：135 张 task_card.json 的 `taxonomy` 字段观察到 14 域 / 49 子域（含 other/sports）。**不能**用此样本替代完整分类。

task_card.json 的 `taxonomy` 字段结构：`domain_id` / `domain_code` / `subdomain_id` / `subdomain_code` / `subdomain_name`，以及 `classifier`（含 `source`、`applied_at`、`previous` 重分类历史、`model`、`classified_at`、`rationale`——但 13 张跨域重分类卡**无 `rationale` 字段**）。

搜索确认：仓库中**不存在** `task_all_workflows.csv` 或独立的 Taxonomy 定义文档（S1/S2/S3/S4 内均无）。`classifier.source` 中出现的 `task_all_workflows.csv` 引用无法定位到实际文件，属**未确认事项**（U）。

55 官方子域 vs 49 观察子域：差 **6 个未覆盖子域**（1.4/1.7/10.1/10.2/11.1/12.2）。另有 2 个空 ID 号（1.9、8.3，编号跳号，非子域）。详见 GAPS 第 2 节。

## 3. 集合口径来源对照

| 对象 | 值 | 来源 | 证据状态 |
|---|---|---|---|
| 活动任务（v1.1） | 122 | `tasks/published_tasks.json`（122 键）== `selected_tasks/full.txt`（去注释 122）== `selected_tasks/full/overall.txt`（122） | E1 |
| v1 历史任务 | **152**（非 153） | v1 tag `selected_tasks/full.txt` = 153 行 = 152 任务 + 1 注释行（首行 `# All tasks from`） | E1 |
| 物理 task_card.json（HEAD） | 135 | `tasks/*/task_card.json` 遍历 | E1 |
| 物理 task_card.json（v1 tag） | 165 | v1 tag 遍历 = 152 选中 + 13 额外 | E1 |
| 额外卡（未发布） | 13 | 135 − 122（8 demo + 4 visual_media + 1 engineering） | E1 |
| 退役任务 | 30 | `docs/releases/v1.1-task-review.md`（行 69 起） | E1 |
| 难度名单 | near-term 45 / full-spectrum 46 / last-exam 36 | `selected_tasks/full/*.txt` | E1 |
| CPU / GPU | cpu.txt 119 / gpu.txt 3（并集 122） | `selected_tasks/{cpu,gpu}.txt` | E1 |
| 官方 Taxonomy 顶层（完整） | 13 命名簇 + Other 兜底 | 论文 Figure 2（S6） | E1 |
| 官方 Taxonomy 子域（完整） | 55 | 论文 Figure 2（S6） | E1 |
| 官方 Taxonomy 子域（观察） | 49 | `task_card.json.taxonomy.subdomain_code` | E1 |
| 未覆盖官方子域 | 6 | 55 − 49 | E1/E3 |

说明：`agriculture_env` 目录仅含 `__init__.py`，无 task_card.json（其 2 个任务全退役），但其官方域存在，且有 1 个由 `physical_sciences/glm_lake_calibration` 重分类进入的活动任务。

## 4. 本轮生成的派生证据文件

| 文件 | 内容 | 生成脚本 |
|---|---|---|
| `evidence/taxonomy_domains.tsv` | 14 观察域（domain_id → domain_code） | `scripts/01_taxonomy_extract.py` |
| `evidence/taxonomy_subdomains.tsv` | 49 观察子域（含名称与编号） | 同上 |
| `evidence/taxonomy_card_rows.tsv` | 135 行逐卡 taxonomy（含 category 对照与 taxonomy_missing 标记） | 同上 |
| `evidence/official_taxonomy_55.tsv` | 55 官方子域完整名单（来自论文 Figure 2 OCR，含 official_domain_name / id_source / observed 标志） | 手工整理（OCR 结果） |
| `evidence/task_archetype_rows.tsv` | 135 行逐卡原型证据（软件/verifier/OS/VM/评估存在性与类型/输入输出文件名，仅元数据与结构，不含任务正文与评分内容） | `scripts/02_archetype_extract.py` |
| `S1_01_RECLASSIFICATION_EVIDENCE.csv` | 13 行逐任务跨域重分类证据（真实 task_id + task_card 路径 + previous 历史 + rationale 存在性） | `scripts/06_reclassification_evidence.py` |

校验脚本：`scripts/07_validate.py`（8 项检查：49 观察行 / 55 官方子域 / 6 未覆盖 / 122 活动任务 / 13 重分类 / 135 卡行 / eval_hardGates 无泄露 / 原型 49 行 122 示例）。修订记录见 `S1_01_REVISION_LOG.md`。

## 5. 版本/口径变更要点

- **v1 → v1.1**：v1 真实任务数 152（full.txt 153 行含 1 注释行）；v1.1 选 122 条 active、退役 30 条，**152 = 122 + 30 精确成立**（v1.1 == v1 − retired，无缺失）。57 条需重跑、65 条可保留；6 条开源工具转换（Blender / FreeCAD / FreeCAD CAM / Kratos / MuseScore / Ardour）。见 `docs/releases/v1.md`、`v1.1.md`。
- **目录（category）≠ 官方域（taxonomy.domain_code）**：存在 13 处跨域重分类（逐任务证据见 `S1_01_RECLASSIFICATION_EVIDENCE.csv`）。R1 的目录口径统计与官方 taxonomy 口径统计**不一致**（例如 health_medicine 目录 19 → taxonomy 17；social_sciences 目录 1 → taxonomy 4），不得混为一谈。
- **官方完整分类 ≠ 观察样本**：55 官方子域（完整）vs 49 观察子域（当前活动任务样本），差 6 个未覆盖子域。任务卡样本不能替代完整官方分类。
