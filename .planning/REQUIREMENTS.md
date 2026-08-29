# Requirements: itembank — AI-taught learning platform

**Defined:** 2026-08-05
**Core Value:** One runtime, one scorer, one evidence store — and the runtime, not the model, decides what reaches the learner.

## v1 Requirements

### Evidence

- [x] **EVID-01**: An item keeps the same identity across bank edits, so evidence recorded a month ago still points at the same question
- [x] **EVID-02**: A legitimate stem edit does not orphan that item's history; `lint` warns when a keyed item's content changed
- [x] **EVID-03**: One evidence store replaces `_attempts/*.md`, session JSON, and `daily_log.md`; each of those becomes a view over it
- [x] **EVID-04**: A single query answers "how am I doing on this objective over time" across every session and subject
- [x] **EVID-05**: Every evidence write is auditable and reversible — nothing is silently overwritten
- [x] **EVID-06**: Existing attempt files and session JSON migrate into the new store without losing a recorded response
- [x] **EVID-07**: Evidence records response time, confidence, error category, hint tier reached, session mode, and manual-review state, whether or not anything reads them yet
- [x] **EVID-08**: A "correct" from drill mode is distinguishable in the evidence from a "correct" from exam mode

### Protocol

- [x] **PROTO-01**: Items, sessions, responses, and reports each carry an explicit schema version
- [x] **PROTO-02**: `lint` emits machine-readable errors with a stable error code and the field at fault, alongside the human text
- [x] **PROTO-03**: Submitting the same response twice does not record two attempts, and the tool says which happened
- [x] **PROTO-04**: A published JSON schema or contract fixture defines the agent interface, and CI checks the runtime against it
- [x] **PROTO-05**: An agent with no repository context can read the contract, run a full session, and interpret the evidence

### Lessons

- [x] **LESSON-01**: A bank can carry an optional `LESSON` section holding the teaching text its items test
- [ ] **LESSON-02**: An item can reference a lesson heading via `LESSON-REF`
- [ ] **LESSON-03**: A bank with no `LESSON` section parses byte-identically to how it parses today
- [x] **LESSON-04**: `lint` fails, by item number, when a `LESSON-REF` names a heading that does not exist -- never a render-time crash
- [ ] **LESSON-05**: `spec` documents both, so an authoring agent can write lessons without seeing the source
- [x] **LESSON-06**: A lesson renders in the app as reading material, with its items reachable from it
- [ ] **LESSON-07**: A `## TERMS` block plus `[[term]]` references render as a Popover-API hover gloss, degrade to a glossary appendix with no JavaScript, pass through a runtime `glossable()` gate so a gloss can never leak a keyed answer, and each lookup lands as a `term_lookup` event
- [ ] **LESSON-08**: A `[!KEY]` callout is a GitHub-compatible block with a minted `[ID:]`/`[HASH:]`, exports to Anki TSV with a `#guid` that round-trips on re-export, supports `{{cloze}}`, and emits `key_review` events
- [ ] **LESSON-09**: A style file carries a `## Voice` prose zone and a machine-parsed `## Rules` pipe table; machine-checkable rules are implemented, model-judged rules are declared `manual`, and a rule row claiming a lintable severity the linter does not implement is itself a lint error
- [ ] **LESSON-10**: The style registry ships five styles in order with `expository` as parent, one file per style, exactly one inheritance level, a locked house `lock` column, fixed selection precedence, and a `render_style`/`restyle` split that refuses named-impossible transforms
- [ ] **LESSON-11**: Style enforcement runs as three cost classes on every lint, the check catalogue is closed, every warning ships with a recorded false-positive rate, `<!-- style-ignore: -->` exists, and the whole pass stays under 50ms on a 5000-word lesson
- [ ] **LESSON-12**: The authoring model receives distilled imperatives capped at seven (configurable), placed last in the prompt, plus exactly one exemplar, never the style file or `## Voice` verbatim
- [x] **LESSON-13**: `[!CHECK: <id>]` is the single new parse path with no key and no scoring path, same-bank-only by lint rule; `[!EXAMPLE]` is a callout kind against the existing callout container
- [x] **LESSON-14**: Callouts, figures, print CSS, and the reading measure/heading ramp render on Phase 4's token set with no new type sizes; a bank using none of the new blocks renders byte-identically to Phase 3 output
- [ ] **LESSON-15**: Every item carries an optional one-sentence lintable Educational Objective line, present in `explain_payload()` only, consumable by selection, dedup, Anki export, and the auditor without any of them re-deriving it
- [ ] **LESSON-16**: The TERMS grammar reserves one optional ignorable `zh=` meta field, dropped from rendered output entirely
- [ ] **LESSON-17**: Two-file lesson layout is the default; the subject-profile `lesson_layout` field overrides it and is folded into `09-02-PLAN.md` before Phase 9 executes

### Seeding & provenance (Phase 3.2)

- [ ] **SEED-01**: A modern Anki `.apkg` imports losslessly with an exhaustive per-note account (converted / skipped / refused, each with the note id and reason) — no note silently dropped; zstd-compressed collections decode through one pinned, checksummed, license-reviewed dependency
- [ ] **SEED-02**: Draft → lint → retry → explicit human accept, one item at a time; nothing writes to a bank without an accept, and a cancelled run writes nothing
- [ ] **SEED-03**: The accept loop ships as both a CLI command and a daemon route — one accept endpoint, two surfaces, never two implementations of the decision
- [ ] **SEED-04**: `[SRC:]` and `[OBJ:]` resolve through an additive `## SOURCES` registry; an unresolvable id is a lint error naming the id and the file
- [ ] **SEED-05**: Paraphrase lint uses stdlib winnowing over fingerprints only, errors at ≥8 consecutive copied words, warns above Jaccard 0.25 (both thresholds settings), and never stores source text
- [ ] **SEED-06**: `[CASE:]` grouping and `[PREREQ:]` edges are authorable and linted here — cycle detection and unresolvable-target detection — ahead of Phases 6/7 consuming them
- [ ] **SEED-07**: The real EMT / Math / CS corpus lives outside the repository (guard keeps it out of CI) and calibrates every Phase 3.1 style warning with recorded false-positive rates
- [ ] **SEED-08**: The objective coverage map is computed on demand from the bank and registry, never stored
- [ ] **SEED-09**: A bank using none of `## SOURCES`, `[SRC:]`, `[OBJ:]`, `[CASE:]`, or `[PREREQ:]` parses and renders byte-identically

### Teaching

- [x] **TEACH-01**: A wrong answer holds the session cursor instead of advancing, so a second attempt is possible
- [x] **TEACH-02**: A `hint` command and route return the next tier: lesson pointer, objective, trap, the rationale for the option actually picked, the discriminator, then the reveal
- [x] **TEACH-03**: Hints used are recorded per response, so "right at tier 1" and "right at tier 4" are different outcomes in `report`
- [ ] **TEACH-04**: The tutoring model reads the item, key, rationale, and the learner's specific wrong answer, and writes a hint about that error
- [ ] **TEACH-05**: The runtime decides which tier the model may speak at; model output reaching past the unlocked tier is dropped, not shown
- [ ] **TEACH-06**: A learner cannot argue the model into revealing, because the gate is code and not instruction
- [ ] **TEACH-07**: Every model-generated hint is recorded in the evidence store and recoverable later
- [ ] **TEACH-08**: A `short` answer is marked against its rubric points as a tickable checklist beside what was written, producing per-rubric-point evidence
- [ ] **TEACH-09**: The model can mark a `short` answer against the rubric, and its verdict lands as pending review rather than as accepted evidence

### Modes

- [x] **MODE-01**: Feedback policy is a property of the session mode, chosen per sitting
- [x] **MODE-02**: Drill mode reveals the correct answer and explanation immediately on a wrong answer, then advances
- [x] **MODE-03**: Practice mode runs the hint ladder with the cursor held, revealing at the final tier
- [x] **MODE-04**: Diagnostic mode gives no feedback until the sitting ends
- [x] **MODE-05**: Exam mode gives no feedback until the attempt file is marked
- [x] **MODE-06**: The mode used is recorded with every response

### Selection

- [x] **SEL-01**: A session can be selected by objective, prerequisite, item type, and difficulty
- [x] **SEL-02**: Selection modes exist for diagnostic, practice, remediation, and exam
- [x] **SEL-03**: Recent exposure is tracked, so a session does not accidentally repeat what was just answered
- [x] **SEL-04**: Discrimination pairs can be requested, serving two commonly confused items together
- [x] **SEL-05**: The first selector is rule-based and inspectable — it can explain why it chose each item

### Scheduling

- [ ] **SCHED-01**: The tool computes what is due today per objective from its own evidence
- [ ] **SCHED-02**: A daily cap prevents a course being binged, enforced through `day`
- [ ] **SCHED-03**: Anki keeps owning card reviews; itembank never writes a card schedule
- [ ] **SCHED-04**: A completed lesson enters a review queue with a transparent, hand-set schedule rather than a fitted model

### Trends

- [ ] **TREND-01**: A weak objective raises its selection weight; a mastered one drops out of rotation
- [ ] **TREND-02**: `day`'s `load` number is backed by evidence rather than tick counts, and says when the plan needs re-cutting
- [ ] **TREND-03**: A longitudinal report shows accuracy by objective over weeks, hint tier reached, and items pending manual marking
- [ ] **TREND-04**: An objective answered correctly a month ago and untouched since is flagged as at-risk before it is failed
- [ ] **TREND-05**: Every trend states the evidence it rests on, so a claim can be checked rather than trusted

### Code items

- [ ] **CODE-01**: A `check` item is verified by running the learner's own code and comparing its output to an expected result
- [ ] **CODE-02**: `check` scores dichotomously, through the same scorer as every other type
- [ ] **CODE-03**: The code field is a real editor: monospace, tab inserts a tab, line numbers a rubric point can reference
- [ ] **CODE-04**: Execution is bounded by a timeout and the process tree is cleaned up on both Windows and POSIX
- [ ] **CODE-05**: The documentation states plainly that this stops accidents and not deliberate escapes, and does not claim isolation

### Visual interactions

- [ ] **VIS-01**: One versioned declarative `visual` item protocol describes renderer configuration and semantic responses without allowing bank-authored JavaScript
- [ ] **VIS-02**: Public visual payloads expose only the scene, initial state, allowed semantic actions, response grammar, and accessibility text; accepted states, tolerance, misconception mapping, and reveal material remain private
- [ ] **VIS-03**: Mouse, touch, keyboard, and semantic-HTML controls serialize the same domain action and response rather than pixels, paths, screenshots, or renderer-specific state
- [ ] **VIS-04**: Visual responses are normalized and scored deterministically by `runtime.score_response()` alone, including exact versioned tolerance boundaries, and remain dichotomous
- [ ] **VIS-05**: `plot` and `numberline` ship together as one shared inline-SVG and semantic-HTML vertical slice
- [ ] **VIS-06**: Committed semantic actions, runtime observations, final state, error category, feedback anchor, and bounded hint entitlement are append-only, agent-queryable evidence; raw pointer movement is not stored
- [ ] **VIS-07**: Every visual interaction has equivalent keyboard and non-drag operation, accessible names/status, touch targets and cancellation, narrow/zoom reflow, and a semantic fallback that remains mandatory if a future dense simulation uses canvas
- [ ] **VIS-08**: `spec`, named lint errors, published schemas, and synthetic golden fixtures form a complete visual-item authoring contract for a model with no renderer-source access
- [ ] **VIS-09**: GIFT export refuses visual items loudly by item number and stable code instead of approximating an interaction the format cannot express

### Gate

- [x] **GATE-01**: A lesson can gate its own continuation on an inline check; clearing is an ordinary `runtime.score_response()` verdict, not a lesson-local rule
- [x] **GATE-02**: Clearing an inline check writes ordinary response evidence, distinguishable from a quiz attempt on the same objective only by a `context` field
- [x] **GATE-03**: An idea cleared inside a lesson re-enters the normal retention queue through the same evidence store, with no lesson-specific schedule
- [x] **GATE-04**: `[GATE: required|recommended|off]` all ship; a learner can always read ahead by an explicit, recorded `gate_skip` choice; the skip is never a `response` with a null score
- [x] **GATE-05**: A bank whose lessons declare no gates renders byte-identically to Phase 3.1 output
- [x] **GATE-06**: The gate outcome split (cleared vs skipped, over gates encountered) is derivable from the evidence log alone, with a stated denominator, no target, no streak

### Subject loop

- [ ] **LOOP-01**: One subject-invariant loop drives EMT, Math, and CS; only lesson medium, allowed item types, and verifier vary
- [ ] **LOOP-02**: Math lessons and items render LaTeX offline from a vendored asset, with no CDN and no build step
- [ ] **LOOP-03**: CS lessons carry runnable code inside the prose
- [ ] **LOOP-04**: EMT lessons render prose and tables
- [ ] **LOOP-05**: Adding a fourth subject requires configuration, not a fourth surface

### Auditor

- [ ] **AUDIT-01**: A syllabus or standards document is ingested and its objectives extracted, including subtleties rather than only headings
- [ ] **AUDIT-02**: Extracted objectives are mapped against bank coverage, and gaps are reported by objective
- [ ] **AUDIT-03**: Every coverage claim cites the evidence it rests on; an unciteable claim is reported as unknown, not as covered
- [ ] **AUDIT-04**: The auditor points at materials that would fill a gap, and absorbs them into the bank once obtained
- [ ] **AUDIT-05**: Autonomy is a configured range from report-only, through draft-and-approve, to audit-draft-lint-fix-commit
- [ ] **AUDIT-06**: Every generated item passes `lint` before reaching a bank
- [ ] **AUDIT-07**: A second quality gate beyond `lint` catches machine-authored failure modes `lint` cannot: answer-position skew, near-duplicate stems, stem-option overlap that leaks the key, and distractors that never say when they would be correct
- [ ] **AUDIT-08**: Every auditor write is reversible in one step, and the tool shows what it changed before it is accepted
- [ ] **AUDIT-09**: At the highest autonomy setting the tool reports its own volume, so rubber-stamping is visible rather than silent

### Authoring

- [ ] **AUTH-01**: One command runs the whole authoring cycle — print the spec, take the draft, lint it, feed errors back, repeat to clean or to a retry cap, write the bank — with no human relaying errors
- [ ] **AUTH-02**: The loop cannot invent content beyond what it was asked to write; the model authors, the tool validates
- [ ] **AUTH-03**: A model with no repository context can complete the loop from the contract alone

### Surfaces

- [x] **SURF-01**: One daemon serves every surface on one port: the day view, a sitting, the study loop, reports, settings, and the JSON API
- [ ] **SURF-02**: The browser page is a client of the same JSON API an agent uses; it holds no key and implements no scoring
- [x] **SURF-03**: Starting the daemon twice does not fight over the port, and `--lan` still reaches a phone on the same wifi
- [x] **SURF-04**: Every capability has both a route and a CLI command, over one runtime
- [ ] **SURF-05**: The question surface shows one sticky context line rather than five bands of chrome above the stem
- [x] **SURF-06**: `study` renders the per-option rationale, second-best, and notes it currently discards
- [x] **SURF-07**: The whole tool uses one palette; the `day` page stops being a third stylesheet in literal hex
- [x] **SURF-08**: The accent colour is set from the OS colour picker with light and dark pairs computed from it, and correct/incorrect stay contrast-checked and colour-blind safe
- [x] **SURF-09**: `day` supports full in-page markdown editing with an optimistic-concurrency guard, so an edit cannot silently overwrite one made in Obsidian

### Model layer

- [ ] **MODEL-01**: One adapter interface serves hosted CLIs and a local OpenAI-compatible server as the same code path
- [ ] **MODEL-02**: Switching between a hosted model and a local model is a configuration change, not a code change
- [ ] **MODEL-03**: The core loop degrades rather than blocks when no model is reachable — sitting, scoring, lessons, the authored ladder, evidence, and reports all still work
- [ ] **MODEL-04**: An agent usage contract states permissions, disclosure limits, retry behaviour, manual-grading rules, and what an agent may not infer
- [ ] **MODEL-05**: A model never scores a structured response and never writes accepted evidence directly

### Delivery

- [x] **DEL-01**: The tool ships as one double-clickable artifact per OS, built with stdlib `zipapp`, on Windows, macOS, and Linux
- [x] **DEL-02**: The artifact is still plain Python inside, so a person or an agent can open and edit it
- [x] **DEL-03**: The daemon opens as a frameless app window, falling back to an ordinary browser tab when that is unavailable
- [x] **DEL-04**: One documented config file holds theme, daily cap, selection weights, auditor autonomy, model backend, and update policy
- [x] **DEL-05**: `itembank config` prints the settings schema the way `spec` prints the format contract, and an invalid value is rejected with a named error
- [x] **DEL-06**: The tool updates itself from GitHub Releases with checksum verification and atomic replacement
- [x] **DEL-07**: Update behaviour toggles between opt-in-only and check-on-launch, and fails silently when offline
- [x] **DEL-08**: GIFT export produces a file a real LMS importer accepts, and item types GIFT cannot express fail loudly by item number rather than exporting silently wrong

### Desktop shell (Phase 13)

- [x] **DEL-09**: The Tauri shell talks to the sidecar over the existing localhost HTTP surface only, with the bound port and a per-launch token announced on the sidecar's stdout — no second IPC protocol, no fixed-port assumption
- [x] **DEL-10**: Killing the shell leaves no orphaned sidecar and no held port; on Windows the sidecar sits in a job object, and a second launch attaches to the running instance via a named mutex rather than racing it
- [x] **DEL-11**: The app installs per-user via NSIS (machine-wide option), uninstalling never deletes the evidence store, and the installed size lands in the 25–45 MB target as a PyInstaller onedir artifact
- [x] **DEL-12**: `tauri-plugin-updater` (signed) and the Phase 2.1 Python updater consume one GitHub Releases channel with their own manifest formats, one `notified_at` disclosure record covers both, and version coherence is checked at the sidecar handshake
- [x] **DEL-13**: The code-signing and AV checklist is executed (certificate named or unsigned shipped honestly, Microsoft false-positive submission, VirusTotal baseline), and every capability stays reachable from the CLI without the shell installed

### Audio drill export (Phase 9.1)

- [x] **AUDIO-01**: One `TTSEngine` interface with named registered implementations; adding an engine is a new module plus a settings entry, never a dispatcher branch, and the registry is the model-backend shape, not a second idiom
- [x] **AUDIO-02**: `edge-tts` (network, MP3-native), Piper (local, WAV), and `transcript-only` (the always-available null engine) all register by name; Kokoro is documented as a registration target and is not built
- [x] **AUDIO-03**: A pack sequences stem → timed pause → key → why, with the pause duration read from a per-item-type settings map rather than a constant
- [x] **AUDIO-04**: An unreachable or missing engine never silently falls back — the command emits the transcript, names the engine and the reason, exits non-zero, and never half-writes an audio file (temp-then-atomic-rename)
- [x] **AUDIO-05**: `itembank export audio --objective <id>` and a daemon route both ship, reaching one runtime implementation — neither surface is the real one
- [x] **AUDIO-06**: Output defaults to MP3 with WAV available; `--split per-item` and `--split per-pack` both ship (per-pack default); one transcript per pack is always emitted with the same text in the same order; files are named from the objective id and a content digest so unchanged re-exports are idempotent
- [x] **AUDIO-07**: Listening records nothing (the evidence log stays the record of what was answered); no player, sync, or mobile build; every third-party artifact is pinned with a recorded checksum and named license review; the command's own help text states that edge-tts sends item text to Microsoft

### Canvas LMS Integration via LTI (Phase 999.4, BACKLOG — planned 2026-08-11)

> Backlog phase promoted to planning by the user on 2026-08-11 (the "real
> consumer exists" event the ROADMAP verdict asked for; see ROADMAP.md
> Phase 999.4 and `.planning/phases/999.4-canvas-lms-integration-lti/`).

- [ ] **LTI-01**: A launch is authenticated solely by LTI 1.3's own OIDC flow — login initiation, authorize redirect with one-time nonce/state, and a signed `id_token` verified against the platform's JWKS (signature, `iss`, `aud`, `nonce`, `exp`, `deployment_id`); a launch failing any check is refused by name, and itembank adds no accounts, passwords, or login page
- [ ] **LTI-02**: The LTI surface is an adapter over the existing JSON commands — it calls the same daemon handlers (`handle_api_*`) in-process, never parses a bank a second way, never decides correctness, and changes none of `API_ROUTES`, `SURFACE_PARITY`, or the route-scope test (Directive §4.2)
- [ ] **LTI-03**: The learner surface renders only `runtime.public_item()`; no key, why-best, distractor analysis, or higher-tier content is reachable before a recorded response for that item exists, and tier gating is server-side, identical to every surface (Directive §4.1)
- [ ] **LTI-04**: Deep linking — a verified `LtiDeepLinkingRequest` launch lets an instructor select exactly one objective from the local bank registry, returning one `ltiResourceLink` content item whose custom objective id the signed learner launch resolves through the existing stem allowlist; unresolvable objectives refuse by name
- [ ] **LTI-05**: AGS grade passback is outbound-only, at session completion, opt-in per launch (the AGS score scope must be present), with `scoreGiven`/`scoreMaximum` read from the runtime report, idempotent re-posts, and `short` items pending review never auto-graded (`gradingProgress: PendingManual` or no numeric publish); the evidence store stays the local record — the published score is a copy, not a second store
- [ ] **LTI-06**: The LTI bind is opt-in with the loopback default unchanged; TLS is stdlib `ssl` with user-supplied certs or a documented reverse proxy, and `public_base_url` is the one knob driving every URL the platform calls — no new auth surface beyond LTI's own
- [ ] **LTI-07**: The surface, its help text, and its hosting doc state exactly what leaves the machine (item text to the learner's browser via the LMS, the final score to the LMS gradebook; no telemetry, no hosted storage); the LTI crypto dependencies (`cryptography`, `PyJWT`) are optional, pinned, checksummed, and license-reviewed per Directive 4a, with a named refusal when absent

### Reading & teaching surface quality (Phase 13.5)

> Renumbered from Phase 14 on 2026-08-13. The source-to-course reframe claimed
> the number 14 for Course Workspace & Source Binding; this work kept its content
> and changed its number. See `.planning/quick/260813-r5c-merge-source-to-course-renumber-13-5/PLAN.md`.
>
> IDs assigned at plan time on 2026-08-12; the roadmap recorded them as TBD.
> Every one of Phase 13.5's six success criteria maps to at least one row:
> criterion 1 → RTS-02; criterion 2 → RTS-01, RTS-03, RTS-04; criterion 3 →
> RTS-05; criterion 4 → RTS-06; criterion 5 → RTS-07, RTS-08; criterion 6 →
> RTS-09, RTS-10, RTS-11, RTS-12.

- [ ] **RTS-01**: Every `var(--…)` a served reader, quiz, study or day page references resolves to a custom property defined in that same document, proven by a fixture that fails naming the token, the document and a referencing selector
- [x] **RTS-02**: The first line of an item stem is fully visible on first paint at 1280/768/375/320px and at 200% zoom, scripting on and off, and every in-page anchor jump lands clear of the sticky band; the band never exceeds two rows and a card already fully in view is not scrolled
- [x] **RTS-03**: The reader and the sat quiz render in the same vendored voices on one type scale — five sizes, two weights, no literal family, no colour literal — and every daemon-served page declares all four `@font-face` rules with root-absolute urls that return 200
- [ ] **RTS-04**: The reader's vertical rhythm and reading measure are set against the shipped faces as they actually render: 24px paragraph rhythm against a 29.7px line box, 66 real characters per line, x-height-matched inline runs, and a step down to an existing token below 480px
- [x] **RTS-05**: The glossary gloss lands at its term, flips at the viewport edges, becomes a bottom sheet on a narrow coarse pointer, opens on hover intent that never moves focus and never steals a pinned panel, links onward to the `[!KEY]` card and the full entry, and returns the learner to the text — with the click and keyboard path complete without script
- [x] **RTS-06**: `reader_nav` ships `none | column | rail | auto` with `auto` default: a lesson of four or more sections offers a nav, a shorter one does not, the rail occupies otherwise-empty margin at 1280px and wider without changing the reading measure, and the print rule stays inside the print block
- [ ] **RTS-07**: The six-tier authored hint ladder is reachable from the browser and from the CLI through one runtime-owned route; the payload carries shown tiers' resolved text plus locked headers and unlock sentences and nothing else, no request can name a tier, and drill/diagnostic/exam return the ladder unavailable with the mode's own stated reason
- [ ] **RTS-08**: The wrong-answer state renders the ladder in an in-flow support region above a collapsed generated-help disclosure; each opened tier adds a card and replaces none; the whole ladder is operable with no script and no network; and absence of a model is communicated only by the absence of an offer
- [ ] **RTS-09**: Nothing on screen pre-announces a reveal — no progress indicator over the ladder, no reveal control, no dimmed or `aria-disabled` affordance, a locked card carrying only its header and unlock sentence, and no first person or encouragement anywhere in the ladder
- [ ] **RTS-10**: A rendered page holds exactly one polite announcing region in the steady state — two on a visual item, as the recorded `06.1-UI-SPEC` exception — with two named transient exceptions, and both blocking-failure paths provably announce with the live attributes written before the text
- [x] **RTS-11**: Every element that is itself an interactive control or an input surface carries a boundary at 3:1 or better against the surface behind it in both modes, and the six semantic tokens the ladder needs ship measured by the project's own contrast function rather than assumed
- [ ] **RTS-12**: A bank with no `## TERMS` and no `## LESSON` renders byte-identically through the item path, proven by fixture

> **Destination after the reframe (recorded 2026-08-13).** These twelve rows are
> not retired by the source-to-course milestone; `research/phase-16/14-synthesis.md`
> section 15 gives each of them a home. RTS-01, RTS-03, RTS-04 and RTS-11 are
> inputs to subphase 17A (visual system and component foundation); RTS-02 and
> RTS-06 to 16B (IA, modes and recovery); RTS-05 to 16A (semantic capability
> contract, where hover/focus/touch definitions are the first catalogued
> capability); RTS-07, RTS-08 and RTS-09 to exit gate G6 (assessment authority),
> which the reframe leaves untouched; RTS-10 and RTS-12 to gate G4 (portable
> capability). Executing them now makes them the prototypes section 15 requires
> before those contracts freeze.

## Next-milestone source-to-course requirements

These requirements implement `.planning/SOURCE-TO-COURSE.md`. They compose the
shipped bank, lesson, audit, model, and evidence contracts rather than replacing
them.

> **Family expansion recorded 2026-08-13** (per `research/phase-16/14-synthesis.md`
> section 14, `.planning/REQUIREMENTS.md` block). The three original next-milestone
> families `COURSE-01..04`, `DIRECTOR-01..04`, and `LEARNUI-01..04` are superseded
> and expanded into eighteen families that carry owner, durable object, authority,
> degraded state, and verification gate on every clause. The original rows are kept
> below with a supersession pointer, never deleted, so traceability holds. No scope
> is dropped; each original clause maps forward through the table that follows.
>
> Two contract reversals are recorded here so they are not rediscovered later.
> First, any reading of `COURSE-01`'s "objective hierarchy" as a universal
> hierarchy or fixed prerequisite tree is superseded by the constrained typed graph
> plus authored outline projection in `GRAPH-01` and `GRAPH-02` (per synthesis
> sections 5 and 12.4). Second, any aggregate completion, mastery, or readiness
> score is superseded by the independent honest-progress tuple in `GRAPH-03` (per
> synthesis section 5 and the section 12.4 hard rejection of a single aggregate
> score). Widget-specific lesson grammar is likewise superseded: teaching meaning
> is expressed as semantic roles composed from shared primitives in `CAP-01`, not
> as per-widget content types (per synthesis section 4).

**Old-to-new family map (supersedes, does not delete):**

| Superseded ID (2026-08-13) | Replacing requirements |
|---|---|
| COURSE-01 | GRAPH-01, GRAPH-03, FILE-01, ID-01, APP-01 |
| COURSE-02 | FILE-02, RIGHTS-01 |
| COURSE-03 | TREAT-02, ID-02 |
| COURSE-04 | TREAT-01 |
| DIRECTOR-01 | AGENT-02 |
| DIRECTOR-02 | AGENT-01 |
| DIRECTOR-03 | ACTIVITY-02 |
| DIRECTOR-04 | AGENT-03, GRAPH-03 |
| LEARNUI-01 | APP-01 |
| LEARNUI-02 | CAP-01, FLOW-02 |
| LEARNUI-03 | CAP-01, CAP-02 |
| LEARNUI-04 | FLOW-01, A11Y-01, VISUAL-01 |

### Course workspace (superseded 2026-08-13, retained for traceability)

> The `COURSE-*`, `DIRECTOR-*`, and `LEARNUI-*` rows below are superseded by the
> expanded families. Their text is preserved verbatim; see the map above for their
> replacements.

- [ ] **COURSE-01** (superseded 2026-08-13): A course is a first-class, readable artifact that names its
  target, learner, approved source and write roots, objective hierarchy,
  prerequisites, treatments, accepted artifacts, drafts, and evidence location;
  any machine index is derived and disposable.

- [ ] **COURSE-02** (superseded 2026-08-13): Discovery is read-only and root-bounded; scaffolding and
  binding are explicit, idempotent operations, and finding a file never grants
  permission to transmit or modify it.

- [ ] **COURSE-03** (superseded 2026-08-13): Every objective-to-source and coverage claim carries a stable
  locator, confidence, and state (`covered`, `thin`, `missing`, `conflicting`, or
  `unknown`); heading similarity alone cannot produce `covered`.

- [ ] **COURSE-04** (superseded 2026-08-13): Every objective has an explicit, reviewable treatment plan
  drawn from direct reading, excerpt, guided lesson, notes/terms, worked example,
  visual/demonstration, practice, test, assessment-first, or human review; direct
  reading is a complete result and generation is never the automatic default.

### AI course director and quality

- [ ] **DIRECTOR-01** (superseded 2026-08-13): Hosted coding-agent clients and registered local backends
  reach the same course operations and schemas; backend choice changes capability,
  latency, and privacy disclosure, not the course artifact contract.

- [ ] **DIRECTOR-02** (superseded 2026-08-13): AI autonomy is scoped per operation as recommend-only,
  draft-and-review, or approved bounded writes; proposals cite sources, label
  synthesis, show quality findings, and are inspectable and recoverable.

- [ ] **DIRECTOR-03** (superseded 2026-08-13): Standardized-test courses require a cited, versioned
  blueprint mapping domains, weights, cognitive demand, item conventions,
  difficulty, timing, permitted tools, and feedback mode; knowledge courses use
  their actual syllabus and expected demand. The UI never claims exam fidelity
  without this mapping.

- [ ] **DIRECTOR-04** (superseded 2026-08-13): Evidence-based proposals name their observation window,
  denominator, included and missing signals, uncertainty, and competing
  explanations. Sparse evidence cannot produce a mastery percentage or a confident
  causal claim. Accepted next actions remain recommendations until the learner or
  deterministic selection policy acts.

### Comprehensive learner UI

- [ ] **LEARNUI-01** (superseded 2026-08-13): The home surface is a course shelf and each course provides
  coherent Learn, Practice, Test, Sources, Course map, and Build/review areas; banks
  are assessment artifacts inside courses rather than the primary navigation unit.

- [ ] **LEARNUI-02** (superseded 2026-08-13): One parsed lesson supports continuous reader and guided modes;
  neither mode creates a second parser or scorer, and a learner can move between
  direct source reading, lesson, practice, feedback, and the next course action
  without reconstructing context.

- [ ] **LEARNUI-03** (superseded 2026-08-13): Lessons render semantic teaching roles: hover/focus
  definitions, things-to-know blocks, expert or niche tips, warnings, worked
  examples, citations, diagrams, math, runnable code, inline checks, hints, and
  accessible visual interactions—with graceful unavailable states and no
  decorative block required by style alone.

- [ ] **LEARNUI-04** (superseded 2026-08-13): The reference course tracer demonstrates orient → predict or
  act → observe → explain → changed-context transfer → evidence → next action at
  desktop and phone widths, including keyboard/screen-reader equivalence, model-
  unavailable operation, and no early keyed-content leak.

### Expanded source-to-course families (added 2026-08-13)

These eighteen families replace the three superseded families above, per
`research/phase-16/14-synthesis.md` section 14. Each requirement names its owner,
durable object, authority, degraded state, and verification gate; gate labels
`G1` through `G12` are the synthesis section 16 exit gates. Registered, prototype,
and backburner capabilities stay in traceability so architecture breadth survives
staged implementation (per synthesis sections 1 and 12).

#### GRAPH: objective graph, pathways, and honest progress

- [ ] **GRAPH-01**: The durable instructional spine is a constrained, layered typed
  graph of concepts and objectives; structural containment nodes accept local
  labels (program, semester, module, week, unit, chapter) without schema change,
  and structural order never implies prerequisite status. An imported scope or
  framework binds as an immutable version; local edits are overlay records with
  their own identity and a migration relation, never edits to the import (lands
  clauses C011/C075, 2026-08-14). Owner: course builder via
  curriculum-design. Durable object: course objective graph. Authority: versioned
  course graph records. Degraded: with no graph, the authored outline projection
  still reads in plain Markdown. Gate: G2, G5. (per synthesis sections 2.2, 5;
  supersedes any universal-hierarchy reading of COURSE-01.) Fixture: the 14B
  three-domain graph tracer, a synthetic course graph spanning three fictional
  domains with structural containers labeled module, week, and chapter,
  asserting the outline projection reads in plain Markdown and structural order
  mints no prerequisite edge.

- [ ] **GRAPH-02**: Dependency edges carry type, authority, rationale, confidence,
  and override policy; hard gates are exceptional, and alignment never implies
  evidence transfer. Owner: course builder. Durable object: typed relation records.
  Authority: course graph. Degraded: an unknown edge type renders as an advisory
  recommended-before, never a hard block. Gate: G5. (per synthesis sections 2.2,
  5.) Fixture: the 14B three-domain graph tracer extended with one edge of every
  registered type plus one deliberately unknown edge type, asserting the unknown
  type renders as an advisory recommended-before and never a hard block.

- [ ] **GRAPH-03**: Progress is reported through the independent tuple (claim kind,
  scope/version, numerator, denominator or indeterminate, rule, snapshot/window,
  settled/pending/unknown, authority, uncertainty); the seven dimensions (design
  coverage, participation, settled evidence, current retention, formal
  completion, selected enrichment, uncertainty) stay
  separate and no single aggregate completion, mastery, or readiness score is
  produced *(this last clause is **amended 2026-08-27**, see the amendment note
  at the end of this requirement; the seven dimensions still stay separate, but
  an aggregate figure and a percent display are now permitted)*. Required, required-choice, and enrichment memberships keep separate
  denominators, and adding enrichment can never lower completion. A bounded,
  versioned course may truthfully report complete under its named predicate; an
  open field has no universal completion percentage; formal completion persists
  while retention may decay (lands clauses C073/C078/C079, 2026-08-14). Difficulty, Stability, and Retrievability are inspectable, but
  Retrievability is never surfaced to the learner as a percentage; the learner
  display uses the per-objective, self-adjustable fill state resolved in
  D-14A-3, never a probability number (bake-in 2026-08-14, per
  `research/2026-08-10-ui-inspiration-missing-surfaces.md`). Owner: runtime for settled evidence, course records for design
  coverage. Durable object: progress claim. Authority: evidence store and course
  records by dimension. Degraded: a missing denominator reports indeterminate,
  never an invented percent. Gate: G5. (per synthesis section 5; supersedes the
  aggregate-score idea rejected in section 12.4.) Fixture: a synthetic evidence
  set in the 16C cross-subject missing-feature suite with a missing denominator,
  a pending prose mark, and a version-split objective, asserting each tuple
  dimension reports separately *(the "and no aggregate score appears" leg of
  this fixture is amended 2026-08-27, see below)*.

  **Amendment 2026-08-27, owner ruling.** Weibao ruled, verbatim in
  `USER-VISION.md`: "Percent is fine even if it breaks contract, since
  uservision over any other contracts and more". Under the precedence rule that
  same statement establishes, `USER-VISION.md` outranks this requirement.
  Disposition recorded as `IDEA-LEDGER.md` IL-20260827-01.

  - **Permitted from 2026-08-27:** a single aggregate completion, mastery, or
    readiness figure may be produced and displayed, and a percent character may
    appear in learner-facing progress display including a course card.
  - **Unchanged, and not reached by the ruling:** the seven dimensions still
    stay separate underneath, because the aggregate is now a permitted
    *display* over them and not a replacement for them. Required,
    required-choice, and enrichment memberships still keep separate
    denominators. Adding enrichment still never lowers completion. A bounded,
    versioned course may still truthfully report complete under its named
    predicate.
  - **Also unchanged, and adjacent enough to name:** the degraded rule that a
    missing denominator reports indeterminate and never an invented percent,
    and the D-14A-3 decision that Retrievability is never surfaced to the
    learner as a percentage. Neither was raised in the ruling. Both are
    strikeable by the same authority if Weibao wants them gone; they are left
    standing rather than widened by inference.
  - **Consequence for the fixture:** the 16C suite asserts each dimension
    reports separately, and no longer asserts the absence of an aggregate.

- [ ] **GRAPH-04**: Objective splits, merges, renames, and changed demand generate
  reviewed migration proposals; historical evidence is never transferred
  automatically. Owner: reviewer via curriculum-design. Durable object: migration
  relation. Authority: reviewer acceptance. Degraded: unmigrated evidence stays on
  the original objective identity and reads as unknown for the new one. Gate: G5.
  (per synthesis sections 5, 6; section 12.4 rejection of automatic transfer.)
  Fixture: a 14B three-domain graph tracer scenario that splits one synthetic
  objective and renames another, asserting a reviewed migration proposal is
  generated and unmigrated evidence reads unknown on the new identity.

#### FILE: multi-root files, discovery, and operations

- [ ] **FILE-01**: A course links user files where they live and edits owned files
  in place across multiple approved roots (vault, source, bank, note directories).
  Owner: learner and course builder. Durable object: linked or owned file plus
  metadata. Authority: filesystem bytes plus course binding records. Degraded: an
  unreachable root reports unavailable and the course opens over the last valid
  index. Gate: G3. (per synthesis section 6.) Fixture: the 14A file-fault and
  external-edit tracer's synthetic multi-root tree (vault, source, bank, and
  note directories of fictional files), with one root made unreachable to assert
  the course opens over the last valid index.
  *Pointer added 2026-08-27: FILE-01's degraded clause becomes implementable
  under FILE-04, which persists the index the clause needs. FILE-01's text is
  unchanged.*

- [ ] **FILE-02**: Discovery is read-only, root-bounded, cancellable, resumable,
  symlink-safe, and useful before completion; it never grants transmit, transform,
  execute, or write authority. Owner: discovery-and-binding skill. Durable object:
  disposable discovery index. Authority: read-root approval. Degraded: an
  interrupted scan yields partial, clearly-marked results with omissions visible.
  Gate: G3, G11. (per synthesis sections 3, 6, 11.5; retains COURSE-02.)
  Fixture: a 14A tracer discovery run over the synthetic multi-root tree seeded
  with a symlink cycle and an out-of-root symlink, cancelled midway, asserting
  partial results are clearly marked and no write, transmit, or execute occurs.

- [ ] **FILE-03**: Link, import, copy, move, supersede, and migrate are distinct
  operations with distinct identity effects and approval and recovery semantics; no
  automatic merge is permitted and name similarity is only a search hint. Owner:
  course builder. Durable object: operation record plus affected files. Authority:
  explicit per-operation approval. Degraded: an ambiguous match is surfaced for
  manual reconciliation, never merged. Gate: G3. (per synthesis section 6 table;
  supersedes name-based identity rejected in section 12.4.) Fixture: a 14A
  tracer scenario with two synthetic near-identically-named files that differ in
  bytes, exercising link, import, copy, move, and supersede as distinct
  journaled operations and asserting the name match is surfaced, never auto-
  merged.

- [ ] **FILE-04**: A workspace names the learner's set of courses as an ordered
  set of approved roots plus one durable member entry per course, pinned by
  `course_object_id` rather than by directory name; the course index built by
  walking those roots is derived and disposable. The workspace is a locator set
  and not a membership set: it carries no objective, no completion predicate,
  and no progress claim, and every question of curricular membership,
  boundedness, and rollup stays with the scope object and GRAPH-03. It is
  machine-local and never travels in a course package. Owner: the learner.
  Durable object: workspace record. Authority: root approval by the learner,
  mutated only through the operation journal. Degraded: an absent record or an
  empty root list is not an error and degrades to a single-root scan, so a fresh
  install needs no setup step before the shelf works; an unreachable root reports
  unavailable and its courses open over the last valid index, marked unavailable
  rather than dropped; a pinned id that disagrees with the sidecar found at its
  path is a conflict, surfaced and never merged. Gate: G3. (per synthesis
  section 6; makes FILE-01's degraded clause implementable, and supersedes the
  daemon-root-is-the-workspace assumption at `16B-04-PLAN.md:382`.) Fixture: a
  synthetic two-root workspace holding three courses, one root made unreachable,
  one course moved between roots, and one path whose sidecar reports a different
  `course_object_id`, asserting the unreachable root's courses render from the
  last valid index as unavailable, the moved course reconciles by id to one card
  rather than two, and the id disagreement reports a conflict without writing.

#### ID: stable identity, fingerprints, and versions

- [ ] **ID-01**: Every durable object carries a stable opaque ID plus fingerprint,
  revision, and the applicable profile, source, and generator versions, each with a
  distinct purpose. Owner: runtime and course records. Durable object: identity
  fields on every object. Authority: minting is a runtime or course operation.
  Degraded: a missing fingerprint blocks a compare-and-swap write rather than
  allowing a blind overwrite. Gate: G2, G3. (per synthesis section 6.) Fixture:
  the 14A tracer's synthetic object set minted with IDs, fingerprints,
  revisions, and version fields, plus one object stripped of its fingerprint to
  assert the compare-and-swap write is blocked.

- [ ] **ID-02**: Hashes detect change but never prove identity, truth, authorship,
  or rights; same ID with divergent bytes is a conflict, same fingerprint with
  different IDs suggests a copy, and a moved path with the same ID is a move
  candidate. Owner: runtime. Durable object: identity and conflict state. Authority:
  runtime identity rules. Degraded: an undecidable case is reported as a conflict
  for review. Gate: G3. (per synthesis section 6; retains COURSE-03; supersedes
  hash, path, or name as durable identity, rejected in section 12.4.) Fixture:
  the 14A external-edit tracer cases built from synthetic files (same ID with
  divergent bytes, same fingerprint with different IDs, moved path with same
  ID), asserting conflict, copy-candidate, and move-candidate outcomes
  respectively.

#### TREAT: treatment decisions and source binding

- [ ] **TREAT-01**: Every objective has an explicit, reviewable treatment chosen
  from direct reading, excerpt, guided lesson, notes or terms, worked example,
  visual or demonstration, practice, formal test, assessment-first diagnostic,
  learner artifact, or human review; direct reading is a complete result and
  generation is never the automatic default. Owner: course builder via absorb-book.
  Durable object: treatment binding. Authority: reviewer acceptance. Degraded: an
  objective with no chosen treatment reads as untreated, never silently generated.
  Gate: G7. (per synthesis sections 3 Loop B, 7; retains COURSE-04.) Fixture:
  the 15A four-subject recommendation review over four synthetic subject
  outlines, including one objective bound to direct reading as a complete result
  and one left untreated, asserting nothing is silently generated.

- [ ] **TREAT-02**: Every objective-to-source and coverage claim carries a stable
  locator, confidence, and state (covered, thin, missing, conflicting, unknown);
  heading or name similarity alone cannot produce covered. Owner: course builder.
  Durable object: source binding. Authority: reviewed binding records. Degraded: an
  unverifiable claim reads as unknown, not covered. Gate: G7. (per synthesis
  section 2.2; retains COURSE-03.) Fixture: a 15A synthetic binding set carrying
  one covered, one thin, one missing, one conflicting, and one unknown claim,
  plus a heading-similarity decoy that must not read as covered.

#### FLOW: core end-to-end loops

- [ ] **FLOW-01**: The seven core loops (A discover and bind, B design a course, C
  learn and construct notes, D practice and test, E evidence and remediation, F
  author, review, and accept, G maintain, recover, and leave) are the product's
  end-to-end acceptance surface, each resumable with an exact position and a next
  justified action. Owner: runtime plus app. Durable object: session and course
  state. Authority: runtime for assessment loops, course records elsewhere.
  Degraded: an interrupted loop preserves the last accepted state and exposes the
  next safe action. Gate: G8. (per synthesis section 3; retains LEARNUI-04.)
  Fixture: the 16B storyboard and interruption scenarios, interrupting a
  synthetic run of each of loops A through G mid-step and asserting each resumes
  at an exact position with a next justified action.

- [ ] **FLOW-02**: A learner moves between direct source reading, lesson, practice,
  feedback, and the next course action without reconstructing context, and no loop
  introduces a second parser or scorer. Reading is continuous and scrolls; no
  reading surface paginates. A Socratic or tutoring refusal renders as a locked
  card stating its unlock condition, never as a chat exchange (bake-in
  2026-08-14, consistent with RTS-09's locked-card contract). Owner: app. Durable object: navigation and
  resume state. Authority: runtime. Degraded: a model-unavailable state still allows
  reading, scoring, the authored hint ladder, evidence, and reports. Gate: G8. (per
  synthesis section 3 Loops C and D; retains LEARNUI-02.) Fixture: a 16B
  storyboard scenario walking a synthetic reading, lesson, practice, and
  feedback path with the model backend disabled, asserting scoring, the authored
  hint ladder, evidence, and reports still run through the one runtime.

#### CAP: semantic lesson capability catalog

- [ ] **CAP-01**: One parsed canonical lesson supports both continuous reader and
  guided modes and renders semantic teaching roles (key idea, warning, prerequisite,
  misconception, expert tip, worked example, counterexample, source excerpt, term
  and definition, uncertainty, summary, inline check, hint, accessible visual
  interaction) composed from shared primitives, not separate content types. The
  default block order for a new conceptual lesson places a worked example or
  concrete case before the formal definition; an author or course director may
  override per lesson with a recorded reason (bake-in 2026-08-14, per
  `research/2026-08-10-style-registry-mechanics.md`). Semantic emphasis is
  author-provided orientation; no flow may compel learner highlighting, which
  aids memory but not comprehension (bake-in 2026-08-14, per
  `research/phase-16/12-active-annotation-notes.md`). Owner:
  lesson-authoring skill. Durable object: canonical Markdown lesson. Authority: one
  parser. Degraded: an unknown optional semantic renders its fallback with a warning;
  an unknown required semantic fails safely. Gate: G4. (per synthesis sections 4,
  7.1; retains LEARNUI-03; supersedes widget-specific lesson grammar.) Fixture:
  the 16A portable rich lesson stress corpus, one synthetic lesson exercising
  every semantic teaching role plus one unknown optional and one unknown
  required semantic, rendered in both continuous reader and guided modes. The
  corpus also carries a medical evolving-case fixture with a dated jurisdiction
  warning and no premature reveal, and a disputed-timeline fixture preserving
  disagreement, locators, and uncertainty (lands clauses C196/C197, 2026-08-14).

- [ ] **CAP-02**: Each semantic capability declares an accessible-behavior,
  offline-fallback, renderer-availability, version, validation, and known-limits
  profile, and each media asset carries rights, credit, accessible-alternative,
  derivation, availability, and integrity metadata (media sentence lands clause
  C067, 2026-08-14); no decorative block is required by style alone. Owner:
  capability owner via MAINT. Durable object: capability support profile. Authority: capability
  registry. Degraded: an unavailable renderer shows the static instructional path.
  Gate: G4. (per synthesis sections 4.1, 4.2.) Fixture: a 16A profile fixture
  declaring one synthetic capability's full support profile and a second
  capability with its renderer marked unavailable, asserting the static
  instructional path is shown.

- [ ] **CAP-03**: Registered output modes (notebook page, outline, Cornell notes,
  concept map, glossary, formula sheet, timeline, comparison table, study guide,
  source-extracted notes) compose from shared note and activity schemas plus
  provenance; a new canonical type is minted only when validation or behavior
  genuinely differs. Owner: lesson-authoring skill. Durable object: registered
  output-mode record. Authority: capability registry. Degraded: an unregistered mode
  stays a backburner catalog entry naming its shared primitive, dependency, cost,
  and trigger. Gate: G4, G12. (per synthesis sections 12.2, 12.3; breadth
  preservation.) Fixture: a 16A fixture composing two registered output modes
  (outline and glossary) from one stress-corpus lesson's shared schemas, plus
  one unregistered mode entry asserting it stays a backburner catalog record
  naming its primitive, dependency, cost, and trigger.

#### ACTIVITY: purpose-first activities and runtime-owned assessment

- [ ] **ACTIVITY-01**: Every activity declares purpose, cognitive demand, objective,
  stimulus or source, response schema, retry behavior, feedback and disclosure
  policy, evidence status, accessibility equivalence, and static fallback; existing
  response forms serve many purposes and a new item type is warranted only when
  scoring semantics or response structure cannot be expressed safely. Owner:
  author-bank and lesson-authoring. Durable object: activity record. Authority:
  runtime for scored assessment. Degraded: an unsupported response form falls back
  to its declared static equivalent. Gate: G6, G7. (per synthesis section 7.3.)
  Fixture: a 16A synthetic activity set exercising each declared purpose over
  the existing response forms, including one unsupported response form that must
  fall back to its declared static equivalent.

- [ ] **ACTIVITY-02**: Formal assessment fidelity requires a cited, versioned
  blueprint (construct, domain weight, demand, format, difficulty, timing, tools,
  feedback conditions); the UI never claims exam fidelity without it, and
  practice-generated questions stay drafts until parser, lint, review, blueprint,
  and runtime gates pass. Owner: course builder via author-bank. Durable object:
  blueprint plus frozen form. Authority: runtime and reviewer. Degraded: absent a
  blueprint, the course presents practice without an exam-fidelity claim. Gate: G6,
  G7. (per synthesis section 7.3; retains DIRECTOR-03.) Fixture: a 15B
  acceptance tracer pairing a synthetic cited blueprint with a draft question
  set, asserting the exam-fidelity claim appears only after the parser, lint,
  review, blueprint, and runtime gates pass.

- [ ] **ACTIVITY-03**: The runtime alone scores, grants keyed disclosure, selects
  authoritative assessment behavior, and writes assessment evidence; prose remains
  pending until approved marking, and no surface, agent, note, import, or visual
  leaks a key, invents a score, auto-grades prose, or changes a frozen sitting.
  Owner: deterministic runtime. Durable object: attempt evidence event. Authority:
  runtime. Degraded: with no model, formal sittings run unchanged under runtime
  authority. Gate: G6. (per synthesis sections 2.3, 4.2.) Fixture: a 16A
  adversarial fixture in which a scripted agent, a note, and an import each
  attempt to leak a key, invent a score, auto-grade prose, or edit a frozen
  synthetic sitting, asserting the runtime refuses each attempt.

#### NOTE: learner-owned notes and artifacts

- [ ] **NOTE-01**: Notes are learner-owned artifacts, never annotations baked into
  accepted lessons, and carry note ID, ownership, course and objective relation,
  anchor or selector, source or lesson revision, authorship type, strategy, text or
  structure, privacy, revision, and optional promotion or review state. Authored
  pre-highlighting is orientation, never learner evidence (lands clause C107,
  2026-08-14). Owner:
  learner. Durable object: note file or learner record. Authority: learner.
  Degraded: a stale anchor keeps the note attached to its objective and flags the
  broken selector. Gate: G9. (per synthesis section 7.2.) Fixture: the 16C
  suite's synthetic note set anchored to a synthetic lesson, with one anchor
  invalidated by a lesson revision, asserting the note stays attached to its
  objective with the broken selector flagged.

- [ ] **NOTE-02**: Notes may ground reflection, retrieval proposals, and draft
  questions but never silently become accepted source, lesson, key, score, or
  mastery; promotion requires explicit source-backed review. Owner: reviewer.
  Durable object: promotion and review record. Authority: reviewer acceptance over
  source-backed content. Degraded: an unreviewed note stays learner-private and
  non-authoritative. Gate: G9, G6. (per synthesis section 7.2; section 12.4
  rejection of silent promotion.) Fixture: a 16C scenario promoting one
  synthetic note through source-backed review while a second unreviewed note is
  asserted to stay learner-private and non-authoritative.

- [ ] **NOTE-03**: A learner artifact (proof, program, diagram, explanation,
  project, observation) carries a rubric and pending or review state and produces
  descriptive or pending evidence until reviewed. Owner: learner and reviewer.
  Durable object: learner-owned file plus evidence relation. Authority: runtime
  records pending, reviewer settles. Degraded: unreviewed artifacts read as pending,
  never as settled mastery. Gate: G9. (per synthesis section 7.3.) Fixture: a
  16C synthetic learner artifact, a fictional proof with a rubric, asserted to
  read as pending evidence until a scripted review settles it.

#### STRATEGY: registered finite learning strategies

- [ ] **STRATEGY-01**: Learning strategies are a finite registered set (continuous
  reading, guided note spine, worked reasoning, retrieval-first or assessment-first
  where policy permits) sharing canonical objects; each states purpose, eligibility,
  required and optional learner actions, skip and resume, evidence effects,
  accommodations, offline behavior, and tests. Owner: course builder within the
  catalog. Durable object: versioned strategy registry. Authority: objective and
  blueprint eligibility plus runtime for assessment. Degraded: an unavailable
  strategy falls back to continuous reading. Gate: G9. (per synthesis sections 7.2,
  8.) Fixture: the 16C cross-subject missing-feature suite running each
  registered strategy against the synthetic subjects, with one strategy marked
  unavailable, asserting fallback to continuous reading.

- [ ] **STRATEGY-02**: Learner preference, author or course strategy, objective
  constraint, accommodation override, instructor policy, runtime authority, and
  system safety are ordered precedence layers; a learner chooses only among allowed
  strategies and runtime assessment behavior is never user-configurable during a
  sitting. Owner: layered per row. Durable object: preference and policy records.
  Authority: the precedence order is fixed. Degraded: a conflicting preference
  yields to the higher layer with a stated reason. Gate: G9. (per synthesis section
  8 table.) Fixture: a 16C conflict-matrix fixture in which a synthetic learner
  preference contradicts an accommodation override and an instructor policy,
  asserting each yields to the higher layer with a stated reason and no mid-
  sitting change.

#### RIGHTS: rights by operation and egress

- [ ] **RIGHTS-01**: Rights are operation-specific (read, quote, transform, remote
  process, package, export, share) recorded per source; unknown stays unknown and
  restrictive, and finding a file never grants permission to transmit or modify it.
  A source's rights authority is its owner or license terms; the local reader of
  a file is not thereby its rights owner, and the source record carries edition
  and scope (lands clause C004, 2026-08-14).
  Owner: source owner plus learner policy. Durable object: rights grant record.
  Authority: local policy record. Degraded: an unknown right refuses the unsafe
  operation by name. Gate: G11. (per synthesis sections 2.2, 6, 11.2; retains
  COURSE-02.) Fixture: a 14A tracer scenario over synthetic sources granted
  differing per-operation rights, including one source with unknown rights,
  asserting the unsafe operation is refused by name.

- [ ] **RIGHTS-02**: Hosted operations minimize and disclose exact egress, agents
  receive only approved source spans and operation authority, and presentation
  visibility is never authorization. Owner: agent client plus runtime. Durable
  object: operation manifest plus egress log. Authority: rights and egress policy.
  Degraded: no reachable backend keeps all core work local and model-free. Gate:
  G11. (per synthesis sections 2.3, 10, 11.1; section 12.4 rejection of presentation
  state as authorization.) Fixture: a 15A recommendation-review run against a
  mock hosted backend, asserting the egress log lists exactly the approved
  synthetic source spans and that an unreachable backend leaves all core work
  local and model-free.

#### A11Y: authored-output accessibility and localization

- [ ] **A11Y-01**: Representative authored outputs pass keyboard, touch,
  screen-reader, zoom and reflow, high-contrast, reduced-motion, and equivalent-task
  review; WCAG checks are necessary but insufficient and AI never self-certifies
  accessibility. Owner: reviewer plus capability owner. Durable object:
  accessibility review record. Authority: human acceptance. Degraded: an output
  failing equivalence review is not accepted; its inaccessible form is rejected
  while the capability remains pending equivalence. Gate: G4, G11. (per synthesis
  section 11.4; section 12.4 rejection of hover-only or visual-only
  equivalence.) Fixture: the 17A same-flow accessibility QA pass over one
  synthetic authored lesson driven by keyboard, screen reader script, zoom and
  reflow, high contrast, and reduced motion, including a deliberately hover-only
  variant that must fail equivalence review.

- [ ] **A11Y-02**: Canonical records carry language and direction, and localization
  fixtures cover RTL, mixed code and math direction, CJK, combining marks, long
  strings, localized numbers and units, and culturally dependent examples. Owner:
  lesson-authoring plus MAINT. Durable object: localization fixtures plus language
  metadata. Authority: capability validation. Degraded: an unhandled locale renders
  a clearly-marked fallback rather than corrupt text. Gate: G4, G11. (per synthesis
  section 11.3.) Fixture: the localization fixture set named above, built as
  synthetic strings (RTL, mixed code and math direction, CJK, combining marks,
  long strings, localized numbers and units) inside the 16A portable rich lesson
  stress corpus.

#### PORT: portability, interchange, and restore

- [ ] **PORT-01**: The canonical lesson is UTF-8 Markdown with shallow metadata and
  an additive, versioned semantic profile; complete core meaning, captions,
  citations, definitions, static activity instructions, and media alternatives
  remain readable outside the app, and derived HTML, index, or cache is never the
  sole understandable copy. A proprietary or open-package canonical format stays
  rejected unless every criterion in research report 04 section 8 passes (lands
  clause C097, 2026-08-14). Owner: lesson-authoring. Durable object: canonical
  Markdown file. Authority: one parser. Degraded: an unknown optional semantic
  renders its fallback; derived views are disposable and rebuildable. Gate: G10, G4.
  (per synthesis section 6; section 12.4 rejection of derived-only meaning.)
  Fixture: a 16A stress-corpus lesson opened outside the app in a plain Markdown
  viewer with every derived HTML, index, and cache deleted, asserting core
  meaning, captions, citations, and fallbacks stay readable and the derived
  views rebuild.

- [ ] **PORT-02**: Portability is reported at five levels (readable, structurally
  editable, behaviorally executable, evidence-preserving, round-trip safe);
  interchange adapters carry a supported profile, conformance fixtures, and an
  explicit semantic loss report; EPUB and narrow QTI are prototypes, and broader
  packaging waits for a named consumer. Owner: export and adapter owner. Durable
  object: export package plus loss report. Authority: adapter conformance suite.
  Degraded: an unsupported capability appears in the loss report, never silently
  dropped. Gate: G10. (per synthesis sections 4.2, 6; section 12.5 backburner.)
  Fixture: the adapter conformance fixtures named above, exercised in the 17B
  end-to-end tracer as a synthetic export through the EPUB and narrow QTI
  prototype adapters, asserting each emits an explicit semantic loss report.

- [ ] **PORT-03**: Export is not complete until a clean-machine, offline restore
  validates a manifest and reports every loss, restoring all supported canonical
  objects and evidence. Owner: packaging owner. Durable object: restore manifest.
  Authority: restore validation. Degraded: a restore gap is reported against the
  manifest, not silently accepted. Gate: G10. (per synthesis section 6.)
  Fixture: the 14B clean restore drill, exporting a synthetic course and
  restoring it on a clean offline machine against its manifest, asserting every
  loss is reported.

#### RELIABILITY: atomic mutation, journals, and staleness

- [ ] **RELIABILITY-01**: Every durable mutation uses an expected-base fingerprint
  compare-and-swap, temporary output, validation, atomic commit, and an operation
  journal; fault injection yields the old or new valid state, never a mixed state.
  Owner: runtime plus operation owner. Durable object: journaled operation.
  Authority: runtime write path. Degraded: crash, disk-full, offline, or
  permission-denied preserves the last accepted state. Gate: G3. (per synthesis
  sections 6, 11.7.) Fixture: the 14A file-fault tracer injecting crash, disk-
  full, and permission-denied faults into a synthetic compare-and-swap write,
  asserting the old or new valid state survives and the journal records the
  operation.

- [ ] **RELIABILITY-02**: Agent and maintenance operations run through a durable
  local operation journal with intent, actor, scopes, inputs, expected fingerprints,
  phases, checkpoints, proposals, validation, and undo, shared across hosted, local,
  and manual continuation. Owner: agent client. Durable object: operation journal.
  Authority: the journal is the durable job record, not a chat transcript. Degraded:
  an interrupted job resumes or reverses from its last checkpoint. Gate: G3, G12.
  (per synthesis sections 2.2, 10.) Fixture: a 15A journaled synthetic agent
  operation interrupted at each checkpoint phase, asserting resume and reverse
  work from the journal alone without any chat transcript.

- [ ] **RELIABILITY-03**: External, source, or version changes mark affected
  bindings and proposals stale and require a rebind, migrate, supersede, or retain
  review; a stale derivative is rebuilt, never trusted silently. Owner: course
  builder plus UPGRADE. Durable object: staleness and dependency state. Authority:
  reviewer for rebinding. Degraded: a stale proposal is shown as stale and blocked
  from acceptance until reconciled. Gate: G3. (per synthesis sections 3 Loop G,
  6.) Fixture: a 15B acceptance-tracer scenario editing a synthetic source out
  from under its bindings, asserting dependents mark stale and acceptance is
  blocked until a rebind, migrate, supersede, or retain review.

#### APP: course-first information architecture and packaging

- [ ] **APP-01**: The home surface is a course shelf with an exact resume cue and
  attention state; each course exposes Overview, Learn, Practice, Test, Course map
  (outline first), Sources, Build and review, Evidence, and contextual Notes; banks
  are assessment artifacts inside courses, not the primary navigation unit. Owner:
  app. Durable object: course plus IA routes. Authority: course records. Degraded: a
  course that fails to load shows its last valid overview and plain-file access.
  Gate: G8. (per synthesis section 9.1; retains LEARNUI-01.) Fixture: the 16B
  storyboard's synthetic course shelf with two fictional courses, one corrupted
  so it must show its last valid overview and plain-file access, asserting exact
  resume cues and every named course section.

- [ ] **APP-02**: Navigation uses stable opaque deep links and anchors, explicit
  parent and back semantics, focus and scroll restoration, and the same routes
  across wide and narrow layouts; chat is contextual to an object or operation,
  never the home or sole job record. Owner: app. Durable object: route and anchor
  identity. Authority: app routing. Degraded: a narrow screen stacks supporting
  panes as destinations without losing routes. Gate: G8. (per synthesis section 9.1;
  section 12.4 rejection of chat-first home.) Fixture: 16B storyboard navigation
  scenarios replaying the same synthetic deep links across wide and narrow
  layouts, asserting focus and scroll restoration and identical routes in both.

- [ ] **APP-03**: First launch offers a clearly synthetic, removable sample course
  and a skippable, replayable walkthrough reachable without granting source roots or
  configuring an agent; help is offline and routes from named error codes, and long
  jobs never block learning or invent a percent when the denominator is unknown.
  Settings expose approved roots, model backends, network and egress policy,
  accessibility, theme, storage, backups, and update policy; the shipped DEL-04
  subset grows to this list at 16B (lands clause C137, 2026-08-14).
  Owner: app plus packaging. Durable object: sample course plus offline help bundle.
  Authority: app. Degraded: agent or network failure preserves local Learn,
  Practice, Test, Evidence, and search over the last valid index. Gate: G8, G10.
  (per synthesis section 9.2.) Fixture: the 16B first-launch interruption
  scenario running the clearly synthetic sample course and walkthrough with no
  roots granted, no agent configured, and the network disabled, asserting
  offline help routes from named error codes.

#### VISUAL: visual system and fixed rules

- [ ] **VISUAL-01**: The default visual direction is Structured Studio with Quiet
  Workbench density for long reading and bounded Guided Canvas staging for guided
  moments; all three project the same semantic flow rather than three products.
  Owner: visual system via UI-SPEC. Durable object: visual token set. Authority:
  fixed hierarchy and accessibility rules override theme. Degraded: missing theme
  assets fall back to the accessible default palette. Gate: G8. (per synthesis
  section 9.3.) Fixture: the 17A same-flow three-direction comparison, one
  synthetic lesson-plus-practice flow rendered in Structured Studio, Quiet
  Workbench, and Guided Canvas, asserting all three project the same semantic
  flow.

- [ ] **VISUAL-02**: Configurable tokens (light and dark palette, density, reading
  measure within safe bounds, approved local fonts, modest surface treatment,
  optional motion) are separated from fixed rules (content hierarchy, status
  meaning, focus visibility, contrast, keyboard order, target size, zoom and reflow,
  reduced motion, non-color state cues, source and acceptance visibility, semantic
  equivalence across widths); authors select semantic roles, never raw colors,
  shadows, coordinates, arbitrary icons, or animation. Owner: visual system. Durable
  object: token and rule split. Authority: fixed rules are non-configurable.
  Degraded: an out-of-bounds token clamps to its safe range. Gate: G8. (per
  synthesis section 9.3.) Fixture: a 17A token-abuse fixture applying out-of-
  bounds density, measure, and palette tokens over the same-flow three-direction
  comparison, asserting every fixed rule holds and each token clamps to its safe
  range.

#### AGENT: operation protocol and backend parity

- [ ] **AGENT-01**: All clients implement one operation protocol (declare intent;
  declare approved roots, rights, egress, write, and execute authority; inventory
  before creating; plan treatment; checkpoint; draft the smallest missing artifact;
  cite and label synthesis; run deterministic validation; render accessible, plain,
  and rich previews; show a bounded diff; pass configured review; commit atomic
  acceptance; update dependency and staleness; report undo and uncertainty). Owner:
  agent client. Durable object: operation journal plus accepted revision. Authority:
  reviewer for acceptance, runtime for assessment. Degraded: an unavailable agent
  leaves the core loop fully operable. Gate: G6, G12. (per synthesis section 10;
  retains DIRECTOR-02.) Fixture: a 15A four-subject review operation replayed
  step by step from a synthetic operation journal against the protocol
  checklist, asserting every protocol stage is present and the core loop stays
  operable with the agent disabled.

- [ ] **AGENT-02**: Hosted coding-agent and registered local backends reach the same
  operations and schemas; backend choice changes capability, latency, cost, and
  privacy disclosure, not the artifact or authority contract, and an agent may
  recommend, draft-and-review, or perform approved bounded writes but never
  self-expand scope, self-certify accessibility, silently accept its own
  uncertain source claim, transfer evidence, or cross runtime
  disclosure. Owner: agent client. Durable object: operation manifest. Authority:
  runtime and reviewer. Degraded: backend loss falls back to another registered
  backend or manual continuation. Gate: G6, G12. (per synthesis section 10; retains
  DIRECTOR-01.) Fixture: the same 15A synthetic operation run through a mock
  hosted backend and a mock local backend, asserting identical artifacts and
  journals, then disabling the active backend to assert fallback or manual
  continuation.

- [ ] **AGENT-03**: Evidence-based proposals name their observation window,
  denominator, included and missing signals, uncertainty, and competing
  explanations; sparse evidence cannot produce a mastery percentage or a confident
  causal claim, and accepted next actions remain recommendations until the learner
  or deterministic selection policy acts. Owner: agent client. Durable object:
  proposal record. Authority: the learner or selection policy acts, not the model.
  Degraded: sparse evidence yields an explicitly uncertain recommendation. Gate: G5,
  G7. (per synthesis sections 5, 10; retains DIRECTOR-04.) Fixture: a 15B
  proposal fixture over a sparse synthetic evidence set of two attempts on one
  objective, asserting the proposal names its window, denominator, and
  uncertainty and refuses a mastery percentage.

#### UPGRADE: legacy-artifact audit and upgrade

- [ ] **UPGRADE-01**: Legacy-artifact upgrades begin with a baseline audit (current
  parse, identity, fingerprint, objectives, sources, rights, media, assessment
  boundaries, plain rendering, rich rendering, validation) and present a bounded
  diff before editing; stable identity and source history are preserved and cosmetic
  novelty is rejected. Owner: legacy-upgrade skill. Durable object: audited artifact
  plus accepted revision. Authority: reviewer acceptance. Degraded: an artifact that
  cannot express an enhancement retains its form and links a derived enhancement
  with its portability cost. Gate: G6. (per synthesis section 10.) Fixture: a
  16C legacy-upgrade scenario over a synthetic pre-13.5 lesson artifact,
  asserting the baseline audit runs first and the enhancement lands as a bounded
  diff with identity and source history preserved.

- [ ] **UPGRADE-02**: Assessment-semantic changes (keyed content, difficulty,
  objective alignment) are separate reviewed revisions and are never silently
  changed by an upgrade. Owner: reviewer. Durable object: reviewed assessment
  revision. Authority: runtime and reviewer. Degraded: an upgrade touching keyed
  meaning halts for explicit assessment review. Gate: G6. (per synthesis section 10;
  CLAUDE.md audit-before-editing rule.) Fixture: a 16C scenario in which a
  scripted upgrade attempts to touch a synthetic item's keyed answer, asserting
  the upgrade halts for explicit assessment review.

#### MAINT: capability ownership, breadth, and diagnostics

- [ ] **MAINT-01**: Every capability has an owner, version, validator, fallback,
  dependency and license record, research refresh trigger, migration rule, fixtures,
  and retirement path; unsupported capabilities degrade visibly. Owner: named
  maintenance owner. Durable object: capability catalog entry. Authority: capability
  registry. Degraded: an unmaintained capability is marked degraded, not silently
  broken. Gate: G12. (per synthesis section 11.9.) Fixture: a 17B catalog
  fixture registering one synthetic capability with every required field, then
  marking it unmaintained to assert it degrades visibly rather than breaking
  silently.

- [ ] **MAINT-02**: Architecture breadth is preserved through the capability
  catalog: registered, prototype, and backburner capabilities name their shared
  primitive, dependency, cost, and revisit trigger and remain in traceability even
  when implementation is staged; hard rejections keep the full section 12.4 ledger
  row and cannot be silently reintroduced or deleted. Owner: maintenance owner.
  Durable object: disposition ledger. Authority: the append-only ledger. Degraded:
  an untimely capability stays a backburner entry rather than being dropped. Gate:
  G12. (per synthesis sections 12, 12.4, 12.5; breadth preservation.) Fixture: a
  17B ledger fixture containing a synthetic backburner entry and a synthetic
  hard-rejection row, asserting a scripted attempt to delete or silently
  reintroduce either is refused.

- [ ] **MAINT-03**: Diagnostics redact secrets, protected content, private paths in
  portable reports, and keys; evaluation of learning, authoring quality,
  time-to-course, search, and recovery uses local synthetic or consented fixtures,
  and page views, clicks, streaks, and time are never learning evidence. Owner:
  maintenance owner. Durable object: redacted diagnostics bundle. Authority: local
  policy. Degraded: a report that cannot be redacted is withheld rather than leaked.
  Gate: G11, G12. (per synthesis sections 11.1, 11.8; section 12.4 rejection of
  engagement-as-mastery.) Fixture: a 17B diagnostics run over a synthetic course
  seeded with fake secrets, protected text, and private paths, asserting the
  portable report redacts all three or is withheld.

- [ ] **MAINT-04**: Each capability's research refresh trigger is operable
  through a portable research-refresh playbook covering bounded research waves,
  evidence reconciliation, and disposition updates per
  `.planning/AGENT-WORKFLOW.md`; the playbook becomes an agent skill only once
  its procedure stabilizes, per the 999.5 rule that skills document shipped
  surfaces. Owner: maintenance owner. Durable object: research wave record plus
  disposition ledger update. Authority: PLANNING-DIRECTIVES and the append-only
  disposition ledger. Degraded: with no playbook run, existing dispositions stay
  valid and stale research is flagged by its refresh trigger, never silently
  trusted. Gate: G12. (added 2026-08-14; lands synthesis section 13
  RESEARCH-GATE and clause C220.) Fixture: a synthetic research-refresh drill
  re-checking one registered capability's evidence and recording a disposition
  update in the append-only ledger.

> **Family-alias note (2026-08-14, audit A1 clause C219).** Synthesis section 13
> names requirement families that landed under different IDs: BLUEPRINT lands in
> ACTIVITY-02, EVIDVIEW in GRAPH-03 and AGENT-03, UI and IA in the APP family,
> DIRECTOR in the AGENT and TREAT families, BASELINE in the synthesis 12.1 core
> rows, RESEARCH-GATE in MAINT-04, and VISION-GOV in PLANNING-DIRECTIVES
> section 9 (vision capture governance). No content is missing; the aliases map
> here so the traceability table stays readable against the landed families.

## v2 Requirements

### Retention

- **V2-RET-01**: Deeper Anki merge — whether itembank should own card scheduling as well as objective scheduling
- **V2-RET-02**: Hint support fading with demonstrated mastery (the expertise-reversal effect)

### Delivery

- **V2-DEL-01**: Signed binaries — exe, `.app`, AppImage — revisited when a second person runs the tool
- **V2-DEL-02**: Windows CPU and memory limits for `check` items via Job Objects through `ctypes`

### Interop

- **V2-INT-01**: QTI 3.0 export, once a real consumer exists
- **V2-INT-02**: MCP as transport over the JSON API, never as a second parser or scorer.
  **Expanded 2026-08-10** from `.planning/notes/2026-08-10-mcp-as-third-surface.md`,
  against MCP spec revision **2026-07-28**. Design promoted to `ROADMAP.md` Phase 999.3.
  Five conditions, binding on any plan that implements this:

  1. The tool table is a **projection of `surfaces/daemon.py:API_ROUTES`**, and each
     tool's `inputSchema` is the already-published `schemas/*.json` document read off
     disk. No embedded copy, no second contract.

  2. `SURFACE_PARITY` grows a third column (route, CLI command, MCP tool) rather than
     gaining a second parity map, so Extensibility Rule 7 covers it unchanged.

  3. Pre-response tools return `runtime.public_item()`. `explain_payload()` is
     reachable **only** after a recorded response for that item exists in the evidence
     store. The gate is the evidence log, not a request flag.

  4. A refusal is `isError: true` with explanatory text, which is the spec's own shape
     for a business-logic error. Tier state is read in the Python handler. **A tool
     description is not a gate** (Directive §4.1).

  5. stdio and an HTTP mount on the Phase 2 daemon are **both** built against one tool
     table, per Directive §3. One dispatcher, two byte-transports. This does not trip
     Directive §4.2.

- **V2-INT-03** *(new, 2026-08-10)*: WebMCP (`navigator.modelContext`) as a fourth mount
  of the V2-INT-02 tool table inside the Phase 13 shell. Blocked on stable browser
  support; W3C Draft Community Group Report 2026-02-12, Chrome 149 origin trial only.
  See `.planning/seeds/webmcp-tool-declaration.md`.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Hosted storage: accounts, gradebook, cloud sync, telemetry | No learner evidence or bank leaves the machine at rest. Hosted models are permitted; hosted storage is not. |
| A social layer: matchmaking, public profiles, leaderboards | Worth something at ten thousand students and zero at one. A business, not a feature. |
| Gamification: points, badges, levels, scores | A score is a thing you optimise instead of studying. A captive user of one gains nothing from retention mechanics. |
| Team or competitive scoring | Easy to copy accidentally alongside CTFd's verifier idea. Same reason as gamification. |
| A model that decides for itself how much to reveal | The model writes the hint; the runtime decides the tier. A chat box may be a surface, never the authority. |
| Auto-grading prose into mastery without a review state | Keyword matching cannot separate a correct explanation from a confident wrong one with the right nouns. |
| Per-learner ML personalisation or knowledge tracing | FSRS defaults are trained on ~700M reviews across ~10k users. Fitting a model to one learner's evidence produces confident noise. |
| Question generation as a runtime feature | The model writes questions, the tool validates them. The auditor drafts through the lint loop; the runtime never invents content. |
| A rewrite in a compiled language | Buys a static binary, costs the one verified scorer and five passing test files. Adaptability is bought at the JSON API seam instead. |
| Native mobile app, video hosting, content marketplace, push notifications | Product layers of hosted competitors, all irrelevant at one user. `--lan` already reaches a phone. |
| Question banks in this repository | Fixtures are synthetic; `guard` enforces it in CI; real banks live in private storage. |
| Mandarin TTS and `.apkg` packaging | Content-specific dependencies and network behaviour; stays a separate private pipeline. |

## Open Decisions

Resolved during roadmap or in the phase named, not deferred past it.

| Decision | Options | Resolve in |
|----------|---------|-----------|
| Item identity scheme | Opaque IDs with content-hash as a fingerprint, versus content-hash as the ID with a rekey/alias table | Evidence phase |
| Tier-gate enforcement mechanism | No prior art found; how the runtime detects and drops model output that reaches past the unlocked tier | Model adapter phase |
| Second quality gate algorithm | Distractor-overlap heuristic, near-duplicate detection thresholds | Auditor phase |
| Syllabus input formats | Markdown and text only, versus PDF and DOCX which stdlib cannot parse well | Auditor phase |
| Auditor reversibility mechanism | Shadow copy versus a git commit per write; depends on whether the private bank directory is git-tracked | Auditor phase |
| Windows append-write durability for the event log | Single-`write()` atomicity is POSIX-flavoured; needs a spike since this runs on Windows | Evidence phase |
| GitHub release-asset `digest` field format | Existence confirmed, literal shape unverified against a live response | Delivery phase |

## Traceability

Populated during roadmap creation. See `.planning/ROADMAP.md` for phase goals and success criteria.

| Requirement | Phase | Status |
|-------------|-------|--------|
| EVID-01 | Phase 1 | Complete |
| EVID-02 | Phase 1 | Complete |
| EVID-03 | Phase 1 | Complete |
| EVID-04 | Phase 1 | Complete |
| EVID-05 | Phase 1 | Complete |
| EVID-06 | Phase 1 | Complete |
| EVID-07 | Phase 1 | Complete |
| EVID-08 | Phase 1 | Complete |
| PROTO-01 | Phase 1 | Complete |
| PROTO-02 | Phase 1 | Complete |
| PROTO-03 | Phase 1 | Complete |
| PROTO-04 | Phase 1 | Complete |
| PROTO-05 | Phase 1 | Complete |
| LESSON-01 | Phase 3 | Complete |
| LESSON-02 | Phase 3 | Pending |
| LESSON-03 | Phase 3 | Pending |
| LESSON-04 | Phase 3 | Complete |
| LESSON-05 | Phase 3 | Pending |
| LESSON-06 | Phase 3 | Complete |
| LESSON-07 | Phase 3.1 | Pending |
| LESSON-08 | Phase 3.1 | Pending |
| LESSON-09 | Phase 3.1 | Pending |
| LESSON-10 | Phase 3.1 | Pending |
| LESSON-11 | Phase 3.1 | Pending |
| LESSON-12 | Phase 3.1 | Pending |
| LESSON-13 | Phase 3.1 | Complete |
| LESSON-14 | Phase 3.1 | Complete |
| LESSON-15 | Phase 3.1 | Pending |
| LESSON-16 | Phase 3.1 | Pending |
| LESSON-17 | Phase 3.1 | Pending |
| SEED-01 | Phase 3.2 | Pending |
| SEED-02 | Phase 3.2 | Pending |
| SEED-03 | Phase 3.2 | Pending |
| SEED-04 | Phase 3.2 | Pending |
| SEED-05 | Phase 3.2 | Pending |
| SEED-06 | Phase 3.2 | Pending |
| SEED-07 | Phase 3.2 | Pending |
| SEED-08 | Phase 3.2 | Pending |
| SEED-09 | Phase 3.2 | Pending |
| TEACH-01 | Phase 6 | Complete |
| TEACH-02 | Phase 6 | Complete |
| TEACH-03 | Phase 6 | Complete |
| TEACH-04 | Phase 8 | Pending |
| TEACH-05 | Phase 8 | Pending |
| TEACH-06 | Phase 8 | Pending |
| TEACH-07 | Phase 8 | Pending |
| TEACH-08 | Phase 8 | Pending |
| TEACH-09 | Phase 8 | Pending |
| MODE-01 | Phase 6 | Complete |
| MODE-02 | Phase 6 | Complete |
| MODE-03 | Phase 6 | Complete |
| MODE-04 | Phase 6 | Complete |
| MODE-05 | Phase 6 | Complete |
| MODE-06 | Phase 6 | Complete |
| SEL-01 | Phase 7 | Complete |
| SEL-02 | Phase 7 | Complete |
| SEL-03 | Phase 7 | Complete |
| SEL-04 | Phase 7 | Complete |
| SEL-05 | Phase 7 | Complete |
| SCHED-01 | Phase 10 | Pending |
| SCHED-02 | Phase 10 | Pending |
| SCHED-03 | Phase 10 | Pending |
| SCHED-04 | Phase 10 | Pending |
| TREND-01 | Phase 10 | Pending |
| TREND-02 | Phase 10 | Pending |
| TREND-03 | Phase 10 | Pending |
| TREND-04 | Phase 10 | Pending |
| TREND-05 | Phase 10 | Pending |
| CODE-01 | Phase 5 | Pending |
| CODE-02 | Phase 5 | Pending |
| CODE-03 | Phase 5 | Pending |
| CODE-04 | Phase 5 | Pending |
| CODE-05 | Phase 5 | Pending |
| VIS-01 | Phase 06.1 | Pending |
| VIS-02 | Phase 06.1 | Pending |
| VIS-03 | Phase 06.1 | Pending |
| VIS-04 | Phase 06.1 | Pending |
| VIS-05 | Phase 06.1 | Pending |
| VIS-06 | Phase 06.1 | Pending |
| VIS-07 | Phase 06.1 | Pending |
| VIS-08 | Phase 06.1 | Pending |
| VIS-09 | Phase 06.1 | Pending |
| GATE-01 | Phase 6.2 | Delivered |
| GATE-02 | Phase 6.2 | Delivered |
| GATE-03 | Phase 6.2 | Delivered |
| GATE-04 | Phase 6.2 | Delivered |
| GATE-05 | Phase 6.2 | Delivered |
| GATE-06 | Phase 6.2 | Delivered |
| LOOP-01 | Phase 9 | Pending |
| LOOP-02 | Phase 9 | Pending |
| LOOP-03 | Phase 9 | Pending |
| LOOP-04 | Phase 9 | Pending |
| LOOP-05 | Phase 9 | Pending |
| AUDIT-01 | Phase 11 | Pending |
| AUDIT-02 | Phase 11 | Pending |
| AUDIT-03 | Phase 11 | Pending |
| AUDIT-04 | Phase 11 | Pending |
| AUDIT-05 | Phase 11 | Pending |
| AUDIT-06 | Phase 11 | Pending |
| AUDIT-07 | Phase 11 | Pending |
| AUDIT-08 | Phase 11 | Pending |
| AUDIT-09 | Phase 11 | Pending |
| AUTH-01 | Phase 11 | Pending |
| AUTH-02 | Phase 11 | Pending |
| AUTH-03 | Phase 11 | Pending |
| SURF-01 | Phase 2 | Complete |
| SURF-02 | Phase 4 | Pending |
| SURF-03 | Phase 2 | Complete |
| SURF-04 | Phase 2 | Complete |
| SURF-05 | Phase 4 | Pending |
| SURF-06 | Phase 4 | Complete |
| SURF-07 | Phase 4 | Complete |
| SURF-08 | Phase 4 | Complete |
| SURF-09 | Phase 4 | Complete |
| MODEL-01 | Phase 8 | Pending |
| MODEL-02 | Phase 8 | Pending |
| MODEL-03 | Phase 8 | Pending |
| MODEL-04 | Phase 8 | Pending |
| MODEL-05 | Phase 8 | Pending |
| DEL-01 | Phase 12 | Complete |
| DEL-02 | Phase 12 | Complete |
| DEL-03 | Phase 12 | Complete |
| DEL-04 | Phase 2 | Complete |
| DEL-05 | Phase 2 | Complete |
| DEL-06 | Phase 12 | Complete |
| DEL-07 | Phase 12 | Complete |
| DEL-08 | Phase 12 | Complete |
| DEL-09 | Phase 13 | Complete |
| DEL-10 | Phase 13 | Complete |
| DEL-11 | Phase 13 | Complete |
| DEL-12 | Phase 13 | Complete |
| DEL-13 | Phase 13 | Complete |
| AUDIO-01 | Phase 9.1 | Complete |
| AUDIO-02 | Phase 9.1 | Complete |
| AUDIO-03 | Phase 9.1 | Complete |
| AUDIO-04 | Phase 9.1 | Complete |
| AUDIO-05 | Phase 9.1 | Complete |
| AUDIO-06 | Phase 9.1 | Complete |
| AUDIO-07 | Phase 9.1 | Complete |
| LTI-01 | Phase 999.4 | Pending |
| LTI-02 | Phase 999.4 | Pending |
| LTI-03 | Phase 999.4 | Pending |
| LTI-04 | Phase 999.4 | Pending |
| LTI-05 | Phase 999.4 | Pending |
| LTI-06 | Phase 999.4 | Pending |
| LTI-07 | Phase 999.4 | Pending |
| RTS-01 | Phase 13.5 | Pending |
| RTS-02 | Phase 13.5 | Complete |
| RTS-03 | Phase 13.5 | Complete |
| RTS-04 | Phase 13.5 | Pending |
| RTS-05 | Phase 13.5 | Complete |
| RTS-06 | Phase 13.5 | Complete |
| RTS-07 | Phase 13.5 | Pending |
| RTS-08 | Phase 13.5 | Pending |
| RTS-09 | Phase 13.5 | Pending |
| RTS-10 | Phase 13.5 | Pending |
| RTS-11 | Phase 13.5 | Complete |
| RTS-12 | Phase 13.5 | Pending |
| COURSE-01 | Phase 14 | Superseded 2026-08-13 -> GRAPH-01, GRAPH-03, FILE-01, ID-01, APP-01 |
| COURSE-02 | Phase 14 | Superseded 2026-08-13 -> FILE-02, RIGHTS-01 |
| COURSE-03 | Phase 14 | Superseded 2026-08-13 -> TREAT-02, ID-02 |
| COURSE-04 | Phase 14 | Superseded 2026-08-13 -> TREAT-01 |
| DIRECTOR-01 | Phase 15 | Superseded 2026-08-13 -> AGENT-02 |
| DIRECTOR-02 | Phase 15 | Superseded 2026-08-13 -> AGENT-01 |
| DIRECTOR-03 | Phase 15 | Superseded 2026-08-13 -> ACTIVITY-02 |
| DIRECTOR-04 | Phase 15 | Superseded 2026-08-13 -> AGENT-03, GRAPH-03 |
| LEARNUI-01 | Phase 16 | Superseded 2026-08-13 -> APP-01 |
| LEARNUI-02 | Phase 16 | Superseded 2026-08-13 -> CAP-01, FLOW-02 |
| LEARNUI-03 | Phase 16 | Superseded 2026-08-13 -> CAP-01, CAP-02 |
| LEARNUI-04 | Phase 16 | Superseded 2026-08-13 -> FLOW-01, A11Y-01, VISUAL-01 |
| GRAPH-01 | Phase 14B | Complete |
| GRAPH-02 | Phase 14B | Complete |
| GRAPH-03 | Phase 16C | Pending |
| GRAPH-04 | Phase 14B | Complete |
| FILE-01 | Phase 14A | Complete; advanced 2026-08-28 by Phase 14C, which made ten media addressable objects through one import boundary |
| FILE-02 | Phase 14A | Complete |
| FILE-03 | Phase 14A | Complete; advanced 2026-08-28 by Phase 14C, whose two-file source pair is proven atomic by three injected faults (check_two_file_pair_atomicity) |
| FILE-04 | Unscheduled (phase chosen after the 14B freeze) | Pending |
| ID-01 | Phase 14A | Complete |
| ID-02 | Phase 14A | Complete |
| TREAT-01 | Phase 15A | Pending |
| TREAT-02 | Phase 15A | Pending; advanced 2026-08-28 by Phase 14C, which gives every medium a place-level locator (page, part, slide, CSS and quote anchor, millisecond, spine fragment) |
| FLOW-01 | Phase 16B | Pending |
| FLOW-02 | Phase 16B | Pending |
| CAP-01 | Phase 16A | Pending |
| CAP-02 | Phase 16A | Pending |
| CAP-03 | Phase 16A | Pending |
| ACTIVITY-01 | Phase 16A | Pending |
| ACTIVITY-02 | Phase 15B | Pending |
| ACTIVITY-03 | Phase 16A | Pending |
| NOTE-01 | Phase 16C | Pending |
| NOTE-02 | Phase 16C | Pending |
| NOTE-03 | Phase 16C | Pending |
| STRATEGY-01 | Phase 16C | Pending |
| STRATEGY-02 | Phase 16C | Pending |
| RIGHTS-01 | Phase 14A | Complete; advanced 2026-08-28 by Phase 14C, where a remote capture mints all seven rights unknown and deriving from it refuses by name |
| RIGHTS-02 | Phase 15A | Pending |
| A11Y-01 | Phase 17A | Pending |
| A11Y-02 | Phase 16A | Pending |
| PORT-01 | Phase 16A | Pending |
| PORT-02 | Phase 17B | Pending, unchanged. Phase 14C added the EPUB import direction to a prototype-level interchange adapter and carries its semantic loss report in the sidecar; the requirement is not completed by that |
| PORT-03 | Phase 14B | Complete |
| RELIABILITY-01 | Phase 14A | Complete |
| RELIABILITY-02 | Phase 15A | Pending |
| RELIABILITY-03 | Phase 15B | Pending |
| APP-01 | Phase 16B | Pending |
| APP-02 | Phase 16B | Pending |
| APP-03 | Phase 16B | Pending |
| VISUAL-01 | Phase 17A | Pending |
| VISUAL-02 | Phase 17A | Pending |
| AGENT-01 | Phase 15A | Pending |
| AGENT-02 | Phase 15A | Pending |
| AGENT-03 | Phase 15B | Pending |
| UPGRADE-01 | Phase 16C | Pending |
| UPGRADE-02 | Phase 16C | Pending |
| MAINT-01 | Phase 17B | Pending |
| MAINT-02 | Phase 17B | Pending |
| MAINT-03 | Phase 17B | Pending |

**Coverage:**

- v1 + next-milestone requirements: 217 total
- Mapped to phases: 217
- Unmapped: 0 ✓

> **Count corrected 2026-08-13.** Both sides of the source-to-course merge
> carried "127 total", a figure that stopped being true several phases before
> either branch existed. Counted at merge time: 170 checklist ids (105 open, 65
> closed) and 170 rows in the table above, so the mapping is still complete. The
> number was recounted rather than carried forward.

> **Recount after the family expansion 2026-08-13.** The eighteen expanded
> source-to-course families add 47 new requirement ids (GRAPH, FILE, ID, TREAT,
> FLOW, CAP, ACTIVITY, NOTE, STRATEGY, RIGHTS, A11Y, PORT, RELIABILITY, APP,
> VISUAL, AGENT, UPGRADE, MAINT). The twelve superseded ids (COURSE-01..04,
> DIRECTOR-01..04, LEARNUI-01..04) are retained, not deleted, so the id total
> rises from 170 to 217 with a matching 217 table rows. Superseded ids keep their
> phase mapping and point forward to their replacements; every new id is mapped to
> a section 15 subphase, so the mapping stays complete.

---
*Requirements defined: 2026-08-05*
*Roadmap created: 2026-08-05*
