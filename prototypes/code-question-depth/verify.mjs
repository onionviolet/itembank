import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {tasks, orders, sourceFor, makeTrial, commitPrediction, finishTrial, packet} from './prototype.js';
const response = {trace: ['unsure', 'unsure', 'unsure'], firstMistakenRow: 'unsure', proposedReplacement: 'unsure', finalPrediction: 'unsure', explanation: 'unsure'};
for (const [assignment, sequence] of Object.entries(orders)) {
  assert.deepEqual(new Set(sequence.map(t => t[0])), new Set(['A', 'B']));
  assert.deepEqual(new Set(sequence.map(t => t[1])), new Set(['D1', 'D2']));
  const trials = sequence.map(([id, depth], index) => {
    const trial = makeTrial(id, depth, index + 1, 100);
    assert.equal(finishTrial(trial, response, 150), false);
    assert.equal(commitPrediction(trial, '  ', 200), false);
    assert.equal(commitPrediction(trial, 'unsure', 200), true);
    assert.equal(commitPrediction(trial, 'changed', 250), false);
    assert.equal(trial.initialPrediction, 'unsure');
    assert.equal(finishTrial(trial, {...response, explanation: ''}, 300), false);
    if (depth === 'D2') for (const trace of [[], ['1'], ['1', '', '3']]) assert.equal(finishTrial(trial, {...response, trace}, 300), false);
    assert.equal(finishTrial(trial, response, 500), true);
    assert.equal(finishTrial(trial, response, 600), false);
    assert.equal(trial.completionMs, 400); assert.equal(trial.predictionMs, 100); assert.equal(trial.reasoningMs, 300);
    assert.equal(trial.humanReview.taskSuccess, 'unreviewed');
    assert.equal(trial.trace.length, depth === 'D2' ? 3 : 0);
    return trial;
  });
  assert.equal(packet(assignment, trials.slice(0, 1)).complete, false);
  assert.equal(JSON.parse(JSON.stringify(packet(assignment, trials))).complete, true);
}
for (const id of Object.keys(tasks)) for (const depth of ['D1', 'D2']) {
  assert.equal(Object.values(orders).filter(seq => seq[0][0] === id && seq[0][1] === depth).length, 1);
}
const [html, js, manual] = await Promise.all(['index.html', 'prototype.js', 'manual.html'].map(p => readFile(new URL(p, import.meta.url), 'utf8')));
for (const token of ['Commit prediction', 'Text trace fallback', 'aria-label="Python source"', 'role="status"', 'manual.html']) assert.ok(html.includes(token), token);
for (const id of Object.keys(tasks)) assert.ok(manual.includes(sourceFor(id)), `static source parity ${id}`);
for (const token of ['Task success:', 'First mistaken state:', 'Explanation quality:', 'Total seconds', 'Burden (0 to 3)']) assert.ok(manual.includes(token), token);
assert.ok(!/expectedTrace|checkTrace|eval\s*\(|new Function|fetch\s*\(|XMLHttpRequest|WebSocket|sendBeacon|localStorage/.test(js));
assert.ok(!/https?:\/\//.test(html + js + manual));
console.log('ok: four balanced orders, prediction-first D1/D2, no key or scoring, local observation export, static parity');
