# ale-data / Harbor 契约测试

这组文件是 `02-platform-design.md` 第 14 节的可执行版本。平台还没开发，先用它冻结格式契约：任何一方改包结构、校验规则或字段映射，都必须让这里的测试继续通过。

## 跑法

```bash
cd work/platform-p1
python3 tests/test_roundtrip.py
```

只用 Python 标准库，3.9 及以上可跑，不装依赖。

## 文件

| 文件 | 作用 |
| --- | --- |
| `ale_data_format.py` | 校验 ale-data 包、转 Harbor、回转 ale-data、算 canonical hash |
| `test_roundtrip.py` | 13 个用例：合法包、缺件、篡改、版本、许可、映射、往返 |
| `fixtures/legal_dr_fees_01/base/` | 取自 `inputs/frozen/03_ale-data/task-data-v1.1/legal/legal_dr_fees_01/base` |

fixture 里 `task_brief.md`、`output_contract.json`、`cases.json`、`runtime_env/pyproject.toml`、`reference/answer_key.json` 是真实文件。七个 PDF 是字节相同的占位文件，文件名保留中文原名，`document_manifest.json` 按占位文件重算了 sha256；这样做是为了让测试覆盖中文文件名与哈希校验，同时不把 1 MB 的许可资料复制进仓库。

## 它不证明什么

- 不证明镜像能构建，不证明任务可运行。运行在工程侧，见 `05-pilot-and-rollout.md` 第 4 节。
- 不证明答案正确。`answer_key.json` 来自官方包，只作 fixture。
- 不替代平台测试。平台实现后，同一组用例必须原样通过，再加数据库与权限测试。
