# 15 平台架构、数据模型与 API 设计 v1

这份文件把第一波的产品功能地图落成可评审的平台骨架设计。它覆盖用户与权限、分层架构、数据库表、任务状态机、API 表面、专家工作台、资料隔离、Agent 建议、审核返修、冻结组包入库和管理统计。它不预先确定 HTTP 框架，也不把 Django、FastAPI、Dify 或 LangGraph 写成既定选型。

## 15.1 结论与范围

平台第一版采用分层骨架，业务规则放在 domain 层，SQL 放在 repo 层，外部副作用放在 adapter 层，合同常量放在 contracts 层。当前实现用 Python 标准库和 SQLite 跑通，目标数据库是 PostgreSQL。HTTP 适配层尚未绑定框架，接口表面先以资源和方法定义。

骨架已经能创建数据库、校验任务源结构、执行九态状态机、保存资料版本、记录审计事件和计算候选包哈希。14 项单元测试全部通过。它还不是完整产品：没有登录页、HTTP 路由、对象存储 S3 适配器、PostgreSQL 迁移脚本和前端页面。

P1 核心覆盖专家任务源编辑、资料上传、自动结构检查、专业评审、质量审核、冻结快照、组包校验和幂等入库。完整产品再加批次规划、运营看板、Agent 成本核算、外部评审门户和跨批次统计分析。

## 15.2 用户与权限

七类用户映射到角色码。专家 `expert` 只能编辑自己的草稿和资料；领域评审 `domain_reviewer` 在授权域内领取和退回；质量审核 `quality_reviewer` 做跨域质量判断和冻结；平台管理员 `platform_admin` 管账号、批次、组包和入库；工程接口人 `engineer` 只读交接合同和登记 Verifier；项目负责人 `project_lead` 看全局统计和例外批准；合作方接口人 `partner_viewer` 只看验收结果，不进入生产数据。

权限按 `(domain, subdomain, batch)` 三元组授权。`user_roles` 的 `scope_domain`、`scope_subdomain`、`scope_batch` 支持 `*` 通配。任务级权限从范围推导，不为每条任务写一行授权记录。这个设计让 500 条任务和 104 份合同不必产生几十万行权限数据。

专家不能改任务状态以外的生产字段。版本号、冻结哈希、包哈希、入库回执、审核结论由平台写。专家提交后只能通过返修路径修改，不能直接覆盖已提交版本。

## 15.3 分层架构

| 层 | 目录 | 职责 | 不做什么 |
| --- | --- | --- | --- |
| HTTP 适配 | 未绑定 | 路由、鉴权、请求解析、错误映射 | 不写业务规则 |
| domain | `platform/app/domain/` | 状态机、任务、资料、审核、审计、幂等 | 不拼 SQL |
| repo | `platform/app/repo/` | 参数化 SQL、行映射、事务内读写 | 不判断业务对错 |
| adapter | `platform/app/adapters.py` | 时间、ID、哈希、本地对象存储 | 不决定权限 |
| contracts | `platform/contracts/` | Canonical 字段、包合同、验证合同常量 | 不写数据库 |
| 数据库 | `platform/app/schema.sql` | 表、约束、触发器、索引 | 不承载业务文案 |

domain 层依赖 repo 与 contracts，不依赖 HTTP。这样同一套业务可以在 CLI、测试、后台任务和未来 HTTP 服务中复用。repo 层只接受已校验的参数，不把用户输入直接拼进 SQL。

`contracts_bridge.py` 统一规范 JSON 的序列化与点路径读写。字段名只出现在 contracts 和种子数据里，路由与仓储不散落字段名。A 线或 B 线合同升级时，替换 contracts 实现，历史 payload 仍按原版本保存。

## 15.4 数据模型

数据库有 20 张表，按职责分五组。

| 组 | 表 | 关键约束 |
| --- | --- | --- |
| 身份与批次 | users、roles、user_roles、batches | 邮箱唯一；角色范围三元组唯一；批次有配额与开闭时间 |
| 任务与版本 | tasks、task_versions | 状态受 CHECK 限制；版本主键 task_id+version_no；版本不可更新 |
| 资料 | materials、material_versions | role 三值；layer 四层；PII 四级；同文件第二次上传成新版本 |
| 检查与审核 | checks、reviews、assignments、review_items | 检查带 layer/code/severity；评审有轮次与结论；派单可撤回 |
| 生产与审计 | snapshots、packages、package_validations、ingest_records、agent_runs、agent_suggestions、audit_events、idempotency_keys | 快照不可变；包与校验分离；入库幂等；审计追加写 |

`tasks` 保存当前草稿、当前版本号、锁版本、退回次数和作废原因。`task_versions` 保存提交时的规范 payload 与内容哈希，提交后只读。`materials` 保存资料元数据，`material_versions` 保存字节哈希与存储键，版本 1 永远保留。

`packages` 与 `package_validations` 分开。包记录只存身份、布局、native_hash、候选 package_hash、构建来源和状态；校验报告单独存 L1 到 L5 的发现。`ingest_records` 存入库回执、包哈希、校验报告哈希、接收时间和接收人。三段哈希形成证据链。

`agent_runs` 存模型、提示版本、输入摘要、耗时与成本；`agent_suggestions` 存字段路径、建议值、置信度、状态、确认人和确认时间。没有确认行的建议不能写入 `task_versions`。

`audit_events` 追加写，记录 actor、role、action、object、前后状态、payload 和 request_id。`idempotency_keys` 以 actor、endpoint、key 唯一，保存请求哈希与首次响应。重复请求返回首次响应，不同请求体复用同一个 key 会被拒绝。

## 15.5 任务状态机

任务有九个主状态和两个旁路。主链是 `draft -> submitted -> auto_checked -> in_review -> approved -> frozen -> packaged -> package_validated -> ingested`。`returned` 是返修旁路，`void` 是冻结前作废旁路。

`submit` 由专家执行，只能从 draft 或 returned 出发。`auto_check_pass` 与 `auto_check_fail` 由系统执行。`start_review` 由领域评审领取。`domain_pass` 后仍在 `in_review`，但进入质量审核队列。`quality_pass` 到 approved，`freeze` 到 frozen。冻结后 `package` 到 packaged，`validate_pass` 到 package_validated，`ingest` 到 ingested。

冻结后不能退回。组包失败回到 frozen，校验失败也回到 frozen，修正后重新组包。入库是幂等的：同一个 task_id 与 task_version，同一个 package_hash 返回首次回执；哈希不同则拒绝并告警。

状态机表是唯一决定状态迁移的地方。任何服务动作都调用 `assert_can`，不直接写 `tasks.state`。这样 20 多个动作的合法性可以在一屏内审完。

## 15.6 API 表面

HTTP 框架未定，下面按资源与方法定义接口。所有写接口要求 `Idempotency-Key`，所有响应带 `request_id`，所有列表支持分页。鉴权用会话或令牌，具体机制在选型后定。

| 方法 | 路径 | 角色 | 用途 |
| --- | --- | --- | --- |
| POST | `/api/v1/sessions` | 公开 | 登录，返回会话与角色 |
| GET | `/api/v1/me` | 已登录 | 当前用户、角色、范围 |
| GET | `/api/v1/tasks` | 专家/评审/管理员 | 按状态、域、批次筛选 |
| POST | `/api/v1/tasks` | 专家 | 创建草稿 |
| GET | `/api/v1/tasks/{id}` | 有权限者 | 任务详情与当前草稿 |
| PATCH | `/api/v1/tasks/{id}` | 专家 | 按字段路径更新草稿 |
| POST | `/api/v1/tasks/{id}/validate` | 专家 | 结构检查，返回阻断与警告 |
| POST | `/api/v1/tasks/{id}/submit` | 专家 | 提交并生成不可变版本 |
| POST | `/api/v1/tasks/{id}/return` | 评审/审核 | 退回并写原因 |
| POST | `/api/v1/tasks/{id}/approve` | 质量审核 | 质量通过 |
| POST | `/api/v1/tasks/{id}/freeze` | 质量审核/管理员 | 冻结快照 |
| POST | `/api/v1/materials` | 专家 | 登记资料元数据 |
| POST | `/api/v1/materials/{id}/versions` | 专家 | 上传新版本，返回哈希 |
| GET | `/api/v1/materials/{id}` | 有权限者 | 元数据与版本列表 |
| GET | `/api/v1/checks/{task_id}` | 有权限者 | 自动检查结果 |
| GET | `/api/v1/reviews/queue` | 评审 | 领取队列 |
| POST | `/api/v1/reviews/{id}/claim` | 评审 | 领取任务 |
| POST | `/api/v1/reviews/{id}/decision` | 评审 | 通过、退回、拒收 |
| GET | `/api/v1/packages/{task_id}` | 管理员/工程 | 包记录与哈希 |
| POST | `/api/v1/packages/{task_id}/build` | 管理员/系统 | 从冻结快照组包 |
| POST | `/api/v1/packages/{task_id}/validate` | 管理员/系统 | 跑 L1 到 L5 |
| POST | `/api/v1/ingest` | 管理员/系统 | 幂等入库 |
| GET | `/api/v1/admin/stats` | 负责人/管理员 | 生产、入库、验收计数 |

错误响应统一为 `code`、`message`、`details`、`request_id`。业务错误码稳定，前端按码处理。权限错误不返回资源是否存在，避免枚举。

## 15.7 专家工作台流程

专家进入后先看分配到的域、子域、批次和任务列表。创建任务后进入任务源编辑器，按十块分组填写。编辑器每块有必填标记、示例、常见失败提示和字段级帮助。资料区支持上传、引用公开 URL、登记合成资料和查看许可状态。

专家点“结构检查”时，平台跑 Canonical 结构校验、资料存在性、许可完整性、PII 等级、重复任务和交付物路径检查。阻断项必须修复，警告项可以带理由提交。检查结果按字段定位，点击跳到对应输入框。

专家点“提交”时，平台生成新版本、计算内容哈希、锁定草稿、写审计事件，并进入自动检查队列。提交后专家只能查看，不能直接改。被退回后，专家看到退回原因、评审意见和需要修改的字段，修改后再次提交生成新版本。

Agent 面板只给建议。访谈、追问、结构化、预检和审核辅助五项能力都写 `agent_suggestions`，不直接改任务源。专家逐字段确认后，平台才把确认值写入草稿。自动采纳必须为 0。

## 15.8 资料上传与隔离

资料分四层：raw 原始件、deidentified 脱敏件、work 工作件、reference 参考件。原始件只存一次，脱敏件与工作件是派生版本，参考件只对评审和工程可见。每次上传计算 sha256，按内容寻址存储，重复字节收敛到同一个对象。

单文件上限 20 GiB，分片 64 MiB，失败重试三次。大文件先进入暂存区，校验哈希后再登记版本。对象存储键不暴露给专家，下载走短期签名 URL 或平台代理。

PII 分四级。高危 PII 必须有隐私安全确认才能登记。许可类型六值，`pending` 的资料不能进入可计数包，`restricted` 可以入库但 `counted_in_500=false` 并带 scope_exception。

Agent 视图只挂载 input 与 software。reference、评分依据、`PACKAGE.json` 的参考清单和敏感元数据不进入 Agent 视图。L4 校验用 `PKG_AGENT_VIEW_LEAK` 阻断泄漏。

## 15.9 审核与返修

自动检查通过后进入领域评审队列。派单按域、子域、负载和利益冲突匹配。评审领取后有 SLA，默认 5 个工作日。评审可以专业通过、退回或拒收。专业通过后进入质量审核，质量审核可以批准、退回或升级。

退回必须写原因、问题字段和建议修改方向。任务回到 returned，专家修改后重新提交。退回次数记录在 `tasks.return_count`。两轮返修默认包含在合同内，超过两轮由领域负责人决定继续、换人或作废。

审核记录分 `reviews` 与 `review_items`。前者是一次评审，后者是逐项结论。审核证据、签字和例外批准留在数据库，不写进 ALE-data 包。`handoff.json` 只带审核结论摘要。

## 15.10 冻结、组包与入库

冻结时平台生成快照，记录任务版本、资料版本、哈希、审核结论和冻结人。快照不可变。组包只读冻结快照，不读草稿，不读未冻结资料。

组包流程是：读快照与十块任务源；按 entrypoints 复制 input、software、reference；生成 `PACKAGE.json` 与四个边车；计算候选 native_hash 与 package_hash；在临时目录跑 L1 到 L5；通过后原子移动；同版本同哈希幂等返回。

L1 查结构、路径安全和入口存在；L2 查域、子域、版本与 contract.kind；L3 查文件清单、哈希和 manifest 一致；L4 查许可、PII、来源、绝对路径、答案泄漏与 Agent 视图；L5 查版本冲突、supersedes 和 counted_in_500 条件。单包超过 5 GiB 阻断，超过 1 GiB 警告，12 GiB 级资产需负责人批准 external_ref。

入库写 `ingest_records`，记录 package_hash、validation_report 哈希、接收时间和接收人。重复入库同哈希返回首次回执；哈希不同拒绝。入库成功不等于计入 500，`counted_in_500` 只由合作方验收回执改写。

## 15.11 管理与统计

管理员看批次进度、域配额、任务状态分布、评审负载、退回率、冻结数、组包失败、入库数、验收数。统计口径分生产完成与验收完成两个计数器：`produced_ingested` 是审核加包校验加入库，`accepted` 是四道门全过。

Agent 统计看采纳率、净节省、误报、漏报、单条成本、延迟分位。阻断级漏报必须为 0。自动采纳必须为 0。Agent 成本按模型调用和 token 计，不写进专家手册。

审计查询按 actor、对象、动作、时间范围和 request_id 过滤。审计导出用于离线复核，不修改原记录。备份与恢复在 P1 后半段做，先保证 SQLite 本地快照和导出。

## 15.12 安全与边界

平台不转 Harbor、不建镜像、不跑任务、不判分、不产生运行分数。平台只负责验证意图、包、校验和入库。运行环境构造、框架转换、运行和评分属于工程侧，通过 handoff 合同交接。

平台不决定专业价值、不替专家签字、不替合作方验收。Agent 不决定业务价值、专业标准、资料授权、高风险隐私版权安全、验证器是否表达目标。所有 Agent 输出都是建议。

权限检查在 domain 层做，不依赖前端隐藏按钮。对象存储路径做穿越检查。SQL 全部参数化。审计追加写，冻结快照与任务版本禁止 UPDATE。这些规则在 schema 触发器和 repo 层双重约束。

## 15.13 P1 与完整产品

P1 核心是专家能完成一条任务从草稿到入库的最小闭环：任务源编辑、资料上传、结构检查、提交、评审、审核、冻结、组包、校验、入库。P1 加固是权限细化、批量操作、统计看板、审计导出和故障恢复。

完整产品再加批次规划与配额调度、跨批次分析、外部评审门户、合作方验收工作台、Agent 成本中心、资料库检索与复用、模板市场和多语言界面。完整产品不改变 P1 的合同与状态机。

## 15.14 测试与运行

当前测试命令：

```bash
PYTHONPATH=platform python3 -m unittest discover -s platform/tests -v
```

14 项测试覆盖数据库建表、非法状态拒绝、主链状态迁移、返修重提、跳步拒绝、空任务源、身份必填、资料许可必填、native_hash 顺序无关、mode 影响哈希、package_hash 忽略自身字段、稳定字段改变哈希、对象存储收敛和路径穿越拒绝。

这些测试证明骨架的接缝，不证明完整业务。HTTP、鉴权、PostgreSQL、S3、并发和前端页面仍待实现。

## 15.15 技术选型与未决

当前实现刻意只用标准库：sqlite3、hashlib、json、os、secrets、shutil、uuid。这样骨架不依赖未安装的框架，评审可以直接跑。目标生产环境是 PostgreSQL，数据库访问已收在 repo 层，迁移时替换驱动与 DDL 类型。

HTTP 框架、任务队列、对象存储、身份提供方和前端框架都未定。选择时看四项：与现有团队技能匹配、能跑 22 并发、支持幂等与审计、能在本地和云端一致复现。Django、FastAPI、Dify、LangGraph 都只是候选，不在本轮锁定。

未决事项包括：PostgreSQL 迁移工具、会话与令牌机制、S3 适配器、22 并发压测、审计链离线校验、前端页面清单、Agent 调用网关、专家工作台的文件预览、审核派单算法和统计口径。

## 15.16 版本记录

v1 草案，2026-11-14。首版定义七类用户、六层架构、20 张表、九态状态机、22 个 API 资源动作、专家工作台流程、资料隔离、审核返修、冻结组包入库和管理统计。骨架 14 项测试通过。HTTP 与 PostgreSQL 选型未定。
