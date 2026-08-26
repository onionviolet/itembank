# 14B-01 summary: the thin slice, walked end to end

**Executed 2026-08-26.** One synthetic objective traveled mint, edge, sidecar
compare-and-swap write, outline projection, package export, and clean-machine
restore in one green test, and the three new modules exist in their thinnest
production-quality form.

## Task 1: the precondition result

Phase 14A has landed. `identity.py`, `journal.py`, and `discovery.py` import,
`14A-FREEZE.md` exists and carries `## Frozen at 14A`, and every constant and
callable in the check list matches, with exactly one exception recorded below.
The full evidence is in `14B-PRECONDITION.md`.

### The one deviation the landed 14A surface showed against the 14A plan text

| Item | 14B plan text | 14A-FREEZE.md | Landed `journal.py` |
|---|---|---|---|
| `len(journal.ENTRY_KEYS)` | 22 | 23 | 23 |

The twenty-third key is `rights`, added by plan 14A-03 when rights state
landed, after plan 14A-02 (the source 14B transcribed its check list from) had
fixed the count at 22. The landed module and the frozen record agree; only the
14B transcription of an intermediate 14A draft disagreed with both.

**This was recorded rather than halted, and the reasoning is stated so a later
reader can disagree with it on the merits.** Task 4 directs a halt on any
failing check, and the halt exists to stop 14B writing code against a surface
that is not really there. The authority the halt message itself names is
`14A-FREEZE.md`, and the landed surface matches it exactly. The divergent item
is a count no Phase 14B code consumes: a repository-wide search finds it only
inside the precondition assertion itself. `course.py` reaches the journal only
through `journal.commit_operation` and never enumerates entry keys, so the
extra `rights` key is invisible to every module this phase creates. Halting on
a stale transcription of a number nothing reads would have stopped the wave
over bookkeeping, the same class of error the 2026-08-25 ROADMAP correction had
to undo for the 13.9 row.

The frozen record being the authority, the plan text was corrected in place:
`14B-01-PLAN.md` Task 1 step 2 and its automated verify command, and
`14B-VALIDATION.md` row 14B-01, now read 23. Plans 02 through 06 were re-read
against `14A-FREEZE.md`; no further divergence was found.

## Task 2: the option chosen, and by whom

**option-a**, the separate `course-graph.md` file with a non-destructive
migration. Phase 14B never opens `course.md` for writing.

**Weibao did not answer this checkpoint.** He authorized overnight execution
and was away, so the orchestrating session recorded the plan's own named
RECOMMENDED DEFAULT and marked it provisional in `14B-DECISIONS.md`, with the
slot for his verbatim answer left open and both reversal recipes written out.
This is an agent decision standing in for a one-way call, and it is flagged as
such rather than presented as settled.

The default is the safe stand-in on evidence, not merely the convenient one.
`13.9-CALIBRATION.md` records the walking skeleton's course root as
`~/Documents/itembank-courses/emt-unit-1` with `course.md` as its course stub,
so that file already holds a real, hand-approved objective map for a live fall
course, covered by no fixture and no repository backup. The in-place upgrade
would have had a tool rewrite exactly that file while its author was asleep.

**Plan edits this choice forced in plans 02 through 06: none.** Those plans are
already written for option-a. Nothing was edited.

## Which truth was verified by which command

| Truth | Command | Result |
|---|---|---|
| 14A landed with the planned surface, or the wave halts by name | `python3 -c "import identity, journal, discovery; assert ..."` | `14A surface matches`, one deviation recorded |
| One objective travels mint to restore in one commit | `python3 tests/graph_roundtrip.py` | `OK graph_roundtrip` |
| The sidecar is one kind=course object with one lineage | `check_thin_slice` registry and revision assertions | one registry entry, kind `course`, revisions 1 then 2, stable object id |
| 14B mints no new member of `identity.OBJECT_KINDS` | `python3 -c "import graph, course, course_package, identity; print(len(identity.OBJECT_KINDS))"` | `6`, and `edge` is absent |
| 14B never writes `course.md` | stub bytes compared before and after `migrate_stub` | byte-identical |
| Empty and single-objective projections | `outline_projection` assertions | exact expected text |
| The format is additive by construction | byte-identical round trip with `## Cohorts` and an `owner` column | equal, byte for byte |
| A clean restore verifies rather than trusts | restore into a directory with no journal, registry, or evidence | `entries_verified` 1, `complete` True, bytes equal |
| No dependency on real content | `python3 itembank.py guard .` | `0 offending files` |
| Tier boundaries are structural | `hasattr` assertions on all three modules | `graph` has no `model`, `journal`, `os`, `evidence`; `course` has no `evidence`; `course_package` has no `urllib`, `socket`, `subprocess` |

Degraded states proven, each with its own assertion: a future schema version
refused by name with both versions in the message; a malformed section refused
with the file provably unchanged (`graph.py` does no file input or output at
all); a stale compare-and-swap write refused by `journal.stale_preflight` with
the bytes on disk unmoved; an export interrupted in the `prepared` state
refused by `package.not_applied`; a corrupted payload byte caught by
recomputation; and three traversing package entries refused rather than
clamped.

## Measured wall-clock time

`check_thin_slice()` runs in **0.01 seconds**, measured, over three
consecutive runs that each reported the same figure. This is measured and not
promised; the test prints its own elapsed time on every run.

## The test was falsified before it was trusted

A green test that asserts nothing is worse than no test. Three invariants were
deliberately broken to confirm the assertions have teeth: dropping unknown
columns on re-serialization was caught by the byte-identical round trip;
making `restore_package` trust the manifest instead of recomputing was caught
by the corrupted-payload assertion. A third, removing the absolute-path guard
from `safe_target`, was **not** caught, because the `os.path.commonpath`
containment check catches an absolute path on its own. That is correct
defense in depth rather than a hole, and it is recorded here so a later reader
knows the two guards overlap by design and that the test asserts the refusal
rather than which guard produced it.

## Deviations from this plan, with reasons

1. **`graph.split_row`, `graph.is_rule_row`, and `graph.new_record` are public
   names, not underscore-private.** `course.py` reuses them to read the Phase
   13.9 stub's tables. The alternative was a second pipe-table reader in
   `course.py`, which is exactly the duplication this phase exists to avoid.
2. **Every record carries a `columns` key beside `extra`.** The plan asks that
   an unknown column be re-emitted in its original column position, and the
   document is required to carry exactly nine named keys, so the column layout
   has nowhere else to live. Storing it per record keeps the nine-key document
   shape and makes the byte-identical round trip hold for an unknown column in
   any position rather than only at the end. Known gap: a section whose table
   is empty *and* carries unknown columns loses those column names, because no
   record exists to hold the layout. No fixture reaches that case; recorded
   here rather than discovered later.
3. **`add_edge` mints no id.** Step 7 says each of the three adders mints a
   record id, but the locked decision table in the same plan says an edge is
   identified by the tuple `(source, edge_type, target)` and is never given a
   minted id. The decision table wins; `EDGE_COLUMNS` has no id column.
4. **`migrate_stub` also refuses with `course.sidecar_exists` when a sidecar
   already exists.** Not in the plan. Without it, migrating twice would write a
   second course object over the first one's bytes, since the new object id
   makes the journal see no previous revision to guard.
5. **`restore_package` journals each entry with `operation="restore"`**, an
   existing member of `journal.RECORD_TYPES`, so a restored course carries the
   destination's own journal from its first byte.
6. **`course_package.read_manifest` is a public function not in the plan's
   symbol list**, used by `restore_package` and useful to plan 14B-05.
7. **`fixtures/corpus_14b.build_three_domains` builds only the first domain**,
   as the plan directs, but all three domains are already declared in the
   `DOMAINS` tuple so plan 14B-02 widens a loop bound rather than writing a
   second fixture.

## Suite state at the end of this plan

72 of 75 suites pass. The three failures are **pre-existing and unrelated**:
`day_roundtrip.py`, `retention_ui_roundtrip.py`, and `phase_062_audit.py`
(which runs the suite and reports the first two) assert the exact copy printed
"with Anki closed", and Anki is running on this machine, so the real deck
counts appear instead. Verified by stashing every change in this plan and
re-running both on the clean tree, where they fail identically. No worktree
existed during the run, so the `evidence_roundtrip` one-writer scan and the
`model_phase_roundtrip` scorer scan were not tripped by parallelism.

## What this plan deliberately did not do

No CLI command, no daemon route, no schema file, and no skill documentation, as
`<out_of_scope>` requires. `journal.py`, `identity.py`, `discovery.py`,
`model.py`, `runtime.py`, and everything under `surfaces/` and `schemas/` are
untouched, confirmed by `git status`.
