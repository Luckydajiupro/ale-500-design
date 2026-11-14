# 官方 ALE 任务拆解：六个代表性案例与数据合同

这份文件回答三个问题：ALE 官方任务到底由哪些部件构成、它们的成功判定长什么样、ALE 500 要从官方包里继承什么又必须自己补什么。取材对象是冻结快照中的旧任务仓库、ALE-data v1.1 数据包和新引擎规范；每个结论都带项目相对路径与定位符，没有运行过的部分明确标 NOT_RUN。

## 方法与证据口径

选样不是按目录名挑的，六条案例都打开过 `task_card.json`、`main.py`、评分脚本、数据包内的 `input/`、`reference/`、`software/` 实际文件。

选样规则有三条。第一，覆盖三类业务：商业会计/财务两条、神经影像一条、工程两条、法律一条。第二，产物类型不同：xlsx 工作簿、浏览器表单导出的 JSON、NIfTI 二进制、OBJ+BLEND 模型对、JSON 答案集。第三，判定机制不同：结构+公式扰动、逐字段等值、几何不变量、图像 LLM 判定、集合等值、十进制容差。

证据分四档，全文一致使用：file fact 指文件里直接读到的事实；code fact 指评分或运行代码里直接读到的事实；inference 指由文件结构与代码路径推出、但未被任何执行验证的结论；unknown 指快照里没有证据、必须跑一次或拿到别处的材料才能回答的问题。

官方状态取自 `inputs/frozen/01_agents-last-exam/tasks/published_tasks.json`，该文件结构是 `{"published": {"<domain>/<task>": {"variants": [...]}}}`，共 122 条。数据包只有已发布变体，`inputs/frozen/03_ale-data/task-data-v1.1/` 下同样是 122 个任务目录、122 个变体目录，按目录名逐一比对后有 119 个任务与发布清单完全一致，3 个任务的变体名不一致（`other/mota_exploration`、`visual_media/uv_reproduction`、`visual_media/skeletal_animation_reproduction`）。

## 案例索引

| # | 案例 | domain / subdomain | 变体 | 产物 | contract kind | 判定原型 |
|---|---|---|---|---|---|---|
| C1 | equity_research_summary | business_finance / 6.3 enterprise_analytics | tsla_fy2023 | xlsx 工作簿 | tabular_columns | 结构 + 公式扰动 |
| C2 | taxform_4_1 | business_finance / 6.1 accounting | variant_1 | 表单 JSON | numeric_cases | 逐字段等值 + 硬门 |
| C3 | scene2_resample | psychology_neuro / 5.2 exp_psychology | base | NIfTI + PNG + CSV | artifact_diff | 几何 + 数值不变量 |
| C4 | 2d_drawings_to_3d_building_model | engineering / 1.3 civil_geo | base | OBJ + BLEND | artifact_diff | 图像 LLM 判定 |
| C5 | chisel_verilog_alignment_seq_1 | engineering / 1.8 semiconductor | base | JSON 答案集 | code_artifact | 集合等值 |
| C6 | legal_dr_fees_01 | legal / 7.2 legal_research | base | JSON 数值表 | document_qa | 十进制容差 |

contract kind 一列用的是本波任务书里的五种平台术语，不是 ALE 官方词汇。`inputs/frozen/02_ale/docs/specs/` 十个规范文件里没有任何一处出现 `contract.kind`、`numeric_cases`、`artifact_diff` 或 `tabular_columns`（对本目录做全文检索无命中），所以这五种 kind 只能算平台侧的分类假设，不能写成官方事实。C5 的归类尤其勉强，它的产物是 JSON 而不是代码，归入 code_artifact 只是因为证据全部来自代码。

## C1 business_finance/equity_research_summary

这一条是财务分析产物：把一份给定的 FY2023 摘录做成六节 Excel 摘要，判定既看结构也看公式是否真的随输入变化。

### 1. 身份

domain 为 business_finance，taxonomy 记 `domain_id 6`、`subdomain_id 6.3`、`subdomain_code enterprise_analytics`，分类器在 2026-05-28 把它从 6.1 accounting 改判，rationale 写在 `inputs/frozen/01_agents-last-exam/tasks/business_finance/equity_research_summary/task_card.json:52-68`。slug 为 equity_research_summary，已发布变体只有 tsla_fy2023（`published_tasks.json`）。旧仓库该目录四个文件：`task_card.json` 4,288 B、`main.py` 6,616 B、`scripts/score_workbook.py` 20,421 B、`scripts/formula_evaluator.py` 8,665 B。

### 2. 真实任务说明

任务说明有两个副本：`task_card.json:9` 的 taskPrompt，以及数据包内 `inputs/frozen/03_ale-data/task-data-v1.1/business_finance/equity_research_summary/tsla_fy2023/input/instruction.md`（3,599 B）。instruction 要求建六节：Market Data、Valuation Metrics、Income Statement (FY 2023, $mm)、Balance Sheet、Cash Flow、Key Metrics Dashboard（`input/instruction.md:12` 要求六个节、标签文本精确、数值放在相邻列，并说明布局与单元格位置由 agent 自定）。原句只引这一句：“with values in the adjacent column”（`input/instruction.md:12`，短句引用）。推导字段必须以公式写入而不是硬编码（`input/instruction.md:87`），输出路径是 `output\TSLA_Financial_Summary.xlsx`（`input/instruction.md:82`），表头要求加粗并填色（`input/instruction.md:88`）。

### 3. 输入资料

包内 `input/` 三个文件：`instruction.md` 3,599 B；`tsla_fy2023_financials.md` 697 B，给的是一张固定数值摘录，10 个 FY2023 数值为 Total Revenue 96,773、Cost of Revenue 79,113、Operating Expenses 8,769、Net Income 14,974、Total Assets 106,618、Total Liabilities 43,009、Cash & Equivalents 16,398、Total Debt 2,857、Operating Cash Flow 13,256、Capital Expenditures 8,969，单位百万美元（`input/tsla_fy2023_financials.md:10-13`、`:19-22`、`:28-29`）；`source_urls.txt` 146 B，三条 URL 指向 Yahoo Finance 报价页、Yahoo 关键统计页和 SEC EDGAR 检索页。数值与 Tesla 2023 年 10-K 量级一致，但任务方要求“使用这些确切数值”，因此按固定摘录处理，判为合成摘录而非可复算的原始报表（inference）。

### 4. 软件环境

`task_card.json:6-9` 写 Chrome 与 LibreOffice Calc；`task_card.json:47-51` 写 `c4-standard-4`、快照 `cpu-free`、超时 7,200 秒；`task_card.json:70-72` 要求系统包 `google-chrome-149.0.7827.54`。包内 `software/` 两个文件：`launch_calc.bat` 480 B，先调用同目录的 PowerShell 引导脚本，再按 `C:\Program Files\LibreOffice\program\scalc.exe` 与 x86 路径依次探测后启动 Calc；`bootstrap_libreoffice.ps1` 818 B，找不到时执行 `winget install --id TheDocumentFoundation.LibreOffice --exact --silent --accept-package-agreements --accept-source-agreements`（该行在脚本第 19 行）。

### 5. 操作流程

agent 先跑 `software\launch_calc.bat` 打开 Calc；按 instruction 建立六节；把 10 个给定值落到相邻单元格；对推导字段写公式而不是硬编码；从浏览器取 Yahoo 三个实时字段；最后存成 `output\TSLA_Financial_Summary.xlsx`。多步证据在 instruction 的分节要求与公式要求里，跨应用证据在 `source_urls.txt` 与 `launch_calc.bat` 里。旧仓库 `main.py:155-181` 把工作簿 base64 后连同 manifest 通过子进程交给 `scripts/score_workbook.py --stdin`，说明评分发生在宿主侧而不是 VM 内。

### 6. 预期产物

精确路径 `output\TSLA_Financial_Summary.xlsx`（`input/instruction.md:82`，Windows 反斜杠）。结构约束五条：sheet 名含 “TSLA”；六个节标题加粗且有非白填充；每个标签右侧相邻单元格放值；9 个公式单元格必须引用正确来源单元格；5 个 dashboard 公式与 12 个实时字段标签存在。

### 7. reference 与 oracle

`reference/reference_manifest.json` 2,881 B 是真正的判定依据，编码了：`sheet_name_contains: "TSLA"`；6 个 `section_headers`，每个都要求 bold 与 fill（`:7-14`）；10 个 `fixed_values`，容差 1.0（`:15-26`）；9 个 `formula_cells`，每个带 `must_reference` 列表（`:27-37`）；5 个 `dashboard_formulas`（`:38-44`）；12 个 `live_labels`（`:45-58`）。另有 `reference/reference_workbook.xlsx` 8,520 B 与 `reference/raw_submission/TSLA_Financial_Summary_Feb2026 - Yushan Li.xlsx` 8,520 B，两者 MD5 都是 `8864a767192d27d1d8e98c75a90eff2c`，即参考工作簿是提交者原件的逐字节副本。这一点直接影响 oracle 的独立性判断：`inputs/frozen/02_ale/docs/specs/task-quality-standard.md:60-63` 明确写“某个 solver 输出或 oracle 实现不是独立真值来源”，本案例恰好是反例。

### 8. 评分与验证

代码事实来自 `inputs/frozen/01_agents-last-exam/tasks/business_finance/equity_research_summary/scripts/score_workbook.py`。标签定位不依赖坐标：`_build_label_map` 把“非公式文本单元格”映射到“同一行下一列”（`:216-232`），`_find_label` 还接受 `label — value` 的合并写法（`:235-248`）。公式判定不是看有没有等号，而是用 `FormulaEvaluator` 在四组扰动场景（scale 1.137、0.863，两组 0.9–1.1；offset 13.7、7.3、3–12）下重算，要求结果随输入变化且与规则一致（`:372-481`）。固定值容差 1.0（`:353-370`）。实时字段只做 `_parse_numeric`，即只要求“是数值”，不校验数值本身（`:483-494`）。最终 `score = passed / total`（`:496`），`WorkbookScoreResult` 的 `passed` 布尔只在 `score >= 1.0` 时为真（`:497`）；但 `main.py:210` 返回的是 `result["score"]`，所以 43 项按通过占比给分，全对才得 1.0，错一项只失该项分，不是 0.0。43 由 1 个 sheet 名、6 个表头、10 个固定值、9 个公式、5 个 dashboard 公式、12 个实时标签相加得到（code fact + inference）。硬门：缺输出返回 `[0.0]`（`main.py:190-200`），缺 manifest 抛错。文件上限：xlsx 成员不超过 2,000 个、不超过 64 MB（`:282-290`），单表不超过 20 万格（`:296-297`）。

### 9. 证据表

| claim | source | evidence type | design implication |
|---|---|---|---|
| 参考工作簿与提交者原件字节相同 | `.../tsla_fy2023/reference/reference_workbook.xlsx` 与同目录 `raw_submission/...xlsx`，MD5 均为 8864a767192d27d1d8e98c75a90eff2c | file fact | oracle 不能直接复用提交件，500 条要独立复算或双人复核 |
| 公式必须随输入变化 | `scripts/score_workbook.py:372-481` | code fact | 表格类任务的验证要能识别硬编码数字 |
| 实时字段只验类型不验值 | `scripts/score_workbook.py:483-494` | code fact | 联网取数不适合做可复现评分，500 条应改为给定时点快照 |
| 43 项按通过占比计分，全对才 1.0 | `scripts/score_workbook.py:496-497`、`main.py:210` | code fact | reward 是 score，存在部分分；`passed` 布尔只在 1.0 时为真 |
| LibreOffice 靠 winget 现场安装 | `.../tsla_fy2023/software/bootstrap_libreoffice.ps1:19` | file fact | 软件必须预装进镜像，不能依赖运行期联网 |

### 10. 这个案例证明了什么

它证明表格任务可以把“结构正确”和“计算正确”分开评，并且能用扰动输入识别硬编码；也证明官方会为单元格位置不固定留出标签定位的余地。它没有证明实时市场数据可以被公平评分，没有证明 oracle 独立，也没有证明该 reference 工作簿在评分器下能得 1.0——这三项都是 NOT_RUN。

## C2 business_finance/taxform_4_1

这一条是税务表单产物：在本地 HTML 表单里填完 191 个字段并导出 JSON，判定是逐字段等值加一组硬门。

### 1. 身份

domain business_finance，taxonomy 6.1 accounting（`inputs/frozen/01_agents-last-exam/tasks/business_finance/taxform_4_1/task_card.json:62-84`），slug taxform_4_1，共 5 个变体，已发布的是 variant_1。旧仓库三个文件：`task_card.json` 6,109 B、`main.py` 9,501 B、`scripts/score_taxform_outputs.py` 7,135 B。

### 2. 真实任务说明

taskPrompt 在 `task_card.json:9`，包内独立说明是 `.../taxform_4_1/variant_1/input/instruction.txt`（7 行）。它给的是一份虚构纳税人资料：Lisa M. Chen，Single，SSN 487-61-3295，地址 1730 Pacific Coast Drive, San Diego, CA 92101，电话 619-555-0238，邮箱 lisachen.sd@gmail.com，无 dependent；W-2 上有工资与联邦预扣；另有 450 美元应税利息，其中 120 美元免税；采用标准扣除；按 2025 年 Single 税率 10%（前 11,925 美元）、12%（11,926–48,475 美元）、22%（48,475 美元以上）；退税入储蓄账户，routing 322271627、account 9041758230（`input/instruction.txt` 全文 7 行）。真实工作流是“读表单→填表→导出结构化数据”。

### 3. 输入资料

variant_1 共 13 个文件、1.6 MB。`input/forms/` 下有 `formw2.html`、`formw2.pdf`、`form1040.html`、`form1040.pdf`、`form-handler.js`、`ssn-fields.js`、`shared-form.css`；`input/formw2_input.json` 是页面读取的源数据；`input/README.md` 说明流程。所有表单是纯 HTML/CSS/JavaScript，没有后端，输入框用 `name="line_12e"` 之类的字段名。数据是合成的：SSN、地址、金额都是为题目编的，不对应真实纳税人（file fact：`instruction.txt` 与 `formw2_input.json` 一致）。

### 4. 软件环境

`task_card.json:6-9` 写 Python 与 Chrome；`task_card.json:57-61` 写 `c4-standard-4`、`cpu-free`、超时 7,200 秒；`task_card.json:85-87` 要求 `google-chrome-149.0.7827.54`。包内 `software/start_http_server.bat` 68 B 左右，先 `cd /d "%~dp0..\input"` 再 `python -m http.server 8080`，即用本地静态服务器把表单喂给浏览器（`main.py:30-60` 的 `SOURCE_FORM_INFO`/`OUTPUT_FORM_INFO` 给出 `http://localhost:8080/forms/formw2.html?data=/` 这类地址）。

### 5. 操作流程

启动静态服务器；打开 W-2 页面读取工资与预扣；打开 1040 页面，分两页填 191 个字段；点 “Save Results” 下载 JSON；把下载文件移到 `output/form1040_output.json`。variant_5 更复杂：四种来源表单（W-2、1099-INT、1099-R、1099-MISC）同时输入，输出 1040 与 Schedule 1 两张表（`main.py:71-102` 的五个 `VariantSpec`）。跨应用证据是浏览器与文件系统之间的下载/移动动作。

### 6. 预期产物

精确路径 `output/form1040_output.json`，variant_5 另加 `output/form1040s1_output.json`。顶层只允许 `fields` 与 `pagination` 两个键（`scripts/score_taxform_outputs.py:6`），`fields` 是字段名到值的映射，`pagination` 至少含 `current_page_index` 与 `total_pages`（GT 里是 1 和 2）。

### 7. reference 与 oracle

`reference/form1040_gt.json` 给出 191 个字段的期望值（129 个 text、54 个 checkbox、8 个 radio），关键行值包括 line_1a 52,000、line_2a 120、line_2b 450、line_9 52,450、line_11a/11b 52,450、line_12e 15,000、line_14 15,000、line_15 37,450、line_16 4,256、line_18/22/24 4,256、line_25a 5,800、line_33 5,800、line_34 1,544、line_35a 1,544。`reference/form1040_gt_alt.json` 与主 GT 恰有 10 个字段不同：line_12e 15,750、line_14 15,750、line_15 36,700、line_16/18/22/24 4,165.50、line_34/35a 1,634.50、line_37。alt 文件的作用是第二条合法答案通道（`scripts/score_taxform_outputs.py:71`、`:116-120`）。

### 8. 评分与验证

硬门在 `scripts/score_taxform_outputs.py:56-143`：缺输出文件、参考字段非法、缺字段、额外字段、字段类型不符、值形状不符、顶层键意外，任一命中直接 0 分。通过硬门后按 informative 字段等权计分（`:16-21` 只把非空 checkbox 列表与非空 text-like 字符串算 informative），`score = matched / total`（`:162`）。比较规则：checkbox 用集合相等（`:32-42`），`line_` 前缀字段去逗号后按 0.01 容差比 float（`:9-13`、`:32-42`），其余严格相等。注意 `target` 之类的值不参与比较，只比字段值。一个必须写进 500 条设计的细节是：`input/forms/form1040.html:208` 的页面上印着标准扣除 “Single or MFS, $15,750”，但主 GT 用的是 15,000，alt GT 才用 15,750。也就是说“按页面信息算对”的答案只有落到 alt 通道才不被判错。

### 9. 证据表

| claim | source | evidence type | design implication |
|---|---|---|---|
| 表单是纯前端 HTML，无后端 | `.../variant_1/input/forms/form1040.html` 与 `form-handler.js`；`software/start_http_server.bat` | file fact | 任务可离线自包含，不依赖外部服务 |
| 题面数字与主 GT 冲突 | `input/forms/form1040.html:208` 印 15,750；`reference/form1040_gt.json` 用 15,000 | file fact | 多解必须显式给出 alt reference，否则正确解被判错 |
| 字段比较有严格硬门 | `scripts/score_taxform_outputs.py:56-143` | code fact | 表单类任务的 schema 校验要前置，失败即 0 |
| 数值字段走 0.01 容差 | `scripts/score_taxform_outputs.py:32-42` | code fact | 金额类答案需要统一舍入与容差口径 |
| 191 个字段里只有约 39 个 informative | `reference/form1040_gt.json` 逐字段统计 | inference | 评分覆盖的是少数字段，专家要标出哪些字段计分 |

### 10. 这个案例证明了什么

它证明“浏览器表单 + JSON 导出”可以作为一条完整的专业工作流，并且能让硬门与部分分共存；也证明 alt reference 是处理题面歧义的现实手段。它没有证明税额计算本身正确（页面与 GT 就冲突），没有证明 39 个 informative 字段的统计口径（自写脚本推断），也没有证明 5 个变体的评分代码都被同一个测试覆盖——只读了 variant_1 的实跑路径。

## C3 psychology_neuro/scene2_resample

这一条是神经影像产物：在 3D Slicer 里把 1 mm ROI 重采样到 2 mm 网格，判定靠几何契约与三个派生统计量。

### 1. 身份

domain psychology_neuro，taxonomy `domain_id 5`、`subdomain_id 5.2`、`subdomain_code exp_psychology`，backfill 分类器 gpt-4o-mini 于 2026-05-13 标注，rationale 在 `inputs/frozen/01_agents-last-exam/tasks/psychology_neuro/scene2_resample/task_card.json:57-79`。slug scene2_resample，已发布变体 base。旧仓库 `main.py` 只有 38 行，全部逻辑在共享模块 `tasks/psychology_neuro/_shared/cognitive_science/neuro_runtime.py`（242 行）和任务自带 `scripts/verify_outputs.py`（173 行）。

### 2. 真实任务说明

taskPrompt 在 `task_card.json:9`，要求“在 3D Slicer 5.0.3 里完成 GUI 工作流”：打开 1 mm ROI mask 与 2 mm 统计图，把 mask 用最近邻重采样到 2 mm 网格，存 `output/roi_mask_2mm_nn.nii.gz`，导出重采样设置截图 `output/resample_settings.png`，再算 ROI 统计写 `output/scene2_stats.csv`（单行，列 `mean,max,voxel_count`，mask 取大于 0.5 的体素）。`agentMustDo` 五条在 `task_card.json:10-16`。

### 3. 输入资料

包内 `input/` 两个 NIfTI：`statmap_z_2mm.nii.gz` 582,057 B、`roi_mask_1mm.nii.gz` 49,968 B。`reference/scene2_stats.csv` 65 B，一行三值：mean -0.8635807633399963、max 3.2616043090820312、voxel_count 6906。`software/` 下有 `launch_gui.sh` 168 B、`containers_manifest.yaml` 2,380 B、`README.txt` 340 B，以及 `computer_use_benchmark_bundle/`：`run_scene.sh` 4,094 B、`smoke_test.sh` 3,214 B、任务副本输入五个文件（比正式 `input/` 多了 `roi_mask_1mm_smooth.nii.gz` 1,061,833 B 与 `roi_labelmap_1mm.nii.gz` 266,363 B），以及 8,658,481,183 B 的 `slicer_5.0.3_20221025.simg`。数据是真实影像还是合成体模，快照里没有说明（unknown）；能确认的只有体素规模与统计学量级合理（inference）。

### 4. 软件环境

`task_card.json:6-8` 只写 Python，但 prompt 要求 3D Slicer 5.0.3；`task_card.json:80-82` 要求系统包 `apptainer-1.3.0`；`task_card.json:52-56` 写 `c4-standard-4`、`cpu-free-ubuntu`、超时 7,200 秒。`software/README.txt` 写明：canonical launcher 是 `./launch_gui.sh`，容器内命令是 `Slicer`，软件族是 3D Slicer 5.0.3，大镜像留在 raw bundle，`software/` 只暴露稳定的启动器与清单。`launch_gui.sh` 实际执行 `exec "$DIR/computer_use_benchmark_bundle/run_scene.sh" "scene2_resample" "$@"`。

### 5. 操作流程

启动 GUI；载入两个卷；在 Resample Scalar/Vector 模块里选最近邻、参考卷为 2 mm 统计图；保存重采样 mask；截图；再用 mask 在统计图上算 mean/max/体素数并写 CSV。这里的关键是“GUI 操作也会被检查设置”，因此截图是流程证据而不是装饰。

### 6. 预期产物

三个文件，精确路径 `output/roi_mask_2mm_nn.nii.gz`、`output/resample_settings.png`、`output/scene2_stats.csv`。CSV 单行，列序与附加列不限，但 `mean`、`max`、`voxel_count` 三个名字必须出现。

### 7. reference 与 oracle

reference 只有一个 65 B 的 CSV，没有参考 mask、没有参考截图。也就是说 oracle 只固定了“几何正确时应该得到的三个统计量”，没有固定逐体素的 mask 内容。`task_card.json:51` 还声称 reference 里包含 PNG 判定口径，实际代码只判可读性。

### 8. 评分与验证

验证器由 `neuro_runtime.py:211-242` 从任务目录上传到 VM 的 `/tmp/agenthle_eval/cognitive_science/<task>/`，以 `--task-name/--input-dir/--reference-dir/--output-dir` 运行、超时 300 秒，stdout 的 JSON `score` 即 reward，非零退出且无 stdout 记 0。`scripts/verify_outputs.py` 的事实：`TOL = 1e-6`（`:12-13`）；三个必需输出缺失即硬门（`:126-130`）；PNG 只做 `Image.open(...).verify()`（`:132-137`），完全不比像素；自带 NIfTI 解析器处理大小端、datatype、`scl_slope/inter` 与 sform 仿射（`:55-112`）；mask 与 statmap 必须同 shape（`:146-148`）、仿射 `np.allclose`（`:149-151`）、mask 大于 0.5 且非空（`:153-156`）；用 agent 的 mask 在统计图上重算 mean/max/voxel_count，与参考 CSV 逐项 1e-6 比较（`:158-164`）；给分是 0.7（重算值全对）+ 0.3（agent 自己的 CSV 全对），任一项超差即失去该分量（`:32-48`）。

### 9. 证据表

| claim | source | evidence type | design implication |
|---|---|---|---|
| 截图只判可读，不判内容 | `scripts/verify_outputs.py:132-137` | code fact | 500 条的“过程证据”若要求真实内容，必须另设 OCR/像素或人工审核 |
| mask 判定靠仿射+统计不变量 | `scripts/verify_outputs.py:146-164` | code fact | 二进制产物可以用几何与数值指纹验收，不必逐字节比对 |
| 参考目录没有参考 mask | `.../scene2_resample/base/reference/` 仅 `scene2_stats.csv` | file fact | oracle 允许一族解，只要统计量一致 |
| 8.66 GB 容器镜像随包 | `.../base/software/computer_use_benchmark_bundle/containers/slicer_5.0.3_20221025.simg` | file fact | 软件资产需要独立分层与哈希，不能塞进 Git |
| 验证器不在数据包里 | 数据包 `base/` 无任何 `verify*`/`test*` 文件；验证器来自旧仓库 `scripts/verify_outputs.py` | file fact | 数据合同必须单独携带验证器或验证器引用 |

### 10. 这个案例证明了什么

它证明神经影像类任务可以用“几何对齐 + 派生统计”验收二进制产物，且能给出 0.7/0.3 的部分分。它没有证明截图内容被检查，没有证明 1e-6 容差下单个体素差异不会改变体素数（这依赖数据本身），也没有证明该任务是真实临床数据。8.66 GB 的单文件镜像说明“软件环境”本身就是一项数据合同义务。

## C4 engineering/2d_drawings_to_3d_building_model

这一条是 3D 建模产物：从六份建筑图纸重建厂房并导出 OBJ/BLEND，判定是几何一致性硬门加多视角图像判定。

### 1. 身份

domain engineering，taxonomy `domain_id 1`、`subdomain_id 1.3`、`subdomain_code civil_geo`，分类器 gpt-4o-mini 于 2026-05-28 标注（`inputs/frozen/01_agents-last-exam/tasks/engineering/2d_drawings_to_3d_building_model/task_card.json:112-120`）。slug 2d_drawings_to_3d_building_model，已发布变体 base。旧仓库有 `main.py`、`task_card.json`、`assets/output_contract.json`、`scripts/{score_outputs.py,validate_native.py,render_human_views.py,detect_floors.py}`。

### 2. 真实任务说明

taskPrompt 在 `task_card.json:9`，要求按六份建筑图纸在 Blender 里重建 Betonwerk Katzenberger 厂房（宽矮的 Hall 加高窄的 Tower），导出 `base/output/model.obj` 与 `base/output/model.blend`，两者必须含同一份 evaluated geometry（含修改器与实例），单位毫米，+X 东、+Y 北、+Z 上，地面 z=0，禁止输出 `.dwg`。任务说明强调“材质与纹理不计分”“允许整体 X/Y 平移”“相对位置必须正确”。

### 3. 输入资料

`input/` 六个 PDF 共约 50 MB：`Diagram.pdf` 约 13.7 MB、`Hall Ground Floor_Layout.pdf` 18,308,930 B、`Hall First Floor_Layout.pdf` 616,526 B、`Hall Second Floor_Layout.pdf` 616,526 B 量级、`Hostel_ Elevation and Section.pdf` 16,738,189 B、`Tower_Layout.pdf` 约 598 KB；另有 `3D Snapshot.png` 164,185 B、`README.md` 2,665 B、`output_contract.json` 1,156 B、`base_model.obj` 846 B、`base_model.3dm` 9,465 B。`base_model.obj` 只是定位锚：11 个顶点的凸包 footprint 加三条正交轴线与指北 chevron，不含墙体、楼板。图纸为真实建筑项目的扫描/矢量件（inference，基于文件体积与命名），没有版权说明文件。

### 4. 软件环境

`task_card.json:6-8` 写 Blender 4.5；`task_card.json:107-111` 写 `c4-standard-4`、`cpu-free-ubuntu`、linux。`main.py:46-50` 的候选路径是 `/opt/blender-4.5.1/blender`、`/usr/local/bin/blender`、`/usr/bin/blender`；渲染在 VM 上用 CPU Cycles（`main.py:328-461` 的 evaluate）。数据包里没有 `software/` 目录——该包只有 `input/` 与 `reference/` 两类，软件完全靠镜像。

### 5. 操作流程

读 README、output contract 与六份 PDF；把 `base_model.obj` 以 +Y forward、+Z up、毫米单位导入 Blender 作为定位锚；建 Hall 与 Tower 的体量、楼板、南北立面（北实墙、南开放钢架）、幕墙竖梃、三个workshop 模块、夹层；导出 OBJ 与 BLEND，确保 BLEND 重新打开时链接几何已打包。多步证据在 `task_card.json:10-15` 的 agentMustDo 与 `output_contract.json` 的 required_features 八项。

### 6. 预期产物

`base/output/model.obj`（Wavefront OBJ ASCII）与 `base/output/model.blend`，两者须一致到 1 mm；不得有任何 `.dwg`；`output_contract.json:5-13` 把 required_files、coordinate_system、mesh_constraints、forbidden_outputs、required_features 全部机器可读化。

### 7. reference 与 oracle

包内 `reference/eval_config.json` 2,187 B，含 task_description、8 条判定问题、`pass_threshold` 0.5、14 个视角名、`render_units: "mm"`、`render_source_up_axis: "Z"`；`reference/reference_renders_linux/` 14 张 PNG，每张 713–813 KB，是用同一 Linux CPU 渲染器从参考 OBJ 生成的固定视角。**数据包里没有参考 OBJ**：`task_card.json:92-96` 声称归档 `reference_obj/3D Model.{obj,3dm,dwg}`，实际包内只有渲染图与配置（file fact，目录清单为空）。这意味着只拿到数据包的人无法重新生成参考渲染。

### 8. 评分与验证

硬门在 `main.py:344-362`：缺 OBJ 或 BLEND 返回 `[0.0]`；输出目录出现任何 `.dwg` 返回 `[0.0]`；`validate_native.py` 判无效返回 `[0.0]`（`main.py:417`）。`validate_native.py` 从 BLEND 的 evaluated depsgraph 取网格类实例，要求非空且坐标有限（`:16-37`），用 KDTree 把 OBJ 顶点对应过去，最大顶点距离超过 1.0 mm 即失败（`:41-50`），三角面标签多重集必须完全一致，再做双向采样点到面距离（`:59-106`），最后 `valid = max(distances.values()) <= 1.0`（`:135`）。通过后渲染 14 个固定视角（`scripts/score_outputs.py:35-50`），候选图为 1024 px、32 samples（`main.py` 内 `CAND_RES`/`CAND_SAMPLES` 默认值），渲染脚本 `--factory-startup --disable-autoexec`、900 秒超时。最后 `scripts/score_outputs.py` 把候选渲染与参考渲染成对送多模态 LLM，按 8 条二元 YES/NO 问题逐条判定（`:53-91`），`score = yes_count / 8`（`:283`），`passed = score >= 0.5`（`:284`）。判定器对格式很硬：答案不是纯 YES/NO 或 `finish_reason != "stop"` 就抛错（`:269-273`），缺任一 PNG 也抛错（`:230-233`）。注意 `passed` 只是报告字段，真正的 reward 是 `score` 本身（`main.py:461`），所以 0.5 并不构成及格线。

### 9. 证据表

| claim | source | evidence type | design implication |
|---|---|---|---|
| 几何一致性靠 OBJ/BLEND 双向距离 ≤1 mm | `scripts/validate_native.py:41-106`、`:135` | code fact | 多产物任务要有“同一性”检查，不能只查存在 |
| 视觉判定是 8 条二元问题 | `scripts/score_outputs.py:53-91`、`:283-284` | code fact | 感知类验收要拆成可复核的子问题，并保留原始回答 |
| 参考 OBJ 不在数据包内 | `.../2d_drawings_to_3d_building_model/` 目录清单只有 `reference/eval_config.json` 与 14 张 PNG | file fact | 参考渲染不可重建，复评依赖原始仓库 |
| 判定失败会抛错而非给 0 | `scripts/score_outputs.py:269-273` | code fact | 基础设施故障不能算作 agent 失败 |
| 8 问分数即是 reward | `main.py:461` | code fact | 图像判定任务的分数是 0/8–8/8 的离散值 |

### 10. 这个案例证明了什么

它证明 3D 建模任务可以用“几何同一性硬门 + 多视角图像判定”组合验收，并且能把材质、命名、三角化这些无关变量排除。它没有证明图像判定在不同模型/不同次运行下稳定（NOT_RUN），没有证明 8 条问题覆盖了图纸的全部专业要求，也没有证明参考渲染与提交渲染在同一 Blender 版本下可复现（只看到渲染脚本与 `--factory-startup`）。

## C5 engineering/chisel_verilog_alignment_seq_1

这一条是代码证据产物：把优化后 Verilog 的一个子表达式追回到 Chisel 源码位置，判定是集合等值。

### 1. 身份

domain engineering，taxonomy `domain_id 1`、`subdomain_id 1.8`、`subdomain_code semiconductor`（`inputs/frozen/01_agents-last-exam/tasks/engineering/chisel_verilog_alignment_seq_1/task_card.json` 的 taxonomy 段）。title 为 “Chisel-to-Verilog Source Location Alignment”，已发布变体 base。旧仓库只有 `main.py` 与 `task_card.json`。

### 2. 真实任务说明

正式说明在包内 `.../chisel_verilog_alignment_seq_1/base/input/workdir/TASK.md`（3,527 B）。它给一个 Chisel 双缓冲 FIFO（`Fifo.scala`，87 行）和 firtool 1.138.0 的优化输出 `optimized.sv`，要求找出 `stateReg == 2'h2` 这个子表达式（第 21 行第 23–39 列）在 `Fifo.scala` 中语义对应的全部源码位置（`TASK.md:41-57`）。TASK.md 明确写：firtool 的 `@[file:line:col]` 注释既嘈杂又不完整，逐字读注释不是可靠解法（`TASK.md:28-37`），并给出 CIRCT issue #2733 与 #4358 作为依据。

### 3. 输入资料

`input/workdir/src/main/scala/Fifo.scala` 2,430 B；`generated/optimized.sv` 6,351 B；`generated/DoubleBufferFifo.fir` 8,339 B（FIRRTL 中间表示，允许重新生成其它 Verilog）；`input/workdir/output/.keep` 0 B，预建输出目录。软件包装器在 `base/software/`：`yosys` 83 B、`firtool` 83 B、`sbt` 73 B、`python` 64 B、`jq` 60 B，全部是 `exec /opt/...` 的薄壳；`README.txt` 450 B 写明 yosys 走 `OSS CAD Suite 2026-04-22`、firtool 1.138.0、sbt 1.9.9 且 Chisel 6.5.0 依赖已预热、Python 与 jq 走 `/usr/bin`。

### 4. 软件环境

`task_card.json` 的 software 列 Yosys 0.33+、firtool 1.138.0、sbt 1.9+ with Chisel 6.5.0、Python 3.10；vm 是 `c4-standard-4`、`cpu-free-ubuntu`、超时 7,200 秒；requiredSystemPackages 是 `oss-cad-suite-20260422`、`firtool-1.138.0`、`sbt-1.9.9`、`jdk-default`。TASK.md:26 明确写“VM has no internet access during solve time”。

### 5. 操作流程

读 optimized.sv 第 21 行；注意到注释列了 6 个位置；用 firtool 从 `.fir` 重新生成未优化 Verilog；用 yosys 做 miter + `sat -tempinduct` 形式等价，找出哪些未优化 wire 与 `stateReg == 2'h2` 恒等；把这些 wire 的 `@[...]` 注解收集成集合；写 `output/answer.json`。经验证据在 `TASK.md:62-65` 明确允许形式验证、仿真、语义分析三条路径。

### 6. 预期产物

单文件 `output/answer.json`，三个键：`target_signal` 必须精确等于 `"stateReg == 2'h2"`；`target_location_in_optimized_sv` 形如 `"21.23-39"`；`chisel_sources` 是无序集合，元素必须匹配 `Fifo\.scala:\d+:\d+`（`TASK.md:71-87`）。

### 7. reference 与 oracle

`reference/answer.json` 213 B，给出四个位置：`Fifo.scala:26:27`、`Fifo.scala:30:22`、`Fifo.scala:46:20`、`Fifo.scala:59:51`，`target_location_in_optimized_sv` 为 `21.23-39`。它编码的是人工判定的语义对应集合，不是可执行程序。

### 8. 评分与验证

代码事实在 `main.py:159-185`。`_score` 先要求 `chisel_sources` 是 list、每个元素匹配 `^Fifo\.scala:\d+:\d+$`（`:164-169`），再要求三个键都在（`:171-173`），满足才加 0.10；`target_signal` 精确匹配再加 0.10（`:177-178`）；集合相等再加 0.80（`:180-183`）。没有部分分：少一个位置就丢掉 0.80。两处文档与代码不一致必须记录。第一，`target_location_in_optimized_sv` 只检查键存在，值完全不被读取，写错也能拿分。第二，`task_card.json` 的硬门声称“src/、generated/ 或 TASK.md 被修改则 0 分”，但 `_score` 与 `evaluate` 都没有做任何哈希或时间戳校验（`:129-185` 无相关代码），这条硬门实际未实现。另一个可核验的事实是注释与真值的关系：`optimized.sv` 第 21 行的注释列出 `26:27, 27:22, 30:22, 46:20, 51:29, 52:19` 六个位置，其中 `27:22`、`51:29`、`52:19` 不在真值集合里，而真值里的 `59:51` 不在注释里；`59:51` 指向 `io.deq.valid := (stateReg === one || stateReg === two)` 中第二个 `===` 的等号位（第 59 行第 51 列，逐列核对）。这正好印证了“注释既过报又漏报”的任务设定。

### 9. 证据表

| claim | source | evidence type | design implication |
|---|---|---|---|
| 真值集合 4 个位置，注释 6 个且只有 3 个重合 | `optimized.sv:21` 注释；`reference/answer.json` | file fact | 代码理解类任务的 oracle 必须人工复核，不能由工具注释直接生成 |
| `target_location` 值不被校验 | `main.py:171-185` | code fact | 答案 schema 的每个字段要么校验要么删掉 |
| “禁止修改源文件”硬门未实现 | `task_card.json` evaluation 段 vs `main.py:129-185` | code fact | 500 条的反作弊门必须有代码实现与测试 |
| 集合相等无部分分 | `main.py:180-183` | code fact | 精确集合类答案的难度集中在完整性，评分要接受“漏一个=错”的设定 |
| 工具链全部是 /opt 薄壳 | `base/software/{yosys,firtool,sbt,python,jq}`、`README.txt` | file fact | 离线软件要固定版本并写进镜像清单 |

### 10. 这个案例证明了什么

它证明代码证据类任务可以用确定性集合评分，不需要 LLM，也证明“工具注释不可信”可以成为任务的核心难度来源。它没有证明 0.80 的集合权重与 0.10/0.10 的格式分是合理配比，没有证明未实现的硬门不会导致刷分，也没有证明四个真值位置在形式等价意义下完整（需要重跑 miter 才能确认，NOT_RUN）。

## C6 legal/legal_dr_fees_01

这一条是法律文档产物：按七份中文收费材料算出五个仲裁案件的费用，判定是 15 个数值的十进制容差比较。

### 1. 身份

domain legal，taxonomy `domain_id 7`、`subdomain_id 7.2`、`subdomain_code legal_research`，2026-05-28 从 7.1 litigation 改判（`inputs/frozen/01_agents-last-exam/tasks/legal/legal_dr_fees_01/task_card.json:75-92`）。slug legal_dr_fees_01，已发布变体 base。旧仓库三个文件：`task_card.json` 4,789 B、`main.py`、`scripts/score_outputs.py`。

### 2. 真实任务说明

taskPrompt 在 `task_card.json:9`，要求按北京仲裁委员会（BAC）收费材料算五个案件的机构费、仲裁员报酬与总费用。包内 `input/task_brief.md`（1,546 B）重复同一要求并给出五个争议金额：5,800,000.00、65,902,536.17、882,480,634.38、251,620,139.47、3,215.00 元（`task_brief.md:20-28`）。Case 4 的特殊条件是“当事人在申请仲裁前已就争议达成和解协议”（`task_brief.md:25-27`）。任务还规定 closed-book：只能用 `input/` 下材料，禁止外部检索与监管知识（`task_brief.md:6-9`）。

### 3. 输入资料

七份中文 PDF 共约 1 MB：小时费率操作指引 112,109 B、案件收费标准 309,594 B、收费标准实施细则 198,871 B、案件退费标准 93,577 B、调仲对接快速程序撤案退费标准 55,221 B、调仲对接快速程序案件收费标准 77,243 B、收费标准及细则操作指引 157,455 B。`input/document_manifest.json` 2,449 B，逐份给 `document_id`、`filename`、`format`、`relative_path`、`sha256`；`input/cases.json` 702 B 给五个案件与金额；`input/output_contract.json` 807 B 给字段与示例形状；`input/runtime_env/pyproject.toml` 144 B。PDF 是公开监管文本的副本（inference，基于标题与文件体积），快照里没有抽取过正文。

### 4. 软件环境

`task_card.json:6-8` 只写 Python；`task_card.json:70-74` 写 `c4-standard-4`、`cpu-free-ubuntu`、超时 7,200 秒；`requiredSystemPackages` 为空数组（`task_card.json:93`）。`software/python3.12` 68 B 是薄壳，`software/README.txt` 96 B 说明入口。

### 5. 操作流程

读 task_brief 与 cases.json；在七份 PDF 里找到收费表与细则；按争议金额套阶梯费率算机构费；按收费表算仲裁员报酬；判断 Case 4 的和解条件是否触发退费或折扣；把 15 个数写成两位小数；写 `output/arbitration_fee_results.json`。这是典型的“文档检索 + 规则套用 + 数值计算”多步流程，全部证据在离线 PDF 内。

### 6. 预期产物

恰好一个文件 `output/arbitration_fee_results.json`，顶层键 `cases`（`output_contract.json` 的 `required_top_level_key`），每个案件给 `institution_fee_rmb`、`arbitrator_remuneration_rmb`、`total_fee_rmb`，都是两位小数的 RMB 金额。

### 7. reference 与 oracle

`reference/answer_key.json` 1,141 B：五个案件各四个金额（含 `amount_in_dispute_rmb`），加 `component_weights`（7/7/6）与 `tolerance_rmb: "0.01"`。数值为 case_1 27,100.00 / 59,000.00 / 86,100.00；case_2 205,756.34 / 270,297.86 / 476,054.20；case_3 1,749,465.14 / 2,353,953.52 / 4,103,418.66；case_4 147,269.57 / 197,553.09 / 344,822.66；case_5 5,000.00 / 12,000.00 / 17,000.00。同一组数值还被硬编码在 `scripts/score_outputs.py:16-47` 的 `ANSWER_KEY` 里，两处必须同步，否则参考文件与评分不一致。

### 8. 评分与验证

代码事实：`TOLERANCE = Decimal("0.01")`（`scripts/score_outputs.py:8`）；`COMPONENT_WEIGHTS` 机构费 7、报酬 7、总费 6（`:10-14`）；`score_submission` 遍历 `ANSWER_KEY` 五个案件，每字段按 `abs(submitted - expected) <= 0.01` 判对（`:152-157`），分母是 `20 * 5 = 100`（`:142`），最后 `score = earned / total_points`（`:167`）。输入被宽容地归一化：字段名有别名表（`:49-59`），案件 id 接受 `case_1`、`case1`、`1`、整数 1 等写法（`:86-101`），顶层可以是 `{"cases": [...]}`、裸 list 或 `{case_id: {...}}` 字典（`:104-129`）。一个重要发现是 `main.py:164-185`：它读取并 `json.loads` 了 `reference/answer_key.json`，但结果赋给 `_` 后丢弃，真正评分用的是代码内硬编码的 `ANSWER_KEY`；缺输出或缺 answer key 都返回 `[0.0]`（`:169-174`），JSON 解析失败也返回 `[0.0]`（`:180-182`）。因此参考文件的角色是“给人和审计看的副本”，不是评分输入。另有一处口径差异：`output_contract.json` 要求顶层键 `cases`，而评分器同时接受裸 list 与字典。

### 9. 证据表

| claim | source | evidence type | design implication |
|---|---|---|---|
| 15 个数值、容差 0.01、权重 7/7/6 | `scripts/score_outputs.py:8-14`、`:152-167` | code fact | 数值类任务要给逐字段权重与统一舍入口径 |
| 评分不读 reference/answer_key.json | `main.py:177-179` | code fact | 参考数据必须只有一份权威副本，避免双写漂移 |
| 案件输入被多种写法接受 | `scripts/score_outputs.py:49-129` | code fact | 输出契约要声明“接受哪些等价形状”，否则隐藏要求 |
| Case 4 的和解条件只写在题面 | `task_brief.md:25-27`、`cases.json` 的 `special_condition` | file fact | 特殊规则必须可判定，否则会变成猜出题人意图 |
| 七份 PDF 带 sha256 清单 | `input/document_manifest.json` | file fact | 资料引用要可校验，防止 PDF 被替换 |

### 10. 这个案例证明了什么

它证明文档检索类任务可以收敛成一组确定的数值答案，并用 Decimal 容差稳定评分；也证明官方会用“输入归一化 + 字段别名”来避免格式差异误伤。它没有证明这 15 个数能从七份 PDF 复算出来——快照环境没有 pdftotext 或 PDF 解析库，正文从未被抽取，这一项是 NOT_RUN；它也没有证明 Case 4 的特殊条件确实改变了答案（答案键里看不到折扣痕迹）。

## 跨案例综合

六条案例在四个维度上分化，这四维决定了 500 条的契约设计。

第一维是答案基数。C1 是一个工作簿里的 43 个检查点；C2 是 191 个字段里的约 39 个计分项；C3 是三个文件、其中两个由数值不变量约束；C4 是两个必须互相一致的文件；C5 是一个四元素集合；C6 是 15 个数。基数从 3 到 191，说明“契约”不能只有一种粒度。

第二维是证据形态。C1 与 C2 的输入是文档与表单，证据在单元格与字段里；C3 与 C4 的产物是二进制或半结构化 3D 文件，证据必须靠解析器提取；C5 的证据全在源代码与工具输出里；C6 的证据在 PDF 正文里。对应地，验证器分别用 openpyxl/公式求值、JSON 字段比较、NIfTI 解析、Blender 几何比较、正则与集合、Decimal 比较。没有一种通用比较器能覆盖六者。

第三维是判定确定性。C2、C5、C6 完全确定；C1、C3 确定但依赖解析器实现（浮点、仿射、样式）；C4 含 LLM 判定，是唯一非确定的。官方对非确定判定的处理是“拆成 8 条二元问题 + 保存原始回答”，这比一个 1–10 分的整体打分更容易复核。

第四维是失败模式。硬门失败（缺文件、格式错、几何不一致）在六条案例里都是 0 分；部分分出现在 C1（43 项占比，reward 直接取 score）、C2（逐字段）、C3（0.7/0.3）、C4（8 问）；C5 的集合部分 0.8 是二值，但仍有 0.2 格式分。C1 的 `passed` 与 C4 的 `passed` 只是报告字段，不决定 reward，不能把 `passed` 当分数。500 条如果统一按“检查项比例”给分，会与官方的二值通过字段风格不一致，需要在契约里显式声明。

**专家必须提供的字段。** 按原型分四组。表格/工作簿原型（C1）：节名与顺序、每个标签的精确文本、每个值的来源单元格或公式依赖、容差、表头样式要求、允许的 sheet 名匹配方式。表单/数值原型（C2、C6）：字段清单与类型、哪些字段计分（informative）、数值容差与舍入、字段别名、多解答案（alt reference）、输入归一化规则。二进制/3D 原型（C3、C4）：几何契约（shape/affine/单位/坐标系）、派生量的定义与容差、渲染视角与判定问题、产物一致性阈值（1 mm）、禁止的格式。代码证据原型（C5）：目标符号、允许的工具链版本、真值集合、集合比较口径、源文件不可修改的校验方式。

**专业审核该看什么。** 表格原型看“标签是否唯一可定位、公式是否真的依赖输入、是否存在硬编码也能过”；表单原型看“题面数字与 GT 是否一致、alt 通道是否覆盖合法歧义、硬门是否误伤等价写法”；影像原型看“几何契约是否足以排除错误重采样、派生统计是否唯一确定 mask、截图是否真的被检查”；3D 原型看“参考渲染是否可重建、8 条问题是否覆盖图纸要求、LLM 判定是否有稳定性记录”；代码原型看“真值集合是否人工复核、反篡改门是否有代码”；法律原型看“每个数字能否在 PDF 里找到出处、特殊条件是否可判定”。

**共同缺口。** 六条案例的评分代码全部在旧任务仓库里，数据包内没有一份验证器；C1 的参考工作簿是提交者提交件的字节副本，C3 的参考只有一个统计 CSV，两者都不构成独立复算；C2 的 alt GT 与主 GT 在 10 个字段上互相矛盾，需要先判定哪条是准的；两条案例（C1 的实时字段、C4 的图像判定）存在不可复现或非确定的验证环节；一条案例（C5）的硬门写在文档里但没有实现。这些不是个别瑕疵，而是官方形态的常态，500 条必须在契约层把“oracle 独立性”“验证器随包”“非确定判定的复核记录”写成硬要求。

## ALE-data 数据合同要求

先给官方事实。`inputs/frozen/03_ale-data/task-data-v1.1/` 下 13 个 domain 目录、122 个任务目录、122 个变体目录，共 79,065 个文件、磁盘占用约 50 GB。每个变体目录只有三类子目录：104 个包有 `input/`、`reference/`、`software/` 三件套；16 个包只有 `input/` 与 `reference/`；2 个包只有 `input/` 与 `software/`（`engineering/cailian_road_highway_alignment_2/base`、`engineering/inner_support_elevation_optimization/base`，两者都没有 `reference/`）。包内文件数中位数 16，最少 3（`computing_math/newyear_keygen2/base` 等三个），最多 41,775（`life_sciences/idp_ensemble_scoring/default`，约 11.8 GB）。变体根目录下没有 `output/`，唯一的 `output` 目录是 `engineering/chisel_verilog_alignment_seq_1/base/input/workdir/output`（含一个 0 B 的 `.keep`）。

包级 `PACKAGE.json` 不存在。对整个 `task-data-v1.1` 递归查找 `PACKAGE*.json` 命中 2 个，但两个都是任务内容而非包描述：`computing_math/k8s_migration_1/base/input/app/frontend/PACKAGE.json` 是前端应用清单，`visual_media/skeletal_animation_reproduction/.../reference/PACKAGE.json` 是参考产物；没有任何任务根或 `base/` 下的包级元数据。`docs/02-plan.md:68` 写“包结构按 `task-data-v1.1`，`PACKAGE.json` 边车可以放平台字段”，`docs/02-plan.md:135` 写“全部按冻结的 `task-data-v1.1` 和 `PACKAGE.json` 契约”，这两句是平台设计意图，不是对官方包现状的描述。官方包里没有任何边车文件，平台要放自己的字段，只能新增文件并自己定义校验规则。

官方唯一的发布级元数据在 `inputs/frozen/03_ale-data/archive/release-v1.1.json`：`version: "1.1"`、`source_revision: "5e077cc254535f479e425ad3aaa4621dce62fc00"`、`selected_tasks: 122`、`logical_members: 79494`、`archive.bytes: 39155440558`、`archive.sha256`、`data_manifest_sha256`。逐文件元数据在 `selected-members.jsonl`，每行五字段：`path`、`bytes`、`mode`、`sha256`、`type`。`inputs/frozen/03_ale-data/archive/README.md` 说明存档包含 input、setup software 与 evaluator references，保留原生文件名、权限与符号链接，访问受 gated 审批。

把 122 个包逐目录名与 `published_tasks.json` 比对，119 个任务完全一致，3 个任务的变体名对不上：`other/mota_exploration`（发布清单写 `images`，包里是 `mota_24_ez`）、`visual_media/uv_reproduction`（`images` vs `uv_reproduction_anime_singing_girl`）、`visual_media/skeletal_animation_reproduction`（`images` vs `skeletal_animation_reproduction_singing_anime_character`）。这说明 `published_tasks.json` 在变体粒度上不是可靠的连接键。

**一个包必须携带什么。** 从六条案例能反推出四类必需内容。第一类是 `input/`：任务所需的全部资料，且必须离线自足；C2 的 HTML 表单、C3 的 8.66 GB 容器镜像、C4 的 50 MB 图纸都属于这一类。第二类是 `reference/`：判定所需的真值，形态可以是 manifest（C1）、GT JSON 与 alt JSON（C2）、单行 CSV（C3）、14 张参考渲染（C4）、答案 JSON（C5）、answer key（C6）。第三类是 `software/`：启动器与包装器，通常是 `/opt/...` 薄壳或 winget 引导脚本，不保证每个包都有。第四类是随包的验证入口——官方包里没有，这是最大的缺口。

**官方包实际缺什么元数据。** 缺任务身份（domain/subdomain/taxonomy 只在旧仓库 `task_card.json` 里）；缺指令入口（六个案例的指令文件分别是 `instruction.md`、`instruction.txt`、`TASK.md`、`README.md`、`task_brief.md`，C3 甚至没有包内指令文件，prompt 只在 `task_card.json:9`）；缺软件版本的机器可读声明（版本写在旧仓库 task_card 或包装器注释里）；缺 VM 规格（`c4-standard-4`、`cpu-free-ubuntu`、超时 7,200 秒都只在旧仓库）；缺验证器与验证配置；缺预期产物的完整清单与容差；缺专家字段与审核记录；缺许可与 PII 标记（七份法律 PDF 与医学影像都没有许可证文件）。

**自动组包还要补什么。** 一个能自动生成官方等价包的系统，至少要在包根放一份平台自己的清单，声明：任务身份与 taxonomy、contract kind、指令入口的相对路径、`input/` 清单与哈希、`reference/` 清单与哈希、软件版本与镜像依赖、验证器入口与哈希、预期产物路径与格式、容差与评分口径、专家与审核元数据、许可与 PII 字段。这份清单就是平台设计里的 `PACKAGE.json`，但它必须被明确标注为平台新增，不能声称官方已有。校验器要能拒绝四类包：缺验证器、`reference/` 为空、指令入口不存在、声明路径与磁盘不一致。

## 映射表

| case | contract.kind | 必需任务源字段 | reference / 验证要求 | 审核重点 |
|---|---|---|---|---|
| C1 | tabular_columns | 节名与顺序、标签文本、固定值、公式依赖、容差、样式 | manifest 五段（headers/fixed/formulas/dashboard/live）+ 独立复算的工作簿 | 公式是否依赖输入、实时字段是否已快照化、oracle 是否独立 |
| C2 | numeric_cases | 纳税人资料、来源表单、字段类型、informative 清单、alt 答案 | 主 GT + alt GT + 硬门 schema | 题面与 GT 是否一致、alt 是否覆盖合法歧义、等价写法是否被误杀 |
| C3 | artifact_diff | 输入卷、几何契约、统计定义、截图要求、容差 | 统计 CSV + 几何契约（shape/affine）+ 可读性检查 | mask 是否唯一确定、截图是否真被检查、镜像是否随包 |
| C4 | artifact_diff | 图纸、锚点、坐标约定、必需构件、一致性阈值、判定问题 | 14 张参考渲染 + eval_config（8 问）+ 参考 OBJ | 参考渲染可否重建、判定问题是否覆盖图纸、LLM 稳定性 |
| C5 | code_artifact | 源文件、优化输出、目标子表达式、工具链版本、真值集合 | answer.json（集合）+ 正则与 schema | 真值是否人工复核、反篡改门是否实现、集合权重是否合理 |
| C6 | document_qa | 案件金额、收费表、特殊条件、字段与容差 | answer key（15 数）+ 权重 | 每个数能否溯源到 PDF、特殊条件是否可判定、参考是否双写 |

## 未知项与解决证据

未知项一：C1 的参考工作簿在评分器下是否得 1.0。解决证据：在隔离环境跑一次 `scripts/score_workbook.py`，输入 `reference_workbook.xlsx` 与 `reference_manifest.json`，看 43 项是否全过。当前状态 NOT_RUN，因为任务书禁止运行官方任务代码。

未知项二：C6 的 15 个数能否从七份 PDF 复算。解决证据：用 PDF 文本抽取工具取出收费表正文，按阶梯费率重算五个案件，尤其确认 Case 4 是否触发折扣。当前快照没有 `pdftotext` 也没有 `pypdf`，NOT_RUN。

未知项三：C4 的 8 条 LLM 判定在不同模型、不同次运行下的稳定性。解决证据：同一组 14 张参考渲染与同一份候选渲染，用固定模型重复判定 5 次，记录每题 YES/NO 的翻转率。快照里没有历史判定记录，unknown。

未知项四：C3 的 1e-6 容差是否唯一确定 mask。解决证据：构造两个仅在边界体素上不同的最近邻重采样，看是否都能通过；若都能通过，说明 oracle 允许一族解。当前未构造，unknown。

未知项五：官方是否存在未冻结进快照的 `PACKAGE.json` 契约。解决证据：查 ALE 官方仓库与 HF 数据集的最新 revision，确认 1.1 之后是否新增边车文件。快照的 `source_revision` 是 `5e077cc254535f479e425ad3aaa4621dce62fc00`，之后的变更不在快照内，unknown。

未知项六：C5 的四个真值位置在形式等价意义下是否完整。解决证据：按 TASK.md 给的方法用 yosys miter + `sat -tempinduct` 枚举所有未优化 wire，确认没有第五个恒等 wire 指向别的行。当前未运行，NOT_RUN。

## 对 500 条生产的直接含义

第一，500 条的每条都必须带自己的验证器，且验证器要能在包内被定位与哈希；官方形态把验证器留在旧仓库，这个做法不能复制。

第二，oracle 必须独立于提交件。C1 的参考工作簿与提交件字节相同，C2 的 alt GT 与主 GT 只差 10 个字段，C3 的参考只有一个 CSV——这些都说明“参考”在官方语境里是宽松的，ALE 500 若沿用会让评分退化成“像不像提交者”。

第三，说明书里写了的硬门必须有代码实现。C5 的“禁止修改源文件”是现成反例；C2 的顶层键硬门则是正面例子。审核清单要加一条“文档声称的每个 0 分条件，在评分代码里能找到对应分支”。

第四，多解要显式建模。C2 的 alt reference 是唯一一个处理了题面与 GT 冲突的机制；500 条一旦出现等价答案，必须有同构的 alt 通道，否则正确解会被判错。

第五，非确定判定要留证据。C4 的 8 条二元问题与逐题落盘的 `raw_response` 是可复核的写法；500 条如果用 LLM 判定，至少要保留问题、图片、原始回答与模型版本四项。
