#!/usr/bin/env python3
"""S1-02B3 scope matrix generator.

Inputs (all read-only):
  S1_01_CATEGORY_MAPPING.csv         official names, coverage, reclass info
  evidence/task_archetype_rows.tsv   official example task ids
  evidence/s1_02b3_research/<stem>_candidates.csv   row counts per subdomain
Output: S1_02B3_SCOPE_MATRIX.csv (refuses to overwrite an existing file).
Writes nothing else. No model calls. Subdomain ids are read from S1-01 only.

The output header mirrors S1_02B2_SCOPE_MATRIX.csv with s1_02b2_batch
renamed s1_02b3_batch (value batch_3). Notes carry the S1-01 dispute and
reclassification fields verbatim.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
OUT_PATH = ROOT / "S1_02B3_SCOPE_MATRIX.csv"

SCOPE_HDR = [
    "cohort",
    "cluster_code",
    "cluster_name",
    "subdomain_id",
    "subdomain_code",
    "subdomain_name",
    "coverage_status",
    "active_taxonomy_count",
    "official_example_task_ids",
    "s1_02b3_batch",
    "candidate_workflow_count",
    "ab_A_status",
    "ab_B_status",
    "ab_dispute",
    "notes",
]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(
        name, SCRIPT_DIR / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_28 = _load("28_b3_precheck")


def load_archetypes() -> dict[tuple[str, str], list[str]]:
    path = ROOT / "evidence" / "task_archetype_rows.tsv"
    out: dict[tuple[str, str], list[str]] = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            key = (row["domain_code"], row["subdomain_code"])
            out.setdefault(key, []).append(row["task_id"])
    return out


def candidate_counts() -> dict[str, int]:
    counts = {code: 0 for _sid, code, _name in _28.B3_TARGETS}
    frag_dir = ROOT / "evidence" / "s1_02b3_research"
    for stem in ("vm_cluster", "ts_cluster", "edu_cluster"):
        path = frag_dir / f"{stem}_candidates.csv"
        if not path.exists():
            continue
        with open(path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                code = row["subdomain_code"]
                counts[code] = counts.get(code, 0) + 1
    return counts


def build_rows(s1_rows: list[dict[str, str]],
               arche: dict[tuple[str, str], list[str]],
               counts: dict[str, int]) -> list[list[str]]:
    by = {(r["subdomain_id"], r["subdomain_code"]): r for r in s1_rows}
    by_domain = {}
    for r in s1_rows:
        by_domain.setdefault(r["domain_id"], r)
    out = []
    for sid, code, name in _28.B3_TARGETS:
        r = by.get((sid, code))
        if r is None:
            raise ValueError(f"S1-01 missing target subdomain {sid} {code}")
        if r["subdomain_name"] != name:
            raise ValueError(
                f"S1-01 name drift for {sid} {code}: {r['subdomain_name']!r}"
            )
        domain_id = sid.split(".")[0]
        if domain_id not in _28.B3_DOMAINS:
            raise ValueError(f"target {sid} maps to domain outside B3 set")
        dom = by_domain.get(domain_id, {})
        cluster_code = dom.get("domain_code", "")
        cluster_name = dom.get("official_domain_name", "")
        examples = ";".join(sorted(arche.get((cluster_code, code), [])))
        note = f"s1-01 dispute: {r.get('mapping_dispute', '')}"
        if r.get("reclassified_in"):
            note += f"; reclassified-in: {r['reclassified_in']}"
        if r.get("reclassified_out"):
            note += f"; reclassified-out: {r['reclassified_out']}"
        out.append([
            "formal_non_cs",
            cluster_code,
            cluster_name,
            sid,
            code,
            name,
            r.get("coverage_status", ""),
            r.get("active_taxonomy_count", ""),
            examples,
            "batch_3",
            str(counts.get(code, 0)),
            r.get("ab_A_status", ""),
            r.get("ab_B_status", ""),
            r.get("ab_dispute", ""),
            note,
        ])
    return out


def write_matrix(rows: list[list[str]], out_path: Path) -> None:
    if out_path.exists():
        raise FileExistsError(
            f"{out_path} already exists; refusing to overwrite"
        )
    tmp = out_path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(SCOPE_HDR)
        w.writerows(rows)
    os.replace(tmp, out_path)


def selftest() -> int:
    import tempfile

    def check(name, ok: bool):
        assert ok, name
        print(f"flip OK {name}")

    s1_rows = [{
        "domain_id": did, "domain_code": dcode,
        "official_domain_name": dname,
        "subdomain_id": sid, "subdomain_code": code,
        "subdomain_name": name,
        "coverage_status": "active_observed",
        "active_taxonomy_count": "1",
        "mapping_dispute": "None.",
        "reclassified_in": "", "reclassified_out": "",
        "ab_A_status": "", "ab_B_status": "", "ab_dispute": "",
    } for sid, code, name in _28.B3_TARGETS
        for did, (dcode, dname) in _28.B3_DOMAINS.items()
        if sid.startswith(did + ".")]
    for r in s1_rows:
        if r["subdomain_code"] == "animation_3d":
            r["reclassified_in"] = "engineering->visual_media/animation_3d"
    arche = {("visual_media", "animation_3d"): ["visual_media/task_a"],
             ("visual_media", "graphic_design"): ["visual_media/task_g"]}
    counts = {code: 3 for _sid, code, _name in _28.B3_TARGETS}
    rows = build_rows(s1_rows, arche, counts)
    check("matrix-9-rows", len(rows) == 9)
    check("matrix-hdr", rows[0][0] == "formal_non_cs")
    anim = [r for r in rows if r[4] == "animation_3d"][0]
    check("matrix-anim-example", anim[8] == "visual_media/task_a")
    check("matrix-anim-note",
          "reclassified-in: engineering->visual_media/animation_3d" in anim[14])
    check("matrix-batch", all(r[9] == "batch_3" for r in rows))
    check("matrix-count", all(r[10] == "3" for r in rows))

    s1_bad = [dict(r) for r in s1_rows]
    for r in s1_bad:
        if r["subdomain_code"] == "aviation":
            r["subdomain_name"] = "Tampered"
    try:
        build_rows(s1_bad, arche, counts)
        check("matrix-name-drift", False)
    except ValueError:
        check("matrix-name-drift", True)

    s1_less = s1_rows[:6]
    try:
        build_rows(s1_less, arche, counts)
        check("matrix-missing-target", False)
    except ValueError:
        check("matrix-missing-target", True)

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        out = d / "S1_02B3_SCOPE_MATRIX.csv"
        write_matrix(rows, out)
        check("matrix-write", out.is_file())
        with open(out, encoding="utf-8", newline="") as f:
            hit = list(csv.reader(f))
        check("matrix-write-hdr", hit[0] == SCOPE_HDR)
        check("matrix-write-len", len(hit) == 10)
        try:
            write_matrix(rows, out)
            check("matrix-refuse-overwrite", False)
        except FileExistsError:
            check("matrix-refuse-overwrite", True)
    print("selftest: matrix probes flip as expected")
    return 0


def main() -> int:
    if OUT_PATH.exists():
        print(f"FAIL {OUT_PATH} already exists; refusing to overwrite")
        return 1
    rows = build_rows(_28.load_s1_mapping(), load_archetypes(),
                      candidate_counts())
    write_matrix(rows, OUT_PATH)
    print(f"written {OUT_PATH}: {len(rows)} rows")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="S1-02B3 scope matrix generator")
    ap.add_argument("--selftest", action="store_true",
                    help="run in-memory negative self-tests")
    args = ap.parse_args()
    sys.exit(selftest() if args.selftest else main())