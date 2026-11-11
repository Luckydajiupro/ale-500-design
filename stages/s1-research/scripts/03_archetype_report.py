#!/usr/bin/env python3
"""Print a per-subdomain archetype aggregation report to guide hand-writing."""
import csv, json, collections

pub = set(json.load(open('/Users/mac/Workspaces/ale-研究设计/agents-last-exam/tasks/published_tasks.json'))['published'].keys())
rows = [r for r in csv.DictReader(open('evidence/task_archetype_rows.tsv'), delimiter='\t') if r['task_id'] in pub]
g = collections.defaultdict(list)
for r in rows:
    if r['domain_code'] == 'UNKNOWN':
        continue
    g[(r['domain_code'], r['subdomain_code'])].append(r)

for (dom, sub), rs in sorted(g.items()):
    sw = set()
    for r in rs:
        for x in r['software'].split(';'):
            if x:
                sw.add(x)
    ver = collections.Counter()
    osc = collections.Counter()
    mt = set()
    for r in rs:
        if r['r1_verifier_type']:
            ver[r['r1_verifier_type']] += 1
        if r['r1_os_linux'] == 'yes':
            osc['linux'] += 1
        if r['r1_os_windows'] == 'yes':
            osc['win'] += 1
        if r['vm_machineType'] != 'UNKNOWN':
            mt.add(r['vm_machineType'])
    subs = [r['summary'][:85] for r in rs]
    print(f"## {dom}/{sub}  ({len(rs)} tasks)  ver={dict(ver)}  os={dict(osc)}  mt={sorted(mt)}")
    print("   sw:", '; '.join(sorted(sw)[:14]) or '(none)')
    for s in subs[:3]:
        print("   -", s)
    if len(rs) > 3:
        print(f"   ... (+{len(rs)-3} more)")
    print()
