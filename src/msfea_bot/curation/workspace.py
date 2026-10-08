"""Private previews and one bounded retrieval repair, using the existing worker."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any
from uuid import uuid4

from psycopg.types.json import Json

from msfea_bot.config import settings
from msfea_bot.curation import assistance
from msfea_bot.curation.assistance import PROMPT_VERSION, _connect, prepare_retrieval, reserve_model_call
from msfea_bot.curation.revisions import DraftPayload, EvidenceReference, _insert_revision
from msfea_bot.curation.validation import get_revision, start_validation, validation_fingerprint, validation_runs
from msfea_bot.generation.answer import generate_answer
from msfea_bot.llm import LLMError, LLMRateLimitError, get_preview_provider
from msfea_bot.llm.base import LLMAdmissionError
from msfea_bot.retrieval.store import indexed_generation


def preview_fingerprint() -> str:
    """Bind saved answers to the student configuration and generation contract."""
    package = Path(__file__).resolve().parents[1]
    profile = {
        "model": settings.llm_model,
        "max_output_tokens": settings.llm_max_output_tokens,
        "thinking_level": settings.llm_gemini_thinking_level,
        "sampling": settings.llm_gemini_use_sampling_params,
        "temperature": settings.llm_temperature if settings.llm_gemini_use_sampling_params else None,
        "seed": settings.llm_seed if settings.llm_gemini_use_sampling_params else None,
        "generation_contract": {
            name: hashlib.sha256((package / name).read_bytes()).hexdigest()
            for name in ("generation/answer.py", "generation/conversation.py", "llm/gemini.py", "llm/__init__.py")
        },
    }
    return hashlib.sha256(json.dumps(profile, sort_keys=True).encode()).hexdigest()


def schedule(conn: Any, run_id: str, revision_id: int, kind: str) -> None:
    """Called in the terminal validation transaction; no candidate ownership gap."""
    review = conn.execute(
        "SELECT report FROM curation_assistance WHERE accepted_revision_id=%s AND prompt_version=%s",
        (revision_id, PROMPT_VERSION),
    ).fetchone()
    if not review:
        return
    if kind == "repair":
        if review[0].get("requires_decision"):
            return
        prior = conn.execute(
            "SELECT 1 FROM curation_workspace_jobs j JOIN curated_revisions r ON r.id=j.revision_id"
            " JOIN curated_revisions proposed ON proposed.id=%s"
            " WHERE j.kind='repair' AND r.entry_id=proposed.entry_id AND r.answer=proposed.answer",
            (revision_id,),
        ).fetchone()
        if prior:
            return
    conn.execute(
        "INSERT INTO curation_workspace_jobs (id, revision_id, run_id, kind) VALUES (%s,%s,%s,%s)"
        " ON CONFLICT (run_id,kind) DO NOTHING", (uuid4().hex, revision_id, run_id, kind),
    )


def workspace(revision_id: int) -> dict[str, Any]:
    revision = get_revision(revision_id)
    if revision is None:
        raise ValueError("This knowledge draft was not found.")
    run = next((run for run in validation_runs() if run["revision_id"] == revision_id), None)
    with _connect() as conn:
        jobs = conn.execute(
            "SELECT id,kind,status,result,error_code FROM curation_workspace_jobs"
            " WHERE revision_id=%s ORDER BY created_at DESC", (revision_id,),
        ).fetchall()
        review = conn.execute("SELECT id,prompt_version FROM curation_assistance WHERE accepted_revision_id=%s", (revision_id,)).fetchone()
    current_profile = preview_fingerprint()
    visible_jobs = []
    for row in jobs:
        job = {"id": row[0], "kind": row[1], "status": row[2], "result": row[3], "error_code": row[4]}
        if job["kind"] == "preview" and job["status"] == "completed" and job["result"].get("profile_fingerprint") != current_profile:
            # Preserve the historical record; only its eligibility changes.
            job.update(status="failed", error_code="preview_profile_changed")
            job["result"] = {**job["result"], "passed": False}
        visible_jobs.append(job)
    return {
        "revision": {**asdict(revision), "created_at": revision.created_at.isoformat()},
        "run": run,
        "assistance": assistance.get_review(str(review[0])) if review else None,
        "review_outdated": bool(review and review[1] != PROMPT_VERSION),
        "jobs": visible_jobs,
        "stale": bool(run and not revision.active and validation_fingerprint(revision) != run["fingerprint"]),
    }


def retry_preview(revision_id: int) -> None:
    state = workspace(revision_id)
    run = state["run"]
    if not run or run["status"] != "passed" or state["stale"]:
        raise ValueError("Run fresh successful checks before previewing this draft.")
    with _connect() as conn:
        row = conn.execute(
            "SELECT id,result,error_code FROM curation_workspace_jobs"
            " WHERE run_id=%s AND kind='preview' AND (status='failed' OR"
            " (status='completed' AND result->>'profile_fingerprint' IS DISTINCT FROM %s)) FOR UPDATE",
            (run["id"], preview_fingerprint()),
        ).fetchone()
        if not row:
            raise ValueError("There is no failed preview to retry.")
        conn.execute(
            "INSERT INTO curation_events (revision_id,event_type,actor_type,reason,payload)"
            " VALUES (%s,'preview_retried','admin','Fresh student answers requested; prior attempt retained.',%s)",
            (revision_id, Json({"job_id": row[0], "result": row[1], "error_code": row[2]})),
        )
        conn.execute(
            "UPDATE curation_workspace_jobs SET status='queued',error_code=NULL,result='{}',completed_at=NULL WHERE id=%s",
            (row[0],),
        )


def _repair(state: dict[str, Any], job_id: str) -> dict[str, Any]:
    revision = get_revision(state["revision"]["id"])
    assert revision is not None
    review = state["assistance"]
    if not review or review["report"]["requires_decision"]:
        raise ValueError("A policy decision cannot be repaired by rewriting search questions.")
    failures = {result["step"]: result["details"] for result in state["run"]["results"] if result["status"] == "failed"}
    questions, coverage = prepare_retrieval(
        review["id"], review["model"], revision.answer,
        [revision.representative_question or revision.question, revision.paraphrase_question or revision.question,
         *([review["intake"]["question"]] if review["intake"]["question"] else []),
         *review["report"].get("prepared_retrieval_questions", [])], failures,
    )
    if not coverage["supported"] or coverage["missing_details"]:
        return {"needs_clarification": coverage["missing_details"], "summary": coverage["explanation"]}
    report = copy.deepcopy(review["report"])
    report["draft"]["retrieval_questions"] = questions
    report["coverage"] = coverage
    payload = DraftPayload(
        question=revision.question, answer=revision.answer, department=revision.department or "all",
        programs=tuple(revision.programs), evidence_refs=tuple(EvidenceReference(**item) for item in revision.evidence_refs),
        representative_question=revision.representative_question or revision.question,
        paraphrase_question=revision.paraphrase_question or revision.question, expected_evidence=revision.expected_evidence or "",
        change_reason=revision.change_reason, linked_feedback_ids=tuple(revision.linked_feedback_ids),
        source_kind=revision.source_kind, document_title=revision.document_title, authority_label=revision.authority_label,
        effective_date=revision.effective_date, supporting_reference=revision.supporting_reference, retrieval_questions=tuple(questions),
    )
    with _connect() as conn:
        conn.execute("SELECT id FROM curated_entries WHERE id=%s FOR UPDATE", (revision.entry_id,))
        latest = conn.execute("SELECT id,revision_number FROM curated_revisions WHERE entry_id=%s ORDER BY revision_number DESC LIMIT 1", (revision.entry_id,)).fetchone()
        if latest[0] != revision.id:
            raise ValueError("Another revision already replaced this working draft.")
        successor = _insert_revision(conn, revision.entry_id, int(latest[1]) + 1, revision.id, payload, revision.created_by)
        if successor == revision.id:
            return {"summary": "Search preparation was unchanged. The failed checks still block publication."}
        new_review = uuid4().hex
        conn.execute(
            "INSERT INTO curation_assistance (id,request_key,intake,status,stage,model,prompt_version,kb_generation,"
            " evidence,report,accepted_revision_id,steps,completed_at)"
            " VALUES (%s,%s,%s,'completed','completed',%s,%s,%s,%s,%s,%s,%s,now())",
            (new_review, new_review, Json(review["intake"]), review["model"], PROMPT_VERSION, review["kb_generation"],
             Json(review["evidence"]), Json(report), successor, Json(review["steps"] + [{"stage": "repairing", "summary": coverage["explanation"]}])),
        )
        conn.execute(
            "INSERT INTO curation_events (revision_id,event_type,actor_type,reason,payload)"
            " VALUES (%s,'retrieval_repaired','worker','Facts and original tests preserved; private successor requires fresh checks.',%s)",
            (successor, Json({"parent_revision_id": revision.id, "job_id": job_id})),
        )
        conn.execute("UPDATE curation_workspace_jobs SET result=%s WHERE id=%s", (Json({"successor_revision_id": successor, "summary": coverage["explanation"]}), job_id))
    return {"successor_revision_id": successor, "run_id": start_validation(successor), "summary": coverage["explanation"]}


def retry_repair(revision_id: int) -> None:
    """Explicitly retry a service failure in the same bounded logical repair job."""
    state = workspace(revision_id)
    run = state["run"]
    if state["stale"] or state["review_outdated"] or not run or run["status"] != "failed":
        raise ValueError("Run fresh checks before retrying search preparation.")
    with _connect() as conn:
        row = conn.execute(
            "UPDATE curation_workspace_jobs SET status='queued',error_code=NULL,completed_at=NULL"
            " WHERE run_id=%s AND kind='repair' AND status='failed'"
            " AND error_code IN ('quota','provider_unavailable','interrupted','service_unavailable','spending_paused')"
            " AND NOT result ? 'successor_revision_id' RETURNING id", (run["id"],),
        ).fetchone()
        if not row:
            raise ValueError("There is no interrupted search correction to retry. Keep the original facts and tests.")


def process_next_workspace_job() -> bool:
    with _connect() as conn:
        conn.execute("UPDATE curation_workspace_jobs SET status='failed',error_code='interrupted' WHERE status='running' AND lease_expires_at < now()")
        conn.execute("SELECT pg_advisory_xact_lock(820261004)")
        row = conn.execute("SELECT id,revision_id,kind FROM curation_workspace_jobs WHERE status='queued' ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1").fetchone()
        if row is None:
            return False
        conn.execute("UPDATE curation_workspace_jobs SET status='running',lease_expires_at=now()+interval '10 minutes' WHERE id=%s", (row[0],))
    error: str | None = None
    result: dict[str, Any] = {}
    try:
        state = workspace(int(row[1]))
        run = state["run"]
        if state["stale"] or not run or indexed_generation(settings.validation_database_url) != run["candidate_generation"]:
            raise ValueError("The private candidate is stale. Run fresh checks.")
        if row[2] == "repair":
            result = _repair(state, str(row[0]))
        else:
            profile = preview_fingerprint()
            revision = state["revision"]
            if run["status"] != "passed":
                raise ValueError("All checks must pass before previews.")
            questions = [revision["representative_question"], revision["paraphrase_question"]]
            original = state["assistance"]["intake"]["question"] if state["assistance"] else ""
            if original:
                questions[0] = original
            previews = []
            for question in dict.fromkeys(questions):
                answer = generate_answer(
                    question, department=None if revision["department"] == "all" else revision["department"],
                    database_url=settings.validation_database_url,
                    provider=get_preview_provider(before_request=lambda: reserve_model_call(str(row[0]), settings.llm_model, preview=True)),
                )
                previews.append({"question": question, **asdict(answer)})
            result = {"previews": previews, "model": settings.llm_model, "profile_fingerprint": profile,
                      "candidate_generation": run["candidate_generation"],
                      "passed": bool(previews) and all(not item["refused"] and item["citations"] for item in previews)}
            if preview_fingerprint() != profile:
                raise ValueError("The student generation profile changed during previews.")
        checked_revision = get_revision(int(row[1]))
        if checked_revision is None or validation_fingerprint(checked_revision) != run["fingerprint"]:
            raise ValueError("The KB changed during this operation.")
    except LLMAdmissionError:
        error = "spending_paused"
    except LLMRateLimitError:
        error = "quota"
    except LLMError:
        error = "provider_unavailable"
    except ValueError:
        error = "stale_or_invalid"
    except Exception:
        error = "service_unavailable"
    with _connect() as conn:
        conn.execute("UPDATE curation_workspace_jobs SET status=%s,result=result || %s::jsonb,error_code=%s,lease_expires_at=NULL,completed_at=now() WHERE id=%s",
                     ("failed" if error else "completed", Json(result), error, row[0]))
    return True
