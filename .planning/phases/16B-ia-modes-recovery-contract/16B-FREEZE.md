# Phase 16B freeze record

## Frozen at 16B

**Dated 2026-08-28.** All six freeze legs hold. The evidence was re-run in this
task rather than trusted from plan `16B-11` Task 1, because a freeze record must
describe the tree it is freezing.

**How the second leg closed, stated first because it was the one in doubt.**
When Task 1 ran, the full suite was red: `tests/retention_roundtrip.py` failed
with `3 settled with 1 correct must be weak, got 'at-risk'`, and
`tests/phase_062_audit.py` inherited it. The cause was an expiring fixture, not
a 16B regression: two `report()` calls in `check_states` omitted the fixed
`cutoff` every other case in that file passes, so they read the wall clock while
their events stayed pinned to August 2026. Once real elapsed time passed
`at_risk_after_days`, at-risk won the D-14 precedence order and the assertion
failed on a tree nobody had changed. Verified pre-existing by reproducing it on
a detached `git worktree` at `HEAD` with no 16B change present.

Weibao was given the choice of fixing the fixture, freezing anyway with the
failure recorded, or withholding, and chose to fix it. Both calls now pass
`cutoff="2026-08-10T12:00:00.000Z"`, the same fixed clock the rest of the file
uses, so the fixture cannot age out again. The suite is now genuinely green at
88 files, 0 failing, and the freeze rests on a green tree rather than on a
judgment about a red one.

**How the fourth leg closed.** `16B-REVIEW.md` records
`accept-with-findings`, made under a standing delegation Weibao gave on
2026-08-28 and labelled there as an agent judgment rather than his own. This is
the same shape `16A-REVIEW.md` used. **Whoever relies on this freeze should read
`16B-REVIEW.md`'s Provenance section first**, since striking that section
reopens the review leg. The review was not a rubber stamp: it raised seven
findings, all carried into Open items below.

## What is frozen

### Routes

Six new route patterns, each with its `ROUTE_CLI` twin:

| Method and pattern | Handler | CLI twin |
|---|---|---|
| `("GET", "/activity")` | `handle_activity_get` | `activity` |
| `("GET", HELP_GET_RE)` where `HELP_GET_RE = re.compile(r"^/help/(?P<code>[a-z0-9_.]{1,64})$")` | `handle_help_get` | `help-code` |
| `("GET", COURSE_GET_RE)` where `COURSE_GET_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})$")` | `handle_course_get` | `daemon` |
| `("GET", COURSE_AREA_RE)` where `COURSE_AREA_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/(?P<area>learn\|practice\|test\|map\|sources\|build\|evidence)$")` | `handle_course_area_get` | `daemon` |
| `("GET", COURSE_LESSON_RE)` where `COURSE_LESSON_RE = re.compile(r"^/course/(?P<course_id>[A-Za-z0-9_.-]{1,64})/learn/(?P<lesson_id>[A-Za-z0-9_.-]{1,64})$")` | `handle_course_lesson_get` | `daemon` |
| `("POST", "/api/shelf")` | `handle_api_shelf` | `shelf` |

`/activity` sits inside the fixed-literal block of `ROUTES`, before every
stem-parameterised entry. The other five are appended to the trailing regex
block. `POST /api/shelf` is the fourteenth member of `API_ROUTES` and adds the
one new `SURFACE_PARITY` row `(("POST", "/api/shelf"), "shelf", "shelf")`,
reserving `shelf` as its MCP tool name per Extensibility Rule 9(a).
`SHELF_ALLOWED_FIELDS = ("action",)` is frozen: the body may carry that field
and no other.

The literal `("GET", "/")` route and its `ROUTE_CLI` value `daemon` are
**unchanged**. The course shelf lives inside the existing `handle_index` behind
a two-way gate (D1): the shelf renders when at least one course exists, and
every other case falls through to the entire shipped bank and plan listing,
including the documented `EMPTY_STATE` copy.

### CLI commands

`activity`, `help-code`, and `shelf`, each registered in `surfaces/cli.py` with
`set_defaults(fn=...)` and each reaching the same `surfaces/ia.py` function its
route reaches.

### Settings keys

Four new top-level properties in `schemas/settings.schema.json`, each carrying
`"x-itembank-phase": 16.2` and a restrictive default:

| Key | Default |
|---|---|
| `approved_roots` | `[]` |
| `network_egress` | `{"hosted_operations": "off", "last_disclosure": ""}` |
| `accessibility` | `{"reduced_motion": "system", "high_contrast": "system"}` |
| `storage` | `{"data_dir": "", "backups_enabled": false, "backup_dir": ""}` |

The schema's top-level `required` array is **unchanged**, and
`additionalProperties` remains `false`. The three object groups each carry
`additionalProperties: false`. `settings.THIS_PHASE` stays `10` and
`settings.SETTINGS_CODES` stays at six members.

Accessors: `NETWORK_EGRESS_SETTINGS_DEFAULTS`,
`ACCESSIBILITY_SETTINGS_DEFAULTS`, `STORAGE_SETTINGS_DEFAULTS`,
`SETTINGS_GROUP_LABELS`, `SETTINGS_DECLARED_NOT_ENFORCED_NOTE`.

### Closed vocabularies on `surfaces/ia.py`

| Name | Members |
|---|---|
| `IA_HELP_CODES` | 12 |
| `ACTIVITY_JOB_STATES` | 8 |
| `DEGRADED_STATES` | 8, and its tuple order is the banner precedence (D-16B-9) |
| `ATTENTION_STATES` | 6 |
| `ATTENTION_ORDER` | 6, and it is the shelf's first sort key (D-16B-10) |
| `MODE_LAYERS` | 7, ordered lowest authority first |
| `MODE_LAYERS_FIXED` | 2 |
| `COURSE_AREAS` | 8 |
| `SHELF_ACTIONS` | 4 |
| `LOOP_ORDER` | 7 |
| `LOOP_STEPS` | 7 loops, 59 steps in total |

### Locked copy constants

`ACTIVITY_COPY`, `ACTIVITY_TOKENS`, `HELP_TABLE`, `HELP_FALLBACK_COPY`,
`ATTENTION_COPY`, `ATTENTION_TOKENS`, `SHELF_EMPTY_HEADING`,
`SHELF_EMPTY_BODY`, `COURSE_AREA_LABELS`, `AREA_NOT_FOUND_NOTICE`,
`ANCHOR_NOT_FOUND_NOTICE`, `DEGRADED_COPY`, `DEGRADED_ACTIONS`,
`DEGRADED_HELP_CODES`, `MODE_LAYER_ROWS`, `MODE_LAYER_FIXED_HEADING`,
`MODE_LAYER_CONFLICT_TEMPLATE`, `MODE_LAYER_DISPLAY_PHRASES`,
`LOCKED_CARD_HEADER_TEMPLATE`, `LOCKED_CARD_TEMPLATE`,
`LOCKED_CARD_NO_CONDITION`, `WALKTHROUGH_COPY`, `WALKTHROUGH_STEPS`,
`SAMPLE_COURSE_COPY`, `LOOP_NEXT_ACTION`, `LOOP_EMPTY_OUTCOME`, and
`daemon.COURSE_NOSCRIPT` and `daemon.SHELF_NOSCRIPT`.

### State files

`_ia/walkthrough.json` and `_ia/sample_course.json`, one JSON object each,
under a daemon-root `_ia/` directory. Both are written through one helper,
`ia.write_ia_state`, which writes to `<path>.tmp` and then calls `os.replace`,
the identical atomic-rename shape `runtime.write_session` uses, so a fault
during a write leaves the old file or the new file and never a half-written
one. `ia.read_ia_state` returns the plain default for a missing, unreadable, or
truncated record and creates no file. Neither is a settings key and neither is
evidence (D-16B-5).

### The bundled sample course

`sample_course.SAMPLE_COURSE_ID = "sample-study-skills"`,
`sample_course.SAMPLE_COURSE_NAME = "Study Skills Basics (Sample)"` with the
`(Sample)` suffix inside the name string itself so no renderer can drop it, and
`sample_course.SAMPLE_COURSE_DIRNAME = "_sample_course"`. That directory is in
`.gitignore` and in `cmd_guard`'s skipped-directory tuple, alongside `_ia`.
`sample_course.py` is staged in `build.py`'s `STAGE_FILES`.

### The document-level contract

`16B-UI-SPEC.md` itself is frozen for its Typography voice-assignment table, its
Color semantic-token assignment table, its Copywriting Contract, its
Degraded-State Matrix, its Activity Contract, its Core Loop Resume Contract, its
Mode-Layer Precedence Contract, its route contract, and its Decisions log D1
through D9. Phase 17A renders against those assignments, and no 16B plan emits a
voice class or a token value.

One discrepancy inside that document is recorded rather than silently resolved:
it states the mode-layer conflict sentence twice and the two differ over the
phrase "for this course". The Copywriting Contract form, which includes the
phrase, was taken as binding. See `16B-DECISIONS.md`,
`## Recorded discrepancy: the mode-layer conflict sentence`.

### Decisions

`16B-DECISIONS.md` carries `D1` through `D9` transcribed from the approved
UI-SPEC, and `D-16B-1` through `D-16B-13` locked by this phase.

## What is NOT frozen

Following the ROADMAP's prototype-before-freeze coupling clause, this freeze
covers the loop storyboards, IA routes and anchors, resume semantics, the job
and approval surface, the mode-layer contract, and the offline, help, and error
states **only**. It is explicitly:

- **not a visual system or token freeze. Phase 17A owns that.** No 16B plan
  introduced a color value, a spacing value, a typography size, a motion rule,
  or a new token constant. Every token name this phase used is an existing one,
  reused by assignment.
- **not a notes, learner-artifact, or strategy freeze. Phase 16C owns that.**
- **not a course schema freeze. Phase 14B owns that.**
- **not a semantic lesson capability freeze. Phase 16A owns that.**

The six rows of `16B-UI-SPEC.md`'s "Open Items Deferred to Other Phases" table,
carried verbatim:

| Item | Deferred to | Why not 16B |
|---|---|---|
| Pixel spacing, typography sizes, and hex color values for every new surface named in this document | Phase 17A | 16B is a structural/copy contract, not a token freeze (ROADMAP Phase 16B goal, explicit). |
| Full mode-layer precedence *enforcement* (a composed resolver over live strategy/accommodation/instructor state) | Phase 16C | Owns `STRATEGY-02`; see Decision D8. |
| Notes and learner-artifact authoring surfaces | Phase 16C | Owns `NOTE-01/02/03`; 16B only reserves their contextual placement inside Learn/Evidence. |
| Real `journal.py`/`course.py`/`graph.py`-backed route content (as opposed to the degraded "not yet available" states this document specifies) | Phase 14A / 14B execution | Neither module exists on disk yet (confirmed this session); every 16B route handler that would call into them sits behind the 16B-01 precondition check per `16B-RESEARCH.md` Pattern 1. |
| New semantic teaching-role rendering inside Learn (beyond the shipped four `_CALLOUT_KINDS`) | Phase 16A execution | `16A-FREEZE.md` does not exist yet; Learn-area fixtures in 16B use only the shipped `KEY`/`EXAMPLE`/`NOTE`/`WARNING` kinds until 16A lands. |
| Search (App-level IA area) | unassigned future phase | See Decision D5. |

Two of those six rows were written before 14A, 14B, and 16A executed and their
"does not exist on disk yet" clauses are now out of date: all three landed, and
`16B-PRECONDITION.md` records the verification. They are carried verbatim
because the deferral itself still holds: 16B renders no real journal-backed or
course-backed area content, and its Learn fixtures still use only the shipped
four callout kinds.

## Evidence

Re-run in this task, on macOS-27.0-arm64 with Python 3.14.6:

```
python3 tests/ia_route_roundtrip.py        IA ROUTES: 24 passed, 0 failed
python3 tests/ia_storyboard_tracer.py      STORYBOARD: 12 passed, 0 skipped, 0 failed
python3 tests/mode_layer_roundtrip.py      MODE LAYERS: 6 passed, 0 failed
python3 tests/degraded_state_roundtrip.py  DEGRADED: 7 passed, 0 failed
python3 itembank.py guard .                0 offending files
the full suite, 88 files                   0 failing
```

Settings additivity, compared against the baseline `16B-PRECONDITION.md`
recorded before any 16B change existed:

```
                                  baseline    now
pre-existing settings keys        22          22
sorted-JSON SHA-256               3d9a94c7...4a1235   3d9a94c7...4a1235
```

Byte-identical. Full value:
`3d9a94c70270413b29390317660b37dc198fc6ae1530c4d5dd3041710c4a1235`.

Route structures as frozen:

```
len(daemon.ROUTES)          43
len(daemon.API_ROUTES)      14
len(daemon.SURFACE_PARITY)  14
len(daemon.ROUTE_CLI)       43
```

Review verdict: `accept-with-findings`, recorded in `16B-REVIEW.md`, signed
"Claude, as an agent, under Weibao's standing delegation of 2026-08-28. Not
Weibao's own signature."

Freeze-gate fixtures: four of five `passed`, one (`APP-02`) `weaker proof`. The
weaker-proof note is that the two layouts are distinguished only by a
viewport-hint header, so what is proven is one route and one identical back href
serving both widths, not rendered layout at either width, which is Phase 17A's;
and that the browser half of the focus-restoration scenario is not observed by
any check here.

## Open items, with owners

### Deferrals this phase made by name

| Item | Owner |
|---|---|
| No Activity write path of any kind: no resolve route, no resolve control, no journal write (`D-16B-8`) | the phase that ships after `journal.py`'s commit and undo surface is exercised |
| No enforcement of `approved_roots`, `network_egress`, `accessibility`, or `storage`; all four are declared at 16.2 and gated on by nothing (plan 16B-06) | unassigned; the settings panel states this on the same screen it offers them |
| No live-state mode-layer collector (`D8`, `D-16B-12`) | Phase 16C, under `STRATEGY-02` |
| No real course-area content; every area reports `content_available` False (plan 16B-05) | Phases 14A and 14B execution |
| No producer for six of the eight degraded states; only `course_corrupted` and `agent_unavailable` are wired into a route (plan 16B-08) | the phases that add each producer |
| Notes: contextual panels inside Learn and Evidence only, no route (`D4`) | Phase 16C |
| Search: reserved as an App-level area name, not built (`D5`) | unassigned future phase |
| The ROADMAP goal clause "hosted, local, and manual continuation share durable checkpoints under the one operation protocol". Phase 16B satisfies only the **read** side of this. `RELIABILITY-02` and `AGENT-01/02/03` own the protocol itself. Recorded so no reader mistakes this phase's display contract for the protocol. | Phases 15A and 15B |
| FILE-04's workspace record does not exist, so `course_shelf_state` runs FILE-04's documented degraded mode, an immediate-subdirectory scan. Reconciliation by pinned id, unreachable-root handling, and the pinned-id-versus-sidecar conflict state are not implemented. | the phase that schedules FILE-04 |

### The APP-02 unresolved probe row

The spec-less edge-coverage probe returned APP-02's row as `unclassified`.
`16B-DECISIONS.md`'s `## APP-02 probe enumeration` names three scenarios rather
than dropping it, and `check_deep_link_scenarios` executes all three: deep-link
stability under rename or move; an anchor into deleted content; and focus
restoration when the target no longer exists, server-side half only. If a
reviewer judges the three insufficient, the correct response is a fourth
scenario, not treating the row as covered.

### Findings the review recorded

| Finding | Owner |
|---|---|
| `Needs reconciliation` is written in operation-protocol vocabulary and would not be meaningful to a learner. Not reachable by any 16B fixture today. | Phase 16C |
| `ia.crash_recovered`'s help page restates its banner and its next action points at "the resume cue" without saying where that is. | the phase that first produces a crash banner |
| The `offline` degraded sentence promises a marking no 16B route renders, because no producer for the offline state exists. | the phase that adds the producer |
| The settings mode-layer disclosure puts all seven layers under a heading reading `Always fixed by itembank`, which could be read as applying to all seven. | Phase 17A |
| The sample course's CTA reads `Start Study Skills Basics (Sample)`, long and ending on the least useful word. | Phase 17A |
| The walkthrough's steps 1 and 3 are close to self-evident from the screen they describe. | Phase 17A, or a later first-run pass |
| Loop B's empty outcome uses "treatment" in the course-design register. | Phase 16C |

### Backstop markers carried by plans 02 through 10

Twenty five markers, enumerated in full in `16B-TRACER-REPORT.md`'s "Backstop
markers carried by plans 02 through 10" table with their owning plan. The review
accepted all twenty five as honest unknowns and none as blocking, on this
reasoning: twelve are loading-state and overflow claims that are unreachable by
construction because every 16B read is synchronous and server-rendered, and each
names Phase 17A or a held-out visual test as owner; two were in fact proven here
and the tracer report says so; and eleven need a producer or a record this phase
does not build.

The review flagged one for a later human pass rather than accepting it
silently: 16B-09's "a long-running job never blocks Learn, Practice, Test, or
Evidence". It is only partially proven, because `/learn` and `/activity` both
returned 200 mid-walkthrough but no durable job was actually in flight, since no
route can start one.

### Other open items

- One em dash character survives at `surfaces/cli.py:1409`, in a pre-existing
  Phase 999.4 comment about LTI. It violates the repository prose rule, it is
  not this phase's, and every file 16B wrote passes the `chr(0x2014)` check.
  Owner: whoever next touches that file.
- `tests/retention_roundtrip.py`'s two wall-clock `report()` calls were pinned
  to the fixed clock during this task, which is a change outside 16B's scope
  made under Weibao's explicit instruction. Recorded here so it is visible in
  the phase's own record rather than only in git history.

- **The "88 files, 0 failing" claim above held an unstated environment
  condition, found 2026-08-28 after the freeze was written.** Re-running the
  suite on a machine with Anki Desktop *open* produced three failures:
  `day_roundtrip.py` and `retention_ui_roundtrip.py` each assert the exact
  "Anki is unavailable" copy and reached a live AnkiConnect instead, and
  `phase_062_audit.py` inherited both because it runs the suite and asserts it
  is green. No 16B code was involved and nothing frozen above is affected.
  This is the same family as the expiring `report()` fixture: a test whose
  verdict depends on the world outside the repository.

  Fixed the same day by pinning `ANKI_CONNECT_URL` to `http://127.0.0.1:9`,
  the discard port, at module scope in both files, which is the pattern
  `tests/due_roundtrip.py` already used. Child processes inherit it, so the
  `day --check` subprocess and the daemon under `start_daemon` are both
  covered. Set unconditionally rather than with `setdefault`, because an
  ambient `ANKI_CONNECT_URL` aimed at a live instance is precisely the case
  being defended against. Verified by running both files against a stub
  AnkiConnect listening on the default port: they passed, where before the fix
  a live instance failed them.

  The freeze's green-tree leg therefore now rests on a suite that does not
  consult the developer's desktop. Owner: closed.
