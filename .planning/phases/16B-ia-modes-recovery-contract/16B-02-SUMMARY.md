# 16B-02 summary

Plan `16B-02`, wave 2, three tasks, all complete. The phase tracer is green: a
real daemon on a real port answers `GET /activity` with a page built by
`surfaces/ia.py`'s read model, and the assertion is made on bytes that crossed
a socket.

## Command output, final line of every verify block

| Command | Final line |
|---|---|
| `python3 tests/ia_route_roundtrip.py` | `IA ROUTES: 6 passed, 0 failed`, exit 0 |
| `python3 tests/daemon_roundtrip.py` | `ok: daemon served 76 checks ...`, exit 0 |
| `python3 -c "... print(len(ia.IA_HELP_CODES), ...)"` | `12 8 8 7 8` |
| `python3 -c "... print([p for m,p,h in daemon.ROUTES if p=='/activity'], daemon.ROUTE_CLI[('GET','/activity')])"` | `['/activity'] activity` |
| `python3 itembank.py activity .` | a JSON object carrying `available`, `code`, `notice`, `needs_input`, `jobs`, exit 0 |
| the structural no-write ban command | `no write path` |
| `python3 itembank.py guard .` | `0 offending files` |
| the whole suite, 85 files | `0 failing` |

## Final route-table values

```
len(daemon.ROUTES)          38
len(daemon.API_ROUTES)      13
len(daemon.SURFACE_PARITY)  13
```

`API_ROUTES` and `SURFACE_PARITY` are unchanged by this plan, as its out-of-scope
section requires. They read 13 rather than the plan's stated 12 because of the
`14C-01` drift reconciled in `16B-PRECONDITION.md`, not because this plan added
an `/api/*` route. The `/activity` entry sits at index 7 of `ROUTES`, inside the
fixed-literal block, strictly before `("POST", "/api/start", ...)` at index 11.

## The flagged assumption fired: the landed journal entry schema differs

`16B-02-PLAN.md`'s flagged assumption anticipated this exactly, and the plan's
instruction was to change the mapping and record the deviation rather than
invent a second entry schema. The landed `journal.ENTRY_KEYS` is a fixed
23-key tuple and does not carry four of the eight field names the plan read
from `14A-02-PLAN.md` text.

| Plan-text field | Landed `journal.py` | How `activity_view_state` maps it |
|---|---|---|
| `entry_id` | `entry_id` | unchanged |
| `timestamp` | `timestamp` | unchanged |
| `state` | `state` | unchanged |
| `resolves_entry` | `resolves_entry` | unchanged |
| `object_id` | `object_id` | unchanged |
| `reason` | `code` plus `message` | `_reason_of` reads `message` first, then `reason`, so a landed entry and a plan-text-shaped entry produce the same display |
| `intent` | no equivalent field | `_intent_of` composes the recorded `operation` over the recorded `path`, with the path half through the D9 basename rule |
| `cancelled` | **no equivalent field** | read with `.get()`; the landed journal never sets it, so `cancelled` is reachable today only through a synthetic stand-in |
| `step`, `steps_total`, `stage` | **no equivalent fields** | read with `.get()`; the landed journal never sets them, so a real journal always yields `needs_input` or `in_progress_no_estimate`, never `in_progress_known` |

This is honest rather than papered over: `in_progress_known` and `cancelled`
stay in `ACTIVITY_JOB_STATES` and in `ACTIVITY_COPY` because the UI-SPEC
Activity Contract locks them, they are exercised by `_FakeJournal`, and the
read model refuses to synthesize either one from data the journal does not
record. D7's ban on an invented figure is what makes that the right outcome: a
step count the journal never wrote is exactly the ratio D7 forbids.

**No second entry schema was invented.** No field was added to `journal.py`, and
`surfaces/ia.py` reads only through `.get()`.

## The ordering check was observed failing, then the position restored

Moving `("GET", "/activity", "handle_activity_get")` after the trailing regex
block made `python3 tests/ia_route_roundtrip.py` exit non-zero with exactly:

```
FAIL: a new fixed-literal route was appended after the stem-parameterised block
```

The correct position was restored and the suite is green again. One incident
worth recording: after the restore, the check kept failing against source that
was already correct. The cause was a stale `__pycache__` entry. The modified and
restored `surfaces/daemon.py` had **identical byte size** (one line removed and
an identical line added elsewhere) and the same-second mtime, so CPython's
mtime-plus-size `.pyc` validation accepted the wrong bytecode. Clearing
`__pycache__` resolved it. Recorded here because it would read as a real
ordering regression to the next person who hits it.

## The served not-yet-available page was proven through the env switch

`ITEMBANK_IA_NO_JOURNAL=1` was used, so the degraded path was proven **served**,
not only in-process. `check_activity_unavailable_state` asserts both halves: the
direct `activity_view_state(".", journal=None)` call, and a live daemon launched
with the variable set, whose body carries the exact notice and
`href="/help/ia.activity_unavailable"`.

One adjustment: the served page escapes the notice's apostrophe to `&#x27;`,
which is correct output escaping. The assertion runs `html.unescape(body)`
before comparing rather than weakening the escaping or asserting on the escaped
form.

## Which truth was verified by which command

| Truth | Command | Actual result |
|---|---|---|
| One request proves the stack end to end over a socket | `check_activity_route_end_to_end` | 200, `<h1>Activity</h1>`, `Back to courses` present |
| `/activity` is one row in the shipped structures and nothing else | `check_route_cli_inventory` (extended), `check_route_order_is_load_bearing` | both pass; index 7 < index 11 |
| No second dispatcher | `check_one_dispatcher` | `inspect.getsource(daemon).count("def _dispatch") == 1` |
| No write path in the read model | the structural ban grep | `no write path` |
| Every job state renders its locked copy and token | `check_activity_job_states` | all seven non-unavailable cases exact |
| No invented percent anywhere | same check, plus the served-page `<h3>` scan | no `%` in any label or heading |
| No journal payload escapes to a page | `check_activity_no_write_path` | `SECRET-BEFORE-IMAGE` in no job dict and no rendered page; every job's key set equals `ia.JOB_KEYS` |
| A malformed entry degrades rather than raising | same check | one `Failed: unreadable journal entry` job, nothing raised |
| Zero jobs renders no section header | same check | `Needs your input` absent from the zero-jobs page |
| One and three jobs share one structure | same check | 1 and 3 occurrences of `<article class="job"` |
| Ordering is newest first, ties by entry_id ascending | same check | `["new","old"]` and `["a1","b1","c1"]` |

## Deviations from this plan, with reasons

**1. The landed journal entry schema.** Recorded in full above. This is the
plan's own flagged assumption firing, handled as the plan directed.

**2. `python3` was substituted for `python` in every command.** No `python`
executable exists on this machine. Carried forward from `16B-01`.

**3. `surfaces/cli.py` contains one em dash, at line 1409, and it is not this
task's.** The acceptance criterion lists `surfaces/cli.py` among the files that
must carry no em dash. The character sits in a pre-existing Phase 999.4 comment
about LTI, untouched by this plan; the six lines this task added to that file
carry none. Removing it would be an edit to unrelated shipped prose that this
plan's out-of-scope section forbids, so it is recorded here rather than made.
`surfaces/ia.py`, `tests/ia_route_roundtrip.py`, `tests/daemon_roundtrip.py`,
and `surfaces/daemon.py` all pass the `chr(0x2014)` check.

**4. Three shipped tests fail on this machine unless Anki Desktop is
unreachable, and the cause is environmental rather than 16B's.**
`tests/day_roundtrip.py` and `tests/retention_ui_roundtrip.py` each assert the
exact locked "Anki closed" copy, and `tests/phase_062_audit.py` fails only
because it runs the whole suite. Anki is running on this machine and answers
with `0 due, 173 new`. Verified pre-existing by stashing every 16B change and
reproducing the identical failure on the clean tree. With
`ANKI_CONNECT_URL=http://127.0.0.1:1/` pointing at a closed port, all three pass
and the whole 85-file suite reports `0 failing`. The user's running Anki was not
touched.

## Artifacts created or changed

- `surfaces/ia.py`, new: the module docstring with the D6 distinction and the
  test-only env switch, the seven closed vocabularies, `ACTIVITY_COPY`,
  `ACTIVITY_TOKENS`, `JOB_KEYS`, `activity_view_state`, `cmd_activity`.
- `surfaces/daemon.py`: `ia` added to the surfaces import, one `ROUTES` entry,
  one `ROUTE_CLI` entry, and `handle_activity_get`.
- `surfaces/cli.py`: the `cmd_activity` import and `add_parser("activity")`.
- `tests/ia_route_roundtrip.py`, new: six checks.
- `tests/daemon_roundtrip.py`: one added assertion inside the existing
  `check_route_cli_inventory`, no fork.
