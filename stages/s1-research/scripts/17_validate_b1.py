#!/usr/bin/env python3
"""S1-02B1 U9 — validator for this round's standalone deliverables.

Read-only: it never writes the deliverables. It loads the service schema and
the naming constants from scripts/16_merge_b1.py (single source of truth) and
checks:
  V1  candidate ids unique + surface-form <slug>_wfNN per subdomain
  V2  exactly the 13 target subdomains, >=3 candidates each
  V3  linux_verification_state == NOT_VERIFIED on every row (nothing verified)
  V4  E4 <=> expert_pending_proposal <=> expert_pending flag carries the reason
  V5  engineering_pending non-empty iff adaptation in
      {partial_function_replacement, unverified_or_unavailable, conditional}
      (the exact A flag convention: A flagged 21 rows = 15+2+4)
  V6  source-claim map has exactly the same id set as the workflow file, 1:1
  V7  ethics: life_/med_ rows carry all 4 fields, phys_ rows all 4 empty
  V8  duplicate attribution: every primary/secondary row has its mark
      (duplicate_status in {primary,secondary,none}; primary_home filled on
      primary; secondary_tag filled on secondary; primary count == secondary
      count; every marked role appears as a pair in the attribution CSV)
  V9  attribution CSV structure: pair, candidates, substantively_duplicate,
      primary_home, primary_reason, secondary_tag, difference_basis, pending;
      every pair carries a decided primary_home, and pending is empty
  V10 fresh territory: no B1 id collides with the 51 S1-02A ids; every pair in
      the attribution CSV that involves an A id names real A ids

Then it runs negative self-tests on an in-memory copy (the S1-02A validator
pattern): each mutation must flip exactly the check that guards it.

Exit 0 iff every V-check and every negative self-test passes.
"""
import csv, importlib.util, os, re, sys
from collections import Counter

WS = "/Users/mac/Workspaces/ale-研究设计/ale-500-category-research"
WF_PATH = f"{WS}/S1_02B1_WORKFLOW_CANDIDATES.csv"
SC_PATH = f"{WS}/S1_02B1_SOURCE_CLAIM_MAP.csv"
DUP_PATH = f"{WS}/S1_02B1_DUPLICATE_ATTRIBUTION.csv"
A_PATH = f"{WS}/S1_02A_EFFECTIVE_CANDIDATES.csv"

# load the merge script as the schema authority
spec = importlib.util.spec_from_file_location(
    "merge_b1", f"{WS}/scripts/16_merge_b1.py")
merge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(merge)
ID_SLUG = merge.ID_SLUG
ETHICS_COLS = merge.ETHICS_COLS
LIFE_HEALTH = merge.LIFE_HEALTH_PREFIXES
ADAPT_FLAGGED = {"partial_function_replacement", "unverified_or_unavailable",
                 "conditional"}
DUP_COLS = ["pair", "candidates", "substantively_duplicate", "primary_home",
            "primary_reason", "secondary_tag", "difference_basis", "pending"]

def load_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def id_re(sub):
    return re.compile(re.escape(ID_SLUG[sub]) + r"_wf\d{2}$")

class Checks:
    def __init__(self, wf_rows, sc_rows, dup_rows, a_rows):
        self.wf, self.sc, self.dup, self.a = wf_rows, sc_rows, dup_rows, a_rows
        self.results = {}

    def check(self, name, ok, detail=""):
        self.results[name] = (ok, detail)

    def run(self):
        wf, sc, dup, a = self.wf, self.sc, self.dup, self.a

        # V1 unique ids + surface form
        ids = [r["candidate_id"] for r in wf]
        bad = [i for i, n in Counter(ids).items() if n > 1]
        forms = [r["candidate_id"] for r in wf
                 if not id_re(r["subdomain_code"]).fullmatch(r["candidate_id"])]
        self.check("V1", not bad and not forms,
                   f"dup={sorted(bad)} bad_form={sorted(forms)}")

        # V2 exactly 13 subdomains, floor 3
        per = Counter(r["subdomain_code"] for r in wf)
        missing = [s for s in ID_SLUG if per.get(s, 0) < 3]
        extra = [s for s in per if s not in ID_SLUG]
        self.check("V2", not missing and not extra,
                   f"missing={missing} extra={extra} counts={dict(per)}")

        # V3 linux state
        bad_l = [r["candidate_id"] for r in wf
                 if r["linux_verification_state"] != "NOT_VERIFIED"]
        self.check("V3", not bad_l, f"rows={bad_l}")

        # V4 E4 <=> expert_pending_proposal <=> flag carries reason
        bad4 = []
        for r in wf:
            is_e4 = r["evidence_level"] == "E4"
            is_epp = r["evidence_kind"] == "expert_pending_proposal"
            flag = r["expert_pending"]
            ok = is_e4 and is_epp and flag.startswith("YES: E4:")
            ok = ok or (not is_e4 and not is_epp and flag == "")
            if not ok:
                bad4.append(r["candidate_id"])
        self.check("V4", not bad4, f"rows={bad4}")

        # V5 engineering flag mapping (A convention)
        bad5 = []
        for r in wf:
            flagged = r["software_adaptation"] in ADAPT_FLAGGED
            has = bool(r["engineering_pending"].strip())
            if flagged != has:
                bad5.append(r["candidate_id"])
        self.check("V5", not bad5, f"rows={bad5}")

        # V6 source-claim map 1:1 with workflow ids, urls agree
        sc_ids = [r["candidate_id"] for r in sc]
        bad6 = sorted(set(ids) ^ set(sc_ids)) or len(sc_ids) != len(ids)
        wf_url = {r["candidate_id"]: r["primary_source_url"] for r in wf}
        drift = [r["candidate_id"] for r in sc
                 if r["source_url"] != wf_url.get(r["candidate_id"], "")]
        self.check("V6", not bad6 and not drift,
                   f"sym_diff={sorted(set(ids) ^ set(sc_ids))} url_drift={drift}")

        # V7 ethics all-4 or none-4
        bad7 = []
        for r in wf:
            filled = all(r[e].strip() for e in ETHICS_COLS)
            any_f = any(r[e].strip() for e in ETHICS_COLS)
            want = r["candidate_id"].startswith(LIFE_HEALTH)
            if want and not filled:
                bad7.append(r["candidate_id"] + " (life/med, empty fields)")
            if not want and any_f:
                bad7.append(r["candidate_id"] + " (phys, ethics must be empty)")
        self.check("V7", not bad7, f"rows={bad7[:8]}")

        # V8 per-row duplicate marks consistent with the adjudication file
        bad8, prims, secs = [], 0, 0
        pair_ids = set()
        for d in dup:
            pair_ids.update(p for p in d["split_pairs"])
        for r in wf:
            st = r.get("duplicate_status", "")
            if st not in {"primary", "secondary", "none"}:
                bad8.append(r["candidate_id"] + f" bad status {st!r}")
            if st == "primary":
                prims += 1
                if not r.get("primary_home", "").strip():
                    bad8.append(r["candidate_id"] + " primary without primary_home")
            if st == "secondary":
                secs += 1
                if not r.get("secondary_tag", "").strip():
                    bad8.append(r["candidate_id"] + " secondary without secondary_tag")
            if st in {"primary", "secondary"} and r["candidate_id"] not in pair_ids:
                bad8.append(r["candidate_id"] + " marked but not in attribution pairs")
        if prims != secs:
            bad8.append(f"imbalance primary={prims} secondary={secs}")
        self.check("V8", not bad8, f"issues={bad8[:8]}")

        # V9 attribution CSV structure + decided rows
        bad9 = []
        if dup:
            cols = list(dup[0].keys())
            if cols != DUP_COLS + ["split_pairs"]:
                bad9.append(f"cols={cols}")
        for d in dup:
            sd = d["substantively_duplicate"]
            if sd not in {"yes", "no"}:
                bad9.append(f"pair {d['pair']} substantively_duplicate={sd!r}")
            if sd == "yes":
                if not d["primary_home"].strip():
                    bad9.append(f"pair {d['pair']} yes without primary_home")
                if not d["secondary_tag"].strip():
                    bad9.append(f"pair {d['pair']} yes without secondary_tag")
            else:
                if not d["difference_basis"].strip():
                    bad9.append(f"pair {d['pair']} no without difference_basis")
                if d["primary_home"].strip():
                    bad9.append(f"pair {d['pair']} no but primary_home set")
            if d["pending"].strip():
                bad9.append(f"pair {d['pair']} pending={d['pending']}")
        self.check("V9", not bad9, f"issues={bad9[:8]}")

        # V10 fresh territory + attribution only names real ids
        a_ids = {r["candidate_id"] for r in a}
        collide = sorted(set(ids) & a_ids)
        ghost = sorted(set().union(*[d["split_pairs"] for d in dup]) - set(ids) - a_ids)
        self.check("V10", not collide and not ghost,
                   f"collide={collide} ghost={ghost}")

    def summary(self):
        lines = []
        for name in sorted(self.results):
            ok, detail = self.results[name]
            lines.append(f"{'PASS' if ok else 'FAIL'} {name}: {detail}")
        return "\n".join(lines)

    def all_ok(self):
        return all(v[0] for v in self.results.values())

def negative_self_tests(base_wf, base_sc, base_dup, base_a):
    """Each mutation must flip exactly the check that guards it."""
    import copy
    tests = []

    def tryflip(name, wf, sc, dup, a, expect_flip):
        c = Checks(copy.deepcopy(wf), copy.deepcopy(sc),
                   copy.deepcopy(dup), copy.deepcopy(a))
        c.run()
        ok = c.results[name][0]
        tests.append((name, ok == expect_flip, f"flipped={ok}"))

    wf = base_wf
    m1 = copy.deepcopy(base_wf)
    m1[0]["linux_verification_state"] = "VERIFIED"
    tryflip("V3", m1, base_sc, base_dup, base_a, False)

    m2 = copy.deepcopy(base_wf)
    med = next(i for i, r in enumerate(m2)
               if r["candidate_id"].startswith("med_"))
    m2[med]["reproducibility_assessment"] = ""
    tryflip("V7", m2, base_sc, base_dup, base_a, False)

    m3 = copy.deepcopy(base_wf)
    m3.append(dict(m3[0]))
    tryflip("V1", m3, base_sc, base_dup, base_a, False)

    m4 = copy.deepcopy(base_sc)
    m4 = m4[:-1]
    tryflip("V6", base_wf, m4, base_dup, base_a, False)

    m5 = copy.deepcopy(base_wf)
    native = next(i for i, r in enumerate(m5)
                  if r["software_adaptation"] == "native")
    m5[native]["engineering_pending"] = "YES: injected"
    tryflip("V5", m5, base_sc, base_dup, base_a, False)

    m6 = copy.deepcopy(base_wf)
    # B1 has no E4 rows; promote one E1 row to E4+expert_pending_proposal with a
    # blank expert_pending flag so the E4 pairing check guards the pairing
    e4 = next(i for i, r in enumerate(m6) if r["evidence_level"] == "E1")
    m6[e4]["evidence_level"] = "E4"
    m6[e4]["evidence_kind"] = "expert_pending_proposal"
    m6[e4]["expert_pending"] = ""
    tryflip("V4", m6, base_sc, base_dup, base_a, False)

    m7 = copy.deepcopy(base_wf)
    a_id = base_a[0]["candidate_id"]
    m7[0]["candidate_id"] = a_id
    tryflip("V10", m7, base_sc, base_dup, base_a, False)

    m8 = copy.deepcopy(base_wf)
    m8[0]["duplicate_status"] = "primary"
    tryflip("V8", m8, base_sc, base_dup, base_a, False)

    m9dup = copy.deepcopy(base_dup)
    if m9dup:
        m9dup[0]["difference_basis"] = ""
    tryflip("V9", base_wf, base_sc, m9dup, base_a, False)

    return tests

def main():
    missing = [p for p, label in ((WF_PATH, "S1_02B1_WORKFLOW_CANDIDATES.csv"),
               (SC_PATH, "S1_02B1_SOURCE_CLAIM_MAP.csv"),
               (DUP_PATH, "S1_02B1_DUPLICATE_ATTRIBUTION.csv"),
               (A_PATH, "S1_02A_EFFECTIVE_CANDIDATES.csv")) if not os.path.exists(p)]
    if missing:
        print("VALIDATION FAILED: missing deliverable(s):", ", ".join(
            os.path.basename(p) for p in missing))
        return 1

    wf = load_csv(WF_PATH)
    sc = load_csv(SC_PATH)
    a = load_csv(A_PATH)
    # the attribution file gets a derived column: every id named in pair/candidates
    dup = load_csv(DUP_PATH)
    for d in dup:
        ids = d["pair"].split("|") + d["candidates"].split(",")
        d["split_pairs"] = {i.strip() for i in ids if i.strip()}
    # tolerate missing annotation cols on WF until U8 has run
    for r in wf:
        r.setdefault("duplicate_status", "")
        r.setdefault("primary_home", "")
        r.setdefault("secondary_tag", "")

    c = Checks(wf, sc, dup, a)
    c.run()
    print(c.summary())
    tests = negative_self_tests(wf, sc, dup, a)
    print("negative self-tests:")
    all_t = True
    for name, ok, detail in tests:
        all_t &= ok
        print(f"  {'PASS' if ok else 'FAIL'} {name}: {detail}")
    overall = c.all_ok() and all_t
    print("Overall:", "PASS" if overall else "FAIL")
    return 0 if overall else 1

if __name__ == "__main__":
    sys.exit(main())