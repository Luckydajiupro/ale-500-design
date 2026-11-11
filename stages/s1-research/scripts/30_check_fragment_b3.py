#!/usr/bin/env python3
"""S1-02B3 research fragment contract: schema and rules, single source of truth.

Input: one fragment CSV (43 EFFECTIVE-shaped columns) plus its JSON sidecar,
lives under evidence/s1_02b3_research/<stem>_candidates.csv.
Output: verdict lines on stdout. Exit 0 if every cluster passes, 1 otherwise.
Writes nothing outside the fragment directory it reads.

B3 fragments are born EFFECTIVE-shaped. Research agents fill the 32 core
columns plus the 4 evidence columns (source_support_mode, evidence_scope,
workflow_family_id, process_incident). The 7 derived columns must stay empty
here; 31_merge_b3.py is the only writer that fills them.

Contract highlights (all encoded as gates below):
- 1 <= rows per subdomain, target 3, hard cap 5 (user: 3-5 per subdomain,
  fewer than 3 only with justification, never padded beyond 5).
- evidence_kind / evidence_level / software_adaptation vocabulary mirrors B2.
- E2 is banned. E4 <=> expert_pending_proposal and source_type project_proposal.
- source_support_mode is a distinct vocabulary from software_adaptation; a
  recorded_full_support row is an original-record claim only and may carry no
  verified_E1 block (encodes the B2 evidence-scope erratum lesson).
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAG_DIR = ROOT / "evidence" / "s1_02b3_research"

FRAG_COLS = [
    "subdomain_code",
    "subdomain_business_boundary",
    "subdomain_occupations",
    "candidate_id",
    "workflow_title",
    "occupation_scope",
    "workflow_summary",
    "source_type",
    "evidence_level",
    "source_reference",
    "expert_raw_materials",
    "usage_permissions",
    "task_input",
    "professional_operations",
    "expected_deliverable",
    "success_criteria",
    "verification_approach",
    "platform_dependencies",
    "blocking_risks",
    "expert_capability",
    "cross_domain_overlap",
    "granularity_check",
    "pending_confirmation",
    "data_usage_authorization",
    "privacy_considerations",
    "research_ethics",
    "reproducibility_assessment",
    "evidence_kind",
    "source_category",
    "primary_source_url",
    "primary_claim",
    "software_adaptation",
]
DERIVED_COLS = [
    "linux_verification_state",
    "expert_pending",
    "engineering_pending",
    "fragment_path",
    "duplicate_status",
    "primary_home",
    "secondary_tag",
]
EVIDENCE_COLS = [
    "source_support_mode",
    "evidence_scope",
    "workflow_family_id",
    "process_incident",
]
B3_FRAG_COLS = FRAG_COLS + DERIVED_COLS + EVIDENCE_COLS

ETHICS_COLS = [
    "data_usage_authorization",
    "privacy_considerations",
    "research_ethics",
    "reproducibility_assessment",
]
CORE_REQUIRED = [c for c in FRAG_COLS if c not in ETHICS_COLS]

EVIDENCE_KINDS = {
    "industry_standard_complete",
    "tool_existence",
    "agent_inferred_combination",
    "expert_pending_proposal",
}
EVIDENCE_LEVELS = {"E1", "E3", "E4"}
SOURCE_TYPES = {"industry_supported", "project_proposal"}
ADAPTATIONS = {
    "native",
    "partial_function_replacement",
    "conditional",
    "unverified_or_unavailable",
    "needs_task_redesign",
}
NO_STANDARD_CLAIM_FROM = {"vendor_doc", "vendor_blog", "government_tool_page"}

SUPPORT_MODES = {
    "recorded_full_support",
    "recorded_partial_support",
    "verified_support",
    "conditional_support",
    "name_reference_support",
    "uncited_support",
    "judgment_support",
    "unspecified_support",
}
SCOPE_STATUS = {
    "as_recorded",
    "verified_E1",
    "conditional_E1",
    "name_reference",
    "uncited",
    "expert_judgment",
    "not_specified_by_code",
}
WEAK_TOKENS = {"name_reference", "uncited", "expert_judgment", "not_specified_by_code"}

MIN_ROWS = 1
TARGET_ROWS = 3
MAX_ROWS = 5

CLUSTERS = {
    "vm_cluster": {
        "subdomains": ["animation_3d", "graphic_design", "audio_music"],
        "slugs": {
            "animation_3d": "vm_anim",
            "graphic_design": "vm_gra",
            "audio_music": "vm_aud",
        },
    },
    "ts_cluster": {
        "subdomains": ["aviation", "maritime_port", "fire_safety"],
        "slugs": {
            "aviation": "ts_avi",
            "maritime_port": "ts_mar",
            "fire_safety": "ts_fir",
        },
    },
    "edu_cluster": {
        "subdomains": ["educational_technology", "library_info", "translation"],
        "slugs": {
            "educational_technology": "edu_edt",
            "library_info": "edu_lib",
            "translation": "edu_trn",
        },
    },
}

ID_SLUG: "OrderedDict[str, str]" = OrderedDict()
for _stem, _cfg in CLUSTERS.items():
    for _code, _slug in _cfg["slugs"].items():
        ID_SLUG[_code] = _slug

SUBDOMAIN_OF_CLUSTER = {
    code: stem for stem, cfg in CLUSTERS.items() for code in cfg["subdomains"]
}

ENG_FLAGS = {
    "partial_function_replacement": (
        "YES: open-source substitute covers part of the proprietary tool; "
        "functional equivalence NOT verified"
    ),
    "unverified_or_unavailable": (
        "YES: no verified open-source equivalent; engineering run NOT verified"
    ),
    "conditional": (
        "YES: tool runs only under a condition (Windows GUI, third-party "
        "container, or registration); Linux path NOT verified"
    ),
}

ID_PATTERN = re.compile(
    r"^(" + "|".join(re.escape(s) for s in ID_SLUG.values()) + r")_wf\d{2}$"
)
FAMILY_PATTERN = re.compile(r"^fc_[a-z0-9_]+(,fc_[a-z0-9_]+)*$")
INCIDENT_PATTERN = re.compile(r"^(none|inc:[^;]{1,120})$")


def parse_csv(text: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(text)))


def rows_to_dicts(rows: list[list[str]]) -> list[dict[str, str]]:
    header = rows[0]
    return [dict(zip(header, r)) for r in rows[1:]]


def parse_scope(scope_text: str):
    """Return list of (step, status) or None when malformed."""
    try:
        parts = [p for p in scope_text.split(";") if p.strip()]
        out = []
        for p in parts:
            step, status = p.split("=", 1)
            step, status = step.strip(), status.strip()
            if not step or status not in SCOPE_STATUS:
                return None
            out.append((step, status))
        return out
    except (ValueError, AttributeError):
        return None


def evidence_errors(d: dict[str, str]) -> list[str]:
    errs = []
    mode = d["source_support_mode"].strip()
    if mode not in SUPPORT_MODES:
        errs.append(
            f"source_support_mode {mode!r} not one of {sorted(SUPPORT_MODES)}"
        )
        return errs
    if mode in ADAPTATIONS or d["software_adaptation"].strip() in SUPPORT_MODES:
        errs.append(
            "source_support_mode and software_adaptation vocabularies overlap: "
            f"mode={mode!r} adaptation={d['software_adaptation']!r}"
        )
    scope = parse_scope(d["evidence_scope"])
    if scope is None:
        errs.append("evidence_scope malformed; want step=status pairs joined by ;")
        return errs
    tokens = {status for _, status in scope}
    if "verified_E1" in tokens and mode != "verified_support":
        errs.append(f"verified_E1 block requires verified_support, got {mode}")
    if "conditional_E1" in tokens and mode != "conditional_support":
        errs.append(f"conditional_E1 block requires conditional_support, got {mode}")
    if mode == "verified_support":
        if "verified_E1" not in tokens:
            errs.append("verified_support needs >=1 verified_E1 block")
        if "conditional_E1" in tokens:
            errs.append("verified_support must not carry conditional_E1")
    if mode == "conditional_support":
        if "conditional_E1" not in tokens:
            errs.append("conditional_support needs >=1 conditional_E1 block")
        if "verified_E1" in tokens:
            errs.append("conditional_support must not carry verified_E1")
    if mode == "recorded_full_support" and not tokens <= {"as_recorded"}:
        errs.append(
            "recorded_full_support is an original-record claim only; "
            f"no correction tokens allowed, got {sorted(tokens)}"
        )
    if mode == "recorded_partial_support" and (
        "verified_E1" in tokens or "conditional_E1" in tokens
    ):
        errs.append("recorded_partial_support must not carry verified/conditional blocks")
    weak_expect = {
        "name_reference_support": "name_reference",
        "uncited_support": "uncited",
        "judgment_support": "expert_judgment",
        "unspecified_support": "not_specified_by_code",
    }
    if mode in weak_expect:
        token = weak_expect[mode]
        if token not in tokens:
            errs.append(f"{mode} needs >=1 {token} block")
        if not tokens <= {"as_recorded", token}:
            errs.append(
                f"{mode} may carry only as_recorded or {token}, got {sorted(tokens)}"
            )
    return errs


def check(rows: list[list[str]], stem: str) -> dict[str, list[str]]:
    """Run every fragment check; map check-id -> error lines.

    Floors and targets are scoped to the cluster the rows belong to.
    """
    out: dict[str, list[str]] = {k: [] for k in (
        "header", "counts", "ids", "enums", "levels", "p5",
        "required", "ethics", "derived", "url", "evidence", "family",
        "incident", "warn_target",
    )}

    if not rows or rows[0] != B3_FRAG_COLS:
        out["header"].append("header must equal the 43 B3 fragment columns exactly")
        return out
    dicts = rows_to_dicts(rows)
    known = set(CLUSTERS[stem]["subdomains"])

    counts: dict[str, int] = {}
    for d in dicts:
        counts[d["subdomain_code"]] = counts.get(d["subdomain_code"], 0) + 1
    for code, n in counts.items():
        if code not in known:
            pass  # ids checks own unknown-subdomain rows
        elif n < MIN_ROWS:
            out["counts"].append(f"{code}: {n} rows below hard floor {MIN_ROWS}")
        elif n > MAX_ROWS:
            out["counts"].append(
                f"{code}: {n} rows exceed hard cap {MAX_ROWS}"
            )
    for code in known:
        n = counts.get(code, 0)
        if n < MIN_ROWS:
            out["counts"].append(f"{code}: {n} rows below hard floor {MIN_ROWS}")
        if n < TARGET_ROWS:
            out["warn_target"].append(
                f"{code}: {n} rows below target {TARGET_ROWS}; justification "
                "must be present in the JSON sidecar coverage_notes"
            )

    seen: set[str] = set()
    for d in dicts:
        cid = d["candidate_id"]
        if cid in seen:
            out["ids"].append(f"duplicate candidate_id {cid}")
        seen.add(cid)
        code = d["subdomain_code"]
        if code not in known:
            out["ids"].append(f"{cid}: unknown subdomain_code {code!r}")
            continue
        if not ID_PATTERN.match(cid):
            out["ids"].append(f"{cid}: must match {ID_PATTERN.pattern}")
        elif not cid.startswith(ID_SLUG[code] + "_wf"):
            out["ids"].append(f"{cid}: prefix must be {ID_SLUG[code]}_wf")

        if d["evidence_kind"] not in EVIDENCE_KINDS:
            out["enums"].append(f"{cid}: evidence_kind {d['evidence_kind']!r} invalid")
        level = d["evidence_level"]
        if level == "E2":
            out["enums"].append(f"{cid}: evidence_level E2 is banned")
        if level not in EVIDENCE_LEVELS:
            out["enums"].append(f"{cid}: evidence_level {level!r} invalid")
        if d["source_type"] not in SOURCE_TYPES:
            out["enums"].append(
                f"{cid}: source_type {d['source_type']!r} invalid; "
                f"want one of {sorted(SOURCE_TYPES)}"
            )
        if d["software_adaptation"] not in ADAPTATIONS:
            out["enums"].append(
                f"{cid}: software_adaptation {d['software_adaptation']!r} invalid"
            )
        if level != "E2" and level in EVIDENCE_LEVELS:
            is_e4 = level == "E4"
            is_pp = d["evidence_kind"] == "expert_pending_proposal"
            if is_e4 != is_pp:
                out["levels"].append(
                    f"{cid}: E4 <=> expert_pending_proposal; "
                    f"level={level} kind={d['evidence_kind']}"
                )
            if is_e4 and d["source_type"] != "project_proposal":
                out["levels"].append(
                    f"{cid}: E4 requires source_type=project_proposal"
                )
            if level == "E1" and d["source_type"] == "project_proposal":
                out["levels"].append(
                    f"{cid}: E1 must not pair with source_type=project_proposal"
                )
        if (
            d["evidence_kind"] == "industry_standard_complete"
            and d["source_category"] in NO_STANDARD_CLAIM_FROM
        ):
            out["p5"].append(
                f"{cid}: industry_standard_complete cannot rest on "
                f"source_category {d['source_category']!r}"
            )

        for col in CORE_REQUIRED:
            if not d[col].strip():
                out["required"].append(f"{cid}: {col} is empty")
        for col in ETHICS_COLS:
            if not d[col].strip():
                out["ethics"].append(f"{cid}: ethics column {col} is empty")
        for col in DERIVED_COLS:
            if d[col].strip():
                out["derived"].append(
                    f"{cid}: derived column {col} must stay empty in fragments; "
                    "31_merge_b3.py fills it"
                )
        if not d["primary_source_url"].strip().startswith("http"):
            out["url"].append(
                f"{cid}: primary_source_url must start with http, "
                f"got {d['primary_source_url']!r}"
            )
        out["evidence"].extend(f"{cid}: {e}" for e in evidence_errors(d))
        family = d["workflow_family_id"].strip()
        if not family or not FAMILY_PATTERN.match(family):
            out["family"].append(
                f"{cid}: workflow_family_id must be non-empty fc_* codes "
                f"joined by commas, got {family!r}"
            )
        if not INCIDENT_PATTERN.match(d["process_incident"].strip()):
            out["incident"].append(
                f"{cid}: process_incident must be 'none' or 'inc:...', "
                f"got {d['process_incident']!r}"
            )
    return out


def check_sidecar(
    stem: str, csv_dicts: list[dict[str, str]], frag_dir: Path
) -> list[str]:
    """Validate <stem>.json against the cluster spec and the CSV it describes."""
    errs: list[str] = []
    cfg = CLUSTERS[stem]
    side = frag_dir / f"{stem}.json"
    if not side.exists():
        errs.append(f"missing sidecar {side.name}")
        return errs
    try:
        data = json.loads(side.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{side.name}: invalid JSON: {exc}"]
    if set(data) != {"subdomains"}:
        errs.append(f"{side.name}: top-level keys must be exactly ['subdomains']")
        return errs
    entries = data["subdomains"]
    codes = [e.get("subdomain_code") for e in entries]
    if set(codes) != set(cfg["subdomains"]):
        errs.append(
            f"{side.name}: subdomain set {sorted(codes)} must equal "
            f"cluster spec {cfg['subdomains']}"
        )
    actual = {}
    for d in csv_dicts:
        actual[d["subdomain_code"]] = actual.get(d["subdomain_code"], 0) + 1
    for e in entries:
        code = e.get("subdomain_code")
        if "candidate_count" not in e:
            errs.append(f"{side.name}: {code} missing candidate_count")
        elif int(e["candidate_count"]) != actual.get(code, 0):
            errs.append(
                f"{side.name}: {code} candidate_count {e['candidate_count']} "
                f"!= CSV rows {actual.get(code, 0)}"
            )
        if not str(e.get("coverage_notes", "")).strip():
            errs.append(f"{side.name}: {code} coverage_notes is empty")
    return errs


def check_fragment_text(text: str, stem: str, frag_dir: Path) -> int:
    rows = parse_csv(text)
    errs = check(rows, stem)
    dicts = rows_to_dicts(rows) if rows and rows[0] == B3_FRAG_COLS else []
    errs["json"] = check_sidecar(stem, dicts, frag_dir)
    total = 0
    print(f"== fragment {stem}: {len(dicts)} rows")
    for key in ["header", "counts", "ids", "enums", "levels", "p5", "required",
                "ethics", "derived", "url", "evidence", "family", "incident",
                "json"]:
        if errs[key]:
            total += 1
            for line in errs[key]:
                print(f"   FAIL[{key}] {line}")
        else:
            print(f"   OK[{key}]")
    for line in errs["warn_target"]:
        print(f"   WARN[target] {line}")
    return total


def main() -> int:
    stems = ["vm_cluster", "ts_cluster", "edu_cluster"]
    failures = 0
    seen = 0
    for stem in stems:
        path = FRAG_DIR / f"{stem}_candidates.csv"
        if not path.exists():
            print(f"FAIL {stem}: {path} missing; run the research children first")
            failures += 1
            continue
        seen += 1
        failures += check_fragment_text(path.read_text(encoding="utf-8"), stem, FRAG_DIR)
    if seen == 0:
        print("FAIL no fragments found; run the research children first")
        return 1
    print(f"fragments ok={seen - failures} failed={failures}")
    return 1 if failures else 0


def make_row(subdomain: str, cid: str, **over) -> dict[str, str]:
    base = {c: "" for c in B3_FRAG_COLS}
    base.update({
        "subdomain_code": subdomain,
        "subdomain_business_boundary": "boundary",
        "subdomain_occupations": "occupation",
        "candidate_id": cid,
        "workflow_title": f"Title for {cid}",
        "occupation_scope": "scope",
        "workflow_summary": "summary",
        "source_type": "industry_supported",
        "evidence_level": "E3",
        "source_reference": "ref",
        "expert_raw_materials": "materials",
        "usage_permissions": "perms",
        "task_input": "inputs",
        "professional_operations": "ops",
        "expected_deliverable": "deliverable",
        "success_criteria": "criteria",
        "verification_approach": "approach",
        "platform_dependencies": "deps",
        "blocking_risks": "risks",
        "expert_capability": "capability",
        "cross_domain_overlap": "none",
        "granularity_check": "ok",
        "pending_confirmation": "none",
        "data_usage_authorization": "authorization",
        "privacy_considerations": "privacy",
        "research_ethics": "ethics",
        "reproducibility_assessment": "repro",
        "evidence_kind": "agent_inferred_combination",
        "source_category": "professional_standard",
        "primary_source_url": "http://example.invalid/p",
        "primary_claim": "claim",
        "software_adaptation": "native",
        "source_support_mode": "recorded_partial_support",
        "evidence_scope": "whole_workflow=as_recorded",
        "workflow_family_id": "fc_test",
        "process_incident": "none",
    })
    base.update(over)
    return base


def rows_text(dicts: list[dict[str, str]]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(B3_FRAG_COLS)
    for d in dicts:
        w.writerow([d[c] for c in B3_FRAG_COLS])
    return buf.getvalue()


def assert_flip(name: str, dicts, mutate, check_kind: str):
    body = rows_text(mutate(dicts))
    errs = check(parse_csv(body), "vm_cluster")
    keys = {k for k, v in errs.items() if v and k != "warn_target"}
    assert keys == {check_kind}, f"{name}: expected { {check_kind} } got {keys}"


def _row0(dicts, **over):
    mutated = make_row(dicts[0]["subdomain_code"], dicts[0]["candidate_id"], **{
        c: dicts[0][c] for c in B3_FRAG_COLS
    })
    mutated.update(over)
    return [mutated] + dicts[1:]


def selftest() -> int:
    import tempfile
    rows = [
        make_row("animation_3d", "vm_anim_wf01"),
        make_row("animation_3d", "vm_anim_wf02"),
        make_row("graphic_design", "vm_gra_wf01"),
        make_row("audio_music", "vm_aud_wf01"),
    ]
    base_text = rows_text(rows)
    good = {k: v for k, v in check(parse_csv(base_text), "vm_cluster").items()
            if k not in ("json", "warn_target")}
    assert not any(good.values()), good

    header_rows = parse_csv(base_text)
    header_rows[0] = header_rows[0][:] + ["bogus"]
    errs_header = check(header_rows, "vm_cluster")
    assert set(k for k, v in errs_header.items() if v) == {"header"}, errs_header
    print("flip OK header")

    def dup_ids(_r):
        out = [dict(d) for d in _r]
        out[1]["candidate_id"] = "vm_anim_wf01"
        return out

    def cap_rows(_r):
        out = [dict(d) for d in _r]
        for n in range(3, 7):
            out.append(make_row("animation_3d", f"vm_anim_wf0{n}"))
        return out

    flips = [
        ("counts", cap_rows, "counts"),
        ("ids-dup", dup_ids, "ids"),
        ("ids-prefix", lambda r: _row0(r, candidate_id="edu_lib_wf01"), "ids"),
        ("ids-unknown", lambda r: _row0(r, subdomain_code="robotics",
                                        candidate_id="vm_anim_wf03"), "ids"),
        ("enums-kind", lambda r: _row0(r, evidence_kind="bogus"), "enums"),
        ("enums-e2", lambda r: _row0(r, evidence_level="E2"), "enums"),
        ("enums-adapt", lambda r: _row0(r, software_adaptation="bogus"), "enums"),
        ("levels-e4", lambda r: _row0(r, evidence_level="E4",
                                      evidence_kind="agent_inferred_combination"),
         "levels"),
        ("levels-e4-sla", lambda r: _row0(r, evidence_level="E4",
                                          evidence_kind="expert_pending_proposal",
                                          source_type="industry_supported"),
         "levels"),
        ("levels-e1-pp", lambda r: _row0(r, evidence_level="E1",
                                         source_type="project_proposal"), "levels"),
        ("p5", lambda r: _row0(r, evidence_kind="industry_standard_complete",
                               source_category="vendor_doc"), "p5"),
        ("required", lambda r: _row0(r, task_input=""), "required"),
        ("ethics", lambda r: _row0(r, research_ethics=""), "ethics"),
        ("derived", lambda r: _row0(r, linux_verification_state="NOT_VERIFIED"),
         "derived"),
        ("url", lambda r: _row0(r, primary_source_url="ftp://example.invalid/p"),
         "url"),
        ("evidence-mode", lambda r: _row0(r, source_support_mode="native"),
         "evidence"),
        ("evidence-full-verified", lambda r: _row0(
            r, source_support_mode="recorded_full_support",
            evidence_scope="step_A=verified_E1"), "evidence"),
        ("evidence-verified-none", lambda r: _row0(
            r, source_support_mode="verified_support",
            evidence_scope="whole_workflow=as_recorded"), "evidence"),
        ("evidence-partial-cond", lambda r: _row0(
            r, source_support_mode="recorded_partial_support",
            evidence_scope="step_A=conditional_E1"), "evidence"),
        ("family-empty", lambda r: _row0(r, workflow_family_id=""), "family"),
        ("family-bad", lambda r: _row0(r, workflow_family_id="fc bad"), "family"),
        ("incident", lambda r: _row0(r, process_incident="yes"), "incident"),
    ]
    for name, mutate, kind in flips:
        assert_flip(name, rows, mutate, kind)
        print(f"flip OK {kind} ({name})")

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "vm_cluster_candidates.csv").write_text(base_text, encoding="utf-8")
        counts = {}
        for r in rows:
            counts[r["subdomain_code"]] = counts.get(r["subdomain_code"], 0) + 1
        good_payload = {"subdomains": [
            {"subdomain_code": c, "candidate_count": counts.get(c, 0),
             "coverage_notes": "note"}
            for c in CLUSTERS["vm_cluster"]["subdomains"]
        ]}
        (d / "vm_cluster.json").write_text(json.dumps(good_payload), encoding="utf-8")
        good_json = check_sidecar("vm_cluster", rows_to_dicts(parse_csv(base_text)), d)
        assert not good_json, good_json

        (d / "vm_cluster.json").write_text(
            json.dumps({"subdomains": good_payload["subdomains"][:2]}), encoding="utf-8")
        flipped = check_sidecar("vm_cluster", rows_to_dicts(parse_csv(base_text)), d)
        assert any("subdomain set" in e for e in flipped), flipped
        print("flip OK json")

        (d / "vm_cluster.json").write_text(
            json.dumps({"subdomains": [dict(e, candidate_count=999)
                                       for e in good_payload["subdomains"]]}),
            encoding="utf-8")
        flipped2 = check_sidecar("vm_cluster", rows_to_dicts(parse_csv(base_text)), d)
        assert any("candidate_count" in e for e in flipped2), flipped2
        print("flip OK json-count")

    print("selftest: all fragment checks flip exactly their own gate")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="S1-02B3 fragment contract checker")
    ap.add_argument("--selftest", action="store_true",
                    help="run in-memory negative self-tests")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    sys.exit(main())