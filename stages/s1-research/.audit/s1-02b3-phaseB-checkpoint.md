# S1-02B3 Phase B checkpoint — 脚本合同冻结

Run: s1-02b3 · Date: 2026-11-10 · Zone: Asia/Taipei · Trail: `.audit/s1-02b3.tsv`

本文记录 scripts/28–33 的合同内容与自测结果。本轮不启动研究子代理、不生成候选、不产出六个 S1-02B3 交付文件。

## 1. 脚本清单

| # | 文件 | 职责 | 自测结果 |
|---|---|---|---|
| 28 | scripts/28_b3_precheck.py | phase0-final 基线登记与哈希检查、S1-01 映射检查、B2-effective 读取检查、B3 目标域子域检查、冻结输入只读检查 | 13 组 probe 全绿，exit 0 |
| 29 | scripts/29_b3_scope_matrix.py | 从 S1-01 生成 9 官方子域范围矩阵；不手猜编号；不覆盖 A/B1/B2 | 12 组 probe 全绿，exit 0 |
| 30 | scripts/30_check_fragment_b3.py | 三研究片段字段合同；证据等级/source_support_mode/software_adaptation/Linux 状态；伦理版权授权风险字段；候选粒度与禁止凑数 | 25 组 flip 全绿，exit 0 |
| 31 | scripts/31_merge_b3.py | 合并三片段生成 B3 候选与来源主张映射；candidate_id 唯一；不覆盖历史成果 | 9 组 probe 全绿，exit 0 |
| 32 | scripts/32_validate_b3.py | 校验 B3 交付物；与 A/B1/B2-effective id 零冲突；scope 矩阵与候选数一致；来源映射/证据范围/Linux 状态/负例 | 16 组 flip + 3 组 clean 探测全绿，exit 0 |
| 33 | scripts/33_b3_overlap.py | B3 内部跨子域重复；B3 与 A/B1/B2-effective 重复；输出机器扫描；不裁夺 | 9 组 probe 全绿，exit 0 |

全部自测运行于本机，六脚本 `--selftest` 均 exit 0。28 的 `--record` 与默认 verify 模式两次运行 gates failed=0。

## 2. 每脚本的输入、输出、冻结边界

### 28_b3_precheck.py

- 输入: `--phase0-final` 指定的 phase0-final 目录（默认 `/Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108/analysis/phase0-final`，参数缺省时从 `.audit/s1-02b3-phase0-final-register.md` 正则解析）；`S1_01_CATEGORY_MAPPING.csv`；`S1_02B2_EFFECTIVE_CANDIDATES.csv`；33 个 project 侧冻结件。
- 门: G1 phase0 65 条校验和逐一重哈希 + 4 top 文件存在；G2 register 一致性；G3 S1-01 9 子域（id/code/name 逐字）+ 3 域确认；G4 B2-effective 39 行且 source_support_mode 合法；G5 6 个 B3 交付物不存在（`--post` 跳过）；G6 manifest 记录/重哈希。
- 输出: 仅 `--record` 时写 `.audit/s1-02b3-frozen-manifest.json`（37 文件 sha256+size，拒绝覆盖）。
- 冻结边界: 不写任何冻结文件；只读 A/B1/B2/B2-effective/S1-01/phase0-final。

### 29_b3_scope_matrix.py

- 输入: S1_01_CATEGORY_MAPPING.csv（9 目标行）；evidence/task_archetype_rows.tsv（生成 official_example_task_ids）；evidence/s1_02b3_research/<stem>_candidates.csv 行数。
- 输出: S1_02B3_SCOPE_MATRIX.csv（15 列，batch 列名 `s1_02b3_batch`=batch_3；refuse-overwrite）。
- 冻结边界: 只读 S1-01 与 archetype 表；不覆盖任何历史矩阵。

### 30_check_fragment_b3.py

- 输入: evidence/s1_02b3_research/<stem>_candidates.csv + 同名 <stem>.json 侧车。
- 输出: 无写盘（stdout 报 OK/FAIL；exit 0/1）。被 31 以 importlib 复用的合同叶子。
- 冻结边界: 不写任何文件；不调用研究模型。

### 31_merge_b3.py

- 输入: 三个片段 CSV + 三个 JSON 侧车；内部再过 30 的全部门。
- 输出: S1_02B3_WORKFLOW_CANDIDATES.csv（43 列 EFFECTIVE 语义形状）+ S1_02B3_SOURCE_CLAIM_MAP.csv（10 列）；refuse-overwrite；7 个派生列由合并统一填充（linux 全 NOT_VERIFIED、expert 仅 EPP、eng 三态短语、fragment_path=stem、duplicate_status=none、home/tag 空）。
- 冻结边界: 不接触 6 个 B3 交付物之外的历史文件；不覆盖历史成果。

### 32_validate_b3.py

- 输入: 6 个 B3 交付物 + A(51)/B1(57)/B2-effective(39) + `.audit/s1-02b3-frozen-manifest.json` + evidence/s1_02b2_research/b1_open_review_items.md。
- 门: V1-V14（V1 id 唯一形态；V2 恰 9 子域各≥1；V3 linux 全 NOT_VERIFIED；V4 E4 三向一致；V5 eng 旗标短语；V6 claim map 1:1；V7 伦理 4 列；V8 dup_status 三值+行归因；V9 dup 文件结构；V10 与 A/B1/B2E 零碰撞+ghost；V11 scope 矩阵 9 行+名+batch_3+counts==合并；V12 manifest 重哈希；V13 B1 五条逐字在两 MD+review 结构+overlap 5 分组标题；V14 行级证据语义门）。
- 输出: 无写盘；stdout 逐门 OK/FAIL；exit 0 iff 全绿。
- 冻结边界: 只读一切；不改冻结件。

### 33_b3_overlap.py

- 输入: S1_02B3_WORKFLOW_CANDIDATES.csv + A + B1 + B2-effective。
- 输出: `.audit/b3_overlap_sweep.csv`（9 列，refuse-overwrite）；标题分词 Jaccard≥0.35 三组配对 + B3 内部跨子域。
- 冻结边界: 只读；仅写 .audit 证据。不裁夺。

## 3. 预计正项

- 28: 6/6 门 OK；record 写 manifest；verify 重哈希一致。
- 29: 9 行矩阵；无手工编号；9 子域名与 S1-01 逐字一致。
- 30: 43 列头逐字；每子域 1–5 行；枚举/伦理/URL/E 级配对全过。
- 31: 43+10 列输出；id 全唯一；行序 = subdomain_id 序 + id 序。
- 32: V1-V14 全 OK；exit 0。
- 33: sweep 写入 .audit；标记对数打印；exit 0。

## 4. 预计负例（逐项恰翻转自己的门）

- 28: G1 错哈希 / G2 register 漂移 / G3 名字漂移 / G4 mode 非法 / G5 交付物已存在 / G6 manifest 漂移。
- 29: 缺行 / 名字漂移 / refuse-overwrite。
- 30: 头漂移 / count 超上限或低于地板无说明 / id 形态 / 枚举 / E2 / E4 配对 / P5 / 伦理空 / 派生列非空 / URL 非法 / evidence 语义门 / family / incident。
- 31: 非法片段 id 归错簇 / 侧车 count 不符 / derived 派生词条。
- 32: v1-dup+v1-form / v2-missing / v3-linux / v4-e4 / v5-eng / v6-sc / v7-ethics / v8-dup / v9-dup / v10-collide / v11-scope / v12-drift / v13-item+v13-header / v14-mode+v14-scope。
- 33: 低于阈值不标记 / 同子域内部跳过 / refuse-overwrite。

## 5. B3 研究片段字段合同

- CSV: 43 列 = FRAG_COLS 32（与 B2 完全一致）+ 7 派生（linux_verification_state/expert_pending/engineering_pending/fragment_path/duplicate_status/primary_home/secondary_tag，片段内必须为空）+ 4 证据列（source_support_mode/evidence_scope/workflow_family_id/process_incident）。
- 侧车 JSON: 顶层仅 `{"subdomains": [{"subdomain_code", "candidate_count", "coverage_notes"}]}`；code 集合与片段簇完全一致；count 与 CSV 实数一致；coverage_notes 解释低于 3 的原因。
- 枚举: evidence_kind 4/evidence_level E1,E3,E4/source_type 2/software_adaptation 5/source_support_mode 8。
- 语义门: recorded_full_support 只配 as_recorded；verified_E1⇔verified_support；recorded_partial_support 禁 verified/conditional；family=^fc_[a-z0-9_]+(,...)*$；incident=^(none|inc:[^;]{1,120})$。
- 九子域 slug: animation_3d=vm_anim, graphic_design=vm_gra, audio_music=vm_aud, aviation=ts_avi, maritime_port=ts_mar, fire_safety=ts_fir, educational_technology=edu_edt, library_info=edu_lib, translation=edu_trn；id=slug+_wfNN。
- 三片段: vm_cluster（3 子域）、ts_cluster（3 子域）、edu_cluster（3 子域），位于 evidence/s1_02b3_research/。

## 6. phase0-final 版本标识与 65 项校验结果

- 目录: `/Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108/analysis/phase0-final`（唯一有效基线；只读姿态，不写不改）。
- 版本标识: SOURCE_MANIFEST_FINAL.json — phase "phase0-final", stage "final", lifecycle "closed", created_at 2026-11-10T10:59:28+08:00, amendment=closeout。
- FINAL_CHECKSUMS.sha256: 65 条，本轮 28 G1 全量重哈希 65/65 通过（exit 0）；`.audit/s1-02b3-frozen-manifest.json` 收录 4 个 top 文件（FINAL_CHECKSUMS.sha256、FINAL_VALIDATION_REPORT.md、PHASE0_FINAL_REPORT.md、SOURCE_MANIFEST_FINAL.json）。

## 7. B2-effective 读取哈希

- S1_02B2_EFFECTIVE_CANDIDATES.csv sha256 = `eb99cdb41962bc120aa16c77641c6fc457195b6b1dd52f0145efc2854be05e3f`。
- evidence/s1_02b2_research/b1_open_review_items.md sha256 = `fcd941ee9ea76490ed9d77a0dae375795fcbf6d4fa55fc0328f4a11165acfb3b`。
- SHA-1: nil（未使用 git；工作区非 git 仓）。

## 8. 尚未解决的 UNKNOWN

1. 总方案 v0.4 在工作区不存在（grep 方案|总 为空）；冻结义务以缺席满足，登记 UNKNOWN。
2. source_support_mode=verified_support 在 B2-effective 语料中无实例；B3 合同允许该值，若出现将作为 B3 新先例。
3. B2-effective 存在 1 行 workflow_family_id 为空串（B2 缺口）；B3 片段层强制非空。
4. phase0 报告中 9 条 GUI unknown 保持 UNKNOWN 口径（不推断）。
5. 轨迹已修复段落: 2026-11-10T17:22 的三行因缺尾换行与多行单元格损坏，已按规则追加 supersede 行 + 三条正式版本；被 supersede 的行保留不改。