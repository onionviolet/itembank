import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { JSDOM } from 'jsdom';
import { python } from './python_bin.mjs';

const html = execFileSync(python, ['-c', `
import sys
sys.path.insert(0, 'tests')
from ui_overhaul_workspace_roundtrip import reading_page
print(reading_page())
`], { cwd: new URL('../..', import.meta.url), encoding: 'utf8' });
const key = 'itembank-reading:["synthetic","synthetic-reading","revision-one"]';
const draft = 'Previous source thought 中文\n  Keep this spacing.';

async function setup({ source = null, savedDraft = draft, savedSource = 'original', mode = 'read' } = {}) {
  const dom = new JSDOM(html, { url: 'http://localhost/', runScripts: 'outside-only' });
  const { window } = dom;
  const requests = [];
  const scrolls = [];
  window.scrollTo = value => scrolls.push(value);
  window.matchMedia = () => ({ matches: false, addEventListener() {} });
  window.sessionStorage.setItem(key, JSON.stringify({ source: savedSource, draft: savedDraft, y: 800 }));
  window.sessionStorage.setItem(key + ':workspace', JSON.stringify({ mode }));
  const initialDraft = window.sessionStorage.getItem(key);
  window.fetch = async (url, options) => {
    requests.push({ url, body: JSON.parse(options.body) });
    return { ok: true, json: async () => ({
      occurrence: { source_ref: { source_fingerprint: source === null ? null : 'current' } },
      reading_state: { state: 'not-reported' }, availability: { state: source === null ? 'course.reading_source_stale' : 'available' },
      content: source, notes: [], note_error: null,
    }) };
  };
  window.eval([...window.document.scripts].find(script => script.textContent.includes('const ctx=')).textContent);
  await new Promise(resolve => setImmediate(resolve));
  return { dom, window, requests, scrolls, initialDraft, get: id => window.document.getElementById(id) };
}

test('stale or unavailable source recovery opens the exact readonly draft from Read mode without a write', async () => {
  for (const source of [null, 'Changed source bytes']) {
    const app = await setup({ source });
    try {
      assert.equal(app.get('recover-reading-draft').hidden, false);
      assert.equal(app.window.document.querySelector('.reading-notes').hidden, true);
      assert.equal(app.get('note').value, '', 'Old wording cannot become a current draft automatically.');
      app.get('reading-tools').open = true;
      app.get('recover-reading-draft').click();
      const field = app.get('previous-drafts').querySelector('textarea');
      assert.equal(app.window.document.querySelector('.reading-layout').dataset.readingMode, 'notebook');
      assert.equal(app.get('reading-tools').open, false);
      assert.equal(field.closest('details').open, true);
      assert.equal(app.window.document.activeElement, field);
      assert.equal(field.value, draft);
      assert.equal(field.readOnly, true);
      assert.equal(app.get('note').value, '');
      assert.equal(app.window.sessionStorage.getItem(key), app.initialDraft);
      assert.equal(app.get('resume-reading').disabled, true);
      assert.deepEqual(app.scrolls, [], 'Recovery cannot restore stale reading coordinates.');
      assert.deepEqual(app.requests.map(row => row.url), ['/api/course/reading-view']);
    } finally { app.dom.window.close(); }
  }
});

test('there is no previous-draft action for empty history or the current source revision', async () => {
  for (const options of [{ savedDraft: '' }, { source: 'Current source', savedSource: 'current' }]) {
    const app = await setup(options);
    try {
      assert.equal(app.get('recover-reading-draft').hidden, true);
      assert.equal(app.get('previous-drafts').children.length, 0);
      assert.deepEqual(app.requests.map(row => row.url), ['/api/course/reading-view']);
    } finally { app.dom.window.close(); }
  }
});

test('source selection survives tool activation, while other controls and invalid selections keep native behavior', async () => {
  const app = await setup({ source: 'Current source passage', savedSource: 'current', savedDraft: '' });
  try {
    const selection = app.window.getSelection();
    const range = app.window.document.createRange();
    range.selectNodeContents(app.get('source-content'));
    selection.addRange(range);
    const summary = app.get('reading-tools').querySelector('summary');
    const pointer = element => {
      const event = new app.window.MouseEvent('pointerdown', { bubbles: true, cancelable: true });
      element.dispatchEvent(event);
      return event.defaultPrevented;
    };
    assert.equal(pointer(summary), true);
    assert.equal(pointer(app.get('reading-quote')), true);
    assert.equal(pointer(app.get('reading-help-selection')), true);
    assert.equal(pointer(app.get('reading-size')), false);
    app.get('reading-tools').open = true;
    app.get('reading-quote').click();
    assert.equal(app.get('note').value, 'Source passage: Current source passage\nMy thought: ');
    assert.equal(app.get('reading-tools').open, false);
    selection.removeAllRanges();
    assert.equal(pointer(summary), false);
    range.selectNodeContents(app.get('note-state'));
    selection.addRange(range);
    assert.equal(pointer(summary), false);
    assert.deepEqual(app.requests.map(row => row.url), ['/api/course/reading-view']);
  } finally { app.dom.window.close(); }
});
