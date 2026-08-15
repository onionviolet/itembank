---
phase: 16B-ia-modes-recovery-contract
plan: 05
type: execute
wave: 5
depends_on: ["16B-04"]
files_modified:
  - surfaces/ia.py
  - surfaces/daemon.py
  - tests/ia_route_roundtrip.py
autonomous: true
requirements: [APP-02]
estimate:
  tokens: 88000
  raw_tokens: 88000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "All nine named course areas are addressable and render: Overview at /course/<course_id>, and Learn, Practice, Test, Course map, Sources, Build and review, and Evidence at /course/<course_id>/<area>, with Notes rendering as contextual panels inside Learn and Evidence and holding no route of its own (APP-01 named sections, D4, CourseAreaNav populated consideration)."
    - "The same route serves both layouts: no entry in ROUTES gains a second width-conditional pattern for the same object, and the identical deep link replayed with a narrow-viewport request returns the same route, the same course_id, and the same area (APP-02 fixture, CourseAreaNav partial consideration)."
    - "Route segments that name an object are opaque IDs, never titles, slugs, or ordinal positions, so renaming a course or a lesson never changes its URL (APP-02 scenario a: deep-link stability under object rename or move)."
    - "An anchor addresses a heading or term by the shipped model.lesson_slug scheme rather than by ordinal index, and surfaces/ia.py contains no second slug implementation."
    - "An unresolvable deep link or anchor is the named code ia.route_not_found routed through the offline help contract, never a bare stack trace and never a silent blank page (CourseAreaNav error consideration, DeepLinkNav error consideration)."
    - "An anchor into content that no longer exists lands on the area's own primary heading with a stated notice naming ia.route_not_found, and the surrounding page still renders in full (APP-02 scenario b: anchor into deleted content)."
    - "When the original focus target no longer exists, focus moves to the area's primary heading rather than being left on the document body, and the page states that the target was not found (APP-02 scenario c: focus restoration when the original target no longer exists)."
    - "Parent and back semantics are an explicit labelled in-page control rather than a reliance on browser history: every course-level area renders 'Back to {course name}' targeting /course/<course_id>, and Overview renders 'Back to courses' targeting /, both as real anchors that work with scripting disabled."
    - "Both back labels wrap rather than truncating mid-word, and nav labels are fixed Chrome-voice strings that no surface shortens (CourseAreaNav overflow and long-text considerations, DeepLinkNav overflow consideration)."
    - statement: "A course area with no content yet, such as Practice before any bank is bound, renders a stated area-level empty state rather than a blank region; the exact per-area empty copy is contracted at execution against each area's own record shape and confirmed by a held-out storyboard check."
      verification: backstop
    - statement: "A genuinely slow course-area read renders a stated loading state; today the render is synchronous and server-side, so no loading state is reachable, and asserting that by construction needs a held-out timing test."
      verification: backstop
    - statement: "Area lists that can grow, such as many lessons or many sources, inherit list behavior contracted per area at execution; a held-out storyboard check confirms the zero, one, and many shapes per area."
      verification: backstop
    - statement: "Focus and scroll restoration timing, applied after the server render, is confirmed by the APP-02 replay rather than asserted, because the ordering of paint, hash resolution, and focus is a browser behavior no server-side test observes."
      verification: backstop
    - statement: "Opaque deep-link display length in narrow layouts is confirmed by the APP-02 fixture rather than asserted, because how a long identifier wraps is a rendering outcome Phase 17A owns."
      verification: backstop
  prohibitions:
    - statement: "Chat must not be the home surface or the sole record of a job or an object; any conversational affordance is contextual to one object or one operation and never replaces a route, a record, or the Activity view."
      status: kept
      verification: flagged-unverified
    - statement: "A reading surface must not paginate; reading is continuous and scrolls, so no page-number control, next-page link, or item cap may appear on any course-level reading area."
      status: kept
      verification: flagged-unverified
    - statement: "A second width-conditional URL must not exist for the same object; a narrow layout is a rendering decision inside one handler, never a second route."
      status: kept
      verification: flagged-unverified
    - statement: "A course or lesson identifier in a URL must not be derived from a title or an ordinal position, because a rename or a reorder would then silently break every saved and shared link."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "surfaces/ia.py gains COURSE_AREA_LABELS, anchor_slug, deep_link_target, and course_area_state"
    - "surfaces/daemon.py gains COURSE_GET_RE, COURSE_AREA_RE, COURSE_LESSON_RE, their three route entries and ROUTE_CLI twins, and handle_course_get, handle_course_area_get, handle_course_lesson_get"
    - "surfaces/daemon.py gains the restoration script block emitted by the course-level handlers, with a noscript equivalent"
    - "tests/ia_route_roundtrip.py gains check_course_areas_all_render, check_same_routes_both_widths, check_deep_link_scenarios, and check_no_pagination_on_reading"
  key_links:
    - "The three regexes must be appended to the trailing stem-parameterised block in the order COURSE_GET_RE, COURSE_AREA_RE, COURSE_LESSON_RE. COURSE_GET_RE cannot shadow the other two because its pattern is anchored and admits no slash, but writing them out of order invites a later edit that relaxes one pattern and silently swallows the others."
    - "anchor_slug must delegate to model.lesson_slug rather than reimplement it. A second slug function would produce a second anchor vocabulary, so a link authored against the lesson reader would silently fail to resolve in the course reader, which is the class of drift a shared helper exists to prevent."
    - "Focus restoration has to be progressive enhancement over a page that already works. The Back control is a real anchor and the target heading carries a real id, so the whole contract holds with scripting disabled; the script only moves focus and adjusts scroll past the sticky context line."
    - "The unresolvable-anchor path and the unresolvable-route path are different: an unknown course or area is a 404 with the ia.route_not_found help link, while an unknown anchor inside an existing area is a 200 whose page renders fully and states the anchor was not found. Collapsing them would either hide a real page or invent a missing one."
---

<objective>
Register every course-level route, make its links stable, and make a link that
no longer resolves land somewhere useful.

`REQUIREMENTS.md` APP-02 requires "stable opaque deep links and anchors,
explicit parent and back semantics, focus and scroll restoration, and the same
routes across wide and narrow layouts". Its fixture is the same synthetic deep
links replayed across both layouts asserting identical routes and restored
focus and scroll.

The spec-less edge-coverage probe returned APP-02's row `unclassified` and
unresolved. It is not dropped. Plan 16B-01 recorded three named scenarios and
this plan executes all three: a deep link that survives a rename or a move, an
anchor into content that has been deleted, and focus restoration when the
original target no longer exists.

What this plan does **not** do is fill the eight course-level areas with real
content. `course.py` and `graph.py` shape that content and their record shapes
are outside this phase's scope; `16B-UI-SPEC.md`'s "Open Items Deferred to Other
Phases" table names real record-backed area content as Phase 14A and 14B
execution work. This plan registers the routes, proves their identity and
restoration semantics, and renders each area's frame with a stated area-level
state, so a later phase fills a frame rather than inventing one.

Decisions already made, cited, and never re-derived here:

- **`16B-DECISIONS.md` `## D3`**: course-level routes use the fixed pattern
  `/course/<course_id>/<area>` with named area segments rather than a query
  parameter, matching the shipped `/quiz/<stem>`, `/study/<stem>`, and
  `/lesson/<stem>` convention.
- **`16B-DECISIONS.md` `## D4`**: Notes get no dedicated route and render only
  as contextual panels inside Learn and Evidence.
- **`16B-DECISIONS.md` `## D5`**: Search is not built or routed by this phase.
- **`16B-DECISIONS.md` `## D-16B-1`**: the three exact regexes and their
  position in the trailing block.
- **`16B-DECISIONS.md` `## D-16B-3`**: all three course patterns map to the
  existing `daemon` CLI command, because they are browser renderings of records
  the `daemon` command already serves and `course.py` has no CLI verb yet.
- **`16B-UI-SPEC.md` "Deep link, anchor, parent/back, and resume contract"**,
  all six numbered points, binding verbatim.
- **`16B-RESEARCH.md` Pitfall 4**: layout mode is a rendering decision inside
  the handler, never a second URL for the same object.
- **`PLANNING-DIRECTIVES.md` section 4a**, quoted: `UI-SPEC.md` section 7
  "permits embedded vanilla JS in plain words", so the restoration script is
  permitted; it is written as progressive enhancement because section 4.5's nine
  accessibility gates stay in force.

Purpose: make a saved link keep working, and make a broken one land on a page
that says so.
Output: three routes, three handlers, one restoration script with a noscript
equivalent, and the APP-02 fixture executed.
</objective>

<context>
@.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-PATTERNS.md
@.planning/UI-SPEC.md
@.planning/REQUIREMENTS.md
@surfaces/ia.py
@surfaces/daemon.py
@surfaces/presentation.py
@model.py
@tests/ia_route_roundtrip.py
@fixtures/course_storyboard_corpus.py
</context>

## Artifacts this phase produces (plan 16B-05 share)

New symbols introduced by this plan, and by nothing earlier:

- `surfaces/ia.py`: `COURSE_AREA_LABELS`, `AREA_NOT_FOUND_NOTICE`,
  `ANCHOR_NOT_FOUND_NOTICE`, `anchor_slug`, `deep_link_target`,
  `course_area_state`.
- `surfaces/daemon.py`: `COURSE_GET_RE`, `COURSE_AREA_RE`, `COURSE_LESSON_RE`,
  their three `ROUTES` entries and three `ROUTE_CLI` entries,
  `handle_course_get`, `handle_course_area_get`, `handle_course_lesson_get`,
  and `RESTORE_SCRIPT`.
- `tests/ia_route_roundtrip.py`: `check_course_areas_all_render`,
  `check_same_routes_both_widths`, `check_deep_link_scenarios`,
  `check_no_pagination_on_reading`.

The phase-wide symbol union is repeated in `16B-01-PLAN.md`.

<tasks>

<task type="auto">
  <name>Task 1: the three course-level routes and the eight area frames</name>
  <files>surfaces/ia.py, surfaces/daemon.py, tests/ia_route_roundtrip.py</files>
  <read_first>
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md`, `## D3`,
  `## D4`, `## D5`, `## D-16B-1`, and `## D-16B-3`.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the
  "Course level" route table in full, all eight rows plus the Notes row.
- `surfaces/daemon.py` lines 180 to 260 as they stand after plan 16B-03, so the
  three new regexes join their siblings and the three new entries are appended
  after `("GET", HELP_GET_RE, "handle_help_get"),`.
- `surfaces/daemon.py`, `handle_activity_get` and `handle_help_get`, the handler
  shape these three copy.
- `surfaces/ia.py`, `COURSE_AREAS` and `course_shelf_state`, as they stand after
  plan 16B-04.
- `model.py`, `lesson_slug`, its exact signature and normalization behavior.
  `anchor_slug` delegates to it and reimplements nothing.
  </read_first>
  <action>
1. Add to `surfaces/ia.py`:

   - `COURSE_AREA_LABELS`, a dict over `COURSE_AREAS` giving each area its exact
     Chrome-voice nav label from the UI-SPEC Course level table:
     `"overview"` maps to `"Overview"`; `"learn"` to `"Learn"`; `"practice"` to
     `"Practice"`; `"test"` to `"Test"`; `"map"` to `"Course map"`;
     `"sources"` to `"Sources"`; `"build"` to `"Build and review"`;
     `"evidence"` to `"Evidence"`.
   - `AREA_NOT_FOUND_NOTICE = "That address does not name anything itembank can open."`
   - `ANCHOR_NOT_FOUND_NOTICE = "The part of this page that link pointed at is no longer here. The rest of the page is below."`
   - `def anchor_slug(text):` returning `model.lesson_slug(text)`, with a
     docstring stating that it is a named alias so callers read intent, that
     there is exactly one slug implementation in this repository, and that a
     second one would create a second anchor vocabulary. Add
     `import model` to the module's imports and state in the module docstring
     that this is the only name imported from `model`.
   - `def deep_link_target(course_id, area=None, lesson_id=None, anchor=None):`
     returning a plain dict with keys `path`, `area`, `label`, `back_href`,
     `back_label`, and `anchor`. `path` is `/course/<course_id>` when `area` is
     None or `"overview"`, `/course/<course_id>/<area>` for a named area, and
     `/course/<course_id>/learn/<lesson_id>` when `lesson_id` is given.
     `back_href` is `/` and `back_label` is `Back to courses` for Overview;
     `back_href` is `/course/<course_id>` and `back_label` is
     `"Back to " + course_name` for every other case, where `course_name` is
     passed in by the caller and falls back to the `course_id` when absent.
     `anchor` is the value passed through `anchor_slug` when given, else `None`.
     Raise nothing; an area not in `COURSE_AREAS` returns `area` None and
     `path` the Overview path, and the caller decides whether that is a 404.

2. Add `def course_area_state(root, course_id, area, course=_UNSET):` to
   `surfaces/ia.py`. It resolves the course module exactly as
   `course_shelf_state` does, including the `ITEMBANK_IA_NO_COURSE=1` switch,
   and returns a plain dict with keys `found`, `course_id`, `course_name`,
   `area`, `area_label`, `nav`, `notice`, `help_code`, and `content_available`:

   - `found` is False when the course directory does not exist under `root` or
     when `area` is not a member of `COURSE_AREAS`; in that case `notice` is
     `AREA_NOT_FOUND_NOTICE`, `help_code` is `"ia.route_not_found"`, and every
     other key carries a safe default.
   - `course_name` comes from the record when readable, and falls back to
     `os.path.basename` of the course directory when the record cannot be read,
     per D9.
   - `nav` is a list of dicts, one per member of `COURSE_AREAS`, each with
     `area`, `label` from `COURSE_AREA_LABELS`, `href` from `deep_link_target`,
     and `current` True for exactly one entry. The list is always all eight
     entries in `COURSE_AREAS` order regardless of layout width.
   - `content_available` is False in this phase for every area, because the
     record shapes that fill an area belong to Phases 14A and 14B; `notice` in
     that case is the area's own stated state, the literal string
     `Nothing has been added to {area_label} for this course yet.` with
     `{area_label}` substituted.

3. Add the three regexes to `surfaces/daemon.py`, beside the other `*_RE`
   constants, exactly as D-16B-1 spells them:

```
COURSE_GET_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})$")
COURSE_AREA_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/(?P<area>learn|practice|test|map|sources|build|evidence)$")
COURSE_LESSON_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/learn/(?P<lesson_id>[A-Za-z0-9_.-]{1,64})$")
```

   With a comment stating that the bounded character classes refuse a path
   separator, a percent escape, and an unbounded run, so a traversal attempt is
   refused at dispatch, and that the area alternation is a closed vocabulary
   mirroring `ia.COURSE_AREAS` minus `overview`, which `COURSE_GET_RE` serves.

4. Append three entries to the trailing stem-parameterised block of `ROUTES`,
   in this order, after `("GET", HELP_GET_RE, "handle_help_get"),`:

```
    ("GET", COURSE_GET_RE, "handle_course_get"),
    ("GET", COURSE_AREA_RE, "handle_course_area_get"),
    ("GET", COURSE_LESSON_RE, "handle_course_lesson_get"),
```

   And three `ROUTE_CLI` entries, each mapping to the literal `"daemon"`.

5. Add the three handlers to `surfaces/daemon.py`, immediately after
   `handle_help_get`:

   - `handle_course_get(handler, course_id)`: calls
     `ia.course_area_state(handler.root, course_id, "overview")`. When `found`
     is False, send a 404 through `handler.send_error(404, ia.AREA_NOT_FOUND_NOTICE)`
     and include no path; the page a learner reaches for the explanation is
     `/help/ia.route_not_found`, linked from the shelf, and the 404 body carries
     that link. Otherwise render the Overview frame: the nav list, the area
     notice, and the back control `{"href": "/", "label": "Back to courses"}`.
   - `handle_course_area_get(handler, course_id, area)`: same shape, with the
     back control `{"href": "/course/" + course_id, "label": "Back to " + course_name}`.
   - `handle_course_lesson_get(handler, course_id, lesson_id)`: same shape with
     `area` `"learn"`, and additionally emits `id="{anchor_slug(heading)}"` on
     its primary heading so an anchor has a real target.

   Every heading emitted by these handlers carries an `id` produced by
   `ia.anchor_slug`. Every nav entry is a real anchor. No handler emits a
   pagination control, a page-number link, a next-page link, or an item cap.

6. Add `check_course_areas_all_render()` to `tests/ia_route_roundtrip.py`. With
   one real daemon over `build_two_course_shelf`'s directory, for
   `course_id = "crs-kestrel-01"`:
   - `GET /course/crs-kestrel-01` returns 200 and its body contains
     `Back to courses`.
   - For each of the seven named area segments, `GET /course/crs-kestrel-01/<area>`
     returns 200, its body contains that area's exact label from
     `COURSE_AREA_LABELS`, and its body contains `Back to `.
   - Every one of the eight labels appears in the nav of every one of the eight
     pages, so the nav is complete on every area.
   - `GET /course/crs-kestrel-01/notes` returns 404, because Notes has no route
     per D4.
   - `GET /course/crs-kestrel-01/search` returns 404, per D5.
   - `GET /course/no-such-course` returns 404 and its body contains no
     `Traceback` and no `os.sep` run.

7. Update `main()` to run sixteen checks and print
   `"IA ROUTES: 16 passed, 0 failed"`. Run:

```
python tests/ia_route_roundtrip.py
python tests/daemon_roundtrip.py
```

   Expected: exit 0 from both.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_route_roundtrip.py && python tests/daemon_roundtrip.py</automated>
Expected: `IA ROUTES: 16 passed, 0 failed` and exit 0, then exit 0, which proves
`check_route_cli_inventory` still passes with three new routes and three new
twins. The degraded state this task proves is the unknown-course and
unknown-area 404: it carries no path and no traceback, and Notes and Search both
return 404 by design rather than by accident.
  </verify>
  <acceptance_criteria>
- `python tests/ia_route_roundtrip.py` exits 0 with final line
  `IA ROUTES: 16 passed, 0 failed`.
- `python tests/daemon_roundtrip.py` exits 0.
- All eight course areas return 200 and every page's nav lists all eight labels.
- `GET /course/<id>/notes` and `GET /course/<id>/search` both return 404.
- `GET /course/no-such-course` returns 404 whose body contains no `Traceback`.
- `python -c "import sys; sys.path.insert(0,'.'); from surfaces import ia; import model; print(ia.anchor_slug('Airway Adjuncts') == model.lesson_slug('Airway Adjuncts'))"`
  prints `True`.
- A grep of `surfaces/ia.py` for `re.sub` and `lower()` inside any function
  named like a slug shows no second slug implementation; the only slug path is
  the one-line delegation in `anchor_slug`.
- No course-level page body contains any of `Next page`, `Previous page`,
  `page=`, or `rel="next"`.
- `len(daemon.API_ROUTES)` is still `12`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="costly">These four route literals become the app's
  bookmarkable identity: `/course/<id>` and its seven area suffixes are what a
  saved link, a shared link, and every later phase's deep link point at, and
  changing a segment after that breaks links that already exist. That one-way
  door was confirmed before this task rather than by it: the shape was settled
  by the checker-approved `16B-UI-SPEC.md` Decision D3 on 2026-08-15 and the
  exact patterns by `16B-DECISIONS.md` D-16B-1, transcribed by plan 16B-01 Task
  1 in the same plan as its blocking checkpoint. This task transcribes, so its
  own cost is a coordinated re-transcription rather than a fresh
  decision.</reversibility>
  <done>All eight areas are addressable, Notes and Search are deliberately not,
  and an unresolvable course is a path-free 404.</done>
</task>

<task type="auto">
  <name>Task 2: parent and back semantics, focus and scroll restoration, one route per object at every width</name>
  <files>surfaces/daemon.py, tests/ia_route_roundtrip.py</files>
  <read_first>
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the
  "Deep link, anchor, parent/back, and resume contract" points 3, 4, and 5, in
  full, and the Spacing Scale section's inherited RTS-02 constraint that the
  sticky context line never exceeds two rows and that a card already fully in
  view is not scrolled.
- `.planning/UI-SPEC.md` section 7, the sentence permitting embedded vanilla
  JavaScript, and section 8, the nine accessibility gates, in full. The script
  written here is progressive enhancement and must not be load-bearing for any
  gate.
- `surfaces/presentation.py`, `surface_shell`'s `back` and `noscript`
  parameters and `context_line`, all three already shipped.
- `surfaces/daemon.py`, the three handlers written in Task 1.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md`, Pitfall 4
  in full.
  </read_first>
  <action>
1. Confirm the back control is already a real anchor and needs no script:
   `presentation.surface_shell` renders `back` as
   `<p class="back"><a href="...">&larr; label</a></p>`. Pass
   `back={"href": "/", "label": "Back to courses"}` from `handle_course_get` and
   `back={"href": "/course/" + course_id, "label": "Back to " + course_name}`
   from the other two. Add no second back mechanism and do not call
   `history.back()` anywhere.

2. Add `RESTORE_SCRIPT` to `surfaces/daemon.py`, a module-level string holding
   one small vanilla script emitted only by the three course-level handlers. It
   does exactly four things and nothing else:

   - On load, when `location.hash` is non-empty, look up
     `document.getElementById(hash.slice(1))`.
   - When that element exists, call `scrollIntoView({block: "start"})` on it,
     then set `tabIndex = -1` and call `focus({preventScroll: true})`, then
     adjust `window.scrollBy(0, -contextLineHeight)` where `contextLineHeight`
     is the measured `offsetHeight` of the element carrying
     `data-surface-context`, or 0 when that element is absent. Skip the scroll
     entirely when the target's bounding rectangle is already fully inside the
     viewport, which is RTS-02's "a card already fully in view is not scrolled".
   - When that element does **not** exist, move focus to the page's single `h1`
     instead, and reveal a region already present in the DOM carrying
     `data-anchor-missing` whose text is `ia.ANCHOR_NOT_FOUND_NOTICE`.
   - On a `pagehide` event, write `{path, hash, scrollY, activeId}` to
     `sessionStorage` under one fixed key; on load, when the current path
     matches a stored entry and `location.hash` is empty, restore `scrollY` and
     focus the stored `activeId` when that element still exists, else focus the
     `h1`.

   The script adds no library, no framework, no polyfill, and no network
   request. It never changes page content other than revealing the
   already-rendered `data-anchor-missing` region.

3. Render the `data-anchor-missing` region server-side, present in the DOM and
   hidden with the `hidden` attribute, so the script reveals rather than
   injects. Pass
   `noscript="Links to a specific part of this page still work. Your browser jumps to it without the extra focus handling."`
   into `surface_shell` from all three handlers, so the scripting-disabled state
   is stated rather than silent.

4. Add `check_same_routes_both_widths()` to `tests/ia_route_roundtrip.py`. For
   each of the eight area paths it issues two requests against the same daemon,
   one with no extra headers and one with a narrow-viewport hint header
   (`Sec-CH-Viewport-Width: 360` and `Viewport-Width: 360`), and asserts:
   - Both responses return 200.
   - Both were served by the same route: assert by matching the request path
     against `daemon.ROUTES` in Python and confirming exactly one entry matches
     and that it is the same entry for both requests.
   - `daemon.ROUTES` contains no two entries whose patterns both match any of
     the eight paths, so no width-conditional second route exists. Implement as:
     for each of the eight paths, the count of matching `ROUTES` entries is
     exactly 1.
   - No response body differs in its `<a class="back"` href between the two
     requests.

5. Add `check_no_pagination_on_reading()`. Against every course-level page and
   the shelf, assert none of `Next page`, `Previous page`, `page=`,
   `rel="next"`, or `rel="prev"` appears. Assert also that no response carries a
   `Link` header with `rel=next`.

6. Update `main()` to run eighteen checks and print
   `"IA ROUTES: 18 passed, 0 failed"`. Run the full suite:

```
python tests/ia_route_roundtrip.py
for t in tests/*.py; do python "$t" || exit 1; done
```

   Expected: `IA ROUTES: 18 passed, 0 failed` and exit 0; exit 0.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_route_roundtrip.py</automated>
Expected: final line `IA ROUTES: 18 passed, 0 failed`, exit 0. The degraded
state this task proves is the scripting-disabled path: the back control is a
real anchor and the anchor target is a real `id`, both present in the served
HTML with no script executed, and the `noscript` sentence states what changes.
  </verify>
  <acceptance_criteria>
- `python tests/ia_route_roundtrip.py` exits 0 with final line
  `IA ROUTES: 18 passed, 0 failed`.
- Every one of the eight course-level paths matches exactly one entry in
  `daemon.ROUTES`, asserted in Python over the real tuple.
- Every course-level response contains `<p class="back"><a href=` and the exact
  back label for its level.
- Every course-level response contains a `data-anchor-missing` element carrying
  the exact `ANCHOR_NOT_FOUND_NOTICE` text and the `hidden` attribute.
- Every course-level response contains the `noscript` sentence
  `Links to a specific part of this page still work. Your browser jumps to it without the extra focus handling.`
- `RESTORE_SCRIPT` contains none of the substrings `history.back`, `fetch(`,
  `XMLHttpRequest`, `document.write`, or `innerHTML =`.
- No course-level or shelf response contains any of `Next page`,
  `Previous page`, `page=`, `rel="next"`, `rel="prev"`, and no response carries a
  `Link` header with `rel=next`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">A progressive-enhancement script and two
  server-rendered regions. Removing the script leaves every route, anchor, and
  back control working.</reversibility>
  <done>Back is a labelled anchor, an anchor lands on a real target, one route
  serves both widths, and nothing reading paginates.</done>
</task>

<task type="auto">
  <name>Task 3: the three APP-02 scenarios the probe left unresolved</name>
  <files>surfaces/ia.py, tests/ia_route_roundtrip.py</files>
  <read_first>
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md`, the
  `## APP-02 probe enumeration` section, which names the three scenarios this
  task executes.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, points 1, 2,
  and 4 of the deep-link contract.
- `surfaces/ia.py`, `deep_link_target` and `course_area_state` as written in
  Task 1.
- `fixtures/course_storyboard_corpus.py`, `FakeCourseModule`, as written in plan
  16B-04.
  </read_first>
  <action>
1. Add `check_deep_link_scenarios()` to `tests/ia_route_roundtrip.py`, covering
   all three enumerated scenarios in one check with three clearly named
   sections.

2. **Scenario a, deep-link stability under rename or move.** In process, build a
   `FakeCourseModule` whose record for `crs-kestrel-01` carries the name
   `Kestrel County Field Basics`. Compute
   `deep_link_target("crs-kestrel-01", "learn")` and record its `path`. Change
   the record's `name` to `Kestrel Field Skills` and move the course directory
   to a new parent directory inside the same temp root. Recompute the target and
   assert:
   - `path` is byte-identical to the recorded value, because the segment is the
     opaque `course_id` and not the name.
   - `back_label` changed to `Back to Kestrel Field Skills`, because the label
     is display text and is expected to follow the rename.
   - No returned field contains the old name.

3. **Scenario b, an anchor into deleted content.** Start a real daemon over the
   fixture directory. Request `GET /course/crs-kestrel-01/learn#no-such-heading`
   and, because a fragment is never sent to the server, request the same path
   without the fragment and assert:
   - Status 200 and the whole area page renders, including all eight nav labels
     and the back control.
   - The page carries the hidden `data-anchor-missing` region with the exact
     `ANCHOR_NOT_FOUND_NOTICE` text, which is the region the client script
     reveals when the id is not found.
   - The page carries no server-side 404 and no `ia.route_not_found` link,
     because the route resolved and only the anchor did not. Assert the
     distinction explicitly: the body contains
     `href="/help/ia.route_not_found"` zero times.
   - Then assert the other half of the distinction: `GET /course/crs-kestrel-01/nosucharea`
     returns 404 and its body **does** contain
     `href="/help/ia.route_not_found"`.

4. **Scenario c, focus restoration when the original target no longer exists.**
   Assert the server-side half, which is the half a Python test can prove:
   - The page's single `h1` carries an `id` produced by `ia.anchor_slug`, so the
     script has a real fallback target to focus.
   - `RESTORE_SCRIPT` contains the literal substring
     `document.getElementById` and a branch that focuses the `h1` when the hash
     target is absent, asserted by finding both the `h1` selector and the
     `data-anchor-missing` selector in the script text.
   - `course_area_state` for an existing course and area returns `found` True
     while `deep_link_target(course_id, area, anchor="gone")` returns an
     `anchor` value equal to `ia.anchor_slug("gone")`, so a stale anchor is
     normalized rather than passed through raw.

   Record explicitly in `16B-05-SUMMARY.md` that the browser half of scenario c,
   the actual focus move after paint, is not asserted by this suite and is
   carried as the DeepLinkNav loading backstop row, confirmed by the APP-02
   replay rather than by construction. Do not claim a browser behavior this
   suite did not observe.

5. Update `main()` to run nineteen checks and print
   `"IA ROUTES: 19 passed, 0 failed"`. Run:

```
python tests/ia_route_roundtrip.py
for t in tests/*.py; do python "$t" || exit 1; done
python itembank.py guard .
```

   Expected: `IA ROUTES: 19 passed, 0 failed` and exit 0; exit 0;
   `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_route_roundtrip.py</automated>
Expected: final line `IA ROUTES: 19 passed, 0 failed`, exit 0. The degraded
states this task proves are exactly the three enumerated scenarios: a renamed
and moved course keeps its link, a dead anchor keeps its page, and a missing
focus target has a real fallback.
  </verify>
  <acceptance_criteria>
- `python tests/ia_route_roundtrip.py` exits 0 with final line
  `IA ROUTES: 19 passed, 0 failed`.
- Scenario a: the `path` before and after a rename and a directory move is
  byte-identical, and no returned field carries the old name.
- Scenario b: an existing area with a dead anchor is 200, renders in full,
  carries the `data-anchor-missing` region, and contains
  `href="/help/ia.route_not_found"` zero times; an unknown area is 404 and
  contains that link at least once.
- Scenario c: the page's `h1` carries an `id` equal to
  `ia.anchor_slug(<the heading text>)`, and `RESTORE_SCRIPT` contains both the
  `h1` fallback branch and the `data-anchor-missing` selector.
- `16B-05-SUMMARY.md` states in plain words that the post-paint focus move was
  not observed by this suite and is carried as a backstop row.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0 and
  `python itembank.py guard .` reports `0 offending files`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Test coverage plus two notice constants.
  </reversibility>
  <done>The three scenarios the probe left unresolved are executed rather than
  assumed, and the one half no Python test can see is named as unproven rather
  than claimed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| URL path segments to filesystem lookup | `course_id`, `area`, and `lesson_id` are attacker-influenced under `--lan` and select a directory. |
| URL fragment to DOM lookup | An anchor value reaches `getElementById` in the browser. |
| sessionStorage to focus target | Restoration reads a value the page itself wrote earlier. |
| course record to nav and heading text | A record supplies the course name rendered into the back label and headings. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16B-05-01 | Tampering | path traversal through `course_id` or `lesson_id` | high | mitigate | Both segments are bounded `[A-Za-z0-9_.-]{1,64}` classes admitting no separator and no percent escape, refused at dispatch before any handler runs; the acceptance criteria assert unknown and malformed paths return 404. |
| T-16B-05-02 | Tampering | the `area` segment reaching a filesystem or attribute lookup | high | mitigate | `area` is a closed alternation inside `COURSE_AREA_RE` mirroring `ia.COURSE_AREAS`, so a value outside the eight never matches a route; Notes and Search are asserted to 404. |
| T-16B-05-03 | Information Disclosure | a filesystem path or traceback in a course 404 | high | mitigate | The 404 is sent through the shipped `send_error`, which never emits a path or a traceback (T-2-05); the criteria assert no `Traceback` and no `os.sep` run in the body. |
| T-16B-05-04 | Tampering | script injection through a course name in the back label or a heading | high | mitigate | Every record-derived string is emitted through `presentation.esc`, and the restoration script never assigns `innerHTML` and never reads a record value; the criteria forbid `innerHTML =` and `document.write` in `RESTORE_SCRIPT`. |
| T-16B-05-05 | Tampering | the restoration script becoming load-bearing for navigation | medium | mitigate | Back is a real anchor, the anchor target is a real `id`, and the missing-anchor notice is server-rendered and merely revealed; the `noscript` sentence states what changes without scripting. |
| T-16B-05-06 | Information Disclosure | sessionStorage retaining a path or an element id across contexts | low | accept | The stored record is one path, one hash, one scroll offset, and one element id, all values the same origin already rendered; it is per-origin, per-session, and cleared by the browser, and the single-learner local product has no second party to leak to. |
| T-16B-05-07 | Spoofing | a width-conditional second URL for the same object | medium | mitigate | `check_same_routes_both_widths` asserts each of the eight paths matches exactly one `ROUTES` entry and that the same entry serves both the default and the narrow-hint request. |
| T-16B-05-08 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; the restoration script is inline vanilla JavaScript with no library, no polyfill, and no network request, and the criteria forbid `fetch(` and `XMLHttpRequest` in it. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- **No real area content.** Learn does not render lessons, Practice does not
  start a session, Test does not open a sitting, Course map does not project an
  outline, Sources does not list bindings, Build and review does not show a
  diff, and Evidence does not compose the honest-progress tuple. Every area
  renders its frame, its nav, and its stated area-level state. Filling them
  needs `course.py` and `graph.py` record shapes this phase does not own, and
  `16B-UI-SPEC.md`'s "Open Items Deferred to Other Phases" table assigns that to
  Phase 14A and 14B execution.
- **No Notes route and no Search route**, per D4 and D5. Both are asserted to
  404 rather than left undefined.
- No chat surface of any kind. Any conversational affordance is contextual to
  one object or operation and is not built here.
- No `course` CLI verb. D-16B-3 maps all three patterns to `daemon` and names a
  `course` verb as waiting for `course.py` to have a CLI-shaped capability.
- No client-side routing, no single-page application shell, no history
  manipulation. The restoration script never calls `history.back`,
  `history.pushState`, or `history.replaceState`.
- No new visual constant, no CSS rule, no media query. Narrow-layout rendering
  differences are Phase 17A's.
</out_of_scope>

<flagged_assumptions>
- **APP-02's edge-coverage probe row is unresolved and is carried as an explicit
  assumption, not as coverage.** The planner enumerated three scenarios and this
  plan executes all three. A reviewer who judges the enumeration incomplete
  should add a fourth scenario to this plan rather than treat the row as
  covered.

- **The browser half of scenario c is not observed by this suite.** A Python
  test that drives a subprocess daemon sees served bytes; it does not see focus
  after paint. Task 3 step 4 asserts the server-side half and requires the
  summary to state plainly that the post-paint focus move was not observed,
  carried as the DeepLinkNav loading backstop row. Claiming it would be claiming
  a behavior nothing exercised.

- **Every course area renders `content_available` False in this phase.** That is
  a scope statement, not a defect. If a later reading finds that a 14B record
  shape is already sufficient to fill one area, filling it is that phase's task
  and not a silent extension of this one.

- **The CourseAreaNav empty and zero-one-many rows and the DeepLinkNav loading
  and long-text rows are carried as backstop markers**, because per-area empty
  copy and per-area list behavior depend on record shapes this phase does not
  own, and both restoration timing and narrow-layout wrapping are browser and
  17A outcomes. At verification time, no explicit evidence for a backstop row is
  `insufficient_spec` and needs a human, never a silent pass.
</flagged_assumptions>

<summary_obligations>
`16B-05-SUMMARY.md` records: the final line of every verify command; the exact
count of `ROUTES` entries matching each of the eight course-level paths; the
before and after `path` values from scenario a, quoted, proving byte identity;
which of the two distinct not-found behaviors each of scenario b's two requests
produced; the plain statement that the post-paint focus move was not observed by
this suite and is a backstop row; the exact `noscript` sentence as served; the
final values of `len(daemon.ROUTES)` and `len(daemon.API_ROUTES)`; which truth
was verified by which command with its actual stdout; and any deviation from
this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16B-ia-modes-recovery-contract/16B-05-SUMMARY.md`
when done.
</output>
