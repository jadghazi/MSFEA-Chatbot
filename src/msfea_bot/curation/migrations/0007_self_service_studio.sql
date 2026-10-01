ALTER TABLE curation_assistance ADD COLUMN steps JSONB NOT NULL DEFAULT '[]';
ALTER TABLE curated_revisions ADD COLUMN retrieval_questions JSONB NOT NULL DEFAULT '[]';

CREATE TABLE curation_workspace_jobs (
    id TEXT PRIMARY KEY,
    revision_id BIGINT NOT NULL REFERENCES curated_revisions(id),
    run_id TEXT NOT NULL REFERENCES curation_validation_runs(id),
    kind TEXT NOT NULL CHECK (kind IN ('preview', 'repair')),
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','running','completed','failed')),
    result JSONB NOT NULL DEFAULT '{}',
    error_code TEXT,
    lease_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    UNIQUE (run_id, kind)
);
CREATE INDEX curation_workspace_pending ON curation_workspace_jobs (created_at)
    WHERE status IN ('queued','running');
