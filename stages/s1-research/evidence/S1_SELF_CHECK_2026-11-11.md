# 阶段一自检记录

日期 2026-11-11。范围是阶段一收口包，依据是 `STAGE.md` 的速查表、`S1_PHASE1_HANDOFF_CHECKLIST.csv` 和两个校验器。性质是项目负责人自检，不是独立复审。

## 结论

自检通过。两个校验器 31 项检查全过，两套负例自检分别抓到 10 个和 13 个注入错误。关键数字与 CSV 一致，没有发现需要改阶段一证据的缺陷。签字后阶段一进入“已收口”。

## 命令与结果

| 检查 | 命令 | 结果 |
|---|---|---|
| 结构校验 35 | `python3 -B scripts/35_validate_s1_02c.py` | 15 项，0 失败，退出码 0 |
| 结构校验 36 | `python3 -B scripts/36_validate_s1_02c_c16.py` | 16 项，0 失败，退出码 0 |
| 负例自检 35 | `python3 -B scripts/35_validate_s1_02c.py --self-test` | 10 个注入错误全部抓到，对照组通过 |
| 负例自检 36 | `python3 -B scripts/36_validate_s1_02c_c16.py --self-test` | 13 个注入错误全部抓到，对照组通过 |
| 文档规则 | `python3 tools/check_docs.py` | 12 份文档，0 失败 |
| 数字规则 | `python3 tools/check_numbers.py` | 23 条数字，0 失败 |

## 关键数字

| 项 | 自检值 | 核对方式 |
|---|---|---|
| 官方子域 | 55，49 有活动任务，6 空 | `S1_01_CATEGORY_MAPPING.csv` 55 行，`active_observed` 49，`uncovered_official` 6 |
| 候选 | 174，A 51、B1 57、B2 39、B3 27 | 归属表 174 行，按 `source_batch` 计数 |
| 任务族 | 72，单成员 15 | 族登记表 72 行，`total_distinct_candidates=1` 15 行 |
| 专家能力组 | 50，中位 3，最小 1，最大 8 | 能力矩阵 50 行，`primary_candidate_count` 统计 |
| 授权风险组 | 9 | 授权风险登记 9 行 |
| 工程风险组 | 7，ENG-01 覆盖 174 | 工程风险登记 7 行，ENG-01 `candidate_count=174` |
| 重复对照 | 25 组，实质重复 3、非重复 22 | 四份对照表 `substantively_duplicate` 计数；归属表 25 个 `DP-*` 编号 |
| 未进入对照 | 129 | 归属表 `duplicate_attribution_role=none` 129 行 |
| 证据等级 | E1 83、E3 87、E4 4 | 归属表 `evidence_level` 计数 |
| 独立验证 | 0 条 | `independent_verification_present=no` 174 行 |
| Linux 运行 | 0 条已验证 | `linux_verification_state=NOT_VERIFIED` 174 行，`linux_not_verified_flag=yes` 174 行 |
| 待办工程项 | 83，A 21、B1 25、B2 15、B3 22 | `engineering_pending_flag=yes` 计数 |
| 空覆盖子域候选 | 22，A 13、B3 9 | `uncovered_official_flag=yes` 计数 |
| 凑数风险 | 27，高 9、中 18，全在 B3 | `padding_risk_flag=yes` 计数 |
| 需专家背书 | 45 | `expert_endorsement_required=yes` 计数 |
| 专家待确认 | 9，全在 A | `expert_pending` 以 `YES` 开头的行，按批次计数 |
| 交接清单 | 53 项，已确认 36、开放 9、有条件 4、未知 2、未开始 2；阻塞 1 | `S1_PHASE1_HANDOFF_CHECKLIST.csv` 状态计数 |

## 阶段 0 依赖

`stages/s0-baseline/04_task_inventory.csv` 自检值如下。122 条任务，13 个域，computing_math 排除 19 条，非 CS 103 条。Linux 71 条，Windows 32 条。GUI 为 yes 40、no 73、unknown 9。外部服务为 staged-local 5、online-required 6、public-ref 2。运行状态全部 NOT_RUN。3 条 GPU 任务来自 `selected_tasks/gpu.txt`，在清单里全部 `os_windows=yes`。

## 文件计数口径

根目录有 52 份研究文件和 `STAGE.md`，共 53 个文件。前缀分组为 7、10、7、8、6、12、2。`scripts/` 有 40 个 `.py` 脚本和 1 个 `README.md`，共 41 个文件。速查表里的“52 个文件”和“40 个脚本”分别指研究文件和 `.py` 脚本。

## 限制

自检不是独立复审。阶段一证据没有第二个人独立复核，这个风险已写在 `docs/03-quality-and-acceptance.md` 和 `docs/04-roles-and-decisions.md`。25 组重复对照只覆盖已对照候选对，129 条候选从未进入对照。B3 时间线是事后补记，历史顺序无法复原。174 条候选全部未做运行验证。

## 签字

项目负责人签字：项目负责人（电子签字）

日期：2026-11-11

签署方式：项目负责人在会话内授权，按自检记录签字。

签字即表示已按速查表抽验，接受阶段一包为“自检通过”，不把它表述为“独立复审通过”。
