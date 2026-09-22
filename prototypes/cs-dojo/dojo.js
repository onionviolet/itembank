'use strict';
(() => {
  const lessons = window.DOJO_LESSONS;
  const $ = (id) => document.getElementById(id);
  const initial = (lesson) => ({files: {...lesson.files}, file: Object.keys(lesson.files)[0], prediction: '', reflection: '', output: [], observations: [], status: 'Ready', state: 'ready', snapshot: '', ran: false, stale: false});
  const drafts = new Map(lessons.map((lesson) => [lesson.id, initial(lesson)]));
  const storageKey = 'itembank-cs-dojo-drafts-v1';
  let storageAvailable = true;
  let saved = {};
  try {
    const raw = localStorage.getItem(storageKey);
    if (raw) {
      try { saved = JSON.parse(raw); }
      catch { saved = {}; }
    }
    if (saved && saved.version === 1 && saved.lessons && typeof saved.lessons === 'object') {
      for (const lesson of lessons) {
        const record = saved.lessons[lesson.id];
        if (!record || !record.files || typeof record.files !== 'object') continue;
        const names = Object.keys(lesson.files);
        if (!names.every((name) => typeof record.files[name] === 'string' && record.files[name].length <= 30000)) continue;
        if (typeof record.prediction !== 'string' || record.prediction.length > 30000 || typeof record.reflection !== 'string' || record.reflection.length > 30000) continue;
        drafts.set(lesson.id, {...initial(lesson), files: Object.fromEntries(names.map((name) => [name, record.files[name]])), file: names.includes(record.file) ? record.file : names[0], prediction: record.prediction, reflection: record.reflection});
      }
    }
  } catch { storageAvailable = false; }
  let active = 0;
  let execution = null;
  let exportURL = null;
  const current = () => drafts.get(lessons[active].id);
  const setText = (id, value) => { $(id).textContent = value; };
  let codeView = null;
  let loadingCode = false;

  function indentCodeMirror(view, outdent) {
    if (view.state.readOnly) return true;
    const selection = view.state.selection.main;
    const last = selection.to > selection.from && view.state.doc.sliceString(selection.to - 1, selection.to) === '\n' ? selection.to - 1 : selection.to;
    const changes = [];
    for (let line = view.state.doc.lineAt(selection.from).number; line <= view.state.doc.lineAt(last).number; line++) {
      const item = view.state.doc.line(line);
      if (outdent) {
        const spaces = item.text.match(/^ {1,2}/)?.[0].length || 0;
        if (spaces) changes.push({from: item.from, to: item.from + spaces, insert: ''});
      } else changes.push({from: item.from, insert: '  '});
    }
    if (changes.length) view.dispatch({changes});
    return true;
  }

  if (window.CodeMirror) {
    const CM = window.CodeMirror;
    const readOnly = new CM.Compartment();
    const view = new CM.EditorView({
      parent: $('editor-mount'),
      extensions: [
        CM.lineNumbers(), CM.history(),
        CM.keymap.of([
          {key: 'Ctrl-]', run: (editor) => indentCodeMirror(editor, false)},
          {key: 'Meta-]', run: (editor) => indentCodeMirror(editor, false)},
          {key: 'Ctrl-[', run: (editor) => indentCodeMirror(editor, true)},
          {key: 'Meta-[', run: (editor) => indentCodeMirror(editor, true)},
          {key: 'Ctrl-Enter', run: () => { run(); return true; }},
          {key: 'Meta-Enter', run: () => { run(); return true; }},
          {key: 'Mod-z', run: CM.undo}, {key: 'Mod-y', run: CM.redo}, {key: 'Mod-Shift-z', run: CM.redo},
        ]),
        readOnly.of(CM.EditorState.readOnly.of(false)),
        CM.EditorView.updateListener.of((update) => {
          if (update.docChanged && !loadingCode) {
            $('editor').value = update.state.doc.toString();
            $('editor').dispatchEvent(new Event('input', {bubbles: true}));
          }
          position();
        }),
      ],
    });
    codeView = {view, readOnly};
    $('editor').hidden = true;
    $('line-numbers').hidden = true;
    $('editor-mount').hidden = false;
  }
  const getCode = () => codeView ? codeView.view.state.doc.toString() : $('editor').value;
  const focusCode = () => codeView ? codeView.view.focus() : $('editor').focus();
  function setCode(value) {
    $('editor').value = value;
    if (codeView && getCode() !== value) {
      loadingCode = true;
      codeView.view.dispatch({changes: {from: 0, to: codeView.view.state.doc.length, insert: value}});
      loadingCode = false;
    }
  }
  function setCodeReadOnly(value) {
    $('editor').readOnly = value;
    if (codeView) codeView.view.dispatch({effects: codeView.readOnly.reconfigure(window.CodeMirror.EditorState.readOnly.of(value))});
  }
  window.DojoEditor = {
    getValue: getCode,
    setValue: (value) => { setCode(value); $('editor').dispatchEvent(new Event('input', {bubbles: true})); position(); },
    focus: focusCode,
    select: (from, to) => {
      if (codeView) codeView.view.dispatch({selection: {anchor: from, head: to}});
      else $('editor').setSelectionRange(from, to);
    },
  };

  function saveDrafts() {
    if (!storageAvailable) return;
    const saved = {version: 1, lessons: {}};
    for (const lesson of lessons) {
      const {files, file, prediction, reflection} = drafts.get(lesson.id);
      if (Object.values(files).some((text) => text.length > 30000) || prediction.length > 30000 || reflection.length > 30000) {
        setText('draft-indicator', 'Draft too large to save · export your draft');
        return;
      }
      saved.lessons[lesson.id] = {files, file, prediction, reflection};
    }
    try {
      localStorage.setItem(storageKey, JSON.stringify(saved));
      setText('draft-indicator', 'Draft saved on this device');
    } catch {
      storageAvailable = false;
      setText('draft-indicator', 'Local save unavailable · export your draft');
    }
  }

  function position() {
    if (codeView) {
      const view = codeView.view;
      const head = view.state.selection.main.head;
      const line = view.state.doc.lineAt(head);
      setText('cursor-position', `Line ${line.number}, column ${head - line.from + 1}`);
      return;
    }
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
        saveDrafts();
        renderFiles();
        focusCode();
      });
      $('file-tabs').append(button);
    }
    setCode(draft.files[draft.file]);
    const language = lessons[active].language === 'python' ? 'Python' : 'JavaScript';
    setText('editor-label', `${language} code editor: ${draft.file}`);
    if (codeView) codeView.view.contentDOM.setAttribute('aria-label', `${language} code editor: ${draft.file}`);
    setText('entry-label', `Runs ${lessons[active].entry}`);
    setCodeReadOnly(Boolean(execution));
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
    setCodeReadOnly(Boolean(execution));
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
      small.textContent = item.navLabel;
      label.append(strong, small);
      button.append(number, label);
      button.addEventListener('click', () => navigate(index));
      $('activity-nav').append(button);
    });
    setText('family', `Unit 01 / ${lesson.number} / ${lesson.family}`);
    setText('language-label', lesson.language === 'python' ? 'Python' : 'JavaScript');
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

  function indentSelection(outdent) {
    const editor = $('editor');
    const value = editor.value;
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const lineStart = value.lastIndexOf('\n', start - 1) + 1;
    const lineEnd = end > start && value[end - 1] === '\n' ? end - 1 : end;
    const segment = value.slice(lineStart, lineEnd);
    const changed = segment.split('\n').map((line) => outdent ? line.replace(/^ {1,2}/, '') : `  ${line}`).join('\n');
    editor.setRangeText(changed, lineStart, lineEnd, 'select');
    const firstDelta = changed.split('\n')[0].length - segment.split('\n')[0].length;
    editor.setSelectionRange(Math.max(lineStart, start + firstDelta), lineStart + changed.length);
    editor.dispatchEvent(new Event('input', {bubbles: true}));
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
    const python = lesson.language === 'python';
    draft.status = python ? 'Loading Python' : 'Running';
    draft.state = 'running';
    let worker;
    try { worker = python ? new Worker('python-runner.js', {type: 'module'}) : new Worker('runner.js'); }
    catch {
      draft.status = 'Execution unavailable';
      draft.state = 'unavailable';
      draft.output = ['Open the dedicated loopback preview to run code. You can still read the unit and export your draft.'];
      renderResults();
      return;
    }
    const timedOut = () => {
      draft.output.push('Stopped after 2 seconds. Check the loop condition, then try again. This is not a correctness result.');
      finish('Time limit reached', 'timeout');
    };
    execution = {worker, draft, messages: 0, characters: 0, timer: setTimeout(() => {
      if (python) {
        draft.output.push('Python did not load within 20 seconds. You can still read and export this activity.');
        finish('Python unavailable', 'unavailable');
      } else timedOut();
    }, python ? 20000 : 2000)};
    worker.addEventListener('message', ({data}) => {
      if (!execution || execution.worker !== worker) return;
      if (!data || typeof data !== 'object') return;
      if (python && data.type === 'ready') {
        clearTimeout(execution.timer);
        execution.timer = setTimeout(timedOut, 2000);
        draft.status = 'Running';
        worker.postMessage({files: {...draft.files}, entry: lesson.entry});
        renderResults();
        return;
      }
      if (data.type === 'unavailable') {
        draft.output.push('Python could not load. The plain-text unit and draft export remain available.');
        finish('Python unavailable', 'unavailable');
        return;
      }
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
    if (!python) worker.postMessage({files: {...draft.files}, entry: lesson.entry});
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
      for (const [name, text] of Object.entries(draft.files)) lines.push(`#### ${name}`, '', fence(text, lesson.language), '');
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
    setText('export-status', `Draft download requested with all ${lessons.length} activities. Keep the file before closing this tab.`);
  }

  $('editor').addEventListener('input', () => { current().files[current().file] = getCode(); markStale(); position(); saveDrafts(); });
  $('editor').addEventListener('scroll', position);
  $('editor').addEventListener('click', position);
  $('editor').addEventListener('keyup', position);
  $('editor').addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') { event.preventDefault(); run(); }
    if ((event.ctrlKey || event.metaKey) && (event.code === 'BracketRight' || event.code === 'BracketLeft')) { event.preventDefault(); indentSelection(event.code === 'BracketLeft'); }
  });
  $('indent').addEventListener('click', () => { if (codeView) indentCodeMirror(codeView.view, false); else indentSelection(false); focusCode(); });
  $('outdent').addEventListener('click', () => { if (codeView) indentCodeMirror(codeView.view, true); else indentSelection(true); focusCode(); });
  $('prediction').addEventListener('input', () => { current().prediction = $('prediction').value; setText('prediction-help', 'A prediction opens the first run. It is not graded.'); saveDrafts(); });
  $('reflection').addEventListener('input', () => { current().reflection = $('reflection').value; saveDrafts(); });
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
    saveDrafts();
    $('reset-dialog').close();
    render();
    focusCode();
  });
  $('reset-dialog').addEventListener('close', () => $('reset').focus());
  window.addEventListener('pagehide', () => { finish('Stopped on page exit', 'stopped'); if (exportURL) URL.revokeObjectURL(exportURL); });
  render();
  if (!storageAvailable) setText('draft-indicator', 'Local save unavailable · export your draft');
})();
