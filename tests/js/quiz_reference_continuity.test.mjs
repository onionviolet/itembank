import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {JSDOM} from 'jsdom';
import {python} from './python_bin.mjs';

const fixture = JSON.parse(execFileSync(python, ['-c', `
import json
from surfaces import quiz_page
def page(kind):
    item=dict(id='synthetic', number=1, stem='Synthetic question', type=kind,
              options=[dict(key='A',text='One'),dict(key='B',text='Two')],
              response_schema=dict(select=2))
    return quiz_page.baseline_for(dict(session_id='sitting',item=item),{},'/answer',dict(submit='token'))
print(json.dumps(dict(script=quiz_page.SERVED_JS,mc=page('mc'),multi=page('multi'))))
`], {cwd:new URL('../..',import.meta.url),encoding:'utf8'}));

function setup(kind='mc'){
  const dom = new JSDOM(`<div id="host">${fixture[kind]}</div>`,
    {runScripts:'outside-only',url:'http://localhost/quiz/synthetic'});
  const w = dom.window;
  w.BOOT={bank:'synthetic'};
  const begin=fixture.script.indexOf('function draftKey(');
  w.eval(fixture.script.slice(begin,fixture.script.indexOf('/* ---- start:',begin)));
  w.requestAnimationFrame=fn=>fn();
  w.scrollTo=(x,y)=>{w.restoredY=y;};
  return {dom,w,baseline:w.document.querySelector('[data-server-baseline]')};
}
const key='itembank.draft.synthetic.synthetic';

test('native choices restore a radio or multiple checkboxes after a reference detour',()=>{
  for(const kind of ['mc','multi']){
    const {dom,w,baseline}=setup(kind);
    const options=[...baseline.querySelectorAll('[name=option]')];
    w.installDraft(baseline);
    options[0].checked=true;
    if(kind==='multi') options[1].checked=true;
    options[0].dispatchEvent(new w.Event('change',{bubbles:true}));
    const raw=w.localStorage.getItem(key);
    const next=setup(kind);
    next.w.localStorage.setItem(key,raw);
    next.w.installDraft(next.baseline);
    assert.equal(next.baseline.querySelectorAll('[name=option]:checked').length,kind==='mc'?1:2);
    assert.equal(next.baseline.querySelector('[name=form_token]').value,'token');
    dom.window.close();next.dom.window.close();
  }
});

test('changed public item, foreign option and multiple radio drafts are refused',()=>{
  const {dom,w,baseline}=setup();
  for(const saved of [
    {signature:'old',values:['A']},
    {signature:baseline.dataset.presentationSignature,values:['foreign']},
    {signature:baseline.dataset.presentationSignature,values:['A','B']},
    {signature:baseline.dataset.presentationSignature,values:['A','A']}]){
    w.localStorage.setItem(key,JSON.stringify(saved));w.installDraft(baseline);
    assert.equal(baseline.querySelectorAll(':checked').length,0);
  }
  dom.window.close();
});

test('server-echoed refused answer wins over an older browser draft',()=>{
  const {dom,w,baseline}=setup();
  baseline.querySelector('[value=B]').checked=true;
  w.localStorage.setItem(key,JSON.stringify({signature:baseline.dataset.presentationSignature,values:['A']}));
  w.installDraft(baseline);
  assert.equal(baseline.querySelector(':checked').value,'B');
  dom.window.close();
});

test('feedback clears choices and storage failure preserves native input',()=>{
  const {dom,w,baseline}=setup();
  w.localStorage.setItem(key,'draft');baseline.setAttribute('data-feedback-pause','');
  w.installDraft(baseline);assert.equal(w.localStorage.getItem(key),null);
  baseline.removeAttribute('data-feedback-pause');
  Object.defineProperty(w,'localStorage',{get(){throw new Error('unavailable');}});
  assert.doesNotThrow(()=>w.installDraft(baseline));
  assert.equal(baseline.querySelector('form').getAttribute('action'),'/answer');
  dom.window.close();
});

test('same sitting and revision restore saved viewport and answer focus',()=>{
  const {dom,w,baseline}=setup();
  const option=baseline.querySelector('[name=option]');option.focus();
  Object.defineProperty(w,'scrollY',{value:720,configurable:true});
  assert.equal(w.restoreQuizPosition(baseline),false);
  w.dispatchEvent(new w.Event('pagehide'));
  baseline.querySelector('h1').focus();
  assert.equal(w.restoreQuizPosition(baseline),true);
  assert.equal(w.restoredY,720);assert.equal(w.document.activeElement,option);
  baseline.dataset.presentationSignature='new-revision';
  assert.equal(w.restoreQuizPosition(baseline),false);
  assert.equal(w.sessionStorage.length,0);
  dom.window.close();
});

test('other sitting, feedback and unavailable storage never restore old position',()=>{
  const {dom,w,baseline}=setup();
  w.restoreQuizPosition(baseline);w.dispatchEvent(new w.Event('pagehide'));
  baseline.dataset.sessionId='another';assert.equal(w.restoreQuizPosition(baseline),false);
  assert.equal(w.sessionStorage.length,0);
  baseline.setAttribute('data-feedback-pause','');assert.equal(w.restoreQuizPosition(baseline),false);
  Object.defineProperty(w,'sessionStorage',{get(){throw new Error('unavailable');}});
  assert.equal(w.restoreQuizPosition(baseline),false);dom.window.close();
});
