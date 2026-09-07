# 19A-07 Plan: migration settlement and undo

## Objective

Complete the existing migration settlement surface so a reviewer can accept
or reject an append-only objective migration through the route and CLI twins,
then restore the exact pre-settlement sidecar bytes through the existing
operation reversal authority.

## Scope

- Keep proposal creation in the four objective-editing operations shipped by
  19A-03.
- Keep acceptance and rejection in `graph.accept_migration` and
  `graph.reject_migration` through the existing course-operation dispatcher.
- Attach one operation id to the applied compare-and-swap entry that settles
  the proposal. Do not append a second acceptance entry.
- Reuse `director.reverse_operation` and `journal.undo` for recovery. Add no
  migration-specific restore path and no journal operation type.
- Preserve every objective row, migration row, and evidence identity.

## Acceptance gate

The route and CLI twin each settle a proposal, record exactly one applied
operation-identified CAS entry with a restore before-image, and reject stale,
self-settled, unknown, empty-rationale, and already-settled requests without
changing the sidecar. Reversing that operation restores the exact original
valid sidecar bytes. Schema, route parity, graph, and surface coverage checks
pass.
