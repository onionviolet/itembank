# Phase 20 sequential continuation and daisy-chain packet

GOAL: Finish the next safe portion of Phase 20 from the current shared working
tree, verify it, and create a fresh continuation task for the following portion
when meaningful Phase 20 work remains.

OWNER: Weibao owns product-scope changes and aesthetic acceptance. The active
task owns bounded implementation and deterministic verification.

BUILDER: Use the `efficient-agent-routing` skill. Prefer one capable Balanced
tier writer at medium reasoning for each tightly coupled wave. Use a read-only reviewer only
when a concrete independent verification benefit exists. Keep one writer per
file and plan.

VERIFIER: The active task reviews the actual diff and reruns the narrow gates.
Do not treat a builder summary as proof. A later independent task may verify a
completed wave if the changed authority or migration behavior warrants it.

SCOPE:

1. Read `AGENTS.md`, `.planning/STATE.md`, the Phase 20 plans, context, UI spec,
   crosswalk, and the latest matching summaries. Inspect `git status` and the
   current diff before editing.
2. Resume Plan 20-01 after completed Tasks 1 and 2. Finish only deterministic
   Task 3 transition and degraded-state behavior that can be proven with
   synthetic fixtures. Do not run a real Math 1400 sitting.
3. Record Task 4 human visual and screen-reader review as skipped by explicit
   user direction, not passed or certified. Automated accessibility and
   responsive checks still run.
4. Close 20-01 only if its revised deterministic gates pass. Then continue
   plans 20-02 through 20-05 strictly in dependency order, one bounded plan or
   coherent wave per task when context allows.
5. If work remains after the current bounded portion, create a new Codex task
   in this same saved project and local checkout. Its prompt must invoke
   `efficient-agent-routing`, reference this packet, name the exact next plan or
   failed gate, include current evidence, and repeat the no-human-review and
   no-real-sitting boundaries. Emit the created-task directive in the return.

DO NOT TOUCH: Do not reset, stash, discard, or bulk-stage the dirty working
tree. Do not overwrite user or concurrent-agent changes. Do not create a second
parser, scorer, evidence authority, route table, renderer, state store, or
external package loader. Do not change canonical question formats, runtime
scoring, keyed disclosure, evidence ownership, or course identity. Do not
repair local Ollama proposal generation in Phase 20.

CONTEXT:

- Reach closed for sequencing under the 2026-09-08 user waiver. Local AI, the
  new Math 1400 sitting, its evidence and recommendation, and dependent restore
  observation remain deferred and unclaimed.
- Plan 20-01 Tasks 1 and 2 are implemented but not summarized or committed.
  `field-guide` and `trajectory-deck` are recoverable settings values over one
  shared semantic renderer. Saved selection reaches live home, course, lesson,
  Study, and served Quiz output while preserving behavior tokens.
- Focused profile, home, component, serve, stylesheet, visual-accessibility,
  vision-audit, and quick-preflight gates passed. `daemon_roundtrip.py` has an
  existing concurrent-request timeout. Investigate only if the current wave
  changes that behavior or a narrower deterministic reproduction fails.
- The shared tree contains extensive preexisting changes. Commit only when the
  user explicitly asks. If asked, stage exact owned paths only.

TOOLS NEEDED: Local repository tools and deterministic test fixtures. No model
backend, remote service, real learner sitting, or human-review checkpoint is
required for this continuation.

GATE: For each bounded plan, run its targeted tests plus `python3
scripts/preflight.py --quick` and `git diff --check`. Run full preflight once on
the final Phase 20 candidate. A skipped human gate is reported as skipped. It
does not block this user-requested showcase pass and does not become a pass.

RETURN: Exact changed paths, tests and outcomes, deferred or skipped gates,
unresolved defects with one next action, large modules sampled rather than read
whole, and the next created task when Phase 20 work remains.
