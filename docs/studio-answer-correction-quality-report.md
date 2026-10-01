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
