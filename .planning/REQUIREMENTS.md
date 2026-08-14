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
- [ ] **RTS-02**: The first line of an item stem is fully visible on first paint at 1280/768/375/320px and at 200% zoom, scripting on and off, and every in-page anchor jump lands clear of the sticky band; the band never exceeds two rows and a card already fully in view is not scrolled
- [x] **RTS-03**: The reader and the sat quiz render in the same vendored voices on one type scale — five sizes, two weights, no literal family, no colour literal — and every daemon-served page declares all four `@font-face` rules with root-absolute urls that return 200
- [ ] **RTS-04**: The reader's vertical rhythm and reading measure are set against the shipped faces as they actually render: 24px paragraph rhythm against a 29.7px line box, 66 real characters per line, x-height-matched inline runs, and a step down to an existing token below 480px
- [x] **RTS-05**: The glossary gloss lands at its term, flips at the viewport edges, becomes a bottom sheet on a narrow coarse pointer, opens on hover intent that never moves focus and never steals a pinned panel, links onward to the `[!KEY]` card and the full entry, and returns the learner to the text — with the click and keyboard path complete without script
- [ ] **RTS-06**: `reader_nav` ships `none | column | rail | auto` with `auto` default: a lesson of four or more sections offers a nav, a shorter one does not, the rail occupies otherwise-empty margin at 1280px and wider without changing the reading measure, and the print rule stays inside the print block
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

### Course workspace

- [ ] **COURSE-01**: A course is a first-class, readable artifact that names its
  target, learner, approved source and write roots, objective hierarchy,
  prerequisites, treatments, accepted artifacts, drafts, and evidence location;
  any machine index is derived and disposable.

- [ ] **COURSE-02**: Discovery is read-only and root-bounded; scaffolding and
  binding are explicit, idempotent operations, and finding a file never grants
  permission to transmit or modify it.

- [ ] **COURSE-03**: Every objective-to-source and coverage claim carries a stable
  locator, confidence, and state (`covered`, `thin`, `missing`, `conflicting`, or
  `unknown`); heading similarity alone cannot produce `covered`.

- [ ] **COURSE-04**: Every objective has an explicit, reviewable treatment plan
  drawn from direct reading, excerpt, guided lesson, notes/terms, worked example,
  visual/demonstration, practice, test, assessment-first, or human review; direct
  reading is a complete result and generation is never the automatic default.

### AI course director and quality

- [ ] **DIRECTOR-01**: Hosted coding-agent clients and registered local backends
  reach the same course operations and schemas; backend choice changes capability,
  latency, and privacy disclosure, not the course artifact contract.

- [ ] **DIRECTOR-02**: AI autonomy is scoped per operation as recommend-only,
  draft-and-review, or approved bounded writes; proposals cite sources, label
  synthesis, show quality findings, and are inspectable and recoverable.

- [ ] **DIRECTOR-03**: Standardized-test courses require a cited, versioned
  blueprint mapping domains, weights, cognitive demand, item conventions,
  difficulty, timing, permitted tools, and feedback mode; knowledge courses use
  their actual syllabus and expected demand. The UI never claims exam fidelity
  without this mapping.

- [ ] **DIRECTOR-04**: Evidence-based proposals name their observation window,
  denominator, included and missing signals, uncertainty, and competing
  explanations. Sparse evidence cannot produce a mastery percentage or a confident
  causal claim. Accepted next actions remain recommendations until the learner or
  deterministic selection policy acts.

### Comprehensive learner UI

- [ ] **LEARNUI-01**: The home surface is a course shelf and each course provides
  coherent Learn, Practice, Test, Sources, Course map, and Build/review areas; banks
  are assessment artifacts inside courses rather than the primary navigation unit.

- [ ] **LEARNUI-02**: One parsed lesson supports continuous reader and guided modes;
  neither mode creates a second parser or scorer, and a learner can move between
  direct source reading, lesson, practice, feedback, and the next course action
  without reconstructing context.

- [ ] **LEARNUI-03**: Lessons render semantic teaching roles—hover/focus
  definitions, things-to-know blocks, expert or niche tips, warnings, worked
  examples, citations, diagrams, math, runnable code, inline checks, hints, and
  accessible visual interactions—with graceful unavailable states and no
  decorative block required by style alone.

- [ ] **LEARNUI-04**: The reference course tracer demonstrates orient → predict or
  act → observe → explain → changed-context transfer → evidence → next action at
  desktop and phone widths, including keyboard/screen-reader equivalence, model-
  unavailable operation, and no early keyed-content leak.

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
| RTS-02 | Phase 13.5 | Pending |
| RTS-03 | Phase 13.5 | Complete |
| RTS-04 | Phase 13.5 | Pending |
| RTS-05 | Phase 13.5 | Complete |
| RTS-06 | Phase 13.5 | Pending |
| RTS-07 | Phase 13.5 | Pending |
| RTS-08 | Phase 13.5 | Pending |
| RTS-09 | Phase 13.5 | Pending |
| RTS-10 | Phase 13.5 | Pending |
| RTS-11 | Phase 13.5 | Complete |
| RTS-12 | Phase 13.5 | Pending |
| COURSE-01 | Phase 14 | Pending |
| COURSE-02 | Phase 14 | Pending |
| COURSE-03 | Phase 14 | Pending |
| COURSE-04 | Phase 14 | Pending |
| DIRECTOR-01 | Phase 15 | Pending |
| DIRECTOR-02 | Phase 15 | Pending |
| DIRECTOR-03 | Phase 15 | Pending |
| DIRECTOR-04 | Phase 15 | Pending |
| LEARNUI-01 | Phase 16 | Pending |
| LEARNUI-02 | Phase 16 | Pending |
| LEARNUI-03 | Phase 16 | Pending |
| LEARNUI-04 | Phase 16 | Pending |

**Coverage:**

- v1 + next-milestone requirements: 170 total
- Mapped to phases: 170
- Unmapped: 0 ✓

> **Count corrected 2026-08-13.** Both sides of the source-to-course merge
> carried "127 total", a figure that stopped being true several phases before
> either branch existed. Counted at merge time: 170 checklist ids (105 open, 65
> closed) and 170 rows in the table above, so the mapping is still complete. The
> number was recounted rather than carried forward.

---
*Requirements defined: 2026-08-05*
*Roadmap created: 2026-08-05*
