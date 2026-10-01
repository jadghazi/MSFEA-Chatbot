# Self-service Knowledge Studio — implementation review

2026-10-01. Implemented and exercised in a disposable local Compose stack,
then deployed to Oracle after explicit authorization. Oracle's 253-chunk knowledge
and generation hash remained unchanged. See [the deployment verification](oracle-studio-deployment-20261001.md).

## Product result

One resumable **Describe → Resolve → Preview → Publish** workspace handles direct
intake, unanswered questions and updates to published Studio entries. Admins
provide approved facts and their scope. The assistant prepares the title and
student questions, compares literal claims, asks specific clarification questions
and explains its final review. Broad retrieved passages are collapsed into the
source audit rather than presented as the administrator's reading assignment.

Four focused provider calls separate search planning, initial claim comparison,
search-question preparation and independent coverage/claim verification.
Clarification normally stops after the first two. Each stage's feedback is visible.
The verifier checks every initial finding and can explain why two similar passages
govern different claims. It cannot approve a policy or waive a retrieval failure.

After source confirmation, the same page runs all seven private checks and two
actual student-model previews. Staff see the rendered answer, citations and links,
then give named approval. The existing n8n publication guard rebuilds normal serving
knowledge atomically; linked feedback resolves only after successful publication.
Approved revisions retain their author, authority, scope, version and predecessor.

Service failures preserve work and offer the appropriate retry. An interrupted
search correction retries the same bounded job; a completed correction cannot run
again. Approval notes survive refresh, while the authorization checkbox must be
confirmed again. Switching workspaces preserves saved versions and visibly asks
before replacing working guidance. Both desktop and a 375px dashboard frame were
checked; the latter had equal client/scroll width with no horizontal overflow.

## Measured decisions

### Retrieval preparation

Six independently written questions, separate from the generated acceptance
questions, cover synthetic advising and portfolio-clinic entries.

| Index variant | Intended-entry hits | MRR |
|---|---:|---:|
| Serving knowledge before advising publication, clinic already present | 3/6 | 0.50 |
| Both entries, canonical embeddings | 6/6 | 1.00 |
| Both entries, enriched embeddings | 6/6 | 1.00 |

There was **no measured advantage from enrichment**. Normal publication therefore
embeds the canonical content first. Verified AI questions remain unchanged private
acceptance tests. Only an actual retrieval failure permits one search-only repair
and an immutable successor; the facts, scope and original tests cannot change.
Multi-window entries retain canonical section embeddings. This small synthetic
comparison does not establish a general retrieval benefit for other policies.

### Advising / letter failure

Two distinct faults were investigated without changing unrelated policies:

- Equal SQL keyword scores had no deterministic tie order. Rebuilding identical
  official chunks changed the selected evidence. Stable chunk-ID ordering produced
  zero new lost golden cases after the addition and recovered the recorded letter
  check. No test was waived or weakened.
- During real student UI testing, the letter evidence was present but the
  conversational resolver turned “Where do I get it?” into a question about
  “CDC.” A general rule now prioritizes the named document over its provider's
  acronym. Before/after retrieval on 124 frozen evidence cases plus ECE/MECH letter
  variants stayed 124/126, with the same two existing misses and no new losses.
  The repeated ECE UI conversation improved from 1/2 successful turns to 2/2:
  the follow-up returned the exact official form URL, citation and disclaimer.
  The student model and system prompt were unchanged.

### Live AI review

The frozen ten-case review set includes new information, complementary guidance,
duplicates, changed numbers, contradictory scope, negated requirements, missing
conditions, mixed topics, prompt injection and different numbers governing
different claims. The final `self-service-studio-v9` batch returned nine correct
completed assessments and one provider-service failure. Explicitly retrying that
failed case produced **10/10 expected outcomes**; the failed attempt is retained.
That is 9/10 first-batch completion, not a claim of perfect service availability.

The actual mobile contradiction quoted the proposed optional EECE 500 presentation
and the official mandatory presentation/narration claims. It offered **Update
guidance & review again** and hid source confirmation/publication controls.
An official rule cannot be silently replaced by a second contradictory entry.
An intentional change to the same published Studio entry uses the successor path
and still requires a named replacement decision.

The browser walkthrough published advising from Needs attention, then changed the
existing clinic from Thursday to Tuesday with an explicit replacement approval.
Both versions passed all seven checks and two actual previews. The student UI
returned Tuesday clinic hours and unchanged Thursday advising hours. Normal source
ingestion rebuilt **255 chunks with an identical generation hash**. Only the clinic
successor was active, its old Thursday source was absent, and both independently
phrased live questions retrieved their intended entry at rank 1.

## Validation

- Full Python run: **385 passed, 2 skipped**. The last document-reference change
  was then covered by **32 conversation tests**, including its new regression case.
- Node: **24 passed**, covering widget submission/history guards, review
  explanations, external-policy ownership and safe preview links/formatting.
- Ruff and strict mypy passed. No new runtime dependency was added.
- Private integration coverage includes original-question preservation, serving
  index isolation, failed previews, bounded repair, interruption recovery,
  immutable facts, stale review rejection, approval gates and candidate ownership
  during concurrent validation/preview work.

Frozen gates passed again after the final document-reference correction:

| Gate | Result |
|---|---:|
| Golden production context recall | 122/124 |
| Faculty source-document recall | 198/205 |
| Valid queries passing the similarity threshold | 165/165 |
| Off-topic queries blocked before generation | 12/20 |
| Synthesis premise/context/threshold checks | 75/75 |
| Conversation evidence hits | 21/21 |
| Conversation stress evidence hits | 43/43 |
| Independent conversation/stress parity | 9/9 and 19/19 |
| Publication and conflict guards | Passed |

The two existing golden misses are `internship-vs-coop` and `faq-cee-exception`.
The final gate rerun and browser replacement/rebuild results are recorded in the
machine-readable [measurement record](../eval/results/studio_self_service_20261001.json).

## Model and operational limits

The project's AI Studio limits page showed Gemini 3.1 Flash-Lite at **15 RPM /
250K TPM / 500 RPD**, compared with **5 RPM / 20 RPD** for full Flash models.
Routine Studio uses 3.1 Flash-Lite with admission defaults of 12 attempts/minute
and 400/day/model. Four calls mean roughly 100 routine reviews/day before retries,
repairs and other attempts; actual previews have a separate 60-call daily cap and
share the student's provider quota. This is bounded capacity, not unlimited parallel
generation. Recheck project-specific quotas before changing models or aliases.

The existing worker persists and paces calls. Comparison and verifier output may
each receive one format/evidence retry; the provider permits one transient retry.
Every actual provider attempt is counted. There is no silent fallback model.
Using one inference thread under the worker's CPU cap reduced the measured
three-query probe from 3.392s to 0.750s; this supports that deployment setting,
not a general end-user latency claim.

AI checks and previews reduce routine admin work. They do not certify policy
authority or every possible answer. Persistent retrieval faults can still require
technical diagnosis. Legacy manual publication remains available under its existing
guard. No faculty usability study or comprehensive new answer-quality score is
claimed. See [the staff guide](guided-studio-guide.md) and [ADR-0029](decisions/0029-self-service-studio.md).
