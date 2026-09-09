# ADR-0023: Local usage guards for the single-worker pilot

Status: Accepted for local implementation; deployment pending.
Date: 2026-09-09

The free-tier usage audit found that bounded prompts and provider retry controls
already existed, but repeated acknowledgements, duplicate requests and simultaneous
submissions could still reach expensive processing. The widget alone cannot enforce
backend limits. See [the audit](../usage-audit.md) for measurements and all findings.

Use deterministic whole-message local replies before inference, bounded in-memory
rate/concurrency state and a 30-second response replay cache. Scope replay to IP,
session, effective question/history, department and KB revision. Apply IP limits
even when sessions rotate. Keep the existing follow-up behavior and measured
retrieval/prompt settings. Add a non-truncating context ceiling for oversized future
content rather than silently discarding policy evidence.

Alternatives rejected for this pilot: Redis/shared infrastructure before multiple
workers exist; LLM-based spam classification or summarization that consumes another
call; fuzzy duplicate matching that might conflate distinct eligibility questions;
dictionary-based gibberish rejection that blocks acronyms and misspellings; waiting
on duplicate requests that occupies additional server threads; a global outage
circuit breaker triggered by one transient error.

Trade-offs: process state resets on restart; multi-worker deployment requires shared
state; NAT users share an IP budget; a failed result may replay for up to 30 seconds;
uncertain noise still reaches local retrieval. Sessions remain anonymous and are
not authentication. Current source context is below the cap, and no golden-set input
is falsely blocked by the local gate. Provider answers were not re-tuned.
