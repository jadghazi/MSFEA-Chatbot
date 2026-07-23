# ADR-0007 — Observability: interaction logging + anonymization

**Status:** Accepted
**Date:** 2026-07-23
**Decision owner:** Jad Ghazi

## Context

CLAUDE.md §5.9 requires structured logging of every interaction (question,
retrieved chunks, answer, whether it escalated) and, critically, an
**unanswered-questions log** — the roadmap for what KB content to add next. A live
example motivated this: a student asked "how many credits is the internship?",
which the KB doesn't cover; the bot correctly refused, but that signal must be
captured. CLAUDE.md §7 also forbids sending/storing student-identifying data.

## Options considered

1. **Log to a file (JSONL).** Simplest, no DB dependency; but querying the
   unanswered log and feeding a future dashboard is clumsier.
2. **Log to a PostgreSQL table.** We already run Postgres; queryable, and the
   admin dashboard (backlog B-3) can read it directly. Chosen.

For anonymization:
- **Regex-based** (emails + long digit runs) vs **NER-based** name detection.
  Regex chosen for now; NER is heavier and can wait.

## Decision

- **Store interactions in a Postgres `interactions` table** (ts, anonymized
  question, refused, answer, citations, retrieved). Logging is **fail-safe**: any
  logging error is swallowed so it never breaks the student's answer.
- **Anonymize the question once at the API boundary**, and use that anonymized
  text for BOTH the LLM call and the log (satisfies §7 "don't send to the LLM or
  store" for the identifiers we can detect).
- Anonymization strips **emails and long digit sequences** (student IDs, phone
  numbers) and deliberately preserves domain numbers ("8 weeks", "3.3", "75%").
- Surface the unanswered log via `python -m msfea_bot.observability`.

## Consequences

- The unanswered-questions log now exists and is queryable — directly supports
  Phase 12 (grow KB from real demand) and the admin dashboard (B-3/B-3a), which
  can also show `retrieved` chunks for the audit queue.
- **Known limitation:** regex anonymization does **not** reliably strip personal
  names. If a student types their name, it may be stored/sent. Mitigations for
  later: add NER-based redaction, and/or a system-prompt instruction. Tracked as
  a safety follow-up (Phase 8).
- Logging depends on Postgres; if the DB is down, logging silently no-ops and the
  chat still works (fail-safe).
