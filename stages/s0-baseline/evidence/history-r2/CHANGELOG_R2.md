# CHANGELOG_R2.md

Phase 0 R2 定点修复与复验。执行日 2026-11-09。依据为 A 至 G 复审证据回传，回传原文存于 evidence/AG_REVIEW_EXECUTOR_READBACK.md。

结论状态按任务书结尾要求，写在本文件与验证报告的统一结论行。本轮不宣布 Phase 0 最终验收通过。

## 范围与边界

- 本轮唯一写入目录为 analysis/phase0-official-baseline-r2/。
- R1 全部文件、第一轮 12 份产物、inputs-readonly、项目原始四个目录、DIRECTORY_SUMMARY_REPORT.md、历史 .audit 记录全部未改动。src-01 检查在每次运行中逐个重算第一轮 12 项与 R1 52 项共 64 项 SHA256 并比对首次固定值。
- 官方大数据包未重新复制，未重新散列。本轮不宣称重新验证了全部输入字节。
- 未安装环境，未运行官方任务，未跑评测。04_task_inventory.csv 的 run_state_current 全部保持 NOT_RUN，NOT_RUN 是冻结事实，不是本轮漏执行。
- 未更新总体实施方案，未决定 Windows/GPU 预算或正式配额，未进入 Phase 0.5 或 P1。

## A 输入与输出（03_repo_structure_comparison.md）

- pre: 输入投递行的 02 新引擎格写的是 artifacts，与 07 的冻结源码证据冲突。
- post: 该行 02 格改为「无输入清单字段，输入走镜像文件、setup 脚本与 HF 资产」。新增独立「输出收集」行，02 格为「artifacts 数组，声明输出收集路径」，01 格「无对应字段」，03 格「reference 目录（参考输出）」。
- 依据: 07_old_new_format_comparison.md 的 artifacts 语义段落与 taskspec.py 冻结源码。检查: a-01、a-02。

## B 合并遗漏（06_runtime_provider_matrix.md）

- pre: 第 4.1 节残留六个「待合并 / merge point」占位句，外部服务与 GUI 沿用第一轮旧口径。
- post: 第 5 节合入 04 的 external_service 终版统计，staged-local 5、online-required 6、public-ref 2，合计 13 个非 none 任务，并写明 13 个不等于 13 个在线硬依赖。全量与过滤后集合分列。第 6.4 节合入 04 的 GUI 三值统计，全集 40 yes、9 unknown、73 no，非 CS 36 yes、8 unknown、59 no。第一轮 8 任务表与 6-yes 口径保留原文，逐处标注 [历史引用]。
- 依据: 04 external_service 与 gui_status 两列、evidence/staged_local_os.tsv。检查: a-03、b-01、b-02、b-03。

## C 系统归属（09_unknowns_and_decisions.md 与 04）

- pre: 09 原第 63 行声称 5 个 staged-local 应用都在 Windows 集内。
- post: 改为按 04 逐任务记录聚合，2 Linux（两个 BPMN 任务）、3 Windows（metabase_bi_dashboard_01、odoo、taxform_4_1），并写明各处数字单源聚合不手工抄写。Windows 集内另有 3 个 GPU 任务的表述保留。
- 依据: 04 external_service 与 os_linux/os_windows 列交叉聚合。检查: c-01、c-02、c-03。

## D UNKNOWN 与风险（scripts/20_build_04_05.py 与 04）

- pre: risk_cells 只在 gui 等于 yes 时加入 GUI 因子，gui 等于 unknown 且无其他重因子时自动落 low，违反 UNKNOWN 不自动落低风险的约定。
- post: gui 等于 unknown 时一律追加「GUI必要性待核实」因子。分层结果仍为 low 的，engineering_risk 与 audit_risk 写「UNKNOWN (GUI必要性待核实)」。已有依据的 medium/high 保持原级并在启发式串中补记该因子。9 条 GUI unknown 全部不进入自动低风险通道，无人把 unknown 擅自改成 gui=no，也无人把全部 unknown 强行改成 high。
- 受影响行: basel_operational_risk_bia_cn、cell_translocation_analysis、yeast_colony_detection、fds_single_compartment_detector_reconstruction 四行两列改为 UNKNOWN (GUI必要性待核实)，inner_support_elevation_optimization 的 audit_risk 改为 UNKNOWN，工程列保持 medium 并补记因子。其余 unknown 行保持原级并补记。
- 检查: d-01、d-02、d-03。03 的 NOTE_LINE 同步说明该语义。

## E 任务名字节（scripts/21_build_08.py 与 08）

- pre: 08 的 other 与 social_sciences 两行任务名与字节来自手写且错配（social 写了 abm_hangzhou_metro 与 469,325,814 B，other 写 mota_exploration 加 aerobics 的字节数）。
- post: 两行改为从 census 按 task_id 关联排序生成。other 行最大任务 aerobics_wc2026_portugal_trio_difficulty_scoring 180,191,212 B，次任务 mota_exploration 23,838,273 B。social 行唯一任务 atwood_2022_measles_vaccine_reproduction 469,325,814 B。abm_hangzhou_metro 归 transport_safety（178,304,281 B），在 08 说明文字中注明。逐域总量与 evidence/sizes_scopes.tsv 一致。
- 依据: 04 按 task_id 的逐行字节、FILE_SHA256SUMS.txt 按任务路径求和、census 排序重建。检查: c08-e-other、c08-e-social、c04-e-attrib、c08-sizes。

## F 验证器可信度（scripts/validate_r2.py，本轮新建）

- 替换第一轮验证器中不可信的十六进制权限扫描（BSD find 不接受 -perm /222，静默按 0 处理）。改为两部分并分别记录，一是模式位检查 mode & 0o222，二是当前执行身份的 os.access W_OK 检查，均基于 lstat 且不跟随符号链接。遍历错误显式进 errors 列表，任何文件的读取或遍历失败都会使对应检查失败，不静默忽略。
- 明确断言 04 有 122 条数据、122 个唯一 task_id、每行 31 列且列头符合本轮字段约定。明确检查 05 的 TOTAL 行与逐域计数。
- A 至 E 的跨文件断言全部在检查集内，不止检查文件存在或字段取值合法。
- 数据侧 30_checker.py 的有效检查复用，但总入口每次都以子进程实际执行并记录 rc、stdout、stderr、解析 SUMMARY，绝不把历史 11/11 输出冒充本轮执行。
- 每项检查有唯一 check_id、检查对象、判定内容、PASS/FAIL/ERROR/SKIP 状态与证据位置。必查项 FAIL、ERROR 或未执行时总体验证不得通过（rc 非零）。分组数、总数与报告表格全部从同一份 VALIDATION_RESULTS.json 生成，不手工填写，不维持 97 这个历史数字。
- 开发期缺陷修正三条记录在案: WS 常量重复包含 workspace 段导致所有默认路径加倍，首次试运行 32 项 ERROR 暴露后修正。GIT_HEADS 的 ale 头多一个 0（a02cd00ee81），修正为 73517c2eb097abe7974e9ec4de9819a02cd0ee81。e-01 在 sealed 模式原要求 VALIDATION_RESULTS.json 与 R2_VALIDATION_REPORT.md 在检查期存在，而这两份由本轮自身在检查通过后产生，构成死锁，改为 sealed 模式只要求 SOURCE_MANIFEST_R2.json 与 CHANGELOG_R2.md，其余两份的存在与哈希由结封阶段的 FINAL_CHECKSUMS.sha256 承担。
- 结封工具开发期缺陷一条记录在案: 60_build_manifest.py 的 final 模式读取 pre 清单时检查 "mode" 键，而清单实际写入的键名是 "stage"，导致首次 final 运行把 hashed_at_pre 回退成 final 时点（17:52:39）。已改为无条件沿用磁盘上已有的 hashed_at_pre，并将终清单的 hashed_at_pre 修正回真实 pre 时点 2026-11-09T17:42:44+08:00。pre 时点此前仅存在于 pre 运行输出与进度记录中，修正依据两者一致。
- 结封工具开发期缺陷再补两条: (1) sealed 重跑时自身控制台曾直接重定向进 evidence/sealed_stdout.txt（自引用竞态，m-03 瞬时 FAIL），改为重跑时控制台落 /tmp、运行结束后再复制进 evidence，最终由只读 verify 包对；(2) m-02/m-03/m-04 原只在 sealed 模式运行，verify-checksums 模式下被跳过，与“封存后只读复核清单绑定”的设计不符，改为仅在 prefreeze 跳过，sealed 与 verify 两个模式都执行。

## G 完整性与记录范围

- 记录第一轮 12 份产物与 R1 全部小型产物的完整 SHA256，即 evidence/source_hashes_round1_r1.tsv 的 64 行，每次验证运行由 src-01 对磁盘逐项重算比对。
- 参与生成与校验的脚本全部登记在 SOURCE_MANIFEST_R2.json 的 r2_scripts 节，含完整 SHA256。清单信息两阶段生成，pre 覆盖封存前静态集，final 覆盖全部交付集，均以相对路径与 SHA256 记录。
- 原轮文件是否改变、R1 来源是否改变、R2 产物是否与登记版本一致、inputs-readonly 当前权限状态四类检查各自独立（src-01、m 组、in 组），不互相代替。
- 反例测试与原始输出全部落在 evidence/ 内（八 封存要求），counterexamples/ 目录含夹具、每例的验证器原始输出与 results.tsv。

## 反例测试

- scripts/build_fixtures.py 构建 8 个注入用例，scripts/run_counterexamples.py 断言每例触发对应失败且 rc 非零，结果写入 evidence/counterexamples/results.tsv。
- 用例覆盖: 扫描/遍历报错（chmod 000 子目录）、04 少一条数据、证据文件缺失、清单 SHA256 篡改、GUI unknown 被标为 low、staged-local 系统归属错误、任务名称与字节数错配、正文残留待合并占位。
- 全部 8 例最终 TRIGGERED，runner rc 0。c07 首跑未触发的原因是原注入把名称加字节整段对称互换，两个独立的包含式正则各自仍可满足，可读性对称所以检查看似失明。改注入为只互换字节数字后正确命中 c08-e-other。该首跑现象同时说明现有检查以名称与字节的紧邻配对为判定单位，交叉错配会命中。

## 边界事件记录

- 16:24 至 16:28 用户在 ale-data 与 ale-tasks-base 内产生 Finder 产物共 12 项（.DS_Store 与两个含 __MACOSX AppleDouble 的 zip 文件）。bd-06 与 bd-07 依据 evidence/boundary_user_delta.tsv 将它们登记为已知增量。它们不是本轮执行方的写入，也不计入干净工作区判定。
- 首次 sealed 校验（17:43:07）后、最终结封前，用户侧 Finder 又发生多项变化：ale-data/task-data-v1.1/legal.zip 被移除（17:43 至 17:59 之间），ale-data/task-data-v1.1/.DS_Store 被重写（mtime 17:57:51），随后 ale-data/.DS_Store 也被重写（18:10 至 18:17）。18:17 测算确认 ale-data 非 .DS_Store 常规文件恰为 79,070，与原始基线完全相等，即内容文件已回到基线，只有 Finder 元数据在变动。处理：boundary_user_delta.tsv 的 ale-data 段改为 6 行；验证器 bd-07 升级为 v2 断言设计（.DS_Store 行断言存在性与总数，内容增量行断言字节精确；总数为基线 79070 加登记行数 6 = 79076，links=3），任何内容文件增删都会让总数断言失败并触发显式重基线。事件全过程记录于 evidence/boundary_event_r2_note.md 与 evidence/boundary_final_audit.txt 的追加说明。执行器本身零越界写入（bd-01 至 bd-05 通过）。按结封流程重新执行 sealed 校验，使 VALIDATION_RESULTS.json 与冻结的边界登记一致。

## 剩余 UNKNOWN

剩余 UNKNOWN 维持第一轮与 R1 复审后的结论，本轮不强行收口。

- humanoid_wbc_policy_evaluation 的任务卡无 vm.timeout，time_limit_sec 与 time_source 为 UNKNOWN。
- 9 个 gui unknown 任务的 GUI 必要性待复核，风险列已按 D 修正不自动落低风险。
- computing_math 官方类目描述不在输入内，CS 排除是项目口径过滤器，已记录映射依据。
- 历史 153 与 152 数字在输入内未找到出处。
- 拓扑结构与 hook 评分入口对部分任务不可静态可见，沿用 R1 结论。
- Windows 首期是否纳入、GPU 预算、正式配额仍未决定，属项目负责人决策项。

## 验证执行顺序与结果归属

- 反例测试结果见 evidence/counterexamples/results.tsv。
- 正式校验（--sealed）的结果、输出与退出码见 evidence/validate_r2_output.json、evidence/validate_r2_output.txt、evidence/sealed_stdout.txt、evidence/sealed_stderr.txt 与 progress.log 中的记录。
- 结封复验（--verify-checksums）只读执行，其退出码与汇总在聊天回传中报告，封存后不再改动树内任何文件。