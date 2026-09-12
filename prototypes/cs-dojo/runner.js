/* Disposable execution adapter. Program messages are untrusted observations. */
'use strict';
const send = self.postMessage.bind(self);
const stringify = JSON.stringify.bind(JSON);
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
let emitted = 0;
let characters = 0;

function display(value) {
  if (typeof value === 'string') return value.slice(0, 2000);
  if (value === undefined) return 'undefined';
  if (typeof value === 'number' && !Number.isFinite(value)) return String(value);
  try { return (stringify(value) ?? String(value)).slice(0, 2000); }
  catch { return '[Value could not be displayed]'; }
}

function emit(message) {
  const size = stringify(message).length;
  if (emitted >= 80 || characters + size > 16000) {
    send({type: 'limit'});
    throw new Error('Output limit reached');
  }
  emitted += 1;
  characters += size;
  send(message);
}

const output = Object.freeze({
  log: (...values) => emit({type: 'log', text: values.map(display).join(' ')}),
  warn: (...values) => emit({type: 'log', text: values.map(display).join(' ')}),
  error: (...values) => emit({type: 'log', text: values.map(display).join(' ')}),
});

function report(label, actual, expected) {
  emit({type: 'observation', label: display(label), actual: display(actual), expected: display(expected)});
}

self.onmessage = async ({data}) => {
  self.onmessage = null;
  const files = data.files;
  const cache = Object.create(null);
  const compile = (text, name) => new Function('module', 'exports', 'require', 'console', 'report',
    '"use strict";\n' + text + '\n//# sourceURL=' + name);
  const requireFile = (name) => {
    const key = String(name).replace(/^\.\//, '');
    if (!Object.hasOwn(files, key)) throw new Error('Only provided files can be required: ' + key);
    if (Object.hasOwn(cache, key)) return cache[key].exports;
    const module = {exports: {}};
    cache[key] = module;
    compile(files[key], key)(module, module.exports, requireFile, output, report);
    return module.exports;
  };
  try {
    if (Object.keys(files).length === 1) {
      const fn = new AsyncFunction('console', 'report', 'require',
        '"use strict";\n' + files[data.entry] + '\n//# sourceURL=' + data.entry);
      await fn(output, report, requireFile);
    } else {
      requireFile(data.entry);
    }
    send({type: 'done'});
  } catch (error) {
    send({type: 'error', text: display(error?.name) + ': ' + display(error?.message)});
  }
};
