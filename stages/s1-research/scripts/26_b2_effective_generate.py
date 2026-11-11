#!/usr/bin/env python3
"""S1-02B2 effective-view generator.

Reads the frozen S1_02B2_WORKFLOW_CANDIDATES.csv (39 rows, 39 cols) and the
corrections spec scripts/b2_effective_corrections_spec.json, and writes
S1_02B2_EFFECTIVE_CANDIDATES.csv with all 39 original columns byte-identical
plus four appended columns (source_support_mode, evidence_scope,
workflow_family_id, process_incident).  The frozen CSV is opened read-only;
nothing else is touched.  Atomic write via temp file + os.replace.
"""
import csv, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF_IN = os.path.join(ROOT, "S1_02B2_WORKFLOW_CANDIDATES.csv")
SPEC_IN = os.path.join(ROOT, "scripts", "b2_effective_corrections_spec.json")
OUT = os.path.join(ROOT, "S1_02B2_EFFECTIVE_CANDIDATES.csv")

NEW_COLS = ["source_support_mode", "evidence_scope", "workflow_family_id", "process_incident"]
DEFAULT_SCOPE = "whole_workflow=as_recorded"


def load_wf():
    with open(WF_IN, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, "frozen WF csv is empty"
    header = list(rows[0].keys())
    # no field loss: read exactly 39 columns
    assert len(header) == 39, f"expected 39 cols, got {len(header)}"
    return header, rows


def main():
    header, rows = load_wf()
    with open(SPEC_IN, encoding="utf-8") as f:
        spec = json.load(f)

    corrections = spec["corrections"]
    extended = spec.get("process_incidents_extended", {})

    out_rows = []
    for r in rows:
        cid = r["candidate_id"]
        corr = corrections.get(cid)
        if corr is not None:
            sm = corr["source_support_mode"]
            esc = corr["evidence_scope"]
            fam = corr["workflow_family_id"]
            inc = corr["process_incident"]
        else:
            # evidence-support state, never a copy of software_adaptation
            by_level = spec["meta"]["uncorrected_mode_by_evidence_level"]
            lvl = r["evidence_level"]
            assert lvl in by_level, f"{cid} unexpected evidence_level {lvl!r}"
            sm = by_level[lvl]
            esc = DEFAULT_SCOPE
            fam = ""
            inc = extended.get(cid, "none")
        new = dict(r)
        # original columns stay byte-identical; append new columns in order
        new["source_support_mode"] = sm
        new["evidence_scope"] = esc
        new["workflow_family_id"] = fam
        new["process_incident"] = inc
        out_rows.append(new)

    assert len(out_rows) == 39, f"expected 39 rows, got {len(out_rows)}"
    out_header = header + NEW_COLS

    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_header)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    os.replace(tmp, OUT)
    print(f"wrote {OUT}: 39 rows x {len(out_header)} cols")
    return 0


if __name__ == "__main__":
    sys.exit(main())