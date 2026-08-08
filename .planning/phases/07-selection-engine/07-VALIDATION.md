---
phase: 7
slug: selection-engine
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-08
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — direct script execution, stdlib only |
| **Config file** | none |
| **Quick run command** | `python tests/selection_roundtrip.py` |
| **Full suite command** | `for f in tests/*_roundtrip.py; do python "$f" || exit 1; done` |
| **Estimated runtime** | ~8 seconds quick, ~70 seconds full |

---

## Sampling Rate

- **After every task commit:** Run `python tests/selection_roundtrip.py`
- **After every plan wave:** Run the full suite
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 70 seconds

---

## Per-Task Verification Map

*Filled by the planner 2026-08-08. One row per task, mapped to a SEL-xx requirement.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 07-01-T1 | 07-01 | 1 | SEL-01, SEL-05 (Wave 0) | — | Fixture is synthetic; `itembank guard` still passes because it lives under `fixtures/` | fixture | `python itembank.py lint fixtures/selection_bank.md && python tests/selection_roundtrip.py` | created by this task | ⬜ pending |
| 07-01-T2 | 07-01 | 1 | SEL-01, SEL-05 | T-07-01, T-07-05 | `do_start`'s positive-count guard moves into `select()` verbatim; `select()` opens no file and joins no path | integration | `python tests/scoring_roundtrip.py && python tests/agent_roundtrip.py && python tests/daemon_roundtrip.py && python tests/packaging_roundtrip.py` | ✅ | ⬜ pending |
| 07-01-T3 | 07-01 | 1 | SEL-01, SEL-05, D-10 | T-07-03 | `check_trace_leaks_no_key` builds its forbidden-string list from the parsed bank | unit | `python tests/selection_roundtrip.py` | ✅ | ⬜ pending |
| 07-02-T1 | 07-02 | 2 | SEL-01, SEL-04 | — | Format change is additive; no existing `[HASH:]` moves | unit | `python tests/protocol_roundtrip.py && python tests/scoring_roundtrip.py && python itembank.py lint fixtures/sample_bank.md` | ✅ | ⬜ pending |
| 07-02-T2 | 07-02 | 2 | SEL-01, SEL-04 | T-07-03, T-07-05 | `pair`/`prereq` are never added to `public_item()`; both filter values are exact string compares, never a path | unit | `python itembank.py lint fixtures/selection_bank.md && python tests/selection_roundtrip.py` | ✅ | ⬜ pending |
| 07-02-T3 | 07-02 | 2 | SEL-01, SEL-04 | — | Both new lint codes have a reachable, tested trigger built inline, leaving `fixtures/broken_bank.md` untouched | unit | `python tests/selection_roundtrip.py && python tests/protocol_roundtrip.py` | ✅ | ⬜ pending |
| 07-03-T1 | 07-03 | 2 | SEL-03 | T-07-04, T-07-06 | Every filter bound as a `?` parameter; both query halves stay retraction-aware | unit | `python tests/evidence_roundtrip.py && python tests/protocol_roundtrip.py` | ✅ | ⬜ pending |
| 07-03-T2 | 07-03 | 2 | SEL-03 | T-07-02 | `idx_bank` gives the bank-scoped query a fast path; `/api/*` route scope untouched | integration | `python tests/evidence_roundtrip.py && python tests/daemon_roundtrip.py` | ✅ | ⬜ pending |
| 07-03-T3 | 07-03 | 2 | SEL-03 | T-07-06 | The fixture's retracted response is absent from both the indexed and the fallback path | unit | `python tests/evidence_roundtrip.py` | ✅ | ⬜ pending |
| 07-04-T1 | 07-04 | 3 | SEL-02 | — | One-way door (D-11) gated before anything is written to the append-only log | checkpoint | blocking human decision — no automated command | n/a | ⬜ pending |
| 07-04-T2 | 07-04 | 3 | SEL-02 | T-07-01 | An absent or unrecognised `selection_mode` from `/api/start` coerces to a safe default; `select()` raises a contained `SystemExit` | unit | `python tests/selection_roundtrip.py && python tests/daemon_roundtrip.py && python tests/agent_roundtrip.py` | ✅ | ⬜ pending |
| 07-04-T3 | 07-04 | 3 | SEL-03 | — | One-way door (D-03) gated before anything is written to the append-only log | checkpoint | blocking human decision — no automated command | n/a | ⬜ pending |
| 07-04-T4 | 07-04 | 3 | SEL-03 | T-07-03, T-07-06 | The recorded `selection_spec` key set is a subset of `SPEC_FIELDS` — no item text, no answer key | integration | `python tests/selection_roundtrip.py && python tests/evidence_roundtrip.py && python tests/protocol_roundtrip.py` | ✅ | ⬜ pending |
| 07-05-T1 | 07-05 | 4 | SEL-03 | T-07-01 | `cooldown_responses` bounded 0..500 and `recency_decay` bounded 0..1 in the schema, validated before any read | unit | `python tests/config_roundtrip.py && python schema_validate.py schemas/settings.schema.json itembank.json` | ✅ | ⬜ pending |
| 07-05-T2 | 07-05 | 4 | SEL-02, SEL-03 | T-07-02, T-07-03 | Exactly one bank-scoped history read per request through the indexed fast path; composition reasons name stages, never option text | unit | `python tests/scoring_roundtrip.py && python tests/selection_roundtrip.py && python tests/agent_roundtrip.py` | ✅ | ⬜ pending |
| 07-05-T3 | 07-05 | 4 | SEL-02, SEL-03 | — | Seed literals re-pinned; no assertion's meaning weakened to make a new one pass | integration | `python tests/selection_roundtrip.py && python tests/daemon_roundtrip.py && python tests/evidence_roundtrip.py` | ✅ | ⬜ pending |
| 07-06-T1 | 07-06 | 5 | SEL-01, SEL-05 | — | `schemas/selection.schema.json` stays inside `schema_validate.SUPPORTED`, so a green validation means the whole document was checked | unit | `python tests/protocol_roundtrip.py` | ✅ | ⬜ pending |
| 07-06-T2 | 07-06 | 5 | SEL-01, SEL-04, SEL-05 | T-07-03 | The preview returns `runtime.public_item()` payloads; the rendered trace carries no keyed answer, option text or rationale | integration | `python tests/agent_roundtrip.py && python tests/selection_roundtrip.py && python tests/daemon_roundtrip.py` | ✅ | ⬜ pending |
| 07-06-T3 | 07-06 | 5 | SEL-01, SEL-05 | T-07-01, T-07-03, T-07-05 | Preview writes no session and appends no event; `API_FORBIDDEN_FIELDS` still 400s on the preview branch; profiles validated at use time | integration | `python tests/selection_roundtrip.py && python tests/daemon_roundtrip.py && python tests/config_roundtrip.py` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Sampling continuity:** no three consecutive tasks lack an automated verify — the two
blocking checkpoints in 07-04 are separated by an automated task, and 07-04-T4 follows the
second immediately.

**Requirement coverage:** SEL-01 (07-01, 07-02, 07-06), SEL-02 (07-04, 07-05),
SEL-03 (07-03, 07-04, 07-05), SEL-04 (07-02, 07-06), SEL-05 (07-01, 07-06).

---

## Wave 0 Requirements

*All three are owned by plan 07-01, Task 1 — the tracer plan's first task, so no later
plan discovers them missing mid-implementation.*

- [ ] `tests/selection_roundtrip.py` — new file, stubs for SEL-01..SEL-05
- [ ] `fixtures/selection_bank.md` — **new, and load-bearing.** `fixtures/sample_bank.md` holds
      6 items with unnamespaced objectives and no `[PAIR:]` tags, which is too small to exercise
      a cooldown of 20 or to make four selection modes visibly differ. The new fixture needs
      roughly 30 items across at least 4 namespaced objectives, a spread of difficulties and item
      types, at least two `[PAIR:]` groups, and at least one `[PREREQ:]` chain
- [ ] `fixtures/selection_evidence.jsonl` — a synthetic evidence history so cooldown, remediation
      selection, and the runner-up trace can be tested without sitting a real session

No framework install — the project forbids one.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The trace reads as plain English to a human, not as rule ids | SEL-05 | "In plain terms" is a readability judgment; a test can assert the fields are present but not that the sentence is legible | Run `itembank select fixtures/selection_bank.md --mode practice --explain` and read the output; every block must name the chosen item, the reason, the runner-up, and why the runner-up lost, without jargon |
| The four modes' compositions differ in a way that *matches each mode's purpose* | SEL-02 | A test can assert the four sets differ; whether the difference is the right one is a design judgment | Generate all four from the same fixture and seed, print the objective/difficulty distribution of each, and confirm diagnostic spreads, remediation concentrates on failures, and exam ignores history |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 70s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
