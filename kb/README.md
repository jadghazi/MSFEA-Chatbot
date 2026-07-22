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
| `msfea_cdc_kb.md` | Curated CDC knowledge base (internship, IAESTE, CO-OP, career readiness, forms); includes FAQs | Provided by student (batch 1) | 2026-07 | Clean markdown, section-split already. Broader than internship-only. |
| `Summer training guidelines - June 2026.docx` | Official Approved Experience course guidelines | Provided (batch 1) | Jun 2026 | Authoritative for course rules. Contains department contacts + department-specific rules. Tables need clean extraction (python-docx). |
| `Internship Templates and Rubrics- Shared with Committee.docx` | Report/presentation templates + rubrics | Provided (batch 1) | 2026 | Strip committee cover note; keep student-facing templates/rubrics. |
| `MSFEA_AUB_Advanced Experience template font.pptx` | Final-presentation slide template (8 slides) | Provided (batch 1) | 2022 | Template artifact; extract section structure only. |

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
