---
status: clean
phase: 13-desktop-packaging-tauri-sidecar
reviewed: 2026-08-10
method: inline review (subagent dispatch unreliable in this runtime per AGENTS.md)
scope: phase-13 source changes only (sidecar, shell, packaging, updater)
---

# Phase 13 Code Review

## Review focus

The phase's security-sensitive surfaces: the per-launch token gate, the
stdout handshake, the loopback proxy, the job-object lifecycle, the
installer/uninstaller scope, and the updater channel.

## Findings

| Severity | Finding | Resolution |
|---|---|---|
| High (fixed) | Token gate used `==` string comparison -- a local timing probe could leak token prefix length (T-13-01). | `secrets.compare_digest` applied in `_sidecar_token_ok`; packaging_shell suite re-verified green. |
| Info | `tauri://localhost` asset URLs are Windows-specific -- correct for this phase (D-13 defers Linux/macOS), documented in main.rs. |
| Info | The shell's job object and proxy are intentionally leaked for the app lifetime; comments explain why dropping them would kill the sidecar / close the listener. |
| Info | The updater pubkey is empty until the build supplies a real key -- the plugin is inert rather than unverified (T-13-13), recorded in 13-04-SUMMARY. |

## Scope notes

- The proxy forwards only to the sidecar's loopback daemon, strips
  `Origin`/hop-by-hop headers, and adds the token -- no new trust boundary.
- The uninstaller's `RMDir /r "$INSTDIR\*"` is the only deletion; the fixture
  proves profile data survives.
- The frozen sidecar is `--noconsole` onedir; its stdout pipe is what the
  shell reads, so the handshake contract holds in the packaged shape.

## Blocked suites (environmental, not review findings)

Six prior-phase suites (`agent`, `daemon`, `evidence`, `lesson`, `protocol`,
`serve`) failed during the run because a concurrent session was mid-refactor
of `session.py`/`evidence.py`/`selection.py`; they are not phase-13 changes
and are tracked in 13-GATES.md. `agent_roundtrip` re-passed as the refactor
converged.
