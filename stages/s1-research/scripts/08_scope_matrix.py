#!/usr/bin/env python3
"""S1-02A: generate the coverage-skeleton SCOPE_MATRIX from the S1-01 taxonomy mapping.

Read-only over S1-01 deliverables. Writes S1_02A_SCOPE_MATRIX.csv (skeleton; candidate
counts are backfilled by scripts/09_workflow_candidates.py after the first-batch research).
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

MAPPING = os.path.join(ROOT, "S1_01_CATEGORY_MAPPING.csv")
ARCHETYPE = os.path.join(ROOT, "S1_01_TASK_ARCHETYPE_EVIDENCE.csv")
OUT = os.path.join(ROOT, "S1_02A_SCOPE_MATRIX.csv")

BATCH1 = {"engineering", "agriculture_env", "legal"}

# example_task_ids by subdomain_code, from the S1-01 archetype evidence.
example_ids = {}
with open(ARCHETYPE, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        example_ids[row["subdomain_code"]] = row.get("example_task_ids", "")

def cohort_of(domain_code):
    if domain_code == "computing_math":
        return "computing_math_ab"
    if domain_code == "other":
        return "other"
    return "formal_non_cs"

cols = [
    "cohort", "cluster_code", "cluster_name", "subdomain_id", "subdomain_code",
    "subdomain_name", "coverage_status", "active_taxonomy_count",
    "official_example_task_ids", "s1_02a_batch", "candidate_workflow_count",
    "ab_A_status", "ab_B_status", "ab_dispute", "notes",
]

rows = []
with open(MAPPING, newline="", encoding="utf-8") as f:
    for m in csv.DictReader(f):
        dc = m["domain_code"].strip()
        batch = "batch_1" if dc in BATCH1 else "pending"
        rows.append({
            "cohort": cohort_of(dc),
            "cluster_code": dc,
            "cluster_name": m["official_domain_name"].strip(),
            "subdomain_id": m["subdomain_id"].strip(),
            "subdomain_code": m["subdomain_code"].strip(),
            "subdomain_name": m["subdomain_name"].strip(),
            "coverage_status": m["coverage_status"].strip(),
            "active_taxonomy_count": m["active_taxonomy_count"].strip(),
            "official_example_task_ids": example_ids.get(m["subdomain_code"].strip(), ""),
            "s1_02a_batch": batch,
            "candidate_workflow_count": "",  # backfilled later
            "ab_A_status": m["ab_A_status"].strip(),
            "ab_B_status": m["ab_B_status"].strip(),
            "ab_dispute": m["ab_dispute"].strip(),
            "notes": "",
        })

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

n_formal = sum(1 for r in rows if r["cohort"] == "formal_non_cs")
n_ab = sum(1 for r in rows if r["cohort"] == "computing_math_ab")
n_other = sum(1 for r in rows if r["cohort"] == "other")
n_batch1 = sum(1 for r in rows if r["s1_02a_batch"] == "batch_1")
print(f"rows={len(rows)} formal_non_cs={n_formal} computing_math_ab={n_ab} other={n_other} batch_1={n_batch1}")
