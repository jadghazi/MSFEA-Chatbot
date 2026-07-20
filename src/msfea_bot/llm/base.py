"""The LLM provider contract.

Every LLM call in the app goes through this interface, so swapping
OpenAI / Azure / Gemini / a local model is a one-file change inside this
package (CLAUDE.md §3).
"""

from typing import Protocol


class LLMProvider(Protocol):
    """Minimal contract a concrete provider must satisfy."""

    def generate(self, prompt: str) -> str:
        """Return the model's completion for a fully-built prompt."""
        ...
