"""Ingestion pipeline (CLAUDE.md §5.4).

load -> clean/normalize -> chunk -> embed source documents -> store in pgvector.
One command rebuilds the index from source (`python -m msfea_bot.skeleton
ingest`); the vector store is never hand-edited.

Modules: `chunking` (section-aware windowing, ADR-0006) and `embeddings` (local
sentence-transformers model, ADR-0004). Curated admin answers are windowed with
the same rules — see `curation.service` (ADR-0013).

**Known gap.** Chunk frontmatter (`last_updated`, `program`, `department`) is
parsed into `Chunk.metadata` but not persisted: the `chunks` table has no column
for it, so it is dropped at the storage boundary. Backlog B-2 asks for a reserved
`department`/`applies_to` field precisely because retrofitting is expensive once
the index exists. Not yet done.
"""
