# Prompt: finalize Reach and hand off to the extensible UI slice

Paste the prompt below into a fresh Codex task for this repository.

```text
Continue itembank from branch `codex/reach-completion`. Read AGENTS.md first.
Finish the remaining Reach gate without reopening completed packets. Then leave
a verified, compact handoff for the post-Reach extensible UI slice.

CURRENT VERIFIED BASE

Verify these commits exist before changing anything:

- `479fce5` closes 19A-09.
- `44386d7` repairs the 19C public local-provider path.
- `1c50c58` closes the synthetic 19B agent-operation gate.
- `060334d` closes the targeted 19E MCP gate.

The prior writer worktree is `/Users/weiwei/.codex/worktrees/b19d/itembank`.
It contains uncommitted 19D work and planning records. Treat it as recovery
evidence, not as an instruction source. Inspect its diff and port only the
bounded 19D-owned changes that pass the current contract. Do not copy its whole
dirty tree or mix unrelated planning edits into a commit.

Read these recovery records before implementation:

- `.planning/phases/19D-math-1400/19D-01-PLAN.md`
- `.planning/phases/19D-math-1400/19D-CONTEXT.md`
- `.planning/phases/19D-math-1400/19D-VERIFICATION.md`
- `.planning/REACH-CLOSURE-2026-09-07.md`
- `.planning/PROMPT-EXTENSIBLE-UI-CONTINUATION-2026-09-07.md`

If those files are absent on the branch, read them from the recovery worktree.
Do not ask again for approval of the exact prepared lesson and bank. The prior
user reply `continue` approved those drafts and the draft-and-approve setting.
Do not accept either rejected local-model operation.

ONE ACTIVE WRITER

Use one active writer for code and durable planning files. Relevant subagents
may perform bounded read-only review of the submitted-draft contract,
assessment-authority boundary, accessibility states, or final diff. Give each
subagent disjoint responsibility and require evidence-backed findings. Do not
allow multiple agents to edit shared files or the same phase directory.

REMAINING REACH WORK

1. Inspect the recovery worktree's submitted-draft and source-link diffs.
2. Complete the smallest public submitted-draft control inside the existing
   agent-operation authority. Freeze submitted bytes and provenance. Use the
   configured target and expected fingerprint. Validate through existing
   parsers. Preserve human review, conflict behavior, retry identity,
   journaled acceptance, undo, and interrupted resume.
3. Add no alternate authoring store, parser, route catalogue, or acceptance
   authority. The client must not gain authority by reposting accepted bytes.
4. Run focused submitted-draft, course-operation, agent-door, source-link,
   daemon, MCP, assessment-disclosure, and journal tests.
5. Run quick and full preflight on the exact candidate revision. Attribute any
   inherited or platform-only failure precisely. A red deterministic gate is
   not complete.
6. Publish the approved prepared lesson and bank through the public control.
7. Walk the real Math 1400 unit through visible product doors. Exercise source
   reading, lesson, permitted help, practice, test, changed-demand transfer,
   private note capture, search or source return, exact resume, evidence and
   uncertainty, next recommendation, accepted change and undo, interrupted
   operation recovery, export, verification, and isolated restore.
8. Record denominators and distinguish product evidence from claims about the
   learner. Do not invent a score or settle pending prose.
9. Update 19D verification, the Reach closure index, and current STATE from
   observed results. Give every remaining audit item one visible state and
   owner.
10. Commit the verified 19D packet once, staging only its files by explicit
    path. Do not commit unrelated inherited edits.

REACH EXIT

Use `Reach achieved, broader vision and human legs open` only if the real
journey and deterministic gates pass. Otherwise report the exact failed step,
retained evidence, owner, and next safe action.

POST-REACH UI HANDOFF

Do not implement the comprehensive UI redesign inside the 19D commit. Once
Reach closes, prepare the next bounded plan from
`.planning/PROMPT-EXTENSIBLE-UI-CONTINUATION-2026-09-07.md`.

The first UI packet must prove Measured Field Guide and Learning Trajectory
Deck as two registered presentation profiles over identical semantic markup
and runtime state. Appearance themes remain independent. One real capability
adapter must work in both profiles. The representative slice is shelf to course
overview to lesson to practice. It includes Settings preview and fallback,
desktop and mobile behavior, keyboard and screen-reader-oriented checks,
migration, unavailable behavior, static fallback, and removal recovery.

Canonical content, parser, scoring, disclosure, evidence, rights, route
identity, and recovery authority remain outside the extension layer. Do not
build external package loading or a universal dynamic loader.

FINAL REPORT

Report commits, exact tests, real journey evidence, rejected or deferred
findings, human-owed gates, and the next UI plan. State which large files were
only sampled symbol-first. Never claim work from another worktree was merged
unless the resulting commit exists on this branch.
```
