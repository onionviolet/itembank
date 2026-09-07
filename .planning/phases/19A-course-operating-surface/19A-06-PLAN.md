# 19A-06 Plan: blueprint and audit

## Objective

Expose the settled blueprint and audit engine functions through the existing
course-operation request document, dispatcher, HTTP routes, CLI twins, and
surface coverage grid.

## Scope

- `bind_blueprint` is the sole write. It records the blueprint through the
  existing course mutation and compare-and-swap journal path.
- `blueprint_gate`, `audit`, and `staleness` are read operations. They must not
  change the course sidecar or invent assessment authority.
- Reuse the existing operation schema and route parity conventions.
- Keep `journal.OPERATION_TYPES` unchanged and add no new durable object.

## Acceptance gate

The route and CLI twin each bind a blueprint and report a new revision and
fingerprint. Each read operation returns its published result shape and leaves
the bound fingerprint unchanged. Schema validation, route parity, and surface
coverage checks pass.

