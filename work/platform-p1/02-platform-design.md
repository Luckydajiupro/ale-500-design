# 平台 P1 设计

本文件把需求落成可开发的设计。范围是五个核心模块，其余先手工。设计目标是让类目差异靠配置表达，让冻结快照离开平台也能读。

## 1. 设计原则

| 原则 | 做法 | 代价 |
| --- | --- | --- |
| 状态机固定，类目可变 | 九个状态（含 `void`）对所有类目一致，差异放进类目配置 | 个别类目要接受统一流程 |
| 原件不可变，版本叠加 | 资料、任务源、快照都按版本存，不覆盖 | 存储多一倍 |
| 交接靠文件，不靠接口 | 导出包是唯一交接物，工程不需要连平台 | 导出要一次做对 |
| 平台不碰运行 | 环境只描述意图，验证在工程侧 | 平台不能承诺任务可跑 |
| 单机优先 | 一台 Linux 加对象存储，Docker Compose 部署 | 横向扩展要改架构 |

规模上限按 500 条任务、40 个账号、2 TiB 资产设计。超过这个量再谈集群。

## 2. 架构

```
浏览器（SSR 页面 + 少量 JS）
        |
   Nginx（TLS、限流、静态文件）
        |
   FastAPI 应用（4 个 worker）
      |                  |
Postgres 16         对象存储（S3 兼容）
元数据、状态、审计    资料原件、快照 zip
      |
   后台任务（同机 cron worker）
   自动检查、邮件、备份、快照构建
```

### 技术栈

| 层 | 选择 | 理由 |
| --- | --- | --- |
| Web | FastAPI + Jinja2 SSR | 40 人内部系统，SSR 足够，前端复杂度低 |
| 数据库 | Postgres 16，JSONB 存任务源 | 十块结构半结构化，JSONB 加快照哈希稳定 |
| 对象存储 | S3 兼容（MinIO 或云对象存储） | 大文件不进数据库，便于异地备份 |
| 队列 | Postgres 表加 cron worker | 不引入 Redis，少一个组件 |
| 部署 | Docker Compose，单台 Linux | 1 名工程师可运维 |
| 迁移 | Alembic | 结构变更可回滚 |
| 认证 | 邮箱魔法链接 + 服务端会话 | 不维护密码，专家上手快 |

### 为什么不上集群

500 条任务、40 个账号、峰值 10 个并发页面请求。单台 8 vCPU、32 GiB 的机器足够。集群会带来服务发现、分布式事务、日志聚合三套运维负担，与两周 MVP 冲突。

## 3. 模块

| 模块 | 范围 | 第一版做法 |
| --- | --- | --- |
| M1 认证与权限 | 登录、角色、任务级授权、会话 | 邮箱链接，角色表，中间件校验 |
| M2 任务源编辑器 | 十块表单、校验、版本、提交门禁 | 服务端渲染表单，JSONB 存版本 |
| M3 资料上传 | 分片上传、哈希、许可、扫描 | 直传对象存储，服务端签发临时凭证 |
| M4 评审队列 | 检查结果、风险路由、意见、争议 | 待办列表加结构化表单 |
| M5 冻结与导出 | 快照、校验、交接包、回执 | 后台任务构建 zip，清单含哈希 |
| M6 审计与报表 | 审计、看板、导出 | 审计表加只读 SQL 视图 |
| M7 Agent 接口 | 建议、检查、摘要 | 独立 token，只写建议表 |
| M8 管理配置 | 类目、评审池、账号、配额 | 简单后台表单 |

第一版只做 M1 到 M5 的 MVP 路径。M6 只做审计写入与查询，看板用 SQL 出数。M7 只开一个建议接口。M8 用配置文件加管理员脚本，不做界面。

## 4. 数据模型

### 核心表

| 表 | 关键列 | 约束 |
| --- | --- | --- |
| `users` | id, email, name, org, roles, status, created_at | email 唯一，status 取 active, disabled |
| `categories` | domain_code PK, name_zh, profile, active | domain_code 取 14 个枚举值 |
| `subdomains` | domain_code, subdomain_code, name_zh, active | 联合主键，外键到 categories |
| `tasks` | id, task_id, domain_code, subdomain_code, owner_id, batch_id, state, current_version, risk_tier, void_reason | task_id 唯一，state 取 9 个枚举值 |
| `task_versions` | id, task_id, version, source, source_hash, created_by, created_at, frozen | 唯一 (task_id, version)，frozen 后不可写 |
| `materials` | id, task_id, version, material_id, kind, path, sha256, bytes, license, pii_level, scan_status | 唯一 (task_id, material_id, version) |
| `checks` | id, task_id, version, check_code, status, evidence_path, duration_ms, created_at | 唯一 (task_id, version, check_code, created_at) |
| `reviews` | id, task_id, version, reviewer_id, review_role, verdict, submitted_at, due_at | verdict 取 pass, return, escalate |
| `review_items` | id, review_id, block, field, severity, evidence_level, comment, resolved | severity 取 blocking, non_blocking |
| `assignments` | id, task_id, reviewer_id, review_role, due_at, status | 唯一 (task_id, reviewer_id, review_role) |
| `snapshots` | id, task_id, version, manifest, zip_sha256, bytes, created_by, created_at | 唯一 (task_id, version) |
| `handoffs` | id, snapshot_id, target_format, status, receipt, gaps, updated_at | status 取 pending, accepted, rejected |
| `batches` | id, name, due_date, state, released_by, released_at | state 取 open, released, closed |
| `audit_events` | id, actor_id, action, object_type, object_id, before_hash, after_hash, ts, request_id, prev_hash, hash | 只插入，不更新 |
| `agent_suggestions` | id, task_id, version, block, field, value, model, model_version, prompt_hash, confidence, status, confirmed_by | status 取 pending, accepted, rejected |

### 索引

- `tasks(state, domain_code)` 支持看板。
- `assignments(reviewer_id, status, due_at)` 支持评审待办。
- `audit_events(object_type, object_id, ts)` 支持时间线还原。
- `materials(task_id, sha256)` 支持引用完整性检查。

### 任务标识

- `task_id` 形如 `engineering/building_energy_retrofit_01`。
- 域名取 14 个 `domain_code`，子域取 55 个 `subdomain_code`。
- slug 规则 `^[a-z0-9][a-z0-9_]{2,60}$`，全域唯一。
- 首次冻结后 `task_id` 不可改。改标识等于新任务。

## 5. 状态机

### 状态

| 状态 | 含义 | 谁能进入 |
| --- | --- | --- |
| `draft` | 专家编辑中 | 作者 |
| `submitted` | 已提交，等待自动检查 | 作者 |
| `auto_checked` | 自动检查完成，等待路由 | 系统 |
| `in_review` | 评审中 | 系统，或管理员手工指派 |
| `approved` | 评审通过，等待批次放行 | 系统 |
| `frozen` | 已冻结，快照不可变 | 负责人或质量审核人 |
| `handed_off` | 工程已接收 | 工程回执 |
| `returned` | 退回修改 | 评审人或质量审核人 |
| `void` | 终止，不计数 | 负责人 |

`void` 是第九个状态，只给负责人用，用于重复任务或专家退出。平台计数只算走到 `frozen` 与 `handed_off` 的生产进度，不等于项目 500 条验收数。500 只算合作方四道门全部通过的任务。

### 迁移

| 从 | 到 | 角色 | 守卫 | 副作用 |
| --- | --- | --- | --- | --- |
| draft | submitted | 作者 | 十块齐全，必填项通过，资料许可齐全 | 生成版本，跑九项检查 |
| submitted | auto_checked | 系统 | 检查任务完成 | 写检查结果，算风险层 |
| auto_checked | in_review | 系统 | 无阻断项 | 按风险层建评审槽位 |
| auto_checked | returned | 系统 | 存在阻断项 | 退回理由指向字段 |
| in_review | approved | 系统 | 所需评审全部通过，无未决阻断项 | 写批准时间 |
| in_review | returned | 评审人 | 至少 1 条阻断项 | 进入下一轮 |
| approved | frozen | 负责人或质量审核人 | 批次已放行，快照构建成功 | 生成不可变快照 |
| frozen | handed_off | 工程 | 回执校验通过 | 写回执与缺口 |
| returned | draft | 作者 | 无 | 版本加 1，保留旧轮次 |
| frozen | approved | 负责人 | 只允许在 24 小时内撤回 | 作废快照，留审计 |
| 任意 | void | 负责人 | 填写理由 | 不计入配额，保留数据 |

### 版本规则

- 每次提交加 1 版。版本号只增不减。
- 冻结针对某一版。快照 id 为 `{task_id}@v{version}`。
- 冻结后改内容必须新建任务版本，重新走评审。平台不提供"解冻编辑"。

## 6. 权限矩阵

| 动作 | 专家 | 领域评审 | 质量审核 | 工程 | 负责人 | 管理员 |
| --- | --- | --- | --- | --- | --- | --- |
| 建任务 | 自己的槽位 | 否 | 否 | 否 | 是 | 是 |
| 编辑任务源 | 自己的草稿与退回 | 否 | 否 | 否 | 否 | 否 |
| 上传资料 | 自己的任务 | 否 | 否 | 否 | 否 | 是 |
| 提交 | 自己的任务 | 否 | 否 | 否 | 否 | 否 |
| 看任务 | 自己的 | 被分配的 | 全部 | 已冻结 | 全部 | 全部 |
| 写评审 | 否 | 被分配的 | 争议与抽查 | 否 | 否 | 否 |
| 批准 | 否 | 是（自己那票） | 是 | 否 | 否 | 否 |
| 冻结 | 否 | 否 | 建议 | 否 | 是 | 否 |
| 导出 | 否 | 否 | 是 | 是 | 是 | 是 |
| 改类目配置 | 否 | 否 | 否 | 否 | 是 | 是 |
| 看审计 | 自己的任务 | 自己的评审 | 全部 | 相关任务 | 全部 | 全部 |

规则：一个人不能在同一任务上既是作者又是评审人。同机构评审人默认回避，负责人可书面豁免。

## 7. 任务源十块

任务源是一个 JSON 文档，十块固定。字段名用英文，值可以是中文。校验规则写在字段表里，服务端与前端共用一份 schema。

### 7.1 identity

| 字段 | 类型 | 必填 | 校验 |
| --- | --- | --- | --- |
| task_id | string | 是 | 匹配 `{domain}/{slug}`，全域唯一，冻结后不可改 |
| version | integer | 是 | 大于 0，服务端生成 |
| domain_code | enum | 是 | 14 个值之一 |
| subdomain_code | enum | 是 | 属于该 domain 的 55 个子域之一 |
| title_zh | string | 是 | 8 到 80 字，不含换行 |
| title_en | string | 否 | 8 到 120 字符 |
| language | enum | 是 | zh-CN, en, 双语 |
| batch_id | string | 是 | 属于已建批次 |
| owner_expert_id | uuid | 是 | 账号状态 active |
| difficulty_rationale | string | 是 | 50 到 500 字，说明为什么不是问答 |

### 7.2 scenario

| 字段 | 类型 | 必填 | 校验 |
| --- | --- | --- | --- |
| role | string | 是 | 具体岗位，不接受"专业人士" |
| organization_context | string | 是 | 100 到 800 字 |
| trigger | string | 是 | 说明为什么现在要做 |
| audience | string | 是 | 交付物给谁看 |
| constraints | array | 是 | 至少 2 条，每条 10 到 200 字 |
| out_of_scope | array | 是 | 至少 1 条，防止任务发散 |
| realism_evidence | string | 是 | 说明场景来自哪类真实工作，附来源或经验说明 |

### 7.3 materials

| 字段 | 类型 | 必填 | 校验 |
| --- | --- | --- | --- |
| material_id | string | 是 | `M-` 加 3 位序号，任务内唯一 |
| kind | enum | 是 | dataset, document, image, code, url, template, other |
| role | enum | 是 | input, reference, template |
| path | string | 是 | 相对路径，禁止 `..`，长度小于 200 |
| sha256 | string | 是 | 64 位十六进制，与服务端计算一致 |
| bytes | integer | 是 | 大于 0，不超过类目上限 |
| license | object | 是 | type 取 public_domain, cc_by, proprietary, internal, synthetic |
| license.redistribution | boolean | 是 | 为 false 时禁止进入导出包 |
| source_url | string | 条件 | license 非 synthetic 时必填，http 或 https |
| pii_level | enum | 是 | none, low, medium, high |
| deidentification | string | 条件 | pii_level 非 none 时必填，说明方法 |
| irb | object | 条件 | 涉及人类受试数据时必填，含 protocol_id |
| used_by | array | 是 | 引用该资料的 operation 或 deliverable id |

规则：至少 1 份 `role=input`。`pii_level=high` 且未脱敏时禁止提交。`redistribution=false` 的资料只允许平台内存量保存，导出前必须替换或移除。

### 7.4 operations

| 字段 | 类型 | 必填 | 校验 |
| --- | --- | --- | --- |
| step_no | integer | 是 | 从 1 连续递增 |
| actor | enum | 是 | human, agent, system |
| action | string | 是 | 动词开头，10 到 200 字 |
| tool | string | 否 | 具体工具或"手工" |
| inputs | array | 是 | 引用 material_id 或上一步输出 |
| expected_state | string | 是 | 可观察的结果，不写"处理好" |
| checkpoint | boolean | 是 | 是否为可验证检查点 |
| time_estimate_min | integer | 是 | 1 到 480 |

规则：至少 3 步。至少 1 个 checkpoint。所有 deliverable 必须能追到某一步。

### 7.5 deliverables

| 字段 | 类型 | 必填 | 校验 |
| --- | --- | --- | --- |
| deliverable_id | string | 是 | `D-` 加序号 |
| path | string | 是 | 相对路径，扩展名在允许列表 |
| format | enum | 是 | docx, xlsx, pptx, pdf, csv, json, py, md, png, other |
| description | string | 是 | 20 到 300 字 |
| produced_by_step | integer | 是 | 必须是已有 step_no |
| mandatory | boolean | 是 | 至少 1 个为 true |
| acceptance_ref | array | 是 | 引用 criterion_id，至少 1 条 |

### 7.6 success_criteria

| 字段 | 类型 | 必填 | 校验 |
| --- | --- | --- | --- |
| criterion_id | string | 是 | `C-` 加序号 |
| dimension | enum | 是 | correctness, completeness, format, professional_judgment, process |
| check_method | enum | 是 | auto_script, artifact_diff, llm_judge, human_rubric |
| weight | integer | 是 | 1 到 100，全任务合计 100 |
| threshold | string | 是 | 可判定的阈值，不接受"合理" |
| evidence_required | enum | 是 | E1 到 E5，对应 docs/03 证据五档 |
| verifier_hint | string | 条件 | check_method 非 human_rubric 时必填 |
| critical | boolean | 是 | 至少 1 条为 true |

规则：权重合计必须为 100。每条至少 1 个 critical。`check_method=human_rubric` 时必须写评分档位。

### 7.7 environment

| 字段 | 类型 | 必填 | 校验 |
| --- | --- | --- | --- |
| os | enum | 是 | linux, windows, macos, any |
| os_version | string | 条件 | os 非 any 时必填 |
| gui_required | enum | 是 | yes, no, unknown |
| gpu | object | 是 | required, vram_gb, cuda_version |
| software | array | 是 | name, version, license_type, install_method |
| network | object | 是 | mode 取 none, staged-local, online-required, public-ref |
| network.endpoints | array | 条件 | mode 非 none 时必填，列域名与用途 |
| network.justification | string | 条件 | online-required 时必填，20 到 300 字 |
| resources | object | 是 | cpu, ram_gb, disk_gb, time_limit_min |
| nested_virt | boolean | 是 | 是否需要 KVM |
| external_services | array | 否 | name, mode, host, data_flow |

规则：`gui_required=unknown` 时风险层不得为 low，按 docs/03 处理。`network.mode=online-required` 自动进高风险。`gpu.required=true` 且 `os!=windows` 时提示复核，不阻断。

### 7.8 review

| 字段 | 类型 | 必填 | 校验 |
| --- | --- | --- | --- |
| risk_tier | enum | 是 | low, medium, high, unknown |
| tier_rationale | string | 是 | 30 到 300 字，逐条对应触发规则 |
| required_reviewers | array | 是 | role, domain, count |
| reviews | array | 是 | 评审记录摘要，只读 |
| sign_offs | object | 是 | content, domain, engineering, license 四类签署 |
| open_issues | array | 是 | 未决问题，冻结前必须清空或降级为 known_gap |

规则：`sign_offs` 缺 license 时禁止提交。`open_issues` 中存在 blocking 项时禁止冻结。

### 7.9 provenance

| 字段 | 类型 | 必填 | 校验 |
| --- | --- | --- | --- |
| author_type | enum | 是 | human, agent_assisted |
| agent_runs | array | 条件 | agent_assisted 时至少 1 条 |
| agent_runs[].model | string | 是 | 模型名与版本 |
| agent_runs[].prompt_hash | string | 是 | 64 位十六进制 |
| agent_runs[].output_ref | string | 是 | 指向建议或草稿 |
| agent_runs[].human_confirmed | boolean | 是 | 未确认的输出不能进入任务源 |
| sources | array | 是 | citation, url, accessed_at, evidence_level |
| originality | object | 是 | not_copied, similar_check_ref |
| revision_history | array | 是 | 版本、作者、时间、摘要 |

### 7.10 handoff

| 字段 | 类型 | 必填 | 校验 |
| --- | --- | --- | --- |
| target_format | enum | 是 | ale_task_toml, harbor, other |
| target_schema_version | string | 是 | 与阶段 2 冻结版本一致 |
| engine_commit | string | 是 | 40 位十六进制 |
| files_expected | array | 是 | 相对路径列表 |
| converter_version | string | 条件 | 工程填写，未转换时为空 |
| known_gaps | array | 是 | 已知不可执行项，冻结前必须列全 |
| execution_notes | string | 否 | 给工程的注意事项 |
| secrets_attestation | boolean | 是 | 必须为 true，声明无密钥与令牌 |
| frozen_snapshot_id | string | 是 | 冻结时生成 |

## 8. 类目差异怎么配置

类目差异只允许出现在四处：必填字段、资产上限、评审角色、风险规则。状态机、权限、快照格式对所有类目一致。

### 配置结构

```json
{
  "domain_code": "agriculture_env",
  "display_name": "农业与环境",
  "subdomains": ["env_water", "precision_agriculture"],
  "asset_cap_gib": 2,
  "asset_cap_override_gib": 12,
  "allowed_os": ["linux", "windows"],
  "gui_flag_required": true,
  "gpu_allowed": false,
  "verifier_types": ["script", "checker", "scorer", "hook-evaluator", "evaluator"],
  "required_review_roles": ["domain_reviewer"],
  "risk_rules": [
    {"when": "asset_bytes > 1GiB", "tier": "high"},
    {"when": "network.mode == 'online-required'", "tier": "high"},
    {"when": "gui_required == 'unknown'", "tier": "unknown"}
  ],
  "handoff_notes": "环境模型需附运行参数与单位说明"
}
```

### 新类目上线步骤

1. 管理员新增 `categories` 行与 `subdomains` 行。
2. 指定评审池与备用评审人。
3. 设定资产上限与风险规则。
4. 用一条样例任务走完 `draft` 到 `frozen`。
5. 记录配置变更审计。

验收：不改代码、不重启服务，30 分钟内可建第一条任务。这条验收对应 NFR-6 与 AT-03。

### 为什么不做成每类目一套状态机

500 条任务跨 13 个类目。每类一套状态机意味着 13 套测试、13 套权限、13 套导出。改动一次要回归 13 次。固定状态机加配置，代价是个别类目要接受统一流程。这个代价可以接受。

## 9. 评审路由

### 风险层判定

| 层 | 触发条件（任一） | 评审配置 |
| --- | --- | --- |
| high | 隐私 high，许可受限，online-required，GPU，资产大于 1 GiB，GUI unknown，类目首批任务 | 2 名评审，1 名工程复核，全量人工 |
| medium | Windows，GUI yes，专有软件，资产 200 MiB 到 1 GiB，含专业判断交付物 | 1 名领域评审 |
| low | 以上都不满足，且自动检查全过 | 1 次抽查，抽样率由负责人定 |
| unknown | 信息不足，无法判定 | 按 high 处理，补齐信息后重判 |

抽样率在试点期设为 100%。docs/03 尚未冻结抽样率，平台把抽样率做成配置项，默认 30%，试点期手动改 100%。这不违反"试点前不冻结审核比例"。

### 分配规则

1. 按 `subdomain_code` 找评审池。
2. 排除作者、同机构、近 90 天有合作记录的人。
3. 按当前负载取最闲的 1 到 2 人。
4. 无可用评审人时，升级给质量审核人手工指派。

### 时限

- 领域评审 3 个工作日。
- 质量审核 2 个工作日。
- 工程回执 5 个工作日。
- 超时进入负责人看板的红色列表。

## 10. 快照与导出

### 快照结构

```
snapshot.zip
  manifest.json
  task_source.json
  instruction.md
  materials/index.csv
  materials/<material_id>/<filename>
  reviews/review_<id>.json
  checks/check_<code>.json
  provenance/agent_runs.json
  handoff/contract.json
  hashes.sha256
  README.md
```

### manifest 字段

| 字段 | 说明 |
| --- | --- |
| snapshot_id | `{task_id}@v{version}` |
| task_id, version | 与任务一致 |
| created_at | ISO 8601，UTC |
| schema_version | 任务源 schema 版本 |
| category_profile_hash | 冻结时类目配置的哈希 |
| source_hash | 任务源 JSON 的规范化哈希 |
| files | 路径、sha256、字节数，按路径排序 |
| review_ids, check_ids | 引用的评审与检查 |
| frozen_by | 操作人 id |
| known_gaps | 从 handoff 块复制 |

### 可复现要求

- 文件按路径排序写入。
- zip 内时间戳统一为 1980-01-01。
- JSON 用 UTF-8、无 BOM、键排序、缩进 2 空格。
- 同一版本重建快照，`zip_sha256` 必须一致。

### 导出与回执

导出包就是快照加一份 `handoff/contract.json`。工程侧不需要连平台。回执包含 `run_id`、处理结果、缺口列表、时间。回执写回 `handoffs` 表，状态变 `handed_off`。

导出前检查：评审齐全、检查无阻断、许可允许再分发、隐私已处理、`known_gaps` 已列。任一条不满足，导出按钮禁用并列出原因。

### 回执缺口

工程发现字段缺项时提交 `handoff_gap`。任务退回 `approved`，作者补字段后生成新版本。平台不允许工程直接改快照。

## 11. 审计

- 每条写操作产生一条 `audit_events`，含操作人、对象、前后哈希、请求 id、时间。
- 事件按 `prev_hash` 串成哈希链。每日把链头哈希写入对象存储的日期文件。
- 审计只插入，不更新，不删除。保留期暂定 3 年，待负责人确认。
- 导出提供 CSV 与 JSON 两种格式，字段与页面一致。

审计覆盖的最小集合：登录、失败登录、角色变更、任务创建、字段修改、资料上传与删除、提交、评审、裁决、冻结、导出、回执、配置变更。

## 12. Agent 工具边界

### 能做什么

- 读任务源与资料，生成字段草稿建议。
- 跑九项自动检查中的文本类检查，输出证据位置。
- 汇总评审意见，标出重复与冲突。
- 按规则建议风险层与评审人。

### 不能做什么

- 不能提交、批准、冻结、导出。
- 不能修改许可、隐私级别、签署状态。
- 不能删除资料或审计。
- 不能替专家判断专业正确。
- 不能把未确认的建议写入任务源。

### 接口约束

| 约束 | 做法 |
| --- | --- |
| 凭证 | 每个 Agent 一个 token，绑定任务范围，90 天轮换 |
| 写权限 | 只能写 `agent_suggestions`，不能写 `task_versions` |
| 记录 | 模型名、版本、提示哈希、输入哈希、置信度、耗时全部入库 |
| 人工确认 | 建议被作者接受才合并，合并动作记审计 |
| 限流 | 每任务每小时 60 次调用，超限排队 |

## 13. 失败与恢复

| 失败 | 处理 |
| --- | --- |
| 上传中断 | 分片续传，已传分片保留 24 小时 |
| 快照构建中断 | 临时目录清理，任务停在 `approved`，可重试 |
| 数据库故障 | 每日全量备份加 WAL 归档，RPO 24 小时 |
| 对象存储故障 | 开启版本控制，误删可恢复 |
| 重复冻结请求 | 幂等键，第二次返回同一快照 |
| 邮件失败 | 出站表重试 3 次，失败进管理员待办 |

## 14. 第一版不做的

- 不做富文本协同编辑。
- 不做自动评审分配算法，管理员手工指派。
- 不做多语言界面。
- 不做移动端适配。
- 不做单点登录，邮箱链接够用。
- 不做任务市场与对外 API。

这些都不影响 500 条生产。需要时再加。
