# 类目覆盖验证

本文件验证平台设计是否覆盖全部 14 个 domain_code，而不只是首批三个类目。结论先说：平台字段与流程可以覆盖 14 个类目，但 08 草案的配额漏了 `agriculture_env`，必须显式补上。

## 1. 口径、来源与缺口

### 14 个 domain_code

以 `stages/s1-research/S1_01_CATEGORY_MAPPING.csv` 为准，官方域是 13 个命名域加 Other，共 14 个 `domain_code`。`stages/s0-baseline/08_coverage_matrix_draft.csv` 只有 12 个非 CS 类目，合计 500。

| domain_code | 中文 | 子域数 | 官方任务 | 08 配额 | 建议配额 | 差 |
| --- | --- | --- | --- | --- | --- | --- |
| business_finance | 商业与金融 | 8 | 19 | 50 | 47 | -3 |
| computing_math | 计算与数学 | 7 | 19 | 0 | 0 | 0 |
| education_info | 教育与信息 | 3 | 2 | 36 | 36 | 0 |
| engineering | 工程 | 10 | 16 | 50 | 48 | -2 |
| health_medicine | 健康与医学 | 5 | 19 | 60 | 57 | -3 |
| legal | 法律 | 2 | 2 | 36 | 36 | 0 |
| life_sciences | 生命科学 | 4 | 12 | 48 | 46 | -2 |
| other | 其他 | 1 | 2 | 32 | 32 | 0 |
| physical_sciences | 物理科学 | 4 | 14 | 46 | 44 | -2 |
| psychology_neuro | 心理与神经 | 2 | 3 | 34 | 34 | 0 |
| social_sciences | 社会科学 | 1 | 1 | 34 | 34 | 0 |
| transport_safety | 交通与安全 | 3 | 2 | 34 | 34 | 0 |
| visual_media | 视觉与媒体 | 3 | 11 | 40 | 40 | 0 |
| agriculture_env | 农业与环境 | 2 | 0 | 无行 | 12 | 新增 |
| 合计 |  | 55 | 122 | 500 | 500 | 0 |

### 缺口一：agriculture_env 被漏掉

`08_coverage_matrix_draft.csv` 的 12 个非 CS 类目配额合计正好 500，但 `agriculture_env` 不在表里。它不是 CS 域，也不该按 0 处理。按 12 类做覆盖，等于把一个官方域从 500 条里静默删掉。

建议补 12 条，全部给 `env_water`。`precision_agriculture` 没有官方样本，暂不分配配额，留在手工组做后续扩样。来源从五个资产最重的类目各减一点：health 60 减 3，business 50 减 3，engineering 50 减 2，life 48 减 2，physical 46 减 2。总数仍是 500，08 其余不动。

这条要负责人拍板。未拍板前，500 的计数模型按"13 类加 1 个待补"处理，不能报成 12 类已完成。

### 缺口二：computing_math 的 A/B 口径未裁决

`08` 把 computing_math 的 `proposed_tasks` 设为 0，理由是 CS 不计入 500。但 docs/04 把"computing_math 是否 A/B 并行"列为未定。平台按 0 处理，同时在类目配置里保留 `active=false`，随时可打开。这不影响 500 的口径，但要在看板上标"待裁决"，避免被读成"该类目不需要专家"。

### 缺口三：6 个空覆盖子域没有官方样本

`chemical_process`、`mining_petroleum`、`aviation`、`maritime_port`、`educational_technology`、`precision_agriculture` 在官方 122 条里没有任务。没有样本就没有环境先例。平台对它们的态度是手工兜底，不进 MVP 自动流程。

## 2. 环境维度总表

数字来自 `stages/s0-baseline/04_task_inventory.csv` 与阶段 0 汇总。官方 122 条中 Linux 86、Windows 36，非 CS 是 71 Linux、32 Windows。GUI 维度是 40 条需要、73 条不需要、9 条未知。

| domain_code | OS（L/W） | GUI 是/未知 | GPU | 外部服务 | 专有软件 | 数据规模 | 验证器主型 | 网络 | 隐私 | 专家可得性 | P1 状态 | 首批 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| business_finance | 12/7 | 9/2 | 0 | 4 online + 5 staged | 中 | 1.69 GiB，中位 0.6 MiB | scorer, evaluator | 需在线与本地服务 | 中 | 高（19 条） | 后续 | 否 |
| computing_math | 15/4 | 4/1 | 0 | 0 | 低 | 1.37 GiB，中位 0.4 MiB | scorer, checker | 无 | 低 | 高（19 条） | 后续（A/B 待裁） | 否 |
| education_info | 1/1 | 1/0 | 0 | 0 | 低 | 0.55 MiB | scorer | 无 | 低 | 低（2 条） | MVP | 否 |
| engineering | 11/5 | 7/2 | 1 | 0 | 中（仿真） | 1.42 GiB，中位 12.1 MiB | scorer, checker | 无 | 中 | 高（16 条） | MVP | 是 |
| health_medicine | 15/4 | 1/0 | 0 | 0 | 中（影像） | 16.76 GiB，中位 9.0 MiB | scorer | 无 | 高 | 高（19 条） | MVP | 否 |
| legal | 2/0 | 0/0 | 0 | 0 | 低 | 1.25 MiB | scorer | 无 | 中 | 低（2 条） | MVP | 是 |
| life_sciences | 12/0 | 1/2 | 0 | 1 public-ref | 中（生信） | 14.51 GiB，中位 178.5 MiB | scorer, hook, checker | 只读公开库 | 高 | 中（12 条） | MVP | 否 |
| other | 1/1 | 2/0 | 0 | 1 public-ref | 低 | 195 MiB，中位 97.3 MiB | scorer | 只读公开库 | 低 | 低（2 条） | 后续 | 否 |
| physical_sciences | 10/4 | 3/0 | 0 | 2 online | 中（化学） | 1.50 GiB，中位 10.2 MiB | checker, scorer | 需在线 | 低 | 中（14 条） | MVP | 否 |
| psychology_neuro | 2/1 | 3/0 | 0 | 0 | 中（Slicer） | 9.57 GiB，中位 1.5 GiB | scorer, checker, hook 各 1 | 无 | 高（IRB） | 低（3 条） | MVP | 是 |
| social_sciences | 1/0 | 0/0 | 0 | 0 | 低 | 447 MiB，单条 | scorer | 无 | 中 | 低（1 条） | MVP | 否 |
| transport_safety | 2/0 | 0/1 | 0 | 无 | 低 | 170 MiB，中位 85.1 MiB | scorer, evaluator | 无 | 低 | 低（2 条） | MVP | 否 |
| visual_media | 2/9 | 9/1 | 2 | 无 | 高（Adobe 类） | 2.03 GiB，中位 7.4 MiB | evaluator, scorer, hook | 无 | 中 | 中（11 条） | 后续 | 否 |
| agriculture_env | 目录 0，重分类 1（Linux） | 未知 | 0 | 0 | 低 | 32 KiB（glm_lake_calibration） | script/scorer（参考 glm_lake_calibration） | 无 | 中（地块数据） | 待招募 | MVP | 否 |

说明：专家可得性用官方任务数加阶段 1 候选族密度作代理，不是独立调查。agriculture_env 官方目录 0 条，但 `env_water` 有 1 条重分类活动任务（`physical_sciences/glm_lake_calibration`），不能当成完全无样本。

## 3. 按环境门槛分组

平台支持状态不等于任务可交付。下面按"卡在哪"分组，这样采购和排期能对上。

### A 组：Linux 加无外部服务，平台可全覆盖

`computing_math` 不计入 500，不参与分组。

legal、psychology_neuro、education_info、social_sciences、transport_safety。

- 共同点：不需要 Windows，不需要 GPU，网络可以完全离线。
- 差异：psychology_neuro 有 8.06 GiB 的 Slicer 资产与 IRB 要求，走大资产与隐私通道。
- 平台动作：标准流程，资料上限按类目配置。

### B 组：大资产或只读公开引用，平台可覆盖但要加限制

health_medicine、life_sciences、physical_sciences、agriculture_env。

- health_medicine 有 16.76 GiB，单任务最大 12.08 GiB（`nsclc_radiomics_cox_signature_v1`），另有 3.04 GiB 的 `wsi_tumor_localization_1`。
- life_sciences 有 14.51 GiB，单任务最大 11.80 GiB（`idp_ensemble_scoring`），另有 UCSC 只读引用。
- physical_sciences 有 2 条 online-required（ChemInfo、Ketcher），必须在线才能复现。
- 平台动作：单文件上限 20 GiB，任务级 `asset_cap_override_gib` 可到 12 GiB，导出分卷；公开引用只存 URL 与访问证据，不保证长期可达。

### C 组：需要 Windows 宿主，平台能写不能验

business_finance、visual_media，另有 engineering 的 5 条 Windows。

- business_finance 有 3 条 Windows staged-local（Metabase、Odoo 加 psql、taxform）。
- visual_media 有 9 条 Windows，占该域 11 条的大头。
- 平台动作：`environment.os=windows` 正常保存，风险层自动升 medium；交接包标注 `windows_required`。任务能不能跑由工程侧决定，平台不承诺。

### D 组：需要 GPU，3 条全在 Windows

`engineering/humanoid_velocity_tracking_policy`、`visual_media/chroma_key_from_reference`、`visual_media/compress_3dgs_scene_ply`。

- 平台动作：`gpu.required=true` 与显存、CUDA 版本入库，风险层升 high。平台不调度 GPU。
- 决策点：docs/06 默认 2026-11-25 不采购 GPU。若不采购，这 3 条标不可交付，不占编号。

### E 组：外部服务，13 条

- staged-local 5 条：2 条 Linux（BPMN 双任务，Flowable localhost:8080），3 条 Windows（Metabase 3000、Odoo 8069 加 psql、taxform 8080）。
- online-required 6 条：business 4 条（ar_full_1500、ar_full_300、equity_research_summary、ff5_public_reconstruction），physical 2 条（ChemInfo、Ketcher）。
- public-ref 2 条：life 的 UCSC、other 的 Ruffle。

平台动作：`network.mode` 四值枚举，`endpoints` 列域名与用途，`secrets_attestation` 声明无密钥。online-required 一律 high，且必须附可达性证据。平台不做代理、不缓存外部内容。

### F 组：只能手工

6 个空覆盖子域。没有官方样本，没有环境先例，没有可参照的验证器。平台保留字段，但不进自动流程，由负责人指派专家从零设计。

## 4. 平台字段与流程要预留什么

结论：14 个类目共用一套 schema，差异靠配置。下面每行是"后续类目要用到的能力"，现在就要留位，否则将来要改表。

| 后续需求 | 现在留的字段或流程 | 启用时要改什么 |
| --- | --- | --- |
| Windows 任务 | `environment.os`、`os_version`、`gui_required`、`handoff.execution_notes` | 只改类目配置与工程适配器，不改表 |
| GPU 任务 | `environment.gpu.required`、`vram_gb`、`cuda_version` | 打开风险规则，不改表 |
| GUI 任务 | `gui_required` 三值、交付物支持 png、人工评分档位 | 评审表单加截图证据项 |
| 大资产 | `asset_cap_gib`、`asset_cap_override_gib`、分片上传、分卷导出 | 调上限，不改表 |
| 外部服务 | `network.mode`、`endpoints`、`external_services`、`secrets_attestation` | 工程侧建服务清单，平台只登记 |
| 专有软件 | `software[].license_type`、`install_method`、资料 `license.redistribution` | 采购与许可审核，不改表 |
| 隐私与伦理 | `pii_level`、`deidentification`、`irb.protocol_id` | 收紧扫描规则 |
| 监管签署 | `review.sign_offs` 四类签署 | 增加签署角色 |
| 新类目 | `categories.profile` JSON | 后台加一行配置 |
| 新子域 | `subdomains` 表 | 后台加一行配置 |
| 新验证器类型 | `success_criteria.check_method` 与 `verifier_hint` | 工程侧实现，平台只存提示 |

关键设计：状态机不认识类目。没有任何一个状态迁移以 `domain_code` 为条件。类目只影响必填项、资产上限、评审角色、风险规则。这条约束保证新增类目不用回归 13 套状态机。

## 5. 三个类目的配置差异示例

### legal：文档密集，低资产，人工判断重

```json
{
  "domain_code": "legal",
  "asset_cap_gib": 1,
  "allowed_os": ["linux"],
  "gui_flag_required": false,
  "required_review_roles": ["domain_reviewer", "license_reviewer"],
  "risk_rules": [
    {"when": "pii_level == 'high'", "tier": "high"},
    {"when": "deliverables has legal_opinion", "tier": "high"}
  ]
}
```

### psychology_neuro：大资产，IRB，BIDS

```json
{
  "domain_code": "psychology_neuro",
  "asset_cap_gib": 12,
  "allowed_os": ["linux"],
  "gui_flag_required": true,
  "required_review_roles": ["domain_reviewer", "ethics_reviewer"],
  "risk_rules": [
    {"when": "asset_bytes > 1GiB", "tier": "high"},
    {"when": "irb.protocol_id is null", "tier": "high"}
  ]
}
```

### engineering：仿真与 GUI，含 GPU 例外

```json
{
  "domain_code": "engineering",
  "asset_cap_gib": 4,
  "allowed_os": ["linux", "windows"],
  "gui_flag_required": true,
  "gpu_allowed": true,
  "required_review_roles": ["domain_reviewer", "engineering_reviewer"],
  "risk_rules": [
    {"when": "gpu.required == true", "tier": "high"},
    {"when": "os == 'windows'", "tier": "medium"}
  ]
}
```

同一套字段，三种类目只差配置。新增 agriculture_env 时只写配置，不改代码。

## 6. 首批覆盖与后续路径

### 首批三个类目

法律、神经影像、建筑节能（属 engineering 的 `energy_power` 子域）。选择理由在 `work/recruitment-plan-v0.md`：专家可得、资料可公开或合成、环境是 Linux。

首批覆盖 3 个 domain_code、5 个子域、5 条任务。这只占 14 个类目的 21%，不能当成覆盖结论。

### 平台能力覆盖的时间线

| 阶段 | 覆盖类目 | 依赖 |
| --- | --- | --- |
| 试点两周 | legal、psychology_neuro、engineering（energy_power） | 无额外设备 |
| 前 100 条 | 加 health、life、physical、education、social、agriculture、transport | 大资产存储、公开引用证据 |
| 满产 | 加 business、visual、other | Windows 宿主、外部服务清单、GPU 决策 |
| 手工 | 6 个空覆盖子域 | 专家从零设计，平台只记录 |

## 7. 结论

1. 平台 schema 覆盖 14 个 domain_code。没有任何一类因为字段缺失而无法录入。
2. 第一批能完整支持的是 3 个类目，能支持录入与评审但受资产、引用或 GUI 未知限制的是 7 个，需要 Windows、GPU 或在线服务才能验的是 4 个。
3. `agriculture_env` 必须补进配额，建议 12 条，从五个大类目各减一点，总数仍 500。
4. 6 个空覆盖子域只能手工兜底。平台不做假样本，也不把它们计入自动流程。
5. 后续类目不会被堵死：新增类目只加配置行，状态机、权限、快照格式都不变。

## 8. 自检

- 14 个 domain_code 都有覆盖行：第 2 节与 `data/category-environment-matrix.csv` 一致。
- `agriculture_env` 缺口已显式标出：第 1 节。
- Windows、GPU、GUI、大资产、外部服务都有对应设计：第 3、4 节。
- 首批是否只覆盖 3 个类目：是，且明确说明不代表全量覆盖。
