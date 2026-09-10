"""Google Gemini provider (ADR-0005, provisional).

A concrete implementation of the LLMProvider contract. The SDK is imported
lazily so the core package does not require it unless Gemini is actually used
(install with the `gemini` extra).
"""

from __future__ import annotations

import logging
from time import perf_counter, sleep

from msfea_bot.config import settings
from msfea_bot.observability.usage import count
from msfea_bot.llm.base import (
    GenerationResult,
    LLMConfigurationError,
    LLMError,
    LLMRateLimitError,
    LLMServiceError,
)


class GeminiProvider:
    """LLMProvider backed by the Gemini free tier."""

    def __init__(self) -> None:
        from google import genai
        from google.genai import types

        if not settings.llm_api_key:
            raise LLMConfigurationError(
                "LLM_API_KEY is not set. Add your Gemini key to .env "
                "(get one free at https://aistudio.google.com/apikey)."
            )
        self._client = genai.Client(
            api_key=settings.llm_api_key,
            http_options=types.HttpOptions(
                timeout=30_000, retry_options=types.HttpRetryOptions(attempts=1)
            ),
        )
        self._model = settings.llm_model or "gemini-flash-lite-latest"
        # Deterministic decoding (ADR-0012). Built once here rather than per call.
        self._config = types.GenerateContentConfig(
            temperature=settings.llm_temperature,
            seed=settings.llm_seed,
            max_output_tokens=settings.llm_max_output_tokens,
        )

    def generate(self, prompt: str) -> GenerationResult:
        from google.genai import errors
        from httpx import TransportError

        started = perf_counter()
        for attempt in range(2):
            try:
                return self._generate_once(prompt)
            except LLMError as exc:
                cause = exc.__cause__
                status = getattr(cause, "code", None)
                transient = (
                    isinstance(cause, (TimeoutError, ConnectionError, TransportError))
                    or isinstance(cause, errors.ServerError) and status in (500, 502, 503, 504)
                    or isinstance(cause, errors.ClientError) and status == 408
                )
                # Never log SDK messages, prompts, URLs or response bodies: they can
                # contain student text or credentials. These fields identify failures.
                logging.getLogger(__name__).warning(
                    "llm_failure model=%s reason=%s cause=%s status=%s attempt=%d elapsed_ms=%d retry=%s",
                    self._model, str(exc), type(cause).__name__, status, attempt + 1,
                    round((perf_counter() - started) * 1000), transient and attempt == 0,
                )
                if not transient or attempt == 1:
                    raise
                count("provider_retries")
                sleep(0.5)
        raise AssertionError("unreachable")

    def _generate_once(self, prompt: str) -> GenerationResult:
        # Import here as well as in __init__: the SDK remains an optional extra and
        # importing msfea_bot.llm never forces it on non-Gemini deployments.
        from google.genai import errors, types
        from httpx import TransportError

        started = perf_counter()
        count("llm_calls")
        try:
            response = self._client.models.generate_content(
                model=self._model, contents=prompt, config=self._config
            )
        except errors.ClientError as exc:
            count("provider_errors")
            if exc.code == 429:
                raise LLMRateLimitError("Gemini rate or quota limit reached") from exc
            if exc.code in (408,):
                raise LLMServiceError("Gemini request timed out") from exc
            if exc.code in (401, 403, 404):
                raise LLMConfigurationError("Gemini credentials or model are unavailable") from exc
            raise LLMServiceError("Gemini rejected the request") from exc
        except errors.ServerError as exc:
            count("provider_errors")
            raise LLMServiceError("Gemini is temporarily unavailable") from exc
        except (TimeoutError, ConnectionError, TransportError) as exc:
            count("provider_errors")
            raise LLMServiceError("Could not reach Gemini") from exc

        usage = getattr(response, "usage_metadata", None)
        for name, field in (
            ("input_tokens", "prompt_token_count"),
            ("output_tokens", "candidates_token_count"),
            ("total_tokens", "total_token_count"),
        ):
            value = getattr(usage, field, None)
            if value is not None:
                count(name, value)
        count("llm_latency_ms", round((perf_counter() - started) * 1000))
        candidates = getattr(response, "candidates", None) or []
        if candidates and candidates[0].finish_reason == types.FinishReason.MAX_TOKENS:
            count("provider_errors")
            raise LLMServiceError("Gemini response was truncated")
        text = response.text or ""
        if not text.strip():
            count("provider_errors")
            raise LLMServiceError("Gemini returned no answer")

        usage = getattr(response, "usage_metadata", None)
        return GenerationResult(
            text=text,
            input_tokens=getattr(usage, "prompt_token_count", None),
            output_tokens=getattr(usage, "candidates_token_count", None),
            total_tokens=getattr(usage, "total_token_count", None),
            cached_tokens=getattr(usage, "cached_content_token_count", None),
            latency_ms=round((perf_counter() - started) * 1000),
        )
