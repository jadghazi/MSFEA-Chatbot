"""Local embedding model (ADR-0004), wrapping sentence-transformers.

Free, offline, no API key. The model is loaded once (cached) and reused.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, cast

from msfea_bot.config import settings

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_model() -> "SentenceTransformer":
    """Load (and cache) the configured sentence-transformers model."""
    from sentence_transformers import SentenceTransformer

    return cast("SentenceTransformer", SentenceTransformer(settings.embedding_model))


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts into normalized vectors (for cosine similarity)."""
    vectors = get_model().encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vectors]


def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([text])[0]


def embedding_dim() -> int:
    """Dimensionality of the embedding vectors (must match the pgvector column)."""
    return len(embed_query("dimension probe"))
