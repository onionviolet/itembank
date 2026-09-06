# The object-by-verb surface grid, measured

Generated 2026-09-05 by `PYTHONPATH=. python3 tools/surface_coverage.py`,
which reads the command list from `surfaces.cli.build_parser()` and the
route list from `surfaces.daemon.ROUTES` rather than from any copy. Rerun it
rather than trusting this file: the numbers below are a snapshot of a
measurement that moves, and `tests/surface_coverage_check.py` fails the
build if a command or route is ever added without being classified, or if an
empty cell is left without a sentence saying what it costs.

The measured half below was regenerated 2026-09-05 after plan 19A-01; the prose above it is the reading of the shape, which has not changed.

This is the measured form of the 2026-09-05 gap pass's sentence, "the engine
is real and has almost no door"
(`2026-09-05-what-the-vision-still-needs.md`). What that pass argued, this
counts.

## How to read it

- Rows are durable objects, in the order `AGENTS.md` lists them, plus four
  the runtime owns that a learner meets anyway.
- Columns are the five verbs a surface has to answer for an object to be
  usable: make one, look at one, alter one, understand why it is as it is,
  and take a step back.
- `cli+http` means both surfaces reach it, `cli` or `http` means one does,
  `--` means neither, and `n/a` means the verb does not apply to that object
  and the reason is recorded in `NOT_MEANINGFUL`.
- An empty cell is the finding, and every one of them carries one sentence
  on what its absence costs. That sentence is the argument; the grid is just
  where it lives.

## What the shape says, in three lines

- **Sitting a quiz is finished work.** Every verb on `sitting`, `item`,
  `bank` and `evidence event` has a surface, most of them two.
- **Building a course is nearly unreachable.** `objective / create` and
  `lesson / create` are still empty, and those are most of what
  `SOURCE-TO-COURSE.md` describes as the milestone. Two of the four have
  been built since this was first measured. `source binding / create` was
  the first cell this grid caused to be built, on 2026-09-05: `itembank bind
  source`, `itembank bind treatment`, `POST /api/course/bind`, and a panel
  in the course's Sources area, all reaching the one rights-gated path that
  already existed. `course / create` and `course / change` followed the same
  day with plan 19A-01's dispatch spine: `itembank course create` /
  `rename`, `POST /api/course/create` / `rename`, one validated request
  document, and `course.create_course` / `write_course` underneath.
- **The things the project is proudest of are still the least reachable.**
  Provenance, notes, strategies and agent operations are implemented, tested
  and frozen, and a learner cannot see or touch any of them. Rights left
  that list on 2026-09-05, because a binding refused for a right nobody
  declared has to have its way out on the same surface.

# Surface coverage: 40 of 82 meaningful (object, verb) cells reached

19 objects by 5 verbs is 95 cells; 13 do not apply and are named with a reason, leaving 82 that should have a surface. 42 of those have none.

71 commands and 53 routes measured, every one of them classified.

| object | create | inspect | change | explain | undo |
|---|---|---|---|---|---|
| course | cli+http | cli+http | cli+http | cli+http | cli |
| scope | n/a | -- | -- | -- | -- |
| objective | -- | cli+http | -- | cli | -- |
| source | cli+http | cli+http | -- | -- | -- |
| source binding | cli+http | cli+http | -- | -- | -- |
| lesson | -- | cli+http | cli | cli+http | -- |
| bank | cli | cli+http | cli | cli | cli |
| item | -- | cli+http | cli | cli+http | -- |
| activity | -- | cli+http | -- | -- | -- |
| learner note | -- | -- | -- | -- | -- |
| evidence event | cli+http | cli+http | n/a | cli | cli |
| strategy | n/a | -- | -- | -- | -- |
| agent operation | -- | http | -- | -- | -- |
| rights grant | cli+http | cli+http | cli+http | -- | n/a |
| accepted revision | n/a | -- | n/a | n/a | n/a |
| sitting | cli+http | cli+http | cli+http | -- | cli |
| package | cli+http | -- | -- | -- | -- |
| settings | n/a | cli+http | cli+http | n/a | n/a |
| day plan | n/a | cli+http | cli+http | -- | n/a |

## Empty cells, and what each costs

- **scope / inspect.** scope.md is read by tools/rollup_screens.py and by nothing a learner can open. The rollup screens are evidence files, not routes.
- **scope / change.** Boundedness, membership and the completion predicate are edited by hand in scope.md.
- **scope / explain.** Nothing states why a scope is open or bounded, which is the sentence that governs whether it may ever report complete.
- **scope / undo.** A scope edit is a text edit; git is the only undo.
- **objective / create.** Objectives are authored by hand into objectives.md and the sidecar. No surface adds one, and no surface links one to a source passage.
- **objective / change.** Rewording an objective, or moving it between containers, is a hand edit of two files that must stay in step.
- **objective / undo.** No surface reverses an objective edit.
- **source / change.** Re-importing is the only way to refresh a source, and it mints a new object rather than updating.
- **source / explain.** The Sources area now states each source's read right, but not what it was used FOR: which objectives cite it and which items came from it.
- **source / undo.** An imported source cannot be unbound from a surface.
- **source binding / change.** Re-pointing a binding at a different passage is a sidecar table edit.
- **source binding / explain.** A binding carries confidence and a rationale and no surface reads them out.
- **source binding / undo.** No surface removes a binding.
- **lesson / create.** The lesson-authoring skill is a stub and no command writes a lesson. Lessons are written by hand or by an agent editing files directly.
- **lesson / undo.** An authoring audit is reversible; a hand edit is not.
- **item / create.** Writing an item is the author-bank skill editing a file. No surface adds one, which is why a bad question found mid-sitting cannot be fixed there.
- **item / undo.** No surface reverses an item edit or retires an item.
- **activity / create.** The ACTIVITIES registry is authored in the bank; no surface declares one.
- **activity / change.** Same registry, same absence.
- **activity / explain.** An activity declares purpose, demand and evidence state; nothing reads them back.
- **activity / undo.** No surface withdraws an activity declaration.
- **learner note / create.** notes.py implements the whole note lifecycle, including promotion and the authority guard. No surface writes one.
- **learner note / inspect.** Same module, same absence: nothing renders a note.
- **learner note / change.** notes.py implements editing and promotion; no surface reaches it.
- **learner note / explain.** A note's provenance and review state are recorded and never shown.
- **learner note / undo.** Deletion is implemented and unreachable.
- **strategy / inspect.** strategies.py freezes four contracts with eight declared columns each. No surface lists them or offers a choice.
- **strategy / change.** A learner cannot choose a strategy, which is the one axis the strategy contract says is theirs.
- **strategy / explain.** Each contract declares eight columns including accommodation and evidence effect; none is rendered.
- **strategy / undo.** Nothing to undo while nothing can be chosen.
- **agent operation / create.** No surface starts an agent operation. The whole propose-and-accept seam is unplugged.
- **agent operation / change.** No surface accepts or rejects a proposal.
- **agent operation / explain.** The journal records exactly what left the machine for each agent call. No surface shows it.
- **agent operation / undo.** Rejecting or reversing an agent operation has no surface.
- **rights grant / explain.** Unknown stays restrictive, and nothing says which right is unknown or why an export refused.
- **accepted revision / inspect.** 15B's accept_revision record has no reader.
- **sitting / explain.** A finished sitting reports counts. Nothing walks it back item by item with what was shown and when.
- **package / inspect.** A package's manifest and loss report are written to disk and read by nobody: the loss report is the honest half of an export and it has no reader.
- **package / change.** No surface re-exports or repairs a package.
- **package / explain.** Nothing explains why an object did not cross.
- **package / undo.** No surface deletes or supersedes a package.
- **day plan / explain.** The plan says what is due and not why this rather than that.

