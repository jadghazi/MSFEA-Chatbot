from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pilot_page_mounts_the_standalone_chat() -> None:
    page = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")

    assert 'id="chat-app"' in page
    assert 'data-layout="standalone"' in page
    assert 'data-mount="#chat-app"' in page
    assert "Pilot version" in page
    assert "Jad Ghazi" in page
    assert 'src="/widget/widget.js?v=pilot-standalone-1"' in page
    assert 'href="#"' not in page


def test_shared_client_keeps_standalone_and_embedded_modes() -> None:
    client = (ROOT / "widget" / "widget.js").read_text(encoding="utf-8")

    assert 'getAttribute("data-layout") === "standalone"' in client
    assert 'getAttribute("data-mount")' in client
    assert 'root.className = "msfea-w" + (STANDALONE ? " is-standalone" : "")' in client
    assert "if (STANDALONE) openPanel();" in client
    assert ".msfea-w.is-standalone .msfea-bubble{display:none}" in client
