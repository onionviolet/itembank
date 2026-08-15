---
phase: 16B-ia-modes-recovery-contract
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md
  - .planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
autonomous: false
requirements: [FLOW-01, FLOW-02, APP-01, APP-02, APP-03]
estimate:
  tokens: 52000
  raw_tokens: 52000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "Phase 16B writes no code that imports identity, journal, discovery, graph, course, course_package, or capabilities until a recorded precondition check has confirmed those modules exist on disk and that every constant this phase was planned against matches; a divergence halts the wave by name instead of surfacing as an ImportError or a silent vocabulary drift mid-task."
    - "Both freeze records this phase depends on, 14A-FREEZE.md and 16A-FREEZE.md, are checked for their own frozen headings, and a file that opens with a Freeze withheld heading counts as a failed check rather than as a present record."
    - "16A-PRECONDITION.md's own dated result line is read as well as 16A-FREEZE.md's heading, because a present-but-wrong 16A freeze resting on an unresolved divergence 16A itself recorded is a failure mode a heading check alone cannot see."
    - "Phase 13.9 is confirmed walked, because ROADMAP.md's Phase 14B entry forbids 14B's freeze closing before the walking skeleton has been walked and 16A sits downstream of 14B, which makes an unwalked skeleton a divergence in 16B's transitive dependency."
    - "The shipped route and settings surface this phase extends is re-checked live before it is extended: daemon.API_ROUTES still has exactly twelve members, daemon.ROUTE_CLI's key set still equals daemon.ROUTES' method and pattern pairs, the settings schema still carries exactly twenty top-level properties with additionalProperties false, and settings.SETTINGS_CODES still has exactly six members."
    - "The additivity baseline is recorded as literal SHA-256 values before any 16B change exists, so every later plan proves settings-format additivity by comparison rather than by promise."
    - "The nine UI-SPEC decisions D1 through D9 are transcribed into 16B-DECISIONS.md verbatim rather than re-litigated, and the nine further decisions this plan locks, D-16B-1 through D-16B-9, are recorded beside them so every later plan reads one file for its route shape, its module boundary, its CLI twin names, its settings key set, and its first-run state files."
    - "The assumption-delta detector's finding on the phase text is disposed of on the record: the noun is parser and scorer authority, the decision is no-change, and the reason is that the detected term sits inside a prohibition that preserves the single-authority invariant."
    - "APP-02's unresolved probe row is enumerated as three named scenarios rather than dropped: deep-link stability under object rename or move, an anchor into deleted content, and focus restoration when the original target no longer exists."
  prohibitions:
    - statement: "A failed precondition check must not be worked around by stubbing a missing module, by wrapping the import in a try or except, by continuing with a reduced check set, or by recording the divergence and proceeding anyway; the halt is the correct outcome."
      status: kept
      verification: flagged-unverified
    - statement: "An unanswered checkpoint must not receive a silent default; a decision recorded as chosen when nobody chose it is a false record of authority."
      status: kept
      verification: flagged-unverified
    - statement: "A decision the approved 16B-UI-SPEC already settled must not be reopened by a plan or an executor; transcription is the only permitted operation on D1 through D9."
      status: kept
      verification: flagged-unverified
  artifacts:
    - ".planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md with its five named sections"
    - ".planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md carrying the transcribed D1 through D9, the locked D-16B-1 through D-16B-9, the assumption-delta disposition, and the APP-02 probe enumeration"
  key_links:
    - "The precondition check reads 16A-FREEZE.md, but 16A's own freeze rests on 14B's, which ROADMAP.md makes conditional on Phase 13.9 having been walked. Checking only the frozen heading would accept a freeze whose own upstream gate was never honored, so step 5 reads 16A-PRECONDITION.md's dated result line and the 13.9 evidence directly."
    - "16B-DECISIONS.md is read by every later 16B plan before its first task. A decision recorded here in words a plan cannot act on leaves the executor choosing after all, which is the exact failure PLANNING-DIRECTIVES section 5 exists to prevent."
    - "D-16B-2 decides the module name and boundary, and that name appears in every import in plans 02 through 11, in every structural ban assertion, and in the 16B freeze record. It is the same one-way class 16A-01 Task 3 raised for capabilities.py, and it is raised the same way."
    - "The settings schema hashes recorded here are the only evidence that plan 16B-06's four new top-level keys stayed additive. A hash computed after a 16B edit makes every later additivity assertion pass for the wrong reason, which is why this plan runs first and touches no file outside .planning/."
---

<objective>
Do the two things that must happen before any Phase 16B route, module, or
settings key exists.

First, verify that Phases 14A and 16A actually landed on disk with the surface
16B was planned against, and halt by name if they did not. `16B-RESEARCH.md`'s
"Critical caveat" records that `identity.py`, `journal.py`, `discovery.py`,
`graph.py`, `course.py`, `course_package.py`, `director.py`, and `blueprint.py`
all read MISSING at the repository root when this phase was researched and
planned, that no `14A-FREEZE.md` and no `16A-FREEZE.md` existed, and that
`.planning/phases/13.9-walking-skeleton/` held only three PLAN files with no
SUMMARY. Every 14A and 16A signature this phase cites was therefore read from
plan text, never from source.

This phase's check is one degree stricter than 16A-01's, for the reason
`16B-RESEARCH.md` Pitfall 1 states: 16B must distrust **two** freeze records,
and because 16A is itself downstream of 14B and 13.9, a present-but-wrong
`16A-FREEZE.md` is a failure mode 16A-01 did not have to consider. So the check
reads `16A-PRECONDITION.md`'s dated result line in addition to
`16A-FREEZE.md`'s heading.

Second, write the phase's single decisions file. Nine decisions were already
settled by the checker-approved `16B-UI-SPEC.md` (D1 through D9) and are
transcribed verbatim, never re-litigated. Nine more are locked by this plan
because they are choices an executor would otherwise make: the module boundary
(raised as a blocking checkpoint, exactly as 16A-01 Task 3 raised
`capabilities.py`'s), the exact route regexes, the CLI twin names, the settings
key set and its `required` treatment, the first-run state file shape, and the
one new mutating API route.

Decisions already made, cited, and never re-derived here:

- **PLANNING-DIRECTIVES section 4**, all five non-negotiables, in particular
  number 2 (exactly one parser, one scorer, one evidence store) and number 4
  (format changes are additive, proven by a byte-identical fixture and not by
  promise).
- **PLANNING-DIRECTIVES section 4a**, quoted: section 4.2 "forbids a **second**
  parser, scorer, or evidence store. It does not freeze the one parser's
  grammar." Every additive growth in this phase rests on that sentence, and the
  four new settings keys in plan 16B-06 rest on section 4.4.
- **PLANNING-DIRECTIVES section 4a**, the citation-discipline rule: this plan
  quotes the sentence behind every constraint it invokes.
- **PLANNING-DIRECTIVES section 2 rule 1**: a planning session stops only for an
  action that is hard to reverse, "such as an append-only evidence field, a
  published schema, a format decision other phases will build against". The one
  checkpoint in this plan is exactly that class and is the only one 16B raises
  before its freeze-gate review.
- **ROADMAP.md Phase 16B "Depends on"**, quoted: "Phases 14A and 16A are planned
  but not yet executed, so every signature this phase imports is read from plan
  text at planning time; the first 16B plan opens with a recorded precondition
  check that halts by name on any divergence, the same pattern plans 14B-01,
  15A-01, 15B-01, and 16A-01 set, extended to check for a `16A-FREEZE.md`
  record."
- **ROADMAP.md Phase 16B "Prototype-before-freeze coupling"**, quoted: the 16B
  freeze "is explicitly not a visual system or token freeze (17A), not a notes,
  learner-artifact, or strategy freeze (16C), not a course schema freeze (14B),
  and not a semantic lesson capability freeze (16A)". No 16B plan may
  **introduce** a color value, a spacing value, a typography size, a motion
  rule, or a new token constant. Reusing an existing token name by assignment,
  which is exactly what `16B-UI-SPEC.md`'s Color and Typography sections do, is
  permitted and is not a token freeze.
- **16B-UI-SPEC.md**, checker-approved 2026-08-15, all six dimensions PASS. Its
  Copywriting Contract, Degraded-State Matrix, Activity Contract, Route
  Contract, Settings Expansion Contract, and Decisions log are the binding
  source for every user-visible string in this phase.

Decisions this plan makes and locks, so the executor never guesses (the
`PLANNING-DIRECTIVES.md` section 5 bar). Task 1 transcribes each of these into
`16B-DECISIONS.md` verbatim under its own dated heading. `D-16B-2` is instead
answered by the Task 2 checkpoint.

| ID | Open question | Locked answer | One-line rationale |
|---|---|---|---|
| D-16B-1 | What exactly are the new route patterns, and where do they sit in the load-bearing `ROUTES` order | `("GET", "/activity", "handle_activity_get")` is a fixed literal inserted immediately after `("GET", "/disclosure", "handle_disclosure")` and before `("POST", "/api/theme", ...)`, so it lands inside the fixed-literal block. Four new stem-parameterised entries are appended to the trailing regex block in this order: `("GET", COURSE_GET_RE, "handle_course_get")`, `("GET", COURSE_AREA_RE, "handle_course_area_get")`, `("GET", COURSE_LESSON_RE, "handle_course_lesson_get")`, `("GET", HELP_GET_RE, "handle_help_get")`. The four regexes are exactly: `COURSE_GET_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})$")`, `COURSE_AREA_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/(?P<area>learn|practice|test|map|sources|build|evidence)$")`, `COURSE_LESSON_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/learn/(?P<lesson_id>[A-Za-z0-9_.-]{1,64})$")`, `HELP_GET_RE = re.compile(r"^/help/(?P<code>[a-z0-9_.]{1,64})$")`. | `surfaces/daemon.py:238-244`, quoted: "Order is load-bearing: every fixed literal route comes before every stem-parameterised route". The bounded character classes are also the path-traversal mitigation: an opaque ID that cannot contain `/`, `\`, `%`, or `.` runs of arbitrary length cannot address a file outside its record. |
| D-16B-3 | Which CLI command is each new route's twin | `/activity` maps to a new CLI command `activity`. `/help/<code>` maps to a new CLI command `help-code`. `/course/<id>` and all three course-level patterns map to the existing `"daemon"` command, exactly as `("GET", "/")` and the asset routes already do. `POST /api/shelf` maps to a new CLI command `shelf`. | `tests/daemon_roundtrip.py`'s `check_route_cli_inventory` asserts `set(ROUTE_CLI) == set(e[:2] for e in ROUTES)` and that every value has an `add_parser` registration in `surfaces/cli.py`, so a twin is not optional. `activity`, `help-code`, and `shelf` are genuine runtime capabilities an agent client needs. Course pages are browser renderings of records the `daemon` command already serves, and `course.py` does not exist, so a `course` verb would be a command with nothing behind it; it is named out of scope in plan 16B-05 instead of invented. |
| D-16B-4 | How many new settings top-level keys, what are they called, and do they join `required` | Exactly four new top-level keys: `approved_roots` (array of strings, default `[]`), `network_egress` (object), `accessibility` (object), `storage` (object). Backups are properties **inside** `storage`, not a fifth top-level key. None of the four is added to the schema's top-level `required` array, matching the shipped `update` and `audio` keys which sit in `properties` and not in `required`. | `16B-UI-SPEC.md`'s Settings Expansion Contract table names exactly these four groups plus the two unchanged existing ones and puts backups inside `storage` ("Storage & backups"). Leaving `required` untouched is what makes a pre-16B `itembank.json` validate byte-for-byte as it does today, which is non-negotiable number 4 proven rather than promised. |
| D-16B-5 | Where does first-run and shelf state live on disk | One JSON file per record under a daemon-root directory `_ia/`: `_ia/walkthrough.json` and `_ia/sample_course.json`. Both are written through one helper that writes to `<path>.tmp` and then calls `os.replace`, the identical atomic-rename shape `runtime.write_session` uses. Neither is a settings key and neither is evidence. | Walkthrough position and sample-course removal are per-install app state, not learner preferences and not evidence. Putting them in `itembank.json` would mix app state into a published settings contract; putting them in the evidence store would create a second writer over it. |
| D-16B-6 | Where do the sample course's bundled bytes live, and how is `itembank guard` kept green | A new root-level module `sample_course.py` holds the course as literal Python string constants and exposes `write_sample_course(dest_dir)`. First launch materialises it into `<root>/_sample_course/`. `_sample_course/` is added to `.gitignore` and to `cmd_guard`'s skipped-directory list in `surfaces/cli.py`, beside the existing `fixtures` and `_tmp*` entries. | Guard exists to stop a real bank being **committed**; a gitignored, runtime-materialised directory cannot be committed, so skipping it removes no protection. Shipping the bytes in a `.py` module rather than a committed `.md` keeps guard's markdown walk untouched, and a module import resolves in a checkout and inside a `.pyz` alike without needing `resources.py`. |
| D-16B-7 | What is the one new mutating route, and what may its body carry | Exactly one: `("POST", "/api/shelf", "handle_api_shelf")`, appended to `API_ROUTES` as its thirteenth member. `SHELF_ALLOWED_FIELDS = ("action",)` and `SHELF_ACTIONS = ("remove_sample_course", "skip_walkthrough", "replay_walkthrough", "advance_walkthrough")`. Any other body field is refused with 400 before any helper runs, and the route runs `_reject_cross_origin_write` first. `check_api_route_scope`'s literal `12` becomes `13`, and `SURFACE_PARITY` gains the row `(("POST", "/api/shelf"), "shelf", "shelf")`. | `surfaces/daemon.py:204-208`'s `SEED_ACCEPT_ALLOWED_FIELDS` is the shipped fixed-allowed-fields precedent, and Extensibility Rule 9(a) requires every `/api/*` route to reserve its MCP tool name in the same commit. One route for four small actions keeps the parity tables from growing four rows for one capability. |
| D-16B-8 | What does the Activity view do about a needs-input job while `journal.py` is absent | Nothing that writes. 16B renders needs-input jobs read-only and renders no resolve control at all while `journal.py` is absent. A resolve route, a resolve action, and any journal write are explicitly out of scope for the whole phase and are named as such in plan 16B-02's `<out_of_scope>`. | `16B-RESEARCH.md` Pitfall 2: "Every state-changing Activity action must call into `journal.py`'s own commit/undo functions". A resolve control with no journal behind it can only be a second write path, which is exactly what the pitfall names. |
| D-16B-9 | What is the deterministic order when several degraded banners fire at once | The order of `ia.DEGRADED_STATES`, which is the literal tuple `("crash", "cancelled", "disk_full", "offline", "permission_denied", "future_schema", "agent_unavailable", "course_corrupted")`. The first member present wins the banner slot; every other fired state is still reachable through its own `/help/<code>` link listed below the banner. | The APP-03 ordering probe row asks for a deterministic precedence and a one-to-one banner-to-help-page routing. A declared tuple gives both, and it is the same closed-vocabulary shape `model.GATE_VALUES` already uses. |

Purpose: make the other ten plans transcription rather than judgment.
Output: one recorded precondition result and eighteen recorded decisions.
</objective>

<context>
@.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-PATTERNS.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-VALIDATION.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-01-PLAN.md
@.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md
@.agents/skills/OPERATION-CONTRACT.md
</context>

## Artifacts this phase produces (plan 16B-01 share)

This plan creates no module, no route, no schema key, no CLI flag, and no test.
It creates exactly two planning artifacts, both new in this phase:

- `.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md`
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md`

New symbols introduced by this plan: none.

The full symbol inventory for the phase, repeated in each later plan's own
"Artifacts this phase produces" section so a source-grounding pass can exclude
newly created names from drift verification, is the union below.

- **`surfaces/ia.py`** (module path confirmed by the D-16B-2 checkpoint):
  constants `IA_HELP_CODES`, `ATTENTION_STATES`, `ACTIVITY_JOB_STATES`,
  `DEGRADED_STATES`, `MODE_LAYERS`, `MODE_LAYERS_FIXED`, `COURSE_AREAS`,
  `HELP_TABLE`, `WALKTHROUGH_STEPS`, `SHELF_ACTIONS`; functions
  `activity_view_state`, `help_entry`, `course_shelf_state`,
  `course_area_state`, `deep_link_target`, `anchor_slug`,
  `mode_layer_conflict_copy`, `mode_layer_rows`, `degraded_banner`,
  `locked_refusal_card`, `sample_course_state`, `walkthrough_state`,
  `write_ia_state`, `read_ia_state`, `cmd_activity`, `cmd_help_code`,
  `cmd_shelf`.
- **`surfaces/daemon.py`**: regex constants `COURSE_GET_RE`, `COURSE_AREA_RE`,
  `COURSE_LESSON_RE`, `HELP_GET_RE`; allowed-fields constants
  `SHELF_ALLOWED_FIELDS`; route entries `("GET", "/activity", ...)`,
  `("POST", "/api/shelf", ...)`, `("GET", COURSE_GET_RE, ...)`,
  `("GET", COURSE_AREA_RE, ...)`, `("GET", COURSE_LESSON_RE, ...)`,
  `("GET", HELP_GET_RE, ...)`; handlers `handle_activity_get`,
  `handle_help_get`, `handle_course_get`, `handle_course_area_get`,
  `handle_course_lesson_get`, `handle_api_shelf`; the course-shelf branch inside
  `handle_index`; the read-only mode-layer rows inside `handle_settings_get`.
- **`surfaces/cli.py`**: `add_parser("activity")`, `add_parser("help-code")`,
  `add_parser("shelf")`, and one added entry in `cmd_guard`'s skipped-directory
  list.
- **`schemas/settings.schema.json`**: top-level properties `approved_roots`,
  `network_egress`, `accessibility`, `storage`.
- **`surfaces/settings.py`**: `NETWORK_EGRESS_SETTINGS_DEFAULTS`,
  `ACCESSIBILITY_SETTINGS_DEFAULTS`, `STORAGE_SETTINGS_DEFAULTS`.
- **`sample_course.py`** (new root module): `SAMPLE_COURSE_NAME`,
  `SAMPLE_COURSE_FILES`, `write_sample_course`.
- **`fixtures/course_storyboard_corpus.py`**: `build_two_course_shelf`,
  `build_corrupted_course`, `build_loop_storyboard`, `build_all_16b`.
- **`tests/ia_route_roundtrip.py`**, **`tests/ia_storyboard_tracer.py`**,
  **`tests/mode_layer_roundtrip.py`**, **`tests/degraded_state_roundtrip.py`**
  and every `check_*` and `scenario_*` function on them.
- The planning artifacts `16B-PRECONDITION.md`, `16B-DECISIONS.md`,
  `16B-TRACER-REPORT.md`, `16B-REVIEW.md`, `16B-FREEZE.md`.

<tasks>

<task type="auto">
  <name>Task 1: verify Phases 14A and 16A landed, record the additivity baseline, and write the decisions file</name>
  <files>.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md, .planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md</files>
  <read_first>
- `.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md`, the section
  "Critical caveat: both of 16B's declared dependencies (14A and 16A) have not
  executed, and neither has 16A's own dependency chain", plus Pitfall 1 and the
  Assumptions Log, in full. This task exists because of them.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-01-PLAN.md`
  Task 1, in full. This task copies its shape and adds the second freeze leg and
  the 16A-PRECONDITION dated-result-line leg.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the
  "Decisions and Reasoning Log" table in full. Its nine rows are transcribed
  verbatim by step 8.
- `.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md`, the
  "Artifacts this phase produces" section, for `journal.OBJECT_STATES`,
  `journal.ENTRY_STATES`, and the `entries`, `replay`, `object_state`, `undo`
  signatures plan 16B-02 composes over.
- `surfaces/daemon.py` lines 210 to 335, the four parallel route structures, in
  full. Step 6 asserts their current shape.
- `surfaces/settings.py` lines 26 to 45, `SETTINGS_FILE` and `SETTINGS_CODES`.
- `schemas/settings.schema.json`, its top-level `additionalProperties`,
  `required`, and `properties` keys.
  </read_first>
  <action>
1. Check that the seven dependency modules 16B may reference import. Run:

```
python -c "import identity, journal, discovery, graph, course, course_package, capabilities; print('modules present')"
```

   Expected stdout: `modules present`, exit code 0.

2. Check that the frozen 14A journal surface matches what Phase 16B was planned
   against. Run a single `python -c` that asserts, in this order, printing
   `14A journal surface matches` on success:
   - `journal.OBJECT_STATES` equals
     `("clean", "conflict", "interrupted", "missing", "unavailable")`.
   - `journal.ENTRY_STATES` equals `("prepared", "applied", "refused")`.
   - Every one of `journal.entries`, `journal.replay`, `journal.object_state`,
     and `journal.undo` is callable.
   - `identity.OBJECT_KINDS` is a tuple and `"lesson"` is a member of it.

   These are the exact names plan 16B-02's Activity read model composes over. A
   divergence here changes what the Activity view can render, so it halts.

3. Check that the frozen 16A surface matches. Run a single `python -c` that
   asserts, printing `16A surface matches` on success:
   - `capabilities.RENDERER_AVAILABILITY` equals
     `("available", "degraded", "unavailable")`.
   - `model.SEMANTIC_PROFILE_VERSION` equals `1`.
   - `len(lesson._CALLOUT_KINDS) >= 4` and every one of `"KEY"`, `"EXAMPLE"`,
     `"NOTE"`, `"WARNING"` is a member, where `lesson` is
     `from surfaces import lesson`.

   16B's Learn-area fixtures use only the shipped four callout kinds, so a
   larger membership is not a divergence; a **missing** shipped kind is.

4. Check that both freeze records exist and are real freezes, not withholdings:
   - `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` contains
     the literal heading `## Frozen at 14A`.
   - `.planning/phases/16A-semantic-capability-activity-contract/16A-FREEZE.md`
     contains the literal heading `## Frozen at 16A`.
   - Neither contains the literal heading `## Freeze withheld`. A file carrying
     a withholding heading fails this check even if the frozen heading is also
     present.

5. Check what those freezes rest on, rather than trusting them.
   `16B-RESEARCH.md` Pitfall 1 names this leg by itself:
   - `.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md`
     exists and its `## Dated result line` section contains a sentence stating
     that 16A may proceed. If that section instead records unresolved
     deviations, that is a divergence: record it as
     `16A froze on an unresolved precondition divergence`.
   - `.planning/phases/13.9-walking-skeleton/13.9-03-SUMMARY.md` exists. If it is
     absent while `16A-FREEZE.md` carries its frozen heading, record the
     divergence as `13.9 unwalked behind a frozen 16A`.

6. Check that the shipped surface this phase extends is still what
   `16B-RESEARCH.md` and `16B-PATTERNS.md` read. Run:

```
python -c "import sys; sys.path.insert(0,'.'); from surfaces import daemon, settings; import json; s=json.load(open('schemas/settings.schema.json')); print(len(daemon.API_ROUTES), len(daemon.ROUTES), set(daemon.ROUTE_CLI)==set(e[:2] for e in daemon.ROUTES), len(daemon.SURFACE_PARITY), len(settings.SETTINGS_CODES), len(s['properties']), s['additionalProperties'], len(s['required']))"
```

   Expected stdout exactly:
   `12 34 True 12 6 20 False 18`

   A different `len(daemon.ROUTES)` alone is not automatically a halt: record the
   found value beside the planned value in the Deviations section and continue,
   because the plans address routes by name rather than by index. A `False` in
   the third field, a changed `additionalProperties`, or a
   `len(settings.SETTINGS_CODES)` other than `6` **is** a halt, because plans
   16B-02 and 16B-06 are written against exactly those facts.

7. Record the additivity baseline. This is the phase's only proof that the
   settings-format change in plan 16B-06 stayed additive, so it is taken before
   any 16B change exists. Run:

```
python -c "import hashlib
for p in ('schemas/settings.schema.json','itembank.json'):
    print(p, hashlib.sha256(open(p,'rb').read()).hexdigest())"
```

   Record both `path sha256` lines verbatim as the baseline. Then capture the
   pre-16B effective settings document, which is what plan 16B-06 proves
   unchanged for every pre-existing key:

```
python -c "import sys,json,hashlib; sys.path.insert(0,'.'); from surfaces import settings; d=settings.load_settings('.'); print(len(d)); print(hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest())"
```

   Record both printed lines. A hash that differs from a value you expected is
   not automatically a failure: record the found value as the baseline and note
   any expectation beside it in Deviations. What must never happen is recording
   a baseline computed after a 16B edit, which is why this task runs before any
   file outside `.planning/` is touched.

   Confirm the shipped route and settings suites are green before trusting the
   baseline. Run:

```
python tests/daemon_roundtrip.py
python tests/config_roundtrip.py
```

   Expected: exit code 0 from both.

8. If any check in steps 1 through 6 fails, STOP. Write nothing else, create no
   module, and print exactly this line with the failing item substituted for
   `<item>`, then exit non-zero:

   `HALT 16B-01 precondition: Phase 14A or Phase 16A has not landed, its frozen surface differs from what Phase 16B was planned against, 16A froze on an unresolved divergence, Phase 13.9 was not walked, or the shipped daemon route table and settings surface moved. Re-verify every 16B plan against .planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md and .planning/phases/16A-semantic-capability-activity-contract/16A-FREEZE.md before writing any code. Divergent or missing: <item>`

   Do not work around a failure by stubbing the missing module, by wrapping the
   import in a try or except, by continuing with a reduced check set, or by
   recording the divergence and proceeding anyway. A halt here is the correct
   outcome; it is what this task is for.

9. On success, create
   `.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md` with
   exactly these five sections and nothing more:
   - **Why this check exists.** One paragraph citing `16B-RESEARCH.md`'s
     Critical caveat: every 14A and 16A signature in the 16B research and
     pattern map was read from plan text, not from source, and 16B sits
     downstream of two unexecuted phases plus, transitively, 14B and an unwalked
     13.9.
   - **What was checked.** The full list from steps 1 through 6, one line each,
     each marked `ok` or `divergent`.
   - **Additivity baseline.** The two `path sha256` lines and the two lines from
     step 7's second command, each on its own line, under the sentence: `Plan
     16B-06 asserts every pre-existing settings key unchanged against these
     values. A changed pre-existing key means the settings change was not
     additive.`
   - **Deviations found.** Every place the landed 14A or 16A surface differs from
     the plan text, with the plan-text value and the landed value side by side.
     Write `none` when there are none. A non-empty section means plans 02 through
     11 must be re-read against the two freeze records before execution.
   - **Dated result line.** The date, the verbatim command output of steps 2, 3,
     6, and 7, and one sentence stating whether 16B may proceed.

10. Also on success, create
    `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md` with
    these sections, in this order, and nothing more:
    - A one paragraph header stating that this file is the single source of
      truth for every 16B route, module, CLI, settings, state-file, and copy
      decision; that every later 16B plan reads it before its first task; and
      that Task 2 of this plan appends `## D-16B-2` below.
    - `## Transcribed from 16B-UI-SPEC.md (checker-approved 2026-08-15)`, then
      `## D1` through `## D9`, one dated heading each, each carrying the
      Decision cell and the Reasoning cell copied verbatim from the UI-SPEC's
      "Decisions and Reasoning Log" table. Use these exact headings:
      `## D1. Course-shelf Home lives inside handle_index`,
      `## D2. GET /activity is registered now and renders not-yet-available`,
      `## D3. Course routes use /course/<course_id>/<area> path segments`,
      `## D4. Notes get no dedicated route`,
      `## D5. Search is not built or routed by 16B`,
      `## D6. The Activity IA area is distinct from the ACTIVITY-* requirement family`,
      `## D7. No percent-complete number anywhere in the Activity view`,
      `## D8. Mode-layer enforcement composition is Phase 16C's`,
      `## D9. Path-bearing copy shows the basename only`.
      Do not re-argue, re-word, or extend any of the nine. Transcription is the
      only permitted operation on them.
    - `## D-16B-1` and `## D-16B-3` through `## D-16B-9`, one dated heading each,
      each carrying the locked answer and the one-line rationale transcribed
      verbatim from this plan's objective decision table. Use these exact
      headings: `## D-16B-1. The new route patterns and their position in ROUTES`,
      `## D-16B-3. CLI twin names for every new route`,
      `## D-16B-4. The four new settings keys and the required array`,
      `## D-16B-5. Where first-run and shelf state live on disk`,
      `## D-16B-6. Where the sample course's bytes live and how guard stays green`,
      `## D-16B-7. The one new mutating route and its allowed fields`,
      `## D-16B-8. No Activity write path exists in 16B`,
      `## D-16B-9. Deterministic degraded-banner precedence`.
    - `## Assumption-delta disposition`, recording exactly this: the
      deterministic assumption-delta detector fired on the phase text "no loop
      introduces a second parser or scorer" with kind `pluralization` and term
      `second`; the noun is `parser/scorer authority`; the decision is
      `no-change`; the rationale is that the detected term appears inside a
      prohibition that preserves the single-authority invariant rather than
      introducing a second case, and no identity model changes this phase. Note
      that this disposition is advisory and non-blocking.
    - `## APP-02 probe enumeration`, recording that the spec-less edge-coverage
      probe returned APP-02's row as `unclassified` and unresolved, that the
      planner enumerated it as three named scenarios rather than dropping it,
      and listing the three verbatim: (a) deep-link stability under object
      rename or move, (b) an anchor into deleted content, (c) focus restoration
      when the original target no longer exists. Record that all three are
      carried as acceptance criteria in plan 16B-05 and that none was dropped.
    - `## API coverage note`, recording that the api-coverage detector returned
      `detected: false` over this phase's scope, that no COVERAGE.md matrix is
      owed, and that model backends appear in the Settings surface as
      configuration display only.

    No em dash characters anywhere in either file.
  </action>
  <verify>
  <automated>python -c "import sys,io; sys.path.insert(0,'.'); import identity, journal, capabilities, model; from surfaces import daemon, settings; import json; s=json.load(open('schemas/settings.schema.json')); assert journal.ENTRY_STATES==('prepared','applied','refused'); assert len(daemon.API_ROUTES)==12; assert set(daemon.ROUTE_CLI)==set(e[:2] for e in daemon.ROUTES); assert len(settings.SETTINGS_CODES)==6; assert s['additionalProperties'] is False and len(s['properties'])==20; p=io.open('.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md',encoding='utf-8').read(); assert '## D9.' in p and '## D-16B-9.' in p and '## Assumption-delta disposition' in p and '## APP-02 probe enumeration' in p; print('16B preconditions match')"</automated>
Expected: prints `16B preconditions match` and exits 0. The degraded state this
task must prove rather than paper over is the halt itself: if any assertion
fails, the run exits non-zero with the named HALT line and no file outside
`.planning/` is created. Confirm this by checking that `surfaces/ia.py` does not
exist on disk at the end of a failed run.
  </verify>
  <acceptance_criteria>
- The step 1 command prints `modules present` and exits 0.
- The step 2 command prints `14A journal surface matches` and exits 0.
- The step 3 command prints `16A surface matches` and exits 0.
- Both freeze files exist, each contains its own `## Frozen at` heading, and
  neither contains `## Freeze withheld`.
- `16A-PRECONDITION.md` exists and its `## Dated result line` section states 16A
  may proceed.
- `.planning/phases/13.9-walking-skeleton/13.9-03-SUMMARY.md` exists.
- The step 6 command prints exactly `12 34 True 12 6 20 False 18`, or prints a
  different second field with that difference recorded in Deviations while every
  other field matches.
- `python tests/daemon_roundtrip.py` and `python tests/config_roundtrip.py` both
  exit 0.
- `16B-PRECONDITION.md` exists with all five named sections, and its Additivity
  baseline section carries two `path sha256` lines plus the two lines from step
  7's second command.
- `16B-DECISIONS.md` exists and contains the literal headings `## D1.` through
  `## D9.`, `## D-16B-1.`, `## D-16B-3.` through `## D-16B-9.`,
  `## Assumption-delta disposition`, `## APP-02 probe enumeration`, and
  `## API coverage note`.
- Neither file contains an em dash character. Verify with the command below,
  which builds the character from its code point rather than embedding it, so
  the check is not invalidated by its own text. Expected stdout: `no em dash`.

```
python -c "import io,sys; D=chr(0x2014); bad=[p for p in ('.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md','.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md') if D in io.open(p,encoding='utf-8').read()]; sys.exit('em dash found in '+', '.join(bad)) if bad else print('no em dash')"
```

  Every later 16B plan reuses this same `chr(0x2014)` form for its own em dash
  check, for the same reason. A check that embeds the character it forbids
  reports itself.
- No file outside `.planning/` is created or modified by this task.
  </acceptance_criteria>
  <precondition>Phases 14A and 16A have executed, `identity.py`, `journal.py`, `discovery.py`, `graph.py`, `course.py`, `course_package.py`, and `capabilities.py` exist at the repository root with the surfaces frozen in `14A-FREEZE.md` and `16A-FREEZE.md`, and Phase 13.9 has been walked with `13.9-03-SUMMARY.md` recorded.</precondition>
  <reversibility rating="reversible">The two files record a check and transcribe decisions already made in the plan and in the approved UI-SPEC; nothing durable in the codebase is created and the check can be re-run at any time.</reversibility>
  <done>Either 16B is cleared to proceed with the evidence and the additivity
  baseline recorded, or the wave is halted with the divergence named.</done>
</task>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 2: where the IA read models and the new CLI handlers live</name>
  <files>.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md</files>
  <read_first>
- `16B-RESEARCH.md`, the "Recommended Project Structure" block and Assumption A1,
  both in full. A1 is the reason this is a checkpoint rather than a silent
  adoption: it names this as "a naming/module-boundary choice the planner can
  lock as a `checkpoint:decision` in 16B-01, exactly as 16A-01 locked
  `capabilities.py`'s module boundary (D-16A-2)".
- `16B-PATTERNS.md`, the two `surfaces/ia.py` rows of the File Classification
  table and both Pattern Assignment sections, including the "Do not fold into"
  note.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-01-PLAN.md`
  Task 3 in full, the sibling checkpoint this one copies in shape.
- `surfaces/settings.py` lines 1 to 60, the module docstring plus
  `SETTINGS_CODES` and the two `..._SETTINGS_DEFAULTS` accessors, as the shipped
  example of a surface module that holds both pure logic and a `cmd_*` handler.
- `surfaces/daemon.py` lines 939 to 968, `handle_index`, for the rendering scope
  option-c would widen.
- `.planning/PLAN-TEMPLATE.md`, the standing rule "Name the seam before adding a
  provider", in full.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md` as written
  by Task 1, so the new section is appended below `## D-16B-9` rather than
  overwriting one.
  </read_first>
  <decision>
Does Phase 16B add one new module `surfaces/ia.py` holding the IA read models,
the closed vocabularies, the copy tables, and the three new `cmd_*` CLI
handlers, leaving `surfaces/daemon.py` with route registration and HTML
rendering only; or does the pure logic live in a root-level `ia.py` beside
`model.py` with the CLI handlers in a separate module; or is there no new module
at all, with everything folding into `surfaces/daemon.py`?
  </decision>
  <context>
Phase 16B adds five kinds of new surface: six new routes and their handlers, a
set of closed vocabularies and copy tables (attention states, Activity job
states, degraded states, mode layers, help codes, walkthrough steps), a set of
pure read models over evidence and, once 14A lands, the journal, two small
atomic state files, and three new CLI commands (`activity`, `help-code`,
`shelf`).

Two of those five are unambiguously daemon work: route registration in the four
parallel structures and HTML rendering through `presentation.surface_shell`.
The other three are not. A read model that turns journal entries into a
needs-input list, a table that maps an error code to help text, and a function
that computes a resume cue are all pure transforms with no request behind them,
and they need to be callable from a CLI command as well as from a route, because
`.claude/CLAUDE.md`'s Surfaces constraint states that "every capability has both
a route in the daemon and a command in the CLI. Neither surface is the real one;
both are clients of the runtime."

`surfaces/settings.py` is the shipped precedent for a surface module carrying
both halves: it holds `load_settings`, the validator wiring, the code namespace,
and `cmd_config`, and its docstring states there is exactly one validator behind
every write. 16A established the sibling precedent one phase earlier by putting
its new pure registry in its own module rather than growing `model.py`.

This is rated one-way. The chosen module path appears in every import in plans
02 through 11, in every structural ban assertion, in the 16B freeze record, and
in whatever Phases 16C and 17A build on top. Undoing it after the freeze means
renaming a published surface, not editing a line.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: one new module `surfaces/ia.py` holding the read models, the vocabularies, and the three CLI handlers</name>
      <pros>`surfaces/ia.py` is a new module importing `evidence`, `settings`,
      and (once 14A lands) `journal` and `course`, holding every constant and
      function in this plan's symbol inventory, including `cmd_activity`,
      `cmd_help_code`, and `cmd_shelf`. It matches `surfaces/settings.py`'s
      shipped shape exactly: pure logic, one code namespace, and the `cmd_*`
      handler in the same file, wired into `surfaces/cli.py` by
      `set_defaults(fn=...)` like every other command. `surfaces/daemon.py`
      keeps its stated scope, route registration and rendering, and gains six
      handlers that each call one `ia.*` function and render its result.
      Structural bans that hold by construction rather than by care:
      `surfaces/ia.py` never imports `runtime`, so it cannot score, and it
      imports `model` for exactly one pure helper, `lesson_slug`, so the anchor
      scheme is the shipped one rather than a second slug vocabulary; the only
      `open(` calls in it are the two `_ia/*.json` state helpers. It is also the module a 16C or 17A plan imports, which is
      the seam PLAN-TEMPLATE's "Name the seam before adding a provider" rule
      asks to be named before a second provider exists.</pros>
      <cons>`surfaces/` grows another module, and a reader asking "what does
      `GET /activity` render" reads `daemon.py` for the route and `ia.py` for
      the state. The three CLI handlers sit in a module whose other half is
      consumed by routes, so the file has two audiences.</cons>
    </option>
    <option id="option-b">
      <name>Root-level `ia.py` for the pure half, `surfaces/ia_cli.py` for the CLI handlers</name>
      <pros>The pure half sits beside `model.py`, `runtime.py`, and
      `resources.py`, which is where this repository already puts modules with
      no surface of their own, and it can be imported by a future non-surface
      caller without reaching into `surfaces/`. The pure/CLI split is explicit
      in the filenames.</pros>
      <cons>Two new modules instead of one for a single capability, and no
      shipped precedent for a `*_cli.py` companion except `surfaces/evidence_cli.py`
      and `surfaces/selection_cli.py`, both of which are CLI faces over a
      root-level module that already existed. Here the root module would be
      created in the same phase, so the split buys separation this phase has no
      second consumer for yet.</cons>
    </option>
    <option id="option-c">
      <name>No new module: everything folds into `surfaces/daemon.py`</name>
      <pros>Zero new modules. Every 16B route, handler, vocabulary, and copy
      string is in one file, and a reader tracing a request never leaves
      it.</pros>
      <cons>`surfaces/daemon.py` is already the largest surface module and its
      stated scope is the one dispatcher and its handlers. The three new CLI
      commands would have to import their logic out of a daemon module, which
      makes the CLI depend on the HTTP surface for a capability that has no HTTP
      in it. `16B-PATTERNS.md` names this by name in its "Do not fold into"
      note. It also gives the mode-layer table, the help table, and the degraded
      copy no home a 16C plan can import without importing the router.</cons>
    </option>
  </options>
  <action>
Ask Weibao the question above, present all three options with the recommended
default named, and record the answer verbatim in
`.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md` under a dated
heading `## D-16B-2. Where the IA read models and the new CLI handlers live`.

The recorded section must state, in one sentence each: which option was chosen,
the exact path of every new module, which module holds `activity_view_state`,
which module holds `help_entry`, which module holds `cmd_activity`, and whether
`surfaces/daemon.py` may contain any 16B copy string.

What the executor does with each answer:

- **option-a**: proceed as every task in plans 02 through 11 is already written.
  No plan edit is needed. The module path is `surfaces/ia.py` everywhere.
- **option-b**: before plan 16B-02 Task 1, record in `16B-DECISIONS.md` that the
  module path in every later plan's `files_modified`, `<files>`, `<read_first>`,
  and acceptance criteria changes from `surfaces/ia.py` to `ia.py` for every
  constant and pure function, and to `surfaces/ia_cli.py` for `cmd_activity`,
  `cmd_help_code`, and `cmd_shelf`; that `ia.py` may not import anything from
  `surfaces/`; and that the structural ban assertions in plans 16B-02 and 16B-11
  are split across the two files. Then build it that way.
- **option-c**: before plan 16B-02 Task 1, record in `16B-DECISIONS.md` that no
  `surfaces/ia.py` is created; that every symbol in this plan's inventory lands
  on `surfaces/daemon.py` with the same names; that the three CLI handlers
  import from `surfaces.daemon`; that the structural ban assertions in plans
  16B-02 and 16B-11 are rewritten as function-level assertions because a
  module-level import ban is no longer available; and that the 16B freeze record
  states the daemon module now owns the IA vocabularies and names the reason.
  Then build it that way.

Do not proceed with a silent default. An unanswered checkpoint stops the wave.
  </action>
  <verify>
`16B-DECISIONS.md` carries a dated `## D-16B-2` heading with the chosen option
id and Weibao's answer recorded verbatim.
  </verify>
  <acceptance_criteria>
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md` contains
  the literal heading `## D-16B-2. Where the IA read models and the new CLI
  handlers live`.
- The recorded answer names exactly one of `option-a`, `option-b`, `option-c`.
- The recorded section states, in one sentence each, the exact path of every new
  module, which module holds `activity_view_state`, which module holds
  `help_entry`, which module holds `cmd_activity`, and whether
  `surfaces/daemon.py` may contain any 16B copy string.
- When the answer is `option-b` or `option-c`, the file also carries the
  consequence list this task's action names for that option.
- The file contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">The module path appears in every import in
  plans 02 through 11, in every structural ban assertion, in the 16B freeze
  record, and in whatever Phases 16C and 17A build on it. Undoing it after the
  freeze renames a published surface.</reversibility>
  <resume-signal>Reply with `option-a`, `option-b`, or `option-c`.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| plan text to landed code | Every 14A and 16A signature in this phase's research was read from plan text; the precondition check is the only place that boundary is tested before code is written. |
| freeze record to this phase | Whatever the two freeze records say is frozen is what plans 02 through 11 build against; a withheld freeze read as a present one would authorize planning against an unproven surface. |
| upstream precondition to downstream freeze | 16A's freeze rests on 14B's, which ROADMAP.md makes conditional on Phase 13.9 having been walked; a frozen 16A with an unresolved 16A precondition divergence is a record whose own gate was never honored. |
| checkpoint answer to plan set | The recorded module path changes which files ten later plans may touch; a decision recorded without being asked would authorize a one-way change nobody chose. |
| pre-phase tree to additivity claim | The settings hashes recorded here are the only evidence that plan 16B-06's four new keys stayed additive; a hash taken after a 16B edit makes every later assertion pass for the wrong reason. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16B-01-01 | Tampering | the precondition check worked around instead of obeyed | high | mitigate | Step 8 forbids stubbing, `try` or `except` wrapping, a reduced check set, and recording-and-proceeding by name, and the acceptance criteria assert `surfaces/ia.py` does not exist after a failed run. |
| T-16B-01-02 | Spoofing | a `Freeze withheld` file read as a present freeze record | high | mitigate | Step 4 checks for the absence of the literal `## Freeze withheld` heading in addition to the presence of `## Frozen at`, and states that a file carrying both fails. |
| T-16B-01-03 | Spoofing | a frozen 16A standing in for a resolved 16A precondition and a walked 13.9 | high | mitigate | Step 5 reads `16A-PRECONDITION.md`'s dated result line and `13.9-03-SUMMARY.md` directly rather than trusting `16A-FREEZE.md`, and names both divergences by their own halt strings. |
| T-16B-01-04 | Elevation of Privilege | a one-way module-boundary decision adopted without being asked | high | mitigate | Task 2 is a `checkpoint:decision` with `gate="blocking"` recording a named option id and a verbatim answer, and its action ends with the sentence that an unanswered checkpoint stops the wave. |
| T-16B-01-05 | Repudiation | a decision recorded with no consequence, leaving the executor to choose after all | high | mitigate | Each option's action block names the exact plan edits that option forces, by plan number and by symbol, so a non-default answer produces an actionable record rather than a note. |
| T-16B-01-06 | Tampering | an additivity baseline taken after a 16B edit | high | mitigate | Step 7 runs before any file outside `.planning/` is touched, and the acceptance criteria assert no such file is created or modified by this task. |
| T-16B-01-07 | Tampering | the shipped route table or settings surface drifting between research and execution | medium | mitigate | Step 6 re-checks the API route count, the ROUTE_CLI to ROUTES key-set equality, the SURFACE_PARITY length, the settings code count, and the schema's `additionalProperties` and property count live, with an exact expected stdout. |
| T-16B-01-08 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; this plan runs only `python -c` and two shipped tests against in-repo modules. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
| T-16B-01-09 | Repudiation | a precondition file recording a check that was not run | medium | mitigate | The Dated result line section requires the verbatim stdout of steps 2, 3, 6, and 7, so a fabricated record would have to fabricate four command outputs whose expected values are written into the acceptance criteria. |
| T-16B-01-10 | Information Disclosure | real course or learner content entering the repository | low | accept | This plan creates only two planning markdown files and touches no fixture, bank, or evidence path. Accepted because there is no content path to leak through; `python itembank.py guard .` remains an acceptance check on every later plan that touches `fixtures/` or `sample_course.py`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- No module file of any kind. `surfaces/ia.py` is created by plan 16B-02 Task 1
  and by nothing earlier.
- No route, no route-table edit, no CLI registration, no schema key, and no
  fixture. Every one of those belongs to a named later plan.
- No edit to `surfaces/daemon.py`, `surfaces/settings.py`,
  `schemas/settings.schema.json`, `surfaces/cli.py`, `runtime.py`, `model.py`,
  or `evidence.py`. This plan reads them and changes none.
- No second checkpoint. Every other open question in `16B-RESEARCH.md` is
  resolved either by the approved `16B-UI-SPEC.md` Decisions log (D1 through D9,
  transcribed) or by this plan's objective decision table (D-16B-1 and D-16B-3
  through D-16B-9).
- No re-litigation of D1 through D9. The UI-SPEC passed all six checker
  dimensions on 2026-08-15; a plan that reopens one of its decisions is
  reopening an approved contract, not making a plan.
- No new visual constant of any kind. A new color value, spacing value,
  typography size, motion rule, or token constant is Phase 17A's, and no 16B
  plan may introduce one. Reusing the five existing semantic token names
  (`--ok`, `--bad`, `--warn`, `--unknown`, `--pending`) and the four existing
  voice token names by assignment is what `16B-UI-SPEC.md` already did and is
  permitted.
- No freeze record and no freeze amendment. Plan 16B-11 owns the 16B freeze.
</out_of_scope>

<flagged_assumptions>
Surfaced, not silently dropped, per the spec-less probe fallback protocol.

- **The landed 14A and 16A surfaces may differ from plan text (open until Task 1
  runs).** Every constant value and function signature this plan asserts in Task
  1 steps 2 and 3 was read from `14A-02-PLAN.md` and `16A-01-PLAN.md`, never
  from source, because none of those modules existed when 16B was planned. Task
  1's Deviations found section is where a real divergence is recorded; a
  non-empty Deviations section means plans 02 through 11 must be re-read against
  the two freeze records before execution.

- **APP-02's edge-coverage probe row came back unclassified and unresolved.**
  The planner did not drop it. It is enumerated in Task 1 step 10 as three named
  scenarios (deep-link stability under rename or move, an anchor into deleted
  content, focus restoration when the original target no longer exists) and is
  carried as acceptance criteria in plan 16B-05. If a reviewer judges those
  three insufficient, the correct response is to add a fourth scenario to
  16B-05, not to treat the row as covered.

- **`len(daemon.ROUTES)` is asserted as `34` from a read taken 2026-08-15.**
  Unlike the other five fields in step 6, a change here is not a halt, because
  every 16B plan addresses routes by name and by position relative to a named
  neighbour rather than by index. The value is recorded so a drift is visible
  rather than silent.

- **The phase's seventeen edge-coverage probe rows and fifty-three UI-SPEC UI
  Considerations rows are distributed to the plans that own their surfaces**,
  not held here: the FLOW rows in plan 16B-10, the CourseShelf and APP-01 rows in
  16B-04, the ActivityView and APP-03 precision rows in 16B-02, the
  CourseAreaNav and DeepLinkNav and APP-02 rows in 16B-05, the LockedRefusalCard
  and DegradedStateBanner and APP-03 ordering rows in 16B-08, the SettingsPanel
  and APP-03 boundary rows in 16B-06, the OfflineHelpPanel rows in 16B-03, and
  the FirstLaunchWalkthrough and WalkthroughOffer and remaining APP-03 rows in
  16B-09. This plan holds none of them itself.
</flagged_assumptions>

<summary_obligations>
`16B-01-SUMMARY.md` records: the precondition result and every deviation the
landed 14A and 16A surfaces showed against their plan text, quoted side by side;
whether 16A's own precondition recorded unresolved deviations and whether Phase
13.9 was walked, with the files that proved each; the four additivity baseline
lines as recorded; the option Weibao chose at Task 2 and every plan edit that
choice forced in plans 02 through 11, by plan number and by symbol; the exact
module path every later plan must now use; which truth was verified by which
command, with the command's actual stdout; and any deviation from this plan with
its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16B-ia-modes-recovery-contract/16B-01-SUMMARY.md`
when done.
</output>
