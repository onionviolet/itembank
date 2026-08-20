"""The 17A same-flow three-direction tracer (VISUAL-01, VISUAL-02).

One synthetic lesson-plus-practice flow, rendered three times. The body markup
is byte-identical across all three directions on purpose: the direction is a
token and stylesheet overlay and nothing else. If a direction ever needed its
own markup it would stop being a direction and start being a second product,
which is exactly what VISUAL-01 forbids and what the parity test catches.

Direction CSS lives in `prototypes/17a/<direction>.css`, one deletable file
each, so any direction can be removed after the comparison without touching the
other two or any shipped surface (D-04 reversibility).

This module renders a fixture. It holds no key, scores nothing, and reaches no
session state. It is development-only and its route stays behind an explicit
opt in.
"""
import json
import os
import re

from surfaces import presentation, theme

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTOTYPE_DIR = os.path.join(ROOT, "prototypes", "17a")
FIXTURE_PATH = os.path.join(ROOT, "fixtures", "visual_system_flow.json")

DIRECTIONS = ("structured-studio", "quiet-workbench", "guided-canvas")
DEFAULT_DIRECTION = "structured-studio"

# VISUAL-02: configurable tokens with a safe range. Anything outside the range
# clamps rather than passing through, because a token that does not clamp is a
# fixed rule wearing a token's clothes.
DENSITY_VALUES = ("comfortable", "compact")
MEASURE_MIN_CH, MEASURE_MAX_CH = 48, 90
LEADING_MIN, LEADING_MAX = 1.3, 1.9
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

# VISUAL-02 fixed rules: never configurable, always emitted, regardless of what
# a caller puts in the token dict.
FIXED_RULES = """
:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
[data-state] { border-left: 4px solid var(--line); }
.vf-locked { border-left: 4px solid var(--unknown); }
"""


def load_fixture(path=FIXTURE_PATH):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def clamp_tokens(tokens):
    """Return a safe token dict. Every out-of-range value falls back to its
    default and the caller is never told it succeeded, because a silently
    honored abusive token is the failure this function exists to prevent."""
    tokens = tokens or {}
    density = tokens.get("density")
    if density not in DENSITY_VALUES:
        density = "comfortable"

    measure = tokens.get("measure")
    ch = None
    if isinstance(measure, str):
        match = re.match(r"^(\d+)ch$", measure.strip())
        if match:
            ch = int(match.group(1))
    elif isinstance(measure, int):
        ch = measure
    if ch is None or ch < MEASURE_MIN_CH or ch > MEASURE_MAX_CH:
        ch = 68

    leading = tokens.get("leading")
    try:
        leading = float(leading)
    except (TypeError, ValueError):
        leading = 1.6
    if leading < LEADING_MIN or leading > LEADING_MAX:
        leading = 1.6

    accent = tokens.get("accent")
    if not (isinstance(accent, str) and HEX_RE.match(accent.strip())):
        accent = theme.DEFAULT_ACCENT

    return {"density": density, "measure": "%dch" % ch,
            "leading": "%.2f" % leading, "accent": accent}


def direction_css(direction):
    """The one deletable stylesheet for a direction. A missing file degrades to
    an empty overlay rather than raising, so deleting a direction after the
    comparison leaves the other two working."""
    if direction not in DIRECTIONS:
        direction = DEFAULT_DIRECTION
    path = os.path.join(PROTOTYPE_DIR, direction + ".css")
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _esc(value):
    return presentation.esc("" if value is None else str(value))


def _fill_blocks(filled, total=5):
    """Five discrete blocks, never a continuous bar and never a percentage
    (D-06 ruling 10). The legend text always sits beside them."""
    marks = []
    for index in range(total):
        state = "on" if index < filled else "off"
        marks.append('<span class="vf-fill vf-fill-%s" aria-hidden="true"></span>' % state)
    return "".join(marks)


def _shelf(stage):
    cards = []
    for card in stage.get("cards", []):
        if card.get("state") == "locked":
            cards.append(
                '<li class="vf-card vf-locked"><h3>%s</h3>'
                '<p class="vf-status">Locked</p><p>%s</p></li>'
                % (_esc(card.get("course")), _esc(card.get("unlock"))))
        else:
            cards.append(
                '<li class="vf-card"><h3>%s</h3><p class="vf-status">%s</p></li>'
                % (_esc(card.get("course")), _esc(card.get("resume"))))
    return '<ul class="vf-shelf">%s</ul>' % "".join(cards)


def _objective(stage):
    source = stage.get("source") or {}
    prereqs = "".join("<li>%s</li>" % _esc(p) for p in stage.get("prerequisites", []))
    return (
        '<p class="vf-source">Source: <cite>%s</cite></p>'
        '<h3>Prerequisites</h3><ul>%s</ul>'
        '<p class="vf-standing">%s <span class="vf-legend">%s</span></p>'
        % (_esc(source.get("label")), prereqs,
           _fill_blocks(stage.get("fill_state", 0)),
           _esc(stage.get("fill_legend"))))


def _lesson(stage):
    parts = []
    for block in stage.get("blocks", []):
        form = block.get("form")
        if form == "definition":
            parts.append('<dl class="vf-def"><dt>%s</dt><dd>%s</dd></dl>'
                         % (_esc(block.get("term")), _esc(block.get("body"))))
        elif form == "warning":
            parts.append('<aside class="vf-warn" data-state="warn">'
                         '<p><strong>Watch for this.</strong> %s</p></aside>'
                         % _esc(block.get("body")))
        elif form == "table":
            head = "".join("<th scope=\"col\">%s</th>" % _esc(h)
                           for h in block.get("head", []))
            rows = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % _esc(c) for c in row)
                           for row in block.get("rows", []))
            parts.append('<figure class="vf-table-wrap"><figcaption>%s</figcaption>'
                         '<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>'
                         "</figure>" % (_esc(block.get("caption")), head, rows))
        elif form == "cited_image":
            parts.append('<figure class="vf-figure"><div class="vf-image-slot" '
                         'role="img" aria-label="%s"></div>'
                         "<figcaption>%s</figcaption></figure>"
                         % (_esc(block.get("alt")), _esc(block.get("credit"))))
        elif form == "inline_prediction":
            parts.append('<aside class="vf-predict"><p>%s</p></aside>'
                         % _esc(block.get("prompt")))
        elif form == "inline_check":
            options = "".join("<li>%s</li>" % _esc(o) for o in block.get("options", []))
            parts.append('<section class="vf-check"><h3>Check yourself</h3>'
                         "<p>%s</p><ul>%s</ul>"
                         '<p class="vf-status">The answer is released by the runtime '
                         "after you respond. It is not in this page.</p></section>"
                         % (_esc(block.get("prompt")), options))
    return "".join(parts)


def _practice(stage):
    tiers = []
    for tier in stage.get("hint_tiers", []):
        if tier.get("released"):
            tiers.append(presentation.details_section(
                "Hint %d" % tier.get("tier", 0),
                "<p>%s</p>" % _esc(tier.get("text"))))
        else:
            tiers.append('<p class="vf-locked vf-status">Hint %d is locked. '
                         "The runtime releases it, not this page.</p>"
                         % tier.get("tier", 0))
    return (
        '<p class="vf-answer">Your answer: <span data-state="bad">%s</span></p>'
        '<div class="vf-feedback" data-state="bad"><p>%s</p></div>'
        "%s<p><button type=\"button\">Try again</button></p>"
        % (_esc(stage.get("learner_choice")), _esc(stage.get("entitled_feedback")),
           "".join(tiers)))


def _evidence(stage):
    rows = []
    for row in stage.get("rows", []):
        result = row.get("result")
        note = row.get("pending_reason") or ""
        rows.append('<tr><td>%s</td><td data-state="%s">%s</td><td>%s</td>'
                    "<td>%s</td></tr>"
                    % (_esc(row.get("item")), _esc(result), _esc(result),
                       _esc(row.get("recorded")), _esc(note)))
    return ('<p class="vf-denominator">%s</p>'
            '<figure class="vf-table-wrap"><table><thead><tr>'
            '<th scope="col">Item</th><th scope="col">Result</th>'
            '<th scope="col">Recorded</th><th scope="col">Note</th>'
            "</tr></thead><tbody>%s</tbody></table></figure>"
            % (_esc(stage.get("denominator_note")), "".join(rows)))


def _proposal(stage):
    cites = "".join("<li><cite>%s</cite></li>" % _esc(c)
                    for c in stage.get("citations", []))
    lines = []
    for line in stage.get("diff", []):
        mark = "+" if line.get("op") == "add" else " "
        lines.append('<li class="vf-diff-%s"><code>%s %s</code></li>'
                     % (_esc(line.get("op")), mark, _esc(line.get("text"))))
    return ('<p class="vf-status" data-state="pending">Proposed, not accepted. '
            "Nothing changes until you accept it.</p>"
            "<p>%s</p><h3>Cited from</h3><ul>%s</ul>"
            '<h3>Proposed change</h3><ul class="vf-diff">%s</ul>'
            '<p><button type="button">Accept</button> '
            '<button type="button">Reject</button></p>'
            % (_esc(stage.get("rationale")), cites, "".join(lines)))


def _status(stage):
    panels = []
    for key in ("agent", "offline"):
        block = stage.get(key) or {}
        panels.append(presentation.state_panel(
            {"kind": "unknown", "status": block.get("copy", "")}))
    return "".join(panels)


RENDERERS = {"shelf": _shelf, "objective": _objective, "lesson": _lesson,
             "practice": _practice, "evidence": _evidence,
             "proposal": _proposal, "status": _status}


def render_body(data):
    """The semantic body, identical for every direction.

    An empty or unrecognized flow renders an explicit unavailable state rather
    than an empty page or an invented number, because a prototype that quietly
    shows nothing reads as a working prototype with no content.
    """
    stages = data.get("stages") or []
    if not stages:
        return presentation.state_panel({
            "kind": "unknown",
            "status": "Flow data is unavailable. This prototype renders synthetic "
                      "fixture content only, and none was supplied."})
    sections = []
    for index, stage in enumerate(stages, start=1):
        renderer = RENDERERS.get(stage.get("kind"))
        if renderer is None:
            inner = presentation.state_panel({
                "kind": "unknown",
                "status": "This stage kind is unavailable in the fixture renderer."})
        else:
            inner = renderer(stage)
        sections.append(
            '<section class="vf-stage" data-stage="%s">'
            '<h2><span class="vf-step">Step %d</span> %s</h2>%s</section>'
            % (_esc(stage.get("id")), index, _esc(stage.get("title")), inner))
    return "".join(sections)


def token_css(tokens):
    safe = clamp_tokens(tokens)
    return (":root{--vf-density:%s;--vf-measure:%s;--vf-leading:%s;"
            "--vf-text-xs:0.82rem;--accent:%s;}"
            % (safe["density"], safe["measure"], safe["leading"], safe["accent"]))


def page(data, direction=DEFAULT_DIRECTION, tokens=None):
    """One rendered direction. The body never varies; the style block does."""
    if direction not in DIRECTIONS:
        direction = DEFAULT_DIRECTION
    base = theme.theme_css(theme.DEFAULT_THEME_CONFIG)
    css = "\n".join([base, token_css(tokens), FIXED_RULES, direction_css(direction)])
    return presentation.surface_shell(
        "Visual direction: %s (synthetic)" % direction,
        render_body(data),
        theme_css=css,
        context=["Synthetic fixture", "Development only", "Direction: %s" % direction],
        noscript="This prototype needs no JavaScript. Everything above is static.")


def write_static(out_dir, data=None):
    """Write the three directions as standalone files, for looking at them side
    by side without running a server."""
    data = data if data is not None else load_fixture()
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for direction in DIRECTIONS:
        path = os.path.join(out_dir, direction + ".html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(page(data, direction))
        written.append(path)
    return written
