# Historical evidence archive

These files are dated snapshots, not current instructions for agents.
Start with [AGENTS.md](../../AGENTS.md), [architecture](../architecture.md) and the
[task index](../README.md). Load a report only when investigating that change.

Reports retain their original measured outcomes, failures, retries and limitations.
The historical banner and repaired navigation distinguish them from current guidance.
"Current", "not deployed" or model/limit claims inside a report refer to its recorded
period. The latest optional-draft rule is [ADR-0031](../decisions/0031-advisory-ai-drafts.md).

## Evidence map

| Investigation | Retained evidence |
| --- | --- |
| Early RAG audit and resolved findings | [July audit](rag-audit-20260730.md) |
| Synthesis experiments and failed approaches | [Engineering lessons](engineering-lessons-20260908.md); [raw/result reviews](../../eval/results/synthesis/) |
| API admission/cache audit | [September usage audit](usage-audit.md); current settings in [operations](../deployment.md) |
| Paid-call admission, monitoring and emergency pause | [October 8 safeguard audit](paid-usage-safeguards-20261008.md) |
| Source scope/provenance audit | [Scope audit](kb-scope-provenance-audit.md); subsequent faculty decisions in [intake](../intake/) |
| Publication baseline, guard quality and isolated rehearsal | [Baseline](kb-publication-guard-baseline.md), [quality report](kb-publication-guard-quality-report.md), [operator rehearsal](kb-publication-guard-operations.md) |
| Original guided Studio and clarity investigation | [Original review](guided-studio-quality-report.md), [clarity review](guided-studio-clarity-review.md) |
| Self-service Studio and Oracle rollout | [Quality report](studio-self-service-quality-report.md), [rollout receipt](oracle-studio-deployment-20261001.md) |
| Optional answer writer and subsequent correction trials | [Writer review](studio-answer-suggestion-quality-report.md), [correction review](studio-answer-correction-quality-report.md), [initial rollout receipt](oracle-answer-suggestion-deployment-20261001.md) |
| Paid student profile and general RAG/Studio alignment rollout | [October 8 release receipt](oracle-paid-release-20261008.md) |
| Prelaunch engineering snapshot | [Pilot-readiness snapshot](pilot-readiness.md) |
| Earlier local dashboard/student-page visual reviews | [Dashboard review](dashboard-design-review-2026-09-27.md), [student page review](frontend-design-review-2026-09-27.md); fixtures are not live policy answers |
| Superseded early faculty workbook review | [September 25 draft review](faq-workbook-classification-2026-09-25.md); later approved intake records remain canonical |
| Original chronological capstone journal | [Progress through October 2](progress-through-20261002.md) |

Superseded Studio/publication implementation plans and overlapping technical guides
were removed after their current contracts were consolidated into
[Studio](../studio.md), [curation](../curation.md) and [operations](../deployment.md).
Their original versions remain available in Git history before the documentation
cleanup. Archived references to original plan stages describe historical work,
not missing features. Future dated evidence belongs here or alongside its eval results;
do not resume the old session journal.
