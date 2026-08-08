---
schema_version: 1
open_count: 3
waived_count: 0
fixed_count: 0
total_count: 3
last_updated: 2026-08-08T04:45:12.364Z
---

# Broken Windows Ledger

> Cross-phase defect register. `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 02 | unrun-verify | surfaces/daemon.py |  | start_server()'s reserved-port/EACCES branch is proven present by source inspection only, not exercised end-to-end (cross-platform OS-refusal repro not attempted) | open |  | 2026-08-07T19:09:03.424Z |  |
| 2 | 02 | unrun-verify | surfaces/daemon.py |  | LAN cross-device reachability from a phone on the same wifi is a documented manual-only check (02-VALIDATION.md), not exercised this session | open |  | 2026-08-07T19:09:16.543Z |  |
| 3 | 02.1 | unrun-verify | .planning/phases/02.1-packaging-self-update-interop-export/02.1-06-SUMMARY.md |  | Success Criterion 5's manual LMS-import layer (D-04/D-05): no browser/computer-use tool is available in this executor's tool set to sign into sandbox.moodledemo.net and perform the real GIFT import; the automated golden-file layer (tests/gift_export_roundtrip.py) is complete and green, but the manual layer is deferred to a human. See SUMMARY.md's LMS Import Outcome section. | open |  | 2026-08-08T04:45:12.364Z |  |

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
  },
  {
    "id": 3,
    "kind": "unrun-verify",
    "phase": "02.1",
    "file": ".planning/phases/02.1-packaging-self-update-interop-export/02.1-06-SUMMARY.md",
    "line": null,
    "description": "Success Criterion 5's manual LMS-import layer (D-04/D-05): no browser/computer-use tool is available in this executor's tool set to sign into sandbox.moodledemo.net and perform the real GIFT import; the automated golden-file layer (tests/gift_export_roundtrip.py) is complete and green, but the manual layer is deferred to a human. See SUMMARY.md's LMS Import Outcome section.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-08T04:45:12.364Z",
    "resolved_at": null
  }
]
````
