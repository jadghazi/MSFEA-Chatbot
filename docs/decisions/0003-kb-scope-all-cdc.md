# ADR-0003 — Phase 1 KB scope: all CDC content

**Status:** Accepted
**Date:** 2026-07-22
**Decision owner:** Jad Ghazi

## Context

The first batch of source material (see [kb/README.md](../../kb/README.md)
manifest) covers the whole MSFEA Career Development Center: internships (Approved
Experience), CO-OP, IAESTE, full-time job support, and mentorship — not only the
internship course.

CLAUDE.md §1 originally scoped Phase 1 to *"the internship course only"* and
warns to *"resist scope creep."* But the same section also says a later
expansion *"should mean adding a new content set, not rewriting the system,"* and
the actual product goal is to **deflect repetitive student emails** — students
email the CDC about all of these topics, not just internships.

## Options considered

1. **Internship / Approved Experience only.** Tightest and most on-mandate;
   smallest eval set and system-prompt surface. CO-OP/IAESTE/etc. deferred.
2. **Internship + CO-OP only.** Middle ground — the two most course-like academic
   experience programs.
3. **All CDC content.** Bot answers internship, CO-OP, IAESTE, full-time, and
   mentorship questions. Maximum email deflection. Chosen.

## Decision

**All CDC content** (option 3). Rationale:
- It maximizes the north-star metric (email deflection): students email about the
  whole CDC, so answering the whole CDC deflects the most.
- The content already exists and is coherent (one curated KB + the guidelines).
- Crucially, this is **content-set expansion**, which CLAUDE.md explicitly
  sanctions — *not* a rewrite and *not* new features.

## Consequences

- **The guardrail we still hold: no career-center *features*.** No logins, no
  portals, no per-program workflows — the system stays "RAG over documents." The
  boundary is features, not content. (CLAUDE.md §7 still applies.)
- **Eval + prompt must cover the broader surface.** The golden set, the system
  prompt's in-scope definition, and the refusal boundaries must span internship,
  CO-OP, IAESTE, full-time, and mentorship. Refusal still fires for anything
  outside this CDC content.
- **Don't let breadth dilute internship depth.** Internships are the richest and
  most-emailed area; the eval set must keep strong internship coverage, not just
  spread thin across topics.
- **Supersedes** CLAUDE.md §1's "internship course only" scope line. Proposed:
  update that wording to "the MSFEA CDC content set (internship + CO-OP + IAESTE +
  full-time + mentorship)". Pending owner approval before editing CLAUDE.md.
