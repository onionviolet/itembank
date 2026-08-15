---
phase: 15A-director-treatment-policy
plan: 05
type: execute
wave: 5
depends_on: ["15A-04"]
files_modified:
  - director.py
  - tests/journal_roundtrip.py
  - tests/director_roundtrip.py
  - fixtures/corpus_14b.py
autonomous: true
requirements: [RELIABILITY-02, AGENT-01]
estimate:
  tokens: 70000
  raw_tokens: 70000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "One recorded agent operation replays step by step from the journal alone, with no chat transcript and no in-memory state: director.replay_operation reads only journal.entries and returns a report naming each of the thirteen OPERATION-CONTRACT steps as recorded, not-applicable with a stated reason, or missing, and the verdict is complete only when no step is missing."
    - "An operation interrupted at any checkpoint phase resumes or reverses from the journal alone: for each of the thirteen phases, killing the operation immediately after that phase leaves director.resume_point naming that phase as the last recorded one and the next phase as the next action, and director.reverse_operation restores the pre-operation state through journal.undo without a second undo mechanism."
    - "The journal stays one journal: journal.py's whole-phase diff is still exactly the two lines plan 15A-01 added, OPERATION_TYPES is still exactly six, and no file matching the pattern of a second append-only operation log exists anywhere under the journal directory."
    - "RELIABILITY-02 adjacency edge: two phases recorded in the same clock tick are distinguished by their phase_index, never merged; two entries never share an entry_id; and a repeated phase name within one operation id is refused with director.duplicate_phase rather than appended."
    - "RELIABILITY-02 empty edge: an operation interrupted before its first recorded phase reports resumable false with reason no-checkpoint-recorded and reverses to a no-op, rather than replaying a partial write; an operation id with zero entries raises director.operation_unknown naming the id."
    - "RELIABILITY-02 ordering edge: replay reads entries in journal append order and never sorts by timestamp, so two entries written within one clock tick keep the order they were appended in, and the report names an out-of-order phase_index rather than silently sorting it."
    - "AGENT-01 adjacency edge: two protocol steps recorded with the same phase name inside one operation collide and the second is refused; the same phase name in two different operation ids is two independent records that never interfere."
    - "AGENT-01 empty edge: a journal with zero agent_operation entries replays to a report whose thirteen steps are all missing and whose verdict is incomplete, never complete, and never an empty report that reads as success."
    - "AGENT-01 encoding edge: phase names are compared as exact ASCII tokens against the frozen thirteen-name director.PROTOCOL_STEPS tuple, byte for byte, with no case folding, no synonym table, and no prefix matching; an unrecognized phase name is refused with director.unknown_phase naming the value."
    - "AGENT-01 ordering edge: the report lists the thirteen steps in PROTOCOL_STEPS index order regardless of the order they were journaled, and any step whose recorded phase_index does not match its PROTOCOL_STEPS index is named in the report's out_of_order list rather than silently reordered."
    - "AGENT-01 idempotency edge: replaying the same operation twice with the same operation id appends no second entry and returns already_recorded, following the same dedupe discipline evidence.py already applies to a replayed response."
    - statement: "Two director operations against one course root never both write: the loser reports journal.busy, writes nothing, and leaves the sidecar bytes unchanged, and an operation killed mid-write leaves either the old or the new valid state and never a mixed one."
      verification: backstop
    - "The core loop stays fully operable with the agent disabled: with every registered profile removed from settings, the shipped scoring, evidence, and protocol suites pass and a course sidecar can still be read, written, and bound by a human actor through course.py directly."
  prohibitions: []
  artifacts:
    - "director.py gains PROTOCOL_STEPS, PHASE_OUTCOMES, PROTOCOL_REPORT_KEYS, replay_operation, protocol_report, resume_point, and reverse_operation"
    - "tests/journal_roundtrip.py gains check_agent_operation_record"
    - "tests/director_roundtrip.py gains check_protocol_replay, check_resume_and_reverse, and check_protocol_edges"
    - "fixtures/corpus_14b.py gains build_interrupted_operation and a --child mode entry point for the kill fixtures"
  key_links:
    - "This plan owns the tests/journal_roundtrip.py addition. 15A-RESEARCH.md's Wave 0 Gaps left the question open of whether 14A, 14B, or 15A adds check_agent_operation_record; the answer is 15A, because 15A is the phase that adds the record type, and a coupling test that lives with the vocabulary it checks cannot drift from it."
    - "replay_operation must read only journal.entries. If it accepts the in-memory operation object, or reads back anything director held during the run, the test proves that a process can remember its own work rather than that the journal is the durable job record, which is exactly the claim RELIABILITY-02 makes."
    - "reverse_operation must call journal.undo. A second restore path in director.py would be a second undo mechanism, and the guarantee that any fault leaves the old or the new valid state would then depend on two implementations agreeing."
---

<objective>
Make the operation protocol checkable rather than merely stated: one recorded
agent operation replays step by step from the journal alone against the
thirteen-step contract, an interruption at any phase resumes or reverses from
that record, and the whole thing runs on the one journal Phase 14A froze.

The defect this closes is the one RELIABILITY-02 names in plain words: "the
journal is the durable job record, not a chat transcript." A system whose
resumability depends on a conversation still being open is a system that loses
work when a window closes, and a protocol that exists only as prose in a skill
file is a protocol nothing can fail.

Decisions already made, cited, and never re-derived here:

- **REQUIREMENTS.md RELIABILITY-02**, quoted: "Agent and maintenance operations
  run through a durable local operation journal with intent, actor, scopes,
  inputs, expected fingerprints, phases, checkpoints, proposals, validation,
  and undo, shared across hosted, local, and manual continuation... Degraded:
  an interrupted job resumes or reverses from its last checkpoint. Fixture: a
  15A journaled synthetic agent operation interrupted at each checkpoint phase,
  asserting resume and reverse work from the journal alone without any chat
  transcript."
- **REQUIREMENTS.md AGENT-01**, quoted, its Fixture sentence: "a 15A
  four-subject review operation replayed step by step from a synthetic
  operation journal against the protocol checklist, asserting every protocol
  stage is present and the core loop stays operable with the agent disabled."
- **OPERATION-CONTRACT.md**, "The one operation protocol", the thirteen
  numbered steps, read verbatim. This plan freezes their tokens; it does not
  rewrite their meaning.
- **15A-RESEARCH.md Pitfall 3**: RELIABILITY-02 is a requirement on what the
  journal must be able to express, not a mandate for a second journal.
- **15A-01 Task 4**: `journal.RECORD_TYPES` already gained
  `agent_operation` and `journal.ENTRY_KEYS` already gained `agent`. This plan
  adds nothing further to `journal.py`.

Decisions this plan makes and locks, so the executor never guesses:

| Open question | Locked answer | One-line rationale |
|---|---|---|
| The thirteen phase tokens | The frozen tuple given verbatim in Task 1, one token per numbered OPERATION-CONTRACT step | An unfrozen name set is a synonym table waiting to happen, and a checklist whose names drift cannot fail. |
| What a step with no shipped surface records | `not-applicable` with a required non-empty reason, which the report counts as present | Recording `recorded` for a preview surface that does not exist would be a false claim; recording `missing` would make every operation permanently incomplete. A named exemption is honest and reviewable. |
| The accessible-preview step in particular | Always `not-applicable` with the reason `no learner-facing preview surface ships before 16B; accessibility is never self-certified` | AGENT-02 forbids an agent self-certifying accessibility, and this phase ships no learner-facing surface. |
| Whether replay sorts | It never sorts. It reads append order and names any phase whose recorded index disagrees with its `PROTOCOL_STEPS` index in an `out_of_order` list | Sorting hides the defect the check exists to find. |
| Where the reverse comes from | `journal.undo`, the one undo mechanism 14A-02 built | A second restore path would make the old-or-new guarantee depend on two implementations agreeing. |
| Who owns `check_agent_operation_record` | This plan, in `tests/journal_roundtrip.py` | The phase that adds the record type owns the coupling test for it; `15A-RESEARCH.md` left the ownership open and this is the answer. |

Purpose: make the journal, and not a conversation, the thing an operation
resumes from.
Output: the thirteen-step replay, the resume and reverse paths, the
interruption fixtures, and the journal coupling test.
</objective>

<context>
@.planning/phases/15A-director-treatment-policy/15A-RESEARCH.md
@.planning/phases/15A-director-treatment-policy/15A-PATTERNS.md
@.planning/phases/15A-director-treatment-policy/15A-01-PLAN.md
@.planning/phases/15A-director-treatment-policy/15A-04-PLAN.md
@.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md
@.agents/skills/OPERATION-CONTRACT.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
</context>

## Artifacts this phase produces (plan 15A-05 share)

Added to `director.py`. Every symbol below is new in this phase.

- Constants: `PROTOCOL_STEPS` (the frozen thirteen-token tuple defined in
  Task 1), `PHASE_OUTCOMES = ("recorded", "not-applicable", "missing")`,
  `PROTOCOL_REPORT_KEYS = ("operation_id", "steps", "out_of_order",
  "verdict", "resumable", "reason")`,
  `PROTOCOL_VERDICTS = ("complete", "incomplete")`.
- Functions: `replay_operation(base, operation_id)`,
  `protocol_report(entries)`, `resume_point(base, operation_id)`,
  `reverse_operation(base, operation_id, actor_kind, actor_name)`.
- New `DirectorError` codes: `director.duplicate_phase`,
  `director.unknown_phase`, `director.operation_unknown`,
  `director.already_recorded`.

Added to `tests/journal_roundtrip.py`: `check_agent_operation_record()`, wired
into that file's existing `main()`.

Added to `fixtures/corpus_14b.py`: `build_interrupted_operation(dest, kill_after_phase)`
and a `--child` mode entry point following the shape
`tests/journal_roundtrip.py` and `tests/durability_roundtrip.py` already use
for their kill fixtures.

New test functions in `tests/director_roundtrip.py`:
`check_protocol_replay()`, `check_resume_and_reverse()`,
`check_protocol_edges()`.

No CLI command, no daemon route, no schema file, and no further journal record
type or entry key is produced by this plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the thirteen frozen phases and the replay report</name>
  <files>director.py, tests/director_roundtrip.py</files>
  <read_first>
- `.agents/skills/OPERATION-CONTRACT.md`, the section "The one operation
  protocol", all thirteen numbered steps and the paragraph immediately after
  them, verbatim. The tokens this task freezes come from those numbers and
  from nowhere else.
- `director.py` as it stands after plan 15A-04, in full: `AGENT_ENTRY_KEYS`,
  `AGENT_RECORD_TYPE`, `begin_operation`, `record_phase`, `recommend_once`,
  `apply_recommendation`, `egress_record`, and `authorize_write`.
- `journal.py` as landed: `entries`, `append_entry`, `ENTRY_KEYS`,
  `RECORD_TYPES`, `new_entry_id`, `ENTRY_STATES`, and `JournalError`.
- `evidence.py` lines 51 to 55 (`KNOWN_EVENT_TYPES`) and lines 755 to 774
  (`events`), the closed-vocabulary skip-and-warn read discipline this
  project already established and that the phase-name check mirrors in its
  strictness.
- `tests/director_roundtrip.py` as it stands after plan 15A-04.
  </read_first>
  <behavior>
Assertions added to `tests/director_roundtrip.py` in a new
`check_protocol_replay()` function, written before the code. Run and confirm it
fails.

The frozen vocabulary:

- `director.PROTOCOL_STEPS` equals, in this exact order,
  `("declare-intent", "declare-authority", "inventory", "plan-treatment",
  "checkpoint", "draft", "cite", "validate", "preview", "diff", "review",
  "accept", "report")` and has exactly thirteen members.
- `director.PHASE_OUTCOMES` equals `("recorded", "not-applicable", "missing")`.
- `director.PROTOCOL_VERDICTS` equals `("complete", "incomplete")`.
- `director.record_phase` with a phase name of `"Declare-Intent"` raises
  `DirectorError` with code `director.unknown_phase`, naming the value. There
  is no case folding.
- `director.record_phase` with a phase name of `"declare"` raises the same
  code. There is no prefix matching.
- `director.record_phase` with a phase name of `"declare_intent"` raises the
  same code. There is no separator normalization and no synonym table.

Replay reads only the journal:

- `director.replay_operation(base, operation_id)` has exactly two parameters,
  asserted by introspecting its signature. No in-memory operation object can be
  passed to it.
- After one full operation runs, `replay_operation` returns a dict whose key
  set equals `set(director.PROTOCOL_REPORT_KEYS)`.
- Its `steps` value is a list of exactly thirteen dicts, one per
  `PROTOCOL_STEPS` member, each with the keys `step`, `index`, `outcome`,
  `reason`, and `entry_id`, listed in `PROTOCOL_STEPS` index order.
- Every `outcome` is a member of `director.PHASE_OUTCOMES`.
- Every step whose `outcome` is `not-applicable` has a non-empty `reason`, and
  every step whose `outcome` is `recorded` has a non-empty `entry_id` that
  matches a real entry in `journal.entries(base)`.
- The `preview` step's `outcome` is `not-applicable` and its `reason` is
  exactly `no learner-facing preview surface ships before 16B; accessibility is
  never self-certified`.
- The `verdict` is `complete` when no step's outcome is `missing`, and
  `incomplete` otherwise.
- Deleting the journal file and re-running `replay_operation` raises
  `DirectorError` with code `director.operation_unknown` naming the operation
  id, rather than returning a report built from anything the process still held.

Duplicates, ordering, and empty:

- Recording the same phase name twice within one operation id raises
  `DirectorError` with code `director.duplicate_phase`, naming the phase and
  the operation id, and appends nothing.
- Recording the same phase name under two different operation ids succeeds
  twice. Two operations never interfere.
- Journaling the phases out of contract order, for example `cite` before
  `draft`, still produces a report listing the thirteen steps in
  `PROTOCOL_STEPS` order, and names both steps in the report's
  `out_of_order` list. The report never reorders the journal and never sorts by
  timestamp.
- `director.protocol_report([])` returns a report whose thirteen steps are all
  `missing`, whose `verdict` is `incomplete`, and whose `out_of_order` is
  empty. An empty journal never reads as success.
- Two entries appended without an intervening clock change keep their append
  order in `journal.entries(base)`, and the report's `entry_id` values follow
  that same order. Asserted by appending two phases in a tight loop and
  comparing the order.

Idempotency:

- Calling `director.record_phase` a second time with an identical operation id,
  phase, and phase index returns the string `already_recorded` and appends no
  entry, rather than raising. The journal length is unchanged.
- The distinction is explicit: a repeat of the same phase with a DIFFERENT
  phase index is a duplicate and raises `director.duplicate_phase`; a repeat
  with the identical index is an idempotent replay and returns
  `already_recorded`.
  </behavior>
  <action>
1. Add `check_protocol_replay()` to `tests/director_roundtrip.py` first, wired
   into `main()`, with every assertion above. Run
   `python tests/director_roundtrip.py` and confirm it fails.

2. Add to `director.py` the constant `PROTOCOL_STEPS = ("declare-intent",
   "declare-authority", "inventory", "plan-treatment", "checkpoint", "draft",
   "cite", "validate", "preview", "diff", "review", "accept", "report")` with
   a comment stating that each token is one numbered step of the one operation
   protocol in `.agents/skills/OPERATION-CONTRACT.md`, that the tuple is frozen
   and closed, that comparison is exact ASCII with no case folding and no
   synonyms, and that a fourteenth step is a change to the shared contract and
   not to this module.

3. Add `PHASE_OUTCOMES = ("recorded", "not-applicable", "missing")`,
   `PROTOCOL_VERDICTS = ("complete", "incomplete")`, and
   `PROTOCOL_REPORT_KEYS = ("operation_id", "steps", "out_of_order",
   "verdict", "resumable", "reason")`.

4. Add these codes to `DIRECTOR_CODES` with these exact message templates:
   - `director.unknown_phase`: `"%s is not one of the thirteen operation
     protocol steps; the vocabulary is frozen and comparison is exact, with no
     case folding and no synonyms"`
   - `director.duplicate_phase`: `"the phase %s is already recorded for
     operation %s at a different index; a protocol step is recorded once per
     operation and a second recording is refused rather than appended"`
   - `director.operation_unknown`: `"no journal entry carries operation id %s;
     the journal is the durable job record and there is nothing to replay"`
   - `director.already_recorded`: `"the phase %s at index %d is already
     recorded for operation %s; this replay appended nothing"`

5. Extend `record_phase` so that it raises `director.unknown_phase` for a phase
   name not in `PROTOCOL_STEPS`, returns the string `already_recorded` and
   appends nothing when an entry with the identical operation id, phase, and
   phase index already exists, and raises `director.duplicate_phase` when an
   entry with the same operation id and phase exists at a different index.
   Determine each case by reading `journal.entries(base)`, never a cached list.

6. Implement `protocol_report(entries)`, a pure function taking a list of
   journal entries already filtered to one operation id and returning the
   report dict. It walks `PROTOCOL_STEPS` in index order, finds the matching
   recorded entry by exact phase-name equality, sets `outcome` from the entry's
   own recorded outcome or `missing` when no entry exists, collects into
   `out_of_order` every step whose recorded `phase_index` differs from its
   `PROTOCOL_STEPS` index, and sets `verdict` to `complete` only when no step
   is `missing`. It sorts nothing.

7. Implement `replay_operation(base, operation_id)` taking exactly those two
   parameters. It reads `journal.entries(base)`, filters to entries whose
   `operation` is `AGENT_RECORD_TYPE` and whose `agent` dict's `operation_id`
   matches, raises `director.operation_unknown` when that filter is empty, and
   otherwise returns `protocol_report` over the filtered list in append order.
   Its docstring states in plain sentences that this function reads the journal
   and nothing else, and that if it ever accepted an in-memory operation object
   the test would prove a process can remember its own work rather than that
   the journal is the durable job record.

8. Make every existing phase-recording call site in `director.py` use a token
   from `PROTOCOL_STEPS`, and record the `preview` step as `not-applicable`
   with the exact reason string given in `<behavior>` at the point in
   `recommend_once` where a preview would otherwise be produced.

9. Re-run `python tests/director_roundtrip.py` until it passes, then run
   `python itembank.py guard .` and confirm it reports `0 offending files`.
  </action>
  <verify>
  <automated>python tests/director_roundtrip.py</automated>
Expected: prints `OK director_roundtrip` and exits 0. Degraded states this task
proves: an empty journal replays to thirteen missing steps and the verdict
incomplete rather than to an empty report that reads as success; a deleted
journal raises by name rather than returning a remembered report; and phases
journaled out of contract order are named rather than silently sorted.
  </verify>
  <acceptance_criteria>
- `python tests/director_roundtrip.py` exits 0 and prints `OK director_roundtrip`.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `python -c "import director; print(len(director.PROTOCOL_STEPS), director.PROTOCOL_STEPS[0], director.PROTOCOL_STEPS[-1])"`
  prints `13 declare-intent report`.
- `python -c "import director; print(len(director.PHASE_OUTCOMES), len(director.PROTOCOL_REPORT_KEYS))"`
  prints `3 6`.
- `python -c "import director,inspect; print(list(inspect.signature(director.replay_operation).parameters))"`
  prints `['base', 'operation_id']`.
- `python -c "import director; r=director.protocol_report([]); print(r['verdict'], len(r['steps']), r['out_of_order'])"`
  prints `incomplete 13 []`.
- `director.py` contains `def replay_operation(`, `def protocol_report(`.
- `replay_operation`'s docstring contains the phrase `reads the journal and
  nothing else`.
- Neither `director.py` nor `tests/director_roundtrip.py` contains an em dash
  character.
  </acceptance_criteria>
  <done>The thirteen protocol steps are a frozen, exactly-compared vocabulary,
  and one operation replays from the journal alone into a report that can
  fail.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: interruption at every phase, resume, and reverse</name>
  <files>director.py, fixtures/corpus_14b.py, tests/director_roundtrip.py</files>
  <read_first>
- `director.py` as it stands after Task 1, in full.
- `journal.py` as landed, in full: `commit_operation`'s ordered steps,
  `undo(base, entry_id, actor_kind, actor_name)`, `replay`,
  `rebuild_registry`, `object_state`, `LOCK_FILENAME`,
  `LOCK_TIMEOUT_SECONDS`, `BEFORE_DIRNAME`, and the `journal.busy` refusal
  code.
- `tests/journal_roundtrip.py` as landed, in full, especially its `--child`
  mode and however it spawns and kills a child process. This task copies that
  harness shape rather than inventing one.
- `tests/durability_roundtrip.py`, its `--writer` mode, for the second
  precedent of the same harness in this repository.
- `fixtures/corpus_14b.py` as it stands after plan 15A-04.
- `tests/director_roundtrip.py` as it stands after Task 1.
  </read_first>
  <behavior>
Assertions added to `tests/director_roundtrip.py` in a new
`check_resume_and_reverse()` function, written before the code.

Interruption at every phase:

- `fixtures.corpus_14b.build_interrupted_operation(dest, kill_after_phase)`
  spawns a child process that runs one full agent operation and exits abruptly
  immediately after recording the named phase, following the same spawn and
  kill harness `tests/journal_roundtrip.py` already uses.
- For each of the thirteen members of `director.PROTOCOL_STEPS`, running that
  fixture with that phase as `kill_after_phase` leaves a journal whose last
  `agent_operation` entry for that operation id names exactly that phase.
- For each of those thirteen runs, `director.resume_point(base, operation_id)`
  returns a dict with the keys `last_phase`, `next_phase`, `resumable`, and
  `reason`, where `last_phase` equals the killed-after phase and `next_phase`
  equals the following member of `PROTOCOL_STEPS`, or the empty string when the
  killed-after phase was the last one.
- When the killed-after phase is `report`, the final step, `resumable` is
  `False` and `reason` is `operation-complete`.
- For every other killed-after phase, `resumable` is `True`.
- No chat transcript, no session file, and no in-memory value is consulted:
  every one of these assertions is made in a fresh Python process that only
  opens the journal directory, asserted by running the resume check through
  `subprocess` rather than in the test process.

The empty case:

- A child killed before recording any phase leaves zero
  `agent_operation` entries for that operation id, and
  `director.resume_point` raises `DirectorError` with code
  `director.operation_unknown`.
- An operation whose only entry is `declare-intent` reports `resumable` `True`,
  `last_phase` `declare-intent`, and `next_phase` `declare-authority`, and
  `director.reverse_operation` on it is a no-op that appends one journal entry
  recording the reversal and changes no course bytes, because nothing durable
  had been written yet.

Reverse:

- `director.reverse_operation(base, operation_id, actor_kind, actor_name)`
  calls `journal.undo` for each entry of the operation that carries a
  non-null `undo` value, in reverse append order, and returns a dict with the
  keys `reversed_entries`, `restored_revisions`, and `complete`.
- After an operation that bound one treatment and was then reversed, the course
  sidecar bytes equal the bytes recorded before the operation began, compared
  byte for byte in the test.
- `director.py` contains no second restore path: asserted behaviorally by
  reversing an operation whose before-image file has been deleted from
  `_journal/before/` and confirming the call raises `JournalError` from
  `journal.undo` rather than reconstructing the content some other way.
- Reversing an already-reversed operation returns `complete` `True` and appends
  no further entries, the same idempotent-replay discipline `record_phase`
  follows.

Concurrency and the lock:

- With the journal lock held by a separate process, a `director` operation
  against the same course root refuses with `JournalError` code
  `journal.busy`, writes nothing, and leaves the sidecar bytes unchanged.
- Two child processes started together, each running one full operation against
  the same course root, produce a journal in which every entry parses, no two
  entries share an `entry_id`, and the sidecar's final content equals one of
  the two operations' outputs rather than a mixture, asserted by comparing
  against both expected byte strings.
- A child killed in the middle of a compare-and-swap write leaves the sidecar
  equal to either the pre-write bytes or the post-write bytes, never a third
  value.

One journal, still:

- No file under `journal.journal_dir(base)` other than the journal log, the
  registry, the lock, and the `before` directory exists after all thirteen
  interruption runs, unless `15A-DECISIONS.md` recorded `option-b` or
  `option-c` for `D-15A-2`, in which case the egress file it named is the one
  permitted addition and the test names it explicitly.
- `len(journal.OPERATION_TYPES)` is still `6` and `len(journal.ENTRY_KEYS)` is
  still `23`.
  </behavior>
  <action>
1. Add `check_resume_and_reverse()` to `tests/director_roundtrip.py` first,
   wired into `main()`, with every assertion above. Run and confirm it fails.

2. Add `build_interrupted_operation(dest, kill_after_phase)` to
   `fixtures/corpus_14b.py`, plus a `--child` mode entry point in that file's
   `__main__` block taking `--kill-after-phase` and `--root` arguments. Copy
   the spawn, wait, and kill mechanics from `tests/journal_roundtrip.py`'s
   existing `--child` harness rather than writing a new one; if that harness
   uses a different flag name, use its name and record the difference in the
   summary. All fixture content stays fictional and is generated from the
   existing fixed seed.

3. Implement `resume_point(base, operation_id)` in `director.py`. It calls
   `replay_operation`, takes the last recorded step in append order, sets
   `next_phase` from `PROTOCOL_STEPS` by index, sets `resumable` to `False`
   with reason `operation-complete` when the last recorded step is `report`,
   sets `resumable` to `False` with reason `no-checkpoint-recorded` when no
   phase is recorded at all, and otherwise sets `resumable` to `True` with an
   empty reason. It reads the journal and nothing else.

4. Implement `reverse_operation(base, operation_id, actor_kind, actor_name)`.
   It reads the operation's entries in append order, walks them in reverse, and
   calls `journal.undo(base, entry_id, actor_kind, actor_name)` for each entry
   whose `undo` value names a restorable before-image. It adds no restore path
   of its own, catches no `JournalError`, and returns the three-key report
   described in `<behavior>`. Its docstring states in plain sentences that a
   second restore path here would make the guarantee that any fault leaves the
   old or the new valid state depend on two implementations agreeing.

5. Re-run `python tests/director_roundtrip.py` until it passes. Then run
   `python tests/journal_roundtrip.py` and
   `python tests/durability_roundtrip.py` and confirm both still pass, which is
   the proof that the new kill fixtures did not disturb the existing ones. Then
   run `python itembank.py guard .`.
  </action>
  <verify>
  <automated>python tests/director_roundtrip.py</automated>
Expected: prints `OK director_roundtrip` and exits 0. Also run
`python tests/journal_roundtrip.py` and `python tests/durability_roundtrip.py`,
both expected exit 0. Degraded states this task proves: a kill at each of the
thirteen phases leaves a resumable record naming that phase; a kill before any
phase reports no-checkpoint-recorded rather than replaying a partial write; a
held lock refuses with `journal.busy` and writes nothing; and a kill mid-write
leaves either the old or the new bytes and never a third value.
  </verify>
  <acceptance_criteria>
- `python tests/director_roundtrip.py` exits 0 and prints `OK director_roundtrip`.
- `python tests/journal_roundtrip.py` exits 0.
- `python tests/durability_roundtrip.py` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `python -c "import director,inspect; print(list(inspect.signature(director.resume_point).parameters), list(inspect.signature(director.reverse_operation).parameters))"`
  prints `['base', 'operation_id'] ['base', 'operation_id', 'actor_kind', 'actor_name']`.
- `python -c "import journal; print(len(journal.OPERATION_TYPES), len(journal.ENTRY_KEYS))"`
  prints `6 23`.
- `director.py` contains `def resume_point(` and `def reverse_operation(`.
- `fixtures/corpus_14b.py` contains `def build_interrupted_operation(`.
- `git diff --name-only` after this task does not list `journal.py`,
  `identity.py`, `graph.py`, `course.py`, `model_adapter.py`, or any path under
  `surfaces/` or `schemas/`.
- None of `director.py`, `fixtures/corpus_14b.py`, or
  `tests/director_roundtrip.py` contains an em dash character.
  </acceptance_criteria>
  <done>An operation interrupted at any of the thirteen phases resumes or
  reverses from the journal alone, through the one undo mechanism, with no
  second restore path and no second log.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: the journal coupling test and the agent-disabled core loop</name>
  <files>tests/journal_roundtrip.py, tests/director_roundtrip.py, director.py</files>
  <read_first>
- `tests/journal_roundtrip.py` as landed, in full: its `fail(msg)` helper, its
  `check_*()` function convention, its `main()` wiring, and any existing
  assertion on `RECORD_TYPES` or `ENTRY_KEYS` membership or length. The new
  function follows that file's own conventions exactly.
- `journal.py` as landed: `RECORD_TYPES`, `ENTRY_KEYS`, `append_entry`,
  `entries`, and whatever validation `append_entry` performs on an unknown key
  or an unknown record type.
- `director.py` as it stands after Task 2, in full, especially
  `AGENT_ENTRY_KEYS` and `AGENT_RECORD_TYPE`.
- `15A-RESEARCH.md`, the "Wave 0 Gaps" list, which names this addition and
  leaves its owner open. This task is the answer.
- `tests/director_roundtrip.py` as it stands after Task 2.
  </read_first>
  <behavior>
Assertions added to `tests/journal_roundtrip.py` in a new
`check_agent_operation_record()` function, and to
`tests/director_roundtrip.py` in a new `check_protocol_edges()` function, both
written before the code.

The journal coupling check, in `tests/journal_roundtrip.py`:

- `"agent_operation"` is a member of `journal.RECORD_TYPES`.
- `"agent"` is the last member of `journal.ENTRY_KEYS`, and `ENTRY_KEYS` has
  exactly twenty-three members.
- `journal.OPERATION_TYPES` still has exactly six members, and
  `"agent_operation"` is not one of them. An agent operation is a record type,
  not a file operation.
- An entry appended with `operation` equal to `"agent_operation"` and a well
  formed `agent` dict round-trips through `journal.append_entry` and
  `journal.entries` with its `agent` dict equal, key for key and value for
  value.
- An entry whose `agent` value is `None` round-trips as `None`. The key is
  optional in value, not in presence.
- The `agent` dict's key set is checked against `director.AGENT_ENTRY_KEYS` by
  importing `director` inside the test function, so the two vocabularies cannot
  drift without this file going red. The import is local to the function so the
  rest of `tests/journal_roundtrip.py` still runs if `director.py` is absent.
- An entry whose `operation` is a string not in `journal.RECORD_TYPES` is
  refused by `journal.append_entry` exactly as it was before this phase, proven
  by asserting the same refusal code the file already asserts elsewhere.

The AGENT-01 edges, in `tests/director_roundtrip.py`:

- Adjacency: two `record_phase` calls in one operation with the same phase name
  and different indices raise `director.duplicate_phase`; the same phase name
  under two different operation ids both succeed and produce two entries whose
  `agent.operation_id` values differ.
- Empty: `director.replay_operation` against a base whose journal has entries
  but none of type `agent_operation` raises `director.operation_unknown`.
- Encoding: the three rejected spellings from Task 1 are asserted again here as
  a regression fence, plus a phase name with a trailing space and one with a
  non-breaking space, both raising `director.unknown_phase`.
- Ordering: journaling `report` before `accept` produces a report listing them
  at indices 12 and 11 respectively and naming both in `out_of_order`.
- Idempotency: running one complete operation, then running
  `record_phase` again for every one of its thirteen phases with identical
  indices, leaves `len(journal.entries(base))` unchanged and returns
  `already_recorded` thirteen times.

The core loop with the agent disabled:

- With `settings["model_backend"]["profiles"]` set to an empty list, a fresh
  process can still: read a course sidecar with `course.read_course`, write it
  with `course.write_course`, bind a treatment with `course.bind_treatment`
  acting as a human actor, replay a previously recorded operation with
  `director.replay_operation`, and reverse it with
  `director.reverse_operation`. None of those five calls reaches
  `model_adapter.invoke`.
- With the same empty profile list, `python tests/scoring_roundtrip.py`,
  `python tests/evidence_roundtrip.py`, and `python tests/protocol_roundtrip.py`
  all exit 0, run as subprocesses from within the test.
- `director.recommend_treatments` with an empty profile list returns one
  untreated entry per objective with the adapter code
  `adapter.profile_disabled`, writes no binding, and raises nothing.
  </behavior>
  <action>
1. Add `check_agent_operation_record()` to `tests/journal_roundtrip.py` and
   `check_protocol_edges()` to `tests/director_roundtrip.py` first, both wired
   into their files' `main()` functions, with every assertion above. Run both
   and confirm both fail.

2. Write `check_agent_operation_record()` following
   `tests/journal_roundtrip.py`'s own existing `check_*()` conventions exactly:
   the same `fail(msg)` calls, the same temp-directory setup and teardown, and
   the same style of message. Import `director` inside the function body, not
   at module scope, so this file still runs when `director.py` is absent. Add
   the function's call into that file's `main()` in the position that keeps the
   file's existing ordering convention.

3. Write `check_protocol_edges()` in `tests/director_roundtrip.py` with the
   five AGENT-01 edge groups and the agent-disabled core-loop group. Run the
   three shipped suites as subprocesses with
   `subprocess.run([sys.executable, os.path.join(ROOT, "tests", name)], ...)`
   and assert each `returncode` is `0`, naming the failing suite in the
   `fail(msg)` message.

4. If any assertion in step 2 or step 3 exposes a real defect in
   `director.py`, fix `director.py` rather than weakening the assertion, and
   record the fix in the summary. In particular, confirm that
   `recommend_treatments` with an empty profile list returns entries rather
   than raising, and fix it here if it does not.

5. Re-run `python tests/journal_roundtrip.py` and
   `python tests/director_roundtrip.py` until both pass. Then run the wave
   check: every file in `tests/` in one pass with
   `for t in tests/*.py; do python "$t" || exit 1; done`, expected to exit 0.
   Then run `python itembank.py guard .`.
  </action>
  <verify>
  <automated>python tests/journal_roundtrip.py && python tests/director_roundtrip.py</automated>
Expected: both print their OK lines and exit 0. Also run the full suite with
`for t in tests/*.py; do python "$t" || exit 1; done`, expected exit 0.
Degraded state this task proves: with every model backend profile removed, five
named core operations still work in a fresh process and three shipped suites
still pass, so an unavailable agent leaves the core loop fully operable.
  </verify>
  <acceptance_criteria>
- `python tests/journal_roundtrip.py` exits 0.
- `python tests/director_roundtrip.py` exits 0 and prints `OK director_roundtrip`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `tests/journal_roundtrip.py` contains `def check_agent_operation_record(`.
- `tests/director_roundtrip.py` contains `def check_protocol_edges(`.
- `python -c "import journal; print('agent_operation' in journal.RECORD_TYPES, 'agent_operation' in journal.OPERATION_TYPES, journal.ENTRY_KEYS[-1], len(journal.ENTRY_KEYS))"`
  prints `True False agent 23`.
- `git diff --name-only` after this task does not list `journal.py`,
  `identity.py`, `graph.py`, `course.py`, `model_adapter.py`, or any path under
  `surfaces/` or `schemas/`.
- None of `director.py`, `tests/journal_roundtrip.py`, or
  `tests/director_roundtrip.py` contains an em dash character.
  </acceptance_criteria>
  <done>The agent_operation record type has a coupling test living beside the
  journal it extends, the AGENT-01 edges are fenced, and the core loop is
  proven operable with every backend removed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| journal file to replay | A file that survived a crash, or was edited outside the tool, is read back as the authoritative record of what an operation did. |
| interrupted process to next process | A second process resumes or reverses work a dead process started. |
| two concurrent operations to one course root | Two writers contend for one compare-and-swap lineage. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-15A-05-01 | Repudiation | an operation whose record depends on a chat transcript or an in-memory object | high | mitigate | `replay_operation` takes exactly two parameters and reads only `journal.entries`, asserted by signature introspection, and the resume assertions run in a fresh subprocess that opens only the journal directory. |
| T-15A-05-02 | Tampering | a mixed or partial state surviving a kill mid-write | high | mitigate | Inherited from `journal.commit_operation`'s compare-and-swap and atomic replace, exercised here by killing a child at each of the thirteen phases and asserting the sidecar equals either the pre-write or the post-write bytes and never a third value. |
| T-15A-05-03 | Elevation of Privilege | two concurrent operations both writing one course root | high | mitigate | The journal lock refuses the loser with `journal.busy`; the concurrent-child scenario asserts the final content equals one of the two expected outputs rather than a mixture. The residual risk that some interleaving exists which the fixture does not reach is recorded as this plan's backstop truth. |
| T-15A-05-04 | Spoofing | a phase name spelled differently reading as a satisfied protocol step | high | mitigate | Comparison is exact ASCII equality against the frozen thirteen-token tuple, with case, separator, prefix, trailing-space, and non-breaking-space variants each asserted to raise `director.unknown_phase`. |
| T-15A-05-05 | Repudiation | a step reported as satisfied that never happened | high | mitigate | A `recorded` outcome requires a non-empty `entry_id` matching a real journal entry, and a `not-applicable` outcome requires a non-empty reason. An absent step is `missing` and makes the verdict `incomplete`. |
| T-15A-05-06 | Spoofing | an agent self-certifying accessibility through the preview step | high | mitigate | The `preview` step is always `not-applicable` with a fixed reason naming 16B as the owner and stating that accessibility is never self-certified. The reason string is asserted verbatim. |
| T-15A-05-07 | Tampering | a second undo mechanism disagreeing with the journal's | high | mitigate | `reverse_operation` calls `journal.undo` and catches no `JournalError`; deleting a before-image makes the call raise rather than reconstructing content some other way, which is the behavioral proof that no second path exists. |
| T-15A-05-08 | Tampering | a second append-only operation log appearing under the journal directory | high | mitigate | The interruption scenario asserts the journal directory's file set after thirteen runs, permitting only the log, the registry, the lock, the before directory, and whichever egress file `D-15A-2` explicitly authorized. |
| T-15A-05-09 | Denial of Service | a lock held by a dead process blocking every later operation | medium | mitigate | Inherited from `journal.LOCK_TIMEOUT_SECONDS`, the ten-second bound 14A-02 already ships, after which the caller gets `journal.busy` rather than hanging. This plan adds no new locking. |
| T-15A-05-10 | Tampering | supply chain: a workflow engine, job queue, or state machine library introduced here | high | mitigate | None is added; the whole replay is a tuple walk over a list of dicts read from one JSONL file. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is not itself the mitigation: any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No second journal, no second append-only log, no in-memory job tracker, no
  file matching `*_journal.py` or a second `*.jsonl` under the journal
  directory beyond whatever `D-15A-2` explicitly authorized.
- No further change to `journal.py`. Its whole-phase diff stays the two lines
  plan 15A-01 added.
- No fourteenth protocol step, no synonym table, no alias map, no case-folding
  comparison.
- No cross-client job protocol, no agent job queue, no resumption across
  machines. `PLANNING-DIRECTIVES.md` section 3a names cross-client interruption
  as a prototype owed before an agent job protocol freezes, and this phase is
  not that freeze.
- No CLI command and no daemon route for replay, resume, or reverse.
- No evidence read, no evidence write, no evidence transfer.
- No fourth synthetic domain and no freeze record. Plan 15A-06 owns both.
- No accessibility certification of any kind. The preview step is recorded
  not-applicable with its reason, and that is the whole of this phase's
  position on it.
</out_of_scope>

<summary_obligations>
`15A-05-SUMMARY.md` records: the thirteen `PROTOCOL_STEPS` tokens as landed;
the flag name the existing `--child` harness actually uses, if it differed from
this plan's `--kill-after-phase`; which of the thirteen interruption runs, if
any, needed a fix in `director.py` and what it was; the measured wall-clock time
of one full `tests/director_roundtrip.py` run and one full-suite run; the exact
file set found under the journal directory after the thirteen interruption
runs; the backstop truth's residual risk restated in one sentence with whatever
evidence the concurrency fixture actually produced; and any deviation from this
plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/15A-director-treatment-policy/15A-05-SUMMARY.md`
when done.
</output>
</content>
