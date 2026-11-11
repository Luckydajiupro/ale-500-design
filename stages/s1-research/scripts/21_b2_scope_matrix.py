#!/usr/bin/env python3
"""S1-02B2 scope matrix — inherit the frozen official fields from the S1-02A
scope matrix for exactly the 11 B2 subdomains, add the B2 merged candidate
counts, and enrich notes with S1-01 mapping remarks.

Run AFTER scripts/23_merge_b2.py (needs S1_02B2_WORKFLOW_CANDIDATES.csv).

Writes S1_02B2_SCOPE_MATRIX.csv with A's 15-column schema:
  cohort, cluster_code, cluster_name, subdomain_id, subdomain_code,
  subdomain_name, coverage_status, active_taxonomy_count,
  official_example_task_ids, s1_02b2_batch, candidate_workflow_count,
  ab_A_status, ab_B_status, ab_dispute, notes

The frozen cells (everything except s1_02b2_batch / candidate_workflow_count /
notes) are copied verbatim from S1_02A_SCOPE_MATRIX.csv so the official fields
cannot drift between A and B2. Exit 0 = matrix written; exit 1 = derivation
mismatch (the internal self-test proves a mutation is detectable).
"""
import csv, sys
from collections import Counter

WS = "/Users/mac/Workspaces/ale-研究设计/ale-500-category-research"
IN_A = f"{WS}/S1_02A_SCOPE_MATRIX.csv"
IN_S1 = f"{WS}/S1_01_CATEGORY_MAPPING.csv"
IN_WF = f"{WS}/S1_02B2_WORKFLOW_CANDIDATES.csv"
OUT = f"{WS}/S1_02B2_SCOPE_MATRIX.csv"

B2_IDS = [
    "5.1", "5.2",
    "6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8",
    "13.1",
]
COLS = ["cohort", "cluster_code", "cluster_name", "subdomain_id",
        "subdomain_code", "subdomain_name", "coverage_status",
        "active_taxonomy_count", "official_example_task_ids",
        "s1_02b2_batch", "candidate_workflow_count", "ab_A_status",
        "ab_B_status", "ab_dispute", "notes"]


def build(rows_a, rows_s1, counts):
    """rows_a: A matrix rows (dicts); rows_s1: S1-01 mapping rows; counts:
    subdomain_code -> merged B2 count. Returns the matrix rows."""
    by_s1 = {r["subdomain_id"]: r for r in rows_s1}
    out = []
    for r in rows_a:
        if r["subdomain_id"] not in B2_IDS:
            continue
        code = r["subdomain_code"]
        s1 = by_s1.get(r["subdomain_id"], {})
        note_bits = []
        if s1.get("mapping_dispute", "").strip() not in ("", "None."):
            note_bits.append("s1-01 dispute: " + s1["mapping_dispute"].strip())
        if s1.get("reclassified_in", "").strip():
            note_bits.append("reclassified-in: " + s1["reclassified_in"].strip())
        if s1.get("reclassified_out", "").strip():
            note_bits.append("reclassified-out: " + s1["reclassified_out"].strip())
        out.append({
            "cohort": r["cohort"], "cluster_code": r["cluster_code"],
            "cluster_name": r["cluster_name"], "subdomain_id": r["subdomain_id"],
            "subdomain_code": r["subdomain_code"],
            "subdomain_name": r["subdomain_name"],
            "coverage_status": r["coverage_status"],
            "active_taxonomy_count": r["active_taxonomy_count"],
            "official_example_task_ids": r["official_example_task_ids"],
            "s1_02b2_batch": "batch_2",
            "candidate_workflow_count": str(counts.get(code, 0)),
            "ab_A_status": r["ab_A_status"], "ab_B_status": r["ab_B_status"],
            "ab_dispute": r["ab_dispute"], "notes": "; ".join(note_bits),
        })
    return out


def main():
    with open(IN_A, encoding="utf-8") as f:
        rows_a = list(csv.DictReader(f))
    try:
        with open(IN_WF, encoding="utf-8") as f:
            rows_wf = list(csv.DictReader(f))
    except FileNotFoundError:
        raise SystemExit("MISSING S1_02B2_WORKFLOW_CANDIDATES.csv; "
                         "run scripts/23_merge_b2.py first")
    with open(IN_S1, encoding="utf-8") as f:
        rows_s1 = list(csv.DictReader(f))

    counts = Counter(r["subdomain_code"] for r in rows_wf)
    matrix = build(rows_a, rows_s1, counts)

    a_ids = [r["subdomain_id"] for r in rows_a if r["subdomain_id"] in B2_IDS]
    if sorted(a_ids) != sorted(B2_IDS):
        raise SystemExit(f"A matrix lacks B2 rows: {sorted(set(B2_IDS) - set(a_ids))}")
    if sorted(r["subdomain_id"] for r in matrix) != sorted(B2_IDS):
        raise SystemExit("matrix row count != 11")
    if len(matrix) != 11:
        raise SystemExit(f"matrix rows={len(matrix)} expected 11")

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(matrix)

    # self-tests on mutations of the in-memory inputs (no files touched)
    tampered = dict(counts)
    tampered["economics"] = tampered.get("economics", 0) + 1
    mutated = build(rows_a, rows_s1, tampered)
    n1 = len([r for r in mutated if r["subdomain_id"] == "13.1"
              and r["candidate_workflow_count"] == str(tampered["economics"])])
    n2 = len([r for r in build([x for x in rows_a if x["subdomain_id"] != "6.1"],
                               rows_s1, counts)])
    print(f"negative: dropped subdomain -> rows={n2} (must != 11)")
    print(f"negative: count tamper flagged={bool(n1)}")
    print({r["subdomain_id"]: r["candidate_workflow_count"] for r in matrix})
    print(f"wrote {OUT} with {len(matrix)} rows")
    return 0 if n2 != 11 and n1 else 1


if __name__ == "__main__":
    sys.exit(main())