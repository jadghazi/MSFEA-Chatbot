# ADR-0001 — Adopt ADR process + provisional success metrics

**Status:** Accepted
**Date:** 2026-07-20
**Decision owner:** Jad Ghazi

## Context

This is a monitored capstone that will be handed off after graduation
([CLAUDE.md](../../CLAUDE.md) §2, §12). Decisions must be traceable and their
rationale must outlive the author. Separately, we need a Phase 0 Definition of
Done ([CLAUDE.md](../../CLAUDE.md) §5.0) before building, but the department has
**not yet provided** the real source material, a baseline email volume, or
numeric success targets — only the goal: *reduce repetitive student emails by
deflecting questions the guidelines already answer.*

## Options considered

1. **Wait for the department's numbers before defining anything.** Trade-off:
   nothing is documented, no work can start, and the "no content yet" block
   stalls the whole project.
2. **Pick final numeric targets now and treat them as fixed.** Trade-off: fast,
   but bakes guessed thresholds into the project as if they were real — violates
   the eval-driven, no-invented-facts discipline (§2).
3. **Adopt a lightweight ADR process, and write a Definition of Done with
   *provisional* targets explicitly marked `[CONFIRM]`.** Trade-off: slightly
   more upfront structure, but work proceeds now and every provisional number is
   visibly flagged for department sign-off.

## Decision

Option 3. Use ADRs (this folder) for reversible-but-costly decisions, a dated
progress journal ([../progress.md](../progress.md)) for the monitoring trail, and
a Definition of Done ([../definition-of-done.md](../definition-of-done.md)) whose
quantitative targets are marked `[CONFIRM]` until the department ratifies them.

## Consequences

- Work can start immediately on scaffolding, eval harness, and walking skeleton
  using placeholder content, without pretending we have real numbers.
- Every provisional target is auditable and clearly labelled, so the monitor and
  the department can see exactly what still needs their input.
- Overhead risk: the ADR log must stay signal-heavy (see the README) or it
  becomes noise. We accept that discipline cost.
