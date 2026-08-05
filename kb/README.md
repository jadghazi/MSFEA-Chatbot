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

## How normalization is done

`source/` files are converted to clean Markdown in `normalized/` in two steps:

1. **Mechanical extraction (deterministic code).** A parser using `python-docx`
   / `python-pptx` walks each document in reading order and emits a Markdown
   draft — headings, lists, and tables. This step is reproducible.
2. **Assisted curation (human/AI review).** The draft is then cleaned into the
   final file: fix encoding artifacts, split merged sentences, normalize
   headings/bullets, strip non-content (e.g. committee cover notes), and add YAML
   frontmatter (`title`, `source`, `type`, `program`, `last_updated`,
   `department`). This step involves editorial judgment, so the result is
   **verified against the original** (facts, numbers, contacts, tables) before it
   is trusted. Originals in `source/` remain the ground truth for that check.

The `normalized/` Markdown is the **canonical input to ingestion** — the vector
store is rebuilt from it, so it is version-controlled and reviewable. Known
limitation: `python-docx` does not capture hyperlink URLs (only link text).

### Normalized outputs (batch 1)

| Normalized file | From |
|-----------------|------|
| `cdc-knowledge-base.md` | `msfea_cdc_kb.md` (frontmatter added; content unchanged) |
| `summer-training-guidelines-2026.md` | `Summer training guidelines - June 2026.docx` |
| `internship-report-templates-and-rubrics.md` | `Internship Templates and Rubrics- Shared with Committee.docx` (committee note stripped) |
| `final-presentation-slide-template.md` | `MSFEA_AUB_Advanced Experience template font.pptx` |

### Normalized outputs (batch 2)

| Normalized file | From |
|-----------------|------|
| `msfea-cdc-coop-handbook.md` | `msfea-cdc-coop-handbook.pdf` (extracted with `pypdf`; ToC/headers/footnotes stripped). Now the **authoritative CO-OP source** — the CO-OP section in `cdc-knowledge-base.md` was reduced to a pointer to avoid duplicate chunks. The Figure-1 application-timeline (an image) was transcribed from the batch-1 KB; the FEAA 500 syllabus appendix is not included. |

## Provenance manifest

Record every document as it lands, so freshness (`last-updated`) is trackable.

| File | What it is | Source / received from | Last updated | Notes |
|------|-----------|------------------------|--------------|-------|
| `msfea_cdc_kb.md` | Curated CDC knowledge base (internship, IAESTE, CO-OP, career readiness, forms); includes FAQs | Provided by student (batch 1) | 2026-07 | Clean markdown, section-split already. Broader than internship-only. |
| `Summer training guidelines - June 2026.docx` | Official Approved Experience course guidelines | Provided (batch 1) | Jun 2026 | Authoritative for course rules. Contains department contacts + department-specific rules. Tables need clean extraction (python-docx). |
| `Internship Templates and Rubrics- Shared with Committee.docx` | Report/presentation templates + rubrics | Provided (batch 1) | 2026 | Strip committee cover note; keep student-facing templates/rubrics. |
| `MSFEA_AUB_Advanced Experience template font.pptx` | Final-presentation slide template (8 slides) | Provided (batch 1) | 2022 | Template artifact; extract section structure only. |
| `msfea-cdc-coop-handbook.pdf` | Official 10-page MSFEA CO-OP (Cooperative Education) handbook | Provided by student (batch 2) | 2026-07 (received; undated in source) | Authoritative CO-OP reference. **Known extraction gap:** the application-deadline workflow is an image (Figure 1) and the FEAA 500 syllabus (Appendix 1) is not in the text — see the "About this document" note in the normalized file. |

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

- **2026-08-05:** `summer-training-guidelines-2026.md` gained four URLs that were lost in the original normalization (they sat behind anchor text in the .docx) plus three rules supplied by the CDC that are not in the June 2026 file. Both are recorded in that document's "About this document" footer, which is excluded from the index.
