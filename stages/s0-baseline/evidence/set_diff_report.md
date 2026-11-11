# set_diff_report, task set reconciliation

本报告按 R1 任务书第 9 条重新核对任务集合，[cmd] 标签对应的统计均由 R1/scripts/24_build_set_diff.py 从冻结输入重算。

## (a) full.txt 发布集合

路径 01_agents-last-exam/selected_tasks/full.txt，共 124 行，其中 2 行注释头，任务 122 条。表中每域数量如下。

| domain | count |
| --- | ---: |
| business_finance | 19 |
| computing_math | 19 |
| education_info | 2 |
| engineering | 16 |
| health_medicine | 19 |
| legal | 2 |
| life_sciences | 12 |
| other | 2 |
| physical_sciences | 14 |
| psychology_neuro | 3 |
| social_sciences | 1 |
| transport_safety | 2 |
| visual_media | 11 |
| TOTAL | 122 |

## (b) 01 仓库物理 task_card.json 统计

review 引用 135，[cmd] 重算为 135 张物理 task_card.json，比 122 多 13 张。多出的 13 张不属于任何 selected_tasks 列表，也不在 v1.1 的 30 条退役名单里。

| extra task id | card schema note |
| --- | --- |
| demo/apply_patch_win | keys category,summary,taskId,title,vm; status no status field |
| demo/hello | keys category,summary,taskId,title,vm; status no status field |
| demo/hello_win | keys category,summary,taskId,title,vm; status no status field |
| demo/readfile_secret | keys category,summary,taskId,title,vm; status no status field |
| demo/seecheck | keys category,summary,taskId,title,vm; status no status field |
| demo/seecheck_win | keys category,summary,taskId,title,vm; status no status field |
| demo/tool_smoke | keys agentMustDo,category,evaluation,summary,taskId,title,vm; status no status field |
| demo/tool_smoke_win | keys agentMustDo,category,evaluation,summary,taskId,title,vm; status no status field |
| engineering/2d_drawings_to_3d_bridge_model | keys agentMustDo,category,evaluation,inputFiles,referenceFiles,requiredSystemPackages,software,summary,taskId,taskPrompt,taxonomy,title,vm; status no status field |
| visual_media/high_to_low_modeling | keys agentMustDo,category,evaluation,evaluatorCredentials,inputFiles,referenceFiles,requiredSystemPackages,software,summary,taskId,taskPrompt,taxonomy,title,vm; status no status field |
| visual_media/mota_reproduction | keys agentMustDo,category,evaluation,evaluatorCredentials,inputFiles,referenceFiles,requiredCredentials,software,summary,taskId,taskPrompt,taxonomy,title,vm; status no status field |
| visual_media/object_generation | keys agentMustDo,category,evaluation,inputFiles,referenceFiles,requiredSystemPackages,software,summary,taskId,taskPrompt,taxonomy,title,vm; status no status field |
| visual_media/scene_restoration | keys agentMustDo,category,evaluation,inputFiles,outputContracts,referenceFiles,software,summary,taskId,taskPrompt,taxonomy,title,vm; status no status field |

extra 分布。demo 8 张，visual_media 4 张，engineering 1 张。

## (c) 03 data tree 任务目录

03_ale-data/task-data-v1.1 下每个任务的目录数与 full.txt 完全一致，共 122 个。

| domain | dirs |
| --- | ---: |
| business_finance | 19 |
| computing_math | 19 |
| education_info | 2 |
| engineering | 16 |
| health_medicine | 19 |
| legal | 2 |
| life_sciences | 12 |
| other | 2 |
| physical_sciences | 14 |
| psychology_neuro | 3 |
| social_sciences | 1 |
| transport_safety | 2 |
| visual_media | 11 |
| TOTAL | 122 |

## (d) 集合差异

差异组 1。01 仓库有卡但不在 full.txt，共 13 张，全部列出。

- demo/apply_patch_win
- demo/hello
- demo/hello_win
- demo/readfile_secret
- demo/seecheck
- demo/seecheck_win
- demo/tool_smoke
- demo/tool_smoke_win
- engineering/2d_drawings_to_3d_bridge_model
- visual_media/high_to_low_modeling
- visual_media/mota_reproduction
- visual_media/object_generation
- visual_media/scene_restoration

差异组 2。full.txt 有 id 但 01 仓库没有卡，0 条。

差异组 3。full.txt 有 id 但 03 data tree 没有目录，0 条。

## (e) 135 与 122 的来源解释

官方 v1.1.md 第 3 行，[doc: docs/releases/v1.1.md:3]。

> ALE v1.1 selects **122 active tasks** after 30 retirements.

官方 v1.1.md 第 77 行至 80 行，[doc: docs/releases/v1.1.md:77-80]。

> education_info/homework_grading_numerical_pdes_instance_02 is retired because feedback verification was overly tied to fixed wording. A further 28 tasks are retired from v1.1; the task review lists all 30. Retirement is a release-scope decision, not a claim that every retired task is defective.

30 条退役名单在 v1.1-task-review.md 的 Retired tasks 一节，[doc: docs/releases/v1.1-task-review.md:69]。该节正文说明退役是发布范围决定。

> All 30 tasks below are outside the v1.1 source and selection lists.

名单如下。

- agriculture_env/crop_rotation_d02
- agriculture_env/ndvi_zonal_statistics_d02
- business_finance/financial_stmt_reconstruction_aapl_fy2024
- business_finance/pe_screening_memo_1
- computing_math/branch_bound_atsp
- computing_math/ising_post_measurement_1
- computing_math/k3_abelian_extensions
- computing_math/os_log_permission_guard_v1
- education_info/homework_grading_numerical_pdes_instance_02
- education_info/moodle_gradebook_closeout_reconciliation
- engineering/abb_irb6700_asset_to_urdf_instance_1
- engineering/mold-flow
- engineering/sanding_performance_scoring_instance_1
- health_medicine/Clinical_Variant_Annotation
- health_medicine/crf_sdtm_mapping_4
- health_medicine/epidemiology_forecast
- health_medicine/healthcare_bias_audit_27a_public_replication_v1
- health_medicine/healthcare_variant_annotation_pipeline
- health_medicine/replicate_paper_1
- health_medicine/scene3_skullstrip_qc
- life_sciences/amber_minimization_script_prep_instance_1
- life_sciences/gene_expression_differential_analysis_functional_enrichment_analysis_1
- life_sciences/genomic_interval_processing_1
- life_sciences/hg002_chr22_germline_variant_pipeline
- life_sciences/protein_function_annotation_instance_1
- life_sciences/pseudotime_de
- life_sciences/rgi_mcr1_colistin_v2
- physical_sciences/adapt_vqe_molecular_energy
- transport_safety/capacitated_vehicle_routing_problems
- visual_media/inkscape_cultural_poster_design

因此 135 减 122 的 13 张不属于退役口径。这 13 张卡是仓库历史遗留的未发布或 demo 任务，未进入任何 selected_tasks 列表。round-1 文件引用的 135 是物理卡的总数，不是发布任务数。

## (f) 历史数字 153

在全部 inputs 中未找到把 153 作为任务数量使用的记录。153 只以字符串子串形式出现于哈希值、URL、上传时间戳与 1536 像素值中，没有一处指代任务总数。152 也同样未作为任务数出现。

## (g) 难度名单 reconciliation

列表文件都在 01_agents-last-exam/selected_tasks/full/ 下，无版本标记字段。版本锚点是 releases/v1.1/assets.json 的 published_date 2026-10-14 与每份名单的 sha256。

| list file | count |
| --- | ---: |
| near-term.txt | 45 |
| full-spectrum.txt | 46 |
| last-exam.txt | 36 |

两两交集与并集，[cmd]。

| pair | intersection |
| --- | ---: |
| near-term and full-spectrum | 0 |
| near-term and last-exam | 0 |
| full-spectrum and last-exam | 5 |
| union size | 122 |

并集等于 full.txt 的 122 条，每个发布任务至少进入一个难度层。同属 full-spectrum 与 last-exam 两层的任务共 5 条。

- business_finance/legal_ma_consistency_audit_01
- computing_math/cfr_game_theory_equilibrium
- education_info/yi_manuscript_translation_1
- engineering/aerospace_low_thrust_trajectory
- visual_media/skeletal_animation_reproduction

## (h) computing_math 与 CS 口径

官方输入没有对 computing_math 类别的文字描述。卡的 category 字段值为 computing_math，例如 cfr_game_theory_equilibrium 的 taxonomy subdomain 是 math_ops_research（Mathematical & Operations Research）。把该域等同于 CS 口径是本项目的过滤决定，不是官方分类。[unknown: 官方无该类别描述]

round-1 的 05 文件把 computing_math 标为 cs_domain=yes 且 retained_for_500=no。R1 保留这两个值，但这是当前统计过滤器，只影响 500 口径统计，不代表官方宣布该域属于 computer science。
