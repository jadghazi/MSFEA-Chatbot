"""Turn curated answers into retrievable chunks and publish new ones.

Curated answers go through the **same size-bounded windowing as KB content**
(ADR-0013). They used to be indexed as one chunk each, which silently lost most
of a long answer: the embedding model caps at 512 tokens, so a max-size 8000-char
answer had only ~39% of its text embedded and the tail was unreachable by any
query.
"""

from __future__ import annotations

import re

from msfea_bot.curation.revisions import Revision, list_revisions
from msfea_bot.ingestion.chunking import (
    DEFAULT_MAX_CHARS,
    DEFAULT_OVERLAP,
    Chunk,
    split_windows,
)
from msfea_bot.retrieval.store import delete_chunk, delete_chunks

CURATED_SOURCE = "admin-curated"

# The question is repeated on every window (as KB windows repeat their section
# heading) so each stays self-describing. Capped so header + window can't approach
# the embedding model's 512-token limit; the full question is always kept in the
# curated_answers row regardless.
_MAX_HEADER_CHARS = 300


def _chunk_id(curated_id: int, index: int) -> str:
    """Stable per-window id.

    The trailing "-" before the index matters: it makes `curated-1-` an unambiguous
    delete prefix that cannot also match `curated-10-`. That collision is the exact
    footgun `delete_chunk` was originally added to avoid.
    """
    return f"curated-{curated_id}-{index:02d}"


def _as_lines(text: str) -> str:
    """Give the windower line boundaries to split on.

    `split_windows` only breaks on newlines, and an answer typed into the dashboard
    textarea is often one long paragraph — verified to come back as a single
    oversized window. Breaking after sentence endings supplies the boundaries
    without cutting mid-sentence.
    """
    return re.sub(r"(?<=[.!?])[ \t]+", "\n", text.strip())


def _to_chunks(curated_id: int, question: str, answer: str, author: str) -> list[Chunk]:
    """One curated answer as one or more retrievable, size-bounded chunks."""
    header = f"Q: {question[:_MAX_HEADER_CHARS]}"
    windows = split_windows(_as_lines(answer), DEFAULT_MAX_CHARS, DEFAULT_OVERLAP)
    return [
        Chunk(
            id=_chunk_id(curated_id, i),
            text=f"{header}\nA: {window}",
            source_doc=CURATED_SOURCE,
            section=question[:80],
            metadata={"source": CURATED_SOURCE, "author": author},
        )
        for i, window in enumerate(windows)
    ]


def _drop_chunks(curated_id: int) -> None:
    """Remove every chunk belonging to one curated answer.

    Prefix-deletes the windows, then clears the pre-ADR-0013 single-chunk id
    (`curated-<n>`, no window suffix) so answers indexed before windowing don't
    linger after an edit or retire. A full re-ingest truncates either way.
    """
    delete_chunks(f"curated-{curated_id}-")
    delete_chunk(f"curated-{curated_id}")


def curated_chunks() -> list[Chunk]:
    """All active immutable revisions, with reviewed scope, for a full rebuild."""
    chunks: list[Chunk] = []
    for revision in list_revisions():
        if revision.active:
            chunks.extend(revision_chunks(revision))
    return chunks


def revision_chunks(revision: Revision, *, candidate: bool = False) -> list[Chunk]:
    """Window one immutable revision with explicit publish-safe applicability."""
    header = f"Q: {revision.question[:_MAX_HEADER_CHARS]}"
    windows = split_windows(_as_lines(revision.answer), DEFAULT_MAX_CHARS, DEFAULT_OVERLAP)
    prefix = "candidate" if candidate else "curated"
    metadata = {
        "source": CURATED_SOURCE,
        "author": revision.created_by,
        "program": ", ".join(revision.programs),
        "entry_id": str(revision.entry_id),
        "revision_id": str(revision.id),
        "provenance_status": revision.provenance_status,
    }
    # Legacy rows had no reviewed applicability. Omitting the key preserves their
    # pre-migration retrieval behaviour while clearly retaining needs_review; only
    # submitted revisions can carry an explicit department claim.
    if revision.department:
        metadata["department"] = revision.department
    return [
        Chunk(
            id=f"{prefix}-{revision.entry_id}-r{revision.revision_number}-{index:02d}",
            text=f"{header}\nA: {window}",
            source_doc=CURATED_SOURCE,
            section=revision.question[:80],
            metadata=metadata,
        )
        for index, window in enumerate(windows)
    ]
