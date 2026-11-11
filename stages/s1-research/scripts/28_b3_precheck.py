#!/usr/bin/env python3
"""S1-02B3 precheck: phase0-final baseline, frozen inputs, mapping, B2-effective gates.

Gates (each printed OK/FAIL):
  G1 phase0-final baseline: checksum file lists 65 entries and every rehash
     matches; the other PHASE0_TOP files exist.
  G2 register consistency: .audit/s1-02b3-phase0-final-register.md names the
     same phase0-final directory.
  G3 S1-01 mapping: the 9 B3 target subdomains carry the exact official names,
     and the 3 domain codes/names are confirmed.
  G4 B2-effective readable: 39 rows, source_support_mode vocabulary valid.
  G5 outputs absent: none of the 6 S1-02B3 deliverables exists yet (skipped
     with --post so later runs can re-verify the frozen state).
  G6 frozen manifest: --record writes .audit/s1-02b3-frozen-manifest.json over
     the 33 project-side frozen files plus the 4 phase0-final top files;
     default run re-reads it and rehashes every entry.

Writes: .audit/s1-02b3-frozen-manifest.json only, under --record.
Never writes any frozen file, never calls a research model.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
AUDIT_DIR = ROOT / ".audit"
MANIFEST_PATH = AUDIT_DIR / "s1-02b3-frozen-manifest.json"
REGISTER_PATH = AUDIT_DIR / "s1-02b3-phase0-final-register.md"

B3_TARGETS = [
    ("8.1", "animation_3d", "3D, Animation & Interactive Media"),
    ("8.2", "graphic_design", "Graphic, Visual & Product Design"),
    ("8.4", "audio_music", "Audio, Music & Post-Production Media"),
    ("10.1", "aviation", "Aviation & Airspace Operations"),
    ("10.2", "maritime_port", "Maritime & Port Operations"),
    ("10.3", "fire_safety", "Fire Science & Public Safety"),
    ("11.1", "educational_technology", "Educational Technology"),
    ("11.2", "library_info", "Library & Information Science"),
    ("11.3", "translation", "Translation & Localization"),
]
B3_DOMAINS = {
    "8": ("visual_media", "Visual & Media Arts"),
    "10": ("transport_safety", "Transport & Safety"),
    "11": ("education_info", "Education & Information"),
}
EXPECTED_CHECKSUM_ENTRIES = 65
EXPECTED_B2E_ROWS = 39

B3_OUTPUTS = [
    "S1_02B3_SCOPE_MATRIX.csv",
    "S1_02B3_WORKFLOW_CANDIDATES.csv",
    "S1_02B3_SOURCE_CLAIM_MAP.csv",
    "S1_02B3_DUPLICATE_ATTRIBUTION.csv",
    "S1_02B3_OVERLAP_AND_RISKS.md",
    "S1_02B3_REVIEW_SUMMARY.md",
]

FROZEN_REL = [
    # S1-01
    "S1_01_CATEGORY_MAPPING.csv",
    "S1_01_GAPS_AND_RISKS.md",
    "S1_01_RECLASSIFICATION_EVIDENCE.csv",
    "S1_01_REVIEW_SUMMARY.md",
    "S1_01_REVISION_LOG.md",
    "S1_01_SOURCE_REGISTER.md",
    "S1_01_TASK_ARCHETYPE_EVIDENCE.csv",
    # S1-02A
    "S1_02A_DUPLICATE_ATTRIBUTION.csv",
    "S1_02A_DUPLICATE_ATTRIBUTION.md",
    "S1_02A_EFFECTIVE_CANDIDATES.csv",
    "S1_02A_EFFECTIVE_VIEW_VALIDATION.md",
    "S1_02A_EVIDENCE_AND_RISKS.md",
    "S1_02A_REVIEW_SUMMARY.md",
    "S1_02A_REVISION_LOG.md",
    "S1_02A_SCOPE_MATRIX.csv",
    "S1_02A_SOURCE_CLAIM_MAP.csv",
    "S1_02A_WORKFLOW_CANDIDATES.csv",
    # S1-02B1
    "S1_02B1_BASELINE_CONSISTENCY_REPORT.md",
    "S1_02B1_DUPLICATE_ATTRIBUTION.csv",
    "S1_02B1_DUPLICATE_ATTRIBUTION.md",
    "S1_02B1_EVIDENCE_AND_RISKS.md",
    "S1_02B1_REVIEW_SUMMARY.md",
    "S1_02B1_SOURCE_CLAIM_MAP.csv",
    "S1_02B1_WORKFLOW_CANDIDATES.csv",
    # S1-02B2
    "S1_02B2_DUPLICATE_ATTRIBUTION.csv",
    "S1_02B2_EFFECTIVE_CANDIDATES.csv",
    "S1_02B2_EVIDENCE_SCOPE_ERRATUM.md",
    "S1_02B2_OVERLAP_AND_RISKS.md",
    "S1_02B2_REVIEW_SUMMARY.md",
    "S1_02B2_SCOPE_MATRIX.csv",
    "S1_02B2_SOURCE_CLAIM_MAP.csv",
    "S1_02B2_WORKFLOW_CANDIDATES.csv",
    # carried B1 open items (verbatim carry into the two B3 MDs)
    "evidence/s1_02b2_research/b1_open_review_items.md",
]
PHASE0_TOP = [
    "FINAL_CHECKSUMS.sha256",
    "FINAL_VALIDATION_REPORT.md",
    "PHASE0_FINAL_REPORT.md",
    "SOURCE_MANIFEST_FINAL.json",
]
CSUM_LINE = re.compile(r"^([0-9a-f]{64})\s+(.+)$")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(
        name, SCRIPT_DIR / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_frag = _load("30_check_fragment_b3")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_checksum_lines(lines: list[str]) -> list[tuple[str, str]]:
    pairs = []
    for line in lines:
        m = CSUM_LINE.match(line.strip())
        if not m:
            raise ValueError(f"unparseable checksum line: {line!r}")
        pairs.append((m.group(1), m.group(2)))
    return pairs


def check_phase0(phase0_dir: Path,
                 expected: int = EXPECTED_CHECKSUM_ENTRIES) -> list[str]:
    errs = []
    if not phase0_dir.is_dir():
        return [f"phase0-final dir not found: {phase0_dir}"]
    for name in PHASE0_TOP:
        if not (phase0_dir / name).is_file():
            errs.append(f"missing {name}")
    csum = phase0_dir / "FINAL_CHECKSUMS.sha256"
    if not csum.is_file():
        return errs + ["missing FINAL_CHECKSUMS.sha256; cannot verify entries"]
    lines = csum.read_text(encoding="utf-8").splitlines()
    pairs = parse_checksum_lines(lines)
    if len(pairs) != expected:
        errs.append(f"checksum entry count {len(pairs)} != {expected}")
    for want, rel in pairs:
        p = phase0_dir / rel
        if not p.is_file():
            errs.append(f"checksum target missing: {rel}")
        elif sha256(p) != want:
            errs.append(f"checksum mismatch: {rel}")
    return errs


def check_register(phase0_dir: Path) -> list[str]:
    if not REGISTER_PATH.is_file():
        return [f"register missing: {REGISTER_PATH}"]
    text = REGISTER_PATH.read_text(encoding="utf-8")
    want = str(phase0_dir.resolve())
    if want not in text:
        return [f"register does not name {want}"]
    if "/analysis/phase0-final" not in text:
        return ["register names no phase0-final line"]
    return []


def load_s1_mapping() -> list[dict[str, str]]:
    with open(ROOT / "S1_01_CATEGORY_MAPPING.csv",
              encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_s1_rows(rows: list[dict[str, str]]) -> list[str]:
    errs = []
    by = {(r["subdomain_id"], r["subdomain_code"]): r for r in rows}
    for sid, code, name in B3_TARGETS:
        r = by.get((sid, code))
        if r is None:
            errs.append(f"missing target subdomain {sid} {code}")
            continue
        if r["subdomain_name"] != name:
            errs.append(
                f"{sid} {code}: official name {r['subdomain_name']!r} "
                f"!= expected {name!r}"
            )
    for did, (dcode, dname) in B3_DOMAINS.items():
        matched = [r for r in rows if r["domain_id"] == did
                   and r["official_domain_name"] == dname]
        if not matched:
            errs.append(f"domain {did} {dcode} {dname!r} not confirmed in S1-01")
    return errs


def check_b2e_rows(rows: list[dict[str, str]]) -> list[str]:
    errs = []
    if len(rows) != EXPECTED_B2E_ROWS:
        errs.append(
            f"B2-effective rows {len(rows)} != expected {EXPECTED_B2E_ROWS}"
        )
    bad_modes = sorted({
        r["source_support_mode"] for r in rows
        if r["source_support_mode"] not in _frag.SUPPORT_MODES
    })
    if bad_modes:
        errs.append(f"invalid source_support_mode values {bad_modes}")
    return errs


def check_outputs_absent(root: Path) -> list[str]:
    present = [n for n in B3_OUTPUTS if (root / n).exists()]
    return [f"B3 deliverable already exists: {n}" for n in present]


def sniff_phase0_dir() -> Path:
    text = ""
    if REGISTER_PATH.is_file():
        text = REGISTER_PATH.read_text(encoding="utf-8")
    for ln in text.splitlines():
        if "/analysis/phase0-final" in ln:
            m = re.search(r"(/\S*/analysis/phase0-final)", ln)
            if m:
                return Path(m.group(1))
    return Path("")


def build_manifest(phase0_dir: Path) -> dict:
    files = {}
    for rel in FROZEN_REL:
        p = ROOT / rel
        if not p.is_file():
            raise FileNotFoundError(f"frozen project file missing: {p}")
        files[str(p.resolve())] = {"sha256": sha256(p), "size": p.stat().st_size}
    for name in PHASE0_TOP:
        p = phase0_dir / name
        if not p.is_file():
            raise FileNotFoundError(f"phase0 file missing: {p}")
        files[str(p.resolve())] = {"sha256": sha256(p), "size": p.stat().st_size}
    return {
        "files": files,
        "meta": {
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "phase0_final": str(phase0_dir.resolve()),
            "check_entries": EXPECTED_CHECKSUM_ENTRIES,
            "frozen_project_files": len(FROZEN_REL),
            "frozen_phase0_files": len(PHASE0_TOP),
        },
    }


def verify_manifest_at(path: Path) -> list[str]:
    if not path.is_file():
        return [f"manifest missing: {path}"]
    data = json.loads(path.read_text(encoding="utf-8"))
    errs = []
    for fpath, info in sorted(data["files"].items()):
        p = Path(fpath)
        if not p.is_file():
            errs.append(f"manifest entry missing on disk: {fpath}")
            continue
        if sha256(p) != info["sha256"]:
            errs.append(f"manifest drift: {fpath}")
        elif p.stat().st_size != info["size"]:
            errs.append(f"manifest size drift: {fpath}")
    return errs


def run_gates(phase0_dir: Path, mode: str, post: bool) -> int:
    print(f"phase0-final dir: {phase0_dir}")
    failures = 0

    def gate(tag, errs):
        nonlocal failures
        if errs:
            failures += 1
            print(f"FAIL {tag}")
            for e in errs:
                print(f"     {e}")
        else:
            print(f"OK   {tag}")

    gate("G1-phase0", check_phase0(phase0_dir))
    gate("G2-register", check_register(phase0_dir))
    gate("G3-s1-mapping", check_s1_rows(load_s1_mapping()))
    with open(ROOT / "S1_02B2_EFFECTIVE_CANDIDATES.csv",
              encoding="utf-8", newline="") as f:
        b2e = list(csv.DictReader(f))
    gate("G4-b2-effective", check_b2e_rows(b2e))
    if post:
        print("SKIP G5-outputs-absent (post mode)")
    else:
        gate("G5-outputs-absent", check_outputs_absent(ROOT))
    if mode == "record":
        if MANIFEST_PATH.exists():
            gate("G6-manifest-record",
                 [f"{MANIFEST_PATH} already exists; refusing to overwrite"])
        else:
            try:
                MANIFEST_PATH.write_text(
                    json.dumps(build_manifest(phase0_dir), indent=2,
                               ensure_ascii=False), encoding="utf-8")
                gate("G6-manifest-record", verify_manifest_at(MANIFEST_PATH))
                print(f"manifest written: {MANIFEST_PATH}")
            except FileNotFoundError as exc:
                gate("G6-manifest-record", [str(exc)])
    else:
        gate("G6-manifest-verify", verify_manifest_at(MANIFEST_PATH))
    print(f"gates failed={failures}")
    return 1 if failures else 0


def selftest() -> int:
    import tempfile

    def check(name, ok: bool):
        assert ok, name
        print(f"flip OK {name}")

    s1_ok = [{
        "domain_id": did, "domain_code": dcode,
        "official_domain_name": dname,
        "subdomain_id": sid, "subdomain_code": code,
        "subdomain_name": name,
    } for sid, code, name in B3_TARGETS
        for did, (dcode, dname) in B3_DOMAINS.items()
        if sid.startswith(did + ".")]
    check("s1-good", check_s1_rows(s1_ok) == [])

    s1_bad = [dict(r, subdomain_name="Tampered") for r in s1_ok[:8]] + s1_ok[8:]
    check("s1-name-tamper",
          any("official name" in e for e in check_s1_rows(s1_bad)))

    s1_missing = s1_ok[:]
    s1_missing.pop(3)
    check("s1-missing",
          any("missing target" in e for e in check_s1_rows(s1_missing)))

    b2e_ok = [
        {"candidate_id": str(i),
         "source_support_mode": "recorded_partial_support"}
        for i in range(EXPECTED_B2E_ROWS)
    ]
    check("b2e-good", check_b2e_rows(b2e_ok) == [])
    check("b2e-badmode", check_b2e_rows(
        b2e_ok[:1] + [dict(b2e_ok[1], source_support_mode="registered")]) != [])
    check("b2e-len", check_b2e_rows(b2e_ok[:-1]) != [])

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "S1_02B3_SCOPE_MATRIX.csv").write_text("x", encoding="utf-8")
        check("outputs-present", check_outputs_absent(d) != [])
        check("outputs-absent",
              check_outputs_absent(Path(td) / "sub") == [])

        file_a = d / "a.txt"
        file_a.write_text("hello", encoding="utf-8")
        good = sha256(file_a)
        for name in PHASE0_TOP:
            (d / name).write_text("x", encoding="utf-8")
        (d / "FINAL_CHECKSUMS.sha256").write_text(
            f"{good}  a.txt\n", encoding="utf-8")
        check("phase0-good", check_phase0(d, expected=1) == [])

        (d / "FINAL_CHECKSUMS.sha256").write_text(
            f"{'0' * 64}  a.txt\n", encoding="utf-8")
        check("phase0-csum-mismatch", check_phase0(d, expected=1) != [])

        (d / "FINAL_CHECKSUMS.sha256").write_text(
            "\n".join(f"{'0' * 64}  f{n}.txt" for n in range(64)) + "\n",
            encoding="utf-8")
        check("phase0-entry-count", check_phase0(d, expected=65) != [])

        mp = d / "manifest.json"
        manifest = {"files": {str(file_a.resolve()): {"sha256": good, "size": 5}}}
        mp.write_text(json.dumps(manifest), encoding="utf-8")
        check("manifest-good", verify_manifest_at(mp) == [])
        manifest["files"][str(file_a.resolve())]["sha256"] = "0" * 64
        mp.write_text(json.dumps(manifest), encoding="utf-8")
        check("manifest-drift", verify_manifest_at(mp) != [])
    print("selftest: all precheck probes flip as expected")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="S1-02B3 precheck gates")
    ap.add_argument("--selftest", action="store_true",
                    help="run in-memory negative self-tests")
    ap.add_argument("--record", action="store_true",
                    help="write the frozen manifest instead of verifying it")
    ap.add_argument("--post", action="store_true",
                    help="skip the outputs-absent gate (post-merge runs)")
    ap.add_argument("--phase0-final",
                    help="phase0-final directory (default: sniffed from register)")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    mode = "record" if args.record else "verify"
    p0 = Path(args.phase0_final).resolve() if args.phase0_final \
        else sniff_phase0_dir()
    if not p0:
        print("FAIL cannot locate phase0-final; pass --phase0-final")
        sys.exit(1)
    sys.exit(run_gates(p0, mode, args.post))