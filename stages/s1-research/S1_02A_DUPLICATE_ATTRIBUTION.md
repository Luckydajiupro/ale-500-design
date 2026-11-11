# S1-02A 跨领域重复归属裁定（独立评审定向修订）

本文件是对 S1-02A 第一轮 51 个候选工作流中 3 组跨领域重复对的裁定记录。
裁定原则（评审要求）：**不删除任何一个覆盖方向**，只记录唯一主归属、次级标签、差异依据与待确认项。

证据等级沿用 S1-01 约定：E1=本轮直接观察（全文已读）、E2=引自 S1-01/R1（待复审）、E3=行业公开资料（可追溯 URL）、E4=项目推断（须专家确认）、U=未知。

---

## 裁定 1：HEC-RAS 河道洪水模型（civil_geo vs env_water）

| 项 | 内容 |
|---|---|
| 候选对 | `eng_civilgeo_wf02`（洪水泛滥区与河道水力建模 HEC-RAS）vs `ag_envwater_wf03`（河流水文-水力建模与洪泛区勾绘） |
| 是否实质性重复 | **是**（输入、专业操作、产物、成功标准高度重叠） |
| 唯一主归属 | **env_water（`ag_envwater_wf03`）** |
| 主归属依据 | 完整的水文-水力洪泛区建模（HEC-HMS 降雨径流 + HEC-RAS 河道演进 + 洪泛区勾绘）是**水资源管理**职能；`ag_envwater_wf03` 覆盖了更完整的生命周期，且证据等级更高（E3 工具手册，而 `eng_civilgeo_wf02` 仅 E3 工具页面）。 |
| 次级标签 | `eng_civilgeo_wf02` → 重新标注为 **"面向土木基础设施的河道水力设计（桥涵/涵洞/堤防尺寸、冲刷、回水）"** |
| 差异依据 | 输入：设计流量（civil_geo）vs 流域降雨径流（env_water）；操作：仅 HEC-RAS（civil_geo）vs HEC-HMS+HEC-RAS（env_water）；产物：构筑物水力参数（civil_geo）vs 洪水淹没范围图（env_water）；成功标准：构筑物容量（civil_geo）vs 洪水图精度（env_water）。 |
| 待确认 | 专家确认"土木基础设施设计"与"水资源管理"的边界；确认两者作为**不同工作流保留**（而非合并）。 |

## 裁定 2：EPANET 配水管网（civil_geo vs env_water）

| 项 | 内容 |
|---|---|
| 候选对 | `eng_civilgeo_wf03`（EPANET 配水管网水力建模）vs `ag_envwater_wf04`（配水管网水力建模与校准） |
| 是否实质性重复 | **是（最接近真合并的一对）** |
| 唯一主归属 | **env_water（`ag_envwater_wf04`）** |
| 主归属依据 | 配水管网建模/校准是**水务公司运营管理**职能；`ag_envwater_wf04` 有更强证据（E1 EPA 官方页面）。 |
| 次级标签 | `eng_civilgeo_wf03` → 重新标注为 **"面向新开发项目的配水管网设计（管径选择）"** |
| 差异依据 | 较弱：设计语境（新建管网选型）vs 运营语境（既有管网校准）；两者本质都是 EPANET 水力建模。 |
| 待确认 | **高优先级**：接近重复。专家决定"合并（单主归属 env_water + civil_geo 次级标签）"还是"按设计/运营区分保留"。 |

## 裁定 3：DFT 扫描/ATPG（electronics vs semiconductor）

| 项 | 内容 |
|---|---|
| 候选对 | `eng_electronics_wf02`（可测性设计扫描链插入与 ATPG 故障覆盖率分析）vs `eng_semiconductor_wf03`（DFT 扫描插入与 ATPG） |
| 是否实质性重复 | **是** |
| 唯一主归属 | **semiconductor（`eng_semiconductor_wf03`）** |
| 主归属依据 | 扫描链插入 + ATPG 是**芯片（IC）级设计活动**，属于 semiconductor 领域，不属于 electronics/PCB。 |
| 次级标签 | `eng_electronics_wf02` → **归属错误，重归属到 semiconductor**；或重构为 **板级边界扫描（IEEE 1149.1 JTAG）**，这才是 electronics 领域独立且不同的可测性工作流。 |
| 差异依据 | 芯片可测性（scan/ATPG，IC 级）vs 板级可测性（JTAG 边界扫描，PCB 级）。`eng_electronics_wf02` 当前按 scan/ATPG 框架属于**错误归属到 electronics**。 |
| 待确认 | 专家确认 electronics/semiconductor 可测性划分。`eng_electronics_wf02` 还存在**错误平台声明**："OpenROAD … ATPG"——OpenROAD 只有扫描插入，**没有生产级 ATPG**。 |

---

## 结论

- 3 组重复对均已裁定唯一主归属 + 次级标签 + 差异依据 + 待确认项，**未删除任何覆盖方向**。
- 2 组（HEC-RAS、EPANET）是"同一工具跨两个领域"的覆盖重叠，通过主/次归属消解；1 组（DFT/ATPG）是**归属错误**，需重归属或重构。
- 所有裁定仍属**项目推断（E4）**级别，须专家确认后才能作为最终分类依据。
