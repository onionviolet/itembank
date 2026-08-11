---
phase: 07-selection-engine
plan: 01
subsystem: selection
tags: [selection, tracer, determinism, trace, fixture]

# Dependency graph
requires:
  - phase: 01
    provides: evidence store, item identity ([ID:]/[HASH:]), the one evidence_key
  - phase: 02
    provides: /api/* conventions and the shared do_* surface bodies
provides:
  - selection.select() as the only place an item is chosen
  - the selection spec dict (objective/count/seed/exclude_item_ids) and its trace shape
  - fixtures/selection_bank.md and fixtures/selection_evidence.jsonl
  - tests/selection_roundtrip.py with the phase's 18 declared checks
affects: [07-02, 07-03, 07-04, 07-05, 07-06, 10]

actuals:
  tokens: 21500
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - one selector, mirroring the one-scorer rule in runtime.py's docstring
    - pure selection with history passed in as an argument (D-09)
    - a spec field a later plan has not wired is refused loudly, not ignored

key-files:
  created:
    - selection.py
    - fixtures/selection_bank.md
    - fixtures/selection_evidence.jsonl
    - tests/selection_roundtrip.py
  modified:
    - surfaces/session.py
    - surfaces/daemon.py
    - itembank.py
    - build.py

key-decisions:
  - "select() raises SystemExit on any spec key outside SPEC_FIELDS, so an unwired field is refused loudly rather than silently ignored; each later plan appends its field in the same commit that wires it."
  - "The D-09 focus pin rides inside the spec dict (session-level) and is consumed by do_start before select(), preserving the pin while keeping the plan's 5-parameter do_start signature."
  - "order_shuffled() reproduces the old inline rng.shuffle byte-identically, so every existing seed-pinned assertion held unchanged in this wave; plan 07-05 owns the re-pinning the mode ordering swap will cause."
  - "Exclusions compare only evidence.evidence_key(q) values (never positional numbers), per 01-CONTEXT D-05."

patterns-established:
  - "Trace blocks cross the same public/private boundary public_item() enforces: identity, objective, difficulty and prose only, never correct/opts/da/why/disc/second/trap."

requirements-completed: [SEL-01, SEL-05]

coverage:
  - id: D1
    description: 30-item synthetic selection fixture across four namespaced objectives (8/8/7/7), six item types, two unlabelled difficulties, balanced answer positions
    requirement: SEL-01
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_fixture_lints_clean
        status: pass
      - kind: unit
        ref: tests/selection_roundtrip.py#check_objective_filter
        status: pass
    human_judgment: false
  - id: D2
    description: synthetic evidence history with 40 schema-valid response events, 3 cross-bank events, and one retraction
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_fixture_history_matches_response_schema
        status: pass
    human_judgment: false
  - id: D3
    description: selection.select() deterministic given bank, spec, history and seed
    requirement: SEL-01
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_determinism
        status: pass
    human_judgment: false
  - id: D4
    description: every selection returns a trace naming a distinct runner-up in plain English
    requirement: SEL-05
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_trace_names_runner_up
        status: pass
    human_judgment: false
  - id: D5
    description: trace leaks no answer key, rationale, or option text (threat T-07-03)
    verification:
      - kind: unit
        ref: tests/selection_roundtrip.py#check_trace_leaks_no_key
        status: pass
    human_judgment: false
  - id: D6
    description: itembank start and POST /api/start both reach selection.select() through do_start(); selection.py ships in the .pyz
    requirement: SEL-01
    verification:
      - kind: integration
        ref: tests/daemon_roundtrip.py
        status: pass
      - kind: integration
        ref: tests/agent_roundtrip.py
        status: pass
      - kind: integration
        ref: tests/packaging_roundtrip.py
        status: pass
    human_judgment: false
  - id: D7
    description: the trace reads as plain English to a human reader, not as rule ids
    requirement: SEL-05
    verification: []
    human_judgment: true
    rationale: "Readability is a manual judgment; it stays in 07-VALIDATION.md's manual-only table (run `itembank select --explain` when plan 07-06 ships the command)."

# Metrics
duration: 50min
completed: 2026-08-10
status: complete
---

# Phase 7 Plan 1: Selection Tracer Summary

**The one selector exists: `selection.select(questions, spec, history) -> (items, trace)` is now the only place an item is chosen, reached by both `itembank start` and `POST /api/start` through the same `do_start()` call, with a trace that names a runner-up and leaks no answer key.**

## Performance

- **Duration:** 50 min
- **Started:** 2026-08-10T18:44:00Z
- **Completed:** 2026-08-10T19:34:00Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- `selection.py`: pure, deterministic `select()`/`filter_by_spec()`/`order_shuffled()`,
  `SPEC_FIELDS = (objective, count, seed, exclude_item_ids)`, `DEFAULT_COUNT = 10`, and
  a trace shape (`spec`/`evidence`/`chosen`/`notes`, blocks with `item_id`,
  `item_ref`, `objective`, `reason`, `runner_up`) that later plans extend rather than
  replace.
- `do_start(bank_path, spec, mode, out, force)`: the inline `rng.shuffle` and count clamp
  are gone; the count guard moved into `select()` verbatim; the D-09 focus pin rides
  inside the spec dict so the pin survives the signature change.
- `/api/start` builds the same spec dict the CLI builds and returns the trace on the
  result; both `except` clauses in `handle_api_start` are untouched.
- `fixtures/selection_bank.md` (30 items, 4 namespaced objectives, 6 item types, 2
  unlabelled difficulties, balanced A-D answers), `fixtures/selection_evidence.jsonl`
  (40 schema-valid response events + 1 retraction), and `tests/selection_roundtrip.py`
  (2 filled + 4 filled-by-Task-3 checks + 12 declared stubs for plans 07-02..07-06).
- `build.py` stages `selection.py`; `itembank.py` exports `select`/`SPEC_FIELDS`/
  `DEFAULT_COUNT` in the existing sorted style.

## Task Commits

Each task was committed atomically:

1. **Task 1: fixture bank, synthetic evidence, test stubs** - `26e6460`
2. **Task 2: TRACER - selection.py and both start surfaces** - `b209a5f` (daemon hunk);
   `dac4bbd` (selection.py, session.py, itembank.py, build.py - see coordination
   deviation below)
3. **Task 3: tracer tests - objective filter, determinism, runner-up, no key leak** -
   `d0162c5`

**Plan metadata:** pending (next commit)

## Files Created/Modified

- `selection.py` - the one selector: pure select/filter/order + trace builder
- `surfaces/session.py` - do_start rewritten around the spec dict; cmd_start builds it
- `surfaces/daemon.py` - /api/start builds the same spec and returns the trace
- `itembank.py` - exports the selector's public symbols
- `build.py` - STAGE_FILES gains selection.py
- `fixtures/selection_bank.md` - 30-item synthetic bank for the whole phase
- `fixtures/selection_evidence.jsonl` - synthetic history (40 responses + 1 retraction)
- `tests/selection_roundtrip.py` - 18 declared checks, 6 live

## Decisions Made

- Unknown spec fields are refused loudly (SystemExit) rather than silently ignored.
- The D-09 focus pin lives in the spec dict, consumed before `select()` - this keeps
  the shipped lesson-backlink pin (serve_roundtrip D-09 test) working alongside the
  plan's 5-parameter signature.
- Ordering reproduces the pre-existing shuffle byte-identically; no seed-literal churn
  in this wave (plan 07-05 owns the mode-ordering swap).

## Deviations from Plan

### Coordination (environmental, not a code deviation)

**1. Concurrent 13-01 session swept staged Task-2 files into its commit**
- **Found during:** Task 2 commit
- **Issue:** A concurrent agent session was committing the sidecar (13-01) work at the
  same time; its `test(13-01)` commit (`dac4bbd`) swept up the still-staged
  `selection.py`, `surfaces/session.py`, `itembank.py` and `build.py` changes.
- **Fix:** No content was lost; the phase-7 daemon hunk kept its own commit
  (`b209a5f`), and the remaining phase-7 files are fully present in `dac4bbd`. The
  user's pending `fonts` STAGE_DIRS entry was recovered from the dangling stash commit
  `3b948c5` and restored to the working tree (still uncommitted, as it was).
- **Files modified:** commit labels in git history
- **Verification:** `git diff HEAD -- selection.py surfaces/session.py itembank.py
  build.py` is empty; the full suite is green.

**2. `itembank guard .` and `tests/lesson_roundtrip.py` are red for pre-existing
reasons** - both logged in `deferred-items.md`; neither is caused by phase 7 changes
(guard trips on pre-existing untracked skill/temp files; the lesson spec-only test
belongs to the in-progress 03.1-06 work). Phase-7-relevant suites are all green.

**3. `daemon_roundtrip` needs an isolated TEMP when `reasonix-desktop` is running** -
the running reasonix process writes `reasonix-*` temp dirs into the same snapshot root
the hostile-bank traversal check watches, producing a false positive. The suite is
green (58 checks) with an isolated temp root. Logged in `deferred-items.md`.

---

**Total deviations:** 3 documented (0 code deviations; 1 coordination, 2 pre-existing
environmental)
**Impact on plan:** None on the shipped selector; all phase-7 acceptance criteria pass.

## Issues Encountered

- The Q22 item initially lacked a `CORRECT:` line and the fixture bank had an
  answer-position skew (10/19 keyed B); both fixed by rebalancing option letters and
  refreshing fingerprints with `itembank id-assign` (10 hashes updated, lint back to
  0 errors / 0 warnings).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for 07-02 (pair/prereq tags in model.py) and 07-03 (bank-scoped cooldown index):
  the fixture carries no `[PAIR:]`/`[PREREQ:]` tags yet, and the cooldown history the
  index must answer lives in `fixtures/selection_evidence.jsonl`.
- The spec dict and trace shape are the seam 07-04's `selection_mode`/`selection_spec`
  recording and 07-05's mode compositions extend.

---
*Phase: 07-selection-engine*
*Completed: 2026-08-10*
