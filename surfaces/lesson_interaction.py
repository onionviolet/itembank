"""Trusted, deterministic enhancement for an explicitly authored Example.

No authored code, requests, scoring or accepted-content writes. Exploration
uses bounded tab-local presentation storage only with admitted identity.
The model owns parsing. This module receives validated scalar data only.
"""
import resources
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
EXPLORATION_JS = resources.read_text("surfaces/assets/lesson_interaction/exploration.js")


CSS = resources.read_text("surfaces/assets/lesson_interaction/interaction.css")


JS = "<script>" + EXPLORATION_JS + resources.read_text("surfaces/assets/lesson_interaction/interaction.js")


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


LINEPLOT_CSS = resources.read_text("surfaces/assets/lesson_interaction/lineplot.css")


LINEPLOT_JS = "<script>" + EXPLORATION_JS + resources.read_text("surfaces/assets/lesson_interaction/lineplot.js")


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
