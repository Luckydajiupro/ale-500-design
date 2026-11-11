# r1_data_notes, R1 数据侧审核笔记

用途。本笔记供 CHANGELOG_R1.md 使用，记录命令清单、冲突与 UNKNOWN。
所有统计来自 R1/scripts 里的脚本，可以重跑。

## 脚本与命令清单

| script | output |
| --- | --- |
| scripts/01_census.py | evidence/census_raw.json，任务卡清单、名单成员、vm 快照、逻辑字节 |
| scripts/02_templates.py | 04_ale-tasks-base tasks 树 task.toml 扫描 |
| scripts/03_symlinks.py | evidence/symlink_resolution_raw.tsv |
| scripts/04_perms.py | evidence/perms_histogram.txt |
| scripts/05_keyword_context.py | evidence/keyword_context.txt，GUI 与 URL 判定原始凭据 |
| scripts/20_build_04_05.py | 04_task_inventory.csv 与 05_task_category_summary.csv |
| scripts/21_build_08.py | 08_coverage_matrix_draft.csv |
| scripts/22_build_evidence_tsvs.py | evidence/sizes_scopes.tsv 与 evidence/file_attribution.tsv |
| scripts/23_build_gpu_staged_templates.py | evidence/gpu_cross.tsv、evidence/staged_local_os.tsv、evidence/template_tasks.tsv |
| scripts/24_build_set_diff.py | evidence/set_diff_report.md |
| scripts/25_build_symlink_chmod.py | evidence/symlink_resolution_r1.tsv 与 evidence/chmod_wording_check.md |
| scripts/30_checker.py | evidence/checker_output.txt |

一次性命令。awk 直接对 FILE_SHA256SUMS.txt 求 engineering 域和，复核 1,527,073,733 B。grep 全 inputs 搜索 153 与 152。sed 读取 v1.1.md 引用行。

## 冲突清单，before 到 after

| id | round-1 或 review 的说法 | R1 实测 | 证据 |
| --- | --- | --- | --- |
| C1 | review 引用 135 张物理卡 | 135 正确，但发布集是 full.txt 的 122，135 是物理卡总数 | [cmd]; set_diff_report.md (b)(e) |
| C2 | 10_phase0_summary 71 Linux 32 Windows | 86 Linux 36 Windows | [cmd] vm.snapshot 普查; 04 与 05 |
| C3 | 08 写 physical GPU | gpu.txt 3 个任务全部 gpu-free Windows，发布集无 gpu-license 快照，physical GPU 0 | [cmd]; gpu_cross.tsv |
| C4 | ketcher external public-ref | online-required，唯一交付编辑器是托管 Ketcher 应用，离线无副本 | [code] Ketcher.url |
| C5 | equity 与 ar_full_1500、ar_full_300、ff5 external none | online-required，数据获取是任务的一部分 | [code] source_urls.txt; agent_prompt.md; file_list.txt |
| C6 | tp53 external none | public-ref，UCSC 启动器可选，VCF 与 BigWig 本地齐备 | [code] open_ucsc_browser.sh |
| C7 | egt710 yes-online | online-required，R1 词表换算 | [code] ChemInfo.url |
| C8 | 08 资产单位 MiB | business 1.69 GiB, engineering 1.42 GiB, health 16.76 GiB, physical 1.50 GiB, visual 2.03 GiB | [cmd] sizes_scopes.tsv |
| C9 | 08 把 3 GiB TIFF 与 1.5 GiB HDF5 算在 life_sciences | TIFF 属 health_medicine/wsi_tumor_localization_1，HDF5 属 psychology_neuro/celegans_neuron_tracking | [cmd] file_attribution.tsv |
| C10 | 08 social 资产极小 | 实测 469,325,814 B，447.6 MiB | [cmd] sizes_scopes.tsv |
| C11 | 02 大文件 replay 811 MiB, CA_R0 613 MiB, tms 592 MiB | 870,922,433 B, 658,672,244 B, 635,863,817 B | [cmd] FILE_SHA256SUMS.txt |
| C12 | parent CHANGELOG_R1.md engineering 1,527,077,333 B | 1,527,073,733 B，差 3,600 B，awk 复核两次 | [cmd] |
| C13 | 04 gui 6 yes 其余 unknown | 40 yes, 9 unknown, 73 no，按 GUI 判据重推 | [cmd] 04 普查 |
| C14 | round-1 04 两行 task_name 空 | 已填 humanoid_wbc_policy_evaluation 与 Obermeyer Bias Reproduction | [code] task_card.json |
| C15 | 00_project_brief 写 inputs-readonly 整体 chmod 555 | 目录 555，01/04 普通文件 444，03 数据与 README 400 | [cmd]; chmod_wording_check.md |
| C16 | 08 computing_math 19/0 draft 排除 | 保留，cs_domain=yes retained_for_500=no，过滤器仅统计语义 | [cmd] 05 |

一致项。review 的 demo=10 example_task=1 与 11 个 task.toml 总数被证实。
round-1 08 的 7/5/9 Windows 分域数被证实。staged-local 5 个任务 OS 拆分（2 BPMN Linux, 3 Windows）被证实。

## 兄弟文件说明

R1/evidence/ 与 R1/scripts/ 里另有引擎侧审计员写的文件（engine_format_evidence.md, historical_log_index.md, license_evidence.md, r1_engine_notes.md, runtime_claim_audit.md, scripts/validate_r1.py），本审计不触碰。
validate_r1.py 期望 04 不带注释行。本任务书要求 header-adjacent note，所以 04 第一行是 # 注 注释。检查器 30_checker.py 跳过注释行后全部通过。

## UNKNOWN 清单

| id | item |
| --- | --- |
| U1 | engineering/humanoid_wbc_policy_evaluation 的卡没有 vm.timeout，time_limit_sec 与 time_source 为 UNKNOWN |
| U2 | gui_status unknown 9 个任务，GUI 类软件在场但使用未被强制 |
| U3 | computing_math 官方类别描述在 inputs 中不存在，CS 归类无官方文字 |
| U4 | 153 作为任务数在 inputs 中未找到，152 也未找到 |
| U5 | hook-evaluator 类任务的计分入口函数名，main.py 的 @cb.evaluate_task 可见，内部实现函数名不总是静态可见 |
| U6 | 13 张额外卡无 status 字段，未发布或 demo 属性是推断 |
| U7 | atlas_outpost_graybox_navigation 提示词写 Windows GPU VM，卡快照是 cpu-free，官方未解释 |
| U8 | software 为空的 3 个任务（obermeyer, WGS_Variant_Calling, butterfly）software_versions 用 main.py 顶层 import 兜底 |

## checker 输出

```
PASS 04 column count uniform | header=31 data rows=122
PASS 04 unique task_id | unique=122
PASS 04 task set equals full.txt | n=122
PASS 04 windows census | win=36 lin=86
PASS 04 linux_runnable census | allowlist=78 doc_exception=8
PASS 05 domain counts and notes match 04 census | all match
PASS 04 gpu rows match gpu.txt | gpu list n=3
PASS staged-local OS split 2 bpmn linux / 3 windows | linux=['business_finance/bpmn_category_governance_restructuring_l3', 'business_finance/bpmn_supply_disruption_l3'] windows=['business_finance/metabase_bi_dashboard_01', 'business_finance/odoo', 'business_finance/taxform_4_1']
PASS windows totals agree 04/05/08 vs vm.snapshot census | 04=36 05=36
PASS 08 asset_profile sizes and counts match sizes_scopes.tsv | proposed sum=500
PASS sizes_scopes internal sums | tree=53327153701 dom_sum=53327153701 whole03=92500607918 arch+tree=92500607918 inputs=94086734364
SUMMARY 11/11 pass
```

checker 结论。11 项全部通过。
