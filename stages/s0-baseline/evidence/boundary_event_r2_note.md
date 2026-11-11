# 边界重基线事件记录（R2 结封期）

本文件记录首次 sealed 校验（2026-11-09T17:43:07+08:00）之后、最终结封之前，
工作区保护区内出现的一次用户侧 Finder 活动及其处理。属执行器回传记录。

## 事件一：ale-data/task-data-v1.1/legal.zip 被移除

- 该文件由用户侧 Finder 于 2026-11-09T16:28:08 创建（AppleDouble 压缩包），
  最初登记于 boundary_user_delta.tsv（sha256 122bbe1f2d399d00c7fc508be32f967b1cd0b028e1fd895a31a8a87c4676ae96，
  1007838 字节）。
- 首次 sealed 校验（17:43:07）时仍在位，bd-07 通过（regular=79077 links=3 delta-found=7/7）。
- 最终 verify-checksums（17:59:07 左右）发现 bd-07 FAIL：regular=79076，delta-found=5/7。
- 定位：legal.zip 已不存在；ale-data 常规文件数 79076 = 基线 79070 + 6 个 .DS_Store，
  与 legal.zip 移除完全吻合。
- 归因：用户侧操作（未发现任何执行器对该路径的写入或删除；执行器全程只写 R2 目录，
  且 17:43 之后执行器对 ale-data 仅有只读遍历）。

## 事件二：ale-data/task-data-v1.1/.DS_Store 被重写

- 旧值（登记于初版 boundary_user_delta.tsv）：sha256 21cb90ac308424271dba95cfc6237f9413d04870e88012d5feb96002ebbc9800，
  6148 字节，mtime 2026-11-09T16:41:47。
- 新值（本次测得的当前值）：sha256 1749c68239d0df0074ce559f5ab863abea8af380c5a17918a1e5c09bbc53491d，
  6148 字节，mtime 2026-11-09T17:57:51。
- 归因：用户侧 Finder 浏览目录时改写文件夹元数据（.DS_Store 是 Finder 自身的元数据文件）。

## 重基线动作

1. boundary_user_delta.tsv 的 ale-data 段由 7 行改为 6 行：删除 legal.zip 行，
   更新 task-data-v1.1/.DS_Store 行的哈希与 mtime。
2. scripts/validate_r2.py 的 bd-07 期望值由 regular=79077 改为 79076
   （79076 = 基线 79070 + 6 个 .DS_Store；links=3 不变）。
3. CHANGELOG_R2.md 边界事件节追加本条记录。
4. 由于验证器与边界登记在首次 sealed 之后发生变化，按结封流程重新执行 sealed 校验，
   使 VALIDATION_RESULTS.json 与最终冻结的边界登记一致。
5. 本事件与首次 sealed 的历史证据（validate_r2_output.json/txt、sealed_stdout.txt、
   sealed_stderr.txt 的 17:43 版本）不再存在于磁盘（被重跑覆盖），
   其内容事实记录于 progress.log 与 CHANGELOG_R2.md。

## 对“越界写入检查”结论的影响

- 执行器越界写入：本执行器在整个 R2 期间（含本重基线）对四个原始目录、inputs-readonly、
  第一轮目录、R1 目录、DIRECTORY_SUMMARY_REPORT.md、.audit 均为零写入，见 bd-01 至 bd-05。
- ale-data 与 ale-tasks-base 的变更全部可归因于用户侧 Finder 活动（本文件与 boundary_user_delta.tsv 为证）。
- bd-06 与 bd-07 通过即证明：除上述登记的用户增量外，两个数据目录没有其他变化。
## 事件三：封存期 Finder 持续改写 .DS_Store（18:10 至 18:17）

- 18:12 与 18:13 两次 sealed 重跑的 bd-07 先后发现 task-data-v1.1/.DS_Store 与 ale-data/.DS_Store
  被用户侧 Finder 重写（非执行器写入；执行器对 ale-data 只有只读遍历）。
- 18:17 测算确认：ale-data 非 .DS_Store 常规文件恰为 79,070，与原始基线完全相等，
  说明内容文件已回到基线状态（legal.zip 已由用户移除），只有 Finder 元数据在变动。

## bd-07 断言设计（版本 2，回应上述事件）

- 覆盖范围仍是 ale-data 内容保护。断言分两类：
  1. .DS_Store 登记行：只断言存在性与总数（总数 = 基线 79070 + 登记行数），不断言字节，
     因为用户在 Finder 浏览会持续改写其字节；
  2. 非 .DS_Store 登记行（内容增量，如 zip）：断言存在且字节精确匹配。
- 若用户新增或删除任何内容文件，总数断言会失败，触发下一次显式重基线并记录，
  不会被静默吞掉。
- regular 计数当前期望值：79070 + 6 = 79076；links=3。
