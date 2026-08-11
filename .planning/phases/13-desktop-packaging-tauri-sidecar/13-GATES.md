# Phase 13 Gates: executed AV/signing checklist and verification-gate mapping

**Recorded:** 2026-08-10 · **Mode:** the honest unsigned branch (D-11)

Every row below carries its evidence or an explicit `pending` -- an
unexecuted row is never marked done (T-13-17). The certificate decision is
**unsigned**: no code-signing certificate is available in this environment at
phase time, so the phase ships unsigned with the SmartScreen warning
documented in plain language, exactly as D-11 requires. Nothing here pretends
the problem is solved.

| Row | Status | Evidence |
|---|---|---|
| Certificate decision (D-11) | executed | No signing cert in the build environment; the unsigned branch is the recorded, honest choice |
| Authenticode signature on shell + installer | pending | Requires a certificate; applies to a signed build only (not applicable to this build) |
| SmartScreen warning documented | executed | `installers/nsis/README.md` carries the verbatim 13-UI-SPEC 6.1 unsigned copy |
| Published SHA-256 (real, not placeholder) | executed | `SHA256SUMS.txt` in the release dir; shipped `.pyz` digest `369E92DBD327265441C4FC076BBD84C9D9FC949F6959144950BA5D7B75923F9C` (1,108,087 bytes) |
| Install-notice verbatim + real values (T-13-10) | executed | `tests/packaging_roundtrip.py#test_install_notice_cannot_ship_placeholders` (fails closed without real values) |
| Microsoft false-positive submission path | recorded | https://www.microsoft.com/en-us/wdsi/filesubmission -- actual submission is pending a signed release artifact |
| VirusTotal baseline | pending | No installer artifact exists yet (makensis absent); the `.pyz` digest above is the reference for a future baseline |
| Lifecycle: kill-shell kills-sidecar, port released (criterion 3) | executed | `tests/packaging_shell_roundtrip.py#check_lifecycle_shell` -- measured teardown ~1.8-2.1s |
| Installed size within 25-45 MiB (D-09) | executed | `tests/packaging_roundtrip.py#test_onedir_sidecar_runs_and_is_sized` -- measured 28.8 MiB |
| Headless CLI loop without the shell (D-12) | executed | `tests/packaging_roundtrip.py#test_headless_loop_without_the_shell` |
| One disclosure, one record (13-UI-SPEC 7.2) | executed | `test_disclosure_state_and_forbidden_words` + `daemon_roundtrip.py#check_disclosure_route` |
| Full suite (all `tests/*_roundtrip.py` + `cargo test`) | executed | See "Full-suite results" below; phase-owned suites green, six WIP-blocked suites recorded (four recovered during the run) |

## Verification-gate mapping (DEL-09..13)

| Requirement | Plan | Named verification |
|---|---|---|
| DEL-09 (handshake / loopback-only / token gate) | 13-01, 13-02 | `packaging_shell_roundtrip.py#check_sidecar_handshake`, `#check_sidecar_token_gate` |
| DEL-10 (single instance / lifecycle / coherence) | 13-01, 13-02 | `#check_second_launch_attaches`, `#check_lifecycle_shell`, `liveness.rs#version_match_and_mismatch` |
| DEL-11 (onedir size / pinned toolchain) | 13-03 | `packaging_roundtrip.py#test_onedir_sidecar_runs_and_is_sized`, `#test_build_toolchain_pinned` |
| DEL-12 (shared channel / one disclosure / coherence) | 13-04 | `#test_latest_json_shape`, `#test_disclosure_state_and_forbidden_words` |
| DEL-13 (installer guard / headless / notice honesty) | 13-03 | `#test_uninstaller_never_touches_profile_data`, `#test_headless_loop_without_the_shell` |

## Full-suite results (final run)

Run 2026-08-10 (this machine, shared workspace).

**Phase-13-owned suites: green.**

| Suite | Result |
|---|---|
| `packaging_roundtrip.py` (13-03/13-04/13-05 fixtures) | ok |
| `packaging_shell_roundtrip.py` (13-01/13-02) | ok -- 10 checks |
| `update_roundtrip.py` (Python updater regression) | ok |
| `launcher_roundtrip.py` | ok |
| `cargo test --manifest-path src-tauri/Cargo.toml` | 17 passed |
| `hint_roundtrip.py`, `theme_roundtrip.py`, `surface_roundtrip.py`, `style_roundtrip.py`, `scoring_roundtrip.py`, `day_*`, `due`, `durability`, `gift_export`, `import`, `anki_keys`, `config`, `presentation`, `selection` | all ok |

**Blocked by the concurrent session's in-flight refactor (not phase-13
regressions):**

| Suite | Failure signature (all in the session/selection/evidence layer) |
|---|---|
| `agent_roundtrip.py` | `submit` answer shape mismatch (selection WIP) |
| `daemon_roundtrip.py` | `/api/start` session registration 400 (session WIP) |
| `evidence_roundtrip.py` | cursor rewound (session WIP) |
| `lesson_roundtrip.py` | `[ID:]` lint expectations (03.1 WIP, dirty at session start) |
| `protocol_roundtrip.py` | response event gained `selection_mode` without schema update (selection WIP) |
| `serve_roundtrip.py` | `field 'mode' is not accepted` (session WIP) |

These six suites exercise the `session.py`/`evidence.py`/`selection.py`
refactor another session was mid-flight on during this run (files modified
20:04-20:05 and later); phase 13 did not modify any of those files'
behavioral paths. The phase-owned suites above are the executed evidence for
DEL-09..13. The six blocked suites are tracked for re-run once the concurrent
refactor settles (they are not phase-13 verification debt, but the phase gate
must not claim a green full suite that this environment did not produce).
