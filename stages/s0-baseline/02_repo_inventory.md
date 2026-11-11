# 仓库盘点

## 四份输入的定位

| 快照目录 | 身份 | HEAD 与标签 | 文件数 | 大小 | 角色 |
| --- | --- | --- | --- | --- | --- |
| 01_agents-last-exam | rdi-berkeley/agents-last-exam，旧官方公开基准仓库 | 2e91edd3cd26baa35a38127c90c8e5241dfbe62f，tags v1 与 runtime-qe-bgw-6.7.0-4.0 | 28,444 | 约 1.5 GiB 逻辑字节 [cmd: manifest 求和] | v1.1 已发布任务的权威来源，旧格式与提示词的出处 |
| 02_ale | AgentsLastExam/ale，新引擎仓库 | 73517c2eb097abe7974e9ec4de9819a02cd0ee81，0 标签 | 495 | 约 9.2 MiB 逻辑字节 [cmd: manifest 求和] | 目标运行时，定义 task.toml 1.4+ale.1 契约 |
| 03_ale-data | 无 git，官方 v1.1 数据 dump | 无 | 79,070 | 约 86.1 GiB 逻辑字节 [cmd: manifest 求和] | 任务输入、参考解与运行时资产的大宗来源 |
| 04_ale-tasks-base | AgentsLastExam/ale-tasks-base，新任务模板仓库 | 492249a2ca4b9d74efd3584a90399473c2e928c7，0 标签 | 105 | 约 158 KiB 逻辑字节 [cmd: manifest 求和] | 目标任务格式的样板。tasks/ 下两个顶层分组，任务声明 11 个，见后文 [cmd] |

文件数与负责人预检一致（28,444、495、79,070、105）。[cmd: manifest 过滤求和]

## 01_agents-last-exam

旧官方公开基准仓库，来自 UC Berkeley RDI。内含 v1.1 的 122 个已发布任务，分布在 tasks/ 的 13 个类别目录下，每任务一个主目录。[code: 01_agents-last-exam/tasks/]

发布与运行清单集中在 selected_tasks/ 目录。[code: 01_agents-last-exam/selected_tasks/]

- full.txt 列 122 个已发布任务。
- ale_cli.txt 列 86 个 Linux VM 配置任务，头部标注包含桌面工作流。
- docker_support.txt 列 78 个 Docker 支持任务。
- cpu.txt 列 119 个 CPU 配置任务，gpu.txt 列 3 个 GPU 配置任务。
- v1.1_modified.txt 列 57 个有修改的任务。
- full/ 子目录含 near-term.txt（45）、full-spectrum.txt（46）、last-exam.txt（36）、overall.txt。

发布说明 docs/releases/v1.1.md 记录 30 个任务退役、57 个任务修改，以及 6 个授权软件工作流转为开源工具（Blender、FreeCAD Road、FreeCAD CAM 与 LinuxCNC、Kratos、MuseScore、Ardour）。[doc: 01_agents-last-exam/docs/releases/v1.1.md:58-63]

Docker 运行性文档在 docs/ale-docs-site/pages/local-docker.html。文档写明仅限 Linux 任务，8 个 Linux 任务因嵌套 Docker、GUI 捆绑包或 namespace 需求被排除。[doc: 01_agents-last-exam/docs/ale-docs-site/pages/local-docker.html:121-125]

旧仓库内置的是 cua-bench 运行包（ale_run/），CLI 只有 run 与 list。构建、推送、转换都在私有仓库（AgentHLE），不在本快照。[doc: evidence/notes/01_agents-last-exam.md]

## 02_ale

新引擎仓库，官方继任者。uv 工作区，包为 ale-core、ale-run、ale-verify，版本都是 0.1.1。[code: 02_ale/pyproject.toml]

- 任务契约在 docs/specs/task-authoring.md。它是 Harbor 格式 1.4 加 ALE 扩展（1.4+ale.1），任务文件夹自包含。[doc: 02_ale/docs/specs/task-authoring.md:1-14]
- task.toml 的严格形状在 packages/ale-core/src/ale/core/taskspec.py:783-800。只有 schema_version 与 [task].name 必填。[code]
- CLI 入口为 ale.run.cli.main:main，子命令 run、validate、prepare、reverify（隐藏）、lint、new-task、vm-image、assets、sandbox。[doc: evidence/notes/02_ale.md]
- 模型提供方字面量在 packages/ale-core/src/ale/core/config.py:156，8 家。[code]
- 沙箱提供方有 docker、qemu、daytona、orchard 四个实现文件。[code: 02_ale/packages/ale-run/src/ale/run/providers/]
- HF 资产命名空间在 packages/ale-run/src/ale/run/assets.py:33，为 agents-last-exam。[code]
- 仓库没有 LICENSE 文件。[code: 02_ale 根目录]（见 09 未决问题）
- 作者契约里提到格式转换的原文只有两句话，且方向对称相反。task-authoring.md:9-14 写 ALE 任务经一次 conversion 达到 Harbor，taskspec.py:523-525 常量注释写纯 1.4 是 Harbor 文件、一次 conversion 把它变成 ALE 的。方向未定。引擎快照没有任何转换器命令，CLI 只有 assets、vm-image、sandbox、new-task 与 run 系列。[doc + code: 原文摘录与检索结果见 07_old_new_format_comparison.md 与 evidence/engine_format_evidence.md]（见 09）

## 03_ale-data

官方 v1.1 数据 dump，无 git。顶层两块。

- archive/ 放置 ale-tasks-data.tar.gz，约 36.5 GB，即官方发布数据包。[cmd: manifest 求和]
- task-data-v1.1/ 按 13 个类别目录组织，122 个任务目录与官方清单一一对应。[cmd: find 抽查]

数据树任务目录形态为 task-data-v1.1/<domain>/<task>/<variant>/。变体目录常见 input、reference、software 三个子目录。[cmd: ls 抽查 american_option_pricing_ls/base]

122 个任务里 100 个用 base 变体，22 个用命名变体（含 health_medicine/wsi_tumor_localization_1 的 center_point）。[doc: evidence/notes/03_04_task_data_and_templates.md]（逐任务变体名见 04_task_inventory.csv 的 input_style 列）

### 大文件签名

100 MiB 以上的单文件集中在这几处。字节数来自 SHA256 清单与 R1 逐任务路径重核，换算口径 1 GiB = 1073741824 bytes，1 MiB = 1048576 bytes。[cmd: manifest 过滤 + R1 ls]

| 路径 | 大小 |
| --- | --- |
| task-data-v1.1/psychology_neuro/scene2_resample/base/software/computer_use_benchmark_bundle/containers/slicer_5.0.3_20221025.simg | 8,658,481,183 bytes（约 8.06 GiB） |
| task-data-v1.1/health_medicine/wsi_tumor_localization_1/center_point/input/tumor_001.tif | 3,264,779,514 bytes（约 3.04 GiB） |
| task-data-v1.1/psychology_neuro/celegans_neuron_tracking/137/input/137.h5 | 1,615,261,704 bytes（约 1.50 GiB） |
| task-data-v1.1/health_medicine/prostate_imrt_matrad_reproduction/base/reference/replay_state.mat | 870,922,433 bytes（约 831 MiB） |
| task-data-v1.1/life_sciences/idp_ensemble_scoring/default/input/CSpred/models/CA_R0.sav | 658,672,244 bytes（约 628 MiB） |
| task-data-v1.1/life_sciences/tms_marrow_cell_type_annotation_instance_1/base/input/tms_marrow_unlabeled.h5ad | 635,863,817 bytes（约 606 MiB） |
| task-data-v1.1/social_sciences/atwood_2022_measles_vaccine_reproduction/base/input/replication_package.zip | 432,270,326 bytes（约 412 MiB） |
| task-data-v1.1/engineering/humanoid_wbc_policy_evaluation/base/input/runtime_env/mjlab.zip | 216,693,106 bytes（约 207 MiB） |

扩展名统计（03_ale-data 全树）如下。pdb 37,973，py 13,247，dat 3,751，hea 3,649，csv 3,249，gz 1,443，png 626，so 533，json 520。[cmd: manifest 过滤]

符号链接记录如下。SYMLINKS.tsv 共 25 条，2 条内部断链位于 life_sciences/tcga_brca_deg_analysis 的 .venv，1 条外部断链。[cmd: 行数抽查]

## 04_ale-tasks-base

新任务模板仓库。105 个文件。tasks/ 下只有 demo 与 example_task 两个顶层分组，不是两个任务。任务声明目录按 task.toml 计数共 11 个。demo 组 10 个，example_task 组 1 个。demo 组的 10 个为 docker_in_vm、external_assets、resource_injection、tool_smoke、verification_agent_judge、verification_deterministic、verification_domain_a、verification_domain_b、verification_llm_judge、verification_separate。[cmd: R1 find 计数] 本轮只做静态盘点，未运行任何示例。

example_task 展示完整目标形状。task.toml 只有 16 行。schema_version、artifacts、task 名称、environment 资源、agent 参数（no-network、timeout）、verifier 参数。[code: 04_ale-tasks-base/tasks/example_task/task.toml]

文件夹形状为 task.toml、instruction.md、environment/、tests/、solution/。[code: 04_ale-tasks-base/tasks/example_task/]（与 02_ale/docs/specs/task-authoring.md:20-42 一致）

新引擎开发指南把 ale-tasks-base 称为任务仓库之一，任务仓库共用同一 CI 工作流 task-check.yml。[code: 02_ale/docs/guides/development.md:91-92]

## 关系链

四条关系如下。

- 01 旧仓库与 02 新引擎是官方先后代。组织从 rdi-berkeley 迁到 AgentsLastExam。两仓库之间没有任何内置迁移或转换命令，作者契约里只出现两句方向相反的转换表述。旧任务迁移链路与 Harbor 格式转换链路、专家源到 ALE 的生成链路三者分开，见 07 与 09。[doc: task-authoring.md:9-14 + code: taskspec.py:523-525]
- 02 新引擎与 04 模板仓库是运行时与任务源的分离。任务发布为独立仓库，模板仓库就是群任务的样板。[code: 02_ale/docs/guides/development.md:91-92]
- 03 数据 dump 与 01 旧仓库同源。每个已发布任务在 01 有提示词与卡片，在 03 有输入数据（可能多个变体）。[inference: 多方验证过的目录对应关系]
- 资产命名上游是 HF 的 agents-last-exam 命名空间 [code: 02_ale/packages/ale-run/src/ale/run/assets.py:33]，而任务 org 名是 agentslastexam [code: 04_ale-tasks-base/tasks/example_task/task.toml:5]。两者是不同实体。

## 归属

面向下一轮的角色分工如下。

- 上游所有权归 GitHub 相应组织。本项目只用冻结快照，不上推。
- 专家后续生产 Canonical Task Source，内容来自专家新生产的资料与采集，不是官方 01 与 03 的拷贝或迁移。官方 01 与 03 是研究与对齐参考，不自动计入交付。
- 工程侧以 02 引擎为运行时契约，以 04 模板为任务仓库形状。
- 旧的 main.py 与 task_card.json 只作为转换源，不进入新运行链。