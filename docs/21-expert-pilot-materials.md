# 专家试点材料包

本文件是 ALE 500 专家试点的配套材料，包含项目说明一页版、一条可直接改写的示范任务、两条不合格示例、专业审核清单、T1 人工基线记录模板、T2 平台辅助记录模板和试点反馈表。示范任务为原创合成案例，不复制官方 122 条任务，也不包含任何客户真实数据。本文件只讲内容、操作和记录，不涉及商务或结算安排。

材料的使用顺序是：培训时先读项目说明，再用示范任务走一遍字段，然后用不合格示例做审核练习，最后用记录模板和反馈表收集试点证据。示范任务只示范“怎样算合格”，不要求专家照抄题目；专家应按自己的方向写同等工作量的原创任务。

## 1. 项目说明一页版

以下内容用于试点启动和培训开场，控制在一页内，讲清项目、试点、交付、边界和时间。

### 1.1 项目是什么

ALE 500 为 Agents' Last Exam 评测集生产 500 条原创专业工作任务。每条任务是一段可运行、可评测、可复现的专业工作，不是问答，也不是把教科书习题换个说法。任务要有真实资料、执行环境、多步操作、明确交付物和可判定的成功标准。

官方已有的 122 条任务不计入 500，三条试点线也不计入 500。试点是能力探索，用来检验专家人工标注、平台辅助和 Agent 建议是否可用，不承担 500 条的配额验证。

### 1.2 试点做什么

试点从 2026-11-18 到 2026-12-30，三条方向并行：商业会计对账、神经影像 DICOM 转 BIDS、建筑能耗基线。每条方向做 T1 人工基线和 T2 平台辅助两个实例，共 6 个任务实例。T1 与 T2 使用同一题族的不同实例，间隔至少 3 个工作日。

T1 在平台外完成，记录人工过程、用时和卡点。T2 在平台内完成，记录平台辅助后的用时、自动检查、评审返修和 Agent 建议处理情况。试点只使用公开数据或合成资料，不接触真实客户材料。

### 1.3 专家交付与合格线

每条任务交付一份规范任务源，包含任务身份、场景、资料、步骤、交付物、成功标准、环境、审核、来源、交接十个块。合格线是：真实工作流、至少 3 步、至少 1 个真实工具、至少 1 个专业判断、至少 1 个必观测交付物、成功标准可验证且权重合计 100。

专家还要提交实际用时、卡点、证据和反馈。任务组织参考工时为 28 小时，平台辅助目标为 22 小时；这是任务级排期参考，不是个人工作量承诺，也不作为个人考核依据。

### 1.4 边界与保密

试点不写 Dockerfile、不写 Verifier、不拼运行包，也不做 Harbor 转换和正式评测。资料必须是公开或合成的；客户合同、真实流水、病历、员工记录和未脱敏个人信息不能进入试点。答案和评分依据放 `reference`，不能放 `input`。

平台当前是本地演示形态，没有正式 TLS、密码重置、资料删除和工单页面。这些功能当前版本不可用，相关事项走项目组指定的书面支持渠道。

### 1.5 时间与联系

第 1 周完成签约、培训、范围冻结和账号准备；第 2 至 3 周做 T1；第 4 至 5 周做 T2；第 6 周组包校验；第 7 周收口。具体日期以项目组通知为准。支持渠道、响应时限和培训安排由项目组在试点启动时书面确认。

## 2. 示范任务：商业会计对账

示范任务按平台十块任务源完整写出，专家可以按自己的方向替换领域、资料和数值，但保留同样的工作量和验证结构。

### 2.1 任务概览

这是一条原创合成任务，题族是月度银行流水与总账对账。任务要求被评 Agent 读取两份合成 CSV 和一份对账政策，完成控制总额核对、交易匹配、异常分类、调整桥和差异报告。所有金额、凭证号、交易号和组织名称都是虚构的，不对应任何真实客户。

| 项目 | 内容 |
|---|---|
| 任务 ID | business_finance/accounting_reconcile_demo_01 |
| 中文标题 | 月度银行流水与总账对账及差异报告 |
| 英文标题 | Monthly Bank-to-Ledger Reconciliation and Exception Report |
| 领域与子域 | business_finance / accounting |
| 难度 | 中等；需要跨表匹配、重复识别、异常分类和调整桥 |
| 主要工具 | Python 3.11、pandas 2.1.4、文本编辑器 |
| 交付物 | 对账报告、异常清单 CSV、对账摘要 JSON |
| 资料性质 | 全部合成，PII 为 none，许可为 synthetic |

### 2.2 完整任务源

以下按 canonical 任务源的十个块展示字段。文件路径、SHA-256 和字节数在上传时由平台写入；示例里的 `PLATFORM_FILLED` 和 `0` 是占位，不是让专家手填的值。任务源正文用英文，便于后续生成 ALE-data 包。

```yaml
identity:
  task_id: business_finance/accounting_reconcile_demo_01
  version: 1
  domain_code: business_finance
  subdomain_code: accounting
  title_zh: 月度银行流水与总账对账及差异报告
  title_en: Monthly Bank-to-Ledger Reconciliation and Exception Report
  language: en
  batch_id: w1-demo
  owner_expert_id: pilot_expert_01
  difficulty_rationale: >-
    The task requires control-total verification, duplicate detection,
    exception classification across two sources, and an adjustment bridge.
    A single lookup or a summary of the files cannot produce the deliverables.

scenario:
  role: Staff accountant at a fictional wholesale distributor
  organization_context: >-
    Northwind Supplies is a fictional wholesale distributor with a small
    finance team. The September 2026 close is three days away, and the
    ledger export and the bank statement have already been downloaded.
  trigger: >-
    The finance manager asks for a reconciled bank-to-ledger package before
    the month-end close meeting.
  audience: Finance manager and external auditor, read-only
  constraints:
    - Use only the files under input/.
    - Do not modify or delete source rows; list every exclusion.
    - Match on amount and normalized reference, allowing a posting date
      difference of up to three business days.
    - Report all amounts in CNY with exactly two decimal places.
  out_of_scope:
    - Do not file tax returns or post adjusting entries to the ERP.
    - Do not contact the bank or infer missing statements.
  realism_evidence: >-
    The workflow follows a standard month-end bank reconciliation procedure.
    All parties, accounts, references and amounts are synthetic.

materials:
  - material_id: M-001
    kind: dataset
    role: input
    path: input/SYNTHETIC_ledger_2026-09.csv
    sha256: PLATFORM_FILLED
    bytes: 0
    license:
      type: synthetic
      redistribution: true
    pii_level: none
    used_by:
      - "1"
    synthetic_disclosure: Synthetic ledger, no real customer data.
  - material_id: M-002
    kind: dataset
    role: input
    path: input/SYNTHETIC_bank_2026-09.csv
    sha256: PLATFORM_FILLED
    bytes: 0
    license:
      type: synthetic
      redistribution: true
    pii_level: none
    used_by:
      - "1"
    synthetic_disclosure: Synthetic bank statement, no real customer data.
  - material_id: M-003
    kind: document
    role: input
    path: input/SYNTHETIC_reconciliation_policy.md
    sha256: PLATFORM_FILLED
    bytes: 0
    license:
      type: synthetic
      redistribution: true
    pii_level: none
    used_by:
      - "1"
    synthetic_disclosure: Synthetic reconciliation policy.
  - material_id: M-004
    kind: dataset
    role: reference
    path: reference/SYNTHETIC_expected_reconciliation.json
    sha256: PLATFORM_FILLED
    bytes: 0
    license:
      type: synthetic
      redistribution: true
    pii_level: none
    used_by:
      - "5"
    synthetic_disclosure: Synthetic answer key, not visible to the evaluated agent.

operations:
  - step_no: 1
    actor: human
    action: >-
      Inspect the two CSV files and the policy note; record row counts and
      control totals before matching.
    tool: Python 3.11 with pandas 2.1.4
    inputs:
      - M-001
      - M-002
      - M-003
    expected_state: >-
      Ledger has 120 rows and bank has 119 rows; ledger total is 486445.00
      and bank total is 486333.40.
    checkpoint: true
    time_estimate_min: 15
  - step_no: 2
    actor: human
    action: >-
      Normalize dates to ISO format, strip currency symbols, trim references,
      and reject rows with missing required columns.
    tool: Python 3.11 with pandas 2.1.4
    inputs:
      - M-001
      - M-002
    expected_state: >-
      All 239 rows have valid dates and two-decimal amounts; no source row is
      silently dropped.
    checkpoint: true
    time_estimate_min: 20
  - step_no: 3
    actor: human
    action: >-
      Match ledger entries to bank transactions on amount and normalized
      reference, allowing a posting date difference of up to three business
      days.
    tool: Python 3.11 with pandas 2.1.4
    inputs:
      - M-001
      - M-002
    expected_state: >-
      Exactly 117 pairs match and the matched amount total is 486240.00.
    checkpoint: true
    time_estimate_min: 30
  - step_no: 4
    actor: human
    action: >-
      Classify each unmatched item as duplicate posting, outstanding check,
      bank fee, or interest; do not net items against each other.
    tool: Python 3.11 with pandas 2.1.4
    inputs:
      - M-001
      - M-002
      - M-003
    expected_state: >-
      Five exceptions are listed: three ledger-only items and two bank-only
      items, each with a signed amount and a recommended action.
    checkpoint: true
    time_estimate_min: 25
  - step_no: 5
    actor: human
    action: >-
      Write the reconciliation report, the exception CSV and the summary
      JSON; prove that adjusted ledger and adjusted bank both equal 485813.40.
    tool: Text editor and Python 3.11
    inputs:
      - step 4 exception register
    expected_state: >-
      Three deliverables exist at the declared paths, both adjusted balances
      equal 485813.40, and the residual difference is 0.00.
    checkpoint: true
    time_estimate_min: 20

deliverables:
  - deliverable_id: D-001
    path: output/reconciliation_report.md
    format: md
    description: >-
      Report with six sections: scope and sources, control totals, method and
      tolerances, exception register, adjustment bridge, conclusion and
      residual. Include the preparer role and the report date.
    produced_by_step: 5
    mandatory: true
    acceptance_ref:
      - C-001
      - C-002
      - C-004
      - C-005
  - deliverable_id: D-002
    path: output/unmatched_items.csv
    format: csv
    description: >-
      One row per exception with columns item_id, source, reference, amount,
      exception_type, recommended_action, owner. Amounts are signed and have
      two decimals.
    produced_by_step: 5
    mandatory: true
    acceptance_ref:
      - C-001
      - C-003
      - C-004
  - deliverable_id: D-003
    path: output/reconciliation_summary.json
    format: json
    description: >-
      Summary with ledger_rows, bank_rows, matched_pairs, exception_count,
      ledger_total, bank_total, adjusted_ledger_total, adjusted_bank_total
      and residual.
    produced_by_step: 5
    mandatory: true
    acceptance_ref:
      - C-001
      - C-002
      - C-003

success_criteria:
  - criterion_id: C-001
    dimension: correctness
    check_method: auto_script
    weight: 30
    threshold: >-
      matched_pairs equals 117, matched total equals 486240.00, and the
      exception set equals the five expected item IDs and signed amounts.
    evidence_required: output/unmatched_items.csv and output/reconciliation_summary.json
    verifier_hint: >-
      Recompute the match from the two input files and compare sets, not row
      order.
    critical: true
  - criterion_id: C-002
    dimension: completeness
    check_method: artifact_diff
    weight: 25
    threshold: >-
      The report contains all six required sections, both adjusted balances
      equal 485813.40, and the residual is 0.00.
    evidence_required: output/reconciliation_report.md and output/reconciliation_summary.json
    verifier_hint: >-
      Check section headings and required numeric fields against the reference.
    critical: true
  - criterion_id: C-003
    dimension: format
    check_method: auto_script
    weight: 15
    threshold: >-
      CSV header is exactly the seven declared columns, JSON parses, all
      amounts have two decimals, and the report is valid UTF-8 Markdown.
    evidence_required: all three deliverables
    verifier_hint: Parse each file and compare the schema.
    critical: false
  - criterion_id: C-004
    dimension: professional_judgment
    check_method: human_rubric
    weight: 20
    threshold: >-
      All five exceptions have the correct type and a specific recommended
      action; no item is netted against another.
    evidence_required: output/unmatched_items.csv and the exception section of the report
    critical: false
  - criterion_id: C-005
    dimension: process
    check_method: human_rubric
    weight: 10
    threshold: >-
      Control totals 486445.00 and 486333.40 are shown, both adjusted
      balances are reproducible, and every excluded row has an explanation.
    evidence_required: report method section and the matching script or command log
    critical: false

environment:
  os: linux
  os_version: Ubuntu 22.04
  gui_required: "no"
  gpu:
    required: false
  software:
    - name: Python
      version: 3.11.8
      license_type: PSF-2.0
      install_method: preinstalled
    - name: pandas
      version: 2.1.4
      license_type: BSD-3-Clause
      install_method: preinstalled
  network:
    mode: none
  resources:
    cpu: 2
    ram_gb: 4
    disk_gb: 20
    time_limit_min: 120
  nested_virt: false
  external_services: []

review:
  risk_tier: medium
  tier_rationale: >-
    The data is synthetic and contains no PII, but the task depends on
    professional judgment in duplicate detection and exception classification.
  required_reviewers:
    - role: domain_reviewer
      count: 1
    - role: quality_reviewer
      count: 1
  reviews: []
  sign_offs: []
  open_issues: []

provenance:
  author_type: human
  agent_runs: []
  sources:
    - source_id: S-001
      url_or_path: synthetic://pilot/accounting_reconcile_demo_01
      note: Synthetic files created for the pilot.
  originality:
    not_copied: true
  revision_history:
    - version: 1
      date: "2026-11-20"
      change: Initial pilot draft.

handoff:
  target_format: ale_task_toml
  target_schema_version: "1.4+ale.1"
  files_expected:
    - output/reconciliation_report.md
    - output/unmatched_items.csv
    - output/reconciliation_summary.json
  known_gaps: >-
    No ERP export, no tax filing, and no bank API. The task covers
    reconciliation and reporting only.
  execution_notes: >-
    Python and pandas are preinstalled. The output/ directory is empty at
    start. No network access is required.
  secrets_attestation: true
```

### 2.3 输入资料说明

所有文件都是合成的。文件名加 `SYNTHETIC_` 前缀，任务源和资料说明都标注“不含真实客户数据”。金额、凭证号、交易号、组织名称均为虚构。

| ID | 文件 | 角色 | 内容 | 为什么需要 | 许可与 PII |
|---|---|---|---|---|---|
| M-001 | input/SYNTHETIC_ledger_2026-09.csv | input | 120 行总账分录，列是 entry_id、posting_date、account_code、description、debit、credit、reference | 提供待对账的账务侧数据，含两笔重复入账和一笔未兑现支票 | synthetic，none |
| M-002 | input/SYNTHETIC_bank_2026-09.csv | input | 119 行银行交易，列是 transaction_id、value_date、description、amount、reference | 提供银行侧数据，含手续费和利息两笔未入账项目 | synthetic，none |
| M-003 | input/SYNTHETIC_reconciliation_policy.md | input | 一页对账政策，写匹配字段、日期容差、异常分类和报告结构 | 让判断标准可复现，避免专家口径变成隐含知识 | synthetic，none |
| M-004 | reference/SYNTHETIC_expected_reconciliation.json | reference | 期望的匹配数、异常清单、总额和调整后余额 | 供脚本复核和评审对照，不进入被评 Agent 可见输入 | synthetic，none |

数据设计。总账 120 行，其中 117 行与银行 119 行中的 117 行一一匹配，匹配金额合计 486,240.00。总账另有 2 笔重复入账，金额为 420.00 和 305.00；另有 1 笔未兑现支票，金额为 -520.00。银行另有 1 笔手续费 -35.00 和 1 笔利息 128.40。总账合计 486,445.00，银行合计 486,333.40。

调整桥。总账调整后余额 = 486,445.00 - 420.00 - 305.00 - 35.00 + 128.40 = 485,813.40。银行调整后余额 = 486,333.40 - 520.00 = 485,813.40。两边相等，残余差异为 0.00。

五条异常的具体值。

| 异常 ID | 来源 | 参考号 | 金额 | 类型 | 建议动作 |
|---|---|---|---|---|---|
| E-001 | ledger | INV-2026-0914 | 420.00 | duplicate posting | 冲销重复分录并保留原始凭证 |
| E-002 | ledger | INV-2026-0921 | 305.00 | duplicate posting | 冲销重复分录并核对发票 |
| E-003 | ledger | CHK-10482 | -520.00 | outstanding check | 列入未兑现支票清单，下月跟踪 |
| E-004 | bank | BANK-FEE-0930 | -35.00 | bank fee | 补记手续费并取得银行回单 |
| E-005 | bank | INT-0930 | 128.40 | interest | 补记利息收入并复核计提 |

资料设计要避免答案泄漏。`M-004` 是 reference，平台不会把它放进被评 Agent 的 `base/input`。`M-001` 到 `M-003` 只包含原始数据和规则，不包含期望异常清单、调整后余额或评分脚本。

### 2.4 交付物

| ID | 路径 | 格式 | 必须包含的内容 | 产出步骤 |
|---|---|---|---|---|
| D-001 | output/reconciliation_report.md | md | 范围与来源、控制总额、方法与容差、异常登记表、调整桥、结论与残余差异六节；写明编制角色和日期 | 5 |
| D-002 | output/unmatched_items.csv | csv | 表头 item_id,source,reference,amount,exception_type,recommended_action,owner；5 行数据；金额带符号和两位小数 | 5 |
| D-003 | output/reconciliation_summary.json | json | ledger_rows、bank_rows、matched_pairs、exception_count、ledger_total、bank_total、adjusted_ledger_total、adjusted_bank_total、residual 九个键 | 5 |

交付物路径全部是相对路径，以 `output/` 开头，不使用 `../` 和绝对路径。三个文件的路径要和任务源、成功标准和交接里的文件清单逐字一致。

### 2.5 成功标准与验证依据

五条标准的权重是 30、25、15、20、10，合计 100。C-001 和 C-002 是关键标准，任一不通过则整条任务不通过。

验证分两层。第一层是脚本，读取 `M-001`、`M-002` 和三个交付物，重算匹配集合、异常集合、总额和调整后余额，检查 CSV 表头、JSON 键和金额格式。第二层是人工评分表，检查异常分类是否专业、建议动作是否具体、控制总额和排除项是否有解释。

人工评分表按四档执行。

- 4 分：五条异常分类全部正确，建议动作具体，可直接执行，未净额抵销。
- 3 分：四条异常分类正确，建议动作基本可执行，未净额抵销。
- 2 分：三条异常分类正确，或有两处建议动作空泛。
- 1 分：两条及以下分类正确，或把异常净额抵销后给出结论。

C-004 的通过线是至少 4 分。C-005 的通过线是控制总额、调整桥和排除说明都能从输入复算，且没有未解释的源数据改动。

这条任务不依赖外部网站、在线银行、ERP 或客户系统。所有数值都能从合成输入重算，reference 只用于复核，不进入可见输入。验证脚本不读取 reference 之外的隐藏信息，评审人可以用同一份 reference 复算。

### 2.6 这条示范任务为什么合格

- 真实工作流：月末对账是会计岗位的常规工作，有明确触发、受众和截止时间。
- 多步操作：资料核对、规范化、匹配、异常分类、报告和调整桥，共 5 步，有依赖关系。
- 真实工具：Python、pandas 和文本编辑器，版本和安装方式写清，离线可运行。
- 专业判断：重复入账、未兑现支票、手续费和利息的分类，以及建议动作，不能靠格式检查代替。
- 必观测交付物：三个文件有固定路径、格式和内容要求，能被脚本和人工同时检查。
- 可验证标准：匹配数、异常集合、总额、调整后余额和残余差异都有确定值，权重合计 100，至少一条关键标准。
- 资料可授权：全部合成，许可清楚，PII 为 none，答案在 reference。
- 不与官方重复：题目、数据、金额和异常均为本次试点原创，不复制官方 122 条。

## 3. 两条不合格示例

两条示例分别代表问答化和真实数据依赖两种常见失败，培训时可以先用它们做退回练习，再对照示范任务。

### 3.1 示例一：问答化、单步化

任务描述：请解释银行对账为什么重要，并写三点对账建议。要求语言通顺、观点正确。

问题解释。

- 这是问答题，不是工作任务；没有组织情境、触发事件和受众。
- 没有输入资料，没有工具，没有多步操作，也没有交付物路径。
- 成功标准是“语言通顺、观点正确”，无法判定，也没有权重和证据。
- 没有专业判断点，模型可以直接凭常识作答，测不到工具使用和资料处理。
- 没有许可和 PII 记录，无法进入 ALE-data 包。

改法。把它改成一条真实对账任务：给出合成总账和银行流水，要求匹配、分类异常、写报告和调整桥，用确定数值和异常集合判定。示范任务就是改写后的形态。

### 3.2 示例二：真实客户数据、在线系统、答案泄漏

任务描述：登录公司网银，导出 2026 年 9 月真实客户流水，与总账对账，把标准答案放在 input/answer.xlsx 里方便核对。要求使用公司 ERP 和网银账号，结果直接发财务经理邮箱。

问题解释。

- 使用真实客户流水，没有授权、许可和 PII 记录，违反试点保密边界。
- 依赖在线网银和公司 ERP，需要账号、口令和外部服务，环境不可复现。
- 把标准答案放在 `input/`，被评 Agent 可以直接读取，任务失效。
- 没有说明数据脱敏、保存期限和删除方式，存在合规风险。
- 交付方式写成发邮件，不是可检查的文件交付物，无法自动验证。
- 成功标准缺失，无法判断对账是否完成。

改法。改用合成流水和合成总账；把答案放 `reference`，不进入可见输入；环境改成离线，工具和版本写清；交付物改成固定路径的报告、CSV 和 JSON；删除真实客户信息、网银账号和邮件交付。

### 3.3 不合格形态对照表

| 形态 | 典型表现 | 后果 | 修正方向 |
|---|---|---|---|
| 问答化 | “解释”“说明”“写三点建议” | 测不到工具和多步工作 | 改成有资料、有产物的任务 |
| 单步化 | 一步查表或一次计算就完成 | 难度不足，无法观察过程 | 拆出核对、处理、验证步骤 |
| 只考格式 | 标准只检查文件存在和扩展名 | 专业判断没有被测 | 增加正确性、完整性和判断标准 |
| 验证器测不到目标 | 标准写“合理”“基本正确” | 无法判定，评审争议 | 改成数值、集合、字段或评分表 |
| 资料不可授权 | 客户数据、受限数据库、来源打不开 | 不能入库，合规风险 | 换公开或合成资料 |
| 答案泄漏 | 答案、评分脚本放在 input | 任务失效 | 移到 reference，检查可见输入 |
| 实时外部源 | 依赖网银、ERP、网站当天数据 | 不可复现，环境不稳定 | 改为离线快照或合成数据 |
| 工具不可用 | 写“最新版”“运行期下载” | 环境无法构建 | 写明确版本和安装方式 |
| 角色泛化 | “专业人士”“专家” | 场景不真实，判断无边界 | 写具体岗位和组织情境 |
| 标准不可判定 | 没有权重、没有关键标准、阈值含糊 | 不能通过自动检查 | 权重合计 100，至少一条关键标准 |

## 4. 专业审核清单

清单覆盖专业真实性、任务契约一致、资料可授权、交付物可验证、难度与工作量和重复与泄漏六个维度，供领域评审和质量审核共用。

### 4.1 使用方式

领域评审人和质量审核人逐项判定。平台评审页当前只提供“通过”和“退回返修”两个按钮；拒收、升级和边界不清的事项由评审人通过支持渠道提交，不在评审页操作。任何一项标为阻断时，不能写“通过但备注”。专家不评自己的任务，同一对评审人不连续互评。

### 4.2 六维检查表

| 维度 | 序号 | 检查项 | 判定 |
|---|---|---|---|
| 专业真实性 | 1 | 角色是具体岗位，不是“专业人士” | 通过 / 阻断 |
| 专业真实性 | 2 | 组织情境、触发事件和受众构成真实工作 | 通过 / 阻断 |
| 专业真实性 | 3 | 工具是真实工具，版本和安装方式可复现 | 通过 / 阻断 |
| 专业真实性 | 4 | 至少一个专业判断点，不能靠格式或常识替代 | 通过 / 阻断 |
| 专业真实性 | 5 | 工作流与岗位实际做法一致，没有编造步骤 | 通过 / 阻断 |
| 契约一致 | 6 | 标题、场景、步骤、交付物和标准指向同一条工作 | 通过 / 阻断 |
| 契约一致 | 7 | 交付物路径是相对路径，与标准、交接逐字一致 | 通过 / 阻断 |
| 契约一致 | 8 | 每个交付物有产出步骤，每个步骤有输入和预期状态 | 通过 / 阻断 |
| 契约一致 | 9 | 权重合计 100，至少一条关键标准，阈值可判定 | 通过 / 阻断 |
| 契约一致 | 10 | 环境、软件、网络和资源与步骤实际需要一致 | 通过 / 阻断 |
| 资料可授权 | 11 | 每份资料有许可、来源和 PII 记录 | 通过 / 阻断 |
| 资料可授权 | 12 | 至少一份 input，合成件已标注，文件名可识别 | 通过 / 阻断 |
| 资料可授权 | 13 | 客户数据、未脱敏高危 PII、受限资料没有进入 | 通过 / 阻断 |
| 资料可授权 | 14 | 答案、评分脚本和隐藏测试只在 reference | 通过 / 阻断 |
| 资料可授权 | 15 | 来源可打开、可追溯，没有“先用后补” | 通过 / 阻断 |
| 交付物可验证 | 16 | 每个交付物有路径、格式、结构和验收对应 | 通过 / 阻断 |
| 交付物可验证 | 17 | 自动检查能测到正确性和完整性，不只是文件存在 | 通过 / 阻断 |
| 交付物可验证 | 18 | 人工评分表有维度、等级和判分边界 | 通过 / 阻断 |
| 交付物可验证 | 19 | 判定证据来自交付物、日志或截图，不靠口头说明 | 通过 / 阻断 |
| 难度与工作量 | 20 | 至少 3 步，步骤之间有依赖，不能一步完成 | 通过 / 阻断 |
| 难度与工作量 | 21 | 难度来自资料、工具或判断，不是堆字数 | 通过 / 阻断 |
| 难度与工作量 | 22 | 参考工时与步骤、资料和环境大致匹配 | 通过 / 阻断 |
| 重复与泄漏 | 23 | 不复制官方 122 条、第三方任务或客户材料 | 通过 / 阻断 |
| 重复与泄漏 | 24 | 与已有任务没有高度相似，题族和实例可区分 | 通过 / 阻断 |
| 重复与泄漏 | 25 | 可见输入没有答案、隐藏测试和评分依据 | 通过 / 阻断 |

### 4.3 阻断与结论

阻断项只能通过返修、拒收或升级处理。可以返修的，给出具体字段和可执行修改建议；不能返修的，写清拒收理由；许可、跨法域、医疗或未成年人数据、执业签字、外部服务不可替代等边界不清的，升级给项目负责人。

审核结论要附证据。通过时写明版本号和检查范围；退回时逐条写维度、字段、级别和说明；拒收时写明不可修复的原因。评审记录进入任务版本历史，不能事后改写。

## 5. T1 人工基线记录模板

T1 记录人工完成一条任务的全过程，重点是真实用时、卡点和判断依据，不追求格式漂亮。

### 5.1 记录字段

T1 在平台外完成，用来建立人工基线。记录一条任务一个文件，文件名建议 `T1-<direction>-<expert>-<date>.md`。所有时间用实际发生值，不补记、不估算成整数小时。

| 字段 | 填写要求 |
|---|---|
| record_id | 例如 T1-BF-01 |
| task_id | 试点任务 ID 或题族实例 ID |
| direction | business_finance / psychology_neuro / engineering |
| expert_id | 专家编号，不写客户名 |
| date | 完成日期，格式 YYYY-MM-DD |
| start_time / end_time | 本地时间，精确到 15 分钟 |
| total_min | 总实际用时，扣除明确空闲 |
| material_min | 资料获取、清洗、授权确认用时 |
| step_min | 各步骤实际用时 |
| tool_min | 工具安装、配置、排错用时 |
| rework_min | 自检后返修用时 |
| stuck_points | 卡点、等待、无法判断的地方 |
| quality_self_check | 自检结论和未解决项 |
| evidence | 截图、脚本、日志、交付物路径 |
| notes | 口径、假设、异常情况 |

### 5.2 记录模板

```markdown
# T1 人工基线记录

- record_id:
- task_id:
- direction:
- expert_id:
- date:
- start_time / end_time:
- total_min:
- material_min:
- tool_min:
- rework_min:

## 步骤用时

| 步骤 | 计划分钟 | 实际分钟 | 工具 | 产物 | 卡点 | 证据 |
|---|---|---|---|---|---|---|
| 1 |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |

## 资料与授权

- 资料清单：
- 许可与 PII：
- 获取或清洗用时：
- 未能获取的资料：

## 卡点与判断

- 最花时间的判断：
- 最难解释的步骤：
- 需要同事确认的问题：
- 平台可能帮上的地方：

## 自检与返修

- 自检发现的问题：
- 返修用时：
- 未解决项：

## 证据

- 交付物路径：
- 脚本或命令：
- 截图：
- 备注：
```

### 5.3 计时规则

- 以 15 分钟为记录粒度，起止时间用同一时区。
- 等待资料、等待回复的时间单列，不算进步骤用时。
- 工具安装和排错单列，不混进专业判断时间。
- 返修单列，不把返修时间摊回原步骤。
- 同一天完成多条任务时，分别记录，不合并计时。
- 记录实际用时，不按 28 小时或 22 小时倒推。

## 6. T2 平台辅助记录模板

T2 记录同题族另一实例在平台内完成的过程，重点是与 T1 的可比用时、检查效果和 Agent 建议处理。

### 6.1 记录字段

T2 在平台内完成，与 T1 使用同一题族的不同实例。记录平台版本、状态变化、自动检查、Agent 建议和返修，重点是比较平台辅助前后的净节省时间，而不是只看总用时。

T2 启动前要完成真实模型验收。当前平台默认使用 Mock Provider，只能做流程演练；Mock 建议不能当作真实 Agent 效果，也不能写成 T2 的质量结论。真实模型是否启用，以项目组配置和 `docs/19-agent-readiness.md` 的校准报告为准。

| 字段 | 填写要求 |
|---|---|
| record_id | 例如 T2-BF-01 |
| task_id | 平台任务 ID |
| paired_t1 | 对应的 T1 记录 ID |
| platform_version | 例如 S2 或具体提交号 |
| expert_id | 专家编号 |
| start_time / end_time | 平台操作起止时间 |
| total_min | 平台内总实际用时 |
| form_min | 填写任务源用时 |
| upload_min | 资料上传递交用时 |
| check_min | 自动检查与处理阻断用时 |
| review_wait | 评审等待时间，单列 |
| rework_min | 退回返修用时 |
| agent_min | 处理 Agent 建议用时 |
| blockers | 检查阻断项数量和错误码 |
| false_positive | 误报项和原因 |
| missed | 漏报项和原因，阻断级漏报必须为 0 |
| net_saving | T1 总用时减 T2 总用时，注明口径 |
| evidence | 截图、版本号、检查记录、评审记录 |

### 6.2 记录模板

```markdown
# T2 平台辅助记录

- record_id:
- task_id:
- paired_t1:
- platform_version:
- expert_id:
- start_time / end_time:
- total_min:
- form_min:
- upload_min:
- check_min:
- review_wait:
- rework_min:
- agent_min:

## 状态变化

| 时间 | 状态 | 动作 | 版本 | 备注 |
|---|---|---|---|---|
|  | draft | 创建草稿 | v0 |  |
|  | returned | 领域退回 | v1 |  |
|  | auto_checked | 重新提交 | v2 |  |

## 自动检查

- 运行次数：
- 阻断项：
- 错误码：
- 误报：
- 漏报：
- 跳过项是否被误当成通过：

## Agent 建议

| 建议 ID | 字段 | 建议值摘要 | 处理 | 理由 | 节省或增加分钟 |
|---|---|---|---|---|---|
|  |  |  | accepted / edited / rejected |  |  |

- 建议总数：
- 接受数：
- 编辑后接受数：
- 拒绝数：
- 自动采纳数，必须为 0：

## 用时与结论

- T1 总用时：
- T2 总用时：
- 净节省：
- 节省来自哪一步：
- 平台新增的负担：
- 仍需人工兜底的地方：

## 证据

- 任务详情截图：
- 检查结果截图：
- 评审记录：
- 交付物路径：
```

### 6.3 Agent 建议记录规则

每条建议都要记录去向和理由。拒绝要写“不适用”“不准确”“引入错误”或“已有更好写法”，不能只写“不要”。编辑后接受要写清改了哪个值、为什么。自动采纳必须为 0；发现平台绕过逐条确认时，立即停用并报告。

误报和漏报分开记。误报是平台报了但实际没问题，漏报是平台没报但评审发现了问题。阻断级漏报必须为 0；出现一次就升级，不能只在本条记录里备注。

## 7. 试点反馈表

反馈表用于收集界面、流程、检查和 Agent 建议的实际体验，评分与开放题一起提交。

### 7.1 评分题

每题 1 到 5 分，1 分表示完全不可用，5 分表示可以直接用于正式生产。没有使用过的功能填“未使用”，不要凭印象打分。

| 序号 | 问题 | 1 | 2 | 3 | 4 | 5 | 未使用 |
|---|---|---|---|---|---|---|---|
| 1 | 登录、退出和会话稳定性 |  |  |  |  |  |  |
| 2 | 新建任务和任务 ID 规则是否清楚 |  |  |  |  |  |  |
| 3 | 八张表单卡片是否覆盖十块任务源 |  |  |  |  |  |  |
| 4 | 资料上传、许可和 PII 字段是否够用 |  |  |  |  |  |  |
| 5 | 保存草稿和并发保护是否可靠 |  |  |  |  |  |  |
| 6 | 自动检查的提示是否准确、可处理 |  |  |  |  |  |  |
| 7 | 提交和版本生成是否符合预期 |  |  |  |  |  |  |
| 8 | 领域评审退回意见是否具体 |  |  |  |  |  |  |
| 9 | 质量审核流程是否清楚 |  |  |  |  |  |  |
| 10 | Agent 建议是否有用、是否可控 |  |  |  |  |  |  |
| 11 | 本手册和材料是否够用 |  |  |  |  |  |  |
| 12 | 支持渠道是否响应、是否能解决问题 |  |  |  |  |  |  |

### 7.2 开放题

- 最影响你完成任务的三个问题是什么，分别出现在哪一步。
- 哪个字段最没用、哪个字段最缺，为什么。
- 哪条自动检查最误导，哪条最该补，给出一个具体例子。
- Agent 最好的一次建议和最差的一次建议，各写清字段、建议值和你的处理。
- T2 比 T1 快或慢在哪里，给出大致分钟数。
- 有没有哪一步必须靠平台外的工具或同事才能完成。
- 资料许可、PII 和保密流程有没有让你犹豫的地方。
- 如果只能改一处，你希望先改什么。
- 还有哪些话不适合写在评分题里。

### 7.3 提交方式

反馈表与 T1、T2 记录一起提交到项目组指定的书面渠道。反馈里不要贴客户数据、个人信息、账号口令和未公开材料；需要举例时用字段名、错误码和合成数据。项目组汇总后用于平台修订、手册修订和试点出口判定，不把单条反馈当成对个人的评价。

## 8. 版本记录

- v0.1，2026-11-14：首版试点材料包。包含项目说明、商业会计对账示范任务、两条不合格示例、专业审核清单、T1 与 T2 记录模板和试点反馈表，全部使用合成数据。
