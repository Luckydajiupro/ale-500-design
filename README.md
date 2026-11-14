# ALE 500 条任务数据生产与交付项目

本项目为 ALE（Agents' Last Exam）评测集生产 500 条原创的专业工作任务，交给合作方验收。任务不是问答样本，而是可运行、可评测、可复现的专业工作：有真实资料、有执行环境、有多步操作、有交付物、有成功判定。

当前处在阶段一收口、阶段二与阶段三设计修订的位置。2026-11-13 的修订把阶段二和阶段三从严格串行改为部分并行：阶段 3 从 11-13 起做骨架、11-18 起做 M1a-Core，阶段 2 试点 11-18 签人；12-01 是首批 30 条受控启动和 M1b 启动日，不是两条线的开工日，也不代表平台与 Agent 已完成全部试点。七阶段状态见下表和 `stages/README.md`。

先记住四件事。第一，阶段 1 已由项目负责人签字收口，独立复审已决定不做。第二，阶段 2 的出口不再是 3 条任务四段全 PASS，而是 3 条试点走完“人工标注、平台辅助、专家确认、审核、自动 ALE-data 组包、校验、入库”，工程侧的格式转换与运行冒烟只作并行证据，不作为试点通过条件。第三，平台 P1 是专家生产与半自动化标注系统，负责把规范任务源自动构建成完整 ALE-data 包、校验并入库，不负责 Harbor 转换、运行容器、判分和正式评测。第四，500 是项目目标，配额已按 14 个域定好，分 W1 到 W4 四批生产，2027-04-30 交付；首批 30 条是正式生产第一梯队，完成生产指审核通过并入库，计入 500 仍以四道门和合作方验收为准。

## 仓库范围

本仓库收三类东西。一类是当前被批准的设计，在 `docs/`。另一类是阶段目录的完整内容，在 `stages/`，用来证明每个阶段的结论。第三类是对外沟通材料，在 `deliverables/`，从设计派生，不是设计源。

513 个文件，约 7.5 MB，克隆下来就是全部内容。

克隆下来能读设计，也能复跑两个阶段的出口检查。阶段 0 的 65 条校验和、阶段 1 的 15 项和 16 项校验、阶段 2 工程冒烟检查器与试点出口检查器的自检，都在仓库里跑，不需要额外准备。阶段 2 出口只跑 `pilot_gate.py`，`phase2_gate.py` 的 PASS 不是出口。

不进仓库的只有三类。官方输入的 88 GiB 副本、工作副本 `work/`、创建只读副本用的 `tools/freeze/`。前两类由 `.gitignore` 排除，第三类是冻结动作的一次性脚本，已经用完。

因此校验分两种。文档规则、文档数字、阶段 0 与阶段 1 的出口、阶段 2 工程冒烟检查器与试点出口检查器的自检，在这个仓库里就能跑。官方输入的全量哈希要持有 88 GiB 副本的机器才能跑。两种在下面分开列。

## 协作流程

`main` 是保护分支。所有改动走同一条路：拉分支、改、开 PR、合并。不直接提交 `main`。

分支名带前缀，一眼看出改什么。`docs/<主题>` 改设计文档，`stage/<阶段号>-<主题>` 收口一个阶段，`tool/<主题>` 改校验工具，`ci/<主题>` 改流水线。

一个 PR 只做一件事。PR 描述写清为什么改、改了什么、怎么验证。合并用 squash，`main` 上每个提交对应一个已合并的 PR。

远端分支在合并后自动删除，仓库设置 `delete_branch_on_merge` 已打开。本地那份分支要自己删，分两步。

先 `git switch main` 切走。处在某个分支上时 git 拒绝删除该分支，合并时人通常正站在功能分支上。

再 `git branch -D <分支名>`。这里用大写 `-D`，不用 `-d`。squash 合并产生的提交不是原分支的祖先，`-d` 只在你本地还留着 `origin/<分支名>` 时才会放行。远端分支既然合并时就删了，下一次 `git fetch --prune` 之后那个 ref 就没了，`-d` 随即报未合并。2026-11-11 在临时仓库里复现过这两种状态，`-d` 在 tracking ref 还在时通过并给出警告，被 prune 后直接失败。

`-D` 删 ref 时顺带把 `.git/config` 里那段 `[branch "<分支名>"]` 一起去掉。这一步写失败时，git 打印 `error: could not write config file .git/config: Operation not permitted` 和一条 warning，分支照样删掉，退出码 0，那段配置留在原地。2026-11-11 在本机 agent 沙箱里碰到过一次。普通终端下 `-D` 会把配置清干净，我另建临时仓库对过。

残留什么时候有影响。没有同名分支时它不起作用。再建一个同名分支，git 就当它是上游，`git status` 立刻报 `[gone]`，`git push` 不带参数也会建出同名远端分支，2026-11-11 在临时仓库里对过。要清掉跑 `git config --remove-section "branch.<分支名>"`。

合并命令不要加 `--delete-branch`，2026-11-11 实测它会在删本地分支那一步挂住不返回，合并本身早已完成。

服务端保护目前在免费私有仓库上开不了。GitHub 对私有仓库的分支保护和规则集要求 Pro 或以上，免费计划只对公开仓库开放。所以保护落在三处。一处是 `.githooks/pre-push`，直推 `main` 会被拒绝，克隆后执行一次 `git config core.hooksPath .githooks` 生效。一处是 GitHub Actions 在每次 PR 上跑六条检查，任何一条不过就不合并。还有一处是约定，任何人都不直推。

要真正的服务端强制，只有两条路：把仓库改成公开，或升级 GitHub Pro。

## 七阶段状态

| 阶段 | 名称 | 状态 | 入口 |
|---|---|---|---|
| 0 | 官方基线 | 已关闭，可复验 | `stages/s0-baseline/STAGE.md` |
| 1 | 类别、任务族、专家、配额研究 | 已收口，已签字 | `stages/s1-research/STAGE.md` |
| 2 | 试点探索与交付合同 | 未启动 | 设计草案在 `plan/expert-supply` 与 `plan/platform-p1` 分支，阶段目录未建立 |
| 3 | 平台 P1 建设与验收 | 未启动 | 设计草案在 `plan/platform-p1` 分支，阶段目录未建立 |
| 4 | 首批 30 条正式生产 | 未启动 | 尚无产出 |
| 5 | 四批生产与质量控制 | 未启动 | 尚无产出 |
| 6 | 评测、冻结与交付 | 未启动 | 尚无产出 |

上表记的是 2026-11-13 的正式阶段状态。阶段 2 和阶段 3 的设计修订已于 2026-11-13 获项目负责人批准，但还没有进入执行，所以阶段状态仍是“未启动”。按批准稿，阶段 3 从 11-13 做骨架、11-18 做 M1a-Core，阶段 2 试点 11-18 签人；12-01 是首批 30 条受控启动和 M1b 启动日，试点出口最早 12-25，不可能在 12-01 供料。

## 目录约定

三层，职责不重叠。哪一层能改，看目录名就知道。

| 目录 | 是什么 | 能不能改 |
|---|---|---|
| `docs/` | 当前被批准的设计。永远只有一份，改就直接改这里 | 可改，改动即新结论 |
| `stages/` | 每个阶段交出的东西和它的证据。按阶段分目录 | 不改。要补充说明写在 `STAGE.md` |
| `deliverables/` | 对外沟通材料。从设计派生，不是设计源 | 可改，改动不代表设计结论 |
| `inputs/frozen/` | 官方内容的唯一副本，88 GiB，只读 | 不改。要工作副本另建 `work/` |

`docs/` 回答"现在怎么设计的"。`stages/` 回答"当时到底做出了什么"。`deliverables/` 回答"对外怎么讲"。`inputs/` 回答"官方资料长什么样"。四者不互相替代。

`stages/` 现在整目录进仓库。它的作用是让"已关闭"和"已收口"这两句话能被外部复核，不是当时那台机器上的自言自语。

## 二十份设计文档

| 文件 | 回答什么问题 |
|---|---|
| `docs/01-charter.md` | 为什么做、做什么、不做什么、交什么、500 条怎么算 |
| `docs/02-plan.md` | 七个阶段怎么走、每阶段产出什么、什么条件才能进下一阶段、每个出口怎么验 |
| `docs/03-quality-and-acceptance.md` | 什么样的任务算合格、四道门怎么过、生产完成和验收完成怎么分 |
| `docs/04-roles-and-decisions.md` | 谁决定什么、哪些已定、哪些没定 |
| `docs/05-research-findings.md` | 阶段一研究出了什么、这些数字能怎么用、不能怎么用 |
| `docs/06-decisions-and-blockers.md` | 哪些事还悬着、卡住哪个阶段、谁定、最晚什么时候、没定时的默认走法 |
| `docs/07-expert-supply.md` | 500 条配额怎么分到一级和二级类目、四批 W1 到 W4 怎么排、22 名核心与 104 份合同怎么来、评审怎么自动派单 |
| `docs/08-pilot-design.md` | 三条试点怎么从人工标注迁到平台辅助标注、平台和 Agent 怎么同步调试、试点怎么判定通过 |
| `docs/09-official-task-cases.md` | 六个官方任务怎么拆、真实产物和验证器长什么样、对 500 条和数据合同提出什么要求 |
| `docs/10-expert-annotation-spec-v0.md` | 专家实际做什么、一条合格任务怎么设计、十块任务源与 94 个字段怎么填、怎么自检和送审 |
| `docs/11-platform-product-design.md` | 平台完整功能地图、用户旅程、页面、Agent 介入点、组包校验入库、P1 与完整产品边界 |
| `docs/12-wave1-integration.md` | 三条线怎么合、Canonical 字段怎么统一、官方包与平台包怎么对齐、哪些要 PoC、下一波做什么 |
| `docs/13-canonical-schema-v1.md` | 规范任务源 112 个字段、41 个核心必填叶子、官方 variant 导入矩阵、平台包 overlay 与候选哈希 |
| `docs/14-verification-contract.md` | 验证意图合同十键、五种模式、六案例映射、Judge 校准与工程交接 |
| `docs/15-platform-architecture.md` | 平台分层、20 张表、九态状态机、22 个 API 动作、专家工作台与组包入库流程 |
| `docs/16-wave2-integration.md` | 三份合同怎么拼、哪些已有证据、哪些仍是候选、骨架启动条件与下一波模块 |
| `docs/17-wave3-implementation.md` | 真实工作台怎么跑、P12 包合同与哈希怎么验、两个验收节点的实际证据、已实现与未实现 |
| `docs/18-local-integration.md` | 本地 Docker Compose、PostgreSQL、Worker、Agent Gateway、P12 加固、备份恢复与浏览器验收证据 |
| `docs/20-expert-pilot-handbook.md` | 专家试点操作手册：按实际页面写登录、任务源、资料、Agent 建议、检查、提交、返修 |
| `docs/21-expert-pilot-materials.md` | 试点项目说明、示范任务、不合格示例、审核清单、T1/T2 模板与反馈表 |

`docs/data/` 放第一波与第二波的证据、字段、冲突、验证模式、PoC、合同对照与待裁决表，随对应文档一起读。

## 怎么校验

六条检查在这个仓库里就能跑，每次 PR 自动跑。

```bash
python3 tools/check_docs.py                    # 26 份活文档的写作规则
python3 tools/check_numbers.py                 # 文档里的数字与仓库表格一致
python3 tools/exit/selftest_phase2_gate.py     # 阶段 2 工程冒烟检查器自检
python3 tools/exit/selftest_pilot_gate.py      # 阶段 2 试点出口检查器自检
cd stages/s0-baseline && shasum -a 256 -c FINAL_CHECKSUMS.sha256
cd stages/s1-research && python3 -B scripts/35_validate_s1_02c.py
cd stages/s1-research && python3 -B scripts/36_validate_s1_02c_c16.py
```

第二波新增三条可复现检查。

```bash
python3 tools/wave2/hash_poc.py
python3 tools/wave2/verify_contract_check.py --selftest
PYTHONPATH=platform python3 -m unittest discover -s platform/tests -v
```

第七条要完整工作副本，仓库里没有那 88 GiB。

```bash
python3 tools/verify_frozen.py
```

失败怎么读。数据校验失败说明文件被动过，不要继续。文档写作规则失败说明有文档需要跳转才能读懂。数字校验失败说明文档和表格对不上，动手改之前先确认哪一个是对的，不要为了让检查通过而改数字。

## 保密与授权

这个仓库不含官方输入的副本，不含专家提交的原始资料，不含客户材料。研究表里出现的是公开标准与工具文档的链接和摘录，以及研究者自己的判断。

专家资料的授权方式、法域限制和合作条款还没有裁决。它们是待决事项，不在设计结论里，登记在 `docs/06-decisions-and-blockers.md`。

## 按角色怎么读

新加入的工程师，先读本文件，再读 `docs/02-plan.md` 知道全貌，然后读 `docs/03-quality-and-acceptance.md` 知道你交出去的东西要过什么关。

要接着做阶段二的人，先读 `docs/01-charter.md` 的交付物和非目标，再读 `docs/02-plan.md` 的阶段二、阶段三和出口表，重点看七段链、M1/M2、两个计数器。然后读 `docs/08-pilot-design.md` 看三条试点怎么排、平台和 Agent 什么时候进场。最后读 `docs/06-decisions-and-blockers.md` 看试点、法律 8 条、W1 衔接三件事有没有答案。

要评审阶段一的人，先读 `stages/s1-research/STAGE.md`，直接按里面的速查表定位文件，两个校验器跑一遍就是证据。不需要完整工作副本，也不需要先读 `docs/`。

要对外沟通的人，读 `docs/01-charter.md` 和 `docs/05-research-findings.md`，这两份不含内部过程。

## 文档写作规则

`tools/check_docs.py` 会强制检查，不合规就报错。

<!-- check-docs:off -->
1. 开头三行说清这份文件回答什么问题。
2. 不写"见第 X 节""参见附录""如前所述"。需要的信息就地写全。
3. 数字带出处，并标明是实测、文件事实还是推断。
4. 路径一律相对项目根，不写 `/Users/mac/...`。
<!-- check-docs:on -->
