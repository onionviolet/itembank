import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile, mkdir, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const {chromium} = await import(process.env.ITEMBANK_PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(fileURLToPath(new URL('.', import.meta.url)));
const fontRoot = path.resolve(root, '../../../fonts');
const server = createServer(async (req, res) => {
  try {
    const pathname = decodeURIComponent(new URL(req.url, 'http://local').pathname);
    const isFont = pathname.startsWith('/assets/fonts/');
    const base = isFont ? fontRoot : root;
    const relative = isFont ? pathname.slice('/assets/fonts/'.length) : pathname.slice(1);
    const file = path.resolve(base, relative || 'workshop-light.html');
    if (!file.startsWith(base + path.sep)) throw new Error('outside preview root');
    res.setHeader('Content-Type', isFont ? 'font/woff2' : 'text/html; charset=utf-8');
    res.end(await readFile(file));
  } catch { res.writeHead(404); res.end('Preview file unavailable'); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
const evidence = process.env.ITEMBANK_VISUAL_EVIDENCE || path.join(root, 'observed');
await mkdir(evidence, {recursive:true});
let browser;
const observations = [];
try {
  browser = await chromium.launch({executablePath:process.env.ITEMBANK_CHROMIUM,headless:true});
  for (const file of ['quiet-light','workshop-light','quiet-dark','workshop-dark','workshop-custom']) {
    for (const width of [1440,1024,768,390,320]) {
      const page = await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});
      const errors=[]; page.on('pageerror',error=>errors.push(error.message));
      await page.goto(`${origin}/${file}.html`);
      await page.evaluate(()=>document.fonts.ready);
      const metrics = await page.evaluate(()=>{
        const box=element=>{ const r=element.getBoundingClientRect();return {width:r.width,height:r.height,x:r.x,y:r.y};};
        const nav=document.querySelector('.product-sidebar');
        const source=document.querySelector('.overhaul-source');
        const note=document.querySelector('.overhaul-notes');
        return {overflow:document.documentElement.scrollWidth-innerWidth,nav:box(nav),source:box(source),note:box(note),
          controls:[...document.querySelectorAll('.product-nav a,.go,.overhaul-response label')].map(box),
          scheme:getComputedStyle(document.documentElement).colorScheme,
          motion:getComputedStyle(document.querySelector('.go')).transitionDuration};
      });
      assert(metrics.overflow<=1, `${file} ${width} overflows by ${metrics.overflow}px`);
      assert(metrics.controls.every(control=>control.height>=44), 'touch target below 44px');
      if(width>=768) assert(metrics.nav.height<100,'desktop frame consumes too much height');
      if(width<768) assert(metrics.note.y>metrics.source.y,'notes must follow source at narrow width');
      if(file.includes('dark')) assert.equal(metrics.scheme,'dark');
      assert(metrics.motion.split(',').every(value=>parseFloat(value)===0),'reduced motion not honored');
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(()=>getComputedStyle(document.activeElement).outlineStyle),'solid');
      await page.getByLabel('What would you check next?').fill('A synthetic draft remains while the layout resizes.');
      await page.setViewportSize({width:width===390?1440:390,height:1000});
      assert.equal(await page.getByLabel('What would you check next?').inputValue(),'A synthetic draft remains while the layout resizes.');
      await page.setViewportSize({width,height:1000});
      await page.evaluate(()=>{document.activeElement.blur();window.scrollTo(0,0);});
      await page.waitForTimeout(100);
      assert.equal(errors.length,0);
      await page.screenshot({path:path.join(evidence,`${file}-${width}.png`),fullPage:true});
      observations.push({file,width,...metrics});
      await page.close();
    }
  }
  const nojs=await browser.newPage({viewport:{width:390,height:1000},javaScriptEnabled:false});
  await nojs.goto(`${origin}/workshop-light.html`);
  assert(await nojs.locator('noscript').isVisible());
  await nojs.getByText('Review the source',{exact:true}).click();
  assert(await nojs.getByText('Return to the observation',{exact:true}).isVisible());
  await nojs.screenshot({path:path.join(evidence,'workshop-no-script-390.png'),fullPage:true});
  // Long headings and prose must wrap, without hiding or clipping meaningful text.
  const long=await browser.newPage({viewport:{width:390,height:1000}});
  await long.goto(`${origin}/workshop-light.html`);
  await long.evaluate(()=>{
    document.querySelector('h1').textContent='Long synthetic course: 观察、解释、and carefully checking a claim '.repeat(8);
    document.querySelector('.overhaul-prose p').textContent='SyntheticCitationWithoutSpaces'.repeat(35);
  });
  assert(await long.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await long.screenshot({path:path.join(evidence,'workshop-long-390.png'),fullPage:true});
  await writeFile(path.join(evidence,'metrics.json'),JSON.stringify(observations,null,2));
  console.log(`PASS ${observations.length} comparison renders, keyboard focus, 44px targets, reflow, reduced motion, resize-safe inputs, no-script disclosure and long content`);
} finally { if(browser)await browser.close();await new Promise(resolve=>server.close(resolve)); }
