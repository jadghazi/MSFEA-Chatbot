# Knowledge base — source of truth

This folder holds the **source documents** the bot answers from. It is the single
source of truth (CLAUDE.md §2, §5.1). The vector store (pgvector) is *derived*
from these files and rebuilt from them with one command — **never hand-edit the
vector store**. Content changes = update files here → re-run ingestion.

## Structure

```
kb/
  source/       original documents exactly as received (PDF/docx/etc.).
                Preserved unchanged, for provenance. TRACKED in git.
  normalized/   cleaned, section-split text derived from source/ (created during
                ingestion; reviewable so the cleaning is auditable). TRACKED.
```

The built vector index lives in `data/` (gitignored) — it is regenerated, never
committed.

## Provenance manifest

Record every document as it lands, so freshness (`last-updated`) is trackable.

| File | What it is | Source / received from | Last updated | Notes |
|------|-----------|------------------------|--------------|-------|
| _(add rows as documents arrive)_ | | | | |

## Adding or updating content later

1. Drop the new/updated file into `kb/source/`.
2. Add/update its row in the manifest above.
3. Re-run ingestion (full rebuild by default — simple and consistent).
4. Add matching questions to the eval golden set and re-run the eval, to confirm
   the new content is retrievable and nothing regressed.

## Rules

- No student-identifying data in here (CLAUDE.md §7).
- Originals in `source/` stay byte-for-byte as received; all cleaning happens in
  the pipeline and lands in `normalized/`.
