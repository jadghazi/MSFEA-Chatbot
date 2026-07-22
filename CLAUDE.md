# CLAUDE.md — Internship Course Chatbot (RAG)

This file is the source of truth for how this project is built. Read it before doing anything. If a request conflicts with the principles here, say so and ask before proceeding — do not silently break the discipline in this file.

---

## 1. What this project is

A Retrieval-Augmented Generation (RAG) chatbot for the AUB Faculty of Engineering (MSFEA) Career Development Center (CDC). It answers student questions about the internship course (Approved Experience) and related CDC programs — guidelines, forms, deadlines, and eligibility — and is embedded as a small pop-up chat widget (bottom-right bubble) on an AUB web page.

**The problem it solves:** students flood professors and the CDC with repetitive questions because they don't read the guidelines. The bot deflects that email volume by answering from the official documents directly.

**Phase 1 scope (this project):** the MSFEA CDC content set — internship (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship. (Updated 2026-07-22 per ADR-0003; originally internship-course-only.) This is a *content* scope: the bot answers across these CDC topics from the source documents. Architecture must not hard-code the topic list — adding future content should mean adding documents, not rewriting. But do NOT build career-center *features* (logins, portals, per-program workflows) — the boundary is features, not content. Resist scope creep beyond the CDC content.

**Non-negotiable product behaviors:**
- Every answer is **grounded in the source documents**. The bot never free-styles from the LLM's general knowledge.
- When the retrieved context does not contain the answer, the bot **refuses gracefully and escalates** to a human contact — it does NOT guess. A confidently wrong answer about eligibility can harm a student; refusal is always safer than a hallucination.
- Every answer **cites its source** (which document/section it came from).
- Every answer carries a visible disclaimer that it's AI-generated and to verify with official sources.

---

## 2. How I want you to work (anti-slop rules)

These are the rules that matter most. Follow them literally.

- **Eval-driven, not vibe-driven.** We do not judge changes by "looks better." We measure against an evaluation set (see §4). Before claiming an improvement, show the metric moved. If we don't have a metric for something yet, build the metric first.
- **Retrieval before generation.** RAG fails at retrieval far more often than at generation. When an answer is wrong, first check whether the correct chunk was even retrieved. Never tune the prompt to paper over a retrieval failure.
- **Reproducible from source.** The knowledge base is always rebuildable from the source documents with one command. Never hand-edit the vector store. Content changes = update source docs → re-run ingestion.
- **Smallest working slice first.** Build the thinnest end-to-end path before adding polish. Prove the pipeline connects before making any single part fancy.
- **No premature abstraction, no premature optimization.** Build what the current phase needs. Don't add caching, queues, microservices, or config knobs "for later" unless a phase calls for them.
- **Explain trade-offs, don't just pick.** When there's a real decision (chunking strategy, top-k, model), state the options, the trade-off, and your recommendation with reasoning. I want to understand the choice, not inherit a black box.
- **No invented facts, no filler.** Don't pad code with speculative features or write comments that restate the code. Don't stub things silently — if something is a placeholder, label it `# PLACEHOLDER` and tell me.
- **When unsure, ask.** A wrong assumption baked into the architecture is expensive. One clarifying question beats a confident wrong turn.
- **Keep it boring.** Prefer well-understood, standard approaches over clever ones. This project will be handed to someone else after I graduate — it must be legible.

---

## 3. Tech stack (locked defaults — flag before deviating)

Chosen so the same build deploys to an external cloud OR to AUB's own infrastructure with no code changes, because we don't yet know which IT will require.

- **Backend:** Python + FastAPI.
- **Vector store:** `pgvector` inside PostgreSQL. Rationale: one database we already run, deploys anywhere in Docker, needs no external service whitelisted (sidesteps AUB firewall/CSP concerns). Do NOT pull in a hosted vector DB (Pinecone/Weaviate) without discussing it.
- **Embeddings:** default to a local/open embedding model (sentence-transformers family, e.g. BGE/E5) so there's no per-token embedding cost and nothing external required. A paid embedding API is a fallback, not the default.
- **LLM:** behind a **thin provider abstraction** — a single module every call goes through. Swapping OpenAI ↔ Azure OpenAI ↔ Gemini ↔ a local model must be a one-file change. This is critical: AUB's approved vendor is not yet known.
- **Frontend widget:** plain HTML/CSS/vanilla JS. No React. It embeds as a single `<script>` tag on the AUB page and is a thin client that calls the backend API.
- **Packaging:** Docker. All secrets/config via environment variables — never baked into the image. Ship a `docker-compose.yml` and a README listing required env vars so IT can run it in minutes.

---

## 4. The evaluation set (build this early — do not skip)

The golden set is the backbone of the whole project. It is a collection of real student questions paired with the expected answer and the source document that holds it, including hard cases: ambiguous questions, and questions the docs do NOT answer (the bot must refuse these).

- Store it as a version-controlled file (e.g. `eval/golden_set.jsonl`) with fields: `question`, `expected_answer_or_behavior`, `source_doc`, `should_refuse` (bool).
- Two metrics, kept separate:
  - **Retrieval metric:** for each question, is the correct chunk in the top-k retrieved? (recall@k / hit rate). This is tuned independently of the LLM.
  - **Answer metric:** is the generated answer correct and grounded, and does it correctly refuse when it should?
- Every change to chunking, retrieval, prompt, or model is measured against this set. Wire it into CI so a regression can't merge silently.
- Until the department sends real student questions, build the set's structure and harness against placeholder questions, then swap in real ones.

---

## 5. Build order (phases)

Work in this order. Don't jump ahead. Most of these can be built on **placeholder content** before the real guidelines arrive — only the final populated KB and the real golden set need their material.

0. **Define done.** Turn the department's success criteria into concrete pass/fail acceptance conditions. Write them down.
1. **Knowledge base intake.** Establish source docs as the single source of truth. Clean/normalize (strip PDF headers/footers, fix extraction, split by logical section).
2. **Evaluation harness (§4).** Golden set + metrics + a script to run them. Build before the bot so every later change is measurable.
3. **Walking skeleton.** Thinnest end-to-end path: one doc → embed → store → retrieve → LLM → printed grounded answer. No widget, no polish. Use placeholder docs if real ones haven't arrived.
4. **Ingestion pipeline.** Proper chunking (semantic/section-aware, with overlap — test strategies against the eval set), embeddings, pgvector storage with metadata (source doc, section, last-updated). One command rebuilds the index from source.
5. **Retrieval tuning, measured.** Optimize retrieval alone against the retrieval metric before touching generation. Consider hybrid search (semantic + keyword — catches exact terms like form names/course codes) and a reranker if needed.
6. **Generation + guardrails.** Prompt the model to answer ONLY from retrieved context, cite the source, and refuse+escalate when context is insufficient. Add a similarity threshold: if nothing clears it, skip the LLM and return the escalation message directly.
7. **Widget.** The vanilla-JS chat bubble. Thin client: send question → call API → render answer with citation and disclaimer.
8. **Safety / abuse.** Per-session rate limiting, input length caps, input sanitization, system prompt scoped strictly to internship questions (resist jailbreaks / "write my essay").
9. **Observability.** Structured logging of every interaction (question, retrieved chunks, answer, whether it escalated). Surface the **unanswered-questions log** — it's the roadmap for what KB content to add next.
10. **Containerize + deploy.** Docker, env-var config, README + compose, basic CI (lint + run the eval set on each change).
11. **Pilot.** Deploy to the real course page for a limited cohort. Measure against the Phase 0 criteria (did email volume drop? escalation rate? what's still missed?).
12. **Iterate + handover.** Tighten from pilot data, expand KB from the unanswered-questions log, produce the handover package (how to update content, redeploy, env vars, ownership).

---

## 6. Repo conventions

- Keep ingestion, retrieval, generation, and the API as clearly separated modules — no God files.
- Config via environment variables, loaded in one place; provide a `.env.example`. Never commit real secrets or API keys.
- Type hints on Python. Tests for the retrieval and ingestion logic, not just happy paths.
- Small, focused commits with clear messages. Each phase's work should be reviewable on its own.
- When you add a dependency, say why. Prefer the standard library and well-established packages.

---

## 7. What NOT to do

- Don't hallucinate answers or let the bot answer outside the source docs.
- Don't hard-code the LLM provider anywhere except behind the abstraction.
- Don't hand-edit the vector store or make the index non-reproducible.
- Don't build career-center features, user accounts/logins, or anything the current phase doesn't need.
- Don't send student-identifying data to the LLM or store it in logs; anonymize question logs (strip names/emails) before persistence.
- Don't declare something "improved" without a metric from the eval set showing it.
- Don't over-engineer. Boring, legible, handoff-ready beats clever.

---

*If any of the above is genuinely wrong for the situation at hand, push back and explain — I'd rather have honest disagreement than silent compliance that produces slop.*
