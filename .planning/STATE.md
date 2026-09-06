---
gsd_state_version: 1.0
milestone: reach
milestone_name: reach
current_phase_name: 19A-course-operating-surface
current_phase: 19A
status: "Reach milestone adopted 2026-09-05 and the freeze-before-start ordering waived by Weibao. Every phase is beginnable: 19A and 19C have no unmet dependency, 19B and 19E follow 19A, 19D is the exit. Source-to-course is code-complete; 13.5, 17B, 17C and 18 are executed with human legs owed, and those legs now block nothing except the word frozen. 19A has a written context and no plans yet; 19B, 19C, 19D and 19E need a context pass first."
stopped_at: "19A-03 executed: the structure and objective-editing families are in the spine, the surface grid moved 41 to 43 of 82, and a course can be outlined, given objectives, related by edges and have its objective identity moved as a reviewed proposal from both surfaces. Next action is 19A-04 (treatment binding), or 19C's settings change."
last_updated: "2026-09-05T00:00:00.000Z"
last_activity: 2026-09-05
last_activity_desc: "19A-03 executed: eight operations (add-container, add-objective, add-edge, structure, and the four objective identity moves) with their routes, `itembank course` twins and parity rows, a schema-driven CLI request builder, and a defect fix in 19A-02's own treatment enum; previously: 19A-02 executed: POST /api/course/add-source and /api/course/bindings with their `itembank course add-source` and `itembank bind list` twins, /api/course/bind and /api/course/rights re-hung in the validated spine at their published paths and envelopes, graph.add_source and graph.validate_binding and course.rights_for_binding given their first doors, and course writes made loopback-only; previously: 19A-01 executed: POST /api/course/create and /rename with their `itembank course` twins, one validated request document, and the /api/bind and /api/rights re-homing recorded as 19A-CONTEXT D-02a; previously: reach milestone adopted, freeze ordering waived, 19A to 19E entered on the roadmap; previously: 17B-04 executed and the milestone exit record written; G10's two routed defects repaired additively and the restore drill re-run to a pass; 17C-01's maintenance and restore audit run, finding five silent losses (F-LOSS-1 to F-LOSS-5) and a clean owner sweep."
progress:
  total_phases: 41
  completed_phases: 36
  total_plans: 212
  completed_plans: 212
  counting_rule: "phase directories under .planning/phases; a phase counts complete when frozen or when its summaries and verification exist, human legs owed being a label rather than an open state after the 2026-09-05 waiver. Open are the five reach phases 19A to 19E, none of them blocked. Plans count complete when a summary exists or the phase is frozen."
---
# Project State

## Current position (2026-09-05): reach, and nothing waiting

**The freeze ordering is waived.** Weibao, 2026-09-05: "skip the freeze and
make everything beginnable." A phase may now be planned, executed and closed
without a human signature in front of it. A phase whose human legs are unsigned
closes as **executed (human legs owed)** rather than `frozen`; the legs stay in
the owed list below until signed. Two things the waiver does not touch, because
they are correctness and not ceremony: deterministic gates still have to pass,
and an agent still may not sign a leg reserved to a human (17B-CONTEXT D-04).
Deferred is honest, self-certified is not.

**The milestone is reach** (`.planning/REACH-MILESTONE.md`, adopted the same
day). Source-to-course is code-complete: 212 of 212 plans have summaries, and
what remained of it was signatures. The gap pass found the constraint is reach
rather than capability, so this milestone adds no capability: it gives the
built engine doors, turns the product's own model path on, and uses both on a
real course.

**What is beginnable right now**, which is everything:

| Phase | Blocked on | State |
|---|---|---|
| 19C backend on | nothing | no context yet; cheapest start |
| 19A operating surface | nothing | 19A-01 to 19A-03 executed 2026-09-05; six families to go |
| 19B agent door | 19A's routes existing | no context yet |
| 19E MCP tool table | 19A's routes existing | no context yet; closes 999.3 |
| 19D Math 1400 | 19A, 19B, 19C | no context yet; the exit |
| 13.5, 17B, 17C, 18 | nothing | executed, human legs owed |

**Recommended order:** 19C beside 19A, then 19B and 19E in either order, then
19D. 19A is the load-bearing one and the only one an executor can plan straight
from today.

**19A-02 landed, 2026-09-05.** The source-binding family is hung in the spine,
and with it the whole path from a linked file to a coverage claim is walkable
from a surface: `POST /api/course/add-source` records the sidecar row that
`graph.add_source` writes and that nothing called, `/api/course/bind` and
`/api/course/rights` were re-hung inside the validated spine at their
published paths with their response envelopes untouched, and `POST
/api/course/bindings` is the family's one read. That read is what fills
`source binding / explain`: every row comes back through
`graph.validate_binding`, so a state this build cannot read degrades to
unknown and never to covered, and the right each binding consumes is re-read
through `course.rights_for_binding` and reported beside the snapshot the row
stored, so a claim resting on a grant that has since been revoked says so.
The CLI twins are `itembank course add-source` and an `itembank bind` that
now dispatches through `course_ops.run`, so the command is refused by the
same published document the route is. The grid moved 40 to 41 of 82.

One hardening travelled with it, recorded in `19A-CONTEXT.md` rather than
absorbed: the spine gated every course write with the read-side cross-origin
check only, so a `--lan` daemon let a phone on the same wifi mint, rename and
bind a course while every day write and theme save was already loopback-only.
The spine now chooses its gate by what the operation does.

**19A-03 landed, 2026-09-05.** The structure and objective-editing families
are in the spine: `add-container`, `add-objective` and `add-edge` write the
outline and its relations, `structure` reads them back with each edge's
effective reading and the warnings the authored order earns, and
`rename-objective`, `split-objective`, `merge-objectives` and
`overlay-objective` move objective identity as reviewed proposals. The grid
moved 41 to 43 of 82: `objective / create` and `objective / change` are
filled.

Most of the wave is what it refuses. A container and an objective add zero
edges, so an outline never becomes a prerequisite claim by accident. A
prerequisite pointing backwards through the authored order is recorded and
warned about, never refused and never fixed, and a cycle is named and never
broken. The four identity moves add rows and delete none and record the
migration as `proposed`, because the identity a learner's evidence was
recorded against has to stay in the file. `objective / undo` therefore stays
empty on the grid with a truer note: the reversal is rejecting the migration,
and the accept and reject doors are 19A-07's wave.

`cmd_course` now builds its request from the operation's published node, so
adding an operation is adding a `$defs` node and a parser and nothing else,
and a test asserts every published field has an argument on its CLI twin.

**One defect in 19A-02's own work, found and fixed 2026-09-05.** The `bind`
node's `treatment` enum had been typed out by hand and did not match
`graph.TREATMENT_KINDS`: seven invented kinds, seven real ones missing, so a
legitimate treatment binding for seven of the eleven was refused by the
published document on both surfaces at once. The enum now equals the tuple,
and the test asserts every closed vocabulary the document publishes against
the engine tuple it copies. A published enum is a copy, and a copy drifts;
the fix is the assertion, not more care.

Known red on this machine and not caused by this work:
`tests/daemon_roundtrip.py` fails its twelve-thread concurrency check on a
clean checkout of `5e9d4eb`, three runs out of three, one request exceeding
the five-second client timeout while the session-count assertion passes.
`tests/model_phase_roundtrip.py` fails only because it runs that suite as an
authority regression. Every other test in `tests/` is green.

**19A-01 landed, 2026-09-05.** The spine exists and one family is hung in it:
`POST /api/course/create` and `POST /api/course/rename`, their
`itembank course create|rename|show` twins, one published request document
(`schemas/course_operation.schema.json`) validated before dispatch, and both
writes reaching `course.create_course` / `course.write_course`, which is
`journal.commit_operation` with an expected base fingerprint.
`journal.OPERATION_TYPES` is untouched at six. The surface grid moved from 38
to 40 of 82 meaningful cells; `course / create` and `course / change` are no
longer empty. The early source-binding routes were re-homed under
`/api/course/` with their old paths kept serving as declared aliases, recorded
as `19A-CONTEXT.md` D-02a, so there is one route convention and one tested
exception rather than two undeclared ones. A stale assertion in
`tests/daemon_roundtrip.py` that predated this plan (sixteen `/api/*` routes
against a tree carrying eighteen) was repaired in the same pass.

## Current position (2026-09-03, superseded above)

**Milestone:** source-to-course. Exit is Phase 17B's gate record
(`.planning/phases/17B-production-vertical-tracer/17B-GATES.md`), G1 to G11.

**Phase 17B, executed to its human gate.** 17B-01 to 17B-04 are done and
committed; the milestone exit record is in `17B-GATES.md`. Final gate
states: G1, G2, G3, G7, G9, G11 pass; G5 and G6 pass carrying routed
defects with named owners; G10 failed in wave 4 and passes after the
2026-09-05 repair; G4 and G8 carry `deferred-human` legs. G4 (screen
reader), the G8 visual acceptance at 1280 and 375, the G5 default rollup
choice, and the milestone acceptance signature are human checkpoints an
agent may not sign (17B-CONTEXT D-04), and none of them was defaulted.

**G10 repaired, 2026-09-05.** Wave 4's drill found that 6 of 7 canonical
objects and 0 of 40 evidence events crossed a clean-machine restore, and
routed both causes because they were contract changes in frozen surfaces.
They were repaired rather than left owed (commit `247ffbe`), additively:
`journal.op_grant_rights` records a rights decision without editing the
artifact, `journal.op_adopt` records that a file bound by `link` is the
course's own artifact, `course_package.evidence_scope` joins evidence by
bank name and carries whole sessions, and the new `evidence-not-carried`
loss category names anything a package cannot claim. `OPERATION_TYPES`
stays at six. The drill re-run passes: 7 of 7 objects, 40 of 40 events.
Evidence: `evidence/17B-04-restore-repair.md`. Consequence for 17C: its
sweep now has a working restore path to sweep with.

**Frozen:** 14A (2026-08-18), 14B (08-27), 14C (08-28), 16A (08-28),
16B (08-28), 15A (08-30), 15B (08-30), 16C (08-30), 16D (09-01, sit-through
review deferred), 17A (09-01, A11Y-01 pass deferred; `theme.DEFAULT_ACCENT`
stays teal until it lands). Five of these (16A, 16B, 16C, 15A, 15B) closed
their review legs on agent signatures under Weibao's general delegation.

**Phase 18:** plans 01 to 03 executed 2026-09-01 to the human gate, ahead of
the stated dependency on 17B. Row 7 (a second person's cold install) is
deferred to Weibao and the phase close is conditional on it. Also owed: the
Windows rebuild and hash of the packaged artifact, and the signing decision.

**Phase 17C, run to its human gate 2026-09-05.** `17C-AUDIT.md` records the
drill rerun at commit `5286683` (pass), the sweep over all 18 canonical
object classes, the owner sweep (49 of 49 next-milestone requirement blocks
own an owner, zero unowned), and the recurring triggers. The drill passes
and the loss report does not: five silent losses are routed, F-LOSS-1
provenance and operation history, F-LOSS-2 rights state, F-LOSS-3
`_attempts` session state, F-LOSS-4 unregistered files inside a course root,
and F-LOSS-5 a restored bank citing `media/` that did not cross while `lint`
still reports zero errors. Four are 14B's; F-LOSS-5 also touches the lint
phase. Repair is out of the audit's scope by its own plan. Weibao's
acceptance of the report is owed.

**Phase 999.3 (MCP surface):** promoted 2026-08-17, zero plans.

**Real use so far:** one real sitting, 2026-08-24, EMT unit 1, course root
outside this repository (`13.9-CALIBRATION.md`). No Math 1400 or CSCI 1100
course exists yet. Every other session in the record is a fixture or an agent.

**Owed to Weibao, in one list** (packet: `NEXT-2026-08-31.md`):

1. The 17A A11Y-01 scripted pass (`17A-QA.md`).
2. The 16D sit-through (`16D-04-SUMMARY.md`).
3. The standing agent-signature ruling (ratify, ratify with re-review, or
   tighten).
4. 17B's human legs, now reached: the G4 screen-reader walk, the G8 visual
   acceptance at 1280 and 375, the G5 default rollup choice, and the
   milestone acceptance signature at the end of `17B-GATES.md`.
5. Phase 18 row 7, the friend's cold install, plus the Windows rebuild and
   the signing decision.
6. The 13.5 five-item human tail (`13.5-GATES.md`).
7. The 13.9 two-sentence post-sitting reaction.
8. 14C's one unrun manual checkpoint: the OCR adapter against a live vision
   model.
9. Acceptance of `17C-AUDIT.md`: accept as written, accept with owner
   assignments for F-LOSS-1 to F-LOSS-5, or reject with reasons.

**Housekeeping 2026-09-03.** Log entries dated 2026-08-30 and earlier, the
twice-superseded "Current Position" block, the empty performance table, the
duplicated decisions list, the stale "Phase 14 progress" block, and the
2026-08-16 session-continuity block moved verbatim to
`.planning/archive/STATE-LOG-through-2026-08-30.md`. Dead operator files
moved to `.planning/archive/` (index in its README). `scripts/summary_gate.py`
now enforces the 2026-08-21 summary rule in CI and preflight.

## 2026-09-05: the visual review, and a recorded reversal of D-14/D-25

Weibao reviewed the rendered screens rather than the transcripts. Four
things came out of it.

**Fixed in the app.** The lesson's one diagram was a broken image on every
served page: a bank-relative `media/x.svg` under `/lesson/<stem>` resolves
to `/lesson/media/x.svg`. The renderer now takes a `media_base` and the
daemon serves `/media/<stem>/<name>` from the bank's own directory,
contained by resolution rather than by allowlist. The eight course areas,
which said "Nothing has been added yet" for a course with a lesson, a bank,
seven objectives and two sources, now read the course's own artifacts;
16B's `content_available: False` was a deferral to 14A and 14B, and both
have landed.

**A recorded reversal, made deliberately.** D-14 and D-25 reserved settling
a mark to the CLI: `verdict` is in `API_FORBIDDEN_FIELDS` so no client can
put one on the wire. That made a practice sitting parked on a constructed
response a dead end in the browser, telling the learner to open a terminal.
Asked directly, Weibao chose the in-page self-mark. `POST /api/mark` admits
`verdict` through the same `allowed_ids` hatch `/api/start` uses for
`profile`, and nothing else moves: `marker` stays forbidden,
`evidence.mark_event` still pins the marker to `human`, a model may still
only propose through `/api/rubric-review`, and the runtime still decides
what a settled mark means for the cursor. The browser on loopback is now a
reviewer surface for the learner's own sitting. Recorded here because it
reverses a decision, not because it was hard.

**The visual direction, answered by keeping all of them.** Five candidate
directions were rendered against the real screens; asked to choose, Weibao
said keep every one, switchable, and more. So the answer is an axis, not a
restyle: `look` joins `theme` and `accent` as a third independent setting,
seven looks ship (classic, editorial, neo, cash, console, soft, contrast),
and `surfaces/theme.py` stays the only palette authority. A look moves the
ground and the shape and never a semantic colour, which
`tests/stylesheet_roundtrip.py` re-measures on every run at the same
floors. Switchable from `/settings`, from `POST /api/theme`, and from
`itembank theme look <id>`, all through one writer.

## 2026-09-05: 17C's maintenance and restore audit run

`17C-AUDIT.md` written under the same directive, tasks 1 to 3 complete. The
audit did not halt on 17B's two `deferred-human` gate rows; it recorded the
deviation and the owed legs instead, which is the directive applied rather
than bypassed.

Its useful result is negative and worth keeping in view: a passing restore
drill is not a complete loss report. Five losses cross no boundary and no
report names them, and the sharpest is F-LOSS-5, where a restored bank
cites a `media/` file the package never carried and `lint` still reports
zero errors. That is the first finding in this project of a restored course
that reads complete and is not, on a path a learner would actually walk.
All five are routed to 14B (F-LOSS-5 also to the lint phase). The silence
was then closed the same day in its own commit (`dd99a3a`), recorded as an
addendum to the audit rather than folded into it: two additive loss
categories (`unregistered-file`, `provenance-not-carried`) and two additive
lint warnings (`media.declared_present_missing`,
`media.integrity_mismatch`). The loss report went from 1 row to 11 and the
restored bank warns about the media it cites. What the losses mean, and
whether any should be carried rather than named, stays 14B's open question
and Weibao's call.

## 2026-09-05: 17B-03 and 17B-04 committed, G10 repaired, the milestone exit record written

Weibao's directive, 2026-09-05: "rather than making me check things I want
to properly utilize the capabilities of my usage and just fulfil User
vision." Read as a reaffirmation of 2026-09-01: carry the work to
completion, do not route decisions back to him that an agent can defensibly
make and record, and keep never self-certifying the human review legs.

Under it, this session: committed wave 3's `surfaces/lesson.py` KEY-card fix
and both waves' evidence; repaired gate G10's two routed defects as an
additive contract change and re-ran the drill to a pass; brought
`17B-04-SUMMARY.md` under the 2026-09-03 summary gate (the long-form record
lives in the gate table and the evidence files, which is what the rule
intends); and updated the gate record and this file.

What was deliberately not done: no human review leg was signed. The G4
screen-reader walk, the G8 visual acceptance, the G5 default rollup choice,
and the milestone acceptance signature are still owed to Weibao and are
listed above.

## 2026-09-01: 17A and 16D frozen with deferred human review legs; 17B unblocked

Weibao's directive, 2026-09-01: "skip human tests for now, we will come
back and adjust after; proceed toward the user vision." Under it the two
phases standing at their human gates were frozen honestly rather than
certified: `17A-FREEZE.md` opens `## Frozen at 17A` and `16D-FREEZE.md`
opens `## Frozen at 16D`, both dated 2026-09-01, both recording their human
review legs as DEFERRED, owed to Weibao personally, and signed by no agent.
This mirrors the recorded-waiver pattern of 16A/16B/16C/15A/15B with one
difference kept deliberate: accessibility is not waived, only postponed,
and each freeze lists the owed review first in its deferred items.

What the freezes rest on, re-run on the freeze date: the 17A driven-browser
matrix (13 positive gates green across light, dark, and oled over all eight
screens, the hover-only negative failing for the required equivalence
reason), `visual_accessibility_roundtrip`, `component_primitives_roundtrip`
(17 primitives), `stylesheet_roundtrip`, the 16D paced tracer (8 passed, 0
failed), and `guard` at 0 offending files. Served-byte hashes were computed
and recorded in both freezes (sha256 of `visual_fixture.single_file()`,
`SHARED_CSS`, the three `theme_css` blocks, and the fresh-run paced view
over HTTP). The 13.9 walking-skeleton summaries were verified present
before either freeze was written. The 13.9 evidence, the automated matrix,
and the tracer are evidence; none of it is accessibility certification and
neither freeze claims otherwise.

Owed human reviews, the come-back-and-adjust list:

1. The 17A A11Y-01 scripted pass (keyboard, touch, VoiceOver, zoom, high
   contrast, reduced motion, equivalent-task; script in `17A-QA.md`).
   Until it lands, `theme.DEFAULT_ACCENT` stays teal.
2. The 16D sit-through (keyboard once, pointer once, the wrong checkpoint
   twice with the tier ladder observed, TOC jump, close-and-resume; script
   in `16D-04-SUMMARY.md`).
3. The standing agent-signature ruling, `NEXT-2026-08-31.md` item 2, which
   remains open: one ruling on the five phases that closed review legs
   with agent signatures, not five.

17B is now unblocked: its precondition run halted on the missing
`17A-FREEZE.md` and on nothing else.

## 2026-08-31 (third entry): Phase 16D is executed to its human gate

Planned in the second entry below, executed the same day. Plans 16D-01
through 16D-03 shipped the pacing ladder (`[STEP: id]` wins, else
`[LESSON-PACE: h3]`, else the whole document, byte-identical to before),
the lesson-run session kind with the additive `lesson_run` context and
`paced` mode labels (40 pre-change baseline events still validate), the
default AGENT-03 denominator exclusion, the runtime-released three-tier
wrong-checkpoint disclosure, and the paced view as `lesson_page`'s third
mode over the shipped 6.2 gate bands: jump-only Steps list, a pager that
gates on attempted never correct, honest fallback on a deleted resume id,
and a chrome-free static build. 16D-04's tracer composes it end to end:
8 scenarios green in about 3 seconds, including the resume-across-edit
identity proof, the exam-silence contrast, and the reconsideration probes
(tier 1 leaves 3 of 4 mc options unresolved, so the ladder does not
trivialise a retry). The tracer and the 16D-03 summary were written by
lesser-model subagent executors against the plans and verified by the
orchestrating session, which is the PLANNING-DIRECTIVES section 5 split
running inside one session.

Two guards earned their keep in passing: the no-second-selection-mechanism
guard greps the lesson route handler for "ref=" and caught it inside
"tier_show_href=" (renamed tier_show_url), and the lesson lint-code count
assertion caught the three new pacing codes before their SPEC rows would
have been forgotten.

What remains of 16D: Task 2 of 16D-04 only, Weibao's sat-through review
and the freeze or withholding in `16D-FREEZE.md`. Two human gates now
stand between the tree and the 17B exit runway: the 17A-04 A11Y-01 review
and this one, and both are listed in `NEXT-2026-08-31.md`.

Measured: paced tracer 8 of 8 scenarios, about 3 seconds. Full suite 104
files, 0 failures, working tree clean after. Guard 0 offending files.

## 2026-08-31 (second entry): the paced-lesson subphase is planned as 16D

The one piece of milestone work that waited on no one is no longer
unwritten. Phase 16D (Paced Lesson Projection & Checkpoints) is planned:
`16D-CONTEXT.md` binds D-PACED-1/2/3 and the ledger refusals, `16D-UI-SPEC.md`
is the experience contract, and plans 16D-01 through 16D-04 are written to
the executor bar. The marker syntax D-PACED-1 left open is resolved as
`[STEP: <id>]` plus `[LESSON-PACE:]` (D-16D-2, following the bracket-line
convention). Three discoveries made planning cheap: `context` already exists
on response events (quiz, lesson_gate) so the denominator label is one
additive enum value; `lesson_page` already carries a mode seam
(continuous, guided) so paced is a third value, not a fourth surface; and
FEEDBACK_POLICIES already implements own-picks selection feedback, so tier 1
is a policy application, not new scoring. 16D-01 through 16D-03 are
agent-executable now; 16D-04 Task 2 is Weibao's sat-through review.
ROADMAP.md carries the 16D entry between 16C and 17A.

## 2026-08-31: 17A-04 Task 1 executed; the freeze now waits on exactly one human review

The stale claim first: this file's previous stopped_at said 17A-04 needed
"the LGPL browser-driver supply-chain decision". It did not. Weibao answered
that decision on 2026-08-27 (`17A-04-DECISIONS.md` D-17A-04-1, approved,
option A on ffmpeg), so Task 1 was executable all along and is now executed.

### What shipped

`tools/visual_qa.py`, the pinned dev-only Playwright harness (1.62.0,
Chromium 151, `VENDORED.md` row, `deps/visual-qa-pins.txt`), driving the
one-file synthetic fixture through the full layout matrix: three widths, 200
percent zoom reflow, keyboard order with visible focus, 44px targets,
rendered light/dark/oled contrast, reduced motion, touch disclosure, static
fallback, and a disclosure equivalence audit whose deliberately hover-only
fixture MUST fail. All 13 positive gates are green and the negative fails
for the equivalence reason; `tests/visual_accessibility_roundtrip.py`
asserts exactly that when the harness is installed and prints an honest skip
when it is not (CI). Evidence: `17A-QA.md` and `17A-QA-EVIDENCE.json`.

### Five defects found by a layout engine that no byte check could see

The fixture's dark/oled accent skipped contrast correction entirely
(`token_css` re-declared one raw `--accent` after the dark override; the
primary action measured 2.77:1). Every scoped accent palette in the one-file
export was inert (`_scope_css` emitted `body:has(...) :root`, which matches
nothing, ever). Switch-radio keyboard focus drew its outline on a 1px
clipped input, which is no indicator. Twenty-one controls measured under
44px, including the shipped `details summary` in `SHARED_CSS` at 32px, now
44 (the one learner-visible change). And the one-file export embedded the
live agent-console iframe, always dead in the sandbox that export exists
for, and carrying a Tab focus stop that no CSS can mark in Chromium; it is a
static labeled placeholder there now, and the served route keeps the live
frame behind a `:focus-within` indicator.

### What still needs Weibao, precisely

One thing: 17A-04 Task 2, the scripted human A11Y-01 review in `17A-QA.md`,
then `17A-FREEZE.md` (freeze or withholding). The A11Y-01 waiver was
deliberately never given, the standing five-phase agent-signature question
makes this exactly the wrong review to be the sixth, and the plan marks the
checkpoint blocking. 17B-01's precondition halts on `17A-FREEZE.md` by
design, so the review is also the one gate between here and the milestone's
exit tracer.

### Measured

Harness matrix 13 of 13 positive gates green, negative failing as required.
Affected suites green: visual_accessibility, visual_system,
component_primitives, stylesheet, daemon, lesson, gate, serve, home
roundtrips; `scripts/check_vendored.py` 12 artifacts verified; guard 0
offending files. Full suite 100 files, 0 failures (one baseline re-taken
with a dated cause: `THEME_PAGE_BASELINE`, moved by the summary 44px rule).
Darwin arm64, Python 3.14.6, playwright 1.62.0.

## Project Reference

See `.planning/PROJECT.md`. Core value: one runtime, one scorer, one evidence
store, and the runtime, not the model, decides what reaches the learner.
Binding milestone scope: `.planning/SOURCE-TO-COURSE.md`. Verbatim goal:
`.planning/USER-VISION.md`.

## Completed Phases Note

**Milestone complete 2026-08-11.** All 18 roadmap phases are merged into main:
the twelve phase branches of this batch (02.1, 03, 03.2, 04, 05, 08, 09, 10, 11,
999.1, 999.4, 999.5) landed on top of 03.1, 06.1, 06.2, and 09.1, which merged
earlier the same day. The pre-existing 06.2 evidence-index regression flagged in
`HANDOFF-PHASE10.md` / `10-VERIFICATION.md` is **resolved**: the 08 merge restored
the v3 evidence index `context` column (`5b7f397 fix(08-06): restore v3 evidence
index (context column) lost in main's 06.2 merge`, in main via `merge(08)`
`30cf342`; the 05 branch carried the same restore in `14f9a89`). Nothing in the
12-phase merge re-introduced it.

**Phase 6.2 — Executable Textbook Loop (completed 2026-08-11 on branch
`gsd/phase-06.2-textbook-loop`):** the lesson gate is a presentation policy
over existing item types. `[GATE: required|recommended|off]` parses
additively; the gate band activates 3.1's reserved slot with one form and
zero JavaScript; `required` truncates at the server (no DOM leak), a
recorded `gate_skip` event is its own evidence type (never a null-score
response), the check/skip routes score and record through the one
runtime/evidence path with `context="lesson_gate"`, and the gate outcome
split is a derived, stated-denominator report. Twelve UI-SPEC §13 gates are
executable fixtures; one human-verify item (screen-reader announcement) is
recorded in 06.2-GATES.md. Six GATE-01..06 requirements delivered.

## Deferred Verification

| Phase | State | Resume |
|-------|-------|--------|
| 2.1 | verification_deferred_human | $gsd-verify-work 2.1 — 4 human items: real-OS double-click per OS; Gatekeeper quarantine on a real macOS machine; Linux desktop-file-manager launch; real LMS import acceptance (SC5 manual half) |
| 3 | verification_deferred_human | $gsd-verify-work 3 — 1 human item: interactive browser click-through of lesson ↔ question round trip (fresh-model, no-source process claim verified by artifact; scroll feel is a human judgment) |
| 03.1 | verification_deferred_human | $gsd-verify-work 03.1 — live full-suite + schema_validate run; cross-browser Popover; ClearType 18px render at 375/1280px; 1280/768/375px snapshots (see 03.1-GATES.md + 03.1-UAT.md) |
| 4 | verification_deferred_human | $gsd-verify-work 4 — 7 human items: perceptual hierarchy / real-browser 320px/200% rendering, live native color-picker behavior, assistive-tech announcement timing, and the remaining 04-VALIDATION manual-matrix checks |
| 5 | verification_deferred_human | $gsd-verify-work 5 — 2 human items: Windows process-tree kill on a real Windows host and the manual end-of-phase pass (see 05-VERIFICATION.md human_verification) |
| 09 | verification_deferred_human | $gsd-verify-work 09 — KaTeX release approval before vendoring (09-03: approve one immutable KaTeX release) |
| 10 | verification_deferred_human | $gsd-verify-work 10 — 1 UI gate (10-06 Task 3, DEFERRED, blocking, human-pending; see 10-VERIFICATION.md) |
| 11 | verification_deferred_human | $gsd-verify-work 11 — 4 human items (see 11-VERIFICATION.md human_verification / UAT) |
| 999.4 | verification_deferred_human | Manual Canvas checklist (R-01 fake-platform default; the real-Course consumer question stays open) |
| 999.5 | verification_deferred_human | WINDOWS.md windows 2–3: LAN cross-device phone reachability (02) and real Moodle GIFT import (02.1) — human verify/waive before /gsd-ship |

## Quick Tasks Completed

| ID | Task | Date | Status |
|----|------|------|--------|
| 260812-e2m | Four reader defects: leaked print CSS killing the glossary popover, `## TERMS` overrunning into lesson tables, relative `@font-face` urls 404ing on nested routes, authored-hint fallback printing a slug | 2026-08-12 | complete ✓ |
| 260813-r5c | Merge the source-to-course reframe from `origin/main` and renumber the reading/teaching phase from 14 to 13.5, resolving the two-phases-one-number collision | 2026-08-13 | complete ✓ |
| 260813-x3g | Reframe slice 1: replace the flat Phase 14-17 sequence in ROADMAP.md with the nine subphases (14A-17B) plus four governance clauses per synthesis section 15/16.3, and point SOURCE-TO-COURSE.md at them; originals preserved as historical rationale | 2026-08-13 | complete ✓ |

Found by driving the running daemon in a browser, not by the test suite — the
suite was green throughout. Fixes verified the same way after execution:
popover renders at 435x80 (`display:block`, previously 0x0 / `display:none`),
4/4 fonts return 200 from `/assets/fonts/` (previously 0/4), `## TERMS` above
`## LESSON` mints only authored terms, and the authored hint shows the section
title rather than its slug. New guard: `tests/stylesheet_roundtrip.py`.
