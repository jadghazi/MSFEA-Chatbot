// Exercise the actual send function with a pending fetch, without a browser dependency.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('widget/widget.js', 'utf8');
const sendCode = source.slice(source.indexOf('  function send(preset, isRetry)'),
                              source.indexOf('  /* ---------- open / close ---------- */'));

const departmentCodes = ['mech', 'ece', 'chem', 'iem', 'cee'];

function harness(department = 'cee') {
  let resolve;
  const calls = [], answers = [];
  const noop = () => {};
  const scope = {
    input: { value: 'Requirements?', focus: noop }, sendBtn: { disabled: false },
    clearWelcome: noop, addUser: noop, autoGrow: noop, updateCount: noop,
    showTyping: noop, hideTyping: noop, getDept: () => department,
    deptLabel: code => departmentCodes.includes(code) ? code.toUpperCase() : null,
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
  assert.equal(JSON.parse(h.calls[0][1].body).department, 'cee');
  await h.finish(200, { answer: 'Grounded answer', refused: false });
  assert.equal(h.scope.sendBtn.disabled, false);
  assert.equal(h.scope.conversation.length, 2);
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
