"""Google Gemini provider (ADR-0005, provisional).

A concrete implementation of the LLMProvider contract. The SDK is imported
lazily so the core package does not require it unless Gemini is actually used
(install with the `gemini` extra).
"""

from __future__ import annotations

import logging
from time import perf_counter, sleep
from typing import Any, Callable

from msfea_bot.config import settings
from msfea_bot.observability.usage import count
from msfea_bot.llm import budget
from msfea_bot.llm.base import (
    GenerationResult,
    LLMConfigurationError,
    LLMError,
    LLMRateLimitError,
    LLMServiceError,
)


class GeminiProvider:
    """LLMProvider backed by the configured Gemini API project."""

    def __init__(
        self, *, model: str | None = None, response_schema: dict[str, Any] | None = None,
        max_output_tokens: int | None = None, timeout_ms: int = 30_000,
        purpose: str = "", retry_transient: bool = True,
        before_request: Callable[[], None] | None = None,
    ) -> None:
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
                timeout=timeout_ms, retry_options=types.HttpRetryOptions(attempts=1)
            ),
        )
        self._model = model or settings.llm_model or "gemini-flash-lite-latest"
        self._purpose = purpose
        self._retry_transient = retry_transient
        self._before_request = before_request
        # Staff curation retains its existing profile. Student previews use the
        # actual student profile, including omission of deprecated SDK fields.
        staff = purpose == "curation_"
        sampling = staff or settings.llm_gemini_use_sampling_params
        thinking = (
            types.ThinkingLevel.MEDIUM if staff
            else types.ThinkingLevel(settings.llm_gemini_thinking_level.upper())
            if settings.llm_gemini_thinking_level else None
        )
        self._config = types.GenerateContentConfig(
            temperature=settings.llm_temperature if sampling else None,
            seed=settings.llm_seed if sampling else None,
            max_output_tokens=max_output_tokens or settings.llm_max_output_tokens,
            response_mime_type="application/json" if response_schema else None,
            response_json_schema=response_schema,
            thinking_config=types.ThinkingConfig(thinking_level=thinking) if thinking else None,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

    def count_input_tokens(self, prompt: str) -> int:
        """Count an evaluation prompt without generating student text."""
        from google.genai import errors
        from httpx import TransportError

        try:
            count_result = self._client.models.count_tokens(model=self._model, contents=prompt)
        except errors.ClientError as exc:
            if exc.code == 429:
                raise LLMRateLimitError("Gemini token counting rate limit reached") from exc
            raise LLMServiceError("Gemini could not count evaluation input") from exc
        except (errors.ServerError, TimeoutError, ConnectionError, TransportError) as exc:
            raise LLMServiceError("Gemini could not count evaluation input") from exc
        if count_result.total_tokens is None:
            raise LLMServiceError("Gemini did not return an input token count")
        return int(count_result.total_tokens)

    def _count(self, name: str, value: int = 1) -> None:
        count(self._purpose + name, value)

    def generate(self, prompt: str) -> GenerationResult:
        from google.genai import errors
        from httpx import TransportError

        started = perf_counter()
        for attempt in range(2 if self._retry_transient else 1):
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
                    round((perf_counter() - started) * 1000),
                    transient and attempt == 0 and self._retry_transient,
                )
                if not transient or attempt == 1 or not self._retry_transient:
                    raise
                self._count("provider_retries")
                sleep(0.5)
        raise AssertionError("unreachable")

    def _generate_once(self, prompt: str) -> GenerationResult:
        # Import here as well as in __init__: the SDK remains an optional extra and
        # importing msfea_bot.llm never forces it on non-Gemini deployments.
        from google.genai import errors, types
        from httpx import TransportError

        started = perf_counter()
        if self._before_request is not None:
            self._before_request()
        try:
            with budget.attempt(
                prompt, self._model, self._config.max_output_tokens or 1024,
                self._purpose, self._config.response_json_schema,
            ) as ticket:
                self._count("llm_calls")
                response = self._client.models.generate_content(
                    model=self._model, contents=prompt, config=self._config
                )
                budget.settle(ticket, getattr(response, "usage_metadata", None))
        except errors.ClientError as exc:
            self._count("provider_errors")
            if exc.code == 429:
                raise LLMRateLimitError("Gemini rate or quota limit reached") from exc
            if exc.code in (408,):
                raise LLMServiceError("Gemini request timed out") from exc
            if exc.code in (401, 403, 404):
                raise LLMConfigurationError("Gemini credentials or model are unavailable") from exc
            raise LLMServiceError("Gemini rejected the request") from exc
        except errors.ServerError as exc:
            self._count("provider_errors")
            raise LLMServiceError("Gemini is temporarily unavailable") from exc
        except (TimeoutError, ConnectionError, TransportError) as exc:
            self._count("provider_errors")
            raise LLMServiceError("Could not reach Gemini") from exc

        usage = getattr(response, "usage_metadata", None)
        for name, field in (
            ("input_tokens", "prompt_token_count"),
            ("output_tokens", "candidates_token_count"),
            ("total_tokens", "total_token_count"),
        ):
            value = getattr(usage, field, None)
            if value is not None:
                self._count(name, value)
        self._count("llm_latency_ms", round((perf_counter() - started) * 1000))
        candidates = getattr(response, "candidates", None) or []
        if candidates and candidates[0].finish_reason == types.FinishReason.MAX_TOKENS:
            self._count("provider_errors")
            raise LLMServiceError("Gemini response was truncated")
        text = response.text or ""
        if not text.strip():
            self._count("provider_errors")
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
