-- First-class focused knowledge documents authored through the admin dashboard.
-- Official normalized files remain immutable; these fields describe a separate,
-- revisioned source whose body is the submitted answer itself.

ALTER TABLE curated_revisions
    ADD COLUMN source_kind TEXT NOT NULL DEFAULT 'official_reference' CHECK (
        source_kind IN ('official_reference', 'admin_authored', 'legacy')
    ),
    ADD COLUMN document_title TEXT NOT NULL DEFAULT '',
    ADD COLUMN authority_label TEXT NOT NULL DEFAULT '',
    ADD COLUMN effective_date DATE,
    ADD COLUMN supporting_reference TEXT NOT NULL DEFAULT '';

-- This is the one migration-time backfill permitted on immutable revision rows.
-- It is transactional and records only a classification that did not exist in
-- the old schema; submitted payloads are not changed.
ALTER TABLE curated_revisions DISABLE TRIGGER curated_revisions_immutable;
UPDATE curated_revisions
SET source_kind = 'legacy'
WHERE provenance_status = 'needs_review';
ALTER TABLE curated_revisions ENABLE TRIGGER curated_revisions_immutable;

ALTER TABLE curated_revisions
    ADD CONSTRAINT admin_authored_source_metadata CHECK (
        source_kind <> 'admin_authored'
        OR (
            length(btrim(document_title)) > 0
            AND length(btrim(authority_label)) > 0
            AND length(btrim(created_by)) > 0
            AND jsonb_array_length(evidence_refs) = 0
        )
    ),
    ADD CONSTRAINT official_reference_source_metadata CHECK (
        source_kind <> 'official_reference'
        OR (
            document_title = ''
            AND authority_label = ''
            AND effective_date IS NULL
            AND supporting_reference = ''
            AND jsonb_array_length(evidence_refs) > 0
        )
    );
