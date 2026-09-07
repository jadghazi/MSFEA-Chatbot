# Small pilot readiness

This is the current launch target: a limited group of students using the chatbot so
we can observe real questions, refusal quality, latency, and Gemini quota behavior.
It supersedes the older department-wide outcome targets as the immediate release gate;
those remain useful after the pilot produces real data.

## Automated evidence

- Ruff and strict mypy pass.
- 124 tests pass, including same-chat history, operational failures, readiness, and
  startup behavior.
- The 70-case golden set includes 23 selected email-clarification cases. Across the
  64 answerable golden questions plus one live curated case, context recall is 95% at
  k=5 and 98.5% at the production k=7. The sole tracked miss is the multi-topic
  internship-versus-CO-OP comparison.
- Live two-turn follow-up returned grounded answers and citations.
- Live weather, prompt-injection, and unsupported exact-deadline questions refused.
- Targeted live answers verified the universal 25% AI rule and ECE-specific report and
  presentation limits; ECE rules were excluded from a MECH answer. Citations contained
  only the directly supporting sections after the citation prompt was tightened.
- The calibrated 0.60 pre-LLM similarity gate passed 94/94 valid questions and stopped
  14/20 varied off-topic prompts before Gemini. Its retrieval-only evaluation runs in
  CI; the prompt refusal still handles relevant but unsupported questions.
- Production Compose exposes only Caddy; app and database have no host ports.
- The production image loaded both local models successfully with container networking
  disabled. Its current size is about 592 MiB (the developer image is about 623 MiB).
- A fully cached production + developer image rebuild completes in about 22 seconds on
  the current Docker Desktop machine.

## Operator checklist before inviting students

- [ ] Rotate/set `LLM_API_KEY` and a strong `ADMIN_TOKEN` in `.env`.
- [ ] Set the exact pilot page origin in `CORS_ALLOW_ORIGINS`.
- [ ] Set `DOMAIN` and verify HTTPS through Caddy.
- [ ] Build/start with the production overlay.
- [ ] Run ingestion once; verify `/health` returns `ok` and `/ready` returns `ready`.
- [ ] Confirm active Gemini RPM/TPM/RPD in AI Studio.
- [ ] Ask the pilot group not to enter names, IDs, phone numbers, or personal emails.
- [ ] Manually try the highest-risk rules for each represented department before
      sharing the URL (duration, eligibility, department exceptions, deliverables,
      links, one refusal, and one follow-up).
- [ ] Decide how often interaction logs are reviewed/deleted during the pilot.
- [ ] Keep the pilot small enough to stop or correct content quickly.

## Minimal production command

```bash
DOMAIN=chatbot.example.edu docker compose \
  -f docker-compose.yml -f docker-compose.prod.yml up -d --build

docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  run --rm app python -m msfea_bot.skeleton ingest
```

Do not add scale infrastructure before measurements from this pilot justify it.
