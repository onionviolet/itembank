import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {JSDOM} from 'jsdom';
import {python} from './python_bin.mjs';

const fixture = JSON.parse(execFileSync(python,['-c',`
import json, runpy, model, runtime
from surfaces import quiz_page
qs = model.parse_bank(runpy.run_path('tests/matching_workflow_roundtrip.py')['authored_text']())
items = [runtime.public_item(q) for q in qs]
print(json.dumps(dict(items=items, script=quiz_page.SERVED_JS, offline=quiz_page.OFFLINE_JS,
    pages=[quiz_page.baseline_for(dict(session_id='synthetic',item=q), {}, '/answer',dict(submit='token')) for q in items])))
`],{cwd:new URL('../..',import.meta.url),encoding:'utf8'}));

function setup(index=0){
  const dom = new JSDOM(`<div id="host">${fixture.pages[index]}</div>`,{runScripts:'outside-only',url:'http://localhost/quiz/matching'});
  const w=dom.window;
  w.BOOT={bank:'matching'};w.host=w.document.getElementById('host');
  w.sessionId=null;w.setContext=()=>{};
  w.api=()=>{throw new Error('Baseline cannot create a second sitting');};
  const start=fixture.script.indexOf('function draftKey(');
  w.eval(fixture.script.slice(start,fixture.script.indexOf('/* ---- start:',start)));
  const begin=fixture.script.indexOf('async function start()');
  w.eval(fixture.script.slice(begin,fixture.script.indexOf('if(BOOT && BOOT.bank)',begin)));
  return {dom,w,form:w.host.querySelector('form')};
}

function choose(w,select,value){select.value=value;select.dispatchEvent(new w.Event('change',{bubbles:true}));}

test('normal matching POST preserves IDs, enforces capacity for drag and native controls, restores exact draft',async()=>{
  const {dom,w,form}=setup();
  try{
    await w.start();
    const selects=[...form.querySelectorAll('select[data-row-id]')];
    assert.deepEqual(selects.map(s=>s.dataset.rowId),['first','second']);
    assert.equal(form.action,'http://localhost/answer');
    choose(w,selects[0],'a');
    assert.equal(selects[1].querySelector('[value="a"]').disabled,true);
    const word=form.querySelector('[data-word="a"]');
    word.dispatchEvent(new w.Event('dragstart',{cancelable:true}));
    selects[1].closest('label').dispatchEvent(new w.Event('drop',{cancelable:true}));
    assert.equal(selects[1].value,'');
    choose(w,selects[1],'b');
    const key='itembank.draft.matching.q1';
    const saved=w.localStorage.getItem(key);
    assert.deepEqual(JSON.parse(saved).values,{first:'a',second:'b'});
    selects.forEach(s=>s.value='');
    w.installDraft(w.host.querySelector('[data-server-baseline]'));
    assert.deepEqual(selects.map(s=>s.value),['a','b']);
    choose(w,selects[0],'');
    assert.equal(selects[1].querySelector('[value="a"]').disabled,false);
    const baseline=w.host.querySelector('[data-server-baseline]');
    baseline.setAttribute('data-feedback-pause','');w.installDraft(baseline);
    assert.equal(w.localStorage.getItem(key),null);
  }finally{dom.window.close();}
});

test('unlimited matching permits reuse; stale revision drafts and unavailable storage remain safe',async()=>{
  const {dom,w,form}=setup(1);
  try{
    await w.start();const selects=[...form.querySelectorAll('select[data-row-id]')];
    choose(w,selects[0],'a');assert.equal(selects[1].querySelector('[value="a"]').disabled,false);
    choose(w,selects[1],'a');
    const key='itembank.draft.matching.q2';const saved=JSON.parse(w.localStorage.getItem(key));
    assert.deepEqual(saved.values,{first:'a',second:'a'});
    saved.signature='older declaration';w.localStorage.setItem(key,JSON.stringify(saved));
    selects.forEach(s=>s.value='');w.installDraft(w.host.querySelector('[data-server-baseline]'));
    assert.deepEqual(selects.map(s=>s.value),['','']);
    Object.defineProperty(w,'localStorage',{get(){throw new Error('storage refused');}});
    assert.doesNotThrow(()=>w.installDraft(w.host.querySelector('[data-server-baseline]')));
    assert.equal(form.querySelector('[name="form_token"]').value,'token');
  }finally{dom.window.close();}
});

for(const source of ['script','offline']) test(`${source} rich matching uses IDs and capacity; served drafts recover and static preview saves nothing`,()=>{
  const {dom,w}=setup();
  try{
    if(source === 'offline') delete w.BOOT;
    const script=fixture[source],begin=script.indexOf('function asMatching(');
    w.eval(script.slice(begin,script.indexOf('function asAssign(',begin)));
    w.mkSubmit=act=>{const b=w.document.createElement('button');act.appendChild(b);return b;};
    const body=w.document.createElement('div'),act=w.document.createElement('div');
    w.asMatching(fixture.items[0],body,act,body);
    let selects=[...body.querySelectorAll('select')];
    choose(w,selects[0],'a');choose(w,selects[1],'b');
    assert.equal(act.firstChild.disabled,false);
    const key='itembank.draft.matching.q1';
    if(source === 'script') assert.deepEqual(JSON.parse(w.localStorage.getItem(key)).values,{first:'a',second:'b'});
    else assert.equal(w.localStorage.getItem(key),null);
    let submitted;
    w.settle=(q,answer,card,actions,done,revert)=>{submitted=answer;revert();};
    act.firstChild.click();assert.equal(act.firstChild.disabled,false);
    assert.deepEqual({...submitted},{first:'a',second:'b'});
    const body2=w.document.createElement('div'),act2=w.document.createElement('div');
    w.asMatching(fixture.items[0],body2,act2,body2);
    if(source === 'script') assert.deepEqual([...body2.querySelectorAll('select')].map(s=>s.value),['a','b']);
    else {
      const fresh=[...body2.querySelectorAll('select')];
      assert.deepEqual(fresh.map(s=>s.value),['','']);
      choose(w,fresh[0],'a'); choose(w,fresh[1],'b');
    }
    w.settle=(q,answer,card,actions,done)=>done({explain:{row_cats:{first:'a',second:'b'}}});
    act2.firstChild.click();assert.equal(w.localStorage.getItem(key),null);
    assert.equal(body2.querySelectorAll('select.right').length,2);
  }finally{dom.window.close();}
});
