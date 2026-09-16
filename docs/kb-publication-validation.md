# KB publication guard — deterministic validation

Implementation stage: Step 4 of `kb-publication-guard-plan.md`.

Draft validation is reproducible and does not call an LLM. FastAPI records a
validation run, durable jobs and an outbox event; the Git-exported n8n workflow
requests the seven named steps from a token-protected worker. Draft vectors
are built only in `VALIDATION_DATABASE_URL`, which must differ from `DATABASE_URL`.
The student-serving `chunks` table is never used as scratch space.

## Fingerprint and invalidation

Each run is bound to the immutable revision content hash, hashes of every normalized
source, the active KB generation, embedding model fingerprint, retrieval settings,
all relevant eval files, application commit, and validator version. A mismatch at
execution or review marks the run stale and blocks the revision. Start a new run;
individual stale results are never reused.

## Required checks

1. `schema_source`: validates scope/program values, unique source locators, exact
   evidence presence and unexpected email/long-number identifiers.
2. `candidate_index`: rebuilds the isolated index from normalized sources, active
   revisions, and the candidate replacing its predecessor.
3. `conflict_review`: retrieves related passages at review depth, records explainable
   exact/numeric/negation flags, and always retains related evidence for a person.
4. `positive_retrieval`: requires the representative question and independent
   paraphrase to retrieve the candidate and expected evidence above the similarity
   threshold.
5. `department_isolation`: tests all five department filters and requires zero
   cross-department candidate retrieval.
6. `unknown_department`: verifies department-only context reaches generation with
   an explicit applicability label.
7. `regression`: compares the current and candidate indexes and blocks newly lost
   golden or multi-premise cases. Existing baseline misses remain visible rather
   than being misreported as candidate regressions.

Every result must exist and pass. A missing, failed, timed-out, skipped or stale
result cannot be waived. Automatic success means only that the deterministic checks
passed. It is not policy approval.

## Mandatory human review

The dashboard presents the immutable draft, source locator and excerpt, related
passages, applicability and explainable flags. With no flags it says “No potential
conflicts flagged”; it never says “conflict-free.” A reviewer must record their name
or role, decision and reason against the exact run fingerprint. Potential flags can
be resolved as a scoped exception or outdated replacement, but a reviewer cannot
override a failed automatic check.

The shared admin token authenticates the action but cannot identify an individual,
so the reviewer label is explicitly self-reported and preserved in the event log.

## Independent conflict coverage

Run:

```text
python -m eval.conflict_gate
```

The frozen seven-case set covers a same-scope numeric contradiction, paraphrased
negation, exact duplicate, valid department exception, differing condition, outdated
replacement and no-conflict case. Candidate-evidence coverage is the release gate;
false-positive flags are reported separately because similarity and token heuristics
cannot prove that natural-language policies agree or conflict.

No preview generation is included in the MVP. That keeps per-draft validation local,
deterministic and free of provider quota/cost.
