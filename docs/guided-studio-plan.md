# Guided Knowledge Studio

Acceptance conditions, recorded before implementation:

- One composer serves direct intake and unanswered-question review; saving does
  not resolve feedback or expose content to students.
- Staff supply approved guidance and explicit scope. AI suggests a focused title,
  student questions and exact quoted comparisons. Canonical guidance stays verbatim;
  generated questions never become answer evidence.
- A structured response cannot invent a source, quote, verification phrase,
  replacement target or approval. Missing details and conflicting claims require
  staff judgment. A duplicate should point staff to the existing source.
- Persist the original sanitized intake, evidence snapshot, model, prompt version,
  report, accepted revision and knowledge-generation fingerprint. An edited or stale
  review cannot silently authorize a different draft.
- Use the existing private Python worker for bounded AI jobs. Keep n8n's existing
  deterministic validation/publication workflow and atomic publication unchanged.
  No new orchestration system or student-path LLM call.
- All original retrieval gates must pass. Measure new-entry retrieval with both
  generated questions and independently authored questions. Test numeric conflicts,
  negation, scope exceptions, duplicates, unrelated content, missing conditions,
  prompt injection, malformed responses, quota failures, stale reviews and replay.
- Browser-check real loading, review, correction, draft handoff and conflict states,
  plus narrow-screen layout and keyboard/accessibility semantics.

Deliberately deferred: embedding synthetic aliases or rewritten answer text.
Existing Q&A/title chunking already accepts focused curated sources. Additional
retrieval representations need a separate measured comparison before adoption.
