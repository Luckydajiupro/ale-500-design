# 容量模型

本文件记录 `storage-sizing.csv` 的公式、参数与敏感性。所有数字由同一脚本算出，可复算。

## 参数

| 参数 | 低 | 中 | 高 | 说明 |
| --- | --- | --- | --- | --- |
| 任务数 | 500 | 500 | 500 | 固定 |
| 类目配额 | 03 文件建议值 | 同左 | 同左 | 含 agriculture_env 12 |
| 基础中位 | 0.6 × 官方中位 | 同左 | 同左 | 新任务比官方样本精简 |
| 情景系数 | 0.6 | 1.0 | 1.6 | 资产偏瘦、正常、偏胖 |
| 层乘数 | 2.5 | 3.5 | 4.5 | 原件、工作副本、评审、快照、历史 |
| 备份系数 | 1.2 | 1.2 | 1.2 | 日备 30 天、月备 12 个月去重 |
| DB | 3 GiB | 6 GiB | 6 GiB | 估算 |
| 日志 | 12 GiB | 30 GiB | 30 GiB | 估算 |

## 公式

```
base_d = clamp(0.6 × official_median_d, 5, 2048)   MiB
footprint_d = base_d × scenario_factor              MiB
live = Σ(quota_d × footprint_d × layer) / 1024      GiB
backup = live × 1.2
provisioned_hot = ceil_to_512(live × 1.3 + 100)
```

`official_median_d` 取 `stages/s0-baseline/08_coverage_matrix_draft.csv` 的中位。`agriculture_env` 没有官方样本，按 2048 MiB 上限估，这是最保守的假设。

## 逐类目结果（中档，层乘数 3.5）

| domain_code | 配额 | 官方中位 MiB | 采用中位 MiB | live GiB |
| --- | --- | --- | --- | --- |
| business_finance | 47 | 0.6 | 5.0 | 0.80 |
| education_info | 36 | 0.3 | 5.0 | 0.62 |
| engineering | 48 | 12.1 | 7.26 | 1.19 |
| health_medicine | 57 | 9.0 | 5.4 | 1.05 |
| legal | 36 | 0.6 | 5.0 | 0.62 |
| life_sciences | 46 | 178.5 | 107.1 | 16.84 |
| other | 32 | 97.3 | 58.38 | 6.39 |
| physical_sciences | 44 | 10.2 | 6.12 | 0.92 |
| psychology_neuro | 34 | 1542 | 925.2 | 107.52 |
| social_sciences | 34 | 447.6 | 268.56 | 31.21 |
| transport_safety | 34 | 85.1 | 51.06 | 5.93 |
| visual_media | 40 | 7.4 | 5.0 | 0.68 |
| agriculture_env | 12 | 无样本 | 2048 | 84.00 |
| 合计 | 500 |  |  | 257.77 |

## 三档结果

| 档 | live GiB | 备份 GiB | DB | 日志 | 已开通热存储 |
| --- | --- | --- | --- | --- | --- |
| 低 | 110.47 | 132.57 | 3 | 12 | 512 GiB |
| 中 | 257.77 | 309.32 | 6 | 30 | 512 GiB |
| 高 | 530.27 | 636.32 | 6 | 30 | 1024 GiB |

中档热占用约 294 GiB，512 GiB 留 74% 余量。高档热占用约 566 GiB，1 TiB 留 80% 余量。

## 敏感性

| 变化 | 影响 | 结果 |
| --- | --- | --- |
| 基础中位翻倍 | live ×2 | 221 / 516 / 1061 GiB |
| 任务 800 | live ×1.6 | 177 / 412 / 848 GiB |
| 单条 12 GiB | 该条占 42 GiB | 中档 +16% |
| 快照保留 3 份 | live +50% | 不建议 |
| agriculture 中位降到 50 MiB | 该项从 84 降到 2 GiB | 中档 -32% |

## 结论

- 512 GiB 热存储覆盖低档与中档，高档升 1 TiB。
- 存储不是瓶颈。psychology_neuro 与 agriculture 两项假设主导总量。
- 单任务上限比总量更值得管。12 GiB 的例外要负责人批。
