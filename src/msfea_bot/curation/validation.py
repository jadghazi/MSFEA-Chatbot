"""Deterministic validation steps for guarded KB publication.

No step calls an LLM. n8n may sequence these bounded operations, but PostgreSQL
state and this module remain authoritative.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

import psycopg
from psycopg.types.json import Json

from eval.loader import load_golden_set
from eval.metrics import evidence_present
from msfea_bot import departments
from msfea_bot.config import settings
from msfea_bot.curation.revisions import Revision, list_revisions, program_registry
from msfea_bot.curation.service import curated_chunks, revision_chunks
from msfea_bot.generation.answer import build_prompt, passes_similarity_gate
from msfea_bot.generation.conversation import ConversationMessage, build_retrieval_query
from msfea_bot.ingestion.chunking import Chunk, chunk_normalized_dir
from msfea_bot.ingestion.embeddings import model_fingerprint
from msfea_bot.retrieval.store import index_chunks, indexed_generation, retrieval_depth, search

VALIDATOR_VERSION = "publication-guard-v2-admin-sources"
REQUIRED_STEPS = (
    "schema_source",
    "candidate_index",
    "conflict_review",
    "positive_retrieval",
    "department_isolation",
    "unknown_department",
    "regression",
)
_TERMINAL_RESULTS = {"passed", "failed", "timed_out", "skipped"}
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_LONG_NUMBER = re.compile(r"\b\d[\d\s().-]{5,}\d\b")
_WORD = re.compile(r"[a-z0-9]+")
_NEGATION = re.compile(r"\b(no|not|never|cannot|can't|prohibited|forbidden)\b", re.I)
_NUMBER = re.compile(r"\b\d+(?:\.\d+)?%?\b")
_NUMBER_WITH_UNIT = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*((?:credits?|weeks?|months?|hours?|days?|pages?|words?)\b|%)",
    re.I,
)
_GENERIC_CONFLICT_WORDS = {
    "a", "all", "an", "and", "are", "as", "at", "be", "because", "by", "can",
    "course", "do", "does", "experience", "for", "from", "guidance", "in", "internship",
    "is", "it", "may", "must", "of", "on", "or", "program", "registered", "student",
    "students", "the", "their", "this", "to", "when", "with", "your",
}


def _connect() -> Any:
    return psycopg.connect(settings.database_url, autocommit=False, connect_timeout=5)


def get_revision(revision_id: int) -> Revision | None:
    return next((item for item in list_revisions() if item.id == revision_id), None)


def _normalized(value: str) -> str:
    value = re.sub(r"[*_`]", "", value).casefold()
    return re.sub(r"\s+", " ", value).strip()


def expected_evidence_present(chunk_texts: list[str], evidence: str) -> bool:
    """Match ordered evidence words without making punctuation a failure mode."""
    needle = " ".join(_WORD.findall(evidence.casefold()))
    return bool(needle) and any(
        needle in " ".join(_WORD.findall(text.casefold())) for text in chunk_texts
    )


def _number_units(value: str) -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for number, raw_unit in _NUMBER_WITH_UNIT.findall(value):
        unit = raw_unit.casefold()
        if unit != "%" and unit.endswith("s"):
            unit = unit[:-1]
        found.setdefault(unit, set()).add(number)
    return found


def _opposite_polarity_claim(answer: str, chunk: str, answer_words: set[str]) -> bool:
    """Require shared claim words in the particular sentence carrying the opposite polarity."""
    answer_negative = bool(_NEGATION.search(answer))
    for segment in re.split(r"(?:\r?\n)+|(?<=[.!?])\s+", chunk):
        if bool(_NEGATION.search(segment)) == answer_negative:
            continue
        segment_words = set(_WORD.findall(_normalized(segment))) - _GENERIC_CONFLICT_WORDS
        if len(answer_words & segment_words) >= 2:
            return True
    return False


def _same_scope_for_flag(candidate: RetrievedLike, department: str | None) -> bool:
    """General guidance is context for a scoped exception, not an automatic conflict."""
    candidate_scope = candidate.metadata.get("department", "all") or "all"
    requested_scope = department or "all"
    return candidate_scope == requested_scope


def _file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _eval_hash() -> str:
    root = Path(__file__).resolve().parents[3] / "eval"
    names = (
        "golden_set.jsonl",
        "synthesis_set.jsonl",
        "followup_set.jsonl",
        "scope_regression_set.jsonl",
        "conflict_review_set.jsonl",
    )
    digest = hashlib.sha256()
    for name in names:
        path = root / name
        digest.update(name.encode())
        if path.exists():
            digest.update(path.read_bytes())
    return "sha256:" + digest.hexdigest()


def validation_fingerprint(revision: Revision) -> str:
    normalized = Path(__file__).resolve().parents[3] / "kb" / "normalized"
    sources = {path.name: _file_hash(path) for path in sorted(normalized.glob("*.md"))}
    payload = {
        "revision": revision.content_hash,
        "sources": sources,
        "active_kb_generation": indexed_generation() or "missing",
        "embedding": model_fingerprint(),
        "retrieval": {
            "top_k": settings.top_k,
            "similarity_threshold": settings.similarity_threshold,
        },
        "evaluation_set": _eval_hash(),
        "app_commit": settings.app_commit or "local-unset",
        "validator": VALIDATOR_VERSION,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _validation_database_url(override: str | None = None) -> str:
    dsn = override or settings.validation_database_url
    if not dsn:
        raise ValueError("VALIDATION_DATABASE_URL is required")
    if dsn == settings.database_url:
        raise ValueError("validation and student-serving database URLs must differ")
    return dsn


def start_validation(revision_id: int) -> str:
    revision = get_revision(revision_id)
    if revision is None:
        raise ValueError("revision does not exist")
    if revision.state not in {"draft", "blocked", "ready"}:
        raise ValueError(f"revision in state {revision.state!r} cannot be validated")
    fingerprint = validation_fingerprint(revision)
    run_id = str(uuid4())
    with _connect() as conn:
        state = conn.execute(
            "SELECT state FROM curation_revision_state WHERE revision_id = %s FOR UPDATE",
            (revision_id,),
        ).fetchone()
        if state is None or state[0] not in {"draft", "blocked", "ready"}:
            raise ValueError("revision state changed; reload and try again")
        conn.execute(
            "UPDATE curation_revision_state SET state = 'validating', state_version = state_version + 1,"
            " reason = 'Deterministic validation is running.', updated_at = now()"
            " WHERE revision_id = %s",
            (revision_id,),
        )
        conn.execute(
            "INSERT INTO curation_validation_runs (id, revision_id, fingerprint, status)"
            " VALUES (%s, %s, %s, 'pending')",
            (run_id, revision_id, fingerprint),
        )
        for step in REQUIRED_STEPS:
            conn.execute(
                "INSERT INTO curation_jobs (id, validation_run_id, step, status)"
                " VALUES (%s, %s, %s, 'pending')",
                (f"{run_id}:{step}", run_id, step),
            )
        conn.execute(
            "INSERT INTO curation_outbox (event_type, aggregate_id, payload)"
            " VALUES ('validation_requested', %s, %s)",
            (run_id, Json({"run_id": run_id, "revision_id": revision_id})),
        )
        conn.execute(
            "INSERT INTO curation_events (entry_id, revision_id, validation_run_id,"
            " event_type, actor_type, reason)"
            " VALUES (%s, %s, %s, 'validation_requested', 'admin', 'Draft submitted for checks.')",
            (revision.entry_id, revision.id, run_id),
        )
    return run_id


def _run(run_id: str) -> tuple[Revision, str, str | None]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT revision_id, fingerprint, candidate_generation"
            " FROM curation_validation_runs WHERE id = %s",
            (run_id,),
        ).fetchone()
    if row is None:
        raise ValueError("validation run does not exist")
    revision = get_revision(int(row[0]))
    if revision is None:
        raise RuntimeError("validation run references a missing revision")
    return revision, str(row[1]), str(row[2]) if row[2] is not None else None


def _source_check(revision: Revision) -> tuple[bool, dict[str, Any]]:
    root = Path(__file__).resolve().parents[3] / "kb" / "normalized"
    errors: list[str] = []
    resolved: list[dict[str, str]] = []
    if revision.source_kind == "admin_authored":
        if not revision.document_title.strip():
            errors.append("Focused knowledge document title is required")
        if not revision.authority_label.strip():
            errors.append("Responsible CDC office or policy owner is required")
        resolved.append(
            {
                "source_doc": f"CDC Knowledge KB-{revision.entry_id}: {revision.document_title}",
                "locator": revision.document_title,
                "source_hash": revision.content_hash,
                "evidence_hash": "sha256:"
                + hashlib.sha256(_normalized(revision.answer).encode()).hexdigest(),
                "authority": revision.authority_label,
            }
        )
    elif revision.source_kind != "official_reference":
        errors.append("Legacy knowledge must be replaced by a reviewed successor before validation")

    evidence_text = "\n".join(reference["excerpt"] for reference in revision.evidence_refs)
    references = revision.evidence_refs if revision.source_kind == "official_reference" else []
    for reference in references:
        source_doc = reference["source_doc"]
        path = root / source_doc
        if path.parent != root or not path.is_file() or path.suffix.lower() != ".md":
            errors.append(f"Unknown reviewed source: {source_doc}")
            continue
        locator = reference["locator"].strip().casefold()
        matching_sections = [
            line.lstrip("#").strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("##") and line.lstrip("#").strip().casefold() == locator
        ]
        if len(matching_sections) != 1:
            errors.append(f"Locator must resolve to one section: {source_doc} > {reference['locator']}")
            continue
        if _normalized(reference["excerpt"]) not in _normalized(path.read_text(encoding="utf-8")):
            errors.append(f"Evidence excerpt not found in declared source: {source_doc}")
            continue
        resolved.append(
            {
                "source_doc": source_doc,
                "locator": matching_sections[0],
                "source_hash": _file_hash(path),
                "evidence_hash": "sha256:"
                + hashlib.sha256(_normalized(reference["excerpt"]).encode()).hexdigest(),
            }
        )
    allowed_identifiers = set(_EMAIL.findall(evidence_text)) | set(
        _LONG_NUMBER.findall(evidence_text)
    )
    if revision.source_kind == "official_reference":
        authored = "\n".join((revision.question, revision.answer, revision.change_reason))
        unexpected = (
            set(_EMAIL.findall(authored)) | set(_LONG_NUMBER.findall(authored))
        ) - allowed_identifiers
        if unexpected:
            errors.append("Draft contains identifiers not present in its reviewed evidence")
    valid_scope = revision.department in {
        "all",
        *(department.code for department in departments.DEPARTMENTS),
    }
    if not valid_scope:
        errors.append("Missing or invalid department applicability")
    allowed_programs = set(program_registry())
    if not revision.programs or any(program not in allowed_programs for program in revision.programs):
        errors.append("Missing or invalid reviewed program")
    return not errors, {"errors": errors, "resolved_evidence": resolved}


class RetrievedLike(Protocol):
    """Structural typing helper kept runtime-light for related passage logic."""

    id: str
    text: str
    source_doc: str
    section: str
    score: float
    metadata: dict[str, str]


def review_candidates(
    question: str,
    answer: str,
    department: str | None,
    *,
    database_url: str | None = None,
    depth: int = 30,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return related passages and explainable potential-conflict flags."""
    found: dict[str, RetrievedLike] = {}
    for query in (question, answer):
        for chunk in search(query, depth, candidates=max(depth, 40), database_url=database_url):
            if not chunk.id.startswith("candidate-"):
                found.setdefault(chunk.id, chunk)
    related: list[dict[str, Any]] = []
    flags: list[dict[str, Any]] = []
    answer_plain = _normalized(answer)
    answer_words = set(_WORD.findall(answer_plain))
    answer_units = _number_units(answer)
    answer_distinctive = answer_words - _GENERIC_CONFLICT_WORDS
    for related_chunk in sorted(found.values(), key=lambda item: item.score, reverse=True):
        scope = related_chunk.metadata.get("department", "all") or "all"
        item = {
            "id": related_chunk.id,
            "source_doc": related_chunk.source_doc,
            "section": related_chunk.section,
            "department": scope,
            "score": round(related_chunk.score, 6),
            "text": related_chunk.text,
        }
        related.append(item)
        chunk_plain = _normalized(related_chunk.text)
        chunk_words = set(_WORD.findall(chunk_plain))
        overlap = len(answer_words & chunk_words) / max(1, len(answer_words))
        exact = answer_plain in chunk_plain or chunk_plain in answer_plain
        polarity_differs = _opposite_polarity_claim(
            answer, related_chunk.text, answer_distinctive
        )
        chunk_units = _number_units(related_chunk.text)
        shared_units = set(answer_units) & set(chunk_units)
        unit_numbers_differ = any(
            answer_units[unit] != chunk_units[unit] for unit in shared_units
        )
        answer_numbers = set(_NUMBER.findall(answer))
        chunk_numbers = set(_NUMBER.findall(related_chunk.text))
        high_overlap_numbers_differ = bool(
            overlap >= 0.55
            and answer_numbers
            and chunk_numbers
            and answer_numbers != chunk_numbers
        )
        numbers_differ = unit_numbers_differ or high_overlap_numbers_differ
        if exact:
            flags.append({"candidate_id": related_chunk.id, "reason": "exact_duplicate"})
        elif _same_scope_for_flag(related_chunk, department) and (
            numbers_differ or polarity_differs
        ):
            flags.append(
                {
                    "candidate_id": related_chunk.id,
                    "reason": "possible_negation_conflict"
                    if polarity_differs
                    else "possible_numeric_conflict",
                }
            )
        elif _same_scope_for_flag(related_chunk, department) and overlap >= 0.90:
            flags.append(
                {"candidate_id": related_chunk.id, "reason": "possible_duplicate"}
            )
    return related, flags


def _candidate_chunks(revision: Revision) -> list[Chunk]:
    chunks = chunk_normalized_dir() + curated_chunks()
    active_prefix = f"curated-{revision.entry_id}-"
    chunks = [chunk for chunk in chunks if not chunk.id.startswith(active_prefix)]
    return chunks + revision_chunks(revision, candidate=True)


def _candidate_ids(revision: Revision) -> set[str]:
    return {chunk.id for chunk in revision_chunks(revision, candidate=True)}


def _declared_evidence_candidates(revision: Revision) -> list[dict[str, Any]]:
    declared: list[dict[str, Any]] = []
    for reference in revision.evidence_refs:
        for chunk in chunk_normalized_dir():
            if (
                chunk.source_doc == reference["source_doc"]
                and chunk.section.casefold() == reference["locator"].casefold()
                and evidence_present([chunk.text], reference["excerpt"])
            ):
                declared.append(
                    {
                        "id": chunk.id,
                        "source_doc": chunk.source_doc,
                        "section": chunk.section,
                        "department": chunk.metadata.get("department", "all"),
                        "score": None,
                        "text": chunk.text,
                        "reason": "declared_evidence",
                    }
                )
    return declared


def _positive_retrieval(revision: Revision, dsn: str) -> tuple[bool, dict[str, Any]]:
    expected_ids = _candidate_ids(revision)
    cases: list[dict[str, Any]] = []
    for question in (revision.representative_question, revision.paraphrase_question):
        if question is None:
            continue
        chunks = search(
            question,
            retrieval_depth(question, settings.top_k),
            department=revision.department if revision.department != "all" else None,
            database_url=dsn,
        )
        ids = [chunk.id for chunk in chunks]
        evidence_hit = expected_evidence_present(
            [chunk.text for chunk in chunks], revision.expected_evidence or ""
        )
        candidate_hit = bool(expected_ids & set(ids))
        similarity_passed = passes_similarity_gate(chunks, settings.similarity_threshold)
        passed = candidate_hit and evidence_hit and similarity_passed
        cases.append(
            {
                "question": question,
                "passed": passed,
                "retrieved_ids": ids,
                "candidate_hit": candidate_hit,
                "evidence_hit": evidence_hit,
                "similarity_passed": similarity_passed,
                "expected_evidence": revision.expected_evidence or "",
            }
        )
    return bool(cases) and all(case["passed"] for case in cases), {"cases": cases}


def _department_isolation(revision: Revision, dsn: str) -> tuple[bool, dict[str, Any]]:
    expected_ids = _candidate_ids(revision)
    results: dict[str, bool] = {}
    question = revision.representative_question or revision.question
    for department in departments.DEPARTMENTS:
        chunks = search(question, settings.top_k, department=department.code, database_url=dsn)
        present = bool(expected_ids & {chunk.id for chunk in chunks})
        results[department.code] = present
    if revision.department == "all":
        passed = all(results.values())
    else:
        passed = results.get(revision.department or "", False) and not any(
            present for code, present in results.items() if code != revision.department
        )
    return passed, {"candidate_returned_by_department": results}


def _unknown_department(revision: Revision, dsn: str) -> tuple[bool, dict[str, Any]]:
    question = revision.representative_question or revision.question
    chunks = search(question, settings.top_k, database_url=dsn)
    expected = _candidate_ids(revision)
    candidate_chunks = [chunk for chunk in chunks if chunk.id in expected]
    if not candidate_chunks:
        return False, {"error": "candidate absent from unknown-department retrieval"}
    # Validate the candidate's own display context. Other top-k passages may be
    # department-scoped and legitimately carry an applicability label; checking
    # the whole mixed prompt would therefore reject a general candidate for an
    # unrelated scoped passage.
    prompt = build_prompt(question, candidate_chunks)
    if revision.department == "all":
        passed = "Applicability:" not in prompt
    else:
        label = departments.describe(revision.department)
        passed = f"Applicability: {label} only." in prompt
    return passed, {"candidate_ids": [chunk.id for chunk in candidate_chunks], "labeled": passed}


def _jsonl_cases(name: str) -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parents[3] / "eval" / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _regression(dsn: str) -> tuple[bool, dict[str, Any]]:
    lost: list[str] = []
    baseline_failures: list[str] = []
    checked = 0
    for item in load_golden_set():
        if item.should_refuse or not item.evidence:
            continue
        query = build_retrieval_query(item.question, item.history)
        depth = retrieval_depth(item.question, settings.top_k)
        before = search(query, depth, department=item.department)
        after = search(query, depth, department=item.department, database_url=dsn)
        was_hit = evidence_present([chunk.text for chunk in before], item.evidence)
        now_hit = evidence_present([chunk.text for chunk in after], item.evidence)
        checked += 1
        if not was_hit:
            baseline_failures.append(item.id)
        if was_hit and not now_hit:
            lost.append(item.id)
    premise_baseline_failures: list[str] = []
    premise_regressions: list[str] = []
    for name in ("synthesis_set.jsonl", "followup_set.jsonl", "scope_regression_set.jsonl"):
        for case in _jsonl_cases(name):
            if case["should_refuse"]:
                continue
            history = [ConversationMessage(**message) for message in case.get("history", [])]
            query = build_retrieval_query(case["question"], history)
            before = search(
                query,
                retrieval_depth(case["question"], settings.top_k),
                department=case.get("department"),
            )
            after = search(
                query,
                retrieval_depth(case["question"], settings.top_k),
                department=case.get("department"),
                database_url=dsn,
            )
            was_complete = all(
                evidence_present([chunk.text for chunk in before], evidence)
                for evidence in case["evidence_all"]
            )
            now_complete = all(
                evidence_present([chunk.text for chunk in after], evidence)
                for evidence in case["evidence_all"]
            )
            if not was_complete:
                premise_baseline_failures.append(case["id"])
            if was_complete and not now_complete:
                premise_regressions.append(case["id"])
    return not lost and not premise_regressions, {
        "golden_cases_compared": checked,
        "golden_baseline_failures": baseline_failures,
        "newly_lost_previously_passing": lost,
        "premise_baseline_failures": premise_baseline_failures,
        "new_premise_regressions": premise_regressions,
    }


def _save_result(
    run_id: str, step: str, passed: bool, details: dict[str, Any]
) -> None:
    status = "passed" if passed else "failed"
    with _connect() as conn:
        conn.execute(
            "INSERT INTO curation_validation_results (run_id, step, status, details,"
            " started_at, completed_at) VALUES (%s, %s, %s, %s, now(), now())"
            " ON CONFLICT (run_id, step) DO NOTHING",
            (run_id, step, status, Json(details)),
        )
        conn.execute(
            "UPDATE curation_jobs SET status = %s,"
            " updated_at = now(), last_error = %s WHERE validation_run_id = %s AND step = %s",
            ("succeeded" if passed else "failed", None if passed else json.dumps(details), run_id, step),
        )
        conn.execute(
            "UPDATE curation_validation_runs SET status = 'running',"
            " started_at = COALESCE(started_at, now()) WHERE id = %s AND status = 'pending'",
            (run_id,),
        )
        if not passed:
            revision_id = conn.execute(
                "SELECT revision_id FROM curation_validation_runs WHERE id = %s", (run_id,)
            ).fetchone()
            conn.execute(
                "UPDATE curation_validation_runs SET status = 'failed', completed_at = now(),"
                " error_code = %s WHERE id = %s",
                (f"{step}_failed", run_id),
            )
            conn.execute(
                "UPDATE curation_jobs SET status = 'cancelled', updated_at = now()"
                " WHERE validation_run_id = %s AND status = 'pending'",
                (run_id,),
            )
            if revision_id is not None:
                conn.execute(
                    "UPDATE curation_revision_state SET state = 'blocked', reason = %s,"
                    " state_version = state_version + 1, updated_at = now()"
                    " WHERE revision_id = %s",
                    (f"Automatic validation failed: {step}", revision_id[0]),
                )
    _finalize_if_complete(run_id)


def _finalize_if_complete(run_id: str) -> None:
    revision, _, _ = _run(run_id)
    with _connect() as conn:
        rows = conn.execute(
            "SELECT step, status, details FROM curation_validation_results WHERE run_id = %s",
            (run_id,),
        ).fetchall()
        results = {str(row[0]): (str(row[1]), row[2]) for row in rows}
        if set(results) != set(REQUIRED_STEPS):
            return
        failed = [step for step, (status, _) in results.items() if status != "passed"]
        conflict_flags = results["conflict_review"][1].get("flags", [])
        if failed:
            run_status, state = "failed", "blocked"
            reason = "Automatic validation failed: " + ", ".join(sorted(failed))
        elif conflict_flags:
            run_status, state = "passed", "blocked"
            reason = "Human review required for potential conflicts."
        else:
            run_status, state = "passed", "ready"
            reason = "Automatic checks passed; mandatory human review is still required."
        conn.execute(
            "UPDATE curation_validation_runs SET status = %s, completed_at = now() WHERE id = %s",
            (run_status, run_id),
        )
        conn.execute(
            "UPDATE curation_revision_state SET state = %s, reason = %s,"
            " state_version = state_version + 1, updated_at = now() WHERE revision_id = %s",
            (state, reason, revision.id),
        )


def execute_step(run_id: str, step: str, validation_database_url: str | None = None) -> None:
    if step not in REQUIRED_STEPS:
        raise ValueError(f"unknown validation step: {step}")
    with _connect() as conn:
        job = conn.execute(
            "SELECT j.status, r.status FROM curation_jobs j"
            " JOIN curation_validation_runs r ON r.id = j.validation_run_id"
            " WHERE j.validation_run_id = %s AND j.step = %s FOR UPDATE",
            (run_id, step),
        ).fetchone()
        if job is None:
            raise ValueError("validation job does not exist")
        if job[0] != "pending" or job[1] not in {"pending", "running"}:
            raise ValueError(f"validation step is not pending (job={job[0]}, run={job[1]})")
        conn.execute(
            "UPDATE curation_jobs SET status = 'leased', lease_expires_at = now() + interval '15 minutes',"
            " attempts = attempts + 1, updated_at = now()"
            " WHERE validation_run_id = %s AND step = %s",
            (run_id, step),
        )
    revision, fingerprint, candidate_generation = _run(run_id)
    if validation_fingerprint(revision) != fingerprint:
        with _connect() as conn:
            conn.execute(
                "UPDATE curation_validation_runs SET status = 'stale', completed_at = now()"
                " WHERE id = %s",
                (run_id,),
            )
            conn.execute(
                "UPDATE curation_revision_state SET state = 'blocked',"
                " reason = 'Validation fingerprint is stale; rerun all checks.',"
                " state_version = state_version + 1, updated_at = now() WHERE revision_id = %s",
                (revision.id,),
            )
            conn.execute(
                "UPDATE curation_jobs SET status = 'cancelled', updated_at = now()"
                " WHERE validation_run_id = %s AND status IN ('pending', 'leased')",
                (run_id,),
            )
        return
    dsn = _validation_database_url(validation_database_url)
    if step == "schema_source":
        passed, details = _source_check(revision)
    elif step == "candidate_index":
        count = index_chunks(_candidate_chunks(revision), database_url=dsn)
        generation = indexed_generation(dsn)
        with _connect() as conn:
            conn.execute(
                "UPDATE curation_validation_runs SET candidate_generation = %s WHERE id = %s",
                (generation, run_id),
            )
        passed, details = bool(generation), {"chunks": count, "generation": generation}
    else:
        if not candidate_generation:
            raise ValueError("candidate_index must complete before retrieval validation steps")
        if indexed_generation(dsn) != candidate_generation:
            raise ValueError("isolated candidate index changed; restart validation")
        if step == "conflict_review":
            related, flags = review_candidates(
                revision.question,
                revision.answer,
                revision.department,
                database_url=dsn,
            )
            present = {item["id"] for item in related}
            related.extend(
                item for item in _declared_evidence_candidates(revision)
                if item["id"] not in present
            )
            passed, details = True, {
                "label": "No potential conflicts flagged" if not flags else "Potential conflicts flagged",
                "related": related,
                "flags": flags,
            }
        elif step == "positive_retrieval":
            passed, details = _positive_retrieval(revision, dsn)
        elif step == "department_isolation":
            passed, details = _department_isolation(revision, dsn)
        elif step == "unknown_department":
            passed, details = _unknown_department(revision, dsn)
        else:
            passed, details = _regression(dsn)
    _save_result(run_id, step, passed, details)


def execute_step_idempotent(
    run_id: str,
    step: str,
    idempotency_key: str,
    workflow_execution_id: str = "",
) -> dict[str, Any]:
    """Execute one n8n-requested step, returning an existing durable result on replay."""
    expected_key = f"{run_id}:{step}"
    if idempotency_key != expected_key:
        raise ValueError("idempotency key does not match validation run and step")
    with _connect() as conn:
        existing = conn.execute(
            "SELECT status FROM curation_validation_results"
            " WHERE run_id = %s AND step = %s",
            (run_id, step),
        ).fetchone()
        if existing is not None:
            return {"run_id": run_id, "step": step, "status": str(existing[0]),
                    "idempotent": True}
        job = conn.execute(
            "SELECT status, available_at FROM curation_jobs"
            " WHERE validation_run_id = %s AND step = %s",
            (run_id, step),
        ).fetchone()
        if job is None:
            raise ValueError("validation job does not exist")
        if job[0] == "leased":
            raise ValueError("validation step is already leased")
        if job[0] != "pending" or job[1] > datetime.now(timezone.utc):
            raise ValueError("validation step is not ready for execution")
        if workflow_execution_id:
            conn.execute(
                "UPDATE curation_validation_runs SET workflow_execution_id = %s"
                " WHERE id = %s AND (workflow_execution_id IS NULL"
                " OR workflow_execution_id = %s)",
                (workflow_execution_id, run_id, workflow_execution_id),
            )
    try:
        execute_step(run_id, step)
    except Exception as exc:
        with _connect() as conn:
            job = conn.execute(
                "SELECT attempts FROM curation_jobs"
                " WHERE validation_run_id = %s AND step = %s FOR UPDATE",
                (run_id, step),
            ).fetchone()
            attempts = int(job[0]) if job else 0
            if attempts < 3:
                conn.execute(
                    "UPDATE curation_jobs SET status = 'pending',"
                    " lease_expires_at = NULL, available_at = now() + (%s * interval '1 second'),"
                    " last_error = %s, updated_at = now()"
                    " WHERE validation_run_id = %s AND step = %s AND status = 'leased'",
                    (min(60, 2**attempts), type(exc).__name__, run_id, step),
                )
        raise
    with _connect() as conn:
        result = conn.execute(
            "SELECT status FROM curation_validation_results"
            " WHERE run_id = %s AND step = %s",
            (run_id, step),
        ).fetchone()
    if result is None:
        raise RuntimeError("validation step completed without a durable result")
    return {"run_id": run_id, "step": step, "status": str(result[0]),
            "idempotent": False}


def record_human_review(
    run_id: str,
    reviewer_label: str,
    decision: str,
    reason: str,
) -> int:
    revision, fingerprint, _ = _run(run_id)
    if not reviewer_label.strip() or not reason.strip():
        raise ValueError("reviewer label and reason are required")
    allowed = {"confirm_no_conflict", "valid_scoped_exception", "reject", "replace_outdated"}
    if decision not in allowed:
        raise ValueError("invalid review decision")
    if decision == "replace_outdated" and (
        revision.source_kind != "admin_authored" or revision.predecessor_revision_id is None
    ):
        raise ValueError(
            "supersession is only available for a successor of an admin-authored source; "
            "official files must be corrected through reviewed file ingestion"
        )
    if validation_fingerprint(revision) != fingerprint:
        raise ValueError("validation is stale; rerun before review")
    with _connect() as conn:
        results = conn.execute(
            "SELECT step, status, details FROM curation_validation_results WHERE run_id = %s",
            (run_id,),
        ).fetchall()
        statuses = {str(row[0]): str(row[1]) for row in results}
        if set(statuses) != set(REQUIRED_STEPS) or any(
            status not in _TERMINAL_RESULTS for status in statuses.values()
        ):
            raise ValueError("all validation steps must finish before human review")
        if any(status != "passed" for status in statuses.values()) and decision != "reject":
            raise ValueError("human review cannot waive failed automatic checks")
        conflict_details: dict[str, Any] = next(
            (row[2] for row in results if str(row[0]) == "conflict_review"), {}
        )
        has_flags = bool(conflict_details.get("flags", []))
        if has_flags and decision == "confirm_no_conflict":
            raise ValueError(
                "potential conflicts or duplicates require an exception, supersession, or rejection"
            )
        if not has_flags and decision == "valid_scoped_exception":
            raise ValueError("a scoped-exception decision requires a flagged related rule")
        row = conn.execute(
            "INSERT INTO curation_human_reviews (revision_id, validation_run_id, fingerprint,"
            " decision, reviewer_label, reason) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (revision.id, run_id, fingerprint, decision, reviewer_label.strip(), reason.strip()),
        ).fetchone()
        if row is None:
            raise RuntimeError("review insert returned no ID")
        state = "blocked" if decision == "reject" else "ready"
        state_reason = (
            "Human reviewer rejected this revision."
            if decision == "reject"
            else "Human source/conflict review recorded; ready for publication authorization."
        )
        conn.execute(
            "UPDATE curation_revision_state SET state = %s, reason = %s,"
            " state_version = state_version + 1, updated_at = now() WHERE revision_id = %s",
            (state, state_reason, revision.id),
        )
        conn.execute(
            "INSERT INTO curation_events (entry_id, revision_id, validation_run_id,"
            " event_type, actor_type, actor_label, reason, payload)"
            " VALUES (%s, %s, %s, 'human_review_recorded', 'admin', %s, %s, %s)",
            (
                revision.entry_id,
                revision.id,
                run_id,
                reviewer_label.strip(),
                reason.strip(),
                Json({"decision": decision, "shared_token_attribution": True}),
            ),
        )
        return int(row[0])


def validation_runs() -> list[dict[str, Any]]:
    """Return complete run/check/review state for the authenticated dashboard."""
    with _connect() as conn:
        runs = conn.execute(
            "SELECT id, revision_id, fingerprint, status, workflow_execution_id,"
            " error_code, candidate_generation, created_at, started_at, completed_at"
            " FROM curation_validation_runs ORDER BY created_at DESC"
        ).fetchall()
        results = conn.execute(
            "SELECT run_id, step, status, details, case_ids FROM curation_validation_results"
            " ORDER BY id"
        ).fetchall()
        reviews = conn.execute(
            "SELECT validation_run_id, id, decision, reviewer_label, reason, reviewed_at"
            " FROM curation_human_reviews ORDER BY id"
        ).fetchall()
    results_by_run: dict[str, list[dict[str, Any]]] = {}
    for row in results:
        results_by_run.setdefault(str(row[0]), []).append(
            {
                "step": str(row[1]),
                "status": str(row[2]),
                "details": row[3],
                "case_ids": row[4],
            }
        )
    reviews_by_run: dict[str, list[dict[str, Any]]] = {}
    for row in reviews:
        reviews_by_run.setdefault(str(row[0]), []).append(
            {
                "id": int(row[1]),
                "decision": str(row[2]),
                "reviewer_label": str(row[3]),
                "reason": str(row[4]),
                "reviewed_at": row[5].isoformat(),
            }
        )
    return [
        {
            "id": str(row[0]),
            "revision_id": int(row[1]),
            "fingerprint": str(row[2]),
            "status": str(row[3]),
            "workflow_execution_id": row[4],
            "error_code": row[5],
            "candidate_generation": row[6],
            "created_at": row[7].isoformat(),
            "started_at": row[8].isoformat() if row[8] else None,
            "completed_at": row[9].isoformat() if row[9] else None,
            "results": results_by_run.get(str(row[0]), []),
            "reviews": reviews_by_run.get(str(row[0]), []),
        }
        for row in runs
    ]
