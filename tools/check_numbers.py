#!/usr/bin/env python3
"""Check that numbers stated in living documents match the files that hold them.

Every check reads the claim from the document that states it, then compares it
with the repository file that records the fact, so a number that drifts away
from its source fails instead of quietly aging. Stage 0 and stage 1 claims are
skipped when the document no longer states them at all; a stated claim that
disagrees is always a failure.
"""

import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

README = ROOT / "README.md"
STAGES_README = ROOT / "stages" / "README.md"
PLAN = ROOT / "docs" / "02-plan.md"
CHARTER = ROOT / "docs" / "01-charter.md"
FINDINGS = ROOT / "docs" / "05-research-findings.md"
STAGE1 = ROOT / "stages" / "s1-research" / "STAGE.md"
STAGE0 = ROOT / "stages" / "s0-baseline" / "STAGE.md"

S1 = ROOT / "stages" / "s1-research"
S0 = ROOT / "stages" / "s0-baseline"

ASSIGNMENT = "S1_02C_CANDIDATE_FAMILY_ASSIGNMENT.csv"
REGISTRY = "S1_02C_WORKFLOW_FAMILY_REGISTRY.csv"
CAPABILITY = "S1_02C_EXPERT_CAPABILITY_MATRIX.csv"
AUTHORIZATION = "S1_02C_AUTHORIZATION_RISK_REGISTER.csv"
ENGINEERING = "S1_02C_ENGINEERING_RISK_REGISTER.csv"

STATUS_MARKERS = (
    ("已关闭", "closed"),
    ("收口", "awaiting_review"),
    ("未启动", "not_started"),
)

STAGE_ROW = re.compile(r"^\|\s*([0-6])(?:\s|\||$)")

# Column positions differ between the three tables, so the status is whichever
# cell normalizes into the known set.
CLAIM_COUNTS = (
    ("D1", ASSIGNMENT, re.compile(r"(?P<n>\d+)\s*条研究候选")),
    ("D2", REGISTRY, re.compile(r"(?P<n>\d+)\s*个任务族")),
    ("D3", CAPABILITY, re.compile(r"(?P<n>\d+)\s*个专家能力组")),
    ("D4", AUTHORIZATION, re.compile(r"授权风险\s*(?P<n>\d+)\s*组")),
    ("D5", ENGINEERING, re.compile(r"工程风险\s*(?P<n>\d+)\s*组")),
)

FALSE_LIKE = {"false", "no", "0", "n"}


def text(path):
    return path.read_text(encoding="utf-8")


def rel(path):
    return path.relative_to(ROOT).as_posix()


def describe(docs):
    names = [rel(path) for path in docs]
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " or " + names[-1]


def find(docs, pattern):
    for path in docs:
        for line in text(path).splitlines():
            match = pattern.search(line)
            if match:
                return path, line.strip(), match
    return None, None, None


def claim_value(docs, pattern):
    path, line, match = find(docs, pattern)
    if match is None:
        return None, None
    return int(match.group("n")), f"{rel(path)}: {line}"


def compare(claim_id, docs, pattern, actual, where):
    value, quoted = claim_value(docs, pattern)
    if value is None:
        return claim_id, "skip", f"claim not stated in {describe(docs)}"
    if value != actual:
        return claim_id, "fail", f"doc says {value}, {where} counts {actual} ({quoted})"
    return claim_id, "pass", f"{value} matches {where}"


def read_csv(path):
    lines = text(path).splitlines()
    body = [line for line in lines if not line.startswith("#")]
    return [row for row in csv.DictReader(body) if any(row.values())]


def stage_rows(path):
    rows = {}
    for line in text(path).splitlines():
        match = STAGE_ROW.match(line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.setdefault(int(match.group(1)), []).append(cells)
    return rows


def normalize(cell):
    for marker, value in STATUS_MARKERS:
        if marker in cell:
            return value
    return "unknown"


def status_cells(cells):
    return [(cell, normalize(cell)) for cell in cells if normalize(cell) != "unknown"]


def check_a():
    quoted = None
    for line in text(README).splitlines():
        if "个文件" in line and "克隆下来就是全部内容" in line:
            quoted = line.strip()
            break
    if quoted is None:
        return "A", "fail", "README no longer states the tracked file count"
    match = re.search(r"(?P<n>\d+)\s*个文件", quoted)
    if match is None:
        return "A", "fail", f"README states no numeric file count: {quoted!r}"
    value = int(match.group("n"))
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files"],
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return "A", "skip", f"git unavailable: {exc}"
    if result.returncode != 0:
        reason = result.stderr.strip().splitlines()
        return "A", "skip", f"git unavailable: {reason[0] if reason else result.returncode}"
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    if value != len(tracked):
        return "A", "fail", f"README says {value} files, git ls-files shows {len(tracked)} ({quoted})"
    return "A", "pass", f"README says {value}, git ls-files has {len(tracked)}"


def check_b():
    listed = sorted(set(re.findall(r"`(docs/[^`\s]+\.md)`", text(README))))
    if not listed:
        return "B", "fail", "README no longer lists the docs/*.md paths"
    on_disk = sorted(f"docs/{path.name}" for path in (ROOT / "docs").glob("*.md"))
    missing = [item for item in listed if item not in on_disk]
    extra = [item for item in on_disk if item not in listed]
    if missing or extra:
        parts = []
        if missing:
            parts.append("listed but missing: " + ", ".join(missing))
        if extra:
            parts.append("on disk but not listed: " + ", ".join(extra))
        return "B", "fail", "; ".join(parts)
    return "B", "pass", f"{len(listed)} listed paths match docs/*.md"


def check_c():
    tables = [README, STAGES_README, PLAN]
    rows = {rel(path): stage_rows(path) for path in tables}
    results = []
    for stage in range(7):
        cells = []
        problem = None
        for path in tables:
            name = rel(path)
            candidates = rows[name].get(stage)
            if not candidates:
                problem = f"no row for stage {stage} in {name}"
                break
            found = [
                (row, status_cells(row))
                for row in candidates
                if len(status_cells(row)) == 1
            ]
            if len(found) != 1:
                listed = " || ".join(" | ".join(row) for row in candidates)
                problem = (
                    f"{name} stage {stage} has {len(found)} rows carrying a status, "
                    f"expected 1: {listed}"
                )
                break
            row, status = found[0]
            cells.append((name, status[0][0], status[0][1]))
        if problem:
            results.append((f"C{stage}", "fail", problem))
            continue
        values = {value for _, _, value in cells}
        if len(values) == 1:
            results.append((f"C{stage}", "pass", f"all three tables say {values.pop()}"))
        else:
            detail = "; ".join(f"{name}: {raw!r} -> {value}" for name, raw, value in cells)
            results.append((f"C{stage}", "fail", detail))
    return results


def check_stage1_counts(tables):
    results = []
    for claim_id, filename, pattern in CLAIM_COUNTS:
        results.append(
            compare(claim_id, [FINDINGS, STAGE1], pattern, len(tables[filename]), f"{filename} rows")
        )
    return results


def check_d6(registry):
    pattern = re.compile(r"单成员(?:族)?\s*(?P<n>\d+)\s*个")
    actual = sum(1 for row in registry if row["primary_candidate_count"].strip() == "1")
    return compare("D6", [FINDINGS, STAGE1], pattern, actual, f"{REGISTRY} rows with primary_candidate_count 1")


def check_d7(assignment):
    pattern = re.compile(r"(?P<level>E[134])\s*(?:共|有)\s*(?P<n>\d+)\s*条")
    stated = {}
    for path in (FINDINGS, STAGE1):
        for line in text(path).splitlines():
            for level, number in re.findall(pattern, line):
                stated.setdefault(level, (int(number), f"{rel(path)}: {line.strip()}"))
    if not stated:
        return [("D7", "skip", f"claim not stated in {describe([FINDINGS, STAGE1])}")]

    counts = {}
    for row in assignment:
        level = row["evidence_level"].strip()
        counts[level] = counts.get(level, 0) + 1

    failures = []
    parts = []
    for level in ("E1", "E3", "E4"):
        if level not in stated:
            parts.append(f"{level} not stated")
            continue
        value, quoted = stated[level]
        actual = counts.get(level, 0)
        if value != actual:
            failures.append(f"{level}: doc says {value}, CSV has {actual} ({quoted})")
        else:
            parts.append(f"{level}={actual}")
    if failures:
        return [("D7", "fail", "; ".join(failures))]
    return [("D7", "pass", ", ".join(parts) + f" in {ASSIGNMENT}")]


def check_d8(assignment):
    pattern = re.compile(r"(?P<label>[A-Z][0-9]?)\s*批\s*(?P<n>\d+)\s*条")
    pairs = []
    quoted = None
    for path in (FINDINGS, STAGE1):
        for line in text(path).splitlines():
            found = pattern.findall(line)
            if len(found) == 4:
                pairs = [(label, int(number)) for label, number in found]
                quoted = f"{rel(path)}: {line.strip()}"
                break
        if pairs:
            break
    if not pairs:
        return [("D8", "skip", f"claim not stated in {describe([FINDINGS, STAGE1])}")]

    counts = {}
    for row in assignment:
        label = row["source_batch"].strip()
        counts[label] = counts.get(label, 0) + 1

    labels = [label for label, _ in pairs]
    if labels == ["A", "B1", "B2", "B3"]:
        matched = pairs
    else:
        derived = sorted(counts)
        if len(derived) != len(pairs):
            return [("D8", "fail", f"doc names {labels}, CSV batches are {derived} ({quoted})")]
        matched = [(derived[index], number) for index, (_, number) in enumerate(pairs)]

    failures = []
    parts = []
    for label, value in matched:
        actual = counts.get(label, 0)
        if value != actual:
            failures.append(f"{label}: doc says {value}, CSV has {actual} ({quoted})")
        parts.append(f"{label}={value}")
    if failures:
        return [("D8", "fail", "; ".join(failures))]
    return [("D8", "pass", ", ".join(parts) + f" match source_batch counts in {ASSIGNMENT}")]


def check_e3(inventory):
    pattern = re.compile(r"非\s*CS\s*剩\s*(?P<n>\d+)\s*条")
    actual = sum(1 for row in inventory if row["cs_excluded"].strip().lower() in FALSE_LIKE)
    where = "inventory rows with cs_excluded false-like (false/no/0/n)"
    return compare("E3", [CHARTER, PLAN, STAGE0], pattern, actual, where)


def check_e5(inventory):
    pattern = re.compile(r"(?P<n>\d+)\s*条[^。\n]{0,40}运行状态都是\s*NOT_RUN")
    value, quoted = claim_value([CHARTER, PLAN, STAGE0], pattern)
    if value is None:
        return "E5", "skip", f"claim not stated in {describe([CHARTER, PLAN, STAGE0])}"
    off = [row for row in inventory if row["run_state_current"].strip() != "NOT_RUN"]
    if off:
        detail = (
            f"doc says all {value} rows are NOT_RUN, but {len(off)} differ, "
            f"e.g. {off[0]['task_id']}={off[0]['run_state_current']} ({quoted})"
        )
        return "E5", "fail", detail
    if value != len(inventory):
        return "E5", "fail", f"doc says {value}, inventory has {len(inventory)} rows ({quoted})"
    return "E5", "pass", f"all {value} rows say NOT_RUN"


def check_e6(inventory):
    pattern = re.compile(r"Windows\s*(?P<n>\d+)\s*条")
    actual = sum(
        1
        for row in inventory
        if row["os_windows"].strip() == "yes" and row["cs_excluded"].strip().lower() in FALSE_LIKE
    )
    where = "non-excluded rows with os_windows yes"
    return compare("E6", [CHARTER, PLAN, STAGE0], pattern, actual, where)


def evaluate():
    results = [check_a(), check_b()]
    results.extend(check_c())

    tables = {
        name: read_csv(S1 / name)
        for name in (ASSIGNMENT, REGISTRY, CAPABILITY, AUTHORIZATION, ENGINEERING)
    }
    results.extend(check_stage1_counts(tables))
    results.append(check_d6(tables[REGISTRY]))
    results.extend(check_d7(tables[ASSIGNMENT]))
    results.extend(check_d8(tables[ASSIGNMENT]))

    inventory = read_csv(S0 / "04_task_inventory.csv")
    results.append(
        compare("E1", [CHARTER, PLAN, STAGE0], re.compile(r"(?P<n>\d+)\s*条任务"), len(inventory),
                "04_task_inventory.csv rows")
    )
    results.append(
        compare(
            "E2",
            [CHARTER, PLAN, STAGE0],
            re.compile(r"(?P<n>\d+)\s*个行业域"),
            len({row["domain"].strip() for row in inventory}),
            "distinct domain values in 04_task_inventory.csv",
        )
    )
    results.append(check_e3(inventory))
    results.append(
        compare(
            "E4",
            [CHARTER, PLAN, STAGE0],
            re.compile(r"(?P<n>\d+)\s*条是\s*Windows"),
            sum(1 for row in inventory if row["os_windows"].strip() == "yes"),
            "04_task_inventory.csv rows with os_windows yes",
        )
    )
    results.append(check_e5(inventory))
    results.append(check_e6(inventory))
    return results


def main():
    failures = 0
    checked = 0
    for claim_id, status, detail in evaluate():
        checked += 1
        if status == "fail":
            failures += 1
        print(f"{status.upper()} {claim_id}  {detail}")
    print(f"checked {checked} claims, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
