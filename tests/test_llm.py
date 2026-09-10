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
    def __init__(self, api_key: str = "", **kwargs: Any) -> None:
        self.models = _FakeModels()
        self.http_options = kwargs.get("http_options")


class _RateLimitedModels:
    def generate_content(self, **kwargs: Any) -> _FakeResponse:
        from google.genai import errors

        raise errors.ClientError(
            429,
            {"error": {"code": 429, "message": "quota", "status": "RESOURCE_EXHAUSTED"}},
        )


class _RateLimitedClient:
    def __init__(self, api_key: str = "", **kwargs: Any) -> None:
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
    assert cast(_FakeClient, provider._client).http_options.timeout == 30_000
    assert cast(_FakeClient, provider._client).http_options.retry_options.attempts == 1


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


@pytest.mark.parametrize("text,finish_reason", [("", "STOP"), ("You must complete", "MAX_TOKENS")])
def test_gemini_never_returns_empty_or_truncated_policy_answers(
    monkeypatch: pytest.MonkeyPatch, text: str, finish_reason: str
) -> None:
    pytest.importorskip("google.genai")
    from google import genai

    from msfea_bot.llm import LLMServiceError
    from msfea_bot.llm.gemini import GeminiProvider

    class IncompleteModels:
        def generate_content(self, **kwargs: Any) -> SimpleNamespace:
            return SimpleNamespace(
                text=text, candidates=[SimpleNamespace(finish_reason=finish_reason)]
            )

    monkeypatch.setattr(
        genai, "Client", lambda **kwargs: SimpleNamespace(models=IncompleteModels())
    )
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    with pytest.raises(LLMServiceError):
        GeminiProvider().generate("Question about a policy")


@pytest.mark.parametrize("failure", ["timeout", "429", "500", "503"])
def test_provider_failures_have_bounded_attempts(monkeypatch, failure):
    pytest.importorskip("google.genai")
    from google import genai
    from google.genai import errors
    from msfea_bot.llm import LLMRateLimitError, LLMServiceError
    from msfea_bot.llm.gemini import GeminiProvider

    monkeypatch.setattr("msfea_bot.llm.gemini.sleep", lambda _: None)
    calls = []

    def generate(**kwargs):
        calls.append(1)
        if failure == "timeout":
            raise TimeoutError("private transport details")
        code = int(failure)
        cls = errors.ClientError if code == 429 else errors.ServerError
        raise cls(code, {"error": {"code": code, "message": "private provider details"}})

    monkeypatch.setattr(
        genai,
        "Client",
        lambda **kw: SimpleNamespace(models=SimpleNamespace(generate_content=generate)),
    )
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    with pytest.raises((LLMRateLimitError, LLMServiceError)) as exc:
        GeminiProvider().generate("Requirements?")
    assert "private" not in str(exc.value)
    assert len(calls) == (1 if failure == "429" else 2)

@pytest.mark.parametrize("failure", ["timeout", "503"])
def test_transient_failure_recovers_once_without_logging_private_details(monkeypatch, caplog, failure):
    pytest.importorskip("google.genai")
    from google import genai
    from google.genai import errors
    from msfea_bot.llm.gemini import GeminiProvider

    calls = []

    def generate(**kwargs):
        calls.append(1)
        if len(calls) == 1:
            if failure == "timeout":
                raise TimeoutError("private student text and key")
            raise errors.ServerError(503, {"error": {"message": "private student text and key"}})
        return _FakeResponse()

    monkeypatch.setattr(genai, "Client", lambda **kw: SimpleNamespace(
        models=SimpleNamespace(generate_content=generate)))
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    monkeypatch.setattr("msfea_bot.llm.gemini.sleep", lambda _: None)
    assert GeminiProvider().generate("private question").text == "ok"
    assert len(calls) == 2
    assert "llm_failure" in caplog.text
    assert "retry=True" in caplog.text
    assert "private" not in caplog.text
