"""LLM provider abstraction (CLAUDE.md §3).

`get_llm_provider()` is the single factory the rest of the app calls. Concrete
providers are added here in the generation phase (§5.6); AUB's approved vendor
is not yet known, so no implementation is wired.
"""

from msfea_bot.config import settings
from msfea_bot.llm.base import LLMProvider

__all__ = ["LLMProvider", "get_llm_provider"]


def get_llm_provider() -> LLMProvider:
    """Return the configured LLM provider.

    PLACEHOLDER: no concrete provider is wired yet. When generation is built
    (§5.6), add provider classes and dispatch on ``settings.llm_provider`` here —
    this factory is the one place that changes when swapping vendors.
    """
    raise NotImplementedError(
        f"PLACEHOLDER: LLM provider '{settings.llm_provider}' is not implemented "
        "yet; concrete providers are added in the generation phase (CLAUDE.md §5.6)."
    )
