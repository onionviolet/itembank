# Planner Brief - Phase 08: Model Adapter Interface & Tier-Gate Enforcement

You are the gsd-planner agent. Execute your planner role end-to-end for Phase 08 and write executable PLAN.md files to disk. This phase was already planned once (6 plans, 2026-08-08) but the CONTEXT.md was just updated with round-two research; **replan from scratch**, replacing the stale plan set. You may keep a wave structure that still fits, but every plan must reflect the updated CONTEXT.md and ROADMAP criteria below.

<planning_context>
**Phase:** 08
**Mode:** standard

<files_to_read>
- C:/Users/wayba/Downloads/CTF/itembank/.planning/STATE.md (Project State)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/ROADMAP.md (Roadmap - Phase 8 section carries 14 success criteria and round-two rulings)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/REQUIREMENTS.md (Requirements - TEACH-04..09, MODEL-01..05)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md (USER DECISIONS from discuss-phase - D-01..D-27, mandatory)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-RESEARCH.md (Technical Research - bounded hint-plan gate design, validation architecture)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-PATTERNS.md (Pattern Map - analog files and code excerpts)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-UI-SPEC.md (UI Design Contract - learner-facing surfaces are UI-BLOCKED on its gates; copy tables are binding)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-AI-SPEC.md (AI Design Contract - framework decision, 30-case reference dataset, evaluation dimensions, guardrails)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-VALIDATION.md (Validation strategy)
</files_to_read>

**Phase requirement IDs (every ID MUST appear in at least one plan's `requirements` field):** TEACH-04, TEACH-05, TEACH-06, TEACH-07, TEACH-08, TEACH-09, MODEL-01, MODEL-02, MODEL-03, MODEL-04, MODEL-05

**Project instructions:** Read ./AGENTS.md or ./.claude/CLAUDE.md if either exists — follow project-specific guidelines.
**Project skills:** Check .claude/skills/ or .agents/skills/ directory (if either exists) — read SKILL.md files and account for project skill rules.

<security_contribution>
Each PLAN.md must include a `<threat_model>` block when security enforcement is active.
- ASVS enforcement level: 1
- Blocking threshold: high-severity threats
</security_contribution>

<api_coverage_contribution>
# API Coverage Decision Checkpoint

Full API Coverage by Default — Opt Out, Never Opt In. This phase integrates an external model API/service. Detect whether the phase integrates an external API by running the deterministic scan over the phase scope (ROADMAP Phase 8 section + plan body):

```bash
SCOPE="$(cat "${PHASE_DIR}"/*-PLAN.md 2>/dev/null) $(gsd_run query roadmap.get-phase "08" 2>/dev/null || true)"
API_COVERAGE_JSON=$(printf '%s' "$SCOPE" | node gsd-core/bin/lib/api-coverage.cjs --json 2>/dev/null || echo '{"detected":false,"signals":[]}')
```

Read `API_COVERAGE_JSON.detected`. If `true`, produce an API coverage matrix at `${PHASE_DIR}/COVERAGE.md` enumerating the external API capability surface (e.g., chat/completion invoke, hint plan generation, rubric review) with INTEGRATE/OPT-OUT decisions and one-line reasons for every OPT-OUT. INTEGRATE is the default. If `false`, write a reasoned `No external API integration: ...` declaration instead. The seal-time gate validates this file.
</api_coverage_contribution>

<assumption_delta_contribution>
# Assumption-Delta Architecture Checkpoint

Advisory, non-blocking. Run the detector:

```bash
ASSUMPTION_DELTA_JSON=$(gsd_run query assumption-delta scan "08" --json 2>/dev/null || echo '{"detected":false,"signals":[],"terms":{}}')
```

If `detected` is true, record the outcome in PLAN.md front matter / an `<assumption_delta_decision>` block: the noun that is now primary, the decision (`promote` | `add-alongside` | `no-change`) with a one-line rationale, and if `add-alongside`, call it out as accepted debt with what would force a later promote. Phase 8 adds a second backend path and a third review pathway, so a pluralization signal is likely.
</assumption_delta_contribution>

**TRACER_MODE:** true (lead with one production-quality end-to-end tracer slice that is verified before expansion tasks)
**REVERSIBILITY_GATES:** true (a decision rated `one-way` earns a `checkpoint:decision` before the task implementing it; see gsd-core/references/planner-reversibility.md)
**MVP_MODE:** true (ROADMAP Phase 8 declares Mode: mvp — read `C:/Users/wayba/.codex/gsd-core/references/planner-mvp-mode.md` and follow its vertical-slice planning rules; each plan delivers a complete vertical slice)
**WALKING_SKELETON:** false
**Granularity:** standard

<specless_probe_fallback>
No SPEC.md exists for this phase, so the spec-less probe fallback ran. Edge coverage report (author predicates into `must_haves` per the downstream_consumer else-branch; unresolved probes become explicit assumptions, never silently dropped):

```json
{"items":[{"requirement_id":"TEACH-04","category":"adjacency","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"When two things are exactly equal or just touch, do they merge, collide, or separate?"},{"requirement_id":"TEACH-04","category":"empty","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"What is the result for empty, single-element, or null input?"},{"requirement_id":"TEACH-04","category":"ordering","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"When elements compare equal, is output order specified and stable?"},{"requirement_id":"TEACH-05","category":"unclassified","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"unclassified - review manually"},{"requirement_id":"TEACH-06","category":"unclassified","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"unclassified - review manually"},{"requirement_id":"TEACH-07","category":"adjacency","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"When two things are exactly equal or just touch, do they merge, collide, or separate?"},{"requirement_id":"TEACH-07","category":"empty","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"What is the result for empty, single-element, or null input?"},{"requirement_id":"TEACH-07","category":"ordering","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"When elements compare equal, is output order specified and stable?"},{"requirement_id":"TEACH-07","category":"idempotency","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"What happens if this runs twice on the same input?"},{"requirement_id":"TEACH-07","category":"concurrency","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"If interrupted or run in parallel, what is guaranteed?"},{"requirement_id":"TEACH-08","category":"unclassified","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"unclassified - review manually"},{"requirement_id":"TEACH-09","category":"unclassified","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"unclassified - review manually"},{"requirement_id":"MODEL-01","category":"unclassified","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"unclassified - review manually"},{"requirement_id":"MODEL-02","category":"boundary","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"What happens exactly at each min/max/threshold - and one step either side?"},{"requirement_id":"MODEL-02","category":"precision","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"Where can precision loss, overflow, or rounding/tie-breaking occur - and what is the exact contract (e.g. half-up vs half-to-even, ceil/floor/truncate)?"},{"requirement_id":"MODEL-03","category":"adjacency","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"When two things are exactly equal or just touch, do they merge, collide, or separate?"},{"requirement_id":"MODEL-03","category":"empty","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"What is the result for empty, single-element, or null input?"},{"requirement_id":"MODEL-03","category":"ordering","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"When elements compare equal, is output order specified and stable?"},{"requirement_id":"MODEL-04","category":"idempotency","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"What happens if this runs twice on the same input?"},{"requirement_id":"MODEL-04","category":"concurrency","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"If interrupted or run in parallel, what is guaranteed?"},{"requirement_id":"MODEL-05","category":"unclassified","status":"unresolved","verification":null,"resolution":null,"reason":null,"probe":"unclassified - review manually"}],"coverage":{"applicable":21,"resolved":0,"unresolved":21,"byVerification":{"explicit":0,"backstop":0}}}
```
</specless_probe_fallback>

<downstream_consumer>
Output consumed by execute-phase. Plans need:
- Frontmatter (wave, depends_on, files_modified, autonomous, requirements)
- Tasks in XML format with read_first and acceptance_criteria fields (MANDATORY on every task)
- Verification criteria
- must_haves for goal-backward verification (truths + prohibitions blocks; no silent drops)
- An "Artifacts this phase produces" section (MANDATORY) listing every symbol this phase creates: classes, functions, CLI flags, new file paths, schema fields
</downstream_consumer>

<deep_work_rules>
Every task MUST include:
1. `<read_first>` — the file being modified, any source-of-truth file referenced in CONTEXT.md, and any file whose patterns must be respected.
2. `<acceptance_criteria>` — verifiable source/behavior/test-command/CLI-output assertions with exact strings or commands; never subjective language.
3. `<action>` — concrete identifiers and values (config keys, function signatures, table names, class names, endpoint paths, env vars); never fenced code blocks or full implementations.
</deep_work_rules>

<quality_gate>
- PLAN.md files created in the phase directory
- Valid frontmatter; tasks specific and actionable
- Every task has `<read_first>` and `<acceptance_criteria>`
- Dependencies and waves correct
- must_haves derived from the phase goal (ROADMAP 14 success criteria + CONTEXT D-01..D-27)
- Every PLAN.md has an "Artifacts this phase produces" section
- Every UI-SPEC resolved consideration and probe predicate represented in must_haves (no silent drops)
</quality_gate>
</planning_context>

## Key phase constraints to honor

1. Tier-gate is a first-class deterministic component; prompting is never the gate (D-05..D-09).
2. Tier-3 is NOT a scorer strategy: constant-zero promotability, no auto-accept, no setting that enables it (D-20, D-25). Self-assessment against a revealed model answer is the default tier-3 pathway; deferred human marking and rubric decomposition stay registered alternatives (D-21).
3. Hosted Claude-Code-class backend is built first and default; local OpenAI-compatible is an additional registration; no invented tok/s or latency figures (D-18, D-19).
4. `mark_proposal` event type; `mark_event` human-only guard unchanged (D-23); partial credit = N booleans (D-24).
5. Learner-facing surfaces are UI-BLOCKED until the adversarial gate evidence and Phase 6 fact seam are green; copy tables in 08-UI-SPEC.md are binding (D-26).
6. `suggestion_reveal` ships all three values, default `after-self-mark`; suggestion renders only as a `--pending` token (D-22).
7. Adding a third backend must be a module + config entry, proven by a stub backend in a test (D-27).

## Deliverable

- Write the plan set to `C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/08-model-adapter-interface-tier-gate-enforcement/` as `08-01-PLAN.md`, `08-02-PLAN.md`, ... (pattern `{padded_phase}-{NN}-PLAN.md`).
- Finish your final message with the marker `## PLANNING COMPLETE` (or `## CHECKPOINT REACHED` / `## PLANNING INCONCLUSIVE` if you cannot complete).

Working directory: C:/Users/wayba/Downloads/CTF/itembank
