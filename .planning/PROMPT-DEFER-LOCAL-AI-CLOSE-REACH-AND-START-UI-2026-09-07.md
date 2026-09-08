# Prompt: defer local AI, close the non-AI Reach journey, and start the production UI slice

Run this packet in a fresh Codex task for the `itembank` project.

```text
Continue itembank from the current working tree. Read `AGENTS.md` first. This
task has three ordered outcomes: reconcile the user's decision to defer local
AI, finish the remaining agent-executable Reach evidence without depending on
model output, then implement and verify the first bounded production UI slice.

USER DECISION

The user decided on 2026-09-07 that local AI proposal generation, Ollama
compatibility, and the live qwen3.5:4b proposal gate may be deferred to a
future phase. Preserve the work and evidence. Do not delete the adapter, agent
operation door, fixtures, proposal contract, or failure record. Give the
deferral an owner, trigger, required evidence, and recovery path. Do not treat
the malformed response as fixed or verified.

SKILLS AND AGENT SHAPE

Use `current-state-hygiene` to reconcile live summaries without deleting
history. Use `user-vision` to capture and route the new scope decision while
keeping the user's words separate from interpretation. Use the applicable GSD
planning and execution skills for the new bounded production UI phase. Use the
existing UI audit and selected prototypes instead of restarting design
research.

Use one integration writer for shared code and planning state. The user has
explicitly authorized relevant subagents. Spawn only bounded, disjoint lanes:

1. A read-only Reach and authority reviewer checks that deferring local AI does
   not weaken parser, scorer, evidence, proposal acceptance, or recovery
   authority.
2. A read-only UI contract reviewer maps the selected Measured Field Guide and
   Learning Trajectory Deck prototypes to current production symbols and lists
   the smallest vertical slice.
3. After implementation, an independent read-only verifier inspects the diff
   and reruns the narrow acceptance gates. It must not merely trust the writer's
   summary.

Do not assign two writers to the same files. Do not use subagents for broad
repository rereads, duplicated planning, or work a single writer can verify
locally.

AUTHORITATIVE INPUTS

Read these first, symbol-first where large:

- `.planning/USER-VISION.md` and `.planning/USER-VISION-INBOX.md`
- `.planning/SOURCE-TO-COURSE.md`
- `.planning/AGENT-WORKFLOW.md`
- `.planning/STATE.md`
- `.planning/REACH-MILESTONE.md`
- `.planning/REACH-CLOSURE-INDEX.md`
- `.planning/AUDIT-REMEDIATION-PLAN-2026-09-06.md`
- `.planning/UI-CHARACTER-AUDIT-2026-09-06.md`
- `.planning/PROMPT-EXTENSIBLE-UI-CONTINUATION-2026-09-07.md`
- `.planning/notes/2026-09-07-home-and-transition-ui-scope.md`
- `.planning/phases/19D-math-1400/19D-01-PLAN.md`
- `.planning/phases/19D-math-1400/19D-VERIFICATION.md`
- `.planning/phases/19D-math-1400/19D-DEFECTS.md`
- `.planning/phases/19D-math-1400/19D-WALKTHROUGH.md`
- `prototypes/17c-finalists/field-guide.html`
- `prototypes/17c-finalists/trajectory-deck.html`

Before editing, inspect git status and the current diff. The working tree is
shared and dirty. Preserve all user and concurrent-agent work. Never reset,
stash, or bulk-stage it. Verify whether a claimed change already exists before
implementing it again.

PACKET A: RECONCILE THE REACH CONTRACT

Update the durable planning state so it states all of the following without
rewriting history:

- Local AI proposal generation is deferred, not failed closed as the active
  Reach blocker.
- The existing malformed-output defect remains open under a future owner and
  trigger.
- A generated treatment is no longer required for the current Reach exit.
- Reach still requires a representative source-grounded Math 1400 lesson and
  assessment accepted through existing deterministic content, validation,
  scoring, evidence, journal, and recovery authorities.
- Manually or previously prepared content may satisfy the treatment input only
  after source, provenance, objective alignment, lint, and review gates pass.
- No agent may fabricate learner mastery, human accessibility approval, a cold
  install, or a settled prose grade.

At minimum reconcile USER-VISION, SOURCE-TO-COURSE if its active summary is
stale, STATE, REACH-MILESTONE, the 19D plan and evidence records, the closure
index, and the idea or disposition ledger. Prefer append-only amendments and
small current-state replacements. Record superseded text rather than leaving
two active next actions.

Run the vision and planning consistency checks appropriate to those files.

PACKET B: FINISH AGENT-EXECUTABLE REACH EVIDENCE

Use the already prepared or approved Math 1400 lesson and bank if they remain
valid. Otherwise make only the smallest source-grounded repair needed. Do not
invoke a local or hosted model to generate course content.

Through the product's public controls, verify one continuous representative
journey: shelf, course, source locator, lesson, permitted help, practice,
formal test, changed-demand transfer, private note capture, exact resume,
source return, evidence with denominator and uncertainty, next activity, and
home. A controlled verification sitting may prove product behavior. Label it
as product evidence and never as evidence about the user's learning.

Then verify export, manifest, isolated clean-root restore, loss reporting, and
every applicable F-LOSS-1 through F-LOSS-5 condition. Exercise acceptance and
byte-identical undo only for content entering through an already authorized
public non-model path. Do not invent a model proposal to satisfy the old gate.

Run targeted phase gates, then quick and full preflight once on the exact
candidate revision. Attribute inherited, intermittent, platform-only, and
human-only failures precisely. A deterministic red gate blocks only the
outcome it actually tests.

Close Reach with `Reach achieved, broader vision and human legs open` only if
the revised representative journey and recovery gates pass. Keep these open
with named owners when they cannot be executed here: human screen-reader,
keyboard and visual acceptance, instructional-quality review, second-person
cold install, Windows rebuild, packaged-app recovery observation, and signing
choice.

PACKET C: FIRST PRODUCTION UI SLICE

After Reach state is reconciled, create the smallest proper post-Reach UI phase
or phase plan. Do not append UI implementation to the 19D commit or evidence.
Do not repeat the completed UI character audit or prototype selection.

Implement one production shelf to course overview to lesson to practice slice
that proves:

- Measured Field Guide and Learning Trajectory Deck are two presentation
  profiles over identical semantic markup, routes, content, session state,
  scoring, disclosure, and evidence.
- Shared semantic roles, minimum foundation tokens, and only the primitives
  exercised by this slice exist in one implementation.
- Settings provides profile preview, save, visible fallback for unknown values,
  versioned export, and a recoverable migration or removal path.
- Switching profiles preserves route identity and current activity. Preserve
  reading position and focus where the current architecture can prove them.
  Record a bounded defect if either requires a later primitive.
- Desktop, 375px, and 320px layouts remain usable. Keyboard focus, contrast,
  reduced motion, unavailable states, and plain or no-script fallbacks have
  deterministic checks where possible.
- Both profiles consume the same capability adapter for at least one real
  lesson or practice capability.

Do not build a universal component library, external package loader, framework
rewrite, third renderer, automatic task-based profile switching, per-course
profile override, or comprehensive migration of every surface. Do not change
the parser, runtime scoring, keyed disclosure, canonical file formats, evidence
authority, or route identities.

The UI gate is before-and-after evidence for identical representative content
in both profiles at desktop and mobile widths, plus targeted browser and
roundtrip tests. The independent verifier must inspect actual rendered state
and the diff. Human screen-reader and aesthetic acceptance remain owed even if
automated semantics and browser measurements pass.

COMMITS AND RETURN

Follow repository commit discipline. Make one atomic commit for the completed
Reach reconciliation and closure packet only after its gates pass. Make a
separate atomic commit for the UI plan or implementation packet only after its
own gates pass. Stage files by explicit path. Do not commit unrelated dirty
work. If the existing dirty tree prevents a safe atomic commit, stop before
committing and report exact overlapping paths rather than hiding or discarding
them.

Return:

- exact changed paths and commits,
- tests and observed journey evidence,
- the local-AI deferral owner and trigger,
- Reach outcomes verified, deferred, and human owed,
- UI slice acceptance results in both profiles,
- subagent findings and how they changed the work,
- unresolved defects with one next action,
- large modules sampled rather than read in full.
```
