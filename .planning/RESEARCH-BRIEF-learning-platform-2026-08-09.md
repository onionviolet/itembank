# Research Brief — Learning Platform Inspiration and Differentiators

- **Created:** 2026-08-09
- **Status:** brief written, research not yet run
- **Purpose:** drive one comprehensive research pass whose findings are embedded
  into Phases 5–12. This document is the input contract for that research and the
  home of its conclusions.
- **Execution split:** Claude plans and researches here. DeepSeek V4 executes.
  Do not run `/gsd-execute-phase` from this session.

---

## 1. Constraint Change — Weibao's Words, Verbatim

Recorded 2026-08-09. This supersedes the Constraints section of
`.claude/CLAUDE.md`, which is stale until amended.

> "our constraints is bendable if the idea is good enough, local first is not a
> real contraint, but a preference, build step is not a constraintm we cab build
> if need b, and shoudnt be limited by python if better options exist and mroe,
> we do want a packaged app in the end,"

Also recorded, from the same session:

> "goal is the plan and explore comprehensively, leaving executrion to deepseek"

> "Cool features no one has like keyterms with hover over, seperate blocks of
> stuff to remember, lesson generation styling/voice, we can combine all their
> unique benefits and address all their weaknesses too"

### What that means operationally

| Was | Now |
|---|---|
| Python stdlib only | Preference. Dependencies allowed when they earn it. |
| No install/build step | Not a constraint. Bundlers and npm are permitted. |
| Python only | Not binding. Other languages allowed where clearly better. |
| Offline-first, local-first | A preference, not a rule. |
| No packaging goal | **A packaged desktop app is now an end goal.** |

### What did NOT change

These remain non-negotiable and any research finding that violates them is rejected:

1. The **runtime**, not a model, decides what reaches the learner.
2. Exactly **one parser, one scorer, one evidence store**.
3. Evidence and banks stay on disk; no telemetry.
4. Format changes are **additive**: a bank without a new section parses unchanged.
5. Accessibility gates in `.planning/UI-SPEC.md` hold. DOM-based rendering, no canvas
   for content, semantic equivalent beside any pixel-shaped visual.

### Open recommendation, not yet decided

The Python runtime (parser, scorer, evidence store, daemon) is the project's
differentiating asset and represents four completed phases. Recommendation is to
keep it and add a real frontend on top, packaged together — Python as a sidecar
process under Tauri — rather than rewriting it. **Weibao has not ruled on this.**
The research prompt in §4 asks the question rather than assuming the answer.

---

## 2. Inspiration Set

Grouped by what we would take. Not a shortlist; the research pass should widen it.

### Executable textbook
Execute Program (named by Weibao in PROJECT.md), Runestone Academy, Brilliant,
Boot.dev, Observable, Jupyter Book.
**Take:** short prose → inline runnable check → same concept resurfaces days later.

### SR-native authoring
RemNote, Mochi, Obsidian SR plugins, Anki + FSRS, Quizlet Learn.
**Take:** notes and cards are one object; inline cloze; FSRS as the Phase 10 scheduler.

### Reader with gloss
LingQ, Readlang, Migaku, Kindle Word Wise, Readwise Reader.
**Take:** tap a term, gloss appears, term joins a review queue. This is both our
glossary feature and the deferred language-learning product.

### AI tutor UX
Khanmigo, Synthesis Tutor, Exercism mentoring.
**Take:** the copy and affordances used when refusing to hand over an answer.
We refuse structurally, which is stronger; we want their wording.

### Editors
CodeMirror 6, Monaco, Tiptap, Milkdown, ProseMirror, Typora, iA Writer,
Notion slash-blocks, Bear.

### Typography and rich blocks
Stripe docs, MDN, Docusaurus, VitePress, Logseq, Bear.
**Take:** callout grammar, code presentation, figure/caption, doc navigation.

### Math and diagrams
KaTeX, MathJax, Desmos, GeoGebra, Manim, Excalidraw, tldraw, Mermaid.

### Packaging
Tauri, Electron, PyInstaller, Python-as-sidecar architectures.

---

## 3. Differentiators — Combine Strengths, Fix Weaknesses

The pitch: no single product does all of these. We can, because we own the format,
the renderer, and the scorer.

| # | Feature | Who does part of it | What they get wrong | Our version |
|---|---|---|---|---|
| D1 | **Key terms with hover definitions** | LingQ, Kindle Word Wise, Obsidian | Language readers only, or notes-only with no assessment link | `## TERMS` glossary; `[[term]]` inline renders `<dfn>`; hover or tap reveals; term is linkable to the items that test it, and to a review queue. Degrades to visible text with JS off. |
| D2 | **Blocks of stuff to remember** | GitHub/Docusaurus callouts, Anki | Callouts are decorative; Anki cards are divorced from prose | A `[!KEY]` callout is a *first-class memorizable*: it renders as a styled block, exports to Anki, and is schedulable. One authoring act, three surfaces. |
| D3 | **Lesson generation voice and style contract** | Nobody | Every AI-authored lesson reads differently and uses every block it is given | `LESSON-STYLE.md`: a house style an authoring model reads before writing and a linter checks after. Lesson quality becomes a lint pass, not a hope. |
| D4 | **The runtime gates the tutor** | Khanmigo, Synthesis | A system prompt asks the model to withhold, and prompts can be argued with | Hint tier and session mode are runtime state. A model talked into revealing still cannot. Already our core claim; needs the UX to make it visible. |
| D5 | **One evidence store across subjects** | Anki (cards only), Quizlet (sets), Brilliant (walled) | Progress is per-product and unexportable | Every subject, every item type, one append-only store on your disk. Exportable. |
| D6 | **Prose and assessment in one file** | RemNote, Mochi | Markdown-ish but proprietary sync and no scoring contract | Plain markdown banks with `## LESSON`, `## TERMS`, and items. Backlinks already implemented. |
| D7 | **Executable prose** | Execute Program, Runestone | Language- or course-locked, subscription, online-only | Runnable blocks by fenced info string, subject-invariant, on your machine. |
| D8 | **Provenance you can audit** | Nobody in this space | No product tells you which textbook page an item came from | `[SRC:]` tags plus an objective coverage map, so the curriculum auditor can say what the syllabus covers that the bank does not. |

### Weaknesses to design against

- **Duolingo streak psychology** is punitive. Our spec already forbids punitive framing. Take the pacing, not the guilt.
- **Anki's authoring UX** is hostile. Take FSRS, not the note-type editor.
- **Brilliant is a walled garden.** Take the one-idea-per-screen loop, not the lock-in.
- **Notion-style block editors** cost a document model, a selection model, and an IME story. Only adopt if raw markdown is proven to be a real barrier.
- **Every AI tutor** leaks answers under pressure. Our structural gate is the fix; make it legible in the UI.

---

## 3.5 Blind Spots — Things We Have Not Considered

Written before the research runs, so the research can confirm, refute, or extend
it. Each is a real question the current roadmap does not answer.

| # | Blind spot | Why it matters |
|---|---|---|
| B1 | **Cold start.** How does a learner get their first usable bank without hand-authoring 200 items? | This is the difference between a tool Weibao uses and a tool Weibao abandons. Phase 11 authoring is late. |
| B2 | **Mobile.** Studying happens on a phone, in a car, between shifts. Every surface we have is a desktop browser page. | A packaged desktop app may optimize the wrong device. |
| B3 | **Audio and TTS.** EMT protocol memorization while driving or walking. | Highest-leverage modality we have zero plan for. |
| B4 | **Print and PDF export.** Paper study is real, especially for EMT. | Cheap to add, never discussed. |
| B5 | **First-run and empty states.** What does day one look like with no bank, no evidence, no history? | Currently undefined across every surface. |
| B6 | **Search.** Across banks, lessons, terms, and past attempts. | Absent from the roadmap entirely. |
| B7 | **Backup and portability.** Local-first means the disk dying loses everything. | We removed cloud sync without replacing the guarantee it gave. |
| B8 | **Adherence and motivation.** The thing that actually determines outcomes. | We forbid punitive framing but have proposed no positive mechanism. |
| B9 | **Image ingestion / OCR.** Photographing a textbook page or a diagram. | Directly serves B1 cold start and EMT figures. |
| B10 | **Handwriting and stylus.** Math work is done by hand. | Math 1400 short-answer may be unusable typed. |
| B11 | **Exam-format fidelity.** NREMT and course exam formats have specific shapes. | A quiz that does not look like the real exam trains the wrong thing. |
| B12 | **Bank versioning and diffing.** Banks are markdown in git; edits are reviewable. | An underused asset no competitor has. |
| B13 | **Reading accessibility beyond WCAG.** Dyslexia-friendly typefaces, line-length control, ADHD pacing, focus mode. | Our gates cover contrast and keyboard, not readability. |
| B14 | **Degraded-model UX.** What the tutor surface looks like with no network or no credits. | Named as a constraint, never designed. |
| B15 | **Time-on-task honesty.** Useful analytics without telemetry. | All measurement is local; we have not said what we measure. |

---

## 4. The Research Prompt

Run this first. Everything downstream depends on its output.

```text
/gsd-explore Comprehensively research modern learning platforms, editors, readers,
and packaging approaches to inform itembank Phases 5-12. Read
.planning/RESEARCH-BRIEF-learning-platform-2026-08-09.md first and treat its
sections 1-3 as binding context.

CONSTRAINTS — see brief section 1. Stdlib-only, no-build-step, Python-only and
offline-first are now PREFERENCES, not rules. A build step is allowed.
Non-Python components are allowed where clearly better. A PACKAGED DESKTOP APP
is an end goal. Judge each idea on whether it makes the product better and
report its real cost; do not reject an idea for needing a dependency.
Non-negotiable: the runtime not the model decides what reaches the learner;
one parser, one scorer, one evidence store; additive format changes;
the accessibility gates in .planning/UI-SPEC.md.

DO NOT limit yourself to the inspiration set in section 2. Widen it. Add
categories, products, and patterns it misses, and say what it missed.

RESEARCH THE VISUAL DESIGN, not only the feature set. For the products in
section 2, study how they actually LOOK and FEEL, and report specifics we can
act on rather than adjectives:
- Type: typeface pairing, scale ratio, body size, measure (line length),
  leading, and how they handle long-form reading versus dense UI.
- Color: how many colors carry meaning, how semantic states (correct, wrong,
  hint, locked, unavailable) are encoded, and how dark mode is handled without
  a second palette.
- Layout: grid, density, whitespace, sidebar versus single column, where
  navigation lives, and how a long lesson is navigated.
- Blocks: exactly how callouts, definitions, figures, code, and math are
  styled, including borders, icons, backgrounds, and spacing.
- Motion: what animates, what does not, and what earns its cost.
- Identity: what makes each one recognizable in one screenshot, and what the
  templated-looking ones have in common.
- Empty states, first-run, loading, and error screens.
Then propose ONE coherent visual direction for itembank that unifies quiz,
study, lesson, day, report and settings into a product that reads as one thing.
It must build on Phase 4's shipped token system rather than replace it, and it
must state its distinctive move: the single deliberate choice that keeps it
from looking like a default admin template.

ALSO ADDRESS THE BLIND SPOTS in section 3.5 of the brief. For each of B1-B15,
say whether it is real, how competitors handle it, what it would cost us, and
which phase should own it. Add blind spots the list misses and say why they
matter. Treat B1 cold start, B2 mobile, and B3 audio as high priority: they
may change the roadmap rather than fit inside it.

Answer these directly and concretely:
1. What does an excellent lesson display look like in 2026? Name the specific
   typographic and block-level decisions, not principles.
2. What should the bank/lesson markdown editor be, and why that one over the
   alternatives? Include live-lint integration and split preview.
3. What belongs in LESSON-STYLE.md so an AI writes consistently good lessons?
   Which of those rules are machine-checkable by our linter, and how?
4. Design differentiators D1, D2 and D3 in section 3 in detail: key-term hover
   definitions, memorizable [!KEY] blocks that export to Anki, and the lesson
   voice contract. These are the features no competitor combines. Specify the
   format grammar, the render behavior, the no-JS fallback, and the evidence
   semantics for each.
5. Best extraction standard from a textbook, or from a syllabus that references
   one: provenance tagging, objective coverage mapping, paraphrase-not-transcribe,
   and how to lint all three.
6. Per-subject best fit: EMT readings and scenarios, Math 1400 LaTeX and
   manipulables, CSCI 1100 bottom-up runnable code.
7. Can a bilingual reader be one extra glossary field rather than a separate
   codebase? Where is the real fork line?
8. What packaging path gives a real installer? Evaluate Tauri with a Python
   sidecar, Electron, and PyInstaller. Say explicitly whether the Python runtime
   should be kept or replaced, and argue it.
9. What are we not asking that we should be? Be specific and uncomfortable.
   Name assumptions in this brief that are probably wrong.
10. What is the single highest-leverage change we could make that is not
    currently anywhere in the roadmap?

For each finding report: what it is, why it works pedagogically, its cost in our
stack, which phase it belongs to (5-12 or a new insert), and whether it is a
FORMAT, RENDERER, RUNTIME, PACKAGING or CONVENTION change.

Write findings to .planning/research/ as durable artifacts. Append a
"Findings" section to this brief summarizing conclusions and phase assignments.
Phase 4 is IMPLEMENTED: the token system and shell exist. Build on them.
```

---

## 5. Embedding Plan — Where Findings Land

Remaining phases are 5, 6, 6.1, 7, 8, 9, 10, 11, 12, plus proposed inserts.

| Phase | Absorbs from research |
|---|---|
| **03.1 (INSERT)** Lesson Rich Blocks, Glossary & Style | D1 hover terms, D2 memorizable blocks, D3 `LESSON-STYLE.md`, callouts, figures, type scale. Consumes Phase 4's tokens. |
| **03.2 (INSERT)** Source Provenance & Extraction | Q5 extraction standard, `[SRC:]`, objective coverage map, syllabus import. Shrinks Phase 11. |
| **5** Check Item Type & Code Editor | Q2 editor choice (CodeMirror 6 or successor), runnable-block presentation, D7. |
| **6** Hint Ladder & Feedback Modes | Q4 D4 tutor-refusal UX and copy from Khanmigo/Synthesis/Exercism. |
| **6.1** Visual Assessment Protocol | Desmos/GeoGebra/Excalidraw/Mermaid patterns for manipulable and diagram items. |
| **06.2 (INSERT)** Executable Textbook Loop | Execute Program / Runestone loop: prose → check → spaced re-exposure. |
| **7** Selection Engine | Brilliant one-idea-per-screen sequencing; "why this item" trace wording. |
| **8** Model Adapter & Tier Gate | Q4 provenance and refusal surfacing; generated-hint presentation. |
| **9** Subject-Invariant Loop | Q6 per-subject profiles; KaTeX/manipulables for math; bottom-up for CS. |
| **10** Retention, Pacing & Trends | FSRS scheduler; D2 memorizables entering the queue; anti-punitive pacing copy. |
| **11** Authoring Loop & Curriculum Auditor | `LESSON-STYLE.md` enforcement; coverage audit against 03.2's map. |
| **12** Packaging & Self-Update | Q8 Tauri vs Electron vs PyInstaller; the packaged-app goal. |
| **999.2 (BACKLOG)** Language Reader | Q7. Design D1's grammar with a third optional field now; build nothing yet. |

---

## 6. Run Sequence

1. `/gsd-explore` with the §4 prompt. Findings land in `.planning/research/`.
2. Append conclusions to §5 of this brief.
3. `/gsd-phase` to insert 03.1, 03.2, 06.2 and update Phase 5-12 scope from §5.
4. Per phase: `/gsd-ui-phase <n>` then `/gsd-plan-phase <n>`. Chains for different
   phases are independent and can run in separate sessions.
5. **Stop.** Hand to DeepSeek V4 for `/gsd-execute-phase`.

Note: execute-phase runs plans sequentially here regardless of worktree config,
because of a fork-base guard. Concurrency is available in planning only.

---

## 7. Findings

Research pass run 2026-08-09 (seven parallel agents, web-sourced, verified
against `model.py`, `ROADMAP.md`, and `UI-SPEC.md`). Full detail lives in the
durable artifacts; this section is the conclusions and phase assignments.

### 7.1 Artifact index

| Artifact (`.planning/research/`) | Covers |
|---|---|
| `2026-08-09-visual-design.md` | Look-and-feel specifics per product; the proposed visual direction |
| `2026-08-09-lesson-display-editor.md` | Q1 lesson display; Q2 editor choice |
| `2026-08-09-differentiators-d1-d2-d3.md` | Q3 LESSON-STYLE.md; Q4 D1/D2/D3 grammar, render, no-JS, evidence |
| `2026-08-09-extraction-subjects-bilingual.md` | Q5 extraction standard; Q6 per-subject fit; Q7 bilingual fork line |
| `2026-08-09-packaging.md` | Q8 packaging path and keep-vs-replace verdict |
| `2026-08-09-blind-spots.md` | B1–B15, seven new blind spots, Q9, Q10 |
| `2026-08-09-landscape-widening.md` | What §2 missed; fight-for and do-not-copy lists; standards verdict |

### 7.2 Question verdicts

| Q | Verdict |
|---|---|
| Q1 | 72ch measure, spaced paragraphs, three heading levels on the existing 4-size/2-weight ramp, filename-tab code blocks without line numbers, `<details>` footnotes, TOC + `aria-current` scroll-spy, no progress bar. Fits Phase 4 tokens with zero new type sizes. One open ruling: 18px lesson body vs locked 16px `text-body`. |
| Q2 | **CodeMirror 6** (MIT, ~300KB): its `Diagnostic{from,to,severity,message}` maps 1:1 onto our lint records; preview reuses our own renderer via `data-line` scroll sync — never a second markdown engine. External-editor-plus-watch is a first-class peer path; server-rendered textarea + lint list is the no-JS floor. CM6 plumbing in Phase 5; full authoring surface in Phase 11. |
| Q3 | One `LESSON-STYLE.md` with a prose voice zone (model reads) and a `## Rules` pipe table (linter parses) so contract and config cannot drift. **18 machine-checkable rules (8 errors, 10 warnings) vs 5 model-judged** (`manual` severity, Phase 11 report-only). A rule row claiming lintable severity the linter doesn't implement is itself a lint error. |
| Q4 | D1: `## TERMS` + `[[term]]`, Popover-API render, glossary-appendix no-JS fallback, runtime `glossable()` gate so a gloss never leaks a keyed answer, `term_lookup` events. D2: `[!KEY]` GitHub-compatible callout with minted `[ID:]`/`[HASH:]`, `#guid` Anki TSV round-trip, `{{cloze}}`, `key_review` events replayed into FSRS state. D3: as Q3. All additive; ~20 new lint codes. |
| Q5 | `[SRC: <source-id> <locators>]` + `[OBJ: framework/objective-id]` resolved through an additive `## SOURCES` registry; coverage map computed, never stored. Paraphrase lint is pure-stdlib winnowing (~70 lines): error at ≥8 consecutive copied words, warn at Jaccard >0.25; fingerprints only, source text never stored (right legal posture for AAOS-derivative content). |
| Q6 | EMT: 2026 NREMT TEI widgets already map to our six types; the real gap is a `## SCENARIO` phased container where the **runtime stages the information reveal**. Math: WeBWorK-style random-point numeric equivalence in ~200 stdlib lines; sympy later behind the same accept rule; skip Desmos/GeoGebra (licensing), extend our 6.1 SVG protocol. CS: `check` needs stdin/stdout cases + function-signature harness mode; Parsons = `build` as convention; execution stays daemon-side. |
| Q7 | Yes — one optional ignorable `key=value` meta field on TERMS (`zh=…`). The fork to a separate codebase happens only when un-authored running prose must be tappable with tracked word status (tokenization + lemma + word-state store = LingQ's whole product). Reserve the field in 03.1; build nothing (backlog 999.2). |
| Q8 | **Keep the Python runtime.** Tauri 2.x shell + PyInstaller-onedir sidecar + existing localhost HTTP as IPC; NSIS installer + signed `tauri-plugin-updater` from the same GitHub Releases the Phase 2.1 updater uses. Porting would temporarily create two scorers — the forbidden anti-pattern. Electron is the named Linux fallback. ~25–45 MB installer. Top risks: AV false positives on frozen Python, sidecar lifecycle/ports, Linux WebKitGTK. |
| Q9 | Wrong assumptions named: the bottleneck is content + adherence, not features; consumption is phone/audio-shaped while the desktop app optimizes the authoring surface; "Phase 11 is late" conflates the risky auditor with the safe human-approved generation loop; no success criterion anywhere measures actual use. |
| Q10 | **Pull a thin seeding loop in front of Phase 5** — Anki `.apkg` import (stdlib-readable ZIP+SQLite) plus a human-approves-everything draft→lint→retry generation loop, as a widened 03.2. Seeding is upstream of everything; every later phase becomes dogfoodable against real content. |

### 7.3 Visual direction (adopted proposal)

**"Paper & Ledger" — typography encodes authority.** Authored content speaks in
a vendored serif (Source Serif 4, OFL); everything the runtime asserts —
verdicts, tiers, evidence, status — speaks in a duospace "ledger" voice (iA
Writer Quattro, OFL); UI chrome stays system-ui; a model gets no voice of its
own (generated text renders in plain chrome inside its labeled container). The
core guarantee becomes visible on every screen; no studied competitor does
this. Extends Phase 4 tokens (`--font-paper/--font-ledger/--font-chrome/--font-code`,
`text-lesson 18/1.65`, `measure-prose 66ch`, completes `--unknown/--pending/--warn-bg`);
`theme.py` stays the single palette source; offline/no-font degrades to today's
look exactly. Locked hint tiers render as dashed-border "Locked by session
mode" cards — structural refusal made visible (anti-Khanmigo). Rejected: 
celebration motion, dopamine palettes, skeleton loaders.

### 7.4 Blind-spot dispositions

| # | Disposition | Owner |
|---|---|---|
| B1 | **Roadmap-changing.** Widen 03.2 into "Seeding, Import & Provenance," land before Phase 5: Anki import ~1 plan, human-gated generation loop ~2 plans. Auditor/autonomy stays in Phase 11. | 03.2 (widened) |
| B2 | Real need, descope native apps (iOS forbids the Python sidecar). Answer: responsive pages over `--lan` (shipped Phase 2) + Tailscale recipe + exports; written rationale. | CONVENTION + docs |
| B3 | Real, cheap, differentiating: `itembank export audio` — stem→pause→key→why drill packs per objective; engine is config (edge-tts now, Piper local, Kokoro on the 7900 XTX); playback = any podcast app. ~1–2 plans. | New small insert near 9/10 |
| B4 | Cheap print CSS + PDF-via-browser export. | 03.1 render pass |
| B5 | Empty states as copyable CLI commands (visual-design artifact). | Each surface's phase |
| B6 | Grep-grade local search route over banks/lessons/attempts. | Phase 9 or 10, small |
| B7 | Backup = documented copy story + export completeness; "one writing home" convention (see M1). | CONVENTION, Phase 2.1 docs |
| B8 | WaniKani-style named stages + terminal "retired" state: legible non-punitive motivation; jpdb-style blueprint-weighted due ordering. | Phase 10 |
| B9 | Defer OCR; photograph→model→draft loop rides the 03.2 generation path later. | Backlog |
| B10 | Explicitly descope handwriting/stylus. | Recorded descope |
| B11 | **Elevate.** `[CASE:]` grouping (additive) + exam-sim preset; NREMT TEIs already map to our types. | Phases 6/7 preset + 03.2 format |
| B12 | Already owned (banks in git); surface diffs in authoring UI. | Phase 11 |
| B13 | Dyslexia-font research is negative; ship measure/spacing controls instead. | Covered by direction |
| B14 | Already designed (UI-SPEC degraded states). | Phase 8 |
| B15 | **Time-critical:** latency/duration fields must land with Phase 6's response events — append-only history can never backfill them. | Phase 6, non-deferrable |

New blind spots added (see artifact §new): the sharpest is **M1 — the coming
7900 XTX machine makes multi-machine evidence forking a real corruption risk;
adopt a "one writing home" convention now.**

### 7.5 What §2 missed (landscape)

No sequencing-engine category and no medical-education category — the most
directly applicable missed industry for an EMT-first product. Top additions:
**ALEKS** (fringe-based selection: only serve objectives whose prerequisites
are mastered — Phase 7 gets a correctness principle; needs additive `PREREQ`
edges), **UWorld** (mandatory one-sentence lintable **Educational Objective**
per item — cheapest high-leverage format addition found; feeds selection,
dedup, Anki export, and the auditor), **Amboss** (two-level gloss = direct D1
prior art), **2025 study-mode wave** (Socratic tutoring is commoditized at the
prompt layer, so D4's runtime lock must be *visible* UI state: "Tier 3 unlocks
after another attempt," never first-person model reluctance), **WaniKani/jpdb**
(named stages, terminal burn state, utility-weighted scheduling). Standards
verdict: skip QTI/LTI/LRS; keep Anki TSV + JSON; align evidence field names
with xAPI vocabulary for a free future export. SiYuan's kernel-behind-webview
architecture is shipping proof of the Q8 sidecar pattern.

### 7.6 Phase assignments (supersedes §5 where they differ)

| Phase | Now absorbs |
|---|---|
| 03.1 (INSERT) | D1 TERMS/gloss gate, D2 [!KEY]/Anki ids, D3 LESSON-STYLE.md + 18 lint rules, Q1 lesson display, print CSS, UWorld Educational-Objective line, bilingual field reserved, Paper & Ledger font vendoring |
| 03.2 (INSERT, **widened + moved before Phase 5**) | Q5 [SRC:]/[OBJ:]/## SOURCES + paraphrase lint, B1 Anki .apkg import, human-gated draft→lint→retry seeding loop, `[CASE:]` format, PREREQ edges |
| 5 | CM6 integration + vendoring pipeline, check-type stdin/stdout + harness mode, runnable-block presentation |
| 6 | Hint/refusal copy (runtime-lock visible, Khanmigo redirect formula), **B15 latency/duration evidence fields (non-deferrable)**, exam-sim feedback preset |
| 6.1 | Keep SVG protocol; extend with 2–3 math scene types; Desmos/GeoGebra rejected on licensing |
| 06.2 (INSERT) | Executable-textbook loop: prose → inline check → spaced re-exposure |
| 7 | ALEKS fringe selection over PREREQ edges; blueprint-weighted ordering; `[CASE:]`/exam-sim serving |
| 8 | Study-mode-wave refusal UX; typed provenance display (already contracted) |
| 9 | ## SCENARIO staged reveal (EMT), numeric-equivalence accept rule (Math), audio export insert nearby, search route |
| 10 | FSRS from replayed `key_review` events; WaniKani stages + retired state; jpdb utility weighting |
| 11 | LESSON-STYLE enforcement (manual rules), auditor over 03.2's computed coverage map, full CM6 authoring surface, autonomy ladder |
| Packaging (NEW number — slot 12 is retired) | Tauri 2.x + PyInstaller-onedir sidecar, NSIS, signed updater, AV/signing checklist; Linux deferred to hardware |
| 999.2 (BACKLOG) | Bilingual reader beyond the TERMS field |

### 7.7 Open rulings for Weibao

1. Adopt "Paper & Ledger" and vendor the two OFL faces? (Degrades cleanly; license review per the KaTeX pattern.)
2. 18px lesson-reader body vs the locked 16px `text-body` token.
3. Confirm Q8: keep Python, Tauri sidecar, NSIS — and assign the new packaging phase number.
4. Approve widening/moving 03.2 (the B1/Q10 seeding pull-forward) — the single biggest roadmap change.
5. CM6 also replacing the learner-facing textarea CodeEditor contract in UI-SPEC §4, or authoring-only.
6. Confirm "The Bottom Up" = Wienand-style runnable-artifact-first pedagogy (assumption logged in the subjects artifact).
