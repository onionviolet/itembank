# Phase 16B: IA, Modes & Recovery Contract - Research

**Researched:** 2026-08-15
**Domain:** Information architecture contract (course shelf, deep links, resume
semantics), the seven core end-to-end loops as an acceptance surface, the
Activity job/approval surface, the seven-layer mode contract, first-run and
offline help, and the crash/cancel/offline/permission/schema/agent degraded-state
matrix. Built on top of Phase 14A (identity, journal, atomic recovery; planned,
not executed) and Phase 16A (semantic capability and activity contract; planned,
not executed). No new external package is required.
**Confidence:** MEDIUM. Everything cited from the shipped `surfaces/daemon.py`,
`surfaces/settings.py`, `schemas/settings.schema.json`, `evidence.py`, and
`runtime.py` is `[VERIFIED: <file>:<lines>]` against real, executed source code
read this session. Everything cited from 14A or 16A is `[VERIFIED: <plan
file>:<lines>]` against plan text only, because neither phase has executed
(confirmed below by direct filesystem check). Composition recommendations for
16B's own new surface (route table shape, Activity job schema, mode-layer
enforcement point) are this research's own synthesis and are flagged
`[ASSUMED]`.

## Critical caveat: both of 16B's declared dependencies (14A and 16A) have not executed, and neither has 16A's own dependency chain

Confirmed by direct filesystem check this session:

```
identity.py MISSING       journal.py MISSING       discovery.py MISSING
graph.py MISSING          course.py MISSING        course_package.py MISSING
director.py MISSING       blueprint.py MISSING
```

`[VERIFIED: repo root `ls *.py`, this session, the listing contains
`audit_writer.py, auditor.py, authoring.py, build.py, evidence.py,
fake_hosted_unused.py, itembank.py, model.py, model_adapter.py, resources.py,
retention.py, runner.py, runtime.py, schema_validate.py, selection.py,
server.py, subjects.py, tier_gate.py` and none of the eight names above.]`

`.planning/phases/14A-identity-lifecycle-operation/` contains only
`14A-01-PLAN.md` through `14A-04-PLAN.md`, `14A-BRIEF.md`, `14A-PATTERNS.md`,
`14A-RESEARCH.md`, `14A-VALIDATION.md`, no `14A-FREEZE.md`, no
`14A-*-SUMMARY.md`. `[VERIFIED: directory listing, this session]`

`.planning/phases/16A-semantic-capability-activity-contract/` contains only
`16A-01-PLAN.md` through `16A-10-PLAN.md`, `16A-PATTERNS.md`, `16A-RESEARCH.md`,
`16A-VALIDATION.md`, no `16A-FREEZE.md`, no `16A-DECISIONS.md`, no
`16A-PRECONDITION.md`, no `16A-*-SUMMARY.md`. `[VERIFIED: directory listing,
this session]`

`.planning/phases/13.9-walking-skeleton/` contains only `13.9-01-PLAN.md`
through `13.9-03-PLAN.md`, no `13.9-*-SUMMARY.md`, no `13.9-DECISIONS.md`.
`[VERIFIED: directory listing, this session]` The walking skeleton has not been
walked. Because `ROADMAP.md`'s Phase 14B entry forbids that freeze closing
"before Phase 13.9 has been walked" and 16A's own dependency is 14B, the whole
chain 13.9 → 14B → 16A that 16B sits downstream of is unexecuted, in addition
to 16B's direct dependency on unexecuted 14A.

This is one step deeper than 16A's own caveat: 16A only had to distrust 14B's
freeze conditional on 13.9. 16B must distrust **two** freeze records (14A's and
16A's) plus, transitively, everything 16A's own precondition check would have
caught if 16A had actually executed. `ROADMAP.md`'s Phase 16B entry states this
explicitly: **"Phases 14A and 16A are planned but not yet executed, so every
signature this phase imports is read from plan text at planning time; the first
16B plan opens with a recorded precondition check that halts by name on any
divergence, the same pattern plans 14B-01, 15A-01, and 15B-01 set, extended to
check for a `16A-FREEZE.md` record."** `[VERIFIED: ROADMAP.md:1944-1950]`

Every function signature, constant, and refusal code cited below as "from 14A"
or "from 16A" is `[VERIFIED: <plan file>:<lines>]`, never `[VERIFIED:
<module>.py]`. By contrast, `surfaces/daemon.py`, `surfaces/settings.py`,
`schemas/settings.schema.json`, `evidence.py`, and `runtime.py` are shipped and
executed, confirmed by reading them directly this session, and 16B's job for
the routing, settings, and evidence-adjacent surfaces those already own is
extension of an existing additive pattern (see Architecture Patterns below),
not invention from nothing.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FLOW-01 | The seven core loops (A discover and bind, B design a course, C learn and construct notes, D practice and test, E evidence and remediation, F author, review, and accept, G maintain, recover, and leave) are the product's end-to-end acceptance surface, each resumable with an exact position and a next justified action. `[VERIFIED: REQUIREMENTS.md:519-529]` | Each loop's exact step sequence is defined in `research/phase-16/14-synthesis.md` section 3, quoted verbatim below. FLOW-01's fixture is "the 16B storyboard and interruption scenarios, interrupting a synthetic run of each of loops A through G mid-step and asserting each resumes at an exact position with a next justified action" `[VERIFIED: REQUIREMENTS.md:527-529]`. Because loops A, B, E, F, and G all read or write objects that live in unexecuted 14A/14B modules, the storyboard fixture must be built against plan-text signatures behind the same precondition-check discipline 16A established, or against a synthetic in-memory stand-in the plan names explicitly as a stand-in. |
| FLOW-02 | A learner moves between direct source reading, lesson, practice, feedback, and the next course action without reconstructing context, reading is continuous and scrolls with no paginating surface, no loop introduces a second parser or scorer, and a Socratic or tutoring refusal renders as a locked card stating its unlock condition, never as a chat exchange. `[VERIFIED: REQUIREMENTS.md:531-542]` | The "locked card, never a chat exchange" clause is a bake-in from 2026-08-14, consistent with RTS-09's locked-card contract `[VERIFIED: REQUIREMENTS.md:536-537]`. The shipped hint ladder and its UI-SPEC §9 Agent Interaction Boundaries table already establish this shape for hints (AgentAssist is "contextual and collapsed; ActivityCanvas remains primary" `[VERIFIED: UI-SPEC.md:603-611]`); FLOW-02 generalizes it to the Socratic-refusal case. The fixture disables the model backend entirely and asserts scoring, the hint ladder, evidence, and reports still run `[VERIFIED: REQUIREMENTS.md:538-542]`. |
| APP-01 | The home surface is a course shelf with an exact resume cue and attention state; each course exposes Overview, Learn, Practice, Test, Course map (outline first), Sources, Build and review, Evidence, and contextual Notes; banks are assessment artifacts inside courses, not the primary navigation unit. `[VERIFIED: REQUIREMENTS.md:816-825]` | The shipped `GET /` route (`handle_index`) is currently a bank-and-plan index, not a course shelf: it lists every bank/plan stem found at startup and links to `/report`, `/quiz/<stem>`, and `/day` `[VERIFIED: surfaces/daemon.py:939-964]`. APP-01 is a genuine architectural supersession of that route's meaning, marked explicitly in `UI-SPEC.md` §15.5: "Bank-first entry language is superseded by the course-first Home and course shelf... The bank remains a durable object and a validated input, not the primary entry" `[VERIFIED: UI-SPEC.md:826-828]`. The fixture is "the 16B storyboard's synthetic course shelf with two fictional courses, one corrupted so it must show its last valid overview and plain-file access" `[VERIFIED: REQUIREMENTS.md:822-825]`. |
| APP-02 | Navigation uses stable opaque deep links and anchors, explicit parent and back semantics, focus and scroll restoration, and the same routes across wide and narrow layouts; chat is contextual to an object or operation, never the home or sole job record. `[VERIFIED: REQUIREMENTS.md:827-835]` | The shipped daemon already has a route-table discipline to extend rather than replace: `ROUTES`, `API_ROUTES`, `ROUTE_CLI`, and `SURFACE_PARITY` are four parallel structures asserted equal in shape by `tests/daemon_roundtrip.py`'s `check_api_route_scope`/`check_surface_parity` `[VERIFIED: surfaces/daemon.py:210-334]`. APP-02's stable-deep-link requirement composes with that discipline: a course-level route is a new fixed-literal or stem-parameterized entry in the same four structures, not a second router. |
| APP-03 | First launch offers a clearly synthetic, removable sample course and a skippable, replayable walkthrough reachable without granting source roots or configuring an agent; help is offline and routes from named error codes; long jobs never block learning or invent a percent when the denominator is unknown; settings expose approved roots, model backends, network and egress policy, accessibility, theme, storage, backups, and update policy, growing the shipped DEL-04 subset to this list. `[VERIFIED: REQUIREMENTS.md:837-850]` | The shipped `schemas/settings.schema.json` top-level keys are exactly `theme, accent, daily_cap, selection_weights, selection, auditor_autonomy, model_backend, suggestion_reveal, update_policy, daemon, reader, teaching, update, style, paraphrase, lti, retention, audio, check, subject_profiles` `[VERIFIED: schemas/settings.schema.json, read via `json.load(...).keys()` this session]`. APP-03's named list (approved roots, model backends, network/egress policy, accessibility, theme, storage, backups, update policy) already has three matches (`model_backend`, `theme`, `update_policy`) and five genuinely new groups (approved roots, network/egress policy, accessibility, storage, backups) that must land as additive top-level keys per `settings.SETTINGS_CODES`'s dotted-code convention `[VERIFIED: surfaces/settings.py:10,39]`, never a second settings file or a second validator. |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

These directives bind every plan this research feeds and are cited here so the
planner does not have to re-derive them:

1. **Runtime invariant, unchanged by this phase.** "One runtime, one scorer, one
   evidence store, and the runtime, not the model, settles scoring, assessment
   disclosure, and evidence." A 16B storyboard, job, or chat affordance must
   never gain scoring, disclosure, or evidence-write authority; only the
   existing runtime keeps that authority.
2. **Five non-negotiables** (`.claude/CLAUDE.md` Constraints, mirrored in
   `PLANNING-DIRECTIVES.md` §4, quoted there verbatim): (1) the runtime owns
   assessment authority; (2) exactly one parser, one scorer, one evidence
   store; (3) evidence and banks stay on disk, no telemetry; (4) format changes
   are additive, proven by a byte-identical fixture; (5) the nine accessibility
   gates in `UI-SPEC.md` §8, which stay LOCKED per `UI-SPEC.md` §15's own
   header note.
3. **Constraint relaxation (2026-08-09).** Python-stdlib-only, no-install-step,
   Python-only, and offline-first are preferences, not rules, for this phase.
   A 16B plan may take a dependency if it earns its cost and is vendored per
   the supply-chain rule (pinned version, recorded checksum, named license
   review). Nothing researched here currently requires one (see Package
   Legitimacy Audit below).
4. **Object, authority, and operation summary (2026-08-13).** Every accepted
   feature this phase contracts must name: actor/owner, durable object, source
   of truth, authority, state axes, provenance, rights, egress, degraded
   behavior, accessibility, validation, and maintenance owner. This is the same
   discipline `REQUIREMENTS.md`'s APP/FLOW rows already apply per-clause; the
   planner's tasks should carry it forward rather than re-deriving it.
5. **Data**: no real question banks or real learner content in this repository,
   enforced by `itembank guard` in CI. Every fixture and corpus this phase's
   plans build must be synthetic, matching the `fixtures/corpus_14a.py` and
   `fixtures/lesson_capability_corpus.py` precedent `[VERIFIED:
   14A-01-PLAN.md:110, 16A-01-PLAN.md:201-203]`.
6. **Compatibility**: format changes are additive; a bank or settings file not
   using a new field parses exactly as before. Applies directly to the
   `schemas/settings.schema.json` expansion APP-03 requires.
7. **No em dash characters** anywhere in repository-authored prose, including
   this research file, generated fixtures, and eventual plan/task text.

## Summary

Phase 16B is a **contract phase for navigation, jobs, mode authority, and
degraded states**, not a visual-design phase and not a course-schema phase. Its
job is to freeze what the app's information architecture, mode layering, and
recovery behavior mean, using the shipped daemon's route-table discipline and
the (planned) journal's compare-and-swap and replay machinery, so that Phase
17A can style the result and Phase 16C can add strategies and notes without
renegotiating navigation or authority.

The first major discovery is that **16B sits two unexecuted phases deep**, one
level deeper than 16A's own caveat. 16B depends directly on 14A (unexecuted)
and 16A (unexecuted), and 16A itself depends on 14B (unexecuted), which itself
may not freeze before Phase 13.9 (unwalked). Every 14A and 16A signature this
research cites is read from plan text, and the planner must open 16B-01 with a
precondition check one step stricter than 16A-01's: it checks for **two**
frozen headings (`14A-FREEZE.md`'s `## Frozen at 14A` and
`16A-FREEZE.md`'s `## Frozen at 16A`), and because 16A is itself downstream of
14B/13.9, a present-but-wrong `16A-FREEZE.md` is a possible failure mode 16A-01
Task 1's shape does not have to consider but 16B-01 does.

The second discovery is that **the shipped daemon already has exactly the
route-table discipline APP-02 asks for**, and 16B's job is extension, not
invention. `ROUTES`, `API_ROUTES`, `ROUTE_CLI`, and `SURFACE_PARITY` are four
parallel tuples/dicts in `surfaces/daemon.py`, checked for shape agreement by
`tests/daemon_roundtrip.py`'s `check_api_route_scope` and
`check_surface_parity` `[VERIFIED: surfaces/daemon.py:210-334]`. A course-shelf
Home, a course-level Overview/Learn/Practice/Test/Course-map/Sources/Build-review
/Evidence route, and an Activity view are new entries in those same four
structures, following the fixed-literal-before-stem-parameterized ordering rule
already documented in-line (`"Order is load-bearing: every fixed literal route
comes before every stem-parameterised route"` `[VERIFIED:
surfaces/daemon.py:238-244]`).

The third discovery is that **the Activity job surface (durable agent and
maintenance jobs) is not itself a 16B build**: `RELIABILITY-02` (the durable
local operation journal with checkpoints, undo, and cross-client resume) is
owned by Phase 15A, and `AGENT-01`/`AGENT-02`/`AGENT-03` (the operation
protocol and backend parity) are also owned by 15A/15B `[VERIFIED:
REQUIREMENTS.md:1291-1293, 881-919]`. 16B's job is the **IA contract that
displays** durable jobs (needs-input, outcomes, recovery, no invented percent)
by reading `journal.py`'s planned `entries`/`replay`/`object_state` surface
`[VERIFIED: 14A-02-PLAN.md:116-119]`, not building a second job-execution
engine. This is a load-bearing distinction: `REQUIREMENTS.md`'s `ACTIVITY-*`
family (purpose-first learner activities/questions) is a **different concept**
from the IA-level "Activity" app area (durable agent/maintenance jobs) that
`research/phase-16/14-synthesis.md` §9.1 names; the two share a word, not a
schema, and a plan or fixture that conflates them will misname its own tests.

The fourth discovery is that **the mode-layer contract (synthesis §8) already
has a partial enforcement precedent in the shipped runtime**: "Runtime
authority... is fixed and not user-configurable during a sitting" `[VERIFIED:
research/phase-16/14-synthesis.md:461]` is exactly the same authority boundary
`runtime.public_item()` and `evidence.mark_event()`'s human-only marker
enforce today (`mark_event` "rejects any marker other than 'human'" `[VERIFIED:
STATE.md:355]`). 16B's job is to name and place the other six layers (learner
preference, author/course strategy, objective constraint, accommodation
override, instructor policy, system safety) as a documented precedence order a
settings/course-record read enforces, not to build a seventh enforcement
mechanism from nothing.

**Primary recommendation:** treat 16B as a two-part deliverable. Part one is
**pure documentation/fixture work that needs no unexecuted module**: the loop
storyboards (loops A-G step sequences, quoted from synthesis §3), the IA route
map (App level + Course level areas), the mode-layer precedence table, and the
degraded-state matrix (crash/cancel/disk-full/offline/permission-denied/
future-schema/agent-unavailable), all of which can be written and fixture-proven
today against synthetic in-memory stand-ins the plan names explicitly, following
16A-02's `capabilities.py` precedent of building new pure modules with no
dependency on unexecuted 14A/14B code. Part two is **thin route wiring in the
shipped daemon** (a course-shelf `GET /`, a `GET /activity` stub, a `GET
/settings` schema expansion) that follows the existing `ROUTES`/`API_ROUTES`/
`ROUTE_CLI`/`SURFACE_PARITY` discipline and degrades to the current bank-index
behavior when no course exists yet (since `course.py` is unexecuted), the same
graceful-precondition pattern 16A used for its capability registry. Every task
that would need a real `journal.entries()` call, a real `course.read_course()`
call, or a real `graph.outline_projection()` call must sit behind the
16B-01 precondition check and either be written against the exact plan-text
signature (re-verified live if 14A/16A land before execution) or built as an
explicitly-labeled synthetic stand-in the freeze record names as such.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Course shelf / Home route | Frontend Server (daemon route + server-rendered HTML) | Course records (14B, not yet built) | `GET /` is served by `surfaces/daemon.py`'s `handle_index` today `[VERIFIED: surfaces/daemon.py:939-964]`; a course-first Home is the same tier, reading a course index once `course.py` exists, degrading to the current bank/plan listing until then. |
| Deep links, anchors, back/parent semantics | Frontend Server (route table) | Browser (focus/scroll restoration, client-side) | Route identity and the HTML response are server-owned (SURF-02: "the browser page is a client of the same JSON API... it holds no key and implements no scoring" `[VERIFIED: REQUIREMENTS.md:161]`); focus/scroll restoration on navigation is necessarily client-side behavior over server-identified anchors. |
| Activity view (durable agent/maintenance jobs) | Frontend Server (new route reading the journal) | API/Backend (journal.py, Phase 14A) | The durable record is `journal.py`'s append-only log (Phase 14A, runtime tier); the Activity **view** is a new daemon route that reads `journal.entries()`/`journal.replay()` and renders needs-input/outcome/recovery state, display, not a second job engine. |
| Mode-layer precedence enforcement | API/Backend (runtime authority layers) | Frontend Server (settings/course-record read for the other six layers) | Runtime authority (scoring, selection, keyed disclosure, formal-test pause) is fixed server-side truth today (`runtime.public_item`, `evidence.mark_event`'s human-only gate) `[VERIFIED: STATE.md:355; runtime.py cited in 16A-RESEARCH.md:73]`; the other six layers (preference through instructor policy) are read-only precedence data the frontend server resolves before rendering, never client-side logic that could be bypassed. |
| First-run sample course + walkthrough | Frontend Server (route + bundled synthetic fixture) | CDN/Static (bundled sample-course asset, no network fetch) | APP-03 requires reachability "without granting source roots or configuring an agent" `[VERIFIED: REQUIREMENTS.md:837-839]`, so the sample course ships as a bundled resource read the same way `resources.py` already serves bundled assets, not a network fetch. |
| Offline help routed from named error codes | Frontend Server (static help bundle keyed by code) | (none) | Follows the shipped `SETTINGS_CODES`/`LINT_CODES`/`GIFT_CODES` dotted-error-code precedent `[VERIFIED: surfaces/settings.py:10,39]`; help text is a local lookup table, never a network fetch, consistent with DEL-07's "fails silently when offline" precedent. |
| Settings expansion (roots, egress policy, accessibility, storage, backups) | Frontend Server (settings.py + schema) | API/Backend (settings read by every route that needs approved-root or backend info) | Same tier the shipped `theme`, `daily_cap`, `model_backend` fields already occupy `[VERIFIED: schemas/settings.schema.json properties list, this session]`; additive top-level keys, one shared validator, no second settings surface. |
| Degraded-state matrix (crash, cancel, offline, permission-denied, future-schema, agent-unavailable) | API/Backend (journal replay decides "old or new valid state") plus Frontend Server (rendering the next safe action) | (none) | RELIABILITY-01's "fault injection yields the old or new valid state, never a mixed state" is the backend guarantee `[VERIFIED: REQUIREMENTS.md:783-792]`; 16B's job is the **rendering contract** for that guarantee (what the learner sees and what action is offered), not the fault-tolerant write path itself. |

## Standard Stack

### Core

No new third-party library is required for this phase's deliverables. Every
16B artifact composes shipped stdlib-only modules (`http.server`,
`socketserver`, `json`, `re`, `os`) the same way every prior daemon-facing
phase has, per the shipped `Frameworks` list in `.claude/CLAUDE.md`
(`http.server` BaseHTTPRequestHandler/TCPServer for the loopback server;
`socketserver.TCPServer` for OS-fallback port binding).

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python standard library | 3.11+ | Route dispatch, JSON responses, settings validation, fixture generation | Every existing daemon route, `settings.py` validator, and test fixture in this repository is stdlib-only; 16B extends the same modules rather than introducing a new runtime dependency. `[VERIFIED: itembank.py imports cited in .claude/CLAUDE.md "Key Dependencies"]` |

### Supporting

None identified. If a future 16B task needs a client-side focus/scroll
restoration helper beyond what vanilla JS in `UI-SPEC.md` §7 already permits,
it is embedded vanilla JS per the shipped precedent (`UI-SPEC.md` §7 "permits
embedded vanilla JS in plain words" `[VERIFIED: PLANNING-DIRECTIVES.md:218-220]`),
not a new package.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Extending the shipped `ROUTES`/`API_ROUTES` tuples | A separate router module or a third-party micro-framework (e.g. a WSGI router) | Rejected: would create a second dispatch mechanism alongside the shipped `DaemonHandler._dispatch`, violating no stated non-negotiable directly but contradicting the project's own "one daemon on one port... every capability in it also has a CLI command" success criterion pattern (`ROADMAP.md` Phase 2) and the Extensibility Rule 9(a) route/CLI/MCP parity discipline already in force. |
| A synthetic-course-fixture module for the storyboard tracer | Reusing 16A's `fixtures/lesson_capability_corpus.py` directly | Reuse where the fixture need overlaps (a lesson to read in Loop C); build a new `fixtures/course_storyboard_corpus.py` for course-shelf/Overview/Sources content 16A's corpus does not model, following the same generator-writes-into-a-caller-supplied-directory shape as `fixtures/corpus_14a.py` `[VERIFIED: 14A-01-PLAN.md:90]`. |

**Installation:** none required.

**Version verification:** not applicable, no external package is recommended.

## Package Legitimacy Audit

**Not applicable.** This phase's research identifies no external package to
install. `gsd_run query package-legitimacy check` was not run because there is
no candidate package name to check. If a later 16B plan introduces a
dependency (for example, a client-side focus-trap or scroll-restoration
micro-library), the planner must run the Package Legitimacy Gate protocol
before that plan is finalized, and the resulting install must be gated behind
a `checkpoint:human-verify` task per this project's supply-chain rule
(`PLANNING-DIRECTIVES.md` §4a: "every third-party artifact... is vendored at a
pinned version with a recorded checksum and a named license review"
`[VERIFIED: PLANNING-DIRECTIVES.md:244-247]`).

**Packages removed due to [SLOP] verdict:** none (no packages evaluated).
**Packages flagged as suspicious [SUS]:** none (no packages evaluated).

## Architecture Patterns

### System Architecture Diagram

```
                         ┌────────────────────────────────────────┐
                         │      Learner / Agent (HTTP client)      │
                         └───────────────┬──────────────────────────┘
                                         │ GET/POST over loopback (or --lan)
                                         ▼
                    ┌──────────────────────────────────────────────────┐
                    │   surfaces/daemon.py :: DaemonHandler._dispatch    │
                    │   walks ROUTES tuple, first-match-wins,            │
                    │   fixed literals BEFORE stem-parameterized regexes │
                    └───┬───────────┬───────────┬───────────┬──────────┘
                        │           │           │           │
             ┌──────────▼──┐ ┌──────▼─────┐ ┌───▼────────┐ ┌▼─────────────┐
             │ handle_index │ │handle_     │ │ (NEW 16B)  │ │(NEW 16B)     │
             │  -> today:   │ │settings_get│ │ course-    │ │ activity view│
             │  bank/plan   │ │  reads     │ │ shelf Home │ │ reads        │
             │  listing;    │ │  schema +  │ │ reads      │ │ journal      │
             │  16B: course │ │  settings  │ │ course.py  │ │ .entries()/  │
             │  shelf when  │ │  .json     │ │ (14B, NOT  │ │ .replay()    │
             │  course.py   │ │            │ │  yet built)│ │ (14A, NOT    │
             │  exists,     │ │            │ │            │ │  yet built)  │
             │  else the    │ │            │ │            │ │              │
             │  shipped     │ │            │ │            │ │              │
             │  fallback    │ │            │ │            │ │              │
             └──────────────┘ └────────────┘ └────────────┘ └──────────────┘
                        │
                        ▼ (existing, unchanged)
             ┌───────────────────────────────────────────┐
             │ runtime.py :: score_response / public_item │
             │ evidence.py :: append_event / mark_event   │
             │  (the ONE assessment authority, untouched │
             │   by any 16B route; APP-02's "runtime      │
             │   authority... fixed" layer)                │
             └───────────────────────────────────────────┘
```

A reader tracing "learner opens the app, resumes a course, hits a stumped
Socratic prompt, and comes back after closing the app" follows: the top
`_dispatch` box picks the course-shelf Home route on first request (empty
resume state) → the learner enters a course, hitting Loop C's `resume with
objective and rationale` step `[VERIFIED: research/phase-16/14-synthesis.md
section 3, Loop C]` → a wrong response holds the cursor (shipped
`runtime.py`/`evidence.py` box, unchanged) → the model backend refuses further
disclosure and the learner sees the FLOW-02 locked card, not a chat exchange →
the learner closes the app mid-lesson → on relaunch, the course-shelf Home
route's resume cue (APP-01) points at the exact position Loop C's `save
position and next action` step recorded, without the learner reconstructing
context (FLOW-02).

### Recommended Project Structure

```
surfaces/
├── daemon.py          # existing: ROUTES/API_ROUTES/ROUTE_CLI/SURFACE_PARITY
│                       #   gains: course-shelf Home, course-level routes,
│                       #   /activity route, expanded /settings
├── ia.py               # NEW (name is a checkpoint:decision candidate,
│                       #   following the module-naming precedent of
│                       #   16A's capabilities.py): course-shelf listing,
│                       #   deep-link/anchor resolution, mode-layer
│                       #   precedence resolver, pure functions, no I/O
│                       #   beyond reading course.py/journal.py once they exist
├── settings.py         # existing: SETTINGS_CODES, load_settings, validator
│                       #   gains: approved_roots, network_egress, accessibility,
│                       #   storage, backups top-level keys
schemas/
├── settings.schema.json  # gains the five new top-level property groups,
│                         #   additively (existing keys unchanged)
fixtures/
├── course_storyboard_corpus.py   # NEW: synthetic multi-course fixture for
│                                  #   the loop A-G storyboard tracer
tests/
├── ia_storyboard_tracer.py       # NEW: loops A-G interruption scenarios
├── ia_route_roundtrip.py         # NEW: course-shelf/deep-link/resume fixtures
├── mode_layer_roundtrip.py       # NEW: seven-layer precedence conflict matrix
├── degraded_state_roundtrip.py   # NEW: crash/cancel/offline/permission/
│                                  #   schema/agent-unavailable matrix
```

### Pattern 1: Precondition check before any code that imports an unexecuted module

**What:** The first plan in a phase whose dependency has not executed opens
with a `type="auto"` task that (a) imports every dependency module the phase
was planned against and asserts it succeeds, (b) asserts every cited constant
and function signature matches what the research/plan text recorded, (c)
checks for the literal frozen heading in each upstream `*-FREEZE.md` (not just
file existence, a withheld freeze must fail the check too), and (d) halts by
name, writing nothing else, on any divergence.

**When to use:** Any 16B plan that would import `identity`, `journal`,
`discovery`, `graph`, `course`, or `course_package` (14A/14B), or `capabilities`
or the new `_CALLOUT_KINDS` entries (16A).

**Example (the exact shape to extend for 16B-01, quoting the working pattern
14A-01 was checked against by 16A-01 and that 16B-01 must extend one degree
further, two freeze records instead of one):**
```python
# Source: 16A-01-PLAN.md Task 1, steps 1-9 (plan text, verified this session)
# 16B-01 extends this shape to check BOTH 14A-FREEZE.md and 16A-FREEZE.md
python -c "import identity, journal; print('14A modules present')"
python -c "import identity
assert identity.RIGHTS_OPERATIONS == ('read','quote','transform',
    'remote_process','package','export','share')
assert identity.OBJECT_KINDS  # tuple, 'lesson' member, etc.
print('14A surface matches')"
# then: check .planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md
#       contains literal '## Frozen at 14A' and NOT '## Freeze withheld'
# then: check .planning/phases/16A-semantic-capability-activity-contract/
#       16A-FREEZE.md contains literal '## Frozen at 16A' and NOT
#       '## Freeze withheld'
# then: check 16A's OWN precondition passed, i.e. 16A-PRECONDITION.md's
#       "Dated result line" states 16A may proceed: otherwise a present
#       16A-FREEZE.md could still rest on a divergence 16A itself recorded
#       and never resolved
```
`[VERIFIED: 16A-01-PLAN.md:246-374 (the numbered steps 1-9), 14A-01-PLAN.md:1-48
(frontmatter and constants asserted)]`

### Pattern 2: Route/CLI/MCP triple-parity table

**What:** Every daemon route is one row in four parallel structures:
`ROUTES` (method, pattern, handler name), `ROUTE_CLI` (route key → CLI command
name), `SURFACE_PARITY` (route, CLI command, reserved MCP tool name) for
`/api/*` routes specifically, and a coupling test (`check_api_route_scope`,
`check_surface_parity`) that asserts the sets agree.

**When to use:** Every new 16B route (course-shelf Home, course-level Overview/
Learn/Practice/Test/Course-map/Sources/Build-review/Evidence, Activity view,
expanded Settings).

**Example:**
```python
# Source: surfaces/daemon.py:223-236, 245-334 (verified this session)
API_ROUTES = (
    ("POST", "/api/start", "handle_api_start"),
    ("POST", "/api/next", "handle_api_next"),
    # ... nine more, then 16B would append its own /api/* additions here,
    # e.g. ("POST", "/api/activity/resolve", "handle_api_activity_resolve"),
)
ROUTES = (
    ("GET", "/", "handle_index"),                 # -> 16B: course shelf
    ("GET", MARKER_PATH, "handle_marker"),
    ("GET", "/day", "handle_day_index"),
    ("GET", "/report", "handle_report_get"),
    ("GET", "/settings", "handle_settings_get"),   # -> 16B: expanded schema
    ("GET", "/disclosure", "handle_disclosure"),
    ("POST", "/api/theme", "handle_theme_post"),
    ("POST", "/cli-twin", "handle_cli_twin"),
    ("POST", "/seed/accept", "handle_seed_accept"),
) + API_ROUTES + (
    # KATEX/FONT asset routes, QUIZ/STUDY/LESSON/GLOSS/KEY/DAY regex routes...
)
# "Order is load-bearing: every fixed literal route comes before every
#  stem-parameterised route" -- a new fixed literal like /course or /activity
# must be inserted into the fixed-literal block, never appended after the
# regex block.
ROUTE_CLI = {
    ("GET", "/"): "daemon",       # -> 16B: still "daemon"; course shelf has
                                   #    no separate CLI verb, matching the
                                   #    shipped index's own CLI mapping
    # ...
}
```
`[VERIFIED: surfaces/daemon.py:223-236, 238-270, 277-313]`

### Pattern 3: Journal-backed job/checkpoint surface (Activity view's data source)

**What:** The Activity view is a read model over `journal.py`'s append-only
log, not a second execution engine. `journal.py`'s planned public surface
already carries everything a needs-input/outcome/recovery view needs:
`entries(base)` (raw reader), `replay(base)` (fault-aware state reconstruction
naming which valid state survived), `object_state(base, object_id)` (one of
`"clean", "conflict", "interrupted", "missing", "unavailable"`), and `undo(base,
entry_id, actor_kind, actor_name)`.

**When to use:** The 16B Activity route's read path.

**Example:**
```python
# Source: 14A-02-PLAN.md:104-140 (plan text, verified this session: journal.py
# does not exist on disk yet, so this cites the planned public surface)
# journal.OBJECT_STATES = ("clean", "conflict", "interrupted", "missing",
#                           "unavailable")
# journal.ENTRY_STATES = ("prepared", "applied", "refused")
#
# A 16B Activity view route composes, never re-derives:
#   for entry in journal.entries(course_root):
#       if entry["state"] == "prepared" and no resolving "applied"/"refused"
#           entry exists yet -> render as "needs-input" or "in progress"
#       state = journal.object_state(course_root, entry["object_id"])
#       if state == "conflict": render base/current/proposal + undo action
#       if state == "interrupted": render "recoverable", offer resume
```
`[VERIFIED: 14A-02-PLAN.md:104-140]`

### Pattern 4: Closed-vocabulary additive registration (settings expansion)

**What:** Every settings/grammar addition in this project is a closed tuple or
enum plus a dotted error code, never a free-form string. `settings.py` follows
this for its own top-level keys; `model.py`'s `GATE_VALUES`,
`surfaces/lesson.py`'s `_CALLOUT_KINDS`, and 16A's planned
`RENDERER_AVAILABILITY` all use the identical shape.

**When to use:** APP-03's five new settings groups (approved roots, network/
egress policy, accessibility, storage, backups).

**Example:**
```python
# Source: schemas/settings.schema.json top-level keys (verified this session
# via json.load) plus surfaces/settings.py:26,39 (SETTINGS_FILE, SETTINGS_CODES)
# Existing top-level keys: theme, accent, daily_cap, selection_weights,
# selection, auditor_autonomy, model_backend, suggestion_reveal, update_policy,
# daemon, reader, teaching, update, style, paraphrase, lti, retention, audio,
# check, subject_profiles
#
# 16B adds, additively, e.g.:
#   "approved_roots": {"type": "array", "items": {"type": "string"}}
#   "network_egress": {"type": "object", "properties": {
#       "hosted_operations_disclosed": {"type": "boolean"}, ...}}
#   "accessibility": {"type": "object", "properties": {
#       "reduced_motion": {"type": "boolean"}, ...}}
#   "storage": {"type": "object", "properties": {"backups_enabled": ...}}
# A settings file that omits every new key must still validate and load
# exactly as it does today (additive-format non-negotiable #4).
```
`[VERIFIED: schemas/settings.schema.json, python json.load this session;
surfaces/settings.py:26,39]`

### Anti-Patterns to Avoid

- **A second router or dispatch mechanism for course/Activity routes:** the
  shipped `DaemonHandler._dispatch` walking `ROUTES` in order is the one
  dispatcher; a new route is a new tuple entry, never a parallel `if` chain or
  a separate WSGI app mounted alongside it.
- **A job-execution engine inside the Activity view:** the Activity route
  reads `journal.py`'s state; it must never itself decide whether an operation
  applied, retry it, or write a new journal entry outside the compare-and-swap
  path 14A-02 defines. That would create a second write authority over the
  same journal.
- **Collapsing the "Activity" IA area with `REQUIREMENTS.md`'s `ACTIVITY-*`
  family:** these are different objects (durable agent/maintenance jobs vs.
  purpose-first learner questions/activities). A fixture or route named
  `activity` without a doc comment distinguishing the two will be
  misread by a future planner.
- **A percent-complete progress bar on a long job:** REQUIREMENTS.md APP-03 and
  synthesis §9.2 both forbid inventing a percent when the denominator is
  unknown; render a named stage or "in progress, no estimate" instead.
- **Treating a Socratic refusal as a chat turn:** FLOW-02's bake-in requires a
  locked card with a stated unlock condition, mirroring RTS-09's shipped
  locked-card contract for the hint ladder, never a free-text chat bubble.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Route dispatch for new IA surfaces | A second router/framework, or an `if`-chain outside `_dispatch` | The shipped `ROUTES`/`API_ROUTES` tuples plus `ROUTE_CLI`/`SURFACE_PARITY` parity maps | One daemon, one dispatcher is a SURF-01/SURF-04 non-negotiable pattern already enforced by `tests/daemon_roundtrip.py`'s coupling checks. |
| Durable job/checkpoint tracking for Activity view | A new job queue, task table, or second event log | `journal.py`'s planned `entries`/`replay`/`object_state`/`undo` (Phase 14A) | RELIABILITY-02 already names the journal as "the durable job record, not a chat transcript" `[VERIFIED: REQUIREMENTS.md:797-798]`; a second job store would be a second evidence-adjacent authority. |
| Progress/completion reporting on the course shelf or Overview | A single aggregate mastery/completion percentage | The honest-progress tuple (claim kind, scope/version, numerator, denominator-or-indeterminate, rule, snapshot/window, settled/pending/unknown, authority, uncertainty) from GRAPH-03 | GRAPH-03 explicitly forbids "a single aggregate completion, mastery, or readiness score" `[VERIFIED: REQUIREMENTS.md:403-407]`; APP-01's Overview area must compose the tuple, not invent a rollup. |
| Mode/feedback authority for a sitting | A UI-level toggle that lets a learner change scoring or disclosure mid-sitting | The existing runtime authority layer (`runtime.public_item`, `evidence.mark_event`'s human-only marker gate) plus the mode-layer precedence table naming runtime authority as fixed | MODE-01 through MODE-06 already lock feedback policy to session mode server-side; 16B's settings/preference layer must sit below that layer in the precedence order, never override it. |
| Offline help content | A hosted help site or network-fetched FAQ | A bundled, local, error-code-keyed lookup table following `SETTINGS_CODES`/`LINT_CODES` | APP-03 requires help to be "offline and routes from named error codes" `[VERIFIED: REQUIREMENTS.md:839]`; a network dependency for help text would violate the no-blocking-on-network resilience rule (`CLAUDE.md:57`, quoted in `PLANNING-DIRECTIVES.md` §4a). |
| First-run sample course delivery | A generated-on-first-run course (calling an agent or a model) | A bundled, pre-built synthetic sample course shipped as a resource, read the same way `resources.py` serves other bundled assets | APP-03 requires the walkthrough reachable "without granting source roots or configuring an agent" `[VERIFIED: REQUIREMENTS.md:837-839]`; generating it on first run would require exactly the agent configuration the requirement says must not be needed. |

**Key insight:** every "don't hand-roll" in this phase resolves to the same
principle the project already enforces everywhere else: there is one
dispatcher, one durable write authority (the journal, once 14A lands, playing
the same role `evidence.py` already plays for assessment), and one progress
representation (the honest-progress tuple). 16B's contribution is IA and mode
*documentation and read-side composition* over those, not a fourth authority.

## Runtime State Inventory

Not applicable. This is a greenfield contract phase (new routes, new IA
documents, new settings keys), not a rename, refactor, or migration of an
existing string, key, or identifier. No stored data, live service config,
OS-registered state, secret/env var name, or build artifact is being renamed
or relocated by this phase's scope. The one adjacent fact worth recording
explicitly rather than leaving implicit: the shipped `GET /` route's *meaning*
changes (bank/plan index → course shelf), which is a **behavior** supersession
documented in `UI-SPEC.md` §15.5, not a rename of a route path, a file, or a
stored key, the literal string `"/"` is unchanged.

## Common Pitfalls

### Pitfall 1: Trusting a frozen heading without checking what it rests on

**What goes wrong:** A plan checks that `16A-FREEZE.md` contains `## Frozen at
16A` and proceeds, without checking whether 16A's own precondition check
(against 14B) passed or recorded a divergence 16A never resolved.
**Why it happens:** The frozen-heading check is a fast, purely textual
assertion; tracing the freeze back through 16A's own `16A-PRECONDITION.md`
"Dated result line" requires reading a second file.
**How to avoid:** 16B-01's precondition check must read
`16A-PRECONDITION.md`'s dated result line in addition to `16A-FREEZE.md`'s
heading, exactly as 16A-01 read `14B-06-PLAN.md`'s Phase-13.9 gating step
rather than trusting `14B-FREEZE.md` alone `[VERIFIED: 16A-01-PLAN.md:295-304]`.
**Warning signs:** A `16A-FREEZE.md` that exists but whose companion
`16A-PRECONDITION.md` records "Deviations found" with unresolved items.

### Pitfall 2: Building the Activity view as a second write path

**What goes wrong:** A plan implements "resolve this job" as a direct write to
some job-state file from the Activity route handler, bypassing
`journal.commit_operation`'s compare-and-swap discipline.
**Why it happens:** The Activity view naturally wants a "mark resolved" action,
and it is tempting to give the route a direct write for responsiveness.
**How to avoid:** Every state-changing Activity action must call into
`journal.py`'s own commit/undo functions, never write `_journal/objects.json`
or `journal.jsonl` directly; `objects.json` is explicitly documented as "a
disposable projection" `[VERIFIED: 14A-02-PLAN.md:28]` and rebuildable , 
writing to it directly breaks that guarantee.
**Warning signs:** A route handler that opens `_journal/journal.jsonl` for
append itself instead of calling a `journal.py` function.

### Pitfall 3: A percent-complete number appearing anywhere on the course shelf or Overview

**What goes wrong:** A "76% complete" badge appears on a course card because it
is visually satisfying and easy to compute as `answered / total`.
**Why it happens:** A single number is the path of least resistance for a
shelf-card layout, and the honest-progress tuple is more verbose to render.
**How to avoid:** GRAPH-03's fixture explicitly asserts "each tuple dimension
reports separately and no aggregate score appears" `[VERIFIED:
REQUIREMENTS.md:421-424]`; the course-shelf attention cue (APP-01) must use a
qualitative resume cue (e.g., "3 objectives due", "last read 2 days ago") built
from named denominators, never a synthesized ratio across incompatible
dimensions.
**Warning signs:** Any UI copy or fixture assertion containing a bare `%`
computed from more than one evidence dimension.

### Pitfall 4: Narrow-screen stacking losing route identity

**What goes wrong:** On a narrow screen, a supporting pane (Sources, Evidence,
Activity) becomes a stacked destination with a *different* URL shape than its
wide-layout counterpart, breaking APP-02's "same routes across wide and narrow
layouts" clause.
**Why it happens:** It is easy to implement narrow-screen stacking as a
separate "mobile route" rather than the same route rendered in a stacked
layout mode.
**How to avoid:** The route table (`ROUTES`) must not gain width-conditional
entries; layout mode is a rendering decision inside the handler (or a query
parameter/viewport hint), never a second URL for the same object.
**Warning signs:** Two different `(method, pattern)` tuples in `ROUTES` that
resolve to what is conceptually the same object.

### Pitfall 5: Offline help silently depending on the model backend

**What goes wrong:** A "get more help" action on an error routes through the
hosted model adapter rather than the bundled offline lookup, so help becomes
unavailable exactly when network/model access is the thing that failed.
**Why it happens:** The model adapter is the richer, more flexible source of
explanation text, and it is tempting to prefer it even for baseline help.
**How to avoid:** APP-03 requires help to be "offline and routes from named
error codes" as the baseline; any model-backed elaboration is an *optional*
enhancement layered on top, never the only path, matching MODEL-03's "core
loop degrades rather than blocks when no model is reachable" `[VERIFIED:
REQUIREMENTS.md:174]`.
**Warning signs:** A help fixture that fails when
`ITEMBANK_MODEL_BACKEND` (or equivalent) is unset or the network is disabled.

## Code Examples

### Reading the journal for the Activity view's needs-input list (planned signature)

```python
# Source: 14A-02-PLAN.md:104-119 (plan text; journal.py does not exist yet)
import journal

def activity_needs_input(course_root):
    """Return entries whose 'prepared' state has no resolving entry yet."""
    resolved_ids = set()
    prepared = []
    for entry in journal.entries(course_root):
        if entry["state"] in ("applied", "refused") and entry["resolves_entry"]:
            resolved_ids.add(entry["resolves_entry"])
        elif entry["state"] == "prepared":
            prepared.append(entry)
    return [e for e in prepared if e["entry_id"] not in resolved_ids]
```

### Extending the daemon's route table additively (shipped shape)

```python
# Source: surfaces/daemon.py:223-270 (verified this session)
# A 16B course-shelf Home is a new GET "/" behavior inside the EXISTING
# handle_index, gated on whether any course exists yet -- not a new route
# entry, since "/" is already taken. A new fixed-literal Activity route is
# a NEW entry, inserted into the fixed-literal block before API_ROUTES:
ROUTES = (
    ("GET", "/", "handle_index"),
    ("GET", MARKER_PATH, "handle_marker"),
    ("GET", "/day", "handle_day_index"),
    ("GET", "/report", "handle_report_get"),
    ("GET", "/settings", "handle_settings_get"),
    ("GET", "/disclosure", "handle_disclosure"),
    ("GET", "/activity", "handle_activity_get"),     # NEW, 16B
    ("POST", "/api/theme", "handle_theme_post"),
    ("POST", "/cli-twin", "handle_cli_twin"),
    ("POST", "/seed/accept", "handle_seed_accept"),
) + API_ROUTES + (
    # ... unchanged regex routes ...
)
```

### Settings schema additive expansion (shipped file, new keys only)

```python
# Source: schemas/settings.schema.json properties list (read via json.load,
# this session): ['theme', 'accent', 'daily_cap', 'selection_weights',
# 'selection', 'auditor_autonomy', 'model_backend', 'suggestion_reveal',
# 'update_policy', 'daemon', 'reader', 'teaching', 'update', 'style',
# 'paraphrase', 'lti', 'retention', 'audio', 'check', 'subject_profiles']
#
# 16B adds five new top-level keys to this same file (not a new file):
# approved_roots, network_egress, accessibility, storage, backups.
# A settings.json written before this phase, carrying none of the five,
# must still load_settings() and validate() exactly as it does today --
# proven by a byte-identical-defaults fixture the same way GATE-05 and
# LESSON-14 proved additivity for earlier grammar additions.
```

## State of the Art

Not applicable in the conventional sense (this is not a third-party library
whose API changed). The relevant "old approach to current approach" shift is
internal to the project's own roadmap:

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Bank/plan-first `GET /` index as the app's primary entry | Course-first shelf as Home, banks as assessment artifacts inside courses | Source-to-course reframe, 2026-08-13, landed in `UI-SPEC.md` §15.5 | `handle_index` gains course-shelf behavior; the shipped bank/plan listing becomes the degraded fallback when no course exists, not deleted. |
| Four broad Phases 14-17 | Nine subphases 14A-17B with named freeze gates and prototype-before-commitment gates | 2026-08-13 (`ROADMAP.md`, synthesis §14-15) | 16B's own scope boundary (not a visual, notes/strategy, course-schema, or lesson-capability freeze) comes directly from this resequencing. |
| Two-phase "logical then visual" split (old §8) | Nine-subphase dependency table with 16B depending on 14A+16A specifically | 2026-08-13, `PLANNING-DIRECTIVES.md` §8 | Determines exactly which two upstream freeze records 16B-01's precondition check must verify. |

**Deprecated/outdated:** any planning artifact that still frames the app
around "dashboard" metrics above the next instructional action is explicitly
superseded per `UI-SPEC.md` §15.5, and standalone "visual card" inventories are
superseded by semantic teaching blocks composed from shared relations.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The new IA/mode-layer module should be named `surfaces/ia.py` (or similar), following 16A's `capabilities.py` precedent of a new pure-logic module rather than folding new logic into `surfaces/daemon.py` directly. | Recommended Project Structure | Low: this is a naming/module-boundary choice the planner can lock as a `checkpoint:decision` in 16B-01, exactly as 16A-01 locked `capabilities.py`'s module boundary (D-16A-2). No behavior depends on the name. |
| A2 | The course-shelf Home should live inside the existing `handle_index` (gated on course existence) rather than as a brand-new route, to avoid a second meaning for `GET /`. | Code Examples, Architectural Responsibility Map | Medium: if the planner instead mints a new `/home` or `/courses` route and leaves `/` as the legacy bank index permanently, APP-01's "the home surface is a course shelf" requirement is not literally satisfied by the app's actual entry point. This should be raised as an explicit 16B-01 checkpoint, not assumed silently. |
| A3 | Five specific new settings top-level keys (`approved_roots`, `network_egress`, `accessibility`, `storage`, `backups`) are the right decomposition of APP-03's named list, rather than fewer, more nested keys. | Architecture Patterns Pattern 4, Phase Requirements APP-03 row | Low: this is a schema-shape choice within an additive, closed-vocabulary discipline the planner can adjust freely; no downstream phase is cited as depending on the exact key names yet. |
| A4 | The Activity IA area and the `ACTIVITY-*` requirement family are conceptually distinct and this distinction has not previously been stated explicitly in any binding contract file read this session. | Summary, Don't Hand-Roll | Medium: if this research's reading is wrong and some other file does equate them, a plan built on this distinction could misname a test or a route. Recommend the planner confirm this reading explicitly in 16B-01's decisions record, citing both `research/phase-16/14-synthesis.md` §9.1 (Activity IA area) and `REQUIREMENTS.md`'s `ACTIVITY-01/02/03` (learner activity family) side by side. |

## Open Questions

1. **Does 16B write real route-wiring code in `surfaces/daemon.py`, or only planning artifacts and fixtures (mirroring 16A-01's split between planning-only Task 1 and later code-writing plans)?**
   - What we know: 16A's later plans (02-10) did write real code into shipped modules (`surfaces/lesson.py`, `model.py`) despite 14A/14B being unexecuted, because that code was additive and did not need `course.py`/`graph.py` to exist to be tested via synthetic fixtures.
   - What's unclear: whether a course-shelf `GET /` and an Activity route can be similarly tested via synthetic fixtures without any real `course.py`/`journal.py`, or whether they must be deferred to code-writing plans that sit behind the 16B-01 precondition and are explicitly conditional on 14A/16A landing before execution.
   - Recommendation: follow 16A's split. Write the IA/mode/degraded-state *documents and pure-function fixtures* now (no dependency), and write the *route wiring* as plans whose Task 1 `<read_first>` explicitly says "re-verify against the live `14A-FREEZE.md`/`16A-FREEZE.md` before executing this task," the same caveat 16A-01's own objective states for every signature it cites.

2. **What exact HTTP status/behavior does `GET /activity` return when `journal.py` does not exist on disk (today's actual state)?**
   - What we know: the precedent for a route whose backing data is absent is `handle_day_index`'s documented "ambiguous case (zero, or two-or-more) is the documented 404 rather than a guess" `[VERIFIED: surfaces/daemon.py:1965-1969]`.
   - What's unclear: whether an Activity route with no journal module should 404, redirect to a "feature not yet available" static page, or simply not be registered in `ROUTES` until 14A lands.
   - Recommendation: the planner should decide this as an explicit checkpoint in 16B-01, since it is exactly the class of one-way, other-phases-will-build-against-it decision `PLANNING-DIRECTIVES.md` §2 requires stopping for.

3. **Should the mode-layer precedence table (synthesis §8) be enforced by a single new function 16B introduces, or does 16B only need to document the table and defer enforcement composition to 16C (which owns strategies)?**
   - What we know: `STRATEGY-02` (owned by Phase 16C per `REQUIREMENTS.md` mapping) already covers "learner preference, author or course strategy, objective constraint, accommodation override, instructor policy, runtime authority, and system safety are ordered precedence layers" as its own requirement text, nearly identical to synthesis §8's table.
   - What's unclear: whether 16B's mode-layer contract clause in the ROADMAP Phase 16B goal ("the mode layering from synthesis section 8 is contracted so learner preferences... never collapse into one settings pile") is fully satisfied by documentation plus the settings-schema shape, or whether it requires a runnable precedence-resolution function 16B itself must ship.
   - Recommendation: treat 16B's obligation as the settings-schema shape plus a documented precedence table and a fixture proving a conflict resolves toward the higher layer (per `REQUIREMENTS.md` STRATEGY-02's fixture pattern), and explicitly note in the 16B freeze record that full strategy-level enforcement composition is 16C's, avoiding scope duplication between the two phases.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11+ | All 16B code and fixtures | Yes (per `.claude/CLAUDE.md` "Runtime": tested via `actions/setup-python@v5`) | 3.11+ | (none) |
| `identity.py`, `journal.py`, `discovery.py` (Phase 14A) | Route wiring that reads real journal/course-adjacent state | No, confirmed missing this session | (none) | Build against plan-text signatures behind a precondition check; degrade route behavior to a documented "not yet available" state until 14A lands. |
| `graph.py`, `course.py`, `course_package.py` (Phase 14B) | Course-shelf content, Course map, Sources routes | No, confirmed missing this session | (none) | Same as above; 16A already established this fallback discipline for its own dependency on 14B. |
| `capabilities.py`, expanded `_CALLOUT_KINDS` (Phase 16A) | Learn-area rendering that surfaces new semantic roles | No, confirmed missing this session (no `16A-FREEZE.md`) | (none) | Build IA/route contracts that do not require the new semantic roles to exist; a Learn-area fixture can use the shipped four `_CALLOUT_KINDS` (`KEY`, `EXAMPLE`, `NOTE`, `WARNING`) until 16A lands. |
| Git | Optional, for any phase-state inspection | Yes (repo is a git working tree) | (none) |, |

**Missing dependencies with no fallback:** none. Every missing dependency above
has a documented degrade-and-precondition-check fallback, matching the pattern
16A already established for its own unexecuted upstream.

**Missing dependencies with fallback:** `identity.py`/`journal.py` (14A),
`graph.py`/`course.py`/`course_package.py` (14B, transitively), `capabilities.py`
(16A), see table above.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Direct-execution Python scripts, no pytest/unittest runner dependency, matching every existing `tests/*_roundtrip.py` file `[VERIFIED: .claude/CLAUDE.md "Testing", "Python unittest/subprocess-based... Test runner: Direct Python script execution"]` |
| Config file | none, see Wave 0 |
| Quick run command | `python tests/ia_route_roundtrip.py` (per-file, following e.g. `python tests/lesson_roundtrip.py`) |
| Full suite command | the project's existing full-suite invocation (no single documented aggregate command was found in files read this session; the planner should confirm the CI invocation in `.github/workflows/ci.yml` before writing the plan's verify steps) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FLOW-01 | Loops A-G each resume at an exact position with a next justified action after interruption | integration/tracer | `python tests/ia_storyboard_tracer.py` | ❌ Wave 0 |
| FLOW-02 | Reading/lesson/practice/feedback/next-action moves without context reconstruction; model-unavailable degrade keeps scoring/hints/evidence/reports working | integration | `python tests/ia_storyboard_tracer.py` (same file, a distinct `scenario_*` function per the 16A precedent of `scenario_*` functions in one tracer module) | ❌ Wave 0 |
| APP-01 | Course shelf shows exact resume cue; a corrupted course still shows last valid overview + plain-file access | integration | `python tests/ia_route_roundtrip.py` | ❌ Wave 0 |
| APP-02 | Same deep links resolve identically wide and narrow; focus/scroll restoration | integration + manual-assist (narrow-width rendering is a visual check, deferred in substance to 17A but the route-identity assertion is automatable now) | `python tests/ia_route_roundtrip.py` | ❌ Wave 0 |
| APP-03 | First-run sample course/walkthrough reachable with no roots/agent/network; offline help routes by error code; settings expose the five new groups | integration | `python tests/ia_route_roundtrip.py` plus `python tests/config_roundtrip.py` (existing settings-validation file, extended) | Partial, `tests/config_roundtrip.py` exists `[VERIFIED: repo tests/ directory listing, this session]`; the first-run/offline-help fixture is Wave 0 |

### Sampling Rate

- **Per task commit:** the specific new `tests/*_roundtrip.py` or
  `tests/*_tracer.py` file the task's `<verify>` step names.
- **Per wave merge:** every new 16B test file plus the existing
  `tests/daemon_roundtrip.py` (route-table coupling checks) and
  `tests/config_roundtrip.py` (settings validation), since 16B touches both
  surfaces.
- **Phase gate:** full suite green before `/gsd-verify-work`, per this
  project's standing Nyquist validation setting (`config.json`
  `workflow.nyquist_validation: true`).

### Wave 0 Gaps

- [ ] `tests/ia_storyboard_tracer.py`, covers FLOW-01, FLOW-02 (loop A-G
      interruption scenarios; model-unavailable degrade scenario)
- [ ] `tests/ia_route_roundtrip.py`, covers APP-01, APP-02, APP-03 (course
      shelf, deep-link/anchor resume, first-run/offline-help)
- [ ] `tests/mode_layer_roundtrip.py`, covers the mode-layer precedence
      table's conflict-resolution behavior (supports the ROADMAP Phase 16B
      goal clause on mode layering; shared with 16C's STRATEGY-02 fixture,
      see Open Question 3)
- [ ] `tests/degraded_state_roundtrip.py`, covers the crash/cancel/offline/
      permission-denied/future-schema/agent-unavailable matrix
- [ ] `fixtures/course_storyboard_corpus.py`, shared synthetic fixture
      generator all four new test files above draw from, following
      `fixtures/corpus_14a.py`'s generator-into-caller-directory shape
- [ ] Framework install: none, stdlib only, no new dependency to install

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | This is a single-learner local product with no accounts (`.claude/CLAUDE.md` "Users" constraint); 16B adds no login surface. |
| V3 Session Management | Partial | The existing loopback-token gate (`X-Itembank-Token`, injected by the Tauri shell proxy) already covers session/route access `[VERIFIED: STATE.md:452-454, "13-01: token gate covers every route except /__itembank__"]`; any new 16B route must be added to that same gate, not exempted. |
| V4 Access Control | Yes | The mode-layer precedence table IS an access-control contract: runtime authority must never be overridden by a lower layer (learner preference, accommodation override, instructor policy) during a sitting. Standard control: server-side precedence resolution, never a client-settable override for the fixed layers. |
| V5 Input Validation | Yes | New `/api/*` routes (e.g. an Activity-resolve action) must validate their body fields against a fixed allowed-fields list, matching the shipped `DAY_EDIT_ALLOWED_FIELDS`/`SEED_ACCEPT_ALLOWED_FIELDS` precedent `[VERIFIED: surfaces/daemon.py:201-208]`, refusing any authority-shaped field (a raw filesystem path, a full-document replacement) before any helper runs. |
| V6 Cryptography | No | 16B introduces no new cryptographic operation; existing checksum/token mechanisms (updater, loopback token) are unchanged. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A new `/api/activity/*` route accepting an authority-shaped field (a raw path, an object id it should derive itself) | Elevation of Privilege | Fixed allowed-fields list per request shape, refused before any helper runs, following `SEED_ACCEPT_ALLOWED_FIELDS`'s pattern `[VERIFIED: surfaces/daemon.py:204-208]`. |
| Cross-origin write to a new mutating 16B route (Activity resolve, settings save) | Spoofing / Tampering | Reuse the shipped `_reject_cross_origin_write(handler)` same-origin check already applied to `handle_day_save` and other mutating routes `[VERIFIED: surfaces/daemon.py:1979-1986]`. |
| An Activity view leaking a journal entry's `before_image` bytes (which could contain assessment-relevant content) to the browser before it should be visible | Information Disclosure | The Activity route must render journal metadata (state, timestamps, object kind) and never serialize `before_image`/raw content bytes into the public JSON/HTML payload, mirroring `runtime.public_item()`'s public/private payload split. |
| A course-shelf resume cue or Activity job description echoing raw filesystem paths from outside the approved course roots | Information Disclosure | Follow the shipped `lesson.src_unreadable` precedent, which "echoes the bank-author-written basename, never a resolved absolute path" `[VERIFIED: STATE.md:405]`; any 16B path-bearing error copy applies the same discipline. |

## Sources

### Primary (HIGH confidence: read directly this session)

- `C:/Users/wayba/Downloads/CTF/itembank/.planning/REQUIREMENTS.md`, FLOW-01,
  FLOW-02, APP-01, APP-02, APP-03, RELIABILITY-01/02/03, AGENT-01/02/03,
  MAINT-01-04, GRAPH-03, ACTIVITY-01/02/03 (lines 519-993, 1240-1310)
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/ROADMAP.md`, Phase 16B
  section in full (lines 1906-1974), subphase table (lines 1975-2024)
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/PLANNING-DIRECTIVES.md` , 
  full file (§1-10, especially §2, §3, §4, §4a, §5, §8)
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/SOURCE-TO-COURSE.md`, full
  file
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/AGENT-WORKFLOW.md`, full
  file
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/UI-SPEC.md`, §8
  (Responsive/Offline/Accessibility, lines 580-603), §9-14 (lines 603-700),
  §15 (Source-to-course UI additions, lines 702-833)
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/PLAN-TEMPLATE.md`, full
  file
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/research/phase-16/14-synthesis.md`
 , sections 3, 4, 5, 8, 9, 10, 11, 15, 16 (lines 195-603, 913-1031)
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/16A-semantic-capability-activity-contract/16A-01-PLAN.md`
 , full frontmatter and Task 1 (lines 1-439)
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/16A-semantic-capability-activity-contract/16A-RESEARCH.md`
 , lines 1-130
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/14A-identity-lifecycle-operation/14A-01-PLAN.md`
 , lines 1-120
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md`
 , lines 1-140
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/phases/13.9-walking-skeleton/13.9-01-PLAN.md`
 , lines 1-90
- `C:/Users/wayba/Downloads/CTF/itembank/surfaces/daemon.py`, lines 195-334
  (ROUTES/API_ROUTES/ROUTE_CLI/SURFACE_PARITY), 939-964 (handle_index),
  1118-1145 (handle_settings_get), 1965-1990 (handle_day_index,
  handle_day_save)
- `C:/Users/wayba/Downloads/CTF/itembank/surfaces/settings.py`, lines 1-40
- `C:/Users/wayba/Downloads/CTF/itembank/schemas/settings.schema.json` , 
  top-level `properties` keys, read via `python -c "json.load(...)"`
- `C:/Users/wayba/Downloads/CTF/itembank/.claude/CLAUDE.md`, full file
  (project instructions block in this session's system context)
- `C:/Users/wayba/Downloads/CTF/itembank/.planning/STATE.md`, lines 1-470
  (decisions log, phase-6.2/13-01 route/gate precedents)
- Repository root directory listing (`ls *.py`) and phase directory listings
  for 14A, 16A, 13.9, 16B, run directly this session via Bash

### Secondary (MEDIUM confidence)

- None used beyond the primary sources above; no web search was required for
  this phase because every open question resolves against in-repo binding
  documents and shipped code.

### Tertiary (LOW confidence)

- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, no new dependency; stdlib-only extension of shipped
  modules, verified by direct read.
- Architecture (IA/route patterns): HIGH for the parts extending shipped
  `surfaces/daemon.py`/`settings.py` (read directly this session); MEDIUM for
  the parts composing planned 14A/16A signatures (read from plan text only,
  per the same caveat 16A-RESEARCH.md itself carries).
- Mode-layer contract and degraded-state matrix: MEDIUM, the seven-layer
  table and the seven-state matrix are quoted verbatim from
  `research/phase-16/14-synthesis.md`, an accepted synthesis document, but
  their enforcement mechanism inside 16B's own new code is this research's
  synthesis (`[ASSUMED]`) pending the planner's checkpoint decisions.
- Pitfalls: HIGH, every pitfall traces to a specific requirement clause, a
  specific shipped-code precedent, or a specific line in 16A's own precondition
  check that establishes the pattern 16B must extend.

**Research date:** 2026-08-15
**Valid until:** Re-verify before 16B execution if either `14A-FREEZE.md` or
`16A-FREEZE.md` comes into existence between this research and plan execution
,  at that point every plan-text-sourced claim in this document must be
re-checked against the real frozen surface, following the exact discipline
16B-01's own precondition check (Pattern 1 above) is designed to enforce. If
neither freeze record exists yet, this research remains valid (nothing it
depends on has changed). Treat as valid for 30 days absent a freeze event.
