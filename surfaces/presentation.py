"""The shared semantic-HTML presentation seam (plan 04-04 Task 2).

Every surface that renders reads from one visual system: the palette comes
from `surfaces.theme.theme_css()`, and the *structure* comes from the small
escaped native-element primitives in this module -- `surface_shell`,
`context_line`, `teaching_step`, `state_panel`, and `details_section` --
plus `render_surface(view, adapter=None)`, the replaceable view-to-HTML
seam. Nothing here owns scoring, persistence, routing, scheduling,
evidence, or lesson parsing; view dictionaries carry presentation-ready
labels, content, state, and actions only, never scorers, keys, session
file paths, evidence writers, or mutation callbacks (D-04's "surfaces are
thin clients" rule extended to the markup itself).

The design tokens below implement the shared shell. `SHARED_CSS`'s `:root`
block is the OWNER of the spacing, radius, voice and measure tokens --
`--space-1` … `--space-7`, `--r-1` … `--r-3`, `--font-paper`/`--font-ledger`/
`--font-chrome`/`--font-code`, `--measure-prose`/`--measure-wide` and
`--leading-lesson` -- while `surfaces/theme.py` stays the sole owner of the
palette. No surface file may define a spacing or voice token of its own, and
no surface file may name a font family literally (`.planning/UI-SPEC.md` §7);
that rule was unenforceable until `--font-chrome` and `--font-code` existed
here, because there was no token to name instead.

The project type scale is **five sizes -- 12 / 16 / 18 / 20 / 32 px -- at
weights 400 and 600 only** (`.planning/UI-SPEC.md` §7, `03.1-UI-SPEC.md` §4,
14-UI-SPEC §4.2). 12px is the *label* size, not a general "small text" size:
any string inside an interactive control, and any string a learner must read
in order to recover from a failure, is 16px minimum. This paragraph
previously claimed four sizes of 14/16/20/28, which predated `text-lesson`
and the display row and is what let eleven 14px sites accumulate below. Plan
14-02 dispositioned those eleven individually -- the four disclosure/link
controls and the two recovery regions to 16px, the five label roles to 12px
-- and moved the display row from 28px to 32px, so no size in this file is
off the scale. `day.py`, `study.py` and `theme.py`'s settings CSS still
carry 14px sites; that is recorded debt (14-UI-SPEC §17 item 6), not a
second scale.

The rest of the shell is unchanged: the 8-point spacing scale
(4/8/16/24/32/48/64), 720px content / 800px shell measures, 44px interactive
targets, a 2px focus ring with 2px offset, a 768px breakpoint, 320px overflow
protection, a 150ms motion cap, and the reduced-motion kill rule. A future
graphical/canvas presentation may only attach behind `render_surface`'s
adapter seam while equivalent semantic HTML remains present and operable.
"""
import html, json


# Shared spacing/typography/measure/accessibility CSS. Token *names* come
# from the generated theme block a caller substitutes; this file introduces
# no color literals and no second palette (D-04). No `nowrap` and no
# `text-overflow` anywhere: meaningful text wraps rather than truncating.
#
# THE @font-face URL FORM, and its cost, recorded once here rather than in
# the emitted stylesheet (every CSS comment below ships in every served
# page's <style> block, so rationale belongs in Python, not in CSS):
#
# The four vendored-face urls are ROOT-ABSOLUTE, under the daemon's
# `/assets/fonts/` route -- the same closed-map shape the vendored KaTeX
# asset route already uses. They were relative until the fix for this
# defect, and a relative url resolves against the *route*, not against the
# site root: on a nested page route the browser asked for
# `/lesson/fonts/...` and got four 404s per page load, so the reader never
# once rendered in its intended typefaces under the daemon. Served pages go
# from zero of four faces loading to four of four, at every route depth.
#
# The stated cost: a standalone page written with `itembank build --out`
# resolves nothing here and degrades to the Georgia / ui-monospace fallback
# stack by design. That is not a regression -- the --out file is written
# beside the bank, and no bank directory carries a fonts/ directory, so the
# relative form already resolved nothing there either. Embedding the four
# faces as data urls would fix the file-scheme case at roughly a third of a
# megabyte of base64 added to every emitted page plus a second emit path to
# maintain; rejected on cost, and recorded here as the honest future option
# behind an explicit embed flag rather than as a silent default.
#
# WHY --measure-prose IS 59ch AND NOT 66ch (14-UI-SPEC §4.3, plan 14-02),
# recorded in Python for the same reason as above:
#
# `1ch` is the advance of `0`, which is 0.500 em in Source Serif 4, while the
# frequency-weighted average character in running English prose (spaces
# included) is 0.447 em. The ratio is 1.118; in iA Writer Quattro it is
# 1.119, so one correction serves both voices. The old `66ch` therefore
# rendered 74 real characters at 18px -- past .planning/UI-SPEC.md §8's
# 72-character ceiling -- and `90ch` rendered about 101. The token names and
# their stated intent are unchanged; only the numbers that express that
# intent moved: 59ch is 531px at 18px, which is 66 real characters, and 80ch
# is the 720px container cap. The reader must also add its side gutter
# OUTSIDE this token (`*{box-sizing:border-box}` is global), or the padding
# eats the column and the correction does nothing.
SHARED_CSS = r"""
*{box-sizing:border-box}
/* The document is the scroll container. If a shell introduces a nested
   overflow canvas, this padding moves to that container in the same change. */
html{scroll-behavior:smooth;scroll-padding-top:calc(var(--sticky-h,0px) + var(--space-2))}
html:has([data-surface-context]){--sticky-h:56px}
@media (max-width:767px){html:has([data-surface-context]){--sticky-h:88px}}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.5 var(--font-chrome)}
/* Voice & measure tokens (03.1-UI-SPEC §2, §7.1): fonts resolve by token
   only. --font-paper/--font-ledger prefer the vendored faces (Source Serif
   4 / iA Writer Quattro -- landed in plan 03.1-01) and fall back to the
   no-vendor stack Georgia / ui-monospace when no font file is present; the
   @font-face rules for the vendored faces live in this same token layer
   (plan 03.1-06 Task 2). A @font-face whose src cannot load (file absent)
   makes its family unavailable, so the token stack degrades to the
   fallback with no surface knowing a family name. --measure-prose/
   --measure-wide are character measures, not pixel spacing;
   --leading-lesson is the sustained-prose line height. */
/* Vendored faces (03.1-06 Task 1): the last path segments match
   fonts/MANIFEST.json file rows; weights are the reading surface's 400/600
   pair for the paper voice and 400/700 for the ledger voice (UI-SPEC §7
   "two weights per face"). The urls are root-absolute because a relative
   one resolves against the page route and 404s; a file-scheme page
   therefore resolves nothing here and degrades to the fallback stack by
   design. Full rationale and rejected alternative: the module comment
   above this constant. */
@font-face{font-family:"Source Serif 4";font-style:normal;font-weight:400;
  src:url("/assets/fonts/source-serif/SourceSerif4-Regular.ttf.woff2") format("woff2");
  font-display:swap}
@font-face{font-family:"Source Serif 4";font-style:normal;font-weight:600;
  src:url("/assets/fonts/source-serif/SourceSerif4-Semibold.ttf.woff2") format("woff2");
  font-display:swap}
@font-face{font-family:"iA Writer Quattro";font-style:normal;font-weight:400;
  src:url("/assets/fonts/ia-writer-quattro/iAWriterQuattroS-Regular.woff2") format("woff2");
  font-display:swap}
@font-face{font-family:"iA Writer Quattro";font-style:normal;font-weight:700;
  src:url("/assets/fonts/ia-writer-quattro/iAWriterQuattroS-Bold.woff2") format("woff2");
  font-display:swap}
/* The spacing scale (14-UI-SPEC §3.1, fixing DEFECT D-A): exactly
   .planning/UI-SPEC.md §7's 8-point scale with 03.1-UI-SPEC.md §3's
   assignments. These seven names were referenced 64 times by LESSON_CSS and
   defined nowhere, so every margin/padding/gap in the reader resolved to its
   initial value -- no paragraph rhythm, no callout padding, no side gutter,
   no section spacing, and no browser error to say so. There is no eighth step
   and no second scale.
   --font-chrome and --font-code complete the voice set that --font-paper and
   --font-ledger began: the stacks are copied verbatim from the `body` and
   `.mono`/`code,pre` declarations that spelled them out inline, so the
   emitted stacks are unchanged. This is centralisation, not a new choice. */
:root{
  --font-paper:"Source Serif 4",Georgia,serif;
  --font-ledger:"iA Writer Quattro",ui-monospace,monospace;
  --font-chrome:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --font-code:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --space-1:4px;
  --space-2:8px;
  --space-3:16px;
  --space-4:24px;
  --space-5:32px;
  --space-6:48px;
  --space-7:64px;
  --measure-prose:59ch;
  --measure-wide:80ch;
  --leading-lesson:1.65;
  --r-1:6px;
  --r-2:8px;
  --r-3:12px;
  /* The five frozen type tokens (17A-UI-SPEC Typography, plan 17A-02 Task 2).
     These are a transcription of the sizes already rendering across
     quiz_page.py, lesson.py, study.py and this file, not a new scale: there
     is no sixth size, and a component that wants one routes the need through
     these five rows first. Each token carries only the SIZE; the paired
     weight and line height stay in the rule that uses it, because a weight
     belongs to a heading rather than to a size. */
  --text-xs:12px;
  --text-body:16px;
  --text-lesson:18px;
  --text-heading:20px;
  --text-display:32px;
  /* Density aliases (17A-UI-SPEC Density tokens). Comfortable is the default
     and is what every existing rule already spaces by, so adopting a token
     changes nothing until a surface opts into compact. Every value on both
     sides is an alias of the existing --space-* scale, never a new raw pixel,
     which is what keeps compact bounded: --space-1 is the floor of the scale,
     so density cannot express anything tighter than 4px. The 44px touch
     target is fixed regardless of density and is not aliased here. */
  --density-row-gap:var(--space-3);
  --density-card-pad:var(--space-3);
  --density-list-gap:var(--space-2)
}
/* Compact is one opt-in attribute on any ancestor, so a dense panel can sit
   inside a comfortable page. The bound is the alias, not a clamp: there is no
   third step below this one. */
[data-density="compact"]{
  --density-row-gap:var(--space-2);
  --density-card-pad:var(--space-2);
  --density-list-gap:var(--space-1)
}
.surface{max-width:720px;margin:0 auto;padding:24px 16px 64px;min-width:0}
.surface.wide{max-width:800px}
h1{font-size:32px;font-weight:600;line-height:1.2;margin:0 0 8px}
h2{font-size:20px;font-weight:600;line-height:1.2;margin:32px 0 16px}
h3{font-size:16px;font-weight:600;line-height:1.4;margin:24px 0 8px}
p{font-size:16px;line-height:1.5;margin:0 0 16px;overflow-wrap:anywhere}
a{color:var(--accent);text-decoration:none;font-weight:600}
a:hover,a:focus-visible,button:focus-visible,summary:focus-visible,
input:focus-visible,textarea:focus-visible,select:focus-visible{
  outline:2px solid var(--accent);outline-offset:2px}
.mono{font-family:var(--font-code);
  font-variant-numeric:tabular-nums}
.back{margin:0 0 24px;color:var(--mut);font-size:16px}
.app-nav{display:flex;align-items:center;justify-content:space-between;
  gap:var(--space-3);margin:0 0 var(--space-4);padding:0 0 var(--space-3);
  border-bottom:1px solid var(--line)}
.app-nav .app-name{color:var(--ink);font-weight:600}
.app-nav ul{display:flex;align-items:center;gap:var(--space-3);
  list-style:none;margin:0;padding:0}
.app-nav a[aria-current]{color:var(--ink);text-decoration:underline;
  text-underline-offset:5px;text-decoration-thickness:2px}
.current-area{color:var(--mut);font-size:var(--text-xs);margin:0 0 var(--space-2)}
.course-nav-mobile{display:none}
.course-nav-mobile summary{cursor:pointer;min-height:44px;padding:10px 0;
  font-size:var(--text-body);font-weight:600}
.shelf-empty .actions{margin-top:var(--space-3)}
.context-line{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;
  gap:4px 18px;align-items:center;background:var(--bg);padding:8px 0 10px;
  border-bottom:1px solid var(--line);margin-bottom:14px;font-size:12px;
  color:var(--mut)}
.context-line .cx{overflow-wrap:anywhere}
.card,.step,.state,.empty{background:var(--card);border:1px solid var(--line);
  border-radius:12px;padding:16px;margin:0 0 16px}
.step .step-label{font-size:20px;font-weight:600;margin:0 0 8px}
.step .step-prompt{font-size:16px;font-weight:600;margin:0 0 12px}
.step-body{font-size:16px;line-height:1.5;overflow-wrap:anywhere}
.step-status{min-height:24px;font-size:12px;color:var(--mut);
  margin:12px 0 0}
.step details{margin:12px 0 0;border-top:1px solid var(--line);
  padding-top:8px}
.step details summary{cursor:pointer;font-size:16px;font-weight:600;
  min-height:44px;box-sizing:border-box;padding:10px 0}
details.details-section{border:1px solid var(--line);border-radius:8px;
  padding:8px 12px;margin:12px 0 16px;background:var(--card)}
details.details-section summary{cursor:pointer;font-size:16px;
  font-weight:600;min-height:44px;box-sizing:border-box;padding:10px 0}
.actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:12px}
button.go,a.go{display:inline-flex;align-items:center;justify-content:center;
  min-height:44px;font:inherit;font-size:16px;font-weight:600;
  padding:10px 16px;border-radius:8px;border:1px solid var(--line);
  background:var(--card);color:inherit;cursor:pointer;text-decoration:none;
  transition:.12s}
button.go.primary,a.go.primary{background:var(--accent-soft);
  border-color:var(--accent);color:var(--accent)}
button.go:disabled{opacity:.55;cursor:default}
.state{padding:12px 16px;font-size:16px;color:var(--mut)}
.state .state-text{margin:0}
.state.state-ok{color:var(--ok);background:var(--ok-bg);border-color:var(--ok)}
.state.state-bad{color:var(--bad);background:var(--bad-bg);border-color:var(--bad)}
.state.state-warn{color:var(--warn);border-color:var(--warn)}
/* Course-area rows (`17B-03 D-06 item 3`): the areas now carry the course's
   own artifacts, so they need a list shape. One rule set, composed from the
   existing tokens: no new color, no new spacing value, no new size. */
.area-lead{color:var(--mut);margin:0 0 var(--space-3)}
/* The bind panel (`source binding / create`): a two-column label/field grid
   that stacks under 768, composed from the existing tokens. */
.bind-panel{margin:var(--space-5) 0 0;padding:var(--space-4) 0 0;
  border-top:1px solid var(--line)}
.bind-grid{display:grid;grid-template-columns:minmax(9rem,auto) 1fr;
  gap:var(--space-2) var(--space-3);align-items:center;
  margin:0 0 var(--space-3)}
.bind-grid label{color:var(--mut);font-size:var(--text-xs)}
.bind-grid select,.bind-grid input{font:inherit;font-size:var(--text-body);
  padding:10px 12px;min-height:44px;border-radius:var(--r-2);
  border:1px solid var(--edge);background:var(--card);color:var(--ink);
  max-width:100%}
@media (max-width:767px){.bind-grid{grid-template-columns:1fr}}
.course-rows{list-style:none;margin:0;padding:0;display:grid;
  gap:var(--density-list-gap)}
.course-rows .row{display:grid;gap:var(--space-1)}
.row-head{display:flex;flex-wrap:wrap;gap:var(--space-2);
  align-items:baseline;justify-content:space-between}
.row-meta{color:var(--mut);font-size:var(--text-xs)}
.row-note{margin:0;color:var(--mut);font-size:var(--text-xs)}
.row{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:16px;margin:0 0 16px}
.row .name{font-size:16px;font-weight:600;overflow-wrap:anywhere}
.row .links{display:flex;gap:16px;flex-wrap:wrap;margin-top:8px;font-size:16px}
.row a{color:var(--accent)}
.empty h2{font-size:20px;font-weight:600;margin:0 0 16px}
.empty p{color:var(--mut);font-size:16px}
.headline{font-size:32px;font-weight:600;color:var(--accent);line-height:1.1}
.headline-label{font-size:12px;color:var(--mut);margin:4px 0 0}
.figures{display:flex;gap:32px;flex-wrap:wrap;margin-top:24px}
.figure-value{font-size:20px;font-weight:600;font-variant-numeric:tabular-nums}
.figure-label{font-size:12px;color:var(--mut);margin-top:4px}
/* Recovery copy, not a chip: LESSON_CSS defines no `.status` rule, so this
   one declaration styles the reader's degraded-lesson and style-warning
   notice. A learner who cannot read the failure sentence cannot recover from
   it, so it takes the 16px floor alongside `.state` (14-UI-SPEC §4.2). A
   genuinely compact status chip uses `.step-status`, which is 12px. */
.status{font-size:16px;color:var(--mut);margin:16px 0 0}
table{width:100%;border-collapse:collapse;margin:8px 0 16px}
th,td{text-align:left;padding:8px;border-bottom:1px solid var(--line);
  font-size:16px;overflow-wrap:anywhere;vertical-align:top}
th{font-size:12px;color:var(--mut);font-weight:600}
.table-wrap{overflow-x:auto;min-width:0}
code,pre{font-family:var(--font-code);
  overflow-wrap:anywhere}
pre{background:var(--chip);border:1px solid var(--line);border-radius:8px;
  padding:12px;overflow-x:auto;max-width:100%}
@media (max-width:767px){
  .surface{padding:16px 16px 56px}
  h1{font-size:20px}
  .actions button{width:100%}
  .course-nav-desktop{display:none}
  .course-nav-mobile{display:block;margin:0 0 var(--space-4)}
  .course-nav-mobile ul{list-style:none;margin:0;padding:var(--space-2) 0 0}
  .course-nav-mobile a{display:flex;align-items:center;min-height:44px}
}
@media (prefers-reduced-motion:reduce){
  *{transition:none!important}
  html{scroll-behavior:auto!important}
}
"""


# ---- 17A-03: the accessible component primitive layer ---------------------
#
# One CSS block for every 16B/16C component primitive below. It is appended to
# SHARED_CSS at the bottom of this section, so every surface that composes
# `surface_shell` already carries it and no component ships a second sheet.
#
# What this block may and may not do, and why each bound is mechanical rather
# than documentary:
#
#   - Colour comes from `surfaces/theme.py` by token name only. There is no
#     hex, rgb or hsl literal here. `--accent` appears exactly once, on the
#     walkthrough callout border, which is the one use 17A-UI-SPEC's component
#     table assigns it. A status chip, a job outcome or a fill-state block
#     that reached for it would widen the reserve, so none of them do: the
#     fill block is `--ink`, and every chip is its own semantic token.
#   - Spacing comes from `--space-*`, panel padding and list gaps from
#     `--density-*`, radius from `--r-*`. No raw length is introduced except
#     the two glyph box sizes (the fill block and the chip dot), which are
#     decorative marks rather than spacing and are not interactive targets.
#   - `min-height` on an interactive control is a literal 44px and is never
#     sized from a density token, so compact density cannot shrink a target.
#   - NO TRUNCATION RULE ANYWHERE. Neither `white-space` nor the overflow
#     ellipsis property appears in this block, and three shipped fixtures scan
#     the served bytes for exactly those two strings. The one place
#     17A-UI-SPEC does authorise a clipped label (Direction-Neutral #8, the
#     decorative concept-map node) is therefore clipped in PYTHON, in
#     `_clip_node_label`, with the full label kept untouched in the textual
#     adjacency list that is the accessible form.
#
# Every size below names a frozen token rather than restating its value, and
# that was not true when this block was first written. Recorded because the
# order matters: plan 17A-02 froze five names, and plan 17A-03 then found it
# could not USE them, because `tests/stylesheet_roundtrip.py:size_problems`
# demanded a literal px and rejected `font-size:var(--text-xs)` while
# accepting the `12px` it stands for. A freeze nothing may consume is a
# documentation exercise, so the gate learned to resolve the five frozen names
# to their values, and only those five: any other `var(...)` in a `font-size`
# still fails, which is what keeps a sixth size out.
#
# The `font` shorthand remains a hole in that gate, since a var-valued size
# makes its `size_at` -1 and the whole shorthand goes unchecked. Nothing here
# uses the shorthand, and the hole is recorded rather than exploited.
PRIMITIVE_CSS = r"""
.ib-list{list-style:none;margin:0;padding:0;display:flex;
  flex-direction:column;gap:var(--density-list-gap)}
.ib-card{background:var(--card);border:1px solid var(--line);
  border-radius:var(--r-2);padding:var(--density-card-pad)}
.ib-group{margin:0 0 var(--space-4)}
.ib-group-head{font-size:var(--text-body);font-weight:600;line-height:1.4;
  margin:0 0 var(--space-2)}
.ib-name{font-family:var(--font-paper);font-size:var(--text-body);font-weight:600;
  line-height:1.4;margin:0;overflow-wrap:anywhere}
.ib-meta{font-family:var(--font-ledger);font-size:var(--text-xs);line-height:1.4;
  color:var(--mut);margin:var(--space-1) 0 0;overflow-wrap:anywhere}
.ib-body{font-size:var(--text-body);line-height:1.5;margin:var(--space-2) 0 0;
  max-width:var(--measure-prose);overflow-wrap:anywhere}
.ib-empty{font-size:var(--text-body);line-height:1.5;color:var(--mut);margin:0}
.ib-slow{font-family:var(--font-ledger);font-size:var(--text-body);line-height:1.5;
  color:var(--mut);margin:0}
.ib-notice{border:1px solid var(--line);border-radius:var(--r-2);
  padding:var(--space-2) var(--space-3);margin:0 0 var(--space-3);
  font-family:var(--font-ledger);font-size:var(--text-body);line-height:1.5;
  overflow-wrap:anywhere}
.ib-notice-label{font-weight:600;margin-inline-end:var(--space-1)}
.ib-notice-ok{color:var(--ok);background:var(--ok-bg);border-color:var(--ok)}
.ib-notice-bad{color:var(--bad);background:var(--bad-bg);
  border-color:var(--bad)}
.ib-notice-warn{color:var(--warn);background:var(--warn-bg);
  border-color:var(--warn)}
.ib-notice-unknown{color:var(--unknown);background:var(--unknown-bg);
  border-color:var(--unknown)}
.ib-notice-pending{color:var(--pending);background:var(--pending-bg);
  border-color:var(--pending)}
.ib-chips{list-style:none;display:flex;flex-wrap:wrap;
  gap:var(--density-list-gap);margin:var(--space-2) 0 0;padding:0}
.ib-chip{display:inline-flex;align-items:center;gap:var(--space-1);
  font-family:var(--font-ledger);font-size:var(--text-xs);line-height:1.4;
  background:var(--chip);color:var(--ink);border:1px solid var(--line);
  border-inline-start:3px solid var(--edge);border-radius:var(--r-1);
  padding:var(--space-1) var(--space-2);overflow-wrap:anywhere}
.ib-chip .ib-dot{width:8px;height:8px;border-radius:var(--r-1);
  background:var(--edge);flex:none}
.ib-chip-ok{border-inline-start-color:var(--ok)}
.ib-chip-ok .ib-dot{background:var(--ok)}
.ib-chip-bad{border-inline-start-color:var(--bad)}
.ib-chip-bad .ib-dot{background:var(--bad)}
.ib-chip-warn{border-inline-start-color:var(--warn)}
.ib-chip-warn .ib-dot{background:var(--warn)}
.ib-chip-unknown{border-inline-start-color:var(--unknown)}
.ib-chip-unknown .ib-dot{background:var(--unknown)}
.ib-chip-pending{border-inline-start-color:var(--pending)}
.ib-chip-pending .ib-dot{background:var(--pending)}
.ib-fill-row{display:flex;flex-wrap:wrap;align-items:center;
  gap:var(--space-2);margin:var(--space-2) 0 0}
.ib-fill{display:inline-flex;gap:var(--space-1);align-items:center}
.ib-fill i{display:inline-block;width:12px;height:12px;
  border-radius:var(--r-1);border:1px solid var(--edge);background:transparent}
.ib-fill i.on{background:var(--ink);border-color:var(--ink)}
.ib-fill-legend{font-family:var(--font-ledger);font-size:var(--text-xs);line-height:1.4;
  color:var(--mut)}
.ib-path{font-family:var(--font-code);font-size:var(--text-xs);line-height:1.5;
  overflow-wrap:anywhere}
.ib-setting-row{display:flex;flex-wrap:wrap;gap:var(--space-1) var(--space-3);
  padding:var(--space-2) 0}
.ib-setting-label{font-size:var(--text-body);line-height:1.5}
.ib-settings-group + .ib-settings-group{border-top:1px solid var(--line);
  margin-top:var(--space-3);padding-top:var(--space-3)}
.ib-walkthrough{border:1px solid var(--accent);border-radius:var(--r-3);
  background:var(--card);padding:var(--density-card-pad);
  margin:0 0 var(--space-3)}
.ib-walkthrough p{max-width:var(--measure-prose)}
.ib-activity-frame{margin:var(--space-4) 0}
.ib-activity-facts{display:flex;flex-wrap:wrap;gap:var(--space-2) var(--space-4);margin:0 0 var(--space-3)}
.ib-activity-facts div{min-width:10rem}.ib-activity-facts dt{font-size:12px;color:var(--mut)}
.ib-activity-facts dd{margin:2px 0 0;font-size:16px}.ib-course-identity p,.ib-source{color:var(--mut)}
.ib-profile-trajectory-deck .ib-activity-frame{border-top:2px solid var(--edge);padding-top:var(--space-3)}
.ib-profile-field-guide .ib-source{border-inline-start:2px solid var(--line);padding-inline-start:var(--space-3)}
.ib-profile-guide-main{max-width:var(--measure-prose)}
.ib-profile-deck-task{border:1px solid var(--edge);border-radius:var(--r-2);
  padding:var(--space-3);background:var(--card)}
.ib-profile-deck-task .actions{margin:var(--space-3) 0 0}
.ib-capture textarea{display:block;width:100%;min-width:0;min-height:44px;
  max-height:calc(var(--text-body) * 1.5 * 8 + var(--space-3));overflow-y:auto;
  font-family:var(--font-paper);font-size:var(--text-body);line-height:1.5;
  color:var(--ink);background:var(--bg);border:1px solid var(--edge);
  border-radius:var(--r-1);padding:var(--space-2)}
.ib-capture label{display:block;font-size:var(--text-body);font-weight:600;
  line-height:1.4;margin:var(--space-2) 0 var(--space-1)}
.ib-stage{border:1px solid var(--line);border-radius:var(--r-3);
  padding:var(--density-card-pad);margin:0 0 var(--space-3)}
.ib-nodes{display:flex;flex-wrap:wrap;gap:var(--density-list-gap);
  margin:var(--space-2) 0 0;padding:0;list-style:none}
.ib-node{border:1px solid var(--line);border-radius:var(--r-1);
  padding:var(--space-1) var(--space-2);background:var(--chip);
  font-family:var(--font-ledger);font-size:var(--text-xs);line-height:1.4}
.ib-diff{margin:0 0 var(--space-3)}
.ib-diff pre{margin:var(--space-2) 0 0}
"""

# One sheet, not two. Every existing caller of `surface_shell` emits
# `SHARED_CSS`, so folding the primitive block in here is what makes a
# primitive usable from any surface without that surface shipping CSS of its
# own. `PRIMITIVE_CSS` stays a separate name because
# `tests/stylesheet_roundtrip.py` collects every module-level `*_CSS` constant
# by name, and a named block is what a failure message can point at.
SHARED_CSS = SHARED_CSS + PRIMITIVE_CSS

# The accepted learner-facing product identity. This stays in the shared shell
# so the normal shelf, course, reading, practice, evidence, review, and recovery
# routes remain one application instead of becoming a detached theme demo.
# It changes presentation only. Theme colors still come from theme.py, and all
# behavior and authority remain with the existing route and runtime owners.
PRODUCT_CSS = r"""
body{margin:0;background:var(--paper);color:var(--product-ink)}
.product-shell{min-height:100vh;display:grid;grid-template-columns:224px 1fr}
.product-sidebar{position:sticky;top:0;height:100vh;border-right:1px solid var(--product-line);
  padding:var(--space-5) var(--space-4);display:flex;flex-direction:column}
.standalone-product-nav{position:fixed;left:0;z-index:20;width:224px;background:var(--paper)}
.wrap:has(.standalone-product-nav){margin-left:max(224px,calc((100vw - 1040px) / 2 + 112px))}
.product-brand{font-family:var(--font-chrome);font-size:var(--text-heading);font-weight:600;
  color:var(--product-ink);display:flex;gap:var(--space-2);align-items:center}
.product-brand:before{content:"";width:22px;height:26px;border-radius:4px 9px 4px 4px;
  background:var(--product-ink)}
.product-tag{font-size:var(--text-xs);letter-spacing:.14em;text-transform:uppercase;
  color:var(--product-muted);margin:var(--space-2) 0 var(--space-6)}
.product-nav{display:grid;gap:var(--space-2)}
.product-nav a{min-height:44px;padding:10px 12px;border-radius:var(--r-1);
  color:var(--product-muted);font-weight:400}
.product-nav a[aria-current]{background:var(--product-active);color:var(--product-ink);font-weight:600}
.product-local{margin-top:auto;border-top:1px solid var(--product-line);padding-top:var(--space-3);
  color:var(--product-muted);font-size:var(--text-xs)}
.product-local:before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;
  background:var(--product-green);margin-right:var(--space-2)}
.product-workspace{min-width:0}
.product-topbar{height:82px;border-bottom:1px solid var(--product-line);padding:0 var(--space-6);
  display:flex;align-items:center;justify-content:space-between;color:var(--product-muted);
  font-size:var(--text-xs)}
.product-topbar span:last-child{border:1px solid var(--product-line);border-radius:999px;
  padding:var(--space-1) var(--space-2)}
.surface,.surface.wide{max-width:1040px;margin:0 auto;padding:var(--space-6) var(--space-6) var(--space-7)}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;
  clip:rect(0,0,0,0);border:0}
.surface:has(.desk-heading)>h1{position:absolute;width:1px;height:1px;padding:0;
  margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}
h1,h2{font-family:var(--font-paper);font-weight:400;letter-spacing:-.02em}
h1{font-size:var(--text-display)}h2{font-size:var(--text-display)}
.app-nav{display:none}
button.go,a.go{border-radius:var(--r-1);padding-inline:var(--space-4)}
button.go.primary,a.go.primary{background:var(--product-ink);border-color:var(--product-ink);
  color:var(--paper)}
.desk-heading{display:flex;justify-content:space-between;align-items:flex-start;gap:var(--space-4);
  margin-bottom:var(--space-5)}
.desk-heading h2{margin:var(--space-2) 0}.desk-heading p{color:var(--product-muted)}
.desk-eyebrow{font-family:var(--font-ledger);font-size:var(--text-xs);
  letter-spacing:.14em;text-transform:uppercase;color:var(--product-muted)}
.desk-hero{position:relative;overflow:hidden;min-height:350px;margin-bottom:var(--space-5);
  border:1px solid var(--product-line);border-radius:var(--r-2);background:var(--product-wash);
  display:grid;grid-template-columns:1.05fr .95fr;align-items:stretch}
.desk-hero-copy{padding:var(--space-5);align-self:center;position:relative;z-index:1}
.desk-hero h2{font-size:var(--text-display);margin:var(--space-3) 0 var(--space-2)}
.desk-hero p{color:var(--product-muted)}
.desk-hero .resume-cue{font-size:var(--text-xs);margin-top:var(--space-3)}
.desk-plant{width:100%;height:100%;min-height:310px;color:var(--product-green)}
.desk-below{display:grid;grid-template-columns:1.55fr 1fr;gap:var(--space-6)}
.desk-section-title{display:flex;justify-content:space-between;border-bottom:1px solid var(--product-line);
  padding-bottom:var(--space-3)}
.desk-section-title h2{font-family:var(--font-chrome);font-size:var(--text-body);
  font-weight:600;margin:0}.desk-section-title span{font-size:var(--text-xs);color:var(--product-muted)}
.course-shelf{display:block}
.course-card{display:grid;grid-template-columns:48px 1fr auto;gap:var(--space-3);
  align-items:center;padding:var(--space-4) 0;border-bottom:1px solid var(--product-line)}
.course-card:before{content:"";width:48px;height:64px;grid-row:1/5;border-radius:3px 7px 7px 3px;
  background:var(--product-green);box-shadow:inset 6px 0 color-mix(in srgb,var(--paper) 18%,transparent)}
.course-card h2{font-family:var(--font-chrome);font-size:var(--text-body);font-weight:600;
  margin:0;grid-column:2}.course-card .chip{font-size:var(--text-xs);color:var(--product-muted);
  grid-column:2}.course-card .resume-cue{font-size:var(--text-xs);color:var(--product-muted);
  grid-column:2;margin:0}.course-card .actions{grid-column:3;grid-row:1/4;margin:0}
.course-card .actions a.go{background:transparent;border:0;color:var(--product-ink);
  padding:var(--space-2);min-width:44px}
.course-card .actions .secondary{display:none}.course-card .sample-note,.course-card form{display:none}
.desk-next{padding:var(--space-4) 0}.desk-next h3{font-size:var(--text-body);margin:var(--space-2) 0}
.desk-next p{font-size:var(--text-xs);color:var(--product-muted)}
.course-areas ul{display:flex;flex-wrap:wrap;gap:var(--space-2) var(--space-4);
  list-style:none;padding:0;margin:0}
.course-areas{border-bottom:1px solid var(--product-line);padding-bottom:var(--space-3);
  margin-bottom:var(--space-5)}
.course-areas a{color:var(--product-ink)}
.course-areas a[aria-current]{background:var(--product-ink);color:var(--paper);text-decoration:underline;
  text-underline-offset:8px;text-decoration-thickness:2px}
.course-rows{list-style:none;padding:0;margin:0}
.course-rows .row{padding:var(--space-4) 0;border-bottom:1px solid var(--product-line)}
.row-head{display:flex;flex-wrap:wrap;justify-content:space-between;gap:var(--space-2)}
.row-note,.area-lead{color:var(--product-muted)}
.vf-diff,.ib-diff{border-radius:var(--r-2);overflow:auto}
@media(max-width:767px){
  .product-shell{display:block}.product-sidebar{position:fixed;z-index:20;top:auto;bottom:0;
    width:100%;height:66px;padding:0 var(--space-2);border:0;border-top:1px solid var(--product-line);
    background:var(--paper)}
  .product-brand,.product-tag,.product-local{display:none}.product-nav{height:100%;display:flex;
    justify-content:space-around}.product-nav a{display:grid;place-items:center;padding:var(--space-2);
    font-size:var(--text-xs);background:transparent!important}
  .product-topbar{height:64px;padding:0 var(--space-3)}
  .wrap:has(.standalone-product-nav){margin-left:auto}
  .ib-palette-open{display:none}
  .surface,.surface.wide{padding:var(--space-4) var(--space-3) calc(var(--space-7) + 66px)}
  .desk-heading{gap:var(--space-2)}
  .desk-hero{min-height:0;grid-template-columns:1fr}
  .desk-plant{height:180px;min-height:0;grid-row:1}
  .desk-hero-copy{padding:var(--space-4);grid-row:2}
  .desk-below{grid-template-columns:1fr;gap:var(--space-5)}
  .course-card{grid-template-columns:48px 1fr auto}
}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;
  transition-duration:0s!important;animation-duration:0s!important}}
"""


def product_theme_css():
    """The accepted fixed learner palette, separate from admin theme preview."""
    return """
:root{--paper:#f6f5f0;--product-ink:#243a44;--product-muted:#65716f;
  --product-line:#dcded4;--product-green:#365e4c;--product-wash:#e9eddf;
  --product-active:#e6eade;--bg:#f6f5f0;--card:#fffef9;--ink:#243a44;
  --mut:#65716f;--line:#dcded4;--accent:#365e4c;--edge:#68805b;
  --chip:#e6eade;--ok:#365e4c;--ok-bg:#e9eddf;--warn:#75531f;
  --warn-bg:#f3ecdb;--bad:#7f3b32;--bad-bg:#f3e9e4;
  --unknown:#58636a;--unknown-bg:#eceeea;--pending:#705b2d;
  --pending-bg:#f3ecdb}
"""


def _product_sidebar(current="courses", standalone=False):
    """One product navigation with an honest active destination."""
    links = []
    for key, href, label in (("desk", "/", "Your desk"),
                             ("courses", "/courses", "Courses"),
                             ("activity", "/activity", "Activity"),
                             ("settings", "/settings", "Settings")):
        active = ' aria-current="page"' if key == current else ""
        links.append('<a href="%s"%s>%s</a>' % (href, active, label))
    extra = " standalone-product-nav" if standalone else ""
    return ('<aside class="product-sidebar%s">'
            '<a class="product-brand" href="/">itembank</a>'
            '<p class="product-tag">A place for understanding</p>'
            '<nav class="product-nav" aria-label="Main navigation">%s</nav>'
            '<p class="product-local">On this device</p></aside>'
            % (extra, "".join(links)))


def product_frame_open(title):
    """Open the shared responsive learner frame for standalone activities."""
    return ('<div class="product-shell">%s'
            '<div class="product-workspace"><header class="product-topbar">'
            '<span>Your workspace / %s</span><span>Local</span></header>'
            % (_product_sidebar(), esc(title)))


PRODUCT_FRAME_CLOSE = "</div></div>"


def standalone_product_nav():
    return _product_sidebar(standalone=True)

def esc(value):
    """Escape one presentation value for HTML text."""
    return html.escape("" if value is None else str(value))


def script_safe_json(value):
    """JSON that cannot close a page's `<script>` data element (T-04-17):
    escape `<`, `>`, `&` and the JS line separators U+2028/U+2029 so bank
    prose can never terminate the script element or splice executable
    markup. Every surface that embeds boot/item payloads into a `<script>`
    data element routes them through this one helper (study, quiz, day);
    rendered text is escaped again by each surface's own HTML escaper, and
    this only guarantees the embedded data element itself stays inert.
    """
    return (json.dumps(value, ensure_ascii=False)
            .replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def _action_markup(action, primary=False):
    """One native action from a behavior-free dict: `{"label"}` renders a
    button, `{"label", "href"}` a link. Exactly one element per teaching
    step may carry `data-action-primary`; every other action is
    `data-action-secondary` and can never acquire the primary marker.
    """
    label = action.get("label", "")
    marker = "data-action-primary" if primary else "data-action-secondary"
    cls = "go primary" if primary else "go"
    href = action.get("href")
    if href:
        return '<a class="%s" %s href="%s">%s</a>' % (
            esc(cls), marker, esc(href), esc(label))
    return '<button type="button" class="%s" %s>%s</button>' % (
        esc(cls), marker, esc(label))


def surface_shell(title, body, theme_css="", back=None, wide=False,
                  context=None, noscript=None, extra_css="", doc_title=None,
                  tail="", classes="", palette=False, presentation_profile="",
                  product=True):
    """The one shared semantic document shell: doctype, generated theme
    block plus shared design-token CSS, an optional sticky context line,
    an optional back link, a single `h1`, a `main` landmark holding `body`,
    and an optional `<noscript>` fallback note. `wide=True` uses the 800px
    quiz measure; the default is the 720px reading column.

    The four trailing arguments exist so a surface can join this shell
    instead of assembling a second one, which is the whole point of plan
    17A-02: a token freeze that a served route bypasses is not a freeze.
    Each defaults to today's behaviour, so no existing caller changes.

    `palette=True` adds the command palette's own sheet and its overlay
    after `main`. Off by default, because the palette reaches routes and a
    document with no server behind it (the offline build, an exported page)
    must not offer them.

    `extra_css` is emitted AFTER `SHARED_CSS`, so a surface's own sheet still
    wins the cascade it won when it owned the whole document. `doc_title`
    separates the `<title>` element from the `h1` for a route whose two
    headings legitimately differ. `tail` is markup placed after `main` and
    the noscript note, which is where a boot script belongs. `classes` adds
    to the shell wrapper, which is how a route opts into compact density.
    """
    # Application pages supply their stable app navigation as the first body
    # element. Promote it into the shell header so the product frame leads the
    # page, while standalone exports and offline pages keep their old shape.
    app_header = ""
    if body.startswith('<nav class="app-nav"'):
        nav_end = body.find("</nav>")
        if nav_end >= 0:
            nav_end += len("</nav>")
            app_header, body = body[:nav_end], body[nav_end:]
    parts = []
    if context:
        parts.append(context_line(context))
    if back:
        parts.append('<p class="back"><a href="%s">&larr; %s</a></p>'
                     % (esc(back.get("href", "/")),
                        esc(back.get("label", "back"))))
    parts.append("<h1>%s</h1>" % esc(title))
    ns = ""
    if noscript is not None:
        ns = "<noscript><p>%s</p></noscript>" % esc(noscript)
    head_title = title if doc_title is None else doc_title
    sheet = SHARED_CSS + (PRODUCT_CSS if product else "")
    if extra_css:
        sheet = sheet + "\n" + extra_css
    if palette:
        from surfaces import palette as palette_surface
        sheet = sheet + "\n" + palette_surface.PALETTE_CSS
        tail = tail + palette_surface.palette_markup()
    product_theme = product_theme_css() if product else ""
    style = "<style>\n%s\n%s\n%s\n</style>" % (theme_css, product_theme, sheet)
    cls = "surface" + (" wide" if wide else "")
    if classes:
        cls = cls + " " + classes
    if presentation_profile in PROFILE_RECIPES:
        cls += " ib-profile ib-profile-%s" % presentation_profile
    profile_attr = (' data-presentation-profile="%s"' % esc(presentation_profile)
                    if presentation_profile else "")
    if product:
        current = ({"Your desk": "desk", "Courses": "courses",
                    "Activity": "activity", "Settings": "settings"}
                   .get(head_title, "courses"))
        product_sidebar = _product_sidebar(current)
        return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
                "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
                "<title>%s</title>%s</head><body><div class=\"product-shell\">%s"
                '<div class="product-workspace"><header class="product-topbar">'
                '<span>Your workspace / %s</span><span>Local</span></header>'
                '<div class="%s"%s>%s%s<main>%s</main>%s%s'
                '</div></div></div></body></html>'
                % (esc(head_title), style, product_sidebar, esc(head_title), esc(cls),
                   profile_attr, app_header, "\n".join(parts), body, ns, tail))
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>%s</title>%s</head><body><div class=\"%s\"%s>%s%s<main>%s"
            "</main>%s%s</div></body></html>"
            % (esc(head_title), style, esc(cls), profile_attr, app_header,
               "\n".join(parts), body, ns, tail))


def context_line(parts, label="Context"):
    """One sticky, labelled semantic context region (a nav, not a heading),
    carrying the stable `data-surface-context` enhancement hook.
    """
    items = "".join('<span class="cx">%s</span>' % esc(p) for p in parts)
    return ('<nav class="context-line" data-surface-context aria-label="%s">%s'
            "</nav>" % (esc(label), items))


def details_section(summary, body="", data=None, classes=""):
    """One native disclosure whose summary names its content, with optional
    stable `data-*` hooks for integration tests.
    """
    attrs = "".join(' data-%s="%s"' % (esc(k), esc(v))
                    for k, v in (data or {}).items())
    cls = "details-section"
    if classes:
        cls += " " + classes
    return ('<details class="%s"%s><summary>%s</summary>%s</details>'
            % (esc(cls), attrs, esc(summary), body))


def state_panel(state):
    """One persistent polite status region (`role=status`) with optional
    recovery actions -- the shared loading/error/empty/unavailable surface.
    """
    kind = state.get("kind", "neutral")
    text = state.get("status", "")
    actions = "".join(_action_markup(a) for a in state.get("actions", ()))
    return ('<div class="state state-%s" data-state="%s" role="status" '
            'aria-live="polite"><p class="state-text">%s</p>%s</div>'
            % (esc(kind), esc(kind), esc(text), actions))


def teaching_step(label="", prompt="", body="", status="", action=None,
                  details=(), secondary=()):
    """One concise teaching step: a short label/prompt, body prose, a
    persistent immediate-status slot, optional progressive details, and
    exactly one primary next action with optional secondary actions. The
    adapter supplies presentation structure only -- it never decides the
    next step, sequences anything, or renders behavior.
    """
    h = ['<article class="step" data-presentation-step>']
    if label:
        # h2, not h3: the shell's single h1 is followed directly by the step
        # label, and the a11y contract forbids skipping heading levels.
        h.append('<h2 class="step-label">%s</h2>' % esc(label))
    if prompt:
        h.append('<p class="step-prompt">%s</p>' % esc(prompt))
    if body:
        h.append('<div class="step-body">%s</div>' % esc(body))
    if status:
        h.append('<div class="step-status" role="status" aria-live="polite">%s'
                 "</div>" % esc(status))
    for d in details or ():
        h.append(details_section(d.get("summary", ""), d.get("body", "")))
    acts = []
    if action:
        acts.append(_action_markup(action, primary=True))
    for a in secondary or ():
        acts.append(_action_markup(a))
    if acts:
        h.append('<div class="actions">%s</div>' % "".join(acts))
    h.append("</article>")
    return "".join(h)


def default_adapter(view):
    """The polished low-chrome default adapter: one behavior-free view
    dictionary to semantic HTML. Reads only presentation labels, content,
    state, and actions; an optional `theme_css` string in the view supplies
    the generated palette block (consumed by name, never authored here).
    """
    parts = []
    if view.get("context"):
        parts.append(context_line(view["context"]))
    step = view.get("step")
    if isinstance(step, dict):
        parts.append(teaching_step(**step))
    state = view.get("state")
    if isinstance(state, dict):
        parts.append(state_panel(state))
    return surface_shell(view.get("title", "itembank"), "\n".join(parts),
                         theme_css=view.get("theme_css", ""),
                         back=view.get("back"),
                         wide=bool(view.get("wide")),
                         noscript=view.get("noscript"))


def render_surface(view, adapter=None):
    """Render one behavior-free view dictionary to semantic HTML through
    `adapter` (the polished default when none is given). An alternate
    adapter receives the exact same view data and may produce any HTML, but
    it can never own scoring, persistence, routing, scheduling, or evidence
    decisions -- the view carries none of those objects by contract.
    """
    if adapter is None:
        adapter = default_adapter
    return adapter(view)


# ---- Phase 20 semantic presentation seam ---------------------------------
# These primitives carry learner-facing meaning only. They do not receive a
# scorer, a writable session, a key, or an evidence path.
ACTIVITY_PURPOSE_LABELS = {
    "diagnostic": "Diagnostic", "practice": "Practice",
    "remediation": "Remediation", "exam": "Formal assessment",
    "drill": "Drill", "study": "Deliberate review",
}
RESPONSE_FORMAT_LABELS = {
    "mc": "Single choice", "multi": "Multiple choice",
    "table": "Table response", "build": "Build response",
    "dnd": "Ordering or matching", "short": "Short response",
    "visual": "Visual interaction", "check": "Code check",
    "reading": "Reading", "recall": "Recall and reveal",
}
RESPONSE_FORMAT_INSTRUCTIONS = {
    "mc": "Choose one option.",
    "multi": "Choose the requested number of options.",
    "table": "Choose one category for every row.",
    "build": "Select every step in the order it should happen.",
    "dnd": "Match every row to a category. Dragging is not required.",
    "short": "Write your response. It stays pending until a marker reviews it.",
    "visual": "Use the visual or its adjacent keyboard controls, then submit.",
    "check": "Edit the source, then run the check. The runtime records the verdict.",
    "reading": "Read the passage in order or use its section navigation.",
    "recall": "Recall your answer before revealing the reference answer.",
}
DISCLOSURE_LABELS = {
    "now": "Feedback available now", "completion": "Feedback after completion",
    "locked": "Review locked", "pending": "Pending human review",
}
PROFILE_RECIPES = ("field-guide", "trajectory-deck")

# Phase 20's bounded UI-adapter inventory. These declarations describe how
# existing surfaces consume presentation profiles. They contain no callable
# loader, route, scorer, writer, or package hook.
SURFACE_ADAPTER_VERSION = 1
SURFACE_ADAPTERS = (
    {
        "identity": "question-response", "version": SURFACE_ADAPTER_VERSION,
        "roles": ("learner",), "operations": ("read", "respond"),
        "modes": PROFILE_RECIPES,
        "input": "runtime.public_item plus runtime-owned session state",
        "fallback": "semantic HTML and native controls",
        "unavailable": "name the unavailable interaction and retain static instructions",
        "migration": "presentation-only. Canonical item and session schemas stay unchanged",
        "tests": ("presentation_profiles_roundtrip.py", "component_primitives_roundtrip.py"),
        "removal_recovery": "render the field-guide semantic fallback without changing session or evidence",
        "disposition": "shared-profile-framing",
    },
    {
        "identity": "course-areas", "version": SURFACE_ADAPTER_VERSION,
        "roles": ("learner", "reviewer"),
        "operations": ("overview", "learn", "practice", "test", "map", "sources", "build", "agent", "evidence"),
        "modes": PROFILE_RECIPES, "input": "ia course-area read models",
        "fallback": "shared course frame with plain rows and supported links",
        "unavailable": "typed area notice with one supported recovery action",
        "migration": "same course ids, URLs, and operation dispatch",
        "tests": ("ia_route_roundtrip.py", "presentation_profiles_roundtrip.py", "agent_operation_roundtrip.py"),
        "removal_recovery": "retain the route and field-guide frame; never mutate course content",
        "disposition": "shared-profile-framing",
    },
    {
        "identity": "settings", "version": SURFACE_ADAPTER_VERSION,
        "roles": ("learner",), "operations": ("preview", "save", "recover"),
        "modes": PROFILE_RECIPES, "input": "validated local settings",
        "fallback": "visible field-guide preview for an unsupported saved value",
        "unavailable": "no-script copy keeps current saved settings",
        "migration": "missing profile resolves to field-guide without writing",
        "tests": ("settings_roundtrip.py", "presentation_profiles_roundtrip.py"),
        "removal_recovery": "preserve the unknown string until a supported profile is explicitly saved",
        "disposition": "shared-profile-framing",
    },
    {
        "identity": "authoring-export-integrations", "version": SURFACE_ADAPTER_VERSION,
        "roles": ("author", "learner"),
        "operations": ("author", "export", "mcp"),
        "modes": ("current-semantic-output",),
        "input": "existing CLI, API, and generated projection contracts",
        "fallback": "current deterministic output remains unchanged",
        "unavailable": "existing typed command or capability error",
        "migration": "not migrated where profile framing would change non-UI output identity",
        "tests": ("course_ops_roundtrip.py", "mcp_roundtrip.py", "surface_roundtrip.py"),
        "removal_recovery": "remove the declaration only; commands, exports, and tool projection remain unchanged",
        "disposition": "compatibility-adapter-no-profile-rewrite",
    },
)


def surface_adapter_manifest():
    """Return a defensive, JSON-ready copy of the bounded UI declarations."""
    return json.loads(json.dumps({"version": SURFACE_ADAPTER_VERSION,
                                  "external_loader": False,
                                  "adapters": SURFACE_ADAPTERS}))


def semantic_view(application="itembank", course="", location="", purpose="practice",
                  response_type="mc", disclosure="now", position="", content="",
                  next_action=None, status=None, source=""):
    """Build the profile-neutral slice view from public state only."""
    return {"application": application, "course": course, "location": location,
            "purpose": purpose, "response_type": response_type,
            "disclosure": disclosure, "position": position, "content": content,
            "next_action": next_action or {}, "status": status or {}, "source": source}


def activity_frame(view):
    """One learner activity frame. Purpose always precedes response format."""
    purpose = ACTIVITY_PURPOSE_LABELS.get(view.get("purpose"), "Practice")
    response = RESPONSE_FORMAT_LABELS.get(view.get("response_type"), "Response")
    disclosure = DISCLOSURE_LABELS.get(view.get("disclosure"), "Review locked")
    facts = ('<dl class="ib-activity-facts"><div><dt>Purpose</dt><dd>%s</dd></div>'
             '<div><dt>Response format</dt><dd>%s</dd></div>'
             '<div><dt>Disclosure</dt><dd>%s</dd></div>%s</dl>'
             % (esc(purpose), esc(response), esc(disclosure),
                ('<div><dt>Position</dt><dd>%s</dd></div>' % esc(view["position"]))
                if view.get("position") else ""))
    instruction = RESPONSE_FORMAT_INSTRUCTIONS.get(
        view.get("response_type"), "Follow the response instructions below.")
    return ('<section class="ib-activity-frame" aria-label="Learner activity">'
            '%s<p class="ib-activity-instructions">%s</p>%s</section>'
            % (facts, esc(instruction), view.get("content", "")))


def render_profile(view, profile="field-guide"):
    """Render either recipe over identical semantic state and action data."""
    active = profile if profile in PROFILE_RECIPES else "field-guide"
    identity = ('<header class="ib-course-identity"><p>Application: %s</p><h1>%s</h1>'
                '<p>%s</p></header>' % (esc(view.get("application", "itembank")),
                esc(view.get("course") or view.get("application", "itembank")),
                esc(view.get("location", ""))))
    status = view.get("status") or {}
    notice = status_notice(status.get("text", ""), status.get("kind", "neutral"),
                           status.get("label", "")) if status.get("text") else ""
    source = ('<aside class="ib-source" aria-label="Source">%s</aside>' % esc(view["source"])
              if view.get("source") else "")
    action = _action_markup(view.get("next_action") or {}, primary=True) if (view.get("next_action") or {}).get("label") else ""
    if active == "trajectory-deck":
        task = ('<section class="ib-profile-deck-task" aria-label="Current task">%s%s</section>' %
                (activity_frame(view), ('<div class="actions">%s</div>' % action if action else "")))
        core = identity + task + notice + source
    else:
        core = ('<div class="ib-profile-guide-main">%s%s%s%s</div>' %
                (activity_frame(view), notice, source,
                 ('<div class="actions">%s</div>' % action if action else "")))
        core = identity + core
    return '<div class="ib-profile ib-profile-%s" data-presentation-profile="%s">%s</div>' % (active, active, core)


# ---- 17A-03: component primitives -----------------------------------------
#
# One function per 16B/16C component in 17A-UI-SPEC's Component Styling
# Assignments table, each rendering native semantic HTML from a behavior-free
# dictionary. The same contract as the primitives above holds: no scorer, no
# session path, no evidence writer, no key, no mutation callback ever reaches
# these arguments, and none of them decides anything. A component reads a
# label, a piece of content, a state name, and an action's label and href.
#
# Direction neutrality is the point of the layer. The 17A prototypes differ by
# token and stylesheet overlay only, so a state's MEANING lives in the class
# name and the required text label here, never in a direction's CSS. The
# component fixture asserts that a state row renders its label as text even
# with every stylesheet removed.

# Copy this phase locks (17A-UI-SPEC Copywriting Contract). A caller may pass
# its own surface-specific empty or error copy, which 16B and 16C already
# locked per surface, but it may never re-word one of these control strings.
LOADING_PATTERN = "Loading %s…"
SHOW_ALL_NOTES = "Show all %d notes"
SHOW_EARLIER_ACTIVITY = "Show earlier activity"
SHOW_NEXT_DIFFS = "Show next 10 proposed changes"
REVIEW_EVIDENCE = "Review evidence"
SHOW_ALL_OBJECTIVES = "Show all %d objectives"

# The bounds the Progressive Disclosure Contract fixes. Each is the count of
# rows that stay VISIBLE, never a page size that hides the first rows too.
NOTES_PER_GROUP = 3
ACTIVITY_HISTORY_SHOWN = 5
OBJECTIVE_FILL_SHOWN = 10
DIFF_PAGE_SIZE = 10
FILL_BLOCKS = 5

# Activity's three groups, in the fixed order 17A-UI-SPEC Direction-Neutral #2
# rules: actionable first, then running, then finished.
ACTIVITY_NEEDS_INPUT = "Needs your input"
ACTIVITY_IN_PROGRESS = "In progress"
ACTIVITY_HISTORY = "Completed and failed"

# A decorative concept-map node label is clipped at this many characters
# (Direction-Neutral #8). The accessible adjacency list never clips.
NODE_LABEL_MAX = 18

SEMANTIC_KINDS = ("ok", "bad", "warn", "unknown", "pending")


def semantic_kind(kind):
    """A state name reduced to one of the five semantic tokens, or `neutral`.

    An unrecognised state falls back to neutral rather than to a plausible
    guess: a state whose meaning this layer does not know must not be painted
    as if it did, because colour would then be asserting something the label
    does not say.
    """
    return kind if kind in SEMANTIC_KINDS else "neutral"


def _text(tag, cls, value):
    return "<%s class=\"%s\">%s</%s>" % (tag, esc(cls), esc(value), tag)


def _actions(actions, primary=None):
    """An action row: at most one primary, every other action secondary."""
    out = []
    if primary:
        out.append(_action_markup(primary, primary=True))
    for a in actions or ():
        out.append(_action_markup(a))
    if not out:
        return ""
    return '<div class="actions">%s</div>' % "".join(out)


def _section(cls, label, inner, extra=""):
    return ('<section class="%s" aria-label="%s"%s>%s</section>'
            % (esc(cls), esc(label), extra, inner))


def _fallback(state, label, empty_text, has_rows):
    """The shared zero/loading/error head every list primitive shares.

    Returns rendered markup when the list must NOT render its rows, and `None`
    when it must. Three rules from 17A-UI-SPEC live here rather than in each
    caller, because a rule restated per component is a rule that drifts:
    a slow read shows a stated loading line and never a wordless spinner; a
    failed read shows the surface's own degraded copy; and an empty section
    renders its empty copy directly, never a disclosure control with nothing
    behind it.
    """
    state = state or {}
    if state.get("kind") == "loading":
        return _section("ib-state", label, loading_line(state.get("of", label)))
    if state.get("kind") in ("error", "bad", "warn", "unavailable"):
        return _section("ib-state", label, state_panel(
            {"kind": "bad" if state.get("kind") in ("error", "bad") else "warn",
             "status": state.get("status", ""),
             "actions": state.get("actions", ())}))
    if not has_rows:
        return _section("ib-state", label,
                        _text("p", "ib-empty", empty_text))
    return None


def loading_line(content_name):
    """The one slow-read state this phase authorises: a stated Ledger-voice
    line, announced once, never a wordless spinner.

    The class is `ib-slow` rather than the obvious name. Every page carries
    `SHARED_CSS`, and `daemon_roundtrip.check_unreachable_runtime_band` fails
    a served page whose bytes contain the substring "loading" anywhere,
    because a degraded band that appears to be working on something is a lie
    about the runtime's state. A class name is bytes on that page, so the
    class had to lose the word even though the learner-visible copy keeps it.
    """
    return ('<p class="ib-slow" role="status" aria-live="polite">%s</p>'
            % esc(LOADING_PATTERN % content_name))


def status_notice(text, kind="neutral", label="", urgent=False):
    """An inline banner, never a card and never collapsible: a status notice
    that has to be expanded before it can be read has failed at the one job it
    has. `urgent=True` uses `role=alert` for a state that interrupts; every
    other severity is a polite `role=status`.
    """
    k = semantic_kind(kind)
    role = "alert" if urgent else "status"
    live = "" if urgent else ' aria-live="polite"'
    head = _text("span", "ib-notice-label", label) if label else ""
    return ('<p class="ib-notice ib-notice-%s" data-state="%s" role="%s"%s>'
            "%s%s</p>" % (esc(k), esc(k), role, live, head, esc(text)))


def anchor_chip(label, kind="unknown"):
    """A small state chip: a token-coloured start border and dot plus a text
    label that is always present and always sufficient on its own. Never an
    icon-only chip, and never the full semantic background fill, which is a
    banner's intensity and would make a list of chips unreadable.
    """
    k = semantic_kind(kind)
    return ('<span class="ib-chip ib-chip-%s" data-state="%s">'
            '<span class="ib-dot" aria-hidden="true"></span>%s</span>'
            % (esc(k), esc(k), esc(label)))


def chip_row(chips, label="State"):
    """A wrapping list of chips. Chips wrap onto new lines and are never
    packed into a special many-chips layout, so the count changes the height
    and nothing else.
    """
    if not chips:
        return ""
    items = "".join('<li>%s</li>' % anchor_chip(c.get("label", ""),
                                                c.get("kind", "unknown"))
                    for c in chips)
    return ('<ul class="ib-chips" aria-label="%s">%s</ul>'
            % (esc(label), items))


def fill_state(filled, legend, total=FILL_BLOCKS, describedby=""):
    """Five discrete blocks, the filled count being the current standing.

    Never a continuous bar and never a probability: the discreteness is the
    anti-precision signal.

    The role is `progressbar` with `aria-valuetext` and deliberately no
    `aria-valuenow`, which is `progress_claims.ARIA_CONTRACT["fill_state"]`
    verbatim: a standing is not a measured quantity on a scale, so a screen
    reader is given the words rather than a number it would read as one.
    Before 2026-09-05 this emitted `role="img"` with a bare `n of N` label,
    which the 17B wave-3 pass recorded as `17B-03 D-06 item 8`.

    `describedby` names an element that already carries the legend text, for
    a list of standings that would otherwise repeat one fixed sentence under
    every row (the ROLLUP screens repeated it seven times). The association
    survives; only the duplication goes. Passing nothing keeps the legend
    beside the blocks, which is what a single standing on its own needs.
    """
    total = max(1, int(total))
    filled = max(0, min(total, int(filled)))
    marks = "".join('<i%s></i>' % (' class="on"' if i < filled else "")
                    for i in range(total))
    described = (' aria-describedby="%s"' % esc(describedby)
                 if describedby else "")
    tail = "" if describedby else _text("span", "ib-fill-legend", legend)
    return ('<p class="ib-fill-row"><span class="ib-fill" role="progressbar" '
            'aria-valuetext="%d of %d blocks filled" aria-label="%d of %d"%s '
            'data-filled="%d">%s</span>%s</p>'
            % (filled, total, filled, total, described, filled, marks, tail))


def course_shelf(courses, label="Courses", empty="", state=None,
                 legend="", legend_id=""):
    """One vertically scrolling list of course cards at any count.

    No pagination control and no load-more: the page scrolls, which is the
    project's own long-content rule, and a locked card renders in its normal
    list position with its own unlock sentence rather than being summarised
    into a count of locked items.

    A card may carry `fill`, an int standing, which renders through the one
    `fill_state` primitive inside the card. That slot is why this signature
    grew: the ROLLUP-MAP screen needed a card with a standing on it and no
    primitive had one, so the 17B wave-3 pass composed the screen out of two
    primitives by hand and recorded the gap as `17B-03 D-06 item 7`. One
    `legend` is rendered once for the whole list and every standing points at
    it, rather than each row repeating the same fixed sentence.
    """
    head = _fallback(state, label, empty, bool(courses))
    if head is not None:
        return head
    shared_legend = ""
    described = ""
    if legend:
        described = legend_id or "ib-shelf-fill-legend"
        shared_legend = ('<p class="ib-fill-legend" id="%s">%s</p>'
                         % (esc(described), esc(legend)))
    rows = []
    for course in courses:
        body = [_text("h2", "ib-name", course.get("name", ""))]
        if course.get("meta"):
            body.append(_text("p", "ib-meta", course["meta"]))
        if course.get("locked"):
            body.append(_text("p", "ib-body", course.get("unlock", "")))
        if course.get("fill") is not None:
            body.append(fill_state(course["fill"], legend,
                                   describedby=described))
        body.append(chip_row(course.get("chips", ()), label="Course state"))
        body.append(_actions(course.get("actions", ()),
                             course.get("action")))
        rows.append('<li class="ib-card">%s</li>' % "".join(body))
    return _section("ib-shelf", label,
                    '<ul class="ib-list">%s</ul>%s'
                    % ("".join(rows), shared_legend))


def _job_rows(jobs):
    rows = []
    for job in jobs:
        body = [_text("h3", "ib-name", job.get("name", ""))]
        # Ledger voice, stated status text only. An in-progress job never
        # renders a percent, because no module on disk produces one and an
        # invented number is the precise failure this contract forbids.
        if job.get("status"):
            body.append(_text("p", "ib-meta", job["status"]))
        body.append(chip_row(job.get("chips", ()), label="Job outcome"))
        rows.append('<li class="ib-card">%s</li>' % "".join(body))
    return '<ul class="ib-list">%s</ul>' % "".join(rows)


def activity_view(needs_input=(), in_progress=(), history=(),
                  label="Activity", empty="", state=None):
    """Job groups in the fixed order: needs-your-input, in progress, then
    completed and failed, each internally reverse-chronological as the caller
    supplies it.

    The actionable group is never collapsed at any count. History past the
    five most recent sits behind one disclosure, and no group heading renders
    over an empty group.
    """
    rows = list(needs_input) + list(in_progress) + list(history)
    head = _fallback(state, label, empty, bool(rows))
    if head is not None:
        return head
    parts = []
    for name, jobs in ((ACTIVITY_NEEDS_INPUT, needs_input),
                       (ACTIVITY_IN_PROGRESS, in_progress)):
        if jobs:
            parts.append('<div class="ib-group">%s%s</div>'
                         % (_text("h2", "ib-group-head", name),
                            _job_rows(jobs)))
    hist = list(history)
    if hist:
        shown, rest = hist[:ACTIVITY_HISTORY_SHOWN], hist[ACTIVITY_HISTORY_SHOWN:]
        inner = _text("h2", "ib-group-head", ACTIVITY_HISTORY) + _job_rows(shown)
        if rest:
            inner += details_section(SHOW_EARLIER_ACTIVITY, _job_rows(rest),
                                     data={"disclosure": "activity-history"})
        parts.append('<div class="ib-group">%s</div>' % inner)
    return _section("ib-activity", label, "".join(parts))


def wrap_path(path):
    """A filesystem path that wraps at its separators and nowhere else.

    A `<wbr>` after each separator gives the browser a legal break point per
    segment; `overflow-wrap:anywhere` in the stylesheet is the fallback for a
    single pathologically long segment. Nothing is clipped and the root is
    never hidden: a learner auditing which roots an agent may read has to be
    able to read the whole path.
    """
    out = esc(path)
    for sep in ("/", "\\"):
        out = out.replace(sep, sep + "<wbr>")
    return '<span class="ib-path">%s</span>' % out


def settings_panel(groups, label="Settings", empty="", state=None):
    """Setting rows grouped with a divider between groups and no card border
    between rows inside one. No group collapses, and a row whose value is a
    path renders through `wrap_path`.
    """
    head = _fallback(state, label, empty, bool(groups))
    if head is not None:
        return head
    parts = []
    for group in groups:
        rows = []
        for row in group.get("rows", ()):
            value = (wrap_path(row["path"]) if row.get("path")
                     else _text("span", "ib-meta", row.get("value", "")))
            rows.append('<div class="ib-setting-row">%s%s</div>'
                        % (_text("span", "ib-setting-label",
                                 row.get("label", "")), value))
        parts.append('<div class="ib-settings-group">%s%s</div>'
                     % (_text("h2", "ib-group-head", group.get("label", "")),
                        "".join(rows)))
    return _section("ib-settings", label, "".join(parts))


def first_launch_walkthrough(step, label="Walkthrough"):
    """One transient callout anchored to the element it explains.

    Copy wraps to as many lines as it needs and the callout's height is
    intrinsic to its content. It is dismissible, which is not a collapse:
    there is no disclosure control and nothing stays hidden behind one.
    """
    body = [_text("h2", "ib-group-head", step.get("label", ""))]
    if step.get("body"):
        body.append(_text("p", "ib-body", step["body"]))
    body.append(_actions(step.get("actions", ()), step.get("action")))
    anchor = ""
    if step.get("anchor"):
        anchor = ' data-anchor="%s"' % esc(step["anchor"])
    return _section("ib-walkthrough", label, "".join(body), extra=anchor)


def note_capture_panel(field_id="note-capture", label="Note",
                       anchor_label="", role_line="", privacy_line="",
                       value="", action=None, actions=(), state=None):
    """The capture field at an anchored block.

    The field grows with its content to roughly eight lines and then scrolls
    inside itself, so the anchored lesson block underneath never gets pushed
    out of view. The role line and the privacy line are never collapsed: what
    a note is and where it goes is not secondary metadata.
    """
    body = [_text("h2", "ib-group-head", label)]
    if anchor_label:
        body.append(_text("p", "ib-meta", anchor_label))
    if role_line:
        body.append(_text("p", "ib-meta", role_line))
    if privacy_line:
        body.append(_text("p", "ib-meta", privacy_line))
    if state:
        body.append(state_panel(state))
    body.append('<label for="%s">%s</label>' % (esc(field_id), esc(label)))
    body.append('<textarea id="%s" name="%s" rows="3">%s</textarea>'
                % (esc(field_id), esc(field_id), esc(value)))
    body.append(_actions(actions, action))
    return _section("ib-capture", label, "".join(body))


def notes_panel_evidence(groups, label="Notes", empty="", state=None):
    """Notes grouped by objective, each group showing its first three rows.

    The group heading and its first three rows are always visible, so the
    objective structure survives first paint; the rest of a group sits behind
    one disclosure named with the group's real total. A group with three or
    fewer notes renders no control at all.
    """
    head = _fallback(state, label, empty,
                     any(g.get("notes") for g in groups or ()))
    if head is not None:
        return head
    parts = []
    for group in groups:
        notes = list(group.get("notes", ()))
        if not notes:
            continue
        rows = []
        for note in notes:
            body = [_text("p", "ib-name", note.get("text", ""))]
            body.append(chip_row(note.get("chips", ()), label="Note state"))
            rows.append('<li class="ib-card">%s</li>' % "".join(body))
        inner = _text("h2", "ib-group-head", group.get("objective", ""))
        inner += '<ul class="ib-list">%s</ul>' % "".join(rows[:NOTES_PER_GROUP])
        if len(rows) > NOTES_PER_GROUP:
            inner += details_section(
                SHOW_ALL_NOTES % len(rows),
                '<ul class="ib-list">%s</ul>' % "".join(rows[NOTES_PER_GROUP:]),
                data={"disclosure": "notes-group"})
        parts.append('<div class="ib-group">%s</div>' % inner)
    return _section("ib-notes", label, "".join(parts))


def strategy_picker(rows, label="Strategies", empty="", state=None):
    """Every available, locked and fallback row, always visible.

    Nothing here collapses: a learner choosing a strategy has to be able to
    see the ones that are not available and read why in the same glance.
    """
    head = _fallback(state, label, empty, bool(rows))
    if head is not None:
        return head
    items = []
    for row in rows:
        body = [_text("h2", "ib-group-head", row.get("name", ""))]
        if row.get("purpose"):
            body.append(_text("p", "ib-body", row["purpose"]))
        if row.get("note"):
            body.append(_text("p", "ib-meta", row["note"]))
        body.append(chip_row(row.get("chips", ()), label="Strategy state"))
        body.append(_actions(row.get("actions", ()), row.get("action")))
        items.append('<li class="ib-card">%s</li>' % "".join(body))
    return _section("ib-strategies", label,
                    '<ul class="ib-list">%s</ul>' % "".join(items))


def progress_comprehension_display(dimensions, objectives=(),
                                   label="Progress", empty="", state=None):
    """The claim dimensions, then per-objective standing.

    Every dimension row renders, always: an aggregate that hides its parts is
    the failure this display exists to prevent, so there is no disclosure over
    the dimension rows at any count. Per-objective standing is unbounded in
    the general case and follows the long-list rule, ten visible and the rest
    behind one named control.
    """
    head = _fallback(state, label, empty,
                     bool(dimensions) or bool(objectives))
    if head is not None:
        return head
    rows = []
    for dim in dimensions or ():
        body = [_text("h2", "ib-group-head", dim.get("label", ""))]
        # `progress_claims.ARIA_CONTRACT` says a claim is a progressbar: a
        # determinate one carries valuemin/valuemax/valuenow and a valuetext
        # holding the whole sentence, because the number alone is not
        # meaningful; an indeterminate one carries the valuetext and no
        # valuenow, and is never an unexplained spinner. Neither was emitted
        # before 2026-09-05 (`17B-03 D-06 item 8`); the visible text is
        # unchanged, so a sighted reader sees exactly what they saw.
        text = dim.get("text", "")
        numerator, denominator = dim.get("value"), dim.get("max")
        determinate = (isinstance(numerator, int)
                       and isinstance(denominator, int)
                       and not isinstance(numerator, bool)
                       and not isinstance(denominator, bool))
        if determinate:
            attrs = (' role="progressbar" aria-valuemin="0" aria-valuemax="%d"'
                     ' aria-valuenow="%d" aria-valuetext="%s"'
                     % (denominator, numerator, esc(text)))
        else:
            attrs = ' role="progressbar" aria-valuetext="%s"' % esc(text)
        body.append('<p class="ib-meta"%s>%s</p>' % (attrs, esc(text)))
        rows.append('<li class="ib-card">%s</li>' % "".join(body))
    parts = ['<ul class="ib-list" data-dimensions="%d">%s</ul>'
             % (len(rows), "".join(rows))] if rows else []
    objectives = list(objectives)
    if objectives:
        # One legend for the whole list, pointed at by every standing, rather
        # than the same fixed sentence under each of seven rows.
        legend_text = ""
        for obj in objectives:
            if obj.get("legend"):
                legend_text = obj["legend"]
                break
        legend_id = "ib-objective-fill-legend" if legend_text else ""

        def block(items):
            out = []
            for obj in items:
                out.append('<li class="ib-card">%s%s</li>'
                           % (_text("h3", "ib-name", obj.get("label", "")),
                              fill_state(obj.get("filled", 0),
                                         obj.get("legend", ""),
                                         describedby=legend_id)))
            return '<ul class="ib-list">%s</ul>' % "".join(out)
        parts.append(block(objectives[:OBJECTIVE_FILL_SHOWN]))
        if legend_id:
            parts.append('<p class="ib-fill-legend" id="%s">%s</p>'
                         % (legend_id, esc(legend_text)))
        if len(objectives) > OBJECTIVE_FILL_SHOWN:
            parts.append(details_section(
                SHOW_ALL_OBJECTIVES % len(objectives),
                block(objectives[OBJECTIVE_FILL_SHOWN:]),
                data={"disclosure": "objective-fill"}))
    return _section("ib-progress", label, "".join(parts))


def _clip_node_label(text):
    """Clip a decorative concept-map node label in Python, not in CSS.

    17A-UI-SPEC authorises clipping exactly here and nowhere else, and the
    stylesheet cannot be the place it happens: three shipped fixtures scan
    served bytes for a truncation rule, because a CSS clip hides text from a
    reader with no indication it did. Clipping in Python keeps the rule to
    this one decorative label, and the adjacency list below keeps the full
    string.
    """
    text = "" if text is None else str(text)
    if len(text) <= NODE_LABEL_MAX:
        return text
    return text[:NODE_LABEL_MAX - 1].rstrip() + "…"


def note_output_trio(mode="notebook", sections=(), nodes=(), adjacency=(),
                     label="Note output", empty="", state=None):
    """Notebook, Cornell, or concept map, all three from one primitive.

    The map's graphic nodes are a secondary projection: their labels clip and
    they are hidden from assistive technology, because the textual adjacency
    structure beneath them is the contract form and it never clips. Removing
    the graphic leaves a complete, operable note.
    """
    head = _fallback(state, label, empty, bool(sections) or bool(adjacency))
    if head is not None:
        return head
    parts = ['<p class="ib-meta" data-mode="%s">%s</p>'
             % (esc(mode), esc(mode))]
    for section in sections or ():
        parts.append('<div class="ib-card">%s%s%s</div>'
                     % (_text("h2", "ib-group-head", section.get("label", "")),
                        _text("p", "ib-body", section.get("body", "")),
                        chip_row(section.get("chips", ()),
                                 label="Note provenance")))
    if nodes:
        parts.append('<ul class="ib-nodes" aria-hidden="true">%s</ul>'
                     % "".join('<li class="ib-node">%s</li>'
                               % esc(_clip_node_label(n))
                               for n in nodes))
    if adjacency:
        rows = "".join("<li>%s</li>" % esc(a) for a in adjacency)
        parts.append('<div class="ib-group">%s<ul>%s</ul></div>'
                     % (_text("h2", "ib-group-head", "Related concepts"),
                        rows))
    return _section("ib-trio", label, "".join(parts))


def evidence_drawer(summary, trail=(), label="Evidence", empty="",
                    state=None):
    """A one-line reason, with the full trail behind a named control.

    The summary line is always readable without expanding anything and reads
    identically whether the trail holds one entry or many, because a count
    there would be an aggregate nobody computed. A drawer with nothing behind
    it renders its empty copy and no control.
    """
    head = _fallback(state, label, empty, bool(trail))
    body = _text("p", "ib-body", summary) if summary else ""
    if head is not None:
        return _section("ib-drawer", label, body + head)
    rows = "".join('<li class="ib-card">%s</li>'
                   % _text("p", "ib-body", entry) for entry in trail)
    return _section("ib-drawer", label,
                    body + details_section(
                        REVIEW_EVIDENCE,
                        '<ul class="ib-list">%s</ul>' % rows,
                        data={"disclosure": "evidence-trail"}))


def diff_review(diffs, offset=0, label="Proposed changes", empty="",
                state=None, more_action=None):
    """Bounded diff review: every shown diff is open, the list is paged.

    A diff is never collapsed, because a reviewer must be able to read what
    they are accepting without an extra click. What is bounded is the working
    set: ten at a time, with one named control for the next ten, and no
    control at all at ten or fewer.
    """
    head = _fallback(state, label, empty, bool(diffs))
    if head is not None:
        return head
    diffs = list(diffs)
    offset = max(0, min(len(diffs), int(offset)))
    window = diffs[offset:offset + DIFF_PAGE_SIZE]
    items = []
    for diff in window:
        body = [_text("h2", "ib-group-head", diff.get("label", ""))]
        if diff.get("finding"):
            body.append(_text("p", "ib-meta", diff["finding"]))
        if diff.get("body"):
            body.append("<pre>%s</pre>" % esc(diff["body"]))
        body.append(chip_row(diff.get("chips", ()), label="Change state"))
        body.append(_actions(diff.get("actions", ()), diff.get("action")))
        items.append('<li class="ib-card ib-diff">%s</li>' % "".join(body))
    inner = '<ul class="ib-list">%s</ul>' % "".join(items)
    if offset + DIFF_PAGE_SIZE < len(diffs):
        nxt = dict(more_action or {})
        nxt["label"] = SHOW_NEXT_DIFFS
        inner += _actions((nxt,))
    return _section("ib-diffs", label, inner)
