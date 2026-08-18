---
phase: 14A-identity-lifecycle-operation
plan: 01
subsystem: identity-kernel
status: complete
tags: [identity, fingerprint, discovery, corpus, evidence-mapping]
requires: []
provides:
  - identity.py, the model-tier opaque id minting and change-detection
    fingerprint kernel with the bank/lesson keyed-content carve-out
  - discovery.py, the read-only, cancellable, resumable multi-root walker
  - fixtures/corpus_14a.py, the seeded synthetic multi-root corpus generator
  - the D-14A-3 evidence-field migration mapping decision record
affects: [14A-02, 14A-03, 14A-04, phase-13.9-walking-skeleton]
tech-stack:
  added: []
  patterns:
    - opaque ids are uuid4().hex[:16], never derived from content, path, or
      display name (matches model.new_item_id())
    - object_fingerprint normalizes line endings for every kind and
      additionally strips trailing whitespace for every kind except bank
      and lesson
    - discovery walks in os.walk pre-order with resume tracked by exact
      path match against that same order, never by string comparison
key-files:
  created:
    - identity.py
    - discovery.py
    - fixtures/corpus_14a.py
    - tests/identity_roundtrip.py
    - .planning/phases/14A-identity-lifecycle-operation/14A-EVIDENCE-FIELD-MAPPING.md
    - .planning/phases/14A-identity-lifecycle-operation/14A-01-SUMMARY.md
key-decisions:
  - "discovery.run_report gained an optional approved_roots kwarg (not in the plan's literal 3-argument signature) to make the discovery.root_unapproved refusal code reachable; see Deviations."
  - "D-14A-3's rename is recorded as a mapping only; retention.py, selection.py, surfaces/, and schemas/report.schema.json are untouched."
requirements-completed: [ID-01, FILE-01, FILE-02, RIGHTS-01]
duration: ~1h
completed: 2026-08-18
---

# Phase 14A Plan 01: Identity Kernel Summary

**The identity kernel is shipped: opaque object ids, a normalized change-detection fingerprint with a keyed-content carve-out, the eleven-key revision record, restrictive rights defaults, bounded component ids, and a read-only multi-root discovery walker, all proven against a synthetic corpus with a symlink cycle, an out-of-root symlink, a permission-denied pocket, and a duplicate-fingerprint pair.**

## Task outcomes

- **Task 1 (identity.py, minted and fingerprinted end to end):** Complete.
  `identity.py` created at the repository root with every symbol named in
  the plan's "Artifacts this phase produces" section: the constants,
  `IdentityError`, `utc_now`, `new_object_id`, `new_component_id`,
  `normalize_for_fingerprint`, `object_fingerprint`, `rights_default`,
  `revision_record`, `mint_object`, `next_revision`, `mint_component`,
  `component_anchor`, `find_component_anchors`, `registry_rows`,
  `copy_candidates`. `tests/identity_roundtrip.py` was written first,
  confirmed failing (`ModuleNotFoundError: No module named 'identity'`),
  then made to pass. All acceptance criteria hold: 16-hex ids, the exact
  eleven-key `REVISION_KEYS` order, `rights_default()` all-`unknown`,
  `identity.unknown_kind` refusal, no `model`/`runtime`/`evidence` attribute
  leakage, and no em dash in the file.
- **Task 2 (corpus generator and discovery walker):** Complete.
  `fixtures/corpus_14a.py` builds three sibling roots (`root_vault`,
  `root_sources`, `root_banks`) from a fixed seed (1000 files for `"1k"`),
  plus a duplicate-fingerprint pair, a near-identically-named pair, a
  symlink cycle, an out-of-root symlink, and a permission-denied pocket, with
  `teardown_corpus()` restoring permissions before `shutil.rmtree`.
  `discovery.py` walks read-only with `os.walk(..., followlinks=False)`,
  detects out-of-root and cyclic symlinks by resolved real path before ever
  opening them, records denied paths without raising, reports a missing root
  as `unavailable` without stopping the rest of the inventory, and supports
  `cancel` and `resume_after`. `check_discovery()` added to
  `tests/identity_roundtrip.py`, including the before/after
  `(path, size, mtime_ns)` mutation snapshot. `python itembank.py guard .`
  reports `0 offending files`.
- **Task 3 (evidence-field mapping and regression set):** Complete.
  `14A-EVIDENCE-FIELD-MAPPING.md` records the D-14A-3 decision (`mastered`
  becomes a per-objective, self-adjustable fill state, working field name
  `evidence_support`), the five-location inventory of where the old label
  actually lives, the per-state disposition table, and an explicit statement
  that 14A executes no rename. `check_regressions()` added to
  `tests/identity_roundtrip.py`: the keyed-content carve-out, a proof that
  `model.content_fingerprint()` is unaffected by `identity.object_fingerprint()`
  having been called on the same bytes, `rights={}` versus `rights=None`
  equivalence, `registry_rows()` ordering stability, and `copy_candidates()`
  over duplicate and distinct records. `git diff --name-only` after this task
  touched only `tests/identity_roundtrip.py` (modified) and the new mapping
  file plus this summary (created); no path under `schemas/`, `retention.py`,
  `selection.py`, or `surfaces/` changed.

## Platform fallbacks and SKIP lines

Run on this machine (macOS, POSIX): `os.symlink` succeeded (`symlinks: True`,
both the cycle and the out-of-root link were created for real), and
`os.chmod(path, 0o000)` genuinely denied read access (`denied_mode: "read"`).
Neither of the two named SKIP lines fired on this run:

- `SKIP: symlink assertions (os.symlink unavailable on this platform)` -- not
  printed; the real symlink assertions ran.
- `SKIP: read-denial assertion (os.chmod cannot deny read on this platform);
  write refusal is proven in tests/journal_roundtrip.py` -- not printed; the
  real denied-read assertion ran.

Both SKIP paths exist in the test and are exercised by the corpus's own
`symlinks`/`denied_mode` flags on a platform where the fallback fires (for
example Windows without symlink privilege).

## Wall-clock budget baseline (recorded, not promised)

One full `"1k"` corpus build plus one complete `discovery.run_report()` over
it, measured on this machine: build 0.063s, inventory 0.021s, total 0.083s
for 1007 files (1000 generated plus the duplicate pair, near-duplicate pair,
and denied pocket). Recorded for 14A-04's D-12.6-10 budget comparison; no
budget claim is made here.

## Truth-to-command verification map

| must_have truth (abbreviated) | Verified by |
|---|---|
| 16-hex opaque ids, never content-derived | `check_identity()`, `new_object_id()` collision and determinism assertions |
| Eleven-key revision record, revision 1 / parent_revision None | `check_identity()`, `mint_object()`/`REVISION_KEYS` assertions |
| Trailing-ws carve-out for bank/lesson only | `check_identity()` and `check_regressions()`, `CORRECT: B ` assertions |
| No Unicode normalization | `check_identity()`, NFC/NFD byte comparison |
| No-fingerprint recorded as None, not "" | `check_identity()`, `mint_object(..., raw=None)` |
| Byte-identical content, different ids -> copy candidate, never merged | `check_identity()` and `check_discovery()`, `copy_candidates()` over the corpus duplicate pair |
| Zero-root inventory returns empty, complete True | `check_discovery()`, `discovery.run_report([])` |
| `registry_rows` stable sort by (kind, object_id) | `check_identity()` and `check_regressions()`, shuffled-input assertions |
| Source rights default to all-unknown | `check_identity()`, `rights_default()` and minted-source assertions |
| Discovery root-bounded, cancellable, resumable | `check_discovery()`, cancel-after-ten and resume_after concatenation assertions |
| Out-of-root symlink refused by name, never read | `check_discovery()`, `symlink_out_of_root` / `report["refused"]` / target-mtime assertions |
| Denied path inventoried, named, never mutated | `check_discovery()`, `denied_mode == "read"` branch |
| Missing root reports unavailable, rest still returns | `check_discovery()`, mixed-roots assertion |
| discovery.py has no journal/subprocess/urllib attribute | `check_discovery()`, `hasattr()` assertions |
| Synthetic corpus is the only 14A test data source | `fixtures/corpus_14a.py` construction plus `python itembank.py guard .` |
| identity.py stays model-tier (no model/runtime/evidence/journal attr) | `check_identity()`, `hasattr()` assertions |

## Disposition of the flagged FILE-02 unclassified edge

The plan's `<out_of_scope>` flagged one unclassified edge: whether FILE-02's
"useful before completion" clause implies any obligation beyond streaming
partial results, specifically a stable partial-result identity that survives
a resume, beyond what this plan's generator plus `resume_after` contract
already provides.

Disposition: closed here, not deferred to 14B. `discovery.inventory()`'s
`resume_after` contract tracks resumption by exact match against the
walker's own deterministic pre-order (never by string-sorting the relative
path, which would disagree with `os.walk`'s traversal order for a mixed
root-file/subdirectory tree). `check_discovery()` proves the concatenation
of a cancelled run's entries and a `resume_after`-continued run's entries
equals one uninterrupted run's entry list, which is the stability property
FILE-02 asks for: a partial result is not just present before completion,
it is also resumable to exactly the same total result. No further identity
beyond the relative path plus root is needed for this, because the walker's
order is already a deterministic function of the corpus's own file names
and directory structure, not of wall-clock timing or process state.

## Deviations from plan

- **`discovery.run_report` gained an optional `approved_roots` keyword
  argument.** The plan's behavior list requires
  `discovery.run_report(["/some/path/outside"])` "with an explicit
  approved-root list that excludes it" to raise `DiscoveryError` with code
  `discovery.root_unapproved`, but the plan's own function signature list
  gives `run_report(roots, cancel=None, resume_after=None)` with no fourth
  parameter to carry that "explicit approved-root list." Rather than guess a
  hidden global registry (which would violate the project's "no global
  state" architectural constraint) or silently drop the `root_unapproved`
  refusal code the plan explicitly names as introduced by this plan, an
  optional `approved_roots=None` keyword was added: when omitted, `roots` is
  trusted as approved (matching every other call site in this plan and
  preserving the plan's literal 3-argument usage everywhere else); when
  supplied, every entry of `roots` is checked with `inside_any_root` against
  `approved_roots` and a violation raises `discovery.root_unapproved` before
  any walking happens. This is recorded here per Rule 1-3 (auto-fix a
  missing-functionality gap) rather than silently omitted, since the
  refusal code is named in the plan's "Refusal codes introduced by this
  plan" list and is asserted in `<behavior>`.
- No other deviation. Every other function signature, constant, and file
  path matches the plan exactly.

## Verification results

- `python3 tests/identity_roundtrip.py` -- exit 0, prints `OK check_identity`,
  `OK check_discovery`, `OK check_regressions`, `OK identity_roundtrip`.
- `python3 tests/scoring_roundtrip.py` -- exit 0, `scoring contract: ok (6
  items, one scorer)`.
- `python3 tests/evidence_roundtrip.py` -- exit 0, full evidence contract
  suite passes (including its own deliberate unknown-event-type skip-and-warn
  case, unrelated to this plan).
- `python3 itembank.py guard .` -- `0 offending files`, exit 0.
- `python3 schema_validate.py --all` -- `17 schema documents self-check
  clean`, confirming `schemas/report.schema.json` (and every other shipped
  schema) is unchanged by this plan.
- `identity.py`, `discovery.py`, `fixtures/corpus_14a.py`,
  `tests/identity_roundtrip.py`, and
  `14A-EVIDENCE-FIELD-MAPPING.md` each contain zero em dash characters
  (checked with a `grep -c` count of the em dash character against each file).

## Commits

- `db805dd` -- `feat(14A-01): identity.py, minted and fingerprinted end to end`
- `f4859c9` -- `feat(14A-01): synthetic corpus generator and read-only discovery walker`
- `1f4cfdd` -- `docs(14A-01): record the D-14A-3 evidence-field migration mapping`

## Known Stubs

None beyond what the plan itself scopes out: no journal, no compare-and-swap
write, no operation vocabulary, no CLI command, no daemon route, no schema
file, and no `mastered` rename. All explicitly deferred to 14A-02, 14A-03,
14A-04, or 16B by the plan's own `<out_of_scope>` section.

## Threat Flags

None new. The plan's own `<threat_model>` STRIDE register covers this slice;
every "mitigate" row is exercised by `tests/identity_roundtrip.py` as
described in the truth-to-command table above. No endpoint, authority path,
or new persistence boundary was added: `identity.py` is pure functions over
caller-supplied bytes and dicts, and `discovery.py` opens files for reading
only.

## Self-Check: PASSED

`identity.py`, `discovery.py`, `fixtures/corpus_14a.py`,
`tests/identity_roundtrip.py`, `14A-EVIDENCE-FIELD-MAPPING.md`, and this
summary all exist. All three tasks' `<verify>` commands pass. `git diff
--name-only` after Task 3 touched no forbidden path. `itembank guard .` and
`schema_validate.py --all` both pass.
