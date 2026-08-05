# ADR-0013 — Department-scoped answers and escalation routing

**Status:** Accepted
**Date:** 2026-08-05
**Decision owner:** Jad Ghazi

Implements backlog **B-1** (smart escalation routing) and **B-2** (department-specific
answers), both raised 2026-07-20 and deliberately deferred until single-answer
retrieval was solid.

## Context

Several internship rules differ by department, and they **contradict each other**:

| Question | MECH | CEE | IEM |
|---|---|---|---|
| Split into two 4-week periods? | Not allowed | Allowed if ≥1 period is civil/construction | — |
| Final presentation required? | — | — | Generally **not** required |
| Summer course while interning? | If hours are completed | Allowed | — |

Answering a MECH student with CEE's rule is precisely the confidently-wrong answer
CLAUDE.md §1 forbids — worse than refusing, because it looks authoritative.

Separately, every refusal escalated to one generic address, even though the KB lists
a named coordinator per department. B-1's point is that a *well-routed* escalation
still deflects email away from the wrong professor, which is the project's actual goal.

## What the measurement showed

Retrieval was measured before choosing a design (§2, retrieval-before-generation).

**Unscoped retrieval mixes departments.** "Can I split my internship into two 4-week
periods?" returns **four different departments' contradictory rules** in the top-5.

**Exclusion alone is not enough.** For "do I need to give a final presentation?" the
IEM exception sits at **vector rank 8** — outside the top-5 but inside the candidate
pool. Excluding other departments does not promote it, because the chunks ranked
above it are general, not departmental. An IEM student would be told the general rule.

Vector rank of each department's chunk, real KB:

| Question | Ranks |
|---|---|
| Split into two 4-week periods? | CHEM 1, CEE 2, MECH 3, IEM 12, ECE 13 |
| Final presentation? | **IEM 8**, ECE 82, CHEM 97, MECH 107, CEE 148 |

## Decision

**1. Tag chunks by department at ingestion.** Derived from the KB's own
`### Civil and Environmental Engineering (CEE)` headings, matching the parenthesised
abbreviation so general sections that merely mention a department aren't tagged.
Stored in the `metadata` column added during the 2026-07-30 audit — the field
backlog B-2 asked to reserve, now earning its place. 6 of 175 chunks are tagged.

**2. Department-aware retrieval, two mechanisms.**
- **Exclude other departments.** Another department's rule can never be correct for
  this student, and leaving it in actively misleads.
- **Reserve one slot** for the student's own department when its rule reached the
  candidate pool but not the top-k. Bounded to a single slot, and only promotes a
  chunk retrieval already judged relevant — so an irrelevant department rule is never
  forced in. This is the only mechanism that fixes the rank-8 case.

**3. Route escalations to the department coordinator (B-1).** Contacts live in
`msfea_bot/departments.py` as *data*, per B-1's instruction not to hard-code a
constant. The KB remains the source of truth: `tests/test_departments.py` asserts
every address and name still appears in the source document, so the two cannot drift.

**4. Label the answer.** The prompt tells the model which department the student is
in and to say so ("For CEE students: ..."), extending the existing program-labelling
rule. The student can see which rule they were given.

**5. Keep it stateless.** The department lives in the browser's `localStorage` and is
sent per request. No session store, no TTL, no student profile — statelessness stays
a privacy property (§7), and a coarse one-of-five attribute is not identifying.

**6. Treat it as untrusted.** It arrives from a page we don't control, so an unknown
code degrades to an unscoped answer rather than an error. `from_code` is the single
validation point, applied at the API edge.

## Measured result

Context-recall@5 on the four new department cases, with and without scoping:

| Case | Without | With |
|---|---|---|
| `dept-split-cee` | hit | hit |
| `dept-split-mech` | hit | hit |
| `dept-presentation-iem` | **miss** | hit |
| `dept-summer-course-cee` | **miss** | hit |
| | **2/4** | **4/4** |

**No regression on general questions:** context-recall@5 stays **97%** with the same
single known `internship-vs-coop` miss (now over 33 answerable questions, was 29).
General questions pass `department=None` and take a byte-identical retrieval path.

Verified end-to-end against the live API — the same question, three ways:

- CEE → "For CEE students: Yes, internships may be split into two 4-week periods if
  at least one period is in civil or construction engineering."
- MECH → "For MECH students: Internships cannot be split into two separate 4-week
  periods."
- No department → answers with CEE's rule, labelled. *This is the old behaviour, and
  it is why the feature exists:* a MECH student previously got the CEE answer.

Escalation routing confirmed live: ECE → Rafika Dinnawi, CHEM → Adnan Itani,
CEE → Hiam Khoury, none → `fcareer@aub.edu.lb`.

## Consequences

- The two departments that already retrieved correctly still improve: their answer no
  longer competes with three contradictory ones in the same context window.
- A general question asked by a scoped student may spend one slot on their department
  rule. Measured as beneficial, not noise — a CEE student asking about minimum
  duration now also learns their 6-week exception exists.
- **The registry duplicates data held in the KB.** Routing needs a lookup that cannot
  depend on a retrieval hit, so this is deliberate; the drift test is the mitigation.
- **A wrong self-selection produces a confidently wrong answer.** Mitigated by
  labelling every scoped answer with the department and making the choice visibly
  changeable in the widget header. Not eliminated — a student who picks the wrong
  department gets the wrong department's rules, correctly labelled.
- Adding a department later means one entry in `DEPARTMENTS`, a KB section using the
  same heading convention, and one entry in the widget's list.

## Alternatives rejected

- **Prompt-level only** (tell the model the department, don't touch retrieval).
  Rejected on evidence: the IEM rule is not in the context to reason about.
- **Filtering without a reserved slot.** Simpler, but does not fix the rank-8 case.
- **Asking the student's department conversationally.** Needs multi-turn state, which
  the bot deliberately does not have; one tap at the start is cheaper and clearer.
- **Server-side session storage.** Would create a student-conversation store for no
  benefit over `localStorage`.
