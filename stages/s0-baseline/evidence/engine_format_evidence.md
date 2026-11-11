# 引擎格式证据 R1

本文件是 06 与 07 两份修订文件每一处承重断言的引用底座。
本文件同时充当 R10 合规件。
引擎路径全部相对 inputs-readonly/，引擎 commit 为 73517c2eb097abe7974e9ec4de9819a02cd0ee81。
本轮没有执行任何代码与任务，全部取证为静态读取与文本检索，命令见 r1_engine_notes.md。

## task.toml 校验器与必填字段

断言如下。新格式只有 schema_version 与 [task].name 必填，其余字段全部有默认值。
先看 TaskConfig 自身文档串的声明。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:783-788]

```text
class TaskConfig(BaseModel):
    """The strict authored shape of ``task.toml``.

    A Harbor field keeps Harbor's meaning. A field ALE adds sits in the Harbor table of what
    it configures, under a name Harbor gives no other meaning. Only ``schema_version`` and
    ``[task].name`` are required.
```

字段定义如下。

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

校验器视角如下。schema_version 与 task 两字段没有默认值，其余六字段都有默认值。
[task] 表内部只有 name 没有默认值，其余四字段全部有默认值。

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

因此解析层面的必填项恰好是 schema_version 与 [task].name 两个，与文档串一致。
解析入口如下。

[code: 02_ale/packages/ale-run/src/ale/run/tasksets/manifest.py:268]

```text
        config = TaskConfig.model_validate(_read_toml(path))
```

另有单元测试用最小两字段任务验证这一点。

[code: 02_ale/tests/unit/test_contracts.py:104]

```text
        {"schema_version": "1.4+ale.1", "task": {"name": "org/demo"}}
```

结论 verdict 为 supported。
第一轮 07 文件写只有 schema_version 与任务名必填，与本证据一致，无需修正。
注意区分两层。解析层必填只有上述两项。目录层必填文件另有一组，见下一条。

## 目录层必填文件

任务目录要求的文件不在 task.toml 校验器里，而在作者契约里。

[doc: 02_ale/docs/specs/task-authoring.md:36-43]

```text
Required files are `task.toml`, `instruction.md`, and the tests and solution entries for the
Task OS: `tests/test.sh` and `solution/solve.sh` on Linux and macOS, `test.ps1` and
`solve.ps1` on Windows.
```

constants 如下。

[code: 02_ale/packages/ale-run/src/ale/run/tasksets/manifest.py:42-43]

```text
TASK_CONFIG = "task.toml"
INSTRUCTION = "instruction.md"
```

结论 verdict 为 supported。
这是一个 07 表格里配置模型必填的补充维度，R1 修订版单独列出。

## schema_version 字面量

任务要求的字面量是 1.4+ale.1，常量与校验器一致。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:523-525]

```text
#: The ``task.toml`` schema ALE reads: revision 1 of ALE's fields on Harbor's schema 1.4. Plain
#: ``1.4`` is a Harbor file, which a conversion turns into this one.
SCHEMA_VERSION = "1.4+ale.1"
```

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:793]

```text
    schema_version: Literal["1.4+ale.1"]
```

结论 verdict 为 supported。
第一轮写 1.4+ale.1 正确，无需修正。
上面常量注释同时是转换方向的证据，见后文转换方向条目。

## metadata 解析与运行时效果

metadata 是自由格式字典，两个位置各声明一次，都没有结构约束。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:501]

```text
    metadata: dict[str, Any] = Field(default_factory=dict)
```

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:796]

```text
    metadata: dict[str, Any] = Field(default_factory=dict)
```

作者契约的说法如下。

[doc: 02_ale/docs/specs/task-authoring.md:67-68]

```text
[metadata]                                  # free-form values; no runtime behavior
network_justification = "the Task reads one publisher's live catalog"
```

全仓检索结果如下。metadata 键出现在任务运行时的地方只有一处，是把配置里的 metadata 原样放进 TaskSpec 供携带，不做解释。

[code: 02_ale/packages/ale-run/src/ale/run/tasksets/manifest.py:318]

```text
        metadata=config.metadata,
```

[cmd: grep metadata 到 packages/*/src]

其余命中全部是无关的 metadata.json 文件处理、importlib.metadata、容器镜像 metadata，没有一处读取 [metadata] 表内容驱动运行行为。
唯一例外在 lint 层。作者的契约说 public 模式必须写 metadata.network_justification。

[doc: 02_ale/docs/specs/task-authoring.md:211]

```text
`[agent].network_mode` ... `ale lint` requires `[metadata].network_justification` for `public`.
```

另一处相关表述写 metadata 是来源信息的归属地。

[doc: 02_ale/docs/specs/task-authoring.md:135-136]

```text
ALE keeps its copies in an inventory of its own, so an artifact has no `destination`. An origin
belongs in `[metadata]`, so there is no `source`.
```

结论 verdict 为 largely supported。
具体说，metadata 本身无运行时语义这一点成立。但要写明一处边界，就是 ale lint 会读 network_justification 这一键做静态检查。第一轮 07 写 metadata 无运行时效果，方向正确但不够精确。R1 修订版补上 lint 例外。
metadata 可选。任务存难度、学科、成本这类分类信息可以放 metadata，但引擎不解释这些键。

## artifacts 的语义

artifacts 声明的是输出收集路径，不是输入清单。
三种形状如下。字符串是路径或 glob，相对路径以 agent 起始目录为基准。表形式加 exclude，按 tar --exclude 规则匹配。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:74-84]

```text
class Artifact(BaseModel):
    """One ``artifacts`` entry: a path or glob, below where the agent starts when relative.

    A plain string when nothing is left out. ``exclude`` takes ``tar --exclude`` patterns, as
    in Harbor: they match after any ``/``, so ``.venv`` is that name at any depth.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: str = Field(min_length=1)
    exclude: tuple[str, ...] = ()
```

路径校验如下。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:94-100]

```text
def _validate_artifact_paths(
    artifacts: tuple[Artifact, ...], operating_system: OperatingSystem
) -> None:
    for artifact in artifacts:
        path = _task_path(artifact.source, operating_system)
        if ".." in path.parts or (path.is_absolute() and path == path.parent):
            raise ValueError("artifact paths must not be filesystem roots or contain '..'")
```

作者契约的标注直接写 outcome paths。

[doc: 02_ale/docs/specs/task-authoring.md:53-58]

```text
schema_version = "1.4+ale.1"                # required; exactly this
artifacts = [                               # outcome paths
  "output",                                 # below where the agent starts
  "/home/user/games/*.sgf",
  { source = "/srv/app", exclude = [".venv", "*.pyc"] },
]
```

指令的交付物必须落在声明的 artifacts 里，这是输出侧的强证据。

[doc: 02_ale/docs/specs/task-authoring.md:158-160]

```text
When the instruction requires deliverable files, every instructed destination must equal or be
contained by a declared `artifacts` path, or matched by a declared glob.
```

运行侧配置 confirm 这是输出收集策略。collect 取 host 时留下副本，默认 none 不保留。

[code: 02_ale/packages/ale-core/src/ale/core/config.py:105-117]

```text
class ArtifactPolicy(BaseModel):
    """What happens to the paths a task declared as its output.
    ...
    collect: Literal["host", "none"] = "none"
```

不支持的两个 Harbor artifact 键也被逐出，一个 artifact 只有一个 source。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:819-825]

```text
        artifacts = data.get("artifacts")
        for item in artifacts if isinstance(artifacts, list) else ():
            if isinstance(item, dict):
                unsupported.extend(
                    f"artifact {key} is not supported by ALE"
                    for key in sorted({"destination", "service"} & item.keys())
                )
```

结论 verdict 如下。artifacts 是输出收集声明，这一点无疑。第一轮 07 把 artifacts 当作 inputFiles 的新格式对应物，属于错误，R1 修订版必须改成输出收集语义。新格式没有 inputFiles 字段，输入投递走另一条机制，见资产条目。

## 沙箱 provider 的四个声明文件

四个 provider 各自一个模块，在 providers 包内。

[code: 02_ale/packages/ale-run/src/ale/run/providers/README.md:5-8]

```text
| Module | Backend | Prepared input |
|---|---|---|
| `docker.py` | local Docker container | immutable OCI image identity |
| `qemu.py` | QEMU/KVM guest runner | materialized qcow2 identity |
| `daytona.py` | Daytona cloud container | immutable OCI image identity, pushed by digest |
| `orchard.py` | macOS VM on Orchard/Tart | digest-pinned OCI image, or a local image `build.sh` built |
```

注册表的选择逻辑如下。macOS VM 无条件走 Orchard，容器按配置走 daytona 或 docker，其余 VM 走 qemu。

[code: 02_ale/packages/ale-run/src/ale/run/providers/__init__.py:20-58]

```text
class ProviderRegistry:
    """Lazily construct and reuse the configured Provider for each image kind.

    macOS VMs have one Provider, the local Orchard, so they are not configured.
    """
    ...
    def get(self, kind: ImageKind, operating_system: OperatingSystem) -> Provider:
        macos = kind is ImageKind.VM and operating_system is OperatingSystem.MACOS
        ...
        if macos:
            provider: Provider = OrchardProvider()
        elif kind is ImageKind.CONTAINER:
            config = self.settings.container
            if config.provider == "daytona":
                provider = DaytonaProvider(config.daytona)
            else:
                provider = DockerProvider(gpus=config.gpus)
        else:
            provider = QemuProvider()
```

运行配置把 provider 选择固定为字面量。容器只有 docker 与 daytona，VM 只有 qemu。

[code: 02_ale/packages/ale-core/src/ale/core/config.py:257-281]

```text
class ContainerProviderConfig(BaseModel):
    ...
    provider: Literal["docker", "daytona"] = "docker"
    gpus: tuple[Annotated[int, Field(ge=0, strict=True)], ...] = ()
    ...
class VmProviderConfig(BaseModel):
    ...
    provider: Literal["qemu"] = "qemu"
```

RETAINING_PROVIDERS 只有 docker、qemu、daytona 三个。

[code: 02_ale/packages/ale-run/src/ale/run/providers/__init__.py:16]

```text
RETAINING_PROVIDERS = ("docker", "qemu", "daytona")
```

结论 verdict 为 supported。
第一轮 06 写四个 provider 的存在与归属文件正确。

## docker provider 对宿主的要求

docker provider 要求宿主机有 docker 命令且 daemon 可达。

[code: 02_ale/packages/ale-run/src/ale/run/providers/docker.py:483-488]

```text
    async def preflight(self) -> None:
        if shutil.which("docker") is None:
            raise ProviderStartError("docker is not installed — see `just doctor`")
        code, _, stderr = await _docker("info", "--format", "{{.ServerVersion}}", timeout=30)
        if code != 0:
            raise ProviderStartError(f"docker daemon unreachable: {stderr.strip()}")
```

GPU 时通过 nvidia-smi 读取宿主 GPU 并租用。

[code: 02_ale/packages/ale-run/src/ale/run/providers/README.md:76-78]

```text
| Docker | Reads the Host's GPUs with `nvidia-smi` and leases only those among `container.gpus`,
or among all when it is unset, of an accepted model.
```

结论 verdict 为 supported。
docker 是本地 Linux 容器路径。

## daytona provider 对宿主的要求

daytona 是云端容器后端，标题行直接写明。

[code: 02_ale/packages/ale-run/src/ale/run/providers/daytona.py:1]

```text
"""Daytona container Provider: Linux sandboxes on Daytona's cloud.
```

本地只需两个工具，认证靠云 API key。

[code: 02_ale/packages/ale-run/src/ale/run/providers/daytona.py:654-667]

```text
    async def preflight(self) -> None:
        for tool, why in (("docker", "builds and pushes the image"), ("ssh", "reaches guestd")):
            if shutil.which(tool) is None:
                raise ProviderStartError(f"{tool} is not installed; Daytona needs it, it {why}")
        try:
            await self._api.request("GET", "/sandbox", params={"limit": 1})
        except DaytonaError as exc:
            if exc.status in {401, 403}:
                raise ProviderStartError(
                    f"Daytona rejected the API key in {self.config.api_key_env}: {exc.reason}"
                ) from exc
```

key 变量名与区域默认值在配置里。

[code: 02_ale/packages/ale-core/src/ale/core/config.py:242-254]

```text
class DaytonaProviderConfig(BaseModel):
    ...
    target: str = Field(default="us", min_length=1)
    """The Daytona region sandboxes are created in."""
    api_key_env: str = Field(default="ALE_DAYTONA_API_KEY", pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    ...
    lifetime_hours: int = Field(default=24, ge=1, le=720, strict=True)
```

结论 verdict 为 supported。
daytona 是 Linux 容器路径的云端变体，不是本地 VM。

## qemu provider 对宿主的要求

qemu 模块头写明主机只需要 Docker 与 /dev/kvm。

[code: 02_ale/packages/ale-run/src/ale/run/providers/qemu.py:11-14]

```text
  rather than running ``qemu-system-x86_64`` on the
  host, a runner image holds it — the same one the previous framework used, which already
  solves the parts that are tedious and easy to get subtly wrong:
  ...
  outliving it. It also means the host needs nothing installed but Docker and ``/dev/kvm``.
```

preflight 对 /dev/kvm 的检查原文如下。

[code: 02_ale/packages/ale-run/src/ale/run/providers/qemu.py:703-726]

```text
    async def preflight(self) -> None:
        """Fail early and specifically, before anything is provisioned."""
        problems: list[str] = []

        if shutil.which("docker") is None:
            problems.append("docker is not on PATH; the runner image is what holds qemu")
        if shutil.which("qemu-img") is None:
            problems.append("qemu-img is not on PATH (apt install qemu-utils)")
        if not Path("/dev/kvm").exists():
            problems.append(
                "/dev/kvm is missing: this host has no hardware virtualisation, so the "
                "container backend is the usable one here"
            )
        elif not os.access("/dev/kvm", os.R_OK | os.W_OK):
            problems.append("/dev/kvm is present but not writable (add yourself to the kvm group)")
```

runner 容器挂载设备如下。

[code: 02_ale/packages/ale-run/src/ale/run/providers/qemu.py:944]

```text
            "--device=/dev/kvm",
```

README 的实测段落直接以主机条件开头。

[code: 02_ale/packages/ale-run/src/ale/run/providers/README.md:187]

```text
Measured on a KVM host:
```

测试标记同样写明 VM 工作要硬件虚拟化。

[code: 02_ale/pyproject.toml:58-59]

```text
    "needs_kvm: VM work: requires hardware virtualisation (/dev/kvm) or builds VM disks",
```

qemu 头写明它运行 Windows guest，macOS guest 留给 Orchard。

[code: 02_ale/packages/ale-run/src/ale/run/providers/qemu.py:6-8]

```text
It also runs Windows guests; macOS guests
run on the Orchard Provider, since only a Mac may host them.
```

结论 verdict 为 supported。
/dev/kvm 是 qemu provider 前台检查的硬条件，缺它时 provider 在 provision 前失败。
嵌套虚拟化方面引擎没有任何声明。

[cmd: grep 嵌套与 nested 到 packages、images、docs，无一条命中嵌套虚拟化概念]

引擎没有说 /dev/kvm 可以从嵌套环境获得，也没有说不可以。这一组合属于 [unknown]。
当前 Tencent Cloud Linux 服务器不能嵌套虚拟化是 R1 任务书确认的前提，而非引擎声明，见 06 的宿主层写法。

## 模型 provider 的八个字面量与方言

八个模型 provider 字面量在 config.py 一行给出。

[code: 02_ale/packages/ale-core/src/ale/core/config.py:155-158]

```text
#: The model vendor whose API the Gateway or a Judge calls. Not a sandbox Provider.
ModelProvider = Literal["anthropic", "gemini", "meta", "moonshot", "openai", "qwen", "xai", "zai"]
#: A protocol the Gateway serves to the Sandbox and speaks to the provider.
Dialect = Literal["anthropic", "gemini", "openai-chat-completions", "openai-responses"]
```

四个方言字面量。键与端点的机制在 GatewayConfig 字段说明里。

[code: 02_ale/packages/ale-core/src/ale/core/config.py:166-172]

```text
    provider: ModelProvider = Field(
        default="anthropic",
        description=(
            "Whose API the Gateway calls. Its key is ALE_<PROVIDER>_API_KEY and its "
            "endpoint ALE_<PROVIDER>_BASE_URL, or the provider's own API when that is unset."
        ),
    )
```

.env.example 逐 provider 列出键与默认端点。

[code: 02_ale/.env.example:7-24]

```text
# One key per model provider. ALE_<PROVIDER>_BASE_URL is optional and defaults to the
# provider's own API; a provider's key is only ever sent to its own URL.
ALE_ANTHROPIC_API_KEY=
# ALE_ANTHROPIC_BASE_URL=https://api.anthropic.com
ALE_GEMINI_API_KEY=
# ALE_GEMINI_BASE_URL=https://generativelanguage.googleapis.com
ALE_META_API_KEY=
# ALE_META_BASE_URL=https://api.meta.ai
ALE_MOONSHOT_API_KEY=
# ALE_MOONSHOT_BASE_URL=https://api.moonshot.ai
ALE_OPENAI_API_KEY=
# ALE_OPENAI_BASE_URL=https://api.openai.com
ALE_QWEN_API_KEY=
# ALE_QWEN_BASE_URL=https://maas.qwencloudapi.com/compatible-mode
ALE_XAI_API_KEY=
# ALE_XAI_BASE_URL=https://api.x.ai
ALE_ZAI_API_KEY=
# ALE_ZAI_BASE_URL=https://api.z.ai/api/anthropic
```

沙箱内模型流量凭证走 Gateway。任务沙箱收到的是 episode Gateway token，不是任何 provider 键。

[doc: 02_ale/.env.example:1-3]

```text
# Copy to .env and fill only the credentials used by this checkout.
# Values stay on the Host; Task Sandboxes receive an episode Gateway token and the
# variables a Task's env tables name (see docs/specs/task-authoring.md#variables).
```

结论 verdict 为 supported。
第一轮写八个 provider 与 ALE_ 前缀机制正确。
R1 任务书要求模型 provider 与沙箱 provider 分开表述，config.py:155 的注释本身就是引擎侧的分隔证据。
选哪一家没有定，是 open decision，R1 修订版只列出字面量，不挑 vendor。

## 资产命名空间与输入投递机制

新格式的大资产投递机制是 Hugging Face dataset 同步，不是 task.toml 的 inputFiles。
资产根固定三个。资产根内的文件不进源码 digest，有独立 commit 身份。

[code: 02_ale/packages/ale-run/src/ale/run/assets.py:26-33]

```text
#: Where a Task keeps assets, relative to its folder: beside the files that read them.
#: The Task loader leaves them out of source digests, so it imports this list from here.
ASSET_ROOTS: tuple[str, ...] = (
    "environment/assets",
    "tests/assets",
    "solution/assets",
)
DEFAULT_NAMESPACE = "agents-last-exam"
```

模块自己的说明如下。

[code: 02_ale/packages/ale-run/src/ale/run/assets.py:1]

```text
"""Synchronize Task-local assets with same-named Hugging Face datasets."""
```

命名空间默认 agents-last-exam，环境变量可覆盖。

[code: 02_ale/packages/ale-run/src/ale/run/assets.py:258-264]

```text
def asset_namespace() -> str:
    """The Hugging Face organization or user that owns asset datasets and their collection."""
    return os.environ.get("ALE_ASSETS_NAMESPACE", "").strip() or DEFAULT_NAMESPACE


def asset_repo_id(repository_name: str) -> str:
    return f"{asset_namespace()}/{repository_name}"
```

拉取路径用 snapshot_download，按任务路径加资产根的 allow_patterns 取回。

[code: 02_ale/packages/ale-run/src/ale/run/assets.py:151-189]

```text
def pull_assets(...)
    ...
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

资产规格文档确认命名空间与下载语义。

[doc: 02_ale/docs/specs/task-assets.md:57]

```text
namespace is `agents-last-exam` unless `ALE_ASSETS_NAMESPACE` names another organization
```

[doc: 02_ale/docs/specs/task-assets.md:21]

```text
Running a Task never implicitly downloads assets.
```

结论 verdict 为 supported，同时修正第一轮 07 的一个表述。
agents-last-exam 是资产 dataset 的 HF namespace，是这个同步机制的默认归属组织。
它不是任务目录规则，也不是运行时对 task.toml 任何字段的解释。
大资产进任务的方式是放在三个 assets 根之一，由 git 之外、HF dataset 上管理。
输入件另有普通方式，即镜像内文件与 setup 脚本，见 07 的输入投递表格。

## 转换方向

作者契约里唯一的格式转换句子如下，方向是 ALE 任务通过一次 conversion 达到 Harbor。

[doc: 02_ale/docs/specs/task-authoring.md:9-14]

```text
The format is Harbor's (`task.toml` schema 1.4, `environment/`, `tests/`, `solution/`): a
field ALE implements as Harbor does keeps Harbor's name, table and meaning. A field ALE adds
sits in the Harbor table of what it configures, under a name Harbor gives no other meaning: a
separate namespace would not stop one name meaning two things, and would have to mirror every
table it extends. ALE runs Tasks in its own runtime and a Task reaches Harbor through a
conversion, so `schema_version = "1.4+ale.1"` marks the file as ALE's.
```

常量注释描述反向镜像。纯 1.4 是 Harbor 文件，一次 conversion 把它变成 ALE 的。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:523-525]

```text
#: The ``task.toml`` schema ALE reads: revision 1 of ALE's fields on Harbor's schema 1.4. Plain
#: ``1.4`` is a Harbor file, which a conversion turns into this one.
SCHEMA_VERSION = "1.4+ale.1"
```

引擎快照没有转换器命令。CLI 顶层入口只有 assets、vm-image、sandbox、new-task 与 run 系列命令。

[code: 02_ale/packages/ale-run/src/ale/run/cli/main.py:48-54]

```text
app.add_typer(assets_app, name="assets")
app.add_typer(vm_image_app, name="vm-image")
app.add_typer(sandbox_app, name="sandbox")
```

[code: 02_ale/packages/ale-run/src/ale/run/cli/main.py:291]

```text
@app.command("new-task")
```

[cmd: grep convert 到 docs 与 packages，无 convert 子命令，无格式转换器模块]

结论 verdict 为 partially supported。
第一轮 09 写 autor 规范承诺任务经一次 conversion 到 Harbor 仓库，方向听说成立，句子在 task-authoring.md:13-14。
但第一轮把这条当作旧引擎到新引擎的转换承诺，属于方向混淆。
真实的三条链在 07 修订版分开写。
除了这两处，引擎没有任何内置转换器或转换命令，这一点 07 要写明。
旧 ALE 迁移链的证据在 01_agents-last-exam 仓，见 07 的对应引用。

## reward.json 契约

验证明书写 reward.json in Harbor 的 verifier 目录。

[doc: 02_ale/docs/specs/task-authoring.md:414-418]

```text
`tests/test.sh` (or Windows `tests/test.ps1`) evaluates the final outcome and writes its
`reward` to `/logs/verifier/reward.json` ...
```

只写 reward.json，reward 在 0 到 1 之间。

[doc: 02_ale/docs/specs/task-authoring.md:156]

```text
- The verifier writes `reward.json` only, with `reward` between 0 and 1; see [tests/](#tests).
```

打分库的契约函数如下。

[code: 02_ale/packages/ale-verify/src/ale_verify/__init__.py:114-132]

```text
def read_result(reward: str | bytes, verification: str | bytes | None = None) -> dict[str, Any]:
    """Check what a verifier wrote and return the complete result, ``reward`` rounded.

    ``reward`` is the content of ``reward.json``: a flat object of numbers whose ``reward``
    is from 0 through 1. ``verification`` is the content of ``verification.json`` when one
    was written: any object whose ``reward`` equals ``reward.json``'s. Only ``reward`` is
    rounded, to two decimal places, half up.
    """
    rewards = json_object(reward)
    for name, value in rewards.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"reward.json values must be numbers: {name}")
    if "reward" not in rewards:
        raise ValueError("reward.json must contain reward")
```

写入函数把完整结果落 verification.json，把 reward 落 reward.json。

[code: 02_ale/packages/ale-verify/src/ale_verify/__init__.py:136-149]

```text
def write(result: dict[str, Any]) -> None:
    """Atomically save a result. The engine accepts it only after normal exit.

    ``verification.json`` receives the complete result and ``reward.json`` its ``reward``,
    both with ``reward`` rounded, in the platform's framework-owned verifier directory.
    """
```

episode 协议里的 verifier 目录定义如下。

[code: 02_ale/packages/ale-run/src/ale/run/protocol/episode_protocol.py:139]

```text
    """Where verification writes ``reward.json``: Harbor's verifier directory.
```

结论 verdict 为 supported。
这是新格式验证契约的评分 JSON 出处，07 验证接口格引用这一组行。

## network_mode 默认值

TOML 层三个字面量与默认值如下，默认 no-network。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:696]

```text
    network_mode: Literal["no-network", "allowlist", "public"] = "no-network"
```

与内部枚举的映射如下。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:528-532]

```text
_NETWORK_MODES = {
    "no-network": NetworkMode.BLOCK,
    "allowlist": NetworkMode.ALLOWLIST,
    "public": NetworkMode.OPEN,
}
```

语义的文档如下。no-network 只到 Gateway，allowlist 加白名单主机，public 全开。

[doc: 02_ale/docs/specs/task-authoring.md:198-202]

```text
`[agent].network_mode` applies to the evaluated agent and the oracle: `no-network` reaches
only the Gateway, `allowlist` also the declared hosts, `public` everything.
```

结论 verdict 为 supported。
第一轮写 default no-network 正确，三个值原文也用对。
R1 修订版在 06 中保留这一行并引用上面行号。

## GUI 与 cua-desktop MCP 的引擎证据

Linux 镜像基座由 task-authoring 声明。

[doc: 02_ale/docs/specs/task-authoring.md:280-286]

```text
The image is the reproducible initial computer state supplied to the agent. Start from the ALE
GUI base matching the Task OS and sandbox ...
The Linux bases are:

- container: `ghcr.io/agentslastexam/container-ubuntu22-base` (Ubuntu 22.04);
- VM: `ghcr.io/agentslastexam/vm-ubuntu24-base` (Ubuntu 24.04).
```

镜像目录与文档写明桌面容器基座与 VM 基座。

[code: 02_ale/images/README.md:5-9]

```text
base/
├── container-ubuntu22/  Ubuntu desktop container base
├── vm-ubuntu24/         Ubuntu OCI source for a bootable VM
└── vm-windows10/        private Windows seed preparation recipe
```

[doc: 02_ale/docs/specs/sandbox-image.md:115]

```text
- `container-ubuntu22-base` provides an Ubuntu 22.04 GNOME desktop container and the
```

GUI 是否需要看镜像自身配置，不看任务声明字段。

[doc: 02_ale/docs/specs/sandbox-image.md:50-57]

```text
There are no image labels to declare. Whether a sandbox has a desktop is decided from the
image's own configuration before anything starts: a VM has one when its systemd enables a
display manager (`display-manager.service`), and a container has one when its image sets
`DISPLAY` or `WAYLAND_DISPLAY` ...
```

cua-desktop 是 Run 层 opt-in 的内置 MCP server，不是任务自动注入。

[doc: 02_ale/docs/specs/lexicon.md:41]

```text
| **CUA Desktop MCP** (`cua-desktop`) | ALE's built-in screen-control MCP server selected at Run level. |
```

[doc: 02_ale/docs/specs/autonomous-harness.md:266]

```text
- `cua-desktop` is an ordinary opt-in Run-level built-in MCP server.
```

实现文件与注册名如下。

[code: 02_ale/packages/ale-run/src/ale/run/tools/cua_desktop_mcp.py:26]

```text
SERVER = {"name": "cua-desktop", "version": "0.3.0"}
```

[code: 02_ale/packages/ale-run/src/ale/run/tools/__init__.py:17]

```text
CUA_DESKTOP_NAME = "cua-desktop"
```

内置源的 schema 侧声明如下。

[code: 02_ale/packages/ale-core/src/ale/core/taskspec.py:233-251]

```text
class McpSource(BaseModel):
    ...
    path: str | None = Field(default=None, min_length=1)
    builtin: str | None = Field(default=None, min_length=1)
    #: The longest side, in pixels, of a screenshot the built-in ``cua-desktop`` returns;
    #: unset, it returns the screen as Cua Driver captures it.
    screenshot_max_dimension: int | None = Field(default=None, ge=1)
```

运行侧允许的内置名只有 cua-desktop。

[code: 02_ale/packages/ale-run/src/ale/run/agent_resources.py:226]

```text
        if source.builtin != "cua-desktop":
```

结论 verdict 为 supported。
第一轮 06 写桌面基础镜像加 cua-desktop MCP 的 opt-in 组合，与上述证据一致。
R1 修订版写明 per-task 的 gui_status 值在 R1 任务清单内，含义无证据指向任何一方，任务清单由数据侧审计方负责。

## macOS 只走 Orchard 的来源

注册表注释与分支已在上条 provider 条目引用。
qemu 模块头一句补充如下。

[code: 02_ale/packages/ale-run/src/ale/run/providers/qemu.py:6-8]

```text
It also runs Windows guests; macOS guests
run on the Orchard Provider, since only a Mac may host them.
```

orchard 模块头写明本地 Orchard 与 Tart worker 由脚本安装在同一台 Mac。

[code: 02_ale/packages/ale-run/src/ale/run/providers/orchard.py:1-6]

```text
"""macOS sandboxes on the local Orchard controller and Tart worker.

``scripts/setup_macos.py`` runs both on this Mac. Every VM ALE creates is a clone of a local
image that carries the framework (``orchard_framing``); ALE owns only the VMs it creates for
one episode ...
```

macOS 无运行设置，需要本机 Orchard。

[code: 02_ale/packages/ale-run/src/ale/run/providers/README.md:229]

```text
from its state directory, so macOS needs no run settings.
```

[code: 02_ale/images/README.md:19]

```text
macOS Tasks name a Tart image of their own; the Orchard and Tart that run it come from
`scripts/setup_macos.py`, not from this directory.
```

结论 verdict 为 supported。
第一轮 06 写 macOS 只走 Orchard 正确，无需修正。

## 无 Playwright 依赖

依赖清单里没有 Playwright。根 workspace 依赖只有三个本仓包。

[code: 02_ale/pyproject.toml:6]

```text
dependencies = ["ale-core", "ale-run", "ale-verify"]
```

ale-run 的第三方依赖如下。

[code: 02_ale/packages/ale-run/pyproject.toml:6-12]

```text
dependencies = [
    "huggingface-hub>=0.27",
    "ale-core",
    "ale-verify",
    "typer>=0.15",
    "aiohttp>=3.11",
    "pyyaml>=6.0",
]
```

ale-core 只有 pydantic，ale-verify 只有 fastjsonschema。

[code: 02_ale/packages/ale-core/pyproject.toml:6]

```text
dependencies = ["pydantic>=2.9"]
```

[code: 02_ale/packages/ale-verify/pyproject.toml:6-8]

```text
dependencies = [
    "fastjsonschema==2.21.2",
]
```

[cmd: 对 pyproject.toml、packages/*/pyproject.toml、uv.lock、docs、packages 检索 playwright，忽略大小写，零命中]

结论 verdict 为 supported。
第一轮写无 Playwright 依赖正确。
桌面控制由 Cua Driver 承担，上面的 GUI 条目已给出行号。

## 证据质量说明

以下边界适用于本文件全部引用。
本机没有执行任何引擎命令、镜像构建或任务运行。
全部证据是静态读取与文本检索，属于 recorded-by 级。
冻结的 01 与 04 仓相关内容在同包内的其他证据文件里，路径单独标注。
第一轮文件本身不构成事实来源，本文件只以第一轮文件为待核对象。