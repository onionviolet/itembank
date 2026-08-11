# Autonomous Run Handoff — Phase 999.4 (Canvas LMS integration via LTI)

**Project:** itembank
**Branch:** `gsd/phase-999.4-exec` (worktree `C:\Users\wayba\Downloads\CTF\itembank\.phase9994x-wt`)
**Created from:** `gsd/phase-999.4-plan` (the planning branch — CONTEXT/RESEARCH/UI-SPEC/VALIDATION and the three plans were present)
**Executed:** 2026-08-11, all three waves, one atomic commit per plan
**Not merged, not pushed** — per the run instructions.

## Where we are

| Wave | Plan | Commit | What landed |
|---|---|---|---|
| 1 | 999.4-01 | `c174694` feat | LTI 1.3 spine: platforms registration store, optional crypto guard (named refusal), JWKS-verified OIDC launch (iss/aud/nonce/exp/deployment), one-time nonce store, in-process wrap of `daemon.handle_api_*` (D-01), `itembank lti status/doctor/serve`, opt-in bind with stdlib-TLS |
| 2 | 999.4-02 | `6c04055` feat | Deep-link picker (one objective per assignment, ids/titles only, verbatim copy), embedded learner player (quiz serve projection, public_item-only until a recorded response, frame-ancestors CSP), privacy line + completion framing |
| 3 | 999.4-03 | `587027f` feat | AGS grade passback (opt-in, completion-only, idempotent, PendingManual for pending prose, evidence untouched), hosting doc (stdlib TLS + reverse proxy), dependency pins with CVE disposition, manual Canvas checklist |

Phase docs: `999.4-0N-SUMMARY.md` (×3), `999.4-VERIFICATION.md`,
`999.4-UAT.md`, `999.4-VALIDATION.md` (statuses green), `STATE.md` updated.

## How to resume / next steps

1. **Review the branch.** `git -C .phase9994x-wt log --oneline -4` and
   `git -C .phase9994x-wt diff gsd/phase-999.4-plan..gsd/phase-999.4-exec`.
   The worktree is ready to merge (`git worktree remove` after review; a
   merge was deliberately left undone per the run instructions — the
   planner's worktree `.phase9994-wt` and the main tree were untouched).
2. **Run the phase tests:** `python tests/lti_roundtrip.py` (24 checks) and
   the full suite `tests/*_roundtrip.py`.
3. **UAT (manual-only, R-01 fallback):** the live-Canvas install → launch →
   deep-link → learner completion → AGS passback → gradebook checklist in
   `999.4-UAT.md` / `999.4-VALIDATION.md`. The automated suite never fakes
   a live Canvas result.
4. **`$gsd-verify-work 999.4`** when the manual items are ratified, then
   merge `gsd/phase-999.4-exec` and update REQUIREMENTS.md statuses
   (LTI-01..LTI-07 currently Pending → Implemented/Verified).

## Decisions and findings a fresh chat must know

- **D-01 spine:** the LTI surface calls the daemon's `handle_api_*`
  functions in-process through a shim handler; `API_ROUTES`/`ROUTE_CLI`/
  `check_api_route_scope` are byte-unchanged; no scoring outside runtime.py
  (grep-asserted).
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
