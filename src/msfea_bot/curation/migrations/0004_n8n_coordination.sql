ALTER TABLE curation_publication_attempts
    ADD COLUMN workflow_execution_id TEXT;

CREATE INDEX curation_outbox_retry_idx
    ON curation_outbox (status, available_at, attempts);
