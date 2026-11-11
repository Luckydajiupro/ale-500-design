# chmod_wording_check, inputs-readonly 权限措辞核对

结论。round-1 写的 555 只对目录成立。普通文件是 444 或 400。该树不是整体 555。

## round-1 措辞原样引用

[doc: analysis/phase0-official-baseline/00_project_brief.md:32] - inputs-readonly 整体 chmod 555。任何写入、改名、删除、chmod 都被禁止。

## stat 实测

取样命令是 stat -f 与 stat -x 组合，[cmd]。目录全部是 dr-xr-xr-x 0555，属主 mac uid 501。

| 对象 | mode |
| --- | --- |
| inputs-readonly 根与各级目录 | dr-xr-xr-x 0555 |
| 01 任务卡 task_card.json | -r--r--r-- 0444 |
| 01 tasks 树可执行脚本（8 个） | -r-xr-xr-x 0555 |
| 04 task.toml | -r--r--r-- 0444 |
| 04 模板树可执行脚本（40 个） | -r-xr-xr-x 0555 |
| 03 数据文件（含 tumor_001.tif） | -r-------- 0400 |
| FILE_SHA256SUMS.txt | -r--r--r-- 0444 |
| SYMLINKS.tsv | -r--r--r-- 0444 |
| README_READ_ONLY.md | -r-------- 0400 |

直方图证据行。

```
== samples ==
                 dr-xr-xr-x 0555 owner_mac_uid=501 gid=20
01_agents-last-exam dr-xr-xr-x 0555 owner_mac_uid=501 gid=20
01_agents-last-exam/tasks dr-xr-xr-x 0555 owner_mac_uid=501 gid=20
01 card json     -r--r--r-- 0444 owner_mac_uid=501 gid=20
01 task dir      dr-xr-xr-x 0555 owner_mac_uid=501 gid=20
03 tif           -r-------- 0400 owner_mac_uid=501 gid=20
04 toml          -r--r--r-- 0444 owner_mac_uid=501 gid=20
manifest         -r--r--r-- 0444 owner_mac_uid=501 gid=20
symlinks tsv     -r--r--r-- 0444 owner_mac_uid=501 gid=20
readme           -r-------- 0400 owner_mac_uid=501 gid=20

== histograms ==
01 tasks (all files): files=621 {292: 613, 365: 8}
03 data sample (one variant): files=12 {256: 12}
04 templates: files=105 {292: 65, 365: 40}
```

## R1 修正表述

inputs-readonly 目录统一为 0555。01 与 04 的普通文件大多是 0444，其中可执行脚本
是 0555。03 数据文件是 0400，只有属主可读。两个清单文件是 0444，README 是 0400。
属主（mac uid 501）保留写入与 chmod 能力，冻结依赖纪律而非权限。

本次审核没有改动 inputs-readonly 里任何权限位。
