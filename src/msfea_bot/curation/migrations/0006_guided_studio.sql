-- AI reports are advisory snapshots; publication still requires the existing guard.
CREATE TABLE curation_assistance (
    id TEXT PRIMARY KEY,
    request_key TEXT NOT NULL UNIQUE,
    intake JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'completed', 'failed')),
    stage TEXT NOT NULL DEFAULT 'queued',
    model TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    kb_generation TEXT,
    evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
    report JSONB,
    error_code TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    lease_expires_at TIMESTAMPTZ,
    accepted_revision_id BIGINT UNIQUE REFERENCES curated_revisions(id)
);
CREATE INDEX curation_assistance_queue_idx ON curation_assistance (status, created_at);
