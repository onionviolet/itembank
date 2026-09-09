import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';

// A deliberately minimal DOM host. Network and storage APIs are absent.
function mount() {
  const nodes = new Map();
  const details = [{open: true}, {open: true}];
  const pageEvents = {};
  const node = id => {
    if (!nodes.has(id)) nodes.set(id, {value:'18', hidden:true, attrs:{}, events:{},
      setAttribute(k,v) { this.attrs[k] = v; },
      addEventListener(k,v) { this.events[k] = v; }});
    return nodes.get(id);
  };
  vm.runInNewContext(readFileSync(new URL('./lesson.js', import.meta.url),'utf8'), {
    document: {getElementById:node, querySelectorAll:() => details},
    window: {addEventListener:(k,v) => {pageEvents[k] = v;}}
  });
  return {node, details, pageEvents, set(b) {node('depth').value = b; node('depth').events.input();}};
}

test('source state is correct with no provider or persistence API', () => {
  const {node} = mount();
  assert.equal(node('comparison').textContent, 'B is 6 mm higher than A.');
  assert.equal(node('bar-b').attrs.width, '285');
  assert.equal(node('controls').hidden, false);
});
test('all supported values retain origin, signed difference and diagram equivalence', () => {
  const {node,set} = mount();
  for (let b=0;b<=24;b++) {
    set(b);
    assert.equal(node('depth').value,String(b));
    assert.equal(Number(node('bar-b').attrs.width),b/24*380);
    assert.equal(node('depth').attrs['aria-valuetext'],`${b} millimeters`);
    assert.equal(node('scenario').textContent.startsWith('Source values'), b===18);
    assert.ok(node('chart-desc').textContent.includes(node('comparison').textContent));
    assert.equal(node('less').disabled,b===0);
    assert.equal(node('more').disabled,b===24);
  }
  set(12); assert.equal(node('comparison').textContent,'A and B have equal depths.');
  set(6); assert.equal(node('equation').textContent,'6 − 12 = −6 mm');
});
test('invalid, fractional and out-of-range inputs cannot produce a misleading graph', () => {
  const {node,set} = mount();
  for (const [input,want] of [['bad',18],[Infinity,18],[-5,0],[99,24],[12.7,13]]) {
    set(input); assert.equal(node('depth').value,String(want));
  }
});
test('buttons, reset and browser reopen restore declared presentation state', () => {
  const {node,set,details,pageEvents} = mount();
  node('less').events.click(); assert.equal(node('depth').value,'17');
  node('more').events.click(); assert.equal(node('depth').value,'18');
  set(0); node('reset').events.click();
  assert.equal(node('depth').value,'18'); assert.ok(details.every(d => !d.open));
  set(24); details[0].open=true; pageEvents.pageshow();
  assert.equal(node('depth').value,'18'); assert.ok(details.every(d => !d.open));
});
