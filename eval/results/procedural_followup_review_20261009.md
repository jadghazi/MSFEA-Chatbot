# Procedural follow-up correction — 2026-10-09

Dated engineering verification, not an independent human accuracy estimate.
Scope: reference resolution and contextual-versus-literal scoring only. No KB,
embedding, threshold, model, system-policy, UI or Studio implementation changes.

## Diagnosis and bounded change

The reported internship → offer preparation → “and once I finish it?” sequence
retrieved completion evidence but refused before generation. The generic offer
question replaced the internship anchor, producing “finish before accepting
offer”; dual retrieval then scored against the unresolved literal fragment.

Generic process-stage objects now retain their parent activity. References to the
offer/form can use that recent object within the activity; completion/start
references use the activity, and a named report/program becomes the new subject.
Named switches bound history. Pure process ellipses use the existing contextual
search and score. Numbers and substantive new conditions retain literal checks.
An unresolved singular status/sign-up reference after an explicit comparison
clarifies locally rather than guessing one compared subject.

This follows the established conversational RAG separation of reference resolution,
retrieval and generation. [LangChain's primary engineering account](https://www.langchain.com/blog/langchain-chat)
explains why retrieval needs a resolved question and why embedding entire history
can contaminate topic switches. We retain the existing deterministic resolver:
no framework, persistent memory or extra LLM rewrite call was introduced.

## Frozen acceptance and results

The [21 probes](../procedural_followup_set.jsonl) and
[two ten-turn-total conversations](../procedural_followup_dialogues.jsonl) were
written before the candidate. Four completion probes also extend the existing
CI/Studio synthesis set; none of its original nine expectations changed.

| Check | Before | Candidate |
| --- | --- | --- |
| Four completion paraphrases: existing similarity gate | 1/4 | 4/4 |
| Reported completion fragment: strongest primary score | 0.53814 | 0.74000 |
| CO-OP duration after generic offer stage: required six-month evidence | missing | present |
| Original conversation evidence gate | prior accepted baseline | 21/21; 9/9 independent retrieval parity |
| Original stress evidence gate | prior accepted baseline | 43/43; 19/19 independent retrieval parity |
| Synthesis: required premises in retrieval, exact model context and gate | 75 existing probes | 79/79, including four new probes |
| Threshold calibration | prior accepted baseline | 165/165 valid pass; 13/20 off-topic blocked locally |
| Golden adaptive-depth evidence | prior accepted baseline | 123/124; existing CEE exception miss remains |
| Faculty expected-document coverage | prior accepted baseline | 199/205; same six existing document misses |

The golden/faculty figures are preservation floors, not answer accuracy. Existing
misses were outside this request and were not patched. Publication/conflict gates
also passed. Five independent/off-topic/injection probes in the paired new set have
identical complete retrieved chunks before and after.

P15 retains a false exact-phrase flag for `8 full weeks`: its highest-ranked
approved EECE-duration passage states **eight full weeks**, and another passage
states **8 weeks**. Both before and after contain the correct rule. We retained
the frozen flag and reviewed the source instead of changing the expectation.

## Live answer source review

Ten actual-history replies and five controls were checked against the approved
passages supplied in their exact model contexts. Thirteen required provider calls;
the unsupported early-leaving fee and comparison clarification returned locally.
No provider failures occurred. Estimated local generation spend: **$0.1030815**,
including reasoning. This is an application estimate, not a provider invoice.

All 15 reviewed replies satisfied their focused criteria:

- Internship completion now lists ordinary exit submissions with the controlling
  ECE final report/presentation deadline of one week after completion.
- The following contact request gives the CDC and ECE course contacts.
- Report focus retains the 5–20-page and 1,500-word ECE requirements; switching to
  CO-OP gives its six-month minimum and correct FEAA 500/500A tuition conditions.
- Rejecting “it” resolves the offer. The reply identifies missing rejection policy
  and gives verified contacts instead of inventing permission.
- CO-OP completion gives documented course/outcome requirements, not the ordinary
  internship exit checklist or a promise of employment.
- Four months remains below CO-OP's documented six-month minimum.
- Unknown conditional tuition information refuses; an ambiguous compared program
  asks which subject without a paid call.

Every accepted live/local trace was rechecked against the final code's resolved
query and exact provider prompt (or identical local response), without extra paid
calls. Dataset, source-code and index hashes are in the
[verification manifest](procedural_followup_manifest_20261009.json).

## Retained evidence and reproduction

- [Before retrieval](procedural_followup_before_20261009.jsonl) and
  [candidate retrieval](procedural_followup_after_20261009.jsonl).
- [Intermediate trial](procedural_followup_trial_20261009.jsonl): review caught that
  reference selection must be separate from the decision to keep numerical literal
  checks. The final candidate resolves constrained completion to the activity.
- [Actual-history replies](procedural_followup_live_20261009.jsonl),
  [controls](procedural_followup_controls_live_20261009.jsonl) and
  [paid ledger](procedural_followup_budget_20261009.jsonl).
- [Original conversation preservation](procedural_preservation_20261009.json) and
  [stress preservation](procedural_stress_20261009.json).

Use the existing audit/dialogue commands in [eval/README](../README.md) on the
isolated development Compose database. Run the ordinary eight deterministic CI
gates after ingestion; no provider is involved. The paired baseline reloaded
unchanged pre-candidate conversation and answer modules at HEAD `48ec7e8` in the
existing audit runner, on the same canonical 246-chunk index.

Verification status: final full-suite and release receipt pending.

An earlier in-progress full-suite run was interrupted after 246 passes and one
`stale_validation` rejection: adding the frozen CI subset during that run changed
its validation fingerprint. The safeguard correctly rejected publication. The
final suite runs against stable source/datasets; no safeguard was weakened.
The initial disposable DB bootstrap attempts failed before retrieval because
pgvector/index tables did not yet exist; initialization was confined to that DB.

## Limits and stopping criterion

This is a measured fix for process ellipses and parent/activity references within
the existing eight-message history. Deterministic English resolution cannot
guarantee every possible ambiguous utterance, and source review here is engineering
review rather than independent student sampling or human calibration. Stop after
the frozen acceptance, existing gates, complete tests and deployment smoke pass;
do not add speculative memory services, topic aliases or a second model call.
