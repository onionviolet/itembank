# EXT-02: reuse validated descriptors for model transports

Status: executed pending parent review.
Depends on: EXT-01 commit `02b36b0` and its validated `build_registry` helper.
Context: `EXTENSION-DELIVERY-2026-09-06.md`, EXT-02.

## Promotion check

The EXT-01 descriptor is reusable without a transport-specific branch. Its
`handler` field accepts the existing four-argument transport functions as
callables and returns a fresh ordinary handler dictionary. That preserves the
existing `test_stub_third_backend_registration` pattern, which temporarily
adds and removes a transport. Constructing descriptors invokes no handler,
performs no I/O, and preserves the shipped no-call default.

## Bounded change

OWNER: model-adapter owner.

SYMBOLS: `model_adapter.TRANSPORT_ENTRIES`, `TRANSPORT_REGISTRY`,
`TRANSPORT_VERSIONS`, `TRANSPORT_DESCRIPTIONS`, and the focused model adapter
roundtrip test.

CHANGE: declare the two existing transports with EXT-01's six-field
descriptor. Build the existing mutable `TRANSPORT_REGISTRY` and two new
metadata maps from that declaration. Preserve order, handler identities,
versions, `_invoke` dispatch, default settings, and direct temporary mutation
in the third-backend test.

EXCLUSIONS: no settings schema, provider profile, transport implementation,
network invocation, model request or result envelope, scoring, evidence,
course operation, UI, dependency, loader, or external package change.

MIGRATION: none. The new metadata maps are process-local derived data.

UNDO: restore only the transport declaration hunk and remove this plan's
focused test assertions. No learner object or accepted revision changes.

## Acceptance

Run `python3 tests/model_adapter_roundtrip.py` and
`python3 tests/extension_registry_roundtrip.py`. Inspect the focused diff and
run `git diff --check`. The model suite must retain the mutation-based third
backend proof. No test may open a real network connection.

## Execution record

The promotion check passed. `python3 tests/model_adapter_roundtrip.py` exited
0 and retained the direct temporary third-backend registration. `python3
tests/extension_registry_roundtrip.py` exited 0. `git diff --check` exited 0.
The model suite uses fake subprocesses and loopback-only HTTP fixtures. No
real network call was made. No full preflight was run because this bounded
packet changes only the model declaration and its focused test while the shared
tree has unrelated in-flight edits.
