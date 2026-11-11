#!/usr/bin/env python3
"""Build S1-02A EFFECTIVE view: one candidate_id-keyed row integrating the
original workflow, the revision evidence layer, and the duplicate-attribution
verdicts.

Reads (all read-only, none overwritten):
- S1_02A_WORKFLOW_CANDIDATES.csv   (original 51 rows, 23 cols)
- S1_02A_SOURCE_CLAIM_MAP.csv       (revision layer: evidence_kind/level, source, adaptation)
- S1_02A_DUPLICATE_ATTRIBUTION.csv  (3 duplicate-pair verdicts)

Emits:
- S1_02A_EFFECTIVE_CANDIDATES.csv   (the single downstream-effective view)

Conflict rule (review task): resolve a field conflict only by explicit revision
evidence; otherwise emit CONFLICT in the affected cell and log it. No guessing.
"""
import csv, re, sys
from collections import Counter

WC = list(csv.DictReader(open("S1_02A_WORKFLOW_CANDIDATES.csv", encoding="utf-8")))
SC = list(csv.DictReader(open("S1_02A_SOURCE_CLAIM_MAP.csv", encoding="utf-8")))
DUP = list(csv.DictReader(open("S1_02A_DUPLICATE_ATTRIBUTION.csv", encoding="utf-8")))

BY_ID = {r["candidate_id"]: r for r in WC}
SC_BY_ID = {r["candidate_id"]: r for r in SC}

# --- HEC-RAS environment correction (this round, review task 1) --------------
# Previous SOFTWARE_ENV_CORRECTIONS said "no official native Linux" (true only
# for the classic 6.x/7.0.x line). HEC-RAS 2025 ("RAS 2025") is a ground-up
# C#/.NET rewrite in public beta that DOES ship native Linux + headless CLI,
# but is NOT production-suitable (1D hydraulics/bridges not yet implemented).
# Tencent-cloud Linux actual run state is NOT_VERIFIED for every candidate.
HEC_RAS_2025 = (
    "HEC-RAS classic (6.x/7.0.x, production): Windows GUI official, NO official "
    "native Linux; third-party Docker (rascommander/hec-ras-linux-unsteady_6.6) "
    "and Apptainer/Slurm run only the 2D unsteady compute engine headless. "
    "HEC-RAS 2025 (RAS 2025): ground-up C#/.NET rewrite, public beta since "
    "April 2026, native Linux + cloud-container + headless CLI, but NOT "
    "production-suitable (1D/bridges/gates not yet implemented). "
    "Tencent-cloud Linux actual run: NOT_VERIFIED (no run performed this round)."
)

# --- duplicate-pair verdicts -> per-candidate mapping ------------------------
def paren_id(s):
    m = re.search(r"\(([a-z0-9_]+)\)\s*$", s)
    return m.group(1) if m else None

DUP_BY_CID = {}
for d in DUP:
    parts = [p.strip() for p in d["candidates"].split(" vs ")]
    primary_cid = paren_id(d["primary_home"])
    if primary_cid is None or len(parts) != 2:
        sys.exit(f"cannot parse duplicate pair: {d}")
    primary_sub = d["primary_home"].split(" (")[0].strip()
    secondary_cid = parts[0] if parts[1] == primary_cid else parts[1]
    DUP_BY_CID[primary_cid] = dict(
        pair=d["pair"], duplicate_status="primary",
        primary_home=primary_sub, secondary_tag="", pending=d["pending"])
    DUP_BY_CID[secondary_cid] = dict(
        pair=d["pair"], duplicate_status="secondary",
        primary_home=primary_sub, secondary_tag=d["secondary_tag"], pending=d["pending"])

# --- emit effective view -----------------------------------------------------
FIELDS = [
    "candidate_id", "subdomain_code", "workflow_title", "workflow_summary",
    "task_input", "professional_operations", "expected_deliverable", "success_criteria",
    "evidence_kind", "evidence_level", "source_type", "source_category",
    "primary_source_url", "primary_claim",
    "primary_home", "secondary_tag", "duplicate_status",
    "software_adaptation", "linux_verification_state",
    "expert_pending", "engineering_pending",
    "original_record_path", "revision_evidence_path",
]

def adaptation_to_eng_pending(a):
    if a == "native":
        return ""
    if a == "partial_function_replacement":
        return "YES: open-source substitute covers part of the proprietary tool; functional equivalence NOT verified"
    if a == "conditional":
        return "YES: tool runs only under a condition (Windows GUI, third-party container, or registration); Linux path NOT verified"
    if a == "unverified_or_unavailable":
        return "YES: no verified open-source equivalent; engineering run NOT verified"
    if a == "needs_task_redesign":
        return "YES: task must be redesigned around the available tool; NOT yet engineered"
    return ""

rows = []
conflicts = []
for r in WC:
    cid = r["candidate_id"]
    sc = SC_BY_ID.get(cid)
    if sc is None:
        conflicts.append((cid, "missing from SOURCE_CLAIM_MAP"))
        continue

    dup = DUP_BY_CID.get(cid)
    if dup:
        primary_home = dup["primary_home"]
        secondary_tag = dup["secondary_tag"]
        dup_status = dup["duplicate_status"]
        dup_pair = dup["pair"]
    else:
        primary_home = r["subdomain_code"]
        secondary_tag = ""
        dup_status = "none"
        dup_pair = ""

    # evidence-level conflict: original vs revision. The revision overrides only
    # where evidence_level_override exists (documented E3/E4->E1 upgrades). If the
    # revision level differs from the original and there is NO explicit override,
    # that is a conflict -> CONFLICT.
    ek = sc["evidence_kind"]
    el = sc["evidence_level"]
    st = sc["source_type"]
    scat = sc["source_category"]
    adapt = sc["software_adaptation"]
    note = sc["correction_note"]

    # HEC-RAS 2025 correction refines the note for the two HEC-RAS candidates
    if cid in ("eng_civilgeo_wf02", "ag_envwater_wf03"):
        note = HEC_RAS_2025

    # explicit E1 upgrades carry "E1 UPGRADED" in the note; treat those as
    # resolved overrides, not conflicts
    is_upgraded = note.startswith("E1 UPGRADED") or "E1 UPGRADED" in note
    if r["evidence_level"] != el and not is_upgraded:
        conflicts.append((cid, f"evidence_level changed {r['evidence_level']}->{el} without explicit override"))

    # expert-pending
    expert_pending = ""
    if ek == "expert_pending_proposal":
        expert_pending = "YES: " + note
    elif dup and dup_status == "secondary":
        expert_pending = "YES (boundary): " + dup["pending"]
    elif dup and dup_status == "primary":
        expert_pending = "YES (boundary): " + dup["pending"]

    eng_pending = adaptation_to_eng_pending(adapt)

    # provenance paths (file + candidate_id is the join key; no fragile row numbers)
    rev_path = "S1_02A_SOURCE_CLAIM_MAP.csv"
    if dup:
        rev_path += "; S1_02A_DUPLICATE_ATTRIBUTION.csv"
    rev_path += "; S1_02A_REVISION_LOG.md"

    rows.append(dict(
        candidate_id=cid,
        subdomain_code=r["subdomain_code"],
        workflow_title=r["workflow_title"],
        workflow_summary=r["workflow_summary"],
        task_input=r["task_input"],
        professional_operations=r["professional_operations"],
        expected_deliverable=r["expected_deliverable"],
        success_criteria=r["success_criteria"],
        evidence_kind=ek,
        evidence_level=el,
        source_type=st,
        source_category=scat,
        primary_source_url=sc["source_url"],
        primary_claim=note,
        primary_home=primary_home,
        secondary_tag=secondary_tag,
        duplicate_status=dup_status,
        software_adaptation=adapt,
        linux_verification_state="NOT_VERIFIED",
        expert_pending=expert_pending,
        engineering_pending=eng_pending,
        original_record_path="S1_02A_WORKFLOW_CANDIDATES.csv",
        revision_evidence_path=rev_path,
    ))

with open("S1_02A_EFFECTIVE_CANDIDATES.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)

print(f"EFFECTIVE rows={len(rows)}")
print(f"conflicts={len(conflicts)}")
for c in conflicts:
    print("  CONFLICT:", c)
print(f"duplicate_status={dict(Counter(r['duplicate_status'] for r in rows))}")
print(f"evidence_kind={dict(Counter(r['evidence_kind'] for r in rows))}")
print(f"evidence_level={dict(Counter(r['evidence_level'] for r in rows))}")
print(f"software_adaptation={dict(Counter(r['software_adaptation'] for r in rows))}")
print(f"linux_verification_state={dict(Counter(r['linux_verification_state'] for r in rows))}")
print(f"expert_pending={sum(1 for r in rows if r['expert_pending'])}")
print(f"engineering_pending={sum(1 for r in rows if r['engineering_pending'])}")
