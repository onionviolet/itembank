# Plan 14C-08 summary

Executed 2026-08-28 on Darwin arm64, Python 3.14.6. All three tasks ran. The
plan is `autonomous: true` and carries no blocking human checkpoint.

## What landed

- `ASR_BACKENDS = ()` and `_extract_asr` in `source_adapters.py`; `asr`
  registered at version `0.0.0`. Ten adapters now.
- `$defs.body_asr` in `schemas/source_locator.schema.json`, added to the
  `$defs.locator.body` `oneOf` list, with `x-itembank-version` and the
  `schema_version` `const` both left at 1 and the reason written into the
  schema's own top-level description.
- `VENDORED.md` completed: KaTeX 0.18.4 (two files), the CodeMirror 6 bundle,
  and the two font families backfilled with hashes recomputed today; the
  `## Backfill owed` section discharged and removed; a `## Update cadence`
  section with today's dated review note.
- `scripts/check_vendored.py`, a stdlib gate that recomputes every recorded
  checksum, follows the font manifest pointer, verifies each package row
  against its pin line, and fails on a row naming a parked package.
- One CI step running it, and one local `vendored` gate in
  `scripts/preflight.py` mirroring that step.
- A `## Bringing a source in` section in `README.md`.
- Five checks in `tests/source_adapters_roundtrip.py`.
- `.planning/phases/14C-source-adapter-registry/14C-FREEZE.md`, the phase
  freeze with a 61-row multi-source coverage audit.
- `14C-VALIDATION.md` filled in and signed off; `ROADMAP.md` and
  `REQUIREMENTS.md` status rows updated.

## The coverage audit, honestly

**61 rows. One is `flagged-unverified`**, and it is RESEARCH assumption A6:
no plan in this phase downloaded and inspected the eight audited packages'
sdist build scripts, and none promised to. It is recorded as an accepted limit
in `D-14C-3` rather than quietly marked covered. Every other row names a
specific `check_*` function or a specific command, never a plan number alone.

Two rows carry a qualification rather than a flat "covered":

- **Roster 6 (OCR)** is covered by `check_ocr_stubbed_extraction` and
  `check_ocr_honest_degradation`, and the live-model eye check is recorded
  UNRUN in `14C-06-SUMMARY.md` with its date and reason.
- **PORT-02** is advanced but not completed: the EPUB import direction is a
  prototype-level interchange adapter carrying a semantic loss report, which
  is what the requirement asks of an interchange adapter, not what it asks to
  be finished.

`nyquist_compliant` is set `true`, and it is true on the automated rows alone:
no behavior row rests on a manual checkpoint as its only coverage, which is
why the unrun OCR checkpoint does not hold the flag down.

## Which truth was verified by which command and which check

| Truth | Command | `check_*` |
|---|---|---|
| `adapter="asr"` is a named refusal pointing at the transcript adapter, writing nothing | `python3 tests/source_adapters_roundtrip.py` | `check_asr_registered_not_built` |
| The `body_asr` shape is frozen and tested before any backend exists, and a transcript-shaped body is rejected | same | `check_asr_locator_shape_frozen` |
| `body_asr` and `body_transcript` agree structurally apart from the index field's name | same | `check_asr_body_matches_transcript_body` |
| The schema addition is additive, proven by re-running four end-to-end checks against the amended document | same | `check_schema_addition_is_additive` |
| The checksum gate passes clean and was observed failing on a tampered artifact, a missing one, and a row naming a parked package | same | `check_vendored_manifest` |
| Eleven vendored artifacts match their recorded checksums | `python3 scripts/check_vendored.py` | exit 0, final line reports 11 |
| The README's new section names only registered subcommands | `python3 scripts/check_readme_commands.py` | exit 0, 52 registered |
| Every CI step is mirrored by a local gate or excused with a reason | `python3 tests/preflight_roundtrip.py` | 13 CI steps, 11 mirrored gates, 2 ci-only |
| Ten adapters, `ASR_BACKENDS` empty, `asr` at 0.0.0 | `python3 -c "import source_adapters as s; ..."` | prints `ten adapters registered` |
| The schema version did not move | `python3 -c "import json; ..."` | prints `schema additive` |
| The freeze file carries all seven required sections | the plan's own `for h in ...` loop | prints `freeze sections present` |
| The audit has at least 40 data rows | the plan's own row-count one-liner | prints `audit rows 61` |
| No `TBD` left in the validation map | `python3 -c "... assert 'TBD' not in t"` | prints `validation map filled` |
| Every schema document self-checks | `python3 schema_validate.py --all` | 20 documents clean |
| No repository-authored em dash | `python3 itembank.py guard .` | exit 0, `0 offending files` |
| `runtime.py`, `model.py`, `auditor.py` untouched **across the whole phase** | `git show --stat --format= <commit> -- runtime.py model.py auditor.py` for each of the eight 14C commits | empty for all eight |
| The whole suite | `for t in tests/*.py; do python3 "$t" || exit 1; done` | 88 of 88 pass |

## Deviations from the plan, each with its reason

1. **`scripts/preflight.py` gained a `vendored` gate**, which the plan's
   `files_modified` does not list. `tests/preflight_roundtrip.py` fails on any
   CI step that no local gate mirrors and `CI_ONLY` does not excuse, so adding
   the CI step alone broke that test. Mirroring it as a real local gate rather
   than excusing it in `CI_ONLY` is the right half of that choice: the check
   runs in under a second locally, and `CI_ONLY` is for things like the 40-line
   shell pipeline that genuinely cannot be mirrored.

2. **`check_vendored.py` verifies package rows against their pin lines, not
   against bytes.** The plan describes hashing every row's artifact, but the
   six wheels are installed from PyPI and are not committed to this tree, so
   there are no bytes to hash. Verifying the row against
   `deps/source-adapter-pins.txt` is the strongest check available and is
   better than a skip, because it catches a `VENDORED.md` row drifting from
   the pin file.

3. **`assets/vendor/codemirror/check-editor-boot.js` gets no table row.** It
   lives beside the vendored bundle but is repository-authored configuration,
   not a third-party artifact. Stated in `VENDORED.md` so its absence is a
   recorded judgement rather than an oversight.

4. **An inconsistency found and recorded rather than fixed.** `D-14C-3`
   records an agent choice, under Weibao's delegation, to pin `pypdf` at
   **6.16.2**; `deps/source-adapter-pins.txt` and `VENDORED.md` both still
   read **6.16.1** with 6.16.1's hash. Moving the pin means fetching the wheel
   and recording its own hash, which is a supply-chain action and not a text
   edit, so this plan did not make it. `pypdf` is the recorded page-level
   fallback and is wired into no code path, so nothing runs on either version
   today. Recorded in `VENDORED.md`'s update-cadence section and in the freeze
   file's reconsideration conditions.

5. **The hand-built ASR sidecar in the test needed a `sha256:`-prefixed
   fingerprint and a millisecond-precision timestamp.** Both are enforced by
   patterns in the frozen envelope that the plan's description of the test did
   not mention. Caught by the assertion going red twice, which is the schema
   doing its job on a hand-written document.

6. **The freeze file quotes per-commit diffs, not a range diff.** A range diff
   from a pre-phase commit attributes other phases' work to 14C, because other
   phases committed to `runtime.py` and `model.py` in the same window. The
   per-commit form is the honest measurement and it is empty for all eight 14C
   commits. Stated in the Evidence section so a later reader does not think
   the range form was avoided for a worse reason.

## What this plan did not do

It did not build an ASR backend, download a model, or construct a request:
`ASR_BACKENDS` is empty and `_extract_asr` returns before touching anything.
It did not move any pin, including `pypdf`'s. It adopted no package. It left
`runtime.py`, `model.py`, and `auditor.py` untouched, as did every other plan
in the phase.
