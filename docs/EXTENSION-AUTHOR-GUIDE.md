# First-party extension author guide

This repository accepts first-party extensions at named registry seams. A
declaration makes an implementation registered. It does not install code,
configure a profile, grant permissions, or prove that a dependency is usable.
There is no external extension loader.

## Use an existing seam

Source adapters add one row to `source_adapters.SOURCE_ADAPTER_ENTRIES`.
Model transports add one row to `model_adapter.TRANSPORT_ENTRIES`. Use the
existing `extension_registry.build_registry` descriptor shape and preserve the
owning module's mutable registry for its existing tests.

Every row names a callable, semantic capability, degraded fallback, and the
focused check command. Do not add discovery code, imports from strings, or a
second catalogue.

## Report state precisely

- **Registered** means the callable is present in the live first-party registry.
- **Configured** means an accepted local setting selects it for an operation.
- **Available** means the owning runtime has verified the needed executable,
  dependency, endpoint, or gate for this invocation.
- **Disabled** means an explicit setting or policy prevents use.

These are separate facts. A descriptor or version string cannot establish
configuration, installation, availability, or permission. When a fact was not
checked, leave it unknown rather than guessing. The machine-readable
`capabilities.json` manifest reports registrations only. Its diagnostic helper
accepts the other state sets explicitly and never derives them from metadata.

## Verification and fallback

Add fidelity and refusal coverage to the owning roundtrip test. Exercise the
missing-dependency or disabled path and verify the existing typed refusal or
static fallback. Do not open a real network connection in a focused test.
Inspect the relevant schema before proposing a new medium or transport.
