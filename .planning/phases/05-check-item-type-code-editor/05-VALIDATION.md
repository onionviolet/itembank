---
phase: 5
slug: check-item-type-code-editor
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-08
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — direct script execution, stdlib only |
| **Config file** | none |
| **Quick run command** | `python tests/check_roundtrip.py` |
| **Full suite command** | `for f in tests/*_roundtrip.py; do python "$f" || exit 1; done` |
| **Estimated runtime** | ~20 seconds quick (the timeout cases spend real wall-clock), ~80 seconds full |

---

## Sampling Rate

- **After every task commit:** Run `python tests/check_roundtrip.py`
- **After every plan wave:** Run the full suite
- **Before `/gsd-verify-work`:** Full suite must be green **on Windows as well as CI Linux** — see
  the manual table below; CI runs `ubuntu-latest` only
- **Max feedback latency:** 80 seconds

---

## Per-Task Verification Map

*Filled by the planner. One row per task, mapped to a CODE-xx requirement.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| | | | | | | | | | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/check_roundtrip.py` — new file, stubs for CODE-01..CODE-05
- [ ] `fixtures/check_bank.md` — new synthetic fixture: a multi-case passing item, a mixed
      pass/fail item, an item whose code times out, an item whose code spawns a **grandchild**
      that outlives its parent, an item that floods stdout past the cap, and an item with a
      `[LANG:]` value not in the allowlist
- [ ] `fixtures/grandchild_spawner.py` — the grandchild fixture, written so it cannot leak a
      process when the test itself fails (the test must reap deterministically on both platforms)

No framework install — the project forbids one.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The Windows process-tree kill actually kills a grandchild | CODE-04 | **CI is `ubuntu-latest` only.** The Job Object path cannot be exercised by CI at all; it can only be run on the target Windows 11 machine, matching the `01-01-PLAN.md` spike precedent | On Windows: run `python tests/check_roundtrip.py`, then confirm with `tasklist` that no orphaned `python.exe` from the grandchild fixture survives the timeout |
| The `CREATE_SUSPENDED` race window | CODE-04 | CPython's Windows `_execute_child` closes the child's thread handle before returning (`bpo-1677688`), so a race-free assign-then-resume is not reachable through `subprocess.Popen`. Whether the residual window ever loses a grandchild in practice is empirical | Run the grandchild fixture repeatedly (50 iterations) on Windows and confirm zero escapes; record the observed rate rather than claiming zero |
| Gutter-to-line pixel alignment at 500 lines | CODE-03 | Sub-pixel font-metric drift is a visual judgment | Paste 500 lines into the editor, scroll to the bottom, confirm line 500 in the gutter sits on line 500 of the textarea |
| The editor's tab and shift-tab behavior preserves usable undo | CODE-03 | Undo-stack behavior differs per browser and is not scriptable here | Type, Tab, Shift-Tab, then Ctrl-Z repeatedly and confirm the document walks back sensibly |
| No documentation anywhere claims sandboxing | CODE-05 | Partly automatable (the grep), but judging whether some *other* sentence overclaims safety is a reading task | Run the grep for `sandbox` / `isolat` / `contain`, then read the `check` sections of `SPEC`, README, and the UI copy for any implied safety claim |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 80s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
