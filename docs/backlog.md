# Open work and revisit conditions

Reviewed 2026-10-08. This is the active backlog; shipped foundations are described
in [architecture](architecture.md), not retained as "do not build yet" proposals.
These items are not authorization to implement them automatically.

## Current priorities

| Work | Evidence needed / completion condition |
| --- | --- |
| Independently calibrate answer judging | Human source review of the existing faculty calibration sample; report agreement and rubric failures before trusted full-set accuracy claims |
| Measure real pilot value | Agreed cohort/time window and email baseline; distinguish answered/refused/provider-error traffic and collect anonymous feedback |
| Close known retrieval/evidence misses | Inspect failures from the current golden/faculty gates, add independently sourced probes and show improvement without department/condition regressions |
| Institutional handover and AUB embedding | Confirm maintenance/policy owners, escalation contacts, approved provider/quota, host page/CORS and integration acceptance |
| Keep sources current | Obtain policy-owner review of outdated source versions, image-only/extraction gaps and future faculty decisions; retain dated provenance |
| Verify ongoing off-VM recovery | Confirm current application/n8n dumps and encryption key are recoverable; rehearse restores on isolated databases |

## Engineering follow-ups requiring evidence

- **Student external validation:** the
  [paid-model audit](../eval/results/student_quality_paid_migration_20261008.md)
  records completed constructed-set engineering acceptance. The
  [Oracle release](archive/oracle-paid-release-20261008.md) verifies deployed
  source/profile parity and bounded student/Studio smoke checks. General improvements
  cover coherent evidence, governing exceptions, attributes, spelling, process scope
  and current intent. Minor completeness/clarity issues and known retrieval misses
  remain documented. Obtain policy-owner review of normalized changes and independent
  answer calibration before institutional accuracy claims. Studio alignment is
  deployed; no synthetic curated test facts were published. FEAA 500/500A is the
  two-semester sequence, not a conflict. Untagged future approved revisions still
  require scope review. Add independently sourced student questions and real pilot
  observations; preserve department isolation, canonical provenance and the threshold.

- **Dependency reproducibility:** local model weights are pinned, but many runtime
  package ranges are not locked. Evaluate a deliberate lock/update workflow and
  verify ARM64 builds before claiming fully reproducible images.
- **Privacy fail-closed behavior:** name redaction is best effort and depends on the
  local model. Measure failure paths and realistic anonymization before changing
  availability behavior; never claim all personal information is removed.
- **Staff usability and failure quality:** owner/admin walkthroughs exist; a faculty
  usability study does not. Use actual staff tasks to check missing facts, warnings,
  conflicts, stale runs, quotas and recovery without publishing synthetic policies.
- **Capacity and quotas:** observe real traffic, latency, memory and quota use before
  increasing model budgets or worker counts. A second instance requires coordinated
  admission/cache state; no Redis or autoscaling work is currently justified.

## Revisit only when measured need appears

- A second model for student query rewriting: ADR-0027 found no gain over the
  deterministic resolver on the paired set. Revisit only for new reference failures
  and a measured improvement.
- Bulk question-augmented indexing, rerankers or vector indexes: require retrieval
  gains on frozen/holdout cases and acceptable cost/latency. Studio already has a
  bounded measured search-repair path; that is not a general enrichment rollout.
- SSO/multiple staff roles: the pilot uses a shared admin token with self-reported
  reviewer labels. Discuss institutional requirements before adding identity systems.

Department-scoped answers/escalation, feedback review, comparison retrieval,
versioned edit/retire and guided publication are already implemented.
