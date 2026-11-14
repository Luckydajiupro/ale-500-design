#!/usr/bin/env bash
# Install a single-line model API key for the local Compose stack.
set -euo pipefail

usage() {
  echo "usage: $0 --from-file PATH [--dest PATH]" >&2
  exit 2
}

SRC=""
DEST="$(cd "$(dirname "$0")/../.." && pwd)/.secrets/model_api_key"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --from-file) SRC="${2:-}"; shift 2 ;;
    --dest) DEST="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    *) usage ;;
  esac
done
[ -n "$SRC" ] && [ -f "$SRC" ] || usage

value="$(tr -d '\r\n' < "$SRC")"
case "$value" in
  *[[:space:]]*) echo "key must not contain whitespace" >&2; exit 1 ;;
esac
[ "${#value}" -ge 8 ] || { echo "key must be at least 8 characters" >&2; exit 1; }

mkdir -p "$(dirname "$DEST")"
umask 077
printf '%s' "$value" > "$DEST"
chmod 600 "$DEST"
echo "installed secret at $DEST (content not printed)"
echo "set ALE_MODEL_PROVIDER=openai_compatible, ALE_MODEL_BASE_URL and ALE_MODEL_ID in .env"
