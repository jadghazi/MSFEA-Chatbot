# Operational notes

- Baseline uses the unchanged current checkout at `afbe3ab`, 206 existing local
  index chunks, local BGE embeddings, `gemini-flash-lite-latest`, k=7, temperature
  0, seed 42, 1024 output-token cap and the first-result 0.60 gate.
- The `two_step` batch was interrupted after seven completed cases to harden
  runner isolation: reset model/temperature from the saved baseline on every
  invocation. It resumed the remaining five cases after verifying an identical
  manifest. No temperature/model contamination entered a completed experiment.
- `model_swap` attempted `gemini-2.5-flash`, listed by this account's model API,
  but generation returned 404: the model is no longer available to new users and
  the provider recommended `gemini-3.6-flash`. Only the pre-LLM refusal case was
  recorded; this incomplete run has no quality score and is not compared as if
  it tested model capacity. The replacement run is named `model_current`.
- Evaluation requests call the pipeline directly and do not enter pilot
  interaction logs. Fixed synthetic histories isolate follow-up quality.
- Raw evidence-hit arrays preserve the original test probes. Audited reporting
  corrects the too-specific s06 eight-week probe across every saved run, accepting
  the same fact from the Quick Reference or FAQ. See the protocol for rationale.
- The selected run and repeat contain identical answer text, citations and refusal flags for all 12 cases. Latency fields differ. All 12 production prompts match the recorded selected prompts.
- `model_budget` completed eight cases at 4096 output tokens before the alternative model's explicit daily quota stopped the batch. Excluded from aggregate scores; no quota/billing configuration changed.
- `golden_contaminated_discarded` is an INVALID partial verification run: a targeted pytest command mistakenly used the demo DB and fixture chunks affected concurrent retrieval. Stopped it, restored 206 chunks through normal source ingestion, and restarted as `golden_final`. Discarded the contaminated retrieval summary too; the clean rerun has 68/69 expected-evidence recall, not 27/69.
- `local_http.json` records six real HTTP turns against the rebuilt local app, passing actual previous replies (bounded to four messages). These synthetic calls have ordinary local interaction IDs; Oracle was not contacted. Both confirmations are concise and correct; IAESTE switches topics successfully. The summer-course paraphrase supplies the correct ten-week requirement but leads with permission to take the course instead of an explicit No: a remaining directness limitation.
