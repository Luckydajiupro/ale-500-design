# BAC Arbitration Fee Calculation

You are calculating arbitration fees under the Beijing Arbitration Commission /
Beijing International Arbitration Center materials supplied in this task.

## Closed-Book Rule

Use only the staged materials under `/media/user/data/agenthle/legal_compliance/legal_dr_fees_01/base/input`. Do not use outside
web search or external regulatory knowledge.

## Source Materials

The `documents/` directory contains seven BAC PDF documents. They include fee
schedules, implementation rules, refund rules, mediation-arbitration fast
procedure materials, and hourly-rate remuneration guidance. The documents are
in Chinese.

## Cases

The five cases are also listed in `cases.json`:

1. Case 1: amount in dispute is RMB 5,800,000.00.
2. Case 2: amount in dispute is RMB 65,902,536.17.
3. Case 3: amount in dispute is RMB 882,480,634.38.
4. Case 4: amount in dispute is RMB 251,620,139.47. Special condition: the
   parties reached a settlement agreement regarding the dispute before applying
   for arbitration.
5. Case 5: amount in dispute is RMB 3,215.00.

## Deliverable

Write exactly one JSON file:

`/media/user/data/agenthle/legal_compliance/legal_dr_fees_01/base/output/arbitration_fee_results.json`

The required schema is documented in `output_contract.json`. For each case,
report all amounts in RMB to exactly two decimal places:

- `institution_fee_rmb`
- `arbitrator_remuneration_rmb`
- `total_fee_rmb`

You may include explanatory notes, but the numeric fields above are the fields
that will be evaluated.
