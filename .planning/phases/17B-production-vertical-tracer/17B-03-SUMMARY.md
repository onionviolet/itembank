# 17B-03 summary: the learner pass, the provisional rollup record, and the legacy audit

**Executed 2026-09-01.** Tasks 1 and 3 ran in full; Tasks 2 and 4 are the
two human checkpoints, handled under Weibao's standing directive of
2026-09-01 (human reviews are deferred, recorded as owed, never
self-certified, and never silently defaulted): Task 2 carries a recorded
PROVISIONAL default and Task 4 carries a `deferred-human` record, both
owed to Weibao by name. The pass was interrupted once by a rate limit
between stages 5 and 6; durable state resumed without loss and the
interruption became the sampled stage 8 scenario.

## Recorded deviations

- `python` is not on PATH; every command ran as `python3` (the 16C
  precedent deviation, recorded again).
- Task 4's verify line expects row G4 to read `pass` or `fail` with a
  human reviewer name and date. It reads `deferred-human`, owner Weibao,
  2026-09-01, and G8 carries the same annotation for its visual half. This
  is deliberate: the standing directive forbids an agent self-certifying
  the screen-reader item and the visual acceptance (17B-CONTEXT D-04) and
  forbids a silent default, and no human was available to sit the review
  in this session. The agent-verifiable halves are observations in the
  evidence file, not certification.
- Task 2's verify line expects the chooser to be Weibao. The record names
  the chooser as "provisional, coordinator under Weibao's 2026-09-01
  deferral directive; the real choice is owed to Weibao", preserves the
  verbatim question, and adopts the plan's own recommended-default line
  as the provisional value. Nothing stores it as configuration.
- The driven browser's screenshot and pointer pipeline stalled partway
  through stage 4 (a tool-side fault; the DOM, accessibility tree, network
  log, and JavaScript evaluation kept working). Structure and layout were
  verified from the accessibility tree and the layout engine's geometry,
  and the remaining form submissions were dispatched as DOM clicks on the
  real submit controls (same `POST`, confirmed by the receipt redirects).
  Pixel screenshots are not part of the record; the visual acceptance was
  always the human half of G8.
- The graded sitting ran through the runtime session CLI (the CLI twin of
  the served sitting) because the daemon's per-bank session is fixed in
  practice mode; the served exam disclosure shape was checked separately
  over `/api/start` and `/api/submit`.
- "Fully offline" was proven by making every non-loopback connection and
  DNS lookup fail inside the process under test (the D-07 mechanism),
  not by toggling the machine's radio, which is a system setting this
  agent does not change.

## Stage-by-stage evidence pointers

All in `evidence/17B-03-learner-pass.md`:

| stage | outcome | section |
|---|---|---|
| 1 Arrive | shelf renders the fixture course with honest chips and no aggregate; resume works on the quiz route; scope tree not on the shelf (D-06 item 2) | Stage 1 |
| 2 Orient | course frame with eight areas, honest empty notices (D-06 item 3); cited sources and 15 locators inspectable on the lesson route; reading scrolls | Stage 2 |
| 3 Predict | prompt precedes the mechanism; the prediction's response is recorded as a scored practice response, not participation (D-06 item 4) | Stage 3 |
| 4 Read and learn | term popovers by keyboard (Return) and pointer, Key point, Expert tip, Example, Common mistake, Not settled, In short, media with full alt and derivation; no horizontal scroll at 1280/768/375; KEY card body defect found and fixed (D-06 item 1) | Stage 4 |
| 5 Practice | no key or tier text before the gate; RTS-09 locked cards; wrong answer held with `RATIONALE FOR B`; one tier per unlock; short parked `score=None` until `mark`; `Item 1 of 8` never advances (D-06 item 5) | Stage 5 |
| 6 Test | exam sitting to completion: no key field in any `next`, no `explain` in any `submit`, short pending until marked, closed sitting refuses a submit; deferred sittings park on machine-scored items (D-06 item 6) | Stage 6 |
| 7 See progress | both rollup screens over one tuple set; denominators stated, pending and unknown shown, no aggregate, field states its version and never completes, course complete under `afe101-complete-v1`; two 17A-03 primitive gaps (D-06 items 7, 8) | Stage 7 |
| 8 Continue | in-sitting next action present; shelf CTA not composed from evidence (D-06 item 9); the real interruption resumed from durable state; APP-02 anchor-missing notice on served bytes | Stage 8 |
| offline | shelf, course, lesson, quiz, fonts, start, submit, and a tier reveal all over loopback with the network unplugged for the process | The journey with the network unplugged |
| G4 agent half | plain-Markdown coherence: coherent standalone (one authoring nit noted) | Plain-Markdown coherence |
| G9 | four strategies tabulated with all eight columns and the note-authority guard | G9 |

Rendered artifacts committed beside the evidence: `evidence/17B-03-rollup-dim.html`
(`e797f28b...`), `evidence/17B-03-rollup-map.html` (`6d1743c5...`),
`evidence/17B-03-rollup-tuples.json` (`66ec543c...`).

## The rollup decision as answered (Task 2)

`evidence/17B-03-rollup-choice.md`: PROVISIONAL default, "ROLLUP-MAP for
scope trees deeper than one level, ROLLUP-DIM otherwise" (the plan's own
recommended-default line), chooser "provisional, coordinator under
Weibao's 2026-09-01 deferral directive; the real choice is owed to
Weibao", dated 2026-09-01, verbatim question preserved, per-scope
override note recorded (no scope in the fixture overrides; his answer
replaces the provisional value). Not a silent default and not his answer.

## The legacy audit verdicts (Task 3)

`evidence/17B-03-legacy-audit.md`, through the shipped `legacy-upgrade`
skill and `upgrade_audit.py`:

- `fixtures/legacy_pre135_bank.md` (legacy question artifact): eleven
  baseline rows recorded; two rationale-only changes proposed with
  learning-value reasons, one cosmetic change refused with the frozen
  sentence; identity and fingerprints preserved; a stem rewrite halted
  with `KEYED_HALT_COPY` and exactly two affordances; nothing written.
  `python3 itembank.py lint fixtures/legacy_pre135_bank.md` exits 0
  (`2 items, 0 errors, 12 warnings`).
- `fixtures/lesson_bank.md` (legacy lesson artifact): eleven baseline
  rows recorded; the 16A capabilities it cannot express are linked beside
  it as a derived projection with the portability cost stated; nothing
  written; lint exits 0.
- The three `plan-text stand-in` rows are reported as such, not as
  checked. No skill gap (the skill shipped in 16C-08).

## The human checkpoint outcome (Task 4)

Deferred, not held. Reviewer owed: Weibao, personally. Date of the
deferral record: 2026-09-01. Rows G4 and G8 in `17B-GATES.md` read
`deferred-human` with that owner and date; the wave-3 note under the
table cites the directive. What the reviewer will need is in the evidence
file: the served routes, the widths, the term-button measurement (30 to
34 px inline targets), and the three items no agent observed (touch
activation of a term popover, the screen-reader walk through orient,
lesson, practice, and sitting, and the browser-side anchor-missing
reveal).

## Gate rows after this plan

| gate | state |
|---|---|
| G1 | pass (unchanged; evidence pointer now also names the legacy audit) |
| G4 | deferred-human (owner Weibao, 2026-09-01); agent half observed |
| G5 | pass on rendering and honesty; default provisional, owed to Weibao |
| G6 | pass; one flow defect routed (item 6) |
| G8 | agent half observed with five flow defects recorded; visual half deferred-human (owner Weibao, 2026-09-01) |
| G9 | pass |
| G2, G3, G7 | pass (unchanged from wave 2) |
| G10, G11 | pending, owed to 17B-04 |

## D-06 defects, with mechanism and owner

Full mechanisms in `evidence/17B-03-learner-pass.md`, "D-06 defects".

1. **KEY card body rendered literal `> ` markers.** In-phase single-file
   fix in `surfaces/lesson.py` (`_parse_key_callout` appended the raw
   line; now the de-prefixed line, matching `model.parse_key_blocks`).
   Pre-fix observation preserved in the evidence file; six lesson and
   key test files pass after the fix; no contract, parser, or scorer
   change. Owner: 17B (fixed); originating 03.1 and 16A.
2. **Scope tree not on the shelf.** FILE-04 degraded subdirectory scan;
   no route reads `scope.md`. Owner: the phase that schedules FILE-04 and
   the 14B shelf wiring.
3. **Course areas carry no content.** 16B's recorded deferral. Owner:
   14A/14B execution.
4. **Prediction recorded as a graded verdict.** No participation-event
   producer for `activity_trace`/`activity_completed`. Owner: the phase
   that ships the activity evidence producer (16A activity matrix).
5. **`Item 1 of 8` never advances on the server-rendered quiz flow.**
   `quiz_page.py:314` hard-codes the position. Owner: the quiz surface
   (13.5/13.9).
6. **Deferred-feedback sittings park on machine-scored items.**
   `defer_feedback` never moves the cursor and `marker_close` collects
   only human marks, so an eight-item exam needs eight marks. Owner: the
   runtime phase that shipped `FEEDBACK_POLICIES` (Phase 6, amended
   2026-08-24).
7. **No 17A card primitive with a fill-state slot for ROLLUP-MAP child
   cards.** Composed from `course_shelf` and `fill_state`. Owner: 17A-03.
8. **`progress_comprehension_display` omits the determinate-claim
   `progressbar` role and `aria-valuetext` of `ARIA_CONTRACT`.** Owner:
   17A-03.
9. **Shelf next action not composed from session or evidence state.**
   Owner: 14B / FILE-04 shelf wiring, 16C live-state collector seam.

No hosted-model call was made by any step; the D-09 egress records in
both evidence files say so at call time.

## Validation outputs, verbatim

Recorded in the commit's final section of this file after the guard and
em-dash scans ran (see below).

## Next safe action

Wave 4 (17B-04): the restore drill (G10) and the egress and
rights-unknown checks (G11), then the freeze record naming, for every
gate, pass or the defect and owner. Owed to Weibao before 17B can close
its human legs: the G4 screen-reader walk, the G8 visual acceptance at
1280 and 375, and the G5 rollup default.
