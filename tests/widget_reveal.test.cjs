// Exercise the real reveal scheduler with DOM text nodes and an explicit clock.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('widget/widget.js', 'utf8');
const code = source.slice(source.indexOf('  function revealAnswer(bodyEl)'),
                          source.indexOf('  function addBot(data, failedQuestion)'));

function element(parent = null) {
  return {
    children: [], hidden: false, parentElement: parent, parentNode: parent,
    setAttribute() {},
    insertBefore(node, next) {
      node.remove();
      const index = next ? this.children.indexOf(next) : this.children.length;
      this.children.splice(index, 0, node);
      node.parentNode = node.parentElement = this;
    },
    remove() {
      if (this.parentNode) {
        const siblings = this.parentNode.children;
        siblings.splice(siblings.indexOf(this), 1);
        this.parentNode = this.parentElement = null;
      }
    },
    get previousSibling() {
      return this.parentNode && this.parentNode.children[this.parentNode.children.indexOf(this) - 1];
    },
  };
}

function harness({ reduced = false, hidden = false, scrolledUp = false, texts = ['Hello 👋', 'Safe link text'] } = {}) {
  const frames = new Map(), listeners = new Map(), motionListeners = new Set();
  let nextFrame = 0, scrolls = 0;
  const body = element();
  const blocks = texts.map(() => element(body));
  body.children = blocks;
  const nodes = texts.map((text, index) => {
    const node = {
      data: text, parentElement: blocks[index], parentNode: blocks[index],
      get nextSibling() { return this.parentNode.children[this.parentNode.children.indexOf(this) + 1] || null; },
    };
    blocks[index].children.push(node);
    return node;
  });
  body.querySelectorAll = () => blocks;
  const motion = {
    matches: reduced,
    addEventListener(type, listener) { motionListeners.add(listener); },
    removeEventListener(type, listener) { motionListeners.delete(listener); },
  };
  const document = {
    hidden,
    createTreeWalker() { let index = 0; return { nextNode: () => nodes[index++] || null }; },
    createElement: () => element(),
    addEventListener(type, listener) { listeners.set(type, listener); },
    removeEventListener(type) { listeners.delete(type); },
  };
  const scope = {
    window: {
      matchMedia: () => motion,
      requestAnimationFrame(callback) { const id = ++nextFrame; frames.set(id, callback); return id; },
      cancelAnimationFrame(id) { frames.delete(id); },
    },
    document, NodeFilter: { SHOW_TEXT: 4 },
    msgs: { scrollHeight: 1000, scrollTop: scrolledUp ? 0 : 500, clientHeight: 500 },
    scrollDown() { scrolls++; },
  };
  vm.createContext(scope);
  vm.runInContext(code, scope);
  const ready = scope.revealAnswer(body);
  return {
    ready, body, blocks, nodes, frames, listeners, motionListeners,
    get scrolls() { return scrolls; },
    tick(now) {
      const callbacks = [...frames.values()];
      frames.clear();
      callbacks.forEach(callback => callback(now));
    },
    hide() { document.hidden = true; listeners.get('visibilitychange')?.(); },
    reduceMotion() { motionListeners.forEach(listener => listener({ matches: true })); },
  };
}

test('reveals text gradually, preserves Unicode, and restores the exact full answer', async () => {
  const h = harness();
  assert.deepEqual(h.nodes.map(node => node.data), ['', '']);
  assert.equal(h.body.inert, true);
  assert.equal(h.blocks.every(block => block.hidden), true);
  h.tick(0);
  assert.equal(h.nodes[0].data, 'H');
  assert.equal(h.blocks[0].hidden, false);
  assert.equal(h.blocks[1].hidden, true);
  h.tick(90);
  assert.equal(h.nodes[0].data, 'Hello 👋');
  h.tick(300);
  await h.ready;
  assert.deepEqual(h.nodes.map(node => node.data), ['Hello 👋', 'Safe link text']);
  assert.equal(h.body.inert, false);
  assert.equal(h.frames.size + h.listeners.size + h.motionListeners.size, 0);
  assert.equal(h.blocks.every(block => block.children.length === 1), true);
});

test('long answers finish within the capped reveal duration', async () => {
  const h = harness({ texts: ['Long answer '.repeat(1000)] });
  h.tick(0);
  h.tick(2800);
  await h.ready;
  assert.equal(h.nodes[0].data, 'Long answer '.repeat(1000));
  assert.equal(h.frames.size, 0);
});

test('reduced motion and hidden tabs display the full answer without animation', async () => {
  for (const options of [{ reduced: true }, { hidden: true }]) {
    const h = harness(options);
    await h.ready;
    assert.equal(h.nodes[0].data, 'Hello 👋');
    assert.equal(h.frames.size, 0);
    assert.equal(h.listeners.size, 0);
  }
});

test('hiding the tab or enabling reduced motion finishes and cleans up an active reveal', async () => {
  for (const finish of ['hide', 'reduceMotion']) {
    const h = harness();
    h.tick(0);
    h[finish]();
    await h.ready;
    assert.equal(h.nodes[1].data, 'Safe link text');
    assert.equal(h.body.inert, false);
    assert.equal(h.frames.size + h.listeners.size + h.motionListeners.size, 0);
  }
});

test('reading older messages is not interrupted by reveal scrolling', async () => {
  const h = harness({ scrolledUp: true });
  h.tick(0);
  h.tick(300);
  await h.ready;
  assert.equal(h.scrolls, 0);
});
