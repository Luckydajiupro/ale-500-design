#!/usr/bin/env python3
"""Per-fragment contract checker for S1-02B1.

Usage: python3 scripts/18_check_fragment.py <stem>
  stem in {phys_cluster, life_cluster, med_a, med_b}

Checks the fragment CSV + JSON written by one research child against the
S1-02B1 schema contract before the U7 merge. Exit 0 = PASS, exit 1 = FAIL.
"""

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
FRAG_DIR = WS / "evidence" / "s1_02b1_research"

FRAG_COLS = [
    "subdomain_code", "subdomain_business_boundary", "subdomain_occupations",
    "candidate_id", "workflow_title", "occupation_scope", "workflow_summary",
    "source_type", "evidence_level", "source_reference",
    "expert_raw_materials", "usage_permissions", "task_input",
    "professional_operations", "expected_deliverable", "success_criteria",
    "verification_approach", "platform_dependencies", "blocking_risks",
    "expert_capability", "cross_domain_overlap", "granularity_check",
    "pending_confirmation",
    "data_usage_authorization", "privacy_considerations",
    "research_ethics", "reproducibility_assessment",
    "evidence_kind", "source_category", "primary_source_url", "primary_claim",
    "software_adaptation",
]
ETHICS_COLS = ["data_usage_authorization", "privacy_considerations",
               "research_ethics", "reproducibility_assessment"]
EVIDENCE_KINDS = {"industry_standard_complete", "tool_existence",
                  "agent_inferred_combination", "expert_pending_proposal"}
EVIDENCE_LEVELS = {"E1", "E2", "E3", "E4"}
ADAPTATIONS = {"native", "partial_function_replacement", "conditional",
               "unverified_or_unavailable", "needs_task_redesign"}
NO_STANDARD_CLAIM_FROM = {"vendor_doc", "vendor_blog", "government_tool_page"}
SLA = "industry_supported"
PP = "project_proposal"

CLUSTERS = {
    "phys_cluster": {
        "subdomains": ["physics", "chemistry_materials", "astronomy",
                       "earth_atmo"],
        "slugs": {"physics": "phys_phys", "chemistry_materials": "phys_chem",
                  "astronomy": "phys_astro", "earth_atmo": "phys_earth"},
        "ethics_required": False,
    },
    "life_cluster": {
        "subdomains": ["biomolecular", "genomics", "cell_imaging",
                       "systems_microbial"],
        "slugs": {"biomolecular": "life_biomol", "genomics": "life_genom",
                  "cell_imaging": "life_cellimg",
                  "systems_microbial": "life_sysmic"},
        "ethics_required": True,
    },
    "med_a": {
        "subdomains": ["clinical_diagnostics", "therapeutic_oncology"],
        "slugs": {"clinical_diagnostics": "med_diag",
                  "therapeutic_oncology": "med_onco"},
        "ethics_required": True,
    },
    "med_b": {
        "subdomains": ["clinical_informatics", "public_health",
                       "clinical_trials"],
        "slugs": {"clinical_informatics": "med_inform",
                  "public_health": "med_pubhealth",
                  "clinical_trials": "med_trials"},
        "ethics_required": True,
    },
}

FAILURES = []


def fail(msg):
    FAILURES.append(msg)
    print("  FAIL " + msg)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in CLUSTERS:
        raise SystemExit("usage: 18_check_fragment.py "
                         "<phys_cluster|life_cluster|med_a|med_b>")
    stem = sys.argv[1]
    spec = CLUSTERS[stem]
    csv_path = FRAG_DIR / f"{stem}_candidates.csv"
    json_path = FRAG_DIR / f"{stem}.json"
    print(f"checking fragment {stem}")

    if not csv_path.exists():
        fail(f"{csv_path} missing")
    if not json_path.exists():
        fail(f"{json_path} missing")
    if FAILURES:
        raise SystemExit(1)

    raw_lines = csv_path.read_text(encoding="utf-8").splitlines()
    if raw_lines[0] != ",".join(FRAG_COLS):
        fail("header row is not the exact 32-column FRAG_COLS header")
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    if len(rows) < 3 * len(spec["subdomains"]):
        fail(f"row floor: expected >= {3 * len(spec['subdomains'])}, "
             f"got {len(rows)}")
    print(f"  rows={len(rows)}")

    counts = Counter(r["subdomain_code"] for r in rows)
    for sub in spec["subdomains"]:
        n = counts.get(sub, 0)
        if n < 3:
            fail(f"{sub}: only {n} candidates, floor is 3")
        else:
            print(f"  {sub}={n}")

    ids = [r["candidate_id"] for r in rows]
    if len(set(ids)) != len(ids):
        fail("duplicate candidate_id values")
    id_re = re.compile(
        "^(" + "|".join(spec["slugs"].values()) + r")_wf\d{2}$")
    for cid in ids:
        if not id_re.match(cid):
            fail(f"bad candidate_id {cid}")
    for r in rows:
        if r["subdomain_code"] in spec["subdomains"]:
            slug = spec["slugs"][r["subdomain_code"]]
            if not r["candidate_id"].startswith(slug + "_wf"):
                fail(f"{r['candidate_id']}: id slug does not match "
                     f"subdomain {r['subdomain_code']}")

    for r in rows:
        if r["evidence_kind"] not in EVIDENCE_KINDS:
            fail(f"{r['candidate_id']}: bad evidence_kind "
                 f"{r['evidence_kind']}")
        if r["evidence_level"] not in EVIDENCE_LEVELS:
            fail(f"{r['candidate_id']}: bad evidence_level "
                 f"{r['evidence_level']}")
        if r["evidence_level"] == "E2":
            fail(f"{r['candidate_id']}: E2 forbidden by child brief")
        if (r["evidence_kind"] == "expert_pending_proposal") != \
                (r["evidence_level"] == "E4"):
            fail(f"{r['candidate_id']}: E4 <-> expert_pending_proposal "
                 f"mismatch ({r['evidence_kind']}/{r['evidence_level']})")
        if r["evidence_kind"] == "industry_standard_complete" and \
                r["source_category"] in NO_STANDARD_CLAIM_FROM:
            fail(f"{r['candidate_id']}: industry_standard_complete backed by "
                 f"weak source category {r['source_category']}")
        if r["evidence_level"] == "E4" and r["source_type"] == SLA:
            fail(f"{r['candidate_id']}: E4 must not be {SLA}")
        if r["evidence_level"] == "E1" and r["source_type"] == PP:
            fail(f"{r['candidate_id']}: E1 must not be {PP}")
        if r["source_type"] not in {SLA, PP}:
            fail(f"{r['candidate_id']}: bad source_type {r['source_type']}")
        if r["software_adaptation"] not in ADAPTATIONS:
            fail(f"{r['candidate_id']}: bad software_adaptation "
                 f"{r['software_adaptation']}")
        non_empty = [c for c in FRAG_COLS
                     if c not in ETHICS_COLS and not r[c].strip()]
        if non_empty:
            fail(f"{r['candidate_id']}: empty non-ethics field(s) "
                 f"{','.join(non_empty)}")
        empty_ethics = [c for c in ETHICS_COLS if not r[c].strip()]  # noqa
        if spec["ethics_required"] and empty_ethics:
            fail(f"{r['candidate_id']}: ethics field(s) empty "
                 f"{','.join(empty_ethics)}")
        if not spec["ethics_required"] and len(empty_ethics) != 4:
            remaining = set(ETHICS_COLS) - set(empty_ethics)
            fail(f"{r['candidate_id']}: phys cluster must leave all 4 ethics "
                 f"fields empty, filled {sorted(remaining)}")

    print("  kind=" + str(dict(Counter(r["evidence_kind"] for r in rows))))
    print("  level=" + str(dict(Counter(r["evidence_level"] for r in rows))))

    j = json.loads(json_path.read_text(encoding="utf-8"))
    if list(j.keys()) != ["subdomains"]:
        fail("json top-level key must be exactly 'subdomains'")
    subs = sorted(s["subdomain_code"] for s in j["subdomains"])
    if subs != sorted(spec["subdomains"]):
        fail(f"json subdomains {subs} != expected {spec['subdomains']}")

    if FAILURES:
        print(f"RESULT: FAIL ({len(FAILURES)} failure(s))")
        raise SystemExit(1)
    print("RESULT: PASS")


if __name__ == "__main__":
    main()