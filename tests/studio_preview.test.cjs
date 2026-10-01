const test = require('node:test');
const assert = require('node:assert/strict');
const preview = require('../dashboard/studio_preview.js');

test('renders the actual official form as a clickable safe link', () => {
  const output = preview.render('Use [CDC letter request form](https://forms.office.com/Pages/ResponsePage.aspx?id=abc&origin=cdc).');
  assert.match(output, /href="https:\/\/forms.office.com\/Pages\/ResponsePage.aspx\?id=abc&amp;origin=cdc"/);
  assert.match(output, />CDC letter request form<\/a>/);
  assert.match(output, /rel="noopener noreferrer"/);
});
test('model HTML and unsafe markdown schemes cannot execute', () => {
  const output = preview.render('<img src=x onerror=alert(1)> [open](javascript:alert) **<script>bad</script>**');
  assert.doesNotMatch(output, /<img|<script|href="javascript:/);
  assert.match(output, /&lt;img/);
  assert.match(output, /<strong>&lt;script&gt;/);
});
test('long bare form URLs remain usable without consuming the page width', () => {
  const url = 'https://forms.office.com/?id=' + 'A'.repeat(200);
  const output = preview.render('Form: ' + url + '.\nCheck the source.');
  assert.ok(output.includes('href="' + url + '"'));
  assert.match(output, />Open official link<\/a>\.<br>Check/);
});
