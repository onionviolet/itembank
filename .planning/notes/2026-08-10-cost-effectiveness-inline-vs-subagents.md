# Cost-Effectiveness: Inline Execution vs Subagent Dispatch

- **Date:** 2026-08-10
- **Status:** EXPERIMENT SETUP — run the probe prompt below in a fresh chat.
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

## 6. Repo state to start from

- `main`, milestone v1.0, 19 phases; phase 03.1 at plan 4/7 (3/7 summaries).
- Phase 03.1 plans 01–03 complete and committed; next plan: 03.1-04.
- All 20 test suites green; worktrees disabled; commit directly on main.
- See `.planning/phases/03.1-lesson-rich-blocks-glossary-style/.continue-here.md`
  for the full handoff.
