"""Tests for the LLM provider abstraction.

Hermetic: the Gemini SDK client is faked, so nothing here needs an API key or a
network call. Guards ADR-0012 — the audit found sampling params were never set at
all, so these assert they actually reach the SDK.
"""

from __future__ import annotations

from typing import Any

import pytest

from msfea_bot.config import Settings, settings


class _FakeResponse:
    text = "ok"


class _FakeModels:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def generate_content(self, **kwargs: Any) -> _FakeResponse:
        self.calls.append(kwargs)
        return _FakeResponse()


class _FakeClient:
    def __init__(self, api_key: str = "") -> None:
        self.models = _FakeModels()


def test_gemini_passes_sampling_params_to_the_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    from google import genai

    monkeypatch.setattr(genai, "Client", _FakeClient)
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    # Distinctive values, so this proves propagation rather than restating defaults.
    monkeypatch.setattr(settings, "llm_temperature", 0.25)
    monkeypatch.setattr(settings, "llm_seed", 99)
    monkeypatch.setattr(settings, "llm_max_output_tokens", 777)

    from msfea_bot.llm.gemini import GeminiProvider

    provider = GeminiProvider()
    assert provider.generate("a question") == "ok"

    call = provider._client.models.calls[0]
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
