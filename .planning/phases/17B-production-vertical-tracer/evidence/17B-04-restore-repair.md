# G10 repair and re-run: the clean-machine restore drill passes

Dated 2026-09-05, under Weibao's directive of the same day ("rather than
making me check things I want to properly utilize the capabilities of my
usage and just fulfil User vision"), which reaffirms his 2026-09-01
deferral directive. Wave 4 routed `17B-04 D-06 item 10` and `item 11`
rather than patching them, because both are contract changes in frozen
surfaces and D-06 bounds an in-phase fix to one file. This file records the
repair that followed, made deliberately as a contract change with its own
commit, and the drill re-run that judges it.

The bar is unchanged and is the requirement's own sentence: "Export is not
complete until a clean-machine, offline restore validates a manifest and
reports every loss, restoring all supported canonical objects and
evidence."

## What was wrong, in one paragraph each

**Item 10, rights could not be granted without editing the artifact.**
Rights live on a revision record, and until this repair the only way to
write a revision record was to commit new bytes. Granting an accepted
lesson the `package` right therefore required changing the lesson (a no-op
commit is refused `journal.no_change`), which the audit-before-editing rule
forbids. `journal.op_grant_rights` records the decision instead:
`write_target=False`, bytes and mtime untouched, revision advanced, the
grant merged onto the recorded rights so naming one right never resets the
others, and a right name or state outside `identity.RIGHTS_OPERATIONS` and
`identity.RIGHTS_STATES` refused by name. `_commit_impl` now also carries a
recorded rights record forward through later operations, so an edit no
longer silently erases a grant.

**Item 10, second mechanism, found only once the rights gate passed.** With
`package` granted, all six objects were still refused, now as
`external-link`. `link` is the only operation that binds a file already on
disk, so a course's own authored lesson, bank, objective list, and scope
file entered the journal as links, and `course_package` correctly refuses
to copy a linked object out of its owner's control. Only `course-graph.md`
crossed because `course.create_course` mints it. The missing vocabulary was
ownership, not permission: `journal.op_adopt` is the owner's recorded
decision that a bound file is the course's own artifact. Id, path, history,
and bytes are unchanged, the link entry stays in the log exactly as it was,
and an object that entered any other way is refused `journal.not_linked`.
An unadopted link is still never copied, which the package test asserts
both ways.

**Item 11, the evidence join.** `_evidence_export_lines` filtered by the
sidecar's `## Objectives` `id` column (graph object ids such as
`67b9a4f0cfab4cb8`) while the evidence log's `objective` field carries bank
slugs such as `afe:unit3.threshold`. The vocabularies never intersect, so
0 of 40 events exported and nothing said so. `course_package.evidence_scope`
now reads the course's bank names from the registry, which is a join that
exists on both sides today; a second pass carries whole sessions, so a mark
or a hint that carries no bank and no objective rides with the response it
resolves; and anything still unclaimed is named by the new
`evidence-not-carried` loss category rather than dropped. Another course's
history is still never exported, which the test asserts with a seeded
foreign event.

## The repair, as recorded operations on the fixture

Six objects, each adopted and then granted, through the two new operations
and nothing else. Every artifact was read before and after and is
byte-identical:

```
skip (not linked): course-graph.md
adopted + granted objective objectives.md
adopted + granted course scope.md
adopted + granted source sources/fen_hydrology_field_notes.md
adopted + granted source sources/lantern_moss_survey.md
adopted + granted bank unit3_bank.md
adopted + granted lesson unit3_lesson.md
every artifact byte-identical: True
```

`python3 itembank.py lint course_fixture_17b/unit3_bank.md` still exits 0
with `8 items, 0 errors, 0 warnings`.

## The drill, re-run

Same command as wave 4, same drill file, same judgment code (the driver
judges, the worker only reports, so a change to the code under test cannot
move its own bar):

```
python3 tools/restore_drill_17b.py --commit HEAD --workdir "$TMPDIR/17b_restore"
```

```
restore drill: repository /Users/weiwei/Documents/Dev/itembank
restore drill: commit 247ffbea177d83a721251f79aacb2697ef7203a0 (HEAD)
restore drill: workdir $TMPDIR/17b_restore2
restore drill: cloned at commit, HEAD 247ffbea177d83a721251f79aacb2697ef7203a0
restore drill: source course copied from course_fixture_17b
restore drill: fresh empty data directory $TMPDIR/17b_restore2/data
restore drill: network made unavailable (proxies at http://127.0.0.1:9, sockets refused, ITEMBANK_NO_NETWORK=1)
restore drill: network refused inside the worker = True
manifest: state applied, keys course_object_id, created, entries, loss_report, package_id, schema_version, state
manifest: 7 payload entr(y/ies) carried
  carried: bank unit3_bank.md (1672ba231fd446ee)
  carried: course course-graph.md (ba070378d35d44e7)
  carried: course scope.md (d035bddef2d84eff)
  carried: lesson unit3_lesson.md (36157b3e10cb46e5)
  carried: objective objectives.md (95abc1ccd3e241f9)
  carried: source sources/lantern_moss_survey.md (5c5bc6b17baa44c6)
  carried: source sources/fen_hydrology_field_notes.md (8bd25c20ceaa4e20)
manifest validation: 7 of 7 entries verified by recomputation, complete = True
restore: 7 of 7 entries verified, complete = True, evidence events recorded = 40
source registry: 7 canonical object(s); 0 did not reach the destination
evidence: 40 event(s) in the source log, 40 carried by the package
loss report: 1 row(s)
  [export] machine-local: settings
      not included by design; model backend configuration, update policy, and local paths belong to the machine, not to the course
restore drill: PASS
```

Judged by the drill's own failure list, all five conditions hold: the
worker could not open a socket, the manifest validated complete by
recomputation, the restore verified every manifest entry, no canonical
object was missing, and the source log's events were carried rather than
silently dropped.

## What this does and does not close

Closes: gate G10's own check. Seven of seven canonical objects and forty of
forty evidence events cross a clean detached clone, with an empty data
directory, an empty home, every proxy at the discard port, and sockets
raising inside the worker.

Does not close: the drill proves the tracer's one unit. Phase 17C's sweep
over every accepted item is still owed, and is the reason the drill takes
`--commit` rather than reading this working tree.

Not affected: the G4 screen-reader walk, the G8 visual acceptance at 1280
and 375, the G5 default rollup choice, and the milestone acceptance itself
all remain owed to Weibao and were not signed here (17B-CONTEXT D-04).

## Suite

Every `tests/*.py` after the repair: 101 pass, 4 fail. Two of the four
(`tests/daemon_roundtrip.py` and `tests/model_phase_roundtrip.py`, which
runs it) fail identically on a clean checkout of the previous commit with
`concurrent request N did not return 200: URLError(TimeoutError)`, a
loopback concurrency timeout in this environment and not a regression;
`tests/stylesheet_roundtrip.py` passes on its own for the same reason. The
fourth, `tests/visual_system_roundtrip.py`, was a real consequence of the
repair and is fixed here: every journal record type must carry a
learner-facing phrase, so `grant_rights` reads "recorded what may be done
with" and `adopt` reads "claimed as this course's own".
