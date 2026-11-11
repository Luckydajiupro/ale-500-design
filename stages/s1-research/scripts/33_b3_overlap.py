#!/usr/bin/env python3
"""S1-02B3 overlap sweep (T6 evidence) — title-token Jaccard across batches.

Read-only against frozen inputs. Compares S1_02B3 merged candidates against
S1-02A effective (51), S1-02B1 (57), and S1-02B2 effective (39), plus
intra-B3 cross-subdomain pairs. A pair is flagged when the title token
Jaccard >= THRESHOLD (B1 precedent 0.35). The sweep is evidence only for the
human-written S1_02B3_OVERLAP_AND_RISKS.md and S1_02B3_DUPLICATE_ATTRIBUTION.csv;
it does not adjudicate. Writes .audit/b3_overlap_sweep.csv (refuses to
overwrite — delete it to re-sweep).

Usage: python3 scripts/33_b3_overlap.py [--selftest]
Exit 0 iff the sweep ran.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / "S1_02B3_WORKFLOW_CANDIDATES.csv"
A = ROOT / "S1_02A_EFFECTIVE_CANDIDATES.csv"
B1 = ROOT / "S1_02B1_WORKFLOW_CANDIDATES.csv"
B2E = ROOT / "S1_02B2_EFFECTIVE_CANDIDATES.csv"
OUT = ROOT / ".audit" / "b3_overlap_sweep.csv"
THRESHOLD = 0.35
COLS = ["kind", "id_a", "sub_a", "title_a", "id_b", "sub_b", "title_b",
        "jaccard", "shared"]

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


def sweep(b3_rows, prior_sets):
    """prior_sets: dict kind -> list of prior rows. Returns flagged pairs."""
    pairs = []
    for kind, rows in prior_sets:
        for y in b3_rows:
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
                        "shared": " ".join(sorted(tokens(x["workflow_title"]) & ty))})
    for i, y in enumerate(b3_rows):
        for x in b3_rows[i + 1:]:
            if x["subdomain_code"] == y["subdomain_code"]:
                continue
            sx = tokens(x["workflow_title"])
            sy = tokens(y["workflow_title"])
            j = jaccard(sx, sy)
            if j >= THRESHOLD:
                pairs.append({
                    "kind": "b3-internal",
                    "id_a": x["candidate_id"], "sub_a": x["subdomain_code"],
                    "title_a": x["workflow_title"],
                    "id_b": y["candidate_id"], "sub_b": y["subdomain_code"],
                    "title_b": y["workflow_title"],
                    "jaccard": f"{j:.3f}",
                    "shared": " ".join(sorted(sx & sy))})
    return pairs


def write_sweep(pairs, out):
    if out.exists():
        raise SystemExit(f"refusing to overwrite {out}; delete it to re-sweep")
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(pairs)


def main():
    for p in (A, B1, B2E):
        if not p.is_file():
            raise SystemExit(f"missing frozen input {p}")
    if not WF.is_file():
        raise SystemExit("missing S1_02B3_WORKFLOW_CANDIDATES.csv; "
                         "run scripts/31_merge_b3.py first")
    b3 = load(WF)
    prior_sets = [("b3xA", load(A)), ("b3xB1", load(B1)), ("b3xB2E", load(B2E))]
    pairs = sweep(b3, prior_sets)
    write_sweep(pairs, OUT)
    by_kind = {}
    for p in pairs:
        by_kind[p["kind"]] = by_kind.get(p["kind"], 0) + 1
    print(f"flagged {len(pairs)} pairs above Jaccard {THRESHOLD}: {by_kind}")
    for p in sorted(pairs, key=lambda r: -float(r["jaccard"]))[:40]:
        print(f"  {p['jaccard']} {p['kind']} {p['id_a']}({p['sub_a']}) "
              f"`{p['title_a']}` <-> {p['id_b']}({p['sub_b']}) "
              f"`{p['title_b']}` shared={p['shared'][:60]}")
    print(f"wrote {OUT}")
    return 0


def selftest():
    import tempfile

    def row(cid, sub, title):
        return {"candidate_id": cid, "subdomain_code": sub,
                "workflow_title": title}

    b3 = [row("vm_anim_wf01", "animation_3d", "3d model flight"),
          row("vm_gra_wf01", "graphic_design", "3d model render"),
          row("ts_avi_wf01", "aviation", "airport wildlife risk plan")]
    prior = {"b3xA": [row("eng_urban_wf01", "urban_planning", "3d city model")]}

    assert jaccard(tokens("3d model flight"), tokens("3d model render")) == 0.5
    print("probe OK jaccard-basic")
    assert jaccard(set(), tokens("x")) == 0.0
    print("probe OK jaccard-empty")

    got = sweep(b3, list(prior.items()))
    # pairs above threshold: prior 3d city model vs 3d model flight -> 2/4=0.5
    # vs 3d model render -> 2/4=0.5 ; internal 3d model flight vs 3d model
    # render (cross-subdomain) -> 0.5
    assert len(got) == 3, got
    print("probe OK sweep-count")
    kinds = {p["kind"] for p in got}
    assert kinds == {"b3xA", "b3-internal"}, kinds
    print("probe OK sweep-kinds")
    assert all(set(p) == set(COLS) for p in got)
    print("probe OK sweep-cols")

    # same-subdomain internal pair must be skipped
    b3_same = [row("ts_avi_wf01", "aviation", "3d model flight"),
               row("ts_avi_wf02", "aviation", "3d model render")]
    assert sweep(b3_same, []) == []
    print("probe OK internal-same-subdomain-skipped")

    # below threshold is not flagged
    lo = [row("vm_anim_wf01", "animation_3d", "alpha beta gamma"),
          row("ts_avi_wf01", "aviation", "delta epsilon zeta")]
    assert sweep(lo, []) == []
    print("probe OK below-threshold-clean")

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "sweep.csv"
        write_sweep(got, out)
        assert out.exists()
        rows = load(out)
        assert [set(r) for r in rows] == [set(COLS)] * 3
        print("probe OK write-sweep")
        try:
            write_sweep(got, out)
        except SystemExit as e:
            assert "refusing to overwrite" in str(e)
            print("probe OK refuse-overwrite")
        else:
            raise AssertionError("overwrite not refused")

    print("selftest: 9 probes green")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="S1-02B3 overlap sweep")
    ap.add_argument("--selftest", action="store_true",
                    help="run in-memory self-tests")
    args = ap.parse_args()
    sys.exit(selftest() if args.selftest else main())