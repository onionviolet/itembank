# 17B-03 evidence: the learner pass, stages 1 through 8

Recorded 2026-09-01 by plan 17B-03 Task 1, run from the repository root
on Darwin 27.0.0 arm64. `python` is not on PATH on this machine, so every
command uses `python3` (the recorded 16C-precedent deviation, also
recorded by 17B-01 and 17B-02). Written incrementally as each stage was
observed; a stage section is complete when it carries its observations
and its gate note.

## Serving commands, verbatim

The 16B freeze records the course routes (`/`, `/course/<id>`,
`/course/<id>/<area>`, `/help/<code>`, `/activity`, `POST /api/shelf`)
and the 17A freeze records the served routes its stylesheet roundtrip
measures (the quiz included), both served by the one daemon. The
commands run for this pass:

```
python3 itembank.py daemon . --no-open --port 8730
```

Daemon banner, verbatim (first launch):

```
itembank daemon
  dir     /Users/weiwei/Documents/Dev/itembank
  banks   26
  plans   2
  collision  stem 'SKILL': ./.agents/skills/author-bank/SKILL.md wins, ./.claude/skills/author-bank/SKILL.md loses
  url     http://127.0.0.1:8730/
```

The daemon was restarted twice during the pass: once to serve the KEY
card fix (D-06 item 1 below), once after a rate-limit interruption cut
the session and the background process with it. The fixture course id is
`ba070378d35d44e7` (the sidecar object minted by 17B-02).

The graded sitting (stage 6) uses the runtime session CLI, the CLI twin of
the served sitting:

```
python3 itembank.py start course_fixture_17b/unit3_bank.md --mode exam --seed 0
python3 itembank.py next <session file>
python3 itembank.py submit <session file> --answer <answer>
python3 itembank.py mark --session <id> --base course_fixture_17b --item <ref> --verdict pass|fail
python3 itembank.py report <session file>
```

Widths were emulated in the driven browser (Claude Browser pane, the
one tool available in this session; no new dependency was added, D-08)
with `resize_window` at 1280x900, 768x900, and 375x812. Below 768 the
pane emulates a mobile device (touch input, mobile user agent), which is
the touch leg. Keyboard input was sent as key events (`Return`,
`Escape`). A tool-side limitation is recorded honestly rather than
worked around silently: partway through stage 4 the pane's screenshot
and pointer pipeline stalled (screenshots returned black frames; pointer
clicks stopped reaching the page while the DOM, accessibility tree,
network log, and JavaScript evaluation kept working). From that point,
structure was verified through the accessibility tree (`read_page`),
text through `get_page_text`, layout through the real layout engine's
`getBoundingClientRect` geometry, and the remaining form submissions
were dispatched as DOM `click()` on the real submit controls, which sent
the same `POST` the pointer path sends (confirmed in the network log by
the `?receipt=` redirect each answer produced). Where a step was driven
that way the section says so. Pixel screenshots are therefore not part of
this record; the visual acceptance is the human half of G8 (Task 4,
deferred, see 17B-GATES.md).

## Stage 1: Arrive (shelf, scope tree, resume)

Command: `GET http://127.0.0.1:8730/` at 1280 width, keyboard.

Accessibility tree, verbatim as read:

```
heading "Courses"
main
 region
  generic "New here? A short walkthrough shows how a course works."
  form
   button "Start walkthrough"
   button "Skip for now"
 form
  button "Replay walkthrough"
 article
  heading "Aldrasse Fen Ecology 101"
  generic "Up to date"
  generic "Not started"
  link "Start Aldrasse Fen Ecology 101" href="/course/ba070378d35d44e7"
 article
  heading "Study Skills Basics (Sample)"
  generic "Up to date"
  generic "Not started"
  link "Start Study Skills Basics (Sample)" href="/course/sample-study-skills"
  generic "For exploring itembank. Remove it anytime."
  form
   button "Remove sample course"
```

Observations:

- The shelf renders the fixture course from its sidecar name (not its
  folder name), with the 16B attention chips `Up to date` and `Not
  started`; no percentage, no aggregate score, no invented ratio (the
  record supplies no numerator or denominator, so the card carries none,
  per IL-20260827-01's rule). The bundled sample course sits beside it
  with its `(Sample)` suffix inside the name string.
- First-run walkthrough offered and skippable; keyboard order is
  walkthrough controls, then the course card link, then the sample card.
- Resume: the shelf's card state is `Not started` before any activity. After
  the practice sitting (stage 5) the daemon's quiz route resumed the open
  session at its current item on every return (`GET /quiz/unit3_bank`
  re-served the item the learner was on, three times during the pass,
  including after navigating away to the paced lesson view and back). Stage
  8 records the sampled interruption scenario.
- The scope tree (field, course, unit) is NOT visible as structure on the
  shelf. The shelf shows courses only, because `course_shelf_state` runs
  FILE-04's documented degraded mode (an immediate-subdirectory scan of the
  daemon root, recorded in 16B-FREEZE.md's deferral table) and no route
  renders `scope.md`'s field scope. The scope tree is visible as structure
  on the two rollup screens (stage 7). Recorded as D-06 item 2 below,
  not silently passed.

Gate note: G8 first-run and resume transitions preserve context (course
name, state chips, walkthrough) at 1280; the 768 and 375 legs are in the
width table under stage 4. G5's shelf progress display carries no
aggregate.

## Stage 2: Orient (course frame, objectives, sources, locators)

Command: `GET http://127.0.0.1:8730/course/ba070378d35d44e7` at 1280,
keyboard.

Accessibility tree, verbatim as read:

```
link "<- Back to courses" href="/"
heading "Aldrasse Fen Ecology 101"
main
 navigation "Course areas"
  list: Overview, Learn, Practice, Test, Course map, Sources, Build and review, Evidence
   (each a link under /course/ba070378d35d44e7/<area>, Overview aria-current)
 status (hidden anchor-missing region, revealed only by the restoration script)
 heading "Overview"
 generic "Nothing has been added to Overview for this course yet."
```

Observations:

- The course frame renders the eight 16B areas at every width from one
  route, with the real course name from the sidecar and the frozen
  `Nothing has been added to {area} for this course yet.` notice.
  `content_available` is False for every area: this is the 16B freeze's
  recorded deferral ("No real course-area content; every area reports
  content_available False", owner Phases 14A and 14B execution), not a
  17B regression. Recorded as D-06 item 3 below.
- Orientation therefore happens on the lesson route the bank stem serves
  (`GET /lesson/unit3_bank`), which is where the unit's cited sources and
  locators live: every source-derived paragraph renders its `[SRC:
  fen-notes #basin-overview]` style locator inline and inspectable
  (counts on the served page: fen-notes #basin-overview 2, #water-table-
  dynamics 5, #peat-accumulation-and-decay 2, #mineral-inflow-and-the-
  lagg-boundary 1; moss-survey #annual-cycle 3, #hydrological-sensitivity
  2). The lesson's section list is a `navigation "Sections in this
  lesson"` landmark with seven anchors, and each section closes with an
  `Items testing this` list linking the objective's items, so objectives
  and their items are visible from the reading surface.
- Direct-reading treatment (O3.5, `Read The Source: The Lagg Boundary`):
  the lesson section names the source section to read and the locator
  `[SRC: fen-notes #mineral-inflow-and-the-lagg-boundary]`; the source
  file itself (`course_fixture_17b/sources/fen_hydrology_field_notes.md`)
  is a plain Markdown document that reads by scrolling. No served route
  opens the raw source file as a view (the 16B Sources area is the
  degraded state above), so the source view leg of FLOW-02 is covered by
  the lesson route's scrolling (no pagination control, no item cap: the
  document height at 1280 measured 6830 px and scrolls) and by the plain
  file. Recorded under D-06 item 3.

Gate note: G8 source-inspection transition holds on the lesson route;
the course-area content leg is owed to 14A/14B wiring.

## Stage 3: Predict (prompt before mechanism, participation evidence)

Commands: `GET /lesson/unit3_bank` (continuous document) and
`GET /lesson/unit3_bank?view=paced` (the 16D paced view), then the
practice sitting's Q1 (stage 5).

Observations:

- The prediction prompt precedes the explanatory content. In the section
  `Two Layers, Two Clocks` the served text reads, first: "Before reading
  further, make a prediction and write it down: after a heavy storm, does
  the fen's water table stay high for weeks, or fall back within days?
  Commit to one answer now; the first practice item records your
  prediction as participation, not as a grade." The damped-oscillator
  and acrotelm/catotelm paragraphs follow it. Verified in both the
  continuous and the paced view (`get_page_text` transcript).
- The paced view rendered `Step 1 of 1` (the authored lesson carries no
  step-grammar checkpoints, so 16D's run store holds the whole lesson as
  one step and created `course_fixture_17b/_attempts/lessonrun_unit3_bank.json`
  as presentation state). No inline checkpoint exists for the prediction.
- The prediction's response path is therefore the practice sitting's Q1
  (`4dc7c93e7a4c4f18`, the `## ACTIVITIES` row `prediction`, evidence
  class `activity_trace`). When Q1 was answered `C` in the practice
  sitting (stage 5) the evidence log recorded it as an ordinary scored
  response, verbatim from `course_fixture_17b/_evidence/evidence.jsonl`:

  ```
  response 4dc7c93e7a4c4f18 score= True mode= practice hint_tier= None
  ```

  and the practice surface displayed `Correct` for it. That is a graded
  verdict, not participation-only evidence. The registry vocabulary exists
  (`model.ACTIVITY_EVIDENCE_STATES` carries `activity_trace`; 16C added
  `activity_completed` and `activity_skipped` to `evidence.KNOWN_EVENT_TYPES`
  with `notes.strategy_lifecycle_event` as their writer) but no served
  route or runtime path maps an activity-linked item response to a
  participation event, and `grep activity_trace *.py surfaces/*.py`
  finds the vocabulary constant only. Recorded as D-06 item 4 below. The
  lesson's own sentence promising participation-only recording is,
  today, not honoured by the practice surface; this record says so.

Gate note: stage 3 is NOT passed on the "never a graded verdict"
clause; the gap carries a mechanism and an owner (D-06 item 4).

## Stage 4: Read and learn (capabilities, widths, keyboard, touch)

Command: `GET /lesson/unit3_bank` at 1280, 768, and 375.

Capability checklist rows (17B-UI-SPEC section 2), as observed on the
served page's accessibility tree:

| capability | observed |
|---|---|
| Hover and focus term definitions, accessible equivalent | each `[[term]]` renders as a native `button.term` carrying `popovertarget=gloss-<term>` and `aria-details=gloss-<term>`; the definition is a `div.gloss[popover]` holding the term, its definition, and a `Full entry` link into the Glossary section. Keyboard: the button was focused and `Return` was pressed; `gloss-acrotelm` reported `:popover-open` true. Pointer: a click on the same button toggled it closed (`openBefore true, openAfter false`). Touch: at 375 (mobile emulation) the same native button is the tap target; the pane's pointer pipeline had stalled by then, so the touch activation itself was not observed by this agent and is listed under the deferred human items. A Glossary section at the end carries every term with `Back to first use` links, the no-hover equivalent. |
| Things-to-know block | `region` labelled `Key point`, title `The Aldrasse drought threshold`, footer `key: 76f829119a7142fd · exports to Anki`, `Add to review` form (the runtime is serving, so the real control renders, not the unavailable copy). See D-06 item 1 for the body-text defect found and fixed here. |
| Expert-tip block | `region` labelled `Expert tip` in `Moss As Instrument`, body as authored. |
| Cited visual explanation with static fallback | `image` whose accessible name is the full authored alt text ("Four phases in a clockwise circle: spring green-up, then early-summer investment, then the late-summer lantern phase, then the autumn wager. The arrow into early-summer investment is marked as the hinge..."), followed by the credit and derivation line ("Diagram drawn for this unit, synthetic. Drawn from the Annual cycle section of lantern_moss_survey.md; synthesis, no tracing of any published figure"). The SVG itself carries title and desc (17B-02). |
| Prediction prompt, participation-only evidence | prompt verified (stage 3); participation-only recording not honoured (D-06 item 4). |
| Other semantic roles present | `Example` (Banking Peat), `Common mistake` (the `[!MISCONCEPTION]` card), `Not settled` (the `[!UNCERTAINTY]` card), `In short` (the `[!SUMMARY]` card), each a labelled `region`. |
| Items testing this | every section closes with links to its items (`/quiz/unit3_bank#q<n>`), Q7 and Q8 both under `Moss As Instrument`. |

Layout geometry from the real layout engine (JavaScript
`getBoundingClientRect`, `document.documentElement.scrollWidth` against
`innerWidth`), verbatim results:

| width | horizontal body scroll | term button height | media overflow |
|---|---|---|---|
| 1280 | false | 34 px | not measured (no image wider than viewport at any width) |
| 768 | false | 34 px | false |
| 375 | false | 30 px | false |

The term buttons are inline controls inside prose; at 30 to 34 px they
sit below the 44 px minimum UI-SPEC section 8 sets for tablet touch
targets. WCAG 2.5.8 exempts inline targets within a sentence, and the
17A freeze added 44 px only to `summary` controls; whether the inline
exemption is accepted for term chips is a judgment left to the human
accessibility review (Task 4 deferral), and the measurement is recorded
here so that review has the number.

Plain-Markdown coherence (the agent half of G4): see the dedicated
section after stage 8.

Gate note: G4 keyboard and narrow-screen legs observed; touch activation
and screen reader are human items (Task 4). G8 learn transition holds.

## Stage 5: Practice (hint ladder, targeted feedback, pending short)

Command: `GET /quiz/unit3_bank` (the daemon's per-bank practice session,
mode `practice`, seed default). Item order served: Q5, Q2, Q6, Q3, Q1,
Q4, Q8, Q7.

Pre-answer served bytes (curl of the same route, scanned before any
answer):

```
grep -c "CORRECT:" quiz.html        -> 0
grep -c "WHY BEST" quiz.html        -> 0
authored tier text (for example "acrotelm") in the quiz page -> 0 occurrences
```

No key, no rationale, no authored hint text is in the page before the
learner answers; hint cards carry only their header and unlock sentence.

Hint ladder as served on the first item, verbatim from the accessibility
tree:

```
region
 heading "Hints"
 list
  TIER 0 · LESSON        "Tier 0 unlocks after another attempt. Or unlock it now with "I'm stumped"."
  TIER 1 · OBJECTIVE     "Tier 1 unlocks after tier 0."
  TIER 2 · TRAP          "Tier 2 unlocks after tier 1."
  TIER 3 · RATIONALE     "Tier 3 unlocks after tier 2."
  TIER 4 · DISCRIMINATOR "Tier 4 unlocks after tier 3."
  TIER 5 · REVEAL        "Tier 5 unlocks after tier 4."
 form
  button "I'm stumped, show the next hint"
region "Optional generated guidance"
  button "Get optional guidance"
```

This is RTS-09's locked-card contract exactly: a locked card carries only
its header and its unlock sentence, no progress indicator over the
ladder, no reveal control, no dimmed affordance, no first person, and the
tier text is absent from the DOM until the runtime unlocks it.

Sequence observed (Q5, drought threshold):

1. Wrong answer `B` submitted (pointer click on the radio label via the
   pane, then the `Submit answer` button; the network log shows `POST`
   then `GET /quiz/unit3_bank?receipt=Jq6fApy4m5EgpjMb5QUPR1QzfJHBximm`).
   Page after: status `Not correct. Try a different answer, or open the
   next hint.`; the card holds on the same item; tier 3's header changed
   to `TIER 3 · RATIONALE FOR B`, naming the learner's specific wrong
   answer while its text stays locked; the stumped button's label became
   `Open the next hint`. Evidence row: `response 3010fee339a94556 score=
   False mode= practice`.
2. `Open the next hint` (dispatched as a DOM click on the real submit
   control after pane pointer input stalled). Page after: `TIER 0 ·
   LESSON` shows its authored content, `The Drought Threshold` (the
   `[LESSON-REF:]` pointer); tier 1 now carries the unlock-now sentence;
   tiers 2 through 5 still locked. Evidence row: `hint 3010fee339a94556`.
3. Correct answer `D` submitted. Page after: `Correct`, the session
   advanced to Q2 with a fresh, fully locked ladder. Evidence row:
   `response 3010fee339a94556 score= True mode= practice hint_tier= 0`;
   the report distinguishes correct-after-tier from plain correct.
4. Q2 `B`, Q6 `A`, Q3 `A,D` (native checkboxes, `Select 2` legend), Q1
   `C` (the prediction; see stage 3), Q4 (the build item renders four
   labelled `select` controls, one per step, listing the four phases: the
   keyboard-operable equivalent path, no drag required; set Green-up,
   Investment, Lantern, Wager), Q8 `C` (the transfer item), each
   recorded once with `score= True`.
5. Q7 (short). A prose response was entered in the `Your response`
   textarea and submitted. Page after, verbatim:

   ```
   Recorded, and waiting on a mark.
   A constructed response is not scored by the machine. This sitting stays on this item until a human marker records a verdict, so nothing you wrote has been graded and no model answer is shown to you now.
   Record the verdict with itembank mark --session <id> --item q7 --verdict pass|fail, then reload this page to continue.
   ```

   Evidence row: `response a42004eabf0343b9 score= None`. No model answer,
   no rubric, no verdict was served; `score` is `None`, never `False`.
6. The mark, through the runtime's one gate:

   ```
   python3 itembank.py mark --session 76ba50caf1d143a09a266b7e0019cf19 --base course_fixture_17b --item q7 --verdict pass --rubric '[{"point":"Names the station-mean vitality threshold (below 2.5) as the drought-equivalent signal","pass":true},{"point":"Connects it to the dipwell drought definition (more than twenty five centimeters down, sustained about four weeks)","pass":true},{"point":"States the evidential basis or its limit (nine seasons of plot data at this one fen, roughly one month lag)","pass":true}]' --notes "17B-03 learner pass practice mark, human-role verdict recorded by the coordinator agent under the 2026-09-01 delegation, labeled as such"
   ```

   Output tail: `1 recorded, 0 already recorded`, exit 0 (mark event
   `f4bdd15098df4a06bfcfc0447e6b3aed`). Reloading `/quiz/unit3_bank` then
   served `Session complete.`

One display defect observed on this surface: the session-context line
read `Item 1 of 8` on every item of the sitting. `surfaces/quiz_page.py`
line 314 hard-codes `<b id="pos">1</b>` and the server-rendered answer
flow re-serves the template substituting only `__CTX_TOTAL__`; the two
JavaScript updaters (lines 811 and 1404) belong to the client-rendered
paths and do not run on the receipt-redirect flow. Recorded as D-06
item 5 below.

Gate note: G6 practice leg holds (no key before the runtime's gate, hint
tiers runtime-gated one at a time, prose pending until a human mark, the
mark recorded as an event beside the response, never an edit). G8
practice transition holds except the position counter (D-06 item 5).

## Stage 6: Test (the graded sitting in exam mode)

The graded sitting ran through the runtime session CLI, the CLI twin of
the served sitting, because the daemon's per-bank session is fixed in
`practice` mode. Session file
`course_fixture_17b/_attempts/session_46e90a278e08.json`, session id
`d15cb53a1c6f435db6023e6b8e4721f3`, `--mode exam --seed 0`.

Two facts checked on the served surface first, because G6 is about
surfaces: `POST /api/start` with `{"bank":"unit3_bank","mode":"exam",
"count":8,"seed":0}` returned the public item with keys
`difficulty, id, lesson_slug, number, response_schema, schema_version,
stem, steps, type` (a build item; no key field), and `POST /api/submit`
in that exam session returned top-level keys `accepted, action,
evidence, hint_tier, interaction_result, item_id, next, status`: no
`score`, no `explain` (the answer sent was malformed for a build item,
so the action was `hold`; the disclosure shape is what this check is
for, and the served test `tests/evidence_roundtrip.py` asserts the same
absence for a genuine exam answer).

The CLI driver, transcribed verbatim, ran as
`python3 /private/tmp/.../t6_exam_sitting.py` from the repository root;
its calls are the shipped `next`, `submit`, `mark`, and `report`
commands. Its output, verbatim:

```
next: cursor 1/8 item q2 type=mc public keys=difficulty,id,lesson_slug,number,options,response_schema,schema_version,stem,type leaked=[]
submit q2: action=defer_feedback score=True explain_present=False evidence=recorded
  after submit, next serves item q2 at cursor 1 (parked=True)
  mark q2: 1 recorded, 0 already recorded
next: cursor 2/8 item q4 type=build public keys=difficulty,id,lesson_slug,number,response_schema,schema_version,stem,steps,type leaked=[]
submit q4: action=defer_feedback score=True explain_present=False evidence=recorded
  after submit, next serves item q4 at cursor 2 (parked=True)
  mark q4: 1 recorded, 0 already recorded
next: cursor 3/8 item q6 type=mc public keys=difficulty,id,lesson_slug,number,options,response_schema,schema_version,stem,type leaked=[]
submit q6: action=defer_feedback score=True explain_present=False evidence=recorded
  after submit, next serves item q6 at cursor 3 (parked=True)
  mark q6: 1 recorded, 0 already recorded
next: cursor 4/8 item q5 type=mc public keys=difficulty,id,lesson_slug,number,options,response_schema,schema_version,stem,type leaked=[]
submit q5: action=defer_feedback score=True explain_present=False evidence=recorded
  after submit, next serves item q5 at cursor 4 (parked=True)
  mark q5: 1 recorded, 0 already recorded
next: cursor 5/8 item q3 type=multi public keys=difficulty,id,lesson_slug,number,options,response_schema,schema_version,stem,type leaked=[]
submit q3: action=defer_feedback score=True explain_present=False evidence=recorded
  after submit, next serves item q3 at cursor 5 (parked=True)
  mark q3: 1 recorded, 0 already recorded
next: cursor 6/8 item q7 type=short public keys=difficulty,id,lesson_slug,number,response_schema,schema_version,stem,type leaked=[]
submit q7: action=defer_feedback score=None explain_present=False evidence=recorded
  after submit, next serves item q7 at cursor 6 (parked=True)
  report while pending: status=active pending_manual=1 auto_attempts=6
  mark q7: 1 recorded, 0 already recorded
next: cursor 7/8 item q8 type=mc public keys=difficulty,id,lesson_slug,number,options,response_schema,schema_version,stem,type leaked=[]
submit q8: action=defer_feedback score=True explain_present=False evidence=recorded
  after submit, next serves item q8 at cursor 7 (parked=True)
  mark q8: 1 recorded, 0 already recorded
next: status=complete (no item)
final report: status=complete summary={"auto_attempts": 7, "auto_correct": 7, "pending_manual": 0}
submit against the closed sitting: exit=1 message='session is already complete'
```

(Before the interruption the same session had already served item q1,
recorded answer `C` as `defer_feedback`, and been collected by a mark;
the transcript above resumes at cursor 1.)

Observations:

- Every `next` payload carried the public item only; the leaked-field scan
  (`correct, answer_key, key, why, disc, trap, model, rubric, explain,
  distractors, second_best`) found nothing on any of the eight items.
- Every `submit` in exam mode returned `action=defer_feedback` with no
  `explain`; the CLI payload does carry the runtime's own `score` field
  (the CLI is the local runtime client, and the served surface strips
  it, see above).
- The short item q7 recorded with `score=None`, the report while it was
  pending read `pending_manual=1 auto_attempts=6`, and the sitting stayed
  parked on q7 until the human-role mark landed. The mark is an appended
  event; the response event's `score` stays `None` forever (GRADING.md).
- Final report: `status=complete`, `auto_attempts 7, auto_correct 7,
  pending_manual 0`. A submit against the closed sitting was refused:
  `session is already complete` (exit 1). A sitting's mode is immutable
  (`runtime.teaching_transition` refuses a mismatched mode by name).
- The transfer item q8 was included and answered (`C`).

Defect found here (D-06 item 6): a deferred-feedback sitting (`exam`,
`diagnostic`, and the `legacy` policy) does not advance past a
machine-scored item on its own. `runtime.teaching_transition` returns
`defer_feedback` without moving the cursor for a right answer under a
`defer_feedback` policy (runtime.py, the `policy["right"] ==
"defer_feedback"` branch), and the only collector, `marker_close` called
from `surfaces.session.do_next`, advances solely on a human mark event
(`settled_mark_keys` counts `mark` events only). The transcript above
shows it directly: `after submit, next serves item q2 at cursor 1
(parked=True)` on every machine-scored item, and each advanced only
after `mark --item q<n>`. On the served quiz page the same state renders
`Recorded. This mode holds every verdict until the sitting is closed.`
with a `Check again` control that asks the server and gets the same item
back. The docstring of `marker_close` frames "exam must not move the
cursor before an accepted mark" as design, so the owner should decide
whether a machine-scored deferred item settles at the marker's desk
(current behavior, which makes an eight-item exam need eight marks) or
settles on its recorded score. Owner: the runtime phase that shipped
`FEEDBACK_POLICIES` (Phase 6, amended 2026-08-24). Workaround used here:
the marks, each labelled in its `--notes`.

Gate note: G6 holds on every clause it names (no key before the gate, no
invented score, prose not auto-graded, frozen sitting immutable); the
advance defect is a G8 flow finding routed under D-06.

## Stage 7: See progress (both rollup screens)

Script `t7_rollups.py`, transcribed below, run as
`PYTHONPATH=. python3 t7_rollups.py <out dir>` from the repository root.
It computes the GRAPH-03 tuples once (frozen 16C
`progress_claims.claims_from_events` and `progress_claims.fill_state`
over `evidence.capture_events` of the fixture's real log, with course
records in the shape that function documents, fed from `scope.md` and
`course-graph.md`: seven required objectives, each cited) and renders
both screens from the same tuple dict through frozen 17A primitives only.
Output, verbatim:

```
rollup_dim.html bytes=22518 sha256=e797f28bd2672f95bf4ef6ff250e579f415e709877d041eaf2218fc043e1453f
rollup_map.html bytes=19375 sha256=6d1743c51ae9a63043336189bcc5171ff9d0f663452bee0636330bfdbc5310ce
tuples sha256=66ec543c07e700442aa2d7f9071ded872b395b59b2fecaf0330a2475fa451092 (identical input to both screens)
unit complete under afe101-complete-v1: True
settled responses per objective: {"afe:unit3.cycle": 3, "afe:unit3.instrument": 4, "afe:unit3.lagg": 2, "afe:unit3.layers": 2, "afe:unit3.minerotrophy": 2, "afe:unit3.peat": 2, "afe:unit3.threshold": 3}
retention words: {"afe:unit3.minerotrophy": "unknown", "afe:unit3.layers": "unknown", "afe:unit3.threshold": "unknown", "afe:unit3.peat": "unknown", "afe:unit3.lagg": "unknown", "afe:unit3.cycle": "unknown", "afe:unit3.instrument": "unknown"}
fill states: [('afe:unit3.minerotrophy', 2, 4), ('afe:unit3.layers', 2, 4), ('afe:unit3.threshold', 3, 4), ('afe:unit3.peat', 2, 4), ('afe:unit3.lagg', 2, 4), ('afe:unit3.cycle', 3, 4), ('afe:unit3.instrument', 3, 4)]
-- field --
  Design coverage: 7 of 7 required objectives with a cited source
  Participation: Indeterminate: Fenland Systems has no fixed denominator.
  Settled evidence: 16 of 18 responses with a settled mark
  Current retention: 7 of 7 objectives unknown
  Formal completion: 7 of 7 required objectives formally complete
  Selected enrichment: Indeterminate: Fenland Systems has no fixed denominator.
  Open uncertainty: 2 pending review; Unknown: not enough settled attempts yet
   Open scope. Never reports complete. Every claim above is as of scope version FS-2026-09-01.1.
-- course --
  Design coverage: 7 of 7 required objectives with a cited source
  Participation: Indeterminate: Aldrasse Fen Ecology 101 has no fixed denominator.
  Settled evidence: 16 of 18 responses with a settled mark
  Current retention: 7 of 7 objectives unknown
  Formal completion: 7 of 7 required objectives formally complete
  Selected enrichment: Indeterminate: Aldrasse Fen Ecology 101 has no fixed denominator.
  Open uncertainty: 2 pending review; Unknown: not enough settled attempts yet
   Bounded scope, membership version AFE101-m1. Completion predicate afe101-complete-v1: complete.
-- unit --
  Design coverage: 7 of 7 required objectives with a cited source
  Participation: Indeterminate: Unit 3: Peat Hydrology and the Lantern Moss Cycle has no fixed denominator.
  Settled evidence: 16 of 18 responses with a settled mark
  Current retention: 7 of 7 objectives unknown
  Formal completion: 7 of 7 required objectives formally complete
  Selected enrichment: Indeterminate: Unit 3: Peat Hydrology and the Lantern Moss Cycle has no fixed denominator.
  Open uncertainty: 2 pending review; Unknown: not enough settled attempts yet
   Bounded scope, membership version AFE101-m1. Completion predicate afe101-complete-v1: complete.
DIM: percent signs=4, aggregate 'score' words=0, 'Retrievability'=0
MAP: percent signs=4, aggregate 'score' words=0, 'Retrievability'=0
```

The rendered screens and the tuple set are committed beside this file:
`17B-03-rollup-dim.html`, `17B-03-rollup-map.html`,
`17B-03-rollup-tuples.json` (hashes above). Structural checks on the
rendered bytes: visible percent signs 0 on both (the four `%` characters
each page carries are inside its stylesheet), the word `score` absent,
`Retrievability` absent, seven `ib-fill` rows (`role="img"`, accessible
name `n of 4`, no `aria-valuenow`) on both, 28 `ib-card` rows on DIM
(three scopes times seven dimensions plus seven objectives) and 2 on
MAP (one direct child per parent scope).

Observations against 17B-UI-SPEC section 3:

- ROLLUP-DIM: every figure is `n of N <rule>` or the frozen indeterminate
  copy; the required class is stated on its rows (`required objectives
  with a cited source`, `required objectives formally complete`); no
  enrichment member exists, so `Selected enrichment` reads indeterminate
  rather than zero; retention is a state distribution (`7 of 7
  objectives unknown`) and never a number; open uncertainty carries the
  pending count (`2 pending review`: the two throwaway served-API
  sessions' responses from the stage 6 disclosure check and the offline
  run, recorded honestly as pending in the same log) and the unknown
  retention reason. No aggregate anywhere.
- ROLLUP-MAP: each parent shows its direct child as a card carrying that
  child's own settled-evidence summary and `bounded`/`complete` (or
  `open` / `as of <version>`) chips; nothing aggregates past the direct
  child.
- The bounded course reads `complete` under `afe101-complete-v1` because
  every required objective has settled evidence; the open field never
  reads complete and states `as of scope version FS-2026-09-01.1` on its
  block. Adding enrichment could not lower either (separate rows).
- The retention words are all `unknown` (`not enough settled attempts
  yet` in the retention module's own terms), so every fill state is
  stepped down to at most 3 of 4: the two-way movement D-14A-3 requires,
  visible on the unit.

Two primitive findings (D-06 items 7 and 8): the 17A freeze has no card
primitive that takes a fill-state row inside a child card, so the
ROLLUP-MAP child card is the frozen `course_shelf` card (name, tuple
summary as meta, chips) with the frozen `fill_state` rows placed beside
it rather than inside it (the 17B-UI-SPEC sign-off recommendation named
exactly this gap; recorded before the Task 2 checkpoint as the plan
requires); and `progress_comprehension_display` renders each determinate
claim as text in a card without the `progressbar` role and
`aria-valuetext` that `progress_claims.ARIA_CONTRACT` (16C, D10)
specifies for a determinate claim (the fill state's `img` role with a
words-and-number name is per contract).

Gate note: G5 evidence rows rendered in both models over identical
tuples, denominators stated, pending and unknown shown, no aggregate;
the default choice is Task 2's record (provisional, owed to Weibao).

## Stage 8: Continue (next action, one sampled interruption)

- Next action. `surfaces/ia.py` `LOOP_NEXT_ACTION["D"]` carries `Resume
  practice` / `Start practice` and `["C"]` carries `Resume {course name}`
  / `Continue reading: {heading}`. After the practice and exam sittings
  the shelf was re-read (`GET /`): the fixture card still read `Up to
  date`, `Not started`, `Start Aldrasse Fen Ecology 101`. The shelf's
  state comes from the course record only; no route composes the loop
  next action from session or evidence state, so the course path does not
  yet name the next action from what the learner did. Recorded as D-06
  item 9. Inside the sittings the next action is always present: the
  quiz route re-serves the open item (practice) or `Session complete.`,
  and the paced lesson view announces `Resuming at step N.` from its run
  store.
- Sampled interruption, the real one. This pass was interrupted by a
  rate limit between stage 5 and stage 6, which killed the daemon
  process and the agent session. Durable state survived without loss:
  the exam session file resumed at `cursor 1` with its one recorded
  response and mark intact (`next` served q2, transcript in stage 6), the
  evidence log kept every event, and the daemon restarted from the same
  command. That is FLOW-01's binding rule ("a loop interrupted at any
  step (crash, cancellation, close-and-reopen) never loses its position;
  the next visit ... recomputes the resume unit from durable state")
  observed on loop D, the session-cursor resume unit.
- Sampled served scenario (APP-02 probe, deep link into content that is
  gone): `GET /course/ba070378d35d44e7/learn` serves the hidden
  `data-anchor-missing hidden role="status"` region carrying the frozen
  `The part of this page that link pointed at is no longer here. The rest
  of the page is below.` notice and the restoration script that reveals
  it when `location.hash` names no element; the `noscript` copy (`Links
  to a specific part of this page still work...`) covers the script-free
  case. Observed on served bytes; the browser-side reveal is part of the
  human visual pass.

## The journey with the network unplugged

Script `t8_offline.py`, transcribed below, run as
`PYTHONPATH=. python3 t8_offline.py` from the repository root. It
monkeypatches `socket.socket.connect`, `connect_ex`, and
`socket.getaddrinfo` in the process before importing the daemon, so any
non-loopback connection or DNS lookup fails as an unreachable network
(the same "network access unavailable to the process under test"
mechanism 17B-CONTEXT D-07 names for the restore drill; a literal radio
toggle is a system setting this agent does not change), starts
`daemon.cmd_daemon` in a thread on port 8741, then walks the journey over
loopback. Output, verbatim (access-log lines omitted):

```
itembank daemon
  dir     /Users/weiwei/Documents/Dev/itembank
  banks   26
  plans   2
  collision  stem 'SKILL': ./.agents/skills/author-bank/SKILL.md wins, ./.claude/skills/author-bank/SKILL.md loses
  url     http://127.0.0.1:8741/
daemon answered on loopback after 0.8s with the network unplugged
GET /                                                            200 marker present
GET /course/ba070378d35d44e7                                     200 marker present
GET /lesson/unit3_bank                                           200 marker present
GET /quiz/unit3_bank                                             200 marker present
GET /assets/fonts/ia-writer-quattro/iAWriterQuattroS-Regular.woff2 200 
POST /api/start -> item q3 type multi, key fields present: []
POST /api/submit -> action advance, evidence recorded, hint ladder from runtime: present
POST /api/teach (stumped) -> action reveal_tier, tier shown: None, tiers locked: 0
non-loopback connection attempts refused during the run: 0 []
```

Shelf, course frame, lesson, quiz, the self-hosted font, a session start,
a scored submit with the runtime's ladder payload, and a stumped tier
reveal all worked with the network unplugged. The process made no
non-loopback connection attempt during the run (the DEL-07 background
release check, dogfooded by this repository's `itembank.json`, did not
reach the socket within the run; had it tried, the guard would have
refused it and the daemon's own try/except swallows that). Every asset the
driven browser loaded during stages 1 through 5 was from `127.0.0.1:8730`
(network log: the pages and four `/assets/fonts/...woff2` files, nothing
else; no CDN, no KaTeX fetch on these pages).

## Plain-Markdown coherence (agent half of G4)

`course_fixture_17b/unit3_lesson.md` read as plain Markdown, no itembank
renderer (structural check transcribed, run with python3 from the
repository root):

```
headings: h1=1 h2=['SOURCES', 'LESSON'] h3=7
h3 order: ['Why The Fen Is Minerotrophic', 'Two Layers, Two Clocks', 'The Drought Threshold', 'Banking Peat', 'Read The Source: The Lagg Boundary', 'The Annual Cycle Of Lantern Moss', 'Moss As Instrument']
callouts as blockquotes (readable in any Markdown reader): ['KEY', 'EXAMPLE', 'MISCONCEPTION', 'TIP', 'UNCERTAINTY', 'SUMMARY']
term references (wiki-link form, Obsidian-native, plain readers show the brackets): ['minerotrophic', 'acrotelm', 'catotelm', 'lagg', 'vitality score']
locators: 15, keys ['fen-notes', 'moss-survey']
media directive lines: ['moss-cycle'] | static fallback in prose beside it: True
prediction prompt precedes mechanism: True
HTML tags in the file: 0
em dash characters: 0
non-Markdown directive lines (bracket tokens a plain reader shows verbatim): ['LESSON-LANG', 'MEDIA', 'SEMANTIC-PROFILE', 'SRC']
```

Read-through by the agent: the file opens with its own title and a
paragraph saying what it is; the seven sections read in teaching order;
every callout is an ordinary blockquote whose first line names its role,
so a plain reader shows `[!KEY] The Aldrasse drought threshold` followed
by the quoted text; the `[ID:]`/`[HASH:]` lines inside the KEY card show
as two short bracket lines, which a plain reader tolerates; the media
line `[MEDIA: moss-cycle]` shows as a bracket token, and the paragraphs
on either side of it describe the four phases and the hinge in words, so
the diagram's content is present without the image; the `[SRC: ...]`
locators read as inline citations. Four of the five terms are defined in
the prose at first use; `vitality score` is used with context ("a
station mean vitality score below 2.5") but its four-point-rating
definition lives only in the bank's `## TERMS` registry, a small
coherence nit for the authored unit (owner 17B-02's authoring, not a
tool defect; noted, not a D-06 item). Verdict for the agent half:
coherent standalone. The screen-reader half is Task 4 (deferred).

## G9: the strategies the tracer offers

The four registered strategies (`strategies.STRATEGY_IDS`, frozen at
16C), read from `strategies.strategy_contract(<id>)` on this tree. The
tracer's unit offers all four through the frozen picker
(`strategies.picker_rows`; `continuous_reading` is the code-owned
fallback row, `retrieval_first` is choosable only where objective policy
permits an assessment-first route). The note-authority guard is the same
for every row: `notes.note_record` carries `epistemic_role` and
`authorship` (`learner` or `authored`), promotion produces a cited
derived copy with `from_note_id` and never mutates the original, and the
lifecycle event is the closed nine-key `activity_completed` /
`activity_skipped` record with no content field (D-16C-1), so a learner
note can never become lesson truth, an answer key, a score, or mastery.

| strategy | choice | requirement | skip and resume | accommodation | evidence effect | privacy | provenance | note-authority guard |
|---|---|---|---|---|---|---|---|---|
| Continuous reading (`continuous_reading`, fallback) | choosable always; the fallback when another strategy is unavailable (`UNAVAILABLE_COPY` names it) | no required actions; optional `highlight`, `add_note` | resumes at the last read heading; skipping always allowed | highlight has a keyboard block-and-range picker and a structured block-choice list equivalent to pointer selection (D13); add_note in the normal tab order, 44 px touch target, never hover-only | `activity_completed` only | the event carries no wording; the note store is deletable and separate from the append-only log | note record names `owner`, `strategy_id`, `authorship`, targets by anchor | guard as above; no promotion path exists without the cited derived copy |
| Guided note spine (`guided_note_spine`) | choosable on any lesson carrying headings a note can anchor to (this unit has seven) | required `select_target`, `restate_in_own_words`; optional `add_question` | each prompted block may be skipped as `skipped_optional`; resume returns to the first block without a completed or skipped state | structured block-choice list (D13 keyboard and touch equivalent; drag-only highlighting forbidden); plain labelled text entry, no pointer-only path | `activity_completed`, `activity_skipped` | as above | as above; restatements are `learner_claim` notes | as above; `relocated_probable` is never auto-applied, so a moved anchor cannot silently reattach a note to other content |
| Worked reasoning (`worked_reasoning`) | choosable on any lesson carrying worked steps or an example order (Banking Peat and the cycle sequence qualify) | required `predict_next_step`, `explain_step`, `self_check` | a step may be skipped as `skipped_optional`; resume returns to the first unresolved step | labelled text entry or structured choice, keyboard reachable; self_check in the normal tab order, 44 px target, never hover-only | `activity_completed`, `activity_skipped` | as above | as above | as above; a prediction is participation, never a graded verdict (see stage 3's defect for the item path) |
| Retrieval first (`retrieval_first`) | choosable only where objective policy permits an assessment-first route (STRATEGY-01) | required `attempt_items_first`; optional `read_after` | skipping the attempt falls back to continuous reading; resume returns to the unattempted items | the shipped item surfaces, whose keyboard, touch, and screen-reader paths are the runtime's and unchanged | `activity_completed`, `activity_skipped` | as above | as above | as above; item responses go through the one scorer and never through a note |

All four state `offline_behavior: fully available offline`, and the
picker is locked mid-sitting with `MID_SITTING_LOCK_COPY` ("Strategy
changes are paused during a test sitting."). `composed_resolve` takes an
explicit layer state, so no strategy can override runtime authority or
system safety (the two fixed layers). No strategy surface makes a
hosted-model call.

## Egress record (17B-CONTEXT D-09)

No step of this plan made a hosted-model call. The driven browser's
network log holds only `127.0.0.1:8730` requests; the offline run's guard
saw no non-loopback attempt; the `Get optional guidance` control on the
quiz page was never activated (and the settings' `network_egress.
hosted_operations` is `off` by default). G11's egress row stays
not-applicable with this reason unless 17B-04 makes a hosted call at call
time.

## D-06 defects found by this pass, with mechanism and owner

1. **KEY card body rendered literal `> ` markers (in-phase fix, one
   file).** Pre-fix observation on the served lesson: the accessibility
   tree read `generic "> A water table more than twenty five centimeters
   below the peat surface > is a drought state, and t..."` inside the
   `Key point` region, and the served bytes carried `&gt; A water table`.
   Mechanism: `surfaces/lesson.py` `_parse_key_callout` tested each line
   with the `> ` prefix stripped but appended the raw line to the body,
   so every multi-line KEY body rendered its blockquote transport
   markers as text; `model.parse_key_blocks`, which the docstring says it
   mirrors, appends the stripped line. Fix: append the de-prefixed line
   (`re.sub(r"^>\s?", "", line)`), one line plus a comment citing this
   pass. Verified: the reproduction (`'> A first body line\n> and a
   second.'` became `'A first body line\nand a second.'`), the re-served
   page carries `A water table more than twenty five centimeters below
   the peat surface` with zero `&gt;`, and `tests/lesson_roundtrip.py`,
   `lesson_code_roundtrip.py`, `lesson_retention_roundtrip.py`,
   `lesson_run_roundtrip.py`, `paced_lesson_tracer.py`,
   `anki_keys_roundtrip.py` all pass. No contract change, no parser or
   scorer edit. Owner: 17B (fixed here); originating phase 03.1 (the
   card renderer), 16A (the semantic lint pass that never caught it).
2. **Scope tree not visible as structure on the shelf (stage 1).**
   Mechanism: `ia.course_shelf_state` runs FILE-04's degraded
   immediate-subdirectory scan and no route reads `scope.md`; the field
   scope has no directory. Owner: the phase that schedules FILE-04 and
   the 14B shelf wiring (16B-FREEZE deferral table). Visible instead on
   the rollup screens.
3. **Course areas carry no content (stage 2).** Mechanism: every
   `course_area_state` returns `content_available False` by 16B design;
   the Learn, Practice, Test, Sources, Evidence areas do not link the
   bank-stem routes that hold the real surfaces. Owner: Phases 14A and
   14B execution (16B-FREEZE "No real course-area content"). Orientation
   and source inspection happen on the lesson route today.
4. **Prediction response recorded as a graded verdict (stage 3).**
   Mechanism: no producer maps an `## ACTIVITIES` row with evidence class
   `activity_trace` (or 16C's `activity_completed`) to a participation
   event; the item goes through the one scorer as an ordinary response
   and the practice surface says `Correct`. Owner: the phase that ships
   the activity evidence producer (16A activity matrix execution; 16B
   already lists the missing producers).
5. **`Item 1 of 8` never advances on the server-rendered quiz flow
   (stage 5).** Mechanism: `surfaces/quiz_page.py:314` hard-codes
   `<b id="pos">1</b>`; the receipt-redirect flow substitutes only
   `__CTX_TOTAL__`, and the JavaScript updaters at lines 811 and 1404
   belong to the client-rendered paths. Owner: the quiz surface (Phase
   13.5 / 13.9 sitting fixes).
6. **Deferred-feedback sittings park on machine-scored items (stage 6).**
   Mechanism and owner in the stage 6 section.
7. **No 17A card primitive with a fill-state slot for ROLLUP-MAP child
   cards (stage 7).** Mechanism: `presentation.course_shelf` cards take
   name, meta, chips, actions; `fill_state` is a separate primitive.
   Rendered by composing the two, fill rows beside the card. Owner: 17A-03
   (primitive gap, per the 17B-UI-SPEC sign-off recommendation).
8. **`progress_comprehension_display` omits the determinate-claim
   `progressbar` role and `aria-valuetext` (stage 7).** Mechanism: the
   17A primitive renders each dimension claim as `p.ib-meta` text in a
   card; `progress_claims.ARIA_CONTRACT` (16C, D10) specifies a
   `progressbar` with `aria-valuetext` carrying words and number for a
   determinate claim. Owner: 17A-03.
9. **Shelf next action not composed from session or evidence state
   (stage 8).** Mechanism: the card state and CTA come from the course
   record only; `LOOP_NEXT_ACTION` copy exists but no collector reads
   sessions or the evidence log for the shelf. Owner: the 14B / FILE-04
   shelf wiring, with 16C's live-state collector (D-16B-12) as the named
   seam.

Observations recorded, not defects: term buttons measure 30 to 34 px
(inline-target exemption question for the human review); the daemon's
`SKILL` stem collision on the two mirrored skill directories (harmless,
deterministic, printed at startup); `vitality score` defined only in the
bank registry (authoring nit).

### 2026-09-06 normal-entry UX audit follow-up

This bounded pass follows REACH-MILESTONE's Vision alignment refinement and
the vision entries on home/navigation (2026-08-20), progressive files
(2026-08-13), feedback (2026-08-24), and course first page (2026-08-26).
It used an isolated copy of this synthetic course, starting at the daemon
root and following visible controls. No learner files were changed.
Implementation was delegated to three gpt-5.6-luna workers and reviewed by
the coordinating agent. No measured cost savings are claimed. No commits.

Ranked findings, with stable IDs for this follow-up:

| ID / status | Reproduction, expectation and observed impact | Location, smallest improvement and acceptance |
|---|---|---|
| F4 / open, reach owners 19A/19B/19D | Shelf, course, Sources lists two readable sources without an open control. The lesson explicitly assigns a source section but its citation is literal text. Test and Build and review show only empty copy. No notes control was found in Learn or the reader, and palette search for note returned no results. Activity opens an empty main region. These stop the requested source-reading, notes, formal-test and proposal/review/accept/undo journeys. | `surfaces/daemon.py::_course_area_rows`, `_course_area_extra`, `handle_report_get`, and `surfaces/ia.py::_healthy_card`. Reuse existing engines one journey at a time, beginning with a rights-checked source-reading control and return path. Do not invent a new authoring system. Acceptance must start at the shelf and reach the assigned source, a saved note, a formal sitting and a reviewed reversible proposal through visible controls. These UI paths are unavailable, not evidence that their engines are broken. |
| F6 / fixed and UI verified | Course, Sources, default coverage binding, Record this binding sent `treatment: ''`, rejected by the published schema. At 375 pixels the form widened the document to 777 pixels. Expected a valid default request and usable narrow controls. | `surfaces/daemon.py::BIND_PANEL` now omits treatment for coverage requests, constrains field width and wraps refusal text. UI-created coverage and direct-reading bindings reached the copied course journal and sidecar. The document now measures 375 pixels at a 375-pixel viewport. Regression: `tests/source_binding_surface_roundtrip.py`. |
| F1 / fixed and UI verified | Course, Learn, lesson left no visible app return navigation. Browser Back was required to continue the audit, so that original journey failed. | `surfaces/daemon.py::_lesson_context_nav`, `handle_lesson_get`, `surfaces/lesson.py::lesson_page`. Uniquely resolved course ownership supplies Back to course, with Courses fallback. Keyboard activation returned to the owning course. Standalone output has no daemon links and print CSS hides navigation. Resolver, fallback and renderer checks are in `tests/lesson_roundtrip.py`. |
| F2 / fixed and UI verified | In the lesson, focus minerotrophic and press Enter. Definition text was black on RGB(22,30,29), making the teaching aid unreadable. | Shared `.gloss` rule in `surfaces/lesson.py` now sets the theme ink color. Live text became RGB(228,235,233) on the same panel. Enter opens, Escape closes and the focus outline is visible. The lesson and open panel fit at 375 pixels. This is agent observation, not human accessibility approval. |
| F3 / partially fixed | Practice, answer correctly, observe a new question still labeled Item 1 of 8. The prior verdict also appeared as Correct beside the new unanswered item. | `_send_quiz_page` now uses the public runtime position, and `quiz_page.baseline_for` labels prior-answer feedback. Live advance showed Item 2, a wrong retry stayed at Item 2, and prior-answer copy was explicit. `tests/serve_roundtrip.py` exercises this redirect. Remaining: submitting an empty radio response produced Not correct. Small next fix is surface validation that requests a choice without submitting an attempt, with an evidence-count regression. Runtime scoring must remain unchanged. |

F4 also includes misleading resume and evidence context. The shelf continued
to say Not started and Up to date after responses were recorded. Re-entering
practice during one daemon run preserved the current question, but restarting
the daemon started another sitting. Course Evidence showed 24 responses while
the palette's global Report showed 0 live events. The counts refer to different
stores, but the UI provides no scope explanation or course report handoff.
Use existing runtime session and course evidence collectors for the next
bounded fix. Verify re-entry and restart separately, retain old sittings, and
name the report's scope. Do not treat absent attention metadata as evidence
that the learner is up to date.

The plain lesson was read directly in Markdown. Its explanations, worked
calculation, uncertainty and cycle sequence remain useful without rendering.
The standalone `[MEDIA: moss-cycle]` token does not display its diagram, and
source citations are textual locators. The prediction promises ungraded
participation, which the prior D-06 item 4 already identifies as unresolved.
No replacement lesson was authored.

Observed layouts were 1280 by 800 and 375 by 812. Course map and lesson reflow
worked in the sampled screens. Keyboard term disclosure and course return
worked. Source refusal and empty course-area states were inspected. Loading
was too brief to assess. No full screen-reader, touch-device, high-contrast,
reduced-motion, cross-subject, clean-machine restore, real learner efficacy,
or human visual-acceptance pass was performed. Modules were read around the
named symbols, not in full. Unreachable test and agent flows were not bypassed
with guessed URLs or APIs.

Validation: focused lesson, stylesheet, served-session and source-form suites
passed. Full `python3 scripts/preflight.py` completed all 110 Python suites
and the JS gate. Fast gates and JS passed. Five Python suites failed:
capabilities manifest freshness, daemon route count (32 expected, 39 present),
model-phase's nested daemon concurrent-request timeout, subject-loop's
CLI/daemon lesson comparison, and surface coverage for
`course apply-recommendation`. The subject-loop comparison requires the same
daemon-only navigation exclusion as the lesson parity tests and was returned
to the reader worker. The manifest, route table and command coverage were not
changed by this audit. The timeout's cause was not established. The clean-tree
gate also failed because the shared checkout is intentionally uncommitted,
including unrelated planning changes. The worker corrected the subject-loop
comparison and `python3 tests/subject_loop_roundtrip.py` then passed. Only that
affected suite was rerun. Final `git diff --check` passed. No clean preflight
pass is claimed.
