#!/usr/bin/env python3
"""Extract per-task archetype evidence from task_card.json into a TSV.

Reads all 135 task_card.json under agents-last-exam/tasks/ and joins R1's
04_task_inventory.csv (for verifier_type, input_style, gui_status, os flags,
external_service, software_versions). Outputs evidence/task_archetype_rows.tsv.

This only extracts *metadata and structure* (field names, counts, short summary,
software list, VM machineType, evaluation type and hardGates presence/type only).
It never copies taskPrompt, agentMustDo, reference, or scoring content (hardGates
rules, evaluation bodies) into the research output.
"""
import json, os, csv, sys, collections

TASKS_DIR = "/Users/mac/Workspaces/ale-研究设计/agents-last-exam/tasks"
INV_CSV = "/Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108/analysis/phase0-official-baseline-r1/04_task_inventory.csv"
OUT = "/Users/mac/Workspaces/ale-研究设计/ale-500-category-research/evidence/task_archetype_rows.tsv"


def get_id(d, category):
    for k in ("taskId", "id", "task_id"):
        if k in d and d[k]:
            v = str(d[k])
            if not v.startswith(category):
                v = f"{category}/{v}"
            return v
    return f"{category}/UNKNOWN"


def first_ok(d, *keys):
    for k in keys:
        if k in d and d[k]:
            return d[k]
    return None


def load_inventory():
    rows = {}
    with open(INV_CSV, encoding="utf-8") as f:
        # skip the leading '# 注 note:' comment line
        lines = f.read().splitlines()
    data_lines = [l for l in lines if not l.startswith("#")]
    reader = csv.DictReader(data_lines)
    for r in reader:
        tid = r.get("task_id", "")
        rows[tid] = r
    return rows


def main():
    inv = load_inventory()
    cards = []
    for root, dirs, files in os.walk(TASKS_DIR):
        for fn in files:
            if fn == "task_card.json":
                cards.append(os.path.join(root, fn))
    cards.sort()

    out_rows = []
    for p in cards:
        d = json.load(open(p, encoding="utf-8"))
        cat = d.get("category", "")
        tid = get_id(d, cat)
        tax = d.get("taxonomy") or {}
        dom = tax.get("domain_code", "UNKNOWN")
        sub = tax.get("subdomain_code", "UNKNOWN")
        sub_name = tax.get("subdomain_name", "UNKNOWN")

        inv_row = inv.get(tid, {})

        # software list (dedup, sorted)
        sw = d.get("software") or []
        sw = sorted({str(x) for x in sw}) if isinstance(sw, list) else []

        # system packages
        sp = d.get("requiredSystemPackages") or []
        sp = sorted({str(x) for x in sp}) if isinstance(sp, list) else []

        # evaluation type + hard gates (presence and JSON type only; never the gate content)
        ev = d.get("evaluation") or {}
        ev_type = ev.get("type", "UNKNOWN") if isinstance(ev, dict) else "UNKNOWN"
        if isinstance(ev, dict) and "hardGates" in ev:
            hg_raw = ev.get("hardGates")
            hg_present = "yes"
            if isinstance(hg_raw, list):
                hg_type = "list"
            elif isinstance(hg_raw, str):
                hg_type = "str"
            else:
                hg_type = "other"
        else:
            hg_present = "no"
            hg_type = "absent"

        # deliverable contracts
        oc = d.get("outputContracts") or d.get("output_contract") or d.get("outputs")
        oc_names = []
        if isinstance(oc, list):
            for o in oc:
                if isinstance(o, dict):
                    oc_names.append(o.get("name") or o.get("id") or str(o)[:60])
                else:
                    oc_names.append(str(o)[:60])
        elif isinstance(oc, dict):
            oc_names = list(oc.keys())

        # input / reference file names (names only, not content)
        inf = d.get("inputFiles") or []
        rff = d.get("referenceFiles") or []
        inf_names = []
        rff_names = []
        if isinstance(inf, list):
            for x in inf:
                if isinstance(x, dict):
                    inf_names.append(x.get("name") or x.get("path") or str(x)[:60])
                else:
                    inf_names.append(str(x)[:60])
        if isinstance(rff, list):
            for x in rff:
                if isinstance(x, dict):
                    rff_names.append(x.get("name") or x.get("path") or str(x)[:60])
                else:
                    rff_names.append(str(x)[:60])

        vm = d.get("vm") or {}
        mt = vm.get("machineType", "UNKNOWN") if isinstance(vm, dict) else "UNKNOWN"
        snap = vm.get("snapshot", "UNKNOWN") if isinstance(vm, dict) else "UNKNOWN"

        summary = (d.get("summary") or "").strip().replace("\t", " ").replace("\n", " ")
        title = (d.get("title") or first_ok(d, "taskName", "task_name") or "").strip()

        out_rows.append({
            "task_id": tid,
            "category": cat,
            "domain_code": dom,
            "subdomain_code": sub,
            "subdomain_name": sub_name,
            "title": title,
            "summary": summary,
            "software": ";".join(sw),
            "system_packages": ";".join(sp),
            "vm_machineType": mt,
            "vm_snapshot": snap,
            "eval_type": ev_type,
            "eval_hardGates_present": hg_present,
            "eval_hardGates_type": hg_type,
            "output_contracts": ";".join(oc_names),
            "input_file_names": ";".join(inf_names),
            "reference_file_names": ";".join(rff_names),
            "has_agentMustDo": "yes" if d.get("agentMustDo") else "no",
            "has_taskPrompt": "yes" if d.get("taskPrompt") else "no",
            "r1_verifier_type": inv_row.get("verifier_type", ""),
            "r1_input_style": inv_row.get("input_style", ""),
            "r1_gui_status": inv_row.get("gui_status", ""),
            "r1_os_linux": inv_row.get("os_linux", ""),
            "r1_os_windows": inv_row.get("os_windows", ""),
            "r1_external_service": inv_row.get("external_service", ""),
        })

    cols = ["task_id", "category", "domain_code", "subdomain_code", "subdomain_name",
            "title", "summary", "software", "system_packages", "vm_machineType",
            "vm_snapshot", "eval_type", "eval_hardGates_present", "eval_hardGates_type",
            "output_contracts",
            "input_file_names", "reference_file_names", "has_agentMustDo",
            "has_taskPrompt", "r1_verifier_type", "r1_input_style", "r1_gui_status",
            "r1_os_linux", "r1_os_windows", "r1_external_service"]
    with open(OUT, "w", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print(f"wrote {len(out_rows)} rows -> {OUT}")
    # quick per-domain/subdomain distribution
    dist = collections.Counter((r["domain_code"], r["subdomain_code"]) for r in out_rows)
    for (dom, sub), c in sorted(dist.items()):
        print(f"{dom}/{sub}: {c}")


if __name__ == "__main__":
    main()
