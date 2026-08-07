---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 02
current_phase_name: Daemon Consolidation & Settings Foundation
status: verifying
stopped_at: Completed 02-06-PLAN.md (phase 02 complete)
last_updated: "2026-08-07T19:08:49.553Z"
last_activity: 2026-08-07
last_activity_desc: Phase 02 execution started
progress:
  total_phases: 2
  completed_phases: 2
  total_plans: 17
  completed_plans: 17
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-07)

**Core value:** One runtime, one scorer, one evidence store — and the runtime, not the model, decides what reaches the learner.
**Current focus:** Phase 02 — Daemon Consolidation & Settings Foundation

## Current Position

Phase: 02 (Daemon Consolidation & Settings Foundation) — EXECUTING
Plan: 6 of 6
Status: Phase complete — ready for verification
Last activity: 2026-08-07 — Phase 02 execution started

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**

- Total plans completed: 11
- Average duration: - min
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 11 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 01 P01 | 15min | 3 tasks | 5 files |
| Phase 01 P02 | 18min | 3 tasks | 8 files |
| Phase 01 P03 | 20min | 2 tasks | 5 files |
| Phase 01 P04 | 18min | 3 tasks | 6 files |
| Phase 01 P05 | 25min | 3 tasks | 9 files |
| Phase 01 P06 | 35min | 3 tasks | 6 files |
| Phase 01 P07 | 40min | 3 tasks | 9 files |
| Phase 01 P08 | 21min | 3 tasks | 6 files |
| Phase 01 P09 | 12min | 3 tasks | 7 files |
| Phase 01 P10 | ~21min | 3 tasks | 9 files |
| Phase 01 P11 | ~30min | 3 tasks | 10 files |
| Phase 02 P01 | 55min | 2 tasks | 5 files |
| Phase 02 P02 | 26min | 2 tasks | 8 files |
| Phase 02 P03 | 65min | 3 tasks | 6 files |
| Phase 02 P04 | 16min | 2 tasks | 4 files |
| Phase 02 P05 | 16min | 2 tasks | 2 files |
| Phase 02 P06 | 25min | 2 tasks | 3 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Evidence spine (Phase 1) and daemon/settings/lesson/surfaces/check foundations (Phases 2-5) run as parallel-eligible tracks per `Depends on: Nothing`; the teaching loop, selection, model adapter, subject-loop integration, retention/trends, and the auditor form the dependent chain (Phases 6-11); packaging closes the milestone (Phase 12).
- [Roadmap]: Three phases carry unresolved design questions flagged for their own research at plan time — Phase 1 (item identity scheme, Windows event-log durability), Phase 8 (tier-gate enforcement mechanism, no prior art), Phase 11 (second quality gate algorithm, syllabus input formats, auditor reversibility mechanism).
- [Roadmap]: The auditor (Phase 11) is deliberately last among new subsystems; its pitfall guard rails (citation-per-claim, second quality gate, one-item-per-commit reversibility, graduated autonomy) are written as phase acceptance criteria, not follow-on hardening.
- [Phase ?]: 01-01: evidence.py built as a peer module to runtime.py, never imported by model.py; advisory-locked single-write()-per-event append confirmed durable on this Windows machine via a real-OS-process spike that also reproduced the unlocked-O_APPEND corruption bpo-42606 predicts
- [Phase ?]: 01-02: Task 1 checkpoint resolved as option-a — response_time_ms and confidence captured with real values (served_ts, --confidence flag); error_category and hint_tier recorded as explicit null with the reason stated in code, since no error taxonomy or hint ladder exists before Phase 6/8
- [Phase ?]: 01-02: evidence.py's response_event()/append_event()/events()/attempt_number()/objective_history() built as the first real writer and reader over the evidence log; surfaces/session.py is the first caller, and model.py additively parses [ID:]/[HASH:] into item_id/content_hash (empty until plan 01-04 assigns them)
- [Phase ?]: 01-03: LINT_CODES built from sorted(set(...)) rather than a hand-ordered tuple, so sortedness/no-duplicates is structural rather than maintained by eye
- [Phase ?]: 01-04: content_fingerprint() hashes only tested-content fields (never rationale); assign_ids() is a pure text transform, cmd_id_assign is the only bank writer, checking D-05 cross-bank id-uniqueness in a read-only first pass before any write
- [Phase ?]: 01-05: SESSION_UPGRADES registry + upgrade_session() closes CONCERNS.md's version-evolution gap; response.schema.json's required array follows the live 23-key response_event() (not the plan's stated 22), matching the same discrepancy 01-02 already resolved
- [Phase ?]: 01-06: schema_validate.py implements exactly the SUPPORTED keyword subset schemas/*.json use; check_schema() raises SchemaError on any keyword outside SUPPORTED/ANNOTATIONS before any instance is examined, so a green validation always means the whole document was checked
- [Phase ?]: 01-06: itembank schema --all is PROTO-05's delivery mechanism -- one sort_keys JSON object carrying model.SPEC, all five schemas/*.json documents in sorted order, and the exact command sequence to run a session, mirroring cmd_spec's no-processing precedent
- [Phase ?]: 01-07: response_event()'s canonical field now stores idempotency_canon()'s output (never null) instead of runtime.canonical_response()'s raw output, so a short item's canonical value matches what dedupe_key is built from -- schemas/response.schema.json updated in the same commit
- [Phase ?]: 01-07: D-10 implemented as a read-side filter -- live_events(log) is the only function views (attempt_number, objective_history) may use for counting; retracted_ids(log) collects over the whole log before anything is emitted, so a retraction physically preceding its target still suppresses it; events(log) stays the raw reader for audit
- [Phase ?]: 01-08: objective_history() is the ONE call site that invokes ensure_index(); cmd_evidence deliberately does not duplicate the call, inferring used/fallback status afterward via a read-only index_stale() check so a regression skipping ensure_index() stays observable rather than being masked by a redundant refresh
- [Phase ?]: 01-08: prefix objective matching implemented as two escaped LIKE clauses (x.% / x:%), never a bare LIKE 'x%', so emt:airway can never also match emt:airwaymanagement
- [Phase ?]: 01-08: index_stale() catches an unopenable/corrupted index internally and treats it as a full-rebuild trigger rather than letting the exception escape -- fixed while confirming test_index_is_disposable goes red per the plan's own acceptance criteria
- [Phase ?]: [Phase 1] 01-09: session_events()/marks_by_event() read exclusively through live_events(), extending D-10's read-side-filter discipline to renders -- a retracted response or a retracted mark vanishes from a view exactly as it vanishes from a count
- [Phase ?]: [Phase 1] 01-09: render_attempt_md/render_session_json take only (log, session_id, qs, bank_path), never the session JSON file itself -- the session file cannot be an input to its own render (D-11), so neither render can claim a sitting is finished, only report what the log itself proves happened
- [Phase ?]: [Phase 1] 01-09: mark_event() rejects any marker other than 'human' (T-1-24); a model verdict is not accepted evidence until Phase 8/TEACH-09 teaches the runtime to hold one as pending review
- [Phase ?]: [Phase 1] 01-09: fixed _tail_dedupe_keys() to track the dedupe key of any event carrying one (response or mark), not just event_type=='response' -- found while confirming a replayed mark batch reports already_recorded per D-12
- [Phase ?]: [Phase 1] 01-09: cmd_mark validates and resolves every batch entry before appending any of them, so an unresolved item_ref anywhere in the batch appends nothing at all, not a partial prefix
- [Phase ?]: 01-10: the day surface's evidence directory is derived from daily_log.md's own resolved location (--log override), not the plan file's directory, so evidence lives beside wherever the tick history itself lives
- [Phase ?]: 01-10: tests/serve_roundtrip.py's attempt-file assertions updated to match render_attempt_md()'s established 01-09 vocabulary (MARK: pending, no finished claim) and the evidence log's append-only attempt semantics (re-answering opens a new live attempt rather than overwriting)
- [Phase ?]: 01-10: cmd_serve prints session_id in its startup banner so a marker can pass it to itembank mark / itembank render attempt after the sitting ends
- [Phase ?]: 01-11: source_key(kind, basename, ref) becomes a migrated response event's dedupe_key, deliberately separate from the live path's session+item+attempt+canonical scheme (D-17), so two unrelated unresolved legacy records can never collide into one event
- [Phase ?]: 01-11: mark and day_tick events reuse mark_event()/day_tick_event()'s own already-idempotent dedupe keys during migration rather than a source_key override -- a day_tick imported by migration and one recorded live via itembank day since 01-10 naturally reconcile
- [Phase ?]: 01-11: no resolution by default (D-14) -- item_id is empty and item_ref carries the original positional reference unless --resolve-by-position is explicitly given, which records source_ref.resolution on every event it touches; no similarity-matching path exists
- [Phase ?]: [Phase 2] 02-01: surfaces/daemon.py's cmd_daemon opens one session (session_id/log/attempt-file) per bank at startup, stored on DaemonHandler.sessions[stem]; isolation between banks sharing one evidence log is by the event's bank field, matching the existing evidence design, not by a separate log file per bank
- [Phase ?]: [Phase 2] 02-01: quiz.record_answer() factored out of cmd_serve's record() closure so the CLI serve path and the new daemon path score through runtime.score_response() and write through evidence.append_event() via exactly the same function (D-08 continued)
- [Phase ?]: [Phase 2] 02-01: scan_dir() sorts candidates by (stem.lower(), full_path) rather than stem alone, so a stem-collision winner is deterministic across restarts even where directory-enumeration order is not guaranteed stable
- [Phase ?]: 02-02: day_state()/day_render()/apply_day_post() take an explicit iso threaded through serve_scoped's day_extra rather than computing 'today' internally, so itembank day --date backfilling still works once day became a daemon launch
- [Phase ?]: 02-02: handle_quiz_answer reads reveal/progress off the bank's session dict (default off) rather than at the route-table level, so a general itembank daemon launch is unaffected while itembank serve's scoped launch keeps --reveal and its progress line
- [Phase ?]: 02-03: Task 1 checkpoint resolved as option-a -- itembank config mirrors itembank schema exactly (no-args table, config schema verbatim, config set validate-then-write); SETTINGS_CODES built as a sorted dotted tuple following the LINT_CODES precedent
- [Phase ?]: 02-03: added required arrays to the nested daemon/selection_weights/model_backend object schemas so settings.missing_key has a reachable input path via config set, rather than a published code nothing can trigger
- [Phase ?]: 02-04: do_submit(session_file, answer, confidence) calls normalize_answer(answer) itself, so the same function serves a raw CLI string and an already-JSON-native /api/submit value without a second call site
- [Phase ?]: 02-04: every /api/* handler wraps its session.do_* call in except SystemExit (400) then except Exception (500), in that order -- SystemExit derives from BaseException so the existing except-Exception-only pattern would not catch it and would kill the daemon
- [Phase ?]: 02-04: session_index(root) rebuilds from _attempts/ on every API request rather than caching at startup, so a concurrently created session is addressable immediately; a client-supplied session/bank_path/out field is refused with 400 rather than accepted
- [Phase ?]: 02-05: handle_report_get calls session.do_report for the summary and a direct read_session for cursor/len(items) in the in-progress branch, keeping do_report's own return shape untouched per the plan's files_modified scope
- [Phase ?]: 02-05: the empty-state report branch is decided purely on auto_attempts==0 and pending_manual==0, independent of session status -- the three report states are branches of one template chosen on data, not a flag
- [Phase ?]: 02-05: REPORT_TEMPLATE's data-field="<name>" markers give tests a stable regex hook against every numeric figure instead of scraping prose
- [Phase ?]: 02-06: probe()/start_server() implement D-02's three-case detect-and-attach startup; fixed a Windows-only bug where Daemon's allow_reuse_address=True silently defeated it (SO_REUSEADDR lets a second process bind an already-listening port on Windows, unlike POSIX)
- [Phase ?]: 02-06: cmd_daemon reads daemon.port/daemon.lan from itembank.json via settings.load_settings(), with --port/--lan overriding; --lan has no CLI off-switch, so 'explicitly given' collapses to a.lan is True

### Pending Todos

None yet.

### Blockers/Concerns

- ~~[Phase 1]: Item identity scheme is an open decision~~ — RESOLVED in plan 01-04 (2026-08-06). Chose opaque `[ID:]` plus a `[HASH:]` content fingerprint over content-hash-as-ID. `model.py` gained `content_fingerprint()`/`new_item_id()`/`assign_ids()` and five identity lint checks; `itembank id-assign` is the only writer into a bank.
- [Phase 8]: Tier-gate enforcement (detecting and dropping model output that reaches past the unlocked hint tier) has no prior-art analog found in research; expect original design work, not adapter plumbing.
- [Phase 11]: Auditor autonomy beyond report-only is flagged `⚠️ Revisit` in PROJECT.md's Key Decisions — ship report-only and draft-and-approve fully proven before full audit-draft-lint-fix-commit is wired up.

### Quick Tasks Completed

| ID | Description | Date | Status |
|----|-------------|------|--------|
| 260806-u63 | Fix `iter_raw` crash on a torn multi-byte UTF-8 tail in `evidence.py` (closes Phase 1 verification gap / CR-01) | 2026-08-06 | complete ✓ |

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none — this is the project's first milestone)* | | | |

## Session Continuity

Last session: 2026-08-07T19:08:49.538Z
Stopped at: Completed 02-06-PLAN.md (phase 02 complete)
Resume file: None
