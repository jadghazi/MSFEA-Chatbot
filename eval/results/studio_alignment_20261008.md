# Knowledge Studio alignment — 2026-10-08

Local engineering verification against base `a0caa4d` and the existing dirty
student-quality candidate. Oracle, n8n and serving knowledge were not changed.
This is a dated measurement, not a claim of universal policy accuracy.

## Changes and evidence

| Gap before alignment | Implemented behavior | Verification |
| --- | --- | --- |
| Staff evidence discarded program/process-stage labels and used raw retrieved windows | Main comparison, predecessor evidence, independent finding review, optional writing and its verifier retain applicability. Comparison expands reviewed controlling sections across departments. | Scoped packet/sanitization tests; live stage comparison correctly treats placement and later career support as different claims. |
| A long curated revision could lose a condition in another window | Multi-window revisions carry their immutable revision identity as a bundle. Existing one-hop expansion restores only the same entry/revision's eligible windows. | Actual PostgreSQL expansion excludes another revision, entry and department; stage exclusions still apply. Restored evidence survives final context selection and cannot authorize the similarity gate. |
| Positive checks could count candidate evidence discarded before generation | Original, representative/paraphrase and prepared questions use student retrieval and final answer-context selection. Validator version changed, invalidating earlier check results. | A candidate present in raw retrieval but removed from the actual answer context correctly fails the check. Original tests remain intact. |
| Old previews could stay passed after model/settings changes | Saved answers bind to the student model, output/thinking/sampling settings and generation/provider code. Legacy or mismatched previews block approval and can be retried without rebuilding valid source checks. | API rejection and preview-only recovery tested for changed model, thinking and output ceiling; previous attempts retained in event history. |
| A queued publication could outlive the approved preview profile | Publication rechecks previews before writes. Named approval must follow the latest preview completion. | Current approval passes; a changed profile fails; rerunning previews alone does not reuse earlier approval; a fresh human review restores eligibility. Manual runs without previews retain their existing source/human gates. |

The Describe → Resolve → checks/previews → human publication flow is unchanged.
No new services, dependencies, database migrations, automatic policy interpretation,
topic-specific retrieval patches or extra routine model calls were added. Staff
review/writing remains `gemini-3.1-flash-lite`; actual student previews use the
configured paid student profile. No environment change was needed for this work.

## Verification

All database tests ran through development Compose on the disposable
`msfea-quality-tests` project. Fixtures created separate temporary databases.

- Broader regression run: **211 passed**, covering Studio, curation, complete
  validation, publication, retrieval and generation (938.40 seconds). This run
  started before the final asynchronous publication guard was added.
- Final Studio run after that guard: **98 passed** (220.33 seconds), including
  actual authorization checks, approval after preview refresh and existing private
  repair/resume/suggestion behavior.
- JavaScript: **35 passed**; final `dashboard/studio.js` syntax check passed.
- Ruff: passed; final strict mypy: **114 source files**, no issues.
- Diff whitespace and current-guide link checks passed.

Commands:

```powershell
docker compose -p msfea-quality-tests -f docker-compose.yml -f docker-compose.dev.yml run --rm -e OMP_NUM_THREADS=1 dev pytest -q tests/test_studio_alignment.py tests/test_studio_assistance.py tests/test_studio_suggestions.py tests/test_studio_workspace.py tests/test_curation.py tests/test_curation_validation.py tests/test_curation_publication.py tests/test_retrieval.py tests/test_generation.py
docker compose -p msfea-quality-tests -f docker-compose.yml -f docker-compose.dev.yml run --rm -e OMP_NUM_THREADS=1 dev pytest -q tests/test_studio_workspace.py tests/test_studio_alignment.py tests/test_studio_suggestions.py tests/test_studio_assistance.py
```

## Live staff smoke and retained first attempt

The opt-in [live test](../../tests/test_studio_live_alignment.py) exercises the
existing four-call review and two-call answer suggestion using synthetic private
advising schedules, then one separate process-stage comparison. The LLM calls are
real; evidence is deliberately fixed to test comparison/writing independently
from retrieval, which the deterministic tests cover. No source revision or
publication is created. The isolated index stays unchanged.

Both attempts detected the Thursday/Wednesday schedule conflict, quoted the exact
claims, proposed the existing source's Wednesday answer, disclosed its correction
with source references, and produced no independent-verifier warnings.
The later-support claim was classified **complementary**, explicitly distinguishing
it from the placement rule and requiring no policy decision.

The [first receipt](studio_alignment_live_20261008.json) is retained: its test
failed because it required exactly `new_information` for the stage case. That
assertion was too narrow for the intended acceptance criterion. The corrected
test accepts `new_information` or `complementary`, while still rejecting a false
conflict or policy decision. Production behavior and frozen student datasets were
not changed to obtain a pass. The [fresh seven-call rerun](studio_alignment_live_20261008_retry.json)
passed in 103.28 seconds.

Fourteen total SDK responses across the retained attempts measured approximately
**$0.015965** including reasoning. Maximum-output reservations totalled **$0.131650**;
the test has an explicit per-run $0.20 ceiling and audits retries. Together with
the previous student ledger's $4.546144 conservative estimate, reservations remain
below the authorized $5 evaluation budget. These are estimates, not account-balance
readings. Standard rates were verified in [Google's API pricing](https://ai.google.dev/gemini-api/docs/pricing).

## Acceptance boundary

The requested local Studio alignment is complete. Previously accepted student
results remain historical measurements; this change does not repeat their full
live benchmark. The normalized KB and student generation prompts were not edited
in this Studio task. Existing publication/source confirmation, privacy, department,
refusal and human approval constraints remain in force. No stronger staff model or
workflow redesign is justified by this bounded check.

The approach uses the existing hybrid RAG pipeline, evidence provenance and scoped
context rather than a new retrieval architecture. It is consistent with the
retrieval/metadata considerations in [Microsoft's RAG guidance](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview?tabs=docs).
Deployment and independent policy-owner calibration remain separate work.
