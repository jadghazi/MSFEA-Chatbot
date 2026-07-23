/* MSFEA CDC chatbot widget — vanilla JS, no dependencies (CLAUDE.md §3, §5.7).
 * Embed with:  <script src=".../widget.js" data-api-url="https://your-api"></script>
 * The API base can also be set via window.MSFEA_CHAT_API. Defaults to same origin.
 */
(function () {
  "use strict";

  var script = document.currentScript;
  var API = (
    (script && script.getAttribute("data-api-url")) ||
    window.MSFEA_CHAT_API ||
    ""
  ).replace(/\/+$/, "");

  var css =
    ".msfea-bubble{position:fixed;right:20px;bottom:20px;width:56px;height:56px;border-radius:50%;" +
    "background:#6a1b1a;color:#fff;border:none;cursor:pointer;font-size:24px;box-shadow:0 4px 12px rgba(0,0,0,.25);z-index:2147483000}" +
    ".msfea-panel{position:fixed;right:20px;bottom:88px;width:360px;max-width:calc(100vw - 40px);height:520px;max-height:calc(100vh - 120px);" +
    "background:#fff;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.25);display:none;flex-direction:column;overflow:hidden;z-index:2147483000;font-family:system-ui,Arial,sans-serif}" +
    ".msfea-panel.open{display:flex}" +
    ".msfea-head{background:#6a1b1a;color:#fff;padding:12px 14px;font-weight:600}" +
    ".msfea-head small{display:block;font-weight:400;opacity:.85;font-size:11px;margin-top:2px}" +
    ".msfea-msgs{flex:1;overflow-y:auto;padding:12px;background:#f7f7f8}" +
    ".msfea-msg{margin:8px 0;padding:9px 12px;border-radius:12px;max-width:85%;white-space:pre-wrap;line-height:1.4;font-size:14px}" +
    ".msfea-user{background:#6a1b1a;color:#fff;margin-left:auto;border-bottom-right-radius:3px}" +
    ".msfea-bot{background:#fff;color:#1a1a1a;border:1px solid #e3e3e6;border-bottom-left-radius:3px}" +
    ".msfea-cite{font-size:11px;color:#666;margin-top:6px}" +
    ".msfea-cite b{color:#6a1b1a}" +
    ".msfea-disc{font-size:11px;color:#8a8a8a;font-style:italic;margin-top:6px}" +
    ".msfea-foot{display:flex;border-top:1px solid #e3e3e6;padding:8px}" +
    ".msfea-foot input{flex:1;border:1px solid #ccc;border-radius:8px;padding:9px;font-size:14px;outline:none}" +
    ".msfea-foot button{margin-left:6px;background:#6a1b1a;color:#fff;border:none;border-radius:8px;padding:0 14px;cursor:pointer}" +
    ".msfea-foot button:disabled{opacity:.5;cursor:default}";

  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  var bubble = document.createElement("button");
  bubble.className = "msfea-bubble";
  bubble.setAttribute("aria-label", "Open CDC chat");
  bubble.textContent = "💬";

  var panel = document.createElement("div");
  panel.className = "msfea-panel";
  panel.innerHTML =
    '<div class="msfea-head">MSFEA CDC Assistant' +
    "<small>AI-generated · verify with official CDC sources</small></div>" +
    '<div class="msfea-msgs"></div>' +
    '<div class="msfea-foot">' +
    '<input type="text" placeholder="Ask about internships, CO-OP, ..." />' +
    "<button>Send</button></div>";

  document.body.appendChild(bubble);
  document.body.appendChild(panel);

  var msgs = panel.querySelector(".msfea-msgs");
  var input = panel.querySelector("input");
  var sendBtn = panel.querySelector("button");

  function el(cls, text) {
    var d = document.createElement("div");
    d.className = cls;
    if (text !== undefined) d.textContent = text;
    return d;
  }

  function addUser(text) {
    var m = el("msfea-msg msfea-user", text);
    msgs.appendChild(m);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function addBot(data) {
    var wrap = el("msfea-msg msfea-bot");
    wrap.appendChild(el("", data.answer));
    if (data.citations && data.citations.length && !data.refused) {
      var c = el("msfea-cite");
      c.innerHTML = "<b>Sources:</b> " + data.citations.map(escapeHtml).join("; ");
      wrap.appendChild(c);
    }
    if (data.disclaimer) wrap.appendChild(el("msfea-disc", data.disclaimer));
    msgs.appendChild(wrap);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function setBusy(busy) {
    sendBtn.disabled = busy;
    input.disabled = busy;
    sendBtn.textContent = busy ? "…" : "Send";
  }

  function send() {
    var q = input.value.trim();
    if (!q) return;
    addUser(q);
    input.value = "";
    setBusy(true);
    fetch(API + "/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q }),
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        addBot(data);
      })
      .catch(function () {
        addBot({
          answer: "Sorry, I couldn't reach the assistant. Please try again later.",
          refused: true,
          disclaimer: "",
        });
      })
      .finally(function () {
        setBusy(false);
        input.focus();
      });
  }

  bubble.addEventListener("click", function () {
    panel.classList.toggle("open");
    if (panel.classList.contains("open")) input.focus();
  });
  sendBtn.addEventListener("click", send);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") send();
  });
})();
