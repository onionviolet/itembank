"""Trusted, deterministic enhancement for an explicitly authored Example.

No authored code, persistence, requests, scoring or accepted-content writes.
The model owns parsing. This module receives validated scalar data only.
"""
import html


CSS = """
.lesson-comparison {overflow-wrap:anywhere}
.lesson-comparison strong {font-weight:700}
.comparison-static {white-space:pre-line}
.comparison-controls {margin-block:1.5rem;border-top:1px solid var(--line);padding-top:1rem;
  font-family:var(--font-chrome)}
.comparison-controls label {display:block}
.comparison-controls input[type=range] {width:100%;min-height:44px;accent-color:var(--accent)}
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
.comparison-bars meter {width:100%;height:1.5rem}
.comparison-result {font-weight:600;border-top:1px solid var(--line);padding-top:.75rem}
@media print {.comparison-controls {display:none!important}}
@media (forced-colors:active) {.lesson-comparison strong {color:CanvasText;background:Canvas;text-decoration:underline}}
"""


JS = """<script>
(() => {
  function initialize() {
    document.querySelectorAll('.lesson-comparison').forEach(root => {
      if (root.dataset.initialized === '1') return;
      const input = root.querySelector('input[type=range]');
      const number = root.querySelector('.comparison-number');
      const decrease = root.querySelector('.comparison-decrease');
      const increase = root.querySelector('.comparison-increase');
      const reset = root.querySelector('.comparison-reset');
      const controls = root.querySelector('.comparison-controls');
      if (!input || !number || !decrease || !increase || !reset || !controls) return;
      const a = Number(input.dataset.a), initial = Number(input.defaultValue);
      const maximum = Number(input.max), unit = input.dataset.unit;
      if (![a, initial, maximum].every(Number.isSafeInteger) || maximum < 1 ||
          maximum > 10000 || a < 0 || a > maximum || initial < 0 || initial > maximum) return;
      function update() {
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
        root.querySelector('.comparison-result').textContent =
          'B − A = ' + delta + ' ' + unit + '. ' +
          (delta === 0 ? 'Equal quantities.' : 'B is ' + Math.abs(delta) + ' ' + unit +
          (delta > 0 ? ' higher.' : ' lower.')) +
          (b === initial ? ' Authored starting value.' : ' Hypothetical value.');
      }
      input.value = String(initial);
      input.oninput = update;
      number.oninput = () => number.setCustomValidity('');
      number.onchange = () => {
        const b = Number(number.value);
        if (!number.value || !Number.isSafeInteger(b) || b < 0 || b > maximum) {
          number.setCustomValidity('Enter a whole number from 0 to ' + maximum + '.');
          number.reportValidity();
          return;
        }
        input.value = String(b);
        update();
      };
      decrease.onclick = () => { input.value = String(Math.max(0, Number(input.value) - 1)); update(); };
      increase.onclick = () => { input.value = String(Math.min(maximum, Number(input.value) + 1)); update(); };
      reset.onclick = () => { input.value = String(initial); update(); };
      update();
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
        '<div class="comparison-bars">'
        '<label>A: %d %s <meter min="0" max="%d" value="%d"></meter></label>'
        '<label>B: <span class="comparison-b">%d</span> %s '
        '<meter class="comparison-meter-b" min="0" max="%d" value="%d"></meter></label>'
        '</div><p class="comparison-result" role="status" aria-live="polite"></p>'
        '</div></div>'
        % (inline(data["text"]), a, unit, b, unit, b-a, unit,
           unit, maximum, maximum, b, a, unit, unit, maximum, b, a, unit, maximum, a,
           b, unit, maximum, b))


LINEPLOT_CSS = """
.lesson-lineplot {overflow-wrap:anywhere}
.lineplot-static {margin-block:.75rem}
.lineplot-controls {margin-block:1rem;font-family:var(--font-chrome)}
.lineplot-controls fieldset {margin-block:.75rem;border:1px solid var(--line);padding:1rem}
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


LINEPLOT_JS = """<script>
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
      function update() {
        const current = Number(value.value);
        if (!Number.isSafeInteger(current) || current < -2 || current > 2) return;
        equation.textContent = 'y = ' + m + 'x ' + (current < 0 ? '- ' + Math.abs(current) : '+ ' + current);
        [-2,0,2].forEach((x, i) => { points[i].textContent = String(m*x + current); });
        line.setAttribute('points', [-2,0,2].map(x => coordinate(x,m*x+current)).join(' '));
        live.textContent = 'Intercept ' + current + '. At x = -2, 0, 2, y = ' +
          [-2,0,2].map(x => m*x+current).join(', ') + '. Slope remains ' + m + '.';
      }
      value.value = String(changed);
      commit.onclick = () => {
        if (!selection.value) {
          choice.textContent = 'Choose a prediction before revealing the change.';
          selection.focus();
          return;
        }
        choice.textContent = 'Your prediction: ' + selection.options[selection.selectedIndex].text + '.';
        manipulate.hidden = false;
        staticView.hidden = false;
        update();
        value.focus();
      };
      value.onchange = update;
      reset.onclick = () => { value.value = String(changed); update(); value.focus(); };
      root.dataset.initialized = '1';
      root.classList.add('lineplot-enhanced');
      staticView.hidden = true;
      controls.hidden = false;
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
        '<label for="lineplot-prediction-%s">Which plotted points change when only the intercept changes?</label>'
        '<select class="lineplot-prediction" id="lineplot-prediction-%s">'
        '<option value="">Choose a prediction</option>'
        '<option value="all">All three points</option><option value="origin">Only the point at x = 0</option>'
        '<option value="none">No points</option></select>'
        '<button class="lineplot-commit" type="button">Commit prediction</button></fieldset>'
        '<p class="lineplot-choice"></p>'
        '<div class="lineplot-manipulate" hidden>'
        '<label>Intercept (whole number from -2 to 2)'
        '<select class="lineplot-value">%s</select></label>'
        '<button class="lineplot-reset" type="button">Reset to authored change</button>'
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
           '%d-%d-%d' % (m+2,b+2,changed+2),
           '%d-%d-%d' % (m+2,b+2,changed+2),
           ''.join('<option value="%d">%d</option>' % (n,n) for n in range(-2,3))))
