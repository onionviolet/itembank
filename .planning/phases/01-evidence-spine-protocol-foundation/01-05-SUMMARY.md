---
phase: 01-evidence-spine-protocol-foundation
plan: 05
subsystem: infra
tags: [json-schema, protocol, schema-versioning, session-migration, evid-07]

# Dependency graph
requires:
  - phase: 01-02
    provides: "evidence.py's response_event()/append_event() as the 23-field response event this plan's response.schema.json describes, and the EVID-07 capture policy (option-a) whose reasons go into the schema's field descriptions"
  - phase: 01-03
    provides: "model.py's LintError namedtuple and LINT_CODES (27 codes) as the shape and code enum lint_error.schema.json describes"
  - phase: 01-04
    provides: "the five identity/hash lint codes item.missing_id/item.duplicate_id/item.missing_hash/item.content_drift/item.objective_unnamespaced folded into LINT_CODES, which lint_error.schema.json's code enum now includes"
provides:
  - "runtime.py: ITEM_VERSION, REPORT_VERSION beside SESSION_VERSION; public_item() and session_summary() stamp their own schema_version"
  - "runtime.py: SESSION_UPGRADES registry and upgrade_session() -- a session whose schema_version has no registered upgrade path, or is newer than this build understands, exits with a distinct named error instead of a bare equality check; closes the CONCERNS.md gap"
  - "surfaces/session.py: cmd_report's top-level payload also stamps schema_version: REPORT_VERSION"
  - "schemas/item.schema.json, session.schema.json, response.schema.json, report.schema.json, lint_error.schema.json -- five self-contained JSON Schema documents, each carrying x-itembank-version and staying inside a fixed keyword subset (no patternProperties/allOf/if-then-else) for plan 01-06's validator"
  - "tests/protocol_roundtrip.py: test_schema_versions_present, test_schema_version_required, test_event_schema_fields -- ties every version-stamped payload to its published document and asserts the EVID-07 null policy against a real recorded event, not just its description"
affects: [01-06, 01-07, 01-08, 01-09, 01-10, 01-11]

actuals:
  tokens: 10125
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Version constants live beside the payload builder they stamp (ITEM_VERSION next to public_item, REPORT_VERSION next to session_summary/cmd_report, SESSION_VERSION next to read_session/upgrade_session), so a future bump touches one constant and one schema document rather than a search across the codebase"
    - "SESSION_UPGRADES is a registry (int source version -> one-step upgrade function) rather than a growing if/elif chain in read_session; upgrade_session() walks it forward one step at a time and exits by name on a missing step or a version from the future -- the concrete migration seam CONCERNS.md flagged as absent"
    - "Every schemas/*.json document stays inside a fixed 17-keyword subset (no patternProperties, allOf, if/then/else, default, examples) so plan 01-06's validator can implement exactly that subset and fail loud on anything outside it, rather than silently ignoring an unsupported keyword"
    - "response.schema.json's $defs carries unenforced placeholder shapes (mark_event, retraction_event, day_tick_event) for the three non-response event_type values plans 01-07/01-09 will give bodies to, without those plans having to invent the document from scratch"

key-files:
  created:
    - schemas/item.schema.json
    - schemas/session.schema.json
    - schemas/response.schema.json
    - schemas/report.schema.json
    - schemas/lint_error.schema.json
  modified:
    - runtime.py
    - surfaces/session.py
    - itembank.py
    - tests/protocol_roundtrip.py

key-decisions:
  - "response.schema.json's required array lists the 23 keys evidence.response_event() actually emits (including 'bank'), not the 22 the plan's own must_haves/action text counted. This is the identical discrepancy 01-02-SUMMARY.md already resolved for the event builder itself; the schema now matches the live code rather than reproducing the plan's stale count."
  - "response.schema.json documents event_type as a 4-value enum (response/mark/retraction/day_tick) with $defs placeholders for the three not-yet-written types, but the top-level required/additionalProperties:false pairing enforces only the response shape this build actually writes -- the placeholders are unenforced scaffolding for 01-07/01-09, not a live oneOf branch."
  - "lint_error.schema.json's x-itembank-version is tied to the literal 1 surfaces/cli.py:cmd_lint hardcodes for its JSON envelope, since no exported LINT_SCHEMA_VERSION constant exists in code; test_schema_versions_present asserts against that literal rather than inventing a constant the plan never asked for."

requirements-completed: [PROTO-01, EVID-07]

coverage:
  - id: D1
    description: "Every item, session, response and report payload carries an explicit schema_version integer; a payload with no schema_version is rejected with a named error rather than silently accepted"
    requirement: PROTO-01
    verification:
      - kind: unit
        ref: "tests/protocol_roundtrip.py#test_schema_versions_present"
        status: pass
      - kind: unit
        ref: "tests/protocol_roundtrip.py#test_schema_version_required"
        status: pass
    human_judgment: false
  - id: D2
    description: "A session file whose schema_version is older than SESSION_VERSION is upgraded forward through a registered SESSION_UPGRADES function; one whose version is newer exits by name; a non-integer schema_version also exits by name"
    requirement: PROTO-01
    verification:
      - kind: unit
        ref: "Task 1 acceptance commands: schema_version 99 exits with 'newer than this build understands'; schema_version 0 exits with 'no upgrade path'"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every response event carries all six EVID-07 fields (response_time_ms, confidence, error_category, hint_tier, mode, review_state), with error_category and hint_tier explicitly null and the reason for each null published in schemas/response.schema.json's field descriptions"
    requirement: EVID-07
    verification:
      - kind: unit
        ref: "tests/protocol_roundtrip.py#test_event_schema_fields"
        status: pass
    human_judgment: false
  - id: D4
    description: "Five self-contained JSON Schema documents under schemas/ describe the whole agent-facing contract, each stamped with x-itembank-version:1 and staying inside the fixed keyword subset plan 01-06's validator will enforce"
    verification:
      - kind: unit
        ref: "Task 2 verify script: keyword-subset walk over all five documents; python itembank.py guard . exits 0"
        status: pass
    human_judgment: false
  - id: D5
    description: "A shape change to any schemas/*.json document is accompanied by a bump of its x-itembank-version value"
    verification: []
    human_judgment: true
    rationale: "The plan's own must_haves marks this truth's verification as 'backstop': there is no committed baseline of the schema documents to diff a shape change against within this phase (this is the phase that first creates them), so the check cannot be mechanically confirmed on first release. A future plan that edits a schemas/*.json file without bumping its x-itembank-version is what a human reviewer or a later phase's regression test would catch."

duration: ~25min
completed: 2026-08-06
status: complete
---

# Phase 1 Plan 5: Publish the Contract Summary

**Five JSON Schema documents under `schemas/` describe the whole agent-facing protocol (item, session, response, report, lint entry), every runtime payload now stamps `schema_version`, and a session from an older build upgrades forward through a registered `SESSION_UPGRADES` seam instead of the bare version-equality check `.planning/codebase/CONCERNS.md` flagged as missing.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-06 (continuation from 01-04)
- **Completed:** 2026-08-06
- **Tasks:** 3
- **Files modified:** 9 (5 created, 4 modified)

## Accomplishments

- `runtime.py` gains `ITEM_VERSION = 1` and `REPORT_VERSION = 1` beside the
  existing `SESSION_VERSION = 1`. `public_item()` and `session_summary()`
  each stamp their own `schema_version` as their first key;
  `surfaces/session.py`'s `cmd_report` stamps its top-level payload with
  `REPORT_VERSION` too.
- `runtime.py` gains `SESSION_UPGRADES = {}` (empty today -- version 1 is
  the only version that has ever existed) and `upgrade_session(data)`,
  which `read_session` now calls in place of its old bare equality check.
  A non-integer `schema_version` exits by name; a version below
  `SESSION_VERSION` with no registered `SESSION_UPGRADES` entry exits
  `"no upgrade path from session schema %d to %d"`; a version above
  `SESSION_VERSION` exits `"session schema %d is newer than this build
  understands (%d); upgrade itembank"`. This is the concrete migration seam
  `CONCERNS.md`'s "JSON session file format has no version evolution
  strategy" finding asked for.
- `ITEM_VERSION`, `REPORT_VERSION`, `SESSION_UPGRADES` and
  `upgrade_session` are exported from `itembank.py`, alphabetized into the
  existing `from runtime import (...)` block and `__all__`.
- Five schema documents land under `schemas/`: `item.schema.json` (the
  `public_item()` shape, `oneOf` over four per-type variants, explicit that
  it never carries a key/rationale/model answer), `session.schema.json`
  (the resumable session file), `response.schema.json` (the 23-key
  evidence event, `additionalProperties: false`, every EVID-07 field's
  Phase 1 disposition and reason written into its own `description`),
  `report.schema.json` (`oneOf` between the session summary and the
  objective history), and `lint_error.schema.json` (the 27-code `enum`
  matching `LINT_CODES` exactly). Every document stays inside a fixed
  17-keyword subset so plan 01-06's validator can implement exactly that
  subset.
- `tests/protocol_roundtrip.py` gains three tests: `test_schema_versions_present`
  drives a real session end to end (start/submit/report) and checks every
  stamped payload's `schema_version` against its constant and every
  schema document's `x-itembank-version` against the constant it
  describes; `test_schema_version_required` confirms an unstamped session
  is rejected by name and that every document requires `schema_version`;
  `test_event_schema_fields` drives a full six-item session (one of every
  item type) to completion and asserts each raw log line's key set equals
  `response.schema.json`'s `required` array exactly, plus the documented
  field dispositions (`response_time_ms` non-negative int, `confidence`
  echoed back, `mode` matched, `error_category`/`hint_tier` exactly
  `None`, `review_state` `"n/a"` for auto-scored items and `"pending"` for
  the short item).
- Both drift-detection tests were manually confirmed to go red: a
  throwaway key added to `evidence.response_event()` broke
  `test_event_schema_fields`, and bumping `ITEM_VERSION` without bumping
  `item.schema.json`'s `x-itembank-version` broke `test_schema_versions_present`.
  Both changes were reverted before the Task 3 commit.

## Task Commits

Each task was committed atomically:

1. **Task 1: Stamp a schema version on every payload and give the session a forward upgrade path** - `53bc97e` (feat)
2. **Task 2: Write the five published schema documents under schemas/** - `deaa707` (docs)
3. **Task 3: Pin the version stamps and the EVID-07 field set in tests/protocol_roundtrip.py** - `01f3f22` (test)

_Note: no TDD red/green/refactor split was called for; all three tasks are `type="auto"`._

## Files Created/Modified

- `runtime.py` - `ITEM_VERSION`, `REPORT_VERSION` constants; `public_item()`/`session_summary()` stamp `schema_version`; `SESSION_UPGRADES` registry and `upgrade_session()`; `read_session` calls `upgrade_session` instead of a bare equality check
- `surfaces/session.py` - `REPORT_VERSION` imported; `cmd_report`'s top-level JSON payload stamps `schema_version`
- `itembank.py` - `ITEM_VERSION`, `REPORT_VERSION`, `SESSION_UPGRADES`, `upgrade_session` added to the `from runtime import (...)` block and `__all__`, alphabetized
- `schemas/item.schema.json` (new) - the `public_item()` contract, `oneOf` over mc/multi, table/dnd, build and short variants
- `schemas/session.schema.json` (new) - the resumable session file contract
- `schemas/response.schema.json` (new) - the 23-key evidence event contract, `additionalProperties: false`, EVID-07 null-policy field descriptions
- `schemas/report.schema.json` (new) - `oneOf` between the session summary and the objective history
- `schemas/lint_error.schema.json` (new) - the lint entry contract, 27-code `enum` matching `LINT_CODES`
- `tests/protocol_roundtrip.py` - `run()`/`correct_answer()`/`load_schema()` helpers; `test_schema_versions_present`, `test_schema_version_required`, `test_event_schema_fields`

## Decisions Made

- **`response.schema.json`'s `required` array lists the live 23-key set
  `evidence.response_event()` emits, not the plan's own "22 keys"
  count.** Identical to the discrepancy `01-02-SUMMARY.md` already
  resolved for the event builder itself (`must_haves` names 22 keys, the
  plan's own field list and threat model T-1-06 require a 23rd, `bank`).
  The schema is written to match what the code actually emits and what
  `test_event_schema_fields` verifies against a live event, rather than
  reproducing the plan's stale count a second time.
- **`event_type`'s `mark`/`retraction`/`day_tick` variants are documented
  but not enforced.** `response.schema.json`'s top-level
  `additionalProperties: false` + `required` pairing describes only the
  `response` event this build writes; the three future event types get
  unenforced `$defs` placeholders (`mark_event`, `retraction_event`,
  `day_tick_event`) so plans 01-07 and 01-09 have a named slot to fill in
  rather than a blank page, without this plan inventing shapes for events
  that don't exist yet.
- **`lint_error.schema.json`'s `x-itembank-version` is tied to the literal
  `1` `surfaces/cli.py:cmd_lint` hardcodes for its JSON envelope.** No
  exported lint-schema version constant exists in code (unlike
  `ITEM_VERSION`/`SESSION_VERSION`/`REPORT_VERSION`/`EVENT_SCHEMA_VERSION`),
  so `test_schema_versions_present` asserts against that literal directly
  rather than adding a constant the plan never asked for.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `response.schema.json`'s required-key count follows the live 23-key event, not the plan's stated 22**
- **Found during:** Task 2, reading `evidence.response_event()` to write the schema
- **Issue:** The plan's Task 2 `<action>` and Task 3 `<action>` both say "22 keys" for the response event's required list, but `evidence.response_event()` (built in 01-02, with `bank` as a required 23rd field per that plan's own field list and threat model T-1-06) has emitted 23 keys since 01-02 landed. This is the same plan-internal inconsistency 01-02-SUMMARY.md already documented and resolved once.
- **Fix:** `response.schema.json`'s `required` array lists all 23 live keys; `test_event_schema_fields` asserts the raw event's key set equals that array exactly (verified against a real event produced by driving the CLI, not a hand-typed list).
- **Files modified:** `schemas/response.schema.json`, `tests/protocol_roundtrip.py`
- **Verification:** `test_schema_versions_present` and `test_event_schema_fields` both pass; a manual throwaway-key injection into `evidence.response_event()` was confirmed to break `test_event_schema_fields` before being reverted.
- **Committed in:** `deaa707` (Task 2 commit), `01f3f22` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 plan-inconsistency bugfix, matching a pattern already established in 01-02)
**Impact on plan:** Keeps the published contract aligned with the live code and with what 01-02 already decided about this exact field count. No scope creep.

## Issues Encountered

- **`tests/durability_roundtrip.py`'s kill-probe failed once during a full-suite run** with the same pre-existing `FileNotFoundError` on its temp `kill.jsonl` noted in every prior plan's summary in this phase. Confirmed out of scope: re-running the file in isolation three times (once after each task) passed cleanly every time, and this plan touches neither `evidence.py`'s kill-probe path nor `tests/durability_roundtrip.py` itself.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Every item, session, response and report payload now states which
  contract version it was written against, and `runtime.upgrade_session`
  gives a session a real forward path instead of a dead-end rejection --
  closing the `CONCERNS.md` gap PROTO-01 named.
- The five `schemas/*.json` documents are self-contained: an agent with no
  repository access can read them and know what an item, a session, a
  response event, a report and a lint entry are. Every one stays inside
  the fixed 17-keyword subset plan 01-06's validator is scoped to enforce.
- `response.schema.json`'s `$defs` already name `mark_event`,
  `retraction_event` and `day_tick_event` as reserved, unenforced slots --
  plans 01-07 and 01-09 can fill those in rather than starting from a
  blank document.
- PROTO-01's `adjacency` truth ("a shape change is accompanied by a
  version bump") is authored as an explicit `backstop` in this plan's
  `must_haves`, not mechanically verified here -- there is no committed
  baseline to diff a shape change against on this document's first
  release. PROTO-01's `ordering` edge is deferred to plan 01-06, where
  `itembank schema --all` gives it something to be stable about.
- No blockers identified for `01-06` onward. The one open item remains the
  pre-existing `durability_roundtrip.py` kill-probe timing flakiness noted
  above and in every prior plan's summary in this phase.

---
*Phase: 01-evidence-spine-protocol-foundation*
*Completed: 2026-08-06*

## Self-Check: PASSED

- FOUND: schemas/item.schema.json
- FOUND: schemas/session.schema.json
- FOUND: schemas/response.schema.json
- FOUND: schemas/report.schema.json
- FOUND: schemas/lint_error.schema.json
- FOUND: runtime.py
- FOUND: surfaces/session.py
- FOUND: itembank.py
- FOUND: tests/protocol_roundtrip.py
- FOUND: .planning/phases/01-evidence-spine-protocol-foundation/01-05-SUMMARY.md
- FOUND: 53bc97e (Task 1 commit)
- FOUND: deaa707 (Task 2 commit)
- FOUND: 01f3f22 (Task 3 commit)
