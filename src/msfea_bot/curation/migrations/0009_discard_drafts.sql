-- Discard private work without deleting immutable revisions or audit records.
ALTER TABLE curation_revision_state DROP CONSTRAINT curation_revision_state_state_check;
ALTER TABLE curation_revision_state ADD CONSTRAINT curation_revision_state_state_check
    CHECK (state IN ('draft', 'validating', 'blocked', 'ready', 'publishing',
                     'active', 'retired', 'discarded'));
