#!/usr/bin/env sh
# Back up the chatbot database (admin-curated answers + interaction logs) to a
# timestamped, compressed SQL file. The vector index is rebuildable from source,
# but curated answers and logs are NOT — back them up.
#
# Run on a schedule in production, e.g. daily via cron:
#   0 2 * * *  cd /opt/msfea-chatbot && ./deploy/backup.sh >> backups/backup.log 2>&1
#
# Usage:
#   ./deploy/backup.sh                 # writes ./backups/msfea-YYYYmmdd-HHMMSS.sql.gz
#   BACKUP_DIR=/mnt/nas ./deploy/backup.sh
set -eu

DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$DIR"
OUT="$DIR/msfea-$(date +%Y%m%d-%H%M%S).sql.gz"

# -T: no TTY (needed when run non-interactively, e.g. from cron).
docker compose exec -T db pg_dump -U msfea msfea | gzip > "$OUT"

echo "Backup written: $OUT"
