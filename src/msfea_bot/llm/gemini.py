"""Google Gemini provider (ADR-0005, provisional).

A concrete implementation of the LLMProvider contract. The SDK is imported
lazily so the core package does not require it unless Gemini is actually used
(install with the `gemini` extra).
"""

from __future__ import annotations

from time import perf_counter

from msfea_bot.config import settings
from msfea_bot.llm.base import (
    GenerationResult,
    LLMConfigurationError,
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
        # Import here as well as in __init__: the SDK remains an optional extra and
        # importing msfea_bot.llm never forces it on non-Gemini deployments.
        from google.genai import errors, types
        from httpx import TransportError

        started = perf_counter()
        try:
            response = self._client.models.generate_content(
                model=self._model, contents=prompt, config=self._config
            )
        except errors.ClientError as exc:
            if exc.code == 429:
                raise LLMRateLimitError("Gemini rate or quota limit reached") from exc
            if exc.code in (408,):
                raise LLMServiceError("Gemini request timed out") from exc
            if exc.code in (401, 403, 404):
                raise LLMConfigurationError("Gemini credentials or model are unavailable") from exc
            raise LLMServiceError("Gemini rejected the request") from exc
        except errors.ServerError as exc:
            raise LLMServiceError("Gemini is temporarily unavailable") from exc
        except (TimeoutError, ConnectionError, TransportError) as exc:
            raise LLMServiceError("Could not reach Gemini") from exc

        candidates = getattr(response, "candidates", None) or []
        if candidates and candidates[0].finish_reason == types.FinishReason.MAX_TOKENS:
            raise LLMServiceError("Gemini response was truncated")
        text = response.text or ""
        if not text.strip():
            raise LLMServiceError("Gemini returned no answer")

        usage = response.usage_metadata
        return GenerationResult(
            text=text,
            input_tokens=getattr(usage, "prompt_token_count", None),
            output_tokens=getattr(usage, "candidates_token_count", None),
            total_tokens=getattr(usage, "total_token_count", None),
            cached_tokens=getattr(usage, "cached_content_token_count", None),
            latency_ms=round((perf_counter() - started) * 1000),
        )
