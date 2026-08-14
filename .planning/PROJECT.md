# itembank — source-to-course learning workspace

## What This Is

> **Next-milestone reframe (2026-08-13):**
> `.planning/SOURCE-TO-COURSE.md` is binding. The primary user-facing object is
> a course, objectives are its spine, and books, syllabi, notes, blueprints,
> lessons, and banks are connected inputs and artifacts.

`itembank` is a source-to-course workspace built on a local-first assessment
protocol and runtime for human and AI collaborators.
Today it tests: a markdown format contract with an actionable linter, six item types,
deterministic scoring behind one scorer, resumable JSON sessions, an offline HTML quiz,
a graded loopback sitting, Anki TSV export, and a cross-subject `day` cockpit.

The next milestone makes it a **comprehensive AI-assisted course builder and
learning environment**. It discovers learner-approved sources, builds a cited
objective and prerequisite map, chooses an appropriate treatment per objective,
creates missing course artifacts under reviewable autonomy, provides rich
learning and assessment UI, and closes the loop using evidence. A capable model
is a course builder, analyst, and optional teacher; it is not the deterministic
scorer.

It is for one learner — Weibao — across EMT, Math 1400, and CSCI 1100, with AI tutors
as first-class clients of the same runtime a human uses.

## Product North Star

**Learner-owned sources become an inspectable, high-quality, AI-operable course
whose readings, lessons, practice, tests, and next actions are aligned to cited
objectives and improved by honest evidence.**

## Runtime invariant

**One runtime, one scorer, one evidence store. The runtime owns correctness,
session state, evidence, and keyed assessment disclosure; AI may build and
teach the course around that boundary.**

The tutoring model is smart and well-informed: it reads the item, the key, the
rationale, and the learner's specific wrong answer, so it can teach about *this*
error rather than about the item in general. What it is not allowed to do is choose
how much to say. The runtime gates that by session mode and by hint tier, so a model
argued into wanting to reveal still cannot, because the reveal is the runtime's call
and not the model's.

This is a narrow safety and consistency boundary rather than the product thesis.
AI may search approved roots, design curricula, select readings, draft and revise
artifacts, interpret metrics, propose remediation, and perform approved bounded
writes. It cites sources, labels synthesis, reports uncertainty and denominators,
and leaves acceptance and reversal visible. If a feature requires a second
scorer, parser, or evidence store, the feature is wrong.

## Requirements

### Validated

<!-- Shipped and confirmed working. Inferred from the codebase map and git history. -->

- ✓ Machine-readable format contract (`spec`) and actionable lint errors by item number — existing
- ✓ Six item types: `mc`, `multi`, `table`, `build`, `dnd`, `short` — existing
- ✓ Dichotomous scoring on every type, matching the NREMT no-partial-credit rule — existing
- ✓ Offline HTML quiz (`build`) and graded loopback sitting (`serve`) with incremental attempt writes — existing
- ✓ Deterministic JSON sessions: `start`, `next`, `submit`, `report` — existing
- ✓ Answer-key withholding via `public_item()` / `explain_payload()` — existing
- ✓ One scorer: every surface reaches a verdict through `runtime.score_response()` (closes #2) — commit `e25fbdf`
- ✓ Four-layer split: `model` / `runtime` / `server` / `surfaces` with no behaviour change (closes #3) — commit `deb754e`
- ✓ Wiring path resolution walks to the repo root, expands `~`, accepts absolute paths (closes #16) — commit `58d4eb9`
- ✓ One shared `THEME_CSS` palette across quiz and study (closes #17 part 1) — commit `58d4eb9`
- ✓ Per-option rationale renders inside the option it describes — commit `4be75b3`
- ✓ Flashcard and Learn surface (`study`); Basic and Cloze Anki TSV export (`export`) — existing
- ✓ Daily cross-subject surface (`day`): dated-plan parsing, floor rule, streak log, lane fuses and load — existing
- ✓ Repository guard against real question-bank content (`guard`) — existing
- ✓ Synthetic fixture tests for server, agent, study, export, and `day` paths — existing
- ✓ Stable opaque `[ID:]` item IDs plus `[HASH:]` content fingerprint, immutable after first `id-assign`, replacing positional `Qn` (#4) — Phase 01 (01-04)
- ✓ One evidence store (`evidence.py` append-only JSONL log) replacing three (`_attempts/*.md`, session JSON, `daily_log.md`) — Phase 01 (01-01 through 01-11)
- ✓ Explicit schema versions for items, sessions, responses, and reports (`schemas/*.json`, `SESSION_UPGRADES`) — Phase 01 (01-05)
- ✓ Machine-readable lint errors with declared, sorted `LINT_CODES` — Phase 01 (01-03)
- ✓ Defined resume and idempotency behaviour for repeated `submit`/`mark` calls (`dedupe_key`, `idempotency_canon`, D-12) — Phase 01 (01-02, 01-07)
- ✓ Public JSON schema / contract fixture for the agent interface: `itembank schema --all`, `schemas/*.json`, `schema_validate.py` in CI — Phase 01 (01-06)

### Active

<!-- This milestone. All 13 unbuilt GitHub issues plus three new capability areas. -->

**The teaching loop**

- [ ] `LESSON` sections in the bank format plus per-item `LESSON-REF`, optional and non-breaking (#5)
- [ ] Deterministic hint ladder over authored distractor analysis: tier 0 lesson pointer, 1 objective, 2 trap, 3 `da[picked letter]`, 4 discriminator, 5 reveal (#1)
- [ ] `submit` holds the cursor on a wrong answer instead of auto-advancing; new `hint` command; `hints_used` per response (#1)
- [ ] `report` distinguishes "right at tier 1" from "right at tier 4" (#1)
- [ ] Rubric checklist beside a submitted `short` answer, producing structured evidence per rubric point (#8)
- [ ] `check` item type: verified by running the learner's own code and comparing output, with a monospace editor — tab handling, line numbers, no proportional font (#13)
- [ ] One subject-invariant loop with three varying parts — lesson medium, allowed item types, verifier — rendering EMT prose, Math with rendered LaTeX, and CS with runnable code (#18)

**Retention and pacing**

- [ ] itembank schedules what is due today per objective from its own evidence (#18)
- [ ] Daily cap enforced through `day`, so a course cannot be binged and forgotten (#18)
- [ ] Anki keeps owning card reviews; itembank owns objective-level scheduling only

**The auditor** *(new — not previously filed)*

- [ ] Ingest a syllabus or standards document and extract its objectives, including subtleties, not just headings
- [ ] Map extracted objectives against bank coverage and report what has no items
- [ ] Point at existing materials that cover a gap, and absorb them into the bank once obtained
- [ ] Autonomy range from report-only through draft-and-approve to full audit-draft-lint-fix-commit, set by configuration
- [ ] Every generated item passes `lint` before reaching a bank; every write is reversible

**Trends as a control loop** *(new — not previously filed)*

- [ ] Weak objectives raise their selection weight; mastered ones drop out
- [ ] Evidence-backed `load` extends `day`'s existing number, saying when the plan needs re-cutting
- [ ] Longitudinal `/report` view: accuracy by objective over weeks, hint tier reached, items pending manual marking
- [ ] Decay flagging: an objective correct a month ago and untouched since surfaces as at-risk
- [ ] Evidence records more than currently needed — response time, confidence, error category, review state — because an uncaptured field cannot be backfilled

**Selection**

- [ ] Selection modes: diagnostic, practice, remediation, exam (root ROADMAP §2)
- [ ] Recent-exposure tracking to avoid accidental repeats (root ROADMAP §2)
- [ ] Selection by objective, prerequisite, item type, and difficulty; first selector rule-based and inspectable (root ROADMAP §2)
- [ ] Discrimination-pair support for common confusions (root ROADMAP §2)

**Surfaces and delivery**

- [ ] One daemon with routes replacing a server per subcommand: `/`, `/quiz/<bank>`, `/study/<bank>`, `/report`, `/api/*` (#7)
- [ ] Question-surface UI: collapse five chrome bands to one sticky line, real typographic hierarchy, and the rest of the six fixes (#6)
- [ ] `study` stops discarding `opts`, `da`, `second`, and `notes` (#17 part 2)
- [ ] Theming: accent set from an OS colour picker with light/dark pairs computed, contrast-checked and deuteranopia-safe correct/incorrect, saved to `theme.json` (#9)
- [ ] `day` fork 1: full in-page markdown editing with an optimistic-concurrency guard, expanded rather than narrowed (#15, decided against the issue's proposal)

**Agent and interop**

- [ ] Closed authoring loop: spec, draft, lint, feed errors back, repeat to clean or retry cap, write the bank — no human relaying errors (#11)
- [ ] Model adapter as an interface, not a vendor: works with Claude Code, Codex, or a competitor today, and an open local model such as Qwen when the hardware exists (#14)
- [ ] `short` rubric marking through that adapter, with the model a client of `next`/`submit`/`hint` and never a scorer (#14)
- [ ] The tutoring model reads the key, rationale, and the learner's specific wrong answer, and writes a hint about *that* error
- [ ] The runtime, not the model, decides which tier the model may speak at; the model cannot reach past the tier the session has unlocked
- [ ] Model-generated hints are checked against the tier gate before rendering, and a hint that leaks the key is dropped rather than shown
- [ ] Local model is a first-class backend, prepared in advance rather than retrofitted: the adapter is written against an OpenAI-compatible shape so a hosted CLI and a local server are the same code path
- [ ] Every model interaction is logged to the evidence store, so a hint you were given is recoverable later

**Feedback policy per session mode** *(new — resolves the Albert question)*

- [ ] Feedback policy is a property of the session mode, not a global setting
- [ ] Drill mode: correct answer and explanation immediately on a wrong answer, then next item (Albert's behaviour)
- [ ] Practice mode: hint ladder, cursor held for a second attempt, reveal at tier 5
- [ ] Diagnostic mode: no feedback until the sitting ends, because a hint contaminates the measurement
- [ ] Exam mode: no feedback at all until the attempt file is marked
- [ ] Mode is chosen per sitting and recorded in the evidence, so a "correct" from drill mode is distinguishable from a "correct" from exam mode
- [ ] Agent usage contract covering permissions, answer leakage, retries, manual grading, and what an agent may not infer (root ROADMAP §4)
- [ ] GIFT export as the cheapest proof of the interoperability claim (#12)

**Packaging, settings, and updates** *(new — supersedes #10 in part)*

- [ ] Single double-clickable artifact per OS via stdlib `python -m zipapp`: `.pyz` plus a one-line launcher for Windows, macOS, and Linux
- [ ] `--app=http://127.0.0.1:PORT` frameless window so the daemon opens as an app, not a browser tab
- [ ] One documented config file (`itembank.json`, beside `lanes.md`) holding theme, daily cap, selection weights, auditor autonomy level, model adapter choice, and update policy
- [ ] `itembank config` prints the settings schema the way `spec` prints the format contract, so an agent can discover what it may change; `lint` rejects an invalid value
- [ ] Self-update against GitHub Releases with checksum verification and atomic replacement, no dependency
- [ ] Update behaviour toggleable between opt-in-only and check-on-launch, and silent-failing when offline
- [ ] **Every capability reachable from both the app and the CLI** — settings, updates, reports, and the auditor each have a route and a command, over one runtime

### Out of Scope

- **Hosted storage: accounts, a gradebook, cloud sync, hosted analytics** — no learner evidence and no bank leaves the machine at rest. This still holds. Hosted *models* are now permitted (see Constraints); hosted *storage* is not.
- **A social layer: matchmaking, public profiles, leaderboards** — worth something at ten thousand students and exactly zero at one. It is a business, not a feature.
- **Gamification: points, badges, levels, scores** — a streak plus a git evidence dot is a signal; a score is a thing you optimise instead of studying. Retention mechanics buy nothing from a captive user of one.
- **Auto-grading prose into mastery without a review state** — keyword matching cannot separate a correct explanation from a confident wrong one containing the right nouns. A grader that cannot tell those apart certifies the wrong answer.
- **A model that decides for itself how much to reveal** — the model writes the hint; the runtime decides which tier it may speak at and drops anything that reaches past it. A chat box may exist as *a* surface, never as the authority on what the learner sees.
- **Full spaced-repetition ownership: intervals, ease, a card queue** — deferred, not rejected. Anki owns card reviews this milestone; itembank owns objective-level scheduling. Merging them deeper is a v2 question.
- **A compiled binary: signed exe, `.app` bundle, AppImage** — deferred to v2, not rejected. It solves "Python is not installed", which is not a problem on either machine, and costs a release pipeline, a signing certificate, and a near-certain Defender false positive on a machine where that already bit this project. The zipapp gives the double-click on all three platforms for an afternoon instead. Revisit when a second person runs it, which is when "install Python first" becomes a real barrier (#10, partly superseded).
- **A rewrite in Go, Rust, or any compiled language** — it would buy a static binary and cost the one verified scorer, the format contract, and five passing test files. Cross-language adaptability is bought at the JSON API seam (#7) instead, where any future native shell, TUI, or phone surface is a client rather than a reimplementation.
- **Auto-updates that cannot be turned off** — update policy is a setting, and offline must degrade silently rather than block the page.
- **QTI 3.0 export** — an order of magnitude more cost than GIFT for the same job, and nothing in the current path reads it. Revisit when a real consumer exists (#12).
- **Mandarin TTS and `.apkg` packaging** — content-specific dependencies and network behaviour; stays a separate private pipeline.
- **Question banks in this repository** — fixtures are synthetic, `guard` enforces it in CI, real banks live in private storage.
- **Any dependency outside the Python standard library** — with one named exception under review: vendored KaTeX as a file asset for Math rendering. Goal 5 forbids services and network, not files.

## Context

**Why the project exists at all.** An AI was asked to write a 21-item question bank.
It invented its own format, wrote four turns of content in it, and nothing noticed —
in a repository that already held three renderers and a documented format. That is a
missing feedback signal, not a discipline problem. The useful artifact is the
**contract**, not the renderer: `spec` hands an authoring agent the format, `lint`
tells it exactly what it got wrong by item number.

**Why this milestone exists.** The tool tests and does not teach. Read honestly on
2026-08-05: nothing renders a lesson; `study_item` keeps `stem`, `answer`, `why`,
`disc`, and `trap` and drops `opts`, `da`, `second`, and `notes`, discarding exactly
the per-option rationale the quiz surface had just learned to use; Learn neither
persists nor schedules, resetting on reload. Weibao's question was "why cant itembank
be something like this?" pointing at StudyBro, then "Like a local version of this, to
walk through things and more?"

**The architectural advantage worth spending on.** StudyBro's tutor is a system prompt
over a chat box, and a prompt-based tutor caves. A tutor over this runtime structurally
cannot leak the key, because `next` withholds it. That advantage has been sitting
unused behind a deferred agent-adapter decision.

**The material is already authored.** `da` is a per-option dict and `lint` already
warns when a distractor never says when that option would be correct. Measured against
a live EMT bank: 25 of 45 wrong options lack the "would be correct when" clause, and
**zero lack a line entirely**. So hint tier 3 always fires and teaches on roughly 20 of
45. Authoring is a gap, not a blocker.

**Prior art to study rather than guess at** (Weibao, this session: "dont forget to take
a look at and get inspired from stuff already out there and more"):

| Source | What to take |
|---|---|
| Execute Program | Prose interleaved with checked problems, rising complexity, spaced review over the top, a daily cap. One loop across four languages, not four surfaces. |
| Runestone | Runnable code inside the prose — the natural home of the `check` type. CSCI 1100's own book runs on it. |
| PrairieLearn | Question-plus-content structure, arrived at independently by `CSCI_1100/Blocks/`. |
| pwn.college, CTFd | A machine-checkable verifier as the spine of a learning platform. |
| Anki's reviewer | What it refuses to do: no animation, no chrome, keyboard-only, one card. |
| StudyBro | The Socratic walkthrough, and nothing else — the social layer, accounts, and gamification are its business model, not its pedagogy. |
| Moodle GIFT | A plain-text interchange format every LMS-adjacent tool imports. |

The research phase surveys these and looks wider — the instruction is explicitly to get
inspired by what already exists rather than reinvent it.

**Current state.** Four layers, stdlib only, no install step, 18 GitHub issues filed on
`onionviolet/itembank`. Five are effectively shipped (#2, #3, #16, half of #17) and
still open; they need closing. The codebase map lives in `.planning/codebase/`, refreshed
2026-08-05. The root `ROADMAP.md` is the protocol-hardening plan and is an input to this
one, not a replacement for it.

**Known technical debt.** The `day` page is a third palette written in literal hex with
no variables, left untouched when #17's first half landed. `serve` and `day` each stand
up their own server on their own port, so two surfaces can hold different state for the
same day.

## Constraints

- **Tech stack**: Python standard library only, no install step — the founding design constraint. Two named exceptions: a vendored KaTeX asset for Math rendering (goal 5 forbids services and network, not files), and stdlib `urllib` for the opt-in updater.
- **Network**: hosted models are permitted, so the tool is no longer offline-only. But the core loop must **degrade, never block**: sitting a quiz, scoring, lessons, the authored hint ladder, evidence, and reports all work with the network unplugged. The model layer goes quiet when unreachable, the same way `day` omits Anki counts when Anki is closed. Being out of credits must never stop you studying.
- **Data residency**: evidence and banks stay on disk. No cloud sync, no hosted gradebook, no telemetry. Item text may transit to a model in a request; it is never stored remotely by this tool.
- **Model backends**: hosted (Claude Code, Codex, or a competitor) and local (an OpenAI-compatible server such as llama.cpp or Ollama running Qwen) are the same code path. The local backend is prepared in advance rather than retrofitted, so the hardware arriving is a config change and not a rewrite.
- **Surfaces**: every capability has both a route in the daemon and a command in the CLI. Neither surface is the real one; both are clients of the runtime.
- **Accepted risk — hosted models see item text.** Weibao's explicit decision on 2026-08-05, after the tradeoff was put to him. It means AAOS-12e-derivative EMT items and course-derived CSCI 1100 items transit to a hosted provider. Two things stay true and are recorded here so they are not rediscovered as surprises: hosted or local, this is **AI assistance on graded coursework**, and the CSCI 1100 AI-use ban applies to both; and the local-only path remains fully built, so any subject can be moved back behind it by changing one setting rather than by changing the code.
- **Data**: No real question banks in this repository, enforced by `itembank guard` in CI. Fixtures are synthetic. Learner evidence lives beside the private bank.
- **Compatibility**: Format changes must be additive. A bank without a `LESSON` section must parse exactly as it does today.
- **Hardware**: The local-model path targets a 7900 XTX build that does not exist yet. The adapter is designed now as a vendor-neutral interface; the local backend waits for the machine.
- **Users**: One. No accounts, no auth, no multi-tenancy, and no design work spent on them.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Root `ROADMAP.md` is an input, expanded, not replaced | It is a protocol-hardening plan; the learning platform lives in the issues. Both are real and neither supersedes the other. | — Pending |
| All 13 unbuilt issues plus 3 new capability areas in v1 | Weibao: "a comprehensive learning platform... like a combination of all the good learning programs." Scope is deliberate; sequencing carries the risk. | — Pending |
| Evidence spine (#4) and daemon (#7) before the auditor and trends | Both later areas write and read evidence. Building them before stable IDs and one store means building them twice. | — Pending |
| `check` item type in v1 | It is what makes the CS and Linux lanes expressible; today they have no item type at all. Scoped to running the learner's own answer, no sandboxing claim. | — Pending |
| Model layer is an interface, not a vendor | Weibao: "Interfacible with standard claude code or codex or competetor, but also with something like qwen or something open sourced someday." Decouples the milestone from hardware that does not exist. | — Pending |
| Auditor autonomy is a configurable range, ends included | Report-only through full audit-draft-lint-fix-commit. A range is a knob; two modes is a rewrite. | — Pending |
| The auditor may generate items, bounded by lint and reversibility | Moves the README's "does not generate questions" line on purpose. It survives only because every generated item passes the same contract a human's does, and every write can be undone. | ⚠️ Revisit |
| Scheduling in, cards stay in Anki | One scheduler and no second card store. A deeper Anki merge is a v2 question, not an assumption. | — Pending |
| Trends drive selection, not just display | All four uses chosen: selection weight, plan re-cutting, longitudinal view, decay flagging. Evidence captures more than currently needed. | — Pending |
| `day` fork 1 keeps the full editor and grows | Decided against issue #15's proposal to narrow it to dated capture. The optimistic-concurrency guard remains non-negotiable, because Obsidian and agents write the same files. | — Pending |
| Stay Python; buy adaptability at the JSON API seam | Weibao asked what works best and adapts to the others. The seam is cheap and a rewrite restarts the scorer. A future native shell is a client of `/api/*`, not a second implementation. | — Pending |
| Zipapp plus per-OS launcher, not a compiled binary | Double-click on Windows, macOS, and Linux from stdlib `python -m zipapp`, no signing, no Defender fight, and still plain Python inside so an agent can read it. Signed binaries deferred to v2. | — Pending |
| Updater ships, and the network constraint narrows on purpose | Weibao wanted grimoire's self-update. Grimoire is Electron plus `electron-updater` against GitHub Releases — a pipeline this project does not have. The stdlib equivalent is ~100 lines. Both opt-in and check-on-launch exist, toggleable. | ⚠️ Revisit |
| Settings are one documented file with a printed schema | "Tunable" means an agent adjusts settings, not source. `itembank config` does for settings what `spec` does for the format: a contract an agent can read and a linter can enforce. | — Pending |
| Every capability is both an app route and a CLI command | Weibao, twice: "shoudnt it be app based rather than terminal based? Both options should exist." Same shape as the one-scorer rule — two surfaces, one runtime. | — Pending |
| The model sees the key; the runtime gates the tier | Weibao: "It can refer to keys as needed?" A key-blind model can only recite authored text. A key-aware model teaching about *your* error is a much better tutor, and the guarantee survives by moving from "the model lacks the key" to "the model lacks the decision." | — Pending |
| Feedback policy belongs to the session mode | Weibao asked about Albert revealing the answer on a wrong response. Albert is right for volume drilling and wrong for diagnosis. Drill reveals, practice ladders, diagnostic and exam stay silent. One config field instead of one global argument. | — Pending |
| Hosted models permitted, risk accepted explicitly | Weibao chose "hosted allowed everywhere, accept the risk" after the AAOS-derivation and CSCI-1100-AI-ban tradeoff was stated. His call, recorded rather than relitigated. The local path stays built so any subject can move back with a setting. | ⚠️ Revisit |
| Model-first, offline-capable, local model prepared in advance | Weibao: "Maybe model first, and for me to prepare an powerful(ish) local model in advance?" Build against the model as the primary teaching path, keep the authored ladder as the floor, and write the adapter to an OpenAI-compatible shape so the 7900 XTX build is a config change. | — Pending |
| Item identity: opaque `[ID:]` plus a `[HASH:]` content fingerprint, not content-hash-as-ID | An edit to explanation text must not silently mint a new evidence-tracked item; the opaque ID stays stable across edits while `[HASH:]` tracks content drift for lint warnings. Resolves Phase 1's flagged identity-scheme question. | ✓ Shipped — Phase 01 (01-04) |
| Windows append-write durability: single `os.write()` per event under an advisory lock (`msvcrt.locking`/`fcntl.flock`) | The roadmap called this spike load-bearing before the append pattern could be trusted. Measured on the target Windows 11 machine: unlocked `O_APPEND` reproduced bpo-42606 corruption across three runs; the locked, single-write-per-event pattern did not tear once. | ✓ Shipped — Phase 01 (01-01, see `01-SPIKE-RESULT.md`) |
| `render_session_json`'s seed/selection approximation (always reports `seed: 0`; derives `items`/`cursor`/`status` from the item_refs the log proves were answered) is acceptable as-is | The session file cannot be an input to its own render (D-11), and an append-only log has no way to recover the true original seed/cursor once the session file is gone. Weibao confirmed the honest approximation is good enough for the day cockpit, resumed sittings, and agent tooling as currently scoped. | ✓ Accepted as-is — Phase 01 UAT (2026-08-07) |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-08-07 after Phase 01*
