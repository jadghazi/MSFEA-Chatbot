> Updated 2026-09-10: transient transport/408/500/502/503/504 failures now get
> one retry after 0.5 seconds (two 30-second attempts maximum). SDK retries
> remain disabled. Transient error responses are no longer cached; rate-limit
> responses retain the 30-second cooldown. Safe failure diagnostics are logged.
> The original audit measurements below describe the September 9 implementation.

# LLM/API usage audit — 2026-09-09

The audit inspected the existing API, security helpers, widget, conversation logic,
retrieval, embeddings, Gemini adapter, logging, deployment templates and reachable
Git history before changing behavior. No new dependencies or services were added.

## What already existed

| Area | Existing protection |
| --- | --- |
| Messages/history | 2,000 characters per question; four history messages, each at most 1,200 characters; browser trims history. |
| Follow-ups | Local reference resolution; only relevant history enters the prompt; retrieval uses prior student text, not verbose assistant answers. No summarization LLM. |
| Retrieval | Local BGE embeddings; hybrid search merges candidate IDs; calibrated similarity gate of 0.60 before generation; normally seven chunks, twelve for comparisons. |
| Output/retries | 1,024 output tokens; 30-second Gemini timeout; one SDK attempt, no application retry loop; shared provider client. |
| Frontend | Synchronous busy guard and disabled Send/input; no automatic chat retries; one vanilla-JS widget shared by both layouts. |
| API/privacy | Per-IP minute limiter, sanitization and best-effort local PII redaction, generic provider errors, CORS allowlist, protected admin routes. |
| Observability | Anonymized interactions, retrieved labels, provider token metadata and latency persisted; operational failures excluded from unanswered-content queue. |
| Deployment/secrets | Environment-sourced server-only key, ignored `.env`, excluded Docker secrets, non-root container, private app/database in production overlay. |

## Changes

1. Whole-message local acknowledgement, greeting and obvious-noise handling runs
   before anonymization, embeddings, DB logging and generation. Bare yes/no is local
   only without history: with history it may answer a clarification. Short questions,
   acronyms, unfamiliar words and mixed acknowledgement-plus-question inputs remain
   eligible for retrieval. Noise gets a rephrase request, not an escalation email.
   These replies carry the disclaimer but no invented source citation or feedback ID.
2. Added IP burst/hour windows and session minute/hour windows. Request quotas also
   apply to local replies and cache hits, so they cannot flood the endpoint freely.
3. Added atomic concurrency admission before expensive work: one request per session,
   four per IP, sixteen per worker. Duplicate in-flight requests return friendly 429
   immediately rather than occupying more threads waiting on another generation.
   Legacy requests without session IDs still get IP and in-flight fingerprint checks.
4. A bounded 256-entry response cache replays an exact effective request for 30 seconds.
   Keys include IP, session, question, department, relevant history and a KB revision.
   No response caching for callers without a session ID. Context-dependent follow-ups
   and confirmation frames retain their history in the key. Self-contained repeats
   can reuse an answer despite irrelevant history appended by the widget. Replays
   reuse the interaction ID without logging or counting the original tokens again.
   Failures also replay briefly to dampen repeated manual retries. Admin KB mutations
   invalidate the cache; offline re-ingestion should be followed by app restart.
5. Added a 64 KiB request-body limit before JSON parsing, checking declared and actual
   streamed bytes. Validation errors are friendly strings and do not echo submitted
   values. Existing message/history bounds remain unchanged.
6. Added a 24,000-character retrieved-context ceiling, including citation labels.
   An oversized context asks for a narrower question without calling Gemini. It does
   not silently discard table rows or policy conditions. Current chunk rankings,
   overlap, prompt wording, similarity threshold and output limit are unchanged.
7. Added content-free, process-local counters at `/admin/api/usage`, protected by the
   existing admin token. Counters cover chat arrivals, local replies, size/validation
   blocks, rate/concurrency hits, duplicates avoided, embedding queries, similarity
   refusals, actual Gemini attempts, provider/backend errors, token usage and latency
   sums. Missing counters mean no recorded events since startup. Token usage is
   counted even for an empty/truncated response when metadata is available; no token
   estimate is invented for failed requests without metadata. Existing durable
   interaction metrics remain available separately.
8. The widget now sends an ephemeral per-tab session identifier, preserved across
   refresh through sessionStorage. Local replies do not evict useful conversation
   history. Friendly HTTP errors are displayed rather than replaced by a misleading
   network error. Existing synchronous double-send protection remains intact.
9. The nginx template overwrites `X-Forwarded-For` with the connecting client address;
   the app uses the rightmost forwarded address only when proxy trust is enabled.
   Rate-limit maps have an explicit key bound in addition to expiry cleanup.

## Limits and deployment

| Scope | Limits |
| --- | --- |
| IP | Configurable minute window; new default 60/minute. Also 12/5 seconds and 300/hour. |
| Session | 20/minute and 80/hour; changing session ID does not reset IP limits. |
| Concurrent expensive work | 1/session, 4/IP, 16/worker. |
| Input | 2,000-character question, four 1,200-character history messages, 64 KiB HTTP body. |
| Retrieved context / output | 24,000 context characters; configured output default 1,024 tokens. |
| Duplicate reuse | 30 seconds, 256 entries maximum, same IP/session/effective context. |

The current local `.env` explicitly sets `RATE_LIMIT_REQUESTS=20`; that operator
override was preserved. The new default and `.env.example` use 60 to give shared
campus networks more headroom while retaining the tighter session limits. Review
actual rate/concurrency hits during the pilot before changing these values.

Use **one Uvicorn worker / one app instance**. The limiter, cache and counters are
in memory, reset on restart and are not coordinated across workers. A future
multi-instance rollout needs shared admission state; Redis is unnecessary for the
current deployment. Session IDs are not authentication. Rotating IDs cannot bypass
IP limits, but distributed clients with many IPs can still consume quota. These
guards bound obvious abuse; they do not guarantee the account's quota never runs out.

Only enable `TRUST_PROXY_HEADERS` with a private backend behind the supplied single
edge proxy. Do not expose port 8000 publicly with that flag enabled. Multiple proxy
hops/CDNs require a reviewed trusted-proxy configuration. Caddy ignores untrusted
incoming forwarded headers by default; see its [official reverse proxy documentation](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy).
CORS controls browser access, not direct API callers.

The Gemini SDK's retry implementation uses the configured attempt count as the
stopping bound; the existing `attempts=1` was retained. See the [SDK implementation](https://github.com/googleapis/python-genai/blob/main/google/genai/_api_client.py).
No extra retry or summarization call was introduced.

## Verification and measured changes

Compared the original `/chat` implementation at commit `d1aecd3` with the new endpoint using
a counted replacement for `generate_answer` (no real provider calls):

| Five requests | Original pipeline calls | New pipeline calls |
| --- | ---: | ---: |
| `ok` | 5 | 0 |
| `thanks` | 5 | 0 |
| Identical internship requirements question, one session | 5 | 1 |

These are **pipeline invocation counts**, not claimed Gemini token savings: the old
similarity gate could already refuse some inputs after embedding/retrieval.

All 74 golden-set questions pass the new local filter (0 falsely blocked). For the
205 normalized source chunks, the twelve largest chunks plus conservative label
overhead total at most 13,065 characters, below the 24,000-character guard. Thus the
new budget cannot remove existing normalized-source evidence at the current top-k.
Admin-curated content remains separately subject to the runtime guard.

Automated tests cover acknowledgements repeated five times, empty/whitespace input,
keyboard/random-consonant/character/pattern repetition, legitimate short questions,
context-sensitive yes/no, repeated valid requests, changed history/department/session,
burst and hourly limits, session rotation, concurrent requests, cache expiry and
capacity, oversized messages/history/chunked bodies, provider timeout/429/500/503,
and frontend repeated Send attempts. Provider tests fake transport results and check
one invocation; SDK option tests verify the one-attempt configuration.

Run the gates with the existing isolated Docker test database:

```sh
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm dev python -m pytest -q
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps dev python -m ruff check src tests eval
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps dev python -m mypy --strict src eval
node --test tests/widget_submission.test.cjs
```

The JavaScript submission tests are now included in CI. No live Gemini answer eval
was needed: the generation prompt, model, sampling, retrieval ranking and history
construction were preserved, and the new context guard is inactive for current
normalized content. This audit does not claim an answer-quality improvement.

Final local checks: **214 Python tests passed**, **3 JavaScript tests passed**, Ruff
passed and strict mypy passed across 41 source files. The isolated source rebuild
indexed 205 chunks. Production-depth context recall is **67/68 (98.5%)**, above the
CI floor of 90%; the fixed-k=7 report flags `internship-vs-coop` as an evidence miss. The existing
threshold calibration accepts **109/109** valid questions and blocks **11/20**
off-topic stress queries before generation. These are preservation checks, not
claimed retrieval improvements.
The synthesis/follow-up gate retains all required premises and passes threshold
for **11/11** answerable cases.

## Remaining findings

- Arbitrary gibberish is not reliably distinguishable from names, course codes or
  misspellings with cheap universal rules. Ambiguous inputs deliberately proceed to
  bounded retrieval and the existing similarity gate rather than a brittle dictionary
  filter. No embedding response cache was added because embeddings are local and the
  response cache already avoids duplicate embedding work for the common retry path.
- Near-duplicate content can intentionally carry different conditions/table headers.
  Hybrid retrieval already deduplicates IDs. Similarity-based text deduplication or
  removing every individually low-scoring chunk needs retrieval/answer evidence first;
  it was not added speculatively.
- Prompt rules treat user text/history as untrusted and citations are checked against
  retrieved labels. There are no tools, shell actions or environment-reading actions
  exposed to Gemini, and secrets are not inserted into its prompt. However, instructions
  and retrieved content share one text prompt; source-document prompt injection and
  hidden-prompt disclosure are not proven impossible. Trusted source/admin access
  remains necessary. Native system-instruction migration should be evaluated separately.
- PII redaction is best effort, and existing code skips name redaction if spaCy's model
  cannot load. This remains a privacy risk: deployment must include the baked NER model,
  and fail-closed name-redaction behavior deserves a separate measured review.
- No common Gemini/OpenAI key or private-key signatures were found in 965 reachable
  Git objects, and `.env` is not tracked. This is a pattern scan, not a proof about
  unreachable/deleted Git objects, every possible secret format, or external logs.
- The cache can replay a temporary failure for up to 30 seconds after recovery. It
  deliberately avoids a global outage circuit breaker that could block all students
  after one transient failure. Access logs and process counters still need normal
  operator retention/monitoring; counters are not a billing ledger.
- Runtime dependencies mostly use minimum-version ranges without a lockfile. Model
  weights are pinned, but future image rebuilds can still pick up different SDK/web
  dependencies. Dependency locking and deliberate upgrades remain a reproducibility
  follow-up rather than part of the usage behavior change.
