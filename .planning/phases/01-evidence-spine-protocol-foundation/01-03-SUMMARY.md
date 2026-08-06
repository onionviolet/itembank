---
phase: 01-evidence-spine-protocol-foundation
plan: 03
subsystem: infra
tags: [lint, error-codes, json-contract, protocol, format-contract]

# Dependency graph
requires:
  - phase: 01-02
    provides: "The evidence spine tracer and item identity fields, landed before this plan so identity's later lint checks (01-04) are authored against the coded shape rather than the string shape"
provides:
  - "model.py: LintError namedtuple (code, field, item, message) with a __str__ that reproduces the historical 'Qn: message' text exactly; LINT_CODES, the published 22-code namespace, built via sorted(set(...)) so it is provably sorted and duplicate-free"
  - "itembank lint --json: {schema_version, bank, items, errors, warnings} with ensure_ascii=False, exit code 1 if errors else 0 in both modes"
  - "The three call sites that used to concatenate a lint entry with + (surfaces/cli.py cmd_lint, surfaces/quiz.py cmd_build, surfaces/quiz.py cmd_serve) all render via str(e) now, moved in the same commit as the return-type change"
  - "tests/protocol_roundtrip.py: the protocol contract test harness, extended by later plans in this phase (schema versions, itembank schema command)"
affects: [01-04, 01-05, 01-06, 01-07, 01-08, 01-09, 01-10, 01-11]

actuals:
  tokens: 5271
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "LintError as a namedtuple subclass with __slots__ = () and a __str__ override — the additive machine-readable fields (code, field, item) travel alongside the record, while every existing string-consuming call site keeps working because str() on the record reproduces exactly what a plain string used to be"
    - "LINT_CODES built from sorted(set(...)) rather than a hand-ordered tuple literal, so 'sorted and duplicate-free' is a property of construction rather than something that has to be maintained by eye across future edits"

key-files:
  created:
    - tests/protocol_roundtrip.py
  modified:
    - model.py
    - surfaces/cli.py
    - surfaces/quiz.py
    - itembank.py

key-decisions:
  - "LINT_CODES is generated from a Python set literal passed through sorted(), not a manually ordered tuple. The plan asked for 'sorted order' as an output property; building it from a set makes that property structural (a future code added out of order still sorts correctly and a future duplicate is silently deduped rather than shipping a second copy of the same code) instead of relying on the author to sort by hand."
  - "test_lint_json_encoding uses two items, not one: a table item with a CJK category name that is deliberately absent from CATEGORIES (echoed verbatim into the item.row_category_unknown message, proving the JSON round-trip), and a short item with a 30-character CJK rubric point (proving the length threshold counts str.split() tokens, not bytes). A single-item version was tried first and failed silently — a fully valid CJK bank produces zero warnings, so there was nothing in the JSON payload for the round-trip assertion to find; splitting the concern into two items with one deliberately-broken field fixed this."
  - "The subprocess-based JSON tests set PYTHONIOENCODING=utf-8 on the child process explicitly. Passing encoding='utf-8' to subprocess.run only affects how the parent decodes captured bytes; the child's own stdout encoding is still the host console code page (cp1252 on this Windows machine), which raised UnicodeEncodeError on non-ASCII content until the environment variable was set for the child."

requirements-completed: [PROTO-02]

coverage:
  - id: D1
    description: "Every entry lint() returns is a LintError carrying a stable dotted code, the field at fault, the item tag, and the unchanged human-readable message"
    requirement: PROTO-02
    verification:
      - kind: unit
        ref: "tests/protocol_roundtrip.py#test_lint_error_shape"
        status: pass
    human_judgment: false
  - id: D2
    description: "str(LintError(...)) reproduces today's 'Qn: message' text exactly, so itembank lint, build and serve print byte-identical output to what they printed before this plan"
    requirement: PROTO-02
    verification:
      - kind: unit
        ref: "tests/protocol_roundtrip.py#test_lint_error_shape (str() assertion) and the CI-equivalent acceptance commands run directly: sample_bank.md clean-lint and broken_bank.md's eight required substrings"
        status: pass
    human_judgment: false
  - id: D3
    description: "A bank that lints clean emits {errors: [], warnings: []} under itembank lint --json and exits 0; a bank with errors emits well-shaped error objects and exits non-zero"
    requirement: PROTO-02
    verification:
      - kind: unit
        ref: "tests/protocol_roundtrip.py#test_lint_json_clean"
        status: pass
    human_judgment: false
  - id: D4
    description: "itembank lint --json is UTF-8 with ensure_ascii=False, and length thresholds inside lint() count whitespace-separated tokens on the Unicode code-point string rather than bytes"
    requirement: PROTO-02
    verification:
      - kind: unit
        ref: "tests/protocol_roundtrip.py#test_lint_json_encoding"
        status: pass
    human_judgment: false
  - id: D5
    description: "The three call sites that used to concatenate a lint entry with + all moved to str(e) in the same commit as the return-type change, so no bank can trigger a TypeError"
    requirement: PROTO-02
    verification:
      - kind: unit
        ref: "acceptance-criteria AST scan command (surfaces/cli.py, surfaces/quiz.py, no bare '+' concatenation of an error/warning entry), run directly during Task 1"
        status: pass
    human_judgment: false
  - id: D6
    description: "The published code namespace (LINT_CODES) is sorted, duplicate-free, and every code's prefix is item or bank"
    requirement: PROTO-02
    verification:
      - kind: unit
        ref: "tests/protocol_roundtrip.py#test_lint_codes_declared"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-08-06
status: complete
---

# Phase 1 Plan 3: Machine-Readable Lint Error Codes Summary

**`model.lint()` now returns `LintError` records with a dotted code and the field at fault behind a `__str__` that reproduces the exact historical text, plus `itembank lint --json` as the machine contract an authoring agent branches on — with all three concatenating call sites moved in the same commit so no bank can raise a `TypeError`.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-06 (continuation from 01-02)
- **Completed:** 2026-08-06
- **Tasks:** 2
- **Files modified:** 5 (1 created, 4 modified)

## Accomplishments

- `LintError`, a `collections.namedtuple` subclass with `code`, `field`, `item`, `message`
  and a `__str__` that reproduces `"Qn: message"` byte-for-byte, replaces every plain
  string `lint()` used to append. All 22 of the plan's specified `errors.append`/
  `warnings.append` call sites were converted 1:1 against the plan's own message-to-code
  table, including the bank-wide `answer_position_skew` warning, whose `"BANK: "` literal
  prefix now lives in the record's `item` field instead of the message string.
- `LINT_CODES` publishes the 22-code namespace, built from `tuple(sorted({...}))` rather
  than a hand-typed ordered tuple, so "sorted, no duplicates" is a property of how the
  tuple is constructed rather than something that has to stay correct by inspection as
  codes are added later.
- `itembank lint --json` emits `{schema_version, bank, items, errors, warnings}` with
  `ensure_ascii=False`; each entry is `LintError._asdict()`, giving `code`/`field`/`item`/
  `message` keys in that order. Exit code stays `1 if errors else 0` in both human and JSON
  modes.
- All three call sites RESEARCH.md's Common Pitfall 2 named — `surfaces/cli.py`
  `cmd_lint`, `surfaces/quiz.py` `cmd_build`, `surfaces/quiz.py` `cmd_serve` — moved to
  `str(e)` in the same commit as the return-type change (Task 1's single commit), so
  `lint`, `build` and `serve` cannot go from working to a `TypeError` traceback together.
  The three read-only callers (`surfaces/anki.py`, `surfaces/session.py`,
  `surfaces/study.py`) needed no change — confirmed by reading each, not assumed — since
  they only test the list for truthiness.
- `tests/protocol_roundtrip.py` (new) pins the whole contract: every lint entry's shape,
  the code namespace's sortedness and namespace prefix, `--json`'s clean/broken behavior
  over a real subprocess invocation, and the token-vs-byte length edge PROTO-02 flagged —
  proven by a CJK rubric point that must NOT trip the too-long warning and a CJK category
  name that must round-trip unescaped through the JSON output.

## Task Commits

Each task was committed atomically:

1. **Task 1: Give every lint entry a dotted code, a field, and an unchanged human message** - `280b22b` (feat)
2. **Task 2: Create tests/protocol_roundtrip.py and pin the lint contract** - `3409342` (test)

_Note: no TDD red/green/refactor split was called for; both tasks are `type="auto"`._

## Files Created/Modified

- `model.py` - `LintError` namedtuple subclass (code/field/item/message, `__str__` reproduces `"Qn: message"`); `LINT_CODES` published tuple; `lint()` rewritten to append `LintError` records at all 22 sites, docstring updated
- `surfaces/cli.py` - `import json` added; `cmd_lint` renders via `str(e)`/`str(w)` in human mode and a new `--json` branch producing the `{schema_version, bank, items, errors, warnings}` contract; `lint` subparser gains `--json`
- `surfaces/quiz.py` - `cmd_build` and `cmd_serve` both render lint entries via `str(e)` instead of bare `+` concatenation
- `itembank.py` - `LintError` and `LINT_CODES` added to the `from model import (...)` block and `__all__`, in alphabetical position
- `tests/protocol_roundtrip.py` (new) - `fail()`, `run_lint_json()` helper, `test_lint_error_shape()`, `test_lint_codes_declared()`, `test_lint_json_clean()`, `test_lint_json_encoding()`, `main()`

## Decisions Made

- **`LINT_CODES` built from `sorted(set(...)))` rather than a hand-ordered tuple.** The
  plan asked for the tuple to be "in sorted order" as an output property; deriving it from
  a set-then-sort makes that structural rather than a maintenance burden on whoever edits
  the code list next.
- **`test_lint_json_encoding` uses two items, not one.** A single fully-valid short item
  with a CJK rubric point produces zero warnings (correctly — one whitespace-separated
  token never trips the 25-word threshold), which meant the JSON round-trip assertion had
  no non-ASCII content to find. Splitting into a second, deliberately-broken table item
  whose CJK category name is echoed verbatim into `item.row_category_unknown` gives the
  round-trip assertion something real to check while keeping the rubric-length assertion
  isolated to its own item.
- **`PYTHONIOENCODING=utf-8` set explicitly on the subprocess environment.** `subprocess.run(..., encoding="utf-8")` only controls how the parent decodes captured bytes; the child process's own `stdout` still uses the host console code page (`cp1252` on this Windows machine) unless told otherwise, which raised `UnicodeEncodeError` inside the child before this was added.

## Deviations from Plan

None - plan executed exactly as written. Every message-to-code mapping in Task 1's table
was applied verbatim; the three call sites were confirmed and moved in the same commit;
the three read-only callers were read and confirmed to need no change rather than assumed
safe.

## Issues Encountered

- The first draft of `test_lint_json_encoding` used a single short item and asserted the
  CJK rubric text appeared in the `--json` output; it failed because a fully-valid CJK
  rubric point produces zero warnings, so nothing in the payload carried the text to
  assert against. Fixed by adding a second, deliberately-broken item whose non-ASCII
  content is guaranteed to be echoed into an error message (see Decisions Made).
- The subprocess calls to `python itembank.py lint ... --json` initially raised
  `UnicodeEncodeError: 'charmap' codec can't encode characters` from inside the child
  process on this Windows machine, because the child's stdout defaults to the console
  code page rather than UTF-8. Fixed by passing `PYTHONIOENCODING=utf-8` in the
  subprocess's environment (see Decisions Made).
- `tests/durability_roundtrip.py`'s kill-probe (built in plan 01-01, outside this plan's
  `<files>` scope) failed intermittently during full-suite runs with a
  `FileNotFoundError` on its temp `kill.jsonl` — a timing race in the subprocess-kill
  probe, not a regression from this plan's changes. Confirmed by re-running the file in
  isolation three times consecutively with no failures, and by confirming this plan
  touched none of `evidence.py` or `tests/durability_roundtrip.py`. Not fixed here since
  it is out of this plan's file scope (Rule scope boundary); left for whoever next touches
  that test.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `lint()`'s return shape is now the coded contract PROTO-02 and D-16 require; `01-04`
  (item identity assignment via `itembank id-assign`) can author its four new lint checks
  directly against `LintError`/`LINT_CODES` rather than against bare strings, which is
  exactly the redundant-conversion cost this plan's objective named as the reason to land
  before identity.
- `itembank lint --json`'s `{schema_version: 1, ...}` shape is the first schema-versioned
  surface in the codebase; `01-05` (published schemas) should treat this shape as the
  worked example when it defines `response.schema.json` and friends.
- No blockers identified for `01-04` onward. The one open item is the pre-existing
  `durability_roundtrip.py` flakiness noted above, which belongs to whoever next touches
  that file, not to this plan's scope.

---
*Phase: 01-evidence-spine-protocol-foundation*
*Completed: 2026-08-06*

## Self-Check: PASSED

- FOUND: tests/protocol_roundtrip.py
- FOUND: model.py
- FOUND: .planning/phases/01-evidence-spine-protocol-foundation/01-03-SUMMARY.md
- FOUND: 280b22b (Task 1 commit)
- FOUND: 3409342 (Task 2 commit)
