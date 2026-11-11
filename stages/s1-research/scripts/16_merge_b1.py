#!/usr/bin/env python3
"""S1-02B1 U2/U7 — merge the four cluster research fragments into this round's
standalone deliverables.

This file is the SINGLE SOURCE OF TRUTH for the B1 candidate schema. The four
research children write fragment CSVs against FRAG_COLS; this script validates
every row against the schema and the evidence rules before writing anything,
then produces:

  S1_02B1_WORKFLOW_CANDIDATES.csv  (merged rows + derived flags)
  S1_02B1_SOURCE_CLAIM_MAP.csv     (the source->claim evidence view)

Rules encoded here (the S1-02A lessons as gates):
  P1  fragment headers must be exactly FRAG_COLS; only the 4 known fragments
      are accepted (each cluster file owns its rows: no shared write target).
  P2  candidate_id unique across all fragments and surface-form
      <id_slug>_wfNN where id_slug is fixed by subdomain_code.
  P3  every subdomain of the 13 must carry >=3 candidates (research
      completeness floor; an upper bound is left to source quality).
  P4  evidence enums: evidence_kind in the A 4-kind set; evidence_level in
      {E1,E2,E3,E4}; E4 <=> expert_pending_proposal (A's exact pairing).
  P5  never let a vendor/tool page support a full-workflow claim:
      industry_standard_complete forbids source_category in
      {vendor_doc, vendor_blog, government_tool_page} (the A downgrade trap).
  P6  software_adaptation in the A 5-state set; linux_verification_state is
      NOT written by children at all and is appended here as NOT_VERIFIED
      for every row (children cannot fabricate a verified state).
  P7  life_/med_ rows must carry all 4 ethics fields
      (data_usage_authorization, privacy_considerations, research_ethics,
      reproducibility_assessment); phys_ rows are exempt but reported.
  P8  derived flags match A's conventions: expert_pending="YES: E4: "+pending
      iff expert_pending_proposal; engineering_pending uses the A-standard
      phrase for partial/unverified/conditional adaptations (A flags all
      three; partial 15 + unverified 2 + conditional 4 = its 21 flagged rows).

Nothing is written unless every check passes (atomic merge).
"""
import csv, glob, os, re, sys
from collections import Counter, OrderedDict
from pathlib import Path

WS = "/Users/mac/Workspaces/ale-研究设计/ale-500-category-research"
FRAG_DIR = f"{WS}/evidence/s1_02b1_research"
OUT_WF = f"{WS}/S1_02B1_WORKFLOW_CANDIDATES.csv"
OUT_SC = f"{WS}/S1_02B1_SOURCE_CLAIM_MAP.csv"

# subdomain_code -> candidate id slug; the order is the canonical row order.
ID_SLUG = OrderedDict([
    ("physics", "phys_phys"), ("chemistry_materials", "phys_chem"),
    ("astronomy", "phys_astro"), ("earth_atmo", "phys_earth"),
    ("biomolecular", "life_biomol"), ("genomics", "life_genom"),
    ("cell_imaging", "life_cellimg"), ("systems_microbial", "life_sysmic"),
    ("clinical_diagnostics", "med_diag"), ("therapeutic_oncology", "med_onco"),
    ("clinical_informatics", "med_inform"), ("public_health", "med_pubhealth"),
    ("clinical_trials", "med_trials"),
])
CLUSTER_OF_FILE = {
    "phys_cluster_candidates": "physical_sciences",
    "life_cluster_candidates": "life_sciences",
    "med_a_candidates": "health_medicine",
    "med_b_candidates": "health_medicine",
}
CLUSTER_OF_SLUG = {
    "physics": "physical_sciences", "chemistry_materials": "physical_sciences",
    "astronomy": "physical_sciences", "earth_atmo": "physical_sciences",
    "biomolecular": "life_sciences", "genomics": "life_sciences",
    "cell_imaging": "life_sciences", "systems_microbial": "life_sciences",
    "clinical_diagnostics": "health_medicine",
    "therapeutic_oncology": "health_medicine",
    "clinical_informatics": "health_medicine", "public_health": "health_medicine",
    "clinical_trials": "health_medicine",
}
LIFE_HEALTH_PREFIXES = ("life_", "med_")

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
EVIDENCE_KINDS = {"industry_standard_complete", "tool_existence",
                  "agent_inferred_combination", "expert_pending_proposal"}
EVIDENCE_LEVELS = {"E1", "E2", "E3", "E4"}
ADAPTATIONS = {"native", "partial_function_replacement", "conditional",
               "unverified_or_unavailable", "needs_task_redesign"}
NO_STANDARD_CLAIM_FROM = {"vendor_doc", "vendor_blog", "government_tool_page"}
ETHICS_COLS = ["data_usage_authorization", "privacy_considerations",
               "research_ethics", "reproducibility_assessment"]

def err(msg):
    raise SystemExit("MERGE FAILED: " + msg)

def main():
    files = sorted(glob.glob(f"{FRAG_DIR}/*_candidates.csv"))
    known = set(CLUSTER_OF_FILE)
    got_stems = {Path(f).stem for f in files}
    unknown = got_stems - known
    if unknown:
        err(f"unexpected fragment file(s) {sorted(unknown)}; allowed={sorted(known)}")
    if not files:
        err("no fragment CSVs under evidence/s1_02b1_research/ "
            "(expected 4: phys/life/med_a/med_b cluster fragments)")

    rows = []
    for f in files:
        stem = Path(f).stem
        with open(f, encoding="utf-8") as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            if header != FRAG_COLS:
                err(f"{stem}: header mismatch. got {header}")
            for line in reader:
                if not any(cell.strip() for cell in line):
                    continue
                rows.append([stem] + line)

    errs = []
    ids = [r[1 + FRAG_COLS.index("candidate_id")] for r in rows]
    dup_ids = [i for i, n in Counter(ids).items() if n > 1]
    if dup_ids:
        errs.append(f"P2 duplicate candidate_id across fragments: {sorted(dup_ids)}")

    per_sub = Counter()
    for stem, *vals in rows:
        d = dict(zip(FRAG_COLS, vals))
        sid = d["candidate_id"]
        sub = d["subdomain_code"]
        per_sub[sub] += 1
        if sub not in ID_SLUG:
            errs.append(f"P2 {sid}: unknown subdomain_code {sub!r}")
            continue
        if not re.fullmatch(re.escape(ID_SLUG[sub]) + r"_wf\d{2}$", sid):
            errs.append(f"P2 {sid}: id must be {ID_SLUG[sub]}_wfNN")
        if CLUSTER_OF_SLUG[sub] != CLUSTER_OF_FILE[stem]:
            errs.append(f"P2 {sid}: subdomain {sub} belongs to "
                        f"{CLUSTER_OF_SLUG[sub]}, not fragment {stem}")
        if d["evidence_kind"] not in EVIDENCE_KINDS:
            errs.append(f"P4 {sid}: evidence_kind={d['evidence_kind']!r}")
        if d["evidence_level"] not in EVIDENCE_LEVELS:
            errs.append(f"P4 {sid}: evidence_level={d['evidence_level']!r}")
        if (d["evidence_kind"] == "expert_pending_proposal") != (d["evidence_level"] == "E4"):
            errs.append(f"P4 {sid}: E4 <-> expert_pending_proposal pairing violated")
        if (d["evidence_kind"] == "industry_standard_complete"
                and d["source_category"] in NO_STANDARD_CLAIM_FROM):
            errs.append(f"P5 {sid}: source_category={d['source_category']} cannot "
                        "support industry_standard_complete (tool page proves tool "
                        "existence, not standard practice)")
        if d["software_adaptation"] not in ADAPTATIONS:
            errs.append(f"P6 {sid}: software_adaptation={d['software_adaptation']!r}")
        if not d["primary_source_url"].startswith("http"):
            errs.append(f"P4 {sid}: primary_source_url={d['primary_source_url']!r}")
        if not d["primary_claim"].strip():
            errs.append(f"P4 {sid}: primary_claim empty")
        if not d["source_category"].strip():
            errs.append(f"P4 {sid}: source_category empty")
        if d["source_type"] not in {"industry_supported", "project_proposal"}:
            errs.append(f"P4 {sid}: source_type={d['source_type']!r}")
        if d["evidence_level"] == "E2":
            errs.append(f"P4 {sid}: E2 forbidden by research brief")
        if d["evidence_kind"] == "expert_pending_proposal" and d["source_type"] == "industry_supported":
            errs.append(f"P4 {sid}: E4 row must not be industry_supported")
        if d["evidence_level"] == "E1" and d["source_type"] == "project_proposal":
            errs.append(f"P4 {sid}: E1 row must not be project_proposal")
        if sid.startswith(LIFE_HEALTH_PREFIXES):
            for e in ETHICS_COLS:
                if not d[e].strip():
                    errs.append(f"P7 {sid}: ethics field {e} empty (life/health row)")

    for sub in ID_SLUG:
        n = per_sub.get(sub, 0)
        if n < 3:
            errs.append(f"P3 subdomain {sub}: only {n} candidates (floor is 3)")

    if errs:
        for e in sorted(set(errs)):
            print(e)
        err(f"{len(errs)} schema/rule violation(s)")

    order = {sub: i for i, sub in enumerate(ID_SLUG)}
    rows.sort(key=lambda r: (order[r[1 + FRAG_COLS.index('subdomain_code')]],
                             r[1 + FRAG_COLS.index('candidate_id')]))

    wf_rows, sc_rows = [], []
    for stem, *vals in rows:
        d = dict(zip(FRAG_COLS, vals))
        sid = d["candidate_id"]
        expert = ("YES: E4: " + d["pending_confirmation"]) if d["evidence_kind"] == "expert_pending_proposal" else ""
        eng = {
            "partial_function_replacement": "YES: open-source substitute covers part of the "
                "proprietary tool; functional equivalence NOT verified",
            "unverified_or_unavailable": "YES: no verified open-source equivalent; "
                "engineering run NOT verified",
            "conditional": "YES: tool runs only under a condition (Windows GUI, third-party "
                "container, or registration); Linux path NOT verified",
        }.get(d["software_adaptation"], "")
        wf_rows.append(vals + ["NOT_VERIFIED", expert, eng, stem])
        sc_rows.append([sid, d["subdomain_code"], d["workflow_title"],
                        d["primary_source_url"], d["source_category"],
                        d["evidence_kind"], d["evidence_level"], d["source_type"],
                        d["software_adaptation"], ""])

    with open(OUT_WF, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(FRAG_COLS + ["linux_verification_state", "expert_pending",
                                "engineering_pending", "fragment_path"])
        w.writerows(wf_rows)
    with open(OUT_SC, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["candidate_id", "subdomain_code", "workflow_title",
                    "source_url", "source_category", "evidence_kind",
                    "evidence_level", "source_type", "software_adaptation",
                    "correction_note"])
        w.writerows(sc_rows)

    print(f"merged rows: {len(wf_rows)}")
    print("per-subdomain:", dict(per_sub))
    kids, levels, adapts = Counter(), Counter(), Counter()
    ethics_done = ethics_total = 0
    for stem, *vals in rows:
        d = dict(zip(FRAG_COLS, vals))
        kids[d["evidence_kind"]] += 1
        levels[d["evidence_level"]] += 1
        adapts[d["software_adaptation"]] += 1
        if d["candidate_id"].startswith(LIFE_HEALTH_PREFIXES):
            ethics_total += 1
            ethics_done += all(d[e].strip() for e in ETHICS_COLS)
    print("evidence_kind:", dict(kids))
    print("evidence_level:", dict(levels))
    print("software_adaptation:", dict(adapts))
    print(f"life/health ethics coverage: {ethics_done}/{ethics_total}")
    print(f"wrote {OUT_WF}")
    print(f"wrote {OUT_SC}")

if __name__ == "__main__":
    exit(main())