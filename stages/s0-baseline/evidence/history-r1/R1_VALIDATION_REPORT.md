# R1 验证报告

本项目是 Phase 0 的 R1 修订轮。输入只读，官方任务只作参考。500 条交付任务全部来自专家新生产，官方 122 条不自动计入。本报告记录修订完成后的验证结果。

## 范围与方法

- 只读静态解析。没有导入或运行任何官方任务代码。没有运行评测。[方法]
- 自动验证脚本 scripts/validate_r1.py。共 97 项检查，全部通过，退出码 0。[cmd: validate_r1.py 输出, evidence/validate_r1_output.txt]
- 父级人工核查覆盖全部 12 份 R1 产物的交叉一致性。子代理 D 与 E 各自交付附自身校验记录。[cmd + 人工]
- 验证对象清单。R1 目录的全部产物、14 份证据文件、12 份轮一产物的哈希书挡、inputs-readonly 锁状态、四份原始目录状态。

## 自动检查结果

| 检查组 | 项数 | 结果 |
| --- | --- | --- |
| SOURCE_MANIFEST_R1.json 可解析，pre 记录在案，post 与磁盘一致，状态字段就位 | 25 | PASS |
| R1 产物存在性 | 9 | PASS |
| 04 CSV 列数统一 31，列头与委派口径逐项一致，task_id 唯一 122，域集合合法，受控词汇合规，运行状态全 NOT_RUN | 12 | PASS |
| 05 CSV 列数统一，TOTAL 行 | 2 | PASS |
| 08 CSV 列数统一，非 CS proposed 合计 500，computing_math 为 0 | 3 | PASS |
| 04 与 05 域计数一致 | 1 | PASS |
| 10 类别资产表与 evidence/sizes_scopes.tsv 逐域 bytes 一致 | 13 | PASS |
| 14 份证据文件存在 | 14 | PASS |
| 路线与风险措辞上下文合法性扫描 | 11 | PASS |
| 收尾状态语句存在 | 1 | PASS |
| inputs-readonly 零可写位，mtime 锁内，文件总数 108,118，清单行数 108,117 | 4 | PASS |
| progress.log 全部条目带时间戳 | 1 | PASS |

## R01 至 R13 逐项状态

- R01 路线修正。两条链明确分开。官方参考链与专家生产链不混用。103+397 与先转换 71 已被全部写入否定语境。见 00_project_brief.md 目标节与 09 条目 2。[已修]
- R02 嵌套虚拟化前提。不在本轮写入任何 qemu 加 KVM 可用推断。GPU 预算全部表述为未提供。见 06 宿主层与 runtime_claim_audit.md 对轮一 06:90 与 06:92 的裁定。[已修]
- R03 bytes 基准。02 大文件表、10 类别资产表全部以 bytes 为准，MiB 与 GiB 换算口径 1048576 与 1073741824。四档体积口径见 evidence/sizes_scopes.tsv。[已修]
- R04 逐任务重聚合。04 增加 os、gui_status、external_service、linux_runnable 等列。5 个 staged-local 拆分 2 Linux 3 Windows。3 个 GPU 与 3 个大文件逐条归属。见 staged_local_os.tsv、gpu_cross.tsv、file_attribution.tsv。[已修]
- R05 任务板口径。04_ale-tasks-base 的 tasks 下 11 份 task.toml。demo 10 加 example_task 1。见 evidence/template_tasks.tsv 与 02 对应节。[已修]
- R06 格式语义。inputFiles 只在旧格式。artifacts 是新格式输出收集声明。metadata 是自由字典，引擎运行时不解释。转换方向只有两句引文支撑，无随仓转换器。三条链分开记录。见 07 与 engine_format_evidence.md。[已修]
- R07 122 清单扩展。04 从轮一的 12 列扩展到 31 列。没有证据的写 UNKNOWN，没有运行的写 NOT_RUN。gui unknown 不再等同于无 GUI。原题名与展示题名分列。[已修]
- R08 P0-9 定性。P0-9 是决策编号不是流水线阶段。只记录已批 6 项机制。1 GiB 阈值、两名审查者、抽样率全部标建议。UNKNOWN 不自动落入低风险。见 09 与 10 对应节。[已修]
- R09 三层可运行性。旧支持名单、引擎声明、当前宿主机实测分栏。允许名单任务只作候选。8 个 Docker 例外逐条保留原因。见 06。[已修]
- R10 引用证据。轮一引擎侧主张审计结果 32 支持、24 部分支持、10 不支持、9 未探查。见 evidence/runtime_claim_audit.md。历史 rsync 与权限检查全部标注原执行方记录。见 evidence/historical_log_index.md。[已修]
- R11 集合口径。135 张物理卡片对应 122 发布加 13 张额外。数据树与 full.txt 一比一。退休历史 30 条。153 在全输入内未找到。computing_math 排除保留为当前统计过滤。见 evidence/set_diff_report.md。[已修]
- R12 错漏记录只进 R1。chmod 精确表述目录 555、01 与 04 文件 444、03 数据 400。25 个软链接直达目标、最终解析目标、越界、缺失状态全录。见 chmod_wording_check.md 与 symlink_resolution_r1.tsv。[已修]
- R13 许可证据。01 仓 Apache-2.0 代码加 CC BY 4.0 任务数据。02 与 04 无许可文件或声明字段。不下法律结论。见 evidence/license_evidence.md。[已修]

## 剩余 UNKNOWN

数据侧 U1 至 U8 见 evidence/r1_data_notes.md。引擎侧未知项见 evidence/r1_engine_notes.md。对外口径如下。

1. humanoid_wbc_policy_evaluation 的任务卡没有 vm.timeout。时间上限来源 UNKNOWN。[data]
2. 9 个任务 gui unknown。GUI 软件在包内但任务是否强制运行 GUI 无证据。[data]
3. computing_math 的官方类目描述不在输入内。CS 分类是项目过滤决策。[data]
4. 历史 153 或 152 在输入内无任何出现。[data]
5. 部分评分入口函数名静态不可见。[data]
6. 13 张额外卡片没有状态字段。未发布或是 demo 是推断。[data]
7. atlas_outpost_graybox_navigation 提示文说 Windows GPU VM，快照却是 cpu-free。[data]
8. 3 个任务 software 字段为空，以 main.py 顶层导入兜底。[data]
9. 12 份轮一产物的原错漏已修，但 09 保留 16 项开放决策。500 条排产、Windows 取舍、外部服务重宿主、GPU 采购、体积成本核算全部待负责人裁决。[parent]
10. 新版本镜像配方未经真实运行验证。Windows 与 qemu 路径本轮全部 NOT_RUN。[engine]

## 变更文件清单

| 文件 | 轮一来源 | r1_sha256 前 16 | 状态 |
| --- | --- | --- | --- |
| 00_project_brief.md | 同名 | 2c31732ba1386a4d | 复制后修订 |
| 02_repo_inventory.md | 同名 | a60c74375f7dd1af | 复制后修订 |
| 03_repo_structure_comparison.md | 同名 | 83db547a9f10a859 | 复制后修订 |
| 09_unknowns_and_decisions.md | 同名 | 394398ef532a3e5e | 复制后修订 |
| 10_phase0_summary.md | 同名 | f254372e718fa9b6 | 复制后修订 |
| 04_task_inventory.csv | 同名 | 9d73e17515b594eb | 子代理 D 重写 |
| 05_task_category_summary.csv | 同名 | f2bc36a1b8683119 | 子代理 D 重写 |
| 08_coverage_matrix_draft.csv | 同名 | 91f5e5f5ad867978 | 子代理 D 重写 |
| 06_runtime_provider_matrix.md | 同名 | 31f22482d41ccd60 | 子代理 E 重写 |
| 07_old_new_format_comparison.md | 同名 | 3f4ce84e6eef3ee8 | 子代理 E 重写 |
| 01_baseline_manifest.json | 同名 | 未复制 | 引用轮一原文件 |
| parse_progress.log | 同名 | 未复制 | 引用轮一原文件 |

未在上表的新增文件。CHANGELOG_R1.md、SOURCE_MANIFEST_R1.json、R1_VALIDATION_REPORT.md、progress.log、EXECUTION_BRIEF_FROM_CHAT.md、evidence 全目录、scripts 全目录。

## 证据位置

- evidence/sizes_scopes.tsv 四档体积口径。
- evidence/file_attribution.tsv 大文件逐条归属。
- evidence/gpu_cross.tsv GPU 与快照交叉。
- evidence/staged_local_os.tsv 外部服务分级与系统。
- evidence/template_tasks.tsv 模板任务清单。
- evidence/set_diff_report.md 集合差异与退休历史。
- evidence/symlink_resolution_r1.tsv 软链接解析。
- evidence/chmod_wording_check.md 权限表述核对。
- evidence/r1_data_notes.md 数据侧冲突表 C1 至 C16 与未知表 U1 至 U8。
- evidence/engine_format_evidence.md 引擎格式证据。
- evidence/runtime_claim_audit.md 轮一引擎主张审计。
- evidence/historical_log_index.md 历史日志索引与名称修正记录。
- evidence/license_evidence.md 许可证据。
- evidence/r1_engine_notes.md 引擎侧笔记。
- evidence/validate_r1_output.txt 本轮自动验证原始输出。
- scripts 目录 15 个脚本全部可重跑。父级 40_reconcile_parent_files.py 与 validate_r1.py 尤为重要。

全部证据文件 SHA256 记录在 SOURCE_MANIFEST_R1.json 的 r1_evidence 段。

## 越界写入审计

- inputs-readonly 零可写位，mtime 无晚于最后合法记录写入，文件总数与清单行数吻合。[cmd]
- 四份原始目录状态。三个 git 仓 clean，HEAD 分别 2e91edd、73517c2、492249a。ale-data 文件数 79,070 不变。[cmd]
- 轮一 12 份产物哈希书挡。pre 与 post 一致，磁盘哈希等于记录值。[cmd]
- 原始 DIRECTORY_SUMMARY_REPORT.md mtime 2026-11-09 00:11:44，早于 R1 启动。[cmd]
- .audit 目录在 R1 期间零写入。[cmd]
- R1 期间写入只发生在 analysis/phase0-official-baseline-r1 子树内。[cmd]
- 没有执行任何 git 变更、环境安装、官方任务运行、平台或转换器开发。[方法]

## 未验证即不声明通过的项

- R1 未运行任何官方任务。04 全部行 run_state_current 为 NOT_RUN。
- 新引擎 Windows 配方与 qemu 路径未实测。
- 专家新生产能力未实测。500 条覆盖矩阵仍是草案。
- 上述项不构成 PASS。它们保持 NOT_RUN 或 UNKNOWN。

## 结论

状态。Phase 0 R1修订完成，待复审。

本轮的修改、证据与验证记录可以支撑复审。停止等待人工复核。不自动放行，不进入 Phase 0.5 与 P1。