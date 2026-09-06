<!-- generated-by: gsd-doc-writer -->
# Testing

## Test framework and setup

Python tests are self-contained executable scripts that use the standard library. They do not require pytest. JavaScript editor tests use Node.js and the pinned lockfile under `tests/js/`.

## Running tests

Run one focused Python test:

```bash
python tests/protocol_roundtrip.py
```

Run the fast contributor gates:

```bash
python scripts/preflight.py --quick
```

Run every portable CI gate before a consequential push:

```bash
python scripts/preflight.py
```

List the preflight-to-CI mapping:

```bash
python scripts/preflight.py --list
```

## Writing new tests

Place Python tests in `tests/` and follow the existing `*_roundtrip.py` naming convention. Tests must be deterministic, self-contained, and safe to run directly with Python. Write generated files to a temporary directory. A test must not leave the repository dirty.

Use synthetic fixtures under `fixtures/`. Never add a real learner bank or learner evidence. When changing a published payload, update and validate the corresponding file under `schemas/`.

## Coverage requirements

No numeric line or branch coverage threshold is configured. Acceptance is behavior-based through roundtrip tests, schema validation, fixture checks, guard checks, and the preflight mirror of CI.

## CI integration

`.github/workflows/ci.yml` runs on every push and pull request. It validates fixtures, schemas, Python roundtrip tests, JavaScript editor behavior, generated assets, repository cleanliness, skill-tree parity, and path-leak protections.

CI has two checks that local preflight deliberately does not reproduce. `python scripts/preflight.py --list` names them and explains why they remain CI-only.
