#!/usr/bin/env python3
"""S1-02B3 distribution report over the merged candidate file.

Reads S1_02B3_WORKFLOW_CANDIDATES.csv when present, otherwise the three
fragments. Prints the counts the batch report must carry.
"""
import csv
import sys
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MERGED = ROOT / "S1_02B3_WORKFLOW_CANDIDATES.csv"
FRAG = ROOT / "evidence" / "s1_02b3_research"

SUBDOMAIN_ORDER = [
    "animation_3d", "graphic_design", "audio_music",
    "aviation", "maritime_port", "fire_safety",
    "educational_technology", "library_info", "translation",
]


def load():
    if MERGED.is_file():
        with open(MERGED, encoding="utf-8") as f:
            return list(csv.DictReader(f)), "merged"
    rows = []
    for stem in ("vm_cluster", "ts_cluster", "edu_cluster"):
        p = FRAG / f"{stem}_candidates.csv"
        if p.is_file():
            with open(p, encoding="utf-8") as f:
                rows.extend(csv.DictReader(f))
    return rows, "fragments"


def main() -> int:
    rows, src = load()
    print(f"source={src} rows={len(rows)}")
    per = Counter(r["subdomain_code"] for r in rows)
    print("per_subdomain:", dict((k, per.get(k, 0)) for k in SUBDOMAIN_ORDER))
    for field in ("evidence_level", "evidence_kind", "source_support_mode",
                  "software_adaptation", "source_type", "source_category"):
        print(field + ":", dict(Counter(r[field] for r in rows)))
    print("linux_not_verified:", sum(
        1 for r in rows if r.get("linux_verification_state") == "NOT_VERIFIED"))
    print("process_incident_non_none:", sum(
        1 for r in rows if r.get("process_incident", "none") != "none"))
    e4 = [r for r in rows if r["evidence_level"] == "E4"]
    print(f"e4_count={len(e4)}")
    for r in e4:
        print("  E4", r["candidate_id"], "|", r["pending_confirmation"][:120])
    fam = Counter()
    for r in rows:
        for code in r.get("workflow_family_id", "").split(","):
            if code.strip():
                fam[code.strip()] += 1
    print("families:", dict(fam))
    return 0


if __name__ == "__main__":
    sys.exit(main())