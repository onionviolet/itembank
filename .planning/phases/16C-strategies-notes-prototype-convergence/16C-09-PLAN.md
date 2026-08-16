---
phase: 16C-strategies-notes-prototype-convergence
plan: 09
type: execute
wave: 6
depends_on: ["16C-04", "16C-05", "16C-08"]
files_modified:
  - tests/cross_subject_suite_tracer.py
  - .planning/phases/16C-strategies-notes-prototype-convergence/16C-TRACER-REPORT.md
  - .planning/phases/16C-strategies-notes-prototype-convergence/16C-REVIEW.md
  - .planning/phases/16C-strategies-notes-prototype-convergence/16C-FREEZE.md
  - .planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md
  - .planning/phases/16C-strategies-notes-prototype-convergence/16C-VALIDATION.md
autonomous: false
requirements: [GRAPH-03, NOTE-01, NOTE-02, NOTE-03, STRATEGY-01, STRATEGY-02, UPGRADE-01, UPGRADE-02]
estimate:
  tokens: 90000
  raw_tokens: 90000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "Every ROADMAP freeze-gate fixture runs in one pass over the four synthetic subjects and each is recorded as passed, weaker proof, or not run: the strategy fallback run, the conflict matrix, the invalidated anchor, the promotion pair, the pending artifact, the progress tuple set, the trio with its broken fixtures, and the two upgrade scenarios."
    - "Phase 13.9's A9 closure is checked by reading the 13.9 SUMMARY evidence directly, and the tracer halts by name if the walking skeleton has not been walked, because 16C's freeze is a 14B-or-later freeze."
    - "The tracer report measures rather than asserts: every duration, count, and figure in 16C-TRACER-REPORT.md was produced by the run on the machine and Python version the report names, and no budget or target number appears anywhere in it."
    - "The shipped runtime is unregressed: the full suite runs green, the evidence additivity baselines recorded in 16C-PRECONDITION.md still hold, and python itembank.py guard . reports 0 offending files."
    - "A human, not an agent, judges contract legibility in 16C-REVIEW.md with one of three literal verdicts, and no freeze record is written on a red suite, a missing or rejecting review, an unresolved precondition divergence, an open 13.9 closure, or a skipped prototype with no recorded judgment."
    - "The freeze record's scope statement transcribes the ROADMAP scope sentences verbatim, covering the seven named deliverables only and naming 17A, 16B, 16A, and 14B as the owners of what it does not freeze; a withheld freeze opens with the Freeze withheld heading and contains the frozen string nowhere."
  prohibitions:
    - statement: "An agent must not sign its own contract; whether the note, strategy, progress, trio, and upgrade copy is legible and honest to a learner is a human's judgment, and a green suite is not that judgment."
      status: kept
      verification: flagged-unverified
    - statement: "The freeze record must not claim a leg that was not run; a leg that could not be executed is named as withheld or as a weaker proof rather than described as satisfied or omitted."
      status: kept
      verification: flagged-unverified
    - statement: "A figure that was not measured must not appear in the tracer report; a budget, a target, or an estimate presented among measurements is a fabricated measurement."
      status: kept
      verification: flagged-unverified
    - statement: "No output mode beyond the trio and no fifth strategy may be registered by this plan; the freeze records the kill criterion and the runway, it does not spend them."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "tests/cross_subject_suite_tracer.py, the one-pass freeze-gate suite"
    - "16C-TRACER-REPORT.md with measured figures only"
    - "16C-REVIEW.md carrying one of three literal verdict words, a signature, and a date"
    - "16C-FREEZE.md opening with exactly one of two headings"
    - "16C-DECISIONS.md gains the dated D-16C-9 freeze-scope entry"
    - "16C-VALIDATION.md finalized: Status column complete, measured runtime, sign-off boxes resolved"
  key_links:
    - "Task 3 re-runs every suite rather than trusting Task 1's record, because the review may have prompted a fix and a freeze record must describe the tree it freezes."
    - "The freeze record's What is NOT frozen section is what plans 17A-01 and later read before planning against this surface; an omission there is how a later phase assumes a contract 16C never made."
    - "The tracer asserts notes.py's local strategy-id tuple equals strategies.STRATEGY_IDS, closing the deliberate duplication 16C-06 recorded."
    - "The D-12.6-5 checkpoint answer from 16C-01 Task 2 is carried into the freeze record's open items when it was anything but the recommended default, so 17A renders against the recorded choice."
---

<objective>
Run the phase's own freeze gate and either write the freeze or name the leg
that withheld it.

`ROADMAP.md`'s Phase 16C freeze gate names the fixtures: every registered
strategy against the four synthetic subjects with one marked unavailable
(STRATEGY-01); the conflict matrix extending 16B's fixture (STRATEGY-02);
the invalidated anchor keeping its objective (NOTE-01); the promotion pair
with one unreviewed note staying private (NOTE-02); the fictional proof
pending until a scripted review settles it (NOTE-03); the evidence set with
a missing denominator, a pending prose mark, and a version-split objective,
no aggregate anywhere (GRAPH-03); the trio from one parse with each
validator failing its broken fixture and each output degrading to plain
Markdown; the audited bounded-diff upgrade (UPGRADE-01); and the scripted
keyed-answer upgrade halting for assessment review (UPGRADE-02).

All of these were built by plans 16C-02 through 16C-08. This plan re-runs
them in one pass over the four subjects, measures the run, lets a human
judge what a test cannot (whether the copy is legible and honest), and then
either freezes or says why not. It also checks Phase 13.9's A9 closure
directly, because 16C's freeze is a 14B-or-later freeze and may not close
before the walking skeleton is walked.

Decisions already made, cited, and never re-derived here:

- **`16C-DECISIONS.md`**, every heading from `## D1` through `## D-16C-8`
  plus the D-12.6-5 record, read in full before Task 1. This plan resolves
  no design question.
- **`16C-PRECONDITION.md`, the Additivity baseline section**, re-verified
  one final time.
- **`ROADMAP.md`'s Phase 16C freeze gate and "Prototype-before-freeze
  coupling" paragraphs**, whose scope sentences the freeze record
  transcribes verbatim.
- **STYLE-DISCIPLINE-16A-2026-08-14.md**: the remaining seven modes and
  genre styles register only after the trio passes, one validator and one
  representative fixture each; the freeze records this runway.
- **Report 12 section 10.4's kill criterion** (via 16C-DECISIONS D-16C-4):
  a mode requiring a second parser, scorer, note truth, or UI state machine
  is killed; written into the freeze record.

Purpose: prove the whole contract at once, in one run, and let a human
judge it.
Output: one measured tracer report, one signed review, and one freeze
record or one named withholding.
</objective>

<context>
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-PRECONDITION.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-UI-SPEC.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-RESEARCH.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-VALIDATION.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/PLANNING-DIRECTIVES.md
@notes.py
@strategies.py
@progress_claims.py
@note_outputs.py
@upgrade_audit.py
@fixtures/note_strategy_corpus.py
</context>

## Artifacts this phase produces (plan 16C-09 share)

New symbols introduced by this plan: `tests/cross_subject_suite_tracer.py`
and its `scenario_*` functions. No module, vocabulary, schema, or fixture
changes. No change is made to `notes.py`, `strategies.py`,
`progress_claims.py`, `note_outputs.py`, `upgrade_audit.py`,
`evidence.py`, `model.py`, or `surfaces/cli.py`; if the review finds a
defect, the fix is a new plan and not a task here.

The planning artifacts this plan creates are `16C-TRACER-REPORT.md`,
`16C-REVIEW.md`, and `16C-FREEZE.md`, plus the `## D-16C-9` heading in
`16C-DECISIONS.md` and the completed `16C-VALIDATION.md`.

<tasks>

<task type="auto">
  <name>Task 1: the cross-subject suite in one measured pass</name>
  <files>tests/cross_subject_suite_tracer.py, .planning/phases/16C-strategies-notes-prototype-convergence/16C-TRACER-REPORT.md</files>
  <read_first>
- `ROADMAP.md`, the Phase 16C freeze-gate paragraph in full: its fixture
  list is this tracer's checklist.
- `16C-PRECONDITION.md`, the Additivity baseline section, all five lines.
- Every 16C summary that exists, `16C-02-SUMMARY.md` through
  `16C-08-SUMMARY.md`, specifically recorded deviations.
- The seven 16C test files, each one's `main()` and printed summary line,
  so the report quotes real final lines.
- `.planning/phases/13.9-walking-skeleton/` directory contents, for the A9
  closure evidence.
  </read_first>
  <action>
1. Create `tests/cross_subject_suite_tracer.py` in the shipped
   direct-execution shape with a local `fail(msg)`. It builds all four
   subjects via `note_strategy_corpus.build_all` into one temp directory
   and drives, over every subject in one process:
   - `scenario_strategy_fallback` (STRATEGY-01): for each subject, resolve
     each of the four strategies with `worked_reasoning` marked unavailable
     and assert it alone falls back to `continuous_reading` while the
     others resolve to themselves; assert the picker's fallback row carries
     the exact unavailable sentence and preselects continuous reading.
   - `scenario_conflict_matrix` (STRATEGY-02): run `composed_resolve` over
     the 16C-05 matrix per subject and assert every conflict sentence
     equals `ia.mode_layer_conflict_copy`'s output; assert the mid-sitting
     lock; then run `python tests/mode_layer_roundtrip.py` as a subprocess
     and assert exit 0, so the extended 16B fixture runs beside the 16C
     one.
   - `scenario_note_anchor` (NOTE-01): per subject, anchor notes, run
     `revise_lesson`, and assert the invalidated note keeps its
     objective_ids with a non-resolved relocation state.
   - `scenario_promotion_pair` (NOTE-02): per subject, promote one sourced
     note to `applied` and assert the second unreviewed note stays private
     with zero derived artifacts and zero evidence references.
   - `scenario_pending_artifact` (NOTE-03): the fictional proof reads
     pending, a model marker raises, a scripted human mark settles it.
   - `scenario_progress_tuple` (GRAPH-03): build the full claim scenario
     over a temp evidence log that includes real appended
     `activity_completed` and `activity_skipped` events (via
     `notes.strategy_lifecycle_event`), render, and assert the no-percent
     and no-aggregate scans plus the three degraded sentences.
   - `scenario_trio` : re-run the parse-once proof, the three broken
     fixtures with their exact refusal sentences, and prototype gates A, B,
     and C by importing and calling the `scenario_*` functions from
     `tests/note_trio_roundtrip.py`.
   - `scenario_upgrade`: the audit-first bounded diff and the keyed halt
     over the legacy fixture, asserting untouched bytes.
   - `scenario_registry_consistency`: assert notes.py's local strategy-id
     validation tuple equals `strategies.STRATEGY_IDS` (closing 16C-06's
     recorded duplication), and that `evidence.KNOWN_EVENT_TYPES` has
     exactly sixteen members.
   - `main()` times the whole pass with `time.monotonic()`, prints one line
     per scenario with `passed`, and a final line
     `CROSS-SUBJECT SUITE: 9 passed, 0 failed` plus
     `elapsed: <seconds>s`, exiting 0 only when every scenario passed.

2. Check Phase 13.9's A9 closure directly. Confirm
   `.planning/phases/13.9-walking-skeleton/13.9-03-SUMMARY.md` exists. If
   it does not, STOP: print exactly
   `HALT 16C-09 freeze gate: Phase 13.9 has not been walked (13.9-03-SUMMARY.md missing); the 16C freeze is a 14B-or-later freeze and may not close before the walking skeleton is walked.`
   and write `16C-TRACER-REPORT.md` with only its What was run section and
   this halt recorded; do not proceed to Task 2.

3. Run every suite this phase created plus the shipped regression net,
   timing each subprocess, recording each final line verbatim:

```
python tests/cross_subject_suite_tracer.py
python tests/note_schema_roundtrip.py
python tests/strategy_registry_roundtrip.py
python tests/progress_claim_roundtrip.py
python tests/strategy_precedence_roundtrip.py
python tests/mode_layer_roundtrip.py
python tests/note_promotion_roundtrip.py
python tests/note_trio_roundtrip.py
python tests/legacy_upgrade_roundtrip.py
python tests/evidence_roundtrip.py
python tests/lesson_roundtrip.py
```

   Then the full suite and the guard:

```
for t in tests/*.py; do python "$t" || exit 1; done
python itembank.py guard .
git status --porcelain
```

   Expected: exit 0 from every command, `0 offending files`, and
   `git status --porcelain` listing no generated bank, note document, or
   evidence file.

4. Re-verify the evidence additivity baselines one final time with the two
   commands from 16C-01 step 10 and record both sides beside the
   `16C-PRECONDITION.md` values.

5. Write `16C-TRACER-REPORT.md`. Every figure is measured during this run,
   and the report names the operating system and Python version. Sections,
   in this order:
   - **What was run.** Every command above, verbatim, with its final line.
   - **The freeze-gate fixtures.** One row per ROADMAP fixture (the nine
     scenarios), each marked `passed`, `weaker proof`, or `not run`, naming
     the covering scenario function. Anything but `passed` carries one
     sentence saying what was not exercised.
   - **Measured figures.** Wall-clock duration of each suite and of the
     full pass; the corpus's item, heading, term, and relation counts per
     subject; the count of `KNOWN_EVENT_TYPES`; the count of lifecycle
     events the progress scenario appended. No budget or target number
     appears.
   - **Additivity evidence.** The five baseline lines beside the values
     found now.
   - **Open findings.** Every deviation any 16C summary recorded, quoted;
     every backstop row from `16C-UI-SPEC.md`'s UI Considerations table
     with its owner; every deferral by name, at minimum: pixel rendering
     and tokens (17A), component-ID anchors (14A seam per D-16C-7), real
     course-record layer states (14B seam per 16C-05), the remaining seven
     output modes and genre styles (post-trio runway), the D-12.6-5 answer
     if it was not the recommended default, and the empty-copy locked-row
     interim 16C-03 recorded with 16C-05 as its closure.

   No em dash characters anywhere in the file.
  </action>
  <verify>
  <automated>python tests/cross_subject_suite_tracer.py && python itembank.py guard .</automated>
Expected: final line `CROSS-SUBJECT SUITE: 9 passed, 0 failed` with a
measured elapsed line, exit 0, then `0 offending files`. The degraded state
this task must prove rather than paper over is the halt path: a missing
13.9 SUMMARY stops the freeze gate by name, and a red or skipped leg is
marked `weaker proof` or `not run` with a naming sentence for Task 3 to
weigh.
  </verify>
  <acceptance_criteria>
- The tracer runs all nine scenarios over all four subjects in one process
  and exits 0.
- The 13.9 closure check ran, with its evidence path named in the report.
- Every listed suite exits 0 and its final line is quoted verbatim.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0 and guard
  reports `0 offending files`.
- The additivity baselines match `16C-PRECONDITION.md`.
- `16C-TRACER-REPORT.md` has all five named sections, a nine-row fixture
  table, measured figures only, and the open-findings list.
- No em dash character, verified with the `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">A tracer and a report; nothing durable
  changes.</reversibility>
  <done>The whole 16C contract runs in one measured pass over four
  subjects, or the missing leg is named.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: the contract-legibility review a human signs</name>
  <files>.planning/phases/16C-strategies-notes-prototype-convergence/16C-REVIEW.md</files>
  <read_first>
- `16C-TRACER-REPORT.md` as written by Task 1, in full.
- `16C-DECISIONS.md` in full, every heading.
- `REQUIREMENTS.md`, the eight Fixture sentences for this phase's
  requirements.
- The copy constants, read as prose: `notes.CAPTURE_COPY`,
  `notes.ANCHOR_STATE_LABELS`, `notes.PROMOTION_COPY`,
  `notes.ARTIFACT_COPY`, `notes.DELETE_COPY`, `strategies.STRATEGY_PURPOSES`,
  `strategies.UNAVAILABLE_COPY`, `strategies.MID_SITTING_LOCK_COPY`,
  `progress_claims`' copy constants, `note_outputs.VALIDATOR_FAILURE_COPY`,
  and `upgrade_audit`'s copy constants.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-REVIEW.md` if it
  exists, as the precedent shape.
  </read_first>
  <what-built>
Plans 16C-02 through 16C-08 built the notes, strategies, progress, trio,
and upgrade contracts, and Task 1 walked them over four synthetic subjects:
a note schema with four relocation states that never auto-applies a guess;
a promotion flow no note crosses without sources, no conflicts, and a human
reviewer; a learner artifact that stays pending until a human settles it; a
four-strategy registry whose absence degrades to continuous reading with a
stated sentence; a precedence collector over 16B's one function with the
locked conflict copy; a progress display that cannot render a percent or an
aggregate; three note outputs from one parse that refuse in their own words
and always leave plain Markdown standing; and an upgrade pipeline that
audits first, rejects cosmetic novelty, and halts on any keyed-meaning
change with no override.

What none of that can decide is whether the contract is legible and honest.
A green test proves a string is present. It cannot tell you that "Anchor
probably moved: review needed" would make you review rather than shrug;
that the promotion gates read as protection rather than bureaucracy; that
"Recorded as pending by itembank. A reviewer settles this. A model never
settles it." reads as reassurance rather than legalese; or that the
progress rows would tell you where you actually stand. That judgment is the
freeze gate's actual subject.
  </what-built>
  <how-to-verify>
1. Read `16C-TRACER-REPORT.md` end to end; note every fixture row that is
   not `passed` and every open finding.

2. Run the tracer yourself and watch it:

```
python tests/cross_subject_suite_tracer.py
```

   Expected: `CROSS-SUBJECT SUITE: 9 passed, 0 failed`, exit 0.

3. Read the capture panel copy (`notes.CAPTURE_COPY`) as a learner. Would
   you know what "This objective (no anchor)" does? Does the privacy line
   leave any doubt about who can see a note?

4. Read the four anchor-state labels and the two probable controls. Would
   "Anchor probably moved: review needed" get you to review? Is "Anchor
   lost. Still linked to {objective name}." reassuring or alarming?

5. Read the promotion copy: the source-check sentence with N substituted,
   the conflict stop, the accept confirmation, the declined badge. Does the
   flow read as protecting the course, or as refusing you? Would you know
   your note is unchanged after a decline?

6. Read the artifact copy: pending badge, explainer, proposal line, settled
   line. Does "A model never settles it." earn trust?

7. Read the four strategy purposes and the unavailable sentence. Would you
   pick correctly on the first read? Is the mid-sitting lock line an
   explanation or a wall?

8. Read a rendered progress block from the tracer's GRAPH-03 scenario (the
   report quotes one). Do seven separate rows tell you more or less than
   one bar would? Is "Indeterminate: {scope name} has no fixed
   denominator." acceptable English?

9. Read the three trio refusal sentences. Does each name something you
   could fix?

10. Read the upgrade halt sentence and its two affordances. Is it clear
    there is no override and why?

11. Judge each open finding in the report: accept it as an honest unknown
    carried forward, or name it as withholding the freeze.

12. Record your verdict in `16C-REVIEW.md` as one of the literal words
    `accept`, `accept-with-findings`, or `reject`, followed by your answers
    to steps 3 through 11, followed by your name or initials and the date.
    `accept-with-findings` means the freeze may be written and the findings
    are carried into the freeze record's open-items list.

    No em dash characters anywhere in the file.
  </how-to-verify>
  <verify>
`16C-REVIEW.md` exists, carries one of the three literal verdict words,
carries answers to steps 3 through 11, and carries a signature and a date.
  </verify>
  <acceptance_criteria>
- `16C-REVIEW.md` exists and contains exactly one of the literal strings
  `accept`, `accept-with-findings`, or `reject` as its recorded verdict.
- It contains a named response for the capture copy, the anchor states, the
  promotion flow, the artifact copy, the strategy purposes, the progress
  block, the trio refusals, and the upgrade halt.
- It contains a per-item judgment on the open-findings list.
- It carries a signature or initials and a date, and no em dash character.
  </acceptance_criteria>
  <reversibility rating="reversible">A review artifact recording a
  judgment.</reversibility>
  <resume-signal>Write `16C-REVIEW.md` with your verdict, then reply `accept`, `accept-with-findings`, or `reject`.</resume-signal>
</task>

<task type="auto">
  <name>Task 3: write the freeze record, or withhold it by name</name>
  <files>.planning/phases/16C-strategies-notes-prototype-convergence/16C-FREEZE.md, .planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md, .planning/phases/16C-strategies-notes-prototype-convergence/16C-VALIDATION.md</files>
  <read_first>
- `16C-REVIEW.md` as written by Task 2, including its verdict word.
- `16C-TRACER-REPORT.md` in full.
- `16C-PRECONDITION.md`, the Deviations found section.
- `ROADMAP.md`, the Phase 16C "Prototype-before-freeze coupling" paragraph,
  whose scope sentences step 3 transcribes verbatim.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-FREEZE.md`, the
  established freeze-record shape and heading conventions.
- `16C-VALIDATION.md` in full, including its Per-Task Verification Map.
  </read_first>
  <action>
1. Re-run the evidence rather than trusting Task 1's record:

```
python tests/cross_subject_suite_tracer.py
for t in tests/*.py; do python "$t" || exit 1; done
python itembank.py guard .
```

   Then re-verify the additivity baselines against `16C-PRECONDITION.md`
   one final time.

2. Evaluate the six freeze legs. The freeze is written only when all six
   hold:
   - The cross-subject tracer is green with zero failures.
   - The full suite is green and guard reports `0 offending files`.
   - The evidence additivity baselines are unchanged.
   - `16C-REVIEW.md` exists, is signed, and its verdict is `accept` or
     `accept-with-findings`; a `reject` or a missing signature is a
     failing leg.
   - `16C-PRECONDITION.md`'s Deviations found section is either `none` or
     every deviation has a recorded resolution in a 16C summary.
   - Phase 13.9's A9 closure held (Task 1's check), and every prototype
     (the trio and tracers A, B, C) either passed or carries an explicit
     recorded judgment in `16C-REVIEW.md`; a skipped prototype with no
     judgment is a failing leg.

3. If every leg holds, write `16C-FREEZE.md` opening with the literal
   heading `## Frozen at 16C` and carrying, in this order:
   - **What is frozen.** The published surface, enumerated: the note
     record's field set and its seven closed vocabularies by name with
     member counts; `schemas/note.schema.json`; the note document pair
     (`notes.md` plus `notes.md.json`) and its atomic write contract; the
     four relocation states with probable-never-auto-applied; the promotion
     outcome vocabulary (`blocked`, `conflict_stop`, `applied`, `refused`);
     the two additive event types and the closed nine-key lifecycle event;
     the four-strategy registry with its eleven contract keys and the
     code-owned fallback; `composed_resolve`'s explicit-layer-state
     signature; the nine-field claim tuple, the seven dimensions, and the
     fill-state contract; the trio's three modes, five validator codes, and
     refusal shape; the eleven-item baseline audit order and the
     keyed-halt contract; and every locked copy constant by module and
     name. Then, as document-level contract, name `16C-UI-SPEC.md` frozen
     for its Copywriting Contract, its semantic-token assignments, its
     voice assignments, and its Decisions log D1 through D16.
   - **What is NOT frozen.** Transcribe the ROADMAP scope sentences
     verbatim: "The 16C freeze covers the note and learner-artifact
     schemas, the promotion and review contract, the finite strategy
     registry, the composed precedence resolver, the progress comprehension
     display, the note-output trio, and the legacy-upgrade contract only.
     It is explicitly not a visual system or token freeze (17A), not an
     information architecture or navigation freeze (16B), not a semantic
     lesson capability freeze (16A), and not a course schema freeze (14B),
     and its freeze record says so." Name each phase as the owner of its
     unfrozen area.
   - **The runway and the kill criterion.** The remaining seven output
     modes and the genre styles register only after this freeze, one
     validator and one representative fixture each; a mode requiring a
     second parser, scorer, note truth, or UI state machine is killed
     (report 12 section 10.4 via D-16C-4).
   - **Evidence.** The tracer's final line verbatim, the full-suite result,
     the guard result, the additivity comparison, and the review's verdict
     and signature.
   - **Open items, with owners.** Every item from the tracer report's Open
     findings plus every review finding, each with a named owner, at
     minimum the deferrals Task 1 step 5 lists.

4. If any leg fails, write the same file opening instead with the literal
   heading `## Freeze withheld`, naming the failing leg or legs, what would
   close each, and stating that Phase 16C stays open. The string
   `Frozen at 16C` must appear nowhere in the file in that case.

5. Append `## D-16C-9. Freeze scope` to `16C-DECISIONS.md`, one dated
   paragraph matching the freeze record's two scope sections, so a later
   phase reading only the decisions file gets the same answer.

6. Finalize `16C-VALIDATION.md`:
   - Complete the Per-Task Verification Map's Status column: a row exists
     for every task in plans 16C-01 through 16C-09 and every Status is one
     of the four status marks.
   - Replace the Estimated runtime placeholder with the measured full-suite
     figure from the tracer report, naming the machine and Python version.
   - Resolve every Sign-Off checkbox honestly. Set `status: validated`,
     `nyquist_compliant: true`, and `wave_0_complete: true` in the
     frontmatter only if every condition actually holds; leave any box
     unticked whose condition does not hold and say why beside it.

   No em dash characters anywhere in any file this task writes.
  </action>
  <verify>
  <automated>python -c "import io; p = '.planning/phases/16C-strategies-notes-prototype-convergence/16C-FREEZE.md'; s = io.open(p, encoding='utf-8').read(); frozen = '## Frozen at 16C' in s; withheld = '## Freeze withheld' in s; assert frozen != withheld, 'freeze record must carry exactly one of the two headings'; assert not (withheld and 'Frozen at 16C' in s), 'a withholding must not contain the frozen string'; print('freeze record shape ok:', 'frozen' if frozen else 'withheld')"</automated>
Expected: prints `freeze record shape ok: frozen` or
`freeze record shape ok: withheld` and exits 0. The degraded state this
task must prove rather than paper over is the withholding path itself: the
record carries exactly one of the two headings, never both, and a
withholding never contains the string a downstream precondition check greps
for.
  </verify>
  <acceptance_criteria>
- `16C-FREEZE.md` exists and contains exactly one of `## Frozen at 16C` or
  `## Freeze withheld`.
- When frozen, its What is NOT frozen section carries the ROADMAP scope
  sentences verbatim and names 17A, 16B, 16A, and 14B as owners, and its
  runway section carries the kill criterion.
- The tracer and full suite were re-run in this task with their final lines
  quoted; guard reports `0 offending files`; the additivity baselines hold.
- `16C-DECISIONS.md` contains the literal heading `## D-16C-9. Freeze
  scope`.
- `16C-VALIDATION.md` has no pending placeholder remaining, a measured
  runtime with machine and Python version, and frontmatter flags matching
  its sign-off boxes.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="one-way">A freeze record is what Phase 17A's
  precondition check will assert against and what the output-mode long tail
  registers on top of. Reopening a frozen surface after later phases plan
  against it means reshaping a published contract. The judgment it requires
  is the blocking human review immediately above it.</reversibility>
  <done>Phase 16C is either frozen with its surface enumerated, its
  evidence recorded, and its open items owned, or held open with the
  missing leg named.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| phase suites to shipped suites | A green phase suite could mask a regression in the parser, scorer, or evidence store if the full suite did not run too. |
| freeze record to later phases | Whatever this file says is frozen is what 17A and the output-mode long tail assert against. |
| human review to freeze | A signature is the only thing between a green machine and an accepted claim about legibility. |
| 13.9 evidence to freeze eligibility | A frozen 16C over an unwalked skeleton would violate the ROADMAP's own ordering. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16C-09-01 | Spoofing | an agent self-certifying the contract-legibility review | high | mitigate | The review is a blocking checkpoint producing a signed file with one of three literal verdicts; Task 3 fails the leg on a missing signature or a reject and withholds by name. |
| T-16C-09-02 | Repudiation | a freeze record claiming a leg that was not run | high | mitigate | Task 3 re-runs the tracer, the full suite, the guard, and the additivity comparison rather than trusting Task 1, and the automated verify asserts the two-heading exclusivity. |
| T-16C-09-03 | Tampering | a regression hidden behind green phase suites | high | mitigate | The full suite runs in both Task 1 and Task 3, and the additivity baselines are re-verified in both. |
| T-16C-09-04 | Repudiation | budget numbers presented as measurements | medium | mitigate | The report forbids any figure the run did not produce and names the machine and Python version; acceptance asserts no target number appears. |
| T-16C-09-05 | Elevation of Privilege | freezing over an unwalked 13.9 or an unresolved precondition divergence | high | mitigate | Task 1 halts by name on missing 13.9 SUMMARY evidence; Task 3 leg five reads the Deviations section and requires recorded resolutions. |
| T-16C-09-06 | Information Disclosure | generated note or bank content entering version control during the tracer run | medium | mitigate | Every scenario writes only to temp directories; git status porcelain is asserted clean and guard runs in both tasks. |
| T-16C-09-07 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; this plan runs shipped commands and writes markdown. Per PLANNING-DIRECTIVES section 4a, any future dependency is vendored at a pinned version with a recorded checksum and a named license review. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- Any change to `notes.py`, `strategies.py`, `progress_claims.py`,
  `note_outputs.py`, `upgrade_audit.py`, `evidence.py`, `model.py`,
  `surfaces/cli.py`, or any fixture. If the review or a scenario finds a
  defect, the fix is a new plan and the freeze is withheld, not patched
  here.
- Any new output mode, strategy, vocabulary member, copy string, or event
  type.
- Any softened assertion to make a leg pass; a leg that cannot be exercised
  is marked `weaker proof` or `not run` and weighed.
- Any visual decision; 17A owns tokens, glyphs, and rendering.
- Freezing anything 14B, 16A, 16B, or 17A owns; the scope sentences are
  transcribed, not paraphrased.
- Closing any deferred item; every deferral is recorded with an owner.
</out_of_scope>

<flagged_assumptions>
- **`accept-with-findings` permits the freeze**, with findings carried into
  the open-items list with owners, the same reading 16B-11 recorded; the
  alternative would push a reviewer toward accept to avoid blocking.
- **Phase 13.9 execution is in flight at planning time** (Codex is
  executing it on this branch); the A9 check reads whatever SUMMARY
  evidence exists at execution time, which is exactly what the check is
  for. This plan touches no 13.9 file.
- **The tracer imports scenario functions from tests/note_trio_roundtrip.py
  rather than duplicating them**; if the landed functions are not
  importable (module-main guards aside), the fallback is a subprocess run
  asserting the suite's final line, recorded as a deviation.
</flagged_assumptions>

<summary_obligations>
`16C-09-SUMMARY.md` records: each freeze-gate fixture and its result,
including any marked `weaker proof` or `not run` and why; the measured
figures with machine and Python version; the additivity comparison as
re-verified; the 13.9 closure evidence path; the review's verdict,
signature, and every finding; whether the freeze was written or withheld
and, if withheld, the exact failing legs; the final state of
`16C-VALIDATION.md`'s frontmatter flags and any unticked box with its
reason; which truth was verified by which command with its actual stdout;
and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16C-strategies-notes-prototype-convergence/16C-09-SUMMARY.md`
when done.
</output>
