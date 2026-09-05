# The object-by-verb surface grid, measured

Generated 2026-09-05 by `PYTHONPATH=. python3 tools/surface_coverage.py`,
which reads the command list from `surfaces.cli.build_parser()` and the
route list from `surfaces.daemon.ROUTES` rather than from any copy. Rerun it
rather than trusting this file: the numbers below are a snapshot of a
measurement that moves, and `tests/surface_coverage_check.py` fails the
build if a command or route is ever added without being classified, or if an
empty cell is left without a sentence saying what it costs.

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
- **Building a course is not reachable at all.** `course / create`,
  `objective / create`, `source binding / create` and `lesson / create` are
  all empty, and those four are the whole of what
  `SOURCE-TO-COURSE.md` describes as the milestone.
- **The things the project is proudest of are the least reachable.** Rights,
  provenance, notes, strategies and agent operations are implemented,
  tested and frozen, and a learner cannot see or touch any of them.

# Surface coverage: 34 of 82 meaningful (object, verb) cells reached

19 objects by 5 verbs is 95 cells; 13 do not apply and are named with a reason, leaving 82 that should have a surface. 48 of those have none.

64 commands and 46 routes measured, every one of them classified.

| object | create | inspect | change | explain | undo |
|---|---|---|---|---|---|
| course | -- | cli+http | -- | cli+http | cli |
| scope | n/a | -- | -- | -- | -- |
| objective | -- | cli+http | -- | cli | -- |
| source | cli+http | cli+http | -- | -- | -- |
| source binding | -- | http | -- | -- | -- |
| lesson | -- | cli+http | cli | cli+http | -- |
| bank | cli | cli+http | cli | cli | cli |
| item | -- | cli+http | cli | cli+http | -- |
| activity | -- | cli+http | -- | -- | -- |
| learner note | -- | -- | -- | -- | -- |
| evidence event | cli+http | cli+http | n/a | cli | cli |
| strategy | n/a | -- | -- | -- | -- |
| agent operation | -- | http | -- | -- | -- |
| rights grant | -- | -- | -- | -- | n/a |
| accepted revision | n/a | -- | n/a | n/a | n/a |
| sitting | cli+http | cli+http | cli+http | -- | cli |
| package | cli+http | -- | -- | -- | -- |
| settings | n/a | cli+http | cli+http | n/a | n/a |
| day plan | n/a | cli+http | cli+http | -- | n/a |

## Empty cells, and what each costs

- **course / create.** A course is created by calling course.create_course from Python. Neither a person nor an agent client can start a course from a surface.
- **course / change.** No surface renames a course, moves a unit, or edits the scope tree. The sidecar is hand-edited Markdown.
- **scope / inspect.** scope.md is read by tools/rollup_screens.py and by nothing a learner can open. The rollup screens are evidence files, not routes.
- **scope / change.** Boundedness, membership and the completion predicate are edited by hand in scope.md.
- **scope / explain.** Nothing states why a scope is open or bounded, which is the sentence that governs whether it may ever report complete.
- **scope / undo.** A scope edit is a text edit; git is the only undo.
- **objective / create.** Objectives are authored by hand into objectives.md and the sidecar. No surface adds one, and no surface links one to a source passage.
- **objective / change.** Rewording an objective, or moving it between containers, is a hand edit of two files that must stay in step.
- **objective / undo.** No surface reverses an objective edit.
- **source / change.** Re-importing is the only way to refresh a source, and it mints a new object rather than updating.
- **source / explain.** Nothing shows what a source was used for: which objectives cite it and which items came from it.
- **source / undo.** An imported source cannot be unbound from a surface.
- **source binding / create.** course.bind_source exists in Python. Binding a source to an objective is the central act of building a course and has no surface at all.
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
- **rights grant / create.** See rights grant / change: one operation records both, and neither is reachable.
- **rights grant / inspect.** A learner cannot see what they may do with a source they bound, which is the question that decides whether a course can be exported at all.
- **rights grant / change.** journal.op_grant_rights landed 2026-09-05 and has no surface: rights are granted from Python only.
- **rights grant / explain.** Unknown stays restrictive, and nothing says which right is unknown or why an export refused.
- **accepted revision / inspect.** 15B's accept_revision record has no reader.
- **sitting / explain.** A finished sitting reports counts. Nothing walks it back item by item with what was shown and when.
- **package / inspect.** A package's manifest and loss report are written to disk and read by nobody: the loss report is the honest half of an export and it has no reader.
- **package / change.** No surface re-exports or repairs a package.
- **package / explain.** Nothing explains why an object did not cross.
- **package / undo.** No surface deletes or supersedes a package.
- **day plan / explain.** The plan says what is due and not why this rather than that.

