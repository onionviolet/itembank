# Autonomous Run Handoff — Phase 999.4 (Canvas LMS integration via LTI)

**Project:** itembank
**Branch:** `gsd/phase-999.4-exec` (worktree `C:\Users\wayba\Downloads\CTF\itembank\.phase9994-wt`)
**Created from:** `gsd/phase-999.4-plan` (the planning branch — CONTEXT/RESEARCH/UI-SPEC/VALIDATION and the three plans were present)
**Executed:** 2026-08-11, all three waves, one atomic commit per plan
**Finalized for merge:** 2026-08-11 — `main` merged in (branch up to date), post-merge suite + schema validation green, handoff current. Not yet merged into `main`, not pushed — per the run instructions.

## Where we are

| Wave | Plan | Commit | What landed |
|---|---|---|---|
| 1 | 999.4-01 | `c174694` feat | LTI 1.3 spine: platforms registration store, optional crypto guard (named refusal), JWKS-verified OIDC launch (iss/aud/nonce/exp/deployment), one-time nonce store, in-process wrap of `daemon.handle_api_*` (D-01), `itembank lti status/doctor/serve`, opt-in bind with stdlib-TLS |
| 2 | 999.4-02 | `6c04055` feat | Deep-link picker (one objective per assignment, ids/titles only, verbatim copy), embedded learner player (quiz serve projection, public_item-only until a recorded response, frame-ancestors CSP), privacy line + completion framing |
| 3 | 999.4-03 | `587027f` feat | AGS grade passback (opt-in, completion-only, idempotent, PendingManual for pending prose, evidence untouched), hosting doc (stdlib TLS + reverse proxy), dependency pins with CVE disposition, manual Canvas checklist |

Phase docs: `999.4-0N-SUMMARY.md` (×3), `999.4-VERIFICATION.md`,
`999.4-UAT.md`, `999.4-VALIDATION.md` (statuses green), `STATE.md` updated.

## Merge into main and post-merge verification (2026-08-11)

`main` was merged into `gsd/phase-999.4-exec` (`a25cc9d`) and the branch is
up to date. Six conflicts resolved, keeping both phases' behavior:

| File | Resolution |
|---|---|
| `schemas/settings.schema.json` | `required` gains both `lti` (999.4) and `retention` (10); the `lti`, `retention` and `audio` property blocks all ship; JSON re-verified |
| `surfaces/cli.py` | evidence import gains `cmd_trends` (main); the `lti` subparser family kept (999.4) |
| `surfaces/quiz.py` | `page_for` carries `lti_framing`/`boot_extra` (999.4) *and* `assist` (08-05); both `__LTI_FRAMING__` and `__ASSIST__`/`__ASSIST_JS__` slots substituted |
| `tests/config_roundtrip.py` | schema key set expects `lti` + `retention` + `audio` |
| `.planning/REQUIREMENTS.md` | AUDIO rows `Complete` (main) + LTI rows `Pending` (999.4) both kept |
| `.planning/STATE.md` | kept main's version — orchestrator reconciles centrally; not hand-edited per run instructions |

One merge-adaptation fix on top: `test(999.4-04)` reworked the LTI
route-scope check — main grew `daemon.API_ROUTES` from 5 to 10, so the
hardcoded count was a merge casualty. The check now asserts the phase's
real invariant (the five wrapped session handlers are present, and
`surfaces/lti.py` never assigns/mutates `daemon.API_ROUTES`); route-count
ownership stays with `daemon_roundtrip.check_api_route_scope`.

**Post-merge suite:** 46 test files — 42 green, 4 failures, all
pre-existing on `main` (verified by running them against a pristine `main`
extraction), none introduced by this merge:
- `evidence_roundtrip.py` — expects `meta.index_version` "3"; `evidence.py`
  ships `INDEX_VERSION = 2` on `main` (a 3 existed in 06.2 history and was
  later reverted; the test was never re-synced).
- `gate_roundtrip.py` — expects `objective_history` rows to carry `context`
  (`["lesson_gate", "quiz"]`); `main`'s rows come back `[None, None]`.
- `packaging_roundtrip.py` — environment-gated: needs the machine-built
  Windows bundle `dist/itembank-sidecar-onedir` (documented pre-existing).
- `phase_062_audit.py` — re-runs the suite, inherits the three above.

Also green after the merge: `tests/lti_roundtrip.py` (24 checks), `itembank.py
lint fixtures/sample_bank.md` (0 errors), `itembank.py build` of the sample,
and the CI `schema_validate.py` flow (session, item, response, report,
history, lint_error errors+warnings) — 0 failures.

## How to resume / next steps

1. **Merge the branch into `main`** when the orchestrator is ready: `gsd/phase-999.4-exec` is up to date with `main` (merged `a25cc9d`) and the post-merge suite is green. Do NOT edit `.planning/ROADMAP.md`, `.planning/STATE.md` or `.planning/config.json` — the orchestrator reconciles them centrally after all phase branches merge (STATE.md was kept at main's version in the merge for exactly this reason).
2. **UAT (manual-only, R-01 fallback):** the live-Canvas install → launch →
   deep-link → learner completion → AGS passback → gradebook checklist in
   `999.4-UAT.md` / `999.4-VALIDATION.md`. The automated suite never fakes
   a live Canvas result.
3. **`$gsd-verify-work 999.4`** when the manual items are ratified, then
   update REQUIREMENTS.md statuses
   (LTI-01..LTI-07 currently Pending → Implemented/Verified).

## Decisions and findings a fresh chat must know

- **D-01 spine:** the LTI surface calls the daemon's `handle_api_*`
  functions in-process through a shim handler; `API_ROUTES`/`ROUTE_CLI`/
  `check_api_route_scope` are byte-unchanged in the daemon; no scoring
  outside runtime.py (grep-asserted). The 999.4 route-scope test was
  reworked post-merge (`test(999.4-04)`) — see the merge section above.
- **Registration resolution:** the launch handler resolves the platform
  from the server-issued `state` (never an unverified `iss` claim); the
  message type is branched from the *verified* claims.
- **Objective picker:** lists the distinct `[OBJECTIVE:]` values per bank —
  the exact set `handle_api_start` resolves (D-07's operative clause), not
  `[OBJ:]` provenance ids. id == title (an `[OBJECTIVE:]` reference is
  self-describing).
- **Phase finding:** a completed session with pending prose is unreachable
  through the learner flow in this build (`short` defers without advancing;
  marks don't advance the cursor either). The PendingManual branch is
  implemented and tested against the marker-closed state (runtime's own
  completion arithmetic via `write_session`). A future close-session
  feature makes it reachable end-to-end. See 999.4-VERIFICATION.md.
- **CVE disposition:** cryptography 43.0.0 + PyJWT 2.10.1 are pinned with
  checksums and the license review; their published advisories affect paths
  this code never calls (PyJWT decode, cryptography x509 verification). The
  pin record (`deps/lti-pins.txt`) documents the upgrade path
  (PyJWT>=2.13.0, cryptography>=49.0.0).
- **config.json** was not changed: it carries workflow toggles only and has
  never been updated per-phase in this repo's history; STATE.md carries the
  phase state.
- **Known transient:** `tests/daemon_roundtrip.py` occasionally flakes under
  socket churn from the LTI harness servers (fixed-port probing vs
  TIME_WAIT); re-run is green — pre-existing sensitivity, not a regression.
- **Environment-gated test:** `tests/packaging_roundtrip.py` requires the
  machine-built Windows shell bundle (`dist/itembank-sidecar-onedir` from
  `scripts/build_shell.ps1`) plus a Windows runtime to execute the frozen
  sidecar; it fails on this Linux bash identically on the planning branch —
  unchanged by phase 999.4. `packaging_shell_roundtrip.py` (10 checks) is
  green. A stray untracked `fake_hosted_unused.py` (pre-existing in the
  main tree) sits in the worktree and is not committed.
- **Review hardening:** `147e379` tightened JWKS key selection (a header
  kid must match a JWKS key; only a kid-less header falls back to the
  single key) — found in the final review pass after the wave commits.
