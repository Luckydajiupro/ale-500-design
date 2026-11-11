# 运行侧声明审计 R1

本文件把第一轮四个文件里的引擎相关声明逐条裁定。
裁定分四档。supported 有引擎证据相符。partially-supported 方向对但措辞过头或只对一半。unsupported 与冻结证据或 R1 任务书前提冲突。not-explored 本轮没有查证或属于数据侧审计方。
证据指针指向本包 C1 文件（evidence/engine_format_evidence.md）或直接给文件行号。
引擎路径相对 inputs-readonly/02_ale，commit 73517c2eb097abe7974e9ec4de9819a02cd0ee81。
旧官方仓相对 inputs-readonly/01_agents-last-exam，commit 2e91edd3cd26baa35a38127c90c8e5241dfbe62f。
第一轮四个文件在 analysis/phase0-official-baseline/ 下，本文件引其行号。

## 四个项目负责人点名的核查项

### 第一轮有没有说任务在当前宿主机可跑

有。两处。

[doc: 第一轮 06_runtime_provider_matrix.md:89]

```text
- 首轮环境是 Tencent Cloud Linux 服务器。docker 提供方能直接落地 64 个非 CS Docker 允许任务。
```

[doc: 第一轮 06_runtime_provider_matrix.md:90]

```text
- 7 个非 CS 文档例外任务需要 VM。Tencent 上可用 qemu 加 KVM 自托管，或用云侧 VM 产品，等价于新引擎的 Linux VM 路径。
```

裁定都是 unsupported。
第一处把旧允许名单当成当前宿主机的落地现实，没有运行证据 [cmd: 本轮零执行]。
第二处违反 R1 前提，现有 Tencent Cloud Linux 服务器不能嵌套虚拟化 [doc: R1 brief 前提]。
两处在 R1 版本 06 中已删除。

### 第一轮有没有写 qemu 加 KVM 可用

有。

[doc: 第一轮 06_runtime_provider_matrix.md:90]

```text
Tencent 上可用 qemu 加 KVM 自托管
```

裁定 unsupported。
引擎要求 /dev/kvm 且没有嵌套虚拟化的任何声明 [code: 02_ale/packages/ale-run/src/ale/run/providers/qemu.py:703-726]。
Tencent 侧的结论由 R1 前提否定 [doc: R1 brief]。

### 第一轮有没有写无 GPU 预算为已定

有，一处正文一处措辞。

[doc: 第一轮 06_runtime_provider_matrix.md:92]

```text
- 首轮无 GPU 预算时，3 个 GPU Windows 任务自然留在挂起池。
```

[doc: 第一轮 09_unknowns_and_decisions.md:14]

```text
8. GPU 3 个任务全是 Windows 快照。首轮无 GPU 预算时这三者随 Windows 挂起，但后续进入时需要明确 GPU 提供方。
```

裁定 partially-supported。
GPU 任务富士是 Windows 快照这一事实有清单支持 [code: 01_agents-last-exam/selected_tasks/gpu.txt]。
无 GPU 预算被写成既定背景，而 R1 任务书说 GPU 采用与预算仍是开放决策 [doc: R1 brief 前提]。
两处在 R1 版本改为 open 表述。

### 第一轮有没有把 P0-9 写成管线阶段 P0 到 P5

有，最直接的一句如下。

[doc: 第一轮 09_unknowns_and_decisions.md:33]

```text
- P0-9 质量管线顺序为全自动检查、专家自检、agent 质量预审、风险分层人工审查、工程自动验证、负责人批量发布。P0-9 是管线阶段标号，不是十个风险等级。
```

随后把六项机制安进 P0 到 P5 六个阶段。

[doc: 第一轮 09_unknowns_and_decisions.md:40-47]

```text
| P0 | 全自动检查 | 内容稿进入库 | 命名、schema、解析、禁用字符检查全绿 [doc: 管线定义] |
| P1 | 专家自检 | P0 绿 | 作者签名 [doc: 管线定义] |
| P2 | agent 质量预审 | P1 签名 | ... |
| P3 | 风险分层人工审查 | P2 过 | 见分层 |
| P4 | 工程自动验证 | P3 过 | ... |
| P5 | 负责人批量发布 | P4 绿 | 负责人签发 [doc: 管线定义] |
```

裁定 unsupported。
R1 任务书写明 P0-9 是决策编号，不是管线阶段编号 [doc: R1 brief 前提]。
六项机制集合本身是获批的，但抽样率、风险阈值、审查人数都未冻结 [doc: R1 brief]。
第一轮 09 第 51 行写 Tier A 的 1 GiB 门槛与两名审查者，裁定 partially-supported。
机制方向正确，阈值与人frozen数属于待标定参数，R1 版本不再写成冻结值。

## 第一轮 06 的行级审计

| 位置 | 主张 | 裁定 | 证据指针 |
| --- | --- | --- | --- |
| 06:5-10 | OS 分布 86 加 36，除 CS 后 71 加 32，GPU 3 个 | not-explored | 04 CSV 属数据侧审计方 |
| 06:16 | 宿主机官方只支持 Ubuntu 或 Debian | not-explored | 本轮未重查旧引擎宿主声明 |
| 06:17 | 旧 provider 列表六个 | supported | [cmd: ls 01 ale_run/environments/providers 六个模块] |
| 06:18 | 本地 Docker 配方 78 任务 | supported | [code: 01 selected_tasks/docker_support.txt:1-2] |
| 06:19 | 8 个排除与原因 | supported | [code: docker_support.txt:5-11, doc: local-docker.html:121-124] |
| 06:21 | Windows 与 GPU 快照不在 Docker 映射 | supported | [doc: local-docker.html:121] |
| 06:22 | 桌面分辨率记录 1920x1080 | not-explored | 历史记录未重查 |
| 06:24 | 网络默认开启 4 张卡设 off | not-explored | 数据侧普查 |
| 06:30 | 任务 OS 三值 | supported | [code: taskspec.py:783-800 environment 表] |
| 06:31 | 四 provider 模块 | supported | [code: providers/README.md:5-8] |
| 06:32 | macOS 只 Orchard，Windows VM 加 PowerShell | supported | [code: providers/__init__.py:20-58, qemu.py:6-8] |
| 06:33 | 三个基座镜像 | supported | [code: images/README.md:5-9] |
| 06:34 | GUI opt-in cua-desktop，无 Playwright | supported | C1 GUI 与 no-Playwright 条目 |
| 06:35 | no-network 默认 | supported | [code: taskspec.py:696] |
| 06:36 | 8 家模型 provider 与 4 方言 | supported | [code: config.py:155-158] |
| 06:37 | ALE_ 键加 Gateway token | supported | C1 模型 provider 条目 |
| 06:38 | reward.json 0 到 1 两位小数 | supported | C1 reward.json 条目 |
| 06:44 | docker Linux 容器默认底座 | supported | [code: config.py:262] |
| 06:45 | qemu Linux VM 支持，Windows 未验证 | supported | [code: README.md:5-8, qemu.py:703-726]，R1 版补 /dev/kvm 条件 |
| 06:46 | daytona 云端容器 | supported | [code: daytona.py:1] |
| 06:47 | orchard 唯一 macOS 路径 | supported | [code: providers/__init__.py:20-58] |
| 06:56 | 新引擎 network_mode 三值 | supported | [code: taskspec.py:696] |
| 06:57 | setup 与 verify 出口开放 | partially-supported | 阶段划分有文档，出口开放未本轮重查 |
| 06:60-75 | 外部服务 8 任务普查表 | not-explored | 数据侧审计方，R1 保持合并点 |
| 06:77-83 | GUI 6 行判定与桌面镜像推理 | partially-supported | 数据行数归数据侧，桌面由镜像配置决定 [doc: sandbox-image.md:50-57] |
| 06:89 | docker 直接落地 64 任务 | unsupported | 见上核查项一 |
| 06:90 | qemu 加 KVM 自托管可行 | unsupported | 见上核查项二，且 daytona 非 VM 路径 [code: daytona.py:1] |
| 06:91 | 单一模型商约束与 8 字面量兼容 | partially-supported | 机制对，选哪家是开放决策 [doc: R1 brief]，不预设单一 |
| 06:92 | 无 GPU 预算挂起池 | partially-supported | 见上核查项三 |
| 06:93 | egt710 需 allowlist 或改设计 | supported | [code: taskspec.py:696, 528-532] |
| 06:100-108 | Windows 证据与建议，状态 OPEN | supported | 开放状态与 R1 前提一致 |

## 第一轮 07 的行级审计

| 位置 | 主张 | 裁定 | 证据指针 |
| --- | --- | --- | --- |
| 07:9-10 | 旧双文件包，新目录包 | supported | [cmd: ls 任务目录, doc: task-authoring.md:36-43] |
| 07:11 | task_card 无 schema 版本字段 | supported | [cmd: 顶层 16 键列表无 schema] |
| 07:12 | 04 模板存在 example_task | supported | [cmd: ls 04 tasks/ 有 demo 与 example_task] |
| 07:18-19 | 身份与提示字段 | supported | [cmd: 任务卡键 + doc: task-authoring.md] |
| 07:20 | inputFiles 形状 | supported | [code: 01 定价任务卡 inputFiles 四元素] |
| 07:20 | artifacts 是输入清单对应物 | unsupported | artifacts 是输出收集 [code: taskspec.py:74-84, doc: task-authoring.md:53-58] |
| 07:21 | vm.snapshot 与 vm.network.mode 两键 | partially-supported | vm 键含 snapshot，network.mode 子键未本轮验证 |
| 07:22 | [agent] 表字段 | supported | C1 与 [code: taskspec.py AgentTable] |
| 07:23 | [verifier] 表 | supported | [code: taskspec.py VerifierTable] |
| 07:24 | solution oracle 专用 | supported | [doc: task-authoring.md:449-453] |
| 07:25 | metadata 无运行时效果 | partially-supported | lint 读 network_justification [doc: task-authoring.md:211] |
| 07:26 | 必填集两项 | supported | [code: taskspec.py:793,572] |
| 07:32 | HF namespace agents-last-exam | supported | [code: assets.py:33] |
| 07:34 | 数据体积与单文件上限 | not-explored | 数据侧与 [unknown] |
| 07:35 | 变体目录 100 base 加 22 变体 | not-explored | 数据侧 |
| 07:41 | main.py 导入 cua_bench | supported | [code: 01 main.py:12 import cua_bench as cb] |
| 07:42 | 旧 _secrets.json 侧车 | not-explored | 仅历史记录 |
| 07:43 | 旧网络默认开，新默认 no-network | partially-supported | 新侧 [code: taskspec.py:696]，旧侧属数据侧 |
| 07:49 | scripts scorer | partially-supported | 目录存在 [cmd]，评分器行为仅为记录 |
| 07:50 | reward.json 路径与两位小数 | supported | C1 reward.json 条目 |
| 07:51 | ResultRecord 2 版八状态 | supported | [code: result.py:61, verdict.py:19-41]，R1 版补了直引 |
| 07:52 | validate 零分与满分两次 | not-explored | 命令存在 [doc: 04 README.md:61-63]，双跑设置未验证 |
| 07:56-59 | 元数据缺口三段推断 | unsupported | metadata 可存任意键 [code: taskspec.py:796] |
| 07:64 | feat/tasks-v2 分支预览 | supported | [cmd: 01 .git/packed-refs:31 有 ref] |
| 07:65 | 规范承诺 Harbor 到 ALE 转换器 | partially-supported | 两句原文方向相反，无转换器随引擎 [doc: task-authoring.md:9-14, code: taskspec.py:523-525] |
| 07:66 | AgentHLE 私有界面 | not-explored | 仅原执行人记录 |
| 07:67-75 | 重做表 | partially-supported | 输入输出两格已按 C1 修正 |
| 07:81-82 | 机械化搬迁与补齐推荐字段 | partially-supported | 方向合理，仍属推断 |

## 第一轮 09 的行级审计

| 位置 | 主张 | 裁定 | 证据指针 |
| --- | --- | --- | --- |
| 09:7 | 转换器未随快照发布 | supported | [cmd: 全仓无 converter] |
| 09:8 | 103 对 500 差 397 与三选项 | partially-supported | 算术属数据侧，R1 未见批准路线 [doc: R1 brief] |
| 09:9 | 分类必须放 task.toml 之外 | unsupported | metadata 可存 [code: taskspec.py:796] |
| 09:13 | Docker 例外 8 任务 | supported | [doc: local-docker.html:123] |
| 09:14 | GPU 挂起措辞 | partially-supported | 见上核查项三 |
| 09:15 | egt710 allowlist 或本地化 | supported | [code: taskspec.py:696] |
| 09:18 | tasks-v2 分支 | supported | [cmd: packed-refs:31] |
| 09:19 | 拼写一致性问题 | supported | [code: assets.py:33 与 template org] |
| 09:21 | @task-params 不存在 | partially-supported | 引擎侧 grep 无命中，输入树未重扫 |
| 09:30 | 只接一个主模型提供方 | unsupported | 选谁开放 [doc: R1 brief]，机制兼容但无单一约束必要性 |
| 09:33 | P0-9 是管线阶段标号 | unsupported | 见上核查项四 |
| 09:40-47 | P0 到 P5 阶段表 | unsupported | 同上 |
| 09:51-53 | 1 GiB 门槛与两名审查者 | partially-supported | 阈值与人手未冻结 [doc: R1 brief] |
| 09:61-66 | Windows 分布证据 | partially-supported | 引擎部分正确，计数属数据侧 |
| 09:70-73 | Windows 建议保持 OPEN | supported | 与 R1 前提一致 |

## 第一轮 10 的行级审计

| 位置 | 主张 | 裁定 | 证据指针 |
| --- | --- | --- | --- |
| 10:9-12 | 四个输入摘要 | supported | 与冻结 HEAD 一致 [doc: 原执行人清单] |
| 10:14 | 关系链与 Canonical 来源句 | partially-supported | 需按 R1 前提改述，专家新产非官方复制 [doc: R1 brief] |
| 10:18 | 旧双文件包 cua-bench 钩子 | supported | [code: 01 main.py:12] |
| 10:19 | 新格式必填项 | supported | [code: taskspec.py:793,572] |
| 10:20 | 类别信息必须落格式之外 | unsupported | metadata 可存 |
| 10:21 | 新引擎承诺转换器未发布 | partially-supported | 只有双向转换句，无 shipped 承诺 [doc: task-authoring.md:9-14] |
| 10:27 | 103 加 397 头寸与三选项 | partially-supported | 见 09:8 |
| 10:34-38 | 提供方与网络发现 | supported | 各条已在上表核 |
| 10:42 | Windows 首轮只 71 建议，决定 OPEN | supported | 建议标注与开放状态合规 |
| 10:46-50 | 风险清单 | partially-supported | 转换器与数据体积部分属实，其余属推断 |

## 汇总数字

| 裁定 | 条数 |
| --- | --- |
| supported | 32 |
| partially-supported | 24 |
| unsupported | 10 |
| not-explored | 9 |

四个点名核查项的结果重述如下。

- 宿主可跑说法存在，处 06:89 与 06:90，均 unsupported。
- qemu 加 KVM 可用说法存在，处 06:90，unsupported。
- 无 GPU 预算说法存在，处 06:92 与 09:14，partially-supported，已成 open。
- P0-9 作管线阶段说法存在，处 09:33 与 09:40-47，unsupported。