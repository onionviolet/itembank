# 17B-03 evidence: the rollup default (17B-CONTEXT D-03 checkpoint)

Recorded 2026-09-01 by plan 17B-03 Task 2.

## What was rendered for the choice

Both rollup models were rendered over the same GRAPH-03 tuples, computed
once from the fixture's real evidence after the practice and exam sittings
and the scope tree in `course_fixture_17b/scope.md`:

| artifact | SHA-256 | bytes |
|---|---|---|
| `evidence/17B-03-rollup-tuples.json` (the one tuple set both screens read) | `66ec543c07e700442aa2d7f9071ded872b395b59b2fecaf0330a2475fa451092` | as written |
| `evidence/17B-03-rollup-dim.html` (ROLLUP-DIM) | `e797f28bd2672f95bf4ef6ff250e579f415e709877d041eaf2218fc043e1453f` | 22518 |
| `evidence/17B-03-rollup-map.html` (ROLLUP-MAP) | `6d1743c51ae9a63043336189bcc5171ff9d0f663452bee0636330bfdbc5310ce` | 19375 |

The rendering script and its output are transcribed in
`evidence/17B-03-learner-pass.md`, stage 7. Open the two HTML files in a
browser to see the screens; both carry the 17A stylesheet and the light
theme block.

## The question, verbatim, preserved for Weibao

> Which rollup model is the global default? Options: ROLLUP-DIM
> (dimension-wise, stated denominators) and ROLLUP-MAP (one-level map
> view). Recommended default: ROLLUP-MAP for scope trees deeper than one
> level, ROLLUP-DIM otherwise.

## The answer as recorded

- **Chosen model:** PROVISIONAL, adopted per the plan's own recommended
  default line: **ROLLUP-MAP for scope trees deeper than one level,
  ROLLUP-DIM otherwise.** For the tracer's own tree (field containing
  course containing unit, depth two below the field) that provisional
  default resolves to ROLLUP-MAP at the field and course scopes and
  ROLLUP-DIM at the unit (a leaf has no children to map).
- **Chooser:** provisional, coordinator under Weibao's 2026-09-01 deferral
  directive ("human reviews are deferred, recorded as owed, never
  self-certified, and never silently defaulted"); the real choice is owed
  to Weibao. This is a recorded provisional, not a silent default, and
  not Weibao's answer.
- **Date:** 2026-09-01.
- **Per-scope override note:** the rollup is a per-scope setting with a
  global default (D-03). Any scope may override the global default; the
  fixture's `scope.md` records no override, so every scope in the tracer
  inherits the provisional global default above. When Weibao answers, his
  answer replaces the provisional global default here and any per-scope
  overrides he names are recorded beside it; nothing in the fixture or the
  code stores the provisional value as configuration.

## What the two screens showed (so the choice can be made from them)

- ROLLUP-DIM: for each of the three scopes, the seven dimension rows
  (`Design coverage`, `Participation`, `Settled evidence`, `Current
  retention`, `Formal completion`, `Selected enrichment`, `Open
  uncertainty`), each with numerator and denominator or the frozen
  indeterminate copy, the required membership class kept separate (no
  enrichment member exists in this tree, so the enrichment row reads
  indeterminate rather than zero), and at the unit the seven per-objective
  fill states (D-14A-3 blocks, `n of 4`, legend present). No single
  aggregate number, no percentage in visible text (0 visible percent
  signs), no `score` word. The open field states its scope version on its
  claim block and never reads complete; the bounded course reads complete
  under `afe101-complete-v1`.
- ROLLUP-MAP: the field shows its one direct child (the course) as a card
  with that child's settled-evidence summary and `bounded` / `complete`
  chips; the course shows its one direct child (the unit) the same way,
  with the unit's fill-state rows beside the card. No aggregation past
  direct children; the field's own status line names its scope version.

## Owed

The real answer, from Weibao, from these two screens. Until it lands this
record reads provisional and the G5 row in `17B-GATES.md` says so.

## Addendum, 2026-09-05: both screens regenerated after the primitives were fixed

Weibao asked for the two 17B-03 defects behind these screens to be fixed,
not only recorded. Both were 17A primitive gaps, so both were fixed in the
primitives rather than worked around in the screens, and the screens were
then rebuilt from the same evidence through the fixed primitives.

- **`17B-03 D-06 item 7`, the missing fill-state slot.** No card primitive
  carried a standing, so the wave-3 pass composed ROLLUP-MAP out of
  `course_shelf` and `fill_state` by hand. `presentation.course_shelf` now
  takes a per-card `fill` and renders it through the one `fill_state`
  primitive, with one `legend` rendered once for the whole list and every
  standing pointing at it by `aria-describedby`. The legend used to repeat
  verbatim under all seven objective rows.
- **`17B-03 D-06 item 8`, the missing ARIA roles.**
  `progress_claims.ARIA_CONTRACT` says a standing is a `progressbar`
  carrying `aria-valuetext` and deliberately no `aria-valuenow`, and that a
  determinate claim carries valuemin, valuemax, valuenow and the whole
  sentence as valuetext. Neither was emitted. Both are now, in
  `presentation.fill_state` and
  `presentation.progress_comprehension_display`. The visible text is
  unchanged, so a sighted reader sees exactly what they saw before.

Two legibility repairs came with them, both found by looking at the
rendered screens rather than at the markup:

- Every scope now carries a **visible heading and its own note above its
  own block**. `_section` puts a label in `aria-label` only, so DIM stacked
  three blocks of identical row labels and a sighted reader had to reach
  the note at the END of a block to learn which scope they had been
  reading. On MAP the note fell after the NEXT scope's cards, so the open
  field's "never reports complete" sentence read as if it described the
  bounded course.
- The scope names are read from `scope.md`'s own headings rather than
  assumed, so the screens render a second course's tree without edits.

The generator is now a committed tool, `tools/rollup_screens.py`, run as
`PYTHONPATH=. python3 tools/rollup_screens.py course_fixture_17b <out>`.
The wave-3 script was a scratch file that was never committed, which is why
these screens could not be rebuilt until now. Regenerated artifacts, beside
this file:

| artifact | bytes | SHA-256 |
|---|---|---|
| `17B-03-rollup-dim.html` | 23655 | `a6feaafa8600038186cb59057e5dea09044a56610de3b207ce11f5ce7b9eac66` |
| `17B-03-rollup-map.html` | 20869 | `b1599b4aff3be7afb5b75af0778097724fda18a6500f8c70405bb0135177c287` |
| `17B-03-rollup-tuples.json` | 4863 | `cb3b79dad649d484fa46c567bfd73dea4c2f74f9e853dd7bafc453a60b701cfd` |

Structural checks on the new bytes: visible percent signs 0 on both, the
word `score` absent from both, 17 progressbar rows on DIM (three scopes of
dimension claims plus seven objective standings) and 7 on MAP, and one
legend per list rather than one per row.

**The choice itself is still owed to Weibao.** Nothing here answers it; the
screens are just now worth choosing from.
