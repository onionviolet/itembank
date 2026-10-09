"""Trusted, deterministic enhancement for an explicitly authored Example.

No authored code, requests, scoring or accepted-content writes. Exploration
uses bounded tab-local presentation storage only with admitted identity.
The model owns parsing. This module receives validated scalar data only.
"""
import html


def exploration_attributes(lesson_id=None, revision_id=None, occurrence_id=None):
    """Expose caller-admitted identity, never infer it from titles or URLs."""
    values = (lesson_id, revision_id, occurrence_id)
    if any(not isinstance(value, str) or not value.strip() or len(value) > 256
           or any(ord(char) < 32 for char in value) for value in values):
        return ""
    return ''.join(' data-exploration-%s="%s"' %
                   (name, html.escape(value, quote=True))
                   for name, value in zip(('lesson', 'revision', 'occurrence'), values))


# One bounded presentation ledger shared by these trusted enhancements.
# Every read rechecks the supplied revision. There is no content/evidence write.
EXPLORATION_JS = """
if (!window.itembankLessonExploration) {
  window.itembankLessonExploration = function(root, kind, valid) {
    const owner = root.closest('[data-exploration-lesson]');
    const note = kind === 'reading' ? null : root.querySelector('.exploration-continuity');
    let available = false, storage, recovery = '';
    const key = 'itembank:lesson-exploration:v1';
    const ids = owner ? ['lesson','occurrence','revision'].map(name =>
      owner.getAttribute('data-exploration-' + name)) : [];
    const admitted = ids.length === 3 && ids.every(id => typeof id === 'string' &&
      id.trim() && id.length <= 256 && !/[\\x00-\\x1f]/.test(id));
    const section = root.closest('section[id]') || owner;
    const peers = kind === 'reading' && root === owner ? [root] :
      section ? Array.from(section.querySelectorAll('.lesson-' + kind)) : [];
    const shape = kind === 'reading' ? Array.from(root.querySelectorAll('.stage')).map(stage =>
      [stage.closest('section[id]') && stage.closest('section[id]').id || '', stage.dataset.stage]) :
      section && section.id || '';
    const slot = JSON.stringify([kind, shape, peers.indexOf(root)]);
    function notice() {
      if (note) note.textContent = available ?
        recovery + 'Exploration stays in this tab for this reading revision. Reset clears it.' :
        'Exploration is available on this page. Tab storage is unavailable; changes may not survive reopening.';
    }
    function ledger() {
      const raw = storage.getItem(key);
      if (!raw) return {version:1, entries:[]};
      if (raw.length > 32768) throw new Error('Exploration storage is too large');
      const data = JSON.parse(raw);
      if (!data || data.version !== 1 || !Array.isArray(data.entries) || data.entries.length > 16 ||
          data.entries.some(entry => !entry || !Array.isArray(entry.identity) ||
            entry.identity.length !== 2 || entry.identity.some(id => typeof id !== 'string') ||
            typeof entry.revision !== 'string' || !Array.isArray(entry.states) || entry.states.length > 32 ||
            entry.states.some(pair => !Array.isArray(pair) || pair.length !== 2 || typeof pair[0] !== 'string')))
        throw new Error('Exploration storage is invalid');
      return data;
    }
    function matching(entry) {return entry.identity[0] === ids[0] && entry.identity[1] === ids[1];}
    function put(data) {
      const raw = JSON.stringify(data);
      if (raw.length > 32768) throw new Error('Exploration storage is full');
      if (!data.entries.length) storage.removeItem(key);
      else storage.setItem(key, raw);
    }
    if (admitted && peers.indexOf(root) >= 0) {
      try {
        storage = window.sessionStorage;
        // A newly opened same-origin tab may inherit its opener's storage.
        // Give that tab an independent ledger; reloads retain its new token.
        const tabKey = key + ':tab';
        let token = storage.getItem(tabKey);
        if (window.opener && token && window.opener.itembankExplorationTab === token) {
          storage.removeItem(key); token = null;
        }
        token = token || window.crypto.randomUUID();
        storage.setItem(tabKey, token);
        window.itembankExplorationTab = token;
        let data;
        try {data = ledger();} catch (_) {
          storage.removeItem(key); data = {version:1,entries:[]};
          recovery = 'Previous exploration was unreadable and has been cleared. ';
        }
        const fresh = data.entries.filter(entry => !matching(entry) || entry.revision === ids[2]);
        if (fresh.length !== data.entries.length) {
          data.entries = fresh; put(data); recovery = 'Reading changed; previous exploration was cleared. ';
        }
        available = true;
      } catch (_) {available = false;}
    }
    notice();
    function use(action) {
      if (!available) return null;
      try {return action(ledger());}
      catch (_) {
        available = false;
        try {storage.removeItem(key);} catch (_) {}
        notice(); return null;
      }
    }
    return {
      read: () => use(data => {
        const entry = data.entries.find(item => matching(item) && item.revision === ids[2]);
        const pair = entry && entry.states.find(item => item[0] === slot);
        return pair && valid(pair[1]) ? pair[1] : null;
      }),
      write: value => {
        if (!valid(value)) return;
        use(data => {
          let entry = data.entries.find(item => matching(item) && item.revision === ids[2]);
          data.entries = data.entries.filter(item => !matching(item));
          entry = entry || {identity:ids.slice(0,2),revision:ids[2],states:[]};
          entry.states = entry.states.filter(pair => pair[0] !== slot);
          entry.states.push([slot,value]); entry.states = entry.states.slice(-32);
          data.entries.push(entry); data.entries = data.entries.slice(-16); put(data);
        });
      },
      clear: () => use(data => {
        data.entries.forEach(entry => {if (matching(entry)) entry.states = entry.states.filter(pair => pair[0] !== slot);});
        data.entries = data.entries.filter(entry => entry.states.length); put(data);
      })
    };
  };
}
"""


CSS = """
.lesson-comparison {overflow-wrap:anywhere}
.lesson-comparison strong {font-weight:700}
.comparison-static strong {text-shadow:0 0 .45em color-mix(in srgb,var(--accent) 30%,transparent)}
.comparison-static {white-space:pre-line}
.comparison-controls {margin-block:1.5rem;border-top:1px solid var(--line);padding-top:1rem;
  font-family:var(--font-chrome)}
.comparison-controls label {display:block}
.comparison-controls input[type=range], .comparison-meter-b {position:absolute;width:1px;height:1px;
  min-height:0;padding:0;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
.comparison-adjust {display:flex;align-items:end;flex-wrap:wrap;gap:.5rem;margin-block:.75rem}
.comparison-adjust label {font-size:var(--text-xs);color:var(--mut)}
.comparison-adjust input {display:block;width:7rem;max-width:100%;min-height:44px;
  border:1px solid var(--edge);border-radius:var(--r-1);background:var(--bg);color:var(--ink);
  padding:.5rem;font:inherit;font-size:var(--text-body);font-variant-numeric:tabular-nums}
.comparison-controls button {min-width:44px;min-height:44px;padding:.5rem .75rem;
  border:1px solid var(--edge);border-radius:var(--r-1);background:var(--bg);color:var(--ink);font:inherit}
.comparison-controls button:disabled {opacity:.4}
.comparison-controls :is(input,button):focus-visible {outline:2px solid var(--accent);outline-offset:3px}
.comparison-bars {display:grid;gap:.75rem;margin-block:1rem;font-variant-numeric:tabular-nums}
.comparison-bars meter:not(.comparison-meter-b) {width:calc(100% - 44px);height:1.5rem;margin-inline:22px}
.comparison-direct {position:relative;height:52px;margin-inline:22px;touch-action:pan-y}
.comparison-direct-track {position:absolute;inset:22px 0 auto;height:8px;background:var(--line);border-radius:var(--r-1)}
.comparison-direct-fill {height:100%;width:var(--comparison-b);background:var(--accent);border-radius:inherit}
.comparison-controls .comparison-handle {position:absolute;top:4px;left:var(--comparison-b);transform:translateX(-50%);
  width:44px;height:44px;padding:0;touch-action:none;cursor:ew-resize;border-color:var(--accent);font-weight:700}
.comparison-handle[data-pending="1"] {background:var(--accent);color:var(--bg)}
.comparison-controls:has(input[type=range]:focus-visible) .comparison-handle {outline:2px solid var(--accent);outline-offset:3px}
.comparison-gesture-help {font-size:var(--text-xs);color:var(--mut)}
.exploration-continuity {font-size:var(--text-xs);color:var(--mut)}
.comparison-result {font-weight:600;border-top:1px solid var(--line);padding-top:.75rem}
@media print {.comparison-controls {display:none!important}.comparison-static strong {text-shadow:none}}
@media (forced-colors:active) {.lesson-comparison strong {color:CanvasText;background:Canvas;text-decoration:underline;text-shadow:none}}
"""


JS = "<script>" + EXPLORATION_JS + """
(() => {
  function initialize() {
    document.querySelectorAll('.lesson-comparison').forEach(root => {
      if (root.dataset.initialized === '1') return;
      const input = root.querySelector('input[type=range]');
      const number = root.querySelector('.comparison-number');
      const decrease = root.querySelector('.comparison-decrease');
      const increase = root.querySelector('.comparison-increase');
      const reset = root.querySelector('.comparison-reset');
      const cancel = root.querySelector('.comparison-cancel');
      const controls = root.querySelector('.comparison-controls');
      const direct = root.querySelector('.comparison-direct');
      const handle = root.querySelector('.comparison-handle');
      if (!input || !number || !decrease || !increase || !reset || !controls || !direct || !handle) return;
      const a = Number(input.dataset.a), initial = Number(input.defaultValue);
      const maximum = Number(input.max), unit = input.dataset.unit;
      if (![a, initial, maximum].every(Number.isSafeInteger) || maximum < 1 ||
          maximum > 10000 || a < 0 || a > maximum || initial < 0 || initial > maximum) return;
      let gesture = null;
      const state = window.itembankLessonExploration(root, 'comparison', value =>
        Number.isSafeInteger(value) && value >= 0 && value <= maximum);
      const restored = state.read();
      function update(remember = true) {
        let b = Number(input.value);
        if (!Number.isSafeInteger(b) || b < 0 || b > maximum) b = initial;
        input.value = String(b);
        number.value = String(b);
        number.setCustomValidity('');
        decrease.disabled = b === 0;
        increase.disabled = b === maximum;
        const delta = b - a;
        root.querySelector('.comparison-b').textContent = String(b);
        root.querySelector('.comparison-meter-b').value = b;
        direct.style.setProperty('--comparison-b', (b / maximum * 100) + '%');
        handle.dataset.pending = gesture && gesture.moved ? '1' : '0';
        if (cancel) cancel.disabled = !gesture && number.value === input.value;
        root.querySelector('.comparison-result').textContent =
          'B − A = ' + delta + ' ' + unit + '. ' +
          (delta === 0 ? 'Equal quantities.' : 'B is ' + Math.abs(delta) + ' ' + unit +
          (delta > 0 ? ' higher.' : ' lower.')) +
          (b === initial ? ' Authored starting value.' : ' Hypothetical value.') +
          (gesture && gesture.moved ? ' Preview. Release to keep; Escape to cancel.' : '');
        if (remember && !gesture) state.write(b);
      }
      function finish(cancelled) {
        if (!gesture) return;
        const previous = gesture;
        gesture = null;
        if (cancelled) input.value = String(previous.start);
        if (handle.hasPointerCapture && handle.hasPointerCapture(previous.id)) {
          handle.releasePointerCapture(previous.id);
        }
        update(!cancelled);
      }
      handle.onpointerdown = event => {
        if (gesture || !event.isPrimary || event.button !== 0) return;
        const bounds = direct.getBoundingClientRect();
        if (!bounds.width) return;
        event.preventDefault();
        input.focus({preventScroll:true});
        const start = Number(input.value);
        gesture = {id:event.pointerId, start, x:event.clientX, y:event.clientY,
          left:bounds.left, width:bounds.width, height:bounds.height,
          offset:event.clientX - (bounds.left + start / maximum * bounds.width), moved:false};
        if (cancel) cancel.disabled = false;
        try { handle.setPointerCapture(event.pointerId); }
        catch (_) { finish(true); }
      };
      function previewPointer(event) {
        if (!gesture || gesture.id !== event.pointerId) return;
        const dx = event.clientX - gesture.x, dy = event.clientY - gesture.y;
        if (!gesture.moved && dx * dx + dy * dy < 16) return;
        gesture.moved = true;
        input.value = String(Math.max(0, Math.min(maximum, Math.round(
          (event.clientX - gesture.left - gesture.offset) / gesture.width * maximum))));
        update();
      }
      handle.onpointermove = previewPointer;
      handle.onpointerup = event => {
        if (gesture && gesture.id === event.pointerId) { previewPointer(event); finish(false); }
      };
      handle.onpointercancel = event => { if (gesture && gesture.id === event.pointerId) finish(true); };
      handle.onlostpointercapture = event => { if (gesture && gesture.id === event.pointerId) finish(true); };
      root.addEventListener('keydown', event => {
        if (event.key === 'Escape') { event.preventDefault(); cancelChange(); }
      });
      ['blur', 'resize', 'pagehide'].forEach(name => window.addEventListener(name, () => finish(true)));
      if (typeof ResizeObserver === 'function') {
        new ResizeObserver(() => {
          if (!gesture) return;
          const bounds = direct.getBoundingClientRect();
          if (bounds.width !== gesture.width || bounds.height !== gesture.height) finish(true);
        }).observe(direct);
      }
      input.addEventListener('blur', () => finish(true));
      function cancelChange() {
        finish(true); number.value = input.value; number.setCustomValidity('');
        if (cancel) cancel.disabled = true;
      }
      if (cancel) {
        cancel.onclick = cancelChange;
        cancel.onpointerdown = event => event.preventDefault();
      }
      input.value = String(restored === null ? initial : restored);
      input.oninput = () => { const value = input.value; finish(true); input.value = value; update(); };
      number.oninput = () => {number.setCustomValidity(''); if (cancel) cancel.disabled = number.value === input.value;};
      number.onchange = () => {
        finish(true);
        const b = Number(number.value);
        if (!number.value || !Number.isSafeInteger(b) || b < 0 || b > maximum) {
          number.setCustomValidity('Enter a whole number from 0 to ' + maximum + '.');
          number.reportValidity();
          return;
        }
        input.value = String(b);
        update();
      };
      decrease.onclick = () => { finish(true); input.value = String(Math.max(0, Number(input.value) - 1)); update(); };
      increase.onclick = () => { finish(true); input.value = String(Math.min(maximum, Number(input.value) + 1)); update(); };
      reset.onclick = () => { finish(true); state.clear(); input.value = String(initial); update(false); };
      update(false);
      root.dataset.initialized = '1';
      controls.hidden = false;
    });
  }
  initialize();
  window.addEventListener('pageshow', initialize);
})();
</script>"""


def render(data, inline):
    """Render static meaning first. Controls stay hidden without script."""
    a, b, maximum = data["a"], data["b"], data["max"]
    unit = html.escape(data["unit"], quote=True)
    return (
        '<div class="lesson-comparison">'
        '<div class="comparison-static">%s</div>'
        '<p>Starting comparison: A = %d %s, B = %d %s. B minus A = %d %s.</p>'
        '<div class="comparison-controls" hidden>'
        '<label>Adjust B (%s), hypothetical values from 0 to %d'
        '<input type="range" min="0" max="%d" step="1" value="%d" '
        'data-a="%d" data-unit="%s"></label>'
        '<div class="comparison-adjust">'
        '<button class="comparison-decrease" type="button" aria-label="Decrease B by 1">−</button>'
        '<label>B value (%s)<input class="comparison-number" type="number" '
        'min="0" max="%d" step="1" value="%d" required></label>'
        '<button class="comparison-increase" type="button" aria-label="Increase B by 1">+</button>'
        '<button class="comparison-reset" type="button">Reset comparison</button></div>'
        '<button class="comparison-cancel" type="button" disabled>Cancel change</button>'
        '<p class="exploration-continuity"></p>'
        '<div class="comparison-bars">'
        '<label>A: %d %s <meter min="0" max="%d" value="%d"></meter></label>'
        '<div>B: <span class="comparison-b">%d</span> %s '
        '<meter class="comparison-meter-b" aria-label="B quantity" min="0" max="%d" value="%d"></meter>'
        '<div class="comparison-direct" aria-hidden="true">'
        '<div class="comparison-direct-track"><div class="comparison-direct-fill"></div></div>'
        '<button class="comparison-handle" type="button" tabindex="-1">B</button></div></div>'
        '<p class="comparison-gesture-help">Drag the B handle to compare quantities. '
        'Release to keep the value; Escape cancels. Tab to adjust B with arrow keys, '
        'or use exact entry and step buttons.</p>'
        '</div><p class="comparison-result" role="status" aria-live="polite"></p>'
        '</div></div>'
        % (inline(data["text"]), a, unit, b, unit, b-a, unit,
           unit, maximum, maximum, b, a, unit, unit, maximum, b, a, unit, maximum, a,
           b, unit, maximum, b))


LINEPLOT_CSS = """
.lesson-lineplot {overflow-wrap:anywhere}
.lineplot-authored,.lineplot-static {white-space:pre-line}
.lineplot-static {margin-block:.75rem}
.lineplot-controls {margin-block:1rem;font-family:var(--font-chrome)}
.lineplot-controls fieldset {min-inline-size:0;margin-block:.75rem;border:1px solid var(--line);padding:1rem}
.lineplot-controls legend {font-weight:600;padding-inline:.4rem}
.lineplot-controls label {display:block;margin-block:.4rem}
.lineplot-controls select,.lineplot-controls button {min-height:44px;max-width:100%;
  border:1px solid var(--edge);border-radius:var(--r-1);background:var(--bg);color:var(--ink);
  font:inherit;padding:.5rem .75rem;margin:.25rem .5rem .25rem 0}
.lineplot-controls label select {display:block}
.lineplot-controls :is(select,button):focus-visible {outline:2px solid var(--accent);outline-offset:3px}
.lineplot-views {display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,16rem),1fr));gap:1rem;margin-block:1rem}
.lineplot-views svg {width:100%;height:auto;max-width:22rem;border:1px solid var(--line)}
.lineplot-views svg text {fill:currentColor;font-family:var(--font-chrome);font-size:var(--text-body)}
.lineplot-line {stroke:var(--accent)}
.lineplot-equation {font-family:var(--font-ledger);font-variant-numeric:tabular-nums}
.lineplot-views table {border-collapse:collapse;width:100%}
.lineplot-views th,.lineplot-views td {padding:.5rem;border:1px solid var(--line);text-align:center}
.lineplot-views p {margin-block:.4rem}
@media print {.lineplot-controls {display:none!important}.lineplot-static {display:block!important}}
"""


LINEPLOT_JS = "<script>" + EXPLORATION_JS + """
(() => {
  function coordinate(x, y) { return (160 + x * 55) + ',' + (120 - y * 17); }
  function initializeLineplot() {
    document.querySelectorAll('.lesson-lineplot').forEach(root => {
      if (root.dataset.initialized === '1') return;
      const m = Number(root.dataset.m), b = Number(root.dataset.b);
      const changed = Number(root.dataset.changedB);
      if (![m,b,changed].every(Number.isSafeInteger) ||
          [m,b,changed].some(n => n < -2 || n > 2) || changed === b) return;
      const controls = root.querySelector('.lineplot-controls');
      const staticView = root.querySelector('.lineplot-static');
      const selection = root.querySelector('.lineplot-prediction');
      const commit = root.querySelector('.lineplot-commit');
      const cancel = root.querySelector('.lineplot-cancel');
      const choice = root.querySelector('.lineplot-choice');
      const manipulate = root.querySelector('.lineplot-manipulate');
      const value = root.querySelector('.lineplot-value');
      const reset = root.querySelector('.lineplot-reset');
      const live = root.querySelector('.lineplot-live');
      const equation = root.querySelector('.lineplot-equation');
      const points = root.querySelectorAll('.lineplot-y');
      const line = root.querySelector('.lineplot-line');
      if (!controls || !staticView || !selection || !commit || !choice ||
          !manipulate || !value || !reset || !live || !equation ||
          points.length !== 3 || !line) return;
      let prediction = '';
      const state = window.itembankLessonExploration(root, 'lineplot', value =>
        value && ['all','origin','none'].includes(value.prediction) &&
        Number.isSafeInteger(value.intercept) && value.intercept >= -2 && value.intercept <= 2);
      const restored = state.read();
      function update(remember = true) {
        const current = Number(value.value);
        if (!Number.isSafeInteger(current) || current < -2 || current > 2) return;
        const shift = current - b;
        equation.textContent = 'y = ' + m + 'x ' + (current < 0 ? '- ' + Math.abs(current) : '+ ' + current);
        [-2,0,2].forEach((x, i) => { points[i].textContent = String(m*x + current); });
        line.setAttribute('points', [-2,0,2].map(x => coordinate(x,m*x+current)).join(' '));
        live.textContent = 'Intercept ' + current + '. At x = -2, 0, 2, y = ' +
          [-2,0,2].map(x => m*x+current).join(', ') + '. Compared with the starting rule, each y value ' +
          (shift > 0 ? 'increases by ' + shift : shift < 0 ?
            'decreases by ' + Math.abs(shift) : 'is unchanged') + '. Slope remains ' + m + '.';
        if (remember && prediction) state.write({prediction,intercept:current});
      }
      function cancelDraft() {
        selection.value = prediction;
        if (cancel) cancel.disabled = true;
      }
      selection.onchange = () => {if (cancel) cancel.disabled = selection.value === prediction;};
      selection.addEventListener('blur', event => {
        if (event.relatedTarget !== commit && event.relatedTarget !== cancel) cancelDraft();
      });
      root.addEventListener('keydown', event => {
        if (event.key === 'Escape') {event.preventDefault(); cancelDraft();}
      });
      window.addEventListener('blur', cancelDraft);
      window.addEventListener('pagehide', cancelDraft);
      if (cancel) cancel.onclick = cancelDraft;
      value.value = String(restored ? restored.intercept : changed);
      function reveal(remember = true) {
        prediction = selection.value;
        if (cancel) cancel.disabled = true;
        choice.textContent = 'Your prediction: ' + selection.options[selection.selectedIndex].text + '.';
        manipulate.hidden = false;
        staticView.hidden = false;
        update(remember);
      }
      commit.onclick = () => {
        if (!selection.value) {
          choice.textContent = 'Choose a prediction before revealing the change.';
          selection.focus();
          return;
        }
        reveal();
        value.focus();
      };
      value.onchange = () => update();
      reset.onclick = () => {
        state.clear(); prediction = ''; cancelDraft(); value.value = String(changed);
        manipulate.hidden = true; staticView.hidden = true;
        choice.textContent = 'Exploration reset. Choose a prediction to start again.';
        selection.focus();
      };
      root.dataset.initialized = '1';
      root.classList.add('lineplot-enhanced');
      staticView.hidden = true;
      controls.hidden = false;
      if (restored) {selection.value = restored.prediction; reveal(false);}
    });
  }
  initializeLineplot();
  window.addEventListener('pageshow', initializeLineplot);
})();
</script>"""


def render_lineplot(data, inline):
    """Render one finite line model with a usable script-free worked state."""
    m, b, changed = data["m"], data["b"], data["changed_b"]
    introduction, static_explanation = data["text"].split("Static explanation:", 1)
    xs = (-2, 0, 2)
    starting = ", ".join("(%d, %d)" % (x, m*x+b) for x in xs)
    later = ", ".join("(%d, %d)" % (x, m*x+changed) for x in xs)
    sign = lambda n: ("- %d" % -n) if n < 0 else ("+ %d" % n)
    return (
        '<div class="lesson-lineplot" data-m="%d" data-b="%d" data-changed-b="%d">'
        '<div class="lineplot-authored">%s</div>'
        '<div class="lineplot-static"><p><strong>Static explanation:</strong> %s</p>'
        '<p>Starting rule: y = %dx %s. Points: %s.</p>'
        '<p>Change only the intercept to %d. The rule becomes y = %dx %s. '
        'Points: %s. Each y value changes by %d and the slope stays %d.</p></div>'
        '<div class="lineplot-controls" hidden>'
        '<fieldset><legend>Predict before changing the intercept</legend>'
        '<label>Which plotted points change when only the intercept changes?'
        '<select class="lineplot-prediction">'
        '<option value="">Choose a prediction</option>'
        '<option value="all">All three points</option><option value="origin">Only the point at x = 0</option>'
        '<option value="none">No points</option></select></label>'
        '<button class="lineplot-commit" type="button">Commit prediction</button>'
        '<button class="lineplot-cancel" type="button" disabled>Cancel prediction</button></fieldset>'
        '<p class="exploration-continuity"></p>'
        '<p class="lineplot-choice" role="status" aria-live="polite"></p>'
        '<div class="lineplot-manipulate" hidden>'
        '<label>Intercept (whole number from -2 to 2)'
        '<select class="lineplot-value">%s</select></label>'
        '<button class="lineplot-reset" type="button">Reset exploration</button>'
        '<div class="lineplot-views">'
        '<div><p class="lineplot-equation"></p>'
        '<svg viewBox="0 0 320 240" role="img" aria-label="Line plot; the adjacent table gives exact coordinates">'
        '<line x1="50" y1="120" x2="270" y2="120" stroke="currentColor"/>'
        '<line x1="160" y1="18" x2="160" y2="222" stroke="currentColor"/>'
        '<polyline class="lineplot-line" fill="none" stroke="currentColor" stroke-width="3" points=""/>'
        '<text x="275" y="124">x</text><text x="164" y="18">y</text></svg></div>'
        '<table><caption>Coordinates for the current rule</caption>'
        '<thead><tr><th scope="col">x</th><th scope="col">y</th></tr></thead>'
        '<tbody><tr><th scope="row">-2</th><td class="lineplot-y"></td></tr>'
        '<tr><th scope="row">0</th><td class="lineplot-y"></td></tr>'
        '<tr><th scope="row">2</th><td class="lineplot-y"></td></tr></tbody></table></div>'
        '<p class="lineplot-live" role="status" aria-live="polite"></p></div></div></div>'
        % (m, b, changed, inline(introduction), inline(static_explanation), m, sign(b),
           html.escape(starting), changed, m, sign(changed),
           html.escape(later), changed-b, m,
           ''.join('<option value="%d">%d</option>' % (n,n) for n in range(-2,3))))
