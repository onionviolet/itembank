---
phase: 16A-semantic-capability-activity-contract
plan: 09
type: execute
wave: 9
depends_on: ["16A-08"]
files_modified:
  - tests/assessment_authority_adversarial.py
  - fixtures/lesson_capability_corpus.py
  - tests/capability_stress_corpus_tracer.py
autonomous: true
requirements: [ACTIVITY-03]
estimate:
  tokens: 90000
  raw_tokens: 90000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "Three scripted attackers, an agent, a note, and an import, each attempt all four ACTIVITY-03 attacks, leak a key, invent a score, auto-grade prose, and edit a frozen sitting, and every one of the twelve attempts is refused by the real shipped gate rather than by a test double."
    - "The suite calls the real runtime.py and evidence.py functions and contains no class whose name begins with Mock and no function whose name begins with fake_; a grep for both patterns reports zero, because a stub that refuses proves nothing about whether the shipped gate refuses."
    - "runtime.public_item carries no key, no rationale, and no correct-answer field at three points, before any response exists, after one response exists, and after the sitting is complete, so the boundary is asserted on both sides and at the threshold rather than only in the easy pre-response case (ACTIVITY-03 boundary probe)."
    - "A short response's mark stays None, meaning pending, and is never coerced to False; evidence.mark_event coerces its verdict to bool only after the human-marker gate has already passed, so no rounding, coercion, or tie-break can manufacture a settled verdict out of a pending one (ACTIVITY-03 precision probe)."
    - "Phase 16A's own new grammar is attacked, not just the shipped surface: a source-excerpt callout quoting keyed rationale text, a media alt attribute carrying an answer, an activity static fallback carrying an answer, and a composed glossary built from a term runtime.glossable suppresses are each attempted, and each is either refused by the existing gate or is proven not to reach the learner before a response exists."
    - "No new leak detector is written: every disclosure question this phase's new grammar raises is answered by runtime.glossable and runtime.public_item, the gates that already exist, because a second leak detector would risk disagreeing with the first about what counts as keyed content."
    - "A frozen sitting stays frozen through both paths: submitting into a completed session is refused by name, and editing the session JSON directly does not change what a render reports, because a render is computed from the append-only evidence log and never from the session file."
  prohibitions:
    - statement: "No surface, agent, note, import, capability profile, activity declaration, media record, or output mode may leak a key, invent a score, auto-grade prose, or change a frozen sitting; the runtime alone scores, grants keyed disclosure, selects authoritative assessment behavior, and writes assessment evidence."
      status: kept
      verification: flagged-unverified
    - statement: "A model verdict must not become accepted evidence; an advisory grader may propose a mark and never settle one, and evidence.mark_event's refusal of any marker other than the literal string human is the structural expression of that."
      status: kept
      verification: flagged-unverified
    - statement: "The adversarial suite must not test a stub; a mock that refuses proves the mock refuses, and the whole value of this fixture is that the shipped code is the thing under attack."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "tests/assessment_authority_adversarial.py with attacker_agent, attacker_note, attacker_import, and twelve named attack_* functions"
    - "fixtures/lesson_capability_corpus.py gains build_adversarial_bank"
    - "tests/capability_stress_corpus_tracer.py gains scenario_assessment_authority"
  key_links:
    - "The suite must construct real sessions, real evidence logs, and real bank fixtures, which is more setup than a mock. That extra setup is the deliverable: 16A-RESEARCH.md's Pitfall 5 names a mocked gate as the failure mode, because a simplified stand-in for runtime.score_response or evidence.mark_event proves nothing about whether the actual shipped gates hold."
    - "The 16A-specific attacks in Task 3 are the ones that did not exist before this phase. The excerpt callout, the media alt, and the activity static fallback are three new places an author or an agent can put text that a learner sees before responding, and each is a new mouth for the same old leak. Attacking only the shipped surface would leave this phase's own additions untested."
    - "The glossary attack must go through runtime.glossable rather than through a new check. glossable is deliberately conservative and returns False on any ambiguity; a second detector written for composed glossaries would eventually disagree with it, and two gates that disagree about what is keyed content is worse than one gate that is occasionally too strict."
    - "The frozen-sitting attack has two halves because the two refusals are different in kind. The submit refusal is an active check that names the state; the JSON-edit refusal is structural, because D-11 made the session file stop being an input to its own render. Testing only the first would miss that the second is what actually makes the freeze hold."
---

<objective>
Attack the assessment-authority boundary with the real shipped gates under the
knife, from all three directions ACTIVITY-03 names, including the three new
places Phase 16A itself created.

ACTIVITY-03, quoted: "The runtime alone scores, grants keyed disclosure, selects
authoritative assessment behavior, and writes assessment evidence; prose remains
pending until approved marking, and no surface, agent, note, import, or visual
leaks a key, invents a score, auto-grades prose, or changes a frozen sitting.
Owner: deterministic runtime. Durable object: attempt evidence event. Authority:
runtime. Degraded: with no model, formal sittings run unchanged under runtime
authority."

Its Fixture sentence, quoted: "a 16A adversarial fixture in which a scripted
agent, a note, and an import each attempt to leak a key, invent a score,
auto-grade prose, or edit a frozen synthetic sitting, asserting the runtime
refuses each attempt."

This plan writes no runtime machinery. `16A-RESEARCH.md` is explicit that the
shipped runtime already enforces most of ACTIVITY-03 structurally:
`runtime.public_item()` withholds the key before a response exists,
`evidence.mark_event()` raises `ValueError` on any marker other than the literal
string `"human"`, and `runtime.glossable()` is, in its own docstring's words,
"the same class of decision as `public_item()` withholding a key: the runtime,
not the author and not a model, decides what reaches the learner." What is new
here is a test suite that attacks those gates on purpose.

`16A-RESEARCH.md`'s Pitfall 5 names the way this goes wrong: writing the suite
against a simplified mock of `runtime.score_response` or `evidence.mark_event`
"to keep the test isolated", which proves nothing about whether the actual
shipped gates hold. Constructing real sessions, real evidence logs, and real
bank fixtures is more setup than a mock. That setup is the deliverable.

The part `16A-RESEARCH.md` could only gesture at is Task 3. Phase 16A created
three new places a learner can be shown authored text before responding: an
`[!EXCERPT]` callout, a media `alt` attribute, and an activity's
`static_fallback`. Each is a new mouth for the same old leak. A composed
glossary is a fourth, because it assembles definitions into one document. All
four are attacked here, and all four are answered by the gates that already
exist. This phase writes no second leak detector: `runtime.glossable` is
deliberately conservative and returns `False` on any ambiguity, and a second
detector would eventually disagree with it about what counts as keyed content,
which is worse than one gate that is occasionally too strict.

Decisions already made, cited, and never re-derived here:

- **`16A-RESEARCH.md` Pitfall 5**: the suite calls the real imported functions;
  no `class Mock*` and no `def fake_*` stands in for `runtime.py` or
  `evidence.py`.
- **`16A-RESEARCH.md`'s Don't Hand-Roll table**, the leak-detector row:
  `runtime.glossable()`'s existing pattern is the answer for the new roles, not
  a new leak-scanning regex.
- **`.claude/CLAUDE.md`'s Runtime invariant**, quoted: "the runtime, not the
  model, settles scoring, assessment disclosure, and evidence", and its
  clarification that the invariant "names one scoring authority, not a frozen
  capability set", so an advisory grader may propose a mark and never settle
  one.
- **The Phase 1 decision log entry for `mark_event`**, quoted: "mark_event()
  rejects any marker other than 'human' (T-1-24); a model verdict is not
  accepted evidence until Phase 8/TEACH-09 teaches the runtime to hold one as
  pending review".
- **The Phase 1 decision D-11**, quoted from the decision log: renders take
  "only `(log, session_id, qs, bank_path)`, never the session JSON file itself:
  the session file cannot be an input to its own render", which is why editing
  a session file cannot change what a render reports.
- **`16A-DECISIONS.md` `## D-16A-1`**: the `EXCERPT` role token, whose callout
  is the first of the three new places authored text reaches a learner before a
  response exists.
- **`16A-DECISIONS.md` `## D-16A-7`**: the `## MEDIA` registry's `alt` column,
  the second of those three places.
- **`16A-DECISIONS.md` `## D-16A-8`**: media rights are declared and not
  enforced in 16A, so no attack in this suite tests a rights gate that does not
  exist; the deferral is recorded rather than tested.
- **The phase-shape constraint**: this plan invents no new runtime enforcement.

Purpose: prove the boundary holds under deliberate attack, including against
this phase's own additions.
Output: twelve refused attacks, four refused new-grammar leaks, and zero mocks.
</objective>

<context>
@.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-RESEARCH.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PATTERNS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md
@.planning/REQUIREMENTS.md
@.claude/CLAUDE.md
@runtime.py
@evidence.py
@surfaces/session.py
@tests/evidence_roundtrip.py
@tests/capability_stress_corpus_tracer.py
</context>

## Artifacts this phase produces (plan 16A-09 share)

New symbols introduced by this plan, and by nothing earlier:

- `tests/assessment_authority_adversarial.py` and on it: `fail`,
  `build_synthetic_sitting`, `attacker_agent`, `attacker_note`,
  `attacker_import`, twelve `attack_*` functions, four `attack_16a_*`
  functions, `main`
- `fixtures/lesson_capability_corpus.py`: `build_adversarial_bank`
- `tests/capability_stress_corpus_tracer.py`: `scenario_assessment_authority`

No module, no CLI command, no daemon route, and no schema file is produced by
this plan. No change is made to `runtime.py` or `evidence.py` by this plan.

<tasks>

<task type="auto">
  <name>Task 1: the suite skeleton, the synthetic sitting, and the agent and note attackers</name>
  <files>tests/assessment_authority_adversarial.py, fixtures/lesson_capability_corpus.py</files>
  <read_first>
- `16A-RESEARCH.md`'s Pitfall 5 in full, and its Don't Hand-Roll table's
  auto-grade row and leak-detector row.
- `runtime.py` lines 44 to 99, `public_item` in full. Note exactly which keys it
  returns for each item type and, more importantly, which it never returns.
- `runtime.py` lines 260 to 340, `canonical_response` and `score_response`, so
  the attacker calls the real scorer rather than reimplementing a verdict.
- `runtime.py` lines 1591 to 1644, `explain_payload` and `page_item`, so the
  post-response disclosure surface is distinguished from the pre-response one.
- `evidence.py` lines 394 to 460, `response_event`, and lines 735 to 800,
  `append_event`, so the import attacker writes through the real writer.
- `evidence.py` lines 1416 to 1471, `mark_event` in full, especially the
  `marker != "human"` refusal and the `verdict = bool(verdict)` line that
  follows it. The order of those two statements is the precision probe's whole
  subject.
- `tests/evidence_roundtrip.py` lines 1 to 40, the shipped test-file convention,
  and its session-construction helpers, so the synthetic sitting is built the
  way the repository already builds one.
- `surfaces/session.py`'s `cmd_submit`, for the exact refusal message a
  completed session produces.
- `fixtures/lesson_capability_corpus.py` in full as it stands after plan
  16A-08.
  </read_first>
  <action>
1. Create `tests/assessment_authority_adversarial.py` following
   `tests/evidence_roundtrip.py`'s opening convention exactly: shebang, module
   docstring stating it is standard library only, runnable as
   `python tests/assessment_authority_adversarial.py`, and that every gate it
   attacks is the real shipped function and never a stand-in; the
   standard-library import block; `ROOT` from `__file__`;
   `sys.path.insert(0, ROOT)`; and a local `fail(msg)` helper printing
   `FAIL: ` plus the message and exiting 1.

   Add a second paragraph to the module docstring stating the rule this file
   lives or dies by: no `class Mock*`, no `def fake_*`, no monkeypatched
   `runtime` or `evidence` attribute, and no simplified stand-in of any kind.
   State that a stub which refuses proves only that the stub refuses.

2. Add `build_adversarial_bank(dest_dir)` to
   `fixtures/lesson_capability_corpus.py`, following the established shape:
   literal fictional content, no `random`, deterministic bytes, no em dash
   characters. The bank carries at least one `mc` item with a full rationale
   block and one `short` item with a model answer and rubric points, because
   the four attacks need both a deterministically scored item and a
   human-marked one. It lints clean.

3. Add `build_synthetic_sitting(dest_dir)` to the test file. It creates a real
   temporary root, writes the adversarial bank, starts a real session through
   the shipped session path, answers the `mc` item correctly through the real
   scorer, and returns a small record carrying the root path, the bank path, the
   session id, the evidence log path, and the parsed questions. It uses no
   fixture-only shortcut: if the repository's session start requires a
   subprocess or a specific helper, use that one.

4. Add `attacker_agent(sitting)`, which stands for a scripted model client, and
   its four attacks. Each is its own named function so a failure says which
   attack succeeded:
   - `attack_agent_leak_key(sitting)`: call the real
     `runtime.public_item(question)` for the `mc` item before any response
     exists for it, and assert none of the returned dict's keys or values
     carries the correct option letter, the `WHY BEST` text, the
     `KEY DISCRIMINATOR` text, the `SECOND-BEST` text, or the distractor
     analysis. Assert on the whole serialized dict, not on a key list, so a
     future field that smuggles the key in a nested structure is caught.
   - `attack_agent_invent_score(sitting)`: build a `response_event` claiming a
     correct verdict for the `short` item without going through
     `runtime.score_response`, append it through the real
     `evidence.append_event`, and assert that what the evidence log reports for
     that item is not a settled correct score. Read the result through the same
     reader a report uses, not by inspecting the raw line.
   - `attack_agent_auto_grade(sitting)`: call the real `evidence.mark_event`
     with `marker="model"`, and assert it raises `ValueError`. Then call it with
     `marker="agent"` and `marker=""` and assert both raise. The gate is an
     equality check against the literal string `human`, and the second and third
     calls prove it is not a substring or a truthiness check.
   - `attack_agent_edit_frozen(sitting)`: complete the sitting, then attempt one
     more submit through the real session path and assert it is refused with the
     message `cmd_submit` actually produces; transcribe that message into the
     assertion from the shipped source rather than paraphrasing it.

5. Add `attacker_note(sitting)` and its four attacks. A note stands for
   learner-authored text that must never become source truth, lesson truth, an
   answer key, a score, or mastery. Each attack writes a learner-authored string
   into a place a note can reach and asserts it changes nothing authoritative:
   - `attack_note_leak_key(sitting)`: put the correct answer text into a learner
     note field and assert `runtime.public_item` for the item is unchanged,
     byte for byte, from the same call made before the note existed.
   - `attack_note_invent_score(sitting)`: put a string reading
     `SCORE: correct` into a note and assert the evidence log reports no
     additional response event and no changed verdict.
   - `attack_note_auto_grade(sitting)`: put a rubric-shaped verdict into a note
     and assert the `short` item's mark is still `None`, meaning pending, when
     read through the real reader.
   - `attack_note_edit_frozen(sitting)`: write a note referring to the completed
     sitting and assert the render computed from the evidence log is byte
     identical to the render taken before the note was written.

   If the repository has no learner-note storage yet, which is Phase 16C's,
   simulate a note as a plain text file beside the bank and assert that no
   shipped reader consults it. State that explicitly in the test's docstring so
   a later reader knows the attack surface is a stand-in for a store that does
   not exist rather than a mock of one that does.
  </action>
  <verify>
  <automated>python tests/assessment_authority_adversarial.py</automated>
Expected final line at the end of this task:
`ADVERSARIAL: 8 attempted, 8 refused, 0 succeeded`, exit code 0. The degraded
state this task must also prove is that the suite fails loudly when an attack
succeeds: temporarily invert one assertion, confirm the run exits non-zero and
names which attack succeeded, then restore it and re-run.
  </verify>
  <acceptance_criteria>
- `python tests/assessment_authority_adversarial.py` exits 0 with the final line
  `ADVERSARIAL: 8 attempted, 8 refused, 0 succeeded`.
- `grep -cE "class Mock|def fake_|monkeypatch|setattr\\((runtime|evidence)" tests/assessment_authority_adversarial.py`
  reports `0`.
- `grep -cE "^import (pytest|unittest)|^from (pytest|unittest)" tests/assessment_authority_adversarial.py`
  reports `0`.
- The file imports `runtime` and `evidence` directly and calls
  `runtime.public_item`, `runtime.score_response`, `evidence.append_event`, and
  `evidence.mark_event` by name; a grep finds each at least once.
- `evidence.mark_event` raises `ValueError` for `marker="model"`,
  `marker="agent"`, and `marker=""`.
- The frozen-sitting refusal message in the assertion matches the string
  `surfaces/session.py` produces; record both in the summary side by side.
- `python itembank.py lint` on the generated adversarial bank exits 0 with no
  errors.
- `python itembank.py guard .` reports `0 offending files`.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="reversible">A test file and a fixture builder. Neither
  changes a published surface and both can be rewritten.</reversibility>
  <done>A scripted agent and a scripted note each fail all four attacks against
  the real shipped gates, and the suite would say so loudly if either
  succeeded.</done>
</task>

<task type="auto">
  <name>Task 2: the import attacker, the boundary probe, and the precision probe</name>
  <files>tests/assessment_authority_adversarial.py</files>
  <read_first>
- `surfaces/import_anki.py` and `surfaces/migrate.py`, enough to see how the
  repository's existing import paths reach the evidence store, so the import
  attacker uses a real path rather than an invented one.
- `evidence.py`'s `live_events`, `events`, `attempt_number`, `marks_by_event`,
  and the retraction read-side filter, because the import attacker's success or
  failure must be judged through the same reader a report uses.
- `evidence.py` lines 1416 to 1471, `mark_event`, specifically the two adjacent
  statements: the `marker != "human"` raise and the `verdict = bool(verdict)`
  that follows it. Their order is the precision probe's subject.
- `runtime.py` lines 303 to 340, `score_response`, specifically what it returns
  for a `short` item, which is `None` and not `False`.
- `runtime.py` lines 44 to 99, `public_item`, again, for the boundary probe's
  three call points.
- `tests/assessment_authority_adversarial.py` as it stands after Task 1.
  </read_first>
  <action>
1. Add `attacker_import(sitting)` and its four attacks. An import stands for
   externally sourced records arriving through a migration or an interchange
   path:
   - `attack_import_leak_key(sitting)`: construct an import record whose payload
     carries the correct answer in a field name a renderer might reflect, run it
     through whichever real import path the repository exposes, and assert
     `runtime.public_item` for the affected item is unchanged from before.
   - `attack_import_invent_score(sitting)`: construct an import record claiming
     a settled correct verdict for the `short` item, append it through the real
     `evidence.append_event`, and assert the item's mark read through
     `marks_by_event` is still `None`, meaning pending, and is not `True`.
   - `attack_import_auto_grade(sitting)`: construct an import record carrying a
     mark whose `marker` field is anything other than `human`, and assert the
     real `mark_event` refuses it. If the import path builds its event through
     a different constructor, follow that constructor and assert the refusal
     wherever it actually lives; record in the summary which path was taken.
   - `attack_import_edit_frozen(sitting)`: attempt to change the completed
     sitting by two routes, because the two refusals are different in kind.
     First, rewrite the session JSON file directly on disk to claim a different
     verdict, then render the attempt through the real render function and
     assert the render is byte identical to the render taken before the edit.
     That refusal is structural: Phase 1's D-11 made the session file stop being
     an input to its own render, so an edited session file changes nothing a
     report says. Second, attempt an append that claims to overwrite an existing
     event and assert the log still carries both records, because the store is
     append-only and correction happens through a recorded retraction rather
     than through an edit.

2. Add `attack_boundary_public_item(sitting)`, resolving ACTIVITY-03's boundary
   probe. It calls the real `runtime.public_item` for the same item at three
   points and asserts the same absence at each: before any response exists for
   it, immediately after one response exists, and after the sitting's status is
   complete. Assert on the whole serialized dict at each point, checking that
   none of the correct option letter, the rationale text, the discriminator
   text, the second-best text, or any distractor-analysis text appears anywhere
   in it.

   Asserting only the pre-response case would test the easy side of the
   threshold. The step either side is where a boundary check earns its keep.

3. Add `attack_precision_pending_mark(sitting)`, resolving ACTIVITY-03's
   precision probe. It asserts three things:
   - `runtime.score_response` for the `short` item returns `None` and not
     `False`, so a not-yet-marked prose answer is distinguishable from a wrong
     one.
   - Reading that item's mark through the real reader returns `None` after a
     response exists and before any human mark exists.
   - `evidence.mark_event` performs its `marker != "human"` refusal before it
     coerces `verdict` to `bool`. Prove it behaviorally rather than by reading
     the source: call `mark_event` with `marker="model"` and a `verdict` value
     that is neither `True` nor `False`, such as the string
     `probably correct`, and assert the raised exception is the `ValueError`
     about the marker rather than any error about the verdict. If coercion ran
     first, a non-boolean verdict would have been silently accepted as truthy
     before the marker was ever checked.

4. Add `main()` to the suite: run every `attack_*` function in source order,
   count attempted, refused, and succeeded, and print as the final line exactly
   `ADVERSARIAL: %d attempted, %d refused, %d succeeded`. Exit 0 only when
   succeeded is zero. Add the standard `if __name__ == "__main__": main()`
   guard.

   An attack that raises an unexpected exception counts as neither refused nor
   succeeded and fails the run by name, because an unexpected exception is a
   result nobody predicted and reading it as a refusal would be generous in the
   wrong direction.
  </action>
  <verify>
  <automated>python tests/assessment_authority_adversarial.py</automated>
Expected final line at the end of this task:
`ADVERSARIAL: 14 attempted, 14 refused, 0 succeeded`, exit code 0. The degraded
state this task must also prove is the with-no-model clause of ACTIVITY-03's
Degraded sentence: run the whole suite with any model backend configuration
absent or disabled and confirm every refusal is identical, since none of these
gates consults a model.
  </verify>
  <acceptance_criteria>
- `python tests/assessment_authority_adversarial.py` exits 0 with the final line
  `ADVERSARIAL: 14 attempted, 14 refused, 0 succeeded`.
- `runtime.score_response` on the `short` item returns `None`, not `False`.
- `mark_event(marker="model", verdict="probably correct")` raises `ValueError`
  whose message mentions the marker and not the verdict.
- The session-file edit leaves the rendered attempt byte identical; record both
  SHA-256 digests in the summary.
- The overwrite-shaped append leaves both records in the log.
- `attack_boundary_public_item` asserts at three distinct points and the
  assertion covers the whole serialized dict at each.
- An attack raising an unexpected exception fails the run rather than counting
  as refused; prove it once by temporarily raising inside one attack and
  confirming the run exits non-zero and names it, then restore.
- `grep -cE "class Mock|def fake_|monkeypatch" tests/assessment_authority_adversarial.py`
  reports `0`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="reversible">A test file. It changes no published
  surface.</reversibility>
  <done>An import fails all four attacks, the disclosure boundary is asserted on
  both sides and at the threshold, and a pending prose mark is proven
  uncoercible into a settled one.</done>
</task>

<task type="auto">
  <name>Task 3: attack Phase 16A's own new mouths, through the gates that already exist</name>
  <files>tests/assessment_authority_adversarial.py, fixtures/lesson_capability_corpus.py, tests/capability_stress_corpus_tracer.py</files>
  <read_first>
- `runtime.py` lines 1509 to 1540, `glossable` in full, including the exact
  fragments it checks against: `canonical_key()` output, correct option labels,
  and collapsed key and answer text. This function is the answer for all four
  attacks in this task and no second detector is written.
- `16A-RESEARCH.md`'s Don't Hand-Roll table, the leak-detector row, verbatim.
- `surfaces/lesson.py` as it stands after plans 16A-03 through 16A-06: the
  `EXCERPT` callout, `_media_figure_html`'s `alt` emission, and the activity
  static-fallback paragraph inside the check branch. These are the three new
  places authored text reaches a learner before a response exists.
- `capabilities.compose_glossary` as landed by plan 16A-07, the fourth place.
- `model.parse_terms` and the shipped gloss path in `surfaces/lesson.py`, so the
  existing suppression behavior is understood before the composed glossary is
  attacked.
- `tests/capability_stress_corpus_tracer.py` in full.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md`.
  </read_first>
  <action>
1. Extend `build_adversarial_bank` so the generated bank additionally carries,
   all with fictional content and all deliberately hostile:
   - One `> [!EXCERPT]` callout whose body quotes, verbatim, the `WHY BEST`
     rationale text of the bank's `mc` item.
   - One `## MEDIA` row whose `alt` column states the correct option letter and
     the correct option's text for that same item.
   - One `## ACTIVITIES` row for that item whose `static_fallback` states the
     correct answer in plain words.
   - One `## TERMS` row whose definition restates the correct answer, so a
     composed glossary would carry it.

   Every one of these is authored content a hostile or careless author could
   write today. The bank is a fixture of bad authoring, not of malformed syntax,
   and it must still lint clean apart from any finding these deliberately
   produce; record which findings it produces in the summary.

2. Add four `attack_16a_*` functions to
   `tests/assessment_authority_adversarial.py`, each answering its question
   through an existing gate and never through a new detector:
   - `attack_16a_excerpt_leak(sitting)`: render the lesson before any response
     exists and assert either that the rendered page does not contain the `mc`
     item's rationale text, or, if it does, that the page is one no learner
     reaches before responding and that `runtime.public_item` for the item still
     carries none of it. State which of the two holds in the assertion message,
     because those are materially different results and the summary must record
     which one this codebase actually produces.
   - `attack_16a_media_alt_leak(sitting)`: assert `runtime.glossable` returns
     `False` for a term whose definition is the media row's `alt` text, using
     the real function against the real parsed questions, and assert that
     `runtime.public_item` for the item still carries no key. The `alt` text
     itself is authored content the renderer will show; the assertion here is
     that the runtime's own conservative gate classifies it as keyed material,
     which is the signal a later phase needs to suppress it.
   - `attack_16a_activity_fallback_leak(sitting)`: the same assertion for the
     activity's `static_fallback` text.
   - `attack_16a_composed_glossary_leak(sitting)`: compose the glossary through
     `capabilities.compose_glossary`, then assert that for every composed entry,
     `runtime.glossable(questions, entry_term)` is consulted and that the entry
     whose definition restates the answer is the one for which it returns
     `False`. Assert that no new leak-scanning regex exists anywhere in the
     phase's code by grepping `capabilities.py`, `model.py`, and
     `surfaces/lesson.py` for a second detector; a match fails the attack.

   Where an assertion discovers that this phase's new grammar currently does
   leak, the correct outcome is a FAILING attack, a recorded finding, and a
   named follow-up, not a weakened assertion. Write the assertions to be honest
   first. If one fails, record it in the summary as an open finding with the
   exact rendered text, and let plan 16A-10's freeze gate decide whether the
   freeze is withheld. Do not soften the check to make the suite green.

3. Add `scenario_assessment_authority()` to
   `tests/capability_stress_corpus_tracer.py`. It runs
   `tests/assessment_authority_adversarial.py` as a subprocess, asserts exit
   code 0, and asserts the final line matches the pattern
   `ADVERSARIAL: N attempted, N refused, 0 succeeded` with the attempted and
   refused counts equal. It does not duplicate the attacks; the adversarial
   suite is their home and the tracer records that it passed.

4. Update `16A-VALIDATION.md`'s Per-Task Verification Map with three rows for
   plan 16A-09's tasks, naming `tests/assessment_authority_adversarial.py` and
   `scenario_assessment_authority`, with a Status of `passing`. Tick the Wave 0
   Requirements checkbox for `tests/assessment_authority_adversarial.py`.
  </action>
  <verify>
  <automated>python tests/assessment_authority_adversarial.py</automated>
Expected final line: `ADVERSARIAL: 18 attempted, 18 refused, 0 succeeded`, exit
code 0. Then run `python tests/capability_stress_corpus_tracer.py`, expecting
`TRACER: 14 passed, 0 skipped, 0 failed`. The degraded state this task must also
prove is honesty under failure: if any `attack_16a_*` assertion fails, the run
exits non-zero and names the leak, and the summary records the exact rendered
text rather than the assertion being softened.
  </verify>
  <acceptance_criteria>
- `python tests/assessment_authority_adversarial.py` exits 0 with the final line
  `ADVERSARIAL: 18 attempted, 18 refused, 0 succeeded`, or exits non-zero with a
  named leak recorded in the summary as an open finding.
- `python tests/capability_stress_corpus_tracer.py` exits 0 with the final line
  `TRACER: 14 passed, 0 skipped, 0 failed`.
- All four `attack_16a_*` functions call `runtime.glossable` or
  `runtime.public_item` by name; a grep finds each at least once.
- No second leak detector exists: a grep of `capabilities.py`, `model.py`, and
  `surfaces/lesson.py` for a function whose name contains `leak`, `disclose`, or
  `key_scan` reports `0`.
- `grep -cE "class Mock|def fake_|monkeypatch" tests/assessment_authority_adversarial.py`
  reports `0`.
- `python itembank.py guard .` reports `0 offending files`.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- `16A-VALIDATION.md` has three new filled rows naming plan `16A-09` and the
  adversarial-suite Wave 0 checkbox is ticked.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="reversible">A test file, a fixture extension, and one
  tracer scenario. None changes a published surface.</reversibility>
  <done>Every new place Phase 16A lets authored text reach a learner is attacked
  through the gate that already exists, and any leak found is recorded rather
  than assumed away.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| scripted agent to runtime | A model client can call every public function this repository exposes and can construct any payload it likes. |
| learner note to accepted truth | Learner-authored text must never become source truth, lesson truth, an answer key, a score, or mastery. |
| imported record to evidence store | External records arrive through a migration or interchange path and reach the same append-only store live responses do. |
| authored lesson text to pre-response learner | Phase 16A created three new places authored text is shown before a response exists, plus a fourth in a composed glossary. |
| completed sitting to later edit | A frozen sitting is where a retroactive change would be least visible and most damaging. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16A-09-01 | Information Disclosure | a key reaching a learner before a response exists | critical | mitigate | `runtime.public_item` never returns key, rationale, discriminator, second-best, or distractor-analysis fields, asserted on the whole serialized dict at three boundary points by `attack_boundary_public_item`, plus once per attacker. |
| T-16A-09-02 | Elevation of Privilege | a model verdict recorded as accepted evidence | critical | mitigate | `evidence.mark_event` raises `ValueError` for any marker other than the literal string `human`, asserted for `model`, `agent`, and the empty string, and asserted to fire before verdict coercion by the non-boolean-verdict probe. |
| T-16A-09-03 | Tampering | a score invented without passing through the one scorer | critical | mitigate | Each attacker constructs a manufactured event and appends it through the real `evidence.append_event`, and the result is judged through the same reader a report uses; the short item's mark stays `None`. |
| T-16A-09-04 | Tampering | a frozen sitting changed after the fact | high | mitigate | Two refusals are asserted separately: the active refusal from the session path with its shipped message transcribed, and the structural one where an edited session file changes no render because a render is computed from the append-only log and never from the session file (Phase 1 D-11). |
| T-16A-09-05 | Information Disclosure | Phase 16A's own new grammar leaking a key through an excerpt, a media alt, an activity fallback, or a composed glossary | critical | mitigate | Four dedicated `attack_16a_*` functions, each answering through `runtime.glossable` or `runtime.public_item` rather than through a new detector. A failure is recorded as an open finding and routed to plan 16A-10's freeze decision rather than softened. |
| T-16A-09-06 | Spoofing | a mocked gate proving nothing while the suite reports green | critical | mitigate | The module docstring states the rule, and the acceptance criteria grep for `class Mock`, `def fake_`, `monkeypatch`, and direct attribute assignment on `runtime` or `evidence`, requiring zero matches on every task. |
| T-16A-09-07 | Repudiation | an unexpected exception counted as a refusal | high | mitigate | `main()` counts an unexpected exception as neither refused nor succeeded and fails the run by name; the acceptance criteria require this proven once by temporarily raising inside an attack. |
| T-16A-09-08 | Tampering | a second leak detector disagreeing with `runtime.glossable` | high | mitigate | Task 3 forbids one and greps three modules for a function whose name contains `leak`, `disclose`, or `key_scan`, requiring zero matches. |
| T-16A-09-09 | Information Disclosure | real course or exam content entering the repository through an adversarial bank | high | mitigate | Every string in `build_adversarial_bank` is a literal fictional constant with no `random` and no external read; `python itembank.py guard .` reporting `0 offending files` is an acceptance criterion on every task. |
| T-16A-09-10 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; the suite is standard library only and imports only in-repo modules. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- Any change to `runtime.py` or `evidence.py`. This plan attacks them and
  changes neither. If an attack succeeds, the correct outcome is a recorded
  finding routed to plan 16A-10's freeze decision, not a fix invented here.
- Any new leak detector, key scanner, or disclosure regex in `capabilities.py`,
  `model.py`, or `surfaces/lesson.py`. `runtime.glossable` is the one gate of
  its class.
- Any new enforcement machinery of any kind. `16A-RESEARCH.md` is explicit that
  this fixture is new test code proving existing gates hold.
- Any mock, stub, monkeypatch, or simplified stand-in for `runtime.py` or
  `evidence.py`.
- A learner-note storage system. Notes are Phase 16C's; this plan simulates a
  note as a plain file and says so in the test docstring.
- Suppressing a leaking excerpt, media alt, or activity fallback at render time.
  If one leaks, this plan records it; deciding the suppression is the work of
  whichever phase owns it, informed by the finding.
- Softening any assertion to make the suite green.
</out_of_scope>

<flagged_assumptions>
- **ACTIVITY-03's two probe rows are resolved by this plan** as explicit
  criteria carried in `must_haves.truths`: the boundary row as
  `runtime.public_item` asserted at three points rather than one, and the
  precision row as a pending mark that stays `None` and a marker gate that fires
  before verdict coercion.
- **Whether Phase 16A's new grammar actually leaks is not known at plan time.**
  Task 3's four attacks are written to find out honestly. The plan states the
  correct outcome for either result, and routes a discovered leak to plan
  16A-10's freeze decision rather than to a same-plan fix, because a fix
  designed under a green-suite deadline is how a real finding becomes a
  weakened assertion.
- **The import attacker's exact path depends on what the repository exposes.**
  `surfaces/import_anki.py` and `surfaces/migrate.py` are named as the places to
  look; the plan requires the real path be used and the choice recorded, rather
  than specifying one that may not fit.
- **The learner-note attack surface is a stand-in.** No learner-note store
  exists yet. The attacks assert that no shipped reader consults a plain file
  beside the bank, which is a weaker claim than attacking a real store would be,
  and the test docstring is required to say so.
</flagged_assumptions>

<summary_obligations>
`16A-09-SUMMARY.md` records: the eighteen attack function names and the result
of each; the frozen-sitting refusal message from `surfaces/session.py` and the
one transcribed into the assertion, side by side; the two render SHA-256 digests
from the session-file-edit attack; which import path the import attacker used
and why; the exact result of each of the four `attack_16a_*` attacks, including,
if any leaked, the exact rendered text and the item it came from, recorded as an
open finding for plan 16A-10; the lint findings the adversarial bank produced;
confirmation that the unexpected-exception path was exercised and restored; the
adversarial suite's and the tracer's final lines verbatim; which truth was
verified by which command with the command's actual stdout; and any deviation
from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16A-semantic-capability-activity-contract/16A-09-SUMMARY.md`
when done.
</output>
