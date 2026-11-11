#!/usr/bin/env python3
"""Generate S1_01_RECLASSIFICATION_EVIDENCE.csv — per-task reclassification table.

One row per cross-domain reclassification (category != taxonomy.domain_code),
located by the task's REAL task_id (never a directory wildcard). Records the old
directory, current taxonomy, classifier.previous history, reclassification source
(task_all_workflows.csv), and whether a rationale field exists. The rationale field
is NOT copied; only its presence is recorded (it is absent on all 13 rows, so the
reclassification basis stays UNKNOWN).
"""
import json, os, csv

TASKS = "/Users/mac/Workspaces/ale-研究设计/agents-last-exam/tasks"
OUT = "/Users/mac/Workspaces/ale-研究设计/ale-500-category-research/S1_01_RECLASSIFICATION_EVIDENCE.csv"


def get_id(d, category):
    for k in ("taskId", "id", "task_id"):
        if k in d and d[k]:
            v = str(d[k])
            if not v.startswith(category):
                v = f"{category}/{v}"
            return v
    return f"{category}/UNKNOWN"


def main():
    cards = []
    for root, dirs, files in os.walk(TASKS):
        for fn in files:
            if fn == "task_card.json":
                cards.append(os.path.join(root, fn))
    cards.sort()

    rows = []
    for p in cards:
        d = json.load(open(p, encoding="utf-8"))
        cat = d.get("category", "")
        tax = d.get("taxonomy") or {}
        dom = tax.get("domain_code", "")
        if not cat or not dom or cat == dom:
            continue
        cl = tax.get("classifier") or {}
        prev = cl.get("previous") or {}
        rationale_present = "yes" if "rationale" in cl else "no"
        rel = os.path.relpath(p, TASKS)
        rows.append({
            "task_id": get_id(d, cat),
            "old_directory": cat,
            "current_domain_id": tax.get("domain_id", "UNKNOWN"),
            "current_domain_code": dom,
            "current_subdomain_id": tax.get("subdomain_id", "UNKNOWN"),
            "current_subdomain_code": tax.get("subdomain_code", "UNKNOWN"),
            "current_subdomain_name": tax.get("subdomain_name", "UNKNOWN"),
            "previous_domain_id": prev.get("domain_id", "UNKNOWN"),
            "previous_domain_code": prev.get("domain_code", "UNKNOWN"),
            "previous_subdomain_id": prev.get("subdomain_id", "UNKNOWN"),
            "previous_subdomain_code": prev.get("subdomain_code", "UNKNOWN"),
            "previous_subdomain_name": prev.get("subdomain_name", "UNKNOWN"),
            "reclassification_source": cl.get("source", "UNKNOWN"),
            "applied_at": cl.get("applied_at", "UNKNOWN"),
            "rationale_present": rationale_present,
            "task_card_path": f"agents-last-exam/tasks/{rel}",
        })

    cols = ["task_id", "old_directory", "current_domain_id", "current_domain_code",
            "current_subdomain_id", "current_subdomain_code", "current_subdomain_name",
            "previous_domain_id", "previous_domain_code", "previous_subdomain_id",
            "previous_subdomain_code", "previous_subdomain_name",
            "reclassification_source", "applied_at", "rationale_present",
            "task_card_path"]
    rows.sort(key=lambda r: r["task_id"])
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {len(rows)} reclassification rows -> {OUT}")
    for r in rows:
        print(f"  {r['task_id']}: {r['old_directory']} -> "
              f"{r['current_domain_code']}/{r['current_subdomain_code']} "
              f"(prev {r['previous_domain_code']}/{r['previous_subdomain_code']}, "
              f"rationale={r['rationale_present']})")


if __name__ == "__main__":
    main()
