"""The lesson reader: a bank's teaching text rendered as a document, linked
both ways to the items that test it.

This is a read-only render of author-provided prose. It holds no answer key
and reaches no verdict, and its links navigate rather than answer (D-10): the
only way out of a lesson is to another surface, never to a score.
"""
import resources
import html, json, os, re, sys
from urllib.parse import parse_qs, quote, urlsplit, urlunsplit

import capabilities
from markdown_blocks import (FENCE_RE, CALLOUT_MARK_RE, callout_spec,
                             callout_required_of, callout_kind_of, callout_entered,
                             split_cells, is_separator_row, protect_fenced_code)
from model import parse_lesson_comparison, parse_lesson_lineplot
from surfaces import lesson_interaction, lesson_progressive
import evidence
import retention
import subjects
from model import (CHECK_UNRESOLVED_COPY, grab, lesson_slug, lesson_steps,
                   load, load_style,
                   parse_activities, parse_key_blocks, parse_lesson,
                   parse_media, parse_terms, resolve_style)
from runtime import glossable
from surfaces.presentation import (SHARED_CSS, PRODUCT_CSS,
                                   product_theme_css, standalone_product_nav)


def product_reader_css():
    return product_theme_css() + PRODUCT_CSS + """
.wrap{max-width:1200px;background:var(--paper);color:var(--product-ink);
  padding-block:var(--space-5) var(--space-7)}
.wrap>header,.wrap>.reader-nav,.wrap>.lesson-context,.wrap>.lesson-context-nav{
  max-width:var(--measure-prose);margin-inline:auto}
.wrap>header{padding-bottom:var(--space-2);margin-bottom:var(--space-2);
  border-bottom:1px solid var(--line)}
.wrap>header h1{font-family:var(--font-paper);font-weight:600;
  font-size:var(--text-title);font-weight:600;letter-spacing:-.025em;line-height:1.15;
  text-wrap:balance}
.wrap .sub{font-family:var(--font-chrome);font-size:var(--text-xs);line-height:1.6}
.wrap .reader-nav summary{min-height:44px;display:flex;align-items:center;gap:var(--space-2);
  font-family:var(--font-chrome);letter-spacing:normal;text-transform:none}
.wrap .reader-nav summary:before{content:'+';font-size:var(--text-body)}
.wrap .reader-nav details[open]>summary:before{content:'−'}
#lesson-content>section>h2{font-family:var(--font-paper);font-size:var(--text-heading);
  font-weight:400;line-height:1.3;letter-spacing:-.015em}
#lesson-content.card{background:transparent;border:0;border-radius:0;padding:0}
.overhaul-lesson #lesson-content{max-width:var(--measure-prose);margin-inline:auto}
.overhaul-lesson #lesson-content:has(.runnable,.lesson-comparison,.lesson-lineplot,pre,table,svg){max-width:100%}
.overhaul-lesson:has(.runnable,.lesson-comparison,.lesson-lineplot,pre,table,svg)>:is(header,.reader-nav,.lesson-context,.lesson-context-nav){margin-inline:0}
.overhaul-lesson #lesson-content :is(p,ul,ol,blockquote){max-width:var(--measure-prose)}
.overhaul-lesson #lesson-content>section{padding-block:var(--space-4);border-block-end:1px solid var(--line)}
.overhaul-lesson #lesson-content>section:last-child{border-block-end:0}
.overhaul-lesson #lesson-content :is(pre,.runnable,figure){min-width:0;max-width:100%}
.overhaul-lesson #lesson-content pre{overflow-x:auto}
#lesson-content figure.media{margin-inline:0;min-width:0}
#lesson-content .media img{display:block;max-width:100%;height:auto}
#lesson-content .media-description summary{min-height:44px;display:list-item;box-sizing:border-box;padding-block:var(--space-2);cursor:pointer}
#lesson-content .media-description p{overflow-wrap:anywhere}
.overhaul-lesson .reader-nav{margin-block:var(--space-3)}

.wrap>.lesson-context-nav{font-family:var(--font-chrome);padding-block:var(--space-2)}
.wrap[data-reading-mode="guided"]>header{padding-bottom:var(--space-2);margin-bottom:var(--space-2)}
.wrap[data-reading-mode="guided"]>header h1{font-family:var(--font-paper);
  font-size:var(--text-body);line-height:1.4;margin-bottom:var(--space-1)}
.wrap[data-reading-mode="guided"] .lesson-reading-about summary{cursor:pointer;
  font-family:var(--font-chrome);font-size:var(--text-xs);min-height:44px;
  display:flex;align-items:center;color:var(--mut)}
.wrap .lesson-reading-about summary{cursor:pointer;font-family:var(--font-chrome);
  font-size:var(--text-xs);min-height:44px;display:flex;align-items:center;color:var(--mut)}
.wrap[data-reading-mode="continuous"]>header h1{font-size:var(--text-heading);
  margin-bottom:0;line-height:1.3}
.wrap[data-reading-mode="continuous"] #lesson-content>section:first-child{padding-top:var(--space-2)}
.wrap[data-reading-mode="continuous"] #lesson-content>section:first-child>h2{margin-top:var(--space-2)}
.section-practice{font-family:var(--font-chrome);margin-block:var(--space-3)}
.section-practice summary{cursor:pointer;min-height:44px;display:flex;align-items:center;
  font-size:var(--text-body);color:var(--mut)}
.section-practice .practice-item{margin-block:var(--space-3)}
.section-practice .practice-preview{font-size:var(--text-body)}
#lesson-content .practice-preview p{font-size:var(--text-body);margin-block:var(--space-2)}
.section-practice a{min-height:44px;display:flex;align-items:center}
.wrap[data-reading-mode="guided"] #lesson-content>section:first-child{padding-top:var(--space-2)}
.wrap[data-reading-mode="guided"] #lesson-content>section:first-child>h2{margin-top:var(--space-2)}
#lesson-content .callout{border-radius:var(--r-1);box-shadow:none;background:transparent;
  padding:var(--space-4);margin-block:var(--space-4)}
#lesson-content :is(.callout-tip,.callout-note){border:0;border-inline-start:2px solid var(--line);
  padding-block:var(--space-2)}
#lesson-content .callout-excerpt{border:0;border-inline-start:3px solid var(--source-mark);
  padding-block:var(--space-2);background:var(--source-bg)}
#lesson-content .callout-excerpt .callout-label{color:var(--source-mark)}
#lesson-content .callout-note{border-inline-start:3px solid var(--note-mark);
  background:var(--note-bg)}
#lesson-content .callout-note .callout-label{color:var(--note-mark)}
#lesson-content .callout-example{background:var(--card);border:1px solid var(--line);
  border-inline-start:3px solid var(--edge)}
#lesson-content .callout-example .callout-label{color:var(--ink)}
#lesson-content pre{border:1px solid var(--line);border-radius:var(--r-1);
  background:var(--card);padding:var(--space-3)}
.wrap .run-source-label,.wrap .run-output-label{font-family:var(--font-chrome);
  letter-spacing:.02em}
#lesson-content :is(.lesson-comparison,.lesson-lineplot){padding:var(--space-3);
  border-block-start:1px solid var(--edge);background:var(--card)}
#lesson-content :is(.comparison-controls,.lineplot-controls){font-family:var(--font-chrome)}
#lesson-content .callout-label{font-family:var(--font-chrome);font-size:var(--text-xs);
  letter-spacing:.04em;font-weight:600}
@media(max-width:767px){.wrap{padding:var(--space-4) var(--space-3) 96px}}
"""
from surfaces import settings
from surfaces.theme import THEME_CSS


SUB_BYLINE = ("Read the material, then open practice or return to your saved sitting in this tab. "
              "Reading alone records no answers.")

EMPTY_HEADING = "No lesson yet"
EMPTY_BODY = ("This bank has no ## LESSON section. Add one above the first "
              "Qn. line \u2014 see itembank spec for the LESSON/LESSON-REF grammar.")
WARN_SENTENCE = ("The external lesson file for this bank could not be read. "
                 "Run itembank lint %s for details.")
ORPHAN_COPY = "No items reference this section yet."
BACKLINKS_LABEL = "Section practice"
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

# The Phase 6.2 gate copy (06.2-UI-SPEC section 15, verbatim -- the linter,
# the renderer, and the tests reproduce the same strings). Inherited rows
# (the inert slot, the D1 print label, the held-definitions and gloss lines)
# are 3.1's and are reproduced by reference above/unchanged.
CHECK_ANSWER_COPY = "Check answer"
GATE_HEADER_REQUIRED = "Check \u00b7 required to continue"
GATE_HEADER_RECOMMENDED = "Check \u00b7 recommended"
SKIP_COPY = "Read ahead without answering"
MODE_DEGRADE_COPY = ("This sitting holds feedback until it ends, so checks "
                     "do not gate reading here.")
BOUNDARY_MANY = "{n} more sections below this check."
BOUNDARY_ONE = "1 more section below this check."
SKIP_RECORDED_COPY = "Read ahead recorded. This check stays open."
SKIP_AFTER_ATTEMPT_COPY = ("Read ahead becomes available after one attempt.")
REVEAL_CLAUSE_COPY = "The next section is below."
TOC_FILTERED_COPY = "More sections appear as you clear each check."
RUNTIME_UNREACHABLE_COPY = ("This check cannot be submitted while the runtime "
                            "is unreachable. Run itembank daemon and reload.")
CLEARED_IN_SITTING_COPY = "Cleared in this sitting."
READ_AHEAD_IN_SITTING_COPY = "Read ahead in this sitting."
VERDICT_CORRECT_COPY = "Correct"
VERDICT_NOT_CORRECT_COPY = "Not correct"
GATE_DENOMINATOR_COPY = "Of {n} required gates encountered"
GATE_EXCLUSION_COPY = ("Recommended gates are not counted \u2014 reading "
                       "past one is not a recorded choice.")

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
WARN_CSS = """.warn{color:var(--warn);font-size:16px;margin:14px auto 0;max-width:520px;
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
#
# THREE THINGS PLAN 14-02 SETTLED, recorded here rather than in the emitted
# CSS (every CSS comment below ships in every served page):
#
# 1. `.wrap` adds the side gutter OUTSIDE the measure. `*{box-sizing:
#    border-box}` is global in SHARED_CSS, so `max-width:var(--measure-prose)`
#    with padding inside it meant the token was never the content measure --
#    the column was two gutters narrower than the number claimed. With the
#    retuned 59ch this is a 563px box holding a 531px, 66-character column.
#    Tables, code, [!EXAMPLE] grids and math displays keep their existing
#    escape to --measure-wide.
# 2. The prose rhythm is scoped to `#lesson-content`, the container that
#    already exists and is already the enhancement hook for math and for
#    runnable code. The 24px paragraph gap is 0.81 of the reader's real
#    29.7px line box (the Paper face's glyph box is 1.371 em at 18px); the
#    16px it replaced was 0.54 of a line, the standard "reads as one grey
#    slab" figure. The bare `p,li` rule keeps its shipped 16px because it
#    also styles callouts, the gate band, the nav and the glossary.
# 3. `font-size-adjust` changes the USED glyph size without changing the
#    computed font-size, so it introduces no sixth size and cannot break the
#    type-scale fixture; where unsupported it is ignored and the page renders
#    exactly as it did before. The Ledger face's x-height ratio is 0.516
#    against the Paper face's 0.475 -- the two families are named only by
#    surfaces/presentation.py, which is why they are described by voice here
#    and not by name -- so an inline Ledger or Code run at the inherited
#    18px renders 8.6% larger than the prose around it. `pre code` is reset
#    to `none` because its 16px is already the matched size (0.516 x 16 =
#    8.26px against Paper's 8.55px at 18px) and adjusting it would undo that.
LESSON_CSS = resources.read_text("surfaces/assets/lesson/lesson.css")


LESSON_TEMPLATE = r"""<!doctype html><html lang="__LANG__" dir="__DIR__"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title>
<style>
__THEME__
__SHARED_CSS__
__LESSON_CSS__
__WARN_CSS__
__GLOSS_ANCHOR_CSS__
__GLOSS_PRINT_CSS__
__RUNNABLE_CSS__
__PRODUCT_CSS__
</style>
__MATH_ASSETS__
</head><body><div class="wrap overhaul-lesson ib-profile ib-profile-__PRESENTATION_PROFILE__" data-presentation-profile="__PRESENTATION_PROFILE__" data-reading-mode="__READING_MODE__">__PRODUCT_NAV__
<header>
  __READER_APPLICATION__
  <h1>__TITLE__</h1>
  __READER_BYLINE__
</header>
__STATUS__
__CONTEXT_NAV__
__READER_NAV__
__GLOSS_SCRIPT__
<div class="card" id="lesson-content"__RUN_SESSION_ATTR__>__STYLE_WARN____BODY__</div>
__MATH_SCRIPT__
__RUNNABLE_JS__
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
MATH_ADAPTER_JS = resources.read_text("surfaces/assets/lesson/math-adapter.js") % {
    "unavailable": json.dumps(MATH_UNAVAILABLE_COPY),
    "parse_failure": json.dumps(MATH_PARSE_FAILURE_COPY),
}


# --- 09-05 runnable lesson code --------------------------------------------
# The locked page copy for lesson Run observations (09-UI-SPEC "State
# machines and exact copy"). These strings are the page-facing contract;
# the daemon returns bounded observations and machine reasons, and the page
# renders exactly these statuses. No assessment vocabulary ("correct",
# "passed", "score", "verdict") appears in any of them (D-11).
RUN_EXAMPLE_LABEL = "Example code"
RUN_SOURCE_LABEL = "Source code"
RUN_READY_COPY = "Run example"
RUN_RUNNING_COPY = "Running example\u2026"
RUN_COMPLETED_COPY = "Run finished (exit code {code})."
RUN_TIMEOUT_COPY = "Run stopped after the configured timeout."
RUN_TRUNCATED_COPY = "Output was truncated at the configured limit."
RUN_REQUEST_ERROR_COPY = ("Couldn\u2019t run this example. Your edits are "
                          "still here. Try again.")
RUN_LANG_UNAVAILABLE_COPY = ("Run unavailable: {language} is not enabled "
                             "for this lesson.")
RUN_STATIC_COPY = ("Run this example in the local app. The source remains "
                   "available here.")
RUN_LAN_REFUSAL_COPY = "Run unavailable from this network view."
RUN_NO_OUTPUT_COPY = "No output."
RUN_HELP_COPY = ("Tab inserts a tab, Shift-Tab dedents, Escape then Tab "
                 "leaves the editor.")
RUN_STDOUT_LABEL = "stdout"
RUN_STDERR_LABEL = "stderr"

# 09-05 runnable-code adapter (09-UI-SPEC "Runnable code example" / "CS
# runnable prose"). One delegated handler on `#lesson-content` owns every
# block: each block keeps its own source/status/output/request state, the
# Run POST carries exactly {session_id, block_id, language, source}, and the
# status region announces only the concise summary -- labelled stdout/stderr
# are never live regions. Tab/Shift-Tab edit inside the textarea; Escape
# arms the next Tab to leave the editor (the platform focus escape); the Run
# button follows the source in DOM/tab order and keeps native Enter/Space
# activation. Request errors are announced once with role="alert"; the
# source and previous output are never replaced by a failure.
#
# TYPE AND VOICE (plan 14-02, 14-UI-SPEC §4.2). Every size here was relative
# (`.9em`, `.85em`, `.8em`) or off-scale (13px, 14px), and both `font:`
# shorthands named a family literally, which .planning/UI-SPEC.md §7 forbids.
# Now: `.run-source` is 16px because it is an editable control, and 16px is
# also what stops iOS zooming on focus -- which is why the old
# `@media (max-width:320px){.run-source{font-size:13px}}` is DELETED rather
# than retuned: the floor has to hold exactly where a phone needs it.
# `.run-status` and `.run-unavailable` are 16px in Ledger voice because they
# are runtime assertions and the sentence a learner acts on after a failed
# run; without a size they inherited the surrounding 18px Paper prose and
# spoke in the author's voice. `.run-stdout`/`.run-stderr` stay small at 12px
# -- the ONE named exception in the contract: verbatim machine output, dense
# and arbitrarily long, in a bounded scrolling pane, whose recovery sentence
# lives in `.run-status` instead.
RUNNABLE_CSS = resources.read_text("surfaces/assets/lesson/runnable.css")
RUNNABLE_JS = resources.read_text("surfaces/assets/lesson/runnable.js") % {
    "copies": json.dumps({
        "ready": RUN_READY_COPY, "running": RUN_RUNNING_COPY,
        "completed": RUN_COMPLETED_COPY, "timed_out": RUN_TIMEOUT_COPY,
        "truncated": RUN_TRUNCATED_COPY, "request_error": RUN_REQUEST_ERROR_COPY,
    }, ensure_ascii=False),
    "no_output": json.dumps(RUN_NO_OUTPUT_COPY, ensure_ascii=False),
}


def _truncate(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit] + "\u2026"


_TOKEN_RE = re.compile(r"^\x00K(\d+)\x00$")
# A line that is ONLY a `[MEDIA: <id>]` directive (plan 16A-05). Anchored at
# both ends on purpose: a figure is a block-level thing, so a `[MEDIA:]`
# appearing inside a paragraph, a list item, a table cell, or a fence is left
# alone and renders as literal text. Inlining a figure would break the run it
# sits in, and no requirement asks for one.
_MEDIA_BLOCK_RE = re.compile(r"^\s*\[MEDIA:\s*([^\]]*?)\s*\]\s*$")

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
GLOSS_ENHANCEMENT_JS = resources.read_text("surfaces/assets/lesson/gloss-enhancement.js") % {"loading": json.dumps(LOADING_COPY),
                 "unavailable": json.dumps(UNAVAILABLE_COPY)}

CODE_CRAFT_JS = resources.read_text("surfaces/assets/lesson/code-craft.js")

GLOSS_HOVER_JS = resources.read_text("surfaces/assets/lesson/gloss-hover.js")


# The glossary rules are sliced out of the shipped LESSON_CSS rather than copied,
# so the 17A visual tracer and any later surface that shows a hover definition
# style it from the same bytes the reader uses. A copy would drift silently; a
# slice fails loudly the moment the markers move.
GLOSS_CSS_START = ".term{text-decoration:underline dotted"
GLOSS_CSS_END = ".gloss-back:hover,.gloss-back:focus-visible{text-decoration:underline}"


def gloss_css():
    """Just the term-trigger, popover-panel and glossary-appendix rules."""
    start = LESSON_CSS.find(GLOSS_CSS_START)
    end = LESSON_CSS.find(GLOSS_CSS_END)
    if start == -1 or end == -1:
        raise RuntimeError(
            "glossary CSS markers moved in LESSON_CSS; update GLOSS_CSS_START/END "
            "rather than copying the rules into a second stylesheet")
    return LESSON_CSS[start:end + len(GLOSS_CSS_END)]


def _gloss_trigger_html(ref_text, slug):
    """One Popover-API trigger (03.1-UI-SPEC §8.1 DOM LOCKED): a real
    `<button>` whose accessible name is the term text itself -- no
    aria-label, no title, so a definition can never ride the trigger's
    accessible name (C7)."""
    if not re.match(r"^[a-z0-9-]+$", slug or ""):
        return html.escape(ref_text)
    return ('<button type="button" class="term" popovertarget="gloss-%s" '
            'aria-details="gloss-%s">%s</button>'
            % (slug, slug, html.escape(ref_text)))


def _gloss_panel_html(record, slug, key_anchor=None):
    """One `[popover]` panel: the definition ships with the page, so the
    reader gloss works with the network unplugged and before any script
    loads (§8.1). The `Full entry` link is the Chrome-voice target of the
    glossary appendix."""
    key_link = ('<p class="gloss-key"><a href="#%s">Also a key point</a></p>'
                % html.escape(key_anchor)) if key_anchor else ""
    return ('<div id="gloss-%s" class="gloss" popover>'
            '<p class="gloss-term">%s</p>'
            '<p class="gloss-def">%s</p>'
            '%s<p class="gloss-more"><a href="#term-%s">%s</a></p>'
            '<div class="gloss-actions"><button type="button" class="go gloss-pin" '
            'aria-pressed="false" hidden>Pin</button>'
            '<button type="button" class="go gloss-close" popovertarget="gloss-%s" '
            'popovertargetaction="hide">Close</button></div></div>'
            % (slug, html.escape(record["canonical"]), _inline(record["def"]),
               key_link, slug, html.escape(FULL_ENTRY_COPY), slug))


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
        if not re.match(r"^[a-z0-9-]+$", slug or ""):
            continue
        rules.append(
            'button.term[popovertarget="gloss-%s"]{anchor-name:--anchor-%s}'
            '#gloss-%s{--gloss-anchor:--anchor-%s}'
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


def _reader_nav_html(headings, variant="column"):
    """The reader_nav column (03.1-UI-SPEC §7.3): a collapsed disclosure
    listing every heading by slug, Chrome-voice summary."""
    items = "".join(
        '<li><a href="#%s"><span class="nav-n">%d</span><span>%s</span></a></li>'
        % (h["slug"], n, html.escape(h["text"]))
        for n, h in enumerate(headings, 1))
    rail = " nav-rail" if variant in ("rail", "auto") else ""
    opened = " open" if variant == "rail" else ""
    return ('<nav class="reader-nav%s" aria-label="%s"><details%s>'
            '<summary>%s</summary><ul>%s</ul></details></nav>'
            % (rail, html.escape(SECTIONS_NAV_COPY), opened,
               html.escape(SECTIONS_NAV_COPY), items))


# The locked user-visible copy of the unsupported-block refusal (D-16A-3,
# CAP-01's Degraded clause). One string, one place: a learner who meets a
# block this reader cannot honor reads this sentence and then the author's own
# text. Do not rephrase it, do not add a variant, and do not localize it in
# Phase 16A.
UNSUPPORTED_SEMANTIC_COPY = ("This block needs a lesson feature this reader "
                             "does not have. Its text is below, unchanged.")


# The two locked media degraded-path strings (CAP-02, plan 16A-05). Both are
# user-visible copy and both are locked here: do not rephrase them, do not add
# a variant, and do not localize them in Phase 16A.
#
# Neither says "error". A missing asset and a remote asset are ordinary states
# of a lesson a learner can still read, and the sentence's job is to hand the
# reader straight to the description rather than to report a fault.
MEDIA_MISSING_COPY = ("This image is not available on this machine. Its "
                      "description is below.")
MEDIA_REMOTE_COPY = ("This image lives outside this course and is not loaded "
                     "here. Its description is below, and the link opens it.")


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
    marker = CALLOUT_MARK_RE.match(raw_lines[0])
    title = marker.group(2).strip() if marker else ""
    raw = "\n".join(raw_lines)
    kid = grab(r"(?m)^>\s*\[ID:\s*(\S+)\s*\]", raw)
    body = []
    for line in raw_lines[1:]:
        stripped = re.sub(r"^>\s?", "", line).strip()
        if not stripped or re.match(r"^\[(ID|HASH):", stripped):
            continue
        # The de-prefixed line, matching model.parse_key_blocks(): the raw
        # blockquote marker is transport, never body text, and appending the
        # raw line rendered a literal "> " inside every multi-line KEY card
        # (found by the 17B-03 learner pass; 17B-CONTEXT D-06 in-phase fix).
        body.append(re.sub(r"^>\s?", "", line))
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


def _gate_check_answer(q):
    """The check item's response controls as server-rendered HTML (no
    JavaScript): the same object the quiz surface shows, reduced to its
    public fields only -- stem and options, never the key, rationale,
    distractor analysis, or objective line (06.2-UI-SPEC section 5.4).
    """
    esc = html.escape
    out = ['<p class="gate-stem">%s</p>' % esc(q["stem"])]
    t = q["type"]
    if t in ("mc", "multi"):
        kind = "radio" if t == "mc" else "checkbox"
        for k in sorted(q.get("opts") or {}):
            out.append(
                '<label class="gate-opt"><input type="%s" name="option" '
                'value="%s"> <span>%s) %s</span></label>'
                % (kind, esc(k), esc(k), esc(q["opts"][k])))
    elif t in ("table", "dnd"):
        cats = q.get("cats") or []
        for i, r in enumerate(q.get("rows") or []):
            opts = "".join(
                '<option value="%s">%s</option>' % (esc(c), esc(c))
                for c in cats)
            out.append(
                '<div class="gate-row"><span>%s</span> <select name="row_%d">'
                "<option value=\"\"></option>%s</select></div>"
                % (esc(r["text"]), i, opts))
    elif t == "build" and "ordering" in q:
        import random
        blocks = list(q.get("blocks") or [])
        random.Random(0).shuffle(blocks)
        opts = "".join('<option value="%s">%s (%s)</option>' %
                       (esc(block["id"]), esc(block["text"]), esc(block["id"]))
                       for block in blocks)
        for i in range(len(blocks)):
            out.append('<div class="gate-row"><label>Position %d '
                       '<select name="step_%d"><option value=""></option>'
                       '%s</select></label></div>' % (i + 1, i, opts))
    elif t == "build":
        import random
        steps = list(q.get("steps") or [])
        random.Random(0).shuffle(steps)
        for i, s in enumerate(steps):
            opts = "".join(
                '<option value="%s">%s</option>' % (esc(x), esc(x))
                for x in steps)
            out.append(
                '<div class="gate-row"><select name="step_%d">'
                '<option value=""></option>%s</select></div>' % (i, opts))
    elif t == "short":
        out.append('<div class="gate-row"><textarea name="answer" rows="3">'
                   "</textarea></div>")
    return "\n".join(out)


def _gate_band_html(check_id, ctx):
    """The live gate band (06.2-UI-SPEC section 5.2): the same box as 3.1's
    reserved slot, filled with the check item's public projection, the
    Ledger header, and one `<form method="post">` whose two named submit
    buttons are `name="action" value="check"` first and `value="skip"`
    second -- check first in DOM order so Enter submits the check. The skip
    control is an ordinary control, never a transgression (C16); no
    JavaScript anywhere.

    When the check id resolves to no item in the bank, the band degrades to
    the D1 labelled rule with the warn-tone line and never gates -- reading
    continues (06.2-UI-SPEC section 14 error row). When the runtime is
    unreachable the band states the reason and offers no submission and no
    reveal (section 12.1). In diagnostic/exam sittings a declared required
    gate renders as recommended with the exact degrade line and no skip
    control (section 5.7).
    """
    gate = ctx.get("gate")
    q = gate["resolve"](check_id) if gate else None
    esc = html.escape
    declared = gate.get("as_authored") or gate["policy"]
    header = (GATE_HEADER_REQUIRED if declared == "required"
              else GATE_HEADER_RECOMMENDED)
    if q is None:
        # Unresolvable check: D1 labelled rule, warn tone, never gates.
        return ('<section class="callout callout-check"><p class="callout-label">'
                "%s</p><p class=\"gate-warn\">%s</p></section>"
                % (esc("Check"), esc(CHECK_UNRESOLVED_COPY
                                    % {"bank": gate["bank"]})))
    state = (gate.get("states") or {}).get(check_id, "open")
    if gate.get("print"):
        # ?print=1 / ?print=drill: 3.1's D1 labelled rule with the check's
        # own objective (06.2-UI-SPEC section 8.1); a print is not a skip.
        label = "Check \u00b7 %s" % (q.get("objective") or "")
        return ('<section class="callout callout-check"><p class="callout-label">'
                "%s</p></section>" % esc(label))
    if state == "cleared":
        verdict = ('<p class="gate-verdict y">%s</p>'
                   % esc(VERDICT_CORRECT_COPY))
        return ('<section class="gate"><p class="gate-label">%s</p>%s%s</section>'
                % (esc(header), _gate_check_answer(q), verdict))
    if gate.get("unreachable"):
        # C9: never a disabled button with no reason; the reason is stated
        # beside the controls, and no section is revealed.
        return ('<section class="gate"><p class="gate-label">%s</p>%s'
                '<p class="gate-note">%s</p></section>'
                % (esc(header), _gate_check_answer(q),
                   esc(RUNTIME_UNREACHABLE_COPY)))
    degrade_line = ""
    skip_button = ""
    skip_note = ""
    if gate.get("degraded"):
        degrade_line = ('<p class="gate-note">%s</p>' % esc(MODE_DEGRADE_COPY))
    elif gate.get("skip") == "after-attempt" and not gate.get("attempted"):
        # gate_skip: after-attempt -- the condition is stated in real
        # Ledger-voice text until one recorded attempt exists; never a
        # disabled button with no reason (C9, 06.2-UI-SPEC section 6.2).
        skip_note = ('<p class="gate-note">%s</p>'
                     % esc(SKIP_AFTER_ATTEMPT_COPY))
    elif gate.get("skip") != "off":
        skip_button = ('<button type="submit" name="action" '
                       'value="skip" class="go">%s</button>'
                       % esc(SKIP_COPY))
    # Paced embedding only (plan 16D-03): the POST must come back to the
    # same paced step, so the form carries the view and step as hidden
    # fields. Structure and copy are otherwise untouched; a non-paced
    # render emits the exact bytes it always did.
    paced_fields = ""
    if gate.get("paced_step"):
        paced_fields = ('<input type="hidden" name="view" value="paced">'
                        '<input type="hidden" name="step" value="%s">'
                        % esc(gate["paced_step"]))
    form = ('<form method="post" action="/lesson/%s/check" class="gate-form">'
            '<input type="hidden" name="check" value="%s">%s'
            "%s<div class=\"actions\">"
            '<button type="submit" name="action" value="check" '
            'class="go primary">%s</button>%s'
            "</div></form>"
            % (esc(gate["stem"]), esc(check_id), paced_fields,
               _gate_check_answer(q),
               esc(CHECK_ANSWER_COPY), skip_button))
    if gate.get("degraded") and not gate.get("unreachable"):
        # The item stays answerable in a degraded sitting (feedback is
        # deferred, not withheld); the line states why the gate does not run.
        form = ('<form method="post" action="/lesson/%s/check" class="gate-form">'
                '<input type="hidden" name="check" value="%s">'
                "%s<div class=\"actions\">"
                '<button type="submit" name="action" value="check" '
                'class="go primary">%s</button>'
                "</div></form>"
                % (esc(gate["stem"]), esc(check_id), _gate_check_answer(q),
                   esc(CHECK_ANSWER_COPY)))
    return ('<section class="gate"><p class="gate-label">%s</p>%s%s%s</section>'
            % (esc(header), form, skip_note, degrade_line))


def _gate_boundary_html(n):
    """The truncation boundary (06.2-UI-SPEC section 5.3): a full-measure
    1px --line rule, space-5 below the band, one Ledger-voice line. Two
    copy rows, so a plural bug cannot ship; never rendered for n == 0
    (nothing below the check)."""
    if n <= 0:
        return ""
    line = BOUNDARY_ONE if n == 1 else BOUNDARY_MANY.format(n=n)
    return ('<div class="gate-boundary"><p class="gate-note">%s</p></div>'
            % html.escape(line))


def _check_ids(lesson):
    """The `[!CHECK: <id>]` references in a parsed lesson, in document
    order -- the ids the daemon derives gate state for (plan 06.2-03)."""
    if not isinstance(lesson, dict):
        return []
    return [m.group(1) for m in
            re.finditer(r"\[!CHECK:\s*([^\s\]]+)\s*\]",
                        lesson.get("body", ""))]


def _callout_html(spec, body, ctx=None, required=False):
    """One honest callout container (D-18): a `<section class="callout
    callout-<slug>">` whose Ledger-voice label and decorative icon are
    accompanied by the escape-first `_inline()` body pass every other text
    run uses (T-031-01). The `[!CHECK: <id>]` variant renders the inert
    reserved slot with the exact Ledger copy and no form, no key, and no
    scoring path (03.1-UI-SPEC §9.4, §15) -- or, when a gate context is
    active, the live band (06.2-UI-SPEC §5.2).

    `ctx` (when supplied) carries the gate policy; `example_layout` is the
    reader setting (03.1-UI-SPEC §9.3/§14): an `[!EXAMPLE]` callout carries
    the `example-parallel` class when the setting is `parallel`, and stays
    stacked (the default) otherwise.

    `required` (D-16A-3) adds `data-required="1"` and nothing else, and
    defaults to False so every shipped call site renders byte identically. A
    required semantic is not a different block; it is the same block that
    says it matters. The attribute is a presentation marker: nothing in the
    runtime reads it and it grants no authorization.
    """
    slug, label, check_id = spec
    icon = '<span class="callout-icon">%s</span>' % _CALLOUT_ICON
    if slug == "check":
        gate = ctx.get("gate") if ctx is not None else None
        if gate is None:
            # CAP-02's Degraded clause, and the one place the shipped
            # renderer already implemented it before CAP-02 existed. The copy
            # now has exactly one home, the `inline_check` profile's
            # `offline_fallback`, so the contract and the learner-visible
            # string cannot drift. The surrounding markup is unchanged on
            # purpose: tests/gate_roundtrip.py asserts these bytes, and a
            # one-character difference in the registry turns it red rather
            # than shipping wrong copy quietly.
            inner = "<p>%s</p>" % html.escape(
                capabilities.static_path("inline_check"))
            # ACTIVITY-01's Degraded clause, on the surface a learner
            # actually meets: when this check's item declares a response form
            # this build does not have, the activity's own declared static
            # equivalent is appended after the no-session copy. When no
            # activity registry was threaded in, or the id does not resolve,
            # or the form is one of the eight shipped ones, nothing is
            # appended and these bytes are exactly what they were.
            declared = (ctx or {}).get("activities") or {}
            fallback = capabilities.activity_fallback(
                declared.get(check_id) or {})
            if fallback:
                inner += ('<p class="capability-static">%s</p>'
                          % html.escape(fallback))
            return ('<section class="callout callout-check">'
                    '<p class="callout-label">%s%s</p>'
                    '<div class="callout-body">%s</div></section>'
                    % (icon, html.escape(label), inner))
        return _gate_band_html(check_id, ctx)
    inner = _inline(body)
    if slug == "example":
        comparison = parse_lesson_comparison(body)
        if comparison is not None:
            if ctx is None or "comparison_questions" not in ctx or not glossable(
                    ctx["comparison_questions"], {"def": body}):
                inner = "Comparison withheld by the runtime disclosure check."
            elif comparison.get("error"):
                inner = ('<p>Comparison unavailable. Read the static explanation below.</p>'
                         + inner)
            else:
                inner = lesson_interaction.render(comparison, _inline)
        else:
            lineplot = parse_lesson_lineplot(body)
            if lineplot is not None:
                if ctx is None or "comparison_questions" not in ctx or not glossable(
                        ctx["comparison_questions"], {"def": body}):
                    inner = "Line plot withheld by the runtime disclosure check."
                elif lineplot.get("error"):
                    inner = ('<p>Line plot unavailable. Read the static explanation below.</p>'
                             + inner)
                else:
                    inner = lesson_interaction.render_lineplot(lineplot, _inline)
    extra = ""
    if slug == "example" and ctx is not None \
            and ctx.get("example_layout") == "parallel":
        extra = " example-parallel"
    flag = ' data-required="1"' if required else ""
    return ('<section class="callout callout-%s"%s><p class="callout-label">'
            "%s%s</p><div class=\"callout-body\"%s>%s</div></section>"
            % (slug + extra, flag, icon, html.escape(label),
               _dir_attr(ctx), inner))


def _dir_attr(ctx):
    """` dir="auto"` when the author explicitly declared `[LESSON-DIR: auto]`,
    the empty string otherwise (A11Y-02, plan 16A-08).

    The condition is `dir_declared AND the value survived validation AND
    dir == "auto"`, never `dir == "auto"` alone. `auto` is also the value a lesson that never asked receives, so the
    shorter condition would put this attribute on every paragraph of every
    existing bank, change the shipped golden content fixture's bytes, and turn
    tests/lesson_roundtrip.py red for a reason that has nothing to do with
    localization. Explicit opt-in is what makes this addition additive.

    On the opt-in path each text run resolves its own direction from its own
    first strong character, which is what a lesson mixing scripts inside one
    document needs. The resolution itself is the browser's: this file
    implements no bidi algorithm and adds no dependency that does.
    """
    return ' dir="auto"' if (ctx or {}).get("auto_dir") else ""


def _media_src(path, ctx):
    """Where a `present` asset's declared path is fetched from.

    A bank-relative path is prefixed with the context's `media_base`, which
    a served surface sets to its own route and every other caller leaves
    empty. An absolute path, a rooted path, or one already carrying a scheme
    is returned untouched: it is not the renderer's business to rewrite a
    location an author stated completely.
    """
    base = (ctx or {}).get("media_base") or ""
    if not base or not path:
        return path
    if "://" in path or path.startswith("/") or path.startswith(".."):
        return path
    return base.rstrip("/") + "/" + path.lstrip("/")


def _media_figure_html(asset, ref_id, ctx=None):
    """One media asset as a figure, in all four of its states (CAP-02,
    D-16A-7).

    `asset` is the registry row for `ref_id`, or `None` when the reference
    resolves to nothing, which happens both for a typo and for a render given
    no registry at all. Those two cases render the SAME figure on purpose: an
    author debugging a blank figure should not first have to work out which
    of the two failures they are looking at before they can read the message.

    The three declared states, from `capabilities.MEDIA_AVAILABILITY`:

    - `present` renders the image with its declared alternative and credit.
    - `missing` renders no image, the locked missing copy, and the
      alternative as readable text, so the lesson still says what the picture
      showed.
    - `remote` renders no image, the locked remote copy, the alternative, and
      a plain link. NOTHING is fetched here or anywhere else at render time:
      the recorded network rule is that the core loop must degrade and never
      block, and a lesson that needed a network to be understood would block.

    Every interpolated value passes through `html.escape`, the same
    escape-first discipline every other text run in this file follows, so an
    author-supplied path stays text and never becomes markup.

    No width, no height, no `style` attribute, no color, no spacing value, and
    no token. `media`, `media-unavailable`, and `media-remote` are class names
    for Phase 17A to style; this plan adds no CSS rule for any of them.
    """
    anchor = lesson_slug(ref_id) or "unknown"
    if not isinstance(asset, dict):
        # Unknown reference, or no registry at all. Show the id: the author
        # needs to see which reference failed, and the learner needs to know
        # something was meant to be here.
        return ('<figure class="media media-unavailable" id="media-%s">'
                "<p>%s</p><p>%s</p></figure>"
                % (html.escape(anchor), html.escape(MEDIA_MISSING_COPY),
                   html.escape(ref_id)))

    availability = (asset.get("availability") or "").strip()
    alt = (asset.get("alt") or "").strip()
    credit = (asset.get("credit") or "").strip()
    derivation = (asset.get("derivation") or "").strip()
    path = (asset.get("path") or "").strip()

    caption = ""
    if credit or derivation:
        parts = []
        if credit:
            parts.append(html.escape(credit))
        if derivation:
            parts.append(html.escape(derivation))
        caption = ("<figcaption%s>%s</figcaption>"
                   % (_dir_attr(ctx), "<br>".join(parts)))

    if availability == "present":
        description = ('<details class="media-description"%s><summary>Image description</summary>'
                       '<p>%s</p></details>' % (_dir_attr(ctx), html.escape(alt))) if alt else ""
        return ('<figure class="media" id="media-%s"><img src="%s" alt="%s">'
                "%s%s</figure>"
                % (html.escape(anchor), html.escape(_media_src(path, ctx)),
                   html.escape(alt), description, caption))
    if availability == "remote":
        return ('<figure class="media media-remote" id="media-%s">'
                '<p>%s</p><p>%s</p><a href="%s">%s</a>%s</figure>'
                % (html.escape(anchor), html.escape(MEDIA_REMOTE_COPY),
                   html.escape(alt), html.escape(path), html.escape(path),
                   caption))
    # `missing`, and anything the registry declares that lint has already
    # refused: the honest render is the one that still says what the picture
    # showed.
    return ('<figure class="media media-unavailable" id="media-%s">'
            "<p>%s</p><p>%s</p>%s</figure>"
            % (html.escape(anchor), html.escape(MEDIA_MISSING_COPY),
               html.escape(alt), caption))


def _static_instructional_html(name, registry=None):
    """The declared static instructional path for one capability, as one
    `<p class="capability-static">`, or the empty string when the capability
    is unregistered or declares no fallback (CAP-02's Degraded clause).

    One class and nothing else: no inline style, no color, no spacing value,
    no token, and no script. `.capability-static` has no CSS rule after Phase
    16A, deliberately. An unstyled paragraph is still legible, and Phase 17A
    owns how it looks; adding a rule here would be a visual decision Phase 16A
    is not allowed to make.
    """
    text = capabilities.static_path(name, registry)
    if not text:
        return ""
    return '<p class="capability-static">%s</p>' % html.escape(text)


def _unsupported_callout_html(kind, body):
    """The one refusal container for an unknown REQUIRED semantic (D-16A-3).

    The same shape `_callout_html` produces, with a literal label rather than
    a registry lookup (there is no registry entry to look up), the locked
    `UNSUPPORTED_SEMANTIC_COPY` sentence, and then the author's own body run
    through the identical escape-first `_inline()` pass every other text run
    uses. Nothing is dropped: a reader that quietly swallowed a block the
    author marked essential would be lying about what the lesson said.

    `kind` is accepted so a caller cannot lose it, and is deliberately NOT
    printed: the sentence a learner reads must not depend on an arbitrary
    author token. It is the linter, naming the kind, that tells the author.
    No color, no spacing value, no token, and no script is introduced here.
    """
    icon = '<span class="callout-icon">%s</span>' % _CALLOUT_ICON
    return ('<section class="callout callout-unsupported" '
            'data-required="1"><p class="callout-label">%s%s</p>'
            "<p>%s</p><div class=\"callout-body\">%s</div></section>"
            % (icon, html.escape("Unsupported block"),
               html.escape(UNSUPPORTED_SEMANTIC_COPY), _inline(body)))


def lesson_fence_languages(lesson):
    """The ordered list of fenced-block languages in a parsed lesson, in
    document order. The reader renders one section per heading (the intro is
    not rendered), so this walks each heading's body top to bottom with the
    same `FENCE_RE` and open-to-closer consumption `_protect_code` uses --
    the server-side enumeration the daemon's `/api/lesson/run` block-id
    resolution and the renderer's sequential `data-code-block` ids both
    follow (09-05 D-05), so a block id always names the same fence. A fence
    with no info string yields "" (never runnable)."""
    langs = []
    if lesson:
        for h in lesson.get("headings") or []:
            lines = (h.get("body") or "").split("\n")
            i = 0
            while i < len(lines):
                m = FENCE_RE.match(lines[i])
                if m:
                    langs.append(lesson_slug(m.group(2).strip() or ""))
                    fence = m.group(1)
                    closer = re.compile(r"^`{%d,}\s*$" % len(fence))
                    i += 1
                    while i < len(lines) and not closer.match(lines[i]):
                        i += 1
                i += 1
    return langs


def _block_runnable(lang, ctx):
    """A fence may render a live Run control only when every server-side
    prerequisite holds at render time: a daemon-served page, a non-empty
    language the stored profile enables, no LAN refusal, and a session to
    post against. Everything else renders the escaped source plus the
    unavailable reason (09-UI-SPEC "CS runnable prose": static/disabled/LAN
    blocks never render an enabled or deceptive control)."""
    if ctx is None or not ctx.get("runtime"):
        return False
    if not lang:
        return False
    if lang not in (ctx.get("run_languages") or ()):
        return False
    if ctx.get("lan_refused"):
        return False
    if not ctx.get("run_session_id"):
        return False
    return True


def _block_unavailable_reason(lang, ctx):
    """The locked unavailable copy for a fence that cannot run (09-UI-SPEC
    state table). An unknown profile (None, conservative presentation) or a
    fence with no language reads as static; a known profile whose runnable
    languages omit this language reads as disabled-language; an enabled
    language with no session/LAN refusal reads as static/LAN. A runnable
    block returns None. CLI and daemon resolve the profile through the same
    selector, so both surfaces render identical copy for the same bank."""
    if not lang:
        return RUN_STATIC_COPY
    run_languages = ctx.get("run_languages") if ctx is not None else None
    # A non-empty runnable list is a real run capability: a language outside
    # it is the disabled-language state. An empty list or an unknown profile
    # declares no run capability at all, which reads as the generic static
    # copy -- a profile with no runnable languages must render the reader
    # byte-for-byte like no profile at all (09-04 D-08).
    if run_languages and lang not in run_languages:
        return RUN_LANG_UNAVAILABLE_COPY.format(language=lang)
    if ctx is not None and ctx.get("lan_refused"):
        return RUN_LAN_REFUSAL_COPY
    return RUN_STATIC_COPY


def _code_block(info, content, ctx=None):
    """The one markup shape Phase 9 attaches to (D-08): a preformatted
    element wrapping a code element whose class names the info string.
    The class is sanitised with the same restricted character set
    `lesson_slug` uses, so a hostile info string cannot close the class
    attribute or introduce a second one (T-3-10); the content is the
    block's source, HTML-escaped and otherwise untouched -- no re-indent,
    no syntax highlighting.

    Every fence gets a stable sequential `data-code-block` id in document
    order (09-05 D-05, no reparse of the source). A fence that passes
    `_block_runnable` renders the runnable control instead of the inert
    `<pre>`: Example-code label, visible source label + textarea, keyboard
    help, the native Run example button, an idle `aria-live="off"` readout
    described by that control, and separately labelled non-live stdout/stderr regions --
    observation only, never a verdict (D-11). Every other fence keeps the
    escaped source and the locked unavailable reason.
    """
    lang = lesson_slug(info)
    esc = html.escape(content)
    seq = (ctx or {}).get("code_seq")
    if seq is None:
        seq = [0]
        if ctx is not None:
            ctx["code_seq"] = seq
    seq[0] += 1
    block_id = seq[0]
    if _block_runnable(lang, ctx):
        ctx["run_emitted"] = True
        textarea_id = "lesson-code-%d" % block_id
        rows = max(3, min(12, content.count("\n") + 2))
        return (
            '<div class="scroll runnable" data-code-block="%d" data-lang="%s">'
            '<span class="lang">%s</span><span class="example-label">%s</span>'
            '<label class="run-source-label" for="%s">%s</label>'
            '<textarea id="%s" class="run-source" rows="%d" spellcheck="false">%s</textarea>'
            '<p class="run-help">%s</p>'
            '<button type="button" class="run-go" aria-describedby="run-status-%d">%s</button>'
            '<p class="run-status" id="run-status-%d" aria-live="off"></p>'
            '<p class="run-label">%s</p><pre class="run-stdout"></pre>'
            '<p class="run-label">%s</p><pre class="run-stderr"></pre>'
            '</div>'
            % (block_id, html.escape(lang), html.escape(lang),
               html.escape(RUN_EXAMPLE_LABEL), textarea_id,
               html.escape(RUN_SOURCE_LABEL), textarea_id, rows, esc,
               html.escape(RUN_HELP_COPY), block_id, html.escape(RUN_READY_COPY), block_id,
               html.escape(RUN_STDOUT_LABEL), html.escape(RUN_STDERR_LABEL)))
    reason = _block_unavailable_reason(lang, ctx)
    notice = ('<p class="run-unavailable">%s</p>' % html.escape(reason)
              if reason is not None else "")
    code = ('<code class="language-%s">%s</code>' % (lang, esc)
            if lang else "<code>%s</code>" % esc)
    label = ('<span class="lang">%s</span>' % html.escape(lang)
             if lang else "")
    return ('<div class="scroll" data-code-block="%d" data-lang="%s">'
            '%s<pre class="code-source" tabindex="0" role="region" '
            'aria-label="Example code">%s</pre>'
            '<div class="code-tools" hidden><button type="button" class="go code-select">'
            'Select code</button><button type="button" class="go code-copy">Copy code</button>'
            '<span class="code-status" role="status" aria-live="polite"></span></div>%s</div>'
            % (block_id, html.escape(lang), label, code, notice))


def _protect_code(text, ctx=None):
    """Protect fenced code with the shared parser, then render its tokens."""
    protected, blocks = protect_fenced_code(text)
    return protected, [_code_block(info, body, ctx) for info, body in blocks]


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
    if len(rows) < 2 or not is_separator_row(rows[1]):
        return None
    header = split_cells(rows[0])
    body = [split_cells(r) for r in rows[2:]]
    if any(len(r) != len(header) for r in body):
        return None
    label = (ctx or {}).get("section_title") or "Lesson table"
    head = "".join('<th scope="col">%s</th>' % _inline(c) for c in header)
    rows_html = "".join(
        "<tr>%s</tr>" % "".join("<td%s>%s</td>"
                                % (_dir_attr(ctx), _inline(c)) for c in r)
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
                ctx["panels"].append((slug, _gloss_panel_html(
                    rec, slug, ctx["key_links"].get(slug))))
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
    protected, tokens = _protect_code(text, ctx)
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
        cm = CALLOUT_MARK_RE.match(line)
        if cm and callout_entered(line):
            # The callout branch (D-18): a `> [!KIND]` marker starts a run
            # whose body is every following `>`-prefixed line, closed at
            # the first non-`>` line. Only locked kinds -- plus the plan
            # 03.1-03 [!KEY] card -- enter here; an unknown OPTIONAL kind
            # falls through to the paragraph path unchanged. Phase 16A adds
            # one more entrant and no other change: an unknown kind marked
            # REQUIRED with a trailing `!` (D-16A-3), which is refused out
            # loud below rather than silently dropped.
            if callout_kind_of(line) == "KEY":
                raw_lines = [line]
                i += 1
                while i < len(lines) and lines[i].startswith(">"):
                    raw_lines.append(lines[i])
                    i += 1
                out.append(_key_card_html(raw_lines, ctx))
                continue
            spec = callout_spec(cm.group(1))
            kind, required = callout_required_of(cm.group(1))
            if spec is None and required:
                spec = callout_spec(kind)
            body = [cm.group(2)] if cm.group(2) else []
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                body.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            if spec is None:
                # Unknown and required: the only path that reaches here,
                # because an unknown optional kind never entered the branch.
                out.append(_unsupported_callout_html(kind, "\n".join(body)))
                continue
            out.append(_callout_html(spec, "\n".join(body), ctx,
                                     required=required))
            # G1 truncation (06.2-UI-SPEC section 5.2): under required,
            # the server emits nothing below the first OPEN check -- the
            # band already rendered, so the rest of this section and every
            # later section is withheld. A cleared OR skipped check
            # releases its section (a skip advances the reading position,
            # section 6.3), so truncation stops only at "open". The flag
            # is read by render_markdown and lesson_page to stop and to
            # size the boundary. An unresolvable check never gates
            # (reading continues).
            if (ctx is not None and ctx.get("gate")
                    and ctx["gate"]["policy"] == "required"
                    and not ctx["gate"].get("degraded")
                    and spec[0] == "check"
                    and ctx["gate"]["resolve"](spec[2]) is not None
                    and (ctx["gate"].get("states") or {}).get(spec[2],
                                                             "open")
                    == "open"):
                ctx["gate_stop"] = True
            if ctx is not None and ctx.get("gate_stop"):
                break
            continue
        mb = _MEDIA_BLOCK_RE.match(line)
        if mb:
            # The media branch (plan 16A-05): one line in, one figure out. The
            # registry rides in `ctx` under "media" exactly as the gate policy
            # and the example layout already do. A render given no registry
            # resolves every reference to None, which renders the honest
            # unavailable figure rather than guessing or dropping the line.
            registry = (ctx or {}).get("media") or {}
            ref_id = mb.group(1).strip()
            out.append(_media_figure_html(registry.get(ref_id), ref_id, ctx))
            i += 1
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
                items.append("<li%s>%s</li>"
                             % (_dir_attr(ctx), rendered))
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
                items.append("<li%s>%s</li>"
                             % (_dir_attr(ctx), rendered))
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
                    or callout_entered(nxt)
                    or _MEDIA_BLOCK_RE.match(nxt)):
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
        para = "<p%s%s>%s</p>" % (ids, _dir_attr(ctx), _inline(raw))
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
        if ctx is not None and ctx.get("gate_stop"):
            break
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
            focus_attr = ""
            if (ctx is not None and ctx.get("focus_section")
                    and ctx["section"] == ctx["focus_section"]):
                # The post-redirect-get focus target (06.2-UI-SPEC section
                # 7.1): the newly revealed section's h2 carries the
                # platform mechanism for moving focus after a navigation
                # with no script.
                focus_attr = ' tabindex="-1" autofocus'
            out.append('<section id="%s"><h2%s>%s</h2>%s</section>'
                       % (lesson_slug(heading), focus_attr,
                          html.escape(heading), prose))
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
        "comparison_questions": qs,
        "gloss": {},
        "marks": reader.get("gloss_marks", "all"),
        "print_inline": reader.get("print_gloss", "appendix") == "inline",
        "gloss_hover": reader.get("gloss_hover", "on") == "on",
        "example_layout": reader.get("example_layout", "stacked"),
        "reader_nav": reader.get("reader_nav", "auto"),
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
        "key_links": {},
        # A11Y-02's per-element direction opt-in (plan 16A-08). True only
        # when the author explicitly wrote [LESSON-DIR: auto]; see _dir_attr
        # for why the parsed default is not enough.
        "auto_dir": False,
        # The parsed `## ACTIVITIES` registry, item id -> declaration, or an
        # empty dict. Read only to resolve a fallback TEXT for an unsupported
        # response form; no feedback, retry, or evidence value is consulted
        # here or anywhere else in Phase 16A.
        "activities": {},
        # The parsed `## MEDIA` registry, or an empty dict. `lesson_page`
        # replaces this when a caller supplies one; a caller that supplies
        # none leaves it empty, and every [MEDIA:] reference then renders the
        # honest unavailable figure. `_reader_context` reads settings and does
        # not read the bank's media registry itself, because the render
        # function takes parsed data and reads no file of its own.
        "media": {},
        # The URL prefix a `present` asset's bank-relative path is served
        # under, or "" for the durable document, where the path is already
        # correct beside the file. A served page lives at `/lesson/<stem>`,
        # so a bare `media/x.svg` resolves to `/lesson/media/x.svg` and
        # 404s: the one image in the 17B tracer's lesson was broken in the
        # app for exactly this reason, with only its alt text carrying the
        # meaning. Empty by default, so the static build and `cmd_lesson`
        # render byte-identically to before.
        "media_base": "",
    }
    for key in parse_key_blocks(bank_path):
        if not key.get("id"):
            continue
        for ref in _GLOSS_MARK_RE.findall(key.get("body") or ""):
            slug = lesson_slug(ref.strip())
            if re.match(r"^[a-z0-9-]+$", slug or ""):
                ctx["key_links"].setdefault(slug, "key-%s" % lesson_slug(key["id"]))
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


def _backlinks_html(stem, qs, slug, context_nav=None):
    refs = backlinks(qs, slug)
    if not refs:
        return ""
    # Navigation identities come from the caller's admitted actions, never
    # from a course label or a locally inferred saved-session identifier.
    base = "/quiz/%s" % quote(stem, safe="")
    for entry in context_nav or ():
        href = entry.get("href") or ""
        target = urlsplit(href)
        if not target.scheme and not target.netloc and target.path == base:
            base = urlunsplit(("", "", target.path, target.query, ""))
            break
    rows = []
    saved_sitting = bool(parse_qs(urlsplit(base).query).get("session"))
    action = "Return to saved sitting" if saved_sitting else "Open practice"
    for q in refs:
        # The existing block renderer protects fences before classifying
        # prose, without creating lesson-section identities for a stem.
        preview = _render_blocks(q.get("stem") or "")
        if q.get("type") == "visual":
            preview += '<p>Open the question for its diagram and response controls.</p>'
        href = base if saved_sitting else base + "#" + quote(str(q["id"]), safe="")
        rows.append('<div class="practice-item"><span class="blabel">Question %d</span>'
                    '<a href="%s">%s</a>'
                    '<div class="practice-preview">%s</div></div>' %
                    (q["number"], html.escape(href, quote=True), action, preview))
    return ('<details class="bl section-practice"><summary>%s (%d)</summary>%s</details>'
            % (html.escape(BACKLINKS_LABEL), len(refs), "".join(rows)))


# ---- Phase 16A guided mode (D-16A-9) --------------------------------------
# Guided mode groups a heading's already-rendered blocks into stages. It does
# not re-render them: the rendered callout containers are byte-identical in
# both modes, because guided mode cuts the very string continuous mode
# produced rather than producing a second one. That is what keeps one
# renderer, and it is asserted rather than asserted-in-prose by the tracer.
#
# Reading position and resume are Phase 16B's and are deliberately absent
# here. A stage is a semantic grouping proven by an attribute; what it looks
# like is Phase 17A's decision and no color, spacing, token, transition, or
# script is introduced by any of this.

_CALLOUT_OPEN = '<section class="callout'
_SECTION_CLOSE = "</section>"


def guided_stages(heading_body, heading_slug=""):
    """Split one `###` heading's body into stages at each callout boundary.

    A stage is the run of blocks up to and including the next callout, so a
    callout ends a stage rather than starting one: the prose that leads up to
    a prerequisite or an example belongs with it, not with what follows.

    Returns a list of dicts carrying `index` (zero based), `slug`, `blocks`
    (the raw text of the stage), and `requires` (the required-semantic kinds
    found in the stage, always empty in this plan because required semantics
    are plan 16A-03's). A body with no callout returns a one-element list; an
    empty body returns an empty list.

    `heading_slug` is optional and is a deliberate departure from plan
    16A-02's one-argument signature, recorded in that plan's summary: the
    field spec says a stage slug is the heading slug plus a `-stage-<index>`
    suffix, which a function given only the body cannot produce. It defaults
    to the empty string so the one-argument call the plan writes still works,
    and the slug is built through `model.lesson_slug` either way, imported
    into this module as `lesson_slug`, rather than by raw string
    manipulation.
    """
    if not (heading_body or "").strip():
        return []
    lines = heading_body.split("\n")
    stages = []
    current = []
    in_callout = False
    for line in lines:
        stripped = line.strip()
        is_callout_mark = bool(CALLOUT_MARK_RE.match(stripped))
        if is_callout_mark:
            in_callout = True
        current.append(line)
        # A callout ends at the first line that is not a blockquote line, so
        # the stage boundary is the end of the callout and not its first line.
        if in_callout and not stripped.startswith(">"):
            in_callout = False
            body = "\n".join(current).strip()
            if body:
                stages.append(body)
            current = []
    tail = "\n".join(current).strip()
    if tail:
        stages.append(tail)
    if not stages:
        return []
    out = []
    for index, blocks in enumerate(stages):
        out.append({
            "index": index,
            "slug": lesson_slug("%s stage %d" % (heading_slug, index)),
            "blocks": blocks,
            "requires": [],
        })
    return out


def _stage_html(stage, rendered_blocks):
    """Wrap one stage's already-rendered block HTML in its stage section.

    Exactly one attribute beyond the class: `data-stage`, plus
    `data-stage-open` on index 0 only. No other class, no inline style, no
    script.
    """
    open_attr = ' data-stage-open="1"' if stage["index"] == 0 else ""
    return ('<section class="stage" data-stage="%d"%s>%s</section>'
            % (stage["index"], open_attr, rendered_blocks))


def _split_rendered_stages(rendered):
    """Cut one heading's rendered HTML after each callout container close.

    Operates on the rendered string rather than re-rendering, so every
    callout container in guided mode is the same bytes continuous mode
    produced. Callout containers do not nest a `<section>`, so the first
    `</section>` at or after a callout open is that callout's own close.
    Returns a list of HTML strings; a render with no callout returns a
    one-element list, and an empty render returns an empty list.
    """
    if not rendered:
        return []
    pieces = []
    pos = 0
    while True:
        start = rendered.find(_CALLOUT_OPEN, pos)
        if start == -1:
            break
        close = rendered.find(_SECTION_CLOSE, start)
        if close == -1:
            break
        cut = close + len(_SECTION_CLOSE)
        pieces.append(rendered[pos:cut])
        pos = cut
    tail = rendered[pos:]
    if tail.strip():
        pieces.append(tail)
    return pieces or [rendered]


# ---- Phase 16D paced mode (D-16D-5, D-16D-6, D-16D-7) ---------------------
#
# The paced view is a projection of the same rendered headings, one ladder
# step at a time, with a jump-only table of contents and a pager that gates
# forward only on an unattempted declared gate. It renders what the reader
# renders: intro prose before the first heading has never been part of this
# page in any mode, so a marker step carrying only such prose is a durable
# identity in `model.lesson_steps` but not a navigation stop here.

PACED_GATED_CONTINUE = ("Attempt the checkpoint above to continue, or use "
                        "the Steps list to jump ahead.")
PACED_UNKNOWN_STEP = ("That step is not in this lesson any more. Showing "
                      "the first step.")
PACED_NO_EVIDENCE = "This step records nothing."
PACED_STEPS_LABEL = "Steps"


def paced_view_steps(lesson):
    """The ladder's steps mapped onto the parsed headings this reader
    renders, keeping only heading-bearing steps (see the section comment).
    Returns `[{"id", "title", "idxs"}, ...]` in document order; a heading
    whose line appears in no step content (which the grammar does not
    produce) is appended to the nearest earlier step so no rendered heading
    can silently vanish from the paced view."""
    steps = lesson_steps(lesson)
    headings = (lesson or {}).get("headings") or []
    view = []
    for s in steps:
        idxs = [i for i, h in enumerate(headings)
                if ("### %s" % h["text"]) in s["content"]]
        if idxs:
            view.append({"id": s["id"], "title": s["title"], "idxs": idxs})
    claimed = set()
    for v in view:
        claimed.update(v["idxs"])
    for i in range(len(headings)):
        if i not in claimed and view:
            target = view[0]
            for v in view:
                if min(v["idxs"]) <= i:
                    target = v
            target["idxs"] = sorted(set(target["idxs"]) | {i})
    return view


def _paced_toc_html(view, current_id):
    items = []
    for n, v in enumerate(view, start=1):
        label = "%d. %s" % (n, v["title"])
        if v["id"] == current_id:
            items.append('<li><a href="?view=paced&amp;step=%s" '
                         'aria-current="true">%s (current)</a></li>'
                         % (html.escape(v["id"]), html.escape(label)))
        else:
            items.append('<li><a href="?view=paced&amp;step=%s">%s</a></li>'
                         % (html.escape(v["id"]), html.escape(label)))
    return ('<details class="details-section paced-steps" open>'
            "<summary>%s</summary><ol>%s</ol></details>"
            % (html.escape(PACED_STEPS_LABEL), "".join(items)))


PACED_TOUCHED_HEADING = "About what you picked"
PACED_SHOW_ANSWER = "Show the answer"


def _paced_tier_html(payload, show_href=None):
    """Render the runtime-settled checkpoint disclosure (D-PACED-3).

    The surface renders exactly what `runtime.checkpoint_feedback` handed
    it and decides nothing: which options appear, which rationale shows,
    and whether the full reveal is present were all settled by the runtime.
    Never colour alone: right and not-right are text chips.
    """
    if not payload or payload.get("error") or payload.get("tier", 0) == 0:
        return ""
    esc = html.escape
    parts = ['<section class="paced-feedback">']
    if payload["selection_marks"]:
        rows = "".join(
            '<li>%s) <span class="paced-mark">%s</span></li>'
            % (esc(m["option"]),
               "right" if m["state"] == "right" else "not right")
            for m in payload["selection_marks"])
        parts.append("<ul>%s</ul>" % rows)
    if payload["touched_da"]:
        das = "".join("<li>%s) %s</li>" % (esc(k), esc(v))
                      for k, v in sorted(payload["touched_da"].items()))
        parts.append("<h3>%s</h3><ul>%s</ul>"
                     % (esc(PACED_TOUCHED_HEADING), das))
    if payload.get("reveal"):
        reveal = payload["reveal"]
        answer = reveal.get("answer_text") or ", ".join(
            reveal.get("correct") or ())
        why = reveal.get("why") or ""
        parts.append('<div class="paced-reveal"><p>Answer: %s</p><p>%s</p>'
                     "</div>" % (esc(str(answer)), esc(why)))
    elif show_href:
        parts.append('<p><a class="go" href="%s">%s</a></p>'
                     % (esc(show_href), esc(PACED_SHOW_ANSWER)))
    parts.append("</section>")
    return "".join(parts)


def _paced_pager_html(view, index, gated):
    parts = ['<nav class="paced-pager" aria-label="Paced navigation">']
    if index > 0:
        parts.append('<a class="go" href="?view=paced&amp;step=%s">Back</a>'
                     % html.escape(view[index - 1]["id"]))
    if index + 1 < len(view):
        if gated:
            parts.append('<p class="paced-gated">%s</p>'
                         % html.escape(PACED_GATED_CONTINUE))
        else:
            parts.append('<a class="go" href="?view=paced&amp;step=%s">'
                         "Continue</a>"
                         % html.escape(view[index + 1]["id"]))
    parts.append("</nav>")
    return "".join(parts)


def lesson_page(bank_path, qs, lesson, ref=None, runtime=False, drill=False,
                style_override=None, profile=None, gate=None, focus=None,
                announce=None, session_id=None, lan_refused=False,
                mode="continuous", media=None, activities=None,
                step_id=None, tier_payload=None, tier_show_url=None,
                media_base="", context_nav=None, theme_css=None,
                exploration_context=None):
    """The one render both surfaces call: the daemon route and `cmd_lesson`
    write the same document because there is only one `lesson_page`.

    `mode` is `"continuous"` or `"guided"` (D-16A-9). It defaults to
    `"continuous"`, so every shipped caller renders the document it always
    rendered and guided mode is reached only by asking for it. Guided mode
    groups a heading's already-rendered blocks into stages; it does not
    re-render them, so the callout containers are byte-identical in both.
    Reading position and resume are Phase 16B's and are deliberately absent
    here. Any other value raises `ValueError`, because an unknown mode is a
    programming error at a call site rather than authored content and must
    fail loudly instead of falling back.

    `media` is whatever `model.parse_media()` returned, or `None`. It defaults
    to `None` so no positional caller changes and a bank with no `[MEDIA:]`
    line renders byte identically whether or not it is supplied. A `None`
    registry renders every `[MEDIA:]` reference as the unavailable figure
    carrying its own id, rather than dropping it: the renderer was given no
    registry, so it knows nothing about the asset and says so.

    `activities` is whatever `model.parse_activities()` returned, or `None`.
    It is read for one purpose only: an inline check whose item declares a
    response form outside the eight shipped ones shows that activity's
    declared static equivalent. No `feedback`, `retry`, or `evidence` value is
    consulted, here or anywhere else in Phase 16A; those columns describe what
    the runtime does and a renderer that obeyed them would be a second
    authority.

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

    `gate` is the Phase 6.2 policy context -- a dict with `policy`
    (required|recommended|off), `states` (check id -> open|cleared|skipped,
    derived from the evidence log by the caller), `resolve` (check id ->
    item or None), and the provenance the band needs (stem, bank, skip,
    degraded, unreachable, print, attempted). When `gate` is None -- a
    static render, `cmd_lesson`, no session, `[GATE: off]`, or the print
    path with policy off -- the reader renders exactly as Phase 3.1's:
    every [!CHECK:] is the inert reserved slot (D-14, the compatibility
    floor). The one render path carries the policy; there is no second
    reader (D-05).

    `focus` names a section slug whose rendered `<h2>` carries
    `tabindex="-1" autofocus` -- the post-redirect-get focus mechanism for
    a gate reveal (06.2-UI-SPEC section 7.1: focus moves only when the
    document grew). `announce` is the composed status-region text
    (section 7.2), rendered inside the single `role=status` region.
    """
    if mode not in ("continuous", "guided", "paced"):
        raise ValueError(
            'lesson_page: mode must be "continuous", "guided", or "paced" '
            "(got %r)" % mode)
    with open(bank_path, encoding="utf-8") as source_handle:
        bank_text = source_handle.read()
    title = (grab(r"(?m)^#\s+(.*?)\s*$", bank_text)
             or os.path.basename(bank_path))
    warn_css = ""
    nav_html = ""
    context_nav_html = ""
    if context_nav:
        links = []
        for entry in context_nav:
            href = entry.get("href")
            label = entry.get("label")
            if href and label:
                links.append('<a href="%s">%s</a>' % (
                    html.escape(href, quote=True), html.escape(label)))
        if links:
            context_nav_html = ('<nav class="lesson-context-nav" '
                                'aria-label="Lesson navigation">%s</nav>'
                                % "".join(links))
    anchor_css = ""
    print_css = ""
    gloss_script = ""
    status_html = ""
    ctx = None
    paced_view = None
    paced_index = 0
    paced_fallback = False
    if announce:
        status_html = ('<div class="status" role="status">%s</div>'
                       % html.escape(announce))
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
        elif mode == "paced":
            # One ladder step's headings (D-16D-5..7). An unknown step id
            # falls back to the first step and says so; it never guesses a
            # neighbouring step, because a resumed position that silently
            # moved is the identity failure D-PACED-1 exists to prevent.
            paced_view = paced_view_steps(lesson)
            if paced_view:
                match = next((n for n, v in enumerate(paced_view)
                              if v["id"] == step_id), None)
                if step_id is not None and match is None:
                    paced_fallback = True
                paced_index = match if match is not None else 0
                idxs = tuple(paced_view[paced_index]["idxs"])
            else:
                idxs = range(len(lesson["headings"]))
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
        # The parsed `## MEDIA` registry, threaded in exactly as the gate
        # policy and the example layout are. An absent registry stays the
        # empty dict `_reader_context` seeded, which is what makes a render
        # with no media argument byte identical to a pre-16A-05 render.
        if isinstance(media, dict):
            ctx["media"] = media.get("assets") or {}
        if media_base:
            ctx["media_base"] = media_base
        if isinstance(activities, dict):
            ctx["activities"] = activities.get("activities") or {}
        # The opt-in needs all three: the directive was present
        # (`dir_declared`), its value survived validation (`dir_raw` empty,
        # so nothing was refused), and that surviving value is `auto`. A
        # refused value like `[LESSON-DIR: sideways]` falls back to `auto`
        # too, and a fallback is not a declaration.
        ctx["auto_dir"] = bool(isinstance(lesson, dict)
                               and lesson.get("dir_declared")
                               and not (lesson.get("dir_raw") or "")
                               and lesson.get("dir") == "auto")
        ctx["key_answers"] = []
        # 09-05 runnable lesson code: the sequential data-code-block counter,
        # the profile's runnable languages, the session id to post against,
        # and whether this daemon is LAN-served with check.allow_lan off --
        # all decided here once per page, consumed by _code_block.
        ctx["code_seq"] = [0]
        ctx["run_emitted"] = False
        # None = no profile resolved (conservative static presentation);
        # a list = the profile's declared runnable languages. The CLI and
        # daemon resolve the profile through the same selector, so fence
        # copy matches byte-for-byte between surfaces.
        ctx["run_languages"] = (
            (profile or {}).get("profile", {}).get("lesson", {})
            .get("runnable_languages")) if profile is not None else None
        ctx["run_session_id"] = session_id
        ctx["lan_refused"] = bool(lan_refused)
        if gate is not None:
            ctx["gate"] = gate
            ctx["gate_stop"] = False
        if focus:
            ctx["focus_section"] = focus
        parts = []
        stop_at = None
        stage_index = 0
        for idx in idxs:
            h = lesson["headings"][idx]
            ctx["section"] = h["slug"] or ("section-%d" % idx)
            rendered = render_markdown(
                "### %s\n\n%s" % (h["text"], h["body"]), ctx)
            if mode == "guided":
                # Group, never re-render: the cuts are taken out of the very
                # string continuous mode produced, so every callout container
                # below is the same bytes it is above.
                #
                # Stage indices run across the whole document rather than
                # restarting per heading, so exactly one stage in the document
                # carries `data-stage-open`. Per-heading numbering would open
                # the first stage of every heading, which is not one guided
                # reading but several started at once.
                stages = guided_stages(h["body"], h["slug"] or "")
                # Keep the heading container outside the stages. Splitting
                # through it creates unbalanced sections that browsers repair
                # into nested stages, making later content impossible to reveal.
                heading_open = re.match(r'<section\b[^>]*>', rendered)
                outer_open = outer_close = ""
                stage_body = rendered
                if heading_open and rendered.endswith("</section>"):
                    outer_open = heading_open.group(0)
                    outer_close = "</section>"
                    stage_body = rendered[len(outer_open):-len(outer_close)]
                chunks = _split_rendered_stages(stage_body)
                if chunks:
                    if len(stages) != len(chunks):
                        stages = [{"index": i, "slug": "", "blocks": "",
                                   "requires": []}
                                  for i in range(len(chunks))]
                    numbered = []
                    for offset, (stage, chunk) in enumerate(
                            zip(stages, chunks)):
                        stage = dict(stage)
                        stage["index"] = stage_index + offset
                        numbered.append(_stage_html(stage, chunk))
                    stage_index += len(chunks)
                    rendered = outer_open + "".join(numbered) + outer_close
            if ctx.get("gate_stop"):
                # G1 truncation: the section ends at the band; the rest of
                # this section and every later section is withheld, and the
                # section's own backlinks (which would land after the band)
                # are withheld too -- the boundary is the last element.
                parts.append(rendered)
                stop_at = idx
                break
            parts.append(rendered + _backlinks_html(stem, qs, h["slug"], context_nav))
        body = "\n".join(parts)
        if stop_at is not None and gate is not None \
                and gate["policy"] == "required":
            # The boundary names how many full sections remain below the
            # check (06.2-UI-SPEC section 5.3); n == 0 renders no line.
            n = len(lesson["headings"]) - stop_at - 1
            body += _gate_boundary_html(n)
        if ctx["gloss"]:
            gloss_map = ctx["gloss"]
            if stop_at is not None:
                # Gated-read appendix filter (06.2-UI-SPEC section 5.6):
                # only terms marked in revealed sections render; a term that
                # appears only below an uncleared gate would otherwise reach
                # the DOM through the appendix's back door.
                gloss_map = {slug: rec for slug, rec in gloss_map.items()
                             if slug in ctx["panels_emitted"]}
            body += ctx["held_line"] + _glossary_html(
                gloss_map, ctx["first_uses"])
            anchor_css = _gloss_anchor_css(ctx["panels_emitted"])
            print_css = _gloss_print_css(
                "inline" if ctx["print_inline"] else "appendix")
            gloss_script = GLOSS_ENHANCEMENT_JS
            if ctx["gloss_hover"]:
                gloss_script += GLOSS_HOVER_JS
        visible_headings = [lesson["headings"][idx] for idx in idxs
                            if stop_at is None or idx <= stop_at]
        nav_mode = ctx["reader_nav"]
        if nav_mode == "auto":
            nav_mode = ("column" if mode == "continuous" and
                        len(visible_headings) >= 2 else "none")
        if nav_mode != "none":
            nav_html = _reader_nav_html(visible_headings, nav_mode)
            if stop_at is not None:
                nav_html += '<p class="gate-note">%s</p>' % html.escape(TOC_FILTERED_COPY)
        if drill and ctx.get("key_answers"):
            answers = "".join(
                "<li>%s</li>" % _inline(text)
                for _kid, text in ctx["key_answers"])
            body += ('<section id="answers"><h2>%s</h2><ol>%s</ol></section>'
                     % (html.escape(ANSWERS_HEADING), answers))
        if mode == "paced" and paced_view:
            v = paced_view[paced_index]
            header = ('<p class="paced-header">Step %d of %d: %s</p>'
                      % (paced_index + 1, len(paced_view),
                         html.escape(v["title"])))
            # When the lesson carries any checkpoint at all, a step with
            # none says in the Ledger voice that it records nothing, so a
            # silent step is a stated fact rather than an implication.
            all_checks = _check_ids(lesson)
            step_has_check = any(
                "[!CHECK:" in lesson["headings"][i]["body"]
                for i in v["idxs"])
            if all_checks and not step_has_check:
                header += ('<p class="paced-ledger">%s</p>'
                           % html.escape(PACED_NO_EVIDENCE))
            # The pager gates forward on ATTEMPTED, never on correct
            # (IL-20260828-03 via D-16D-5): a wrong answer opens it, a
            # skip opens it, and only a declared required gate nobody has
            # touched holds it. This is deliberately looser than the 6.2
            # read-truncation above, which keeps withholding the step's
            # tail until the check clears; the two compose.
            gated = False
            if gate is not None and gate.get("policy") == "required" \
                    and not gate.get("degraded") \
                    and not gate.get("unreachable"):
                for i in v["idxs"]:
                    for cid in re.findall(r"\[!CHECK:\s*([^\]]+)\]",
                                          lesson["headings"][i]["body"]):
                        cid = cid.strip()
                        if not (gate.get("attempted", {}).get(cid)
                                or gate.get("states", {}).get(cid)
                                == "cleared"):
                            gated = True
            body = (header + _paced_toc_html(paced_view, v["id"]) + body
                    + _paced_tier_html(tier_payload, tier_show_url)
                    + _paced_pager_html(paced_view, paced_index, gated))
            # The Steps disclosure is the paced view's navigation; the
            # reader nav would be a second list of the same headings.
            nav_html = ""
            lines = []
            if announce:
                lines.append(announce)
            if paced_fallback:
                lines.append(PACED_UNKNOWN_STEP)
            lines.append("Step %d of %d." % (paced_index + 1,
                                             len(paced_view)))
            status_html = ('<div class="status" role="status">%s</div>'
                           % html.escape(" ".join(lines)))
    if runtime and nav_html and _check_ids(lesson):
        # A changing visible-section outline must not move a required
        # check band. Keep the safe outline after the rendered material
        # in every live/inert state of a checkpoint-bearing lesson.
        body += nav_html
        nav_html = ""
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
    # exactly as a session would; the CLI resolves the same profile for
    # fence copy but enhancement stays a served-page capability). Only a
    # daemon-served page whose profile's lesson.math flag is true loads the
    # local assets and the adapter; EMT/plain profiles emit empty slots and
    # byte-identical pages (D-08).
    math_assets = ""
    math_script = ""
    if runtime and profile and \
            (profile.get("profile") or {}).get("lesson", {}).get("math"):
        math_assets = MATH_ASSETS_HTML
        math_script = MATH_ADAPTER_JS
    # 09-05 runnable lesson code: the adapter ships only when at least one
    # fence actually rendered a Run control (no runnable blocks -> no empty
    # runner panel and no script, keeping the gated/no-run reader script-free
    # and every non-CS profile byte-identical to pre-09-05). The session id
    # rides on #lesson-content as a data attribute; the JS posts it back so
    # the daemon resolves the stored profile and bank.
    run_emitted = bool(ctx is not None and ctx.get("run_emitted"))
    runnable_css = RUNNABLE_CSS if run_emitted else ""
    runnable_js = RUNNABLE_JS if run_emitted else ""
    run_session_attr = (' data-run-session="%s"'
                        % html.escape(session_id) if session_id else "")
    if (runtime and isinstance(exploration_context, dict) and
            (mode == "guided" or 'class="lesson-comparison"' in body or
             'class="lesson-lineplot"' in body)):
        run_session_attr += lesson_interaction.exploration_attributes(
            exploration_context.get("lesson_id"),
            exploration_context.get("revision_id"),
            exploration_context.get("occurrence_id"))
    # A11Y-02: the document language and direction come from the parsed
    # lesson's own directives, escaped exactly as every other interpolated
    # value in this chain is. `lesson` may be None and may predate the two
    # directives entirely, so both fall back to the same defaults
    # `model.parse_lesson` uses, which is what keeps a bank written before
    # this phase rendering the page it always rendered.
    doc_lang = html.escape((lesson or {}).get("lang") or "en")
    doc_dir = html.escape((lesson or {}).get("dir") or "auto")
    presentation_profile, _profile_notice = settings.resolve_presentation_profile(
        settings.load_settings(bank_dir))
    return (LESSON_TEMPLATE
            .replace("__LANG__", doc_lang)
            .replace("__DIR__", doc_dir)
            .replace("__PRESENTATION_PROFILE__",
                     html.escape(presentation_profile, quote=True))
            .replace("__READING_MODE__", mode)
            .replace("__READER_APPLICATION__",
                     '')
            .replace("__READER_BYLINE__",
                     ('<details class="lesson-reading-about"><summary>About this reading</summary>'
                      '<div class="sub">Reading · __SUB__</div></details>'))
            .replace("__THEME__", THEME_CSS if theme_css is None else theme_css)
            .replace("__SHARED_CSS__", SHARED_CSS)
            .replace("__LESSON_CSS__", LESSON_CSS + (lesson_interaction.CSS
                     if 'class="lesson-comparison"' in body else "")
                     + (lesson_interaction.LINEPLOT_CSS
                        if 'class="lesson-lineplot"' in body else "")
                     + (lesson_progressive.CSS if mode == "guided" else ""))
            .replace("__WARN_CSS__", warn_css)
            .replace("__GLOSS_ANCHOR_CSS__", anchor_css)
            .replace("__GLOSS_PRINT_CSS__", print_css)
            .replace("__RUNNABLE_CSS__", runnable_css)
            .replace("__PRODUCT_CSS__", product_reader_css())
            .replace("__PRODUCT_NAV__", standalone_product_nav())
            .replace("__READER_NAV__", nav_html)
            .replace("__GLOSS_SCRIPT__", gloss_script)
            .replace("__MATH_ASSETS__", math_assets)
            .replace("__MATH_SCRIPT__", math_script + (lesson_interaction.JS
                     if 'class="lesson-comparison"' in body else "")
                     + (lesson_interaction.LINEPLOT_JS
                        if 'class="lesson-lineplot"' in body else "")
                     + (lesson_progressive.JS if mode == "guided" else "")
                     + (CODE_CRAFT_JS if 'class="code-tools"' in body else ""))
            .replace("__STATUS__", status_html)
            .replace("__CONTEXT_NAV__", context_nav_html)
            .replace("__RUNNABLE_JS__", runnable_js)
            .replace("__RUN_SESSION_ATTR__", run_session_attr)
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
    cm = CALLOUT_MARK_RE.match(text)
    if cm:
        return cm.group(1).split(":")[0].strip().upper()
    if text.startswith("```"):
        return "code"
    if re.match(r"^#{4,}\s", text):
        return "heading"
    if re.match(r"^(\s*[-*]\s|\s*\d+\.\s)", text):
        return "list"
    lines = text.splitlines()
    if len(lines) >= 2 and "|" in lines[0] and is_separator_row(lines[1]):
        return "table"
    return "paragraph"


def _split_section_blocks(body):
    """Split one section body into the logical blocks _render_blocks() would
    consume, so a permutation moves blocks rather than fragments: fenced
    code protected first, then blank-line boundaries, with `>` callout runs
    and pipe-table runs kept whole (D-11)."""
    protected, tokens = _protect_code(body, None)
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
    with open(out, "w", encoding="utf-8") as source_handle:
        source_handle.write(page)
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
    if getattr(a, "complete", False):
        return cmd_lesson_complete(a)
    qs = load(a.bank)
    lesson = parse_lesson(a.bank)
    out = a.out or os.path.splitext(a.bank)[0] + "_lesson.html"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    # Plan 09-05: the lesson presentation resolves the subject profile
    # through the same server-side selector the daemon route uses, so the
    # static render's fence copy (disabled-language/static) matches the
    # served page byte-for-byte; enhancement (math, run controls) still
    # stays a served-page capability (D-08). A profile that cannot be
    # resolved renders the conservative static copy, never a refusal.
    # `--subject-profile` supplies the one explicit id a client may send;
    # only the id crosses the boundary, the selector resolves it once.
    try:
        profile = subjects.select_profile(
            qs, subjects.load_registry(
                os.path.dirname(os.path.abspath(a.bank)) or "."),
            explicit_id=getattr(a, "subject_profile", None))
    except subjects.SubjectProfileError:
        profile = None
    page = lesson_page(a.bank, qs, lesson, ref=a.ref, profile=profile,
                       media=parse_media(a.bank),
                       activities=parse_activities(a.bank))
    if page is None:
        sys.exit("no lesson heading matching %r in %s" % (a.ref, a.bank))
    with open(out, "w", encoding="utf-8") as source_handle:
        source_handle.write(page)
    if a.ref:
        count = 1
    elif lesson and lesson.get("headings"):
        count = len(lesson["headings"])
    else:
        count = 0
    print("%d lesson section(s) -> %s" % (count, out))
    return 0


def cmd_lesson_complete(a):
    """`itembank lesson BANK --ref HEADING --complete` (plan 10-02,
    SCHED-04/D-24): the ONE explicit completion seam. Resolves the heading
    through the Phase 3 slugifier and reader (`model.lesson_slug`,
    `model.parse_lesson`, `model.load` -- never a second parser, slugger, or
    a filesystem path from client input), discovers the sorted unique
    objectives of items referencing it, appends exactly one
    `lesson_complete` event through the ONE evidence writer, then captures
    once and prints the event status, the configured interval, the derived
    next-review date, the reason, and the snapshot id from that projection.

    The command is idempotent: retrying the same completion reports
    `already_recorded` and appends nothing (D-02). A completion without
    `--ref`, an unknown heading, or a heading no item references with an
    [OBJECTIVE:] line is refused with a named explanation and writes
    nothing. The read/render path stays side-effect-free -- completion is a
    separate branch, never a side effect of rendering or scrolling.
    """
    if not getattr(a, "ref", None):
        sys.exit("lesson --complete requires --ref HEADING: a completion "
                 "names exactly one Phase 3 lesson heading")
    qs = load(a.bank)
    lesson = parse_lesson(a.bank)
    slug = lesson_slug(a.ref)
    if lesson is None or not any(h["slug"] == slug for h in lesson["headings"]):
        sys.exit("no lesson heading matching %r in %s" % (a.ref, a.bank))
    objectives = sorted({q.get("objective", "") for q in qs
                         if q.get("lesson_slug") == slug and q.get("objective")})
    if not objectives:
        sys.exit("lesson.no_referenced_objective: no item referencing %r "
                 "carries an [OBJECTIVE:] line, so nothing can enter the "
                 "review queue" % (a.ref,))
    subject = evidence.subject_of(objectives[0])
    if not subject or any(evidence.subject_of(o) != subject for o in objectives):
        sys.exit("lesson.no_single_subject: items referencing %r must share "
                 "one namespaced subject to record a completion" % (a.ref,))
    bank_dir = os.path.dirname(os.path.abspath(a.bank)) or "."
    event = evidence.lesson_complete_event(
        session_id="reader", bank=os.path.basename(a.bank),
        lesson_slug=slug, subject=subject, objectives=objectives,
        zone=getattr(a, "zone", None) or "UTC")
    result = evidence.append_event(evidence.log_path(bank_dir), event)
    cfg = {}
    try:
        from surfaces import settings as _settings
        cfg = _settings.load_settings(bank_dir)
    except Exception:
        cfg = {}
    events = evidence.capture_events(evidence.log_path(bank_dir))
    snapshot = retention.capture(events, zone=event["zone"], cfg=cfg)
    rows = [r for r in retention.lesson_queue(snapshot)
            if r["event_id"] == result["event_id"]]
    print("%s lesson completion for %r (%d objective(s) -> review queue)"
          % (result["status"], a.ref, len(rows)))
    for r in rows:
        print("  %s: next review %s (%d day(s), reason: %s)"
              % (r["objective"], r["next_review_date"], r["interval_days"],
                 r["reason"]))
    print("snapshot: %s" % snapshot["claim"]["snapshot_id"])
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


def gloss_page(stem, record, slug, return_href=None):
    """The served gloss page for the navigation path (03.1-UI-SPEC §8.3
    degraded): the definition plus a real `Back to the question` link whose
    href is the lesson anchor -- never a dead control, never a spinner."""
    back_href = return_href or "/lesson/%s#term-%s" % (stem, slug)
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            "<title>%s</title></head><body>"
            "<p>%s</p><p>%s</p>"
            '<p><a href="%s">%s</a></p>'
            "</body></html>"
            % (html.escape(record["canonical"]),
               html.escape(record["canonical"]),
               _inline(record["def"]),
               html.escape(back_href, quote=True),
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
