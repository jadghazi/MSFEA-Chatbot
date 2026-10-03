> Historical local review. This predates the current guides and later implementation/approval decisions; it is not current operating guidance. Start with [the documentation index](../README.md).

# Main chatbot page refinement — 2026-09-27

## Scope and design decision

Local changes to the standalone student page. Plain HTML/CSS and the existing vanilla-JS client; no dependencies, retrieval, generation, API, dashboard or deployment changes. The embedded widget keeps its existing presentation. Existing unrelated workspace changes were left alone.

The revised design keeps the original maroon university header, introductory desktop sidebar and framed chat panel. It adds a consistent assistant icon, sans-serif chat headings, balanced department tiles, defined user/assistant bubbles, and an upward send arrow. The department-change control uses a compact bordered button with a chevron and hover state, keeping it close to the assistant title. The visible composer anchors the interface even before department selection. On mobile, the sidebar disappears, the chat toolbar is simplified, and five departments occupy a compact two-column layout with a full-width final choice.

Privacy details use a native disclosure with a visible no-personal-details reminder. An AI disclaimer is rendered as text beneath the composer in every standalone state. Source citations and per-answer disclaimers remain intact.

Trade-off: the persistent composer consumes some space before selection, but makes the screen immediately recognizable as a chat interface. Short screens retain internal scrolling instead of shrinking text or removing options. All five supported departments remain available.

## Research

- [NN/g: AI chatbot design guidelines](https://www.nngroup.com/articles/ai-chatbots-design-guidelines/): communicate scope and provide relevant starting questions. Applied through the existing scope statement and four question prompts.
- [NN/g: Explainable AI in chat interfaces](https://www.nngroup.com/articles/explainable-ai/): encourage verification and make sources available. Source disclosures and visible AI guidance remain.
- [W3C: Reflow](https://www.w3.org/WAI/WCAG21/Understanding/reflow): check narrow 320 CSS-pixel layouts for horizontal overflow.
- [WCAG 2.2](https://www.w3.org/TR/wcag/): keyboard focus, reflow and target size inform the review. The project uses a 44px button-height target here; this is not a claim of a complete WCAG audit.

## Acceptance checks and measured results

Criteria: no horizontal page overflow at five viewport sizes; primary buttons at least 44px high; the compact department-change button is 32px high; composer inside the viewport during chat; department selection, source disclosure, privacy disclosure, feedback and retry continue working; no browser JavaScript errors.

| Metric | Before | After |
| --- | ---: | ---: |
| 390 × 844 initial content viewport height | 518px | 567px |
| 320 × 568 welcome content overflow | 306px | 99px |
| Visible buttons below 44px, welcome screen | 3 | 1 (32px department selector) |
| Horizontal overflow across five viewport sizes | 0 | 0 |

Viewport sizes: 1440 × 900, 390 × 844, 320 × 568, 768 × 1024 and 844 × 390. Small-screen content still scrolls. Original `before-metrics.json` and final `revised-metrics.json` records are in `artifacts/ui/refinement/`. Landscape before/after heights are not directly comparable because the old page enforced a 540px minimum chat panel even in a 390px viewport.

Validation:

- `node --check widget/widget.js`
- `node --test tests/widget_submission.test.cjs`: 6 passed.
- `python -m pytest --noconftest tests/test_frontend.py -q`: 4 passed. These are dependency-free frontend assertions; normal pytest startup was blocked by missing local psycopg in the shared backend conftest.
- Browser flow checks at four sizes: department selection/reset, privacy, source expansion, feedback open/close, error/retry, composer bounds and no JavaScript errors. Passed using explicitly labeled intercepted sample answers, not live policy responses.
- Final `revised-*` screenshots inspected for initial, ready-to-chat and answer states. The standalone composer uses “Ask a question…” to avoid a wrapping placeholder. Earlier `after-*` screenshots belong to the rejected first pass.

Browser scripts are in `tmp/frontend-refinement/`. This is a Chromium viewport review, not physical iOS/Android keyboard testing. No backend answer-quality improvement is claimed and no RAG evaluation was necessary for these presentation-only changes.

## Review

Run `python -m http.server 8765 --bind 127.0.0.1` from the repository and open `http://127.0.0.1:8765/frontend/` for a layout-only preview. That static server has no chat API; production answers require the normal FastAPI application. Screenshots with `answer-fixture` in the filename contain test content only.

No commit, push or Oracle deployment was performed.
