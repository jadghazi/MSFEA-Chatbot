# ADR-0016 — Actionable links in answers, and the retrieval changes they forced

**Status:** Accepted
**Date:** 2026-08-05
**Decision owner:** Jad Ghazi

## Context

An audit of the original sources found that **four URLs present in the .docx were lost
during normalization**. They sat behind anchor text ("here", "petition", "self-secured
internship form"), which is exactly how links disappear when Word is converted to
Markdown — the visible text survives, the `Target` in the relationship file does not.

The bot was therefore telling students *"complete the CDC's self-secured internship
form"* with no way to reach it, in a paragraph that also warns the internship
**won't count toward graduation** if not processed correctly.

The CDC separately supplied three rules absent from the June 2026 document (90-credit
eligibility; remote internships not accepted; AUB-internal internships not accepted
except in special circumstances) and a fourth URL, the letter/convention-de-stage
request form.

## Decisions

**1. Restore the links, and render them clickable.** Answers now carry the URL
verbatim, and the widget turns URLs and emails into real links.

**2. Build links from DOM nodes, never `innerHTML`.** The answer is model output; it
is not trusted markup. `linkify()` walks the text, emits `createTextNode` for prose and
an `<a>` only for a scheme-checked match, so injection is *impossible by construction*
rather than escaped after the fact. External links get `rel="noopener noreferrer"`.
Verified: `javascript:` and `data:` URLs, and raw `<img onerror=…>`, all render as
inert text. Long Office Forms URLs are display-truncated with the full URL in `href`
and `title`.

**3. Instruct the model to emit URLs verbatim.** Measured need: with the link in
context, the model still answered *"linked on their website"*. One prompt rule fixed it.

**4. `top_k` 5 → 7.** The KB grew from 175 to 183 chunks and the new content competed.
Swept against context-recall:

| k | context-recall | misses |
|---|---|---|
| 3 | 87% | 5 |
| 5 | 92% | 3 |
| **7** | **95%** | 2 |
| 10 | 97% | 1 |

7 is the knee: it recovers a real case for two extra chunks (~1k chars), where 10
doubles the context for one more. The eval now reports at the **configured** `top_k`,
because gating CI on a depth production doesn't use tests the wrong thing.

**5. Exclude provenance footers from the index.** "About this document" sections are
notes for whoever maintains the KB, not answers for students. **7 of 182 chunks were
these notes**, and one was retrieved at **rank 5** for "how do I submit a petition?",
displacing real content. One of the two footers predates this work, so this was a
latent bug, not only a new one.

## Measured result

Context-recall@7 = **97%** (37/38), back to the pre-change level with the same single
known `internship-vs-coop` miss — over 38 answerable questions, up from 33.

The path there is worth recording, because two intermediate steps were **wrong and the
measurement said so**:

- Adding the KB content first *regressed* context-recall 97% → 92%, breaking
  `internship-mandatory` (a real, common question).
- Excluding department chunks for unscoped students — which seemed principled, since
  another department's rule can't be right for a student we can't place — measured
  **worse** (89%) and broke `dept-split-internship`, whose expected behaviour is that
  an unplaced student still learns the rule *depends* on their department. Reverted.
- Removing the provenance chunks is what actually recovered `internship-mandatory`.

New golden cases: `eligibility-90-credits`, `remote-not-accepted`,
`aub-internal-internship`, `self-secured-form-link`, `letter-request-link`. The two
link cases use the **distinct tails of the two Office Forms ids** as evidence, so the
bot fails them if it returns the wrong one of the two forms.

Verified end-to-end: the self-secured form, the letter-request form, the 90-credit
rule, and both "not accepted" rules all answer correctly with the URL emitted in full.

## Consequences

- Students can act on an answer instead of being told a form exists somewhere.
- **The petition deep link was deliberately not used.** The .docx held a URL carrying
  an Oracle APEX session id, which is not durable; the bare
  `https://petitions.aub.edu.lb` entry point is recorded instead.
- **A contradiction is now explicit in the KB.** The new general rule "remote
  internships are not accepted" sits alongside an IEM rule permitting remote
  internships with U.S.-based companies. The general rule points at the department
  exceptions rather than stating a false absolute — but which takes precedence needs
  CDC confirmation.
- **Provenance is recorded in the document itself.** The rules supplied verbally are
  marked as such, so a future maintainer doesn't assume they came from the .docx. They
  should be folded into the next official revision of the source document.
- Known follow-up: "How do I submit a petition for an exception?" still refuses even
  though the link is retrieved at rank 2 — a generation-side over-refusal, not a
  retrieval gap. The petition instructions are scattered across three sections; giving
  them one section is the likely fix.
- A dozen forms named in the KB (Notice of Arrival, Summary Sheet, CO-OP Joint
  Agreement, …) still have **no link in any source document**. That is a content gap
  for the CDC, not a normalization loss, and is a plausible driver of the repetitive
  email this project exists to reduce.
