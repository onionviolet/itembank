# 19A-09 Verification

`python3 -m py_compile director.py surfaces/course_ops.py surfaces/daemon.py`

Result: pass.

`python3 tests/course_ops_roundtrip.py`

Result: pass. The complete operating-surface suite exercised every added read,
verified its schema fields and frozen engine result, and verified no read
changed a course fingerprint or revision.

`python3 tools/capabilities_manifest.py && python3 tests/capabilities_roundtrip.py`

Result: pass. The checked-in manifest is byte-identical to regeneration.

`git diff --check`

Result: pass.

`python3 tests/ia_route_roundtrip.py`

Result: pass. The suite completed in 3.36 seconds with 26 passed and 0 failed.

`python3 scripts/preflight.py --quick`

Result: pass. All ten mirrored quick gates passed. The Python, clean-tree, and
JavaScript suites are intentionally excluded by `--quick`.

No commit was made.
