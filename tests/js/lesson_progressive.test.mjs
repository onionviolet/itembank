import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {JSDOM} from 'jsdom';
import {python} from './python_bin.mjs';

const page = execFileSync(python, ['-c',
  "import model; from surfaces.lesson import lesson_page; p='fixtures/lesson_comparison.md'; " +
  "print(lesson_page(p,model.load(p),model.parse_lesson(p),mode='guided'))"],
  {cwd:new URL('../..', import.meta.url), encoding:'utf8'});

async function reader(hash='') {
  const dom = new JSDOM(page, {runScripts:'dangerously', url:'http://localhost/lesson/demo'+hash,
    beforeParse(window) {
      window.HTMLElement.prototype.scrollIntoView = function () {};
      window.fetch = () => {throw new Error('Unexpected network request');};
    }});
  await new Promise(resolve => dom.window.addEventListener('load', resolve));
  return dom;
}

test('native stages reveal, restart, highlight, and preserve authored wording', async () => {
  const dom = await reader();
  const doc = dom.window.document;
  const stages = [...doc.querySelectorAll('.stage')];
  assert.ok(stages.length > 1);
  assert.equal(doc.querySelector('.stage .stage'), null);
  const content = stages.map(stage => stage.textContent);
  const preview = doc.querySelector('.lesson-source-preview');
  assert.ok(preview);
  assert.equal(preview.open, false);
  assert.equal(preview.querySelector('blockquote').textContent,
    doc.querySelector('.callout-excerpt .callout-body').textContent);
  const visible = () => stages.filter(stage => !stage.hidden).length;
  const button = label => [...doc.querySelectorAll('button')].find(b => b.textContent === label);
  assert.equal(visible(), 1);
  button('Next explanation').click();
  assert.equal(visible(), 2);
  button('Show all explanations').click();
  assert.equal(visible(), stages.length);
  assert.equal(button('Next explanation').disabled, true);
  button('Start again').click();
  assert.equal(visible(), 1);
  button('Highlight key wording').click();
  assert.equal(button('Highlight key wording').getAttribute('aria-pressed'), 'true');
  assert.ok(doc.getElementById('lesson-content').classList.contains('reading-emphasis'));
  button('Highlight key wording').click();
  assert.equal(button('Highlight key wording').getAttribute('aria-pressed'), 'false');
  assert.deepEqual(stages.map(stage => stage.textContent), content);
  dom.window.close();
});

test('source fragment reveals its stage and printing exposes all permitted stages', async () => {
  const dom = await reader('#source-rain-01');
  const stages = [...dom.window.document.querySelectorAll('.stage')];
  const source = dom.window.document.getElementById('source-rain-01');
  assert.ok([...source.querySelectorAll('.stage')].every(stage => !stage.hidden));
  const detail = dom.window.document.querySelector('.lesson-reading-detail');
  assert.ok(detail.textContent.includes('hold the time interval fixed'));
  detail.open = false;
  dom.window.dispatchEvent(new dom.window.Event('beforeprint'));
  assert.ok(stages.every(stage => !stage.hidden));
  assert.equal(detail.open, true);
  dom.window.dispatchEvent(new dom.window.Event('afterprint'));
  assert.equal(detail.open, false);
  [...dom.window.document.querySelectorAll('button')].find(b => b.textContent === 'Start again').click();
  dom.window.document.querySelector('.lesson-reading-outline a[href="#source-rain-01"]').click();
  assert.ok([...source.querySelectorAll('.stage')].every(stage => !stage.hidden));
  [...dom.window.document.querySelectorAll('button')].find(b => b.textContent === 'Start again').click();
  dom.window.document.querySelector('.stage a[href="#source-rain-01"]').click();
  assert.ok([...source.querySelectorAll('.stage')].every(stage => !stage.hidden));
  dom.window.close();
});

test('without JavaScript every stage and source excerpt remains readable', () => {
  const dom = new JSDOM(page);
  assert.ok([...dom.window.document.querySelectorAll('.stage')].every(stage => !stage.hidden));
  assert.ok(dom.window.document.getElementById('source-rain-01').textContent.includes('12 mm'));
  assert.equal(dom.window.document.querySelector('.lesson-reading-controls'), null);
  dom.window.close();
});
