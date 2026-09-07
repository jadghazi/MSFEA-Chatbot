"""LLM provider abstraction (CLAUDE.md §3).

`get_llm_provider()` is the single factory the rest of the app calls. Concrete
providers are added here in the generation phase (§5.6); AUB's approved vendor
is not yet known, so no implementation is wired.
"""

from functools import lru_cache

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
