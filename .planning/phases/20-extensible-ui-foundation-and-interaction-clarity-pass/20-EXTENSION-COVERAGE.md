# Phase 20 extension coverage

**Current source:** `EXTENSION-DELIVERY-2026-09-06.md`
**Phase 20 owner:** The UI portion of EXT-04
**Checked:** 2026-09-08

| Extension packet | Current state | Phase 20 obligation | Closure evidence |
|---|---|---|---|
| EXT-01 first-party registration | Implemented before Phase 20 | Preserve source-adapter registration and mutation-based test isolation | Existing source-adapter tests plus full preflight remain green |
| EXT-02 model transport descriptors | Implemented before Phase 20 | Preserve the third-backend registration and zero-network default | Existing model-adapter tests plus full preflight remain green |
| EXT-03 author guide and capability diagnostics | Implemented before Phase 20 | Keep registered, configured, available, and disabled states distinct in Settings and diagnostics | Capability-manifest and Settings fixtures show all four states |
| EXT-04 presentation profiles | Phase 20 owner | Ship Field Guide and Trajectory Deck over one semantic renderer | Same-state profile parity, migration, fallback, and removal recovery pass |
| EXT-04 appearance themes | Phase 20 owner | Preserve `theme`, `accent`, and all seven shipped `look` values as independent appearance axes | Cross-product settings and contrast tests pass without preference reset |
| EXT-04 UI capability adapters | Phase 20 owner | Register the existing question-response renderer and every migrated surface through bounded declarations | Each declaration names identity, version, roles, operations, modes, input, fallback, unavailable state, migration, tests, and removal recovery |
| EXT-04 Agent composition | Phase 19B implemented, Phase 20 presents | Apply shared profile framing without moving proposal acceptance or undo authority | Agent states and forms remain route-identical across both profiles |
| EXT-04 MCP projection | Phase 19E implemented | Preserve generated tool projection. Phase 20 exposes capability state only where Settings or diagnostics already do | MCP suites and full preflight remain green. No UI-generated tool table appears |
| EXT-05 external packages | Deferred decision gate | Keep metadata-only inspection, isolation, compatibility, acquisition, grants, rollback, and recovery questions visible. Do not execute external packages | Phase 20 verification confirms no loader, runtime fetch, dynamic import, live reload, or package-executed code was added |

Task 1 evidence is the versioned `presentation.surface_adapter_manifest()`.
It names the response renderer, course areas including Agent, Sources, Map,
Evidence, and Build, Settings, plus the compatibility disposition for authoring,
export, and MCP output. The manifest exports `external_loader: false`. The
settings roundtrip also scans the Phase 20 UI foundation for loader primitives.

## Appearance axes preserved

- Presentation profile: `field-guide` or `trajectory-deck`.
- Home mode: shipped `shelf`, `next-action`, `agent`, or `split`.
- Look: shipped `classic`, `editorial`, `neo`, `cash`, `console`, `soft`, or `contrast`.
- Theme: system, light, dark, or OLED where currently supported.
- Accent, density, contrast, and motion remain independently recoverable settings.

Changing one axis must not silently rewrite another. A deliberate one-time look preset may continue to suggest a mode or accent through the existing settings path, but the learner can change either afterward without changing the look or presentation profile.
