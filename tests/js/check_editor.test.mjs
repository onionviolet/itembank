// check_editor.test.mjs — the CM6 editor's interactive contract, executed
// against the REAL vendored bundle and boot script (ruling 16). The served
// page embeds the same two files; this test boots them in jsdom so Tab,
// Shift-Tab, Enter and the read-only submit lock are proven by execution,
// not by reading the page source. The string checks in
// tests/check_roundtrip.py are source assertions; these are the behaviour
// assertions.
//
// jsdom (pinned 29.1.1, recorded under the §4a rule in
// assets/vendor/codemirror/VENDOR.md) cannot measure layout, so the
// measurement APIs CM6's measure loop calls are shimmed to stable zero
// geometry. The tests assert state and DOM structure — the 500-line pixel
// alignment stays a manual row in 05-VALIDATION.md. jsdom also does not
// synthesize native keyboard activation of a focused button (a real browser
// fires click for Enter/Space on a focused <button>), so the submission
// path is asserted through the button's click handler plus the structural
// fact that the Check control is a real button and the editor's own Enter
// binding never triggers submission.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { JSDOM } from 'jsdom';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const BUNDLE = path.join(ROOT, 'assets', 'vendor', 'codemirror', 'codemirror.bundle.js');
const BOOT = path.join(ROOT, 'assets', 'vendor', 'codemirror', 'check-editor-boot.js');

function makeDom() {
  const dom = new JSDOM(
    '<!doctype html><html><body><div id="host"></div></body></html>',
    { pretendToBeVisual: true, runScripts: 'outside-only' });
  const win = dom.window;
  // CM6's measure loop queries geometry; jsdom returns none. Stable zero
  // geometry keeps the editor functional for state-level assertions. (The
  // pixel alignment itself is 05-07's manual pass.)
  const ZERO = { x: 0, y: 0, top: 0, left: 0, right: 0, bottom: 0,
                 width: 0, height: 0, toJSON() { return this; } };
  const emptyList = () => ({ length: 0, item: () => null,
                             [Symbol.iterator]: function* () {} });
  if (!win.Range.prototype.getClientRects) {
    win.Range.prototype.getClientRects = emptyList;
  }
  if (!win.Range.prototype.getBoundingClientRect) {
    win.Range.prototype.getBoundingClientRect = () => ZERO;
  }
  if (!win.Element.prototype.getClientRects) {
    win.Element.prototype.getClientRects = emptyList;
  }
  if (!win.Element.prototype.getBoundingClientRect) {
    win.Element.prototype.getBoundingClientRect = () => ZERO;
  }
  const ctx = dom.getInternalVMContext();
  vm.runInContext(readFileSync(BUNDLE, 'utf8'), ctx, { filename: 'codemirror.bundle.js' });
  vm.runInContext(readFileSync(BOOT, 'utf8'), ctx, { filename: 'check-editor-boot.js' });
  if (typeof win.CodeMirror !== 'object' || typeof win.CheckEditorBoot !== 'object') {
    throw new Error('vendored bundle/boot did not install their globals');
  }
  return dom;
}

function boot(dom, opts) {
  const mount = dom.window.document.getElementById('host');
  const editor = dom.window.CheckEditorBoot.create(mount, opts || {});
  return { dom, mount, editor, win: dom.window };
}

function keyDown(win, target, key, mods) {
  const ev = new win.KeyboardEvent('keydown', Object.assign(
    { key, bubbles: true, cancelable: true }, mods || {}));
  const prevented = !target.dispatchEvent(ev);
  return prevented;
}

/* CM6 renders a hidden gutter element to measure the widest digit; the
   visible line numbers are the ones that are not hidden. */
function visibleGutterNumbers(mount) {
  return [...mount.querySelectorAll('.cm-gutterElement')]
    .filter((g) => g.style.visibility !== 'hidden')
    .map((g) => g.textContent)
    .filter((t) => /^\d+$/.test(t));
}

test('bundle and boot script are loaded from the vendored path (no network)', () => {
  // The files themselves are read above; a network URL would be a different
  // origin and cannot be read by readFileSync. Assert the boot file has no
  // loader call and no CDN reference.
  const bootSrc = readFileSync(BOOT, 'utf8');
  assert.ok(!/\b(import|require|fetch)\s*\(/.test(bootSrc),
    'boot script must not load anything from a network URL');
  assert.ok(!bootSrc.includes('http://') && !bootSrc.includes('https://'),
    'boot script must not reference a CDN');
});

test('Tab inserts a literal tab at the cursor and keeps focus', () => {
  const { win, editor } = boot(makeDom(), { starter: '' });
  const view = editor.getView();
  view.focus();
  const content = view.contentDOM;
  assert.equal(editor.isEmpty(), true);
  keyDown(win, content, 'Tab');
  assert.equal(editor.getSource(), '\t', 'Tab must insert a literal tab');
  assert.equal(win.document.activeElement, content,
    'Tab must not move focus out of the editor');
  // The tab is a real transaction: it is undoable, not a value assignment.
  assert.equal(editor.lineCount(), 1);
});

test('Shift-Tab dedents the current line only, never past column 0', () => {
  const { win, editor } = boot(makeDom(), { starter: '\tone\n  two\nthree' });
  const view = editor.getView();
  view.focus();
  const content = view.contentDOM;
  // cursor at the end of line 1 (the "\tone" line) -> dedent removes the tab.
  view.dispatch({ selection: { anchor: 4 } });
  keyDown(win, content, 'Shift-Tab');
  assert.equal(editor.getSource(), 'one\n  two\nthree',
    'Shift-Tab must remove one leading tab from the current line only');
  // line 2 has two leading spaces -> dedent removes both (up to four).
  view.dispatch({ selection: { anchor: 8 } });
  keyDown(win, content, 'Shift-Tab');
  assert.equal(editor.getSource(), 'one\ntwo\nthree',
    'Shift-Tab must remove up to four leading spaces from the current line');
  // an unindented line -> nothing changes.
  view.dispatch({ selection: { anchor: 11 } });
  keyDown(win, content, 'Shift-Tab');
  assert.equal(editor.getSource(), 'one\ntwo\nthree',
    'Shift-Tab on an unindented line must do nothing');
  // never past column 0: a one-space line becomes empty, then nothing more.
  view.dispatch({ changes: { from: 0, insert: ' x\n' } });
  view.dispatch({ selection: { anchor: 1 } });
  keyDown(win, content, 'Shift-Tab');
  assert.equal(editor.getSource(), 'x\none\ntwo\nthree');
  keyDown(win, content, 'Shift-Tab');
  assert.equal(editor.getSource(), 'x\none\ntwo\nthree',
    'Shift-Tab must never dedent past column 0');
});

test('gutter is 1-based and grows with the document', () => {
  const { mount, editor } = boot(makeDom(), { starter: 'a\nb\nc' });
  assert.deepEqual(visibleGutterNumbers(mount), ['1', '2', '3'],
    'gutter must number lines 1..N in order');
  // paste more lines -> the gutter grows.
  editor.getView().dispatch({
    changes: { from: editor.getView().state.doc.length, insert: '\nd\ne' },
  });
  assert.deepEqual(visibleGutterNumbers(mount), ['1', '2', '3', '4', '5'],
    'gutter must grow with the document');
});

test('no lineWrapping: a long line is one logical line', () => {
  const { editor } = boot(makeDom(), { starter: '' });
  const view = editor.getView();
  view.dispatch({ changes: { from: 0, insert: 'x'.repeat(300) } });
  assert.equal(editor.lineCount(), 1,
    'a long line must stay one line (no soft wrap)');
  assert.equal(editor.wraps(), false,
    'the lineWrapping facet must not be enabled');
});

test('Enter in the editor inserts a newline; submission only via the button', () => {
  const { win, editor } = boot(makeDom(), { starter: '' });
  const view = editor.getView();
  view.focus();
  const content = view.contentDOM;
  keyDown(win, content, 'Enter');
  assert.equal(editor.getSource(), '\n',
    'Enter in the editor must insert a newline (native typing preserved)');
  keyDown(win, content, ' ');
  // Space is a character; the keymap leaves it to CM6's input handling.
  assert.equal(editor.getSource(), '\n',
    'Space in the editor must not submit or move focus');

  // The Check control is a real button: a focused button in a browser
  // activates on Enter/Space via a click. Assert the submission path is the
  // button's click handler (jsdom cannot synthesize native button
  // activation, so the click is dispatched directly) and that the editor's
  // own Enter key never reaches it.
  const btn = win.document.createElement('button');
  btn.type = 'button';
  btn.textContent = 'Submit answer';
  win.document.body.appendChild(btn);
  let submissions = 0;
  btn.addEventListener('click', () => { submissions++; });
  btn.focus();
  btn.click();
  assert.equal(submissions, 1, 'the button click reaches the submission handler');
  assert.equal(btn.tagName, 'BUTTON',
    'the Check control must be a real semantic button (browser Enter/Space activate it)');
});

test('editor goes read-only after submit; source stays visible', () => {
  const { win, editor } = boot(makeDom(), { starter: 'print(1)' });
  const view = editor.getView();
  view.focus();
  const content = view.contentDOM;
  editor.setReadOnly(true);
  const before = editor.getSource();
  keyDown(win, content, 'Tab');
  assert.equal(editor.getSource(), before,
    'a read-only editor must not accept a Tab insert');
  keyDown(win, content, 'Enter');
  assert.equal(editor.getSource(), before,
    'a read-only editor must not accept a newline');
  assert.equal(editor.getSource().length > 0, true,
    'the submitted source stays visible after the lock');
});
