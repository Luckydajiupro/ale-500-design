# A-G 只读复审回传记录（执行方回传原文）

来源：执行方在 A-G 复审（R1 复审核查）后的聊天回传原文（m00717，2026-11-09 15:44:26 +0800）。
本文件由 R2 进场时从压缩会话块 b24 恢复并落盘，仅增加本头部说明，正文未改动。
共 9 个 A-G 问题定位与证据都在正文里，R2 修复以此为准。

**本轮目标。** 只读复查 R1 目录七份文件的版本一致性，并对 A 至 G 七项逐条给出盘上证据，结论直接回传聊天，全程零写入，不宣布复审通过。

## 1. 版本核对表

磁盘 SHA256 现算，与 SOURCE_MANIFEST_R1.json 的 r1_sha256 登记值比较。相对路径以 `analysis/phase0-official-baseline-r1/` 为根。

| 文件 | 磁盘 SHA256（前16位） | 清单登记 | 结果 |
|---|---|---|---|
| 03_repo_structure_comparison.md | `83db547a9f10a859` | 83db547a9f10a859 | 一致 |
| 04_task_inventory.csv | `9d73e17515b594eb` | 9d73e17515b594eb | 一致 |
| 06_runtime_provider_matrix.md | `31f22482d41ccd60` | 31f22482d41ccd60 | 一致 |
| 07_old_new_format_comparison.md | `3f4ce84e6eef3ee8` | 3f4ce84e6eef3ee8 | 一致 |
| 08_coverage_matrix_draft.csv | `91f5e5f5ad867978` | 91f5e5f5ad867978 | 一致 |
| 09_unknowns_and_decisions.md | `394398ef532a3e5e` | 394398ef532a3e5e | 一致 |
| R1_VALIDATION_REPORT.md | `c46736611810e944` | 未登记 | 未登记 |

六个已登记文件全哈希完全一致。R1_VALIDATION_REPORT.md 不在清单 `files` 也不在 `r1_evidence` 里，按你的要求写未登记，没有补写清单。evidence/validate_r1_output.txt 同样未登记，此处一并说明。

## 2. A 至 G 结果总表

| 项 | 核查内容 | 结果 |
|---|---|---|
| A | 03 输入投递行是否仍写 artifacts | 确认问题 |
| B | 06 是否仍有 merge point 残句，是否已合并 | 确认问题，实际未合并 |
| C | 5 个 staged-local 的系统归属，09 是否仍写 5 个在 Windows | 确认问题 |
| D | gui unknown 且低风险的行，及判定逻辑 | 确认问题 |
| E | 08 social 唯一任务与 other 最大任务的名称字节 | 确认问题，两处名字字节错位 |
| F | 97 项检查的真实统计与覆盖 | 确认问题，报告分组合计与明细对不上 |
| G | 哈希检查的实际范围 | 部分符合，R1 主文件与证据只查存在 |

下面是逐项原文。

## 3. 各项原文

### A. 03 的输入投递行

03_repo_structure_comparison.md:53 表头。

`| 维度 | 01 旧仓库 | 02 新引擎 | 03 数据 dump | 04 模板仓库 |`

03_repo_structure_comparison.md:60。

`| 输入投递 | taskPrompt 点名 base/input 可见文件 | artifacts 表列产出路径 | input 目录 | 由 instruction 与 environment 决定 |`

02 新引擎格的输入投递一栏仍写 artifacts。07 的纠正语义在同目录两处相反。07_old_new_format_comparison.md:11。

`artifacts 是输出收集路径，不是输入清单 [code: taskspec.py:74-84]`

07_old_new_format_comparison.md:495-496 的清单对照表。

`| 输入清单 | inputFiles 数组… | 无输入清单字段，输入走镜像文件、setup 脚本与 HF 资产 [code: assets.py, doc: task-authoring.md:362-372] | /`

`| 输出清单 | 无对应字段 [cmd: 顶层键列表] | artifacts 数组，声明输出收集路径 [code: taskspec.py:74-84] |`

结论。03:60 格子里的文字说的是产出路径，本身没有写错语义，但把输出收集概念放在输入投递维度上，与 07:495 的新格式无输入清单结论错位。03 全文对 artifacts 只有这一处提及。

### B. 06 的合并残留

六处残句全部在盘上。06_runtime_provider_matrix.md:391。

`任务级外部服务普查的权威数字属于数据侧审计方，本文件留合并点 [inference: 边界划分]。`

06_runtime_provider_matrix.md:392。

`第一轮 06 第 62 到 73 行的 8 任务表沿用第一轮口径，标记为待 R1 数据证据合并，三个级别照旧。`

06_runtime_provider_matrix.md:398。

`merge point。数据侧 R1 的最终三分类表到位后，本节由项目负责人拼接替换。`

还有 06:394（本地服务需重新宿主的推断注记）、06:399（不重复第一轮 8 行表格原文）和 06:511。

`本文件不以第一轮的 6 个 yes 当定稿，等数据侧 R1 清单合并。`

实际是否合并。没有合并。在 06 里检索 13 个与三分类终稿数字，命中只落在 394 至 398 行的残句本身，没有任何 5/6/2 分级或 13 个的终稿表。数据侧终稿实际在这里：04_task_inventory.csv 的 external_service 列、evidence/staged_local_os.tsv、09_unknowns_and_decisions.md:31。06 本节没有引用它们。

### C. staged-local 的系统归属

04_task_inventory.csv 里 external_service 为 staged-local 的五行，逐条。

| task_id | OS |
|---|---|
| business_finance/bpmn_supply_disruption_l3 | Linux |
| business_finance/bpmn_category_governance_restructuring_l3 | Linux |
| business_finance/metabase_bi_dashboard_01 | Windows |
| business_finance/odoo | Windows |
| business_finance/taxform_4_1 | Windows |

evidence/staged_local_os.tsv 头部五行与上表一致，2 个 cpu-free-ubuntu 加 3 个 cpu-free，并带 localhost 证据串 8080/flowable、3000、8069、8080 forms。

但 09_unknowns_and_decisions.md:63 仍写。

`Windows 集内有 3 个 GPU 任务与 5 个 staged-local 应用任务。[cmd]`

同篇 09:31（第 9 号开放项）没有系统归属的断言，是对的。R1_VALIDATION_REPORT.md:34（R04 行）写。

`5 个 staged-local 拆分 2 Linux 3 Windows。[已修]`

结论。09:63 是漏改的一颗旧 bullet，把 2 Linux 3 Windows 写成了 5 个都在 Windows 集。修正后的口径分布在 04、staged_local_os.tsv 和报告 R04 行，09:63 没跟上。

### D. gui unknown 与低风险

04 里 gui_status 为 unknown 且工程或审计风险以 low 开头的行，共 5 条，三列值如下。

| task_id | gui_status | engineering_risk | audit_risk |
|---|---|---|---|
| business_finance/basel_operational_risk_bia_cn | unknown | low (heuristic: no heavy factors) | low (heuristic: no heavy factors) |
| engineering/inner_support_elevation_optimization | unknown | medium (heuristic: docker exception) | low (heuristic: no heavy factors) |
| life_sciences/cell_translocation_analysis | unknown | low (heuristic: no heavy factors) | low (heuristic: no heavy factors) |
| life_sciences/yeast_colony_detection | unknown | low (heuristic: no heavy factors) | low (heuristic: no heavy factors) |
| transport_safety/fds_single_compartment_detector_reconstruction | unknown | low (heuristic: no heavy factors) | low (heuristic: no heavy factors) |

unknown 全集是 9 条，另外 4 条是 ar_full_1500 high/high、newyear_keygen2 medium/medium、humanoid_velocity_tracking_policy high/medium、butterfly_flap_animation medium/medium。

判定逻辑原文在 scripts/20_build_04_05.py。第 251 行，工程侧因子。

`if gui_of(tid) == "yes": factors.append("GUI workflow")`

unknown 不进入 factors。第 253 至 257 行定高、中、低。high 条件是 assets、staged-local、gpu、online-required。medium 是 windows VM、docker exception、GUI workflow、public-ref。其余落 low(no heavy factors)。第 270 行审计侧同样只认 yes。第 281 至 290 行 gui_of 从 GUI_YES（29 行）和 GUI_UNKNOWN（71 行）两个字典取值，返回三值。

所以 unknown 对分级的影响是零。它既不能抬级也不能降级，任务带 unknown 且没有其他重因子时，自动落在 low(no heavy factors)。GUI_UNKNOWN 字典里对这 5 条的原始依据，20_build_04_05.py:74（inner_support 的 Kratos 走 Python CLI）、76（basel 的 prompt 只要求文件输出）、77（fds 的纯 CLI 合约）、78（yeast 的 CellProfiler 入口按条件提供）、79（cell_translocation 的可选 Python wrapper）。

交叉面。09_unknowns_and_decisions.md:51 的 Tier A 建议确实把 9 个 unknown 放进全面复核，写的是。

`GUI 40 个明确任务加 9 个 unknown [suggestion]`

但 R1_VALIDATION_REPORT.md:38（R08 行）写。

`UNKNOWN 不自动落入低风险。见 09 与 10 对应节。[已修]`

结论。这个 [已修] 在 09 的 P3 分层面成立，在 04 的工程与审计两列不成立，那里有 5 条 unknown 落在 low。两张表面的口径不一致，报告把一张表面的修正写成了整体已修。

### E. 类别与大资产归属

08_coverage_matrix_draft.csv 的 social_sciences 行写。

`唯一任务 abm_hangzhou_metro 469,325,814 B (0.44 GiB)`

04 里 social_sciences 下唯一任务是 social_sciences/atwood_2022_measles_vaccine_reproduction，approx_size_kb 458,325。独立按 FILE_SHA256SUMS.txt 前缀求和，atwood 为 469,325,814 B，25 个文件，与 08 的字节数吻合。abm_hangzhou_metro 实际是 transport_safety 的任务（full.txt:112，01 仓库 tasks 目录与 03 数据目录同证），字节 178,304,281，17 个文件。字节数对，任务名是从相邻行抄串了。

08 的 other 行写。

`主体是 mota_exploration 180,191,212 B (171.8 MiB)`

04 里 other 两行。aerobics_wc2026_portugal_trio_difficulty_scoring 175,967 KB，正好等于 180,191,212 B，5 个文件，Linux。mota_exploration 23,279 KB，正好等于 23,838,273 B，268 个文件，Windows。名字和字节两处都错位。

域级总量各文件完全一致（other 204,029,485 B，social 469,325,814 B，08 与 evidence/sizes_scopes.tsv 与 10 三处相同）。错的只是 08 asset_profile 里的任务级名字归属。

### F. 97 项检查的数量与覆盖

evidence/validate_r1_output.txt 共 100 行。97 行以 OK 开头。1 行是 stderr 的 find 报错。1 行空白。末行 `FAILED CHECKS: 0`。没有任何一行以 FAIL 开头，退出码 0。所以 PASS 97，FAIL 0，这个总数是真实的。

按检查名分组逐类统计实际行数。

| 组 | 实际行数 |
|---|---|
| manifest（parses 1 + hashed_at_filled 1 + pre_post 12 + status_set 12 + post_matches_disk 12） | 38 |
| r1 产物存在（10 份修订文件） | 10 |
| 04 系列（列统一、列符合委派 30 加 1 列、id 唯一、域合法、3 项受控词、NOT_RUN） | 8 |
| 05 列统一 | 1 |
| 08 系列（列统一、非 CS 和 500、computing_math 为 0） | 3 |
| 04 与 05 域计数一致 | 1 |
| 10 域字节表对照 sizes_scopes | 13 |
| 证据文件存在（14 份） | 14 |
| 语境合法性扫描 | 3 |
| 10 收尾状态 | 1 |
| inputs-readonly 四项 | 4 |
| progress.log 时间戳 | 1 |

合计 97。注意 10_has_byte_row 是只在失败时打点的检查，13 项全中所以没有输出行。

R1_VALIDATION_REPORT.md:14-27 的分组表数字是 25/9/12/2/3/1/13/14/11/1/4/1，相加为 96，与第 8 行写的共 97 项自相矛盾。逐组对照实际，多处不一致。manifest 报告 25 对实际 38。R1 产物存在报告 9 对实际 10。04 报告 12 对实际 8，且报告的 task_id 唯一 122 实际脚本只查唯一不查 122，列数统一 31 实际只查统一不查等于 31。05 报告 2 对实际 1，TOTAL 行的检查不存在。语境扫描报告 11 对实际 3。

A 至 E 的自动断言覆盖。

| 项 | 是否有对应断言 |
|---|---|
| A | 未覆盖。校验器从不读 03 内容，只查文件存在 |
| B | 未覆盖。06 只被扫敏感词，不查 merge 残句 |
| C | 未覆盖。没有 09 与 04 的 OS 交叉断言 |
| D | 仅词汇。只查 gui_status 三值合法，不查它和风险列的交互 |
| E | 部分。13 项 sizes_scope_agree 校准的是 10 的域级字节表，08 的任务名与单任务字节没有任何断言 |

### G. 哈希检查范围

scripts/validate_r1.py:25-28 对原轮 12 份文件真实读取并算哈希。

`actual = hashlib.sha256(open(op, "rb").read()).hexdigest()`

`check(..., actual == f["sha256_pre"], actual[:16])`

这是确实计算并比较内容哈希，输出里 12 行携带 16 位前缀证明。pre 等于 post 那 12 项（21-23 行）只是清单两个字段的自比，不涉及磁盘。

10 份 R1 修订主文件只查存在，validate_r1.py:31-34 的 r1_output_exists。全文没有任何地方读取清单里的 r1_sha256 值。14 份证据文件在 107-110 行只用 os.path.exists。所以这两组是只检查存在，没有比较内容哈希。

validate_r1_output.txt 本身没有登记哈希，清单里也没有它。文件内含的哈希只有原轮 12 份的 16 位前缀，不含任何 R1 文件或证据文件的哈希。

另外一项空转检查必须说明。validate_r1.py:138 用 `find {IN} -perm /222` 统计可写文件，这条 find 在 macOS 的 BSD find 上非法，报 `find: -perm: /222: illegal mode string` 且退出 1，空输出数出 0 所以检查通过，原因错了。本轮我用 python 的 os.access 全树扫 inputs-readonly 的 115,337 个条目，0 个可写，只读状态本身是真的。轮一验证也只数了 inputs-readonly 的文件个数与哈希清单行数，没有重算 108,117 个文件的哈希。原轮 12 份文件不变，不能扩大成所有原始输入都已复验。此前也没有文件做这个扩大声明，后续也不该做。

## 4. 此前结论超出证据的地方

第一，共 97 项的结论成立（退出码 0、97 行 OK），但报告的分组表与它矛盾，总数真实不等于分组可信。其中 1 项零可写检查是空转，另外报告声称存在的 122 计数、31 列数、05 TOTAL 行检查实际都不在脚本里。

第二，报告 R08 行写 UNKNOWN 不自动落入低风险 [已修]，只在 09 的 P3 分层面成立，04 的工程与审计两列仍有 5 条 unknown 落 low。这个 [已修] 覆盖过宽。

第三，A、B、C、E 四个残留没有任何自动断言兜底，此前 97 项全绿不能覆盖它们。四个残留分别是 03:60 的 artifacts 错位、06 的六处合并残句、09:63 的五任务归 Windows、08 两处任务名字节错位。

