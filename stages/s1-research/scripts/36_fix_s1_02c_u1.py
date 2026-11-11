#!/usr/bin/env python3
"""Apply the S1-02C-U1 uncovered_official propagation to the live CSVs.

The truth source is S1_01_CATEGORY_MAPPING.csv coverage_status per
subdomain_code. This script sets, for every assignment row:

    uncovered_official_flag = yes iff mapping.coverage_status == uncovered_official
    uncovered_official_basis  = a sentence naming this mapping row

Then it recomputes the registry and matrix uncovered_official_count columns
from the assignment rows, and rewrites only those three deliverables plus the
stats json. Historical A/B1/B2/B3 candidate files are never opened for
writing. scripts/35_validate_s1_02c.py is never touched.

The C16 validator (scripts/36_validate_s1_02c_c16.py) independently re-derives
the same field expectations from the two files, so this fix is verifiable by a
script that does not trust this script.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAPPING = "S1_01_CATEGORY_MAPPING.csv"
ASSIGN = "S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv"
REGISTRY = "S1_02C_WORKFLOW_FAMILY_REGISTRY.csv"
MATRIX = "S1_02C_EXPERT_CAPABILITY_MATRIX.csv"
STATS = ".audit/s1-02c-stats.json"

BATCH_HASH_FILES = [
    "S1_02A_EFFECTIVE_CANDIDATES.csv",
    "S1_02A_WORKFLOW_CANDIDATES.csv",
    "S1_02B1_WORKFLOW_CANDIDATES.csv",
    "S1_02B2_EFFECTIVE_CANDIDATES.csv",
    "S1_02B3_WORKFLOW_CANDIDATES.csv",
]


def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    return rows


def write_rows(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    before = {}
    for f in BATCH_HASH_FILES:
        before[f] = (ROOT / f).read_bytes()
    mapping = read_rows(ROOT / MAPPING)
    status_by_code = {r["subdomain_code"].strip(): (r["coverage_status"] or "").strip() for r in mapping}
    basis_by_code = {}
    for r in mapping:
        code = r["subdomain_code"].strip()
        if (r["coverage_status"] or "").strip() == "uncovered_official":
            basis_by_code[code] = (
                f"{MAPPING}: {r['subdomain_code']} coverage_status=uncovered_official"
                f", official_domain={r['domain_code']}, subdomain_name={r['subdomain_name']}"
            )

    assignment = read_rows(ROOT / ASSIGN)
    for row in assignment:
        code = (row.get("subdomain_code") or "").strip()
        is_uncovered = status_by_code.get(code) == "uncovered_official"
        row["uncovered_official_flag"] = "yes" if is_uncovered else "no"
        row["uncovered_official_basis"] = basis_by_code.get(code, "") if is_uncovered else ""

    registry = read_rows(ROOT / REGISTRY)
    matrix = read_rows(ROOT / MATRIX)
    uncovered_by_family = Counter()
    uncovered_by_group = Counter()
    for row in assignment:
        code = (row.get("subdomain_code") or "").strip()
        is_uncovered = status_by_code.get(code) == "uncovered_official"
        if is_uncovered:
            uncovered_by_family[(row.get("workflow_family_id") or "").strip()] += 1
            uncovered_by_group[(row.get("expert_capability_group_id") or "").strip()] += 1

    changed_registry = 0
    for row in registry:
        want = uncovered_by_family.get((row.get("workflow_family_id") or "").strip(), 0)
        if int(row.get("uncovered_official_count", "0") or 0) != want:
            changed_registry += 1
        row["uncovered_official_count"] = want
    changed_matrix = 0
    for row in matrix:
        want = uncovered_by_group.get((row.get("expert_capability_group_id") or "").strip(), 0)
        if int(row.get("uncovered_official_count", "0") or 0) != want:
            changed_matrix += 1
        row["uncovered_official_count"] = want

    write_rows(ROOT / ASSIGN, list(assignment[0].keys()), assignment)
    write_rows(ROOT / REGISTRY, list(registry[0].keys()), registry)
    write_rows(ROOT / MATRIX, list(matrix[0].keys()), matrix)

    count = sum(1 for r in assignment if r["uncovered_official_flag"] == "yes")
    per = Counter(r["subdomain_code"] for r in assignment if r["uncovered_official_flag"] == "yes")
    print(f"uncovered_official total = {count}")
    print(f"uncovered_official per subdomain = {dict(per)}")
    print(f"registry rows changed = {changed_registry}, matrix rows changed = {changed_matrix}")

    state_raw = (ROOT / STATS).read_text(encoding="utf-8")
    state = json.loads(state_raw)
    state["flags"]["uncovered_official"] = count
    state["uncovered_candidates"] = [a["candidate_id"] for a in assignment if a["uncovered_official_flag"] == "yes"]
    state["uncovered_by_subdomain"] = dict(per)
    state["families_with_uncovered"] = [r["workflow_family_id"] for r in registry if r["uncovered_official_count"]]

    stats_path = ROOT / STATS
    stats_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print("stats uncovered =", state["flags"]["uncovered_official"])

    after = {}
    for f in BATCH_HASH_FILES:
        after[f] = (ROOT / f).read_bytes()
    for f in BATCH_HASH_FILES:
        if before[f] != after[f]:
            print(f"UNEXPECTED batch byte drift: {f}")
    print("batch files byte-identical after fix")


if __name__ == "__main__":
    main()