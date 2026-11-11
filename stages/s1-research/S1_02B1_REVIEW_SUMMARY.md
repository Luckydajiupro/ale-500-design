# S1-02B1 评审摘要

阶段：S1-02B1，研究范围物理科学 4 + 生命科学 4 + 健康医学 5 共 13 个子领域。
性质：独立交付与验证证据，不修改 S1-01 / S1-02A 任何成果。
截止状态：**等待独立评审。** 本阶段不自动开始 B2。

## 本轮状态汇总

| 维度 | 状态 | 依据 |
| --- | --- | --- |
| B0 旧阶段成果只读重校验 | PASS | `scripts/14_validate_effective_view.py` 复跑 exit 0（C1–C7 + 7 负例全过） |
| B1 基线一致性检查 | PASS | `scripts/15_b1_baseline_check.py` exit 0，B0–B4 全过；HEC-RAS 冲突已录报告不改文件 |
| B2 目标子领域映射完整 | PASS | 13/13 子领域在 S1-01 映射存在 |
| B3 HEC-RAS 事实差异 | REPORT-ONLY | A 文本 vs 评审核实事实：classic 行表述有出入，以评审核实为准记录，见 `S1_02B1_BASELINE_CONSISTENCY_REPORT.md` |
| 研究覆盖 | PASS | 57 条候选，13 子领域每条 ≥3；无配额（目标密度为研究工作密度） |
| 来源—主张证据 | PASS | 57/57 行有主来源 URL + primary_claim；不存在把工具存在当工作流证据的行（tool_existence=0） |
| 来源 URL 核验 | PARTIAL-UNKNOWN | phys 13/16、med_a 10/10、med_b 9/13（CDC 拦截已被独立 web_fetch 证实为机器人封锁）、life 16/18（IUCr 同理）HTTP 200；所有非 200 均已披露并按缺口标记 |
| 医疗/生命模块伦理 | PASS | life/med 41 行 4 个伦理字段全部非空且带来源；禁用合规缺口（EGA/dbGaP、UniProt 许可、ISO 付费墙等）全部在 pending_confirmation 披露 |
| 跨领域重复检查 | PASS | 0 实质性重复；5 相邻对全部否决重复并留有差异依据，见 `S1_02B1_DUPLICATE_ATTRIBUTION.md` |
| Linux 运行验证 | UNKNOWN（按设计） | 57/57 NOT_VERIFIED：本阶段没有在服务器上运行任何工具（不与权限边界冲突，后续报告含义不变） |
| 验证器 | PASS | `scripts/17_validate_b1.py` exit 0，V1–V10 + 9 负例全部翻转 |
| 决策留痕 | PASS | 决策追踪表 `.audit/s1-02b1.tsv` 覆盖起始行到 U10 全过程 |
| 内部审计（Phase D） | PASS (APPROVE, 同路由回退) | 独立审计代理复跑两道闸门（exit 0），重算全部统计数字并独立重做去重扫描：无伪造、无矛盾；唯一 FAIL 点为一处标注错误（ESMO/Elsevier 全文机构访问限制被误标为 403），已修正 |

**总体状态：PASS with UNKNOWNs — 等待独立评审，不自动开始 B2。**

## 独立评审需要确认的条目

1. HEC-RAS classic 线 Linux 引擎的表述差异只在报告层面记录，是否需要在后续阶段「回写修订」S1-02A 有效视图（本阶段按规则未动）。
2. 全部 Linux 运行验证均未执行（57/57 NOT_VERIFIED），评审是否接受其为 B1 交付状态。
3. 5 个跨领域相邻对全部否决重复的裁定（E4 级）需要专家背书。
4. E3 证据链中的付费墙/受限披露缺口（ISO、EGA/dbGaP、ESMO/Elsevier 全文机构访问限制、TransCelerate 403 等）是否满足验收标准。
5. 伦理字段均由来源推演得出，而未经过机构伦理委员会复核（本阶段不在授权范围内）。

## 非目标（本阶段明确不做）

不制定正式配额、不计算招聘人数、不招募、不开发平台、不启动批量工程评测。B2 是否启动由独立评审决定。