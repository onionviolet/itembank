# 16B-04 summary

Plan `16B-04`, wave 4, three tasks, all complete. `GET /` is a course shelf when
courses exist, APP-01's fixture executes end to end with one healthy card beside
one degraded card, and the shipped bank and plan listing is intact.

## Command output, final line of every verify block

| Command | Final line |
|---|---|
| `python3 tests/ia_route_roundtrip.py` | `IA ROUTES: 15 passed, 0 failed`, exit 0 |
| `python3 tests/daemon_roundtrip.py` | exit 0 |
| the corpus smoke command | `2 ['crs-mirefield-02']` then `1 2` |
| `python3 -c "... print(ia.SHELF_EMPTY_HEADING) ..."` | `No courses yet`, the empty body, `needs_input up_to_date` |
| `python3 itembank.py guard .` | `0 offending files` |
| the whole suite, 85 files | `0 failing` |

## The 14B signatures re-verified live, as Task 1 step 1 required

```
python3 -c "import course; print(course.COURSE_SIDECAR_FILENAME, course.read_course.__doc__ is not None)"
course-graph.md True

python3 -c "import inspect, course; print(inspect.signature(course.read_course))"
(course_root)
```

The signature matches the plan text: one positional course-directory path.

## Deviations from this plan, with reasons

**1. The landed course record shape is not the flat shape this plan assumed.
This is the largest deviation and it changed how a card is built.**

`course.read_course` returns `{"doc", "text", "fingerprint", "revision",
"object_id", "state"}`. It carries no `course_id`, no `name`, no `attention`, no
`due_count`, no `pending_review_count`, no `resume_cue`, and no `last_activity`.
The projection `_record_field` therefore reads the landed shape first:

| Card field | Landed source | When absent |
|---|---|---|
| `course_id` | `record["object_id"]`, the pinned `course_object_id` the sidecar names | the directory basename, degraded cards only |
| `name` | `record["doc"]["header"]["title"]` | the directory basename |
| `attention` | `record["state"] == "conflict"` maps to `needs_reconciliation` | `up_to_date` |
| `due_count`, `pending_review_count` | **no landed source** | `0` |
| `resume_cue` | **no landed source** | the literal `Not started` |
| `last_activity` | **no landed source** | `None` |

`record["state"]` is the one genuine attention signal 14B records, and it is
used. The rest are read only when a record carries them, which is how the
synthetic stand-in exercises every attention state, and defaulted otherwise.
Nothing is synthesized: a course with no recorded cue reads `Not started` rather
than a guessed cue, which is the plan's own prohibition on a guessed resume cue
honored rather than worked around. This is one projection over one record, not a
second course schema, and `course.py` was not modified.

**2. Task 1 step 8's claim that no builder writes a `.md` file is not
achievable, because `COURSE_SIDECAR_FILENAME` is `course-graph.md`.** A builder
must write that file or the shelf scan finds no course. The builders write only
into a caller-supplied destination directory, and every caller passes a
`tempfile.mkdtemp()` path outside the repository, so nothing lands in a path
`itembank guard` walks. The module docstring states this rather than repeating
the plan's claim. `python3 itembank.py guard .` reports `0 offending files`.

**3. The fixture writes a valid course graph for the healthy course rather than
an empty file.** Task 1 step 5 said each directory contains "an empty file named
`COURSE_SIDECAR_FILENAME`". The real `graph.parse_course` refuses an empty file,
so following that literally would have made **both** cards degrade end to end,
and APP-01's fixture is explicitly two courses with **one** corrupted. Task 3
step 4 anticipated this and offered asserting two degraded cards, but that would
not execute APP-01's fixture at all. Instead `_sidecar_text` builds a real
document through `graph.new_course` and `graph.serialize_course`, and the
corrupted course gets text whose first line is not the title line, which
`graph.parse_course` genuinely refuses. Verified: the real `course.read_course`
reads the healthy directory and raises `GraphError` on the corrupted one, so the
served shelf renders one healthy card and one degraded card through the real
module. No assertion was fabricated in either direction.

**4. The end-to-end healthy card is keyed by its pinned object id, and its CTA
is the Start form.** Task 3 step 4 expected `data-course-id="crs-kestrel-01"` and
`Resume Kestrel County Field Basics`. The served card is
`data-course-id="crskestrel010000"`, the `course_object_id` the sidecar names,
and its CTA is `Start Kestrel County Field Basics`. Both differences are correct
and both are asserted as such:

- Identity by pinned id rather than folder name is exactly FILE-03's rule and
  the FILE-04 amendment written into `course_shelf_state`'s docstring. The test
  now asserts the pinned id is present **and** that the folder name is not, so a
  regression to name-based identity fails.
- The Start form follows because the landed record carries no resume cue.
  Asserting the Resume form against the real module would have asserted a cue
  nothing recorded. The Resume form is still proved, against the stand-in, by
  `check_shelf_state_shape`.

The degraded card keeps the basename as its key, and the test asserts that too:
a record that would not read cannot supply an identity, and the card says so
rather than claiming one.

**5. FILE-04's workspace mode does not exist, so the shelf runs FILE-04's
documented degraded mode.** The plan's amendment requires reading courses from a
workspace record by pinned `course_object_id`. `REQUIREMENTS.md` line 1313
records FILE-04 as `Unscheduled` and `Pending`, and there is no `workspace.py` in
the tree. `course_shelf_state` therefore performs the immediate-subdirectory
scan the amendment retains as the degraded mode, and its docstring says so by
name and cites IL-20260826-01. Reconciliation by pinned id, unreachable-root
handling, and the pinned-id-versus-sidecar conflict state are not implemented,
because the record they read does not exist.

**6. The plan's fourth `handle_index` gate branch was not built, because it
contradicts D1, this plan's own key link, and four shipped tests.** Task 3 step 1
said that when the shelf is available, its cards are empty, and `stems` is also
empty, `handle_index` should render the shelf's own empty state. Building that
broke `tests/daemon_roundtrip.py`, `tests/home_roundtrip.py`,
`tests/model_phase_roundtrip.py`, and `tests/presentation_roundtrip.py`, each of
which asserts the shipped `EMPTY_STATE` heading `Nothing to serve here yet` on an
empty directory. The plan's own key link forbids exactly this: "Replacing that
body rather than branching around it would delete a shipped surface to add a new
one, and the shipped daemon suite asserts the old page." D1 is equally explicit
that when no course exists, "including a fresh install before any course is
bound", the shipped listing renders unchanged.

Resolved in favor of D1 and the key link. The gate is two-way: the shelf renders
when it has cards, and every other case falls through to the entire existing
body unchanged. `SHELF_EMPTY_HEADING` and `SHELF_EMPTY_BODY` remain in
`course_shelf_state`'s returned state for a caller that wants them, and
`check_shelf_falls_back_to_bank_index` asserts them there, plus asserts over HTTP
that the shipped heading survives and that no course card renders. The plan's
acceptance criterion that a bare directory serves `No courses yet` is the one
criterion in this plan not met as written, and this is why.

**7. `python3` was substituted for `python`, and the full-suite criterion was run
with `ANKI_CONNECT_URL=http://127.0.0.1:1/`.** Both carried forward and recorded
in `16B-02-SUMMARY.md`.

## Which truth was verified by which command

| Truth | Command | Actual result |
|---|---|---|
| The shelf renders one card per course with its cue and attention state | `check_shelf_state_shape` | two cards, CTAs `Resume Kestrel County Field Basics` and `Start Mirefield Numeracy` |
| One healthy card beside one degraded card in one response | `check_shelf_end_to_end` | two `class="course-card"` occurrences, one of each, served |
| The empty state is exact | `check_shelf_falls_back_to_bank_index` | `No courses yet` and its body on the read model |
| Same-named courses stay two cards | `check_shelf_ordering_is_total` | two ids, one name, never merged |
| Ordering is total and deterministic | same check | ten shuffled rebuilds, one identical sequence |
| The course-id tiebreak fires | same check | `crs-twin-a` before `crs-twin-b` at equal attention and timestamp |
| A corrupted course is a door, not a wall | `check_shelf_corrupted_course` | chip `Showing last valid overview`, actions `Open last valid overview` and `View files` |
| No resolved path reaches a degraded card | same check | name is `crs-mirefield-02`, no separator |
| Every attention state carries a text label | `ATTENTION_COPY` over `ATTENTION_STATES` | six states, six labels, no color-only state |
| No invented percentage | `_no_percent` across every fixture | no `%` in any chip, cue, or CTA |
| No pagination | `check_shelf_end_to_end` | `Next page`, `Previous page`, `page=` all absent |
| The shipped listing is intact | `tests/daemon_roundtrip.py` and the whole suite | exit 0, `0 failing` |

## Artifacts created or changed

- `fixtures/course_storyboard_corpus.py`, new: `FICTIONAL_COURSES`,
  `CORRUPT_SIDECAR_TEXT`, `FakeCourseModule`, `build_two_course_shelf`,
  `build_corrupted_course`, `build_same_name_pair`.
- `surfaces/ia.py`: `SHELF_EMPTY_HEADING`, `SHELF_EMPTY_BODY`, `ATTENTION_COPY`,
  `ATTENTION_TOKENS`, `ATTENTION_ORDER`, `NOT_STARTED_CUE`, `_record_field`,
  `_attention_of`, `_chip_for`, `course_shelf_state`, `_healthy_card`,
  `_degraded_card`, `_shelf_sort_key`, `_descending`.
- `surfaces/daemon.py`: `_course_shelf_body` and the course branch plus the
  rewritten docstring in `handle_index`.
- `tests/ia_route_roundtrip.py`: `_no_percent`, `check_shelf_state_shape`,
  `check_shelf_ordering_is_total`, `check_shelf_corrupted_course`,
  `check_shelf_end_to_end`, `check_shelf_falls_back_to_bank_index`.
- `16B-DECISIONS.md`: `## D-16B-10. Course-shelf ordering`.
