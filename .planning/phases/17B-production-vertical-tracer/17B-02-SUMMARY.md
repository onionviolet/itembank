# 17B-02 summary: the fixture unit authored through the skills

**Executed 2026-09-01, all four tasks complete and verified.** Discovery
through accepted authoring ran end to end on `course_fixture_17b/`:
binding and inventory with the object and authority record (G2), the
reviewed treatment decision per objective (G7), the unit lesson and bank
authored through the skill playbooks and the lint loop (G1), and the
four file-fault drills (G3). Three D-06 items were recorded, one of them
an in-phase single-file fix. Gate rows G1, G2, G3, G7 flipped from
`pending` to `pass`, each with an evidence pointer into `evidence/`.

## Recorded deviations

- `python` is not on PATH on this machine; every command ran as
  `python3` (the 16C precedent deviation, also recorded by 17B-01).
- The discovery, binding, operation, and review flows were driven
  through the frozen module surfaces invoked by transcribed python3
  scripts (`PYTHONPATH=. python3 <script>` from the repository root),
  because the freeze records freeze module contracts and
  `OPERATION-CONTRACT.md` lists the discovery/binding/operation CLI
  surface as pending (14A/14B). No command was invented; every call is a
  frozen item of its freeze record. Scripts are transcribed verbatim in
  the evidence files.

## Frozen-contract commands used, with their source freeze files

| frozen surface used | source of the freeze |
|---|---|
| `journal.op_link`, `journal.op_move`, `journal.op_edit_in_place`, `journal.commit_operation`, `journal.detect_external_edits`, `journal.reconcile`, `journal.replay`, `journal.object_state`, `journal.rebuild_registry`, the two-line prepared-then-resolved protocol and the 24 entry keys | `14A-FREEZE.md` (operations, journal protocol; entry-key count as amended by 15A) |
| `identity.new_object_id`, `identity.object_fingerprint`, `identity.rights_default`, the rights states and RIGHTS-01 restrictive-unknown rule | `14A-FREEZE.md` |
| `course.create_course`, `course.read_course`, `course.write_course`, `course.bind_source`, `course.bind_treatment`, `graph.add_container`, `graph.add_objective`, `graph.add_source`, `graph.outline_projection`, the `course-graph.md` sidecar and section order | `14B-FREEZE.md` (and its 15B Blueprint amendment) |
| `graph.TREATMENT_KINDS` and the per-kind rights mapping | `14B-FREEZE.md` table; policy contract per `15A-FREEZE.md` |
| `director.begin_operation`, `director.record_phase`, `director.protocol_report`, the thirteen protocol steps, `draft-and-review` autonomy | `15A-FREEZE.md` |
| review-before-authoring discipline (verdict recorded per decision before any draft) | `15B-FREEZE.md` review mechanics, applied at the treatment seam |
| semantic roles, `## TERMS`/`## MEDIA`/`## ACTIVITIES` grammar, `[LESSON-SRC:]`, capability lint codes | `16A-FREEZE.md` |
| `python3 itembank.py lint / stats / coverage / id-assign / guard / lesson / build` | shipped surfaces per `OPERATION-CONTRACT.md` |

Skill playbooks followed: `author-bank` (declare, inventory via
`spec`/`stats`/`coverage`, draft, lint-fix-lint, statistical review,
preview both forms, `id-assign` after acceptance, `guard`),
`build-course` and `curriculum-design` (operation manifest, treatment
table, review), `absorb-book`'s shipped `## LESSON` contract for the
lesson (the `lesson-authoring` skill is a stub; defect 3 below).

## What was produced

- `course_fixture_17b/course-graph.md`: the course sidecar, revision 24
  at rest: 1 unit container, 7 objectives, 2 source rows, 7 source
  bindings and 15 treatment bindings, all locator-cited.
- `course_fixture_17b/treatments.md`: 7 decision blocks, each with
  treatment, scope, demand, rationale, uncertainty, and the explicit
  `no prior artifact found` search result; 7 review verdicts with
  operation ids; O3.5 is direct source reading with a `[SRC:]` locator,
  O3.1/O3.2/O3.6/O3.7 are lesson plus practice.
- `course_fixture_17b/unit3_lesson.md`: the durable authored lesson,
  coherent standalone: term references, a `[!KEY]` things-to-know card
  (id `76f829119a7142fd` minted by `id-assign`), a `[!TIP]` expert tip,
  `[!EXAMPLE]`, `[!MISCONCEPTION]`, `[!UNCERTAINTY]`, `[!SUMMARY]`, a
  prediction prompt before the explanatory content, a cited
  `[MEDIA: moss-cycle]` visual with static fallback, `[SRC:]` locators
  on every source-derived section, and the synthesis section labeled.
- `course_fixture_17b/unit3_bank.md`: 8 items (5 mc, 1 multi, 1 build,
  1 short with MODEL and a three-point RUBRIC; Q8 is the changed-context
  transfer item), every item cited to an objective and a source locator,
  `## TERMS`, `## MEDIA` (alt, rights, derivation, sha256 integrity),
  `## ACTIVITIES` (a `prediction` row with `activity_trace`
  participation-only evidence, practice, explanation, transfer),
  `[LESSON-SRC: unit3_lesson.md]`, ids and hashes minted.
- `course_fixture_17b/media/lantern_moss_cycle.svg`: the synthetic cycle
  diagram (title, desc, four phases, the hinge marked).
- Evidence: `evidence/17B-02-binding.md`, `evidence/17B-02-coverage.md`,
  `evidence/17B-02-faults.md`.

## Lint and guard outputs, verbatim

Final state, from the repository root:

```
$ python3 itembank.py lint course_fixture_17b/unit3_bank.md

8 items, 0 errors, 0 warnings
```

Exit 0. (First pass had 6 errors, all registry placement, fixed by
moving `## TERMS` and `## MEDIA` into the bank preamble the linter
reads; the loop is transcribed in the evidence files.)

```
$ python3 itembank.py guard .
0 offending files
```

Exit 0. Pre-fix guard output, preserved per D-06 item 1:

```
error  ./course_fixture_17b/unit3_lesson.md carries the corpus marker (?m)^##\s+SOURCES\s*$. Banks and corpus content belong in your private vault, never in this repo.
error  ./course_fixture_17b/unit3_bank.md parses as a question bank (8 items). Banks and corpus content belong in your private vault, never in this repo.

2 offending files
```

Em dash checks: the plan's Task 2 command printed `no em dash`, exit 0;
a chr(8212) scan over every file this plan wrote is clean (the one hit
in `surfaces/cli.py` is pre-existing at line 1541, in a comment this
plan did not touch). `python3 tests/guard_roundtrip.py` passes (4
checks) after the guard fix; `journal_roundtrip` and
`operations_roundtrip` also exit 0.

`stats`: mix 5 mc / 1 multi / 1 build / 1 short; difficulty 5
application, 2 analysis, 1 recall; answer positions A 1, B 1, C 2, D 1.
`coverage`: all 7 objectives covered.

## Gate rows after this plan

| gate | new state |
|---|---|
| G1 Coverage | pass (wave-2 scope; the owed-promise table in evidence/17B-02-coverage.md names 17B-03/17B-04 for every remaining row) |
| G2 Object/authority | pass |
| G3 File safety | pass |
| G7 Course quality | pass |

G4, G5, G6, G8, G9, G10, G11 remain `pending`, owed to waves 3 and 4 as
scaffolded.

## Fault drill outcomes (G3), condensed

Full transcripts in `evidence/17B-02-faults.md`.

- **(a) move**: object id survived, registry re-bound
  (`unit3_lesson_moved.md`, revision 2, state clean), old path removed,
  dependent bank breakage loud (9 lint errors while moved), moved back
  clean at revision 3.
- **(b) external edit**: detected (`detect_external_edits` named the
  object), state `conflict`, stale write refused with
  `journal.stale_preflight`, recovery via `reconcile` plus a journaled
  restoring edit; one reconcile nuance recorded honestly in the
  evidence.
- **(c) same-ID divergent bytes**: state `conflict`, write refused with
  `journal.conflict`, never a silent overwrite; accepted bytes restored.
- **(d) interrupted write**: child killed mid-commit; the OLD valid
  bytes survived byte for byte, the journal ended with an unresolved
  `prepared` entry, `replay` classified it `interrupted`, and the
  resolution was an appended `refused` record naming it. Re-lint after
  all four drills: exit 0, 0 errors, 0 warnings.

## D-06 defects, with mechanism and owner

1. **guard versus the fixture course (in-phase fix, one file).**
   Mechanism: `cmd_guard`'s directory skip list predates 17B-CONTEXT
   D-02's decision to keep a synthetic fixture course at the repository
   root, so D-02's own pair of requirements (fixture in-repo AND guard
   clean) was mechanically unsatisfiable once the unit bank existed.
   Fix: `surfaces/cli.py` skips `course_fixture_17b` by name with a
   comment citing D-02; neither refusal class was weakened and no
   contract changed. Owner: 17B (its own fixture rule).
2. **`[!KEY: <title>]` lint false positive (recorded, not fixed).**
   Mechanism: `model.py`'s semantic-role check compares the raw callout
   marker against `surfaces.lesson._CALLOUT_KINDS` directly instead of
   routing through `surfaces.lesson._callout_kind_of`, which maps
   `KEY:`-prefixed markers to the KEY index card; the renderer honors
   the documented form and the linter warns on it
   (`lesson.unknown_semantic`). Workaround: the corpus-established
   `> [!KEY] <title>` form, used in unit3_lesson.md. Owner: Phase 16A.
3. **`lesson-authoring` skill still a stub (recorded gap).** The lesson
   was authored against the 16A capability contract directly plus
   `absorb-book`'s shipped `## LESSON` contract, exactly as the stub
   instructs. Owner: the subphase that ships the lesson-authoring
   command surface (16A, its named prerequisite, has shipped; the skill
   rewrite is still owed).

No drill and no authoring step required a hosted-model call; the D-09
egress record in `evidence/17B-02-binding.md` says so at call time.

## Next safe action

Wave 3 (17B-03): the learner pass on this unit (G4, G5, G6, G8, G9),
including the mandatory human checkpoints for the screen-reader item and
the D-03 rollup choice.
