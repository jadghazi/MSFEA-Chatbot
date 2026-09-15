ALTER TABLE curation_validation_runs
    DROP CONSTRAINT curation_validation_runs_revision_id_fingerprint_key;

ALTER TABLE curation_validation_runs
    ADD COLUMN candidate_generation TEXT;

CREATE INDEX curation_validation_runs_fingerprint_idx
    ON curation_validation_runs (revision_id, fingerprint, created_at DESC);
