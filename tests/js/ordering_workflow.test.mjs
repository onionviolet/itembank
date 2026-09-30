import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {JSDOM} from 'jsdom';
import {python} from './python_bin.mjs';

const fixture=JSON.parse(execFileSync(python,['-c',`
import copy, json, runpy, model, runtime
from surfaces import quiz_page
qs=model.parse_bank(runpy.run_path('tests/ordering_workflow_roundtrip.py')['authored_text']())
items=[runtime.public_item(q) for q in qs]
revised=copy.deepcopy(qs[1]); revised['ordering']['dependencies']=[]
revised=runtime.public_item(revised)
print(json.dumps(dict(items=items,script=quiz_page.SERVED_JS,offline=quiz_page.OFFLINE_JS,
 revised=revised,revised_page=quiz_page.baseline_for(dict(session_id='synthetic',item=revised),{},'/answer',dict(submit='token')),
 pages=[quiz_page.baseline_for(dict(session_id='synthetic',item=q),{},'/answer',dict(submit='token')) for q in items])))
`],{cwd:new URL('../..',import.meta.url),encoding:'utf8'}));

function setup(index=1){
  const dom=new JSDOM(`<div id="host">${fixture.pages[index]}</div>`,{runScripts:'outside-only',url:'http://localhost/quiz/ordering'});
  const w=dom.window; w.BOOT={bank:'ordering'}; w.host=w.document.getElementById('host');
  w.sessionId=null; w.currentActivity=null; w.setContext=()=>{};
  w.api=()=>{throw new Error('Baseline must not create a new sitting');};
  const helper=fixture.script.indexOf('function installOrderingControls(');
  w.eval(fixture.script.slice(helper,fixture.script.indexOf('function asBuild(',helper)));
  const draft=fixture.script.indexOf('function draftKey(');
  w.eval(fixture.script.slice(draft,fixture.script.indexOf('/* ---- start:',draft)));
  const start=fixture.script.indexOf('async function start()');
  w.eval(fixture.script.slice(start,fixture.script.indexOf('if(BOOT && BOOT.bank)',start)));
  return {dom,w,form:w.host.querySelector('form')};
}
function choose(w,select,value){select.value=value;select.dispatchEvent(new w.Event('change',{bubbles:true}));}
function add(form,id){form.querySelector(`button[data-block-id="${id}"]`).click();}
const key='itembank.draft.ordering.q2';

test('native ordering restores partial positions, exact stable IDs and focused answer after reload or detour',async()=>{
  const {dom,w,form}=setup();
  try{
    await w.start();
    const selects=[...form.querySelectorAll('select')];
    let context;
    w.setContext=value=>{context=value;};
    await w.start();
    assert.equal(context.ordering,true);
    assert.match(form.textContent,/Leave unused blocks in the source area/);
    assert.doesNotMatch(form.textContent,/Select every step/);
    choose(w,selects[0],'start'); choose(w,selects[2],'left'); selects[2].focus();
    assert.deepEqual(JSON.parse(w.localStorage.getItem(key)).values,['start','','left','']);
    assert.equal(form.querySelector('[data-block-id="left"]').disabled,true);
    assert.equal(selects[1].querySelector('[value="left"]').disabled,true);
    const stored=w.localStorage.getItem(key);
    w.host.innerHTML=fixture.pages[1]; w.localStorage.setItem(key,stored);
    await w.start();
    const restored=[...w.host.querySelectorAll('select')];
    assert.deepEqual(restored.map(s=>s.value),['start','','left','']);
    assert.equal(w.document.activeElement,restored[2]);
    w.host.querySelector('[aria-label="Up block at position 3"]').click();
    assert.deepEqual(restored.map(s=>s.value),['start','left','','']);
    assert.equal(w.document.activeElement,restored[1]);
    w.host.querySelector('[aria-label="Remove block at position 2"]').click();
    assert.equal(w.host.querySelector('[data-block-id="left"]').disabled,false);
    add(w.host,'right');
    assert.deepEqual(restored.map(s=>s.value),['start','right','','']);
    const signature=JSON.parse(w.localStorage.getItem(key)).signature;
    w.localStorage.setItem(key,JSON.stringify({signature:'old',values:['spare'],focus:0}));
    w.host.innerHTML=fixture.pages[1];await w.start();
    assert.match(w.host.textContent,/older ordering declaration/);
    assert.deepEqual([...w.host.querySelectorAll('select')].map(s=>s.value),['','','','']);
    assert.ok(signature.includes('version'));
  }finally{dom.window.close();}
});

test('native source drag preserves identity and permits optional unselected blocks; ack alone clears draft',async()=>{
  const {dom,w,form}=setup();
  try{
    await w.start();
    const selects=[...form.querySelectorAll('select')];
    const block=form.querySelector('span[data-ordering-block-id="right"]');
    assert.equal(block.draggable,true);
    assert.equal(form.querySelector('button[data-block-id="right"]').draggable,false);
    block.dispatchEvent(new w.Event('dragstart',{cancelable:true}));
    assert.match(form.querySelector('[role="status"]').textContent,/Moving Independent task \(right\)\. Drop it on an answer position\./);
    const over=new w.Event('dragover',{cancelable:true}),transfer={dropEffect:'none'};
    Object.defineProperty(over,'dataTransfer',{value:transfer});
    selects[2].closest('label').dispatchEvent(over);
    assert.equal(over.defaultPrevented,true);assert.equal(transfer.dropEffect,'copy');
    assert.equal(selects[2].closest('label').classList.contains('ordering-drop-active'),true);
    selects[2].closest('label').dispatchEvent(new w.Event('drop',{cancelable:true}));
    assert.equal(selects[2].closest('label').classList.contains('ordering-drop-active'),false);
    assert.equal(selects[2].value,'right');
    block.dispatchEvent(new w.Event('dragend'));
    assert.equal(form.querySelector('[role="status"]').textContent,'Placed Independent task (right) at position 3.');
    assert.equal(block.draggable,false);
    assert.equal(block.getAttribute('aria-disabled'),'true');
    block.dispatchEvent(new w.Event('dragstart',{cancelable:true}));
    selects[1].closest('label').dispatchEvent(new w.Event('drop',{cancelable:true}));
    assert.equal(selects[1].value,'');
    const spare=form.querySelector('span[data-ordering-block-id="spare"]');
    spare.dispatchEvent(new w.Event('dragstart',{cancelable:true}));
    spare.dispatchEvent(new w.Event('dragend'));
    assert.equal(form.querySelector('[role="status"]').textContent,'Move cancelled. Use Add or drag to an answer position.');
    // External drag payloads have no locally issued source identity.
    selects[1].closest('label').dispatchEvent(new w.Event('drop',{cancelable:true}));
    assert.equal(selects[1].value,'');
    add(form,'start');add(form,'left');
    assert.deepEqual(selects.map(s=>s.value),['start','left','right','']);
    assert.equal(form.querySelector('[data-block-id="spare"]').disabled,false);
    form.dispatchEvent(new w.Event('submit',{cancelable:true}));
    assert.ok(w.localStorage.getItem(key));
    const baseline=w.host.querySelector('[data-server-baseline]');
    baseline.setAttribute('data-feedback-pause','');w.installDraft(baseline);
    assert.equal(w.localStorage.getItem(key),null);
  }finally{dom.window.close();}
});

for(const source of ['script','offline']) test(`${source} structural controls submit IDs without scoring and retry after refusal`,()=>{
  const {dom,w}=setup();
  try{
    if(source==='offline') delete w.BOOT;
    const script=fixture[source],begin=script.indexOf('function installOrderingControls(');
    w.eval(script.slice(begin,script.indexOf('function asBuild(',begin)));
    w.mkSubmit=act=>{const button=w.document.createElement('button');act.appendChild(button);return button;};
    const body=w.document.createElement('div'),act=w.document.createElement('div');w.host.replaceChildren(body,act);
    w.asOrdering(fixture.items[1],body,act,body);
    add(body,'start');
    const handle=body.querySelector('span[data-ordering-block-id="right"]');
    handle.dispatchEvent(new w.Event('dragstart',{cancelable:true}));
    assert.match(body.querySelector('[role="status"]').textContent,/Moving Independent task \(right\)/);
    const over=new w.Event('dragover',{cancelable:true}),transfer={dropEffect:'none'};
    Object.defineProperty(over,'dataTransfer',{value:transfer});
    body.querySelectorAll('select')[1].closest('label').dispatchEvent(over);
    assert.equal(over.defaultPrevented,true);assert.equal(transfer.dropEffect,'copy');
    body.querySelectorAll('select')[1].closest('label').dispatchEvent(new w.Event('drop',{cancelable:true}));
    assert.equal(body.querySelector('[role="status"]').textContent,'Placed Independent task (right) at position 2.');
    add(body,'left');
    let submitted;
    w.settle=(q,answer,card,actions,done,revert)=>{
      submitted=[...answer];
      assert.equal([...body.querySelectorAll('span[data-ordering-block-id]')].every(span=>!span.draggable),true);
      revert();
    };
    act.firstChild.click();
    assert.deepEqual(submitted,['start','right','left']);
    assert.equal(body.querySelector('select').disabled,false);
    assert.equal(act.firstChild.disabled,false);
    if(source==='script') assert.ok(w.localStorage.getItem(key));
    else assert.equal(w.localStorage.getItem(key),null);
    assert.equal(body.querySelectorAll('.right,.wrong').length,0);
    w.settle=(q,answer,card,actions,done)=>done({score:true});act.firstChild.click();
    assert.equal(w.localStorage.getItem(key),null);
    assert.equal(body.querySelectorAll('.right,.wrong').length,0);
  }finally{dom.window.close();}
});

test('malformed drafts and storage refusal cannot inject duplicate or foreign blocks',async()=>{
  const {dom,w}=setup();
  try{
    await w.start();
    const signature=w.host.querySelector('[data-ordering-signature]').dataset.orderingSignature;
    for(const values of [['start','start'],['foreign']]){
      w.localStorage.setItem(key,JSON.stringify({signature,values}));
      w.host.innerHTML=fixture.pages[1];await w.start();
      assert.deepEqual([...w.host.querySelectorAll('select')].map(s=>s.value),['','','','']);
    }
    Object.defineProperty(w,'localStorage',{get(){throw new Error('refused');}});
    assert.doesNotThrow(()=>w.installDraft(w.host.querySelector('[data-server-baseline]')));
  }finally{dom.window.close();}
});

test('unchanged public blocks with a changed private dependency graph reject stale drafts',async()=>{
  const {dom,w,form}=setup();
  try{
    await w.start();add(form,'start');add(form,'left');
    assert.notEqual(fixture.items[1].ordering.revision,fixture.revised.ordering.revision);
    assert.deepEqual(fixture.items[1].blocks,fixture.revised.blocks);
    w.host.innerHTML=fixture.revised_page;await w.start();
    assert.match(w.host.textContent,/older ordering declaration/);
    assert.deepEqual([...w.host.querySelectorAll('select')].map(s=>s.value),['','','','']);
  }finally{dom.window.close();}
});

test('actual offline build renderer requires runtime and cannot submit or imply a pending mark',()=>{
  const {dom,w}=setup();
  try{
    delete w.BOOT;
    const begin=fixture.offline.indexOf('function installOrderingControls(');
    w.eval(fixture.offline.slice(begin,fixture.offline.indexOf('function asShort(',begin)));
    w.mkSubmit=act=>{const button=w.document.createElement('button');act.appendChild(button);return button;};
    w.settle=()=>{throw new Error('Offline ordering must not submit');};
    const body=w.document.createElement('div'),act=w.document.createElement('div');
    w.asBuild(fixture.items[1],body,act,body);
    add(body,'start');assert.equal(act.firstChild.disabled,true);act.firstChild.click();
    assert.match(body.textContent,/needs a served itembank session/);
    assert.equal(w.localStorage.getItem(key),null);
  }finally{dom.window.close();}
});

test('real served verify/settle preserves released diagnostic and clears advanced deferred draft without verdict',async()=>{
  const {dom,w}=setup();
  try{
    const script=fixture.script;
    const verify=script.indexOf('async function verify(');
    w.eval(script.slice(verify,script.indexOf('function lessonChip(',verify)));
    const settle=script.indexOf('async function settle(');
    w.eval(script.slice(settle,script.indexOf('function shuffled(',settle)));
    const diagnostic=script.indexOf('function orderingCard(');
    w.eval(script.slice(diagnostic,script.indexOf('function selectionCard(',diagnostic)));
    w.feedbackFor=card=>card;
    let projected;
    w.close=(q,card,act,v)=>{projected=v;};
    const q=fixture.items[1],card=w.document.createElement('div'),act=w.document.createElement('div');
    w.localStorage.setItem(key,'draft');
    w.api=async()=>({action:'hold',score:false,ordering_diagnostic:{version:1,category:'dependency_violation'}});
    let cleaned=0;
    const cleanup=()=>{cleaned++;w.localStorage.removeItem(key);};
    await w.settle(q,['left','start','right'],card,act,cleanup,()=>{});
    assert.equal(cleaned,0);assert.match(w.orderingCard(projected.ordering_diagnostic),/prerequisite/);
    w.api=async()=>({action:'defer_feedback',next:{status:'active',item:{id:'q3'}}});
    await w.settle(q,['start','right','left'],card,act,cleanup,()=>{});
    assert.equal(cleaned,1);assert.equal(w.localStorage.getItem(key),null);
    assert.equal(projected.score,undefined);assert.equal(w.orderingCard(projected.ordering_diagnostic),'');
  }finally{dom.window.close();}
});
