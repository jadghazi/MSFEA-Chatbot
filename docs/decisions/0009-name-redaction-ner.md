# ADR-0009 — Name redaction via local NER

**Status:** Accepted
**Date:** 2026-07-23
**Decision owner:** Jad Ghazi

## Context

CLAUDE.md §7 requires stripping student-identifying data (names/emails) before it
is sent to the LLM or stored in logs. ADR-0007 added regex redaction of emails and
long numbers (IDs/phones) but left **personal names** unredacted — a real privacy
gap before a pilot with real students.

## Options considered

1. **Regex/heuristic name detection** (e.g. capitalized word after "I'm"). Cheap
   but unreliable — misses most names and false-positives on ordinary capitalized
   words.
2. **Local NER model (spaCy `en_core_web_sm`).** Detects `PERSON` entities and
   redacts them. Free, offline, no API/per-use cost (~15 MB model). Chosen.
3. **Hosted NER / PII API.** Accurate but adds cost and an external dependency —
   against §3 (local/open, nothing to whitelist).

## Decision

Option 2. Extend `observability.privacy.anonymize()` to redact `PERSON` spans via
spaCy after the email/number regexes. The model is loaded lazily and cached.

**Fail-safe:** if the model isn't installed, name redaction is skipped with a
visible warning and the regex redactions still apply — the app never crashes over
a missing model.

## Consequences

- Closes the §7 names gap: verified that "Sara Khoury, student 202012345,
  sara@aub.edu.lb" is stored/sent as "[redacted-name], student [redacted-number],
  [redacted-email]", while domain terms ("8 weeks", "FEAA 500", "3.3") are kept.
- **Cost:** none at runtime — local/offline, ~milliseconds per short question.
  Adds the `spacy` dependency + a one-time model download
  (`python -m spacy download en_core_web_sm`); must be baked into the Docker image
  (Phase 10).
- **Limitations:** NER is not perfect — it may miss unusual names or occasionally
  over-redact (e.g. a professor's name a student mentions). Acceptable: biasing
  toward privacy is the right default, and the regex layer is independent.
- Resolves the open item carried from ADR-0007 / ADR-0008.
