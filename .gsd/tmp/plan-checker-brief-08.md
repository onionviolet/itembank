# Plan Checker Brief - Phase 08

## PHASE 08 ONLY — DO NOT VERIFY PHASE 10

The plans to verify are the SIX files named `08-01-PLAN.md` … `08-06-PLAN.md` under `C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/08-model-adapter-interface-tier-gate-enforcement/`. Ignore every `10-*` file, every HANDOFF file, and all other phases. The phase directory path above is the ONLY directory you may read for plans.

You are the gsd-plan-checker agent. Verify the Phase 08 plan set and return a verdict. Do NOT touch any file outside the phase directory, do NOT read .planning/HANDOFF*.md, and do NOT modify or commit anything.

<verification_context>
**Phase:** 08
**Phase Goal:** The tutoring model reads the key and the learner's specific wrong answer and writes a hint about that error, but the runtime - not the model - decides which tier it may speak at, and a hint that reaches past that tier never renders.
**Mode:** standard

<files_to_read>
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/08-model-adapter-interface-tier-gate-enforcement/*-PLAN.md (Plans to verify)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/ROADMAP.md (Roadmap - Phase 8 section, 14 success criteria)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/REQUIREMENTS.md (Requirements)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md (USER DECISIONS - D-01..D-27)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-RESEARCH.md (Technical Research)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-UI-SPEC.md (UI contract)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-AI-SPEC.md (AI contract)
</files_to_read>

**Phase requirement IDs (MUST ALL be covered across the plan set):** TEACH-04, TEACH-05, TEACH-06, TEACH-07, TEACH-08, TEACH-09, MODEL-01, MODEL-02, MODEL-03, MODEL-04, MODEL-05

**Project instructions:** Read ./AGENTS.md or ./.claude/CLAUDE.md if either exists - verify plans honor project guidelines.
</verification_context>

## Checks

1. Every requirement ID above appears in at least one plan's `requirements` field.
2. Every CONTEXT.md decision D-01..D-27 is represented in at least one plan's must_haves/truths or task text (decision-coverage gate).
3. ROADMAP Phase 8 success criteria 1-14 (including round-two rulings: hosted-first, tier-3 constant-zero, suggestion_reveal, mark_proposal, no auto-accept, structural lock, no invented figures) are addressed by the plan set.
4. Plans honor the UI-SPEC and AI-SPEC gates (learner-facing surfaces UI-BLOCKED on adversarial gate evidence; 30-case reference set).
5. Every task has concrete action/acceptance/verify content; waves and dependencies are coherent; threat models are present in each plan.

## Expected output

- If all checks pass: final message must start with `## VERIFICATION PASSED` and a short summary.
- If issues are found: final message must start with `## ISSUES FOUND` followed by a YAML issues block (dimension, severity BLOCKER|WARNING|INFO, finding, affected_field, suggested_fix).

Working directory: C:/Users/wayba/Downloads/CTF/itembank
