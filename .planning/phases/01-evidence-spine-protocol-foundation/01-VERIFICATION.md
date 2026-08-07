---
phase: 01-evidence-spine-protocol-foundation
verified: 2026-08-06T00:00:00Z
status: passed
score: 6/6 primary truths verified (65+ plan-level must-haves cross-checked; 0 blockers, 4 non-blocking warnings carried forward)
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 5/6 primary truths verified
  gaps_closed:

    - "A process killed mid-append leaves at most one torn trailing line; evidence.iter_raw() skips exactly that line, reports it as `warn evidence.jsonl:<lineno> malformed, skipped`, and returns every line before it intact"
  gaps_remaining: []
  regressions: []
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
**Verified:** 2026-08-06 (initial pass), **re-verified:** 2026-08-06 (after gap closure)
**Status:** human_needed
**Re-verification:** Yes — after gap closure (quick task 260806-u63)

## Re-Verification: Gap Closure Check

The prior pass found exactly one blocking gap: `evidence.iter_raw()` raised an uncaught
`UnicodeDecodeError` (instead of the documented D-09 skip-and-report behavior) when the evidence
log's tail was torn mid multi-byte UTF-8 sequence. Quick task 260806-u63 (commits `1e09df4`,
`fbb87fb`, `4c2ba4b`) claims this is fixed. This pass independently re-verified the fix rather
than trusting the SUMMARY. Two checks were run, both required by the verification brief:

**Check 1 — independently reproduced the torn-tail case against the current tree** (not the
SUMMARY's exact repro, a fresh one built directly against `evidence.iter_raw`):

```
$ python -c "... build a log: one complete JSON line, then a hand-cut multi-byte tail
              (けさ文 encoded to utf-8, cut 2 bytes into the 3-byte 文 character) ...
              list(evidence.iter_raw(path)) ..."
warn  torn.jsonl:2 malformed, skipped
NO CRASH. records=1
(1, {'probe': 'indep', 'marker': 'kept'}, '{"probe": "indep", "marker": "kept"}\n')
```

Confirmed: `iter_raw()` on this tree returns the one complete record, reports the torn line, and
raises nothing. `evidence.py:280` was inspected directly and reads
`with open(path, encoding="utf-8", errors="replace") as fh:` — matching the posture
`_tail_dedupe_keys`/`_index_tail_update` already used, exactly as claimed.

**Check 2 — independently confirmed `probe_torn_multibyte()` would go red on a revert** (a
regression test that passes either way is worthless, so this was not taken on faith from the
SUMMARY's own RED/GREEN transcript): copied `evidence.py` to an isolated scratch location,
reverted only the one keyword (`errors="replace"` → removed) in that copy, loaded it as a
separate module via `importlib`, monkeypatched `itembank.iter_raw` to point at the reverted
function, and ran `tests/durability_roundtrip.py`'s actual `probe_torn_multibyte()` against it
unmodified:

```
FAIL: probe_torn_multibyte: iter_raw raised UnicodeDecodeError on a torn multi-byte tail
('utf-8' codec can't decode bytes in position 0-1: unexpected end of data); D-09 requires a
malformed line to be skipped and reported, never fatal
probe correctly FAILED (went RED) against the reverted (unfixed) iter_raw, SystemExit code: 1
```

Confirmed: the probe is a genuine regression guard, not a test that would pass regardless of the
fix. It was also re-run against the actual current tree (`python tests/durability_roundtrip.py`)
in this pass, independently of the orchestrator's own run, and passed cleanly (torn multi-byte
probe: ok; locked probe: 10000/10000 lines; kill probe: reader survived, post-kill append
readable).

Also confirmed independently:

- `tests/durability_roundtrip.py`'s kill probe (`probe_kill`) now pads with genuine multi-byte
  content via the `PAD_CHARS`/`pad_key` mechanism, with `probe_unlocked`/`probe_locked` correctly
  left on ASCII padding — their `PAD_SHORT`/`PAD_LONG` constants are byte-calibrated against
  512/4096-byte NTFS sector boundaries, and multi-byte padding would silently triple those line
  sizes and invalidate what those two probes measure. This reasoning holds; it is not an
  inconsistency.

- Commits `1e09df4`, `fbb87fb`, `4c2ba4b` exist on this branch with the described diffs
  (`git log`/`git show --stat` against `evidence.py` and `tests/durability_roundtrip.py`).

- Working tree is otherwise clean apart from two pre-existing, unrelated items
  (`.planning/config.json` modified, `_tmp_check.html` untracked) — neither touches evidence
  code and neither is part of this phase's scope.

**Verdict: gap genuinely closed.** Truth #6 below is flipped from ✗ FAILED to ✓ VERIFIED.

## Goal Achievement

### Observable Truths (Roadmap Success Criteria + the one plan-level truth that falsifies EVID-05's crash-safety guarantee)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A learner can edit an item's stem after linting, and evidence history for that item still resolves via the opaque `[ID:]` — identity survives a legitimate content edit | ✓ VERIFIED | `model.py` implements `content_fingerprint`/`new_item_id`/`assign_ids`; `evidence_cli.py:cmd_id_assign` wired (`model.assign_ids(...)` at `surfaces/evidence_cli.py:328`); `tests/evidence_roundtrip.py` reports "identity survives edit, missing/duplicate ids, fingerprint stability, hash states" and the full suite passed on this tree |
| 2 | Migration against `_attempts/*.md`, session JSON, and `daily_log.md` produces one evidence store with no recorded response lost, verified by comparing pre/post counts | ✓ VERIFIED | `surfaces/migrate.py:cmd_migrate` routes every imported record through `evidence.append_event()` (confirmed by grep, not just cited); `tests/evidence_roundtrip.py` reports "migration reconciliation" passing. Non-blocking caveat: WR-01 below |
| 3 | Submitting the same response twice within the same attempt records one accepted response, and the tool states which happened (recorded vs. already-recorded) | ✓ VERIFIED (primary path) | `evidence.py` implements `append_line_checked`/dedupe/`attempt_number`; `tests/evidence_roundtrip.py` reports "duplicate-submit dedupe, retraction" passing. Non-blocking caveat: WR-02 below (two distinct *malformed* structured answers collapse into one dedupe bucket) |
| 4 | A single query answers "how am I doing on objective X over time" across every session and subject, reading from the unified store alone | ✓ VERIFIED | `evidence.py` implements `ensure_index`/`rebuild_index`/`objective_rollup`, falling back to `live_events()` when the index is unavailable (confirmed by grep at `evidence.py:610,676,888`); `tests/evidence_roundtrip.py` reports "objective query, index disposability" passing |
| 5 | An agent with no repository context can read published schema versions, and `lint` emits a machine-readable error code plus offending field alongside human-readable text | ✓ VERIFIED (mechanically) / see human item #1 | `model.LintError`/`LINT_CODES` implemented; CI step pipes live command output through `schema_validate.py` against `schemas/*.json` (`.github/workflows/ci.yml:36-64`); `itembank schema --all` implemented in `surfaces/protocol_cli.py`; `tests/protocol_roundtrip.py` reports "27 lint codes declared, schema versions pinned, ... schema --all self-contained and stable". Whether the output is *sufficient* for a genuinely fresh model to author from is explicitly deferred to human judgment (01-06-PLAN.md's own design) — see Human Verification #1 |
| 6 | (01-01-PLAN.md must-have / phase's own D-09 guarantee) A process killed mid-append leaves at most one torn trailing line; `evidence.iter_raw()` skips exactly that line and returns every line before it intact — never fatal | ✓ VERIFIED (gap closed) | **Fix independently re-verified in this pass** (not taken on the SUMMARY's word): `evidence.py:280` opens with `open(path, encoding="utf-8", errors="replace")`; a fresh, independently-built torn multi-byte repro against the current tree returns the surviving record and reports the torn line instead of raising; `tests/durability_roundtrip.py`'s `probe_torn_multibyte()` was independently confirmed to go RED against a reverted copy of the fix and GREEN against the current tree — see "Re-Verification: Gap Closure Check" above for both transcripts. Originally flagged as CR-01 in `01-REVIEW.md`, closed by quick task 260806-u63 (`1e09df4`/`fbb87fb`/`4c2ba4b`) |

**Score:** 6/6 primary truths verified, 0 failed

### Plan-Level Must-Haves — Artifact & Wiring Verification (all 11 plans)

Unchanged from the initial pass (not affected by this gap or its closure — re-checked only for
regressions, not re-derived from scratch). All artifacts declared across the 11 plans'
`must_haves.artifacts` exist and are substantive (no stubs, no missing-pattern issues):

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
| EVID-05 | 01-01, 01-07 | ✓ SATISFIED (gap closed) | Retraction/idempotency mechanics are sound (dedupe, `already_recorded`, retraction ordering all tested and pass). The "auditable" half — previously blocked by the CR-01 `iter_raw` crash on a torn multi-byte tail — is now closed and independently re-verified (see Truth #6 and "Re-Verification: Gap Closure Check" above): a crash no longer makes the evidence store unreadable after an ordinary kill |
| EVID-06 | 01-11 | ✓ SATISFIED | Migration reconciliation test passes; dry-run-by-default and `--write` gate implemented |
| EVID-07 | 01-02, 01-05, 01-09, 01-10 | ✓ SATISFIED | All 6 fields present on every event; `error_category`/`hint_tier` are documented-null (option-a, confirmed in `schemas/response.schema.json:88-95`) |
| EVID-08 | 01-02, 01-08, 01-10 | ✓ SATISFIED | `mode` field recorded and rolled up per-mode, tested |
| PROTO-01 | 01-02, 01-05 | ✓ SATISFIED | `schema_version` on item/session/response/report/lint payloads, upgrade seam implemented |
| PROTO-02 | 01-03 | ✓ SATISFIED | `LintError`/`LINT_CODES`, `lint --json`, byte-identical `str()` output all tested |
| PROTO-03 | 01-07 | ✓ SATISFIED (primary path) | Idempotent submit, `already_recorded` reporting tested. Non-blocking caveat: WR-02 |
| PROTO-04 | 01-06 | ✓ SATISFIED | CI validates live command output against `schemas/*.json` on every push |
| PROTO-05 | 01-06 | ✓ SATISFIED (mechanically), sufficiency judgment deferred | `itembank schema --all` implemented and tested for self-containment/stability; whether a fresh model can actually author from it is Human Verification #1 |

No orphaned requirements — all 13 IDs listed in the phase's `Requirements:` field (`EVID-01..08`, `PROTO-01..05`) are claimed by at least one plan, and all 13 now appear satisfied mechanically, including EVID-05. `REQUIREMENTS.md` already carries `EVID-05` as `[x]`/`Complete` (Phase 1 row), consistent with this re-verification's finding.

### Anti-Patterns Found

| File | Line(s) | Pattern | Severity | Impact |
|------|---------|---------|----------|--------|
| `evidence.py` | 257-281 (was 280 pre-fix) | `iter_raw()` decoded outside its own try/except, crashing on a torn multi-byte UTF-8 tail | ✅ RESOLVED (was 🛑 Blocker) | Fixed by quick task 260806-u63 (`fbb87fb`): `open(..., errors="replace")`, matching `_tail_dedupe_keys`/`_index_tail_update`'s posture. Independently re-verified in this pass — see "Re-Verification: Gap Closure Check" above. No longer contradicts D-09 or blocks EVID-05 |
| `runtime.py` (canonical_response), `evidence.py` (idempotency_canon) | 91-99, 316-334 | Two distinct malformed structured responses (e.g. two different incomplete `table` answers) both canonicalize to `""` and collapse into one dedupe bucket; the second is silently dropped from the log | ⚠️ Warning (still open) | Narrow edge case (reachable via `itembank submit --answer` with malformed JSON, not via the browser UI where "Check" stays disabled until complete); touches PROTO-03's "the tool says which happened" spirit but not the literal must-have text. Untested by the suite. Out of scope for quick task 260806-u63; not addressed |
| `schemas/session.schema.json`, `surfaces/session.py`, `evidence.py` | schema 59-87, `session.py:106-108`, `evidence.py:1294-1302` | `render_session_json` always adds `review_state` to each response record; `cmd_submit`'s live-written session JSON never does; the schema documents neither | ⚠️ Warning (still open) | Confirmed by grep (no `review_state` in `schemas/session.schema.json` or `surfaces/session.py`). Doesn't fail schema validation (no `additionalProperties: false`) but is a real contract-drift between the two writers of "the same" shape. Out of scope for quick task 260806-u63; not addressed |
| `surfaces/migrate.py`, `evidence.py` | `migrate.py:401-402`, `evidence.py:45-53` | Migration idempotency ("re-run imports 0 new") relies on an 8 MiB dedupe tail window sized for one sitting, not for a migration re-run months later after ordinary studying has grown the log past 8 MiB | ⚠️ Warning (still open) | Re-verified reasoning from 01-REVIEW.md WR-01 against the cited line ranges in the initial pass; not independently re-derived from scratch in this pass. Untested at that scale. Out of scope for quick task 260806-u63; not addressed |
| `surfaces/day.py` | 832 | `date.fromisoformat(a.date)` used unguarded, unlike every other date-shaped input in the codebase | ℹ️ Info (still open) | Crashes with a raw traceback on malformed `--date` instead of the house-style `sys.exit(...)`. Minor, CLI ergonomics only. Out of scope for quick task 260806-u63; not addressed |
| `surfaces/quiz_page.py` | (pre-existing, commit `deb754e`) | `esc()` does not actually escape; output feeds `.innerHTML` at 8 sites (01-REVIEW.md CR-02) | ℹ️ Info (pre-existing, out of scope) | Predates this phase (introduced before Phase 1's own work) and is not a Phase 1 regression. Not part of this phase's `must_haves` or requirements, and not touched by quick task 260806-u63. Flagged here only to keep it visible rather than silently dropped, per this re-verification's explicit instructions — it is not resolved and not this phase's responsibility to resolve |

Also noted (not a gap, not a code anti-pattern): quick task 260806-u63 fixed a pre-existing
subprocess-startup timing race in `tests/durability_roundtrip.py`'s `probe_kill()` (a 0.2s sleep
could lose the race against child interpreter startup, causing an intermittent `FileNotFoundError`
in the test harness itself, unrelated to `iter_raw`). This is a test-harness robustness fix, not a
product-code change, and is the likely explanation for prior reports of "flaky kill probe."

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` debt markers found in any phase-modified file (`evidence.py`, `model.py`, `runtime.py`, `schema_validate.py`, `itembank.py`, `surfaces/*.py`, `tests/durability_roundtrip.py`).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| All modules compile | `python -m py_compile evidence.py model.py runtime.py schema_validate.py itembank.py surfaces/*.py` | Clean (initial pass) | ✓ PASS |
| Full test suite (run once, per constraint; re-run once more in this pass for `durability_roundtrip.py` specifically) | `python tests/*.py` (9 files); `python tests/durability_roundtrip.py` (this pass, standalone) | All 9 report `ok`/`PASS` (orchestrator's run); `durability_roundtrip.py` independently re-run in this pass: torn multi-byte probe ok, locked probe 10000/10000, kill probe survived and post-kill append readable | ✓ PASS |
| `_evidence/` excluded from git | `grep _evidence .gitignore` | `_evidence/` present | ✓ PASS |
| One `append_event` function exists | `grep -n "^def append_event"` across repo | Exactly one, in `evidence.py:386` | ✓ PASS |
| **CR-01 gap closure — independent fresh repro against current tree** | Independently-built torn multi-byte fixture (not the SUMMARY's exact bytes) fed to `evidence.iter_raw()` directly | `warn torn.jsonl:2 malformed, skipped`; 1 record returned; no exception | ✓ PASS (was ✗ FAIL pre-fix) |
| **CR-01 gap closure — independent revert check** | Isolated copy of `evidence.py` with the one-keyword fix manually reverted, loaded via `importlib`, `itembank.iter_raw` monkeypatched to it, then the real unmodified `tests/durability_roundtrip.py:probe_torn_multibyte()` run against it | `FAIL: ... UnicodeDecodeError ...`; `SystemExit` code 1 — probe correctly goes RED | ✓ PASS (confirms the regression probe is a genuine guard, not a test that passes regardless) |
| EVID-07 null-field rationale present in schema | `grep -A4 '"error_category"\|"hint_tier"' schemas/response.schema.json` | Both carry `"type": "null"` and a documented reason | ✓ PASS |
| `review_state` contract drift (WR-03) | `grep review_state schemas/session.schema.json surfaces/session.py` | No output — confirms neither file mentions it | ✗ Confirms warning (non-blocking, still open) |
| Commit trail for the fix | `git log --oneline -- evidence.py tests/durability_roundtrip.py`; `git show --stat <hash>` for each of `1e09df4`/`fbb87fb`/`4c2ba4b` | All three commits present with the described file scope | ✓ PASS |
| Working tree state | `git status --porcelain` | Only `.planning/config.json` (modified) and `_tmp_check.html` (untracked) — both pre-existing and unrelated to evidence code | ✓ PASS |

Full suite executed at most once per file in this pass (durability_roundtrip.py specifically, since it is the file under re-verification); not re-run per must-have.

### Human Verification Required

See frontmatter `human_verification` block. Unchanged from the initial pass — neither item was
part of the closed gap, and neither is silently marked resolved. Two items, both explicitly
flagged by the plans themselves as sufficiency/product judgments rather than code-correctness
questions:

1. Whether `itembank schema --all`'s output is genuinely sufficient for a fresh, repository-less model context to author all six item types (PROTO-05 spirit).
2. Whether `render_session_json`'s documented, honest inability to recover a session's original `seed`/item-selection/`cursor` from the log alone (only ever recoverable from the live session file) is an acceptable approximation for what later phases (selection engine, retention) will build on.

### Gaps Summary

**No gaps remain.** The single confirmed blocker from the initial pass — `evidence.iter_raw()`
crashing with an uncaught `UnicodeDecodeError` on a torn multi-byte UTF-8 tail instead of
skipping-and-reporting per D-09 — was closed by quick task 260806-u63 and independently
re-verified in this pass (not taken on the SUMMARY's word): the fix line was read directly, a
fresh torn-tail repro was built and run against the current tree with no crash, and the
regression probe (`probe_torn_multibyte`) was confirmed to actually go RED against a reverted
copy of the fix, so it is a real guard and not a vacuous test. EVID-05 is now fully satisfied.

Four non-blocking findings from the initial pass (`01-REVIEW.md` WR-01 through WR-04 — migration
idempotency window, malformed-answer dedupe collision, `review_state` schema/writer drift,
unguarded `day --date`) remain open, unchanged, and out of scope for the quick task that closed
the blocker. One pre-existing, out-of-phase finding (`01-REVIEW.md` CR-02, `quiz_page.py`'s
non-escaping `esc()`, from commit `deb754e` before this phase began) also remains open and is
noted here for visibility only — it was never this phase's `must_haves` or requirement, and
remains unaddressed.

Two human-verification items also remain open, unchanged from the initial pass, and are the
reason this phase's overall status is `human_needed` rather than `passed`: a sufficiency judgment
on `schema --all`'s output for a fresh model, and a product judgment on `render_session_json`'s
honest `seed`/selection approximation. Everything else — item identity survival, migration
reconciliation, idempotent submission, the cross-subject objective query, schema versioning/CI
validation, and now crash-safe evidence reads — is verified against the actual codebase, not just
against SUMMARY.md claims.

**Recommendation:** No further action required to close Phase 1's blocking gap. The two
human-verification items above should be resolved by a human before the phases that build on
`schema --all` output or `render_session_json`'s recovery path (selection engine, retention)
proceed too far without that judgment. The four non-blocking warnings and the one pre-existing,
out-of-phase CR-02 finding may be addressed opportunistically or folded into a later phase/plan;
none of them falsify a Phase 1 must-have truth.

---

## Acknowledged Gaps

- item: "01-CONTEXT.md `## Open Questions Flagged for Research / Plan Time` still lists 3 questions from context-gathering (2026-08-06) as unresolved."
  status: acknowledged, resolved-in-later-artifacts
  reason: |
    1. Windows append-write durability — resolved by 01-SPIKE-RESULT.md, measured on the
       target Windows 11 machine, feeding the lock-based mitigation in evidence.append_line.
    2. EVID-07 event field set (names/types/null semantics) — resolved by response.schema.json's
       23-key contract and test_event_schema_fields (01-05-SUMMARY.md).
    3. JSON Schema validation with no stdlib validator — resolved by the hand-rolled
       schema_validate.py subset validator wired into CI (01-06-SUMMARY.md).
  acknowledged_by: user, during /gsd-verify-work 01 artifact scan
  acknowledged_at: 2026-08-07

---

_Verified: 2026-08-06 (initial), re-verified: 2026-08-06 (after gap closure)_
_Verifier: Claude (gsd-verifier)_
