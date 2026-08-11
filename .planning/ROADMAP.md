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

**Revision 2026-08-10 — research absorbed.** The 2026-08-09 research pass
(`.planning/RESEARCH-BRIEF-learning-platform-2026-08-09.md` §7, seven artifacts in
`.planning/research/`) changed four things about the shape above. First, content
became a phase: the research named content and adherence, not features, as the
real bottleneck, so **Phase 3.2 pulls seeding and import in front of Phase 5** and
every phase after it is judged against a real corpus. Second, the lesson grew
teeth — **Phase 3.1** adds the glossary, the memorizable block, and one written
style contract the linter enforces, and **Phase 6.2** turns reading into a gated
loop. Third, the differentiator became visible: the runtime's refusal renders as
structural state rather than model reluctance, because Socratic tutoring is now
commoditized at the prompt layer and only the visible lock distinguishes this from
a system prompt. Fourth, packaging returns as **Phase 13** on a keep-the-Python
verdict, because a port would temporarily create a second scorer.

Two more things were added deliberately and cheaply: **Phase 9.1** exports audio
drill packs, correcting a real mismatch the research found between a desktop app
optimized for authoring and consumption that is phone- and audio-shaped; and the
**Extensibility Rules** section below, which exists because absorbing a dozen
features across ten phases is only affordable if each one registers a strategy
instead of adding a branch. Nothing was renumbered. Every format change stays
additive, and every phase adding grammar owes a byte-identical no-op fixture.
Six rulings remain open for Weibao (brief §7.7); each is recorded on the phase it
blocks, and none of them blocks starting.

**Revision 2026-08-10 (round two) — lesson styles, tiered verdicts, file layout.**
The second research pass (`.planning/RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md`
§4, five artifacts in `.planning/research/2026-08-10-*.md`) is complete and folded in
here additively, with no renumbering. Four things changed shape. First, **lesson
style is plural and is a registry**: five styles ship, `expository` is the parent,
one file per style at `styles/<id>.md`, exactly one inheritance level, and adding a
sixth is a file — Phase 3.1 criteria 3a/3b stop being placeholders and carry the real
specification. Second, `??? for math` is answered: **Worked Example → Variation →
Formalization** (`math-worked`), with `math-explore` shipped alongside it per
Directive §3. Third, **two-file lesson layout is the default**, overridable per
subject profile (`lesson_layout`) — the prose separates, the item never does. Fourth,
and most consequential, the Extensibility Rules §8 tiered-verdict hypothesis is
**partially overturned**: strategies do not declare authority, because that hands
every strategy the power to decide and then asks it not to. Two registries of
**normalizers** feed the unchanged `score_response()`, and tier 3 is not a scorer
strategy at all. Rules §8 below is rewritten to the researched design. Rulings 7–10
are recorded on the phases they block; none blocks starting.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Evidence Spine & Protocol Foundation** - Stable item identity, one evidence store, and migration so nothing built after this reads a stale or split history. (completed 2026-08-07)
- [x] **Phase 2: Daemon Consolidation & Settings Foundation** - One daemon on one port serving every surface, with a printable, agent-discoverable settings schema. (completed 2026-08-08)
- [ ] **Phase 2.1: Packaging, Self-Update & Interop Export (INSERTED, moved from Phase 12)** - One double-clickable artifact per OS, a safe self-updater, and a GIFT export that fails loudly rather than wrong — pulled forward so a runnable exe of the Phase 1+2 feature set exists early, and the self-updater ships phases 3-11 as real releases instead of being written and tested last.
- [ ] **Phase 3: Lesson Format & In-App Reader** - An optional `LESSON` section renders as reading material inside the app, linked to the items it teaches.
- [ ] **Phase 3.1: Lesson Rich Blocks, Glossary & Style (INSERTED 2026-08-10)** - `## TERMS` + `[[term]]` hover glossary, `[!KEY]` memorizable blocks that round-trip to Anki, one `LESSON-STYLE.md` contract the linter reads, and the callout/figure/print render pass on Phase 4 tokens.
- [ ] **Phase 3.2: Seeding, Import & Provenance (INSERTED 2026-08-10)** - Content arrives before the features that consume it: Anki `.apkg` import, a human-approves-everything draft→lint→retry seeding loop, and the `[SRC:]`/`[OBJ:]`/`## SOURCES` provenance standard with paraphrase-not-transcribe lint.
- [ ] **Phase 4: Surface Redesign & Theming** - One shared palette, OS-driven theming, a decluttered question surface, and safe in-page `day` editing.
- [ ] **Phase 5: Check Item Type & Code Editor** - A `check` item type runs the learner's own code in a real editor and scores it through the one scorer.
- [x] **Phase 6: Hint Ladder, Cursor-Hold & Feedback Modes** - A wrong answer holds the cursor, hints unlock one authored tier at a time, and feedback behavior follows session mode. (completed 2026-08-10)
- [ ] **Phase 6.2: Executable Textbook Loop (INSERTED 2026-08-10)** - Prose, an inline check the learner must clear to continue, then spaced re-exposure of the same idea — the Execute Program / Runestone loop over the existing lesson, hint, and evidence machinery.
- [x] **Phase 7: Selection Engine** - Sessions are assembled by an inspectable rule engine — objective, difficulty, discrimination pairs, no accidental repeats. (completed 2026-08-11)
- [ ] **Phase 8: Model Adapter Interface & Tier-Gate Enforcement** - The tutoring model sees the key and writes hints about the learner's actual error; the runtime gates the tier, not the model.
- [ ] **Phase 9: Subject-Invariant Loop — EMT, Math, CS Integration** - One loop — lesson, hint, verify — carries a learner through EMT prose, Math LaTeX, and runnable CS code.
- [ ] **Phase 9.1: Audio Drill Export (INSERTED 2026-08-10)** - `itembank export audio` turns an objective into a stem→pause→key→why drill pack, so the commute is study time and the TTS engine is a config entry, not a dependency.
- [ ] **Phase 10: Retention, Pacing & Trends** - What's due today, a daily cap, and evidence-driven selection weight and decay flagging, with itembank's and Anki's "due" shown apart.
- [ ] **Phase 11: Closed Authoring Loop & Curriculum Auditor** - A closed spec-draft-lint-retry authoring loop, reused by a syllabus auditor that cites its coverage claims and never over-autonomizes silently.
- [ ] ~~**Phase 12: Packaging, Self-Update & Interop Export**~~ - MOVED to Phase 2.1 (2026-08-07) — see Phase 2.1 above. Slot retired, not reused.
- [x] **Phase 13: Desktop Packaging — Tauri Shell over the Python Sidecar** - A signed, installable desktop app whose inside is still the same Python runtime, because porting it would temporarily create a second scorer. (completed 2026-08-10)

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

### Phase 3.1: Lesson Rich Blocks, Glossary & Style (INSERTED 2026-08-10)

**Goal**: A lesson can define its own vocabulary, mark what must be memorized, and be held to one written style contract — so reading material teaches like a textbook instead of rendering like a text file, and every block it adds is scored, exported, or linted by machinery that already exists.
**Mode:** mvp
**Depends on**: Phase 3, Phase 4 (tokens)
**Requirements**: LESSON-07, LESSON-08, LESSON-09, LESSON-10, LESSON-11, LESSON-12, LESSON-13, LESSON-14, LESSON-15, LESSON-16, LESSON-17
**UI hint**: yes
**Research basis**: `.planning/research/2026-08-09-differentiators-d1-d2-d3.md` (D1/D2/D3 grammar — use verbatim as this phase's format contract), `2026-08-09-lesson-display-editor.md` Q1, `2026-08-09-visual-design.md`, brief §7.2 Q3/Q4/Q7 and §7.6.
**Round-two research: COMPLETE (2026-08-10)** — this phase is no longer blocked. R1 and R2 are answered in `.planning/RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md` §4.3, with full verdicts in `.planning/research/2026-08-10-lesson-style-catalogue.md` (styles) and `2026-08-10-style-registry-mechanics.md` (registry shape). Criteria 3a and 3b below are rewritten from those verdicts and are now specifications, not placeholders. R2 enforcement lands as criterion 3c; R5 file layout as criterion 7.
**Success Criteria** (what must be TRUE):

  1. A `## TERMS` block plus `[[term]]` references render as a hover gloss via the Popover API, degrade to a glossary appendix with no JavaScript, and pass through a runtime `glossable()` gate so a gloss can never leak a keyed answer; each lookup lands as a `term_lookup` event.
  2. A `[!KEY]` callout is a GitHub-compatible block with a minted `[ID:]`/`[HASH:]`, exports to Anki TSV with a `#guid` that round-trips on re-export, supports `{{cloze}}`, and emits `key_review` events Phase 10 can replay into scheduler state.
  3. A style file carries a prose voice zone the model reads and a `## Rules` pipe table the linter parses; the machine-checkable rules are implemented (round one found 18 — 8 errors, 10 warnings — for a single style), model-judged rules are declared `manual` and deferred to Phase 11, and a rule row claiming a lintable severity the linter does not implement is itself a lint error.
  3a. **Styles are plural, and the registry ships five.** In this order: `expository` (the parent every other style inherits from, cost zero), `worked-example`, `checked-prose` (Execute Program and Brilliant merged behind a `predict_first` flag and a prose budget — Directive §3 applied properly rather than shipping two near-identical styles), `artifact-first` (Bottom-Up ordering plus PRIMM pacing, which are orthogonal and compose), and `case-narrative` (last only because it depends on Phase 9's `## SCENARIO`). Four styles are **rejected with the no-cheap-fix reason named** and must not be revived without new evidence: Feynman (every rule it contributes is semantic, so the contract is uncheckable), cookbook (its weakness is its purpose — keep the Diátaxis split as a house rule instead), written Socratic (branching is a second parser per Directive §4.2, and unbranched it collapses into the rhetorical questions W7 already bans), and explorable explanations (per-lesson bespoke JavaScript is bank-authored executable code, which `VIS-01` and `UI-SPEC.md:609` refuse outright; it is also a second renderer against Directive §4.2, and the evidence base is thin). Two reclassifications: the atomic prompt sheet already ships as `[!KEY]` plus Anki export, and productive failure is not a style but the `predict_first` flag. Adding a sixth style is one file — no parser change, no lint-code change, no renderer change, proven by the Extensibility Rule 6 stub.
  3b. **The registry's mechanics are fixed.** One file per style at `styles/<id>.md`; exactly one inheritance level, and a `[STYLE-PARENT:]` naming anything other than `house` is a lint error. **House constrains the artifact, style constrains the sequence** — the test is that a rule is house-wide iff violating it would still be wrong in every other style. House rows carry a `lock` column encoding the five non-negotiables, which cannot be overridden by any style; that lock is what makes the registry safely model-writable. Selection precedence is **lesson, then bank, then subject profile, then house**. Two operations must never be conflated: `render_style` is runtime, model-free, and may only permute blocks that already exist; `restyle` is Phase 11, model-driven, human-gated, and produces a new file. The mechanically impossible transforms are named and the renderer must refuse them rather than approximate: expository→case-narrative, expository→Socratic, expository→worked-example, anything→Bottom-Up, and case-narrative→anything.
  3c. **Enforcement is three cost classes, not two.** Structural counts over the parsed heading tree and one shared lexical metrics pass both run on **every** lint; only discourse judgement defers to Phase 11. Structure is checkable because a style declares its section skeleton (the markdownlint MD043 pattern), which moves "worked examples precede variations" out of model-judged and into a deterministic count. Severity is **earned by construction**: `error` only for structural counts or author-controlled literal lists, and that is a ceiling a style may not raise. All eight of round one's error-severity rules survive. The check catalogue is **closed** — a style file may enable, disable, re-severity, and parameterize a check, but may never define one, because `LINT_CODES` is a published API and sprawl is the real scale risk. Every warning is calibrated against the Phase 3.2 corpus before shipping enabled, with its false-positive rate recorded; above roughly 20% it ships disabled by default. Local `<!-- style-ignore: -->` suppression must exist, because the failure mode is that an unsuppressable warning gets its whole category globally disabled; suppression counts are themselves a report that retires bad checks. A style `error` blocks a machine-authored write and never a human's `lint`. Budget: the whole style pass under 50ms for a 5000-word lesson, asserted by test.
  3d. **The authoring model does not receive the style file.** It receives **distilled imperatives, capped at seven, placed last in the prompt**, plus exactly one exemplar. Adherence collapses past roughly ten simultaneous instructions and shows a recency bias, so the cap and the position are the finding, not formatting taste. The `## Voice` prose zone is for the human and is never sent to a model.
  3e. **New blocks: one parse path, two additive entries.** `[!CHECK: <id>]` is the single new parse path — an inline placement anchor carrying no key and no scoring path, so `runtime.score_response()` is untouched. `[!EXAMPLE]` is a callout *kind* against the existing callout container, not a new block. `## SCENARIO` is owed by Phase 9 whether or not any style uses it and is not this phase's cost.

  4. Callouts, figures, print CSS (B4), and the Q1 reading measure/heading ramp render on Phase 4's token set with no new type sizes beyond the ones this phase adds to `theme.py`, and a bank using none of these blocks renders byte-identically to Phase 3 output.
  5. Every item carries an optional one-sentence lintable **Educational Objective** line (UWorld pattern), consumable later by selection, dedup, Anki export, and the auditor without any of them re-deriving it.
  6. The TERMS grammar reserves one optional ignorable `key=value` meta field (`zh=…`) so a bilingual reader is a later field-read, not a format break; nothing bilingual is built here.
  7. **(round two, R5) Two-file lesson layout is the default**, and the rule is **separate the prose, never the item**. The subject-profile field `lesson_layout: "separate" | "inline"` overrides it — EMT and Math separate, CS inline, because a Bottom-Up CS lesson *is* its exercises. The field governs scaffolding, the authoring prompt, and one warning; it adds **no parser, renderer, or scorer branch**. The brief's stated hash-drift worry was **false and was re-argued**: `content_fingerprint()` (`model.py:259-294`) excludes `lesson_ref`, `objective`, and every rationale field, so rewriting a lesson for style cannot drift an item hash in either layout. The real argument is concurrent writers — Phase 11 SC4 commits each autonomous write separately and SC5 demands one-action reversibility, which is impossible without hunk surgery when a style pass shares a file with seeding. `[LESSON-SRC:]`'s arrow runs many banks to one lesson and must not be reversed; reversing it imports the Canvas item-bank failure, where editing an answered item breaks the bank-to-quiz link. **Unit:** a lesson file is one chapter and one reading session, subdivided by `###` headings, which are the objective-sized, LESSON-REF-targeted generation unit. An item belongs to exactly one lesson, which is true by construction today. Migration is `itembank lesson split|inline` — pure text transforms, item chunks byte-identical, no id or hash reminted.

**Open decisions** (unresolved — see brief §7.7 and Research Brief 2 §4.4):

- **OPEN — ruling 13** (constraint audit F6): criterion 3b claims the `lock` column "is what makes the registry safely model-writable", while 3c ships `<!-- style-ignore: -->` suppression and lets a style "enable, disable, re-severity, and parameterize a check". A model-writable file plus suppression plus re-severity is a short path to §4.1 or §4.5 being demoted to a warning by an ordinary-looking authoring action. Three hardening sentences are owed at `/gsd-discuss-phase 3.1`: (1) the locked house rows are **code constants in the linter**, not rows read out of `styles/house.md`, which documents them and cannot define or remove them; (2) `<!-- style-ignore: -->` **cannot suppress a locked rule**, and attempting it is itself an error; (3) a style may not re-severity a locked rule in any direction, and `severity: off` on a locked id is `style.override_locked`. **Default if unruled: adopt all three.**
- **OPEN — ruling 1**: Adopt "Paper & Ledger" and vendor Source Serif 4 + iA Writer Quattro (both OFL), per the KaTeX license-review precedent? Blocks the font-vendoring task only; everything else in this phase proceeds either way.
- **OPEN — ruling 2**: 18px lesson-reader body vs the locked 16px `text-body` token.
- **OPEN — ruling 6**: Confirm "The Bottom Up" = Wienand-style runnable-artifact-first pedagogy (assumption logged in the subjects artifact).
- **OPEN — ruling 7** (also blocks Phase 9): `subject_profiles` is a *closed* object per `09-02-PLAN.md`, so adding `lesson_layout` (criterion 7) is a registry version bump unless it is folded into 09-02 before Phase 9 is planned. **Default if unruled: fold into 09-02.**
- **OPEN — ruling 8**: Is `[!KEY]` legal inside item rationales, or lesson-only? Changes the scope of `key.duplicate_id`. **Default if unruled: lesson-only.**
- **OPEN — ruling 9** (also blocks Phase 6.2): May `[!CHECK:]` reference an item in another bank? **Default if unruled: no — narrower now, additive later.**

**Named unknowns carried into planning** (Research Brief 2 §4.5 — record the gap, never a number):

- **`executeprogram.com` mechanics are secondhand.** The site is JS-rendered and could not be read directly; Brilliant publishes no pedagogy document; Feynman has no primary source at all. `checked-prose` rests on reconstructed mechanics.
- **The Runestone Parsons-to-`build` mapping is inference**, and `artifact-first`'s rank-4 placement partly rests on it. Falsify this early at plan time rather than after building.
- **The PreTeXt label-stability claim is inference** from the PreTeXt Guide; `runestone.academy` returned 403.
- **The seven-imperative prompt cap (3d) is extrapolated** from format-compliance research, not measured on pedagogical structure. Treat the cap as a starting value to measure, not a validated constant.
- **No trustworthy open-weight prose-quality benchmark exists**, so any model choice for lesson authoring must be settled by running our own 18-rule check over generated lessons.
- **There is no real bank yet**, so the criterion-7 layout argument is structural against Phase 11's criteria, not observed churn.

**Plans**: 3/7 plans executed across 3 waves

Plans:
**Wave 1**

- [x] 03.1-01-PLAN.md — Tokens + the one callout container; LESSON_TEMPLATE onto theme_css + SHARED_CSS + LESSON_CSS
- [x] 03.1-02-PLAN.md — TERMS glossary: parse_terms, glossable() gate, Popover gloss + appendix, term_lookup

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 03.1-03-PLAN.md — [!KEY] cards, Anki keys export with round-tripping #guid, key_review, Educational Objective privacy
- [ ] 03.1-04-PLAN.md — Style registry: five styles + house, LOCKED_RULE_IDS, render_style and the named refusals
- [ ] 03.1-05-PLAN.md — Style enforcement cost classes, suppression + 50ms budget, StylePrompt capped imperatives

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 03.1-06-PLAN.md — Font vendoring (Source Serif 4 + iA Writer Quattro), spec grammar documentation, lesson_layout fold into 09-02
- [ ] 03.1-07-PLAN.md — Phase verification: the eight UI-SPEC §17 gates, requirement-coverage audit, full suite

### Phase 3.2: Seeding, Import & Provenance (INSERTED 2026-08-10)

**Goal**: Real content is in the bank before the phases that consume it are built, and every piece of it can name where it came from — so Phases 5 through 11 are dogfooded against a real EMT/Math/CS corpus instead of synthetic fixtures, and nothing in the bank is a transcription of a copyrighted source.
**Mode:** mvp
**Depends on**: Phase 1, Phase 3
**Requirements**: SEED-01, SEED-02, SEED-03, SEED-04, SEED-05, SEED-06, SEED-07, SEED-08, SEED-09
**Research basis**: `.planning/research/2026-08-09-extraction-subjects-bilingual.md` (Q5), `2026-08-09-blind-spots.md` (B1, Q9, Q10). This is the milestone's largest roadmap change: the research named content and adherence, not features, as the real bottleneck, and no success criterion anywhere else measures actual use.
**Success Criteria** (what must be TRUE):

  1. An existing Anki `.apkg` imports into a bank through stdlib ZIP+SQLite reads alone, with a per-note report of what converted, what was skipped, and why — no note is silently dropped.
  2. A draft→lint→retry seeding loop produces items a human approves one at a time before anything is written; nothing in this phase writes to a bank without an explicit accept. Autonomy beyond that stays Phase 11's problem.
  3. `[SRC: <source-id> <locators>]` and `[OBJ: framework/objective-id]` resolve through an additive `## SOURCES` registry, and the objective coverage map is **computed on demand, never stored**, so it cannot go stale against the bank.
  4. Paraphrase lint errors at ≥8 consecutive copied words and warns above Jaccard 0.25, using stdlib winnowing over fingerprints only — the source text itself is never stored, which is also the defensible posture for AAOS-derivative EMT content.
  5. `[CASE:]` grouping is in the format contract (additive), so an NREMT-style case set is one authored construct that Phases 6 and 7 can serve as an exam-sim preset.
  6. `[PREREQ:]` prerequisite edges are authorable and linted here, ahead of Phase 7's fringe-based selection consuming them.
  7. A bank with none of `## SOURCES`, `[SRC:]`, `[OBJ:]`, `[CASE:]`, or `[PREREQ:]` parses and renders exactly as it does before this phase.
  8. **(round two, R3.4) Long-lesson generation runs as six stages, in this order**: deterministic source selection, outline-only, per-section drafting, **deterministic checks before any model critique**, independent CoVe-style verification, then human accept. The ordering is the finding — spending model calls critiquing a draft that a lint pass would have rejected is waste, and a model critiquing before the deterministic gate anchors on its own text. Roughly nine model calls per lesson, so **authoring is a batch operation and the UI must say so** rather than presenting it as interactive.
  9. **(round two, R3.4) The cheapest real anti-fabrication guard is a new `style.unsourced_specific` check**: numerals, units, and doses require a `[SRC:]`. This is a structural check, not a model judgement, and it lands here because seeding is where fabricated specifics enter the corpus.
  10. **(round two, R2.1/3.1-3c) This phase's corpus is the calibration set for every style warning.** A warning ships enabled only with a recorded false-positive rate measured against this corpus; above roughly 20% it ships disabled by default. Phase 3.1 owns the checks; this phase owns the evidence that any of them are usable.
  11. **(round two, R5) Seeding writes items; a style pass writes prose.** Because Phase 3.1 criterion 7 makes two-file the default, a seeding write and a style rewrite must not contend for the same file — which is what makes Phase 11's one-action reversibility possible without hunk surgery.

**Named unknowns carried into planning**: **no benchmark for single-objective adherence in long generation exists** as of mid-2026 (Research Brief 2 §4.5). Criterion 8's staging is a structural argument, not a measured improvement; do not carry a percentage figure for it into any plan.
**Sequencing note**: land this **before Phase 5**. Seeding is upstream of every phase that needs content to be judged against; building the check type, the hint ladder, or the selector first means tuning them against fixtures and re-tuning them against reality.
**Open decisions**:

- **OPEN — ruling 12** (constraint audit F3, revisit): SC1's *"through stdlib ZIP+SQLite reads alone"* is a relaxed preference baked into an acceptance criterion, and it may be **unmeetable** — Anki 2.1.50+ exports ship `collection.anki21b` zstd-compressed, and the standard library has no zstd decoder. **Verify against a real modern `.apkg` at plan time, before writing the plan.** The load-bearing requirement is criterion 1's second clause: lossless import with a per-note account of what converted, what was skipped, and why, no note silently dropped. **Default if unruled: prefer stdlib `zipfile`/`sqlite3`; if the archive's compression requires a dependency, take one and record it under the §4a supply-chain rule.**
- **OPEN — ruling 4**: Weibao approves widening and moving 03.2 (the B1/Q10 seeding pull-forward). Recorded as adopted-pending-ruling; if declined, 03.2 shrinks back to provenance only and Phase 11 keeps the seeding loop.

**Plans**: 5 plans across 3 waves

Plans:
**Wave 1**

- [ ] 03.2-01-PLAN.md — The .apkg importer: ZIP + zstd + sqlite3, note-type mapping with loud refusals, lint gate, per-note report
- [ ] 03.2-02-PLAN.md — Provenance: ## SOURCES registry, [SRC:]/[OBJ:] resolution, on-demand coverage map

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 03.2-03-PLAN.md — The seeding loop: six-stage pipeline, one accept endpoint behind CLI + daemon, batch UI
- [ ] 03.2-04-PLAN.md — Paraphrase lint (winnowing, tunable thresholds), style.unsourced_specific, [CASE:]/[PREREQ:] edges

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 03.2-05-PLAN.md — Phase verification: corpus-residency guard, calibration rates, requirement audit, full suite

### Phase 4: Surface Redesign & Theming

**Goal**: As a learner, I want to read every surface from one visual system with an accent colour that follows my OS choice and to edit day plans safely in-page, so that the app feels like one product and my day edits never silently overwrite each other.
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

**Plans**: 6/6 plans executed

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

- [x] 04-06-PLAN.md — Structured day browser editing, day palette migration, conflict recovery, and one-use force confirmation

### Phase 5: Check Item Type & Code Editor

**Goal**: A learner can write and run their own code against a `check` item, in a real editor, and get a dichotomous verdict through the same scorer as every other item type; the item also establishes the reusable interaction contract future visual manipulatives will use.
**Mode:** mvp
**Depends on**: Phase 3.2 (seeded content to score against); coordinate `model.py`/`runtime.py` diffs with Phase 1
**Requirements**: CODE-01, CODE-02, CODE-03, CODE-04, CODE-05
**UI hint**: yes
**Absorbed from research (2026-08-10)**: CodeMirror 6 (MIT, ~300KB) is the editor, chosen because its `Diagnostic{from,to,severity,message}` shape maps 1:1 onto our existing lint records — no adapter layer, no second diagnostic vocabulary. Preview reuses **our own renderer** via `data-line` scroll sync; a second markdown engine is forbidden. This phase does the CM6 vendoring pipeline and learner-facing plumbing only; the full authoring surface is Phase 11. External-editor-plus-watch is a first-class peer path (authoring; Phase 11), and — **superseded 2026-08-11, criterion 9** — a server-rendered textarea with a lint list is the no-JS floor: CM6 is JS-only, so no such floor exists. The `check` type gains stdin/stdout test cases and a function-signature harness mode; Parsons problems are `build` items by convention, needing no new type. See `.planning/research/2026-08-09-lesson-display-editor.md` (Q2) and `2026-08-09-extraction-subjects-bilingual.md` (Q6 CS).
**Additional success criteria (research-derived)**:

  8. A `check` item can specify stdin/stdout cases *or* a function-signature harness, and both reach a verdict through `runtime.score_response()` — the harness mode is a configured strategy, not a second scorer.
  9. **(SUPERSEDED 2026-08-11 by ruling 5/11 + ruling 16 — see RESOLVED rulings below)** Turning JavaScript off leaves a working textarea-plus-lint-list path to the same submitted response shape, and editing the same bank in an external editor with `--watch` reaches the same runtime call as the in-app editor. **Dropped in its first half**: CM6 is JS-only, so the server-rendered textarea-plus-lint-list no-JS floor does not exist and no plan in this phase provides one. The external-editor `--watch` authoring path survives but belongs to Phase 11 (closed authoring loop, B12), which reuses the Phase 5 plumbing rather than duplicating it.
  10. **(round two, R1.1) The `artifact-first` / "Bottom Up" CS style needs nothing the `check` type does not already have.** Bottom-Up ordering and PRIMM pacing are orthogonal and compose as a Phase 3.1 style file; Parsons problems remain `build` items by convention. If plan time falsifies the Runestone Parsons-to-`build` mapping (a **named unknown**, Research Brief 2 §4.5), that is a Phase 3.1 style-ranking problem, not a new item type here.
  11. **(round two, R4.1/R4.2) The `check` verdict reaches `score_response()` as a normalizer, not as a strategy that decides.** A registered normalizer has signature `(q, answer) -> str | None` and reduces code execution to a **per-case outcome vector**; the unchanged `score_response()` performs the single `==`. The return type has no channel for a verdict, which is the first and strongest accretion guard — a `check` implementation *cannot* become a second scorer, because it has nowhere to put a decision. Adding this normalizer requires **zero edits to `score_response()`**; a plan whose diff touches that function has failed this criterion, and a source-hash test pins it.
  12. **(round two, R4.2) A timeout is not a verdict.** Return `None` plus an `error_category`, matching the None-not-False discipline already in the constructed-response path. The authority rule this phase is measured against: *re-running on another machine, from the recorded item version and the response alone, must produce the same verdict; no model, and no input not derivable from the item.* A killed-at-timeout run does not meet it and therefore does not produce one.
  13. **(round two, R4.6c) A missing normalizer degrades to a human, never to a false verdict.** A registry miss leaves the item permanently pending and human-markable, at zero cost. `item.no_normalizer` is a warning; `item.tolerance_unstated` is an error.

**Open decisions**:

- **RESOLVED 2026-08-11 — ruling 5 + ruling 11** (user decision: *"Vendored assets are fine unless we can definitively come up with something better"*): the vendored-asset veto is dead — **CM6 is the editor**, learner-facing and authoring alike, replacing the hand-rolled textarea `CodeEditor` contract in `.planning/UI-SPEC.md` §4. `05-RESEARCH.md:168`, `05-CONTEXT.md:134`, and `05-UI-SPEC.md:65` (the "explicitly forbidden" lines) are **SUPERSEDED**; `05-05-PLAN.md` (the hand-rolled field the dead veto produced) must be rewritten to the CM6 plan before execution. `UI-SPEC.md` §8.2 (no keyboard trap, Tab inserts, Escape returns to navigation) still holds either way. The CM6 vendoring/update pipeline and its supply-chain record are this phase's work, not a budget objection.
- **RESOLVED 2026-08-11 — ruling 16** (applied documented default, consistent with the vendored-assets ruling): a JS test runner is **taken**, recorded under the §4a supply-chain rule — the §8 accessibility gates (keyboard path, focus, no-leak) earn its cost now that CM6 is in; `05-VALIDATION.md`'s manual-UAT fallback for the §4.5 gates is upgraded accordingly.

**Success Criteria** (what must be TRUE):

  1. A learner types code into a monospace field with working line numbers and a tab key that inserts a tab rather than moving focus.
  2. Submitting `check` code runs it, compares output against multiple expected test cases (not one hardcoded string), and reaches its verdict through `runtime.score_response()` like every other item type.
  3. Code that loops forever is killed at the timeout on both Windows and POSIX, including any child process it spawned — verified with a grandchild-spawning test case.
  4. `spec` and any UI copy state plainly that this stops accidents, not deliberate escapes, with no claim of sandboxing anywhere in the documentation.
  5. The editor is the first proof of a renderer-independent interactive-item contract: validated configuration enters the renderer, a meaningful structured response leaves it, `runtime.score_response()` alone returns the verdict, and an accessible non-pointer interaction reaches the same response shape.

**Plans**: 7 plans

**Wave 1**

- [ ] 05-01-PLAN.md — Tracer: one `check` item end to end — parse, run, score, record

**Wave 2** *(blocked on 05-01)*

- [ ] 05-02-PLAN.md — Execution bounds: output cap, Windows Job Object kill, grandchild test
- [ ] 05-03-PLAN.md — Settings group, the agent submit path, and the default-closed LAN refusal

**Wave 3** *(blocked on 05-02, 05-03)*

- [ ] 05-04-PLAN.md — Windows process-tree kill: manual verification and spike record
- [ ] 05-05-PLAN.md — Vendored CM6 editor: mount, theme, line numbers, Tab/Shift-Tab, honest-limits line + JS-runner keyboard assertions

**Wave 4** *(blocked on 05-02, 05-05)*

- [ ] 05-06-PLAN.md — Per-case result matrix and the three refusal states

**Wave 5** *(blocked on 05-04, 05-06)*

- [ ] 05-07-PLAN.md — Honest-limits gate, README, item schema, end-of-phase pass

**Cross-cutting constraints** (must_haves that appear in 2+ plans and must hold at the phase gate):

- **One scorer, byte-identical (criterion 11).** `runtime.score_response()` is the only verdict authority and must be byte-identical after this phase. 05-01 (registry conversion), 05-03 (both submit paths gate on the runner), 05-06 (verdict stays the sole-grader value) and 05-07 (schema + non-page `/api/submit` consumer) all carry must_haves that assume it; the shared gate is the `T-R4-01` source-hash pin in `tests/scoring_roundtrip.py`.
- **A timeout is not a verdict (criterion 12).** Every plan that touches a killed run — 05-01 (normalizer returns `None`, evidence records `error_category: "timeout"`), 05-02 (`killed_at_timeout` flag; test asserts `score_response()` is `None`, never `False`), 05-06 (null verdict renders the pending treatment), 05-07 (schema `score: null`, end-of-phase pass checks the timeout→pending path) — keeps the run pending and human-markable; only the output-cap kill (D-08) is a real fail.
- **No case/key material before submission.** 05-01 (served contract leak check), 05-06 (pre-submit absence assertion) and 05-07 (schema states the omission is deliberate) depend on the same boundary.
- **Honest-limits one-constant identity (D-10).** 05-05 (both readers of `model.HONEST_LIMITS_NOTE`), 05-06 (the line survives every refusal state) and 05-07 (byte-identity assertion + claim-word gate) share one string from `model.HONEST_LIMITS_NOTE`.
- **Suite + guard green.** Every execute plan's verification ends with `for t in tests/*.py; do python "$t" || exit 1; done`; 05-02 and 05-07 additionally require `python itembank.py guard .` (new fixtures must not be mistaken for banks), and 05-05/05-07 add `node --test tests/js/` (ruling 16).

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
  7. **(research-derived, non-deferrable)** Every response event records latency and duration fields from the day this phase's events first land. The evidence log is append-only; a field not written now can never be backfilled, and every pacing, trend, and scheduling feature downstream reads them (B15).
  8. **(research-derived)** A locked tier is *visible runtime state*, never first-person model reluctance: the UI says "Tier 3 unlocks after another attempt" in a dashed-border locked card. Socratic tutoring is commoditized at the prompt layer in every competitor, so the structural lock is the differentiator only if the learner can see it is structural.
  9. **(research-derived)** An exam-sim feedback preset exists that serves a `[CASE:]` group under exam-mode feedback rules in one command.
  10. **(round two, R3.3) A recorded skip does not release the cursor hold's semantics.** Phase 6.2's gate is a default rather than a lock, so this phase must state plainly which of skip and cursor-hold wins when both apply: a skipped gate advances the *reading position* and never the *hint tier*, and skipping is not an attempt. A `gate_skip` event and a hint-tier advance are different events about different things.
  11. **(round two, R3.1) Hint-ladder depth distribution is this phase's usage measure.** A ratio with a stated denominator — the share of correct responses reached at each tier, over responses in modes where the ladder runs. It is a property of the system, not of the person; it is never shown to the learner with a target; and it exists so a ladder nobody climbs past tier 0 is visible as a design failure rather than as learner behaviour.

**Absorbed from research (2026-08-10)**: refusal and redirect copy follows the Khanmigo redirect formula and the study-mode-wave findings in `.planning/research/2026-08-09-landscape-widening.md`; degraded-model states are already designed in `.planning/UI-SPEC.md` (B14).
**Plans**: 2 plans

Plans:

**Wave 1**

- [x] 06-01-PLAN.md — Runtime-owned feedback policy, append-only hint evidence, and derived teaching outcomes

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 06-02-PLAN.md — CLI, identifier-addressed API, and browser clients over the one policy

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
  8. **(round two, R4.3 — non-deferrable) The private versioned tolerance policy's version is written into the event.** Without it, a policy bump silently reinterprets every past visual verdict in the history. The evidence log is append-only, so a version field not written now can never be backfilled — this is the same class of one-way door as Phase 6 criterion 7.
  9. **(round two, R4.1) Visual tolerance reaches `score_response()` as tolerance-as-quantization** — a registered normalizer of signature `(q, answer) -> str | None`, so the single `==` survives literally. Reproducibility ranking, strongest first: **bounds stated in the item** (primary), strategy name and version in the evidence (interpretability, not reproducibility), and a recorded seed (weakest — avoid). `item.tolerance_unstated` is an error, which is what makes the primary mechanism enforceable.

**Absorbed from research (2026-08-10)**: the SVG protocol stands, and Desmos/GeoGebra are **rejected on licensing** rather than on capability — extend our own protocol with two or three math scene types instead of embedding a third-party engine. Canvas/LTI stays backlog. See `.planning/research/2026-08-09-extraction-subjects-bilingual.md` (Q6 Math).
**Benchmark posture:** Brilliant is an explicit learn-by-doing quality target. Public patterns from Brilliant, Desmos/Amplify, GeoGebra, Khanmigo, H5P/QTI, and ALEKS inform prediction-before-explanation, meaningful manipulation, immediate targeted feedback, transparent state, accessibility, and authorability. This phase does not copy proprietary content, interaction details, branding, or pursue competitor feature parity.
**Plans:** 3 plans

Plans:

**Wave 1**

- [ ] 06.1-01-PLAN.md — TRACER: one declarative plot path, then the shared plot/number-line protocol and deterministic runtime scorer

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 06.1-02-PLAN.md — Model-authoring contract, named lint/schema/golden fixtures, and semantic action/observation evidence API

**Wave 3** *(blocked on Waves 1 and 2 completion)*

- [ ] 06.1-03-PLAN.md — Accessible mouse/touch/keyboard equivalence, canvas fallback boundary, GIFT loud refusal, and phase gate

### Phase 6.2: Executable Textbook Loop (INSERTED 2026-08-10)

**Goal**: A lesson reads like a textbook that will not let you skim it — a short passage, an inline check the learner must clear before the next idea appears, and the same idea returning on a schedule days later — built entirely from the lesson reader, the hint ladder, and the evidence log that already exist.
**Mode:** mvp
**Depends on**: Phase 3.1, Phase 5, Phase 6
**Requirements**: GATE-01, GATE-02, GATE-03, GATE-04, GATE-05, GATE-06
**UI hint**: yes
**Research basis**: Execute Program and Runestone loop patterns in `.planning/research/2026-08-09-landscape-widening.md`; brief §7.6.
**Success Criteria** (what must be TRUE):

  1. A lesson can gate its own continuation on an inline check: the next passage does not render until the check is cleared, and clearing it is a `runtime.score_response()` verdict like any other, not a lesson-local rule.
  2. The gate is a **presentation policy over existing item types**, adding no seventh item type and no second scorer — a gated lesson and an ungated one differ by a declared block, not by a code path.
  3. Clearing an inline check writes ordinary response evidence, so a lesson-embedded attempt and a quiz attempt on the same objective are indistinguishable to Phase 10's scheduler except by the `selection_mode`/context field that names where it happened.
  4. An idea cleared inside a lesson re-appears in a later session through the normal retention queue rather than a lesson-specific schedule, proving the loop feeds one store.
  5. A learner can always read ahead by an explicit, recorded choice — the gate is a default, not a lock, and skipping is evidence too.
  6. A bank whose lessons declare no gates renders exactly as it does after Phase 3.1.
  7. **(round two, R3.3) Build both — `[GATE: required|recommended|off]` — and the reason is stronger than the mastery-learning literature.** A hard gate is **theater on a plaintext file the learner owns**: it is a claim the product cannot keep, and a claim that cannot be kept is worse than an absent feature. The loop's value is the return, not the wall. A recorded skip preserves that value *better* than a hard gate does, because skipped-and-still-unclear is a prioritizable signal while a hard gate learns nothing.
  8. **(round two, R3.3) Skip is a new `gate_skip` event type**, verified additive against `evidence.py`, and **explicitly not a `response` carrying a null score**. Conflating them would make a skip indistinguishable from an unmarked attempt in every downstream count.
  9. **(round two, R3.1) Gate outcome split is this phase's usage measure** — the ratio of cleared to skipped gates, over gates encountered. Stated denominator, no target shown to the learner, and no streak.
  10. **(round two, R1.1) The inline check is anchored by `[!CHECK: <id>]`**, the single new parse path Phase 3.1 adds. It carries no key and no scoring path, so this phase adds no scoring surface of its own — consistent with criterion 2's no-seventh-item-type rule.

**Open decisions**:

- **OPEN — ruling 9** (shared with Phase 3.1): May `[!CHECK:]` reference an item in another bank? **Default if unruled: no — narrower now, additive later.** Affects whether a gated lesson can pull its check from a shared bank or only from its own.

**Plans**: 4 plans across 3 waves

Plans:
**Wave 1**

- [x] 06.2-01-PLAN.md — Gate grammar, gate_skip event, response context field, gate_state derivation

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 06.2-02-PLAN.md — The gate band: activate 3.1's D2 slot, three renderings, truncation, mode-degrade, compatibility floor
- [x] 06.2-03-PLAN.md — The recorded-skip control, check/skip routes, settings, and the outcome-split report

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 06.2-04-PLAN.md — Phase verification: the twelve UI-SPEC §13 gates, requirement audit, full suite

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
  7. **(research-derived — ALEKS fringe principle)** The selector serves an objective only when its `[PREREQ:]` edges (authored in Phase 3.2) are already mastered, so the learner is always working the fringe of what they know rather than a randomly-sampled objective. A learner may override, and the override is recorded.
  8. **(research-derived)** Serving order can be blueprint-weighted — an exam blueprint's objective proportions become selection weights — and a `[CASE:]` group serves as one unit under the exam-sim preset.
  9. **(research-derived)** Every selection rule is a **named, registrable strategy** with one interface (candidates in, ranked candidates plus a reason string out). Adding a rule is registering a strategy; it never edits a central `if`-chain, and `select --explain` names the strategy that ranked the winner.
  10. **(round two, R3.1) Corpus reach is a selection-side measure, and this phase serves it.** The share of the bank's items the selector has ever served, over items eligible under any mode — a property of the selector, not of the learner. It exists so an engine that keeps re-serving the same fifty items is visible as a defect. Phase 3.2 owns the corpus; this phase owns the reach.
  11. **(round two, R4.5) A pending model-suggested mark influences selection in no way, but is not nothing.** It counts as an attempt, it grants no mastery, and it never advances an interval. Weight, cooldown, and fringe eligibility all read accepted evidence only. This is a selection-side invariant and must be asserted here rather than assumed from Phase 8.

**Absorbed from research (2026-08-10)**: ALEKS fringe-based selection, UWorld's Educational-Objective line as a selection input, jpdb-style utility weighting, and Brilliant's one-idea-per-screen sequencing wording for the "why this item" trace. See `.planning/research/2026-08-09-landscape-widening.md`.
**Open decisions resolved here**: The selection-mode naming collision — resolved at plan time as a **distinct `selection_mode` field** (D-11), because `schemas/session.schema.json`, `schemas/response.schema.json` and `surfaces/daemon.py:SESSION_MODES` already enumerate `"remediation"` as a *feedback* mode; gated by a blocking `checkpoint:decision` in plan 07-04 because the evidence log is append-only. What the log records about a selection — resolved as a **`selection` event once per sitting plus `selection_mode` on every response event** (D-03), also gated in 07-04. Cooldown scope — resolved as **bank-scoped** (D-13), paid for by bumping `INDEX_VERSION` and adding a `bank` column to the disposable sqlite3 index in plan 07-03. `selection_weights.recency_decay` — resolved as **being** D-08's soft penalty rather than a second knob for the same thing (D-15), with `objective_miss_rate` and `difficulty_spread` retagged to Phase 10.
**Plans**: 6/6 plans executed

Plans:
**Wave 1**

- [x] 07-01-PLAN.md — TRACER: one selector, one objective, one trace with a named runner-up, reached by the CLI and `/api/start`

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 07-02-PLAN.md — `[PAIR:]` and `[PREREQ:]` in the format contract, their two lint codes, and the pair/prerequisite filters
- [x] 07-03-PLAN.md — Bank-scoped exposure: `INDEX_VERSION` 2, a `bank` column, wider history rows, `itembank evidence --bank`

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 07-04-PLAN.md — The two one-way doors: a distinct `selection_mode` field, and the recorded selection spec on the session and in the log

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 07-05-PLAN.md — The four mode compositions in one table, the hard/soft exposure split, and the `selection` settings group

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 07-06-PLAN.md — `itembank select --explain`, `/api/start` preview, named profiles, and `schemas/selection.schema.json`

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
  6. **(research-derived)** The refusal the learner sees is runtime state, not model voice: a locked tier renders as a labeled structural lock with the unlock condition stated, and generated text renders in plain chrome inside a labeled container so a model never acquires a typographic voice of its own. Copy tables in `08-UI-SPEC.md` are updated to the study-mode-wave findings.
  7. **(research-derived)** Adding a third backend (a second hosted CLI, a local llama.cpp server, a future vendor) is a new adapter module plus a config entry, with zero edits to tier-gate, evidence, or prompt-assembly code — proven by adding a stub backend in a test.
  8. **(round two, PLANNING-DIRECTIVES §1 as amended 2026-08-10) This phase plans against a hosted Claude-Code-class backend as the design target.** Weibao, 2026-08-10: *"can establish that the main stuff should work with something like claude code for now to not worry so much."* Consequences, binding: the hosted adapter is built first and is the default; the local 24GB card is an **additional registration behind the same interface**, not a fork and not a prerequisite; prompt-size and latency budgets are written against the hosted model, and the local backend **declares its own limits**, so a plan assuming an 8K context everywhere is wrong. This does **not** relax Directive §4.1 — a hosted model decides nothing about correctness, and the tier-3 `pending` rule is not a function of which backend runs.
  9. **(round two, R3.5) `itembank bench` is still owed, but it is off the critical path** — and **no plan or roadmap entry may carry an invented tok/s or latency figure** in the meantime. The recommended local pairing when the hardware lands is Qwen3-30B-A3B-Instruct-2507 Q4_K_M with gpt-oss-20b as a second backend, Vulkan over ROCm on gfx1100. That is a starting configuration to measure, not a validated one.
  10. **(round two, R4.4 — decisive) Tier-3 promotability is a constant zero, not a spectrum.** Two independent findings force this: LLM judges are **non-reproducible even at temperature 0**, so tier 3 fails the R4.2 authority rule on physics *independently* of Directive §4.1; and judge bias survives explicit anti-bias prompting (d=4.25). Ofqual (14 Jan 2026) independently forbids AI as a sole marker. Therefore **tier 3 is not a scorer strategy at all** — it is a peer of the human marker, sitting outside `score_response()` entirely. Ranked approaches, best first: **self-assessment against a revealed model answer** (g=0.55/0.664, and a learner self-mark *is* a human accept, which dissolves the pending state rather than managing it), deferred human marking, then rubric decomposition — the last justified on **accept ergonomics, not accuracy**, since the within-task A/B does not exist and the one prompt-controlled study finds holistic matches atomic.
  11. **(round two, R4.5) Presentation: self-mark first, and the suggestion never wears a grade's clothes.** The model suggestion sits behind a disclosure control `suggestion_reveal`, default `after-self-mark`, with all three values shipped per Directive §3. It renders as a `--pending` token only — **never a number, never a fraction, never a check or cross glyph**. Accept is the existing `mark_event`. A suggestion never accepted stays pending forever, which is a correct terminal state and not a queue to drain.
  12. **(round two, R4.5) This phase adds a `mark_proposal` event type and must not widen the human-only guard.** `mark_event` raises `ValueError` on `marker != "human"` (`evidence.py:1058`), and that runtime enforcement is what makes criterion 4 true structurally rather than by convention. Three facts verified against the code change the shape of this work: a mark is **already** a separate append-only event about a response, `review_state` is **already** computed at read time, and `mark_event(rubric=...)` **already** stores per-criterion results as N booleans.
  13. **(round two, R4.7) Partial credit is N booleans. No fractional score, no confidence weighting.** A derived "4 of 5" computed at read time is fine. The one-way door was built correctly in Phase 1 and does not need opening, so no `checkpoint:decision` is owed for it.
  14. **(round two, R4.6d) Auto-accepting a tier-3 suggestion must be *impossible*, not off by default** — on four independent grounds, including that **no valid gate variable exists**, since model confidence is uncalibrated. There is no setting, no flag, and no autonomy level that turns it on. Batch accept by a human is the right concession to ergonomics and is the only one offered. Criterion 2's config-swap freedom stops exactly here.

**Named unknowns carried into planning**: **no verified 7900 XTX throughput figure exists** for any candidate model (Research Brief 2 §4.5) — this is the reason criterion 9 forbids a carried number rather than asking for a better estimate. **No trustworthy open-weight prose-quality benchmark exists**, so backend choice for authoring is settled by running our own 18-rule check, not by a leaderboard.
**Absorbed from research (2026-08-10)**: `.planning/research/2026-08-09-landscape-widening.md` (2025 study-mode wave: Socratic tutoring is commoditized at the prompt layer, so the visible runtime lock is the differentiator) and `2026-08-09-blind-spots.md` B14 (degraded-model UX already designed in UI-SPEC). Adapter interface and tier-gate mechanics stay **LOCKED**; only learner-facing copy, provenance presentation, and generated-hint surfaces change.
**Open decisions resolved here**: Tier-gate enforcement mechanism — no prior art found for how the runtime detects and drops model output that reaches past the unlocked tier; this phase must design and test the actual detection/stripping mechanism as a first-class deliverable, not adapter plumbing added after the fact.
**Plans**: 5/6 plans executed (replanned 2026-08-10 against round-two CONTEXT D-01..D-27)

Plans:
**Wave 0**

- [x] 08-01-PLAN.md — TRACER: the deterministic tier gate, bounded-plan contract, and the 30-case adversarial corpus (no provider yet)

**Wave 1** *(blocked on Wave 0 completion)*

- [x] 08-02-PLAN.md — One adapter boundary: hosted CLI + local OpenAI-compatible transports, named profile registry, third-backend stub proof

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 08-03-PLAN.md — Evidence spine: model_interaction and mark_proposal events, descriptor-only drops, N-boolean human accept reference

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 08-04-PLAN.md — Runtime orchestration and CLI: hint/rubric-review commands, retry lineage, human-only proposal accept, agent usage contract

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 08-05-PLAN.md — Daemon routes, SURFACE_PARITY, AgentAssist/rubric UI, no-leak DOM tests, blocking human UAT

**Wave 5** *(blocked on Wave 4 completion)*

- [ ] 08-06-PLAN.md — Phase release gate: cross-surface scenario, offline matrix, authority regressions, contract audit

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
  7. **(research-derived — EMT)** A `## SCENARIO` phased container exists in which **the runtime stages the information reveal**: vitals, history, and scene findings become available on the runtime's schedule, not all at once and not at the model's discretion. This is where the 2026 NREMT TEI patterns land; the existing six item types already cover the widget shapes.
  8. **(research-derived — Math)** Numeric answer equivalence is decided by WeBWorK-style random-point evaluation in roughly 200 stdlib lines, behind one accept rule. `sympy` may later implement the same accept rule as a swappable strategy; the rule, not the library, is the contract.
  9. **(research-derived)** A grep-grade local search route spans banks, lessons, and attempts (B6) — small, and the cheapest thing that makes a growing corpus usable.
  10. Adding a fourth subject remains configuration only, now including its verifier strategy and its lesson medium — verified by adding one in a test, not by argument.
  11. **(round two, R1.7) `??? for math` is answered: the form is Worked Example → Variation → Formalization (`math-worked`).** A section equals one knowledge point: claim, then `[!EXAMPLE]` annotated, then `[!CHECK]` varying exactly one dimension, then `[!KEY]` stating the formal result **after** the example rather than before it. `math-explore` (Experience First, Formalize Later) is the same four blocks inverted and costs one extra file, zero blocks, zero lint codes, and zero parser change — the cleanest Directive §3 case in the project, so **both ship**. `math-worked` is the default for first exposure. **KaTeX is delivery, not form**, and the Phase 6.1 SVG is a figure inside a section, not a style; neither answers this question and neither may be mistaken for the answer.
  12. **(round two, R3.2) `## SCENARIO` is ordered `[STAGE:]` blocks with a closed two-value advance vocabulary — `on-ack` and `on-item`.** `on-elapsed` is **rejected** against `UI-SPEC.md:105`; `on-correct` is **rejected** because it gates a reveal on a verdict. **The reveal position is a derived integer replayed from existing evidence**, which is the mechanism that lets a model author the scenario file while never moving the pointer — criterion 7's "runtime stages the reveal" made structural rather than promised. No un-reveal and no answer locking. Cost: five lint codes, zero new item types, zero scorer change.
  13. **(round two, ruling 7) `lesson_layout` is a subject-profile field**, and `subject_profiles` is a *closed* object per `09-02-PLAN.md`. Folding the field into 09-02 before this phase is planned avoids a registry version bump. EMT and Math are `separate`; CS is `inline`.
  14. **(round two, R4.2/R4.3) Random-point Math evaluation qualifies as reproducible only once its seed is derived from the existing `content_hash`**, which makes the sample points a pure function of the item rather than of the run. Criterion 8's WeBWorK-style checker reaches `score_response()` as a normalizer producing an **agreement vector at pinned points**; the single `==` is unchanged. `sympy` later implementing the same accept rule is a config key plus a module — the proof that the rule, not the library, is the contract.

**Absorbed from research (2026-08-10)**: `.planning/research/2026-08-09-extraction-subjects-bilingual.md` (Q6 per-subject verdicts). Desmos/GeoGebra rejected on licensing; the 6.1 SVG protocol is the math manipulable path.
**Open decisions**:

- **OPEN — ruling 7** (shared with Phase 3.1): fold `lesson_layout` into `09-02-PLAN.md`'s closed `subject_profiles` object, or accept a registry version bump? **Default if unruled: fold into 09-02.**
- **OPEN — ruling 15** (constraint audit F7, revisit): `03-CONTEXT.md:158` and `03-04-PLAN.md:79` grant leave to **drop table rendering** "if a stdlib table renderer proves out of proportion" — an effort budget that only exists because `03-RESEARCH.md:228` refused `markdown`/`mistune`/`commonmark` unread ("Not evaluated further"). SC4 here requires that an EMT lesson renders prose **and tables** correctly, and `UI-SPEC.md` §8 Narrow requires tables to preserve headers via a horizontal-scroll wrapper with an accessible name or stacked definition rows. A learner-facing feature carrying a §8 obligation is not droppable on effort. The single-renderer decision itself stands, on the better ground that §4.2 forbids a second parser and Phase 5's preview reuses ours via `data-line` sync. **Default if unruled: table rendering is in scope and the §8 Narrow obligation is met.**

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

### Phase 9.1: Audio Drill Export (INSERTED 2026-08-10)

**Goal**: An objective leaves itembank as an audio drill pack — stem, pause, key, why — so a commute or a run is study time, with no app to build, no player to write, and no dependency the tool cannot do without.
**Mode:** mvp
**Depends on**: Phase 1, Phase 9
**Requirements**: AUDIO-01, AUDIO-02, AUDIO-03, AUDIO-04, AUDIO-05, AUDIO-06, AUDIO-07
**Research basis**: `.planning/research/2026-08-09-blind-spots.md` B3 — named as real, cheap, and differentiating. Research also found (Q9) that consumption is phone- and audio-shaped while the desktop app optimizes authoring; this is the cheapest correction available.
**Success Criteria** (what must be TRUE):

  1. ✅ `itembank export audio --objective <id>` writes an audio file plus a plain-text transcript per pack, sequencing stem → timed pause → key → why.
  2. ✅ The TTS engine is a **settings entry behind one interface** — `edge-tts` today, Piper locally, Kokoro on the 7900 XTX when it arrives — and swapping it is a config change with no code change, exactly like the model backend.
  3. ✅ With no engine installed or reachable, the command still emits the transcript and a named, actionable refusal; it never half-writes an audio file.
  4. ✅ Playback is any podcast app. No player, no sync service, and no mobile build is in scope.
  5. ✅ Listening records nothing — an audio pack is a one-way export, and the evidence log stays the record of what was actually answered.

**Plans**: 4 plans across 3 waves

Plans:
**Wave 1**

- [x] 09.1-01-PLAN.md — TRACER: TTSEngine interface + registry + transcript-only engine + `itembank export audio` CLI, sequence/pause settings, transcript, digest naming, atomic write

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 09.1-02-PLAN.md — The engines: edge-tts (network, MP3-native) and Piper (local, WAV + lameenc MP3), pinned and license-reviewed, D-16 help-text disclosure
- [x] 09.1-03-PLAN.md — Pack assembly: timed pauses, MP3/WAV container policy, --split per-item|per-pack, digest-stable atomic writes, daemon route

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 09.1-04-PLAN.md — Phase verification: fake engine + transcript-diff + no-evidence fixtures, both-surfaces proof, requirement + supply-chain audits, full suite

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
  7. **(research-derived)** **FSRS is the scheduler baseline**, its state derived by replaying the append-only evidence log — including Phase 3.1's `key_review` events — rather than stored as mutable per-item scheduling rows. Rebuilding scheduler state from the log alone must reproduce it exactly.
  8. **(research-derived)** The scheduler sits behind one interface with FSRS as the default strategy, so a later algorithm change is a registered strategy plus a replay, not a migration.
  9. **(research-derived)** Progress is named in WaniKani-style stages with a terminal "retired" state, and due ordering is jpdb-style utility-weighted — legible, non-punitive motivation with no streaks and no points.
  10. **(round two, R3.1) Return rate is this phase's usage measure, and it is deliberately not a streak.** A ratio with a stated denominator — sittings that occurred over sittings that came due — and it is a property of the system's pacing, not a judgement of the person. It is never shown with a target, never renders as a consecutive count, and never produces a loss state. The anti-streak rule in `UI-SPEC.md` holds over any tension with it.
  11. **(round two, R3.1) Lesson-to-item transfer is the most interesting measure available and is deliberately deferred**, because it is not computable from the evidence log as it stands. Recorded here with its cost rather than silently dropped, so a later phase can pick it up knowing why it was not built now.
  12. **(round two, R4.5) A pending model suggestion never advances an interval and grants no mastery**, though it does count as an attempt. Scheduler state replayed from the log must read accepted marks only — a rule that has to hold here because this phase is where "what is due" is decided.

**Absorbed from research (2026-08-10)**: FSRS, WaniKani stages, jpdb weighting (`.planning/research/2026-08-09-landscape-widening.md`); D2 memorizables entering the queue (`2026-08-09-differentiators-d1-d2-d3.md`); anti-punitive pacing copy already LOCKED in `.planning/UI-SPEC.md`.
**Plans**: 0/6 plans executed
**Wave 1**

- [ ] 10-01-PLAN.md

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 10-02-PLAN.md

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 10-03-PLAN.md

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 10-04-PLAN.md

**Wave 5** *(blocked on Wave 4 completion)*

- [ ] 10-05-PLAN.md

**Wave 6** *(blocked on Wave 5 completion)*

- [ ] 10-06-PLAN.md

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
  6. **(research-derived)** The auditor consumes Phase 3.2's **computed** coverage map rather than deriving coverage a second way, and the five `manual`-severity `LESSON-STYLE.md` rules are enforced here as model-judged, report-only findings.
  7. **(research-derived)** The full CodeMirror 6 authoring surface lands here — diff, preview through our own renderer, approve, write — reusing the Phase 5 plumbing rather than introducing a second editor integration, and surfacing git diffs of the bank (B12).
  8. **(round two, R2) Model-judged rules are enforced here at registry scale, and only the discourse-judgement class reaches this phase.** Structural counts and the shared lexical metrics pass both run on every `lint` in Phase 3.1; what is left for this phase is genuinely semantic and is **report-only**, never blocking a human's lint. The style check catalogue is **closed** — this phase may not define a check that Phase 3.1's catalogue does not contain, for the same reason Phase 3.1 cannot: `LINT_CODES` is a published API.
  9. **(round two, R3.4) The six-stage generation pipeline is this phase's authoring loop**: deterministic source selection, outline-only, per-section drafting, deterministic checks **before** any model critique, independent CoVe-style verification, human accept. Roughly nine model calls per lesson, so criterion 4's autonomy ladder is governing a **batch** operation, and the UI must present it as one. A style `error` blocks a machine-authored write here; that is the whole point of the severity split.
  10. **(round two, R1.6) `restyle` is this phase's operation and is model-driven, human-gated, and produces a new file.** It must never be conflated with the runtime's `render_style`, which is model-free and may only permute existing blocks. The mechanically impossible transforms are refused rather than approximated: expository→case-narrative, expository→Socratic, expository→worked-example, anything→Bottom-Up, case-narrative→anything.
  11. **(round two, R5.2) One-action reversibility is what forced the two-file default.** SC4 commits each autonomous write separately and SC5 demands single-action undo, which is impossible without hunk surgery when a style pass and a seeding pass share a file. This criterion is the reason Phase 3.1 criterion 7 exists, and a plan that re-merges prose and items breaks it.
  12. **(round two, R3.1) Style adherence density is this phase's usage measure** — style-rule violations per thousand words over generated lessons, with a stated denominator, shown to nobody as a target. Suppression counts (`<!-- style-ignore: -->`) are themselves a report here: a check suppressed everywhere is a check to retire, not a learner to correct.

**Open decisions**:

- **OPEN — ruling 14** (constraint audit F4, revisit): D-03 (`11-RESEARCH.md:15`, `11-CONTEXT.md:19`) defers PDF/DOCX because markdown/UTF-8 are first-class *"under the stdlib constraint"*, and `REQUIREMENTS.md:200` pre-loads the same framing. That constraint no longer binds, so the "open" decision below is really pre-answered by a dead rule. A syllabus is very often a PDF, and Phase 11 has no plans yet, so this is cheap to reopen. The deciding question is **locator fidelity for citation**, not stdlib coverage. **Default if unruled: markdown and UTF-8 stay the guaranteed lossless, locator-stable inputs; a PDF text extractor is a dependency decision made on merit at plan time.**
- **OPEN — ruling 10**: Does the style exemplar earn its prompt tokens? Untested — the seven-imperative cap plus one exemplar (Phase 3.1 criterion 3d) is extrapolated from format-compliance research, not measured on pedagogical structure. **Default if unruled: ship it toggleable and measure.**

**Named unknowns carried into planning**: **no benchmark for single-objective adherence in long generation** exists (Research Brief 2 §4.5), and **no trustworthy open-weight prose-quality benchmark** exists — so criterion 9's pipeline is justified structurally, and model choice for authoring is settled by running our own 18-rule check over generated lessons rather than by any published score.
**Scope note (2026-08-10)**: this phase **shrinks**. Anki import and the human-gated seeding loop moved to Phase 3.2; the `[SRC:]`/`[OBJ:]` provenance standard and the coverage-map computation moved with them. What stays is the risky part the research agreed should stay late: the autonomy ladder, the citation contract, the second quality gate, and reversibility.
**Open decisions resolved here**: Second quality gate algorithm (distractor-overlap heuristic, near-duplicate detection thresholds); syllabus input formats (markdown/text only, vs. PDF/DOCX that stdlib parses poorly); auditor reversibility mechanism (shadow copy vs. a git commit per write, depending on whether the private bank directory is git-tracked). These three converge with the top pitfalls flagged for this subsystem — the citation contract, the second quality gate, and reversibility are novel mechanisms with no working precedent in any examined product, and need fresh design at plan time, not just implementation.
**Plans**: 5 plans across 4 waves

### Phase 12: ~~Packaging, Self-Update & Interop Export~~ (MOVED)

This phase's full content — goal, requirements, success criteria, open decisions — now lives at **Phase 2.1**, inserted after Phase 2 on 2026-08-07. This numbered slot is retired: do not plan or execute against "Phase 12" and do not reuse this number for new work. The desktop-packaging work the 2026-08-09 research produced is **Phase 13**, a new number, not a revival of this one.

### Phase 13: Desktop Packaging — Tauri Shell over the Python Sidecar

**Goal**: itembank installs and launches like a real desktop application on Windows, and the thing inside the window is still the same Python runtime, the same scorer, and the same evidence store the CLI uses.
**Mode:** mvp
**Depends on**: Phase 2.1 (the `.pyz`, the updater, and the release channel it reuses)
**Requirements**: DEL-09, DEL-10, DEL-11, DEL-12, DEL-13
**Research basis**: `.planning/research/2026-08-09-packaging.md` (Q8). Verdict: **keep the Python runtime.** Porting the runtime to a JS/Rust stack would temporarily create two scorers — the one anti-pattern this project forbids outright. SiYuan's kernel-behind-webview architecture is shipping proof of the pattern.
**Success Criteria** (what must be TRUE):

  1. A Tauri 2.x shell launches a PyInstaller-onedir Python sidecar and talks to it over the existing localhost HTTP surface — the sidecar is the same daemon Phase 2 built, reached the same way, with no second IPC protocol.
  2. An NSIS installer installs, launches, and uninstalls cleanly on Windows, and a signed `tauri-plugin-updater` updates from the same GitHub Releases the Phase 2.1 updater already uses.
  3. Killing the shell leaves no orphaned sidecar process and no held port; a second launch attaches or refuses cleanly rather than racing.
  4. The installer is within roughly 25–45 MB, and an antivirus/code-signing checklist is written and executed — AV false positives on frozen Python are the named top risk, not a hypothetical one.
  5. Every capability remains reachable from the CLI without the shell installed; the desktop app is a client of the runtime, never a precondition for it.
  6. Linux (WebKitGTK) and macOS are **deferred to hardware**, with Electron recorded as the named Linux fallback rather than silently unresolved.

**Open decisions**:

- **OPEN — ruling 3**: Weibao confirms Q8 (keep Python, Tauri sidecar, NSIS) and this phase number. The direction is recorded as adopted-pending-ruling; nothing else in the roadmap depends on the answer.

**Plans**: 5/5 plans executed across 3 waves

Plans:
**Wave 1**

- [x] 13-01-PLAN.md — Sidecar handshake (port + token + version), token gate, single-instance attach/refuse, lifecycle fixture

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 13-02-PLAN.md — The Tauri shell: sidecar spawn, Job Object lifecycle, named mutex, window chrome, liveness states
- [x] 13-03-PLAN.md — PyInstaller onedir build, NSIS installer with evidence-store guard, install notice, headless CLI proof

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 13-04-PLAN.md — Updater: latest.json + minisign alongside SHA256SUMS.txt, tauri-plugin-updater, one-disclosure StatusNotice
- [x] 13-05-PLAN.md — Phase verification: executed AV/signing checklist, lifecycle/size/headless evidence, full suite

## How this roadmap gets planned (added 2026-08-10)

`.planning/PLANNING-DIRECTIVES.md` is binding on every planning session and holds
Weibao's instructions verbatim. The three rules that change what a planner does:

1. **Keep going.** Stop only for a hard-to-reverse decision, a quality fork the
   research does not resolve, or a conflict with the five non-negotiables. Record
   assumptions and continue rather than asking.

2. **When two designs are both defensible, ship both** behind one interface and make
   the choice a setting. This is affordable exactly because of the Extensibility
   Rules below. It stops being affordable — and the rule stops applying — when the
   two options would need two parsers, two scorers, or two evidence stores.

3. **Claude plans, DeepSeek V4 executes.** Consequential decisions, UI above all,
   are made by the more capable model before any code is written, so execution is
   transcription rather than judgment. A plan that leaves a design decision to the
   executor has failed at its job.

Per phase, in order: `/gsd-discuss-phase <n>` → `/gsd-ui-phase <n>` if it has a
learner-facing surface → `/gsd-plan-phase <n>`.

**Research status**: **both passes are complete.**
`.planning/RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md` (the lesson-style registry
plus five threads round one left loose) finished 2026-08-10 and its §4 verdicts were
folded into Phases 3.1, 3.2, 5, 6, 6.1, 6.2, 7, 8, 9, 10, 11 and Extensibility Rule 8
on the same day, additively and with no renumbering. **Phase 3.1 is unblocked.**
Rulings 7–10 are recorded as OPEN on the phase each blocks, each with a default if
unruled; none of them blocks starting.

`.planning/research/2026-08-10-constraint-audit.md` (cargo-culted constraints across
the planning corpus) finished 2026-08-10. Its constraint-basis block is now
`PLANNING-DIRECTIVES.md` §4a, additive only — §4's five non-negotiables are unchanged
and **no decision in this roadmap is reversed**. F1's six propagation sites were
reworded to cite `VIS-01` (bank-authored JavaScript) instead of Directive §4.5; the
rejection of explorable explanations stands. F2, F3, F6 and the four revisit
candidates (F3, F4, F7, F17) are recorded as **rulings 11–16** on the phases they
block. Ruling 11 (Phase 5 / CodeMirror 6) is the only one without a default and is
the highest-priority item: Phase 5 currently carries two incompatible editor plans. Where the research could not determine
something (brief §4.5), the phase carries a **named unknown** rather than a number —
notably the 7900 XTX throughput figure, which no plan may invent.

Next action per brief §6: `/gsd-discuss-phase 3.1`.

## Extensibility Rules (cross-cutting, added 2026-08-10)

The research adds twelve or so features across ten phases. That only stays
affordable if each phase adds a **registration**, not a branch. These rules are
phase acceptance criteria wherever they apply, and a reviewer may cite them
against any plan.

1. **One interface per swappable decision.** Model backend, TTS engine, scheduler
   algorithm, numeric-equivalence checker, selection strategy, subject profile,
   and lesson-block renderer are each one interface with named registered
   implementations. Adding one is a new module plus a config entry.

2. **No central `if`-chain may grow.** If a plan's diff adds a branch to a
   dispatcher that already has three or more, the plan converts it to a registry
   in the same commit.

3. **Additive format only, and provably so.** Every phase adding grammar ships a
   fixture bank using none of it and asserts byte-identical output against the
   prior phase. This is the compatibility floor, tested rather than promised.

4. **Strategies are named in evidence.** Whatever chose, scheduled, or scored
   something writes its strategy name into the event, so a later algorithm change
   is legible in the history instead of silently reinterpreting it.

5. **Derived, never stored.** Coverage maps, scheduler state, and trends are
   computed from the append-only log on demand. A cache is allowed only if it is
   disposable and its staleness is detectable (the Phase 1 sqlite3 index is the
   precedent).

6. **The extension point is proven by a stub.** A phase claiming "adding another
   X is configuration only" adds a throwaway second X in a test. An untested
   extension point is a claim, not a seam.

7. **Every capability keeps both surfaces.** A route and a CLI command, both
   calling the same runtime function. A feature reachable from only one surface
   is unfinished.

   *Amended 2026-08-10 (`.planning/notes/2026-08-10-mcp-as-third-surface.md`).* When
   V2-INT-02 lands, this becomes **three** surfaces and `SURFACE_PARITY`
   (`surfaces/daemon.py:99`) grows a third column: route, CLI command, **MCP tool**.
   It does not become a second parity map, and it does not become a second
   dispatcher. The rule's teeth are that an unmapped entry fails a test; a third
   column keeps those teeth for free, and a second map loses them quietly. An MCP
   surface added any other way is a violation of this rule, not an extension of it.

8. **One scorer, two normalizer registries, and a judgement path that is not a
   scorer at all.** *(Rewritten 2026-08-10 from Research Brief 2 §4.3 R4. The prior
   wording — "a registered strategy that declares its own authority" — was the
   working hypothesis and is **overturned**: it hands every strategy the power to
   decide and then asks it not to. The tier table below still describes the world
   correctly; what changed is the mechanism underneath it.)*

   Different item types genuinely need different verdict methods, and pretending
   otherwise is what produces a second scorer. The researched design:

   | Tier | Method | Item types | Authority | Reproducible? |
   |---|---|---|---|---|
   | 1 | Canonical-form equality | `mc`, `multi`, `table`, `dnd`, `build` | `accepted` | Yes — item + response alone |
   | 2 | Executable or computed checker | `check` code, Math equivalence, `visual` tolerance | `accepted` | Yes — deterministic given the same bounds |
   | 3 | Model judgement against a rubric | `short`, future open-text | **`pending`** until a human accepts | No |

   **The mechanism.** Two registries of **normalizers**, signature
   `(q, answer) -> str | None`, feeding the **unchanged** `score_response()`. All
   three tier-2 checkers reduce to normalization — code to a per-case outcome
   vector, math to an agreement vector at pinned points, visual to
   tolerance-as-quantization — so the single `==` at `runtime.py:120-130` survives
   **literally**, not rhetorically. A reviewer can point at one three-line function
   and say every verdict passes through it.

   **Four accretion guards, strongest first.** (1) The return type has **no channel
   for a verdict**, so a strategy cannot smuggle one out. (2) **Authority is a
   property of the code path, not a declaration** — nothing declares itself
   trustworthy. (3) **Tier 3 is not a scorer strategy at all**: it is a peer of the
   human marker, living outside `score_response()` entirely (Phase 8 criteria
   10–12). (4) A source-hash test pins the function, so an edit to it fails CI.

   **The authority rule, in one testable sentence:** *re-running on another machine,
   from the recorded item version and the response alone, must produce the same
   verdict; no model, and no input not derivable from the item.* A timeout is **not
   a verdict** — return `None` plus an `error_category`, matching the None-not-False
   discipline already in the constructed-response path. Sampling qualifies **only**
   once the seed is derived from the existing `content_hash`, making the sample
   points a pure function of the item.

   **Tier 3 promotability is a constant zero, not a spectrum.** LLM judges are
   non-reproducible even at temperature 0, so tier 3 fails the rule above on physics
   *independently* of Directive §4.1. Auto-accepting a tier-3 suggestion must be
   **impossible, not off by default**. Partial credit is **N booleans** — no
   fractional score, no confidence weighting; a derived "4 of 5" computed at read
   time is fine. Phase 1 built this door correctly and it does not need opening, so
   **no `checkpoint:decision` is owed** for it.

   **Cost of the whole R4 design:** 2 registries, 2 lint codes
   (`item.tolerance_unstated` error, `item.no_normalizer` warning), 2 tests, 1
   optional dependency (`sympy`), 1 config key, 1 event type (`mark_proposal`). No
   new blocks, no parser change, **no edit to `score_response()`** — a plan whose
   diff touches that function has failed.

9. **A new API route reserves its tool name, and a key-bearing payload is gated on
   evidence.** *(Added 2026-08-10, extracted from backlog Phase 999.3 criteria 2 and 3
   during `/gsd-review-backlog`. Binds Phases 3 through 11 now. The phase itself stays
   in the backlog; this rule does not.)*

   Two cheap habits now, because both are expensive retrofits later and one of them
   fails **silently**.

   **(a) Reserve the tool name.** Any plan adding an entry to
   `surfaces/daemon.py:API_ROUTES` adds its CLI command **and** its future MCP tool
   name to `SURFACE_PARITY` in the same commit. The tool need not exist. The name
   being present is what makes the parity test meaningful the day a dispatcher is
   written, and what stops the third surface arriving as a second parity map. Cost:
   one string per route.

   **(b) A key-bearing payload rides the answer path, and says so.** Verified against
   the tree 2026-08-10, today's code is **already correct, by construction rather than
   by rule**, and that is the thing worth pinning before a fourth caller exists:

   - `surfaces/daemon.py:1261` and `:705` attach `explain` to a **submit result** —
     a response has necessarily been recorded to produce one.

   - `reveal` (`daemon.py:660`) is narrower than its name suggests: it controls only
     whether `explain_payload` returns the **short-item model answer**, and it defaults
     off. It is not the gate on the explain block itself.

   - `surfaces/study.py:29` passes `reveal=True` unconditionally, which is correct and
     deliberate: study is an answers-visible surface by definition, not a sitting.

   The rule: **any new caller of `explain_payload()`, or any new payload carrying the
   key, rationale, or distractor analysis, either sits on the answer path or names the
   evidence read that authorized it.** A caller-supplied boolean is not authorization.
   Study-mode-style always-reveal surfaces remain legitimate and must declare
   themselves as such in a docstring, the way `study.py` already does.

   **Why (b) is urgent and (a) is merely tidy.** The current correctness is
   *incidental* — it holds because every caller happens to live on the submit path. The
   day a caller does not, a leak breaks Directive §4.1 **invisibly**: the browser
   surface still behaves, every existing test still passes, and the defect is
   unobservable until a non-browser caller exists. By then every payload path written
   under the old habit needs re-auditing. A reviewer may cite this rule against any plan
   whose diff constructs an explain-shaped payload off the answer path without naming
   what authorized it.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 2.1 → 3 → 3.1 → 3.2 → 4 → 5 → 6 → 6.1 → 6.2 → 7 → 8 → 9 → 9.1 → 10 → 11 → 13.
Phases 1, 2, 3, and 5 have no dependency on each other and are parallel-eligible per config
(`parallelization: true`); their `Depends on` fields, not their numbering, are the source of truth
for what can run concurrently.

**Sequencing change 2026-08-10**: Phase 3.2 (Seeding, Import & Provenance) must land
**before Phase 5**. Phase 5 onward are tuned against content; building them against
synthetic fixtures means tuning them twice. Phase 5's `Depends on` was changed
accordingly — it is no longer parallel-eligible with Phase 1.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Evidence Spine & Protocol Foundation | 11/11 | Complete    | 2026-08-07 |
| 2. Daemon Consolidation & Settings Foundation | 6/6 | Complete    | 2026-08-08 |
| 2.1 Packaging, Self-Update & Interop Export | 9/9 | Complete | 2026-08-08 |
| 3. Lesson Format & In-App Reader | 6/6 | Complete | 2026-08-11 |
| 3.1 Lesson Rich Blocks, Glossary & Style | 7/7 | Complete (human-verify items open; see 03.1-GATES.md) | 2026-08-11 |
| 3.2 Seeding, Import & Provenance | 0/5 | Planned | - |
| 4. Surface Redesign & Theming | 6/6 | Complete | 2026-08-11 |
| 5. Check Item Type & Code Editor | 0/7 | Planned | - |
| 6. Hint Ladder, Cursor-Hold & Feedback Modes | 2/2 | Complete    | 2026-08-10 |
| 6.1 Interactive Visual Assessment Protocol | 3/3 | Complete | 2026-08-11 |
| 6.2 Executable Textbook Loop | 4/4 | Complete | 2026-08-11 |
| 7. Selection Engine | 6/6 | Complete (roadmap gaps in 07-VERIFICATION.md) | 2026-08-11 |
| 8. Model Adapter Interface & Tier-Gate Enforcement | 5/6 | In Progress|  |
| 9. Subject-Invariant Loop — EMT, Math, CS Integration | 0/5 | Planned | - |
| 9.1 Audio Drill Export | 4/4 | Complete | 2026-08-11 |
| 10. Retention, Pacing & Trends | 6/6 | Complete | 2026-08-11 |
| 11. Closed Authoring Loop & Curriculum Auditor | 0/TBD | Not started | - |
| 12. ~~Packaging, Self-Update & Interop Export~~ | — | Retired (moved to 2.1) | - |
| 13. Desktop Packaging — Tauri Shell over Python Sidecar | 5/5 | Complete    | 2026-08-10 |

## Backlog

> **Backlog reviewed 2026-08-10** (`/gsd-review-backlog`). Nothing promoted, nothing
> removed, one entry split. The reasoning for each verdict is recorded inline below so
> the next review argues with it rather than re-deriving it.

### Small enhancements (recorded 2026-08-10)

| Item | Disposition |
|---|---|
| OLED / true-black theme mode | Deferred to backlog. Small, well-scoped add: one `theme` enum value (`oled`) plus a true-black token set (`bg` `#000000`, dimmer card/chip, semantic contrast re-verified) and the `/settings` theme option. Natural home: a small follow-up to Phase 4 theming, or folded into Phase 13's desktop pass when native window chrome is revisited. Raised from Phase 4 UAT (2026-08-10). |

### Phase 999.1: Advanced Visual Item Families (BACKLOG)

**Goal:** Extend the Phase 06.1 visual protocol beyond plot and number line into advanced visual families.
**Requirements:** TBD
**Depends on:** Phase 06.1 (0/3 plans, not executed)
**Plans:** 0 plans

Covers `hotspot`, `diagram`, `timeline`, `trace`, geometry/construction, and dense
simulation-style responses. Phase 06.1 owns the initial plot/number-line protocol, the
SVG/HTML slice, semantic evidence, and the canvas-fallback rule. Renderers continue to
receive validated configuration rather than bank-authored JavaScript
(`REQUIREMENTS.md` VIS-01, `UI-SPEC.md:609`).

**2026-08-10 review verdict: KEEP.** Not promotable, for a mechanical reason rather
than a judgement call: its only dependency, Phase 06.1, has 0 of 3 plans executed.
Promoting a phase ahead of the phase whose protocol it extends would mean designing
`hotspot` against a plot/number-line contract that does not exist yet. Re-review when
06.1 is verified.

**Split from Canvas/LTI on 2026-08-10.** The two halves were bundled and have opposite
dependency profiles and opposite constraint status: visual families depend on 06.1 and
violate nothing, while Canvas/LTI depends on nothing here and collides head-on with a
product constraint. Bundling them meant neither could be reviewed on its own terms. The
LTI half is now 999.4.

### Phase 999.4: Canvas LMS Integration via LTI (BACKLOG, split from 999.1 on 2026-08-10)

**Goal:** Expose the item player inside Canvas LMS through an explicitly hosted, authenticated LTI surface, as an adapter to the same local runtime and scorer rather than a second authority.
**Requirements:** TBD
**Depends on:** nothing in this roadmap
**Plans:** 0 plans

Covers the hosting, identity, privacy, deep-linking, and grade-passback decisions LTI
requires.

**Redirect.** Artifacts written before 2026-08-10 park Canvas/LTI in "Phase 999.1" and
still read correctly except for the number: `06.1-03-PLAN.md:125`,
`06.1-RESEARCH.md:298`, `2026-08-09-landscape-widening.md:428`,
`HANDOFF-2026-08-09.md:5`. They are not rewritten, because their reasoning is unchanged
and rewriting executed and historical artifacts to chase a renumber is churn. **This
entry is the live one.**

**2026-08-10 review verdict: KEEP, and the next review should seriously consider
Out of Scope instead.** The argument against it is not cost, it is that three separate
recorded constraints point the other way, and no one has answered them:

1. `.claude/CLAUDE.md` **Users**: *"One. No accounts, no auth, no multi-tenancy, and no
   design work spent on them."* LTI is an authentication and identity protocol. It is
   the thing that sentence names.

2. `.claude/CLAUDE.md` **Data residency**: *"No cloud sync, no hosted gradebook, no
   telemetry."* Grade passback is a hosted gradebook write.

3. `ROADMAP.md` **Recorded descopes (2026-08-10)**: *"QTI / LTI / xAPI LRS (landscape
   verdict) | Skipped."* The descope table already skipped LTI and then pointed at this
   entry, which is circular. That circularity is the defect this split exposes.

Note that Directive §4a's constraint-basis rule cuts **for** this entry too: the Users
and Data-residency lines are `CLAUDE.md` constraints, not §4 non-negotiables, so they
inform and do not veto. The honest position is that LTI is not forbidden, it is
unjustified: **no consumer exists.** The same standard already applied to QTI
(`V2-INT-01`: *"once a real consumer exists"*). Promote when a real Canvas course
requires it, and not before.

### Phase 999.2: Bilingual Reader (BACKLOG)

**Goal:** Tappable, tracked-word-status reading over un-authored running prose — LingQ's actual product.
**Requirements:** TBD
**Plans:** 0 plans

Phase 3.1 reserves one optional ignorable `key=value` meta field on `## TERMS`
(`zh=…`) so authored bilingual glosses work today. The fork to a separate
codebase happens only when un-authored prose must be tappable with tracked word
status: that needs tokenization, lemmatization, and a per-word state store, which
is a second product rather than a feature. Build nothing until then.
See `.planning/research/2026-08-09-extraction-subjects-bilingual.md` (Q7).

**2026-08-10 review verdict: KEEP, unchanged.** This is what a correctly parked backlog
entry looks like and it needs nothing from this review. It names a sharp trigger (prose
must be tappable with tracked word status), names the three capabilities that trigger
requires (tokenization, lemmatization, a per-word state store), states the conclusion
that follows (a second product, not a feature), and records the cheap thing already
shipped in its place (the `zh=` meta field on `## TERMS` in Phase 3.1). Nothing to
re-litigate.

### Phase 999.3: MCP Surface — the runtime as a tool table (BACKLOG, added 2026-08-10)

**Goal:** An AI tutor drives a real itembank session through MCP tools instead of
scraping a page or shelling out, and every gate the HTTP surface enforces the MCP
surface enforces identically, because it is the same handler.
**Requirements:** V2-INT-02 (expanded 2026-08-10), V2-INT-03
**Depends on:** Phase 2 (complete). Not Phase 8.
**Design basis:** `.planning/notes/2026-08-10-mcp-as-third-surface.md`, against MCP
spec revision **2026-07-28**.
**Plans:** 0 plans

**Why this is not Phase 8.** Phase 8 is itembank calling a model: the model is an
upstream producer of hint text, and the gate asks *may this text render*. This is a
model calling itembank: the model is a downstream client, and the gate asks *may
this tool run, and what may it return*. They share no code. A plan that folds them
together has confused "involves an LLM" with "is the same seam."

**Success Criteria** (what must be TRUE):

  1. A registered stdio MCP server exposes one tool per `surfaces/daemon.py:API_ROUTES`
     entry, whose `inputSchema` is the corresponding published `schemas/*.json`
     document **read off disk** by the same `resources.py` path `protocol_cli.py`
     uses. Proven by a test that mutates a schema file and observes the tool
     signature change without a code edit.

  2. `SURFACE_PARITY` carries three columns and its existing test fails on a tool
     without a route, or a route without a tool. No second parity map exists.

  3. A pre-response tool call returns exactly `runtime.public_item()`. Proven by the
     existing no-key-in-payload discipline: a test asserts the key, rationale, and
     distractor analysis appear in **no** MCP response for an item with no recorded
     response in the evidence store.

  4. A tool call that reaches past the currently unlocked tier returns
     `isError: true` with the unlock condition stated, and the tier is read in the
     Python handler. Proven adversarially: an agent instructed to demand the answer
     receives the same refusal as one that asks politely, because the tool
     description participates in neither.

  5. stdio and an HTTP mount on the Phase 2 daemon both dispatch the same tool table
     through one framing function. Adding the second mount is a registration, not a
     fork (Extensibility Rule 6: prove it with a stub third mount in a test).

  6. The server implements `server/discover`, `tools/list`, `tools/call`, tolerates
     `notifications/cancelled`, **and** retains a legacy `initialize` /
     `notifications/initialized` path, because clients probe discover-first and fall
     back on any error, and it is unverified which revision Claude Code and Codex
     speak today.

  7. The server writes **no non-MCP bytes to stdout**. This collides with the
     codebase's `print()`-to-stdout convention and is the named top risk; logging on
     the MCP path goes to stderr, enforced by a test that asserts every stdout line
     parses as JSON-RPC.

  8. The server validates every tool input against its schema before dispatch, per
     the spec's MUST. `schema_validate.py` is reused; no validator dependency is added.

  9. `outputSchema` is declared for every tool and the structured result is mirrored
     into a TextContent block, per the spec's SHOULD.

  10. Every capability stays reachable from the CLI with no MCP client installed. The
      MCP surface is a client of the runtime, never a precondition for it.

**Named unknowns carried into planning:**

- Whether an MCP session and a browser session may share one session id. Leaning yes,
  since the evidence store already distinguishes actors. Undecided.

- Whether authoring tools (`lint`, `guard`, `export`) join the sitting tools in one
  table or a second capability group. Leaning one table.

- Whether `mark_proposal` (Phase 8 criterion 12) is reachable over MCP at all.
  Leaning no, until Phase 8 lands.

**Size estimate:** roughly 350 to 450 lines of stdlib Python for transport, dispatch,
discover-plus-legacy, and six tools. Estimate, not measured. No dependency.

**2026-08-10 review verdict: KEEP — but its one-way door was extracted and now binds
Phases 3 through 11 immediately (Extensibility Rule 9).**

The promote case is genuinely strong and is recorded here so the next review does not
have to rebuild it. `CLAUDE.md` states the milestone's own user as *"AI tutors as
first-class clients of the same runtime a human uses."* MCP is that sentence in
protocol form. Directive §1 settles the design-target backend as *"something like
claude code,"* and MCP is how Claude Code natively reaches a local tool. The phase
depends only on Phase 2, which is complete. It costs roughly 400 lines, no dependency,
and no UI, so it does not touch `UI-SPEC.md` or the Directive §5 planning sequence.

**It stays in the backlog anyway, on scheduling, not merit.** V1 has 18 phase
directories and 11 of them are unstarted. Directive §5 hands execution to DeepSeek
**sequentially**, so an added phase is real serial time. Nothing in V1 is blocked on
this, and promoting it buys only an earlier slot in a queue that is not moving.
`REQUIREMENTS.md` files it under V2 and that boundary should hold.

**Promotion trigger (specific, so the next review is a lookup, not a re-argument):**
promote when Phase 8 is verified **and** either an AI tutor is being used against
itembank often enough that shelling out to the CLI is the friction, or V1 reaches
`/gsd-complete-milestone`. Whichever comes first.

**What could not wait, and did not.** Criteria 2 and 3 are one-way doors on code that
Phases 3 through 11 are actively growing. Every API route added without a reserved tool
name, and every payload path added without the evidence-log gate, is retrofit cost paid
later at a worse rate. That constraint is now Extensibility Rule 9 and binds now,
without promoting the phase.

Plans:

- [ ] TBD (promote per the trigger above)

### Phase 999.5: Agent Onboarding & Skill Library (BACKLOG, added 2026-08-10)

**Goal:** Keep the agent on-ramp — `AGENTS.md` and the five repo skills
(`absorb-book`, `curriculum-design`, `guiding-questions`, `author-bank`,
`ocr`) — in sync with the shipped command surface, and add skills as later
phases land. The skills are the living, prose half of the agentic goal: a fresh
agent reads `AGENTS.md`, invokes a playbook, and runs the loop without
scraping HTML or reimplementing scoring.
**Requirements:** TBD (feeds MODEL-04's agent usage contract, Phase 8)
**Depends on:** nothing in this roadmap. It is a maintenance obligation, not
a feature: every later phase that changes the CLI or the session protocol
changes what the skills must say.
**Plans:** 2 plans — [999.5-01](phases/999.5-agent-onboarding-skill-library/999.5-01-SUMMARY.md)
shipped 2026-08-11: skills synced to the shipped surface (hint ladder,
rubric-review, select, coverage, guard, seed), per-tool discovery documented
in README/AGENTS.md (Claude Code, Codex, Gemini CLI, Cursor, Reasonix),
`reasonix.toml` de-shipped (gitignored; portable `reasonix.toml.example`),
and CI now asserts the skill mirrors stay byte-identical and no machine path
leaks into agent docs. [999.5-02](phases/999.5-agent-onboarding-skill-library/999.5-02-SUMMARY.md)
shipped 2026-08-11: README rewritten against the frozen 44-command surface
(grouped index, seven item types incl. `visual`, reconciled Design
boundaries, real repository tree), spec heading corrected to the shipped
type count, ROADMAP phase-status table corrected to STATE.md, CI gates for
README command claims and full schema coverage, and the broken-windows
ledger audited to truth.

**Why this is backlog.** The on-ramp already exists (2026-08-10) and documents
the *shipped* surface — that is why it is truthful. It becomes load-bearing
the moment a phase ships a command that changes what a skill says. The named
trigger points, so the next review is a lookup and not a re-argument:

- **Phase 6 (hint ladder, cursor-hold)** — `guiding-questions` must gain the
  hint tier: `hint`-style command, cursor-hold semantics, `hints_used` in
  `report`. Today it correctly documents `submit` auto-advancing; Phase 6
  changes that sentence.

- **Phase 7 (selection engine)** — `guiding-questions` gains `--objective`/
  `--mode` selection semantics and the inspectable "why this item" reason.

- **Phase 8 (model adapter, agent usage contract)** — the formal
  machine-readable contract (`schemas/agent_usage.schema.json`, `itembank
  usage`) ships; the skills must reference it and stop being the only agent
  contract. Add a model-adapter skill or extend `guiding-questions` with the
  adapter's tier-gated hinting.

- **Phase 11 (curriculum auditor)** — `curriculum-design` gains the
  auditor's citation-per-coverage-claim loop.

- **Phase 999.3 (MCP surface)** — add an MCP skill mapping tools to the
  existing playbooks, or extend `guiding-questions`; the MCP surface must not
  arrive with a second parser/scorer (Extensibility Rule 9).

**Maintenance convention:** the two skill trees (`.agents/skills/` and
`.claude/skills/`) are byte-identical mirrors; editing one requires mirroring
the other in the same change. Skills document only the shipped surface —
a planned command is never written into a skill before it exists.

### Recorded descopes (2026-08-10)

| Item | Disposition |
|---|---|
| Native mobile apps (B2) | Descoped — iOS forbids the Python sidecar. Answer is responsive pages over `--lan` (shipped in Phase 2), a Tailscale recipe, and exports. Documentation, not a phase. |
| Handwriting / stylus input (B10) | Explicitly descoped. |
| OCR of photographed pages (B9) | Deferred to backlog; the photograph→model→draft loop later rides Phase 3.2's generation path. |
| QTI / LTI / xAPI LRS (landscape verdict) | Skipped. Keep Anki TSV + JSON; align evidence **field names** with xAPI vocabulary so a future export is free. Canvas/LTI stays in **999.4** (split out of 999.1 on 2026-08-10). |
| Dyslexia-specific typefaces (B13) | Research is negative. Ship measure and spacing controls instead (covered by the Phase 3.1 render pass). |
| Backup/sync service (B7) | Convention, not code: a documented copy story plus export completeness, and the "one writing home" rule below. |
| TanStack Charts for Phase 10 trends | **Rejected on merit, not on dependency** (`.planning/notes/2026-08-10-tanstack-verdict.md`). Measured 2026-08-10: **0.9.0 pre-alpha**, unstable API, **17 transitive d3 packages**, not vendorable as one file. Phase 10 renders trends as **Python-generated inline `<polyline>` SVG**: zero JS, works in the `.pyz`, the Tauri webview and a `--lan` phone tab identically, carries a real `<table>` fallback for `UI-SPEC.md` §8, and is styled by the existing `SHARED_CSS` semantic tokens. |
| TanStack Table / Query / Router / Start | Rejected on merit. `table-core` is 111 KB + `@tanstack/store` 5.8 KB and exists to sort and filter thousands of rows client-side; itembank renders tables server-side from Python over banks of a few hundred items. The rest presuppose a JS application shell, which is Phase 13's question and not a library question. **What is adopted is TanStack's architecture, which this project already has**: headless separation (Core Value) and invalidation-over-refresh (Extensibility Rule 5). |
| TanStack `virtual-core` | **Not rejected — seeded.** 23 KB, zero imports, one vendorable ESM file, no bundler. Held against a *measured* trigger (a real list over 1000 rows that is measurably slow), because the real cost is the `aria-setsize`/`aria-posinset` work virtualization forces under `UI-SPEC.md` §8, not the 23 KB. See `.planning/seeds/tanstack-virtual-core.md`. |

**M1 — "one writing home" (adopt now, cheap now, expensive later).** The 7900 XTX
machine that is coming makes multi-machine evidence forking a real corruption
risk: two machines appending to two copies of an append-only log produce two
histories that cannot be merged. The convention is that exactly one machine is
the writer at a time, stated in the Phase 2.1 documentation, before a second
machine exists.
