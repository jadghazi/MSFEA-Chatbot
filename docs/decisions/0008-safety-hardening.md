# ADR-0008 — Safety / abuse hardening

**Status:** Accepted
**Date:** 2026-07-23
**Decision owner:** Jad Ghazi

## Context

Before exposing the bot to real students (Phase 8, CLAUDE.md §5.8), it needs
per-session rate limiting, input sanitization, input length caps, and a system
prompt that resists jailbreaks / off-topic abuse ("write my essay",
prompt injection).

## Decisions

- **Rate limiting:** an in-memory sliding-window limiter keyed by client, applied
  to `/chat` as a dependency (returns HTTP 429 when exceeded). Configurable
  (`rate_limit_requests`, `rate_limit_window_seconds`).
- **Client key:** `request.client.host` by default; the first `X-Forwarded-For`
  entry only when `trust_proxy_headers` is enabled (set that **only** behind a
  trusted reverse proxy, else it is spoofable).
- **Input handling:** length cap of 2000 chars (request model); `sanitize()`
  strips null bytes and control chars; an empty post-sanitize question returns a
  gentle prompt-to-rephrase instead of calling the LLM.
- **Prompt hardening:** the system prompt now tells the model it only handles CDC
  topics, to treat the question as untrusted, to ignore embedded instructions
  (role changes, prompt reveal, essays/code/chit-chat), and to refuse
  (`INSUFFICIENT_CONTEXT`) anything out of scope or trying to override the rules.
- **Eval:** added a jailbreak golden case (`refuse-injection`).

## Consequences

- Verified live: a legit question is answered; an injection ("reply HACKED") and
  an abuse request ("write my essay") are both refused.
- **Grounding is the primary defense** (the bot only answers from retrieved CDC
  context); prompt hardening is defense-in-depth. No prompt is jailbreak-proof —
  the eval's jailbreak case guards against regressions, and new attacks get added
  to the golden set as found.
- **Rate limiter is per-process (in-memory):** correct for a single instance /
  pilot; a multi-instance deployment needs a shared store (e.g. Redis). Memory is
  one entry per distinct client key seen in the window; a production version would
  add TTL eviction.
- **Open gap (from ADR-0007):** personal *names* are still not stripped from logs
  (needs NER). Carried forward as a follow-up.
