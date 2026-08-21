---
phase: 17A-visual-system-component-foundation
plan: 07
type: execute
wave: 3
depends_on: ["17A-01", "17A-02", "17A-06"]
files_modified:
  - surfaces/agent_operation.py
  - surfaces/visual_fixture.py
  - tests/agent_operation_roundtrip.py
  - .planning/phases/17A-visual-system-component-foundation/17A-07-SUMMARY.md
autonomous: true
requirements: [AGENT-01, VISUAL-01]
must_haves:
  truths:
    - "One skill run from the Agent area reaches a model only through model_adapter.invoke, and a change becomes real only through journal.commit_operation."
    - "A run produces exactly one journal entry, or zero. Never two, and never a partial write."
    - "Every adapter unavailable code has a named next action on the page, and none of them stops studying, scoring, or authored hints."
    - "report_only autonomy disables accept visibly rather than hiding it."
    - "The runtime settles nothing new. No scoring, no marking, no key disclosure reaches this page, ever."
  artifacts:
    - "surfaces/agent_operation.py, the run-propose-accept state machine, with no HTTP call and no second writer of its own."
    - "tests/agent_operation_roundtrip.py covering the happy path, each unavailable code, the report_only refusal, the double-accept refusal, and the undo."
  key_links:
    - "The page reaches a model only through model_adapter.invoke."
    - "The write goes through journal.commit_operation with an expected base fingerprint."
    - "The undo path is the prior revision journal.commit_operation already records; this plan invents no second one."
---

<objective>
Join the two halves that already exist and do not touch. Make one skill run
end to end from the Agent area, and make the accepted result a real, undoable
change. This is the smallest change that makes "agentic" a description of the
product rather than a description of an embedded window.
</objective>

<context>
@.planning/EXEC-CONTEXT.md
@.planning/phases/17A-visual-system-component-foundation/17A-06-SUMMARY.md
@model_adapter.py
@journal.py
</context>

<findings>
Measured 2026-08-21 during 17A-06, so this plan is sized against what exists.

1. **Both halves are built and neither is wired.** `journal.commit_operation`
   does compare-and-swap with an operation log and a prior revision. The Agent
   panel already reads that journal through `visual_fixture.live_journal`, and
   already classifies reads and external edits as not-undoable. The skill
   buttons on the same page run nothing.

2. **The model boundary is finished.** `model_adapter.invoke` normalizes every
   failure family to one typed unavailable result and raises nothing. The
   shipped `local-qwen` profile reaches Ollama through `openai_compatible`.
   This plan adds no transport and no provider code.

3. **`resolve_profile` refuses every name while `model_backend.active` is
   empty**, including a name passed explicitly. The page must therefore treat
   "no active profile" as the first-class starting state, not as an error.

4. **`auditor_autonomy` ships three levels** (`report_only`,
   `draft_and_approve`, `audit_draft_lint_fix_commit`) and the panel already
   displays which is current. Nothing enforces it, because nothing writes.

5. **The Python SDK for the embedded console is not published.** Checked
   against PyPI 2026-08-21: `deepseek-harness-sdk` does not exist, and the
   `deepseek-harness` name belongs to an unrelated third-party client. The
   stdio seam named in 17A-06-DECISIONS.md has no importable artifact, which
   is why this plan drives the model through the shipped adapter and not
   through the harness.
</findings>

<tasks>
<task type="auto">
  <name>Task 1: the run-propose-accept state machine, as its own module</name>
  <files>surfaces/agent_operation.py, tests/agent_operation_roundtrip.py</files>
  <action>
Write the test first.

Build `surfaces/agent_operation.py` holding one bounded state machine with
four states and no others: `idle`, `running`, `proposed`, `settled`. It is a
pure module: it takes a settings document, a skill name, and a base path, and
it returns a state dict. It makes no HTTP call of its own, opens no socket,
and writes nothing except through `journal.commit_operation`.

`start(skill, settings, base)` builds a request with
`model_adapter.request_from_operation` and calls `model_adapter.invoke`. An
`unavailable` result becomes a `settled` state carrying the typed code, the
adapter's message, and a `next_action` string chosen from a fixed map, one
entry per code in `model_adapter.ADAPTER_CODES`. A missing entry is a test
failure, not a fallback, so a new adapter code cannot ship with no copy.

An `ok` result becomes a `proposed` state carrying the draft, its citations,
and a bounded diff against the current bytes of the target file. The diff is
computed with `difflib`, capped at a stated number of lines, and says how many
lines it withheld rather than silently truncating.

`accept(state, settings)` calls `journal.commit_operation` exactly once with
the expected base fingerprint the proposal was computed against, and returns
`settled` carrying the journal entry id and the prior revision id. A second
`accept` on an already-settled state returns the same state unchanged and
records nothing; the guard is in the module, not in the page, so a double
submit cannot write twice.

`accept` refuses when `auditor_autonomy` is `report_only`, returning a
`settled` state whose reason names the setting and where to change it. The
refusal is a state, not an exception.

A fingerprint that no longer matches is a conflict state naming the file, not
an overwrite. `journal.commit_operation` already enforces this; the page must
report it in words a learner can act on.
  </action>
  <verify>python tests/agent_operation_roundtrip.py exits 0 with no network available and no model running.</verify>
</task>

<task type="auto">
  <name>Task 2: the Agent area drives it, and says what it cannot do</name>
  <files>surfaces/visual_fixture.py, tests/agent_operation_roundtrip.py</files>
  <action>
Replace the fixture skill buttons with the real list, rendered from the skills
that exist under `.claude/skills/`, each with the state machine behind it. A
skill whose command surface has not shipped (the stubs) renders as unavailable
with the reason, rather than as a button that does nothing.

Render each of the four states. `proposed` shows the bounded diff, the
citations, the target file, and Accept plus Reject. `settled` shows the
journal entry and its Undo, or the typed failure and its named next action.

Keep the embedded console from 17A-06 exactly where it is. Two paths ship, per
PLANNING-DIRECTIVES section 1: the console is the open-ended one, this is the
one itembank drives. Add one sentence to the Agent area saying which is which,
so the pair reads as a decision rather than as duplication.

The five unavailable states each get their named next action. No active
profile is first, because it is the shipped state: it names the setting and
the fact that studying, scoring and authored hints are unaffected.
  </action>
  <verify>python tests/agent_operation_roundtrip.py, python tests/local_harness_roundtrip.py, python tests/visual_system_roundtrip.py, python tests/journal_roundtrip.py, and python itembank.py guard . all exit 0.</verify>
</task>

<task type="auto">
  <name>Task 3: prove the undo by using it</name>
  <files>tests/agent_operation_roundtrip.py</files>
  <action>
One test that runs the whole loop against a stubbed endpoint and a temporary
course directory: start, propose, accept, read the file and confirm the change
landed, then undo through the prior revision the journal recorded and confirm
the file is byte-identical to what it was before the run.

Then delete the accept guard and confirm the suite fails, so the
single-journal-entry claim is proven rather than asserted.
  </action>
  <verify>python tests/agent_operation_roundtrip.py exits 0, and exits nonzero with the guard removed.</verify>
</task>
</tasks>

<out_of_scope>
No new transport. No harness SDK, which is not published. No conversation
history store. No scoring, marking, mark proposal, or key disclosure from this
page, ever. No change to `theme.DEFAULT_ACCENT`, which belongs to 17A-04. No
new durable object: this plan writes through the existing journal to existing
artifact types and introduces no assignment, due date, or gradebook object.
Those belong to the UI-flow planning session, not here.
</out_of_scope>

<summary_obligations>
Record the four states and the exact copy for every adapter code, the single
journal entry a run produces with its id shape, the undo path proven by test,
what `report_only` refuses and how it says so, and which skills rendered
unavailable and why.
</summary_obligations>
