
- 2026-08-10 [out-of-scope, env flake] tests/daemon_roundtrip.py check_api_start_traversal failed: snapshot_dirs walks the whole %TEMP% root and concurrent processes (two long-running python PIDs during the run) created temp dirs in the snapshot window. Unrelated to plan 03.1-04 changes. Re-run when no concurrent agents are active.
# Deferred Items -- Phase 03.1

Out-of-scope discoveries logged during execution (never auto-fixed).

- 2026-08-10 [out-of-scope, env flake] `tests/daemon_roundtrip.py`
  `check_api_start_traversal` failed once in the full-suite run:
  `snapshot_dirs` walks the whole `%TEMP%` root, and concurrent processes
  (two long-running python PIDs observed during the run) created temp dirs
  inside the snapshot window. Unrelated to plan 03.1-04 changes; re-run
  when no concurrent agents are active.
