# ADR-0032 — Paid student model profile and coherent grounded context

**Status:** Accepted for the local engineering candidate; release separate
**Date:** 2026-10-08
**Decision owner:** Project maintainer authorization; implementation and constructed-set review by Codex

## Context

Students need broad explanations, informal wording, scoped decisions and topic-aware
follow-ups. The general audit found fragmented evidence, missing controlling
conditions, wrong process scope and generation that could answer an earlier task.
The user authorized a paid Gemini student model and local configuration changes,
while deferring Oracle deployment and staff Knowledge Studio alignment.

The [dated audit and evaluation](../../eval/results/student_quality_paid_migration_20261008.md)
separates retrieval coverage, semantic source review and provider availability.
Earlier Lite verification was interrupted; it is not a completed head-to-head
comparison. Paid low-thinking trials still produced material conditional errors.
Higher thinking with the old long prompt did not fix them by itself.

## Options considered

1. **Keep Lite or low thinking and add exceptions to prompts.** Lower cost, but
   remaining errors concern intent and policy conditions. Question-specific
   exceptions would overfit the constructed examples.
2. **Use measured Flash with coherent evidence and a compact current-task prompt.**
   Keeps one generation call, local embeddings and the existing PostgreSQL stack.
   Medium thinking costs more than low but passed the controlled condition sample
   and the independently verified frozen-set/actual-history acceptance.
3. **Use Pro, a second rewriter, reranking or an additional answer judge.** Adds
   cost and operational complexity. Current evidence does not justify these changes;
   previous rewriter testing did not add retrieval gains.

## Decision

Use `gemini-3.8-flash` with explicit medium thinking, a 4096-token ceiling including
reasoning and omission of legacy sampling fields for student generation. Follow
[Google's API migration guidance](https://ai.google.dev/gemini-api/docs/generate-content/latest-model).
Legacy adapter defaults stay configurable; staff curation retains its separate
model and profile. This partially supersedes ADR-0012 for this student profile,
without rewriting its historical decision body.

Keep precise FAQ facts alongside reviewed topic overviews and coherent chunks.
Use bounded reviewed governing links for conditions and exceptions. Preserve
department filters and the 0.60 similarity threshold. Ground answers in canonical
evidence, not overview embedding text or assistant history.

The compact prompt distinguishes current intent, supported synthesis, hypothetical
arithmetic, formal approval and unknown individual records. Earlier user turns
supply references only. Generic relationship references retain their antecedent
even when another operand is named; independent subject changes still omit history.
Do not interpret “no longer required” as a duration request.

## Consequences

The candidate avoids new services, vendors, paid embeddings and extra production
LLM calls. It has higher reasoning cost and visible latency than a minimal profile;
the dated report measures both. The output ceiling is not an answer-length target.
Evaluation pacing has no artificial RPM delay, but spending admission remains.

Exact prompt/profile/source verification makes reuse reviewable, not deterministic.
Transient provider failures and retries remain possible and are retained separately
from policy grading. New evidence or model changes must rerun the relevant frozen
sets and actual-answer conversation chains.

This is local engineering acceptance only. Source-owner approval, independent
human calibration and real pilot outcomes remain separate. Oracle deployment and
staff alignment require their subsequently authorized release work.
