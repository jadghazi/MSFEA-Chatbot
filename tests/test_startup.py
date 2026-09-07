"""Focused tests for pilot startup work that must stay off the request path."""

import pytest


def test_embedding_warmup_executes_inference(monkeypatch: pytest.MonkeyPatch) -> None:
    import msfea_bot.ingestion.embeddings as embeddings

    seen: list[str] = []
    def fake_embed(text: str) -> list[float]:
        seen.append(text)
        return [0.0]

    monkeypatch.setattr(embeddings, "embed_query", fake_embed)
    embeddings.embedding_dim.cache_clear()
    try:
        embeddings.warm_embedding_model()
        assert seen == ["dimension probe"]
    finally:
        embeddings.embedding_dim.cache_clear()


def test_interaction_schema_is_initialized_once(monkeypatch: pytest.MonkeyPatch) -> None:
    import msfea_bot.observability.store as store

    calls: list[object] = []
    connection = object()
    monkeypatch.setattr(store, "_schema_ready", False)
    monkeypatch.setattr(store, "_init_schema", lambda conn: calls.append(conn))

    store._ensure_schema(connection)
    store._ensure_schema(connection)

    assert calls == [connection]
