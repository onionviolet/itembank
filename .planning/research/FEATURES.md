# Feature Research

**Domain:** Local-first assessment-and-teaching runtime for one learner across EMT, university Math, and intro CS (itembank)
**Researched:** 2026-08-05
**Confidence:** MEDIUM — findings are cross-verified across official docs, primary-source blog/forum accounts, and (for the education-research claims) secondary summaries of the underlying papers. No product was hands-on trialed this session and no full-text academic PDFs were read; single-source claims are flagged LOW inline.

## Feature Landscape

Fifteen-plus distinct systems examined: **Execute Program**, **Runestone Academy** (+ PreTeXt), **PrairieLearn**, **Anki** (scheduler and reviewer, as two separate design questions), **pwn.college**, **CTFd**, **Khan Academy**, **Brilliant**, **Duolingo**, **StudyBro**, **Moodle GIFT**, **IMS QTI**, three **Obsidian** plugins (Spaced Repetition, Flashcards, Flashcard Generator/LearnKit), and **H5P**/**Open edX**. Education research consulted: expertise-reversal effect (Kalyuga), worked-example effect (Sweller/cognitive load theory), desirable difficulties and interleaving (Bjork), and Bayesian/Deep Knowledge Tracing as the ITS literature's answer to "what should be reviewed next."

### Table Stakes (Users Expect These)

Features every examined platform has in some form. Missing these makes itembank feel like a test-runner, not a learning platform — which is exactly the gap PROJECT.md names.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Checked items with instant right/wrong feedback | Universal across Execute Program, Runestone activecode, PrairieLearn, Khan Academy, Brilliant, CTFd/pwn.college | LOW | Already shipped (`runtime.score_response()`) |
| Explanation attached to the verdict, not just the verdict | Brilliant's "hint nudges toward reasoning," Khan Academy's worked hints, itembank's `why`/`disc`/`trap` | MEDIUM | Partially shipped; `study` currently drops `opts`/`da`/`second`/`notes` (#17 part 2, active) |
| Multiple item/exercise types beyond plain MC | Runestone (activecode, CodeLens, Parsons, matching), PrairieLearn (dozens of element types), H5P (~50 content types) | MEDIUM–HIGH | itembank has six types plus `check` planned; breadth is already competitive |
| Spaced review of previously-learned material, not just linear progress | Execute Program's review queue, Anki, Obsidian SR plugin, RemNote | MEDIUM | itembank plans objective-level scheduling; card-level review deliberately stays with Anki |
| A pacing gate that prevents bingeing a whole course in one sitting | Execute Program explicitly "limits the number of lessons you can complete in a day for a given course" ([code.brettchalupa.com](https://code.brettchalupa.com/execute-program-review)) | LOW–MEDIUM | `day`'s floor rule and daily cap already exist; extending the cap to lessons is new work |
| Resumable, persisted progress | Every platform examined; PrairieLearn variants persist per-attempt, Anki persists the collection, Execute Program persists review state | LOW | Shipped — JSON sessions with resume |
| Plain-text, versionable content authoring | GIFT (text file), PreTeXt/Runestone source, PrairieLearn's `info.json`/`server.py`, Obsidian's `Question::Answer` inline syntax | MEDIUM | Table stakes specifically *for this class of tool* (local-first, git-tracked); most commercial products hide authoring behind a GUI, which would be a regression here |
| Hints that don't just hand over the answer | Brilliant's guided nudge, Khan Academy's step hints, CTFd's cost-gated hints | HIGH | itembank's deterministic ladder (#1, active) is the rigorous version of a pattern every platform has informally |
| A visible history of right/wrong over time | Every platform; itembank's evidence-spine work (#4) | MEDIUM | Currently split across three stores — the active work to unify it is exactly on the critical path |
| A verifier that runs the learner's own artifact, not just matches a string | pwn.college/CTFd (run the exploit, check the flag), PrairieLearn's `server.py` grading | HIGH | itembank's planned `check` type is this pattern applied to CS coursework |

### Differentiators (Competitive Advantage)

Where a local-first, key-withholding, single-user tool can beat every hosted product examined.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Answer-key withholding as an *architectural* guarantee, not a prompt instruction | Every AI-tutor product examined (StudyBro's "Bro," Khanmigo-style Socratic bots) relies on the model choosing not to reveal the answer under a system prompt. A model in a chat loop can be argued or role-played out of that discipline — a documented, well-known failure mode. itembank's `next`/`hint` never hand the key to a model at all: there is nothing to leak. | HIGH | This is the single biggest structural advantage over every competitor examined, hosted or open-source |
| Deterministic hint ladder tied to *authored distractor analysis* | Brilliant and Khan Academy hand-author hints per problem but not as a structured escalation over "why each specific wrong option is wrong." itembank's tier 3 (`da[picked letter]`) is targeted per-mistake, not generic | HIGH | Directly Core Value; measured against a live EMT bank, 100% of wrong options already have a `da` line, so tier 3 already fires broadly (per PROJECT.md) |
| One evidence store feeding selection, pacing, and a syllabus-coverage auditor | No examined single-user tool does the "audit coverage against a standards document" piece at all. BKT/DKT-style ITSs do adaptive selection but assume population-scale training data itembank does not have and structurally should not want (see Anti-Features) | HIGH | Novel combination, not a novel primitive — every piece (evidence, selection, audit) exists elsewhere separately |
| One subject-invariant loop across heterogeneous content (EMT prose, Math LaTeX, CS runnable code) | Execute Program is one loop but single-domain (JS/TS/SQL/regex). Runestone is one domain (CS/Math texts). PrairieLearn is course-scoped. No examined product runs one loop across genuinely different media and verifiers | MEDIUM–HIGH | This is PROJECT.md's explicit ask ("one loop... not four surfaces") |
| Git-evidence trail as the progress signal, replacing points/badges | Mirrors what the desirable-difficulties research actually supports (visible effortful practice, not extrinsic reward) without the anxiety/compulsion pattern documented around Duolingo streaks | LOW–MEDIUM | Already itembank-native via the `day` streak log |
| A machine-readable format contract + linter an authoring agent can self-correct against | PrairieLearn's `info.json`/`server.py` is the closest analog but is not documented as a contract for LLM self-correction. GIFT and QTI are consumption formats, not authoring contracts. `spec`/`lint` giving item-numbered, machine-readable errors is close to unique | MEDIUM | Mostly shipped; closing the authoring loop (#11) completes it |
| GIFT export as a cheap, one-way interoperability door | QTI is the "more complete" interchange format but is XML-based and materially heavier to implement; GIFT is plain text and Moodle-adjacent tools import it broadly | MEDIUM | Correctly scoped as the cheap proof rather than QTI (#12) |

**A pattern examined and deliberately not adopted:** PrairieLearn's randomized-variant engine (`server.py` generates new random parameters per attempt) exists to solve a *classroom* problem — many students working the same assessment need different numbers so they can't share answers, and homework mode regenerates a fresh variant after every wrong attempt to enable retry-to-mastery without repetition. A single learner has nobody to cheat off of and nobody to desync from. Variant generation is real engineering investment PrairieLearn needs and itembank does not; the value it would add here (fresh numbers on retry) is available more cheaply by simply drawing the next item from the bank's pool rather than building a parametrized generator.

### Anti-Features (Commonly Requested, Often Problematic)

PROJECT.md already rejects gamification, a social layer, hosted accounts, and a chat box as the *primary* tutoring surface. Those four hold up under this research (reasoning given below) and are marked **[reaffirmed]**. Six more are new, marked **[NEW]**.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|------------------|-------------|
| Points/badges/levels/leaderboards **[reaffirmed]** | "Keeps me motivated like Duolingo" | Duolingo's own retention numbers come with well-documented criticism of streak anxiety and compulsive-checking that substitutes score-optimization for studying; a single captive user gets none of the network-effect value a leaderboard exists to create | Git evidence trail + streak-as-signal, already planned |
| Chat box as the primary hint/tutor surface **[reaffirmed]** | "Just ask it to explain," mirrors StudyBro/Khanmigo-style Socratic bots | A model in an open chat loop can be argued or role-played into revealing the key — the defining failure mode of every prompt-based tutor examined. Expertise-reversal research also shows open-ended dialogue helps most *after* a learner already has a base — which the tiered ladder already encodes structurally, unlike a chat box | Deterministic hint ladder; the model appears only as a bounded rubric-grading client behind `submit`/`short`, never as the source of a hint |
| Data-hungry per-user model personalization (fitting BKT or FSRS-style parameters from scratch on one person's history) **[NEW]** | "Adaptive like a real ITS" | FSRS defaults are trained on ~700M reviews across ~10,000 Anki users; community guidance on when *optimizing* personal parameters beats the shipped defaults ranges from dozens to ~1,000 reviews depending on source — below that you fit noise. Bayesian Knowledge Tracing has the same population-data assumption baked into its learn/guess/slip/forget parameters. One learner's evidence store will not reach that scale for years, if ever, per subject | Transparent heuristics an owner can read and override: recency-weighted accuracy per objective, hand-set decay thresholds — exactly what "trends as a control loop" already plans |
| A content/bank marketplace or public sharing hub **[NEW]** | "Other learners could reuse my EMT bank" | Direct conflict with the never-a-content-store rule: EMT items are AAOS-derivative and CSCI 1100 runs under an AI-use ban. It is also infrastructure — accounts, hosting, moderation — sized for an audience of one | Banks stay in private storage; GIFT export is the answer for the rare case content needs to leave in a controlled, one-off way |
| A native mobile app (iOS/Android) **[NEW]** | "Study on my phone" | Doubles the surface count against the "every capability is a route and a command" rule; app-store distribution needs accounts, signing, and telemetry that conflict with the no-hosted-anything and stdlib-only constraints | The daemon's planned `--app=` frameless window already gives an app-like experience on the machine holding the content; a browser on the same network covers the rare off-machine case |
| Video lecture hosting / lecture capture **[NEW]** | "Walk me through it like a video" | Runestone's own PreTeXt book is already CSCI 1100's assigned material — building a video pipeline duplicates rented content, and video adds a storage/codec dependency the stdlib-only constraint can't satisfy | `LESSON` sections in prose, with vendored KaTeX for math and runnable code for CS, cover the "walk through" ask; point at the existing Runestone book instead of re-hosting it |
| Team/competitive multiplayer challenges (CTFd-style scoreboards, StudyBro-style matchmaking) **[NEW]** | "Verifier-backed problems are basically CTF challenges, so borrow the platform" | True of the mechanics (`check` mirrors "run it and compare"), but CTFd's actual product is built around team scoring and a public leaderboard. It's easy to copy the verifier idea and accidentally drag the competition layer in with it | Take pwn.college/CTFd's verifier-as-spine idea and stop there; competition/scoring is the social-layer rejection PROJECT.md already names, worth flagging explicitly because the source material makes it tempting |
| Push notifications / a background nagging daemon **[NEW]** | "Remind me before I forget" | There's no mobile app to notify from, and reminder-driven engagement is the same extrinsic-trigger mechanism the gamification rejection already avoids. Desirable-difficulty research is about *voluntary* effortful retrieval, not compliance nagging | The `day` cockpit is the one daily-visited surface; a streak/decay flag rendered there is the reminder |
| Auto-grading prose into mastery without a review state **[reaffirmed, already in PROJECT.md]** | "The model can just check if the explanation is right" | Keyword matching can't separate a correct explanation from a confident wrong one with the right nouns in it | Rubric checklist producing structured evidence per point (#8, active), not a binary auto-grade |
| A social layer generally **[reaffirmed, already in PROJECT.md]** | — | Worth something at ten thousand students, nothing at one | — |

**On chat-box tutoring specifically — a narrower reconsideration, not a reversal.** The rejection of chat-as-primary-surface is correct and this research does not overturn it. But there is a bounded variant worth naming so it isn't accidentally rejected too: a natural-language *restatement* of an already-unlocked hint tier (e.g., "put tier-1's objective pointer in your own words") never touches withheld content, because it operates only on text the ladder has already released. That is different from an open chat box that can be walked backward toward the key. If a natural-language surface is ever added, the boundary is "restates what's already unlocked," not "answers freely."

## Feature Dependencies

```
Evidence store (unified, stable content-hash IDs)
    ├──requires──> Content-hash item IDs (#4, must land first)
    ├──feeds──> Selection weighting (weak objectives raise, mastered drop out)
    ├──feeds──> Decay flagging (correct a month ago, untouched since)
    ├──feeds──> Auditor coverage report (bank vs syllabus objectives)
    └──feeds──> Longitudinal /report view (accuracy by objective over weeks)

LESSON sections + LESSON-REF
    └──requires──> Format contract stays additive (a bank without LESSON parses unchanged)
    └──enables──> Hint ladder tier 0 (lesson pointer) and tier 1 (objective)

Hint ladder (tiers 0–5)
    ├──requires──> LESSON-REF (tiers 0–1)
    ├──requires──> Authored `da` distractor analysis (tier 3) — already ~100% coverage in the live EMT bank
    ├──requires──> `submit` holding the cursor instead of auto-advancing (#1)
    └──feeds──> report distinguishing right-at-tier-1 from right-at-tier-4

`check` item type
    ├──requires──> A monospace code-editing surface (tab handling, line numbers)
    └──enables──> The CS/Math lanes having any verifier-backed item type at all — today they have none

One subject-invariant loop (prose / LaTeX / code)
    ├──requires──> LESSON sections (medium)
    ├──requires──> `check` type (CS verifier)
    └──requires──> Vendored KaTeX (Math medium) — the one named non-stdlib exception

Daily cap / pacing gate (Execute Program pattern)
    ├──requires──> `day`'s existing floor rule (already shipped)
    └──enhances──> Retention, per desirable-difficulties research (spacing beats massing)

Auditor (syllabus ingestion → gap report → optional draft)
    ├──requires──> Evidence store (to diff coverage against)
    ├──requires──> `lint` (every generated item must pass it before reaching a bank)
    └──requires──> Reversible writes (every auditor write can be undone)

GIFT export
    └──requires──> Stable item IDs (#4) — otherwise round-tripping breaks on re-lint

Full spaced-repetition ownership (item-level FSRS/SM-2 inside itembank)
    └──conflicts with──> "Anki owns card reviews" decision — building a second scheduler recreates
                          the double-scheduling / conflicting-due-dates failure mode this project
                          is explicitly trying to avoid by keeping scheduling layers separate

Chat box as primary tutor
    └──conflicts with──> Answer-key withholding architecture (the Core Value) — a model that can
                          be asked anything can be argued into anything
```

### Dependency Notes

- **Evidence store before selection, decay, auditor:** all three read the same evidence and would otherwise be built against three different partial stores that later need reconciling — exactly the ordering PROJECT.md's Key Decisions table already calls out.
- **`da` distractor analysis before hint tier 3:** this is already satisfied for the live EMT bank (0 of 45 wrong options lack a `da` line entirely per PROJECT.md's own audit), so tier 3 is not blocked on authoring — it's blocked on the hint ladder's own build.
- **Full SRS ownership conflicts with keeping Anki:** this is a genuine either/or, not a nice-to-have stack. Anki already has a mature FSRS implementation; duplicating it inside itembank at objective granularity (not card granularity) avoids the conflict rather than resolving it — which is exactly the design itembank has already chosen.
- **Chat-box-as-tutor conflicts with the Core Value directly:** not a resource conflict, a structural one. Any surface that lets a model answer freely reopens the exact vulnerability ("a tutor built on this cannot cave... because it was never handed the key") that PROJECT.md states as the reason the project exists in its current form.

## MVP Definition

### Launch With (v1)

Minimum to prove itembank teaches, not just tests — reframed from PROJECT.md's Active list around "what's the smallest working loop":

- [ ] Evidence store (single source, stable IDs) — everything else reads or writes it
- [ ] `LESSON` sections + per-item `LESSON-REF`, additive to the format — the medium the loop needs to exist at all
- [ ] Deterministic hint ladder (tiers 0–5) over already-authored `da`/`disc`/`trap` — the one differentiator no competitor has
- [ ] `submit` holds the cursor on a wrong answer; `hint` command; `hints_used` tracked — mirrors Execute Program's "don't penalize unless you give up" pattern, already validated by that product's design
- [ ] `report` distinguishing right-at-tier-1 from right-at-tier-4 — the signal that makes the hint ladder legible, not just functional
- [ ] `check` item type (run the learner's own code, compare output; no sandboxing claim) — the only way the CS lane gets an item type at all
- [ ] One subject-invariant loop: EMT prose, Math LaTeX, CS code, same runtime
- [ ] Daily cap enforced through `day` — the pacing gate every retention-focused competitor examined has in some form

### Add After Validation (v1.x)

Trigger: the core loop above has real usage and real evidence data to act on.

- [ ] Selection modes (diagnostic/practice/remediation/exam) — needs an evidence store with enough history to select meaningfully against
- [ ] Recent-exposure tracking, discrimination pairs — refinements to selection, not blockers for it
- [ ] Decay flagging and weak-objective weighting — needs weeks of real evidence before decay is a real, not hypothetical, signal
- [ ] Auditor in draft-and-approve mode — only after report-only mode has been trusted for a while (per PROJECT.md's own configurable-autonomy design)
- [ ] GIFT export — needs stable content-hash IDs first, or round-tripping breaks

### Future Consideration (v2+)

- [ ] Full spaced-repetition ownership merged with Anki's queue — defer until objective-level scheduling has run long enough to know whether card-level scheduling is actually a bottleneck, not a hypothetical one
- [ ] Local model backend (Qwen on the 7900 XTX build) — defer until the hardware exists; the adapter interface ships now, the backend later
- [ ] Compiled binary packaging — defer until a second person actually runs this, which is when "install Python" becomes a real barrier rather than a theoretical one
- [ ] Bounded natural-language restatement of already-unlocked hint tiers — worth a v2 look once the deterministic ladder has real usage data showing where it feels rigid

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Unified evidence store, stable IDs | HIGH | MEDIUM | P1 |
| Deterministic hint ladder | HIGH | HIGH | P1 |
| `submit` holds cursor + `hint` command | HIGH | MEDIUM | P1 |
| `check` item type (CS verifier) | HIGH | HIGH | P1 |
| `LESSON` sections + `LESSON-REF` | HIGH | LOW–MEDIUM | P1 |
| Daily cap / pacing gate | MEDIUM | LOW | P1 |
| Report: hint tier reached | MEDIUM | LOW | P1 |
| Selection modes (diagnostic/practice/remediation/exam) | MEDIUM | MEDIUM | P2 |
| Decay flagging, weak-objective weighting | MEDIUM | MEDIUM | P2 |
| Auditor (coverage report, draft-and-approve) | MEDIUM–HIGH | HIGH | P2 |
| GIFT export | LOW–MEDIUM | LOW | P2 |
| Full SRS ownership merged with Anki | LOW (Anki already does this) | HIGH | P3 |
| Randomized item variants (PrairieLearn pattern) | LOW (single learner, no cheating pressure) | HIGH | P3 |
| Bounded NL restatement of unlocked hints | LOW–MEDIUM | MEDIUM | P3 |
| Local model backend | Blocked on hardware | HIGH | P3 |

**Priority key:** P1 must exist for the "comprehensive learning platform" claim to be true; P2 should follow once P1 generates real evidence to build on; P3 is genuinely deferrable without weakening Core Value.

## Competitor Feature Analysis

| Dimension | Execute Program | Anki | CTFd / pwn.college | Khan Academy | itembank's approach |
|-----------|------------------|------|---------------------|---------------|----------------------|
| Spaced review | Fixed-schedule queue, roughly retires an item after the 4th correct rep (~day 64); author calls it "crude relative to Anki" ([mike.place](https://mike.place/2020/executeprogram/)) | Adaptive per-card (FSRS: difficulty/stability/retrievability) or classic SM-2 ease factor | None — challenge-based, not review-based | Mastery decay implied by the "Attempted → Familiar → Mastered" ladder, mechanism not public | Objective-level scheduling only; card-level review deliberately stays in Anki |
| Hint mechanism | None documented beyond retry-until-correct | None (reviewer shows answer on demand) | Cost-gated unlockable hints, admin-authored | Step-by-step worked hints | Deterministic 6-tier ladder over authored distractor analysis — structurally cannot skip to reveal |
| Content authoring | Closed/proprietary | Plain-text-adjacent (note fields), or GUI | Admin web UI, some YAML/JSON import | Closed | Plain-text markdown, git-tracked, linted with machine-readable errors |
| Verifier-backed items | Executable code checks inline | N/A | Run the exploit/binary, compare against a flag | Auto-graded MC/numeric | Planned `check`: run the learner's code, compare output |
| Daily pacing gate | Per-course lesson cap, cannot binge a whole course in one day | None (reviewer just shows what's due) | None | None documented | `day`'s floor rule + cap, extending to lesson pacing |
| Answer-key protection | N/A (no AI tutor layer) | N/A | N/A (flag itself is the secret) | N/A | Architectural: `next`/`hint` never hand the key to a model — the differentiator over every AI-tutor product (StudyBro, Khanmigo-style) |
| Multi-subject, one loop | One loop, single domain (JS/TS/SQL/regex) | One loop, content-agnostic (cards are cards) | One loop, single domain (security) | Multiple domains, but siloed per subject | One loop across genuinely different media (prose/LaTeX/code) and verifiers — the explicit ask |
| Reviewer/quiz surface | Web app, moderate chrome | Deliberately minimal: no animation, no chrome by default, keyboard-only, one card at a time | Web app with scoreboard chrome | Rich, animated UI | Modeled on Anki's minimalism for `study`; `day` still carries technical debt (a third, un-variabled palette) |

## Sources

**Execute Program:** [mike.place — first-hand account of pacing, review schedule, retry-without-penalty](https://mike.place/2020/executeprogram/) (LOW — single blog source for the day-64/4th-repetition detail) · [Andy Matuschak's notes — prerequisite gating, executable-everything design](https://notes.andymatuschak.org/zSsjk5UvNPGrYp8B6DEFCMS) (MEDIUM) · [code.brettchalupa.com review — explicit daily lesson cap](https://code.brettchalupa.com/execute-program-review) (MEDIUM)

**Runestone / PreTeXt:** [About Runestone Academy](https://pretextbook.org/doc/guide/html/about-runestone.html) · [Overview of Runestone Academy](https://runestone.academy/ns/books/published/overview/index.html) · [Interactive Exercises — PreTeXt Guide](https://runestone.academy/ns/books/published/pretextguide/topic-interactive-exercises.html) · [The Runestone Philosophy](https://runestone.academy/ns/books/published/instructorguide/prose-philosophy.html)

**PrairieLearn:** [Question overview docs](https://docs.prairielearn.com/question/overview/) · [Assessment configuration docs](https://docs.prairielearn.com/assessment/configuration/) — homework-mode variant regeneration and exam-mode fixed variants confirmed here (MEDIUM)

**Anki scheduler:** [Anki FAQ — spaced repetition algorithm](https://faqs.ankiweb.net/what-spaced-repetition-algorithm) · [fsrs4anki tutorial](https://github.com/open-spaced-repetition/fsrs4anki/blob/main/docs/tutorial.md) · [FSRS vs SM-2 comparison](https://flica.app/article/fsrs-vs-sm2) · [Anki GitHub issue on minimum-reviews-for-optimization research](https://github.com/ankitects/anki/issues/3094) · [Anki forums — how many reviews for accurate optimization](https://forums.ankiweb.net/t/how-many-reviews-for-accurate-optimization/53320) (MEDIUM — forum discussion, cross-checked against official issue tracker) · [Expertium's technical explanation of FSRS](https://expertium.github.io/Algorithm.html)

**Anki reviewer minimalism:** general search corroboration only (no single authoritative design-philosophy doc found); cross-checked against PROJECT.md's own prior characterization ("no animation, no chrome, keyboard-only, one card") — LOW independent confidence, MEDIUM as corroboration of an already-asserted claim

**Leitner system:** [e-student.org — Leitner box mechanics](https://e-student.org/leitner-system/) (MEDIUM, cross-checked against multiple similar summaries)

**pwn.college / CTFd:** [pwn.college GitHub org](https://github.com/pwncollege) · [pwn.college site](https://pwn.college/) · [PWN the Learning Curve — SIGCSE paper on pedagogical design goals and pwnshop generator](https://yancomm.net/papers/2024%20-%20SIGCSE%20-%20PWN%20the%20Learning%20Curve.pdf) · [CTFd flags/overview docs](https://docs.ctfd.io/docs/flags/overview/) · [CTFd GitHub](https://github.com/CTFd/CTFd)

**Khan Academy:** [Why Mastery Learning, by Sal Khan](https://support.khanacademy.org/hc/en-us/articles/360030753412-Why-Mastery-Learning-by-Sal-Khan) · [Cult of Pedagogy — Khan mastery learning](https://www.cultofpedagogy.com/khan-mastery-learning/) · [What is self-paced Mastery](https://support.khanacademy.org/hc/en-us/articles/360007253831-What-is-self-paced-Mastery) — hint-system internals not publicly documented (gap, noted)

**Brilliant:** [Brilliant Basics help center](https://brilliant.org/help/using-brilliant/) · [UX Collective — interactive play in math/science learning](https://uxdesign.cc/the-key-to-learning-math-and-science-online-is-interactive-play-6ea68ce167fe) · [Rive — Brilliant's "Game Feel" motivation design](https://rive.app/blog/how-brilliant-org-motivates-learners-with-rive-animations)

**Duolingo:** [Medium — Duolingo gamification analysis](https://medium.com/@navsrujan.mit/duolingo-gamifying-language-learning-eb8e6a55b521) · [gadallon.substack.com — engagement vs. education tension](https://gadallon.substack.com/p/duolingos-scaling-journey-education) (MEDIUM — commentary/opinion source, retention-vs-criticism claims cross-checked across multiple independent write-ups)

**StudyBro:** [studybro.academy — product page](https://studybro.academy/) (HIGH-confidence primary source; confirms hint/simplify/analogy Socratic mechanic, social matchmaking, gamified streak/badges, and tiered pricing directly)

**GIFT / QTI:** [GIFT (file format) — Wikipedia](https://en.wikipedia.org/wiki/GIFT_(file_format)) · [QTI — Wikipedia](https://en.wikipedia.org/wiki/QTI) · [Edlink — What is the QTI Specification](https://ed.link/community/ims-question-test-interoperability-qti-specification/amp/)

**Obsidian plugins:** [Spaced Repetition plugin](https://community.obsidian.md/plugins/obsidian-spaced-repetition) · [obsidianstats.com — spaced-repetition plugin roundup](https://www.obsidianstats.com/posts/2025-05-01-spaced-repetition-plugins) · [Flashcards plugin](https://www.obsidianstats.com/plugins/flashcards-obsidian) · [Flashcard Generator / LearnKit](https://www.obsidianstats.com/plugins/flashcard-gen)

**H5P / Open edX:** [Appsembler — Adding H5P activities to Open edX](https://help.appsembler.com/article/411-adding-h5p-interactive-activities-to-open-edx-courses) · [OpenCraft — Creating course content with H5P](https://opencraft.com/creating-course-content-with-h5p/)

**Education research:** [Expertise Reversal Effect — Wikipedia](https://en.wikipedia.org/wiki/Expertise_reversal_effect) · [Cognitive Load Theory blog — expertise reversal](https://cognitiveloadtheory.wordpress.com/the-expertise-reversal-effect/) · [Effect of worked examples on solution steps and transfer](https://www.tandfonline.com/doi/full/10.1080/01443410.2023.2273762) · [Worked-example effect — Wikipedia](https://en.wikipedia.org/wiki/Worked-example_effect) · [NSW Dept of Education — cognitive load theory research summary](https://education.nsw.gov.au/content/dam/main-education/about-us/educational-data/cese/2017-cognitive-load-theory.pdf) · [Structural Learning — Bjork's desirable difficulties](https://www.structural-learning.com/post/robert-bjork-teachers-guide-desirable) · [Durrington Research School — Bjork's desirable difficulties](https://researchschool.org.uk/durrington/news/bjorks-desirable-difficulties) · [UNH — Introducing Desirable Difficulties into Practice and Instruction (Bjork & Bjork)](https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-introducing-desirable-difficulties-into-practice-and-instruction-bjork-and-bjork.pdf) · [Bayesian Knowledge Tracing — Wikipedia](https://en.wikipedia.org/wiki/Bayesian_Knowledge_Tracing) · [ACM — 25 years of Bayesian Knowledge Tracing, systematic review](https://dl.acm.org/doi/10.1007/s11257-023-09389-4)

**CS1 pedagogy (context for CSCI 1100 lane design):** [ACM — a bottom-up approach for CS programming education](https://dl.acm.org/doi/abs/10.5555/3469581.3469588) · [Brown — bottom-up and datatype-driven program design](https://cs.brown.edu/~kfisler/Pubs/sigcse16-interplay-design.pdf)

---
*Feature research for: itembank — local-first learning platform, single user*
*Researched: 2026-08-05*
