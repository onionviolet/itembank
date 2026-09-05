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

## Exit criterion

A real Math 1400 course, built through the product's own doors, sat at least
once, with its defects recorded and routed. Not a gate record over a fixture.

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

Every phase below is beginnable today. 19C and 19A have no unmet dependency at
all; 19B and 19E need 19A's routes to exist; 19D needs all three. 19A is the
only phase with a written context (`19A-CONTEXT.md`, ten decisions pinned,
ten plans, one operation family each), so it is the one an executor can plan
straight from. The other four need a context pass before their plans.
