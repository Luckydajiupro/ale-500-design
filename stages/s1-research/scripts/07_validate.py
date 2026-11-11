#!/usr/bin/env python3
"""Validate S1-01 deliverables after revision.

Checks (each prints PASS/FAIL/UNKNOWN):
- C1  49 active-observed subdomain rows (CATEGORY_MAPPING coverage_status).
- C2  55 total official subdomain rows (complete official classification).
- C3  6 uncovered_official rows.
- C4  122 unique active tasks (sum of active_taxonomy_count).
- C5  13 cross-domain reclassification rows.
- C6  135 task-card rows in the archetype evidence.
- C7  eval_hardGates content removed (presence/type columns only, no rule text).
- C8  TASK_ARCHETYPE_EVIDENCE has 49 rows and 122 example tasks.
"""
import csv, sys, collections

def rows(path):
    return list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t" if path.endswith(".tsv") else ","))

def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}: {name} — {detail}")
    return ok

fails = 0

# C1/C2/C3/C4
cm = list(csv.DictReader(open("S1_01_CATEGORY_MAPPING.csv", encoding="utf-8")))
total = len(cm)
observed = sum(1 for r in cm if r["coverage_status"] == "active_observed")
uncovered = sum(1 for r in cm if r["coverage_status"] == "uncovered_official")
sum_atc = sum(int(r["active_taxonomy_count"]) for r in cm)
if not check("C1 49 active-observed rows", observed == 49, f"observed={observed}"):
    fails += 1
if not check("C2 55 official subdomain rows", total == 55, f"total={total}"):
    fails += 1
if not check("C3 6 uncovered_official rows", uncovered == 6, f"uncovered={uncovered}"):
    fails += 1
if not check("C4 122 unique active tasks", sum_atc == 122, f"sum_active_taxonomy_count={sum_atc}"):
    fails += 1

# C5
rc = list(csv.DictReader(open("S1_01_RECLASSIFICATION_EVIDENCE.csv", encoding="utf-8")))
if not check("C5 13 reclassification rows", len(rc) == 13, f"rows={len(rc)}"):
    fails += 1
# all 13 rationale_present should be "no" (field absent)
no_rationale = sum(1 for r in rc if r["rationale_present"] == "no")
print(f"      (rationale_present=no on {no_rationale}/13 rows)")

# C6
ta = rows("evidence/task_archetype_rows.tsv")
if not check("C6 135 task-card rows", len(ta) == 135, f"rows={len(ta)}"):
    fails += 1

# C7: eval_hardGates content removed
has_present = "eval_hardGates_present" in ta[0] if ta else False
has_type = "eval_hardGates_type" in ta[0] if ta else False
has_old = "eval_hardGates" in ta[0] if ta else False
leak = 0
if ta:
    for r in ta:
        if "eval_hardGates_type" in r and r["eval_hardGates_type"] in ("list", "str"):
            # these columns must hold presence/type only, no rule text
            pass
    # scan for obvious rule-text markers in the new columns
    for r in ta:
        v = r.get("eval_hardGates_type", "") + r.get("eval_hardGates_present", "")
        if "->" in v or "0.0" in v:
            leak += 1
ok7 = has_present and has_type and (not has_old) and leak == 0
if not check("C7 eval_hardGates content removed", ok7,
             f"present_col={has_present} type_col={has_type} old_col_present={has_old} leak_rows={leak}"):
    fails += 1

# C8
ae = list(csv.DictReader(open("S1_01_TASK_ARCHETYPE_EVIDENCE.csv", encoding="utf-8")))
n_ae = len(ae)
n_ex = sum(len(r["example_task_ids"].split(";")) for r in ae if r["example_task_ids"])
if not check("C8 archetype 49 rows / 122 example tasks", n_ae == 49 and n_ex == 122,
             f"rows={n_ae} example_tasks={n_ex}"):
    fails += 1

# verifier impl vs method separated
has_impl = "verifier_impl_class" in ae[0] if ae else False
has_method = "verification_method" in ae[0] if ae else False
has_hyp = "research_hypothesis_fields" in ae[0] if ae else False
print(f"      (verifier_impl_class={has_impl} verification_method={has_method} research_hypothesis_fields={has_hyp})")

print()
print("RESULT:", "FAIL" if fails else "PASS", f"({fails} failed check(s))")
sys.exit(1 if fails else 0)
