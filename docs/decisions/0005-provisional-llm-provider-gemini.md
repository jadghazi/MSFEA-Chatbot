# ADR-0005 — Provisional LLM provider: Google Gemini (free tier)

**Status:** Accepted (provisional)
**Date:** 2026-07-22
**Decision owner:** Jad Ghazi

## Context

The walking skeleton (CLAUDE.md §5.3) needs an actual LLM for the final
generation step. AUB's approved vendor is not yet known, and CLAUDE.md §3
requires the provider to sit behind a one-file abstraction (`msfea_bot.llm`) so
it can be swapped. We need *a* provider now, chosen for low cost to a solo
student.

## Options considered

1. **Google Gemini (free tier)** via the `google-genai` SDK. Genuinely free tier
   with generous limits for dev/eval; needs only a free API key.
2. **OpenAI / Anthropic (paid).** Easy and high quality, but per-call cost and a
   paid key.
3. **Local model via Ollama.** Free and fully private, but needs Ollama installed
   and capable hardware.

## Decision

Option 1 — **Gemini free tier**, wired behind `msfea_bot.llm` as the
**provisional** skeleton provider. This is *not* a final vendor commitment; it is
the cheapest way to prove the end-to-end flow. Swapping to Azure/OpenAI/local
later is a one-file change in the `llm/` package.

## Consequences

- Requires a Gemini API key in `.env` (`LLM_API_KEY`) — **never committed**.
- Free tier has rate limits; fine for development and eval runs, not yet sized
  for production traffic.
- **Privacy:** queries sent to Gemini leave the machine to Google. Acceptable now
  (no real student data in the skeleton). Before any real student data flows,
  revisit this per CLAUDE.md §7 (anonymize; and AUB's approved-vendor decision).
- The `llm/` abstraction is exercised for real for the first time, validating the
  swap-in design.
