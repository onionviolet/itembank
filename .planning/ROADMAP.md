# Roadmap: itembank — AI-taught learning platform

## Overview

This is a brownfield extension of a working, stdlib-only Python protocol and
runtime. Nothing here rewrites the four existing layers (`model` / `runtime` /
`server` / `surfaces`); every phase extends them under the same one-scorer,
one-parser rules, with format changes staying additive throughout. The journey
starts by rebuilding the ground everything else stands on — stable item
identity and one evidence store, migrated from the three stores that exist
today — because every later phase reads or writes against it, and building
trends, scheduling, or the auditor before it means building them twice. Once
that root is closed and demoable, work fans out into genuinely parallel
tracks the research identified with no dependency on the evidence spine:
daemon route plumbing and settings scaffolding, the `LESSON` grammar and
reader, surface theming and `day` editing, and the `check` item type's core
logic and editor. Those tracks converge on the teaching loop — the
deterministic hint ladder and per-mode feedback policy, then session
selection, then the model adapter that lets a tutoring model see the key and
write about a learner's *specific* wrong answer while the runtime, not the
model, decides which tier it may speak at. The subject-invariant loop across
EMT, Math, and CS is the integration checkpoint that proves all three prior
tracks actually cohere into one loop. Retention, pacing, and trend-driven
selection come next, feeding on real evidence history. The closed authoring
loop and the curriculum auditor come deliberately late: the auditor is the
highest-risk subsystem in this milestone, and its phase carries the pitfall
guard rails — citation-per-coverage-claim, a second quality gate beyond
`lint`, one-item-per-commit reversibility, graduated autonomy — as acceptance
criteria, not follow-on hardening. Packaging and self-update were originally
sequenced to close the milestone but were pulled forward to Phase 2.1 (see
"Phase Numbering" below) so a double-clickable artifact of the Phase 1+2
feature set exists early, and the self-updater ships every phase after it as
a real release rather than being written and tested last. GIFT export moved
with it.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Evidence Spine & Protocol Foundation** - Stable item identity, one evidence store, and migration so nothing built after this reads a stale or split history. (completed 2026-08-07)
- [x] **Phase 2: Daemon Consolidation & Settings Foundation** - One daemon on one port serving every surface, with a printable, agent-discoverable settings schema. (completed 2026-08-08)
- [ ] **Phase 2.1: Packaging, Self-Update & Interop Export (INSERTED, moved from Phase 12)** - One double-clickable artifact per OS, a safe self-updater, and a GIFT export that fails loudly rather than wrong — pulled forward so a runnable exe of the Phase 1+2 feature set exists early, and the self-updater ships phases 3-11 as real releases instead of being written and tested last.
- [ ] **Phase 3: Lesson Format & In-App Reader** - An optional `LESSON` section renders as reading material inside the app, linked to the items it teaches.
- [ ] **Phase 4: Surface Redesign & Theming** - One shared palette, OS-driven theming, a decluttered question surface, and safe in-page `day` editing.
- [ ] **Phase 5: Check Item Type & Code Editor** - A `check` item type runs the learner's own code in a real editor and scores it through the one scorer.
- [ ] **Phase 6: Hint Ladder, Cursor-Hold & Feedback Modes** - A wrong answer holds the cursor, hints unlock one authored tier at a time, and feedback behavior follows session mode.
- [ ] **Phase 7: Selection Engine** - Sessions are assembled by an inspectable rule engine — objective, difficulty, discrimination pairs, no accidental repeats.
- [ ] **Phase 8: Model Adapter Interface & Tier-Gate Enforcement** - The tutoring model sees the key and writes hints about the learner's actual error; the runtime gates the tier, not the model.
- [ ] **Phase 9: Subject-Invariant Loop — EMT, Math, CS Integration** - One loop — lesson, hint, verify — carries a learner through EMT prose, Math LaTeX, and runnable CS code.
- [ ] **Phase 10: Retention, Pacing & Trends** - What's due today, a daily cap, and evidence-driven selection weight and decay flagging, with itembank's and Anki's "due" shown apart.
- [ ] **Phase 11: Closed Authoring Loop & Curriculum Auditor** - A closed spec-draft-lint-retry authoring loop, reused by a syllabus auditor that cites its coverage claims and never over-autonomizes silently.
- [ ] ~~**Phase 12: Packaging, Self-Update & Interop Export**~~ - MOVED to Phase 2.1 (2026-08-07) — see Phase 2.1 above. Slot retired, not reused.

## Phase Details

### Phase 1: Evidence Spine & Protocol Foundation

**Goal**: Every session the learner sits produces evidence that survives item edits, bank migrations, and repeated submissions, in one auditable store instead of three.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: EVID-01, EVID-02, EVID-03, EVID-04, EVID-05, EVID-06, EVID-07, EVID-08, PROTO-01, PROTO-02, PROTO-03, PROTO-04, PROTO-05
**Success Criteria** (what must be TRUE):

  1. A learner can edit an item's stem after it has been linted once, and a query for that item's evidence history still resolves to the same objective/response trail — item identity survives a legitimate content edit.
  2. Running the one-time migration against existing `_attempts/*.md`, session JSON, and `daily_log.md` produces a single evidence store with no recorded response lost, verified by comparing pre- and post-migration counts.
  3. Submitting the same response twice to the same item within the same attempt records one accepted response, and the tool states which happened (recorded vs. already-recorded).
  4. A single query answers "how am I doing on objective X over time" across every session and subject, reading from the unified store alone.
  5. An agent with no repository context can read published schema versions for items, sessions, responses, and reports, and `lint` emits a machine-readable error code plus the offending field alongside the human-readable text.

**Open decisions resolved here**: Item identity scheme — **resolved at plan time as an opaque 12/16-hex `[ID:]` stored in the bank markdown with a separate `[HASH: sha256:...]` content fingerprint used only for drift detection (D-01/D-02); landed in plan 01-04.** Windows append-write durability for the event log — **resolved as an advisory lock (`msvcrt.locking` / `fcntl.flock`) held across exactly one `os.write()` per event, measured on the target machine by plan 01-01's blocking spike and recorded in `01-SPIKE-RESULT.md` before any plan appends a real event.**
**Plans**: 11/11 plans executed

Plans:
**Wave 1**

- [x] 01-01-PLAN.md — Windows append-durability spike and the locked log primitive

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-02-PLAN.md — TRACER: one submitted response reaches the log and comes back out of it

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 01-03-PLAN.md — Machine-readable lint errors with dotted codes and `lint --json`

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 01-04-PLAN.md — Item identity: content fingerprint, `id-assign`, drift warning

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 01-05-PLAN.md — Schema versions everywhere, the session upgrade seam, and the five published contracts

**Wave 6** *(blocked on Wave 5 completion)*

- [x] 01-06-PLAN.md — Minimal stdlib schema validator, `itembank schema`, and the CI contract gate

**Wave 7** *(blocked on Wave 6 completion)*

- [x] 01-07-PLAN.md — Idempotent submission, attempt numbering, and compensating retractions

**Wave 8** *(blocked on Wave 7 completion)*

- [x] 01-08-PLAN.md — Disposable sqlite3 index and the cross-subject objective query

**Wave 9** *(blocked on Wave 8 completion)*

- [x] 01-09-PLAN.md — Attempt file and session JSON become renders; marking becomes a batch command

**Wave 10** *(blocked on Wave 9 completion)*

- [x] 01-10-PLAN.md — `serve` and `day` become callers; `daily_log.md` becomes a render

**Wave 11** *(blocked on Wave 10 completion)*

- [x] 01-11-PLAN.md — Migration: the three legacy stores import with reconciled counts

### Phase 2: Daemon Consolidation & Settings Foundation

**Goal**: The learner opens one process on one port for everything — sitting, studying, the day view, reports, and settings — and every capability in it also has a CLI command.
**Mode:** mvp
**Depends on**: Nothing (parallel-eligible with Phase 1)
**Requirements**: SURF-01, SURF-03, SURF-04, DEL-04, DEL-05
**Success Criteria** (what must be TRUE):

  1. Starting the daemon once serves `/`, `/quiz/<bank>`, `/study/<bank>`, `/report`, `/api/*`, and the day view from one port, replacing the need for a server per subcommand.
  2. Starting the daemon a second time does not fight over the port, and `--lan` still reaches a phone on the same wifi.
  3. For every route exercised in a manual pass, an equivalent CLI command exists and reaches the same result through the same runtime call, not a second implementation.
  4. `itembank config` prints the current settings schema (theme, daily cap, selection weights, auditor autonomy, model backend, update policy) the way `spec` prints the format contract, and setting an invalid value is rejected with a named error.

**Plans**: 6/6 plans executed

Plans:
**Wave 1**

- [x] 02-01-PLAN.md — TRACER: one daemon, one port, one bank's quiz end to end, plus the `/` index

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 02-02-PLAN.md — Study, day and day-mutation routes; `serve`/`day` demoted from server owners to daemon launches
- [x] 02-03-PLAN.md — Settings foundation: `itembank.json`, its schema, numeric bounds in the validator, and `itembank config`

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 02-04-PLAN.md — `/api/start|next|submit|report` over the same runtime, identifier-addressed and `SystemExit`-contained

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 02-05-PLAN.md — The `/report` page: populated, in-progress, empty and not-found states

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 02-06-PLAN.md — Detect-and-attach singleton, `--lan`, and settings-driven daemon defaults

### Phase 2.1: Packaging, Self-Update & Interop Export (INSERTED, moved from Phase 12)

**Goal**: The learner double-clicks one file per OS to open itembank as an app, the tool can update itself safely, and a bank can leave itembank through GIFT without silently mangling anything GIFT can't express.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: DEL-01, DEL-02, DEL-03, DEL-06, DEL-07, DEL-08
**Success Criteria** (what must be TRUE):

  1. A double-clickable `.pyz` artifact plus a one-line launcher opens the app on Windows, macOS, and Linux, in a frameless window where available, falling back to an ordinary browser tab otherwise.
  2. The shipped artifact is still plain Python inside — a person or an agent can open and edit it without unpacking a build step.
  3. Checking for an update, downloading, and verifying a checksum leaves the currently-running process untouched; the new version lands at a side-by-side path and a relaunch hands off to it, never overwriting the running file.
  4. An update whose version is not strictly newer than the running version is rejected even if its checksum is valid, and a failed or offline check fails silently rather than blocking the page.
  5. GIFT export produces a file a real LMS importer accepts for expressible item types, and any item type GIFT cannot express fails loudly, by item number, rather than exporting silently wrong.

**Why inserted here (reasoning)**:

- No other phase's `Depends on` field named Phase 12 anywhere in the original roadmap — confirmed by inspection of all 12 phase entries. Its only real dependency, Phase 2, is complete (6/6 plans). Moving it up breaks no dependency chain.
- Packaging is architecture, not a one-time snapshot: the shipped artifact stays "plain Python inside... without unpacking a build step" (Success Criterion 2), so every later phase's code lands in the next `.pyz` rebuild automatically. Landing this phase early doesn't require redoing it once Phases 3-11 add code.
- The self-updater built here becomes the delivery path for every phase after it — Phases 3-11 ship through it as real releases, exercising it repeatedly, instead of it being written last and validated against nothing.
- User's explicit goal (2026-08-07): a valid, double-clickable exe of the current (Phase 1 + Phase 2) feature set, sooner than waiting for the full 12-phase milestone to close.

**Open decisions resolved here**: GitHub release-asset `digest` field format — **RESOLVED 2026-08-07 at plan time by a live request**: the asset object carries `digest` shaped as `sha256:` followed by 64 hex characters, and `tag_name` is a plain `vX.Y.Z` string. The parser is built on that shape, with the `SHA256SUMS.txt` asset kept as a redundant fallback for the null-digest case (plan 02.1-05).
**Plans**: 9/9 plans executed (2 gap-closure plans added 2026-08-08 from `02.1-VERIFICATION.md`)

Plans:
**Wave 1**

- [x] 02.1-01-PLAN.md — Tracer: one `.pyz` that actually runs (version constant, bundled-resource reader, `build.py`, Windows shim)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 02.1-02-PLAN.md — macOS `.command` and Linux `.desktop` shims, release bundle, README install section
- [x] 02.1-03-PLAN.md — Settings contract (`daemon.window`, `update` group, phase-number fix) and the frameless app window

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 02.1-04-PLAN.md — GIFT export: one escape function and the five expressible item types
- [x] 02.1-05-PLAN.md — Updater decisions: strictly-newer comparison, checksum verification, offline silence

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 02.1-06-PLAN.md — GIFT loud failures, `--strict`, and the real LMS import
- [x] 02.1-07-PLAN.md — Updater install: side-by-side landing, pointer manifest, relaunch handoff, `itembank update`

**Wave 5** *(gap closure — blocked on Wave 4 completion)*

- [x] 02.1-08-PLAN.md — CR-01: the update token stops at the redirect, and only ever goes to GitHub

**Wave 6** *(gap closure — blocked on Wave 5 completion)*

- [x] 02.1-09-PLAN.md — CR-02/CR-03: a throttle that starts on the first check, and a first launch that discloses before it asks

### Phase 3: Lesson Format & In-App Reader

**Goal**: As a learner, I want to open the lesson an item is drawn from inside the app, so that I can read the teaching text and jump straight back to the question that tests it.
**Mode:** mvp
**Depends on**: Nothing (parallel-eligible with Phase 1, Phase 2)
**Requirements**: LESSON-01, LESSON-02, LESSON-03, LESSON-04, LESSON-05, LESSON-06
**UI hint**: yes
**Success Criteria** (what must be TRUE):

  1. A bank carrying a `LESSON` section with `LESSON-REF`-tagged items renders the lesson as reading material in the app, with a working link from the lesson to each item that references it.
  2. A bank with no `LESSON` section still parses and renders byte-identically to how it does today — the compatibility floor holds.
  3. `lint` fails with an actionable message, by item number, when a `LESSON-REF` names a heading that does not exist — never a render-time crash.
  4. `spec` documents the `LESSON`/`LESSON-REF` grammar well enough that an authoring agent with no source access can write a valid lesson on the first try.

**Plans**: 6/6 plans executed

Plans:
**Wave 1**

- [x] 03-01-PLAN.md — TRACER: one lesson, one reference, rendered at `/lesson/<bank>` and linked both ways

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 03-02-PLAN.md — Shared lesson source `[LESSON-SRC:]` with path containment and a degraded reader state

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 03-03-PLAN.md — Lint: four codes, two CI couplings, one REQUIREMENTS reconciliation

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 03-04-PLAN.md — The renderer's real markdown scope and the Phase 9 fenced-code seam

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 03-05-PLAN.md — CLI twin completeness: `--ref` filtering and the output contract

**Wave 6** *(blocked on Wave 5 completion)*

- [x] 03-06-PLAN.md — `spec` documents the grammar, plus the phase gate

### Phase 4: Surface Redesign & Theming

**Goal**: Every surface reads from one visual system, the accent colour follows the learner's OS choice, and `day` supports safe in-page editing instead of round-tripping through Obsidian.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: SURF-02, SURF-05, SURF-06, SURF-07, SURF-08, SURF-09
**UI hint**: yes
**Success Criteria** (what must be TRUE):

  1. The question surface shows one sticky context line in place of the current five chrome bands, with a real typographic hierarchy for the stem.
  2. `study` renders the per-option rationale, second-best, and notes fields it currently discards, matching what the quiz surface already shows.
  3. Quiz, study, and `day` all read from one shared palette — `day` no longer carries its own literal-hex stylesheet — and the browser page holds no key and performs no scoring of its own; every verdict comes back from `/api/*`.
  4. The accent colour is set from an OS colour picker, with light/dark pairs computed, contrast-checked, and correct/incorrect kept colour-blind safe.
  5. Editing a `day` plan in-page under an optimistic-concurrency guard does not silently overwrite an edit made in Obsidian at the same time — the conflict is surfaced, not lost.

**Plans**: 5/6 plans executed

Plans:

**Wave 0 — validation foundation, then the first production tracer**

- [x] 04-01-PLAN.md — Phase-wide executable test harness, then API-authoritative quiz tracer and accessible one-line hierarchy

**Wave 1** *(blocked on 04-01 Wave 0 foundation/tracer)*

- [x] 04-02-PLAN.md — Exact-span day document grammar, revisions, atomic save, and CLI proof

**Wave 2** *(blocked on 04-02)*

- [x] 04-03-PLAN.md — Additive source-accent schema, accessible palette derivation, and guarded native picker

**Wave 3** *(blocked on 04-01 and 04-03)*

- [x] 04-04-PLAN.md — Semantic presentation adapter, settings UI, and shared palette for index/report/quiz

**Wave 4** *(blocked on 04-04)*

- [x] 04-05-PLAN.md — Complete progressive study explanations, deliberate-reveal accessibility, and study palette migration

**Wave 5** *(blocked on 04-02, 04-04, and 04-05)*

- [ ] 04-06-PLAN.md — Structured day browser editing, day palette migration, conflict recovery, and one-use force confirmation

### Phase 5: Check Item Type & Code Editor

**Goal**: A learner can write and run their own code against a `check` item, in a real editor, and get a dichotomous verdict through the same scorer as every other item type; the item also establishes the reusable interaction contract future visual manipulatives will use.
**Mode:** mvp
**Depends on**: Nothing (parallel-eligible with Phase 1; coordinate `model.py`/`runtime.py` diffs with Phase 1)
**Requirements**: CODE-01, CODE-02, CODE-03, CODE-04, CODE-05
**UI hint**: yes
**Success Criteria** (what must be TRUE):

  1. A learner types code into a monospace field with working line numbers and a tab key that inserts a tab rather than moving focus.
  2. Submitting `check` code runs it, compares output against multiple expected test cases (not one hardcoded string), and reaches its verdict through `runtime.score_response()` like every other item type.
  3. Code that loops forever is killed at the timeout on both Windows and POSIX, including any child process it spawned — verified with a grandchild-spawning test case.
  4. `spec` and any UI copy state plainly that this stops accidents, not deliberate escapes, with no claim of sandboxing anywhere in the documentation.
  5. The editor is the first proof of a renderer-independent interactive-item contract: validated configuration enters the renderer, a meaningful structured response leaves it, `runtime.score_response()` alone returns the verdict, and an accessible non-pointer interaction reaches the same response shape.

**Plans**: 7 plans

Plans:

- [ ] 05-01-PLAN.md — Tracer: one `check` item end to end — parse, run, score, record (wave 1)
- [ ] 05-02-PLAN.md — Execution bounds: output cap, Windows Job Object kill, grandchild test (wave 2)
- [ ] 05-03-PLAN.md — Settings group, the agent submit path, and the default-closed LAN refusal (wave 2)
- [ ] 05-04-PLAN.md — Windows process-tree kill: manual verification and spike record (wave 3)
- [ ] 05-05-PLAN.md — The code editor: field, gutter, Tab/Shift-Tab, honest-limits line (wave 3)
- [ ] 05-06-PLAN.md — Per-case result matrix and the three refusal states (wave 4)
- [ ] 05-07-PLAN.md — Honest-limits gate, README, item schema, end-of-phase pass (wave 5)

### Phase 6: Hint Ladder, Cursor-Hold & Feedback Modes

**Goal**: A wrong answer holds the session open for a real second attempt, hints unlock one authored tier at a time, and feedback behavior changes correctly by session mode.
**Mode:** mvp
**Depends on**: Phase 1, Phase 3
**Requirements**: TEACH-01, TEACH-02, TEACH-03, MODE-01, MODE-02, MODE-03, MODE-04, MODE-05, MODE-06
**Success Criteria** (what must be TRUE):

  1. Submitting a wrong answer holds the cursor on that item instead of advancing, and a `hint` command/route returns tier 0 (lesson pointer), then 1 (objective), then 2 (trap), then 3 (rationale for the picked option), then 4 (discriminator), then 5 (reveal) — one new tier per call, never skipping ahead.
  2. `report` distinguishes an item answered correctly at tier 1 from one answered correctly at tier 4, reading `hints_used` recorded per response.
  3. Sitting the same bank in drill mode reveals the answer and explanation immediately on a wrong response and advances; in practice mode the ladder runs with the cursor held; in diagnostic mode nothing is shown until the sitting ends; in exam mode nothing is shown until the attempt file is marked.
  4. Every response records which mode produced it, so a "correct" from drill mode is distinguishable from a "correct" from exam mode in the evidence.
  5. Rapidly resubmitting the same or an empty answer does not advance the hint tier faster than one tier per genuine attempt.
  6. A lesson can interleave a short explanation with a learner action, prediction, or attempt before revealing the next idea; feedback addresses the learner's move, and hints guide without simply handing over the answer.

**Plans**: 2 plans

Plans:

**Wave 1**

- [ ] 06-01-PLAN.md — Runtime-owned feedback policy, append-only hint evidence, and derived teaching outcomes

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 06-02-PLAN.md — CLI, identifier-addressed API, and browser clients over the one policy

### Phase 06.1: Interactive Visual Assessment Protocol (INSERTED)

**Goal:** A learner can manipulate a plot or number line and receive deterministic, runtime-governed feedback while a teaching agent observes meaningful actions and state instead of pixels, without receiving the answer or scoring authority.
**Depends on:** Phase 4, Phase 5, Phase 6
**Requirements:** VIS-01, VIS-02, VIS-03, VIS-04, VIS-05, VIS-06, VIS-07, VIS-08, VIS-09
**UI hint:** yes
**Approved phase contracts:** `06.1-CONTEXT.md` reconciles the prior locked research/UI decisions. `06.1-01` and `06.1-02` are `UPSTREAM-CONTRACT` / `UI-INDEPENDENT`; `06.1-03` learner-renderer work is `UI-BLOCKED` on `.planning/phases/06.1-interactive-visual-assessment-protocol/06.1-UI-SPEC.md` and the shared `.planning/UI-SPEC.md`.
**Success Criteria** (what must be TRUE):

  1. One versioned `visual` item protocol declaratively describes `plot` and `numberline` interactions; `spec`, the published schema, named lint errors, and synthetic golden fixtures let an authoring model create and diagnose items without reading renderer source, and bank-authored JavaScript is refused.
  2. Plot and number-line items render through one SVG-plus-semantic-HTML adapter and serialize the same domain response for mouse, touch, keyboard, and the non-drag HTML control path; the first slice uses no canvas.
  3. The served public payload contains the scene, initial state, allowed semantic actions, response grammar, and accessibility text, but never accepted states, tolerance, misconception mapping, reveal content, or solution paths.
  4. `runtime.score_response()` alone normalizes fixed grid/rational units, applies the private versioned tolerance policy at its exact boundaries, and returns a dichotomous verdict; viewport size, zoom, device-pixel ratio, and renderer rounding cannot change the result.
  5. Committed learner actions, runtime observations, final semantic state, error category, opaque feedback anchor, and Phase-6-bounded hint entitlement are append-only evidence that a later teaching agent can query; raw pointer movement is neither accepted nor stored.
  6. The visual interaction works at 320 CSS px and 200% zoom with visible focus, status announcements, 24x24-or-larger pointer targets plus a non-drag alternative, pointer cancellation, and equivalent keyboard operation. Canvas remains reserved for a future dense simulation and may never replace the semantic HTML state/control fallback.
  7. GIFT export refuses every visual interaction loudly by item number and `gift.type_unsupported`; Canvas LMS/LTI, QTI export, advanced visual families, hosted identity, and grade passback remain backlog work.

**Benchmark posture:** Brilliant is an explicit learn-by-doing quality target. Public patterns from Brilliant, Desmos/Amplify, GeoGebra, Khanmigo, H5P/QTI, and ALEKS inform prediction-before-explanation, meaningful manipulation, immediate targeted feedback, transparent state, accessibility, and authorability. This phase does not copy proprietary content, interaction details, branding, or pursue competitor feature parity.
**Plans:** 3 plans

Plans:

**Wave 1**

- [ ] 06.1-01-PLAN.md — TRACER: one declarative plot path, then the shared plot/number-line protocol and deterministic runtime scorer

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 06.1-02-PLAN.md — Model-authoring contract, named lint/schema/golden fixtures, and semantic action/observation evidence API

**Wave 3** *(blocked on Waves 1 and 2 completion)*

- [ ] 06.1-03-PLAN.md — Accessible mouse/touch/keyboard equivalence, canvas fallback boundary, GIFT loud refusal, and phase gate

### Phase 7: Selection Engine

**Goal**: A session is assembled by rule, not by hand — targeted at an objective, a difficulty, or a discrimination pair — and the tool can say why it picked each item.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: SEL-01, SEL-02, SEL-03, SEL-04, SEL-05
**Success Criteria** (what must be TRUE):

  1. A session can be requested filtered by objective, prerequisite, item type, and difficulty, and the returned set matches the filter.
  2. Diagnostic, practice, remediation, and exam selection modes each produce a session whose composition visibly differs in a way that matches the mode's purpose.
  3. Items just answered in the current session are not immediately re-served in the same or the next session, verified across a resumed session.
  4. Requesting a discrimination pair for a named confusion serves both commonly-confused items together.
  5. For any selected item, the tool can state in plain terms why it was chosen over another candidate.
  6. A guided path can sequence prerequisites into bite-sized concept steps with periodic application checkpoints, while keeping the selector's reasons visible and rule-based.

**Open decisions resolved here**: The selection-mode naming collision — resolved at plan time as a **distinct `selection_mode` field** (D-11), because `schemas/session.schema.json`, `schemas/response.schema.json` and `surfaces/daemon.py:SESSION_MODES` already enumerate `"remediation"` as a *feedback* mode; gated by a blocking `checkpoint:decision` in plan 07-04 because the evidence log is append-only. What the log records about a selection — resolved as a **`selection` event once per sitting plus `selection_mode` on every response event** (D-03), also gated in 07-04. Cooldown scope — resolved as **bank-scoped** (D-13), paid for by bumping `INDEX_VERSION` and adding a `bank` column to the disposable sqlite3 index in plan 07-03. `selection_weights.recency_decay` — resolved as **being** D-08's soft penalty rather than a second knob for the same thing (D-15), with `objective_miss_rate` and `difficulty_spread` retagged to Phase 10.
**Plans**: 6 plans

Plans:
**Wave 1**

- [ ] 07-01-PLAN.md — TRACER: one selector, one objective, one trace with a named runner-up, reached by the CLI and `/api/start`

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 07-02-PLAN.md — `[PAIR:]` and `[PREREQ:]` in the format contract, their two lint codes, and the pair/prerequisite filters
- [ ] 07-03-PLAN.md — Bank-scoped exposure: `INDEX_VERSION` 2, a `bank` column, wider history rows, `itembank evidence --bank`

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 07-04-PLAN.md — The two one-way doors: a distinct `selection_mode` field, and the recorded selection spec on the session and in the log

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 07-05-PLAN.md — The four mode compositions in one table, the hard/soft exposure split, and the `selection` settings group

**Wave 5** *(blocked on Wave 4 completion)*

- [ ] 07-06-PLAN.md — `itembank select --explain`, `/api/start` preview, named profiles, and `schemas/selection.schema.json`

### Phase 8: Model Adapter Interface & Tier-Gate Enforcement

**Goal**: The tutoring model reads the key and the learner's specific wrong answer and writes a hint about that error, but the runtime — not the model — decides which tier it may speak at, and a hint that reaches past that tier never renders.
**Mode:** mvp
**Depends on**: Phase 1, Phase 6
**Requirements**: TEACH-04, TEACH-05, TEACH-06, TEACH-07, TEACH-08, TEACH-09, MODEL-01, MODEL-02, MODEL-03, MODEL-04, MODEL-05
**Approved phase contracts:** `.planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-UI-SPEC.md` and `08-AI-SPEC.md`. Adapter/tier/evidence work is upstream; generated learner support remains blocked on implementation of the Phase 6 tier/fact seam and green adversarial gate evidence.
**UI contract**: `UI-DEPENDENT` — adapter and deterministic tier-gate work may proceed as an upstream contract; learner-facing model status, provenance, uncertainty, and generated-hint surfaces must validate against `.planning/UI-SPEC.md` before completion.
**Success Criteria** (what must be TRUE):

  1. Given an item, its key, rationale, and the learner's actual wrong answer, the model produces a hint about that specific error at the tier the runtime currently permits and no further — verified by a case where the model is prompted (adversarially) to reveal more, and the output is dropped rather than shown.
  2. Switching the configured model backend between a hosted CLI and a local OpenAI-compatible endpoint is a one-line config change with no code change, and both paths produce the same response shape.
  3. With the network unplugged (or the model unreachable), sitting a quiz, scoring, lessons, the authored hint ladder, evidence, and reports all keep working — only the model-generated tier of hinting goes quiet.
  4. Marking a `short` answer against its rubric through the adapter lands each rubric point as `review_state: pending`, never as accepted evidence, until an explicit accept.
  5. Every model interaction — a hint given, a rubric suggestion — is logged to the evidence store and retrievable later by session.

**Open decisions resolved here**: Tier-gate enforcement mechanism — no prior art found for how the runtime detects and drops model output that reaches past the unlocked tier; this phase must design and test the actual detection/stripping mechanism as a first-class deliverable, not adapter plumbing added after the fact.
**Plans**: TBD

### Phase 9: Subject-Invariant Loop — EMT, Math, CS Integration

**Goal**: One loop carries a learner through EMT prose, Math with rendered LaTeX, and CS with runnable code, proving the loop is subject-invariant rather than three separate tools wearing the same theme.
**Mode:** mvp
**Depends on**: Phase 3, Phase 5, Phase 6
**Requirements**: LOOP-01, LOOP-02, LOOP-03, LOOP-04, LOOP-05
**UI hint**: yes
**UI contract**: Mixed. `09-01` and `09-02` are `UPSTREAM-CONTRACT` with UI-dependent public status/semantic-table checks; `09-03` is `UI-INDEPENDENT`; `09-04` and `09-05` are `UI-BLOCKED` and must implement `.planning/phases/09-subject-invariant-loop-emt-math-cs-integration/09-UI-SPEC.md` alongside the global `.planning/UI-SPEC.md` foundation.
**Success Criteria** (what must be TRUE):

  1. The same lesson-then-hint-then-check loop drives a session in each of the three subjects, with only the lesson medium, allowed item types, and verifier varying per subject.
  2. Math lessons and items render LaTeX correctly offline, from the vendored asset, with the network unplugged.
  3. A CS lesson embeds runnable code inline in its prose, and a learner can execute it from the reading view.
  4. An EMT lesson renders prose and tables correctly, matching the source markdown structure.
  5. Adding a fourth subject requires only a configuration entry (lesson medium, item types, verifier), not a new surface or a code fork.
  6. Each subject includes at least one guided-discovery sequence that cycles through context, learner action or prediction, immediate targeted feedback, and explanation instead of presenting a lecture followed by detached questions.

**Plans**: 5 plans across 4 waves

Plans:
**Wave 1**

- [ ] 09-01-PLAN.md - Persist one selected subject profile and prove the EMT tracer through the shared loop.

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 09-02-PLAN.md - Publish EMT/Math/CS profile configuration and prove a fourth subject requires configuration only.
- [ ] 09-03-PLAN.md - Approve one immutable KaTeX release before vendoring.

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 09-04-PLAN.md - Bundle and render offline Math through the shared reader under the Phase 9 UI contract.

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 09-05-PLAN.md - Add observation-only runnable lesson code and prove the four-profile integration matrix.

### Phase 10: Retention, Pacing & Trends

**Goal**: The tool tells the learner what's due today, stops a course being binged in one sitting, and raises or lowers what gets selected based on real performance history — with itembank's and Anki's notions of "due" shown as two labeled signals, never silently merged.
**Mode:** mvp
**Depends on**: Phase 1, Phase 7
**Requirements**: SCHED-01, SCHED-02, SCHED-03, SCHED-04, TREND-01, TREND-02, TREND-03, TREND-04, TREND-05
**Approved phase UI contract:** `.planning/phases/10-retention-pacing-trends/10-UI-SPEC.md`; derivation/evidence snapshots are upstream, while report/recommendation surfaces remain `UI-BLOCKED` on its verification gates.
**UI hint**: yes
**UI contract**: Mixed. Derivation and evidence-snapshot modules are `UPSTREAM-CONTRACT`; due-today, trend, recommendation, pacing, and evidence-inspection surfaces are `UI-BLOCKED` until they satisfy `.planning/UI-SPEC.md`.
**Success Criteria** (what must be TRUE):

  1. `day`'s cockpit shows what's due today per objective, computed from itembank's own evidence, alongside Anki's due/new counts as a separate, clearly labeled signal, both read from one shared per-render snapshot.
  2. A daily cap enforced through `day` blocks a course from being over-worked in one sitting, and Anki keeps owning card reviews — itembank writes no card schedule.
  3. An objective the learner keeps missing visibly raises its selection weight in the next session; one the learner has mastered drops out of rotation.
  4. An objective answered correctly a month ago and untouched since is flagged at-risk in the longitudinal `/report` view, before it would actually be failed.
  5. The longitudinal report shows accuracy by objective over weeks, hint tier reached, and items pending manual marking, and every trend shown states the evidence it rests on.
  6. Recommendations favor short, focused sessions and surface the learner's strategy, surprise, or sticking point as optional reflection evidence without turning streaks or points into the definition of mastery.

**Plans**: TBD

### Phase 11: Closed Authoring Loop & Curriculum Auditor

**Goal**: An agent can both draft a clean item end-to-end with no human relaying lint errors, and audit a syllabus against the bank for coverage gaps — reporting what it's unsure of as unsure, writing only through the same contract a human uses, and leaving every write reversible in one step.
**Mode:** mvp
**Depends on**: Phase 1, Phase 8, Phase 10 (loosely — only for weak-objective-pointing refinement)
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUDIT-01, AUDIT-02, AUDIT-03, AUDIT-04, AUDIT-05, AUDIT-06, AUDIT-07, AUDIT-08, AUDIT-09
**Approved phase contracts:** `.planning/phases/11-closed-authoring-loop-curriculum-auditor/11-UI-SPEC.md` and `11-AI-SPEC.md`; browser review/write surfaces remain `UI-BLOCKED`, and live-model authoring additionally requires green Phase 8 adapter evidence plus Phase 11 AI evaluation fixtures.
**UI hint**: yes
**UI contract**: Mixed. Ingestion, lint, citation, and coverage-engine work may proceed as `UPSTREAM-CONTRACT`; diff, preview, approval, reversible-write, uncertainty, and audit-queue surfaces are `UI-BLOCKED` until they satisfy `.planning/UI-SPEC.md`.
**Success Criteria** (what must be TRUE):

  1. One command runs the full authoring cycle — spec, draft, lint, feed errors back, retry to clean or to a cap — and writes the bank with no human relaying an error message; a model given no repository context can complete it from the contract alone, and cannot invent content beyond what it was asked to write.
  2. Ingesting a syllabus produces an objective-by-objective coverage report where every "covered" claim cites the exact syllabus passage and bank item(s) behind it, and anything uncitable is reported as unknown rather than covered.
  3. Every generated item passes `lint` before reaching a bank, and a second quality gate (distractor-overlap, near-duplicate stems, answer-leaking overlap, missing "would-be-correct" rationale) blocks a machine-authored item `lint` alone would pass.
  4. At report-only autonomy the tool only reports; at draft-and-approve a human accepts each item before it's written; at full autonomy each write is its own commit, distinctly tagged as machine-authored, and the tool states its own volume at the highest setting so batching isn't invisible.
  5. Every auditor write is undone by a single documented action (shadow copy or `git revert`), demonstrated once for a report-only-stage write and once for an autonomous one.

**Open decisions resolved here**: Second quality gate algorithm (distractor-overlap heuristic, near-duplicate detection thresholds); syllabus input formats (markdown/text only, vs. PDF/DOCX that stdlib parses poorly); auditor reversibility mechanism (shadow copy vs. a git commit per write, depending on whether the private bank directory is git-tracked). These three converge with the top pitfalls flagged for this subsystem — the citation contract, the second quality gate, and reversibility are novel mechanisms with no working precedent in any examined product, and need fresh design at plan time, not just implementation.
**Plans**: 5 plans across 4 waves

### Phase 12: ~~Packaging, Self-Update & Interop Export~~ (MOVED)

This phase's full content — goal, requirements, success criteria, open decisions — now lives at **Phase 2.1**, inserted after Phase 2 on 2026-08-07. This numbered slot is retired: do not plan or execute against "Phase 12" and do not reuse this number for new work.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12.
Phases 1, 2, 3, and 5 have no dependency on each other and are parallel-eligible per config
(`parallelization: true`); their `Depends on` fields, not their numbering, are the source of truth
for what can run concurrently.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Evidence Spine & Protocol Foundation | 11/11 | Complete    | 2026-08-07 |
| 2. Daemon Consolidation & Settings Foundation | 6/6 | Complete    | 2026-08-08 |
| 3. Lesson Format & In-App Reader | 6/6 | In Progress|  |
| 4. Surface Redesign & Theming | 5/6 | In Progress|  |
| 5. Check Item Type & Code Editor | 0/TBD | Not started | - |
| 6. Hint Ladder, Cursor-Hold & Feedback Modes | 0/TBD | Not started | - |
| 7. Selection Engine | 0/6 | Planned | - |
| 8. Model Adapter Interface & Tier-Gate Enforcement | 0/TBD | Not started | - |
| 9. Subject-Invariant Loop — EMT, Math, CS Integration | 0/TBD | Not started | - |
| 10. Retention, Pacing & Trends | 0/TBD | Not started | - |
| 11. Closed Authoring Loop & Curriculum Auditor | 0/TBD | Not started | - |
| 12. Packaging, Self-Update & Interop Export | 0/TBD | Not started | - |

## Backlog

### Phase 999.1: Advanced Visual Items and Canvas LMS Integration (BACKLOG)

**Goal:** Extend the Phase 06.1 visual protocol beyond plot and number line into advanced visual families, then expose the player inside Canvas LMS through an explicitly hosted, authenticated LTI surface.
**Requirements:** TBD
**Plans:** 0 plans

Future exploration should cover `hotspot`, `diagram`, `timeline`, `trace`, geometry/construction, and dense simulation-style responses, plus the hosting, identity, privacy, deep-linking, and grade-passback decisions required by LTI. Phase 06.1 owns the initial plot/number-line protocol, SVG/HTML slice, semantic evidence, and canvas-fallback rule. Renderers continue to receive validated configuration rather than bank-authored JavaScript, and Canvas/LTI must remain an adapter to the same local runtime/scorer rather than a second authority.

Plans:

- [ ] TBD (promote with $gsd-review-backlog when ready)
