"""Derive live eval cases from the admin-curated answers (ADR-0010 follow-up).

Each *active* curated Q&A is expanded into a retrieval + grounding regression
case **at run time** — it is deliberately NOT written into ``golden_set.jsonl``.

Deriving live is what keeps the eval consistent with the dashboard's edit/retire:
an edit regenerates the case from the current row, and a retire (``active=false``)
makes the case disappear automatically. There is no snapshot in the golden file
to drift out of sync. See docs/progress.md (2026-07-23).

These are *retrieval-and-grounding* checks, not independent quality golds: the
expected text is the same admin answer we indexed, so they verify "does the bot
still retrieve and stay grounded in this curated chunk?" — the #1 place RAG
regresses (CLAUDE.md §2) — rather than answer quality against a separate truth.
"""

from __future__ import annotations

from eval.loader import GoldenItem
from msfea_bot.curation.service import CURATED_SOURCE
from msfea_bot.curation.store import list_curated


def curated_eval_items() -> list[GoldenItem]:
    """Active curated answers as ``GoldenItem``s (all answerable).

    Returns an empty list if the curated table can't be read, so a database
    hiccup degrades to "no curated cases" instead of wiping the file-based eval.
    """
    try:
        rows = list_curated(active_only=True)
    except Exception as exc:  # noqa: BLE001 - don't let a DB issue break the file eval
        print(f"[eval] skipping live curated cases (curated table unavailable): {exc}")
        return []

    return [
        GoldenItem(
            id=f"curated-{c.id}",
            question=c.question,
            expected_answer_or_behavior=c.answer,
            should_refuse=False,
            source_doc=CURATED_SOURCE,
            # The chunk is "Q: <question>\nA: <answer>", so the answer text is
            # verbatim in it — a precise context-recall signal that *this* curated
            # chunk was retrieved (not just any admin-curated chunk).
            evidence=c.answer,
            tags=["curated"],
            is_synthetic=True,
        )
        for c in rows
    ]
