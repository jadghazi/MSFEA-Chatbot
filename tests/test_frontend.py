from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pilot_page_mounts_the_standalone_chat() -> None:
    page = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")

    assert 'id="chat-app"' in page
    assert 'data-layout="standalone"' in page
    assert 'data-mount="#chat-app"' in page
    assert "Pilot version" in page
    assert "Jad Ghazi" in page
    assert 'src="/widget/widget.js?v=pilot-standalone-4"' in page
    assert 'rel="icon"' in page
    assert 'href="#"' not in page


def test_shared_client_keeps_standalone_and_embedded_modes() -> None:
    client = (ROOT / "widget" / "widget.js").read_text(encoding="utf-8")

    assert 'getAttribute("data-layout") === "standalone"' in client
    assert 'getAttribute("data-mount")' in client
    assert 'root.className = "msfea-w" + (STANDALONE ? " is-standalone" : "")' in client
    assert "if (STANDALONE) openPanel();" in client
    assert ".msfea-w.is-standalone .msfea-bubble{display:none}" in client


def test_chat_controls_preserve_temporary_context_contract() -> None:
    client = (ROOT / "widget" / "widget.js").read_text(encoding="utf-8")

    assert "function resetChat()" in client
    assert "conversation = [];" in client
    assert "showWelcome();" in client
    assert "var selectedDepartment = null;" in client
    assert "window.localStorage" not in client
    assert "Messages reset when you refresh or close this page" in client
    assert 'body: JSON.stringify({ rating: chosenRating, tags: selectedTags, comment:' in client
    assert "session_identifier" not in client
    assert "View sources (" in client
    assert "navigator.clipboard.writeText(answerText)" in client
    assert 'send(failedQuestion, true)' in client
    assert "vote(-1, null, null);" in client


def test_admin_dashboard_uses_guarded_drafts_not_immediate_publication() -> None:
    page = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")

    assert 'data-tab="drafts"' in page
    assert "/admin/api/revisions" in page
    assert "/admin/api/curation-options" in page
    assert "/admin/api/validation-runs" in page
    assert "/admin/api/revisions/validate" in page
    assert "/admin/api/revisions/review" in page
    assert "/admin/api/revisions/publish" in page
    assert "/admin/api/curated/retire" in page
    assert "Save draft" in page
    assert "Drafts are never visible to students" in page
    assert "Save replacement draft" in page
    assert "the live answer is unchanged" in page
    assert "No potential conflict was flagged" in page
    assert "Record mandatory review" in page
    assert 'data-tab="create"' in page
    assert "One focused knowledge document" in page
    assert "New CDC knowledge" in page
    assert "Contributor name" in page
    assert "Responsible authority" in page
    assert "This submitted text is the source artifact" in page
    assert "Sample student questions" in page
    assert "This draft needs a correction" in page
    assert "Fix this draft" in page
    assert "Create a corrected revision" in page
    assert "Publish to chatbot" in page
    assert "Short answer phrase to verify" in page
    assert "All departments” is a positive policy claim" in page
    assert "truly applies to all five departments" in page
