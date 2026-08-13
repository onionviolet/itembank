---
phase: 14-reading-teaching-surface-quality-pass
plan: 02
subsystem: presentation
status: complete
tags: [typography, type-scale, vertical-rhythm, measure, accessibility, css]
requires:
  - "surfaces/presentation.py SHARED_CSS :root -- --space-1..7, --font-chrome, --font-code (plan 14-01)"
  - "surfaces/lesson.py #lesson-content, the shipped reader content container"
  - "tests/stylesheet_roundtrip.py collect_static/collect_served/normalise (plan 14-01)"
provides:
  - "one type scale in the reader: 12/16/18/20/32px at 400/600, no relative unit, no literal family"
  - "--measure-prose 59ch / --measure-wide 80ch, and a .wrap that adds its gutter OUTSIDE the measure"
  - "the #lesson-content 24/8/24 prose rhythm, scoped so callouts, the gate band, the nav and the glossary keep their shipped values"
  - "font-size-adjust x-height matching for inline Ledger/Code runs in prose"
  - "the below-480px prose step-down to 16px"
  - "tests/stylesheet_roundtrip.py check_type_scale + TYPE_SCALE_SCOPE/TYPE_SCALE_DEBT (14-UI-SPEC gate 12)"
affects:
  - "every daemon-served lesson page"
  - "every surface that renders through presentation.surface_shell (quiz, study, session shells)"
  - "plan 14-04, which appends surfaces.quiz_page and served /quiz/ to TYPE_SCALE_SCOPE"
tech-stack:
  added: []
  patterns:
    - "scope-coverage assertion: every prefix in a scoped fixture must match at least one collected artifact, so a scoped check can never be green by matching nothing"
    - "reader rhythm scoped to the container that actually ships (#lesson-content), never to a spec-side name that exists nowhere in the tree"
key-files:
  created: []
  modified:
    - surfaces/presentation.py
    - surfaces/lesson.py
    - tests/stylesheet_roundtrip.py
    - tests/presentation_roundtrip.py
decisions:
  - "The eleven 14px sites were dispositioned by what each string IS, never by how small it looked: four disclosure/link controls and two recovery regions to 16px, five label roles to 12px. .status is 16px because LESSON_CSS defines no .status rule, so that one declaration styles the reader's degraded-lesson and style-warning notice -- recovery copy, not a chip."
  - "The measure retune is arithmetic, not taste: 1ch is the advance of 0 at 0.500 em against a 0.447 em frequency-weighted average character, so 66ch always rendered 74 characters. 59ch is 531px at 18px = 66 real characters."
  - "The prose rhythm is scoped to #lesson-content because .lesson-prose -- the name the design contract uses -- exists nowhere in this codebase (grep -c lesson-prose surfaces/lesson.py = 0). Using the spec-side name would have been a silent no-op, which is the exact D-A failure mode this phase exists to end."
  - "font-size-adjust:0.475 is reset to none on `pre code`. The contract says block Ledger must not receive the adjustment, but the selector it specifies matches code inside pre; without the reset the deliberate 16px block-code size (0.516 x 16 = 8.26px x-height, matched to Paper's 8.55px at 18px) would have been silently undone."
  - "The 320px .run-source override was DELETED rather than retuned. 16px is what stops iOS zooming on focus, and a floor that lapses at 320px lapses exactly where a phone needs it."
  - "check_type_scale's scope is an explicit tuple with a coverage guard. A scoped assertion that matches nothing is green for the same reason an unscoped one is -- it checked nothing -- and that is the pooling shape that let D-B survive a green suite."
metrics:
  duration: ~70min
  completed: 2026-08-13
  tasks: 3
  commits: 4
  files: 4
actuals:
  tokens: 7969
  tasks: 3
  commits: 4
---

# Phase 14 Plan 02: Reader Type, Rhythm and Measure — Summary

The reader now has one type scale, a paragraph rhythm that is 0.81 of its real
line box instead of 0.54, and a reading column that holds the 66 characters its
token has always claimed and never delivered — each value derived from the
vendored faces' own metrics, each proved on a served page, and all three locked
behind a new stylesheet invariant that names the files still owed.

## What Was Built

**Task 1 — `surfaces/presentation.py`, the shared primitive layer.** The eleven
`14px` sites were dispositioned individually against 14-UI-SPEC §4.2's rule
that what decides a size is what a string *is*: `.back`, `.step details
summary`, `details.details-section summary` and `.row .links` to **16px**
(strings inside interactive controls), `.state` and `.status` to **16px**
(recovery copy a learner acts on), `.context-line`, `.step-status`,
`.headline-label`, `.figure-label` and `th` to **12px** (label roles). The
display row `h1`/`.headline` went 28px → **32px**; the `@media
(max-width:767px)` `h1` override stays at 20px, which is on the scale. Every
`font-size` in the file is now one of 12/16/20/32 (the file carries no 18px
site; 18px is the reader's `text-lesson` and lives in `lesson.py`).

`--measure-prose` went `66ch` → **`59ch`** and `--measure-wide` `90ch` →
**`80ch`**, with the 1.118 correction factor and its consequence recorded in
Python rather than in the emitted CSS, because every CSS comment in
`SHARED_CSS` ships in every served page.

**Task 2 — `surfaces/lesson.py`, the reader.**

- *Sizes and voices.* `.warn` and `pre code` to 16px; `th,td` split into `td`
  16px / `th` 12px; `.orphan` to 12px. Every `RUNNABLE_CSS` relative size
  (`.9em`, `.85em`, `.8em`) and off-scale size (13px, 14px) is now an explicit
  scale size, and both `font:` shorthands resolve their family through a token
  instead of naming `ui-monospace,Consolas,monospace` literally. `.run-status`
  and `.run-unavailable` gained **16px in Ledger voice** — they are runtime
  assertions and the sentence a learner acts on after a failed run, and having
  no size at all they inherited the surrounding 18px Paper prose and spoke in
  the author's voice. `.run-stdout`/`.run-stderr` are 12px, the one named
  exception. `@media (max-width:320px){.run-source{font-size:13px}}` is
  deleted.
- *The measure stopped being eaten.* `.wrap` is now
  `max-width:calc(var(--measure-prose) + 2 * var(--space-3))` with its existing
  padding — a 563px box holding a 531px column, because
  `*{box-sizing:border-box}` is global and the gutter was inside the token.
- *Rhythm*, scoped to `#lesson-content`: `p` 24px, `li` 8px, `:is(ul,ol)` 24px.
  The bare `p,li` rule is untouched and keeps its shipped 16px, because it also
  styles callouts, the gate band, the nav and the glossary.
- *Inline voice mix.* `#lesson-content :is(code,samp,kbd,.ledger-inline)
  {font-size-adjust:0.475}`, with `#lesson-content pre code{font-size-adjust:
  none}` as the block-code exclusion.
- *Narrow viewports.* `@media (max-width:479px){#lesson-content :is(p,li)
  {font-size:16px}}`.

**Task 3 — `tests/stylesheet_roundtrip.py`, invariant 9.** `check_type_scale`
walks each in-scope stylesheet's brace tree and asserts three things per
declaration: a size is `px` and on {12,16,18,20,32}; a weight is 400 or 600; a
family — including the family portion of a `font` shorthand — is only
`var(--NAME)`. `@font-face` descriptor blocks are excluded from all three (a
`font-weight` there declares what a *file* is; the vendored Bold is a 700-weight
file), a declaration must be a property followed by `:` so an SVG `font-size=`
markup attribute is never matched, and a `--custom-property:` definition is a
definition rather than a use. `TYPE_SCALE_DEBT` names the three owed files and
is printed on every green run.

## Verification — actual output

### Suites

| Command | Result |
|---|---|
| `python tests/stylesheet_roundtrip.py` | EXIT=0 — 18 stylesheets balanced, token completeness, **type scale**, semantic contrast, font urls, per-route faces, manifest agreement |
| `python tests/lesson_roundtrip.py` | EXIT=0 |
| `python tests/presentation_roundtrip.py` | EXIT=0 |
| `python tests/lesson_code_roundtrip.py` | EXIT=0 |
| `python tests/gate_roundtrip.py` | EXIT=0 — the gate band shares `p,li` and this plan deliberately did not move it |
| `python tests/surface_roundtrip.py` | EXIT=0 |
| `python tests/visual_accessibility_roundtrip.py` | EXIT=0 |
| `python tests/theme_roundtrip.py` | EXIT=0 |
| `python tests/serve_roundtrip.py` | EXIT=0 |
| `python tests/scoring_roundtrip.py` | EXIT=0 |
| `python itembank.py lint fixtures/lesson_bank.md` | `3 items, 0 errors, 4 warnings` |
| `python itembank.py lint fixtures/sample_bank.md` | `6 items, 0 errors, 6 warnings` |

`presentation_roundtrip.py` prints `FAIL: expected exactly one h1, found 2` and
exits 0: that is its own `assert_single_h1` self-check tripping inside a
`try/except SystemExit`, pre-existing output and not a regression.

The full 64-file suite was **not** re-run as a whole, and that is deliberate
rather than an omission: plan 14-03 was executing concurrently in the same
working tree and had `surfaces/daemon.py`, `surfaces/session.py`,
`surfaces/cli.py` and `README.md` uncommitted at the time, so a whole-suite run
would have reported their in-flight state as though it were this plan's.

### The reader, served — actual bytes, not inference

`python itembank.py daemon <tmp> --no-open` → `url http://127.0.0.1:8730/`.

```
GET http://127.0.0.1:8730/lesson/lesson_bank -> HTTP 200, 21830 bytes served

  --measure-prose    = 59ch
  --measure-wide     = 80ch
  --leading-lesson   = 1.65
  --space-1..7       = 4px 8px 16px 24px 32px 48px 64px

  .wrap{max-width:calc(var(--measure-prose) + 2 * var(--space-3));
    margin:0 auto;padding:var(--space-4) var(--space-3) var(--space-7);
    font-family:var(--font-paper)}

  #lesson-content p{margin:0 0 var(--space-4)}
  #lesson-content li{margin:0 0 var(--space-2)}
  #lesson-content :is(ul,ol){margin:0 0 var(--space-4)}
  #lesson-content :is(code,samp,kbd,.ledger-inline){font-size-adjust:0.475}
  #lesson-content pre code{font-size-adjust:none}
  @media (max-width:479px){#lesson-content :is(p,li){font-size:16px}}

  <div class="card" id="lesson-content">      <- the container exists
  paragraphs inside it: 12
  literal 'lesson-prose' anywhere in the served page: False

  every font-size the document declares: ['12px','16px','18px','20px','32px']
  every font shorthand:                  ['16px/1.5 var(--font-chrome)','inherit']
```

`--space-4` resolving to `24px` beside `--leading-lesson: 1.65` on 18px prose
is the arithmetic behind the rhythm claim: 24 / (18 × 1.65) = 24 / 29.7 = 0.81
of a line, against the 0.54 it was.

### The runnable panel, served

`RUNNABLE_CSS` only reaches a document when a runnable fence renders, which
needs a daemon-served page, a profile enabling the language, no LAN refusal and
a live session. All four were arranged (`POST /api/start {"bank":"cs_loop",
"profile":"cs"}` → `200 session_id 93867bb2…`), then:

```
GET http://127.0.0.1:8730/lesson/cs_loop -> HTTP 200, 25358 bytes served
runnable control present in DOM: True

  .run-source-label{...font-size:12px;font-family:var(--font-chrome)}
  .run-source{...font:16px/1.45 var(--font-code);...}
  .run-help{font-size:16px;font-family:var(--font-chrome);...}
  .run-status{...font-size:16px;line-height:1.5;font-family:var(--font-ledger)}
  .run-label{font-size:12px;font-family:var(--font-ledger);font-weight:600;...}
  .run-stdout,.run-stderr{...font:12px/1.45 var(--font-code);...}
  .run-unavailable{font-size:16px;font-family:var(--font-ledger);line-height:1.5;...}

  '@media (max-width:320px)' anywhere in this document: False
  sizes:  ['12px','16px','18px','20px','32px']
  font:   ['12px/1.45 var(--font-code)','16px/1.45 var(--font-code)',
           '16px/1.5 var(--font-chrome)','inherit']
  families outside @font-face: ['var(--font-chrome)','var(--font-code)',
                                'var(--font-ledger)','var(--font-paper)']
  weights outside @font-face: ['600']
```

Daemon stopped; `netstat` confirms port 8730 clear; the temp directory removed.

**What this does and does not prove — stated plainly.** These are the *declared*
bytes the browser receives. They prove the rule reaches the document, the
selector matches a container that exists, the token carries the corrected value
and no off-scale or relative size or literal family survives anywhere in the
served reader. They do **not** measure rendered geometry: no browser laid this
out, so "531px column", "66 characters per line", "29.7px line box" and the
`font-size-adjust` used-size claim are arithmetic over the vendored faces'
metrics as 14-UI-SPEC §1 recorded them, not observations. Gate 11's headless
measurement is the phase's own answer to that and belongs to a later plan.

### The new invariant was negative-tested

Synthetic stylesheets through `check_type_scale`, to prove it bites rather than
merely passes:

```
an off-scale size          -> FAIL: surfaces.lesson.X: '.foo' declares font-size:14px;
                                    the project scale is 12/16/18/20/32
a relative size            -> FAIL: ... declares font-size:.9em -- a relative unit
                                    resolves off-scale against whichever parent it inherits
an off-pair weight         -> FAIL: ... declares font-weight:700; the project pair is 400/600
a literal family           -> FAIL: ... names the font 'Consolas', 'monospace' literally
a shorthand naming a family-> FAIL: ... font (size):13px  +  names 'ui-monospace','Consolas'
                                    literally in a font shorthand
an SVG font-size= attribute      -> no failure (must not trip)
an @font-face 700 descriptor     -> no failure (must not trip)
a --font-chrome definition       -> no failure (must not trip)
font:inherit                     -> no failure (must not trip)
an out-of-scope file (day.py)    -> no failure (must not trip)
scope covering nothing     -> FAIL: no stylesheet was collected for 'surfaces.lesson',
                                    'served /lesson/', so gate 12 asserted nothing about it
                                    and would stay green however far the type drifted
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking] `tests/presentation_roundtrip.py` pinned the old measure**

- **Found during:** Task 1, by the plan's own `<verify>` chain
- **Issue:** `test_voice_measure_leading_tokens_ship_in_shared_css` asserted
  `--measure-prose:66ch` and `--measure-wide:90ch` literally, so the retune the
  plan mandates could not land without it. The file is in neither this plan's
  nor plan 14-03's declared file set.
- **Fix:** both values moved to 59ch / 80ch **with the arithmetic recorded in
  the docstring**, so a later reader sees a re-derived assertion rather than a
  weakened one. `--leading-lesson:1.65` is re-confirmed by measurement (§4.5)
  and did not move. The assertion was not removed or loosened.
- **Files modified:** `tests/presentation_roundtrip.py` · **Commit:** `92265b4`

**2. [Rule 2 — Missing critical functionality] `pre code` needed an explicit
`font-size-adjust` reset**

- **Found during:** Task 2
- **Issue:** the contract's selector `#lesson-content :is(code,samp,kbd,
  .ledger-inline)` matches `code` inside `pre` by descent, while the same
  section states block code must not receive the adjustment. Left as written it
  would have silently undone the deliberate 16px block-code size — 0.475 × 16 =
  7.6px x-height instead of the matched 8.26px.
- **Fix:** `#lesson-content pre code{font-size-adjust:none}` immediately after,
  chosen over `:not(pre code)` because a reset has no Selectors-4 support
  question and degrades identically.
- **Files modified:** `surfaces/lesson.py` · **Commit:** `b962a05`

**3. [Rule 3 — Blocking] the new `lesson.py` comments named the vendored faces**

- **Found during:** the full verification sweep after Task 3
- **Issue:** `presentation_roundtrip.py` Test 2 scans **source text** —
  comments included — and permits only `presentation.py` to spell a family. The
  rhythm and x-height rationale added in Task 2 named both faces in prose. This
  is the identical trap plan 14-01 hit in `quiz_page.py`.
- **Fix:** reworded to "the Paper face" / "the Ledger face" with the reason
  recorded inline so it is not reintroduced. The test was not weakened.
- **Files modified:** `surfaces/lesson.py` · **Commit:** `6101f79`

**4. [Rule 1 — Bug] a non-ASCII section sign in a printed fixture line**

- **Found during:** Task 3's first green run
- **Issue:** the closing debt line printed `§17` and a Windows console rendered
  it lossily (`�17`), and two failure messages carried a `…` for the same
  reason. Plan 14-01 hit and fixed the identical defect.
- **Fix:** `section 17` and `var(--NAME)` in every **printed** string; the `§`
  in docstrings and comments, which never reach a console, is untouched.
- **Files modified:** `tests/stylesheet_roundtrip.py` · **Commit:** `3b34442`

### Additions beyond the plan

**5. [Rule 2] a scope-coverage guard on `check_type_scale`**

The plan specified an explicit `TYPE_SCALE_SCOPE` but no assertion that the
scope matches anything. A scoped fixture whose prefixes match zero collected
stylesheets is green for exactly the reason an unscoped one is — it checked
nothing — and that is the pooling shape `REQUIRED_FONT_ROUTES` exists to
prevent one invariant earlier in the same file. Every prefix must now match at
least one collected stylesheet. Commit `3b34442`.

## Deferred Issues

| Item | Where | Why deferred |
|---|---|---|
| `surfaces/theme.py` SETTINGS_CSS, `surfaces/day.py`, `surfaces/study.py` still carry off-scale sizes | named in `TYPE_SCALE_DEBT` | 14-UI-SPEC §17 item 6 / §4.2 — the Phase 4 cleanup this phase does not widen its diff to reach. Printed on every green run so it cannot be forgotten. Needs an owning plan. |
| `surfaces/quiz_page.py` and `served /quiz/` are outside `TYPE_SCALE_SCOPE` | `tests/stylesheet_roundtrip.py` | The quiz has not been migrated; plan 14-04 appends both once it is. A premature entry turns the fixture red for the wrong reason. |
| Rendered geometry is unverified | — | No browser measured this. Gate 11's headless measurement is the phase's answer and belongs to a later plan; the claims here are arithmetic over the faces' recorded metrics. |

## Known Stubs

None. No hardcoded empty value, placeholder string, TODO or unwired component
was introduced. Every rule added reaches a served page and was read back off
the wire; `.ledger-inline` is in the `font-size-adjust` selector matching
nothing today, which the plan directs explicitly because the design contract
names it — it is a forward hook in a selector, not a stub in the code path.

## Threat Flags

None. No new network endpoint, auth path, file-access pattern or schema change
at a trust boundary. `T-14-05` holds: every rule added is selector-scoped
presentation, none is generated from bank text, and the lesson renderer's
escaping is untouched. `T-14-08` is mitigated as planned — the 16px recovery
floor is applied by disposition and re-checked by the new size assertion.
`T-14-SC` holds: no package manager was invoked and no byte was fetched.

## Success Criteria

| Criterion | Status |
|---|---|
| Reader prose: 18px, 1.65 leading, 24px paragraph gap, 66 real characters | met — `--space-4:24px`, `--leading-lesson:1.65` and `font-size:18px` all read off the served page; the 66 characters are arithmetic, not measured |
| Below 480px: prose at 16px, at least 45 characters per line | met as a declaration — the rule is in the served bytes; 47.9 characters is the contract's arithmetic. 320px yields 40 and is recorded as not met rather than faked |
| No relative-unit font size and no literal font family anywhere in the reader | met — served document declares only 12/16/18/20/32px and only `var(--…)` families outside `@font-face` |
| Machine output stays at 12px; the sentence after a failed run is 16px Ledger | met — `.run-stdout`/`.run-stderr` `font:12px/1.45 var(--font-code)`, `.run-status` 16px `var(--font-ledger)` |
| The type-scale fixture is green for the reader and names the deferred files | met — invariant 9 green, debt line printed on every run, negative-tested ten ways |

## Self-Check: PASSED

- `.planning/phases/14-reading-teaching-surface-quality-pass/14-02-SUMMARY.md` — FOUND
- `surfaces/presentation.py`, `surfaces/lesson.py`, `tests/stylesheet_roundtrip.py`,
  `tests/presentation_roundtrip.py` — FOUND and importable (every suite above loads them)
- commit `92265b4` — FOUND
- commit `b962a05` — FOUND
- commit `3b34442` — FOUND
- commit `6101f79` — FOUND
- `git diff --diff-filter=D 0fbfe07..HEAD -- surfaces tests` — no deletions
- no file belonging to plan 14-03 was staged or committed by this plan
