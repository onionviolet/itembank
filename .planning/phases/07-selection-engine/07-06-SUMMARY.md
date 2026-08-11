---
phase: 07-selection-engine
plan: 06
subsystem: selection
tags: [selection, contract, cli, preview, profiles]

requires:
  - phase: 07
    plan: 05
    provides: MODES, exposure, selection settings
provides:
  - schemas/selection.schema.json (sixth published contract)
  - itembank select --explain + render_trace()
  - /api/start preview branch (no fifth route)
  - expand_spec() + selection.profiles
affects: [10]

actuals:
  tokens: 5500
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - one runtime call (do_select) behind the CLI and the daemon preview
    - profiles expand key-by-key under explicit flags, validated at use time

key-files:
  created:
    - schemas/selection.schema.json
    - surfaces/selection_cli.py
  modified:
    - surfaces/protocol_cli.py
    - surfaces/session.py
    - surfaces/cli.py
    - surfaces/daemon.py
    - selection.py
    - schemas/settings.schema.json
    - itembank.py
    - tests/selection_roundtrip.py
    - tests/protocol_roundtrip.py
    - tests/agent_roundtrip.py

key-decisions:
  - "The sixth contract is warranted: every other request/response shape is published, and the spec is the one shape all surfaces must agree on."
  - "Preview rides /api/start (D-14) and writes nothing: no session, no evidence append -- a preview that recorded itself would poison the cooldown history it previews."

patterns-established:
  - "render_trace lives in the CLI tier; select() stays pure."

requirements-completed: [SEL-01, SEL-04, SEL-05]

coverage:
  - id: D1
    description: itembank select --explain prints plain-English prose with a named runner-up and no key material
    requirement: SEL-05
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_explain_renders_plain_text
        status: pass
    human_judgment: false
  - id: D2
    description: the selection spec is a published, validator-checked contract
    requirement: SEL-01
    verification:
      - kind: integration
        ref: tests/protocol_roundtrip.py (six contracts, schema --all stable)
        status: pass
    human_judgment: false
  - id: D3
    description: preview writes no session and no evidence; profiles expand and flags override key by key
    requirement: SEL-04
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_preview_writes_no_session
        status: pass
      - kind: unit
        ref: tests/selection_roundtrip.py#check_profile_flags_override
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-10
status: complete
---

# Phase 7 Plan 6: Selection Surfaces Summary

**The selector speaks: `itembank select --explain` renders the trace as prose a learner reads, `/api/start` previews without a fifth route, named profiles expand key-by-key, and the selection spec is the sixth published contract.**

## Performance

- **Duration:** 45 min
- **Started:** 2026-08-10T21:56:00Z
- **Completed:** 2026-08-10T22:41:00Z
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments

- `schemas/selection.schema.json`: sixth published contract, all keywords in
  `schema_validate.SUPPORTED`, properties matching SPEC_FIELDS + profile.
- `do_select` (shared load/lint/history with do_start) returns public_item
  payloads + trace and writes nothing; `surfaces/selection_cli.py` has
  `render_trace` + `cmd_select`.
- `select` and `start` carry the full spec flag set with None defaults;
  `type`/`difficulty` filter stages complete SEL-01's four-way filter.
- `/api/start` `"preview": true` returns items + trace, writes no session and
  appends no evidence; forbidden fields still 400.
- `selection.profiles` + `expand_spec()` (profile expanded, flags override key
  by key, validated at use time).
- All 18 selection checks live; pending count 0.

## Task Commits

1. **Task 1: sixth contract** - `cf70457`
2. **Task 2: select --explain + flags + expand_spec** - `0312ebd`
3. **Task 3: preview + profiles + final checks** - `dcbce87`

**Plan metadata:** pending (next commit)

## Deviations from Plan

- `API_ROUTES` is currently five, not four: the concurrent 13-04 session added
  a `/disclosure` route (their work, uncommitted/committed under their label).
  Phase 7 added no route; the plan's four-route acceptance is blocked by the
  concurrent session, logged in deferred-items.md.
- The daemon preview acceptance "temp root gains no _attempts/" cannot be
  isolated from `itembank serve`'s own launch-time `_attempts/` creation; the
  meaningful property (preview adds no files, no evidence append) is asserted
  by the CLI-driven check and verified on the daemon path.
- Concurrent sweeps again mixed labels (session.py refactor rode in `0312ebd`).

## Issues Encountered

- Preview initially crashed post-registration on `result["session_id"]`;
  guarded the registration with `preview is not True`.
- `public_item()` does not expose `objective`; profile checks assert via the
  resolved spec instead.

## Next Phase Readiness

- Phase 7 complete (pending verification gates): 6/6 plans, 18/18 selection
  checks, SEL-01..SEL-05 implemented. Phase 10 consumes the spec/profiles and
  the soft-penalty seam.

---
*Phase: 07-selection-engine*
*Completed: 2026-08-10*
