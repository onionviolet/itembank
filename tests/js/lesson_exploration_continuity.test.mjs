import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {JSDOM} from 'jsdom';
import {python} from './python_bin.mjs';

const fixture = JSON.parse(execFileSync(python, ['-c', `
import html,json,model
from surfaces import lesson,lesson_interaction,lesson_progressive
p='tests/fixtures/exploration_lineplot.md'
print(json.dumps(dict(comparison=lesson_interaction.render(dict(a=12,b=18,max=24,unit='mm',text='Original synthetic comparison.'),html.escape),
lineplot=lesson_interaction.render_lineplot(dict(m=1,b=0,changed_b=2,text='Prediction: Which points move? Static explanation: Every point rises by two. Transfer: try a falling line.'),html.escape),
comparison_js=lesson_interaction.JS,lineplot_js=lesson_interaction.LINEPLOT_JS,
guided=lesson.lesson_page(p,model.load(p),model.parse_lesson(p),runtime=True,mode='guided',exploration_context=dict(lesson_id='lesson-1',revision_id='revision-1',occurrence_id='occurrence-1')))))
`], {cwd:new URL('../..', import.meta.url),encoding:'utf8'}));

const KEY = 'itembank:lesson-exploration:v1';
function page({kind='comparison',saved={},occurrence='occurrence-1',revision='revision-1',lesson='lesson-1',denied=false,writeDenied=false,noIdentity=false,copies=1}={}) {
  const attrs = noIdentity ? '' : `data-exploration-lesson="${lesson}" data-exploration-revision="${revision}" data-exploration-occurrence="${occurrence}"`;
  const dom = new JSDOM(`<main id="lesson-content" ${attrs}><section id="example">${fixture[kind].repeat(copies)}</section></main>`,
    {runScripts:'outside-only',url:'https://example.test/lesson/same-title-and-url'});
  for (const [key,value] of Object.entries(saved)) dom.window.sessionStorage.setItem(key,value);
  if (denied) Object.defineProperty(dom.window,'sessionStorage',{get(){throw new Error('Storage denied');}});
  else if (writeDenied) dom.window.Storage.prototype.setItem = () => {throw new Error('Quota exceeded');};
  dom.window.eval(fixture[kind+'_js'].replace(/^<script>|<\/script>$/g,''));
  return dom;
}
function storage(dom) {
  return Object.fromEntries(Array.from({length:dom.window.sessionStorage.length},(_,i) => {
    const key=dom.window.sessionStorage.key(i);return [key,dom.window.sessionStorage.getItem(key)];
  }));
}
function setNumber(dom,value,index=0) {
  const field=dom.window.document.querySelectorAll('.comparison-number')[index];
  field.value=String(value);field.dispatchEvent(new dom.window.Event('change'));return field;
}
function lineCommit(dom,prediction='all',intercept='-1') {
  const doc=dom.window.document;
  doc.querySelector('.lineplot-prediction').value=prediction;
  doc.querySelector('.lineplot-commit').click();
  const value=doc.querySelector('.lineplot-value');value.value=intercept;
  value.dispatchEvent(new dom.window.Event('change'));
}

test('committed comparison survives reconstructed document, reset clears only its block, and title/URL cannot join occurrences', () => {
  const first=page({copies:2});setNumber(first,9);setNumber(first,22,1);
  const saved=storage(first), reload=page({saved,copies:2});
  assert.deepEqual([...reload.window.document.querySelectorAll('.comparison-number')].map(n=>n.value),['9','22']);
  reload.window.document.querySelector('.comparison-reset').click();
  const reset=page({saved:storage(reload),copies:2});
  assert.deepEqual([...reset.window.document.querySelectorAll('.comparison-number')].map(n=>n.value),['18','22']);
  for (const settings of [{occurrence:'occurrence-2'},{lesson:'lesson-2'},{}, {noIdentity:true}]) {
    const isolated=page({...settings,saved:settings.noIdentity ? saved : settings.occurrence||settings.lesson ? saved : {}});
    assert.equal(isolated.window.document.querySelector('.comparison-number').value,'18');isolated.window.close();
  }
  const changed=page({saved,revision:'revision-2'});
  assert.equal(changed.window.document.querySelector('.comparison-number').value,'18');
  assert.match(changed.window.document.querySelector('.exploration-continuity').textContent,/Reading changed/);
  const oldAgain=page({saved:storage(changed)});
  assert.equal(oldAgain.window.document.querySelector('.comparison-number').value,'18','superseded state must be invalidated');
  [first,reload,reset,changed,oldAgain].forEach(dom=>dom.window.close());
});

test('storage denial, quota and corruption preserve usable controls and safe authored defaults', () => {
  for (const settings of [{denied:true},{writeDenied:true},{saved:{[KEY]:'{broken'}},
    {saved:{[KEY]:JSON.stringify({version:1,entries:[{identity:['lesson-1','occurrence-1'],revision:'revision-1',states:[['wrong',999]]}]})}}]) {
    const dom=page(settings);assert.equal(dom.window.document.querySelector('.comparison-number').value,'18');
    assert.equal(setNumber(dom,5).value,'5');
    assert.equal(dom.window.document.querySelector('.comparison-controls').hidden,false);
    if (settings.denied||settings.writeDenied) assert.match(dom.window.document.querySelector('.exploration-continuity').textContent,/unavailable/);
    dom.window.close();
  }
});

test('pointer preview is never persisted and Escape, blur, lost capture and explicit cancel retain committed state', () => {
  for (const interruption of ['escape','blur','pagehide','pointercancel','cancel']) {
    const dom=page(),doc=dom.window.document;setNumber(dom,10);
    const handle=doc.querySelector('.comparison-handle'),direct=doc.querySelector('.comparison-direct');
    direct.getBoundingClientRect=()=>({left:0,width:240,height:52});
    let captured=false;handle.setPointerCapture=()=>{captured=true;};
    handle.hasPointerCapture=()=>captured;handle.releasePointerCapture=()=>{captured=false;};
    const send=(type,x)=>{const event=new dom.window.Event(type,{bubbles:true,cancelable:true});
      Object.assign(event,{pointerId:1,isPrimary:true,button:0,clientX:x,clientY:50});handle.dispatchEvent(event);};
    send('pointerdown',100);send('pointermove',200);
    const during=page({saved:storage(dom)});assert.equal(during.window.document.querySelector('.comparison-number').value,'10');
    if(interruption==='escape') handle.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
    else if(interruption==='cancel') doc.querySelector('.comparison-cancel').click();
    else if(interruption==='pointercancel') send('pointercancel',200);
    else dom.window.dispatchEvent(new dom.window.Event(interruption));
    assert.equal(doc.querySelector('.comparison-number').value,'10');assert.equal(captured,false);
    const after=page({saved:storage(dom)});assert.equal(after.window.document.querySelector('.comparison-number').value,'10');
    [dom,during,after].forEach(view=>view.window.close());
  }
});

test('lineplot restores committed prediction/intercept, cancels unfinished prediction, and reset returns to prediction', () => {
  const first=page({kind:'lineplot'});lineCommit(first,'origin','-1');
  const reload=page({kind:'lineplot',saved:storage(first)}),doc=reload.window.document;
  assert.equal(doc.querySelector('.lineplot-prediction').value,'origin');
  assert.equal(doc.querySelector('.lineplot-value').value,'-1');
  assert.equal(doc.querySelector('.lineplot-manipulate').hidden,false);
  assert.match(doc.querySelector('.lineplot-live').textContent,/decreases by 1/);
  const prediction=doc.querySelector('.lineplot-prediction');
  for(const action of ['escape','blur','cancel']) {
    prediction.value='none';prediction.dispatchEvent(new reload.window.Event('change'));
    if(action==='escape') prediction.dispatchEvent(new reload.window.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
    else if(action==='blur') prediction.dispatchEvent(new reload.window.FocusEvent('blur'));
    else doc.querySelector('.lineplot-cancel').click();
    assert.equal(prediction.value,'origin');
  }
  doc.querySelector('.lineplot-reset').click();
  assert.equal(prediction.value,'');assert.equal(doc.querySelector('.lineplot-manipulate').hidden,true);
  const reset=page({kind:'lineplot',saved:storage(reload)});
  assert.equal(reset.window.document.querySelector('.lineplot-manipulate').hidden,true);
  [first,reload,reset].forEach(dom=>dom.window.close());
});

test('ledger is bounded, rejects out-of-range saved scalars, and never uses learner evidence/network stores', () => {
  let saved={};
  for(let i=0;i<20;i++) {const dom=page({saved,occurrence:'reading-'+i});setNumber(dom,i);saved=storage(dom);dom.window.close();}
  assert.equal(JSON.parse(saved[KEY]).entries.length,16);assert.ok(saved[KEY].length<=32768);
  const dom=page();setNumber(dom,5);const data=JSON.parse(storage(dom)[KEY]);data.entries[0].states[0][1]=999;
  const rejected=page({saved:{[KEY]:JSON.stringify(data)}});assert.equal(rejected.window.document.querySelector('.comparison-number').value,'18');
  for(const script of [fixture.comparison_js,fixture.lineplot_js]) {
    for(const forbidden of ['fetch(', 'XMLHttpRequest','localStorage','sendBeacon','innerHTML','eval(','new Function','submit(']) assert.ok(!script.includes(forbidden),forbidden);
  }
  [dom,rejected].forEach(view=>view.window.close());
});

async function guided(saved={}) {
  const dom=new JSDOM(fixture.guided,{url:'https://example.test/lesson/guided',runScripts:'dangerously',beforeParse(window){
    window.HTMLElement.prototype.scrollIntoView=function(){};
    for(const [key,value] of Object.entries(saved)) window.sessionStorage.setItem(key,value);
  }});
  await new Promise(resolve=>dom.window.addEventListener('load',resolve));return dom;
}
test('guided continuation restores only runtime-visible stage count and emphasis; start again clears that presentation',async()=>{
  const first=await guided();const button=(dom,label)=>[...dom.window.document.querySelectorAll('button')].find(node=>node.textContent===label);
  button(first,'Show all explanations').click();button(first,'Highlight key wording').click();
  const reload=await guided(storage(first));assert.equal(reload.window.document.querySelectorAll('.stage[hidden]').length,0);
  assert.equal(reload.window.document.getElementById('lesson-content').classList.contains('reading-emphasis'),true);
  button(reload,'Start again').click();const reset=await guided(storage(reload));
  assert.equal([...reset.window.document.querySelectorAll('.stage')].filter(stage=>!stage.hidden).length,1);
  assert.equal(reset.window.document.getElementById('lesson-content').classList.contains('reading-emphasis'),false);
  [first,reload,reset].forEach(dom=>dom.window.close());
});
