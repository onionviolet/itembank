---
phase: 01-evidence-spine-protocol-foundation
verified: 2026-08-06T00:00:00Z
status: gaps_found
score: 5/6 primary truths verified (65+ plan-level must-haves cross-checked; 1 confirmed blocker, 3 non-blocking warnings)
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "A process killed mid-append leaves at most one torn trailing line; evidence.iter_raw() skips exactly that line, reports it as `warn evidence.jsonl:<lineno> malformed, skipped`, and returns every line before it intact (01-01-PLAN.md must-have; also the phase's own documented D-09 guarantee, and the substance of EVID-05's 'auditable' half)."
    status: failed
    reason: "Reproduced directly against the current tree (not just cited from 01-REVIEW.md). evidence.iter_raw() opens the log with `open(path, encoding=\"utf-8\")` (no `errors=`) and iterates the file handle outside its try/except, which only guards `json.loads`. A log whose tail is torn mid multi-byte UTF-8 sequence (realistic on a process kill while a CJK short-answer, objective, or rationale is mid-write -- the project explicitly targets a Mandarin lane and tests CJK content elsewhere) raises an uncaught UnicodeDecodeError instead of being skipped-and-reported. This is not a single skipped line: it crashes iter_raw() entirely, and every function built on it (events, live_events, retracted_ids, objective_history's fallback, attempt_number, marks_by_event, render_attempt_md, render_session_json, day_log_from_events) -- i.e. `itembank evidence`, `report`, `mark`, `render`, `day`, and `serve`'s own save/read path -- inherits the crash on the next read. tests/durability_roundtrip.py's kill probe only pads lines with ASCII x/y characters, so this exact failure mode was never exercised by the suite that gates this phase."
    artifacts:
      - path: "evidence.py"
        issue: "iter_raw() (lines 257-281): `open(path, encoding=\"utf-8\")` with no `errors=` argument, and the `for lineno, raw in enumerate(fh, 1)` loop that decodes each line sits outside the `try/except (ValueError, TypeError)` that only wraps `json.loads`. The sibling tail-readers in the same file (`_tail_dedupe_keys`, `_index_tail_update`) already defend against this by reading raw bytes and calling `.decode(\"utf-8\", errors=\"replace\")`; `iter_raw` is the one reader that doesn't, and it is the one every other reader is built on."
    missing:
      - "Open the log with `errors=\"replace\"` (matching the posture already used by `_tail_dedupe_keys`/`_index_tail_update`), or read raw bytes and decode defensively before the try/except that reports a malformed line, so a torn multi-byte tail degrades to a reported, skipped line instead of an uncaught exception."
      - "A durability-probe case (or an addition to tests/durability_roundtrip.py's kill probe) that pads with genuine multi-byte UTF-8 content, not just ASCII, so this exact regression is caught by CI going forward."
deferred: []
human_verification:
  - test: "Give a model with no repository access only the pasted output of `itembank schema --all` and ask it to author one item of each of the six types plus a legal recorded response, with no other file or source access."
    expected: "The model succeeds in authoring all six item types and describing a valid response from the schema text alone, with no back-and-forth needed to discover fields the schema omitted."
    why_human: "01-06-PLAN.md's own Task 3 human-check and Flagged Assumptions section mark this explicitly as a sufficiency judgment, not a string match. The automated suite (tests/protocol_roundtrip.py) confirms the output parses, is self-contained, and is byte-stable across runs -- it cannot confirm a genuinely fresh model succeeds at authoring from it alone. 01-06-SUMMARY.md confirms this was carried forward undone, as the plan itself designed."
  - test: "Inspect a session recovered by `render_session_json` after the live session JSON has been deleted or is unavailable, and judge whether reporting `seed: 0` (always) and deriving `items`/`cursor`/`status` from the distinct item_refs the log proves were answered, rather than the session's true original selection, is an acceptable approximation for downstream consumers (day cockpit, resumed sessions, agent tooling)."
    expected: "A human (or product-owner-level) judgment on whether this documented, honest approximation is good enough, or whether the original seed/selection needs to be captured as a first-class logged fact in a follow-up plan."
    why_human: "01-09-PLAN.md and 01-09-SUMMARY.md both document this as a deliberate, honest approximation rather than a bug -- render_session_json has no way to recover the original seed/cursor from the log alone, and says so rather than guessing. Whether that tradeoff is acceptable for the phases that build on it (selection engine, retention) is a product decision, not a code-correctness question."
---

# Phase 1: Evidence Spine & Protocol Foundation Verification Report

**Phase Goal:** Every session the learner sits produces evidence that survives item edits, bank migrations, and repeated submissions, in one auditable store instead of three.
**Verified:** 2026-08-06
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria + the one plan-level truth that falsifies EVID-05's crash-safety guarantee)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A learner can edit an item's stem after linting, and evidence history for that item still resolves via the opaque `[ID:]` — identity survives a legitimate content edit | ✓ VERIFIED | `model.py` implements `content_fingerprint`/`new_item_id`/`assign_ids`; `evidence_cli.py:cmd_id_assign` wired (`model.assign_ids(...)` at `surfaces/evidence_cli.py:328`); `tests/evidence_roundtrip.py` reports "identity survives edit, missing/duplicate ids, fingerprint stability, hash states" and the full suite passed on this tree |
| 2 | Migration against `_attempts/*.md`, session JSON, and `daily_log.md` produces one evidence store with no recorded response lost, verified by comparing pre/post counts | ✓ VERIFIED | `surfaces/migrate.py:cmd_migrate` routes every imported record through `evidence.append_event()` (confirmed by grep, not just cited); `tests/evidence_roundtrip.py` reports "migration reconciliation" passing. Non-blocking caveat: WR-01 below |
| 3 | Submitting the same response twice within the same attempt records one accepted response, and the tool states which happened (recorded vs. already-recorded) | ✓ VERIFIED (primary path) | `evidence.py` implements `append_line_checked`/dedupe/`attempt_number`; `tests/evidence_roundtrip.py` reports "duplicate-submit dedupe, retraction" passing. Non-blocking caveat: WR-02 below (two distinct *malformed* structured answers collapse into one dedupe bucket) |
| 4 | A single query answers "how am I doing on objective X over time" across every session and subject, reading from the unified store alone | ✓ VERIFIED | `evidence.py` implements `ensure_index`/`rebuild_index`/`objective_rollup`, falling back to `live_events()` when the index is unavailable (confirmed by grep at `evidence.py:610,676,888`); `tests/evidence_roundtrip.py` reports "objective query, index disposability" passing |
| 5 | An agent with no repository context can read published schema versions, and `lint` emits a machine-readable error code plus offending field alongside human-readable text | ✓ VERIFIED (mechanically) / see human item #1 | `model.LintError`/`LINT_CODES` implemented; CI step pipes live command output through `schema_validate.py` against `schemas/*.json` (`.github/workflows/ci.yml:36-64`); `itembank schema --all` implemented in `surfaces/protocol_cli.py`; `tests/protocol_roundtrip.py` reports "27 lint codes declared, schema versions pinned, ... schema --all self-contained and stable". Whether the output is *sufficient* for a genuinely fresh model to author from is explicitly deferred to human judgment (01-06-PLAN.md's own design) — see Human Verification #1 |
| 6 | (01-01-PLAN.md must-have / phase's own D-09 guarantee) A process killed mid-append leaves at most one torn trailing line; `evidence.iter_raw()` skips exactly that line and returns every line before it intact — never fatal | ✗ FAILED | **Reproduced directly**: a log torn mid multi-byte UTF-8 sequence raises an uncaught `UnicodeDecodeError` out of `iter_raw()` (`evidence.py:268-269`, `open(path, encoding="utf-8")` with no `errors=`, decode happens outside the try/except). This crashes every reader built on `iter_raw` — `evidence`, `report`, `mark`, `render`, `day`, and `serve`'s save/read path — not just the one torn line. Confirmed pre-existing in 01-REVIEW.md as CR-01 and independently reproduced here with a minimal repro script; `tests/durability_roundtrip.py`'s kill probe never exercises multi-byte content so CI does not catch it |

**Score:** 5/6 primary truths verified, 1 failed (blocker)

### Plan-Level Must-Haves — Artifact & Wiring Verification (all 11 plans)

All artifacts declared across the 11 plans' `must_haves.artifacts` exist and are substantive (no stubs, no missing-pattern issues):

| Plan | Artifacts (exists+substantive) | Key Links (manually re-verified after tool false-negatives) |
|------|-------------------------------|----------------------------------------------------------|
| 01-01 | 3/3 ✓ | 2/2 ✓ (`itembank.append_line/iter_raw` used in `tests/durability_roundtrip.py`; `os.write()` in `evidence.py:143,251`) |
| 01-02 | 4/4 ✓ | 3/3 ✓ (`append_event` in `surfaces/session.py:98`; `objective_history` in `surfaces/evidence_cli.py:69`; `from runtime import` present) |
| 01-03 | 2/2 ✓ | 2/2 ✓ (`str(e)` at `surfaces/cli.py:40`, `surfaces/quiz.py:41,86`) |
| 01-04 | 2/2 ✓ | 2/2 ✓ (`assign_ids(` at `surfaces/evidence_cli.py:328`; `hashlib.sha256` at `model.py:177`) |
| 01-05 | 6/6 ✓ | 2/2 ✓ (`upgrade_session` defined `runtime.py:144`, called `runtime.py:175`) |
| 01-06 | 3/3 ✓ | 2/2 ✓ (`schema_validate.py` referenced 8x in `.github/workflows/ci.yml`) |
| 01-07 | 2/2 ✓ | 2/2 ✓ (`live_events(` used at 8 call sites in `evidence.py`) |
| 01-08 | 2/2 ✓ | 2/2 ✓ (`sqlite3.connect` at `evidence.py:690`; `live_events(` fallback confirmed) |
| 01-09 | 3/3 ✓ | 2/2 ✓ (`session_events(` defined/used `evidence.py:1083,1154,1272`) |
| 01-10 | 3/3 ✓ | 3/3 ✓ (`append_event` in `surfaces/quiz.py:114`; `render_daily_log(` in `surfaces/day.py:928`) |
| 01-11 | 4/4 ✓ | 2/2 ✓ (`append_event` in `surfaces/migrate.py:369`; `load_day_log(` in `surfaces/migrate.py:479`) |

Note: the `gsd_run query verify.key-links` tool reported false negatives on nearly every plan (double-escaped regex patterns from YAML producing "Invalid regex pattern" or "not found" errors even where the pattern trivially matches). Every link above was re-verified manually with direct Grep against the source, which is the evidence recorded in this table — the tool's own output is not relied on.

### Requirements Coverage

| Requirement | Source Plan(s) | Status | Evidence |
|---|---|---|---|
| EVID-01 | 01-04 | ✓ SATISFIED | Opaque `[ID:]` identity, `content_fingerprint`, `assign_ids` implemented and tested |
| EVID-02 | 01-04 | ✓ SATISFIED | `item.duplicate_id`/`item.missing_id`/`item.missing_hash` lint codes implemented |
| EVID-03 | 01-02, 01-09, 01-10 | ✓ SATISFIED | Attempt md, session JSON, and daily_log.md are all renders of the log (`render_attempt_md`, `render_session_json`, `render_daily_log`) |
| EVID-04 | 01-02, 01-08 | ✓ SATISFIED | `objective_history`/`objective_rollup` read the unified store, index-optional |
| EVID-05 | 01-01, 01-07 | ✗ BLOCKED | Retraction/idempotency mechanics are sound (dedupe, `already_recorded`, retraction ordering all tested and pass), but the "auditable" half of this requirement is broken by the CR-01 crash — see Truth #6 above. Evidence is not silently overwritten, but it can become **entirely unreadable** after an ordinary crash, which is the opposite of auditable |
| EVID-06 | 01-11 | ✓ SATISFIED | Migration reconciliation test passes; dry-run-by-default and `--write` gate implemented |
| EVID-07 | 01-02, 01-05, 01-09, 01-10 | ✓ SATISFIED | All 6 fields present on every event; `error_category`/`hint_tier` are documented-null (option-a, confirmed in `schemas/response.schema.json:88-95`) |
| EVID-08 | 01-02, 01-08, 01-10 | ✓ SATISFIED | `mode` field recorded and rolled up per-mode, tested |
| PROTO-01 | 01-02, 01-05 | ✓ SATISFIED | `schema_version` on item/session/response/report/lint payloads, upgrade seam implemented |
| PROTO-02 | 01-03 | ✓ SATISFIED | `LintError`/`LINT_CODES`, `lint --json`, byte-identical `str()` output all tested |
| PROTO-03 | 01-07 | ✓ SATISFIED (primary path) | Idempotent submit, `already_recorded` reporting tested. Non-blocking caveat: WR-02 |
| PROTO-04 | 01-06 | ✓ SATISFIED | CI validates live command output against `schemas/*.json` on every push |
| PROTO-05 | 01-06 | ✓ SATISFIED (mechanically), sufficiency judgment deferred | `itembank schema --all` implemented and tested for self-containment/stability; whether a fresh model can actually author from it is Human Verification #1 |

No orphaned requirements — all 13 IDs listed in the phase's `Requirements:` field (`EVID-01..08`, `PROTO-01..05`) are claimed by at least one plan, and all 13 appear satisfied mechanically except EVID-05.

### Anti-Patterns Found

| File | Line(s) | Pattern | Severity | Impact |
|------|---------|---------|----------|--------|
| `evidence.py` | 257-281 | `iter_raw()` decodes outside its own try/except, crashing on a torn multi-byte UTF-8 tail | 🛑 Blocker | Contradicts the module's documented D-09 "never fatal" guarantee; breaks EVID-05's auditability under a realistic crash. See Truth #6/gap above. Reproduced independently in this verification, not just cited from 01-REVIEW.md |
| `runtime.py` (canonical_response), `evidence.py` (idempotency_canon) | 91-99, 316-334 | Two distinct malformed structured responses (e.g. two different incomplete `table` answers) both canonicalize to `""` and collapse into one dedupe bucket; the second is silently dropped from the log | ⚠️ Warning | Narrow edge case (reachable via `itembank submit --answer` with malformed JSON, not via the browser UI where "Check" stays disabled until complete); touches PROTO-03's "the tool says which happened" spirit but not the literal must-have text. Untested by the suite (confirmed by grep — no test constructs two distinct malformed answers) |
| `schemas/session.schema.json`, `surfaces/session.py`, `evidence.py` | schema 59-87, `session.py:106-108`, `evidence.py:1294-1302` | `render_session_json` always adds `review_state` to each response record; `cmd_submit`'s live-written session JSON never does; the schema documents neither | ⚠️ Warning | Confirmed by grep (no `review_state` in `schemas/session.schema.json` or `surfaces/session.py`). Doesn't fail schema validation (no `additionalProperties: false`) but is a real contract-drift between the two writers of "the same" shape |
| `surfaces/migrate.py`, `evidence.py` | `migrate.py:401-402`, `evidence.py:45-53` | Migration idempotency ("re-run imports 0 new") relies on an 8 MiB dedupe tail window sized for one sitting, not for a migration re-run months later after ordinary studying has grown the log past 8 MiB | ⚠️ Warning | Re-verified reasoning from 01-REVIEW.md WR-01 against the cited line ranges; not independently re-derived from scratch. Untested at that scale (fixtures are far below 8 MiB) |
| `surfaces/day.py` | 832 | `date.fromisoformat(a.date)` used unguarded, unlike every other date-shaped input in the codebase | ℹ️ Info | Crashes with a raw traceback on malformed `--date` instead of the house-style `sys.exit(...)`. Minor, CLI ergonomics only |

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` debt markers found in any phase-modified file (`evidence.py`, `model.py`, `runtime.py`, `schema_validate.py`, `itembank.py`, `surfaces/*.py`).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| All modules compile | `python -m py_compile evidence.py model.py runtime.py schema_validate.py itembank.py surfaces/*.py` | Clean | ✓ PASS |
| Full test suite (run once, per constraint) | `python tests/*.py` (9 files) | All 9 report `ok`/`PASS`, including `durability_roundtrip.py`'s kill probe (345/345 records) | ✓ PASS |
| `_evidence/` excluded from git | `grep _evidence .gitignore` | `_evidence/` present | ✓ PASS |
| One `append_event` function exists | `grep -n "^def append_event"` across repo | Exactly one, in `evidence.py:386` | ✓ PASS |
| CR-01 reproduction: `iter_raw()` on a log torn mid multi-byte UTF-8 sequence | Custom repro script (see gap detail) | `UnicodeDecodeError` raised uncaught, propagates out of `iter_raw()` | ✗ FAIL (confirms the gap) |
| EVID-07 null-field rationale present in schema | `grep -A4 '"error_category"\|"hint_tier"' schemas/response.schema.json` | Both carry `"type": "null"` and a documented reason | ✓ PASS |
| `review_state` contract drift (WR-03) | `grep review_state schemas/session.schema.json surfaces/session.py` | No output — confirms neither file mentions it | ✗ Confirms warning (non-blocking) |

Full suite executed exactly once, per the verification protocol's single-run constraint. Not re-run per must-have.

### Human Verification Required

See frontmatter `human_verification` block. Two items, both explicitly flagged by the plans themselves as sufficiency/product judgments rather than code-correctness questions:

1. Whether `itembank schema --all`'s output is genuinely sufficient for a fresh, repository-less model context to author all six item types (PROTO-05 spirit).
2. Whether `render_session_json`'s documented, honest inability to recover a session's original `seed`/item-selection/`cursor` from the log alone (only ever recoverable from the live session file) is an acceptable approximation for what later phases (selection engine, retention) will build on.

### Gaps Summary

One confirmed blocker: `evidence.iter_raw()` — the read primitive every evidence consumer in the codebase is built on — crashes with an uncaught `UnicodeDecodeError` instead of skipping-and-reporting when a process is killed mid-append on a line containing multi-byte UTF-8 content (any CJK text, explicitly relevant given the project's Mandarin study lane and its own CJK test fixtures). This was flagged as CR-01 in the phase's own code review (`01-REVIEW.md`) and is independently reproduced here against the current tree with a minimal, self-contained repro. It directly falsifies a must-have truth stated in `01-01-PLAN.md` ("returns every line before it intact... never fatal") and the module's own documented D-09 guarantee, and it is the mechanism behind the "auditable" half of EVID-05 — a crash does not lose data on disk, but it can make the *entire* evidence store unreadable through every surface (`evidence`, `report`, `mark`, `render`, `day`, `serve`) until manually repaired. `tests/durability_roundtrip.py`'s kill probe pads only with ASCII, so this exact regression was never caught by the suite that gates this phase, despite the suite otherwise passing cleanly and thoroughly exercising the crash-kill, dedupe, retraction, and migration paths.

Three non-blocking warnings (WR-02, WR-03, WR-04 from `01-REVIEW.md`, independently re-confirmed by grep against the cited files/lines) round out the picture but do not, on their own, falsify a stated must-have truth — they are narrower edge cases (malformed-answer dedupe collision, a schema/writer contract-drift on `review_state`, and an unguarded `--date` CLI flag).

Everything else — item identity survival, migration reconciliation, idempotent submission on the primary (valid-answer) path, the cross-subject objective query, schema versioning/CI validation, and the full 92-test-name suite spanning every plan's documented behaviors — is verified against the actual codebase, not just against SUMMARY.md claims.

**Recommendation:** Apply the CR-01 fix (`errors="replace"` on `iter_raw`'s `open()` call, matching the pattern already used elsewhere in the same file by `_tail_dedupe_keys`/`_index_tail_update`) before this phase is considered closed — it is a small, well-scoped fix directly contradicting the phase's own explicit guarantee, not a design question requiring a new plan.

---

_Verified: 2026-08-06_
_Verifier: Claude (gsd-verifier)_
