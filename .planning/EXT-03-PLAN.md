# EXT-03: extension author guide and capability diagnostics

Status: implemented, pending parent review.
Depends on: EXT-01's `extension_registry.build_registry` and EXT-02's reuse for
source adapters and model transports.

## Bounded contract

OWNER: `tools/capabilities_manifest.py` and its disclosure test.

CHANGE: add `capability_diagnostics()` and a generated `capabilities` section
to the existing manifest. Add a first-party author guide that distinguishes
registered, configured, available, and disabled. The diagnostic accepts caller
facts explicitly. It never infers installation or activation from metadata.

EXCLUSIONS: no second discovery catalogue, package loader, settings mutation,
course operation, UI, transport behavior, scoring, evidence, or EXT-04 work.

## Acceptance

Run `python3 tests/capability_diagnostics_roundtrip.py`,
`python3 tests/capabilities_roundtrip.py`, and `git diff --check`. Regenerate
`capabilities.json` and confirm the manifest remains byte-stable.

## Recovery

Remove the diagnostic helper, manifest field, focused test, guide, and this plan.
No learner object, accepted revision, or migration is affected.
