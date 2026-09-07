# 19A-07 Summary: migration settlement and undo

## Why this summary exists

Completed the migration operation family that arrived partially with the
19A-06 surface expansion.

- Kept the existing `accept_migration` and `reject_migration` request nodes,
  routes, CLI twins, dispatcher entries, and graph authorities.
- Added an optional operation id to both published requests and CLI commands.
  A fresh opaque id is minted when the caller omits one.
- Attached that id to the same applied compare-and-swap journal entry that
  changes the proposal state. No second acceptance entry is appended.
- Routed undo through the existing `course reverse-operation` surface, which
  reaches `director.reverse_operation` and `journal.undo`.
- Proved both acceptance and rejection leave objective and evidence identity
  untouched, and that undo restores the exact pre-settlement sidecar bytes.
- Moved objective undo from the coverage gap list into the reached surface
  grid.

No migration state, graph format, assessment authority, evidence transfer,
journal operation type, or migration-specific restore path was introduced.
