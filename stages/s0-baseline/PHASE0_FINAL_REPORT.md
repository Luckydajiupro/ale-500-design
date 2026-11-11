# ALE 500 任务项目 Phase 0 最终基线报告

本报告整合 Phase 0 第一轮基线、R1 修订轮与 R2 定点修复轮。它是 Phase 0 的最终基线，后续设计以它为准，官方参考研究链与专家新任务生产链的表述全部按 R2 口径执行。[doc: 10_phase0_summary.md:100, evidence/history-r2/EXECUTION_BRIEF_R2_CHAT.md]

## 1 项目目标与阶段边界

- 交付目标。500 条最终任务全部由专家在平台新生产，官方任务不自动计入 500。[doc: 00_project_brief.md]
- 四道门。500 条依次通过内容审核、工程转换、运行验证、交付验收。[doc: 00_project_brief.md]
- 链路分离。官方参考研究链与专家新任务生产链分开。专家 Canonical Task Source 是独立新生产物，不是官方任务的复制或转换。[doc: 00_project_brief.md]
- 分工。平台负责采集、审核与冻结。工程负责 ALE 转换、运行验证、评测与交付。[doc: 00_project_brief.md]
- 已确认前提共 8 条。要点是腾讯云 Linux 不能嵌套虚拟化，沙箱 provider 与模型 provider 必须分开，Windows 与 GPU 的采用和预算待负责人确认。[doc: 00_project_brief.md]
- 第一轮。analysis/phase0-official-baseline/ 产出初版基线，由 R1 修订轮整体承接修订。[doc: evidence/history-r1/R1_VALIDATION_REPORT.md 范围与方法与变更文件清单节]
- R1 修订轮。修复 R01 到 R13 共 13 类问题，状态是 Phase 0 R1修订完成，待复审。[doc: evidence/history-r1/R1_VALIDATION_REPORT.md:119]
- R2 定点修复轮。关闭 A 到 G 七项缺陷，50 项检查 PASS 48、FAIL 0、ERROR 0、SKIP 2，退出码 0，8 个反例注入全部 TRIGGERED，状态是 Phase 0 R2定点修复完成，待验收。[cmd: evidence/history-r2/R2_VALIDATION_REPORT.md:13,48-61]
- 本轮地位。Phase 0 已完成并验收通过，历史目录已归档并完成清理，analysis/phase0-final/ 是当前唯一有效基线。[doc: 10_phase0_summary.md:100]
- 本轮边界。不裁决正式配额，不进入 P0.5 或 P1，不设计平台，不重新盘点官方数据。历史目录归档与清理由项目负责人批准并已完成。[doc: 10_phase0_summary.md:100, evidence/history-r2/EXECUTION_BRIEF_R2_CHAT.md]
- R2 修正口径全部继承。GUI unknown 风险通道、staged-local 逐条归属、任务名字节按 task_id 关联，本报告不再改回。[cmd: evidence/history-r2/R2_VALIDATION_REPORT.md:38-46]

## 2 四份官方输入与版本

- 冻结快照。四份输入冻结在 inputs-readonly/ 下，复制完成于 2026-11-08，时区 Asia/Taipei，工具 rsync -aH。[doc: inputs-readonly/README_READ_ONLY.md:7]
- 01 旧任务仓库 agents-last-exam。HEAD 2e91edd3cd26baa35a38127c90c8e5241dfbe62f，28,444 个文件。职责是提供旧任务形态、任务卡、名单分配与退役历史的官方源头。[doc: inputs-readonly/README_READ_ONLY.md:18,24]
- 01 在 main 上带标签 v1 与 runtime-qe-bgw-6.7.0-4.0。[doc: inputs-readonly/README_READ_ONLY.md:18]
- 02 新引擎 ale。HEAD 73517c2eb097abe7974e9ec4de9819a02cd0ee81，495 个文件。职责是执行新任务格式、沙箱与验证的合同引擎。[doc: inputs-readonly/README_READ_ONLY.md:18,24]
- 02 是 uv 工作区，三个包 ale-core、ale-run、ale-verify，版本都是 0.1.1。[doc: 02_repo_inventory.md, code: inputs-readonly/02_ale/packages/ale-core/pyproject.toml:1-4]
- 03 数据包 ale-data。无 git，79,070 个文件。职责是保存 122 个官方任务的输入、参考与评分数据。[doc: inputs-readonly/README_READ_ONLY.md:15,26]
- 03 逻辑字节总量 92,500,607,918，等于 86.15 GiB。其中 archive/ 是 39,173,454,217 字节，等于 36.48 GiB。task-data-v1.1/ 是 53,327,153,701 字节，等于 49.66 GiB。[cmd: evidence/sizes_scopes.tsv]
- 04 模板仓库 ale-tasks-base。HEAD 492249a2ca4b9d74efd3584a90399473c2e928c7，105 个文件。职责是提供新任务包的目录与 task.toml 样板。[doc: inputs-readonly/README_READ_ONLY.md:18,27]
- 04 的 tasks/ 下有 demo 10 个与 example_task 1 个，按 task.toml 计 11 个任务声明。[cmd: evidence/template_tasks.tsv]
- 冻结尺度一。四个快照子目录普通文件合计 108,114 个。[doc: inputs-readonly/README_READ_ONLY.md:7]
- 冻结尺度二。FILE_SHA256SUMS.txt 有 108,117 行，覆盖除清单自身外的全部普通文件。[cmd: 原执行轮 wc -l, 00_project_brief.md:47]
- 冻结尺度三。inputs-readonly 文件总数 108,118 个，含清单自身。[cmd: evidence/history-r1/R1_VALIDATION_REPORT.md:26]
- 输入整体逻辑字节 94,086,734,364，等于 87.63 GiB。du 口径约 88.1 GiB，差量来自分配块，不是范围冲突。[cmd: evidence/sizes_scopes.tsv, 10_phase0_summary.md:61]
- 符号链接 25 条。22 条指向目录内部且可解析，2 条指向内部但目标缺失，1 条指向外部且目标缺失。三条断链都在 tcga_brca_deg_analysis 任务的 .venv 里。[doc: inputs-readonly/README_READ_ONLY.md:31]
- 只读锁实测。目录 555，01 与 04 普通文件 444，03 数据 400，可执行脚本 555，可写路径 0。[cmd: evidence/chmod_wording_check.md]
- 复制一致性。rsync -c 证明副本与原树字节一致，仅权限位按设计不同。19 个文件的分配块差异记录在 evidence/size-compare.tsv。[原执行方记录: evidence/verify-rsync-checksum.log]

## 3 发布任务集与类别分布

- 结论。官方发布集合是 122 条任务，13 个域，全部来自 01 的 full.txt。[cmd: evidence/set_diff_report.md:7]
- full.txt 共 124 行，其中 2 行注释头，任务 122 条。[cmd: evidence/set_diff_report.md:7]
- 域分布。business_finance 19，computing_math 19，education_info 2，engineering 16，health_medicine 19，legal 2，life_sciences 12，other 2，physical_sciences 14，psychology_neuro 3，social_sciences 1，transport_safety 2，visual_media 11。[cmd: 05_task_category_summary.csv, evidence/set_diff_report.md]
- CS 排除口径。computing_math 域 19 条按当前统计口径标记为 CS 并排除。04 的 cs_excluded 列只有这 19 行是 true。[cmd: 04_task_inventory.csv]
- CS 排除是项目统计过滤条件，不是官方分类。computing_math 的官方类目描述不在输入内。[unknown: evidence/history-r1/R1_VALIDATION_REPORT.md:51]
- 非 CS 剩 103 条。103 条是官方参考资产，不自动计入 500，也不是转换承诺。[doc: 10_phase0_summary.md:66]
- 05 的 TOTAL 行写 tasks 122 与 retained_for_500 103，与域行求和一致。[cmd: 05_task_category_summary.csv]
- 500 条的来源。全部来自专家新生产链路，官方 122 条只作参考。[doc: 00_project_brief.md]
- 08 的 proposed_tasks 列是生产目标配额草案，不是官方任务转换计数。[doc: 08_coverage_matrix_draft.csv 注行]
- 12 个非 CS 域的提议配额合计 500。business 50，education 36，engineering 50，health 60，legal 36，life 48，other 32，physical 46，psych 34，social 34，transport 34，visual 40。[cmd: 08_coverage_matrix_draft.csv]
- computing_math 行的 proposed_tasks 是 0，并标注排除。[cmd: 08_coverage_matrix_draft.csv]
- 配额是草案不是决策。正式配额转正与排产由项目负责人裁决。[doc: 10_phase0_summary.md:65, 09_unknowns_and_decisions.md 条目 2]
- 物理卡片对照。01 仓库物理 task_card.json 有 135 张，比发布集多 13 张。多出的是 demo 8 张、visual_media 4 张、engineering 1 张，都不在任何 selected_tasks 名单与 v1.1 退役名单里。未发布或 demo 是推断。[cmd: evidence/set_diff_report.md:26-46]
- 03 数据树按任务拆开是 122 个目录，与 full.txt 一比一。[cmd: evidence/set_diff_report.md:50]
- 退役历史。v1.1.md 记录 30 条退休与 57 条修改。[doc: 02_repo_inventory.md]
- 历史数字 153 与 152 在全输入内没有任何出处。[unknown: evidence/history-r1/R1_VALIDATION_REPORT.md:52]
- 变体目录。数据侧有 100 个 base 与 22 个具名变体目录，wsi_tumor_localization_1 用 center_point。旧变体到新格式单声明目录的映射规则未定。[cmd: 09_unknowns_and_decisions.md 条目 10]

## 4 新旧任务格式与工程交接

- 结论。新格式是 Harbor 1.4 加 ALE 扩展，合同里只有两个必填字段，交接依赖任务自带验证脚本与 validate 两道关。[doc: 07_old_new_format_comparison.md]
- schema。task.toml 的 schema_version 只接受字面量 1.4+ale.1。[code: inputs-readonly/02_ale/packages/ale-core/src/ale/core/taskspec.py:793]
- 必填字段。TaskConfig 只有 schema_version 与 [task].name 必填，其余六字段全有默认值。[code: inputs-readonly/02_ale/packages/ale-core/src/ale/core/taskspec.py:783-800]
- 最小合法任务。{"schema_version":"1.4+ale.1","task":{"name":"org/demo"}}。[code: evidence/engine_format_evidence.md]
- 目录必填。task.toml 与 instruction.md。Linux 与 macOS 用 tests/test.sh 与 solution/solve.sh，Windows 用 test.ps1 与 solve.ps1。[doc: inputs-readonly/02_ale/docs/specs/task-authoring.md:36-43]
- 输入投递一。大资产走 HF dataset，显式同步后落到 environment/assets、tests/assets、solution/assets 三根，默认命名空间 agents-last-exam，运行从不隐式下载资产。[code: inputs-readonly/02_ale/packages/ale-run/src/ale/run/assets.py:26-33]
- 输入投递二。小输入与软件由镜像内文件加 setup 脚本交付，不是固定卷。[doc: inputs-readonly/02_ale/docs/specs/task-authoring.md:362-372]
- 旧输入语义。inputFiles 是旧任务卡专属数组，元素是 name、format、path、description。135 张卡里有 122 张声明了 inputFiles。[cmd: evidence/engine_format_evidence.md]
- artifacts 语义。artifacts 是输出收集路径声明，不是输入清单。声明之后还要运行侧 ArtifactPolicy 设成 collect=host 才会收集，默认 none。[code: 07_old_new_format_comparison.md artifacts 节]
- metadata 语义。metadata 是自由字典 dict[str, Any]，引擎运行时不解释只原样携带。lint 只静态读 metadata.network_justification 一项。[code: inputs-readonly/02_ale/packages/ale-core/src/ale/core/taskspec.py:783-800, 02_ale/docs/specs/task-authoring.md:211]
- 验证合同一。任务自带 tests/test.sh，两行脚本 exec python3 verify.py。verify.py 调 ale_verify 检查并写 reward.json，内容含 reward 与 format。[doc: evidence/notes/03_04_task_data_and_templates.md:370-373]
- 验证合同二。reward 取值 0 到 1，两位小数。[code: inputs-readonly/02_ale/packages/ale-verify/src/ale_verify/__init__.py:114-132]
- 验证合同三。reward.json 产物路径是 /logs/verifier/reward.json。[doc: 07_old_new_format_comparison.md:530]
- validate 两道关。全新沙箱跑出零分必须通过，满分 oracle 必须通过，两道都用干净沙箱。[doc: evidence/notes/02_ale.md]
- 三条工程交接链分立记录。[doc: 07_old_new_format_comparison.md]
- 链一，旧 ALE 迁移。01 的 feat/tasks-v2 未合并分支预览了 instruction.md、setup/run.sh、verify/run.sh、oracle/run.sh 与 task.yaml，只到 task.yaml，不是 task.toml，成熟转换器未发布。[doc: 07_old_new_format_comparison.md 三条链节]
- 链二，Harbor 与 ALE 互转。官方文档一处说 ALE 任务经一次 conversion 达 Harbor，引擎代码一处说纯 1.4 的 Harbor 文件一次 conversion 变 ALE，方向表述相反。本快照没有转换器命令或模块，CLI 只有 assets、vm-image、sandbox、new-task、run 系列。[code: 07_old_new_format_comparison.md, evidence/engine_format_evidence.md]
- 链三，专家 Canonical Task Source。专家在平台新生产，不是官方任务的迁移。转换器未随引擎交付，交付方向与时点待定。[prereq: 00_project_brief.md, 09_unknowns_and_decisions.md 条目 1]
- 元数据缺口。新格式没有 id、difficulty、subject、cost 等分类字段，登记位置未定。[unknown: 09_unknowns_and_decisions.md 条目 3]

## 5 系统与外部约束

- 结论。官方 OS 口径是 86 Linux 与 36 Windows，排除 CS 后是 71 Linux 与 32 Windows。Windows 首期决策与 GPU 预算没有执行侧结论。[cmd: 04_task_inventory.csv]
- 全量 OS。122 条里 os_linux 为 yes 的 86 条，os_windows 为 yes 的 36 条，两列互补。[cmd: 04_task_inventory.csv]
- 非 CS OS。103 条里 Linux 71 条，Windows 32 条。[cmd: 04_task_inventory.csv]
- 候选集口径。71 条非 CS Linux 是官方参考研究的候选集，不是转换承诺，也不自动计入交付。[doc: 09_unknowns_and_decisions.md:68]
- Windows 挂起。32 条 Windows 整体挂起，首期是否纳入状态 OPEN，决定权在项目负责人。[doc: 09_unknowns_and_decisions.md:70]
- Windows 域分布。visual_media 9 条最多，business_finance 7 条次之，其余域合计 20 条。[cmd: 05_task_category_summary.csv 注列]
- GUI 全集。yes 40 条，unknown 9 条，no 73 条。[cmd: 04_task_inventory.csv gui_status 列]
- GUI 非 CS 范围。yes 36 条，unknown 8 条，no 59 条。[cmd: 04_task_inventory.csv gui_status 列]
- 9 条 GUI unknown 分布。business 2，computing 1，engineering 2，life 2，transport 1，visual 1。[cmd: 04_task_inventory.csv gui_status 列]
- GUI unknown 语义。这 9 条的任务是否强制 GUI 没有证据，一律不可写成无 GUI。[unknown: evidence/history-r1/R1_VALIDATION_REPORT.md:50]
- GPU 全集 3 条，全在 Windows 侧。engineering/humanoid_velocity_tracking_policy，visual_media/chroma_key_from_reference，visual_media/compress_3dgs_scene_ply。[cmd: evidence/gpu_cross.tsv, inputs-readonly/01_agents-last-exam/selected_tasks/gpu.txt]
- 3 条 GPU 任务都是官方 gpu.txt 成员，快照名都是 gpu-free。[cmd: evidence/gpu_cross.tsv]
- GPU 决策。GPU 预算未提供不等于已决定没有 GPU 预算，采购与 provider 接入待确认。[doc: 09_unknowns_and_decisions.md 条目 8]
- 外部服务全集。external_service 非 none 的 13 条，全部在非 CS 范围。[cmd: 04_task_inventory.csv]
- staged-local 5 条。BPMN 双任务在 Linux，即 bpmn_supply_disruption_l3 与 bpmn_category_governance_restructuring_l3，用 localhost:8080 的 Flowable。metabase_bi_dashboard_01、odoo、taxform_4_1 在 Windows，分别用 localhost:3000、localhost:8069、localhost:8080 表单。[cmd: evidence/staged_local_os.tsv]
- online-required 6 条。business 的 ar_full_1500、ar_full_300、equity_research_summary、ff5_public_reconstruction，physical 的 egt710_table1_smiles_extraction、ketcher_smiles_reproduction。[cmd: 04_task_inventory.csv]
- public-ref 2 条。life_sciences/tp53_locus_variant_histone_browser_svg 开 UCSC 浏览器，other/mota_exploration 用 Ruffle 演示页作可选回退。[cmd: evidence/staged_local_os.tsv]
- 外部服务方案。13 条任务的重新宿主与网络策略未定。[doc: 09_unknowns_and_decisions.md 条目 9]
- Docker 例外 8 条。business BPMN 双任务，computing 的 k8s_migration_1，engineering 的 cailian_road_highway_alignment_2、gcode、inner_support_elevation_optimization、openroad_sky130_ibex_pnr_signoff，psychology 的 scene2_resample。[cmd: 04_task_inventory.csv linux_runnable 列]
- 官方的 Docker 仅限 Linux 口径把这 8 条排除，逐条原因保留在 06 与证据里，不预设必须走 VM。[doc: 06_runtime_provider_matrix.md, 09_unknowns_and_decisions.md 条目 7]
- 运行状态。全部 122 条的 run_state_current 都是 NOT_RUN，这是冻结事实，不是本轮漏执行。[cmd: 04_task_inventory.csv]

## 6 Provider 能力与验证边界

- 结论。8 个模型 provider 与 4 个沙箱 provider 的声明来自引擎代码。一切运行结论停在 NOT_RUN。[code: 06_runtime_provider_matrix.md]
- 模型 provider 8 个字面量。anthropic、gemini、meta、moonshot、openai、qwen、xai、zai。[code: inputs-readonly/02_ale/packages/ale-core/src/ale/core/config.py:156]
- 模型方言 4 个。anthropic、gemini、openai-chat-completions、openai-responses。[code: inputs-readonly/02_ale/packages/ale-core/src/ale/core/config.py:158]
- 凭据形态。ALE_<PROVIDER>_API_KEY 与 ALE_<PROVIDER>_BASE_URL 自定义端点。[doc: 06_runtime_provider_matrix.md 模型层]
- 沙箱内 agent 只拿 Gateway token，不拿 provider 键。[doc: inputs-readonly/02_ale/.env.example]
- 模型 provider 与沙箱 provider 是两个维度，必须分开。[prereq: 00_project_brief.md]
- 沙箱 provider 4 个。docker 本地容器，qemu QEMU 与 KVM guest，daytona 云端容器，orchard macOS VM 且只支持 Mac 宿主。[code: 06_runtime_provider_matrix.md 沙箱层]
- 容器 provider 字面量只有 docker 与 daytona，VM provider 字面量只有 qemu。[code: inputs-readonly/02_ale/packages/ale-core/src/ale/core/config.py:257-281]
- RETAINING_PROVIDERS 是 docker、qemu、daytona，不含 orchard。[code: inputs-readonly/02_ale/packages/ale-run/src/ale/run/providers/__init__.py:16]
- qemu preflight 要求 /dev/kvm 存在且可读写，缺失时报硬件虚拟化缺失。[code: inputs-readonly/02_ale/packages/ale-run/src/ale/run/providers/qemu.py:703-726]
- 引擎对嵌套虚拟化没有任何语句。[cmd: 06_runtime_provider_matrix.md 检索零命中]
- 腾讯云 Linux 不能嵌套虚拟化是项目前提，不是引擎声明。由 /dev/kvm 要求推出当前服务器不能直接跑任何 guest VM。[doc: 00_project_brief.md 前提, evidence/runtime_claim_audit.md]
- daytona 需要本地 docker 加 ssh 加 ALE_DAYTONA_API_KEY，默认 target 是 us。[code: 06_runtime_provider_matrix.md daytona 节]
- Windows 路径声明。引擎 qemu provider 声明支持 Windows guest，作者规范要求 VM 加 PowerShell。[code: inputs-readonly/02_ale/packages/ale-run/src/ale/run/providers/qemu.py:6-8, doc: 06_runtime_provider_matrix.md:364]
- Windows 验证边界。镜像与显卡组合在腾讯云 Linux 上未验证，状态 unknown。[unknown: 06_runtime_provider_matrix.md:192]
- GUI 基础镜像。container-ubuntu22、vm-ubuntu24、vm-windows10 是私有 BYOL 种子配方。[code: 06_runtime_provider_matrix.md GUI 节]
- 桌面有无由镜像配置决定，依据 display-manager.service 或 DISPLAY 与 WAYLAND_DISPLAY 变量。[code: 06_runtime_provider_matrix.md GUI 节]
- 屏幕控制。内置 cua-desktop MCP，版本 0.3.0，Run 层 opt-in，没有任何 preset 默认打开。[code: inputs-readonly/02_ale/packages/ale-run/src/ale/run/tools/cua_desktop_mcp.py:26]
- Playwright 依赖为零。ale-run 依赖是 huggingface-hub、ale-core、ale-verify、typer、aiohttp、pyyaml，全仓检索零命中。[cmd: 06_runtime_provider_matrix.md GUI 节]
- 网络三模式。no-network 默认且只连 Gateway，另有 allowlist 与 public。[code: inputs-readonly/02_ale/packages/ale-core/src/ale/core/taskspec.py:696]
- macOS 任务必须声明 public，public 要 metadata.network_justification 过 lint。[doc: 06_runtime_provider_matrix.md 网络节]
- GPU 接入声明。docker 读宿主 nvidia-smi，qemu 绑 vfio-pci，daytona 映射云端机型，orchard 拒绝一切 GPU。[code: 06_runtime_provider_matrix.md GPU 节]
- 三层可运行性。旧支持名单只作候选标注，引擎声明只作能力，当前宿主实测是全 NOT_RUN。[doc: 10_phase0_summary.md:68-74]
- 旧名单。docker_support 78 条加 8 条排除，ale_cli 86 条，gpu.txt 3 条，cpu.txt 119 条。[cmd: inputs-readonly/01_agents-last-exam/selected_tasks/]
- 轮一引擎主张审计。32 supported，24 partially-supported，10 unsupported，9 not-explored。[cmd: evidence/runtime_claim_audit.md]
- 措辞纪律。本报告不出现任何可跑通表述，运行结论全部停在 NOT_RUN。[规则: 10_phase0_summary.md:68-74]

## 7 专家新任务生产原则

- 结论。500 条全部走专家生产 Canonical Task Source，冻结成 Engineering Ready 快照后交工程。[prereq: 00_project_brief.md]
- 生产链。专家在平台生产任务，平台做内容审核与冻结，工程做 ALE 转换与运行验证。[doc: 00_project_brief.md]
- 官方资产只作专家生产的事实参考，不自动变成交付。[doc: 00_project_brief.md]
- P0-9 定性。P0-9 是决策编号，不是流水线阶段编号。[prereq: 09_unknowns_and_decisions.md:42]
- 已批 6 项机制。全量自动检查、专家自检、Agent 质量预审、风险分层人工审核、工程自动验证、项目负责人批次放行。[prereq: 09_unknowns_and_decisions.md:43]
- 未冻结参数。抽样率、风险阈值、审核人数。[prereq: 09_unknowns_and_decisions.md:44]
- 建议值。1 GiB 资产线、双审配置都是建议，负责人校准后才生效。[suggestion: 09_unknowns_and_decisions.md:44]
- UNKNOWN 通道。UNKNOWN 项不自动落入低风险层。[prereq: 09_unknowns_and_decisions.md:45]
- GUI unknown 通道。gui_status 是 unknown 的 9 条不进自动低风险通道。04 对 unknown 且无其他重因子的行把 engineering_risk 与 audit_risk 写成 UNKNOWN，附注 GUI必要性待核实。原有依据的 medium 或 high 不降。[suggestion + cmd: 09_unknowns_and_decisions.md:54, 04_task_inventory.csv]
- 风险分层是建议。Tier A 高险全查，Tier B 域核验，Tier C 常规抽查，入口与出口待负责人校准。[suggestion: 09_unknowns_and_decisions.md:47-53]
- 配额与排产。500 配额转正与生产节奏由负责人裁决。[doc: 09_unknowns_and_decisions.md 条目 2]

## 8 决策、未知与风险

- 已定决策。输入冻结与四道门边界已立。CS 排除口径已立。两条链路分离已立。P0-9 六机制已批。三层可运行性表述已立。9 条 GUI unknown 的风险通道已立。staged-local 系统归属按逐任务聚合。任务名字节按 task_id 关联。[doc: 09_unknowns_and_decisions.md, 10_phase0_summary.md, evidence/history-r2/R2_VALIDATION_REPORT.md]
- 体积口径。逻辑字节与 du 的差量来自分配块，该项已闭环，不再列为开放问题。[cmd: 09_unknowns_and_decisions.md 条目 5]
- 待决 16 项清单出自 09，逐条如下。转换器方向与交付时点。500 排产。分类字段登记层。Windows 首期 OPEN。输出文件数口径差已记录不复现。Docker 例外承载路径。GPU 采购与接入。外部服务 13 条方案。变体目录映射规则。feat/tasks-v2 分支取舍。命名空间拼写统一。Windows 静态迁移成本。@task-params 无命中保持结论。标题归一化只在展示列。许可不下法律结论。[doc: 09_unknowns_and_decisions.md:23-38]
- 主要风险 6 条。转换器未随引擎发布。专家生产与工程验证吞吐匹配未定。大资产存储与传输成本未核算。13 个外部服务任务方案未定。Windows 挂起削弱 visual_media 官方参考。UNKNOWN 不落低风险且分层参数待校准。[doc: 10_phase0_summary.md:89-96]
- 验证报告剩余 UNKNOWN，R2 不强行收口。humanoid_wbc_policy_evaluation 的任务卡没有 vm.timeout。9 条 GUI unknown 必要性待复核。computing_math 官方类目描述不在输入。153 与 152 无出处。部分评分入口函数静态不可见。13 张额外卡未发布或 demo 是推断。atlas_outpost_graybox_navigation 提示文写 Windows GPU VM 而快照是 cpu-free。3 个任务 software 字段为空以 main.py 顶层导入兜底。Windows 首期、GPU 预算、正式配额三件事在负责人手里。Windows 与 qemu 路径本轮 NOT_RUN。[doc: evidence/history-r1/R1_VALIDATION_REPORT.md:45-58, evidence/history-r2/R2_VALIDATION_REPORT.md:90-99]
- GUI 风险格。9 条 GUI unknown 任务的工程与审核风险格保持 UNKNOWN，这是正确口径，不是分级失效。[cmd: evidence/history-r2/R2_VALIDATION_REPORT.md 缺陷 D 关闭记录]
- 后续入口。本报告是 Phase 0 最终基线。下一阶段的排队从负责人对 Windows、GPU 预算、正式配额、排产与转换器的裁决开始。[doc: 09_unknowns_and_decisions.md, 10_phase0_summary.md]
- 硬边界。本轮不进入 P0.5 或 P1，不设计平台，不自动清理历史目录。[doc: 10_phase0_summary.md:100]

## 9 证据来源

- 基线文件。00_project_brief.md 到 10_phase0_summary.md 共 11 份，其中 04_task_inventory.csv、05_task_category_summary.csv、08_coverage_matrix_draft.csv 是表格。
- 任务书。evidence/history-r1/EXECUTION_BRIEF_FROM_CHAT.md 与 evidence/history-r2/EXECUTION_BRIEF_R2_CHAT.md。
- 验证报告。evidence/history-r1/R1_VALIDATION_REPORT.md、evidence/history-r2/R2_VALIDATION_REPORT.md、evidence/history-r2/CHANGELOG_R2.md。
- 体量与归属。evidence/sizes_scopes.tsv 四口径字节。evidence/gpu_cross.tsv GPU 与快照交叉。evidence/staged_local_os.tsv 外部服务分级与系统。evidence/file_attribution.tsv 大文件归属。
- 集合证据。evidence/set_diff_report.md 集合差异与退休历史。evidence/template_tasks.tsv 模板任务清单。evidence/symlink_resolution_r1.tsv 软链接解析。
- 引擎证据。evidence/engine_format_evidence.md 格式断言底座。evidence/runtime_claim_audit.md 轮一主张裁定。evidence/license_evidence.md 许可检索。evidence/chmod_wording_check.md 权限位。evidence/notes/02_ale.md 与 evidence/notes/03_04_task_data_and_templates.md 引擎与模板笔记。
- 验收证据。evidence/checker_output.txt。evidence/counterexample_results.tsv。evidence/AG_REVIEW_EXECUTOR_READBACK.md。evidence/boundary_final_audit.txt。
- 冻结输入。inputs-readonly/README_READ_ONLY.md、inputs-readonly/FILE_SHA256SUMS.txt、inputs-readonly/SOURCE_MAP.tsv、inputs-readonly/SYMLINKS.tsv，以及 inputs-readonly/01_agents-last-exam、inputs-readonly/02_ale、inputs-readonly/03_ale-data、inputs-readonly/04_ale-tasks-base 四份快照。
- Git HEAD。01 是 2e91edd3cd26baa35a38127c90c8e5241dfbe62f。02 是 73517c2eb097abe7974e9ec4de9819a02cd0ee81。04 是 492249a2ca4b9d74efd3584a90399473c2e928c7。03 无 git。[cmd: evidence/history-r2/R2_VALIDATION_REPORT.md bd-06]
- 证据分级规则五档。doc 指官方文档或原文。code 指引擎代码行。cmd 指本轮或原执行方的命令输出。inference 指由证据推出的推断。unknown 指无证据。[doc: 00_project_brief.md 证据规则]
- 引用纪律。无证据不写实，没运行不写 PASS，引用不存在的来源等于无证据。[方法: 00_project_brief.md R10 规则]

状态:Phase 0 CLOSED。
Phase 0 已完成并验收通过。
历史目录已归档并完成清理。
analysis/phase0-final/ 是当前唯一有效基线。
Phase 0 最终基线已验收，历史版本已归档，后续不再修改 Phase 0 内容。