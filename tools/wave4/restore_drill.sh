#!/usr/bin/env bash
# Restore the latest backup into an isolated PostgreSQL container and file roots.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKUP_ROOT="${ALE_BACKUP_ROOT:-$ROOT/work/backups}"
if [ -n "${1:-}" ]; then
  SRC="$1"
else
  SRC="$(ls -dt "$BACKUP_ROOT"/w4-* 2>/dev/null | head -1 || true)"
fi
[ -n "${SRC:-}" ] && [ -f "$SRC/db.dump" ] || {
  echo "no backup with db.dump found; pass a backup directory or run tools/wave4/backup.sh" >&2
  exit 2
}
RESTORE_DB=ale500_restore_db
RESTORE_WEB=ale500_restore_web

cleanup() {
  docker rm -f "$RESTORE_WEB" "$RESTORE_DB" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup
docker run -d --name "$RESTORE_DB" --network ale500_net -e POSTGRES_PASSWORD=ale_local_dev -p 127.0.0.1:55432:5432 postgres:16-alpine >/dev/null
for _ in $(seq 1 60); do
  if docker exec "$RESTORE_DB" pg_isready -U postgres >/dev/null 2>&1; then break; fi
  sleep 1
done
docker exec -i "$RESTORE_DB" psql -U postgres -c "CREATE DATABASE ale500_restore" >/dev/null
docker exec -i "$RESTORE_DB" pg_restore -U postgres -d ale500_restore --no-owner --no-privileges < "$SRC/db.dump"

WEB_IMAGE=$(docker compose -p ale500 images -q web | head -1)
docker run -d --name "$RESTORE_WEB" --network ale500_net -p 127.0.0.1:8089:8080 \
  -e ALE_DB_URL=postgresql://postgres:ale_local_dev@ale500_restore_db:5432/ale500_restore \
  -e ALE_STORAGE_ROOT=/data/objects -e ALE_PACKAGE_ROOT=/data/packages \
  -e ALE_SECRET_PATH=/data/session.key -e ALE_HOST=0.0.0.0 -e ALE_PORT=8080 \
  -v "$SRC/objects:/data/objects:ro" -v "$SRC/packages:/data/packages:ro" \
  "$WEB_IMAGE" >/dev/null

for _ in $(seq 1 60); do
  if curl -sf http://127.0.0.1:8089/healthz >/dev/null 2>&1; then break; fi
  sleep 1
done
curl -sf http://127.0.0.1:8089/healthz
echo
docker exec -i "$RESTORE_DB" psql -U postgres -d ale500_restore -Atc "
  SELECT 'tasks=' || COUNT(*) FROM tasks;
  SELECT 'packages=' || COUNT(*) FROM packages;
  SELECT 'ingests=' || COUNT(*) FROM ingest_records;
"
