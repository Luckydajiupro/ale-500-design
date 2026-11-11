#!/usr/bin/env python3
"""Independent validator for the five S1-02C deliverables.

Every number is re-derived from the read-only S1-02A/B1/B2/B3 batches, the four
SOURCE_CLAIM_MAP files, the four DUPLICATE_ATTRIBUTION files, and the frozen
hash baseline. scripts/34_build_s1_02c.py is never imported or executed, so a
bug in the builder cannot hide itself from this script.

REVISION U1 (2026-11-10, recorded by S1-02C-U1 recovery): check_10
uncovered_official expectations changed from 9 (B3 only) to 22 (A 13 + B3 9),
per .audit/s1-02c-uncovered-correction.md and the truth source
S1_01_CATEGORY_MAPPING.csv. This is a count revision only. The row-by-row
mapping proof (C16) lives in scripts/36_validate_s1_02c_c16.py and is not
implemented here.

Exit codes: 0 all checks pass, 1 at least one check failed, 2 bad usage.
    13|"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent

DELIVERABLES = {
    'assignment': 'S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv',
    'registry': 'S1_02C_WORKFLOW_FAMILY_REGISTRY.csv',
    'matrix': 'S1_02C_EXPERT_CAPABILITY_MATRIX.csv',
    'auth': 'S1_02C_AUTHORIZATION_RISK_REGISTER.csv',
    'eng': 'S1_02C_ENGINEERING_RISK_REGISTER.csv',
}
EXPECTED_ROWS = {'assignment': 174, 'registry': 72, 'matrix': 50, 'auth': 9, 'eng': 7}
PRIMARY_KEYS = {
    'assignment': 'candidate_id',
    'registry': 'workflow_family_id',
    'matrix': 'expert_capability_group_id',
    'auth': 'risk_group_id',
    'eng': 'risk_group_id',
}
ID_COLUMNS = {
    'assignment': 'candidate_id',
    'registry': 'workflow_family_id',
    'matrix': 'expert_capability_group_id',
    'auth': 'risk_group_id',
    'eng': 'risk_group_id',
}

BATCHES = ('A', 'B1', 'B2', 'B3')
SOURCES = {
    'A': ('S1_02A_EFFECTIVE_CANDIDATES.csv', 51),
    'B1': ('S1_02B1_WORKFLOW_CANDIDATES.csv', 57),
    'B2': ('S1_02B2_EFFECTIVE_CANDIDATES.csv', 39),
    'B3': ('S1_02B3_WORKFLOW_CANDIDATES.csv', 27),
}
A_ORIGINAL = 'S1_02A_WORKFLOW_CANDIDATES.csv'
CLAIM_MAPS = {
    'A': 'S1_02A_SOURCE_CLAIM_MAP.csv',
    'B1': 'S1_02B1_SOURCE_CLAIM_MAP.csv',
    'B2': 'S1_02B2_SOURCE_CLAIM_MAP.csv',
    'B3': 'S1_02B3_SOURCE_CLAIM_MAP.csv',
}
DUPLICATE_FILES = {
    'A': 'S1_02A_DUPLICATE_ATTRIBUTION.csv',
    'B1': 'S1_02B1_DUPLICATE_ATTRIBUTION.csv',
    'B2': 'S1_02B2_DUPLICATE_ATTRIBUTION.csv',
    'B3': 'S1_02B3_DUPLICATE_ATTRIBUTION.csv',
}
ERRATUM_DOC = 'S1_02B2_EVIDENCE_SCOPE_ERRATUM.md'
BASELINE = Path('.audit') / 's1-02c-baseline.sha256'
LOG_PATH = Path('.audit') / 's1-02c-validator.log'

FORBIDDEN_TOKENS = ('配额', 'quota', 'headcount', '招募', 'recruit')
URL_RE = re.compile(r'https?://\S+|www\.\S+')
TITLE_RE = re.compile(r'《[^》]*》')
PAIR_ID_RE = re.compile(r'DP-[A-Z0-9]+-\d{2}')
PRIMARY_HOME_RE = re.compile(r'\(([^()]+)\)\s*$')

EXPECTED_ENGINEERING_PENDING = {'A': 21, 'B1': 25, 'B2': 15, 'B3': 22}
# REVISION U1: propagation from B3-only to all six uncovered_official subdomains.
# A rows carry chemical_process 3 + mining_petroleum 5 + precision_agriculture 5.
EXPECTED_UNCOVERED_COUNT = 22
EXPECTED_UNCOVERED_BATCHES = {'A', 'B3'}
EXPECTED_UNCOVERED_SUBDOMAINS = {
    'chemical_process', 'mining_petroleum', 'precision_agriculture',
    'aviation', 'maritime_port', 'educational_technology',
}
EXPECTED_UNCOVERED_PER_CODE = {
    'chemical_process': 3,
    'mining_petroleum': 5,
    'precision_agriculture': 5,
    'aviation': 3,
    'maritime_port': 3,
    'educational_technology': 3,
}


# --------------------------------------------------------------------------
# loading helpers


def read_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as fh:
        return list(csv.DictReader(fh))


def split_ids(value):
    return [part.strip() for part in re.split(r'[;,]', value or '') if part.strip()]


def yes(value):
    return (value or '').strip().lower().startswith('yes')


def to_int(value, problems, where):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        problems.append('%s: not an integer (%r)' % (where, value))
        return None


def load_dataset(root):
    root = Path(root)
    ds = {'root': root}
    for key, name in DELIVERABLES.items():
        ds[key] = read_csv(root / name)
    ds['source'] = {}
    ds['source_by_id'] = {}
    for batch, (name, _expected) in SOURCES.items():
        rows = read_csv(root / name)
        ds['source'][batch] = rows
        ds['source_by_id'][batch] = {r.get('candidate_id'): r for r in rows}
    ds['a_original'] = read_csv(root / A_ORIGINAL)
    ds['claim_maps'] = {b: read_csv(root / name) for b, name in CLAIM_MAPS.items()}
    ds['duplicates'] = {b: read_csv(root / name) for b, name in DUPLICATE_FILES.items()}
    erratum_path = root / ERRATUM_DOC
    ds['erratum_text'] = erratum_path.read_text(encoding='utf-8') if erratum_path.is_file() else ''
    return ds


# --------------------------------------------------------------------------
# checks. Each returns (problems, notes).


def check_01(ds, root):
    problems, notes = [], []
    shapes = []
    for key in ('assignment', 'registry', 'matrix', 'auth', 'eng'):
        rows = ds[key]
        shapes.append(str(len(rows)))
        if len(rows) != EXPECTED_ROWS[key]:
            problems.append('%s holds %d rows, expected %d' % (DELIVERABLES[key], len(rows), EXPECTED_ROWS[key]))
    for key in ('assignment', 'registry', 'matrix', 'auth', 'eng'):
        column = PRIMARY_KEYS[key]
        rows = ds[key]
        blanks = [i + 2 for i, row in enumerate(rows) if not (row.get(column) or '').strip()]
        if blanks:
            problems.append('%s: blank %s at record(s) %s' % (DELIVERABLES[key], column, blanks[:10]))
        counts = Counter((row.get(column) or '').strip() for row in rows)
        duplicated = sorted(key_ for key_, n in counts.items() if n > 1)
        if duplicated:
            problems.append('%s: duplicated %s %s' % (DELIVERABLES[key], column, duplicated[:10]))
    notes.append('rows %s for assignment/registry/matrix/auth/eng; all primary keys unique' % '/'.join(shapes))
    return problems, notes


def check_02(ds, root):
    problems, notes = [], []
    assignment = ds['assignment']
    batch_counts = Counter((r.get('source_batch') or '').strip() for r in assignment)
    for batch in BATCHES:
        expected = SOURCES[batch][1]
        if batch_counts.get(batch, 0) != expected:
            problems.append('source_batch %s holds %d rows, expected %d' % (batch, batch_counts.get(batch, 0), expected))
    unknown = sorted(set(batch_counts) - set(BATCHES))
    if unknown:
        problems.append('unexpected source_batch value(s): %s' % unknown)

    seen = Counter((r.get('candidate_id') or '').strip() for r in assignment)
    repeated = sorted(k for k, n in seen.items() if n > 1)
    if repeated:
        problems.append('candidate_id repeated in assignment: %s' % repeated[:10])

    union = set()
    for batch in BATCHES:
        source_ids = set(ds['source_by_id'][batch])
        union |= source_ids
        assigned = {(r.get('candidate_id') or '').strip() for r in assignment if (r.get('source_batch') or '').strip() == batch}
        missing = sorted(source_ids - assigned)
        extra = sorted(assigned - source_ids)
        if missing:
            problems.append('batch %s: %d source candidate(s) absent from assignment: %s' % (batch, len(missing), missing[:8]))
        if extra:
            problems.append('batch %s: %d assignment id(s) not in source: %s' % (batch, len(extra), extra[:8]))
    assigned_all = {(r.get('candidate_id') or '').strip() for r in assignment}
    if assigned_all != union:
        problems.append('assignment id set != union of the four source files (missing %s, extra %s)'
                        % (sorted(union - assigned_all)[:8], sorted(assigned_all - union)[:8]))

    source_file_by_batch = {b: SOURCES[b][0] for b in BATCHES}
    for row in assignment:
        cid = (row.get('candidate_id') or '').strip()
        batch = (row.get('source_batch') or '').strip()
        if batch not in BATCHES:
            problems.append('%s: unknown source_batch %r' % (cid, batch))
            continue
        expected_file = source_file_by_batch[batch]
        if (row.get('source_file') or '').strip() != expected_file:
            problems.append('%s: source_file %r != %r' % (cid, (row.get('source_file') or '').strip(), expected_file))
        source_row = ds['source_by_id'][batch].get(cid)
        if source_row is None:
            problems.append('%s: not present in %s' % (cid, expected_file))
            continue
        for column in ('subdomain_code', 'workflow_title'):
            got = (row.get(column) or '').strip()
            want = (source_row.get(column) or '').strip()
            if got != want:
                problems.append('%s: %s %r != source %r' % (cid, column, got, want))

    a_original_ids = {(r.get('candidate_id') or '').strip() for r in ds['a_original']}
    a_effective_ids = set(ds['source_by_id']['A'])
    if a_original_ids != a_effective_ids:
        problems.append('S1_02A effective view id set != the 51 original candidates (sym diff %s)'
                        % sorted(a_original_ids ^ a_effective_ids)[:8])

    notes.append('A/B1/B2/B3 = %d/%d/%d/%d; union 174 == assignment; source_file, subdomain_code and workflow_title match origin rows'
                 % tuple(batch_counts.get(b, 0) for b in BATCHES))
    return problems, notes


def check_03(ds, root):
    problems, notes = [], []
    for row in ds['assignment']:
        cid = (row.get('candidate_id') or '').strip()
        batch = (row.get('source_batch') or '').strip()
        source_row = ds['source_by_id'].get(batch, {}).get(cid)
        if source_row is None:
            problems.append('%s: no source row to compare evidence fields' % cid)
            continue
        for column in ('evidence_level', 'evidence_kind'):
            got = (row.get(column) or '').strip()
            want = (source_row.get(column) or '').strip()
            if got != want:
                problems.append('%s: %s %r != source %r' % (cid, column, got, want))
    levels = Counter((r.get('evidence_level') or '').strip() for r in ds['assignment'])
    notes.append('evidence_level/evidence_kind identical to source on 174 rows; levels %s'
                 % ', '.join('%s=%d' % kv for kv in sorted(levels.items())))
    return problems, notes


def check_04(ds, root):
    problems, notes = [], []
    erratum_rows = []
    recorded = 0
    for row in ds['assignment']:
        cid = (row.get('candidate_id') or '').strip()
        batch = (row.get('source_batch') or '').strip()
        mode = (row.get('source_support_mode') or '').strip()
        status = (row.get('source_support_mode_status') or '').strip()
        if batch in ('A', 'B1'):
            if mode != 'not_recorded_in_batch':
                problems.append('%s: %s source_support_mode %r, expected not_recorded_in_batch' % (cid, batch, mode))
            if status != 'not_recorded_in_batch':
                problems.append('%s: %s source_support_mode_status %r, expected not_recorded_in_batch' % (cid, batch, status))
            continue
        source_row = ds['source_by_id'].get(batch, {}).get(cid)
        if source_row is None:
            problems.append('%s: no %s source row for source_support_mode' % (cid, batch))
            continue
        want = (source_row.get('source_support_mode') or '').strip()
        if mode != want:
            problems.append('%s: source_support_mode %r != source %r' % (cid, mode, want))
        if status == 'recorded':
            recorded += 1
        elif status == 'corrected_by_erratum':
            erratum_rows.append(cid)
            if batch != 'B2':
                problems.append('%s: corrected_by_erratum outside B2 (%s)' % (cid, batch))
        else:
            problems.append('%s: unexpected source_support_mode_status %r' % (cid, status))

    if len(erratum_rows) != 5:
        problems.append('%d rows carry corrected_by_erratum, expected exactly 5' % len(erratum_rows))
    missing_from_doc = [cid for cid in erratum_rows if cid not in ds['erratum_text']]
    if missing_from_doc:
        problems.append('erratum-marked rows absent from %s: %s' % (ERRATUM_DOC, missing_from_doc))

    notes.append('A/B1 not_recorded_in_batch 108 rows; B2/B3 recorded %d rows; corrected_by_erratum %d rows (%s)'
                 % (recorded, len(erratum_rows), ', '.join(sorted(erratum_rows))))
    return problems, notes


def risk_class(level, mode):
    if level == 'E4':
        return '6'
    if level == 'E1':
        if mode == 'recorded_full_support':
            return '1'
        if mode in ('recorded_partial_support', 'not_recorded_in_batch'):
            return '2'
        return '3'
    if level == 'E3':
        if mode in ('recorded_full_support', 'recorded_partial_support', 'not_recorded_in_batch'):
            return '4'
        return '5'
    return None


def check_05(ds, root):
    problems, notes = [], []
    for row in ds['assignment']:
        cid = (row.get('candidate_id') or '').strip()
        level = (row.get('evidence_level') or '').strip()
        mode = (row.get('source_support_mode') or '').strip()
        stored = (row.get('evidence_risk_class') or '').strip()
        derived = risk_class(level, mode)
        if derived is None:
            problems.append('%s: evidence_level %r is outside E1/E3/E4' % (cid, level))
            continue
        if stored != derived:
            problems.append('%s: evidence_risk_class %r but (%s, %s) recomputes to %r' % (cid, stored, level, mode, derived))
        verified = (row.get('independent_verification_present') or '').strip()
        if verified != 'no':
            problems.append('%s: independent_verification_present %r, expected no' % (cid, verified))
    distribution = Counter((r.get('evidence_risk_class') or '').strip() for r in ds['assignment'])
    notes.append('risk class recomputed from (level, mode) on 174 rows; %s; independent_verification_present=no on all 174'
                 % ', '.join('%s=%d' % kv for kv in sorted(distribution.items())))
    return problems, notes


def check_06(ds, root):
    problems, notes = [], []
    allowed = {'column_absent', 'registered', 'unregistered_empty'}
    status_counts = Counter()
    for row in ds['assignment']:
        cid = (row.get('candidate_id') or '').strip()
        batch = (row.get('source_batch') or '').strip()
        original = (row.get('original_workflow_family_ids') or '').strip()
        status = (row.get('original_family_registration_status') or '').strip()
        if status not in allowed:
            problems.append('%s: original_family_registration_status %r outside %s' % (cid, status, sorted(allowed)))
        if batch in ('A', 'B1'):
            if original:
                problems.append('%s: %s row carries original_workflow_family_ids %r, expected empty' % (cid, batch, original))
            if status != 'column_absent':
                problems.append('%s: %s row status %r, expected column_absent' % (cid, batch, status))
            continue
        source_row = ds['source_by_id'].get(batch, {}).get(cid)
        if source_row is None:
            problems.append('%s: no %s source row for original_workflow_family_ids' % (cid, batch))
            continue
        want = (source_row.get('workflow_family_id') or '').strip()
        if original != want:
            problems.append('%s: original_workflow_family_ids %r != source %r' % (cid, original, want))
        expected_status = 'registered' if want else 'unregistered_empty'
        if status != expected_status:
            problems.append('%s: status %r but source family id is %r (expect %s)' % (cid, status, want, expected_status))
        status_counts[(batch, status)] += 1

    b2_unregistered = status_counts[('B2', 'unregistered_empty')]
    b2_registered = status_counts[('B2', 'registered')]
    if b2_unregistered != 34:
        problems.append('B2 unregistered_empty rows = %d, expected 34' % b2_unregistered)
    if b2_registered != 5:
        problems.append('B2 registered rows = %d, expected 5' % b2_registered)
    notes.append('A/B1 empty with column_absent 108 rows; B2 unregistered_empty 34 + registered 5; B3 registered 27')
    return problems, notes


def check_07(ds, root):
    problems, notes = [], []
    assignment = ds['assignment']
    registry = ds['registry']
    batch_of = {(r.get('candidate_id') or '').strip(): (r.get('source_batch') or '').strip() for r in assignment}

    primary = defaultdict(set)
    secondary = defaultdict(set)
    for row in assignment:
        cid = (row.get('candidate_id') or '').strip()
        family = (row.get('workflow_family_id') or '').strip()
        primary[family].add(cid)
        for other in split_ids(row.get('secondary_workflow_family_ids')):
            if other == family:
                problems.append('%s: secondary_workflow_family_ids repeats its own primary family %s' % (cid, family))
                continue
            secondary[other].add(cid)

    registry_ids = [(r.get('workflow_family_id') or '').strip() for r in registry]
    registry_set = set(registry_ids)
    unknown_families = sorted(set(primary) - registry_set)
    if unknown_families:
        problems.append('assignment workflow_family_id(s) absent from registry: %s' % unknown_families[:10])
    unknown_secondary = sorted(set(secondary) - registry_set)
    if unknown_secondary:
        problems.append('secondary_workflow_family_ids absent from registry: %s' % unknown_secondary[:10])

    total_primary = 0
    for row in registry:
        family = (row.get('workflow_family_id') or '').strip()
        primary_ids = primary.get(family, set())
        secondary_ids = secondary.get(family, set())
        members = primary_ids | secondary_ids
        total_primary += len(primary_ids)

        stored_primary_ids = set(split_ids(row.get('primary_candidate_ids')))
        if stored_primary_ids != primary_ids:
            problems.append('%s: primary_candidate_ids mismatch (only in file %s, only in assignment %s)'
                            % (family, sorted(stored_primary_ids - primary_ids)[:6], sorted(primary_ids - stored_primary_ids)[:6]))
        stored_secondary_ids = set(split_ids(row.get('secondary_candidate_ids')))
        if stored_secondary_ids != secondary_ids:
            problems.append('%s: secondary_candidate_ids mismatch (only in file %s, only in assignment %s)'
                            % (family, sorted(stored_secondary_ids - secondary_ids)[:6], sorted(secondary_ids - stored_secondary_ids)[:6]))

        checks = (
            ('primary_candidate_count', len(primary_ids)),
            ('secondary_candidate_count', len(secondary_ids)),
            ('total_distinct_candidates', len(members)),
        )
        for column, expected in checks:
            got = to_int(row.get(column), problems, '%s %s' % (family, column))
            if got is not None and got != expected:
                problems.append('%s: %s %d != %d' % (family, column, got, expected))

        for batch in BATCHES:
            expected = sum(1 for cid in primary_ids if batch_of.get(cid) == batch)
            got = to_int(row.get('count_%s' % batch), problems, '%s count_%s' % (family, batch))
            if got is not None and got != expected:
                problems.append('%s: count_%s %d != %d' % (family, batch, got, expected))

        span = ';'.join(b for b in BATCHES if any(batch_of.get(cid) == b for cid in members))
        stored_span = (row.get('all_member_batch_span') or '').strip()
        if stored_span != span:
            problems.append('%s: all_member_batch_span %r != %r' % (family, stored_span, span))
        expected_cross = 'yes' if span.count(';') >= 1 else 'no'
        stored_cross = (row.get('cross_batch_flag') or '').strip()
        if stored_cross != expected_cross:
            problems.append('%s: cross_batch_flag %r != %r' % (family, stored_cross, expected_cross))
        if not primary_ids:
            problems.append('%s: registry family has no primary candidate' % family)

    if total_primary != 174:
        problems.append('registry primary counts sum to %d, expected 174' % total_primary)
    notes.append('%d families; primary counts sum %d; secondary memberships %d; cross-batch families %d'
                 % (len(registry), total_primary, sum(len(v) for v in secondary.values()),
                    sum(1 for row in registry if (row.get('cross_batch_flag') or '').strip() == 'yes')))
    return problems, notes


def check_08(ds, root):
    problems, notes = [], []
    assignment = ds['assignment']
    matrix = ds['matrix']
    batch_of = {(r.get('candidate_id') or '').strip(): (r.get('source_batch') or '').strip() for r in assignment}
    by_group = defaultdict(set)
    for row in assignment:
        by_group[(row.get('expert_capability_group_id') or '').strip()].add((row.get('candidate_id') or '').strip())

    matrix_ids = [(r.get('expert_capability_group_id') or '').strip() for r in matrix]
    if len(set(matrix_ids)) != 50:
        problems.append('matrix holds %d distinct expert_capability_group_id, expected 50' % len(set(matrix_ids)))
    missing_groups = sorted(set(by_group) - set(matrix_ids))
    extra_groups = sorted(set(matrix_ids) - set(by_group))
    if missing_groups:
        problems.append('assignment group(s) absent from matrix: %s' % missing_groups[:8])
    if extra_groups:
        problems.append('matrix group(s) with no assignment row: %s' % extra_groups[:8])

    owner = {}
    total = 0
    for row in matrix:
        group = (row.get('expert_capability_group_id') or '').strip()
        ids = split_ids(row.get('candidate_ids'))
        total += len(ids)
        for cid in ids:
            if cid in owner and owner[cid] != group:
                problems.append('%s: appears in both %s and %s' % (cid, owner[cid], group))
            owner[cid] = group
        want = by_group.get(group, set())
        if set(ids) != want:
            problems.append('%s: candidate_ids mismatch (only in file %s, only in assignment %s)'
                            % (group, sorted(set(ids) - want)[:6], sorted(want - set(ids))[:6]))
        if len(ids) != len(set(ids)):
            problems.append('%s: candidate_ids repeats an id' % group)
        got = to_int(row.get('primary_candidate_count'), problems, '%s primary_candidate_count' % group)
        if got is not None and got != len(want):
            problems.append('%s: primary_candidate_count %d != %d' % (group, got, len(want)))
        for batch in BATCHES:
            expected = sum(1 for cid in want if batch_of.get(cid) == batch)
            got = to_int(row.get('count_%s' % batch), problems, '%s count_%s' % (group, batch))
            if got is not None and got != expected:
                problems.append('%s: count_%s %d != %d' % (group, batch, got, expected))

    if len(owner) != 174:
        problems.append('matrix candidate_ids union holds %d distinct ids, expected 174' % len(owner))
    if set(owner) != set(batch_of):
        problems.append('matrix candidate_ids union != assignment ids (sym diff %s)'
                        % sorted(set(owner) ^ set(batch_of))[:8])
    if total != 174:
        problems.append('matrix rows list %d ids in total, expected 174' % total)
    notes.append('%d expert groups, %d ids, no overlap, per-batch counts match' % (len(matrix), len(owner)))
    return problems, notes


def check_09(ds, root):
    problems, notes = [], []
    assignment = ds['assignment']
    batch_of = {(r.get('candidate_id') or '').strip(): (r.get('source_batch') or '').strip() for r in assignment}
    summary = []
    for key, column in (('auth', 'authorization_risk_group_ids'), ('eng', 'engineering_risk_group_ids')):
        register = ds[key]
        membership = defaultdict(set)
        for row in assignment:
            cid = (row.get('candidate_id') or '').strip()
            for group in split_ids(row.get(column)):
                membership[group].add(cid)
        register_ids = {(r.get('risk_group_id') or '').strip() for r in register}
        referenced_not_declared = sorted(set(membership) - register_ids)
        if referenced_not_declared:
            problems.append('%s: assignment references undeclared group(s) %s' % (column, referenced_not_declared[:8]))
        for row in register:
            group = (row.get('risk_group_id') or '').strip()
            ids = set(split_ids(row.get('candidate_ids')))
            want = membership.get(group, set())
            if ids != want:
                problems.append('%s: candidate_ids mismatch (only in file %s, only in assignment %s)'
                                % (group, sorted(ids - want)[:6], sorted(want - ids)[:6]))
            if len(split_ids(row.get('candidate_ids'))) != len(ids):
                problems.append('%s: candidate_ids repeats an id' % group)
            got = to_int(row.get('candidate_count'), problems, '%s candidate_count' % group)
            if got is not None and got != len(want):
                problems.append('%s: candidate_count %d != %d' % (group, got, len(want)))
            for batch in BATCHES:
                expected = sum(1 for cid in want if batch_of.get(cid) == batch)
                got = to_int(row.get('count_%s' % batch), problems, '%s count_%s' % (group, batch))
                if got is not None and got != expected:
                    problems.append('%s: count_%s %d != %d' % (group, batch, got, expected))
        summary.append('%s %d groups' % (key.upper(), len(register)))

    eng01 = next((r for r in ds['eng'] if (r.get('risk_group_id') or '').strip() == 'ENG-01'), None)
    if eng01 is None:
        problems.append('ENG-01 missing from the engineering register')
    else:
        got = to_int(eng01.get('candidate_count'), problems, 'ENG-01 candidate_count')
        if got != 174:
            problems.append('ENG-01 candidate_count %r, expected 174' % eng01.get('candidate_count'))
    notes.append('%s; ENG-01 covers 174' % ', '.join(summary))
    return problems, notes


def check_10(ds, root):
    problems, notes = [], []
    assignment = ds['assignment']
    batch_of = {(r.get('candidate_id') or '').strip(): (r.get('source_batch') or '').strip() for r in assignment}

    linux = sum(1 for row in assignment if yes(row.get('linux_not_verified_flag')))
    if linux != 174:
        problems.append('linux_not_verified_flag=yes on %d rows, expected 174' % linux)

    pending = Counter()
    for row in assignment:
        cid = (row.get('candidate_id') or '').strip()
        batch = (row.get('source_batch') or '').strip()
        flag = yes(row.get('engineering_pending_flag'))
        if flag:
            pending[batch] += 1
        source_row = ds['source_by_id'].get(batch, {}).get(cid)
        if source_row is None:
            problems.append('%s: no source row for engineering_pending' % cid)
            continue
        source_flag = yes(source_row.get('engineering_pending'))
        if flag != source_flag:
            problems.append('%s: engineering_pending_flag %r but source engineering_pending %r'
                            % (cid, (row.get('engineering_pending_flag') or '').strip(),
                               (source_row.get('engineering_pending') or '').strip()[:40]))
        own_text = yes(row.get('engineering_pending'))
        if own_text != flag:
            problems.append('%s: engineering_pending_flag disagrees with its own engineering_pending text' % cid)
    total_pending = sum(pending.values())
    if total_pending != 83:
        problems.append('engineering_pending_flag=yes on %d rows, expected 83' % total_pending)
    for batch in BATCHES:
        if pending.get(batch, 0) != EXPECTED_ENGINEERING_PENDING[batch]:
            problems.append('engineering_pending_flag=yes in %s: %d, expected %d'
                            % (batch, pending.get(batch, 0), EXPECTED_ENGINEERING_PENDING[batch]))

    # REVISION U1: uncovered_official now propagates to all six uncovered
    # subdomains, not just the three B3 ones. Only the count/batch/set
    # expectations changed. The per-row mapping proof stays in
    # scripts/36_validate_s1_02c_c16.py (C16).
    uncovered = [row for row in assignment if yes(row.get('uncovered_official_flag'))]
    if len(uncovered) != EXPECTED_UNCOVERED_COUNT:
        problems.append('uncovered_official_flag=yes on %d rows, expected %d'
                        % (len(uncovered), EXPECTED_UNCOVERED_COUNT))
    uncovered_batches = {batch_of.get((r.get('candidate_id') or '').strip()) for r in uncovered}
    if uncovered_batches != EXPECTED_UNCOVERED_BATCHES:
        problems.append('uncovered_official_flag=yes batches %s, expected %s'
                        % (sorted(uncovered_batches), sorted(EXPECTED_UNCOVERED_BATCHES)))
    uncovered_subdomains = Counter((r.get('subdomain_code') or '').strip() for r in uncovered)
    if set(uncovered_subdomains) != EXPECTED_UNCOVERED_SUBDOMAINS:
        problems.append('uncovered_official subdomains %s, expected %s'
                        % (sorted(uncovered_subdomains), sorted(EXPECTED_UNCOVERED_SUBDOMAINS)))
    for name, count in sorted(uncovered_subdomains.items()):
        if count != EXPECTED_UNCOVERED_PER_CODE.get(name):
            problems.append('uncovered_official in %s: %d rows, expected %d'
                            % (name, count, EXPECTED_UNCOVERED_PER_CODE.get(name)))

    padding = [row for row in assignment if yes(row.get('padding_risk_flag'))]
    if len(padding) != 27:
        problems.append('padding_risk_flag=yes on %d rows, expected 27' % len(padding))
    padding_batches = {batch_of.get((r.get('candidate_id') or '').strip()) for r in padding}
    if padding_batches != {'B3'}:
        problems.append('padding_risk_flag=yes outside B3: %s' % sorted(padding_batches))
    severity_high = sum(1 for r in padding if (r.get('padding_risk_severity') or '').strip() == 'high')
    if severity_high != 9:
        problems.append('padding_risk_severity=high on %d rows, expected 9' % severity_high)
    stray_severity = [r.get('candidate_id') for r in assignment
                      if not yes(r.get('padding_risk_flag')) and (r.get('padding_risk_severity') or '').strip()]
    if stray_severity:
        problems.append('severity set on rows without padding risk: %s' % stray_severity[:8])

    endorsement = {(r.get('candidate_id') or '').strip() for r in assignment if yes(r.get('expert_endorsement_required'))}
    if len(endorsement) != 45:
        problems.append('expert_endorsement_required=yes on %d distinct candidates, expected 45' % len(endorsement))

    expert_pending = [(r.get('candidate_id') or '').strip() for r in assignment
                      if (r.get('expert_pending') or '').strip()]
    if len(expert_pending) != 9:
        problems.append('expert_pending populated on %d rows, expected 9' % len(expert_pending))
    non_a = [cid for cid in expert_pending if batch_of.get(cid) != 'A']
    if non_a:
        problems.append('expert_pending outside batch A: %s' % non_a[:8])

    notes.append('linux_not_verified 174; engineering_pending 83 (%s); uncovered_official %d (A 13 + B3 9); padding 27 with 9 high; endorsement 45; expert_pending 9 (A)'
                 % ('/'.join(str(pending.get(b, 0)) for b in BATCHES), len(uncovered)))
    return problems, notes


def check_11(ds, root):
    problems, notes = [], []
    assignment = ds['assignment']
    by_id = {(r.get('candidate_id') or '').strip(): r for r in assignment}

    pairs = []
    for batch in BATCHES:
        rows = ds['duplicates'][batch]
        if not rows:
            problems.append('%s is empty' % DUPLICATE_FILES[batch])
        for index, row in enumerate(rows, 1):
            raw = (row.get('candidates') or '').strip()
            ids = [part.strip() for part in re.split(r'\s+vs\s+|,', raw) if part.strip()]
            pairs.append({
                'batch': batch,
                'index': index,
                'pair_id': 'DP-%s-%02d' % (batch, index),
                'ids': ids,
                'yes': (row.get('substantively_duplicate') or '').strip().upper() == 'YES',
                'primary_home': (row.get('primary_home') or '').strip(),
                'row': row,
            })

    yes_pairs = [p for p in pairs if p['yes']]
    no_pairs = [p for p in pairs if not p['yes']]
    if len(pairs) != 25:
        problems.append('%d duplicate pair rows across the four files, expected 25' % len(pairs))
    if len(yes_pairs) != 3:
        problems.append('%d YES pair rows, expected 3' % len(yes_pairs))
    if len(no_pairs) != 22:
        problems.append('%d no pair rows, expected 22' % len(no_pairs))

    slot_ids = []
    for pair in pairs:
        if len(pair['ids']) != 2:
            problems.append('%s: %d candidate ids, expected 2 (%s)' % (pair['pair_id'], len(pair['ids']), pair['ids']))
        for cid in pair['ids']:
            if cid not in by_id:
                problems.append('%s: candidate %r does not exist in the assignment' % (pair['pair_id'], cid))
            else:
                slot_ids.append(cid)
        mentioned = {(r.get('candidate_id') or '').strip(): split_ids(r.get('duplicate_pair_ids'))
                     for r in assignment}
        holders = sorted(cid for cid, ids in mentioned.items() if pair['pair_id'] in ids)
        if set(holders) != set(pair['ids']):
            problems.append('%s: duplicate_pair_ids carried by %s, expected %s'
                            % (pair['pair_id'], holders, sorted(pair['ids'])))

    if len(slot_ids) != 50:
        problems.append('%d pair slots, expected 50' % len(slot_ids))
    if len(set(slot_ids)) != 45:
        problems.append('%d distinct candidates across pair slots, expected 45' % len(set(slot_ids)))

    cluster_owner = {}
    yes_members = set()
    for pair in yes_pairs:
        yes_members.update(pair['ids'])
        match = PRIMARY_HOME_RE.search(pair['primary_home'])
        expected_primary = match.group(1).strip() if match else ''
        if expected_primary not in pair['ids']:
            problems.append('%s: primary_home %r does not name one of %s'
                            % (pair['pair_id'], pair['primary_home'], pair['ids']))
            continue
        clusters = {(by_id[cid].get('duplicate_cluster_id') or '').strip() for cid in pair['ids'] if cid in by_id}
        if len(clusters) != 1:
            problems.append('%s: pair members carry %d distinct duplicate_cluster_id values %s'
                            % (pair['pair_id'], len(clusters), sorted(clusters)))
            continue
        cluster = clusters.pop()
        if not cluster:
            problems.append('%s: YES pair has no duplicate_cluster_id' % pair['pair_id'])
            continue
        if cluster in cluster_owner:
            problems.append('%s: duplicate_cluster_id %r already used by %s' % (pair['pair_id'], cluster, cluster_owner[cluster]))
        cluster_owner[cluster] = pair['pair_id']
        members = [cid for cid in pair['ids'] if cid in by_id]
        primaries = [cid for cid in members
                     if (by_id[cid].get('duplicate_attribution_role') or '').strip() == 'primary']
        secondaries = [cid for cid in members
                       if (by_id[cid].get('duplicate_attribution_role') or '').strip() == 'secondary']
        if len(primaries) != 1:
            problems.append('%s: %d primary rows for cluster %r, expected 1' % (pair['pair_id'], len(primaries), cluster))
        elif primaries[0] != expected_primary:
            problems.append('%s: primary row %r != primary_home id %r' % (pair['pair_id'], primaries[0], expected_primary))
        if len(secondaries) != 1:
            problems.append('%s: %d secondary rows for cluster %r, expected 1' % (pair['pair_id'], len(secondaries), cluster))

    clustered = {cid for cid, row in by_id.items() if (row.get('duplicate_cluster_id') or '').strip()}
    if clustered != yes_members:
        problems.append('rows carrying duplicate_cluster_id %s, expected exactly the YES pair members %s'
                        % (sorted(clustered), sorted(yes_members)))

    notes.append('%d pairs (3 YES / 22 no), %d slots, %d distinct ids, %d clusters'
                 % (len(pairs), len(slot_ids), len(set(slot_ids)), len(cluster_owner)))
    return problems, notes


def check_12(ds, root):
    problems, notes = [], []
    empty_fragments = []
    for row in ds['assignment']:
        cid = (row.get('candidate_id') or '').strip()
        batch = (row.get('source_batch') or '').strip()
        if not (row.get('source_reference_or_fragment') or '').strip():
            empty_fragments.append(cid)
        claim = next((r for r in ds['claim_maps'][batch] if (r.get('candidate_id') or '').strip() == cid), None)
        if claim is None:
            problems.append('%s: absent from %s' % (cid, CLAIM_MAPS[batch]))
            continue
        got = (row.get('primary_source_url') or '').strip()
        want = (claim.get('source_url') or '').strip()
        if got != want:
            problems.append('%s: primary_source_url %r != %s source_url %r' % (cid, got, CLAIM_MAPS[batch], want))
    if empty_fragments:
        problems.append('empty source_reference_or_fragment: %s' % empty_fragments[:8])
    for batch in BATCHES:
        claim_ids = {(r.get('candidate_id') or '').strip() for r in ds['claim_maps'][batch]}
        if claim_ids != set(ds['source_by_id'][batch]):
            problems.append('%s: candidate ids differ from %s' % (CLAIM_MAPS[batch], SOURCES[batch][0]))
    notes.append('primary_source_url equal to claim-map source_url on 174 rows; source_reference_or_fragment non-empty on 174')
    return problems, notes


def _spans(pattern, text):
    return [(m.start(), m.end()) for m in pattern.finditer(text)]


def _covered(position, spans):
    return any(start <= position < end for start, end in spans)


def check_13(ds, root):
    problems, notes = [], []
    manifest = Path(root) / BASELINE
    if not manifest.is_file():
        return ['missing %s' % BASELINE.as_posix()], []

    raw_lines = manifest.read_text(encoding='utf-8').splitlines(keepends=True)
    entries = []
    for index, line in enumerate(raw_lines):
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            problems.append('manifest line %d unparseable: %r' % (index + 1, line.strip()[:80]))
            continue
        entries.append((parts[0].strip().lower(), os.path.normpath(parts[1].strip()), index))

    if len(entries) != 61:
        problems.append('manifest lists %d entries, expected 61 historical files (the 62-line as-taken original minus its self-hash line)' % len(entries))

    manifest_rel = os.path.normpath(BASELINE.as_posix())
    matched = 0
    for recorded, rel, index in entries:
        if rel == manifest_rel:
            actual = hashlib.sha256(manifest.read_bytes()).hexdigest()
            prefix = hashlib.sha256(''.join(raw_lines[:index]).encode('utf-8')).hexdigest()
            detail = '; recorded value equals sha256 of the first %d lines, so the self-hash came from a partially written file' % index
            if prefix != recorded:
                detail = ''
            problems.append('%s: manifest hashes itself; no file can carry its own sha256 (recorded %s, actual %s)%s'
                            % (rel, recorded[:12], actual[:12], detail))
            continue
        target = Path(root) / rel
        if not target.is_file():
            problems.append('%s: missing file' % rel)
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != recorded:
            problems.append('%s: sha256 %s != recorded %s' % (rel, actual[:16], recorded[:16]))
        else:
            matched += 1

    notes.append('%d/%d entries hash-match; %d unsatisfiable' % (matched, len(entries), len(entries) - matched))
    return problems, notes


def check_14(ds, root):
    problems, notes = [], []
    exempt = []
    for key in ('assignment', 'registry', 'matrix', 'auth', 'eng'):
        id_column = ID_COLUMNS[key]
        for row in ds[key]:
            row_id = (row.get(id_column) or '').strip()
            for column, value in row.items():
                if not value:
                    continue
                url_spans = _spans(URL_RE, value)
                title_spans = _spans(TITLE_RE, value)
                for token in FORBIDDEN_TOKENS:
                    for match in re.finditer(re.escape(token), value, re.IGNORECASE):
                        position = match.start()
                        context = value[max(0, position - 30):position + len(token) + 30].replace('\n', ' ')
                        if _covered(position, url_spans) or _covered(position, title_spans):
                            exempt.append('%s/%s/%s' % (row_id, column, token))
                        else:
                            problems.append('%s: forbidden allocation token %r in %s: %r'
                                            % (row_id, token, column, context))
    note = 'no asserted allocation language in the five files'
    if exempt:
        note += '; %d citation/URL hit(s) exempt (%s)' % (len(exempt), ', '.join(sorted(set(exempt))))
    notes.append(note)
    return problems, notes


def check_15(ds, root):
    problems, notes = [], []
    columns = ('authorization_risk_level', 'engineering_risk_level', 'evidence_risk_class', 'source_support_mode')
    for column in columns:
        counts = Counter((row.get(column) or '').strip() or '<empty>' for row in ds['assignment'])
        total = sum(counts.values())
        notes.append('%s: %s (total %d)' % (column, ', '.join('%s=%d' % kv for kv in sorted(counts.items())), total))
        if total != 174:
            problems.append('%s distribution sums to %d, expected 174' % (column, total))
        empty = counts.get('<empty>', 0)
        if empty:
            problems.append('%s has %d empty value(s)' % (column, empty))
    return problems, notes


CHECKS = (
    ('C01', 'row counts and primary-key uniqueness', check_01),
    ('C02', 'assignment covers the four source batches', check_02),
    ('C03', 'evidence level and kind equal the source', check_03),
    ('C04', 'source_support_mode and its status', check_04),
    ('C05', 'evidence_risk_class recomputed from (level, mode)', check_05),
    ('C06', 'original family ids and registration status', check_06),
    ('C07', 'workflow family registry', check_07),
    ('C08', 'expert capability matrix', check_08),
    ('C09', 'authorization and engineering risk registers', check_09),
    ('C10', 'flags', check_10),
    ('C11', 'duplicate attribution', check_11),
    ('C12', 'primary_source_url against the claim maps', check_12),
    ('C13', 'historical immutability against the baseline', check_13),
    ('C14', 'forbidden allocation language', check_14),
    ('C15', 'level and mode distributions', check_15),
)


class Result(object):
    def __init__(self, cid, title):
        self.cid = cid
        self.title = title
        self.problems = []
        self.notes = []

    @property
    def ok(self):
        return not self.problems


def run_all(root, ds=None):
    if ds is None:
        ds = load_dataset(root)
    results = []
    for cid, title, function in CHECKS:
        result = Result(cid, title)
        try:
            problems, notes = function(ds, root)
            result.problems = list(problems)
            result.notes = list(notes)
        except Exception as exc:  # a crashing check must never read as a pass
            result.problems = ['check raised %s: %s' % (type(exc).__name__, exc)]
        results.append(result)
    return results


def print_report(results, root):
    print('root: %s' % root)
    for result in results:
        status = 'PASS' if result.ok else 'FAIL'
        tail = ''
        if result.ok and result.notes and result.cid != 'C15':
            tail = '  ' + '; '.join(result.notes)
        print('%s %s  %s%s' % (status, result.cid, result.title, tail))
        if result.cid == 'C15':
            for note in result.notes:
                print('     %s' % note)
        for problem in result.problems[:40]:
            print('     ! %s' % problem)
        if len(result.problems) > 40:
            print('     ! ... %d more problem(s)' % (len(result.problems) - 40))
    failed = [r.cid for r in results if not r.ok]
    print('%d checks, %d failed%s' % (len(results), len(failed), (': ' + ', '.join(failed)) if failed else ''))


def append_log(root, code, results):
    log = Path(root) / LOG_PATH
    failed = [r.cid for r in results if not r.ok]
    stamp = datetime.now().astimezone().isoformat(timespec='seconds')
    line = '%s exit=%d checks=%d failed=%s script=scripts/35_validate_s1_02c.py\n' % (
        stamp, code, len(results), ','.join(failed) if failed else '-')
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, 'a', encoding='utf-8') as fh:
        fh.write(line)


# --------------------------------------------------------------------------
# negative-case self-test


def _read_rows(path):
    with open(path, newline='', encoding='utf-8-sig') as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), list(reader)


def _write_rows(path, fieldnames, rows):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def _fixture_paths(root):
    paths = set(DELIVERABLES.values())
    paths.update(name for name, _n in SOURCES.values())
    paths.update(CLAIM_MAPS.values())
    paths.update(DUPLICATE_FILES.values())
    paths.update({ERRATUM_DOC, A_ORIGINAL})
    manifest = Path(root) / BASELINE
    manifest_rel = os.path.normpath(BASELINE.as_posix())
    for line in manifest.read_text(encoding='utf-8').splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            rel = os.path.normpath(parts[1].strip())
            if rel != manifest_rel:
                paths.add(rel)
    return sorted(paths)


def _split_manifest_line(line):
    parts = line.split(None, 1)
    if len(parts) != 2:
        return None
    return parts[0].strip(), os.path.normpath(parts[1].strip())


def build_fixture(source_root, target_root):
    """Copy the workspace into a throwaway tree that passes all fifteen checks.

    One repair is needed. The real manifest lists itself, and a file cannot carry
    its own sha256, so that single entry is unsatisfiable by construction. The
    recorded digest happens to equal sha256 of the sixteen lines written before
    it, so the fixture keeps the entry and its digest but points it at a
    byte-identical prefix file. Every other line is copied untouched, which is
    what lets a mutation be the only difference from a green baseline.
    """
    source_root = Path(source_root)
    target_root = Path(target_root)
    for rel in _fixture_paths(source_root):
        destination = target_root / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_root / rel, destination)

    manifest_rel = os.path.normpath(BASELINE.as_posix())
    decoy_rel = os.path.normpath('.audit/s1-02c-baseline.prefix.sha256')
    kept = []
    for line in (source_root / BASELINE).read_text(encoding='utf-8').splitlines(keepends=True):
        if not line.strip():
            continue
        if not line.endswith('\n'):
            line += '\n'
        entry = _split_manifest_line(line)
        if entry and entry[1] == manifest_rel:
            prefix = ''.join(kept)
            decoy = target_root / decoy_rel
            decoy.parent.mkdir(parents=True, exist_ok=True)
            decoy.write_text(prefix, encoding='utf-8')
            kept.append('%s  ./%s\n' % (entry[0], decoy_rel.replace(os.sep, '/')))
            continue
        kept.append(line)
    (target_root / BASELINE).write_text(''.join(kept), encoding='utf-8')


def _assignment_copy(root):
    path = Path(root) / DELIVERABLES['assignment']
    fields, rows = _read_rows(path)
    return path, fields, rows


def mut_duplicate_candidate_id(root):
    path, fields, rows = _assignment_copy(root)
    rows.append(dict(rows[0]))
    _write_rows(path, fields, rows)


def mut_missing_candidate(root):
    path, fields, rows = _assignment_copy(root)
    rows.pop()
    _write_rows(path, fields, rows)


def mut_family_not_in_registry(root):
    path, fields, rows = _assignment_copy(root)
    rows[5]['workflow_family_id'] = 'WF-NOT-IN-REGISTRY'
    _write_rows(path, fields, rows)


def mut_registry_primary_count(root):
    path = Path(root) / DELIVERABLES['registry']
    fields, rows = _read_rows(path)
    rows[0]['primary_candidate_count'] = str(int(rows[0]['primary_candidate_count']) + 1)
    _write_rows(path, fields, rows)


def mut_flag_count(root):
    path, fields, rows = _assignment_copy(root)
    for row in rows:
        if (row.get('engineering_pending_flag') or '').strip() == 'yes':
            row['engineering_pending_flag'] = 'no'
            row['engineering_pending'] = ''
            break
    _write_rows(path, fields, rows)


def mut_evidence_class(root):
    path, fields, rows = _assignment_copy(root)
    for row in rows:
        if (row.get('evidence_risk_class') or '').strip() == '1':
            row['evidence_risk_class'] = '4'
            break
    _write_rows(path, fields, rows)


def mut_tampered_history(root):
    target = Path(root) / '.audit' / 's1-02b3.tsv'
    with open(target, 'a', encoding='utf-8') as fh:
        fh.write('\n')


def mut_forbidden_language(root):
    path = Path(root) / DELIVERABLES['registry']
    fields, rows = _read_rows(path)
    rows[0]['definition'] = '本组按配额分配 3 名专家。'
    _write_rows(path, fields, rows)


def mut_ecg_overlap(root):
    path = Path(root) / DELIVERABLES['matrix']
    fields, rows = _read_rows(path)
    donor = split_ids(rows[1]['candidate_ids'])[0]
    rows[0]['candidate_ids'] = ';'.join(split_ids(rows[0]['candidate_ids']) + [donor])
    _write_rows(path, fields, rows)


def mut_manifest_self_reference(root):
    path = Path(root) / BASELINE
    with open(path, 'a', encoding='utf-8') as fh:
        fh.write('%s  ./.audit/s1-02c-baseline.sha256\n' % ('0' * 64))


SELF_TEST_CASES = (
    ('duplicate candidate id', mut_duplicate_candidate_id, ('C01',)),
    ('missing candidate', mut_missing_candidate, ('C02',)),
    ('family id not in registry', mut_family_not_in_registry, ('C07',)),
    ('registry primary count mismatch', mut_registry_primary_count, ('C07',)),
    ('engineering_pending flag count', mut_flag_count, ('C10',)),
    ('evidence risk class', mut_evidence_class, ('C05',)),
    ('tampered historical file', mut_tampered_history, ('C13',)),
    ('forbidden allocation word', mut_forbidden_language, ('C14',)),
    ('expert group overlap', mut_ecg_overlap, ('C08',)),
    ('manifest self-reference', mut_manifest_self_reference, ('C13',)),
)


def run_self_test():
    source_root = DEFAULT_ROOT
    failures = []
    print('self-test: mutated copies under the system temp directory, never in the workspace')

    with tempfile.TemporaryDirectory(prefix='s1-02c-selftest-') as tmp:
        build_fixture(source_root, tmp)
        results = run_all(Path(tmp))
        broken = [r.cid for r in results if not r.ok]
        if broken:
            failures.append('pristine fixture already fails %s, so mutations cannot be told apart' % broken)
            print('FAIL control (pristine copy) unexpected failures: %s' % broken)
        else:
            print('PASS control (pristine copy) all 15 checks pass')

    for name, mutate, expected in SELF_TEST_CASES:
        with tempfile.TemporaryDirectory(prefix='s1-02c-selftest-') as tmp:
            root = Path(tmp)
            build_fixture(source_root, root)
            mutate(root)
            results = run_all(root)
            failed = {r.cid for r in results if not r.ok}
            escaped = [cid for cid in expected if cid not in failed]
            if escaped:
                failures.append('%s: %s stayed green' % (name, escaped))
                print('FAIL %-34s expected %s to fail, failed=%s' % (name, list(expected), sorted(failed)))
            else:
                print('PASS %-34s caught by %s' % (name, ', '.join(sorted(failed))))

    if failures:
        print('self-test FAILED: %d mutation(s) escaped' % len(failures))
        return 1
    print('self-test passed: %d mutations caught, pristine control green' % len(SELF_TEST_CASES))
    return 0


# --------------------------------------------------------------------------


def main(argv=None):
    parser = argparse.ArgumentParser(description='Independent validator for the S1-02C deliverables.')
    parser.add_argument('--root', default=str(DEFAULT_ROOT), help='repository root to validate')
    parser.add_argument('--self-test', action='store_true',
                        help='mutate throwaway copies in a temp dir and require the matching check to fail')
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve()
    try:
        ds = load_dataset(root)
    except Exception as exc:
        print('FATAL could not load inputs: %s: %s' % (type(exc).__name__, exc))
        append_log(root, 1, [])
        return 1

    results = run_all(root, ds)
    print_report(results, root)
    code = 0 if all(r.ok for r in results) else 1
    append_log(root, code, results)
    return code


if __name__ == '__main__':
    sys.exit(main())