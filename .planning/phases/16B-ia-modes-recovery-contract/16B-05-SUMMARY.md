# 16B-05 summary

Plan `16B-05`, wave 5, three tasks, all complete. All eight course areas are
addressable at one URL each, Notes and Search are deliberately unroutable, a
saved link survives a rename and a move, and a dead anchor keeps its page.

## Command output, final line of every verify block

| Command | Final line |
|---|---|
| `python3 tests/ia_route_roundtrip.py` | `IA ROUTES: 19 passed, 0 failed`, exit 0 |
| `python3 tests/daemon_roundtrip.py` | exit 0 |
| `python3 -c "... ia.anchor_slug('Airway Adjuncts') == model.lesson_slug('Airway Adjuncts')"` | `True` |
| `python3 itembank.py guard .` | `0 offending files` |
| the whole suite, 85 files | `0 failing` |

## Final route-table values

```
len(daemon.ROUTES)          42
len(daemon.API_ROUTES)      13
len(daemon.SURFACE_PARITY)  13
```

## What was proven

**One route per object at every width.** Each of the eight course-level paths
matches exactly one entry in `daemon.ROUTES`, asserted in Python over the real
tuple. The same path requested with and without a narrow-viewport hint header
returns 200 both times, is served by the same single matching entry, and carries
a byte-identical back href. Layout is a rendering decision inside the handler and
never a second URL, which is Pitfall 4 honored mechanically.

**Notes and Search are unroutable by design.** `/course/<id>/notes` is 404 per
D4 and `/course/<id>/search` is 404 per D5, both because the area alternation is
a closed vocabulary rather than because they happened to be unimplemented.

**One slug implementation.** `ia.anchor_slug` is a one-line delegation to
`model.lesson_slug`, verified equal on a sample heading. There is no second slug
path in `surfaces/ia.py`.

**Nothing a reader reads paginates.** Across the shelf and all eight
course-level pages, none of `Next page`, `Previous page`, `page=`, `rel="next"`,
or `rel="prev"` appears in any body, and no response carries a `Link` header with
`rel=next`.

**The scripting-disabled path is real.** Every course-level response carries a
real `<p class="back"><a href=` control, a heading with a real `anchor_slug` id,
the hidden `data-anchor-missing` region, and the exact `noscript` sentence.
`RESTORE_SCRIPT` contains none of `history.back`, `fetch(`, `XMLHttpRequest`,
`document.write`, or `innerHTML =`, and it reveals an already-rendered region
rather than injecting content.

## The three APP-02 scenarios

**(a) Deep-link stability under rename or move.** The course was renamed from
`Kestrel County Field Basics` to `Kestrel Field Skills` and its directory moved
to a new parent. `deep_link_target`'s `path` is byte-identical before and after,
because the segment is the opaque course id. `back_label` correctly follows the
rename to `Back to Kestrel Field Skills`, and no returned field carries the old
name.

**(b) An anchor into deleted content.** The area page is 200, renders in full
with all eight nav labels and its back control, carries the
`data-anchor-missing` region, and contains `href="/help/ia.route_not_found"`
**zero** times, because the route resolved and only the anchor did not. The
route-failure half of the distinction is asserted separately and does carry that
link.

**(c) Focus restoration when the original target no longer exists.** The
server-side half is asserted: the area heading carries an `anchor_slug` id so the
script has a real fallback target, `RESTORE_SCRIPT` contains
`document.getElementById`, the `h1` selector, and the `[data-anchor-missing]`
selector, and `deep_link_target(course_id, area, anchor="gone")` normalizes the
stale anchor through `anchor_slug` rather than passing it through raw.

**The browser half of scenario c is not asserted by this suite.** The actual
focus move after paint is not observed by any check here. It is carried as the
DeepLinkNav loading backstop row, to be confirmed by the APP-02 replay rather
than by construction. No browser behavior is claimed that this suite did not
observe.

## Deviations from this plan, with reasons

**1. The unknown-area 404 cannot carry the help link, because the locked regex
refuses it before any handler runs.** Task 3 step 3 expected
`GET /course/<id>/nosucharea` to return 404 with
`href="/help/ia.route_not_found"` in its body. `COURSE_AREA_RE`'s area
alternation is a closed vocabulary locked by D-16B-1, so an unrecognized segment
matches no route at all and `DaemonHandler._dispatch` answers with the shipped
404. No handler runs, so nothing can attach a help link. That is the stronger
property, not a gap: the refusal happens at dispatch.

The distinction the scenario exists to prove is preserved, using the case the
route architecture actually routes: `GET /course/no-such-course/learn` is a
well-formed path whose course does not exist, it reaches `handle_course_area_get`,
and its 404 does carry `href="/help/ia.route_not_found"`. So a route failure
links the help page and a resolved route with a dead anchor does not, which is
exactly what the scenario asserts. The unknown-area case is still asserted as a
404 carrying no traceback.

**2. Tests address courses by pinned `course_object_id`, not by folder name.**
The plan's test text uses `crs-kestrel-01`. The real `course.read_course` reports
the sidecar's own `course_object_id`, so the served id is `crskestrel010000`.
`_shelf_course_ids` resolves ids from the shelf rather than hard-coding either
form, because a test that hard-coded the folder name would assert the name-based
identity FILE-03 forbids. Same root cause as `16B-04-SUMMARY.md` deviation 4.

**3. `course_area_state` resolves a course directory by pinned id first,
basename second.** The plan did not say how to find a course directory from a
`course_id`. `_course_dir_for` scans for the directory whose sidecar names that
id and falls back to a directory whose basename matches only when no sidecar
claims it. The fallback exists so a degraded card, whose record would not read
and which is therefore keyed by basename, still resolves to its own page rather
than 404ing.

**4. `content_available` is False for every area.** The record shapes that fill
Learn, Practice, Test, Map, Sources, Build, and Evidence belong to Phases 14A and
14B. Each area states what it holds with the literal
`Nothing has been added to {area_label} for this course yet.` rather than
rendering a blank region or claiming content it does not have. This is the plan's
own step 2 instruction, recorded here because it is the honest limit of what this
phase ships.

**5. `len(daemon.API_ROUTES)` reads 13, not the plan's stated 12.** The 14C
drift reconciled in `16B-PRECONDITION.md`. This plan added no `/api/*` route, so
the value is unchanged by it.

**6. `python3` for `python`, and the full-suite criterion run with
`ANKI_CONNECT_URL=http://127.0.0.1:1/`.** Both carried forward from
`16B-02-SUMMARY.md`.

## Which truth was verified by which command

| Truth | Command | Actual result |
|---|---|---|
| Eight areas addressable, nav complete on every one | `check_course_areas_all_render` | 8 pages, 200 each, 8 labels on each |
| Notes and Search are 404 | same check | both 404 |
| An unknown course is a path-free 404 | same check | 404, no traceback, no path run |
| One route per object at both widths | `check_same_routes_both_widths` | exactly 1 match per path, identical back href |
| No pagination anywhere a reader reads | `check_no_pagination_on_reading` | 5 markers absent from 9 pages, no `Link: rel=next` |
| The restore script is enhancement, not machinery | same check | 5 banned constructs absent |
| A renamed and moved course keeps its link | `check_deep_link_scenarios` a | byte-identical path, old name gone |
| A dead anchor keeps its page | scenario b | 200, full render, help link count 0 |
| A route failure links its help page | scenario b | 404 with the link |
| A missing focus target has a real fallback | scenario c | heading id present, script branches present |
| A stale anchor is normalized | scenario c | equals `anchor_slug("gone")` |

## Artifacts changed

- `surfaces/ia.py`: `import model`, `COURSE_AREA_LABELS`,
  `AREA_NOT_FOUND_NOTICE`, `ANCHOR_NOT_FOUND_NOTICE`, `anchor_slug`,
  `deep_link_target`, `_course_dir_for`, `course_area_state`.
- `surfaces/daemon.py`: `COURSE_GET_RE`, `COURSE_AREA_RE`, `COURSE_LESSON_RE`,
  three `ROUTES` entries, three `ROUTE_CLI` entries mapping to `daemon`,
  `RESTORE_SCRIPT`, `COURSE_NOSCRIPT`, `_course_frame`, `_course_not_found`,
  `handle_course_get`, `handle_course_area_get`, `handle_course_lesson_get`.
- `tests/ia_route_roundtrip.py`: `_shelf_course_ids`,
  `check_course_areas_all_render`, `check_same_routes_both_widths`,
  `check_no_pagination_on_reading`, `check_deep_link_scenarios`.
