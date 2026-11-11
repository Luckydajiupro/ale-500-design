#!/usr/bin/env python3
# build_manifest_final.py: build SOURCE_MANIFEST_FINAL.json for phase0-final.
# Usage: python3 scripts/build_manifest_final.py [--final]
#   pre   stage: stage=pre,  hashed_at_pre stamped
#   final stage: stage=final, hashed_at_post stamped, requires the report set
import hashlib, json, os, sys, datetime

def now_ts():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

WS = "/Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108"
FINAL = os.path.join(WS, "analysis", "phase0-final")
ARCHIVE = "/Users/mac/Archives/ALE-Phase0-History-20261110"
ARCHIVE_ANALYSIS = os.path.join(ARCHIVE, "analysis")
R0 = os.path.join(ARCHIVE_ANALYSIS, "phase0-official-baseline")
R1 = os.path.join(ARCHIVE_ANALYSIS, "phase0-official-baseline-r1")
R2 = os.path.join(ARCHIVE_ANALYSIS, "phase0-official-baseline-r2")
AUDIT = "/Users/mac/Workspaces/ale-研究设计/.audit"
NOTES = os.path.join(AUDIT, "phase0-notes")

FINAL_STAGE = "--final" in sys.argv

INHERIT = {
    "00_project_brief.md": ("r1", "2c31732ba1386a4dd533e8dff0ca665317ae2972bea5bbb3850b807759be567a", "reworded"),
    "02_repo_inventory.md": ("r1", "a60c74375f7dd1afb151cdc0ea1309af8600e1db69073c3b0a7d430f94010470", "reworded"),
    "03_repo_structure_comparison.md": ("r2", "569b63ae13273a00250d44a9766142a50b4e6872bd74f17d5ea1cfc55364fb60", "reworded"),
    "04_task_inventory.csv": ("r2", "b96a14c1bc4e08c36268a456ba2a08897c2a2c54c4018334d47d354063adc2fb", "copied"),
    "05_task_category_summary.csv": ("r2", "f2bc36a1b86831193ab70dc51dc105bfc21c791fd01942b06c142ec3e55a5fc3", "copied"),
    "06_runtime_provider_matrix.md": ("r2", "462e019206df28b1418f1f841e7faf56743442239df752bb8edaf3892133d16e", "reworded"),
    "07_old_new_format_comparison.md": ("r1", "3f4ce84e6eef3ee8073e1b81958ba3a3d01aaaccebe6e830fc664296577644ac", "reworded"),
    "08_coverage_matrix_draft.csv": ("r2", "17321d76626726954c977c6072dd0e23bbee73e06b9bc0a752691a1d3ba0553c", "copied"),
    "09_unknowns_and_decisions.md": ("r2", "3079fcbed930de719090a5824ec6370ff826a1ca941afd7cbdc539cfeb7ecedc", "reworded"),
    "10_phase0_summary.md": ("r2", "a85d293442b16f7ecf36783b54df3636543e9f09ed25a77d8aba4204aea54cc8", "reworded"),
}

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def find_source(rel):
    name = os.path.basename(rel)
    if rel.startswith("evidence/final_validate_results."):
        return None  # validator output, new this round
    if rel.startswith("evidence/history-final/"):
        return None  # new this round
    if rel.startswith("evidence/history-r0/"):
        return os.path.join(WS, name)
    if rel.startswith("evidence/history-r1/"):
        return os.path.join(R1, name)
    if rel.startswith("evidence/history-r2/"):
        if name == "EXECUTION_BRIEF_R2_CHAT.md":
            return None
        if name == "R2_FINAL_CHECKSUMS.sha256":
            return os.path.join(R2, "FINAL_CHECKSUMS.sha256")
        return os.path.join(R2, name)
    if rel.startswith("evidence/notes/"):
        return os.path.join(NOTES, name)
    if rel == "evidence/counterexample_results.tsv":
        return os.path.join(R2, "evidence", "counterexamples", "results.tsv")
    if rel == "evidence/r0_01_baseline_manifest.json":
        return os.path.join(R0, "01_baseline_manifest.json")
    if rel.startswith("evidence/"):
        cands = [os.path.join(R2, "evidence", name),
                 os.path.join(R1, "evidence", name),
                 os.path.join(R2, name),
                 os.path.join(R1, name),
                 os.path.join(R0, name),
                 os.path.join(AUDIT, name),
                 os.path.join(NOTES, name)]
        found = [c for c in cands if os.path.exists(c)]
        if not found:
            raise SystemExit(f"ERROR {rel}: 0 source candidates")
        copy_h = sha(os.path.join(FINAL, rel))
        agreeing = [c for c in found if sha(c) == copy_h]
        if not agreeing:
            raise SystemExit(f"ERROR {rel}: copy matches no candidate, candidates differ: {found}")
        return agreeing[0]
    if name in INHERIT:
        tag = INHERIT[name][0]
        return {"r0": R0, "r1": R1, "r2": R2}[tag] + "/" + name
    return None  # new this round

def archive_rel_of(sp):
    if sp and sp.startswith(ARCHIVE_ANALYSIS + os.sep) and ARCHIVE_ANALYSIS != sp:
        return os.path.relpath(sp, ARCHIVE_ANALYSIS)
    return None

def main():
    final_files = {}
    sources = []
    for name, (tag, src_sha, mode) in INHERIT.items():
        p = os.path.join(FINAL, name)
        if not os.path.exists(p):
            raise SystemExit(f"ERROR final file missing: {name}")
        src = {"r0": R0, "r1": R1, "r2": R2}[tag]
        sp = os.path.join(src, name)
        if sha(sp) != src_sha:
            raise SystemExit(f"ERROR source sha mismatch: {name}")
        final_files[name] = {"sha256": sha(p), "mode": mode, "source": os.path.relpath(sp, WS)}
        sources.append({"file": name, "source_path": sp, "source_sha256": src_sha, "mode": mode,
                        "archive_rel": archive_rel_of(sp)})

    for req, required in (("PHASE0_FINAL_REPORT.md", True), ("FINAL_VALIDATION_REPORT.md", False)):
        rp = os.path.join(FINAL, req)
        if os.path.exists(rp):
            final_files[req] = {"sha256": sha(rp), "mode": "new", "source": None}
        elif FINAL_STAGE and required:
            raise SystemExit(f"ERROR final stage requires {req}")

    evidence = {}
    for root, dirs, files in os.walk(os.path.join(FINAL, "evidence")):
        for fn in sorted(files):
            if fn == ".DS_Store":
                continue
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, FINAL)
            sp = find_source(rel)
            evidence[rel] = {"sha256": sha(p),
                             "mode": "new" if sp is None else "copied",
                             "source": os.path.relpath(sp, WS) if sp else None}
            if sp is not None:
                sources.append({"file": rel, "source_path": sp,
                                "source_sha256": sha(sp), "mode": "copied",
                                "archive_rel": archive_rel_of(sp)})

    scripts = {}
    for fn in sorted(os.listdir(os.path.join(FINAL, "scripts"))):
        p = os.path.join(FINAL, "scripts", fn)
        if os.path.isfile(p):
            scripts[os.path.relpath(p, FINAL)] = {"sha256": sha(p), "mode": "new"}

    prog = os.path.join(FINAL, "progress.log")
    prev_checksum_sha = None
    cs = os.path.join(FINAL, "FINAL_CHECKSUMS.sha256")
    if os.path.exists(cs):
        prev_checksum_sha = sha(cs)

    prev = {}
    prev_loaded = False
    try:
        prev = json.load(open(os.path.join(FINAL, "SOURCE_MANIFEST_FINAL.json"), encoding="utf-8"))
        prev_loaded = True
    except Exception:
        pass
    hashed_at_pre = prev.get("hashed_at_pre")
    hashed_at_post = None
    amendment = prev.get("amendment")
    if FINAL_STAGE:
        if not hashed_at_pre:
            raise SystemExit("ERROR no pre manifest found; run the pre stage first")
        if prev_loaded and prev.get("stage") == "final":
            if prev.get("lifecycle") != "closed":
                # first closeout re-seal: the prior seal's post bookend becomes the new pre
                hashed_at_pre = prev.get("hashed_at_post") or hashed_at_pre
                hashed_at_post = now_ts()
                amendment = {
                    "amended_at": now_ts(),
                    "prior_hashed_at_post": prev.get("hashed_at_post"),
                    "reason": "closeout amendment: history archived and moved out of analysis, lifecycle closed, source lineage switched to the external archive",
                }
            else:
                # resume of the closed state: keep the bookends, refresh the hashes
                hashed_at_post = prev.get("hashed_at_post")
        else:
            hashed_at_post = now_ts()

    m = {
        "workspace": WS,
        "final_dir": os.path.relpath(FINAL, WS),
        "phase": "phase0-final",
        "stage": "final" if FINAL_STAGE else "pre",
        "created_at": now_ts(),
        "hashed_at_pre": hashed_at_pre if FINAL_STAGE else now_ts(),
        "hashed_at_post": hashed_at_post if FINAL_STAGE else None,
        "lifecycle": "closed",
        "amendment": amendment,
        "brief": "evidence/history-final/EXECUTION_BRIEF_FINAL_CHAT.md",
        "r0_dir": os.path.relpath(R0, WS),
        "r1_dir": os.path.relpath(R1, WS),
        "r2_dir": os.path.relpath(R2, WS),
        "inputs": "inputs-readonly",
        "final_files": final_files,
        "progress_log": {"sha256": sha(prog), "mode": "new"},
        "evidence": evidence,
        "scripts": scripts,
        "sources": sources,
        "checksum_file_sha256": None,
        "prev_checksum_file_sha256": prev_checksum_sha,
        "note": "self-excluded from its own content; FINAL_CHECKSUMS.sha256 is regenerated LAST on each re-seal and covers every file except itself; prev_checksum_file_sha256 records the value from before regeneration",
    }
    json.dump(m, open(os.path.join(FINAL, "SOURCE_MANIFEST_FINAL.json"), "w"), ensure_ascii=False, indent=1)
    print("manifest written:", m["stage"], "| final_files", len(final_files),
          "| evidence", len(evidence), "| scripts", len(scripts))

main()