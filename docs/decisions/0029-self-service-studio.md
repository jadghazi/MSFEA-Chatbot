# ADR-0029: Self-service Studio with measured search preparation

Status: implemented and deployed on Oracle, 2026-10-01. Supersedes ADR-0028's
single-review handoff, routine model and deferred search-preparation decisions.

## Decision

Use one resumable Describe / Resolve / Preview / Publish workspace for direct
intake, unanswered questions and revisions. The existing Python worker makes
four bounded calls: plan searches, compare numbered source claims, prepare
student questions and independently verify coverage and claim relevance.
Specific clarifications stop the flow; staff never have to invent search tests.
The second comparison can dismiss an unrelated match, with its explanation retained.
One format/evidence retry per comparison or verifier is allowed; invalid output
still fails closed. These are explicit stages, not an autonomous tool loop.

Use separately configured Gemini 3.1 Flash-Lite. The project's AI Studio page
showed 15 RPM / 250K TPM / 500 RPD on 2026-10-01, versus 5 RPM / 20 RPD for
full Flash models. Defaults admit 12 attempts/minute and 400/day/model. Calls,
including retries, are audited. The student model and prompt remain independent;
private previews share its provider quota under a separate 60-call daily cap.
Higher RPD does not guarantee availability or correctness.

Version verified search questions as source data, separate from canonical facts.
Six independently written synthetic questions ranked their intended entry first
with both canonical and enriched embeddings: 6/6, MRR 1.0 in both variants.
This supports canonical-first publication, not a claim that enrichment improved
retrieval. Retain prepared questions as unchanged acceptance tests. Only a real
search failure admits one AI search repair; its immutable successor changes
search questions only and requires fresh private checks and staff approval.
For focused single-window entries, approved repair wording supplies embedding
text. Multi-window entries keep canonical embeddings. Keyword search and answer
grounding always use canonical text. Normal ingestion reproduces the index.

Actual previews call the existing student answer pipeline against the private
candidate. Named approval, automatic checks, atomic publication and provenance
stay in the current publication guard. n8n still sequences validation/publication;
model contracts and privacy stay in Python. The shared private candidate cannot
be overwritten by a second validation while checks, repair or previews own it.
Reuse identical source vectors when constructing that candidate.

Resolve equal SQL keyword/vector scores by stable chunk ID. The old advising /
letter failure was caused by unordered keyword ties: identical source text and
vectors produced different rankings after rebuilding. Stable ordering restores
the letter evidence without rewriting an unrelated rule or waiving a test.
The real student follow-up also exposed a distinct reference-resolution error:
the provider acronym was selected instead of the named letter. Prioritize a named
document in that general resolver, without changing the student model or prompt.
Frozen retrieval had no new losses, and the repeated UI follow-up included its form.

## Trade-offs

- Four calls cost more than one, but separate claim relevance from factual
  coverage and expose meaningful feedback. Clarification stops unnecessary work.
- Full Flash models offer deeper reasoning but their 20 RPD allowance is too
  restrictive for routine multi-call use. Do not add an unmeasured Gemma fallback.
- Canonical-first indexing avoids changing embeddings when no benefit is measured.
  Automatic repair remains bounded; persistent retrieval faults may need engineering.
- Actual previews add two student-model calls but reveal the output staff approve.
  AI-generated text remains untrusted and links are rendered with scheme checks.
- Retain the current PostgreSQL worker/n8n architecture. A queue platform,
  separate vector store, frontend framework or parallel retrieval path adds no
  measured value to this scope.

See [the implementation review](../archive/studio-self-service-quality-report.md).
