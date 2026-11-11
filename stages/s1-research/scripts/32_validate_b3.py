#!/usr/bin/env python3
"""S1-02B3 deliverable validator.

Reads the six S1-02B3 deliverables plus the prior A/B1/B2-effective files,
the scope matrix, the frozen manifest, and the S1-01 mapping, then runs
V1-V14 below. Verdicts print OK/FAIL; exit 0 only when every check passes.

V1  B3 candidate ids unique and of the form <slug>_wfNN
V2  exactly the 9 target subdomains, >=1 row each (reports <3 sets)
V3  linux_verification_state all NOT_VERIFIED
V4  E4 <=> expert_pending_proposal <=> expert_pending flag "YES: E4: <pending>"
V5  engineering_pending non-empty <=> adaptation in {pfr, unverified, conditional}
V6  source claim map rows 1:1 with workflow rows by id and url
V7  ethics columns non-empty on every row
V8  duplicate_status values, primary/secondary must be grounded in attribution
V9  attribution CSV structure and per-row requirements
V10 no id collision with A/B1/B2-effective; attribution cites only real ids
V11 scope matrix = 9 S1-01 targets, batch_3, counts equal merged rows
V12 frozen manifest rehash passes
V13 B1 open items verbatim in both MDs, review carries verdict tokens,
    overlap carries the 5 B3 group headers
V14 per-row evidence semantics: support mode vocabulary, scope block
    consistency, workflow_family_id and process_incident forms

Selftests (--selftest) mutate one violation at a time and require exactly the
matching V-check to flip. No model calls, no writes outside .audit evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
AUDIT_DIR = ROOT / ".audit"

DELIVERABLES = [
    "S1_02B3_SCOPE_MATRIX.csv",
    "S1_02B3_WORKFLOW_CANDIDATES.csv",
    "S1_02B3_SOURCE_CLAIM_MAP.csv",
    "S1_02B3_DUPLICATE_ATTRIBUTION.csv",
    "S1_02B3_OVERLAP_AND_RISKS.md",
    "S1_02B3_REVIEW_SUMMARY.md",
]
DUP_COLS = [
    "pair",
    "candidates",
    "substantively_duplicate",
    "primary_home",
    "primary_reason",
    "secondary_tag",
    "difference_basis",
    "pending",
]
GROUP_HEADERS = [
    "视觉媒体与工程设计邻接边界",
    "视觉媒体与商业金融品牌资产",
    "交通安全与城市规划工程",
    "教育信息与健康医疗宣教",
    "教育信息与法律出版与版权",
]
VERDICT_TOKENS = ("PASS", "FAIL", "UNKNOWN")
ENG_FLAG_ADAPTATIONS = {
    "partial_function_replacement", "unverified_or_unavailable", "conditional"}


def _load(name: str):
    spec = importlib.util.spec_from_file_location(
        name, SCRIPT_DIR / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_frag = _load("30_check_fragment_b3")
_28 = _load("28_b3_precheck")


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_open_items() -> list[str]:
    path = ROOT / "evidence" / "s1_02b2_research" / "b1_open_review_items.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    return [ln.split(". ", 1)[1] for ln in lines if re.match(r"^\d\. ", ln)]


def v1_ids(wf: list[dict[str, str]]) -> list[str]:
    errs = []
    seen = set()
    pattern = re.compile("^(" + "|".join(
        re.escape(s) for s in _frag.ID_SLUG.values()) + ")_wf\\d{2}$")
    for r in wf:
        cid = r["candidate_id"]
        if cid in seen:
            errs.append(f"duplicate id {cid}")
        seen.add(cid)
        if not pattern.match(cid):
            errs.append(f"id form invalid: {cid}")
    return errs


def v2_subdomains(wf: list[dict[str, str]]) -> list[str]:
    errs = []
    counts = {}
    for r in wf:
        counts[r["subdomain_code"]] = counts.get(r["subdomain_code"], 0) + 1
    want = set(_frag.ID_SLUG)
    have = set(counts)
    if have != want:
        errs.append(f"subdomain set {sorted(have)} != targets {sorted(want)}")
    low = [c for c, n in counts.items() if n < 3]
    if low:
        errs.append(f"subdomains below target 3: {low}")
    return errs


def v3_linux(wf: list[dict[str, str]]) -> list[str]:
    return [f"{r['candidate_id']}: {r['linux_verification_state']}"
            for r in wf if r["linux_verification_state"] != "NOT_VERIFIED"]


def v4_e4(wf: list[dict[str, str]]) -> list[str]:
    errs = []
    for r in wf:
        is_e4 = r["evidence_level"] == "E4"
        is_pp = r["evidence_kind"] == "expert_pending_proposal"
        want = f"YES: E4: {r['pending_confirmation']}" if is_pp else ""
        if is_e4 != is_pp:
            errs.append(f"{r['candidate_id']}: E4/EPP mismatch")
        if r["expert_pending"] != want:
            errs.append(
                f"{r['candidate_id']}: expert_pending {r['expert_pending']!r}"
                f" != expected {want!r}")
    return errs


def v5_eng(wf: list[dict[str, str]]) -> list[str]:
    errs = []
    for r in wf:
        adapt = r["software_adaptation"]
        expect = _frag.ENG_FLAGS.get(adapt, "")
        if r["engineering_pending"] != expect:
            errs.append(
                f"{r['candidate_id']}: engineering_pending"
                f" {r['engineering_pending']!r} != expected {expect!r}")
    return errs


def v6_scmap(wf: list[dict[str, str]], sc: list[dict[str, str]]) -> list[str]:
    errs = []
    wf_ids = {r["candidate_id"] for r in wf}
    sc_ids = {r["candidate_id"] for r in sc}
    if wf_ids != sc_ids:
        errs.append(f"claim map id set mismatch: wf {len(wf_ids)} sc {len(sc_ids)}")
    if len(sc_ids) != len(sc):
        errs.append("claim map has duplicate ids")
    url = {r["candidate_id"]: r["primary_source_url"] for r in wf}
    for r in sc:
        if r["candidate_id"] in url and r["source_url"] != url[r["candidate_id"]]:
            errs.append(f"{r['candidate_id']}: claim url != workflow url")
    return errs


def v7_ethics(wf: list[dict[str, str]]) -> list[str]:
    errs = []
    for r in wf:
        for col in _frag.ETHICS_COLS:
            if not r[col].strip():
                errs.append(f"{r['candidate_id']}: {col} empty")
    return errs


def _attribution_ids(dup: list[dict[str, str]]) -> set[str]:
    ids = set()
    for d in dup:
        for token in d["pair"].split("|") + d["candidates"].split(","):
            if token.strip():
                ids.add(token.strip())
    return ids


def v8_dupstatus(wf, dup) -> list[str]:
    errs = []
    cited = _attribution_ids(dup)
    for r in wf:
        st = r["duplicate_status"]
        if st not in {"primary", "secondary", "none"}:
            errs.append(f"{r['candidate_id']}: duplicate_status {st!r}")
        elif st == "primary" and not r["primary_home"].strip():
            errs.append(f"{r['candidate_id']}: primary without primary_home")
        elif st == "secondary" and not r["secondary_tag"].strip():
            errs.append(f"{r['candidate_id']}: secondary without secondary_tag")
        elif st != "none" and r["candidate_id"] not in cited:
            errs.append(f"{r['candidate_id']}: {st} not cited in attribution")
    return errs


def v9_dupfile(dup: list[dict[str, str]]) -> list[str]:
    errs = []
    for d in dup:
        pair = d["pair"].split("|")
        cands = [c for c in d["candidates"].split(",") if c.strip()]
        if len(pair) != 2 or len(cands) < 2:
            errs.append(f"{d['pair']}: pair/candidates malformed")
        if set(pair) != set(cands):
            errs.append(f"{d['pair']}: pair and candidates disagree")
        if d["substantively_duplicate"] == "yes":
            if not d["primary_home"].strip():
                errs.append(f"{d['pair']}: yes without primary_home")
            if d["difference_basis"].strip():
                errs.append(f"{d['pair']}: yes must clear difference_basis")
        elif d["substantively_duplicate"] == "no":
            if not d["difference_basis"].strip():
                errs.append(f"{d['pair']}: no without difference_basis")
            if d["primary_home"].strip():
                errs.append(f"{d['pair']}: no must clear primary_home")
        else:
            errs.append(f"{d['pair']}: substantively_duplicate "
                        f"{d['substantively_duplicate']!r}")
        if d["pending"].strip():
            errs.append(f"{d['pair']}: pending must be empty")
    return errs


def v10_collision(wf, prior_ids: set[str], dup) -> list[str]:
    errs = []
    for r in wf:
        if r["candidate_id"] in prior_ids:
            errs.append(f"{r['candidate_id']} collides with a prior batch id")
    real = {r["candidate_id"] for r in wf} | prior_ids
    for cid in sorted(_attribution_ids(dup) - real):
        errs.append(f"attribution cites unknown id {cid}")
    return errs


def v11_scopecounts(wf, scope: list[dict[str, str]]) -> list[str]:
    errs = []
    if len(scope) != 9:
        errs.append(f"scope matrix rows {len(scope)} != 9")
    got = {(r["subdomain_id"], r["subdomain_code"]): r for r in scope}
    counts = {}
    for r in wf:
        counts[r["subdomain_code"]] = counts.get(r["subdomain_code"], 0) + 1
    for sid, code, name in _28.B3_TARGETS:
        r = got.get((sid, code))
        if r is None:
            errs.append(f"scope matrix missing {sid} {code}")
            continue
        if r["subdomain_name"] != name:
            errs.append(f"{sid}: scope name {r['subdomain_name']!r} != {name!r}")
        if r["s1_02b3_batch"] != "batch_3":
            errs.append(f"{sid}: batch {r['s1_02b3_batch']!r} != batch_3")
        if r["candidate_workflow_count"] != str(counts.get(code, 0)):
            errs.append(f"{code}: scope count {r['candidate_workflow_count']}"
                        f" != merged {counts.get(code, 0)}")
    return errs


def v12_manifest(manifest_path: Path) -> list[str]:
    return _28.verify_manifest_at(manifest_path) if manifest_path else []


def v13_mds(overlap_text: str, review_text: str,
            open_items: list[str]) -> list[str]:
    errs = []
    for i, item in enumerate(open_items, 1):
        if item not in overlap_text:
            errs.append(f"overlap MD missing carried B1 item {i}")
        if item not in review_text:
            errs.append(f"review MD missing carried B1 item {i}")
    for h in GROUP_HEADERS:
        if h not in overlap_text:
            errs.append(f"overlap MD missing group header {h!r}")
    if "总体结论" not in review_text:
        errs.append("review MD missing 总体结论")
    if not any(t in review_text for t in VERDICT_TOKENS):
        errs.append(f"review MD missing verdict token {VERDICT_TOKENS}")
    if "未验证事项" not in review_text:
        errs.append("review MD missing 未验证事项")
    if "独立评审" not in review_text:
        errs.append("review MD missing 独立评审")
    return errs


def v14_evidence(wf: list[dict[str, str]]) -> list[str]:
    errs = []
    for r in wf:
        errs.extend(f"{r['candidate_id']}: {e}"
                    for e in _frag.evidence_errors(r))
        if not _frag.FAMILY_PATTERN.match(r["workflow_family_id"].strip()):
            errs.append(f"{r['candidate_id']}: workflow_family_id form")
        if not _frag.INCIDENT_PATTERN.match(r["process_incident"].strip()):
            errs.append(f"{r['candidate_id']}: process_incident form")
    return errs


CHECK_DEFS = [
    ("V1", lambda c: v1_ids(c["wf"])),
    ("V2", lambda c: v2_subdomains(c["wf"])),
    ("V3", lambda c: v3_linux(c["wf"])),
    ("V4", lambda c: v4_e4(c["wf"])),
    ("V5", lambda c: v5_eng(c["wf"])),
    ("V6", lambda c: v6_scmap(c["wf"], c["sc"])),
    ("V7", lambda c: v7_ethics(c["wf"])),
    ("V8", lambda c: v8_dupstatus(c["wf"], c["dup"])),
    ("V9", lambda c: v9_dupfile(c["dup"])),
    ("V10", lambda c: v10_collision(c["wf"], c["prior_ids"], c["dup"])),
    ("V11", lambda c: v11_scopecounts(c["wf"], c["scope"])),
    ("V12", lambda c: v12_manifest(c.get("manifest"))),
    ("V13", lambda c: v13_mds(c["overlap"], c["review"], c["open_items"])),
    ("V14", lambda c: v14_evidence(c["wf"])),
]


def run_checks(ctx: dict) -> dict[str, list[str]]:
    return {tag: fn(ctx) for tag, fn in CHECK_DEFS}


def selftest() -> int:
    import tempfile

    def check(name, ok: bool):
        assert ok, name
        print(f"flip OK {name}")

    def make_wf_row(subdomain, cid, **over):
        base = {c: "" for c in _frag.B3_FRAG_COLS}
        base.update({
            "subdomain_code": subdomain,
            "subdomain_business_boundary": "b",
            "subdomain_occupations": "o",
            "candidate_id": cid,
            "workflow_title": f"Title {cid}",
            "occupation_scope": "s",
            "workflow_summary": "sum",
            "source_type": "industry_supported",
            "evidence_level": "E3",
            "source_reference": "ref",
            "expert_raw_materials": "m",
            "usage_permissions": "p",
            "task_input": "i",
            "professional_operations": "op",
            "expected_deliverable": "del",
            "success_criteria": "crit",
            "verification_approach": "verif",
            "platform_dependencies": "dep",
            "blocking_risks": "risk",
            "expert_capability": "cap",
            "cross_domain_overlap": "none",
            "granularity_check": "ok",
            "pending_confirmation": "none",
            "data_usage_authorization": "auth",
            "privacy_considerations": "priv",
            "research_ethics": "eth",
            "reproducibility_assessment": "rep",
            "evidence_kind": "agent_inferred_combination",
            "source_category": "professional_standard",
            "primary_source_url": f"http://example.invalid/{cid}",
            "primary_claim": "claim",
            "software_adaptation": "native",
            "linux_verification_state": "NOT_VERIFIED",
            "expert_pending": "",
            "engineering_pending": "",
            "fragment_path": _frag.SUBDOMAIN_OF_CLUSTER[subdomain],
            "duplicate_status": "none",
            "primary_home": "",
            "secondary_tag": "",
            "source_support_mode": "recorded_partial_support",
            "evidence_scope": "whole_workflow=as_recorded",
            "workflow_family_id": "fc_test",
            "process_incident": "none",
        })
        base.update(over)
        return base

    wf = []
    for code, slug in _frag.ID_SLUG.items():
        for n in range(1, 4):
            wf.append(make_wf_row(code, f"{slug}_wf{n:02d}"))

    def build_sc(rows):
        return [{
            "candidate_id": r["candidate_id"],
            "subdomain_code": r["subdomain_code"],
            "workflow_title": r["workflow_title"],
            "source_url": r["primary_source_url"],
            "source_category": r["source_category"],
            "evidence_kind": r["evidence_kind"],
            "evidence_level": r["evidence_level"],
            "source_type": r["source_type"],
            "software_adaptation": r["software_adaptation"],
            "correction_note": "",
        } for r in rows]

    def build_scope(rows):
        counts = {}
        for r in rows:
            counts[r["subdomain_code"]] = counts.get(r["subdomain_code"], 0) + 1
        return [{
            "subdomain_id": sid, "subdomain_code": code,
            "subdomain_name": name, "s1_02b3_batch": "batch_3",
            "candidate_workflow_count": str(counts.get(code, 0)),
        } for sid, code, name in _28.B3_TARGETS]

    sc = build_sc(wf)
    scope = build_scope(wf)

    open_items = [f"carried item {i} text" for i in range(1, 6)]
    overlap_md = "\n".join(GROUP_HEADERS) + "\n" + "\n".join(open_items)
    review_md = ("总体结论: PASS\n未验证事项: none\n独立评审: pending\n"
                 + "\n".join(open_items))
    dup = [dict(zip(DUP_COLS, [
        "vm_anim_wf01|vm_anim_wf02", "vm_anim_wf01,vm_anim_wf02", "no",
        "", "none", "", "different task_input; different deliverable", ""]))]

    def ctx_of(prior_ids=None, manifest=None, **over):
        rows = over["wf"] if "wf" in over else wf
        c = {
            "wf": rows,
            "sc": over["sc"] if "sc" in over else build_sc(rows),
            "scope": over["scope"] if "scope" in over else build_scope(rows),
            "dup": dup,
            "prior_ids": prior_ids or set(),
            "open_items": open_items,
            "overlap": overlap_md, "review": review_md,
            "manifest": manifest,
        }
        c.update(over)
        return c

    base_ctx = ctx_of()
    for tag, errs in run_checks(base_ctx).items():
        if tag == "V12":
            continue
        assert errs == [], (tag, errs)
    print("flip OK baseline-clean")

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        f = d / "f.txt"
        f.write_text("data", encoding="utf-8")
        import hashlib
        good = hashlib.sha256(b"data").hexdigest()
        mp = d / "man.json"
        mp.write_text(json.dumps(
            {"files": {str(f.resolve()): {"sha256": good, "size": 4}}}),
            encoding="utf-8")
        base_ctx = ctx_of(manifest=mp)
        base_checks = run_checks(base_ctx)
        assert base_checks["V12"] == [], base_checks["V12"]
        print("flip OK V12-clean")

        mp.write_text(json.dumps(
            {"files": {str(f.resolve()): {"sha256": "0" * 64, "size": 4}}}),
            encoding="utf-8")
        checks12 = run_checks(ctx_of(manifest=mp))
        assert checks12["V12"], "V12 drift must flip V12"
        assert all(not checks12[tag] for tag, _ in CHECK_DEFS
                   if tag != "V12"), "V12 flip leaked"
        check("v12-drift", True)

    def flip(name, mut, expected_fail):
        resp = run_checks(mut())
        fails = {t for t, errs in resp.items() if errs}
        exp = {expected_fail} if isinstance(expected_fail, str) else set(expected_fail)
        assert fails == exp, f"{name}: expected {exp} got {fails}"
        print(f"flip OK {name}")

    def repl(idx, **over):
        rows = [dict(r) for r in wf]
        rows[idx].update(over)
        return rows

    flip("v1-dup", lambda: ctx_of(wf=wf + [dict(wf[0])]), {"V1", "V6"})
    flip("v1-form", lambda: ctx_of(wf=repl(2, candidate_id="vm_anim_wfX")), "V1")
    flip("v2-missing", lambda: ctx_of(wf=[r for r in wf if r["subdomain_code"] != "aviation"]), "V2")
    flip("v3-linux", lambda: ctx_of(wf=repl(0, linux_verification_state="VERIFIED")), "V3")
    flip("v4-e4", lambda: ctx_of(wf=repl(0, evidence_level="E4",
                                          evidence_kind="expert_pending_proposal",
                                          pending_confirmation="await expert")), "V4")
    flip("v5-eng", lambda: ctx_of(wf=repl(0, engineering_pending="YES: bogus")), "V5")
    flip("v6-sc", lambda: ctx_of(sc=sc[:-1]), "V6")
    flip("v7-ethics", lambda: ctx_of(wf=repl(0, research_ethics="")), "V7")
    flip("v8-dup", lambda: ctx_of(wf=repl(5, duplicate_status="primary",
                                           primary_home="vm_gra_wf01")), "V8")
    flip("v9-dup", lambda: ctx_of(dup=[dict(dup[0], difference_basis="")]), "V9")
    flip("v10-collide", lambda: ctx_of(prior_ids={"vm_anim_wf01"}), "V10")
    flip("v11-scope", lambda: ctx_of(scope=scope[:-1]), "V11")
    flip("v13-item", lambda: ctx_of(review="总体结论: PASS\n未验证事项: x\n独立评审: y\n"), "V13")
    flip("v13-header", lambda: ctx_of(overlap="\n".join(GROUP_HEADERS[1:]) + "\n" + overlap_md.split(GROUP_HEADERS[0])[-1]), "V13")
    flip("v14-mode", lambda: ctx_of(wf=repl(0, source_support_mode="native")), "V14")
    flip("v14-scope", lambda: ctx_of(wf=repl(0, source_support_mode="recorded_full_support",
                                              evidence_scope="step_A=verified_E1")), "V14")
    print("selftest: all validation checks flip exactly their own gate")
    return 0


def main() -> int:
    missing = [n for n in DELIVERABLES if not (ROOT / n).is_file()]
    if missing:
        print("FAIL missing deliverables:", missing)
        return 1
    wf = read_csv(ROOT / "S1_02B3_WORKFLOW_CANDIDATES.csv")
    sc = read_csv(ROOT / "S1_02B3_SOURCE_CLAIM_MAP.csv")
    dup = read_csv(ROOT / "S1_02B3_DUPLICATE_ATTRIBUTION.csv")
    scope = read_csv(ROOT / "S1_02B3_SCOPE_MATRIX.csv")
    overlap_text = (ROOT / "S1_02B3_OVERLAP_AND_RISKS.md").read_text(
        encoding="utf-8")
    review_text = (ROOT / "S1_02B3_REVIEW_SUMMARY.md").read_text(
        encoding="utf-8")
    prior_ids = set()
    for name in ("S1_02A_EFFECTIVE_CANDIDATES.csv",
                 "S1_02B1_WORKFLOW_CANDIDATES.csv",
                 "S1_02B2_EFFECTIVE_CANDIDATES.csv"):
        prior_ids |= {r["candidate_id"] for r in read_csv(ROOT / name)}
    ctx = {
        "wf": wf, "sc": sc, "dup": dup, "scope": scope,
        "prior_ids": prior_ids,
        "open_items": load_open_items(),
        "overlap": overlap_text, "review": review_text,
        "manifest": AUDIT_DIR / "s1-02b3-frozen-manifest.json",
    }
    fails = 0
    for tag, fn in CHECK_DEFS:
        errs = fn(ctx)
        if errs:
            fails += 1
            print(f"FAIL {tag} ({len(errs)})")
            for e in errs[:12]:
                print(f"     {e}")
            if len(errs) > 12:
                print(f"     ... {len(errs) - 12} more")
        else:
            print(f"OK   {tag}")
    print(f"validations failed={fails} total={len(CHECK_DEFS)}")
    return 1 if fails else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="S1-02B3 deliverable validator")
    ap.add_argument("--selftest", action="store_true",
                    help="run in-memory negative self-tests")
    args = ap.parse_args()
    sys.exit(selftest() if args.selftest else main())