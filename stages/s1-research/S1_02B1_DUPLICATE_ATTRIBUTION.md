# S1-02B1 跨领域重复归属记录

阶段：S1-02B1（physical_sciences / life_sciences / health_medicine，13 个子领域）
基线：S1-02A 有效视图 51 条（`S1_02A_EFFECTIVE_CANDIDATES.csv`）
生成方式：候选 `cross_domain_overlap` 字段提取 → B1×A 标题词元 Jaccard 相似度扫描（阈值 ≥0.35，命中 0）→ 聚焦对比（B1 物理集群 × A 能源/水环境/土木地质；B1 健康 × B1 物理；B1 生命 × B1 健康）。
结论：**未发现实质性重复候选**；5 组相邻候选已记录差异依据，全部裁定 `substantively_duplicate=no`。

本文件是二级评审材料。全部裁定按上一阶段方法论列为待专家确认级别（对应 A 阶段 "E4-level needing expert confirmation" 口径），但不作为新增候选的 E4 证据——B1 候选行的 `pending_confirmation` 只承载本候选自身的证据缺口。

## 逐对裁定

### 1. phys_phys_wf04 × eng_energypower_wf04（核能计算）

| 字段 | 裁定 |
| --- | --- |
| 是否实质性重复 | 否 |
| 唯一主归属 | 不适用（两条独立） |
| 差异依据 | phys_phys_wf04 校验临界安全方法学（偏差与 USL 基准评测，ANS-8 族）；eng_energypower_wf04 仿真熔盐堆燃料循环与热工水力。输入：临界基准实验 vs 反应堆设计参数。交付物：安全校验报告 vs 仿真结果。标准族不同（ANS-8 vs 反应堆物理程序）。 |
| 待确认 | 无 |

### 2. phys_earth_wf01 × ag_envwater_wf03（气象—水文链）

| 字段 | 裁定 |
| --- | --- |
| 是否实质性重复 | 否 |
| 唯一主归属 | 不适用（两条独立） |
| 差异依据 | phys_earth_wf01 生产业务化全球数值天气预报（观测处理、资料同化、预报、评分）；ag_envwater_wf03 消费预报输出作为河流水文水动力漫滩建模的驱动场。天气—水文链条的生产端 vs 消费端。 |
| 待确认 | 无 |

### 3. phys_phys_wf01 × med_onco_wf01（放疗物理相邻环节）

| 字段 | 裁定 |
| --- | --- |
| 是否实质性重复 | 否 |
| 唯一主归属 | 不适用（两条独立） |
| 差异依据 | phys_phys_wf01 是患者特异性、基于实测的 IMRT QA（γ 分析对照容差/行动限）；med_onco_wf01 是放疗物理计划/病历审查（初始、每周、治疗结束核查）。同一临床链条的相邻步骤；任务与交付物不同（QA 报告 vs 病历审查签字）。 |
| 待确认 | 无 |

### 4. life_sysmic_wf05 × med_pubhealth_wf02（微生物组研究 vs 暴发调查）

| 字段 | 裁定 |
| --- | --- |
| 是否实质性重复 | 否 |
| 唯一主归属 | 不适用（两条独立） |
| 差异依据 | life_sysmic_wf05 应用 STORMS 清单报告已完成微生物组研究的发表流程；med_pubhealth_wf02 是 CDC 十步暴发现场流行病学调查。研究发表报告 vs 公共卫生应急响应，无共享交付物。 |
| 待确认 | 无 |

### 5. phys_chem_wf03 × life_biomol_wf04（(Q)SAR vs 分子对接）

| 字段 | 裁定 |
| --- | --- |
| 是否实质性重复 | 否 |
| 唯一主归属 | 不适用（两条独立） |
| 差异依据 | phys_chem_wf03 在 OECD 原则下开发并验证面向 REACH 安全评估的监管 (Q)SAR 模型；life_biomol_wf04 执行库级对接虚拟筛选用于先导化合物发现，含重对接验证。统计词汇共享，监管语境与交付物不同。 |
| 待确认 | 无 |

## 群组级检查（无 A 行可配对）

- **phys_earth_wf03（地震危险性目录）vs 土木地质集合**：A 阶段土木地质集合（eng_civilgeo_wf01–04）不含地震危险性 A 行，子领域子任务报告中泛化的相邻怀疑为空。目录类交付物为工程危险性分析的输入而非其本体。无配对，仅记录。
- **life_biomol_wf04 与 S1-01 lenacapavir SAR 原型**：S1-01 曾将一个 SAR 类任务卡从 chemistry_materials 重分类至 biomolecular。life_biomol_wf04 与该原型方法相邻，但原型是任务卡而非候选行；无候选 ID 可配对。记录为原型级相邻性，供后续阶段参考。
- **life_sysmic_wf03 与 S1-01 Gillespie GRN 原型**：同上，原型级方法相邻性（随机模拟 vs 系统生物学建模），无候选 ID 可配对。

## 结论

- B1 57 条候选与 A 51 条有效基线之间无实质性重复；5 组相邻对全部裁定独立保留，差异依据已记录。
- B1 候选完整保留：`duplicate_status=none`（57/57），无主归属无次级标签（B1 不在 A 基线上充当主归属或次级标签）。
- 全部裁定待独立评审确认；与本阶段其他产出相同，本文件不修改任何 S1-02A 文件。

机器可读版本：`S1_02B1_DUPLICATE_ATTRIBUTION.csv`