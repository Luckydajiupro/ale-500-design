# 运行提供方矩阵（R2 修订）

本文件重写第一轮的 06_runtime_provider_matrix.md。
最终基线说明。本版继承 R2 修订版（基于 R1 版 31f22482d41ccd60 的 B 项定点修订）。R2 改动对照见 evidence/history-r2/CHANGELOG_R2.md，继承来源与哈希见 SOURCE_MANIFEST_FINAL.json。
引擎路径相对 inputs-readonly/02_ale，commit 73517c2eb097abe7974e9ec4de9819a02cd0ee81。
旧官方仓路径相对 inputs-readonly/01_agents-last-exam，commit 2e91edd3cd26baa35a38127c90c8e5241dfbe62f。
本机这轮没有运行任何引擎命令、镜像构建或任务，全部结论来自静态读取与文本检索，见最后一节证据质量说明 [cmd]。

与第一轮 06 相比，本版的三处结构性修正先行标注。

- 删掉第一轮第 90 行 qemu 加 KVM 可在 Tencent 云 Linux 自托管的说法。理由是不嵌套虚拟化是项目前提 [doc: R1 brief]。
- 提供方矩阵每个单元格全部带上证据类，没有证据的组合写 [unknown]，不留空白。
- 可运行性拆成三栏，旧引擎清单、新引擎声明、当前宿主机实测，实测栏全部 NOT_RUN。

## 1. 宿主层

首轮运行环境是 Tencent Cloud Linux 服务器 [doc: R1 brief 前提]。
这些服务器不能运行嵌套虚拟化 [doc: R1 brief 前提]。
这是一条已确认的项目前提，不是本文件作出的推断 [doc: R1 brief]。
由它直接推出在现有服务器上不能运行任何 guest VM [inference: 无嵌套虚拟化则无硬件虚拟化能力]。
请看第 2 节，新引擎的 VM 路径全都要求 /dev/kvm，或要求一台 Mac。
所以 Linux VM 路径、Windows VM 路径、macOS 路径在现有 Tencent Cloud Linux 服务器上都不可用 [inference: 前提加引擎宿主要求]。
当前宿主机上一概没有实际运行记录，本文件把它与推断分开放。

## 2. 沙箱提供方层

### 2.1 引擎声明了哪四个提供方

提供方包目录下的 README 用一张表声明，四个模块一一对应四个后台。

[code: 02_ale/packages/ale-run/src/ale/run/providers/README.md:5-8]

```text
| Module | Backend | Prepared input |
| `docker.py` | local Docker container | immutable OCI image identity |
| `qemu.py` | QEMU/KVM guest runner | materialized qcow2 identity |
| `daytona.py` | Daytona cloud container | immutable OCI image identity, pushed by digest |
| `orchard.py` | macOS VM on Orchard/Tart | digest-pinned OCI image, or a local image `build.sh` built |
```

注册表的选择逻辑如下。macOS VM 无条件走 Orchard，容器按配置走 daytona 或 docker，其余 VM 走 qemu。

[code: 02_ale/packages/ale-run/src/ale/run/providers/__init__.py:20-58 节选]

```text
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

运行配置把可选值固定为字面量。容器只有 docker 与 daytona，VM 只有 qemu。

[code: 02_ale/packages/ale-core/src/ale/core/config.py:257-281 节选]

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

保留提供方元组只有三个，orchard 不在里面。

[code: 02_ale/packages/ale-run/src/ale/run/providers/__init__.py:16]

```text
RETAINING_PROVIDERS = ("docker", "qemu", "daytona")
```

### 2.2 每个提供方对宿主的要求

docker 需要宿主 PATH 里有 docker，且 daemon 可达。

[code: 02_ale/packages/ale-run/src/ale/run/providers/docker.py:483-488]

```text
    async def preflight(self) -> None:
        if shutil.which("docker") is None:
            raise ProviderStartError("docker is not installed — see `just doctor`")
        code, _, stderr = await _docker("info", "--format", "{{.ServerVersion}}", timeout=30)
```

qemu 需要 docker、qemu-img，以及至关重要的是 /dev/kvm 必须存在且可读写。

[code: 02_ale/packages/ale-run/src/ale/run/providers/qemu.py:703-726 节选]

```text
        if not Path("/dev/kvm").exists():
            problems.append(
                "/dev/kvm is missing: this host has no hardware virtualisation, so the "
                "container backend is the usable one here"
            )
        elif not os.access("/dev/kvm", os.R_OK | os.W_OK):
            problems.append("/dev/kvm is present but not writable (add yourself to the kvm group)")
```

runner 容器带设备挂载启动。

[code: 02_ale/packages/ale-run/src/ale/run/providers/qemu.py:944]

```text
            "--device=/dev/kvm",
```

模块头把要求概括成一句话。

[code: 02_ale/packages/ale-run/src/ale/run/providers/qemu.py:11-14 节选]

```text
  It also means the host needs nothing installed but Docker and ``/dev/kvm``.
```

README 的实测数据段落以主机条件开头，印证这是运行前提。

[code: 02_ale/packages/ale-run/src/ale/run/providers/README.md:187]

```text
Measured on a KVM host:
```

关于嵌套虚拟化，引擎没有任何语句。全仓 grep 嵌套与 nested 与 KVM 上下文，没有一处说 /dev/kvm 可以从嵌套环境获得，也没有一处说不可以 [cmd: grep 无命中]。

[unknown] 嵌套虚拟化下 qemu provider 是否可行，引擎沉默，本文件不下结论。
Tencent 服务器不能嵌套虚拟化是 R1 任务书确认的项目前提，不是引擎声明 [doc: R1 brief]。

daytona 是云端容器，标题行写明。

[code: 02_ale/packages/ale-run/src/ale/run/providers/daytona.py:1]

```text
"""Daytona container Provider: Linux sandboxes on Daytona's cloud.
```

本地只要两条工具链，认证靠云 API key。

[code: 02_ale/packages/ale-run/src/ale/run/providers/daytona.py:654-667 节选]

```text
        for tool, why in (("docker", "builds and pushes the image"), ("ssh", "reaches guestd")):
            if shutil.which(tool) is None:
                raise ProviderStartError(f"{tool} is not installed; Daytona needs it, it {why}")
```

key 环境变量与区域默认值在配置里。

[code: 02_ale/packages/ale-core/src/ale/core/config.py:242-254 节选]

```text
    target: str = Field(default="us", min_length=1)
    api_key_env: str = Field(default="ALE_DAYTONA_API_KEY", pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    lifetime_hours: int = Field(default=24, ge=1, le=720, strict=True)
```

orchard 的宿主是一台 Mac，控制器与 Tart worker 装在同一台 Mac 上。

[code: 02_ale/packages/ale-run/src/ale/run/providers/orchard.py:1-6 节选]

```text
"""macOS sandboxes on the local Orchard controller and Tart worker.

``scripts/setup_macos.py`` runs both on this Mac.
```

qemu 模块头写明 macOS guest 只归 Orchard，因为只有 Mac 能托管它们。

[code: 02_ale/packages/ale-run/src/ale/run/providers/qemu.py:6-8]

```text
It also runs Windows guests; macOS guests
run on the Orchard Provider, since only a Mac may host them.
```

### 2.3 操作系统与提供方矩阵

| 操作系统路径 | docker | daytona | qemu | orchard |
| --- | --- | --- | --- | --- |
| Linux 容器 | 支持，默认容器提供方 [code: config.py:262] | 支持，cloud only [code: daytona.py:1] | 不适用 [code: 注册表 kind=CONTAINER 分支] | 不适用 [code: 注册表] |
| Linux VM | 未声明 [unknown] | 未声明，配置只有 docker|daytona 是为容器 [code: config.py:262]，VM 字面量只有 qemu [code: config.py:281] | 声明支持，preflight 要求 /dev/kvm [code: qemu.py:703-726] | 未声明 [unknown] |
| Windows VM | 未声明 [unknown] | 未声明 [unknown] | 声明支持 [code: qemu.py:6-8]，镜像与显卡组合未在本机验证 [unknown] | 未声明 [unknown] |
| macOS VM | 不支持 [code: qemu.py:6-8 指给 Orchard] | 未声明 [unknown] | 不支持 [code: qemu.py:6-8] | 唯一路径，无条件注册 [code: __init__.py:20-58]，要求 Mac 宿主 [code: orchard.py:1-6] |

第一轮把 docker 写不支持 Windows，这里改为未声明，因为引擎没有 Windows 容器的说法 [unknown]。
其余单元格一律填证据类或不支持加来源，不留空白。
当前宿主机会实推什么，看第 4 节三栏，那一栏全部 NOT_RUN。

### 2.4 GPU 在四个提供方下的声明

任务的 gpu_types 决定可接受的 GPU 模型，每个提供方各有核实方式。

[code: 02_ale/packages/ale-run/src/ale/run/providers/README.md:44-55]

- docker 用 nvidia-smi 读宿主 GPU 并按 container.gpus 租赁，模型不接受则拒绝起步 [code: 第 52 行]。
- qemu 下 GPU 绑给 vfio-pci，模型无法在宿主侧命名，等 guest 用 nvidia-smi 读到才核对，不接受则销毁沙箱 [code: 第 53 行]。
- daytona 把任务名映射到云端类型，含 H100、H200、RTX-PRO-6000、RTX-4090、RTX-5090 [code: 第 54 行]。
- orchard 拒绝一切 GPU 请求 [code: 第 55 行]。

### 2.5 Windows 与 GPU 的开放决策节

Windows 与 GPU 是否采用、资源预算多少，仍是开放决策 [doc: R1 brief 前提]。
第一轮 06 第 92 行写首轮无 GPU 预算时三个 GPU 任务留在挂起池，把预算当成已定事实，本版改为 open，不带预设。
本节的证据基座如下。

- Windows 任务在新引擎总是 VM 加 PowerShell [doc: task-authoring.md:138-156 差异清单]。
- qemu provider 声明运行 Windows guest [code: qemu.py:6-8]。
- Windows VM 在现有 Tencent 服务器不可用，因为无嵌套虚拟化 [doc: R1 brief 加 inference]，云上 Windows 产品或其他宿主机是开放的工程选项 [unknown]。
- GPU 语义是整卡数量与模型名单，由任务声明 gpus 与 gpu_types [doc: task-authoring.md:217-234]。
- 提供方级 GPU 行为见 2.4 节。
- 预算与采用与否由项目负责人定 [doc: R1 brief]，本文件不做推荐。

## 3. 模型提供方层

模型提供方与沙箱提供方是两个独立的关切 [doc: R1 brief 前提]。
引擎代码里的注释把这条也写明了。

[code: 02_ale/packages/ale-core/src/ale/core/config.py:155-158]

```text
#: The model vendor whose API the Gateway or a Judge calls. Not a sandbox Provider.
ModelProvider = Literal["anthropic", "gemini", "meta", "moonshot", "openai", "qwen", "xai", "zai"]
#: A protocol the Gateway serves to the Sandbox and speaks to the provider.
Dialect = Literal["anthropic", "gemini", "openai-chat-completions", "openai-responses"]
```

八个字面量是 anthropic、gemini、meta、moonshot、openai、qwen、xai、zai [code: config.py:156]。
四个方言是 anthropic、gemini、openai-chat-completions、openai-responses [code: config.py:158]。
键与端点的机制在 GatewayConfig 字段说明里。

[code: 02_ale/packages/ale-core/src/ale/core/config.py:166-172 节选]

```text
        provider: ModelProvider = Field(
            default="anthropic",
            description=(
                "Whose API the Gateway calls. Its key is ALE_<PROVIDER>_API_KEY and its "
                "endpoint ALE_<PROVIDER>_BASE_URL, or the provider's own API when that is unset."
            ),
        )
```

.env.example 逐家列出键与默认端点。

[code: 02_ale/.env.example:7-24]

```text
ALE_ANTHROPIC_API_KEY=
# ALE_ANTHROPIC_BASE_URL=https://api.anthropic.com
ALE_GEMINI_API_KEY=
...
ALE_ZAI_API_KEY=
# ALE_ZAI_BASE_URL=https://api.z.ai/api/anthropic
```

沙箱内的 agent 流量不拿任何 provider 键，拿到的是每集 Gateway token。

[code: 02_ale/.env.example:1-3]

```text
# Copy to .env and fill only the credentials used by this checkout.
# Values stay on the Host; Task Sandboxes receive an episode Gateway token and the
# variables a Task's env tables name (see docs/specs/task-authoring.md#variables).
```

选择哪一家模型提供方是开放决策，本文件只列引擎事实，不挑 vendor [doc: R1 brief]。

## 4. 可运行性三栏

三个栏分开写。旧引擎官方清单、新引擎声明、当前宿主机实测。
第三栏全部 NOT_RUN，本机没有任何执行记录 [cmd: 本轮未运行任何任务]。

### 4.1 旧引擎官方支持清单

#### Docker 允许名单

select_tasks 目录下的 docker_support.txt 头部写明总数与排除理由。

[code: 01_agents-last-exam/selected_tasks/docker_support.txt:1-12]

```text
# Linux (cpu-free-ubuntu) Docker allowlist.
# Total: 78 tasks.
# Blender building, MuseScore transcription, and Ardour migration passed
# native workflow checks in the published container.
# The 4 tasks needing nested Docker (openroad_sky130_ibex_pnr_signoff,
# k8s_migration_1, bpmn_supply_disruption_l3, bpmn_category_governance_restructuring_l3)
# and scene2_resample, which needs an Apptainer/Singularity .simg GUI bundle,
# are excluded; see local Docker docs.
# Also excluded: gcode requires bubblewrap PID/network namespaces; Road
# (cailian_road_highway_alignment_2) and inner_support_elevation_optimization
# require systemd supervision, and inner-support requires delegated cgroups.
# Use QEMU for these tasks without weakening isolation or resource limits.
```

78 任务的清单加 8 个带原因排除 [code: 同上]。
文档站的限制段落与它一致。

[doc: 01_agents-last-exam/docs/ale-docs-site/pages/local-docker.html:121-124]

```text
- Linux tasks only. Windows and GPU snapshots are not mapped.
- Eight Linux tasks are excluded: four require nested Docker, one requires an Apptainer or Singularity GUI bundle, and three require namespace or systemd/cgroup facilities unavailable in the default profile.
- G-code requires bubblewrap PID/network namespaces, which the default container denies. Road and inner-support require systemd supervision...
```

8 个排除任务的名字与原因全部在 docker_support.txt 头注里，逐任务可查 [code: 头注]。
允许名单身份只能说明候选资格，不代表在 Tencent Cloud 上已经可跑 [inference: 名单是旧引擎本地的官方配方，与当前宿主无关]。

#### 86 任务 Linux VM 清单

select_tasks 目录下存在 ale_cli.txt。

[code: 01_agents-last-exam/selected_tasks/ale_cli.txt:1-2]

```text
# All published cpu-free-ubuntu tasks, including desktop workflows.
# Total: 86 tasks.
```

共 88 行，减去 2 行头注为 86 个任务 [cmd: wc -l]。
README 的选集表格写它是 Linux VM profile，含桌面工作流 [doc: 01_agents-last-exam/README.md:189]。
v1.1 发布说明同样写 86 个 [doc: 01_agents-last-exam/docs/releases/v1.1.md:156]。
这是旧引擎 QEMU/KVM 路径的官方清单。

#### GPU 清单

gpu.txt 3 个任务，全在 Windows GPU 快照上。

[code: 01_agents-last-exam/selected_tasks/gpu.txt:1-6 节选]

```text
# Published tasks using the gpu-free snapshot.
# Total: 3 tasks.
engineering/humanoid_velocity_tracking_policy
visual_media/chroma_key_from_reference
```

#### 旧引擎提供方模块

旧引擎 environments 里有六个 provider 模块，本次 ls 实际验证存在。

[cmd: ls 01_agents-last-exam/ale_run/environments/providers/ 得到 aliyun.py、aws.py、docker.py、gcloud.py、qemu.py、static.py]

第一轮写提供方列表是 gcloud、aws、aliyun、qemu、docker、static，与模块目录一致 [code: 同上]。
各模块职责见原执行人笔记第 171 到 172 行，属历史记录 [doc: evidence/notes/01_agents-last-exam.md:171-172]。

### 4.2 新引擎声明

新引擎自己宣称支持什么，逐条如下，全部带出处。

- Linux 容器。docker 与 daytona 两条路径 [code: config.py:262, README.md:5-8]。
- Linux VM。qemu 一条路径，前置条件是 /dev/kvm [code: config.py:281, qemu.py:703-726]。
- Windows VM。qemu 声明能跑 Windows guest，作者规范要求 VM 加 PowerShell [code: qemu.py:6-8, doc: task-authoring.md:138-156]。
- macOS VM。只走 Orchard，要求 Mac 宿主 [code: __init__.py:20-58, orchard.py:1-6]。
- GUI。桌面基础镜像加 opt-in 的 cua-desktop MCP，见第 6 节 [doc: lexicon.md:41]。
- GPU。任务可声明 gpus 与 gpu_types，提供方各自核实 [doc: task-authoring.md:217-234, code: README.md:44-55]。

这些是新引擎在冻结快照里写的支持声明，不代表在 Tencent Cloud 上已落地 [inference: 声明与实测是两回事]。

### 4.3 当前宿主机实测

什么都没有运行。本轮的边界禁止任务执行与评测，附上一句话说明。

[cmd: 零次引擎命令、零次镜像构建、零次任务运行]

当前 Tencent Cloud Linux 服务器上的实测状态如下。

| 组合 | 实测状态 |
| --- | --- |
| Linux 容器 docker | NOT_RUN |
| Linux 容器 daytona | NOT_RUN，云端账号未在此验证 |
| Linux VM qemu | NOT_RUN，宿主无嵌套虚拟化前提下不可用 [doc: R1 brief + inference] |
| Windows VM qemu | NOT_RUN，同上，且采用与否开放 [doc: R1 brief] |
| macOS Orchard | NOT_RUN，现有服务器不是 Mac [inference] |

第一轮 06 第 89 到 90 行写的 docker 直接落地与 qemu 加 KVM 自托管两条推断均已删除 [doc: R1 brief 修正]。
在拿到真实运行证据之前，本栏不做任何可用断言。

## 5. 外部服务

R2 已把数据侧审计的最终结果合入本节。口径：122 个官方任务里 external_service 非 none 的共 13 个，全部在非 CS 范围，其中 staged-local 5、online-required 6、public-ref 2。数字取自 04_task_inventory.csv 的 external_service 列与 evidence/staged_local_os.tsv 的逐条记录，不手工抄写 [cmd: R2 聚合]。所谓 13 个不等于 13 个都在线硬依赖。staged-local 是本地服务需重新宿主，online-required 才是在线硬依赖，public-ref 只是引用在线公开端点。

| 级别 | 数量 | 逐条 (task_id) | 系统归属 |
| --- | --- | --- | --- |
| staged-local | 5 | business_finance/odoo、business_finance/taxform_4_1、business_finance/metabase_bi_dashboard_01、business_finance/bpmn_supply_disruption_l3、business_finance/bpmn_category_governance_restructuring_l3 | 2 Linux（BPMN 双任务）+ 3 Windows（Metabase、Odoo、Taxform）|
| online-required | 6 | business_finance/ar_full_1500、ar_full_300、equity_research_summary、ff5_public_reconstruction、physical_sciences/egt710_table1_smiles_extraction、physical_sciences/ketcher_smiles_reproduction | 在线依赖是任务本体 |
| public-ref | 2 | life_sciences/tp53_locus_variant_histone_browser_svg、other/mota_exploration | 引用在线公开端点 |

01 历史口径说明。第一轮 06 第 62 到 73 行的 8 任务表是历史稿，其 8 个数字与三级别划分已被上面的 R2 终稿替代，不再单独引用 [历史引用]。
新引擎网络模式的承载面另见表。

| 网络模式 | 声明 | 出处 |
| --- | --- | --- |
| no-network | 默认，只到 Gateway | [code: taskspec.py:696] |
| allowlist | 加白名单主机 | [doc: task-authoring.md:198-202] |
| public | 全开，macOS 任务必须声明 public | [doc: 同上, 200-202] |

## 6. GUI

### 6.1 桌面基础镜像

作者规范写明 Linux 镜像从 ALE GUI 基座起。

[doc: 02_ale/docs/specs/task-authoring.md:280-286 节选]

```text
The image is the reproducible initial computer state supplied to the agent. Start from the ALE
GUI base matching the Task OS and sandbox ...
- container: `ghcr.io/agentslastexam/container-ubuntu22-base` (Ubuntu 22.04);
- VM: `ghcr.io/agentslastexam/vm-ubuntu24-base` (Ubuntu 24.04).
```

镜像目录 README 的第一列即桌面容器基座。

[code: 02_ale/images/README.md:5-9]

```text
├── container-ubuntu22/  Ubuntu desktop container base
├── vm-ubuntu24/         Ubuntu OCI source for a bootable VM
└── vm-windows10/        private Windows seed preparation recipe
```

有没有桌面由镜像自身配置决定，不看任务声明字段。

[doc: 02_ale/docs/specs/sandbox-image.md:50-57 节选]

```text
Whether a sandbox has a desktop is decided from the image's own configuration before anything
starts: a VM has one when its systemd enables a display manager (`display-manager.service`),
and a container has one when its image sets `DISPLAY` or `WAYLAND_DISPLAY` ...
```

Windows 桌面镜像的来源是私有 Windows 10 BYOL 基座，带已登录桌面 [doc: 02_ale/docs/specs/sandbox-image.md:115-120]。

### 6.2 cua-desktop MCP

cua-desktop 是 ALE 内置的屏幕控制 MCP server，在 Run 层选择，不是任务自动注入。

[doc: 02_ale/docs/specs/lexicon.md:41]

```text
| **CUA Desktop MCP** (`cua-desktop`) | ALE's built-in screen-control MCP server selected at Run level. |
```

[doc: 02_ale/docs/specs/autonomous-harness.md:266]

```text
- `cua-desktop` is an ordinary opt-in Run-level built-in MCP server.
```

实现注册名与版本如下。

[code: 02_ale/packages/ale-run/src/ale/run/tools/cua_desktop_mcp.py:26]

```text
SERVER = {"name": "cua-desktop", "version": "0.3.0"}
```

schema 侧只允许这个名字作 builtin 源，截图尺寸设置只对 cua-desktop 生效。

[code: 02_ale/packages/ale-run/src/ale/run/agent_resources.py:226, 02_ale/packages/ale-core/src/ale/core/taskspec.py:233-251]

[cmd: 全仓检索 preset toml，没有任何预设默认开启 cua-desktop，opt-in 确认]

### 6.3 无 Playwright 依赖

依赖清单里没有 Playwright 任何变体。
根 workspace 只依赖三个本仓包。

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

[code: 02_ale/packages/ale-core/pyproject.toml:6, 02_ale/packages/ale-verify/pyproject.toml:6-8]

[cmd: 对 pyproject.toml、packages 下 pyproject.toml、uv.lock、docs、packages 全仓 grep playwright，忽略大小写，零命中]

### 6.4 任务级 GUI 状态

每任务是否 GUI 的 gui_status 值来自 04_task_inventory.csv 同一版清单，R2 已合入。全集 122 个任务是 40 明确 yes、9 个 unknown、73 个 no [cmd: R2 聚合 04]。排除 computing_math 后是 36 明确 yes、8 个 unknown、59 个 no [cmd: 同上]。首期参考研究候选集只讨论非 CS 集合。第一轮 06 写 6 个 yes 是历史口径，此处终稿不沿用 [历史引用]。这些值的含义在本快照没有引擎或官方文档可佐证，gui 判定本身一概 [unknown]，本节只报告数字来源不解释含义。

## 7. 证据质量说明

本文件全部结论是静态读取与文本检索，零执行 [cmd]。
清单边界只作用于 inputs-readonly 的冻结快照，commit 号在文件头。
历史类断言一律标注原执行人记录身份，引用对象已在 evidence/notes 与 evidence 中复制 [doc: 历史记录]。
当前宿主机的可运行性在拿到真实运行证据之前一律 NOT_RUN，上一节已经把第一轮两条落地推断删除。