# S1-02C 基线清单缺陷与修复记录

记录时间：2026-11-10T21:58:48+08:00
范围：仅涉及 .audit/s1-02c-baseline.sha256 及其校验脚本，不涉及历史候选文件或七份交付物。

## 1. 原始缺陷

2026-11-10T20:14:16+08:00 生成基线清单时，命令把 shasum 输出重定向到 .audit/s1-02c-baseline.sha256，而该文件同时又被 shasum 枚举。结果清单有 62 行，其中一行记录清单自身的 sha256。

该行 recorded 为 02a83246f7ce...，实际为 540490a959d4...；recorded 等于前 16 行内容的 sha256，说明写入时文件只写到了第 16 行。一个文件不可能携带自身的 sha256，这一行不可满足。

## 2. 修复

2026-11-10T21:14:22+08:00 完成以下修复：

- 原 62 行清单完整保留为 .audit/s1-02c-baseline.sha256.as-taken；
- 仅删除自哈希行，当前清单为 61 行；
- 逐条复验 61 条，全部与磁盘一致，0 不匹配。

未修改任何被清单覆盖的历史文件。

## 3. 校验器修正

首次运行 C13 失败，消息为 manifest hashes itself。修复清单后重跑，C13 仍失败，消息为 manifest lists 61 entries, expected 62。原因是 C13 把修复前观察到的 62 行当成了期望值，而 62 行包含自哈希行，不是正确的历史文件数。

修正内容：期望值改为 61，并在消息中说明 61 是 62 行原件减去自哈希行后的历史文件数；保留“清单不得包含自身”的判定；保留逐条 sha256 比对；未删除任何检查项。修正后 C13 通过，61/61 entries hash-match，0 unsatisfiable。自测的 10 个变异全部被捕获，pristine control 为 15/15。

## 4. 最终校验

运行时间：2026-11-10T21:46:48+08:00（校验器日志）
记录时间：2026-11-10T21:58:48+08:00
命令：python3 scripts/35_validate_s1_02c.py
结果：15 checks, 0 failed, exit 0

自测命令：python3 scripts/35_validate_s1_02c.py --self-test
自测结果：10 mutations caught, pristine control green, exit 0

## 5. 交付物指纹（sha256）

以下五个值于 2026-11-10T20:54 计算。此后未重新运行构建脚本，CSV 内容未变。

| 文件 | sha256 |
| --- | --- |
| S1_02C_WORKFLOW_FAMILY_REGISTRY.csv | a61ab67703d948c7788ffa31845476ca0960bb26b6c31b6e81d7f025e51a362e |
| S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv | 6241e1d444aedf3969cd5bb7cc924d68274c2eb9d6d4f7ad0b4c29f59ec099b7 |
| S1_02C_EXPERT_CAPABILITY_MATRIX.csv | e9aa57a0adf5e9331c84911f7fbb6323aaa7221859227b815041fb20ac822661 |
| S1_02C_AUTHORIZATION_RISK_REGISTER.csv | e017809dec35233c3a015dd7764ce0195e1f413a2b17a050ba81490d18be2c62 |
| S1_02C_ENGINEERING_RISK_REGISTER.csv | c1d7a9898fc40d79e70529d3eaea11e1258c25fca30c4b9a57b0165ed949326e |
