#!/usr/bin/env python3
"""C16 validator for the S1-02C-U1 uncovered_official propagation.

Sixteen checks. C16 owns the row-by-row claim this validator exists to prove:

    assignment.uncovered_official_flag == yes
        iff  S1_01_CATEGORY_MAPPING.coverage_status == uncovered_official
        for  the row's subdomain_code
        and  uncovered_official_basis is populated iff the flag is yes

C01-C15 watch the invariants the U1 revision must preserve. The self-test
mutations each corrupt one state and must fail the checks listed for them.
The 61-entry baseline immutability check is C08 and reports the hash-match
count it obtained.

Exit codes: 0 all checks pass, 1 at least one check failed, 2 bad usage.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent

MAPPING = 'S1_01_CATEGORY_MAPPING.csv'
ASSIGNMENT = 'S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv'
REGISTRY = 'S1_02C_WORKFLOW_FAMILY_REGISTRY.csv'
MATRIX = 'S1_02C_EXPERT_CAPABILITY_MATRIX.csv'
AUTH = 'S1_02C_AUTHORIZATION_RISK_REGISTER.csv'
ENG = 'S1_02C_ENGINEERING_RISK_REGISTER.csv'
STATS = Path('.audit') / 's1-02c-stats.json'
BASELINE = Path('.audit') / 's1-02c-baseline.sha256'

EXPECTED_ROWS = 174
EXPECTED_UNCOVERED = 22
EXPECTED_PER_CODE = {
    'chemical_process': 3,
    'mining_petroleum': 5,
    'precision_agriculture': 5,
    'aviation': 3,
    'maritime_port': 3,
    'educational_technology': 3,
}
EXPECTED_FAMILIES = 72
EXPECTED_GROUPS = 50
EXPECTED_AUTH_GROUPS = 9
EXPECTED_ENG_GROUPS = 7
EXPECTED_PADDING = 27
EXPECTED_PADDING_HIGH = 9
EXPECTED_EXPERT_PENDING = 9
EXPECTED_ENDORSEMENT = 45


def read_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as fh:
        return list(csv.DictReader(fh))


def yes(value):
    return (value or '').strip().lower().startswith('yes')


def load(root):
    ds = {'root': root}
    ds['mapping'] = read_csv(root / MAPPING)
    ds['assignment'] = read_csv(root / ASSIGNMENT)
    ds['registry'] = read_csv(root / REGISTRY)
    ds['matrix'] = read_csv(root / MATRIX)
    ds['auth'] = read_csv(root / AUTH)
    ds['eng'] = read_csv(root / ENG)
    ds['stats'] = json.loads((root / STATS).read_text(encoding='utf-8'))
    return ds


# --------------------------------------------------------------------------
# checks. Each returns (problems, notes).

def check_c01_rows(ds, root):
    problems = []
    rows = ds['assignment']
    if len(rows) != EXPECTED_ROWS:
        problems.append('assignment rows %d != %d' % (len(rows), EXPECTED_ROWS))
    ids = [(r.get('candidate_id') or '').strip() for r in rows]
    dup = sorted(c for c, n in Counter(ids).items() if n > 1)
    if dup:
        problems.append('duplicate candidate_id %s' % dup[:8])
    return problems, ['rows %d' % len(rows)]


def check_c02_uncovered_totals(ds, root):
    problems = []
    rows = ds['assignment']
    total = sum(1 for r in rows if yes(r.get('uncovered_official_flag')))
    if total != EXPECTED_UNCOVERED:
        problems.append('uncovered_official total %d != %d' % (total, EXPECTED_UNCOVERED))
    per = Counter((r.get('subdomain_code') or '').strip() for r in rows
                  if yes(r.get('uncovered_official_flag')))
    if set(per) != set(EXPECTED_PER_CODE):
        problems.append('uncovered subdomains %s != %s' % (sorted(per), sorted(EXPECTED_PER_CODE)))
    for code, want in EXPECTED_PER_CODE.items():
        if per.get(code, 0) != want:
            problems.append('uncovered %s count %d != %d' % (code, per.get(code, 0), want))
    return problems, ['uncovered %d' % total]


def check_c03_registry_family_counts(ds, root):
    problems = []
    by_family = Counter()
    for r in ds['assignment']:
        if yes(r.get('uncovered_official_flag')):
            by_family[(r.get('workflow_family_id') or '').strip()] += 1
    for r in ds['registry']:
        fid = (r.get('workflow_family_id') or '').strip()
        got = int(r.get('uncovered_official_count', '0') or 0)
        want = by_family.get(fid, 0)
        if got != want:
            problems.append('%s uncovered_official_count %d != %d' % (fid, got, want))
    return problems, []


def check_c04_matrix_group_counts(ds, root):
    problems = []
    by_group = Counter()
    for r in ds['assignment']:
        if yes(r.get('uncovered_official_flag')):
            by_group[(r.get('expert_capability_group_id') or '').strip()] += 1
    for r in ds['matrix']:
        gid = (r.get('expert_capability_group_id') or '').strip()
        got = int(r.get('uncovered_official_count', '0') or 0)
        want = by_group.get(gid, 0)
        if got != want:
            problems.append('%s uncovered_official_count %d != %d' % (gid, got, want))
    return problems, []


def check_c05_registry_total(ds, root):
    problems = []
    got = sum(int(r.get('uncovered_official_count', '0') or 0) for r in ds['registry'])
    if got != EXPECTED_UNCOVERED:
        problems.append('registry uncovered_official_count sum %d != %d' % (got, EXPECTED_UNCOVERED))
    return problems, ['registry sum %d' % got]


def check_c06_matrix_total(ds, root):
    problems = []
    got = sum(int(r.get('uncovered_official_count', '0') or 0) for r in ds['matrix'])
    if got != EXPECTED_UNCOVERED:
        problems.append('matrix uncovered_official_count sum %d != %d' % (got, EXPECTED_UNCOVERED))
    return problems, ['matrix sum %d' % got]


def check_c07_stats(ds, root):
    problems = []
    stats = ds['stats']
    if stats.get('total_candidates') != EXPECTED_ROWS:
        problems.append('stats total_candidates %r != %d' % (stats.get('total_candidates'), EXPECTED_ROWS))
    flags = stats.get('flags', {})
    if flags.get('uncovered_official') != EXPECTED_UNCOVERED:
        problems.append('stats flags.uncovered_official %r != %d'
                        % (flags.get('uncovered_official'), EXPECTED_UNCOVERED))
    ids = stats.get('uncovered_candidates', [])
    if len(ids) != EXPECTED_UNCOVERED:
        problems.append('stats uncovered_candidates length %d != %d' % (len(ids), EXPECTED_UNCOVERED))
    per = stats.get('uncovered_by_subdomain', {})
    for code, want in EXPECTED_PER_CODE.items():
        if per.get(code, 0) != want:
            problems.append('stats uncovered_by_subdomain %s %r != %d'
                            % (code, per.get(code, 0), want))
    return problems, []


def check_c08_baseline_immutability(ds, root):
    problems = []
    manifest = root / BASELINE
    if not manifest.is_file():
        return ['missing %s' % BASELINE.as_posix()], []
    recorded = {}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            problems.append('manifest line unparseable: %r' % line.strip()[:80])
            continue
        recorded[os.path.normpath(parts[1].strip())] = parts[0].strip().lower()
    matched = 0
    for rel, digest in recorded.items():
        target = root / rel
        if not target.is_file():
            problems.append('%s missing' % rel)
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            problems.append('%s sha256 %s != recorded %s' % (rel, actual[:16], digest[:16]))
        else:
            matched += 1
    if len(recorded) != 61:
        problems.append('manifest entries %d != 61' % len(recorded))
    return problems, ['%d/61 hash-match' % matched]


def check_c09_manifest_self_reference(ds, root):
    problems = []
    manifest_rel = os.path.normpath(BASELINE.as_posix())
    for line in (root / BASELINE).read_text(encoding='utf-8').splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2 and os.path.normpath(parts[1].strip()) == manifest_rel:
            problems.append('manifest lists itself at %s' % BASELINE.as_posix())
    return problems, []


def check_c10_structural_totals(ds, root):
    problems = []
    if len(ds['registry']) != EXPECTED_FAMILIES:
        problems.append('registry rows %d != %d' % (len(ds['registry']), EXPECTED_FAMILIES))
    if len(ds['matrix']) != EXPECTED_GROUPS:
        problems.append('matrix rows %d != %d' % (len(ds['matrix']), EXPECTED_GROUPS))
    if len(ds['auth']) != EXPECTED_AUTH_GROUPS:
        problems.append('auth rows %d != %d' % (len(ds['auth']), EXPECTED_AUTH_GROUPS))
    if len(ds['eng']) != EXPECTED_ENG_GROUPS:
        problems.append('eng rows %d != %d' % (len(ds['eng']), EXPECTED_ENG_GROUPS))
    fams = {(r.get('workflow_family_id') or '').strip() for r in ds['assignment']}
    if len(fams) != EXPECTED_FAMILIES:
        problems.append('assignment distinct families %d != %d' % (len(fams), EXPECTED_FAMILIES))
    groups = {(r.get('expert_capability_group_id') or '').strip() for r in ds['assignment']}
    if len(groups) != EXPECTED_GROUPS:
        problems.append('assignment distinct groups %d != %d' % (len(groups), EXPECTED_GROUPS))
    return problems, ['families %d groups %d auth %d eng %d'
                      % (len(fams), len(groups), len(ds['auth']), len(ds['eng']))]


def check_c11_padding(ds, root):
    problems = []
    rows = ds['assignment']
    pad = [r for r in rows if yes(r.get('padding_risk_flag'))]
    if len(pad) != EXPECTED_PADDING:
        problems.append('padding_risk_flag yes %d != %d' % (len(pad), EXPECTED_PADDING))
    outside = [r.get('candidate_id') for r in pad if (r.get('source_batch') or '').strip() != 'B3']
    if outside:
        problems.append('padding_risk outside B3 %s' % outside[:8])
    high = sum(1 for r in pad if (r.get('padding_risk_severity') or '').strip() == 'high')
    if high != EXPECTED_PADDING_HIGH:
        problems.append('padding_risk high %d != %d' % (high, EXPECTED_PADDING_HIGH))
    return problems, ['padding %d' % len(pad)]


def check_c12_expert_pending(ds, root):
    problems = []
    rows = ds['assignment']
    pending = [r for r in rows if (r.get('expert_pending') or '').strip()]
    if len(pending) != EXPECTED_EXPERT_PENDING:
        problems.append('expert_pending populated %d != %d' % (len(pending), EXPECTED_EXPERT_PENDING))
    non_a = [r.get('candidate_id') for r in pending if (r.get('source_batch') or '').strip() != 'A']
    if non_a:
        problems.append('expert_pending outside A %s' % non_a[:8])
    return problems, []


def check_c13_registry_membership(ds, root):
    problems = []
    assigned = {(r.get('candidate_id') or '').strip() for r in ds['assignment']}
    listed = set()
    for r in ds['registry']:
        for cid in (r.get('primary_candidate_ids') or '').replace(';', ' ').split():
            listed.add(cid.strip())
        for cid in (r.get('secondary_candidate_ids') or '').replace(';', ' ').split():
            listed.add(cid.strip())
    if listed != assigned:
        problems.append('registry listed ids and assignment ids differ '
                        '(only in assignment %s, only in registry %s)'
                        % (sorted(assigned - listed)[:8], sorted(listed - assigned)[:8]))
    total = sum(int(r.get('primary_candidate_count', '0') or 0) for r in ds['registry'])
    if total != EXPECTED_ROWS:
        problems.append('registry primary totals %d != %d' % (total, EXPECTED_ROWS))
    return problems, ['listed %d' % len(listed)]


def check_c14_matrix_membership(ds, root):
    problems = []
    assigned = {(r.get('candidate_id') or '').strip() for r in ds['assignment']}
    listed = set()
    for r in ds['matrix']:
        for cid in (r.get('candidate_ids') or '').replace(';', ' ').split():
            listed.add(cid.strip())
    if listed != assigned:
        problems.append('matrix listed ids and assignment ids differ '
                        '(only in assignment %s, only in matrix %s)'
                        % (sorted(assigned - listed)[:8], sorted(listed - assigned)[:8]))
    total = sum(int(r.get('primary_candidate_count', '0') or 0) for r in ds['matrix'])
    if total != EXPECTED_ROWS:
        problems.append('matrix primary totals %d != %d' % (total, EXPECTED_ROWS))
    return problems, ['listed %d' % len(listed)]


def check_c15_flag_preservation(ds, root):
    problems = []
    rows = ds['assignment']
    linux = sum(1 for r in rows if yes(r.get('linux_not_verified_flag')))
    if linux != EXPECTED_ROWS:
        problems.append('linux_not_verified_flag yes %d != %d' % (linux, EXPECTED_ROWS))
    pending = sum(1 for r in rows if yes(r.get('engineering_pending_flag')))
    if pending != 83:
        problems.append('engineering_pending_flag yes %d != 83' % pending)
    endorse = sum(1 for r in rows if yes(r.get('expert_endorsement_required')))
    if endorse != EXPECTED_ENDORSEMENT:
        problems.append('expert_endorsement_required yes %d != %d' % (endorse, EXPECTED_ENDORSEMENT))
    return problems, []


def check_c16_rowwise(ds, root):
    problems = []
    status_by_code = {}
    for r in ds['mapping']:
        code = (r.get('subdomain_code') or '').strip()
        status_by_code[code] = (r.get('coverage_status') or '').strip()
    for row in ds['assignment']:
        cid = (row.get('candidate_id') or '').strip()
        code = (row.get('subdomain_code') or '').strip()
        raw = (row.get('uncovered_official_flag') or '').strip()
        if raw not in ('yes', 'no'):
            problems.append('%s: uncovered_official_flag=%r is not exactly yes or no'
                            % (cid, raw if raw else '<empty>'))
            continue
        flag = raw
        expected = 'yes' if status_by_code.get(code) == 'uncovered_official' else 'no'
        if code not in status_by_code:
            problems.append('%s: subdomain_code %r absent from %s' % (cid, code, MAPPING))
            continue
        if flag != expected:
            problems.append('%s: subdomain %s flag=%s but %s coverage_status=%s'
                            % (cid, code, flag, MAPPING, status_by_code[code]))
        basis = (row.get('uncovered_official_basis') or '').strip()
        if flag == 'yes' and not basis:
            problems.append('%s: flag=yes but uncovered_official_basis empty' % cid)
        if flag == 'no' and basis:
            problems.append('%s: flag=no but uncovered_official_basis set' % cid)
    return problems, ['%d rows compared' % len(ds['assignment'])]


CHECKS = (
    ('C01', 'assignment rows and primary key', check_c01_rows),
    ('C02', 'uncovered total and per-subdomain shape', check_c02_uncovered_totals),
    ('C03', 'registry per-family uncovered counts', check_c03_registry_family_counts),
    ('C04', 'matrix per-group uncovered counts', check_c04_matrix_group_counts),
    ('C05', 'registry uncovered total', check_c05_registry_total),
    ('C06', 'matrix uncovered total', check_c06_matrix_total),
    ('C07', 'stats uncovered fields', check_c07_stats),
    ('C08', 'historical immutability vs the 61-entry baseline', check_c08_baseline_immutability),
    ('C09', 'baseline manifest does not list itself', check_c09_manifest_self_reference),
    ('C10', 'family, group, auth, eng row counts', check_c10_structural_totals),
    ('C11', 'padding risk count', check_c11_padding),
    ('C12', 'expert pending count', check_c12_expert_pending),
    ('C13', 'registry membership and primary totals', check_c13_registry_membership),
    ('C14', 'matrix membership and primary totals', check_c14_matrix_membership),
    ('C15', 'linux, engineering pending, endorsement flags preserved', check_c15_flag_preservation),
    ('C16', 'flag equals mapping coverage_status row by row', check_c16_rowwise),
)


class Result(object):
    def __init__(self, cid):
        self.cid = cid
        self.problems = []
        self.notes = []

    @property
    def ok(self):
        return not self.problems


def run_all(root, ds=None):
    if ds is None:
        ds = load(root)
    results = []
    for cid, title, fn in CHECKS:
        result = Result(cid)
        try:
            result.problems, result.notes = fn(ds, root)
        except Exception as exc:
            result.problems = ['raised %s: %s' % (type(exc).__name__, exc)]
        results.append(result)
    return results


def print_report(results):
    for result in results:
        tail = ('  ' + '; '.join(result.notes)) if result.ok and result.notes else ''
        print('%s %s%s' % ('PASS' if result.ok else 'FAIL', result.cid, tail))
        for problem in result.problems[:20]:
            print('     ! %s' % problem)
        if len(result.problems) > 20:
            print('     ! ... %d more problem(s)' % (len(result.problems) - 20))
    failed = [r.cid for r in results if not r.ok]
    print('%d checks, %d failed%s' % (len(results), len(failed),
                                     (': ' + ', '.join(failed)) if failed else ''))


# --------------------------------------------------------------------------
# self-test. Each mutation must fail the checks named for it.


def _fixture_paths(root):
    paths = [MAPPING, ASSIGNMENT, REGISTRY, MATRIX, AUTH, ENG, STATS.as_posix(),
             BASELINE.as_posix()]
    for line in (root / BASELINE).read_text(encoding='utf-8').splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            rel = os.path.normpath(parts[1].strip())
            if rel != os.path.normpath(BASELINE.as_posix()):
                paths.append(rel)
    return sorted(set(paths))


def build_fixture(source_root, target_root):
    for rel in _fixture_paths(source_root):
        dst = target_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_root / rel, dst)


def _read(path):
    with open(path, newline='', encoding='utf-8-sig') as fh:
        return list(csv.DictReader(fh))


def _write(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def mut_a_yes_to_no(root):
    rows = _read(root / ASSIGNMENT)
    for r in rows:
        if yes(r.get('uncovered_official_flag')) and (r.get('source_batch') or '').strip() == 'A':
            r['uncovered_official_flag'] = 'no'
            break
    _write(root / ASSIGNMENT, rows)


def mut_b3_yes_to_no(root):
    rows = _read(root / ASSIGNMENT)
    for r in rows:
        if yes(r.get('uncovered_official_flag')) and (r.get('source_batch') or '').strip() == 'B3':
            r['uncovered_official_flag'] = 'no'
            break
    _write(root / ASSIGNMENT, rows)


def mut_nonuncovered_to_yes(root):
    rows = _read(root / ASSIGNMENT)
    for r in rows:
        if not yes(r.get('uncovered_official_flag')):
            r['uncovered_official_flag'] = 'yes'
            break
    _write(root / ASSIGNMENT, rows)


def mut_nonuncovered_no_to_maybe(root):
    rows = _read(root / ASSIGNMENT)
    for r in rows:
        if (r.get('uncovered_official_flag') or '').strip() == 'no':
            r['uncovered_official_flag'] = 'maybe'
            break
    _write(root / ASSIGNMENT, rows)


def mut_uncovered_yes_to_yesterday(root):
    rows = _read(root / ASSIGNMENT)
    for r in rows:
        if (r.get('uncovered_official_flag') or '').strip() == 'yes':
            r['uncovered_official_flag'] = 'yesterday'
            break
    _write(root / ASSIGNMENT, rows)


def mut_delete_row(root):
    rows = _read(root / ASSIGNMENT)
    rows.pop()
    _write(root / ASSIGNMENT, rows)


def mut_registry_count(root):
    rows = _read(root / REGISTRY)
    rows[0]['uncovered_official_count'] = str(int(rows[0]['uncovered_official_count'] or 0) + 1)
    _write(root / REGISTRY, rows)


def mut_matrix_count(root):
    rows = _read(root / MATRIX)
    rows[0]['uncovered_official_count'] = str(int(rows[0]['uncovered_official_count'] or 0) + 1)
    _write(root / MATRIX, rows)


def mut_stats_total(root):
    stats = json.loads((root / STATS).read_text(encoding='utf-8'))
    stats['flags']['uncovered_official'] += 1
    (root / STATS).write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')


def mut_history_hash(root):
    with open(root / '.audit' / 's1-02b3.tsv', 'a', encoding='utf-8') as fh:
        fh.write('\n')


def mut_manifest_self(root):
    with open(root / BASELINE, 'a', encoding='utf-8') as fh:
        fh.write('%s  ./.audit/s1-02c-baseline.sha256\n' % ('0' * 64))


def mut_family_count(root):
    rows = _read(root / ASSIGNMENT)
    rows[0]['workflow_family_id'] = 'WF-NOT-REAL'
    _write(root / ASSIGNMENT, rows)


def mut_padding_count(root):
    rows = _read(root / ASSIGNMENT)
    for r in rows:
        if yes(r.get('padding_risk_flag')):
            r['padding_risk_flag'] = 'no'
            break
    _write(root / ASSIGNMENT, rows)


SELF_TEST_CASES = (
    ('A yes to no', mut_a_yes_to_no, {'C02', 'C03', 'C04', 'C16'}),
    ('B3 yes to no', mut_b3_yes_to_no, {'C02', 'C03', 'C04', 'C16'}),
    ('non-uncovered to yes', mut_nonuncovered_to_yes, {'C02', 'C03', 'C04', 'C16'}),
    ('non-uncovered no to maybe', mut_nonuncovered_no_to_maybe, {'C16'}),
    ('uncovered yes to yesterday', mut_uncovered_yes_to_yesterday, {'C16'}),
    ('deleted assignment row', mut_delete_row, {'C01', 'C11', 'C13', 'C14', 'C15'}),
    ('registry count bumped', mut_registry_count, {'C03', 'C05'}),
    ('matrix count bumped', mut_matrix_count, {'C04', 'C06'}),
    ('stats total bumped', mut_stats_total, {'C07'}),
    ('tampered historical file', mut_history_hash, {'C08'}),
    ('manifest lists itself', mut_manifest_self, {'C08', 'C09'}),
    ('family id injected', mut_family_count, {'C10'}),
    ('padding count dropped', mut_padding_count, {'C11'}),
)


def run_self_test():
    source_root = DEFAULT_ROOT
    failures = []
    issue = unit_case(source_root)
    if issue:
        failures.append(issue)
    print('self-test: mutated copies under the system temp directory, never in the workspace')
    for name, mutate, expected in SELF_TEST_CASES:
        with tempfile.TemporaryDirectory(prefix='s1-02c-c16-selftest-') as tmp:
            root = Path(tmp)
            build_fixture(source_root, root)
            mutate(root)
            results = run_all(root)
            failed = {r.cid for r in results if not r.ok}
            if failed != expected:
                failures.append('%s: expected %s but observed %s' % (name, sorted(expected), sorted(failed)))
                print('FAIL %-24s expected %s observed %s' % (name, sorted(expected), sorted(failed)))
            else:
                print('PASS %-24s caught by %s' % (name, ', '.join(sorted(failed))))
    if failures:
        print('self-test FAILED: %d mutation(s) escaped' % len(failures))
        return 1
    print('self-test passed: %d mutations caught, pristine control green' % len(SELF_TEST_CASES))
    return 0


def unit_case(root):
    results = run_all(root)
    broken = [r.cid for r in results if not r.ok]
    if broken:
        print('FAIL control (pristine copy) unexpected failures: %s' % broken)
        return 'control broken: %s' % broken
    print('PASS control (pristine copy) all 16 checks pass')
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description='C16 validator for S1-02C uncovered propagation.')
    parser.add_argument('--root', default=str(DEFAULT_ROOT), help='repository root to validate')
    parser.add_argument('--self-test', action='store_true',
                        help='mutate throwaway copies in a temp dir and require the matching check to fail')
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test()
    root = Path(args.root).resolve()
    try:
        ds = load(root)
    except Exception as exc:
        print('FATAL could not load inputs: %s: %s' % (type(exc).__name__, exc))
        return 1
    results = run_all(root, ds)
    print_report(results)
    return 0 if all(r.ok for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())