---
phase: 02-daemon-consolidation-settings-foundation
fixed_at: 2026-08-07T21:55:51Z
review_path: .planning/phases/02-daemon-consolidation-settings-foundation/02-REVIEW.md
iteration: 1
findings_in_scope: 9
fixed: 9
skipped: 0
status: all_fixed
---

# Phase 02: Code Review Fix Report

**Fixed at:** 2026-08-07T21:55:51Z
**Source review:** .planning/phases/02-daemon-consolidation-settings-foundation/02-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope (critical + warning): 9 (CR-01, CR-02, WR-01 through WR-08 -- WR-03 and WR-08 describe the same defect and were fixed together)
- Fixed: 9
- Skipped: 0
- Info items (IN-01, IN-02, IN-03) were out of scope for this run (`fix_scope: critical_warning`) and were not touched.

**Update -- fix commits are now on `main`.** All 9 fixes were made and
committed inside an isolated git worktree on a temp branch,
`gsd-reviewfix/02-88709`, created from `main` at `32c46bd`. By the time the
worktree's cleanup tail ran, `main` had advanced with 2 unrelated commits
(`0a9638c`, `1aba4d9`, both `docs(02.1)`/`docs(phase-2.1)` -- neither touches
any file this run modified). The cleanup tail's `git merge --ff-only` refused
to fast-forward on that divergence (by design -- it never silently drops or
rewrites history), so `gsd-reviewfix/02-88709` was preserved rather than
merged or deleted. The orchestrator merged it into `main` with a non-fast-forward
merge commit and re-ran the full test suite (all 12 files pass); the branch has
since been deleted.

**Verification environment:** All edits and test runs happened inside that isolated git worktree (`git worktree add -b gsd-reviewfix/02-88709 <tmp-dir> main`). Every syntax check, manual reproduction, and test-suite run below ran inside the worktree, not the main checkout; the worktree itself was removed after the final commit (its commits live on the preserved branch above), so these results are reproducible from `gsd-reviewfix/02-88709` at the commit hashes listed once merged, not from the (now-gone) worktree path itself. The full suite (`tests/*.py`, 11 files) was run once after all nine fixes were applied, in addition to per-fix targeted runs, and passed end to end.

## Fixed Issues

### CR-01: One non-UTF-8 `.md` file anywhere in the served directory crashes the entire daemon at startup

**Files modified:** `surfaces/daemon.py`
**Commit:** `e7c929a`
**Applied fix:** Wrapped `scan_dir()`'s per-candidate `open(path, encoding="utf-8").read()` in a `try`/`except (OSError, UnicodeDecodeError): continue`, matching the "neither a bank nor a plan; skip silently" precedent already in the same loop. Verified with `tests/daemon_roundtrip.py` (46 checks) and by re-reading the edited lines.

### CR-02: `itembank.json` is never validated against its own schema on read

**Files modified:** `surfaces/settings.py`
**Commit:** `936b954`
**Applied fix:** `load_settings()` now validates the merged document one known top-level key at a time against that key's own subschema via `schema_validate.validate()`, and `sys.exit()`s with a `settings.*`-coded message (the same `classify_error()` mapping `cmd_config set` already uses) on the first failure. Deliberately validates per-key rather than the whole document at once, so the schema's top-level `additionalProperties: false` is not enforced at this layer -- an unrecognized top-level key must keep round-tripping untouched (`merge_over_defaults`'s own "unknown, not dropped" contract, and `tests/config_roundtrip.py::test_unknown_key_preserved`, which would otherwise have broken under a literal whole-document `validate()` call as REVIEW.md's fix snippet showed it). All three reproductions from REVIEW.md were manually re-run against the fixed code and now exit with a clean `settings.invalid_type: ...` message instead of a raw Python traceback:
- `"daemon": "oops-not-a-dict"` + `itembank daemon <dir>` -> `settings.invalid_type: $: expected type object, got str`
- `"daemon": {"port": "not-an-int", ...}` + `itembank daemon <dir>` -> `settings.invalid_type: $.port: expected type integer, got str`
- `"daemon": "oops-not-a-dict"` + `itembank config set daemon.port 9000` -> `settings.invalid_type: $: expected type object, got str` (load_settings now exits before `set_at` is ever reached)

Verified with `tests/config_roundtrip.py` and `tests/daemon_roundtrip.py`.

### WR-01: Daemon `500` responses can leak local filesystem paths, unlike its `404` responses

**Files modified:** `surfaces/daemon.py`
**Commit:** `07bb8fe`
**Applied fix:** Added `DaemonHandler.send_server_error(self, exc)`, mirroring `send_not_found`'s T-2-05 discipline: it prints `str(exc)` server-side only, then sends a generic `handler.send_error(500, "internal error")` to the client. Replaced all 8 occurrences of `handler.send_error(500, str(exc))` with `handler.send_server_error(exc)`. Verified with `tests/daemon_roundtrip.py` and `tests/serve_roundtrip.py`.

### WR-02: The index's "View report" link resolves to an arbitrary session, not the most recent one

**Files modified:** `surfaces/daemon.py`
**Commit:** `205819b`
**Applied fix:** `sessions_by_bank()` now tracks each candidate session's file `mtime` (cheap, alongside the existing `open()`/`json.load()`) and keeps the newest-mtime session per bank stem, instead of letting the lexically-largest `session_id` (a random uuid4 hex, unrelated to time) win. `write_session`'s tmp-then-`os.replace()` refreshes the mtime on every `do_next`/`do_submit`, so this now tracks the most recently *active* session. Verified with `tests/daemon_roundtrip.py`.

### WR-03 / WR-08: `POST /day/<stem>/open` returns a generic `500` instead of `400`/`404` for a non-numeric `i`

**Files modified:** `surfaces/day.py`
**Commit:** `dfabd98`
**Applied fix:** `apply_day_post`'s `open` branch no longer does a bare `int(data.get("i") or 0)`. It now reads `i = data.get("i", 0)`, treats an explicit `None` as `0`, and returns the existing `None` out-of-range sentinel (which `handle_day_open` already turns into a clean 404) for anything that is not a plain `int` (booleans excluded, matching the project's existing `isinstance(x, int) and not isinstance(x, bool)` pattern used elsewhere). Manually reproduced the review's exact scenario (`{"lane": "EMT", "i": "not-a-number"}`) against the fixed `apply_day_post` and confirmed it now returns `None` instead of raising `ValueError`. Verified with `tests/daemon_roundtrip.py` and `tests/day_roundtrip.py`. WR-08 folded into this same fix per REVIEW.md's own note that it is the same defect, not a separate spot.

### WR-04: `/api/start` and the CLI's `--count` accept a negative count, silently truncating the bank via slice semantics

**Files modified:** `surfaces/session.py`
**Commit:** `5df8b4f`
**Applied fix:** `do_start()` now `sys.exit()`s with `"count must be a positive integer, got %r"` when `count` is not a plain positive `int` (booleans excluded), before it ever reaches `candidates[:min(count, len(candidates))]`. Checked centrally in `do_start` rather than per-caller, so both the CLI path (`cmd_start` -> `sys.exit` reports and exits 1) and the daemon path (`handle_api_start`'s existing `except SystemExit as exc: handler.send_error(400, ...)` around `session.do_start`) get the same guard for free. Manually reproduced REVIEW.md's exact repro: `itembank start fixtures/sample_bank.md --count -1 --seed 0` now exits 1 with `count must be a positive integer, got -1` instead of silently writing a 5-item session (out of a 6-item fixture bank). `--count 0` was also confirmed rejected, and a valid positive count still starts a session normally. Verified with `tests/agent_roundtrip.py`, `tests/daemon_roundtrip.py`, and `tests/serve_roundtrip.py`.

### WR-05: `ms_since()` can record a negative `response_time_ms` under a backward wall-clock change

**Files modified:** `surfaces/session.py`
**Commit:** `ba8ad19`
**Applied fix:** `ms_since()`'s return is now `max(0, int((now - served).total_seconds() * 1000))`, matching the client-side JS's `Math.max(0, Math.round(performance.now() - shownAt))` (`surfaces/quiz_page.py`, T-1-25). Manually confirmed with a `served_ts` set 5 seconds in the future (simulating a backward clock adjustment) that `ms_since()` now returns `0` instead of a negative number. Verified with `tests/evidence_roundtrip.py` (which asserts the non-negative `response_time_ms` invariant this fix protects), `tests/agent_roundtrip.py`, and `tests/daemon_roundtrip.py`.

### WR-06: The daemon's per-plan day state fixes "today" once and never re-derives it

**Files modified:** `surfaces/daemon.py`
**Commit:** `d482c2d`
**Commit status:** fixed: requires human verification (date/time-conditional logic; see note below)
**Applied fix:** `_plan_day_state()` now rebuilds a plan's cached `day.day_state()` once the wall-clock date has moved past the cached state's own `iso`, instead of caching it for the handler class's entire lifetime. A backfilled/overridden `iso` (`itembank day --date`, threaded through `day_extra`) is exempt from re-derivation, since it names a specific historical date rather than "today." Manually simulated both branches against a fake handler: (1) a state cached with yesterday's `iso` was rebuilt to today's `iso` on the next `_plan_day_state()` call, confirmed by object identity (`result is not state`) and by the returned `iso` matching `datetime.date.today().isoformat()`; (2) a state cached with an `iso` override present in `day_extra` was returned unchanged (`result is state`), confirming a backfill is never auto-advanced. Verified with `tests/daemon_roundtrip.py` and `tests/day_roundtrip.py`. Flagged for human verification because this is a date-conditional logic change that the existing automated suite cannot exercise across a real midnight rollover (it would require mocking `datetime.date.today()` inside the daemon process); the manual simulation above exercised the same code path directly but a developer should confirm the behavior once more against a real long-running daemon instance before relying on it in production.

### WR-07: `schema_validate.check_schema()` never resolves or recurses into `$ref`

**Files modified:** `schema_validate.py`
**Commit:** `d2dddfe`
**Applied fix:** `check_schema()` now threads a `root` parameter down through its recursive calls (mirroring how `validate()` already threads `root`), and gained a `$ref` branch: it validates the `$ref` string shape, resolves the target against `root`'s `$defs`, raises `SchemaError` if the target does not resolve, and recurses `check_schema()` into the resolved subschema. Manually reproduced REVIEW.md's exact scenario (`{"$ref": "#/$defs/typo"}`) and confirmed `check_schema()` alone (not just `validate()`) now raises `SchemaError: $ref '#/$defs/typo' at #.properties.x does not resolve` immediately, before any instance is examined. Also confirmed a valid `$ref` still passes, and that an unsupported keyword inside a `$ref` target is caught. Verified with `tests/config_roundtrip.py` and a direct CLI run of `schema_validate.py` against the real `schemas/settings.schema.json` + `itembank.json` (0 errors, unchanged).

## Skipped Issues

None -- all 9 in-scope findings (CR-01, CR-02, WR-01 through WR-08) were fixed.

---

_Fixed: 2026-08-07T21:55:51Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
