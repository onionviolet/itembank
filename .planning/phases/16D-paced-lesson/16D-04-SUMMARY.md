# 16D-04 summary

Task 1 executed 2026-08-31. Task 2, Weibao's sat-through review and the
freeze decision, is NOT closed here: the same discipline that held 17A-04's
checkpoint holds this one, and the standing five-phase agent-signature
question makes an agent exactly the wrong signer.

## What shipped

`tests/paced_lesson_tracer.py`, eight scenarios in the
cross_subject_suite_tracer house style, all green in about 3 seconds:

1. `scenario_ladder`: all three rungs resolve (markers, heading slugs,
   whole document).
2. `scenario_full_sitting`: one served paced sitting over HTTP: step 1 of
   3, tier 1 and 2 on the first wrong checkpoint, tier 3 on the second,
   resume at the recorded step, TOC jump to the last step.
3. `scenario_resume_across_edit`: inserting an earlier `[STEP:]` marker
   leaves the recorded resume id resolvable (identity survives edits);
   removing the recorded marker itself fires the honest fallback line and
   step 1, never a guessed neighbour.
4. `scenario_denominator`: 5 rows, 2 labelled `lesson_run`, proposal
   denominator 3.
5. `scenario_exam_contrast`: exam and diagnostic checkpoints refused by
   name; the plain lesson route carries no paced chrome.
6. `scenario_rung3_byte_identity`: a markerless, pace-less lesson is one
   step, and the served plain page is deterministic across GETs.
7. `scenario_reconsideration_probes`: the D-PACED reconsideration
   conditions checked rather than assumed. The fixture uses authored
   markers (reported, informational); tier 1 leaves 3 of 4 mc options
   unresolved after one wrong single pick, so the ladder does not make the
   item trivially solvable; a rows list of only `lesson_run` attempts
   produces denominator 0 and uncertainty `no-evidence`, so nothing
   labelled reaches a denominator unpoliced.
8. `scenario_layout_leg`: `tools/visual_qa.py --json -` (the 17A-04 seam)
   runs when Playwright is installed and reported a clean matrix; absent,
   the scenario prints the honest skip and passes.

Written by a subagent executor against the plan, verified and re-run by the
orchestrating session; stable across repeated runs; guard clean.

## One behaviour surfaced worth keeping

GET-based step navigation updates the recorded resume position, not only
checkpoint POSTs. The tracer's resume scenario therefore re-navigates to
its intended step before editing the lesson, with a comment saying why.
This is the intended reading of "position is presentation state": the
newest position is the position, however it was reached.

## What Task 2 needs from Weibao

Sit the paced fixture lesson end to end in a browser (keyboard once,
pointer once, one wrong checkpoint each way, the TOC jump, the resume),
review accessibility per the standing rules, then write `16D-FREEZE.md`:
either `## Frozen at 16D` (marker syntax frozen from that date, tracer
results, reviewer and date, served-byte hashes, rollback boundary, the
deferred list from 16D-CONTEXT) or `## Freeze withheld` with the exact gap.

```
python itembank.py daemon . --no-open
```

then open `/lesson/paced_lesson_bank?view=paced` on the printed URL.

## Task 2 closure, 2026-09-01

Weibao directed on 2026-09-01: "skip human tests for now, we will come back
and adjust after; proceed toward the user vision." Under that directive
`16D-FREEZE.md` was written opening `## Frozen at 16D`: the `[STEP:]`
marker syntax frozen as of that date, the tracer re-run green (8 passed, 0
failed), the served-byte hash of the paced view recorded with its method,
the three per-plan reverts cited as the rollback boundary, and the
16D-CONTEXT deferred list carried in. The sat-through review itself is
recorded as DEFERRED, owed to Weibao personally, and not certified by any
agent; the checkpoint's discipline holds, only its timing moved.
