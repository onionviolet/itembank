import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {createInterface} from 'node:readline';
import {request} from 'node:http';
import {readFile, mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';

const {chromium} = await import(process.env.ITEMBANK_PLAYWRIGHT_MODULE || 'playwright');
const root = fileURLToPath(new URL('.', import.meta.url));
const pyodideHashes = {
  'pyodide-lock.json': '3fdaef09e9e365c85e002737720f8d0ab8f278c1c244a2dde6a37663cf488ad4',
  'pyodide.asm.mjs': '2ac5eba365ec12839c75c03b39b3be1dd63b798852cc460b014b52238be042f7',
  'pyodide.asm.wasm': '3a0a00dfeaa348ac20f9ef09904233d32d33f644339662d4af368f8a2010f37a',
  'pyodide.mjs': '69e3f6ccec3e14b465df60be577ca62f536251406b9a00cce019eac5252a2495',
  'python_stdlib.zip': '80c5be6babfe03297069703410c3c29404dcf2525d2b128746bae5536f94831f',
};
for (const [name, expected] of Object.entries(pyodideHashes)) {
  const bytes = await readFile(`${root}vendor/pyodide/${name}`);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), expected, `Pyodide asset changed: ${name}`);
}
const server = spawn('python3', [`${root}server.py`, '--port', '0'], {stdio: ['ignore', 'pipe', 'inherit']});
const lines = createInterface({input: server.stdout});
const [line] = await once(lines, 'line');
const origin = line.replace('CS Dojo: ', '');
let browser;
const evidence = process.env.ITEMBANK_DOJO_EVIDENCE || '/tmp/itembank-cs-dojo-evidence';
const checks = [];
const pass = (name) => { checks.push(name); process.stdout.write(`PASS ${name}\n`); };
try {
  browser = await chromium.launch({executablePath: process.env.ITEMBANK_CHROMIUM, headless: true});
  await mkdir(evidence, {recursive: true});
  const page = await browser.newPage({viewport: {width: 1440, height: 1060}});
  const editorValue = () => page.evaluate(() => window.DojoEditor.getValue());
  const editorFill = (value) => page.evaluate((text) => window.DojoEditor.setValue(text), value);
  const editorFocus = () => page.evaluate(() => window.DojoEditor.focus());
  const errors = [];
  const unexpectedRequests = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('request', (request) => { if (!request.url().startsWith(origin) && !request.url().startsWith('blob:')) unexpectedRequests.push(request.url()); });
  await page.goto(origin);
  await page.locator('#run').click();
  assert.equal(await page.evaluate(() => document.activeElement.id), 'prediction');
  assert.equal(await page.locator('#run-state').textContent(), 'Ready');
  await page.locator('#prediction').fill('0 3\n1 7\n2 4\n3 undefined');
  await page.locator('#reflection').fill('The count is one beyond the last occupied index.');
  await editorFocus();
  await page.keyboard.press('Control+Enter');
  await page.waitForFunction(() => document.getElementById('run-state').dataset.state === 'done');
  assert.equal(await page.locator('#output').textContent(), '0 3\n1 7\n2 4\n3 undefined');
  assert.match(await page.locator('#prediction-snapshot').textContent(), /3 undefined/);
  pass('prediction precedes real execution and retains the run snapshot');

  await page.locator('#source-open').click();
  assert(await page.locator('#source-dialog').evaluate((element) => element.open));
  assert.match(await page.locator('#source-text').textContent(), /n - 1/);
  await page.keyboard.press('Escape');
  assert.equal(await page.evaluate(() => document.activeElement.id), 'source-open');
  await editorFocus();
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(() => document.activeElement.closest('.cm-editor')), null);
  pass('source context returns focus and the editor does not trap Tab');
  await editorFocus();
  await page.evaluate(() => window.DojoEditor.select(0, 5));
  await page.locator('#indent').click();
  assert.match(await editorValue(), /^  const readings/);
  await page.locator('#outdent').click();
  assert.match(await editorValue(), /^const readings/);
  pass('editor indents and outdents without trapping Tab');
  await page.screenshot({path: `${evidence}/desktop-predict.png`, fullPage: true});

  await page.locator('#next').click();
  await page.locator('#run').click();
  await page.waitForFunction(() => document.getElementById('run-state').dataset.state === 'done');
  assert.deepEqual(await page.locator('#observation-rows td:nth-child(2)').allTextContents(), ['NaN', 'NaN', 'NaN']);
  const repaired = (await editorValue()).replace('i <= readings.length', 'i < readings.length');
  await editorFill(repaired);
  assert.match(await page.locator('#run-help').textContent(), /previous run/);
  await page.locator('#run').click();
  await page.waitForFunction(() => document.getElementById('run-state').dataset.state === 'done');
  assert.deepEqual(await page.locator('#observation-rows td:nth-child(2)').allTextContents(), ['14', '0', '3']);
  pass('debugging shows NaN, stale output, and repaired values without a score');
  await page.screenshot({path: `${evidence}/desktop-debug.png`, fullPage: true});

  await page.locator('#next').click();
  const lab = 'function mean(readings) {\n  if (readings.length === 0) return null;\n  let sum = 0;\n  for (const value of readings) sum += value;\n  return sum / readings.length;\n}\nmodule.exports = { mean };';
  await editorFill(lab);
  await page.getByRole('button', {name: 'examples.js', exact: true}).click();
  const examples = (await editorValue()) + '\nreport("negative", mean([-2, 6]), 2);\nreport("single", mean([5]), 5);';
  await editorFill(examples);
  await page.locator('#reflection').fill('null distinguishes an absent mean from a mean of zero.');
  await page.getByRole('button', {name: 'stats.js', exact: true}).click();
  assert.equal(await editorValue(), lab);
  await page.locator('#run').click();
  await page.waitForFunction(() => document.getElementById('run-state').dataset.state === 'done');
  assert.deepEqual(await page.locator('#observation-rows td:nth-child(2)').allTextContents(), ['4', 'null', '2', '5']);
  pass('two-file execution retains edits and executes learner-added examples');

  await page.locator('#activity-nav button').first().click();
  assert.equal(await page.locator('#prediction').inputValue(), '0 3\n1 7\n2 4\n3 undefined');
  assert.match(await page.locator('#reflection').inputValue(), /count is one beyond/);
  const downloadEvent = page.waitForEvent('download');
  await page.locator('#export').click();
  const download = await downloadEvent;
  const exported = await readFile(await download.path(), 'utf8');
  assert.match(exported, /unreviewed learner artifact/);
  assert.match(exported, /stats\.js/);
  assert.match(exported, /null distinguishes an absent mean/);
  assert.match(exported, /negative.*mean\(\[-2, 6\]\)/);
  pass('navigation retains separate drafts and Markdown export includes all activities');

  await page.locator('#next').click();
  await page.locator('#reset').click();
  await page.locator('#reset-cancel').click();
  assert.equal(await editorValue(), repaired);
  await page.locator('#reset').click();
  await page.locator('#reset-confirm').click();
  assert.match(await editorValue(), /i <= readings.length/);
  await page.locator('#previous').click();
  assert.match(await page.locator('#reflection').inputValue(), /count is one beyond/);
  pass('reset is confirmed and affects only the selected activity');

  await page.locator('#next').click();
  const execute = async (code, state = 'done') => {
    await editorFill(code);
    await page.locator('#run').click();
    await page.waitForFunction((value) => document.getElementById('run-state').dataset.state === value, state);
    return page.locator('#output').textContent();
  };
  assert.match(await execute('function broken( {', 'error'), /SyntaxError/);
  assert.match(await execute('console.log("recovered");'), /recovered/);
  pass('syntax errors have feedback and the next run uses a fresh worker');

  assert.match(await execute('while (true) {}', 'timeout'), /Stopped after 2 seconds/);
  assert.match(await execute('console.log("after timeout");'), /after timeout/);
  await editorFill('while (true) {}');
  await page.locator('#run').click();
  await page.locator('#stop').click();
  assert.equal(await page.locator('#run-state').textContent(), 'Stopped by you');
  assert.match(await execute('console.log("after stop");'), /after stop/);
  pass('timeout and manual stop recover with the page still usable');

  await execute('for (let i = 0; i < 100000; i++) console.log(i);', 'limit');
  assert((await page.locator('#output').textContent()).length < 20000);
  await execute('for (let i = 0; i < 100000; i++) self.postMessage({type:"log", text:"flood"});', 'limit');
  assert((await page.locator('#output').textContent()).length < 20000);
  pass('adapter and host both bound ordinary and forged output floods');

  const blocked = await execute('try { await fetch("https://example.invalid/dojo-probe"); console.log("BAD"); } catch { console.log("fetch blocked"); }\ntry { importScripts("https://example.invalid/probe.js"); console.log("BAD"); } catch { console.log("import blocked"); }\nawait new Promise((resolve) => {\n  const child = new Worker("runner.js");\n  child.onerror = (event) => { event.preventDefault(); console.log("worker blocked"); resolve(); };\n  child.onmessage = () => { console.log("BAD"); resolve(); };\n  child.postMessage({files: {"probe.js": "console.log(1)"}, entry: "probe.js"});\n});\nconsole.log(typeof document, typeof process);');
  assert.match(blocked, /fetch blocked/);
  assert.match(blocked, /import blocked/);
  assert.match(blocked, /worker blocked/);
  assert.match(blocked, /undefined undefined/);
  assert(!blocked.includes('BAD'));
  assert.match(await execute('try { require("../../runtime.py"); } catch (error) { console.log(error.message); }'), /Only provided files/);
  assert.match(await execute('console.log("<img src=x onerror=alert(1)>");'), /<img/);
  assert.equal(await page.locator('#output img').count(), 0);
  pass('CSP blocks network, imports and nested workers, and output remains text');

  assert.equal((await fetch(`${origin}/../../runtime.py`)).status, 404);
  assert.equal((await fetch(`${origin}/source.md?path=runtime.py`)).status, 404);
  const foreignHostStatus = await new Promise((resolve, reject) => {
    const req = request(origin, {headers: {Host: 'attacker.invalid'}}, (res) => { res.resume(); resolve(res.statusCode); });
    req.on('error', reject);
    req.end();
  });
  assert.equal(foreignHostStatus, 403);
  const policy = (await fetch(`${origin}/runner.js`)).headers.get('content-security-policy');
  assert.match(policy, /connect-src 'none'/);
  assert.match(policy, /worker-src 'none'/);
  assert.equal((await fetch(`${origin}/`, {method: 'POST', body: 'no writes'})).status, 501);
  pass('dedicated server refuses unknown paths, foreign hosts and writes');

  await editorFill('x'.repeat(30001));
  await page.locator('#run').click();
  assert.equal(await page.locator('#run-state').textContent(), 'File too large');
  await page.reload();
  assert.equal(await page.locator('#prediction').inputValue(), '0 3\n1 7\n2 4\n3 undefined');
  assert.match(await page.locator('#reflection').inputValue(), /count is one beyond/);
  await page.locator('#activity-nav button').nth(2).click();
  assert.equal(await editorValue(), lab);
  assert.equal(await page.evaluate(() => localStorage.length), 1);
  pass('file limits refuse oversized code and reload restores local drafts without run results');

  await page.locator('#activity-nav button').nth(3).click();
  assert.equal(await page.locator('#language-label').textContent(), 'Python');
  await page.locator('#run').click();
  await page.waitForFunction(() => document.getElementById('run-state').dataset.state === 'error', {timeout: 30000});
  assert.match(await page.locator('#output').textContent(), /IndexError/);
  const pythonFixed = (await editorValue()).replace('range(len(readings) + 1)', 'range(len(readings))') + '\nreport("single", total([5]), 5)';
  await editorFill(pythonFixed);
  await page.locator('#run').click();
  await page.waitForFunction(() => document.getElementById('run-state').dataset.state === 'done', {timeout: 30000});
  assert.deepEqual(await page.locator('#observation-rows td:nth-child(2)').allTextContents(), ['14', '0', '3', '5']);
  pass('local Python worker reports an index error, then runs the repaired public examples');
  await editorFill('while True:\n    pass');
  await page.locator('#run').click();
  await page.waitForFunction(() => document.getElementById('run-state').dataset.state === 'timeout');
  await editorFill('for i in range(10000):\n    print(i)');
  await page.locator('#run').click();
  await page.waitForFunction(() => document.getElementById('run-state').dataset.state === 'limit');
  await editorFill(pythonFixed);
  await page.locator('#run').click();
  await page.waitForFunction(() => document.getElementById('run-state').dataset.state === 'done');
  pass('Python timeout and output limit replace the worker and allow a fresh run');

  await page.setViewportSize({width: 390, height: 844});
  for (let i = 0; i < 4; i++) {
    await page.locator('#activity-nav button').nth(i).click();
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    assert(await page.locator('#editor-mount .cm-editor').isVisible());
  }
  await page.screenshot({path: `${evidence}/mobile-lab.png`, fullPage: true});
  await page.emulateMedia({reducedMotion: 'reduce', forcedColors: 'active'});
  assert(await page.locator('#run').isVisible());
  pass('all activities fit a 390px viewport with reduced-motion and forced-color controls');

  const offline = await browser.newContext({offline: true});
  const staticPage = await offline.newPage();
  await staticPage.goto(new URL('index.html', import.meta.url).href);
  assert(await staticPage.locator('#activity-title').isVisible());
  await staticPage.locator('#prediction').fill('A static prediction');
  await staticPage.locator('#run').click();
  await staticPage.waitForFunction(() => document.getElementById('run-state').dataset.state === 'unavailable');
  assert(await staticPage.locator('#export').isEnabled());
  await offline.close();
  assert.deepEqual(errors, []);
  assert.deepEqual(unexpectedRequests, []);
  pass('direct-file fallback declares unavailable execution and keeps reading/export usable');
  console.log(`${checks.length} checks passed. Screenshots: ${evidence}`);
} finally {
  await browser?.close();
  lines.close();
  server.kill('SIGTERM');
  await once(server, 'exit');
}
