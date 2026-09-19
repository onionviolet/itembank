import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {glossary, passage, tokenize, emptyState, storageKey, createStore, pack, decode} from './prototype.js';
let checks = 0;
function test(name, fn) { fn(); checks++; console.log(`ok ${checks}: ${name}`); }
const tokens = tokenize(passage);
test('source text and UTF-16 ranges round trip without loss', () => {
  assert.equal(tokens.map(t => t.text).join(''), passage);
  for (const t of tokens) assert.equal(passage.slice(t.start, t.end), t.text);
  assert.equal(tokens.at(-1).end, passage.length);
});
test('repeated lemmas and explicit provenance', () => {
  assert.deepEqual(tokens.filter(t => t.lemma).map(t => t.lemma), ['学习','中文','读','学习','中文','中文']);
  for (const t of tokens.filter(t => t.lemma)) {
    assert.equal(t.source, glossary[t.text].source);
    assert.equal(t.lemmaSource, 'explicit glossary mapping');
  }
});
test('overlaps prefer longest literal match including regex punctuation', () => {
  const entries = {'a':{lemma:'a'}, 'a+b':{lemma:'long'}, '.':{lemma:'dot'}};
  assert.deepEqual(tokenize('a+b.a?', entries).filter(t => t.lemma).map(t => t.lemma), ['long','dot','a']);
});
test('empty, unknown, astral, newline, mixed scripts and punctuation survive', () => {
  for (const text of ['', '🙂\n\t未匹配字!?', '中文English 123, 中文', '<b>学习</b>', 'e\u0301 学习']) {
    assert.equal(tokenize(text).map(t => t.text).join(''), text);
    for (const t of tokenize(text)) assert.equal(text.slice(t.start,t.end), t.text);
  }
});
const memory = new Map([['unrelated', 'keep']]);
const storage = {getItem:key => memory.get(key) ?? null, setItem:(key,val) => memory.set(key,val)};
let revision = 0;
const makeStore = () => createStore(storage, () => `test-${++revision}`);
let a = makeStore(); let b = makeStore();
test('new state and repeated lemma use one state slot', () => {
  assert.deepEqual(a.load(), emptyState()); b.load();
  a.save({...a.states, '学习':'learning'});
  assert.equal(Object.keys(a.states).length, 3);
  assert.equal(makeStore().load()['学习'], 'learning');
});
test('stale tab cannot overwrite saved state', () => {
  const before = memory.get(storageKey);
  assert.throws(() => b.save({...b.states, '中文':'known'}), /Conflict/);
  assert.equal(memory.get(storageKey), before);
  b.load(); b.save({...b.states, '中文':'known'});
});
let backup;
test('portable copy restores into empty independent storage', () => {
  b.load(); backup = b.export();
  let raw = null;
  const fresh = createStore({getItem:() => raw, setItem:(key,val) => { raw = val; }}, () => 'fresh');
  fresh.load(); fresh.save(decode(backup).states);
  assert.deepEqual(fresh.load(), b.states);
});
test('reset affects only this fixture and restore recovers exported states', () => {
  b.save(emptyState()); assert.deepEqual(b.load(), emptyState());
  b.save(decode(backup).states); assert.equal(b.states['中文'], 'known');
  assert.equal(memory.get('unrelated'), 'keep');
});
test('reject wrong fixture/version/occurrence/format, malformed and extra data', () => {
  for (const field of ['fixture','version','occurrenceId','format']) {
    const value = JSON.parse(backup); value[field] = 'changed';
    assert.throws(() => decode(JSON.stringify(value)));
  }
  for (const raw of ['{', 'null', '[]', 'x'.repeat(20001), JSON.stringify({...JSON.parse(backup), extra:1})]) assert.throws(() => decode(raw));
  for (const states of [{'学习':'mastered'}, {...emptyState(), unexpected:'new'}, {...emptyState(), '中文':'invalid'}]) assert.throws(() => decode(JSON.stringify(pack(states,'bad'))));
});
test('corruption and unavailable storage preserve bytes and block saves', () => {
  const corrupt = new Map([[storageKey, '{broken']]);
  const store = createStore({getItem:k => corrupt.get(k), setItem:(k,v) => corrupt.set(k,v)}, () => 'invalid');
  assert.throws(() => store.load());
  assert.throws(() => store.save(emptyState())); assert.equal(corrupt.get(storageKey), '{broken');
  const denied = createStore({getItem:() => {throw Error('denied');}}, () => 'denied');
  assert.throws(() => denied.load(), /denied/); assert.throws(() => denied.save(emptyState()));
});
test('quota failure leaves saved state and in-memory state unchanged', () => {
  const raw = backup;
  const store = createStore({getItem:() => raw, setItem:() => {throw Error('quota');}}, () => 'quota');
  store.load(); const before = store.states;
  assert.throws(() => store.save(emptyState()), /quota/); assert.deepEqual(store.states,before);
});
const html = await readFile(new URL('index.html', import.meta.url), 'utf8');
test('static reading matches source and exposes all glosses without scripts', () => {
  assert.equal(html.match(/id="static-passage"[^>]*>([\s\S]*?)<\/p>/)[1], passage);
  for (const entry of Object.values(glossary)) for (const value of Object.values(entry)) assert.ok(html.includes(value));
  assert.ok(html.includes('id="interactive" hidden')); assert.ok(!html.includes('<noscript>'));
});
console.log(`${checks} deterministic prototype checks passed`);
