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

async function setup() {
  const dom = new JSDOM(html, { url: 'http://localhost/', runScripts: 'outside-only' });
  const { window } = dom;
  const requests = [];
  window.scrollTo = () => {};
  window.matchMedia = () => ({ matches: false, addEventListener() {} });
  window.fetch = async (url, options) => {
    requests.push({ url, body: JSON.parse(options.body) });
    return { ok: true, json: async () => ({
      occurrence: { source_ref: { source_fingerprint: 'original-source' } },
      reading_state: { state: 'not-reported' }, availability: { state: 'available' },
      content: 'Fictional passage for keyboard tools.', notes: [], note_error: null,
    }) };
  };
  window.eval([...window.document.scripts].find(script =>
    script.textContent.includes('const ctx=')).textContent);
  await new Promise(resolve => setImmediate(resolve));
  return { dom, window, requests, get: id => window.document.getElementById(id) };
}

test('Escape from reader tools returns focus and preserves draft without a write', async () => {
  const app = await setup();
  try {
    app.get('note').value = 'Keep my unfinished thought 中文';
    app.get('note').dispatchEvent(new app.window.Event('input', { bubbles: true }));
    app.get('reading-tools').open = true;
    app.get('reading-size').focus();
    app.get('reading-size').dispatchEvent(new app.window.KeyboardEvent('keydown', {
      key: 'Escape', bubbles: true, cancelable: true,
    }));
    assert.equal(app.get('reading-tools').open, false);
    assert.equal(app.window.document.activeElement, app.get('reading-tools').querySelector('summary'));
    assert.equal(app.get('note').value, 'Keep my unfinished thought 中文');
    assert.deepEqual(app.requests.map(row => row.url), ['/api/course/reading-view']);
  } finally { app.dom.window.close(); }
});

test('source context detour closes tools and restores the original reader mode and draft', async () => {
  const app = await setup();
  try {
    app.window.document.querySelector('[data-reading-mode-button="read"]').click();
    app.get('note').value = 'An unsaved source comparison';
    app.get('note').dispatchEvent(new app.window.Event('input', { bubbles: true }));
    app.get('reading-tools').open = true;
    app.get('reading-reference-open').click();
    assert.equal(app.get('reading-tools').open, false);
    assert.equal(app.get('reading-reference').open, true);
    assert.equal(app.window.document.activeElement, app.get('reading-reference').querySelector('summary'));
    app.window.document.querySelector('.reading-return').click();
    assert.equal(app.window.document.querySelector('.reading-layout').dataset.readingMode, 'read');
    assert.equal(app.window.document.activeElement, app.get('source-content'));
    assert.equal(app.get('note').value, 'An unsaved source comparison');
    assert.deepEqual(app.requests.map(row => row.url), ['/api/course/reading-view']);
  } finally { app.dom.window.close(); }
});

test('note action keeps writing prominent while closing an open tool panel', async () => {
  const app = await setup();
  try {
    app.get('reading-tools').open = true;
    app.get('reading-note-open').click();
    assert.equal(app.get('reading-tools').open, false);
    assert.equal(app.window.document.activeElement, app.get('note'));
    assert.equal(app.window.document.querySelector('.reading-layout').dataset.readingMode, 'notebook');
    assert.deepEqual(app.requests.map(row => row.url), ['/api/course/reading-view']);
  } finally { app.dom.window.close(); }
});

test('invalid source selection leaves its tool visible and keyboard focus intact', async () => {
  const app = await setup();
  try {
    app.get('reading-tools').open = true;
    const button = app.get('reading-help-selection');
    button.focus();
    button.click();
    assert.equal(app.get('reading-tools').open, true);
    assert.equal(app.window.document.activeElement, button);
    assert.match(app.get('reading-tools-state').textContent, /Select words inside the source passage/);
    assert.deepEqual(app.requests.map(row => row.url), ['/api/course/reading-view']);
  } finally { app.dom.window.close(); }
});
