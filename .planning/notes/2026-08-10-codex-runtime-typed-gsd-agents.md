# Note: Codex runtime cannot launch typed GSD agents as configured

- **Date:** 2026-08-10
- **Context:** `/gsd-plan-phase 3.1 --skip-research` handoff pickup, running in the Codex desktop app.
- **Status:** workaround in effect; typed dispatch blocked by model/effort mismatch.
- **Verification:** live `spawn_agent` attempts with `agent_type="gsd-planner"`, 2026-08-10.

---

## 1. The failure in one line

**Typed GSD agent roles (e.g. `gsd-planner`, `gsd-plan-checker`) are pinned at
install time to `deepseek-v4-flash` at the `xhigh` reasoning tier, but this
runtime's model router only accepts `low | high | max` for that model — so every
typed spawn is rejected before the prompt is transmitted.**

## 2. What was attempted

1. `spawn_agent(agent_type="gsd-planner", ...)` — rejected:
   `Reasoning effort 'xhigh' is not supported for model 'deepseek-v4-flash'.
   Supported reasoning efforts: low, high, max`
2. Same call with explicit `model="deepseek-v4-pro"` and
   `reasoning_effort="max"` — still rejected with the same message; the typed
   role's pinned settings win over caller overrides.

The failure happens at launch, before any content is delivered, so no prompt
text is ever lost — the cost is repeated rejected spawn calls.

## 3. The workaround that works

Spawn a **generic** agent (no pinned role settings; inherits the parent model)
and inject the role instructions manually:

1. `spawn_agent(task_name=..., message=...)` with no `agent_type` (or
   `agent_type="default"`).
2. In the message, instruct the agent to read the role's `.toml` first
   (`C:/Users/wayba/.codex/agents/gsd-planner.toml` or
   `gsd-plan-checker.toml`) and treat its `developer_instructions` as its
   system prompt, then execute the planning/checking task.
3. Label the result as the GSD "generic-agent workaround" — it carries the full
   role contract but is not identical to typed dispatch.

## 4. Why it matters for token spend

Each typed-spawn attempt costs a full tool round-trip and produces zero work.
Future runs in this runtime should **skip typed GSD agent dispatch entirely**
and go straight to the generic-agent + role-injection path. Revisit this note if
the runtime's supported reasoning tiers change (e.g. `xhigh` becomes valid for
`deepseek-v4-flash`).

## 5. Where the fix would live (permanent)

- GSD install pins (`C:/Users/wayba/.codex/agents/*.toml`) set
  `model_reasoning_effort = "xhigh"` for `deepseek-v4-flash`; aligning those to
  `high` (or mapping `xhigh` → `max` on this runtime) would restore typed
  dispatch.
- Or the runtime's model router could accept `xhigh` for `deepseek-v4-flash`.

Neither is changeable from inside a planning session; the generic-agent
workaround is the current path.

## 6. Follow-up (same session): payload delivery to subagents is broken too

The generic-agent workaround planner then spawned its own sub-subagents
(`plan_031`, `planner_031_v2`); both came up idle with generic "ready" replies
and no task payload. The planner correctly detected this and pivoted to doing
the planner work **inline**, documented as a deviation.

Orchestrator follow-up attempts (`collaboration.followup_task`) to the idle
subagents: harness accepted both, agents transitioned idle → running →
completed, **but their replies still showed no message content arrived** —
identical generic "standing by" responses. So message delivery to subagents is
unreliable in this session at two levels: spawn payloads and follow-up payloads.

**Implication for this runtime:** do not depend on subagent payload delivery for
correctness. Prefer inline execution (documenting the deviation) or verify on
disk that the subagent received its task before trusting a turn. This is
recorded 2026-08-10 alongside the typed-spawn issue above.

## 7. Re-verified 2026-08-10 (later same-day session)

Both failure modes were re-confirmed live while running `$gsd-autonomous`:

1. A generic `spawn_agent` (no agent_type) tasked with writing one RED test
   file (`tests/anki_keys_roundtrip.py`) completed instantly with
   `"I'm ready — awaiting the task details."` and produced **no file on
   disk** (checked).
2. One `followup_task` resend of the same prompt completed with
   `"Ready to begin when you are."` and again produced **no file on disk**
   (checked).

The test file was then written inline by the orchestrator in a few minutes.
This is the fourth/fifth observed payload-loss in the session family. The
conclusion stands: **spawn and follow-up payload delivery are both broken
in this runtime; do not spend turns re-probing it.** See
`2026-08-10-cost-effectiveness-inline-vs-subagents.md` for the measurement
protocol and the one allowed re-probe prompt.
