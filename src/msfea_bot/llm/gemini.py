"""Google Gemini provider (ADR-0005, provisional).

A concrete implementation of the LLMProvider contract. The SDK is imported
lazily so the core package does not require it unless Gemini is actually used
(install with the `gemini` extra).
"""

from __future__ import annotations

from msfea_bot.config import settings


class GeminiProvider:
    """LLMProvider backed by the Gemini free tier."""

    def __init__(self) -> None:
        from google import genai
        from google.genai import types

        if not settings.llm_api_key:
            raise RuntimeError(
                "LLM_API_KEY is not set. Add your Gemini key to .env "
                "(get one free at https://aistudio.google.com/apikey)."
            )
        self._client = genai.Client(api_key=settings.llm_api_key)
        self._model = settings.llm_model or "gemini-flash-lite-latest"
        # Deterministic decoding (ADR-0012). Built once here rather than per call.
        self._config = types.GenerateContentConfig(
            temperature=settings.llm_temperature,
            seed=settings.llm_seed,
            max_output_tokens=settings.llm_max_output_tokens,
        )

    def generate(self, prompt: str) -> str:
        response = self._client.models.generate_content(
            model=self._model, contents=prompt, config=self._config
        )
        return response.text or ""
