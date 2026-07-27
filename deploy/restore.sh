#!/usr/bin/env sh
# Restore the chatbot database from a backup produced by backup.sh.
# WARNING: this overwrites the current contents of the database.
#
# Usage:
#   ./deploy/restore.sh ./backups/msfea-20260727-020000.sql.gz
#
# After restoring, the vector index is already inside the dump; if you restored an
# older dump and have since changed source docs, re-run ingestion:
#   docker compose run --rm app python -m msfea_bot.skeleton ingest
set -eu

FILE="${1:?usage: restore.sh <backup.sql.gz>}"

gunzip -c "$FILE" | docker compose exec -T db psql -U msfea -d msfea

echo "Restored from: $FILE"
