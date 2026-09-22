"""Immutable draft revisions for the guarded publication workflow."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import psycopg
from psycopg.types.json import Json

from msfea_bot import departments
from msfea_bot.config import settings
from msfea_bot.ingestion.chunking import parse_frontmatter


@dataclass(frozen=True)
class EvidenceReference:
    source_doc: str
    locator: str
    excerpt: str


@dataclass(frozen=True)
class DraftPayload:
    question: str
    answer: str
    department: str
    programs: tuple[str, ...]
    evidence_refs: tuple[EvidenceReference, ...]
    representative_question: str
    paraphrase_question: str
    expected_evidence: str
    change_reason: str
    linked_feedback_ids: tuple[int, ...] = ()
    source_kind: str = "official_reference"
    document_title: str = ""
    authority_label: str = ""
    effective_date: str | None = None
    supporting_reference: str = ""


@dataclass(frozen=True)
class Revision:
    id: int
    entry_id: int
    revision_number: int
    predecessor_revision_id: int | None
    question: str
    answer: str
    department: str | None
    programs: list[str]
    evidence_refs: list[dict[str, str]]
    representative_question: str | None
    paraphrase_question: str | None
    expected_evidence: str | None
    change_reason: str
    linked_feedback_ids: list[int]
    provenance_status: str
    content_hash: str
    created_by: str
    created_at: datetime
    source_kind: str
    document_title: str
    authority_label: str
    effective_date: str | None
    supporting_reference: str
    state: str
    state_reason: str
    active: bool
    predecessor_question: str | None = None
    predecessor_answer: str | None = None


def program_registry() -> tuple[str, ...]:
    """Derive program IDs from reviewed normalized document frontmatter."""
    root = Path(__file__).resolve().parents[3] / "kb" / "normalized"
    values: set[str] = set()
    for path in root.glob("*.md"):
        metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        raw = metadata.get("program", "")
        values.update(item.strip().lower() for item in raw.split(",") if item.strip())
    return tuple(sorted(values))


def source_registry() -> tuple[str, ...]:
    """Reviewed normalized source IDs available to draft authors."""
    root = Path(__file__).resolve().parents[3] / "kb" / "normalized"
    return tuple(sorted(path.name for path in root.glob("*.md")))


def validate_payload(payload: DraftPayload) -> DraftPayload:
    if payload.source_kind not in {"official_reference", "admin_authored"}:
        raise ValueError("source kind must be an official reference or admin-authored knowledge")
    allowed_departments = {"all", *(department.code for department in departments.DEPARTMENTS)}
    if payload.department not in allowed_departments:
        raise ValueError("department must be 'all' or a known MSFEA department")
    allowed_programs = set(program_registry())
    if not payload.programs or any(program not in allowed_programs for program in payload.programs):
        raise ValueError("programs must contain reviewed CDC program IDs")
    if len(set(payload.programs)) != len(payload.programs):
        raise ValueError("programs must not contain duplicates")
    if payload.source_kind == "official_reference" and not payload.evidence_refs:
        raise ValueError("an existing-source correction needs at least one source reference")
    if payload.source_kind == "admin_authored" and payload.evidence_refs:
        raise ValueError("admin-authored knowledge must not claim an existing document as its source")
    for evidence in payload.evidence_refs:
        if not all((evidence.source_doc.strip(), evidence.locator.strip(), evidence.excerpt.strip())):
            raise ValueError("every evidence reference needs source, locator, and excerpt")
    required = (
        payload.question,
        payload.answer,
        payload.representative_question,
        payload.paraphrase_question,
        payload.expected_evidence,
        payload.change_reason,
    )
    if any(not value.strip() for value in required):
        raise ValueError("draft text and review fields must not be blank")
    if payload.source_kind == "admin_authored":
        if not payload.document_title.strip():
            raise ValueError("a focused knowledge document title is required")
        if not payload.authority_label.strip():
            raise ValueError("the responsible CDC office or policy owner is required")
        if payload.effective_date:
            try:
                date.fromisoformat(payload.effective_date)
            except ValueError as exc:
                raise ValueError("effective date must be a real ISO date (YYYY-MM-DD)") from exc
    elif any(
        (
            payload.document_title.strip(),
            payload.authority_label.strip(),
            payload.effective_date,
            payload.supporting_reference.strip(),
        )
    ):
        raise ValueError("existing-source corrections must use their declared evidence references")
    if any(item <= 0 for item in payload.linked_feedback_ids):
        raise ValueError("linked feedback IDs must be positive")
    if len(set(payload.linked_feedback_ids)) != len(payload.linked_feedback_ids):
        raise ValueError("linked feedback IDs must not contain duplicates")
    return payload


def _content_hash(payload: DraftPayload) -> str:
    canonical = json.dumps(asdict(payload), sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


def _connect() -> Any:
    return psycopg.connect(settings.database_url, autocommit=False, connect_timeout=5)


def _insert_revision(
    conn: Any,
    entry_id: int,
    revision_number: int,
    predecessor_revision_id: int | None,
    payload: DraftPayload,
    actor: str,
) -> int:
    fingerprint = _content_hash(payload)
    existing = conn.execute(
        "SELECT id FROM curated_revisions WHERE entry_id = %s AND content_hash = %s",
        (entry_id, fingerprint),
    ).fetchone()
    if existing:
        return int(existing[0])
    row = conn.execute(
        "INSERT INTO curated_revisions ("
        " entry_id, revision_number, predecessor_revision_id, question, answer,"
        " department, programs, evidence_refs, representative_question,"
        " paraphrase_question, expected_evidence, change_reason, linked_feedback_ids,"
        " provenance_status, content_hash, created_by, source_kind, document_title,"
        " authority_label, effective_date, supporting_reference)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,"
        " 'submitted', %s, %s, %s, %s, %s, %s, %s) RETURNING id",
        (
            entry_id,
            revision_number,
            predecessor_revision_id,
            payload.question.strip(),
            payload.answer.strip(),
            payload.department,
            Json(list(payload.programs)),
            Json([asdict(reference) for reference in payload.evidence_refs]),
            payload.representative_question.strip(),
            payload.paraphrase_question.strip(),
            payload.expected_evidence.strip(),
            payload.change_reason.strip(),
            Json(list(payload.linked_feedback_ids)),
            fingerprint,
            actor,
            payload.source_kind,
            payload.document_title.strip(),
            payload.authority_label.strip(),
            payload.effective_date or None,
            payload.supporting_reference.strip(),
        ),
    ).fetchone()
    if row is None:
        raise RuntimeError("revision insert returned no ID")
    revision_id = int(row[0])
    conn.execute(
        "INSERT INTO curation_revision_state (revision_id, state, reason)"
        " VALUES (%s, 'draft', 'Awaiting validation.')",
        (revision_id,),
    )
    conn.execute(
        "INSERT INTO curation_events (entry_id, revision_id, event_type, actor_type,"
        " actor_label, reason, payload) VALUES (%s, %s, 'draft_created', 'admin', %s, %s, %s)",
        (
            entry_id,
            revision_id,
            actor,
            payload.change_reason.strip(),
            Json({"revision_number": revision_number}),
        ),
    )
    return revision_id


def create_draft(payload: DraftPayload, actor: str = "admin") -> tuple[int, int]:
    payload = validate_payload(payload)
    with _connect() as conn:
        entry = conn.execute("INSERT INTO curated_entries DEFAULT VALUES RETURNING id").fetchone()
        if entry is None:
            raise RuntimeError("entry insert returned no ID")
        entry_id = int(entry[0])
        revision_id = _insert_revision(conn, entry_id, 1, None, payload, actor)
    return entry_id, revision_id


def create_successor_draft(
    entry_id: int, payload: DraftPayload, actor: str = "admin"
) -> int | None:
    payload = validate_payload(payload)
    with _connect() as conn:
        entry = conn.execute(
            "SELECT id FROM curated_entries WHERE id = %s FOR UPDATE", (entry_id,)
        ).fetchone()
        if entry is None:
            return None
        prior = conn.execute(
            "SELECT id, revision_number FROM curated_revisions"
            " WHERE entry_id = %s ORDER BY revision_number DESC LIMIT 1",
            (entry_id,),
        ).fetchone()
        predecessor = int(prior[0]) if prior else None
        number = int(prior[1]) + 1 if prior else 1
        return _insert_revision(conn, entry_id, number, predecessor, payload, actor)


def list_revisions() -> list[Revision]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT r.id, r.entry_id, r.revision_number, r.predecessor_revision_id,"
            " r.question, r.answer, r.department, r.programs, r.evidence_refs,"
            " r.representative_question, r.paraphrase_question, r.expected_evidence,"
            " r.change_reason, r.linked_feedback_ids, r.provenance_status, r.content_hash,"
            " r.created_by, r.created_at, r.source_kind, r.document_title,"
            " r.authority_label, r.effective_date::text, r.supporting_reference,"
            " s.state, s.reason, e.active_revision_id = r.id, p.question, p.answer"
            " FROM curated_revisions r"
            " JOIN curated_entries e ON e.id = r.entry_id"
            " JOIN curation_revision_state s ON s.revision_id = r.id"
            " LEFT JOIN curated_revisions p ON p.id = r.predecessor_revision_id"
            " ORDER BY r.created_at DESC, r.id DESC"
        ).fetchall()
    return [
        Revision(
            id=int(row[0]),
            entry_id=int(row[1]),
            revision_number=int(row[2]),
            predecessor_revision_id=int(row[3]) if row[3] is not None else None,
            question=str(row[4]),
            answer=str(row[5]),
            department=str(row[6]) if row[6] is not None else None,
            programs=list(row[7]),
            evidence_refs=list(row[8]),
            representative_question=str(row[9]) if row[9] is not None else None,
            paraphrase_question=str(row[10]) if row[10] is not None else None,
            expected_evidence=str(row[11]) if row[11] is not None else None,
            change_reason=str(row[12]),
            linked_feedback_ids=list(row[13]),
            provenance_status=str(row[14]),
            content_hash=str(row[15]),
            created_by=str(row[16]),
            created_at=row[17],
            source_kind=str(row[18]),
            document_title=str(row[19]),
            authority_label=str(row[20]),
            effective_date=str(row[21]) if row[21] is not None else None,
            supporting_reference=str(row[22]),
            state=str(row[23]),
            state_reason=str(row[24]),
            active=bool(row[25]),
            predecessor_question=str(row[26]) if row[26] is not None else None,
            predecessor_answer=str(row[27]) if row[27] is not None else None,
        )
        for row in rows
    ]
