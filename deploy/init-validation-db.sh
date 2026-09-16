#!/bin/sh
set -eu

database_name="${VALIDATION_DB_NAME:-msfea_validation}"
exists="$(psql -tAc "SELECT 1 FROM pg_database WHERE datname = '${database_name}'")"
if [ "$exists" != "1" ]; then
  psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"${database_name}\""
fi

psql -v ON_ERROR_STOP=1 --dbname "$database_name" -c \
  'CREATE EXTENSION IF NOT EXISTS vector'
