#!/usr/bin/env python3
# 60_final_checksums.py: generate FINAL_CHECKSUMS.sha256 covering every file
# under phase0-final except the checksum file itself. Run LAST, after all other
# files are final.
import hashlib, os

FINAL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(FINAL, "FINAL_CHECKSUMS.sha256")

entries = []
for base, dirs, files in os.walk(FINAL):
    dirs.sort()
    for fn in sorted(files):
        if fn == ".DS_Store" or fn == "FINAL_CHECKSUMS.sha256":
            continue
        p = os.path.join(base, fn)
        rel = os.path.relpath(p, FINAL)
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        entries.append((rel, h))

lines = [f"{h}  {rel}" for rel, h in entries]
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("checksums written:", len(entries), "entries ->", OUT)
print("own sha256:", hashlib.sha256(open(OUT, "rb").read()).hexdigest())