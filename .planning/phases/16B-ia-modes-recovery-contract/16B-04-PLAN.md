---
phase: 16B-ia-modes-recovery-contract
plan: 04
type: execute
wave: 4
depends_on: ["16B-03"]
files_modified:
  - fixtures/course_storyboard_corpus.py
  - surfaces/ia.py
  - surfaces/daemon.py
  - tests/ia_route_roundtrip.py
  - .planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
autonomous: true
requirements: [APP-01]
estimate:
  tokens: 84000
  raw_tokens: 84000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "The home surface is a course shelf: GET / renders one card per course with that course's exact resume cue and its attention state, and the two-course fixture with one corrupted course renders one healthy card fully beside one degraded card in the same response (APP-01 fixture, CourseShelf partial consideration)."
    - "A zero-course shelf renders the exact heading 'No courses yet' and the exact body 'Start with the sample course, or bind a source to create your first course.', not a blank region (APP-01 empty edge, CourseShelf empty consideration)."
    - "Two courses whose display names are identical remain two distinct cards keyed by course ID; names are never merged, deduplicated, or collapsed (APP-01 adjacency edge)."
    - "Shelf ordering is total and deterministic: cards sort by attention rank, then by most recent recorded activity descending, then by course ID ascending, so two courses with equal attention states always render in the same order across runs (APP-01 ordering edge, D-16B-10)."
    - "A course whose record cannot be read still renders: its card shows the chip 'Showing last valid overview' and offers both 'Open last valid overview' and 'View files', so a corrupted course is never a dead end (APP-01 fixture, CourseShelf error consideration)."
    - "The populated happy path renders every named attention state with its exact chip text and never with color alone: up to date, due, pending review, needs your input, needs reconciliation, and showing last valid overview each carry a required text label (CourseShelf populated consideration)."
    - "Zero renders the empty state, one course renders through the identical card structure many courses render through with no singular-copy special case, and many courses scroll rather than paginate (CourseShelf zero-one-many consideration)."
    - "Card names wrap to a second line rather than truncating, and no rendered card name is shortened or elided by the surface (CourseShelf long-text consideration)."
    - "AMENDED 2026-08-27 by owner ruling (USER-VISION.md; IL-20260827-01). A percent character and a progress percentage MAY appear on a shelf card, chip, or resume cue. What survives from the original clause: a percentage is derived from a real numerator over a real denominator the record carries, and a denominator that is absent reports indeterminate rather than an invented percent (FLOW-02 precision edge, Pitfall 3). Original clause, superseded, preserved for trace: 'No surface derives or rounds a progress percentage: no shelf card, chip, or resume cue contains a percent character, and a denominator appears only when the underlying record carried one.'"
    - "When the course module is absent or reports no courses, GET / renders the shipped bank and plan listing byte-for-byte as it does today, so the entry point degrades to its previous meaning rather than to an error (D1)."
    - statement: "A genuinely slow multi-root course read renders a stated loading state rather than a blank shelf; today the read is synchronous and server-rendered, so no loading state is reachable, and asserting that by construction needs a held-out timing test rather than a claim."
      verification: backstop
    - statement: "A many-course shelf scrolls rather than clipping; the exact scroll container and its overflow treatment are a Phase 17A rendering decision confirmed by a held-out visual test at 17A."
      verification: backstop
    - statement: "A shelf read concurrent with a job mutating course state shows the last accepted state with no torn read, which the atomic write rule guarantees; confirmed by the plan 16B-09 interruption fixture rather than asserted here."
      verification: backstop
  prohibitions:
    - statement: "OVERTURNED 2026-08-27 by owner ruling (USER-VISION.md; IL-20260827-01; Phase 16 synthesis 12.4 overturn note). A single aggregate completion, mastery, or readiness percentage MAY appear on a course card. Original prohibition, preserved for trace: 'A single aggregate completion, mastery, or readiness percentage must not appear on a course card, because a ratio synthesized across incompatible evidence dimensions is a fabricated measurement presented as fact.' The 2026-08-26 Navigate2 teardown measured that that product's equivalent bar at 90.6 self-report and is the field evidence the ruling overruled; it is recorded, not reopened."
      status: overturned-by-owner-2026-08-27
      verification: not-applicable
    - statement: "A resume cue must not be guessed, cached client-side, or carried over from a previous render; when the underlying record is unavailable the cue reads 'Not started' or 'Showing last valid overview' and never a stale value."
      status: kept
      verification: flagged-unverified
    - statement: "Two courses must not be merged because their names match; identity is the opaque course ID and a name is display text."
      status: kept
      verification: flagged-unverified
    - statement: "Real course, learner, or exam material must not enter the repository through the storyboard fixture; every course, objective, and lesson in it is invented."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "fixtures/course_storyboard_corpus.py with build_two_course_shelf, build_corrupted_course, build_same_name_pair, and a FakeCourseModule stand-in"
    - "surfaces/ia.py gains ATTENTION_COPY, ATTENTION_TOKENS, ATTENTION_ORDER, SHELF_EMPTY_HEADING, SHELF_EMPTY_BODY, and course_shelf_state"
    - "surfaces/daemon.py's handle_index gains the course-shelf branch, gated on course existence, with the shipped bank and plan listing as its unchanged fallback"
    - "16B-DECISIONS.md gains the dated D-16B-10 shelf-ordering rule"
  key_links:
    - "The corrupted-course card must be built from the directory's own basename, never from a resolved absolute path and never from a partially parsed record, because the one thing known about a record that failed to parse is that its contents cannot be trusted to be safe to display."
    - "handle_index's course branch must be additive: when the course module is absent or the course list is empty, the function's existing bank and plan listing runs unchanged. Replacing that body rather than branching around it would delete a shipped surface to add a new one, and the shipped daemon suite asserts the old page."
    - "course_shelf_state takes the course module as an injectable parameter for the same reason activity_view_state takes the journal module: the corrupted-record and module-absent paths are otherwise unreachable in a tree whose precondition already proved 14B landed, and the phase would ship two states it never executed."
    - "Ordering must be a total order with course ID last, or a shelf with two equally-attentive courses renders in dict or filesystem order, which differs between runs and between platforms and makes the ordering edge row unprovable."
---

<objective>
AMENDED 2026-08-27 BY OWNER RULING. Weibao ruled that a percent is permitted
even where it breaks a contract clause, and that `USER-VISION.md` outranks any
other contract in this repository. Six places in this plan carried the percent
prohibition and all six are amended in place, each preserving its original
wording for trace: the must-have truth in the frontmatter, the `status: kept`
prohibition, the D7 and Pitfall 3 restatement in the inputs list, the behaviour
assertion in Task 2, the docstring rule in Task 2, and threat T-16B-04-05's
mitigation. Nothing else in this plan changes. Note that `16B-DECISIONS.md` D7
and `16B-RESEARCH.md` Pitfall 3 are separate documents and are NOT amended
here. `16B-RESEARCH.md` Pitfall 3 and its anti-pattern row WERE amended the
same day. `16B-DECISIONS.md` does not exist yet, because plan 16B-01 creates it
and 16B-01 has not run, so D7 must be written in its amended form when that
file is first authored rather than retrofitted. The
replacement rule throughout is that a percentage must carry the numerator and
denominator it was derived from, and that a record supplying neither reports
indeterminate rather than an invented number. Trace: `USER-VISION.md`
2026-08-27, `IDEA-LEDGER.md` IL-20260827-01, `REQUIREMENTS.md` GRAPH-03
amendment, Phase 16 synthesis section 12.4 overturn note.

Turn the app's entry point into a course shelf, and make a course that will not
load still open.

`REQUIREMENTS.md` APP-01 states that "the home surface is a course shelf with an
exact resume cue and attention state" and that "banks are assessment artifacts
inside courses, not the primary navigation unit". `UI-SPEC.md` section 15.5
records that this supersedes the shipped bank-first entry language. The shipped
`GET /` is today a bank and plan index (`surfaces/daemon.py:939-964`), and
Decision D1 settles that the shelf lives inside that same `handle_index`, gated
on whether any course exists, so the literal route `"/"` and its CLI mapping
`daemon` are unchanged and the old listing survives as the fallback rather than
being deleted.

The corrupted-course half is the part worth building carefully. APP-01's fixture
is "two fictional courses, one corrupted so it must show its last valid overview
and plain-file access". A record that failed to parse is a record whose contents
cannot be trusted, so the degraded card is built from the directory basename and
nothing else, and it still offers two real ways forward.

Decisions already made, cited, and never re-derived here:

- **`16B-DECISIONS.md` `## D1`**: the course shelf lives inside the existing
  `handle_index`, gated on course existence; when no course exists the shipped
  bank and plan listing renders unchanged; the literal `"/"` and its
  `ROUTE_CLI` value `daemon` do not change.
- **`16B-DECISIONS.md` `## D7`** and **`16B-RESEARCH.md` Pitfall 3**: AMENDED
  2026-08-27 by owner ruling. A percent-complete number is permitted, provided
  it carries the numerator and denominator it came from. The attention cue
  stays qualitative and built from named denominators, which the ruling does
  not reach. Original: "no percent-complete number, and the attention cue is
  qualitative and built from named denominators." **`D7` in `16B-DECISIONS.md`
  Pitfall 3 in `16B-RESEARCH.md` was amended on the same date. `D7` does not
  exist on disk yet (plan 16B-01 creates `16B-DECISIONS.md`), so it must be
  authored in its amended form rather than retrofitted.**
- **`16B-DECISIONS.md` `## D9`**: path-bearing copy shows the basename only.
- **`16B-UI-SPEC.md` Copywriting Contract**, rows for the two primary CTAs, the
  empty-state heading, the empty-state body, and the corrupted-course row.
- **`16B-UI-SPEC.md` Color section**, "New semantic-token assignments" table:
  the six attention states and their exact required labels, each carrying a text
  label so no state is signalled by color alone.
- **`16B-UI-SPEC.md` route contract point 6**: the resume cue is server-computed
  and never guessed or cached client-side.
- **`16B-RESEARCH.md` Don't Hand-Roll**, the "Progress/completion reporting" row:
  compose the honest-progress tuple, never a rollup.

One decision this plan locks and Task 2 appends to `16B-DECISIONS.md` as
`## D-16B-10. Course-shelf ordering`:

The shelf sorts by a total order with three keys, in this priority: first the
index of the card's attention state in `ATTENTION_ORDER`, which is the literal
tuple `("needs_input", "needs_reconciliation", "pending_review", "due",
"last_valid_overview", "up_to_date")`; then the card's most recent recorded
activity timestamp, descending, with a missing timestamp sorting last; then the
course ID, ascending, as the final tiebreak. The rationale is that the APP-01
ordering edge requires determinism among equal attention states and the course
ID is the only field guaranteed unique and stable, and that `ATTENTION_ORDER`
puts the states that need a human first without ever synthesizing a score.

Purpose: make the first screen answer "what should I do next" from durable
records, and make a broken course a door rather than a wall.
Output: one synthetic corpus, one read model, one branch inside a shipped
handler, and the APP-01 fixture executed.
</objective>

<context>
@.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-PATTERNS.md
@.planning/REQUIREMENTS.md
@surfaces/ia.py
@surfaces/daemon.py
@surfaces/presentation.py
@tests/ia_route_roundtrip.py
@fixtures/grandchild_spawner.py
</context>

## Artifacts this phase produces (plan 16B-04 share)

New symbols introduced by this plan, and by nothing earlier:

- `fixtures/course_storyboard_corpus.py` (whole file) and on it:
  `FICTIONAL_COURSES`, `FakeCourseModule`, `build_two_course_shelf`,
  `build_corrupted_course`, `build_same_name_pair`.
- `surfaces/ia.py`: `ATTENTION_COPY`, `ATTENTION_TOKENS`, `ATTENTION_ORDER`,
  `SHELF_EMPTY_HEADING`, `SHELF_EMPTY_BODY`, `course_shelf_state`.
- `surfaces/daemon.py`: the course-shelf branch inside `handle_index`.
- `tests/ia_route_roundtrip.py`: `check_shelf_state_shape`,
  `check_shelf_ordering_is_total`, `check_shelf_corrupted_course`,
  `check_shelf_end_to_end`, `check_shelf_falls_back_to_bank_index`.
- `16B-DECISIONS.md`: the heading `## D-16B-10. Course-shelf ordering`.

The phase-wide symbol union is repeated in `16B-01-PLAN.md`.

<tasks>

<task type="auto">
  <name>Task 1: the synthetic two-course corpus and the course-module stand-in</name>
  <files>fixtures/course_storyboard_corpus.py</files>
  <read_first>
- `fixtures/grandchild_spawner.py` in full, the closest real Python fixture
  generator in this repository and the module shape this file copies.
- `.planning/REQUIREMENTS.md`, `APP-01`'s Fixture sentence verbatim: "the 16B
  storyboard's synthetic course shelf with two fictional courses, one corrupted
  so it must show its last valid overview and plain-file access, asserting exact
  resume cues and every named course section".
- `.planning/phases/14B-graph-course-package-prototype/14B-01-PLAN.md`, the
  "Artifacts this phase produces" section, for `course.COURSE_SIDECAR_FILENAME`
  and `course.read_course`'s signature. These are plan-text signatures; step 1
  below re-verifies them live and records any deviation.
- `.claude/CLAUDE.md`, the Data constraint: no real question banks or real
  learner content in this repository, enforced by `itembank guard` in CI.
  </read_first>
  <action>
1. Re-verify the two 14B names this file is written against, and record the
   result in the summary rather than assuming:

```
python -c "import course; print(course.COURSE_SIDECAR_FILENAME, course.read_course.__doc__ is not None)"
python -c "import inspect, course; print(inspect.signature(course.read_course))"
```

   Record both outputs verbatim. If `read_course`'s parameter list differs from
   a single positional course-directory path, record the deviation in
   `16B-04-SUMMARY.md` and adapt `FakeCourseModule` to match the landed
   signature. Do not adapt by guessing a second signature into `ia.py`;
   `course_shelf_state` calls exactly one shape and this fixture mirrors it.

2. Create `fixtures/course_storyboard_corpus.py` with a module docstring
   stating: that every course, objective, lesson, and item in it is invented;
   that no real course, exam, clinical, or learner material appears; that the
   corpus exists to drive the 16B storyboard and route fixtures; and that the
   Activity naming distinction from D6 applies to any activity-shaped content it
   contains.

3. Define `FICTIONAL_COURSES`, a tuple of three dicts, each with the keys
   `course_id`, `name`, `attention`, `due_count`, `pending_review_count`,
   `resume_cue`, and `last_activity`. Use these exact values:

   - `{"course_id": "crs-kestrel-01", "name": "Kestrel County Field Basics",
     "attention": "due", "due_count": 3, "pending_review_count": 0,
     "resume_cue": "Continue reading: Airway adjuncts",
     "last_activity": "2026-03-02T09:00:00Z"}`
   - `{"course_id": "crs-mirefield-02", "name": "Mirefield Numeracy",
     "attention": "up_to_date", "due_count": 0, "pending_review_count": 0,
     "resume_cue": "Not started", "last_activity": None}`
   - `{"course_id": "crs-halloway-03", "name": "Halloway Systems Reading",
     "attention": "pending_review", "due_count": 0,
     "pending_review_count": 2,
     "resume_cue": "Continue draft review: 2 findings to resolve",
     "last_activity": "2026-03-01T18:30:00Z"}`

4. Define `class FakeCourseModule:` with a docstring stating in its first line
   that it is an explicit synthetic stand-in for `course.py`, named as a
   stand-in so no reader mistakes it for the real module, and that the real
   module is exercised by `check_shelf_end_to_end`. It carries:
   - `COURSE_SIDECAR_FILENAME`, defaulting to the value read in step 1.
   - `__init__(self, records, unreadable=())` storing a mapping of course
     directory name to record dict, and a set of directory names whose
     `read_course` raises.
   - `read_course(self, course_dir)` returning the stored record, or raising
     `ValueError("synthetic corrupted course record")` when the directory's
     basename is in `unreadable`.

5. Define `build_two_course_shelf(dest_dir)`. It creates one subdirectory per
   course under `dest_dir`, named exactly by the course id, each containing an
   empty file named `COURSE_SIDECAR_FILENAME`, for the first two entries of
   `FICTIONAL_COURSES`. It returns a `FakeCourseModule` seeded with both records
   and an empty `unreadable` set, plus the list of directory paths it made.

6. Define `build_corrupted_course(dest_dir)`. It creates the same two
   directories as `build_two_course_shelf` and returns a `FakeCourseModule`
   whose `unreadable` set contains exactly `"crs-mirefield-02"`, so one card is
   healthy and one is degraded. This is the APP-01 fixture.

7. Define `build_same_name_pair(dest_dir)`. It creates two directories,
   `crs-twin-a` and `crs-twin-b`, whose records both carry the identical `name`
   value `Field Basics` and different `course_id` values, with equal `attention`
   `up_to_date` and equal `last_activity` `"2026-03-01T00:00:00Z"`. This drives
   both the adjacency edge and the ordering tiebreak.

8. Every builder writes deterministic bytes: no `random`, no timestamp taken
   from the clock, no path outside `dest_dir`. No `.md` file is written by any
   builder, so `itembank guard .` is unaffected by this fixture; state that in
   the module docstring.

9. Run:

```
python -c "import sys; sys.path.insert(0,'fixtures'); import course_storyboard_corpus as c; import tempfile; d=tempfile.mkdtemp(); m,dirs=c.build_corrupted_course(d); print(len(dirs), sorted(m.unreadable))"
python itembank.py guard .
```

   Expected: the first prints `2 ['crs-mirefield-02']`; the second reports
   `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python -c "import sys; sys.path.insert(0,'fixtures'); import course_storyboard_corpus as c; import tempfile; d=tempfile.mkdtemp(); m,dirs=c.build_corrupted_course(d); print(len(dirs), sorted(m.unreadable)); m2,_=c.build_same_name_pair(d); print(len({r['name'] for r in m2.records.values()}), len(m2.records))"</automated>
Expected stdout: `2 ['crs-mirefield-02']` then `1 2`, exit 0. The degraded state
this task builds is the corrupted record itself: `FakeCourseModule.read_course`
raises `ValueError` for the named directory rather than returning a partial
record, which is what a real unparseable sidecar does.
  </verify>
  <acceptance_criteria>
- `fixtures/course_storyboard_corpus.py` exists and its module docstring states
  that all content is invented and that no `.md` file is written.
- `len(FICTIONAL_COURSES)` is `3`.
- `build_corrupted_course` returns a stand-in whose `unreadable` set is exactly
  `{"crs-mirefield-02"}` and creates exactly two directories.
- `build_same_name_pair` returns two records sharing one `name` value and
  carrying two different `course_id` values.
- `FakeCourseModule`'s docstring first line names it as a synthetic stand-in for
  `course.py`.
- No builder calls `random`, `time.time`, or `datetime.now`.
- `python itembank.py guard .` reports `0 offending files`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">A test fixture module. No published surface
  changes.</reversibility>
  <done>Two fictional courses exist, one of them cannot be read, and neither one
  is real.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: course_shelf_state, the attention vocabulary, and the total ordering</name>
  <files>surfaces/ia.py, tests/ia_route_roundtrip.py, .planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md</files>
  <behavior>
    - `course_shelf_state(root, course=None)` returns `available` False and an
      empty `cards` list, and raises nothing.
    - A stand-in with zero records returns `available` True, `cards` empty,
      `empty_heading` equal to `No courses yet`, and `empty_body` equal to
      `Start with the sample course, or bind a source to create your first course.`
    - A stand-in with the two healthy records returns two cards, the first
      carrying `cta_label` `Resume Kestrel County Field Basics` and the second
      `Start Mirefield Numeracy`.
    - The corrupted stand-in returns two cards, exactly one of which has
      `degraded` True, `chip` `Showing last valid overview`, and two actions
      labelled `Open last valid overview` and `View files`.
    - `build_same_name_pair` yields two cards with two different `course_id`
      values and one shared `name`, ordered `crs-twin-a` before `crs-twin-b`.
    - AMENDED 2026-08-27 by owner ruling. A percent character is permitted in
      `chip`, `resume_cue`, and `cta_label`. What is asserted instead: any
      percentage a card carries is accompanied by the numerator and denominator
      it was derived from, and a card whose record could not be read carries no
      percentage at all. Original assertion, superseded, preserved for trace:
      "No card's `chip`, `resume_cue`, or `cta_label` contains a percent
      character, for any fixture."
  </behavior>
  <read_first>
- `surfaces/ia.py` in full as it stands after plan 16B-03, in particular
  `ATTENTION_STATES` and the `_UNSET` sentinel and the `activity_view_state`
  docstring's explanation of the injectable-module pattern this function copies.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the Color
  section's "New semantic-token assignments" table rows 1 through 4 and the
  Copywriting Contract rows for the two CTAs, the empty state, and the
  corrupted course.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md`, `## D1`,
  `## D7`, and `## D9`.
- `fixtures/course_storyboard_corpus.py` as written by Task 1.
  </read_first>
  <action>
1. Add these constants to `surfaces/ia.py`:

   - `SHELF_EMPTY_HEADING = "No courses yet"`.
   - `SHELF_EMPTY_BODY = "Start with the sample course, or bind a source to create your first course."`
   - `ATTENTION_COPY`, a dict over `ATTENTION_STATES`:
     `"up_to_date"` maps to `"Up to date"`; `"due"` maps to `"{N} due"`;
     `"pending_review"` maps to `"{N} pending review"`; `"needs_input"` maps to
     `"Needs your input"`; `"needs_reconciliation"` maps to
     `"Needs reconciliation"`; `"last_valid_overview"` maps to
     `"Showing last valid overview"`.
   - `ATTENTION_TOKENS`, a dict over the same keys, mapping to the existing
     token names the UI-SPEC assigned: `up_to_date` to `ok`; `due`,
     `pending_review`, and `needs_input` to `warn`; `needs_reconciliation` and
     `last_valid_overview` to `unknown`. Bare names, no leading dashes, no color
     value.
   - `ATTENTION_ORDER = ("needs_input", "needs_reconciliation",
     "pending_review", "due", "last_valid_overview", "up_to_date")`, with a
     comment naming it as D-16B-10's first sort key.

2. Add `def course_shelf_state(root, course=_UNSET):` with a docstring stating:
   that it returns the shelf's whole state as a plain dict and performs no
   write; that passing `course=None` forces the module-absent branch, which is
   how a build without `course.py` behaves; that omitting the argument imports
   `course` and falls back to the same branch on `ImportError`; and that a
   record that fails to read yields a degraded card built from the directory
   basename only, never from a partially parsed record and never from a resolved
   absolute path, per D9.

   Behavior, exactly:

   - Resolve the module as `activity_view_state` does, with `ITEMBANK_IA_NO_COURSE=1`
     treated as equivalent to `course=None` when the argument is `_UNSET`.
   - When the module is `None`, return
     `{"available": False, "cards": [], "empty_heading": SHELF_EMPTY_HEADING,
       "empty_body": SHELF_EMPTY_BODY}`.
   - **Amendment 2026-08-27, FILE-04 accepted.** The set of courses is no
     longer this plan's to define. `REQUIREMENTS.md` FILE-04 names the workspace
     as the source of that set: an ordered list of approved roots plus one
     member entry per course pinned by `course_object_id`, with the walked index
     derived and disposable. When a workspace record exists, the shelf reads its
     members and must reconcile a moved or renamed course by pinned id, must
     render an unreachable root's courses from the last valid index marked
     unavailable rather than dropping them, and must surface a pinned id that
     disagrees with the sidecar at its path as a conflict without writing. The
     directory-scan behaviour described below is retained **only** as FILE-04's
     documented degraded mode, reached when no record exists or its root list is
     empty. The basename fallback for `course_id` in the next bullet is
     name-based identity, which FILE-03 forbids; under FILE-04 an unreadable or
     id-less sidecar is a degraded card, never a course keyed by its folder
     name. This amendment supersedes the previously unflagged assumption at
     these lines, recorded in IDEA-LEDGER IL-20260826-01.

   - Otherwise list `root`'s immediate subdirectories, sorted, and keep those
     containing a file named `course.COURSE_SIDECAR_FILENAME`. For each, call
     `course.read_course(<that directory>)` inside a `try`.
   - On success, build a card:
     `course_id` from the record's `course_id`, falling back to the directory
     basename when absent; `name` from the record's `name`, falling back to the
     directory basename; `attention` from the record's `attention` when it is a
     member of `ATTENTION_STATES`, else `"up_to_date"`; `chip` from
     `ATTENTION_COPY[attention]` with `{N}` substituted from the record's
     `due_count` or `pending_review_count` as the state requires; `token` from
     `ATTENTION_TOKENS[attention]`; `resume_cue` from the record's `resume_cue`
     when it is a non-empty string, else the literal `Not started`; `cta_label`
     equal to `"Resume " + name` when `resume_cue` is not `Not started` and
     `"Start " + name` otherwise; `cta_href` equal to `"/course/" + course_id`;
     `degraded` False; `help_code` None; `actions` an empty tuple;
     `last_activity` from the record.
   - On any exception from `read_course`, build a degraded card whose `name` is
     `os.path.basename(<that directory>)` and nothing else from the record;
     `course_id` the same basename; `attention` `"last_valid_overview"`; `chip`
     `ATTENTION_COPY["last_valid_overview"]`; `token` `unknown`; `resume_cue`
     the literal `Showing last valid overview`; `cta_label` the literal
     `Open last valid overview`; `cta_href` `"/course/" + course_id`;
     `degraded` True; `help_code` `"ia.course_corrupted"`; `actions` a tuple of
     exactly two dicts, `{"label": "Open last valid overview", "href": "/course/" + course_id}`
     and `{"label": "View files", "href": "/course/" + course_id + "/sources"}`;
     `last_activity` None. Never let the exception escape.
   - Sort `cards` by the three-key total order in D-16B-10: `ATTENTION_ORDER`
     index, then `last_activity` descending with `None` last, then `course_id`
     ascending.
   - Return `{"available": True, "cards": cards,
     "empty_heading": SHELF_EMPTY_HEADING, "empty_body": SHELF_EMPTY_BODY}`.

   AMENDED 2026-08-27 by owner ruling. A field this function produces MAY
   contain a percent character, and a card MAY carry a computed ratio. The rule
   that replaces it: a ratio is computed only where the record supplies both a
   numerator and a denominator, and where either is missing the field reports
   indeterminate rather than an invented percent. State that in the docstring,
   cite D7 as amended, and cite IL-20260827-01. Original rule, superseded,
   preserved for trace: "No field this function produces ever contains a percent
   character, and no card carries a computed ratio of any kind."

3. Append `## D-16B-10. Course-shelf ordering` to `16B-DECISIONS.md`, carrying
   the three-key rule and the one-line rationale from this plan's objective
   verbatim, under today's date.

4. Add `check_shelf_state_shape()`, `check_shelf_ordering_is_total()`, and
   `check_shelf_corrupted_course()` to `tests/ia_route_roundtrip.py`, asserting
   every behavior in this task's `<behavior>` block plus:

   - `check_shelf_ordering_is_total` builds the three `FICTIONAL_COURSES`
     records, shuffles the input order with `random.Random(20260815).shuffle`
     over a copy, rebuilds the state ten times, and asserts the resulting
     `course_id` sequence is identical every time.
   - It also asserts `build_same_name_pair` orders `crs-twin-a` before
     `crs-twin-b` even though both cards' attention and timestamp are equal,
     which is the course-ID tiebreak firing.
   - `check_shelf_corrupted_course` asserts the degraded card's `name` equals
     the literal `crs-mirefield-02` and contains no path separator, so no
     resolved absolute path reached it.
   - Every check asserts `"%"` appears in no `chip`, `resume_cue`, or
     `cta_label` of any card it produced.

5. Update `main()` to run thirteen checks and print
   `"IA ROUTES: 13 passed, 0 failed"`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_route_roundtrip.py</automated>
Expected: final line `IA ROUTES: 13 passed, 0 failed`, exit 0. The two degraded
states this task proves are the module-absent branch (`course=None` returns
`available` False and raises nothing) and the unreadable-record branch (a
raising `read_course` yields a degraded card rather than an exception).
  </verify>
  <acceptance_criteria>
- `python tests/ia_route_roundtrip.py` exits 0 with final line
  `IA ROUTES: 13 passed, 0 failed`.
- `python -c "import sys; sys.path.insert(0,'.'); from surfaces import ia; print(ia.SHELF_EMPTY_HEADING); print(ia.SHELF_EMPTY_BODY); print(ia.ATTENTION_ORDER[0], ia.ATTENTION_ORDER[-1])"`
  prints exactly `No courses yet`, then
  `Start with the sample course, or bind a source to create your first course.`,
  then `needs_input up_to_date`.
- `ia.course_shelf_state(".", course=None)["available"]` is `False` and the call
  raises nothing.
- The corrupted fixture yields exactly one degraded card whose `chip` equals
  `Showing last valid overview`, whose actions are exactly
  `Open last valid overview` and `View files`, and whose `name` contains no
  `os.sep`.
- Ten rebuilds over a shuffled input produce one identical `course_id` sequence.
- `build_same_name_pair` yields two cards, two `course_id` values, one `name`
  value, ordered `crs-twin-a` then `crs-twin-b`.
- No `chip`, `resume_cue`, or `cta_label` in any fixture contains `%`.
- `16B-DECISIONS.md` contains the literal heading
  `## D-16B-10. Course-shelf ordering`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="costly">The attention vocabulary and the ordering rule
  become the shape plans 16B-05 and 16B-09 and Phase 17A render against.
  Changing them later is a coordinated edit across those surfaces rather than a
  one-line change, which is why the ordering rule is written into
  `16B-DECISIONS.md` rather than left in code.</reversibility>
  <done>The shelf's whole state is computed server-side from durable records, is
  totally ordered, degrades on a bad record, and carries no invented
  number.</done>
</task>

<task type="auto">
  <name>Task 3: the handle_index course branch, end to end, with the shipped listing intact</name>
  <files>surfaces/daemon.py, tests/ia_route_roundtrip.py</files>
  <read_first>
- `surfaces/daemon.py` lines 939 to 990, `handle_index` in full, including its
  three-way populated, empty, and collisions branch and its `BANK_ROW` and
  `PLAN_ROW` template use. The new branch wraps this body rather than replacing
  it.
- `surfaces/presentation.py` lines 281 to 342, `surface_shell` and
  `state_panel`.
- `surfaces/ia.py`, `course_shelf_state` as written by Task 2.
- `tests/daemon_roundtrip.py`, the existing checks that assert `GET /` renders
  the bank and plan index, so this task knows exactly which shipped assertions
  must keep passing.
  </read_first>
  <action>
1. Modify `handle_index` in `surfaces/daemon.py` by adding a branch at the top
   of the function body and changing nothing below it:

   - `shelf = ia.course_shelf_state(handler.root)`.
   - When `shelf["available"]` is False, or when `shelf["available"]` is True
     and `shelf["cards"]` is empty **and** the existing `stems` list is
     non-empty, fall through to the entire existing body unchanged. This is D1's
     "renders today's shipped bank/plan listing unchanged" case.
   - When `shelf["available"]` is True and `shelf["cards"]` is non-empty, render
     the shelf and return.
   - When `shelf["available"]` is True, `shelf["cards"]` is empty, and the
     existing `stems` list is also empty, render the empty state: a heading
     carrying `shelf["empty_heading"]` and a paragraph carrying
     `shelf["empty_body"]`, then return.

   Update `handle_index`'s docstring to describe the new three-way gate and to
   cite D1 by name.

2. Render each card as one `<article class="course-card"
   data-course-id="{course_id}" data-attention="{attention}"
   data-ia-token="{token}">` containing, in this order: an `<h2>` with the
   escaped `name`; a `<span class="chip">` with the escaped `chip`; a
   `<p class="resume-cue">` with the escaped `resume_cue`; and an actions
   region holding one primary anchor whose text is the escaped `cta_label` and
   whose href is `cta_href`, followed by one anchor per entry in `actions`.
   Add no CSS rule and no inline style; the two `data-*` attributes and the two
   class names are stable hooks for tests and for Phase 17A, not styling.

   Wrap the whole card list in a single container element and add no
   pagination control, no page-number links, and no item cap, so a many-course
   shelf scrolls.

3. Render with `presentation.surface_shell("Courses", body, theme_css=...)` and
   send with `handler.send_html`.

4. Add `check_shelf_end_to_end()` to `tests/ia_route_roundtrip.py`. It prepares
   a temp dir with `build_corrupted_course`, starts a real daemon there, and
   asserts against the served `GET /` body:
   - Status 200.
   - Exactly two occurrences of `class="course-card"`.
   - The healthy course's exact `cta_label` string is present.
   - The degraded course's exact chip `Showing last valid overview` is present,
     along with both `Open last valid overview` and `View files`.
   - `data-course-id="crs-kestrel-01"` and `data-course-id="crs-mirefield-02"`
     are both present, so identity is by course ID.
   - No `%` character appears inside any `<span class="chip">` or
     `<p class="resume-cue">` in the body.
   - No pagination affordance: the strings `Next page`, `Previous page`, and
     `page=` are all absent.

   Because the daemon runs in a separate process and cannot receive the
   `FakeCourseModule` object, this check exercises the **real** `course.py`
   against the directories the fixture created. If the real `read_course`
   accepts those directories, assert as written. If it rejects both, then both
   cards render degraded: assert two degraded cards instead, and record in the
   summary that the end-to-end check proved the degraded path twice rather than
   one of each, with the in-process `check_shelf_corrupted_course` remaining the
   proof of the mixed case. Do not fabricate a passing assertion either way.

5. Add `check_shelf_falls_back_to_bank_index()`. It starts a daemon in a temp
   dir holding `fixtures/sample_bank.md` and no course directory at all, with
   `ITEMBANK_IA_NO_COURSE=1` set, and asserts the served `GET /` body contains
   the shipped bank listing markers and contains no `class="course-card"`. Then
   it starts a daemon in an empty temp dir with the same variable unset and no
   course directories and no banks, and asserts the body contains both
   `No courses yet` and
   `Start with the sample course, or bind a source to create your first course.`

6. Update `main()` to run fifteen checks and print
   `"IA ROUTES: 15 passed, 0 failed"`. Then run:

```
python tests/ia_route_roundtrip.py
python tests/daemon_roundtrip.py
for t in tests/*.py; do python "$t" || exit 1; done
python itembank.py guard .
```

   Expected: `IA ROUTES: 15 passed, 0 failed` and exit 0; exit 0; exit 0;
   `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_route_roundtrip.py && python tests/daemon_roundtrip.py</automated>
Expected: `IA ROUTES: 15 passed, 0 failed` and exit 0, then exit 0. The degraded
states this task proves are the corrupted-course card served over HTTP and the
fallback to the shipped bank and plan listing when no course exists, the second
of which is also what keeps `tests/daemon_roundtrip.py` green.
  </verify>
  <acceptance_criteria>
- `python tests/ia_route_roundtrip.py` exits 0 with final line
  `IA ROUTES: 15 passed, 0 failed`.
- `python tests/daemon_roundtrip.py` exits 0, proving the shipped `GET /`
  assertions still pass in the no-course case.
- The served shelf for the corrupted fixture contains exactly two
  `class="course-card"` occurrences and both `data-course-id` values.
- The served shelf contains `Open last valid overview` and `View files`.
- The served shelf contains no `%` inside any chip or resume-cue element and
  none of `Next page`, `Previous page`, `page=`.
- A daemon over a bank-only directory with `ITEMBANK_IA_NO_COURSE=1` serves the
  shipped bank listing and no `class="course-card"`.
- A daemon over an empty directory serves both `No courses yet` and
  `Start with the sample course, or bind a source to create your first course.`
- `daemon.ROUTE_CLI[("GET", "/")]` is still the literal `"daemon"`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0 and
  `python itembank.py guard .` reports `0 offending files`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="costly">`GET /`'s rendered meaning changes for any
  install that has a course. The route literal, its CLI twin, and the old
  listing are all unchanged, and D1 settled the gating, so the change is a
  branch rather than a replacement and is undone by deleting the
  branch.</reversibility>
  <done>The app's first screen is a course shelf when a course exists, is the
  shipped listing when none does, and shows a broken course rather than hiding
  it.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| course record on disk to rendered card | A record is parsed content from outside this phase's control and may be malformed, truncated, or hostile. |
| directory name to page content | A course directory name reaches the page in the degraded path. |
| filesystem layout to disclosure | The shelf enumerates directories under the daemon root. |
| evidence and journal records to a displayed figure | A cue that summarizes progress can misstate what is known. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16B-04-01 | Denial of Service | one unreadable course record breaking the whole shelf | high | mitigate | `read_course` is called inside a `try` per course; any exception yields one degraded card and never escapes, asserted by the corrupted fixture rendering one healthy card beside one degraded one. |
| T-16B-04-02 | Information Disclosure | a resolved absolute path in a degraded card | high | mitigate | The degraded card takes `os.path.basename` of the directory and nothing else from the failed record, per D9; the acceptance criteria assert the rendered name contains no `os.sep`. |
| T-16B-04-03 | Information Disclosure | a malformed record's raw contents rendered into the page | high | mitigate | The degraded path copies **no** field from the failed record; every field of a degraded card is either the basename or a fixed literal string. |
| T-16B-04-04 | Tampering | a hostile record injecting markup into the shelf | high | mitigate | Every record-derived value is emitted through `presentation.esc`; the card template interpolates no unescaped record field, and the two `data-*` values are drawn from closed tuples (`ATTENTION_STATES`, the token names) rather than from the record. |
| T-16B-04-05 | Repudiation | an invented progress figure presented as a measurement | high | mitigate | **Mitigation amended 2026-08-27 by owner ruling (IL-20260827-01).** A card may carry a ratio and a percent. The threat is unchanged and is now mitigated by honesty of derivation rather than by absence: every displayed percentage is accompanied by the numerator and denominator it came from, a record that supplies neither reports indeterminate rather than a number, and checks assert that no percentage appears without its denominator. Original mitigation, superseded, preserved for trace: "No card carries a ratio; `ATTENTION_COPY` has no percent form; three checks assert `\"%\"` appears in no chip, cue, or CTA across every fixture." |
| T-16B-04-06 | Repudiation | a stale resume cue presented as current | medium | mitigate | The cue is recomputed by the route handler on every request from the record, never cached and never carried over; an absent record yields the literal `Not started` and an unreadable one yields `Showing last valid overview`. |
| T-16B-04-07 | Spoofing | two distinct courses collapsed into one card because their names match | medium | mitigate | Cards are keyed by `course_id` throughout, and `build_same_name_pair` asserts two cards with one shared name and two ids render separately in a locked order. |
| T-16B-04-08 | Information Disclosure | real course or learner material entering the repository through the fixture | high | mitigate | Every course, name, and cue in `FICTIONAL_COURSES` is invented, no builder writes a `.md` file, and `python itembank.py guard .` reporting `0 offending files` is an acceptance criterion on every task here. |
| T-16B-04-09 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; every new file is standard library only. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No course-level route. `/course/<course_id>` is linked from every card but is
  registered and handled by plan 16B-05; until that plan lands the link resolves
  to the daemon's existing 404, which is stated and is not a defect this plan
  fixes.
- No sample course and no walkthrough. The empty-state body invites both, and
  plan 16B-09 builds them.
- No writing of any course record. This plan reads records and never creates,
  edits, or repairs one; repairing a corrupted course is not a 16B capability.
- No Notes destination and no Search. D4 and D5 settled both.
- No progress tuple rendering beyond the attention chip. Composing the full
  `GRAPH-03` honest-progress tuple belongs to the Evidence area, which plan
  16B-05 registers as a route and does not fill.
- No new visual constant. The two class names and two `data-*` attributes are
  hooks, and no CSS rule is added.
- No change to `ROUTE_CLI[("GET", "/")]`, which stays `"daemon"` per D1.
</out_of_scope>

<flagged_assumptions>
- **`course.COURSE_SIDECAR_FILENAME` and `course.read_course`'s signature are
  read from `14B-01-PLAN.md` plan text.** Task 1 step 1 re-verifies both live
  and requires the real signature to be recorded in the summary. If the landed
  signature differs, `FakeCourseModule` is adapted to match it and
  `course_shelf_state` still calls exactly one shape.

- **Whether the real `course.py` can read the fixture's directories is unknown
  at plan time.** Task 3 step 4 states both outcomes and what to assert in each,
  and forbids fabricating a passing assertion. The in-process
  `check_shelf_corrupted_course` remains the proof of the mixed healthy and
  degraded case regardless of which outcome the end-to-end check sees.

- **`ITEMBANK_IA_NO_COURSE=1` is a test-only degradation switch**, introduced
  for the same reason `ITEMBANK_IA_NO_JOURNAL=1` was in plan 16B-02: the phase's
  own precondition guarantees `course.py` is present, so the module-absent
  branch would otherwise be unreachable in a real tree and the phase would ship
  a state it never executed.

- **The CourseShelf loading and overflow rows and the APP-01 concurrency row are
  carried as backstop markers**, not as asserted truths. Loading and overflow
  are 17A rendering decisions; concurrency is confirmed by plan 16B-09's
  interruption fixture. At verification time, no explicit evidence for a
  backstop row is `insufficient_spec` and needs a human, never a silent pass.

- **Resolved 2026-08-27, previously unflagged.** This plan assumed the daemon
  root's immediate subdirectories *are* the workspace, and fell back to the
  directory basename for course identity. That assumption was never listed here.
  It is now answered by `REQUIREMENTS.md` FILE-04 rather than by this plan; see
  the amendment in Task 2. FILE-04 is accepted but unscheduled, so if it has not
  shipped when this plan executes, the scan path runs as FILE-04's degraded mode
  and the summary must say so explicitly rather than presenting it as the
  contract.
</flagged_assumptions>

<summary_obligations>
`16B-04-SUMMARY.md` records: the verbatim output of Task 1 step 1's two
signature commands and any deviation from the plan-text signature; which outcome
Task 3 step 4's end-to-end check saw against the real `course.py` and what was
asserted as a result; the final line of every verify command; the exact rendered
chip and CTA strings observed for both fixture courses; whether any `%` was
found anywhere on the shelf; the recorded `## D-16B-10` text; which truth was
verified by which command with its actual stdout; and any deviation from this
plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16B-ia-modes-recovery-contract/16B-04-SUMMARY.md`
when done.
</output>
