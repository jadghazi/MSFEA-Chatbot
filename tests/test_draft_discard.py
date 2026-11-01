"""Discard uses workflow state, preserves immutable history and starts fresh."""

import psycopg
import pytest
from fastapi.testclient import TestClient

import msfea_bot.api.app as api
from msfea_bot.config import settings
from msfea_bot.curation.revisions import (
    create_draft, create_successor_draft, discard_draft, list_revisions,
)
from msfea_bot.curation.validation import record_human_review, start_validation
from msfea_bot.curation.workspace import workspace
import test_curation_migrations

isolated_database = test_curation_migrations.isolated_database


@pytest.fixture
def draft_database(isolated_database, monkeypatch):
    from msfea_bot.curation.migrations import migrate

    migrate(isolated_database)
    monkeypatch.setattr(settings, "database_url", isolated_database)
    return isolated_database


def test_discard_preserves_history_and_identical_case_starts_fresh(draft_database):
    payload = test_curation_migrations._payload()
    entry, first = create_draft(payload)
    second = create_successor_draft(entry, test_curation_migrations._payload("A revised answer."))
    discard_draft(second)
    discard_draft(second)  # Retried HTTP requests do not create duplicate events.
    revisions = list_revisions()
    assert {r.state for r in revisions} == {"discarded"}
    assert all(not r.active for r in revisions)
    with psycopg.connect(draft_database) as conn:
        assert conn.execute("SELECT count(*) FROM curation_events WHERE event_type='draft_discarded'").fetchone()[0] == 1
        assert conn.execute("SELECT answer FROM curated_revisions WHERE id=%s", (first,)).fetchone()[0] == payload.answer
        assert conn.execute("SELECT active_revision_id FROM curated_entries WHERE id=%s", (entry,)).fetchone()[0] is None
    with pytest.raises(ValueError, match="discarded"):
        workspace(second)
    with pytest.raises(ValueError, match="cannot be validated"):
        start_validation(second)
    with pytest.raises(ValueError, match="discarded"):
        create_successor_draft(entry, payload)
    new_entry, new_revision = create_draft(payload)
    assert new_entry != entry and new_revision not in {first, second}
    assert next(r for r in list_revisions() if r.id == new_revision).state == "draft"


@pytest.mark.parametrize("state", ["validating", "publishing", "active", "retired"])
def test_discard_rejects_busy_or_published_revision(draft_database, state):
    _, revision = create_draft(test_curation_migrations._payload())
    with psycopg.connect(draft_database) as conn:
        conn.execute("UPDATE curation_revision_state SET state=%s WHERE revision_id=%s", (state, revision))
    with pytest.raises(ValueError):
        discard_draft(revision)
    assert list_revisions()[0].state == state


def test_discard_successor_preserves_published_predecessor(draft_database):
    entry, published = create_draft(test_curation_migrations._payload())
    with psycopg.connect(draft_database) as conn:
        conn.execute("UPDATE curated_entries SET active_revision_id=%s WHERE id=%s", (published, entry))
        conn.execute("UPDATE curation_revision_state SET state='active' WHERE revision_id=%s", (published,))
    successor = create_successor_draft(entry, test_curation_migrations._payload("New draft answer."))
    with pytest.raises(ValueError, match="newer revision"):
        discard_draft(published)
    discard_draft(successor)
    states = {r.id:r for r in list_revisions()}
    assert states[published].active and states[published].state == "active"
    assert states[successor].state == "discarded"
    fresh = create_successor_draft(entry, test_curation_migrations._payload("Another reviewed update."))
    assert next(r for r in list_revisions() if r.id == fresh).predecessor_revision_id == published


@pytest.mark.parametrize("status", ["queued", "running"])
def test_discard_waits_for_workspace_jobs(draft_database, status):
    _, revision = create_draft(test_curation_migrations._payload())
    with psycopg.connect(draft_database) as conn:
        conn.execute("INSERT INTO curation_validation_runs (id,revision_id,fingerprint,status) VALUES ('test-run',%s,'test-fingerprint','passed')", (revision,))
        conn.execute("INSERT INTO curation_workspace_jobs (id,revision_id,run_id,kind,status) VALUES ('test-job',%s,'test-run','preview',%s)", (revision, status))
    with pytest.raises(ValueError, match="previews"):
        discard_draft(revision)
    assert list_revisions()[0].state == "draft"


def test_old_review_cannot_reactivate_discarded_draft(draft_database):
    _, revision = create_draft(test_curation_migrations._payload())
    with psycopg.connect(draft_database) as conn:
        conn.execute("INSERT INTO curation_validation_runs (id,revision_id,fingerprint,status) VALUES ('test-run',%s,'test-fingerprint','passed')", (revision,))
    discard_draft(revision)
    with pytest.raises(ValueError, match="discarded"):
        record_human_review("test-run", "Test reviewer", "confirm_no_conflict", "Old approval")
    assert list_revisions()[0].state == "discarded"


def test_discard_endpoint_requires_admin_and_strict_input(monkeypatch):
    monkeypatch.setattr(settings, "admin_token", "test-only-admin")
    calls = []
    monkeypatch.setattr(api, "discard_draft", calls.append)
    client = TestClient(api.app)
    assert client.post("/admin/api/studio/discard", json={"revision_id":1}).status_code == 401
    headers = {"Authorization":"Bearer test-only-admin"}
    assert client.post("/admin/api/studio/discard", json={"revision_id":1,"model":"extra"}, headers=headers).status_code == 422
    assert client.post("/admin/api/studio/discard", json={"revision_id":1}, headers=headers).status_code == 200
    assert calls == [1]
