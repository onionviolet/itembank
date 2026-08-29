# Phase 16B decisions

This file is the single source of truth for every Phase 16B route, module,
CLI, settings, state-file, and copy decision. Every later 16B plan reads it
before its first task and treats it as transcription rather than judgment: the
route shape, the module boundary, the CLI twin names, the settings key set, and
the first-run state files are settled here and are not re-derived downstream.
Sections `## D1` through `## D9` are transcribed verbatim from the
checker-approved `16B-UI-SPEC.md` and may not be re-argued, re-worded, or
extended. Sections `## D-16B-1` and `## D-16B-3` through `## D-16B-9` are locked
by plan `16B-01`. Task 2 of that plan appends `## D-16B-2` below.

## Transcribed from 16B-UI-SPEC.md (checker-approved 2026-08-15)

## D1. Course-shelf Home lives inside handle_index

Recorded 2026-08-28. Transcribed verbatim from the `16B-UI-SPEC.md` Decisions and Reasoning Log; not re-litigated.

**Decision.** Course-shelf Home lives inside the existing `handle_index`, gated on course existence, rather than a new `/home` or `/courses` route.

**Reasoning.** `16B-RESEARCH.md` Assumption A2 names this explicitly as the safer reading of APP-01; keeping `"/"`'s literal route avoids a second meaning for the app's one entry point and matches the shipped `ROUTE_CLI` mapping (`daemon`) staying unchanged.

**What would overturn it.** If a later phase finds a concrete reason `"/"` must stay the legacy bank index permanently (none found in any read artifact).

## D2. GET /activity is registered now and renders not-yet-available

Recorded 2026-08-28. Transcribed verbatim from the `16B-UI-SPEC.md` Decisions and Reasoning Log; not re-litigated.

**Decision.** `GET /activity` is registered in `ROUTES` now, rendering a "not yet available" state until `journal.py` (14A) lands, rather than being withheld from the route table entirely.

**Reasoning.** APP-02 requires stable deep links; registering the route now means its identity never changes when 14A lands, only its rendered content does. Matches the shipped "detected-and-attach" style graceful-degradation precedent 16A already used for its own unbuilt dependency.

**What would overturn it.** If Phase 14A's actual `journal.py` surface diverges enough from the plan-text signature cited here that the route's shape itself must change (would be caught by the 16B-01 precondition check).

## D3. Course routes use /course/<course_id>/<area> path segments

Recorded 2026-08-28. Transcribed verbatim from the `16B-UI-SPEC.md` Decisions and Reasoning Log; not re-litigated.

**Decision.** Course-level routes use the fixed pattern `/course/<course_id>/<area>` with named area segments (`learn`, `practice`, `test`, `map`, `sources`, `build`, `evidence`), rather than a single generic `/course/<course_id>?view=<area>` query-parameter shape.

**Reasoning.** Matches the shipped fixed-literal-and-stem-parameterised convention already used for `/quiz/<stem>`, `/study/<stem>`, `/lesson/<stem>`; a path segment is also more legible as a stable, bookmarkable deep link than a query string, which better serves APP-02's "stable opaque deep links."

**What would overturn it.** If a concrete conflict with the daemon's existing route-ordering rule surfaces at 16B-01's precondition check.

## D4. Notes get no dedicated route

Recorded 2026-08-28. Transcribed verbatim from the `16B-UI-SPEC.md` Decisions and Reasoning Log; not re-litigated.

**Decision.** Notes get no dedicated top-level or course-level route; they render only as contextual panels inside Learn and Evidence.

**Reasoning.** Synthesis §9.1 states this outcome explicitly and by name ("contextual within Learn and Evidence first; a cross-course destination is deferred until real use demonstrates the need"); this is not an invented decision but a direct transcription of an already-resolved design point.

**What would overturn it.** Explicit user or reviewer signal that cross-course Notes retrieval is needed now, which would also require reopening `NOTE-01`'s scope in Phase 16C, not 16B.

## D5. Search is not built or routed by 16B

Recorded 2026-08-28. Transcribed verbatim from the `16B-UI-SPEC.md` Decisions and Reasoning Log; not re-litigated.

**Decision.** Search (an App-level area synthesis §9.1 names) is not built or routed by this phase.

**Reasoning.** No FLOW-01/02 or APP-01/02/03 fixture gates Search; building it would be scope invention beyond the phase's five requirements. The area name is reserved here (recorded in the IA table) so a later phase does not have to renegotiate its position in the App-level list.

**What would overturn it.** A future phase explicitly assigned Search as a requirement.

## D6. The Activity IA area is distinct from the ACTIVITY-* requirement family

Recorded 2026-08-28. Transcribed verbatim from the `16B-UI-SPEC.md` Decisions and Reasoning Log; not re-litigated.

**Decision.** The Activity IA area (durable agent/maintenance jobs) is explicitly named and typographically distinguished from `REQUIREMENTS.md`'s `ACTIVITY-*` learner-question family.

**Reasoning.** `16B-RESEARCH.md` Pitfall 3 and Assumption A4 flag this as a real prior-art naming collision risk with no existing binding document stating the distinction outright; recording it here closes that gap before any fixture is written under an ambiguous name.

**What would overturn it.** Not applicable, this is a naming-hygiene decision with no plausible reversal.

## D7. No percent-complete number anywhere in the Activity view

Recorded 2026-08-28. Transcribed verbatim from the `16B-UI-SPEC.md` Decisions and Reasoning Log; not re-litigated.

**Decision.** The Activity view's needs-input/outcome states carry no percent-complete number under any circumstance, including for a job with a real, journal-recorded step count (which instead reads "Step {n} of {N}").

**Reasoning.** `GRAPH-03` and `16B-RESEARCH.md` Pitfall 3 both name a percent-complete badge as a specific, named anti-pattern; "Step n of N" conveys the same real information without synthesizing a ratio across what could be heterogeneous steps.

**What would overturn it.** Not applicable, this restates a binding rule rather than choosing between two open options.

## D8. Mode-layer enforcement composition is Phase 16C's

Recorded 2026-08-28. Transcribed verbatim from the `16B-UI-SPEC.md` Decisions and Reasoning Log; not re-litigated.

**Decision.** The mode-layer precedence table is documented and settings-visible in 16B, but its full runtime *enforcement* (a composed resolver function reading every layer's live state) is explicitly out of 16B's scope and belongs to Phase 16C.

**Reasoning.** Directly follows `16B-RESEARCH.md` Open Question 3's own recommendation, which cites `STRATEGY-02` (owned by 16C per the `REQUIREMENTS.md` old-to-new map) as the requirement that actually needs the composed resolver. Duplicating that logic in 16B would create two implementations of the same precedence contract.

**What would overturn it.** If 16C's plan set finds it cannot proceed without 16B shipping a partial resolver, would surface at 16C's own precondition check against `16B-FREEZE.md`.

## D9. Path-bearing copy shows the basename only

Recorded 2026-08-28. Transcribed verbatim from the `16B-UI-SPEC.md` Decisions and Reasoning Log; not re-litigated.

**Decision.** Permission-denied and other path-bearing degraded-state copy shows only the bank-author-written basename, never a resolved absolute path.

**Reasoning.** Directly reuses the shipped `lesson.src_unreadable` precedent (`STATE.md`: "echoes the bank-author-written basename, never a resolved absolute path"), which is exactly the same class of information-disclosure concern `16B-RESEARCH.md`'s Known Threat Patterns table names for this phase's own new path-bearing copy.

**What would overturn it.** Not applicable, this restates an existing shipped precedent.

## Locked by plan 16B-01

## D-16B-1. The new route patterns and their position in ROUTES

Recorded 2026-08-28. Locked by plan `16B-01`, transcribed verbatim from its objective decision table.

**Open question.** What exactly are the new route patterns, and where do they sit in the load-bearing `ROUTES` order

**Locked answer.** `("GET", "/activity", "handle_activity_get")` is a fixed literal inserted immediately after `("GET", "/disclosure", "handle_disclosure")` and before `("POST", "/api/theme", ...)`, so it lands inside the fixed-literal block. Four new stem-parameterised entries are appended to the trailing regex block in this order: `("GET", COURSE_GET_RE, "handle_course_get")`, `("GET", COURSE_AREA_RE, "handle_course_area_get")`, `("GET", COURSE_LESSON_RE, "handle_course_lesson_get")`, `("GET", HELP_GET_RE, "handle_help_get")`. The four regexes are exactly: `COURSE_GET_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})$")`, `COURSE_AREA_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/(?P<area>learn|practice|test|map|sources|build|evidence)$")`, `COURSE_LESSON_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/learn/(?P<lesson_id>[A-Za-z0-9_.-]{1,64})$")`, `HELP_GET_RE = re.compile(r"^/help/(?P<code>[a-z0-9_.]{1,64})$")`.

**Rationale.** `surfaces/daemon.py:238-244`, quoted: "Order is load-bearing: every fixed literal route comes before every stem-parameterised route". The bounded character classes are also the path-traversal mitigation: an opaque ID that cannot contain `/`, `\`, `%`, or `.` runs of arbitrary length cannot address a file outside its record.

## D-16B-3. CLI twin names for every new route

Recorded 2026-08-28. Locked by plan `16B-01`, transcribed verbatim from its objective decision table.

**Open question.** Which CLI command is each new route's twin

**Locked answer.** `/activity` maps to a new CLI command `activity`. `/help/<code>` maps to a new CLI command `help-code`. `/course/<id>` and all three course-level patterns map to the existing `"daemon"` command, exactly as `("GET", "/")` and the asset routes already do. `POST /api/shelf` maps to a new CLI command `shelf`.

**Rationale.** `tests/daemon_roundtrip.py`'s `check_route_cli_inventory` asserts `set(ROUTE_CLI) == set(e[:2] for e in ROUTES)` and that every value has an `add_parser` registration in `surfaces/cli.py`, so a twin is not optional. `activity`, `help-code`, and `shelf` are genuine runtime capabilities an agent client needs. Course pages are browser renderings of records the `daemon` command already serves, and `course.py` does not exist, so a `course` verb would be a command with nothing behind it; it is named out of scope in plan 16B-05 instead of invented.

## D-16B-4. The four new settings keys and the required array

Recorded 2026-08-28. Locked by plan `16B-01`, transcribed verbatim from its objective decision table.

**Open question.** How many new settings top-level keys, what are they called, and do they join `required`

**Locked answer.** Exactly four new top-level keys: `approved_roots` (array of strings, default `[]`), `network_egress` (object), `accessibility` (object), `storage` (object). Backups are properties **inside** `storage`, not a fifth top-level key. None of the four is added to the schema's top-level `required` array, matching the shipped `update` and `audio` keys which sit in `properties` and not in `required`.

**Rationale.** `16B-UI-SPEC.md`'s Settings Expansion Contract table names exactly these four groups plus the two unchanged existing ones and puts backups inside `storage` ("Storage & backups"). Leaving `required` untouched is what makes a pre-16B `itembank.json` validate byte-for-byte as it does today, which is non-negotiable number 4 proven rather than promised.

## D-16B-5. Where first-run and shelf state live on disk

Recorded 2026-08-28. Locked by plan `16B-01`, transcribed verbatim from its objective decision table.

**Open question.** Where does first-run and shelf state live on disk

**Locked answer.** One JSON file per record under a daemon-root directory `_ia/`: `_ia/walkthrough.json` and `_ia/sample_course.json`. Both are written through one helper that writes to `<path>.tmp` and then calls `os.replace`, the identical atomic-rename shape `runtime.write_session` uses. Neither is a settings key and neither is evidence.

**Rationale.** Walkthrough position and sample-course removal are per-install app state, not learner preferences and not evidence. Putting them in `itembank.json` would mix app state into a published settings contract; putting them in the evidence store would create a second writer over it.

## D-16B-6. Where the sample course's bytes live and how guard stays green

Recorded 2026-08-28. Locked by plan `16B-01`, transcribed verbatim from its objective decision table.

**Open question.** Where do the sample course's bundled bytes live, and how is `itembank guard` kept green

**Locked answer.** A new root-level module `sample_course.py` holds the course as literal Python string constants and exposes `write_sample_course(dest_dir)`. First launch materialises it into `<root>/_sample_course/`. `_sample_course/` is added to `.gitignore` and to `cmd_guard`'s skipped-directory list in `surfaces/cli.py`, beside the existing `fixtures` and `_tmp*` entries.

**Rationale.** Guard exists to stop a real bank being **committed**; a gitignored, runtime-materialised directory cannot be committed, so skipping it removes no protection. Shipping the bytes in a `.py` module rather than a committed `.md` keeps guard's markdown walk untouched, and a module import resolves in a checkout and inside a `.pyz` alike without needing `resources.py`.

## D-16B-7. The one new mutating route and its allowed fields

Recorded 2026-08-28. Locked by plan `16B-01`, transcribed verbatim from its objective decision table.

**Open question.** What is the one new mutating route, and what may its body carry

**Locked answer.** Exactly one: `("POST", "/api/shelf", "handle_api_shelf")`, appended to `API_ROUTES` as its thirteenth member. `SHELF_ALLOWED_FIELDS = ("action",)` and `SHELF_ACTIONS = ("remove_sample_course", "skip_walkthrough", "replay_walkthrough", "advance_walkthrough")`. Any other body field is refused with 400 before any helper runs, and the route runs `_reject_cross_origin_write` first. `check_api_route_scope`'s literal `12` becomes `13`, and `SURFACE_PARITY` gains the row `(("POST", "/api/shelf"), "shelf", "shelf")`.

**Rationale.** `surfaces/daemon.py:204-208`'s `SEED_ACCEPT_ALLOWED_FIELDS` is the shipped fixed-allowed-fields precedent, and Extensibility Rule 9(a) requires every `/api/*` route to reserve its MCP tool name in the same commit. One route for four small actions keeps the parity tables from growing four rows for one capability.

## D-16B-8. No Activity write path exists in 16B

Recorded 2026-08-28. Locked by plan `16B-01`, transcribed verbatim from its objective decision table.

**Open question.** What does the Activity view do about a needs-input job while `journal.py` is absent

**Locked answer.** Nothing that writes. 16B renders needs-input jobs read-only and renders no resolve control at all while `journal.py` is absent. A resolve route, a resolve action, and any journal write are explicitly out of scope for the whole phase and are named as such in plan 16B-02's `<out_of_scope>`.

**Rationale.** `16B-RESEARCH.md` Pitfall 2: "Every state-changing Activity action must call into `journal.py`'s own commit/undo functions". A resolve control with no journal behind it can only be a second write path, which is exactly what the pitfall names.

## D-16B-9. Deterministic degraded-banner precedence

Recorded 2026-08-28. Locked by plan `16B-01`, transcribed verbatim from its objective decision table.

**Open question.** What is the deterministic order when several degraded banners fire at once

**Locked answer.** The order of `ia.DEGRADED_STATES`, which is the literal tuple `("crash", "cancelled", "disk_full", "offline", "permission_denied", "future_schema", "agent_unavailable", "course_corrupted")`. The first member present wins the banner slot; every other fired state is still reachable through its own `/help/<code>` link listed below the banner.

**Rationale.** The APP-03 ordering probe row asks for a deterministic precedence and a one-to-one banner-to-help-page routing. A declared tuple gives both, and it is the same closed-vocabulary shape `model.GATE_VALUES` already uses.

## Assumption-delta disposition

Recorded 2026-08-28. Advisory and non-blocking.

The deterministic assumption-delta detector fired on the phase text "no loop
introduces a second parser or scorer" with kind `pluralization` and term
`second`. The noun is `parser/scorer authority`. The decision is `no-change`.
The rationale is that the detected term appears inside a prohibition that
preserves the single-authority invariant rather than introducing a second case,
and no identity model changes this phase.

## APP-02 probe enumeration

Recorded 2026-08-28.

The spec-less edge-coverage probe returned APP-02's row as `unclassified` and
unresolved. The planner enumerated it as three named scenarios rather than
dropping it:

(a) deep-link stability under object rename or move
(b) an anchor into deleted content
(c) focus restoration when the original target no longer exists

All three are carried as acceptance criteria in plan `16B-05`. None was dropped.

## API coverage note

Recorded 2026-08-28.

The api-coverage detector returned `detected: false` over this phase's scope, so
no `COVERAGE.md` matrix is owed. Model backends appear in the Settings surface
as configuration display only.

## D-16B-2. Where the IA read models and the new CLI handlers live

Recorded 2026-08-28. Answered by Weibao at the `16B-01` Task 2
`checkpoint:decision`, gate `blocking`, reversibility `one-way`.

**Chosen option.** `option-a`.

**Answer, verbatim.**

```
option-a (Recommended)

surfaces/ia.py     <- vocabularies, read models, cmd_activity / cmd_help_code / cmd_shelf
surfaces/daemon.py <- 6 route entries + 6 handlers, each calling one ia.* function

Matches surfaces/settings.py's shipped shape (pure logic + cmd_* in one module).
Bans hold by construction: ia.py never imports runtime, imports model only for
lesson_slug, and its only open() calls are the two _ia/*.json state helpers.
```

**Consequences, one sentence each.**

- The exact path of every new module this decision creates is `surfaces/ia.py`,
  and it is the only new module the decision creates.
- `activity_view_state` lives in `surfaces/ia.py`.
- `help_entry` lives in `surfaces/ia.py`.
- `cmd_activity` lives in `surfaces/ia.py`, beside `cmd_help_code` and
  `cmd_shelf`, wired into `surfaces/cli.py` by `set_defaults(fn=...)` like every
  other command.
- `surfaces/daemon.py` may not contain any 16B copy string: every user-visible
  16B string lives in a copy table in `surfaces/ia.py`, and each of the six new
  daemon handlers calls one `ia.*` function and renders its result.

**Plan edits this answer forces.** None. Plans `16B-02` through `16B-11` are
already written against `surfaces/ia.py`, so the module path in every
`files_modified`, `<files>`, `<read_first>`, structural ban assertion, and
acceptance criterion stands unchanged, and the executor proceeds as written.

## D-16B-10. Course-shelf ordering

Recorded 2026-08-28. Locked by plan `16B-04`.

**Locked answer.** The shelf sorts by a total order with three keys, in this
priority: first the index of the card's attention state in `ATTENTION_ORDER`,
which is the literal tuple `("needs_input", "needs_reconciliation",
"pending_review", "due", "last_valid_overview", "up_to_date")`; then the card's
most recent recorded activity timestamp, descending, with a missing timestamp
sorting last; then the course ID, ascending, as the final tiebreak.

**Rationale.** The APP-01 ordering edge requires determinism among equal
attention states and the course ID is the only field guaranteed unique and
stable, and `ATTENTION_ORDER` puts the states that need a human first without
ever synthesizing a score.

## D-16B-11. The subphase marker on new settings keys

Recorded 2026-08-28. Locked by plan `16B-06`.

**Locked answer.** Every new top-level key added by this phase carries
`"x-itembank-phase": 16.2`, and `settings.THIS_PHASE` stays at `10`, unchanged.

**Rationale.** The shipped comment above `THIS_PHASE` describes the float
precisely: "a sub-phase (2.1) can sit strictly between its parent (2) and the
next whole phase (3) without renumbering anything". Phase 16A is 16.1, 16B is
16.2, 16C is 16.3. A key marked 16.2 while `THIS_PHASE` is 10 reports as
declared rather than as read, which is the honest state of a key nothing gates
on yet.

## D-16B-12. What 16B ships of the mode-layer contract and what 16C ships

Recorded 2026-08-28. Locked by plan `16B-07`.

**Locked answer.** Phase 16B ships `ia.MODE_LAYER_ROWS`, the read-only
rendering of all seven layers in the settings page with the two fixed layers
under the heading `Always fixed by itembank`, and the pure
`ia.mode_layer_resolve` over an explicitly supplied mapping. Phase 16C ships the
collector that populates that mapping from live strategy, accommodation, and
instructor records under `STRATEGY-02`. The conflict fixture's shape is shared
rather than duplicated: 16C appends rows to `CONFLICT_CASES` in
`tests/mode_layer_roundtrip.py` rather than writing a second fixture.

**Rationale.** D8 puts the composed resolver in 16C. Duplicating the precedence
logic in 16B would create two implementations of one contract, so 16B ships the
rule and 16C ships the state that feeds it.

## Recorded discrepancy: the mode-layer conflict sentence

Recorded 2026-08-28 by plan `16B-07`.

`16B-UI-SPEC.md` states the conflict sentence twice and the two statements
differ. Its Mode-Layer Precedence Contract point 2 gives the template as
"{Setting name} is set by {higher layer name} for this course and can't be
changed here." and then illustrates it with "Timed test mode is set by your
instructor's policy and can't be changed here.", which drops "for this course".
Its Copywriting Contract row repeats the template with "for this course".

The template is taken as binding, because the Copywriting Contract is named in
`16B-01-PLAN.md` as "the binding source for every user-visible string in this
phase" and it agrees with point 2's own template. The inline example is treated
as an illustration that lost a phrase. The shipped sentence is therefore:

`Timed test mode is set by your instructor's policy for this course and can't be changed here.`

Plan `16B-07`'s acceptance criterion quotes the shorter example form and is
inconsistent with the template the same plan tells this task to implement.

## D-16B-13. Freeze scope

Recorded 2026-08-28. Locked by plan `16B-11`.

**What the 16B freeze covers.** The six new route patterns and their `ROUTE_CLI`
twins and one `SURFACE_PARITY` row; the three new CLI commands `activity`,
`help-code`, and `shelf`; the course-shelf branch inside `handle_index`, with
the literal `("GET", "/")` route and its `daemon` twin unchanged; the four new
settings top-level keys with their restrictive defaults and their
`x-itembank-phase` 16.2 marker, with the schema's `required` array unchanged;
the eleven closed vocabularies on `surfaces/ia.py`; every locked copy constant
named in the freeze record; the two `_ia/*.json` state files and their atomic
write contract; the bundled sample course's identifier, name, and directory
name; and `16B-UI-SPEC.md` itself as a document-level contract for its
typography voice table, its color token-assignment table, its Copywriting
Contract, its Degraded-State Matrix, its Activity Contract, its Core Loop Resume
Contract, its Mode-Layer Precedence Contract, its route contract, and its
Decisions log D1 through D9.

**What it explicitly does not cover.** It is not a visual system or token freeze,
which is Phase 17A's; not a notes, learner-artifact, or strategy freeze, which is
Phase 16C's; not a course schema freeze, which is Phase 14B's; and not a semantic
lesson capability freeze, which is Phase 16A's. The six rows of
`16B-UI-SPEC.md`'s "Open Items Deferred to Other Phases" table are carried
verbatim into `16B-FREEZE.md` and remain deferred.

**Rationale.** The ROADMAP's prototype-before-freeze coupling clause states this
boundary directly, and stating it in both the freeze record and the decisions
file means a later phase reading only one of the two gets the same answer.
