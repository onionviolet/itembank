---
phase: 14B-graph-course-package-prototype
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - graph.py
  - course.py
  - course_package.py
  - fixtures/corpus_14b.py
  - tests/graph_roundtrip.py
  - .planning/phases/14B-graph-course-package-prototype/14B-PRECONDITION.md
  - .planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md
autonomous: false
requirements: [GRAPH-01, PORT-03]
must_haves:
  truths:
    - "Phase 14B writes no code that imports identity or journal until a recorded precondition check has confirmed that identity.py, journal.py, and discovery.py exist and that their frozen constants match what 14B was planned against; a divergence halts the wave by name instead of surfacing as an ImportError mid-task."
    - "One synthetic objective travels the whole phase path end to end in one commit: an objective is minted into a course sidecar, an edge relates it to a second objective, the sidecar is written through journal.commit_operation as one kind=course object, the outline projection renders it as plain Markdown, the course is exported as a package, and the package is restored into a directory that never saw the original."
    - "The course sidecar is exactly one kind=course object with one compare-and-swap lineage (D-14A-1 hybrid rule); objectives and edges are addressable records inside that one file, never independently compare-and-swap-tracked files, and 14B mints no new member of identity.OBJECT_KINDS."
    - "Phase 14B never writes to <course-root>/course.md. The Phase 13.9 walking-skeleton stub is superseded by a separate readable file and is left byte-identical, proven by a before-and-after byte comparison in the migration test."
    - "An empty course sidecar, one carrying only its header table and zero objectives, parses without raising and projects to an outline whose body is the single line: No objectives are recorded yet. A single-objective graph projects that one objective (GRAPH-01 empty edge)."
    - "graph.serialize_course(graph.parse_course(text)) returns text unchanged for a sidecar containing an unrecognized section heading and an unrecognized table column, so the format is additive by construction and a later build's fields survive an older build's rewrite."
    - "A restored package on a destination with no shared journal, no shared registry, and no shared evidence store reproduces the course sidecar with a fingerprint equal to the manifest's recorded value, and reports its verification result rather than trusting the manifest (PORT-03)."
  prohibitions: []
  artifacts:
    - "graph.py at the repository root, a model-tier peer of model.py and identity.py, with no file input or output"
    - "course.py at the repository root, a runtime-tier peer of journal.py, owning the course sidecar lifecycle"
    - "course_package.py at the repository root, a runtime-tier peer of audit_writer.py"
    - "fixtures/corpus_14b.py, the synthetic three-domain course corpus generator"
    - "tests/graph_roundtrip.py with check_thin_slice() as its first function"
    - ".planning/phases/14B-graph-course-package-prototype/14B-PRECONDITION.md"
    - ".planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md"
  key_links:
    - "The sidecar is one kind=course object because journal.commit_operation ties exactly one object_id to exactly one path per call. If a later plan gives an objective its own compare-and-swap file, two object kinds start competing for the same physical bytes and the whole 14A write path breaks."
    - "graph.py must never import model. model.py stays the one parser of bank and lesson content; graph.py reads only its own sidecar tables, exactly as surfaces/day.py:129 parse_lanes reads lanes.md. If graph.py ever parses bank bytes, non-negotiable 2 in PLANNING-DIRECTIVES section 4 is broken."
    - "course.py must never import evidence. The migration work in plan 14B-04 depends on that being structurally true, not merely observed."
---

<objective>
Land the thinnest real path through this whole phase, end to end, before any
layer is widened: one synthetic objective, minted into a course sidecar, related
by one edge, written through the frozen 14A compare-and-swap path, projected to
a plain-Markdown outline, exported as a package, and restored on a destination
that never saw the original. The three new modules are created here in their
thinnest production-quality form, not as prototypes: the code written in this
plan stays and is expanded by plans 02 through 05.

This plan also does the two things that must happen before any 14B code exists.
First, it verifies that Phase 14A actually landed on disk with the surface 14B
was planned against, and halts by name if it did not (`14B-RESEARCH.md` Critical
Caveat and Assumption A6: `identity.py`, `journal.py`, and `discovery.py` did
not exist when 14B was researched or planned). Second, it settles the Phase 13.9
collision with a named, non-destructive supersession path rather than leaving it
implicit.

Decisions already made, cited, and never re-derived here:

- **D-14A-1** (`DECISIONS-PRE-14A-2026-08-14.md` lines 55 to 59): hybrid graph
  storage. An edge lives inline when it is wholly owned by one file's content
  and in the readable course sidecar when it relates two independently
  identified objects. The sidecar stays diffable and never becomes the only
  readable copy. The minimal edge vocabulary is exactly the four names
  `prerequisite-of`, `covers-objective`, `source-supports`, `treatment-of`.
- **D-14A-2**: object-level opaque ids. 14B mints objective, container, and
  binding record ids with `identity.new_object_id()` and mints no new object
  kind. The `[CID:...]` component-marker family is reserved for lesson blocks
  and is not reused for graph records (`14B-RESEARCH.md` Pitfall 9).
- **D-14A-3**: routed to 16B. This plan touches nothing under `retention.py`,
  `selection.py`, `surfaces/`, or `schemas/report.schema.json`.
- **PLANNING-DIRECTIVES section 4**, all five non-negotiables, in particular
  number 2 (the typed graph kernel is additive machinery and never a second
  document model or a second parser) and number 4 (format changes are additive,
  proven by a byte-identical fixture and not by promise).

Decisions this plan makes and locks, so the executor never guesses (the
`PLANNING-DIRECTIVES.md` section 5 bar):

| Open question | Locked answer | One-line rationale |
|---|---|---|
| Module split | Three new root-level modules: `graph.py` (model tier, pure, no file input or output), `course.py` (runtime tier, sidecar lifecycle and bindings), `course_package.py` (runtime tier, package and restore) | `14B-RESEARCH.md` "Architectural Responsibility Map" splits pure transform from compare-and-swap write from export; three thin peers keep the `journal.py` diff at one line, which the research names as the drift signal to watch. |
| Where the sidecar's records live | Records are rows in tables inside one file; the file is one `kind="course"` object with one compare-and-swap lineage | `journal.commit_operation` binds one `object_id` to one path per call, so two object kinds cannot independently guard the same bytes (`14B-RESEARCH.md` Pattern 1, Assumption A1). |
| Sidecar serialization | Plain Markdown: `##` section headings plus pipe tables, following `fixtures/sample_lanes.md` verbatim in shape | The freeze gate is an authorability review; `14B-RESEARCH.md` Pitfall 8 names minified or nested serialization as an outright failure of that gate, and the project already ships a pipe-table record format read by `surfaces/day.py:129`. |
| Edge identity | The tuple `(source, edge_type, target)`. An edge is never given a minted id and never identified by a hash of its own record | `14B-RESEARCH.md` Anti-Patterns: hashing the record makes editing an edge's rationale look like a different edge, the same class of error D-14A-2 rejects for objects. |
| Unknown sections and columns | Preserved verbatim on rewrite, never dropped | This is what makes the format additive by construction rather than by promise, and it is the property asserted as this phase's byte-identical fixture (non-negotiable 4). |

Purpose: prove the architecture end to end on one path before ten layers are
built on it.
Output: `graph.py`, `course.py`, `course_package.py`, the corpus generator, the
first roundtrip test, and the two recorded decision artifacts.
</objective>

<context>
@.planning/phases/14B-graph-course-package-prototype/14B-RESEARCH.md
@.planning/phases/14B-graph-course-package-prototype/14B-PATTERNS.md
@.planning/DECISIONS-PRE-14A-2026-08-14.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
@.planning/phases/14A-identity-lifecycle-operation/14A-01-PLAN.md
@.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md
@.planning/phases/13.9-walking-skeleton/13.9-01-PLAN.md
@.agents/skills/OPERATION-CONTRACT.md
@fixtures/sample_lanes.md
</context>

## Artifacts this phase produces (plan 14B-01 share)

New modules and the public symbols this plan creates. Every symbol below is new
in this phase and exists in no shipped file.

- `graph.py`
  - Constants: `COURSE_GRAPH_VERSION = 1`, `EDGE_TYPES`, `DEGRADED_EDGE_TYPE`,
    `SECTION_ORDER`, `HEADER_FIELDS`.
  - Exception: `GraphError(Exception)` with `.code` and `.message`.
  - Functions created here: `new_course(title, course_object_id)`,
    `parse_course(text)`, `serialize_course(doc)`, `add_container(...)`,
    `add_objective(...)`, `add_edge(...)`, `outline_projection(doc)`.
- `course.py`
  - Constants: `COURSE_SIDECAR_FILENAME = "course-graph.md"`,
    `STUB_FILENAME = "course.md"`, `COURSE_KIND = "course"`.
  - Exception: `CourseError(Exception)` with `.code` and `.message`.
  - Functions created here: `sidecar_path(course_root)`,
    `create_course(course_root, title, actor_kind, actor_name)`,
    `read_course(course_root)`,
    `write_course(course_root, doc, expected_fingerprint, actor_kind, actor_name, operation="edit_in_place")`,
    `migrate_stub(course_root, actor_kind, actor_name)`.
- `course_package.py`
  - Constants: `PACKAGE_SCHEMA_VERSION = 1`, `MANIFEST_FILENAME`,
    `PAYLOAD_DIRNAME`, `PACKAGE_STATES`, `MANIFEST_ENTRY_KEYS`.
  - Exception: `PackageError(Exception)` with `.code` and `.message`.
  - Functions created here: `safe_target(dest, relpath)`,
    `export_package(base, course_root, dest)`,
    `restore_package(package_root, dest, actor_kind, actor_name)`.
- `fixtures/corpus_14b.py`
  - `build_three_domains(dest)` returning a dict describing what was built,
    `build_stub_course(dest)` writing a Phase 13.9 shaped `course.md`, and
    `teardown(dest)`.
- `tests/graph_roundtrip.py`, a direct-execution script, exit 0 on pass, whose
  first function is `check_thin_slice()`.
- `.planning/phases/14B-graph-course-package-prototype/14B-PRECONDITION.md` and
  `14B-DECISIONS.md`.

New refusal codes introduced by this plan: `graph.future_schema_version`,
`graph.malformed_section`, `course.no_sidecar`, `course.sidecar_exists`,
`course.stub_absent`, `package.path_escape`, `package.not_applied`.

New journal record types introduced by this plan: none. `journal.py` is not
modified by this plan.

No CLI command, no daemon route, and no schema file is produced by this plan.

<tasks>

<task type="auto">
  <name>Task 1: verify Phase 14A landed, or halt by name</name>
  <files>.planning/phases/14B-graph-course-package-prototype/14B-PRECONDITION.md</files>
  <read_first>
- `.planning/phases/14B-graph-course-package-prototype/14B-RESEARCH.md`, the
  "Critical caveat: 14A has not executed yet" section and Assumption A6, in
  full. This task exists because of it.
- `.planning/phases/14A-identity-lifecycle-operation/14A-01-PLAN.md`, the
  "Artifacts this phase produces" section, for the exact `identity.py` constant
  list this task checks.
- `.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md`, the
  "Artifacts this phase produces" section, for `journal.ENTRY_KEYS` and
  `journal.RECORD_TYPES`.
- `.planning/phases/14A-identity-lifecycle-operation/14A-03-PLAN.md`, the
  "Artifacts this phase produces" section, for `identity.RIGHTS_STATES`,
  `identity.rights_state`, `identity.rights_granted`, and
  `journal.read_registry`.
- `.planning/phases/14A-identity-lifecycle-operation/14A-04-PLAN.md` Task 4, for
  the `## Frozen at 14A` section this task requires to exist.
  </read_first>
  <action>
1. Check that the three 14A modules import. Run
   `python -c "import identity, journal, discovery; print('modules present')"`.
   Expected stdout: `modules present`, exit code 0.

2. Check that the frozen constants match what Phase 14B was planned against.
   Run a single `python -c` that asserts, in this order, every one of the
   following, printing `14A surface matches` on success:
   - `identity.OBJECT_KINDS` equals `("course", "objective", "source",
     "lesson", "bank", "component")`.
   - `len(identity.REVISION_KEYS)` equals `11`.
   - `identity.RIGHTS_OPERATIONS` equals `("read", "quote", "transform",
     "remote_process", "package", "export", "share")`.
   - `identity.RIGHTS_STATES` equals `("granted", "denied", "unknown")`.
   - `identity.IDENTITY_SCHEMA_VERSION` equals `1`.
   - `journal.OPERATION_TYPES` equals `("link", "import", "copy", "move",
     "edit_in_place", "supersede")` and has exactly six members.
   - `"reconcile"` is in `journal.RECORD_TYPES` and `"migrate"` is not yet.
   - `len(journal.ENTRY_KEYS)` equals `22`.
   - `journal.JOURNAL_SCHEMA_VERSION` equals `1`.
   - Every one of these names is callable on its module:
     `identity.new_object_id`, `identity.object_fingerprint`,
     `identity.mint_object`, `identity.next_revision`,
     `identity.rights_default`, `identity.rights_state`,
     `identity.rights_granted`, `identity.registry_rows`,
     `journal.commit_operation`, `journal.append_entry`, `journal.entries`,
     `journal.read_registry`, `journal.read_object`, `journal.replay`,
     `journal.object_state`, `discovery.inventory`, `discovery.run_report`,
     `discovery.inside_any_root`.

3. Check that
   `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` exists and
   contains the literal heading `## Frozen at 14A`.

4. If any check in steps 1 through 3 fails, STOP. Write nothing else, create no
   module, and print exactly this line with the failing item substituted for
   `<item>`, then exit non-zero:

   `HALT 14B-01 precondition: Phase 14A has not landed or its frozen surface differs from what Phase 14B was planned against. Re-verify every 14B plan against .planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md before writing any code. Divergent or missing: <item>`

   Do not work around a failure by stubbing the missing module, by adding a
   try or except around the import, or by continuing with a reduced check set.
   A halt here is the correct outcome; it is what this task is for.

5. On success, create
   `.planning/phases/14B-graph-course-package-prototype/14B-PRECONDITION.md`
   with exactly these four sections and nothing more:
   - **Why this check exists.** One paragraph citing `14B-RESEARCH.md`
     Assumption A6: every 14A signature in the 14B research and pattern map was
     read from plan text, not from source, because the modules did not exist
     when 14B was planned.
   - **What was checked.** The full list from steps 1 through 3, one line each,
     each marked `ok` or `divergent`.
   - **Deviations found.** Every place the landed 14A surface differs from the
     14A plan text, with the plan-text value and the landed value side by side.
     Write `none` when there are none. A deviation here is not a failure of
     this task; it is the signal that plans 02 through 06 must be re-read
     against `14A-FREEZE.md` before execution, and this section is where a
     later plan looks for it.
   - **Dated result line.** The date, the command output of step 2 verbatim, and
     one sentence stating whether 14B may proceed.

   No em dash characters anywhere in the file.
  </action>
  <verify>
  <automated>python -c "import identity, journal, discovery; assert len(identity.REVISION_KEYS)==11 and len(journal.OPERATION_TYPES)==6 and len(journal.ENTRY_KEYS)==22; print('14A surface matches')"</automated>
Expected: prints `14A surface matches` and exits 0. The degraded state this
task must prove rather than paper over is the halt itself: if any assertion
fails, the run exits non-zero with the named HALT line and no module file is
created. Confirm this by checking that `graph.py` does not exist on disk at the
end of a failed run.
  </verify>
  <acceptance_criteria>
- `python -c "import identity, journal, discovery; print('modules present')"`
  prints `modules present` and exits 0.
- The step 2 command prints `14A surface matches` and exits 0.
- `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` exists and
  contains the string `## Frozen at 14A`.
- `.planning/phases/14B-graph-course-package-prototype/14B-PRECONDITION.md`
  exists with all four named sections.
- `14B-PRECONDITION.md` contains no em dash character.
  </acceptance_criteria>
  <precondition>Phase 14A has executed and `identity.py`, `journal.py`, and `discovery.py` exist at the repository root with the surface frozen in `14A-FREEZE.md`.</precondition>
  <done>Either 14B is cleared to proceed with the evidence recorded, or the
  wave is halted with the divergence named.</done>
</task>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 2: the sidecar's on-disk name and the Phase 13.9 supersession path</name>
  <files>.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md</files>
  <read_first>
- `.planning/phases/13.9-walking-skeleton/13.9-01-PLAN.md` in full, especially
  its Task 2 step 1 header text and its `key_links` line stating that
  `course.md` is a draft stub Phase 14B owns the real schema for and may
  supersede.
- `.planning/phases/13.9-walking-skeleton/13.9-01-SUMMARY.md` if it exists. It
  tells you whether a real course has already been drafted into `course.md`,
  which is the fact that makes option-b consequential.
- `14B-RESEARCH.md` "Interaction with Phase 13.9" in full, and Assumption A7.
- `.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md` if it
  already exists, so the new section is appended rather than overwriting one.
  </read_first>
  <decision>
Where does the Phase 14B course graph live on disk inside a course root, and
what happens to the `course.md` stub that Phase 13.9 writes there?
  </decision>
  <context>
`13.9-01-PLAN.md` creates `<course-root>/course.md` as a human-authored draft
manifest with Sources, Objectives, and Log sections, headed by text that says
"Phase 14B owns the durable course schema and supersedes this format". That
file may already contain Weibao's real, hand-approved objective map for a live
fall course by the time this plan runs. It lives outside this repository and is
not covered by any test fixture.

This is rated one-way. Whatever path 14B writes becomes the path plans 02
through 06, the package manifest, and every later subphase build against, and
undoing it means migrating any sidecar already written. It also decides whether
a file Weibao authored by hand gets rewritten by a tool.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: separate file, non-destructive migration</name>
      <pros>14B writes `&lt;course-root&gt;/course-graph.md` and never opens
      `course.md` for writing. `course.migrate_stub()` reads a 13.9 shaped
      `course.md`, emits the new sidecar, journals the operation, and leaves
      `course.md` byte-identical, which the test asserts. A hand-authored file
      is never rewritten by a tool. Both files stay readable. The supersession
      is explicit and recorded rather than performed silently.</pros>
      <cons>Two course-shaped files exist in the course root until a later
      phase retires the stub. Each file needs a header line pointing at the
      other.</cons>
    </option>
    <option id="option-b">
      <name>Same path, in-place format upgrade</name>
      <pros>One course file, which is what 13.9's own header text anticipates.
      No cross-reference needed.</pros>
      <cons>A tool rewrites a file a human authored and approved, in a
      directory with no test fixture and no repository backup. If the format
      upgrade is wrong, the recorded objective map is the thing that is
      damaged.</cons>
    </option>
    <option id="option-c">
      <name>Refuse: 14B reads no 13.9 stub at all</name>
      <pros>Smallest surface. No migration code.</pros>
      <cons>The walking skeleton's recorded objective map cannot reach the
      graph without being retyped, which is exactly the manual re-entry the
      whole phase exists to remove.</cons>
    </option>
  </options>
  <action>
Ask Weibao the question above, present all three options with the recommended
default named, and record the answer verbatim in
`.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md` under a
dated heading `## D-14B-1. Sidecar path and the Phase 13.9 supersession`.

What the executor does with each answer:

- **option-a**: proceed as every task in plans 01 through 06 is already
  written. No plan edit is needed.
- **option-b**: before Task 3, edit `course.py`'s
  `COURSE_SIDECAR_FILENAME` to `"course.md"`, delete `STUB_FILENAME`, and
  change `migrate_stub` to an in-place upgrade that takes an
  `expected_fingerprint` and journals `operation="edit_in_place"`. Then record
  in `14B-DECISIONS.md` that the byte-identical stub assertion in Task 3 is
  replaced by a before-image assertion: the pre-upgrade bytes must be
  recoverable from `_journal/before/`.
- **option-c**: before Task 3, delete `migrate_stub` from `course.py`'s symbol
  list and from Task 3's assertions, and record in `14B-DECISIONS.md` that the
  13.9 objective map is re-entered by hand and by whom.

Do not proceed with a silent default. An unanswered checkpoint stops the wave.
  </action>
  <verify>
`14B-DECISIONS.md` exists and carries a dated `## D-14B-1` heading with the
chosen option id and Weibao's answer recorded verbatim.
  </verify>
  <acceptance_criteria>
- `.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md`
  contains the literal heading `## D-14B-1. Sidecar path and the Phase 13.9 supersession`.
- The recorded answer names exactly one of `option-a`, `option-b`, `option-c`.
- The file contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">The sidecar path is consumed by plans 02
  through 06, by the package manifest, and by every later subphase. Undoing it
  after a package has been built means migrating recorded manifests. Under
  option-b it also rewrites a file a human authored outside this
  repository.</reversibility>
  <resume-signal>Reply with `option-a`, `option-b`, or `option-c`.</resume-signal>
</task>

<task type="tracer" tdd="true">
  <name>Task 3: one objective from mint to restore, end to end, one path only</name>
  <files>graph.py, course.py, course_package.py, fixtures/corpus_14b.py, tests/graph_roundtrip.py</files>
  <read_first>
- `identity.py` in full, as landed: `new_object_id`, `object_fingerprint`,
  `mint_object`, `next_revision`, `rights_default`, `REVISION_KEYS`,
  `OBJECT_KINDS`, and the module docstring's peer-module contract.
- `journal.py` in full, as landed: `commit_operation`'s fourteen steps,
  `ENTRY_KEYS`, `RECORD_TYPES`, `read_registry`, `read_object`, and
  `JournalError`.
- `evidence.py` lines 1 to 19, the peer-module docstring contract this project
  restates in every new root module.
- `surfaces/day.py` lines 129 to 197 (`parse_lanes`), the shipped precedent for
  reading pipe-table records outside `model.py`. This is the shape `graph.py`
  follows and the reason a sidecar reader is not a second document model.
- `fixtures/sample_lanes.md` in full, 19 lines, the project's own readable and
  diffable pipe-table record format.
- `audit_writer.py` lines 246 to 265 and 346 to 402, the
  manifest-written-before-mutation, atomic replace, after-fingerprint-guard
  shape `course_package.export_package` follows.
- Any existing `tests/*_roundtrip.py` file, for the local `fail(msg)` helper
  convention. Each test file defines its own; there is no shared test module.
  </read_first>
  <behavior>
Assertions `check_thin_slice()` in `tests/graph_roundtrip.py` must make,
written before any module exists. Run the test first and confirm it fails.

Sidecar shape and round trip:

- `graph.new_course("Meridian Field Response", cid)` returns a document dict
  with the keys `header`, `structure`, `objectives`, `sources`, `edges`,
  `bindings`, `migrations`, `log`, and `unknown_sections`.
- `graph.serialize_course(doc)` output begins with the exact line
  `# Course graph` and contains a header table row whose first two cells are
  `graph_schema_version` and `1`.
- `graph.parse_course(graph.serialize_course(doc))` equals `doc`.
- For a fixture sidecar text containing a section heading `## Cohorts` that
  `graph.SECTION_ORDER` does not name, and an extra column `owner` in the
  `## Objectives` table, `graph.serialize_course(graph.parse_course(text))`
  equals `text` exactly, byte for byte. Unknown sections and unknown columns
  are preserved, never dropped.
- A sidecar text whose header table declares `graph_schema_version` `2` raises
  `GraphError` with code `graph.future_schema_version`, and the raised message
  contains both the numbers 2 and 1.
- `graph.parse_course` of a sidecar whose `## Edges` section is prose rather
  than a table raises `GraphError` with code `graph.malformed_section`, and the
  original text is unchanged on disk because `graph.py` performs no file input
  or output at all.

Empty and single-element cases (GRAPH-01 empty edge):

- `graph.outline_projection(graph.new_course("Empty Course", cid))` equals
  exactly `# Empty Course` then a blank line then the single line
  `No objectives are recorded yet.` and a trailing newline.
- A course with one container and one objective projects to `# <title>`, a
  blank line, `## <container title> (module)`, a blank line, and
  `- <statement> [<objective id>]`.
- `graph.add_container` and `graph.add_objective` add zero edges: after
  building a three-container, three-objective structure,
  `len(doc["edges"])` is `0`. Structural order mints no prerequisite edge
  (GRAPH-01).

Compare-and-swap lifecycle through the frozen 14A path:

- `course.create_course(root, "Meridian Field Response", "human", "weibao")`
  returns a revision record whose keys equal `identity.REVISION_KEYS`, whose
  `kind` is `"course"`, whose `revision` is `1`, and whose `parent_revision` is
  `None`.
- `journal.read_registry(root)` contains exactly one entry after
  `create_course`, and its `kind` is `"course"`.
- Calling `course.create_course` a second time on the same root raises
  `CourseError` with code `course.sidecar_exists`.
- `course.read_course(root)` on a root with no sidecar raises `CourseError`
  with code `course.no_sidecar`.
- `course.write_course(root, doc, wrong_fingerprint, "human", "weibao")` raises
  `JournalError` with code `journal.stale_preflight`, and the sidecar bytes on
  disk are unchanged.
- `course.write_course` with the correct `expected_fingerprint` returns
  `revision == 2` with `parent_revision == 1` and the same `object_id`.
- 14B mints no new object kind: `identity.OBJECT_KINDS` after importing
  `graph`, `course`, and `course_package` still has exactly six members and
  does not contain the string `"edge"`.

The Phase 13.9 supersession path (assertions for option-a; replaced per Task 2
if another option was chosen):

- `fixtures.corpus_14b.build_stub_course(dest)` writes a `course.md` carrying
  the 13.9 header, a `## Sources` table, and a `## Objectives` table with three
  rows.
- `course.migrate_stub(root, "agent", "claude-code")` creates
  `course-graph.md`, returns a dict whose `objectives` is `3`, and appends a
  journal entry.
- The bytes of `course.md` read before `migrate_stub` equal the bytes read
  after it, exactly. A hand-authored file is never rewritten.
- `course.migrate_stub` on a root with no `course.md` raises `CourseError` with
  code `course.stub_absent`.

Package and clean restore, one path (PORT-03):

- `course_package.export_package(root, root, pkg)` writes `manifest.json`,
  `payload/<course object id>.md`, and returns a manifest dict whose `state` is
  `"applied"` and whose `entries` has at least one member whose key set equals
  `set(course_package.MANIFEST_ENTRY_KEYS)`.
- The manifest's course entry `fingerprint` equals
  `identity.object_fingerprint(<the sidecar bytes>, "course")`.
- `course_package.restore_package(pkg, clean_dest, "human", "weibao")` on a
  destination directory that contains no `_journal`, no `_evidence`, and no
  prior file reproduces `course-graph.md` with bytes equal to the original, and
  returns a report whose `entries_verified` is the manifest entry count and
  whose `complete` is `True`.
- The restore report is computed by recomputing each payload fingerprint, not
  by reading the manifest's own claim: corrupting one payload byte after export
  makes `restore_package` raise `PackageError` with code
  `package.fingerprint_mismatch` naming the expected and found values.
- A manifest whose `state` is `"prepared"` raises `PackageError` with code
  `package.not_applied`.
- `course_package.safe_target(dest, "../escape.md")` raises `PackageError` with
  code `package.path_escape`, and so does an absolute `relpath`, and so does
  `"payload/../../escape.md"`. The refusal is a raise, never a clamp to a safe
  path.

Tier and boundary assertions, structural rather than maintained by care:

- `hasattr(graph, "model")`, `hasattr(graph, "journal")`,
  `hasattr(graph, "os")`, and `hasattr(graph, "evidence")` are all `False`.
  `graph.py` performs no file input or output and never reaches the one parser.
- `hasattr(course, "evidence")` is `False`.
- `hasattr(course_package, "urllib")`, `hasattr(course_package, "socket")`, and
  `hasattr(course_package, "subprocess")` are all `False`. A restore is an
  offline operation.
  </behavior>
  <action>
1. Create `tests/graph_roundtrip.py` first, with the local `fail(msg)` helper
   that prints `"FAIL: " + msg` and calls `sys.exit(1)`, the `ROOT` and
   `sys.path.insert` header convention every existing roundtrip test uses, a
   `check_thin_slice()` function holding every assertion in `<behavior>`, and a
   `main()` that calls it and prints `OK graph_roundtrip`. Run it with
   `python tests/graph_roundtrip.py` and confirm it fails because the modules
   do not exist yet.

2. Create `fixtures/corpus_14b.py` with `build_three_domains(dest)`,
   `build_stub_course(dest)`, and `teardown(dest)`. In this plan
   `build_three_domains` only needs to build the FIRST domain,
   `meridian-field-response`, with one container labeled `module`, two
   objectives, and one `prerequisite-of` edge between them; plan 14B-02 widens
   it to three domains. All content is fictional and generated from a fixed
   seed so a rebuild is byte-identical. No real course, book, learner, or bank
   content of any kind. `build_stub_course(dest)` writes a `course.md` whose
   first line is `# Course manifest (DRAFT STUB, 2026-08-14)` followed by the
   four-line 13.9 header paragraph, a `## Sources` table with the columns
   `id | path | format | size | sha256`, and a `## Objectives` table with the
   columns `id | objective | citation | treatment | reason` and three rows.

3. Create `graph.py` at the repository root. Open it with a module docstring
   restating the peer-module contract from `evidence.py` lines 1 to 19, and
   stating in plain sentences: this module is the model tier; it performs no
   file input or output; it never imports `model`, `runtime`, `journal`, or
   `evidence`; it reads and writes only this phase's own course sidecar tables
   and never bank or lesson bytes, so the one parser in `model.py` stays the
   one parser; and it computes no completion, mastery, or readiness value of
   any kind, because that tuple is GRAPH-03's and is read over the graph rather
   than stored in it. No em dash characters anywhere in the file.

4. Define in `graph.py`: `COURSE_GRAPH_VERSION = 1`; `EDGE_TYPES` as the frozen
   four-name tuple from D-14A-1 in the order `("prerequisite-of",
   "covers-objective", "source-supports", "treatment-of")`;
   `DEGRADED_EDGE_TYPE = "recommended-before"`; `SECTION_ORDER = ("Course",
   "Structure", "Objectives", "Sources", "Edges", "Bindings", "Migrations",
   "Log")`; and `HEADER_FIELDS = ("graph_schema_version", "course_object_id",
   "title")`.

5. Define `GraphError(Exception)` carrying `.code` and `.message`, using the
   same two-argument constructor shape `identity.IdentityError` uses. Its two
   codes and their exact message templates for this plan:
   - `graph.future_schema_version`: `"this course graph declares schema version
     %d and this build understands version %d; refusing to read it rather than
     silently dropping fields it does not know"`
   - `graph.malformed_section`: `"the section %s is not a table and cannot be
     read as records; the file is preserved unchanged and no write is
     attempted"`

6. Implement `new_course`, `parse_course`, and `serialize_course`. The
   serialized form is exactly: the line `# Course graph`; a blank line; the
   four-line explanatory paragraph whose first line is `This file is the
   durable cross-object course graph for this course. It is`; a blank line; the
   header table with the column headers `field` and `value` and one row per
   `HEADER_FIELDS` entry; then each section of `SECTION_ORDER` after `Course`
   as a `## ` heading followed by its pipe table; then every preserved unknown
   section, in the order it appeared in the source text, after the known ones.
   Column sets: `## Structure` is `id | label | parent | order | title`;
   `## Objectives` is `id | container | order | statement | origin |
   import_version | overlays`; `## Sources` is `source_object_id | title |
   note`; `## Edges` is `source | edge_type | target | authority | rationale |
   confidence | override`; `## Bindings` is `binding_kind | objective |
   source_object_id | treatment_kind | locator | state | confidence |
   rights_snapshot`; `## Migrations` is `migration_id | kind | from | to |
   rationale | state | actor | timestamp`; `## Log` is `timestamp | note`. Any
   column present in the source text that is not in the known set for that
   section is stored on the record under the key `extra` and re-emitted in its
   original column position, which is what makes the round trip byte-stable.

7. Implement `add_container(doc, label, title, parent="", order=None)`,
   `add_objective(doc, statement, container="", order=None, origin="local")`,
   and `add_edge(doc, source, edge_type, target, authority="proposed",
   rationale="", confidence="unknown", override="advisory")`. Each mints its
   record id with `identity.new_object_id()`, mutates `doc` in place, and
   returns the created record. `add_container` and `add_objective` add nothing
   to `doc["edges"]`, which is the GRAPH-01 assertion that structural order
   mints no prerequisite edge.

8. Implement `outline_projection(doc)` returning plain Markdown text exactly as
   described in `<behavior>`: the course title as an `h1`, each container as a
   heading one level deeper than its parent in authored order, each objective
   as a list item `- <statement> [<objective id>]` in authored order, objectives
   with no container under a final `## Unplaced` heading, and the single line
   `No objectives are recorded yet.` when there are no objectives at all.

9. Create `course.py` at the repository root, a runtime-tier peer of
   `journal.py`. Its module docstring states in plain sentences: this module
   owns the course sidecar's lifecycle; every durable write goes through
   `journal.commit_operation` and this module adds no second atomic-write
   helper; the sidecar is exactly one `kind="course"` object with one
   compare-and-swap lineage per D-14A-1 and `14B-RESEARCH.md` Pattern 1; and
   this module deliberately does not import `evidence`, so the rule that a
   migration never transfers evidence is structural rather than maintained by
   care. No em dash characters.

10. Define in `course.py`: `COURSE_SIDECAR_FILENAME = "course-graph.md"`,
    `STUB_FILENAME = "course.md"`, `COURSE_KIND = "course"`, and
    `CourseError(Exception)` with `.code` and `.message`. Its three codes and
    exact message templates for this plan:
    - `course.no_sidecar`: `"no course graph exists at %s; create one with
      course.create_course before reading or binding anything"`
    - `course.sidecar_exists`: `"a course graph already exists at %s; refusing
      to overwrite it"`
    - `course.stub_absent`: `"no Phase 13.9 course stub exists at %s; nothing
      to migrate"`

11. Implement `sidecar_path`, `create_course`, `read_course`, `write_course`,
    and `migrate_stub`. `create_course` mints the course object id with
    `identity.new_object_id()`, builds the document with `graph.new_course`,
    and calls `journal.commit_operation(base=course_root, object_id=<id>,
    kind="course", rel_path=COURSE_SIDECAR_FILENAME, operation="mint",
    new_bytes=<serialized>, expected_fingerprint=None, actor_kind=...,
    actor_name=..., create_if_missing=True)`. `read_course` returns a dict with
    the keys `doc`, `text`, `fingerprint`, `revision`, `object_id`, and
    `state`, where `state` comes from `journal.object_state`. `write_course`
    calls `journal.commit_operation` with `operation` defaulting to
    `"edit_in_place"` and passes `expected_fingerprint` straight through, so a
    stale write is refused by the 14A path and not by a second check here.
    `migrate_stub` reads `STUB_FILENAME` for reading only, parses its
    `## Sources` and `## Objectives` tables, builds a document, calls
    `create_course`-equivalent commit with `operation="import"`, and never
    opens `STUB_FILENAME` for writing.

12. Create `course_package.py` at the repository root, a runtime-tier peer of
    `audit_writer.py`. Its module docstring states in plain sentences: a
    package is a plain directory tree first and an archive only as optional
    transport; a package received from another machine is untrusted input the
    moment it crosses a machine boundary, so every restore target path is
    resolved and contained before anything is written; and restore recomputes
    every fingerprint rather than trusting the manifest's own claim. No em dash
    characters.

13. Define in `course_package.py`: `PACKAGE_SCHEMA_VERSION = 1`,
    `MANIFEST_FILENAME = "manifest.json"`, `PAYLOAD_DIRNAME = "payload"`,
    `PACKAGE_STATES = ("prepared", "applied")`, `MANIFEST_ENTRY_KEYS =
    ("object_id", "kind", "revision", "relpath", "fingerprint")`, and
    `PackageError(Exception)` with `.code` and `.message`. Its three codes and
    exact message templates for this plan:
    - `package.path_escape`: `"the package entry %s resolves outside the
      restore destination; refused, never clamped"`
    - `package.not_applied`: `"this package's manifest state is %s, not
      applied; it was interrupted during export and must not be restored"`
    - `package.fingerprint_mismatch`: `"payload %s does not match its manifest
      fingerprint; expected %s, found %s"`

14. Implement `safe_target(dest, relpath)`: refuse an absolute `relpath`,
    refuse any `relpath` containing a `..` path component, then join and
    resolve with `os.path.realpath` and refuse unless the result is genuinely
    contained in `os.path.realpath(dest)` using `os.path.commonpath`. Refuse by
    raising `PackageError("package.path_escape", ...)`. Never return a clamped
    or corrected path.

15. Implement `export_package(base, course_root, dest)` for the single course
    object only in this plan: write `manifest.json` with `state` `"prepared"`
    first, write `payload/<object_id>.md`, re-read and re-fingerprint every
    payload file, then rewrite `manifest.json` with `state` `"applied"`. Use
    the atomic tmp-then-`os.replace` idiom from `audit_writer.py` for every
    write. Implement `restore_package(package_root, dest, actor_kind,
    actor_name)`: refuse a manifest whose `state` is not `"applied"`, route
    every write target through `safe_target`, recompute each payload's
    fingerprint with `identity.object_fingerprint(raw, entry["kind"])`, refuse
    on mismatch, and return the report dict described in `<behavior>`.

16. Re-run `python tests/graph_roundtrip.py` until it passes, then run
    `python itembank.py guard .` and confirm it reports `0 offending files`.
  </action>
  <verify>
  <automated>python tests/graph_roundtrip.py</automated>
Expected: prints `OK graph_roundtrip` and exits 0. Also run
`python itembank.py guard .`, expected final line `0 offending files` and exit
code 0. Degraded states this task proves, each with its own assertion in
`<behavior>`: a future schema version is refused by name rather than
partially read; a malformed section is refused with the file left unchanged; a
stale compare-and-swap write is refused and the bytes on disk do not move; an
interrupted export leaves a manifest in `prepared` state that restore refuses;
a corrupted payload byte is caught by recomputation rather than trusted; and a
traversing package entry is refused rather than clamped.
  </verify>
  <acceptance_criteria>
- `python tests/graph_roundtrip.py` exits 0 and prints `OK graph_roundtrip`.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `graph.py` contains `def outline_projection(` and `def parse_course(`.
- `course.py` contains `def create_course(` and `def migrate_stub(`.
- `course_package.py` contains `def safe_target(` and `def restore_package(`.
- `python -c "import graph; print(hasattr(graph,'model'), hasattr(graph,'os'), hasattr(graph,'journal'))"`
  prints `False False False`.
- `python -c "import course; print(hasattr(course,'evidence'))"` prints
  `False`.
- `python -c "import course_package as p; print(hasattr(p,'urllib'), hasattr(p,'socket'), hasattr(p,'subprocess'))"`
  prints `False False False`.
- `python -c "import graph, course, course_package, identity; print(len(identity.OBJECT_KINDS))"`
  prints `6`.
- `git diff --name-only` after this task does not list `journal.py`,
  `identity.py`, `discovery.py`, `model.py`, `runtime.py`, or any path under
  `surfaces/` or `schemas/`.
- None of `graph.py`, `course.py`, `course_package.py`,
  `fixtures/corpus_14b.py`, or `tests/graph_roundtrip.py` contains an em dash
  character.
  </acceptance_criteria>
  <reversibility rating="costly">The sidecar's table column sets and the
  manifest entry key set are consumed by plans 02 through 06. Changing them
  before the 14B freeze gate costs one edit plus one fixture regeneration;
  changing them after a package has been handed to another machine means a
  manifest migration. The genuinely one-way part, the on-disk path, is gated by
  Task 2 above.</reversibility>
  <done>One synthetic objective travels mint, edge, sidecar
  compare-and-swap write, outline projection, package export, and clean-machine
  restore in one green test, and the three new modules exist in their thinnest
  production-quality form.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| package archive to restore path | A package built on another machine crosses into `course_package.restore_package`. This is the one place in Phase 14B where the project's single-local-user posture stops applying, because of the friend-installs-a-copy goal recorded in the amended Users constraint in `.claude/CLAUDE.md`. |
| course root to sidecar reader | Arbitrary, possibly hand-edited or externally edited Markdown crosses into `graph.parse_course`. |
| Phase 13.9 stub to migration reader | A file authored by a human outside this repository is read, and could be rewritten if the migration is destructive. |
| caller to compare-and-swap write | A caller supplies an expected fingerprint that decides whether a durable write proceeds. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14B-01-01 | Tampering / Elevation of Privilege | `course_package.restore_package` payload target paths (Zip Slip class) | high | mitigate | Every target goes through `safe_target`, which refuses an absolute path, refuses any `..` component, and refuses any `os.path.realpath` result not contained in the destination by `os.path.commonpath`. The refusal raises `package.path_escape` and never clamps. Asserted with `../escape.md`, an absolute path, and `payload/../../escape.md`. |
| T-14B-01-02 | Tampering | a corrupted or substituted payload restored as authentic | high | mitigate | `restore_package` recomputes `identity.object_fingerprint` for every payload and compares to the manifest, refusing with `package.fingerprint_mismatch`. A restore that trusts the manifest is not a validated restore. Asserted by corrupting one byte after export. |
| T-14B-01-03 | Tampering | an interrupted export restored as if complete | high | mitigate | The manifest is written with `state` `"prepared"` before any payload and flipped to `"applied"` only after every payload re-verifies, the `audit_writer.py` shape. `restore_package` refuses a non-applied manifest with `package.not_applied`. |
| T-14B-01-04 | Tampering | a human-authored Phase 13.9 `course.md` rewritten by a tool | high | mitigate | Under the recommended option-a, `course.py` never opens `STUB_FILENAME` for writing, and the test asserts the stub's bytes are identical before and after `migrate_stub`. Under option-b the mitigation changes to the journal before-image, which Task 2 records explicitly. |
| T-14B-01-05 | Tampering | a future-version sidecar partially read, silently dropping fields | high | mitigate | `graph.parse_course` refuses a declared version above `COURSE_GRAPH_VERSION` with `graph.future_schema_version`, and preserves unknown sections and unknown columns verbatim on round trip so an older build never destroys a newer build's fields. |
| T-14B-01-06 | Elevation of Privilege | the graph kernel gaining file, network, or parser authority | high | mitigate | `graph.py` imports no `os`, no `journal`, no `evidence`, and no `model`, asserted at runtime. `course_package.py` imports no `urllib`, no `socket`, and no `subprocess`, asserted at runtime, so a restore is structurally offline. |
| T-14B-01-07 | Information Disclosure | real course or learner content entering this repository as a fixture | high | mitigate | `fixtures/corpus_14b.py` generates fictional content from a fixed seed, trees are built into temp directories, and `python itembank.py guard .` is part of this task's acceptance criteria. |
| T-14B-01-08 | Tampering | supply chain: a third-party archive, graph, or schema package introduced here | high | mitigate | None is added; `hashlib`, `json`, `os`, and `uuid` are Python 3.11 standard library already imported by shipped modules. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
| T-14B-01-09 | Denial of Service | a malformed sidecar section crashing the reader or looping it | medium | mitigate | A section that is not a table raises `graph.malformed_section` immediately and performs no write; `graph.py` has no recursion over user-supplied structure in this plan. |
| T-14B-01-10 | Repudiation | a sidecar write with no recorded actor | low | accept | `journal.commit_operation` records `origin` with `actor_kind` and `actor_name`; a caller passing an empty name records an empty name honestly. Accepted because 14B has a single local user and the acceptance-policy decision D-12.6-4 is still open. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- No CLI command and no daemon route for anything in this phase.
  `OPERATION-CONTRACT.md` "Pending surfaces" names "A course manifest or course
  package command (14B)" and the discovery and binding commands as not yet
  shippable, and says in plain words: do not invent commands for them.
- No skill documentation for any of this. The 999.5 rule holds: a skill
  documents only a shipped command surface, and this phase ships none.
- No modification of `journal.py` or `identity.py`. The `migrate` record type is
  plan 14B-04's single-line addition.
- No modification of `model.py`, `runtime.py`, `evidence.py`, `discovery.py`,
  or anything under `surfaces/`, `schemas/`, or `retention.py`.
- No edge vocabulary work beyond storing an edge row. Validation, the degrade
  path, and the GRAPH-02 carried fields are plan 14B-02's.
- No binding rights enforcement, no source binding, no treatment binding. Those
  are plan 14B-03's.
- No migration proposals, no split, merge, or rename. Those are plan 14B-04's.
- No loss report, no evidence export, no archive transport. Those are plan
  14B-05's.
- No freeze record. Plan 14B-06 declares the freeze, and only on a green tracer
  with the Phase 13.9 precondition satisfied.
- No reconciliation of the shipped item-level free-text `objective` field with
  the new objective ids. `14B-RESEARCH.md` Open Question 1 recommends deferring
  it; no GRAPH requirement or fixture names it; a later phase that builds a real
  course over real content owns it. Recorded here so a later phase does not
  assume it silently exists.
- No progress, completion, mastery, or readiness value of any kind. That tuple
  is GRAPH-03's, owned by 16C, and is read over the graph rather than stored in
  it.
</out_of_scope>

<summary_obligations>
`14B-01-SUMMARY.md` records: the precondition result and every deviation the
landed 14A surface showed against the 14A plan text; the option Weibao chose at
Task 2 and any plan edits that choice forced in plans 02 through 06; which
truth was verified by which command; the measured wall-clock time of one
`check_thin_slice()` run, recorded and not promised; and any deviation from
this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/14B-graph-course-package-prototype/14B-01-SUMMARY.md`
when done.
</output>
