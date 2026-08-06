---
phase: 01-evidence-spine-protocol-foundation
plan: 06
subsystem: infra
tags: [json-schema, validator, protocol, ci, contract-delivery, proto-04, proto-05]

# Dependency graph
requires:
  - phase: 01-05
    provides: "The five schemas/*.json documents, each held inside a fixed 17-keyword subset on purpose so this plan's validator could implement exactly that subset; ITEM_VERSION/SESSION_VERSION/REPORT_VERSION/EVENT_SCHEMA_VERSION as the constants each document's x-itembank-version is checked against"
  - phase: 01-03
    provides: "LintError/_asdict() and itembank lint --json's {schema_version, bank, items, errors, warnings} envelope, whose errors/warnings arrays are what lint_error.schema.json describes and this plan's CI step validates"
provides:
  - "schema_validate.py: SUPPORTED, ANNOTATIONS, SchemaError, check_schema(), validate(), main() -- a hand-rolled JSON Schema subset validator, stdlib-only, that refuses to run (SchemaError, exit 2) on any keyword outside the 12-keyword SUPPORTED set rather than silently skipping it"
  - "itembank.py: SUPPORTED, SchemaError, validate re-exported"
  - "surfaces/protocol_cli.py: cmd_schema() -- itembank schema [NAME] and itembank schema --all, the PROTO-05 delivery mechanism: one JSON object carrying model.SPEC, all five schemas/*.json documents in sorted order, and the exact command sequence to run a session, each tied to the contract its output conforms to"
  - ".github/workflows/ci.yml: 'Runtime output matches published schema' step -- drives start/submit/report/evidence/lint end to end under /tmp and validates every payload against schemas/*.json, the CI half of PROTO-04"
  - "tests/protocol_roundtrip.py: test_runtime_matches_schemas() (local mirror of the CI step) and test_schema_command_output() (PROTO-05's automated half)"
affects: [01-07, 01-08, 01-09, 01-10, 01-11]

actuals:
  tokens: 7056
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "schema_validate.py implements exactly the keyword subset schemas/*.json use and nothing more; check_schema() walks the whole document once, before any instance is examined, and raises SchemaError on anything outside SUPPORTED/ANNOTATIONS. A green validation therefore always means the whole document was checked -- the design decision the plan's objective names as decisive."
    - "bool is excluded from both integer and number type matching, since Python's bool is an int subclass and would otherwise silently validate as either -- asserted directly in Task 1's verify block."
    - "$ref resolution is scoped to the local '#/$defs/<name>' form only; anything else raises SchemaError rather than being partially handled."
    - "cmd_schema mirrors cmd_spec exactly: no processing, the schemas/*.json bytes handed over verbatim for a single name, or bundled into one sort_keys JSON object for --all. Two consecutive runs are byte-identical because sort_keys=True makes dict iteration order irrelevant to output bytes."
    - "The CI step and the new local test both validate report['summary'] against report.schema.json's session-summary variant, not the full itembank report wrapper -- the wrapper adds session_id/status beside summary, and the published session-summary shape describes the inner object, matching what 01-05's own test_schema_versions_present already asserts against report['summary']['schema_version']."

key-files:
  created:
    - schema_validate.py
    - surfaces/protocol_cli.py
  modified:
    - itembank.py
    - surfaces/cli.py
    - .github/workflows/ci.yml
    - tests/protocol_roundtrip.py

key-decisions:
  - "The CI step's 'python -c' one-liners take their file paths as sys.argv rather than embedding them as string literals inside the -c script text. Functionally identical on the Linux CI runner either way, but sys.argv is what let the exact same step be verified locally line-for-line on this Windows dev machine, where MSYS/git-bash auto-translates a bare CLI argument like '/tmp/start.json' to the real Windows temp path but does NOT translate the same string when it appears embedded inside a quoted -c script -- a purely local testing artifact, not a CI behavior difference, but worth avoiding since it costs nothing."
  - "surfaces/protocol_cli.py's COMMANDS list marks id-assign's 'contract' as None. Its output ({schema_version, banks, dry_run}) is not one of the five published shapes, and the plan's own Task 2 action text lists id-assign among the required command entries without claiming it conforms to a document -- None says that honestly instead of forcing a wrong match."
  - "cmd_schema's plain-text index (no name, no --all) reads each schemas/*.json document to report its x-itembank-version live, rather than hardcoding '1' five times -- so the index cannot drift from the documents it is summarizing."

requirements-completed: [PROTO-04, PROTO-05]

coverage:
  - id: D1
    description: "schema_validate.py implements exactly the SUPPORTED keyword subset (type, properties, required, additionalProperties, enum, const, items, minItems, minLength, $defs, $ref, oneOf) and refuses (SchemaError, exit 2) on any schema keyword outside SUPPORTED/ANNOTATIONS, checked before any instance is examined"
    requirement: PROTO-04
    verification:
      - kind: unit
        ref: "Task 1 acceptance verify block (bool-as-integer rejection, missing-required rejection, additionalProperties:false rejection, allOf raising SchemaError with 'unsupported keyword')"
        status: pass
      - kind: unit
        ref: "python -c AST scan confirming schema_validate.py imports only json/os/sys"
        status: pass
    human_judgment: false
  - id: D2
    description: "CI gains a step that drives start/next/submit/report/evidence/lint end to end under /tmp and validates every payload against schemas/*.json with schema_validate.py; a broken contract fails the build"
    requirement: PROTO-04
    verification:
      - kind: integration
        ref: "the exact .github/workflows/ci.yml run block extracted and executed locally, exit 0, git status --porcelain clean afterward"
        status: pass
      - kind: unit
        ref: "manual deliberate-break check: schema_validate.py against a hand-edited evidence line missing session_id reports 'missing required key' and exits 1"
        status: pass
    human_judgment: false
  - id: D3
    description: "itembank schema --all emits one self-contained JSON object carrying model.SPEC verbatim, all five schemas/*.json documents in sorted name order, and the exact command sequence (start/next/submit/report/evidence) to run a session, each tied to the contract its output conforms to"
    requirement: PROTO-05
    verification:
      - kind: unit
        ref: "tests/protocol_roundtrip.py#test_schema_command_output"
        status: pass
      - kind: unit
        ref: "diff of two consecutive `itembank schema --all` runs, byte-identical"
        status: pass
    human_judgment: false
  - id: D4
    description: "Whether itembank schema --all's output is sufficient for a model with no repository access to author one item of every type and describe a recorded response -- a sufficiency judgment, not a string match"
    requirement: PROTO-05
    verification: []
    human_judgment: true
    rationale: "01-06-PLAN.md's own Task 3 <human-check> and its Flagged Assumptions section mark this explicitly manual: the automated test can confirm the output parses, is structurally self-contained, and is stable, but not that a fresh model context reading only the pasted output can successfully author all six item types. Not run against a genuinely fresh model context in this execution; carried forward as the plan itself designed."

duration: ~35min
completed: 2026-08-06
status: complete
---

# Phase 1 Plan 6: Enforce and Deliver the Contract Summary

**A hand-rolled, stdlib-only JSON Schema subset validator (`schema_validate.py`) that refuses to run on any keyword it doesn't implement, wired into CI to check real `start`/`submit`/`report`/`evidence`/`lint` output against `schemas/*.json` on every push, plus `itembank schema --all` as the one command that hands an agent with no repository access the whole contract in a single self-contained, byte-stable JSON object.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-06 (continuation from 01-05)
- **Completed:** 2026-08-06
- **Tasks:** 3
- **Files modified:** 6 (2 created, 4 modified)

## Accomplishments

- `schema_validate.py` (new, stdlib-only: `json`, `os`, `sys`) implements exactly
  the keyword subset `schemas/*.json` use -- `type`, `properties`, `required`,
  `additionalProperties`, `enum`, `const`, `items`, `minItems`, `minLength`,
  `$defs`, `$ref`, `oneOf` -- and nothing more. `check_schema()` walks the whole
  schema document once, before any instance is examined, and raises
  `SchemaError` on any keyword outside that set. A green validation therefore
  always means the whole document was checked, which is the design decision
  the plan's objective names as decisive: a validator that silently skipped
  `patternProperties` or `allOf` would report a green build while checking
  half the contract, worse than no check at all.
- `validate()` implements each keyword, including the two edge cases the plan
  called out by name: `bool` is excluded from both `integer` and `number`
  matching (Python's `bool` is an `int` subclass and would otherwise silently
  pass), and `oneOf` reports how many branches matched plus the first
  branch's errors on a near-miss, rather than a bare "no branch matched".
  `$ref` resolves only the local `#/$defs/<name>` form.
  `main()` gives it a CLI with three invocation shapes: one instance
  (`schema.json instance.json | -`), a JSONL log (`--jsonl path`), or an
  array field inside a JSON document (`--array path key`, for `lint --json`'s
  `errors`/`warnings`). Exit 0 clean, 1 on instance errors, 2 on a
  `SchemaError`, so "the schema is broken" is distinguishable from "the data
  is wrong" by exit code alone. `SUPPORTED`, `SchemaError` and `validate` are
  exported from `itembank.py`.
- `surfaces/protocol_cli.py` (new) gives `itembank schema` three behaviours,
  mirroring `cmd_spec` exactly: no name/no `--all` prints a plain-text index
  (name, live `x-itembank-version`, one-line summary) read from each document
  rather than hardcoded; a name prints that one document byte-for-byte;
  `--all` emits one `sort_keys=True` JSON object carrying `schema_version: 1`,
  the whole of `model.SPEC` under `spec`, all five documents under `contracts`
  in sorted name order, and a `commands` list -- the exact
  `lint`/`id-assign`/`start`/`next`/`submit`/`report`/`evidence` invocations,
  each carrying its description and the name of the contract its output
  conforms to (`None` for `id-assign`, whose output matches none of the
  five published shapes). Two consecutive `--all` runs are byte-identical.
- `.github/workflows/ci.yml` gains "Runtime output matches published schema",
  placed between "Sample fixture builds" and "Test suite". Under `set -e` and
  entirely inside `/tmp`, it drives `start` (validates the session file and
  the served item), `submit` (validates every evidence-log line), `report`
  (validates the session-summary half of `report.schema.json`), `evidence`
  (validates the objective-history half), and `lint fixtures/broken_bank.md
  --json` (validates every `errors`/`warnings` entry against
  `lint_error.schema.json`). The one `|| true` is on `lint`'s expected
  non-zero exit, and its output is validated on the very next line so an
  empty file cannot slip through unnoticed.
- `tests/protocol_roundtrip.py` gains `test_runtime_matches_schemas()`, the
  local mirror of the CI step (`itembank.validate()` called directly against
  each payload, so a developer sees red before pushing), and
  `test_schema_command_output()`, PROTO-05's automated half: `itembank
  schema --all` parses, carries `model.SPEC` verbatim, carries all five
  documents in sorted order each checking out under
  `schema_validate.check_schema`, names `start`/`next`/`submit`/`report`/
  `evidence` in its `commands` list, and is byte-identical across two runs.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write the minimal JSON Schema validator that fails loud on anything it cannot check** - `c7ac644` (feat)
2. **Task 2: Ship `itembank schema` so an agent with no repository access can read the whole contract** - `3a28d1f` (feat)
3. **Task 3: Gate the runtime against the published contract in CI and in the test suite** - `b4433d5` (test)

_Note: no TDD red/green/refactor split was called for; all three tasks are `type="auto"`._

## Files Created/Modified

- `schema_validate.py` (new) - `SUPPORTED`, `ANNOTATIONS`, `SchemaError`, `check_schema()`, `validate()`, `main()`, CLI flags `--jsonl` and `--array`
- `surfaces/protocol_cli.py` (new) - `SCHEMA_DIR`, `CONTRACTS`, `COMMANDS`, `cmd_schema()`
- `itembank.py` - `SUPPORTED`, `SchemaError`, `validate` added to the `from schema_validate import (...)` block and `__all__`, alphabetized; module docstring gains the `itembank schema [NAME]` line
- `surfaces/cli.py` - `cmd_schema` imported; `schema` subparser (`name` positional, `--all` flag)
- `.github/workflows/ci.yml` - new step "Runtime output matches published schema"
- `tests/protocol_roundtrip.py` - `import schema_validate`; `test_runtime_matches_schemas()`, `test_schema_command_output()`

## Decisions Made

- **The CI step's `python -c` one-liners read their file paths from
  `sys.argv` rather than embedding them as string literals.** On the Linux
  CI runner this is functionally identical either way. It mattered for
  local verification on this Windows dev machine: MSYS/git-bash
  auto-translates a bare CLI argument like `/tmp/start.json` to the real
  Windows temp path, but does not translate the same literal string when it
  is embedded inside a quoted `-c` script -- purely a local testing
  artifact of how MSYS's path-conversion heuristic scopes to whole
  standalone arguments, not substrings of a larger one. Using `sys.argv`
  sidesteps it for free and is arguably cleaner regardless of platform.
- **`report["summary"]`, not the full `itembank report` payload, is what
  gets validated against `report.schema.json`'s session-summary variant.**
  `cmd_report`'s top-level JSON wraps `runtime.session_summary()` under a
  `summary` key, alongside `session_id`/`status`; the published
  session-summary shape describes the inner object precisely (it is what
  01-05's own `test_schema_versions_present` already asserts against
  `report["summary"]["schema_version"]`), not the wrapper. Both the CI step
  and the new `test_runtime_matches_schemas()` extract `.summary` first
  (mirroring the `.item` extraction the plan already specified for `start`).
- **`surfaces/protocol_cli.py`'s `COMMANDS` marks `id-assign`'s `contract` as
  `None`.** Its output shape (`{schema_version, banks, dry_run}`) is not one
  of the five published documents; `None` says that honestly rather than
  forcing a false match, and `test_schema_command_output()` only requires
  that a *non-null* contract name resolve inside `contracts`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The CI step and local test validate `report["summary"]`, not the raw `itembank report` payload, against `report.schema.json`**
- **Found during:** Task 3, drafting and locally executing the CI step
- **Issue:** The plan's Task 3 action text says "Run `report /tmp/s.json` into `/tmp/report.json` and validate it against `schemas/report.schema.json`" without mentioning an extraction step. Run literally, this fails: `cmd_report`'s top-level payload is `{schema_version, session_id, status, summary}`, and `report.schema.json`'s session-summary variant requires `auto_attempts`/`auto_correct`/`pending_manual`/`objectives` directly at the top level -- those live one level deeper, inside `summary`. This is the same kind of plan-literal-text-vs-live-shape gap 01-02 and 01-05 each documented once already for this codebase's evidence-event field count.
- **Fix:** Both the CI step and `test_runtime_matches_schemas()` extract `.summary` from the report payload first (mirroring the `.item` extraction the plan explicitly specifies for `start`), then validate that against `report.schema.json`. Confirmed against 01-05's own `test_schema_versions_present`, which already asserts `report["summary"]["schema_version"] == REPORT_VERSION` for exactly this reason.
- **Files modified:** `.github/workflows/ci.yml`, `tests/protocol_roundtrip.py`
- **Verification:** The exact CI run block extracted from `ci.yml` and executed locally exits 0; `test_runtime_matches_schemas()` passes; a manual check without the extraction step was confirmed to fail with `oneOf matched 0 of 2 branches`, listing all four missing top-level keys.
- **Committed in:** `b4433d5` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 plan-literal-text-vs-live-shape bugfix, matching a pattern already established twice in this phase)
**Impact on plan:** Keeps the CI gate honest about what `report.schema.json` actually describes. No scope creep.

## Issues Encountered

- **Local Windows/git-bash MSYS path-translation quirk while verifying the CI step line-for-line.** A bare CLI argument like `/tmp/start.json` gets auto-translated by MSYS to the real Windows temp directory when passed to `python.exe`, but the identical string embedded inside a quoted `python -c "..."` script is not translated, since Python's own `open()` then resolves `/tmp/...` as relative to the current drive root (`C:\tmp\...`), which does not exist. This only affects local verification on this machine -- the real GitHub Actions runner is Ubuntu, where `/tmp` is a genuine absolute path either way, so there was never a real bug in the CI step's design. Fixed by having the `python -c` one-liners take their paths via `sys.argv` instead of embedding them as literals (see Decisions Made), which sidesteps the issue entirely and was then used to write the final `ci.yml` step, verified by extracting the exact `run:` block from the committed YAML and executing it line-for-line.
- **`tests/durability_roundtrip.py`'s kill-probe** ran cleanly on every full-suite pass during this plan's work (varying pair counts across runs, as in every prior plan's summary in this phase, but never a failure). Out of scope per the plan's stated pre-existing-issue note; not touched.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The published contract is now enforceable, not just published: CI fails
  the build the moment a runtime payload stops matching its `schemas/*.json`
  document, verified by a manual deliberate-break check (a missing
  `session_id` on a response event is caught and named).
- The published contract is now deliverable: `itembank schema --all` is the
  single artifact PROTO-05 asked for -- the bank format, all five runtime
  contracts, and the exact command sequence to exercise them, in one
  self-contained, byte-stable JSON object. Whether that object is
  *sufficient* for a genuinely fresh model context to author all six item
  types is the one item this plan's own design marks manual-only (D4 above,
  carried forward as `01-06-PLAN.md`'s Flagged Assumptions section already
  anticipated) -- not contradicted by anything found here, but not
  mechanically provable either.
- `schema_validate.py`'s `SUPPORTED`/`ANNOTATIONS` sets are now the concrete
  boundary any future `schemas/*.json` edit must respect: a document that
  needs `patternProperties`, `allOf`, or `if`/`then`/`else` stops CI at exit
  code 2 with a named keyword, rather than silently degrading the check.
  Plans 01-07 and 01-09, which give bodies to `response.schema.json`'s
  reserved `mark_event`/`retraction_event`/`day_tick_event` `$defs`, inherit
  this constraint directly.
- No blockers identified for `01-07` onward. The one open item remains the
  pre-existing `durability_roundtrip.py` kill-probe timing sensitivity noted
  in every prior plan's summary in this phase; it did not reproduce during
  this plan's work.

---
*Phase: 01-evidence-spine-protocol-foundation*
*Completed: 2026-08-06*

## Self-Check: PASSED

- FOUND: schema_validate.py
- FOUND: surfaces/protocol_cli.py
- FOUND: itembank.py
- FOUND: surfaces/cli.py
- FOUND: .github/workflows/ci.yml
- FOUND: tests/protocol_roundtrip.py
- FOUND: c7ac644 (Task 1 commit)
- FOUND: 3a28d1f (Task 2 commit)
- FOUND: b4433d5 (Task 3 commit)
