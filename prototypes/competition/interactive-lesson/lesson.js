/* Original deterministic presentation code. No model, storage, or assessment API. */
(() => {
  'use strict';
  const el = id => document.getElementById(id);
  const depth = el('depth');
  function update(value) {
    const parsed = Number(value);
    const b = Number.isFinite(parsed) ? Math.max(0, Math.min(24, Math.round(parsed))) : 18;
    const delta = b - 12;
    const relation = delta === 0 ? 'A and B have equal depths.' : `B is ${Math.abs(delta)} mm ${delta > 0 ? 'higher' : 'lower'} than A.`;
    depth.value = String(b);
    depth.setAttribute('aria-valuetext', `${b} millimeters`);
    el('depth-value').textContent = `${b} mm`;
    el('bar-b').setAttribute('width', String(b / 24 * 380));
    el('b-label').textContent = `${b} mm`;
    el('chart-desc').textContent = `A is 12 mm. B is ${b} mm. ${relation}`;
    el('comparison').textContent = relation;
    el('equation').textContent = `${b} − 12 = ${delta > 0 ? '+' : delta < 0 ? '−' : ''}${Math.abs(delta)} mm`;
    el('scenario').textContent = b === 18 ? 'Source values · A 12 mm / B 18 mm' : `Hypothetical comparison · A 12 mm / B ${b} mm`;
    el('less').disabled = b === 0;
    el('more').disabled = b === 24;
  }
  depth.addEventListener('input', () => update(depth.value));
  el('less').addEventListener('click', () => update(Number(depth.value) - 1));
  el('more').addEventListener('click', () => update(Number(depth.value) + 1));
  el('reset').addEventListener('click', () => {
    update(18);
    document.querySelectorAll('details').forEach(detail => { detail.open = false; });
  });
  window.addEventListener('pageshow', () => {
    update(18);
    document.querySelectorAll('details').forEach(detail => { detail.open = false; });
  });
  update(18);
  el('controls').hidden = false;
})();
