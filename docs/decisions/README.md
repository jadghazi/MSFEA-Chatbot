# Architecture decisions

Read [current architecture](../architecture.md) first. ADRs explain the reasoning
and evidence at decision time; accepted bodies are historical, not a second
current runbook. The current task guides and later superseding decisions identify
which behavior is deployed.

Write a short ADR only for an expensive-to-reverse or consequential choice.
Use [the template](0000-adr-template.md), the next unused number, and clear
context/options/decision/consequences. Do not rewrite accepted decisions to match
new behavior; record a superseding decision and update this index.

Two historical files were independently numbered 0025. Their full filenames are
the stable identifiers below; no renumbering changes their existing citations.
ADR-0031 documents the already-deployed October 2 draft-warning change and partially
supersedes ADR-0030. Navigation/rules-file references were repaired during cleanup;
historical measurements and decision content were retained.

## Index

| ADR | Decision | Current relationship |
| --- | --- | --- |
| 0001 | [Adopt ADR process + provisional success metrics](0001-adr-process-and-provisional-metrics.md) | Accepted; success targets remain provisional |
| 0002 | [Evaluation methodology: layered hybrid](0002-evaluation-methodology.md) | Accepted; consult current guides for subsequent refinements |
| 0003 | [Phase 1 KB scope: all CDC content](0003-kb-scope-all-cdc.md) | Accepted; consult current guides for subsequent refinements |
| 0004 | [Embedding model: local bge-small-en-v1.5](0004-embedding-model.md) | Accepted; consult current guides for subsequent refinements |
| 0005 | [Provisional LLM provider: Google Gemini (free tier)](0005-provisional-llm-provider-gemini.md) | Provisional vendor choice; Gemini adapter currently implemented |
| 0006 | [Chunking: section-aware with size-bounded overlapping windows](0006-chunking-strategy.md) | Accepted; consult current guides for subsequent refinements |
| 0007 | [Observability: interaction logging + anonymization](0007-observability-logging.md) | Accepted; consult current guides for subsequent refinements |
| 0008 | [Safety / abuse hardening](0008-safety-hardening.md) | Accepted; consult current guides for subsequent refinements |
| 0009 | [Name redaction via local NER](0009-name-redaction-ner.md) | Accepted; consult current guides for subsequent refinements |
| 0010 | [Admin dashboard + curation feedback loop](0010-admin-curation-dashboard.md) | Dashboard foundation; publication extended by 0026–0031 |
| 0011 | [Hybrid retrieval (semantic + keyword, RRF)](0011-hybrid-retrieval.md) | Accepted; consult current guides for subsequent refinements |
| 0012 | [Deterministic decoding (temperature 0) + an output ceiling](0012-generation-sampling-params.md) | Student profile partially superseded by 0032; historical decision retained |
| 0013 | [Curated answers go through the same windowing as KB content](0013-curated-answer-chunking.md) | Accepted; consult current guides for subsequent refinements |
| 0014 | [Split-table headers are display context, not retrieval text](0014-display-prefix-for-split-tables.md) | Split-table strategy superseded by 0017 |
| 0015 | [Department-scoped answers and escalation routing](0015-department-scoped-answers-and-routing.md) | Accepted; consult current guides for subsequent refinements |
| 0016 | [Actionable links in answers, and the retrieval changes they forced](0016-actionable-links-and-retrieval-depth.md) | Accepted; consult current guides for subsequent refinements |
| 0017 | [Tables are atomic chunks](0017-tables-are-atomic-chunks.md) | Accepted; consult current guides for subsequent refinements |
| 0018 | [Bounded same-chat context and LLM operational failures](0018-bounded-conversation-and-llm-failures.md) | Accepted; consult current guides for subsequent refinements |
| 0019 | [Minimal hardening for a small hosted pilot](0019-small-pilot-hardening.md) | Accepted; consult current guides for subsequent refinements |
| 0020 | [Calibrated pre-LLM similarity threshold of 0.60](0020-calibrated-similarity-threshold.md) | Accepted; consult current guides for subsequent refinements |
| 0021 | [Intent-aware grounded answer planning in one LLM call](0021-intent-aware-grounded-answer-planning.md) | Accepted; consult current guides for subsequent refinements |
| 0022 | [Direct answers and confirmation follow-ups](0022-measured-synthesis-and-followups.md) | Accepted and implemented; later follow-up refinements in 0024/0025/0027 |
| 0023 | [Local usage guards for the single-worker pilot](0023-local-usage-guards.md) | Accepted; consult current guides for subsequent refinements |
| 0024 | [Improve follow-up synthesis without changing the pilot model](0024-followup-answer-quality.md) | Accepted; consult current guides for subsequent refinements |
| 0025 (conversation) | [Current-question-first conversation retrieval](0025-conversation-topic-routing.md) | Accepted; conversation refined by 0027 |
| 0025 (scope) | [Inherit department scope in nested chunks](0025-inherit-department-scope-in-nested-chunks.md) | Accepted; nested scope inheritance implemented |
| 0026 | [Guarded KB publication with n8n coordination](0026-guarded-kb-publication.md) | Accepted; consult current guides for subsequent refinements |
| 0027 | [Keep selective LLM rewriting out of the pilot](0027-conversational-rewrite-evaluation.md) | Accepted; second student rewrite model remains excluded |
| 0028 | [Guided Knowledge Studio](0028-guided-knowledge-studio.md) | Superseded by 0029 |
| 0029 | [Self-service Studio with measured search preparation](0029-self-service-studio.md) | Deployed; optional writing extended by 0030/0031 |
| 0030 | [Optional source-backed answer suggestions](0030-source-backed-answer-suggestions.md) | Deployed; strict draft withholding superseded by 0031 |
| 0031 | [Show private AI drafts with advisory source warnings](0031-advisory-ai-drafts.md) | Deployed in 2601082; private warnings, fresh-review/publish gates retained |
| 0032 | [Paid student profile and coherent grounded context](0032-paid-student-profile-and-context.md) | Accepted; student profile and staff alignment deployed on Oracle October 8 |
