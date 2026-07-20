# Backlog / future considerations

Ideas that are **out of scope for the current phase** but must not be lost.
Nothing here gets built until a phase calls for it ([CLAUDE.md](../CLAUDE.md) §7).
The value of this file is (a) not forgetting, and (b) flagging the cheap
decisions we should make *now* so we don't paint ourselves into a corner later.

---

## B-1 — Smart escalation routing (route refusals to the *right* person)

**Idea (from Jad, 2026-07-20).** When the bot can't answer, don't escalate to a
single generic contact — give the email of the person **most likely to own that
question**, chosen from the question's topic (e.g. eligibility → coordinator X,
forms → office Y).

**Why it matters.** It directly serves the core goal: a well-routed escalation
still deflects email away from the wrong professors, even when the bot itself
can't answer. A generic "email the department" is a weaker deflection.

**Where it fits.** Refines Tier A2 / the escalation step in the Definition of
Done. Builds naturally on Phase 6 (generation + guardrails) and Phase 9
(observability), *after* the basic single-contact escalation works.

**Cheap thing to get right now:** treat the escalation contact as **data, not a
constant** — a small topic→contact mapping (config/table), not a hard-coded
address. That keeps the door open for routing without committing to it. Needs
the department to give us the list of who-owns-what (added to DoD §4 open
questions).

**Do NOT build yet.** Smallest working slice first is a *single* escalation
contact (Phase 6). Routing is a v2 refinement.

---

## B-2 — Department-specific answers (same question, different rule per department)

**Idea (from Jad, 2026-07-20).** Some departments have different rules for the
same question. The bot may need to **ask the student their department** before
answering, or otherwise scope the answer to the right department.

**Why it matters.** This is a *correctness and safety* issue, not a nicety. If
the KB holds department-conditional rules and the bot answers with the wrong
department's rule, that's a confidently-wrong answer of exactly the kind
CLAUDE.md forbids. Better to ask a clarifying question than to guess.

**Architectural implication we must respect NOW (Phase 4 ingestion):**
when we design chunk metadata, include a field like `applies_to` /
`department` (default: "all"). This lets department-conditional content be
represented and lets retrieval filter by department later. It costs almost
nothing to add the field now and is expensive to retrofit once the index exists
and is reproducible. This is a forward-compat decision, **not** building the
feature — we are only reserving the metadata slot.

**Open design questions for when we build it (v2):**
- How does the bot know the student's department? Ask a clarifying question only
  when the retrieved content is department-conditional? (Don't nag every user.)
- Does the widget pass department context, or is it always conversational?
- How is department-conditional content authored in the source docs so
  ingestion can tag it reliably?

**Do NOT build yet.** Note it, reserve the metadata field in Phase 4, revisit as
a v2 feature once single-answer retrieval is solid.

---

## B-3 — Admin / usage analytics dashboard (end-stage)

**Idea (from Jad, 2026-07-20).** The department asked whether usage can be seen.
A founder/admin dashboard showing how the bot is being used — for stakeholders
to view value and to guide what content to improve.

**Why it matters.** It's a real stakeholder ask, and it directly demonstrates
the project's goal: is email volume actually being deflected? It also surfaces
the unanswered-questions log as the roadmap for KB improvements.

**Where it fits.** End-stage. It sits **on top of** the Phase 9 observability
logging ([CLAUDE.md](../CLAUDE.md) §5.9) — the structured interaction log is the
*data source*; the dashboard is just a *view* on it. If Phase 9 logging is done
well, the dashboard is cheap.

**Likely metrics (aggregate only):** questions/day, deflection rate,
escalation rate, 👍/👎 ratings (Layer 4, see [decisions/0002-evaluation-methodology.md](decisions/0002-evaluation-methodology.md)),
top topics asked, and the unanswered-questions list.

**Non-negotiable guardrail — privacy.** Aggregate numbers only. **No
student-identifying data** (names/emails stripped before logging, per
[CLAUDE.md](../CLAUDE.md) §7). The dashboard must never expose individual student
queries in a way that identifies the student.

**Keep it simple (solo student).** A read-only view over the existing log — do
not build a heavy analytics stack or user-management/roles system for it. Resist
turning this into a product of its own.

### B-3a — Feedback review / audit queue (part of the dashboard)

**Idea (from Jad, 2026-07-20).** Answers that got a 👎 surface in the dashboard
as an audit/triage list where an admin can review the failure and act — e.g.
note what the bot *should* have answered, or understand *why* it answered the way
it did, so they know what to improve.

**Why it works.** It turns a raw 👎 into an actionable diagnosis. To do that, the
audit view shows **everything the bot had at answer time** — the data
[CLAUDE.md](../CLAUDE.md) §9 already logs per interaction:
question · retrieved chunks · bot answer · citation · rating · escalated? So this
is a *view* on data we're already capturing, not new plumbing.

**Diagnostic payoff.** Seeing the retrieved chunks lets the admin tell *which
half* failed — the retrieval-vs-generation split at the heart of the project:
- right chunk **not** retrieved → content/search problem (missing info or search miss)
- right chunk retrieved but answer wrong → prompt/generation problem

**Discipline — keep grounding intact.** When an admin records "what it should
have said": if the info genuinely isn't in the official docs, the fix is to
**add it to the source documents and rebuild the KB**, NOT to hard-code a canned
answer (that would sneak ungrounded answers back in). Admin-verified corrections
also make excellent new **golden-set** entries — a past failure becomes a
permanent regression test (ties to [decisions/0002-evaluation-methodology.md](decisions/0002-evaluation-methodology.md)).

**Keep it simple.** A review list with a status (new / reviewed / actioned) and
a notes field. Not a ticketing system.

**Do NOT build yet.** Depends on Phase 9 logging (must log retrieved chunks +
ratings) existing first.

---

## How to promote an item off this backlog

When a phase is ready to take one of these on: write an ADR
([decisions/](decisions/)) capturing the decision and trade-offs, move the work
into that phase, and note it in [progress.md](progress.md).
