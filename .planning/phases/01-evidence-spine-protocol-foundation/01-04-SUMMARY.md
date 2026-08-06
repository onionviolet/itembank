---
phase: 01-evidence-spine-protocol-foundation
plan: 04
subsystem: infra
tags: [item-identity, content-hash, lint, cli, evidence]

# Dependency graph
requires:
  - phase: 01-02
    provides: "model.py's additive [ID:]/[HASH:] parsing into item_id/content_hash (empty until this plan), and evidence.py's evidence_key()/response_event() which already key on item_id when present"
  - phase: 01-03
    provides: "LintError namedtuple with dotted codes and LINT_CODES built from sorted(set(...)); this plan's five new checks join that structure directly"
provides:
  - "model.py: content_fingerprint(q) -- a sha256 digest over the tested content only (stem, options/correct/select, cats/rows, steps, model/rubric), whitespace-collapsed via collapse(), never the rationale fields"
  - "model.py: new_item_id() -- a 64-bit-random opaque id (uuid4 hex, first 16 chars)"
  - "model.py: assign_ids(text, taken=None) -- a pure text transform minting missing [ID:] and recording/refreshing [HASH:] lines, reusing parse_bank's own chunk split; a no-change block passes through byte-identical"
  - "model.py: five new lint codes -- item.missing_id, item.duplicate_id, item.missing_hash, item.content_drift, item.objective_unnamespaced (D-06). LINT_CODES now publishes 27 codes"
  - "itembank id-assign BANK... [--dry-run]: the only command that writes into a bank; lint stays read-only by design (D-03). Atomic tmp-file-then-os.replace() write, newline=\"\" preserving CRLF/LF, D-05 cross-bank id-uniqueness checked up front"
  - "fixtures/sample_bank.md: all six items now carry real [ID:]/[HASH:] lines, assigned for real by this plan"
  - "tests/evidence_roundtrip.py: test_identity_survives_edit -- the phase's headline proof that a stem edit leaves the evidence trail untouched"
affects: [01-05, 01-06, 01-07, 01-08, 01-09]

actuals:
  tokens: 7909
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "content_fingerprint(q) hashes only the tested-content fields per item type (never why/disc/second/trap/conf/da/notes/objective/difficulty/number/id/item_id/content_hash), truncated to 16 hex chars behind a 'sha256:' prefix -- a deliberate, documented integrity check rather than a security boundary"
    - "assign_ids(text, taken) is a pure text transform: split with parse_bank's own re.split, parse each chunk, mint/insert or leave byte-identical, rejoin with \"\". Keeps the write path (cmd_id_assign) fully separate from the pure logic (model.assign_ids), the same split runtime.write_session's callers already use for session I/O"
    - "cmd_id_assign checks D-05 cross-bank id-uniqueness in a first pass over all banks before any write, so a caller assigning several banks in one invocation gets a named, pre-write failure rather than a silent post-write collision"

key-files:
  created: []
  modified:
    - model.py
    - itembank.py
    - surfaces/evidence_cli.py
    - surfaces/cli.py
    - tests/evidence_roundtrip.py
    - fixtures/sample_bank.md

key-decisions:
  - "assign_ids's per-item tag in its change dicts (\"Q1\", \"Q2\"...) is a positional counter over successfully-parsed chunks, matching lint()'s own tag convention (positional enumerate, not the parsed Qn number), rather than q[\"number\"] -- keeps the two 'Qn' conventions in the codebase from silently diverging when a bank's own Qn numbering has gaps."
  - "cmd_id_assign prints the JSON payload and a human status line unconditionally (both, always), per the plan's explicit spec. Tests that need the JSON strip the trailing human line (last stdout line) before json.loads() rather than the command gaining a --json flag that isn't in the plan's contract."
  - "test_missing_and_duplicate_ids strips [ID:]/[HASH:] lines from the (now real) fixture rather than assuming a pristine id-less bank, since Task 2's real id-assign run against fixtures/sample_bank.md means the fixture itself now always carries identity fields."

requirements-completed: [EVID-01, EVID-02]

coverage:
  - id: D1
    description: "Editing an item's stem after evidence has been recorded against it leaves that evidence attached: querying by objective returns the same trail before and after, because the key is the opaque [ID:] and never the content"
    requirement: EVID-01
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_identity_survives_edit"
        status: pass
    human_judgment: false
  - id: D2
    description: "Two items assigned ids in separate banks never collide, and a duplicate id within one bank is a lint error (item.duplicate_id); an item with no [ID:] parses with item_id == \"\" and lints as a warning (item.missing_id), never an error, and lint never assigns one"
    requirement: EVID-01
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_missing_and_duplicate_ids"
        status: pass
    human_judgment: false
  - id: D3
    description: "itembank id-assign assigns ids and hashes in document order, is idempotent (a second run reports zero assignments and leaves the file byte-identical), and is the only command that writes into a bank"
    requirement: EVID-01
    verification:
      - kind: unit
        ref: "Task 2 acceptance commands: python -c assign_ids(t, set()) no-change assertion, git diff --quiet after a second real run, id-assign --help contains --dry-run"
        status: pass
    human_judgment: false
  - id: D4
    description: "A whitespace-only stem edit (internal spaces doubled, trailing newline added) leaves content_fingerprint unchanged; a one-character edit changes it"
    requirement: EVID-02
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_fingerprint_whitespace_stability"
        status: pass
    human_judgment: false
  - id: D5
    description: "An item carrying [ID:] but no [HASH:] produces item.missing_hash only, never item.content_drift; an item carrying neither produces item.missing_id only"
    requirement: EVID-02
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_hash_states"
        status: pass
    human_judgment: false
  - id: D6
    description: "lint --json output is stable across repeated runs: errors first then warnings, each in non-decreasing item order, bank-wide entry last within its list"
    requirement: EVID-01
    verification:
      - kind: unit
        ref: "tests/evidence_roundtrip.py#test_lint_order_stable"
        status: pass
    human_judgment: false

duration: ~18min
completed: 2026-08-06
status: complete
---

# Phase 1 Plan 4: Item Identity Outlives Its Text Summary

**`model.content_fingerprint()`/`new_item_id()`/`assign_ids()` plus the `itembank id-assign` command give every item an opaque, content-independent `[ID:]` and a change-detection `[HASH:]`, with five new lint checks (`item.missing_id`, `item.duplicate_id`, `item.missing_hash`, `item.content_drift`, `item.objective_unnamespaced`) reporting drift without writing anything — proven end to end by a test that edits a served item's stem and asserts its evidence trail is byte-identical before and after.**

## Performance

- **Duration:** ~18 min
- **Started:** 2026-08-06T17:08:23Z (continuation from 01-03)
- **Completed:** 2026-08-06T17:26:07Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- `content_fingerprint(q)` hashes exactly the tested content per item type
  (stem plus type-specific fields: `opts`/`correct`/`select` for mc/multi,
  `cats`/`rows` for table/dnd, `steps` for build, `model`/`rubric` for
  short), whitespace-collapsed via `collapse()`, case preserved, truncated
  to a 23-character `"sha256:" + 16 hex chars"` digest. Every rationale
  field (`why`, `disc`, `second`, `trap`, `conf`, `da`, `notes`,
  `objective`, `difficulty`, `number`, `id`, `item_id`, `content_hash`) is
  deliberately excluded, per D-04's accepted risk.
- `new_item_id()` mints a 64-bit-random opaque id (`uuid4().hex[:16]`).
- Five new lint checks join `LINT_CODES` (now 27 codes total):
  `item.missing_id` (warning), `item.duplicate_id` (error, tracked via a
  `seen_item_ids` dict alongside the existing `seen_ids`), `item.missing_hash`
  (warning), `item.content_drift` (warning, compares recorded hash against a
  freshly computed one), and `item.objective_unnamespaced` (warning, D-06's
  subject-namespacing check).
- `model.assign_ids(text, taken=None)` is a pure text transform: splits with
  `parse_bank`'s own `re.split`, parses each chunk, mints a missing `[ID:]`
  (re-minting on collision against `taken`) and records/refreshes `[HASH:]`,
  inserting missing lines before the first stem-terminator line and
  rewriting existing ones in place. A block whose id and hash are both
  already current passes through byte-identical, so a no-change run returns
  `new_text == text`.
- `surfaces/evidence_cli.py:cmd_id_assign` and the new `itembank id-assign`
  subcommand are the only writer into a bank. It checks D-05's cross-bank
  id-uniqueness in a first read-only pass over every bank named, then writes
  atomically (`tmp`-then-`os.replace()`, `newline=""` on both read and
  write to preserve CRLF/LF), skipping any bank whose text is unchanged.
  `--dry-run` prints the same JSON change set without writing.
- Ran `itembank id-assign fixtures/sample_bank.md` for real: all six items
  now carry `[ID:]` and `[HASH:]` lines, and `lint` on the fixture is clean
  of missing-id warnings (six `item.objective_unnamespaced` warnings remain,
  expected — the fixture's objectives are unnamespaced by design).
- `tests/evidence_roundtrip.py` gains five tests:
  `test_identity_survives_edit` (the phase's headline proof — edits a
  served item's stem, confirms `lint` reports drift and exits 0 while
  leaving `[ID:]` unchanged on disk, and confirms the evidence trail is
  byte-identical before the edit, after the edit+lint, and after
  re-running `id-assign` to refresh the hash), `test_missing_and_duplicate_ids`,
  `test_fingerprint_whitespace_stability`, `test_hash_states`, and
  `test_lint_order_stable`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Fingerprint the tested content and mint opaque ids, in model.py** - `f338689` (feat)
2. **Task 2: Add the explicit `itembank id-assign` action that writes ids and hashes into a bank** - `3ad722f` (feat)
3. **Task 3: Prove identity survives a stem edit, end to end** - `c9b9eb2` (test)

_Note: no TDD red/green/refactor split was called for; all three tasks are `type="auto"`. Task 1's commit deliberately excludes `assign_ids`/`TERMINATOR` (added and removed once, then reintroduced in Task 2's commit) so each commit's diff matches its own task's `<files>` scope exactly._

## Files Created/Modified

- `model.py` - `FINGERPRINT_SEP`, `collapse()`, `content_fingerprint()`, `new_item_id()`, `TERMINATOR`, `assign_ids()`; five new lint checks and codes; `seen_item_ids` dict added to `lint()`'s loop state
- `itembank.py` - `collapse`, `content_fingerprint`, `new_item_id`, `assign_ids` added to the `from model import (...)` block and `__all__`, alphabetized
- `surfaces/evidence_cli.py` - `cmd_id_assign(a)`: two-pass cross-bank uniqueness check, atomic per-bank write, JSON + human status line
- `surfaces/cli.py` - new `id-assign` subparser (`banks` nargs="+", `--dry-run`)
- `fixtures/sample_bank.md` - six `[ID:]`/`[HASH:]` line pairs, written by a real `itembank id-assign` run
- `tests/evidence_roundtrip.py` - `BROKEN_BANK` constant; `load_bank_text`/`write_bank_text`/`strip_identity`/`id_assign_json`/`lint_text` helpers; `test_identity_survives_edit`, `test_missing_and_duplicate_ids`, `test_fingerprint_whitespace_stability`, `test_hash_states`, `test_lint_order_stable`

## Decisions Made

- **`assign_ids`'s change-dict `"item"` tag is positional (`Q1`, `Q2`...
  over successfully-parsed chunks), matching `lint()`'s own tag convention**
  rather than the parsed `Qn` number, so the two "Qn" conventions already in
  the codebase (lint's positional tag vs. a bank's own possibly-gapped
  numbering, visible in `fixtures/broken_bank.md`'s `Q9` following `Q6`)
  stay consistent with each other.
- **`cmd_id_assign` prints the JSON payload and a human status line
  unconditionally**, exactly as the plan specifies, rather than gating the
  human line behind the JSON one or adding an undocumented `--json` flag.
  Tests that need the parsed payload strip the trailing human-readable line
  from stdout before `json.loads()`.
- **`test_missing_and_duplicate_ids` strips `[ID:]`/`[HASH:]` lines from
  the fixture rather than assuming a pristine id-less starting point.**
  Task 2 runs `id-assign` for real against `fixtures/sample_bank.md`, so by
  the time Task 3's tests run, the committed fixture always carries
  identity fields; the "missing id" and "two banks assigned distinctly"
  scenarios construct their own id-less copies via `strip_identity()`.

## Deviations from Plan

None — plan executed exactly as written. `assign_ids`'s implementation,
`cmd_id_assign`'s two-pass uniqueness check and atomic write, and all five
Task 3 tests match the plan's `<action>` blocks; the two decisions above are
implementation choices within the plan's own stated contract, not
departures from it.

## Issues Encountered

- **`tests/durability_roundtrip.py`'s kill-probe (built in plan 01-01,
  outside this plan's `<files>` scope) failed intermittently during
  full-suite runs**, with a `FileNotFoundError` on its temp `kill.jsonl` —
  the same pre-existing, documented timing race noted in 01-03's summary
  and flagged in this plan's own prior-context as out of scope. Confirmed
  by re-running the file in isolation: it failed four consecutive times
  under load from the surrounding test-writing session, then passed cleanly
  once the surrounding subprocess load settled. Not fixed here since this
  plan touches neither `evidence.py`'s kill-probe path nor
  `tests/durability_roundtrip.py`, and every other test in the suite
  (including a subsequent clean full-suite run) passed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Every item can now be fingerprinted deterministically and given a
  globally unique opaque id; `evidence.py`'s `evidence_key()` and
  `response_event()` already key on `item_id` when present (built ahead in
  01-02), so evidence recorded against a `sample_bank.md` item today is
  keyed on a real id rather than the `ref:` positional fallback.
- `itembank id-assign` is the only bank writer in the codebase; `lint`
  stays fully read-only, confirmed structurally by
  `test_identity_survives_edit`'s on-disk `[ID:]`-unchanged assertion after
  a lint run.
- `01-05` (published schemas) can treat the five new lint codes and
  `id-assign`'s `{schema_version: 1, banks: [...], dry_run}` JSON shape as
  additional worked examples alongside `lint --json`'s contract from 01-03.
- No blockers identified for `01-05` onward. The one open item is the
  pre-existing `durability_roundtrip.py` kill-probe timing flakiness noted
  above, which belongs to whoever next touches that file, not to this
  plan's scope.

---
*Phase: 01-evidence-spine-protocol-foundation*
*Completed: 2026-08-06*

## Self-Check: PASSED

- FOUND: model.py
- FOUND: itembank.py
- FOUND: surfaces/evidence_cli.py
- FOUND: surfaces/cli.py
- FOUND: tests/evidence_roundtrip.py
- FOUND: fixtures/sample_bank.md
- FOUND: .planning/phases/01-evidence-spine-protocol-foundation/01-04-SUMMARY.md
- FOUND: f338689 (Task 1 commit)
- FOUND: 3ad722f (Task 2 commit)
- FOUND: c9b9eb2 (Task 3 commit)
