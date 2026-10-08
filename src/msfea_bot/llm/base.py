"""The LLM provider contract.

Every LLM call in the app goes through this interface. Gemini is the implemented
provider; another vendor requires an adapter and verification (AGENTS.md §3).
"""

from dataclasses import dataclass
from typing import Protocol


class LLMError(RuntimeError):
    """Base class for provider failures safe for the API layer to classify."""


class LLMRateLimitError(LLMError):
    """The provider rejected a request because a rate/quota limit was reached."""


class LLMAdmissionError(LLMRateLimitError):
    """Local paid-call protection blocked an attempt before contacting Gemini."""


class LLMServiceError(LLMError):
    """A transient provider/network failure."""


class LLMConfigurationError(LLMError):
    """A key, permission, or model configuration prevents generation."""


@dataclass(frozen=True)
class GenerationResult:
    """Provider-neutral completion text and measured usage metadata."""

    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    cached_tokens: int | None = None
    latency_ms: int | None = None


class LLMProvider(Protocol):
    """Minimal contract a concrete provider must satisfy."""

    def generate(self, prompt: str) -> GenerationResult:
        """Return the model's completion for a fully-built prompt.

        Implementations apply `settings.llm_max_output_tokens` and the configured
        model-supported sampling/reasoning profile to their SDK's own config object
        (ADR-0012 and current configuration guidance). Omit deprecated parameters
        for models that no longer accept them. Legacy sampling settings can reduce
        variation but do not guarantee reproducibility or factual grounding;
        measured answer quality remains necessary. These settings stay out of the
        signature because they are configured globally (AGENTS.md §6).
        """
        ...
