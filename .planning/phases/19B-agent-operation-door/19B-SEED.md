# 19B seed: the agent operation door

Not a context. A starting note so this phase is beginnable without rereading
the milestone.

**Goal.** Bind `surfaces/agent_operation.py`, which is complete and today
imported only by the screenshot generator, to one route and one CLI twin, so an
accepted agent proposal is exactly one `journal.commit_operation` with a
visible undo, reachable from the Agent tab and from an agent client.

**Depends on** 19A for the door it hangs on, and on 17A-07, which shipped the
state machine.

**The boundary that matters.** Reach, not authority. The agent may operate what
the learner can operate and propose what an author can propose. It may not
settle a mark or release a key. `OPERATION_TYPES` stays at six.

**Gate.** One proposal accepted from the Agent tab and one from an agent client
over the API, each producing exactly one applied journal entry, each undone and
re-verified. The Agent tab's skill buttons run something, which is the literal
2026-08-21 complaint.

**Before planning:** write `19B-CONTEXT.md`, deciding the route shape (it should
follow 19A's per-operation shape rather than inventing a second one), where the
proposal document lives between propose and accept, and what undo shows.
