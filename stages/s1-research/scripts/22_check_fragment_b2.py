#!/usr/bin/env python3
"""Per-fragment contract checker for S1-02B2.

Usage: python3 scripts/22_check_fragment_b2.py <stem>
  stem in {psy_cluster, biz_a, biz_b1, biz_b2, soc}

Checks the fragment CSV + JSON written by one B2 research child against the
S1-02B2 schema contract before the merge. Exit 0 = PASS, exit 1 = FAIL.

B2 contract differences from B1 (see trail .audit/s1-02b2.tsv, contract row):
  - all 4 clusters require the 4 ethics fields on every row (user §4 covers
    human subjects, enterprise data and survey data; there is no exempt
    physical-sciences cluster in B2);
  - P3 floor per subdomain is 1 hard (a subdomain may legally carry fewer than
    3 candidates where evidence is weak, per user §3; 3 is the documented
    expectation, not a hard gate — padding and trivial official-task variants
    stay forbidden).
"""

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
FRAG_DIR = WS / "evidence" / "s1_02b2_research"

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
MIN_ROWS_PER_SUBDOMAIN = 1   # B2 hard floor (user §3 allows <3 with evidence)
TARGET_ROWS_PER_SUBDOMAIN = 3

CLUSTERS = {
    "psy_cluster": {
        "subdomains": ["comp_neuro", "exp_psychology"],
        "slugs": {"comp_neuro": "psy_comp", "exp_psychology": "psy_exp"},
    },
    "biz_a": {
        "subdomains": ["accounting", "actuarial_risk",
                       "enterprise_analytics", "compliance"],
        "slugs": {"accounting": "biz_acc", "actuarial_risk": "biz_act",
                  "enterprise_analytics": "biz_ana", "compliance": "biz_cmp"},
    },
    "biz_b1": {
        "subdomains": ["hr_pm", "sales_marketing"],
        "slugs": {"hr_pm": "biz_hr", "sales_marketing": "biz_mkt"},
    },
    "biz_b2": {
        "subdomains": ["quant_finance", "supply_chain"],
        "slugs": {"quant_finance": "biz_quant", "supply_chain": "biz_sup"},
    },
    "soc": {
        "subdomains": ["economics"],
        "slugs": {"economics": "soc_econ"},
    },
}

FAILURES = []


def fail(msg):
    FAILURES.append(msg)
    print("  FAIL " + msg)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in CLUSTERS:
        raise SystemExit("usage: 22_check_fragment_b2.py "
                         "<psy_cluster|biz_a|biz_b1|biz_b2|soc>")
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
    if len(rows) < sum(
            MIN_ROWS_PER_SUBDOMAIN for _ in spec["subdomains"]):
        fail(f"row floor: expected >= {len(spec['subdomains'])} (one per "
             f"subdomain), got {len(rows)}")
    print(f"  rows={len(rows)}")

    counts = Counter(r["subdomain_code"] for r in rows)
    for sub in spec["subdomains"]:
        n = counts.get(sub, 0)
        if n < MIN_ROWS_PER_SUBDOMAIN:
            fail(f"{sub}: only {n} candidates, hard floor is "
                 f"{MIN_ROWS_PER_SUBDOMAIN}")
        elif n < TARGET_ROWS_PER_SUBDOMAIN:
            print(f"  {sub}={n} (below the 3-row expectation; shortage must "
                  "be justified in the fragment's own summary)")
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
        sid = r["candidate_id"]
        if r["evidence_kind"] not in EVIDENCE_KINDS:
            fail(f"{sid}: bad evidence_kind {r['evidence_kind']}")
        if r["evidence_level"] not in EVIDENCE_LEVELS:
            fail(f"{sid}: bad evidence_level {r['evidence_level']}")
        if r["evidence_level"] == "E2":
            fail(f"{sid}: E2 forbidden by child brief")
        if (r["evidence_kind"] == "expert_pending_proposal") != \
                (r["evidence_level"] == "E4"):
            fail(f"{sid}: E4 <-> expert_pending_proposal "
                 f"mismatch ({r['evidence_kind']}/{r['evidence_level']})")
        if r["evidence_kind"] == "industry_standard_complete" and \
                r["source_category"] in NO_STANDARD_CLAIM_FROM:
            fail(f"{sid}: industry_standard_complete backed by "
                 f"weak source category {r['source_category']}")
        if r["evidence_level"] == "E4" and r["source_type"] == SLA:
            fail(f"{sid}: E4 must not be {SLA}")
        if r["evidence_level"] == "E1" and r["source_type"] == PP:
            fail(f"{sid}: E1 must not be {PP}")
        if r["source_type"] not in {SLA, PP}:
            fail(f"{sid}: bad source_type {r['source_type']}")
        if r["software_adaptation"] not in ADAPTATIONS:
            fail(f"{sid}: bad software_adaptation {r['software_adaptation']}")
        non_empty = [c for c in FRAG_COLS
                     if c not in ETHICS_COLS and not r[c].strip()]
        if non_empty:
            fail(f"{sid}: empty non-ethics field(s) {','.join(non_empty)}")
        empty_ethics = [c for c in ETHICS_COLS if not r[c].strip()]
        if empty_ethics:
            fail(f"{sid}: B2 requires all 4 ethics fields filled, empty "
                 f"{','.join(empty_ethics)}")

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