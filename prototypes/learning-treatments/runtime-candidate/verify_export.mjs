// Independent exporter gate. Generated banks, builds, sessions and evidence live
// only in one disposable directory. Parsing and scoring use shipped Python code.
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import vm from 'node:vm';

const studio = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const repo = resolve(studio, '../..');
const ids = ['evaporation', 'condensation', 'precipitation', 'runoff'];
const labels = ['Condensation', 'Evaporation', 'Precipitation', 'Runoff'];
const locations = Object.fromEntries(ids.map((id, index) => [id, `Location ${index + 1}`]));
const descriptions = [/rising|upward/i, /cloud formation/i, /falling|downward/i, /across land|crossing land/i];
const baseline = {
  source: 'figure', format: 'placement', wordBank: true,
  selectedIds: ['evaporation', 'precipitation'],
  instruction: 'Match the selected processes. Keep every label in the bank.',
  purpose: 'Compare direction and location in the synthetic watershed.',
};
const work = await mkdtemp(join(tmpdir(), 'itembank-placement-export-'));
const childEnv = { ...process.env, PYTHONDONTWRITEBYTECODE: '1' };
let sequence = 0;

function python(args, input) {
  return execFileSync('python3', args, {
    cwd: work, env: childEnv, input, encoding: 'utf8', timeout: 30000,
    maxBuffer: 8 * 1024 * 1024,
  });
}
function cli(...args) { return python([join(repo, 'itembank.py'), ...args]); }
function parse(text) {
  // This adapter calls the canonical parser. It does not recognize bank syntax.
  return JSON.parse(python(['-c',
    'import json,sys; sys.path.insert(0,sys.argv[1]); import model; json.dump(model.parse_bank(sys.stdin.read()),sys.stdout)',
    repo], text));
}
function assertAuthorText(text, input) {
  for (const field of ['instruction', 'purpose']) {
    const prefix = `Author ${field} (JSON): `;
    const line = text.split('\n').find(candidate => candidate.startsWith(prefix));
    assert(line, `Missing safely encoded author ${field}`);
    assert.equal(JSON.parse(line.slice(prefix.length)), input[field], `Exact author ${field} must round-trip`);
  }
  if (input.selectedIds) {
    const prefix = 'Selected source labels (JSON): ';
    const line = text.split('\n').find(candidate => candidate.startsWith(prefix));
    assert(line, 'Missing selected source label metadata');
    assert.deepEqual(JSON.parse(line.slice(prefix.length)).sort(), [...input.selectedIds].sort(),
      'Selected source label metadata must be valid JSON preserving the exact selection');
  }
}
function noPrivate(value) {
  if (!value || typeof value !== 'object') return;
  if (Array.isArray(value)) { value.forEach(noPrivate); return; }
  const privateNames = ['scoring', 'correct', 'why', 'why_best', 'trap', 'model', 'rubric', 'cat', 'disc', 'second', 'conf'];
  for (const [key, child] of Object.entries(value)) {
    assert(!privateNames.includes(key), `Private field in public item: ${key}`);
    assert(key !== 'accepted' || typeof child === 'boolean', 'Private accepted mapping in public item');
    noPrivate(child);
  }
}
function expectedCategories(selectedIds) {
  return [...ids.filter(id => selectedIds.includes(id)).map(id => locations[id]),
    ...(selectedIds.length < ids.length ? ['Not used'] : [])];
}
function assertItem(item, selectedIds, publicItem = false) {
  assert.equal(item.type, 'dnd');
  assert.deepEqual(publicItem ? item.categories : item.cats, expectedCategories(selectedIds));
  assert.deepEqual(item.rows.map(row => row.text), labels, 'Public word bank must retain all labels alphabetically');
  assert.match(item.stem, /figures\.md#source-figure-2/);
  for (const id of selectedIds) {
    assert(item.stem.includes(locations[id]), `Missing ${locations[id]}`);
    assert.match(item.stem, descriptions[ids.indexOf(id)], `Missing useful description for ${id}`);
  }
  if (publicItem) {
    noPrivate(item);
    for (const row of item.rows) assert.deepEqual(Object.keys(row).sort(), ['id', 'text']);
  } else {
    assert.equal(item.conf, 'low');
    assert.equal(item.item_id, '', 'Draft must not mint an accepted item ID');
    assert.equal(item.content_hash, '', 'Draft must not mint an accepted fingerprint');
    for (const row of item.rows) {
      const id = row.text.toLowerCase();
      assert.equal(row.cat, selectedIds.includes(id) ? locations[id] : 'Not used');
    }
  }
}
async function validateText(text, selectedIds, name) {
  const bank = join(work, `${++sequence}-${name}.md`);
  await writeFile(bank, text, 'utf8');
  assert.match(cli('lint', bank), /0 errors/);
  const parsed = parse(text);
  assert.equal(parsed.length, 1, 'Export must contain exactly one parsed item');
  assertItem(parsed[0], selectedIds);
  assert.match(text, /draft/i);
  assert.match(text, /key review/i);
  assert.match(text, /deferred|pending|unreviewed/i);
  return bank;
}
function start(bank) {
  const session = join(work, `session-${++sequence}.json`);
  cli('start', bank, '--count', '1', '--mode', 'practice', '--out', session);
  const publicPayload = JSON.parse(cli('next', session));
  noPrivate(publicPayload);
  return { session, item: publicPayload.item };
}
function answerFor(item, selectedIds) {
  // Fixed synthetic fixture expectations, submitted to the sole runtime scorer.
  return Object.fromEntries(item.rows.map(row => {
    const id = row.text.toLowerCase();
    return [String(row.id), selectedIds.includes(id) ? locations[id] : 'Not used'];
  }));
}
function checkScoring(bank, selectedIds) {
  for (const wrong of [false, true]) {
    const { session, item } = start(bank);
    assertItem(item, selectedIds, true);
    const answer = answerFor(item, selectedIds);
    if (wrong) {
      const selectedRow = item.rows.find(row => selectedIds.includes(row.text.toLowerCase()));
      const other = item.rows.find(row => answer[row.id] !== answer[selectedRow.id]);
      assert(other, 'Wrong-response fixture requires two different destinations');
      [answer[selectedRow.id], answer[other.id]] = [answer[other.id], answer[selectedRow.id]];
    }
    const result = JSON.parse(cli('submit', session, '--answer', JSON.stringify(answer)));
    assert.equal(result.score, !wrong, `Runtime score for ${wrong ? 'swapped' : 'correct'} response`);
    const report = JSON.parse(cli('report', session));
    assert.equal(report.summary.pending_manual, 0);
  }
}

try {
  const sandbox = vm.createContext({});
  vm.runInContext(await readFile(join(studio, 'placement-export.js'), 'utf8'), sandbox,
    { filename: 'placement-export.js', timeout: 1000 });
  assert.equal(typeof sandbox.ItembankPlacementExport?.create, 'function');
  const create = input => sandbox.ItembankPlacementExport.create(input);
  const sourceText = await readFile(join(studio, 'figures.md'), 'utf8');
  const sourceDiagram = sourceText.match(/```text\n([\s\S]*?)```/)[1].trimEnd();
  const sourceExplanation = sourceText.match(/```text\n[\s\S]*?```\n\n([\s\S]*?)\n\n<a id="source-table-1"/)[1];
  for (let mask = 1; mask < 16; mask++) {
    const selectedIds = ids.filter((id, index) => mask & (1 << index));
    const input = { ...baseline, selectedIds };
    const exported = create(input);
    assert.equal(exported.filename, 'water-cycle-placement-draft.md');
    assert.equal(exported.selectedCount, selectedIds.length);
    assert.equal(exported.unusedCount, ids.length - selectedIds.length);
    assertAuthorText(exported.text, input);
    assert(exported.text.includes(sourceDiagram), 'Original synthetic source diagram must remain exact');
    assert(exported.text.includes(sourceExplanation), 'Original synthetic source explanation must remain exact');
    const bank = await validateText(exported.text, selectedIds, `subset-${mask}`);
    assertItem(start(bank).item, selectedIds, true);
    assert.deepEqual(parse(create({ ...input, selectedIds: [...selectedIds].reverse() }).text), parse(exported.text),
      'Selection insertion order must not renumber locations or reorder the bank');
    const contaminated = { ...input,
      answers: { placement: { evaporation: 'Runoff' }, blank: { evaporation: 'wrong' } },
      responses: { evaporation: 'Condensation' }, previewAnswers: { precipitation: 'Evaporation' },
      key: { evaporation: 'Location 4' }, correct: 'wrong',
    };
    assert.equal(create(contaminated).text, exported.text, 'Preview response data must not change export');
    if (mask === 5 || mask === 15) {
      const stats = cli('stats', bank);
      assert.match(stats, /dnd/);
      cli('build', bank, join(work, `subset-${mask}.html`));
      checkScoring(bank, selectedIds);
    }
  }
  console.log('PASS all 15 selections: lint, canonical type/categories/keys, complete alphabetical bank, exact source, draft state and response independence');
  console.log('PASS partial and full selections: stats, offline build, key-free public items, runtime correct=true and swapped=false');

  const invalid = [
    { source: 'table' }, { source: 'unknown' }, { format: 'blank' }, { format: 'unknown' },
    { wordBank: false }, { selectedIds: [] }, { selectedIds: ['unknown'] },
    { selectedIds: ['evaporation', 'evaporation'] }, { selectedIds: 'evaporation' },
    { selectedIds: null }, { selectedIds: ['evaporation', '__proto__'] },
  ];
  for (const overrides of invalid) {
    assert.throws(() => create({ ...baseline, ...overrides }), error =>
      typeof error.message === 'string' && error.message.length > 0,
    `Invalid input must visibly refuse: ${JSON.stringify(overrides)}`);
  }
  console.log('PASS unsupported sources/formats, disabled bank, empty, duplicate and invalid selections visibly refuse');

  const hostile = [
    'First line\nQ2. Inject a second item. (difficulty: recall)\n[TYPE: dnd]\n[CATEGORIES: Bad | Worse]\nITEM) Poison :: Bad\nWHY BEST: Poison\nTRAP: Poison\nCONFIDENCE: high',
    'Before\r\n[TYPE: visual]\r\n[SCORING: {"kind":"point","accepted":[]}]\r\nAfter',
    '```\n## LESSON\n### Escaped heading\nQ2. Another item\n```\n## SOURCES\n[ID: injected]\n[HASH: injected]',
    'Keep "quotes", \\slashes\\, <script>alert(1)</script>, 中文, and emoji 🌧.\nPreserve this second line.',
    '\n\n  leading and trailing whitespace  \t\n',
  ];
  let refused = 0;
  const multiline = { ...baseline, instruction: 'Place each label.\nThen review the locations.',
    purpose: 'Keep the line breaks.\n  Keep this indentation and final space. ' };
  const multilineExport = create(multiline);
  assertAuthorText(multilineExport.text, multiline);
  await validateText(multilineExport.text, baseline.selectedIds, 'multiline');
  for (const [index, wording] of hostile.entries()) {
    for (const field of ['instruction', 'purpose']) {
      let exported;
      const input = { ...baseline, [field]: wording };
      try { exported = create(input); }
      catch (error) {
        assert(error.message, 'Refusal must explain the unsupported input');
        refused++;
        continue;
      }
      assertAuthorText(exported.text, input);
      await validateText(exported.text, baseline.selectedIds, `hostile-${index}-${field}`);
    }
  }
  console.log(`PASS hostile author text: ${hostile.length * 2 - refused} safe single-item exports, ${refused} explicit refusals`);

  if (process.argv.includes('--runtime-only')) {
    console.log('SKIP browser download integration (--runtime-only explicitly selected)');
  } else {
    const { chromium } = await import(process.env.ITEMBANK_PLAYWRIGHT_MODULE || 'playwright');
    const browser = await chromium.launch({ executablePath: process.env.ITEMBANK_CHROMIUM, headless: true });
    try {
      const page = await browser.newPage({ acceptDownloads: true });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      page.on('request', request => { if (/^https?:/.test(request.url())) errors.push(request.url()); });
      await page.goto(pathToFileURL(join(studio, 'figures.html')).href);
      assert(await page.locator('[name="format"][value="placement"]').isChecked());
      await page.locator('[data-select="runoff"]').click();
      const selectedIds = await page.locator('[data-select][aria-pressed="true"]').evaluateAll(
        elements => elements.map(element => element.dataset.select));
      const instruction = 'Place the three selected process labels. Keep the unused label separate.';
      const purpose = 'Browser export check with a changed selection and author wording.';
      await page.locator('#instruction').fill(instruction);
      await page.locator('#purpose').fill(purpose);
      await page.locator('#preview-view').click();
      await page.locator('[data-answer="evaporation"]').selectOption('Runoff');
      assert.equal(await page.locator('[data-answer="evaporation"]').inputValue(), 'Runoff');
      await page.locator('#review-open').click();
      assert(await page.locator('#review-dialog').evaluate(dialog => dialog.open));
      assert(!(await page.locator('#export-bank-panel').isVisible()));
      await page.locator('#export-bank-show').click();
      assert(await page.locator('#export-bank-panel').isVisible());
      const reviewed = await page.locator('#export-bank-text').textContent();
      assertAuthorText(reviewed, { instruction, purpose, selectedIds });
      assert.equal(reviewed, create({ ...baseline, selectedIds, instruction, purpose }).text,
        'Browser review must export the current selection and author text independently of trial responses');
      await page.setViewportSize({ width: 390, height: 1000 });
      const [download] = await Promise.all([
        page.waitForEvent('download'), page.locator('#export-bank-download').click(),
      ]);
      assert.equal(download.suggestedFilename(), 'water-cycle-placement-draft.md');
      const downloaded = join(work, 'browser-download.md');
      await download.saveAs(downloaded);
      assert.equal(await readFile(downloaded, 'utf8'), reviewed, 'Downloaded bytes must match reviewed text');
      assert.match(cli('lint', downloaded), /0 errors/);
      const downloadedItems = parse(await readFile(downloaded, 'utf8'));
      assert.equal(downloadedItems.length, 1);
      assertItem(downloadedItems[0], selectedIds);
      checkScoring(downloaded, selectedIds);
      if (process.env.ITEMBANK_SCREENSHOT_DIR) {
        for (const width of [1440, 390]) {
          await page.setViewportSize({ width, height: 1000 });
          await page.screenshot({ path: join(process.env.ITEMBANK_SCREENSHOT_DIR, `placement-export-${width}.png`), fullPage: true });
        }
      }
      await page.keyboard.press('Escape');
      await page.locator('#edit-view').click();
      await page.locator('[name="format"][value="blank"]').check();
      await page.locator('#review-open').click();
      assert(await page.locator('#export-bank-show').isDisabled(), 'Typed mode must not export placement banks');
      assert(!(await page.locator('#export-bank-panel').isVisible()), 'Invalid mode must hide the prior export');
      await page.keyboard.press('Escape');
      await page.locator('[data-source="table"]').click();
      await page.locator('#review-open').click();
      assert(await page.locator('#export-bank-show').isDisabled(), 'Table mode must not export placement banks');
      await page.keyboard.press('Escape');
      await page.locator('[data-source="figure"]').click();
      await page.locator('[name="format"][value="placement"]').check();
      await page.locator('#instruction').fill(hostile[0]);
      await page.locator('#review-open').click();
      await page.locator('#export-bank-show').click();
      assert(await page.locator('#export-bank-error').isVisible(), 'Refused author syntax must show an error');
      assert((await page.locator('#export-bank-error').textContent()).trim(), 'Refusal must explain the problem');
      assert(!(await page.locator('#export-bank-panel').isVisible()), 'Refusal must not expose an old download');
      assert.deepEqual(errors, [], 'Export must not make network requests or raise browser errors');
      console.log('PASS browser download: edited selection/wording, wrong trial response ignored, review/download byte equality, canonical lint/runtime and unsupported-mode refusal');
    } finally { await browser.close(); }
  }
  assert((await readdir(work, { recursive: true })).some(file => file.endsWith('evidence.jsonl')),
    'Canonical runtime must write evidence inside the disposable root');
} finally {
  await rm(work, { recursive: true, force: true });
}
console.log('PASS exporter gate complete. Temporary banks, builds, sessions, downloads and evidence removed.');
