---
phase: 10-retention-pacing-trends
plan: 10-04
subsystem: runtime-pacing-override
tags: [cap, pacing, override, day, anki, evidence]
key-files:
  created:
    - tests/pacing_roundtrip.py
  modified:
    - evidence.py
    - retention.py
    - schemas/session.schema.json
    - schemas/response.schema.json
    - surfaces/session.py
    - surfaces/cli.py
    - surfaces/day.py
    - surfaces/daemon.py
    - tests/day_roundtrip.py
    - tests/daemon_roundtrip.py
key-decisions:
  - "The per-subject daily cap is a live-evidence projection: retention.cap_decision/subject_pacing count LIVE response events for the subject on the snapshot's local day -- pending manual responses count (pacing only), retracted and deduped events do not, and tick rows/session cursors/Anki counts/models/cache can never enter the count (D-07, D-09)."
  - "Start and genuine submit are both gated on one server capture: do_start derives the subject from the objective namespace (a client-forged subject/cap/snapshot/override is refused or ignored), decides the cap on the SAME capture that feeds the weights, blocks before choose/write at cap with the exact locked copy, and limits ordinary selection to remaining capacity; do_submit re-captures live evidence before a genuine append so a long/concurrent sitting cannot run past the cap and a crash-retry replay never double-counts (T-10-14)."
  - "The one audited exception is a one-sitting override (D-08): the exact confirmation phrase, an at-cap subject, a server-generated session id minted before the append, ONE append-only cap_override event (structurally scoreless, deterministic dedupe key) bound to that session/subject/local day/snapshot, and expiry when the sitting ends -- there is no persistent cap-disable setting anywhere."
  - "The day surface re-cuts every itembank pacing claim from ONE fresh evidence snapshot per render/--check call; the 60-second render cache can cover only external Anki latency and lanes info, and a cached Anki line discloses its age separately (T-10-17, D-05)."
  - "Anki stays an optional read-only card signal, owner-labelled (Anki: D due · N new) and never summed with itembank counts; when unavailable the exact locked copy is shown and nothing is blocked or written (D-05/SCHED-03); day.py issues only the deckNames/findCards reads."
  - "POST /api/override is the daemon twin of `itembank override`, registered in API_ROUTES/ROUTES/ROUTE_CLI and in the new SURFACE_PARITY table with its reserved itembank_override MCP tool name (Extensibility Rule 9(a)); the daemon error path is encoding-safe so the locked copy's U+2019 cannot kill the request thread."
requirements-completed: [SCHED-01, SCHED-02, SCHED-03, TREND-02, TREND-05]
completed: 2026-08-11
---

# Plan 10-04 Summary — Evidence-Derived Per-Subject Pacing, One-Sitting Override, Honest Anki Separation

**Objective:** Make the daily cap non-cosmetic and non-bypassable through a
long sitting while preserving a deliberate, auditable one-sitting exception,
and make `day` load come from live evidence with Anki as a separate
read-only signal (D-01, D-05, D-07 through D-09).

## What Was Built

- `evidence.cap_override_event` + `CAP_OVERRIDE_EVENT_TYPE` — the audited
  exception record, built exactly like `day_tick_event` (ValueError
  validation, deterministic `dedupe_key` over
  `(session_id, subject, local_date, snapshot_id, cap)`, standard envelope,
  structurally NO `score` key), written only through `append_event`.
- `retention.cap_decision` / `retention.subject_pacing` — pure projections
  over one snapshot: per-subject live local-day ordinary-attempt count
  (pending included; retracted/deduped/other-day excluded), cap/blocked/
  remaining, due-objective counts, and the shared claim marker on every
  row. No I/O, no surface imports, no item choice, no evidence writes.
- `surfaces/session.py` — `do_start(..., override_token=None)` derives the
  subject from the objective namespace (`_derive_subject`, client
  contradiction refused), refuses forged cap/snapshot/override spec fields,
  decides the cap on the same capture as the weights, blocks at cap with
  the locked copy before choosing/writing, clamps ordinary selection to
  remaining capacity, and persists the sitting's cap binding
  (`retention.cap` with override_event_id, null for ordinary sittings).
  `do_submit` re-captures live evidence before a genuine new append
  (replay dedupes to already_recorded and is never blocked -- detected
  across ALL live canonicals for the item, not just the last event, so a
  hint or interleaved answer cannot misclassify a retry; a genuine
  beyond-cap attempt is blocked with the locked copy; a live
  same-session cap_override authorizes). A confirmed override is still
  bounded to at most one cap's worth of items, never an unbounded binge.
  `cmd_override` is the CLI twin.
- `surfaces/cli.py` — `start` gains `--subject` and `--override-cap CONFIRM`;
  a new `override` subcommand (exact `--confirm` phrase, never a persistent
  ignore setting).
- `surfaces/daemon.py` — `POST /api/override` (bank + objective + token +
  count/seed/mode/selection_mode; subject derived server-side, forged
  fields ignored, wrong token 400, SystemExit->400, Exception->path-free
  500), registered in API_ROUTES/ROUTES/ROUTE_CLI plus the new
  SURFACE_PARITY table (route -> CLI twin + reserved `itembank_*` MCP tool
  name). `DaemonHandler.send_error` override makes error responses
  encoding-safe (UTF-8 body, ASCII reason phrase) so the locked copy's
  U+2019 never crashes the request thread.
- `surfaces/day.py` — `day_pacing(state, cfg)` (ONE capture per render),
  `pacing_lines`/`anki_line` (owner-labelled), `ANKI_UNAVAILABLE_COPY`
  exact locked text, pacing block + Anki line in `day_page`, pacing in
  `day_text`/`cmd_day --check`, `day_render` fresh-captures pacing every
  render with the cache restricted to Anki latency/lanes info and Anki age
  disclosed as a note, `day_state` docstring marks the cache as never a
  claim authority. Phase 1 day ticks remain the legacy checklist they are
  and never enter any pacing count.
- Schemas — `session.schema.json` gains an additive optional closed
  `retention.cap`; `response.schema.json` gains a closed `cap_override_event`
  oneOf branch (session scope const "sitting", no score key).
- `tests/pacing_roundtrip.py` (new, 7 checks) — fixed UTC local-day
  boundaries, pending/retraction/dedupe/out-of-day counting, remaining-
  capacity start, replay dedupe, beyond-cap genuine submit block via a
  concurrent-sitting race, scoped override append/expiry, forgery
  rejection. `tests/day_roundtrip.py` +4 checks (--check snapshot report,
  Anki populated/zero/unavailable owner separation, read-only Anki surface,
  local-day recut). `tests/daemon_roundtrip.py` +check_api_override_route
  (route scope 5->6, SURFACE_PARITY parity, forged containment, expiry).

## Verification

- `python tests/pacing_roundtrip.py` — pass
- `python tests/day_roundtrip.py` — pass (existing + 4 new checks)
- `python tests/daemon_roundtrip.py` — pass (61 checks)
- `python tests/evidence_roundtrip.py`, `python tests/protocol_roundtrip.py`,
  `python tests/retention_roundtrip.py`,
  `python tests/selection_retention_roundtrip.py`,
  `python tests/agent_roundtrip.py`, `python tests/config_roundtrip.py`,
  `python tests/selection_roundtrip.py` — all pass
- Full suite: every `tests/*_roundtrip.py` green except the documented
  Windows-only `packaging_roundtrip.py` onedir gate (unchanged from 10-02).

## Post-Implementation Failures and Root Causes

1. **`expand_spec` validated the client `subject` key** (`invalid selection
   spec: additional property 'subject'`). `do_start` popped the subject
   AFTER `selection.expand_spec` ran. Fixed by deriving/popping the subject
   (and the forged-field refusal) before expansion.
2. **The private `_snapshot` leaked into the selector**: `_retention_context`
   now returns `_snapshot` so start and day share one capture, but
   `selection._validate_retention_context` allowlists exactly two keys.
   Fixed at both call sites (`do_start`, `do_select`) by stripping
   `_snapshot` before `selection.select`; selection.py was not modified.
3. **`SURFACE_PARITY` vs `API_ROUTES` key shape**: the new parity test
   compared 2-tuples against 3-tuples. Fixed the projection in the test.
4. **Pacing test shape**: `session_view` returns `total`/`item`, not
   `items`; the replay step needed a still-active session (re-arm the
   cursor); and with an unnamespaced fixture bank the sitting's own
   recorded response cannot push the namespaced subject to cap, so the
   beyond-cap guard is exercised by a concurrent-sitting race (two sittings
   authorized by the same remaining capacity — exactly the race the live
   recheck exists to stop).
5. **The daemon's at-cap 400 killed the request thread**: the locked copy
   carries U+2019 and the built-in `send_error` encodes the reason phrase
   as latin-1, raising `UnicodeEncodeError` inside the `except SystemExit`
   clause (connection closed, no response). Fixed with an encoding-safe
   `DaemonHandler.send_error` (exact message in a UTF-8 body, standard
   ASCII reason phrase).
6. **`check_api_start_traversal` flaked under concurrent sibling agents**:
   it snapshotted the whole `/tmp` parent, and other phase worktrees'
   tests create temp workdirs with `_evidence`/`_attempts` mid-check.
   Scoped the snapshot to the served root plus the one escape target the
   hostile values aim at — same guarantee, hermetic.
7. **`day_page` template slot mismatch** after inserting the pacing/Anki
   blocks (one extra `%s`); caught by the served-page smoke test, fixed.
8. **`tests/day_roundtrip.py` cold-render timeout**: under heavy
   parallel-agent load (load average ~21) the first day page render can
   take several seconds; the 5s urllib timeout flaked. Raised to 60s —
   the check asserts correctness, not speed.

## Success Criteria

- A subject cannot be binged past its daily ordinary-attempt cap through
  start or a long sitting. ✓
- The only exception is explicit, recorded, and expires with one sitting. ✓
- Day load comes from live evidence, not ticks/session files/Anki/model/
  cache. ✓
- Anki remains a separate read-only optional card signal and never becomes
  an objective scheduler. ✓
