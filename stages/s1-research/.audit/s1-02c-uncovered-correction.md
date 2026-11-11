# S1-02C-U1 uncovered_official 传播修正与构建链回退修复说明

版本：S1-02C-U1（第三次修订，S1-02C-U3）
记录时间：2026-11-11
状态：修正已完成并落盘，等待独立评审。

## 1. 修正前状态（以磁盘为准）

- 独立复审确认磁盘快照 uncovered_official_flag=yes 为 22 条，但构建器
  scripts/34_build_s1_02c.py 仍只对 batch == B3 推导该标记。
- 在临时副本重跑修复前的 34 可稳定复现回归：uncovered_official 从 22 回退为 9。
- 根因有两个。其一是 34 第 261 行左右的 batch == B3 限制。其二是
  s1_02c_spec.py 的 UNCOVERED_SUBDOMAINS 只有 aviation、maritime_port、
  educational_technology 三个 B3 子领域，basis 文案还引用 S1_02B3_SCOPE_MATRIX.csv。

## 2. 修正内容

- 34 构建器：
  - 构建开始前把 S1_01_CATEGORY_MAPPING.csv 整体读入 MAPPING_COVERAGE，
    对 subdomain_code 缺失或重复的行直接报错退出，绝不默认为 no。
  - uncovered_official_flag 按候选的 subdomain_code 对应的 coverage_status 推导，
    不再限制 batch == B3。
  - uncovered_official_basis 引用 S1-01 对应记录（subdomain_code、coverage_status、
    official_domain、subdomain_name）。
  - registry、expert matrix 与 stats 继续由 assignment 重新聚合，数字口径不变。
  - A 批新增 13 条未自动标记为 padding_risk；padding 仍只属于 B3 的 27 条。
- s1_02c_spec.py：删除只覆盖 B3 三域的 UNCOVERED_SUBDOMAINS 硬编码表，
  留注释指向本说明。
- 统计键：b2_registered_original_family 删除，替换为
  registered_original_family_rows=32 与
  registered_original_family_by_batch={"B2":5,"B3":27}。
  构建器、stats、S1_02C_REVIEW_SUMMARY.md 口径一致。
- 36 校验器 C16 加强：
  - 先严格检查 uncovered_official_flag 只能是 yes 或 no；
  - 再逐条比较 assignment 与 S1_01_CATEGORY_MAPPING.csv 的 coverage_status；
  - 新增两个负例：非 uncovered 行的 no 改成 maybe、uncovered 行的 yes 改成
    yesterday，均需由 C16 或明确的枚举检查捕获。

## 3. 保持不变

- assignment：174 条
- uncovered_official=yes：22 条，六个子领域分别为
  chemical_process 3、mining_petroleum 5、precision_agriculture 5、
  aviation 3、maritime_port 3、educational_technology 3
- workflow family：72
- expert capability groups：50
- authorization risk groups：9
- engineering risk groups：7
- padding_risk：27 条（全在 B3，high 9）
- Linux NOT_VERIFIED：174 条
- expert_pending：9 条（A）
- 历史候选文件 A/B1/B2/B3 字节不变，C13 基线 61/61 hash-match

## 4. 校验器

- scripts/35_validate_s1_02c.py 15 项检查全绿，
  self-test 10 个负例全部捕获。
- scripts/36_validate_s1_02c_c16.py 16 项检查全绿，
  self-test 13 个负例全部捕获。
- 两套校验各自保留独立的 C 编号，不混用。

## 5. 临时副本重建协议（不在真实目录直接跑 34）

临时副本路径见 .audit/u2-temp-copy.txt。

- 保存修复前 174 条 candidate_id、source_batch、source_file、subdomain_code，
  重建后逐条一致。
- 重建输出与修复前复现的 9 条对照，确认不再回退。
- 连续两次（后续第三次）运行 34，六个产出文件与 stats 哈希完全一致，
  构建可重复。
- 35、36 及其 self-test 全部通过。
- 历史 A/B1/B2/B3 文件与 C13 基线 61 条未变。
- 两份证据日志在临时副本内：evidence-u2.log 与 evidence-u2-validators.log。

## 6. .audit/u2-pre/ 快照口径更正（S1-02C-U3）

独立复审指出 .audit/u2-pre/ 里三个脚本副本不是 U2 修改前的回滚点。本机逐文件核对的结论如下。

脚本快照无效：

- 34_build_s1_02c.py sha256 74336dbd…deb，与当前 scripts/ 下的同名文件完全一致。
- s1_02c_spec.py sha256 2a598d5b…60a7，与当前 scripts/ 下的同名文件完全一致。
- 36_validate_s1_02c_c16.py sha256 ad7d5a3c…ba0c，与当前 scripts/ 下的同名文件完全一致。
- 三个脚本副本均是在 34/36/spec 修改完之后才拷入的，不能作为 U2 之前脚本的回滚快照。此前任何把 u2-pre 描述为可回滚脚本的说法作废。

数据快照有效但范围有限：

- .audit/u2-pre/ 内五张 CSV 与 s1-02c-stats.json 是修订前的数据快照，可分别核对。assignment、registry、matrix、stats 与当前版本哈希不同，authorization、engineering 两张与当前一致。
- 脚本快照与数据快照的可恢复性不能混成一个结论。

上一份压缩包：

- 本机未找到 20261110-171109 压缩包。已查工作区、Downloads、Desktop、Documents、/tmp、/var/tmp、/Users/mac/Archives，不下载、不猜测、不覆盖当前脚本。
- /Users/mac/Archives/ALE-Phase0-History-20261110 是本机唯一相近归档，其 ARCHIVE_SHA256SUMS.txt 只包 Phase 0 三个历史轮次目录，不含 34_build_s1_02c.py、s1_02c_spec.py、36_validate_s1_02c_c16.py，不能用于脚本回滚核对。

## 7. 行级差异说明（重建前后）

- 13 条 A 批 uncovered 行的 notes 增加一句
  "uncovered_official：该子领域在 S1-01 无活跃官方任务。"。
  这是本来就存在的一行代码首次覆盖到 A 批，属于证据补充，不动姓名与风险归属。
- assignment、registry、matrix 三个 CSV 的行结束符由此前的 LF 变为构建器统一的
  CRLF（授权与工程寄存器本来就是 CRLF，不变）。单元格内容逐列一致。
- 任务族、能力组、授权组、工程组的分配与证据类分配均无变化。