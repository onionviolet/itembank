# 19A-08 Verification

## Exercised recovery

The source was a fresh temporary copy of `course_fixture_17b`. Export ran
through `itembank course export-package`. Verification and restore ran through
the same package dispatcher and its CLI twin. The automated acceptance gate
also reads the loss report and restores through the HTTP routes.

The attached package id is `83e8bd0772bc482d`. Its timestamp is
`2026-09-07T02:24:00.196Z`. The manifest and loss report are evidence from this
specific run. They are not canonical package fixtures.

Observed results:

| Check | Result |
|---|---|
| manifest state | `applied` |
| payload verification | 7 of 7 |
| missing payloads | none |
| fingerprint mismatches | none |
| registered objects after restore | 7 of 7 |
| evidence after restore | 47 of 47 |
| restore-time losses | none |
| remote egress | none |
| restored bank lint | 8 items, 0 errors, 1 warning |
| media warning | `media.declared_present_missing` |

## Automated gates

| Command | Result |
|---|---|
| `python3 tests/course_package_roundtrip.py` | PASS |
| `python3 tests/course_ops_roundtrip.py` | PASS |
| `python3 tests/three_domain_tracer.py` | PASS, 5 scenarios passed including clean restore |
| `python3 tools/restore_drill_17b.py --commit HEAD --workdir <fresh-temp>/run` | PASS at committed baseline `9ee1dd9`, 7 objects and 47 evidence events carried, 12 loss rows |
| `python3 tests/surface_coverage_check.py` | PASS, 98 commands and 82 routes classified, 52 of 82 meaningful cells reached |
| `python3 scripts/preflight.py --quick` | PASS, every selected gate passed |
| `python3 -m json.tool evidence/19A-08-manifest.json` | PASS |
| `git diff --check` | PASS |

The course operation test performs the loss classification against the 17B
course. It uses the CLI export, HTTP loss reader, HTTP clean restore, and CLI
lint. It asserts restored state from disk rather than trusting the manifest's
claim.
