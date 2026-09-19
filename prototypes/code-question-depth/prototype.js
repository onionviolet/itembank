// Synthetic comparison observations only. No answer key or assessment authority.
export const tasks = {
  A: {values: [1, 2, 3], proposed: [1, 2, 3]},
  B: {values: [2, 3, 4], proposed: [2, 3, 4]},
};
export const orders = {
  1: [['A', 'D1'], ['B', 'D2']], 2: [['A', 'D2'], ['B', 'D1']],
  3: [['B', 'D1'], ['A', 'D2']], 4: [['B', 'D2'], ['A', 'D1']],
};
export function sourceFor(id) {
  return `1  total = 0\n2  for n in [${tasks[id].values.join(', ')}]:\n3      total += n\n4  print(total)`;
}
export function makeTrial(id, depth, position, now) {
  return {task: id, depth, position, source: sourceFor(id), proposedTrace: tasks[id].proposed,
    startedAt: now, committedAt: null, finishedAt: null, initialPrediction: '', trace: [],
    firstMistakenRow: '', proposedReplacement: '', finalPrediction: '', explanation: '',
    navigation: {tabs: 0, reverseTabs: 0, focusTransitions: 0, clicks: 0, scrollEvents: 0, hiddenEvents: 0},
    burden: 'unreported', notes: '',
    humanReview: {reviewer: '', taskSuccess: 'unreviewed', predictionAccuracy: {initial: 'unreviewed', final: 'unreviewed'},
      firstMistakenState: 'unreviewed', explanationQuality: 'unreviewed', rationale: ''}};
}
export function commitPrediction(trial, value, now) {
  if (!value.trim() || trial.committedAt !== null) return false;
  trial.initialPrediction = value.trim(); trial.committedAt = now;
  return true;
}
export function finishTrial(trial, response, now) {
  if (trial.committedAt === null || trial.finishedAt !== null) return false;
  if (['firstMistakenRow', 'proposedReplacement', 'finalPrediction', 'explanation'].some(k => !response[k]?.trim())) return false;
  if (trial.depth === 'D2' && (response.trace?.length !== 3 || response.trace.some(v => !v.trim()))) return false;
  Object.assign(trial, response, {trace: trial.depth === 'D2' ? response.trace : [], finishedAt: now,
    completionMs: now - trial.startedAt, predictionMs: trial.committedAt - trial.startedAt,
    reasoningMs: now - trial.committedAt});
  return true;
}
export function packet(order, trials) {
  return {format: 'disposable-code-comparison-v1', authority: 'learner-owned observations, not assessment evidence',
    assignment: order, complete: trials.length === 2 && trials.every(t => t.finishedAt !== null),
    timing: 'elapsed monotonic milliseconds, includes interruptions, excludes post-task notes', trials};
}

if (typeof document !== 'undefined') {
  const $ = id => document.getElementById(id);
  let assignment, trial;
  const trials = [];
  const active = () => trial && trial.finishedAt === null;
  $('setup').hidden = false;
  function start() {
    const [id, depth] = orders[assignment][trials.length];
    $('setup').hidden = true; $('review').hidden = true; $('task').hidden = false;
    $('predict').reset(); $('reason').reset(); $('prediction').readOnly = false;
    $('predict').querySelector('button').disabled = false;
    $('reason').hidden = true; $('trace').hidden = true;
    $('status').textContent = ''; $('source').textContent = sourceFor(id);
    $('task-title').textContent = `Task ${trials.length + 1} of 2: ${id}, ${depth}`;
    $('peer').textContent = `Proposed trace to diagnose (may contain mistakes): ${tasks[id].values.map((n, i) => `row ${i + 1}, n = ${n}, total = ${tasks[id].proposed[i]}`).join('; ')}.`;
    $('rows').replaceChildren();
    if (depth === 'D2') tasks[id].values.forEach(n => {
      const row = document.createElement('tr'), th = document.createElement('th'), td = document.createElement('td'), input = document.createElement('input');
      th.scope = 'row'; th.textContent = n;
      input.setAttribute('aria-label', `total after n equals ${n}`); input.required = true;
      td.append(input); row.append(th, td); $('rows').append(row);
    });
    $('task-title').focus();
    trial = makeTrial(id, depth, trials.length + 1, performance.now());
  }
  $('start').addEventListener('click', () => { assignment = $('order').value; start(); });
  $('predict').addEventListener('submit', e => {
    e.preventDefault();
    if (!commitPrediction(trial, $('prediction').value, performance.now())) {
      $('status').textContent = 'Enter a prediction or “unsure”.'; $('prediction').focus(); return;
    }
    $('prediction').readOnly = true; $('predict').querySelector('button').disabled = true;
    $('reason').hidden = false; $('trace').hidden = trial.depth !== 'D2';
    (trial.depth === 'D2' ? $('rows').querySelector('input') : $('first')).focus();
  });
  $('reason').addEventListener('submit', e => {
    e.preventDefault();
    const response = {firstMistakenRow: $('first').value, proposedReplacement: $('replacement').value.trim(),
      finalPrediction: $('final').value.trim(), explanation: $('explanation').value.trim(),
      trace: Array.from($('rows').querySelectorAll('input'), input => input.value.trim())};
    if (!finishTrial(trial, response, performance.now())) {
      $('status').textContent = 'Complete each field, or write “unsure”.'; return;
    }
    trials.push(trial); $('task').hidden = true; $('review').hidden = false;
    $('burden').value = 'unreported'; $('notes').value = ''; $('download-status').textContent = '';
    $('timing').textContent = `Task ${trial.position}: ${(trial.completionMs / 1000).toFixed(1)} seconds elapsed. Interruptions are included.`;
    $('next').hidden = trials.length === 2; notes(); $('review-title').focus();
  });
  function notes() {
    trial.burden = $('burden').value; trial.notes = $('notes').value;
    $('export-preview').value = JSON.stringify(packet(assignment, trials), null, 2);
  }
  $('burden').addEventListener('change', notes); $('notes').addEventListener('input', notes);
  $('next').addEventListener('click', () => { notes(); start(); });
  $('download').addEventListener('click', () => {
    notes();
    const url = URL.createObjectURL(new Blob([$('export-preview').value], {type: 'application/json'}));
    const a = document.createElement('a'); a.href = url;
    a.download = `code-comparison-order-${assignment}-${trials.length}-tasks.json`; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    $('download-status').textContent = 'Download requested. Check your downloads before closing this tab.';
  });
  document.addEventListener('keydown', e => {
    if (active() && e.key === 'Tab') trial.navigation[e.shiftKey ? 'reverseTabs' : 'tabs']++;
  });
  document.addEventListener('focusin', () => { if (active()) trial.navigation.focusTransitions++; });
  document.addEventListener('click', () => { if (active()) trial.navigation.clicks++; });
  document.addEventListener('scroll', () => { if (active()) trial.navigation.scrollEvents++; }, true);
  document.addEventListener('visibilitychange', () => { if (active() && document.hidden) trial.navigation.hiddenEvents++; });
  window.addEventListener('beforeunload', e => { if (trial) { e.preventDefault(); e.returnValue = ''; } });
}
