#!/usr/bin/env python3
"""S1-02B3 audit trail integrity check (6 columns, newline-terminated).

Historical damage at lines 4-5 is kept per the user's instruction and reported
separately. Any other line with a column count other than 6 is a failure.
"""
import sys
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / ".audit" / "s1-02b3.tsv"
LEGACY = {4, 5}


def main() -> int:
    raw = PATH.read_text(encoding="utf-8")
    lines = raw.split("\n")
    body = [(i, ln) for i, ln in enumerate(lines, 1) if ln.strip()]
    bad = [(i, len(ln.split("\t"))) for i, ln in body if len(ln.split("\t")) != 6]
    new_bad = [(i, n) for i, n in bad if i not in LEGACY]
    print(f"lines={len(body)} ends_with_newline={raw.endswith(chr(10))}")
    print(f"legacy_damaged={[i for i, _ in bad if i in LEGACY]}")
    for i, n in new_bad:
        print(f"FAIL line {i}: {n} columns")
    print("OK" if not new_bad and raw.endswith("\n") else "FAIL")
    return 0 if not new_bad and raw.endswith("\n") else 1


if __name__ == "__main__":
    sys.exit(main())