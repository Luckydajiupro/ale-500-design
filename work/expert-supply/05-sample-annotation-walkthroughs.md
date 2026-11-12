# 05 三份样例标注流程：从一份资料到一条可交付任务

> 本文回答：拿到一份公开或合成资料后，怎么找到可做的工作流、怎么拆步骤、怎么填十块、怎么写成功标准与证据、评审会问什么、哪里最容易失败。
> 三份样例分别对应试点三类：法律检索、神经影像、建筑节能。全部使用公开或合成资料，不复制官方任务正文、隐藏评分规则或受限资产。
> 读法：不要照抄样例内容；照抄结构。每份末尾的“最容易失败”比正文更值得先看。

## 样例一：法律检索——从法条到三份解除通知的合法性 memo

### 1. 起点资料

- `中华人民共和国劳动合同法`（官方法规库，公共领域），重点第 39、40、43 条。
- 一份公开的“解除劳动合同通知书”示范文本（人社局网站，政府公开）。
- 合成材料：3 份解除通知（分别以“严重违纪”“不能胜任”“客观情况重大变化”为由）、员工手册签收页、12 个月考勤与绩效记录。
- 全部合成件用虚构公司“华岑制造”、虚构员工“A/B/C”，不含真实案号与姓名。

### 2. 怎么找到任务

先读法条，列出三个“判断分叉”：

1. 第 39 条（过错性解除）不需要提前通知与经济补偿，但要求“严重”违纪且制度已告知。
2. 第 40 条（无过失性解除）需要提前 30 日书面通知或额外支付一个月工资，且“不能胜任”要先培训或调岗。
3. 第 43 条要求通知工会；程序瑕疵会影响解除效力。

再看示范文本，发现它只写了“根据第 X 条”，没有事实、没有程序、没有送达证据。这就是任务种子：**不是“分析合同”，而是“对三份通知逐份判断条款适用、程序、证据缺口，并出具可回溯的引证 memo”**。

淘汰的两个候选：
- “写一份解除通知模板”——太短，一步生成，没有判断。
- “统计某地劳动争议判决”——需要批量判决数据，授权与去重成本高。

### 3. 拆步骤

| 步 | 动作 | 判断点 | 产物 |
|---|---|---|---|
| 1 | 抽取三份通知的事实（理由、日期、依据条款、送达方式） | 事实是否足以支撑“严重”“不能胜任” | `facts.csv` |
| 2 | 对照第 39/40/43 条，逐条匹配 | 适用哪条、是否满足前提 | `mapping.csv` |
| 3 | 检查程序：通知工会、提前 30 日、送达证据 | 程序瑕疵是否致命 | `procedure.md` |
| 4 | 标注证据缺口与需外部律师确认的点 | 哪些结论不能下 | `risks.csv` |
| 5 | 写 memo（问题—结论—理由—风险） | 结论是否超出资料 | `memo.md` |
| 6 | 做引证表，逐条回溯 | 条号、款项、生效日期 | `citations.csv` |

专业难点：区分“实体理由是否成立”与“程序是否合法”；两者任一失败，结论都不同。

### 4. 十块怎么填

**identity**
> `LEGAL-RES-014` 依据《劳动合同法》第 39、40、43 条，对 3 份解除通知做合法性检索并出具引证 memo
> 领域 legal / legal_research；难度中；预计 12 小时；交付 Markdown + CSV。

**scenario**
> 你是华岑制造的法务专员。人力资源部周五要开员工关系会，需要你判断 3 份拟解除通知是否站得住脚。你不能对外发函，只能出具内部 memo；对没有把握的结论，必须标“需外部律师确认”，不能直接下结论。公司没有常年法律顾问，资料只有法条、员工手册和三份通知。

**materials**

| id | 文件 | 来源 | 许可 | 用途 |
|---|---|---|---|---|
| M1 | `labor_law_excerpt.md` | 官方法规库 | 公共领域 | 法条依据 |
| M2 | `notice_A.docx` | 合成 | 项目自制 | 事实 A |
| M3 | `notice_B.docx` | 合成 | 项目自制 | 事实 B |
| M4 | `notice_C.docx` | 合成 | 项目自制 | 事实 C |
| M5 | `handbook_signoff.pdf` | 合成 | 项目自制 | 制度告知 |
| M6 | `attendance_2025.csv` | 合成 | 项目自制 | 考勤事实 |

每个文件标 SHA-256；M2–M6 在 `provenance` 标“合成，不含真实个人信息”。

**operations**
1. 用 `pdftotext`/`python-docx` 抽取 M2–M6 全文，保存到 `work/`。
2. 建 `facts.csv`：`notice_id,reason,date,article_cited,delivery_method,evidence_ref`。
3. 对每份通知，判断适用第 39 条还是第 40 条；写出“满足/不满足/证据不足”三选一。
4. 检查第 43 条工会程序；没有记录的标 `PROCEDURE_GAP`。
5. 对“不能胜任”的通知，检查是否有培训/调岗记录；没有则标 `NO_RECORD`。
6. 对每条结论给出至少 1 个法条引用；无引用则标 `NEED_REVIEW`。
7. 写 memo：问题、结论、理由、风险、建议。
8. 生成 `citations.csv`，逐条填法名、条、款、生效日期、在 M1 中的位置。

**deliverables**

| 文件 | 格式 | 必需内容 |
|---|---|---|
| `output/memo.md` | Markdown | 3 份通知逐份结论、风险、建议 |
| `output/facts.csv` | CSV UTF-8 | 6 列，一行一份通知 |
| `output/citations.csv` | CSV | `claim_id,law,article,paragraph,effective_date,source_ref` |
| `output/risks.csv` | CSV | `risk_id,notice_id,level,description,action` |

**success_criteria**
- 3 份通知都有“事实—条款—结论”三段，缺一段即失败。
- 每条结论至少 1 个现行有效法条；条/款与 M1 一致。
- 第 43 条程序检查在 3 份通知中都有记录；缺记录必须标 `PROCEDURE_GAP`。
- “不能胜任”通知必须检查培训/调岗记录；缺记录标 `NO_RECORD`。
- `citations.csv` 每行能在 M1 中定位；`effective_date` 不晚于任务日期。
- 全文无真实姓名、公司、案号；出现即失败。

**environment**
> Ubuntu 22.04 / x86_64；2 vCPU、4 GB RAM、5 GB 磁盘；Python 3.11、python-docx、pdftotext；完全离线；无 GUI/GPU；预计 15 分钟。

**review**
> 风险中。需人工看：3 份通知的“严重违纪”是否达到第 39 条程度；第 40 条的 30 日通知/代通知金是否满足；工会程序是否影响结论。评审问题：如果员工手册未公示，第 39 条是否仍适用？

**provenance**
> M1 官方法规库，访问 2026-11-01，版本以页面生效日期为准；M2–M6 项目合成，作者专家，CC0；无真实个人信息；未使用客户案卷。

**handoff**
> 包内：`task_source.json`、`materials/`（6 文件，8 MB）、`output/`（4 文件）、`run.md`。已知限制：法条为 2026-11 版本，未覆盖地方裁审口径。未决：通知 C 的“客观情况重大变化”是否成立，需外部律师确认。

### 5. 成功标准与证据怎么对应

| 标准 | 检查方法 | 证据 |
|---|---|---|
| 三段齐全 | 每份通知在 memo 中有三个小标题 | `memo.md` |
| 引证可回溯 | 逐行在 M1 搜索条号 | `citations.csv` |
| 程序检查 | 搜 `PROCEDURE_GAP` | `facts.csv` + `memo.md` |
| 培训/调岗检查 | 搜 `NO_RECORD` | `risks.csv` |
| 匿名化 | 搜真实姓名/公司/案号 | 全包 |

### 6. 评审会问什么

1. 为什么通知 B 适用第 40 条而不是第 39 条？
2. 没有工会记录，是“程序瑕疵”还是“足以撤销”？
3. 考勤记录能证明“严重违纪”吗？还缺什么？
4. 如果员工手册没有签收页，结论怎么变？
5. 你的“需外部律师确认”是偷懒还是真的不确定？边界在哪？

### 7. 最容易失败的地方

1. 把“法条适用”写成“法条介绍”，没有事实涵摄。
2. 只查第 39 条，漏第 43 条程序。
3. 三份通知用同一套结论，没有逐份差异。
4. 引证表条号对、款项错。
5. 出现真实公司/人名/案号。
6. 成功标准写“结论正确”，评审无法判。

## 样例二：神经影像——从合成 DICOM 到可验证的 BIDS 目录

### 1. 起点资料

- 合成 DICOM：用 `pydicom` 生成 3 个序列（T1w、T2w、rest），每个 8 层，像素随机但有解剖形状；header 只含 `PatientID=sub-01`、`StudyDate=19000101`，无姓名/生日。
- 合成 `participants.tsv`：`participant_id,age,sex,group`，3 行。
- 公开规范：BIDS 1.9 摘要、`bids-validator` 文档。
- 公开工具镜像：`dcm2niix`、`bids-validator`、FSL 的 `fslhd`。

### 2. 怎么找到任务

先跑一遍最小转换，发现四个真实错误：

1. `dcm2niix` 默认输出 `sub-01_T1w.nii.gz`，但 rest 序列被命名成 `sub-01_task-rest_bold.nii.gz` 才对。
2. JSON 缺 `RepetitionTime`、`TaskName`、`PhaseEncodingDirection`。
3. `participants.tsv` 有 3 行，但目录只有 2 个受试者。
4. T1w 的方向在 `fslhd` 里显示 qform 与 sform 不一致。

这四类错误就是任务：**不是“跑一下转换”，而是“把一批不规范的导出整理成 validator 通过的 BIDS，并写清修复依据”**。

淘汰的候选：
- “做 fMRIPrep 全流程”——需要 GPU/大数据，试点不做。
- “写一个影像组学分类器”——变成建模任务，偏离数据整理。

### 3. 拆步骤

| 步 | 动作 | 判断点 | 产物 |
|---|---|---|---|
| 1 | 读 DICOM header，列序列 | 哪些是 T1/T2/rest | `series.csv` |
| 2 | `dcm2niix` 转换 | 命令、版本、输出名 | `raw/` + log |
| 3 | 按 BIDS 重命名 | 实体顺序、`task-` 标签 | `bids/sub-01/` |
| 4 | 补/改 JSON | TR、TaskName、相位编码 | 侧车文件 |
| 5 | 跑 validator | error/warning 分类 | `validator.log` |
| 6 | 去脸 + QC | 三个平面、边缘 | `qc/` + `qc.csv` |
| 7 | 核对 participants | 行数、字段 | `participants.tsv` |
| 8 | 写报告 | 参数、异常、限制 | `report.md` |

专业难点：validator 通过不等于字段正确；要能解释每个字段为什么这样填。

### 4. 十块怎么填

**identity**
> `NEURO-BIDS-007` 将 3 个 DICOM 序列转换为 BIDS 结构并修复 4 类侧车字段错误
> 领域 psychology_neuro / comp_neuro；难度中；预计 16 小时；交付 BIDS 目录 + QC + 报告。

**scenario**
> 你是影像核心实验室的数据工程师。PI 下周一要把 3 名受试者的静息态数据上传到公开仓库，但导出目录命名不一致、JSON 缺字段、有一名受试者的 T1w 方向异常。你需要在不上传原始 DICOM、不暴露身份信息的前提下，整理成 BIDS，跑 validator，给出 QC 清单和修复说明。

**materials**

| id | 文件 | 来源 | 许可 | 用途 |
|---|---|---|---|---|
| M1 | `dicom/`（3 序列） | 合成 phantom | CC0 | 原始输入 |
| M2 | `participants_src.tsv` | 合成 | 项目自制 | 受试者表 |
| M3 | `bids_spec_excerpt.md` | BIDS 官方 | CC-BY | 规范 |
| M4 | `validator_help.txt` | 工具文档 | 开源 | 校验 |

`provenance` 写明：合成 DICOM，无 PHI；未使用患者数据。

**operations**
1. `dcm2niix -b y -z y -o raw/ dicom/`，记录版本与完整命令。
2. 读 `raw/*.json`，列 `SeriesDescription`、`ProtocolName`、`RepetitionTime`。
3. 按 BIDS 重命名：`sub-01/anat/sub-01_T1w.nii.gz`、`sub-01/anat/sub-01_T2w.nii.gz`、`sub-01/func/sub-01_task-rest_bold.nii.gz`。
4. 补 JSON：`RepetitionTime`、`TaskName`、`PhaseEncodingDirection`；每个值写来源（DICOM 字段/协议）。
5. 用 `fslhd` 检查 qform/sform、pixdim；方向异常则用 `fslreorient2std` 并记录。
6. 跑 `bids-validator bids/`，保存 stdout/stderr；每个 error 写修复动作，warning 写接受理由。
7. 去脸：对 T1w 三个平面检查；保存去脸前后对比图。
8. 核对 `participants.tsv` 与目录行数；写 `qc.csv`（受试者×序列×检查项）。
9. 写 `report.md`：命令、参数、错误、修复、限制。

**deliverables**

| 文件 | 格式 | 必需内容 |
|---|---|---|
| `output/bids/` | 目录 | 3 序列、JSON、`participants.tsv`、`dataset_description.json` |
| `output/qc.csv` | CSV | `subject,series,check,status,note` |
| `output/logs/` | 目录 | `dcm2niix.log`、`validator.log` |
| `output/report.md` | Markdown | 命令、字段来源、异常、限制 |

**success_criteria**
- `bids-validator` 退出码 0；有 error 即失败。
- 3 个序列文件名、JSON 字段与 `participants.tsv` 一致；逐行核对。
- JSON 无 `PatientName`、`PatientBirthDate`、机构名；出现即失败。
- 去脸覆盖三个平面；只处理一层即失败。
- `qc.csv` 覆盖 3 受试者×3 序列，缺行即失败。
- `report.md` 含完整命令与版本；缺命令即失败。

**environment**
> Ubuntu 22.04；4 vCPU、8 GB RAM、20 GB 磁盘；dcm2niix 1.0.20240202、bids-validator 1.14.6、FSL 6.0.7；离线；无 GUI/GPU；预计 25 分钟。

**review**
> 风险高（健康信息）。需人工看：header 是否残留 PHI；去脸是否彻底；qform/sform 是否改变方向；validator 通过但 TR 错误的情况。评审问题：如果 DICOM 的 TR 与协议不一致，以哪个为准？为什么？

**provenance**
> M1 合成 phantom，pydicom 生成，无真实患者；M2 合成；M3 BIDS 官方文档，CC-BY；未使用 IRB 数据；去标识方法：删除 header 直接标识符 + 去脸。

**handoff**
> 包内：`task_source.json`、`bids/`（180 MB）、`qc.csv`、`logs/`、`report.md`。已知限制：只验证 3 名受试者，未做群体统计；去脸工具版本待工程确认。未决：无。

### 5. 成功标准与证据怎么对应

| 标准 | 检查方法 | 证据 |
|---|---|---|
| validator 0 error | 看退出码与日志 | `validator.log` |
| 字段齐全 | 逐 JSON 对照清单 | `bids/**/*.json` |
| 无 PHI | `grep -ri` + 人工 | header 导出 |
| 去脸彻底 | 三平面截图 | `qc/` |
| QC 覆盖 | 行数 = 3×3 | `qc.csv` |
| 可复现 | 命令可直接重跑 | `report.md` |

### 6. 评审会问什么

1. 你为什么把 rest 命名为 `task-rest`，而不是 `task-restingstate`？
2. TR 从 DICOM 哪个字段来？如果缺失怎么办？
3. qform 与 sform 不一致时，你改了哪个？会不会引入左右翻转？
4. validator 没有报错，但你改了 JSON，怎么证明改对了？
5. 去脸后如何确认没有残留面部信息？

### 7. 最容易失败的地方

1. 只改名，不补 JSON。
2. 补了 JSON，但单位/字段来源说不清。
3. 去脸只做一层。
4. `participants.tsv` 与目录不一致。
5. 用 GUI 工具截图当证据，无法复现。
6. 把“validator 通过”当成“数据正确”。

## 样例三：建筑节能——从示例模型到可重算的节能量

### 1. 起点资料

- EnergyPlus 官方示例 `5ZoneAirCooled.idf`（DOE 公开示例）。
- 北京 TMY3 气象文件（公开）。
- 合成 12 个月电费账单：按月 kWh、需量 kW、分时电价。
- 改造说明：外墙 U 值从 0.6 降到 0.35 W/(m²·K)，其余不变。

### 2. 怎么找到任务

先跑基线，发现三个可做的判断：

1. 示例模型自带 `RunPeriod` 只有 1 周，要做全年得改。
2. 账单是月度总表，模型输出是逐时，必须聚合到月才能校准。
3. 改造只改一个参数，但节能量受气象、入住率、设定点影响，必须控制变量。

任务因此定为：**“跑基线—用合成账单校准—同气象同边界下改外墙—算节能量—给 M&V 方案”**，不是“写一个节能报告”。

淘汰的候选：
- “设计一套地源热泵系统”——需要设备选型与造价，超出资料。
- “做 CFD 气流模拟”——需要 GPU/Windows 工具，试点不做。

### 3. 拆步骤

| 步 | 动作 | 判断点 | 产物 |
|---|---|---|---|
| 1 | 读 IDF，列区域、HVAC、面积 | 边界是否含全部空调区 | `model_notes.md` |
| 2 | 改 `RunPeriod` 为全年，跑基线 | 天气文件匹配 | `baseline.csv` |
| 3 | 月度聚合，和账单对比 | 电量/燃气口径 | `calibration.csv` |
| 4 | 算 CV(RMSE)/NMBE | 是否达标 | `calibration.md` |
| 5 | 复制模型，改外墙 U 值 | 只改一个变量 | `measure.idf` |
| 6 | 同气象重跑 | 面积/系统不变 | `measure.csv` |
| 7 | 算节能量与不确定性 | 单位、边界 | `savings.csv` |
| 8 | 写 M&V 方案 | 选项 A/B/C/D | `mv_plan.md` |

专业难点：校准不是“看起来差不多”，而是有指标；节能量不是“模型差值”，而是有边界与不确定性。

### 4. 十块怎么填

**identity**
> `ENG-BLDG-021` 用 EnergyPlus 示例模型评估外墙保温改造的节能量并给出 M&V 方案
> 领域 engineering / energy_power；难度中高；预计 22 小时；交付模型、CSV、M&V 计划。

**scenario**
> 你是节能咨询公司的分析师。客户要判断一栋既有办公楼的外墙保温改造是否值得做，但只给了 12 个月合成电费单和一份示例模型，没有现场审计。你需要在两周内给出基线、节能量、投资回收期的初步判断，并说明哪些假设需要现场核实。你不能承诺实际节费。

**materials**

| id | 文件 | 来源 | 许可 | 用途 |
|---|---|---|---|---|
| M1 | `5ZoneAirCooled.idf` | EnergyPlus 示例 | DOE 公开 | 基线模型 |
| M2 | `CHN_Beijing.epw` | TMY3 | 公开 | 气象 |
| M3 | `bills_2025.csv` | 合成 | 项目自制 | 校准 |
| M4 | `retrofit_spec.md` | 合成 | 项目自制 | 改造参数 |

**operations**
1. 读 M1：列 5 个区域、面积、HVAC 类型、`RunPeriod`。
2. 把 `RunPeriod` 改为 1/1–12/31，`Site:Location` 与 M2 匹配；跑基线，保存 `eplusout.csv`。
3. 用 Python 把逐时用电聚合为月度 kWh；与 M3 逐月对比。
4. 算 CV(RMSE) 与 NMBE（假设阈值：月度 CV(RMSE) ≤15%、NMBE ±5%，按 Guideline 14 常用口径，待领域评审确认）；不达标则检查面积/入住率/设备。
5. 复制 M1 为 `measure.idf`，只改外墙 `Construction` 的 U 值（0.6→0.35），其余不动。
6. 用同一 M2 跑 `measure.idf`；保存逐时输出。
7. 计算 `savings = baseline - measure`，按月与全年；单位统一 kWh。
8. 写 `mv_plan.md`：选项 B（改造后表计）或 C（账单比对），说明数据需求、基线期、不确定性。

**deliverables**

| 文件 | 格式 | 必需内容 |
|---|---|---|
| `output/model/` | 目录 | `baseline.idf`、`measure.idf`、`run/` |
| `output/baseline.csv` | CSV | 月度电量、需量 |
| `output/measure.csv` | CSV | 同上 |
| `output/savings.csv` | CSV | 月度/全年节能量、单位 |
| `output/mv_plan.md` | Markdown | 选项、基线、数据需求、不确定性 |

**success_criteria**
- 基线/改造使用同一 EPW、同一面积、同一 HVAC 设定；任一不同即失败。
- 单位统一 kWh；出现 kBtu/therm 未换算即失败。
- `savings.csv` 的全年值 = 12 个月之和 = 基线 − 改造；可重算。
- 校准指标可复算；未达标必须写原因与处理。
- M&V 选项与数据条件匹配；只写“建议 M&V”不写选项即失败。
- 结论含“基于模型与假设，不承诺实际节费”。

**environment**
> Ubuntu 22.04；4 vCPU、8 GB RAM、20 GB 磁盘；EnergyPlus 24.1.0、Python 3.11、pandas；离线；无 GUI/GPU；单次全年运行 <15 分钟。

**review**
> 风险中。需人工看：边界是否含全部空调区；入住率/设定点是否与账单一致；节能量是否只归因于外墙；校准指标是否被“调参”凑出。评审问题：如果换一个气象年，节能量方向是否稳定？

**provenance**
> M1 EnergyPlus 官方示例，版本 24.1.0；M2 TMY3 公开；M3 合成，按北京商业电价假设；M4 合成改造说明；未使用业主数据。

**handoff**
> 包内：`task_source.json`、`model/`（2 IDF + 输出，50 MB）、`savings.csv`、`mv_plan.md`、`run.md`。已知限制：示例模型非真实建筑；账单为合成；未做现场核实。未决：外墙构造层材料需现场确认。

### 5. 成功标准与证据怎么对应

| 标准 | 检查方法 | 证据 |
|---|---|---|
| 同气象同边界 | 比对 IDF 的 `RunPeriod`/`Site:Location`/面积 | `model_notes.md` |
| 单位统一 | 搜 kWh/kBtu/therm | `savings.csv` |
| 节能量可重算 | 12 月求和 vs 全年 | CSV 公式 |
| 校准可复算 | 用 CSV 重算 CV(RMSE) | `calibration.md` |
| M&V 选项匹配 | 检查数据需求与选项 | `mv_plan.md` |
| 无业主数据 | 查 provenance | 资料包 |

### 6. 评审会问什么

1. 你为什么选选项 B 而不是 C？
2. 账单只有总量，怎么做月度校准？
3. 入住率没数据，你怎么处理？
4. 节能量 8% 是模型差值，怎么证明不是气象波动？
5. 如果外墙 U 值实际是 0.5，结论怎么变？

### 7. 最容易失败的地方

1. 基线/改造用了不同气象或不同面积。
2. 单位混用，节能量差 3.4 倍。
3. 只改一个参数，却在结论里说“整体节能”。
4. 未校准就报节能量。
5. 账单是年度总表，却做月度校准。
6. 把“模型输出”当成“实测节能量”。

## 三份样例的共同结构

| 环节 | 法律 | 神经影像 | 建筑节能 |
|---|---|---|---|
| 起点 | 公开法条 + 合成通知 | 合成 DICOM | 公开示例模型 + 合成账单 |
| 任务种子 | 三份通知的条款/程序差异 | 四类 BIDS 错误 | 基线校准 + 单变量改造 |
| 核心判断 | 第 39/40/43 条适用 | 字段来源与方向 | 边界/单位/校准 |
| 证据 | 引证表 + 程序记录 | validator 日志 + QC 图 | 模型文件 + 可重算 CSV |
| 最大失败 | 引证错/漏程序 | 只改文件名 | 边界不一致 |

三份都遵守同一条：**任务不是“做一个专业动作”，而是“在约束下做出一套别人能检查的交付物”**。
