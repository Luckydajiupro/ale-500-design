# 05 从官方完整包到三份角色样例

> 本文回答：官方 ALE 任务包长什么样，每个文件起什么作用，怎么把它映射到我们的十块任务源和工程 Harbor 包；然后再看商业会计、神经影像、建筑节能三份角色样例。
> 三份角色样例对应 3 条试点。法律 42 条走供应方 ALE-data 导入，不在专家手册里做全流程样例；供应方包检查见 `04` 第 1 节和本文附录。
> 全部使用公开或合成资料，不复制官方任务正文、隐藏评分规则或受限资产。
> 读法：先读 `02a-ale-context-and-data.md` 第 1 到 6 节，再读本文第 0 节，建立“完整包”的标准；最后看三份样例，学怎么在自己的领域里做到同样的结构。不要照抄样例内容，照抄结构。

## 0. 先看官方完整包

官方数据包里有一条完整任务，路径是 `inputs/frozen/03_ale-data/task-data-v1.1/legal/legal_dr_fees_01/base`。它 1.0M，包含 7 份 PDF、5 个案件、1 份金标、1 份验证记录。

它不是为了让你照抄法律内容。它是让你看到一条 ALE 任务到底要交什么，以及输入、输出、答案、评分和验证怎么分开。

### 0.1 包的完整结构

```
base/
  input/
    task_brief.md
    output_contract.json
    document_manifest.json
    cases.json
    documents/
      bac_*.pdf                7 份
    runtime_env/
      pyproject.toml
  reference/
    answer_key.json
    stage1_manifest.json
  software/
    README.txt
    python3.12
```

### 0.2 每个文件做什么

| 文件 | 作用 | 关键点 |
|---|---|---|
| `input/task_brief.md` | 任务说明 | 闭卷；只允许用 `base/input` 下的材料；5 个案件；交付一个 JSON；字段名和两位小数写死 |
| `input/output_contract.json` | 输出合同 | 根对象、`cases` 数组、case_1 到 case_5、字段类型、示例形状 |
| `input/document_manifest.json` | 材料清单 | 7 份 PDF 的 document_id、文件名、格式、相对路径、sha256 |
| `input/cases.json` | 案件事实 | 5 个案件的金额和 special_condition；case_4 已达成和解 |
| `input/documents/` | 源材料 | 7 份真实形态的 BAC PDF，不是整理后的表格 |
| `input/runtime_env/pyproject.toml` | 运行环境 | 任务需要的 Python 依赖 |
| `reference/answer_key.json` | 金标 | 5 案三字段答案；三项权重 7/7/6；容差 0.01 元 |
| `reference/stage1_manifest.json` | 验证记录 | 正例 1.0、负例 0.0、满分 100；输入泄漏审查结论 |
| `software/` | 运行软件 | 任务运行需要的解释器或工具说明 |

### 0.3 任务说明写到什么程度

`task_brief.md` 只写 Agent 需要知道的四件事。

1. 场景和角色。你在什么机构，处理什么案件。
2. 输入范围。只能读 `base/input` 下的材料，闭卷。
3. 要做什么。对 5 个案件计算机构费和仲裁员报酬。
4. 交付什么。写到 `output/arbitration_fee_results.json`，字段名和两位小数写死。

它不写“先读哪份 PDF，再算什么”，也不给公式答案。步骤由 Agent 自己规划，判断由 Agent 自己做。这是 ALE 任务和“操作手册”的区别。

### 0.4 输出合同写到什么程度

`output_contract.json` 把交付物写死到机器能校验。

- 根对象必须有 `cases`。
- `cases` 是数组，长度 5。
- 每个元素有 `case_id`、`institution_fee_rmb`、`arbitrator_remuneration_rmb`、`total_fee_rmb`。
- 金额是数字，保留两位小数。
- 示例形状给出一个合法对象。

专家写任务源时，`deliverables` 块就要写到这个程度。不是“一份 JSON”，而是路径、字段、类型、精度、示例。

### 0.5 金标和验证怎么分开

`reference/answer_key.json` 写答案、权重和容差。它不在 `input/` 里，Agent 看不到。

`reference/stage1_manifest.json` 写验证结果。正例得分 1.0，负例得分 0.0，满分 100。它还写输入泄漏审查结论。

> input contains source PDFs, case facts, output schema, and runtime manifest only; no gold fee values or scoring code.

这句话是标准动作。提交前要自己检查一遍。输入里不能有答案、评分代码、金标痕迹。

### 0.6 这份包为什么是合格任务

- 有真实材料。7 份 PDF，不是一段编造的案例。
- 有真实摩擦。案件事实、金额、和解条件分散在多份文件里，需要交叉核对。
- 有多步判断。先读任务，再读案件，再找费率规则，再算机构费和报酬，再检查总额。
- 有精确交付物。一个 JSON，5 个案件，4 个字段，两位小数。
- 有可复现判定。答案、权重、容差、正负 fixture 都写死。
- 有泄漏审查。输入和答案分开。

### 0.7 映射到我们的十块任务源

| 官方包 | 作用 | 我们的十块 | 工程 Harbor 包 |
|---|---|---|---|
| `task_brief.md` | 指令和约束 | identity + scenario | `instruction.md` |
| `documents/` + `document_manifest.json` + `cases.json` | 输入和事实 | materials | `input/` 或 environment 挂载 |
| `output_contract.json` | 交付物合同 | deliverables | `instruction.md` 的 artifacts 段 + 验证器 |
| `answer_key.json` | 金标、权重、容差 | success_criteria + review | `solution/` + `tests/` |
| `runtime_env/` + `software/` | 环境 | environment | `environment/` |
| `stage1_manifest.json` | 验证与泄漏审查 | review + provenance | `tests/` + `metadata` |

### 0.8 映射到 Harbor 包

工程最终会把你的任务源转成 Harbor 1.4 + ALE 扩展格式。

| Harbor 文件 | 从哪来 | 谁写 |
|---|---|---|
| `task.toml` | 环境、超时、artifacts、验证器配置 | 工程 |
| `instruction.md` | 你的 scenario + 交付物要求 | 工程基于你的任务源定稿 |
| `input/` | 你的 materials | 工程打包 |
| `environment/` | 你的 environment | 工程 |
| `tests/` | 你的 success_criteria | 工程写验证器 |
| `solution/` | 你的金标答案 | 工程封装 |

专家不写这些文件。专家要把十块写到工程能直接转的程度。

### 0.9 不要照抄什么

- 不要照抄法律内容、案件金额、费率规则。
- 不要照抄官方任务的正文、答案或评分代码。
- 不要以为每条任务都必须长成法律任务。结构和分离方式要学，领域内容要是你自己的。
- 不要用简化的小数据替代真实材料。三份角色样例是应用练习，不是难度上限。

## 样例一：商业会计——从两家年报到可复算的收入与应收勾稽

> 这是一份应用练习。它展示怎么把第 0 节的结构落到会计领域。正式生产要按 02a 的难度门槛，把材料、步骤、判断点和交付物扩到 50+ 步、10–20 份材料的规模。

### 1. 起点资料

- 两家公开制造业公司 A/B 的 2022–2024 年报，取自交易所公告页或公司投资者关系页；记录 URL、下载日、版本。
- 合成总账：12 个科目、4 个季度，含科目编码、期初/期末余额、借方/贷方发生额、币种、单位。
- 公开行业说明：行业协会或统计部门发布的营收、应收周转区间，用于判断异常是否行业性。
- 全部合成件用“A 公司/B 公司”代称，不映射真实主体；公开年报只摘取完成任务所需的报表页与附注页。

### 2. 怎么找到任务

先读三年报表，做三个判断：

1. 收入增速与应收账款增速是否背离。收入涨、应收涨得更快，可能意味着放宽信用或提前确认。
2. 经营现金流是否跟上收入。利润增长但经营现金流下降，说明增长质量要打问号。
3. 合同负债、应收周转天数、收入确认政策是否在三年内变了。口径变了，趋势就不可比。

任务因此定为：**“用两家公司三年年报做收入与应收勾稽，标出 3 条异常，写清事实、可能原因和还缺什么证据”**，不是“分析财报”，也不是“给投资建议”。

淘汰的候选：
- “做 DCF 估值”——需要预测与折现假设，超出资料，也容易变成投资建议。
- “审计全部 12 个科目”——范围太大，一条任务做不完，判断点不集中。

### 3. 拆步骤

| 步 | 动作 | 判断点 | 产物 |
|---|---|---|---|
| 1 | 抽取年报报表页与附注页 | 合并口径、币种、单位、重述 | `source_index.csv` |
| 2 | 建收入—应收桥 | 收入、应收、合同负债、经营现金流 | `revenue_bridge.csv` |
| 3 | 算三年趋势与应收周转天数 | 期末还是平均应收；天数口径 | `trend.csv` |
| 4 | 对合成总账做 12 科目勾稽 | 期初 + 发生额 = 期末；差异阈值 | `gl_diff.csv` |
| 5 | 选 3 条异常，写事实—可能原因—证据缺口 | 哪些能下结论，哪些不能 | `exceptions.csv` |
| 6 | 写 memo，分事实/推断/建议 | 不把推断写成事实 | `memo.md` |

专业难点：同一个“收入增长”，可能来自销量、价格、并表、汇率或提前确认；任务要逼专家把口径和证据分开。

### 4. 十块怎么填

**identity**
> `FIN-ACC-014` 用两家制造业公司 2022–2024 年报，做收入与应收账款勾稽并写 3 条异常说明
> 领域 business_finance / accounting；难度中；预计 16 小时；交付 Excel + CSV + Markdown。

**scenario**
> 你是某集团财务分析岗。CFO 周五要听两家同行业公司的增长质量，只给你公开年报和一份合成总账，要求你判断收入增长是否有应收和现金流支撑。你不能下投资建议，也不能假设拿得到管理层数据；没有把握的地方标“需补充证据”。

**materials**

| id | 文件 | 来源 | 许可 | 用途 |
|---|---|---|---|---|
| M1 | `company_a_2022_2024_annual.pdf` | 交易所公告 | 公开披露 | A 公司报表与附注 |
| M2 | `company_b_2022_2024_annual.pdf` | 交易所公告 | 公开披露 | B 公司报表与附注 |
| M3 | `gl_synthetic_2024.xlsx` | 合成 | 项目自制 | 12 科目勾稽 |
| M4 | `industry_note.md` | 行业协会 | 公开 | 行业口径参考 |

每个文件标 SHA-256；M1/M2 标页码与下载日；M3 标“合成，不映射真实主体”。

**operations**
1. 用 `pdftotext -layout` 抽取 M1/M2，保存到 `work/`；记录页数并与原文核对。
2. 建 `revenue_bridge.csv`：`company,year,revenue,ar,contract_liability,ocf,ar_days`。
3. 计算 2022–2024 收入增速、应收增速、经营现金流增速；标出收入与应收增速差 >10 个百分点的年份。
4. 读 M3，按科目映射表核对 12 个科目：期初 + 借方 − 贷方 = 期末；差异 >5% 进异常池。
5. 从趋势和勾稽里选 3 条异常，每条写“事实—可能原因—还缺什么证据”，不直接下结论。
6. 写 memo：先事实，再推断，最后建议；建议只写“下一步查什么”，不写买卖。
7. 用 `openpyxl` 保留公式与源单元格引用；另存一份 CSV 证据。

**deliverables**

| 文件 | 格式 | 必需内容 |
|---|---|---|
| `output/reconciliation.xlsx` | XLSX | sources、mapping、diff、formulas 四个 sheet |
| `output/exceptions.csv` | CSV UTF-8 | `exception_id,company,year,fact,possible_cause,evidence_gap` |
| `output/memo.md` | Markdown | 事实、推断、建议、限制 |

**success_criteria**
- 两家公司 3 年的收入、应收、经营现金流都能追到年报页码。
- 应收周转天数公式一致；用期末还是平均应收写清楚。
- 12 个科目全部有期初、发生额、期末；差异为 0，或 >5% 有解释。
- 3 条异常都有事实、可能原因、证据缺口；缺一项即失败。
- 全文不出现投资建议、目标价、评级；出现即失败。
- 随机抽 3 个数字，能在年报页码或 Excel 单元格里复算。

**environment**
> Ubuntu 22.04 / x86_64；4 vCPU、8 GB RAM、20 GB 磁盘；Python 3.11、pandas 2.2、openpyxl 3.1、LibreOffice；完全离线；无 GUI/GPU；预计 20 分钟。

**review**
> 风险中。需人工看：合并口径与重述、收入确认政策、币种与单位、应收是否含并表。评审问题：如果应收增长主要来自并表，原来的“增长质量”结论是否还成立？

**provenance**
> M1/M2 公开年报，记录 URL、下载日、报表页；M3 项目合成，作者专家，不映射真实主体；M4 行业协会公开说明；未使用客户底稿、MNPI 或个人信息。

**handoff**
> 包内：`task_source.json`、`materials/`（4 文件，25 MB）、`output/`（3 文件）、`run.md`。已知限制：只有公开报表，没有管理层数据；未决：并表范围是否影响应收口径，需补充附注。

### 5. 成功标准与证据怎么对应

| 标准 | 检查方法 | 证据 |
|---|---|---|
| 数字可追源 | 随机 3 个数字对年报页码/单元格 | `source_index.csv` + Excel 公式 |
| 勾稽可复算 | 期初 + 借方 − 贷方 = 期末 | `gl_diff.csv` |
| 趋势口径一致 | 检查三年币种、单位、合并范围 | `revenue_bridge.csv` |
| 异常三段齐全 | 每条异常有事实/原因/证据缺口 | `exceptions.csv` |
| 不越界 | 搜“买入/卖出/目标价/评级” | `memo.md` |

### 6. 评审会问什么

1. 为什么用应收周转天数，而不是直接看应收/收入比？
2. 收入增长里有多少来自并表或汇率？你怎么排除？
3. 为什么选这 3 条异常，而不是另外 3 条？
4. 合成总账的科目映射是谁定的？会不会循环论证？
5. 如果公司变更了收入确认政策，三年趋势还可比吗？

### 7. 最容易失败的地方

1. 把收入增长直接当增长质量，不看应收和现金流。
2. 合并/母公司口径混用，币种或单位不统一。
3. 应收周转天数用期末数还是平均数不说清。
4. Excel 公式被值覆盖，无法复算。
5. 异常只写“可能有问题”，没有证据缺口。
6. memo 写成投资建议，超出任务边界。

## 样例二：神经影像——从合成 DICOM 到可验证的 BIDS 目录

> 这是一份应用练习。正式生产按 02a 的难度门槛，把材料、步骤、判断点和交付物扩到 50+ 步、10–20 份材料的规模。

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

> 这是一份应用练习。正式生产按 02a 的难度门槛，把材料、步骤、判断点和交付物扩到 50+ 步、10–20 份材料的规模。

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

## 三份试点样例的共同结构

| 环节 | 商业会计 | 神经影像 | 建筑节能 |
|---|---|---|---|
| 起点 | 两家公开年报 + 合成总账 | 合成 DICOM | 公开示例模型 + 合成账单 |
| 任务种子 | 收入/应收背离 + 12 科目勾稽 | 四类 BIDS 错误 | 基线校准 + 单变量改造 |
| 核心判断 | 口径/期间/单位/并表 | 字段来源与方向 | 边界/单位/校准 |
| 证据 | 页码 + 公式 + 差异表 | validator 日志 + QC 图 | 模型文件 + 可重算 CSV |
| 最大失败 | 把增长当质量 | 只改文件名 | 边界不一致 |

三份都遵守同一条：**任务不是“做一个专业动作”，而是“在约束下做出一套别人能检查的交付物”**。三份都是应用练习，不是难度上限。正式生产按 02a 的 50+ 步、10–20 份材料、模型试做得分 ≤40 执行。

## 附录：法律供应方包检查（不占试点位）

法律 42 条不经过专家任务源、评审和冻结全流程，由供应方按 ALE-data 提供，走 `import -> 基础校验 -> 转 Harbor`。专家手册不要求写法律任务源；本节只给平台和工程做供应方包检查。

- 包结构：`base/input/task_brief.md`、`output_contract.json`、`document_manifest.json`、`cases.json`、`documents/`、`runtime_env/`。
- 基础校验：文件存在、JSON 可解析、引用路径可解析、哈希与清单一致、无真实当事人信息。
- 内容抽检：按 `04` 第 1 节的引证、程序、匿名化、争点—证据对应检查；基础校验过不了内容审核。
- 供应方仍要出专业背书、资料授权与脱敏说明；合作方接受供应方包才计入 500。
