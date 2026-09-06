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

- **19A-02, executed 2026-09-05**, on commit `5e9d4eb`
  ("feat(course): the dispatch spine, and a course you can create from a
  surface"). The source-binding family, D-07's second row, hung in the spine
  19A-01 built.
- **What landed.** Four `$defs` nodes in
  `schemas/course_operation.schema.json` (`add_source`, `bind`, `rights`,
  `bindings`) plus six shared ones, all six operations in the top-level
  `oneOf`; `_op_add_source`, `_op_bind`, `_op_rights`, `_op_bindings` in
  `surfaces/course_ops.py`; `POST /api/course/add-source` and `POST
  /api/course/bindings` as new routes, with `POST /api/course/bind` and
  `POST /api/course/rights` re-hung in the spine at their published paths
  and with their published response envelopes intact; `itembank course
  add-source` and an `itembank bind` that now dispatches through
  `course_ops.run`; `ROUTE_CLI` and `SURFACE_PARITY` rows in the same
  commit (`course_add_source`, `course_bindings`); the new checks in
  `tests/course_ops_roundtrip.py` and the route-scope count in
  `tests/daemon_roundtrip.py`.
- **The gap the wave actually closed.** `graph.add_source` had no caller
  outside two tests. A source could be imported (the journal registry held
  the object) and bound (a binding row names an object id), and the course's
  own Sources section stayed empty, so the Sources area, `itembank bind
  list` and any package manifest that walks the sidecar could not see it.
  `add_source` is that door. It refuses a source the registry does not hold,
  because a row naming nothing is a durable claim with nothing behind it,
  and refuses a second row for one source, because a Sources row is a
  reference and not a claim about a place the way a binding row is.
- **D-07's read functions got a reader.** `graph.validate_binding` and
  `course.rights_for_binding` had no surface at all. The `bindings`
  operation runs every row through the first and re-reads every right
  through the second, and reports the recorded snapshot beside the current
  state. That divergence, a snapshot still saying `granted` after the grant
  was revoked, is the one thing a coverage claim cannot notice about itself,
  and it fills `source binding / explain` on the grid.
- **The grid moved 40 -> 41 of 82.** `source binding / explain` is filled.
  `source / create` gained its second command, and `rights grant / explain`
  stays empty with a narrower note: the right each binding consumes and its
  current state are now visible, and what is still missing is why an export
  or a package that already refused did so.
- **One new rule in the spine, and it is about addressing.** `run` takes an
  optional already-resolved `base`, because `itembank bind --base .`
  addresses the course root a person is standing in while the route
  addresses a course by id. The request document is unchanged by this: the
  command reads the course's own `course_object_id` off the sidecar and
  sends that, so no request on either surface carries a path.
- **Deviation, stated rather than absorbed.** `_course_operation` gated
  every course write with `_reject_cross_origin` only, which is the
  read-side check. On a `--lan` daemon that let a phone on the same wifi
  mint, rename and bind a course, while `/api/source/import`, every day
  write and every theme save were already loopback-only. The spine now
  chooses its gate by what the operation does, using
  `course_ops.READ_OPERATIONS`. The shared refusal said "day write
  requires a loopback client" while already gating
  `/api/source/import`; it now says "this write", because a course
  write refused with the word day in it is a refusal that
  misdescribes itself. This is a hardening of 19A-01's own spine
  rather than 19A-02 scope, and it is recorded here rather than left as a
  silent behaviour change: a LAN client that was minting courses will now be
  refused, which is the intended correction.
- **D-09 read, and the deviation from it is the same one 19A-01 declared.**
  No new UI screen, no assessment route touched, no format change, no new
  module: the four operations went into `surfaces/course_ops.py` and the two
  handlers into `surfaces/daemon.py`, beside their neighbours.
  `_binding_course_dir` in `daemon.py` was deleted, not left dead, because
  the spine's `resolve_course` is the same resolution.
- **Defect found and fixed the next session, in 19A-02's own work.** The
  `bind` node's `treatment` enum had been written out by hand and did not
  match `graph.TREATMENT_KINDS`: it named seven treatments the engine does
  not have (`quiz`, `exam`, `practice-set`, `flashcards`, `project`,
  `discussion`, `tutoring`) and omitted seven it does (`notes-or-terms`,
  `visual-or-demonstration`, `practice`, `formal-test`,
  `assessment-first-diagnostic`, `learner-artifact`, `human-review`), so a
  legitimate treatment binding for seven of the eleven kinds was refused by
  the published document on both surfaces at once. It escaped the wave
  because the existing treatment tests call `binding_cli.bind` directly and
  the one HTTP binding test binds a source. The enum now equals the tuple,
  and `tests/course_ops_roundtrip.py` asserts every closed vocabulary the
  document publishes against the engine tuple it copies, which is the check
  that would have caught it. A published enum is a copy, and a copy drifts;
  the fix is the assertion, not more care.
- **What 19A-02 deliberately did not do.** `source binding / change` and
  `source binding / undo` stay empty. Re-pointing or removing a binding
  needs an engine function `graph` does not have, and the reach milestone
  adds no capability; the undo sentences those operations return say plainly
  that the reversal today is restoring the sidecar's previous journalled
  revision, rather than naming a command that does not exist. The treatment
  half of the `bind` node is served because the route already served it
  before the spine existed; 19A-04 gives the treatment family its own
  operations and this node keeps working.

- **19A-03, executed 2026-09-05.** The structure and objective-editing
  families, D-07's third and fourth rows, in one wave because the plan table
  pairs them and because an objective with no container to sit in and no edge
  to relate it is only half a door.
- **What landed.** Eight `$defs` nodes (`add_container`, `add_objective`,
  `add_edge`, `structure`, `rename_objective`, `split_objective`,
  `merge_objectives`, `overlay_objective`) plus six shared ones; eight
  operations in `surfaces/course_ops.py` over one shared `_edit_sidecar`;
  eight routes and eight handlers in `surfaces/daemon.py`; eight
  `itembank course` subcommands; `ROUTE_CLI` and `SURFACE_PARITY` rows in the
  same commit; new checks in `tests/course_ops_roundtrip.py` and the
  route-scope count at thirty in `tests/daemon_roundtrip.py`.
- **The grid moved 41 -> 43 of 82.** `objective / create` and
  `objective / change` are filled, and `course / change` and
  `objective / inspect` gained commands. `objective / undo` stays empty with
  a truer note: an identity move is reversed by REJECTING its migration, and
  the accept and reject doors are 19A-07's wave.
- **One shared helper, and it is a correctness argument rather than
  tidiness.** All eight writes are an `edit_in_place` on one file, so
  `_edit_sidecar` reads, lets a closure edit the parsed document, and writes
  back through the one compare-and-swap path. Eight separate read-and-write
  bodies would have been eight chances to forget the expected fingerprint,
  and a durable write without one is the silent overwrite the rule exists to
  prevent. `journal.OPERATION_TYPES` is still six.
- **What the wave refuses to do, which is most of what it is for.** A
  container and an objective each add zero edges, so an outline never becomes
  a prerequisite claim by accident (GRAPH-01). A prerequisite pointing
  backwards through the authored order is RECORDED and returned as a warning,
  never refused and never fixed: the authored sequence is the author's, and a
  surface that silently reordered it would make every future diff unreadable.
  A cycle is named and never broken. `propose_order` returns a sequence and
  writes nothing. Rename, split and merge each add rows and delete none, and
  record the migration as `proposed`, because the identity a learner's
  evidence was recorded against has to stay in the file or that evidence
  stops naming anything. An imported objective is never edited in place and
  `overlay_objective` is the door that revises it.
- **The `add_objective` node deliberately publishes no `origin` field.** An
  imported scope binds as an immutable version, so a client that could claim
  `imported` could make a hand-authored row un-editable for a reason that was
  never true, and the only way back would be an overlay onto an import that
  never happened. The test asserts the field's absence, not just the
  behaviour.
- **The CLI became schema-driven.** `cmd_course` fills each property the
  operation's node declares from the argparse attribute of the same name, so
  adding an operation is adding a node and a parser and nothing else. A test
  asserts every published field of every operation has an argument on its
  twin and every required field is required, which is the check that would
  have caught a field reachable from the route and not from the command.
- **Two structural test improvements, both prompted by this wave.** The
  loopback-gate check now RUNS every operation the spine calls a read against
  a real course and asserts the sidecar's fingerprint and revision are
  unchanged, so a later wave that misclassifies a write as a read fails there
  rather than serving that write to a phone on the same wifi. And every route
  in the namespace is checked to name a handler that exists and is callable,
  because `_dispatch` resolves a handler by name out of the module globals
  and a name with a typo in it dispatches to nothing while both route tables
  still look right.
- **One test was written twice, and the second version is the honest one.**
  The handler-wiring check first POSTed an empty body to all fourteen routes
  and asserted a typed 400. It was flaky at one run in three, and raising the
  timeout from five seconds to thirty did not fix it, so it was not latency.
  A probe of 120 sequential POSTs across old and new routes showed zero
  timeouts, so it is not the routes either, and the daemon's captured output
  pipe is already drained on a background thread, so it is not a full pipe.
  What remains is the same intermittent daemon hang
  `check_concurrent_requests_share_one_session` has been failing on at HEAD
  on this machine. Whether a handler name resolves is a static property, so
  it is now asserted statically and the check is stable at six runs of six;
  the routes' behaviour is covered by the request checks above. A test that
  fails for a defect it is not measuring is a test nobody reads, and the
  hang itself is tracked separately rather than absorbed here.


- **19A-04, executed 2026-09-05**, on commit `d89501b`
  ("feat(course): the source-binding, structure and objective-editing
  families"). The treatment family, D-07's fifth row.

- **D-11, the choice the plan left open, decided and recorded: the treatment
  family gets its own operations, and `bind`'s treatment half is deprecated
  in place.** The `bind` node already served treatment bindings, so the
  question was whether to formalise that or mint a door. What settled it is
  not tidiness, it is typing. `schema_validate` implements no `if`/`then`
  and no `dependentRequired`, so on a node that serves both binding kinds
  `treatment` HAS to be optional, and the requirement is enforced one call
  later in `binding_cli.bind`. The request document is the generated MCP
  tool signature (999.3 success criterion 1), so that node produces a tool
  advertising an optional field the runtime insists on: it fails at call
  time instead of at type time, and an agent client has no way to know which
  fields are really required. That is D-02's own argument, that an untyped
  tool defeats the phase, one level down from the route shape.

  So `bind_treatment` exists and requires `treatment`. It is a TYPING of the
  older mode and not a second writer: both reach `course.bind_treatment`
  through the same `binding_cli.bind`, and
  `check_the_deprecated_bind_mode_writes_the_same_row` asserts the two leave
  byte-identical sidecar rows. If they ever diverge this repository has two
  writers for one durable object, which is the thing the assertion exists to
  make impossible rather than merely unlikely.

  `bind` keeps accepting `binding_kind: "treatment"`, unchanged, and its
  result now carries a `deprecated` sentence pointing at the new operation.
  This is D-02a's shape again and non-negotiable 4's deprecation path: the
  old door keeps serving, the canonical door is typed, retirement is an
  explicit `migrate` once nothing calls it. `itembank bind treatment` was
  moved onto `bind_treatment`, so the deprecated mode has one caller (a
  client that already used it) rather than two.

- **The gap the wave actually closed, which was neither of those.**
  `graph.treatment_right` and the eleven-kind `TREATMENT_RIGHTS` table had
  no reader on any surface. That mapping decides which treatments a course
  may use for a given source, and the only way to learn it was to attempt a
  binding and be refused, one kind at a time. A learner who had granted
  `read` and not `transform` could bind a direct reading and not a guided
  lesson, and nothing anywhere said so beforehand. `treatments` is that
  reader: the eleven kinds, the right each consumes, and, when a source is
  named, that right's state read FRESH through `course.rights_for_binding`,
  with the count of treatment bindings this course already records for each
  kind beside it. It reports and never grants; the way to change an answer
  is to record the right, which is a different operation with a different
  authority behind it.

  The test is not that the table prints. Every kind the read calls bindable
  is bound for real and every kind it calls refused is refused for real,
  against the same course at the same moment, so what the read reports and
  what the next write enforces cannot disagree.

- **What landed.** A shared `treatment_kind` `$defs` node plus the
  `bind_treatment` and `treatments` operation nodes, all three in the
  top-level `oneOf`; `_op_bind_treatment`, `_op_treatments` and
  `_treatment_sentence` in `surfaces/course_ops.py`;
  `POST /api/course/bind-treatment` and `POST /api/course/treatments` with
  their handlers in `surfaces/daemon.py`; `itembank bind treatments` and an
  `itembank bind treatment` re-pointed at the new operation; `ROUTE_CLI` and
  `SURFACE_PARITY` rows in the same commit (`bind_treatment`,
  `course_treatments`); four new or extended checks in
  `tests/course_ops_roundtrip.py`; the route-scope count at thirty-two in
  `tests/daemon_roundtrip.py`; the grid cells; `capabilities.json`
  regenerated.

- **The published treatment vocabulary now has exactly one copy.** The
  `bind` node inlined its own enum and drifted the day it was written
  (19A-02's recorded defect). Both nodes now `$ref` a single
  `#/$defs/treatment_kind`, the drift assertion reads that one node, and a
  second assertion fails if either node inlines an enum again. One copy of
  an engine tuple drifts; two copies drift apart twice as fast, and the fix
  for a copy is never more care.

- **The grid moved 43 -> 44 of 82.** `rights grant / explain` is filled, and
  `source binding / create` gained the typed route. The remaining half of
  that cell is stated rather than absorbed: what is still missing is the
  refusal's own history, why an export or a package that already refused did
  so, which is 19A-08's read.

- **D-05 held, D-09 read.** `journal.OPERATION_TYPES` is untouched at six; a
  treatment binding is the same `edit_in_place` a source binding is. No new
  UI screen, no assessment route touched, no format change, no new module.
  `treatments` is in `READ_OPERATIONS`, so the loopback-gate check runs it
  against a real course and asserts the sidecar is untouched.

- **Test state, reported rather than rounded.** `tests/daemon_roundtrip.py`
  fails identically in this tree and in a clean worktree at `d89501b`, on
  `check_concurrent_requests_share_one_session` timing out: the intermittent
  daemon hang 19A-03 already tracked, not this wave. The route-scope check
  passes at thirty-two. `tests/course_ops_roundtrip.py` is green 24 runs of
  24 when run alone; it failed twice early in the wave, both times in
  `check_the_route_is_the_cli_twin` with an HTTP request returning no status
  at all, under concurrent load and in the same shape as that hang.


## Plan set

Sequential waves; the executor runs one at a time.

| Plan | What it lands |
|---|---|
| 19A-01 | Precondition halt, the dispatch spine, the first family (course lifecycle) end to end through route, twin, schema, and parity row, as the pattern every later plan copies |
| 19A-02 | Source binding, with rights read at bind time (executed 2026-09-05) |
| 19A-03 | Structure and objective editing (executed 2026-09-05) |
| 19A-04 | Treatment binding (executed 2026-09-05) |
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
