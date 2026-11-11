# 仓库结构对比

最终基线版。继承自 R2 修订版（R2 改动对照见 evidence/history-r2/CHANGELOG_R2.md），正文与 R2 一致。R1 版 SHA256 83db547a9f10a859，继承来源与哈希见 SOURCE_MANIFEST_FINAL.json。

## 顶层布局

四份输入的顶层目录如下。全部来自本代理的 ls 抽查。[cmd: ls]

| 输入 | 顶层条目 |
| --- | --- |
| 01_agents-last-exam | AGENTS.md、LICENSE、LICENSE-DATA、README.md、ale_run/、assets/、configs/、docs/、env/、example_exp.yaml、pyproject.toml、releases/、scripts/、secret/、selected_tasks/、tasks/、tests/、uv.lock |
| 02_ale | AGENTS.md、CLAUDE.md、Justfile、README.md、docs/、images/、packages/、pyproject.toml、scripts/、tests/、uv.lock |
| 03_ale-data | archive/、task-data-v1.1/（其下 13 个类别目录） |
| 04_ale-tasks-base | Justfile、README.md、tasks/ |

## 01_agents-last-exam 布局

- ale_run/ 是旧基准的 CLI 运行包，只有 run 与 list 两个子命令。[doc: evidence/notes/01_agents-last-exam.md]
- tasks/ 按任务组织，每任务一个目录。
- selected_tasks/ 放不同运行配方的清单（ale_cli.txt、docker_support.txt、cpu.txt、gpu.txt、full.txt、v1.1_modified.txt 等）。[code: 01_agents-last-exam/selected_tasks/]
- docs/ 放发布说明与文档站，其中 releases/v1.1.md 是 v1.1 变更记录，ale-docs-site/pages/local-docker.html 是 Docker 运行性说明。[code]
- secret/ 与 env/ 存在，是旧引擎主机侧配置目录。[inference: 目录名与旧引擎笔记一致]
- docs/ 之外另有 releases/ 目录，两者分离。[cmd: ls]

单任务目录形态。抽查 business_finance/american_option_pricing_ls 得 main.py、scripts/、task_card.json 三项。[cmd: ls]

main.py 的头部固定写明 domain、task、variant，导入 cua_bench，挂接 BaseTaskSetup 与 LinuxTaskConfig 或 GeneralTaskConfig，从 scripts/ 导入评分函数。[code: 01_agents-last-exam/tasks/business_finance/american_option_pricing_ls/main.py:1-40]

task_card.json 承载任务元数据与提示词。字段有 taskId、title、summary、category、software、taskPrompt、agentMustDo、inputFiles，还有 vm 配置段。[code: 同一任务的 task_card.json:1-45]

## 02_ale 布局

- packages/ 是单仓多包：ale-core（任务契约与配置）、ale-run（运行与提供方）、ale-verify（验证）。[doc: evidence/notes/02_ale.md]
- docs/specs/ 拥有任务契约文档，task-authoring.md 定义任务文件夹。[doc: 02_ale/docs/specs/task-authoring.md]
- images/ 放基础镜像配方。[code: 02_ale/images/README.md:7-9]
- scripts/ 与 tests/ 是引擎自身的工程脚本与测试。[cmd: ls]
- Justfile 提供 lint 与 test 等工程入口。[code: 02_ale/Justfile]

## 03_ale-data 布局

- archive/ 放 ale-tasks-data.tar.gz，官方发布压缩包，约 36.5 GB。[cmd: manifest 求和]
- task-data-v1.1/ 下 13 个类别目录，共 122 个任务目录。[cmd: find 抽查]
- 任务目录下按变体分子目录。多数任务是 base，少数是命名变体。 [doc: evidence/notes/03_04_task_data_and_templates.md]
- 变体目录内部常见 input、reference、software 三个子目录。抽查 american_option_pricing_ls/base 三项齐全，wsi_tumor_localization_1/center_point 有 input 与 reference。[cmd: ls 抽查]

## 04_ale-tasks-base 布局

- tasks/ 下两个顶层分组 demo 与 example_task。任务声明目录按 task.toml 计数共 11 个。demo 组 10 个，example_task 组 1 个。[cmd: R1 find 计数]
- 任务文件夹形状为 task.toml、instruction.md、environment/、tests/、solution/。[code: 04_ale-tasks-base/tasks/example_task/]
- 形状与引擎契约一致。environment/ 放机器构建，tests/ 放验证，solution/ 放已知好解。[doc: 02_ale/docs/specs/task-authoring.md:20-42]
- 仓库级只放 Justfile、README 与任务目录，无引擎代码。[cmd: ls]

## 对比表

| 维度 | 01 旧仓库 | 02 新引擎 | 03 数据 dump | 04 模板仓库 |
| --- | --- | --- | --- | --- |
| 任务定义文件 | main.py + task_card.json | 无任务，只给契约 | 无，只有数据 | task.toml + instruction.md |
| 任务元数据 | task_card 的 title、summary、category、software | 无内置分类字段 | 无 | task.toml 只有 name、description、version、authors、keywords |
| 环境定义 | vm.snapshot 引用预烤镜像 | environment 表加环境构建目录 | runtime_env 与 software 归档在数据里 | environment/ 目录 |
| 验证方式 | scripts/ 里的评分脚本 | verifier 表加 tests/（test.sh、verify.py） | reference 目录 | tests/ 目录 |
| 提示词 | task_card.json 的 taskPrompt | 契约要求 instruction.md | 无 | instruction.md |
| 输入投递 | taskPrompt 点名 base/input 可见文件 | 无输入清单字段，输入走镜像文件、setup 脚本与 HF 资产 | input 目录 | 由 instruction 与 environment 决定 |
| 输出收集 | 无对应字段 | artifacts 数组，声明输出收集路径 | reference 目录（参考输出） | task.toml 的 artifacts 字段声明 |
| 清单机制 | selected_tasks/ 的各配方清单 | 无任务清单（群模式） | 磁盘目录 | 无 |
| 数据资产 | 少量脚本，输入在镜像或远程 | assets 命令管理 | 全量输入与参考 | 示例无大资产 |

## 结构含义

- 01 是完整的旧闭环。任务、提示、清单、运行文档都在一个仓库。
- 02 只有运行时与契约。任务内容被移到独立任务仓库，模板仓库是样板。
- 03 把大宗资产与任务定义分离。官方参考研究链路里，对齐时可按任务把 03 的 input 挂到新格式任务的 environment 或 assets。
- 官方参考对齐的每任务工序因而是三步。取出 01 的提示词与卡片，取出 03 的输入与参考，按 04 的形状组装成对齐用包。此三步属于参考研究链路，不等同于交付。500 条交付任务由专家新生产，走专家生产链路。参考与交付三条链路的区分见 07_old_new_format_comparison.md 与 00_project_brief.md。