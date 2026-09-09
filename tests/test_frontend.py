from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pilot_page_mounts_the_standalone_chat() -> None:
    page = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")

    assert 'id="chat-app"' in page
    assert 'data-layout="standalone"' in page
    assert 'data-mount="#chat-app"' in page
    assert "Pilot version" in page
    assert "Jad Ghazi" in page
    assert 'src="/widget/widget.js?v=pilot-standalone-3"' in page
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
    assert 'sessionStorageSafe("clear")' not in client.split("function resetChat()", 1)[1].split(
        "function maybeInvite", 1
    )[0]
    assert "Messages reset when you refresh or close this page" in client
    assert 'body: JSON.stringify({ rating: chosenRating, tags: selectedTags, comment:' in client
    assert "session_identifier" not in client
    assert "View sources (" in client
    assert "navigator.clipboard.writeText(answerText)" in client
    assert 'send(failedQuestion, true)' in client
    assert "vote(-1, null, null);" in client
