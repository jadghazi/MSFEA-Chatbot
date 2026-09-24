# Focused answer-quality review — 2026-09-24

## Method and environment

The 15 frozen focused questions were run against disposable PostgreSQL/pgvector
databases on loopback port 55432, populated only by normal ingestion of the
repository's normalized KB. The baseline and comparison
used Gemini `gemini-flash-lite-latest`, `TOP_K=7`, similarity threshold `0.60`,
and the same questions, departments, histories, and configured sampling settings.
No production database was accessed or rebuilt.

The [baseline trace](results/answer_quality_before.jsonl) is one complete live
run before edits. The [earlier comparison trace](results/answer_quality_after_final.jsonl)
contains one complete post-change live run with its EECE500 duration row replaced
by the live rerun after focused query disambiguation; no mock answers were used.
A later retry produced a [complete final 15-case live trace](results/answer_quality_final_live_20260924.jsonl)
on a fresh isolated database rebuilt through normal ingestion. The final run
used the same model, top-k, questions, departments, and histories. Intermittent
504/timeouts recovered on the configured retry.

For each answer I read its text, the retrieved passages, the actual model context,
and its cited source against `expected_answer_or_behavior`. “Correct” requires
the right policy for the student's circumstances; “complete” requires essential
conditions; “grounded” requires the cited passage to support material claims.
Citations, words in an answer, and the LLM's refusal flag were not used as proxies
for semantic correctness. The table uses 14 answerable cases for evidence metrics
and all 15 cases for answer judgments.

| Measure | Baseline | Earlier comparison | Final live run |
|---|---:|---:|---:|
| All required evidence retrieved | 8/14 | 14/14 | 14/14 |
| All required evidence in model context | 6/14 | 14/14 | 14/14 |
| Addresses intended question | 8/15 | 15/15 | 15/15 |
| Correct policy/appropriate refusal | 8/15 | 15/15 | 15/15 |
| Complete essential conditions | 7/15 | 15/15 | 14/15 |
| Grounded in cited passages, among substantive answers | 8/9 | 14/14 | 14/14 |
| Appropriate clarification/refusal decision | 10/15 | 15/15 | 15/15 |
| All answer criteria together | 7/15 | 15/15 | 14/15 |

The final completeness miss is `aq07`: the answer correctly requires ten weeks
for another summer course and lists both documented routes, but omits the
required approvals and class scheduling condition. A repeated live run made the
same omission. A generic prompt change and a tighter arrangement of the same
source conditions did not help in targeted live probes; both were reverted. The
conditional unknown-department answer (`aq14`) names ECE and MECH but is not
an exhaustive map of every department; a student still needs their department
for a definitive answer.

The baseline misses for intent and correctness were `aq01`, `aq03`, `aq04`,
`aq06`, and `aq09`–`aq11`. `aq02` answered the right broad topic but omitted the
required-course purpose, so it failed completeness. The baseline `aq01` answer
introduced the KB's disputed credit description while its displayed citations
did not support that claim, so it failed grounding. The five false refusals were
`aq04`, `aq06`, and `aq09`–`aq11`; `aq15` refused appropriately. All comparison
and final answers were individually checked against the cited passages.

## Representative actual answers

| Student question | Baseline | Complete comparison |
|---|---|---|
| “whats the internship?” | “To successfully complete the Approved Experience course, you must fulfill all internship requirements and submit all required deliverables on time. The internship course is a 1-credit course…” | “The Approved Experience internship is the required engineering training course…with a standard minimum duration of eight full weeks. It allows you to apply classroom learning to real engineering and design challenges…” |
| “How long should the EECE500 be” | “The EECE500 Final Training Report must be at least five pages and 1,500 words…” | “EECE 500 requires a minimum of eight full weeks of approved training, typically 320 work hours…” |
| “Can I do eight weeks while enrolled in a class?” | Refused despite retrieving the ten-week exception; it was filtered out of model context. | “No, eight internship weeks are not enough when you are enrolled in another class during the same summer. You must complete ten weeks…” |
| CO-OP → “Do I need approval?” | Refused after losing CO-OP context. | “For CO-OP: Yes, the department's co-op academic advisor reviews and accepts or rejects applications… For a self-found CO-OP opportunity, you must submit the Proposal…” |
| ECE 6+2 → “What about its progress report?” | Refused despite retrieval of the relevant passage; the option-follow-up filter removed it. | “Submit the Progress Report at the end of Week 4 of the company internship and cover only the company internship in that report.” |

The two reported examples, without shortening the recorded answer text:

> **Before, “whats the internship?”** To successfully complete the Approved Experience course, you must fulfill all internship requirements and submit all required deliverables on time. The internship course is a 1-credit course requiring a minimum of 90 completed credits to register, and the training must last at least 8 weeks.

> **Comparison, “whats the internship?”** The Approved Experience internship is the required engineering training course that normally takes place during the summer before your final year, with a standard minimum duration of eight full weeks. It allows you to apply classroom learning to real engineering and design challenges, gain professional experience and workplace skills, and explore career paths.

> **Before, “How long should the EECE500 be”** The EECE500 Final Training Report must be at least five pages and 1,500 words, excluding the cover page, references, and appendix, and must not exceed 20 pages.

> **Comparison, “How long should the EECE500 be”** EECE 500 requires a minimum of eight full weeks of approved training, typically 320 work hours. If you take another summer course, you must complete ten weeks of approved internship: either ten weeks at one company or six weeks at one company plus four weeks at another company.

> **Final live, “whats the internship?”** The Approved Experience internship is the required engineering training course that is normally completed during the summer before your final year, with a standard minimum duration of eight full weeks. It allows you to apply classroom learning to real engineering and design challenges, gain professional experience and workplace skills, and explore career paths.

> **Final live, “How long should the EECE500 be”** EECE 500 requires a minimum of eight full weeks of approved training, typically 320 work hours. If you take another summer course, you must complete ten weeks of approved internship instead, either ten weeks at one company or six weeks at one company plus four weeks at another.

## Checks against the final code

- The final CI-style synthesis gate checked **47/47** answerable cases for every
  required phrase in both retrieval and the actual model context, plus the
  similarity gate. The existing golden retrieval evaluation found required
  evidence in **92/96** answerable cases at top-k seven; its four misses concern
  internship grading, two graduation-requirement phrasings, and Career+.
- The relevant unit suite passed **68/68** and lint passed after the final
  normalized edits. The 15-case final live run was reviewed against its source
  passages, not just citation or keyword checks.
- Release preflight then corrected identical-question replay when history is present;
  none of the focused live cases has that history shape. The full suite passed
  **285/285**; widget tests, Ruff, strict mypy, retrieval, threshold, synthesis,
  publication-preservation, and conflict gates passed against an isolated database.
- A live scope pass covered ECE, MECH, CHEM, IEM, CEE, and unknown department.
  It found one ECE presentation deadline error: the answer used the general Fall
  schedule instead of the department's one-week deadline. A source-backed note
  was added to the normalized ECE section and the index rebuilt normally; the
  corrected answer passed **two live repeats**. The other seven scope cases
  passed in the initial live pass.
- The [six-week live trace](results/six_week_retry2_20260924.jsonl) answered all
  six scoped cases correctly, and the ordinary ECE six-week paraphrase passed
  an additional [live repeat](results/six_week_paraphrase_final_repeat_20260924.jsonl).
- A report-antecedent probe initially answered internship weeks after a report
  discussion. With the final bounded-history clarification, the live answer was:
  “Are you asking about the duration of the internship or the length of the Final
  Training Report?” A vague CO-OP paperwork-deadline probe initially refused,
  then selected one form; the final targeted live answer gave documented
  application timing conditionally and asked which document the student meant.
- Three fresh phrasings in `answer_quality_final_holdout.jsonl` had required
  evidence in retrieval and model context **3/3**, and their [live answers](results/answer_quality_holdout_live_20260924.jsonl)
  addressed EECE500 duration, CO-OP pay, and CEE's 4+4 condition correctly.

## Six-week policy follow-up check

Six new cases distinguish the ordinary ECE minimum, the approved six-company-plus-
two-research route, combining two companies outside the extra summer-course
condition, the ten-week summer-course exception, and the MECH boundary. With the
same isolated index settings, all required evidence was retrieved and present in
the actual model context for **5/6 before** the targeted KB edit and **6/6 after**.
The one miss was the general two-company approval passage for a student asking
about six plus four company weeks without another summer course. The normalized
two-company entry now states that case and its prior-written-approval condition
explicitly. The final synthesis gate, including the earlier cases, passed
**47/47**. See the [before](results/six_week_before_retrieval.jsonl) and
[after](results/six_week_after_retrieval.jsonl) read-only traces.

An earlier review wrongly called the four-week second-company option unsupported
for an ordinary ECE six-week placement. The original June 2026 training
guidelines explicitly say that ECE students completing six company weeks must
add either two MSFEA faculty-research weeks or a minimum four-week placement at
another company. The email clarification requires prior written approval or a
petition to combine two companies. The same six-plus-four pattern is also a
specified route for the separate ten-week summer-course rule, with its additional
approvals and schedule condition. The four additional company weeks are a
conditional ECE completion route, not the minimum for every internship. The
six-week case expectations were corrected to match that original source.

After this KB edit, the relevant unit suite passed **68/68**, lint passed, and
the existing golden retrieval evaluation found required evidence in **92/96**
answerable cases at the configured top-k of seven. Its four remaining misses
concern internship grading, two internship-versus-CO-OP graduation-requirement
phrasings, and a Career+ follow-up; none are in the six-week set. The broader
47-case synthesis gate had no lost cases.

## Retained changes and limits

The harmful heading-word evidence filters were removed so paraphrases and
explicitly requested reports keep their retrieved passages. Eight bounded
messages and a short topic anchor keep natural follow-ups attached to the current
program while explicit topic switches remain independent; earlier assistant
wording is only a search/reference hint, never policy evidence. The chunker now
retains nested heading paths and keeps both newer and legacy Q&A pairs intact.
Small normalized additions make the course identity, standard duration, ECE
summer-course exception, and CO-OP approval stages self-contained. No provider,
model, embedding, vector store, or top-k change was made.

Gemini recovered enough for the final complete live run, although isolated 503,
504, and read-timeout failures still needed retries. Temperature zero and a
fixed seed reduce variation but do not make output perfectly deterministic.
The repeated `aq07` omission remains a limitation for the pilot: the source
includes the approvals and class schedule, but the generated answer did not.

## Gemini failure diagnosis

On 2026-09-24 the configured `gemini-flash-lite-latest` endpoint returned a 504
on a full RAG request, then a 503 response explicitly saying the model was
experiencing high demand. The client uses a 30-second request deadline and one
application-level retry. A single bounded diagnostic with the same key and model
retrieved model metadata successfully in 460 ms, while a one-word generation
request failed with 504 after 14.8 seconds under a 15-second deadline. Earlier
successful evaluation prompts were 12–17k characters and completed in 1.1–1.7
seconds; the failed RAG prompt was of comparable size. These facts
support a generation-service capacity/latency issue rather than bad credentials,
an invalid model name, or excessive RAG context. No 429 quota error was observed;
project quota cannot be independently read from these API responses.

On the user-requested retry later on 2026-09-24, a fresh isolated database was
populated through normal ingestion (211 chunks), and the unchanged 15-question
focused live run was started with `gemini-flash-lite-latest` and `TOP_K=7`.
The first question received two 503 `UNAVAILABLE` responses; the second
explicitly said the model was experiencing high demand. No answer was produced,
so this retry adds no answer-quality score and does not verify the final code's
remaining six-week or holdout cases. No 429 quota response was observed.

On the next user-requested retry, a one-word generation probe succeeded and a
fresh isolated index supported complete live runs of the 15 focused questions,
six six-week cases, three final holdouts, and eight department-scope cases.
Several individual requests still returned transient 503/504/read-timeout
errors before succeeding on retry. No 429 quota response was observed.
