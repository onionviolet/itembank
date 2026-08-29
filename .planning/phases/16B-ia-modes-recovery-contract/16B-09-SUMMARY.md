# 16B-09 summary

Plan `16B-09`, wave 9, three tasks, all complete. A fresh install with nothing
configured and no network materializes one obviously synthetic course from fixed
bytes, offers a skippable and replayable walkthrough, and reaches a real course
page. Walkthrough position survives a process kill.

## Command output, final line of every verify block

| Command | Final line |
|---|---|
| `python3 tests/ia_route_roundtrip.py` | `IA ROUTES: 24 passed, 0 failed`, exit 0 |
| `python3 tests/daemon_roundtrip.py` | exit 0 |
| `python3 itembank.py guard .` | `0 offending files`, before and after materializing into the repo root |
| `python3 -c "... write_sample_course ..."` | `3`, then `Study Skills Basics (Sample)` |
| `python3 itembank.py lint <materialized bank>` | `2 items, 0 errors, 3 warnings`, exit 0 |
| `python3 itembank.py shelf skip_walkthrough .` | a JSON object with `"ok": true` |
| `python3 tests/packaging_roundtrip.py` | exit 0 |
| `git status --porcelain` | no `_sample_course` or `_ia` entry, both gitignored |

## The guard check, run by hand rather than assumed

```
python3 itembank.py guard .                       0 offending files
<materialize _sample_course/ into the repo root>
ls _sample_course/                                README.md  course-graph.md  study_skills_sample.md
python3 itembank.py guard .                       0 offending files
git status --porcelain | grep _sample_course      (nothing: gitignored)
```

## Final route-table values

```
len(daemon.API_ROUTES)      14
len(daemon.SURFACE_PARITY)  14
daemon.ROUTE_CLI[("POST", "/api/shelf")]  shelf
daemon.SHELF_ALLOWED_FIELDS               ('action',)
```

D-16B-7 said `check_api_route_scope`'s literal `12` becomes `13`. Against the
landed tree that is `13` becoming `14`, exactly as `16B-PRECONDITION.md`
directed, and the new `SURFACE_PARITY` row is the fourteenth.

## Deviations from this plan, with reasons

**1. The sidecar is written through `graph.new_course` and
`graph.serialize_course`, which is neither branch this plan named.** Task 1 step
5 gave two branches: call `course_module.write_course(dest_dir,
SAMPLE_COURSE_RECORD)` when it exists, else write the record as JSON.

Neither works. The landed `course.write_course` has the signature
`(course_root, doc, expected_fingerprint, actor_kind, actor_name,
operation='edit_in_place')`: it is the compare-and-swap **edit** path and needs
a parsed document, an expected fingerprint, and an actor, so it cannot bootstrap
a sidecar that does not exist yet. The two-argument call the plan specified
raises `TypeError`. The JSON fallback would write bytes `course.read_course`
cannot parse, so the sample course would render as a **degraded** card on every
fresh install, which is the opposite of what APP-03 asks for.

`sidecar_text()` therefore builds a real document through the same two calls any
real sidecar is built from. Verified: `course.read_course` reads it, reports
`object_id` `sample-study-skills` and title `Study Skills Basics (Sample)`, and
the sample renders as a healthy card. Same root cause as `16B-04-SUMMARY.md`
deviation 3.

**2. Materialization is gated on a genuinely fresh root, which this plan did not
specify.** Task 3 step 1 said to materialize whenever the sample is absent and
not removed. Built literally, that materialized the sample into **every** root
the daemon served, so a directory already holding banks rendered a course shelf
instead of its bank listing and four shipped checks failed on
`populated index missing 'sample_bank'`.

The gate is now: no bank, no day plan, and no course already bound. A root that
already serves something is not a first launch, and replacing a working home
with a sample the learner never asked for is a regression rather than a feature.

**3. Four shipped tests were updated, because APP-03 changes what an empty
directory renders.** `tests/daemon_roundtrip.py`, `tests/home_roundtrip.py`, and
`tests/presentation_roundtrip.py` each assert the documented `Nothing to serve
here yet` copy on an empty directory, and `tests/model_phase_roundtrip.py` runs
the first of those. With first launch, a genuinely empty root is no longer empty
by the time the page renders.

Each of the three now records the sample course as removed before its request,
so each keeps asserting exactly what it always asserted, on the case the copy
actually governs: no course. Nothing was deleted from any assertion and the
documented copy is unchanged.

**This is deliberately the opposite call from `16B-04-SUMMARY.md` deviation 6,
and the distinction is on the record.** There, the plan's empty-shelf branch had
no requirement behind it and contradicted D1 and the plan's own key link, so it
was dropped in favour of the shipped surface. Here, `REQUIREMENTS.md` APP-03 is
a Requirements-level fixture explicitly about first launch, so the shipped
assumption gives way to it.

**4. `_remove_sample_dir` prunes empty subdirectories and reports what
survived.** As first written it removed files, attempted `os.rmdir`, and
swallowed the failure while still reporting success. The daemon creates an empty
`_attempts/` inside any root it serves, including the sample course directory,
so `rmdir` failed and the action claimed a removal that had not happened. It now
prunes already-empty subdirectories, which is daemon debris rather than learner
data, still refuses to delete a non-empty subtree or follow a symlink, and
returns what survived so the message says what actually occurred rather than
asserting a clean removal.

**5. `build.py` gained `sample_course.py`.** `surfaces/daemon.py` and
`surfaces/ia.py` import it at module scope, so omitting it from `STAGE_FILES`
was a hard `ModuleNotFoundError` inside the built `.pyz`, caught by
`tests/packaging_roundtrip.py` and `tests/math_offline_roundtrip.py`. This is
the same class of gap the 14A/14B and 16A entries in that file already record,
and the comment says so.

**6. The 16B-02 structural no-write ban no longer holds as literally written,
and it should not.** That command greps `surfaces/ia.py` for a write mode.
D-16B-5, from the same decision set, requires this plan to add exactly two state
writers under `_ia/`. The ban's actual intent, no second write authority over
the journal or the evidence store, is intact and is now asserted more precisely
by `check_ia_state_is_atomic`, which parses `apply_shelf_action`'s code body
(not its docstring) and fails if any `os.path.join` in it takes a segment other
than `sample_course.SAMPLE_COURSE_DIRNAME` or `IA_STATE_DIR`, or if the function
mentions a request value or `shutil.rmtree`.

**7. `check_first_launch_offline` and `check_walkthrough_interruption` request
`GET /` before any course-level path.** First launch is what materializes the
sample, so a course path requested first would 404 correctly.

**8. Pre-16B-09 fixtures call a new `suppress_sample_course` helper.** Twelve
fixture directories in `tests/ia_route_roundtrip.py` were asserting on a known
card count or on the shipped bank index; each records the sample as removed so it
keeps testing what it was written for. The five checks that exist to prove first
launch do not call it.

**9. Two suite failures remain, both pre-existing and neither 16B's.**
`tests/retention_roundtrip.py` fails with `3 settled with 1 correct must be
weak, got 'at-risk'`, and `tests/phase_062_audit.py` fails only because it runs
the whole suite and inherits that one. Verified pre-existing by adding a
detached `git worktree` at `HEAD` and reproducing the identical failure there
with no 16B change present. It passed earlier in this same phase, so it is
date-sensitive rather than code-sensitive. Recorded rather than worked around;
it is not this phase's to fix.

**10. `python3` for `python`, and the suite run with
`ANKI_CONNECT_URL=http://127.0.0.1:1/`.** Carried forward from
`16B-02-SUMMARY.md`.

## Which truth was verified by which command

| Truth | Command | Actual result |
|---|---|---|
| The bundled course is obviously synthetic | `check_sample_course_suffix` | name and CTA both end in `(Sample)` |
| Its bytes are fixed and idempotent | same check | two materializations, identical per-file SHA-256 |
| It lints clean | same check | `itembank lint` exit 0 |
| A same-base-name real course stays separate | same check | two cards, two names |
| Guard survives it on disk | by hand, twice | `0 offending files` both times |
| State survives a fault mid-write | `check_ia_state_is_atomic` | no `.tmp` left, truncated file reads as default |
| Reading state creates no file | same check | `_ia/` absent after a read |
| Removal is idempotent and honest | same check | exact no-op message on the second call |
| The deletion path is fixed, not request-derived | same check | every `os.path.join` segment is a module constant |
| The route accepts one field | `check_shelf_action_allowed_fields` | 400 with `body may carry only: action` |
| The route accepts four actions | same check | 400 naming all four |
| The route is loopback and same-origin | same check | 403 cross-origin |
| Only POST is registered | same check | `GET /api/shelf` is 404 |
| A fresh install reaches a real course with nothing configured | `check_first_launch_offline` | `GET /course/sample-study-skills` is 200 |
| Offline help routes on a fresh install | same check | 200 with its exact cause sentence |
| The offer does not block the shelf | same check | `class="course-card"` in the same response |
| Position survives a process kill | `check_walkthrough_interruption` | step 2 restored after `proc.kill()` |
| Skipping is never a lost opportunity | same check | replay control present after a skip |
| No first-run action blocks another area | same check | `/learn` and `/activity` both 200 mid-walkthrough |

## Artifacts created or changed

- `sample_course.py`, new: `SAMPLE_COURSE_ID`, `SAMPLE_COURSE_NAME`,
  `SAMPLE_COURSE_DIRNAME`, `SAMPLE_COURSE_RECORD`, `SAMPLE_COURSE_FILES`,
  `sidecar_text`, `write_sample_course`.
- `surfaces/ia.py`: `IA_STATE_DIR`, `IA_STATE_DEFAULTS`, `read_ia_state`,
  `write_ia_state`, `WALKTHROUGH_COPY`, `SAMPLE_COURSE_COPY`,
  `WALKTHROUGH_STEPS`, `SHELF_ACTIONS`, `walkthrough_state`,
  `sample_course_state`, `apply_shelf_action`, `_remove_sample_dir`,
  `cmd_shelf`.
- `surfaces/daemon.py`: `SHELF_ALLOWED_FIELDS`, the `API_ROUTES`, `ROUTE_CLI`,
  and `SURFACE_PARITY` entries, `handle_api_shelf`, `SHELF_NOSCRIPT`,
  `_walkthrough_offer`, `_sample_course_controls`, the first-launch gate in
  `handle_index`, and the sample controls inside `_course_shelf_body`.
- `surfaces/cli.py`: `add_parser("shelf")` and two entries in `cmd_guard`'s
  skipped-directory tuple.
- `build.py`: `sample_course.py` in `STAGE_FILES`.
- `.gitignore`: `_sample_course/` and `_ia/`.
- `tests/ia_route_roundtrip.py`: `suppress_sample_course`, `_post_shelf`, and
  five new checks.
- `tests/daemon_roundtrip.py`: the fourteen-route scope, the `/api/shelf` twin
  assertion, and the first-launch note in `check_index_empty`.
- `tests/home_roundtrip.py`, `tests/presentation_roundtrip.py`: the same
  first-launch note on their empty-index checks.
