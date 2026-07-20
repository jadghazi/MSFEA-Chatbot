"""Smoke test: the API scaffold stands up and answers the health check."""

from fastapi.testclient import TestClient

from msfea_bot.api.app import app


def test_health_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
