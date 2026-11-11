#!/usr/bin/env python3
"""S1-02B3 fragment merger.

Inputs: the 3 research fragments evidence/s1_02b3_research/<stem>_candidates.csv.
Outputs: S1_02B3_WORKFLOW_CANDIDATES.csv (43 EFFECTIVE-shaped columns) and
S1_02B3_SOURCE_CLAIM_MAP.csv (10 columns). Refuses to overwrite existing
deliverables.

The merger is the only writer that fills the 7 derived columns:
linux_verification_state is uniformly appended NOT_VERIFIED; expert_pending
and engineering_pending are derived from evidence_kind and
software_adaptation via the single vocabulary in 30_check_fragment_b3.py;
duplicate_status starts as "none". Every fragment must pass the 30 contract
checks in full before anything is written. No model calls.
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
FRAG_DIR = ROOT / "evidence" / "s1_02b3_research"
WF_PATH = ROOT / "S1_02B3_WORKFLOW_CANDIDATES.csv"
SC_PATH = ROOT / "S1_02B3_SOURCE_CLAIM_MAP.csv"

SC_COLS = [
    "candidate_id",
    "subdomain_code",
    "workflow_title",
    "source_url",
    "source_category",
    "evidence_kind",
    "evidence_level",
    "source_type",
    "software_adaptation",
    "correction_note",
]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(
        name, SCRIPT_DIR / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_frag = _load("30_check_fragment_b3")


def derived(row: dict[str, str], stem: str) -> tuple[str, str, str]:
    kind = row["evidence_kind"]
    adaptation = row["software_adaptation"]
    expert = (
        f"YES: E4: {row['pending_confirmation']}"
        if kind == "expert_pending_proposal" else ""
    )
    eng = _frag.ENG_FLAGS.get(adaptation, "")
    return "NOT_VERIFIED", expert, eng


def merge(frag_dir: Path = FRAG_DIR) -> tuple[list[list[str]], list[list[str]]]:
    frag_rows: dict[str, list[dict[str, str]]] = {}
    for stem in sorted(_frag.CLUSTERS):
        path = frag_dir / f"{stem}_candidates.csv"
        if not path.exists():
            raise FileNotFoundError(
                f"fragment {path} missing; run the research children first"
            )
        text = path.read_text(encoding="utf-8")
        raw = _frag.parse_csv(text)
        errs = _frag.check(raw, stem)
        dicts = _frag.rows_to_dicts(raw)
        fatal = {k: v for k, v in errs.items() if v and k != "warn_target"}
        if fatal:
            raise ValueError(f"fragment {stem} fails contract: {fatal}")
        sidecar_errs = _frag.check_sidecar(stem, dicts, frag_dir)
        if sidecar_errs:
            raise ValueError(f"fragment {stem} sidecar fails: {sidecar_errs}")
        frag_rows[stem] = dicts

    ordered = []
    for code, _slug in _frag.ID_SLUG.items():
        for d in frag_rows[_frag.SUBDOMAIN_OF_CLUSTER[code]]:
            if d["subdomain_code"] == code:
                ordered.append(d)
    ordered.sort(key=lambda d: (
        list(_frag.ID_SLUG).index(d["subdomain_code"]), d["candidate_id"]))

    wf_rows = []
    sc_rows = []
    for d in ordered:
        linux, expert, eng = derived(d, _frag.SUBDOMAIN_OF_CLUSTER[d["subdomain_code"]])
        wf_rows.append(
            [d[c] for c in _frag.FRAG_COLS]
            + [linux, expert, eng, _frag.SUBDOMAIN_OF_CLUSTER[d["subdomain_code"]],
               "none", "", ""]
            + [d[c] for c in _frag.EVIDENCE_COLS]
        )
        sc_rows.append([
            d["candidate_id"], d["subdomain_code"], d["workflow_title"],
            d["primary_source_url"], d["source_category"], d["evidence_kind"],
            d["evidence_level"], d["source_type"], d["software_adaptation"],
            "",
        ])
    return wf_rows, sc_rows


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    if path.exists():
        raise FileExistsError(f"{path} already exists; refusing to overwrite")
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    os.replace(tmp, path)


def selftest() -> int:
    import tempfile
    import json

    def check(name, ok: bool):
        assert ok, name
        print(f"flip OK {name}")

    def frag_rows(stem):
        out = []
        cfg = _frag.CLUSTERS[stem]
        n = 1
        for code in cfg["subdomains"]:
            for i in range(3):
                out.append(_frag.make_row(
                    code, f"{cfg['slugs'][code]}_wf{i + 1:02d}",
                    workflow_title=f"{cfg['slugs'][code]} workflow {i + 1}"))
                n += 1
        return out

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for stem in _frag.CLUSTERS:
            rows = frag_rows(stem)
            text = _frag.rows_text(rows)
            (d / f"{stem}_candidates.csv").write_text(text, encoding="utf-8")
            counts = {}
            for r in rows:
                counts[r["subdomain_code"]] = counts.get(r["subdomain_code"], 0) + 1
            (d / f"{stem}.json").write_text(json.dumps({"subdomains": [
                {"subdomain_code": c, "candidate_count": counts[c],
                 "coverage_notes": "note"}
                for c in _frag.CLUSTERS[stem]["subdomains"]
            ]}), encoding="utf-8")
        wf, sc = merge(d)
        check("merge-len", len(wf) == 27)
        check("merge-linux", all(r[32] == "NOT_VERIFIED" for r in wf))
        check("merge-dup-none", all(r[36] == "none" for r in wf))
        first_id = [r[3] for r in wf]
        expect_ids = [f"{sl}_wf{n:02d}"
                      for code in _frag.ID_SLUG
                      for sl in [_frag.ID_SLUG[code]]
                      for n in range(1, 4)]
        check("merge-dense-order", first_id == expect_ids)
        check("sc-len", len(sc) == 27 and len(sc[0]) == 10)

        out_wf = d / "S1_02B3_WORKFLOW_CANDIDATES.csv"
        write_csv(out_wf, _frag.B3_FRAG_COLS, wf)
        check("write-wf", out_wf.is_file())
        try:
            write_csv(out_wf, _frag.B3_FRAG_COLS, wf)
            check("refuse-wf", False)
        except FileExistsError:
            check("refuse-wf", True)

        e4 = _frag.make_row("aviation", "ts_avi_wf01",
                            evidence_kind="expert_pending_proposal",
                            evidence_level="E4",
                            source_type="project_proposal",
                            pending_confirmation="await expert")
        linux, expert, eng = derived(e4, "ts_cluster")
        check("derived-e4",
              expert == "YES: E4: await expert" and eng == "" and
              linux == "NOT_VERIFIED")
        cond = _frag.make_row("aviation", "ts_avi_wf01",
                              software_adaptation="conditional")
        _l, _e, ce = derived(cond, "ts_cluster")
        check("derived-conditional",
              ce == _frag.ENG_FLAGS["conditional"])
    print("selftest: merge probes flip as expected")
    return 0


def main() -> int:
    try:
        wf, sc = merge()
    except (FileNotFoundError, ValueError) as exc:
        print(f"FAIL merge: {exc}")
        return 1
    try:
        write_csv(WF_PATH, _frag.B3_FRAG_COLS, wf)
        write_csv(SC_PATH, SC_COLS, sc)
    except FileExistsError as exc:
        print(f"FAIL {exc}")
        return 1
    print(f"written {WF_PATH}: {len(wf)} rows")
    print(f"written {SC_PATH}: {len(sc)} rows")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="S1-02B3 fragment merger")
    ap.add_argument("--selftest", action="store_true",
                    help="run in-memory negative self-tests")
    args = ap.parse_args()
    sys.exit(selftest() if args.selftest else main())