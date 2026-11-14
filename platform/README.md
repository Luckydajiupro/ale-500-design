# ALE 专家工作台

这份文件说明 `platform/` 下的本地专家工作台。它是第三波的运行骨架，不是最终生产部署。

## 启动

```bash
cd platform
python3 -m venv ../.venv
../.venv/bin/pip install -r requirements.txt
ALE_DB_PATH=$PWD/var/platform.db ../.venv/bin/python run.py
```

打开 `http://127.0.0.1:8000`。首次启动会建库并写入演示账号。

演示账号的密码统一为 `AleDemo123!`：

| 邮箱 | 角色 |
| --- | --- |
| `expert@ale.local` | 专家（商业会计） |
| `expert2@ale.local` | 专家（工程） |
| `reviewer@ale.local` | 领域评审 |
| `quality@ale.local` | 质量审核 |
| `admin@ale.local` | 平台管理员 |
| `lead@ale.local` | 项目负责人 |

## 已实现的业务动线

专家可以登录、新建任务、编辑结构化任务源、保存草稿、上传资料、运行自动检查、生成并逐条确认 Agent 建议、提交评审。领域评审核验后，质量审核通过；管理员冻结快照、自动组包、运行 L1–L5 校验、幂等入库。

任务源是 Canonical v1 JSON，但专家只看到表单和摘要，不直接改 JSON。Agent 建议写入 `agent_suggestions`，只有专家确认后才写回 `tasks.draft_payload`。

## 存储

本地用 SQLite，路径由 `ALE_DB_PATH` 控制，默认 `platform/var/platform.db`。文件内容寻址存储在 `ALE_STORAGE_ROOT`，默认 `platform/var/objects`。包输出在 `ALE_PACKAGE_ROOT`，默认 `platform/var/packages`。

PostgreSQL、对象存储和后台队列是目标生产 profile，当前没有实现。HTTP 层与领域服务分离，后续替换适配器即可。

## 安全边界

- 密码使用 PBKDF2-SHA256，会话 cookie 使用 itsdangerous 签名，CSRF 令牌逐表单校验。
- 任务读取校验 owner、`task:read:all` 或实际评审领取记录，不只看角色。
- 上传文件有大小上限，包内路径拒绝绝对路径和 `..`。
- `PACKAGE.json` 在版本层，不在 `base/`，被评 Agent 不可见。
- 这是本地演示配置，cookie 未设 `Secure`。正式外部访问必须启用 HTTPS、`Secure` cookie、生产密钥管理和 PostgreSQL。

## 测试

```bash
PYTHONPATH=platform ../.venv/bin/python -m unittest discover -s platform/tests -v
../.venv/bin/python -m pytest platform/tests -q
```
