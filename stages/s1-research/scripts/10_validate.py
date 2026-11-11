#!/usr/bin/env python3
"""Validate S1-02A deliverables.

Checks (each prints PASS/FAIL):
- C1  55 total official subdomain rows (SCOPE_MATRIX).
- C2  47 formal non-CS subdomain rows + 7 computing_math (A/B) + 1 other.
- C3  14 batch_1 subdomain rows (3 first-batch clusters).
- C4  51 candidate workflow rows (WORKFLOW_CANDIDATES).
- C5  every batch_1 subdomain has >= 1 candidate (no missing boundary).
- C6  zero official_task_example rows (no official task copied).
- C7  source_type only industry_supported / project_proposal.
- C8  evidence_level only E1/E3/E4 this round (E2/U absent).
- C9  5 E4 candidates, all source_type=project_proposal (expert-pending).
- C10 candidate_workflow_count backfill matches actual per-subdomain counts.
- C11 candidate_id unique and follows the agreed prefix convention.
- C12 no empty required field (workflow_title / task_input / professional_operations /
      expected_deliverable / success_criteria / verification_approach).
- C13 23 columns in WORKFLOW_CANDIDATES.
"""
import csv, sys, collections

def rows_csv(path):
    return list(csv.DictReader(open(path, encoding="utf-8"), delimiter=","))

def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}: {name} — {detail}")
    return 0 if ok else 1

fails = 0
PREFIX = {
    "aerospace_mech": "eng_aerospace_wf", "electronics": "eng_electronics_wf",
    "civil_geo": "eng_civilgeo_wf", "chemical_process": "eng_chemproc_wf",
    "manufacturing": "eng_manufacturing_wf", "energy_power": "eng_energypower_wf",
    "mining_petroleum": "eng_mining_wf", "semiconductor": "eng_semiconductor_wf",
    "urban_planning": "eng_urban_wf", "robotics": "eng_robotics_wf",
    "env_water": "ag_envwater_wf", "precision_agriculture": "ag_precision_wf",
    "litigation": "legal_litigation_wf", "legal_research": "legal_research_wf",
}

sm = rows_csv("S1_02A_SCOPE_MATRIX.csv")
wc = rows_csv("S1_02A_WORKFLOW_CANDIDATES.csv")

# C1/C2
n_total = len(sm)
n_formal = sum(1 for r in sm if r["cohort"] == "formal_non_cs")
n_ab = sum(1 for r in sm if r["cohort"] == "computing_math_ab")
n_other = sum(1 for r in sm if r["cohort"] == "other")
fails += check("C1 55 official subdomain rows", n_total == 55, f"total={n_total}")
fails += check("C2 47 formal + 7 computing_math + 1 other", n_formal == 47 and n_ab == 7 and n_other == 1,
               f"formal={n_formal} ab={n_ab} other={n_other}")

# C3
batch1 = [r for r in sm if r["s1_02a_batch"] == "batch_1"]
fails += check("C3 14 batch_1 subdomain rows", len(batch1) == 14, f"batch_1={len(batch1)}")

# C4/C13
fails += check("C4 51 candidate workflow rows", len(wc) == 51, f"rows={len(wc)}")
fails += check("C13 23 columns", len(wc[0]) == 23 if wc else False, f"cols={len(wc[0]) if wc else 0}")

# C5/C10: per-subdomain coverage and backfill
cnt = collections.Counter(r["subdomain_code"] for r in wc)
batch1_codes = [r["subdomain_code"] for r in batch1]
missing = [c for c in batch1_codes if cnt.get(c, 0) < 1]
fails += check("C5 every batch_1 subdomain covered", not missing, f"missing={missing or 'none'}")
backfill_ok = all(r["candidate_workflow_count"] == str(cnt.get(r["subdomain_code"], 0)) for r in batch1)
fails += check("C10 candidate_workflow_count matches", backfill_ok, "backfill consistent" if backfill_ok else "MISMATCH")

# C6/C7: source_type discipline
st = collections.Counter(r["source_type"] for r in wc)
fails += check("C6 zero official_task_example", st.get("official_task_example", 0) == 0,
               f"official={st.get('official_task_example', 0)}")
bad_st = [k for k in st if k not in ("industry_supported", "project_proposal")]
fails += check("C7 source_type only industry_supported/project_proposal", not bad_st,
               f"bad={bad_st or 'none'}")

# C8: evidence discipline
ev = collections.Counter(r["evidence_level"] for r in wc)
bad_ev = [k for k in ev if k not in ("E1", "E3", "E4")]
fails += check("C8 evidence only E1/E3/E4", not bad_ev, f"bad={bad_ev or 'none'} count={dict(ev)}")

# C9: E4 candidates must be project_proposal
e4 = [r for r in wc if r["evidence_level"] == "E4"]
e4_ok = len(e4) == 5 and all(r["source_type"] == "project_proposal" for r in e4)
fails += check("C9 5 E4 candidates all project_proposal", e4_ok,
               f"n_e4={len(e4)} all_proposal={all(r['source_type']=='project_proposal' for r in e4)}")
if e4:
    print("      E4 candidates:", ", ".join(r["candidate_id"] for r in e4))

# C11: id uniqueness + prefix
ids = [r["candidate_id"] for r in wc]
dup = [k for k, v in collections.Counter(ids).items() if v > 1]
prefix_bad = []
for r in wc:
    code = r["subdomain_code"]
    if code in PREFIX and not r["candidate_id"].startswith(PREFIX[code]):
        prefix_bad.append(r["candidate_id"])
fails += check("C11 candidate_id unique + prefix", not dup and not prefix_bad,
               f"dup={dup or 'none'} prefix_bad={prefix_bad or 'none'}")

# C12: required fields non-empty
REQ = ["workflow_title", "task_input", "professional_operations",
       "expected_deliverable", "success_criteria", "verification_approach"]
empty = [(r["candidate_id"], f) for r in wc for f in REQ if not r.get(f, "").strip()]
fails += check("C12 required fields non-empty", not empty,
               f"empty={[(i, f) for i, f in empty] or 'none'}")

print()
print(f"RESULT: {'ALL PASS' if fails == 0 else str(fails) + ' FAILURES'}")
sys.exit(1 if fails else 0)
