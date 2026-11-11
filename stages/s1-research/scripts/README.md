# 脚本说明

这份文件回答一件事：这 40 个脚本里哪些还能跑、哪些只是留档、跑哪个能证明数据没被改。

## 能跑的只有两个

`35_validate_s1_02c.py` 和 `36_validate_s1_02c_c16.py`。

它们从自身位置推出包根目录，不写死绝对路径，整目录搬走后仍然可用。前者做 15 项结构与一致性检查，后者做 16 项行列对照检查。两者都支持 `--self-test`，注入错误验证检查本身有效。

```bash
cd stages/s1-research
python3 -B scripts/35_validate_s1_02c.py
python3 -B scripts/36_validate_s1_02c_c16.py
```

校验器会读取同目录的 `.audit/s1-02c-baseline.sha256`、`.audit/s1-02c-stats.json`、`.audit/s1-02b3.tsv`。这三个文件不能删，删了校验器直接报缺失。

## 被校验器引用的两个模块

`35_validate_s1_02c.py` 会导入 `s1_02c_spec.py` 和 `s1_02c_taxonomy.py`。这两个是常量与分类定义，不要单独运行。

## 只是留档的 15 个

下面这些脚本里写死了项目旧位置的绝对路径，包括已经删除的官方原始目录。它们记录了数据是怎么一步步生成的，可以读，不能直接重跑。

`01_taxonomy_extract.py`、`02_archetype_extract.py`、`03_archetype_report.py`、`04_category_mapping.py`、`05_archetype_csv.py`、`06_reclassification_evidence.py`、`15_b1_baseline_check.py`、`16_merge_b1.py`、`17_validate_b1.py`、`19_annotate_duplicates.py`、`20_b2_precheck.py`、`21_b2_scope_matrix.py`、`23_merge_b2.py`、`24_validate_b2.py`、`25_b2_overlap.py`。

要重跑它们，需要先把路径改成相对根，并恢复官方原始目录。改路径属于重写历史脚本，会破坏这一段的可追溯性，所以本方案不动它们。

## 其余文件

`b2_effective_corrections_spec.json` 是 B2 批生效视图的修正规格，被构建脚本读取。

编号 07 到 14、18、22、26 到 34 的脚本是同批次的校验与构建辅助，同样属于留档。

## 判断一个新脚本该不该放这里

能从包根目录推导路径、能在这里直接跑、失败会以非零退出码结束的，放这里并写进本文件。

依赖外部目录、需要联网、需要旧路径的，放 `tools/` 或留在 `docs/` 描述里，不要混进来。
