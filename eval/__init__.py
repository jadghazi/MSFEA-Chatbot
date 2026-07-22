"""Evaluation harness (CLAUDE.md §4).

Golden set + metrics, built before the bot so every later change is measurable.
Two metric families are kept strictly separate (see ADR-0002):
retrieval (recall@k) and answer (Layer-1 deterministic checks now; Layer-2
LLM-judge once the provider and real questions exist).
"""
