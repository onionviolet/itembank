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
