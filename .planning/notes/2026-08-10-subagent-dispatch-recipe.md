# Subagent dispatch in this runtime: what works (2026-08-10)

- **Status:** VERIFIED this session (six controlled spawns, disk-verified).
- **Purpose:** a reproducible recipe for other chats that need to dispatch
  subagents from this Codex desktop runtime.

## TL;DR

- **Spawn-message payloads are DROPPED** for `fork_turns="none"` spawns. The
  subagent itself confirmed it: `"no message payload arrived with this turn"`.
  It does not matter whether the message uses an absolute path, a relative
  path, or inline task text — nothing arrives.
- **Fork-context delivery WORKS.** With `fork_turns="all"` (also tried `"2"`
  and `"1"`), subagents receive the parent conversation context and act on
  it: they wrote files, designed their own probe experiments, and one spawned
  a sub-subagent. This is the only channel proven to deliver task content.
- **But fork delivery is mission-shaped, not instruction-shaped.** The agent
  inherits *all* parent context, so it drifts to the broadest task it can
  infer, runs long, and may not complete the exact artifact. In this session
  every fork-based probe engaged; **zero** completed the exact 9-byte target
  file within bounded waits (status stayed `running` until interrupted).
- **Net recipe:** fork-based dispatch + a self-contained brief file + disk
  verification + inline fallback. Never trust the reply text; never trust
  that the spawn message arrived.

## The recipe (reproducible steps)

1. **Write the COMPLETE task to a file first** (all agents share the
   filesystem). Make the brief self-contained: exact absolute paths, exact
   expected artifact and content, and explicit guards — *"Ignore any other
   context you inherited. Create no other files. Spawn no agents."*
2. **State the brief path and expected artifact in your own chat text
   immediately before spawning.** That text is what the fork carries.
3. **Spawn a generic subagent** (no `agent_type`), with
   `fork_turns="all"` (safest for delivery) or a small positive fork
   (`"1"`/`"2"` — leaner, less proven). The spawn `message` should be a
   one-line pointer to the brief: it is best-effort only and may be dropped.
4. **Wait once, bounded** (e.g. a few minutes), then **verify the artifact
   on disk byte-for-byte**. Do not rely on the subagent's reply.
5. **Fallback:** if the artifact is missing or the agent drifts (starts
   unrelated work, spawns children, sits `running`), interrupt it, re-dispatch
   once with the brief path restated, then **do the work inline** and
   document the deviation.

## Evidence table (all verified on disk)

| Probe | fork_turns | Spawn message | Result |
|-------|-----------|---------------|--------|
| probe_payload (earlier turn) | none | pointer, backslash path | completed idle; no file |
| probe_pathfmt | none | pointer, relative path | completed: *"no message payload arrived with this turn"*; no file |
| probe_forkall | all | pointer to brief | engaged fast (wrote 3 probe briefs), then hung; interrupted |
| probe_fork2 | 2 | pointer to brief | engaged; spawned sub-subagent `probe_d_pointer_fork2`; interrupted |
| probe_recipe | 2 | pointer + guard-heavy brief | ran 8+ min, no file; interrupted |
| probe_min | 1 | inline task text | ran 4+ min, no file; interrupted |

## Pitfalls

- **Do not leave the broad mission in the parent context near the spawn.**
  The fork inherits everything; agents will chase the biggest task they can
  see (observed: fork agents re-ran the experiment design instead of the
  simple write task).
- **Concurrent sessions share this workspace.** During these probes another
  Codex session was actively editing phase files (08-*, UAT, `.gsd/tmp`
  briefs). Keep probe/worker artifacts in a dedicated directory
  (`.planning/probes/`) and never assume only your agents touch the repo.
- **Status is not completion.** Fork agents can sit `running` indefinitely
  without landing files; use bounded waits + `interrupt_agent`.

## Ready-to-paste template for another chat

```text
1. Create .planning/probes/PROBE-BRIEF.md containing ONLY:
   - exact absolute path of the artifact to create
   - exact required content (byte-exact)
   - "Ignore any inherited context. Create no other files. Spawn no agents."
2. In your own message, write: "Subagent task: read
   .planning/probes/PROBE-BRIEF.md; expected artifact <path>."
3. spawn_agent(task_name="worker_x", message="Read .planning/probes/PROBE-BRIEF.md first; that file is the complete task.", fork_turns="all")  # no agent_type
4. Wait once (bounded), then verify <path> on disk byte-for-byte.
5. If missing/drifted: interrupt, re-dispatch once, then inline with a
   documented deviation.
```
