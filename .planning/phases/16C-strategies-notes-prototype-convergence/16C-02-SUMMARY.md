# 16C-02 summary

**Plan:** 16C-02, the shared synthetic corpus and the learner-note schema.
**Executed:** 2026-08-29. **Tasks:** 3 of 3.

## What landed

| Artifact | What it is |
|---|---|
| `fixtures/note_strategy_corpus.py` | Four fictional subjects, deterministic, written only to caller directories |
| `notes.py` | The NOTE-01 record, seven closed vocabularies, one hashing helper, four relocation states, an atomic writer, one reader |
| `schemas/note.schema.json` | The sidecar contract, inside `schema_validate.SUPPORTED` |
| `tests/note_schema_roundtrip.py` | Eight checks, green |
| `surfaces/cli.py` | One additive corpus-marker branch, `note_document_id` |

## Task 1: the corpus

| Subject | File | Items | Headings | Terms | Typed relations |
|---|---|---|---|---|---|
| `emt_respiratory` | `emt_respiratory_bank.md` | 2 | 4 | 4 | 4 |
| `math_linear_system` | `math_linear_system_bank.md` | 2 | 4 | 4 | 4 |
| `cs_loop_invariant` | `cs_loop_invariant_bank.md` | 2 | 4 | 4 | 4 |
| `history_conflicting_accounts` | `history_conflicting_accounts_bank.md` | 2 | 4 | 4 | 4 |

Building twice into two temp directories produced byte-identical files
(`deterministic True 4`). Every relation slug resolves to a real heading slug
in its own subject, checked rather than assumed. `revise_lesson` on
`emt_respiratory` returned `when-the-numbers-disagree` and that slug is gone
from the reparsed bank.

**One deviation, found by running rather than by reading.** The first
`_terms_block` wrote a Markdown header row and a separator row, in the shape
tables take elsewhere in the repository. `parse_terms` counts any two-cell row
as a term, so the header parsed as a glossary entry named "Term" and every
subject reported five terms instead of four. The shipped fixtures
(`fixtures/terms_above_lesson_bank.md`) carry no header for exactly that
reason. Fixed by writing bare `canonical | definition` rows, with the reason
recorded in the helper's docstring so the next author does not reintroduce it.
The count assertion would have passed either way, since five is more than
four, which is what makes this worth writing down: the check that caught it
was reading the parsed output, not counting it.

## Task 2: notes.py and the schema

All seven vocabularies match D-16C-8 exactly. Every validated field raises
`ValueError` naming its unknown member, asserted for epistemic role,
authorship type, note status, and target kind. Every capture and anchor string
matches the UI-SPEC Copywriting Contract verbatim; the test writes the
expected strings out in full rather than comparing the module to itself, so a
silent edit on either side fails. The seven `role_choices` map positionally
onto the seven `EPISTEMIC_ROLES`, asserted by length.

`resolve_anchor` drives all four relocation states in the test:

- untouched heading: `resolved`
- same body under a renamed heading: `relocated_exact`
- the same body under two headings: `relocated_probable`, two candidates
- **the revised heading: `orphaned`**, the state the real
  `revise_lesson` fixture produced. The plan's flagged assumption anticipated
  either `orphaned` or `relocated_probable` depending on body collisions, so
  the test asserts membership in that pair and prints which occurred rather
  than pinning one. The note's `objective_ids` are unchanged across the
  revision, which is NOTE-01's degraded contract.

`resolve_anchor` mutates nothing and re-anchors nothing. The tier rule is
asserted over `notes.py`'s source with `ast`, covering module-level and
function-level imports both: no `runtime`, nothing from `surfaces`.

The schema passes `python3 schema_validate.py --all schemas` (21 documents
self-check clean) and rejects a sidecar carrying `status: "archived"`.

`check_atomic_write` plants a half-written `notes.md.json.tmp` beside a valid
pair; the reader still returns the last accepted sidecar. `check_authored_zero`
confirms authored pre-highlighting carries `authorship: "authored"`, an empty
`owner`, and leaves the temp evidence path absent: zero events, zero
ownership.

## Task 3: the guard marker

The marker landed as one branch inside the existing `_corpus_marker` helper
plus one module constant beside `CORPUS_SECTION_MARKERS`. No second walker, no
new command, no skip-list entry. `git diff --stat surfaces/cli.py` reports 13
insertions and 2 deletions in that one function and its constants.

Stray-note temp run:

```
error  /tmp/.../stray_note.md carries the corpus marker note_document_id. Banks and corpus content belong in your private vault, never in this repo.

1 offending files
```

exit 1. Repository run: `0 offending files`, exit 0.

## Verification, with actual final lines

```
python3 tests/note_schema_roundtrip.py     ->  NOTE SCHEMA: 8 passed, 0 failed   (exit 0)
python3 tests/guard_roundtrip.py           ->  exit 0
python3 tests/import_roundtrip.py          ->  exit 0
python3 schema_validate.py --all schemas   ->  21 schema documents self-check clean
python3 itembank.py guard .                ->  0 offending files
```

No file this plan wrote contains an em dash character, verified with the
`chr(0x2014)` form. `surfaces/cli.py` carries pre-existing em dashes; every
line this plan added to it was checked separately and carries none.

## Full-suite state, reported rather than smoothed over

The whole suite was run (`for f in tests/*.py`). Two files failed and neither
is 16C's:

1. **`tests/selection_retention_roundtrip.py` fails on a clean tree.**
   `FAIL: the weak objective must fill the sitting: ['q3', 'q1']`. Confirmed
   pre-existing by stashing every 16C change and re-running, then by a
   worktree bisect over about 45 commits which found it failing at every one,
   including `66322ff`, the commit that introduced the test. Also fails on
   Python 3.13 and when run from a different working directory. It is not
   this plan's, it is not recent, and it is recorded here rather than fixed
   because diagnosing it properly is its own task.
2. **`tests/model_phase_roundtrip.py` failed once and passes on repeat.** The
   failure was `concurrent request 2 did not return 200: HTTPError 400` in
   its daemon leg. Two clean re-runs pass. Recorded as a flake in that test's
   concurrency leg, not as a result.

One side effect worth naming: running the full suite rewrites
`.planning/phases/14A-identity-lifecycle-operation/14A-TRACER-REPORT.md` with
freshly measured numbers. It was restored with `git checkout` rather than
committed, the same treatment commit `53d5231` gave it.

## Deviation from the plan

The plan's commands are written as `python`; this machine has only `python3`,
the deviation `16C-PRECONDITION.md` records as item 3. Nothing else changed.
