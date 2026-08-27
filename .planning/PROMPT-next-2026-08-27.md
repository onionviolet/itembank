# Continue: the workspace object, and the decision backlog

Paste this whole file as the first message of a new session.

---

You are continuing work on **itembank** at `/Users/weiwei/Documents/Dev/itembank`
(macOS; earlier handoffs name a Windows path, ignore those).

Read `.planning/EXEC-CONTEXT.md` first, then `.planning/NEXT-2026-08-27.md`.
Do **not** read `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md`, `UI-SPEC.md`,
`AGENT-WORKFLOW.md`, or `PLANNING-DIRECTIVES.md` end to end unless a specific
question needs them. That stack is about 122,000 tokens and re-reading it every
turn is what a previous run spent billions of tokens on. Grep them instead.

`main` is pushed and clean as of 2026-08-27. `.codex/` is untracked and is not
yours; leave it.

## Where things stand

Phase 14A is frozen. **Phase 14B waves 1 to 3 executed on 2026-08-26**, so
`graph.py`, `course.py` and `course_package.py` ship. Waves 4 to 6 are blocked.
Phase 16A is planned and unexecuted, so **Phase 16B's precondition check
HALTS**; that was re-run against the tree on 2026-08-27 and the result is
`.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION-DRYRUN-2026-08-27.md`.
Phase 14C is **fully planned** (eight plans) and also blocked.

**The bottleneck is eight decisions only Weibao can make**, across 14B, 14C and
17A. They are tabulated in `NEXT-2026-08-27.md`. The 14B four have a packet at
`.planning/DECISIONS-14B-DRIVER-2026-08-27.md`; 17A-04's has had one since
2026-08-25.

**Do not stand in for any of them.** Every checkpoint plan carries the sentence
"Do not proceed with a silent default. An unanswered checkpoint stops the wave."
One stand-in was already made on 2026-08-26 under a standing overnight
authorization and is recorded as **provisional** because the call is one-way. A
second on the same phase is the exact pattern that rule exists to prevent. If
Weibao has answered in chat, record the answer and proceed; if he has not, do
the unblocked work below and say plainly that the rest is waiting on him.

## Recent context you will otherwise misread

Between 2026-08-26 and 2026-08-27 a competitor teardown ran (Jones & Bartlett
Navigate2, the EMT course platform Weibao is enrolled in) and produced:

- `.planning/research/2026-08-26-navigate2-teardown.md`, the evidence.
- `.planning/COURSE-SHELL-TEMPLATE.md`, a tentative proposal whose section 0.1
  **withdraws three of its own original ideas** as duplicates of shipped work.
  Read 0.1 before trusting anything else in that file.
- `.planning/research/2026-08-26-shelf-reconciliation.md`.
- `prototypes/16b/`, a course-shelf mockup generated from real 14B records.
- `IDEA-LEDGER.md` IL-20260826-01 through IL-20260827-01.

**One ruling changed the contract stack.** On 2026-08-27 Weibao ruled, verbatim
in `USER-VISION.md`: *"Percent is fine even if it breaks contract, since
uservision over any other contracts and more"*. Two consequences:

1. A percent and an aggregate progress figure are **permitted**. GRAPH-03,
   Phase 16 synthesis 12.4, plan 16B-04 and `16B-RESEARCH.md` were all amended
   on 2026-08-27. Do not re-argue the 2026-08-26 position against it; it is
   settled and the reversal is recorded.
2. **`USER-VISION.md` outranks any other contract in this repository.** That
   precedence rule is general and is not limited to percentages.

One amendment is deliberately outstanding: `16B-DECISIONS.md` `## D7` must be
**authored in its amended form** when plan 16B-01 first creates that file, not
written in the old form and retrofitted. See IL-20260827-01.

## Your job

### 1. The workspace object (the main task)

`IDEA-LEDGER.md` **IL-20260826-01**, narrowed to exactly one gap. The teardown
established that `course`, `container`, `objective`, `treatment` and `package`
all ship. **Nothing names the set of courses.** That set is the top line of the
shelf mockup and the only structural gap between what ships and what the mockup
draws.

Give it a requirement and a home before plan 16B-04 executes, because 16B-04
will otherwise invent one. Open questions to settle in the proposal, not by
fiat:

- Is the workspace a file, or a directory scan, or a set of discovery roots?
  `discovery.py` ships; read it before proposing anything.
- How does it relate to `IL-20260817-01`'s recursive **scope** object, which
  already answers bounded-ness and progress rollup? Reconcile, never duplicate.
- What is its source of truth, authority, degraded behaviour, and recovery, per
  the object-and-authority rules in `.claude/CLAUDE.md`?

Deliverable: a requirement proposal plus a ledger disposition. **Do not open a
phase and do not edit `REQUIREMENTS.md`** without Weibao's word; the 2026-08-27
amendments were applied only because he explicitly said "apply all four".

### 2. If Weibao answers the decisions

Execute 14B waves 4 to 6 in order (`14B-04`, `14B-05`, `14B-06`), recording each
answer in `14B-DECISIONS.md` before the wave that depends on it. Plan 14B-06 is
the freeze gate and writes exactly one of `## Frozen at 14B` or
`## Freeze withheld`. 14B-04 also modifies the frozen `journal.py`, so read
`14A-FREEZE.md` before touching it.

## House rules that will bite you

- **No em dash characters** in anything you author. Commas, parentheses,
  colons, semicolons, or separate sentences. Verbatim quotations in
  `USER-VISION.md` are the only exception. Check with:
  `python3 -c "import io,sys;D=chr(0x2014);print(D in io.open('FILE',encoding='utf-8').read())"`
- **Check the tree before asserting what exists.** Two documents this week
  claimed a blocker that one `ls` disproved: `16B-PATTERNS.md` said 14B was
  unbuilt after it shipped, and `NEXT-2026-08-27.md`'s own first draft said 14C
  was unplanned when all eight plans existed. Both were written from memory of
  the tree. This is the most common failure in this repository right now.
- **Append, never delete.** The rejection and supersession ledger is
  append-only. An overturned decision gets a dated note carrying evidence,
  authority, and what was traded. The 2026-08-27 percent amendments are the
  worked example of the right shape.
- `python3`, not `python`, on this machine.
- Verify with `python3 itembank.py guard .` plus the relevant roundtrip suite in
  `tests/`. Do not trust a commit message over an artifact.
- Commit when the work is coherent; `main` is the working branch here and is
  pushed. Do not push without being asked.
