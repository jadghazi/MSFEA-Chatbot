# ADR-0012 — Deterministic decoding (temperature 0) + an output ceiling

**Status:** Accepted
**Date:** 2026-07-30
**Decision owner:** Jad Ghazi

## Context

A checklist audit of the RAG pipeline (`rag-audit-checklist.md`) found that **no
generation parameters were set anywhere in the project**. `GeminiProvider.generate`
passed only `model` and `contents`, and a repo-wide search for `temperature`,
`top_p`, `seed`, `max_output_tokens` and `generation_config` returned zero hits in
source. The model therefore ran at the vendor's sampling defaults, which for Gemini
means a temperature around 1.0.

This was the audit's only FAIL: unlike `similarity_threshold = 0.0` (a deliberate
"disabled until calibrated" choice, ADR-0001 discipline), there was no configuration
here to have been reasoned about. It was an unconsidered default.

Two distinct problems follow from it:

1. **Correctness.** High-temperature sampling is the regime where a model
   paraphrases loosely, drops a qualifier, or embellishes a number. CLAUDE.md §1
   states a confidently wrong answer about eligibility can harm a student, and this
   bot's whole job is faithful extraction from retrieved text — not writing.
2. **It undermined the project's method.** CLAUDE.md §2 requires showing a metric
   moved before claiming an improvement. At temperature ~1.0 two runs of
   `eval.answer_eval` over *identical* code produce different output, so a small
   change in the false-refusal rate is indistinguishable from sampling noise. The
   eval-driven discipline the whole repo is built on was running on a
   non-deterministic generator.

Problem 2 is why this was fixed first, ahead of more visible bugs: the eval is the
instrument every other change is validated with.

## Options considered

1. **Leave defaults.** Zero work, but keeps both problems. Rejected.
2. **Widen the `LLMProvider.generate` signature** to take `temperature` and
   `max_output_tokens` per call. Makes the requirement explicit at the contract
   level and allows per-call overrides. Cost: every provider must thread parameters
   the SDKs express differently, and there is no current caller that needs to vary
   them per request — premature (CLAUDE.md §2).
3. **Read the settings inside each provider, and state the requirement in the
   Protocol docstring.** Chosen.

## Decision

Option 3.

- Three new settings in `config.py`: `llm_temperature` (default **0.0**),
  `llm_seed` (default **42**) and `llm_max_output_tokens` (default **1024**),
  documented in `.env.example`. All config stays in one place per CLAUDE.md §6.
- `GeminiProvider` builds a `types.GenerateContentConfig` **once in `__init__`**
  from those settings and passes it on every `generate` call.
- `LLMProvider.generate`'s docstring now states that implementations **MUST** apply
  all three, and why. The signature is unchanged, so swapping providers stays a
  one-file change (CLAUDE.md §3).

**The seed was added because temperature 0 alone did not work.** This ADR originally
proposed temperature only; verifying that claim disproved it. Measured 2026-07-30
against `gemini-flash-lite-latest` with a fixed prompt and a fixed index:

| Config | Runs | Distinct answers |
|---|---|---|
| `temperature=0` | 3 | **2** — e.g. "The minimum internship duration is 8 weeks." vs "Based on the provided context, the minimum internship duration is 8 weeks (though CEE and…)" |
| `temperature=0, seed=42` | 3 | **1** |

An end-to-end check through `skeleton.py` reproduced the same variance: two runs of
the same question retrieved *identical* sources but worded the answer differently
("The minimum duration required…" vs "The minimum internship duration required…").
So the variance was in generation, not retrieval — exactly the noise that made the
answer eval unrepeatable.

**Why temperature 0.0 rather than 0.2:** there is no upside to sampling here. The
answer is supposed to be the content of the retrieved chunks; variation across runs
is pure downside, both for students and for the eval. If a future measurement shows
0 causes degenerate repetition, raise it *then*, with the number.

**Why 1024 output tokens:** answers are a short paragraph plus a `SOURCES:` line —
well inside 1024. The ceiling exists to bound a runaway generation against the tight
free-tier quota documented in ADR-0005. If it ever truncates, the `SOURCES:` line is
lost and `parse_answer` falls back to citing the supplied context, which degrades
gracefully rather than failing.

## Consequences

- Answers are now stable for a fixed prompt and index, so `answer_eval` results are
  comparable run-to-run and B3/B4 movements mean something.
- Any future provider (Azure, OpenAI, local) must set these values; the contract
  docstring says so, and this ADR explains why — including the warning that
  temperature alone was empirically insufficient.
- The `placeholder` provider is unaffected (it does not call a model).
- **Honest limits of this.** Stability here is *observed*, not *guaranteed*. Three
  identical runs is a small sample, and Google does not contractually promise
  bit-identical output for a given seed — hosted-inference batching can still
  introduce variance. Two further sources of drift remain deliberately open:
  `LLM_MODEL` is a `-latest` alias, so a model update changes outputs (ADR-0005
  chose the alias for free-tier quota reasons), and any KB re-ingest changes the
  retrieved context. The claim this ADR supports is therefore "sampling noise has
  been removed as a confound in the eval", not "the bot is deterministic".
- If a future measurement shows temperature 0 causing degenerate or truncated
  phrasing, raise it *then*, with the number — do not adjust on a hunch (§2).
