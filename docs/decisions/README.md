# Decision log (ADRs)

This folder holds **Architecture Decision Records** — one short file per real
decision, in the order they were made. It exists because [CLAUDE.md](../../CLAUDE.md)
§2 requires us to *explain trade-offs, not just pick*, and because this is a
monitored capstone that will be handed to someone else: the *why* behind each
choice must outlive the person who made it.

## When to write one

Write an ADR when you make a decision that is **expensive to reverse** or that a
future maintainer would otherwise have to reverse-engineer:
chunking strategy, top-k, embedding model, LLM provider, retrieval approach
(semantic vs. hybrid), refusal threshold, etc.

Do **not** write one for trivial or easily-reversed choices (variable names,
file layout). Keep the log signal-heavy.

## How

1. Copy [`0000-adr-template.md`](0000-adr-template.md).
2. Name it `NNNN-short-title.md` with the next number.
3. Fill it in. Keep it short — context, options, decision, consequences.
4. An ADR is **immutable** once accepted. If a later decision reverses it, write
   a *new* ADR that supersedes it and link back. We never rewrite history.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| 0001 | Adopt ADR process + provisional success metrics | Accepted |
| 0002 | Evaluation methodology: layered hybrid | Accepted |
| 0003 | Phase 1 KB scope: all CDC content | Accepted |
| 0004 | Embedding model: local bge-small-en-v1.5 | Accepted |
| 0005 | Provisional LLM provider: Google Gemini (free tier) | Accepted (provisional) |
| 0006 | Chunking: section-aware + size-bounded overlapping windows | Accepted |
| 0007 | Observability: interaction logging + anonymization | Accepted |
| 0008 | Safety / abuse hardening | Accepted |
| 0009 | Name redaction via local NER | Accepted |
| 0010 | Admin dashboard + curation feedback loop | Accepted |
