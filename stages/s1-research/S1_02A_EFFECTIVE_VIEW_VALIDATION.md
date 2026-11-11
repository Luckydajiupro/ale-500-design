# S1-02A 有效研究视图校验（S1_02A_EFFECTIVE_VIEW_VALIDATION.md）

本文件是本轮（最终纠偏与有效研究视图整合）的校验证据，配合
`S1_02A_EFFECTIVE_CANDIDATES.csv` 一起交付。它不覆盖任何既有原始记录。

证据等级沿用既有约定：E1=本轮直接读取全文、E2=引自S1-01/R1待复审、
E3=行业公开资料（可追溯URL）、E4=项目推断（须专家确认）、U=未知。
凡未经实际运行的结论一律标 `NOT_VERIFIED`。

---

## 一、HEC-RAS 环境纠偏（任务一）

### 结论

| 版本线 | 官方 GUI | 官方原生 Linux | 生产适用性 |
|---|---|---|---|
| HEC-RAS 6.x / 7.0.x（经典线） | Windows GUI（是） | 无 | 7.0.1 为当前稳定版（替代 6.6）；7.0.2 为补丁发布说明 |
| HEC-RAS 2025（"RAS 2025"，重写线） | Windows 新地图界面（是） | 有（原生 Linux + 容器化 + 无头 CLI） | 公开 Beta（2026-04），**不可用于生产**；1D 水力学/桥梁/闸门尚未实现（2026/2027 路线图） |

### 逐项答复

- **Windows GUI 支持**：经典线（6.x/7.0.x）官方仅 Windows（Intel PC）GUI +
  64 位计算引擎。RAS 2025 Beta 提供新的地图式 Windows 界面。
- **Linux 计算引擎是否存在、支持哪些功能**：经典线无官方原生 Linux，仅第三方
  容器运行 2D 非恒定流计算引擎（无 GUI）——Docker
  `rascommander/hec-ras-linux-unsteady_6.6`、Apptainer/Slurm。RAS 2025 Beta
  声明原生 Linux + 云容器 + 无头命令行（E3，第三方转述 USACE 声明），但只覆盖
  2D，1D/桥梁/闸门缺位。
- **不同版本的正式生产适用性**：HEC-RAS 7.0.1 生产可用；RAS 2025 为 Beta，
  USACE 明确不建议用于生产工程研究。
- **腾讯云 Linux 服务器实际运行状态**：`NOT_VERIFIED`——本轮未在任何腾讯云
  Linux 实例上实际运行任何候选工作流，无运行证据。

### 证据等级

本纠偏所依据的页面（USACE 官方 `hec.usace.army.mil` 的 7.0.2 发布说明、
2025 下载页）在本轮环境**未能直接抓取**（`fetch failed`）。因此：

- HEC-RAS 2025 原生 Linux 声明 = **E3**（第三方行业资料转述，可追溯 URL）：
  [CivInnovate HEC-RAS 2025 指南](https://civinnovate.com/2026/06/17/hec-ras-2025-complete-guide/)、
  [Geocorsi RAS 2025 Beta 通报](https://www.geocorsi.it/N1763/ras-2025-entra-in-fase-beta-il-nuovo-hec-ras-per-la-modellazione-idraulica.html)、
  [Hydro-Resource-Hub 安装说明](https://raw.githubusercontent.com/Apurv-Bharadiya/Hydro-Resource-Hub/main/hydraulic_models/hec_ras_master_guide/02_installation_setup.md)。
- 官方系统要求（经典线 Windows-only）= **E3**（第三方转载官方手册要求）。
- 腾讯云 Linux 实际运行状态 = **NOT_VERIFIED**（无运行）。

**纠偏结果**：既有 `SOFTWARE_ENV_CORRECTIONS` 中"HEC-RAS 无官方原生 Linux"
的表述仅对经典线成立；对 HEC-RAS 2025 线不成立。有效视图已采用区分两条
版本线的精确表述，且未把"存在 Linux 计算引擎"标为"已验证可运行"。

---

## 二、有效研究视图（任务二）

### 设计

以 `candidate_id` 为唯一标识，把三层数据合并为一条下游唯一有效行：

| 输入文件 | 提供字段 |
|---|---|
| `S1_02A_WORKFLOW_CANDIDATES.csv` | 最终工作流描述（标题/摘要/输入/专业操作/产物/成功标准） |
| `S1_02A_SOURCE_CLAIM_MAP.csv` | 证据类型/证据等级/来源类型/来源类别/主要来源URL/具体主张/软件适配 |
| `S1_02A_DUPLICATE_ATTRIBUTION.csv` | 主类别/次级标签/重复归属结果 |

### 输出字段（23 列）

`candidate_id, subdomain_code, workflow_title, workflow_summary, task_input,
professional_operations, expected_deliverable, success_criteria,
evidence_kind, evidence_level, source_type, source_category,
primary_source_url, primary_claim, primary_home, secondary_tag,
duplicate_status, software_adaptation, linux_verification_state,
expert_pending, engineering_pending, original_record_path,
revision_evidence_path`

### 字段冲突规则

只有存在明确修订证据时才覆盖原值（如本轮 E3/E4→E1 升级均带 "E1 UPGRADED"
及全文读取记录）；否则标记 `CONFLICT`，不猜测。**本轮冲突数 = 0**。

### 关键计数

- 有效行 51，唯一 `candidate_id` 51，无丢失、无重复。
- `duplicate_status`：primary=3、secondary=3、none=45。
- `evidence_kind`：industry_standard_complete=34、tool_existence=11、
  agent_inferred_combination=2、expert_pending_proposal=4。
- `evidence_level`：E1=24、E3=23、E4=4（E2=0、U=0）。
- `software_adaptation`：native=30、partial_function_replacement=15、
  conditional=4、unverified_or_unavailable=2、needs_task_redesign=0。
- `linux_verification_state`：**51 全部 = NOT_VERIFIED**。
- `expert_pending` 有标记 = 9（4 条 E4 假设 + 6 条重复归属边界待确认，其中
  `eng_semiconductor_wf03` 二者重叠，E4 标记优先）。
- `engineering_pending` 有标记 = 21（15 partial + 4 conditional + 2 unverified）。

---

## 三、有效视图校验（任务三）

校验脚本 `scripts/14_validate_effective_view.py` 对真实文件执行 7 项检查，
并对 7 类关键错误执行负例自测（在内存中篡改副本，断言对应检查转为 FAIL）。

### 7 项检查（全部 PASS）

| 检查 | 结果 | 详情 |
|---|---|---|
| C1 有效视图为 51 条唯一 candidate_id | PASS | ids=51 unique=51 |
| C2 三组已记录重复均有明确归属 | PASS | primary=3 secondary=3 pairs=3 |
| C3 不存在因合并而丢失的候选 | PASS | missing=[] extra=[] |
| C4 证据等级与来源类型不混淆 | PASS | 无 E4+industry_supported、无 E1+project_proposal |
| C5 native 不被解释为已验证 Linux 运行 | PASS | 非 NOT_VERIFIED = [] |
| C6 E4 与部分功能等价风险未遗漏 | PASS | E4=4 且均有 expert_pending；partial/unverified 均有 engineering_pending |
| C7 下游可识别唯一有效视图 | PASS | 51 行、以 candidate_id 为键、一行一 ID |

### 负例自测（全部 PASS，即全部被检测）

| 注入错误 | 触发的检查 |
|---|---|
| 复制一条 candidate_id | C1 |
| 删除一条候选 | C3 |
| native 行标为 VERIFIED | C5 |
| E4 行改 source_type=industry_supported | C4 |
| E4 行清空 expert_pending | C6 |
| partial 行清空 engineering_pending | C6 |
| 撤销一组重复归属 | C2 |

---

## 四、逐项结论

| 项目 | 结论 |
|---|---|
| 任务一 HEC-RAS 环境纠偏 | **PASS**（两条版本线区分；NOT_VERIFIED 保留） |
| 任务二 有效研究视图 | **PASS**（51 条唯一、冲突 0、可追溯路径） |
| 任务三 有效视图校验 | **PASS**（7 项 + 7 负例全部通过） |

## 五、剩余问题（留待评审）

- **HEC-RAS 2025 原生 Linux 声明为 E3**：官方 `hec.usace.army.mil` 页面本轮
  无法抓取，需以官方页面复核后升级为 E1。
- **腾讯云 Linux 实际运行 = NOT_VERIFIED**：任何候选工作流均未在该环境实跑，
  属于工程验证待办，不在本轮范围。
- **重复归属边界仍待专家确认**：三组重复的主/次归属是研究建议，专家需确认
  "civil 基础设施 vs 水资源管理"、"设计 vs 运营"、"IC 级 vs 板级" 三条边界。
- **E4 四假设仍待专家确认**：eng_aerospace_wf03（GD&T）、eng_energypower_wf03
  （M&V ASHRAE G14）、eng_semiconductor_wf03（DFT/ATPG）、eng_urban_wf03
  （四阶段需求模型）。
- **21 条工程验证待办**：open-source 功能等价与 Linux 运行路径未实跑验证。

本轮不进入 S1-02B，不宣布任何配额批准。
