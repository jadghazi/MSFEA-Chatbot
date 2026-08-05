"""Department scoping: escalation routing, prompt labelling, and API validation.

Retrieval scoping itself is DB-backed and lives in `test_retrieval.py`; these are
the hermetic paths that need no database.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from msfea_bot.api.app import app
from msfea_bot.generation.answer import (
    REFUSAL_MARKER,
    Answer,
    build_prompt,
    escalation,
    parse_answer,
)
from msfea_bot.retrieval.store import RetrievedChunk

CHUNKS = [
    RetrievedChunk(
        id="g.md#01-cee",
        text="Internships may be split into two 4-week periods.",
        source_doc="summer-training-guidelines-2026.md",
        section="Civil and Environmental Engineering (CEE)",
        score=0.9,
    )
]


# --------------------------------------------------------------------------- #
# Escalation routing (B-1)
# --------------------------------------------------------------------------- #


def test_escalation_routes_to_the_department_coordinator() -> None:
    ans = escalation("cee")
    assert ans.refused is True
    assert "hk50@aub.edu.lb" in ans.text
    assert "Hiam Khoury" in ans.text


def test_escalation_without_department_stays_general() -> None:
    ans = escalation(None)
    assert ans.refused is True
    # Must not leak a specific coordinator to a student we can't place.
    assert "hk50@aub.edu.lb" not in ans.text
    assert "ek15@aub.edu.lb" not in ans.text


def test_escalation_ignores_an_unknown_department() -> None:
    """An unrecognised code must not route anywhere or raise."""
    ans = escalation("school-of-wizardry")
    assert ans.refused is True
    assert "@aub.edu.lb" in ans.text  # still gives *a* contact


def test_refusal_marker_still_routes_by_department() -> None:
    """The prompt-refusal path must route too, not just the threshold gate."""
    ans = parse_answer(REFUSAL_MARKER, CHUNKS, "mech")
    assert ans.refused is True
    assert "ek15@aub.edu.lb" in ans.text


# --------------------------------------------------------------------------- #
# Prompt labelling (B-2)
# --------------------------------------------------------------------------- #


def test_prompt_names_the_department_when_known() -> None:
    prompt = build_prompt("Can I split my internship?", CHUNKS, "cee")
    assert "Civil and Environmental Engineering" in prompt
    assert "CEE" in prompt
    assert "Never present another department's rule" in prompt


def test_prompt_omits_the_department_block_when_unknown() -> None:
    prompt = build_prompt("Can I split my internship?", CHUNKS, None)
    assert "Never present another department's rule" not in prompt
    # The rest of the prompt is unchanged.
    assert REFUSAL_MARKER in prompt
    assert "Can I split my internship?" in prompt


def test_prompt_ignores_an_unknown_department() -> None:
    prompt = build_prompt("q", CHUNKS, "not-a-dept")
    assert "Never present another department's rule" not in prompt


# --------------------------------------------------------------------------- #
# API contract
# --------------------------------------------------------------------------- #


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Chat endpoint with generation and logging stubbed (no DB, no LLM)."""
    seen: dict[str, object] = {}

    def fake_generate(question: str, **kwargs: object) -> Answer:
        seen["department"] = kwargs.get("department")
        return Answer(text="ok", citations=["a > b"], refused=False)

    monkeypatch.setattr("msfea_bot.api.app.generate_answer", fake_generate)
    monkeypatch.setattr("msfea_bot.api.app.log_interaction", lambda *a, **k: 1)
    c = TestClient(app)
    c.seen = seen  # type: ignore[attr-defined]
    return c


def test_chat_passes_a_valid_department_through(client: TestClient) -> None:
    r = client.post("/chat", json={"question": "hi", "department": "cee"})
    assert r.status_code == 200
    assert client.seen["department"] == "cee"  # type: ignore[attr-defined]


def test_chat_normalises_case(client: TestClient) -> None:
    r = client.post("/chat", json={"question": "hi", "department": "CEE"})
    assert r.status_code == 200
    assert client.seen["department"] == "cee"  # type: ignore[attr-defined]


def test_chat_drops_an_unknown_department_rather_than_failing(client: TestClient) -> None:
    """Untrusted client input: degrade to unscoped, never 4xx/5xx the student."""
    r = client.post("/chat", json={"question": "hi", "department": "'; DROP TABLE--"})
    assert r.status_code == 200
    assert client.seen["department"] is None  # type: ignore[attr-defined]


def test_chat_without_a_department_is_unchanged(client: TestClient) -> None:
    """Existing embeds that never send the field must keep working."""
    r = client.post("/chat", json={"question": "hi"})
    assert r.status_code == 200
    assert client.seen["department"] is None  # type: ignore[attr-defined]
