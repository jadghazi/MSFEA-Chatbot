# Source-backed corrections in the writing assistant

2026-10-01. Suggestions remain available for completed conflict, replacement,
duplicate and clarification reviews. This changes private writing assistance,
not student generation, retrieval, source ingestion or publication authority.

## Boundary

The writer may propose a correction using existing KB evidence. It must disclose
each substantive original-claim correction/removal with original/proposed quotes,
a reason and KB references. The UI places these in a visible **Changes to your
claims** section above the word diff. Original input remains unchanged until use;
the admin can edit/discard. Human-edited proposals clearly identify the earlier
AI explanations as applying to the offered version. Use starts fresh review;
normal source confirmation, private tests and publication approval still apply.
The clean proposed answer is the primary view; word changes and extra evidence
are expandable. Essential unanswered questions appear directly under the answer.
The verifier can add a missing question even if the writer omitted it, rather
than only selecting among the writer's questions.

Code rejects unknown evidence, invented numbers/URLs, invalid claim/sentence references,
disputed-original references used to justify a correction, and unexplained removal
of original numbers/URLs. The separate model call checks sentence support, topic
scope and disclosure rather than asserting that original meaning was preserved.
These checks are advisory, not a proof of semantic correctness.

An absent source is not a contradiction: do not deny a newly supplied service's
existence, substitute another service or borrow its operating hours. Preserve new
admin facts and ask for missing details. Likewise, 'normally summer' establishes
neither winter permission nor a winter prohibition.

## Live trials and retained failures

The fixed live runner now checks declared 3/5-to-1-credit corrections, summer
qualifiers, incomplete guidance, a complete short answer, and two unknown services.
Results and earlier attempts remain in the disposable stack's ignored
`tmp/studio-suggestion-corrections-v2.jsonl`.

The first missing-hours attempt incorrectly substituted existing advising/portfolio
services and denied the fictional desk's existence. No publication occurred. This
failure prompted explicit same-subject and absence-versus-contradiction checks in
both calls, followed by a second unknown-service case rather than reporting the
first attempt as a success. Literal before/after transcription was brittle, so
the writer now selects references and code constructs the quotes. A live schema
probe found Gemini rejected a format with multiple original/sentence references;
one original claim and one revised sentence per change worked. Those rejected
requests, provider 503 failures and interrupted local jobs remain recorded.
Failed suggestions now expose anonymized check feedback, with
no unverified answer offered for use.

The suggestion schema has a new version. Old queued proposals are failed by the
existing version guard; old reports remain readable and the UI requests a new
suggestion. No migrations, dependencies, services or quota changes are required.

## Final verification — 2026-10-02

- Final v4 live fixed set: **8/8 pass**. The complete short-answer case needed an
  explicit retry after a Gemini 503; the earlier failure is retained. These are
  bounded fixture checks, not an estimate of accuracy on arbitrary admin input.
- Backend suggestion checks: **28 pass**. Frontend review/preview/suggestion checks:
  **34 pass**. Ruff and strict typing pass. [CI for implementation b8f5a1f](https://github.com/jadghazi/MSFEA-Chatbot/actions/runs/36928110021)
  passed the full backend suite and all eight existing gates.
- Retrieval gates match the existing baseline: golden 122/124, faculty 198/205,
  synthesis 75/75, conversation 21/21 (independent 9/9), stress 43/43
  (independent 19/19). Threshold checks retain valid 165/165 and off-topic 12/20;
  this change does not fix those existing misses. Publication 9/9 and conflict
  7/7 pass, with zero false positives in the conflict fixtures.
- Browser-tested the actual winter example: the proposal changes mandatory summer
  wording to the quoted **normally** wording, displays the correction and source,
  and asks explicitly whether winter completion is permitted. A human edit updates
  the readable proposal and marks the earlier AI check as applying to the offered
  version. **Use & review again** starts a fresh review, which asks for the missing
  winter policy rather than approving publication. Desktop and mobile inspected;
  no synthetic entry was published in these trials.

## Oracle rollout

Implementation **b8f5a1f** is deployed to the ARM64 app and curation worker.
Application and n8n database backups and rollback image tags were retained before
activation; there were no in-flight staff/publication jobs when containers were
replaced. All six serving services are running, app/worker health checks pass,
public health/readiness return 200, the internal health endpoint remains 404 from
the public proxy, and an unauthenticated suggestion request returns 401.
Public dashboard asset hashes match the image files.

A live v4 production suggestion for the existing 90-credit registration rule
completed, could not create a draft directly, and was submitted to a fresh review
that correctly identified it as duplicate. No entry or publication was created.
Student letter and follow-up answers still contain the official request URL,
citations and disclaimer. Production remains **253 chunks / zero curated entries**
at generation `sha256:d7b163e7be4bad3da2951a80c3a53e0a9ed11e704a4cb2759277f1b37354a2e4`.
The environment file is byte-for-byte unchanged, including models and budgets.
