#!/usr/bin/env python3
"""S1-01: extract official taxonomy structure from all physical task cards.
Read-only over agents-last-exam; writes nothing outside the research dir."""
import json, os, collections, csv, sys

ALE = "/Users/mac/Workspaces/ale-研究设计/agents-last-exam"
TASKS = os.path.join(ALE, "tasks")

def walk_cards(root):
    cards = []
    for dirpath, dirs, files in os.walk(root):
        if "task_card.json" in files:
            cards.append(os.path.join(dirpath, "task_card.json"))
    return sorted(cards)

cards = walk_cards(TASKS)

domains = {}        # domain_id -> domain_code
subdomains = {}     # (domain_id, subdomain_id) -> (subdomain_code, subdomain_name)
rows = []           # per-card rows
missing_taxonomy = []

for c in cards:
    rel = os.path.relpath(c, TASKS)          # e.g. business_finance/x/task_card.json
    category = rel.split(os.sep)[0]          # directory top-level
    task_id = os.path.dirname(rel)           # business_finance/x
    try:
        d = json.load(open(c))
    except Exception as e:
        rows.append(dict(task_id=task_id, category=category, err=f"parse:{e}"))
        continue
    tx = d.get("taxonomy")
    if not tx:
        missing_taxonomy.append(task_id)
        rows.append(dict(task_id=task_id, category=category,
                         dom_id=None, dom_code=None,
                         sub_id=None, sub_code=None, sub_name=None,
                         taxonomy_missing=True))
        continue
    dom_id = tx.get("domain_id"); dom_code = tx.get("domain_code")
    sub_id = tx.get("subdomain_id"); sub_code = tx.get("subdomain_code"); sub_name = tx.get("subdomain_name")
    if dom_id is not None and dom_code:
        domains[dom_id] = dom_code
    if dom_id is not None and sub_id is not None:
        subdomains[(dom_id, sub_id)] = (sub_code, sub_name)
    rows.append(dict(task_id=task_id, category=category,
                     dom_id=dom_id, dom_code=dom_code,
                     sub_id=sub_id, sub_code=sub_code, sub_name=sub_name,
                     taxonomy_missing=False))

# domain ordering by domain_id
dom_sorted = sorted(domains.items(), key=lambda kv: (str(kv[0]).zfill(3)))
sub_sorted = sorted(subdomains.items(), key=lambda kv: (str(kv[0][0]).zfill(3), str(kv[0][1])))

# category vs taxonomy mismatch
mismatch = [r for r in rows if (not r.get("taxonomy_missing") and r["dom_code"] and r["category"] != r["dom_code"])]

# write outputs
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidence")
with open(os.path.join(outdir, "taxonomy_domains.tsv"), "w") as f:
    f.write("domain_id\tdomain_code\n")
    for did, dc in dom_sorted:
        f.write(f"{did}\t{dc}\n")

with open(os.path.join(outdir, "taxonomy_subdomains.tsv"), "w") as f:
    f.write("domain_id\tdomain_code\tsubdomain_id\tsubdomain_code\tsubdomain_name\n")
    for (did, sid), (sc, sn) in sub_sorted:
        f.write(f"{did}\t{domains.get(did,'')}\t{sid}\t{sc}\t{sn}\n")

with open(os.path.join(outdir, "taxonomy_card_rows.tsv"), "w") as f:
    w = csv.DictWriter(f, fieldnames=["task_id","category","dom_id","dom_code","sub_id","sub_code","sub_name","taxonomy_missing"], delimiter="\t")
    w.writeheader()
    for r in sorted(rows, key=lambda x: x["task_id"]):
        w.writerow(r)

print(f"cards={len(cards)}  domains={len(dom_sorted)}  subdomains={len(sub_sorted)}  missing_taxonomy={len(missing_taxonomy)}  mismatch={len(mismatch)}")
print("\n=== DOMAINS (domain_id -> code) ===")
for did, dc in dom_sorted:
    print(f"  {did} -> {dc}")
print("\n=== SUBDOMAINS ===")
for (did, sid), (sc, sn) in sub_sorted:
    print(f"  {did}.{sid}  {sc}  :: {sn}")
print("\n=== CATEGORY != TAXONOMY.DOMAIN_CODE (reclassification) ===")
for r in mismatch:
    print(f"  {r['task_id']}: dir={r['category']}  taxonomy={r['dom_code']} ({r['dom_id']}) sub={r['sub_code']}")
if missing_taxonomy:
    print("\n=== CARDS WITHOUT taxonomy ===")
    for t in missing_taxonomy:
        print("  ", t)
