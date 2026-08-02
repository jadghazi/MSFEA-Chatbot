/* MSFEA CDC chatbot widget — vanilla JS, no dependencies (CLAUDE.md §3, §5.7).
 * Embed with:  <script src=".../widget.js" data-api-url="https://your-api"></script>
 * The API base can also be set via window.MSFEA_CHAT_API. Defaults to same origin.
 *
 * Thin client by design: it POSTs the question to /chat and renders the answer,
 * its sources and the disclaimer. No answer logic lives here.
 */
(function () {
  "use strict";

  var script = document.currentScript;
  var API = (
    (script && script.getAttribute("data-api-url")) ||
    window.MSFEA_CHAT_API ||
    ""
  ).replace(/\/+$/, "");

  // Must match ChatRequest.question's max_length in the API, so the student is
  // told before the request is rejected rather than after.
  var MAX_CHARS = 2000;

  // Shown on the empty state. Real answerable questions from the KB, so a click
  // always demonstrates a grounded answer with citations.
  var SUGGESTIONS = [
    "What is the minimum internship duration?",
    "What GPA do I need for CO-OP?",
    "What do I submit at the end of my internship?",
    "How do I apply to IAESTE?",
  ];

  var ICON_CHAT =
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
    '<path fill="currentColor" d="M12 3c5 0 9 3.36 9 7.5S17 18 12 18a10.5 10.5 0 0 1-2.4-.28L5 20l.9-3.6A7.9 7.9 0 0 1 3 10.5C3 6.36 7 3 12 3Z"/></svg>';
  var ICON_CLOSE =
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
    '<path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" d="M6 6l12 12M18 6L6 18"/></svg>';
  var ICON_SEND =
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
    '<path fill="currentColor" d="M3.4 20.4 21 12 3.4 3.6 3.4 10l12.6 2-12.6 2z"/></svg>';

  /* Styles are scoped under .msfea-w and reset the properties a host page is
     most likely to inherit onto the widget (font, box-sizing, line-height).
     Written as a template literal rather than "+"-concatenation purely for
     legibility — this is the one long block in the file. */
  var css = `
.msfea-w{
  --m:#862633;          /* AUB maroon (PMS 202) */
  --m-dark:#6e1f2a;
  --m-darker:#571820;
  --ink:#1c1c1e;
  --ink-soft:#5b5f66;
  --ink-faint:#8a9099;
  --line:#e4e6ea;
  --canvas:#f6f7f9;
  --radius:14px;
  --shadow:0 10px 40px rgba(20,10,14,.18), 0 2px 8px rgba(20,10,14,.08);
  --font:"Segoe UI",system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif;
}
.msfea-w *,.msfea-w *::before,.msfea-w *::after{box-sizing:border-box}
.msfea-w button{font-family:inherit}

/* ---------- launcher ---------- */
.msfea-bubble{
  position:fixed;right:24px;bottom:24px;width:60px;height:60px;border-radius:50%;
  background:linear-gradient(145deg,var(--m) 0%,var(--m-darker) 100%);
  color:#fff;border:none;cursor:pointer;padding:0;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 6px 20px rgba(134,38,51,.42);
  z-index:2147483000;font-family:var(--font);
  transition:transform .22s cubic-bezier(.34,1.4,.64,1),box-shadow .22s ease;
}
.msfea-bubble:hover{transform:translateY(-3px) scale(1.04);box-shadow:0 10px 26px rgba(134,38,51,.5)}
.msfea-bubble:active{transform:translateY(-1px) scale(.98)}
.msfea-bubble:focus-visible{outline:3px solid #fff;outline-offset:3px;box-shadow:0 0 0 6px rgba(134,38,51,.45)}
.msfea-bubble svg{width:27px;height:27px;transition:transform .2s ease}
.msfea-bubble .msfea-ic-close{display:none}
.msfea-w.is-open .msfea-bubble .msfea-ic-chat{display:none}
.msfea-w.is-open .msfea-bubble .msfea-ic-close{display:block}

/* ---------- panel ---------- */
.msfea-panel{
  position:fixed;right:24px;bottom:96px;width:392px;max-width:calc(100vw - 32px);
  height:min(620px,calc(100vh - 132px));
  background:#fff;border-radius:var(--radius);box-shadow:var(--shadow);
  display:flex;flex-direction:column;overflow:hidden;z-index:2147483000;
  font-family:var(--font);color:var(--ink);
  opacity:0;visibility:hidden;transform:translateY(14px) scale(.97);
  transition:opacity .2s ease,transform .24s cubic-bezier(.34,1.2,.64,1),visibility .24s;
}
.msfea-w.is-open .msfea-panel{opacity:1;visibility:visible;transform:none}

.msfea-head{
  background:linear-gradient(135deg,var(--m) 0%,var(--m-darker) 100%);
  color:#fff;padding:15px 16px;display:flex;align-items:center;gap:12px;flex:0 0 auto;
}
.msfea-crest{
  width:38px;height:38px;border-radius:9px;flex:0 0 auto;
  background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.25);
  display:flex;align-items:center;justify-content:center;
  font-weight:700;font-size:11px;letter-spacing:.4px;
}
.msfea-titles{min-width:0;flex:1}
.msfea-title{font-size:15px;font-weight:650;letter-spacing:.2px;line-height:1.25}
.msfea-sub{font-size:11.5px;opacity:.82;margin-top:2px;line-height:1.3}
.msfea-x{
  background:transparent;border:none;color:#fff;cursor:pointer;opacity:.85;
  width:30px;height:30px;border-radius:8px;display:flex;align-items:center;justify-content:center;padding:0;
  transition:background .15s ease,opacity .15s ease;
}
.msfea-x:hover{background:rgba(255,255,255,.16);opacity:1}
.msfea-x:focus-visible{outline:2px solid #fff;outline-offset:1px}
.msfea-x svg{width:16px;height:16px}

/* ---------- messages ---------- */
.msfea-msgs{flex:1 1 auto;overflow-y:auto;padding:16px;background:var(--canvas);scroll-behavior:smooth}
.msfea-msgs::-webkit-scrollbar{width:8px}
.msfea-msgs::-webkit-scrollbar-thumb{background:#d2d5da;border-radius:4px}
.msfea-msgs::-webkit-scrollbar-thumb:hover{background:#bcc0c6}

.msfea-row{display:flex;margin-bottom:12px;animation:msfea-in .26s ease both}
.msfea-row.u{justify-content:flex-end}
@keyframes msfea-in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}

.msfea-msg{
  padding:11px 14px;border-radius:15px;max-width:88%;
  white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.52;font-size:14px;
}
.msfea-user{background:var(--m);color:#fff;border-bottom-right-radius:5px;box-shadow:0 1px 3px rgba(134,38,51,.28)}
.msfea-bot{background:#fff;color:var(--ink);border:1px solid var(--line);border-bottom-left-radius:5px;box-shadow:0 1px 2px rgba(16,18,22,.05)}
/* An escalation is "a human should answer this", not an error — amber, not red. */
.msfea-bot.esc{border-left:3px solid #c8892a;background:#fffdf7}

.msfea-cite{margin-top:10px;padding-top:9px;border-top:1px solid var(--line)}
.msfea-cite-h{
  font-size:10px;font-weight:700;letter-spacing:.7px;text-transform:uppercase;
  color:var(--ink-faint);margin-bottom:6px;
}
.msfea-chip{
  display:inline-block;font-size:11.5px;line-height:1.35;
  background:#f4eef0;color:var(--m-dark);border:1px solid #ecdde1;
  border-radius:999px;padding:3px 10px;margin:0 5px 5px 0;
}
.msfea-disc{
  font-size:11px;color:var(--ink-faint);margin-top:9px;
  display:flex;gap:5px;align-items:flex-start;line-height:1.45;
}
.msfea-disc::before{content:"ⓘ";font-style:normal;flex:0 0 auto}

.msfea-rate{margin-top:10px;display:flex;align-items:center;gap:6px}
.msfea-rate button{
  background:#fff;border:1px solid var(--line);border-radius:8px;cursor:pointer;
  font-size:13px;padding:3px 9px;line-height:1.4;transition:all .15s ease;
}
.msfea-rate button:hover{border-color:var(--m);background:#fdf7f8;transform:translateY(-1px)}
.msfea-rate button:focus-visible{outline:2px solid var(--m);outline-offset:1px}
.msfea-thanks{font-size:11.5px;color:#2e7d32;font-weight:550}

/* typing indicator — dots MUST be <span> (see showTyping) */
.msfea-thinking{display:flex;align-items:center;gap:10px;padding:12px 14px}
.msfea-thinking-label{font-size:12.5px;color:var(--ink-soft);font-style:italic}
.msfea-typing{display:flex;gap:4px;align-items:center;flex:0 0 auto}
.msfea-typing span{
  display:block;width:7px;height:7px;border-radius:50%;background:var(--m);opacity:.45;
  animation:msfea-bounce 1.3s infinite ease-in-out both;
}
.msfea-typing span:nth-child(2){animation-delay:.16s}
.msfea-typing span:nth-child(3){animation-delay:.32s}
@keyframes msfea-bounce{0%,72%,100%{transform:translateY(0);opacity:.35}36%{transform:translateY(-5px);opacity:1}}

/* ---------- empty state ---------- */
.msfea-welcome{padding:6px 2px 2px}
.msfea-hi{font-size:14.5px;font-weight:650;margin-bottom:5px}
.msfea-hi-sub{font-size:13px;color:var(--ink-soft);line-height:1.55;margin-bottom:14px}
.msfea-sg-h{
  font-size:10px;font-weight:700;letter-spacing:.7px;text-transform:uppercase;
  color:var(--ink-faint);margin-bottom:8px;
}
.msfea-sg{
  display:block;width:100%;text-align:left;background:#fff;border:1px solid var(--line);
  border-radius:10px;padding:10px 12px;margin-bottom:7px;font-size:13px;color:var(--ink);
  cursor:pointer;line-height:1.45;transition:all .16s ease;
}
.msfea-sg:hover{border-color:var(--m);color:var(--m-dark);background:#fdf8f9;transform:translateX(2px)}
.msfea-sg:focus-visible{outline:2px solid var(--m);outline-offset:1px}

/* ---------- composer ---------- */
.msfea-foot{flex:0 0 auto;border-top:1px solid var(--line);padding:11px 12px;background:#fff}
.msfea-inputwrap{
  display:flex;align-items:flex-end;gap:8px;background:var(--canvas);
  border:1.5px solid var(--line);border-radius:12px;padding:6px 6px 6px 12px;
  transition:border-color .18s ease,box-shadow .18s ease;
}
.msfea-inputwrap:focus-within{border-color:var(--m);box-shadow:0 0 0 3px rgba(134,38,51,.11);background:#fff}
.msfea-foot textarea{
  flex:1;border:none;background:transparent;resize:none;outline:none;
  font-family:inherit;font-size:14px;line-height:1.5;color:var(--ink);
  padding:6px 0;max-height:108px;overflow-y:auto;
}
.msfea-foot textarea::placeholder{color:var(--ink-faint)}
.msfea-send{
  flex:0 0 auto;width:36px;height:36px;border-radius:9px;border:none;cursor:pointer;
  background:var(--m);color:#fff;display:flex;align-items:center;justify-content:center;padding:0;
  transition:background .16s ease,transform .16s ease;
}
.msfea-send svg{width:17px;height:17px}
.msfea-send:hover:not(:disabled){background:var(--m-dark);transform:scale(1.06)}
.msfea-send:focus-visible{outline:2px solid var(--m);outline-offset:2px}
.msfea-send:disabled{background:#c9ccd2;cursor:not-allowed}
.msfea-meta{display:flex;justify-content:space-between;align-items:center;margin-top:7px;padding:0 3px}
.msfea-hint{font-size:10.5px;color:var(--ink-faint)}
.msfea-count{font-size:10.5px;color:var(--ink-faint);visibility:hidden}
.msfea-count.show{visibility:visible}
.msfea-count.over{color:#b3261e;font-weight:650}

/* ---------- mobile: full-height sheet ---------- */
@media (max-width:520px){
  .msfea-panel{
    right:0;left:0;bottom:0;width:100%;max-width:100%;
    height:88vh;border-radius:16px 16px 0 0;
  }
  .msfea-bubble{right:16px;bottom:16px}
  .msfea-w.is-open .msfea-bubble{opacity:0;pointer-events:none}
}

@media (prefers-reduced-motion:reduce){
  .msfea-w *{animation-duration:.01ms !important;transition-duration:.01ms !important}
}
`;

  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  var root = document.createElement("div");
  root.className = "msfea-w";

  var bubble = document.createElement("button");
  bubble.className = "msfea-bubble";
  bubble.type = "button";
  bubble.setAttribute("aria-label", "Open the CDC assistant");
  bubble.setAttribute("aria-expanded", "false");
  bubble.innerHTML =
    '<span class="msfea-ic-chat">' + ICON_CHAT + "</span>" +
    '<span class="msfea-ic-close">' + ICON_CLOSE + "</span>";

  var panel = document.createElement("div");
  panel.className = "msfea-panel";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-label", "MSFEA CDC assistant");
  panel.innerHTML =
    '<div class="msfea-head">' +
      '<div class="msfea-crest" aria-hidden="true">AUB</div>' +
      '<div class="msfea-titles">' +
        '<div class="msfea-title">MSFEA CDC Assistant</div>' +
        '<div class="msfea-sub">Career Development Center · Internships &amp; programs</div>' +
      "</div>" +
      '<button class="msfea-x" type="button" aria-label="Close chat">' + ICON_CLOSE + "</button>" +
    "</div>" +
    '<div class="msfea-msgs" role="log" aria-live="polite" aria-atomic="false"></div>' +
    '<div class="msfea-foot">' +
      '<div class="msfea-inputwrap">' +
        '<textarea rows="1" maxlength="' + MAX_CHARS + '" ' +
          'placeholder="Ask about internships, CO-OP, IAESTE…" ' +
          'aria-label="Type your question"></textarea>' +
        '<button class="msfea-send" type="button" aria-label="Send question">' + ICON_SEND + "</button>" +
      "</div>" +
      '<div class="msfea-meta">' +
        '<span class="msfea-hint">Enter to send · Shift+Enter for a new line</span>' +
        '<span class="msfea-count"></span>' +
      "</div>" +
    "</div>";

  root.appendChild(bubble);
  root.appendChild(panel);
  document.body.appendChild(root);

  var msgs = panel.querySelector(".msfea-msgs");
  var input = panel.querySelector("textarea");
  var sendBtn = panel.querySelector(".msfea-send");
  var closeBtn = panel.querySelector(".msfea-x");
  var counter = panel.querySelector(".msfea-count");

  function el(cls, text) {
    var d = document.createElement("div");
    if (cls) d.className = cls;
    if (text !== undefined) d.textContent = text;
    return d;
  }

  function scrollDown() {
    msgs.scrollTop = msgs.scrollHeight;
  }

  function row(kind, node) {
    var r = el("msfea-row" + (kind === "u" ? " u" : ""));
    r.appendChild(node);
    msgs.appendChild(r);
    scrollDown();
    return r;
  }

  /* ---------- empty state ---------- */

  function showWelcome() {
    var w = el("msfea-welcome");
    w.appendChild(el("msfea-hi", "Hello 👋"));
    w.appendChild(
      el(
        "msfea-hi-sub",
        "I answer questions about MSFEA CDC programs using the official " +
          "documents — internships (Approved Experience), CO-OP, IAESTE, " +
          "full-time job support and mentorship."
      )
    );
    w.appendChild(el("msfea-sg-h", "Try asking"));
    SUGGESTIONS.forEach(function (q) {
      var b = document.createElement("button");
      b.className = "msfea-sg";
      b.type = "button";
      b.textContent = q;
      b.addEventListener("click", function () {
        send(q);
      });
      w.appendChild(b);
    });
    msgs.appendChild(w);
  }

  function clearWelcome() {
    var w = msgs.querySelector(".msfea-welcome");
    if (w) w.remove();
  }

  /* ---------- rendering ---------- */

  function addUser(text) {
    row("u", el("msfea-msg msfea-user", text));
  }

  // "summer-training-guidelines-2026.md > Eligibility" -> "summer training guidelines 2026 › Eligibility"
  function prettyCitation(s) {
    var parts = String(s).split(">");
    var doc = parts[0].trim().replace(/\.md$/i, "").replace(/[-_]/g, " ");
    var rest = parts.slice(1).join(">").trim();
    return rest ? doc + " › " + rest : doc;
  }

  function addBot(data) {
    var wrap = el("msfea-msg msfea-bot" + (data.refused ? " esc" : ""));
    wrap.appendChild(el("", data.answer));

    if (data.citations && data.citations.length && !data.refused) {
      var c = el("msfea-cite");
      c.appendChild(el("msfea-cite-h", "Sources"));
      data.citations.forEach(function (s) {
        var chip = el("msfea-chip", prettyCitation(s));
        chip.title = s; // exact label, for anyone verifying
        c.appendChild(chip);
      });
      wrap.appendChild(c);
    }
    if (data.disclaimer) wrap.appendChild(el("msfea-disc", data.disclaimer));
    if (data.interaction_id) wrap.appendChild(ratingUI(data.interaction_id));
    row("b", wrap);
  }

  function ratingUI(interactionId) {
    var box = el("msfea-rate");
    function vote(value) {
      fetch(API + "/rate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ interaction_id: interactionId, rating: value }),
      }).catch(function () {});
      box.textContent = "";
      box.appendChild(el("msfea-thanks", "Thanks for the feedback!"));
    }
    var up = document.createElement("button");
    up.type = "button";
    up.textContent = "👍";
    up.setAttribute("aria-label", "This answer was helpful");
    up.addEventListener("click", function () { vote(1); });
    var down = document.createElement("button");
    down.type = "button";
    down.textContent = "👎";
    down.setAttribute("aria-label", "This answer was not helpful");
    down.addEventListener("click", function () { vote(-1); });
    box.appendChild(up);
    box.appendChild(down);
    return box;
  }

  var typingRow = null;

  function showTyping() {
    var t = el("msfea-msg msfea-bot msfea-thinking");
    var dots = el("msfea-typing");
    dots.setAttribute("aria-label", "Assistant is looking through the documents");
    // Must be <span>: the dot styles are scoped to `.msfea-typing span`.
    for (var i = 0; i < 3; i++) dots.appendChild(document.createElement("span"));
    t.appendChild(dots);
    t.appendChild(el("msfea-thinking-label", "Searching the CDC documents…"));
    typingRow = row("b", t);
  }

  function hideTyping() {
    if (typingRow) {
      typingRow.remove();
      typingRow = null;
    }
  }

  /* ---------- composer ---------- */

  function autoGrow() {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 108) + "px";
  }

  function updateCount() {
    var n = input.value.length;
    // Only surfaces near the cap, so it informs without nagging.
    counter.textContent = n + " / " + MAX_CHARS;
    counter.classList.toggle("show", n > MAX_CHARS * 0.8);
    counter.classList.toggle("over", n >= MAX_CHARS);
  }

  function setBusy(busy) {
    sendBtn.disabled = busy;
    input.disabled = busy;
  }

  function send(preset) {
    var q = (preset !== undefined ? preset : input.value).trim();
    if (!q || sendBtn.disabled) return;
    clearWelcome();
    addUser(q);
    input.value = "";
    autoGrow();
    updateCount();
    setBusy(true);
    showTyping();

    fetch(API + "/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q }),
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        hideTyping();
        addBot(data);
      })
      .catch(function () {
        hideTyping();
        addBot({
          answer: "Sorry, I couldn't reach the assistant. Please check your connection and try again.",
          refused: true,
          disclaimer: "",
        });
      })
      .finally(function () {
        setBusy(false);
        input.focus();
      });
  }

  /* ---------- open / close ---------- */

  function openPanel() {
    root.classList.add("is-open");
    bubble.setAttribute("aria-expanded", "true");
    bubble.setAttribute("aria-label", "Close the CDC assistant");
    if (!msgs.children.length) showWelcome();
    setTimeout(function () { input.focus(); }, 120);
  }

  function closePanel() {
    root.classList.remove("is-open");
    bubble.setAttribute("aria-expanded", "false");
    bubble.setAttribute("aria-label", "Open the CDC assistant");
    bubble.focus(); // return focus to where it came from
  }

  bubble.addEventListener("click", function () {
    if (root.classList.contains("is-open")) closePanel();
    else openPanel();
  });
  closeBtn.addEventListener("click", closePanel);
  sendBtn.addEventListener("click", function () { send(); });

  input.addEventListener("input", function () {
    autoGrow();
    updateCount();
  });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && root.classList.contains("is-open")) closePanel();
  });
})();
