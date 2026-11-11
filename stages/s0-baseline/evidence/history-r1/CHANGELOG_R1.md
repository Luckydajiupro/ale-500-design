# CHANGELOG_R1.md

R1 修订勘误记录。每条记录改前、改后、依据。来源对照见 SOURCE_MANIFEST_R1.json。证据标签沿用五级加 prereq 与 suggestion。

## 父级修订条目

### C01 00_project_brief.md（重写）

- 改前。路线写成"官方 103 条迁移 + 397 条新增"与"先转换 71 条官方 Linux 任务"。CTS 来源写成官方 01 与 03。
- 改后。两条链路分开。专家生产链路产出 500 条交付，官方参考链路只作对齐研究。CTS 内容来自专家新生产，不是官方 01 与 03 的拷贝。不存在 103+397 的已批准方案。
- 依据。R1 任务书确认前提 1 到 6。[prereq] R01。

### C02 00_project_brief.md（重写）

- 改前。环境约束未写嵌套虚拟化限制，默认当前服务器可用 qemu+KVM 的推断出现过。
- 改后。明确当前腾讯云 Linux 服务器不能内部再虚拟化虚拟机。沙箱 provider 与模型 provider 分开。Windows 与 GPU 采用及预算待确认。GPU 预算未提供不等于已决定没有。
- 依据。R1 任务书确认前提 4、5、6。[prereq] R02。

### C03 00_project_brief.md（重写）

- 改前。历史 rsync 与权限检查写成无主语记录，公信力不透明。
- 改后。历史日志明确标注为原执行方（第一轮会话）记录。没有原始日志的不补造，保留证据限制。chmod 表述修正为文件 444 目录 555，属主仍可改回。
- 依据。R1 任务书 R10 与 R12。[prereq] 实际只读属性由 R1 复查确认。[cmd]

### C04 02_repo_inventory.md（7 处修订）

- 改前。04 模板仓写成"只有 demo 与 example_task 两个任务"，共 11 个 task.toml 但表述歧义成两个任务。
- 改后。tasks/ 下 demo 与 example_task 两个顶层分组，不是两个任务。按 task.toml 计数 11 个任务声明目录。demo 组 10 个，example_task 组 1 个。demo 组的 10 个名字列出。只做静态盘点，未运行示例。
- 依据。R1 自查 find 计数。[cmd] R05。

### C05 02_repo_inventory.md（大文件表修订）

- 改前。大文件表只有换算值，无 bytes 基数，且第一轮未标口径。
- 改后。表头注明 1 GiB = 1073741824 bytes。slicer_5.0.3_20221025.simg 8,658,481,183 bytes（8.06 GiB），tumor_001.tif 3,264,779,514 bytes（3.04 GiB），137.h5 1,615,261,704 bytes（1.50 GiB）。
- 依据。FILE_SHA256SUMS.txt 逐文件字节。[cmd] R03。

### C06 02_repo_inventory.md（归属修订）

- 改前。任务内容与数据归后续专家组，"Canonical Task Source 的输入来自 01 与 03"。
- 改后。CTS 内容来自专家新生产的资料与采集，不是官方 01 与 03 的拷贝或迁移。官方 01 与 03 是研究与对齐参考，不自动计入交付。
- 依据。R1 任务书确认前提 1、2。[prereq] R01。

### C07 03_repo_structure_comparison.md（3 处修订）

- 改前。tasks/ 写成"只有 demo 与 example_task"。三步工序写成"转换的每任务工序"，读起来像交付链路。
- 改后。tasks/ 为两顶层分组 11 个任务声明目录。三步工序改成官方参考对齐工序，明确属于参考研究链路，不等同于交付。参考与交付三条链路指向 07 与 00。
- 依据。R1 自查 find 计数，R1 任务书 R01 与 R06。[cmd + prereq]

### C08 09_unknowns_and_decisions.md（重写）

- 改前。开放问题 2 携带"103+397"扩增策略三选项。P0-9 写成 P0 到 P5 的流水线阶段表。风险分层写成分层入口硬条件。Windows 建议写成"先转换验证 71 个官方 Linux 任务"。GPU 写成"首轮无 GPU 预算时"。
- 改后。8 条已确认前提单列并标 prereq。P0-9 是决策编号，6 项机制已批，抽样率、风险阈值、审核人数未冻结。风险分层全部标 suggestion。Windows 结论改成"71 个非 CS Linux 任务构成官方参考研究候选集，不是转换承诺"。GPU 预算未提供不等于已决定没有。16 条待决事项逐条修订，工程可核实与负责人裁决分开。
- 依据。R1 任务书 R01、R02、R08、R13 与确认前提。[prereq]

### C09 10_phase0_summary.md（重写）

- 改前。类别资产写成"1.37 到 16.76 MiB"，实为 GiB 误写。头寸问题写成 103 对 500 差 397 的策略三选项。P0-9 与 Windows 建议携带迁移路线语言。
- 改后。bytes 基准的 13 类资产表，最大三域 health_medicine 17,994,750,542 B、life_sciences 15,585,631,616 B、psychology_neuro 10,278,407,258 B。范围口径拆分 archive、task-data-v1.1、03 全部、inputs-readonly 全部并说明 du 差量。运行性三层分离。500 条全数来自专家生产链路，官方 103 条是参考候选不构成迁移承诺。收尾状态写入"Phase 0 R1修订完成，待复审"。
- 依据。FILE_SHA256SUMS.txt 求和。[cmd] R01、R03、R09。

## 子代理条目

本节在数据侧与引擎侧两位审计员交付后按同一格式补记。每条记改前、改后、依据。
## 子代理条目

### C10 06_runtime_provider_matrix.md（子代理 E 重写，517 行）

- 改前。把 Docker 允许名单直接写成本机可直接落 64 个任务，把 qemu+KVM 自托管写成可行。
- 改后。运行性严格三栏。旧引擎支持名单、新引擎声明、当前宿主机实测分开。当前宿主机一栏全部 NOT_RUN。qemu 需要 /dev/kvm 且在启动时校验，引擎对嵌套虚拟化可行性没有任何表述，标 unknown。宿主机无嵌套虚拟化是任务书前提，不是引擎事实。
- 依据。E 出示 qemu.py:703-726、qemu.py:944 与运行时审计表。[code + doc]

### C11 07_old_new_format_comparison.md（子代理 E 重写，568 行）

- 改前。artifacts 当作输入清单的对应物。难度学科成本必须放引擎之外。转换方向写成 Harbor 到 ALE 的单一方向承诺。
- 改后。artifacts 是输出收集路径，不是输入清单。inputFiles 只存在于旧格式。metadata 是自由字典，任意键引擎不解释，唯一静态读取是 lint 查 network_justification。转换只有两句方向相反的原文，task-authoring.md:9-14 写 ALE 到 Harbor，taskspec.py:523-525 写 Harbor 到 ALE，方向未定且引擎没有转换器命令。三条链分开：旧 ALE 迁移、Harbor 格式转换、专家 CTS 到 ALE 生成。
- 依据。E 出示 taskspec.py:74-84、taskspec.py:523-525、task-authoring.md:9-14、task-authoring.md:211 与 supako 全仓检索结果。[code + doc]

### C12 evidence/runtime_claim_audit.md（子代理 E 新增）

- 内容。第一轮 06 与 09 的每条引擎论断逐行审计。结果：支持 32 条、部分支持 24 条、不支持 10 条、未探索 9 条。不支持项含宿主机可运行性、qemu+KVM 自托管、P0-9 作为流水线阶段 P0 到 P5、artifacts 作输入清单、分类必须放格式之外。
- 依据。E 对第一轮文件的逐行比对记录。[cmd + code]

### C13 evidence/license_evidence.md（子代理 E 新增）

- 内容。01_agents-last-exam 有 Apache-2.0 代码许可与 CC BY 4.0 任务数据许可，含 pyproject:10 字段与 README 徽章，另有 vendored 上游各许可。02_ale 与 04_ale-tasks-base 全仓没有任何许可文件、字段、徽章或章节，记 unconfirmed。不从中得出法律结论。
- 依据。E 的文件检索记录。[cmd]

### C14 evidence/historical_log_index.md（子代理 E 新增）

- 内容。逐一核对 .audit 实存文件与审计要点。要点：委派要点里把基线 tsv 写成了 original-baseline-20261108-225436.tsv，实存是 original-baseline-20261108-225402.tsv。225436 这个名字不存在，第一轮交付物没有引用它，如实记录，没有炮制。7 份历史审计文件与 6 个脚本齐全。
- 依据。E 对 .audit/ 的 ls 与逐项 read。[cmd]

### C15 evidence/engine_format_evidence.md 与 evidence/r1_engine_notes.md（子代理 E 新增）

- 内容。engine_format_evidence.md 972 行，存引擎原文摘录与检索结果，供 06 与 07 引用。r1_engine_notes.md 48 行，E 的工作备注。
- 依据。E 的静态读取。[code + doc]
## C16 父文件与 D 清查对账（脚本 40_reconcile_parent_files.py，12 对，幂等）
- 02_repo_inventory.md 大文件表五行补精确字节。replay_state.mat 870,922,433（约 831 MiB），CA_R0.sav 658,672,244（约 628 MiB），tms_marrow_unlabeled.h5ad 635,863,817（约 606 MiB），replication_package.zip 432,270,326（约 412 MiB），mjlab.zip 216,693,106（约 207 MiB）。此前 811/613/592/202 MiB 偏低。[R03 C11]
- 00_project_brief.md 只读权限表述改精确。目录 555，01 与 04 普通文件 444，03 数据文件与 README_READ_ONLY.md 为 400，可执行脚本 555。[R12 C15]
- 09_unknowns_and_decisions.md 条目 9 外部服务 8 改 13。staged-local 5，online-required 6，public-ref 2。[R04 C4-C7]
- 09_unknowns_and_decisions.md Tier A 入口 GUI 6 个改 40 个明确任务加 9 个 unknown，外部服务 8 改 13。[C13]
- 10_phase0_summary.md 04 清单 30 列改 31 列。[R07]
- 10_phase0_summary.md GUI 6/4 改为 40 yes、9 unknown、73 no，非 CS 范围内 36 yes、8 unknown。外部服务 8 改 13 并带宽细分。[C13]
- 10_phase0_summary.md 官方快照分布改为 86 Linux 与 36 Windows，71/32 仅作非 CS 拆分保留。[R04 C2]
- 10_phase0_summary.md 风险行外部服务 8 改 13，证据标签 inference 改 cmd。[R04]

## C17 C12 核查结论
D 记录的 1,527,077,333 只存在于 D 自己的文件 evidence/r1_data_notes.md 与 scripts/31_build_r1_notes.py。父文件全部使用正确值 1,527,073,733，无需修复。差异 3,600 bytes 只作历史记录保留在 D 的笔记。

## C18 校验脚本同步（scripts/validate_r1.py）
- csv_rows 过滤首个单元格以 # 开头的注释行。04 与 08 的头部注释行不再破坏列数检查。
- 第五节 sizes_scopes.tsv 解析改为 per-domain 行。原写法读图例列 B 导致全部 size 检查误失败。

## C19 清单与证据登记
- SOURCE_MANIFEST_R1.json 的 r1_evidence 从 5 项扩展到 14 项。D 的 9 个证据文件登记 provider child_a，各自的 SHA256 入库。
- 全部 r1_sha256 在对账编辑后重算。05 个父文件其中 00、02、09、10 因本轮修正而哈希变化，03、06、07 未变。

## C20 inputs-readonly mtime 阈值校准
- 校验脚本原阈值 2026-11-08 23:05 早于四条记录文件的合法生成时间。实测最后写入是 FILE_SHA256SUMS.txt 落盘 23:44:55 +0800，此后只有 chmod（只改 ctime）。
- 阈值改为 23:45:00 +0800，并新增普通文件总数 108,117 一致性检查。写入能力主力护栏仍是零可写位检查。

## C21 验证轮收尾
- scripts/validate_r1.py 最终运行 97 项检查全部通过，退出码 0。原始输出存档 evidence/validate_r1_output.txt。
- 12 份轮一产物哈希书挡闭合。hashed_at_post 2026-11-09T13:50:46+08:00。磁盘哈希与 pre 全部一致。
- 越界审计通过。inputs-readonly 零可写位。四份原始目录 unchanged。轮一产物、原目录汇总报告、.audit 全部零改动。R1 期间写入只有 analysis/phase0-official-baseline-r1 子树。
- 新增 R1_VALIDATION_REPORT.md。R01 至 R13 逐项状态、剩余 UNKNOWN 十条、变更文件清单、证据位置、越界审计、未验证项全部收录。
