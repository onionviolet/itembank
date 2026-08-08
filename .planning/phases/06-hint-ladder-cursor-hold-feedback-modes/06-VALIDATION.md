---
phase: 6
slug: hint-ladder-cursor-hold-feedback-modes
# status lifecycle: draft (seeded by plan-phase) -> validated (set by validate-phase)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-08
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for the two coarse Phase 6 plans.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — direct standard-library roundtrip scripts |
| **Config file** | none |
| **Quick run command** | `python tests/hint_roundtrip.py` |
| **Targeted integration command** | `python tests/hint_roundtrip.py && python tests/evidence_roundtrip.py && python tests/protocol_roundtrip.py && python tests/daemon_roundtrip.py && python tests/serve_roundtrip.py && python tests/scoring_roundtrip.py` |
| **Full suite command** | `for f in tests/*_roundtrip.py; do python "$f" || exit 1; done` |
| **Estimated runtime** | ~10 seconds quick, ~55 seconds targeted, ~80 seconds full |

The project test shape is `tests/<concept>_roundtrip.py`, direct execution, a
`fail(msg)` helper, and nonzero exit on failure. No package or test framework is added.

---

## Sampling Rate

- **Before Phase 6 implementation:** run the Phase 3 preflight in 06-01-T1; stop if it fails.
- **After every implementation task:** run `python tests/hint_roundtrip.py` plus the task's named regression scripts.
- **After each plan wave:** run the targeted integration command.
- **Before `/gsd-verify-work`:** run the full suite.
- **Max automated feedback latency:** 80 seconds at the phase gate; task-local feedback remains under 60 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement / Decision | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|------------------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01-T1 | 06-01 | 1 | Phase 3 dependency, D-15, D-16 | T-06-01, T-06-04 | Fail closed unless the Phase 3 lesson test and public lesson_slug contract pass; human confirms v2 fields/linkage/read compatibility before append-only writes | blocking decision + executable preflight | `python tests/lesson_roundtrip.py && python -c "import model,runtime;qs=model.load('fixtures/lesson_bank.md');q=next(q for q in qs if q.get('lesson_slug'));assert runtime.public_item(q)['lesson_slug']==q['lesson_slug']"` | ✅ Phase 3 artifact | ⬜ pending |
| 06-01-T2 | 06-01 | 1 | TEACH-01, TEACH-02, MODE-01..05, D-01..D-14 | T-06-01, T-06-02, T-06-03, T-06-05 | Runtime alone canonicalizes/scores, gates tiers, chooses disclosure, holds/advances cursor, and keeps feedback mode separate from selection_mode; it accepts no renderer observation | unit + tracer | `python tests/hint_roundtrip.py` | created by this task | ⬜ pending |
| 06-01-T3 | 06-01 | 1 | TEACH-03, MODE-06, D-15..D-17 | T-06-02, T-06-04, T-06-05 | Response/hint events use the confirmed closed v2 contract, retain v1 read compatibility, preserve null vs 0, and derive outcomes from live events after retractions | contract + integration | `python tests/hint_roundtrip.py && python tests/evidence_roundtrip.py && python tests/protocol_roundtrip.py` | ✅ except new hint test sections | ⬜ pending |
| 06-02-T1 | 06-02 | 2 | TEACH-01..03, MODE-01..06 | T-06-15 | CLI submit/hint/report share one session adapter, append through the one writer, and reconcile crash-window replays before state changes | CLI integration tracer | `python tests/hint_roundtrip.py` | ✅ after 06-01-T2 | ⬜ pending |
| 06-02-T2 | 06-02 | 2 | TEACH-02, MODE-01..06, renderer handoff | T-06-12, T-06-13, T-06-14 | API resolves opaque session IDs, accepts only Phase 6 action shapes plus an optional 256-byte opaque renderer_meta string, rejects observation/canvas objects, and proves metadata is never persisted, returned, logged, or passed to policy | HTTP integration | `python tests/hint_roundtrip.py && python tests/daemon_roundtrip.py` | ✅ after 06-01-T2 | ⬜ pending |
| 06-02-T3 | 06-02 | 2 | TEACH-01..03, MODE-02..05 | T-06-11, T-06-15 | Served browser renders runtime actions and escaped authorized payloads only; no local scorer, tier increment, mode policy, or cursor authority exists | browser-contract + E2E | `python tests/hint_roundtrip.py && python tests/daemon_roundtrip.py && python tests/serve_roundtrip.py && python tests/scoring_roundtrip.py` | ✅ after 06-01-T2 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Sampling continuity:** the only non-implementation task is the blocking 06-01-T1
decision, and it has an executable Phase 3 preflight. Every implementation task has an
automated command; no two implementation tasks occur without feedback.

**Requirement coverage:** TEACH-01 (06-01-T2, 06-02-T1/T3), TEACH-02 (06-01-T2,
06-02-T1/T2/T3), TEACH-03 (06-01-T3, 06-02-T1/T3), MODE-01..05 (06-01-T2,
06-02-T1/T2/T3), MODE-06 (06-01-T3, 06-02-T1/T2).

---

## Wave 0 Requirements

- [ ] `tests/hint_roundtrip.py` — created by 06-01-T2 before runtime implementation.
      It begins with pure transition checks for all modes, all six fixed tiers,
      unavailable slots, response-specific tier 3, duplicate/empty/stumped behavior,
      manual pending, session upgrade, and mode immutability. 06-01-T3 adds real-log,
      schema, retraction, mark, and derived-outcome checks; 06-02 adds CLI/API/browser
      checks to this same file.
- [x] `tests/lesson_roundtrip.py` and `fixtures/lesson_bank.md` — Phase 3-owned
      prerequisites. They are not recreated by Phase 6. 06-01-T1 executes both the
      Phase 3 roundtrip and a direct `lesson_slug`/`public_item` assertion before the
      evidence decision can resume.
- [x] Existing regression scripts — `evidence_roundtrip.py`, `protocol_roundtrip.py`,
      `daemon_roundtrip.py`, `serve_roundtrip.py`, and `scoring_roundtrip.py` are
      extended or rerun; no parallel framework is introduced.

No concrete visual/canvas fixture, action schema, observation schema, or renderer is a
Wave 0 requirement. Those belong to Phase 06.1. Phase 6's only renderer handoff is the
optional opaque `renderer_meta` string, which is deliberately non-persisted and has no
policy semantics.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The progressive ladder and “I'm stumped — show the next hint” control read as legitimate teaching actions rather than an error state | TEACH-02, MODE-03 | Tone and interaction clarity are human judgments; structural behavior is automated | Start a served practice sitting, answer incorrectly, request the next hint, then use stumped; verify the card remains active, exactly one new tier appears each time, unavailable content is stated honestly, and no styling outside the existing surface is introduced |
| Diagnostic completion review and marked-exam review communicate why feedback was withheld | MODE-04, MODE-05 | Copy clarity cannot be proven by payload assertions | Complete one diagnostic sitting and mark one exam attempt; verify no pre-release content appeared and the released review states the gate that opened it |

These checks are end-of-phase human checks; no Phase 4 redesign or Phase 06.1 visual
assessment implementation is authorized by them.

---

## Validation Sign-Off

- [ ] Phase 3 executable preflight passes before any Phase 6 implementation
- [ ] D-15/D-16 evidence contract checkpoint is explicitly approved before 06-01-T3
- [ ] All implementation tasks have an automated verify
- [ ] Sampling continuity has no three consecutive tasks without automated feedback
- [ ] Wave 0 owns every missing test artifact
- [ ] No watch-mode flags
- [ ] Renderer metadata is opaque, bounded, non-persisted, and absent from policy/evidence/results/logs
- [ ] No visual/canvas action or observation semantics/schema exists outside Phase 06.1
- [ ] No Phase 4 file is modified
- [ ] `nyquist_compliant: true` set in frontmatter after validation execution

**Approval:** pending
