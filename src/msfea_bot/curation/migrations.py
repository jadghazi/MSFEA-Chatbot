"""Transactional, versioned database migrations for guarded curation."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import psycopg

from msfea_bot.config import settings

_MIGRATIONS = Path(__file__).with_name("migrations")
_NAME = re.compile(r"^(?P<version>\d{4})_[a-z0-9_]+\.sql$")
_LOCK_ID = 4_771_102_026


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    sql: str
    checksum: str


def available_migrations() -> list[Migration]:
    migrations: list[Migration] = []
    for path in sorted(_MIGRATIONS.glob("*.sql")):
        match = _NAME.fullmatch(path.name)
        if match is None:
            raise RuntimeError(f"Invalid migration filename: {path.name}")
        sql = path.read_text(encoding="utf-8")
        migrations.append(
            Migration(
                version=int(match.group("version")),
                name=path.name,
                sql=sql,
                checksum=hashlib.sha256(sql.encode()).hexdigest(),
            )
        )
    versions = [migration.version for migration in migrations]
    if versions != sorted(set(versions)):
        raise RuntimeError("Curation migration versions must be unique")
    return migrations


def migrate(database_url: str | None = None) -> list[int]:
    """Apply pending migrations atomically and reject modified applied files."""
    applied_now: list[int] = []
    dsn = database_url or settings.database_url
    with psycopg.connect(dsn, autocommit=False, connect_timeout=5) as conn:
        conn.execute("SELECT pg_advisory_xact_lock(%s)", (_LOCK_ID,))
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            " version INTEGER PRIMARY KEY,"
            " name TEXT NOT NULL UNIQUE,"
            " checksum TEXT NOT NULL,"
            " applied_at TIMESTAMPTZ NOT NULL DEFAULT now()"
            ")"
        )
        rows = conn.execute(
            "SELECT version, name, checksum FROM schema_migrations ORDER BY version"
        ).fetchall()
        applied = {int(row[0]): (str(row[1]), str(row[2])) for row in rows}
        migrations = available_migrations()
        known_versions = {migration.version for migration in migrations}
        unknown = sorted(set(applied) - known_versions)
        if unknown:
            raise RuntimeError(f"Database has unknown curation migrations: {unknown}")
        for migration in migrations:
            prior = applied.get(migration.version)
            if prior is not None:
                if prior != (migration.name, migration.checksum):
                    raise RuntimeError(
                        f"Applied migration {migration.version} no longer matches its file"
                    )
                continue
            conn.execute(migration.sql)
            conn.execute(
                "INSERT INTO schema_migrations (version, name, checksum) VALUES (%s, %s, %s)",
                (migration.version, migration.name, migration.checksum),
            )
            applied_now.append(migration.version)
    return applied_now


def migration_status(database_url: str | None = None) -> dict[str, Any]:
    """Return a compact operator-readable migration inventory."""
    dsn = database_url or settings.database_url
    with psycopg.connect(dsn, autocommit=True, connect_timeout=5) as conn:
        exists = conn.execute(
            "SELECT to_regclass('public.schema_migrations') IS NOT NULL"
        ).fetchone()
        if not exists or not exists[0]:
            applied: list[dict[str, Any]] = []
        else:
            rows = conn.execute(
                "SELECT version, name, checksum, applied_at"
                " FROM schema_migrations ORDER BY version"
            ).fetchall()
            applied = [
                {
                    "version": int(row[0]),
                    "name": str(row[1]),
                    "checksum": str(row[2]),
                    "applied_at": row[3].isoformat(),
                }
                for row in rows
            ]
    return {"available": len(available_migrations()), "applied": applied}


def main() -> None:
    applied = migrate()
    print(json.dumps({"applied_now": applied, **migration_status()}, indent=2))


if __name__ == "__main__":
    main()
