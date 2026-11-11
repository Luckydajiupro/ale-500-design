#!/usr/bin/env python3
"""S1-02B2 overlap sweep (T6 evidence) — title-token Jaccard across batches.

Read-only. Compares S1_02B2 candidates against the 51 S1-02A effective rows and
the 57 S1-02B1 rows, plus intra-B2 cross-subdomain pairs. A pair is flagged
when the title token Jaccard >= THRESHOLD (B1 precedent: 0.35). The sweep is
only evidence for the human-written S1_02B2_OVERLAP_AND_RISKS.md; it does not
adjudicate. Writes .audit/b2_overlap_sweep.csv.

Usage: python3 scripts/25_b2_overlap.py
Exit 0 iff the sweep ran (missing inputs are an error only for A/B1 frozen
files; a missing B2 workflow file is reported and the run exits 1).
"""
import csv, re, sys
from collections import Counter

WS = "/Users/mac/Workspaces/ale-研究设计/ale-500-category-research"
WF = f"{WS}/S1_02B2_WORKFLOW_CANDIDATES.csv"
A = f"{WS}/S1_02A_EFFECTIVE_CANDIDATES.csv"
B1 = f"{WS}/S1_02B1_WORKFLOW_CANDIDATES.csv"
OUT = f"{WS}/.audit/b2_overlap_sweep.csv"
THRESHOLD = 0.35

TOKEN = re.compile(r"[a-z0-9\u4e00-\u9fff]+")

def tokens(title):
    return set(TOKEN.findall(title.lower()))

def jaccard(x, y):
    if not x or not y:
        return 0.0
    return len(x & y) / len(x | y)

def load(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    for p in (A, B1):
        try:
            load(p)
        except FileNotFoundError:
            raise SystemExit(f"missing frozen input {p}")
    try:
        wf = load(WF)
    except FileNotFoundError:
        raise SystemExit("missing S1_02B2_WORKFLOW_CANDIDATES.csv; "
                         "run scripts/23_merge_b2.py first")
    a, b1 = load(A), load(B1)

    pairs = []
    for rows, kind in ((a, "B2xA"), (b1, "B2xB1")):
        for y in wf:
            ty = tokens(y["workflow_title"])
            for x in rows:
                j = jaccard(tokens(x["workflow_title"]), ty)
                if j >= THRESHOLD:
                    pairs.append({
                        "kind": kind,
                        "id_a": x["candidate_id"], "sub_a": x["subdomain_code"],
                        "title_a": x["workflow_title"],
                        "id_b": y["candidate_id"], "sub_b": y["subdomain_code"],
                        "title_b": y["workflow_title"],
                        "jaccard": f"{j:.3f}",
                        "shared": " ".join(sorted(
                            tokens(x["workflow_title"]) & ty))})
    for i, y in enumerate(wf):
        for x in wf[i + 1:]:
            if x["subdomain_code"] == y["subdomain_code"]:
                continue
            j = jaccard(tokens(x["workflow_title"]), tokens(y["workflow_title"]))
            if j >= THRESHOLD:
                pairs.append({
                    "kind": "B2xB2",
                    "id_a": x["candidate_id"], "sub_a": x["subdomain_code"],
                    "title_a": x["workflow_title"],
                    "id_b": y["candidate_id"], "sub_b": y["subdomain_code"],
                    "title_b": y["workflow_title"],
                    "jaccard": f"{j:.3f}",
                    "shared": " ".join(sorted(
                        tokens(x["workflow_title"]) & tokens(y["workflow_title"])))})

    cols = ["kind", "id_a", "sub_a", "title_a", "id_b", "sub_b", "title_b",
            "jaccard", "shared"]
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(pairs)
    by_kind = Counter(p["kind"] for p in pairs)
    print(f"flagged {len(pairs)} pairs above Jaccard {THRESHOLD}: "
          f"{dict(by_kind)}")
    for p in sorted(pairs, key=lambda r: -float(r["jaccard"]))[:40]:
        print(f"  {p['jaccard']} {p['kind']} {p['id_a']}({p['sub_a']}) "
              f"`{p['title_a']}` <-> {p['id_b']}({p['sub_b']}) "
              f"`{p['title_b']}` shared={p['shared'][:60]}")
    print(f"wrote {OUT}")
    return 0

if __name__ == "__main__":
    sys.exit(main())