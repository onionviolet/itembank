# Why the UI feels generic: diagnosis and proposals (2026-10-07)

Status: research and a reversible prototype. Nothing here is accepted. No product source changed.
Method: ran the daemon on the synthetic journey fixture plus `fixtures/subject_loop_math.md`, screenshotted the desk, courses, a course overview, a reading page, a lesson, and the practice question (before and after a wrong answer) at 1280 and 390 wide, and cycled `look` through classic, editorial, neo and console.

## What the owner said (verbatim, `.planning/USER-VISION.md`)

- Line 2314: "Generic cards and browser-default styling do not meet this bar."
- Line 2344: "Future work should refine this direction rather than return to the generic-card prototype."
- Line 3379 (2026-09-30): "Give visual composition, character, interaction feel, and useful advanced learning experiences more attention than expanding tests or reporting passing counts."
- Line 3403: "Avoid generic card/button repetition and vague decorative teaching copy." The owner "finds slightly more personality in the earlier reading composition" and asks not to flatten "color roles, typographic character or material identity".
- STATE.md 2026-09-05: seven looks ship (classic, editorial, neo, cash, console, soft, contrast); `surfaces/theme.py` is the only palette authority.
- COORDINATION.md W4: "Meaningfully different visual composition ... no palette-only closure or default acceptance by inference."

## Diagnosis

D1. The type voices exist but the screens do not use them. Source Serif 4 and iA Writer Quattro are vendored (`presentation.py` lines 117-144, `--font-paper`, `--font-ledger`), yet the desk title, focus title, section titles and course names all set `font-family:var(--font-chrome)` (system-ui), at `.desk-heading h2`, `.desk-focus h2`, `.desk-section-title h2`, `.course-card h2`. Only the quiz stem and lesson prose are serif. Screenshot: desk is all system sans, question stem is serif, so the app has two unrelated voices. The wordmark (`.product-brand`) is plain system-ui 20px.

D2. The type scale is flat. Five frozen tokens, display 32px and heading 20px. The desk title is 32px, only 12px above a 20px card title; the question stem is 20px at weight 400. Nothing on any screen has a scale jump that reads as a deliberate headline. Screenshot: desk title, focus title and course rows have nearly the same visual weight.

D3. Every screen is the same shape: a bordered card or rule-separated row list on a flat ground. Desk (`.desk-focus`, `.course-card`), courses, course overview, practice sets and the question (`.card.overhaul-question`, `.choice` boxes) all use 1px border, 6px radius, one accent edge. Practice question is a box (fieldset) holding boxes (choices) holding a box (hint). There is no screen-specific composition, so a desk, a course and a test feel interchangeable.

D4. Looks change color and corner radius, not composition. I cycled editorial, neo and console on the desk: same layout, same sans headings, only ground and accent moved. Editorial even declares a serif `h1` (`looks.py` editorial block) but the desk uses `h2` with an explicit chrome font in `presentation.py`, so the look's typography never reaches the desk. This matches the owner's W4 warning against palette-only closure. Seven looks give seven tints of one layout.

D5. Chrome and copy carry more weight than content, and neither has a voice. "Your desk" appears three times (top bar, hidden `h1`, `h2`) plus nav label; the desk subtitle "Continue a saved session, or open a course to read and practise." mixes UK spelling into a US-spelled product; wrong answers say "Not correct. Try a different answer, or open the next hint." (`quiz_page.py` 1421 and 4987), the hint panel says "TIER 0 · LESSON / Tier 0 is unlocked." (runtime vocabulary leaking into learner copy). Buttons are the same outline `Start`/`Practice`/`Study` everywhere. No signature element: no numbering, no recurring motif, no memorable detail beyond the 3px accent edge on the focus card.

Not a defect, kept as a strength: 390px layout has no horizontal overflow, 44px targets hold, bottom nav on mobile works, and the dark ground is calm.

## Ranked proposals

P1 (S-M). Assign type by role and add a real display step. Serif (`--font-paper`) for page titles, focus titles, course names and stems; ledger mono (`--font-ledger`) for eyebrows, counts, item position and section labels; chrome only for controls and nav. Add display sizes (about 56px desk title, 34px stem) as tokens beside the five frozen ones, scaled down under 640px. Why safe: fonts and tokens already exist, no color touched, accessibility gates unaffected (sizes only go up, targets unchanged). Files: `surfaces/presentation.py` (desk and course rules), `surfaces/quiz_page.py` (stem), `.planning/UI-SPEC.md` token table. Fixes D1, D2.

P2 (M). Give the desk and the question a composition of their own. Desk: borderless "focus slab" (accent top rule, serif title, oversized Start) over a numbered ledger index (01 Your courses, 02 Practice sets via CSS counters). Question: remove card-in-card-in-card; lettered rule lines with large serif letters, selected row filled with `--accent-soft` plus an inset accent edge, feedback as a "margin note". Why safe: only `--accent`, `--accent-soft`, `--line`, `--mut`, `--ink` are used; the semantic red verdict color is untouched; native radios stay, so the static form works without JS. Files: `presentation.py` (`.desk-*`, `.course-card`), `quiz_page.py` (`.choice`, `.verdict`, `.overhaul-response`). Fixes D3. This is the prototype.

P3 (S). Chrome diet. One page title per screen (drop the `.product-topbar` duplicate, keep the visually hidden `h1`), wordmark in serif with an accent period. Files: `presentation.py` `.product-topbar`, `.product-brand`; `daemon.py` shell. Fixes D5 chrome half.

P4 (M). Let looks own composition tokens, not just ground. Add per-look tokens (`--font-display`, `--display-size`, `--rule-weight`, `--card-style`) in `looks.py`, consumed by the product shell rules so editorial really is serif at the desk and console is mono-led. `theme.py` stays the only palette authority; `stylesheet_roundtrip.py` keeps measuring contrast per look. Fixes D4. Needs a human pick of which looks earn their keep.

P5 (S). Copy pass with a voice rule: concrete, US spelling, no runtime jargon in learner copy ("Tier 0 is unlocked" becomes "Hint 1 ready"), feedback that names what to check without disclosing keyed content. Constraint: runtime still owns disclosure, so wording changes only; test assertions on current strings (grep `Not correct`) move together. Files: `quiz_page.py`, `daemon.py`, desk subtitle. Fixes D5 copy half.

Suggested order: P1+P3 first (small, visible), then P2 behind the existing `look` setting as an opt-in look (reversible), then P4 if the owner prefers it.

## Prototype

`prototypes/ui-character-20261007/` holds static pages copied from the served desk and question markup (scripts stripped, links neutralised, fonts from `../../fonts`): `desk-before.html`, `desk-after.html`, `question-before.html`, `question-after.html`, `question-wrong-before.html`, `question-wrong-after.html`. After pages append one `<style>` block (the P1 to P3 rules) and change no markup except the mock "after" feedback sentence.

Checks run: viewed before and after at about 800 wide (the browser pane is narrower than the requested 1280, so 1280 was emulated and scaled) and at 390. Question page at 390: scrollWidth 390, zero controls under 44px. Desk at 390: visually no overflow, but my scripted overflow reading for that page hit a stale tab and is not trustworthy; re-measure. Contrast was not re-measured: the prototype adds no color, but the accent text on `--accent-soft` for the selected choice should go through `stylesheet_roundtrip.py` before adoption. The mock feedback sentence is placeholder copy; the real text must come from the runtime's disclosure tier.

Not verified: tabs 2 and 3 of the course overview, lesson and reading restyles (diagnosis only); human preference, which COORDINATION.md W4 says must be recorded separately.

## Stage 1 delivery (P1, P3, P5)

Files changed: `surfaces/presentation.py`, `surfaces/daemon.py`, `surfaces/quiz.py`, `surfaces/quiz_page.py`, `surfaces/lesson.py`, `surfaces/reading_desk.py`, `surfaces/theme.py` (copy only), `surfaces/visual_fixture.py` (copy only); tests `tests/stylesheet_roundtrip.py`, `tests/responsive_product_roundtrip.py`, `tests/staged_checker_continuity_roundtrip.py`.

What changed:
- P1: two display tokens beside the frozen five, `--text-title` 40px and `--text-hero` 56px, shrinking to 32px and 40px under 640px. Serif (`--font-paper`) now carries the wordmark, h1, h2, desk title (hero), focus title (title), section and course names, quiz stem (32px, weight 600, 20px under 640px), lesson and reading titles. Ledger mono carries the desk eyebrow, count and course chips. Chrome stays on nav and controls. No color added.
- P3: `.product-topbar` markup and CSS removed (the h1 is the one title; `<title>` unchanged). Wordmark is serif with an accent period.
- P5: "practise" to "practice", desk subtitle reworded; wrong-answer sentence now "Not correct. Re-read the question, then try another answer or open the next hint."; "colour" to "color" in settings copy. Runtime-owned `Tier N is unlocked.` and other hint-ladder copy untouched (LOCKED, in `runtime.py`).
- Extra: desk section links and "Workspace help" summary raised to 44px.

Test edits: stylesheet gate extended with `DISPLAY_TYPE_TOKENS` (scale now 12/16/18/20/32/40/56, every declared value checked); responsive_product asserts the topbar is gone; staged_checker (Playwright) string follows the new sentence. No safety, disclosure or accessibility assertion weakened.

Checks: PASS stylesheet, visual_accessibility, component_primitives, presentation_profiles, responsive_product, desk_craft, desk_experience, home, course_shell, ia_route (second run), ui_overhaul_navigation (second run), navigation_color, practice_entry, hint, surface, lesson, serve, formal_exam, theme, visual_system, reading_desk; `node --test tests/js/*.test.mjs` 147/147; `preflight --quick` passes. Browser: no horizontal overflow at 320, 390, 1280 on desk, courses, course overview, settings, activity, practice quiz in classic and contrast looks; desk and course screenshots in classic, editorial, console, dark; wrong-answer sentence seen live.

Unverified: `tests/daemon_roundtrip.py` fails with "daemon never printed a URL" because daemon startup takes about 6s under load average ~90 and the test allows 6s (environmental; re-run when idle). `tests/js` as a bare directory argument fails to run, use the glob. Playwright staged_checker test not run. Not screenshotted: lesson page, soft/cash/neo looks, practice question at 390. Pre-existing sub-44px items not touched: quiz radio inputs (their labels are 48px), `A.chip.lesson`, quiz `SUMMARY` (32px), course practice/learn links (24px), settings color input (27px). UI-SPEC.md token table not updated.


## Stage 2 delivery (P2 composition)

Authorization: the owner approved implementing P1 through P5 in the continuation
packet. The original diagnosis and prototype status above are retained as history.
This delivery is an uncommitted source change, not installed or human-accepted UI.

Files changed in this stage: `surfaces/presentation.py`, `surfaces/quiz.py`.
The desk now has a top-ruled focus slab, a larger primary action, and a single
ledger index. CSS counters number the Your courses and Practice sets headings in
DOM order. The existing `_desk_loose_section` projection participates in the same
index, including a workspace with no course. Choice rows have lettered rules and
selected-row fill with an inset accent edge. Verdicts use a margin-note rail while
retaining semantic correct/incorrect colors and the existing live region. The
response wrapper loses its extra border and inset. Shared `QUIZ_PRODUCT_CSS` now
holds the question composition previously embedded in `quiz.page_for`.

No server markup replacement was needed: `surfaces/daemon.py` and
`surfaces/quiz_page.py` retain their pre-packet bytes. Native inputs, forms, tokens,
all data attributes, DOM order, held feedback, and runtime-owned disclosure remain
in their original paths. Narrow focus slabs switch the grid to one column.

Stage-stop checks: `desk_craft_roundtrip.py` PASS (exit 0);
`surface_roundtrip.py` PASS (exit 0). `stylesheet_roundtrip.py` failed twice with
`FAIL: daemon never printed a URL. Output was:` and empty captured output.
The explicit synthetic daemon reached binding but failed with
`PermissionError: [Errno 1] Operation not permitted` at
`surfaces/daemon.py:8272`, then `server.py:116`. This is a sandbox socket restriction,
not proof of a layout defect. No test timeout was changed.

Browser checks: Playwright Chrome exited with `TargetClosedError` at
`check_stage2.py:5`; browser PID 16143 exited with SIGABRT. Background browser
creation and inventory both timed out. No screenshot, scrollWidth measurement,
focus traversal, 200 percent reflow, or live script-free POST is claimed.

Recovery: reverse only this packet's desk slab/index rules, question composition
rules, and `quiz.page_for` substitution. Restore the prior inline question CSS from
the task-start snapshot. Keep all Stage 1 and unrelated edits. Do not restore whole
files from Git.

## Stage 3 delivery (P4 look composition)

Files changed: `surfaces/presentation.py`, `surfaces/theme.py`.
Shared composition tokens assign display and label type roles, title and question
scales, row spacing, rules, enclosed surfaces, inset, corner treatment, and list
gaps. `composition_css` emits inherited body aliases through `theme_css`, so both
stylesheet emission orders retain the selected look. Sizes alias the shared scale;
palette values and semantic state colors are unchanged.

| Look | Composition |
|---|---|
| Classic | Serif slab and ruled ledger, baseline display scale |
| Editorial | Serif display, spacious rows, larger question display |
| Neo | Chrome display, heavy rules and enclosed squared rows |
| Cash | Chrome display, large question, filled rounded surfaces without rules |
| Console | Ledger display, smaller titles, tight enclosed grid |
| Soft | Serif display, roomy rounded filled surfaces with thin boundaries |
| Contrast | Chrome display, heavy boundaries, existing maximum-contrast palette |

Stage-stop checks: `presentation_profiles_roundtrip.py` PASS (exit 0),
`component_primitives_roundtrip.py` PASS (exit 0). Direct inspection confirmed all
seven look configurations emit the intended aliases, Console selects Ledger, and
Editorial differs from Console. Classic and unknown-look fallback emit no extra
shape block. Browser comparison remains blocked as described in Stage 2.

Recovery: reverse the composition token additions, `composition_css`, its
`theme_css` call, and the rules consuming composition aliases. Restore the Stage 2
constant values only; preserve the slab, ruled choices, margin note, and Stage 1.

## Stage 1 leftovers delivery

Files changed: `surfaces/presentation.py`, `surfaces/theme.py`,
`.planning/UI-SPEC.md`. Quiz radios and checkboxes now have 44px boxes; their native
labels and input behavior remain intact. Quiz summaries, lesson/context links,
course row links used by Practice/Learn, and the settings color input get a 44px
minimum. Density does not reduce that minimum. The UI-SPEC token table now records
`--text-title`, `--text-hero`, the rule tokens, and every composition token.

Test edits in this packet, complete inventory:

- `tests/responsive_product_roundtrip.py`: superseded flex-slab assertion becomes
  grid; desk index assertion includes its counter; narrow slab assertion becomes
  a single-column grid. Navigation, visible focus, wrapping, and target assertions
  are retained.
- `tests/stylesheet_roundtrip.py`: the old named-size inventory now includes three
  composition-size aliases. Every declaration, including all seven look outputs,
  must alias the explicitly allowed existing display steps. Frozen literal sizes,
  palette, contrast, boundary, and target checks remain unchanged.

Direct renderer previews were generated for desk, question, lesson, and settings
in all seven looks and light/dark modes, using only synthetic source. These are
56 HTML artifacts, not browser evidence. Soft/Cash/Neo, lesson, and 390px question
screenshot checks remain open, as does the full requested browser matrix.

Recovery: reverse the target selector additions and color-input minimum, the new
UI-SPEC token rows, and only the two test adjustments listed above. Preserve the
original Stage 1 changes. `runtime.py`, private learner files, Git staging, commits,
and owner processes were not touched by this packet.


### Verification completed after the source stages

Direct-render stylesheet checks PASS (exit 0): balanced braces, frozen/type alias
values, density bounds, type scale, no palette literals, and control-boundary token.
Semantic token contrast, every look ground contrast, and classic/unknown fallback
checks PASS. A negative alias fixture confirms the gate rejects
`--composition-question-size:14px`. These checks use real renderers but do not
substitute for browser layout, font HTTP serving, or live form submissions.
Control/form inventories match across seven looks and both light/dark modes on the
desk, question, and lesson. The 56 generated previews contain synthetic content.

`responsive_product_roundtrip.py`: PASS, 5 passed and 0 failed after the pinned
composition assertions were updated. `ui_overhaul_visual_roundtrip.py`: PASS,
compact frame, native/theme controls, role separation, and same-content comparison.
`python3 scripts/preflight.py --quick`: PASS twice; every executed gate passed,
with tests, clean-tree and JS intentionally skipped by that command.

`node --test tests/js/*.test.mjs`: 147 tests, 146 pass, 1 fail, 0 skipped.
The isolated `quiz_observers.test.mjs` retry is 2 tests, 1 pass, 1 fail. The persistent
failure is at `tests/js/quiz_observers.test.mjs:130`: `bundled auto-render must
handle delimiters`, actual null. That test imports adapters exclusively from
`surfaces/quiz_page.py`, which matches the task-start snapshot byte for byte.
The failure remains unresolved; no observer code, waits, or assertions were edited.

`git diff --check` over the six modified source/spec/test paths: PASS. Added packet
lines contain no em dash. Source was read symbol-first: presentation, quiz, theme,
daemon, and quiz_page were sampled in relevant windows rather than read in full.
The current UI-SPEC accessibility gates remain requirements, not an agent-issued
accessibility certification.


### Final Python command inventory

Each name below means `python3 tests/<name>_roundtrip.py`. Exit 1 rows are
failed or blocked commands, not passing suites. All startup/timeout failures
were rerun at least once without increasing a timeout. `start_daemon` traceback
failures converge at `tests/daemon_roundtrip.py:76`. There were no persistent
urlopen timeout traces to report.

| Name | Final exit | Result |
|---|---:|---|
| `stylesheet` | 1 | Startup failed twice; direct-render stylesheet gates pass separately. |
| `visual_accessibility` | 1 | Startup failed twice; public-payload/offline checks passed before startup. |
| `component_primitives` | 0 | PASS. |
| `presentation_profiles` | 0 | PASS, including final rerun after question density adjustment. |
| `responsive_product` | 0 | Final retry passes 5/5 after replacing superseded composition pins. |
| `desk_craft` | 0 | PASS. |
| `desk_experience` | 1 | Daemon startup failed twice. |
| `home` | 0 | PASS. |
| `course_shell` | 0 | PASS. |
| `ia_route` | 1 | Daemon startup failed twice. |
| `ui_overhaul_navigation` | 1 | Daemon startup failed twice. |
| `navigation_color` | 0 | PASS. |
| `practice_entry` | 1 | 3 test errors from daemon startup on both runs. |
| `hint` | 1 | Startup failed on both runner attempts and an additional direct retry. |
| `surface` | 0 | PASS. |
| `lesson` | 1 | Both runs time out after 30s in the same CLI subprocess; lesson_roundtrip.py:1979 and :2060. |
| `serve` | 1 | Serve startup failed twice; lifecycle/seed checks passed before startup. |
| `formal_exam` | 1 | Daemon startup failed twice. |
| `theme` | 0 | PASS. |
| `visual_system` | 0 | PASS. |
| `reading_desk` | 1 | 7 tests, 1 startup error on both runs; other 6 complete. |
| `quiz_symbol_return` | 1 | Daemon startup failed twice. |
| `quiz_reference_continuity` | 1 | Daemon startup failed twice. |
| `fill_surface` | 1 | Both runs fail at fill_surface_roundtrip.py:178, called at :210 and :253. |
| `presentation` | 1 | Daemon startup failed twice. |
| `staged_checker_continuity` | 0 | Exit 0 only prints optional --browser-shots guidance; browser journey was not run. |

Additional command: `ui_overhaul_visual_roundtrip.py` PASS (exit 0). The
installed staged-checker browser journey remains unverified; its no-argument
exit 0 is not a browser or continuity pass. Console choice padding now consumes
the same bounded row-density alias as its desk; 44px native inputs and the
choice minimum are independent of that padding.

Final remaining acceptance gate: run the full requested browser matrix on the
current source with socket binding and a working browser. Cover desk, courses,
course Overview/Practice, question before/after a wrong answer, lesson, and
settings at 1280/390/320, in Classic/Editorial/Console/Contrast and dark, plus
Soft/Cash/Neo screenshots. Measure overflow and target boxes, verify 200 percent
reflow, keyboard focus and script-free POST. Prior Stage 1 screenshots do not
verify this packet. Also retain the unresolved KaTeX observer assertion.


Final post-density rerun: direct-render stylesheet/contrast gates PASS (exit 0),
presentation profiles PASS (exit 0), responsive product PASS (5/5, exit 0), and
quick preflight PASS (exit 0). This is the third passing quick-preflight run in
this packet. Five edited Python files parse successfully. Whitespace checks pass.
The final delivery remains uncommitted source, with browser acceptance and the
persistent math-observer assertion open. No server markup, runtime copy, palette
values, or unrelated dirty work was changed by this packet.
