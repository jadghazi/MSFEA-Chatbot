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
  var STANDALONE = Boolean(script && script.getAttribute("data-layout") === "standalone");
  var MOUNT_SELECTOR = script && script.getAttribute("data-mount");

  // Must match ChatRequest.question's max_length in the API, so the student is
  // told before the request is rejected rather than after.
  var MAX_CHARS = 2000;
  var MAX_HISTORY_MESSAGES = 4;
  var MAX_HISTORY_MESSAGE_CHARS = 1200;

  // Same-page, same-widget memory only. This is intentionally a normal variable:
  // closing/reopening the bubble keeps the conversation, while refresh/new tab
  // starts clean. It is never written to localStorage or a server-side session.
  var conversation = [];

  // Kept in the browser, not on the server: the bot stays stateless, and a coarse
  // one-of-five attribute never becomes a stored student profile (CLAUDE.md §7).
  var DEPT_KEY = "msfea_department";

  // Codes MUST match msfea_bot/departments.py. The server re-validates and ignores
  // anything unknown, so a stale copy here degrades to an unscoped answer.
  var DEPARTMENTS = [
    { code: "mech", abbr: "MECH", label: "Mechanical" },
    { code: "ece", abbr: "ECE", label: "Electrical & Computer" },
    { code: "chem", abbr: "CHEM", label: "Chemical" },
    { code: "iem", abbr: "IEM", label: "Industrial & Management" },
    { code: "cee", abbr: "CEE", label: "Civil & Environmental" },
  ];

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
  var ICON_COPY =
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M8 8V5.8A1.8 1.8 0 0 1 9.8 4h8.4A1.8 1.8 0 0 1 20 5.8v8.4a1.8 1.8 0 0 1-1.8 1.8H16M5.8 8h8.4A1.8 1.8 0 0 1 16 9.8v8.4a1.8 1.8 0 0 1-1.8 1.8H5.8A1.8 1.8 0 0 1 4 18.2V9.8A1.8 1.8 0 0 1 5.8 8Z" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>';
  var ICON_UP =
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M7 10v10H4V10h3Zm3 10h7.2a2 2 0 0 0 1.9-1.4l1.7-5.5A2 2 0 0 0 18.9 10H15l.6-3.1A2.5 2.5 0 0 0 13.2 4L9 10v10Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>';
  var ICON_DOWN = ICON_UP.replace('<svg ', '<svg style="transform:rotate(180deg)" ');
  var ICON_RETRY =
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M19 8V4m0 0h-4m4 0-3.2 3.2A7 7 0 1 0 19 13" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';

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
/* Rendered answer structure. white-space is reset to normal inside these, since
   the renderer has already turned newlines into real elements. */
.msfea-p{white-space:normal;margin:0 0 8px}
.msfea-p:last-child{margin-bottom:0}
.msfea-list{white-space:normal;margin:0 0 8px;padding-left:19px}
.msfea-list:last-child{margin-bottom:0}
.msfea-list li{margin-bottom:4px}
.msfea-list li:last-child{margin-bottom:0}
.msfea-bot strong{font-weight:650;color:var(--m-dark)}
.msfea-user{background:var(--m);color:#fff;border-bottom-right-radius:5px;box-shadow:0 1px 3px rgba(134,38,51,.28)}
.msfea-bot{background:#fff;color:var(--ink);border:1px solid var(--line);border-bottom-left-radius:5px;box-shadow:0 1px 2px rgba(16,18,22,.05)}
/* An escalation is "a human should answer this", not an error — amber, not red. */
.msfea-bot.esc{border-left:3px solid #c8892a;background:#fffdf7}
.msfea-bot.err{border-left:3px solid #b3261e;background:#fff8f7}

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

/* links inside an answer (forms, petitions, coordinator emails) */
.msfea-link{
  color:var(--m);font-weight:600;text-decoration:underline;
  text-decoration-color:rgba(134,38,51,.35);text-underline-offset:2px;
  overflow-wrap:anywhere;border-radius:3px;
}
.msfea-link:hover{color:var(--m-dark);text-decoration-color:var(--m-dark);background:#f7ecef}
.msfea-link:focus-visible{outline:2px solid var(--m);outline-offset:2px}

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
.msfea-privacy{font-size:11.5px;color:var(--ink-faint);line-height:1.45;margin:-6px 0 14px}
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

/* ---------- department picker ---------- */
.msfea-dept-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-bottom:9px}
.msfea-dept{
  background:#fff;border:1px solid var(--line);border-radius:10px;padding:11px 10px;
  cursor:pointer;text-align:center;transition:all .16s ease;
}
.msfea-dept:hover{border-color:var(--m);background:#fdf8f9;transform:translateY(-1px)}
.msfea-dept:focus-visible{outline:2px solid var(--m);outline-offset:1px}
.msfea-dept b{display:block;font-size:13px;color:var(--m-dark);font-weight:700;line-height:1.2}
.msfea-dept span{display:block;font-size:10.5px;color:var(--ink-faint);margin-top:3px;line-height:1.25}
.msfea-skip{
  display:block;width:100%;background:none;border:none;cursor:pointer;
  font-size:12px;color:var(--ink-faint);text-decoration:underline;padding:7px;
}
.msfea-skip:hover{color:var(--m-dark)}
/* current department, in the header — clicking it reopens the picker */
.msfea-deptpill{
  background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.3);color:#fff;
  border-radius:999px;padding:2px 9px;font-size:10.5px;font-weight:650;cursor:pointer;
  margin-top:4px;line-height:1.5;transition:background .15s ease;
}
.msfea-deptpill:hover{background:rgba(255,255,255,.3)}
.msfea-deptpill:focus-visible{outline:2px solid #fff;outline-offset:1px}
.msfea-deptpill.hidden{display:none}

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

/* ---------- full-page pilot ----------
   The exact same client can live inside the standalone pilot page or collapse
   back to the floating launcher when it is eventually embedded on aub.edu.lb. */
.msfea-w.is-standalone{
  position:relative;width:100%;height:100%;min-height:inherit;
}
.msfea-w.is-standalone .msfea-bubble{display:none}
.msfea-w.is-standalone .msfea-panel{
  position:relative;inset:auto;width:100%;max-width:none;height:100%;min-height:inherit;
  border:1px solid rgba(86,44,51,.13);border-radius:22px;
  box-shadow:0 18px 46px rgba(58,26,31,.1);
  opacity:1;visibility:visible;transform:none;transition:none;z-index:1;
}
.msfea-w.is-standalone .msfea-head{
  min-height:72px;padding:14px 18px;background:#fff;color:var(--ink);
  border-bottom:1px solid var(--line);
}
.msfea-w.is-standalone .msfea-crest{
  width:42px;height:42px;border:none;border-radius:13px;background:var(--m);color:#fff;
  box-shadow:0 7px 17px rgba(134,38,51,.2);font-family:Georgia,serif;font-size:17px;
}
.msfea-w.is-standalone .msfea-title{font-size:15px;font-weight:720}
.msfea-w.is-standalone .msfea-sub{color:var(--ink-soft);opacity:1;font-size:11px}
.msfea-w.is-standalone .msfea-x{display:none}
.msfea-w.is-standalone .msfea-deptpill{
  background:#f5edef;border-color:#ead9dd;color:var(--m-dark);margin-top:5px;
}
.msfea-w.is-standalone .msfea-deptpill:hover{background:#ecdee1}
.msfea-w.is-standalone .msfea-deptpill:focus-visible{outline-color:var(--m)}
.msfea-w.is-standalone .msfea-msgs{
  padding:22px;background:linear-gradient(180deg,#f9f7f4 0%,#f4f1ed 100%);
}
.msfea-w.is-standalone .msfea-welcome{max-width:590px;margin:0 auto;padding:10px 4px}
.msfea-w.is-standalone .msfea-hi{font-family:Georgia,serif;font-size:24px;font-weight:500;color:var(--m-dark)}
.msfea-w.is-standalone .msfea-hi-sub{font-size:13.5px;line-height:1.65}
.msfea-w.is-standalone .msfea-sg{
  padding:11px 14px;border-color:#e4dcda;background:rgba(255,255,255,.86);
}
.msfea-w.is-standalone .msfea-msg{max-width:min(84%,620px);font-size:14px}
.msfea-w.is-standalone .msfea-foot{padding:13px 16px 14px}
.msfea-w.is-standalone .msfea-inputwrap{border-radius:14px;padding:7px 7px 7px 14px}
.msfea-w.is-standalone .msfea-send{width:40px;height:40px;border-radius:11px}

@media (max-width:600px){
  .msfea-w.is-standalone .msfea-panel{
    position:relative;inset:auto;width:100%;height:100%;min-height:inherit;
    border-width:0;border-radius:0;box-shadow:none;
  }
  .msfea-w.is-standalone .msfea-head{min-height:68px;padding:12px 15px}
  .msfea-w.is-standalone .msfea-msgs{padding:16px 14px}
  .msfea-w.is-standalone .msfea-msg{max-width:92%}
  .msfea-w.is-standalone .msfea-foot{padding:10px 11px 12px}
  .msfea-w.is-standalone .msfea-hint{display:none}
}

/* ---------- restrained service UI additions ---------- */
.msfea-head{background:var(--m);padding:13px 15px;gap:10px}
.msfea-crest{border-radius:3px;background:#fff;color:var(--m);border:0;box-shadow:none}
.msfea-head-actions{display:flex;align-items:center;gap:4px}
.msfea-head-btn{min-height:36px;padding:7px 9px;border:0;border-radius:5px;background:transparent;color:inherit;cursor:pointer;font-size:12px;font-weight:650}
.msfea-head-btn:hover{background:rgba(255,255,255,.14)}
.msfea-head-btn:focus-visible,.msfea-action:focus-visible,.msfea-icon-btn:focus-visible,.msfea-rate button:focus-visible,.msfea-reason:focus-visible{outline:2px solid var(--m);outline-offset:2px}
.msfea-deptpill{display:block;background:transparent;border:0;padding:0;color:inherit;text-align:left;border-radius:2px;font-weight:500;text-decoration:underline;text-underline-offset:2px}
.msfea-notice{padding:8px 14px;border-bottom:1px solid var(--line);background:#faf8f6;color:var(--ink-soft);font-size:11px;line-height:1.45}
.msfea-notice strong{color:var(--ink);font-weight:650}
.msfea-msgs{background:#f5f4f2}
.msfea-msg{border-radius:8px;box-shadow:none}
.msfea-user{border-bottom-right-radius:2px;box-shadow:none}
.msfea-bot{border-bottom-left-radius:2px}
.msfea-bot.err{background:#fff7f6;border-color:#efcfcc;border-left:3px solid #a72d25}
.msfea-bot.esc{background:#fffbf2;border-color:#ead9b8;border-left:3px solid #a66b16}
.msfea-answer-tools{display:flex;align-items:center;gap:6px;margin-top:10px;padding-top:8px;border-top:1px solid var(--line)}
.msfea-icon-btn,.msfea-action{display:inline-flex;align-items:center;justify-content:center;gap:6px;min-height:34px;border:1px solid var(--line);border-radius:5px;background:#fff;color:var(--ink-soft);padding:6px 9px;cursor:pointer;font-size:11.5px;font-weight:600}
.msfea-icon-btn:hover,.msfea-action:hover{border-color:#c8a7ad;color:var(--m);background:#fdf9f9}
.msfea-icon-btn svg,.msfea-action svg,.msfea-rate svg{width:16px;height:16px}
.msfea-copy-status{color:#236b3a;font-size:11px;font-weight:650}
.msfea-cite{margin-top:9px;padding-top:0;border-top:0}
.msfea-cite summary{display:inline-flex;align-items:center;min-height:34px;color:var(--m);font-size:11.5px;font-weight:650;cursor:pointer;border-radius:3px}
.msfea-cite summary:focus-visible{outline:2px solid var(--m);outline-offset:2px}
.msfea-source-list{margin:7px 0 0;padding:8px 10px 8px 25px;border-left:2px solid #d9c4c8;background:#faf8f8;color:var(--ink-soft);font-size:11.5px;overflow-wrap:anywhere}
.msfea-source-list li+li{margin-top:5px}
.msfea-source-list a{color:var(--m);overflow-wrap:anywhere}
.msfea-disc{padding:8px 10px;background:#f7f7f7;border-radius:4px}
.msfea-disc::before{content:"i";display:grid;place-items:center;width:15px;height:15px;border:1px solid currentColor;border-radius:50%;font-size:9px;font-weight:700}
.msfea-rate{align-items:flex-start;flex-wrap:wrap}
.msfea-rate-label{font-size:11.5px;color:var(--ink-soft);line-height:34px}
.msfea-rate button{display:grid;place-items:center;width:34px;height:34px;padding:0;border-radius:5px;font-size:0}
.msfea-reasons{width:100%;padding-top:5px;display:flex;flex-wrap:wrap;gap:5px}
.msfea-reason{min-height:32px!important;width:auto!important;padding:5px 8px!important;font-size:11px!important}
.msfea-retry{margin-top:10px}
.msfea-experience-bar{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:7px 14px;border-top:1px solid var(--line);background:#fff;color:var(--ink-soft);font-size:11px}
.msfea-exp-link{border:0;background:none;color:var(--m);text-decoration:underline;text-underline-offset:2px;cursor:pointer;font-size:11.5px;padding:6px 2px}
.msfea-invite{background:#faf5f6;border-bottom:1px solid #eadadd;padding:9px 14px;display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:11.5px;color:var(--ink-soft)}
.msfea-invite[hidden]{display:none}
.msfea-invite button{white-space:nowrap}
.msfea-modal-backdrop{position:fixed;inset:0;z-index:2147483640;background:rgba(25,18,20,.48);display:grid;place-items:center;padding:18px}
.msfea-modal{width:min(440px,100%);max-height:min(680px,calc(100dvh - 36px));overflow:auto;background:#fff;border-radius:8px;box-shadow:0 18px 54px rgba(20,10,14,.25);padding:22px;color:var(--ink);font-family:var(--font)}
.msfea-modal-head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}
.msfea-modal h2{font:600 21px/1.25 Georgia,serif;margin:0;color:var(--m-dark)}
.msfea-modal p{font-size:12.5px;color:var(--ink-soft);line-height:1.55;margin:7px 0 16px}
.msfea-modal-close{width:36px;height:36px;border:0;background:#f3f3f3;border-radius:4px;cursor:pointer;color:var(--ink)}
.msfea-modal-close svg{width:16px;height:16px}
.msfea-fieldset{border:0;padding:0;margin:0 0 17px}
.msfea-fieldset legend,.msfea-comment-label{font-size:12px;font-weight:700;margin-bottom:8px;color:var(--ink)}
.msfea-stars{display:flex;gap:6px}
.msfea-star{width:43px;height:43px;border:1px solid var(--line);border-radius:5px;background:#fff;color:var(--m);font-size:16px;font-weight:700;cursor:pointer}
.msfea-star[aria-checked="true"]{background:var(--m);color:#fff;border-color:var(--m)}
.msfea-tags{display:flex;flex-wrap:wrap;gap:7px}
.msfea-tag{position:relative}
.msfea-tag input{position:absolute;opacity:0;pointer-events:none}
.msfea-tag span{display:block;border:1px solid var(--line);border-radius:5px;padding:7px 9px;font-size:11.5px;cursor:pointer}
.msfea-tag input:checked+span{border-color:var(--m);background:#f8edef;color:var(--m-dark)}
.msfea-tag input:focus-visible+span{outline:2px solid var(--m);outline-offset:2px}
.msfea-modal textarea{width:100%;min-height:92px;resize:vertical;border:1px solid var(--line);border-radius:5px;padding:9px;font:13px/1.45 var(--font)}
.msfea-modal textarea:focus{outline:2px solid var(--m);outline-offset:1px}
.msfea-modal-meta{display:flex;justify-content:space-between;font-size:10.5px;color:var(--ink-faint);margin:4px 0 15px}
.msfea-modal-actions{display:flex;align-items:center;gap:10px}
.msfea-submit{min-height:40px;border:0;border-radius:5px;background:var(--m);color:#fff;padding:9px 15px;font-weight:650;cursor:pointer}
.msfea-submit:disabled{opacity:.55;cursor:not-allowed}
.msfea-form-status{font-size:11.5px;color:#a72d25}
.msfea-success{text-align:center;padding:24px 6px}
.msfea-success h2{margin-bottom:8px}
.msfea-w.is-standalone .msfea-panel{border-radius:8px;box-shadow:0 6px 24px rgba(58,26,31,.08)}
.msfea-w.is-standalone .msfea-head{background:#fff;padding:12px 16px}
.msfea-w.is-standalone .msfea-crest{border-radius:3px;background:var(--m);box-shadow:none}
.msfea-w.is-standalone .msfea-head-btn:hover{background:#f4ecee}
.msfea-w.is-standalone .msfea-deptpill{color:var(--m-dark)}
@media(max-width:600px){
  .msfea-panel,.msfea-w.is-standalone .msfea-panel{height:100dvh;min-height:0}
  .msfea-w.is-standalone{height:100dvh;min-height:0}
  .msfea-head{padding:10px 11px}
  .msfea-title{font-size:14px}
  .msfea-sub{display:none}
  .msfea-head-btn{min-width:44px;min-height:44px;padding:5px}
  .msfea-notice{padding:7px 11px}
  .msfea-msgs{padding:13px 11px}
  .msfea-foot{padding:9px 10px max(9px,env(safe-area-inset-bottom))}
  .msfea-inputwrap{padding-left:10px}
  .msfea-send{width:44px;height:44px}
  .msfea-experience-bar{padding:4px 11px}
}
`;

  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  var root = document.createElement("div");
  root.className = "msfea-w" + (STANDALONE ? " is-standalone" : "");

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
  panel.setAttribute("role", STANDALONE ? "region" : "dialog");
  panel.setAttribute("aria-label", "MSFEA CDC assistant");
  panel.innerHTML =
    '<div class="msfea-head">' +
      '<div class="msfea-crest" aria-hidden="true">M</div>' +
      '<div class="msfea-titles">' +
        '<div class="msfea-title">MSFEA Student Assistant</div>' +
        '<div class="msfea-sub">Source-grounded internship &amp; CDC guidance</div>' +
        '<button class="msfea-deptpill hidden" type="button"></button>' +
      "</div>" +
      '<div class="msfea-head-actions">' +
        '<button class="msfea-head-btn msfea-new" type="button">New chat</button>' +
        '<button class="msfea-x" type="button" aria-label="Close chat">' + ICON_CLOSE + "</button>" +
      "</div>" +
    "</div>" +
    '<div class="msfea-notice"><strong>Temporary chat.</strong> Messages reset when you refresh or close this page. Do not enter your name, student ID, phone number, or personal email.</div>' +
    '<div class="msfea-invite" hidden><span>Three answers in — would you rate this experience?</span><button class="msfea-exp-link msfea-invite-open" type="button">Rate now</button><button class="msfea-head-btn msfea-invite-close" type="button" aria-label="Dismiss rating invitation">Dismiss</button></div>' +
    '<div class="msfea-msgs" role="log" aria-live="polite" aria-atomic="false"></div>' +
    '<div class="msfea-experience-bar"><span>Anonymous feedback helps improve this pilot.</span><button class="msfea-exp-link msfea-exp-open" type="button">Rate your experience</button></div>' +
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
  var mount = null;
  if (MOUNT_SELECTOR) {
    try {
      mount = document.querySelector(MOUNT_SELECTOR);
    } catch (e) {
      mount = null;
    }
  }
  (mount || document.body).appendChild(root);

  var msgs = panel.querySelector(".msfea-msgs");
  var input = panel.querySelector("textarea");
  var sendBtn = panel.querySelector(".msfea-send");
  var closeBtn = panel.querySelector(".msfea-x");
  var newBtn = panel.querySelector(".msfea-new");
  var counter = panel.querySelector(".msfea-count");
  var completedAnswers = 0;
  var inviteHandled = false;

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

  /* ---------- department ---------- */

  function getDept() {
    try {
      return sessionStorageSafe("get");
    } catch (e) {
      return null;
    }
  }

  // localStorage can throw in private mode / blocked third-party contexts, and the
  // widget is embedded on a page we don't control — so every access is guarded.
  function sessionStorageSafe(op, value) {
    try {
      if (op === "get") return window.localStorage.getItem(DEPT_KEY);
      if (op === "set") window.localStorage.setItem(DEPT_KEY, value);
      if (op === "clear") window.localStorage.removeItem(DEPT_KEY);
    } catch (e) {
      /* storage unavailable — the widget still works, just without memory */
    }
    return null;
  }

  function deptLabel(code) {
    for (var i = 0; i < DEPARTMENTS.length; i++) {
      if (DEPARTMENTS[i].code === code) return DEPARTMENTS[i].abbr;
    }
    return null;
  }

  function refreshDeptPill() {
    var pill = panel.querySelector(".msfea-deptpill");
    var abbr = deptLabel(getDept());
    if (abbr) {
      pill.textContent = "Department: " + abbr + " · Change";
      pill.setAttribute("aria-label", "Your department is " + abbr + ". Change it.");
      pill.classList.remove("hidden");
    } else {
      pill.classList.add("hidden");
    }
  }

  function setDept(code) {
    if (code) sessionStorageSafe("set", code);
    else sessionStorageSafe("clear");
    refreshDeptPill();
  }

  function showDepartmentPicker() {
    msgs.innerHTML = "";
    // The visible chat is reset when the student changes department; its hidden
    // retrieval context must reset at the same time.
    conversation = [];
    var w = el("msfea-welcome");
    w.appendChild(el("msfea-hi", "Welcome"));
    w.appendChild(
      el(
        "msfea-hi-sub",
        "Some internship rules differ by department, so tell me which one you're " +
          "in and I'll give you the rules that actually apply to you — and the right " +
          "person to contact if I can't help."
      )
    );
    w.appendChild(el("msfea-sg-h", "Your department"));
    var grid = el("msfea-dept-grid");
    DEPARTMENTS.forEach(function (d) {
      var b = document.createElement("button");
      b.className = "msfea-dept";
      b.type = "button";
      b.innerHTML = "<b>" + d.abbr + "</b><span>" + d.label + "</span>";
      b.addEventListener("click", function () {
        setDept(d.code);
        msgs.innerHTML = "";
        showWelcome();
      });
      grid.appendChild(b);
    });
    w.appendChild(grid);
    var skip = document.createElement("button");
    skip.className = "msfea-skip";
    skip.type = "button";
    skip.textContent = "Skip — I'm not sure / other";
    skip.addEventListener("click", function () {
      // Recorded as an explicit choice so we don't ask again every visit.
      setDept("skipped");
      msgs.innerHTML = "";
      showWelcome();
    });
    w.appendChild(skip);
    msgs.appendChild(w);
  }

  /* ---------- empty state ---------- */

  function showWelcome() {
    var w = el("msfea-welcome");
    w.appendChild(el("msfea-hi", "How can I help?"));
    w.appendChild(
      el(
        "msfea-hi-sub",
        "I answer questions about MSFEA CDC programs using the official " +
          "documents — internships (Approved Experience), CO-OP, IAESTE, " +
          "full-time job support and mentorship."
      )
    );
    w.appendChild(
      el(
        "msfea-privacy",
        "This conversation is temporary. Please don't include your name, student ID, phone number, or personal email."
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

  // A URL (http/https only) or a bare email address.
  var LINK_RE = /(https?:\/\/[^\s<>"']+)|([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})/g;

  function shortenUrl(u) {
    var s = u.replace(/^https?:\/\//i, "").replace(/\/$/, "");
    // Office Forms links run to 200+ chars and would wreck the layout. The full URL
    // stays in href and title, so nothing is hidden from the student.
    return s.length > 46 ? s.slice(0, 43) + "…" : s;
  }

  /* Turn URLs and emails in the model's answer into real links.
   *
   * Built from DOM nodes, never innerHTML: the answer is model output derived from
   * retrieved documents, so it is not trusted markup. Text goes through
   * createTextNode and only the href of a scheme-checked link is ever set, which
   * makes injection impossible rather than merely escaped. */
  function linkify(text) {
    var frag = document.createDocumentFragment();
    var last = 0;
    var m;
    LINK_RE.lastIndex = 0;
    while ((m = LINK_RE.exec(text)) !== null) {
      var raw = m[0];
      var isEmail = !m[1];
      var href = raw;
      var trail = "";
      if (!isEmail) {
        // Don't swallow sentence punctuation into the link.
        while (/[.,;:!?)\]]$/.test(href)) {
          trail = href.slice(-1) + trail;
          href = href.slice(0, -1);
        }
      }
      // Defence in depth: the regex already excludes other schemes, but never set
      // href from model output without confirming the scheme.
      var safe = isEmail || /^https?:\/\//i.test(href);
      if (m.index > last) {
        frag.appendChild(document.createTextNode(text.slice(last, m.index)));
      }
      if (safe) {
        var a = document.createElement("a");
        a.className = "msfea-link";
        a.href = isEmail ? "mailto:" + href : href;
        a.textContent = isEmail ? href : shortenUrl(href);
        a.title = href;
        if (!isEmail) {
          a.target = "_blank";
          a.rel = "noopener noreferrer";
        }
        frag.appendChild(a);
      } else {
        frag.appendChild(document.createTextNode(href));
      }
      if (trail) frag.appendChild(document.createTextNode(trail));
      last = m.index + m[0].length;
    }
    if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
    return frag;
  }

  // "summer-training-guidelines-2026.md > Eligibility" -> "summer training guidelines 2026 › Eligibility"
  function prettyCitation(s) {
    var parts = String(s).split(">");
    var doc = parts[0].trim().replace(/\.md$/i, "").replace(/[-_]/g, " ");
    var rest = parts.slice(1).join(">").trim();
    return rest ? doc + " › " + rest : doc;
  }

  function citationItem(citation) {
    var li = document.createElement("li");
    var value = String(citation);
    var url = value.match(/https?:\/\/[^\s<>"']+/i);
    if (!url) {
      li.textContent = value;
      li.title = value;
      return li;
    }
    var before = value.slice(0, url.index).trim();
    if (before) li.appendChild(document.createTextNode(before + " "));
    var href = url[0].replace(/[.,;:!?)\]]+$/, "");
    var a = document.createElement("a");
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.textContent = href;
    a.title = href;
    li.appendChild(a);
    return li;
  }

  /* Minimal markdown -> DOM. Deliberately NOT a markdown parser: only the few
   * things the model actually emits (bold, bullet lists, numbered lists), each
   * built as real elements. Same safety rule as linkify — no innerHTML anywhere,
   * so nothing in the model's output can become markup we didn't choose. */
  function inline(text) {
    var frag = document.createDocumentFragment();
    var re = /\*\*([^*]+)\*\*/g;
    var last = 0;
    var m;
    while ((m = re.exec(text)) !== null) {
      if (m.index > last) frag.appendChild(linkify(text.slice(last, m.index)));
      var b = document.createElement("strong");
      b.appendChild(linkify(m[1]));
      frag.appendChild(b);
      last = m.index + m[0].length;
    }
    if (last < text.length) frag.appendChild(linkify(text.slice(last)));
    return frag;
  }

  function renderAnswer(text) {
    var frag = document.createDocumentFragment();
    var lines = String(text).split("\n");
    var list = null; // the <ul>/<ol> currently being filled
    var para = [];   // buffered non-list lines

    function flushPara() {
      if (!para.length) return;
      var p = el("msfea-p");
      p.appendChild(inline(para.join("\n")));
      frag.appendChild(p);
      para = [];
    }
    function flushList() {
      if (list) { frag.appendChild(list); list = null; }
    }

    lines.forEach(function (raw) {
      var bullet = raw.match(/^\s*[-*]\s+(.*)$/);
      var numbered = raw.match(/^\s*\d+[.)]\s+(.*)$/);
      var item = bullet || numbered;
      if (item) {
        flushPara();
        var tag = numbered ? "OL" : "UL";
        if (!list || list.tagName !== tag) {
          flushList();
          list = document.createElement(numbered ? "ol" : "ul");
          list.className = "msfea-list";
        }
        var li = document.createElement("li");
        li.appendChild(inline(item[1]));
        list.appendChild(li);
      } else if (!raw.trim()) {
        flushList();
        flushPara();
      } else {
        flushList();
        para.push(raw);
      }
    });
    flushList();
    flushPara();
    return frag;
  }

  function addBot(data, failedQuestion) {
    var stateClass = data.error_code ? " err" : (data.refused ? " esc" : "");
    var wrap = el("msfea-msg msfea-bot" + stateClass);
    var bodyEl = el("");
    bodyEl.appendChild(renderAnswer(data.answer || ""));
    wrap.appendChild(bodyEl);

    if (data.citations && data.citations.length && !data.refused) {
      var c = document.createElement("details");
      c.className = "msfea-cite";
      var summary = document.createElement("summary");
      summary.textContent = "View sources (" + data.citations.length + ")";
      c.appendChild(summary);
      var sourceList = document.createElement("ol");
      sourceList.className = "msfea-source-list";
      data.citations.forEach(function (s) {
        sourceList.appendChild(citationItem(s));
      });
      c.appendChild(sourceList);
      wrap.appendChild(c);
    }
    if (data.disclaimer) wrap.appendChild(el("msfea-disc", data.disclaimer));
    if (!data.refused && !data.error_code && data.answer) {
      var tools = el("msfea-answer-tools");
      var copy = document.createElement("button");
      copy.className = "msfea-icon-btn";
      copy.type = "button";
      copy.innerHTML = ICON_COPY + "<span>Copy answer</span>";
      copy.setAttribute("aria-label", "Copy answer text");
      var copyStatus = el("msfea-copy-status");
      copy.addEventListener("click", function () {
        var answerText = String(data.answer || "");
        var copied = navigator.clipboard && navigator.clipboard.writeText
          ? navigator.clipboard.writeText(answerText)
          : Promise.reject(new Error("Clipboard unavailable"));
        copied.then(function () {
          copyStatus.textContent = "Copied";
          setTimeout(function () { copyStatus.textContent = ""; }, 1800);
        }).catch(function () {
          copyStatus.textContent = "Could not copy. Select the answer text instead.";
        });
      });
      tools.appendChild(copy);
      tools.appendChild(copyStatus);
      wrap.appendChild(tools);
    }
    if (data.error_code && failedQuestion) {
      var retry = document.createElement("button");
      retry.className = "msfea-action msfea-retry";
      retry.type = "button";
      retry.innerHTML = ICON_RETRY + "<span>Try again</span>";
      retry.addEventListener("click", function () {
        retry.disabled = true;
        send(failedQuestion, true);
      });
      wrap.appendChild(retry);
    }
    if (data.interaction_id && !data.error_code) wrap.appendChild(ratingUI(data.interaction_id));
    row("b", wrap);
  }

  function ratingUI(interactionId) {
    var box = el("msfea-rate");
    box.appendChild(el("msfea-rate-label", "Was this helpful?"));
    function finish() {
      box.textContent = "";
      box.appendChild(el("msfea-thanks", "Thanks for the feedback."));
    }
    function vote(value, reason, onSuccess) {
      return fetch(API + "/rate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ interaction_id: interactionId, rating: value, reason: reason || null }),
      }).then(function (r) {
        if (!r.ok) throw new Error("feedback failed");
        if (onSuccess) onSuccess();
      }).catch(function () {
        var status = box.querySelector(".msfea-thanks");
        if (!status) { status = el("msfea-thanks"); box.appendChild(status); }
        status.textContent = "Feedback could not be saved. Please try again.";
      });
    }
    var up = document.createElement("button");
    up.type = "button";
    up.innerHTML = ICON_UP;
    up.setAttribute("aria-label", "This answer was helpful");
    up.addEventListener("click", function () { vote(1, null, finish); });
    var down = document.createElement("button");
    down.type = "button";
    down.innerHTML = ICON_DOWN;
    down.setAttribute("aria-label", "This answer was not helpful");
    down.setAttribute("aria-expanded", "false");
    down.addEventListener("click", function () {
      if (box.querySelector(".msfea-reasons")) return;
      vote(-1, null, null);
      down.setAttribute("aria-expanded", "true");
      var reasons = el("msfea-reasons");
      reasons.appendChild(el("msfea-rate-label", "What was the issue? (optional)"));
      ["Incorrect", "Unclear", "Missing information", "Wrong department"].forEach(function (reason) {
        var b = document.createElement("button");
        b.className = "msfea-reason";
        b.type = "button";
        b.textContent = reason;
        b.addEventListener("click", function () { vote(-1, reason, finish); });
        reasons.appendChild(b);
      });
      var skip = document.createElement("button");
      skip.className = "msfea-reason";
      skip.type = "button";
      skip.textContent = "Skip";
      skip.addEventListener("click", finish);
      reasons.appendChild(skip);
      box.appendChild(reasons);
      reasons.querySelector("button").focus();
    });
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

  function resetChat() {
    if (sendBtn.disabled) return;
    if (msgs.querySelector(".msfea-row") && !window.confirm("Start a new chat? The current messages will be cleared.")) return;
    conversation = [];
    completedAnswers = 0;
    msgs.textContent = "";
    if (getDept()) showWelcome();
    else showDepartmentPicker();
    input.value = "";
    autoGrow();
    updateCount();
    input.focus();
  }

  function maybeInvite() {
    if (completedAnswers < 3 || inviteHandled) return;
    var invite = panel.querySelector(".msfea-invite");
    invite.hidden = false;
  }

  function openExperienceModal() {
    inviteHandled = true;
    panel.querySelector(".msfea-invite").hidden = true;
    var backdrop = el("msfea-modal-backdrop");
    var modal = document.createElement("section");
    modal.className = "msfea-modal";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "msfea-exp-title");
    modal.innerHTML =
      '<div class="msfea-modal-head"><div><h2 id="msfea-exp-title">Rate your experience</h2>' +
      '<p>Your feedback is anonymous. We store only the rating, selected reasons, optional comment, and submission time.</p></div>' +
      '<button class="msfea-modal-close" type="button" aria-label="Close feedback form">' + ICON_CLOSE + '</button></div>' +
      '<fieldset class="msfea-fieldset"><legend>Overall rating</legend><div class="msfea-stars" role="radiogroup" aria-label="Overall rating from 1 to 5"></div></fieldset>' +
      '<fieldset class="msfea-fieldset"><legend>Reasons (optional)</legend><div class="msfea-tags"></div></fieldset>' +
      '<label class="msfea-comment-label" for="msfea-exp-comment">Comment (optional)</label>' +
      '<textarea id="msfea-exp-comment" maxlength="500" placeholder="What worked well, or what should improve?"></textarea>' +
      '<div class="msfea-modal-meta"><span>Do not include personal information.</span><span class="msfea-comment-count">0 / 500</span></div>' +
      '<div class="msfea-modal-actions"><button class="msfea-submit" type="button" disabled>Submit anonymous feedback</button><span class="msfea-form-status" role="status"></span></div>';
    backdrop.appendChild(modal);
    root.appendChild(backdrop);

    var chosenRating = 0;
    var stars = modal.querySelector(".msfea-stars");
    for (var i = 1; i <= 5; i++) {
      (function (rating) {
        var b = document.createElement("button");
        b.className = "msfea-star";
        b.type = "button";
        b.setAttribute("role", "radio");
        b.setAttribute("aria-checked", "false");
        b.setAttribute("aria-label", rating + (rating === 1 ? " star" : " stars"));
        b.textContent = String(rating);
        b.addEventListener("click", function () {
          chosenRating = rating;
          Array.prototype.forEach.call(stars.children, function (x) {
            x.setAttribute("aria-checked", x === b ? "true" : "false");
          });
          modal.querySelector(".msfea-submit").disabled = false;
        });
        stars.appendChild(b);
      })(i);
    }
    ["Answers were helpful", "Easy to use", "Information was unclear", "Could not find my answer", "Technical problem"].forEach(function (tag, index) {
      var label = document.createElement("label");
      label.className = "msfea-tag";
      var check = document.createElement("input");
      check.type = "checkbox";
      check.value = tag;
      check.id = "msfea-exp-tag-" + index;
      var span = document.createElement("span");
      span.textContent = tag;
      label.appendChild(check);
      label.appendChild(span);
      modal.querySelector(".msfea-tags").appendChild(label);
    });
    var comment = modal.querySelector("textarea");
    comment.addEventListener("input", function () {
      modal.querySelector(".msfea-comment-count").textContent = comment.value.length + " / 500";
    });

    var previouslyFocused = document.activeElement;
    function closeModal() {
      backdrop.remove();
      if (previouslyFocused && previouslyFocused.focus) previouslyFocused.focus();
    }
    modal.querySelector(".msfea-modal-close").addEventListener("click", closeModal);
    backdrop.addEventListener("click", function (event) { if (event.target === backdrop) closeModal(); });
    modal.querySelector(".msfea-submit").addEventListener("click", function () {
      var submit = modal.querySelector(".msfea-submit");
      var status = modal.querySelector(".msfea-form-status");
      var selectedTags = Array.prototype.map.call(modal.querySelectorAll(".msfea-tag input:checked"), function (x) { return x.value; });
      submit.disabled = true;
      status.textContent = "Submitting…";
      fetch(API + "/experience-feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rating: chosenRating, tags: selectedTags, comment: comment.value.trim() || null }),
      }).then(function (r) {
        if (!r.ok) throw new Error("Your feedback could not be saved. Please try again.");
        modal.textContent = "";
        var success = el("msfea-success");
        var heading = document.createElement("h2");
        heading.textContent = "Thank you";
        success.appendChild(heading);
        success.appendChild(el("", "Your anonymous feedback was submitted."));
        var done = document.createElement("button");
        done.className = "msfea-submit";
        done.type = "button";
        done.textContent = "Done";
        done.addEventListener("click", closeModal);
        success.appendChild(done);
        modal.appendChild(success);
        done.focus();
      }).catch(function (error) {
        submit.disabled = false;
        status.textContent = error.message;
      });
    });
    backdrop.addEventListener("keydown", function (event) {
      if (event.key === "Escape") { event.preventDefault(); closeModal(); return; }
      if (event.key !== "Tab") return;
      var focusable = modal.querySelectorAll('button:not(:disabled),input,textarea');
      if (!focusable.length) return;
      var first = focusable[0];
      var last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });
    modal.querySelector(".msfea-modal-close").focus();
  }

  // Ephemeral per-tab identity, survives refresh for short retry protection.
  var sessionId;
  try {
    sessionId = sessionStorage.getItem("msfea-session");
    if (!sessionId) {
      sessionId = crypto.randomUUID();
      sessionStorage.setItem("msfea-session", sessionId);
    }
  } catch (_) {
    sessionId = Date.now().toString(36) + Math.random().toString(36).slice(2);
  }

  function send(preset, isRetry) {
    var q = (preset !== undefined ? preset : input.value).trim();
    if (!q || sendBtn.disabled) return;
    clearWelcome();
    addUser(q);
    input.value = "";
    autoGrow();
    updateCount();
    setBusy(true);
    showTyping();

    // "skipped" is a local marker meaning "don't ask again", not a department —
    // send null so the server answers unscoped.
    var dept = getDept();
    var history = conversation.slice(-MAX_HISTORY_MESSAGES);
    fetch(API + "/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: q,
        session_id: sessionId,
        department: dept && dept !== "skipped" ? dept : null,
        history: history,
      }),
    })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (data) {
          if (!r.ok) {
            var failure = new Error(typeof data.detail === "string" ? data.detail :
              "The assistant could not process that request.");
            failure.userMessage = true;
            throw failure;
          }
          return data;
        });
      })
      .then(function (data) {
        hideTyping();
        addBot(data, q);
        // Provider/network failures are not dialogue and should not contaminate
        // the next retrieval query.
        if (!data.error_code && !data.local) {
          conversation.push({
            role: "user",
            content: q.slice(0, MAX_HISTORY_MESSAGE_CHARS),
          });
          if (!data.refused && data.answer) {
            conversation.push({
              role: "assistant",
              content: String(data.answer).slice(0, MAX_HISTORY_MESSAGE_CHARS),
            });
          }
          conversation = conversation.slice(-MAX_HISTORY_MESSAGES);
          completedAnswers += 1;
          maybeInvite();
        }
      })
      .catch(function (error) {
        hideTyping();
        addBot({
          answer: error.userMessage ? error.message :
            "I couldn't reach the assistant. Check your connection, then choose Try again.",
          refused: true,
          disclaimer: "",
          error_code: "request_failed",
        }, q);
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
    refreshDeptPill();
    // Ask for the department once, before anything else — it changes which rules
    // the answers come from, so it is worth one tap up front.
    if (!msgs.children.length) {
      if (getDept()) showWelcome();
      else showDepartmentPicker();
    }
    if (!STANDALONE) setTimeout(function () { input.focus(); }, 120);
  }

  function closePanel() {
    if (STANDALONE) return;
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
  newBtn.addEventListener("click", resetChat);
  sendBtn.addEventListener("click", function () { send(); });
  panel.querySelector(".msfea-deptpill").addEventListener("click", showDepartmentPicker);
  panel.querySelector(".msfea-exp-open").addEventListener("click", openExperienceModal);
  panel.querySelector(".msfea-invite-open").addEventListener("click", openExperienceModal);
  panel.querySelector(".msfea-invite-close").addEventListener("click", function () {
    inviteHandled = true;
    panel.querySelector(".msfea-invite").hidden = true;
  });

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
    if (root.querySelector(".msfea-modal-backdrop")) return;
    if (!STANDALONE && e.key === "Escape" && root.classList.contains("is-open")) closePanel();
  });
  if (STANDALONE) openPanel();
})();
