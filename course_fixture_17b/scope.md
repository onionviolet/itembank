# Scope tree for the 17B tracer

This file carries the minimal scope tree 17B-CONTEXT D-03 requires: one
open field scope containing one bounded course scope containing the unit.
The vocabulary follows IL-20260817-01 (the scope object, the boundedness
axis, and the three membership classes) and composes with the 14B sidecar
contract (`14B-FREEZE.md`); the rollup displays over these scopes are
ROLLUP-DIM and ROLLUP-MAP, rendered by the 17B-03 learner pass, and
nothing here stores or implies an aggregate score.

## Field scope: Fenland Systems

- **Scope kind:** field
- **Boundedness:** open
- **Scope version:** FS-2026-09-01.1
- **Level label (free text):** survey field
- **Completion:** never reports complete. An open scope states its scope
  version on every claim it makes, so any progress statement over this
  field reads "as of scope version FS-2026-09-01.1" and carries no
  percentage and no completion state.
- **Members:**

| member | class |
|---|---|
| Aldrasse Fen Ecology 101 (bounded course scope, below) | required |

## Course scope: Aldrasse Fen Ecology 101

- **Scope kind:** course
- **Boundedness:** bounded
- **Membership version:** AFE101-m1
- **Level label (free text):** introductory course
- **Completion predicate (named):** `afe101-complete-v1`: this course
  reports complete when every objective of every required member unit
  under membership version AFE101-m1 has settled evidence, with pending
  and unknown states shown as themselves until then. The bounded course
  may truthfully complete under this predicate during the tracer; the
  open field above never does.
- **Members:**

| member | class |
|---|---|
| Unit 3: Peat Hydrology and the Lantern Moss Cycle | required |

## Unit: Unit 3, Peat Hydrology and the Lantern Moss Cycle

- **Scope kind:** unit (leaf of this tree)
- **Parent:** Aldrasse Fen Ecology 101
- **Objectives:** the seven unit objectives in `objectives.md`, each
  cited into one of the two sources under `sources/`.
- **Membership classes in use:** all seven objectives are `required`
  under AFE101-m1. No `required-choice` or `enrichment` member exists in
  this minimal tree; adding an enrichment member later must never lower
  completion (the shared rollup rule in 17B-UI-SPEC section 3).
