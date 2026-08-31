# 16D-03 summary

Executed 2026-08-31. All three tasks complete.

## What shipped

- `surfaces/lesson.py`: `lesson_page` gained mode `"paced"` as its third mode
  (precedent: 16A's D-16A-9 guided mode), with new kwargs `step_id`,
  `tier_payload`, `tier_show_url`. New helpers: `paced_view_steps` (maps
  ladder steps to parsed heading indices, keeping heading-bearing steps
  only), `_paced_toc_html` (a native `details` "Steps" list, open by
  default, `aria-current` plus "(current)" on the active step),
  `_paced_pager_html` (Back/Continue links; on a gated step the exact
  sentence replaces Continue), `_paced_tier_html` (renders
  `runtime.checkpoint_feedback`'s payload verbatim: text chips
  "right"/"not right" per touched option, the "About what you picked"
  heading over touched DA, the full reveal or a "Show the answer" link).
  The pager gates forward on ATTEMPTED, never correct (IL-20260828-03 via
  D-16D-5): computed from the 6.2 gate ctx's attempted map plus cleared
  states, deliberately looser than the 6.2 required-gate read-truncation,
  and the two compose. The 6.2 gate band gained exactly one conditional
  addition: hidden view/step fields when the gate ctx carries `paced_step`;
  structure and copy otherwise untouched. Constants:
  `PACED_GATED_CONTINUE`, `PACED_UNKNOWN_STEP`, `PACED_NO_EVIDENCE`,
  `PACED_STEPS_LABEL`, `PACED_TOUCHED_HEADING`, `PACED_SHOW_ANSWER` (all
  quoted below). Status region composes announce + fallback + "Step {n} of
  {total}." announced once.
- `surfaces/daemon.py`: no new route; GET `/lesson/<stem>` reads
  `?view=paced&step=` (ignored under print). `_lesson_run_path` (one
  `lessonrun_<stem>.json` per bank stem under `_attempts/`),
  `_paced_context` (creates or resumes the run, advances on a valid step
  param, composes "Resuming at step {n}.", recomputes the tier payload
  post-redirect from the run's stored last answer and held count, builds
  the show URL). `handle_lesson_check`: a paced submission records via
  `quiz.record_gate_check` with mode `"paced"` and context `"lesson_run"`,
  summarises the attempt into the run (state correct/held, ordinal, tier,
  stored answer), redirects back to the same paced step (`checked=<id>` on
  wrong, `reveal=check` on correct). `handle_lesson_skip`: a paced skip
  records state `"skipped"` into the run (the `gate_skip` event unchanged)
  and redirects back. Degrade: an unusable run store or a stepless lesson
  renders the continuous document.
- `surfaces/quiz.py`: `record_gate_check` gained a `context` parameter
  defaulting to `"lesson_gate"` (byte-identical for every existing caller).
- `schemas/lesson_run.schema.json`: attempts entries gained the optional
  `"answer"` field (string or array), described as learner scratch state
  for the post-redirect re-render, never a second evidence record.
- `fixtures/paced_lesson_bank.md` gained `[GATE: required]` and a
  `> [!CHECK: 4b6fb5cba3ae425f]` in the mechanism step.
- `tests/paced_view_roundtrip.py`: eleven served assertions (projection,
  jump-only TOC past an unattempted gate, the stated gate sentence with no
  disabled control, tier 1/2 marks for touched options only, tier 3 on the
  second wrong attempt, skip opens the gate, resume, unknown-step
  fallback, `lesson_run`+`paced` labelled schema-valid evidence,
  chrome-free static build).

## Every UI string as rendered

- `PACED_GATED_CONTINUE`: "Attempt the checkpoint above to continue, or use
  the Steps list to jump ahead."
- `PACED_UNKNOWN_STEP`: "That step is not in this lesson any more. Showing
  the first step."
- `PACED_NO_EVIDENCE`: "This step records nothing."
- `PACED_STEPS_LABEL`: "Steps"
- `PACED_TOUCHED_HEADING`: "About what you picked"
- `PACED_SHOW_ANSWER`: "Show the answer"
- "Resuming at step {n}."
- "Step {n} of {total}: {title}" (header)
- "Step {n} of {total}." (status region)
- "{n}. {title}" and "(current)" (TOC rows)
- "Back"
- "Continue"
- "Answer: {answer_text}" (reveal)

## Deviations

1. The paced view paces what the reader renders: intro prose before the
   first heading has never been rendered by `lesson_page` in any mode, so
   an intro-only marker step stays a durable identity in
   `model.lesson_steps` but is not a navigation stop; `paced_view_steps`
   keeps heading-bearing steps only. The UI-SPEC's "(seen)" visited suffix
   was replaced by "(current)" on the active step: the run records
   position, not a visit history, and a truthful "(current)" beats a
   guessed "(seen)".
2. The pager's gating reads the gate ctx's attempted map rather than the
   render's `gate_stop`: 6.2's required gate clears on correct or skip,
   but D-16D-5 gates the pager on attempted, so a wrong answer opens
   Continue while 6.2 keeps withholding the step's tail until the check
   clears; the two compose and the code comment records it.
3. The tier reveal kwarg was renamed `tier_show_href` to `tier_show_url`
   mid-execution: `tests/lesson_roundtrip.py`'s no-second-selection
   mechanism guard greps `handle_lesson_get`'s source for `"ref="`, which
   `"href="` contains. The guard was right to be blunt.
4. The run file is one per bank stem (`lessonrun_<stem>.json`), not one
   per opening: a paced position is presentation state and the newest
   state is the only one worth resuming.
5. The tier disclosure renders outside the band (a paced-feedback section
   under it), because the plan forbids changing the band's structure; the
   band's one addition is the two hidden fields.

## Verification

`python3 tests/paced_view_roundtrip.py` exit 0; daemon, lesson, gate,
serve, home, mode_layer, lesson_run, paced_steps roundtrips all exit 0;
`python3 itembank.py guard .` reports 0 offending files.

## Rollback

Revert the `lesson.py` paced section and `lesson_page` hunks, the
`daemon.py` paced context and handler hunks, the `quiz.py` context
parameter, the schema `"answer"` field, and the fixture's GATE/CHECK
lines; delete the test. The plain lesson route renders byte-identically
without them.
