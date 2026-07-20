"""Generation + guardrails (CLAUDE.md §5.6).

Build a prompt that answers ONLY from retrieved context, cite the source, and
refuse + escalate when context is insufficient (with a similarity-threshold gate
that skips the LLM entirely when nothing clears it). All LLM calls go through the
msfea_bot.llm abstraction.

PLACEHOLDER: no implementation yet — built in the generation phase.
"""
