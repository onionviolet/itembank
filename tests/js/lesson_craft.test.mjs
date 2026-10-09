import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {JSDOM} from 'jsdom';
import {python} from './python_bin.mjs';

const markup = execFileSync(python, ['-c',
  "from surfaces import lesson; print('<div id=\"lesson-content\">'+" +
  "lesson._code_block('python', 'if True:\\n    print(\"< & >\")\\n')+" +
  "lesson._code_block('', '')+lesson._gloss_trigger_html('Boundary', 'boundary')+" +
  "lesson._gloss_panel_html({'canonical':'Boundary','def':'An edge.'},'boundary')+" +
  "'</div>'+lesson.CODE_CRAFT_JS+lesson.GLOSS_HOVER_JS)"],
  {cwd:new URL('../..', import.meta.url), encoding:'utf8'});

function reader(writeText, fine=true) {
  return new JSDOM(markup, {runScripts:'dangerously', url:'http://localhost/lesson/demo',
    beforeParse(window) {
      window.matchMedia = () => ({matches:fine});
      if (writeText) Object.defineProperty(window.navigator, 'clipboard', {value:{writeText}});
      const nativeMatches = window.Element.prototype.matches;
      window.Element.prototype.matches = function (selector) {
        return selector === ':popover-open' ? !!this._open : nativeMatches.call(this, selector);
      };
      const query = window.Document.prototype.querySelector;
      window.Document.prototype.querySelector = function (selector) {
        if (selector.includes(':popover-open')) return [...this.querySelectorAll('.gloss')]
          .find(panel => panel._open && panel.dataset.glossOpen === 'click') || null;
        return query.call(this, selector);
      };
      window.HTMLElement.prototype.showPopover = function () {
        if (this._hiding) throw new Error('Popover opening during hide');
        if (this._open) throw new Error('Repeated popover opening');
        this._open = true; this.dispatchEvent(new window.Event('toggle'));
      };
      window.HTMLElement.prototype.hidePopover = function () {
        this._hiding = true;
        try {
          this._open = false;
          const origin = window.document.getElementById(this.dataset.glossOrigin);
          if (origin && this.contains(window.document.activeElement)) origin.focus();
          this.dispatchEvent(new window.Event('toggle'));
        } finally { this._hiding = false; }
      };
    }});
}

test('copy preserves exact public source, pending lock and focused control', async () => {
  let resolve, calls=0, copied;
  const dom = reader(text => {calls++; copied=text; return new Promise(done => {resolve=done;});});
  const doc = dom.window.document, copy = doc.querySelector('.code-copy');
  copy.focus(); copy.click(); copy.click();
  assert.equal(calls, 1);
  assert.equal(copied, 'if True:\n    print("< & >")\n');
  assert.equal(copy.getAttribute('aria-disabled'), 'true');
  assert.equal(doc.querySelector('.code-status').textContent, 'Copying code...');
  assert.equal(doc.activeElement, copy);
  resolve(); await new Promise(setImmediate);
  assert.equal(doc.querySelector('.code-status').textContent, 'Code copied.');
  assert.equal(copy.hasAttribute('aria-disabled'), false);
  assert.equal(doc.activeElement, copy);
  doc.querySelector('.code-select').click();
  assert.equal(dom.window.getSelection().toString(), copied);
  assert.equal(doc.activeElement, doc.querySelector('.code-source'));
  dom.window.close();
});

test('unavailable, denied and empty copy states stay distinct and permit retry', async () => {
  const unavailable = reader();
  unavailable.window.document.querySelector('.code-copy').click();
  assert.match(unavailable.window.document.querySelector('.code-status').textContent, /^Copy unavailable/);
  unavailable.window.document.querySelectorAll('.code-copy')[1].click();
  assert.equal(unavailable.window.document.querySelectorAll('.code-status')[1].textContent, 'No code to copy.');
  unavailable.window.close();
  let denied=true;
  const dom = reader(() => denied ? Promise.reject(new Error('denied')) : Promise.resolve());
  const doc = dom.window.document;
  doc.querySelector('.code-copy').click(); await new Promise(setImmediate);
  assert.match(doc.querySelector('.code-status').textContent, /^Copy denied/);
  denied=false; doc.querySelector('.code-copy').click(); await new Promise(setImmediate);
  assert.equal(doc.querySelector('.code-status').textContent, 'Code copied.');
  dom.window.close();
});

test('native glossary keyboard entry, pin, Escape and Close return on fine and coarse pointers', async () => {
  for (const fine of [true, false]) {
    const dom = reader(null, fine), doc = dom.window.document;
    const errors = [];
    dom.window.addEventListener('error', event => {errors.push(event.error); event.preventDefault();});
    const term = doc.querySelector('.term'), panel = doc.querySelector('.gloss');
    term.focus();
    assert.equal(panel._open, true);
    term.dispatchEvent(new dom.window.Event('pointerenter'));
    if (fine) await new Promise(resolve => setTimeout(resolve, 220));
    term.click();
    assert.equal(panel.dataset.glossOpen, 'click');
    term.dispatchEvent(new dom.window.KeyboardEvent('keydown', {key:'ArrowDown',bubbles:true,cancelable:true}));
    assert.equal(panel.dataset.glossOpen, 'click');
    assert.equal(doc.activeElement, panel.querySelector('a'));
    assert.equal(panel.querySelector('.gloss-pin').hidden, false);
    panel.querySelector('.gloss-pin').click();
    assert.equal(panel.querySelector('.gloss-pin').getAttribute('aria-pressed'), 'false');
    panel.querySelector('.gloss-pin').click();
    doc.activeElement.dispatchEvent(new dom.window.KeyboardEvent('keydown', {key:'Escape',bubbles:true,cancelable:true}));
    assert.equal(panel._open, false);
    assert.equal(doc.activeElement, term);
    term.click(); panel.querySelector('.gloss-close').focus(); panel.querySelector('.gloss-close').click();
    assert.equal(panel._open, false);
    assert.equal(doc.activeElement, term);
    term.click(); panel.querySelector('a').focus(); panel.querySelector('a').click();
    assert.equal(panel._open, false);
    assert.equal(doc.activeElement, term);
    assert.equal(term.textContent, 'Boundary');
    assert.equal(term.getAttribute('aria-label'), null);
    assert.deepEqual(errors, []);
    dom.window.close();
  }
});
