#!/usr/bin/env bash
# Optional separate n8n execution/workflow backup. The application curation audit
# remains in deploy/backup.sh; store N8N_ENCRYPTION_KEY separately and securely.
set -euo pipefail

dir="${BACKUP_DIR:-./backups}"
mkdir -p "$dir"
out="$dir/n8n-$(date +%Y%m%d-%H%M%S).sql.gz"
tmp="$(mktemp "$dir/.n8n-backup.XXXXXX")"
trap 'rm -f -- "$tmp"' EXIT

docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec -T n8n-db pg_dump -U n8n n8n | gzip > "$tmp"
if [ -e "$out" ]; then
  echo "Refusing to overwrite existing backup: $out" >&2
  exit 1
fi
mv -- "$tmp" "$out"
trap - EXIT

echo "n8n backup written: $out"
