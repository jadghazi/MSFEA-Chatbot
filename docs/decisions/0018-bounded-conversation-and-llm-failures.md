# ADR-0018 — Bounded same-chat context and LLM operational failures

**Status:** Accepted
**Date:** 2026-09-07
**Decision owner:** Jad Ghazi

## Context

The single-turn API cannot resolve follow-ups such as “Where do I get it?” after a
question about an employer support letter. The pilot must remain usable on Gemini's
free tier and must not remember students across chats. Google's current documentation
says chat helpers resend full history on each turn, while free-tier limits are enforced
per project across RPM, input TPM and RPD and vary by model/account. Blindly retaining
the full chat or spending a second generation request on query rewriting would therefore
consume the scarce resources without improving the grounded evidence itself.

Measured before this decision:

- `gemini-flash-lite-latest` reports a 1,048,576-token input limit, so overflow is not
  the practical pilot constraint.
- The existing `top_k=7` prompt for “Where do I get it?” is 6,644 characters / 1,710
  Gemini input tokens before any conversation history.
- A contextual retrieval query concentrated the CO-OP “Is it mandatory?” results from
  one relevant top result plus mixed topics to seven CO-OP results.

## Options considered

1. **Gemini/server-managed chat session with complete history.** Convenient, but ties
   state and retention to one provider, sends/grows the whole history, and conflicts
   with the requirement that memory be local to one visible chat.
2. **LLM rewrite on every follow-up.** Often effective, but doubles generation requests
   on the turns that need it and adds another quota/error/latency point.
3. **Bounded client history plus deterministic contextual retrieval.** The widget keeps
   a small in-memory history; the backend joins earlier user questions to referential
   follow-ups for retrieval and gives bounded history to the existing generation call.
4. **Permanent server conversation store or summarized memory.** Supports long chats,
   but adds identity, retention and summarization complexity the pilot does not need.

## Decision

Choose option 3:

- The widget keeps at most four earlier messages in a normal JavaScript variable. It
  survives closing/reopening the bubble but not a refresh, new tab, or department
  change. It is never put in browser storage or a server-side conversation table.
- The API accepts at most four 1,200-character history messages and sanitizes/anonymizes
  every one before use. Only the current anonymized question is logged.
- A deterministic follow-up detector recognizes references/continuations and short
  elliptical questions. Only then are the last two user questions added to one retrieval
  query and bounded history added to the answer prompt. Self-contained topic switches
  ignore history.
- Earlier assistant text can clarify a reference in the prompt but is explicitly not
  evidence. All answer facts must still exist in newly retrieved KB context.
- Each student turn still uses one local embedding/retrieval operation and at most one
  LLM generation request. There is no query-rewrite LLM call and no runtime token-count
  request.
- Provider 429s and transient/configuration failures become typed operational responses.
  They are logged separately and excluded from the unanswered-content queue and
  deflection metric. Gemini's returned input/output/cached token counts and generation
  latency are stored and surfaced as aggregate admin metrics.

Gemini remains the provisional default. Groq's documented free plan is the strongest
manual fallback candidate (not an automatic failover): it offers useful daily request
limits, but requires another vendor/key, another privacy review, and model-specific
answer evaluation. Cloudflare Workers AI is a second option if hosting later moves
there. Hugging Face's $0.10 monthly free credit and OpenRouter's 50 free requests/day
are too small for this pilot. No alternative is silently added before it passes the
same answer/retrieval evaluation and AUB data-handling review.

## Consequences

- Follow-ups work without permanent identity/state and without doubling Gemini RPM/RPD.
- Prompt growth has a fixed upper bound. The heuristic can miss unusual references or
  contextualize a very short topic switch; conversation and topic-switch golden cases
  guard both failure modes.
- A browser refresh intentionally starts a new chat. Supporting cross-refresh memory
  would be a different privacy/product decision.
- A 429 cannot always reveal whether the exhausted dimension is per-minute or daily, so
  the student gets a cautious retry message rather than a fabricated reset time.
- The SDK may retry transient failures internally before the typed response is returned.
  Pilot token/latency/error metrics will show whether retry or rate-limit tuning is needed.
