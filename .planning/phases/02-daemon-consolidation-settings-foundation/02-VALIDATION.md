---
phase: 02
slug: daemon-consolidation-settings-foundation
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-07
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — stdlib-only, subprocess-driven scripts following the `*_roundtrip.py` naming convention [VERIFIED: `.claude/CLAUDE.md` §Naming Patterns] |
| **Config file** | none — CI runs every file under `tests/*.py` unconditionally [VERIFIED: `.github/workflows/ci.yml`] |
| **Quick run command** | `python tests/daemon_roundtrip.py` (new file) / `python tests/config_roundtrip.py` (new file) |
| **Full suite command** | `for t in tests/*.py; do python "$t" || exit 1; done` (matches CI exactly) |
| **Estimated runtime** | Not measured — no existing `*_roundtrip.py` file in this repo takes more than a few seconds; assume single-digit seconds per new file until Wave 0 measures it |

---

## Sampling Rate

- **After every task commit:** Run the specific `*_roundtrip.py` file(s) touched by that task
- **After every plan wave:** Run `for t in tests/*.py; do python "$t" || exit 1; done`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** single-digit seconds (stdlib subprocess tests, no watch mode, no network calls outside loopback)

---

## Phase Requirements → Test Map

*Task IDs are TBD until the planner assigns them — this table records requirement-level coverage from research; the planner should thread task IDs back into this table when PLAN.md files exist.*

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| SURF-01 | Daemon serves `/`, `/quiz/<bank>`, `/study/<bank>`, `/report`, `/api/*`, day view from one port | integration (background-thread daemon + `urllib.request` per route) | `python tests/daemon_roundtrip.py` | ❌ Wave 0 |
| SURF-03 | Second daemon start attaches instead of binding a second port; `--lan` reachable on `0.0.0.0` | integration | `python tests/daemon_roundtrip.py` | ❌ Wave 0 |
| SURF-04 | Every route has a CLI equivalent reaching the same runtime call | integration (compare `/api/submit`'s recorded evidence event against `itembank submit`'s) | `python tests/daemon_roundtrip.py` (extends `tests/agent_roundtrip.py` coverage on the CLI side) | ❌ Wave 0 (new assertions; CLI half already covered) |
| DEL-04 | `itembank.json` holds all six PROJECT.md keys plus daemon settings, each typed/ranged/defaulted | unit | `python tests/config_roundtrip.py` | ❌ Wave 0 |
| DEL-05 | `itembank config` prints schema like `spec`; invalid value rejected with a named (dotted) error | unit | `python tests/config_roundtrip.py` | ❌ Wave 0 |

---

## Wave 0 Requirements

- [ ] `tests/daemon_roundtrip.py` — covers SURF-01/SURF-03/SURF-04; needs a background-thread server-start helper (`threading.Thread(target=srv.serve_forever)`), the pattern `tests/serve_roundtrip.py` and `tests/day_roundtrip.py` already use
- [ ] `tests/config_roundtrip.py` — covers DEL-04/DEL-05
- [ ] No shared fixture gap — `fixtures/sample_bank.md` and `fixtures/sample_plan.md` already exist and are reusable unmodified
- [ ] Framework install: none — stdlib only

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| A phone on the same wifi reaches the daemon via `--lan` | SURF-03 | Requires a second physical device on the same network; a loopback-only automated test cannot exercise cross-device reachability | Start daemon with `--lan`, note the printed LAN URL, load it from a phone browser on the same wifi, confirm the page renders |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
