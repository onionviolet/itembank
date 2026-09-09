"""Trusted, deterministic enhancement for an explicitly authored Example.

No authored code, persistence, requests, scoring or accepted-content writes.
The model owns parsing. This module receives validated scalar data only.
"""
import html


CSS = """
.lesson-comparison {overflow-wrap:anywhere}
.lesson-comparison strong {color:#18251b;background:#fff08a;font-weight:700;padding:0 .12em}
.comparison-static {white-space:pre-line}
.comparison-controls {margin-block:1rem}
.comparison-controls label {display:block}
.comparison-controls input {width:100%;min-height:44px}
.comparison-controls button {min-height:44px;margin-block:.5rem}
.comparison-bars {display:grid;gap:.5rem;margin-block:1rem}
.comparison-bars meter {width:100%;height:1.5rem}
.comparison-result {font-weight:700}
@media print {.comparison-controls {display:none!important}}
@media (forced-colors:active) {.lesson-comparison strong {color:CanvasText;background:Canvas;text-decoration:underline}}
"""


JS = """<script>
(() => {
  function initialize() {
    document.querySelectorAll('.lesson-comparison').forEach(root => {
      const input = root.querySelector('input');
      const controls = root.querySelector('.comparison-controls');
      if (!input || !controls) return;
      const a = Number(input.dataset.a), initial = Number(input.defaultValue);
      const maximum = Number(input.max), unit = input.dataset.unit;
      if (![a, initial, maximum].every(Number.isSafeInteger) || maximum < 1 ||
          maximum > 10000 || a < 0 || a > maximum || initial < 0 || initial > maximum) return;
      function update() {
        let b = Number(input.value);
        if (!Number.isSafeInteger(b) || b < 0 || b > maximum) b = initial;
        input.value = String(b);
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
      root.querySelector('button').onclick = () => { input.value = String(initial); update(); };
      update();
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
        '<button type="button">Reset comparison</button>'
        '<div class="comparison-bars">'
        '<label>A: %d %s <meter min="0" max="%d" value="%d"></meter></label>'
        '<label>B: <span class="comparison-b">%d</span> %s '
        '<meter class="comparison-meter-b" min="0" max="%d" value="%d"></meter></label>'
        '</div><p class="comparison-result" role="status" aria-live="polite"></p>'
        '</div></div>'
        % (inline(data["text"]), a, unit, b, unit, b-a, unit,
           unit, maximum, maximum, b, a, unit, a, unit, maximum, a,
           b, unit, maximum, b))
