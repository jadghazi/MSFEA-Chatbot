"""Retrieval (CLAUDE.md §5.5).

Embed the user query, search pgvector, and return the top-k chunks with their
metadata. Tuned independently of the LLM against the retrieval metric (§4) —
when an answer is wrong, we check retrieval first.

PLACEHOLDER: no implementation yet — built in the retrieval phase.
"""
