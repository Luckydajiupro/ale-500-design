#!/usr/bin/env python3
"""S1-02B1 U8 — annotate S1_02B1_WORKFLOW_CANDIDATES.csv with the A-style
duplicate columns, derived from S1_02B1_DUPLICATE_ATTRIBUTION.csv.

The attribution CSV is the adjudication source of truth. Rules:
- a 'yes' pair (substantively_duplicate=yes) marks its B1-side candidate
  duplicate_status='secondary' and copies its secondary_tag cell from the
  attribution row; the primary counterpart is the other id in the pair.
  S1-02A rows are the prior baseline, so a B1 row can never be 'primary' in a
  cross-round pair and no A file is touched;
- every other row gets duplicate_status='none', primary_home='', secondary_tag=''.

Idempotent: re-running reproduces the identical file from the attribution CSV.
"""
import csv, sys

WS = "/Users/mac/Workspaces/ale-研究设计/ale-500-category-research"
WF_PATH = f"{WS}/S1_02B1_WORKFLOW_CANDIDATES.csv"
DUP_PATH = f"{WS}/S1_02B1_DUPLICATE_ATTRIBUTION.csv"
ANNO_COLS = ["duplicate_status", "primary_home", "secondary_tag"]

def main():
    with open(WF_PATH, encoding="utf-8") as f:
        wf = list(csv.DictReader(f))
    if set(ANNO_COLS) <= set(wf[0].keys()):
        print("WF already annotated; recomputing from the attribution CSV (idempotent).")
        wf = [{k: r[k] for k in r if k not in ANNO_COLS} for r in wf]
    with open(DUP_PATH, encoding="utf-8") as f:
        dup = list(csv.DictReader(f))

    sec_tag = {}
    for d in dup:
        if d["substantively_duplicate"] != "yes":
            continue
        ids = d["pair"].split("|")
        b1_ids = [i for i in ids if i.startswith(("phys_", "life_", "med_"))]
        if len(b1_ids) != 1:
            raise SystemExit(f"U8 ERROR: pair {d['pair']} must have exactly one B1-side id")
        sec_tag[b1_ids[0]] = f"secondary of {[i for i in ids if i not in b1_ids][0]}: " \
                             f"{d['secondary_tag']}"

    for r in wf:
        sid = r["candidate_id"]
        r["duplicate_status"] = "secondary" if sid in sec_tag else "none"
        r["primary_home"] = ""
        r["secondary_tag"] = sec_tag.get(sid, "")

    header = list(wf[0].keys())
    with open(WF_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        w.writerows(wf)
    marked = [r["candidate_id"] for r in wf if r["duplicate_status"] == "secondary"]
    print(f"annotated {len(wf)} rows: "
          f"secondary={len(marked)} ({marked}) none={len(wf) - len(marked)}")
    print(f"wrote {WF_PATH}")

if __name__ == "__main__":
    main()