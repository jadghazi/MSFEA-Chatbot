"""CLI: `python -m msfea_bot.observability` — show the unanswered-questions log.

These are the questions the bot escalated because it couldn't answer them from
the KB — i.e. the roadmap for what content to add next (CLAUDE.md §5.9, §5.12).
"""

from __future__ import annotations

from msfea_bot.observability.store import recent_unanswered


def main() -> None:
    rows = recent_unanswered()
    if not rows:
        print("No unanswered/escalated questions logged yet.")
        return
    print(f"Unanswered / escalated questions ({len(rows)}), newest first:")
    for ts, question in rows:
        print(f"  {ts:%Y-%m-%d %H:%M}  {question}")


if __name__ == "__main__":
    main()
