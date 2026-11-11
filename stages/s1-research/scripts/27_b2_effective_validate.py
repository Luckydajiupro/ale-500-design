#!/usr/bin/env python3
"""S1-02B2 effective-view validator.

Validates S1_02B2_EFFECTIVE_CANDIDATES.csv against the frozen
S1_02B2_WORKFLOW_CANDIDATES.csv and scripts/b2_effective_corrections_spec.json,
re-verifies source-claim 1:1 coverage and duplicate-attribution coverage,
re-checks that all 12 frozen files keep their baseline sha256, checks the
erratum MD, enforces with V10 that the support columns never reuse the
software_adaptation vocabulary, and runs in-memory negative self-tests that must flip.

Read-only with respect to every B2 frozen artifact (nothing here rewrites
frozen files; the negative tests mutate only in-memory copies).

Exit 0 = PASS.  Usage: python3 scripts/27_b2_effective_validate.py
"""
import csv, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF_IN = os.path.join(ROOT, "S1_02B2_WORKFLOW_CANDIDATES.csv")
SC_IN = os.path.join(ROOT, "S1_02B2_SOURCE_CLAIM_MAP.csv")
DUP_IN = os.path.join(ROOT, "S1_02B2_DUPLICATE_ATTRIBUTION.csv")
EFF_IN = os.path.join(ROOT, "S1_02B2_EFFECTIVE_CANDIDATES.csv")
SPEC_IN = os.path.join(ROOT, "scripts", "b2_effective_corrections_spec.json")
ERRATUM_IN = os.path.join(ROOT, "S1_02B2_EVIDENCE_SCOPE_ERRATUM.md")
BASELINE_IN = os.path.join(ROOT, ".audit", "s1-02b2-effective", "baseline_sha256.txt")

NEW_COLS = ["source_support_mode", "evidence_scope", "workflow_family_id", "process_incident"]
DEFAULT_SCOPE = "whole_workflow=as_recorded"
FAM_RE = re.compile(r"^(|[a-z][a-z0-9_]*(,[a-z][a-z0-9_]*)*)$")
INC_RE = re.compile(r"^(none|inc:[A-Za-z0-9_,()\[\].,;:# -]+)$")

checks = []


def check(name):
    def deco(fn):
        checks.append((name, fn))
        return fn
    return deco


def load_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return list(rows[0].keys()), rows


@check("V1 structure: 39 rows, 43 cols, ids unique and order-preserved")
def v1(wf_header, wf_rows, eff_header, eff_rows):
    assert eff_header == wf_header + NEW_COLS, f"header mismatch: {eff_header[:5]}..."
    assert len(eff_rows) == 39, f"rows {len(eff_rows)}"
    ids = [r["candidate_id"] for r in eff_rows]
    assert len(set(ids)) == 39, "duplicate ids"
    wf_ids = [r["candidate_id"] for r in wf_rows]
    assert ids == wf_ids, "id set or order differs from frozen WF csv"


@check("V2 field preservation: all 39 original columns byte-identical")
def v2(wf_header, wf_rows, eff_header, eff_rows):
    by_id = {r["candidate_id"]: r for r in wf_rows}
    for r in eff_rows:
        orig = by_id[r["candidate_id"]]
        for col in wf_header:
            assert r[col] == orig[col], f"{r['candidate_id']}.{col} differs"


@check("V3 source-claim map 1:1 with effective ids")
def v3(wf_header, wf_rows, eff_header, eff_rows):
    _, sc_rows = load_csv(SC_IN)
    assert set(r["candidate_id"] for r in sc_rows) == set(r["candidate_id"] for r in eff_rows)


@check("V4 duplicate-attribution B2-side ids all resolve in effective set")
def v4(wf_header, wf_rows, eff_header, eff_rows):
    _, dup_rows = load_csv(DUP_IN)
    eff_ids = {r["candidate_id"] for r in eff_rows}
    b2_ids = {r["candidate_id"] for r in wf_rows}
    for row in dup_rows:
        pair_ids = row["pair"].split("|")
        involved = [cid for cid in pair_ids if cid in b2_ids]
        assert involved, f"pair {row['pair']} has no B2-side id"
        for cid in involved:
            assert cid in eff_ids, f"B2-side dup-pair id {cid} missing from effective set"


@check("V5 source_support_mode evidence-state rule and spec equality")
def v5(wf_header, wf_rows, eff_header, eff_rows):
    _, overall_enum, _, _, _, by_level = vocab()
    spec = load_spec()
    for r in eff_rows:
        cid = r["candidate_id"]
        val = r["source_support_mode"]
        assert val in overall_enum, f"{cid} invalid mode {val!r}"
        if cid in spec["corrections"]:
            assert val == spec["corrections"][cid]["source_support_mode"], f"{cid} mode != spec"
        else:
            lvl = r["evidence_level"]
            assert lvl in by_level, f"{cid} unexpected evidence_level {lvl!r}"
            assert val == by_level[lvl], f"{cid} mode {val!r} != {by_level[lvl]!r} for {lvl}"


@check("V6 evidence_scope spec equality and default")
def v6(wf_header, wf_rows, eff_header, eff_rows):
    spec = load_spec()
    for r in eff_rows:
        cid = r["candidate_id"]
        val = r["evidence_scope"]
        assert val and "=" in val, f"{cid} empty or malformed scope"
        if cid in spec["corrections"]:
            assert val == spec["corrections"][cid]["evidence_scope"], f"{cid} scope != spec"
        else:
            assert val == DEFAULT_SCOPE, f"{cid} scope != default"


@check("V7 workflow_family_id regex and spec equality")
def v7(wf_header, wf_rows, eff_header, eff_rows):
    spec = load_spec()
    for r in eff_rows:
        cid = r["candidate_id"]
        val = r["workflow_family_id"]
        assert FAM_RE.match(val), f"{cid} bad family id {val!r}"
        if cid in spec["corrections"]:
            assert val == spec["corrections"][cid]["workflow_family_id"], f"{cid} family != spec"
        else:
            assert val == "", f"{cid} non-corrected family not empty"


@check("V8 process_incident regex, spec and extended equality")
def v8(wf_header, wf_rows, eff_header, eff_rows):
    spec = load_spec()
    for r in eff_rows:
        cid = r["candidate_id"]
        val = r["process_incident"]
        assert INC_RE.match(val), f"{cid} bad incident {val!r}"
        if cid in spec["corrections"]:
            assert val == spec["corrections"][cid]["process_incident"], f"{cid} incident != spec"
        elif cid in spec.get("process_incidents_extended", {}):
            assert val == spec["process_incidents_extended"][cid], f"{cid} incident != extended spec"
        else:
            assert val == "none", f"{cid} incident != none"


@check("V9 every spec id exists in the effective table")
def v9(wf_header, wf_rows, eff_header, eff_rows):
    spec = load_spec()
    ids = {r["candidate_id"] for r in eff_rows}
    for cid in spec["corrections"]:
        assert cid in ids, f"spec correction id {cid} missing"
    for cid in spec.get("process_incidents_extended", {}):
        assert cid in ids, f"spec extended id {cid} missing"
    assert set(spec["corrections"]) == {"psy_comp_wf01", "psy_exp_wf04", "biz_cmp_wf03", "biz_mkt_wf02", "biz_quant_wf02"}


@check("V10 semantic separation: support columns never reuse adaptation vocabulary")
def v10(wf_header, wf_rows, eff_header, eff_rows):
    adapt_enum, overall_enum, block_states, strength, weakest_map, by_level = vocab()
    assert not (adapt_enum & overall_enum), "overall vocabulary overlaps software_adaptation enum"
    assert not (adapt_enum & block_states), "block-state vocabulary overlaps software_adaptation enum"
    spec = load_spec()
    for r in eff_rows:
        cid = r["candidate_id"]
        assert r["source_support_mode"] != r["software_adaptation"], f"{cid} source_support_mode copies software_adaptation"
        if cid in spec["corrections"]:
            blocks = [b.split("=", 1)[1].split("(", 1)[0] for b in re.split(r";(?=[a-z][a-z0-9_]*=)", r["evidence_scope"])]
            assert blocks, f"{cid} evidence_scope has no blocks"
            for st in blocks:
                assert st in block_states, f"{cid} unknown block state {st!r}"
            weakest = min(blocks, key=lambda s: strength.get(s, 0))
            assert weakest in strength, f"{cid} weakest state {weakest!r} not in strength map"
            assert r["source_support_mode"] == weakest_map[weakest], (
                f"{cid} overall {r['source_support_mode']!r} != weakest-state value {weakest_map[weakest]!r}"
            )
        else:
            assert r["evidence_scope"] == DEFAULT_SCOPE, f"{cid} uncorrected row scope != default"
            lvl = r["evidence_level"]
            assert lvl in by_level, f"{cid} unexpected evidence_level {lvl!r}"
            assert r["source_support_mode"] == by_level[lvl], f"{cid} mode not derived from evidence_level"
            if lvl == "E3":
                assert r["source_support_mode"] == "recorded_partial_support", f"{cid} E3 row shows full support"


@check("V11 frozen-file sha256 unchanged vs baseline snapshot")
def v11(wf_header, wf_rows, eff_header, eff_rows):
    with open(BASELINE_IN, encoding="utf-8") as f:
        expect = {}
        for line in f:
            line = line.strip()
            if not line:
                continue
            h, path = line.split(None, 1)
            expect[path] = h
    assert len(expect) == 12, f"baseline has {len(expect)} entries"
    for path, h in expect.items():
        with open(path, "rb") as f:
            cur = hashlib.sha256(f.read()).hexdigest()
        assert cur == h, f"frozen file changed: {path}"


@check("V12 erratum MD exists and names the corrected rows")
def v12(wf_header, wf_rows, eff_header, eff_rows):
    assert os.path.exists(ERRATUM_IN), "erratum md not yet generated"
    text = open(ERRATUM_IN, encoding="utf-8").read()
    norm = lambda s: re.sub(r"\s+", "", s)
    text_n = norm(text)
    for cid in ["psy_comp_wf01", "psy_exp_wf04", "biz_cmp_wf03", "biz_mkt_wf02", "biz_quant_wf02"]:
        assert cid in text, f"erratum missing {cid}"
    assert "## 新增列定义" in text, "erratum missing column definitions section"
    spec = load_spec()
    for cid, c in spec["corrections"].items():
        assert norm(c["evidence_scope"]) in text_n, f"erratum missing scope string for {cid}"
        assert norm(c["change_reason"]) in text_n, f"erratum missing change_reason for {cid}"
        if c["process_incident"] != "none":
            assert norm(c["process_incident"]) in text_n, f"erratum missing incident string for {cid}"


def load_spec():
    with open(SPEC_IN, encoding="utf-8") as f:
        return json.load(f)


def vocab():
    meta = load_spec()["meta"]
    return (
        set(meta["software_adaptation_enum"]),
        set(meta["source_support_mode_enum"]),
        set(meta["block_state_vocabulary"]),
        meta["block_strength"],
        meta["overall_weakest_map"],
        meta["uncorrected_mode_by_evidence_level"],
    )


def run_checks(wf_header, wf_rows, eff_header, eff_rows):
    for name, fn in checks:
        fn(wf_header, wf_rows, eff_header, eff_rows)
        print(f"PASS {name}")
    return True


def negatives(wf_header, wf_rows, eff_header, eff_rows):
    results = []

    def flip(name, mutate, probe):
        bad_header, bad_rows = mutate(wf_header, wf_rows, eff_header, eff_rows)
        passed = False
        try:
            probe(wf_header, wf_rows, bad_header, bad_rows)
            passed = True
        except AssertionError:
            pass
        assert not passed, f"negative {name} did NOT flip"
        results.append(name)

    flip("n1 drop_row", lambda wh, wr, eh, er: (eh, er[:-1]), v1)
    flip(
        "n2 tamper_original_value",
        lambda wh, wr, eh, er: (eh, [dict(r, workflow_title=r["workflow_title"] + "X") for r in er]),
        v2,
    )
    flip(
        "n3 tamper_evidence_scope",
        lambda wh, wr, eh, er: (eh, [dict(r, evidence_scope=r["evidence_scope"] + ";extra=1") if r["candidate_id"] == "psy_exp_wf04" else r for r in er]),
        v6,
    )
    flip(
        "n4 bad_source_support_mode",
        lambda wh, wr, eh, er: (
            eh,
            [dict(r, source_support_mode="nativeX") if r["candidate_id"] == "biz_cmp_wf03" else r for r in er],
        ),
        v5,
    )
    flip(
        "n5 spec_id_missing",
        lambda wh, wr, eh, er: (eh, [r for r in er if r["candidate_id"] != "psy_comp_wf01"]),
        v1,
    )
    flip(
        "n6 duplicate_id",
        lambda wh, wr, eh, er: (eh, er + [dict(er[0])]),
        v1,
    )
    corrected_ids = {"psy_comp_wf01", "psy_exp_wf04", "biz_cmp_wf03", "biz_mkt_wf02", "biz_quant_wf02"}
    flip(
        "n7 v10_copied_adaptation",
        lambda wh, wr, eh, er: (
            eh,
            [
                dict(r, source_support_mode=r["software_adaptation"])
                if r["evidence_level"] == "E3" and r["candidate_id"] not in corrected_ids
                else r
                for r in er
            ],
        ),
        v10,
    )
    flip(
        "n8 v10_wrong_overall",
        lambda wh, wr, eh, er: (
            eh,
            [dict(r, source_support_mode="uncited_support") if r["candidate_id"] == "psy_exp_wf04" else r for r in er],
        ),
        v10,
    )
    print("PASS negative self-tests: " + ", ".join(results))


def main():
    wf_header, wf_rows = load_csv(WF_IN)
    assert len(wf_header) == 39 and len(wf_rows) == 39
    eff_header, eff_rows = load_csv(EFF_IN)
    run_checks(wf_header, wf_rows, eff_header, eff_rows)
    negatives(wf_header, wf_rows, eff_header, eff_rows)
    print("Overall: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())