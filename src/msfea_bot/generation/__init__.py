"""Generation + guardrails (CLAUDE.md §5.6).

Builds a prompt that answers ONLY from retrieved context, cites the source, and
refuses + escalates when context is insufficient (with a similarity-threshold
gate). All LLM calls go through the msfea_bot.llm abstraction.
"""

from msfea_bot.generation.answer import Answer, generate_answer

__all__ = ["Answer", "generate_answer"]
