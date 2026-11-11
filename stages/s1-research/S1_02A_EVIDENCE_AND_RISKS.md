# S1-02A 证据与风险（EVIDENCE AND RISKS）

本文件记录第一批三簇（Engineering & Architecture、Agriculture & Environment、Legal，共 14 子域）候选完整工作流的来源证据、跨领域重叠、任务粒度、平台依赖与阻断风险，以及待专家确认事项。**S1-01 与 Phase 0 尚未正式验收通过**，本文件不构成对二者的验收背书。

## 0. 证据等级与来源类型（本轮口径）

S1-02A 在 S1-01 的 `E1`/`E2`/`E3`/`U` 基础上扩展：

| 等级 | 含义 | 数量 |
|---|---|---|
| `E1` | 本轮直接观察：抓取并阅读了完整原文 | 14 |
| `E2` | 引自 S1-01 / Phase 0 R1（待复审） | 0 |
| `E3` | 行业公开资料：有可追溯 URL | 32 |
| `E4` | 项目推断：LLM 生成的专业判断，必须专家确认 | 5 |
| `U` | 未知 | 0 |

来源类型（`source_type`）：

| 类型 | 含义 | 数量 |
|---|---|---|
| `industry_supported` | 行业公开资料支持的专业工作流程 | 46 |
| `project_proposal` | 本项目新任务研究建议（待专家确认） | 5 |
| `official_task_example` | 官方任务示例（不得复制为交付数据） | 0 |

**E3 的验证深度不一致**：多数 E3 来源本轮只见到搜索摘要或摘要页（ScienceDirect、ACM、IEEE 等付费墙，或抓取失败返回 403），未全文阅读。**E3 不等于全文核实**；凡仅见摘要的，其专业操作细节仍需专家确认。每条候选的 `pending_confirmation` 字段记录了具体验证深度与待确认内容，是本文件的权威逐条记录。

## 1. 跨领域重叠与任务粒度检查（用户要求 5）

### 1.1 真实跨簇重复（需裁决归属，否则双计）

1. **civil_geo 水利建模 ≈ env_water 水利建模**。`eng_civilgeo_wf02`（HEC-RAS 洪泛区水力）与 `ag_envwater_wf03`（HEC-RAS 洪泛区）同工具同工作流；`eng_civilgeo_wf03`（EPANET 配水管网）与 `ag_envwater_wf04`（EPANET 配水管网）同工具同工作流。二者分属两个正式簇。需裁决：以"土木基础设施设计"还是"水资源管理"为归属依据，或将二者合并为一条跨域候选。
2. **electronics DFT ≈ semiconductor DFT**。`eng_electronics_wf02`（扫描链插入 + ATPG 故障覆盖率）与 `eng_semiconductor_wf03`（DFT 扫描 + ATPG）同工作流，区别仅在上下文（板级/PCB 级 vs IC 级）。需裁决拆分还是合并。

### 1.2 方法同构、上下文不同（可保留，需标注区分）

3. aerospace_mech 结构 FEA ↔ civil_geo 结构 FEA（同方法，材料/载荷/规范不同）。
4. manufacturing 公差/Cp-Cpk ↔ aerospace_mech 公差叠加（生产侧 `eng_manufacturing_wf03` vs 设计阶段 `eng_aerospace_wf03`）。

### 1.3 簇间邻接（分类边界需注意，非重复）

5. **Legal 簇 ↔ business_finance/compliance 重度邻接**：litigation 的 e-discovery/TAR/特权审查、legal_research 的法条解释/citator 均标注此邻接。官方成员曾跨此边界重分类：litigation 的活动成员从 business_finance 进入，legal_research 的成员移出到 business_finance/compliance。本簇与 business_finance/compliance 的任务划分需专家裁定。
6. precision_agriculture 影像/NDVI/分区 ↔ visual_media（影像）与 env_water（土壤水/养分）。
7. env_water ↔ physical_sciences/earth_atmo（流域/气候科学）；mining_petroleum 边坡稳定 ↔ civil 岩土；urban_planning ↔ transport_safety（消防/航空/海事）与 transit。
8. robotics 强化学习 ↔ computing_math（ML 训练）。

### 1.4 粒度结论

51 条候选均通过 `granularity_check`：每条是"输入 → 专业操作 → 预期产物 → 成功标准"的完整工作流，非单一操作、非仅参数替换的同质任务。软件名称未作为任何子领域的唯一业务边界（如 electronics 边界为"电子设计/验证服务"而非"KiCad/LTspice 工具操作"；civil_geo 明确排除"仅 CAD/BIM 出图"这一已属官方的任务）。

## 2. 平台依赖与阻断风险

### 2.1 Windows-only 专有工具（阻断 Linux 自动化）

- HEC-RAS / HEC-HMS（`eng_civilgeo_wf02`、`ag_envwater_wf03`）
- ETABS / SAP2000（`eng_civilgeo_wf04`）
- Altium Designer（`eng_electronics_wf01`）
- Minitab（`eng_manufacturing_wf02`）
- 计量 GOM / PolyWorks（`eng_manufacturing_wf01`）

### 2.2 专有 EDA / 行业许可证

- Synopsys TestMAX / Design Compiler / PrimeTime / TetraMAX（electronics + semiconductor 的 DFT/综合/签核）
- Aspen Plus / HYSYS（chemical_process）
- Whittle / NPV Scheduler + Slide / Rocscience（mining）
- KAPPA / FracPro / MFrac（petroleum）
- Relativity / Everlaw / Lighthouse + Westlaw / LexisNexis / Shepard's / KeyCite（legal）

### 2.3 其它

- **GPU**：`eng_robotics_wf01`（RL 训练，CUDA 强要求）。
- APSIM 需注册 + DSSAT Windows 中心（`ag_precision_wf04`）；专有控制器格式（`ag_precision_wf03`）。
- **机密/特权数据访问**：litigation e-discovery/TAR（特权/保密文档）、mining 块模型、petroleum 井数据、建筑计量数据。

每条候选的可替代开源路径已记录于 `platform_dependencies` / `verification_approach`（如 OpenSTA/Magic 替代 PrimeTime、Yosys 替代 Design Compiler、EPANET/wnTR 替代专有 GUI、DWSIM 替代 Aspen、RBTS 标准馈线替代真实电网数据）。但开源等价路径对 EDA/计量/法律数据库类候选是"近似"而非"等价"，工程验证需降级到公开 PDK / 合成数据 / 公开判例。

## 3. 未覆盖官方子域的来源限制

本批 3 个 `uncovered_official` 子域（`chemical_process`、`mining_petroleum`、`precision_agriculture`）的**子域边界本身**只有 E3/E4 来源，无 E1 直接观察（官方活动任务为零）。其边界与职业划分（如 mining_petroleum 是否涵盖完井/压裂、precision_agriculture 是否涵盖 NDVI 侦察、chemical_process 是否涵盖 HAZOP/P&ID）为行业资料推断，需专家确认。

## 4. 待专家确认事项

### 4.1 五条 E4 候选（LLM 推断，不得作为行业事实）

| candidate_id | 内容 | 依据 |
|---|---|---|
| eng_aerospace_wf03 | GD&T 公差叠加设计验证 | 无来源，推断 |
| eng_chemproc_wf03 | 由工艺描述生成 PFD/P&ID | 无来源，推断 |
| eng_energypower_wf03 | 建筑 M&V 至 ASHRAE Guideline 14 | 无来源，推断 |
| eng_semiconductor_wf03 | DFT 扫描/ATPG | 无来源，推断 |
| eng_urban_wf03 | 四阶段出行需求模型 | 无来源，推断 |

### 4.2 其它待确认

- E3 摘要级来源的全文核实（见各候选 `pending_confirmation`）。
- 两条真实跨簇重复（1.1）的归属裁决。
- Legal 簇与 business_finance/compliance 的边界（1.3 第 5 条）。
- 3 个未覆盖子域边界本身的专家确认（第 3 节）。

## 5. 授权与内容约束

- 不修改 Phase 0、R1、四份官方输入、总方案 v0.4（全部只读）。
- 不复制官方任务形成交付数据（`source_type=official_task_example` 数量为 0）。
- 不将 LLM 推断标记为行业事实（5 条 E4 均标注 `project_proposal` + 待专家确认）。
- 本轮不批准 500 配额、不计算招聘人数、不招募、不启动平台开发或工程转换。
- 专家应提供的原始资料与使用权限已记录于每条候选的 `expert_raw_materials` / `usage_permissions`；本文件只列出专家需提供的数据类型与授权条件，不索取、不读取任何受限或机密数据。
