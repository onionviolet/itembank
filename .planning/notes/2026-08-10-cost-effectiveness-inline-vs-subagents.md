# Cost-Effectiveness: Inline Execution vs Subagent Dispatch

- **Date:** 2026-08-10
- **Status:** EXPERIMENT SETUP (updated 2026-08-10) — typed dispatch restored
  via pin fix; re-run the probe in a fresh chat.
- **Owner:** next round (the user explicitly wants to measure this).

---

## 1. The question

For this repo's GSD autonomous runs in this Codex desktop runtime, which is
more cost-effective: executing plans inline in the orchestrator, or
dispatching subagents (executors/planners/test-writers)? "Cost" should mean
both token spend and wall-clock time, and "effective" should mean work
actually landed on disk (commits + SUMMARY.md), not turns spent.

## 2. Evidence so far (why this is a real question)

### Inline execution — measured

| Plan | estimate | actual (chars/4) | tasks | commits | suites green |
|------|----------|------------------|-------|---------|--------------|
| 03.1-02 (TERMS/glossary/term_lookup) | 32000 | 20487 | 3 | 6+1 | 19/19 |
| 03.1-03 ([!KEY]/Anki/review/objective) | 32000 | 18796 | 3 | 6+1 | 20/20 |

Inline is reliable: every plan closed with all suites green, every task
committed atomically, deviations documented. It is context-heavy in the
orchestrator, but the GSD state on disk makes compaction/resume safe.

### Subagent dispatch — observed failures

Verified on 2026-08-10 (same session family, four attempts total):

1. Typed `gsd-executor`/`gsd-planner` spawns: **refused at launch** by the
   model router (roles pin `deepseek-v4-flash` at `xhigh`; router accepts
   only `low|high|max`). Recorded in
   `2026-08-10-codex-runtime-typed-gsd-agents.md`.
2. Generic spawn (this session): agent completed instantly with
   `"I'm ready — awaiting the task details."` — **no task payload arrived**,
   no file created on disk.
3. Follow-up resend to the same agent: completed with
   `"Ready to begin when you are."` — **still no payload**, still no file.
4. Earlier session: the same idle pattern for planner sub-subagents and
   follow-ups (see the typed-agents note, section 6).

**Conclusion so far:** in this runtime, subagent payload delivery is
broken at the harness level (spawn AND follow-up). Cost-effectiveness of
subagents is currently **unmeasurable** because they produce no work. The
experiment below is therefore a *re-probe with a measurement protocol*, not
a comparison we can already run.

## 3. What to measure (protocol for a controlled run)

For each execution mode (A = inline, B = subagent), record per plan:

1. **Token cost** — use the GSD `actuals.tokens` convention (chars/4 over
   the realized diff) AND the model's own usage report if the harness
   exposes it. Record both; never mix scales.
2. **Wall-clock** — start/end timestamps for the plan (SUMMARY `duration`).
3. **Work landed** — SUMMARY.md exists? commits exist? how many? all suites
   green?
4. **Failure rate** — spawns that idled / returned no payload / produced no
   disk change. Count separately from legitimate checkpoint pauses.
5. **Orchestrator context consumed** — approximate: commentary/tool-call
   count in the orchestrator per plan.
6. **Resume safety** — after compaction or a fresh chat, how much state was
   recoverable from disk alone?

**Verdict rule:** mode B beats A only if it lands the same work with lower
token cost AND lower wall-clock AND zero payload-loss turns. If B's payload
loss rate is > 0 in a run, B is not yet viable regardless of its per-success
cost.

## 4. Suggested probe prompt (paste into a fresh Codex chat)

> Run a cost-effectiveness probe comparing inline execution vs subagent
> dispatch in this runtime, for the GSD project at
> C:/Users/wayba/Downloads/CTF/itembank.
>
> 1. Read `.planning/notes/2026-08-10-cost-effectiveness-inline-vs-subagents.md`
>    and `.planning/notes/2026-08-10-codex-runtime-typed-gsd-agents.md`.
> 2. First verify subagent payload delivery with ONE bounded, verifiable
>    probe: spawn a generic subagent (no agent_type) with a task that must
>    create a specific file with specific content under
>    `.planning/probes/` (e.g. write `probe-<timestamp>.txt` containing
>    "payload-ok"). Wait for it, then check the file on disk.
>    - If the file exists with the exact content: report delivery works and
>      proceed to dispatch one real executor-style task (e.g. plan
>      03.1-04's Task 1 test file) as a subagent, measuring the five metrics
>      in section 3, verifying on disk, and comparing against the inline
>      actuals table (20487 / 18796 tokens, ~190 min, all green).
>    - If the file does not exist (agent replies "ready"/"awaiting
>      details"): record the attempt as a payload-loss turn, try ONE
>      follow-up resend, and if that also fails, conclude "subagents not
>      viable in this runtime — inline is the only measurable mode" and
>      stop the probe without burning more turns.
> 3. Append the results to this note under a new "## 5. Probe results"
>    section with the six metrics filled in.
> 4. Do not modify any repo files other than the probe file and this note.

## 5. If the probe shows delivery works

Parallelization opportunities to test next (in dependency order):

- Phase 03.1 plans 04 and 06 touch disjoint file sets (04: model.py +
  lesson.py + new style files; 06: surfaces/presentation.py + fonts) — but
  both touch surfaces/lesson.py, so scope carefully or run sequentially.
- Phase 7 (Selection Engine) depends only on Phase 1 (complete) — its 6
  plans are independently executable *after* 3.1 finishes, in parallel with
  nothing else blocking it. This is the cleanest true-parallel candidate.
- Phases 3.2 and 5/6 chain sequentially; only intra-phase plan-level
  parallelism applies.

## 5. Probe results (2026-08-10, resumed session)

Probe ran as the first dispatch of the resumed `$gsd-execute-phase 3.1`
run, following the protocol in section 4. Brief file on disk:
`.planning/probes/PROBE-BRIEF.md`; expected artifact
`.planning/probes/probe-20260810T2145Z.txt` containing `payload-ok`.

| Metric | Value |
|--------|-------|
| Token cost | 2 idle subagent turns (1 spawn + 1 resend); not measurable as work |
| Wall-clock | ~4-6 min total (spawn + wait + resend + wait) |
| Work landed | None — file never created |
| Failure rate | 2/2 payload-loss turns (spawn AND follow-up) |
| Orchestrator context | Low: 1 brief file + 2 spawns + 2 disk checks |
| Resume safety | n/a — no work produced |

**Verdict:** subagents are still NOT viable in this runtime. Payload loss
reproduces exactly as in section 2 (spawn AND follow-up both idle with no
disk change). Per the verdict rule, inline is the only measurable mode for
this run: plans 03.1-04 through 03.1-07 will execute inline in the
orchestrator, with this deviation documented in the phase summary.

## 6. Repo state to start from

- `main`, milestone v1.0, 19 phases; phase 03.1 at plan 4/7 (3/7 summaries).
- Phase 03.1 plans 01–03 complete and committed; next plan: 03.1-04.
- All 20 test suites green; worktrees disabled; commit directly on main.
- See `.planning/phases/03.1-lesson-rich-blocks-glossary-style/.continue-here.md`
  for the full handoff.

## 7. Update (2026-08-10, later same day): typed dispatch restored

The typed-spawn blocker changed after this note was written: the GSD role pins
were fixed from `xhigh` to `max` (`C:/Users/wayba/.codex/agents/*.toml`), so
typed `gsd-executor`/`gsd-planner` spawns should launch in this runtime now.
The payload-loss failure mode (items 2-4 in section 2) is independent of the
pin fix and is still the gating factor: re-run the probe prompt and treat
payload delivery as the pass/fail gate before comparing inline vs subagent
costs. If delivery passes, the comparison can now include typed dispatch
alongside generic spawns.

## 8. Probe results (post-pin-fix)

Re-ran the payload-delivery probe on 2026-08-10 (post-pin-fix) with six
controlled generic spawns, all verified on disk:

| # | Config | Result |
|---|--------|--------|
| 1 | fork_turns="none", pointer message (backslash path) | payload dropped; no file |
| 2 | fork_turns="none", pointer message (relative path) | agent replied "no message payload arrived with this turn"; no file |
| 3 | fork_turns="all", pointer to brief | context delivered; agent engaged and wrote its own probe briefs; no target file; hung until interrupted |
| 4 | fork_turns="2", pointer to brief | context delivered; spawned a sub-subagent; interrupted |
| 5 | fork_turns="2", guard-heavy brief | ran 8+ min; no file |
| 6 | fork_turns="1", task inline in fork window | ran 4+ min; no file |

**Verdict:** message-payload delivery to subagents is still broken at the
harness level. Fork-context delivery works (subagents receive and act on
inherited context), but fork agents drift to the broadest visible task and
none completed the exact artifact within bounded waits. Subagents are NOT yet
reliably usable for exact-task dispatch; the reproducible pattern is
fork + brief-on-disk + disk verification + inline fallback, documented in
`2026-08-10-subagent-dispatch-recipe.md`. Inline remains the only measurable
mode for the cost comparison.

Typed probe (same day): `agent_type="gsd-executor"` launched post-pin-fix (no
router refusal) but never completed a turn and produced no file - the typed
path adds a bootstrap hang on top of the payload issue. Verdict stands: inline
is the only measurable mode until a fork-based executor lands a real artifact.

**Reasonix harness (same day, parallel probe): PASS — this harness is viable
for wave-parallel execution.** Three subagents dispatched in parallel via
`fleet` landed byte-exact artifacts on the first dispatch (with real time
overlap, no drift, no spawns, no changes outside `.planning/`); full results
in `2026-08-10-reasonix-dispatch-probe.md`. Recommend running GSD wave-
parallel execution here, not on the Codex harness.

## 8.5 Unlock-executors probe (2026-08-10, fork + brief + disk verification)

Ran the two-stage fork-dispatch probe from the subagent-dispatch recipe.

**Stage A (generic agent, `fork_turns="all"`):** first spawn engaged but
produced nothing in a 5-min bounded wait; interrupted and re-dispatched once
via `followup_task`. The byte-exact artifact
`.planning/probes/unlock-ok.txt` (content `unlock-ok`, 9 bytes, no trailing
newline) then LANDED within ~1 min and was verified byte-for-byte on disk.
This is the first positive exact-artifact delivery from a subagent in this
runtime - but only after a re-dispatch; the initial fork wait was silent.

**Stage B (typed `gsd-executor`, `fork_turns="2"`):** the harness rejects
`agent_type` combined with `fork_turns="all"` ("Full-history forked agents
inherit the parent agent type"), so the documented lean fork was used. The
executor drifted: it spawned a recursive subagent chain
(`unlock_b` -> `unlock_a` -> `unlock_a`) in direct violation of the brief's
no-spawn guard, never wrote the expected test file
(`tests/style_roundtrip.py` - untouched, hash unchanged, plan verify still
`ALL TESTS PASSED`), and the drifted chain DELETED the Stage A artifact
`unlock-ok.txt` and rewrote `UNLOCK-BRIEF.md` (914 -> 180 bytes). The Stage A
artifact and brief were restored after the run; no tracked repo files outside
`.planning/` were modified.

**New failure mode:** fork drift is not just a hang - it can mutate or destroy
probe artifacts while recursing. Combined with Stage A's re-dispatch
dependency, fork + brief + disk verification does not yet reliably land exact
artifacts.

**Verdict:** executors stay LOCKED. Inline remains the only production mode.
Experiments stopped per the probe protocol.
