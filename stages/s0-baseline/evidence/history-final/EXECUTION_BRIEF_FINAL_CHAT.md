/poteto-mode
现在执行 ALE Phase 0 最终基线整合。

目标：
将 Phase 0 第一轮、R1、R2 的有效成果整合成
一套自包含、无冗余、可直接供后续设计使用的
正式基线文件。

本任务不是 R3，不重新开展官方数据盘点，
不运行官方任务，不开发平台或转换器。

来源：
analysis/phase0-official-baseline/
analysis/phase0-official-baseline-r1/
analysis/phase0-official-baseline-r2/

唯一新建输出：
analysis/phase0-final/

要求：

1. 首先只读盘点三轮文件及来源关系。
   以实际清单与磁盘哈希决定文件继承版本，
   不简单按文件名或修改时间选择。

2. 建立 PHASE0_FINAL_REPORT.md，
   综合所有有效研究结论，内容包括：
   - 项目目标与阶段边界
   - 四份官方输入及版本
   - 发布任务集合与类别分布
   - 新旧任务格式与工程交接语义
   - Linux/Windows/GUI/GPU/外部服务约束
   - Provider 能力声明与实际验证边界
   - 500 条专家新任务的生产原则
   - P0 决策、UNKNOWN、风险与后续事项
   - 研究结论的证据来源

3. 保留三份最终有效数据表：
   04_task_inventory.csv
   05_task_category_summary.csv
   08_coverage_matrix_draft.csv

4. 汇总必要证据，保留完整引用关系。
   原有证据如果仍然被正式结论依赖，
   必须能够从最终目录或者冻结输入中找到。
   不允许生成悬空引用。

5. 原来的 01_baseline_manifest.json
   保留来源身份，不冒充最终产物清单。
   新建 SOURCE_MANIFEST_FINAL.json，
   登记最终文件来源、哈希和依赖关系。

6. 修正正式报告中的过时表述，
   特别是 R2 汇总末尾沿用 R1 状态的问题。
   不修改原 R2 封存文件。

7. 不把 UNKNOWN 改成 PASS。
   不将 R2 执行方校验视为最终整合版的校验。
   不擅自裁决正式配额、Windows、GPU预算。

8. 为最终版建立独立检查：
   - 任务数、类别数、各表统计一致
   - 技术术语与结论跨文件一致
   - 引用与证据路径全部有效
   - 每份正式文件有完整 SHA256
   - 最终目录不依赖 R0/R1/R2 的活目录
   - 来源追溯不丢失
   - 当前项目状态表达准确

9. 验证通过后冻结 phase0-final，
   生成 FINAL_VALIDATION_REPORT.md
   与 FINAL_CHECKSUMS.sha256。

10. 本轮禁止删除、移动、覆盖原三轮目录。
    也不修改官方仓库、inputs-readonly、.audit。

11. 最后直接在聊天中回报：
    - 最终目录文件树
    - 旧文件至最终文件的映射表
    - 文件数量和空间对比
    - 合并后保留的全部重要结论
    - 验证结果及剩余问题
    - 哪些旧目录可以安全归档或移除

完成后停止，等待我批准清理历史目录。