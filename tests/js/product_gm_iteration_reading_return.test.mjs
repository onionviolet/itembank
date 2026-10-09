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
  const scrolls = [], requests = [];
  let y = 2500;
  Object.defineProperty(window, 'scrollY', { get: () => y });
  window.scrollTo = value => { scrolls.push(value); y = value.top; };
  window.matchMedia = () => ({ matches: false, addEventListener() {} });
  window.Range.prototype.getBoundingClientRect = () => ({ top: 100, bottom: 130 });
  const current = { occurrence: { source_ref: { source_fingerprint: 'one' } },
    reading_state: { state: 'not-reported' }, availability: { state: 'available' },
    content: 'Original synthetic selected source.', notes: [], note_error: null };
  window.fetch = async (url, options) => {
    requests.push({ url, body: JSON.parse(options.body) });
    return { ok: true, json: async () => current };
  };
  window.eval([...window.document.scripts].find(script => script.textContent.includes('const ctx=')).textContent);
  await new Promise(resolve => setImmediate(resolve));
  const source = window.document.getElementById('source-content');
  source.getBoundingClientRect = () => ({ top: 20, bottom: 400 });
  const select = (elementRange = false) => {
    const range = window.document.createRange();
    if (elementRange) range.selectNodeContents(source);
    else { range.setStart(source.firstChild, 0); range.setEnd(source.firstChild, source.textContent.length); }
    const selected = window.getSelection(); selected.removeAllRanges(); selected.addRange(range);
    window.document.dispatchEvent(new window.Event('selectionchange'));
  };
  return { dom, window, source, select, scrolls, requests, current,
    move: value => { y = value; }, settle: () => new Promise(resolve => setImmediate(resolve)) };
}

test('selected-passage position survives toolbar window scrolling without a canonical request', async () => {
  const app = await setup();
  try {
    app.select();
    app.move(0);
    app.window.dispatchEvent(new app.window.Event('scroll'));
    app.window.rememberPassage();
    app.window.returnToPassage();
    assert.equal(app.scrolls.at(-1).top, 2500);
    assert.equal(app.window.document.activeElement, app.source);
    assert.deepEqual(app.requests.map(row => row.url), ['/api/course/reading-view']);
  } finally { app.dom.window.close(); }
});

test('replaced source nodes cannot reuse the previous selection position even at the same fingerprint', async () => {
  for (const elementRange of [false, true]) {
    const app = await setup();
    try {
    app.select(elementRange);
    await app.window.refresh();
    app.move(800);
    app.window.getSelection().removeAllRanges();
    app.window.passageSnapshot();
    const range = app.window.document.createRange();
    if (elementRange) range.selectNodeContents(app.source);
    else { range.setStart(app.source.firstChild, 0); range.setEnd(app.source.firstChild, app.source.textContent.length); }
    app.window.getSelection().addRange(range);
    app.window.rememberPassage();
    app.window.returnToPassage();
    assert.equal(app.scrolls.at(-1).top, 800);
    } finally { app.dom.window.close(); }
  }
});

test('changed or unavailable source return refuses stale positions and preserves the private draft', async () => {
  for (const unavailable of [false, true]) {
    const app = await setup();
    try {
      app.select();
      app.window.rememberPassage();
      const note = app.window.document.getElementById('note');
      note.value = 'Keep my private unfinished thought 中文';
      app.current.occurrence.source_ref.source_fingerprint = 'two';
      if (unavailable) app.current.content = null;
      await app.window.refresh();
      app.move(800);
      app.window.returnToPassage();
      assert.equal(app.scrolls.length, 0);
      assert.equal(note.value, 'Keep my private unfinished thought 中文');
      assert.deepEqual(app.requests.map(row => row.url), ['/api/course/reading-view', '/api/course/reading-view']);
    } finally { app.dom.window.close(); }
  }
});
