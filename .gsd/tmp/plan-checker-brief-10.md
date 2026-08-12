# Plan Checker Brief - Phase 10

You are the gsd-plan-checker agent. Verify the Phase 10 plan set and return a verdict. Do NOT touch any file outside the phase directory, do NOT read .planning/HANDOFF*.md, and do NOT modify or commit anything.

<verification_context>
**Phase:** 10
**Phase Goal:** The tool tells the learner what's due today, stops a course being binged in one sitting, and raises or lowers what gets selected based on real performance history, with itembank's and Anki's notions of "due" shown as two labeled signals, never silently merged.
**Mode:** standard

<files_to_read>
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/10-retention-pacing-trends/*-PLAN.md (Plans to verify)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/ROADMAP.md (Roadmap - Phase 10 section, 12 success criteria)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/REQUIREMENTS.md (Requirements)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/10-retention-pacing-trends/10-CONTEXT.md (USER DECISIONS - D-01..D-24)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/10-retention-pacing-trends/10-RESEARCH.md (Technical Research)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/10-retention-pacing-trends/10-UI-SPEC.md (UI contract)
- C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/10-retention-pacing-trends/10-VALIDATION.md (Validation strategy)
</files_to_read>

**Phase requirement IDs (MUST ALL be covered across the plan set):** SCHED-01, SCHED-02, SCHED-03, SCHED-04, TREND-01, TREND-02, TREND-03, TREND-04, TREND-05

**Project instructions:** Read ./AGENTS.md or ./.claude/CLAUDE.md if either exists - verify plans honor project guidelines.
</verification_context>

## Checks

1. Every requirement ID above appears in at least one plan's `requirements` field.
2. Every CONTEXT.md decision D-01..D-24 is represented in at least one plan's must_haves/truths or task text (decision-coverage gate).
3. ROADMAP Phase 10 success criteria 1-12 (including round-two rulings: FSRS replay baseline, scheduler interface, WaniKani stages/terminal retired, jpdb utility ordering, return rate as non-streak ratio, lesson-to-item transfer deferred, pending model suggestion never advances interval) are addressed by the plan set.
4. Plans honor the 10-UI-SPEC gates (Today/report surfaces UI-BLOCKED on their verification gates; semantic table canonical; anti-streak copy).
5. Every task has concrete action/acceptance/verify content; waves and dependencies are coherent; threat models are present in each plan.

## Expected output

- If all checks pass: final message must start with `## VERIFICATION PASSED` and a short summary.
- If issues are found: final message must start with `## ISSUES FOUND` followed by a YAML issues block (dimension, severity BLOCKER|WARNING|INFO, finding, affected_field, suggested_fix).

Working directory: C:/Users/wayba/Downloads/CTF/itembank
