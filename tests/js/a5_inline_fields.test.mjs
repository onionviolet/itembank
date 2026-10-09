import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const source = ['offline.js', 'served.js'].map(name =>
  readFileSync(new URL(`../../surfaces/assets/quiz/${name}`, import.meta.url), 'utf8')).join('\n');
const helpers = [...source.matchAll(/function fillFields\(q, body\)\{[\s\S]*?\n\}\n\n(?=function asFill)/g)].map(match => match[0]);
assert.equal(helpers.length, 2);

class Element {
  constructor(tag) { this.tag = tag; this.childNodes = []; this._text = ''; this.attributes = {}; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  getAttribute(name) { return this.attributes[name] ?? null; }
  appendChild(child) { assert.ok(child); child.parentNode = this; this.childNodes.push(child); return child; }
  append(...children) { children.forEach(child => this.appendChild(child)); }
  replaceChildren() { this.childNodes.forEach(child => { child.parentNode = null; }); this.childNodes = []; }
  set textContent(value) { this._text = String(value); this.childNodes = []; }
  get textContent() { return this._text + this.childNodes.map(child => child.textContent).join(''); }
}

for (const [index, helper] of helpers.entries()) {
  const label = index === 0 ? 'offline' : 'served';
  const document = {
    createElement: tag => new Element(tag),
    createTextNode: text => Object.assign(new Element('#text'), {textContent: text}),
  };
  const context = vm.createContext({document});
  vm.runInContext(helper, context);
  const fields = [{id: 'count', label: 'Stripe count', kind: 'numeric'},
                  {id: 'color', label: 'Flag color', kind: 'text', case_sensitive: false}];

  test(`${label}: inline sentence positions reuse labelled existing field controls`, () => {
    const body = document.createElement('div');
    const controls = context.fillFields({fields, fill_layout: 'inline',
      stem: 'The flag is {{color}} and has {{count}} stripes.'}, body);
    const wrap = body.childNodes[0];
    const labels = wrap.childNodes.filter(node => node.tag === 'label');
    assert.equal(labels[0], controls.color.parentNode);
    assert.equal(labels[1], controls.count.parentNode);
    assert.equal(controls.color.name, 'fill_color');
    assert.equal(controls.count.type, 'text');
    assert.equal(controls.count.maxLength, 4096);
    assert.ok(wrap.textContent.includes('The flag is '));
    assert.ok(!wrap.textContent.includes('{{'));
    controls.color.value = '  BLUE  ';
    controls.count.value = 'oops';
    assert.equal(labels[0].childNodes.find(node => node.tag === 'input').value, '  BLUE  ');
    assert.equal(labels[1].childNodes.find(node => node.tag === 'input').value, 'oops');
    assert.equal(controls.color.getAttribute('aria-describedby'),
                 labels[0].childNodes.find(node => node.id === controls.color.getAttribute('aria-describedby')).id);
  });

  test(`${label}: text fragments remain literal and legacy fields retain authored order`, () => {
    const body = document.createElement('div');
    context.fillFields({fields, fill_layout: 'inline', stem: '<script>x</script> {{color}} {{count}}'}, body);
    assert.equal(body.childNodes[0].childNodes[0].tag, '#text');
    assert.equal(body.childNodes[0].childNodes[0].textContent, '<script>x</script> ');
    const legacy = document.createElement('div');
    const controls = context.fillFields({fields, stem: '{{literal}}'}, legacy);
    assert.equal(legacy.childNodes[0].childNodes[0], controls.count.parentNode);
    assert.equal(legacy.childNodes[0].childNodes[1], controls.color.parentNode);
  });
}
