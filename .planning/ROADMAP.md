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
(`.planning/archive/RESEARCH-BRIEF-learning-platform-2026-08-09.md` §7, seven artifacts in
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
The second research pass (`.planning/archive/RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md`
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
- [x] **Phase 2.1: Packaging, Self-Update & Interop Export (INSERTED, moved from Phase 12)** - One double-clickable artifact per OS, a safe self-updater, and a GIFT export that fails loudly rather than wrong — pulled forward so a runnable exe of the Phase 1+2 feature set exists early, and the self-updater ships phases 3-11 as real releases instead of being written and tested last. (completed 2026-08-11)
- [x] **Phase 3: Lesson Format & In-App Reader** - An optional `LESSON` section renders as reading material inside the app, linked to the items it teaches. (completed 2026-08-11)
- [x] **Phase 3.1: Lesson Rich Blocks, Glossary & Style (INSERTED 2026-08-10)** - `## TERMS` + `[[term]]` hover glossary, `[!KEY]` memorizable blocks that round-trip to Anki, one `LESSON-STYLE.md` contract the linter reads, and the callout/figure/print render pass on Phase 4 tokens. (completed 2026-08-11)
- [x] **Phase 3.2: Seeding, Import & Provenance (INSERTED 2026-08-10)** - Content arrives before the features that consume it: Anki `.apkg` import, a human-approves-everything draft→lint→retry seeding loop, and the `[SRC:]`/`[OBJ:]`/`## SOURCES` provenance standard with paraphrase-not-transcribe lint. (completed 2026-08-11)
- [x] **Phase 4: Surface Redesign & Theming** - One shared palette, OS-driven theming, a decluttered question surface, and safe in-page `day` editing. (completed 2026-08-11)
- [x] **Phase 5: Check Item Type & Code Editor** - A `check` item type runs the learner's own code in a real editor and scores it through the one scorer. (completed 2026-08-11)
- [x] **Phase 6: Hint Ladder, Cursor-Hold & Feedback Modes** - A wrong answer holds the cursor, hints unlock one authored tier at a time, and feedback behavior follows session mode. (completed 2026-08-10)
- [x] **Phase 6.2: Executable Textbook Loop (INSERTED 2026-08-10)** - Prose, an inline check the learner must clear to continue, then spaced re-exposure of the same idea — the Execute Program / Runestone loop over the existing lesson, hint, and evidence machinery. (completed 2026-08-11)
- [x] **Phase 7: Selection Engine** - Sessions are assembled by an inspectable rule engine — objective, difficulty, discrimination pairs, no accidental repeats. (completed 2026-08-11)
- [x] **Phase 8: Model Adapter Interface & Tier-Gate Enforcement** - The tutoring model sees the key and writes hints about the learner's actual error; the runtime gates the tier, not the model. (completed 2026-08-11)
- [x] **Phase 9: Subject-Invariant Loop — EMT, Math, CS Integration** - One loop — lesson, hint, verify — carries a learner through EMT prose, Math LaTeX, and runnable CS code. (completed 2026-08-11)
- [x] **Phase 9.1: Audio Drill Export (INSERTED 2026-08-10)** - `itembank export audio` turns an objective into a stem→pause→key→why drill pack, so the commute is study time and the TTS engine is a config entry, not a dependency. (completed 2026-08-11)
- [x] **Phase 10: Retention, Pacing & Trends** - What's due today, a daily cap, and evidence-driven selection weight and decay flagging, with itembank's and Anki's "due" shown apart. (completed 2026-08-11)
- [x] **Phase 11: Closed Authoring Loop & Curriculum Auditor** - A closed spec-draft-lint-retry authoring loop, reused by a syllabus auditor that cites its coverage claims and never over-autonomizes silently. (completed 2026-08-11)
- [ ] ~~**Phase 12: Packaging, Self-Update & Interop Export**~~ - MOVED to Phase 2.1 (2026-08-07) — see Phase 2.1 above. Slot retired, not reused.
- [x] **Phase 13: Desktop Packaging — Tauri Shell over the Python Sidecar** - A signed, installable desktop app whose inside is still the same Python runtime, because porting it would temporarily create a second scorer. (completed 2026-08-10)
- [ ] **Phase 13.5: Reading & Teaching Surface Quality Pass** - The reader and quiz surfaces shipped through Phase 13 meet a commercial quality bar. Planned 2026-08-12 as "Phase 14"; renumbered 2026-08-13 when the source-to-course reframe claimed that number. All 9 plans executed; verification recorded 2026-08-14 with status human_needed (see 13.5-VERIFICATION.md), so the human-verify gates are what keep this box unchecked.
- [x] **Phase 13.9: Walking Skeleton — one real course, end to end (INSERTED 2026-08-14)** (walked 2026-08-24, session 13d56ab15efb4709821a6dd86357a5dc; A9 closed; sitting-fallout plans 13.9-04 and 13.9-05 executed 2026-08-25) - One real source from one live fall course, discovered read-only, bound to at least three cited objectives, one treatment decision per objective, and sat by Weibao through the shipped serve/teach/evidence loop. Ugly is acceptable; simulated is not. Runs beside or after 13.5 waves 3+; may stub course storage with the smallest 14A identity/journal slice; introduces no second parser, scorer, or evidence store. Gate: no 14B-or-later freeze closes before this has been walked. See READINESS-AUDIT-14A.md A9.
- [x] **Phase 14A: Identity, Lifecycle & Operation Prototype** (frozen 2026-08-18) - Stable IDs, revisions, fingerprints, operation journal, and link/import/move/edit/supersede semantics with atomic recovery. Depends on the shipped parser/runtime. Freeze gate: file-fault and external-edit tracer.
- [x] **Phase 14B: Graph & Course Package Prototype** (frozen 2026-08-27) - Typed graph kernel, outline projection, source/treatment bindings, versions, rights, and a minimal package. Depends on 14A. Freeze gate: three-domain graph tracer, clean restore, authorability review.
- [x] **Phase 14C: Source Adapter Registry & Remote Intake (ADDED 2026-08-21, EXECUTED and FROZEN 2026-08-28)** - One adapter contract and one locator sidecar schema for every source medium: PDF, DOCX, PPTX, EPUB, web capture, transcript, audio and video, OCR. Closes IL-20260815-07, which researched PDF and DOCX on 2026-08-17 and deliberately left the sidecar schema open. Remote sources are in scope (USER-VISION-INBOX 2026-08-20 corrects the learner-owned-files reading as interpretation drift); binding fingerprints a captured local snapshot rather than a URL, so citations stay stable and bound material stays readable offline. Boundary is the existing token-gated daemon JSON API, so an external agent harness is an HTTP client rather than a rewrite. Depends on 14A; blocks the source-binding half of 14B. Context: `.planning/phases/14C-source-adapter-registry/14C-CONTEXT.md`. **Plans:** 8 plans, one wave each (the executor runs sequentially). All eight executed; frozen in `.planning/phases/14C-source-adapter-registry/14C-FREEZE.md`, whose coverage audit carries 61 rows with exactly one flagged-unverified (RESEARCH A6, sdist build-script inspection, never promised by any plan). One manual checkpoint is recorded UNRUN: the OCR adapter against a live vision model, which needs a running Ollama.
  Plans:
  - [x] 14C-01-PLAN.md - Freeze the locator sidecar schema, build the registry spine, and land the PDF tracer end to end through one route and one CLI command.
  - [x] 14C-02-PLAN.md - The DOCX adapter including the four OOXML parts python-docx never surfaces, the one hardened zip and XML seam, and the two-file write fault tracer.
  - [x] 14C-03-PLAN.md - The PPTX adapter with spine order from the presentation part and a real speaker-notes flag, plus its hand-assembled gold fixtures.
  - [x] 14C-04-PLAN.md - Web capture: hardened fetch, readable extraction with CSS and text-quote anchors, both snapshot storage paths, both bind policies, and the read-time staleness advisory with its route and command.
  - [x] 14C-05-PLAN.md - Transcript intake for SRT, WebVTT, and plain bracketed timestamps through one timestamp grammar with no third-party dependency.
  - [x] 14C-06-PLAN.md - The OCR adapter wrapping the existing local-Ollama skill, with an honestly degraded locator the schema enforces.
  - [x] 14C-07-PLAN.md - EPUB import on stdlib zipfile and xml.etree, with the ebooklib AGPL parking recorded in two durable places.
  - [x] 14C-08-PLAN.md - Register the ASR adapter as a named refusal, discharge the VENDORED.md obligation with a CI checksum gate, and freeze the phase with a multi-source coverage audit.
- [x] **Phase 15A: Director & Treatment Policy** (frozen 2026-08-30) - Treatment recommender, source scope, rights/egress, autonomy levels, and checkpoints. Depends on 14B. Freeze gate: four-subject recommendation review.
- [x] **Phase 15B: Quality, Blueprint & Acceptance** (frozen 2026-08-30) - Blueprint fidelity, course audit, accepted revision, and staleness/dependency impact. Depends on 15A. Freeze gate: lesson-plus-practice acceptance tracer.
- [x] **Phase 16A: Semantic Capability & Activity Contract** (frozen 2026-08-28) - Lesson roles, activity-purpose matrix, capability profiles, and media/citation policy. Depends on 14B and the assessment runtime. Freeze gate: portable rich-lesson stress corpus.
- [x] **Phase 16B: IA, Modes & Recovery Contract** (frozen 2026-08-28) - Core loops, routes, resume, jobs, approvals, and offline/help/error states. Depends on 14A and 16A. Freeze gate: full storyboard and interruption scenarios.
- [x] **Phase 16C: Strategies, Notes & Prototype Convergence** (frozen 2026-08-30) - Notes, learner artifacts, finite strategies, progress comprehension, and legacy upgrade. Depends on 14B, 16A, and 16B. Freeze gate: cross-subject missing-feature suite.
- [x] **Phase 16D: Paced Lesson Projection & Checkpoints (ADDED 2026-08-31, frozen 2026-09-01; the sat-through review is deferred to Weibao)** - A `paced` presentation of an already authored lesson: authored step markers read through a precedence ladder (explicit `[STEP: id]`, else configured heading level, else the whole document, which is today's behaviour), a jump-only table of contents, gates on attempted never correct, checkpoint items scored by the one scorer into the one evidence store inside a distinct lesson-run session whose attempts blueprint denominators exclude by default, and tiered wrong-answer disclosure released by the runtime (rule out and confirm the learner's own picks, then touched rationale, then the full key). Decisions: `.planning/archive/DECISIONS-PACED-LESSON-2026-08-28.md` D-PACED-1/2/3 (answered under Weibao's quoted 2026-08-28 delegation), IL-20260828-01/02/03. Depends on 16A and 16B (both frozen) plus the shipped Phase 6 feedback and 6.2 gate-band machinery; independent of 17A/17B. Plans: `.planning/phases/16D-paced-lesson/` (4 plans, planned 2026-08-31). Freeze gate: the paced-lesson tracer plus Weibao's sat-through review.
- [x] **Phase 17A: Visual System & Component Foundation (frozen 2026-09-01; the A11Y-01 human pass is deferred to Weibao and `theme.DEFAULT_ACCENT` stays teal until it lands)** - Tokens, three themes, seventeen primitives, the shared shell, the agent tab, and the shelf home. Depends on 16B and 16C. Freeze gate: same-flow visual comparison and accessibility QA.
- [ ] **Phase 17B: Production Vertical Tracer** - A polished unit from discovery through restore. Depends on all prior subphases. Freeze gate: end-to-end gates G1 through G11. **In execution (2026-09-03):** 17B-01 and 17B-02 executed 2026-09-01; 17B-03 in flight; 17B-04 unstarted. Gates G1, G2, G3, G7 pass; G4, G5, G6, G8 to G11 pending (`17B-GATES.md`). The milestone exits through this phase.
- [ ] **Phase 17C: Maintenance and Restore Audit (registered 2026-08-17)** - Clean-machine restore sweep across every accepted item, loss-report completeness, maintenance-owner sweep. Depends on 17B. Audit run 2026-09-05 (`17C-AUDIT.md`): drill passes, owner sweep clean at 49 of 49, and five silent losses found and routed (F-LOSS-1 to F-LOSS-5). Open only on Weibao's acceptance of the report.
- [ ] **Phase 18: External-User v1 — a friend can install and use this (ADDED 2026-08-14; plans 01 to 03 executed 2026-09-01 to the human gate, ahead of the stated 17B dependency; row 7, the second person's cold install, is deferred to Weibao and the close is conditional on it)** - The six-criterion bar in READINESS-AUDIT-14A.md A10: install without folklore, agent-guided onboarding from the public repo, first-run self-explanation, scope honesty, stranger-safe privacy defaults, and errors that name the next safe action. Criteria 1, 2, and 5 are largely shipped (Phase 2.1/13 packaging, the README onboarding section, the disclosure-gated updater) and get verified as they land; the phase closes after 17B with a real cold install by a second person. Fires V2-DEL-01's signing decision. Registered capability on this phase's runway (2026-08-14, vision inbox): **agent-facing update and capability disclosure**, where the app tells an agent the installed version is outdated and what features and contracts arrived, machine-readably, building on the shipped `update`/`usage`/`schema` surfaces, with a matching update path for the skill library. Future phase candidate; may land earlier as a cheap additive manifest. **Two-shell scope folded in (2026-08-16, IDEA-LEDGER IL-20260816-02):** the product ships as two shells over the one runtime: the installed app (this phase's packaging work, which resolves the IL-20260815-11 packaging conflict) and a web surface reached in a browser, meaning the learner's own runtime served to a browser, loopback today. Both shells are clients of the one runtime; this phase's cold-install verification covers whichever shells have shipped, and no second scoring authority may exist in either. A hosted multi-tenant web service stays out of scope under the no-accounts and evidence-on-disk rules. The shell question is closed (2026-08-17 correction of stale text): 17A-CONTEXT D-08 makes the browser-served UI the single canonical shell, and the packaged app wraps the same served pages, so this phase packages one shell rather than choosing between two. Details block added 2026-08-17 before the subphase-sequence section.

**Superseded 2026-08-13 - flat Phase 14 to 17 sequence (historical rationale).** The nine subphases above replace the four broad phases below, per `.planning/research/phase-16/14-synthesis.md` sections 14 and 15. The originals are preserved here as rationale, not deleted. The high-level order (durable course and file semantics, then AI course direction, then logical learning contracts, then visual productization) remains correct; the four phases were too coarse and placed some Phase 16 discoveries after Phase 14 format commitments. Full historical detail is preserved in the Phase Details section below under "Superseded flat sequence (historical rationale)."
> - **Phase 14: Course Workspace & Source Binding** - Make the course the primary object; safely discover and bind sources, objectives, prerequisites, treatments, existing lessons/banks, and gaps through a course shelf/map/source workspace.
> - **Phase 15: AI Course Director & Quality Pipeline** - Let hosted or local agents recommend readings/treatments, generate and review missing artifacts, follow standardized-test or knowledge-exam blueprints, and interpret evidence with explicit uncertainty.
> - **Phase 16: Learning Flow & Lesson Capability Contract** - Research and specify the course journey, lesson capabilities, question purposes, portable authoring contract, interactions, accessibility, media policy, and agent guidance.
> - **Phase 17: Visual System & Comprehensive Guided Learning UI** - Establish the visual language and implement the approved course journey as a polished, responsive, accessible, progressively enhanced learning experience.

**Revision 2026-08-13 — source-to-course reframe.** Completed phases remain
the foundation, but the bank is no longer the primary navigation unit. The
binding scope, AI role, quality contract, learner workspace, and four-phase
tracer sequence live in `.planning/SOURCE-TO-COURSE.md`. Phase 14 planning
begins there rather than extrapolating the old bank/auditor framing.

**Update 2026-08-13 - subphase reframe.** The four broad phases have been
resequenced into nine subphases (14A, 14B, 15A, 15B, 16A, 16B, 16C, 17A, 17B),
per `.planning/research/phase-16/14-synthesis.md` section 15. The subphase
table, its dependencies and freeze gates, and the new roadmap governance clauses
(prototype before durable commitment; the implementation-readiness and
maintenance/restore audits; the capability runway; and the permanent rejection
ledger) are recorded in the Phase Details section under "Next-milestone subphase
sequence."

**Revision 2026-08-14 - walking skeleton, external-user v1, executor bar.**
Three adjustments from the 2026-08-14 direction review (vision source:
`USER-VISION-INBOX.md` entry 2026-08-14; gates: `READINESS-AUDIT-14A.md` A9 and
A10). First, the sequence proved durability first and learner value last, with
the only end-to-end tracer (17B) as the final gate while the live fall courses
begin within weeks; **Phase 13.9 inserts a walking skeleton** so a thin real
slice is walked before any 14B-or-later freeze closes, and its recorded
evidence becomes the calibration corpus later plans keep asking for. Second,
**Phase 18 names the external-user v1 bar**, revising the "Users: One"
constraint to one learner per installation with external installations
supported. Third, every next-milestone plan is written to the **lesser-model
executor bar** in `PLANNING-DIRECTIVES.md` section 5: a Sonnet-class executor
must be able to complete it without inventing a decision.

## Phase Details

Completed phase details (Phases 1-13.5, and 999.1/999.4/999.5) moved to
`ROADMAP-ARCHIVE.md` on 2026-08-20. The checklist in `## Phases` above is unchanged.

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
`.planning/archive/RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md` (the lesson-style registry
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
| 3.2 Seeding, Import & Provenance | 5/5 | Complete | 2026-08-11 |
| 4. Surface Redesign & Theming | 6/6 | Complete | 2026-08-11 |
| 5. Check Item Type & Code Editor | 7/7 | Complete | 2026-08-11 |
| 6. Hint Ladder, Cursor-Hold & Feedback Modes | 2/2 | Complete    | 2026-08-10 |
| 6.1 Interactive Visual Assessment Protocol | 3/3 | Complete | 2026-08-11 |
| 6.2 Executable Textbook Loop | 4/4 | Complete | 2026-08-11 |
| 7. Selection Engine | 6/6 | Complete (roadmap gaps in 07-VERIFICATION.md) | 2026-08-11 |
| 8. Model Adapter Interface & Tier-Gate Enforcement | 6/6 | Complete | 2026-08-11 |
| 9. Subject-Invariant Loop — EMT, Math, CS Integration | 5/5 | Complete | 2026-08-11 |
| 9.1 Audio Drill Export | 4/4 | Complete | 2026-08-11 |
| 10. Retention, Pacing & Trends | 6/6 | Complete | 2026-08-11 |
| 11. Closed Authoring Loop & Curriculum Auditor | 5/5 | Complete | 2026-08-11 |
| 12. ~~Packaging, Self-Update & Interop Export~~ | — | Retired (moved to 2.1) | - |
| 13. Desktop Packaging — Tauri Shell over Python Sidecar | 5/5 | Complete    | 2026-08-10 |
| 13.5 Reading & Teaching Surface Quality Pass | 9/9 | Plans executed; D1 and D2 closed and RTS-04 AGENT VERIFIED by the 2026-08-26 agent re-measure; the remaining human-verify tail is what keeps the box unchecked | - |
| 13.9 Walking Skeleton — one real course, end to end | 5/5 | Complete (A9 closed; Weibao's two-sentence reaction still owed, named in A9) | 2026-08-25 |

Table corrected 2026-08-15 against the phase directories (plan SUMMARY files and
VERIFICATION verdicts), which are the source of truth. Rows 3.2, 5, 8, 9, 11,
and 13.5 were stale; the 13.5 row was still labeled "14" from before the
2026-08-13 renumbering. Next-milestone subphases (14A through 17B, 18) are
tracked in the "Next-milestone subphase sequence" section, not this v1.0 table.

## Backlog

> **Backlog reviewed 2026-08-10** (`/gsd-review-backlog`). Nothing promoted, nothing
> removed, one entry split. The reasoning for each verdict is recorded inline below so
> the next review argues with it rather than re-deriving it.

### Small enhancements (recorded 2026-08-10)

| Item | Disposition |
|---|---|
| OLED / true-black theme mode | Folded into Phase 17A on 2026-08-17 as plan 17A-05 (wave 3): one `theme` enum value (`oled`) plus a true-black token set (`bg` `#000000`, dimmer card/chip, semantic contrast re-verified through the stylesheet invariants) and the settings theme option. 17A is the theming-adjacent phase this row was waiting for. Originally raised from Phase 4 UAT (2026-08-10). |
| 13.5 defect D1: reading measure renders 422px, not the contracted 531px (66 chars) | To be fixed (recorded 2026-08-16, agent browser pass). Mechanism and fix candidates in `phases/13.5-reading-teaching-surface-quality-pass/13.5-GATES.md` D1: `--measure-prose:59ch` resolves against the 16px `.wrap` font instead of the 18px reading face, and `.card` padding eats 48px more. CSS-only fix plus a corrected `stylesheet_roundtrip` pin. Executable plan written 2026-08-17: `.planning/quick/260817-q7d-fix-135-defects-d1-d2/260817-q7d-PLAN.md` (supersedes the 2026-08-16 task chip). Blocks the RTS-04 gate from closing. |
| 13.5 defect D2: quiz context band shows "Item 1 of 0" on first paint | To be fixed (recorded 2026-08-16, same pass). `span#tot` is server-rendered as 0 and corrects only after interaction; server-render the real total in the quiz page template plus a `daemon_roundtrip` first-paint assertion. Same executable plan as D1: `.planning/quick/260817-q7d-fix-135-defects-d1-d2/260817-q7d-PLAN.md` (2026-08-17). |
| 13.5 remaining human-verify tail | To be verified, not fixed (2026-08-16). After the agent browser pass, the only rows still needing a human are: real screen-reader announcement behavior (never agent-certifiable), the gloss bottom-sheet painted geometry on a touch device or displayed pane, the script-free and truly network-free ladder walkthrough, the perceptual font-face comparison, and an optional real-200%-zoom rasterization spot-check. Procedures in `13.5-GATES.md`. These are what keep 13.5's box unchecked; nothing else in the phase is open. |

Completed backlog phase details moved to `ROADMAP-ARCHIVE.md`.

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

**2026-08-17 review verdict: KEEP, post-reframe (IDEA-LEDGER IL-20260817-02).**
Re-argued against the source-to-course scope: direct source reading
(SOURCE-TO-COURSE step 4) makes the trigger more reachable because it puts
un-authored running prose in front of the learner, but the trigger itself
stands unchanged and nothing is built until per-word tracked status is wanted
over that surface. Sharpened revisit trigger: a recorded learner request for
per-word lookup or tracked word status over a source-reading treatment, or a
language-learning course entering the course shelf.

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

**2026-08-17 review verdict: PROMOTED per its own trigger (IDEA-LEDGER
IL-20260817-03).** Phase 8 is verified and the v1.0 milestone completed
2026-08-11, so the trigger's second disjunct fired; the review is the lookup
the 2026-08-10 entry promised. The source-to-course reframe strengthens the
case: agents are first-class clients of the runtime, Extensibility Rule 9 has
prepaid the retrofit cost on every route since 2026-08-10, and Phase 18's
agent-facing capability disclosure manifest is a natural payload of the MCP
`server/discover` surface. Sequencing: after 17B, beside Phase 18 (may run in
parallel with it); nothing in the 14A through 17B spine depends on it, so it
does not interrupt the milestone. Scope, the ten success criteria, and the
three named unknowns above carry unchanged into planning. The heading stays
999.3 until its planning session assigns the phase directory.

Plans:

- [ ] TBD (plan at promotion slot: after 17B, beside Phase 18)

### Phase 13.9: Walking Skeleton — one real course, end to end (INSERTED 2026-08-14)

**Goal**: Before the deep subphases freeze anything, Weibao studies one real
unit of one live fall course through a thin, real, end-to-end slice of the
source-to-course loop, and the recorded evidence becomes the calibration corpus
the later plans cite.
**Mode:** tracer
**Depends on**: shipped runtime; Phase 13.5 waves 3+ scheduled before or beside
it (or explicitly waived with a reason); may consume the smallest 14A
identity/journal slice but never waits for 14A to complete.
**Binding spec:** `READINESS-AUDIT-14A.md` section A9. Summary of the success
criteria (A9 wording governs on any divergence):

  1. One real source from one live fall course (EMT, Math 1400, or CSCI 1100),
     discovered and bound read-only, mapped to at least three cited objectives.
  2. A recorded treatment decision per objective: at least one direct reading
     and at least one generated lesson plus practice.
  3. Weibao sits the result end to end through the shipped
     serve/lesson/study/teach/evidence loop. Ugly is acceptable; simulated is
     not.
  4. No second parser, scorer, or evidence store; course-level storage may be
     a stub over the smallest 14A identity/journal slice.
  5. The sitting's evidence lands in the one store, and at least one later
     plan (14B, 15A, or warning calibration) names it as calibration corpus in
     place of a synthetic fixture.

**Gate it imposes on the sequence:** no 14B-or-later freeze commits before this
skeleton has been walked. Freeze gates the skeleton can exercise cheaply
(graph-to-outline, the rich-lesson stress corpus) cite skeleton artifacts
rather than inventing parallel fixtures.

### Phase 14A: Identity, Lifecycle & Operation Prototype

**Goal**: Every durable object carries a stable opaque ID, a revision record,
and a normalized fingerprint; every durable write goes through an operation
journal with compare-and-swap semantics and atomic recovery; and link, import,
copy, move, edit-in-place, and supersede are six distinct journal operations
with distinct provenance effects. An external edit becomes visible stale or
conflict state, never a silent overwrite.
**Depends on**: shipped parser/runtime. The implementation-readiness audit gate
is satisfied by `AUDIT-REPORT-14A-2026-08-14.md`.
**Freeze gate:** the file-fault and external-edit tracer (plan 14A-04) passes
end to end on the synthetic corpus; identity, journal, and operation semantics
freeze only when it is green.
**Requirements**: FILE-01, FILE-02, FILE-03, ID-01, ID-02, RIGHTS-01, RELIABILITY-01
**Phase plan:** `.planning/phases/14A-identity-lifecycle-operation/14A-BRIEF.md`
(plans 14A-01 identity kernel, 14A-02 operation journal and compare-and-swap
writes, 14A-03 operation vocabulary and external-edit states, 14A-04 the
file-fault and external-edit tracer).
**Plans:** 4 plans, expanded to the `PLANNING-DIRECTIVES.md` section 5 executor
bar on 2026-08-14. Waves are strictly sequential (1, 2, 3, 4) because each plan
extends the modules the previous one created.

Plans:
- [ ] 14A-01-PLAN.md (wave 1) identity kernel: `identity.py` opaque ids,
  normalized fingerprints, revision records, the restrictive rights slot,
  bounded component ids, plus `discovery.py` read-only multi-root walking and
  the synthetic corpus generator. The slice Phase 13.9 consumes.
- [ ] 14A-02-PLAN.md (wave 2) operation journal: `journal.py` compare-and-swap
  writes, atomic commit, the append-only journal with undo pointers, replay,
  and crash, disk-full, and permission-denied fault injection.
- [ ] 14A-03-PLAN.md (wave 3) operation vocabulary: six distinct operations
  over one write path, external-edit conflict states, explicit reconciliation
  with no merge path, and the per-operation rights gate.
- [ ] 14A-04-PLAN.md (wave 4, not autonomous) the file-fault and external-edit
  tracer: eight G3 scenarios end to end, measured D-12.6-10 quantities, the
  reflow-normalization corpus check and its blocking decision checkpoint, and
  the freeze record.
**Walking-skeleton coupling:** Phase 13.9 may stub course-level storage over
the smallest 14A identity/journal slice (14A-01 plus the journal append of
14A-02); plans are ordered so that slice lands first (ROADMAP Phase 13.9,
audit A9).

### Phase 14B: Graph & Course Package Prototype

**Goal**: The durable instructional spine is a constrained typed graph of
concepts and objectives stored in one readable, diffable course sidecar per
course; a deterministic outline projection renders it as plain Markdown from
the authored structural order; sources and treatments bind to objectives with
operation-specific rights enforced at the binding rather than at export;
objective splits, merges, and renames produce reviewed migration proposals that
never transfer historical evidence; and a course exports as a minimal package
that a clean, offline machine can restore against a manifest with every loss
reported by name.
**Depends on**: Phase 14A. Every 14A signature this phase imports was read from
plan text and not from source at planning time, so plan 14B-01 opens with a
recorded precondition check that halts by name on any divergence.
**Freeze gate:** three legs, all three green in one place: the three-domain
graph tracer (plan 14B-06), the clean restore drill, and a human authorability
review. No 14B freeze closes before Phase 13.9 has been walked, checked as an
explicit precondition rather than assumed.
**Requirements**: GRAPH-01, GRAPH-02, GRAPH-04, PORT-03
**Phase plan:** `.planning/phases/14B-graph-course-package-prototype/`
(`14B-RESEARCH.md`, `14B-PATTERNS.md`, `14B-VALIDATION.md`; no CONTEXT.md, the
same precedent Phase 14A set, with the binding decisions in
`archive/DECISIONS-PRE-14A-2026-08-14.md`, `REQUIREMENTS.md`, and
`PLANNING-DIRECTIVES.md`).
**Plans:** 6 plans, written to the `PLANNING-DIRECTIVES.md` section 5 executor
bar. Waves are strictly sequential (1 through 6) because each plan extends the
modules the previous one created. Four plans are not autonomous: plans 01, 04,
05, and 06 each carry a blocking `checkpoint:decision` gating a one-way door.

Plans:
- [x] 14B-01-PLAN.md (wave 1, not autonomous) preconditions and the end-to-end
  tracer: verify Phase 14A landed or halt by name; settle the Phase 13.9
  `course.md` collision with a named non-destructive supersession path; then one
  synthetic objective from mint through edge, sidecar compare-and-swap write,
  outline projection, package export, and clean restore, creating `graph.py`,
  `course.py`, and `course_package.py` in their thinnest production form.
- [x] 14B-02-PLAN.md (wave 2) the graph kernel: the frozen four-name edge
  vocabulary with its degrade path and five GRAPH-02 carried fields, structural
  containers accepting any local label without a schema change, the
  deterministic outline projection with order validation and a stable
  topological fallback, the published `schemas/course_graph.schema.json`, and
  the byte-identical format-additivity fixture.
- [x] 14B-03-PLAN.md (wave 3) bindings and rights: source and treatment
  bindings gated by `identity.rights_granted` at bind time, TREAT-01's eleven
  treatment kinds mapped to the rights they consume, imported scopes as
  immutable versions with overlay records, and the version-migration prototype.
  Confirms D-12.6-8 and D-12.6-9, both of which read "pending confirmation at
  14B plan time".
- [ ] 14B-04-PLAN.md (wave 4, not autonomous) migration: `migrate` as an
  additive `journal.RECORD_TYPES` member with `OPERATION_TYPES` left at exactly
  six, reviewed migration proposals for split, merge, rename, demand change,
  and overlay, and a split-and-rename scenario proving the evidence store is
  untouched and each new identity reads unknown.
- [ ] 14B-05-PLAN.md (wave 5, not autonomous) the minimal package: a
  BagIt-inspired manifest hand-rolled in the standard library, a rights gate on
  payload inclusion, five named loss categories, a clean-machine offline restore
  drill that recomputes every fingerprint, and the Zip Slip containment guard on
  the optional archive transport.
- [ ] 14B-06-PLAN.md (wave 6, not autonomous) the freeze gate: the three-domain
  tracer implementing all four requirement Fixture sentences, the authorability
  review a human signs, the Phase 13.9 precondition check, and the freeze record
  or a `Freeze withheld` section naming the missing leg.
**Prototype-before-freeze coupling:** `PLANNING-DIRECTIVES.md` section 3a
requires the graph-to-outline projection and the version migration to be
prototyped before any course schema freeze. Plan 14B-02 delivers the first and
plan 14B-03 the second; Phase 14B is that prototype and its freeze record
states explicitly that it is not the course schema freeze.

### Phase 15A: Director & Treatment Policy

**Goal**: An approved agent client, hosted coding-agent-class or registered
local backend, can recommend an explicit, reviewable treatment for every
objective from the eleven-kind treatment vocabulary, with direct reading as a
complete result and generation never the automatic default; every
objective-to-source coverage claim carries a stable locator, confidence, and
one of five states (covered, thin, missing, conflicting, unknown) with heading
similarity never producing covered; every agent operation runs through the one
operation protocol over the Phase 14A journal with declared intent, scope,
rights, egress, checkpoints, resume, and undo; hosted operations minimize and
disclose exact egress; autonomy levels bound what an agent may do without
review; and backend loss leaves all core work local and model-free.
**Depends on**: Phase 14B (typed graph, source and treatment bindings, rights
enforced at the binding). Phase 14B is planned but not yet executed, so every
14B and 14A signature this phase imports is read from plan text at planning
time; the first 15A plan opens with a recorded precondition check that halts by
name on any divergence, the same pattern plan 14B-01 set.
**Freeze gate:** the four-subject recommendation review: one recommendation
operation over four synthetic subject outlines (EMT, Math 1400, CSCI 1100, and
one standardized-exam blueprint), including one objective bound to direct
reading as a complete result and one left untreated, replayed step by step from
the operation journal against the protocol checklist, run through a mock hosted
and a mock local backend with identical artifacts and journals, with the egress
log listing exactly the approved synthetic source spans.
**Requirements**: TREAT-01, TREAT-02, RIGHTS-02, RELIABILITY-02, AGENT-01, AGENT-02
**Phase plan:** `.planning/phases/15A-director-treatment-policy/`
(`15A-RESEARCH.md`, `15A-PATTERNS.md`, `15A-VALIDATION.md`; no CONTEXT.md, the
same precedent Phases 14A and 14B set, with the binding decisions in
`REQUIREMENTS.md`, `PLANNING-DIRECTIVES.md`, `archive/DECISIONS-PRE-14A-2026-08-14.md`,
and the phase-16 synthesis).
**Plans:** 6 plans, written to the `PLANNING-DIRECTIVES.md` section 5 executor
bar. Waves are strictly sequential (1 through 6) because each plan extends the
module the previous one created. Two plans are not autonomous: plan 01 carries
two blocking `checkpoint:decision` tasks gating one-way doors, and plan 06
carries the blocking human recommendation review.

Plans:
- [ ] 15A-01-PLAN.md (wave 1, not autonomous) preconditions, the two one-way
  doors, and the end-to-end tracer: verify Phases 14A and 14B landed or halt by
  name; settle the recommendation wire boundary and where the egress record
  lives; then one synthetic objective from declared intent through a bounded
  request, the shipped `model_adapter.invoke` boundary, candidate validation, a
  live rights check, and a treatment binding with the operation, its
  checkpoint, and its egress on one journal entry, creating `director.py` in
  its thinnest production form.
- [ ] 15A-02-PLAN.md (wave 2) the treatment recommender: the closed eleven-kind
  vocabulary read from one place, deterministic ranking tie-broken by
  vocabulary order, direct reading as a complete result, an untreated report
  computed from bindings and never from proposals, three outcomes and no
  fourth, and the empty, ordering, and stability edges.
- [ ] 15A-03-PLAN.md (wave 3) coverage claims and states: NFC and line-ending
  locator normalization with no case folding and no fuzzy matching, six ordered
  classification rules with `covered` reachable only through a resolved
  locator, one fixture claim per `graph.BINDING_STATES` member, and a
  heading-similarity decoy that reads unknown.
- [ ] 15A-04-PLAN.md (wave 4) rights, egress, and autonomy: approved spans
  drawn only from sources whose right reads granted in the live registry, an
  exact and ordered egress record with named omissions and no secrets, the
  `settings.agent_policy` block with restrictive defaults, and an
  over-declaring agent refused by name rather than silently narrowed.
- [ ] 15A-05-PLAN.md (wave 5) the operation protocol over the one journal: the
  frozen thirteen-step vocabulary compared as exact ASCII, replay from the
  journal alone, interruption at each of the thirteen phases with resume and
  reverse through `journal.undo`, the `agent_operation` coupling test in
  `tests/journal_roundtrip.py`, and the core loop proven operable with every
  backend removed.
- [ ] 15A-06-PLAN.md (wave 6, not autonomous) the freeze gate: the four-subject
  recommendation review tracer implementing all six requirement Fixture
  sentences, the human review a person signs, the Phase 13.9 precondition
  check, and the freeze record or a `Freeze withheld` section naming the
  missing leg.
**Prototype-before-freeze coupling:** the 15A freeze covers the recommendation,
coverage, egress, autonomy, and protocol surfaces only. It is explicitly not
the course schema freeze, not a lesson-profile freeze, not an agent job
protocol freeze, and not a learner-facing surface freeze, and its freeze record
says so.

### Phase 15B: Quality, Blueprint & Acceptance

**Goal**: A drafted lesson treatment and a drafted practice question set become
accepted, durable course state only through an explicit, reviewable acceptance
pipeline: formal assessment fidelity requires a cited, versioned blueprint
(construct, domain weight, demand, format, difficulty, timing, tools, feedback
conditions) and no surface claims exam fidelity without one; practice-generated
questions stay drafts until the parser, lint, review, blueprint, and runtime
gates all pass, composed from the shipped `model.parse_bank`, `model.lint`,
`authoring.quality_gate`, and `runtime.score_response` plus one new pure
blueprint-fidelity classifier, never a second parser or scorer; a course audit
aggregates treatment state, coverage state, quality findings, and blueprint
compliance into one cited report that names which existing state vocabulary
each claim came from and mints no fourth; a reviewer accepts or rejects
migrations and drafts through the one 14A journal write path with a live
rights and autonomy re-check at accept time; external, source, or version
changes mark dependents stale by fingerprint comparison, and a stale binding
or proposal is blocked from acceptance until a rebind, migrate, supersede, or
retain review is recorded; and evidence-based proposals name their observation
window, denominator, missing signals, and uncertainty, refuse a mastery
percentage over sparse evidence, and remain recommendations until the learner
or a deterministic selection policy acts.
**Depends on**: Phase 15A (director module, operation protocol, autonomy and
rights gates, coverage classifier). Phases 14A, 14B, and 15A are planned but
not yet executed, so every signature this phase imports is read from plan text
at planning time; the first 15B plan opens with a recorded precondition check
that halts by name on any divergence, the same pattern plans 14B-01 and 15A-01
set, extended to check for a `15A-FREEZE.md` record.
**Freeze gate:** the lesson-plus-practice acceptance tracer: one synthetic
cited blueprint paired with one drafted lesson treatment and one drafted
practice set, walked from draft through all five gates to journaled
acceptance; the exam-fidelity claim appearing only after the fifth gate; a
mid-flow synthetic source edit marking dependents stale and blocking
acceptance until a recorded disposition; a migration proposal accepted and a
second one rejected through the reviewer path; and a sparse-evidence proposal
(two attempts on one objective) that names its window, denominator, and
uncertainty and refuses a mastery percentage, all replayed from the operation
journal.
**Requirements**: ACTIVITY-02, RELIABILITY-03, AGENT-03
**Plans:** 7 plans
**Phase plan:** `.planning/phases/15B-quality-blueprint-acceptance/`
(`15B-RESEARCH.md`, `15B-PATTERNS.md`, `15B-VALIDATION.md`, `COVERAGE.md`; no
CONTEXT.md, the same precedent Phases 14A, 14B, and 15A set, with the binding
decisions in `REQUIREMENTS.md`, `PLANNING-DIRECTIVES.md`, and the phase-16
synthesis).

Plans:
- [ ] 15B-01-PLAN.md (wave 1, not autonomous) preconditions and the two one-way
  doors: the recorded check against 14A, 14B, and 15A plus all three freeze
  records, then D-15B-1 (where the blueprint, staleness, audit, and acceptance
  code lives) and D-15B-2 (where a blueprint lives, which write path records an
  acceptance, and which journal record type it uses).
- [ ] 15B-02-PLAN.md (wave 2) the acceptance tracer and the five-gate pipeline:
  one drafted set and one cited blueprint through parser, lint, review,
  blueprint, and runtime to an accepted write; `blueprint.py`,
  `schemas/blueprint.schema.json`, and the additive `gates.blueprint_findings`
  array.
- [ ] 15B-03-PLAN.md (wave 3) staleness and the four dispositions: a fingerprint
  comparison recomputed on read, RELIABILITY-03's own rebind, migrate,
  supersede, and retain vocabulary, and the hard block on acceptance until a
  matching review is recorded.
- [ ] 15B-04-PLAN.md (wave 4) accepted revision: `graph.accept_migration` and
  `graph.reject_migration` closing the gap 14B-04 named, their write through
  `course.write_course`, the live autonomy re-check at accept time, and exactly
  one new `journal.RECORD_TYPES` member.
- [ ] 15B-05-PLAN.md (wave 5, not autonomous) the cited course audit that names
  which of three existing vocabularies each claim came from and mints no
  fourth, plus D-15B-3 (where the course audit report shape lives).
- [ ] 15B-06-PLAN.md (wave 6) AGENT-03 evidence-based proposals: observation
  window, denominator, included and missing signals, uncertainty, competing
  explanations, and the recursive ban that keeps sparse evidence from becoming
  a mastery percentage.
- [ ] 15B-07-PLAN.md (wave 7, not autonomous) the freeze gate: the
  lesson-plus-practice acceptance tracer, the human acceptance-quality review,
  and the freeze record or its named withholding.
**Prototype-before-freeze coupling:** the 15B freeze covers the blueprint,
audit, acceptance, staleness, and proposal-discipline surfaces only. It is
explicitly not the course schema freeze, not a lesson-profile grammar freeze,
not an agent job protocol freeze, and not a learner-facing surface freeze, and
its freeze record says so.

### Phase 16A: Semantic Capability & Activity Contract

**Goal**: One parsed canonical lesson renders every semantic teaching role
(key idea, warning, prerequisite, misconception, expert tip, worked example,
counterexample, source excerpt, term and definition, uncertainty, summary,
inline check, hint, accessible visual interaction) in both continuous reader
and guided modes, composed from shared primitives through the one parser, with
a worked example or concrete case placed before the formal definition by
default and any override recorded; every semantic capability declares an
accessible-behavior, offline-fallback, renderer-availability, version,
validation, and known-limits profile, every media asset carries rights,
credit, accessible-alternative, derivation, availability, and integrity
metadata, and an unavailable renderer shows the static instructional path;
registered output modes (notebook page, outline, Cornell notes, concept map,
glossary, formula sheet, timeline, comparison table, study guide,
source-extracted notes) compose from shared note and activity schemas plus
provenance, and an unregistered mode stays a backburner catalog entry naming
its shared primitive, dependency, cost, and trigger; every activity declares
purpose, cognitive demand, objective, stimulus or source, response schema,
retry behavior, feedback and disclosure policy, evidence status,
accessibility equivalence, and static fallback, with existing response forms
serving many purposes and a new item type minted only when scoring semantics
or response structure cannot be expressed safely; the runtime alone scores,
grants keyed disclosure, selects authoritative assessment behavior, and
writes assessment evidence, refusing every scripted attempt by an agent,
note, or import to leak a key, invent a score, auto-grade prose, or edit a
frozen sitting; canonical records carry language and direction, with
localization fixtures covering RTL, mixed code and math direction, CJK,
combining marks, long strings, and localized numbers and units; and the
canonical lesson remains UTF-8 Markdown with shallow metadata and an
additive, versioned semantic profile whose core meaning, captions, citations,
definitions, and media alternatives stay readable outside the app with every
derived view deleted and rebuildable. The shipped hover, focus, and touch
glossary definitions (RTS-05, complete) are the first catalogued capability,
per the reframe note in `REQUIREMENTS.md`.
**Depends on**: Phase 14B (typed graph kernel, outline projection, source and
treatment bindings, course package) and the shipped assessment runtime.
Phases 14A and 14B are planned but not yet executed, so every signature this
phase imports is read from plan text at planning time; the first 16A plan
opens with a recorded precondition check that halts by name on any
divergence, the same pattern plans 14B-01, 15A-01, and 15B-01 set, extended
to check for a `14B-FREEZE.md` record.
**Freeze gate:** the portable rich-lesson stress corpus: one synthetic lesson
exercising every semantic teaching role plus one unknown optional and one
unknown required semantic, rendered in both continuous reader and guided
modes; the medical evolving-case fixture with a dated jurisdiction warning
and no premature reveal, and the disputed-timeline fixture preserving
disagreement, locators, and uncertainty; the localization fixture set inside
the corpus; the capability profile fixture with one renderer marked
unavailable showing the static instructional path; the two-output-mode
composition fixture plus one backburner catalog entry; the purpose-first
activity set including one unsupported response form falling back to its
declared static equivalent; the adversarial runtime-authority fixture in
which every leak, invented-score, auto-grade, and frozen-sitting edit
attempt is refused; and the corpus opened outside the app in a plain
Markdown viewer with every derived HTML, index, and cache deleted, staying
readable and rebuilding.
**Requirements**: CAP-01, CAP-02, CAP-03, ACTIVITY-01, ACTIVITY-03, A11Y-02, PORT-01
**Plans:** 10 plans
**Phase plan:** `.planning/phases/16A-semantic-capability-activity-contract/`
(`16A-RESEARCH.md`, `16A-PATTERNS.md`, `16A-VALIDATION.md`; no CONTEXT.md, the
same precedent Phases 14A, 14B, 15A, and 15B set, with the binding decisions in
`REQUIREMENTS.md`, `PLANNING-DIRECTIVES.md`, and the phase-16 synthesis).

Plans:
- [ ] 16A-01-PLAN.md (wave 1, not autonomous) preconditions and the two one-way
  doors: the recorded check against 14A and 14B plus both freeze records, plus
  Phase 13.9 checked directly because 14B's freeze may not close before the
  skeleton is walked, plus the additivity baseline recorded as two golden
  SHA-256 values; then D-16A-1 (promote the semantic-role registry or add the
  seven roles alongside, and the exact role tokens) and D-16A-2 (where the
  capability registry lives and which module owns the media and activity
  grammar). Transcribes D-16A-3 through D-16A-9.
- [ ] 16A-02-PLAN.md (wave 2) the tracer: one authored `[!PREREQUISITE]` block
  travelling parser, capability registry, and both continuous and guided
  renderers end to end, plus the three lesson directives, `capabilities.py`
  with one seeded profile, and the golden-parse additivity proof.
- [ ] 16A-03-PLAN.md (wave 3) CAP-01 expansion: the six remaining role
  registrations, the fourteen-entry `SEMANTIC_ROLE_CATALOG` catalogging seven
  shipped mechanisms rather than rebuilding them, the required-semantic marker
  and both unknown-semantic degradation paths, and the worked-example-first
  default with its recorded override.
- [ ] 16A-04-PLAN.md (wave 4) CAP-02 profiles: fifteen capability support
  profiles with all six declared fields, `schemas/capability_profile.schema.json`
  validated by the shipped `schema_validate.py`, and the static instructional
  path proven byte identical against the shipped gate-less check render.
- [ ] 16A-05-PLAN.md (wave 5) CAP-02 media: the `## MEDIA` registry through the
  one `_preamble_section` boundary rule, the figure renderer's three readable
  degraded paths, and rights proven declared-not-enforced by a byte-identity
  assertion.
- [ ] 16A-06-PLAN.md (wave 6) ACTIVITY-01: the `## ACTIVITIES` registry, ten
  purposes over the eight shipped response forms with no ninth type minted,
  eleven lint codes, and the declaration-is-not-authority proof.
- [ ] 16A-07-PLAN.md (wave 7) CAP-03: outline and glossary composed from shared
  schemas with no second outline generator, the eight-entry backburner catalog
  with testable triggers, and the derivation proof that no output mode invents
  content.
- [ ] 16A-08-PLAN.md (wave 8) A11Y-02: the ten-constant localization corpus, the
  explicit `[LESSON-DIR: auto]` per-element opt-in that keeps the change
  additive, and the byte-for-byte preservation proof including a precomposed
  and decomposed pair that no normalization may collapse.
- [ ] 16A-09-PLAN.md (wave 9) ACTIVITY-03: three attackers times four attacks
  against the real shipped gates with no mock anywhere, the boundary and
  precision probes, and four attacks on Phase 16A's own new places authored
  text reaches a learner.
- [ ] 16A-10-PLAN.md (wave 10, not autonomous) the freeze gate: the medical
  evolving-case and disputed-timeline fixtures, `build_all_16a`, the PORT-01
  delete-and-rebuild portability proof, the measured tracer report, the human
  contract-legibility review, and the freeze record or its named withholding.
**Prototype-before-freeze coupling:** the 16A freeze covers the semantic role
vocabulary, the capability profile registry, the media and activity grammars,
the registered output modes, the localization metadata, and the portable
canonical format only. It is explicitly not a visual system or token freeze,
not an information architecture or navigation freeze, not a notes or strategy
freeze, not a learner-facing surface freeze, and not a course schema freeze,
and its freeze record says so.

### Phase 16B: IA, Modes & Recovery Contract

**Goal**: The seven core loops (A discover and bind, B design a course, C learn
and construct notes, D practice and test, E evidence and remediation, F author,
review, and accept, G maintain, recover, and leave) are contracted as the
product's end-to-end acceptance surface, each resumable at an exact position
with a next justified action, and an interrupted loop preserves the last
accepted state and exposes the next safe action; a learner moves between direct
source reading, lesson, practice, feedback, and the next course action without
reconstructing context, reading is continuous and scrolls with no paginating
surface, no loop introduces a second parser or scorer, and a Socratic or
tutoring refusal renders as a locked card stating its unlock condition, never
as a chat exchange; the home surface is a course shelf with an exact resume cue
and attention state, each course exposes Overview, Learn, Practice, Test,
Course map (outline first), Sources, Build and review, Evidence, and contextual
Notes, and banks are assessment artifacts inside courses, not the primary
navigation unit; navigation uses stable opaque deep links and anchors, explicit
parent and back semantics, focus and scroll restoration, and the same routes
across wide and narrow layouts (supporting panes stack as destinations on
narrow screens), with chat contextual to an object or operation, never the home
or sole job record; durable agent and maintenance jobs surface in an Activity
view with needs-input, outcomes, and recovery, long jobs never block learning
and never invent a percent when the denominator is unknown, and hosted, local,
and manual continuation share durable checkpoints under the one operation
protocol; the mode layering from synthesis section 8 is contracted so learner
preferences, author strategies, objective constraints, accommodation overrides,
instructor policy, fixed runtime authority, and fixed system safety each name
their controller and never collapse into one settings pile; first launch
offers a clearly synthetic, removable sample course and a skippable,
replayable walkthrough reachable without granting source roots or configuring
an agent; help is offline and routes from named error codes; settings expose
approved roots, model backends, network and egress policy, accessibility,
theme, storage, backups, and update policy, growing the shipped DEL-04 subset
to that list (clause C137, 2026-08-14); and crash, cancellation, offline,
permission-denied, future-schema, and agent-unavailable states preserve the
last accepted state and expose the next safe action, with a model-unavailable
state still allowing reading, scoring, the authored hint ladder, evidence,
and reports.
**Depends on**: Phase 14A (stable IDs, revisions, fingerprints, operation
journal, atomic recovery) and Phase 16A (semantic capability and activity
contract). Phases 14A and 16A are planned but not yet executed, so every
signature this phase imports is read from plan text at planning time; the
first 16B plan opens with a recorded precondition check that halts by name on
any divergence, the same pattern plans 14B-01, 15A-01, 15B-01, and 16A-01 set,
extended to check for a `16A-FREEZE.md` record.
**Freeze gate:** the full storyboard and interruption scenarios: a synthetic
run of each of loops A through G interrupted mid-step, asserting each resumes
at an exact position with a next justified action (FLOW-01 fixture); a
synthetic reading, lesson, practice, and feedback walk with the model backend
disabled, asserting scoring, the authored hint ladder, evidence, and reports
still run through the one runtime (FLOW-02 fixture); the synthetic course
shelf with two fictional courses, one corrupted so it must show its last valid
overview and plain-file access, asserting exact resume cues and every named
course section (APP-01 fixture); the same synthetic deep links replayed across
wide and narrow layouts, asserting focus and scroll restoration and identical
routes in both (APP-02 fixture); and the first-launch interruption scenario
running the clearly synthetic sample course and walkthrough with no roots
granted, no agent configured, and the network disabled, asserting offline help
routes from named error codes (APP-03 fixture).
**Requirements**: FLOW-01, FLOW-02, APP-01, APP-02, APP-03
**Plans:** 11 plans
**Phase plan:** `.planning/phases/16B-ia-modes-recovery-contract/`
(`16B-RESEARCH.md`, `16B-PATTERNS.md`, `16B-UI-SPEC.md`, `16B-VALIDATION.md`; no
CONTEXT.md, the same precedent Phases 14A, 14B, 15A, 15B, and 16A set, with the
binding decisions in `REQUIREMENTS.md`, `PLANNING-DIRECTIVES.md`, the phase-16
synthesis, and the checker-approved `16B-UI-SPEC.md` Decisions log D1 to D9).

Plans:
- [ ] 16B-01-PLAN.md (wave 1, not autonomous) preconditions and the one one-way
  door: the recorded check against 14A and 16A plus both freeze records, plus
  16A's own precondition dated result line and Phase 13.9 checked directly,
  plus the settings additivity baseline; then D-16B-2 (where the IA read models
  and the three new CLI handlers live). Transcribes UI-SPEC D1 through D9 and
  locks D-16B-1 and D-16B-3 through D-16B-9.
- [ ] 16B-02-PLAN.md (wave 2) the tracer: `GET /activity` end to end through a
  new `surfaces/ia.py`, the shipped four parallel route structures, the shared
  presentation shell, and a real daemon subprocess, plus every Activity job
  state and the no-invented-percent rule.
- [ ] 16B-03-PLAN.md (wave 3) offline help: twelve `ia.*` codes, the
  `GET /help/<code>` route and its `help-code` CLI twin, the unknown-code
  fallback sentence, and the offline claim proven structurally and behaviourally.
- [ ] 16B-04-PLAN.md (wave 4) APP-01: the synthetic two-course corpus with one
  corrupted course, `course_shelf_state` with six attention states and a total
  ordering, and the course-shelf branch inside the shipped `handle_index`.
- [ ] 16B-05-PLAN.md (wave 5) APP-02: the three course-level route patterns and
  eight area frames, back and anchor semantics with progressive-enhancement
  focus restoration, one route per object at every width, and the three deep-link
  scenarios the probe left unresolved.
- [ ] 16B-06-PLAN.md (wave 6) APP-03 clause C137: four additive settings
  top-level keys with restrictive defaults, three defaults accessors, the
  additivity proof against the recorded baseline, and the declared-not-enforced
  note.
- [ ] 16B-07-PLAN.md (wave 7) the mode-layer contract: seven layers as data with
  their controllers, the two fixed layers rendered read-only, the pure
  precedence function over an explicit mapping, and the conflict fixture 16C
  extends rather than duplicates.
- [ ] 16B-08-PLAN.md (wave 8) recovery: eight degraded banners with their codes,
  next safe actions, and the basename-only rule, plus the FLOW-02 locked refusal
  card that carries none of the content it withholds.
- [ ] 16B-09-PLAN.md (wave 9) first launch: the bundled synthetic sample course,
  the skippable and replayable walkthrough, two atomic `_ia` state records, the
  one new mutating route `POST /api/shelf`, and the APP-03 interruption fixture.
- [ ] 16B-10-PLAN.md (wave 10) FLOW-01 and FLOW-02: the seven enumerated loops
  and their resume function, the interruption storyboard over durable records,
  the empty-run outcomes and tie ordering, and the model-disabled reading,
  practice, feedback walk against the real runtime.
- [ ] 16B-11-PLAN.md (wave 11, not autonomous) the freeze gate: all five
  fixtures in one measured pass, the blocking human contract-legibility review,
  and the freeze record or a named withholding, plus the validation closure.

**Prototype-before-freeze coupling:** the 16B freeze covers the loop
storyboards, IA routes and anchors, resume semantics, the job and approval
surface, the mode-layer contract, and the offline, help, and error states
only. Per synthesis section 15, the cross-client interruption prototype is
owed before the agent job protocol freezes. The 16B freeze is explicitly not
a visual system or token freeze (17A), not a notes, learner-artifact, or
strategy freeze (16C), not a course schema freeze (14B), and not a semantic
lesson capability freeze (16A), and its freeze record says so.

### Phase 16C: Strategies, Notes & Prototype Convergence

**Goal**: Learner notes are learner-owned artifacts stored under the
approved-roots vocabulary, never annotations baked into accepted lessons, each
carrying note ID, ownership, course and objective relation, anchor or selector
with quoted-context hash, source or lesson revision, authorship type, strategy,
text or structure, privacy, revision, and optional promotion or review state,
with authored pre-highlighting rendered as sparse orientation and never
recorded as learner evidence; a note whose anchor breaks against a revised
lesson stays attached to its objective with the broken selector flagged and a
relocation state of resolved, relocated_exact, relocated_probable, or orphaned,
where probable requires review; notes may seed reflection, retrieval proposals,
and draft questions but never silently become accepted source, lesson, key,
score, or mastery, promotion requires explicit source-backed review, and an
unreviewed note stays learner-private and non-authoritative; a learner artifact
(proof, program, diagram, explanation, project, observation) carries a rubric
and a pending or review state and reads as pending evidence until a reviewer
settles it, with the runtime recording pending and never settling; learning
strategies are the finite registered set (continuous reading with optional
highlight and note, guided note spine with prompted selection and restatement,
worked reasoning with prediction, explanation, and self-check, and a
retrieval-first or assessment-first route where objective policy permits), each
declaring purpose, eligibility, required and optional learner actions, skip and
resume, evidence effects, accommodations, offline behavior, and tests, with an
unavailable strategy falling back to continuous reading and no Cartesian
product of arbitrary style toggles; the composed mode-layer precedence resolver
reads every layer's live state over 16B's locked seven-layer table, a learner
chooses only among allowed strategies, runtime assessment behavior is never
user-configurable during a sitting, and a conflicting preference yields to the
higher layer using 16B's fixed conflict copy verbatim ("{Setting name} is set
by {higher layer name} for this course and can't be changed here."); progress
renders through the independent claim tuple (claim kind, scope and version,
numerator, denominator or indeterminate, rule, snapshot or window, settled or
pending or unknown, authority, uncertainty) with the seven dimensions kept
separate, no aggregate completion, mastery, or readiness score anywhere,
separate denominators for required, required-choice, and enrichment membership,
a missing denominator reporting indeterminate rather than an invented percent,
and the learner display using the D-14A-3 per-objective self-adjustable fill
state with Retrievability never surfaced as a percentage; the note-output trio
(notebook page, Cornell notes, concept map) is proven as three validated
projections of one parsed content instance, parsed once by the one parser with
zero re-parsing and zero per-style content forks, each validator failing
meaningfully on a deliberately broken fixture and each output degrading to
coherent plain Markdown, before any further output mode registers; and
legacy-artifact upgrades begin with the eleven-item baseline audit (current
parse, identity, fingerprint, objectives, sources, rights, media, assessment
boundaries, plain rendering, rich rendering, validation), present a bounded
diff before editing, preserve stable identity and source history, reject
cosmetic novelty, retain an artifact that cannot express an enhancement and
link a derived enhancement with its portability cost, and halt for explicit
assessment review whenever keyed content, difficulty, or objective alignment
would change.
**Depends on**: Phase 14B (course package; D-14A-2 component IDs are the anchor
targets), Phase 16A (semantic capability and activity contract; shared note and
activity schemas), and Phase 16B (IA, modes, and recovery contract; the locked
seven-layer mode table and the contextual Notes placement inside Learn and
Evidence per 16B-UI-SPEC decision D4). All three are planned but not yet
executed, so every signature this phase imports is read from plan text at
planning time; the first 16C plan opens with a recorded precondition check that
halts by name on any divergence, the same pattern plans 14B-01, 15A-01, 15B-01,
16A-01, and 16B-01 set, extended to check for `14B-FREEZE.md`, `16A-FREEZE.md`,
and `16B-FREEZE.md` records and for Phase 13.9's A9 closure, because 16C's own
freeze is a 14B-or-later freeze and may not close before the walking skeleton
is walked.
**Freeze gate:** the cross-subject missing-feature suite over four synthetic
subjects (an EMT respiratory assessment, a mathematics linear system, a CS loop
invariant with an off-by-one, and a history topic with conflicting primary
accounts): every registered strategy runs against the synthetic subjects with
one strategy marked unavailable, asserting fallback to continuous reading
(STRATEGY-01 fixture); the conflict-matrix fixture in which a synthetic learner
preference contradicts an accommodation override and an instructor policy,
each yielding to the higher layer with the stated-reason copy and no
mid-sitting change, extending 16B's conflict fixture rather than duplicating
it (STRATEGY-02 fixture); the synthetic note set anchored to a synthetic
lesson with one anchor invalidated by a lesson revision, asserting the note
stays attached to its objective with the broken selector flagged (NOTE-01
fixture); the promotion scenario in which one synthetic note passes
source-backed review while a second unreviewed note is asserted to stay
learner-private and non-authoritative (NOTE-02 fixture); the synthetic learner
artifact, a fictional proof with a rubric, reading as pending evidence until a
scripted review settles it (NOTE-03 fixture); the synthetic evidence set with
a missing denominator, a pending prose mark, and a version-split objective,
asserting each tuple dimension reports separately and no aggregate score
appears (GRAPH-03 fixture); the note-output trio built from one parsed content
instance with each validator failing on its deliberately broken fixture (a cue
without notes, an unlabelled edge, an anchor to a moved block) and each output
degrading to coherent plain Markdown; the legacy-upgrade scenario over a
synthetic pre-13.5 lesson artifact, asserting the baseline audit runs first
and the enhancement lands as a bounded diff with identity and source history
preserved (UPGRADE-01 fixture); and the scripted upgrade attempting to touch a
synthetic item's keyed answer, halting for explicit assessment review
(UPGRADE-02 fixture).
**Requirements**: GRAPH-03, NOTE-01, NOTE-02, NOTE-03, STRATEGY-01,
STRATEGY-02, UPGRADE-01, UPGRADE-02
**Plans:** 9 plans
**Phase plan:** `.planning/phases/16C-strategies-notes-prototype-convergence/`
(`16C-RESEARCH.md`, `16C-PATTERNS.md`, `16C-UI-SPEC.md`, `16C-VALIDATION.md`;
no CONTEXT.md, the same precedent Phases 14A through 16B set, with the binding
decisions in `REQUIREMENTS.md`, `PLANNING-DIRECTIVES.md`, the phase-16
synthesis, and the checker-approved `16C-UI-SPEC.md` Decisions log D1 to D16).

Plans:
- [ ] 16C-01-PLAN.md (wave 1, not autonomous) preconditions and decisions: the
  recorded check against 14B, 16A, and 16B plus all three freeze records, the
  three upstream precondition dated result lines, Phase 13.9's A9 closure
  checked directly, the live shipped-surface re-verification, and the evidence
  additivity baselines; writes 16C-PRECONDITION.md and 16C-DECISIONS.md
  (UI-SPEC D1 to D16 transcribed, D-16C-1 to D-16C-8 locked), then the
  D-12.6-5 placement and Evidence-prominence checkpoint held for Weibao.
- [ ] 16C-02-PLAN.md (wave 2) the four-subject synthetic corpus builder, the
  NOTE-01 note record with closed vocabularies and multi-selector provenance,
  the four relocation states with probable-never-auto-applied, the atomic note
  document pair with schemas/note.schema.json, and the guard's additive
  note-document marker.
- [ ] 16C-03-PLAN.md (wave 2) the finite strategy registry: four versioned
  data-record contracts with a code-owned continuous-reading fallback that
  never errors, and the three-row-class picker contract with its locked copy.
- [ ] 16C-04-PLAN.md (wave 2) GRAPH-03: the nine-field claim tuple, seven
  separate dimensions, indeterminate and version-split paths, the D-14A-3
  fill state with its legend, and the rendering scan proving no percent and no
  aggregate anywhere.
- [ ] 16C-05-PLAN.md (wave 3) STRATEGY-02: the composed precedence resolver as
  a collector over 16B's one mode_layer_resolve, the 16B conflict copy reused
  verbatim, the mid-sitting lock, and the conflict matrix appended to 16B's
  CONFLICT_CASES rather than duplicated.
- [ ] 16C-06-PLAN.md (wave 3) NOTE-02 and NOTE-03: two additive content-free
  evidence event types proven against the recorded baselines, the
  source-backed promotion flow with derived-copy acceptance and honest
  decline, the pending-until-human-mark learner artifact, and honest deletion.
- [ ] 16C-07-PLAN.md (wave 4) the note-output trio: notebook page, Cornell,
  and concept map as three validated projections of one parse (call-counted),
  three deliberately broken fixtures failing in the validators' own words with
  plain-Markdown degradation, plus prototype tracers A, B, and C.
- [ ] 16C-08-PLAN.md (wave 5) UPGRADE-01 and UPGRADE-02: the eleven-item
  baseline audit with honest stand-ins, the bounded diff with cosmetic
  rejection and the cannot-express derived link, the keyed-meaning halt with
  no override, and the legacy-upgrade skill updated to reference the shipped
  functions.
- [ ] 16C-09-PLAN.md (wave 6, not autonomous) the freeze gate: the
  cross-subject missing-feature suite in one measured pass over four subjects,
  the 13.9 A9 closure check that halts by name, the blocking human
  contract-legibility review, and the freeze record with the ROADMAP scope
  sentences transcribed verbatim or a named withholding, plus the validation
  closure.

**Prototype-before-freeze coupling:** per `STYLE-DISCIPLINE-16A-2026-08-14.md`
(binding order) the note-output trio prototype executes in 16C against the 16A
contract before the strategy and output registry freezes at 16C's gate, and
the remaining seven output modes plus on-demand genre styles register only
after the trio passes, one validator and one representative fixture each. Per
`PLANNING-DIRECTIVES.md` section 3a the guided-note, worked-reasoning, and
provenance-relocation pathways are prototyped before the strategy registry
freezes. The 16C freeze covers the note and learner-artifact schemas, the
promotion and review contract, the finite strategy registry, the composed
precedence resolver, the progress comprehension display, the note-output trio,
and the legacy-upgrade contract only. It is explicitly not a visual system or
token freeze (17A), not an information architecture or navigation freeze
(16B), not a semantic lesson capability freeze (16A), and not a course schema
freeze (14B), and its freeze record says so.

### Phase 16D: Paced Lesson Projection & Checkpoints (added 2026-08-31)

Inserted after 16C and before 17A/17B per the decision packet
`.planning/archive/DECISIONS-PACED-LESSON-2026-08-28.md` section 3: the treatment is a
lesson-renderer presentation plus a feedback-disclosure tier, belongs to no
existing subphase, and depends only on 16A, 16B (both frozen) and the shipped
Phase 6 / 6.2 machinery. Binding decisions D-PACED-1/2/3 are transcribed as
D-16D-1 through D-16D-7 in
`.planning/phases/16D-paced-lesson/16D-CONTEXT.md`; the experience contract is
`16D-UI-SPEC.md`. Four plans: 01 the authored `[STEP: id]` marker, the
`[LESSON-PACE:]` knob, and the ladder resolver in `model.py`; 02 the
lesson-run session kind, the additive `lesson_run` context and `paced` mode
labels, the default denominator exclusion, and the three-tier
wrong-checkpoint disclosure inside the runtime; 03 the paced view over the
existing lesson mode seam and gate bands; 04 the end-to-end tracer plus
Weibao's sat-through review as the freeze gate. Refusals carried forward: no
timed lock ever (IL-20260828-02), gates on attempted never correct
(IL-20260828-03), position is presentation state and never progress.
Executed: 01, 02, 03 on 2026-08-31 (summaries in the phase directory);
04's tracer runs the same day and its Task 2 review is Weibao's.

### Phase 17A: Visual System & Component Foundation

**Goal**: Freeze the learner-facing visual foundation on served bytes: one
semantic token system for color, typography, spacing, measure, radius, density,
and responsive hierarchy; one browser-served shell shared by the packaged app;
and accessible primitives for every component inherited from 16B and 16C. The
freeze follows a reversible same-flow comparison of Structured Studio, Quiet
Workbench, and Guided Canvas, with the final direction selected by Weibao. It
also brings the day route under the shared presentation shell, resolves the
direction-neutral rendering decisions deferred by 16B and 16C, clamps authored
token abuse to safe ranges, and proves the result through driven-browser plus
human accessibility QA. It does not add runtime authority, reopen IA, notes,
strategies, or lesson semantics, or implement the 17B production tracer.

**Depends on:** Phase 16B and Phase 16C. The token freeze also remains blocked
until the Phase 13.9 walking skeleton has been walked.

**Freeze gate:** The VISUAL-01 synthetic lesson-plus-practice flow is rendered
in all three directions at the required widths, the user selects the default
direction, VISUAL-02 proves safe token clamping, A11Y-01 completes with human
acceptance authority, and the accepted token and component contract is recorded
without silently absorbing the non-token Phase 13.5 backlog.

**Requirements:** VISUAL-01, VISUAL-02, A11Y-01

**Plans:** 8 plans across 4 waves (17A-05 added 2026-08-17; 17A-06, 17A-07 and 17A-08
added 2026-08-21).

**Wave 1**
- [ ] 17A-01-PLAN.md, the synthetic same-flow tracer, three reversible
  direction overlays, semantic parity, and VISUAL-02 abuse fixture.

**Wave 2** *(blocked on Wave 1 completion)*
- [ ] 17A-02-PLAN.md, Weibao's direction checkpoint, five-token type scale,
  bounded density tokens, and the day route shared-shell migration.

**Wave 3** *(blocked on Wave 2 completion)*
- [ ] 17A-03-PLAN.md, the accessible direction-neutral primitives and the
  complete 16B/16C component-state matrix.

**Wave 3 (added 2026-08-17)**
- [ ] 17A-05-PLAN.md, the OLED true-black theme registration: one `theme`
  enum value (`oled`), a true-black token set with measured contrast
  re-verified through the existing stylesheet invariants, and the settings
  surface option. Promoted from the Backlog small-enhancements row
  (2026-08-10); 17A is the theming-adjacent phase it was waiting for.

**Wave 3 (added 2026-08-21)**
- [x] 17A-06-PLAN.md, the local model harness: the shipped `local-qwen`
  profile reaching Ollama through the existing `openai_compatible` transport,
  the five typed unavailable states, and the adopted `dsh` agent console
  embedded as the Agent tab rather than rebuilt. Tasks 1 and 2 complete and
  the embed half of Task 3 complete; the run-and-journal half moved to
  17A-07 rather than left half-done inside a closed plan. See
  `17A-06-SUMMARY.md`.
- [ ] 17A-07-PLAN.md, the agent operation seam: one skill run from the Agent
  area through `model_adapter.invoke`, a bounded diff, and exactly one
  `journal.commit_operation` write with a proven undo. This is the plan that
  makes "agentic" true of the product rather than of an embedded window
  (USER-VISION 2026-08-21).

- [ ] 17A-08-PLAN.md, the shelf home and the four home modes: cards with real
  resume state, one next action with an evidence-sourced reason, and the three
  home shapes Weibao did not pick shipped as settings rather than deleted.
  Chosen 2026-08-21 after he sat the 13.9 skeleton and found the daemon still
  serving a pre-16B file list.

**Wave 4** *(blocked on Wave 3 completion)*
- [ ] 17A-04-PLAN.md, driven-browser evidence, scripted human A11Y-01 review,
  the Phase 13.9 halt check, and the freeze or named withholding record.

### Phase 17B: Production Vertical Tracer (details added 2026-08-17)

**Goal:** One polished course unit travels the whole source-to-course loop at
production quality, and the milestone exits through it: discovery and binding
of sources, a cited objective map with a treatment per objective, artifacts
authored through the skills and the deterministic contracts, the full learner
experience (direct source reading, hover and focus term definitions,
things-to-know and expert-tip blocks, a cited visual explanation, prediction,
targeted feedback, varied practice, transfer, and course-path continuation) at
desktop and phone widths, honest progress over a minimal scope tree, and a
clean-machine offline restore. The authored lesson stays coherent when opened
outside the itembank UI, and one legacy lesson plus one legacy question
artifact pass the upgrade audit (per the preserved Phase 17 rationale in
`SOURCE-TO-COURSE.md`). No phase is complete from framework tests alone: the
tracer exits through a realistic synthetic end-to-end course fixture plus
visual and accessibility verification (SOURCE-TO-COURSE closing bar).

**Depends on:** every prior subphase frozen (14A, 14B, 15A, 15B, 16A, 16B,
16C, 17A) and the Phase 13.9 walking skeleton walked. The 17B plans halt by
name on those preconditions, following the 16C-01 precedent; handing them to
an executor early is safe and the executor will correctly refuse to start.

**Fixture rule:** every gate is proven on a realistic synthetic fixture
course kept in this repository and `itembank guard` clean. Weibao may
additionally exercise the same flow on a real course outside the repository;
that evidence is supplementary and repo-side records carry pointers, counts,
and hashes only.

**Freeze gate: end-to-end gates G1 through G11, defined in
`research/phase-16/14-synthesis.md` section 16.1 and made concrete for this
tracer as follows.**

- **G1 Coverage:** every capability the tracer exercises maps to its
  requirement row and ledger disposition; no undischarged tracer promise.
- **G2 Object/authority:** each artifact the tracer creates names its durable
  object, owner, authority, and source of truth; derived views rebuild.
- **G3 File safety:** the tracer's unit survives the file-fault drills
  (move, external edit, conflict, interrupted write) preserving old or new
  valid state.
- **G4 Portable capability:** the authored lesson reads coherently in plain
  Markdown outside the UI, and in the UI by keyboard, touch, screen reader,
  narrow screen, and offline.
- **G5 Evidence honesty:** progress over the tracer's scope tree (one open
  field containing one bounded course containing the unit) renders in both
  registered rollup models, ROLLUP-DIM and ROLLUP-MAP (IDEA-LEDGER
  IL-20260817-01), with stated denominators, pending and unknown states
  shown, and no aggregate score anywhere; the bounded course may complete,
  the open field never does. Weibao picks the default rollup from the
  rendered screens.
- **G6 Assessment authority:** no surface, agent, or note in the tracer
  leaks a key, invents a score, auto-grades prose, or changes a frozen
  sitting.
- **G7 Course quality:** the tracer's treatment decisions cite scope,
  demand, rationale, uncertainty, and the existing-artifact search, and
  pass review before authoring.
- **G8 Flow/visual:** first-run, resume, learn, practice, test, source
  inspection, review, agent failure, and narrow-screen transitions preserve
  context and hierarchy on the tracer's unit.
- **G9 Strategy/notes:** each strategy the tracer offers states choice,
  requirement, skip and resume, accommodation, evidence effect, privacy,
  provenance, and the note-authority guard.
- **G10 Portability/recovery:** a clean machine restores the tracer's
  canonical objects and evidence offline; every unsupported capability
  appears in a loss report.
- **G11 Cross-cutting:** egress capture equals disclosed manifests;
  rights-unknown refuses unsafe operations; diagnostics are redacted.

**Requirements:** verified end to end rather than newly landed; the gate
checklist above is the acceptance record, kept in `17B-GATES.md`.

**Plans:** 4 plans across 4 waves; see
`.planning/phases/17B-production-vertical-tracer/`.

**Wave 1**
- [ ] 17B-01-PLAN.md, the precondition halt, the realistic synthetic course
  fixture with its scope tree, and the 17B-GATES.md checklist scaffold.

**Wave 2** *(blocked on Wave 1 completion)*
- [ ] 17B-02-PLAN.md, discovery through accepted authoring on the fixture:
  binding, cited objective map, treatment review, authored unit; G1, G2,
  G3, G7 evidence.

**Wave 3** *(blocked on Wave 2 completion)*
- [ ] 17B-03-PLAN.md, the learner pass: reading, lesson, practice, graded
  sitting, notes and strategies, both rollup displays with Weibao's default
  choice checkpoint; G4, G5, G6, G8, G9 evidence plus the legacy upgrade
  audit.

**Wave 4** *(blocked on Wave 3 completion)*
- [ ] 17B-04-PLAN.md, clean-machine offline restore with loss report, egress
  and rights checks, the human visual and accessibility checkpoint, and the
  milestone exit record; G10, G11 evidence.

### Phase 17C: Maintenance and Restore Audit (registered 2026-08-17)

**Goal:** The post-Phase-17 maintenance and restore audit named in the
governance clause below stops being ownerless: after 17B closes, one audit
confirms a clean machine restores all supported canonical objects and
evidence offline (gate G10), every unsupported capability appears in a loss
report, and each accepted item still names its maintenance owner, then names
the recurring audit triggers owed after 14B, 16C, and 17B changes.

**Owner:** a Claude-class planning session runs the audit; Weibao holds
acceptance authority on the report. The report is
`.planning/phases/17C-maintenance-restore-audit/17C-AUDIT.md`.

**Depends on:** Phase 17B complete (its G10 drill is this audit's input, not
a substitute: 17B proves the tracer's unit restores; 17C sweeps all accepted
items and owners).

**Plans:** 1 plan; see `.planning/phases/17C-maintenance-restore-audit/`.

- [x] 17C-01-PLAN.md, the audit run: restore drill inventory, loss-report
  completeness check, maintenance-owner sweep, and the named audit triggers.
  Run 2026-09-05; tasks 1 to 3 complete, Task 4 (Weibao's acceptance)
  unanswered. Report: `17C-AUDIT.md`.

### Phase 18: External-User v1 (details added 2026-08-17)

**Goal:** A friend with no knowledge of this project installs itembank, is
walked through setup by an AI agent reading the public repo, and gets real
value from the shipped loop. Acceptance bar: the six A10 criteria in
`READINESS-AUDIT-14A.md` (install without folklore, agent-guided onboarding,
first-run self-explanation, scope honesty, stranger-safe privacy defaults,
and errors that name the next safe action), verified by a real cold install
by a second person after 17B.

**Sub-decisions this phase owns, dispositioned 2026-08-17 in 18-CONTEXT.md:**
the packaging conflict IL-20260815-11 (resolved: the Phase 13 browser-served
shell plus packaged wrapper is the delivery vehicle; 17A-CONTEXT D-08 already
makes the browser-served UI the single canonical shell), the V2-DEL-01 code
signing decision (a dated cost decision checkpoint for Weibao, with an
unsigned-plus-documented-workaround recommended default), and the
agent-facing update and capability disclosure manifest (a machine-readable
additive surface on the shipped `update`/`usage`/`schema` ground; the
promoted 999.3 MCP surface is a named future consumer).

**Owed fixture:** the cold-agent onboarding transcript (one agent, one run,
recorded) for the README onboarding section, per A10 check 2.

**Depends on:** Phase 17B (the shipped loop it sells is the milestone's
output); 17C may run beside it. The promoted Phase 999.3 (MCP surface) may
run in parallel; neither blocks the other.

**Plans:** 3 plans across 3 waves; see `.planning/phases/18-external-user-v1/`.

**Wave 1**
- [ ] 18-01-PLAN.md, packaging resolution and the install story: the
  packaged artifact built from the Phase 13 shell, the IL-20260815-11
  resolution record, and Weibao's signing cost checkpoint.

**Wave 2** *(blocked on Wave 1 completion)*
- [ ] 18-02-PLAN.md, the agent-facing capability disclosure manifest and
  its update-path wiring.

**Wave 3** *(blocked on Wave 2 completion)*
- [ ] 18-03-PLAN.md, cold-install verification: the second-person install,
  the cold-agent onboarding transcript fixture, and the A10 six-criterion
  acceptance record.

### Next-milestone subphase sequence (14A through 17C)

*Status of record for these subphases is the Status column below and the checklist under "Phases", both corrected 2026-09-03. The v1.0 Progress table does not cover them.*

*Reframed 2026-08-13 from the four broad Phases 14 to 17, per
`.planning/research/phase-16/14-synthesis.md` sections 14 and 15. The four
original detailed blocks are preserved verbatim below under "Superseded flat
sequence (historical rationale)."*

The high-level order is unchanged: durable course and file semantics precede AI
course direction, and logical learning contracts precede visual productization.
The four broad phases were too coarse and placed some Phase 16 discoveries after
Phase 14 format commitments, so execution is now bounded by nine subphases.
These subphases bound execution, not product possibility. Each freezes shared
interfaces and may register multiple capabilities that compose cheaply; optional
or expensive capabilities stay on the capability runway rather than being cut.

**Roadmap governance clauses (new 2026-08-13).**

- **Prototype before durable commitment.** A reversible prototype is required
  before any schema freeze, production UI, or broad interchange commitment.
  Named prerequisites: graph-to-outline and denominator/version migration
  before course-schema freeze; a Markdown rich-lesson stress corpus before
  lesson-profile grammar freeze; guided-note, worked-reasoning, and
  incorrect-note pathways before a strategy registry or question-from-notes
  support; a restricted notebook preview before any execute/trust UI;
  visual-math equivalence before a broad interaction registry; cross-client
  interruption before the agent job protocol freezes; clean-machine restore
  before any course-package or export promise; and the same logical flows in
  three visual directions before Phase 17 tokens freeze.

- **Implementation-readiness audit (gate before any Phase 14A plan).** After the
  contract files and requirements are updated and before the first Phase 14A
  implementation plan, run the readiness audit defined in synthesis section
  16.3. It diffs every accepted synthesis clause against the updated contract
  and exposes missing, duplicate, conflicting, or weaker translations; maps each
  requirement to one owner, subphase, prerequisite, fixture, success gate,
  degraded state, migration, documentation, and maintenance obligation; confirms
  prototypes occur before their dependent schema or UI freezes; builds a
  dependency graph and rejects circular ownership among course, lesson,
  evidence, notes, jobs, and UI state; confirms the shipped parser, scorer, and
  evidence tests stay byte-compatible where required and that no second authority
  was introduced; and confirms every research proposal has a permanent
  disposition. The audit fails on any silently omitted, deleted, or
  simplicity-only rejection.

- **Post-Phase-17 maintenance and restore audit.** After Phase 17B, a
  maintenance and restore audit confirms that a clean machine restores all
  supported canonical objects and evidence offline (gate G10), that every
  unsupported capability appears in a loss report, and that each accepted item
  still names its maintenance owner. New audit triggers are named after 14B,
  16C, and 17B. *Owner assigned 2026-08-17: this audit is Phase 17C (details
  block above), run by a Claude-class planning session with Weibao holding
  acceptance; plan at
  `.planning/phases/17C-maintenance-restore-audit/17C-01-PLAN.md`.*

- **Durable capability runway.** Capability breadth is preserved as a runway of
  registered extensions, prototypes, and backburner items, not by cutting
  research. Promotion changes execution timing, not the existence of a proposal
  or its research trail. Each registered or backburner capability names its
  shared primitive, dependency, cost, and promotion trigger. Backburner
  proposals are tracked in synthesis section 12.5.

- **Permanent rejection ledger (governance input).** The append-only rejection
  and supersession ledger in synthesis section 12.4 is a roadmap governance
  input. A rejected or superseded idea cannot be silently reintroduced or
  deleted; each ledger row carries proposal, origin, evidence considered,
  disposition and exact reason, conflicting rule or quality attribute,
  alternatives retained, date, and reconsideration condition. Any roadmap change
  that would revive a rejected idea must cite and satisfy its recorded
  reconsideration condition.

| Subphase | Deliverable | Depends on | Freeze gate | Status (2026-09-03) |
|---|---|---|---|---|
| 14A: identity, lifecycle, and operation prototype | Stable IDs, revisions, fingerprints, operation journal, link/import/move/edit/supersede semantics, atomic recovery | Shipped parser/runtime | File fault and external-edit tracer | Frozen 2026-08-18 |
| 14B: graph and course package prototype | Typed graph kernel, outline projection, source/treatment bindings, versions, rights, minimal package | 14A | Three-domain graph tracer, clean restore, authorability review | Frozen 2026-08-27 |
| 14C: source adapter registry and remote intake (added 2026-08-21) | One adapter contract and locator sidecar per medium | 14A | Multi-source coverage audit | Frozen 2026-08-28 |
| 15A: director and treatment policy | Treatment recommender, source scope, rights/egress, autonomy levels, checkpoints | 14B | Four-subject recommendation review | Frozen 2026-08-30 (review leg agent-signed) |
| 15B: quality, blueprint, and acceptance | Blueprint fidelity, course audit, accepted revision, staleness/dependency impact | 15A | Lesson plus practice acceptance tracer | Frozen 2026-08-30 (review leg agent-signed) |
| 16A: semantic capability and activity contract | Lesson roles, activity-purpose matrix, capability profiles, media/citation policy | 14B, assessment runtime | Portable rich lesson stress corpus | Frozen 2026-08-28 (review leg agent-signed) |
| 16B: IA, modes, and recovery contract | Core loops, routes, resume, jobs, approvals, offline/help/error states | 14A, 16A | Full storyboard and interruption scenarios | Frozen 2026-08-28 (review leg agent-signed) |
| 16C: strategies, notes, and prototype convergence | Notes, learner artifacts, finite strategies, progress comprehension, legacy upgrade | 14B, 16A, 16B | Cross-subject missing-feature suite | Frozen 2026-08-30 (review leg waived) |
| 16D: paced lesson projection and checkpoints (added 2026-08-31) | Step ladder, lesson-run session, tiered checkpoint disclosure, paced view | 16A, 16B | Paced tracer plus sat-through review | Frozen 2026-09-01, sit-through deferred |
| 17A: visual system and component foundation | Tokens, hierarchy, responsive shell, accessible primitives | 16B, 16C | Same-flow visual comparison and accessibility QA | Frozen 2026-09-01, A11Y-01 deferred |
| 17B: production vertical tracer | Polished unit from discovery through restore | All prior | End-to-end gates G1 through G11 | In execution; 01 and 02 done, 03 in flight, 04 unstarted |
| 17C: maintenance and restore audit (added 2026-08-17) | Clean-machine restore sweep, loss-report completeness, maintenance-owner sweep, named audit triggers | 17B | Audit report accepted with zero unowned accepted items | Audit run 2026-09-05, five silent losses routed; awaiting Weibao's acceptance |

**Planning source:** `.planning/research/phase-16/14-synthesis.md` sections 15
and 16.3, and `.planning/SOURCE-TO-COURSE.md`. Detailed discussion, UI
specification, requirements, schemas, and executable plans for each subphase are
owed by the normal planning sequence; do not invent them during implementation.

### Superseded flat sequence (historical rationale)

*Superseded 2026-08-13 by the nine-subphase sequence above. Preserved verbatim,
not deleted, so the original goals and planning sources remain traceable.*

#### Phase 14: Course Workspace & Source Binding (superseded)

**Goal:** A learner or approved agent creates a course from a syllabus and
source folder, sees a cited objective and prerequisite map, binds existing
artifacts, assigns a treatment to each objective, and sees missing, thin, and
unknown coverage without first generating content.

**Planning source:** `.planning/SOURCE-TO-COURSE.md` Phase 14. Detailed
discussion, UI specification, requirements, schemas, and executable plans are
owed by the normal planning sequence; do not invent them during implementation.

#### Phase 15: AI Course Director & Quality Pipeline (superseded)

**Goal:** A hosted coding-agent-class client or registered local backend can
drive bounded source analysis, treatment recommendation, course generation,
quality review, standardized-test or knowledge-exam alignment, and
evidence-backed remediation through inspectable proposals and recoverable writes.

**Planning source:** `.planning/SOURCE-TO-COURSE.md` Phase 15. Reuse the
shipped `audit`, `coverage`, `seed`, lint, evidence, trends, and model-adapter
contracts.

#### Phase 16: Learning Flow & Lesson Capability Contract (superseded)

**Goal:** Research and specify the logical course journey, lesson-capability
model, question-purpose matrix, portable authored representation, interaction
and accessibility behavior, image and citation policy, and agent authoring
contract before the visual system or implementation hardens those decisions.

**Research scope:** study current source-grounded and learning products,
including NotebookLM, for flow, source navigation, questions, study aids, and
grounded assistance. Use the findings as evidence. The product target remains
a lesson- and objective-centered course platform rather than a chat notebook.

**Planning source:** `.planning/SOURCE-TO-COURSE.md` Phase 16. Completion
requires a realistic course-unit storyboard or prototype across desktop,
narrow, touch, keyboard, screen-reader, offline, and plain-file contexts, plus
an explicit disposition for every researched capability.

#### Phase 17: Visual System & Comprehensive Guided Learning UI (superseded)

**Goal:** Establish a coherent visual language and implement the course journey
against Phase 16's contracts. Deliver direct reading, rich reference and guided
lesson modes, cited visuals, accessible teaching interactions, varied practice,
tests, targeted feedback, and the next course action as one polished experience.

**Planning source:** `.planning/SOURCE-TO-COURSE.md` Phase 17. Framework
completion does not close this phase. A realistic synthetic course tracer and
visual, responsive, degraded-state, portable-source, and accessibility
verification do.
