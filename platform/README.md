# 平台骨架

本目录是 ALE 500 平台的第二波可运行骨架。它用 Python 标准库和 SQLite 跑通任务、资料、审核、组包与入库的接缝，不绑定 HTTP 框架。

## 运行测试

```bash
PYTHONPATH=platform python3 -m unittest discover -s platform/tests -v
```

14 项测试覆盖建表、状态机、Canonical 结构校验、对象存储和候选包哈希。

## 目录

`app/domain/` 放业务规则，`app/repo/` 放 SQL，`app/adapters.py` 放时间、ID、哈希和本地对象存储，`contracts/` 放 Canonical、包和验证合同常量，`app/schema.sql` 是 SQLite 版 DDL。

## 边界

HTTP 路由、PostgreSQL 迁移、S3 适配器、登录页和前端页面尚未实现。包哈希与 `PACKAGE.json` 布局是候选，P12 通过前不对外称最终合同。
