# 17B gate checklist

The acceptance record for Phase 17B (17B-CONTEXT D-04): one row per gate
G1 through G11, the concrete check transcribed from the ROADMAP 17B
details block, the proof command or fixture, the evidence pointer, and
the state. Scaffolded 2026-09-01 by plan 17B-01 with every row pending;
later waves fill proof, evidence, and state, and 17B closes with every
row either passed or carrying a named defect and a named owner (D-06).

| gate | concrete check | proof command or fixture | evidence pointer | state |
|---|---|---|---|---|
| G1 Coverage | every capability the tracer exercises maps to its requirement row and ledger disposition; no undischarged tracer promise | the wave-2 capability map (15 rows exercised, each with requirement row and disposition) plus the owed-promise table naming the wave that discharges each remaining gate; `python3 itembank.py lint course_fixture_17b/unit3_bank.md` exits 0 with 0 errors 0 warnings | evidence/17B-02-coverage.md | pass (wave 2 scope; rendered, sitting, restore, and egress rows owed to 17B-03/17B-04 per the table in the evidence file) |
| G2 Object/authority | each artifact the tracer creates names its durable object, owner, authority, and source of truth; derived views rebuild | the transcribed binding flow over `course_fixture_17b/` (14A `journal.op_link`, 14B `course.create_course`/`bind_source`), registry deleted and rebuilt from the journal log alone (`identical = True`) | evidence/17B-02-binding.md | pass |
| G3 File safety | the tracer's unit survives the file-fault drills (move, external edit, conflict, interrupted write) preserving old or new valid state | the four transcribed drills on `unit3_lesson.md`/`unit3_bank.md` through the frozen 14A surface (`op_move`, `detect_external_edits`, `journal.stale_preflight`, `journal.conflict`, kill-mid-commit with `replay` naming the interrupted entry); re-lint exits 0 afterward | evidence/17B-02-faults.md | pass |
| G4 Portable capability | the authored lesson reads coherently in plain Markdown outside the UI, and in the UI by keyboard, touch, screen reader, narrow screen, and offline | pending | pending | pending |
| G5 Evidence honesty | progress over the tracer's scope tree (one open field containing one bounded course containing the unit) renders in both registered rollup models, ROLLUP-DIM and ROLLUP-MAP (IDEA-LEDGER IL-20260817-01), with stated denominators, pending and unknown states shown, and no aggregate score anywhere; the bounded course may complete, the open field never does. Weibao picks the default rollup from the rendered screens | pending | pending | pending |
| G6 Assessment authority | no surface, agent, or note in the tracer leaks a key, invents a score, auto-grades prose, or changes a frozen sitting | pending | pending | pending |
| G7 Course quality | the tracer's treatment decisions cite scope, demand, rationale, uncertainty, and the existing-artifact search, and pass review before authoring | `course_fixture_17b/treatments.md` (six fields per objective, seven review verdicts recorded through `director.record_phase` before Task 3 authored anything; operation ids in the file) | evidence/17B-02-coverage.md and course_fixture_17b/treatments.md | pass |
| G8 Flow/visual | first-run, resume, learn, practice, test, source inspection, review, agent failure, and narrow-screen transitions preserve context and hierarchy on the tracer's unit | pending | pending | pending |
| G9 Strategy/notes | each strategy the tracer offers states choice, requirement, skip and resume, accommodation, evidence effect, privacy, provenance, and the note-authority guard | pending | pending | pending |
| G10 Portability/recovery | a clean machine restores the tracer's canonical objects and evidence offline; every unsupported capability appears in a loss report | pending | pending | pending |
| G11 Cross-cutting | egress capture equals disclosed manifests; rights-unknown refuses unsafe operations; diagnostics are redacted | pending | pending | pending |

Human checkpoints are mandatory for the G4 screen-reader item and the final visual acceptance; an agent never self-certifies those (17B-CONTEXT D-04).
