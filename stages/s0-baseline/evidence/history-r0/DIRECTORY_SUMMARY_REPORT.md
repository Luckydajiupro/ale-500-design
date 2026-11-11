# ALE 500 任务项目 Phase 0 目录汇总报告

冻结时间。2026-11-08 Asia/Taipei。工作区 /Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108。

## 1. 原始四个目录路径

- /Users/mac/Workspaces/ale-研究设计/agents-last-exam
- /Users/mac/Workspaces/ale-研究设计/ale
- /Users/mac/Workspaces/ale-研究设计/ale-data
- /Users/mac/Workspaces/ale-研究设计/ale-tasks-base

## 2. 只读副本路径

/Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108/inputs-readonly
其中 01_agents-last-exam、02_ale、03_ale-data、04_ale-tasks-base 一一对应上方四个原始目录。

## 3. 每个目录的文件数量

| 目录 | 普通文件数 |
| --- | --- |
| 01_agents-last-exam | 28,444 |
| 02_ale | 495 |
| 03_ale-data | 79,070 |
| 04_ale-tasks-base | 105 |
| 合计 | 108,114 |

副本与原始目录逐目录文件数完全一致。SHA256 清单覆盖全部 108,114 个文件加上 3 个记录文件，共 108,117 行。

## 4. 每个目录的大小

| 目录 | 原始 (KB) | 副本 (KB) |
| --- | --- | --- |
| 01_agents-last-exam | 1,608,148 | 1,616,836 |
| 02_ale | 10,536 | 10,536 |
| 03_ale-data | 90,529,416 | 90,697,168 |
| 04_ale-tasks-base | 520 | 520 |
| 合计 | 92,148,620 | 92,325,060 |

副本约大 172 MB。原因是 19 个文件的已分配磁盘块多于原始文件。逻辑字节大小全部一致。这 19 个文件是稀疏或压缩分配差异，其中 01 有 1 个（git pack 文件），03 有 18 个（.h5、.simg、.sav、pickle、.tif、.ply、h5ad、zip 等大资产）。证据见 .audit/size-compare.tsv。

## 5. Git 仓库的 remote、分支和 HEAD commit

| 仓库 | remote | 分支 | HEAD |
| --- | --- | --- | --- |
| 01_agents-last-exam | https://github.com/rdi-berkeley/agents-last-exam.git | main | 2e91edd3cd26baa35a38127c90c8e5241dfbe62f |
| 02_ale | https://github.com/AgentsLastExam/ale.git | main | 73517c2eb097abe7974e9ec4de9819a02cd0ee81 |
| 04_ale-tasks-base | https://github.com/AgentsLastExam/ale-tasks-base.git | main | 492249a2ca4b9d74efd3584a90399473c2e928c7 |

标签。01_agents-last-exam 有 v1 和 runtime-qe-bgw-6.7.0-4.0。02_ale 和 04_ale-tasks-base 无标签。03_ale-data 不是 git 仓库。

## 6. 是否存在未提交修改

三个仓库在原始位置和只读副本的工作区都干净。无未提交修改。

## 7. 数据包文件数量和大小

03_ale-data 顶部结构为 archive/ 和 task-data-v1.1/。archive/ 中 ale-tasks-data.tar.gz 约 36.5 GB，是官方打包数据。task-data-v1.1/ 是解包后的任务树。常见包类型计数。.gz 1,443（其中多数为 .nii.gz 影像）、.zip 9、.tar.gz 5、.tgz 2、.parquet 1、.simg 1、.h5 2、.h5ad 1。

## 8. 软链接情况

25 条。22 条指向输入目录内部且可解析。2 条指向内部但目标缺失（tcga_brca_deg_analysis 任务内 runtime_env/.venv 的 python3 与 python3.14 链接）。1 条指向输入目录外部且目标缺失（同一 .venv 的 python 指向 /home/user/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin/python3.14）。全部在复制时按原样保留，未解引用。明细在 inputs-readonly/SYMLINKS.tsv。

## 9. SHA256 清单位置

/Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108/inputs-readonly/FILE_SHA256SUMS.txt

每行 sha256、字节大小、相对路径。108,117 行，与 find 统计的普通文件数一致。清单自身不在清单内。

## 10. 只读权限检查结果

chmod -R a-w 已应用于 inputs-readonly。检查发现 0 个可写文件或目录。四个快照目录均存在。三个 .git 目录保留。analysis 目录保持可写。

## 11. 原始目录是否保持未修改

保持未修改。文件数与复制前基线一致（28,444、495、79,070、105）。三个 git 仓库工作区干净。HEAD 未变。

## 内容一致性证明

除上面的 SHA256 清单和逐目录文件数之外，还运行了 rsync -c 全量校验和比较。原始目录与只读副本之间 0 个校验和差异、0 个大小差异。唯一差异是文件权限位，来自本次只读锁定手段本身。结论为字节级内容一致。

## 校验结果

全部通过。目录汇总、哈希、只读校验这三项闸门都满足，进入 Phase 0 官方基线解析。