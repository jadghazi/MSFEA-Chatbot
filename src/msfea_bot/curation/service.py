"""Turn curated answers into retrievable chunks and publish new ones."""

from __future__ import annotations

from msfea_bot.curation.store import (
    add_curated_answer,
    deactivate_curated_answer,
    get_curated,
    list_curated,
    update_curated_answer,
)
from msfea_bot.ingestion.chunking import Chunk
from msfea_bot.retrieval.store import delete_chunk, upsert_chunks

CURATED_SOURCE = "admin-curated"


def _to_chunk(curated_id: int, question: str, answer: str, author: str) -> Chunk:
    return Chunk(
        id=f"curated-{curated_id}",
        text=f"Q: {question}\nA: {answer}",
        source_doc=CURATED_SOURCE,
        section=question[:80],
        metadata={"source": CURATED_SOURCE, "author": author},
    )


def curated_chunks() -> list[Chunk]:
    """All active curated answers as chunks (included in a full index rebuild)."""
    return [_to_chunk(c.id, c.question, c.answer, c.author) for c in list_curated(active_only=True)]


def publish_curated_answer(question: str, answer: str, author: str = "") -> int:
    """Store an admin answer and index it immediately (incremental upsert)."""
    curated_id = add_curated_answer(question, answer, author)
    upsert_chunks([_to_chunk(curated_id, question, answer, author)])
    return curated_id


def edit_curated_answer(curated_id: int, question: str, answer: str) -> bool:
    """Update a curated answer's text and re-index its chunk.

    Returns False if the answer doesn't exist or is already retired.
    """
    if not update_curated_answer(curated_id, question, answer):
        return False
    row = get_curated(curated_id)
    if row is not None:
        upsert_chunks([_to_chunk(row.id, row.question, row.answer, row.author)])
    return True


def retire_curated_answer(curated_id: int) -> bool:
    """Deactivate a curated answer and remove its chunk so the bot stops using it.

    The row is kept (inactive) for history; only the retrievable chunk is dropped.
    Returns False if the answer doesn't exist or is already retired.
    """
    if not deactivate_curated_answer(curated_id):
        return False
    delete_chunk(f"curated-{curated_id}")
    return True
