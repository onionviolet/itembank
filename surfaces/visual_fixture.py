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
import io
import json
import os
import re

from surfaces import lesson, presentation, theme

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTOTYPE_DIR = os.path.join(ROOT, "prototypes", "17a")
FIXTURE_PATH = os.path.join(ROOT, "fixtures", "visual_system_flow.json")

DIRECTIONS = ("structured-studio", "quiet-workbench", "guided-canvas")

# The navigation SHAPE is a second, independent axis from the visual
# direction. Nobody has ever chosen between a sidebar, a tab row and a
# bottom bar for this app: 16B-UI-SPEC settles which areas exist and what
# their routes are, and is silent on what the navigation looks like. All
# three shapes render the same markup and differ only in CSS, so choosing
# one later is a stylesheet decision and not a rewrite.
ACCENTS = (
    ("teal", "#0e6e62"),
    ("indigo", "#4a4ad4"),
    ("plum", "#8a3ffc"),
    ("clay", "#b4531f"),
)
DEFAULT_ACCENT_ID = "teal"

NAV_SHAPES = ("sidebar", "tabs", "bottom")
DEFAULT_NAV = "sidebar"
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


# Structure shared by all three directions: the type scale, the prototype
# toolbar, and the pager. A direction overlay changes layout, weight and
# rhythm on top of this; it never re-declares the scale, or the three
# directions would be comparing typography instead of layout.
CHROME_CSS = """
.vf-harness-run { border: 1px solid var(--line); border-radius: var(--r-3);
     padding: var(--space-4); background: var(--card); margin-bottom: var(--space-5); }
.vf-harness-run[data-state="waiting"] { border-color: var(--warn);
     background: var(--warn-bg); }
.vf-harness-run h3 { margin-top: var(--space-1); }
.vf-approval { border: 1px solid var(--accent); border-radius: var(--r-3);
     padding: var(--space-4); margin-bottom: var(--space-4); background: var(--card); }
.vf-approval h4 { margin: 0 0 var(--space-1); font-size: var(--vf-h3); }
.vf-skills { list-style: none; padding: 0; display: flex; flex-wrap: wrap;
     gap: var(--space-2); }
.vf-backends { list-style: none; padding: 0; }
.vf-backends li { padding: var(--space-2) var(--space-3); border-radius: var(--r-2);
     border: 1px solid var(--line); margin-bottom: var(--space-2); }
.vf-backends li[data-state="ok"] { border-color: var(--ok); background: var(--ok-bg); }
.vf-spend { font-family: var(--font-code); font-size: var(--vf-h3); margin-bottom: 0; }
.vf-nav-course-name { margin: var(--space-5) 0 0; font-weight: 600;
     font-size: var(--vf-meta); color: var(--ink); }
.surface { padding-block: var(--space-5) var(--space-7); }
h1 { font-size: var(--vf-h1); line-height: 1.15; letter-spacing: -0.02em;
     margin: 0 0 var(--space-2); }
.vf-stage h2 { font-size: var(--vf-h2); line-height: 1.2;
     letter-spacing: -0.015em; margin: 0 0 var(--space-4); }
.vf-stage h3 { font-size: var(--vf-h3); line-height: 1.3; margin:
     var(--space-5) 0 var(--space-2); color: var(--ink); }
.vf-stage p, .vf-stage li, .vf-stage td { font-size: var(--vf-body);
     line-height: var(--vf-leading); }
.vf-status, .vf-legend, .vf-progress, .vf-chrome-label, .vf-denominator,
.vf-source, figcaption { font-size: var(--vf-meta); color: var(--mut);
     font-family: var(--font-ledger); }

/* Prototype toolbar. Deliberately reads as scaffolding, not as product. */
.vf-chrome { display: flex; flex-wrap: wrap; align-items: center;
     gap: var(--space-2) var(--space-3); padding: var(--space-2) var(--space-3);
     margin-bottom: var(--space-6); border: 1px dashed var(--line);
     border-radius: var(--r-2); background: var(--chip); }
.vf-chrome-label { margin: 0; text-transform: uppercase;
     letter-spacing: .09em; font-size: var(--vf-micro); }
.vf-dirs, .vf-steps { display: flex; flex-wrap: wrap; gap: var(--space-1);
     list-style: none; margin: 0; padding: 0; }
.vf-steps { counter-reset: vfs; }
.vf-dirs a, .vf-steps a { display: inline-block; padding: 2px var(--space-2);
     border-radius: var(--r-1); text-decoration: none; color: var(--mut);
     font-size: var(--vf-micro); border: 1px solid transparent; }
.vf-dirs a:hover, .vf-steps a:hover { color: var(--ink); background: var(--card); }
.vf-dirs a[aria-current], .vf-steps a[aria-current] { color: var(--ink);
     background: var(--card); border-color: var(--line); font-weight: 600; }

/* Pager: the flow control the product would actually have. */
.vf-pager { display: flex; flex-wrap: wrap; align-items: center;
     gap: var(--space-3); margin-top: var(--space-7);
     padding-top: var(--space-4); border-top: 1px solid var(--line); }
.vf-progress { margin: 0; margin-inline-end: auto; }
/* A control must never shatter mid-word. SHARED_CSS grants p
   overflow-wrap:anywhere so a long path in prose can wrap, and that inherits
   into any control sitting inside a paragraph, which is how a one-word button
   ends up stacking one letter per line in a narrow column. Controls opt out. */
.vf-next, .vf-prev, .of-bar label, .vf-appnav a, .vf-appnav label,
.vf-appnav .vf-area-entry, button { overflow-wrap: normal; word-break: keep-all;
     hyphens: none; }
.vf-prev, .vf-next { display: inline-block; text-decoration: none;
     font-size: var(--vf-body); padding: var(--space-2) var(--space-4);
     border-radius: var(--r-2); border: 1px solid var(--line);
     color: var(--ink); text-align: center; }
.vf-next { background: var(--accent); color: var(--card); border-color: var(--accent); }
.vf-prev:hover { background: var(--chip); }
.vf-next:hover { filter: brightness(1.08); }

/* Content forms. */
.vf-def { margin: var(--space-5) 0; padding-inline-start: var(--space-4);
     border-inline-start: 3px solid var(--accent); }
.vf-def dt { font-weight: 650; font-size: var(--vf-h3); margin-bottom: var(--space-1); }
.vf-def dd { margin: 0; }
.vf-warn { margin: var(--space-5) 0; padding: var(--space-3) var(--space-4);
     border-radius: var(--r-2); background: var(--warn-bg);
     border-inline-start: 4px solid var(--warn); }
.vf-warn p { margin: 0; }
.vf-predict { margin: var(--space-5) 0; padding: var(--space-3) var(--space-4);
     border-radius: var(--r-2); background: var(--chip); }
.vf-predict p { margin: 0; font-style: italic; }
.vf-check { margin: var(--space-6) 0; padding: var(--space-4);
     border-radius: var(--r-2); border: 1px solid var(--line); background: var(--card); }
.vf-check ul { list-style: none; padding: 0; margin: var(--space-3) 0; }
.vf-check li { padding: var(--space-2) var(--space-3); margin-bottom: var(--space-2);
     border: 1px solid var(--line); border-radius: var(--r-1); background: var(--bg); }
.vf-table-wrap { margin: var(--space-5) 0; overflow-x: auto; }
.vf-table-wrap table { border-collapse: collapse; width: 100%; }
.vf-table-wrap th, .vf-table-wrap td { text-align: start;
     padding: var(--space-2) var(--space-3); border-bottom: 1px solid var(--line); }
.vf-table-wrap th { font-size: var(--vf-meta); text-transform: uppercase;
     letter-spacing: .07em; color: var(--mut); font-family: var(--font-ledger); }
.vf-image-slot { aspect-ratio: 16 / 7; border-radius: var(--r-2);
     border: 1px dashed var(--line); background: var(--chip); }
.vf-figure { margin: var(--space-5) 0; }
.vf-fill { display: inline-block; width: 14px; height: 14px;
     border-radius: var(--r-1); border: 1px solid var(--edge); margin-inline-end: 3px; }
.vf-fill-on { background: var(--accent); border-color: var(--accent); }
.vf-fill-off { background: transparent; }
.vf-shelf { list-style: none; padding: 0; margin: 0; }
.vf-card h3 { margin: 0 0 var(--space-1); font-size: var(--vf-h3); }
.vf-card p { margin: 0; }
.vf-diff { list-style: none; padding: 0; }
.vf-diff li { padding: var(--space-1) var(--space-3); border-radius: var(--r-1);
     font-family: var(--font-code); font-size: var(--vf-meta); }
.vf-diff-add { background: var(--ok-bg); border-inline-start: 3px solid var(--ok); }
.vf-diff-context { color: var(--mut); }
.vf-feedback { margin: var(--space-4) 0; padding: var(--space-3) var(--space-4);
     border-radius: var(--r-2); background: var(--bad-bg); }
.vf-feedback p { margin: 0; }
.vf-answer { margin: 0 0 var(--space-3); }
button[type="button"]:not(.term) { display: inline-block; font: inherit;
     font-size: var(--vf-body);
     padding: var(--space-2) var(--space-4); border-radius: var(--r-2);
     border: 1px solid var(--line); background: var(--card); color: var(--ink);
     cursor: pointer; }
button[type="button"]:not(.term):hover { background: var(--chip); }
@media (max-width: 767px) {
  .vf-pager { flex-direction: column; align-items: stretch; }
  .vf-prev, .vf-next { text-align: center; }
}
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


def overlay_css(name):
    """One deletable overlay stylesheet by file stem. Missing files degrade to
    an empty overlay so any single overlay can be removed."""
    path = os.path.join(PROTOTYPE_DIR, name + ".css")
    if not os.path.exists(path):
        return ""
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


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


TERM_RE = re.compile(r"\[\[([^\]]+)\]\]")


def gloss_map(data):
    """Slug -> record, in authored order, in the shape lesson.py already uses."""
    out = {}
    for entry in data.get("terms", []):
        out[entry["slug"]] = {"canonical": entry["canonical"], "def": entry["def"]}
    return out


def mark_terms(text, seen=None):
    """Replace every [[term]] with the shipped popover trigger.

    The trigger, the panel and the appendix all come from surfaces/lesson.py.
    Building a second glossary here would put two hover definitions in the
    product, which is the same mistake as a second scorer.
    """
    def swap(match):
        raw = match.group(1)
        slug = raw.lower().replace(" ", "-")
        if seen is not None:
            seen.add(slug)
        return lesson._gloss_trigger_html(raw, slug)
    return TERM_RE.sub(swap, text)


def _fill_blocks(filled, total=5):
    """Five discrete blocks, never a continuous bar and never a percentage
    (D-06 ruling 10). The legend text always sits beside them."""
    marks = []
    for index in range(total):
        state = "on" if index < filled else "off"
        marks.append('<span class="vf-fill vf-fill-%s" aria-hidden="true"></span>' % state)
    return "".join(marks)



def _home(stage):
    nxt = stage.get("next_action") or {}
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
    jobs = "".join(
        '<li data-state="%s"><span class="vf-status">%s</span> %s</li>'
        % (_esc(job.get("state")),
           "Needs you" if job.get("state") == "needs_input" else "Done",
           _esc(job.get("text")))
        for job in stage.get("activity", []))
    resume = ""
    if nxt:
        resume = ('<section class="vf-resume">'
                  '<p class="vf-status">Pick up where you stopped</p>'
                  "<h3>%s</h3>"
                  '<p class="vf-resume-target">%s</p>'
                  '<p class="vf-resume-why">%s</p>'
                  '<p><a class="vf-next" href="?direction=DIR&amp;nav=NAV&amp;'
                  'stage=%s">%s</a></p></section>'
                  % (_esc(nxt.get("course")), _esc(nxt.get("objective")),
                     _esc(nxt.get("why")), _esc(nxt.get("stage")),
                     _esc(nxt.get("label"))))
    return ('%s<h3>All courses</h3><ul class="vf-shelf">%s</ul>'
            '<h3>Activity</h3><ul class="vf-jobs">%s</ul>' % (resume, "".join(cards), jobs))




# --------------------------------------------------------------------------
# Live wiring. The harness reads the shipped journal and the shipped settings
# rather than a fixture, and says per panel which it got. A prototype that
# shows invented data indistinguishable from real data is worse than one that
# shows nothing: you cannot tell what you are looking at, so you cannot tell
# whether it works.
# --------------------------------------------------------------------------

# journal.RECORD_TYPES in learner-facing words. An operation with no phrase
# here still renders, under its raw name, rather than being dropped.
OPERATION_PHRASE = {
    "mint": "created",
    "link": "linked",
    "import": "imported",
    "copy": "copied",
    "move": "moved",
    "edit_in_place": "edited",
    "supersede": "superseded",
    "reconcile": "reconciled",
    "restore": "restored",
    "external_edit": "changed outside the app",
}

# A write can be reversed from its journalled prior revision; a read cannot,
# and an external edit was never ours to reverse.
UNDOABLE = {"mint", "link", "import", "copy", "move", "edit_in_place",
            "supersede", "reconcile", "restore"}


def live_journal(base):
    """(rows, note). Empty rows with a note is the normal state on a machine
    that has not run an operation yet, never an error."""
    try:
        import journal
    except ImportError:
        return [], "The operation journal is not available in this build."
    try:
        raw = list(journal.entries(base))
    except OSError as exc:
        return [], "The operation journal could not be read: %s" % exc.__class__.__name__
    rows = []
    for entry in raw[-12:]:
        operation = entry.get("operation", "")
        rows.append({
            "op": operation,
            "text": "%s %s" % (OPERATION_PHRASE.get(operation, operation),
                               entry.get("rel_path") or entry.get("object_id") or ""),
            "when": entry.get("recorded_at") or entry.get("at") or "",
            "undo": operation in UNDOABLE,
        })
    rows.reverse()
    if not rows:
        return [], ("No operations recorded yet. Every write this app makes "
                    "lands here with a way back.")
    return rows, ""


def live_backends(base):
    """(rows, note). Egress is derived from the profile's transport, never
    authored per profile, so a new backend cannot quietly claim to be local."""
    try:
        from surfaces import settings as settings_mod
    except ImportError:
        return [], "Settings are not available in this build."
    try:
        data = settings_mod.load_settings(base)
    except (OSError, ValueError) as exc:
        return [], "Settings could not be read: %s" % exc.__class__.__name__
    mb = (data or {}).get("model_backend") or {}
    profiles = mb.get("profiles") or []
    active = mb.get("active") or ""
    rows = []
    for profile in profiles:
        if not isinstance(profile, dict):
            continue
        transport = (profile.get("transport") or "").lower()
        local = transport in ("local", "openai_compatible_local", "llama_cpp", "ollama")
        rows.append({
            "id": profile.get("name", ""),
            "label": profile.get("name", ""),
            "where": "local" if local else "hosted",
            "active": profile.get("name") == active,
            "egress": ("Nothing leaves this machine." if local else
                       "Item text and lesson prose leave this machine."),
        })
    if not rows:
        return [], ("No model backend is configured, so nothing can run here "
                    "yet. Studying, scoring and authored hints are unaffected.")
    if not active:
        return rows, "No backend is active. Choose one before starting a skill."
    return rows, ""


def live_autonomy(base):
    try:
        from surfaces import settings as settings_mod
        data = settings_mod.load_settings(base)
    except (ImportError, OSError, ValueError):
        return None
    return (data or {}).get("auditor_autonomy") or None


def harness_state(stage, base=None):
    """Merge the fixture stage with whatever is really on disk.

    Each panel carries its own `live` flag. They are independent on purpose:
    a machine can have a configured backend and an empty journal, and saying
    so is more useful than picking one word for the whole screen.
    """
    merged = dict(stage or {})
    if base is None:
        merged["journal_live"] = False
        merged["backends_live"] = False
        return merged

    rows, note = live_journal(base)
    merged["journal_live"] = True
    merged["journal_note"] = note
    merged["journal"] = rows

    rows, note = live_backends(base)
    merged["backends_live"] = True
    merged["backends_note"] = note
    # An empty live read means no backend is configured. Falling back to the
    # fixture list here would show three model names this machine cannot
    # reach, under a heading claiming the panel was read from disk.
    merged["backends"] = rows

    current = live_autonomy(base)
    if current:
        autonomy = dict(merged.get("autonomy") or {})
        autonomy["current"] = current
        merged["autonomy"] = autonomy

    # Nothing on disk can tell us what a model is doing right now, because
    # nothing is running one yet. Say so rather than showing a stale job.
    merged["running"] = None
    merged["pending"] = []
    merged["budget"] = None
    return merged


def _harness(stage):
    """The agent console. Every control here maps to something that already
    shipped: model_backend.active (Phase 8), auditor_autonomy (Phase 11), the
    skills in .claude/skills, and journal.commit_operation (Phase 14A). The
    harness is a surface over that machinery, never a second authority: it
    proposes, and the runtime accepts."""
    def source_note(live, note):
        if not live:
            return ('<p class="vf-status" data-state="unknown">Synthetic sample. '
                    "Nothing on this machine was read for this panel.</p>")
        if note:
            return '<p class="vf-status" data-state="unknown">%s</p>' % _esc(note)
        return '<p class="vf-status" data-state="ok">Read from this machine.</p>'

    backends = "".join(
        '<li%s><span class="vf-area-label">%s</span>'
        '<span class="vf-status">%s. %s</span></li>'
        % (' data-state="ok"' if b.get("active") else "",
           _esc(b.get("label")), _esc(b.get("where")), _esc(b.get("egress")))
        for b in stage.get("backends", []))
    autonomy = stage.get("autonomy") or {}
    levels = "".join(
        '<li%s><span class="vf-area-label">%s</span>'
        '<span class="vf-status">%s</span></li>'
        % (' data-state="ok"' if lv["id"] == autonomy.get("current") else "",
           _esc(lv["label"]), _esc(lv["what"]))
        for lv in autonomy.get("levels", []))
    skills = "".join('<li><button type="button">%s</button></li>' % _esc(sk["label"])
                     for sk in stage.get("skills", []))
    budget = stage.get("budget") or {}
    running = stage.get("running") or {}
    pending = []
    for job in stage.get("pending", []):
        lines = "".join('<li class="vf-diff-%s"><code>%s %s</code></li>'
                        % (_esc(d.get("op")), "+" if d.get("op") == "add" else " ",
                           _esc(d.get("text")))
                        for d in job.get("diff", []))
        pending.append(
            '<article class="vf-approval"><h4>%s</h4>'
            '<p class="vf-status">Cited from %s</p>'
            '<ul class="vf-diff">%s</ul>'
            '<p class="vf-status" data-state="ok">%s</p>'
            '<p><button type="button">Accept</button> '
            '<button type="button">Reject</button> '
            '<button type="button">Open full diff</button></p></article>'
            % (_esc(job.get("title")), _esc(job.get("cited")), lines,
               _esc(job.get("validated"))))
    log = "".join(
        '<li><span class="vf-status">%s</span> %s%s</li>'
        % (_esc(entry.get("when")), _esc(entry.get("text")),
           ' <button type="button">Undo</button>' if entry.get("undo") else "")
        for entry in stage.get("journal", []))
    if running:
        run_block = ('<section class="vf-harness-run" data-state="%s">'
                     '<p class="vf-status">Running, %s</p><h3>%s</h3>'
                     "<p>%s</p></section>"
                     % (_esc(running.get("state")), _esc(running.get("elapsed")),
                        _esc(running.get("skill")), _esc(running.get("step"))))
    else:
        run_block = presentation.state_panel({
            "kind": "unknown",
            "status": "Nothing is running. Start a skill below."})

    if pending:
        pending_block = "".join(pending)
    else:
        pending_block = presentation.state_panel({
            "kind": "unknown",
            "status": "Nothing is waiting for you."})

    if budget:
        spend_block = ('<p class="vf-spend">%s spent, %s tokens</p>'
                       '<p class="vf-status">%s</p>'
                       % (_esc(budget.get("spent_usd")), _esc(budget.get("tokens")),
                          _esc(budget.get("note"))))
    else:
        spend_block = presentation.state_panel({
            "kind": "unknown",
            "status": "No spend recorded yet. This app does not have your "
                      "provider bill, so it can only count what it sends."})

    if log:
        log_block = '<ul class="vf-jobs">%s</ul>' % log
    else:
        log_block = presentation.state_panel({
            "kind": "unknown",
            "status": stage.get("journal_note")
                      or "No operations recorded yet."})

    return (
        "%s<h3>Waiting for you</h3>%s"
        '<h3>Start something</h3><ul class="vf-skills">%s</ul>'
        "<h3>Model</h3>%s<ul class=\"vf-backends\">%s</ul>"
        '<h3>How much it may do on its own</h3><ul class="vf-backends">%s</ul>'
        "<h3>Spend</h3>%s"
        "<h3>Operation journal</h3>%s%s"
        % (run_block, pending_block, skills,
           source_note(stage.get("backends_live"), stage.get("backends_note")),
           backends, levels, spend_block,
           source_note(stage.get("journal_live"), stage.get("journal_note")),
           log_block))


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
                         % (mark_terms(_esc(block.get("term"))),
                            mark_terms(_esc(block.get("body")))))
        elif form == "warning":
            parts.append('<aside class="vf-warn" data-state="warn">'
                         '<p><strong>Watch for this.</strong> %s</p></aside>'
                         % mark_terms(_esc(block.get("body"))))
        elif form == "table":
            head = "".join("<th scope=\"col\">%s</th>" % _esc(h)
                           for h in block.get("head", []))
            rows = "".join("<tr>%s</tr>"
                           % "".join("<td>%s</td>" % mark_terms(_esc(c)) for c in row)
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
                         % mark_terms(_esc(block.get("prompt"))))
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


RENDERERS = {"home": _home, "harness": _harness, "shelf": _shelf, "objective": _objective, "lesson": _lesson,
             "practice": _practice, "evidence": _evidence,
             "proposal": _proposal, "status": _status}


STAGE_LABELS = {
    "shelf_resume": "Courses",
    "source_linked_objective": "Objective",
    "long_lesson": "Read",
    "wrong_answer_retry": "Practice",
    "evidence_review": "Evidence",
    "ai_proposed_change": "Review change",
    "agent_offline_status": "Status",
    "agent_harness": "Agent",
}


def stage_ids(data):
    return [stage.get("id") for stage in data.get("stages", [])]


def find_stage(data, stage_id):
    for stage in data.get("stages", []):
        if stage.get("id") == stage_id:
            return stage
    return None


def _link(direction, stage_id, label, current="", nav_shape=DEFAULT_NAV):
    return ('<li><a href="?direction=%s&amp;nav=%s&amp;stage=%s"%s>%s</a></li>'
            % (direction, nav_shape, stage_id, current, _esc(label)))




def _course_picker(app, chooser=None):
    """The course selector. The vision is one learner across three subjects at
    once, so the shell has to offer the switch rather than hide it on Home."""
    courses = app.get("courses") or []
    if not courses:
        return ('<p class="vf-nav-course-name">%s</p>'
                % _esc(app.get("course_name", "Course")))
    rows = []
    for course in courses:
        label = ('<span class="vf-area-label">%s</span>'
                 '<span class="vf-area-route">%s</span>'
                 % (_esc(course.get("label")), _esc(course.get("resume"))))
        mark = ' aria-current="true"' if course.get("current") else ""
        if chooser is not None:
            rows.append("<li>%s</li>" % chooser(course, label, mark))
        else:
            rows.append('<li><span class="vf-area-entry"%s>%s</span></li>'
                        % (mark, label))
    return ('<p class="vf-nav-label">Course</p>'
            '<ul class="vf-nav-course vf-courses">%s</ul>' % "".join(rows))


def _app_nav(data, direction, nav_shape, stage_id):
    """The app shell navigation. Identical markup in all three shapes, because
    a shape is a stylesheet and a rewrite is not a shape."""
    app = data.get("app") or {}
    stage_for = {}
    for area in app.get("course_areas", []):
        stage_for[area["id"]] = area.get("stage")
    current = ""
    for area_id, sid in stage_for.items():
        if sid == stage_id:
            current = area_id
    def item(label, target, is_current, route):
        mark = ' aria-current="page"' if is_current else ""
        inner = ('<span class="vf-area-label">%s</span>'
                 '<span class="vf-area-route">%s</span>'
                 % (_esc(label), _esc(route)))
        if not target:
            return ('<li class="vf-area-todo">'
                    '<span class="vf-area-entry">%s</span></li>' % inner)
        return ('<li><a class="vf-area-entry" href="?direction=%s&amp;nav=%s'
                '&amp;stage=%s"%s>%s</a></li>'
                % (direction, nav_shape, target, mark, inner))
    app_items = "".join(
        item(a["label"], "shelf_resume" if a["id"] == "home" else
             ("agent_offline_status" if a["id"] in ("settings", "help") else None),
             stage_id == "shelf_resume" and a["id"] == "home", a["route"])
        for a in app.get("app_areas", []))
    by_id = {a["id"]: a for a in app.get("course_areas", [])}
    by_id.update({a["id"]: a for a in app.get("app_areas", [])
                  if a["id"] not in by_id})
    blocks = []
    for section in app.get("sections", []):
        rows = "".join(
            item(by_id[aid]["label"], by_id[aid].get("stage"),
                 aid == current, by_id[aid]["route"])
            for aid in section.get("areas", []) if aid in by_id)
        if not rows:
            continue
        blocks.append('<p class="vf-nav-label" title="%s">%s</p>'
                      '<ul class="vf-nav-course" data-section="%s">%s</ul>'
                      % (_esc(section.get("hint")), _esc(section.get("label")),
                         _esc(section["id"]), rows))
    if not blocks:
        blocks.append('<ul class="vf-nav-course">%s</ul>' % "".join(
            item(a["label"], a.get("stage"), a["id"] == current, a["route"])
            for a in app.get("course_areas", [])))
    return ('<nav class="vf-appnav" aria-label="Application">'
            '<p class="vf-nav-brand">itembank</p>'
            '<p class="vf-nav-label">App</p><ul class="vf-nav-app">%s</ul>'
            "%s%s</nav>" % (app_items, _course_picker(app), "".join(blocks)))


def _prototype_chrome(data, direction, stage_id, nav_shape=DEFAULT_NAV):
    """Navigation that exists because this is a prototype, not because the
    product has it. It is excluded from the semantic-parity fingerprint for
    exactly that reason: comparing two directions must not compare their
    prototype chrome."""
    ids = stage_ids(data)
    dirs = "".join(
        _link(d, stage_id, d.replace("-", " "),
              ' aria-current="true"' if d == direction else "", nav_shape)
        for d in DIRECTIONS)
    navs = "".join(
        _link(direction, stage_id, shape,
              ' aria-current="true"' if shape == nav_shape else "", shape)
        for shape in NAV_SHAPES)
    steps = "".join(
        _link(direction, sid, STAGE_LABELS.get(sid, sid),
              ' aria-current="page"' if sid == stage_id else "", nav_shape)
        for sid in ids)
    return ('<nav class="vf-chrome" data-prototype-chrome '
            'aria-label="Prototype controls">'
            '<p class="vf-chrome-label">Look</p>'
            '<ul class="vf-dirs">%s</ul>'
            '<p class="vf-chrome-label">Nav</p>'
            '<ul class="vf-dirs vf-navs">%s</ul>'
            '<p class="vf-chrome-label">Screen</p>'
            '<ol class="vf-steps">%s</ol></nav>' % (dirs, navs, steps))


def _pager(data, direction, stage_id, nav_shape=DEFAULT_NAV):
    ids = stage_ids(data)
    index = ids.index(stage_id)
    links = []
    if index > 0:
        links.append('<a class="vf-prev" href="?direction=%s&amp;nav=%s&amp;stage=%s">'
                     'Back to %s</a>'
                     % (direction, nav_shape, ids[index - 1],
                        _esc(STAGE_LABELS.get(ids[index - 1], ""))))
    if index < len(ids) - 1:
        links.append('<a class="vf-next" href="?direction=%s&amp;nav=%s&amp;stage=%s">'
                     'Continue to %s</a>'
                     % (direction, nav_shape, ids[index + 1],
                        _esc(STAGE_LABELS.get(ids[index + 1], ""))))
    return ('<nav class="vf-pager" aria-label="Flow"><p class="vf-progress">'
            "Step %d of %d</p>%s</nav>"
            % (index + 1, len(ids), "".join(links)))


def render_stage(data, stage_id, base=None):
    """One stage as one screen. The product is a sequence of screens rather
    than one long scroll, so a prototype that stacks every state on one page
    is not testing the flow it claims to test."""
    stage = find_stage(data, stage_id)
    if stage is None:
        return presentation.state_panel({
            "kind": "unknown",
            "status": "This screen is unavailable. The prototype renders "
                      "synthetic fixture content only, and this flow stage "
                      "was not supplied."})
    renderer = RENDERERS.get(stage.get("kind"))
    if renderer is None:
        return presentation.state_panel({
            "kind": "unknown",
            "status": "This stage kind is unavailable in the fixture renderer."})
    if stage.get("kind") == "harness":
        stage = harness_state(stage, base)
    return ('<section class="vf-stage" data-stage="%s"><h2>%s</h2>%s</section>'
            % (_esc(stage.get("id")), _esc(stage.get("title")), renderer(stage)))


def render_body(data, stage_id=None, direction=DEFAULT_DIRECTION,
                nav_shape=DEFAULT_NAV, base=None):
    ids = stage_ids(data)
    if not ids:
        return presentation.state_panel({
            "kind": "unknown",
            "status": "Flow data is unavailable. This prototype renders "
                      "synthetic fixture content only, and none was supplied."})
    if stage_id not in ids:
        stage_id = ids[0]
    inner = render_stage(data, stage_id, base).replace(
        "DIR", direction).replace("NAV", nav_shape)
    gmap = gloss_map(data)
    used = dict((slug, rec) for slug, rec in gmap.items()
                if ('gloss-%s' % slug) in inner)
    panels = "".join(lesson._gloss_panel_html(rec, slug)
                     for slug, rec in used.items())
    appendix = lesson._glossary_html(used, {}) if used else ""
    return "".join([
        _prototype_chrome(data, direction, stage_id, nav_shape),
        '<div class="vf-app" data-nav="%s">' % _esc(nav_shape),
        _app_nav(data, direction, nav_shape, stage_id),
        '<div class="vf-appmain">', inner, panels, appendix,
        _pager(data, direction, stage_id, nav_shape), "</div></div>"])


def token_css(tokens):
    safe = clamp_tokens(tokens)
    tight = safe["density"] == "compact"
    return (":root{--vf-density:%s;--vf-measure:%s;--vf-leading:%s;"
            "--vf-text-xs:0.8125rem;--vf-micro:0.75rem;--vf-meta:0.8125rem;"
            "--vf-body:%s;--vf-h3:1.125rem;--vf-h2:%s;--vf-h1:%s;"
            "--accent:%s;}"
            % (safe["density"], safe["measure"], safe["leading"],
               "1rem" if tight else "1.0625rem",
               "1.375rem" if tight else "1.5rem",
               "1.75rem" if tight else "2rem",
               safe["accent"]))


def page(data, direction=DEFAULT_DIRECTION, tokens=None, stage_id=None,
         nav_shape=DEFAULT_NAV, base=None):
    """One screen of one direction. The body never varies by direction; the
    style block does. Hover definitions come from surfaces/lesson.py, so the
    product has one glossary implementation rather than two."""
    if direction not in DIRECTIONS:
        direction = DEFAULT_DIRECTION
    if nav_shape not in NAV_SHAPES:
        nav_shape = DEFAULT_NAV
    body = render_body(data, stage_id, direction, nav_shape, base)
    marked = set(re.findall(r'popovertarget="gloss-([a-z0-9-]+)"', body))
    css = "\n".join([theme.theme_css(theme.DEFAULT_THEME_CONFIG),
                      token_css(tokens), CHROME_CSS, lesson.gloss_css(),
                      lesson._gloss_anchor_css(marked), FIXED_RULES,
                      overlay_css("_nav-shared"), overlay_css("nav-" + nav_shape),
                      direction_css(direction)])
    stage = find_stage(data, stage_id) or (data.get("stages") or [{}])[0]
    title = stage.get("title") or "Visual direction prototype (synthetic)"
    return presentation.surface_shell(
        title, body, theme_css=css,
        context=["Synthetic fixture", "Development only",
                 "Direction: %s" % direction],
        noscript="Hover definitions also open on click, with no JavaScript.")



# --------------------------------------------------------------------------
# One self-contained file.
#
# The multi-file export links each screen to a sibling file. That is correct
# for walking a folder and useless anywhere the sibling files are not present,
# such as a preview pane handed a single file: every link is dead and the
# prototype reads as broken when it is only incomplete.
#
# This builder inlines every screen, every look and every navigation shape into
# one document and switches between them with radio inputs and CSS. No script,
# no navigation, no sibling files. It works in a sandbox that blocks scripts,
# because there is nothing to block.
# --------------------------------------------------------------------------

# The shipped glossary panel positions itself with CSS anchor positioning
# (position-anchor, position-area, position-try-fallbacks), which is recent
# enough that a viewer without it renders an absolutely positioned panel at an
# arbitrary place on the page. That is most of what "looks broken" means here.
# Progressive enhancement in the correct order: a fixed bottom sheet that works
# everywhere is the base, and anchor positioning is the upgrade.
GLOSS_FALLBACK_CSS = """
.gloss[popover] { position: fixed; inset: auto var(--space-4) var(--space-4) auto;
  max-width: min(38ch, calc(100vw - var(--space-6))); margin: 0; }
@supports (position-area: block-end span-inline-end) {
  .gloss[popover] { position: absolute; inset: auto; }
}
/* Where the Popover API itself is unavailable, :target still opens the panel,
   so a definition is never unreachable. */
.gloss:target { display: block; position: fixed;
  inset: auto var(--space-4) var(--space-4) auto; }
"""

ONEFILE_CSS = """
.of-switch { position: absolute; width: 1px; height: 1px; overflow: hidden;
  clip-path: inset(50%); white-space: nowrap; }
.of-bar { display: flex; flex-wrap: wrap; gap: var(--space-2) var(--space-4);
  align-items: center; padding: var(--space-3);
  border: 1px dashed var(--line); border-radius: var(--r-2);
  background: var(--chip); margin-bottom: var(--space-6); }
.of-group { display: flex; flex-wrap: wrap; gap: var(--space-1);
  align-items: center; }
.of-group > b { font-size: var(--vf-micro); text-transform: uppercase;
  letter-spacing: .09em; color: var(--mut); font-weight: 600;
  margin-inline-end: var(--space-1); font-family: var(--font-ledger); }
.of-bar label, .vf-appnav label, .vf-pager label, .vf-resume label {
  cursor: pointer; }
.of-bar label { display: inline-block; padding: 3px var(--space-3);
  border-radius: var(--r-1); border: 1px solid transparent;
  font-size: var(--vf-micro); color: var(--mut); }
.of-bar label:hover { color: var(--ink); background: var(--card); }
.of-screen { display: none; }
.of-swatch { display: inline-block; width: 1.15rem; height: 1.15rem;
  border-radius: 50%; border: 2px solid var(--line); vertical-align: -3px; }
.of-bar label:has(.of-swatch) { padding: 3px; }
.of-note { font-size: var(--vf-meta); color: var(--mut); margin: 0 0 var(--space-4);
  font-family: var(--font-ledger); }
/* Nav and pager entries are labels here, not links, so they need the link look. */
.vf-appnav label { display: block; padding: var(--space-2) var(--space-3);
  border-radius: var(--r-2); color: var(--mut); }
.vf-appnav label:hover { color: var(--ink); background: var(--chip); }
.vf-pager label, .vf-resume label { display: inline-block; text-decoration: none;
  font-size: var(--vf-body); padding: var(--space-2) var(--space-4);
  border-radius: var(--r-2); border: 1px solid var(--line); color: var(--ink); }
.vf-pager label.vf-next, .vf-resume label.vf-next { background: var(--accent);
  color: var(--card); border-color: var(--accent); }
"""


def _scope_css(css, guard):
    """Prefix every selector in `css` with `guard`, keeping at-rule wrappers.

    Deliberately small: it handles the nesting these overlays actually use,
    which is plain rules and one level of @media/@supports. It is not a CSS
    parser and does not pretend to be one.
    """
    out = []
    depth = 0
    buf = ""
    i = 0
    while i < len(css):
        ch = css[i]
        if ch == "{":
            selector = buf.strip()
            buf = ""
            if selector.startswith("@"):
                out.append(selector + "{")
                depth += 1
            else:
                scoped = ", ".join(
                    ("%s %s" % (guard, part.strip())) if part.strip() else ""
                    for part in selector.split(","))
                out.append(scoped + "{")
                depth += 1
            i += 1
            continue
        if ch == "}":
            out.append(buf)
            buf = ""
            out.append("}")
            depth -= 1
            i += 1
            continue
        if ch == ";" and depth > 0:
            out.append(buf + ";")
            buf = ""
            i += 1
            continue
        buf += ch
        i += 1
    out.append(buf)
    return "".join(out)


def _radio(group, value, checked):
    return ('<input class="of-switch" type="radio" name="%s" id="%s-%s"%s>'
            % (group, group, value, " checked" if checked else ""))


def _label(group, value, text, classes=""):
    cls = ' class="%s"' % classes if classes else ""
    return '<label for="%s-%s"%s>%s</label>' % (group, value, cls, text)


def single_file(data=None, base=None):
    """Every screen, look and nav shape in one document, switched by CSS."""
    data = data if data is not None else load_fixture()
    ids = stage_ids(data)
    app = data.get("app") or {}
    by_id = {a["id"]: a for a in app.get("course_areas", [])}
    by_id.update({a["id"]: a for a in app.get("app_areas", [])
                  if a["id"] not in by_id})

    # --- switches -------------------------------------------------------
    radios = "".join(
        [_radio("look", d, d == DEFAULT_DIRECTION) for d in DIRECTIONS] +
        [_radio("nav", n, n == DEFAULT_NAV) for n in NAV_SHAPES] +
        [_radio("accent", name, name == DEFAULT_ACCENT_ID)
         for name, _ in ACCENTS] +
        [_radio("screen", sid, i == 0) for i, sid in enumerate(ids)])

    bar = ('<div class="of-bar">'
           '<span class="of-group"><b>Look</b>%s</span>'
           '<span class="of-group"><b>Nav</b>%s</span>'
           '<span class="of-group"><b>Accent</b>%s</span>'
           '<span class="of-group"><b>Screen</b>%s</span></div>'
           % ("".join(_label("look", d, _esc(d.replace("-", " ")))
                      for d in DIRECTIONS),
              "".join(_label("nav", n, _esc(n)) for n in NAV_SHAPES),
              "".join(_label("accent", name,
                             '<span class="of-swatch" style="background:%s"></span>'
                             "<span class=\"of-switch\">%s</span>"
                             % (_esc(hexcode), _esc(name)))
                      for name, hexcode in ACCENTS),
              "".join(_label("screen", sid, _esc(STAGE_LABELS.get(sid, sid)))
                      for sid in ids)))

    # --- app nav, as labels rather than links ---------------------------
    def nav_entry(area_id):
        area = by_id.get(area_id)
        if not area:
            return ""
        target = area.get("stage")
        inner = ('<span class="vf-area-label">%s</span>'
                 '<span class="vf-area-route">%s</span>'
                 % (_esc(area["label"]), _esc(area["route"])))
        if target in ids:
            return "<li>%s</li>" % _label("screen", target, inner)
        return ('<li class="vf-area-todo"><span class="vf-area-entry">%s'
                "</span></li>" % inner)

    sections = "".join(
        '<p class="vf-nav-label">%s</p><ul class="vf-nav-course" data-section="%s">%s</ul>'
        % (_esc(sec["label"]), _esc(sec["id"]),
           "".join(nav_entry(a) for a in sec.get("areas", [])))
        for sec in app.get("sections", []))
    app_rows = "".join(
        "<li>%s</li>" % _label(
            "screen", ids[0],
            '<span class="vf-area-label">%s</span>'
            '<span class="vf-area-route">%s</span>'
            % (_esc(a["label"]), _esc(a["route"])))
        for a in app.get("app_areas", []))
    appnav = ('<nav class="vf-appnav" aria-label="Application">'
              '<p class="vf-nav-brand">itembank</p>'
              '<p class="vf-nav-label">App</p><ul class="vf-nav-app">%s</ul>'
              "%s%s</nav>" % (app_rows, _course_picker(app), sections))

    # --- screens --------------------------------------------------------
    screens = []
    for index, sid in enumerate(ids):
        inner = render_stage(data, sid, base)
        # Turn the resume link into a real switch rather than a dead anchor.
        for target in ids:
            inner = inner.replace(
                '<a class="vf-next" href="?direction=DIR&amp;nav=NAV&amp;stage=%s">'
                % target,
                '<label class="vf-next" for="screen-%s">' % target)
        inner = inner.replace('href="?direction=DIR&amp;nav=NAV&amp;stage=',
                              'data-screen-link="')
        pager = ['<p class="vf-progress">Step %d of %d</p>' % (index + 1, len(ids))]
        if index > 0:
            pager.append(_label("screen", ids[index - 1],
                                "Back to " + _esc(STAGE_LABELS.get(ids[index - 1], "")),
                                "vf-prev"))
        if index < len(ids) - 1:
            pager.append(_label("screen", ids[index + 1],
                                "Continue to " + _esc(STAGE_LABELS.get(ids[index + 1], "")),
                                "vf-next"))
        gmap = gloss_map(data)
        used = dict((slug, rec) for slug, rec in gmap.items()
                    if ("gloss-%s" % slug) in inner)
        panels = "".join(lesson._gloss_panel_html(rec, slug)
                         for slug, rec in used.items())
        appendix = lesson._glossary_html(used, {}) if used else ""
        screens.append(
            '<div class="of-screen" data-screen="%s"><div class="vf-app">%s'
            '<div class="vf-appmain">%s%s%s'
            '<nav class="vf-pager" aria-label="Flow">%s</nav>'
            "</div></div></div>"
            % (_esc(sid), appnav, inner, panels, appendix, "".join(pager)))

    # --- css ------------------------------------------------------------
    marked = set()
    for slug in gloss_map(data):
        marked.add(slug)
    parts = [theme.theme_css(theme.DEFAULT_THEME_CONFIG), token_css(None),
             CHROME_CSS, lesson.gloss_css(), lesson._gloss_anchor_css(marked),
             GLOSS_FALLBACK_CSS, FIXED_RULES, ONEFILE_CSS,
             _scope_css(overlay_css("_nav-shared"), "body")]
    for direction in DIRECTIONS:
        parts.append(_scope_css(direction_css(direction),
                                "body:has(#look-%s:checked)" % direction))
    for shape in NAV_SHAPES:
        parts.append(_scope_css(overlay_css("nav-" + shape),
                                "body:has(#nav-%s:checked)" % shape))
    for sid in ids:
        parts.append('body:has(#screen-%s:checked) [data-screen="%s"]'
                     "{display:block}" % (sid, sid))
        parts.append('body:has(#screen-%s:checked) label[for="screen-%s"]'
                     "{color:var(--ink);background:var(--card);"
                     "border-color:var(--line);font-weight:600}" % (sid, sid))
    for name, hexcode in ACCENTS:
        palette = theme.theme_css({"theme": "system", "accent": {"source": hexcode}})
        parts.append(_scope_css(palette, "body:has(#accent-%s:checked)" % name))
    for group, values in (("look", DIRECTIONS), ("nav", NAV_SHAPES),
                          ("accent", [n for n, _ in ACCENTS])):
        for value in values:
            parts.append('body:has(#%s-%s:checked) label[for="%s-%s"]'
                         "{color:var(--ink);background:var(--card);"
                         "border-color:var(--line);font-weight:600}"
                         % (group, value, group, value))

    note = ('<p class="of-note">Every screen, look and navigation shape is in '
            "this one file. Switching uses radio inputs and CSS, so nothing "
            "here needs JavaScript or a second file.</p>")
    return presentation.surface_shell(
        "itembank prototype (synthetic)",
        radios + bar + note + "".join(screens),
        theme_css="\n".join(parts),
        context=["Synthetic fixture", "Development only", "One file, no script"],
        noscript="This page uses no JavaScript.")


def write_static(out_dir, data=None):
    """Write every direction and every screen as linked static files, so the
    whole flow is walkable by opening one file with no server running."""
    data = data if data is not None else load_fixture()
    written = []
    ids = stage_ids(data)
    for direction in DIRECTIONS:
        for nav_shape in NAV_SHAPES:
            target = os.path.join(out_dir, "%s-%s" % (direction, nav_shape))
            os.makedirs(target, exist_ok=True)
            for sid in ids:
                markup = page(data, direction, stage_id=sid, nav_shape=nav_shape)
                for other in DIRECTIONS:
                    for other_nav in NAV_SHAPES:
                        for other_stage in ids:
                            markup = markup.replace(
                                'href="?direction=%s&amp;nav=%s&amp;stage=%s"'
                                % (other, other_nav, other_stage),
                                'href="../%s-%s/%s.html"'
                                % (other, other_nav, other_stage))
                path = os.path.join(target, sid + ".html")
                with io.open(path, "w", encoding="utf-8") as fh:
                    fh.write(markup)
                written.append(path)
    return written
