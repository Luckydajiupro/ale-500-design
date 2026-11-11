# ALE 500 任务项目 Phase 0 项目简报（最终基线版）

本文件是 Phase 0 最终基线产物，继承 R1 修订版。继承来源与 SHA256 见 SOURCE_MANIFEST_FINAL.json 的 sources 节。逐项改前改后记录见 evidence/history-r1/CHANGELOG_R1.md。

## 目标（R01 修订）

项目最终交付 500 条任务。500 条全部由专家在平台上新生产，并依次通过内容审核、工程转换、运行期验证和交付验收四关。

官方任务是研究与对齐参考，不自动计入 500 条交付数量。不存在"先迁移 103 个官方任务再补 397 个"的已批准方案，也不存在"先转换 71 个官方 Linux 任务"的路线。

项目有两条独立链路。

- 官方参考研究链路。读官方输入，产出对齐证据与基线事实。输入是 01 旧基准仓、03 数据转储、02 引擎、04 模板仓。本链路不产出交付任务。
- 专家新任务生产链路。专家在平台上新生产 Canonical Task Source。工程接收冻结的 Engineering Ready 快照后做 ALE 转换。Canonical Task Source 是专家新生产的内容，不是从官方 01 或 03 拷贝迁移的内容。

[doc: evidence/history-r1/EXECUTION_BRIEF_FROM_CHAT.md 二]

## 已确认前提（R02 修订）

以下前提由项目负责人确认，本程序只记录不改变。

- 最终交付 500 条专家新生产并通过验收的任务。
- 官方任务不自动计入 500 条交付数量。不存在"先迁移 103 条再补 397 条"的已批准方案。
- 现有腾讯云 Linux 云服务器不能内部再虚拟化虚拟机，禁止嵌套虚拟化。
- 沙箱或运行环境 provider 与模型 provider 必须分开。
- Windows 与 GPU 是否采用，以及相应资源预算，仍待后续确认。
- 平台负责专家资料采集、脱敏、Agent 辅助、校验审核和冻结交接。后端工程负责目标格式转换、运行验证、评测和交付。
- P0-9 总体方案已采纳。方案含全量自动检查、专家自检、Agent 预审、风险分层人工审核、工程自动验证和项目负责人批次放行六个机制。具体抽样率、风险阈值和审核人数尚未冻结。

[doc: evidence/history-r1/EXECUTION_BRIEF_FROM_CHAT.md 二]

## 输入身份

| 快照目录 | 上游 | HEAD | 角色 |
| --- | --- | --- | --- |
| 01_agents-last-exam | https://github.com/rdi-berkeley/agents-last-exam.git | 2e91edd3cd26baa35a38127c90c8e5241dfbe62f | 旧官方公开基准仓库，v1.1 发布任务集的研究参考来源 |
| 02_ale | https://github.com/AgentsLastExam/ale.git | 73517c2eb097abe7974e9ec4de9819a02cd0ee81 | 新引擎仓库，目标运行时合同的定义源 |
| 03_ale-data | 无 git | 无 | v1.1 任务数据转储，含 archive/ 与 task-data-v1.1/ |
| 04_ale-tasks-base | https://github.com/AgentsLastExam/ale-tasks-base.git | 492249a2ca4b9d74efd3584a90399473c2e928c7 | 新任务模板仓库，目标任务格式的样板 |

原始目录与副本的对应关系见 inputs-readonly/SOURCE_MAP.tsv。[doc: inputs-readonly/SOURCE_MAP.tsv]

## 冻结事实

- 快照复制完成于 2026-11-08（Asia/Taipei 时区，SOURCE_MAP.tsv 记录为 +0800）。[doc: inputs-readonly/README_READ_ONLY.md]
- 快照共 108,114 个普通文件。[doc: inputs-readonly/README_READ_ONLY.md]
- SHA256 清单 inputs-readonly/FILE_SHA256SUMS.txt 有 108,117 行，覆盖除清单自身外的全部普通文件。[cmd: 原执行轮 wc -l]
- 体积统一以 bytes 为计算基准。四个口径分开记录。归档包、解包任务树、数据目录总量、整个只读输入各自的字节数与换算值见 evidence/sizes_scopes.tsv。[cmd: R1 静态统计]
- 符号链接记录 inputs-readonly/SYMLINKS.tsv 共 25 条。直接目标、最终目标、是否越界、是否缺失的四列重核见 evidence/symlink_resolution_r1.tsv。[cmd: R1 静态统计]
- 只读锁由原执行轮验证过，inputs-readonly 内可写路径为 0。文件与目录的精确权限位重核见 evidence/chmod_wording_check.md。[原执行方记录: 04-verify-readonly.sh 输出]
- rsync -c 校验证明副本与原树内容字节一致，仅权限位按设计不同。19 个文件分配块差异在 evidence/size-compare.tsv。[原执行方记录: evidence/verify-rsync-checksum.log]
- 历史执行记录全部来自原执行方留存的日志，引用时注明出处。缺失的日志不补造。[R10 规则]

## 只读边界（R12 修订）

- inputs-readonly 保持锁定。目录 555，01 与 04 普通文件 444，03 数据文件与 README_READ_ONLY.md 为 400，可执行脚本 555，属主仍可改回。精确表述见 evidence/chmod_wording_check.md。
- 四份原始仓库全程不接触。
- 第一轮 12 份产物 analysis/phase0-official-baseline/ 全程不改动。
- 原 DIRECTORY_SUMMARY_REPORT.md 与 .audit/ 历史审计记录全程不改动。
- 最终整合轮唯一允许写入的目录是 analysis/phase0-final/。

## Phase 0 范围

本轮只做这些事。

- 以哈希核定三轮继承关系，把最终有效基线整合进 phase0-final。
- 修正过时表述，全部写入最终目录。
- 产出 PHASE0_FINAL_REPORT.md、SOURCE_MANIFEST_FINAL.json、evidence/、FINAL_VALIDATION_REPORT.md、FINAL_CHECKSUMS.sha256 与只追加的 progress.log。
- 冻结前独立校验，校验通过后封存。

本轮不做这些事。

- 不解除只读，不执行 git pull、checkout、reset、clean。
- 不重新复制数据包，不安装环境，不执行官方任务，不跑评测。
- 不开发平台或转换器，不进入 Phase 0.5 或 P1。

## 证据规则

五类标签（[doc]、[code]、[cmd]、[inference]、[unknown]）与第一轮相同。R1 补充四条。

- 引用路径存在不等于引用支持结论。重要技术断言须核对具体源码片段。
- 历史 rsync、权限检查注明为原执行方记录。没有原始日志就保留证据限制，不补造历史日志。
- 没有证据写 UNKNOWN。没有运行写 NOT_RUN。GUI 未知不等于无 GUI。
- 官方明确说明、代码或命令事实、结构推断、无法确认四类严格分开。

## 产出索引

phase0-final 目录内。

- 10 份正式基线文件，沿用原名。
- PHASE0_FINAL_REPORT.md，综合全部有效研究结论。
- SOURCE_MANIFEST_FINAL.json，每份最终文件的来源与 SHA256。
- evidence/，被结论依赖的证据与三轮历史记录。
- FINAL_VALIDATION_REPORT.md 与 FINAL_CHECKSUMS.sha256，冻结依据。
- progress.log，只追加的进度日志。

继承来源按哈希核定，路径与 SHA256 记入 SOURCE_MANIFEST_FINAL.json。

## 停止条件

Phase 0 已完成并验收通过。历史目录已归档并完成清理，归档位置是 /Users/mac/Archives/ALE-Phase0-History-20261110。analysis/phase0-final/ 是当前唯一有效基线。Phase 0 CLOSED。Phase 0 最终基线已验收，历史版本已归档，后续不再修改 Phase 0 内容。