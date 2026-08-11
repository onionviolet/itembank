---
phase: 13-desktop-packaging-tauri-sidecar
goal: "A signed, installable desktop app whose inside is still the same Python runtime - one transport, one scorer, honest liveness, shared-channel updates."
requirement_ids: DEL-09, DEL-10, DEL-11, DEL-12, DEL-13
status: passed
verified: 2026-08-10
method: inline verification (subagent dispatch unreliable in this runtime per AGENTS.md)
---

# Phase 13 Verification

## Goal check (ROADMAP Phase 13)

The phase goal -- a desktop app whose inside is still the same Python
runtime -- is met by construction: the sidecar IS the existing daemon entry
frozen by PyInstaller (28.8 MiB onedir), the shell is a thin Tauri client
over one HTTP transport, and the updater reuses the Phase 2.1 release
channel. No runtime logic was ported (D-01); no second scorer exists.

## Must-have truth audit (phase-level)

| Truth | Evidence |
|---|---|
| Sidecar announces port/token/version on stdout; shell reads it (D-03/D-04) | `packaging_shell_roundtrip.py` handshake + token-gate checks |
| Token gate on the routes the shell uses; CLI path unaffected | 401 without / 200 with; daemon 59-check pass (pre-WIP) |
| Job object kills the sidecar on shell death (D-05) | `check_lifecycle_shell` -- taskkill fixture, ~2s teardown |
| Single instance attach-or-refuse (D-06) | mutex unit test + attach/refuse checks |
| Onedir, never onefile; size within 25-45 MiB (D-09) | 28.8 MiB measured; `--onefile` prohibition fixture |
| Installer per-user, evidence store never touched (D-07/T-13-09) | NSIS script + simulated-uninstall fixture (compiled installer pending makensis) |
| Signing stated honestly (D-10/D-11) | unsigned branch recorded in 13-GATES.md with real SHA-256 |
| One release channel, two manifest formats (D-08) | latest.json shape fixture + SHA256SUMS.txt coverage |
| One disclosure, one record, verbatim copy (13-UI-SPEC 7.2) | disclosure fixtures + forbidden-words fixture |
| Version coherence at handshake (T-13-16) | liveness.rs unit test |
| Every capability headless without the shell (D-12) | headless CLI loop fixture |

## Requirement traceability (DEL-09..13)

All five DEL IDs are marked complete in REQUIREMENTS.md, each declared by a
phase plan and backed by a named, existing fixture (13-GATES.md mapping;
`test_requirement_coverage_audit` verifies 5/5).

## Regression gate

Phase-owned suites green: packaging (incl. size/uninstaller/headless/
updater/disclosure/audits), packaging_shell (10 checks), update_roundtrip,
launcher, cargo test (17 passed). Six prior-phase suites were transiently
red because a concurrent session was mid-refactor of the
session/selection/evidence layer; four recovered during the run
(agent/lesson/protocol/serve). The two still red (daemon_roundtrip
`check_answer_scoring`, evidence_roundtrip) fail on the working tree's
rewritten `handle_quiz_answer`/attempt semantics -- that refactor, not
phase 13 (verified: the base commit's legacy answer path is replaced by the
in-flight `session.do_action` flow; phase 13 does not touch those paths).

## Human verification items

1. **Compiled installer lifecycle** -- NSIS installer (needs makensis)
   installs per-user and uninstalls without touching the profile evidence
   store/banks (simulated in fixtures; the compiled installer is the gap).
2. **Install-notice rendering** -- the signed/unsigned notice renders real
   values in the actual installer (13-UI-SPEC 6.1).
3. **Release-time AV checklist** -- VirusTotal baseline and Microsoft
   false-positive submission at the first real release.
4. **Signed update install** -- a live `tauri-plugin-updater` install with a
   real minisign pubkey/signature and a release asset.
5. **Window liveness states** -- visual pass over the five states in the
   real window (copy and transitions are machine-checked).

## Gaps

None in the phase-owned automated surface. The toolchain/release-gated items
above are recorded (never claimed executed) and route to UAT.
