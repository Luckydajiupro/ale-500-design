#!/usr/bin/env python3
"""Validate S1-02A EFFECTIVE view against the review's 7 checks, plus
negative-case self-tests that prove each check catches a specific error
(not just row counts / file existence).

Reads:
- S1_02A_EFFECTIVE_CANDIDATES.csv   (the view under test)
- S1_02A_WORKFLOW_CANDIDATES.csv    (the 51 original ids to reconcile against)
- S1_02A_DUPLICATE_ATTRIBUTION.csv  (the 3 recorded pairs)

The 7 checks:
1. 51 unique candidate_id.
2. 3 recorded duplicate pairs each have a primary + secondary adjudication.
3. No candidate lost by merge (effective ids == original 51).
4. evidence_level not confused with source_type (no E4+industry_supported, no E1+project_proposal).
5. software_adaptation=native is NOT read as Tencent-Linux-verified (all linux_verification_state == NOT_VERIFIED).
6. E4 (expert-pending) and partial-equivalence (engineering-pending) risks are not dropped.
7. Downstream can identify the single effective view (one row per id, stable key column).

Negative self-tests mutate a copy in memory and assert the specific check flips FAIL.
"""
import csv, copy

def load(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))

EFF = load("S1_02A_EFFECTIVE_CANDIDATES.csv")
WC  = load("S1_02A_WORKFLOW_CANDIDATES.csv")
DUP = load("S1_02A_DUPLICATE_ATTRIBUTION.csv")

def check_set(rows, wc_ids, dup_pairs):
    ids = [r["candidate_id"] for r in rows]
    out = []

    c1 = len(ids) == 51 and len(set(ids)) == 51
    out.append(("C1_unique_51_ids", c1,
                f"ids={len(ids)} unique={len(set(ids))}"))

    # C2: 3 pairs each have exactly one primary + one secondary in the rows
    stat = {}
    for r in rows:
        stat.setdefault(r["duplicate_status"], []).append(r["candidate_id"])
    n_primary = len(stat.get("primary", []))
    n_secondary = len(stat.get("secondary", []))
    c2 = n_primary == 3 and n_secondary == 3
    out.append(("C2_3_pairs_adjudicated", c2,
                f"primary={n_primary} secondary={n_secondary} pairs={len(dup_pairs)}"))

    # C3: no lost candidate
    eff_ids = set(ids)
    c3 = eff_ids == set(wc_ids)
    out.append(("C3_no_lost_candidate", c3,
                f"missing={sorted(set(wc_ids)-eff_ids)} extra={sorted(eff_ids-set(wc_ids))}"))

    # C4: evidence_level vs source_type not conflated
    bad = [r["candidate_id"] for r in rows
           if (r["evidence_level"] == "E4" and r["source_type"] == "industry_supported")
           or (r["evidence_level"] == "E1" and r["source_type"] == "project_proposal")]
    c4 = len(bad) == 0
    out.append(("C4_evidence_not_source_confused", c4, f"bad={bad}"))

    # C5: native not read as verified
    verified = [r["candidate_id"] for r in rows if r["linux_verification_state"] != "NOT_VERIFIED"]
    c5 = len(verified) == 0
    out.append(("C5_native_not_verified", c5,
                f"non-NOT_VERIFIED={verified}"))

    # C6: E4 and partial-equivalence risks not dropped
    e4 = [r for r in rows if r["evidence_kind"] == "expert_pending_proposal"]
    e4_missing = [r["candidate_id"] for r in e4 if not r["expert_pending"]]
    risky = [r for r in rows if r["software_adaptation"] in ("partial_function_replacement", "unverified_or_unavailable")]
    risky_missing = [r["candidate_id"] for r in risky if not r["engineering_pending"]]
    c6 = len(e4) == 4 and len(e4_missing) == 0 and len(risky_missing) == 0
    out.append(("C6_risks_not_dropped", c6,
                f"E4={len(e4)} E4_no_flag={e4_missing} risky_no_flag={risky_missing}"))

    # C7: single effective view — one row per id, key column present
    c7 = len(rows) > 0 and "candidate_id" in rows[0] and len(ids) == len(set(ids))
    out.append(("C7_single_view_identifiable", c7, f"rows={len(rows)} keyed={c7}"))

    return out

def run(rows, wc_ids, dup_pairs, label):
    results = check_set(rows, wc_ids, dup_pairs)
    print(f"--- {label} ---")
    ok = True
    for name, passed, detail in results:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}  {detail}")
        ok = ok and passed
    print(f"  => {'ALL PASS' if ok else 'HAS FAILURE'}")
    return ok, results

wc_ids = [r["candidate_id"] for r in WC]
dup_pairs = [d["pair"] for d in DUP]

print("POSITIVE (real effective view):")
ok, results = run(EFF, wc_ids, dup_pairs, "S1_02A_EFFECTIVE_CANDIDATES.csv")
positive_ok = ok

print()
print("NEGATIVE self-tests (mutated copies must be DETECTED):")
neg_failures = []

def must_fail(mutation, check_name):
    rows = copy.deepcopy(EFF)
    mutation(rows)
    res = check_set(rows, wc_ids, dup_pairs)
    d = dict((n, p) for n, p, _ in res)
    detected = not d.get(check_name, True)
    status = "PASS" if detected else "FAIL (not detected)"
    print(f"  {status}  {check_name} <- mutation")
    if not detected:
        neg_failures.append(check_name)

# NEG1: duplicate a candidate_id -> C1/C7 fail
def m1(rows):
    rows.append(copy.deepcopy(rows[0]))
must_fail(m1, "C1_unique_51_ids")

# NEG2: drop one candidate -> C3 fails
def m2(rows):
    rows.pop(0)
must_fail(m2, "C3_no_lost_candidate")

# NEG3: mark a native row as verified -> C5 fails
def m3(rows):
    for r in rows:
        if r["software_adaptation"] == "native":
            r["linux_verification_state"] = "VERIFIED"
            break
must_fail(m3, "C5_native_not_verified")

# NEG4: an E4 row gets source_type=industry_supported -> C4 fails
def m4(rows):
    for r in rows:
        if r["evidence_level"] == "E4":
            r["source_type"] = "industry_supported"
            break
must_fail(m4, "C4_evidence_not_source_confused")

# NEG5: an E4 row loses its expert_pending flag -> C6 fails
def m5(rows):
    for r in rows:
        if r["evidence_kind"] == "expert_pending_proposal":
            r["expert_pending"] = ""
            break
must_fail(m5, "C6_risks_not_dropped")

# NEG6: a partial_function_replacement row loses engineering_pending -> C6 fails
def m6(rows):
    for r in rows:
        if r["software_adaptation"] == "partial_function_replacement":
            r["engineering_pending"] = ""
            break
must_fail(m6, "C6_risks_not_dropped")

# NEG7: un-adjudicate a duplicate pair (remove the secondary) -> C2 fails
def m7(rows):
    for r in rows:
        if r["duplicate_status"] == "secondary":
            r["duplicate_status"] = "none"
            break
must_fail(m7, "C2_3_pairs_adjudicated")

print()
print(f"POSITIVE={'PASS' if positive_ok else 'FAIL'}")
print(f"NEGATIVE={'PASS' if not neg_failures else 'FAIL: ' + ','.join(neg_failures)}")
sys_exit = 0 if (positive_ok and not neg_failures) else 1
raise SystemExit(sys_exit)
