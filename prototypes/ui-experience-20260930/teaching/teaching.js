/* Finite synthetic teaching model. No runtime scoring or learner evidence. */
(() => {
  const $ = id => document.getElementById(id);
  const model = { time: 0, revealed: false, prediction: null, step: 0, playing: false };
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let frame = null;
  let announceTimer = null;
  let noteTimer = null;
  const noteKey = 'itembank-synthetic-teaching-20260930-note';
  const urlTheme = new URLSearchParams(location.search).get('theme');
  const initialTheme = urlTheme === 'dark' || (!urlTheme && matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
  document.documentElement.dataset.theme = initialTheme;
  const themeButton = $('theme');
  themeButton.hidden = false;
  function themeText() { themeButton.textContent = document.documentElement.dataset.theme === 'dark' ? 'Light appearance' : 'Dark appearance'; }
  themeText();
  themeButton.addEventListener('click', () => { document.documentElement.dataset.theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; themeText(); });
  $('prediction-form').hidden = false;
  $('controls').hidden = false;
  $('reference-open').hidden = false;
  $('practice-open').hidden = false;
  $('static-core').open = false;
  for (const button of document.querySelectorAll('.step-button')) button.disabled = false;

  function stop() {
    cancelAnimationFrame(frame);
    model.playing = false;
    $('play').textContent = model.time >= 6 ? 'Replay to 6 seconds' : 'Play to 6 seconds';
  }
  function render() {
    const t = model.time, m = 3 * t, n = 5 * t, gap = 2 * t;
    $('time').value = t;
    $('clock').textContent = `${t} s`;
    $('time-big').textContent = t;
    $('mira-walker').setAttribute('transform', `translate(${60 + m * 10} 76)`);
    $('noor-walker').setAttribute('transform', `translate(${60 + n * 10} 163)`);
    $('mira-distance').innerHTML = `${m} <small>m</small>`;
    $('noor-distance').innerHTML = `${n} <small>m</small>`;
    $('gap-distance').innerHTML = `${gap} <small>m</small>`;
    $('gap-bracket').setAttribute('d', `M${60 + m * 10} 256 V247 H${60 + n * 10} V256`);
    $('gap-svg-label').setAttribute('x', 60 + ((m + n) / 2) * 10);
    $('gap-svg-label').textContent = `${gap} m gap`;
    $('gap-group').style.opacity = t === 0 ? '0' : '1';
    const summary = `At ${t} seconds, Mira has travelled ${m} metres and Noor ${n} metres. The gap is ${gap} metres.`;
    $('track-desc').textContent = summary;
    clearTimeout(announceTimer);
    announceTimer = setTimeout(() => { $('scene-summary').textContent = summary; }, 160);
    $('scene-state').textContent = model.revealed ? 'Explore the model' : 'Both at the start';
    $('worked-time').textContent = `AT ${t} SECONDS`;
    $('eq-mira').textContent = `3 m/s × ${t} s = ${m} m`;
    $('eq-noor').textContent = `5 m/s × ${t} s = ${n} m`;
    $('eq-gap').textContent = `${n} m − ${m} m = ${gap} m`;
    $('graph-cursor').setAttribute('d', `M${48 + t * 42} 20 V190`);
    $('graph-mira-point').setAttribute('cx', 48 + t * 42);
    $('graph-mira-point').setAttribute('cy', 190 - m * 170 / 60);
    $('graph-noor-point').setAttribute('cx', 48 + t * 42);
    $('graph-noor-point').setAttribute('cy', 190 - n * 170 / 60);
    $('graph-caption').textContent = `At ${t} seconds: Mira ${m} m; Noor ${n} m; gap ${gap} m.`;
    $('graph-desc').textContent = `${summary} The blue Mira line follows distance = 3 × time; the orange Noor line follows distance = 5 × time.`;
    $('less').disabled = !model.revealed || t === 0;
    $('more').disabled = !model.revealed || t === 12;
    $('time').disabled = !model.revealed;
    $('play').disabled = !model.revealed;
    $('reset-time').disabled = !model.revealed;
    if (!model.playing) $('play').textContent = t >= 6 ? 'Replay to 6 seconds' : 'Play to 6 seconds';
    $('time-help').textContent = model.revealed ? '0 to 12 seconds. Use the slider, arrow keys, or the − / + buttons.' : 'Keep a prediction to unlock the clock.';
    document.querySelector('.experiment').dataset.highlight = model.step;
    document.querySelectorAll('.worked-step').forEach(section => {
      const active = model.step === Number(section.dataset.step);
      section.classList.toggle('active', active);
      const button = section.querySelector('button');
      button.setAttribute('aria-expanded', active ? 'true' : 'false');
      section.querySelector('.step-content').hidden = !active;
      button.querySelector('b').textContent = active ? '−' : '+';
    });
  }
  function setTime(t) { stop(); model.time = Math.max(0, Math.min(12, Math.round(t))); render(); }
  $('prediction-form').addEventListener('submit', event => {
    event.preventDefault();
    if (!$('prediction-form').reportValidity()) return;
    model.prediction = Number($('prediction').value);
    model.revealed = true;
    $('prediction-form').hidden = true;
    $('prediction-result').hidden = false;
    $('retry').hidden = false;
    $('graph-toggle').hidden = false;
    const result = $('prediction-result');
    result.replaceChildren();
    const label = document.createElement('span'); label.textContent = 'Your first prediction';
    const saved = document.createElement('strong'); saved.textContent = `${model.prediction} m`;
    const actualLabel = document.createElement('span'); actualLabel.textContent = 'Model at 6 seconds';
    const actual = document.createElement('strong'); actual.className = 'actual'; actual.textContent = '12 m';
    const explanation = document.createElement('p');
    explanation.textContent = model.prediction === 12 ? 'That matches the model. Noor adds 2 more metres each second: 2 × 6 = 12.' : `Compare your ${model.prediction} m prediction with the 12 m model gap. Use the worked steps to inspect why.`;
    result.append(label, saved, actualLabel, actual, explanation);
    model.step = 3;
    setTime(6);
    $('time').focus({preventScroll:true});
  });
  $('retry').addEventListener('click', () => {
    stop(); model.revealed = false; model.prediction = null; model.time = 0; model.step = 0;
    $('prediction-form').hidden = false; $('prediction-result').hidden = true; $('retry').hidden = true;
    $('prediction').value = ''; $('graph-toggle').hidden = true; $('graph-panel').hidden = true; $('graph-toggle').setAttribute('aria-expanded','false'); $('graph-toggle').textContent = 'See the graph';
    render(); $('prediction').focus({preventScroll:true});
  });
  $('time').addEventListener('input', () => setTime(Number($('time').value)));
  $('less').addEventListener('click', () => setTime(model.time - 1));
  $('more').addEventListener('click', () => setTime(model.time + 1));
  $('reset-time').addEventListener('click', () => setTime(0));
  $('play').addEventListener('click', () => {
    if (model.playing) { stop(); return; }
    if (reduced.matches) { setTime(6); return; }
    if (model.time >= 6) model.time = 0;
    model.playing = true; $('play').textContent = 'Pause demonstration';
    const startTime = model.time, began = performance.now();
    function tick(now) {
      model.time = Math.min(6, startTime + Math.floor((now - began) / 500));
      render();
      if (model.time < 6) frame = requestAnimationFrame(tick);
      else stop();
    }
    frame = requestAnimationFrame(tick);
  });
  reduced.addEventListener('change', () => { if (reduced.matches && model.playing) setTime(6); });
  $('graph-toggle').addEventListener('click', () => {
    const expanded = $('graph-panel').hidden;
    $('graph-panel').hidden = !expanded;
    $('graph-toggle').setAttribute('aria-expanded', String(expanded));
    $('graph-toggle').textContent = expanded ? 'Hide the graph' : 'See the graph';
  });
  document.querySelectorAll('.step-button').forEach(button => button.addEventListener('click', () => {
    const step = Number(button.closest('[data-step]').dataset.step);
    model.step = model.step === step ? 0 : step; render();
  }));
  function openDialog(id, trigger) {
    stop();
    const dialog = $(id), scroll = window.scrollY;
    dialog.showModal();
    dialog.addEventListener('close', () => { trigger.focus({preventScroll:true}); window.scrollTo({top:scroll,behavior:'instant'}); }, {once:true});
  }
  $('reference-open').addEventListener('click', event => openDialog('reference-dialog', event.currentTarget));
  $('practice-open').addEventListener('click', event => openDialog('practice-dialog', event.currentTarget));
  document.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => $(button.dataset.close).close()));
  $('practice-form').addEventListener('submit', event => {
    event.preventDefault();
    if (!$('practice-form').reportValidity()) return;
    const prediction = Number($('practice').value);
    $('practice-feedback').hidden = false;
    $('practice-feedback').textContent = `Your prediction: ${prediction} m. Model: 5 × 4 − 3 × 4 = 20 − 12 = 8 m. ${prediction === 8 ? 'Your prediction matches the model.' : 'Compare the two distances, rather than adding them.'} Demo feedback only.`;
  });
  try {
    const saved = localStorage.getItem(noteKey);
    if (saved !== null) { $('note').value = saved; $('note-status').textContent = 'Synthetic note restored from this browser.'; }
    else $('note-status').textContent = 'Synthetic note. Stored in this browser when you type.';
  } catch { $('note-status').textContent = 'Browser storage is unavailable. This note lasts only while the page is open.'; }
  $('note').addEventListener('input', () => {
    clearTimeout(noteTimer);
    $('note-status').textContent = 'Saving synthetic note…';
    noteTimer = setTimeout(() => {
      try { localStorage.setItem(noteKey, $('note').value); $('note-status').textContent = 'Synthetic note saved in this browser.'; }
      catch { $('note-status').textContent = 'Not saved. Browser storage failed; copy your note before closing.'; }
    }, 250);
  });
  render();
})();
