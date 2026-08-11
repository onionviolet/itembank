"""The lesson reader: a bank's teaching text rendered as a document, linked
both ways to the items that test it.

This is a read-only render of author-provided prose. It holds no answer key
and reaches no verdict, and its links navigate rather than answer (D-10): the
only way out of a lesson is to another surface, never to a score.
"""
import html, json, os, re, sys

import evidence
from model import (grab, lesson_slug, load, load_style, parse_key_blocks,
                   parse_lesson, parse_terms, resolve_style)
from runtime import glossable
from surfaces.presentation import SHARED_CSS
from surfaces import settings
from surfaces.theme import THEME_CSS


SUB_BYLINE = ("Reading material for this bank. Following a link below opens "
              "the item in a new tab; nothing here is scored.")

EMPTY_HEADING = "No lesson yet"
EMPTY_BODY = ("This bank has no ## LESSON section. Add one above the first "
              "Qn. line \u2014 see itembank spec for the LESSON/LESSON-REF grammar.")
WARN_SENTENCE = ("The external lesson file for this bank could not be read. "
                 "Run itembank lint %s for details.")
ORPHAN_COPY = "No items reference this section yet."
BACKLINKS_LABEL = "Items testing this"
CHIP_LABEL = "Read the lesson"

# The plan 03.1-02 copywriting additions (03.1-UI-SPEC §15), verbatim: the
# linter, the renderer, and the tests reproduce the same strings, so a CI
# grep and an authoring agent read the same contract.
GLOSSARY_HEADING = "Glossary"
HELD_COPY = "Some definitions are held until you answer."
UNAVAILABLE_COPY = ("Definitions are unavailable right now. The glossary is "
                    "at the end of the lesson.")
FULL_ENTRY_COPY = "Full entry"
BACK_TO_QUESTION_COPY = "Back to the question"
LOADING_COPY = "Loading the definition\u2026"
SECTIONS_NAV_COPY = "Sections in this lesson"
BACK_TO_FIRST_USE_COPY = "Back to first use"
ADD_TO_REVIEW_COPY = "Add to review"
REVIEW_UNAVAILABLE_COPY = ("Review scheduling is unavailable without the "
                           "runtime. Run itembank export anki to take this "
                           "key to Anki.")
ANSWERS_HEADING = "Answers"

# The style footer and refusal copy (03.1-UI-SPEC 9.6, 15): the only place
# these strings live, so the renderer, the CLI, and the tests reproduce one
# copy contract. The degraded copy echoes the author-written style id and
# the bank basename -- never a resolved absolute path (T-3-07 precedent).
STYLE_FOOT = "style: %s \u00b7 rendered by render_style"
HOUSE_FOOT = "style: house"
STYLE_DEGRADED_COPY = ("The style file %s could not be read. This lesson "
                       "is shown in the house style. Run itembank lint %s "
                       "for details.")
RENDER_REFUSAL_COPY = ("render_style cannot turn %s into %s; that is a "
                       "rewrite, not a rearrangement. No file was changed.")

# Only the degraded state carries the warn note, so its style is substituted
# in (like __THEME__) rather than shipped on every page -- a bank with no
# lesson and a bank whose lesson source broke must be visually
# distinguishable, and the plain empty state must contain no --warn styling
# at all. `overflow-wrap`/`word-break` make a long [LESSON-SRC:] path wrap
# inside the card; there is deliberately no nowrap and no ellipsis
# truncation on the code element.
WARN_CSS = """.warn{color:var(--warn);font-size:14px;margin:14px auto 0;max-width:520px;
  text-align:center}
.warn code{overflow-wrap:anywhere;word-break:break-all}
"""


# The lesson reader's own CSS layer (03.1-UI-SPEC §2 Reader CSS LOCKED):
# structure and spacing only, riding the shared theme tokens and SHARED_CSS.
# Fonts resolve by token -- --font-paper for Paper-voice prose, --font-ledger
# for Ledger-voice labels -- never a literal family. Sizes are the locked
# project scale (12/16/18/20/32) and the weight pair is 400/600; this layer
# introduces no sixth size and no third weight. Every colour is var(--token):
# no hex literal, no second palette (03.1-UI-SPEC §5).
LESSON_CSS = r"""
.wrap{max-width:var(--measure-prose);margin:0 auto;
  padding:var(--space-4) var(--space-3) var(--space-7);
  font-family:var(--font-paper)}
header{margin-bottom:var(--space-4)}
h1{font-size:32px;font-weight:600;line-height:1.1;margin:0 0 var(--space-3)}
.sub{color:var(--mut);font-size:12px}
.card{background:var(--card);border:1px solid var(--line);
  border-radius:12px;padding:var(--space-4) var(--space-4) var(--space-3)}
section{margin-bottom:var(--space-4)}
h2{font-size:20px;font-weight:600;line-height:1.2;margin:var(--space-6) 0 var(--space-3)}
h3{font-size:16px;font-weight:600;line-height:1.4;margin:var(--space-5) 0 var(--space-2)}
p,li{font-size:18px;line-height:var(--leading-lesson);
  margin:0 0 var(--space-3)}
.bl{margin-top:var(--space-2);padding-top:var(--space-2);
  border-top:1px solid var(--line)}
.blabel{display:block;font-size:12px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--mut);margin-bottom:var(--space-1);
  font-family:var(--font-ledger)}
.bl a{display:block;color:var(--accent);text-decoration:none;
  margin:var(--space-1) 0}
.bl a:hover,.bl a:focus-visible{text-decoration:underline;
  outline:2px solid var(--accent);outline-offset:2px}
.scroll{overflow-x:auto;margin:0 0 var(--space-2);
  max-width:var(--measure-wide)}
/* The Phase 9 D-13 table wrapper: the labelled focusable region that owns
   horizontal overflow at narrow widths; the lesson page itself never
   widens. Cells wrap (`overflow-wrap:anywhere`) instead of stretching the
   wrapper, and the focus boundary is the visible --accent outline. */
.lesson-table-scroll{max-width:100%}
.lesson-table-scroll:focus-visible{outline:2px solid var(--accent);
  outline-offset:2px}
pre{margin:0;background:var(--chip);border-radius:8px;
  padding:var(--space-2) var(--space-3)}
pre code{display:block;font-family:var(--font-ledger);font-size:14px;
  line-height:1.5;color:var(--ink)}
.lang{display:block;font-size:12px;letter-spacing:.05em;color:var(--mut);
  margin-bottom:var(--space-1);font-family:var(--font-ledger)}
table{border-collapse:collapse;margin:0 0 var(--space-2);min-width:100%}
th,td{border:1px solid var(--line);padding:var(--space-2);
  text-align:left;font-size:14px;overflow-wrap:anywhere}
th{background:var(--chip);color:var(--mut);font-weight:600}
.orphan{color:var(--mut);font-size:14px}
.empty{text-align:center;padding:var(--space-6) var(--space-3)}
.empty p{color:var(--mut);max-width:var(--measure-prose);margin:0 auto}
.callout{background:var(--card);border:1px solid var(--line);
  border-radius:var(--r-3);box-shadow:0 1px 0 var(--line);
  padding:var(--space-3);margin:0 0 var(--space-4)}
.callout-label{display:flex;align-items:center;gap:var(--space-1);
  font-size:12px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--mut);margin:0 0 var(--space-2);font-family:var(--font-ledger)}
.callout-icon{display:inline-flex}
.callout-body p:last-child{margin:0}
.term{text-decoration:underline dotted;text-underline-offset:.15em;
  color:currentColor;background:none;border:0;padding:0;font:inherit;
  cursor:pointer}
.term:hover,.term:focus-visible{outline:2px solid var(--accent);
  outline-offset:2px}
.gloss{max-width:min(38ch,calc(100vw - var(--space-4)));
  border:1px solid var(--line);border-radius:var(--r-3);
  background:var(--card);padding:var(--space-3);box-shadow:0 1px 0 var(--line)}
.gloss-term{font-weight:600;margin:0 0 var(--space-1);font-size:18px}
.gloss-def{margin:0 0 var(--space-2);font-size:18px;
  line-height:var(--leading-lesson)}
.gloss-more{margin:0;font-size:12px}
.gloss-more a{color:var(--accent);text-decoration:none}
.gloss-more a:hover,.gloss-more a:focus-visible{text-decoration:underline}
#glossary{margin-top:var(--space-7)}
#glossary h2{font-family:var(--font-ledger);font-size:12px;
  letter-spacing:.08em;text-transform:uppercase;color:var(--mut);
  margin:0 0 var(--space-3)}
#glossary dl{margin:0}
#glossary dt{font-weight:600;margin:var(--space-3) 0 var(--space-1);
  font-size:18px}
#glossary dd{margin:0 0 var(--space-3);font-size:18px;
  line-height:var(--leading-lesson)}
.gloss-back{display:block;font-size:12px;color:var(--accent);
  text-decoration:none;margin-top:var(--space-1)}
.gloss-back:hover,.gloss-back:focus-visible{text-decoration:underline}
/* 09-04 Math: the named display wrapper owns horizontal overflow so a wide
   formula scrolls inside the card and the viewport never widens (09-UI-SPEC
   Responsive). The failure note is a persistent adjacent status, never a
   toast: text plus token, not color-only (Capability/media unavailable). */
.lesson-math-display{overflow-x:auto;overflow-y:hidden;max-width:100%}
.lesson-math-note{font-family:var(--font-ledger);font-size:12px;
  color:var(--warn);margin:var(--space-2) 0 0}
.held{font-family:var(--font-ledger);font-size:12px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--mut);margin:var(--space-6) 0 0}
.style-foot{font-family:var(--font-ledger);font-size:12px;
  letter-spacing:.08em;text-transform:uppercase;color:var(--mut);
  margin:var(--space-4) 0 0;text-align:center}
.reader-nav{margin:0 0 var(--space-4)}
.reader-nav summary{cursor:pointer;color:var(--mut);font-size:12px;
  font-family:var(--font-ledger);letter-spacing:.08em;
  text-transform:uppercase}
.reader-nav ul{list-style:none;margin:var(--space-2) 0 0;padding:0}
.reader-nav li{margin:0 0 var(--space-1)}
.reader-nav a{color:var(--accent);text-decoration:none}
.reader-nav a:hover,.reader-nav a:focus-visible{text-decoration:underline}
.callout-example.example-parallel{display:grid;
  grid-template-columns:1fr 1fr;gap:var(--space-3)}
@media print{
  @page{margin:18mm}
  h2{break-after:avoid}
  [popover]{display:none}
  .reader-nav{display:none}
  .gloss-back{display:none}
  .callout{box-shadow:none}
  .callout-check{border:0;border-top:1px solid var(--line);border-radius:0;
    background:none;padding:var(--space-2) 0 0}
  /* Check · <objective> label lands with the gate that fills the slot
     (plan 03.1-04 / Phase 6.2); the reserved slot prints as a labelled
     rule, never an empty box (03.1-UI-SPEC §9.4 D1). */
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
/* ?print=drill second-stylesheet placeholder hook: cloze blanking and the
   Answers list land in plan 03.1-04 as a second stylesheet plus one
   server-side blanking pass -- never a second renderer (03.1-UI-SPEC §10). */
"""


LESSON_TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title>
<style>
__THEME__
__SHARED_CSS__
__LESSON_CSS__
__WARN_CSS__
__GLOSS_ANCHOR_CSS__
__GLOSS_PRINT_CSS__
</style>
__MATH_ASSETS__
</head><body><div class="wrap">
<header>
  <h1>__TITLE__</h1>
  <div class="sub">__SUB__</div>
</header>
__READER_NAV__
__GLOSS_SCRIPT__
<div class="card" id="lesson-content">__STYLE_WARN____BODY__</div>
__MATH_SCRIPT__
<p class="style-foot">__STYLE_FOOT__</p>
</div></body></html>"""


# 09-04 offline Math (09-UI-SPEC "Math" / Component matrix): the lesson
# page loads the vendored KaTeX distribution from the daemon's closed
# /assets/katex/ map -- never a CDN (D-07). `__MATH_ASSETS__` carries the
# three allowlisted browser files in load order (CSS first, then core, then
# auto-render); `__MATH_SCRIPT__` runs the lesson-scoped adapter after the
# content node exists. Both are empty strings on every non-Math profile, so
# an EMT/plain lesson is byte-identical to the pre-09-04 reader (D-08).
MATH_ASSETS_HTML = (
    '<link rel="stylesheet" href="/assets/katex/katex.min.css">\n'
    '<script src="/assets/katex/katex.min.js"></script>\n'
    '<script src="/assets/katex/contrib/auto-render.min.js"></script>')

# The adapter's exact failure copy (09-UI-SPEC "Copy and error grammar"),
# kept here once so the JS, the tests, and the spec can never drift:
MATH_UNAVAILABLE_COPY = "Math unavailable. Formula source is shown."
MATH_PARSE_FAILURE_COPY = ("Math could not be rendered. "
                           "Formula source is shown.")

# 09-04 lesson-scoped math adapter: enhances only `#lesson-content`, leaves
# every Phase 3 `pre`/`code` node untouched, renders display delimiters
# before inline ones, and fails readable. `trust:false` blocks KaTeX's raw
# HTML/class/URL macros; `throwOnError:false` keeps the delimited source
# visible as KaTeX's own error output (a `.katex-error` node holding the
# source); `maxExpand`/`maxSize` bound pathological input (T-09-10/11). If
# the local assets never loaded, one lesson-level unavailable note is
# appended and the raw source remains the page's content -- no CDN fallback,
# no deletion of the source (D-06/D-07).
MATH_ADAPTER_JS = """<script>
(function () {
  var content = document.getElementById("lesson-content");
  if (!content) { return; }
  var note = function (cls, text) {
    var n = document.createElement("p");
    n.className = cls;
    n.textContent = text;
    return n;
  };
  if (typeof window.katex === "undefined" ||
      typeof window.renderMathInElement !== "function") {
    content.appendChild(note("lesson-math-note", %(unavailable)s));
    return;
  }
  var displays = content.querySelectorAll(".katex-display");
  try {
    renderMathInElement(content, {
      delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false}
      ],
      ignoredTags: ["pre", "code", "script", "noscript", "style", "textarea"],
      throwOnError: false,
      trust: false,
      maxExpand: 1000,
      maxSize: 50
    });
  } catch (e) {
    content.appendChild(note("lesson-math-note", %(parse_failure)s));
    return;
  }
  // Display math owns its horizontal overflow in a named wrapper
  // (09-UI-SPEC Responsive): auto-render emits `.katex-display`, and the
  // page wraps each in `.lesson-math-display` so a wide formula scrolls
  // inside the card instead of widening the viewport.
  content.querySelectorAll(".katex-display").forEach(function (el) {
    var wrap = document.createElement("div");
    wrap.className = "lesson-math-display";
    el.parentNode.insertBefore(wrap, el);
    wrap.appendChild(el);
  });
  // One parse failure leaves KaTeX's own error node (the source, readable)
  // plus the exact explanatory note beside it; no error handler deletes it.
  content.querySelectorAll(".katex-error").forEach(function (el) {
    if (el.parentNode.classList.contains("lesson-math-note")) { return; }
    var n = note("lesson-math-note", %(parse_failure)s);
    el.parentNode.insertBefore(n, el.nextSibling);
  });
})();
</script>""" % {
    "unavailable": json.dumps(MATH_UNAVAILABLE_COPY),
    "parse_failure": json.dumps(MATH_PARSE_FAILURE_COPY),
}


def _truncate(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit] + "\u2026"


_TOKEN_RE = re.compile(r"^\x00K(\d+)\x00$")
_FENCE_RE = re.compile(r"^(`{3,})\s*(.*?)\s*$")
_CALLOUT_MARK_RE = re.compile(r"^>\s*\[!([A-Za-z][^\]]*)\]\s*(.*)$")

# The locked callout kinds (03.1-UI-SPEC §9.2-§9.4): each maps to the exact
# Ledger-voice label the renderer and the linter share (§15). The `CHECK:`
# prefix is handled separately as the inert reserved slot (D-18). Adding a
# kind is a one-line registration here -- the container and its degradation
# contract do not change.
_CALLOUT_KINDS = {
    "KEY": ("key", "Key point"),
    "EXAMPLE": ("example", "Example"),
    "NOTE": ("note", "Note"),
    "WARNING": ("warning", "Warning"),
}

# One in-repo decorative callout mark (03.1-UI-SPEC §2): a single 16×16
# currentColor SVG glyph, aria-hidden, whose visible Ledger label carries
# all semantics -- an icon that fails to render loses nothing.
_CALLOUT_ICON = ('<svg width="16" height="16" viewBox="0 0 16 16" '
                 'aria-hidden="true" focusable="false"><rect x="1.5" y="1.5" '
                 'width="13" height="13" rx="2.5" fill="none" '
                 'stroke="currentColor" stroke-width="1.5"/>'
                 '<path d="M8 6.5v4" stroke="currentColor" stroke-width="1.5" '
                 'stroke-linecap="round"/><circle cx="8" cy="4.3" r="1" '
                 'fill="currentColor"/></svg>')


# The one runtime-shipped, vendored, reviewed enhancement hook (03.1-UI-SPEC
# §8.3/C6): the in-sitting gloss fetch. The reader page ships every
# definition, so this is inert unless a trigger carries `data-gloss-fetch`
# (the sitting variant a later plan fills). It intercepts activation, fills
# the panel from the served contract, and on failure renders the locked
# unavailable copy -- never a spinner and never a dead control. The
# navigation href on the trigger remains a real fallback.
GLOSS_ENHANCEMENT_JS = """<script>
(function () {
  var LOADING = %(loading)s;
  var UNAVAILABLE = %(unavailable)s;
  document.addEventListener("click", function (ev) {
    var t = ev.target && ev.target.closest
        ? ev.target.closest("[data-gloss-fetch]") : null;
    if (!t) { return; }
    var panel = document.getElementById(t.getAttribute("aria-details"));
    var def = panel && panel.querySelector(".gloss-def");
    if (!def || def.getAttribute("data-gloss-state") === "done") { return; }
    def.textContent = LOADING;
    def.setAttribute("data-gloss-state", "loading");
    fetch(t.getAttribute("data-gloss-fetch"))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        def.textContent = d && d.def ? d.def : UNAVAILABLE;
        def.setAttribute("data-gloss-state", "done");
      })
      .catch(function () {
        def.textContent = UNAVAILABLE;
        def.setAttribute("data-gloss-state", "done");
      });
  }, true);
})();
</script>""" % {"loading": json.dumps(LOADING_COPY),
                 "unavailable": json.dumps(UNAVAILABLE_COPY)}


def _gloss_trigger_html(ref_text, slug):
    """One Popover-API trigger (03.1-UI-SPEC §8.1 DOM LOCKED): a real
    `<button>` whose accessible name is the term text itself -- no
    aria-label, no title, so a definition can never ride the trigger's
    accessible name (C7)."""
    return ('<button type="button" class="term" popovertarget="gloss-%s" '
            'aria-details="gloss-%s">%s</button>'
            % (slug, slug, html.escape(ref_text)))


def _gloss_panel_html(record, slug):
    """One `[popover]` panel: the definition ships with the page, so the
    reader gloss works with the network unplugged and before any script
    loads (§8.1). The `Full entry` link is the Chrome-voice target of the
    glossary appendix."""
    return ('<div id="gloss-%s" class="gloss" popover>'
            '<p class="gloss-term">%s</p>'
            '<p class="gloss-def">%s</p>'
            '<p class="gloss-more"><a href="#term-%s">%s</a></p></div>'
            % (slug, html.escape(record["canonical"]), _inline(record["def"]),
               slug, html.escape(FULL_ENTRY_COPY)))


def _glossary_html(gloss_map, first_uses):
    """The glossary appendix (03.1-UI-SPEC §9.1): a `<dl>` in `<section
    id="glossary">`, entries in authored order, each `<dt id="term-<slug>">`
    matching the trigger's anchor, each `<dd>` ending with a Chrome-voice
    back-anchor to the first marked use where one exists. Suppressed terms
    are absent, never an empty `<dt>` (§8.4)."""
    entries = []
    for slug, rec in gloss_map.items():
        back = ""
        use_id = first_uses.get(slug)
        if use_id:
            back = (' <a class="gloss-back" href="#%s">%s</a>'
                    % (use_id, html.escape(BACK_TO_FIRST_USE_COPY)))
        entries.append('<dt id="term-%s">%s</dt><dd>%s%s</dd>'
                       % (slug, html.escape(rec["canonical"]),
                          _inline(rec["def"]), back))
    return ('<section id="glossary"><h2>%s</h2><dl>%s</dl></section>'
            % (html.escape(GLOSSARY_HEADING), "".join(entries)))


def _gloss_anchor_css(marked_slugs):
    """One per-lesson `<style>` block of anchor-name/position-anchor pairs,
    keyed by slug -- never an inline style attribute on bank-derived markup
    (03.1-UI-SPEC §8.1)."""
    rules = []
    for slug in sorted(marked_slugs):
        rules.append(
            'button.term[popovertarget="gloss-%s"]{anchor-name:--anchor-%s}'
            '#gloss-%s{position:absolute;position-anchor:--anchor-%s;'
            'position-try-fallbacks:flip-block,flip-inline}'
            % (slug, slug, slug, slug))
    return "\n".join(rules)


def _gloss_print_css(print_gloss):
    """print_gloss inline (03.1-UI-SPEC §10.1): un-hide each `[popover]`
    panel as a small bordered note. Each term ships exactly one panel, so
    the printed note count equals the distinct-term count by construction.
    The appendix default needs no override: LESSON_CSS already hides
    `[popover]` in print."""
    if print_gloss == "inline":
        return ('@media print{.gloss{display:block!important;'
                'position:static!important;border:1px solid var(--line);'
                'border-radius:var(--r-3);background:var(--card);'
                'padding:var(--space-3);margin:0 0 var(--space-4);'
                'box-shadow:none}.gloss-more{display:none}}')
    return ""


def _reader_nav_html(headings):
    """The reader_nav column (03.1-UI-SPEC §7.3): a collapsed disclosure
    listing every heading by slug, Chrome-voice summary."""
    items = "".join(
        '<li><a href="#%s">%s</a></li>'
        % (h["slug"], html.escape(h["text"])) for h in headings)
    return ('<nav class="reader-nav" aria-label="%s"><details>'
            '<summary>%s</summary><ul>%s</ul></details></nav>'
            % (html.escape(SECTIONS_NAV_COPY),
               html.escape(SECTIONS_NAV_COPY), items))


def _callout_spec(raw):
    """Map one `[!KIND]` marker to its locked `(slug, label)` pair, or None.

    `CHECK:` (with or without an id) maps to the inert reserved slot; the id
    is deliberately dropped -- the anchor carries no key and no scoring path
    (D-18). Any other kind returns None so the block classifier falls
    through to the pre-change paragraph output byte-for-byte: an unknown
    kind never raises and never invents a container.
    """
    kind = raw.strip()
    if kind.startswith("CHECK:"):
        return ("check", "Check")
    return _CALLOUT_KINDS.get(kind)


def _callout_kind_of(line):
    """The dispatch key of one `> [!...]` line: the literal string "KEY"
    for any [!KEY] variant (the plan 03.1-03 card), the locked `(slug,
    label)` pair for the generic kinds, or None for an unknown kind that
    must degrade to the pre-change paragraph output."""
    m = _CALLOUT_MARK_RE.match(line)
    if m is None:
        return None
    kind = m.group(1)
    if kind == "KEY" or kind.startswith("KEY:"):
        return "KEY"
    return _callout_spec(kind)


_KEY_CLOZE_RE = re.compile(r"\{\{([^{}]+)\}\}")


def _cloze_visible(text):
    """The on-screen form of a [!KEY] body: `{{...}}` markers render as
    their enclosed text (03.1-UI-SPEC §9.2); blanking happens only in the
    drill print sheet."""
    return _KEY_CLOZE_RE.sub(lambda m: m.group(1), text)


def _cloze_blank(text):
    """The drill-print blanking pass: every `{{...}}` marker becomes a
    fixed blank, so no answer is visible above the Answers list (§10.2)."""
    return _KEY_CLOZE_RE.sub(lambda m: "____", text)


def _parse_key_callout(raw_lines):
    """The render-side parse of one `> [!KEY]` callout: id from the
    `[ID:]` directive, title from the marker line, body from the remaining
    `>` lines, cloze flag from the body -- the same field set
    `model.parse_key_blocks()` returns, resolved here from the raw lines
    the block renderer already holds."""
    marker = _CALLOUT_MARK_RE.match(raw_lines[0])
    title = marker.group(2).strip() if marker else ""
    raw = "\n".join(raw_lines)
    kid = grab(r"(?m)^>\s*\[ID:\s*(\S+)\s*\]", raw)
    body = []
    for line in raw_lines[1:]:
        stripped = re.sub(r"^>\s?", "", line).strip()
        if not stripped or re.match(r"^\[(ID|HASH):", stripped):
            continue
        body.append(line)
    body_text = "\n".join(body).strip()
    return {"id": kid, "title": title, "body": body_text,
            "cloze": "{{" in body_text}


def _key_card_html(raw_lines, ctx):
    """The full [!KEY] index card (03.1-UI-SPEC §9.2): id anchor, Ledger
    `Key point` label, Paper-voice body with `{{cloze}}` shown as its
    enclosed text (blanked under ?print=drill), the Ledger footer naming
    the minted id, and the real Add-to-review form only when a runtime is
    serving the page -- otherwise the exact unavailable copy, never a dead
    control (C9). An id-less block renders label + body with no footer and
    no control (the §16 empty-state rule)."""
    key = _parse_key_callout(raw_lines)
    kid = key["id"]
    anchor = ""
    if kid:
        anchor = ' id="key-%s"' % lesson_slug(kid)
    if ctx is not None and ctx.get("drill"):
        body = _cloze_blank(key["body"])
    else:
        body = _cloze_visible(key["body"])
    inner = []
    if key["title"]:
        inner.append('<p class="key-title">%s</p>' % html.escape(key["title"]))
    inner.append(_inline(body))
    icon = '<span class="callout-icon">%s</span>' % _CALLOUT_ICON
    label = '<p class="callout-label">%s%s</p>' % (
        icon, html.escape("Key point"))
    foot = ""
    if kid:
        foot += '<p class="callout-foot">%s</p>' % html.escape(
            "key: %s \u00b7 exports to Anki" % kid)
        if ctx is not None and ctx.get("runtime"):
            foot += ('<form method="post" action="/key/%s/review" '
                     'class="actions"><button type="submit" '
                     'class="go primary">%s</button></form>'
                     % (html.escape(kid), html.escape(ADD_TO_REVIEW_COPY)))
        else:
            foot += '<p class="callout-foot">%s</p>' % (
                html.escape(REVIEW_UNAVAILABLE_COPY))
    if ctx is not None and kid:
        ctx.setdefault("key_answers", []).append(
            (kid, _cloze_visible(key["body"])))
    return ('<section class="callout callout-key"%s>%s'
            '<div class="callout-body">%s</div>%s</section>'
            % (anchor, label, "".join(inner), foot))


def _callout_html(spec, body, example_layout="stacked"):
    """One honest callout container (D-18): a `<section class="callout
    callout-<slug>">` whose Ledger-voice label and decorative icon are
    accompanied by the escape-first `_inline()` body pass every other text
    run uses (T-031-01). The `[!CHECK: <id>]` variant renders the inert
    reserved slot with the exact Ledger copy and no form, no key, and no
    scoring path (03.1-UI-SPEC §9.4, §15); authored body text under a check
    marker is reserved for the gate that fills the slot (Phase 6.2).

    `example_layout` is the reader setting (03.1-UI-SPEC §9.3/§14): an
    `[!EXAMPLE]` callout carries the `example-parallel` class when the
    setting is `parallel`, and stays stacked (the default) otherwise.
    """
    slug, label = spec
    icon = '<span class="callout-icon">%s</span>' % _CALLOUT_ICON
    if slug == "check":
        inner = "<p>%s</p>" % html.escape(
            "This check is available when you are reading with a session.")
    else:
        inner = _inline(body)
    extra = ""
    if slug == "example" and example_layout == "parallel":
        extra = " example-parallel"
    return ('<section class="callout callout-%s"><p class="callout-label">'
            "%s%s</p><div class=\"callout-body\">%s</div></section>"
            % (slug + extra, icon, html.escape(label), inner))


def _code_block(info, content):
    """The one markup shape Phase 9 attaches to (D-08): a preformatted
    element wrapping a code element whose class names the info string.
    The class is sanitised with the same restricted character set
    `lesson_slug` uses, so a hostile info string cannot close the class
    attribute or introduce a second one (T-3-10); the content is the
    block's source, HTML-escaped and otherwise untouched -- no re-indent,
    no syntax highlighting. A visible label in the muted foreground names
    the language; there is no KaTeX, no run button and no copy button --
    this plan cuts the seam and leaves it inert.
    """
    lang = lesson_slug(info)
    esc = html.escape(content)
    code = ('<code class="language-%s">%s</code>' % (lang, esc)
            if lang else "<code>%s</code>" % esc)
    label = '<span class="lang">%s</span>' % html.escape(lang) if lang else ""
    return '<div class="scroll">%s<pre>%s</pre></div>' % (label, code)


def _protect_code(text):
    """Lift every fenced block out of a section's text before any inline
    pass, replacing each with an opaque placeholder line that no inline
    pattern can match. Returns `(protected_text, tokens)` with the rendered
    code fragments in order.

    This ordering is the whole design: a single interleaved pass would let
    an emphasis or link pattern reach inside a fenced block and silently
    mangle exactly the content Phase 9 depends on being verbatim, and the
    damage would be invisible until someone read the rendered code closely.
    An unterminated fence treats the rest of the section as the block's
    content -- the forgiving reading that keeps the document readable
    (T-3-04).
    """
    lines = text.split("\n")
    out, tokens = [], []
    i = 0
    while i < len(lines):
        m = _FENCE_RE.match(lines[i])
        if m:
            fence = m.group(1)
            info = m.group(2).strip()
            closer = re.compile(r"^`{%d,}\s*$" % len(fence))
            j = i + 1
            body = []
            while j < len(lines) and not closer.match(lines[j]):
                body.append(lines[j])
                j += 1
            if j < len(lines):
                j += 1  # skip the closing fence line
            tokens.append(_code_block(info, "\n".join(body)))
            out.append("\x00K%d\x00" % (len(tokens) - 1))
            i = j
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out), tokens


def _split_cells(row):
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [c.strip() for c in row.split("|")]


def _is_separator_row(row):
    return all(re.match(r"^:?-+:?$", c) for c in _split_cells(row))


def _table_html(rows, ctx=None):
    """A pipe run whose second line is a separator row of dashes becomes a
    table with the first line as the header; anything that does not fit
    that shape -- a lone pipe line, a missing separator, a row with a
    different cell count -- returns None so the caller falls back to a
    paragraph rather than raising or emitting a broken table (T-3-04).
    Alignment markers are not implemented; D-08 declines that edge case.

    Phase 9 (D-13) keeps the table fully semantic -- native
    `<table><thead><th><tbody><td>` in source order -- inside the shared
    labelled, keyboard-focusable `.lesson-table-scroll` region that owns
    horizontal overflow; header cells carry `scope="col"`. The accessible
    name comes from the nearest lesson heading when one is in scope, else
    the generic lesson-table label. There is no subject-specific renderer
    path (D-12).
    """
    if len(rows) < 2 or not _is_separator_row(rows[1]):
        return None
    header = _split_cells(rows[0])
    body = [_split_cells(r) for r in rows[2:]]
    if any(len(r) != len(header) for r in body):
        return None
    label = (ctx or {}).get("section_title") or "Lesson table"
    head = "".join('<th scope="col">%s</th>' % _inline(c) for c in header)
    rows_html = "".join(
        "<tr>%s</tr>" % "".join("<td>%s</td>" % _inline(c) for c in r)
        for r in body)
    return ('<div class="scroll lesson-table-scroll" tabindex="0" '
            'role="region" aria-label="%s"><table><thead><tr>%s</tr>'
            '</thead><tbody>%s</tbody></table></div>'
            % (html.escape(label), head, rows_html))


_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_STRONG_RE = re.compile(r"(?<!\w)\*\*(.+?)\*\*(?!\w)", re.S)
_EM_RE = re.compile(r"(?<!\w)_([^_]+)_(?!\w)", re.S)
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _link_target_ok(target):
    """Only a plain relative path or an http/https URL becomes an anchor;
    every other target renders as plain text, so a scheme-bearing target in
    lesson prose cannot become a clickable action (T-3-11)."""
    t = target.strip()
    if t.startswith(("http://", "https://")):
        return True
    head = re.split(r"[/#]", t, 1)[0]
    return ":" not in head


def _linkify(text):
    def _rep(m):
        label, target = m.group(1), m.group(2).strip()
        if not _link_target_ok(target):
            return m.group(0)
        return '<a href="%s">%s</a>' % (target, label)
    return _LINK_RE.sub(_rep, text)


def _inline(text):
    """The inline pass for one literal text run, ordered so escaping cannot
    be undone: lift backtick code spans to placeholders first (so they are
    never re-scanned), escape the remaining text, apply emphasis and link
    patterns to the escaped text, then substitute the code spans back in
    escaped. Escaping before the patterns run is what keeps a
    markup-shaped stem or heading from reaching the page as markup
    (T-3-01); markers must sit at a word boundary so an underscore inside
    an identifier does not split it. Unmatched markers stay literal rather
    than raising (T-3-04).
    """
    spans = []

    def _lift(m):
        spans.append(m.group(1))
        return "\x00I%d\x00" % (len(spans) - 1)

    text = _INLINE_CODE_RE.sub(_lift, text)
    text = html.escape(text)
    text = _STRONG_RE.sub(r"<strong>\1</strong>", text)
    text = _EM_RE.sub(r"<em>\1</em>", text)
    text = _linkify(text)
    for idx, span in enumerate(spans):
        text = text.replace("\x00I%d\x00" % idx,
                            "<code>%s</code>" % html.escape(span))
    return text


_GLOSS_MARK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def _gloss_placeholders(text, ctx):
    """Replace `[[term]]` markers in one raw text run with placeholder
    tokens that survive the inline pass, returning `(protected_text,
    tokens)` where each token is the trigger HTML or the bare escaped term
    text. Marking honours gloss_marks all|first-use|none; a term with no
    `## TERMS` entry or a suppressed (non-glossable) one renders as bare
    text with no affordance (UI-SPEC §8.2/§8.4/§16). The term's single
    panel is emitted the first time the term is marked, so the printed
    note count equals the distinct-term count by construction (§10.1).
    """
    tokens = []

    def _rep(m):
        ref_text = m.group(1).strip()
        slug = lesson_slug(ref_text)
        rec = ctx["gloss"].get(slug)
        marked = rec is not None and ctx["marks"] != "none"
        if marked and ctx["marks"] == "first-use":
            key = (ctx["section"], slug)
            if key in ctx["used"]:
                marked = False
            else:
                ctx["used"].add(key)
        if not marked:
            tokens.append(html.escape(ref_text))
        else:
            tokens.append(_gloss_trigger_html(ref_text, slug))
            if slug not in ctx["panels_emitted"]:
                ctx["panels_emitted"].add(slug)
                ctx["first_uses"][slug] = "use-%s" % slug
                ctx["first_use_now"].add(slug)
                ctx["panels"].append((slug, _gloss_panel_html(rec, slug)))
        return "\x00G%d\x00" % (len(tokens) - 1)

    return _GLOSS_MARK_RE.sub(_rep, text), tokens


def _render_blocks(text, ctx=None):
    """The D-08 block classifier for one section: fenced placeholders,
    deeper heading levels, one level of list, pipe tables, then
    paragraphs. Structure is resolved first and every literal text run is
    escaped second -- never the raw source wholesale, which would also
    escape the markup the renderer itself emits.

    `ctx` (when supplied) carries the reader settings and gloss map; the
    gloss substitution runs over paragraph and list-item runs, and each
    term's single panel is emitted right after the paragraph of its first
    marked use -- invisible on screen (top-layer popover) and exactly the
    "note after the paragraph that used it" print-inline reflow (§10.1).
    """
    protected, tokens = _protect_code(text)
    out = []
    lines = protected.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        tm = _TOKEN_RE.match(line)
        if tm:
            out.append(tokens[int(tm.group(1))])
            i += 1
            continue
        cm = _CALLOUT_MARK_RE.match(line)
        if cm and _callout_kind_of(line) is not None:
            # The callout branch (D-18): a `> [!KIND]` marker starts a run
            # whose body is every following `>`-prefixed line, closed at
            # the first non-`>` line. Only locked kinds -- plus the plan
            # 03.1-03 [!KEY] card -- enter here; an unknown kind falls
            # through to the paragraph path unchanged.
            if _callout_kind_of(line) == "KEY":
                raw_lines = [line]
                i += 1
                while i < len(lines) and lines[i].startswith(">"):
                    raw_lines.append(lines[i])
                    i += 1
                out.append(_key_card_html(raw_lines, ctx))
                continue
            spec = _callout_spec(cm.group(1))
            body = [cm.group(2)] if cm.group(2) else []
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                body.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            layout = ctx["example_layout"] if ctx is not None else "stacked"
            out.append(_callout_html(spec, "\n".join(body), layout))
            continue
        hm = re.match(r"^#{4,}\s+(.+?)\s*$", line)
        if hm:
            # The grammar defines exactly two heading levels; any deeper
            # heading renders at the same Display size, with no third size.
            out.append("<h2>%s</h2>" % _inline(hm.group(1)))
            i += 1
            continue
        if re.match(r"^-\s+", line):
            items = []
            panels_before = len(ctx["panels"]) if ctx is not None else 0
            while i < len(lines) and re.match(r"^-\s+", lines[i]):
                raw_item = re.sub(r"^-\s+", "", lines[i])
                if ctx is not None:
                    ctx["first_use_now"].clear()
                    raw_item, g_tokens = _gloss_placeholders(raw_item, ctx)
                else:
                    g_tokens = []
                rendered = _inline(raw_item)
                for gidx, tok in enumerate(g_tokens):
                    rendered = rendered.replace("\x00G%d\x00" % gidx, tok)
                items.append("<li>%s</li>" % rendered)
                i += 1
            out.append("<ul>%s</ul>" % "".join(items))
            if ctx is not None:
                out.extend(panel for _slug, panel in ctx["panels"][panels_before:])
                ctx["panels_len"] = len(ctx["panels"])
            continue
        if re.match(r"^\d+\.\s+", line):
            items = []
            panels_before = len(ctx["panels"]) if ctx is not None else 0
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                raw_item = re.sub(r"^\d+\.\s+", "", lines[i])
                if ctx is not None:
                    ctx["first_use_now"].clear()
                    raw_item, g_tokens = _gloss_placeholders(raw_item, ctx)
                else:
                    g_tokens = []
                rendered = _inline(raw_item)
                for gidx, tok in enumerate(g_tokens):
                    rendered = rendered.replace("\x00G%d\x00" % gidx, tok)
                items.append("<li>%s</li>" % rendered)
                i += 1
            out.append("<ol>%s</ol>" % "".join(items))
            if ctx is not None:
                out.extend(panel for _slug, panel in ctx["panels"][panels_before:])
                ctx["panels_len"] = len(ctx["panels"])
            continue
        if "|" in line:
            j = i
            rows = []
            while j < len(lines) and "|" in lines[j]:
                rows.append(lines[j])
                j += 1
            table = _table_html(rows, ctx)
            if table is not None:
                out.append(table)
                i = j
                continue
        buf = [line]
        i += 1
        while i < len(lines) and lines[i].strip():
            nxt = lines[i]
            if (re.match(r"^#{4,}\s", nxt) or re.match(r"^-\s+", nxt)
                    or re.match(r"^\d+\.\s+", nxt) or _TOKEN_RE.match(nxt)
                    or "|" in nxt
                    or _callout_kind_of(nxt) is not None):
                break
            buf.append(nxt)
            i += 1
        if ctx is not None:
            ctx["first_use_now"].clear()
            raw, g_tokens = _gloss_placeholders("\n".join(buf), ctx)
        else:
            raw, g_tokens = "\n".join(buf), []
        ids = ""
        if ctx is not None and ctx["first_use_now"]:
            ids = "".join(' id="use-%s"' % s
                          for s in sorted(ctx["first_use_now"]))
        para = "<p%s>%s</p>" % (ids, _inline(raw))
        for gidx, tok in enumerate(g_tokens):
            para = para.replace("\x00G%d\x00" % gidx, tok)
        out.append(para)
        if ctx is not None:
            out.extend(panel for _slug, panel in ctx["panels"][ctx["panels_len"]:])
            ctx["panels_len"] = len(ctx["panels"])
    return "\n".join(out)


def render_markdown(text, ctx=None):
    """A deliberately small stdlib block renderer for lesson prose, covering
    exactly D-08's declared scope: headings, paragraphs, lists, tables,
    inline code, fenced code, bold/italic and links -- nothing else, and no
    attempt at CommonMark completeness. Every literal text run goes through
    `html.escape` after block structure is resolved and before interpolation,
    matching the discipline `quiz_page.py` and `daemon.py` already apply to
    bank content -- a stray angle bracket in lesson prose must not break the
    page. Fenced blocks are extracted to placeholders before the inline pass
    so code content is never re-scanned.
    """
    out = []
    for block in re.split(r"(?m)(?=^###\s)", text):
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        m = re.match(r"^###\s+(.+?)\s*$", lines[0])
        if m:
            heading = m.group(1).strip()
            if ctx is not None:
                ctx["section"] = lesson_slug(heading)
                ctx["section_title"] = heading
            prose = _render_blocks("\n".join(lines[1:]), ctx)
            out.append('<section id="%s"><h2>%s</h2>%s</section>'
                       % (lesson_slug(heading), html.escape(heading), prose))
        else:
            out.append(_render_blocks(block, ctx))
    return "\n".join(out)


def backlinks(qs, slug):
    """Every question whose stored slug equals `slug`, in bank order.

    Returns the data the row needs -- the question dicts themselves -- not
    HTML; the renderer owns the row markup.
    """
    return [q for q in qs if q.get("lesson_slug") == slug]


def _reader_context(bank_path, qs):
    """The per-page reader settings and gloss map (03.1-UI-SPEC §14): read
    from the bank-adjacent itembank.json through the one settings loader,
    with the locked defaults. The gloss map holds only terms that pass the
    runtime glossable() gate; suppressed terms are tracked for the generic
    held line (§8.4)."""
    cfg = settings.load_settings(
        os.path.dirname(os.path.abspath(bank_path)) or ".")
    reader = cfg.get("reader") or {}
    ctx = {
        "gloss": {},
        "marks": reader.get("gloss_marks", "all"),
        "print_inline": reader.get("print_gloss", "appendix") == "inline",
        "example_layout": reader.get("example_layout", "stacked"),
        "reader_nav": reader.get("reader_nav", "none"),
        "section": "intro",
        "section_title": "",
        "used": set(),
        "panels": [],
        "panels_len": 0,
        "panels_emitted": set(),
        "first_uses": {},
        "first_use_now": set(),
        "held_line": "",
        "suppressed": False,
    }
    terms = parse_terms(bank_path)
    if terms is not None:
        ok = {slug: glossable(qs, rec)
              for slug, rec in terms["terms"].items()}
        ctx["gloss"] = {slug: rec for slug, rec in terms["terms"].items()
                        if ok.get(slug)}
        ctx["suppressed"] = not all(ok.values())
        if ctx["suppressed"] and ctx["gloss"]:
            ctx["held_line"] = '<p class="held">%s</p>' % html.escape(HELD_COPY)
    return ctx


def _backlinks_html(stem, qs, slug):
    refs = backlinks(qs, slug)
    if not refs:
        return '<div class="bl orphan">%s</div>' % html.escape(ORPHAN_COPY)
    rows = "".join(
        '<a href="/quiz/%s#%s">Q%d: %s</a>' %
        (stem, q["id"], q["number"], html.escape(_truncate(q["stem"], 100)))
        for q in refs)
    return '<div class="bl"><span class="blabel">%s</span>%s</div>' % (
        html.escape(BACKLINKS_LABEL), rows)


def lesson_page(bank_path, qs, lesson, ref=None, runtime=False, drill=False,
                style_override=None, profile=None):
    """The one render both surfaces call: the daemon route and `cmd_lesson`
    write the same document because there is only one `lesson_page`.

    A non-empty `ref` narrows the document to the single heading whose slug
    matches the caller's text (D-11): the heading is resolved through
    `model.lesson_slug()` -- the same value the item tag and the HTML anchor
    use -- never by raw string comparison, so a caller may type the heading
    with different casing, spacing or punctuation and still reach it. The
    filtered page keeps the full page's chrome, title and byline; only the
    body sections differ. When `ref` names no heading -- including on a bank
    with no lesson section at all -- the function returns None and leaves
    the hard stop to `cmd_lesson`, so the route, the CLI and a test can call
    it without inheriting a process-exit path (T-3-12).

    `runtime` marks a daemon-served page: only then does a [!KEY] card carry
    its Add-to-review form; a static render shows the exact unavailable copy
    instead (C9). `drill` is the `?print=drill` second-stylesheet pass:
    cloze markers blank server-side and an Answers list prints at the end
    (03.1-UI-SPEC §10.2).

    A bank with no lesson section, or one whose section holds zero headings,
    renders the shared `No lesson yet` empty state -- never a crash and never
    an empty card under a title. A lesson result carrying a non-empty error
    key (an unreadable or out-of-tree `[LESSON-SRC:]`) renders that same
    empty-state layout plus one `var(--warn)` note naming the offending
    source path in a wrapping code element: the degraded state, in the
    warning tone rather than the error tone, and never an exception
    (T-3-04). The only interpolated value in that note is the
    bank-author-written directive path, HTML-escaped like every other text
    run (T-3-07); the reason detail stays with `itembank lint`, because the
    reader is not a diagnostic surface.

    `style_override` is render_style's seam: the page renders under that
    style id whether or not the bank declares it, so the permuted output is
    honest about which style produced it (D-11).

    `profile` is the 09-04 presentation seam: a subject-profile snapshot
    (the same shape `subjects.select_profile`/`session_profile` return). Its
    `lesson.math` flag alone switches on the local KaTeX enhancement; every
    other profile renders the pre-09-04 reader byte-for-byte.
    """
    bank_text = open(bank_path, encoding="utf-8").read()
    title = (grab(r"(?m)^#\s+(.*?)\s*$", bank_text)
             or os.path.basename(bank_path))
    warn_css = ""
    nav_html = ""
    anchor_css = ""
    print_css = ""
    gloss_script = ""
    want = lesson_slug(ref) if ref else ""
    if lesson is None or not lesson.get("headings"):
        # An explicit --ref in a bank with no headings is the same miss as a
        # ref that matches nothing: the caller asked for a section that is
        # not there, and an empty-state page would silently lie about it.
        if want:
            return None
        body = '<div class="empty"><h2>%s</h2><p>%s</p></div>' % (
            html.escape(EMPTY_HEADING), html.escape(EMPTY_BODY))
        if lesson is not None and lesson.get("error"):
            src = grab(r"(?m)^\[LESSON-SRC:\s*(.*?)\s*\]", bank_text)
            warn_css = WARN_CSS
            body += ('<p class="warn">%s <code>%s</code></p>' % (
                html.escape(WARN_SENTENCE % os.path.basename(bank_path)),
                html.escape(src)))
    else:
        stem = os.path.splitext(os.path.basename(bank_path))[0]
        if want:
            head_idx = next((i for i, h in enumerate(lesson["headings"])
                             if h["slug"] == want), None)
            if head_idx is None:
                return None
            idxs = (head_idx,)
        else:
            idxs = range(len(lesson["headings"]))
        # One section per heading, rendered from the heading's own text and
        # body -- the exact block `render_markdown` isolates when it renders
        # the whole lesson, so a filtered page is byte-for-byte the full
        # page narrowed. Each heading's backlinks sit directly under its own
        # prose (the Copywriting Contract), which a re-split of the whole
        # render's `</section>` boundaries cannot guarantee once a `--ref`
        # scope drops other headings.
        ctx = _reader_context(bank_path, qs)
        ctx["runtime"] = runtime
        ctx["drill"] = drill
        ctx["key_answers"] = []
        parts = []
        for idx in idxs:
            h = lesson["headings"][idx]
            ctx["section"] = h["slug"] or ("section-%d" % idx)
            parts.append(render_markdown(
                "### %s\n\n%s" % (h["text"], h["body"]), ctx)
                + _backlinks_html(stem, qs, h["slug"]))
        body = "\n".join(parts)
        if ctx["gloss"]:
            body += ctx["held_line"] + _glossary_html(
                ctx["gloss"], ctx["first_uses"])
            anchor_css = _gloss_anchor_css(ctx["panels_emitted"])
            print_css = _gloss_print_css(
                "inline" if ctx["print_inline"] else "appendix")
            gloss_script = GLOSS_ENHANCEMENT_JS
            if ctx["reader_nav"] == "column":
                nav_html = _reader_nav_html(lesson["headings"])
        if drill and ctx.get("key_answers"):
            answers = "".join(
                "<li>%s</li>" % _inline(text)
                for _kid, text in ctx["key_answers"])
            body += ('<section id="answers"><h2>%s</h2><ol>%s</ol></section>'
                     % (html.escape(ANSWERS_HEADING), answers))
    # The style footer and its degraded copy (03.1-UI-SPEC 9.6): one
    # Ledger-voice line names the style that produced the page. A resolved
    # named style reads `style: <id> · rendered by render_style`; the house
    # fallback reads `style: house`; a missing/unreadable style file keeps
    # the house footer and adds the warn note echoing the author-written
    # id, leaving the reason to `itembank lint` (T-031-15).
    style_warn_html = ""
    style_foot = HOUSE_FOOT
    bank_dir = os.path.dirname(os.path.abspath(bank_path)) or "."
    if style_override:
        st = load_style(style_override, bank_dir)
        if st is None or st.get("error"):
            warn_css = WARN_CSS
            style_warn_html = '<p class="warn">%s</p>' % html.escape(
                STYLE_DEGRADED_COPY
                % (style_override, os.path.basename(bank_path)))
        else:
            style_foot = STYLE_FOOT % lesson_slug(style_override)
    else:
        resolved = resolve_style(
            qs, bank_path, settings.load_settings(bank_dir))
        if resolved.get("id") != "house":
            st = resolved.get("style")
            if st is None or st.get("error"):
                warn_css = WARN_CSS
                style_warn_html = '<p class="warn">%s</p>' % html.escape(
                    STYLE_DEGRADED_COPY
                    % (resolved["id"], os.path.basename(bank_path)))
            else:
                style_foot = STYLE_FOOT % lesson_slug(resolved["id"])
    # 09-04 Math: the presentation seam reads the profile snapshot the
    # caller resolved (the daemon route resolves the bank's subject profile
    # exactly as a session would; cmd_lesson passes none, so a static render
    # stays source-only -- enhancement is a served-page capability). Only a
    # profile whose lesson.math flag is true loads the local assets and the
    # adapter; EMT/plain profiles emit empty slots and byte-identical pages
    # (D-08).
    math_assets = ""
    math_script = ""
    if profile and (profile.get("profile") or {}).get("lesson", {}).get("math"):
        math_assets = MATH_ASSETS_HTML
        math_script = MATH_ADAPTER_JS
    return (LESSON_TEMPLATE
            .replace("__THEME__", THEME_CSS)
            .replace("__SHARED_CSS__", SHARED_CSS)
            .replace("__LESSON_CSS__", LESSON_CSS)
            .replace("__WARN_CSS__", warn_css)
            .replace("__GLOSS_ANCHOR_CSS__", anchor_css)
            .replace("__GLOSS_PRINT_CSS__", print_css)
            .replace("__READER_NAV__", nav_html)
            .replace("__GLOSS_SCRIPT__", gloss_script)
            .replace("__MATH_ASSETS__", math_assets)
            .replace("__MATH_SCRIPT__", math_script)
            .replace("__STYLE_WARN__", style_warn_html)
            .replace("__STYLE_FOOT__", style_foot)
            .replace("__TITLE__", html.escape(title) + " lesson")
            .replace("__SUB__", SUB_BYLINE)
            .replace("__BODY__", body))


def _rule_param_kind(param):
    """Map one order.before rule param to the block kind it names:
    `[!EXAMPLE]` -> EXAMPLE, `[!CHECK]` -> CHECK, `paragraph` -> paragraph.
    A param the classifier cannot name is dropped -- render_style never
    guesses at a block kind it cannot identify (D-11)."""
    p = param.strip()
    if p.startswith("[!") and p.endswith("]"):
        return p[2:-1].split(":")[0].strip().upper()
    return p.lower()


def _style_block_kind(block):
    """Classify one section block for render_style's order.before rules,
    mirroring the block boundaries _render_blocks() actually consumes:
    callout kinds from `> [!KIND]`, fenced code, deeper headings, lists,
    tables, or paragraph."""
    text = block.lstrip()
    cm = _CALLOUT_MARK_RE.match(text)
    if cm:
        return cm.group(1).split(":")[0].strip().upper()
    if text.startswith("```"):
        return "code"
    if re.match(r"^#{4,}\s", text):
        return "heading"
    if re.match(r"^(\s*[-*]\s|\s*\d+\.\s)", text):
        return "list"
    lines = text.splitlines()
    if len(lines) >= 2 and "|" in lines[0] and _is_separator_row(lines[1]):
        return "table"
    return "paragraph"


def _split_section_blocks(body):
    """Split one section body into the logical blocks _render_blocks() would
    consume, so a permutation moves blocks rather than fragments: fenced
    code protected first, then blank-line boundaries, with `>` callout runs
    and pipe-table runs kept whole (D-11)."""
    protected, tokens = _protect_code(body)
    lines = protected.split("\n")
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        start = i
        if line.startswith(">"):
            while i < len(lines) and lines[i].startswith(">"):
                i += 1
            blocks.append("\n".join(lines[start:i]))
            continue
        tm = _TOKEN_RE.match(line)
        if tm:
            blocks.append(tokens[int(tm.group(1))])
            i += 1
            continue
        if "|" in line:
            j = i
            while j < len(lines) and "|" in lines[j]:
                j += 1
            blocks.append("\n".join(lines[i:j]))
            i = j
            continue
        buf = [line]
        i += 1
        while i < len(lines) and lines[i].strip():
            nxt = lines[i]
            if (nxt.startswith(">") or "|" in nxt or _TOKEN_RE.match(nxt)
                    or re.match(r"^#{4,}\s", nxt)
                    or re.match(r"^-\s+", nxt)
                    or re.match(r"^\d+\.\s", nxt)):
                break
            buf.append(nxt)
            i += 1
        blocks.append("\n".join(buf))
    return blocks


def _permute_section_blocks(body, rules):
    """Permute the blocks of one section per the target style's order.before
    rows: within a section, every A precedes every B. The fix is a stable
    partition -- every A block moves, in its original order, to just before
    the first B; nothing is created, deleted, or rewritten, and a rule whose
    kinds the classifier cannot identify is simply not applied (D-11)."""
    order_rules = []
    for row in rules or []:
        if row.get("kind") != "order.before":
            continue
        params = [p for p in (row.get("params") or "").split(",")
                  if p.strip()]
        if len(params) != 2:
            continue
        a, b = _rule_param_kind(params[0]), _rule_param_kind(params[1])
        if a and b:
            order_rules.append((a, b))
    if not order_rules:
        return body
    blocks = _split_section_blocks(body)
    if len(blocks) < 2:
        return body
    guard = 0
    changed = True
    while changed and guard <= len(blocks):
        changed = False
        guard += 1
        kinds = [_style_block_kind(b) for b in blocks]
        for a, b in order_rules:
            first_b = next((i for i, k in enumerate(kinds) if k == b), None)
            if first_b is None:
                continue
            last_a = next((i for i in range(len(kinds) - 1, -1, -1)
                           if kinds[i] == a), None)
            if last_a is not None and last_a > first_b:
                prefix = [x for i, x in enumerate(blocks)
                          if i < first_b and kinds[i] != a]
                moved = [x for i, x in enumerate(blocks)
                         if kinds[i] == a]
                suffix = [x for i, x in enumerate(blocks)
                          if i >= first_b and kinds[i] != a]
                blocks = prefix + moved + suffix
                kinds = [_style_block_kind(b) for b in blocks]
                changed = True
    return "\n\n".join(blocks)


def _render_style_refusal(source_id, target_id):
    """The five named mechanically impossible transforms (D-11, ROADMAP 3b),
    refused by name and never approximated: expository->case-narrative,
    expository->Socratic, expository->worked-example, anything->Bottom-Up
    (artifact-first), and case-narrative->anything. `house` reads as the
    expository base -- the house rules are expository's rules (R1.4)."""
    s = source_id or "house"
    if s in ("expository", "house"):
        if target_id in ("case-narrative", "socratic", "worked-example"):
            return RENDER_REFUSAL_COPY % (s, target_id)
    if target_id == "artifact-first":
        return RENDER_REFUSAL_COPY % (s, target_id)
    if s == "case-narrative" and target_id != "case-narrative":
        return RENDER_REFUSAL_COPY % (s, target_id)
    return None


def render_style(bank_path, style_id, out=None):
    """The runtime, model-free style transform (D-11): permutes only blocks
    a lesson already contains, per the target style's order.before rows,
    and renders the permuted lesson through lesson_page with the footer
    naming the target style. One of the five named impossible transforms is
    refused by name: the refusal copy is returned and no file is written.
    Returns the written output path, or the refusal copy when refused."""
    qs = load(bank_path)
    lesson_data = parse_lesson(bank_path)
    bank_dir = os.path.dirname(os.path.abspath(bank_path)) or "."
    source = resolve_style(qs, bank_path, settings.load_settings(bank_dir))
    slug = lesson_slug(style_id)
    refusal = _render_style_refusal(source.get("id"), slug)
    if refusal:
        return refusal
    target = load_style(slug, bank_dir)
    permuted = lesson_data
    if (lesson_data and lesson_data.get("headings")
            and target is not None and not target.get("error")):
        headings = [dict(h, body=_permute_section_blocks(h["body"],
                                                         target["rules"]))
                    for h in lesson_data["headings"]]
        permuted = dict(lesson_data, headings=headings)
    page = lesson_page(bank_path, qs, permuted, style_override=style_id)
    out = out or (os.path.splitext(bank_path)[0]
                  + "_%s.html" % slug)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write(page)
    return out


def cmd_lesson(a):
    """The lesson CLI's observable contract: render the same document the
    daemon route serves, write it to `--out` (or beside the bank, like
    `cmd_study`), and report on stdout exactly how many sections were
    actually rendered -- one status line, never the document and never a
    progress line. The one hard stop is an explicitly requested `--ref`
    heading that does not exist (T-3-12); a bank with no lesson section, or
    with an unreadable external source, writes its page and exits 0.
    """
    qs = load(a.bank)
    lesson = parse_lesson(a.bank)
    out = a.out or os.path.splitext(a.bank)[0] + "_lesson.html"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    page = lesson_page(a.bank, qs, lesson, ref=a.ref)
    if page is None:
        sys.exit("no lesson heading matching %r in %s" % (a.ref, a.bank))
    open(out, "w", encoding="utf-8").write(page)
    if a.ref:
        count = 1
    elif lesson and lesson.get("headings"):
        count = len(lesson["headings"])
    else:
        count = 0
    print("%d lesson section(s) -> %s" % (count, out))
    return 0


def cmd_render_style(a):
    """The render_style CLI twin (03.1-UI-SPEC 9.6): render the bank's
    lesson permuted into the requested style and write the page; one of the
    five named impossible transforms prints the exact refusal copy, writes
    nothing, and exits 1 (D-11)."""
    result = render_style(a.bank, a.style, out=a.out)
    if result.startswith(RENDER_REFUSAL_COPY.split("%s")[0]):
        print(result)
        return 1
    print("rendered %s in style %s -> %s" % (a.bank, a.style, result))
    return 0


def gloss_lookup(bank_path, term):
    """Resolve one gloss request the way both the /gloss route and the CLI
    twin must (SURF-04): returns ("ok", record) for a glossable term,
    ("unknown", None) for a slug with no `## TERMS` entry, and ("held",
    None) for a term the runtime gate suppresses. One resolution, two
    callers, so a route and a command can never disagree."""
    qs = load(bank_path)
    terms = parse_terms(bank_path)
    if terms is None:
        return "unknown", None
    record = terms["terms"].get(lesson_slug(term))
    if record is None:
        return "unknown", None
    if not glossable(qs, record):
        return "held", None
    return "ok", record


def gloss_page(stem, record, slug):
    """The served gloss page for the navigation path (03.1-UI-SPEC §8.3
    degraded): the definition plus a real `Back to the question` link whose
    href is the lesson anchor -- never a dead control, never a spinner."""
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            "<title>%s</title></head><body>"
            "<p>%s</p><p>%s</p>"
            '<p><a href="/lesson/%s#term-%s">%s</a></p>'
            "</body></html>"
            % (html.escape(record["canonical"]),
               html.escape(record["canonical"]),
               _inline(record["def"]),
               html.escape(stem), slug,
               html.escape(BACK_TO_QUESTION_COPY)))


def cmd_gloss(a):
    """The CLI twin of `GET /gloss/<stem>/<slug>`: prints the definition of
    one glossable term, and exits non-zero for an unknown or suppressed
    term -- the same resolution `gloss_lookup()` gives the route."""
    status, record = gloss_lookup(a.bank, a.term)
    if status == "unknown":
        sys.exit("no term matching %r in %s" % (a.term, a.bank))
    if status == "held":
        sys.exit("the definition for %r is held until the item is answered"
                 % a.term)
    print(record["def"])
    return 0


def record_key_review(bank_path, key_id, mode="practice", session_id="reader"):
    """The one key_review recording path shared by the daemon route and the
    CLI twin (SURF-04): resolves the key id against the bank's parsed key
    blocks, appends the event through the one evidence writer, and returns
    the status string -- or None when the id names no block, so both
    callers can 404/exit identically (T-031-11)."""
    keys = parse_key_blocks(bank_path)
    if not any(k.get("id") == key_id for k in keys):
        return None
    bank_dir = os.path.dirname(os.path.abspath(bank_path)) or "."
    event = evidence.key_review_event(
        session_id=session_id, bank=os.path.basename(bank_path),
        key_id=key_id, mode=mode)
    evidence.append_event(evidence.log_path(bank_dir), event)
    return "Added to review."


def cmd_key_review(a):
    """The CLI twin of `POST /key/<id>/review`: records a key_review event
    for a real [!KEY] block and prints the status string; an unknown id
    exits non-zero, matching the route's 404."""
    status = record_key_review(a.bank, a.key_id)
    if status is None:
        sys.exit("no [!KEY] block with id %r in %s" % (a.key_id, a.bank))
    print(status)
    return 0
