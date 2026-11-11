#!/usr/bin/env python3
"""S1-02A revision validation — negative-case checks (review task 7).

Beyond the count/schema checks in scripts/10_validate.py, this asserts the
revision round's negative cases:

  N1  missing evidence      — every non-E4 candidate has a traceable source URL;
                               every E4 candidate is flagged expert_pending_proposal
  N2  wrong attribution      — scan/ATPG candidates are attributed to semiconductor
                               (IC-level), not electronics (PCB-level); eng_electronics_wf02
                               is flagged mis-attributed
  N3  duplicate candidates   — all 3 known duplicate pairs have a substantive verdict
  N4  wrong environment      — HEC-RAS is conditional (not native); Minitab is not
                               Linux-native; OpenROAD/ATPG is unverified_or_unavailable
  N5  unsupported equivalence— no candidate claims EPANET=HEC-RAS or
                               open-source ATPG = commercial ATPG

Exit 0 only if ALL checks pass. Prints PASS/FAIL per check + violations.
"""
import csv, sys

CL = list(csv.DictReader(open("S1_02A_SOURCE_CLAIM_MAP.csv", encoding="utf-8")))
DUP = list(csv.DictReader(open("S1_02A_DUPLICATE_ATTRIBUTION.csv", encoding="utf-8")))
WC = list(csv.DictReader(open("S1_02A_WORKFLOW_CANDIDATES.csv", encoding="utf-8")))
BY_ID = {r["candidate_id"]: r for r in WC}
CL_BY_ID = {r["candidate_id"]: r for r in CL}

fails = []

def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        fails.append(name)

# N1 missing evidence
n1_bad = []
for r in CL:
    is_e4 = r["evidence_kind"] == "expert_pending_proposal" or r["evidence_level"] == "E4"
    if is_e4:
        if r["evidence_kind"] != "expert_pending_proposal":
            n1_bad.append(f"{r['candidate_id']}: E4 but not flagged expert_pending_proposal")
    else:
        if not r["source_url"].strip():
            n1_bad.append(f"{r['candidate_id']}: no source URL but not E4")
check("N1 missing evidence", not n1_bad, "; ".join(n1_bad[:5]))

# N2 wrong attribution: scan/ATPG is IC-level -> semiconductor
n2_bad = []
for cid in ("eng_electronics_wf02", "eng_semiconductor_wf03"):
    title = BY_ID[cid]["workflow_title"].lower()
    if cid == "eng_electronics_wf02":
        if "scan" in title or "atpg" in title:
            # it is a scan/ATPG candidate filed under electronics -> mis-attributed
            if "mis-attributed" not in CL_BY_ID[cid]["correction_note"].lower():
                n2_bad.append(f"{cid}: scan/ATPG filed under electronics but not flagged mis-attributed")
        else:
            n2_bad.append(f"{cid}: expected scan/ATPG title")
    # both must land in the duplicate verdict
dp = {(d["candidates"].split(" vs ")[0].strip(), d["candidates"].split(" vs ")[1].strip())
      for d in DUP}
if ("eng_electronics_wf02", "eng_semiconductor_wf03") not in dp and \
   ("eng_semiconductor_wf03", "eng_electronics_wf02") not in dp:
    n2_bad.append("DFT pair not present in DUPLICATE_ATTRIBUTION")
check("N2 wrong attribution", not n2_bad, "; ".join(n2_bad[:5]))

# N3 duplicate candidates: 3 pairs present with substantive verdict
n3_bad = []
expected_pairs = {
    ("eng_civilgeo_wf02", "ag_envwater_wf03"),
    ("eng_civilgeo_wf03", "ag_envwater_wf04"),
    ("eng_electronics_wf02", "eng_semiconductor_wf03"),
}
got = set()
for d in DUP:
    a, b = [x.strip() for x in d["candidates"].split(" vs ")]
    got.add(tuple(sorted((a, b))))
    if d["substantively_duplicate"].strip().upper() != "YES":
        n3_bad.append(f"{a}/{b}: not marked substantively_duplicate=YES")
for p in expected_pairs:
    if tuple(sorted(p)) not in got:
        n3_bad.append(f"missing pair {p}")
check("N3 duplicate candidates", not n3_bad, "; ".join(n3_bad[:5]))

# N4 wrong environment
n4_bad = []
env_expect = {
    "eng_civilgeo_wf02": ("conditional", "HEC-RAS is Windows-only; Linux is third-party"),
    "ag_envwater_wf03": ("conditional", "HEC-RAS is Windows-only; Linux is third-party"),
    "eng_manufacturing_wf02": ("partial_function_replacement", "Minitab is not Linux-native"),
    "eng_electronics_wf02": ("unverified_or_unavailable", "OpenROAD/ATPG not a verified equivalent"),
    "eng_semiconductor_wf03": ("unverified_or_unavailable", "open ATPG not verified equivalent"),
}
for cid, (want, why) in env_expect.items():
    got_a = CL_BY_ID[cid]["software_adaptation"]
    if got_a != want:
        n4_bad.append(f"{cid}: adaptation={got_a}, want {want} ({why})")
# HEC-RAS must NOT be native anywhere
for r in CL:
    if "HEC-RAS" in r["correction_note"] and r["software_adaptation"] == "native":
        n4_bad.append(f"{r['candidate_id']}: HEC-RAS marked native")
check("N4 wrong environment", not n4_bad, "; ".join(n4_bad[:5]))

# N5 unsupported equivalence: scan source_claim_map notes + original CSV claims
n5_bad = []
forbidden = [
    ("OpenROAD", "ATPG"),
    ("EPANET", "HEC-RAS"),
]
for r in WC:
    txt = (r["platform_dependencies"] + " " + r["verification_approach"] + " " +
           r["pending_confirmation"]).lower()
    if "openroad" in txt and "atpg" in txt and "not" not in txt.split("atpg")[0][-60:]:
        # rough: flag any OpenROAD+ATPG co-claim that is not already negated
        if "scan" not in txt and "atpg" in txt:
            n5_bad.append(f"{r['candidate_id']}: OpenROAD+ATPG equivalence claim")
# EPANET=HEC-RAS: must never be described as interchangeable
for r in WC:
    txt = (r["workflow_summary"] + " " + r["pending_confirmation"]).lower()
    if "epanet" in txt and "hec-ras" in txt and "substitut" in txt:
        n5_bad.append(f"{r['candidate_id']}: EPANET/HEC-RAS substitution claim")
check("N5 unsupported equivalence", not n5_bad, "; ".join(n5_bad[:5]))

print()
if fails:
    print(f"RESULT: FAIL ({len(fails)} checks failed)")
    sys.exit(1)
print("RESULT: PASS (all negative-case checks)")
