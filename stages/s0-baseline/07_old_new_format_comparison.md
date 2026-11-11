# 旧新格式对照 R1

本文件重写第一轮的 07_old_new_format_comparison.md。
引擎文件按 inputs-readonly/02_ale，commit 73517c2eb097abe7974e9ec4de9819a02cd0ee81 引用。
旧引擎文件按 inputs-readonly/01_agents-last-exam，commit 2e91edd3cd26baa35a38127c90c8e5241dfbe62f 引用。
模板仓文件按 inputs-readonly/04_ale-tasks-base，commit 492249a2ca4b9d74efd3584a90399473c2e928c7 引用。
本机没有运行任何任务，全部结论来自静态读取与文本检索 [cmd]。

先列本版修正第一轮结论的四条。

- artifacts 是输出收集路径，不是输入清单 [code: taskspec.py:74-84]。
- 转换方向有两条引擎原文，一条写 ALE 到 Harbor，一条写 Harbor 到 ALE，引擎没有随快照发布转换器 [doc: task-authoring.md:9-14, code: taskspec.py:523-525]。
- inputFiles 字段有真实样例，形状是四项数组 [cmd: 读取 01 任务卡]。
- metadata 无结构但非完全无读取，lint 会读 network_justification 一个键 [doc: task-authoring.md:211]。

## 1. 必填字段与校验器

TaskConfig 的类文档串写明只有两个字段必填。

[doc: 02_ale/packages/ale-core/src/ale/core/taskspec.py:784-788]

```text
A Harbor field keeps Harbor's meaning. A field ALE adds sits in the Harbor table of what
it configures, under a name Harbor gives no other meaning. Only ``schema_version`` and
``[task].name`` are required.
```

字段定义与默认值如下。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:793-800]

```text
    schema_version: Literal["1.4+ale.1"]
    artifacts: tuple[Artifact, ...] = ()
    task: TaskTable
    metadata: dict[str, Any] = Field(default_factory=dict)
    environment: EnvironmentTable = EnvironmentTable()
    agent: AgentTable = AgentTable()
    verifier: VerifierTable = VerifierTable()
    solution: SolutionTable = SolutionTable()
```

schema_version 与 task 两个字段没有默认值，就是 Pydantic 的必填语义。
[task] 表里 name 没有默认值，其余四字段有默认值。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:567-577]

```text
class TaskTable(BaseModel):
    """``[task]``: the Task's identity; everything else here is descriptive."""

    model_config = _FROZEN

    name: TaskId
    description: str = ""
    version: str | None = Field(default=None, min_length=1)
    authors: tuple[Author, ...] = ()
    keywords: tuple[str, ...] = ()
```

解析入口用 Pydantic 校验读取到的 TOML。

[code: 02_ale/packages/ale-run/src/ale/run/tasksets/manifest.py:268]

```text
        config = TaskConfig.model_validate(_read_toml(path))
```

单元测试的最小合法任务与上文一致。

[code: 02_ale/tests/unit/test_contracts.py:104]

```text
        {"schema_version": "1.4+ale.1", "task": {"name": "org/demo"}}
```

schema_version 只接受字面量 1.4+ale.1。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:793]

```text
    schema_version: Literal["1.4+ale.1"]
```

常量注释说明这个值与纯 1.4 的关系，下一节转换方向再引。
结论 verdict 为 supported。解析层必填项就是 schema_version 与 [task].name 两个。
第一轮 07 第 26 行写这一条，方向正确，本版补齐上面四段引用。
目录层的必填文件是另一组，不属于校验器。作者规范列出六个文件。

[doc: 02_ale/docs/specs/task-authoring.md:36-43]

```text
Required files are `task.toml`, `instruction.md`, and the tests and solution entries for the
Task OS: `tests/test.sh` and `solution/solve.sh` on Linux and macOS, `test.ps1` and
`solve.ps1` on Windows.
```

引擎里对应的两个常量如下。

[code: 02_ale/packages/ale-run/src/ale/run/tasksets/manifest.py:42-43]

```text
TASK_CONFIG = "task.toml"
INSTRUCTION = "instruction.md"
```

required 与 optional 一览表。

| 字段 | 必填 | 默认值 | 证据 |
| --- | --- | --- | --- |
| schema_version | 是 | 无，只收 1.4+ale.1 | [code: taskspec.py:793] |
| [task].name | 是 | 无 | [code: taskspec.py:572] |
| artifacts | 否 | () | [code: taskspec.py:794] |
| [task] 其余 description version authors keywords | 否 | "" None () () | [code: taskspec.py:573-576] |
| [metadata] | 否 | {} | [code: taskspec.py:796] |
| [environment] [agent] [verifier] [solution] | 否 | 各自默认表 | [code: taskspec.py:797-800] |
| 目录文件 task.toml instruction.md tests 与 solution 条目 | 是，按任务 OS | 无 | [doc: task-authoring.md:36-43] |

## 2. metadata 的解析与运行时效果

声明有两处，与类文档串一致，是无结构字典。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:501]

```text
    metadata: dict[str, Any] = Field(default_factory=dict)
```

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:796]

```text
    metadata: dict[str, Any] = Field(default_factory=dict)
```

作者规范说它是无运行时行为的自由值，并列了一个取值范围。

[doc: 02_ale/docs/specs/task-authoring.md:67-68]

```text
[metadata]                                  # free-form values; no runtime behavior
network_justification = "the Task reads one publisher's live catalog"
```

全仓检索 metadata 键的读取位置，运行时只有一处，是把配置原样装进 TaskSpec 携带，不做解释。

[code: 02_ale/packages/ale-run/src/ale/run/tasksets/manifest.py:318]

```text
        metadata=config.metadata,
```

[cmd: grep metadata 到 02_ale/packages，运行时读取点仅上面一行]

其余命中是 metadata.json 文件名、importlib.metadata、容器镜像 metadata，均与 [metadata] 表无关 [cmd]。
唯一的静态读取点如下，public 网络模式要求写 network_justification。

[doc: 02_ale/docs/specs/task-authoring.md:211]

```text
`[agent].network_mode` ... `ale lint` requires `[metadata].network_justification` for `public`.
```

结论 verdict 为 largely supported。
metadata 本身无运行时语义成立，但要写明 lint 会读 network_justification 这一个键。
第一轮 07 第 25 行写无运行时效果，不够精确，本版补上 lint 例外。
第一轮 07 第 56 到 58 行写难度学科成本必须放引擎之外，本版修正为 metadata 可存任意键，引擎不解释。
运营侧要不要再登记一遍是流程决策，不是格式约束 [inference: metadata 是自由字典]。

## 3. 输入与输出三分法

三个概念容易混淆。旧格式的 inputFiles 是输入声明，新格式的大资产走 HF 资产机制，新格式的 artifacts 是输出收集路径。
逐个处理如下。

### 3.1 旧格式 inputFiles

真实样例在定价任务卡里。

[cmd: 读取 01_agents-last-exam/tasks/business_finance/american_option_pricing_ls/task_card.json，commit 2e91edd]

```json
"inputFiles": [
  {
    "name": "problem_spec.md",
    "format": "Markdown",
    "path": "input/problem_spec.md",
    "description": "Full public specification for the three-tier American option pricing benchmark."
  },
  {
    "name": "runtime_env/pyproject.toml",
    "format": "TOML",
    "path": "input/runtime_env/pyproject.toml",
    "description": "Pinned solve-time manifest for NumPy and SciPy."
  },
  {
    "name": "runtime_env/uv.lock",
    "format": "Lockfile",
    "path": "input/runtime_env/uv.lock",
    "description": "Pinned uv lockfile for the staged runtime."
  },
  {
    "name": "software/python.sh",
    "format": "Shell script",
    "path": "software/python.sh",
    "description": "Canonical agent-facing Python entry point for the staged runtime."
  }
]
```

形状是数组，元素含 name、format、path、description 四键，path 指向任务数据树内的相对位置 [code: 同上]。
任务卡顶层共 16 个键。

[cmd: python json 读取同一任务卡的顶层键]

```text
taskId title summary category software taskPrompt agentMustDo inputFiles
referenceFiles evaluation vm variants sourceSubmissionId taxonomy requiredSystemPackages
```

135 份任务卡里有 122 份声明了 inputFiles [cmd: grep -l 计数]。
本机没有运行旧引擎，输入文件实际如何拷进沙箱未在本轮验证 [unknown]。
旧侧有一个离线数据树 03_ale-data/task-data-v1.1，见 evidence/history-r0/DIRECTORY_SUMMARY_REPORT.md 第 55 到 57 行，这是记录文件不是运行证据 [doc: 原执行人的记录]。

### 3.2 新格式的大资产输入

大资产走 Hugging Face dataset 同步机制，入口模块声明如下。

[code: 02_ale/packages/ale-run/src/ale/run/assets.py:1]

```text
"""Synchronize Task-local assets with same-named Hugging Face datasets."""
```

资产只放在三个根下。资产根内的文件不进源码 digest。

[code: 02_ale/packages/ale-run/src/ale/run/assets.py:26-33]

```text
ASSET_ROOTS: tuple[str, ...] = (
    "environment/assets",
    "tests/assets",
    "solution/assets",
)
```

命名空间默认值如下，这就是任务书里查证的那一行。

[code: 02_ale/packages/ale-run/src/ale/run/assets.py:33-34]

```text
DEFAULT_NAMESPACE = "agents-last-exam"
```

```text
def asset_namespace() -> str:
```

拉取用 snapshot_download，按任务路径加资产根做 allow_patterns。

[code: 02_ale/packages/ale-run/src/ale/run/assets.py:151-189 节选]

```text
        remote_repo_id = asset_repo_id(selection.repository_name)
        ...
            snapshot_download(
                repo_id=remote_repo_id,
                token=hf_token(),
                repo_type="dataset",
                revision=commit,
                allow_patterns=[
                    f"{_task_path(task)}/{root}/**"
                    for task in selection.tasks
                    for root in ASSET_ROOTS
                ],
                local_dir=downloaded,
            )
```

资产规范点名这个命名空间的用途。

[doc: 02_ale/docs/specs/task-assets.md:57]

```text
namespace is `agents-last-exam` unless `ALE_ASSETS_NAMESPACE` names another organization
```

模板仓用自己的名字印证了同一机制。

[doc: 04_ale-tasks-base README.md，commit 492249a2]

```text
Large files live in `assets/` directories beside the files that read them ...
They are ignored by Git and synchronized with the
private Hugging Face dataset `agents-last-exam/ale-tasks-base`, which mirrors their paths.
```

用途分三类，环境资产给镜像构建读，测试资产给验证读，解题资产给 oracle 读。

[doc: 02_ale/docs/specs/task-assets.md:9-12]

```text
three roots ALE recognizes ... files read while the image is built ... while it is verified ...
while the solver is run
```

运行一个任务从不隐式下载资产，下载是显式的资产同步动作。

[doc: 02_ale/docs/specs/task-assets.md:21]

```text
Running a Task never implicitly downloads assets.
```

小的输入另有两条路。镜像内的固定文件由 environment/ 构建读入，每集初始化用 setup 脚本。

[doc: 02_ale/docs/specs/task-authoring.md:362-372, 会话初始脚本永久不参与镜像]

第一轮 07 第 32 行写agents-last-exam 是资产命名空间，方向正确，本版补上用途与拉取机制。
第一轮 07 第 75 行把容器内固定卷列为去向之一，本版修正为镜像内文件加 setup 脚本，不叫固定卷 [doc: task-authoring.md:362-372]。

### 3.3 artifacts 的输出收集语义

artifacts 声明输出收集路径。字符串是路径或 glob，相对路径以 agent 起始目录为基准。
表形式多一个 exclude，用 tar --exclude 规则。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:74-84]

```text
class Artifact(BaseModel):
    """One ``artifacts`` entry: a path or glob, below where the agent starts when relative.

    A plain string when nothing is left out. ``exclude`` takes ``tar --exclude`` patterns, as
    in Harbor: they match after any ``/``, so ``.venv`` is that name at any depth.
    """

    source: str = Field(min_length=1)
    exclude: tuple[str, ...] = ()
```

作者规范直接标 outcome paths，即输出路径。

[doc: 02_ale/docs/specs/task-authoring.md:53-58]

```text
artifacts = [                               # outcome paths
  "output",                                 # below where the agent starts
  "/home/user/games/*.sgf",
  { source = "/srv/app", exclude = [".venv", "*.pyc"] },
]
```

指令要求交付的文件必须落在声明的 artifacts 内。

[doc: 02_ale/docs/specs/task-authoring.md:158-160]

```text
When the instruction requires deliverable files, every instructed destination must equal or be
contained by a declared `artifacts` path, or matched by a declared glob.
```

运行侧对产物的处理在配置层定义。collect=host 才保留到宿主机，默认 none 不保留。

[code: 02_ale/packages/ale-core/src/ale/core/config.py:105-117 节选]

```text
class ArtifactPolicy(BaseModel):
    """What happens to the paths a task declared as its output, ...
    collect: Literal["host", "none"] = "none"
```

默认不收集这一句是输出收集语义的精确边界 [code: 同上]。
结论如下。

- artifacts 不声明输入 [code: taskspec.py:74-84]。
- artifacts 声明从某处收集哪些路径，语义是输出收集 [doc: task-authoring.md:53-58]。
- 未声明的不收集，声明了还要运行侧 collect=host 才落宿主机 [code: config.py:105-117]。
- 第一轮 07 第 20 行把 artifacts 当输入清单的对应物，属于错误，本版已纠正。

## 4. 转换方向

### 4.1 引擎原文

作者规范里唯一的格式转换句子如下。

[doc: 02_ale/docs/specs/task-authoring.md:9-14]

```text
The format is Harbor's (`task.toml` schema 1.4, `environment/`, `tests/`, `solution/`): a
field ALE implements as Harbor does keeps Harbor's name, table and meaning. A field ALE adds
sits in the Harbor table of what it configures, under a name Harbor gives no other meaning:
a separate namespace would not stop one name meaning two things, and would have to mirror every
table it extends. ALE runs Tasks in its own runtime and a Task reaches Harbor through a
conversion, so `schema_version = "1.4+ale.1"` marks the file as ALE's.
```

方向一的原文是 ALE 任务通过一次 conversion 到达 Harbor [doc: 同上第 13 行]。
常量注释写的是这条关系的另一面。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:523-525]

```text
#: The ``task.toml`` schema ALE reads: revision 1 of ALE's fields on Harbor's schema 1.4. Plain
#: ``1.4`` is a Harbor file, which a conversion turns into this one.
SCHEMA_VERSION = "1.4+ale.1"
```

方向二的原文是纯 1.4 是 Harbor 文件，一次 conversion 把它变成 ALE 这一版 [code: 同上第 524 到 525 行]。
两条原文描述的是同一个 Harbor 1.4 与 ALE 1.4+ale.1 之间的双向转换关系，句子视角不同 [inference: 两段引用合读]。
文档真正承诺的是格式层面的转换存在，引擎快照没有随附任何转换器。

[cmd: 02_ale 全仓检索 convert 命令与转换器模块，零命中]

CLI 顶层命令是 assets、vm-image、sandbox、new-task 与 run 系列，没有 convert。

[code: 02_ale/packages/ale-run/src/ale/run/cli/main.py:48-54, 291]

verdict 为 partially supported。
第一轮 07 第 65 行写规范承诺 Harbor 到 ALE 的转换器，方向说对了一半。
原文语句写 ALE 到 Harbor，常量注释写 Harbor 到 ALE，两句话都要引用。
转换器本身没有发布，第一轮写没有随引擎发布，这一条成立。
原执行人的 02_ale 笔记第 210 行也留了同一疑问 [doc: evidence/notes/02_ale.md:210, 历史记录]。

### 4.2 三条链分开

#### 链一 旧 ALE 迁移

旧引擎任务包，即 main.py 加 task_card.json 加 scripts/ 的结构 [code: 01 任务卡与目录，见第 3 节]。
旧仓有未合并的 feat/tasks-v2 分支，提交号为 783b93ab969e0298014e4996c86d025302ee21ba。

[cmd: 读取 01_agents-last-exam/.git/packed-refs 第 31 行，commit 2e91edd]

原执行人记录了这个分支的预览内容与提交信息。

[doc: evidence/notes/01_agents-last-exam.md:208, 原执行人的历史记录]

```text
A v2 format experiment exists. Branch remotes/origin/feat/tasks-v2 is unmerged. For demo/hello
it adds instruction.md, setup/run.sh, verify/run.sh, oracle/run.sh and task.yaml beside the old
pair. Its commits read "rebuild demo/hello against the published data", "declare data inline,
create what you need", "artifacts are paths".
```

这条分支内容没有检出到工作区，我只验证了 ref 存在，文件级内容以上述记录为准 [cmd + doc: 记录]。
01 主分支没有 convert 命令，原执行人做过历史扫查，结论是没有过 [doc: evidence/notes/01_agents-last-exam.md:196]。
迁移目标格式是 02 引擎的 task.toml，这是原执行人的推断，见其笔记第 210 行 [doc: 历史记录，inference 归属原执行人]。
分支只到旧仓自己的 task.yaml，与新引擎的 task.toml 不是同一文件，本版单列以分清 [inference: 两个文件名不同]。
结论如下。旧到新的迁移有分支预览证据，成熟转换器没有发布，两件事分开记 [code + doc]。
第一轮 07 第 64 行写检视分支建议，方向正确，本版补上 ref 提交号。

#### 链二 Harbor 转换

见第 4.1 节引擎原文。这条链只涉及 Harbor schema 1.4 与 ALE schema 1.4+ale.1 的格式转换。
04 模板仓的 README 第一句自述其格式就是 Harbor 布局加 ALE 扩展，印证了这条链的产物形态。

[doc: 04_ale-tasks-base README.md, commit 492249a2]

```text
Reference collection of independent container and VM Tasks in ALE's `task.toml` format:
Harbor's Task layout and fields, with ALE's additions in the Harbor tables they configure.
```

旧官方主仓 tasks/ 里的 main.py 结构不是 Harbor 格式，不在这一条链的输入侧 [inference: 文件形状不同]。

#### 链三 专家 Canonical Source

这是 R1 任务书确认的项目前提，不是格式迁移。

[doc: R1 brief 前提]

- 最终 500 个任务是专家在平台上新产出的，不走官方任务的转格式复制。
- 官方任务与官方数据是研究与对齐的参考，不自动计入 500。
- Canonical Source 是专家新生产的规范源，不是官方 01 或 03 任务的副本。

## 5. 对比表

每个单元格带证据类。旧侧文件按 01 commit 2e91edd，新侧按 02 commit 73517c2 与 04 commit 492249a2。

### 5.1 包结构

| 维度 | 旧格式 | 新格式 |
| --- | --- | --- |
| 包形态 | 每任务目录主件 main.py 与 task_card.json，另配 scripts/ [cmd: ls 任务目录] | 目录级必填 task.toml、instruction.md、tests 与 solution 条目，加 environment/ [doc: task-authoring.md:36-43] |
| 实例证据 | tasks/business_finance/american_option_pricing_ls/ 只有 main.py、scripts/、task_card.json [cmd] | 04_ale-tasks-base/tasks/ 下 demo 与 example_task [cmd: ls]，README 给了目录形状 |
| 声明文件 | task_card.json，顶层 16 个键 [cmd] | task.toml，schema_version 只收 1.4+ale.1 [code: taskspec.py:793] |
| 离仓数据 | 03_ale-data/task-data-v1.1 子树，79,070 个文件 [doc: evidence/history-r0/DIRECTORY_SUMMARY_REPORT.md:23] | 大文件进 assets 三根，由 HF dataset 同步 [code: assets.py:26-33] |

修正点。第一轮写脚本目录评分器，原样例里 scripts/ 的作用未本轮验证，本表只写目录事实 [cmd]。
第一轮写 task.toml 是唯一声明文件，本版改为目录级必填文件一组，instruction.md 不叫声明文件 [doc: task-authoring.md:36-43]。

### 5.2 声明字段

| 维度 | 旧 task_card.json | 新 task.toml |
| --- | --- | --- |
| 身份 | taskId 如 business_finance/american_option_pricing_ls，加 title summary category software [cmd] | [task].name 必填，description version authors keywords 可选 [code: taskspec.py:567-577] |
| 提示语 | taskPrompt 一段加 agentMustDo 数组 [cmd] | instruction.md 单文件 [doc: task-authoring.md:36-43] |
| 输入清单 | inputFiles 数组，元素 name format path description [code: 任务卡] | 无输入清单字段，输入走镜像文件、setup 脚本与 HF 资产 [code: assets.py, doc: task-authoring.md:362-372] |
| 输出清单 | 无对应字段 [cmd: 顶层键列表] | artifacts 数组，声明输出收集路径 [code: taskspec.py:74-84] |
| 运行环境 | vm.machineType、vm.snapshot、vm.timeout 等 [cmd: 任务卡 vm 键] | [environment] 加 [agent] 表，字段见作者规范 [doc: task-authoring.md] |
| 验证控制 | evaluation 描述文字 [cmd: 任务卡 evaluation 键] | [verifier] 表加 tests/ 目录 [doc: task-authoring.md:414-427] |
| 自由扩展 | 无 | [metadata] 自由字典，lint 读 network_justification [code: taskspec.py:796, doc: task-authoring.md:211] |
| 必填集 | 无同构校验器证据 [unknown] | 解析层只有 schema_version 与 [task].name [code: taskspec.py:793,572] |

### 5.3 输入交付

| 维度 | 旧格式 | 新格式 |
| --- | --- | --- |
| 声明 | inputFiles 数组带相对路径 [code: 任务卡] | task.toml 不声明资产，资产按目录约定放三根 [code: assets.py:26-33] |
| 数据位置 | 数据树 task-data-v1.1 内 input/ 等目录，镜像烘培或归档 [doc: evidence/history-r0/DIRECTORY_SUMMARY_REPORT.md:55-57, 原执行人记录] | HF dataset agents-last-exam 命名空间，加环境变量覆盖 ALE_ASSETS_NAMESPACE [code: assets.py:33,258-260] |
| 下载时机 | 未在本机验证 [unknown] | 运行任务从不隐式下载，显式同步才拉 [doc: task-assets.md:21] |
| 小输入 | 无 | 镜像内固定文件，加每集 setup 脚本 [doc: task-authoring.md:362-372] |
| 模板仓佐证 | 无 | 04 README 写明私有 dataset agents-last-exam/ale-tasks-base 镜像路径 [doc: 04 README] |

### 5.4 Agent 钩子

| 维度 | 旧格式 | 新格式 |
| --- | --- | --- |
| 代码钩子 | main.py 为主件 [cmd: ls 任务目录]；原执行人笔记写 cua-bench 风格装配 [doc: evidence/notes/01_agents-last-exam.md:200, 历史记录] | 任务内无代码钩子，agent 由 [agent] 表与 instruction.md 指导 [doc: task-authoring.md] |
| 提示与必做 | taskPrompt 加 agentMustDo [cmd] | instruction.md 正文 [doc: task-authoring.md:36-43] |
| 模型链路 | 未在本轮查证 [unknown] | 宿主机持键，沙箱只收 Gateway token [doc: .env.example:1-3] |
| 网络 | 未见统一默认证据 [unknown] | no-network 默认，allowlist 与 public 可选 [code: taskspec.py:696] |

修正点。第一轮写 taskPrompt 与 agentMustDo 是两条字段，本版已核实为真实键 [cmd]。
第一轮写旧侧无显式 agent 表，本版保留但同时标出旧侧 agent 配置另有实验 yaml，原执行人笔记第 190 行有凭证，见 ep_assessment 笔记 [doc: 历史记录]。

### 5.5 验证

| 维度 | 旧格式 | 新格式 |
| --- | --- | --- |
| 评分实现 | scripts/ 目录存在，内部评分器行为未本轮验证 [cmd + unknown] | tests/test.sh 或 test.ps1 驱动，写 reward.json [doc: task-authoring.md:414-418] |
| 产物 | 样例卡文本写 results.json 与 .npy [cmd: evaluation 内容] | reward 在 0 到 1，保留两位小数，半整进位 [code: ale_verify/__init__.py:114-132] |
| 结果路径 | 未在快照内查到统一机读产物定义 [unknown] | /logs/verifier/reward.json，Windows 与 macOS 各有路径 [doc: task-authoring.md:414-427] |
| 准入 | 未验证 [unknown] | validate 要求全新零分通过与满分 oracle 通过，两次都用干净沙箱 [doc: 原执行人笔记 evidence/notes/02_ale.md, 历史记录] |
| 形状 | evaluation 字段是文字评分说明 [cmd] | reward.json 是运行期产物不在仓库内，是扁平数字对象，reward 0 到 1 [code: ale_verify/__init__.py:114-132] |

## 6. 元数据缺口

新 TaskConfig 没有 id、template_id、family、requires、experiments、difficulty、subject、cost 这些字段 [code: taskspec.py:783-800]。
旧格式实际键是 taskId、title、summary、category、software 等 16 键 [cmd]。
后果如下。

- 新格式不存在这些键，不存在这一点是代码事实 [code]。
- 需要分类信息时 metadata 可以放任意键，引擎不解释 [code: taskspec.py:796]。
- 要把官网分类与运营字段登记在 metadata 还是另外登记册，是平台侧流程决策，格式层都允许 [inference]。
- differentiation 与五档难度这类运营信息在本快照没有出处 [unknown]。

第一轮 07 第 56 到 60 行的三段推断按上面四条修正。
第一轮写必须放引擎之外，本版改为可以放 metadata，也可以外部登记。

## 7. 转换面

- 旧仓 feat/tasks-v2 分支存在，ref 在 .git/packed-refs 第 31 行，提交 783b93ab [cmd]。
- 该分支预览内容引用原执行人笔记第 208 行，本工作区未检出该分支 [doc: 历史记录]。
- 新引擎快照没有转换器命令也没有转换器模块 [cmd: 全仓检索]。
- 旧引擎的 build、push、convert 界面属于私有仓 AgentHLE，不在本快照内，这一条沿用原执行人记录 [doc: evidence/notes/01_agents-last-exam.md]。
- 从旧到新重做部分的对照沿用第一轮表格的行结构，但输入输出两格按第 3 节修正。

| 资产 | 旧侧来源 | 新侧去向 |
| --- | --- | --- |
| 任务提示 | taskPrompt 与 agentMustDo [cmd] | instruction.md [doc: task-authoring.md:36-43] |
| 装配逻辑 | main.py 装配类 [cmd: ls] | environment/ 加 setup/ [doc: task-authoring.md:278-372] |
| 评分逻辑 | scripts/ 评分器 [cmd: ls] | tests/ 目录 [doc: task-authoring.md:414-427] |
| 运行参数 | task_card.json 的 vm 键 [cmd] | [environment] 与 [agent] 表 [doc: task-authoring.md] |
| 隐藏输入体 | 数据树与归档，烘进镜像 [doc: 原执行人记录] | HF 资产命名空间 agents-last-exam 或镜像内文件加 setup [code: assets.py:33, doc: task-authoring.md:362-372] |

## 8. 证据质量说明

本文件没有运行任何引擎或任务，全部是静态读取与文本检索 [cmd]。
历史记录类证据全部点名了记录人与出处。
01、02、04 三个仓的 commit 号在文件头。
03 的数据树只引用原执行人的目录报告，本轮没有展开核对 [cmd 范围声明]。