"""Usage regression metric: expensive pipeline calls, not guessed token savings."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest
from fastapi.testclient import TestClient

import msfea_bot.api.app as api
from msfea_bot.api.abuse import BodyLimitMiddleware, RequestGuard, local_reply
from msfea_bot.api.security import RateLimiter
from msfea_bot.generation.answer import Answer

SESSION = "test-session-0001"


@pytest.fixture(autouse=True)
def isolated_guards(monkeypatch):
    for name, limit, seconds in [
        ("_limiter", 60, 60),
        ("_burst_limiter", 12, 5),
        ("_hour_limiter", 300, 3600),
        ("_session_limiter", 20, 60),
        ("_session_hour_limiter", 80, 3600),
    ]:
        monkeypatch.setattr(api, name, RateLimiter(limit, seconds))
    monkeypatch.setattr(api, "_guard", RequestGuard())
    monkeypatch.setattr(api, "anonymize", lambda text: text)
    monkeypatch.setattr(api, "log_interaction", lambda q, a: 1)


@pytest.mark.parametrize(
    "question",
    [
        "ok",
        "thanks",
        "thank you",
        "ok ok ok ok",
        "thanks thanks thanks",
        " \t\n",
        "\x00",
        "qwertyuiopasdfghjkl",
        "aaaaaaaaaaaaaaaa",
        "abababababababab",
        "yes",
        "no",
        "!!!",
    ],
)
def test_local_messages_never_reach_expensive_work(monkeypatch, question):
    def unexpected(*args, **kwargs):
        pytest.fail("Local input reached expensive work")

    monkeypatch.setattr(api, "generate_answer", unexpected)
    monkeypatch.setattr(api, "anonymize", unexpected)
    client = TestClient(api.app)
    for _ in range(5):
        response = client.post("/chat", json={"question": question})
        assert response.status_code == 200
        assert response.json()["local"]
        assert not response.json()["interaction_id"]


@pytest.mark.parametrize(
    "question",
    [
        "IAESTE?",
        "GPA?",
        "deadline?",
        "why?",
        "CV",
        "CO-OP",
        "ok what about the report?",
        "2026?",
        "Is 8 weeks enough?",
        "شكرا موعد التدريب؟",
    ],
)
def test_short_legitimate_questions_reach_pipeline(monkeypatch, question):
    seen = []
    monkeypatch.setattr(
        api, "generate_answer", lambda q, **kw: seen.append(q) or Answer(text="Grounded answer")
    )
    assert TestClient(api.app).post("/chat", json={"question": question}).status_code == 200
    assert seen == [question]


@pytest.mark.parametrize("question", ["yes", "no"])
def test_clarification_answers_preserved(question):
    assert local_reply(question, has_history=True) is None


@pytest.mark.parametrize(
    "payload",
    [
        {"question": ""},
        {"question": "x" * 2001},
        {"question": "Why?", "history": [{"role": "user", "content": "old"}] * 5},
        {"question": "Why?", "history": [{"role": "user", "content": "x" * 1201}]},
    ],
)
def test_invalid_sizes_never_reach_pipeline(monkeypatch, payload):
    monkeypatch.setattr(api, "generate_answer", lambda *a, **kw: pytest.fail("called"))
    response = TestClient(api.app).post("/chat", json=payload)
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)
    assert "x" * 100 not in response.text


def test_body_limit_includes_unknown_fields(monkeypatch):
    monkeypatch.setattr(api, "generate_answer", lambda *a, **kw: pytest.fail("called"))
    response = TestClient(api.app).post("/chat", json={"question": "Why?", "extra": "x" * 65536})
    assert response.status_code == 413


def test_chunked_body_limit_without_content_length():
    async def scenario():
        messages = iter(
            [
                {"type": "http.request", "body": b"1234", "more_body": True},
                {"type": "http.request", "body": b"5678", "more_body": False},
            ]
        )
        sent = []

        async def receive():
            return next(messages)

        async def send(message):
            sent.append(message)

        async def downstream(*args):
            pytest.fail("Oversized request reached JSON parser")

        await BodyLimitMiddleware(downstream, max_bytes=5)(
            {"type": "http", "method": "POST", "path": "/chat", "headers": []}, receive, send
        )
        assert sent[0]["status"] == 413

    asyncio.run(scenario())


def test_repeated_question_replays_without_logging_or_generation(monkeypatch):
    calls, logs = [], []
    monkeypatch.setattr(
        api, "generate_answer", lambda q, **kw: calls.append(q) or Answer(text="Answer")
    )
    monkeypatch.setattr(api, "log_interaction", lambda *args: logs.append(1) or 42)
    client = TestClient(api.app)
    payload = {"question": "What are the internship requirements?", "session_id": SESSION}
    for _ in range(5):
        response = client.post("/chat", json=payload)
        assert response.json()["interaction_id"] == 42
        # A self-contained repeat still needs no history, matching generation.
        payload["history"] = [
            {"role": "user", "content": payload["question"]},
            {"role": "assistant", "content": "Answer"},
        ]
    assert len(calls) == len(logs) == 1


def test_cache_isolated_by_session_department_and_followup_history(monkeypatch):
    calls = []
    monkeypatch.setattr(
        api, "generate_answer", lambda q, **kw: calls.append(kw) or Answer(text="Answer")
    )
    client = TestClient(api.app)
    payload = {
        "question": "What about it?",
        "session_id": SESSION,
        "history": [{"role": "user", "content": "Internship"}],
    }
    for update in [
        {},
        {"session_id": "test-session-0002"},
        {"history": [{"role": "user", "content": "CO-OP"}]},
        {"department": "ece"},
    ]:
        payload.update(update)
        assert client.post("/chat", json=payload).status_code == 200
    assert len(calls) == 4


def test_concurrent_duplicate_and_new_question_do_not_start_second_generation(monkeypatch):
    started, release = Event(), Event()
    calls = []

    def generate(q, **kw):
        calls.append(q)
        started.set()
        assert release.wait(10)
        return Answer(text="Answer")

    monkeypatch.setattr(api, "generate_answer", generate)
    payload = {"question": "What are the internship requirements?", "session_id": SESSION}
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(lambda: TestClient(api.app).post("/chat", json=payload))
        try:
            assert started.wait(5)
            client = TestClient(api.app)
            assert client.post("/chat", json=payload).status_code == 429
            assert (
                client.post(
                    "/chat", json={**payload, "question": "When is the deadline?"}
                ).status_code
                == 429
            )
        finally:
            release.set()
        assert first.result().status_code == 200
    assert len(calls) == 1
    assert not api._guard.active


def test_session_rotation_does_not_bypass_ip_burst_limit():
    client = TestClient(api.app)
    responses = [
        client.post("/chat", json={"question": "ok", "session_id": f"session-{i:016}"})
        for i in range(13)
    ]
    assert [r.status_code for r in responses] == [200] * 12 + [429]
    assert responses[-1].headers["retry-after"]


@pytest.mark.parametrize("limiter", ["_hour_limiter", "_session_hour_limiter", "_session_limiter"])
def test_each_window_is_enforced(monkeypatch, limiter):
    monkeypatch.setattr(api, limiter, RateLimiter(1, 3600))
    client = TestClient(api.app)
    payload = {"question": "ok", "session_id": SESSION}
    assert client.post("/chat", json=payload).status_code == 200
    assert client.post("/chat", json=payload).status_code == 429


def test_ip_concurrency_caps_rotated_sessions():
    guard = RequestGuard()
    for i in range(4):
        assert guard.begin("ip", f"session-{i}", f"key-{i}") is None
    with pytest.raises(Exception) as exc:
        guard.begin("ip", "new-session", "new-key")
    assert exc.value.status_code == 429
    assert guard.begin("other-ip", "other-session", "other-key") is None


def test_golden_set_not_locally_blocked():
    from eval.loader import load_golden_set

    items = load_golden_set()
    blocked = [item.id for item in items if local_reply(item.question, bool(item.history))]
    assert blocked == []


def test_cache_is_bounded_and_invalidated():
    guard = RequestGuard()
    for i in range(260):
        key = f"key-{i}"
        guard.begin("ip", "session", key)
        guard.finish("ip", "session", key, "response")
    assert len(guard.cache) == 256
    previous = guard.version
    guard.invalidate()
    assert not guard.cache
    assert guard.version != previous


@pytest.mark.parametrize("text", ["x", "a" * 100 + "bc", "abc123" * 20, "jksdfghjklzxcvbnm"])
def test_obvious_noise_has_a_local_response(text):
    assert local_reply(text) is not None


def test_forwarded_header_spoof_does_not_pick_attacker_prefix(monkeypatch):
    from starlette.requests import Request
    from msfea_bot.config import settings

    request = Request(
        {
            "type": "http",
            "client": ("10.0.0.2", 8000),
            "headers": [(b"x-forwarded-for", b"fake, 192.0.2.5")],
        }
    )
    monkeypatch.setattr(settings, "trust_proxy_headers", True)
    assert api._client_key(request) == "192.0.2.5"
    monkeypatch.setattr(settings, "trust_proxy_headers", False)
    assert api._client_key(request) == "10.0.0.2"


def test_failure_replay_expires_and_lock_released(monkeypatch):
    from msfea_bot.llm import LLMServiceError
    import msfea_bot.api.abuse as abuse

    calls = []

    def fail(*args, **kwargs):
        calls.append(1)
        raise LLMServiceError("private provider details")

    monkeypatch.setattr(api, "generate_answer", fail)
    clock = [100.0]
    monkeypatch.setattr(abuse.time, "monotonic", lambda: clock[0])
    client = TestClient(api.app)
    payload = {"question": "Requirements?", "session_id": SESSION}
    for _ in range(2):
        response = client.post("/chat", json=payload)
        assert "private provider" not in response.text
    assert len(calls) == 1
    clock[0] += 31
    assert client.post("/chat", json=payload).status_code == 200
    assert len(calls) == 2
    assert not api._guard.active
