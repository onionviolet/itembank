// Focused rendered inspection for this synthetic prototype only.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const {chromium} = await import(process.env.ITEMBANK_PLAYWRIGHT_MODULE || 'playwright');
const root = fileURLToPath(new URL('.',import.meta.url));
const evidence = path.join(root,'observed');
await mkdir(evidence,{recursive:true});
const server = createServer(async(req,res)=>{
  try {
    const url = new URL(req.url,'http://preview');
    const file = path.resolve(root,'.'+url.pathname+(url.pathname.endsWith('/')?'index.html':''));
    if(!file.startsWith(root)) throw Error('Outside owned folder');
    const types={'.html':'text/html','.css':'text/css','.js':'text/javascript','.md':'text/plain'};
    res.setHeader('Content-Type',(types[path.extname(file)]||'application/octet-stream')+'; charset=utf-8');
    res.end(await readFile(file));
  } catch {res.writeHead(404);res.end('Unavailable');}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin=`http://127.0.0.1:${server.address().port}`;
let browser;
const observations=[];
try {
  browser=await chromium.launch({headless:true,executablePath:process.env.ITEMBANK_CHROMIUM});
  for(const width of [1440,390,320]) {
    for(const theme of ['light','dark']) {
      const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});
      const errors=[];page.on('pageerror',error=>errors.push(error.message));
      await page.goto(`${origin}/?theme=${theme}`);
      await page.screenshot({path:path.join(evidence,`${theme}-${width}-predict.png`),fullPage:true});
      await page.locator('#prediction').fill('10');
      await page.locator('#prediction').press('Enter');
      assert.equal(await page.locator('#clock').textContent(),'6 s');
      assert.equal(await page.locator('#gap-distance').textContent(),'12 m');
      assert.match(await page.locator('#prediction-result').textContent(),/Your first prediction10 m/);
      await page.locator('#graph-toggle').click();
      await page.screenshot({path:path.join(evidence,`${theme}-${width}-reveal.png`),fullPage:true});
      await page.locator('#time').focus(); await page.keyboard.press('ArrowRight');
      assert.equal(await page.locator('#clock').textContent(),'7 s');
      assert.equal(await page.locator('#gap-distance').textContent(),'14 m');
      assert.match(await page.locator('#graph-caption').textContent(),/Mira 21 m; Noor 35 m; gap 14 m/);
      await page.locator('#less').click();
      await page.locator('[data-step="1"] button').click();
      assert.equal(await page.locator('#eq-mira').textContent(),'3 m/s × 6 s = 18 m');
      await page.locator('#note').fill('In the same one second, Noor adds two more metres.');
      await page.waitForTimeout(320);
      assert.match(await page.locator('#note-status').textContent(),/saved in this browser/);
      await page.locator('#reference-open').click();
      assert.equal(await page.locator('#reference-dialog').evaluate(el=>el.open),true);
      await page.screenshot({path:path.join(evidence,`${theme}-${width}-reference.png`),fullPage:true});
      await page.keyboard.press('Escape');
      assert.equal(await page.evaluate(()=>document.activeElement.id),'reference-open');
      assert.equal(await page.locator('#clock').textContent(),'6 s');
      assert.equal(await page.locator('#note').inputValue(),'In the same one second, Noor adds two more metres.');
      await page.locator('#practice-open').click();
      await page.locator('#practice').fill('8');await page.locator('#practice').press('Enter');
      assert.match(await page.locator('#practice-feedback').textContent(),/matches the model/);
      await page.keyboard.press('Escape');
      assert.equal(await page.evaluate(()=>document.activeElement.id),'practice-open');
      assert.equal(await page.locator('#clock').textContent(),'6 s');
      await page.locator('#reset-time').click();await page.locator('#play').click();
      assert.equal(await page.locator('#clock').textContent(),'6 s');
      const metrics=await page.evaluate(()=>({
        overflow:document.documentElement.scrollWidth-innerWidth,
        theme:document.documentElement.dataset.theme,
        buttons:[...document.querySelectorAll('main button,header button')].filter(el=>el.getClientRects().length).map(el=>({name:el.textContent.trim(),height:el.getBoundingClientRect().height})),
        focusStyle:getComputedStyle(document.activeElement).outlineStyle
      }));
      assert(metrics.overflow<=1,`Overflow ${theme}/${width}: ${metrics.overflow}`);
      assert(metrics.buttons.every(el=>el.height>=44),'Control height below 44px');
      assert.equal(errors.length,0,errors.join('\n'));
      observations.push({width,theme,...metrics,journey:'prediction > reveal > clock keyboard > worked step > note > reference > practice > return',errors});
      await page.reload();
      assert.equal(await page.locator('#note').inputValue(),'In the same one second, Noor adds two more metres.');
      assert.match(await page.locator('#note-status').textContent(),/restored/);
      await page.close();
    }
  }
  const staticPage=await browser.newPage({viewport:{width:390,height:1000},javaScriptEnabled:false});
  await staticPage.goto(origin);
  assert.equal(await staticPage.locator('#static-core').getAttribute('open'),'');
  assert.match(await staticPage.locator('#step-3').textContent(),/30 m − 18 m = 12 m/);
  assert.equal(await staticPage.locator('#controls').isVisible(),false);
  await staticPage.screenshot({path:path.join(evidence,'no-javascript-390.png'),fullPage:true});
  observations.push({staticMeaning:'visible without JavaScript',width:390});
  const storageFailure=await browser.newPage({viewport:{width:390,height:1000}});
  await storageFailure.addInitScript(()=>{Storage.prototype.setItem=function(){throw Error('synthetic storage failure');};});
  await storageFailure.goto(origin);await storageFailure.locator('#note').fill('A synthetic unsaved note');
  await storageFailure.waitForTimeout(320);
  assert.match(await storageFailure.locator('#note-status').textContent(),/Not saved/);
  observations.push({storageFailure:'honest unsaved notice observed'});
  const animationPage=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'no-preference'});
  await animationPage.goto(origin);await animationPage.locator('#prediction').fill('12');await animationPage.locator('#prediction').press('Enter');
  await animationPage.locator('#play').click();await animationPage.waitForTimeout(750);
  assert.equal(await animationPage.locator('#play').textContent(),'Pause demonstration');
  await animationPage.locator('#play').click();const stopped=await animationPage.locator('#clock').textContent();
  await animationPage.waitForTimeout(650);assert.equal(await animationPage.locator('#clock').textContent(),stopped);
  observations.push({motion:'play/pause stops clock; reduced motion reaches final state immediately'});
  await writeFile(path.join(evidence,'inspection.json'),JSON.stringify({date:'2026-09-30',browser:'Chrome through Playwright',observations},null,2)+'\n');
  console.log(`READY: ${observations.length} focused observations, rendered screenshots in owned observed folder.`);
} finally {await browser?.close();await new Promise(resolve=>server.close(resolve));}
