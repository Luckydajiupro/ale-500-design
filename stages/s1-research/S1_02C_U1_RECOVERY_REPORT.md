# S1-02C-U1 Recovery 报告

状态：修复完成，等待独立评审。不进入配额分配、专家人数计算、专家招募、S1-02C后续扩展或平台开发。
记录时间：2026-11-11

## 1. 任务目标

以当前磁盘文件为准，恢复 S1-02C-U1 交付的真实状态。此前聊天回报、ZIP 名称与摘要文档均不作数。唯一有效基线是 Phase 0 final。

## 2. 诊断（只读，先不改）

`.audit/s1-02c-u1-recovery-diagnosis.md` 记录了完整诊断。核心事实：

- assignment 实际 174 行，但 uncovered_official_flag=yes 只有 9 条（B3 三域各 3），A 三域 13 条全部为 no。
- scripts/36_validate_s1_02c_c16.py 不存在。
- .audit/s1-02c-uncovered-correction.md、.audit/s1-02c-fingerprints.txt、.audit/val36-final.out、.audit/selftest36-final.out 全部不存在。
- registry 与 matrix 的 uncovered_official_count 合计均为 9，与 assignment 一致。
- S1_02C_REVIEW_SUMMARY.md 声称 22 条，与磁盘矛盾。摘要描述的 U1 修正从未落盘。
- 35_validate_s1_02c.py 与 C13 基线存在；当时 35 的 C10 断言 uncovered=9（B3）。

## 3. 修正

依据 S1_01_CATEGORY_MAPPING.csv 的 coverage_status，按 subdomain_code 逐条回填：

- coverage_status=uncovered_official 的子领域置 yes，其余置 no，并写入对应的 uncovered_official_basis。
- A 新增 chemical_process 3 条、mining_petroleum 5 条、precision_agriculture 5 条。
- B3 保持 9 条。
- 最终 22 条 yes。
- 未修改 A/B1/B2/B3 历史候选文件（修正脚本读写前后逐文件字节比对通过）。
- 未把 A 新增 13 条自动标记为 padding_risk。padding 仍 27 条全在 B3。

保持不变：

- assignment 174 条
- workflow family 72
- expert capability groups 50
- authorization risk groups 9
- engineering risk groups 7
- padding_risk 27 条（high 9）
- Linux NOT_VERIFIED 174 条
- expert_pending 9 条（A）
- C13 基线 61 条，不包含自身，61/61 hash-match

## 4. C16 校验器

新建 scripts/36_validate_s1_02c_c16.py，16 项检查。C16 为逐条等式检查 assignment.uncovered_official_flag 与 S1_01_CATEGORY_MAPPING.csv coverage_status 的一致性，且 uncovered_official_basis 与 flag 对应。

C16 自测 11 个负例全部捕获：

1. A 候选 yes 改 no
2. B3 候选 yes 改 no
3. 非 uncovered 子域改 yes
4. 删除一个 assignment 行
5. 改变 registry 的 uncovered_official_count
6. 改变 matrix 的 uncovered_official_count
7. 改变 stats 中的总数
8. 修改历史文件哈希
9. 把 C13 清单自身加入清单
10. 修改已有任务族或能力组数量
11. 修改 padding_risk 数量

保留原 scripts/35_validate_s1_02c.py。仅修订其 C10 的 uncovered 断言从 9（B3）改为 22（A 13 + B3 9），修订记录写在脚本头部与 C10 常量处。C16 逻辑未写入 35。

## 5. 验证结果

python3 scripts/35_validate_s1_02c.py：15 checks，0 failed，exit 0。
python3 scripts/35_validate_s1_02c.py --self-test：10 mutations caught，pristine control green，exit 0。
python3 scripts/36_validate_s1_02c_c16.py：C01–C16 16 checks，0 failed，exit 0，C13 61/61 hash-match。
python3 scripts/36_validate_s1_02c_c16.py --self-test：11 mutations caught，pristine control green，exit 0。

物理检查：

- assignment rows=174，uncovered_yes=22
- chemical_process 3/3 yes
- mining_petroleum 5/5 yes
- precision_agriculture 5/5 yes
- aviation 3/3 yes
- maritime_port 3/3 yes
- educational_technology 3/3 yes
- registry uncovered_official_count 合计 22
- matrix uncovered_official_count 合计 22
- scripts/36_validate_s1_02c_c16.py 存在
- .audit/s1-02c-uncovered-correction.md 存在
- .audit/s1-02c-fingerprints.txt 存在
- .audit/val36-final.out 存在
- .audit/selftest36-final.out 存在

## 6. 交付物

- .audit/s1-02c-u1-recovery-diagnosis.md
- .audit/s1-02c-uncovered-correction.md
- .audit/s1-02c-fingerprints.txt
- .audit/val36-final.out
- .audit/selftest36-final.out
- scripts/36_validate_s1_02c_c16.py
- scripts/36_fix_s1_02c_u1.py（修正脚本，可重复执行且幂等）
- S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv（回填后 22 条 yes）
- S1_02C_WORKFLOW_FAMILY_REGISTRY.csv（uncovered 合计 22）
- S1_02C_EXPERT_CAPABILITY_MATRIX.csv（uncovered 合计 22）
- .audit/s1-02c-stats.json（uncovered_official 22，families_with_uncovered 8 个族）
- S1_02C_REVIEW_SUMMARY.md（改为与磁盘一致，删除别名回映射与调度披露两处失实表述）
- scripts/35_validate_s1_02c.py（仅 C10 断言修订，附修订记录）

## 7. 停止状态

修复已完成并全部落盘。等待独立评审。不启动配额分配、专家人数计算、专家招募、S1-02C后续扩展或平台开发。