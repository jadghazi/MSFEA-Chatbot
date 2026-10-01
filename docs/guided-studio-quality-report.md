# Guided Knowledge Studio — implementation review

Date: 2026-10-01. Base: `93c877b`. Implemented and tested locally; Oracle was not
connected to, migrated, restarted or deployed during this work.

This is the original slice's historical report. The subsequent
[self-service implementation review](studio-self-service-quality-report.md)
records the current model, continuous workflow and measured search preparation.

## Delivered behavior

The subsequent interface rework and historical-diagnostic handling are described
in the [clarity review](guided-studio-clarity-review.md). The checks below record
the original implementation; the progress journal records the follow-up tests.

**Add knowledge** and **Needs attention** open the same guided composer. Staff
provide approved facts, department scope and applicable programs. The assistant
suggests a focused title and realistic questions, checks topic/question coverage,
and compares the proposed claims with existing guidance. Python supplies the
literal quoted statements selected by the model. Full passages stay expandable.

Canonical guidance remains verbatim. Generated questions test retrieval and the
existing Q&A/title representation; they do not become answer evidence. No alias
index, new embedding model, alternative retrieval route or rewritten factual
answer was introduced. Enrichment of embedding text needs a separate experiment.

Private review records contain intake, evidence, model, prompt version, serving
generation and the accepted revision. Edited/stale reviews, unknown statements,
invented verification phrases, malformed responses and replay with different
content cannot authorize a draft. Local privacy checks run before persistence or
model use. Queue admission, leases, pacing and audited provider attempts are bounded.

Saving hands off to the existing n8n/Python publication guard. Semantic findings
join mandatory human review; existing deterministic checks remain authoritative.
No conflict flag disappears merely because the AI calls an entry “new”. A named
review and explicit dashboard confirmation precede publication. Linked feedback
stays open until successful activation. Published admin entries use the composer
for successors; official-source corrections keep their existing editor.

## Automated verification

| Check | Result |
|---|---|
| Python suite | 361 passed, 2 existing skips |
| Final focused assistance/frontend checks | 44 passed, including assisted update integration |
| Existing widget submission tests | 10 passed |
| Ruff and strict mypy (`src eval`) | Passed; 62 typed modules |
| Dashboard JavaScript syntax | Passed |
| Canonical production-depth context recall | 122/124 before and after |
| Faculty, threshold, synthesis, conversation, stress, publication and conflict gates | All passed |
| Stress retrieval | 43/43; 19/19 independent-query parity |

The unchanged misses are `internship-vs-coop` and `faq-cee-exception`. They were not
hidden or counted as new regressions. One stress runner initially refused to
overwrite its earlier result file; a fresh output path passed the gate. See the
[recorded checks](../eval/results/guided_studio_checks_20261001.json).

Tests cover numeric and negated conflicts, exact statement/source verification,
duplicates, department scope, missing details, mixed topics, original-question
coverage, stale generations/rules, privacy, malformed output, quota/interruption,
request deduplication, immutable acceptance and mandatory human review. A regression
failure now supplies the affected question and history for staff inspection.

## Live model results and choice

The frozen [ten-case matrix](../eval/studio_review_set.jsonl) includes invented
guidelines against the real canonical KB. Evaluation submits private review jobs;
it never publishes. Completed reports must match expected judgment and preserve
the supplied answer. Provider failures count as failed cases, not correct judgments.

| Model / prompt | Expected outcomes / 10 | Important observation |
|---|---:|---|
| 3.8 Flash / v1 | 3 | Repeated provider unavailability |
| 3.5 Flash / v1 | 6 | One mixed-topic judgment missed; provider failures |
| 3.7 Flash / v3 | 5 | Completed judgments matched; provider failures |
| 3.6 Flash / v4 | 6 | All six completed judgments matched; four provider failures |
| 3.1 Flash-Lite / v3 | 6 | More available, but completeness/verification failures |
| 3.1 Flash-Lite / v4 and v5 | 5 each | Remaining missing-condition and malformed-review failures |

These are sequential engineering trials with evolving prompts, not a randomized
model ranking. [Compact outcomes](../eval/results/guided_studio_model_trials_20261001.json)
retain the failures. The final v5 contract was also exercised in the actual browser
for a focused addition and a useful three-finding ECE conflict comparison.

The shipped default is **Gemini 3.6 Flash with medium thinking**, independently
configured from the student Flash-Lite model. The full model is a more defensible
choice for policy judgment given these limited results. Its final prompt has not
been proven against every faculty policy; human review remains necessary.
Google documents [structured output and the model's context capacity](https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash)
and [thinking controls](https://ai.google.dev/gemini-api/docs/thinking).
Only a bounded set of relevant passages is needed here.

The project's AI Studio page showed 5 RPM / 20 RPD for full Flash variants and
15 RPM / 500 RPD for the student model and 3.1 Flash-Lite. These are allowances,
not remaining quota; the displayed historical peaks cannot establish today's
remaining requests. Pro had no free allowance. The 2.5 Flash eligibility probe
returned 404; it is not a usable fallback for this project.

Every actual attempt is paced and audited, including at most one transient retry.
The default daily cap is 18; operators must fit it to the selected model's quota.
The disposable Flash-Lite trials used a 50-attempt cap within their observed
500-RPD allowance. Neither invalid reviews nor quota failures are automatically
rerun. The manual editor remains available. Free-tier 503s remain a material
availability limitation; the application cannot promise provider uptime.

## Real dashboard publication test

All examples used an isolated Compose project, databases, volumes and loopback
port. Existing n8n imported and ran the normal publication workflow.

1. A synthetic general CDC-advising entry passed its positive retrieval checks but
   displaced `followup-letter-location`. The seventh check blocked publication.
   Its feedback remained open and the serving index stayed unchanged.
2. A more specific synthetic **Portfolio Review Clinic Hours** entry passed all
   seven checks. The Publish action was absent until the named review. Cancelling
   the inline confirmation kept it as a draft; confirming activated it. Its linked
   question then cleared from Needs attention.
3. Three independently written questions went from having no clinic source to
   finding its complete canonical chunk at **rank 1** (cosines 0.851, 0.888, 0.839).
   This demonstrates content availability; it is not a claim that the ranking
   algorithm itself improved.
4. Two real calls through the unchanged student provider correctly answered the
   closing time and appointment questions, cited the curated source, and carried
   the normal AI disclaimer.
5. A deliberately false ECE voice-over guideline produced exact contradictory
   source claims, scope and source references in the Studio. It was not published.
6. Normal ingestion rebuilt the serving demo to 254 chunks, including its active
   curated source. Production-depth recall was 123/125: the original 122/124 plus
   the retrieved new entry. The original two misses remained unchanged.

Browser QA checked both entry points, refresh recovery, scope/program retention,
real loading states, draft handoff, required review, confirmation cancellation,
publication and queue updates. At 390px the layout had no horizontal overflow.
All source quotations are escaped before presentation formatting. No new dependency
was added. Demo examples must remain in the disposable environment.

## Deployment and remaining limits

The implementation is ready for a reviewed rollout through the existing deployment
procedure. Back up PostgreSQL first; migration 0006 is additive. Set the dedicated
review model and daily cap, and run the existing private worker/n8n stack. Previous
validation runs must be refreshed under the new validator fingerprint; active
student knowledge remains usable.

Before faculty production use, repeat the review matrix with faculty-approved
additions and exceptions, and decide whether the free tier's observed availability
is sufficient. The local demonstration proves the publication/grounding path and
its failure controls; it does not certify policy accuracy or faculty usability.
