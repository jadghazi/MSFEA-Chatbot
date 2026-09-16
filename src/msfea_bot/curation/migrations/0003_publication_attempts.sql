CREATE TABLE curation_publication_attempts (
    id TEXT PRIMARY KEY,
    revision_id BIGINT NOT NULL REFERENCES curated_revisions(id),
    validation_run_id TEXT NOT NULL REFERENCES curation_validation_runs(id),
    fingerprint TEXT NOT NULL,
    prior_revision_id BIGINT REFERENCES curated_revisions(id),
    status TEXT NOT NULL CHECK (
        status IN (
            'intent', 'committed', 'smoke_passed', 'smoke_failed',
            'compensated', 'compensation_skipped', 'failed_precommit'
        )
    ),
    committed_generation TEXT,
    error_code TEXT,
    error_detail TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    committed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    UNIQUE (revision_id, validation_run_id)
);

CREATE INDEX curation_publication_recovery_idx
    ON curation_publication_attempts (status, committed_at);
