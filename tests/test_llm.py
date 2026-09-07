"""Tests for the LLM provider abstraction.

Hermetic: the Gemini SDK client is faked, so nothing here needs an API key or a
network call. Guards ADR-0012 — the audit found sampling params were never set at
all, so these assert they actually reach the SDK.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

from msfea_bot.config import Settings, settings


class _FakeResponse:
    text = "ok"
    usage_metadata = SimpleNamespace(
        prompt_token_count=123,
        candidates_token_count=17,
        total_token_count=140,
        cached_content_token_count=11,
    )


class _FakeModels:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def generate_content(self, **kwargs: Any) -> _FakeResponse:
        self.calls.append(kwargs)
        return _FakeResponse()


class _FakeClient:
    def __init__(self, api_key: str = "") -> None:
        self.models = _FakeModels()


class _RateLimitedModels:
    def generate_content(self, **kwargs: Any) -> _FakeResponse:
        from google.genai import errors

        raise errors.ClientError(
            429,
            {"error": {"code": 429, "message": "quota", "status": "RESOURCE_EXHAUSTED"}},
        )


class _RateLimitedClient:
    def __init__(self, api_key: str = "") -> None:
        self.models = _RateLimitedModels()


def test_gemini_passes_sampling_params_to_the_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    # The Gemini SDK is an optional extra (CLAUDE.md §3 keeps the core
    # vendor-neutral), so skip rather than fail where only ".[dev]" is installed.
    # CI installs ".[dev,gemini]" so this does run there.
    pytest.importorskip("google.genai")
    from google import genai

    monkeypatch.setattr(genai, "Client", _FakeClient)
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    # Distinctive values, so this proves propagation rather than restating defaults.
    monkeypatch.setattr(settings, "llm_temperature", 0.25)
    monkeypatch.setattr(settings, "llm_seed", 99)
    monkeypatch.setattr(settings, "llm_max_output_tokens", 777)

    from msfea_bot.llm.gemini import GeminiProvider

    provider = GeminiProvider()
    result = provider.generate("a question")
    assert result.text == "ok"
    assert result.input_tokens == 123
    assert result.output_tokens == 17
    assert result.total_tokens == 140
    assert result.cached_tokens == 11
    assert result.latency_ms is not None

    call = cast(_FakeClient, provider._client).models.calls[0]
    assert call["config"].temperature == 0.25
    assert call["config"].seed == 99
    assert call["config"].max_output_tokens == 777


def test_defaults_are_deterministic() -> None:
    """Defaults must stay pinned — creative defaults are what ADR-0012 fixed.

    The seed matters as much as the temperature here: temperature 0 alone was
    measured to still vary Gemini's wording between identical calls.
    """
    assert Settings.model_fields["llm_temperature"].default == 0.0
    assert Settings.model_fields["llm_seed"].default == 42
    assert Settings.model_fields["llm_max_output_tokens"].default == 1024


def test_gemini_maps_provider_429_to_rate_limit_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("google.genai")
    from google import genai

    from msfea_bot.llm import LLMRateLimitError
    from msfea_bot.llm.gemini import GeminiProvider

    monkeypatch.setattr(genai, "Client", _RateLimitedClient)
    monkeypatch.setattr(settings, "llm_api_key", "test-key")

    with pytest.raises(LLMRateLimitError):
        GeminiProvider().generate("a question")


def test_provider_factory_reuses_one_client(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("google.genai")
    from google import genai

    import msfea_bot.llm as llm_module

    monkeypatch.setattr(genai, "Client", _FakeClient)
    monkeypatch.setattr(settings, "llm_provider", "gemini")
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    llm_module.get_llm_provider.cache_clear()
    try:
        assert llm_module.get_llm_provider() is llm_module.get_llm_provider()
    finally:
        llm_module.get_llm_provider.cache_clear()
