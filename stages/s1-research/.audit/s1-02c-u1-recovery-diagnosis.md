# S1-02C-C16 U1 恢复诊断（只读）

记录时间：2026-11-10T23:40+08:00
性质：只读诊断，未修改任何交付物。依据是当前工作目录磁盘上的实际文件。

## 1. 触发背景

S1-02C-U1 摘要 `S1_02C_REVIEW_SUMMARY.md` 声称完成一轮 uncovered_official 传播修正，把 yes 从 B3 单批 9 条传播为全域 22 条，并声称产出 C16 校验器 `scripts/36_validate_s1_02c_c16.py` 以及四个审计产物。独立复核怀疑摘要与磁盘不一致，要求以磁盘为准。

## 2. 磁盘实测

### 2.1 assignment 与子领域标记

| 项 | 摘要声称 | 磁盘实测 |
|---|---|---|
| assignment 行数 | 174 | 174 |
| 校验器35 C10 断言 | 9（B3） | 通过（一致） |
| uncovered_official_flag=yes | 22 | 9 |
| chemical_process yes/总数 | 3/3 | 0/3 |
| mining_petroleum yes/总数 | 5/5 | 0/5 |
| precision_agriculture yes/总数 | 5/5 | 0/5 |
| aviation yes/总数 | 3/3 | 3/3 |
| maritime_port yes/总数 | 3/3 | 3/3 |
| educational_technology yes/总数 | 3/3 | 3/3 |

### 2.2 摘要声称内容 vs 磁盘

| 摘要声称 | 磁盘实测 |
|---|---|
| C16 校验器存在 | 不存在，`scripts/36_validate_s1_02c_c16.py` 缺失 |
| 校验器36 16 checks 0 failed | 无法运行，脚本不存在 |
| 自测36 11 mutations caught | 无法运行，脚本不存在 |
| 审计文件 .audit/s1-02c-uncovered-correction.md | 不存在 |
| 审计文件 .audit/s1-02c-fingerprints.txt | 不存在 |
| 审计文件 .audit/val36-final.out | 不存在 |
| 审计文件 .audit/selftest36-final.out | 不存在 |
| 摘要第 3 行声称 U1 修正替代 21:58 版并传播 22 条 | 否，磁盘日期 22:37，字段仍为 9 |

结论：摘要中的 U1 修正从未在磁盘上成立，C16 与四个审计产物从未落盘。

### 2.3 校验器35 交叉验证（在未改任何文件情况下运行）

运行 `python3 scripts/35_validate_s1_02c.py` 得到 15 checks 0 failed；C10 断言 uncovered_official 为 9（B3 单批），C13 61/61 hash-match。这证实当前磁盘状态自我一致地停留在“U1 之前”。校验器35 正是以 9 条为常数固化的旧断言。

### 2.4 修复判定的事实依据（S1_01_CATEGORY_MAPPING.csv）

`S1_01_CATEGORY_MAPPING.csv` 是唯一分类源。六个子领域 coverage_status 均为 `uncovered_official`：

| 子领域 | 官方行数 | coverage_status |
|---|---|---|
| chemical_process | 1 | uncovered_official |
| mining_petroleum | 1 | uncovered_official |
| precision_agriculture | 1 | uncovered_official |
| aviation | 1 | uncovered_official |
| maritime_port | 1 | uncovered_official |
| educational_technology | 1 | uncovered_official |

该文件在 61 条目冻结基线内（`./S1_01_CATEGORY_MAPPING.csv`），C13 本轮 61/61 匹配，故本节引用的分类为止点事实。

assignment 中这六个子领域的候选数为：chemical_process 3、mining_petroleum 5、precision_agriculture 5、aviation 3、maritime_port 3、educational_technology 3，合计 22。其中 B3 三域 9 条已标记 yes，A 三域 13 条（3+5+5）仍为 no 且 `uncovered_official_basis` 为空。

依据 34_build_s1_02c.py 与 35_validate_s1_02c.py 的共同契约，uncovered_official_flag 是源自 S1_01_CATEGORY_MAPPING.csv 每个子领域的 coverage_status 的缓存视图字段。字段的终态目标是逐 candidate 按其 subdomain_code 与 mapping 逐行一致。

## 3. 结论

磁盘上的 S1_02C 交付物停留在 U1 之前状态：assignment 9 条 yes。摘要声称的 22 条传播修正、C16 校验器、修正说明和验证日志均不存在或未落盘。该不一致是“文档声称已完成的修正从未写入磁盘”型的不一致，不是数据被篡改。

本诊断只读，未修改任何文件。修复遵循用户给定的修正条件：按 S1_01_CATEGORY_MAPPING.csv coverage_status 逐条回填 uncovered_official_flag=yes/no 与对应的 uncovered_official_basis，不动 A/B1/B2/B3 历史候选文件，不动校验器35，另建 C16 校验器与审计产物。