# Phase 0 最终基线验证报告

生成时间:2026-11-10T10:59:28+08:00。本报告的全部检查数据来自 evidence/final_validate_results.json 与 SOURCE_MANIFEST_FINAL.json,没有手工填写的数字。[方法: scripts/final_validate.py + scripts/50_build_final_report.py]

## 1 范围与方法

- 独立校验器 scripts/final_validate.py。违例即失败,退出码非零即不放行。[方法]
- 检查对象。10 份最终文件、PHASE0_FINAL_REPORT.md、三份数据表统计、跨文件术语与结论、全部引用路径、状态表述、三个 Git 仓库、inputs-readonly 锁定、继承来源哈希、最终校验和清单。
- 本轮不运行官方任务,不安装环境,不开发平台或转换器。run_state_current 全部保持 NOT_RUN。[约束: 任务书 evidence/history-final/EXECUTION_BRIEF_FINAL_CHAT.md]

## 2 自动检查结果

- 总检查数 41。通过 40 项,失败 0 项,错误 0 项,跳过 1 项。必过项缺口 0 个。
- SKIP 说明。fv-07 的对象是 FINAL_VALIDATION_REPORT.md status,原因是 validation report is regenerated after the freeze run; its closed status is checked in --verify-sums。

| 检查项 | 对象 | 判定 | 证据 |
| --- | --- | --- | --- |
| fv-02a | 04_task_inventory.csv | 通过 | rows=122 unique_ids=122 |
| fv-02b | 04_task_inventory.csv | 通过 | header_cols=31 uniform=True |
| fv-02c | 04_task_inventory.csv vocab | 通过 | gui=['no', 'unknown', 'yes'] ext=['none', 'online-required', 'public-ref', 'staged-local'] lr=['allowlist', 'doc_exception', 'none'] run={'NOT_RUN'} |
| fv-02d | 04_task_inventory.csv domains | 通过 | domains=13 cs=19 |
| fv-03a | 05_task_category_summary.csv | 通过 | total_rows=1 total=['TOTAL', '122', 'n/a', '103', '103 个非 CS 域任务 retained_for_500 口径；122 为官方 full.txt 任务总数。windows 总计=36；staged-local=5；gpu=3；docker_exception=8。'] |
| fv-03b | 05_task_category_summary.csv vs 04 census | 通过 | 05_domains=13 equal=True |
| fv-04a | 08_coverage_matrix_draft.csv | 通过 | non_cs_rows=12 sum=500 |
| fv-04b | 08_coverage_matrix_draft.csv | 通过 | computing_math=0 |
| fv-04c | 08 official_count vs 05 | 通过 | 08_domains=13 equal=True |
| fv-05 | 00_project_brief.md | 通过 | banned_hits=[] |
| fv-05 | 02_repo_inventory.md | 通过 | banned_hits=[] |
| fv-05 | 03_repo_structure_comparison.md | 通过 | banned_hits=[] |
| fv-05 | 06_runtime_provider_matrix.md | 通过 | banned_hits=[] |
| fv-05 | 07_old_new_format_comparison.md | 通过 | banned_hits=[] |
| fv-05 | 09_unknowns_and_decisions.md | 通过 | banned_hits=[] |
| fv-05 | 10_phase0_summary.md | 通过 | banned_hits=[] |
| fv-05 | PHASE0_FINAL_REPORT.md | 通过 | banned_hits=[] |
| fv-06 | 00_project_brief.md | 通过 | dangling=[] |
| fv-06 | 02_repo_inventory.md | 通过 | dangling=[] |
| fv-06 | 03_repo_structure_comparison.md | 通过 | dangling=[] |
| fv-06 | 06_runtime_provider_matrix.md | 通过 | dangling=[] |
| fv-06 | 07_old_new_format_comparison.md | 通过 | dangling=[] |
| fv-06 | 09_unknowns_and_decisions.md | 通过 | dangling=[] |
| fv-06 | 10_phase0_summary.md | 通过 | dangling=[] |
| fv-06 | PHASE0_FINAL_REPORT.md | 通过 | dangling=[] |
| fv-07 | FINAL_VALIDATION_REPORT.md status | 跳过 | validation report is regenerated after the freeze run; its closed status is checked in --verify-sums |
| fv-07 | 10_phase0_summary.md status | 通过 | missing=[] stale=no |
| fv-07 | 00_project_brief.md status | 通过 | missing=[] stale=no |
| fv-07 | PHASE0_FINAL_REPORT.md status | 通过 | missing=[] stale=no |
| fv-08 | PHASE0_FINAL_REPORT.md presence | 通过 | missing=[] |
| fv-13a | manifest final_files vs disk | 通过 | bad=[] |
| fv-13b | source lineage vs archive | 通过 | bad=[] |
| fv-14 | external archive records | 通过 | sums_entries=254 tsv_file_rows=254 verify_c=ok |
| fv-14b | archive index resolves manifest sources | 通过 | mapping ok |
| fv-15 | history dirs moved out of analysis | 通过 | still_present=[] |
| fv-16 | progress.log closeout entry | 通过 | entry=ok |
| fv-11 | repo 01_agents-last-exam HEAD | 通过 | head=2e91edd3cd26 rc=0 |
| fv-11 | repo 02_ale HEAD | 通过 | head=73517c2eb097 rc=0 |
| fv-11 | repo 04_ale-tasks-base HEAD | 通过 | head=492249a2ca4b rc=0 |
| fv-10a | FILE_SHA256SUMS.txt | 通过 | byte_newlines=108117 |
| fv-10b | README_READ_ONLY.md perms | 通过 | mode=0o400 |

## 3 冻结产物与继承

- 冻结阶段 final。哈希前书挡 2026-11-09T22:45:23+08:00,哈希后书挡 2026-11-10T10:53:43+08:00。
- Closeout amendment。前次后书挡 2026-11-09T22:45:23+08:00,再封存时点 2026-11-10T10:53:43+08:00,原由 closeout amendment: history archived and moved out of analysis, lifecycle closed, source lineage switched to the external archive。
- 最终正式文件 12 份,证据文件 47 份,脚本 4 份。

| 最终文件 | SHA256 前 16 位 | 方式 | 继承来源 |
| --- | --- | --- | --- |
| 00_project_brief.md | e04740cead4ac14a | reworded | ../../../Archives/ALE-Phase0-History-20261110/analysis/phase0-official-baseline-r1/00_project_brief.md |
| 02_repo_inventory.md | 78f2356bc8654ba2 | reworded | ../../../Archives/ALE-Phase0-History-20261110/analysis/phase0-official-baseline-r1/02_repo_inventory.md |
| 03_repo_structure_comparison.md | 0117d5e7c90191df | reworded | ../../../Archives/ALE-Phase0-History-20261110/analysis/phase0-official-baseline-r2/03_repo_structure_comparison.md |
| 04_task_inventory.csv | b96a14c1bc4e08c3 | copied | ../../../Archives/ALE-Phase0-History-20261110/analysis/phase0-official-baseline-r2/04_task_inventory.csv |
| 05_task_category_summary.csv | f2bc36a1b8683119 | copied | ../../../Archives/ALE-Phase0-History-20261110/analysis/phase0-official-baseline-r2/05_task_category_summary.csv |
| 06_runtime_provider_matrix.md | 923317c2bb51650f | reworded | ../../../Archives/ALE-Phase0-History-20261110/analysis/phase0-official-baseline-r2/06_runtime_provider_matrix.md |
| 07_old_new_format_comparison.md | 84aa458f14078c3a | reworded | ../../../Archives/ALE-Phase0-History-20261110/analysis/phase0-official-baseline-r1/07_old_new_format_comparison.md |
| 08_coverage_matrix_draft.csv | 17321d7662672695 | copied | ../../../Archives/ALE-Phase0-History-20261110/analysis/phase0-official-baseline-r2/08_coverage_matrix_draft.csv |
| 09_unknowns_and_decisions.md | 874e213990f97952 | reworded | ../../../Archives/ALE-Phase0-History-20261110/analysis/phase0-official-baseline-r2/09_unknowns_and_decisions.md |
| 10_phase0_summary.md | ecbfa574613ff42d | reworded | ../../../Archives/ALE-Phase0-History-20261110/analysis/phase0-official-baseline-r2/10_phase0_summary.md |
| FINAL_VALIDATION_REPORT.md | 2f5d89bbfcb58223 | new | 本轮新写 |
| PHASE0_FINAL_REPORT.md | 902fc4f91e56e00d | new | 本轮新写 |

## 4 未声明通过的项目

- 全部 122 条官方任务 run_state_current 是 NOT_RUN。本轮没有运行任何官方任务,因此没有任何运行结论。
- Windows 首期与 GPU 预算保持 OPEN,正式配额与排产未裁决。这些是负责人决策项,不是执行验证项。
- 9 条 GUI unknown 任务的工程与审核风险保持 UNKNOWN,等待人工复核。遗留 UNKNOWN 清单见 PHASE0_FINAL_REPORT.md 第 8 节。

## 5 结论

验证通过。Phase 0 已完成并验收通过。历史目录已归档并完成清理。analysis/phase0-final/ 是当前唯一有效基线。

Phase 0 CLOSED。Phase 0 最终基线已验收,历史版本已归档,后续不再修改 Phase 0 内容。

状态:Phase 0 CLOSED,phase0-final 为唯一有效基线。本轮仅完成状态收尾与清理后来源校验调整,未进入 Phase 0.5/P1。
