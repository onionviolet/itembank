---
phase: 16B-ia-modes-recovery-contract
plan: 11
type: execute
wave: 11
depends_on: ["16B-10"]
files_modified:
  - .planning/phases/16B-ia-modes-recovery-contract/16B-TRACER-REPORT.md
  - .planning/phases/16B-ia-modes-recovery-contract/16B-REVIEW.md
  - .planning/phases/16B-ia-modes-recovery-contract/16B-FREEZE.md
  - .planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
  - .planning/phases/16B-ia-modes-recovery-contract/16B-VALIDATION.md
autonomous: false
requirements: [FLOW-01, FLOW-02, APP-01, APP-02, APP-03]
estimate:
  tokens: 88000
  raw_tokens: 88000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "All five ROADMAP freeze-gate fixtures are run in one pass and each is recorded as passed, weaker proof, or not run: the loop A through G interruption storyboard, the model-disabled reading and practice walk, the two-course shelf with one corrupted course, the deep-link replay across both layouts, and the first-launch interruption with no roots, no agent, and no network."
    - "The tracer report measures rather than asserts: every duration, byte count, route count, and file count in 16B-TRACER-REPORT.md is a figure the run produced on the machine and Python version the report names, and no budget or target number appears anywhere in it."
    - "The shipped runtime is unregressed: the full suite runs green, the settings additivity baseline recorded in 16B-PRECONDITION.md is unchanged for every pre-existing key, and python itembank.py guard . reports 0 offending files."
    - "The published surface is enumerated in one place: the freeze record lists every new route, every new CLI command, every new settings key, every new closed vocabulary, every new copy constant, and every new state file this phase created."
    - "The freeze record states what it does not freeze, naming Phase 16C, Phase 17A, Phase 14A, and Phase 14B as the owners of strategies and notes, the visual system and tokens, journal-backed content, and the course schema respectively."
    - "No 16B freeze record is written on a red suite, a missing or rejecting human review, an unresolved precondition divergence, or a stage a tracer marked SKIPPED without a recorded judgment. On any missing leg the file opens with a Freeze withheld section naming that leg, the string Frozen at 16B appears nowhere in it, and the phase stays open."
    - "Every backstop row carried by plans 02 through 10 is listed in the freeze record's open items with its owner, so a marker whose evidence was never supplied is visible rather than silently passed."
  prohibitions:
    - statement: "An agent must not sign its own contract; whether nine routes, eight degraded sentences, seven mode layers, twelve help entries, and a first-run experience are legible and honest to a learner is a human's judgment, and a green suite is not that judgment."
      status: kept
      verification: flagged-unverified
    - statement: "The freeze record must not claim a leg that was not run; a leg that could not be executed is named as withheld or as a weaker proof rather than described as satisfied or omitted from the list."
      status: kept
      verification: flagged-unverified
    - statement: "A figure that was not measured must not appear in the tracer report; a budget, a target, or an estimate presented among measurements is a fabricated measurement."
      status: kept
      verification: flagged-unverified
    - statement: "A backstop marker must not be quietly upgraded to covered at freeze time; with no explicit evidence it stays insufficient and needs a human, and the freeze record carries it as an open item."
      status: kept
      verification: flagged-unverified
  artifacts:
    - ".planning/phases/16B-ia-modes-recovery-contract/16B-TRACER-REPORT.md with its five named sections"
    - ".planning/phases/16B-ia-modes-recovery-contract/16B-REVIEW.md carrying one of three literal verdict words, a signature, and a date"
    - ".planning/phases/16B-ia-modes-recovery-contract/16B-FREEZE.md opening with exactly one of two headings"
    - "16B-DECISIONS.md gains the dated D-16B-13 freeze-scope answer"
    - "16B-VALIDATION.md with its Per-Task Verification Map Status column complete, its runtime placeholder replaced by a measured figure, and its sign-off boxes resolved"
  key_links:
    - "Task 3 re-runs every suite rather than trusting Task 1's recorded result, because the review in Task 2 may have prompted a fix and a freeze record must describe the tree it is freezing rather than the tree that was tested."
    - "A stage that plan 16B-10's walk marked SKIPPED is not automatically a withholding leg, but it is never invisible: Task 3 requires an explicit recorded judgment per skipped stage, so the freeze either weighs it or names it."
    - "The freeze record's What is NOT frozen section is what plans 16C-01 and 17A-01 will read before they plan against this surface. An omission there is how a later phase silently assumes it inherited a contract 16B never made."
    - "The backstop rows are the phase's honest unknowns. Listing them in the freeze record's open items with owners is what keeps a verification pass from reading a marker's absence of evidence as a pass."
---

<objective>
Run the phase's own freeze gate and either write the freeze or name the leg that
withheld it.

`ROADMAP.md`'s Phase 16B freeze gate, quoted in full: "the full storyboard and
interruption scenarios: a synthetic run of each of loops A through G interrupted
mid-step, asserting each resumes at an exact position with a next justified
action (FLOW-01 fixture); a synthetic reading, lesson, practice, and feedback
walk with the model backend disabled, asserting scoring, the authored hint
ladder, evidence, and reports still run through the one runtime (FLOW-02
fixture); the synthetic course shelf with two fictional courses, one corrupted
so it must show its last valid overview and plain-file access, asserting exact
resume cues and every named course section (APP-01 fixture); the same synthetic
deep links replayed across wide and narrow layouts, asserting focus and scroll
restoration and identical routes in both (APP-02 fixture); and the first-launch
interruption scenario running the clearly synthetic sample course and
walkthrough with no roots granted, no agent configured, and the network
disabled, asserting offline help routes from named error codes."

All five were built by plans 16B-02 through 16B-10. This plan re-runs them in
one pass, measures the run, lets a human judge the parts a test cannot, and then
either freezes or says why not.

The human review in Task 2 is the part a green suite cannot supply. Nine routes,
eight degraded sentences, twelve help entries, seven mode layers with their
controllers, one locked refusal card, a first-run walkthrough, and a sample
course a learner meets before anything else are all things a test can prove
present and cannot prove legible or honest.
`PLANNING-DIRECTIVES.md` section 3a requires every accepted recommendation to
name its owner, its verification, its evidence class, and its failure condition,
and an agent never signs that for itself.

Decisions already made, cited, and never re-derived here:

- **`16B-DECISIONS.md`**, every heading from `## D1` through `## D-16B-12`, read
  in full before Task 1. This plan resolves no design question.
- **`16B-PRECONDITION.md`, the Additivity baseline section**, which is
  re-verified one final time.
- **`ROADMAP.md`'s Phase 16B freeze gate**, quoted above in full.
- **`ROADMAP.md`'s Phase 16B "Prototype-before-freeze coupling"**, quoted: the
  16B freeze "covers the loop storyboards, IA routes and anchors, resume
  semantics, the job and approval surface, the mode-layer contract, and the
  offline, help, and error states only" and is "explicitly not a visual system
  or token freeze (17A), not a notes, learner-artifact, or strategy freeze
  (16C), not a course schema freeze (14B), and not a semantic lesson capability
  freeze (16A)".
- **`16B-UI-SPEC.md`'s "Open Items Deferred to Other Phases" table**, all six
  rows, which the freeze record carries forward.

Purpose: prove the whole contract at once, in one run, and let a human judge it.
Output: one measured tracer report, one signed review, and one freeze record or
one named withholding.
</objective>

<context>
@.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-VALIDATION.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/PLANNING-DIRECTIVES.md
@surfaces/ia.py
@surfaces/daemon.py
@sample_course.py
</context>

## Artifacts this phase produces (plan 16B-11 share)

New symbols introduced by this plan: none. No module, no route, no CLI command,
no schema key, and no fixture is produced by this plan. No change is made to
`surfaces/ia.py`, `surfaces/daemon.py`, `surfaces/cli.py`,
`schemas/settings.schema.json`, `sample_course.py`, `runtime.py`, `model.py`, or
`evidence.py`; if the review in Task 2 finds a defect, the fix is a new plan and
not a task here.

The planning artifacts this plan creates are `16B-TRACER-REPORT.md`,
`16B-REVIEW.md`, and `16B-FREEZE.md`, plus the `## D-16B-13` heading in
`16B-DECISIONS.md` and the completed `16B-VALIDATION.md`.

The phase-wide symbol union is repeated in `16B-01-PLAN.md`.

<tasks>

<task type="auto">
  <name>Task 1: run all five freeze-gate fixtures in one pass and measure it</name>
  <files>.planning/phases/16B-ia-modes-recovery-contract/16B-TRACER-REPORT.md</files>
  <read_first>
- `.planning/ROADMAP.md`, the Phase 16B freeze-gate paragraph in full. Its five
  fixtures are this task's checklist.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md`, the
  Additivity baseline section, all four recorded lines.
- Every 16B summary that exists, `16B-02-SUMMARY.md` through
  `16B-10-SUMMARY.md`, specifically each one's recorded deviations and any stage
  marked `SKIPPED` or any branch a plan required to be recorded.
- `tests/ia_route_roundtrip.py`, `tests/ia_storyboard_tracer.py`,
  `tests/mode_layer_roundtrip.py`, and `tests/degraded_state_roundtrip.py`, each
  one's `main()` and its printed summary line, so the report quotes real final
  lines.
  </read_first>
  <action>
1. Run every suite this phase created plus the two shipped suites it extends,
   timing each with `time.monotonic()` around the subprocess call, and record
   each command's final line verbatim:

```
python tests/ia_route_roundtrip.py
python tests/ia_storyboard_tracer.py
python tests/mode_layer_roundtrip.py
python tests/degraded_state_roundtrip.py
python tests/daemon_roundtrip.py
python tests/config_roundtrip.py
python tests/theme_roundtrip.py
```

   Then the full suite and the guard:

```
for t in tests/*.py; do python "$t" || exit 1; done
python itembank.py guard .
git status --porcelain
```

   Expected: exit 0 from every command, `0 offending files` from the guard, and
   `git status --porcelain` listing no `_sample_course` or `_ia` entry.

2. Re-verify the settings additivity baseline one final time. Recompute the
   effective settings document, drop the four keys plan 16B-06 added, and
   compare its key count and its sorted-JSON SHA-256 against the values recorded
   in `16B-PRECONDITION.md`. Record both sides side by side.

3. Record the published route surface as measured rather than as claimed:

```
python -c "import sys; sys.path.insert(0,'.'); from surfaces import daemon, ia; print(len(daemon.ROUTES), len(daemon.API_ROUTES), len(daemon.SURFACE_PARITY), len(daemon.ROUTE_CLI)); print(len(ia.IA_HELP_CODES), len(ia.DEGRADED_STATES), len(ia.MODE_LAYERS), len(ia.COURSE_AREAS), len(ia.SHELF_ACTIONS), sum(len(v['steps']) for v in ia.LOOP_STEPS.values()))"
```

   Record both printed lines verbatim.

4. Write
   `.planning/phases/16B-ia-modes-recovery-contract/16B-TRACER-REPORT.md`. Every
   figure in it is measured during this run, and the report names the machine's
   operating system and the Python version that produced them. Sections, in this
   order:

   - **What was run.** Every command above, verbatim, with its final line.
   - **The five freeze-gate fixtures.** One row per fixture from `ROADMAP.md`'s
     paragraph, each marked `passed`, `weaker proof`, or `not run`, with the
     scenario or check that covered it named by function name. A fixture marked
     anything but `passed` carries one sentence saying what was not exercised.
     The five rows are: FLOW-01 loop interruption storyboard; FLOW-02
     model-disabled walk; APP-01 two-course shelf with one corrupted course;
     APP-02 deep-link replay across both layouts; APP-03 first-launch
     interruption with no roots, no agent, and no network.
   - **Measured figures.** The wall-clock duration of each of the seven suite
     commands and of the full suite; the four route-structure counts; the six
     vocabulary counts and the loop step total; the number of files
     `write_sample_course` wrote and their total byte count. No figure appears
     that was not produced by this run, and no budget or target number appears
     at all.
   - **Additivity evidence.** The settings baseline key count and SHA-256 from
     `16B-PRECONDITION.md` beside the values found now.
   - **Open findings.** Every open item, including: every stage plan 16B-10's
     walk marked `SKIPPED` and its naming sentence; every deviation any 16B
     summary recorded, quoted; the APP-02 unresolved probe row and how it was
     enumerated; every backstop marker carried by plans 02 through 10, listed
     with its owning plan; and every deferral this phase made by name, which is
     at minimum: no Activity write path (`D-16B-8`), no enforcement of the four
     new settings keys (plan 16B-06), no live-state mode-layer collector
     (`D8`, `D-16B-12`), no real course-area content (plan 16B-05), no producer
     for six of the eight degraded states (plan 16B-08), Notes (`D4`), and
     Search (`D5`).

   No em dash characters anywhere in the file.
  </action>
  <verify>
  <automated>for t in tests/*.py; do python "$t" || exit 1; done</automated>
Expected: exit 0. Then `python itembank.py guard .` reports `0 offending files`
and `git status --porcelain` lists no `_sample_course` or `_ia` entry. The
degraded state this task must prove rather than paper over is a red or skipped
leg: a fixture that could not be exercised is marked `weaker proof` or `not run`
with a naming sentence, and Task 3's freeze decision weighs it.
  </verify>
  <acceptance_criteria>
- Every one of the seven suite commands exits 0 and its final line is quoted
  verbatim in the report.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` reports `0 offending files`.
- `git status --porcelain` lists no `_sample_course` or `_ia` entry.
- The settings baseline key count and SHA-256 match the values recorded in
  `16B-PRECONDITION.md` for every pre-existing key.
- `16B-TRACER-REPORT.md` exists with all five named sections; its five-fixture
  table has exactly five rows, each naming the covering function; every figure
  in Measured figures is a measured one and no target or budget number appears.
- The Open findings section lists every backstop marker from plans 02 through 10
  with its owning plan, and every deferral named in step 4.
- `16B-TRACER-REPORT.md` contains no em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">A report. It records a run and changes
  nothing in the codebase.</reversibility>
  <done>The whole contract runs in one pass, every figure in the report was
  measured, and every leg that was not fully exercised says so.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: the contract-legibility review a human signs</name>
  <files>.planning/phases/16B-ia-modes-recovery-contract/16B-REVIEW.md</files>
  <read_first>
- `.planning/phases/16B-ia-modes-recovery-contract/16B-TRACER-REPORT.md` as
  written by Task 1, in full.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md` in full,
  every heading.
- `.planning/ROADMAP.md`, the Phase 16B goal paragraph and freeze-gate
  paragraph.
- `.planning/REQUIREMENTS.md`, the five Fixture sentences for FLOW-01, FLOW-02,
  APP-01, APP-02, and APP-03, verbatim.
- `.planning/PLANNING-DIRECTIVES.md` section 3a, the accepted-recommendation
  discipline paragraph.
- `surfaces/ia.py`'s copy tables read as prose rather than as code:
  `ACTIVITY_COPY`, `ATTENTION_COPY`, `HELP_TABLE`, `DEGRADED_COPY`,
  `WALKTHROUGH_COPY`, `SAMPLE_COURSE_COPY`, `LOOP_EMPTY_OUTCOME`, and the two
  locked-card templates.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-REVIEW.md` and
  `.planning/phases/16A-semantic-capability-activity-contract/16A-REVIEW.md`
  if either exists, as the precedent shape for a human review artifact.
  </read_first>
  <what-built>
Plans 16B-02 through 16B-10 built the information architecture, mode, and
recovery contract, and plan 16B-11 Task 1 walked it: a course shelf with exact
resume cues and six attention states, degrading to the shipped bank listing when
no course exists and to a last-valid-overview card when a record cannot be read;
nine course-level areas behind four new route patterns with opaque identifiers,
explicit back semantics, anchor targets, and one route per object at every
width; an Activity view that is a read model over the journal with eight job
states, no write path, and no invented percent; twelve named error codes each
routing to an offline help page with a cause and a next safe action, with no
networking module reachable from the module that serves them; four additive
settings groups whose defaults are all restrictive and whose panel says out loud
that nothing enforces them yet; the seven-layer mode contract as data, with the
two fixed layers rendered read-only and a conflict resolving upward with one
locked sentence; eight degraded-state banners each carrying a code, a help link,
and a next action, with the one path-bearing banner reduced to a basename; a
locked refusal card that states its unlock condition and carries none of the
content it withholds; a bundled synthetic sample course and a skippable,
replayable walkthrough reachable with no root granted, no agent configured, and
no network; and seven enumerated loops that resume at any step boundary from a
record read off disk. The suites are green and the measured figures are in
`16B-TRACER-REPORT.md`.

What none of that can decide is whether the contract is legible and honest. A
green test proves a string is present and a route resolves. It cannot tell you
that a degraded sentence explains what actually happened to the person reading
it; that a next safe action is a thing a learner could really do next; that
"Needs reconciliation" means anything to someone who has not read the roadmap;
that the locked refusal card reads as a rule rather than as a brush-off; or that
a first-run walkthrough would actually orient a new learner rather than describe
the product to itself. That judgment is the freeze gate's actual subject.
  </what-built>
  <how-to-verify>
1. Read
   `.planning/phases/16B-ia-modes-recovery-contract/16B-TRACER-REPORT.md` end to
   end, and note every row in its five-fixture table that is not `passed` and
   every item in its Open findings section.

2. Run the four new suites yourself and watch them:

```
python tests/ia_route_roundtrip.py
python tests/ia_storyboard_tracer.py
python tests/mode_layer_roundtrip.py
python tests/degraded_state_roundtrip.py
```

   Expected: exit 0 from all four, with the summary lines the report quotes.

3. Start a daemon over an empty directory and use it as a new learner would:

```
python itembank.py daemon <an empty temp directory>
```

   Then answer in `16B-REVIEW.md`:
   - Does the first screen tell you what to do next, or does it describe itself?
   - Is it obvious that the sample course is a sample, without reading closely?
   - Would you take the walkthrough, and did its four steps tell you anything
     you would not have worked out?
   - Could you find the sample course's remove control, and did the confirmation
     tell you what would actually happen?

4. Read the eight degraded sentences in `ia.DEGRADED_COPY` as a learner. For
   each, answer:
   - Does it say what happened in words you would use?
   - Does the next safe action name something you could actually do right now?
   - Is there any sentence that would make you think you had lost work when you
     had not, or that you had not when you had?

5. Read the twelve help entries in `ia.HELP_TABLE` as prose. For each, answer:
   - Does the cause explain the situation or restate the error name?
   - Is the next action specific enough to follow?
   - Is there a code whose page you would close no better off than before?

6. Read the six attention chips in `ia.ATTENTION_COPY`. Would you know, seeing
   one on a course card, what it wants from you? Is `Needs reconciliation`
   meaningful, and if not, what would you call it?

7. Read the seven mode layers with their controllers, and the conflict sentence
   `Timed test mode is set by your instructor's policy and can't be changed
   here.` Answer:
   - Does the sentence read as an explanation or as a refusal?
   - Looking at the settings page, is it clear which two layers are fixed and
     why?

8. Read the locked refusal card, rendered from
   `ia.locked_refusal_card("Second hint tier", "you submit an attempt on this
   item")`. Answer:
   - Does it read as a rule you understand, or as a wall?
   - Would you try to argue with it, and is there anything on it that invites
     that?

9. Read the seven `LOOP_EMPTY_OUTCOME` sentences. Would each one tell you that
   something ran and produced nothing, rather than that something broke?

10. Look at the Open findings section's backstop list. For each, state whether
    you accept it as an honest unknown carried forward, or whether any one of
    them should withhold the freeze.

11. Record your verdict in
    `.planning/phases/16B-ia-modes-recovery-contract/16B-REVIEW.md` as one of
    the literal words `accept`, `accept-with-findings`, or `reject`, followed by
    your answers above, followed by your name or initials and the date.
    `accept-with-findings` means the freeze may be written and the findings are
    carried into the freeze record's open-items list.

    No em dash characters anywhere in the file.
  </how-to-verify>
  <verify>
`16B-REVIEW.md` exists, carries one of the three literal verdict words, carries
answers to all of steps 3 through 10, and carries a signature and a date.
  </verify>
  <acceptance_criteria>
- `.planning/phases/16B-ia-modes-recovery-contract/16B-REVIEW.md` exists.
- It contains exactly one of the literal strings `accept`,
  `accept-with-findings`, or `reject` as its recorded verdict.
- It contains a named response for each of the eight degraded sentences, each of
  the twelve help entries, and each of the six attention chips.
- It contains a response for the seven mode layers, the conflict sentence, the
  locked refusal card, the seven empty-outcome sentences, and the first-run
  walkthrough.
- It contains a per-item judgment on the backstop list from the tracer report's
  Open findings section.
- It carries a signature or initials and a date.
- It contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="reversible">A review artifact. It records a judgment and
  changes nothing in the codebase.</reversibility>
  <resume-signal>Write `16B-REVIEW.md` with your verdict, then reply `accept`, `accept-with-findings`, or `reject`.</resume-signal>
</task>

<task type="auto">
  <name>Task 3: write the freeze record, or withhold it by name</name>
  <files>.planning/phases/16B-ia-modes-recovery-contract/16B-FREEZE.md, .planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md, .planning/phases/16B-ia-modes-recovery-contract/16B-VALIDATION.md</files>
  <read_first>
- `.planning/phases/16B-ia-modes-recovery-contract/16B-REVIEW.md` as written by
  Task 2, in full, including its verdict word.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-TRACER-REPORT.md` in
  full, including its five-fixture table and its Open findings section.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md` in full,
  every heading, for the decision list the freeze record enumerates.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md`, the
  Deviations found section.
- `.planning/ROADMAP.md`, the Phase 16B entry and the Phase 14A, 14B, 16A, 16C,
  and 17A entries, so the freeze record's scope statement says what it does not
  freeze.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-FREEZE.md` and
  `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md`, for the
  established freeze-record shape and the exact heading conventions
  `## Frozen at <phase>` and `## Freeze withheld`.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-VALIDATION.md` in full.
  </read_first>
  <action>
1. Re-run the evidence rather than trusting Task 1's record, because Task 2's
   review may have prompted a fix and a freeze record must describe the tree it
   is freezing:

```
python tests/ia_route_roundtrip.py
python tests/ia_storyboard_tracer.py
python tests/mode_layer_roundtrip.py
python tests/degraded_state_roundtrip.py
python itembank.py guard .
for t in tests/*.py; do python "$t" || exit 1; done
```

   Then re-verify the settings additivity baseline against
   `16B-PRECONDITION.md` one final time.

2. Evaluate the six freeze legs. The freeze is written only when all six hold:
   - All four new 16B suites are green with zero failures.
   - The full suite is green and `guard` reports `0 offending files`.
   - The settings additivity baseline is unchanged for every pre-existing key.
   - `16B-REVIEW.md` exists, is signed, and its verdict is `accept` or
     `accept-with-findings`. A `reject` verdict or a missing signature is a
     failing leg.
   - `16B-PRECONDITION.md`'s Deviations found section is either `none` or every
     deviation it records has a recorded resolution in a 16B summary. An
     unresolved precondition divergence is a failing leg, because plans 02
     through 10 were written against a surface that turned out to differ.
   - Every stage plan 16B-10's walk marked `SKIPPED` carries an explicit
     recorded judgment in `16B-REVIEW.md` or in this task's own record. A
     skipped stage with no judgment is a failing leg; a skipped stage a human
     accepted is an open item, not a withholding.

3. If every leg holds, write
   `.planning/phases/16B-ia-modes-recovery-contract/16B-FREEZE.md` opening with
   the literal heading `## Frozen at 16B` and carrying, in this order:

   - **What is frozen.** The complete published surface, enumerated:
     the six new route patterns and their exact literals and regexes
     (`/activity`, `/help/<code>`, `/course/<course_id>`,
     `/course/<course_id>/<area>`, `/course/<course_id>/learn/<lesson_id>`,
     `POST /api/shelf`) with their `ROUTE_CLI` twins and the one new
     `SURFACE_PARITY` row; the three new CLI commands `activity`, `help-code`,
     and `shelf`; the course-shelf branch inside `handle_index` and the
     unchanged `("GET", "/")` literal and its `daemon` twin; the four new
     settings top-level keys with their defaults and their `x-itembank-phase`
     marker, and the unchanged `required` array; every closed vocabulary on
     `surfaces/ia.py` by name with its member count (`IA_HELP_CODES`,
     `ACTIVITY_JOB_STATES`, `DEGRADED_STATES`, `ATTENTION_STATES`,
     `ATTENTION_ORDER`, `MODE_LAYERS`, `MODE_LAYERS_FIXED`, `COURSE_AREAS`,
     `SHELF_ACTIONS`, `LOOP_ORDER`, `LOOP_STEPS`); every locked copy constant by
     name; the two `_ia/*.json` state file names and their atomic write
     contract; `sample_course.SAMPLE_COURSE_ID` and `SAMPLE_COURSE_NAME`; and
     `sample_course.SAMPLE_COURSE_DIRNAME` with its `.gitignore` and `cmd_guard`
     entries. Then, as document-level contract rather than code, name
     `16B-UI-SPEC.md` itself as frozen for its Typography voice-assignment
     table, its Color semantic-token assignment table, its Copywriting Contract,
     its Degraded-State Matrix, its Activity Contract, its Core Loop Resume
     Contract, its Mode-Layer Precedence Contract, its route contract, and its
     Decisions log D1 through D9, since Phase 17A renders against those
     assignments and no plan emits a voice class or a token value.
   - **What is NOT frozen.** Stated explicitly, following the ROADMAP's
     prototype-before-freeze coupling clause: this is not a visual system or
     token freeze (Phase 17A), not a notes, learner-artifact, or strategy freeze
     (Phase 16C), not a course schema freeze (Phase 14B), and not a semantic
     lesson capability freeze (Phase 16A). Name each phase as the owner. Add the
     six rows of `16B-UI-SPEC.md`'s "Open Items Deferred to Other Phases" table
     verbatim.
   - **Evidence.** The four new suites' final lines verbatim, the full-suite
     result, the guard result, the settings additivity comparison, the four
     route-structure counts, and the review's verdict and signature.
   - **Open items, with owners.** Every item from `16B-TRACER-REPORT.md`'s Open
     findings section plus every finding the review recorded, each with a named
     owner and, where known, the phase that would close it. This list must
     include, by name: no Activity write path, deferred per `D-16B-8`; no
     enforcement of `approved_roots`, `network_egress`, `accessibility`, or
     `storage`, deferred per plan 16B-06; no live-state mode-layer collector,
     deferred per `D8` and `D-16B-12`; no real course-area content, deferred to
     Phase 14A and 14B execution; no producer for six of the eight degraded
     states; Notes deferred per `D4`; Search deferred per `D5`; the ROADMAP goal
     clause "hosted, local, and manual continuation share durable checkpoints
     under the one operation protocol", which 16B satisfies only as the read
     side, because `RELIABILITY-02` and `AGENT-01/02/03` own the protocol itself
     and are Phase 15A's and 15B's, recorded here so a reader does not mistake
     the display contract for the protocol; the APP-02 unresolved probe row and
     its three enumerated scenarios; and every backstop marker carried by plans
     02 through 10, each with its owning plan.

4. If any leg fails, write the same file opening instead with the literal
   heading `## Freeze withheld`, naming the failing leg or legs, what would
   close each, and stating that Phase 16B stays open. The string
   `Frozen at 16B` must appear nowhere in the file in that case, so a downstream
   precondition check cannot read a withholding as a freeze.

5. Append `## D-16B-13. Freeze scope` to `16B-DECISIONS.md`, recording in one
   paragraph what the freeze covers and what it explicitly does not, matching
   the freeze record's own two sections, so a later phase reading only the
   decisions file gets the same answer.

6. Finalize
   `.planning/phases/16B-ia-modes-recovery-contract/16B-VALIDATION.md`:
   - Complete the Per-Task Verification Map's Status column, confirming a row
     exists for every task in plans 16B-02 through 16B-11 and that every Status
     is filled with one of the four status marks.
   - Replace the Estimated runtime placeholder in the Test Infrastructure table
     with the measured full-suite figure from `16B-TRACER-REPORT.md`, and name
     the machine and Python version it was measured on.
   - Fill the Manual-Only Verifications table's Test Instructions cell with the
     steps from this plan's Task 2.
   - Resolve every Validation Sign-Off checkbox honestly. Set
     `nyquist_compliant: true` in the frontmatter only if every task in the
     phase has an automated verify or a recorded Wave 0 dependency, and set
     `status: validated` and `wave_0_complete: true` only if that is true. Leave
     any box unticked whose condition does not hold and say why beside it.

   No em dash characters anywhere in any file this task writes.
  </action>
  <verify>
  <automated>python -c "import sys,io; p='.planning/phases/16B-ia-modes-recovery-contract/16B-FREEZE.md'; s=io.open(p,encoding='utf-8').read(); frozen='## Frozen at 16B' in s; withheld='## Freeze withheld' in s; assert frozen != withheld, 'freeze record must carry exactly one of the two headings'; assert not (withheld and 'Frozen at 16B' in s), 'a withholding must not contain the frozen string'; print('freeze record shape ok:', 'frozen' if frozen else 'withheld')"</automated>
Expected: prints `freeze record shape ok: frozen` or
`freeze record shape ok: withheld` and exits 0. The degraded state this task
must prove rather than paper over is the withholding path itself: the record
carries exactly one of the two headings, never both, and a withholding never
contains the string a downstream precondition check greps for.
  </verify>
  <acceptance_criteria>
- `.planning/phases/16B-ia-modes-recovery-contract/16B-FREEZE.md` exists and
  contains exactly one of `## Frozen at 16B` or `## Freeze withheld`.
- When it carries `## Freeze withheld`, the string `Frozen at 16B` appears
  nowhere in the file.
- When it carries `## Frozen at 16B`, it has all four named sections; its What
  is NOT frozen section names Phases 14B, 16A, 16C, and 17A as owners and
  carries all six UI-SPEC deferral rows; and its Open items section names at
  least the eight deferrals listed in step 3 plus every backstop marker with its
  owning plan.
- All four new 16B suites were re-run in this task and their final lines are
  quoted verbatim in the freeze record.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0 and
  `python itembank.py guard .` reports `0 offending files`.
- The settings additivity baseline is unchanged for every pre-existing key and
  is quoted in the freeze record.
- `16B-DECISIONS.md` contains the literal heading `## D-16B-13. Freeze scope`.
- `16B-VALIDATION.md` has no `(filled by planner)` placeholder remaining, its
  Estimated runtime cell carries a measured figure with a named machine and
  Python version, and its frontmatter `status`, `nyquist_compliant`, and
  `wave_0_complete` values match what the sign-off boxes actually show.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="one-way">A freeze record is what plan 16C-01's and
  17A-01's precondition checks will assert against, and what later phases build
  their routes, vocabularies, and copy on. Reopening a frozen surface after
  those phases plan against it means renaming or reshaping a published contract.
  The judgment it requires is the blocking human review in Task 2 immediately
  above it.</reversibility>
  <done>Phase 16B is either frozen with its surface enumerated, its evidence
  recorded, and its open items owned, or held open with the missing leg
  named.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| phase suites to shipped suites | A green phase suite could mask a regression in the shipped parser, renderer, scorer, or evidence store if it does not run those suites too. |
| freeze record to later phases | Whatever this file says is frozen is what plans 16C-01 and 17A-01 will assert against. |
| human review to freeze | A signature is the only thing standing between a green machine and an accepted claim about legibility. |
| backstop marker to verification | A marker with no evidence can be read as a pass by a downstream verification if nothing carries it forward. |
| runtime-materialized state to the repository | The sample course and the `_ia` records are written into whatever directory a suite points a daemon at. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16B-11-01 | Spoofing | an agent self-certifying the contract-legibility review | high | mitigate | The review is a blocking `checkpoint:human-verify` producing a signed file with one of three literal verdict words; Task 3 fails the review leg on a missing signature or a `reject` verdict and withholds the freeze by name. |
| T-16B-11-02 | Repudiation | a freeze record claiming a leg that was not run | high | mitigate | Task 3 re-runs all four new suites, the full suite, the guard, and the additivity comparison rather than trusting Task 1, and quotes their final lines verbatim; a failing leg produces a `## Freeze withheld` file in which the frozen string appears nowhere, asserted by the automated verify. |
| T-16B-11-03 | Tampering | a regression in the shipped runtime hidden behind green phase suites | high | mitigate | The full suite runs in both Task 1 and Task 3, and the settings additivity baseline recorded before any 16B change is re-verified in both. |
| T-16B-11-04 | Repudiation | a tracer report carrying budget numbers presented as measurements | medium | mitigate | The action forbids any figure that was not produced by the run, requires the machine and Python version be named, and the acceptance criteria assert no target or budget number appears. |
| T-16B-11-05 | Repudiation | a backstop marker silently upgraded to covered at freeze time | high | mitigate | Every backstop marker from plans 02 through 10 is listed in the tracer report's Open findings with its owning plan, carried into the freeze record's Open items, and given a per-item human judgment in the review. |
| T-16B-11-06 | Repudiation | a skipped walk stage disappearing between the tracer and the freeze | high | mitigate | Task 3 leg six requires an explicit recorded judgment per skipped stage and makes a judgment-free skip a failing leg. |
| T-16B-11-07 | Information Disclosure | runtime-materialized sample course or state files entering version control | medium | mitigate | `git status --porcelain` is asserted in Task 1 to list neither `_sample_course` nor `_ia`, and `guard` is asserted green in both tasks. |
| T-16B-11-08 | Elevation of Privilege | an unresolved precondition divergence frozen into a published contract | high | mitigate | Task 3 leg five reads `16B-PRECONDITION.md`'s Deviations found section and requires each recorded deviation to have a recorded resolution in a 16B summary; an unresolved one withholds the freeze by name. |
| T-16B-11-09 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; this plan runs shipped commands and writes markdown. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- Any change to `surfaces/ia.py`, `surfaces/daemon.py`, `surfaces/cli.py`,
  `surfaces/settings.py`, `surfaces/theme.py`, `schemas/settings.schema.json`,
  `sample_course.py`, `runtime.py`, `model.py`, or `evidence.py`. If the review
  or a fixture finds a defect, the fix is a new plan and the freeze is withheld,
  not a task added here.
- Any new route, vocabulary, copy constant, settings key, or state file. Every
  one of them was settled in plans 16B-01 through 16B-10.
- Any softened assertion to make a leg pass. A leg that cannot be exercised is
  marked `weaker proof` or `not run` and the freeze decision weighs it.
- Any visual decision. Phase 17A owns the token freeze and the same-flow
  three-direction comparison that must precede it.
- Freezing anything Phase 16C, 17A, 14A, or 14B owns. The freeze record's What
  is NOT frozen section states the boundary explicitly.
- Closing any of the deferred items. Every deferral is recorded with an owner,
  not resolved.
</out_of_scope>

<flagged_assumptions>
- **`accept-with-findings` permits the freeze.** The alternative reading, that
  any finding withholds it, would make the review a pass or fail gate and would
  push a reviewer toward `accept` to avoid blocking. Findings are carried into
  the freeze record's open-items list with owners, which is where
  `PLANNING-DIRECTIVES.md` section 3a's accepted-recommendation discipline
  expects them.

- **A skipped walk stage is not automatically a withholding leg.** It becomes
  one only if nobody judged it. This is a judgment this plan makes rather than
  one a requirement states, and the reason is recorded: a stage that cannot be
  exercised in this environment is information, and burying it is the failure,
  not the skip itself.

- **Whether `16B-PRECONDITION.md` records deviations is unknown at plan time.**
  Task 3 leg five reads it and requires each recorded deviation to have a
  recorded resolution in a 16B summary; if plan 16B-01's precondition halted,
  this plan never runs at all.

- **The backstop markers carried by plans 02 through 10 are the phase's honest
  unknowns**, covering loading and overflow rendering owed to Phase 17A,
  per-area empty and list behavior owed to Phase 14B record shapes, refusal
  payload shapes owed to the runtime, and multi-state and concurrency cases owed
  to producers this phase does not build. At verification time, no explicit
  evidence for a backstop row is `insufficient_spec` and needs a human, never a
  silent pass; the freeze record carrying them with owners is what makes that
  visible.
</flagged_assumptions>

<summary_obligations>
`16B-11-SUMMARY.md` records: the five freeze-gate fixtures and the result of
each, including any marked `weaker proof` or `not run` and why; the measured
figures from `16B-TRACER-REPORT.md`, repeated, with the machine and Python
version; the settings additivity comparison as re-verified one final time; the
four route-structure counts and the six vocabulary counts as measured; the
review's verdict, its signature, and every finding it recorded; every stage plan
16B-10 marked `SKIPPED` and the judgment recorded for it; whether the freeze was
written or withheld and, if withheld, the exact failing legs; the full open-items
list with owners as written into the freeze record; the final state of
`16B-VALIDATION.md`'s frontmatter flags and which sign-off boxes were left
unticked and why; which truth was verified by which command with its actual
stdout; and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16B-ia-modes-recovery-contract/16B-11-SUMMARY.md`
when done.
</output>
