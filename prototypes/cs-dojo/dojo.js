'use strict';
(() => {
  const lessons = window.DOJO_LESSONS;
  const $ = (id) => document.getElementById(id);
  const initial = (lesson) => ({files: {...lesson.files}, file: Object.keys(lesson.files)[0], prediction: '', reflection: '', output: [], observations: [], status: 'Ready', state: 'ready', snapshot: '', ran: false, stale: false});
  const drafts = new Map(lessons.map((lesson) => [lesson.id, initial(lesson)]));
  let active = 0;
  let execution = null;
  let exportURL = null;
  const current = () => drafts.get(lessons[active].id);
  const setText = (id, value) => { $(id).textContent = value; };

  function position() {
    const editor = $('editor');
    const before = editor.value.slice(0, editor.selectionStart);
    setText('cursor-position', `Line ${before.split('\n').length}, column ${before.length - before.lastIndexOf('\n')}`);
    setText('line-numbers', Array.from({length: editor.value.split('\n').length}, (_, i) => i + 1).join('\n'));
    $('line-numbers').scrollTop = editor.scrollTop;
  }

  function markStale() {
    const draft = current();
    if (draft.ran) {
      draft.stale = true;
      renderResults();
    }
  }

  function renderFiles() {
    const draft = current();
    $('file-tabs').replaceChildren();
    for (const name of Object.keys(draft.files)) {
      const button = document.createElement('button');
      button.textContent = name;
      button.setAttribute('aria-pressed', String(name === draft.file));
      button.addEventListener('click', () => {
        draft.file = name;
        renderFiles();
        $('editor').focus();
      });
      $('file-tabs').append(button);
    }
    $('editor').value = draft.files[draft.file];
    setText('editor-label', `JavaScript code editor: ${draft.file}`);
    setText('entry-label', `Runs ${lessons[active].entry}`);
    $('editor').readOnly = Boolean(execution);
    position();
  }

  function renderResults() {
    const draft = current();
    setText('run-state', draft.status);
    $('run-state').dataset.state = draft.state;
    setText('run-help', draft.stale ? 'Code has changed. These observations belong to the previous run.' : execution ? 'Running in a fresh worker. You can stop at any time.' : draft.ran ? 'Compare the observed behavior with your prediction and examples.' : 'Run the program to inspect its output.');
    setText('output', draft.output.length ? draft.output.join('\n') : draft.ran ? 'No console output.' : 'Output will appear here.');
    $('prediction-snapshot').hidden = !draft.snapshot;
    setText('prediction-snapshot', `Your prediction at this run:\n${draft.snapshot}`);
    $('observations').hidden = draft.observations.length === 0;
    $('observation-rows').replaceChildren();
    for (const observation of draft.observations) {
      const row = document.createElement('tr');
      for (const key of ['label', 'actual', 'expected']) {
        const cell = document.createElement('td');
        cell.textContent = observation[key];
        row.append(cell);
      }
      $('observation-rows').append(row);
    }
    $('run').disabled = Boolean(execution);
    $('stop').hidden = !execution;
    $('editor').readOnly = Boolean(execution);
  }

  function finish(status, state) {
    if (!execution) return;
    const {worker, timer, draft} = execution;
    worker.terminate();
    clearTimeout(timer);
    execution = null;
    draft.status = status;
    draft.state = state;
    renderResults();
  }

  function render(moveFocus = false) {
    const lesson = lessons[active];
    const draft = current();
    $('activity-nav').replaceChildren();
    lessons.forEach((item, index) => {
      const button = document.createElement('button');
      button.className = 'nav-activity';
      if (index === active) button.setAttribute('aria-current', 'step');
      const number = document.createElement('span');
      number.className = 'nav-number';
      number.textContent = item.number;
      const label = document.createElement('span');
      const strong = document.createElement('strong');
      strong.textContent = item.family;
      const small = document.createElement('small');
      small.textContent = ['Trace a boundary', 'Repair the calculation', 'A small module'][index];
      label.append(strong, small);
      button.append(number, label);
      button.addEventListener('click', () => navigate(index));
      $('activity-nav').append(button);
    });
    setText('family', `Unit 01 / ${lesson.number} / ${lesson.family}`);
    setText('activity-title', lesson.title);
    document.title = `${lesson.family} | CS Dojo | Itembank`;
    setText('intro', lesson.intro);
    setText('task-text', lesson.task);
    setText('objective-id', lesson.objective);
    setText('objective-text', lesson.objectiveText);
    setText('context-text', lesson.context);
    setText('source-label', lesson.sourceLabel);
    setText('worked-text', lesson.example);
    setText('reflection-label', lesson.reflection);
    setText('next-note', lesson.next);
    $('prediction-section').hidden = !lesson.prediction;
    $('prediction').value = draft.prediction;
    $('reflection').value = draft.reflection;
    $('previous').disabled = active === 0;
    $('next').disabled = active === lessons.length - 1;
    document.querySelectorAll('.brief details').forEach((details) => { details.open = false; });
    renderFiles();
    renderResults();
    if (moveFocus) $('activity-title').focus();
  }

  function navigate(index) {
    if (index < 0 || index >= lessons.length || index === active) return;
    finish('Stopped on activity change', 'stopped');
    active = index;
    render(true);
  }

  function run() {
    if (execution) return;
    const lesson = lessons[active];
    const draft = current();
    if (lesson.prediction && !draft.prediction.trim()) {
      setText('prediction-help', 'Write a prediction first, then run to compare it with the output.');
      $('prediction').focus();
      return;
    }
    if (!Object.values(draft.files).every((text) => text.length <= 30000)) {
      draft.status = 'File too large';
      draft.state = 'error';
      draft.output = ['This prototype accepts at most 30,000 characters per provided file. Shorten the file and run again.'];
      renderResults();
      return;
    }
    draft.output = [];
    draft.observations = [];
    draft.snapshot = lesson.prediction ? draft.prediction : '';
    draft.ran = true;
    draft.stale = false;
    draft.status = 'Running';
    draft.state = 'running';
    let worker;
    try { worker = new Worker('runner.js'); }
    catch {
      draft.status = 'Execution unavailable';
      draft.state = 'unavailable';
      draft.output = ['Open the dedicated loopback preview to run code. You can still read the unit and export your draft.'];
      renderResults();
      return;
    }
    execution = {worker, draft, messages: 0, characters: 0, timer: setTimeout(() => {
      draft.output.push('Stopped after 2 seconds. Check the loop condition, then try again. This is not a correctness result.');
      finish('Time limit reached', 'timeout');
    }, 2000)};
    worker.addEventListener('message', ({data}) => {
      if (!execution || execution.worker !== worker) return;
      if (!data || typeof data !== 'object') return;
      execution.messages += 1;
      if (execution.messages > 85 || data.type === 'limit') {
        draft.output.push('Output limit reached. Print fewer values, then run again.');
        finish('Output limit reached', 'limit');
        return;
      }
      const value = (key) => typeof data[key] === 'string' ? data[key].slice(0, 2000) : '';
      if (data.type === 'log' || data.type === 'error') {
        const text = value('text');
        execution.characters += text.length;
        draft.output.push(text);
      } else if (data.type === 'observation') {
        const observation = {label: value('label'), actual: value('actual'), expected: value('expected')};
        execution.characters += Object.values(observation).join('').length;
        draft.observations.push(observation);
      }
      if (execution.characters > 16000) {
        draft.output.push('Output limit reached. Print fewer values, then run again.');
        finish('Output limit reached', 'limit');
      } else if (data.type === 'done') finish('Run finished', 'done');
      else if (data.type === 'error') finish('Execution error', 'error');
      else renderResults();
    });
    worker.addEventListener('error', (event) => {
      event.preventDefault();
      if (!execution || execution.worker !== worker) return;
      draft.output.push('The worker could not execute this program. Check the code or reopen the dedicated preview, then retry.');
      finish('Execution unavailable', 'unavailable');
    });
    worker.postMessage({files: {...draft.files}, entry: lesson.entry});
    renderResults();
  }

  function fence(text, language = '') {
    const longest = Math.max(2, ...(text.match(/`+/g) || []).map((part) => part.length));
    const marker = '`'.repeat(longest + 1);
    return `${marker}${language}\n${text}\n${marker}`;
  }

  function exportDraft() {
    const lines = ['# CS Dojo learner draft', '', 'Status: unreviewed learner artifact. No score, accepted course revision, or assessment evidence.', '', 'Source: SYN-CS-UNIT-01, original synthetic programming unit.', '', 'The code below is source text. Importing this document must not execute it.', ''];
    for (const lesson of lessons) {
      const draft = drafts.get(lesson.id);
      lines.push(`## ${lesson.number}. ${lesson.title}`, '', `Objective: ${lesson.objective}. ${lesson.objectiveText}`, '', `Source locator: ${lesson.source}`, '', '### Code', '');
      for (const [name, text] of Object.entries(draft.files)) lines.push(`#### ${name}`, '', fence(text, 'javascript'), '');
      if (lesson.prediction) lines.push('### Prediction', '', fence(draft.prediction || '(Not written)'), '');
      lines.push('### Reflection', '', fence(draft.reflection || '(Not written)'), '', '### Last execution observation', '', `State: ${draft.status}. ${draft.stale ? 'Code changed after this run.' : ''}`, '');
      if (draft.snapshot) lines.push('Prediction at this run:', '', fence(draft.snapshot), '');
      for (const row of draft.observations) lines.push(fence(`${row.label}\nObserved: ${row.actual}\nExpected: ${row.expected}`), '');
      lines.push(fence(draft.output.join('\n') || '(No output recorded)'), '');
    }
    if (exportURL) URL.revokeObjectURL(exportURL);
    exportURL = URL.createObjectURL(new Blob([lines.join('\n')], {type: 'text/markdown;charset=utf-8'}));
    const anchor = document.createElement('a');
    anchor.href = exportURL;
    anchor.download = 'cs-dojo-learner-draft.md';
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setText('export-status', 'Draft download requested with all three activities. Keep the file before closing this tab.');
  }

  $('editor').addEventListener('input', () => { current().files[current().file] = $('editor').value; markStale(); position(); });
  $('editor').addEventListener('scroll', position);
  $('editor').addEventListener('click', position);
  $('editor').addEventListener('keyup', position);
  $('editor').addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') { event.preventDefault(); run(); }
  });
  $('prediction').addEventListener('input', () => { current().prediction = $('prediction').value; setText('prediction-help', 'A prediction opens the first run. It is not graded.'); });
  $('reflection').addEventListener('input', () => { current().reflection = $('reflection').value; });
  $('run').addEventListener('click', run);
  $('stop').addEventListener('click', () => { finish('Stopped by you', 'stopped'); $('run').focus(); });
  $('previous').addEventListener('click', () => navigate(active - 1));
  $('next').addEventListener('click', () => navigate(active + 1));
  $('export').addEventListener('click', exportDraft);
  $('source-open').addEventListener('click', () => {
    const lesson = lessons[active];
    setText('source-title', lesson.sourceLabel);
    setText('source-text', lesson.sourceText);
    $('source-anchor').href = lesson.source;
    $('source-dialog').showModal();
  });
  $('source-close').addEventListener('click', () => $('source-dialog').close());
  $('source-dialog').addEventListener('close', () => $('source-open').focus());
  $('reset').addEventListener('click', () => $('reset-dialog').showModal());
  $('reset-cancel').addEventListener('click', () => $('reset-dialog').close());
  $('reset-confirm').addEventListener('click', () => {
    finish('Stopped for reset', 'stopped');
    drafts.set(lessons[active].id, initial(lessons[active]));
    $('reset-dialog').close();
    render();
    $('editor').focus();
  });
  $('reset-dialog').addEventListener('close', () => $('reset').focus());
  window.addEventListener('pagehide', () => { finish('Stopped on page exit', 'stopped'); if (exportURL) URL.revokeObjectURL(exportURL); });
  render();
})();
