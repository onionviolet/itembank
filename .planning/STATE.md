---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase_name: 17B-production-vertical-tracer
status: "Phase 15B is FROZEN (2026-08-30). All seven plans executed. `blueprint.py` ships ACTIVITY-02's five-gate architecture, RELIABILITY-03's staleness discipline, the cited course audit that mints no fourth coverage vocabulary, and AGENT-03's proposal record. `graph.accept_migration` and `graph.reject_migration` close the acceptance gap 14B left open and named 15B as owner of. `15B-FREEZE.md` opens `## Frozen at 15B` and all three legs hold: the acceptance tracer 7 passed 0 skipped 0 failed, the review accept-with-concerns, and Phase 13.9 walked. Full suite 100 files, 884 seconds, 0 failures; guard 0 offending files. FIVE consecutive phases (16A, 16B, 16C, 15A, 15B) have closed their review leg with an AGENT signature, and 15A plus 15B added six one-way agent-made decisions between them, one of which amended `14B-FREEZE.md`. Frozen: 14A, 14B, 14C, 15A, 15B, 16A, 16B, 16C. Open: 17A-04, all of 17B, 17C, 18, and the paced-lesson subphase whose plan is unwritten."
stopped_at: "Phase 15B is closed and the 15A/15B chain is complete. What still needs Weibao and cannot be agent-executed: 17A-04 Task 1, which needs the LGPL browser-driver supply-chain decision and an A11Y-01 review (an agent never self-certifies accessibility, and that one was NOT waived). The standing question, now five phases old: 16A, 16B, 16C, 15A and 15B have all closed their human-review leg with an agent signature, and 15A plus 15B additionally had an agent answer six one-way design questions their plans reserved for Weibao, one of which changed a published schema and one of which amended another phase's frozen record. Every waiver is recorded with its reversal cost in the phase DECISIONS files, but the pattern deserves one decision rather than five inherited defaults. Next executable phase work: 17B, 17C, or 18; 17A-04 blocks the rest of 17A."
last_updated: "2026-08-30T00:00:00.000Z"
last_activity: 2026-08-30
last_activity_desc: "Executed 16C-01 through 16C-09 Task 1. Five new root modules (notes, strategies, progress_claims, note_outputs, upgrade_audit), one published schema, two additive evidence event types proven additive against pre-change baselines, eight new test suites, and the legacy-upgrade skill un-stubbed. Four defects were found by running rather than by reading: the two new event types failed the project's own published event schema and would have shipped into an append-only log; the .agents and .claude skill mirrors had been divergent since 13.9 and 14C-06 so CI's mirror step was red on main; a TERMS header row parsed as a glossary entry; and two records still called legacy-upgrade a stub after it shipped. One pre-existing red test, selection_retention_roundtrip, was bisected to its own introducing commit and recorded rather than absorbed. On 2026-08-30 that test was diagnosed and made green: its CLI leg dated a fixture near a fixed CUTOFF but is captured against the wall clock, so the weak and mastered objectives decayed to an equal weight of 1.0 and Phase 7 ordering settled the sitting. The leg now re-dates its fixture by one identical offset and asserts the invariant rather than a date; no runtime file changed. Also on 2026-08-30: tests/file_fault_tracer.py no longer rewrites 14A-TRACER-REPORT.md on every run, which had made a durable phase record derived and had already cost three commits; it now compares everything that carries meaning and writes only under --write, and a new CI step asserts the suite leaves the working tree clean, verified by a full 96-file run that left git status empty. That open finding is now closed and was not one bug but three. Reproduced at twelve concurrent requests under load, 20 rounds of 20 failing: runtime.write_session used a shared <target>.tmp, so the first os.replace consumed the temp file and the second raised FileNotFoundError, which reached the learner as the 400; _ensure_quiz_session checked and created outside any lock, so six concurrent first hits left six sittings for one bank and kept whichever finished last; and Daemon inherited the stdlib listen backlog of 5, measured as ConnectionResetError past twelve connections and not at six. All three fixed, 0 of 20 rounds failing after, with one session where there were six. Also closed: fake_hosted_unused.py, a test artifact committed as source in 46f0f50 because hosted_profile("") wrote its fake script into the process cwd; the root .continue-here, which had pointed for months at a Phase 09 branch, worktree, and main tip that no longer exist; and two orphaned test processes from 2026-08-28, one of them a fake AnkiConnect squatting on 127.0.0.1:8765, the real AnkiConnect port, so day's Anki lane on this machine had been answering to a stub. The GSD client install under .codex/ is gitignored as tool state, like reasonix.toml."
progress:
  total_phases: 28
  completed_phases: 22
  total_plans: 175
  completed_plans: 152
current_phase: 17B
---

# Project State

## 2026-08-30 (sixth entry): Phase 15B executed and frozen, seven plans

The 15A/15B chain is complete. What it cost in authority is recorded first,
because it is the part a green suite does not show.

### What an agent decided and signed that Weibao was meant to

Phase 15B added **four one-way checkpoint decisions** answered by an agent
(D-15B-1 through D-15B-4) and **one blocking human review** signed by an agent.
Combined with 15A's two decisions and one review, that is six one-way decisions
and two reviews across the two phases, on top of 16A, 16B and 16C's three
reviews.

**Five consecutive phases have now closed their human-review leg with an agent
signature.** D-15B-2 additionally **amended a frozen record**: `14B-FREEZE.md`
carries a dated amendment because `graph.SECTION_ORDER` gained `"Blueprint"`.
Every one is recorded with its reversal cost, and every plan's own text said to
ask Weibao. The pattern deserves one decision from him rather than five
inherited defaults.

### What shipped

`blueprint.py`, a pure classifier importing only `model` and `runtime`, so
`hasattr` is False for `journal`, `course`, `evidence`, `director`, `graph`,
`auditor` and `authoring`. The absent imports ARE the contract: a module that
imports `journal` cannot assert it never writes.

ACTIVITY-02's five gates, with three of the eight blueprint dimensions
checkable from a parsed bank and five supplied as facts; an unsupplied fact is
`warn`, never a silent pass. RELIABILITY-03's staleness, where an absent
fingerprint reads STALE and a disposition carries the fingerprint it was
recorded against so reconciliation is per change. A cited course audit whose
`COVERAGE_VOCABULARIES` holds vocabulary NAMES rather than states, which is the
whole mechanism preventing a fourth. AGENT-03's proposal, where uncertainty is
a band because a figure invites division and a division over sparse evidence is
the mastery percentage the requirement forbids.

`graph.accept_migration` and `graph.reject_migration` close the gap 14B left
open, and `graph.set_migration_state` stays and still refuses, so the count of
ways to settle a proposal went from zero to two rather than becoming unbounded.

### Defects found by running rather than reading

1. **`director.accept_revision` authorized the policy against itself.** It
   called `authorize_write(settings, autonomy_level(settings), 1)`, comparing
   the policy to itself, so the check could never refuse. It looked like a
   check and was not one. It declares the WRITE level now.
2. **The packaged `.pyz` was broken.** `authoring.py` imports `blueprint` at
   module scope and `build.py` stages an explicit allowlist that omitted it, so
   the artifact raised ModuleNotFoundError on startup. `build.py`'s own
   comments record this class of gap twice before, each noting the omission
   stayed invisible until a surface imported the module. Checking the rest
   found `director.py` and 16C's five modules unstaged for the same reason and
   not yet failing; all six are staged alongside.
3. **Two fixture items failed shipped Phase 11 detectors.** Every distractor
   lacked a would-be-correct clause, and one stem quoted its own answer
   verbatim. Both were real defects, both caught by code this phase did not
   write, and both are recorded in the tracer report as evidence about the
   gate: the conforming set was written by the same agent that wrote the gate.
4. **The freeze record's own shape check caught a hazard in the record.** The
   Evidence section quoted the literal withholding heading in prose, and a
   downstream precondition greps these files for exactly that string. Rewritten
   to describe it rather than quote it.

### Two claims weakened to what is true rather than asserted falsely

- Adding two columns to the Migrations table changes that table's header, so a
  pre-15B sidecar no longer round-trips byte-identically. The test asserts the
  precise claim instead: exactly four diff lines, all in the Migrations header,
  no data row and no other section touched.
- An empty question set has no denominator, so every share check is skipped
  rather than reporting "0 percent observed" as a measurement of something
  never measured. The same reasoning GRAPH-03 applies to an indeterminate
  claim.

### One piece of bookkeeping that went wrong four times

`BLUEPRINT_CODES` grew 13 to 14 to 19 to 21 to 24 across four plans, and **each
plan's artifacts section counted from the thirteen it inherited rather than
from what landed**. The code is right and the plan set is wrong in four places.
`15B-FREEZE.md` is now the authority for that number.

### Measured

Acceptance tracer 31.9 s, 7 passed 0 skipped 0 failed. 28 journal entries, 6
replayed from a fresh process, 5 of 5 gates passed, 4 of 4 dispositions cleared
a block, 2 settlements, proposal denominator 2 reading `sparse`. Full suite 100
files, 884 seconds, 0 failures. Guard 0 offending files. Darwin 27.0.0 arm64,
Python 3.14.6.

## 2026-08-30 (fifth entry): Phase 15A executed and frozen, six plans in one session

Weibao's instruction was to finish Phase 15A without him. It is finished and
frozen. What it cost in authority is recorded first, because it is the part
that does not show up in a green suite.

### What an agent decided that Weibao was meant to

Three gates, all waived, all recorded rather than quietly passed:

- **D-15A-1**, the recommendation wire boundary, rated **one-way**. Chose
  `option-a`, a fourth `model_adapter` operation. This changes
  `schemas/model_adapter.schema.json`, a published contract 15B and any
  external agent client build against.
- **D-15A-2**, where the egress record lives, rated **one-way**. Chose
  `option-a`, one dict-valued journal key.
- **15A-06 Task 2**, the blocking human review of recommendation quality. The
  plan's own text says "an agent never signs it for itself". An agent signed
  it.

Both decisions took the plan's recommended default, and in both cases the
alternatives are excluded by rules the project already wrote down rather than
by an agent's preference. That is what made them worth taking rather than
stopping the wave. It is not the same as Weibao having chosen them.

**This is the fourth consecutive phase to close a review leg with an agent
signature** (16A, 16B, 16C, now 15A), and 15A is the heaviest: the other three
asked whether shipped copy reads honestly, this one asked whether a
course-design judgment is any good. Four is a pattern. It belongs in front of
Weibao as a decision rather than as an accumulated habit.

### What shipped

`director.py`, the agent-client tier, about 1600 lines. Sixteen closed
vocabularies, fifteen typed codes, twenty-eight public functions.
`schemas/treatment_recommendation.schema.json`. A fourth adapter operation. Two
journal lines. A `settings.agent_policy` block. Four new fixture builders, a
mock backend reachable three ways, and two test files.

The boundaries are structural rather than maintained by care. `director.py`
does not import `tier_gate`, `evidence`, `runtime`, or `model`, and a test
asserts `hasattr` is False for all four. `replay_operation` takes exactly a
root and an operation id, so a passing replay proves the journal is the durable
job record rather than that a process remembered its own work.
`apply_recommendation` takes no rights argument and computes its own coverage
state, so no parameter exists through which a stale right or a self-certified
claim could authorize a write. `authorize_write` returns `None`, so there is no
value a caller could mistake for a grant.

### Five defects found by running rather than by reading

1. **15A-01 contradicted itself.** It asks for a distinct
   `director.unknown_treatment_kind` and also makes `treatment_kind` a closed
   schema enum, so the schema always fires first and that code is unreachable.
   Resolved by classifying the failure after validation returns, and only when
   the kind is the sole failure.
2. **`apply_recommendation` was adopting the provider's `coverage.state`.**
   Found by reading the four subjects' recommendations as prose, not by any
   assertion. A model certifying its own coverage is what AGENT-02 forbids and
   what 15A-03's own decision table rules out by name. Now computed locally.
3. **A tracer assertion that was true and nearly worthless.**
   `scenario_coverage_states` asserted only that every state produced was a
   member of the vocabulary, and passed. The measured line then read
   `['thin']`: one state out of five. Only the measurement showed it.
4. **`journal.undo` raises a bare `FileNotFoundError`** when a before-image is
   missing, in a module whose whole discipline is typed codes. Not fixed:
   15A-05's acceptance criteria forbid touching `journal.py`. Asserted as-is
   with the defect named, and carried.
5. **`tests/retention_roundtrip.py` was red on a clean tree**, the third time
   in this family. A fixture pinned to August 2026 read against the wall clock,
   so `weak` aged into `at-risk`. 16B fixed two call sites; six more still read
   the clock. All now use one named `CUTOFF`.

### Three shipped tests that conflated additive with regressive

Each asserted a count or a digest that could not tell an additive extension
from a regression, and each is fixed to assert what it meant rather than
loosened:

- `tests/graph_roundtrip.py` asserted `len(RECORD_TYPES) == len(OPERATION_TYPES)
  + 5`. Now names the five 14A record types and the six file operations.
- `tests/config_roundtrip.py` counted every settings key as pre-existing, so
  any later additive key failed an additivity test by being additive.
- `tests/note_promotion_roundtrip.py` checks a byte digest of
  `settings.schema.json` against 16C's frozen baseline. The baseline is **not**
  re-recorded, because re-recording makes the proof circular. The check now
  reconstructs the baselined document by stripping keys added after it, and the
  digest comes back exactly, which **proves** the change was additive rather
  than asserting it.

`surfaces/visual_fixture.py` also needed a learner-facing phrase for the new
record type: `agent_operation` reads "an agent worked on", and is deliberately
not undoable, because it writes no bytes of its own.

### Measured

Four-subject pass 0.377 s. Whole freeze tracer 17.769 s, 8 passed 0 skipped 0
failed. 191 journal entries, 16401 payload bytes across the run, largest single
payload 907 bytes, 5 spans approved and 1 omitted, 19 objectives, outcomes 8
bound / 7 untreated / 4 refused. Full suite 98 files, 313 seconds, 0 failures.
Guard 0 offending files. Darwin 27.0.0 arm64, Python 3.14.6.

## 2026-08-30 (fourth entry): both stops cleared, 16C frozen, 15A unblocked

Weibao's instruction was to bypass his review and proceed toward the user
vision. Both of the day's stops are now closed, and the two closures are
different in kind: one was a judgment an agent made under an explicit waiver,
the other was arithmetic an agent should always have been allowed to do.

### 16C is frozen, and the review leg is waived rather than met

`16C-REVIEW.md` records `accept-with-findings`. It was written by Claude, not
by Weibao, under his explicit instruction of 2026-08-30. Plan 16C-09's first
prohibition, "An agent must not sign its own contract", is **waived by the
learner who owns the gate, not satisfied**, and the review, the freeze record,
`16C-DECISIONS.md`'s D-16C-9, and `16C-VALIDATION.md` all say so in those
words. This is the **third phase in a row** in that state: 16A and 16B closed
the same leg the same way under a standing delegation of 2026-08-28. That is
now a pattern rather than an exception, and it is recorded here so it is
decided deliberately rather than by accumulation.

`16C-VALIDATION.md`'s sign-off box for the human review is **left unticked on
purpose**, and its Per-Task Verification Map marks `16C-09-T2` as a new
`waived` status rather than forcing it into `green`. The freeze leg the plan
actually states (a signed review whose verdict is accept or
accept-with-findings) is satisfied; the box as worded, which says `human`, is
not. Ticking it would have hidden the difference.

**The review was not a rubber stamp.** It raised seven findings and withdrew an
eighth. The withdrawal is the useful part: a first pass read
`note_outputs.VALIDATOR_FAILURE_COPY` and `NOTE_OUTPUT_CHECKS` side by side and
concluded the trio's refusals rendered dotted machine codes at learners.
Rendering them through `render_mode` showed they do not, because
`validate_mode` puts the plain phrase in the `check` key and the dotted code in
`code`. The real sentence reads "The Cornell notes view can't be built from
this content: a cue has no matching notes. Showing plain Markdown instead."
Judging copy from a constant rather than from what a learner would see is
exactly the error the checkpoint exists to catch, and it was caught in the
right direction only because the sentences were actually rendered.

**One finding generalizes past 16C.** Two findings in `16B-REVIEW.md` named
Phase 16C as their owner, and 16C closed neither: `surfaces/ia.py:449` still
reads `"needs_reconciliation": "Needs reconciliation"`, and Loop B's empty
outcome at `surfaces/ia.py:1403` still uses "treatment" in the course-design
register. Both are reassigned to 17A in the freeze record. **A finding whose
owning phase freezes without closing it has no owner unless somebody reassigns
it**, and this one was found only because this review read the previous review.
17A's planning should read `16B-REVIEW.md` and 16C's findings table together.

**The evidence was re-run rather than trusted**, per Task 3's own instruction,
because the review sits between Task 1's run and the freeze:

```
CROSS-SUBJECT SUITE: 9 passed, 0 failed      elapsed: 0.274s
python3 itembank.py guard .                  0 offending files
full suite                                   96 files, 284 seconds, 0 failures
```

All five additivity baselines in `16C-PRECONDITION.md` recomputed identical.
`tests/selection_retention_roundtrip.py`, red in Task 1's run, passes here: it
was the clock-dependent fixture fixed earlier the same day. All nine
freeze-gate fixture rows read `passed`; none reads `weaker proof` and none
reads `not run`.

### 15A was one stale number, and `rights` stays

The halt was correct and the fix is arithmetic. `journal.ENTRY_KEYS` has held
**twenty-three** members since `77b27e9`, the only commit that ever touched it,
so there was never a moment when it had twenty-two. Two planning records
disagree: `14A-02-PLAN.md` lists twenty-two ending in `message`,
`14A-FREEZE.md` lists twenty-three ending in `rights`. 15A-01 step 2 was
written from the plan text exactly as its own `read_first` block instructed.
**The instruction was the defect**: a plan is a proposal, a freeze record is
accepted truth, and where they disagree the freeze record wins. That pointer is
now repointed at `14A-FREEZE.md`.

`rights` stays. Every 15A number shifts by one and nothing else changes:
`15A-01-PLAN.md` asserts a pre-state of 23 and an acceptance of 24 with `agent`
last and the first twenty-three unchanged; `15A-05-PLAN.md`'s two checks read
24; `15A-VALIDATION.md`'s row reads 23. Plans 02, 03, 04 and 06 were grepped
and carry none of these numbers.

**The two-line diff claim survives untouched.** 15A-01's `must_have` says
`journal.py`'s whole-phase diff is one new `RECORD_TYPES` member and one new
`ENTRY_KEYS` member. That was never a claim about the total count, so a
pre-state of 23 does not touch it. Had an executor taken the plan literally
instead of halting, the only way to satisfy "exactly twenty-three, `agent`
last" against a landed twenty-three-key tuple would have been to **delete
`rights`**, the key 14A-03 records the rights state of every journal entry
through. The halt prevented deleting a frozen key to satisfy a stale count.

All five precondition steps were then re-run in full and every one passes.
`15A-PRECONDITION.md` records the check, the deviation, the resolution, and the
root cause. `director.py` still does not exist; 15A proceeds from 15A-01
Task 2.

## 2026-08-30 (third entry): 15A-01 ran its precondition and halted, correctly

With the loose ends closed, the open phase work was checked for what an agent
may actually execute. Three of the four items are not agent work, and the
fourth halted by design.

**17A-04 is not executable.** Task 1 needs a supply-chain decision no agent may
make: no approved browser driver exists, `17A-RESEARCH.md` recommends a pinned
Playwright harness, and its ffmpeg component is LGPL, which
`SUPPLY-CHAIN-POLICY.md` section 2.4 routes to Weibao. The packet with both
options argued is `.planning/DECISIONS-17A04-DRIVER-2026-08-25.md`. Task 2 is
his A11Y-01 review either way. Unchanged, restated here because it was checked
rather than assumed.

**15B cannot start before 15A.** `15B-01`'s precondition halts by name until a
`15A-FREEZE.md` exists. There is none.

**15A-01 Task 1 was executed. It halts.** This is the only piece of open phase
work an agent could legitimately advance, and its first task is an `auto`
precondition check whose whole purpose is to refuse the phase if 14A and 14B
did not land with the surface 15A was planned against.

Steps 1, 3, 4 and 5 pass: the six modules import; the whole 14B surface matches
including `course.COURSE_SIDECAR_FILENAME == "course-graph.md"` under the
confirmed D-14B-1 option-a; `model_adapter` reports exactly
`14 ['hosted_cli', 'openai_compatible']`; and both freeze records carry their
headings.

Step 2 diverges on one item, checked to completion rather than stopped at the
first failure so the record is whole:

```
HALT 15A-01 precondition: Phase 14A or Phase 14B has not landed, or its frozen
surface differs from what Phase 15A was planned against. Re-verify every 15A
plan against .planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md
and .planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md before
writing any code. Divergent or missing: len(journal.ENTRY_KEYS): landed 23,
plan text 22
```

**What the divergence is, and why the halt is right rather than pedantic.**
`journal.ENTRY_KEYS` has twenty-three members and ends in `rights`. It has held
twenty-three since the only commit that ever touched it, `77b27e9`, so this is
not a regression and nothing drifted. The two numbers come from two records:
`14A-02-PLAN.md` lists twenty-two keys ending in `message`, and
`14A-FREEZE.md` lists twenty-three ending in `rights`. 15A-01 step 2 was
written from the plan text, exactly as its own `read_first` block instructs,
and the plan text is the pre-freeze number.

That is the Critical Caveat in `15A-RESEARCH.md` arriving on schedule: every
14A and 14B signature in 15A's research and pattern map was read from plan
text, because the modules did not exist when 15A was planned. The precondition
exists to catch that, and it caught it on its first real assertion.

The consequence is not bookkeeping. 15A-01's own acceptance says
`journal.ENTRY_KEYS` must have "exactly 23 members, its last member `agent`,
and its first twenty-two members unchanged", and its must_have says the whole
phase's `journal.py` diff is exactly two lines. Against a landed
twenty-three-key tuple, an executor working literally could satisfy that count
only by deleting `rights`, silently removing the rights field from every
journal entry 14A-03 records. A halt that prevents that is worth more than a
phase started a day earlier.

**What is needed, and from whom.** Not an executor: a planning pass that
re-reads 15A-01 through 15A-06 against `14A-FREEZE.md` and `14B-FREEZE.md`
rather than against 14A and 14B plan text, and restates the ENTRY_KEYS
assertions, the acceptance count, and the two-line diff claim in terms of what
is frozen. Whether `rights` stays and how the "exactly two lines" claim is
re-derived is a planning call, not an executor's, so nothing was amended here.

**Nothing was written.** Per step 6, no module, no `15A-PRECONDITION.md`, and
no reduced check set. `director.py` does not exist. The plan's own instruction
is quoted rather than paraphrased: "A halt here is the correct outcome; it is
what this task is for."

Suite: 96 of 96 on the committed tree, which the suite leaves clean.


## 2026-08-30 (second entry): the flake was three defects, and the daemon was serving a stub

The one open finding the earlier entry recorded rather than patched is closed.
It was right not to guess: the guess in that entry was wrong.

**Reproduced first, diagnosed second.** `check_concurrency` fires concurrent
`GET /quiz/sample_bank` requests at one daemon. A repro harness that read the
error body the test discards, run under six busy cores, failed 20 rounds of 20
at twelve concurrent requests and 0 of 12 idle at six. The body named the
failure outright, which is why a day of "cause unknown" was avoidable: the test
threw the diagnosis away and kept the status code.

**Defect one, and the 400 itself.** `runtime.write_session` wrote through a
shared `target + ".tmp"`. The daemon mixes in `ThreadingMixIn`, so two requests
can write one session file at once; the first `os.replace` consumed the temp
file and the second raised `FileNotFoundError` on the path it had just written,
which `handle_quiz_get` converted into `400 Bad Request`. The temp name now
carries a per-write nonce and still ends in `.tmp`, so every leftover sweep that
matches `endswith(".tmp")` still sees these, and a failed write removes its own
temp file. Last-writer-wins on content is unchanged and is still the caller's
problem; what is fixed is one writer destroying another's in-flight file.

**Defect two, which no assertion had ever looked for.** `_ensure_quiz_session`
read `api_session_id`, found it unset, and ran `session.do_start`, all outside
any lock. Six concurrent first hits on a fresh daemon therefore produced six
session files under `_attempts/` for one bank, with `cfg["api_session_id"]`
left pointing at whichever thread finished last and five sittings orphaned with
their evidence attached to them. Measured, not inferred: the repro printed
`sessions=6` on every clean round before the fix and `sessions=1` on every round
after. The check and the create are now one decision under a new module-level
`QUIZ_SESSION_LOCK`, deliberately not `quiz_state_lock`: that one guards short
in-memory critical sections over the token and flash stores, and sharing it
would make every token mint wait on a sitting being created. Module-level
rather than a handler attribute because `tests/serve_roundtrip.py` and
`tests/model_phase_roundtrip.py` call this function with a stand-in handler,
which should not have to know a lock lives on the handler class.

**The backlog was real, and was not the bug.** The earlier entry's lead was that
`Daemon` inherits the stdlib `request_queue_size` of 5 while the test opens 6
connections. That is true and it is now set explicitly to 64, but it produces
`ConnectionResetError(54)`, not a 400, and it was not reached at six. It only
appeared at twelve. A backlog bump alone would have made the flake rarer and
left both real defects in place, which is exactly what that entry declined to do.

**The test now keeps what it needs.** `check_concurrency` reads the error body,
runs twelve threads rather than six, asserts one bank yields one session, and
asserts no temp files are left behind. A new `check_session_write_concurrency`
hammers `runtime.write_session` from eight threads directly, because the route
now serializes creation and would pass with the collision still in place; it was
verified in both directions by restoring the shared temp name, which fails it
with the original `FileNotFoundError`. The daemon suite is 78 checks, from 77.

**`fake_hosted_unused.py` was the same shape as the 14A tracer, committed.**
`tests/model_adapter_roundtrip.py` built one profile with `hosted_profile("")`,
for a request that is rejected before dispatch and never invokes it, so the fake
script was written to the process cwd, which is the repository root when the
suite runs from there. It was committed as source in `46f0f50` and had been
named as stray leftover in six planning records since Phase 8 without anyone
tracing it to the line that writes it. `hosted_profile` now refuses a
non-absolute directory by name, the caller passes a temp dir, and the file is
deleted. The clean-tree gate added earlier the same day did not catch this one:
the test rewrote the file with identical bytes every run, so the tree stayed
clean while a test kept writing into the tree it was checking.

**`.continue-here` had been dead for months.** It pointed at branch
`gsd/phase-09-subject-loop`, worktree `.phase09-wt`, and main tip `eadf958`.
None of the three exist; Phase 09 landed and its KaTeX gate resolved, the pin is
vendored under `vendor/katex`. It now points at the actual stop, 16C-09 Task 2,
and says what it used to say and why that was worth checking.

**Two orphaned processes, and one of them mattered.** The daemon from
2026-08-28 still listening on `127.0.0.1:63657` and serving a deleted temp
directory was killed, as recorded. Found beside it: a `fake_anki.py` stub from
an interrupted run two days earlier, listening on `127.0.0.1:8765`, which is
AnkiConnect's own port. Any `itembank day` run on this machine since then had
its Anki lane answered by a test stub rather than by Anki. Killed. Nothing in
the repository changed for this; it is recorded because the symptom would have
looked like an integration bug.

**Not swept, and why.** The shared-temp-name shape also exists in
`journal._write_bytes_atomic`, `evidence.rebuild_index`, and
`notes.write_note_document`. None is on the threaded per-request path, and
`journal`'s temp name is asserted verbatim by `tests/file_fault_tracer.py`
(`endswith(".tmp")` for leftovers, and `.locator.json.tmp` by name), so changing
it there is a change to a fault-injection contract rather than a rename. Left
alone deliberately, recorded here rather than fixed on the strength of an
analogy.

Suite: 96 of 96 files, tree clean. 16C-09 Task 2 is untouched and still open.


## 2026-08-30: two tests that were lying about the tree, and a CI guard so a third cannot

Phase 16C is still held at 16C-09 Task 2, its blocking human review. Nothing
below touches that. These are the two open items that had no phase owner.

**The red selection test was failing on the calendar.**
`tests/selection_retention_roundtrip.py` had been red on main with `the weak
objective must fill the sitting: ['q3', 'q1']`, and the 16C tracer bisected it
over about 45 commits to find it failing at every one including `66322ff`, the
commit that introduced it. That result was the diagnosis, not a mystery: a test
failing at its own introducing commit is not describing a change in the code.
The file's other legs pass `cutoff=CUTOFF` (`2026-08-10`) into
`retention.capture`; the CLI leg cannot, because `do_start` captures against
the wall clock. Measured: `emt:airway 1.1905` against `emt:math 0.8095` at the
pinned cutoff, and `1.0 / 1.0` at the live one. Tied weights leave the
retention context nothing to prefer, so Phase 7's ordering settled the sitting.
The new `as_of_now` helper shifts that one leg's fixture by a single identical
offset, so it asserts the invariant rather than a date. No runtime file
changed. Suite: 96 of 96.

**The 14A tracer was rewriting the record it was checking.**
`tests/file_fault_tracer.py` rewrote `14A-TRACER-REPORT.md` on every run, which
made a durable phase record derived, the one distinction the object model
refuses to collapse. It had already cost three commits: `9590eb4` and `4d59ceb`
carried a stray run's timings into 14C's work, and `53d5231` restored 14A's own
numbers and left the ownership question open. The tracer now builds the report
in `report_lines`, and an ordinary run compares instead of writing.
`report_signature` drops the Platform and Python lines and blanks the Measured
column, because the report's own sentence says those are taken on one machine
and are not promises, and a number that is explicitly not a promise cannot also
be a regression. Everything that carries meaning still compares verbatim: a
renamed section, a dropped scenario, a changed reflow count (seeded at 1400, so
reproducible), or a non-zero suite exit code fails by named line. Re-record
deliberately with `--write` or `ITEMBANK_TRACER_WRITE=1`. Both paths were
verified by perturbing the committed file: a scenario row flipped to `broken`
fails at line 16, while a changed Python version, a changed platform, and a
timing moved to `99.99` all pass. The report gains one additive section saying
how it is kept; 14A's recorded numbers are untouched.

**A CI guard so this class cannot return.** A new step asserts the working tree
is clean after the Python suite, printing the offending paths and the diff. A
test may write whatever it likes under a temp dir; it may not leave the tree
dirty. This is also the first time CI has verified that report at all, since
the old behavior overwrote it before anything could compare.

**A sweep for the same two shapes found nothing else.** Every other
`retention.capture` in the suite either pins a cutoff or asserts something
structural (`retention_roundtrip.py` checks a strategy name,
`protocol_roundtrip.py` a queue row count), so no other decay assertion is
clock-coupled. And a full 96-file run leaves the tree clean, so no other test
mutates tracked content.

**`.codex/` is gitignored** as tool state, alongside the same GSD layout under
`.claude/`, on the precedent this repository already sets for `reasonix.toml`.
It held 68 agents, 67 `gsd-*` skills, hooks and a 43KB manifest, and no project
skill at all. Reversible if it should ship for portability instead.

**One new open finding, observed rather than diagnosed.**
`tests/daemon_roundtrip.py`'s `check_concurrency` failed once, under the
nested run inside `tests/model_phase_roundtrip.py`, with `concurrent request 0
did not return 200: <HTTPError 400: 'Bad Request'>`. What is known: it fails
only under load (three suites in flight on this machine), it passed standalone
in the same run, it passed inside `model_phase_roundtrip` on an idle machine
immediately after, and it passed in two earlier full runs the same day. What is
not known: what produces the 400. `Daemon` does not set `request_queue_size`,
so it inherits the stdlib's listen backlog of 5 while the test opens 6
concurrent connections, which is a plausible lead and nothing more. Recorded
rather than patched: Phase 2 daemon code is not this session's to change on a
guess, and a one-line backlog bump that happens to make a flake rarer is the
kind of fix that hides a race instead of settling it. An orphaned daemon from
2026-08-28, still listening on 127.0.0.1:63657 and serving a deleted temp
directory, was found on this machine while investigating; it is test debris
from an interrupted run and was left running rather than killed unasked.


## 2026-08-29: Phase 16C, plans 01 through 09 Task 1, held at the human review

**What landed.** Twelve commits. Five new root-level modules, one published
schema, two additive evidence event types, eight new test suites, one
un-stubbed skill, and one measured tracer report.

- **16C-01** (`46ed2c0`, `5816709`): the precondition check and the
  twenty-four decisions. Nine of eleven legs clean. `model.parse_lesson` now
  returns a sixteen-key superset where the plan asserted six, which is the
  plan's own halt condition: the wave stopped, the choice was put to Weibao
  with the halt costed, and he chose reconcile-and-proceed. D-12.6-5 was
  answered directly (`option-c`, `primary`) and the answer corrected a stale
  plan claim: the decision had been resolved by delegation on 2026-08-16 and
  was never pending.
- **16C-02** (`9165faf`): four fictional subjects, the NOTE-01 record with
  seven closed vocabularies, four relocation states that never auto-apply,
  and a guard that now recognizes a note document.
- **16C-03** (`17413a7`): four strategies as versioned data with a
  code-owned fallback that raises on nothing, and a picker that shows
  disallowed strategies rather than hiding them.
- **16C-04** (`0b6e854`): seven progress claims that never merge, three
  degraded sentences, and a rendered display the test scans for the percent
  character, aggregate words, and merged dimensions.
- **16C-05** (`c3c784f`): the collector over 16B's one precedence function,
  with three structural assertions that a second implementation does not
  exist, and a sitting that pauses preference changes rather than overruling
  them.
- **16C-06** (`38ab376`): two content-free event types proven additive
  against the baselines 16C-01 recorded before any change existed, promotion
  that derives rather than mutates, and deletion honest about what it cannot
  reach.
- **16C-07** (`844680c`): three projections of one parse, counted; three
  broken fixtures each refusing in the validator's own words; and prototype
  gates A, B, and C.
- **16C-08** (`5c14906`, `07ad027`) and the mirror repair (`55379fb`): the
  eleven-item audit that runs first because no function can skip it, a
  bounded diff that does not offer churn, and a keyed-meaning halt with two
  affordances and no override.
- **16C-09 Task 1** (`3f8d8c4`): nine scenarios over four subjects in one
  0.261-second pass, and a report carrying only measured figures.

**Four defects found by running rather than by reading.** The two new event
types failed `schemas/response.schema.json`, whose `other_event` enum is
closed, and would have shipped an event type the project's own published
contract rejects into an append-only log. The `.agents` and `.claude` skill
mirrors had been divergent since `2c34a65` and `d2804f0`, so CI's mirror step
was red on main and the two agent audiences were being told different things.
A Markdown header row in the fixture's TERMS block parsed as a glossary entry
named "Term". And `tests/agent_operation_roundtrip.py` plus `CLAUDE.md` both
still called `legacy-upgrade` a stub after 16C-08 shipped it.

**One pre-existing red test, recorded rather than absorbed.**
`tests/selection_retention_roundtrip.py` fails with `the weak objective must
fill the sitting: ['q3', 'q1']`. Confirmed not this phase's by stashing every
16C change, and bisected over about 45 commits to find it failing at
`66322ff`, the commit that introduced it. It also fails on Python 3.13 and
from a different working directory. It has its own task and is named in the
tracer report's open findings with an owner.

**Update 2026-08-30: that red test is diagnosed and green.** The cause was the
calendar, not a regression, and the bisect was the evidence for that rather
than against it: a test failing at every commit including its own introducing
one is not describing a change in the code. The file's other legs pin the
snapshot cutoff to `CUTOFF = 2026-08-10T12:00:00.000Z`; the CLI leg cannot,
because `do_start` captures against the wall clock. Each real day aged the
fixture one more day, and by 2026-08-30 both objectives had decayed to weight
`1.0` (measured: `1.1905 / 0.8095` at the pinned cutoff, `1.0 / 1.0` at the
live one). A tie leaves nothing for the retention context to prefer, so Phase
7's ordering settled the sitting and returned `['q3', 'q1']`. The fix re-dates
that one leg's fixture by a single identical offset (`as_of_now`), so it
asserts the invariant rather than a date. No runtime file changed;
`retention.py` and `selection.py` were correct throughout. The tracer report's
deferral row is marked closed in place, and the report's own account of the
failure is preserved with the diagnosis appended underneath it.

**Where it stops, and why.** 16C-09 Task 2 is a `checkpoint:human-verify`
rated blocking, and its prohibition is explicit: an agent must not sign its
own contract. Whether "Anchor probably moved: review needed" makes a learner
review rather than shrug, and whether the promotion gates read as protection
rather than bureaucracy, is not something a green suite can answer. No agent
wrote `16C-REVIEW.md`. The eleven review steps are in `16C-09-PLAN.md` Task 2
and the tracer report quotes a rendered progress block for step 8.


## 2026-08-28: Phase 14C, all eight plans, executed and frozen

**What landed.** Seven commits, seven plan summaries, and a freeze file. Ten
source adapters exist behind one `import_source` boundary, one frozen locator
sidecar, two routes, and two CLI commands. `itembank source import` takes a
PDF, a DOCX, a PPTX, an EPUB, a transcript, a photographed page, or a URL;
`itembank source recheck` reports whether a captured origin still matches and
changes nothing at all.

- **14C-02** (`80a0e00`): DOCX including the five package parts python-docx
  never surfaces, the one hardened zip and XML seam every container format
  reads through, and the finished PDF locators (columns, tables, positional
  footnotes and running heads). The two-file source pair is proven atomic by
  three injected faults.
- **14C-03** (`4d59ceb`): PPTX, with slide order read from the presentation
  part's `sldIdLst` rather than from sorted filenames.
- **14C-04** (`9590eb4`): web capture. Both snapshot storage paths and both
  bind policies ship, the fetch is scheme-locked and header-stripping and
  size-capped and timeout-bounded against a real loopback socket, and the
  staleness advisory is a read that appends nothing.
- **14C-05** (`04e32de`): transcript intake through one timestamp grammar,
  with no third-party dependency at all, which makes it the cleanest proof of
  degrade-never-block in the repository.
- **14C-06** (`d2804f0`): OCR, wrapping the one bridge that exists and saying
  how little it knows. Every locator records null geometry and the schema
  refuses a fabricated one.
- **14C-07** (`6bd7fa0`): EPUB on stdlib zipfile and xml.etree, with the
  `ebooklib` AGPL parking finally recorded in the idea ledger as well as in
  the decisions file.
- **14C-08** (`9f26686`): ASR registered as a named refusal with a frozen
  locator shape, `VENDORED.md` completed with a CI checksum gate that was
  watched failing three ways, and the phase freeze.

**Five defects found by verifying rather than assuming.** A gold manifest that
recorded two of the three lines its own fixture drew. stdlib checking a
redirect's scheme before the subclass ever runs, and allowing `ftp`.
`ok_result`'s `journal_entry_id` null on every successful import since
14C-01. A half-written sidecar temp file surviving a fault. And a CI step
with no local preflight mirror, which the preflight drift test caught.

**One checkpoint is recorded UNRUN, not passed.** The OCR adapter against a
live Ollama vision model on a real photographed page. No Ollama server was
reachable on this machine, and the one-sentence transcription-quality
judgement is the actual output of that checkpoint, so inventing it would
defeat the reason it exists. The four eye checks and the degraded-run step
still owed are written out in `14C-06-SUMMARY.md`.

**One inconsistency recorded rather than quietly fixed.** `D-14C-3` records an
agent choice to pin `pypdf` at 6.16.2; the pins file and `VENDORED.md` both
still read 6.16.1. Moving it needs a wheel fetch and a new hash, which is a
supply-chain action rather than a text edit.

**`runtime.py`, `model.py`, and `auditor.py` are untouched by all eight 14C
commits**, measured per commit rather than as a range diff that would
attribute other phases' work to this one. `journal.py` changed in exactly one
commit, by one additive parameter. 88 of 88 suites pass.

## 2026-08-26: Phase 14B waves 1 to 3, executed overnight; the wave stops at the first checkpoint

**What landed.** Three plans, three commits, each verified against artifacts
and a falsified test rather than against its own commit message.

- **14B-01** (`93bb913`): the thin slice. One synthetic objective travels mint,
  edge, sidecar compare-and-swap write, outline projection, package export, and
  clean-machine restore in one green test. `graph.py` (model tier, no file input
  or output, never reaches `model.py`), `course.py` (writes only through
  `journal.commit_operation`, imports no `evidence`), and `course_package.py`
  (imports no `urllib`, `socket`, or `subprocess`; recomputes every fingerprint
  rather than trusting the manifest) exist in their thinnest production form.
- **14B-02** (`1c3ff60`): the typed graph kernel. The frozen four-name edge
  vocabulary with its five carried fields, every default the least-blocking
  value in its set; the degrade path that keeps an unregistered relation and
  downgrades it to an advisory `recommended-before` that can never hard-block;
  containers accepting any local label with no enum anywhere, in the code and
  in the published contract; a deterministic outline that reports order
  violations and cycles and never corrects them; and
  `schemas/course_graph.schema.json`, which `schema_validate.check_schema`
  passes in whole.
- **14B-03** (`1c64ecf`): bindings, rights, overlays, and the version
  migration. A binding against a source whose right is unknown or denied is
  refused before any write, naming the one edit that fixes it. A revoked right
  refuses immediately even though a stale snapshot row still reads granted. An
  imported scope is immutable by construction: an overlay is a sibling record,
  so no code path targets the import's bytes. `graph.UPGRADES` makes the
  version migration a prototype rather than a promise, which
  `PLANNING-DIRECTIVES.md` section 3a requires before any course schema freeze.

**Also landed:** the 13.5 D1 and D2 agent re-measure (`9d24b20`), run in
parallel. The reading measure renders 529px against the contracted 531px, the
2px being the card border the plan arithmetic never counted, and the quiz band
server-renders its total at first paint. **RTS-04 flips to AGENT VERIFIED.**
The position half of D2 stays open and is stated plainly in the gate rows.

**The one decision an agent stood in for, and it needs Weibao.** 14B-01 Task 2
is a blocking, one-way checkpoint: where the course graph lives on disk and
what happens to the Phase 13.9 `course.md` stub. The plan's recommended default
`option-a` was recorded as **provisional** in `14B-DECISIONS.md`, with the slot
for his verbatim answer open and both reversal recipes written out. The default
is the safe stand-in on evidence, not merely the convenient one:
`13.9-CALIBRATION.md` records `course.md` in the real EMT course root holding a
hand-approved objective map, outside this repository and covered by no backup,
and the in-place option would have had a tool rewrite it unattended. The
reversal window stays open until a package is built or `migrate_stub` is first
run against that real root, and neither has happened.

**Why the wave stopped where it did.** 14B-04, 14B-05, and 14B-06 each carry a
blocking human checkpoint, and 14B-04 also modifies `journal.py`, which 14A
froze. Standing in for one checkpoint under a standing overnight authorization
is defensible and recorded; standing in for four, one of them a freeze gate
whose whole point is a human authorability review, is not.

**Two things found and deliberately left open.**

1. **A tracked planning file is rewritten by running the suite.**
   `.planning/phases/14A-identity-lifecycle-operation/14A-TRACER-REPORT.md`
   re-records its own measured timings on every run, so `git status` reports it
   modified after any full-suite run by anyone. Reverted rather than committed
   here, since re-recording 14A's measurements is not 14B's work. Whether it
   should regenerate on every run belongs to whoever owns 14A's tracer.
2. **The 260817-q7d quick plan never produced its required SUMMARY.** Its
   `summary_obligations` asked for `260817-q7d-SUMMARY.md` beside the plan; the
   directory holds only the PLAN.

**Three suites fail and did before any of this work.** `day_roundtrip.py`,
`retention_ui_roundtrip.py`, and `phase_062_audit.py` assert the exact copy
printed with Anki closed, and Anki is running on this machine. Confirmed by
stashing every change and re-running on the clean tree, where they fail
identically. 72 of 75 pass.


## 2026-08-25 (second entry): the sitting queue is finished; what is left needs Weibao

**What landed today, all verified against artifacts and the real served page,
never against commit messages alone.**

- **13.9-04, the five-defect sweep** (`0a3c68e`, `cf097af`, `12f7dae`,
  `d4ea72f`, `84ac02a`): the serve banner id now IS the evidence id
  (`do_start` gained `preset_session_id` and the daemon passes the CLI-minted
  id through; confirmed live, banner `d82657ff...` matched every evidence
  row); an exam or diagnostic duplicate resubmit returns `defer_feedback`
  instead of a `hold` whose copy discloses "Not correct"; `explain_payload(q,
  reveal=False)` blanks `answer_text` alongside `model` and `rubric`, closing
  the offline `--blind` landmine; `itembank mark` gained `--notes` on the
  single form and the pending attempt render prints a ready-to-edit
  `--rubric` template with every authored point verbatim; and `itembank
  marks --base <root>` lists every short awaiting a mark across all sessions
  with the exact command to settle each. The whole solo-marker loop was
  driven live: sit, park, list, copy, flip a boolean, mark with notes, list
  again reads zero.
- **13.9-05, draft autosave** (`5134560`, `5e0eb71`): the served graded
  sitting keeps typed text in localStorage, restores only into empty
  controls (the 080bffc echo wins), ships only in SERVED_JS, and degrades to
  the script-free baseline when storage is off. The acceptance drive on the
  real page caught that the first commit keyed drafts by session id, which a
  server restart re-mints, orphaning the draft in exactly the loss case
  autosave exists for; `5e0eb71` rekeys by bank and item. Verified live:
  type, kill the server, restart, reload, the prose is back.
- **260817-q7d, the 13.5 D1 and D2 defects** (`c70a29e`, `3ec90f4`, merged
  as `b980671`): the lesson wrap pays the card padding and reads at the 18px
  face (candidate 1; the fallback never fired), and the quiz band total is
  server-rendered, so first paint reads Item 1 of 3. Executed in an isolated
  worktree in parallel with 13.9-04, verified independently in the worktree
  (seven suites, guard), then merged. The 13.5-GATES D1/D2 rows still need
  their re-measure to flip RTS-04.
- **ROADMAP corrected:** the 13.9 checkbox and status row read walked and
  5/5 Complete now; the stale `0/3 Planned` row would have made 14B-06's
  freeze gate record a withheld freeze over bookkeeping.

**Found and left open, deliberately.** The served baseline's position
counter still always reads Item 1: q7d's D2 fix server-renders the total,
but the position half of the 13.5 D2 defect (the client render() never runs
under the server baseline) needs a per-request substitution in the daemon's
baseline injection, and widening q7d mid-acceptance was refused. Cosmetic,
visible, routed to the backlog beside the original D2 entry.

**Process note worth keeping.** Two suites (`evidence_roundtrip`
`test_one_writer`, `model_phase_roundtrip`'s scorer scan) fail while an
agent worktree exists under `.claude/worktrees/`, because they scan
directories for second copies of `evidence.py`/`runtime.py`. Merge and
remove the worktree before the acceptance suite run, or the scanners report
the parallelism itself as a defect.

**The handoff: everything still open needs Weibao.**

1. **17A-04.** Task 1 needs a supply-chain decision no agent may make: no
   approved browser driver exists, `17A-RESEARCH.md` recommends a pinned
   Playwright harness, and its ffmpeg component is LGPL, which section 2.4
   routes to him. The decision packet with both options argued is
   `.planning/DECISIONS-17A04-DRIVER-2026-08-25.md`; on a yes, 17A-04 Task 1
   is executable and Task 2 is his A11Y-01 review either way.
2. **The 13.5 human gates** (13.5-GATES.md): bottom-sheet paint on a coarse
   pointer, network-free ladder, script-free ladder, screen-reader
   announcements, and the font-face comparison. D1 and D2 need only an agent
   re-measure now, not him.
3. **His two-sentence post-sitting reaction** (13.9-03 Task 1 step 4), which
   no agent may write.
4. **14B execution** is unblocked: plans exist, `14B-VALIDATION.md` cites
   the calibration corpus, A9 is closed, and the ROADMAP row no longer
   trips 14B-06's gate. 14C still blocks the source-binding half of 14B.

## 2026-08-25: the walking skeleton is walked, A9 closed, and five defects it opened are fixed

**The sitting.** Weibao sat the rebuilt EMT bank end to end through
`itembank serve` on 2026-08-24: session `13d56ab15efb4709821a6dd86357a5dc`,
status complete, 10 items, 18 auto attempts with 9 correct, one constructed
response marked `fail`, 4 hint tiers opened on a single item, all four course
objectives exercised. The corpus is registered at
`.planning/phases/13.9-walking-skeleton/13.9-CALIBRATION.md`, pointers and
hashes only, `itembank guard .` clean.

**Standing rule this unlocks.** 14B-or-later freezes may now commit; their
plans must cite `13.9-CALIBRATION.md` where it covers them.
`14B-VALIDATION.md` and `15A-VALIDATION.md` carry that pointer as of today.

**Weibao's two-sentence reaction is still uncaptured.** 13.9-03 Task 1 step 4
asks for it after the sitting, and no agent may write it for him. It is
evidence about the experience rather than about whether the skeleton was
walked, so A9 closed without it, and the open slot is named in A9 itself.

**What the skeleton was for.** One real sitting on real material found five
defects that seventy green suites had agreed with, all fixed 2026-08-24 into
2026-08-25:

1. The browser form path never wrote the attempt markdown the `serve` banner
   promised. `_refresh_attempt_view` was reachable only from the JSON route.
2. A failed submit threw away what the learner had typed. It now comes back as
   the quiz page with the answer echoed in and the token unspent, so the
   resubmit works.
3. A held multiple-response attempt said nothing about which of the learner's
   own picks were right. `FEEDBACK_POLICIES` gained a `selection` axis;
   practice and remediation disclose, exam and diagnostic stay silent, and the
   scorer is untouched (this is NOT partial credit).
4. NREMT's published option counts are now a lint error for `emt:` items and
   for no other subject.
5. Distractors nobody has ever chosen are now reported by `itembank stats`
   from the evidence store, with both denominators stated.

Before those, on 2026-08-24: a bank containing a `short` item could not be
completed on any surface, found by the first attempt at this sitting and fixed
under `.planning/quick/260824-m4k-marker-closed-transition/`.

**Still open, routed, not fixed here.** `Item 1 of 0` and the never-advancing
position (13.5 defect D2, plan already written at
`.planning/quick/260817-q7d-fix-135-defects-d1-d2/`, unexecuted); the `serve`
banner printing a session id that is not the evidence id; a second exam-mode
submit returning `hold`; `explain_payload(q, reveal=False)` blanking `model`
and `rubric` while returning the same text in `answer_text`, a landmine rather
than a live leak; marking ergonomics for a solo learner-marker; and draft
autosave, the one answer-loss fix that survives a server restart.


## 2026-08-24: 17A-02, 17A-05 and 17A-03 executed; only 17A-04 remains

Ran the 2026-08-23 finish prompt in order, 02 then 05 then 03, from a Claude
Code orchestrating session on the Mac. Every claim below was checked against
an artifact, not a commit message, because that is the mistake the previous
entry exists to record.

| Plan | State now | Evidence |
|---|---|---|
| 17A-01 | Built. | unchanged |
| 17A-02 | **Built.** Task 1 was already closed on 2026-08-20; Task 2 landed. | `a79c626`, `9115ba9`. `surface_shell` is called by `day_page`; the five `--text-*` and three `--density-*` tokens are in `SHARED_CSS`. |
| 17A-03 | **Built.** | `44482d5..366b6fa`. `tests/component_primitives_roundtrip.py` exists and passes; 17 primitives in `presentation.py`. |
| 17A-04 | Not built, and still blocked. | `tools/visual_qa.py` does not exist. Its remaining blocker is now only the 13.9 sitting; 03 and 05 no longer block it. |
| 17A-05 | **Built.** | `7a0fb65`, `faee59d`. `BASE_TOKENS`/`SEMANTIC_TOKENS` carry an `oled` mode; `stylesheet_roundtrip` invariant 4 measures it. |
| 17A-06, 07, 08 | Built. | unchanged |

**Full suite: 70 of 70 green, `itembank guard .` clean**, measured on the
consolidated tree at `19edacc` with `ANKI_CONNECT_URL` pointed at a dead port.

### Four things worth carrying forward

**1. The day route is no longer outside the token layer.** `surfaces/day.py`
was the one served route that assembled its own doctype, so it carried neither
`SHARED_CSS` nor any of the four vendored faces. It composes
`presentation.surface_shell` now, and `served /day/sample_plan` moved out of
`REPORTED_FONT_ROUTES` into `REQUIRED_FONT_ROUTES`, so gate 9 asserts four
served routes instead of three.

**2. A frozen token nothing could consume.** 17A-02 named five type sizes;
17A-03 then found `size_problems` demanded a literal px and rejected
`font-size:var(--text-xs)` while accepting the `12px` it stands for. The gate
resolves the five frozen names now, and only those five (`544fef1`). Record
the shape of this, not just the instance: **a freeze is only real once
something is required to consume it.**

**3. Two pins that guarded nothing.** `config_roundtrip`'s
`test_theme_schema_additive_accent` was defined and never called from
`main()`, so 17A-05's red gate could not have gone red. And
`day_edit_roundtrip`'s `run_cli` merged stderr into stdout while fifteen
callers ran `json.loads` over the whole stream, so the suite passed or failed
on whether an earlier suite had created `_evidence/`. Both fixed
(`7a0fb65`, `259c2db`). Both are the same failure as the 2026-08-23 entry
below: **trusting a name instead of an artifact.**

**4. An unattended ox run in a worktree cannot commit.** 17A-05 was executed
and fully verified by Ox Alpha and landed zero commits, because a worktree's
`.git` points into the main checkout, outside the agent's writable root. The
agent stopped rather than stacking the next plan on an uncommitted tree, which
was correct, but a whole run was spent first. `scripts/ox_overnight.sh` now
refuses that configuration before the smoke test, with `IB_ALLOW_WORKTREE=1`
as the override for when a human intends to commit the result (`e6f5a43`).
That override is how 17A-05 actually landed: reviewed, re-verified
independently, and committed from the orchestrating session.

### Standing environmental note

`day_roundtrip` and `retention_ui_roundtrip` assert the exact Anki-closed
copy, so they fail while Anki Desktop is running. Quit Anki, or export
`ANKI_CONNECT_URL=http://127.0.0.1:59999`. This is not a code defect and it
has now cost two sessions a wrong baseline.

## 2026-08-23: 17A is not as far along as the commit log suggests

Verified by checking artifacts rather than commit messages, after a
message-based count gave a wrong answer twice in one session.

| Plan | Real state |
|---|---|
| 17A-01 | Built. |
| 17A-02 | **Half done.** Its `checkpoint:decision` closed on 2026-08-20 and `17A-DIRECTION.md` records the choice, but the code never landed: `surface_shell` appears zero times in `surfaces/day.py` and `surfaces/theme.py` carries no density tokens. Two of its three must-have truths are unmet. |
| 17A-03 | Not built. `tests/component_primitives_roundtrip.py` does not exist. Blocked by 17A-02's code. |
| 17A-04 | Not built. `tools/visual_qa.py` does not exist. Blocked by 03, 05, and the 13.9 sitting. |
| 17A-05 | **Not built.** Its only two commits are the plan and a roadmap edit. `tests/stylesheet_roundtrip.py` exists but came from Phase 14 (`test(14-01)`, `test(14-02)`), and `surfaces/theme.py` contains no OLED work. Blocked by 17A-02's code. |
| 17A-06, 07, 08 | Built, and 07 and 08 were executed unattended on 2026-08-22. |

**The consequence for sequencing.** 06, 07 and 08 were executed ahead of 02's
implementation even though the wave order puts 02 before them, so the phase has
a hole in the middle rather than a clean frontier. **Nothing in 17A is
unblocked right now except finishing 17A-02's code**, and 17A-04 additionally
waits on the 13.9 sitting.

**How the wrong answer was reached, since it will recur.** Counting
`git log --grep="(17A-05)"` returns two commits and both are planning commits.
A count that does not exclude planning commits reads a planned phase as an
executed one, and `scripts/ox_overnight.sh`'s skip guard keys on the same
convention, so it can be wrong in both directions: it would re-run a plan whose
implementation landed under an off-convention message, and skip one that was
only ever planned. `IB_FORCE=1` is the override. **Check an artifact the plan
names, not a commit message.**



## Phase 14A executed and frozen (2026-08-18, Claude Code session)

All four 14A plans executed on main in one session, waves strictly in order:

- 14A-01 identity kernel: `identity.py`, `discovery.py`, `fixtures/corpus_14a.py`,
  `tests/identity_roundtrip.py`, evidence-field mapping doc (`db805dd..b28ba80`).
- 14A-02 operation journal: `journal.py` compare-and-swap writes, fault
  injection, path-containment refusal (`77b27e9..2afb7d1`). Real bug caught:
  `append_entry` setdefault never fired, every entry_id/timestamp was None.
- 14A-03 six lifecycle operations, external-edit detection, explicit
  reconciliation, transform-rights gate (`5bdcc05`, `24e073a`, `28e6182`).
  `ENTRY_KEYS` gained a `rights` key here, making it twenty-three keys.
- Pre-14A-04 trunk repair, both pre-existing reds root-caused and fixed:
  `audit_writer.py` macOS symlink bug, tracked-clean banks misrouted to the
  shadow backend because `/var -> /private/var` broke relpath (`a5a1c0d`);
  `tests/lti_roundtrip.py` broken crypto-free skip set (`6b33152`).
- 14A-04 freeze gate: eight-scenario tracer `TRACER: 8 passed, 0 skipped,
  0 failed`, D-12.6-10 budgets measured far inside starting budgets (10k full
  inventory 0.19 s vs 2 s budget), reflow corpus check 2000 mutations with
  zero false absorptions (`bc347a6`, `3ec3600`, `09bcbb0`, `acd7147`,
  `b6b8947`, `cd11a86`).
- Reflow checkpoint: Weibao delegated ("do whats best and keep things open in
  case another option is better"); resolved option-a, no reflow normalization,
  the reversibility-preserving reading, recorded with a reconsideration
  condition in `14A-FREEZE.md`.
- Independent verifier: all mechanical truths VERIFIED, `model.py`/`runtime.py`
  untouched, walking-skeleton mint-plus-journal coupling proven live. One
  gap found and corrected: the freeze record said twenty-two journal entry
  keys where the shipped `ENTRY_KEYS` has twenty-three.
- Seven 14A requirement rows (FILE-01/02/03, ID-01/02, RIGHTS-01,
  RELIABILITY-01) moved to Complete. Full 68-file suite green, guard clean.

Standing rule unchanged: 14B-or-later freezes still wait on 13.9-03 closing
A9 (Weibao's sitting). 14A's own freeze is declared and does not depend on it.

## Plan-the-rest session (2026-08-17, Claude planning side)

Ran `.planning/PROMPT-plan-the-rest-2026-08-17.md` end to end. The milestone
now has zero unplanned subphases and zero open discussions; every remaining
piece is executable by a lesser model without a design question reaching it.

- **Discussions closed (Part A).** A1 field model: `IDEABOARD-FIELD-2026-08-17.md`
  and IL-20260817-01 (scope object, boundedness axis; ROLLUP-DIM and
  ROLLUP-MAP both registered, Weibao picks at the 17B-03 checkpoint). A2:
  `SUPPLY-CHAIN-POLICY.md` settles IL-20260815-09, now Core. A3: PDF/DOCX
  research pass recorded (`research/2026-08-17-pdf-docx-intake.md`;
  pdfplumber plus pdfminer.six primary, python-docx for DOCX, pypdf
  fallback, PyMuPDF parked on AGPL for Weibao). A4: IL-20260816-01 settled
  as the standing seam-delivery pattern, machinery deferred to the first
  second provider. A5: 999.2 KEEP (IL-20260817-02), 999.3 PROMOTED per its
  own fired trigger (IL-20260817-03; after 17B, beside Phase 18).
- **Plans (Part B).** 17B: CONTEXT (D-01..D-10), UI-SPEC (gsd-ui-checker
  approved, six PASS), four plans; first checker run NOT-READY (one
  blocker, five warnings), all six findings fixed, re-verified READY, all
  four PASS. Gates G1-G11 are enumerated concretely in the ROADMAP 17B
  details block. 18: CONTEXT (packaging conflict IL-20260815-11 resolved
  onto the Phase 13 shell per 17A D-08; signing is a costed Weibao
  checkpoint; capability disclosure manifest designed), three plans,
  checker READY. 17C (post-17 maintenance and restore audit) registered
  with an owner and one checker-PASS plan. 13.5 defects D1/D2:
  code-verified executable plan at
  `quick/260817-q7d-fix-135-defects-d1-d2/`. OLED theme folded into 17A
  as plan 17A-05.
- **Corrections (Part C).** This file's stale "17A and 17B unplanned" line
  fixed. 17A now carries its plan-checker verdict: READY, all five plans
  PASS (three findings applied: 17A-04 depends on 17A-05, oled named in
  the QA matrix and freeze inventory, ROADMAP plan count five).
- **Held for Weibao (checkpoints, not blockers):** 17A-02 direction pick,
  17A-04 and 17B-04 human acceptance, 17B-03 default rollup model, 18-01
  signing cost decision, 17C-01 audit acceptance, and the parked PyMuPDF
  AGPL question if PDF fidelity ever demands it.
- All commits pathspec-limited; the concurrent Codex track's in-flight
  files (scripts/preflight.py, tests/preflight_roundtrip.py, AGENTS.md,
  .gitattributes, fixtures/) untouched.

## Phase 16C planning session (2026-08-15/16, Claude planning side)

Phase 16C (Strategies, Notes & Prototype Convergence) is fully planned to the
PLANNING-DIRECTIVES section 5 executor bar, following the 16A/16B artifact
precedent (no CONTEXT.md; binding decisions in the roadmap details block,
REQUIREMENTS, the phase-16 synthesis, and the checker-approved UI-SPEC):

- ROADMAP details block (6439a6b): goal, dependencies (14B, 16A, 16B plus the
  13.9 A9 coupling), the cross-subject missing-feature freeze gate, and the
  prototype-before-freeze coupling (STYLE-DISCIPLINE trio; directives 3a
  strategy-pathway prototypes).

- 16C-RESEARCH.md (9ab4190): 11 assumptions, 11 pitfalls, 7 open questions all
  resolved with recommendations, an 18-item Do Not Re-Open ledger, and the
  binding nine-plan shape. Load-bearing resolution: strategy lifecycle events
  (activity_completed, activity_skipped) append through the one evidence
  writer as additive content-free event types; note content stays in the
  deletable learner note store, because report 12 section 11.2 deletion is
  incompatible with the append-only log.

- 16C-PATTERNS.md (bd1a258), 16C-VALIDATION.md (5722b4a, map filled by the
  planner), 16C-UI-SPEC.md (f136156, decisions D1-D16; checker sign-off
  00a6de5, six dimensions PASS).

- Nine plans 16C-01..09 (1d4813a..7283597, list recorded in ROADMAP by
  4e39e28): waves 1:[01] 2:[02,03,04] 3:[05,06] 4:[07] 5:[08] 6:[09]; 01 and
  09 not autonomous; 23 tasks; plan-checker verdict READY, all nine PASS,
  zero material warnings. The planner run was interrupted once by a session
  limit (16C-01 checkpoint-committed truncated as 313b688, repaired in
  1d4813a); nothing was lost.

- Held for Weibao, surfaced as the 16C-01 Task 2 checkpoint:decision rather
  than silently defaulted: D-12.6-5 (notes default placement and Evidence
  prominence; recommended default is margin capture with Evidence review and
  Evidence as primary navigation).

- Execution order note: 16C-01's precondition halts by name until 14B, 16A,
  and 16B freezes exist and 13.9's A9 is closed, so handing 16C to Codex now
  is safe but it will (correctly) refuse to pass wave 1.

Remaining unplanned subphases as of this 16C session: 17A and 17B, then
Phase 18. (Superseded 2026-08-17: 17A gained plans on 2026-08-16 via
aa21ac1, and the plan-the-rest session above planned 17B, 17C, and 18, so
no unplanned subphase remains.)

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-07)

**Core value:** One runtime, one scorer, one evidence store — and the runtime, not the model, decides what reaches the learner.
**Current focus:** Phase 13.5 (reading and teaching surface quality), wave 3 next. The source-to-course reframe in `.planning/SOURCE-TO-COURSE.md` opens the next milestone as Phases 14 through 17; v1.0's human-pending verification backlog is below and still open.

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

## Current Position

> **Superseded 2026-08-27, later the same day.** The block below was accurate
> when written and is preserved as history. It says waves 4 to 6 are blocked on
> four decisions: **all four were answered, all three waves ran, and Phase 14B
> is frozen.** `14B-FREEZE.md` carries `## Frozen at 14B` on three green legs,
> and its authorability leg was signed by an agent under Weibao's explicit
> waiver of that document's own agent-never-self-certifies clause, which the
> freeze record names in full rather than burying.
>
> **Phase: 14C, plan 01 executed.** `source_adapters.py`, the frozen locator
> sidecar contract, `POST /api/source/import`, `itembank source import`, the
> `source` settings group, and `VENDORED.md` all ship. One PDF imports as a
> cited source with one fingerprint agreeing across sidecar, journal entry, and
> registry. Plans 14C-02 through 14C-08 remain.
>
> **What is unblocked now.** Phase 15A and Phase 16A, both by the 14B freeze.
> 16A-01's precondition check ran green on 2026-08-27 with zero deviations
> (`16A-PRECONDITION.md`), so 16A may proceed.
>
> **What still halts, correctly.** Phase 16B. Its precondition halts on Phase
> 16A never having executed, not on 14B: `capabilities.py`,
> `16A-FREEZE.md`, and `model.SEMANTIC_PROFILE_VERSION` are all absent. That
> halt stays right until 16A runs and freezes, and the course shelf 16B-04
> draws sits behind it.
>
> **What still waits on Weibao.** The 17A-04 browser-driver supply-chain packet,
> open since 2026-08-25. FILE-04's phase, deliberately, which he chose to decide
> after the 14B freeze; that freeze has now closed, so it is answerable.


> **Corrected 2026-08-27.** The block below described Phase 13.5 and said the
> reframe was "not yet pushed". Both were stale: the frontmatter has read
> `current_phase: 14B` since 2026-08-26, and `main` is pushed. A cold agent
> reading this file top-down was getting the wrong phase. The current position
> is stated here; the 2026-08-14 text is preserved underneath as history.
>
> **Phase: 14B, waves 1 to 3 executed 2026-08-26.** `graph.py`, `course.py` and
> `course_package.py` ship. Waves 4 to 6 are BLOCKED on four decisions only
> Weibao can make: D-14B-1's provisional stand-in plus three blocking
> checkpoints in plans 14B-04, 14B-05 and 14B-06. Packet:
> `.planning/DECISIONS-14B-DRIVER-2026-08-27.md`. Sequencing:
> `.planning/NEXT-2026-08-27.md`.
>
> **Also true 2026-08-27:** Phase 16A is planned and unexecuted, so Phase 16B's
> precondition check HALTS (dry run:
> `.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION-DRYRUN-2026-08-27.md`).
> 17A-04 still waits on the 2026-08-25 supply-chain packet. Weibao's 2026-08-27
> percent ruling amended GRAPH-03, synthesis 12.4, plan 16B-04 and
> 16B-RESEARCH.md; see `IDEA-LEDGER.md` IL-20260827-01.

### Historical, as written 2026-08-14

Phase: **13.5 - Reading & Teaching Surface Quality Pass**, waves 1-2 executed (3 of 8 plans)
Status: v1.0's 18 phases are shipped. A next milestone opened on 2026-08-13 with the source-to-course reframe (Phases 14 through 17), merged into `main` and not yet pushed.
Last activity: 2026-08-14 - Quick task 260813-x3g source-to-course contract reframe, slices 1-4a committed and pushed. Applied synthesis section 14 across nine contract/doc files: ROADMAP (nine subphases 14A-17B + governance), SOURCE-TO-COURSE (supersede pointer), REQUIREMENTS (eighteen families GRAPH..MAINT, 47 new requirements, old IDs mapped/superseded), PROJECT (course-first), UI-SPEC (Structured Studio; section 8 gates untouched), PLANNING-DIRECTIVES (finite-strategy + rejection-ledger; section 8 nine-subphase table), AGENTS + .claude/CLAUDE.md (object/authority + operation protocol; non-negotiables intact), README (course-first). Commits: 8b5cab4, e838407, e349c06 (REQUIREMENTS content landed split across the slice-3/4a commits because gsd `query commit` sweeps all modified files while the parallel 13.5 track shared the tree; content verified complete on disk, nothing lost).

DONE 2026-08-14 (audit chat): slice 4b and slice 5 are complete; see the
"Slice 4b and slice 5 completion" block below. The paragraph following is the
pre-completion record, kept for history.

PREVIOUSLY OWED before any Phase 14A plan: reframe slice 4b (rewrite build-course/curriculum-design/absorb-book/author-bank skills per synthesis section 10 and mirror .agents/skills <-> .claude/skills; add lesson-authoring/discovery-and-binding/media-intake/legacy-upgrade skills + shared reference. NOTE: rewrite the four EXISTING skills to the section-10 contract now, but only STUB the new skills (intent + placeholders) - do not document surfaces 14A/14B/16 have not shipped yet. The 999.5 rule holds: a skill documents only a shipped command surface. Flesh out discovery-and-binding after 14A/14B, lesson-authoring after 16A, legacy-upgrade after 16C/17) and slice 5 (the synthesis section 16.3 implementation-readiness audit, which gates Phase 14A).

Progress 2026-08-14: slice-5 audit is now SPEC'd as a bounded checklist in `.planning/READINESS-AUDIT-14A.md` (A1-A8 + research bake-in gate); it still needs to be RUN (output = audit report + contract-delta patch). The three gating pre-14A schema decisions from synthesis 12.6 are RESOLVED in `.planning/DECISIONS-PRE-14A-2026-08-14.md`: (1) hybrid graph storage - local edges inline, cross-object edges in a readable sidecar, edge vocab frozen at prerequisite-of/covers-objective/source-supports/treatment-of; (2) object-level opaque IDs + component IDs only for cited/gated/evidence-bearing blocks, whitespace+line-ending normalization first, reflow deferred to the 14A tracer; (3) the `mastered` field becomes a Khan-style per-objective, self-adjustable fill state (not one aggregate score; level vocabulary routed to 16B). Next action: run the slice-5 readiness audit, then slice 4b skills, then plan Phase 14A.

### Slice 4b and slice 5 completion (2026-08-14, audit chat)

**Slice 4b complete.** build-course, curriculum-design, absorb-book, and
author-bank are rewritten to the synthesis section-10 operation contract, all
pointing at a new shared `.agents/skills/OPERATION-CONTRACT.md`; the four new
skills (lesson-authoring, discovery-and-binding, media-intake, legacy-upgrade)
are stubs only per the 999.5 rule; `.agents/skills` and `.claude/skills` are
verified byte-identical (diff -r clean after every edit).

**Slice 5 complete: the readiness audit RAN and PASSED.** Report:
`.planning/AUDIT-REPORT-14A-2026-08-14.md`. Highlights: A1 diffed 221 accepted
clauses, landed all 9 no-landing clauses additively, fixed 6 weaker landings
(including the seven progress dimensions now named in GRAPH-03 and the
uncertain-source-claim guard restored to AGENT-02), and added MAINT-04 plus a
family-alias note; A2's Fail (43/47 requirements without fixtures) is fixed
with a labeled Fixture sentence on all 47; A3's checklist wording was amended
(prototype-before-freeze-commits, tracer plans first within a freezing
subphase); A8 verified the rejection ledger fully intact (11/11 hard rejects
carry all eight fields, zero simplicity-only). The mid-audit A9/A10 additions
were adopted: both pass, with the cold-agent onboarding transcript recorded as
Phase 18's owed fixture. The bake-in gate landed in CAP-01, NOTE-01, GRAPH-03,
and FLOW-02 (worked-example-first default, no compelled highlighting,
retrievability never a percentage, reading scrolls, Socratic refusal as a
locked card).

**Decisions:** the three gating pre-14A decisions were already resolved; the
eight remaining 12.6 decisions are framed in
`.planning/DECISIONS-12.6-REMAINING-2026-08-14.md`. Four are held for Weibao
(solo self-acceptance by risk tier, notes placement and Evidence prominence,
formal-test pause policy, executable-source trust persistence); four are
technical calibrations confirmed at their owning subphase. Synthesis 12.6 is
annotated CLOSED/FRAMED in place, record preserved.

**New planning artifacts:** `STYLE-DISCIPLINE-16A-2026-08-14.md` (semantic vs
cosmetic rule for every lesson/note style; notebook page, Cornell, and concept
map prototyped from one parsed content before the long tail registers);
`research/phase-16/16-editor-reader-landscape.md` (bounded editor/reader
landscape thread; the Ellipsus branching-drafts pattern mapped as a thin UI
over the 14A revision model via requirements R1-R10);
`.planning/phases/14A-identity-lifecycle-operation/14A-BRIEF.md` (four
plans, file-fault and external-edit tracer as the freeze gate, walking-skeleton
coupling stated, expansion to the PLANNING-DIRECTIVES section-5 executor bar
required before execution).

**Next action:** Weibao decides the four held decisions; execute 13.5 waves 3+
beside Phase 13.9 (walking skeleton); expand and execute the 14A plans. Phase
14A is unblocked.

**Update 2026-08-16:** the four held decisions are resolved by delegation
(`DECISIONS-12.6-REMAINING-2026-08-14.md`, all four Resolved fields). An
agent browser pass closed most of the 13.5 human gates and found two defects
(D1 reading measure 422px vs contracted 531px; D2 "Item 1 of 0" first-paint
counter); results in `phases/13.5-reading-teaching-surface-quality-pass/
13.5-GATES.md`, future-work entries in ROADMAP.md Backlog small-enhancements
(D1, D2, and the remaining human-verify tail: screen reader, bottom-sheet
paint, script-free/no-network walkthrough, font-face comparison).

**Concurrent-edit notice for the audit chat (2026-08-14).** A direction-review
session amended the planning surface WHILE the slice-5 audit run was in flight.
If your audit snapshot predates these, re-read before sign-off and fold the
consequences into the contract-delta patch rather than re-running mechanical
passes:

- `READINESS-AUDIT-14A.md` gained **A9 (walking-skeleton gate)** and **A10
  (external-user v1 bar)**. Both must be checked or waived-with-reason before
  sign-off; A9's Fail condition ("first learner-visible course experience is
  17B") is now cured on paper by Phase 13.9 but must be honored by the 14A/14B
  plan set your step 7 writes.

- `ROADMAP.md` gained **Phase 13.9 (walking skeleton, with a details block
  before the subphase-sequence section)** and **Phase 18 (external-user v1)**,
  plus a 2026-08-14 revision note. Your A7 emitted sequence should read: 13.5
  waves 3+ beside/before 13.9, then 14A, 14B (13.9 walked before any
  14B-or-later freeze commits), then the 15/16 fork, 17A, 17B, 18.

- `.claude/CLAUDE.md` **Users constraint amended** to "one learner per
  installation; external installations supported; no accounts/auth/
  multi-tenancy". A10's constraint-text check is therefore already satisfied
  for CLAUDE.md; AGENTS.md carries no Users line (verified by grep), so record
  that as the reason A10's AGENTS.md half is a no-op.

- `PLANNING-DIRECTIVES.md` section 5 gained the **lesser-model executor bar**
  (six explicit legibility requirements). Every per-subphase plan from step 7
  is written to that bar; treat it as an acceptance check on each plan.

- `USER-VISION-INBOX.md` gained the 2026-08-14 walking-skeleton/external-user
  entry (verbatim, with disposition); `README.md` gained the "Quick start for
  someone brand new" agent-onboarding section, which is A10 check 2's
  artifact (its cold-agent transcript fixture is still owed).

No re-audit of A1 through A8 is required by these edits alone: they add
scope, they do not alter synthesis clauses. The one interaction to check: A3/
A9 overlap on freeze ordering, where A9 is the stricter reading for 14B+.

**Phase 13.9 planned (2026-08-14, direction-review session).** Three
Sonnet-executable plans exist in `.planning/phases/13.9-walking-skeleton/`
(01 bind and map with two checkpoints, 02 author lesson plus bank, 03 the
sitting, calibration corpus, and A9 closure). They are the reference
exemplars for the standing `.planning/PLAN-TEMPLATE.md` (executor bar,
PLANNING-DIRECTIVES section 5); new plans start from that template. 13.9 can
execute immediately; it does not wait on 14A, and no 14B-or-later freeze
commits before 13.9-03 closes A9. A future-phase capability, agent-facing
update and capability disclosure, is registered on the Phase 18 roadmap
entry per the 2026-08-14 vision-inbox entry.

### Correction (2026-08-13): this file claimed "complete" through a live phase

Between 2026-08-12 and 2026-08-13 this file read `current_phase: complete` and
`18/18` while Phase 13.5 was accruing commits on `main` and a second branch was
accruing the source-to-course research. Both branches numbered their new phase

14. The collision was not caught by any tool: `git merge-tree` reports one

content conflict, in `REQUIREMENTS.md`, and `ROADMAP.md` merges clean while
producing two Phase 14 headings.

Resolved by quick task 260813-r5c. The reading and teaching work became Phase
13.5, which is also where it belongs on dependencies: it hardens the reader and
quiz surfaces the source-to-course spine builds on. The number 14 went to Course
Workspace & Source Binding. The twelve RTS requirements keep their content and
are routed to subphases 16A, 16B, 17A and gates G4 and G6 per
`research/phase-16/14-synthesis.md` section 15.

Still owed, and deliberately not done by that quick task: synthesis section 14
and section 15 propose replacing the flat 14-to-17 sequence with nine subphases
(14A, 14B, 15A, 15B, 16A, 16B, 16C, 17A, 17B) and rewriting five contract files.
The roadmap as merged still carries the flat sequence its own research
supersedes.

### Correction (2026-08-12): the v1.0 ship was recorded green against a red trunk

The "shipped" status above was written from the phase-level VERIFICATION
files. Nothing re-ran the suite against merged `main`, so twelve
independently-green branches merged into a trunk whose CI had been failing
since 2026-08-07. The job died 15 seconds in at step 8 of 14 — the schema
step read `['item']['objective']`, a field plan 03.1-03 had deliberately
removed from the public payload — which meant **the test suite, the content
guard and the JS runner did not execute on any commit for five days**.

Three genuine defects were sitting behind that dead step, none of them
caught by any phase's own verification:

- `runner.py` compared captured stdout byte-for-byte, so a Windows child's
  CRLF failed every `check` item — the scorer's verdict depended on the
  learner's OS.

- `itembank guard` refused the repository's own README, because the
  phase-05 grammar widening made README's fenced format sample parse as a
  real item.

- `authoring.py` wrote pending proposals to `sha256:<hex>.json`, a filename
  Windows cannot create, so every stateful authoring run died there.

Four more tests were passing without testing what they claimed (a wall-clock
cutoff that expired, a git identity that fell back to the global config, 20
LTI checks that only re-proved a refusal, and four pacing tests that counted
the wrong local day off-UTC).

Fixed on `fix/ci-green-post-v1.0` (PR #19): CI green across all 14 steps
(run 31565997898), 63/63 on Linux and Windows, node 7/7. **The milestone is
not honestly complete until that merges.**

Three gaps stay open and are deliberately not closed by that branch:

1. The pacing counter's local day defaults to UTC, so the daily cap rolls at
   19:00 Central rather than local midnight. The tests were matched to the
   documented default rather than flipping it, because changing the zone
   moves every snapshot id.

2. Three tests depend on Windows build artifacts CI cannot produce, so the
   packaging contract now passes by skipping rather than by verifying.
   Closing it honestly needs a Windows runner in the matrix.

3. Nothing gates a merge on CI. A required status check on `main` is what
   stops this recurring; a ship step that reads VERIFICATION files cannot.

> **Branch note (gsd/phase-03.1-finish):** Phase 03.1
> (lesson-rich-blocks-glossary-style) is CLOSED — plans 01-07 complete with
> SUMMARYs, `03.1-VERIFICATION.md` (status `human_needed`, 7/7 truths
> statically verified) and `03.1-UAT.md` recorded. Live automated-suite runs
> and the three perceptual/browser human-verify items remain open; see
> `03.1-GATES.md` and the Deferred Verification table. The milestone's
> active phase stays 08 (main).

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**

- Total plans completed: 24
- Average duration: - min
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 11 | - | - |
| 02 | 6 | - | - |
| 13 | 5 | - | - |
| 06 | 2 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 01 P01 | 15min | 3 tasks | 5 files |
| Phase 01 P02 | 18min | 3 tasks | 8 files |
| Phase 01 P03 | 20min | 2 tasks | 5 files |
| Phase 01 P04 | 18min | 3 tasks | 6 files |
| Phase 01 P05 | 25min | 3 tasks | 9 files |
| Phase 01 P06 | 35min | 3 tasks | 6 files |
| Phase 01 P07 | 40min | 3 tasks | 9 files |
| Phase 01 P08 | 21min | 3 tasks | 6 files |
| Phase 01 P09 | 12min | 3 tasks | 7 files |
| Phase 01 P10 | ~21min | 3 tasks | 9 files |
| Phase 01 P11 | ~30min | 3 tasks | 10 files |
| Phase 02 P01 | 55min | 2 tasks | 5 files |
| Phase 02 P02 | 26min | 2 tasks | 8 files |
| Phase 02 P03 | 65min | 3 tasks | 6 files |
| Phase 02 P04 | 16min | 2 tasks | 4 files |
| Phase 02 P05 | 16min | 2 tasks | 2 files |
| Phase 02 P06 | 25min | 2 tasks | 3 files |
| Phase 02.1 P01 | 20min | 3 tasks | 9 files |
| Phase 02.1 P02 | 9min | 2 tasks | 6 files |
| Phase 02.1 P03 | 25min | 3 tasks | 7 files |
| Phase 02.1 P04 | 25min | 3 tasks | 5 files |
| Phase 02.1 P06 | 20min | 2 tasks | 3 files |
| Phase 02.1 P05 | 35min | 2 tasks | 3 files |
| Phase 02.1 P07 | 20min | 3 tasks | 5 files |
| Phase 02.1 P08 | ~15min | 2 tasks | 2 files |
| Phase 02.1 P09 | ~25min | 3 tasks | 6 files |
| Phase 03 P03-02 | 313 | 2 tasks | 5 files |
| Phase 03 P03 | 17min | 3 tasks | 12 files |
| Phase 03 P04 | 313 | 2 tasks | 4 files |
| Phase 03 P03-05 | 8 | 2 tasks | 4 files |
| Phase 04 P02 | 21 | 2 tasks | 4 files |
| Phase 04 P04-03 | 10 | 3 tasks | 8 files |
| Phase 04 P04 | 15 min | 2 tasks | 6 files |
| Phase 04 P05 | 10min | 2 tasks | 2 files |
| Phase 04 P06 | 30min | 2 tasks | 4 files |
| Phase 03.1 P01 | 35 | 3 tasks | 6 files |
| Phase 03.1 P02 | 140 | 3 tasks | 15 files |
| Phase 03.1 P03 | 190 | 3 tasks | 18 files |
| Phase 13 P01 | 16min | 3 tasks | 3 files |
| Phase 07 P01 | 50min | 3 tasks | 8 files |
| Phase 07 P02 | 25min | 3 tasks | 6 files |
| Phase 06 P01 | 95 min | 3 tasks | 9 files |
| Phase 07 P03 | 30min | 3 tasks | 5 files |
| Phase 13 P02 | 105min | 3 tasks | 28 files |
| Phase 13 P03 | 65min | 3 tasks | 7 files |
| Phase 13 P04 | 55min | 3 tasks | 12 files |
| Phase 07 P04 | 40min | 4 tasks | 11 files |
| Phase 13 P05 | 40min | 2 tasks | 2 files |
| Phase 07 P05 | 45min | 3 tasks | 7 files |
| Phase 07 P06 | 45min | 3 tasks | 11 files |
| Phase 06 P02 | 150 min | 3 tasks | 11 files |
| Phase 08-model-adapter-interface-tier-gate-enforcement P08-03 | 22min | 3 tasks | 3 files |
| Phase 08-model-adapter-interface-tier-gate-enforcement P08-04 | 55 | 3 tasks | 9 files |
| Phase 08-model-adapter-interface-tier-gate-enforcement P08-05 | ~35min | 3 tasks | 7 files |
| Phase 09.1-audio-drill-export 09.1-01 | ~50min | 3 tasks | 6 files |
| Phase 09.1-audio-drill-export 09.1-02 | ~45min | 3 tasks | 5 files |
| Phase 09.1-audio-drill-export 09.1-03 | ~50min | 3 tasks | 6 files |
| Phase 09.1-audio-drill-export 09.1-04 | ~40min | 3 tasks | 2 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Phase 3] 03-01: D-04 resolved option-a (user delegation) -- `lesson_ref`/`lesson_slug` stay EXCLUDED from `model.content_fingerprint()` and are locked by a regression assertion (fingerprint of a tagged item equals the byte-identical untagged item); tagging an item never raises `item.content_drift`.
- [Roadmap]: Evidence spine (Phase 1) and daemon/settings/lesson/surfaces/check foundations (Phases 2-5) run as parallel-eligible tracks per `Depends on: Nothing`; the teaching loop, selection, model adapter, subject-loop integration, retention/trends, and the auditor form the dependent chain (Phases 6-11); packaging closes the milestone (Phase 12).
- [Roadmap]: Three phases carry unresolved design questions flagged for their own research at plan time â€” Phase 1 (item identity scheme, Windows event-log durability), Phase 8 (tier-gate enforcement mechanism, no prior art), Phase 11 (second quality gate algorithm, syllabus input formats, auditor reversibility mechanism).
- [Roadmap]: The auditor (Phase 11) is deliberately last among new subsystems; its pitfall guard rails (citation-per-claim, second quality gate, one-item-per-commit reversibility, graduated autonomy) are written as phase acceptance criteria, not follow-on hardening.
- [Phase ?]: 01-01: evidence.py built as a peer module to runtime.py, never imported by model.py; advisory-locked single-write()-per-event append confirmed durable on this Windows machine via a real-OS-process spike that also reproduced the unlocked-O_APPEND corruption bpo-42606 predicts
- [Phase ?]: 01-02: Task 1 checkpoint resolved as option-a â€” response_time_ms and confidence captured with real values (served_ts, --confidence flag); error_category and hint_tier recorded as explicit null with the reason stated in code, since no error taxonomy or hint ladder exists before Phase 6/8
- [Phase ?]: 01-02: evidence.py's response_event()/append_event()/events()/attempt_number()/objective_history() built as the first real writer and reader over the evidence log; surfaces/session.py is the first caller, and model.py additively parses [ID:]/[HASH:] into item_id/content_hash (empty until plan 01-04 assigns them)
- [Phase ?]: 01-03: LINT_CODES built from sorted(set(...)) rather than a hand-ordered tuple, so sortedness/no-duplicates is structural rather than maintained by eye
- [Phase ?]: 01-04: content_fingerprint() hashes only tested-content fields (never rationale); assign_ids() is a pure text transform, cmd_id_assign is the only bank writer, checking D-05 cross-bank id-uniqueness in a read-only first pass before any write
- [Phase ?]: 01-05: SESSION_UPGRADES registry + upgrade_session() closes CONCERNS.md's version-evolution gap; response.schema.json's required array follows the live 23-key response_event() (not the plan's stated 22), matching the same discrepancy 01-02 already resolved
- [Phase ?]: 01-06: schema_validate.py implements exactly the SUPPORTED keyword subset schemas/*.json use; check_schema() raises SchemaError on any keyword outside SUPPORTED/ANNOTATIONS before any instance is examined, so a green validation always means the whole document was checked
- [Phase ?]: 01-06: itembank schema --all is PROTO-05's delivery mechanism -- one sort_keys JSON object carrying model.SPEC, all five schemas/*.json documents in sorted order, and the exact command sequence to run a session, mirroring cmd_spec's no-processing precedent
- [Phase ?]: 01-07: response_event()'s canonical field now stores idempotency_canon()'s output (never null) instead of runtime.canonical_response()'s raw output, so a short item's canonical value matches what dedupe_key is built from -- schemas/response.schema.json updated in the same commit
- [Phase ?]: 01-07: D-10 implemented as a read-side filter -- live_events(log) is the only function views (attempt_number, objective_history) may use for counting; retracted_ids(log) collects over the whole log before anything is emitted, so a retraction physically preceding its target still suppresses it; events(log) stays the raw reader for audit
- [Phase ?]: 01-08: objective_history() is the ONE call site that invokes ensure_index(); cmd_evidence deliberately does not duplicate the call, inferring used/fallback status afterward via a read-only index_stale() check so a regression skipping ensure_index() stays observable rather than being masked by a redundant refresh
- [Phase ?]: 01-08: prefix objective matching implemented as two escaped LIKE clauses (x.% / x:%), never a bare LIKE 'x%', so emt:airway can never also match emt:airwaymanagement
- [Phase ?]: 01-08: index_stale() catches an unopenable/corrupted index internally and treats it as a full-rebuild trigger rather than letting the exception escape -- fixed while confirming test_index_is_disposable goes red per the plan's own acceptance criteria
- [Phase ?]: [Phase 1] 01-09: session_events()/marks_by_event() read exclusively through live_events(), extending D-10's read-side-filter discipline to renders -- a retracted response or a retracted mark vanishes from a view exactly as it vanishes from a count
- [Phase ?]: [Phase 1] 01-09: render_attempt_md/render_session_json take only (log, session_id, qs, bank_path), never the session JSON file itself -- the session file cannot be an input to its own render (D-11), so neither render can claim a sitting is finished, only report what the log itself proves happened
- [Phase ?]: [Phase 1] 01-09: mark_event() rejects any marker other than 'human' (T-1-24); a model verdict is not accepted evidence until Phase 8/TEACH-09 teaches the runtime to hold one as pending review
- [Phase ?]: [Phase 1] 01-09: fixed _tail_dedupe_keys() to track the dedupe key of any event carrying one (response or mark), not just event_type=='response' -- found while confirming a replayed mark batch reports already_recorded per D-12
- [Phase ?]: [Phase 1] 01-09: cmd_mark validates and resolves every batch entry before appending any of them, so an unresolved item_ref anywhere in the batch appends nothing at all, not a partial prefix
- [Phase ?]: 01-10: the day surface's evidence directory is derived from daily_log.md's own resolved location (--log override), not the plan file's directory, so evidence lives beside wherever the tick history itself lives
- [Phase ?]: 01-10: tests/serve_roundtrip.py's attempt-file assertions updated to match render_attempt_md()'s established 01-09 vocabulary (MARK: pending, no finished claim) and the evidence log's append-only attempt semantics (re-answering opens a new live attempt rather than overwriting)
- [Phase ?]: 01-10: cmd_serve prints session_id in its startup banner so a marker can pass it to itembank mark / itembank render attempt after the sitting ends
- [Phase ?]: 01-11: source_key(kind, basename, ref) becomes a migrated response event's dedupe_key, deliberately separate from the live path's session+item+attempt+canonical scheme (D-17), so two unrelated unresolved legacy records can never collide into one event
- [Phase ?]: 01-11: mark and day_tick events reuse mark_event()/day_tick_event()'s own already-idempotent dedupe keys during migration rather than a source_key override -- a day_tick imported by migration and one recorded live via itembank day since 01-10 naturally reconcile
- [Phase ?]: 01-11: no resolution by default (D-14) -- item_id is empty and item_ref carries the original positional reference unless --resolve-by-position is explicitly given, which records source_ref.resolution on every event it touches; no similarity-matching path exists
- [Phase ?]: [Phase 2] 02-01: surfaces/daemon.py's cmd_daemon opens one session (session_id/log/attempt-file) per bank at startup, stored on DaemonHandler.sessions[stem]; isolation between banks sharing one evidence log is by the event's bank field, matching the existing evidence design, not by a separate log file per bank
- [Phase ?]: [Phase 2] 02-01: quiz.record_answer() factored out of cmd_serve's record() closure so the CLI serve path and the new daemon path score through runtime.score_response() and write through evidence.append_event() via exactly the same function (D-08 continued)
- [Phase ?]: [Phase 2] 02-01: scan_dir() sorts candidates by (stem.lower(), full_path) rather than stem alone, so a stem-collision winner is deterministic across restarts even where directory-enumeration order is not guaranteed stable
- [Phase ?]: 02-02: day_state()/day_render()/apply_day_post() take an explicit iso threaded through serve_scoped's day_extra rather than computing 'today' internally, so itembank day --date backfilling still works once day became a daemon launch
- [Phase ?]: 02-02: handle_quiz_answer reads reveal/progress off the bank's session dict (default off) rather than at the route-table level, so a general itembank daemon launch is unaffected while itembank serve's scoped launch keeps --reveal and its progress line
- [Phase ?]: 02-03: Task 1 checkpoint resolved as option-a -- itembank config mirrors itembank schema exactly (no-args table, config schema verbatim, config set validate-then-write); SETTINGS_CODES built as a sorted dotted tuple following the LINT_CODES precedent
- [Phase ?]: 02-03: added required arrays to the nested daemon/selection_weights/model_backend object schemas so settings.missing_key has a reachable input path via config set, rather than a published code nothing can trigger
- [Phase ?]: 02-04: do_submit(session_file, answer, confidence) calls normalize_answer(answer) itself, so the same function serves a raw CLI string and an already-JSON-native /api/submit value without a second call site
- [Phase ?]: 02-04: every /api/* handler wraps its session.do_* call in except SystemExit (400) then except Exception (500), in that order -- SystemExit derives from BaseException so the existing except-Exception-only pattern would not catch it and would kill the daemon
- [Phase ?]: 02-04: session_index(root) rebuilds from _attempts/ on every API request rather than caching at startup, so a concurrently created session is addressable immediately; a client-supplied session/bank_path/out field is refused with 400 rather than accepted
- [Phase ?]: 02-05: handle_report_get calls session.do_report for the summary and a direct read_session for cursor/len(items) in the in-progress branch, keeping do_report's own return shape untouched per the plan's files_modified scope
- [Phase ?]: 02-05: the empty-state report branch is decided purely on auto_attempts==0 and pending_manual==0, independent of session status -- the three report states are branches of one template chosen on data, not a flag
- [Phase ?]: 02-05: REPORT_TEMPLATE's data-field="<name>" markers give tests a stable regex hook against every numeric figure instead of scraping prose
- [Phase ?]: 02-06: probe()/start_server() implement D-02's three-case detect-and-attach startup; fixed a Windows-only bug where Daemon's allow_reuse_address=True silently defeated it (SO_REUSEADDR lets a second process bind an already-listening port on Windows, unlike POSIX)
- [Phase ?]: 02-06: cmd_daemon reads daemon.port/daemon.lan from itembank.json via settings.load_settings(), with --port/--lan overriding; --lan has no CLI off-switch, so 'explicitly given' collapses to a.lan is True
- [Phase ?]: 02.1-01: resources.py is the one bundled-resource reader (checkout and .pyz alike); build.py's STAGE_FILES/STAGE_DIRS are explicit allowlists, never a working-tree walk, keeping evidence and real banks out of the artifact
- [Phase ?]: 02.1-01: itembank.__version__ = "0.3.0" is the first release ever cut from this repo, deliberately pre-1.0; surfaces/cli.py's --version flag imports itembank lazily inside main() to avoid circling back through the .pyz's __main__.py
- [Phase ?]: 02.1-02: build.LAUNCHER_DIR (renamed from LAUNCHERS_DIR) is the one launcher-directory constant; copy_launchers() preserves the source file mode on POSIX so the shipped .command keeps its executable bit
- [Phase ?]: 02.1-02: added .gitattributes (text eol=lf) for launchers/itembank.command and launchers/itembank.desktop -- core.autocrlf on a Windows checkout would otherwise silently corrupt the bash shebang / desktop Exec= line build.py copies verbatim into the release directory
- [Phase ?]: 02.1-03: start_server() (not _bind(), which has no browser-opening code) is where the already-running webbrowser.open() call site lives; wired the real two call sites in daemon.py instead of adding a dead window param -- CONTEXT.md's own line-number caveat anticipated this
- [Phase ?]: 02.1-03: cmd_daemon's effective no-open is a.no_open or not cfg['daemon']['open_browser'] -- open_browser's first-ever reader in the codebase
- [Phase ?]: 02.1-04: gift_item's build (and any unrecognized type) branch is one generic fallback -- not a build-specific case -- per the important_note reserving the tailored refusal contract (locked wording, --strict promotion, unescapable-field detection) for plan 02.1-06
- [Phase ?]: 02.1-04: export_gift() returns exit code 1 when anything was skipped, 0 otherwise -- the plan's own resolution of an unspecified exit-code gap, matching cmd_lint's precedent
- [Phase ?]: 02.1-06: GIFT_CODES carries exactly three refusal codes (gift.type_unsupported, gift.field_unescapable, gift.strict_divergence); the pre-existing default-mode multi warning from 02.1-04 stays uncoded per the plan's own instruction to leave that behaviour unchanged
- [Phase ?]: 02.1-06: the real Moodle sandbox import (D-04's manual layer) could not be attempted -- this executor's tool set has no browser/computer-use capability -- recorded PARTIAL per D-05 and tracked as an open item in .planning/WINDOWS.md
- [Phase ?]: 02.1-05: check_latest reads ITEMBANK_GITHUB_TOKEN from the environment itself (D-09) when no explicit token is passed; found and fixed while writing the token-secrecy test, committed separately from Task 2's own commit
- [Phase ?]: 02.1-05: should_check()'s rate-limit clock is the manifest's own checked_at field, not a second sibling file -- write_manifest's four parameters double as both what's currently trusted and when that was last verified
- [Phase ?]: 02.1-07: install()'s SHA256SUMS.txt fallback is resolved by cmd_update (a new _checksum_fallback helper), not inside install() itself -- install()'s locked 5-argument signature has no url to fetch from, keeping it network-free
- [Phase ?]: 02.1-07: background_check(root, cfg) treats root as the literal base directory (like read_manifest/write_manifest/should_check), not update_root() internally -- lets a test isolate it from the real per-user data directory
- [Phase ?]: [Phase 02.1] 02.1-08: AuthStrippingRedirectHandler overrides redirect_request only and calls super() first -- stdlib decides whether a redirect is legal, the subclass only strips; the origin comparison resolves a missing port to the scheme's default (https->443, http->80) so a url that spells its default port out does not read as a different origin, and the stripped state is sticky because each hop's Request is built from the previous hop's headers
- [Phase ?]: [Phase 02.1] 02.1-08: _github_token_for fails closed -- the token comes only from ITEMBANK_GITHUB_TOKEN (D-09 unchanged) and is returned only for github.com, api.github.com, or a .github.com subdomain, refusing even an explicitly-passed token for any other host, because a release document naming a foreign download url is API-supplied data, not a trustworthy source for the decision to hand it a credential (T-02.1-38)
- [Phase ?]: [Phase 02.1] 02.1-08: the plan's Task 2 test-helper rename (patched_urlopen -> patched_transport on the _open_request seam) collided with Task 1's already-implemented opener-injection helper which had taken the same name; resolved by renaming the Task 1 helper to patched_opener_transport (it injects a transport into the real opener) and giving the seam helper the plan's intended name -- both names now describe what they patch (Rule 3 auto-fix)
- [Phase ?]: [Phase 02.1] 02.1-09: the throttle clock moves into updates/check_state.json (CHECK_STATE_REL/read_check_state/write_check_state), written after every check that reached GitHub whether or not anything was installed -- so should_check throttles from the first check rather than the first install (CR-02), and no placeholder manifest is ever written because handoff() must only trust a real pointer
- [Phase ?]: [Phase 02.1] 02.1-09: status['reached'] on check_latest is the throttle's reachability distinction -- rate-limited (any error status) counts as reached because GitHub charges the 60-per-hour budget for a request that arrived; offline/DNS/timeout does not, so a machine that comes back online checks at its next launch instead of waiting out an interval no request earned
- [Phase ?]: [Phase 02.1] 02.1-09: the disclosure gate writes notified_at alone (never checked_at), so the next launch finds consent satisfied and the clock unstarted and checks immediately rather than a full interval later -- disclosure costs one launch, not one interval; the gate sits after the policy gate so a directory with no itembank.json (opt_in from the schema default) prints nothing and asks nothing
- [Phase ?]: [Phase 02.1] 02.1-09: D-13 stands unrevised and is now documented in three places -- the schema's update_policy description, README's Install section, and CLAUDE.md's Constraints list -- stating the default is opt_in, that this repo's own itembank.json intentionally sets check_on_launch to dogfood the updater, and that the two values are meant to differ; the verifier's alternative (raising the schema default) would make every fresh install phone home by default and was rejected
- [Phase 03]: 03-02: an external [LESSON-SRC:] source wins over an inline ## LESSON section when a bank carries both; the precedence is documented in parse_lesson()'s docstring.
- [Phase 03]: 03-02: the degraded lesson page echoes the bank-author-written directive path (grabbed from the bank text), never the resolved absolute path or the raw OS error text (T-3-07); the reason detail stays with itembank lint because the reader is not a diagnostic surface.
- [Phase 03]: 03-02: warn CSS is template-substituted (__WARN_CSS__) into the lesson page only for the degraded branch, so the plain empty state carries no var(--warn) styling and the two states stay visually distinguishable.
- [Phase ?]: [Phase 3] 03-03: lint(questions, lesson=LESSON_UNCHECKED) uses a sentinel default so 'no lesson data supplied' (skip every lesson check, pre-03-03 callers byte-identical) stays distinct from 'lesson data supplied and there is no ## LESSON section' (every LESSON-REF is unknown, never a skip)
- [Phase ?]: [Phase 3] 03-03: all four lesson lint messages reproduce 03-UI-SPEC.md's Copywriting Contract verbatim (item.lesson_ref_unknown by Qn, lesson.duplicate_heading naming both headings and the slug, lesson.orphan_heading, lesson.src_unreadable), so CI substring greps and authoring agents read the same strings
- [Phase ?]: [Phase 3] 03-03: lesson.src_unreadable echoes the bank-author-written basename, never a resolved absolute path (T-3-09), while the raw OS-error detail stays as the reason -- lint is the diagnostic surface the 03-02 reader defers the detail to
- [Phase ?]: [Phase 3] 03-03: lesson.duplicate_heading is the first BANK-tagged error; bank-level findings trail per-item findings like bank.answer_position_skew, and tests/evidence_roundtrip.py's ordering assertion was extended to admit BANK errors last
- [Phase ?]: [Phase 3] 03-03: accepted lint namespace prefixes live in tests/protocol_roundtrip.py's LINT_PREFIXES and are read (never restated) by the coupling tests, so the tuple, the schema enum and the accepted prefixes cannot drift apart
- [Phase 03]: D-11 executed: --ref filters output to one heading plus its backlinks because the CLI has no anchor to jump to â€” A second matching rule or a render-then-scroll approach would disagree with the slug the tag and anchor already share
- [Phase 03]: lesson_page returns None on a --ref miss so the route, CLI and tests share one render without inheriting an exit path â€” cmd_lesson owns the sys.exit hard stop, keeping the render function exit-free
- [Phase 03]: Resolved the deferred 03-04 backlink-placement quirk: each heading's section renders from its own text/body with its backlinks directly beneath â€” Correct --ref filtering requires per-heading association; the old </section>-re-split nested sections and detached both backlink lists
- [Phase 04]: [Phase 4] 04-02: the day-document adapter was built as one coherent D-08..D-11 implementation, so Task 2's conflict/force assertions passed on first run (no RED); the Task 2 feat commit added the genuinely missing immediately-before-replace revision re-check (TOCTOU closure, T-04-05)
- [Phase 04]: [Phase 4] 04-02: force is a CLI-level second confirmation (--force + --confirm-force OVERWRITE + the conflict's current revision), never a byte-gate bypass -- save(force=True) still requires SHA-256 equality with the fresh bytes and still fails on a third concurrent version
- [Phase 04]: [Phase 4] 04-02: escaped pipes display as literal | and submitted pipes are stored as \| with backslashes escaped first, so _display(_encode(value)) == value; unchanged cells keep their raw bytes because only submitted cells are patched
- [Phase 04]: [Phase 4] 04-02: tests prove exact-byte preservation with a common-prefix/suffix single_replacement helper because difflib SequenceMatcher opcodes are alignment-dependent and non-minimal
- [Phase ?]: 04-03: Accent hex format enforced by theme.py normalization plus schema minLength 7 -- schema_validate.py supports no pattern keyword, and extending the shared validator was outside the plan's file scope.
- [Phase ?]: 04-03: The derived dark accent-soft for the default teal lands exactly on the card color because that is the nearest blend meeting both 4.5:1 pairings -- soft derivation is contrast-first and honestly reported.
- [Phase ?]: 04-03: THEME_CSS is now a computed constant from theme_css(system default); the light warn token moves from #b5760a to the binding #8a5900.
- [Phase ?]: 04-03: The picker fallback reason string is the single source of the exact human copy in both structured and human output.
- [Phase ?]: 04-03: D-07 resolves in favor of one source plus deterministic enforced derivation -- no manual per-mode override path exists in the persisted contract.
- [Phase ?]: 04-04: /api/theme reads only action/source/confirm; any css/path/tokens/config authority field is refused with 400 before any helper runs (T-04-16)
- [Phase ?]: 04-04: same-origin validation applies only when an Origin header is present; netloc comparison normalizes default ports
- [Phase ?]: 04-04: primary actions use the contrast-guaranteed accent-soft/accent pairing instead of white-on-accent, which is not guaranteed in dark mode
- [Phase ?]: 04-04: report empty/partial copy follows 04-UI-SPEC exactly (Nothing has been answered yet. / Some responses still need review. Auto-graded totals exclude them.), superseding the 04-02-era heading
- [Phase ?]: 04-05: study_item composes the runtime's two canonical builders wholesale under an explain member; there is no second explanation allowlist in the surface, so D-12 is enforced structurally rather than maintained by hand.
- [Phase ?]: 04-05: study cards are server-rendered through presentation.surface_shell/state_panel/details primitives with the one theme_css(load_settings(bank_dir)) palette; the client wires only reveal/queue/rating state, never scoring, submission, or a second palette (D-04, D-14).
- [Phase ?]: 04-05: after reveal the Reveal explanation control becomes a quiet 'Explanation revealed' control that keeps focus per UI-SPEC while the revealed/rating groups supply the single primary next action.
- [Phase ?]: 04-05: the embedded CARDS payload legitimately carries explain.correct (study is the deliberate reveal surface, T-04-19 accepted); the no-verdict rule is enforced on client behavior, not on the canonical payload.
- [Phase ?]: 04-05: the locked empty copy 'No study cards match this bank.' comes from the plan's must-haves; the render-error state uses the UI-SPEC study matrix recovery copy 'This card could not be shown. Move to the next card or reload.' with Reload/Choose-another-bank actions.
- [Phase ?]: The force request re-submits against the conflict's current revision (the revision the token is bound to), not the page-load revision; day_document.save's fresh-read gate then catches a third concurrent version.
- [Phase ?]: Day editor conflict/force markup ships server-side with the page; the client only toggles state and wires behavior, so recovery semantics survive no-JS and mid-fetch states.
- [Phase ?]: Token refusals use the same 200 + {status: invalid, reason} shape as every other day edit refusal -- one client error path, no HTTP-status branching.
- [Phase ?]: DAY_CSS migrated onto semantic tokens: --ok/--ok-bg for full/floor states, --bad/--bad-bg for chips/badges, --warn for amber, --accent for interaction only.
- [Phase ?]: 03.1-01: lesson page keeps its own LESSON_TEMPLATE document but composes theme_css + SHARED_CSS + LESSON_CSS in the locked order (surface_shell appends SHARED_CSS last); the composition is imported, never duplicated
- [Phase ?]: 03.1-01: LESSON_CSS uses only the locked project scale sizes (12/16/18/20/32) and 400/600 weights; fonts resolve only via --font-paper/--font-ledger tokens
- [Phase ?]: 03.1-01: --r-2/--r-3 radius tokens landed in SHARED_CSS per UI-SPEC Â§2 ownership (callout contract requires --r-3; Task 1 enumerated voice/measure/leading only)
- [Phase ?]: 03.1-01: [!CHECK: <id>] renders the inert reserved slot and drops the id entirely - no key, no form, no scoring path (D-18)
- [Phase ?]: 03.1-01: Phase 3 warn-note assertions moved from raw var(--warn) grep to the rendered-element contract because SHARED_CSS legitimately carries the token
- [Phase 03.1]: 03.1-02: term_lookup carries an explicit source field ('reader'|'session') -- the append-only provenance UI-SPEC 8.5 owed at first write; the route records source='session'
- [Phase 03.1]: 03.1-02: glossable() includes canonical_key() fragments per the plan's locked set; on any ambiguity it returns False (deliberately conservative)
- [Phase 03.1]: 03.1-02: The /gloss route returns a bare 404 (no event) for suppressed terms, indistinguishable from an unknown slug -- the 8.4-safe branch of the plan's allowed pair
- [Phase 03.1]: 03.1-02: print_gloss:inline ships as one @media print block un-hiding each term's single panel; note count equals distinct-term count by construction (UI-SPEC 16 backstop)
- [Phase 03.1]: 03.1-02: The 8.3 enhancement hook is a vendored inline script carrying the locked unavailable copy, inert on the reader (definitions ship with the page); the sitting fetch-on-open variant is 6.2's fill
- [Phase 03.1]: 03.1-02: model.parse_terms reuses surfaces.lesson's cell splitter via a function-local import -- the plan-mandated reuse without a top-level import cycle
- [Phase 03.1]: 03.1-03: key ids mint through the exact new_item_id()/taken set items use -- no separate key id namespace (research Pitfall 5)
- [Phase 03.1]: 03.1-03: authored cloze grammar is any {{text}} marker -- {{text}} compiles to {{c1::text}} sequentially, {{n::text}} keeps n; on screen the enclosed text renders
- [Phase 03.1]: 03.1-03: C7 closure -- public_item() drops the syllabus [OBJECTIVE:]; study's pre-answer objective chip removed; both render only in explain_payload() behind the verdict
- [Phase 03.1]: 03.1-03: the /key/<id>/review route and `itembank key-review` share record_key_review(); key_review events carry no score and are replayed by Phase 10
- [Phase 03.1]: 03.1-05: style enforcement ships as three cost classes over a closed catalogue (STYLE_CHECK_CATALOGUE) — error severity is earned by construction (structural counts or literal lists) and a style may never raise a check above its catalogue rating (D-13); suppression counts are the report that retires bad checks and locked ids cannot be suppressed (style.ignore_locked fires before the ignore table, T-031-19)
- [Phase 03.1]: 03.1-05: warning calibration is a seam, not a number — STYLE_WARNING_FP_RATES + WARNING_FP_THRESHOLD 0.20 are consumed by Phase 3.2's `itembank calibrate`; StylePrompt.prompt_context emits capped imperatives (default 7, a setting) + exactly one exemplar, placed last, never the ## Voice zone (D-17)
- [Phase 03.1]: 03.1-06: the two OFL-1.1 faces are vendored per the KaTeX precedent (pinned tag/commit, recorded SHA-256 + git-blob SHA-1, license + reserved-names notes beside each file, files shipped unmodified); @font-face lives only in presentation.py's SHARED_CSS token layer with the Georgia/ui-monospace fallback; lesson_layout ("separate" | "inline") is folded into 09-02-PLAN.md before Phase 9 executes with no registry version bump (D-04)
- [Phase 03.1]: 03.1-07: the eight UI-SPEC section-17 gates map to fixtures in 03.1-GATES.md with recorded gaps + human-verify items (cross-browser Popover behavior, ClearType 18px render, 1280/768/375px snapshots); the full-suite green run is recorded as a required action in a python-capable environment, never claimed from this session (approval gate declines python — 03.2-05-SUMMARY precedent)
- [Phase ?]: 13-01: 'itembank sidecar' is the single shell entry point; the --sidecar flag on daemon was removed (plan wording resolved to the command).
- [Phase ?]: 13-01: token gate covers every route except /__itembank__ (401); page navigations are gated because the shell injects the header on every request (13-02).
- [Phase ?]: 13-01: attach failure exits 1 with the 3.3(e) copy, name filled and pid deferred to the shell; attach exits 0 with the already-running line.
- [Phase ?]: select() raises SystemExit on any spec key outside SPEC_FIELDS; each later plan appends its field in the same commit that wires it
- [Phase ?]: D-09 focus pin rides inside the spec dict and is consumed by do_start before select(), keeping the 5-parameter signature
- [Phase ?]: order_shuffled() reproduces the old inline rng.shuffle byte-identically; plan 07-05 owns any seed-literal churn
- [Phase ?]: pair/prereq are pedagogy metadata: excluded from content_fingerprint (D-12), verified with zero hash churn when the fixture was tagged
- [Phase ?]: A pair request serves the whole set adjacently in ascending bank order and raises count to hold it; an unknown pair names the known pair list
- [Phase 6] 06-01: v2 evidence contract confirmed at the Task 1 gate -- response events record integer-or-null hint_tier (null means no tier shown, 0 means tier 0 shown), hint events link session/item/attempt/response with fixed tier index/name, availability, source authored, and unlock path; readers keep accepting v1 events while writers emit v2 (D-15/D-16).
- [Phase 6] 06-01: a genuine wrong practice response unlocks (never shows) the next tier; hint/stumped reveal exactly one fixed tier and append a hint event only when shown -- tier 0 is the lesson pointer and only becomes a hint event at the moment it is actually shown (D-04/D-05/D-07).
- [Phase 6] 06-01: after the authored reveal (tier 5) is shown, the next submit action advances even on a repeat of the last canonical response -- D-06 forbids manufacturing further attempts, and holding the card after full disclosure would do exactly that.
- [Phase 6] 06-01: teaching_outcomes omits a fully-retracted item entirely (D-10 read-side suppression) and never counts stumped as a wrong response; correct-after-tier is only labeled when at least one hint was shown, so two identical correct responses at tier 1 and tier 4 produce different rows (TEACH-03).
- [Phase 6] 06-02: every sitting action goes through session.do_action -- the CLI, /api/*, and the served browser share one adapter, one runtime transition, and one evidence writer; handle_quiz_answer is a compatibility wrapper over the API session, no direct scoring path remains.
- [Phase 6] 06-02: renderer_meta is the ONLY Phase 6 renderer handoff -- one opaque UTF-8 string capped at 256 bytes, discarded before policy/persistence/evidence/response/logs; observation/canvas state belongs to Phase 06.1 and is refused by name on both action envelope and legacy answer form.
- [Phase 6] 06-02: the served browser advances only on runtime-returned advance/complete; a practice hold keeps the card interactive for a materially different retry, the stumped control reveals exactly one fixed tier, and diagnostic/exam responses carry no verdict (score stripped) until their release gates.
- [Phase ?]: INDEX_VERSION 1->2: the disposable index gained a bank column (D-13); the bump alone forces one rebuild and the index stays a cache (delete-and-requery and stale-version rebuild are test-asserted)
- [Phase ?]: 13-02: the shell spawns the externalBin sidecar directly (not Command::sidecar) so the process handle is available for the job object; dev fallback is python itembank.py sidecar.
- [Phase ?]: 13-02: token injection is a shell-local loopback HTTP proxy (WebView2 cannot set navigation headers) - one HTTP transport, proxy adds X-Itembank-Token and strips Origin.
- [Phase ?]: 13-02: POST /cli-twin + 'itembank cli-twin' give the menu its daemon-owned route->CLI mapping; API_ROUTES stays locked at four.
- [Phase ?]: 13-03: the frozen exe is the full CLI entry (sidecar is a CLI mode); the bundled shell passes 'sidecar <dir>'; PyInstaller --add-data carries schemas/styles/fonts because resources.py resolves relative to the frozen root.
- [Phase ?]: 13-03: install-notice values are compile-time defines with !error fail-closed; uninstaller deletes only \ (fixture-proven); NSIS bundling degrades honestly while makensis is absent.
- [Phase ?]: 13-04: one release channel, two manifest formats from the same tag (SHA256SUMS.txt + latest.json/minisign); the shell reads the daemon-owned notified_at record and injects the StatusNotice once into the first HTML page - no second consent store.
- [Phase ?]: User confirmed option-a on both 07-04 gates: distinct selection_mode field (D-11) and a selection event once per sitting plus selection_mode on every response event (D-03)
- [Phase ?]: 13-05: AV/signing decision recorded as the honest unsigned branch (D-11) with real SHA-256; Authenticode/VirusTotal/submission rows are explicit pending, never executed.
- [Phase ?]: D-15 resolved: selection_weights.recency_decay IS the soft penalty (read by phase 7); objective_miss_rate/difficulty_spread retagged to phase 10 and inert
- [Phase 8] 08-01: the tier gate is the five-step algorithm from RESEARCH Pattern 1 — manifest build, strict schema, span, fact, move — fail-closed at every layer; a leaking candidate is dropped whole, never rewritten into a sanitized version (D-06)
- [Phase 8] 08-01: learner_payload is the single constructor surfaces may call; pass -> status+generated, drop/unavailable -> status + null generated, never a reason/tier/fact/provider/detector detail (D-08)
- [Phase 8] 08-01: protected-fragment overlap detection normalizes with casefold + whitespace collapse and a MIN_FRAGMENT_LEN=4 floor so the conservative ambiguity rule stays useful
- [Phase 8] 08-01: the authored-fallback seam reuses the Phase 6 runtime.authored_hint(q, tier, canonical) — not the plan's stated (q, tier) — and keeps the ladder usable at the unlocked tier on drop/unavailable (MODEL-03)
- [Phase 8] 08-02: model_backend became a named profile registry {active, profiles} of fixed records (name, transport hosted_cli|openai_compatible, command|endpoint, model, timeout_seconds, max_output_bytes, context_window, secret_env) plus the top-level suggestion_reveal enum defaulting to after-self-mark (D-22); the shipped default is disabled (active "" + empty profiles), so a fresh install never phones a provider
- [Phase 8] 08-02: the shared profile resolver (surfaces/settings.resolve_profile, re-exported by model_adapter) validates unique names and the two known transports' required fields at read time — settings.invalid_value for a bad registry, adapter.profile_unknown for a missing active name — and DEFERS unrecognized transport names to TRANSPORT_REGISTRY, so a third backend is a registry entry plus a config entry with zero resolver edits (D-27), and an unregistered transport resolves to typed adapter.transport_unknown
- [Phase 8] 08-02: credentials are resolved from os.environ[profile.secret_env] by name at invoke time only; the settings file stores the env-var name, never the value, and the value never enters requests, results, logs, or evidence (D-03/D-15) — enforced structurally by the schema's additionalProperties false and asserted by a flatten() scan over request/result bodies
- [Phase 8] 08-02: the two shipped transports (hosted_cli subprocess, openai_compatible urllib) produce the same normalized request/result shape under a config-only switch, preserving backend class (hosted|local) in private audit metadata (D-17/D-18); every failure family is one typed unavailable result with a named adapter.* code (D-04)
- [Phase 08]: model_interaction and mark_proposal events are registered in KNOWN_EVENT_TYPES and the schema enum in the same commit as each builder (D-23); dedupe is one-generation-per-interaction with retries linked via parent_interaction_id (D-12)
- [Phase 08]: mark_event(proposal_ref=None) folds the reference into the dedupe raw string so accepting two different proposals for the same response records two distinct human marks; the marker != 'human' guard stays byte-for-byte unchanged (D-14/D-23)
- [Phase 08] 08-03: requirements TEACH-07/08/09, MODEL-03, MODEL-05 NOT yet marked complete -- the shared-ID gate (#2388) blocks them because 08-04/05/06 still declare them without SUMMARYs; requirements.mark-complete re-evaluates when the last declaring plan finishes
- [Phase 09.1] 09.1-01..04: audio drill export complete on branch gsd/phase-09.1-audio-export -- one TTSEngine interface + registry (model-backend shape), transcript-only engine, edge-tts (LGPL-3.0 pin) + piper (bundled-binary sidecar decision; the wheel-bearing piper-tts is GPL-3.0-or-later and is NOT imported), assemble_pack one-writer with per-pack/per-item split, /api/export_audio daemon route, digest-stable atomic writes, no evidence write (D-01..D-16 all covered; AUDIO-01..07 marked complete in REQUIREMENTS.md)

### Roadmap Evolution

- Phase 18 edited: folded two-shell decision (IDEA-LEDGER IL-20260816-02) into Phase 18 scope

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

## Phase 14 progress (paused 2026-08-13, waves 1-2 of 7 complete)

3 of 8 plans executed. Stopped at the wave boundary on request; waves 3-7
are planned, checker-passed and unstarted.

| Wave | Plan | State |
|------|------|-------|
| 1 | 14-01 tracer — the token layer end to end | done |
| 2 | 14-02 reader type, rhythm, measure | done |
| 2 | 14-03 `POST /api/teach`, `itembank teach`, the payload boundary | done |
| 3 | 14-04 quiz voice repair, twelve sizes to five, `--edge` | not started |
| 4 | 14-05 the gloss: placement, bottom sheet, hover intent | not started |
| 5 | 14-06 scroll contract and reader section nav | not started |
| 6 | 14-07 the wrong-answer surface, ladder rendered | not started |
| 7 | 14-08 live regions, byte-identity floor, 13.5-GATES.md roll-up | not started |

**D-A and the D-B include are closed and proven on served bytes**, not
inferred: all seven `--space-*` tokens resolve on both the lesson and quiz
documents, which carry four `@font-face` rules each. At base commit the quiz
carried zero of either. **D-D's backend exists**: the six-tier ladder now has
a route and a CLI, walked end to end through all six tiers, and every attempt
to address a tier from a client is refused 400 with the field named.
**D-C is untouched** — the gloss still opens viewport-centred; 14-05 owns it.

Two runtime defects were found and fixed while building the teach route,
both of which would have made 14-07 render a payload that misstated what the
runtime would do:

1. `entitled` could never be true. `_record_from_evidence` derived
   `highest_tier_unlocked` only from tiers already shown, so a tier unlocked
   by a wrong attempt but not yet opened was invisible and `unlock_path`
   always said `stumped`. The `Open the next hint` control was unreachable.

2. `teaching_transition` let a client decide its own entitlement — `hint` and
   `stumped` differed only in the recorded `unlock_path`.

### Owed before Phase 14 closes

- **`/day/sample_plan` declares zero of four fonts.** `surfaces/day.py:1449`
  builds its document from `theme_css(cfg) + DAY_CSS` instead of
  `presentation.surface_shell`, so it never joined the token layer — D-B on a
  third surface. Found by the tracer, deliberately not fixed inside it, not
  waived: it prints above every green build via `REPORTED_FONT_ROUTES`. **It
  needs an owning plan.**

- `surfaces/settings.THIS_PHASE` is stale at 10, so both new teaching settings
  print as `inert -- read from phase 14`. Pre-existing pattern; see
  `.planning/phases/13.5-reading-teaching-surface-quality-pass/deferred-items.md`.

- Gates 4, 5, 10, 11 need a driven browser or a human — jsdom does no layout.
  `13.5-GATES.md` is created by 14-05 and completed by 14-08.

## Session Continuity

Last session: 2026-08-16T21:01:05.004Z
Stopped at: Phase 17A UI-SPEC approved
Resume file: .planning/phases/17A-visual-system-component-foundation/17A-UI-SPEC.md
Deferred human verification: 02.1 (4), 03 (1), 03.1, 04 (7), 05 (2), 09 (KaTeX approval), 10 (1 UI gate), 11 (4), 999.4 (manual Canvas checklist), 999.5 (WINDOWS.md windows 2-3) — see the Deferred Verification table above; 09.1 manual audio-quality checks (see 09.1-UAT.md)
