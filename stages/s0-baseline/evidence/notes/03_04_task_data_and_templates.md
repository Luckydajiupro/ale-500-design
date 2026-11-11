# ALE task data dump and task template repo, inputs 03 and 04

Read-only audit of the two frozen inputs, done for the ALE 500-task program phase 0.
This note answers the eight questions in the investigation brief, in order.

Input roots, relative to this note.

1. `03_ale-data/` means the task data dump root.
2. `04_ale-tasks-base/` means the new task template repo root.

External sources cited below are untrusted web content, fetched on 2026-11-08.
They pin the official list and release notes to the exact source revision named by the archive.

- Task list. `selected_tasks/full.txt` at rdi-berkeley/agents-last-exam, revision 5e077cc254535f479e425ad3aaa4621dce62fc00.
- Release notes. `docs/releases/v1.1.md` at the same revision.
- Engine task-authoring spec. `docs/specs/task-authoring.md` on AgentsLastExam/ale, branch main.
- Engine task-assets spec. `docs/specs/task-assets.md` on AgentsLastExam/ale, branch main.

Evidence tags used per claim. `doc` means a file in the inputs or a cited official doc says so.
`data` means I computed it from the input files. `code` means I read executable source.
`inference` is my reading of evidence. `unknown` is not established anywhere I checked.

## 1. ale-data structure

`03_ale-data/` has two top-level items (data).

1. `03_ale-data/archive/`
2. `03_ale-data/task-data-v1.1/`

### 1.1 archive

`03_ale-data/archive/` holds five items (data).

1. `archive/README.md`. Dataset doc for ALE v1.1 task data. 122 active tasks. License cc-by-4.0. Gated access with an approval form (doc).
2. `archive/ale-tasks-data.tar.gz`. 39,155,440,558 bytes, about 36.5 GiB. SHA256 a7fd6eafbffcebf393580c45ce7afa4908dcd1e2ceaabcebbc867e28c7cea0a2 (data).
3. `archive/selected-members.jsonl`. 79,494 lines, one per tar member. Fields per line. Bytes, mode, path, sha256, type (data).
4. `archive/release-v1.1.json`. Version 1.1. 79,494 logical members. 122 selected tasks. Source revision 5e077cc254535f479e425ad3aaa4621dce62fc00. Data manifest SHA256 def33fda086c5f1ce0064c54294af4aac92a619aeefdbed863bf230b01aa0c63 (data).
5. `archive/.gitattributes`. LFS tracking for *.zst, *.tar.zst, tar.gz, and selected-members.jsonl (data).

The archive README states the archive preserves native filenames, file modes, and symlinks (doc).
The upstream home of this archive is the Hugging Face dataset agents-last-exam/agents-last-exam-data-archive (doc, release notes).

### 1.2 task-data-v1.1

`03_ale-data/task-data-v1.1/` is the extracted archive payload. It is not a git repo (data).
It holds exactly 13 domain directories and nothing else at top level. Background tar scan confirmed all 79,494 members live under the 13 domain dirs (data).

Extraction state (data).

- 79,065 files plus 4 symlinks plus 4,024 directories.
- 79,494 tar members. 79,069 non-directory entries and 425 explicit directory entries.
- The non-directory count equals extracted files plus symlinks. Extraction parity holds.

File modes from selected-members.jsonl (data).

- 69,198 members are mode 0600.
- 7,747 members are mode 0644.
- 2,073 members are mode 0664.
- 452 members are mode 0755, the only executables in the archive.

The 13 domain dirs, file counts, and sizes with du (data).

| Path under task-data-v1.1 | Files | Size |
| --- | ---: | ---: |
| business_finance | 571 | 1.7 GiB |
| computing_math | 1,484 | 1.4 GiB |
| education_info | 67 | under 1 MiB |
| engineering | 3,922 | 1.4 GiB |
| health_medicine | 9,056 | 16.8 GiB |
| legal | 31 | 2 MiB |
| life_sciences | 50,022 | 14.7 GiB |
| other | 273 | 196 MiB |
| physical_sciences | 12,772 | 1.5 GiB |
| psychology_neuro | 96 | 9.6 GiB |
| social_sciences | 25 | 451 MiB |
| transport_safety | 76 | 171 MiB |
| visual_media | 670 | 2.0 GiB |

Extracted total is about 50 GiB. The tar is 36.5 GiB. The snapshot is about 86.9 GiB total (data).

## 2. Task data format

The layout inside every domain dir is fixed (data, inference).

- `task-data-v1.1/<domain>/<task>/<variant>/` is the task instance root.
- `<variant>` is `base` for 100 tasks and a named dir for 22 tasks.
- Each variant dir holds `input/`, `software/`, and `reference/` with the presence stat below.

Presence stats across all 122 variant dirs (data).

- `input/` exists in 122 of 122.
- `software/` exists in 106 of 122.
- `reference/` exists in 120 of 122.

The 16 tasks without a software dir (data). ar_full_1500, cp_test_gen_1,
2d_drawings_to_3d_building_model, humanoid_wbc_policy_evaluation,
healthcare_sap_group_sequential_nsclc, ltmle_targeted_bootstrap_simulation_study,
nsclc_radiomics_cox_signature_v1, wsi_tumor_localization_1, WGS_Variant_Calling,
idp_ensemble_scoring, zdock_hiv_dimer_interface_scoring_v1, exact_diag_heisenberg_j1j2,
gillespie_gene_regulatory_network, qm9_mmff94_forcefield_survey_1, music_transcription,
uv_reproduction.

The 2 tasks without a reference dir (data). cailian_road_highway_alignment_2 and
inner_support_elevation_optimization. Both are engineering tasks the release notes mark
as needing a Linux VM (doc).

### 2.1 Metadata manifests per task

There is no metadata manifest at the task layer. Zero JSON files sit between domain and variant (data).
The only manifests live inside `reference/`, written for the evaluator (data).

- reference_manifest.json in 3 tasks.
- stage1_manifest.json in 23 tasks.
- source_manifest.json in 17 tasks.
- evaluator_data_manifest.json in 1 task.
- metadata.json in 3 tasks.

Shapes (data).

- reference_manifest.json. Holds task_id, variant, agent_visible_inputs, reference_files, required_agent_outputs.
- stage1_manifest.json. Holds task_id for the fine task taxonomy, a gs://agenthle bucket URL, remote root, target VM, built_at.
- evaluator_data_manifest.json. Holds schema_version, task_id, visibility set to evaluator_only, samples, and per-file bytes plus SHA256.

Task description files sit in `input/` and their names vary (data).

- task_prompt.md in 14 tasks, output_contract.json in 14.
- task_brief.md in 11, problem_spec.md in 7, task_instructions.md in 6.
- TASK_PROMPT.md in 6, README.md in 6, task_description.txt in 5.
- output_schema.json in 5, manifest.json in 4, task_spec.md in 3, output_requirements.txt in 3.

`input/runtime_env/` exists in 41 tasks. It holds 40 pyproject.toml files and 34 uv.lock files (data).

### 2.2 Directory naming meaning

Naming is `<domain>/<task>/<variant>` (data, inference).
The domain is the top-level subject area. The task is a slug. The variant selects which
task instance the graders read. The archive readme says the archive holds the 122 active tasks (doc).
The 22 named variants (data, in task → variant form).

- equity_research_summary → tsla_fy2023
- odoo → odoo_compact
- taxform_4_1 → variant_1
- cp_test_gen_1 → default
- Analog_Active → Analog_Active_v1
- gcode → 125162_319
- ct_geometry_calibration_catphan → instance_1
- ecg_rhythm_conduction_ptbxl → ptbxl_2263
- ecg_superclass_ptbxl → ptbxl_1386
- wsi_tumor_localization_1 → center_point
- idp_ensemble_scoring → default
- aerobics_wc2026_portugal_trio_difficulty_scoring → variant_1
- mota_exploration → mota_24_ez
- egt710_table1_smiles_extraction → table1
- ketcher_smiles_reproduction → 7yy
- lenacapavir_sar_table2_extraction → table2
- celegans_neuron_tracking → 137
- chroma_key_from_reference → crane_flyingsky
- music_transcription → dorico_prelude
- project_migration → celeste_symphonic_suite
- skeletal_animation_reproduction → skeletal_animation_reproduction_singing_anime_character
- uv_reproduction → uv_reproduction_anime_singing_girl

### 2.3 Two example task instances

Example 1. `task-data-v1.1/business_finance/american_option_pricing_ls/base/` (data).

- input/problem_spec.md is a tiered pricing spec. Tier 1 is the Black-Scholes closed form. Tier 2 is an American put by Longstaff-Schwartz Monte Carlo. Tier 3 adds a basket option and Greeks.
- software/README.txt declares python.sh as the canonical solver entry point.
- input/runtime_env/pyproject.toml pins numpy==1.26.4 and scipy==1.12.0, requires python from 3.10 to below 3.13, and disables packaging with package=false.
- reference/reference_manifest.json has task_id finance/american_option_pricing_ls, variant base, empty agent_visible_inputs, and reference files results.json, exercise_boundary_tier2.npy, option_solver.py. Required agent outputs are the two result files.

Example 2. `task-data-v1.1/life_sciences/WGS_Variant_Calling/base/` (data).

- No software dir. The task ships only input data and the evaluator.
- reference/evaluator_data_manifest.json stores the task schema version, task_id life_sciences/WGS_Variant_Calling, visibility evaluator_only, samples, and file digests.
- The evaluator-only sample is the hidden answer, kept out of agent-visible inputs.

Example 3. `task-data-v1.1/computing_math/tris_crackme/base/` (data).

- reference/stage1_manifest.json has task_id cybersecurity/tris_crackme and a Windows remote target.
- A Windows target VM is named in the manifest, with build time and a gs://agenthle bucket path.

A task-scoped data file can look like a manifest but is not one. input/task.json in
`task-data-v1.1/social_sciences/atwood_2022_measles_vaccine_reproduction/base/` is a scoring
config with target table, scored columns, matching rule, verdict thresholds, and required
output files (data).

## 3. Task counts

I counted task dirs at depth 2 under each domain with find (data).
The count matches the official list, selected_tasks/full.txt at the source revision (doc).
It also matches the release manifest value selected_tasks=122 (data).

Per-domain task counts, disk and official list agree (data).

| Domain | Tasks |
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

Total is 122 active tasks. Every task dir holds exactly one variant dir. 100 are base and 22 are named (data).

The official full list, grouped by domain. Paths are relative to task-data-v1.1 (doc, verified with find data).

- business_finance. american_option_pricing_ls, ar_full_1500, ar_full_300, basel_operational_risk_bia_cn, bpmn_category_governance_restructuring_l3, bpmn_supply_disruption_l3, digital_marketing_ab_test_analysis_1, digital_marketing_audience_segmentation_1, equity_research_summary, ff5_public_reconstruction, internal_employee_agent_instance_1, legal_ma_consistency_audit_01, llm_ecosystem_privacy_audit_realdata_1, metabase_bi_dashboard_01, odoo, saas_onepager_brand_refresh_instance_1, sec_10k_financial_parsing, sse_northbound_programmatic_trading_01, taxform_4_1.
- computing_math. cfr_game_theory_equilibrium, clustered_cyclic_code_circuit_level_simulation, cost_optimization_1, cp_test_gen_1, data_pipeline_etl_instance_1, dit_pipeline_cfg_alignment_fid_256_001, ghidra_malware_config_extraction_01, go_game_reconstruction_1, k8s_migration_1, k8s_payment_api_root_cause_analysis, mp_checkpoint_consolidation_v2, newyear_keygen2, paper_reproduction_instance_1, particle_filter_nonlinear_tracking, pcap_enterprise_triage_01, ranking_node_feature_parity_recovery_instance_1, recsys_cold_start_instance_1, synthetic_causal_structure_inference, tris_crackme.
- education_info. marc_remediation_folio_overlay, yi_manuscript_translation_1.
- engineering. 2d_drawings_to_3d_building_model, Analog_Active, aerospace_low_thrust_trajectory, cailian_road_highway_alignment_2, chisel_verilog_alignment_seq_1, gcode, humanoid_velocity_tracking_policy, humanoid_wbc_policy_evaluation, inner_support_elevation_optimization, kicad_navswitch_library_integration_release_002, mpc_control_building_v1, openroad_sky130_ibex_pnr_signoff, pcb_layout_kicad_1, power_10kv_feeder_reliability_001, robotics_blender_tabletop_reconstruction, sumo_urban_am_peak_calibration.
- health_medicine. causal_ihdp_ite_estimation_6a_v1, crf_sdtm_mapping_1, ct_geometry_calibration_catphan, ecg_rhythm_conduction_ptbxl, ecg_superclass_ptbxl, flusight_offline_hosp_forecast_2024_12_14, healthcare_sap_group_sequential_nsclc, healthcare_tcga_luad_survival_kras, limited_angle_ct_dps_reconstruction, ltmle_targeted_bootstrap_simulation_study, microdicom_nih_cxr_reader_adjudication, nhanes_confounder_sensitivity_analysis, nsclc_radiomics_cox_signature_v1, obermeyer_bias_reproduction, prostate_imrt_matrad_reproduction, public_health_mask_mandate_ratio, sa_aki_phenotyping, simglucose_safe_basal_control_instance_1, wsi_tumor_localization_1.
- legal. agora_governance_classify_instance_1, legal_dr_fees_01.
- life_sciences. WGS_Variant_Calling, amber_three_stage_mmgbsa_workflow_instance_1, cell_tracking_instance_1, cell_translocation_analysis, idp_ensemble_scoring, merfish_image_decoding_segmentation_1, spatial_transcriptomics_spatial_domain_identification, tcga_brca_deg_analysis, tms_marrow_cell_type_annotation_instance_1, tp53_locus_variant_histone_browser_svg, yeast_colony_detection, zdock_hiv_dimer_interface_scoring_v1.
- other. aerobics_wc2026_portugal_trio_difficulty_scoring, mota_exploration.
- physical_sciences. climate_prediction, computational_materials_science, egt710_table1_smiles_extraction, exact_diag_heisenberg_j1j2, gillespie_gene_regulatory_network, glm_lake_calibration, hst_acs_wfc_visit_reduction, ketcher_smiles_reproduction, lenacapavir_sar_table2_extraction, molecular_structure_plausibility, mose2_bse_absorption_soc, phonon_dispersion_thermodynamics, qm9_mmff94_forcefield_survey_1, silicon_bse_absorption.
- psychology_neuro. celegans_neuron_tracking, reddit_ai_post_codebook_boolean_coding, scene2_resample.
- social_sciences. atwood_2022_measles_vaccine_reproduction.
- transport_safety. abm_hangzhou_metro, fds_single_compartment_detector_reconstruction.
- visual_media. atlas_outpost_graybox_navigation, blender_character_reconstruction_from_multiview_01, butterfly_flap_animation, chroma_key_from_reference, compress_3dgs_scene_ply, human_mesh_animation_reproduction, music_transcription, project_migration, skeletal_animation_reproduction, uv_reproduction, video_storyboard_001.

## 4. Category landscape

The official taxonomy is the 13 domain dirs. No other category field exists in the data (data, inference).
The same 13 names appear in the official list file (doc).

Domain notes and file counts from the table above (data).

- business_finance. Finance and accounting work. 19 tasks, 571 files.
- computing_math. Computation and quantitative work. 19 tasks, 1,484 files.
- education_info. 2 tasks, 67 files.
- engineering. Design and fabrication tools. 16 tasks, 3,922 files.
- health_medicine. Clinical and public health analysis. 19 tasks, 9,056 files.
- legal. 2 tasks, 31 files.
- life_sciences. Proteins, genomics, imaging. 12 tasks, 50,022 files. The pdb family dominates the file count.
- other. 2 tasks, 273 files.
- physical_sciences. 14 tasks, 12,772 files.
- psychology_neuro. 3 tasks, 96 files. Mostly huge single files.
- social_sciences. 1 task, 25 files.
- transport_safety. 2 tasks, 76 files.
- visual_media. Animation, VFX, 3D and audio production. 11 tasks, 670 files.

Size by domain is in the section 1.2 table (data).

The 23 stage1_manifest.json files carry a finer task_id taxonomy. Examples extracted from them (data).

- cybersecurity. tris_crackme, newyear_keygen2.
- cloud_computing. cost_optimization_1, k8s_payment_api_root_cause_analysis.
- machine_learning. ranking_node_feature_parity_recovery_instance_1, particle_filter_nonlinear_tracking, dit_pipeline_cfg_alignment_fid_256_001.
- finance. american_option_pricing_ls, sec_10k_financial_parsing, equity_research_summary.
- supply_chain. odoo, plus two bpmn tasks.
- precision_health. Four ECG tasks, flusight, and NHS-related tasks.
- robotics. humanoid_velocity_tracking_policy.
- media. butterfly_flap_animation.
- game. human_mesh_animation_reproduction, blender_character_reconstruction_from_multiview_01.
- hardware. Analog_Active.
- materials_science. phonon_dispersion_thermodynamics.
- chemistry. molecular_structure_plausibility.
- earth_science. climate_prediction, glm_lake_calibration.
- physics. exact_diag_heisenberg_j1j2.
- biomedical_imaging. cell_tracking_instance_1, limited_angle_ct_dps_reconstruction.
- clinical_data_standards. crf_sdtm_mapping_1.
- aerospace_engineering. aerospace_low_thrust_trajectory.
- transportation_engineering. abm_hangzhou_metro, sumo_urban_am_peak_calibration.
- legal_compliance. agora_governance_classify_instance_1, legal_ma_consistency_audit_01.
- library_information_science. marc_remediation_folio_overlay.
- humanities. yi_manuscript_translation_1.
- communication. saas_onepager_brand_refresh_instance_1.
- marketing. digital_marketing_ab_test_analysis_1.
- fire_protection_engineering. fds_single_compartment_detector_reconstruction.

Tasks that look like CS. There is no official CS tag anywhere. The closest domains are below (inference).

- computing_math, all 19 tasks. Crackmes, malware config extraction, pcap triage, k8s roots, ML pipelines, ETL, recommender and ranking recovery, causal inference, game theory solver, code simulation, paper reproduction.
- engineering, the EDA and robotics slice. chisel_verilog_alignment_seq_1, openroad_sky130_ibex_pnr_signoff, kicad_navswitch_library_integration_release_002, pcb_layout_kicad_1, gcode, humanoid_velocity_tracking_policy, humanoid_wbc_policy_evaluation.
- visual_media, the computer graphics slice. compress_3dgs_scene_ply, blender_character_reconstruction_from_multiview_01, skeletal_animation_reproduction, uv_reproduction.
- computing-flavored finance tasks. k8s_migration_1 sits in computing_math. Business finance has no k8s tasks.

## 5. Asset signatures

Extension histogram, top entries across the archive (data).

- .pdb 37,973 files. Protein structures, almost all in life_sciences.
- .py about 13,247. .dat 3,751. .hea 3,649. .csv about 3,249. .pyi 2,322.
- .gz 1,442. .tab 847. .txt 828. .0 764. .png 613. .so 533. .json 519. .xml 402.

Computed asset classes across the tree (data).

- csv_tsv 3,312 files. gz 1,438. raster_img 888. med_img 241. mat 236. audio 209.
- 3d_mesh 166. pdf 154. pickle_sav 138. npy_npz 138. win_exe 30. office 26.
- svg 23. model_ckpt 21. jar 18. elf_bin 12. ipynb 10. zip7rar 9. sql 7. video 7.
- tar 6. hdf5 3. fasta_fastq 3. tex 1. disk_img 1. parquet 1.

Files over 100 MB, top examples found with find (data).

- psychology_neuro/scene2_resample/base/software/computer_use_benchmark_bundle/containers/slicer_5.0.3_20221025.simg, 8.1 GiB.
- health_medicine/wsi_tumor_localization_1/center_point/input/tumor_001.tif, 3.0 GiB.
- psychology_neuro/celegans_neuron_tracking/137/input/137.h5, 1.5 GiB.
- health_medicine/prostate_imrt_matrad_reproduction/base/reference/replay_state.mat, 831 MB.
- life_sciences/idp_ensemble_scoring/default/input/CSpred/models, 16 .sav model files from 131 MB to 628 MB, about 7 GiB total, plus a stale .git pack of 312 MB.
- business_finance/metabase_bi_dashboard_01/base/software/metabase.jar, 487 MB.
- social_sciences/atwood_2022_measles_vaccine_reproduction/base/input/replication_package.zip, 412 MB.
- visual_media/compress_3dgs_scene_ply/base/input/scene/point_cloud_30000.ply, 300 MB.
- life_sciences/tp53_locus_variant_histone_browser_svg/base/input/wgEncodeBroadHistoneK562H3k27acStdSig.bigWig, 292 MB.
- health_medicine/limited_angle_ct_dps_reconstruction/base/input/ddpm_CT.pth, 243 MB.
- engineering/humanoid_wbc_policy_evaluation/base/input/runtime_env/mjlab.zip, 207 MB.
- physical_sciences/climate_prediction/base/reference/processed/train_inputs.npy, 202 MB.
- computing_math/mp_checkpoint_consolidation_v2/base/reference/expected_model.safetensors, 154 MB.
- computing_math/ranking_node_feature_parity_recovery_instance_1/base/input/workspace, four junk cache and trash bins from 104 MB to 180 MB.
- engineering/aerospace_low_thrust_trajectory/base/reference/tier3_trajectory.npy, 133 MB.
- other/aerobics_wc2026_portugal_trio_difficulty_scoring/variant_1/input/trio.mov, 155 MB.
- visual_media/project_migration/celeste_symphonic_suite/reference/stems/Piano.flac, 101 MB.

Windows-ized tasks found (data).

- computing_math/ghidra_malware_config_extraction_01 ships a launch_ghidra.bat launcher, Ghidra 11.3, and a Windows x64 Temurin JDK 21.
- computing_math/pcap_enterprise_triage_01 ships a launch_wireshark.bat launcher.
- physical_sciences/lenacapavir_sar_table2_extraction/table2/reference/evaluator_env/.venv is a Windows Python install with Scripts and DLLs.
- physical_sciences/egt710_table1_smiles_extraction/table1/reference/evaluator_env/.venv is the same shape.

## 6. ale-tasks-base

Identity and purpose (doc).

- Clone of https://github.com/AgentsLastExam/ale-tasks-base.git, branch main, HEAD 492249a2ca4b9d74efd3584a90399473c2e928c7.
- README calls it the reference collection of independent container and VM tasks in ALE task.toml format. Harbor layout plus ALE schema extensions. No shared task code across tasks.
- Contract files named by the README. Engine docs/specs/task-authoring.md and docs/specs/task-assets.md.

Folder layout for one task, as the README states it (doc).

- task.toml
- instruction.md
- environment/Dockerfile and environment/setup/setup.sh
- tests/test.sh and tests/verify.py, plus an optional tests/Dockerfile
- solution/solve.sh
- assets dirs beside the reading stage. environment/assets, tests/assets, solution/assets. Gitignored and synced to the Hugging Face dataset agents-last-exam/ale-tasks-base through uv run ale assets status, pull, or push.

Tree at depth 3 under tasks (data).

- tasks/demo with 10 entries. docker_in_vm, external_assets, resource_injection, tool_smoke, verification_agent_judge, verification_deterministic, verification_domain_a, verification_domain_b, verification_llm_judge, verification_separate.
- tasks/example_task with environment/Dockerfile, instruction.md, solution/solve.sh, task.toml, tests/test.sh and tests/verify.py.
- 11 task.toml files in total.

task.toml schema observed in the demos (code).

- schema_version is 1.4+ale.1.
- A top-level artifacts key lists agent output paths, for example /home/user/output.
- [task] holds name as org/task, for example agentslastexam/example-task, plus keywords.
- [environment] holds cpus, memory_mb such as 4096, storage_mb such as 8192, vm=true for the VM demo, and skills_dir=/skills.
- One demo declares [[environment.mcp_servers]] with name, transport=stdio, command, and args.
- [agent] holds user, timeout_sec, and network_mode=no-network.
- One demo has [verifier] with timeout_sec, environment_mode=separate, and its own [verifier.environment] cpus and memory_mb.

Dockerfiles (code).

- Container tasks build FROM ghcr.io/agentslastexam/container-ubuntu22-base:0.1.1.
- VM tasks build FROM ghcr.io/agentslastexam/vm-ubuntu24-base:0.1.0.
- The docker-in-vm demo pins a busybox base.

Verification kit (code).

- verify.py imports ale_verify and calls checks.json_value, checks.text_equals, and write with reward plus format.
- The judge API takes judge agent or llm, a name, prompt, an output_schema JSON schema, and files.
- EvidenceError import guards unusable evidence.
- tests/test.sh is a two-line bash script running set -euo pipefail then exec python3 verify.py.

Repo mechanics (code, doc).

- Justfile exposes new-task, lint, validate, check, and run.
- ALE commands run from a sibling ALE checkout with uv run ale new-task, prepare, validate, lint, or run.
- Credential-free validation covers seven tasks. example_task, resource_injection, tool_smoke, verification_deterministic, verification_domain_a, verification_domain_b, verification_separate.
- CI calls AgentsLastExam/ale/.github/workflows/task-check.yml@main.
- Git history shows the format refactors. 492249a drops the old [ale] docs table. 8df0666 moves tasks to schema 1.4+ale.1. a760e8c rewrites every task to the Harbor task.toml layout. Older commits add tool_smoke and the repository template.

The string @task-params appears nowhere in this repo. Grep over *.toml, *.md, *.py, and *.sh is empty (code).
The engine task-authoring spec defines the task.toml tables directly. It has no task-params decorator or
template-params format (doc). Where the program lead saw @task-params is unknown. Likely candidates
are Harbor docs or an ALE engine internal, neither of which lives in these two inputs (unknown).

## 7. Relation between the two inputs

There is no conversion or mapping script in ale-tasks-base. Grep found no reference to any
ale-data task slug and no ale-data file paths (code). The demo task names do not collide with
any real task slug (data).

The relation is by construction (inference).

- ale-data supplies every source task with task_id domain/slug.
- ale-tasks-base supplies the target shape. tasks/<path>/ plus task.toml with [task] name agentslastexam/<slug>.
- A converted task would live at tasks/<domain>/<task>/ in the new repo, with name agentslastexam/<task> in task.toml.
- The org prefix agentslastexam is the only family name or template id observed. No per-domain template families exist (data, inference).

The engine spec confirms the parts a conversion must produce (doc).

- task.toml, instruction.md, environment, tests, and solution stages.
- Windows tasks use build.ps1, test.ps1, and solve.ps1 instead of sh scripts.
- Large files belong in assets under environment/assets, tests/assets, or solution/assets and are never git-tracked.
- Offline software belongs under environment/assets/softwares/<software_id>.

The official upstream source confirms the same task list and adds runnability splits (doc).

- selected_tasks/full.txt lists all 122 tasks. It matches the 122 dirs one for one.
- selected_tasks/cpu.txt lists 119 and gpu.txt 3. Together they cover all 122.
- selected_tasks/docker_support.txt is the Linux container allowlist with 78 tasks.
- selected_tasks/ale_cli.txt lists 86 tasks for a Linux VM profile including desktop workflows.
- selected_tasks/full has difficulty lists. near-term.txt 45 tasks, full-spectrum.txt 46, last-exam.txt 36. They overlap.
- v1.1_modified.txt lists the 57 tasks changed since v1 and needing reruns. 65 remain eligible for retention.

The release notes name the exact tasks the upstream already converted to open-source Linux workflows (doc).

| Task | v1.1 workflow | Environment |
| --- | --- | --- |
| engineering/2d_drawings_to_3d_building_model | Blender building reconstruction | Docker or Linux VM |
| engineering/cailian_road_highway_alignment_2 | FreeCAD Road | Linux VM |
| engineering/gcode | FreeCAD CAM, LinuxCNC, CAMotics | Linux VM |
| engineering/inner_support_elevation_optimization | Kratos analysis | Linux VM |
| visual_media/music_transcription | MuseScore, PDF, MIDI | Docker or Linux VM |
| visual_media/project_migration | Ardour project, mix, stems | Docker or Linux VM |

## 8. CS exclusion evidence

No file in 03_ale-data marks any task CS or non-CS (data).
No category or discipline metadata field exists in any JSON. The only manifest taxonomy fields are
the stage1 task_id values listed above (data, inference).
selected-members.jsonl has no category field. It stores bytes, mode, path, sha256, type (data).

The official selection lists are resource or difficulty lists, not category lists (doc).
The benchmark talks of 55 target sub-industries on its website, but that map is not in the data dump (unknown).
The only usable category signal in the two inputs is the 13 domain dirs, plus the stage1 task_id
sub-taxonomy for 23 tasks (data).

Concrete CS-shaped slugs for the lead to exclude or keep (inference from task names, data paths).

- computing_math. tris_crackme, newyear_keygen2, ghidra_malware_config_extraction_01, pcap_enterprise_triage_01, k8s_migration_1, k8s_payment_api_root_cause_analysis, cost_optimization_1, data_pipeline_etl_instance_1, recsys_cold_start_instance_1, ranking_node_feature_parity_recovery_instance_1, dit_pipeline_cfg_alignment_fid_256_001, particle_filter_nonlinear_tracking, synthetic_causal_structure_inference, cfr_game_theory_equilibrium, clustered_cyclic_code_circuit_level_simulation, cp_test_gen_1, go_game_reconstruction_1, paper_reproduction_instance_1, mp_checkpoint_consolidation_v2.
- engineering EDA and tooling. chisel_verilog_alignment_seq_1, openroad_sky130_ibex_pnr_signoff, kicad_navswitch_library_integration_release_002, pcb_layout_kicad_1, gcode.
- visual_media graphics. compress_3dgs_scene_ply, uv_reproduction, skeletal_animation_reproduction, blender_character_reconstruction_from_multiview_01.

If the CS category the program means is a domain dir, only computing_math qualifies as fully CS (inference).
Engineering and visual_media mix CS tooling with domain work, so a domain-level cut excludes too much to the
exclusion side or too little to the keep side. A slug-list cut is more precise (inference).

Linux server fit is documented, not just inferred (doc, release notes).

- 78 tasks are allowlisted for the Linux Docker profile.
- Eight Linux tasks need runtime Docker exclusion warp help. openroad_sky130_ibex_pnr_signoff, k8s_migration_1, bpmn_supply_disruption_l3, and bpmn_category_governance_restructuring_l3 want nested Docker. scene2_resample wants a Singularity bundle. gcode wants process and network namespaces. cailian_road_highway_alignment_2 and inner_support_elevation_optimization want systemd and cgroups. Use a Linux VM for these, the notes say.
- 119 tasks run CPU-only in the official split. 3 use the published gpu-free snapshot. humanoid_velocity_tracking_policy, chroma_key_from_reference, compress_3dgs_scene_ply.

## 9. Open questions

1. Which CS category definition does the program use? The comments point to a category, not a domain. computing_math is the only fully CS domain. What is the exact slug or domain list to exclude?
2. The data dump delivers 122 tasks. The program needs 500. Where do the other 378 come from? The 28 retired v1.1 tasks, pending contributor tasks, or a new collection round?
3. The 23 stage1_manifest.json files carry the fine task_id taxonomy. Does the program want that classification recreated in task.toml keywords for the other 99 tasks?
4. The Windows tasks. ghidra_malware_config_extraction_01 and pcap_enterprise_triage_01 are Windows workflows. Do they convert to Windows build.ps1 tasks, or are they excluded on Linux servers?
5. Two Windows evaluator venvs ship under reference for lenacapavir and egt710. Who validates those on Linux, given the target is Linux servers?
6. The 16 tasks without a software dir. Which environment base image serves them in the new format?
7. The 41 runtime_env pyproject files. Do they become content of environment/setup scripts or image build steps?
8. The 22 named variant dirs. One named variant per task exists in the dump. Do they become the published instance or separate tasks?
9. Reference data hidden from agents, present in 120 of 122 tasks. Which of tests/assets, solution/assets, or environment/assets should hold each reference in the new format?
10. What does the lead's mention of @task-params map to? The string appears in neither input and not in the engine task-authoring spec.
11. The tar is 36.5 GiB with most files mode 0600. How should the pipeline extract it on servers without losing modes and symlinks?
12. ALE gating. The archive README says data access is gated and licensed cc-by-4.0. Is redistribution inside the program's servers covered by the team's approved access?
13. Difficulty lists near-term, full-spectrum, and last-exam overlap. Should the new format record them as task.toml keywords or drop them?