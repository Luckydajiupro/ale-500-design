#!/usr/bin/env python3
"""Check that hand written project documents follow the four writing rules.

Rule 1. The opening lines state what question the file answers.
Rule 2. No reference that forces the reader into another section or file.
Rule 3. Absolute paths are not allowed.
Rule 4. No heading without content.

Frozen stage artifacts keep their original wording, so only the living documents
listed in TARGETS are checked.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TARGETS = [
    "README.md",
    "inputs/README.md",
    "stages/README.md",
    "docs/*.md",
    "stages/*/STAGE.md",
    "stages/*/scripts/README.md",
]

FORBIDDEN = [
    (re.compile(r"见第\s*[0-9一二三四五六七八九十]+"), "指向章节的引用"),
    (re.compile(r"参见"), "指向外部内容的引用"),
    (re.compile(r"详见"), "指向外部内容的引用"),
    (re.compile(r"如前所述|上文所述|前文所述|同前"), "指向前文的引用"),
    (re.compile(r"附录\s*[A-Za-z]"), "指向附录的引用"),
    (re.compile(r"/Users/"), "绝对路径"),
]

PURPOSE_MARKERS = ("这份文件", "本文件", "本项目", "本目录", "本仓库")


def targets():
    seen = []
    for pattern in TARGETS:
        for path in sorted(ROOT.glob(pattern)):
            if path not in seen:
                seen.append(path)
    return seen


def check(path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    problems = []

    head = [line for line in lines[:12] if line.strip() and not line.startswith("#")]
    if not any(marker in "".join(head) for marker in PURPOSE_MARKERS):
        problems.append("开头没有说明这份文件回答什么问题")

    ignore = False
    fenced = False
    for lineno, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if "check-docs:off" in line:
            ignore = True
            continue
        if "check-docs:on" in line:
            ignore = False
            continue
        if ignore or fenced:
            continue
        for pattern, label in FORBIDDEN:
            if pattern.search(line):
                problems.append(f"第 {lineno} 行出现{label}: {line.strip()[:60]}")

    for index, line in enumerate(lines):
        if not re.match(r"^#{2,6}\s", line):
            continue
        rest = lines[index + 1 :]
        has_body = False
        for follow in rest:
            if re.match(r"^#{1,6}\s", follow):
                break
            if follow.strip():
                has_body = True
                break
        if not has_body:
            problems.append(f"标题下面没有内容: {line.strip()}")

    return problems


def main():
    failures = 0
    checked = 0
    for path in targets():
        checked += 1
        problems = check(path)
        rel = path.relative_to(ROOT).as_posix()
        if problems:
            failures += 1
            print(f"FAIL {rel}")
            for problem in problems:
                print(f"  {problem}")
    print(f"checked {checked} documents, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
