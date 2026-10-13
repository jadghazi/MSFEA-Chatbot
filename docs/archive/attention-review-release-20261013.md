# Needs Attention review — 2026-10-13

Historical release receipt; current staff guidance is in [Studio](../studio.md).

Application release: `e6aa73d9c60fea741df002a55dcff5ec16c686aa`.
Scope: Needs Attention selection/display and bounded interaction-context logging.
No knowledge, retrieval, conversation routing, generation, model or provider-budget changes.

## Behavior and checks

- Queue: unresolved formal refusals, negative ratings and explicit missing-information
  wording signals. The last category is advisory and does not change recorded
  answered/refused outcomes. Ordinary responses and temporary provider errors stay out.
- Cards show actual replies, including refusals; four reason filters, expandable
  redacted conversation context, known department and original retrieval evidence.
  Empty states distinguish no candidates from no matches in the selected filter.
- New requests log at most eight preceding messages of 1,200 characters each.
  Additive interaction columns preserve older records; old context is not inferred
  from adjacent timestamps or tracked sessions. Staff-supplied context is labeled.
- 106 focused Python tests passed against the isolated development Compose test DB;
  final attention/abuse rerun: 53 passed. No live provider calls.
- 29 dashboard/Studio JavaScript tests passed; attention tests cover filtering,
  escaping, visible refusals, advisory labels and historical context states.
  Complete Ruff check and strict mypy check (115 source files) passed.
- Desktop/mobile rendering was visually reviewed. With actual dashboard styles,
  the 390-pixel mobile viewport had no horizontal overflow. JavaScript syntax and
  whitespace checks passed. The new browser test is included in CI.

## Oracle verification

App and worker were built natively and recreated with the matching application
commit. Only `APP_COMMIT` changed in the production environment.

- App image: `sha256:eae26d9ad37a0988c12252ba24d014b21b772ebcf1ff1ca759e575aa3e57430b`.
- Worker image: `sha256:d3e115ed0f781b44f6e635fe5ef094eb7aa44917fbeccceec0dc96278281ea26`.
- Public health/readiness and private worker health returned 200. Unauthenticated
  feedback access returned 401; authenticated feedback returned 23 candidates and
  the pending count matched at verification time.
- Original interaction 552, the reported ECE/CCE comparison, is selected automatically
  by the general wording signal. Its existing answer, refusal flag, rating and
  resolution state were preserved. The owner explicitly supplied the preceding
  exchange; matching stored interactions 550/551 supplied four redacted context
  messages attached only to 552 as `staff_reported`. Those ordinary earlier answers
  were verified absent from the queue. No fabricated student interaction or rating.
- Public dashboard HTML matches the committed file, SHA256
  `94e15cfb50b2907e123d7249429158f44ba31d484aa8cd86bbc533ae99958020`.
  Student page/widget bytes match the pre-release baseline.
- KB generation remains
  `sha256:79a543b25a9189af7d2a902fc6b115acd6ee6606796e1ead68036454bac864ea`;
  no ingestion or publication.

Fresh application/n8n dumps and pre-release environment are restricted in ignored
`backups/attention-20261013/` on Oracle and off VM. Matching SHA256s and complete
gzip/dump contents were verified: app
`cb29b605639f28b7ee02b72ce1de3fb479b4ff7a2e323bd2ab23d79812f01a50`, n8n
`5262317e98ce72dda75686f6d67cca61f4216ba97269e82b8b1b5195bccd1ffa`.
Previous app/worker images are tagged `before-attention-20261013`; additive logging
columns can remain during an image rollback. Preserve later production writes.
Unrelated local CI edits and user files were preserved.
