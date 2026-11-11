# -*- coding: utf-8 -*-
"""S1-02C 构建器：把 174 条只读候选归并到统一任务族，并做风险收敛标记。

只读取既有批次交付物，只写 S1_02C_* 新文件与 .audit/ 下的工作产物；
不修改 Phase 0 final、A、B1、B2、B2-effective、B3 的任何文件。
"""
import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import s1_02c_spec as S
from s1_02c_taxonomy import CAPABILITY_DOMAINS, ECGS, FAMILIES

FAM = {f[0]: f for f in FAMILIES}
ECG = {e[0]: e for e in ECGS}

SEV_ORDER = {"low": 1, "low_medium": 2, "medium": 3, "high": 4}
NEG = re.compile(r"(not required|not needed|no gpu|无\s*gpu|not applicable)", re.I)


def path(name):
    return os.path.join(ROOT, name)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(name):
    with open(path(name), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(name, fieldnames, rows):
    with open(path(name), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def natural_key(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def ids_from(text):
    return re.findall(r"[a-z][a-z0-9_]*_wf\d+", text or "")


def one_line(text, limit=None):
    t = re.sub(r"\s+", " ", (text or "")).strip()
    if limit and len(t) > limit:
        t = t[: limit - 1] + "…"
    return t


# ------------------------------------------------------------------ 读取输入
records = []
for batch, eff_file, orig_file, claim_file, dup_file in S.BATCHES:
    effective = read_csv(eff_file)
    original = {r["candidate_id"]: r for r in read_csv(orig_file)} if batch == "A" else {}
    for r in effective:
        records.append({"batch": batch, "eff": r, "orig": original.get(r["candidate_id"], r)})
records.sort(key=lambda x: (["A", "B1", "B2", "B3"].index(x["batch"]), natural_key(x["eff"]["candidate_id"])))
assert len(records) == 174, len(records)

claims = {}
for batch, eff_file, orig_file, claim_file, dup_file in S.BATCHES:
    for r in read_csv(claim_file):
        claims[(batch, r["candidate_id"])] = r

# S1-02C-U1 修订：uncovered_official 唯一依据是 S1_01_CATEGORY_MAPPING.csv
# 的 coverage_status。构建器在逐条计算前把整个 mapping 读入内存，并对
# subdomain_code 缺失或重复一律报错，宁死不默认成 no。
_mapping_rows = read_csv("S1_01_CATEGORY_MAPPING.csv")
MAPPING_COVERAGE = {}
for _mr in _mapping_rows:
    _code = (_mr.get("subdomain_code") or "").strip()
    if not _code:
        raise SystemExit("S1_01_CATEGORY_MAPPING.csv: subdomain_code 为空的行")
    if _code in MAPPING_COVERAGE:
        raise SystemExit(f"S1_01_CATEGORY_MAPPING.csv: subdomain_code 重复 {_code!r}")
    _status = (_mr.get("coverage_status") or "").strip()
    MAPPING_COVERAGE[_code] = {
        "status": _status,
        "domain": (_mr.get("domain_code") or "").strip(),
        "name": (_mr.get("subdomain_name") or "").strip(),
    }


def coverage_of(code):
    code = (code or "").strip()
    if code not in MAPPING_COVERAGE:
        raise SystemExit(f"assignment candidate subdomain_code 未在 mapping 中找到: {code!r}")
    return MAPPING_COVERAGE[code]


def uncovered_basis(code, info):
    code = (code or "").strip()
    return (f"S1_01_CATEGORY_MAPPING.csv: {code} coverage_status={info['status']}, "
            f"official_domain={info['domain']}, subdomain_name={info['name']}")


def parse_pairs():
    out = []
    for batch, eff_file, orig_file, claim_file, dup_file in S.BATCHES:
        for i, r in enumerate(read_csv(dup_file), 1):
            ids = ids_from(r["candidates"])
            assert len(ids) == 2, (batch, r["pair"], ids)
            primary = ""
            m = re.search(r"\(([a-z][a-z0-9_]*_wf\d+)\)", r.get("primary_home", ""))
            if m:
                primary = m.group(1)
            out.append({
                "pair_id": f"DP-{batch}-{i:02d}",
                "batch": batch,
                "pair_title": r["pair"],
                "candidates": ids,
                "substantively_duplicate": (r.get("substantively_duplicate") or "").strip().lower(),
                "primary_home": r.get("primary_home", ""),
                "primary_candidate": primary,
                "primary_reason": r.get("primary_reason", ""),
                "secondary_tag": r.get("secondary_tag", ""),
                "difference_basis": r.get("difference_basis", ""),
                "pending": r.get("pending", ""),
            })
    return out


PAIRS = parse_pairs()
PAIR_BY_ID = defaultdict(list)
for p in PAIRS:
    for cid in p["candidates"]:
        PAIR_BY_ID[cid].append(p)

CLUSTER_BY_ID = {}
for c in S.CLUSTERS:
    for cid in c["members"]:
        CLUSTER_BY_ID[cid] = c


# ------------------------------------------------------------------ 逐条计算
def family_for(cid):
    if cid in S.ID_OVERRIDE:
        return S.ID_OVERRIDE[cid], "id_override"
    prefix = re.sub(r"_wf\d+$", "", cid)
    return S.PREFIX_DEFAULT[prefix], "prefix_default"


def risk_text(rec, kind):
    src = rec["orig"]
    if kind == "AUTH":
        fields = S.AUTH_FIELDS_A if rec["batch"] == "A" else S.AUTH_FIELDS_BCD
    else:
        fields = ["platform_dependencies", "blocking_risks",
                  "verification_approach", "reproducibility_assessment"]
    return " ;; ".join((src.get(k) or "") for k in fields)


def group_hits(rec, groups):
    hits = []
    for g in groups:
        gid, patterns = g[0], g[5]
        text = risk_text(rec, "AUTH" if gid.startswith("AUTH") else "ENG")
        if patterns == ["__ALL__"]:
            hits.append(gid)
            continue
        if patterns == ["__PENDING__"]:
            if (rec["eff"].get("engineering_pending") or "").strip().lower().startswith("yes"):
                hits.append(gid)
            continue
        if patterns == ["__PROVENANCE__"]:
            if rec["batch"] == "B3" or (rec["eff"].get("process_incident") or "none") not in ("none", ""):
                hits.append(gid)
            continue
        found = False
        for p in patterns:
            for m in re.finditer(p, text, re.I):
                if gid == "ENG-03" and NEG.search(text[max(0, m.start() - 30): m.end() + 30]):
                    continue
                found = True
                break
            if found:
                break
        if found:
            hits.append(gid)
    return hits


def snippet(rec, gid):
    g = next(x for x in S.AUTH_GROUPS + S.ENG_GROUPS if x[0] == gid)
    text = risk_text(rec, "AUTH" if gid.startswith("AUTH") else "ENG")
    for p in g[5]:
        if p.startswith("__"):
            continue
        m = re.search(p, text, re.I)
        if m:
            s = max(0, m.start() - 40)
            e = min(len(text), m.end() + 80)
            return "…" + one_line(text[s:e], 170)
    return ""


def max_sev(gids):
    if not gids:
        return "none_screened"
    groups = {g[0]: g for g in S.AUTH_GROUPS + S.ENG_GROUPS}
    return max((groups[g][3] for g in gids), key=lambda s: SEV_ORDER[s])


def evidence_class(level, mode):
    if level == "E1":
        if mode == "recorded_full_support":
            return 1
        if mode in ("recorded_partial_support", "not_recorded_in_batch"):
            return 2
        return 3
    if level == "E3":
        if mode in ("recorded_full_support", "recorded_partial_support", "not_recorded_in_batch"):
            return 4
        return 5
    if level == "E4":
        return 6
    raise ValueError(f"unexpected evidence_level {level!r}")


assignment = []
for rec in records:
    eff, orig, batch = rec["eff"], rec["orig"], rec["batch"]
    cid = eff["candidate_id"]
    fam_id, basis = family_for(cid)
    assert fam_id in FAM, (cid, fam_id)
    secondary = S.SECONDARY.get(cid, [])
    assert all(f in FAM for f in secondary), (cid, secondary)

    level = (eff.get("evidence_level") or "").strip()
    mode = (eff.get("source_support_mode") or "").strip()
    if batch == "B2" and cid in S.B2_CORRECTED:
        mode = S.B2_CORRECTED[cid]
        mode_status = "corrected_by_erratum"
    elif mode:
        mode_status = "recorded"
    else:
        mode = "not_recorded_in_batch"
        mode_status = "not_recorded_in_batch"

    cls = evidence_class(level, mode)
    auth_hits = group_hits(rec, S.AUTH_GROUPS)
    eng_hits = group_hits(rec, S.ENG_GROUPS)
    auth_hits = [g for g in auth_hits if g not in S.AUTH_REMOVE.get(cid, [])] + \
                [g for g in S.AUTH_ADD.get(cid, []) if g not in auth_hits]
    eng_hits = [g for g in eng_hits if g not in S.ENG_REMOVE.get(cid, [])] + \
               [g for g in S.ENG_ADD.get(cid, []) if g not in eng_hits]

    claim = claims.get((batch, cid))
    claim_status = "missing"
    if claim:
        claim_status = "match" if (claim.get("source_url") or "") == (eff.get("primary_source_url") or "") else "url_mismatch"

    cluster = CLUSTER_BY_ID.get(cid)
    if cluster:
        role = "primary" if cluster["primary"] == cid else "secondary"
        cluster_id = cluster["cluster_id"]
    else:
        role = "no_duplicate_member" if PAIR_BY_ID.get(cid) else "none"
        cluster_id = ""

    pair_ids = [p["pair_id"] for p in PAIR_BY_ID.get(cid, [])]
    if pair_ids:
        basis_parts = []
        for p in PAIR_BY_ID[cid]:
            verdict = "YES" if p["substantively_duplicate"] == "yes" else "no"
            basis_parts.append(f"{p['pair_id']} {p['pair_title']}（{verdict}）")
        endorsement = "yes"
        endorsement_basis = "；".join(basis_parts) + "；裁定待专家背书"
    else:
        endorsement = "no"
        endorsement_basis = "未进入任何已登记重复对照"

    # S1-02C-U1 修订：uncovered_official_flag 由 mapping 的 coverage_status
    # 决定，不再限制 batch == B3。缺失或重复的 subdomain_code 会在
    # coverage_of 处抛错，绝不默认为 no。
    subdomain_code = (eff.get("subdomain_code") or "").strip()
    coverage_info = coverage_of(subdomain_code)
    uncovered = coverage_info["status"] == "uncovered_official"
    padding = batch == "B3"

    eng_pending_raw = (eff.get("engineering_pending") or "").strip()
    eng_pending_flag = "yes" if eng_pending_raw.lower().startswith("yes") else "no"

    notes = []
    if batch == "B2" and not (eff.get("workflow_family_id") or "").strip():
        notes.append("B2 先例：原始 workflow_family_id 为空（未登记），S1-02C 首次登记，不回填历史文件。")
    if mode_status == "corrected_by_erratum":
        notes.append("B2 erratum 更正行：source_support_mode 取最弱证据块。")
    if batch == "B3":
        notes.append("B3 行：参与 9×3 结构，padding 风险按批次统一登记。")
    if uncovered:
        notes.append("uncovered_official：该子领域在 S1-01 无活跃官方任务。")
    if cluster:
        notes.append(f"跨领域重复簇 {cluster['cluster_id']} 成员，主归属 {cluster['primary']}。")

    assignment.append({
        "candidate_id": cid,
        "source_batch": batch,
        "source_file": dict((b[0], b[1]) for b in S.BATCHES)[batch],
        "subdomain_code": eff.get("subdomain_code", ""),
        "workflow_title": eff.get("workflow_title", ""),
        "workflow_family_id": fam_id,
        "workflow_family_name_zh": FAM[fam_id][1],
        "family_membership_role": "primary",
        "secondary_workflow_family_ids": ";".join(secondary),
        "expert_capability_group_id": FAM[fam_id][6],
        "expert_capability_group_name_zh": ECG[FAM[fam_id][6]][1],
        "capability_domain": FAM[fam_id][3],
        "original_workflow_family_ids": (eff.get("workflow_family_id") or "").strip(),
        "original_family_registration_status": (
            "column_absent" if batch in ("A", "B1")
            else ("registered" if (eff.get("workflow_family_id") or "").strip() else "unregistered_empty")),
        "family_assignment_basis": basis + ("+secondary" if secondary else ""),
        "evidence_level": level,
        "evidence_kind": eff.get("evidence_kind", ""),
        "source_type": eff.get("source_type", ""),
        "source_category": eff.get("source_category", ""),
        "source_support_mode": mode,
        "source_support_mode_status": mode_status,
        "evidence_scope_present": "yes" if (eff.get("evidence_scope") or "").strip() else "no",
        "evidence_risk_class": cls,
        "evidence_risk_label": S.EVIDENCE_CLASS_LABEL[cls],
        "independent_verification_present": "no",
        "primary_source_url": eff.get("primary_source_url", ""),
        "source_claim_map_status": claim_status,
        "source_reference_or_fragment": eff.get("source_reference", "") or orig.get("source_reference", "") or eff.get("fragment_path", ""),
        "duplicate_status_original": eff.get("duplicate_status", ""),
        "duplicate_attribution_role": role,
        "duplicate_pair_ids": ";".join(pair_ids),
        "duplicate_cluster_id": cluster_id,
        "authorization_risk_group_ids": ";".join(auth_hits),
        "authorization_risk_group_count": len(auth_hits),
        "authorization_risk_level": max_sev(auth_hits),
        "authorization_field_coverage": "usage_permissions_only" if batch == "A" else "four_authorization_fields",
        "authorization_screening_note": (
            ("命中 " + ("/".join(auth_hits) if auth_hits else "无") + "；组级最高严重度=" + max_sev(auth_hits)
             + "；机械初筛，非法律意见。")
            + (" A 批次仅有 usage_permissions，隐私与伦理维度无法评估。" if batch == "A" else "")),
        "engineering_risk_group_ids": ";".join(eng_hits),
        "engineering_risk_group_count": len(eng_hits),
        "engineering_risk_level": max_sev(eng_hits),
        "engineering_screening_note": (
            "命中 " + ("/".join(eng_hits) if eng_hits else "无") + "；ENG-01 Linux NOT_VERIFIED 为全批共性。"),
        "linux_verification_state": eff.get("linux_verification_state", ""),
        "linux_not_verified_flag": "yes" if (eff.get("linux_verification_state") or "").upper() == "NOT_VERIFIED" else "no",
        "engineering_pending": eng_pending_raw,
        "engineering_pending_flag": eng_pending_flag,
        "expert_pending": (eff.get("expert_pending") or "").strip(),
        "expert_endorsement_required": endorsement,
        "expert_endorsement_basis": endorsement_basis,
        "uncovered_official_flag": "yes" if uncovered else "no",
        # basis 引用 S1-01 对应记录；未找到或重复的 subdomain_code 已在
        # coverage_of/MAPPING_COVERAGE 处抛错，不会到达这里。
        "uncovered_official_basis": (uncovered_basis(subdomain_code, coverage_info) if uncovered else ""),
        "padding_risk_flag": "yes" if padding else "no",
        "padding_risk_severity": ("high" if uncovered else "medium") if padding else "",
        "padding_risk_basis": S.PADDING_BASIS if padding else "",
        "process_incident": (eff.get("process_incident") or "").strip() or "not_applicable",
        "notes": " ".join(notes),
    })

ASSIGN_FIELDS = list(assignment[0].keys())

# ------------------------------------------------------------------ 族登记
registry = []
for fam in FAMILIES:
    fid = fam[0]
    prim = [a for a in assignment if a["workflow_family_id"] == fid]
    sec = [a for a in assignment if fid in a["secondary_workflow_family_ids"].split(";")]
    members = prim + sec
    batch_counts = Counter(a["source_batch"] for a in prim)
    all_batch_counts = Counter(a["source_batch"] for a in members)
    clusters = sorted({a["duplicate_cluster_id"] for a in prim if a["duplicate_cluster_id"]})
    prim_dups = sorted({a["candidate_id"] for a in prim if a["duplicate_attribution_role"] == "primary"})
    sec_dups = sorted({a["candidate_id"] for a in prim if a["duplicate_attribution_role"] == "secondary"})
    cls_dist = Counter(a["evidence_risk_class"] for a in prim)
    mode_dist = Counter(a["source_support_mode"] for a in prim)
    registry.append({
        "workflow_family_id": fid,
        "family_name_zh": fam[1],
        "family_name_en": fam[2],
        "capability_domain": fam[3],
        "expert_capability_group_id": fam[6],
        "definition": fam[4],
        "boundary_exclusion": fam[5],
        "primary_candidate_count": len(prim),
        "secondary_candidate_count": len(sec),
        "total_distinct_candidates": len(members),
        "count_A": batch_counts.get("A", 0),
        "count_B1": batch_counts.get("B1", 0),
        "count_B2": batch_counts.get("B2", 0),
        "count_B3": batch_counts.get("B3", 0),
        "batch_span": ";".join(b for b in ("A", "B1", "B2", "B3") if batch_counts.get(b)),
        "all_member_batch_span": ";".join(b for b in ("A", "B1", "B2", "B3") if all_batch_counts.get(b)),
        "cross_batch_flag": "yes" if len(all_batch_counts) > 1 else "no",
        "primary_candidate_ids": ";".join(a["candidate_id"] for a in prim),
        "secondary_candidate_ids": ";".join(a["candidate_id"] for a in sec),
        "subdomain_codes": ";".join(sorted({a["subdomain_code"] for a in members})),
        "duplicate_cluster_ids": ";".join(clusters),
        "duplicate_primary_candidate_ids": ";".join(prim_dups),
        "duplicate_secondary_candidate_ids": ";".join(sec_dups),
        "uncovered_official_count": sum(1 for a in prim if a["uncovered_official_flag"] == "yes"),
        "padding_risk_count": sum(1 for a in prim if a["padding_risk_flag"] == "yes"),
        "linux_not_verified_count": sum(1 for a in prim if a["linux_not_verified_flag"] == "yes"),
        "engineering_pending_count": sum(1 for a in prim if a["engineering_pending_flag"] == "yes"),
        "primary_evidence_class_distribution": ";".join(f"c{k}={v}" for k, v in sorted(cls_dist.items())),
        "primary_source_support_mode_distribution": ";".join(f"{k}={v}" for k, v in sorted(mode_dist.items())),
        "notes": "",
    })

REG_FIELDS = list(registry[0].keys())

# ------------------------------------------------------------------ 能力矩阵
matrix = []
for ecg in ECGS:
    eid = ecg[0]
    fams = [f for f in FAMILIES if f[6] == eid]
    fam_ids = [f[0] for f in fams]
    members = [a for a in assignment if a["workflow_family_id"] in fam_ids]
    sec = [a for a in assignment if set(a["secondary_workflow_family_ids"].split(";")) & set(fam_ids)]
    batch_counts = Counter(a["source_batch"] for a in members)
    cls_dist = Counter(a["evidence_risk_class"] for a in members)
    auth = sorted({g for a in members for g in a["authorization_risk_group_ids"].split(";") if g})
    eng = sorted({g for a in members for g in a["engineering_risk_group_ids"].split(";") if g})
    matrix.append({
        "expert_capability_group_id": eid,
        "name_zh": ecg[1],
        "name_en": ecg[2],
        "capability_domain": ecg[3],
        "definition": ecg[4],
        "typical_credentials": ecg[5],
        "workflow_family_ids": ";".join(fam_ids),
        "workflow_family_names_zh": ";".join(f[1] for f in fams),
        "primary_candidate_count": len(members),
        "secondary_membership_candidates": ";".join(a["candidate_id"] for a in sec),
        "count_A": batch_counts.get("A", 0),
        "count_B1": batch_counts.get("B1", 0),
        "count_B2": batch_counts.get("B2", 0),
        "count_B3": batch_counts.get("B3", 0),
        "candidate_ids": ";".join(a["candidate_id"] for a in members),
        "subdomain_codes": ";".join(sorted({a["subdomain_code"] for a in members})),
        "evidence_class_distribution": ";".join(f"c{k}={v}" for k, v in sorted(cls_dist.items())),
        "authorization_risk_group_ids": ";".join(auth),
        "engineering_risk_group_ids": ";".join(eng),
        "uncovered_official_count": sum(1 for a in members if a["uncovered_official_flag"] == "yes"),
        "padding_risk_count": sum(1 for a in members if a["padding_risk_flag"] == "yes"),
        "engineering_pending_count": sum(1 for a in members if a["engineering_pending_flag"] == "yes"),
        "review_question": "",
    })

MAT_FIELDS = list(matrix[0].keys())

# ------------------------------------------------------------------ 风险登记
def register_rows(groups, kind):
    out = []
    for g in groups:
        gid, zh, en, sev, definition, patterns, action, question = g
        hits = [a for a in assignment if gid in
                (a["authorization_risk_group_ids"] if kind == "AUTH" else a["engineering_risk_group_ids"]).split(";")]
        batch_counts = Counter(a["source_batch"] for a in hits)
        examples = " || ".join(f"{a['candidate_id']}: {snippet(rec_by_id[a['candidate_id']], gid)}" for a in hits[:3])
        out.append({
            "risk_group_id": gid,
            "name_zh": zh,
            "name_en": en,
            "severity": sev,
            "definition": definition,
            "screening_method": "中英双语正则初筛（字段拼接）+ 批次字段覆盖说明；命中不等于风险成立，未命中不等于已清权",
            "candidate_count": len(hits),
            "count_A": batch_counts.get("A", 0),
            "count_B1": batch_counts.get("B1", 0),
            "count_B2": batch_counts.get("B2", 0),
            "count_B3": batch_counts.get("B3", 0),
            "candidate_ids": ";".join(a["candidate_id"] for a in hits),
            "subdomain_codes": ";".join(sorted({a["subdomain_code"] for a in hits})),
            "example_basis": examples if examples else "无命中；该组保留为待核查面，不代表不存在风险",
            "required_to_clear": action,
            "expert_question": question,
            "status": "open_not_cleared",
            "notes": "",
        })
    return out


rec_by_id = {r["eff"]["candidate_id"]: r for r in records}
auth_rows = register_rows(S.AUTH_GROUPS, "AUTH")
eng_rows = register_rows(S.ENG_GROUPS, "ENG")
RISK_FIELDS = list(auth_rows[0].keys()) + ["linux_related"]

# linux_related 只对工程登记有意义，授权登记留空
for r in eng_rows:
    r["linux_related"] = "yes" if r["risk_group_id"] == "ENG-01" else "no"
for r in auth_rows:
    r["linux_related"] = ""

# ------------------------------------------------------------------ 输入哈希核对
baseline = {}
bpath = os.path.join(ROOT, ".audit", "s1-02c-baseline.sha256")
if os.path.exists(bpath):
    for line in open(bpath, encoding="utf-8"):
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            baseline[parts[1].lstrip("./")] = parts[0]

input_files = []
for batch, eff_file, orig_file, claim_file, dup_file in S.BATCHES:
    input_files.append(eff_file)
    if orig_file != eff_file:
        input_files.append(orig_file)
    input_files.append(claim_file)
    input_files.append(dup_file)
input_files = sorted(set(input_files))

verify = []
for f in input_files:
    cur = sha256_file(path(f))
    base = baseline.get(f, "")
    verify.append({
        "path": f,
        "baseline_sha256": base,
        "current_sha256": cur,
        "status": "match" if base == cur else ("missing_baseline" if not base else "changed"),
    })
assert all(v["status"] != "changed" for v in verify), "input file changed since baseline"

# ------------------------------------------------------------------ 写文件
write_csv("S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv", ASSIGN_FIELDS, assignment)
write_csv("S1_02C_WORKFLOW_FAMILY_REGISTRY.csv", REG_FIELDS, registry)
write_csv("S1_02C_EXPERT_CAPABILITY_MATRIX.csv", MAT_FIELDS, matrix)
write_csv("S1_02C_AUTHORIZATION_RISK_REGISTER.csv", RISK_FIELDS, auth_rows)
write_csv("S1_02C_ENGINEERING_RISK_REGISTER.csv", RISK_FIELDS, eng_rows)

verify_path = os.path.join(ROOT, ".audit", "s1-02c-input-verification.csv")
with open(verify_path, "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["path", "baseline_sha256", "current_sha256", "status"])
    w.writeheader()
    w.writerows(verify)

# ------------------------------------------------------------------ 统计
stats = {
    "total_candidates": len(assignment),
    "by_batch": dict(Counter(a["source_batch"] for a in assignment)),
    "evidence_level": dict(Counter(a["evidence_level"] for a in assignment)),
    "evidence_class": dict(Counter(a["evidence_risk_class"] for a in assignment)),
    "source_support_mode": dict(Counter(a["source_support_mode"] for a in assignment)),
    "mode_status": dict(Counter(a["source_support_mode_status"] for a in assignment)),
    "families": len(FAMILIES),
    "families_used": sum(1 for r in registry if r["primary_candidate_count"] > 0),
    "family_size_distribution": dict(Counter(r["primary_candidate_count"] for r in registry)),
    "singleton_families": [r["workflow_family_id"] for r in registry if r["primary_candidate_count"] == 1],
    "cross_batch_families": [
        {"family": r["workflow_family_id"], "batches": r["all_member_batch_span"],
         "primary_counts": [r["count_A"], r["count_B1"], r["count_B2"], r["count_B3"]],
         "secondary_candidates": r["secondary_candidate_ids"]}
        for r in registry if r["cross_batch_flag"] == "yes"
    ],
    "ecgs": len(ECGS),
    "ecgs_used": sum(1 for m in matrix if m["primary_candidate_count"] > 0),
    "auth_groups": {r["risk_group_id"]: r["candidate_count"] for r in auth_rows},
    "eng_groups": {r["risk_group_id"]: r["candidate_count"] for r in eng_rows},
    "flags": {
        "linux_not_verified": sum(1 for a in assignment if a["linux_not_verified_flag"] == "yes"),
        "engineering_pending": sum(1 for a in assignment if a["engineering_pending_flag"] == "yes"),
        "uncovered_official": sum(1 for a in assignment if a["uncovered_official_flag"] == "yes"),
        "padding_risk": sum(1 for a in assignment if a["padding_risk_flag"] == "yes"),
        "padding_risk_high": sum(1 for a in assignment if a["padding_risk_severity"] == "high"),
        "expert_endorsement_required": sum(1 for a in assignment if a["expert_endorsement_required"] == "yes"),
        "expert_pending": sum(1 for a in assignment if a["expert_pending"]),
    },
    "engineering_pending_by_batch": dict(Counter(a["source_batch"] for a in assignment if a["engineering_pending_flag"] == "yes")),
    "uncovered_candidates": [a["candidate_id"] for a in assignment if a["uncovered_official_flag"] == "yes"],
    "uncovered_by_subdomain": dict(Counter(a["subdomain_code"] for a in assignment if a["uncovered_official_flag"] == "yes")),
    "padding_by_batch": dict(Counter(a["source_batch"] for a in assignment if a["padding_risk_flag"] == "yes")),
    "auth_field_coverage": dict(Counter(a["authorization_field_coverage"] for a in assignment)),
    "b2_empty_original_family": sum(1 for a in assignment if a["original_family_registration_status"] == "unregistered_empty"),
    # S1-02C-U1 修订：原键名 b2_registered_original_family 有误导性，
    # 它统计的是全体 174 条中 registered 的行数（B2 5 + B3 27 = 32），
    # 而不是 B2 单独的 32 条。改为明确的键名与按批拆分。
    "registered_original_family_rows": sum(1 for a in assignment if a["original_family_registration_status"] == "registered"),
    "registered_original_family_by_batch": dict(Counter(
        a["source_batch"] for a in assignment
        if a["original_family_registration_status"] == "registered")),
    "claim_map_status": dict(Counter(a["source_claim_map_status"] for a in assignment)),
    "duplicate_pairs": [
        {"pair_id": p["pair_id"], "batch": p["batch"], "title": p["pair_title"],
         "candidates": p["candidates"], "verdict": p["substantively_duplicate"],
         "primary": p["primary_candidate"]}
        for p in PAIRS
    ],
    "duplicate_pair_count": len(PAIRS),
    "duplicate_pair_slots": sum(len(p["candidates"]) for p in PAIRS),
    "distinct_candidates_in_pairs": sum(1 for a in assignment if a["duplicate_pair_ids"]),
    "duplicate_yes": sum(1 for p in PAIRS if p["substantively_duplicate"] == "yes"),
    "duplicate_no": sum(1 for p in PAIRS if p["substantively_duplicate"] == "no"),
    "clusters": S.CLUSTERS,
    "family_role_counts": dict(Counter(a["family_membership_role"] for a in assignment)),
    "secondary_memberships": [(a["candidate_id"], a["secondary_workflow_family_ids"])
                              for a in assignment if a["secondary_workflow_family_ids"]],
    "risk_levels_auth": dict(Counter(a["authorization_risk_level"] for a in assignment)),
    "risk_levels_eng": dict(Counter(a["engineering_risk_level"] for a in assignment)),
    "families_with_uncovered": [r["workflow_family_id"] for r in registry if r["uncovered_official_count"]],
    "families_with_padding": [r["workflow_family_id"] for r in registry if r["padding_risk_count"]],
    "b3_provenance": S.B3_PROVENANCE,
    "batch_subdomains": {
        b: sorted({r["eff"].get("subdomain_code", "") for r in records if r["batch"] == b})
        for b in ("A", "B1", "B2", "B3")
    },
}
with open(os.path.join(ROOT, ".audit", "s1-02c-stats.json"), "w", encoding="utf-8") as fh:
    json.dump(stats, fh, ensure_ascii=False, indent=2)

print("assignment", len(assignment))
print("registry", len(registry), "used", stats["families_used"])
print("matrix", len(matrix), "used", stats["ecgs_used"])
print("auth", len(auth_rows), "eng", len(eng_rows))
print("flags", stats["flags"])
print("family sizes", stats["family_size_distribution"])
print("cross-batch", stats["cross_batch_families"])
print("input verify", Counter(v["status"] for v in verify))