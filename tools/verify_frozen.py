#!/usr/bin/env python3
"""Verify inputs/frozen against its FILE_SHA256SUMS.txt manifest.

The manifest has three tab separated columns: sha256, byte size, relative path.
Exit code is 0 only when every listed file matches both size and hash.
"""

import argparse
import hashlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "inputs" / "frozen"
CHUNK = 8 << 20


def load_manifest(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                raise SystemExit(f"line {lineno} does not have three columns: {line!r}")
            digest, size, rel = parts
            rows.append((digest, int(size), rel))
    return rows


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="frozen tree to verify")
    parser.add_argument("--limit", type=int, default=0, help="check only the first N entries")
    parser.add_argument("--every", type=int, default=5000, help="progress interval in files")
    args = parser.parse_args()

    manifest = args.root / "FILE_SHA256SUMS.txt"
    if not manifest.is_file():
        raise SystemExit(f"manifest not found: {manifest}")

    rows = load_manifest(manifest)
    if args.limit:
        rows = rows[: args.limit]

    started = time.time()
    total_bytes = 0
    mismatches = []
    for index, (digest, size, rel) in enumerate(rows, 1):
        target = args.root / rel
        if not target.is_file():
            mismatches.append(f"missing  {rel}")
        else:
            actual_size = target.stat().st_size
            if actual_size != size:
                mismatches.append(f"size     {rel} expected {size} got {actual_size}")
            else:
                if sha256_of(target) != digest:
                    mismatches.append(f"hash     {rel}")
                total_bytes += actual_size
        if args.every and index % args.every == 0:
            elapsed = time.time() - started
            rate = total_bytes / elapsed / 1e6 if elapsed else 0
            print(f"  {index}/{len(rows)} files, {total_bytes / 2**30:.1f} GiB, {rate:.0f} MB/s", flush=True)

    elapsed = time.time() - started
    print(f"checked {len(rows)} entries, {total_bytes / 2**30:.1f} GiB in {elapsed:.0f}s")
    if mismatches:
        print(f"FAIL {len(mismatches)} mismatches", file=sys.stderr)
        for line in mismatches[:50]:
            print(f"  {line}", file=sys.stderr)
        return 1
    print("OK all entries match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
