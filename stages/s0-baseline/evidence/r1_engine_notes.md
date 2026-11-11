# R1 引擎侧笔记

本文件是本审计分支的简短笔记，供 CHANGELOG_R1.md 取用。
内容三段。跑了什么命令。第一轮文件与本轮核实的冲突，写成前与后。UNKNOWN 清单。

## 命令

全部为只读操作。没有 git 操作，没有任务执行，没有评测，没有安装 [cmd]。

- read 引擎核心文件。taskspec.py、config.py、assets.py、providers 四模块、providers README、manifest.py、ale_verify __init__.py、result.py、verdict.py。
- read 引擎文档。task-authoring.md、task-assets.md、sandbox-image.md、lexicon.md、autonomous-harness.md、images/README.md、.env.example。
- grep 全仓检索。convert 命令、converter 模块、playwright、nested、metadata 键、@task-params、cua-desktop 预设、license 字样。
- ls 与 wc 核查旧仓。docker_support.txt 90 行头注 12 行，ale_cli.txt 88 行头注 2 行，gpu.txt 6 行头注 3 行，providers 六模块目录。
- read 旧仓样例任务卡与 main.py 头部。american_option_pricing_ls 的 16 个顶层键、inputFiles 四元素、evaluation 文本、vm 键。
- read 01 仓 .git/packed-refs 第 31 行 feat/tasks-v2 ref。
- ls 与 read .audit 记录。phase0-copy、verify-rsync-checksum、size-compare、phase0-precheck、original-baseline 225402、copy-times、scripts 六件、phase0-notes 三份、DIRECTORY_SUMMARY_REPORT.md。
- find 与 grep 许可证。02、04、01 三仓的 LICENSE 类文件和 license 字样。
- read 第一轮 06、07、09、10 四个文件并逐行裁定。

## 冲突清单

每条给前与后。

1. artifacts 语义。前，第一轮 07 第 20 行把它当作 inputFiles 的新格式对应物。后，artifacts 是输出收集路径，未声明的不收集，collect host 才落宿主机 [code: taskspec.py:74-84, config.py:105-117]。
2. 转换方向。前，第一轮 07 第 65 行写新引擎承诺 Harbor 到 ALE 的转换器。后，作者规范一句是 ALE 任务经一次 conversion 到达 Harbor [doc: task-authoring.md:13-14]，常量注释一句是纯 1.4 被一次 conversion 转成 ALE 这版 [code: taskspec.py:523-525]，引擎无转换器，旧仓 feat/tasks-v2 分支有 ref 证据 [cmd: packed-refs:31]。
3. metadata。前，第一轮写无运行时效果且分类必须放引擎之外。后，运行时唯一读取是原样携带 [code: manifest.py:318]，lint 读 network_justification 一键 [doc: task-authoring.md:211]，metadata 是自由字典可存任意键 [code: taskspec.py:796]。
4. qemu 加 KVM 自托管。前，第一轮 06 第 90 行说 Tencent 可自托管。后，不嵌套虚拟化是项目前提 [doc: R1 brief]，qemu 硬要求 /dev/kvm [code: qemu.py:703-726]，引擎对嵌套虚拟化零声明 [cmd: grep 无命中]。
5. 宿主机可跑。前，第一轮 06 第 89 行写 docker 能直接落地 64 个任务。后，三栏拆开，当前宿主机实测栏全部 NOT_RUN [cmd: 本轮零执行]。
6. GPU 预算。前，第一轮 06 第 92 行与 09 第 14 行把无 GPU 预算写成既定。后，GPU 与 Windows 采用及预算为开放决策 [doc: R1 brief]。
7. P0-9。前，第一轮 09 第 33 行写 P0-9 是管线阶段标号并给 P0 到 P5 表。后，P0-9 是决策编号，六项机制获批，抽样率阈值人数未冻结 [doc: R1 brief]。
8. 模型提供方。前，第一轮 09 第 30 行把只接一个主模型提供方写入已定决策。后，八家字面量与 ALE_ 键机制是代码事实 [code: config.py:155-158, .env.example:7-24]，选哪家是开放决策 [doc: R1 brief]。
9. 类别信息落点。前，第一轮三处写必须放 task.toml 之外。后，metadata 可承载，引擎不解释 [code: taskspec.py:796]。
10. ResultRecord。前，第一轮 07 第 51 行给八个状态值但没有行号。后，本分支直接验到 verdict.py:19-41 与 result.py:61，八个状态成立且 schema 字面量为 2。
11. 历史日志名。前，任务书点名 original-baseline-20261108-225436.tsv。后，实盘无此文件，实存 original-baseline-20261108-225402.tsv [cmd: ls 无命中与命中]。
12. 外部服务表。前，第一轮 06 第 62 到 73 行给出 8 任务三分类。后，保持等待数据侧 R1 数字，本次只留合并点。

## UNKNOWN 清单

- qemu provider 在嵌套虚拟化下是否可行。引擎零声明 [cmd]。
- docker 乘 Windows、daytona 乘 Windows、daytona 乘 macOS 等组合引擎未声明，无证据 [code: 注册表与配置字面量]。
- 每任务 gui_status 值含义。快照内无引擎或官方文档佐证，等数据侧任务清单。
- 外部服务的最终三分类普查。数据侧审计方所有。
- 02_ale 与 04_ale-tasks-base 的许可证状态。无文件无字段无 README 章节，未确认 [cmd: find 与 grep 零命中]。
- 旧格式 task_card.json 有无强校验器。01 仓未见 jsonschema 证据 [cmd: grep 仅上游命中]。
- validate 的零分加满分双跑要求。仅原执行人笔记记录，本轮未在引擎文档重查到 [unknown]。
- 旧引擎宿主机官方支持面与 1920x1080 桌面记录。仅历史记录，未重查。
- feat/tasks-v2 分支的完整文件内容。ref 存在 [cmd]，工作区未检出，内容以原执行人笔记为准 [doc: 历史记录]。
- 官方任务变体模型与新单目录声明的映射规则。数据侧未定。
- Windows 与 GPU 的采用决策与预算。开放 [doc: R1 brief]。