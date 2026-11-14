# Contracts: the seam between wave-1 product design and this skeleton

本目录存放两份尚未冻结的对外合同占位：专家标注 Canonical Task Source 与
ALE-data 包合同。工作线 A/B 冻结正式版本之前，业务代码只通过这里的常量、
数据类和纯函数读取字段名与校验码，不把字段名散落到路由或仓储里。

替换方式：保持模块名与函数签名不变，替换常量与实现即可。已经写进数据库的
历史版本不会被回写，因为 task_versions 保存原始 payload。

`canonical_schema.py` 的字段清单目前取自第一波产出的
`docs/data/wave1-canonical-task-source.csv`，标记为 draft；其中只有五组核心字段
被视为可冻结候选，其余按版本化处理。`package_contract.py` 的哈希定义是候选，
PoC P12 通过前不得对外宣称是最终包哈希。
