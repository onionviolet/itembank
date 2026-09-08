# Milestone: reach

**Status:** adopted 2026-09-05 by Weibao ("skip the freeze and make everything
beginnable"). Proposed the same day after the measured gap pass in
`.planning/research/2026-09-05-what-the-vision-still-needs.md`, whose findings
are the whole argument for it.

**Predecessor:** the source-to-course milestone, which exits through 17B's gate
record. That exit and 17C's audit remain owed Weibao's acceptance and are no
longer sequencing blocks; see "Freeze policy" below. Nothing here replaces or
reopens them.

## Freeze policy for this milestone

Weibao waived the freeze-before-start ordering on 2026-09-05. Every phase in
this milestone is **beginnable now**, and a phase may execute its plans and
record its gate results without waiting on any human signature. What changes is
only the label: a phase whose human legs are unsigned closes as
**`executed (human legs owed)`** rather than `frozen`, and the owed legs stay
listed in `STATE.md` until Weibao signs them.

Two things the waiver does not touch, because they are correctness rather than
ceremony: the deterministic gates still have to pass (an executor may not
record a red gate as green), and an agent still may not sign a leg reserved to
a human (17B-CONTEXT D-04). Deferred is honest; self-certified is not.

## Why this milestone

The source-to-course milestone built the engine and did not build its doors.
Measured on 2026-09-05:

- 387 KB of course engine across eleven modules, frozen, under 107 test files.
- A JSON API of 15 routes, every one of them assessment, lesson, source
  import, or a first-run shelf action.
- Every `/course/` route a GET, including `build`, which the product contract
  defines as where proposals, diffs, approval, rejection, and undo live.
- 47 CLI commands, none course-shaped.
- `surfaces/agent_operation.py` complete and imported only by the screenshot
  generator.
- `model_backend.active` set to `""`, which the settings schema documents as
  disabling model calls entirely.
- One real sitting, 2026-08-24. No Math 1400. No CSCI 1100.

So the north star is unchanged and the constraint is reach. This milestone adds
no capability. It gives what exists an entrance, turns the product's own AI path
on, and then uses it on a real course.

## What this milestone does not do

- No change to the bank format, the lesson contract, the item types, or the
  scorer.
- No new durable object. No second parser, scorer, or evidence store.
- No new visual system work. 17A is frozen; its owed leg is a human
  accessibility pass, not a redesign.
- No answer to the TypeScript-frontend question. Routes that do not exist
  cannot be consumed by any frontend, so that question stays open and stays
  after this.
- No new research. The Phase 16 corpus got nothing wrong.

## Phases

### Phase 19A: Course operating surface

**Goal.** Every course operation the engine already implements is reachable as
a route with a CLI twin, under the existing `SURFACE_PARITY` discipline, with
its request document published in `schemas/`.

**Depends on:** 14A, 14B, 14C, 15A, 15B (all frozen). Not on 17B's acceptance,
because it adds no durable object and changes no frozen contract. Under the
2026-09-05 waiver it may also close as executed before that acceptance exists.

**Freeze gate.** A course is created, sources bound, objectives mapped,
treatments chosen, audited, and packaged **entirely through routes and CLI
twins**, with no direct module call anywhere in the transcript, and the
existing `SURFACE_PARITY` test green. The 17B fixture course is rebuilt this
way and compared to the committed one.

**Context:** `.planning/phases/19A-course-operating-surface/19A-CONTEXT.md`.

### Phase 19B: The agent operation door

**Goal.** `surfaces/agent_operation.py` bound to one route and one CLI twin, so
an accepted agent proposal is exactly one `journal.commit_operation` with a
visible undo, reachable from the Agent tab and from an agent client.

**Depends on:** 19A, for the door it hangs on. 17A-07, which shipped the state
machine.

**Freeze gate.** One proposal accepted from the Agent tab and one from an agent
client over the API, each producing exactly one applied journal entry, each
undone and re-verified. The Agent tab's skill buttons run something, which is
the literal 2026-08-21 complaint.

**Boundary, restated because it is the one that matters.** Reach, not
authority. The agent may operate what the learner can operate and propose what
an author can propose. It may not settle a mark or release a key.

### Phase 19C: Backend on, and the first real director run

**Goal.** A local model profile made active, and the director, the treatment
recommender, and the seeding loop run against real material for the first time
in this working copy.

**Depends on:** nothing in this milestone. It can run first, in parallel with
19A, because it is a settings change plus honest reporting.

**Freeze gate.** A recorded run whose output is kept verbatim, with whatever it
produced judged plainly, and every defect routed to its owning subphase rather
than repaired opportunistically. A run that produces poor output still passes
the gate; a run nobody looked at does not.

**Registered basis:** `IL-20260905-08`. ROCm 7.2 reached out-of-the-box parity
for Ollama, llama.cpp, LM Studio, and vLLM on RDNA 3 in March 2026, which is
what changed since the profile was written.

### Phase 19D: Math 1400, through the doors

**Goal.** A real Math 1400 course, built with 19A's routes, 19B's agent door,
and 19C's backend, from an open-licensed algebra source, and sat at least once.

**Depends on:** 19A, 19B, 19C.

**Freeze gate, and the milestone exit.** The course exists, was built through
the product's own surfaces, was sat, and its defects are recorded. Per fork 4
of the gap pass, this exit is measured in use rather than in a gate record; the
gate machinery stays underneath it unchanged as the correctness floor.

**Registered basis:** `IL-20260905-05`. The licence is read per title at
binding time and recorded in rights state, never inferred from the publisher.

### Phase 19E: The MCP tool table (discharges Phase 999.3)

**Goal.** The stdio MCP server of 999.3, generated from `API_ROUTES` as its
success criterion 1 already specifies, now that the table contains course
operations.

**Depends on:** 19A. This is the sequencing finding of the gap pass: 999.3 is
not blocked on MCP work, it is blocked on there being routes worth exposing.
Built before 19A it would expose fifteen assessment tools and no course tools.

**Freeze gate.** 999.3's eight success criteria, unchanged, plus one addition:
an agent client builds a course through the tool table alone. That is the
acceptance test for 19A as much as for this phase. If the generated tools can
build a course, the routes are right.

**Design basis:** MCP specification revision 2026-07-28, still current as of
2026-09-05. `scripts/ocr_mcp.py` is existing in-repo precedent for the
transport.

## Order

```
19C  (settings, independent, cheap)
19A  (the load-bearing phase)
 |-- 19B  (agent door)
 |-- 19E  (MCP tool table, and 999.3 closes)
      \
       19D  (Math 1400, and the milestone exits)
```

19C first or beside 19A, because it is cheap and its findings feed 19D. 19A
before everything else that matters. 19B and 19E are independent of each other
and both depend only on 19A. 19D is last by definition; it is the exit.

### Execution budget, 2026-09-07

Finish Reach with one active writer and at most three new executable plans:

1. Finish the existing 19A-09 packet and its blocked publication gate. Do not
   create another 19A plan.
2. Write one vertical plan for 19B and one vertical plan for 19E. Each plan
   includes implementation, its route or transport acceptance run, undo where
   applicable, and targeted verification.
3. Repair the two diagnosed 19C backend-path defects as one bounded direct
   packet, then rerun the recorded diagnostic. This is completion of observed
   failed behavior, not a new research or planning phase.
4. Write one vertical 19D plan only after the 19A, 19B, and repaired 19C doors
   exist. That plan owns the representative Math 1400 build, sitting, defect
   routing, and milestone-exit evidence.

These are ceilings, not quotas. Do not create separate research, pattern,
review, summary, or verification plans unless a targeted gate exposes a named
unsettled decision or the repository requires an independent gate. Reuse the
existing contracts and cited evidence. A normal successful packet records its
result in its commit and gate output under the B1 summary exception.

## Exit criterion

A real Math 1400 course, built through the product's own doors, sat at least
once, with its defects recorded and routed. Not a gate record over a fixture.

The completion label is **Reach achieved, broader vision and human legs open**.
Do not label this milestone as full user-vision completion or all-audits-closed.
An applicable correctness, lost-work, navigation, or unusable-content defect
blocks the affected Reach outcome until it is repaired and the failed step is
rerun. A deferred breadth item or unsigned human leg remains named and does not
become an agent-certified pass.

### Scope amendment, 2026-09-08

The user deferred live local-AI proposal generation and said, "we can skip the
sitting for now." For milestone sequencing, Reach closes under that explicit
waiver and Phase 20 may begin. This revises the current exit criterion without
rewriting the observed record: the Math 1400 source, objectives, direct
reading, shelf, course route, and Agent entry are verified; the live proposal,
accepted generated treatment, new sitting, learner evidence, recommendation,
and dependent export and restore observation are deferred with owners and
triggers in `REACH-CLOSURE-INDEX.md` and the 19D defect ledger.

The completion label remains **Reach achieved, broader vision and human legs
open**, now qualified by the waiver above. It does not claim the deferred legs
passed. Runtime scoring, keyed disclosure, evidence, content acceptance,
rights, and recovery authority remain unchanged. A later release that claims
Math 1400 learning outcomes must reopen the representative sitting first.

### Current product priority, 2026-09-06

Visible UI and app coherence take the active writer before the next invisible
course-operation family. Run the bounded R5 course-shell packet first: shelf to
course and back, visible current area, mobile navigation disclosure, and an
actionable empty state. Then resume 19A-06 and the dependency order below. This
is a sequencing change inside Reach. It is not the comprehensive future visual
redesign, and it does not waive any course-operation or recovery gate.

### Vision alignment refinement, 2026-09-06

**Verdict:** 19A to 19E address the access gap, but the original exit above
proves a first use, not achievement of the whole user vision. This is a bounded
review of the current context and four seeds against the source-to-course,
rich UI, prior-file reuse, cost, and first-use vision entries. Historical
implementation plans and runtime behavior were not re-audited.

| Finding | Existing owner | Evidence needed before claiming the outcome |
|---|---|---|
| F1: API and CLI parity do not prove a discoverable learner journey | 19B and 19D, APP family | Start at the shelf and follow visible controls through Learn, Practice, Test, evidence, and back home. Record broken or missing controls without using a guessed URL to bypass them. |
| F2: One sitting does not prove instructional quality | 19D, TREAT-01/02 and ACTIVITY-02 | Review a representative unit against its actual syllabus objectives and source locators. Include justified direct reading, a missing generated treatment, and changed-context application. Record gaps instead of claiming the whole course is covered. |
| F3: Backend output can pass 19C while being unusable | 19C then 19D, AGENT-01/02/03 | Keep 19C as a diagnostic run. Only reviewed, accepted artifacts enter the 19D learner course. Use sitting evidence to propose one next activity with its denominator and uncertainty. |
| F4: A new algebra course cannot prove every subject, file workflow, or external-user experience | 19D plus existing 14A/14B, 17B and 18 evidence | Link existing multi-root, plain-Markdown, restore, and subject tracers. State which real-use and human review legs remain unverified. |
| F5: Working doors do not by themselves feel like one dependable desktop product | 19D, Phase 18, and the UI character audit | Enter through the packaged or canonical browser-served shell. Complete the visible first-use and return journey without a guessed URL or CLI repair. Verify clear operation state, recovery, consistent navigation, and actionable empty states. Keep the second-person cold install and human visual review visible when they remain owed. |

The 19D context must turn F1 to F5 into one continuous representative-unit
walkthrough using the existing contracts. Include a learner note, a rich lesson
with a useful plain-file fallback, resume after leaving, and an accepted agent
change that can be undone. Reuse existing fixtures and verification evidence
for lower-level invariants instead of rebuilding their suites.

Correctness, lost-work, navigation, and unusable-content defects that prevent
this walkthrough keep its affected outcome unmet until repaired and rerun.
Other findings receive an owner and next action in the existing defect record.
The freeze waiver remains in force. An agent records an unsigned human leg as
owed and never treats it as visual, accessibility, or learning-quality approval.

Start 19D's source and objective preparation as soon as its read inputs exist.
Run the first unit when its required 19A/19B/19C operations exist, then repeat
only affected steps as remaining operations land. Full phase closure retains
the declared dependencies. 19E remains a milestone deliverable with its own
gate and is not an extra prerequisite for the 19D learner walkthrough.

This refinement implements the 2026-09-06 request to check plans against vision
and reduce future waste. It extends the 2026-08-21 cost and useful-product
direction. It creates no new capability or phase and retires no viable idea.

### Post-Reach closure map

Reach closes only the entrance and representative-use gap. The following work
survives as one post-Reach decision surface rather than being mistaken for
completion:

| Open outcome | Evidence required | Existing owner or next route |
|---|---|---|
| Human accessibility, visual, and instructional acceptance | Signed representative screen-reader, visual, and learning-quality walks | 17A, 17B, and 19D human legs |
| Clean portable recovery | Each applicable F-LOSS-1 to F-LOSS-5 repaired, packaged, restored on a clean machine, and rerun without silent loss | 14B and 17C loss owners, exercised by 19A-08 |
| External first use and onboarding | Second-person cold install, removable sample, first-run guidance, and return journey | Phase 18 continuation |
| Comprehensive visual character | Comparative prototypes across representative states, user selection, accessible implementation, and recoverable settings migration | Future visual phase under the UI character audit |
| Broader course and capability evidence | More than one course and subject, plus triggered note, OCR, annotation, or executable-treatment prototypes | Registered roadmap items after 19D defects are routed |

After 19D, classify every observed defect into one of these owners. Promote
only defects that block the representative Reach journey into immediate repair.
Keep the rest in the existing owner or disposition ledger. Do not create a new
general audit phase merely to copy these rows.

Before Reach closes, publish one compact audit closure index linking every
current vision, UI, recovery, human-gate, and external-install finding to one
of five states: verified closed, human owed, deferred with trigger, superseded
with replacement evidence, or rejected with reconsideration condition. Open
items may remain under the broader-vision label, but unowned or ambiguous
“later” items may not. The index links to owning evidence and does not create a
subplan for each finding.

The 2026-09-06 SaaS-quality desktop direction sharpens F5 without changing the
milestone architecture. Phase 13's Tauri shell remains the container. Phase 18
owns install and first-run evidence. The UI character audit owns the bounded
presentation proposal. Phase 19D proves that the connected experience works as
one learner journey. Hosted accounts, storage, and billing remain outside this
milestone.

**Review checks:** `python3 scripts/preflight.py --quick` passed on 2026-09-06.
Runtime and JS suites were not run for this planning-only edit.
`python3 scripts/vision_audit.py` found no missing paths, missing planning
effects, or orphaned entries. Its ten existing missing-relationship notes
remain open in the vision record and are not repaired by this bounded review.

## What is owed to Weibao, blocking nothing

1. ~~Acceptance of this milestone proposal.~~ Given 2026-09-05.
2. The 17B milestone acceptance signature, the G4 screen-reader walk, the G8
   visual acceptance, and the G5 default rollup choice.
3. Acceptance of 17C's audit report.
4. The Phase 18 second-person cold install.

Under the freeze policy above, none of 2 to 4 blocks any phase from starting or
from closing as executed. They are carried in `STATE.md` as owed legs and are
what convert an executed phase to a frozen one.

## Starting points

The only ready execution packet is the existing 19A-09 publication closure.
19C's diagnostic gate ran and exposed two backend-path defects that must be
repaired and rerun before 19D. After 19A closes, create one plan each for 19B
and 19E from their settled milestone goals and gates. Do not run a separate
context-expansion pass unless implementation finds a decision the milestone
does not settle. Create the single 19D plan last, when its required doors
exist. The remaining plan-file budget is three.
