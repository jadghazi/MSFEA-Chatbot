# Oracle intermittent chat failures — 2026-09-10

## Evidence collected before changes

Oracle app and PostgreSQL containers were healthy; app uptime was 24 hours.
Production revision: 0e234bc. Model: gemini-flash-lite-latest; output cap: 1024.
Interaction 62 succeeded at 13:19:24 UTC; follow-up 63 failed at 13:20:09 UTC
with service_unavailable. Yesterday, interaction 60 failed similarly at 13:01:13
UTC. Older failures include 35, 38 and 55.

The running worker reported six LLM attempts, two provider errors, three duplicate
replays, and no backend-error or rate-limit counters. Total chat processing was
87,086 ms; recorded provider-response latency was 25,590 ms. The approximately
61-second remainder is consistent with two 30-second provider timeouts plus
local processing, but does not prove the specific historical exception.
Docker logs contained no exception diagnostics: API handlers discarded them.
Failure interaction rows also discarded error detail and latency. Therefore the
exact historical upstream HTTP status/transport exception cannot be recovered.
Do not describe this as a proven Gemini outage or a proven memory/retrieval bug.

A separate provider-path replay on Oracle of interaction 63 with interaction 62
as history completed three times without an operational error (8.81, 14.42,
6.91 seconds including local processing). This was not an answer-quality eval:
the replies mixed in the alternative ten-week arrangement, an existing content
quality issue requiring a separate measured retrieval-first investigation.

## Fix

- At most one retry after 0.5 seconds for transport errors, HTTP 408 and selected
  transient 5xx responses. SDK remains at one attempt; no retries on quota,
  credentials, truncation or empty responses. Worst transport wait: about 60.5 s.
- Retry button no longer replays service_unavailable for 30 seconds. Keep exact
  successful-response caching, rate-limit cooldown and concurrency/rate guards.
- Log safe exception category, status, attempt, elapsed time and retry decision;
  never SDK exception bodies, URLs, prompts or credentials. Log unexpected
  backend exception type. Count actual attempts and retries.
- No retrieval, prompt, model, KB or dependency changes.

## Validation

Hermetic timeout/503-then-success cases now recover in two attempts (previously
failed on the first). Persistent transient failures stop at two; quota at one.
Repeated user retries make fresh attempts and release concurrency slots.
Final check and production deployment results are recorded in docs/progress.md.

## Live reproduction after deployment

Deployed 071d9df to Oracle through a Git bundle and normal production Compose
build. Public HTTPS health/readiness passed. Four real HTTP turns completed
without operational errors (interaction IDs 64–67). The final employer-letter
follow-up reproduced the upstream fault:

    llm_failure model=gemini-flash-lite-latest reason=Gemini is temporarily unavailable cause=ServerError status=504 attempt=1 elapsed_ms=29592 retry=True

The second attempt succeeded with a cited answer; total HTTP duration was
38.44 seconds. Under the previous one-attempt behavior this 504 would have
returned service_unavailable. This is direct evidence of a Gemini upstream
504 timeout causing the same symptom, although the exact exception for the
older rows remains unavailable. Other live timings: 2.34, 7.08, 10.44 seconds.

Full suite: 216 passed; widget: 3 passed; Ruff passed; strict mypy passed for
41 files. Persistent-provider failure remains possible after both attempts;
the fix does not promise zero outages or eliminate provider latency.
