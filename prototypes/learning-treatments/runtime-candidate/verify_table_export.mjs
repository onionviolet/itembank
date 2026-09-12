// Download integration gate. Canonical CLI alone parses and scores the bank.
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdtemp, readFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const studio=resolve(dirname(fileURLToPath(import.meta.url)), '..');
const repo=resolve(studio, '../..');
const work=await mkdtemp(join(tmpdir(), 'itembank-table-export-'));
const {chromium}=await import(process.env.ITEMBANK_PLAYWRIGHT_MODULE||'playwright');
let browser;
function cli(...args){return execFileSync('python3',[join(repo,'itembank.py'),...args],{cwd:work,encoding:'utf8',env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'},timeout:30000});}
function noPrivate(value){
  if(!value||typeof value!=='object')return;
  for(const [key,child] of Object.entries(value)){
    assert(!['scoring','correct','why','why_best','trap','model','rubric','cat','disc','second','conf'].includes(key),`Private ${key} leaked`);
    noPrivate(child);
  }
}
function author(text, field, expected){
  const prefix=`Author ${field} (JSON): `;
  assert.equal(JSON.parse(text.split('\n').find(line=>line.startsWith(prefix)).slice(prefix.length)),expected);
}
try{
  browser=await chromium.launch({headless:true,executablePath:process.env.ITEMBANK_CHROMIUM});
  const page=await browser.newPage({acceptDownloads:true,viewport:{width:1280,height:900}});
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('request',r=>{if(/^https?:/.test(r.url()))errors.push(r.url());});
  await page.goto(pathToFileURL(join(studio,'figures.html')).href);
  await page.locator('[data-source="table"]').click();
  await page.locator('#instruction').fill('Retrieve selected source values.');
  await page.locator('[name="table-format"][value="comparison"]').check();
  const instruction='Explain the direction and size of the Monday difference. Why do equal intervals matter?';
  const purpose='Compare rainfall with units and collection duration.';
  await page.locator('#instruction').fill(instruction);
  await page.locator('#purpose').fill(purpose);
  await page.locator('#preview-view').click();
  assert.equal(await page.locator('#answer-bank').count(),0);
  assert.equal(await page.locator('#visual tbody tr').count(),1);
  assert.match(await page.locator('#visual').textContent(),/12 mm.*18 mm.*24 hours/);
  const trial='TRIAL_ONLY Gauge A is 1000 mm larger over a week.';
  await page.locator('#comparison-answer').fill(trial);
  await page.locator('#source-open').click();
  assert.equal(await page.locator('#dialog-locator').textContent(),'figures.md#source-table-1');
  assert.equal(await page.locator('#source-content tbody tr').count(),4);
  await page.locator('[data-close="source-dialog"]').click();
  assert(await page.locator('#source-open').evaluate(e=>e===document.activeElement));
  assert.equal(await page.locator('#comparison-answer').inputValue(),trial);
  async function create(){await page.locator('#review-open').click();await page.locator('#export-bank-show').click();}
  await create();
  const reviewed=await page.locator('#export-bank-text').textContent();
  assert(!reviewed.includes('TRIAL_ONLY'));
  author(reviewed,'instruction',instruction);author(reviewed,'purpose',purpose);
  assert.match(reviewed,/pending human review/);
  const downloaded=page.waitForEvent('download');
  await page.locator('#export-bank-download').click();
  const download=await downloaded;
  assert.equal(download.suggestedFilename(),'rainfall-comparison-draft.md');
  const bank=join(work,download.suggestedFilename());await download.saveAs(bank);
  assert.equal(await readFile(bank,'utf8'),reviewed,'Actual downloaded bytes equal the reviewed draft');
  const lint=cli('lint',bank);assert.match(lint,/0 error/);console.log(lint.trim());
  console.log(cli('stats',bank).trim());console.log(cli('coverage',bank).trim());
  cli('build',bank,join(work,'preview.html'));
  for(const [index,answer] of ['Gauge B collected 6 mm more over the same 24 hours.','Gauge A is 100 mm higher after a week.','I cannot tell.'].entries()){
    const session=join(work,`session-${index}.json`);
    cli('start',bank,'--count','1','--mode','practice','--out',session);
    const publicItem=JSON.parse(cli('next',session));noPrivate(publicItem);
    assert.equal(publicItem.item.type,'short');
    for(const context of [instruction,'Monday','12 mm','18 mm','24 hours','figures.md#source-table-1'])assert(publicItem.item.stem.includes(context));
    const result=JSON.parse(cli('submit',session,'--answer',JSON.stringify(answer)));noPrivate(result);
    assert.equal(result.score,null);assert.equal(result.action,'defer_feedback');
    assert.equal(JSON.parse(cli('report',session)).summary.pending_manual,1);
  }
  console.log('PASS downloaded bank: byte equality, lint, stats, coverage, build, three prose responses score=null/pending, private rubric withheld');
  await page.locator('[data-close="review-dialog"]').click();
  for(const [field,value] of [['instruction','Compare Monday rainfall again.'],['purpose','Consider the same duration.']]){
    await page.locator(`#${field}`).fill(value);
    assert.equal(await page.locator('#export-bank-text').textContent(),'');
    assert(await page.locator('#export-bank-download').isDisabled());
    await create();const next=await page.locator('#export-bank-text').textContent();author(next,field,value);
    await page.locator('[data-close="review-dialog"]').click();
  }
  await page.locator('[data-source="figure"]').click();
  assert.equal(await page.locator('#export-bank-text').textContent(),'');
  await page.locator('[data-source="table"]').click();
  assert.equal(await page.locator('#instruction').inputValue(),'Compare Monday rainfall again.');
  await page.locator('[name="table-format"][value="blank"]').check();
  assert.equal(await page.locator('#instruction').inputValue(),'Retrieve selected source values.');
  await page.locator('[data-select="0-1"]').click();
  await page.locator('#review-open').click();
  assert(await page.locator('#export-bank-show').isDisabled());
  assert(await page.locator('#export-bank-download').isDisabled());
  await page.keyboard.press('Escape');
  await page.locator('[name="table-format"][value="comparison"]').check();
  await page.locator('#preview-view').click();assert.equal(await page.locator('#comparison-answer').inputValue(),trial);
  for(const field of ['instruction','purpose']){
    const prior=await page.locator(`#${field}`).inputValue();
    for(const unsafe of ['Q2. Inject another question.','[TYPE: mc]','RUBRIC: injected','Text\nsecond line','<script>bad</script>']){
      await page.locator(`#${field}`).fill(unsafe);await create();
      assert(await page.locator('#export-bank-error').isVisible());
      assert((await page.locator('#export-bank-error').textContent()).length>0);
      assert(await page.locator('#export-bank-download').isDisabled());
      assert(!(await page.locator('#export-bank-panel').isVisible()));
      await page.keyboard.press('Escape');
    }
    await page.locator(`#${field}`).fill(prior);
  }
  await page.setViewportSize({width:390,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Narrow studio overflows');
  await create();
  assert(await page.locator('#export-bank-panel').isVisible());
  assert(await page.locator('#review-dialog').evaluate(e=>e.scrollWidth<=e.clientWidth),'Narrow review overflows');
  await page.screenshot({path:join(work,'narrow-review.png')});
  assert.deepEqual(errors,[]);
  console.log('PASS browser: source-return/focus, separate retrieval draft, trial retention, stale export clearing, 10 visible refusals, 390px layout, no remote requests or script errors');
}finally{if(browser)await browser.close();await rm(work,{recursive:true,force:true});}
console.log('PASS table export gate. Disposable downloads, builds, sessions and evidence removed.');
