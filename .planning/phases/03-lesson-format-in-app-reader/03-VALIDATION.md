---
phase: 3
slug: lesson-format-in-app-reader
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-08
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — direct script execution. No pytest, no unittest runner, no framework dependency (stdlib-only project constraint). |
| **Config file** | none — no `pyproject.toml`, no `setup.py`, no `requirements.txt` exists or may be added |
| **Quick run command** | `python tests/lesson_roundtrip.py` |
| **Full suite command** | `for f in tests/*_roundtrip.py; do python "$f" || exit 1; done` (CI iterates `tests/*.py` directly) |
| **Estimated runtime** | ~5 seconds quick, ~60 seconds full |

Test convention: a `tests/<name>_roundtrip.py` file, executable directly, printing `FAIL: <msg>`
and exiting 1 on failure. Helper `fail(msg)` per `.planning/codebase/TESTING.md`.

---

## Sampling Rate

- **After every task commit:** Run `python tests/lesson_roundtrip.py`
- **After every plan wave:** Run the full suite
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

*Filled by the planner. One row per task, mapped to a LESSON-xx requirement.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| | | | | | | | | | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/lesson_roundtrip.py` — new file, stubs for LESSON-01..LESSON-06
- [ ] `fixtures/lesson_bank.md` — new synthetic fixture carrying a `## LESSON` section, `###`
      headings, `[LESSON-REF:]` tagged items, one orphan heading, and one fenced code block with
      an info string (the Phase 9 seam)
- [ ] `fixtures/sample_bank.md` — **unchanged**, and used as the LESSON-03 regression: its parse
      result must be byte-identical before and after this phase

No framework install — the project forbids one.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| A full-chapter lesson (~20,000 words) renders and scrolls without a perceptible stall | LESSON-06 | Perceived-performance judgment; no timing threshold is meaningful without a human reading it | Open `/lesson/<bank>` on the largest available fixture, scroll top to bottom, confirm no visible stall |
| `itembank lesson` on a very large `[LESSON-SRC:]` file does not read as a hang | LESSON-06 | Whether silence reads as a hang is a human judgment, not a measurement | Run the CLI against the largest fixture and observe |
| `spec` output is sufficient for an authoring agent with no source access | LESSON-05 | The success criterion is about a model's first-try success, testable only by trying it | Give a model only `itembank spec` output and ask it to author a valid lesson; it must lint clean on the first attempt |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
