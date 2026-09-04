# Runbook: using Ox Alpha to finish the sitting queue, and what comes after

Written 2026-08-25. Companion to
`.planning/PROMPT-finish-the-sitting-work-2026-08-25.md`, which is the queue
itself. This file is about **who executes what**, not about what the work is.

Two hard facts set the shape of everything below.

**The free Ox Alpha preview ends 2026-08-27** (recorded in
`scripts/ox_overnight.sh`, line 31). Counting from the night of 2026-08-25
that is **three nights**, and one of them should be held in reserve for a
re-run. Plan for two productive nights and treat the third as slack.

**Two agents in one working tree lose work.** On 2026-08-24 a second session
committed this tree's index while a first session was mid-commit, and the
first session's message was discarded even though its files landed. The commit
`2c34a65` carries the NREMT lint rule under a message its author did not
write. Nothing was lost that time. Next time the loser will be a half-written
file. `scripts/ox_queue.sh` exists for exactly this and is not optional.

---

## 1. What Ox is good for here, and what it is not

Ox Alpha executes a finished plan well and invents badly. The queue's six
items do not divide evenly along that line, so divide them explicitly.

| Work | Executor | Why |
|---|---|---|
| Item 4, NREMT structural lint | **Done** (`2c34a65`) | Committed 2026-08-24. The rule fires on exactly the one known divergence in the real bank, `q3`, and on nothing else. |
| Item 5, empirical distractor analysis | **Human-led, in flight** | A second session has `evidence.distractor_usage` and a `stats` report half written in this tree. Finish it there. Handing a half-built feature to an unattended agent is how you get two implementations of it. |
| Item 2 step 3, draft autosave | **Ox, after a plan exists** | Bounded, testable, and the decision it needs (client storage, presentation state only, never a second source of truth) is already made and recorded in `080bffc`. |
| The five known-open defects | **Ox, as one plan** | Small, mechanical, each with a named file and line in the queue prompt. This is the single best use of a night. |
| 13.5 defects D1 and D2 | **Ox** | `.planning/quick/260817-q7d-fix-135-defects-d1-d2/260817-q7d-PLAN.md` is written and unexecuted. It needs a prompt path, nothing else. |
| Item 6, calibration and A9 closure | **NOT Ox** | It writes `13.9-CALIBRATION.md` from real learner evidence with two denominators that disagree, and it ticks readiness-audit boxes. Judgement about honest denominators is the whole content of the task, and the existing ox prompts forbid touching `.planning/STATE.md` and the 13.9 phase directory for good reason. Ox may draft the numbers; a human accepts them. |
| 17A-04, `tools/visual_qa.py` | **Ox, once item 6 closes** | A finished plan already exists at `.planning/phases/17A-visual-system-component-foundation/17A-04-PLAN.md`. Its only remaining blocker is the sitting. |
| 14B planning | **NOT Ox** | Planning, not execution. Its plans must cite `13.9-CALIBRATION.md`, which does not exist yet. |

The rule underneath the table: **Ox executes; it does not decide.** Anything
whose output is a judgement, a disposition, or a checkbox in a readiness audit
stays with a human or an orchestrating session.

## 2. Two things the harness needs before the first night

**A prompt route.** `prompt_for()` in `scripts/ox_overnight.sh` maps `13.9-*`
to the rebuild prompt and `17A-02|17A-03|17A-05` to the finish prompt.
Everything else falls through to `PROMPT-ox-17A-overnight-2026-08-22.md`,
which tells the executor to read a plan under the 17A phase directory. A quick
plan id, or a new 13.9 plan id, would be handed the wrong prompt and would
read the wrong path. Either add cases, or pass `IB_PROMPT` per run. **Prefer
`IB_PROMPT`**: it is per invocation, it leaves the script alone, and the ox
prompts forbid the executor from touching `scripts/` anyway.

**Plans for the two unplanned items.** The lesser-model executor bar in
`PLANNING-DIRECTIVES.md` section 5 says a Sonnet-class executor must finish a
plan without inventing a decision. Draft autosave and the defect sweep have no
plan files. Writing them is about an hour of orchestrator time and it is the
difference between a night that lands and a night that produces a summary
explaining why it stopped. Suggested ids, both in the 13.9 phase directory
because they are all sitting fallout:

- `13.9-04-PLAN.md`, the five known-open defects, one task each.
- `13.9-05-PLAN.md`, draft autosave on the script-free form path.

## 3. The nights

**Night one, 2026-08-25. The defect sweep.**

```bash
IB_PROMPT=/Users/weiwei/Documents/Dev/itembank/.planning/PROMPT-ox-13.9-finish-2026-08-25.md scripts/ox_queue.sh 13.9-04
```

Five independent defects, each with its own commit. If the run dies at defect
three, defects one and two are already committed and night two starts at
three. This is why the prompt says commit after every task rather than at the
end: three unattended runs have already died at a final commit step with the
work uncommitted.

**Night two, 2026-08-26. Draft autosave, then the 13.5 defects.**

```bash
IB_PROMPT=/Users/weiwei/Documents/Dev/itembank/.planning/PROMPT-ox-13.9-finish-2026-08-25.md scripts/ox_queue.sh 13.9-05
IB_PROMPT=/Users/weiwei/Documents/Dev/itembank/.planning/PROMPT-ox-13.9-finish-2026-08-25.md scripts/ox_queue.sh 260817-q7d
```

Queued, not parallel, because both touch the served quiz path. `ox_queue.sh`
takes several plan ids in one invocation and runs them in sequence, so one
command with both ids is equivalent and is what the script is for.

Note the skip guard: a plan that already has a non-planning commit is skipped
unless `IB_FORCE=1`. `260817-q7d` has only its plan commit, so it will run.
Check with `git log --oneline --grep="(<id>)"` before assuming either way,
because that guard reads commit messages and commit messages have been wrong
in this repository twice.

**Night three, 2026-08-27. Reserve.** Re-run whatever failed. If nothing
failed, `17A-04` is the only thing that fits, and only if item 6 has closed by
then. If it has not, spend the night on nothing rather than on inventing work
for an executor that will be gone the next morning.

## 4. Tree discipline

- **Never two agents in one tree.** `scripts/ox_queue.sh`, always. It polls for
  an in-flight `dsh --profile headless` and waits.
- **This includes interactive sessions.** The 2026-08-24 collision was two
  interactive agents, not two ox runs, and `ox_queue.sh` cannot see those. If
  you are driving a session in this checkout, do not start a night.
- **Worktrees need `IB_ALLOW_WORKTREE=1` and a human committer.** A worktree's
  `.git` is a file pointing outside the agent's writable root, so the agent
  does the work and commits nothing. 17A-05 was lost that way for a whole run.
  The guard now refuses early. If you use the override, you are promising to
  review and commit the result yourself.
- **Parallel worktrees only when `files_modified` sets do not intersect.** Of
  the work above, `13.9-04` and `13.9-05` both touch `surfaces/quiz_page.py`
  and `surfaces/daemon.py`, so they must never overlap.

## 5. Accepting a night's work

The two cautions from 2026-08-24 are the whole of this section.

**Check an artifact the plan names, not a commit message.** A count of
`git log --grep` read a planned phase as an executed one twice in one session.
For each task, open the file or run the command the plan's verify block names.

**Drive the real page when the change is user facing.** A suite of seventy
green tests agreed with a broken served page all night. Both `13.9-04` and
`13.9-05` are served-page changes. Start the daemon, sit an item, and look.

Then, in order: run the full suite with `ANKI_CONNECT_URL=http://127.0.0.1:59999`
or with Anki quit, run `python3 itembank.py guard .`, read
`.planning/_ox-logs/<stamp>-<plan>.log` for what the executor said it could
not do, and only then roll the result into `.planning/STATE.md` yourself. The
executor is forbidden from touching STATE, so it is always your entry to
write.

**When a test fails after a fix, decide which of the two is wrong before
editing either.** `agent_roundtrip` once asserted `pending_manual >= 1` after a
mark, which encoded the exact bug it was later used to catch.

## 6. After Ox is gone

Ordered, and none of it is unattended work.

1. **Item 5** finishes in the session that started it, with a test that fails
   before the change.
2. **Item 6**: write `13.9-CALIBRATION.md` from the real sitting, pointers,
   counts and hashes only, never item text, both denominators stated. Then the
   four open A9 boxes in `READINESS-AUDIT-14A.md`, then the STATE roll-up.
   This is the gate: `13.9-03` is what unblocks everything below it.
3. **17A-04**, the last unbuilt 17A plan.
4. **Phase 13.5's human-verify gates**, which are what keep that box unchecked
   and are unaffected by any of the above.
5. **14B planning**, whose plans must cite `13.9-CALIBRATION.md`, with no 14B
   freeze commit before `13.9-03` closes.
6. Then 15A, 15B, 16A, 16B, 16C, 17B, 17C, 18.

One durable note for whoever holds the next model budget. Every item on this
runbook that Ox can execute is one that a human already reduced to a plan. The
scarce resource was never the executor. It was the hour spent writing the plan
that made the executor safe to leave alone overnight.
