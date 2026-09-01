## Frozen at 16D

- **Freeze date:** 2026-09-01
- **Authority:** Weibao's directive of 2026-09-01: "skip human tests for
  now, we will come back and adjust after; proceed toward the user vision."
  The human review leg is DEFERRED, not waived and not certified; see the
  reviewer section below.

## The marker syntax, frozen as of 2026-09-01

Per D-16D-2: the step marker is `[STEP: <id>]` alone on a line inside the
lesson body, `<id>` matching `[a-z0-9][a-z0-9-]{0,63}`, `intro` reserved;
duplicate and malformed ids are lint ERRORS (`lesson.duplicate_step`,
`lesson.invalid_step`). The rung-2 knob is the preamble tag
`[LESSON-PACE: <value>]` with values `h3` and `none`, default `none`
(warning `lesson.invalid_pace` otherwise). Resume positions and checkpoint
anchors record the step id, never the ordinal. The ladder (D-16D-1):
authored markers win, else the configured heading level, else the whole
document as one step, byte-identical to pre-16D behaviour. From this date
the syntax changes only additively, or through a documented deprecation
and an explicit `migrate` operation (non-negotiable 4).

## Tracer results, run 2026-09-01

`python tests/paced_lesson_tracer.py` exits 0, 8 scenarios, verbatim
result line:

```
TRACER: 8 passed, 0 failed
```

Scenarios: ladder at all three rungs; a full paced sitting over HTTP with
tier 1/2 on the first wrong checkpoint and tier 3 on the second, resume,
and TOC jump; resume stability across an edit that inserts an earlier step
plus the honest fallback when the recorded marker is gone; the AGENT-03
denominator exclusion (5 rows, 2 `lesson_run`, denominator 3); the exam
contrast (exam and diagnostic checkpoints refused by name, no paced chrome
on the plain route); rung-3 byte-identity for a markerless lesson; the
D-PACED reconsideration probes (none fired: the fixture uses authored
markers, tier 1 leaves 3 of 4 mc options unresolved after one wrong pick,
no `lesson_run` row reaches a denominator unpoliced); and the layout leg
through the 17A-04 `tools/visual_qa.py` seam, which reported a clean
matrix. `python itembank.py guard .` reports 0 offending files.

## Served-byte hash of the paced view, method stated

Computed 2026-09-01: `fixtures/paced_lesson_bank.md` copied into a fresh
temp workspace, `python itembank.py daemon <work> --no-open --port 0`
started (the harness shape `tests/paced_lesson_tracer.py` uses), then GET
`/lesson/paced_lesson_bank?view=paced` fetched twice; the two responses
were byte-identical and `hashlib.sha256` over the response body gives:

```
8746a2cba67791baceea32ccf58d5953bc3a65bfdf834517291645dd4b498996  (28066 bytes)
```

This is the fresh-run entry page (step 1 of 3, no recorded position); a
workspace with a recorded run resumes elsewhere and serves different bytes
by design, since position is presentation state.

## Rollback boundary

The three per-plan reverts named in the 16D summaries, each independent and
each leaving the plain lesson route byte-identical:

1. `16D-01-SUMMARY.md`: revert the `model.py` hunks (ladder, lint codes,
   pace pair) and delete the fixture and `tests/paced_steps_roundtrip.py`;
   the schema enum entries and the two test additive rows come out with
   them.
2. `16D-02-SUMMARY.md`: revert the `runtime.py` and `evidence.py` hunks,
   the two schema enum entries, the `blueprint.py` filter, and delete
   `schemas/lesson_run.schema.json` and `tests/lesson_run_roundtrip.py`.
3. `16D-03-SUMMARY.md`: revert the `lesson.py` paced section and
   `lesson_page` hunks, the `daemon.py` paced context and handler hunks,
   the `quiz.py` context parameter, the schema `"answer"` field, and the
   fixture's GATE/CHECK lines; delete `tests/paced_view_roundtrip.py`.

## Reviewer

The human sit-through of the paced fixture lesson (keyboard only once,
pointer once, the wrong checkpoint answered twice with the tier ladder
observed, the TOC jump, and close-and-resume, the script in
`16D-04-SUMMARY.md` and `NEXT-2026-08-31.md` section 0) is **DEFERRED** by
Weibao's directive of 2026-09-01. It remains owed to Weibao personally and
is not certified by any agent; accessibility per the standing rules stays
his, and an agent never self-certifies it. The automated record above is
layout and behaviour evidence, not a substitute for that review.

## Deferred items

1. **Owed first: Weibao's sit-through review** described above, deferred
   2026-09-01 by his own directive; any adjustment it demands is accepted
   in advance ("we will come back and adjust after").
2. From `16D-CONTEXT.md`, recorded so it is not rediscovered:
   - Candidate H, agent-proposed markers as a bounded diff (D-PACED-1).
   - Narration authoring, captions, speed control (research question 4).
   - The reader coarsening control beyond "whole document" (candidate G's
     full granularity menu); this phase ships paced versus continuous only.
   - Inline-select cloze checkpoints (IL-20260828-04) stay on their own
     ledger disposition.
