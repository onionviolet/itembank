# Phase 19A context: the course operating surface

- **Gathered:** 2026-09-05, planning-only session, autonomous under
  `PLANNING-DIRECTIVES.md` section 2. Decisions recorded here are binding on
  the 19A plan set and are not re-litigated at execution.
- **Phase entry:** `.planning/REACH-MILESTONE.md`, Phase 19A.
- **Evidence:** `.planning/research/2026-09-05-what-the-vision-still-needs.md`
  section 2.2, whose numbers were measured rather than read.
- **Registered basis:** `IDEA-LEDGER.md` `IL-20260905-06`.

## Domain

19A is not a feature phase. Every operation it exposes already exists, is
frozen, and is under test. What is missing is dispatch, a published request
document, and a parity row. An executor that finds itself designing a course
operation has misread this phase; the operation is in the engine, and the plan
names the function.

The defect being closed is the 2026-08-21 defect at milestone scale.
`/lesson/<stem>` returned 200 and rendered correctly while nothing linked to
it, and no framework test could see it because every test knew the URL. The
same is now true of the whole course engine: 387 KB of it, tested, with no
door a person or an agent client can open.

## Decisions

- **D-01 Precondition halt.** Plan 19A-01's first task verifies by file
  presence that 14A, 14B, 14C, 15A and 15B carry freeze records. Any missing
  precondition halts the wave naming the exact missing artifact (16C-01
  precedent). 17B's and 17C's human acceptances are **not** preconditions to
  starting, because this phase adds no durable object and changes no frozen
  contract. They **are** preconditions to freezing 19A.

- **D-02 Route shape, decided so no plan re-decides it.** Course operations
  mount under `POST /api/course/<operation>`, one route per operation, added to
  `API_ROUTES` in the existing tuple form. Not one generic `/api/course` with
  an operation discriminator: 999.3 exposes one MCP tool per `API_ROUTES` entry,
  so a generic route collapses the whole engine into a single untyped tool and
  defeats the phase.

- **D-02a Route shape, amended at execution 2026-09-05 (plan 19A-01).** The
  source-binding door landed on `POST /api/bind` and `POST /api/rights`
  earlier the same day, before this namespace existed, which is 19A-02's cell
  in the wrong route shape. Resolved by re-homing rather than by exception:
  the canonical routes are now `POST /api/course/bind` and
  `POST /api/course/rights`, both reaching the same handlers, and the two
  original paths keep serving from a new `LEGACY_API_ALIASES` tuple in
  `surfaces/daemon.py`, appended to `ROUTES` and deliberately **absent from
  `API_ROUTES`**.

  The absence is the whole point of the shape. 999.3 generates one MCP tool
  per `API_ROUTES` entry, so an alias inside that tuple would mint a second
  tool for one operation and reintroduce, as a duplicate, exactly the untyped
  collapse D-02 refused. An alias outside it reserves no tool name and
  appears in no `SURFACE_PARITY` row, so the tool table stays one tool per
  operation while nothing that already calls the old paths breaks. The
  aliases carry `ROUTE_CLI` entries (the same `bind` twin, because they are
  the same call) and are classified in the surface grid. They are retired by
  an explicit `migrate` once nothing calls them, which is the deprecation
  path non-negotiable 4 allows; retiring them silently is what it forbids.
  `tests/daemon_roundtrip.py:check_api_route_scope` now asserts all three
  facts: the aliases still serve, they are not in `API_ROUTES`, and each
  reaches the same handler as its canonical route. There is one route
  convention, and one declared, tested exception to how it was reached.

- **D-03 Parity is not optional.** Every new route gets a `ROUTE_CLI` entry and
  a `SURFACE_PARITY` row in the same commit. The existing parity test already
  fails on a route without a twin, so this is enforced rather than asked for.
  A CLI twin means the subcommand reaches the same runtime call, not that it
  prints something similar.

- **D-04 Request documents are read off disk.** Each route's request shape is a
  `schemas/*.json` document validated by `schema_validate.py` before dispatch.
  This is what makes 999.3's success criterion 1 mechanical: the MCP tool
  signature is the schema file, so a schema edit changes the tool with no code
  edit. Reuse the five that exist (`course_graph`, `write_manifest`,
  `treatment_recommendation`, `blueprint`, `course_audit_report`) rather than
  minting parallel ones.

- **D-05 No new authority, stated as a test.** Every mutating route reaches
  durable state through `journal.commit_operation` with an expected base
  fingerprint, exactly as the engine already does. No route writes a course
  file directly. `journal.OPERATION_TYPES` stays at its six values (`link`,
  `import`, `copy`, `move`, `edit_in_place`, `supersede`); a plan that needs a
  seventh has found a design change and must stop.

- **D-06 Reads are separated from writes and are cheap.** The read routes
  (outline, coverage claims, untreated objectives, audit report, staleness,
  protocol report) are GET where they take no body. They exist because an agent
  client cannot propose sensibly without them, and because the existing
  `/course/<id>` GET pages should render from the same calls rather than from a
  parallel path.

- **D-07 Operation inventory, by family.** These are the functions each family
  wraps. The list was taken from the modules, not from documentation.

  | Family | Engine functions | Kind |
  |---|---|---|
  | Course lifecycle | `course.create_course`, `read_course`, `write_course` | write, read |
  | Source binding | `course.bind_source`, `graph.add_source`, `graph.validate_binding`, `course.rights_for_binding` | write |
  | Structure | `graph.add_container`, `add_objective`, `add_edge`, `validate_edge`, `propose_order`, `validate_order` | write |
  | Objective editing | `graph.merge_objectives`, `split_objective`, `rename_objective`, `overlay_objective` | write |
  | Treatment | `course.bind_treatment`, `graph.add_binding`, `graph.treatment_right` | write |
  | Director | `director.recommend_treatments`, `recommend_once`, `apply_recommendation`, `accept_revision`, `begin_operation`, `reverse_operation`, `replay_operation`, `autonomy_level`, `authorize_write` | write |
  | Blueprint and audit | `course.bind_blueprint`, `blueprint.validate_blueprint`, `course_audit`, `blueprint_gate`, `staleness_report` | write, read |
  | Migration | `graph.migration_proposal`, `accept_migration`, `reject_migration`, `set_migration_state`, `course.record_migration` | write |
  | Package | `course_package.export_package`, `restore_package`, `verify_manifest`, `loss_report_text` | write, read |
  | Reads | `graph.outline_projection`, `director.coverage_claims_for`, `untreated_objectives`, `protocol_report`, `parity_view` | read |

- **D-08 One family per plan.** Ten families, so the plan set is one spine plan
  plus one plan per family, each landing routes, twins, schemas, and tests
  together. A plan that lands a route without its twin has not finished.

- **D-09 Out of scope, named so an executor does not drift into it.** No new UI
  screens (the `/course/` GET pages already exist and are being filled by
  separate in-flight work). No changes to the assessment routes. No format
  change. No new module: routes live in `surfaces/daemon.py` and twins in
  `surfaces/cli.py`, beside their existing neighbours.

- **D-10 Uncommitted work in the tree, 2026-09-05.** At the time this context
  was written, `surfaces/daemon.py`, `ia.py`, `lesson.py` and `presentation.py`
  carried 341 lines of uncommitted work adding a `/media/<stem>/<name>` route
  and filling the course areas for `17B-03 D-06 item 3`. It is read-only area
  content and collides with nothing here, but it touches the same files.
  Plan 19A-01 rebases on whatever is committed at execution time and states the
  commit it built on.

## Execution record

- **19A-01, executed 2026-09-05**, on commit `28a6da7`
  ("feat(course): bind a source to an objective, from a surface"). D-10's
  uncommitted work was committed before this plan began, so the rebase D-10
  asked for was a no-op.
- **D-01 precondition halt: cleared.** All five freeze records are present:
  `14A-FREEZE.md`, `14B-FREEZE.md`, `14C-FREEZE.md`, `15A-FREEZE.md`,
  `15B-FREEZE.md`. Nothing halted.
- **What landed.** `schemas/course_operation.schema.json` (one `$defs` node
  per operation, the node being the operation's signature);
  `surfaces/course_ops.py`, the spine: read the document off disk, validate
  the request against the node the route's path names, dispatch, return a
  result carrying its own undo sentence; `POST /api/course/create` and
  `POST /api/course/rename` with `handle_api_course_create` /
  `handle_api_course_rename` over one shared `_course_operation`;
  `itembank course create|rename|show`; `ROUTE_CLI` and `SURFACE_PARITY`
  rows in the same commit (`course_create`, `course_rename`); the D-02a
  re-homing above; `tests/course_ops_roundtrip.py`.
- **D-04 reuse, resolved.** Neither `course_graph` nor `write_manifest`
  fits: the first describes the sidecar the operations write, the second the
  writer's own provenance record, and neither is a request. One request
  document was minted rather than reshaping either, and it is one file for
  the whole namespace so `schemas/` does not grow a file per operation.
- **D-05 held.** `journal.OPERATION_TYPES` is untouched at six. A create is
  a `mint`, a rename is an `edit_in_place`, and no route opens a course file
  for writing.
- **The grid moved 38 -> 40 of 82.** `course / create` and `course / change`
  are filled. `tools/surface_coverage.py` gained `course` to
  `SUBCOMMAND_PARENTS` and the four new routes to their cells.
- **D-09 read, and one deviation stated.** No new UI screen, no assessment
  route touched, no format change. One new module was added:
  `surfaces/course_ops.py`. D-09's "no new module" bars a second route table
  and a second parser, and the routes are still in `surfaces/daemon.py` and
  the twins still in `surfaces/cli.py`. The spine itself has to live
  somewhere both import, which is the shape `surfaces/binding_cli.py`
  already set on 2026-09-05: one implementation, two surfaces, so a twin is
  the same call rather than a similar print. Putting it in `daemon.py` would
  have made the CLI import the daemon to reach it.
- **Pre-existing defect repaired in passing.**
  `check_api_route_scope` still asserted sixteen `/api/*` routes while the
  tree carried eighteen, so `tests/daemon_roundtrip.py` was already red on
  `28a6da7`. The count is now twenty and the assertion says what each entry
  is.

## Plan set

Sequential waves; the executor runs one at a time.

| Plan | What it lands |
|---|---|
| 19A-01 | Precondition halt, the dispatch spine, the first family (course lifecycle) end to end through route, twin, schema, and parity row, as the pattern every later plan copies |
| 19A-02 | Source binding, with rights read at bind time |
| 19A-03 | Structure and objective editing |
| 19A-04 | Treatment binding |
| 19A-05 | Director operations, including autonomy level and the reverse and replay paths |
| 19A-06 | Blueprint and audit |
| 19A-07 | Migration |
| 19A-08 | Package export, restore, and the loss report |
| 19A-09 | The read routes, and the `/course/` GET pages rewired to call them rather than a parallel path |
| 19A-10 | Freeze: rebuild the 17B fixture course through routes and twins only, diff it against the committed one, and record the coverage audit |

## Freeze gate

A course created, sources bound, objectives mapped, treatments chosen, audited,
and packaged **entirely through routes and CLI twins**, with no direct module
call in the transcript, and the `SURFACE_PARITY` test green. The 17B fixture
course is rebuilt this way and compared to the committed one; any divergence is
a defect in this phase, not in the fixture.

## Canonical references

- `surfaces/daemon.py`: `ROUTES`, `API_ROUTES`, `ROUTE_CLI`, `SURFACE_PARITY`.
- `journal.py`: `commit_operation`, `OPERATION_TYPES`, `new_entry_id`.
- `schema_validate.py` and `resources.py`, the read-off-disk path
  `protocol_cli.py` already uses.
- `.planning/SOURCE-TO-COURSE.md`, "Agent-operable course workspace".
- `AGENTS.md`, "Object and authority model", for what an operation is.
- `ROADMAP.md` Phase 999.3, whose success criterion 1 this phase makes
  achievable.

## Deferred

- The MCP server itself, which is Phase 19E.
- The agent operation door, which is Phase 19B and needs one of this phase's
  routes to hang on.
- Any judgement about whether `serve` should remain a separate front door, open
  since 2026-08-21.
