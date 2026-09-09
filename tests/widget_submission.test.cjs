// Exercise the actual send function with a pending fetch, without a browser dependency.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('widget/widget.js', 'utf8');
const sendCode = source.slice(source.indexOf('  function send(preset, isRetry)'),
                              source.indexOf('  /* ---------- open / close ---------- */'));

function harness() {
  let resolve;
  const calls = [], answers = [];
  const noop = () => {};
  const scope = {
    input: { value: 'Requirements?', focus: noop }, sendBtn: { disabled: false },
    clearWelcome: noop, addUser: noop, autoGrow: noop, updateCount: noop,
    showTyping: noop, hideTyping: noop, getDept: () => null,
    setBusy: busy => { scope.sendBtn.disabled = busy; },
    conversation: [], MAX_HISTORY_MESSAGES: 4, MAX_HISTORY_MESSAGE_CHARS: 1200,
    sessionId: 'widget-session-0001', API: '', completedAnswers: 0, maybeInvite: noop,
    addBot: answer => answers.push(answer),
    fetch: (...args) => { calls.push(args); return new Promise(r => { resolve = r; }); },
  };
  vm.createContext(scope);
  vm.runInContext(sendCode, scope);
  return { scope, calls, answers, finish: async (status, data) => {
    resolve({ ok: status < 400, json: () => Promise.resolve(data) });
    await new Promise(setImmediate);
  }};
}

test('repeated Send/Enter submissions have one pending fetch', async () => {
  const h = harness();
  for (let i = 0; i < 10; i++) h.scope.send('Requirements?');
  assert.equal(h.calls.length, 1);
  assert.equal(JSON.parse(h.calls[0][1].body).session_id, 'widget-session-0001');
  await h.finish(200, { answer: 'Grounded answer', refused: false });
  assert.equal(h.scope.sendBtn.disabled, false);
  assert.equal(h.scope.conversation.length, 2);
});

test('local acknowledgements preserve useful memory', async () => {
  const h = harness();
  h.scope.send('thanks');
  await h.finish(200, { answer: "You're welcome!", local: true });
  assert.equal(h.scope.conversation.length, 0);
});

test('friendly 429 is displayed and never retried automatically', async () => {
  const h = harness();
  h.scope.send('Requirements?');
  await h.finish(429, { detail: 'Please slow down and try again shortly.' });
  assert.equal(h.calls.length, 1);
  assert.equal(h.answers[0].answer, 'Please slow down and try again shortly.');
  assert.equal(h.scope.conversation.length, 0);
  assert.equal(h.scope.sendBtn.disabled, false);
});
