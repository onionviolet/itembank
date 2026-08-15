---
phase: 16B-ia-modes-recovery-contract
plan: 02
type: execute
wave: 2
depends_on: ["16B-01"]
files_modified:
  - surfaces/ia.py
  - surfaces/daemon.py
  - surfaces/cli.py
  - tests/ia_route_roundtrip.py
  - tests/daemon_roundtrip.py
autonomous: true
requirements: [APP-02, APP-03]
estimate:
  tokens: 78000
  raw_tokens: 78000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "One request proves the whole 16B stack end to end before any expansion task runs: a real daemon started on a real port answers GET /activity with HTTP 200, the response body was produced by surfaces/ia.py's read model rather than by a string inside the route handler, and the assertion is made on bytes that crossed a socket rather than on an in-memory render."
    - "GET /activity is one new row in the four shipped parallel structures and in nothing else: ROUTES gains one fixed-literal entry positioned inside the fixed-literal block, ROUTE_CLI gains its twin, and tests/daemon_roundtrip.py's existing check_route_cli_inventory passes unchanged because the route was not added to a second dispatch mechanism."
    - "The Activity view is a read model with no write path: surfaces/ia.py contains no call that appends to, truncates, or replaces any journal file, and the only state-changing action reachable from the Activity route in this phase is none at all."
    - "The not-yet-available state is proven rather than described: activity_view_state(root, journal=None) returns available False, the code ia.activity_unavailable, and the exact notice 'Activity isn't available yet in this build. Check back after your next update.', and a route driven with the journal forced absent serves that sentence."
    - "Zero jobs is the ordinary happy path and renders no empty-state banner; a missing journal file states that jobs are unavailable rather than raising or erroring (ActivityView empty consideration)."
    - "An unreadable or malformed journal entry renders as a Failed row carrying the journal's own recorded refusal text, never a crash and never a generic something-went-wrong string (ActivityView error consideration)."
    - "Every one of the eight ACTIVITY_JOB_STATES renders its exact locked copy, and the in-progress-without-a-denominator state renders the literal sentence 'In progress: no estimate.' and no percent character (ActivityView populated consideration, Decision D7)."
    - "A cancelled job renders the exact sentence 'Cancelled. Partial results are marked below and were not saved as final.' beside its partial results (ActivityView partial consideration)."
    - "Zero jobs renders no 'Needs your input' section header at all, and one job renders through the identical card structure many jobs render through, with no singular-copy special case (ActivityView zero-one-many consideration)."
    - "Journal-recorded intent text is emitted so it wraps rather than being truncated, and the one field most likely to be long, a filesystem path, is bounded by the basename-only rule so no resolved absolute path ever reaches the page (ActivityView long-text consideration, Decision D9)."
    - "Long jobs never invent a percent when the denominator is unknown; 'In progress: no estimate' is the only permitted copy in that state, and a real journal-recorded step count renders as 'Step {n} of {N}: {stage name}' instead (APP-03 precision edge)."
    - statement: "A genuinely slow Activity read renders a stated loading state rather than a blank region; today the read is synchronous and server-rendered, so no loading state is reachable, and asserting that by construction needs a held-out timing test rather than a claim."
      verification: backstop
    - statement: "A long job list scrolls rather than clipping or paginating; the exact scroll container is a Phase 17A rendering decision, confirmed by a held-out visual test at 17A rather than asserted here."
      verification: backstop
  prohibitions:
    - statement: "The Activity view must not become a second write authority over the journal: no route handler and no ia.py function may open a journal file for append, decide whether an operation applied, retry an operation, or write to the disposable objects projection."
      status: kept
      verification: flagged-unverified
    - statement: "A second router or dispatch mechanism must not appear beside DaemonHandler._dispatch; a new route is a new tuple entry in the shipped structures, never a parallel if-chain, a mounted sub-application, or a separate framework."
      status: kept
      verification: flagged-unverified
    - statement: "A percent-complete number must not appear anywhere in this surface, including when a denominator happens to be computable, because a ratio synthesized across heterogeneous steps is an invented figure presented as a measurement."
      status: kept
      verification: flagged-unverified
    - statement: "The Activity IA area must not be conflated with the ACTIVITY-01/02/03 learner-question family; they share a word and not a schema, and a route, fixture, or test named without that distinction misleads the next reader."
      status: kept
      verification: flagged-unverified
    - statement: "Chat must not become the home surface or the sole record of a durable job; the durable record is the journal and the Activity view reads it, so a job that exists only inside a conversation is a job that was never recorded."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "surfaces/ia.py with IA_HELP_CODES, ACTIVITY_JOB_STATES, DEGRADED_STATES, ATTENTION_STATES, MODE_LAYERS, MODE_LAYERS_FIXED, COURSE_AREAS, and activity_view_state"
    - "surfaces/daemon.py with the ('GET', '/activity', 'handle_activity_get') route entry, its ROUTE_CLI twin, and handle_activity_get"
    - "surfaces/cli.py with add_parser('activity') and set_defaults(fn=cmd_activity)"
    - "tests/ia_route_roundtrip.py with check_activity_route_end_to_end, check_activity_unavailable_state, check_activity_job_states, and check_activity_no_write_path"
  key_links:
    - "The tracer's assertion must be made on bytes returned over HTTP by a real subprocess daemon, not on the return value of an in-process call to handle_activity_get. An in-process assertion would prove the renderer and leave the route registration, the dispatch order, and the token gate untested, which is exactly the trio a tracer exists to prove."
    - "GET /activity must be inserted inside the fixed-literal block of ROUTES, before the + API_ROUTES + concatenation. Appending it after the trailing regex block would leave it shadowed by no route today and shadowed by a stem-parameterised route the moment one matches /activity, which is the failure the shipped ordering comment at surfaces/daemon.py:238-244 exists to prevent."
    - "check_route_cli_inventory asserts set(ROUTE_CLI) == set(e[:2] for e in ROUTES) and that every ROUTE_CLI value has an add_parser registration in surfaces/cli.py. Adding the route without both halves fails the shipped suite rather than shipping silently, so the CLI command and the route land in the same task."
    - "activity_view_state takes journal as an explicit parameter whose None value forces the not-yet-available branch. Without that parameter the degraded state is unreachable in a tree where the 16B-01 precondition already proved journal.py present, and the phase would ship a state it never executed."
---

<objective>
Prove the whole 16B stack with one request before building anything on it.

This is the phase's tracer. `TRACER_MODE` is on and the rule is that the first
task wires one path through every layer 16B touches, end to end, with a real
runnable check, so an architectural dead end is found after one commit rather
than after ten. The path chosen is `GET /activity`, because it is the only new
16B route whose full content is already decided: `16B-UI-SPEC.md` Decision D2
settles that the route is registered now, and its Activity Contract table
settles every state and every string it can render. Nothing about this task is a
prototype: the module, the route, the handler, the CLI twin, and the test are
the ones the phase ships.

The path touches, in one commit: the new module (`surfaces/ia.py`), the shipped
route table's four parallel structures, the shipped dispatcher, the shipped
presentation shell, the CLI parity inventory, and a new direct-execution test
that starts a real daemon subprocess and asserts on bytes that crossed a socket.

Decisions already made, cited, and never re-derived here:

- **`16B-DECISIONS.md` `## D2`**: `GET /activity` is registered in `ROUTES` now,
  rendering a not-yet-available state until `journal.py` lands, rather than
  being withheld from the route table entirely, because APP-02 requires stable
  deep links and registering now means the route's identity never changes when
  14A lands, only its rendered content does.
- **`16B-DECISIONS.md` `## D6`**: the Activity IA area (durable agent and
  maintenance jobs) is a different object from `REQUIREMENTS.md`'s
  `ACTIVITY-01/02/03` learner-question family. Every fixture, route, and test
  this plan adds carries a doc comment saying so.
- **`16B-DECISIONS.md` `## D7`**: no percent-complete number appears under any
  circumstance, including for a job with a real recorded step count, which
  instead reads `Step {n} of {N}: {stage name}`.
- **`16B-DECISIONS.md` `## D8`**: no Activity write path exists in 16B. No
  resolve route, no resolve control, no journal write.
- **`16B-DECISIONS.md` `## D9`**: path-bearing copy shows the bank-author-written
  basename only, never a resolved absolute path.
- **`16B-DECISIONS.md` `## D-16B-1`**: the exact route position and the four
  regex constants.
- **`16B-DECISIONS.md` `## D-16B-2`**: the module path. This plan is written for
  `option-a` (`surfaces/ia.py`); if Task 2 of plan 16B-01 recorded `option-b` or
  `option-c`, apply the consequence list that answer carries before starting.
- **`16B-DECISIONS.md` `## D-16B-3`**: `/activity` maps to a new CLI command
  named `activity`.
- **`16B-UI-SPEC.md` Activity Contract**, the full States and copy table and the
  Journal metadata boundary clause, both binding verbatim.
- **`16B-RESEARCH.md` Pattern 2 and Pattern 3**, and the Anti-Patterns list.

Purpose: prove the architecture end to end on this phase's best early-context
tokens.
Output: one new module, one new route, one new CLI command, and one new test
file that drives a real daemon.
</objective>

<context>
@.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-PATTERNS.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
@surfaces/daemon.py
@surfaces/presentation.py
@surfaces/cli.py
@tests/daemon_roundtrip.py
@.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md
</context>

## Artifacts this phase produces (plan 16B-02 share)

New symbols introduced by this plan, and by nothing earlier:

- `surfaces/ia.py` (whole module) and on it: `IA_HELP_CODES`,
  `ACTIVITY_JOB_STATES`, `DEGRADED_STATES`, `ATTENTION_STATES`, `MODE_LAYERS`,
  `MODE_LAYERS_FIXED`, `COURSE_AREAS`, `ACTIVITY_COPY`, `activity_view_state`,
  `cmd_activity`.
- `surfaces/daemon.py`: the route entry `("GET", "/activity",
  "handle_activity_get")`, the `ROUTE_CLI` entry `("GET", "/activity"):
  "activity"`, and the handler `handle_activity_get`.
- `surfaces/cli.py`: `add_parser("activity")` with `set_defaults(fn=cmd_activity)`.
- `tests/ia_route_roundtrip.py` (whole file) and on it:
  `check_activity_route_end_to_end`, `check_activity_unavailable_state`,
  `check_activity_job_states`, `check_activity_no_write_path`, and `main`.

No schema key, no fixture, and no settings default is produced by this plan. The
phase-wide symbol union is repeated in `16B-01-PLAN.md`.

<tasks>

<task type="tracer">
  <name>Task 1: end-to-end GET /activity, one path only</name>
  <files>surfaces/ia.py, surfaces/daemon.py, surfaces/cli.py, tests/ia_route_roundtrip.py</files>
  <read_first>
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md` in full,
  every heading. This task implements D2, D6, D7, D8, D-16B-1, D-16B-2, and
  D-16B-3 and re-derives none of them.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the section
  "Activity (Durable Jobs) Contract" in full, including the naming warning, the
  Data source paragraph, the States and copy table, and the Journal metadata
  boundary clause. Every string this task emits comes from that table.
- `surfaces/daemon.py` lines 210 to 335 in full: `API_ROUTES`, the load-bearing
  ordering comment at 238 to 244, `ROUTES`, `ROUTE_CLI`, `SURFACE_PARITY`.
- `surfaces/daemon.py` lines 939 to 968, `handle_index`, as the shape a new page
  handler follows: read settings, build a body, call the shared shell, send.
- `surfaces/daemon.py` lines 3310 to 3330, `DaemonHandler._dispatch`, so the
  first-match-wins walk and the token gate are understood before a route is
  inserted.
- `surfaces/presentation.py` lines 281 to 342, `surface_shell`, `context_line`,
  and `state_panel`, the three helpers this handler renders through.
- `surfaces/settings.py` lines 1 to 60, as the shipped example of a surface
  module holding both pure logic and a `cmd_*` handler.
- `surfaces/cli.py` lines 20 to 40 (the `from surfaces import ...` block) and
  lines 1027 to 1050 (`add_parser("schema")` through `add_parser("config")`), the
  exact registration shape a new subcommand copies.
- `tests/daemon_roundtrip.py` lines 1 to 40 and the definitions of
  `start_daemon`, `get`, and `json_request`, which this new test file imports
  rather than reimplements.
- `.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md` lines 104 to
  140, `journal.py`'s public surface, for the exact names `entries`, `replay`,
  `object_state`, `undo`, `OBJECT_STATES`, and `ENTRY_STATES`.
  </read_first>
  <action>
1. Create `surfaces/ia.py` with a module docstring that states, in prose: that
   this module holds the information-architecture read models for Phase 16B;
   that it reads durable records and never writes one, so it never imports
   `runtime`, never calls a scorer, and never opens a journal file for writing;
   that it imports `model` for exactly one name, `lesson_slug`, added by plan
   16B-05, because the anchor scheme must be the shipped one and a second slug
   implementation would be a second anchor vocabulary; and, in its
   own paragraph, the D6 naming distinction verbatim in substance: the Activity
   area named here means durable agent and maintenance jobs, and it is a
   different object from `REQUIREMENTS.md`'s `ACTIVITY-01/02/03` family of
   purpose-first learner questions, which share a word and not a schema.

   Then define these module-level constants, each a plain tuple in
   `model.GATE_VALUES`'s shape, with a one-line comment above each:

   - `IA_HELP_CODES = tuple(sorted({...}))` over exactly these twelve strings:
     `ia.activity_unavailable`, `ia.agent_unavailable`, `ia.cancelled`,
     `ia.course_corrupted`, `ia.crash_recovered`, `ia.disk_full`,
     `ia.future_schema`, `ia.offline`, `ia.permission_denied`,
     `ia.route_not_found`, `ia.sample_course_removed`,
     `ia.walkthrough_unavailable`.
   - `ACTIVITY_JOB_STATES = ("needs_input", "in_progress_no_estimate",
     "in_progress_known", "completed", "failed", "cancelled", "interrupted",
     "unavailable")`.
   - `DEGRADED_STATES = ("crash", "cancelled", "disk_full", "offline",
     "permission_denied", "future_schema", "agent_unavailable",
     "course_corrupted")`, with a comment stating that tuple order is the
     deterministic banner precedence locked by D-16B-9.
   - `ATTENTION_STATES = ("up_to_date", "due", "pending_review", "needs_input",
     "needs_reconciliation", "last_valid_overview")`.
   - `MODE_LAYERS = ("learner_preference", "author_strategy",
     "objective_constraint", "accommodation_override", "instructor_policy",
     "runtime_authority", "system_safety")`, ordered lowest authority first.
   - `MODE_LAYERS_FIXED = ("runtime_authority", "system_safety")`.
   - `COURSE_AREAS = ("overview", "learn", "practice", "test", "map", "sources",
     "build", "evidence")`, with a comment stating that Notes is deliberately
     absent per D4.

   Then define `ACTIVITY_COPY`, a dict mapping each member of
   `ACTIVITY_JOB_STATES` to its exact locked label from the UI-SPEC Activity
   Contract table:

   - `"needs_input"` maps to `"Needs your input"`
   - `"in_progress_no_estimate"` maps to `"In progress: no estimate."`
   - `"in_progress_known"` maps to `"Step {n} of {N}: {stage}"`
   - `"completed"` maps to `"Completed"`
   - `"failed"` maps to `"Failed: {reason}"`
   - `"cancelled"` maps to `"Cancelled. Partial results are marked below and were not saved as final."`
   - `"interrupted"` maps to `"Interrupted: resume available."`
   - `"unavailable"` maps to `"Activity isn't available yet in this build. Check back after your next update."`

   Add a second dict `ACTIVITY_TOKENS` mapping each state to the existing
   semantic token name the UI-SPEC assigned it, as a bare name with no leading
   dashes and no color value: `needs_input` to `pending`, both in-progress
   states to `pending`, `completed` to `ok`, `failed` to `bad`, `cancelled` to
   `warn`, `interrupted` to `warn`, `unavailable` to `unknown`. Add a comment
   stating that these are existing token names assigned by `16B-UI-SPEC.md` and
   that no new token, color, or spacing value is introduced by this phase.

2. In the same module, define one sentinel and one function.

   `_UNSET = object()` at module level, private.

   `def activity_view_state(root, journal=_UNSET):` with a docstring stating:
   that it returns the Activity view's whole state as a plain dict and performs
   no write; that passing `journal=None` forces the not-yet-available branch,
   which is how a build without `journal.py` behaves and how that state is
   exercised in a tree where `journal.py` is present; and that omitting the
   argument imports `journal` and falls back to the same branch on
   `ImportError`.

   Its behavior, exactly:

   - Resolve the module: when `journal is _UNSET`, `try: import journal as
     _j / except ImportError: _j = None`; otherwise `_j = journal`.
   - When `_j is None`, return
     `{"available": False, "code": "ia.activity_unavailable",
       "notice": ACTIVITY_COPY["unavailable"], "needs_input": [], "jobs": []}`
     and nothing else. Do not raise.
   - Otherwise iterate `_j.entries(root)` once. Build `resolved` as the set of
     `entry["resolves_entry"]` for every entry whose `state` is `"applied"` or
     `"refused"` and whose `resolves_entry` is truthy. Collect `prepared` as
     every entry whose `state` is `"prepared"`.
   - For each prepared entry not in `resolved`, call
     `_j.object_state(root, entry["object_id"])` and map its result to a display
     state: `"interrupted"` maps to `"interrupted"`, `"conflict"` maps to
     `"needs_input"`, and everything else maps to `"needs_input"` when the entry
     carries no `step` field, to `"in_progress_known"` when it carries both
     `step` and `steps_total` as positive integers, and to
     `"in_progress_no_estimate"` when it carries `step` without a positive
     `steps_total`.
   - For each resolved entry, the display state is `"completed"` when the
     resolving entry's `state` is `"applied"`, `"failed"` when it is
     `"refused"`, and `"cancelled"` when the resolving entry carries
     `"cancelled": True`.
   - Each job is a dict with exactly these keys and no others: `entry_id`,
     `object_kind`, `state`, `label`, `token`, `intent`, `timestamp`,
     `help_code`. `label` is `ACTIVITY_COPY[state]` with `{n}`, `{N}`,
     `{stage}`, and `{reason}` substituted from the entry's own recorded fields;
     `token` is `ACTIVITY_TOKENS[state]`; `intent` is the entry's own recorded
     intent text passed through `os.path.basename` for any value that contains a
     path separator, per D9; `help_code` is `"ia.agent_unavailable"` for a failed
     job and `None` otherwise.
   - An entry that is not a dict, or that is missing `entry_id` or `state`,
     becomes one job with state `"failed"`, `label` built from
     `ACTIVITY_COPY["failed"]` with `{reason}` replaced by the literal string
     `unreadable journal entry`, and is never allowed to raise past this
     function.
   - Return `{"available": True, "code": None, "notice": "",
     "needs_input": [jobs whose state is "needs_input"],
     "jobs": [every job, newest timestamp first, ties broken by entry_id
     ascending]}`.

   Every key of every returned job is metadata. Never copy `before_image`, a
   raw content field, or any byte payload out of a journal entry into the
   returned dict; the UI-SPEC's Journal metadata boundary clause is the reason
   and the docstring says so.

3. Add `def cmd_activity(a):` to the same module. It calls
   `activity_view_state(a.dir)` and prints
   `json.dumps(state, ensure_ascii=False, indent=2)`, matching the shipped
   `print(json.dumps(result, ensure_ascii=False, indent=2))` convention. It
   performs no write and takes no action argument.

4. Register the route in `surfaces/daemon.py`. Insert exactly one line into the
   fixed-literal block of `ROUTES`, immediately after
   `("GET", "/disclosure", "handle_disclosure"),` and before
   `("POST", "/api/theme", "handle_theme_post"),`:

```
    ("GET", "/activity", "handle_activity_get"),
```

   Then add exactly one entry to `ROUTE_CLI`, beside the other fixed-literal
   entries:

```
    ("GET", "/activity"): "activity",
```

   Add no entry to `API_ROUTES` and no row to `SURFACE_PARITY` in this task;
   `/activity` is a `GET` page route, not an `/api/*` route.

5. Add `handle_activity_get(handler)` to `surfaces/daemon.py`, placed
   immediately after `handle_disclosure`. Its docstring states that it renders
   the Activity view, that it is a read model over the journal and writes
   nothing, and that the D6 naming distinction applies. Its body, exactly:

   - `state = ia.activity_view_state(handler.root)`
   - When `state["available"]` is false, body is
     `presentation.state_panel({"kind": "unknown", "status": state["notice"]})`
     plus one anchor to `/help/ia.activity_unavailable` labelled
     `Read more about this`.
   - Otherwise body is: a `Needs your input` section rendered **only when
     `state["needs_input"]` is non-empty**, whose heading text is exactly
     `Needs your input`; then every job in `state["jobs"]` rendered as one
     `<article class="job" data-ia-state="{state}" data-ia-token="{token}">`
     carrying an `<h3>` with the job's `label` and a `<p>` with its `intent`,
     both HTML-escaped through `presentation.esc`.
   - Send with
     `handler.send_html(presentation.surface_shell("Activity", body,
     theme_css=theme.theme_css(settings.load_settings(handler.root)),
     back={"href": "/", "label": "Back to courses"}).encode("utf-8"))`.

   Add `from surfaces import ia` to `surfaces/daemon.py`'s existing import
   block if it is not already present.

6. Register the CLI twin in `surfaces/cli.py`. Add `cmd_activity` to the
   `from surfaces...` import block, then add a subparser beside the existing
   `add_parser("config")` registration:

```
    s = sub.add_parser("activity", help="list durable agent and maintenance "
                       "jobs (the Activity view's CLI twin)")
    s.add_argument("dir", nargs="?", default=".")
    s.set_defaults(fn=cmd_activity)
```

7. Create `tests/ia_route_roundtrip.py`. Its module docstring states what the
   file proves and carries the D6 naming distinction. It follows the shipped
   direct-execution convention exactly: `#!/usr/bin/env python3`, standard
   library only, `ROOT` computed from `__file__`, `sys.path.insert(0, ROOT)`,
   `import itembank`, then `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`
   and `from daemon_roundtrip import start_daemon, get, json_request`, then its
   own local `fail(msg)` that prints `"FAIL: " + msg` and exits 1.

   Write exactly one check in this task, `check_activity_route_end_to_end()`:

   - Make a temp dir, copy `fixtures/sample_bank.md` into it, and start a real
     daemon with `start_daemon(workdir)`.
   - `status, body = get(url + "activity")`.
   - Assert `status == 200`, or fail with
     `"GET /activity returned %d, expected 200" % status`.
   - Assert the string `<h1>Activity</h1>` is in `body`.
   - Assert the string `Back to courses` is in `body`.
   - Assert no percent sign appears in any `data-ia-state` article in `body`;
     implement as: every substring between `data-ia-state="` and the next `"`
     is a member of `ia.ACTIVITY_JOB_STATES`, and `"%"` does not appear inside
     any `<h3>` in `body`.
   - Terminate the daemon in a `finally`.

   Add `main()` that runs the single check, prints
   `"IA ROUTES: 1 passed, 0 failed"`, and returns 0, guarded by
   `if __name__ == "__main__": sys.exit(main())`.

8. Run, in this order, and record each command's final line:

```
python tests/ia_route_roundtrip.py
python tests/daemon_roundtrip.py
python -c "import sys; sys.path.insert(0,'.'); from surfaces import ia; print(len(ia.IA_HELP_CODES), len(ia.ACTIVITY_JOB_STATES), len(ia.DEGRADED_STATES), len(ia.MODE_LAYERS), len(ia.COURSE_AREAS))"
```

   Expected: exit 0, exit 0, and the third printing exactly `12 8 8 7 8`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_route_roundtrip.py && python tests/daemon_roundtrip.py</automated>
Expected: `IA ROUTES: 1 passed, 0 failed` and exit 0 from the first, exit 0 from
the second. The degraded state this task must also prove is that the route was
added to the one dispatcher and not to a second one: confirm
`python -c "import sys; sys.path.insert(0,'.'); from surfaces import daemon; print([p for m,p,h in daemon.ROUTES if p=='/activity'], daemon.ROUTE_CLI[('GET','/activity')])"`
prints `['/activity'] activity`.
  </verify>
  <acceptance_criteria>
- `python tests/ia_route_roundtrip.py` exits 0 with final line
  `IA ROUTES: 1 passed, 0 failed`.
- `python tests/daemon_roundtrip.py` exits 0 unchanged, which proves
  `check_route_cli_inventory` still passes with the new route and its twin.
- `surfaces/ia.py` exists; `python -c "import sys; sys.path.insert(0,'.'); from surfaces import ia; print(len(ia.IA_HELP_CODES), len(ia.ACTIVITY_JOB_STATES), len(ia.DEGRADED_STATES), len(ia.MODE_LAYERS), len(ia.COURSE_AREAS))"`
  prints exactly `12 8 8 7 8`.
- `ia.ACTIVITY_COPY["in_progress_no_estimate"]` equals the literal
  `In progress: no estimate.` and `ia.ACTIVITY_COPY["unavailable"]` equals the
  literal `Activity isn't available yet in this build. Check back after your next update.`
- `ia.DEGRADED_STATES[0]` equals `"crash"` and `ia.DEGRADED_STATES[-1]` equals
  `"course_corrupted"`, which is D-16B-9's locked precedence.
- The route sits inside the fixed-literal block: the index of
  `("GET", "/activity", "handle_activity_get")` in `daemon.ROUTES` is strictly
  less than the index of `("POST", "/api/start", "handle_api_start")`. Assert
  with a one-line `python -c`.
- `len(daemon.API_ROUTES)` is still `12` and `len(daemon.SURFACE_PARITY)` is
  still `12`; this task adds no `/api/*` route.
- `python itembank.py activity .` exits 0 and prints a JSON object carrying the
  keys `available`, `code`, `notice`, `needs_input`, and `jobs`.
- Structural no-write ban, asserted mechanically. Run and expect stdout
  `no write path`:

```
python -c "import io,sys,re; s=io.open('surfaces/ia.py',encoding='utf-8').read(); body=re.sub(r'^\s*#.*$','',s,flags=re.M); bad=[t for t in ('\"w\"',\"'w'\",'\"a\"',\"'a'\",'os.remove','shutil.rmtree','journal.commit','journal.undo') if t in body]; sys.exit('write path found: '+', '.join(bad)) if bad else print('no write path')"
```

- No file this task writes contains an em dash character. Verify with the
  `chr(0x2014)` form from plan 16B-01, listing `surfaces/ia.py`,
  `surfaces/daemon.py`, `surfaces/cli.py`, and `tests/ia_route_roundtrip.py`.
  Expected stdout: `no em dash`.
  </acceptance_criteria>
  <precondition>`.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md` exists and its Dated result line states that 16B may proceed, and `16B-DECISIONS.md` carries a recorded `## D-16B-2` answer.</precondition>
  <reversibility rating="costly">The route literal `/activity` and the module
  path become a published surface later phases deep-link to and import. The
  one-way class of both was already settled: the route by the approved
  `16B-UI-SPEC.md` Decision D2, and the module path by the blocking checkpoint
  in plan 16B-01 Task 2, so neither is reopened here.</reversibility>
  <done>A real daemon answers a real HTTP request for `/activity` with a page
  built by `surfaces/ia.py`, the shipped route-parity suite is still green, and
  no write path exists anywhere in the new module.</done>
</task>

<task type="auto">
  <name>Task 2: every Activity job state, the unavailable branch, and the no-invented-percent rule</name>
  <files>surfaces/ia.py, tests/ia_route_roundtrip.py</files>
  <read_first>
- `surfaces/ia.py` as written by Task 1, in full.
- `tests/ia_route_roundtrip.py` as written by Task 1, in full.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the Activity
  Contract States and copy table, and the Color section's
  "New semantic-token assignments" table rows for the four Activity job rows.
- `.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md` lines 104 to
  140, for the exact entry field names a synthetic journal stand-in must
  produce.
- `tests/evidence_roundtrip.py` lines 1 to 40, for the local `fail(msg)` and
  direct-execution shell convention.
  </read_first>
  <action>
1. Add to `tests/ia_route_roundtrip.py` a module-level helper
   `def _fake_journal(entries, object_states):` returning a small object with
   three attributes: `entries(root)` returning the given list,
   `object_state(root, object_id)` returning `object_states.get(object_id,
   "clean")`, and `ENTRY_STATES = ("prepared", "applied", "refused")`. Its
   docstring states that it is an explicit synthetic stand-in for `journal.py`,
   named as a stand-in so no reader mistakes it for the real module, and that
   the real module is exercised by `check_activity_route_end_to_end`.

2. Add `check_activity_unavailable_state()`. It asserts, with no daemon:
   - `ia.activity_view_state(".", journal=None)` returns a dict whose
     `available` is `False`, whose `code` is `"ia.activity_unavailable"`, whose
     `notice` is exactly
     `Activity isn't available yet in this build. Check back after your next update.`,
     and whose `needs_input` and `jobs` are both empty lists.
   - The call raises nothing.

   Then assert the same state reaches a browser. Start a real daemon, and
   before the request, force the absent branch for that process by launching the
   daemon with the environment variable `ITEMBANK_IA_NO_JOURNAL=1` set, and make
   `activity_view_state` treat that variable as equivalent to `journal=None`
   when the argument is `_UNSET`. Document the variable in `surfaces/ia.py`'s
   docstring as a test-only degradation switch that exists because the phase's
   own precondition guarantees `journal.py` is present, so the not-yet-available
   state would otherwise be unreachable in a real tree. Assert the served body
   contains the exact notice sentence and the string
   `href="/help/ia.activity_unavailable"`.

3. Add `check_activity_job_states()`. Using `_fake_journal`, drive
   `ia.activity_view_state(root, journal=fake)` through one case per member of
   `ia.ACTIVITY_JOB_STATES` except `"unavailable"`, and assert for each:

   - `needs_input`: one prepared entry with no resolving entry and no `step`
     field yields exactly one job with `state == "needs_input"`,
     `label == "Needs your input"`, and `token == "pending"`.
   - `in_progress_no_estimate`: a prepared entry carrying `step` 2 and no
     `steps_total` yields `label == "In progress: no estimate."` and the
     rendered label contains no `%` character.
   - `in_progress_known`: a prepared entry carrying `step` 2 and `steps_total` 5
     and `stage` `"Binding sources"` yields exactly
     `"Step 2 of 5: Binding sources"`.
   - `completed`: a prepared entry with a resolving `applied` entry yields
     `label == "Completed"` and `token == "ok"`.
   - `failed`: a prepared entry with a resolving `refused` entry carrying
     `reason` `"rights not granted"` yields exactly
     `"Failed: rights not granted"` and `token == "bad"`, and the label is the
     journal's own recorded reason rather than a generic string.
   - `cancelled`: a resolving entry carrying `cancelled` True yields exactly
     `"Cancelled. Partial results are marked below and were not saved as final."`
     and `token == "warn"`.
   - `interrupted`: `object_state` returning `"interrupted"` yields
     `label == "Interrupted: resume available."` and `token == "warn"`.

   Then assert three list-shape rules in the same check:
   - Zero entries yields `jobs == []` and `needs_input == []`, and the rendered
     page for that state contains no occurrence of the string
     `Needs your input`.
   - One job and three jobs both render through the same
     `<article class="job"` structure, asserted by counting occurrences.
   - `jobs` is ordered newest timestamp first with ties broken by `entry_id`
     ascending, asserted with three entries sharing one timestamp.

   Finally assert the no-invented-percent rule across every case at once: for
   every job produced by every case above, `"%"` does not appear in
   `job["label"]`.

4. Add `check_activity_no_write_path()`. It asserts that
   `ia.activity_view_state` never mutates its input: build a `_fake_journal`
   whose `entries` returns a list of dicts, snapshot
   `json.dumps(entries, sort_keys=True)` before the call, and assert it is
   unchanged after. It also asserts that a malformed entry, the literal value
   `"not a dict"` inside the entries list, produces one job with
   `state == "failed"` and `label == "Failed: unreadable journal entry"` and
   raises nothing.

5. Assert the metadata boundary. In `check_activity_no_write_path`, give one
   entry an extra key `before_image` whose value is the string
   `SECRET-BEFORE-IMAGE`, and assert that string appears in no job dict and in
   no rendered page produced from that state.

6. Update `main()` to run all four checks and print
   `"IA ROUTES: 4 passed, 0 failed"`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_route_roundtrip.py</automated>
Expected: final line `IA ROUTES: 4 passed, 0 failed`, exit 0. The degraded state
this task proves is the not-yet-available branch itself, exercised both as a
direct call with `journal=None` and as a served page under
`ITEMBANK_IA_NO_JOURNAL=1`.
  </verify>
  <acceptance_criteria>
- `python tests/ia_route_roundtrip.py` exits 0 with final line
  `IA ROUTES: 4 passed, 0 failed`.
- `ia.activity_view_state(".", journal=None)["notice"]` equals the literal
  `Activity isn't available yet in this build. Check back after your next update.`
- A served `/activity` page under `ITEMBANK_IA_NO_JOURNAL=1` contains that same
  sentence and the string `href="/help/ia.activity_unavailable"`.
- The seven non-unavailable state cases each assert their exact locked label
  string and their exact token name, as listed in step 3.
- No `job["label"]` produced by any case contains a `%` character.
- Zero entries produces a page containing no occurrence of `Needs your input`.
- The `SECRET-BEFORE-IMAGE` value appears in no job dict and in no rendered
  page.
- A malformed entry produces `Failed: unreadable journal entry` and raises
  nothing.
- The structural no-write ban command from Task 1 still prints `no write path`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Test coverage and one branch inside an
  existing function. Nothing published changes.</reversibility>
  <done>Every Activity job state renders its locked copy, the not-yet-available
  branch is executed rather than described, and no percent and no journal
  payload can reach the page.</done>
</task>

<task type="auto">
  <name>Task 3: extend the shipped route-parity coupling test rather than forking it</name>
  <files>tests/daemon_roundtrip.py, tests/ia_route_roundtrip.py</files>
  <read_first>
- `tests/daemon_roundtrip.py`, `check_route_cli_inventory` at line 1016,
  `check_api_route_scope` at line 1090, and `check_surface_parity` at line 1122,
  all three in full. This task extends these, and adds no fourth coupling test.
- `surfaces/daemon.py` lines 210 to 335 as they stand after Task 1.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-PATTERNS.md`, the
  "One dispatcher, four parallel structures, never a second router" shared
  pattern.
  </read_first>
  <action>
1. In `tests/daemon_roundtrip.py`, extend `check_route_cli_inventory` with one
   added assertion after its existing body: `daemon.ROUTE_CLI[("GET",
   "/activity")]` equals `"activity"`, failing with
   `"GET /activity must map to the activity CLI twin"`. Change nothing else in
   that function; its existing set-equality assertion already covers the new
   route.

2. Add to `tests/ia_route_roundtrip.py` a check named
   `check_route_order_is_load_bearing()`. It asserts, against `daemon.ROUTES`:
   - The index of `("GET", "/activity", "handle_activity_get")` is strictly less
     than the index of the first entry whose pattern is not a `str`, failing with
     `"a new fixed-literal route was appended after the stem-parameterised block"`.
   - Every entry whose pattern is a `str` has a lower index than every entry
     whose pattern is not a `str`, failing with
     `"the fixed-literal-before-stem-parameterised ordering rule was broken"`.
   - `set(daemon.ROUTE_CLI)` equals `set(e[:2] for e in daemon.ROUTES)`, so this
     file fails fast on the same coupling `daemon_roundtrip.py` guards, rather
     than only at the shipped suite.

3. Add a check named `check_one_dispatcher()`. It asserts, by reading
   `surfaces/daemon.py`'s source with `inspect.getsource(daemon)`, that the
   literal substring `def _dispatch` appears exactly once, failing with
   `"a second dispatch mechanism appeared beside DaemonHandler._dispatch"`.

4. Update `main()` to run all six checks and print
   `"IA ROUTES: 6 passed, 0 failed"`.

5. Run both suites and record their final lines:

```
python tests/ia_route_roundtrip.py
python tests/daemon_roundtrip.py
```

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_route_roundtrip.py && python tests/daemon_roundtrip.py</automated>
Expected: `IA ROUTES: 6 passed, 0 failed` and exit 0, then exit 0. The degraded
state proven here is the ordering failure itself: temporarily moving the
`/activity` entry after the regex block must make
`check_route_order_is_load_bearing` fail, and the executor confirms that once by
hand before restoring the correct position.
  </verify>
  <acceptance_criteria>
- `python tests/ia_route_roundtrip.py` exits 0 with final line
  `IA ROUTES: 6 passed, 0 failed`.
- `python tests/daemon_roundtrip.py` exits 0 and its
  `check_route_cli_inventory` now asserts the `/activity` twin by name.
- `inspect.getsource(daemon).count("def _dispatch")` equals 1.
- Moving `("GET", "/activity", "handle_activity_get")` after the trailing regex
  block makes `python tests/ia_route_roundtrip.py` exit non-zero with the
  message `a new fixed-literal route was appended after the stem-parameterised block`;
  the executor records that it observed this and restored the correct position.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` reports `0 offending files`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Two added assertions and two added checks.
  </reversibility>
  <done>The one dispatcher, the four parallel structures, and the load-bearing
  route order are all machine-asserted, and the shipped suite is green.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| browser to daemon route | A new `GET` route is a new reachable surface on a loopback (and, under `--lan`, a network) listener. |
| journal record to rendered page | Journal entries can carry before-images and raw content bytes that assessment disclosure rules keep out of a learner's view. |
| filesystem path to learner-visible copy | A job's recorded intent can name a real path outside the approved roots. |
| route table to dispatcher | A route added outside the four parallel structures would be reachable without a CLI twin, a parity row, or the token gate's inventory. |
| CLI argument to read model | `itembank activity <dir>` takes a caller-supplied directory. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16B-02-01 | Information Disclosure | a journal entry's `before_image` or raw content bytes serialized into the Activity page | high | mitigate | `activity_view_state` builds each job from a fixed eight-key allowlist and copies no other field; Task 2 step 5 asserts a planted `SECRET-BEFORE-IMAGE` value appears in no job dict and no rendered page. |
| T-16B-02-02 | Information Disclosure | a resolved absolute filesystem path echoed in a job's intent text | high | mitigate | Every intent value containing a path separator is passed through `os.path.basename` per D9, reusing the shipped `lesson.src_unreadable` precedent; the acceptance criteria assert the rule and plan 16B-08 re-asserts it across the whole degraded matrix. |
| T-16B-02-03 | Elevation of Privilege | the Activity view acquiring a write path over the journal | high | mitigate | D-16B-8 forbids any resolve route, resolve control, or journal write in this phase; the structural ban command greps `surfaces/ia.py` for write modes, `os.remove`, `shutil.rmtree`, `journal.commit`, and `journal.undo` and fails on any hit. |
| T-16B-02-04 | Spoofing | a new route added outside the four parallel structures and therefore outside the loopback token gate's inventory | high | mitigate | The route is one tuple entry in `ROUTES`, so `DaemonHandler._dispatch` applies `_sidecar_token_ok` to it like every other route; `check_one_dispatcher` asserts no second dispatch function exists, and `check_route_cli_inventory` asserts the key sets agree. |
| T-16B-02-05 | Tampering | a stem-parameterised route shadowing `/activity` | medium | mitigate | The route is inserted inside the fixed-literal block and `check_route_order_is_load_bearing` asserts every string pattern precedes every regex pattern, with the failure observed once by hand before the correct position is restored. |
| T-16B-02-06 | Denial of Service | a malformed or unreadable journal entry crashing the route | medium | mitigate | A non-dict or field-missing entry becomes one `Failed: unreadable journal entry` job and raises nothing; the acceptance criteria assert it. |
| T-16B-02-07 | Repudiation | a fabricated progress figure presented as a measurement | high | mitigate | `ACTIVITY_COPY` has no percent form at all; the only two in-progress strings are `In progress: no estimate.` and `Step {n} of {N}: {stage}`, and every case in Task 2 asserts `"%"` is absent from every produced label. |
| T-16B-02-08 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; `surfaces/ia.py` and `tests/ia_route_roundtrip.py` are standard library only. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
| T-16B-02-09 | Information Disclosure | `itembank activity <dir>` reading a directory the caller should not reach | low | accept | The CLI already takes caller-supplied directories on every other command (`daemon`, `lint`, `day`) and the caller is the single local learner with filesystem access anyway; accepted on the same basis every shipped command accepts it, and no new privilege is created. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- **No Activity write path of any kind.** No `POST /api/activity/resolve`, no
  resolve button, no retry control, no undo control, no write to
  `_journal/journal.jsonl` or `_journal/objects.json`. D-16B-8 defers all of it
  to whichever phase ships after `journal.py`'s commit and undo surface is real.
- No `/api/*` route. `API_ROUTES` stays at twelve members in this plan; plan
  16B-09 adds the one new member the phase gets.
- No course-shelf change to `handle_index`. That is plan 16B-04's.
- No `/help/<code>` route. The Activity page links to one, but the route and its
  table are plan 16B-03's; until that plan lands the link resolves to the
  daemon's existing 404, which is stated and is not a defect this plan fixes.
- No settings key, no schema edit, no fixture, and no sample course.
- No new visual constant. The two `data-ia-*` attributes are stable test hooks,
  not styling; no CSS rule is added by this plan.
- No second coupling test. `tests/daemon_roundtrip.py`'s three existing checks
  are extended, never forked.
</out_of_scope>

<flagged_assumptions>
- **`ITEMBANK_IA_NO_JOURNAL=1` is a test-only degradation switch introduced by
  this plan.** It exists because the phase's own precondition guarantees
  `journal.py` is present, which makes the not-yet-available state unreachable
  in a real tree and would let the phase ship a state it never executed. It is
  documented in `surfaces/ia.py`'s docstring as test-only. If a reviewer judges
  a test-only environment variable in a shipped module unacceptable, the
  alternative is to drop the served-page half of
  `check_activity_unavailable_state` and keep only the direct `journal=None`
  call, and the freeze record must then say the served degraded path was proven
  only in-process.

- **The journal entry field names `resolves_entry`, `object_id`, `step`,
  `steps_total`, `stage`, `reason`, `cancelled`, and `timestamp` are read from
  `14A-02-PLAN.md` plan text.** Plan 16B-01's precondition check asserts the
  four function names and the two state tuples but cannot assert per-entry field
  names. If the landed `journal.py` names these fields differently, this task's
  mapping changes and the deviation is recorded in `16B-02-SUMMARY.md` rather
  than worked around by inventing a second entry schema.
</flagged_assumptions>

<summary_obligations>
`16B-02-SUMMARY.md` records: the final line of every command in every task's
verify block, verbatim; whether the landed `journal.py` entry field names
matched the plan-text names in the flagged assumption, with any deviation quoted
side by side; the observed failure message when the `/activity` route was
temporarily moved after the regex block, proving the ordering check fires;
whether the served not-yet-available page was proven through
`ITEMBANK_IA_NO_JOURNAL=1` or only in-process; the exact final values of
`len(daemon.ROUTES)`, `len(daemon.API_ROUTES)`, and `len(daemon.SURFACE_PARITY)`;
which truth was verified by which command, with the command's actual stdout; and
any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16B-ia-modes-recovery-contract/16B-02-SUMMARY.md`
when done.
</output>
