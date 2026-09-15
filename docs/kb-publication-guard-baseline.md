# KB publication guard — pre-change baseline

**Captured:** 2026-09-15 (Asia/Beirut)

**Pre-change commit:** `6a7695e753bf95291ae510f7021a264a87a94d15`

**Purpose:** freeze the measured student behavior and operational facts before the
publication-guard implementation. This is a preservation baseline, not a claim that
the current system has no defects.

## Scope and isolation

All database-backed checks ran through `docker-compose.yml` plus
`docker-compose.dev.yml`. The `dev` service used the disposable `test-db` database
(`msfea_test`), not the local demo database or Oracle production. A clean ingestion
indexed **210 normalized-document chunks** and **0 curated answers** in that isolated
database.

The working tree already contained an untracked
`docs/kb-publication-guard-plan.md` and a deleted generated
`output/documents/MSFEA_LLM_Options_Comparison.docx`. The deleted artifact was not
restored, staged, or otherwise changed. A pre-existing orphaned
`msfea-synthesis` container was reported by Compose and left untouched.

## Frozen configuration

| Setting | Baseline value |
|---|---|
| LLM provider/model | Gemini / `gemini-flash-lite-latest` |
| Resolved model version | Not returned by the current provider adapter/SDK; alias recorded only |
| Temperature / seed | `0.0` / `42` |
| Maximum output | `1024` tokens |
| Normal retrieval depth | `7` (adaptive comparison depth remains enabled) |
| Similarity threshold | `0.60` |
| Embedding | `BAAI/bge-small-en-v1.5@5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` |
| Generation source SHA-256 | `139d19abd66a104ec14408cabc93b9e672010ca7ba9c96c322deb0955ef6293d` |
| Retrieval source SHA-256 | `ab385d9a762f34339307ba41a932512594baa938ffd2b2bbc2be25bd84c24536` |
| Chunking source SHA-256 | `40e28a561a078d94746e45c40b66eb725d1b4f0baf0537a9d054eb587cdaa597` |
| Normalized KB Git tree | `2b2fe38c5047d3eceb030202216e473884c0ecce` |

Runtime: Python 3.12.14, FastAPI 0.141.1, psycopg 3.3.5, pgvector 0.5.0,
Pydantic 2.13.5, pytest 9.1.1, Ruff 0.15.22, and mypy 2.3.0. The development
image is `sha256:388993b558b57907075a3dc635b87b47aaf6ee345869872b0652f8794d8e5c56`
(`amd64`, 653,218,366 bytes). Local Docker had 8 CPUs and 3,944,972,288 bytes of
memory available; this is not evidence of Oracle capacity.

## Automated gates

| Gate | Result |
|---|---|
| Ruff (`src tests eval`) | Pass |
| Strict mypy (`src eval`) | Pass, 43 source files |
| Widget submission guards | Pass, 3/3 |
| Python tests | Pass, 225/225; two upstream TestClient/AnyIO deprecation warnings |
| Clean isolated ingestion | Pass, 210 chunks |
| Production-depth context recall | 67/68 (98.5%); floor 90% |
| Known retrieval miss | `internship-vs-coop`: `graduation requirement` absent at the golden case's production depth |
| Similarity threshold | 109/109 valid queries pass; lowest 0.6329 |
| Off-topic pre-LLM blocking | 11/20 (55%); required floor 50% |
| Synthesis/follow-up premise + threshold gate | 19/19 |

The raw golden snapshot stores retrieved chunks per case. Its `hits` arrays are empty
because `eval/followup_eval.py` reads the `evidence_all` schema used by synthesis and
follow-up sets, while `golden_set.jsonl` uses singular `evidence`; the authoritative
golden pass/fail metric above comes from `eval.retrieval_eval`.

## Representative live answer baseline

The frozen ten-case set covers every known department, unknown department,
department exceptions, a corrective follow-up, comparison, topic switch, citations,
refusal, tone, and verbosity. It used **10 Gemini calls**, 27,363 input tokens and 539
output tokens. Provider latency was 1,043–1,689 ms (median 1,158 ms). Every normal
student turn made one generation call.

| Case | Review | Baseline observation |
|---|---|---|
| ECE 6+2 | Pass | Correct components, approval/documentation, concise answer and citations |
| MECH no-split | Pass | Correctly rejects two four-week periods without leaking ECE guidance |
| CEE split | Pass | Correctly preserves the civil/construction condition |
| IEM presentation | Pass | Correctly applies the IEM exception |
| CHEM/general eligibility | Pass | Correct 90-credit general rule with no invented CHEM exception |
| Unknown-department split | **Known failure** | Both MECH and CEE evidence were retrieved, but generation refused instead of qualifying the department-dependent rules |
| Corrective 6+2 follow-up | **Completeness failure** | Correctly states six company plus two research weeks, but this run omitted required approval/documentation conditions |
| Internship/CO-OP comparison | Pass | Covers duration, pay, optional status, and FEAA 500 waiver |
| IAESTE topic switch | Pass | Answers the new topic without carrying internship requirements forward |
| Undocumented rationale | Pass | Refuses and escalates without inventing a reason |

All eight passing answerable cases carried supporting citations; both refusals carried
none. All ten included the visible AI disclaimer. Answers were otherwise direct and
free of observed unsupported claims or unnecessary procedural dumps. The two failures
are explicit Step 1 targets and must not be hidden by aggregate metrics. The follow-up
omission also shows why the mutable `latest` model alias is not a fully reproducible
model identifier even with temperature and seed fixed.

## Saved per-case evidence

- `eval/publication_guard_baseline_set.jsonl` — frozen answer-preservation cases.
- `eval/results/publication_guard/baseline-answer-cases-live.jsonl` — prompts,
  retrieved chunks, token/latency metadata, answers, citations, and disclaimers.
- `eval/results/publication_guard/baseline-answer-cases-retrieval.jsonl` — the same
  cases without provider calls; all required answerable premises were retrieved.
- `eval/results/publication_guard/baseline-golden-retrieval.jsonl` — raw per-golden-case
  retrieval snapshot.
- `eval/results/publication_guard/baseline-synthesis-retrieval.jsonl` and
  `baseline-followup-retrieval.jsonl` — raw synthesis/follow-up retrieval snapshots.

The frozen case-set SHA-256 is
`455c3cace32eab602b21ac2c22b8a6b041e544db7a8ecd1673d6b61f7b8939d1`.
Artifact hashes are recorded alongside the Step 0 progress entry so later comparison
can detect accidental replacement.

## Production verification and resource feasibility

The Oracle inventory was read over SSH on 2026-09-15 without printing secrets. The
public endpoints also returned HTTP 200 with `{"status":"ok"}` and
`{"status":"ready"}` at `https://msfea-chatbot.duckdns.org`.

| Item | Verified state |
|---|---|
| Checkout | Clean `main` at `6a7695e753bf95291ae510f7021a264a87a94d15` |
| Application image | Compose image ID `sha256:7d5a39e3bcf7b7704b72c62c6641051ab46fe560d7edf4599c374c73c1bf75e6`; app healthy |
| Safe RAG configuration | Matches this baseline: Flash Lite alias, temperature 0, seed 42, 1,024-token ceiling, BGE revision, top-k 7, threshold 0.60 |
| Production index | 210 chunks; matching embedding fingerprint |
| Curated content | 0 active / 0 total rows |
| Host | ARM64, 2 CPUs, 12,506,693,632 bytes RAM, no swap |
| Available resources at snapshot | 11,131,105,280 bytes available RAM; 39,739,572,224 bytes disk available; root volume 16% used |
| Container memory at snapshot | App 650.9 MiB; PostgreSQL 32.68 MiB; Caddy 12.37 MiB |
| Published ports | Only Caddy publishes host ports 80/443; app and PostgreSQL remain private |
| Backup timer | Enabled and active; last trigger 2026-09-15 02:01:40 UTC; next scheduled 2026-09-16 02:04:25 UTC |
| Latest dump | `msfea-20260915-020140.sql.gz`, 456,110 bytes |

The latest dump was restored with `ON_ERROR_STOP` into a uniquely named temporary
database on the same PostgreSQL container. The restored copy contained 210 chunks,
0 curated rows, and 132 interactions. The temporary database was dropped afterward;
its absence and unchanged production counts were verified. This proves that the
on-VM dump is readable and the documented logical restore path works without touching
the live `msfea` database. It does not prove recovery from loss of the VM. A current
off-VM copy could not be verified from the host and remains a deployment/handover item.

Current RAM and disk headroom are sufficient for one resource-limited n8n container,
its small database, and one-at-a-time validation work. Two CPUs and no swap make CPU
contention the limiting risk, so validation must run outside student requests with
explicit CPU/memory limits and operational observation before concurrency is raised.
This is resource feasibility, not authorization to deploy n8n before its pinned ARM64
image and recovery procedure pass Step 7.

## Reproduction commands

Use the isolated Compose overlay for every DB-backed command:

```text
docker compose -f docker-compose.yml -f docker-compose.dev.yml build dev
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm dev python -m ruff check src tests eval
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm dev python -m mypy --strict src eval
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm dev pytest -q
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm dev python -m msfea_bot.skeleton ingest
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm -e EVAL_MIN_CONTEXT_RECALL=0.90 dev python -m eval.retrieval_eval
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm dev python -m eval.threshold_eval
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm dev python -m eval.synthesis_gate
node --test tests/widget_submission.test.cjs
```

Do not run pytest through the demo or production database. The tests intentionally
rebuild retrieval tables.
