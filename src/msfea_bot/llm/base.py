"""The LLM provider contract.

Every LLM call in the app goes through this interface, so swapping
OpenAI / Azure / Gemini / a local model is a one-file change inside this
package (CLAUDE.md §3).
"""

from dataclasses import dataclass
from typing import Protocol


class LLMError(RuntimeError):
    """Base class for provider failures safe for the API layer to classify."""


class LLMRateLimitError(LLMError):
    """The provider rejected a request because a rate/quota limit was reached."""


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

        Implementations MUST apply `settings.llm_temperature`, `settings.llm_seed`
        and `settings.llm_max_output_tokens` to their SDK's own config object
        (ADR-0012). Sampling defaults differ per vendor and are usually creative;
        this bot answers only from retrieved context, so decoding must be
        deterministic. Note that temperature alone was measured to be insufficient
        on Gemini — pin the seed too, if the vendor supports one. Sampling params
        stay out of this signature because they are global config (CLAUDE.md §6),
        not per-call state.
        """
        ...
