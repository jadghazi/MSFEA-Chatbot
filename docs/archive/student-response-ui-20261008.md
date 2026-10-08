# Student response UI release — 2026-10-08

Historical release receipt: observations below describe this deployment, not a
live monitoring snapshot. Current behavior is in [architecture](../architecture.md).

## Change and verification

Release `a206d926387007f65df8730102a25f6294c1bd85` adds a subtle waiting indicator,
progressive display of the complete checked answer, a compact copy/feedback icon
row and an expandable Sources pill. This is client-side presentation, not provider
token streaming. The planned reveal duration is capped at 2.8 seconds. Reduced
motion and hidden tabs skip/complete it, and scrolling back respects the reader.
Sources/actions appear on completion; the composer stays locked through the reveal.

Local verification: 54 JavaScript behavior tests and four Python page checks passed;
JavaScript syntax, Ruff for the affected Python test and Git whitespace checks passed.
Browser fixtures verified standalone and embedded layouts, source expansion, complete
answer copying with confirmation and optional dislike reasons, without paid calls.
The separate user edits to CI environment/dashboard coverage were preserved unstaged.
Only this release's new reveal-test step was committed from that file.

## Oracle deployment

Built natively on aarch64 and recreated only `app`. App image:
`sha256:12b50019183d32cf2cd5bf649b792d238fdf9d1c4a2e1842b916f98bf6bebf95`.
Set only `APP_COMMIT` in the existing environment to the release SHA; student model
remains `gemini-3.8-flash` with its 4096-token ceiling. The curation worker remained
healthy on its previous image. No KB ingestion, schema change or synthetic publication.

Fresh application/n8n dumps and the previous environment/image reference are retained
under restricted ignored `backups/response-ui-20261008/`; SQL dumps were copied off VM
and matching SHA256s verified:

- Application: `b4fb9d5340cb408b6ea878ce423b170f4e11242401aaa38e3b0e87a1b5d67bea`.
- n8n: `be2a9878e8f5aa98de38fe825395cf22102f1918018d3847750a005d626e182e`.

The previous app image is tagged `msfea-chatbot-app:before-response-ui-20261008`.
The deployment shell wrapper reported a trailing carriage-return command after
the successful build/recreation. No deployment retry was needed: subsequent direct
checks confirmed the app healthy and its exact running release marker.

Public `/health`, `/ready` and the pilot page returned 200. The page references
`pilot-standalone-9`; public widget bytes match the reviewed local file, SHA256
`b78f36c2cea28c13cf683087c8bba4091593ea520db970cae3a1d1ce897cb615`.
Index count remained 246; paid attempts remained 14 through rebuild and health checks.

One live ECE question, “What is IAESTE?”, returned a grounded overview citing the
IAESTE source section. The loading state, complete controls, source expansion and
finished reveal cleanup were verified in the production browser with no console
errors. Attempts became 15: one completed student call, 2,421 input + 80 visible +
552 reasoning tokens, estimated $0.00418575. Production feedback was not submitted.

[GitHub CI](https://github.com/jadghazi/MSFEA-Chatbot/actions/runs/37813339850)
was still running when this receipt was recorded; the focused checks above had passed.
