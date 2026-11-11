# S1-02B3 Phase 0 基线登记（依据 2026-11-10 前置指令）

## 1 版本标识

- Phase 0 工作区无 git 仓库，无 tag/commit 可引用。
- 版本标识取 SOURCE_MANIFEST_FINAL.json：
  - phase: `phase0-final`
  - stage: `final`
  - created_at: `2026-11-10T10:59:28+08:00`
  - lifecycle: `closed`
  - hashed_at_pre: `2026-11-09T22:45:23+08:00`
  - hashed_at_post: `2026-11-10T10:53:43+08:00`
  - amendment: closeout（history 归档、来源链切至 Archives/ALE-Phase0-History-20261110）
- FINAL_VALIDATION_REPORT.md：41 项检查，PASS 40 / FAIL 0 / ERROR 0 / SKIP 1（fv-07 自身状态行，预期）；Status: Phase 0 CLOSED。

## 2 关键基线文件路径

- 基线目录：/Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108/analysis/phase0-final（只读使用）
- 冻结清单：analysis/phase0-final/FINAL_CHECKSUMS.sha256（65 条：12 最终文件 + 47 证据 + 4 脚本 + progress.log + SOURCE_MANIFEST_FINAL.json）
- 版本清单：analysis/phase0-final/SOURCE_MANIFEST_FINAL.json
- 总报告：analysis/phase0-final/PHASE0_FINAL_REPORT.md（176 行）
- 验收报告：analysis/phase0-final/FINAL_VALIDATION_REPORT.md
- 冻结输入快照：workspace_root/inputs-readonly/（dr-xr-xr-x）：
  - 01_agents-last-exam HEAD 2e91edd3cd26baa35a38127c90c8e5241dfbe62f
  - 02_ale HEAD 73517c2eb097abe7974e9ec4de9819a02cd0ee81
  - 03_ale-data 无 git（79,070 文件 86.15GiB）
  - 04_ale-tasks-base HEAD 492249a2ca4b9d74efd3584a90399473c2e928c7

## 3 SHA-256 校验结果

- 2026-11-10 本轮已执行 `sha256sum -c FINAL_CHECKSUMS.sha256`：65/65 OK，exit 0。
- 结论：phase0-final 磁盘内容与冻结清单一致，未改动。

## 4 本轮实际读取的 Phase 0 文件

- FINAL_VALIDATION_REPORT.md
- FINAL_CHECKSUMS.sha256
- SOURCE_MANIFEST_FINAL.json
- PHASE0_FINAL_REPORT.md（全部 176 行）
- progress.log（tail 30 行）
- 目录树（find 全量文件名清单，未打开其余文件）
- inputs-readonly/README_READ_ONLY.md 未读；inputs-readonly 文件内容未读（仅 SHA256SUMS 清单计入 FINAL_CHECKSUMS 校验）。

## 5 与当前研究目录的一致性核对（冲突登记）

- phase0-final 官方域目录计数：visual_media 11、transport_safety 2、education_info 2。
- 当前研究目录 S1_01_CATEGORY_MAPPING.csv 的对应子域行与本计数一致（8.x 合计 11、10.x 合计 2、11.x 合计 2）。
- 结论：未发现控制口径冲突。任何既有文档或历史摘要若与 phase0-final 不一致，一律按 UNKNOWN 登记，不修改历史研究成果。
- 后续本批中如再发现冲突，追加到本文件并以 UNKNOWN 记录。

## 6 执行声明

- 本批不再以 Phase 0 R1 草案作为控制依据。
- 不对 phase0-final 做任何写操作、覆盖、重生成或移动。
- 本登记文件与本批交付物一致，写入 S1-02B3 校验的冻结输入清单（SHA-256 门）。