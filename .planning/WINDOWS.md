---
schema_version: 1
open_count: 2
waived_count: 0
fixed_count: 0
total_count: 2
last_updated: 2026-08-07T19:09:16.543Z
---

# Broken Windows Ledger

> Cross-phase defect register. `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 02 | unrun-verify | surfaces/daemon.py |  | start_server()'s reserved-port/EACCES branch is proven present by source inspection only, not exercised end-to-end (cross-platform OS-refusal repro not attempted) | open |  | 2026-08-07T19:09:03.424Z |  |
| 2 | 02 | unrun-verify | surfaces/daemon.py |  | LAN cross-device reachability from a phone on the same wifi is a documented manual-only check (02-VALIDATION.md), not exercised this session | open |  | 2026-08-07T19:09:16.543Z |  |

````json
[
  {
    "id": 1,
    "kind": "unrun-verify",
    "phase": "02",
    "file": "surfaces/daemon.py",
    "line": null,
    "description": "start_server()'s reserved-port/EACCES branch is proven present by source inspection only, not exercised end-to-end (cross-platform OS-refusal repro not attempted)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-07T19:09:03.424Z",
    "resolved_at": null
  },
  {
    "id": 2,
    "kind": "unrun-verify",
    "phase": "02",
    "file": "surfaces/daemon.py",
    "line": null,
    "description": "LAN cross-device reachability from a phone on the same wifi is a documented manual-only check (02-VALIDATION.md), not exercised this session",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-07T19:09:16.543Z",
    "resolved_at": null
  }
]
````
