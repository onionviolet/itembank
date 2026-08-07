---
phase: 02-daemon-consolidation-settings-foundation
plan: 03
subsystem: settings
tags: [json-schema, cli, contract-delivery, validation]

# Dependency graph
requires:
  - phase: 02-daemon-consolidation-settings-foundation
    provides: "02-01: the phase's own established one-Handler/route-table daemon pattern this plan does not touch; this plan is settings-only and has no runtime dependency on 02-01/02-02's daemon code"
provides:
  - "schema_validate.py: minimum/maximum numeric-bound keywords, default and x-itembank-phase accepted annotations -- the validator's full published keyword set as of this plan"
  - "schemas/settings.schema.json: the one published document describing itembank.json -- all seven top-level keys (theme, daily_cap, selection_weights, auditor_autonomy, model_backend, update_policy, daemon) typed, ranged or enumerated, defaulted, and annotated with the phase that reads them"
  - "itembank.json: the one settings file, shipped at repository root, every key at its schema default"
  - "surfaces/settings.py: SETTINGS_CODES, classify_error(), load_settings()/write_settings()/settings_path(), defaults_from_schema(), get_at()/set_at()/schema_for_key(), cmd_config() -- the settings reader/writer and its dotted error-code classifier"
  - "itembank config / config schema / config set KEY VALUE: the CLI surface, registered in surfaces/cli.py"
affects: [4, 7, 8, 10, 11, 12]

actuals:
  tokens: 8583
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "cmd_config mirrors cmd_schema's exact three-tier shape (no-args human table, `config schema` verbatim document, `config set` validate-then-write) -- the decision recorded at Task 1's checkpoint"
    - "SETTINGS_CODES built the same sorted(set(...)) way LINT_CODES is (D-16 extended to settings), with classify_error() as a thin string classifier over schema_validate.validate()'s own message text -- the validator's return contract (a list of plain strings) is never widened"
    - "load_settings()/write_settings() merge itembank.json over the schema's own defaults_from_schema() output and write tmp-then-os.replace() matching runtime.write_session's byte layout exactly, so a repeated `config set` with the same value is byte-identical, not merely equivalent"
    - "Nested object schemas (daemon, selection_weights, model_backend) each declare `required` over their own properties, so a partial nested object on `config set` is a reachable settings.missing_key rather than a published code with no input path to it"

key-files:
  created:
    - schemas/settings.schema.json
    - surfaces/settings.py
    - tests/config_roundtrip.py
  modified:
    - schema_validate.py
    - surfaces/cli.py
    - itembank.json

key-decisions:
  - "Task 1 checkpoint resolved as option-a (2026-08-07): itembank config mirrors itembank schema exactly -- no-args human table, config schema verbatim, config set validate-then-write; dotted SETTINGS_CODES following the LINT_CODES precedent. Recorded inline in 02-03-PLAN.md's new <resolution> block, binding for surfaces/settings.py's cmd_config."
  - "Nested object schemas (daemon, selection_weights, model_backend) gained their own `required` arrays over their own properties -- not specified verbatim in the plan's <action> text, but needed so settings.missing_key (one of the six published codes) has a reachable input path via `config set daemon '{\"port\":8000,\"lan\":false}'` rather than being published and unreachable."
  - "The status column's separator is a plain ASCII '--' rather than the plan text's em dash, to avoid a non-ASCII character reaching a cp1252 Windows console verbatim in printed CLI output -- the project's own comments already prefer '--' in prose for exactly this reason."
  - "merge_over_defaults() does a one-level-deep merge for nested objects (daemon/selection_weights/model_backend), not just a top-level dict update -- so a settings file missing one nested key (e.g. daemon.lan alone) still reads that one key as its default instead of losing its siblings, an edge the plan's <behavior> block implies but does not spell out."

requirements-completed: [DEL-04, DEL-05]

coverage:
  - id: D1
    description: "D-05: One documented file, itembank.json, holds all six PROJECT.md settings plus the daemon's own port/LAN settings, each with a declared type, an allowed value set or numeric range, and a default"
    requirement: DEL-04
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py#test_schema_names_every_project_key"
        status: pass
      - kind: unit
        ref: "Task 2's automated verify block: itembank.json validates clean against schemas/settings.schema.json"
        status: pass
    human_judgment: false
  - id: D2
    description: "itembank config with no arguments prints a table of every settings key with type, allowed values, default, current value and the phase that reads it"
    requirement: DEL-05
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py#test_config_no_args_prints_table"
        status: pass
    human_judgment: false
  - id: D3
    description: "itembank config schema prints schemas/settings.schema.json verbatim from disk"
    requirement: DEL-05
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py#test_config_schema_byte_identical"
        status: pass
    human_judgment: false
  - id: D4
    description: "itembank config set KEY VALUE with an invalid value exits non-zero with a dotted error code from the published namespace, never a bare English sentence"
    requirement: DEL-05
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py#test_config_set_type_errors,test_config_set_invalid_value,test_config_set_unknown_key,test_config_set_missing_key,test_boundary_values_exact,test_config_malformed_file"
        status: pass
    human_judgment: false
  - id: D5
    description: "D-07: Settings validation runs through schema_validate.validate() only; no second type or range checker exists"
    verification:
      - kind: unit
        ref: "python -c \"...assert 'schema_validate' in src...\" (plan acceptance criterion); reviewer confirmation that no hand-written type/range comparison exists outside classify_error's string matching"
        status: pass
    human_judgment: true
    rationale: "The acceptance criterion is itself a source-inspection assertion the plan specifies; confirmed by reading surfaces/settings.py end to end -- classify_error() only pattern-matches validator message text, every actual type/range decision is schema_validate.validate()'s."
  - id: D6
    description: "For every numeric settings key, the value exactly at minimum/maximum is accepted and written; one step outside either is rejected with settings.out_of_range and itembank.json is left byte-identical"
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py#test_boundary_values_exact"
        status: pass
    human_judgment: false
  - id: D7
    description: "config set decodes its value as JSON before validating -- 3 is an integer, true is a boolean, a float supplied for an integer key is invalid_type rather than truncated, a boolean is never accepted where a number is required"
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py#test_config_set_type_errors,test_config_set_bool_stored_as_bool"
        status: pass
      - kind: unit
        ref: "schema_validate.py's _matches_type()/minimum/maximum bool-exclusion (unchanged, extended additively)"
        status: pass
    human_judgment: false
  - id: D8
    description: "Running config set KEY VALUE twice with the same value leaves itembank.json byte-identical -- same key order, indentation, trailing newline -- and exits 0 both times"
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py#test_config_set_idempotent"
        status: pass
    human_judgment: false
  - id: D9
    description: "itembank.json is written tmp-then-os.replace(); after a config set it parses clean, validates clean, and no leftover temp file remains"
    verification:
      - kind: manual_procedural
        ref: "Manual check during implementation: after `config set daemon.port 9002`, os.listdir shows only itembank.json (no .tmp), the written file parses and validates clean against schemas/settings.schema.json"
        status: pass
    human_judgment: false
  - id: D10
    description: "A key present in itembank.json the schema does not define is reported by itembank config as unknown and preserved on the next write -- never silently dropped, never silently honoured"
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py#test_unknown_key_preserved"
        status: pass
    human_judgment: false
  - id: D11
    description: "Two itembank config set commands running concurrently against the same itembank.json are last-writer-wins over the whole file -- neither can produce a torn or unparseable file, but an interleaved read-modify-write may drop the earlier command's key change"
    verification:
      - kind: manual_procedural
        ref: "Architectural: write_settings()'s tmp-then-os.replace() (same primitive runtime.write_session already relies on) makes a torn file impossible by construction; the drop-on-interleave case is the plan's own declared backstop, not asserted by an automated test"
        status: pass
    human_judgment: true
    rationale: "Plan's own must_haves marks this verification: backstop -- accepted architecturally via os.replace()'s atomicity, not exercised by a concurrency test in this plan."
  - id: P1
    description: "MUST NOT present a settings key that nothing reads as if it controls behaviour -- itembank config states per key which phase reads it and marks every key no shipped code reads yet"
    verification:
      - kind: integration
        ref: "tests/config_roundtrip.py#test_config_no_args_prints_table (asserts >=5 'inert' occurrences and that daemon is never marked inert)"
        status: pass
    human_judgment: true
    rationale: "Transparency prohibition; satisfied by rendering the status column from the schema's own x-itembank-phase annotation rather than a hand-maintained list, so it cannot drift -- judgment call on wording, mechanically checked for presence."

duration: 65min
completed: 2026-08-07
status: complete
---

# Phase 02 Plan 03: Settings Foundation -- Schema, Validator, `itembank config` Summary

**`itembank config` now mirrors `itembank schema` exactly across all three tiers -- a human summary table naming every setting's type, range, default, current value and owning phase; `config schema` handing over `schemas/settings.schema.json` verbatim; and `config set KEY VALUE` validating through `schema_validate.validate()` before writing tmp-then-`os.replace()` -- with a rejected value always carrying one of six published dotted codes and never touching `itembank.json` on disk.**

## Performance

- **Duration:** ~65 min (includes the prior executor's Task 1 checkpoint wait, which this continuation agent excludes from active work but the phase's wall-clock spans)
- **Tasks:** 3 (Task 1 checkpoint:decision resolved by the human; Task 2 and Task 3 executed by this continuation agent)
- **Files modified:** 6 (2 new schema/module files, 1 new test file, 1 new settings file at repo root, 2 existing files touched additively)

## Accomplishments

- **Task 1 checkpoint resolved.** The human selected option-a ("Mirror `itembank schema` exactly") for both `itembank config`'s output shape and the settings error-code namespace. Recorded verbatim in `02-03-PLAN.md`'s new `<resolution>` block (commit `b581e47`), binding for Task 3.
- **`schema_validate.py`** gained `minimum`/`maximum` in `SUPPORTED` and `default`/`x-itembank-phase` in `ANNOTATIONS`; `validate()` implements both numeric bounds immediately after the `minLength` block, excluding `bool` from numeric matching the same way `_matches_type()` already does, so `True` can never satisfy a numeric bound.
- **`schemas/settings.schema.json`** (new): the one published document for `itembank.json` -- all seven top-level keys (`theme`, `daily_cap`, `selection_weights`, `auditor_autonomy`, `model_backend`, `update_policy`, `daemon`) typed, ranged/enumerated, defaulted, and annotated with the phase that reads them. Deliberately not registered in `protocol_cli.CONTRACTS` -- `itembank config` is its delivery command, not `itembank schema`. The three nested object schemas (`daemon`, `selection_weights`, `model_backend`) each carry their own `required` array so `settings.missing_key` has a reachable input path.
- **`itembank.json`** (new, repo root): generated programmatically from the schema's own defaults, so the file and the schema cannot disagree on day one.
- **`surfaces/settings.py`** (new): `SETTINGS_CODES` (a sorted dotted tuple following the `LINT_CODES` precedent), `classify_error()` (a thin string classifier over `schema_validate.validate()`'s own message text), `load_settings()`/`write_settings()`/`settings_path()` (merge-over-defaults read, tmp-then-`os.replace()` write matching `runtime.write_session`'s byte layout), `defaults_from_schema()`, `get_at()`/`set_at()`/`schema_for_key()` (dotted key-path accessors), and `cmd_config()` (the three-tier CLI handler mirroring `cmd_schema`).
- **`surfaces/cli.py`** registers the `config` subcommand (`schema|set` action, `key`, `value`, `--base`).
- **`tests/config_roundtrip.py`** (new): 14 checks covering schema completeness, exact boundary values, all three `config` tiers, idempotent/atomic writes, unknown-key preservation, missing-schema-key-reads-as-default, and a structural reachability check that every one of the six `SETTINGS_CODES` is actually triggered by some input the test itself supplies.

## Task Commits

Each task was committed atomically:

1. **Task 1 resolution (checkpoint:decision, human-resolved as option-a)** -- `b581e47` (docs)
2. **Task 2: The settings schema, the validator's missing keywords, and the shipped defaults file** -- `5abc56b` (feat)
3. **Task 3: `itembank config` -- print the contract, reject a bad value by name** -- `1e1ee7e` (feat)

_Note: this plan's docs-completion commit (SUMMARY.md/STATE.md/ROADMAP.md/REQUIREMENTS.md) follows this file's creation, per the execute-plan workflow._

## Files Created/Modified

- `schema_validate.py` -- `minimum`/`maximum` added to `SUPPORTED`; `default`/`x-itembank-phase` added to `ANNOTATIONS`; `validate()` implements both bounds; module docstring's keyword list extended
- `schemas/settings.schema.json` (new) -- the published settings contract; seven top-level keys, three of which are nested objects with their own `required` arrays
- `itembank.json` (new, repo root) -- every key at its schema default
- `surfaces/settings.py` (new) -- `SETTINGS_FILE`, `SCHEMA_PATH`, `THIS_PHASE`, `SETTINGS_CODES`, `settings_path()`, `load_schema()`, `defaults_from_schema()`, `merge_over_defaults()`, `load_settings()`, `write_settings()`, `get_at()`, `set_at()`, `schema_for_key()`, `classify_error()`, `decode_value()`, `range_or_enum()`, `status_text()`, `render_value()`, `print_row()`, `print_table()`, `cmd_config()`
- `surfaces/cli.py` -- imports `cmd_config`; registers the `config` subparser
- `tests/config_roundtrip.py` (new) -- 14 checks; house style (`fail(msg)`, subprocess against a temp `--base`, closing `ok:` summary line)

## Decisions Made

- **Task 1: option-a**, as detailed in `key-decisions` above and recorded verbatim in `02-03-PLAN.md`'s new `<resolution>` block -- the binding D-06 shape for `itembank config` and the `settings.*` error-code namespace.
- **Nested `required` arrays added to `daemon`/`selection_weights`/`model_backend`.** Not spelled out verbatim in the plan's `<action>` text, but needed so `settings.missing_key` -- one of the six codes the plan itself publishes in `SETTINGS_CODES` -- has an actual input that triggers it (a `config set daemon '{"port":8000,"lan":false}'` with `open_browser` omitted). Without this, the code would be published and structurally unreachable, which the plan's own acceptance criteria explicitly guards against ("every code in `SETTINGS_CODES` is reachable from at least one input the test supplies").
- **ASCII `--` instead of an em dash in the printed status column.** The plan's action text writes "inert — read from phase N"; printed directly to a Windows console under a non-UTF-8 codepage, the literal em dash renders as a mangled byte. The project's own comments already prefer `--` in prose for exactly this reason (see `CLAUDE.md`'s documented code style), so this substitution follows house convention rather than introducing a new one.
- **`merge_over_defaults()` merges nested objects one level deep**, not as a flat top-level dict update. A settings file that has drifted to be missing just one nested key (e.g. `daemon` present but without `lan`) still reads that single key as its schema default instead of losing every sibling key in the same object -- a natural reading of "a missing key reads as its default" that the plan's `<behavior>` block implies without spelling out the nested case explicitly.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] `settings.missing_key` had no reachable input path**
- **Found during:** Task 3, while writing `tests/config_roundtrip.py`'s reachability check (`test_all_codes_reachable`), itself required by the plan's own acceptance criteria
- **Issue:** As originally drafted per the plan's literal schema description, none of the three nested object schemas declared `required`, so `schema_validate.validate()` could never emit "missing required key" against them, and `settings.missing_key` -- a code the plan publishes in `SETTINGS_CODES` -- had no test input, or any real user input, that could trigger it.
- **Fix:** Added `required` (listing each object's own property names) to `daemon`, `selection_weights`, and `model_backend` in `schemas/settings.schema.json`. `itembank.json`'s generated defaults already satisfy `required` for all three, so this is additive and does not change the shipped file's validity.
- **Files modified:** schemas/settings.schema.json
- **Verification:** `python tests/config_roundtrip.py` -- `test_config_set_missing_key` and `test_all_codes_reachable` both pass; `for t in tests/*.py; do python "$t" || exit 1; done` still passes.
- **Committed in:** `1e1ee7e` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (Rule 2, found and fixed before commit -- not a separate follow-up)
**Impact on plan:** No scope creep; the fix is required for the plan's own stated acceptance criterion (every published code reachable) to hold, and it is additive to the schema the plan otherwise specifies verbatim.

## Issues Encountered

None beyond the one auto-fixed deviation above. `itembank.py`'s top-level `__all__`/import block was deliberately left untouched -- it is not in this plan's `files_modified`, and `surfaces/settings.py`'s symbols are reachable via `from surfaces import settings` (used by `tests/config_roundtrip.py` and `surfaces/cli.py`) without needing a top-level re-export.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- `schemas/settings.schema.json`, `itembank.json`, and `surfaces/settings.py` are the settings foundation phases 4, 7, 8, 10, 11 and 12 each register real behaviour against by reading their own key(s) -- none of them need to touch the schema shape itself, only start reading a key that already exists.
- `daemon.port`/`daemon.lan`/`daemon.open_browser` are the only keys read by shipped code so far (phase 2 itself); plan 02-06 (LAN/probe) is the natural next consumer if it chooses to read defaults from `itembank.json` rather than only from `--port`/`--lan` CLI flags -- left to that plan's own discretion, not assumed here.
- No blockers.

---
*Phase: 02-daemon-consolidation-settings-foundation*
*Completed: 2026-08-07*

## Self-Check: PASSED

All created/modified files (`schema_validate.py`, `schemas/settings.schema.json`, `itembank.json`, `surfaces/settings.py`, `surfaces/cli.py`, `tests/config_roundtrip.py`, this SUMMARY.md) and all three task commits (`b581e47`, `5abc56b`, `1e1ee7e`) verified present on disk / in git log.
