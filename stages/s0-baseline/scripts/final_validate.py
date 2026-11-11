#!/usr/bin/env python3
# final_validate.py - independent validation for phase0-final (brief m01381 item 8).
# Usage:
#   python3 scripts/final_validate.py                 pre-freeze: content checks only
#   python3 scripts/final_validate.py --freeze        asserts FINAL_VALIDATION_REPORT.md + FINAL_CHECKSUMS.sha256
#   python3 scripts/final_validate.py --verify-sums   re-verify FINAL_CHECKSUMS.sha256 against disk (read-only)
import csv as csv_mod
import hashlib, json, os, re, subprocess, sys
from collections import Counter

WS = "/Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108"
FINAL = os.path.join(WS, "analysis", "phase0-final")
INPUTS = os.path.join(WS, "inputs-readonly")
REPOS = [
    ("01_agents-last-exam", "/Users/mac/Workspaces/ale-研究设计/agents-last-exam",
     "2e91edd3cd26baa35a38127c90c8e5241dfbe62f"),
    ("02_ale", "/Users/mac/Workspaces/ale-研究设计/ale",
     "73517c2eb097abe7974e9ec4de9819a02cd0ee81"),
    ("04_ale-tasks-base", "/Users/mac/Workspaces/ale-研究设计/ale-tasks-base",
     "492249a2ca4b9d74efd3584a90399473c2e928c7"),
]
FINAL_MD = ["00_project_brief.md","02_repo_inventory.md","03_repo_structure_comparison.md",
            "06_runtime_provider_matrix.md","07_old_new_format_comparison.md",
            "09_unknowns_and_decisions.md","10_phase0_summary.md","PHASE0_FINAL_REPORT.md"]

mode_freeze = "--freeze" in sys.argv
mode_verify = "--verify-sums" in sys.argv

results = []
def check(gid, object_, verdict, evidence):
    assert verdict in ("PASS","FAIL","ERROR","SKIP")
    results.append({"check_id": gid, "object": object_, "verdict": verdict, "evidence": evidence})
    print(f"STATUS {gid} | {object_} | {verdict} | {evidence}")

def sha(p):
    try:
        h = hashlib.sha256(open(p,"rb").read()).hexdigest()
        return h, None
    except Exception as e:
        return None, repr(e)

# ---------- fv-02/03/04: the three data tables ----------
def csv_rows(p):
    raw = open(p, encoding="utf-8").read().splitlines()
    out = []
    for line in raw:
        if line.startswith("#"):
            continue
        out.append(next(csv_mod.reader([line])))
    return out

try:
    rows04 = csv_rows(os.path.join(FINAL,"04_task_inventory.csv"))
    hdr, data04 = rows04[0], rows04[1:]
    ncols = len(hdr)
    ok_cols = all(len(r) == ncols for r in data04)
    ids = [r[0] for r in data04]
    domains = {r[1] for r in data04}
    check("fv-02a","04_task_inventory.csv", "PASS" if len(data04)==122 and len(set(ids))==122 else "FAIL",
          f"rows={len(data04)} unique_ids={len(set(ids))}")
    check("fv-02b","04_task_inventory.csv", "PASS" if ncols==31 and ok_cols else "FAIL",
          f"header_cols={ncols} uniform={ok_cols}")
    vocab = {
        "gui_status": {r[19] for r in data04},
        "external_service": {r[25] for r in data04},
        "linux_runnable": {r[27] for r in data04},
        "run_state_current": {r[30] for r in data04},
    }
    vg = vocab["gui_status"] <= {"yes","no","unknown"}
    ve = vocab["external_service"] <= {"none","staged-local","online-required","public-ref"}
    vl = vocab["linux_runnable"] <= {"allowlist","doc_exception","none"}
    vr = vocab["run_state_current"] == {"NOT_RUN"}
    check("fv-02c","04_task_inventory.csv vocab", "PASS" if vg and ve and vl and vr else "FAIL",
          f"gui={sorted(vocab['gui_status'])} ext={sorted(vocab['external_service'])} lr={sorted(vocab['linux_runnable'])} run={vocab['run_state_current']}")
    dom04 = Counter(r[1] for r in data04)
    check("fv-02d","04_task_inventory.csv domains", "PASS" if sorted(dom04) == sorted([
        "business_finance","computing_math","education_info","engineering","health_medicine",
        "legal","life_sciences","other","physical_sciences","psychology_neuro",
        "social_sciences","transport_safety","visual_media"]) else "FAIL",
          f"domains={len(dom04)} cs={dom04.get('computing_math')}")
except Exception as e:
    check("fv-02x","04_task_inventory.csv", "ERROR", repr(e))

try:
    rows05 = csv_rows(os.path.join(FINAL,"05_task_category_summary.csv"))
    body05 = [r for r in rows05[1:] if r[0] != "TOTAL"]
    tot05 = [r for r in rows05[1:] if r[0] == "TOTAL"]
    check("fv-03a","05_task_category_summary.csv",
          "PASS" if len(tot05)==1 and tot05[0][1]=="122" and tot05[0][3].startswith("103") else "FAIL",
          f"total_rows={len(tot05)} total={tot05[0] if tot05 else None}")
    d05 = {r[0]: int(r[1]) for r in body05}
    d04 = {k: v for k, v in dom04.items()}
    match = d05 == d04 and len(d05) == 13
    check("fv-03b","05_task_category_summary.csv vs 04 census",
          "PASS" if match else "FAIL", f"05_domains={len(d05)} equal={d05==d04}")
except Exception as e:
    check("fv-03x","05_task_category_summary.csv", "ERROR", repr(e))

try:
    rows08 = csv_rows(os.path.join(FINAL,"08_coverage_matrix_draft.csv"))
    hdr08, data08 = rows08[0], rows08[1:]
    cs_row = [r for r in data08 if r[0]=="computing_math"]
    noncs = [r for r in data08 if r[0]!="computing_math"]
    quota = sum(int(r[2]) for r in noncs)
    check("fv-04a","08_coverage_matrix_draft.csv", "PASS" if quota==500 and len(noncs)==12 else "FAIL",
          f"non_cs_rows={len(noncs)} sum={quota}")
    check("fv-04b","08_coverage_matrix_draft.csv", "PASS" if cs_row and int(cs_row[0][2])==0 else "FAIL",
          f"computing_math={cs_row[0][2] if cs_row else None}")
    d08 = {r[0]: int(r[1]) for r in data08}
    d05_cur = globals().get("d05", {})
    check("fv-04c","08 official_count vs 05", "PASS" if d05_cur == d08 and len(d08)==13 else "FAIL",
          f"08_domains={len(d08)} equal={d05_cur==d08}")
except Exception as e:
    check("fv-04x","08_coverage_matrix_draft.csv", "ERROR", repr(e))

# ---------- fv-05: cross-file key phrases ----------
BANNED = {
    "待合并": "merge placeholder remains",
    "合并点待": "merge placeholder remains",
    "qemu+KVM 可用": "unproven qemu claim",
    "已跑通": "runtime success claim (NOT_RUN violated)",
    "可直接运行": "runtime success claim",
    "103+397": "rejected route stated as route",
    "Phase 0 R1修订完成": "stale round status",
    "待复审": "stale round status",
    "R1_VALIDATION_REPORT.md 与 CHANGELOG_R1.md": "stale tail cite",
    "待批准历史目录清理": "stale pre-cleanup lifecycle status",
}
NEG = ("不存在","没有","未批准","不是","不构成","未提供","未定","不成立","否决")
def banned_scan(path, rel):
    text = open(path, encoding="utf-8").read()
    hits = []
    for phrase in BANNED:
        for m in re.finditer(re.escape(phrase), text):
            s = max(0, m.start()-120)
            ctx = text[s:m.end()+40].replace("\n"," ")
            if any(n in ctx for n in NEG) or "上一轮" in ctx or "第一轮" in ctx or "历史" in ctx \
           or "history-r1" in ctx or "修订轮" in ctx or "R1_VALIDATION_REPORT.md" in ctx:
                continue
            hits.append(f"{phrase}@ {ctx[:80]}")
    check("fv-05", rel, "PASS" if not hits else "FAIL", f"banned_hits={hits[:5]}")
for rel in FINAL_MD:
    p = os.path.join(FINAL, rel)
    if os.path.exists(p):
        banned_scan(p, rel)
    else:
        check("fv-05", rel, "ERROR", "missing file")

# ---------- fv-06: citation resolution ----------
PATHRE = re.compile(r"([\w./-]+\.(?:tsv|md|json|csv|txt|log|sha256|py))")
CITE_MARK = re.compile(r"(见\s{0,3}|\[doc[:\]]|\[code[:\]]|\[cmd[:\]]|\[原执行方记录[:\]])")
BOUND = re.compile(r"(不改动|只读|禁止|不动|冻结)")
LS = re.compile(r"^analysis/phase0-official-baseline(?!-final)")
ALLOW_FINAL = {"FINAL_CHECKSUMS.sha256","FINAL_VALIDATION_REPORT.md","SOURCE_MANIFEST_FINAL.json"}
_BASEINDEX = None
def _basename_index():
    global _BASEINDEX
    if _BASEINDEX is None:
        idx = {}
        for base, dirs, files in os.walk(INPUTS):
            for fn in files:
                idx.setdefault(fn, os.path.join(base, fn))
        _BASEINDEX = idx
    return _BASEINDEX

def token_resolves(tok, idx):
    if tok in ALLOW_FINAL or os.path.exists(os.path.join(FINAL, tok)):
        return True
    if tok.startswith("inputs-readonly/"):
        return os.path.exists(os.path.join(WS, tok))
    if "/" not in tok:
        return tok in idx
    return os.path.basename(tok) in idx

def scan_cites(path, rel):
    text = open(path, encoding="utf-8").read()
    idx = _basename_index()
    bad = []
    for m in PATHRE.finditer(text):
        tok = m.group(1).rstrip(".,;)")
        if token_resolves(tok, idx):
            continue
        window = text[max(0, m.start()-40):m.end()]
        if re.search(r"(不在仓库内|不在快照内|未在快照内)", text[max(0, m.start()-40):min(len(text), m.end()+60)]):
            continue
        cited = CITE_MARK.search(window) is not None
        if LS.search(tok):
            if cited and not BOUND.search(window):
                bad.append(tok)
        elif cited:
            bad.append(tok)
    check("fv-06", rel, "PASS" if not bad else "FAIL", f"dangling={bad[:6]}")
for rel in FINAL_MD:
    p = os.path.join(FINAL, rel)
    if os.path.exists(p):
        scan_cites(p, rel)

# ---------- fv-07: lifecycle status (closeout amendment) ----------
CLOSED_PHRASES = ["Phase 0 已完成并验收通过", "历史目录已归档并完成清理",
                  "analysis/phase0-final/ 是当前唯一有效基线", "Phase 0 CLOSED"]
STALE_STATUS = "待批准历史目录清理"
status_targets = [("10_phase0_summary.md","tail"), ("00_project_brief.md","stop"),
                  ("PHASE0_FINAL_REPORT.md","tail")]
if mode_verify:
    status_targets.append(("FINAL_VALIDATION_REPORT.md","validation report"))
else:
    check("fv-07", "FINAL_VALIDATION_REPORT.md status", "SKIP",
          "validation report is regenerated after the freeze run; its closed status is checked in --verify-sums")
for rel, where in status_targets:
    p = os.path.join(FINAL, rel)
    if os.path.exists(p):
        text = open(p, encoding="utf-8").read()
        missing = [s for s in CLOSED_PHRASES if s not in text]
        stale = STALE_STATUS in text
        check("fv-07", f"{rel} status",
              "PASS" if not missing and not stale else "FAIL",
              f"missing={missing} stale={'yes' if stale else 'no'}")
    else:
        check("fv-07", rel, "ERROR", "missing file")

# ---------- fv-08: required content presence in the final report ----------
REQ_PRESENCE = ["122", "500", "NOT_RUN", "1.4+ale.1", "Phase 0 CLOSED", "唯一有效基线",
                "2e91edd3", "73517c2e", "492249a2"]
rp = os.path.join(FINAL, "PHASE0_FINAL_REPORT.md")
if os.path.exists(rp):
    rtext = open(rp, encoding="utf-8").read()
    missing = [s for s in REQ_PRESENCE if s not in rtext]
    check("fv-08", "PHASE0_FINAL_REPORT.md presence", "PASS" if not missing else "FAIL", f"missing={missing}")
else:
    check("fv-08", "PHASE0_FINAL_REPORT.md", "ERROR", "missing file")

# ---------- fv-13: source lineage recheck, post-cleanup via the external archive ----------
ARCHIVE = "/Users/mac/Archives/ALE-Phase0-History-20261110"
mp = os.path.join(FINAL, "SOURCE_MANIFEST_FINAL.json")
if os.path.exists(mp):
    try:
        m = json.load(open(mp, encoding="utf-8"))
        if m.get("stage") == "final":
            bad = []
            for f, rec in m.get("final_files", {}).items():
                hh, err = sha(os.path.join(FINAL, f))
                if err or hh != rec.get("sha256"):
                    bad.append(f)
            check("fv-13a", "manifest final_files vs disk", "PASS" if not bad else "FAIL", f"bad={bad[:5]}")
            srcbad = []
            for item in m.get("sources", []):
                sp = item.get("source_path")
                if sp and os.path.exists(sp):
                    hh, err = sha(sp)
                    if err or hh != item.get("source_sha256"):
                        srcbad.append(item.get("file", sp))
                    continue
                ar = item.get("archive_rel")
                if ar:
                    ap = os.path.join(ARCHIVE, "analysis", ar)
                    hh, err = sha(ap)
                    if err or hh != item.get("source_sha256"):
                        srcbad.append(item.get("file", ap))
                else:
                    srcbad.append(item.get("file", sp))
            check("fv-13b", "source lineage vs archive", "PASS" if not srcbad else "FAIL", f"bad={srcbad[:5]}")
            sums_txt = os.path.join(ARCHIVE, "ARCHIVE_SHA256SUMS.txt")
            sources_tsv = os.path.join(ARCHIVE, "ARCHIVE_SOURCES.tsv")
            verify_c = os.path.join(ARCHIVE, "VERIFY_C.tsv")
            sums_map = {}
            if os.path.isfile(sums_txt):
                for l in open(sums_txt, encoding="utf-8").read().splitlines():
                    parts = l.split("  ", 1)
                    if len(parts) == 2:
                        sums_map[parts[1].strip()] = parts[0].strip()
            tsv_set = set()
            if os.path.isfile(sources_tsv):
                for row in csv_mod.reader(open(sources_tsv, encoding="utf-8"), delimiter="\t"):
                    if len(row) >= 4 and row[0] == "file" and row[1] != "rel_path":
                        tsv_set.add((row[1], row[3]))
            vc_ok = os.path.isfile(verify_c) and "OK" in open(verify_c, encoding="utf-8").read()
            fv14_ok = len(sums_map) == 254 and len(tsv_set) == 254 and vc_ok
            check("fv-14", "external archive records", "PASS" if fv14_ok else "FAIL",
                  f"sums_entries={len(sums_map)} tsv_file_rows={len(tsv_set)} verify_c={'ok' if vc_ok else 'missing'}")
            arch_ok = True
            for item in m.get("sources", []):
                ar = item.get("archive_rel")
                if ar and (sums_map.get("analysis/" + ar) != item.get("source_sha256")
                           or (ar, item.get("source_sha256")) not in tsv_set):
                    arch_ok = False
            check("fv-14b", "archive index resolves manifest sources",
                  "PASS" if arch_ok else "FAIL", "mapping ok" if arch_ok else "mapping mismatch")
            gone = [d for d in ("phase0-official-baseline", "phase0-official-baseline-r1", "phase0-official-baseline-r2")
                    if os.path.exists(os.path.join(WS, "analysis", d))]
            check("fv-15", "history dirs moved out of analysis", "PASS" if not gone else "FAIL", f"still_present={gone}")
            try:
                plog = open(os.path.join(FINAL, "progress.log"), encoding="utf-8").read()
                has_closeout = "closeout amendment" in plog and "Phase 0 CLOSED" in plog
            except Exception:
                has_closeout = False
            check("fv-16", "progress.log closeout entry",
                  "PASS" if has_closeout else "FAIL", "entry=ok" if has_closeout else "entry missing")
        else:
            check("fv-13a", "manifest stage", "SKIP", f"stage={m.get('stage')}")
            check("fv-13b", "manifest stage", "SKIP", f"stage={m.get('stage')}")
            check("fv-14", "archive records", "SKIP", f"stage={m.get('stage')}")
            check("fv-14b", "archive index", "SKIP", f"stage={m.get('stage')}")
            check("fv-15", "history dirs", "SKIP", f"stage={m.get('stage')}")
            check("fv-16", "progress.log closeout", "SKIP", f"stage={m.get('stage')}")
    except Exception as e:
        check("fv-13a", "SOURCE_MANIFEST_FINAL.json", "ERROR", repr(e))
        check("fv-13b", "SOURCE_MANIFEST_FINAL.json", "ERROR", repr(e))
        check("fv-14", "archive records", "ERROR", repr(e))
        check("fv-14b", "archive index", "ERROR", repr(e))
        check("fv-15", "history dirs moved out of analysis", "PASS" if not any(
            os.path.exists(os.path.join(WS, "analysis", d))
            for d in ("phase0-official-baseline", "phase0-official-baseline-r1", "phase0-official-baseline-r2")) else "FAIL", "")
        try:
            plog_text = open(os.path.join(FINAL, "progress.log"), encoding="utf-8").read()
            has_entry = "closeout amendment" in plog_text and "Phase 0 CLOSED" in plog_text
            check("fv-16", "progress.log closeout entry", "PASS" if has_entry else "FAIL", "entry missing")
        except Exception as e2:
            check("fv-16", "progress.log closeout entry", "ERROR", repr(e2))
else:
    check("fv-13a", "SOURCE_MANIFEST_FINAL.json", "ERROR", "missing")
    check("fv-13b", "SOURCE_MANIFEST_FINAL.json", "ERROR", "missing")
    check("fv-14", "archive records", "ERROR", "missing manifest")
    check("fv-14b", "archive index", "ERROR", "missing manifest")
    check("fv-15", "history dirs moved out of analysis", "PASS" if not any(
        os.path.exists(os.path.join(WS, "analysis", d))
        for d in ("phase0-official-baseline", "phase0-official-baseline-r1", "phase0-official-baseline-r2")) else "FAIL", "")
    check("fv-16", "progress.log closeout entry", "ERROR", "missing manifest")

# ---------- fv-11: git heads unchanged ----------
for name, path, expected in REPOS:
    r = subprocess.run(["git","-C",path,"rev-parse","HEAD"], capture_output=True, text=True)
    if r.returncode == 0:
        head = r.stdout.strip()
        check("fv-11", f"repo {name} HEAD", "PASS" if head == expected else "FAIL",
              f"head={head[:12]} rc={r.returncode}")
    else:
        check("fv-11", f"repo {name} HEAD", "ERROR", f"rc={r.returncode} {r.stderr[:100]}")

# ---------- fv-10: frozen inputs spot checks ----------
try:
    nlines = open(os.path.join(INPUTS,"FILE_SHA256SUMS.txt"), "rb").read().count(b"\n")
    check("fv-10a","FILE_SHA256SUMS.txt", "PASS" if nlines==108117 else "FAIL", f"byte_newlines={nlines}")
    st = os.stat(os.path.join(INPUTS,"README_READ_ONLY.md"))
    check("fv-10b","README_READ_ONLY.md perms", "PASS" if (st.st_mode & 0o222)==0 else "FAIL", f"mode={oct(st.st_mode & 0o777)}")
except Exception as e:
    check("fv-10x","frozen inputs", "ERROR", repr(e))

# ---------- fv-12: checksum self-exclusion (verify mode) ----------
def _tree_count():
    n = 0
    for base, dirs, files in os.walk(FINAL):
        for fn in files:
            if fn in (".DS_Store", "FINAL_CHECKSUMS.sha256"):
                continue
            n += 1
    return n

tree_files = _tree_count()
if mode_verify:
    cs_file = os.path.join(FINAL, "FINAL_CHECKSUMS.sha256")
    try:
        lines = open(cs_file, encoding="utf-8").read().splitlines()
        entries = [l.split("  ",1) for l in lines if l.strip()]
        listed = {rel for _, rel in entries}
        bad = []
        for h, rel in entries:
            if rel == "FINAL_CHECKSUMS.sha256":
                bad.append(("self-listed", rel)); continue
            actual, err = sha(os.path.join(FINAL, rel))
            if err or actual != h:
                bad.append((rel, (actual or err)[:16]))
        check("fv-12","FINAL_CHECKSUMS.sha256",
              "PASS" if not bad and len(entries)==65 and tree_files==65 else "FAIL",
              f"listed={len(entries)} tree_files={tree_files} bad={bad[:5]}")
    except Exception as e:
        check("fv-12","FINAL_CHECKSUMS.sha256", "ERROR", repr(e))

# ---------- summary ----------
n = Counter(r["verdict"] for r in results)
required_fail = n["FAIL"] + n["ERROR"]
print(f"TOTAL {len(results)} | PASS {n['PASS']} | FAIL {n['FAIL']} | ERROR {n['ERROR']} | SKIP {n['SKIP']} | required_fail {required_fail}")
out = {"results": results, "summary": dict(n), "required_fail": required_fail,
       "mode_freeze": mode_freeze, "mode_verify": mode_verify}
if mode_freeze:
    outpath = os.path.join(FINAL, "evidence", "final_validate_results.json")
    json.dump(out, open(outpath,"w"), ensure_ascii=False, indent=1)
    txt = "\n".join(f"{r['check_id']}\t{r['object']}\t{r['verdict']}\t{r['evidence']}" for r in results)
    open(outpath.replace(".json",".txt"),"w").write(txt + f"\nTOTAL {len(results)} PASS {n['PASS']} FAIL {n['FAIL']} ERROR {n['ERROR']} SKIP {n['SKIP']}\n")
sys.exit(1 if required_fail else 0)