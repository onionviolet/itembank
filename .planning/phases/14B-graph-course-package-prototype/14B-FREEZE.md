# Phase 14B freeze record

Written 2026-08-27 by plan 14B-06 Task 4, on Darwin arm64, Python 3.14.6.
The evidence is in `14B-TRACER-REPORT.md`; this file is the verdict.

## Freeze withheld

**Phase 14B is not frozen. Every interface in it stays changeable.** Two of
the three legs of the gate are green. Two independent things are not, and
either one alone is sufficient to withhold.

### Ground one: the authorability leg has no human sign-off

`14B-AUTHORABILITY-REVIEW.md` exists, its five questions are written out, and
its machine half is green. Its Sign-off section is blank.

The gate is three-legged by the ROADMAP's own words for this phase: "Freeze
gate: three-domain graph tracer, clean restore, authorability review." Two
legs are not three. `OPERATION-CONTRACT.md` states that an agent never
self-certifies this class of judgment, so no agent may close the third, and
this record does not.

### Ground two: the full suite is not green, and one red is this phase's own

Plan 14B-06 Task 4 step 1 requires
`for t in tests/*.py; do python "$t" || exit 1; done` to exit 0. Run
individually on 2026-08-27, 73 of 77 suites exit 0 and four are red.

`tests/visual_system_roundtrip.py` fails
`check_harness_undo_classification` with `journal record type migrate has no
learner-facing phrase`. Commit `5568138` added `migrate` as the eleventh
member of `journal.RECORD_TYPES` under D-14B-3, and
`surfaces/visual_fixture.OPERATION_PHRASE` still has ten entries. This is a
regression Phase 14B introduced. `tests/phase_062_audit.py` fails as a
cascade of it. `tests/day_roundtrip.py` and
`tests/retention_ui_roundtrip.py` are the pre-existing live-Anki
environmental failure and are not this phase's.

Declaring a format durable while the phase that produced it has a red suite
of its own making is exactly the shape of claim a freeze record exists to
prevent.

## What was checked, by name

### The Phase 13.9 precondition: satisfied

The ROADMAP's Phase 13.9 entry states the gate quoted verbatim: "Gate: no
14B-or-later freeze closes before this has been walked." All three checks
plan 14B-06 Task 4 step 2 names:

| Check | Result |
|---|---|
| `.planning/phases/13.9-walking-skeleton/13.9-DECISIONS.md` exists and carries a dated approval line for the objective map | `ok`. Two of them: "2026-08-16 objective-map approval" and "2026-08-22 rebuild executed, and the objective map approved" |
| `13.9-01-SUMMARY.md`, `13.9-02-SUMMARY.md`, and `13.9-03-SUMMARY.md` all exist | `ok`. All three are present |
| The ROADMAP's Phase 13.9 entry is marked complete | `ok`. Line 104 reads `- [x] **Phase 13.9: Walking Skeleton ...** (walked 2026-08-24 ...)` and the subphase table row reads Complete |

The walking skeleton is not what is blocking this freeze. It was walked, and
this record says so explicitly so that a later reader does not go looking.

### The three legs

| Leg | Result | Evidence |
|---|---|---|
| Three-domain graph tracer | **green** | `python3 tests/three_domain_tracer.py` exit 0, final line `TRACER: 5 passed, 0 skipped, 0 failed` |
| Clean restore drill | **green** | `scenario_clean_restore()`: 2 of 2 entries verified by recomputation, `complete` True, restored sidecar byte-identical, both loss lists returned, all four applicable loss categories named with a reason |
| Authorability review | **not green** | `14B-AUTHORABILITY-REVIEW.md` Sign-off is blank. The machine half is green: one hand-edited `order` cell gives a one-line diff, the reordering reaches the re-projected outline, longest sidecar line 126 characters |

### The other commands

| Command | Result |
|---|---|
| `python3 itembank.py guard .` | exit 0, `0 offending files` |
| `python3 schema_validate.py --all` | exit 0, `18 schema documents self-check clean` |
| every `tests/*.py` individually | 73 of 77 exit 0, four red, detailed in `14B-TRACER-REPORT.md` |

## What this withholding does and does not mean

**It does not mean the work is unproven.** All four requirement Fixture
sentences are executable scenario functions and all four pass. Eighteen of
the nineteen rows in `14B-VALIDATION.md`'s Per-Task Verification Map are
green. What is missing is a human judgment nobody has made yet and one line
of learner-facing copy nobody has written yet.

**It does not mean the scope question is reopened.** Weibao answered D-14B-5
on 2026-08-27 and chose option-a, freezing the vocabularies and the record
shapes and leaving copy and layout changeable. That answer stands. The plan's
own text is that Task 3 is asked only when the legs are green, so the answer
is recorded and simply not yet acted on.

**It does mean nothing here may be treated as durable.** Until this record
carries a freeze section, the sidecar file name and section order, the seven
table column sets, the four-name edge vocabulary and its three closed field
sets, the unknown-type downgrade rule, the eleven treatment kinds and their
rights mapping, the five migration kinds and three states, the seven-key
manifest and its five-key entry shape, and the five loss categories are all
still cheap to change. A later subphase composing onto them is composing onto
a prototype.

**It is not a course schema freeze either way.** Phase 14B is the reversible
prototype `PLANNING-DIRECTIVES.md` section 3a requires before a course schema
freeze. Both required prototypes exist: the graph-to-outline projection from
plan 14B-02 and the version migration from plan 14B-03. The course schema
freeze belongs to a later subphase, and a later phase inheriting this record
must not read it as one this phase made. That is true of a withheld freeze
and it would have been true of a granted one.

## Requirement status

`GRAPH-01`, `GRAPH-02`, `GRAPH-04`, and `PORT-03` remain `Pending` in
`.planning/REQUIREMENTS.md`. Plan 14B-06 Task 4 step 5 permits moving them to
`Complete` only when a freeze section was written, and none was.
`.planning/REQUIREMENTS.md` is untouched by this plan.

## What closes this

Two things, in either order.

1. Weibao opens the generated `course-graph.md` in a plain text editor and in
   Obsidian, answers the five questions in `14B-AUTHORABILITY-REVIEW.md`,
   hand-edits one `order` cell, confirms the re-projected outline reflects
   it, and records `authorable` or `not authorable` with the date.
2. One learner-facing phrase for `migrate` is added to
   `surfaces/visual_fixture.OPERATION_PHRASE`, and
   `tests/visual_system_roundtrip.py` and `tests/phase_062_audit.py` go
   green. The Anki-dependent reds need a closed Anki rather than a code
   change.

Then re-run plan 14B-06 Task 4. If both legs come back green it writes the
freeze against D-14B-5's recorded scope with no second checkpoint. A
`not authorable` verdict is a different outcome and is not a formality: it
would mean freezing seven column sets Weibao had just said he cannot read,
and the right response is to fix the shape and re-ask.
