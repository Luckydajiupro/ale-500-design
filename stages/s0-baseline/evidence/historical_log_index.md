# 历史执行记录索引 R1

本文件核实任务书点名的历史执行记录，每一件都注明存在性与内容。
这些记录全部是原执行人（initial executor）在 2026-11-08 留下的，不是本程序处理的产物。
引用它们时要标注这一身份 [doc: 历史记录，原执行人]。
核实方法是 ls 与只读读取，没有改写任何记录文件 [cmd]。

一个位置勘误先行。任务书写的路径是 .audit/xxx，实际这些记录位于工作区根的 .audit 目录，不在 ale-phase0-workspace-20261108 之下。

[cmd: ls /Users/mac/Workspaces/ale-研究设计/.audit/ 与 ls /Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108/.audit/]

后一个目录不存在，前一个目录真实存在。
下面每条都用绝对路径。

## 1. phase0-copy-20261108-225432.log

存在 [cmd: ls]。
路径 /Users/mac/Workspaces/ale-研究设计/.audit/phase0-copy-20261108-225432.log。
记录的是一次 rsync 复制。四个源目录逐一复制到 inputs-readonly，每段 BEGIN 与 END 配对，含文件数与字节数。

[doc: 该日志头部]

```text
BEGIN 01 src=/Users/mac/Workspaces/ale-研究设计/agents-last-exam dst=.../inputs-readonly/01_agents-last-exam
Number of files: 31460
Number of files transferred: 28444
Total file size: 1576355407 B
...
END 01 rc=0
```

四个源目录都带 END xx rc=0 标记。04 段确认文件数为 105 [cmd: 尾部核对]。
这是复制动作的原始证据，与 DIRECTORY_SUMMARY_REPORT.md 的数字一致 [doc: 汇总报告第 19 到 27 行]。

## 2. verify-rsync-checksum.log

存在 [cmd: ls]。
路径 /Users/mac/Workspaces/ale-研究设计/.audit/verify-rsync-checksum.log。
全文四行，记录四对目录的 rsync 校验和比对结论。

[doc: 该文件全文]

```text
pair agents-last-exam -> 01_agents-last-exam: rc=0, changed-items=28444
pair ale -> 02_ale: rc=0, changed-items=493
pair ale-data -> 03_ale-data: rc=0, changed-items=79074
pair ale-tasks-base -> 04_ale-tasks-base: rc=0, changed-items=102
```

四对全部 rc=0。
changed-items 表示校验和模式下被检查的条目数，不是差异数 [inference: rsync -c 语义]。
这是内容一致性的校验记录。

## 3. size-compare.tsv

存在 [cmd: ls]。
路径 /Users/mac/Workspaces/ale-研究设计/.audit/size-compare.tsv。
表格六列，pair、relpath、orig_size、orig_blocks、copy_size、copy_blocks。
记录的是已分配磁盘块的比较，不是逻辑字节差异。
19 个文件块数不同。1 个在 01 的 git pack，18 个在 03 的大资产。

[doc: 该文件头部两行]

```text
pair	relpath	orig_size	orig_blocks	copy_size	copy_blocks
01	.git/modules/.../pack-7a78d700....pack	337788497	659744	337788497	677120
```

orig_size 与 copy_size 在示例中完全相等，orig_blocks 与 copy_blocks 不相等。
这是 03 大文件稀疏或压缩分配差异的记录，汇总报告第 39 行引用了它 [doc: DIRECTORY_SUMMARY_REPORT.md:39]。

## 4. phase0-precheck-20261108-225116.log

存在 [cmd: ls]。
路径 /Users/mac/Workspaces/ale-研究设计/.audit/phase0-precheck-20261108-225116.log。
记录复制前的预检，包括源目录列表、realpath 嵌套检查、四个 git 仓库的 remote 与 HEAD、ale-data 统计、符号链接检查与 rsync 位置。

[doc: 该文件 git 段节选]

```text
--- agents-last-exam ---
branch: main
HEAD: 2e91edd3cd26baa35a38127c90c8e5241dfbe62f
HEAD subject: fix(tasks): improve equity workbook verification (#134)
--- ale ---
HEAD: 73517c2eb097abe7974e9ec4de9819a02cd0ee81
HEAD subject: Merge pull request #108 from AgentsLastExam/feat/task-gpu-types
--- ale-tasks-base ---
HEAD: 492249a2ca4b9d74efd3584a90399473c2e928c7
HEAD subject: docs: drop the removed [ale] table from the README (#6)
```

al-data 统计为 79,070 个文件约 86G [doc: 同文件 ale-data stats 段]。
本文件记录的 HEAD 与本轮引用一致 [cmd: 与 no-nested-virt 前提下的引擎核对]。

## 5. original-baseline-20261108-225436.tsv

任务书点名的这个名字不存在 [cmd: ls .audit/*225436*，无此文件]。
实际存在的是与之同用途、时间戳差 34 秒的文件。

[cmd: ls /Users/mac/Workspaces/ale-研究设计/.audit/original-baseline-20261108-225402.tsv]

文件名 original-baseline-20261108-225402.tsv，264 字节。
内容五行，表头 dir files dirlinks size_bytes git_head，四行数据对应四个原始目录。

[doc: 该文件节选]

```text
dir	files	dirlinks	size_bytes	git_head
agents-last-exam	28444	20	1608148	2e91edd3cd26baa35a38127c90c8e5241dfbe62f
ale	495	1	10536	73517c2eb097abe7974e9ec4de9819a02cd0ee81
ale-data	79070	4	90552520
ale-tasks-base	105	0	520	492249a2ca4b9d74efd3584a90399473c2e928c7
```

这是复制前的基线快照记录 [doc: 原执行人记录]。
本程序没有炮制 225436 这份日志，如实报告 225402 是实际文件 [cmd]。

## 6. scripts 目录

存在 [cmd: ls]。
路径 /Users/mac/Workspaces/ale-研究设计/.audit/scripts/。
六个脚本，名字起头序号连。

[cmd: ls 输出]

```text
01-copy-readonly.sh
02-scan-symlinks.sh
03-generate-sha256.sh
04-verify-readonly.sh
05-compare-sizing.sh
06-rsync-checksum-verify.sh
```

对应动作是复制、符号链接扫描、sha256 清单生成、只读校验、块大小比较、checksum 复核 [inference: 文件名与日志对应]。
这些脚本是原执行人的工具，未被本轮运行 [cmd]。

## 7. DIRECTORY_SUMMARY_REPORT.md

存在 [cmd: ls]。
路径 /Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108/DIRECTORY_SUMMARY_REPORT.md。
83 行，是原执行人在复制与校验之后写的汇总。
内容有四个原始目录路径、只读副本路径、各目录文件数（28,444、495、79,070、105，合计 108,114）、原始与副本大小、git remote 分支与 HEAD、未提交修改检查、数据包统计、符号链接情况（25 条）、SHA256 清单位置（inputs-readonly/FILE_SHA256SUMS.txt，108,117 行）、只读权限检查与内容一致性结论。

[doc: DIRECTORY_SUMMARY_REPORT.md:19-27, 39, 63-83]

它是本工作区的冻结说明，按原执行人的记录引用 [doc: 历史记录]。

## 8. 目录里还有的记录

如实列出其余条目，它们不是任务书点名项但同属这批历史记录 [cmd: ls]。

- copy-times.tsv。四行表格，记录四个目录复制起止时间。
- phase0-notes/。三个笔记文件，01_agents-last-exam.md、02_ale.md、03_04_task_data_and_templates.md。它们是原执行人的审读笔记，本轮的 C2 与 07 有引用 [doc: 历史记录]。

## 9. 不造假声明

本文件列出的每条都有 ls 或读取佐证 [cmd]。
一个名字（original-baseline-20261108-225436.tsv）经查不存在，替代文件是 225402，如实写在第 5 节。
没有其他被任务书点名却找不到的记录 [cmd: 逐条核实]。