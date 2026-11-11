# 许可证证据 R1

本文件是许可证的静态证据检索，不做法学结论。
范围是冻结快照 inputs-readonly 下的 02_ale、04_ale-tasks-base、01_agents-last-exam 三仓。
检索手段是 find 找 LICENSE COPYING NOTICE 文件（任意大小写，排除 .git），grep pyproject 的 license 字段与 classifier，读 README 的徽标与章节，grep 文档中的 license 提及 [cmd]。
引擎 commit 73517c2eb097abe7974e9ec4de9819a02cd0ee81，模板仓 commit 492249a2ca4b9d74efd3584a90399473c2e928c7，旧官方仓 commit 2e91edd3cd26baa35a38127c90c8e5241dfbe62f。
检索时排除 .git 目录，但复制链路中 .git 是对应的保留项，许可证一般放在工作区可见路径 [cmd: 检索范围说明]。

## 02_ale

### LICENSE COPYING NOTICE 文件

零个。

[cmd: find 02_ale \( -iname LICENSE* -o -iname COPYING* -o -iname NOTICE* \)，排除 .git，无命中]

### pyproject 的 license 字段与 classifier

四个 pyproject 都没有 license 字段，也没有 license 类 classifier。

[cmd: grep license 与 classifier 到 02_ale/pyproject.toml、02_ale/packages/*/pyproject.toml，无命中]

四个文件的 [project] 段只有 name、version、description。

[code: 02_ale/packages/ale-core/pyproject.toml:1-4 节选]

```text
[project]
name = "ale-core"
version = "0.1.1"
description = "ALE core contracts: task specs, environments, harnesses, traces, provenance"
```

### README 的徽标与章节

02_ale/README.md 没有 License 徽标，也没有 License 章节。

[cmd: grep -in license 到 02_ale/README.md，无命中]

README 头部是标题与 Quickstart 安装运行说明 [doc: 02_ale/README.md:1-40]。

### 文档中的 license 提及

grep 检出 4 处文档提及，全部是内容或资产相关，不构成仓库许可证声明。

[cmd: grep -rin license 到 02_ale/docs/]

四处逐一如下。

- docs/specs/sandbox-image.md:122。原文 Its licensed disk is not a public ALE artifact。指私有 Windows 种子镜像的许可磁盘不公开。
- docs/specs/task-assets.md:67。原文 tests, solutions and licensed software are never ...。指受许可约束的软件在资产公开前先设 gated。
- docs/guides/windows-task-images.md:48。原文 Share software only where its license permits。是提示任务作者要遵守第三方许可。
- docs/guides/macos-orchard.md:77。原文 the applications and licenses the Task uses。是 macOS 任务镜像的元素清单。

images 目录还有两处相近字样。

[cmd: grep -rin licen 到 02_ale/images/]

- images/base/vm-windows10/README.md:6。原文 the licensed Windows bytes remain in private storage。同样指 Windows 字节的许可状态，不是仓库许可证。
- images/README.md:38 与两个 Dockerfile 的 --exclude=LICENSE 参数是构建清理与镜像版本描述，不是仓库许可证 [code: images/base/vm-windows10/README.md:6, vm-ubuntu24/Dockerfile:29]。

### 小结论

02_ale 本仓没有可检索到的许可证声明文件、元数据字段或 README 章节 [code + cmd]。
透视图里只有受许可约束的 Windows 字节与第三方软件的规避性表述。
仓库自身的许可证状态未确认，本文件不做法学结论 [unknown]。

## 04_ale-tasks-base

### LICENSE COPYING NOTICE 文件

零个。

[cmd: find 04_ale-tasks-base（排除 .git），无命中]

### pyproject 与 README

本仓没有 pyproject.toml [cmd: ls，顶层为 .github、.gitignore、Justfile、README.md、tasks]。
README.md 没有 License 徽标，也没有 License 章节。

[cmd: grep -in license 到 04_ale-tasks-base/README.md，无命中]

全仓 grep 也零命中。

[cmd: grep -ric license 到 04_ale-tasks-base/，全部为 0]

### 文档提及

README 只讲格式、资产与 CLI 用法，没有许可证表述 [doc: 04_ale-tasks-base/README.md 通读]。

### 小结论

04_ale-tasks-base 没有任何可检索到的许可证出处 [cmd]。
状态未确认，不做法学结论 [unknown]。

## 01_agents-last-exam

### LICENSE COPYING NOTICE 文件

根目录有两个许可证文件，确立了双许可证结构。

[cmd: find 01_agents-last-exam -maxdepth 1，可见 LICENSE 与 LICENSE-DATA]

- LICENSE。抬头是 Apache License Version 2.0, January 2004 [doc: 01_agents-last-exam/LICENSE:1-3]。
- LICENSE-DATA。抬头是 Creative Commons Attribution 4.0 International (CC BY 4.0)，版权行 Copyright 2026 UC Berkeley RDI and RDI Foundation [doc: 01_agents-last-exam/LICENSE-DATA:1-2]。
- LICENSE-DATA 写明适用范围是基准数据，含 tasks/、selected_tasks/、sample_run/ 及相关任务内容 [doc: 01_agents-last-exam/LICENSE-DATA:5-7]。

深层还有大量上游 vendor 的许可证，都在 ale_run/agents/<name>/upstream/ 下。

[cmd: find 01_agents-last-exam（排除 .git 与 node_modules），命中 200 个以上]

这些是各 agent harness 的上游依赖自带文件，不代表本仓规则 [inference]。

### pyproject 的 license 字段

有。

[code: 01_agents-last-exam/pyproject.toml:10]

```toml
license = "Apache-2.0"
```

版本上限也一并读出。

[code: 01_agents-last-exam/pyproject.toml:5-11 节选]

```toml
[project]
name = "agent-last-exam"
version = "0.1.0"
description = "Agent benchmark framework. Upper-layer-only replacement for agenthle orchestration."
...
license = "Apache-2.0"
```

### README 的徽标与章节

有两枚徽标加一个 License 章节。

[doc: 01_agents-last-exam/README.md:14-15]

```text
[![License: Apache-2.0](...Apache--2.0...)](LICENSE)
[![License: CC BY 4.0](...CC--BY--4.0...)](LICENSE-DATA)
```

章节在第 217 到 222 行。

[doc: 01_agents-last-exam/README.md:217-222]

```text
| Component | License | Scope |
| **Software** | [Apache-2.0](LICENSE) | `ale_run/`, `configs/`, `docs/`, and other framework files |
| **Data** | [CC-BY-4.0](LICENSE-DATA) | `tasks/`, `selected_tasks/`, `sample_run/`, and other benchmark content |
```

### 小结论

01 旧官方仓的许可证结构清楚。软件 Apache-2.0，数据 CC BY 4.0 [doc: LICENSE, LICENSE-DATA, pyproject.toml:10, README.md:217-222]。
这不构成本文件对任何其余仓库的推论，不做法学结论 [unknown]。

## 跨仓小结

| 仓 | LICENSE 文件 | pyproject 字段 | README 声明 | 结论 |
| --- | --- | --- | --- | --- |
| 02_ale | 无 [cmd] | 无 [cmd] | 无 [cmd] | 未找到出处 [unknown] |
| 04_ale-tasks-base | 无 [cmd] | 无 pyproject [cmd] | 无 [cmd] | 未找到出处 [unknown] |
| 01_agents-last-exam | LICENSE 与 LICENSE-DATA [cmd] | Apache-2.0 [code: pyproject.toml:10] | 双徽标加章节 [doc: README.md:14-15,217-222] | 软件 Apache-2.0，数据 CC BY 4.0 |

已证实的只有存在或不存在本身，许可证状态与合规不做法学结论 [unknown]。
本轮没有访问上游仓库在线页面，全部证据来自本地冻结快照 [cmd: 范围声明]。