# Documentation index

Reviewed against code through `2601082` on 2026-10-03. Start with
[AGENTS.md](../AGENTS.md) and [architecture](architecture.md); then read the
task-specific guide. These current guides replace scattered implementation plans.

## Current guidance

| Task | Read | Implementation authority |
| --- | --- | --- |
| Understand the system and current status | [Architecture](architecture.md) | `src/msfea_bot/`, Compose, configuration |
| Develop, verify and commit a change | [Development](development.md) | `tests/`, `eval/`, CI |
| Deploy, configure, back up or recover | [Deployment/operations](deployment.md) | `deploy/`, `docker-compose*.yml` |
| Use the staff writing/review workspace | [Knowledge Studio](studio.md) | Dashboard and curation worker |
| Modify validation, versions or publication | [Curation contract](curation.md) | `src/msfea_bot/curation/` |
| Review remaining work | [Backlog](backlog.md) | Verified gaps, not old feature proposals |
| Assess acceptance and handover | [Definition of done](definition-of-done.md) | Outcomes and release evidence |
| Update official knowledge | [KB guide](../kb/README.md) | Source files, normalized files and approved revisions |
| Measure retrieval and answers | [Evaluation guide](../eval/README.md) | Frozen datasets, gates and dated results |

## Decisions and evidence

- [Decision index](decisions/README.md): read the relevant decision, not all ADRs.
  The index identifies superseded behavior and the two historical ADR-0025 filenames.
- [Intake records](intake/): source approval and FAQ conflict decisions.
  Some are inputs to reproducible evaluation tools; preserve their paths.
- [Incident records](incidents/): dated operational investigations.
- [Historical archive](archive/README.md): plans/reviews, rollout receipts and past
  progress. Do not treat archived wording or measurements as current instructions.
- [Evaluation results](../eval/results/): measurements tied to datasets and runs.

## Keep this structure current

Update the affected guide when changing behavior. Keep provider quotas as
project-specific observations, not guaranteed limits. Store measurements with
date, code/configuration and denominator in evidence artifacts rather than copying
scores into every guide. Preserve historical failures and explicitly retried runs.

Superseded implementation checklists have been removed; their current contracts
are in Studio/curation/operations. Accepted ADR bodies and historical reports retain
their original decisions and measurements; navigation references were repaired.
