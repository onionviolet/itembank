// Executes the specimen's actual gesture, cache and copy functions.
// DOM/storage/clipboard doubles cover faults, not physical browser input.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
assert.equal(new Set(ids).size,ids.length,'unique IDs');
for(const match of html.matchAll(/\b(?:href|aria-controls)="([^"]+)"/g)){
  const id=match[1].replace(/^#/,'');assert(ids.includes(id),'resolvable control/link '+id);
}
assert(!/<(?:script|img|link)[^>]+(?:src|href)="https?:/i.test(html),'no remote assets');
const decode=s=>s.replace(/<[^>]*>/g,'').replaceAll('&gt;','>').replaceAll('&lt;','<').replaceAll('&amp;','&');
const codeText=decode(html.match(/<pre id="code-example"[^>]*><code>([\s\S]*?)<\/code>/)[1]);
const base=readFileSync(new URL('before-interaction-pass.html',import.meta.url),'utf8');
assert.equal(codeText,decode(base.match(/<pre id="code-example"[^>]*><code>([\s\S]*?)<\/code>/)[1]),'original source preserved');

const nodes=new Map();
let document;
class Element {
  constructor(id){this.id=id;this.textContent='';this.value='';this.hidden=true;this.dataset={};this.style={};this.attrs=new Map();this.listeners={};}
  setAttribute(k,v){this.attrs.set(k,String(v));}
  getAttribute(k){return this.attrs.get(k)??null;}
  removeAttribute(k){this.attrs.delete(k);}
  hasAttribute(k){return this.attrs.has(k);}
  addEventListener(k,v){(this.listeners[k]??=[]).push(v);}
  async fire(k,event={}){for(const handler of this.listeners[k]??[])await handler(event);}
  focus(){document.activeElement=this;}
  scrollIntoView(){}
  querySelector(){return new Element('child');}
  querySelectorAll(selector){return selector==='circle'?circles:[];}
  getScreenCTM(){return {a:1,b:0,inverse:()=>({a:1,c:0,e:0})};}
  setPointerCapture(id){this.pointer=id;}
  hasPointerCapture(id){return this.pointer===id;}
  releasePointerCapture(){this.pointer=null;}
}
const node=id=>{if(!nodes.has(id))nodes.set(id,new Element(id));return nodes.get(id);};
const circles=Array.from({length:7},(_,i)=>{const n=new Element('point');n.dataset.value=String(i+7);return n;});
const strict=node('strict'),inclusive=node('inclusive');strict.value='strict';inclusive.value='inclusive';strict.checked=true;
const diagram=node('diagram');
document={activeElement:null,body:{dataset:{}},getElementById:node,
 querySelector(selector){if(selector.includes('input[name="rule"]'))return selector.includes('value="inclusive"')?inclusive:selector.includes('value="strict"')?strict:inclusive.checked?inclusive:strict;
 if(selector==='.numberline')return diagram;if(selector==='#code-example code')return node('source');return node(selector);},
 querySelectorAll:()=>[],addEventListener:(...a)=>node('document').addEventListener(...a)};
node('value').value='10';node('source').textContent=codeText;
const store=new Map();let denyWrite=false,denyRead=false,writes=0;
const clipboard={calls:[],writeText:async text=>clipboard.calls.push(text)};
const observers=[];
const context=vm.createContext({document,navigator:{clipboard},localStorage:{
 getItem:k=>{if(denyRead)throw Error('denied read');return store.get(k)??null;},
 setItem:(k,v)=>{if(denyWrite)throw Error('denied write');store.set(k,v);writes++;}},
 window:{addEventListener:(...a)=>node('window').addEventListener(...a)},
 ResizeObserver:class{constructor(fn){observers.push(fn);}observe(){}},
 setTimeout,clearTimeout,console});
const chunk=(start,end)=>script.slice(script.indexOf(start),script.indexOf(end));
vm.runInContext(chunk(' const sections',' function rememberView')+
 chunk(" document.getElementById('retry-save').addEventListener",' const term=')+
 chunk(' const code=document.querySelector',' ruleField.disabled=false')+
 `globalThis.probe={update,saveState,restoreState,blocked:()=>blockedSavedState,active:()=>activePointer};`,context);
const probe=context.probe,range=node('value'),key='itembank.boundary-design-study.v1';
probe.update();probe.saveState();assert.equal(JSON.parse(store.get(key)).value,10);
probe.saveState();assert.equal(writes,1,'no duplicate save');
const target=marker=>({closest:selector=>selector.includes(',')?{}:marker?{}:null});
const event=(x,y=0,marker=true,id=7)=>({clientX:x,clientY:y,target:target(marker),pointerId:id,isPrimary:true,button:0,preventDefault(){}});
const down=x=>diagram.fire('pointerdown',event(x));
const move=x=>diagram.fire('pointermove',event(x));
await diagram.fire('pointerdown',{...event(235),isPrimary:false});assert.equal(probe.active(),null,'ignore non-primary pointer');
await diagram.fire('pointerdown',{...event(235),button:1});assert.equal(probe.active(),null,'ignore non-left button');
await down(251);await move(253);assert.equal(range.value,'10','4px intent threshold');
await move(319);assert.equal(range.value,'11','off-center grab retains offset');
probe.saveState();assert.equal(JSON.parse(store.get(key)).value,10,'preview is not saved');
await node('document').fire('keydown',{key:'Escape',preventDefault(){}});
assert.equal(range.value,'10');assert.equal(probe.active(),null);assert(!diagram.hasAttribute('data-dragging'));
for(const interruption of ['pointercancel','lostpointercapture','blur','resize','observer']){
 await down(235);await move(400);assert.equal(range.value,'12');
 if(interruption==='blur'||interruption==='resize')await node('window').fire(interruption);
 else if(interruption==='observer')observers[0]();
 else await diagram.fire(interruption,{pointerId:7});
 assert.equal(range.value,'10',interruption+' rollback');assert.equal(probe.active(),null);
 assert.equal(JSON.parse(store.get(key)).value,10,interruption+' preserves saved base');
}
await down(235);await diagram.fire('pointermove',event(438,0,true,99));assert.equal(range.value,'10','ignore other pointer');
await move(900);await diagram.fire('pointerup',event(900));assert.equal(range.value,'13','outside clamps');assert.equal(JSON.parse(store.get(key)).value,13);
await diagram.fire('pointerdown',event(167.333,0,false));await diagram.fire('pointerup',event(167.333,0,false));assert.equal(range.value,'9','track click');
denyWrite=true;range.value='11';probe.saveState();assert.equal(JSON.parse(store.get(key)).value,9);assert.match(node('local-status').textContent,/unavailable/);
denyWrite=false;node('retry-save').focus();await node('retry-save').fire('click');
assert.equal(JSON.parse(store.get(key)).value,11);assert.equal(document.activeElement.id,'retry-save');assert.equal(node('retry-save').hidden,false);assert.equal(node('retry-save').textContent,'Save again');
store.set(key,'external bytes');range.value='12';probe.saveState();assert.equal(store.get(key),'external bytes');assert(probe.blocked());assert.match(node('local-status').textContent,/changed elsewhere/);
await node('reset-cache').fire('click');assert.equal(JSON.parse(store.get(key)).value,12);
store.set(key,'{"version":99}');probe.restoreState();probe.saveState();assert.equal(store.get(key),'{"version":99}','future cache preserved');
await node('reset-cache').fire('click');
store.set(key,'broken JSON');probe.restoreState();probe.saveState();assert.equal(store.get(key),'broken JSON','corrupt cache preserved');
await node('reset-cache').fire('click');
denyRead=true;probe.saveState();assert.match(node('local-status').textContent,/unavailable/);denyRead=false;

const copy=node('copy-code');copy.focus();await copy.fire('click');
assert.equal(clipboard.calls.at(-1),codeText,'exact indentation/source');assert.equal(document.activeElement.id,'copy-code','copy does not steal focus');
let settle;clipboard.writeText=()=>new Promise(resolve=>{settle=resolve;});
const pending=copy.fire('click');assert.equal(copy.getAttribute('aria-disabled'),'true');assert.match(node('copy-status').textContent,/Copying/);
await copy.fire('click');settle();await pending;assert.equal(copy.getAttribute('aria-disabled'),null);
clipboard.writeText=async()=>{throw Error('clipboard denial');};await copy.fire('click');assert.match(node('copy-status').textContent,/Could not copy/);assert.equal(copy.getAttribute('aria-disabled'),null);
node('source').textContent='';await copy.fire('click');assert.equal(node('copy-status').textContent,'No code to copy.');
console.log('PASS: source/IDs/links; gesture intent/release/cancellation; cache fault/conflict/recovery; exact copy/pending/denied/empty/focus.');
