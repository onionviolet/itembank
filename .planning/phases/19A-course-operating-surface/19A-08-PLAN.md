# 19A-08 Plan: package recovery closure

## Objective

Close the package operation family through its existing HTTP routes and CLI
twins. Exercise the 17B course on a fresh local workspace. Classify
F-LOSS-1 through F-LOSS-5 against the package that was actually exported.
Repair any applicable silent loss before accepting the clean restore.

## Scope

- Keep `course_package.export_package`, `verify_manifest`, `restore_package`,
  and `loss_report_text` as the engine authorities.
- Reuse the four package request nodes, dispatchers, routes, CLI twins, and
  parity rows already present in the 19A spine.
- Repair manifest validation only where it rejects the frozen 17B object
  model.
- Add one route and CLI acceptance drill over `course_fixture_17b`.
- Attach the exercised manifest and its complete plain loss report.

No package schema migration is introduced. No new journal record type is
introduced. No assessment route, parser, scorer, evidence writer, or 19A-09
read route is changed.

## Loss classification

| Finding | Exercised result | Classification and authority |
|---|---|---|
| F-LOSS-1 | The source's operation history does not cross. One `provenance-not-carried` row names 82 applied entries. The destination contains only its own restore journal. | Disclosed exclusion. The Phase 14B clean-machine contract requires no shared journal. G10 permits unsupported capability only when the loss report names it. |
| F-LOSS-2 | Recorded rights do not cross. The same provenance row states that restored rights are unknown and remain restrictive. | Disclosed exclusion. Rights are operation-specific and are not transferable authority. Replaying an old grant on a new machine would invent authorization. |
| F-LOSS-3 | All seven `_attempts` files stay out and each has its own `unregistered-file` row. | Disclosed unsupported session state. The package carries accepted registered objects and evidence. These activity files have no registered package object. |
| F-LOSS-4 | `README.md`, `treatments.md`, the attempt files, and the media file are each named. | Disclosed exclusion. An unregistered file is not an accepted package object. The report gives the recovery action to bind it if it belongs to the course. |
| F-LOSS-5 | `media/lantern_moss_cycle.svg` is named in the loss report. The restored bank emits `media.declared_present_missing`. | Existing silence repair verified. The visual does not cross because it is unregistered. The package and lint surfaces both disclose the missing dependency before a learner meets a broken page. |

The exercised package contains no silent F-LOSS item. Carrying provenance,
rights, session state, or unregistered media would require a new durable
package or media-object decision. This plan does not invent one.

## Acceptance gate

1. `python3 tests/course_package_roundtrip.py` passes.
2. `python3 tests/course_ops_roundtrip.py` passes and prints the F-LOSS-1 to
   F-LOSS-5 surface classification line.
3. The attached manifest verifies 7 of 7 payload entries.
4. The clean restore recreates all 7 registered objects and all 47 evidence
   events.
5. The restore reports zero restore-time losses.
6. `python3 tests/surface_coverage_check.py` passes.
7. `python3 scripts/preflight.py --quick` passes.
8. `git diff --check` passes.

## Stop conditions

Stop rather than extending the format if a loss can only be repaired by
adding a manifest field, changing package identity, replaying rights, adding a
media object kind, or creating another journal or evidence authority.
