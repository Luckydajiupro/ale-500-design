#!/usr/bin/env bash
# Local integration backup: PostgreSQL custom dump plus both file roots.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$ROOT/docs/evidence/w4/backup}"
mkdir -p "$OUT/objects" "$OUT/packages"

docker compose -p ale500 exec -T db pg_dump -U ale -d ale500 --format=custom > "$OUT/db.dump"
docker compose -p ale500 cp web:/data/objects/. "$OUT/objects/" >/dev/null
docker compose -p ale500 cp web:/data/packages/. "$OUT/packages/" >/dev/null

docker compose -p ale500 exec -T db psql -U ale -d ale500 -Atc "
  SELECT 'tasks=' || COUNT(*) FROM tasks;
  SELECT 'packages=' || COUNT(*) FROM packages;
  SELECT 'ingests=' || COUNT(*) FROM ingest_records;
" > "$OUT/counts.txt"

(cd "$OUT" && shasum -a 256 db.dump counts.txt > SHA256SUMS
 find objects packages -type f -print0 | sort -z | xargs -0 shasum -a 256 >> SHA256SUMS)

echo "backup written to $OUT"
