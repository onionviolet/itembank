# Phase 16B tracer report

Every figure in this file was measured on the machine and interpreter named
below during one pass on 2026-08-28. No budget number, no target number, and no
estimate appears anywhere in it.

```
os      macOS-27.0-arm64-arm-64bit-Mach-O
python  3.14.6 at /opt/homebrew/opt/python@3.14/bin/python3.14
```

The whole run used `ANKI_CONNECT_URL=http://127.0.0.1:1/`, an unreachable
loopback port, because Anki Desktop is running on this machine and three shipped
suites assert the exact locked "Anki closed" copy. Recorded first in
`16B-02-SUMMARY.md`.

## What was run

| Command | Exit | Final line, verbatim |
|---|---|---|
| `python3 tests/ia_route_roundtrip.py` | 0 | `IA ROUTES: 24 passed, 0 failed` |
| `python3 tests/ia_storyboard_tracer.py` | 0 | `STORYBOARD: 12 passed, 0 skipped, 0 failed` |
| `python3 tests/mode_layer_roundtrip.py` | 0 | `MODE LAYERS: 6 passed, 0 failed` |
| `python3 tests/degraded_state_roundtrip.py` | 0 | `DEGRADED: 7 passed, 0 failed` |
| `python3 tests/daemon_roundtrip.py` | 0 | `ok: daemon served 76 checks ...` |
| `python3 tests/config_roundtrip.py` | 0 | `config contract: ok (schema completeness, exact numeric bounds, ...)` |
| `python3 tests/theme_roundtrip.py` | 0 | `ok: theme Wave 0 harness ...` |
| the full suite, all 88 files | **2 failing** | see Open findings, leg 2 |
| `python3 itembank.py guard .` | 0 | `0 offending files` |
| `git status --porcelain` | 0 | no `_sample_course` and no `_ia` entry |

## The five freeze-gate fixtures

| ROADMAP fixture | Result | Covered by |
|---|---|---|
| FLOW-01, the loop A through G interruption storyboard | passed | `scenario_loop_a` through `scenario_loop_g` in `tests/ia_storyboard_tracer.py`, each interrupting its loop at a fixed mid-loop step, dropping every in-memory reference, and recomputing the resume state from a file read back off disk |
| FLOW-02, the model-disabled reading and practice walk | passed | `scenario_model_disabled_walk` in `tests/ia_storyboard_tracer.py`, eight stages against the real CLI with `model_backend.active` empty, nothing skipped |
| APP-01, the two-course shelf with one corrupted course | passed | `check_shelf_corrupted_course` and `check_shelf_end_to_end` in `tests/ia_route_roundtrip.py`, one healthy card beside one degraded card served by a real daemon through the real `course.py` |
| APP-02, the deep-link replay across both layouts | **weaker proof** | `check_same_routes_both_widths`, `check_deep_link_scenarios`, and `check_no_pagination_on_reading` in `tests/ia_route_roundtrip.py`. What was not exercised: the two layouts are distinguished only by a viewport-hint request header, so this proves one route and one identical back href serve both widths, and it does not prove anything about rendered layout at either width, which is a Phase 17A visual concern. The browser half of the focus-restoration scenario, the actual focus move after paint, is also not observed by any check here. |
| APP-03, the first-launch interruption with no roots, no agent, and no network | passed | `check_first_launch_offline` and `check_walkthrough_interruption` in `tests/ia_route_roundtrip.py`, a fresh install reaching a real course page and a walkthrough position surviving `proc.kill()` |

## Measured figures

Wall-clock duration of each command, measured with `time.monotonic()` around
the subprocess call:

| Command | Duration |
|---|---|
| `tests/ia_route_roundtrip.py` | 2.9s |
| `tests/ia_storyboard_tracer.py` | 0.8s |
| `tests/mode_layer_roundtrip.py` | 0.2s |
| `tests/degraded_state_roundtrip.py` | 0.3s |
| `tests/daemon_roundtrip.py` | 11.8s |
| `tests/config_roundtrip.py` | 4.7s |
| `tests/theme_roundtrip.py` | 0.3s |
| the full suite, 88 files | 381.4s |

Route structures, printed by one command:

```
len(daemon.ROUTES)          43
len(daemon.API_ROUTES)      14
len(daemon.SURFACE_PARITY)  14
len(daemon.ROUTE_CLI)       43
```

Closed vocabularies and the loop step total, printed by the same command:

```
len(ia.IA_HELP_CODES)        12
len(ia.DEGRADED_STATES)       8
len(ia.MODE_LAYERS)           7
len(ia.COURSE_AREAS)          8
len(ia.SHELF_ACTIONS)         4
total LOOP_STEPS steps       59
```

The bundled sample course:

```
files written by write_sample_course   3
their total size                       5531 bytes
```

## Additivity evidence

| | Recorded in `16B-PRECONDITION.md`, before any 16B change | Found now |
|---|---|---|
| pre-existing settings keys | 22 | 22 |
| sorted-JSON SHA-256 of those keys | `3d9a94c70270413b29390317660b37dc198fc6ae1530c4d5dd3041710c4a1235` | `3d9a94c70270413b29390317660b37dc198fc6ae1530c4d5dd3041710c4a1235` |

Byte-identical. Every key that existed before this phase has exactly the
effective value it had before `surfaces/ia.py` existed. The four keys plan
16B-06 added are excluded from both sides, and none of them joined the schema's
top-level `required` array.

## Open findings

### Leg 2 fails: the full suite is not green

Two of 88 files fail:

```
retention_roundtrip.py   FAIL: 3 settled with 1 correct must be weak, got 'at-risk'
phase_062_audit.py       FAIL: full suite not green: [('retention_roundtrip.py', ...)]
```

`phase_062_audit.py` fails only because it runs the whole suite and inherits the
other. So this is one failure, not two.

**It is not Phase 16B's, and it is not a product defect.** It is an expiring
test fixture. `tests/retention_roundtrip.py` builds three attempts with
hardcoded dates 2026-08-01 through 2026-08-03 and its own comment says they are
"all recent (so at-risk's 28-day silence rule does not fire first -- D-14
precedence)". Today is 2026-08-28, so the last confirmed success is 27 days old
and the 28-day at-risk rule now wins the precedence order, exactly as the
comment warned. The fixture aged out.

Evidence that it is pre-existing: reproduced identically on a detached
`git worktree` at `HEAD` with no 16B change present. It also passed earlier in
this same phase, which is consistent with a date boundary crossing rather than
with a code change.

**This is recorded as a failing freeze leg rather than judged here.** Plan
16B-11's own rule is that no freeze record is written on a red suite. Whether an
unrelated expiring fixture withholds Phase 16B's freeze is a judgment, and it is
put to the human reviewer in Task 2 rather than decided by the agent that ran
the suite.

### Stages marked SKIPPED

None. `tests/ia_storyboard_tracer.py` reports `0 skipped`. One stage did skip on
an earlier run, `scoring: no wrong option was available on the served item`,
because the selector served a drag-and-drop item with no options; the walk now
selects an `mc` item so the scorer genuinely runs, and the skip path remains
implemented and would still report honestly.

### The APP-02 unresolved probe row

The spec-less edge-coverage probe returned APP-02's row as `unclassified`.
`16B-DECISIONS.md`'s `## APP-02 probe enumeration` names three scenarios rather
than dropping it, and all three are executed by `check_deep_link_scenarios`:
deep-link stability under rename or move (path byte-identical, old name gone);
an anchor into deleted content (page 200 and complete, help link count zero);
and focus restoration when the target no longer exists (server-side half only,
see the weaker-proof note above).

### Deviations recorded by the phase summaries

| Plan | Deviation |
|---|---|
| 16B-01 | Five route and settings counts had drifted from `14C-01`, `17A-05`, and `17A-08`; reconciled and recorded, every halt field clean. `python3` substituted for `python` throughout. |
| 16B-02 | The landed journal entry schema carries no `intent`, `step`, `steps_total`, `stage`, or `cancelled` field; the read model maps onto landed fields and defaults the rest rather than inventing a second entry schema. A pre-existing em dash sits at `surfaces/cli.py:1409`. |
| 16B-03 | The schema has no `model_backend` enum member meaning "none"; the disabled state is an empty `active`, and the fixture writes that. |
| 16B-04 | The landed course record is `{doc, text, fingerprint, revision, object_id, state}`, not the flat shape the plan assumed; identity is the pinned `course_object_id`, and the plan's fourth `handle_index` gate branch was not built because it contradicted D1, the plan's own key link, and four shipped tests. FILE-04's workspace mode does not exist, so the shelf runs its documented degraded directory scan. |
| 16B-05 | An unrecognized area segment is refused at dispatch by the locked closed alternation, so it cannot carry a help link; the route-failure half of the distinction is asserted on an unknown course instead. `content_available` is False for every area, because the record shapes that fill one belong to Phases 14A and 14B. |
| 16B-06 | Counts are 26 properties and 19 required, reconciled from the drifted baseline. A group missing one nested member is not malformed. The declared-not-enforced note prints for all nine keys above `THIS_PHASE`, not four, because restricting it to four needed the hard-coded list the plan forbids. |
| 16B-07 | The UI-SPEC states the conflict sentence twice and the two differ; the Copywriting Contract template including "for this course" was taken as binding and the discrepancy recorded in `16B-DECISIONS.md`. |
| 16B-08 | None material. |
| 16B-09 | `course.write_course` is the compare-and-swap edit path and cannot bootstrap a sidecar, so the sample's sidecar is built through `graph.new_course` and `graph.serialize_course`. Materialization is gated on a genuinely fresh root. Four shipped tests were updated because APP-03 changes what an empty directory renders. `_remove_sample_dir` was reporting success while the directory survived. `build.py` gained `sample_course.py`. |
| 16B-10 | `itembank evidence` needs a query argument; the walk passes `--session`. The walk selects `--type mc` so the scoring stage runs rather than skips. |

### Deferrals this phase made, by name

- **No Activity write path at all**, per `D-16B-8`. No resolve route, no resolve
  control, no journal write.
- **No enforcement of `approved_roots`, `network_egress`, `accessibility`, or
  `storage`**, per plan 16B-06. All four are declared at `x-itembank-phase`
  16.2 and gated on by nothing; the settings panel says so on the same screen.
- **No live-state mode-layer collector**, per `D8` and `D-16B-12`. Phase 16C
  owns it under `STRATEGY-02`.
- **No real course-area content**, per plan 16B-05. Every area reports
  `content_available` False; Phases 14A and 14B own the record shapes.
- **No producer for six of the eight degraded states.** Only
  `course_corrupted` and `agent_unavailable` are wired into a route, because
  the other six need a producer this phase does not build.
- **Notes**, per `D4`. Contextual panels inside Learn and Evidence only, no
  route.
- **Search**, per `D5`. Named as a reserved App-level area, not built.
- **The ROADMAP goal clause "hosted, local, and manual continuation share
  durable checkpoints under the one operation protocol."** Phase 16B satisfies
  only the read side of this. `RELIABILITY-02` and `AGENT-01/02/03` own the
  protocol itself and are Phase 15A's and 15B's. Recorded so a reader does not
  mistake this phase's display contract for the protocol.

### Backstop markers carried by plans 02 through 10

Each is a claim whose evidence was deliberately not supplied in this phase.

| Owning plan | Backstop claim |
|---|---|
| 16B-02 | A genuinely slow Activity read renders a stated loading state; the read is synchronous today so no loading state is reachable. |
| 16B-02 | A long job list scrolls rather than clipping or paginating; the exact scroll container is Phase 17A's. |
| 16B-04 | A genuinely slow multi-root course read renders a stated loading state rather than a blank shelf. |
| 16B-04 | A many-course shelf scrolls rather than clipping; the overflow treatment is Phase 17A's. |
| 16B-04 | A shelf read concurrent with a job mutating course state shows the last accepted state with no torn read. |
| 16B-05 | A course area with no content renders a stated area-level empty state rather than a blank region. |
| 16B-05 | A genuinely slow course-area read renders a stated loading state. |
| 16B-05 | Area lists that can grow inherit list behavior contracted per area at execution. |
| 16B-05 | Focus and scroll restoration timing after the server render, confirmed by the APP-02 replay. |
| 16B-05 | Opaque deep-link display length in narrow layouts. |
| 16B-06 | A slow settings read renders a stated loading state. |
| 16B-06 | Many approved roots in one group scroll or collapse rather than clipping; which is Phase 17A's. |
| 16B-06 | A long root path wraps keeping its drive or root visible, never behind a mid-path ellipsis. |
| 16B-08 | Banner precedence when several states fire at once, and one help page per banner. Note: this one **was** proven here, by `check_banner_precedence` over all 28 pairs. |
| 16B-08 | A refusal payload with no unlock condition renders a stated condition; the substitute sentence is contracted at execution. Note: proven here by `check_locked_card_shape`. |
| 16B-08 | A locked card renders synchronously today, so no loading state is reachable. |
| 16B-08 | A failure to obtain the refusal payload degrades to the generic locked state rather than to a chat surface. |
| 16B-08 | Several simultaneous refusal reasons collapse to one card; which reason wins needs a held-out check. |
| 16B-08 | Several locked cards in one view need a storyboard scenario. |
| 16B-08 | A degraded banner renders before, not after, any slow recovery attempt. |
| 16B-09 | Removing an already-removed sample course is a stated no-op and the walkthrough is replayable. Note: both **were** proven here, by `check_walkthrough_interruption`. |
| 16B-09 | A long-running job never blocks Learn, Practice, Test, or Evidence with a job actually in flight. Note: partially proven, `/learn` and `/activity` both returned 200 mid-walkthrough, but no durable job was in flight. |
| 16B-09 | First launch with the sample already removed still offers the walkthrough over an empty shelf. |
| 16B-09 | A missing or corrupted walkthrough bundle degrades to the plain shelf and never blocks first launch. |
| 16B-09 | Walkthrough step copy length in narrow layouts, confirmed at Phase 17A. |

### Other open items

- One em dash character survives at `surfaces/cli.py:1409`, in a pre-existing
  Phase 999.4 comment about LTI. It violates the repository prose rule and is
  not this phase's; every file 16B wrote passes the `chr(0x2014)` check.
