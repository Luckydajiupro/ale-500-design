#!/usr/bin/env python3
"""S1-02A: assemble S1_02A_WORKFLOW_CANDIDATES.csv from the first-batch research JSON.

Reads one JSON file per research subagent from evidence/s1_02a_research/*.json. Each file is
the subagent's returned object: {"subdomains": [...], "candidates": [...]}.

Flattens candidates into a 23-column CSV, validates evidence discipline, dedupes candidate_ids,
and backfills `candidate_workflow_count` into S1_02A_SCOPE_MATRIX.csv.

A candidate whose source_type is "official_task_example" is reference-only: it is NOT counted
as a new candidate and is excluded from the CSV (the research must not copy official tasks).
"""
import csv
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESEARCH_DIR = os.path.join(ROOT, "evidence", "s1_02a_research")
SCOPE = os.path.join(ROOT, "S1_02A_SCOPE_MATRIX.csv")
OUT = os.path.join(ROOT, "S1_02A_WORKFLOW_CANDIDATES.csv")

BATCH1_SUBDOMAINS = {
    "aerospace_mech", "electronics", "civil_geo", "chemical_process", "manufacturing",
    "energy_power", "mining_petroleum", "semiconductor", "urban_planning", "robotics",
    "env_water", "precision_agriculture", "litigation", "legal_research",
}
EVIDENCE_LEVELS = {"E1", "E2", "E3", "E4", "U"}
SOURCE_TYPES = {"official_task_example", "industry_supported", "project_proposal", "expert_pending"}

CANDIDATE_FIELDS = [
    "subdomain_code", "candidate_id", "workflow_title", "occupation_scope",
    "workflow_summary", "source_type", "evidence_level", "source_reference",
    "expert_raw_materials", "usage_permissions", "task_input", "professional_operations",
    "expected_deliverable", "success_criteria", "verification_approach",
    "platform_dependencies", "blocking_risks", "expert_capability",
    "cross_domain_overlap", "granularity_check", "pending_confirmation",
]
COLS = ["subdomain_code", "subdomain_business_boundary", "subdomain_occupations"] + \
    CANDIDATE_FIELDS[1:]  # subdomain_code already leading

errors = []
warnings = []
subdomain_boundary = {}   # subdomain_code -> {"business_boundary", "occupations"}
candidates = []           # list of candidate dicts (21 fields, flattened)
seen_ids = set()

files = sorted(glob.glob(os.path.join(RESEARCH_DIR, "*.json")))
if not files:
    print(f"no research JSON found in {RESEARCH_DIR}")
    sys.exit(2)

for path in files:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for sd in data.get("subdomains", []):
        code = sd.get("subdomain_code", "")
        subdomain_boundary[code] = {
            "business_boundary": sd.get("business_boundary", ""),
            "occupations": sd.get("occupations", ""),
        }
    for c in data.get("candidates", []):
        code = c.get("subdomain_code", "")
        cid = c.get("candidate_id", "")
        stype = c.get("source_type", "")
        if code not in BATCH1_SUBDOMAINS:
            errors.append(f"{os.path.basename(path)}: unknown subdomain_code {code!r}")
        if cid in seen_ids:
            errors.append(f"{os.path.basename(path)}: duplicate candidate_id {cid!r}")
        seen_ids.add(cid)
        if stype not in SOURCE_TYPES:
            errors.append(f"{cid}: bad source_type {stype!r}")
        if c.get("evidence_level", "") not in EVIDENCE_LEVELS:
            errors.append(f"{cid}: bad evidence_level {c.get('evidence_level')!r}")
        for field in ("workflow_title", "workflow_summary", "cross_domain_overlap", "granularity_check"):
            if not c.get(field, "").strip():
                errors.append(f"{cid}: empty required field {field}")
        if stype == "official_task_example":
            warnings.append(f"{cid}: official_task_example — reference-only, dropped from new candidates")
            continue
        flat = {f: c.get(f, "") for f in CANDIDATE_FIELDS}
        candidates.append(flat)

# every batch-1 subdomain must be covered by at least a boundary entry (even if no candidates yet)
missing_sd = BATCH1_SUBDOMAINS - set(subdomain_boundary)
if missing_sd:
    warnings.append(f"no subdomain boundary entry for: {sorted(missing_sd)}")

# write candidates CSV
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for c in sorted(candidates, key=lambda r: (r["subdomain_code"], r["candidate_id"])):
        code = c["subdomain_code"]
        row = {
            "subdomain_code": code,
            "subdomain_business_boundary": subdomain_boundary.get(code, {}).get("business_boundary", ""),
            "subdomain_occupations": subdomain_boundary.get(code, {}).get("occupations", ""),
        }
        row.update({k: c[k] for k in CANDIDATE_FIELDS[1:]})
        w.writerow(row)

# backfill candidate_workflow_count into scope matrix
counts = {}
for c in candidates:
    counts[c["subdomain_code"]] = counts.get(c["subdomain_code"], 0) + 1

scope_rows = []
with open(SCOPE, newline="", encoding="utf-8") as f:
    scope_rows = list(csv.DictReader(f))
for r in scope_rows:
    r["candidate_workflow_count"] = str(counts.get(r["subdomain_code"], 0))
with open(SCOPE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=scope_rows[0].keys())
    w.writeheader()
    w.writerows(scope_rows)

from collections import Counter
stype_dist = Counter(c["source_type"] for c in candidates)
ev_dist = Counter(c["evidence_level"] for c in candidates)

print(f"json_files={len(files)} candidates={len(candidates)} subdomains_boundary={len(subdomain_boundary)}")
print(f"source_type={dict(stype_dist)}")
print(f"evidence_level={dict(ev_dist)}")
print(f"missing_boundary={sorted(missing_sd)}")
for m in warnings:
    print("WARN:", m)
for e in errors:
    print("ERROR:", e)
if errors:
    sys.exit(1)
