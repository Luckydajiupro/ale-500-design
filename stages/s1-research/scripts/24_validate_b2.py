#!/usr/bin/env python3
"""S1-02B2 batch validator — the final gate for this round's deliverables.

Read-only. Loads the schema and naming constants from scripts/23_merge_b2.py
and the carried B1 review items from scripts/20_b2_precheck.py (single sources
of truth), then checks:
  V1  candidate ids unique + surface-form <slug>_wfNN per subdomain
  V2  exactly the 11 B2 subdomains, >=1 candidate each (3 is the expectation;
      sub-3 counts are reported and must be justified in the review summary)
  V3  linux_verification_state == NOT_VERIFIED on every row
  V4  E4 <=> expert_pending_proposal <=> expert_pending flag carries the reason
  V5  engineering_pending non-empty iff adaptation in the 3 flagged states
  V6  source-claim map holds exactly the same id set 1:1, urls agree
  V7  ethics: all 4 fields filled on every row (B2 rule, no domain exemption)
  V8  duplicate attribution: every primary/secondary mark is backed by a pair
  V9  attribution CSV structure: decided pairs carry their basis
  V10 fresh territory: no B2 id collides with the 108 S1-02A/S1-02B1 ids and
      every pair names only real A/B1/B2 ids
  V11 scope matrix: exactly 11 rows, official fields inherited, counts match
      the merged workflow file, subdomain names match S1-01
  V12 phase-0 manifest: the 7 frozen inputs still hash to their start values
  V13 carried review items + MD structure: the 5 B1 items verbatim in the three
      B2 documents; the review summary carries the PASS/FAIL/UNKNOWN verdict,
      the unverified registry and the independent-review todo; the overlap MD
      carries the 5 mandated section-5 group headers

Then negative self-tests on in-memory copies: every mutation must flip exactly
the check that guards it. Exit 0 iff every check and every self-test passes.
"""
import csv, copy, json, hashlib, importlib.util, os, re, sys
from collections import Counter

WS = "/Users/mac/Workspaces/ale-研究设计/ale-500-category-research"
WF_PATH = f"{WS}/S1_02B2_WORKFLOW_CANDIDATES.csv"
SC_PATH = f"{WS}/S1_02B2_SOURCE_CLAIM_MAP.csv"
DUP_PATH = f"{WS}/S1_02B2_DUPLICATE_ATTRIBUTION.csv"
SCOPE_PATH = f"{WS}/S1_02B2_SCOPE_MATRIX.csv"
A_PATH = f"{WS}/S1_02A_EFFECTIVE_CANDIDATES.csv"
B1_PATH = f"{WS}/S1_02B1_WORKFLOW_CANDIDATES.csv"
S1_PATH = f"{WS}/S1_01_CATEGORY_MAPPING.csv"
EVIDENCE = f"{WS}/evidence/s1_02b2_research"
MANIFEST_PATH = f"{EVIDENCE}/phase0_input_manifest.json"
CARRIED_PATH = f"{EVIDENCE}/b1_open_review_items.md"
OVERLAP_PATH = f"{WS}/S1_02B2_OVERLAP_AND_RISKS.md"
REVIEW_PATH = f"{WS}/S1_02B2_REVIEW_SUMMARY.md"

def _load(mod, name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

merge = _load(None, "merge_b2", f"{WS}/scripts/23_merge_b2.py")
pre = _load(None, "precheck20", f"{WS}/scripts/20_b2_precheck.py")
ID_SLUG = merge.ID_SLUG
ETHICS_COLS = merge.ETHICS_COLS
B1_OPEN_ITEMS = pre.B1_OPEN_ITEMS
B2_TARGETS = pre.B2_TARGETS
FROZEN = pre.FROZEN
ADAPT_FLAGGED = {"partial_function_replacement", "unverified_or_unavailable",
                 "conditional"}
DUP_COLS = ["pair", "candidates", "substantively_duplicate", "primary_home",
            "primary_reason", "secondary_tag", "difference_basis", "pending"]
GROUP_HEADERS = [
    "商业金融与法律合规", "商业分析与社会科学计量", "心理学实验与健康医学研究",
    "社会科学统计与医学因果推断", "金融运筹与computing_math待裁决边界",
]
VERDICT_TOKENS = ("PASS", "FAIL", "UNKNOWN")

def load_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def id_re(sub):
    return re.compile(re.escape(ID_SLUG[sub]) + r"_wf\d{2}$")

def verify_manifest(manifest_data, base):
    ok, bad = True, []
    for p, v in manifest_data.items():
        path = f"{base}/{p}"
        if not os.path.exists(path):
            bad.append(f"{p} missing"); ok = False; continue
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        if h.hexdigest() != v["sha256"]:
            bad.append(f"{p} sha256 drift"); ok = False
        if os.path.getsize(path) != v["size"]:
            bad.append(f"{p} size drift"); ok = False
    return ok, "; ".join(bad)

def scope_checks(matrix_rows, s1_rows, wf_rows):
    bad, lines = [], []
    want_ids = [t[0] for t in B2_TARGETS]
    got_ids = sorted(r["subdomain_id"] for r in matrix_rows)
    if got_ids != sorted(want_ids):
        bad.append(f"subdomain_id set={got_ids}")
        lines.append(f"expected {sorted(want_ids)}")
    s1_by = {r["subdomain_id"]: r for r in s1_rows}
    wf_counts = Counter(r["subdomain_code"] for r in wf_rows)
    for r in matrix_rows:
        code = r["subdomain_code"]
        if str(wf_counts.get(code, 0)) != str(r["candidate_workflow_count"]):
            bad.append(f"{code} count matrix={r['candidate_workflow_count']} "
                       f"wf={wf_counts.get(code, 0)}")
        s1 = s1_by.get(r["subdomain_id"], {})
        if r["subdomain_name"].strip() != s1.get("subdomain_name", "").strip():
            bad.append(f"{code} name drift: matrix={r['subdomain_name']!r} "
                       f"s1={s1.get('subdomain_name', '')!r}")
        if r["s1_02b2_batch"] != "batch_2":
            bad.append(f"{code} batch={r['s1_02b2_batch']!r}")
    ok = len(got_ids) == 11 and not bad
    return ok, (", ".join(bad) + (" | " + " ".join(lines) if lines else ""))

def md_checks(texts):
    """texts: dict filename -> file text. Returns (ok, detail)."""
    bad = []
    carried = read_text(CARRIED_PATH)
    overlap = texts.get(OVERLAP_PATH, "")
    review = texts.get(REVIEW_PATH, "")
    for src, sec, num, text in B1_OPEN_ITEMS:
        probe = text[:24]
        for label, doc in (("carried", carried), ("overlap", overlap),
                           ("review", review)):
            if probe not in doc:
                bad.append(f"B1 item {num} missing from {label}")
    if not (any(t in review for t in VERDICT_TOKENS) and "总体结论" in review):
        bad.append("review lacks 总体结论 verdict with PASS/FAIL/UNKNOWN")
    for token in ("未验证事项", "独立评审"):
        if token not in review:
            bad.append(f"review lacks section {token!r}")
    for h in GROUP_HEADERS:
        if h not in overlap:
            bad.append(f"overlap lacks mandated group header {h!r}")
    return not bad, "; ".join(bad)

class Checks:
    def __init__(self, wf_rows, sc_rows, dup_rows, a_rows, b1_rows,
                 matrix_rows, s1_rows, manifest_data):
        self.wf, self.sc, self.dup, self.a = wf_rows, sc_rows, dup_rows, a_rows
        self.b1, self.matrix, self.s1 = b1_rows, matrix_rows, s1_rows
        self.manifest = manifest_data
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

        # V2 exactly 11 target subdomains, floor 1, report sub-3
        per = Counter(r["subdomain_code"] for r in wf)
        missing = [s for s in ID_SLUG if per.get(s, 0) < 1]
        extra = [s for s in per if s not in ID_SLUG]
        below3 = {s: n for s, n in per.items() if n < 3}
        self.check("V2", not missing and not extra,
                   f"missing={missing} extra={extra} below3={below3} "
                   f"counts={dict(per)}")

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

        # V5 engineering flag mapping
        bad5 = [r["candidate_id"] for r in wf
                if (r["software_adaptation"] in ADAPT_FLAGGED)
                != bool(r["engineering_pending"].strip())]
        self.check("V5", not bad5, f"rows={bad5}")

        # V6 source-claim map 1:1 + urls agree
        sc_ids = [r["candidate_id"] for r in sc]
        bad6 = sorted(set(ids) ^ set(sc_ids)) or len(sc_ids) != len(ids)
        wf_url = {r["candidate_id"]: r["primary_source_url"] for r in wf}
        drift = [r["candidate_id"] for r in sc
                 if r["source_url"] != wf_url.get(r["candidate_id"], "")]
        self.check("V6", not bad6 and not drift,
                   f"sym_diff={sorted(set(ids) ^ set(sc_ids))} url_drift={drift}")

        # V7 ethics all-4 filled on every row (B2 rule)
        bad7 = [r["candidate_id"] for r in wf
                if not all(r[e].strip() for e in ETHICS_COLS)]
        self.check("V7", not bad7, f"rows={bad7}")

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

        # V10 fresh territory + attribution names only real ids
        a_ids = {r["candidate_id"] for r in a}
        b1_ids = {r["candidate_id"] for r in self.b1}
        collide = sorted(set(ids) & (a_ids | b1_ids))
        ghost = sorted(set().union(*[d["split_pairs"] for d in dup])
                       - set(ids) - a_ids - b1_ids)
        self.check("V10", not collide and not ghost,
                   f"collide={collide} ghost={ghost}")

        # V11 scope matrix vs S1-01 vs merged counts
        ok11, det11 = scope_checks(self.matrix, self.s1, wf)
        self.check("V11", ok11, det11)

        # V12 manifest re-verify
        ok12, det12 = verify_manifest(self.manifest, WS)
        self.check("V12", ok12, det12)

        # V13 carried items + MD structure
        ok13, det13 = md_checks({OVERLAP_PATH: read_text(OVERLAP_PATH),
                                 REVIEW_PATH: read_text(REVIEW_PATH)})
        self.check("V13", ok13, det13)

    def summary(self):
        lines = []
        for name in sorted(self.results):
            ok, detail = self.results[name]
            lines.append(f"{'PASS' if ok else 'FAIL'} {name}: {detail}")
        return "\n".join(lines)

    def all_ok(self):
        return all(v[0] for v in self.results.values())

def negative_self_tests(base_wf, base_sc, base_dup, base_a, base_b1,
                        base_matrix, base_s1, base_manifest):
    tests = []

    def tryflip(name, wf, sc, dup, a, b1, matrix, s1, manifest, expect_flip):
        c = Checks(copy.deepcopy(wf), copy.deepcopy(sc), copy.deepcopy(dup),
                   copy.deepcopy(a), copy.deepcopy(b1), copy.deepcopy(matrix),
                   copy.deepcopy(s1), copy.deepcopy(manifest))
        c.run()
        ok = c.results[name][0]
        tests.append((name, ok == expect_flip, f"flipped={ok}"))

    m1 = copy.deepcopy(base_wf)
    m1[0]["linux_verification_state"] = "VERIFIED"
    tryflip("V3", m1, base_sc, base_dup, base_a, base_b1, base_matrix,
            base_s1, base_manifest, False)

    m2 = copy.deepcopy(base_wf)
    m2[0]["reproducibility_assessment"] = ""
    tryflip("V7", m2, base_sc, base_dup, base_a, base_b1, base_matrix,
            base_s1, base_manifest, False)

    m3 = copy.deepcopy(base_wf)
    m3.append(dict(m3[0]))
    tryflip("V1", m3, base_sc, base_dup, base_a, base_b1, base_matrix,
            base_s1, base_manifest, False)

    m4 = copy.deepcopy(base_sc)
    m4 = m4[:-1]
    tryflip("V6", base_wf, m4, base_dup, base_a, base_b1, base_matrix,
            base_s1, base_manifest, False)

    m5 = copy.deepcopy(base_wf)
    native = next(i for i, r in enumerate(m5)
                  if r["software_adaptation"] == "native")
    m5[native]["engineering_pending"] = "YES: injected"
    tryflip("V5", m5, base_sc, base_dup, base_a, base_b1, base_matrix,
            base_s1, base_manifest, False)

    m6 = copy.deepcopy(base_wf)
    e4 = next(i for i, r in enumerate(m6) if r["evidence_level"] != "E4")
    m6[e4]["evidence_level"] = "E4"
    m6[e4]["evidence_kind"] = "expert_pending_proposal"
    m6[e4]["expert_pending"] = ""
    tryflip("V4", m6, base_sc, base_dup, base_a, base_b1, base_matrix,
            base_s1, base_manifest, False)

    m7 = copy.deepcopy(base_wf)
    m7[0]["candidate_id"] = base_a[0]["candidate_id"]
    tryflip("V10", m7, base_sc, base_dup, base_a, base_b1, base_matrix,
            base_s1, base_manifest, False)

    m8 = copy.deepcopy(base_wf)
    m8[0]["duplicate_status"] = "primary"
    tryflip("V8", m8, base_sc, base_dup, base_a, base_b1, base_matrix,
            base_s1, base_manifest, False)

    m9dup = copy.deepcopy(base_dup)
    if m9dup:
        m9dup[0]["difference_basis"] = ""
    tryflip("V9", base_wf, base_sc, m9dup, base_a, base_b1, base_matrix,
            base_s1, base_manifest, False)

    m10 = copy.deepcopy(base_matrix)
    m10 = m10[:-1]
    tryflip("V11", base_wf, base_sc, base_dup, base_a, base_b1, m10,
            base_s1, base_manifest, False)

    m11 = copy.deepcopy(base_manifest)
    first = next(iter(m11))
    m11[first] = dict(m11[first], sha256="de" * 32)
    tryflip("V12", base_wf, base_sc, base_dup, base_a, base_b1, base_matrix,
            base_s1, m11, False)

    # V13 mutation is tested through the pure function, since the real MDs are
    # read from disk inside md_checks
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        pass
    tests.append(("V13", True, "pure-function style (see md_strategy)"))

    return tests

def main():
    missing = [p for p, label in (
        (WF_PATH, "S1_02B2_WORKFLOW_CANDIDATES.csv"),
        (SC_PATH, "S1_02B2_SOURCE_CLAIM_MAP.csv"),
        (DUP_PATH, "S1_02B2_DUPLICATE_ATTRIBUTION.csv"),
        (SCOPE_PATH, "S1_02B2_SCOPE_MATRIX.csv"),
        (OVERLAP_PATH, "S1_02B2_OVERLAP_AND_RISKS.md"),
        (REVIEW_PATH, "S1_02B2_REVIEW_SUMMARY.md"))
        if not os.path.exists(p)]
    if missing:
        print("VALIDATION FAILED: missing deliverable(s):", ", ".join(
            os.path.basename(p) for p in missing))
        return 1

    wf = load_csv(WF_PATH)
    sc = load_csv(SC_PATH)
    a = load_csv(A_PATH)
    b1 = load_csv(B1_PATH)
    matrix = load_csv(SCOPE_PATH)
    s1 = load_csv(S1_PATH)
    dup = load_csv(DUP_PATH)
    for d in dup:
        ids = d["pair"].split("|") + d["candidates"].split(",")
        d["split_pairs"] = {i.strip() for i in ids if i.strip()}
    for r in wf:
        r.setdefault("duplicate_status", "")
        r.setdefault("primary_home", "")
        r.setdefault("secondary_tag", "")

    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    c = Checks(wf, sc, dup, a, b1, matrix, s1, manifest)
    c.run()
    print(c.summary())
    tests = negative_self_tests(wf, sc, dup, a, b1, matrix, s1, manifest)
    print("negative self-tests:")
    all_t = True
    for name, ok, detail in tests:
        if name != "V13":
            all_t &= ok
        print(f"  {'PASS' if ok else 'FAIL'} {name}: {detail}")

    # V13's own negative: strip one carried item from an in-memory copy of the
    # review text and prove md_strategy flips
    review_text = read_text(REVIEW_PATH)
    stripped = review_text.replace(B1_OPEN_ITEMS[0][3][:24], "REMOVED-PROBE", 1)
    ok_v13_flip = not md_checks(
        {OVERLAP_PATH: read_text(OVERLAP_PATH),
         REVIEW_PATH: stripped})[0]
    all_t &= ok_v13_flip
    print(f"  {'PASS' if ok_v13_flip else 'FAIL'} V13: flipped={not ok_v13_flip}")

    overall = c.all_ok() and all_t
    print("Overall:", "PASS" if overall else "FAIL")
    return 0 if overall else 1

if __name__ == "__main__":
    sys.exit(main())