---
phase: 18-external-user-v1
plan: 03
subsystem: infra
tags: [gates, onboarding, privacy, readme, transcript]

requires:
  - phase: 18-external-user-v1
    provides: "18-01's shipped-artifact evidence and signing record; 18-02's capabilities.json and README step 0"
provides:
  - "18-GATES.md, the six-criterion A10 record plus the deferred second-person closing row"
  - "18-COLD-AGENT-TRANSCRIPT.md, the A10 check 2 fixture, two runs kept"
  - "the fresh-install privacy evidence (opt_in, no request, degraded loop proven)"
  - "the D-06 scope-honesty copy and eight cold-agent-driven README fixes"
affects: [18-close]

requirements-completed: [A10-C2, A10-C3, A10-C4, A10-C5, A10-C1 (evidence recorded; rebuild gap stands per 18-01), A10-C6 (three of four states provoked; remainder honestly deferred)]

completed: 2026-09-01
status: complete-pending-human-gate
---

# Phase 18 Plan 03 Summary: the A10 gates record, the cold-agent transcript, and the fresh-install check

Executed 2026-09-01 under the standing directive of the same date: human
tests deferred, every agent-executable check run in full, nothing human
self-certified. `python` is absent on this host; every command ran as
`python3` (Python 3.14.6), the same recorded deviation as 18-01 and 18-02.

## Gates row states (detail and quotes in 18-GATES.md)

| Row | State | Evidence pointer |
|---|---|---|
| 1 Install without folklore | passed with the recorded rebuild gap: rebuilt-on-this-host is not achieved | 18-01-SUMMARY.md (shipped sidecar sha256 8b019efd6b6db4b2f3fc3426c2b69d98411495154905aa44395316512ac9684e, commit 0b243c8), 18-DECISIONS.md dated signing entry, README install and download copy |
| 2 Agent-guided onboarding | passed, two runs, rerun after fixes | 18-COLD-AGENT-TRANSCRIPT.md |
| 3 First-run self-explanation | passed on the served UI (walkthrough offer plus bundled sample course); packaged-shell launch folded into row 7 | the recorded first-run observation in 18-GATES.md criterion 3 |
| 4 Scope honesty | passed | README diff in this commit; guard exit 0; check_readme_commands exit 0 |
| 5 Privacy defaults | passed | the verbatim config and disclosure lines and the empty connection-attempt logs in 18-GATES.md criterion 5 |
| 6 Recovery | three of four states provoked and passing; quarantine documented-but-not-provoked; packaged-artifact provocation owed with the rebuild | the recorded error copy in 18-GATES.md criterion 6 |
| 7 Second-person cold install | DEFERRED, owed to Weibao (2026-09-01), not certified; the phase close is conditional on it | 18-GATES.md row 7 |

## Fresh-install evidence lines, verbatim (Task 2)

Staged: the repo tree minus `.git`, `itembank.json`, `_attempts`, and
`.planning`, copied to a temp directory outside the repository; no
`itembank.json` present. Monitoring: a `sitecustomize.py` wrapping
`socket.socket.connect` and `socket.create_connection` to log every
outbound attempt; a second variant raising `OSError` on non-loopback
connects to simulate the network unplugged.

- `python3 itembank.py config` exit 0, the update_policy row:
  `update_policy              string    opt_in|check_on_launch         'opt_in'       'opt_in'       read by this phase`
- `python3 itembank.py disclosure` exit 0:
  `"show": true,` `"notified_at": null,` with the copy "itembank will
  check GitHub for a new version at most once every 24 hours. Nothing but
  the request leaves this machine. Set \"update_policy\": \"opt_in\" in
  itembank.json to turn it off. This notice appears once."
- Connection-attempt log after config, disclosure, lint, and a serve
  startup, scored GET, and shutdown: empty.
- Network blocked: lint exit 0; `GET /` on the served sitting returned
  200; clean shutdown; blocked-attempt log empty. The loop worked with
  the network unplugged.
- `python3 itembank.py update` under the block printed "Could not reach
  GitHub to check for updates (offline, or the connection failed). Try
  again later." and exited 0, with exactly one blocked attempt logged,
  made only because the user ran the update command.
- D-13 stays repo-only: the checked-in `itembank.json` (check_on_launch,
  dogfooding) is absent from a fresh install, so the schema default
  `opt_in` holds for a stranger.

## Cold-agent transcript: defects and rerun count (Task 3)

Rerun count: one rerun (two runs total, both kept in
18-COLD-AGENT-TRANSCRIPT.md). Run 1 completed the full walkthrough and
surfaced nine confusion points; run 2, a second cold agent against the
fixed README, completed cleanly and confirmed the fixes.

README defects fixed (all in README.md, this plan's file list):

1. The "whole format" sample did not parse at all (indented markers,
   single-line options, inline `[TYPE: short]`); found by this executor's
   own fresh-install pass, replaced with a lint-clean sample (verified:
   the sample extracted verbatim from the README lints exit 0).
2. `python` versus `python3`: a quick-start interpreter note now covers
   the whole README and Path 2 uses `python3`.
3. The first-launch update-notice sentence now says first daemon launch,
   once per machine, and that bank commands never check.
4. Errors-block-warnings-advise expectation set beside the sample, with
   the three expected first-run warnings named.
5. `response_schema` documented as the authoritative answer shape.
6. Practice-mode `action: "hold"` (wrong answer does not advance)
   documented in the agent-driver contract list.
7. The submit response's `next` nesting documented.
8. Skill-count and type-count inconsistencies corrected ("five
   playbooks" and the stale "seven types" line).

Named defects routed onward, not patched here (out of this plan's file
list): N-01 `spec`'s item-type numbering is out of order (1-6, 8, 7);
N-02 `submit` accepts wrong-shaped answers as `accepted: true, score:
false` and consumes an attempt; N-03 `start`'s selection trace verbosity.
Recorded in the transcript header.

## Second-person cold install (Task 5)

DEFERRED, owed to Weibao, dated 2026-09-01, per the standing directive of
the same date deferring human tests. Not certified; no defects can be
reported because the install has not happened. The phase does not report
complete while 18-GATES.md row 7 is pending; that row also absorbs the
real-machine checks this host could not perform (packaged-shell first
run, Gatekeeper and SmartScreen dialogs as actually seen, packaged-
artifact error provocation).

## Truths verified, by command or observation

- "Every one of the six A10 criteria has a gates row with a concrete
  check and an evidence pointer": 18-GATES.md, each row carries evidence
  or an explicit deferred/pending state; no row is a bare claim.
- "A fresh install resolves update_policy to opt_in and makes no network
  request without disclosure": the verbatim lines above, plus the empty
  socket-monitor logs.
- "The cold-agent transcript exists, redacted, and a failed walkthrough
  became fixed defects and a rerun": 18-COLD-AGENT-TRANSCRIPT.md, header
  defect list, two runs.
- "The phase closes only on a real second-person cold install":
  18-GATES.md row 7 DEFERRED and blocking; nothing here certifies it.
- Repository checks at commit time: `python3 itembank.py guard .` exit 0;
  `python3 scripts/check_readme_commands.py` exit 0; chr(8212) scan of
  README.md, 18-GATES.md, and this file clean.

## Deviations from plan

1. `python` ran as `python3` throughout (host has no `python`).
2. Task 2's `powershell` command block ran as the equivalent POSIX
   commands (this is a macOS host); the monitoring method (socket-layer
   logging and blocking) substituted for physically unplugging the
   network, and is recorded with the evidence.
3. The criterion 6 provocations ran against the repo runtime and the
   launcher shims, not the packaged Windows artifact, which cannot
   execute on this arm64 macOS host; recorded inside the row per the
   18-01 rebuild gap, not silently.
4. 18-COLD-AGENT-TRANSCRIPT.md contains em dash characters inside the
   two verbatim agent narrations only, under the prose rule's
   verbatim-quotation exception, stated in its header; the framing prose
   and every other file this plan touched scan clean.
5. Task 5's human checkpoint recorded as DEFERRED per the 2026-09-01
   standing directive rather than executed; the phase close stays
   conditional on it.
