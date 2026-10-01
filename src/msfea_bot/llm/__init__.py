"""LLM provider abstraction (CLAUDE.md §3).

Student generation and staff review obtain providers through this module.
Concrete vendor code and purpose-specific configuration stay in this package;
AUB's approved vendor is not yet known.
"""

from functools import lru_cache
from typing import Any, Callable

from msfea_bot.config import settings
from msfea_bot.llm.base import (
    GenerationResult,
    LLMConfigurationError,
    LLMError,
    LLMProvider,
    LLMRateLimitError,
    LLMServiceError,
)

__all__ = [
    "GenerationResult",
    "LLMConfigurationError",
    "LLMError",
    "LLMProvider",
    "LLMRateLimitError",
    "LLMServiceError",
    "get_llm_provider",
    "get_curation_provider",
]


@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProvider:
    """Return the configured LLM provider.

    This factory is the one place that changes when swapping vendors (CLAUDE.md
    §3): add a branch here mapping ``settings.llm_provider`` to a concrete class.
    Reusing one provider also preserves its HTTP connection pool between turns.
    """
    provider = settings.llm_provider.lower()
    if provider == "gemini":
        from msfea_bot.llm.gemini import GeminiProvider

        return GeminiProvider()
    raise NotImplementedError(
        f"LLM provider '{settings.llm_provider}' is not implemented. "
        "Supported: 'gemini' (add others in this factory)."
    )


def get_curation_provider(
    schema: dict[str, Any], *, model: str | None = None,
    before_request: Callable[[], None] | None = None,
) -> LLMProvider:
    """Keep staff model configuration, SDK use and quota accounting in this package."""
    if settings.llm_provider.lower() == "gemini":
        from msfea_bot.llm.gemini import GeminiProvider

        return GeminiProvider(
            model=model or settings.curation_llm_model, response_schema=schema,
            max_output_tokens=6144, timeout_ms=90_000, purpose="curation_",
            retry_transient=True, before_request=before_request,
        )
    raise LLMConfigurationError("The configured provider does not support staff review")


def get_preview_provider(*, before_request: Callable[[], None]) -> LLMProvider:
    """Use the actual student configuration with private preview quota accounting."""
    if settings.llm_provider.lower() == "gemini":
        from msfea_bot.llm.gemini import GeminiProvider
        return GeminiProvider(purpose="curation_preview_", before_request=before_request)
    raise LLMConfigurationError("The configured provider does not support previews")
