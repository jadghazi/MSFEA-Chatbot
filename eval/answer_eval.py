"""Measure answer quality against the golden set (ADR-0002, Layer 1).

Runs guarded generation for each golden question and reports the deterministic
checks: refusal correctness (split into correct-refusal and false-refusal, per
DoD B3/B4), citation presence, and disclaimer presence.

This calls the LLM once per question, so it uses API quota; a small delay paces
requests for the free tier.

Run: `python -m eval.answer_eval`
"""

from __future__ import annotations

import time

from eval.loader import load_golden_set
from eval.metrics import BotAnswer, citation_present, disclaimer_present
from msfea_bot.generation import generate_answer
from msfea_bot.generation.answer import Answer


def _answer_with_retry(question: str, attempts: int = 6, backoff: float = 20.0) -> Answer:
    """Generate an answer, retrying on transient errors (e.g. free-tier 429s)."""
    for attempt in range(attempts):
        try:
            return generate_answer(question)
        except Exception:  # noqa: BLE001 - retry any transient API error
            if attempt == attempts - 1:
                raise
            time.sleep(backoff)
    raise RuntimeError("unreachable")


def evaluate_answers(delay: float = 13.0) -> None:
    items = load_golden_set()
    refuse_items = [i for i in items if i.should_refuse]
    answerable = [i for i in items if not i.should_refuse]

    correct_refusals = 0  # should_refuse AND refused (B3)
    false_refusals: list[str] = []  # answerable BUT refused (B4)
    missed_refusals: list[str] = []  # should_refuse BUT answered
    citations_ok = 0
    disclaimer_ok = 0

    for item in items:
        ans = _answer_with_retry(item.question)
        ba = BotAnswer(
            text=f"{ans.text} {ans.disclaimer}", citations=ans.citations, refused=ans.refused
        )
        if item.should_refuse and ans.refused:
            correct_refusals += 1
        if item.should_refuse and not ans.refused:
            missed_refusals.append(item.id)
        if not item.should_refuse and ans.refused:
            false_refusals.append(item.id)
        if citation_present(ba):
            citations_ok += 1
        if disclaimer_present(ba, "AI-generated"):
            disclaimer_ok += 1
        time.sleep(delay)

    n = len(items)
    print(f"Answer eval on {n} golden questions ({len(answerable)} answerable, "
          f"{len(refuse_items)} should-refuse)\n")
    print(f"  correct-refusal (B3): {correct_refusals}/{len(refuse_items)}")
    print(f"  false-refusal   (B4): {len(false_refusals)}/{len(answerable)} "
          f"({', '.join(false_refusals) or 'none'})")
    print(f"  missed refusals     : {len(missed_refusals)} "
          f"({', '.join(missed_refusals) or 'none'})")
    print(f"  citation present    : {citations_ok}/{n}")
    print(f"  disclaimer present  : {disclaimer_ok}/{n}")


def main() -> None:
    evaluate_answers()


if __name__ == "__main__":
    main()
