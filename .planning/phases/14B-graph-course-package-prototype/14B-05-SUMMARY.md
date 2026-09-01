# 14B-05 summary (RETROSPECTIVE)

**This is a retrospective record, written 2026-09-01** to close the
plan-summary pairing gap found by the 17B-01 precondition run
(`.planning/phases/17B-production-vertical-tracer/17B-PRECONDITION.md`).
Plan 14B-05 was executed 2026-08-27; its summary was never written at the
time. Everything below is reconstructed from the commit record (commits
`fbd7283` and `4c9d2e8`), `14B-DECISIONS.md`, `14B-FREEZE.md`,
`14B-TRACER-REPORT.md`, and the STATE.md 14B entries. Nothing here is a
new claim; where the record is silent, this file says so plainly.

## The checkpoint and how it was settled

Task 1 was a blocking `checkpoint:decision` gate: the package manifest
format and package shape. Per STATE.md, 14B-05's checkpoint was one of the
decisions waves 4 to 6 blocked on, answered by Weibao on 2026-08-27
through `.planning/DECISIONS-14B-DRIVER-2026-08-27.md` and recorded in
`14B-DECISIONS.md` under `## D-14B-4. Manifest contents and package
shape`: **option-a**, a plain directory tree with `zip` as optional
transport, the seven-key manifest (`schema_version`, `package_id`,
`created`, `course_object_id`, `state`, `entries`, `loss_report`) and the
five-key entry shape (`object_id`, `kind`, `revision`, `relpath`,
`fingerprint`).

Two settlement facts worth carrying:

1. **The checkpoint was asked twice.** On the first asking Weibao gave a
   standing directive ("make adaptability and modularity a important
   coding principle, (add to uservisio as well", recorded verbatim in
   `USER-VISION.md`) rather than selecting an option. It was not treated
   as an answer; the checkpoint was re-asked, and he then chose option-a
   explicitly. `14B-DECISIONS.md` records why the inference was refused.
2. **A decision-id transposition was hit and worked around.** D-14B-4 and
   D-14B-5 were first written with their numbers swapped; this plan's
   executor hit the mismatch, and the numbering note in `14B-DECISIONS.md`
   records the correction. Commit `fbd7283`'s message confirms the answer
   was already on record, so Task 1 needed no new decisions-file edit.

## What landed

- Commit `fbd7283` (2026-08-27), Task 2: `MANIFEST_KEYS`,
  `EVIDENCE_DIRNAME`, `EVIDENCE_FILENAME`, `LOSS_REPORT_FILENAME`,
  `LOSS_CATEGORIES`, `PACKAGE_RIGHT`, `PACKAGED_KINDS`, `ARCHIVE_FORMATS`,
  the fixed `LOSS_REASONS` strings, `build_manifest`, `loss_report_text`,
  the evidence export (zero-byte file when nothing matches), and
  `package.duplicate_relpath`. Diffstat: `course_package.py` +293/-22
  (net), `fixtures/corpus_14b.py` +102,
  `tests/course_package_roundtrip.py` +318 (new file).
- Commit `4c9d2e8` (2026-08-27), Task 3: `verify_manifest` (recomputing
  every fingerprint, never trusting the manifest's own value),
  `restore_package` refusing non-applied manifests, missing payloads, and
  fingerprint mismatches and returning both `losses` and `restore_losses`,
  evidence restore one event at a time through `evidence.append_event`,
  `read_manifest` refusing invalid JSON with `package.manifest_unreadable`,
  `extract_archive` iterating `infolist()` and never calling `extractall`
  (symlink refusal, `MAX_ENTRY_BYTES` ceiling, `safe_target` containment),
  and `export_package` gaining `archive="zip"` as optional transport.
  Diffstat: `course_package.py` +196, `fixtures/corpus_14b.py` +51,
  `tests/course_package_roundtrip.py` +279.

## Manifest key set as landed

The seven manifest keys and five entry keys named above, at
`PACKAGE_SCHEMA_VERSION` 1. These were subsequently frozen by
`14B-FREEZE.md` ("The seven-key package manifest and its five-key entry
shape") together with the five loss categories.

## Decisions made in execution, recorded in the commit rather than the plan

From `fbd7283`, two ordering decisions not in the plan text:

1. The rights gate runs BEFORE the external-link check, so a source nobody
   granted the package right for is reported rights-restricted whatever
   else is true of it; a permission problem is never misreported as a
   bookkeeping one.
2. `external-link` is decided from the FIRST applied journal entry for an
   object, not the registry's latest origin, because the registry projects
   the most recent operation and a later rights grant would otherwise
   erase the fact the source was ever linked.

From `4c9d2e8`, two implementation notes recorded as deliberate:

1. A second restore of the same package skips the journal write when the
   object is already present at the same fingerprint (still counted as
   verified); a row at a DIFFERENT fingerprint is left to
   `commit_operation`, which refuses it as a conflict.
2. The interrupted-export probe replaced the durability harness's
   sleep-and-kill with a deterministic `os._exit` inside the first payload
   write in a real subprocess, because a timed kill races interpreter
   startup and the assertion is about ordering, not the scheduler.
3. The oversized-entry assertion lowers `MAX_ENTRY_BYTES` for the test's
   duration rather than building a real hundred-megabyte declared size,
   and asserts the shipped ceiling of 104857600 separately as a constant.

## The plan's summary obligations this retrospective cannot fully meet

The plan asked this summary to quote the full loss report from one real
export verbatim, and to record the measured wall-clock time of one export
and one restore of the three-domain corpus. Neither figure was written
into any surviving artifact; the commits record exit codes, not timings or
report bodies. The record is silent, and this retrospective does not
invent the numbers. The clean-restore leg of the freeze gate
(`14B-TRACER-REPORT.md`, scenario `clean_restore: pass`, cited in
`14B-FREEZE.md`) is the surviving evidence that the drill ran and both
loss lists were returned. Timing measurements exist only in
`14B-TRACER-REPORT.md`'s single-run numbers, which that report itself says
are not budgets.

## The symlink-archive assertion

Not skipped. Commit `4c9d2e8` records, measured on darwin:
`tests/course_package_roundtrip.py` exits 0 with no SKIP line, so the
symlink-archive assertion ran rather than being skipped.

## Verification, per the commit record

`fbd7283`: `python3 tests/course_package_roundtrip.py` exit 0,
`guard .` 0 offending files, `tests/graph_roundtrip.py` still passing.
`4c9d2e8`: `course_package_roundtrip` exit 0 with no SKIP, `guard .` 0
offending files, `schema_validate.py --all` clean, and `graph_roundtrip`,
`identity_roundtrip`, `journal_roundtrip`, `evidence_roundtrip`,
`operations_roundtrip`, `agent_operation_roundtrip`, and
`durability_roundtrip` all passing. A full-suite run under the live-Anki
condition is recorded in `14B-FREEZE.md`'s evidence table.

## Why this summary was missing

The record is silent on why no summary was written on 2026-08-27. As with
14B-04, the plausible mechanism is the checkpoint-blocked wave being
driven commit by commit through the driver packet, with the summary step
dropped before the 14B-06 freeze work started later the same day. That is
an inference, and it is labeled as one.
