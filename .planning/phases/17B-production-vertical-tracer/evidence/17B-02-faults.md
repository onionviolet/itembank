# 17B-02 evidence: the four file-fault drills on the authored unit (G3)

Recorded 2026-09-01 by plan 17B-02 Task 4, run from the repository root
with `python3` (`python` is not on PATH; recorded deviation). The drills
run through the frozen 14A operation surface (`journal.op_move`,
`journal.detect_external_edits`, `journal.op_edit_in_place`,
`journal.reconcile`, `journal.commit_operation`, `journal.replay`,
`journal.object_state`, the two-line prepared-then-resolved protocol),
driven by transcribed python3 scripts because 14A froze module surfaces
and no CLI command exists for these operations (`OPERATION-CONTRACT.md`
lists that surface as pending; same recorded deviation as Task 1). The
interrupted-write child mirrors `tests/journal_roundtrip.py`'s
`kill_before_commit` fixture exactly.

The truth under test: every fault leaves the old or the new valid state,
visibly, never a silent loss, a silent overwrite, or a mixed state.

Objects under drill: `unit3_lesson.md` (`36157b3e10cb46e5`, kind
`lesson`) and `unit3_bank.md` (`1672ba231fd446ee`, kind `bank`), both
linked into the course root's journal in Task 3.

## Drill (a): move, re-binding rather than silent loss

Commands (from `t4_faults.py`, invoked `PYTHONPATH=. python3
t4_faults.py`):

```python
r = journal.op_move(BASE, LESSON, "unit3_lesson_moved.md",
                    fp("unit3_lesson.md", "lesson"), "human", "weibao")
# ... lint the dependent bank while the lesson is at the new path ...
r = journal.op_move(BASE, LESSON, "unit3_lesson.md",
                    fp("unit3_lesson_moved.md", "lesson"), "human", "weibao")
```

Observed output, verbatim:

```
== drill (a): move unit3_lesson.md, confirm re-binding ==
moved: registry path=unit3_lesson_moved.md revision=2 state=clean
old path exists: False
bank lint while lesson is moved (dependent breakage is VISIBLE, not silent): exit=1
error  Q1: LESSON-REF 'Two Layers, Two Clocks' does not match any lesson heading
error  Q2: LESSON-REF 'Why The Fen Is Minerotrophic' does not match any lesson heading
error  Q3: LESSON-REF 'Read The Source: The Lagg Boundary' does not match any lesson heading
error  Q4: LESSON-REF 'The Annual Cycle Of Lantern Moss' does not match any lesson heading
error  Q5: LESSON-REF 'The Drought Threshold' does not match any lesson heading
error  Q6: LESSON-REF 'Banking Peat' does not match any lesson heading
error  Q7: LESSON-REF 'Moss As Instrument' does not match any lesson heading
error  Q8: LESSON-REF 'Moss As Instrument' does not match any lesson heading
error  BANK: [LESSON-SRC: unit3_lesson.md] could not be read ([Errno 2] No such file or directory: '/Users/weiwei/Documents/Dev/itembank/course_fixture_17b/unit3_lesson.md') -- fix the path or remove the directive

8 items, 9 errors, 0 warnings
moved back: registry path=unit3_lesson.md revision=3
```

Verdict: pass. The object id survived the move, the registry re-bound to
the new path with an advanced revision and `clean` state, the previous
path was removed so the bytes live in exactly one place, and the
dependent bank's breakage while the lesson sat at the new path was loud
(nine named lint errors), never silent. Moving back re-bound again at
revision 3 and the bank lints clean (verbatim re-lint at the bottom).

## Drill (b): external edit, stale or conflict, never silent overwrite

Commands: append one line to `unit3_bank.md` outside the journal, then:

```python
affected = journal.detect_external_edits(BASE)
journal.op_edit_in_place(BASE, BANK, "bank", "unit3_bank.md",
                         b"attempted overwrite through a stale base\n",
                         accepted, "human", "weibao")   # accepted = pre-edit fingerprint
```

Observed output, verbatim:

```
== drill (b): external edit to unit3_bank.md ==
detect_external_edits: ['1672ba231fd446ee']
object_state after external edit: conflict
stale write refused: code=journal.stale_preflight
```

Recovery (from `t4_faults_cd.py`): `journal.reconcile` choosing the
observed on-disk fingerprint (the recorded human decision the module
requires; there is no merge and no auto-revert), then a journaled
`op_edit_in_place` restoring the accepted bytes with the true current
base:

```
== drill (b), recovery ==
restored through the journal; object_state: clean
```

One observed nuance, recorded rather than glossed: after
`detect_external_edits` appends its record, the registry row's
fingerprint tracks the observed on-disk value, so a `reconcile` naming
the pre-edit accepted fingerprint refuses with `journal.stale_preflight`
(first attempt, transcript kept in the Task 4 run log below). The
recovery path that works is reconcile on the observed state, then a
journaled restoring edit. Nothing was overwritten silently at any step.

Verdict: pass. The external edit was detected and surfaced as
`conflict`, the stale write was refused with the typed
`journal.stale_preflight` code, and recovery went through the journal.

## Drill (c): same-ID divergent bytes is a conflict

Commands: write wholly divergent bytes to `unit3_bank.md` (same object
id on the recorded path, different content), then attempt a write that
believes the accepted base:

```
== drill (c): same-ID divergent bytes is a conflict ==
object_state with divergent bytes on disk: conflict
write against the divergent copy refused: code=journal.conflict
accepted bytes restored by hand; object_state: clean
```

Verdict: pass. Same id with divergent bytes read as `conflict`, never a
silent overwrite, and the attempted write was refused with the typed
`journal.conflict` code. The accepted bytes were restored and the state
read `clean` again.

## Drill (d): interrupted write leaves old or new valid state

The child process (`t4_child.py`, mirroring
`tests/journal_roundtrip.py`'s `kill_before_commit`) shims
`journal._write_bytes_atomic` to stall inside the target write and is
killed one second in:

```
== drill (d): interrupted write, kill mid-operation ==
bytes after kill are the OLD valid state: True
journal ends with unresolved prepared entry: True
replay classifies the entry as interrupted: True
object_state: interrupted
```

Recovery: the unresolved `prepared` entry (`4dd86656b8774c59924c7b00564d4b12`)
was resolved by appending a `refused` record naming it via
`resolves_entry`, per the frozen two-line prepared-then-resolved
protocol; the abandoned operation is legible in the journal forever:

```
unresolved prepared entry: 4dd86656b8774c59924c7b00564d4b12
refused resolution appended: 759661398066424c945e16cfcf2d55bf
object_state: clean
replay interrupted list now: []
```

Verdict: pass. The kill landed between the `prepared` append and the
atomic replace; the old valid bytes survived intact, the journal showed
the unresolved `prepared` entry, `replay` re-read the disk and
classified it `interrupted` honestly, and the resolution was an
append-only record, never a rewrite.

## After all four drills

Run verbatim from the repository root:

```
$ python3 itembank.py lint course_fixture_17b/unit3_bank.md

8 items, 0 errors, 0 warnings
```

Exit 0. The authored unit survived all four drills in the old valid
state, and every fault was visible in the journal or the linter at the
moment it existed.

No drill required a capability the frozen surface could not express, so
no D-06 defect arises from this task. The absence of a CLI command for
these operations is the already-recorded pending surface in
`OPERATION-CONTRACT.md`, restated here rather than rediscovered.
