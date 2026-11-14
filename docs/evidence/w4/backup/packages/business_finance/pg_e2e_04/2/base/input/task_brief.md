# End-to-end bank reconciliation

## Context

月度结账期间核对银行流水与总账。

## Workflow

1. 读取流水与总账
   Expected state: 步骤完成
2. 核对差异并按原因归类
   Expected state: 步骤完成
3. 生成对账结果并说明差异
   Expected state: 差异原因已写入结果

## Deliverables

- `output/reconciliation.json` (xlsx)
