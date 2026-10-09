import {test} from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import vm from 'node:vm';
import {JSDOM} from 'jsdom';

const script = execFileSync('python3', ['-c', 'from surfaces.quiz_page import QUESTION_STEM_JS; print(QUESTION_STEM_JS)'],
  {cwd: new URL('../..', import.meta.url), encoding: 'utf8'});
const esc = value => String(value || '').replace(/[&<>]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[ch]));
const context = vm.createContext({esc});
vm.runInContext(script, context);

test('fenced public stimulus is read-only, indented and inert', () => {
  const code = 'if 2 < 3:\n    print("<img src=x onerror=alert(1)>")';
  const rendered = context.questionStemHTML('Predict.\n\n```python\n' + code + '\n```');
  const doc = new JSDOM(rendered).window.document;
  assert.equal(doc.querySelector('h1').textContent, 'Predict.');
  assert.equal(doc.querySelector('pre code').textContent, code);
  assert.equal(doc.querySelector('pre').getAttribute('tabindex'), '0');
  assert.equal(doc.querySelector('img'), null);
  assert.match(doc.querySelector('figcaption').textContent, /Read-only/);
});

test('plain and malformed stems retain their complete text', () => {
  for (const stem of ['Plain <text>.', 'Predict.\n\n```python\nno closing fence']) {
    const doc = new JSDOM(context.questionStemHTML(stem)).window.document;
    assert.equal(doc.querySelector('h1').textContent, stem);
    assert.equal(doc.querySelector('pre'), null);
  }
});
