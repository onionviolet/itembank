# 19A-07 Verification

## Targeted gates

`python3 tests/course_ops_roundtrip.py`

Result: pass. The route and CLI twin each settled a migration through one
operation-identified CAS entry. Self-settlement, empty rationale, unknown id,
stale fingerprint, and repeat settlement were refused without changing the
course. The shared reverse-operation path restored the exact original valid
sidecar bytes.

One later run reported `F1 route accepted the dot-directory id '..'` in the
already-present 19A-08 package-path section after every migration check passed.
The immediate rerun passed in full. No 19A-08 code was changed or claimed by
this plan.

`python3 tests/surface_coverage_check.py`

Result: pass. All 98 commands and 82 routes were classified. Objective undo is
now reached through migration settlement and the existing reverse-operation
surface. The grid reports 52 of 82 meaningful cells reached.

`python3 tests/graph_roundtrip.py`

Result: pass. The graph suite retained the three migration states, the two
reviewer settlement authorities, append-only identity rows, and the refusal of
the legacy generic state setter.

`python3 scripts/preflight.py --quick`

Result: pass. Every quick gate that ran passed: lint, broken fixture, build,
guard, mirrored skills, README commands, schemas, vendored dependency, path,
and summary checks. The quick mode skipped the full Python suite, clean-tree
gate, and JavaScript suite by design.

No claim is made about the pre-existing intermittent daemon concurrency timeout
documented in `19A-CONTEXT.md`.
