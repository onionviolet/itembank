# Phase 20 verification

**Checked:** 2026-09-08
**Verdict:** Blocked from full closure
**Scope:** Plan 20-05 Task 3 audit closure and deterministic verification

Every current audit and inspiration row has a terminal disposition, evidence,
an exact blocked condition, or a named external or human owner. Phase 20 cannot
honestly close because the stylesheet suite still names owed off-scale modules,
the required full daemon transition suite remains unavailable in this runner,
and the blocking human visual, touch, and screen-reader checkpoint remains
owed.

## Requirement coverage

| Requirement | Deterministic evidence | Current result |
|---|---|---|
| FLOW-01 | Home, IA-route, profile, lifecycle, and transition fixtures preserve exact next actions, course context, Back, Home, interruption, and recovery | Focused deterministic legs pass. The required full daemon result remains unavailable because the runner terminates it at about 30 seconds |
| FLOW-02 | Profile course-to-lesson-to-practice context, serve lifecycle, and route parity checks | Passed for the Phase 20 slice |
| CAP-02 | Versioned `presentation.surface_adapter_manifest()`, settings migration and removal recovery, plain fallback, and no-loader checks | Passed |
| ACTIVITY-01 | Purpose precedes response format across every shipped purpose and response type | Passed |
| ACTIVITY-03 | Serve, hint, Agent, MCP, and profile parity checks preserve runtime scoring and disclosure authority | Passed |
| A11Y-01 | Deterministic keyboard, focus, target, reflow, fallback, and state checks | Automated leg passes. Human touch and screen-reader acceptance is skipped and not certified |
| VISUAL-01 | Both profiles render the same semantic state with separate hierarchy and stable routes | Deterministic leg passes. Weibao's aesthetic acceptance is skipped |
| VISUAL-02 | Settings and profile fixtures preserve independent profile, home, look, theme, contrast, accent, density, and motion axes | Passed |

The repository-wide requirement statuses remain owned by their canonical
phases. This record verifies only Phase 20's contribution and does not mark the
global requirement ledger complete.

## Decision coverage

`gsd-sdk query check.decision-coverage-plan` passed with 14 of 14 trackable
decisions covered. D-01 through D-06 are exercised by the semantic hierarchy,
profile, activity, transition, and degraded-state fixtures. D-07 and D-13 are
covered by the versioned adapter manifest and compatible surface adoption.
D-10 closes every audit row without hiding blockers. D-11 and D-12 are recorded
in the inspiration and home comparison matrices. D-14 preserves EXT-01 through
EXT-03, completes the bounded UI declaration for EXT-04, and adds no EXT-05
loader.

## Audit and inspiration coverage

`20-AUDIT-CROSSWALK.md` now gives every current finding one of these terminal
states: fixed and deterministically verified, human owed with an automated leg,
externally owned, or blocked by an exact condition. No owned deterministic
finding remains merely deferred.

`20-INSPIRATION-MATRIX.md` records an acceptance result for every adapted or
rejected pattern. Resume and Shelf are retained. Agenda and Path remain
registered prototypes because the human comparison was skipped. PrairieLearn
runtime generation, blended progress, engagement mechanics, authority-bearing
frontend slots, and external package behavior remain absent.

## Deterministic evidence

Evidence inherited from the accepted working tree and rerun for Task 3 is
listed separately. A command is not called green unless it exited zero in this
checkout.

| Command | Result |
|---|---|
| `gsd-sdk query check.decision-coverage-plan <phase-dir> <context>` | Passed, 14 of 14 decisions covered |
| `python3 tests/settings_roundtrip.py` | Passed |
| `python3 tests/component_primitives_roundtrip.py` | Passed, 17 primitives |
| `python3 tests/presentation_profiles_roundtrip.py` | Passed |
| EXT-01 through EXT-04 preservation suites | Passed: extension registry, source adapters, model adapter, capability diagnostics, Agent operation, MCP, course operations, and surface roundtrips |
| Home, visual-accessibility, serve, IA-route, hint, and stylesheet suites | Passed. The visual suite reported 13 positive layout gates. The stylesheet suite also reported Settings, Day, and Study as off-scale and owed rather than done |
| `python3 scripts/preflight.py --quick` | Passed every enabled gate. Tests, clean, and JS were skipped by quick mode |
| `git diff --check` | Passed |
| `python3 tests/daemon_roundtrip.py` | Unavailable in this runner. The earlier picker-timeout cause was repaired in the shared checkout. The runner now terminates the full suite at about 30 seconds before it returns a result. This is owed, not passed |

`20-TRANSITION-GATES.md` remains the exact owner of the unavailable full daemon
result. Its 11 transition families have passing focused contract legs, but its
overall gate remains incomplete.

## Human and sampling results

### Implementation audit link, 2026-09-08

The local normal flow exercised visible Courses, Sit sample_bank, a correct
table submission, feedback pause, Continue, Home, command-palette Settings,
and both unsaved profile previews. The feedback pause held Item 1 of 6 with
the runtime-issued correct verdict and advanced only after Continue. The audit
reopened the crosswalk's locked-hint claim because the live page showed all six
tiers. The bounded repair now exposes only the next tier and one help action.
`tests/serve_roundtrip.py`, `tests/presentation_profiles_roundtrip.py`, and
`tests/settings_roundtrip.py` passed after the repair. Profile previews now
show structurally distinct compositions on identical state without saving a
profile. This is direct implementation evidence, not Weibao's visual, touch,
or screen-reader acceptance.

The scoped local fixture did not contain a course object or a lesson body.
Its visible Courses control returned the shelf, and Read sample_bank rendered
the honest "No lesson yet" state. Course overview and lesson-to-practice could
not be directly audited in this launch. Touch hardware and a screen-reader
setup were also unavailable. Their deterministic legs remain the existing
profile, IA-route, visual-accessibility, and transition fixtures.

No real Math 1400 sitting was run. Human visual comparison, touch-device
review, screen-reader review, 200 percent text judgment, 400 percent zoom
judgment, and aesthetic acceptance remain owed to Weibao at Task 2. They are
not passes and this document does not certify accessibility or usability.

Synthetic fixtures cover both profiles, all shipped home modes, registered
Agenda and Path prototypes, all response types, desktop and phone breakpoints,
degraded states, no-script fallback, offline behavior, profile migration, and
adapter removal recovery. Large modules were sampled by symbol and narrow line
windows rather than read whole: `surfaces/daemon.py`, `tests/daemon_roundtrip.py`,
`surfaces/presentation.py`, `tests/ia_route_roundtrip.py`, and
`tests/source_adapters_roundtrip.py`.

## Rollback and remaining risk

Rollback for Task 3 is limited to restoring this verification file and the
terminal-disposition edits in `20-AUDIT-CROSSWALK.md` and
`20-INSPIRATION-MATRIX.md`. No runtime, parser, scorer, route, evidence,
settings, Canvas, catalog, or external service state changes in Task 3.

The unresolved deterministic condition is the unavailable full daemon result.
Run it in a normal terminal or CI that permits it to return. The stylesheet
suite also names an owned type-scale scope for Settings, Day, and Study that
must enter enforcement and pass before its crosswalk row is fixed. Weibao owns
the visual, touch, and screen-reader Task 2 checkpoint. Until those conditions
are satisfied, Phase 20 stays blocked and no continuation task is created merely
to repeat the blockers.
