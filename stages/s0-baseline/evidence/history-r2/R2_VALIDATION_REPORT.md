# R2_VALIDATION_REPORT.md

Phase 0 R2 定点修复与复验的验证报告。生成时间 2026-11-09T10:19:42.024215+00:00，来自 sealed 运行（mode=sealed）结果数据，不手工填写任何数字。

**结论状态。** Phase 0 R2定点修复完成，待验收

本轮不宣布 Phase 0 最终验收通过。

## 范围与方法

依据 A 至 G 复审证据回传逐项修复后，由 scripts/validate_r2.py 以 --sealed 模式执行全部必查项。检查结果写入 VALIDATION_RESULTS.json，本报告与分组表全部从同一份结果数据生成。

检查总数 50，PASS 48，FAIL 0，ERROR 0，SKIP 2，必查失败 0，退出码 rc=0。

## 自动检查结果

按组统计。

| 组 | PASS | FAIL | ERROR | SKIP |
| --- | --- | --- | --- | --- |
| boundary | 7 | 0 | 0 | 0 |
| checksums | 1 | 0 | 0 | 2 |
| csv | 13 | 0 | 0 | 0 |
| fixes | 12 | 0 | 0 | 0 |
| inputs | 5 | 0 | 0 | 0 |
| man | 4 | 0 | 0 | 0 |
| req | 4 | 0 | 0 | 0 |
| src | 1 | 0 | 0 | 0 |
| sub | 1 | 0 | 0 | 0 |

跳过的检查及其策略原因。

    checksums/fc-02: every listed hash matches disk (checksum verification not requested)
    checksums/fc-03: checksum file excludes itself (checksum verification not requested)

## A 至 G 逐项关闭

| 缺陷项 | 修复位置 | 对应检查 | sealed 状态 |
| --- | --- | --- | --- |
| A | 03 输入投递行与新增输出收集行。 | a-01,a-02 | 全部 PASS |
| B | 06 外部服务与 GUI 统计合入，历史口径加标。 | a-03,b-01,b-02,b-03 | 全部 PASS |
| C | 09 与 04 的系统归属改为逐任务聚合。 | c-01,c-02,c-03 | 全部 PASS |
| D | 20_build_04_05.py 与 04 的 unknown 风险通道。 | d-01,d-02,d-03 | 全部 PASS |
| E | 21_build_08.py 与 08 的任务名与字节按 census 关联。 | c08-e-other,c08-e-social,c04-e-attrib,c08-sizes | 全部 PASS |
| F | validate_r2.py 验证器与 30_checker.py 子进程执行。 | in-01,in-02,in-03,in-04,in-05,c04-rows,c04-cols,c04-ids,c04-vocab,c04-census,c05-total,c05-domains,chk-01 | 全部 PASS |
| G | 来源哈希固定、清单预绑定与封存清单。 | src-01,m-01,m-02,m-03,m-04,fc-01,fc-02,fc-03,e-01,e-02,e-03,e-04 | fc-02=SKIP fc-03=SKIP |

## 反例测试结果

8 个注入用例全部 TRIGGERED，即每个缺陷都触发了对应检查失败。

| 用例 | 注入内容 | 期望触发检查 | 实际 rc | 额外未通过检查 |
| --- | --- | --- | --- | --- |
| c01 | inputs traversal error (chmod-000 subdir, mock inputs) | in-01,in-02,in-03 | rc=1 | bd-05,in-04,in-05 |
| c02 | 04 one data row removed (122 -> 121) | c04-rows | rc=1 | b-03,c-02,c04-census,c04-ids,c05-domains,c08-official,chk-01 |
| c03 | evidence/source_hashes_round1_r1.tsv deleted | src-01,e-02 | rc=1 | 无 |
| c04 | sealed mode with wrong sha256 for 03 in manifest | m-02 | rc=1 | 无 |
| c05 | unknown-gui row forced to bare low cells | d-01,d-02 | rc=1 | 无 |
| c06 | staged-local odoo OS cells swapped to Linux | c-02,chk-01 | rc=1 | c04-census |
| c07 | 08 other row name<->bytes swapped back | c08-e-other | rc=1 | 无 |
| c08 | 06 merge placeholder line restored | a-03 | rc=1 | 无 |

## 越界写入审计

边界检查组 bd-01 至 bd-07 覆盖第一轮目录、R1 目录、.audit、原始汇总报告、工作区晚于本轮回放起点的文件、三个 Git 仓库 head 与工作区状态、ale-data 文件计数与已登记用户增量。全部状态取自结果数据。

    PASS bd-01: late=0
    PASS bd-02: late=0
    PASS bd-03: late=0
    PASS bd-04: late=0
    PASS bd-05: late=0
    PASS bd-06: heads=['2e91edd3cd26baa35a38127c90c8e5241dfbe62f', '73517c2eb097abe7974e9ec4de9819a02cd0ee81', '492249a2ca4b9d74efd3584a90399473c2e928c7'] dirty-sets=[[], [], ['?? .DS_Store', '?? tasks/.DS_Store', '?? tasks/demo/.DS_Store', '?? tasks/example_task.zip', '?? tasks/example_task/.DS_Store']] rc=[0, 0, 0, 0, 0, 0]
    PASS bd-07: regular=79076 links=3 present=6/6 nondot-exact=0/0 missing=none

封存前对工作区做了一次独立 find 扫描，输出存于 evidence/boundary_final_audit.txt，末尾内容。

    
    - 18:12 与 18:13 期间发现：用户在 Finder 中浏览 ale-data，先后重写 task-data-v1.1/.DS_Store
      与 ale-data/.DS_Store，并已移除 17 时创建的 legal.zip。
    - 本执行器对此无任何写入；18:17 测算 ale-data 非 .DS_Store 常规文件 = 79,070，与原始基线相等。
    - bd-07 断言设计升级为 v2（见 evidence/boundary_event_r2_note.md）：
      .DS_Store 登记行断言存在性与总数，内容增量行断言字节精确。

## 封存记录

SOURCE_MANIFEST_R2.json 两阶段生成。pre 阶段绑定 11 个输出文件、168 个证据文件、9 个脚本文件，记录时点 pre=2026-11-09T17:42:44+08:00。final 阶段在 sealed 运行与本报告生成之后重建，覆盖全部交付物，其哈希与时点以清单自身内容为准。

封存完成后 FINAL_CHECKSUMS.sha256 覆盖树内全部普通文件（排除清单自身），随后以 --verify-checksums 只读复验，复验退出码与总览在聊天回传中报告，封存后不再改动树内任何文件。

## 剩余 UNKNOWN 与 NOT_RUN

剩余 UNKNOWN 维持第一轮与 R1 复审后的结论，本轮不强行收口。
- humanoid_wbc_policy_evaluation 的任务卡无 vm.timeout，time_limit_sec 与 time_source 为 UNKNOWN。
- 9 个 GUI unknown 任务的 GUI 必要性待复核。
- computing_math 官方类目描述不在输入内，CS 排除是项目口径过滤器。
- 历史 153 与 152 数字在输入内未找到出处。
- 部分任务的 hook 评分入口不可静态可见。
- Windows 首期是否纳入、GPU 预算、正式配额属项目负责人决策项。
- 04 的 run_state_current 全部保持 NOT_RUN，属于冻结事实。

## 结论

A 至 G 七项缺陷的修复文件、生成脚本、验证器与反例测试全部就位，sealed 校验 通过（PASS 48 FAIL 0 ERROR 0）。结论状态。

**Phase 0 R2定点修复完成，待验收。**

本轮不更新总方案，不决定 Windows/GPU 预算或正式配额，不宣布 Phase 0 最终通过。
