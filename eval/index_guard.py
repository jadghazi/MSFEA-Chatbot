"""Reject live retrieval evaluation against stale or incomplete canonical inputs."""

from msfea_bot.curation.service import curated_chunks
from msfea_bot.ingestion.chunking import chunk_normalized_dir
from msfea_bot.retrieval.store import _generation_hash, indexed_generation


def canonical_generation() -> str:
    generation = indexed_generation()
    expected = _generation_hash(chunk_normalized_dir() + curated_chunks())
    if generation != expected:
        raise RuntimeError("Evaluation index does not match current canonical inputs; rebuild first")
    return expected
