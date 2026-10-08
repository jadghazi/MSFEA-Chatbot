// Exercise the actual send function with a pending fetch, without a browser dependency.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('widget/widget.js', 'utf8');
const sendCode = source.slice(source.indexOf('  function send(preset, isRetry)'),
                              source.indexOf('  /* ---------- open / close ---------- */'));

const departmentCodes = ['mech', 'ece', 'chem', 'iem', 'cee'];

function harness(department = 'cee', render) {
  let resolve;
  const calls = [], answers = [];
  let limitNotices = 0;
  const noop = () => {};
  const scope = {
    input: { value: 'Requirements?', focus: noop }, sendBtn: { disabled: false },
    clearWelcome: noop, addUser: noop, autoGrow: noop, updateCount: noop,
    showTyping: noop, hideTyping: noop, getDept: () => department,
    deptLabel: code => departmentCodes.includes(code) ? code.toUpperCase() : null,
    setBusy: busy => { scope.sendBtn.disabled = busy; },
    conversation: [], MAX_CHAT_QUESTIONS: 6, MAX_HISTORY_MESSAGES: 8,
    MAX_HISTORY_MESSAGE_CHARS: 1200,
    sessionId: 'widget-session-0001', API: '', completedAnswers: 0, maybeInvite: noop,
    showChatLimitModal: () => { limitNotices += 1; },
    addBot: answer => { answers.push(answer); return render && render(answer); },
    fetch: (...args) => { calls.push(args); return new Promise(r => { resolve = r; }); },
  };
  vm.createContext(scope);
  vm.runInContext(sendCode, scope);
  return { scope, calls, answers, get limitNotices() { return limitNotices; }, finish: async (status, data) => {
    resolve({ ok: status < 400, status, json: () => Promise.resolve(data) });
    await new Promise(setImmediate);
  }};
}

test('repeated Send/Enter submissions have one pending fetch', async () => {
  const h = harness();
  for (let i = 0; i < 10; i++) h.scope.send('Requirements?');
  assert.equal(h.calls.length, 1);
  assert.equal(JSON.parse(h.calls[0][1].body).session_id, 'widget-session-0001');
  assert.equal(JSON.parse(h.calls[0][1].body).department, 'cee');
  await h.finish(200, { answer: 'Grounded answer', refused: false });
  assert.equal(h.scope.sendBtn.disabled, false);
  assert.equal(h.scope.conversation.length, 2);
});

test('answer reveal keeps Send locked and delays history/count until the full reply is visible', async () => {
  let finishReveal;
  const h = harness('cee', () => new Promise(resolve => { finishReveal = resolve; }));
  h.scope.send('Requirements?');
  await h.finish(200, { answer: 'Grounded answer', refused: false });
  assert.equal(h.scope.sendBtn.disabled, true);
  assert.equal(h.scope.conversation.length, 0);
  assert.equal(h.scope.completedAnswers, 0);
  h.scope.send('Another question?');
  assert.equal(h.calls.length, 1);
  finishReveal();
  await new Promise(setImmediate);
  assert.equal(h.scope.sendBtn.disabled, false);
  assert.equal(h.scope.conversation.length, 2);
  assert.equal(h.scope.completedAnswers, 1);
});

test('question submission is blocked until a valid department is selected', () => {
  const h = harness(null);
  h.scope.send('Requirements?');
  assert.equal(h.calls.length, 0);
});

test('student picker contains exactly the five supported departments', () => {
  const block = source.slice(source.indexOf('  var DEPARTMENTS = ['),
                             source.indexOf('  ];', source.indexOf('  var DEPARTMENTS = [')) + 4);
  const codes = [...block.matchAll(/code: "([^"]+)"/g)].map(match => match[1]);
  const labels = [...block.matchAll(/label: "([^"]+)"/g)].map(match => match[1]);
  assert.deepEqual(codes, departmentCodes);
  assert.deepEqual(labels, [
    'Mechanical Engineering',
    'Electrical and Computer Engineering',
    'Chemical Engineering',
    'Industrial Engineering and Management',
    'Civil and Environmental Engineering',
  ]);
  assert.doesNotMatch(source, /Skip —|I'm not sure|No department/);
});

test('opening the department picker clears the selected department and conversation', () => {
  const pickerCode = source.slice(source.indexOf('  function showDepartmentPicker()'),
                                  source.indexOf('  /* ---------- empty state ---------- */'));
  const buttons = [];
  let selected = 'ece';
  const makeNode = () => ({
    children: [],
    appendChild(child) { this.children.push(child); },
    addEventListener(type, listener) { this[type] = listener; },
  });
  const scope = {
    msgs: makeNode(), conversation: [{ role: 'user', content: 'old context' }],
    completedAnswers: 2, setDept: code => { selected = code; },
    el: () => makeNode(), DEPARTMENTS: departmentCodes.map(code => ({ code, abbr: code, label: code })),
    document: { createElement: () => { const button = makeNode(); buttons.push(button); return button; } },
    showWelcome: () => {}, input: { focus: () => {} },
  };
  vm.createContext(scope);
  vm.runInContext(pickerCode, scope);
  scope.showDepartmentPicker();
  assert.equal(selected, null);
  assert.equal(scope.conversation.length, 0);
  assert.equal(scope.completedAnswers, 0);
  assert.equal(buttons.length, 5);
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

test('six completed questions end the chat, while failures do not use a slot', async () => {
  const h = harness();
  h.scope.send('Question 1?');
  await h.finish(200, { answer: 'Temporary failure', error_code: 'service_unavailable' });
  assert.equal(h.scope.completedAnswers, 0);
  for (let i = 1; i <= 6; i++) {
    h.scope.send(`Question ${i}?`);
    await h.finish(200, { answer: `Answer ${i}`, refused: false });
  }
  assert.equal(h.scope.completedAnswers, 6);
  assert.equal(h.limitNotices, 1);
  h.scope.send('Question 7?');
  assert.equal(h.calls.length, 7);
  assert.equal(h.limitNotices, 2);
});

test('upstream 503 has a clear retry message and does not use a slot', async () => {
  const h = harness();
  h.scope.send('Requirements?');
  await h.finish(503, { detail: 'Service Unavailable' });
  assert.match(h.answers[0].answer, /temporarily unavailable.*try again shortly/i);
  assert.equal(h.scope.completedAnswers, 0);
  assert.equal(h.scope.conversation.length, 0);
});

test('an incomplete success response does not create an empty answer or use a slot', async () => {
  const h = harness();
  h.scope.send('Requirements?');
  await h.finish(200, {});
  assert.match(h.answers[0].answer, /try again/i);
  assert.equal(h.scope.completedAnswers, 0);
  assert.equal(h.scope.conversation.length, 0);
});

test('starting a new chat clears history and creates a new session', () => {
  const resetCode = source.slice(source.indexOf('  function resetChat(skipConfirm)'),
                                 source.indexOf('  function showChatLimitModal()'));
  let removed = false;
  let focused = false;
  const scope = {
    requestBusy: false, completedAnswers: 6, conversation: [{ role: 'user', content: 'old' }],
    sessionId: 'old-session',
    msgs: { querySelector: () => ({}), textContent: 'old answer' },
    root: { querySelector: () => ({ remove() { removed = true; } }) },
    panel: { querySelector: () => ({ hidden: false }) },
    getDept: () => 'ece', showWelcome() {}, showDepartmentPicker() {},
    input: { value: 'new text', focus() { focused = true; } },
    autoGrow() {}, updateCount() {}, syncComposerState() {},
    startNewSession() { scope.sessionId = 'new-session'; },
  };
  vm.createContext(scope);
  vm.runInContext(resetCode, scope);
  scope.resetChat(true);
  assert.equal(scope.conversation.length, 0);
  assert.equal(scope.completedAnswers, 0);
  assert.equal(scope.msgs.textContent, '');
  assert.equal(scope.sessionId, 'new-session');
  assert.equal(removed, true);
  assert.equal(focused, true);
});
