# ADR-0028: Guided Knowledge Studio

Status: superseded by ADR-0029; the resulting workflow was deployed on Oracle on 2026-10-01.

The later [ADR-0029](0029-self-service-studio.md) supersedes the workflow,
routine-model and search-preparation choices below; this record describes the
original slice.

## Decision

Keep the current source → local BGE → pgvector hybrid retrieval → grounded answer
pipeline. Add a staff-only, persisted review step in the existing Python curation
worker. n8n continues sequencing deterministic private validation and publication.
The assistant neither publishes nor edits the serving vector store.

The intake accepts approved guidance, an optional student question and explicit
department/program scope. Structured output supplies a focused title, two natural
questions, an exact verification phrase, quoted comparisons and clarifications.
The model selects numbered statements; Python supplies their literal source text.
Canonical answer text remains verbatim. Questions are test inputs and the focused
Q&A title uses existing chunking; synthetic aliases and rewritten embeddings are
deferred until an independent retrieval experiment justifies them.

Each report records original intake, evidence snapshot, KB generation, model and
prompt version. Unknown sources, invented quotes, malformed responses and missing
verification phrases fail closed. Mixed topics and guidance that cannot answer
the supplied question block draft acceptance. Reviewed content/scope/test questions
cannot change at acceptance; edits require a fresh review.

The immutable accepted revision references its review. Semantic conflict findings
join the existing mandatory human review; deterministic flags are retained.
The original unanswered question cannot be replaced and is privately retrieval-tested.
Feedback remains open until successful publication or explicit dismissal.
Updates to admin-authored entries create successors; official-source policy changes
must follow the existing document-correction path.

## Model and availability

Use a separately configurable Gemini model through the existing provider package.
The project's AI Studio limits on 2026-10-01 showed Flash 3.5/3.7/3.8 at
5 RPM, 250K TPM and 20 RPD each; the student Flash-Lite model had 15 RPM / 500 RPD.
Pro models had no free allowance. Flash supports structured output and 1M-token
input contexts ([Google model documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash)).
This workload needs only a bounded set of relevant passages, not the whole corpus.

Live testing of 3.8, 3.7, 3.6 and 3.5 exposed intermittent 503s, so nominal model
strength is insufficient as a selection criterion. The default is pinned to
3.6 Flash with medium thinking: all six completed cases in its ten-case batch
matched the frozen expected outcomes; four failed because the provider was
unavailable. This is limited evidence, not a ten-case accuracy claim. Flash-Lite
3.1 was more available in early trials but missed important completeness checks
and produced unverifiable reviews. It is not the default for policy judgment.
The remaining uncertainty is explicitly recorded in the quality report. The
manual editor and mandatory publication guard remain available during failures.
Allow one existing-provider transient retry, pace every actual attempt, and audit
the configured per-model daily allowance (default 18 actual attempts). Set it
below the selected model's observed daily quota. Quota errors and invalid reviews are
not retried. These controls preserve student capacity and prevent a retry storm;
they cannot guarantee Gemini free-tier uptime.

## Alternatives

- Rewriting canonical guidance: easier formatting, but introduces policy drift.
  Preserve facts and make staff edits explicit instead.
- Embedding generated aliases/questions in a parallel index: additional tuning,
  migrations and grounding ambiguity without measured benefit yet.
- Putting policy decisions into n8n LLM nodes: splits provider, privacy and authority
  logic. Keep those contracts in Python and retain the existing visual orchestration.
- A conversational agent/tool loop: extra calls and hidden decisions. One structured
  comparison followed by human review is sufficient for this slice.

Validation evidence is recorded in the accompanying implementation review.
