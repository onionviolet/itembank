# A2 course shelf and restart resume repair

Date: 2026-09-12. Base inspected: `e7c242a89d16ecd2d715a0cb6b7197ab285bbff6`.
Status: implementation and A2 deterministic gates complete. Integration pending.
Owner: A2 implementation task. A1 owns integration and shared state updates.

## Findings and scope

F1, reproduced and repaired: a populated synthetic course with an active
canonical sitting rendered Start on the real shelf route. The new regression
failed at its first active-session shelf assertion before the repair.
`course.read_course` does not supply `resume_cue`, and `_healthy_card` defaulted
the missing value to Not started. This confirms the earlier walkthrough's
cause without treating that screenshot as current evidence.

F2, reproduced and repaired: after submitting and restarting the daemon,
opening the same quiz created a second sitting. The new regression failed at
`restart created another sitting`. The coordinator explicitly extended A2's
ownership to the daemon's session-restoration symbols on 2026-09-12. No other
daemon behavior or production module was assigned to A2.

F3, resolved during verification: the first restart repair also intercepted
explicit scoped `serve` launches. The serve regression failed because changing
the seed no longer changed selection. Recovery now applies only to the
workspace daemon. Explicit serve keeps its own announced mode, seed and id.

Changed paths:

- `surfaces/ia.py`: read-only cue projection and CTA selection.
- `surfaces/daemon.py`: `_saved_quiz_session` and its call under the existing
  `_ensure_quiz_session` lock.
- `tests/course_resume_roundtrip.py`: disposable synthetic route regression.
- This result artifact.

`tests/ia_route_roundtrip.py` remains unchanged. No staging, commits, pushes,
branch switches, real learner writes, scoring changes, or schema changes.

## Resulting behavior

| Observed state | Shelf cue and action |
| --- | --- |
| No recorded sitting or evidence | Not started, Start |
| Latest sitting per bank active | Session in progress, Resume |
| Latest recorded sittings complete | Recorded sessions complete, Open |
| Session unreadable or unsupported | Session status unavailable, Open |
| Evidence survives a missing session | Previous activity recorded, Open |

The completed label concerns recorded sittings, not completion of a course.
The existing corrupted-course card and its recovery links remain unchanged.
Explicit client-provided cues remain supported. Missing projection modules
degrade to unavailable instead of asserting a fresh start.

The daemon uses the existing session index and newest-session-per-bank helper,
the runtime session reader, the published session schema, and existing
selection evidence. It restores the same id, selected items, pending cursor
and responses. A completed sitting remains complete. Invalid files, invalid
positions, mode mismatches, changed selections and later bank modifications
are refused before creating or advancing a sitting. The latest completed
sitting does not revive an older active one.

## Verification evidence

| Gate actually run | Result |
| --- | --- |
| `python3 tests/course_resume_roundtrip.py` | Pass on final code |
| `python3 tests/daemon_roundtrip.py` | Pass, 78 checks on final code |
| `python3 tests/serve_roundtrip.py` | Pass on final code, six scored items and evidence checks |
| `python3 tests/ia_route_roundtrip.py` | Pass, 26 checks on final code in isolated rerun. The preceding parallel run had a connection timeout in walkthrough interruption. |
| `python3 scripts/preflight.py --quick` | All ten executed gates passed. Tests, clean and JS skipped by quick mode. |
| `git diff --check` for owned production paths | Pass |

The dedicated regression drives real loopback HTTP shelf and quiz routes.
It submits through the canonical session adapter, leaves the course, returns,
restarts the process and returns again. The same session and item 2 remain.
Whole-fixture byte snapshots around shelf GETs prove no added files or changed
session, evidence, course or journal bytes. Corrupt-session refusal also leaves
the fixture unchanged. Completion, future schema and evidence-only labels are
checked through rendered HTTP HTML. Permission failure, missing projection,
invalid cursor, invalid indices, mode mismatch and changed-bank refusal also
have in-process checks. A latest-completed-over-older-active case is covered.

This is served HTML and canonical-state verification. No browser automation,
visual review, touch review or screen-reader review was performed. No human
acceptance is claimed. No independent A2 reviewer was required or spawned.
The builder inspected the actual owned diff. Large modules were read by
symbol windows, not in full.

One run hit A1's in-flight `_file_descriptor` NameError while creating the
synthetic course. The rerun passed after A1's helper landed. This was distinct
from A2's reproduced serve regression. A1 is separately rerunning its nested
evidence suite after A2 stopped production edits.

## Limits, recovery and handoff

The daemon restores sessions already addressable in its workspace `_attempts`
index. The shelf can also report course-local CLI sessions, but this change
does not add those external locations to daemon API addressing. It creates no
second progress store and transfers no evidence.

Sessions do not pin a bank revision. Selection identities and file modification
time provide a conservative restart check, not proof of content identity.
A copied or touched bank may require review even if its bytes are unchanged.
Legacy sessions without selection evidence are not silently resumed. An
unreadable workspace session cannot be assigned safely to a course, so it can
degrade other course cues and block automatic starts until reviewed.

All test data lived in dedicated temporary directories and was removed by the
tests. To undo the code repair, remove only the A2 hunks and its new test and
report after inspecting current ownership. No learner-data migration or undo
operation is needed. Preserve all other writers' dirty changes.

NEXT ACTION: A1 should integrate the stable A2 diff with the other lanes and
run A4's populated-course walkthrough and combined validation. This report
supersedes the old shelf observation within the tested scope. A1 owns shared
index reconciliation and successor creation. No A2 successor is created.
