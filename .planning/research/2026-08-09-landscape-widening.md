---
date: 2026-08-09
topic: Competitive/inspiration landscape widening beyond RESEARCH-BRIEF section 2
brief: .planning/RESEARCH-BRIEF-learning-platform-2026-08-09.md (sections 1-3 binding)
confidence:
  sequencing-engines: HIGH (multiple independent sources incl. official docs and peer-reviewed KST paper)
  medical-education: HIGH (official Amboss/Sketchy pages; UWorld structure cross-checked across reviews)
  cs-practice: MEDIUM (official Exercism/CodeCrafters pages; pedagogy claims from secondary sources)
  srs-deep-cuts: MEDIUM (WaniKani official docs HIGH; Bunpro/Clozemaster details ASSUMED from training)
  ai-tutors-2025-2026: MEDIUM (launch facts multi-source; exact refusal copy is quoted secondhand)
  local-first-pkm: MEDIUM (SiYuan architecture from repo docs; Anytype ASSUMED)
  open-standards: HIGH for verdict (adoption numbers cited; QTI complexity from 1EdTech's own post)
  novel-2025-2026: LOW-MEDIUM (trend reporting, fast-moving)
valid_until: 2026-09-09 (ai-tutor section: 2026-08-23, fast-moving)
---

# Landscape Widening — What Section 2 Missed and What to Take

Section 2 of the brief covers executable textbooks, SR-native authoring, gloss
readers, three AI tutors, editors, typography, math/diagrams, and packaging.
It has **no category for sequencing engines, no medical-education products at
all** (despite EMT being the first subject), no SRS UX above the FSRS math, a
pre-2025 AI-tutor list, no standards question, and no exam-fidelity prior art.
This document widens all of it. Every entry: what it is → the ONE pattern worth
taking → why it works → cost → phase → FORMAT/RENDERER/RUNTIME/PACKAGING/CONVENTION.

Non-negotiables honored throughout: runtime gates the learner; one parser/scorer/
evidence store; evidence on disk; additive format; accessibility gates; no
punitive gamification.

---

## 1. Structured Self-Study Sequencing Engines

The brief's biggest structural gap: Phase 7 (Selection Engine) has zero prior
art in section 2. This is the category that owns it.

### Math Academy
- **What:** Mastery-based math system: adaptive diagnostic → knowledge graph →
  algorithm picks ~5 tasks/day → XP per task → spaced-repetition quizzes kick in
  within a week. [CITED: mathacademy.com/how-it-works; nor-blog review; Matuschak notes]
- **ONE pattern:** **The short pre-decided menu.** The learner never browses the
  graph; the dashboard shows ~5 tasks the algorithm already chose as optimal,
  and picking among them is the only choice. Autonomy without decision fatigue.
- **Why it works:** Removes the "what should I study" metacognitive tax — the
  single biggest self-study failure mode — while a small menu preserves agency.
  XP is an *effort meter* (roughly minutes of productive work), not a leaderboard.
- **Cost:** Selector returns a ranked shortlist instead of one item; day surface
  renders it. Small — the selection logic is the phase anyway.
- **Phase:** 7. **Tag:** RUNTIME (+ RENDERER for the day-surface menu).

### ALEKS (Knowledge Space Theory)
- **What:** McGraw Hill adaptive system built on 30 years of peer-reviewed KST:
  a knowledge state is the exact set of mastered problems; the engine computes
  the "outer fringe" — topics whose prerequisites are all mastered — and serves
  only those. [CITED: aleks.com/about_aleks/knowledge_space_theory; Matayoshi et al. JMP 2021]
- **ONE pattern:** **Fringe-based readiness.** Never serve an item whose
  prerequisites are unmastered; never re-serve deep inside the mastered set.
  "Ready to learn" is a computable set, not a heuristic.
- **Why it works:** Failure on an item you lack prerequisites for produces
  noise, not signal, and demoralizes. Fringe selection keeps every attempt
  informative and every success earned.
- **Cost:** Needs prerequisite edges between objectives. Additive bank/plan
  metadata (`PREREQ:` on objectives or a small objectives file) + a set
  computation in the selector. Moderate; the authoring cost is the real cost,
  and the Phase 11 auditor can flag missing edges.
- **Phase:** 7 (selector), 03.2 (edges live beside the objective coverage map).
  **Tag:** RUNTIME + FORMAT.

### DreamBox (Intelligent Adaptive Learning)
- **What:** K-8 math that adapts *within* a lesson based on the strategy a
  student used — manipulative choices, error patterns, decision sequences —
  not just right/wrong. [CITED: dreamboxlearning.zendesk.com "How Does DreamBox Math Work"]
- **ONE pattern:** **Score the how, not only the what.** Two correct answers can
  reflect different depths of understanding; the evidence record should carry
  *which* wrong option, time-on-item, and hint tier consumed — and the selector
  should read them.
- **Why it works:** Correctness alone under-measures. A learner who needed tier-3
  hints "passed" differently than one who answered cold; treating them the same
  mis-schedules both.
- **Cost:** We already record answer + score; add hint-tier-consumed and elapsed
  time to the evidence row (additive JSON fields). Selector weighting is Phase 7
  logic. Small. Full within-item strategy detection is NOT worth copying — it
  requires instrumented manipulables per item.
- **Phase:** 6 (hint tier lands in evidence), 7/10 (selector/scheduler read it).
  **Tag:** RUNTIME.

### Mathigon Polypad
- **What:** The most comprehensive virtual-manipulatives library on the web —
  50+ manipulative types (algebra tiles, fraction bars, geometry) on one shared
  canvas. [CITED: polypad.amplify.com; mathigon.org]
- **ONE pattern:** **Manipulatives as a shared component library**, not bespoke
  per-item canvases. Every manipulable item type draws from one small vocabulary
  of interaction primitives with one accessibility story.
- **Why it works:** Learners transfer fluency with the tool across items;
  authors compose rather than build; the semantic-equivalent-beside-visual gate
  is solved once per primitive instead of once per item.
- **Cost:** Phase 6.1 already scopes visual assessment; this is a design
  constraint on it, nearly free if adopted now, expensive to retrofit.
- **Phase:** 6.1 / 9 (Math profile). **Tag:** RENDERER.

### Smartick
- **What:** Children's math program whose signature is a hard **15-minute daily
  session cap** — the system ends the session, not the learner. [ASSUMED — training
  knowledge; verify session length on smartick.com before citing in copy]
- **ONE pattern:** **The system ends the session.** A positive adherence
  mechanism (B8) that is the structural opposite of streak guilt: short daily
  contact the runtime enforces by stopping, not by shaming.
- **Why it works:** Ending on time (often on a success) preserves tomorrow's
  motivation; caps are anti-burnout and Duolingo-inverse.
- **Cost:** Session mode already exists; a soft "good stopping point" banner is
  a day/quiz-surface affordance. Trivial.
- **Phase:** 10 (pacing). **Tag:** CONVENTION.

---

## 2. Medical / Clinical Education

Section 2's most surprising omission given EMT is the first subject. This is
the industry that writes the best rationales and built D1 before we named it.

### UWorld — the rationale gold standard
- **What:** The QBank every US medical/nursing student treats as the primary
  *learning* resource, not just practice: many students study by reading
  explanations in untimed mode. [CITED: uworld.com; multiple 2025-26 reviews]
- **Explanation anatomy (study this, it is the spec for ours):**
  1. Rationale for the correct answer — mechanism first, then clinical reasoning;
  2. **A specific reason each distractor is wrong** — every one, no skipping;
  3. A custom illustration/flowchart where the concept is visual;
  4. A closing one-sentence **"Educational Objective"** — the single takeaway
     the item exists to teach. [VERIFIED: structure cross-checked across
     medboardtutors.com, scrubscommunity.com, katalystprep.com reviews]
- **ONE pattern:** **The mandatory Educational Objective sentence.** We already
  have per-distractor DA (UWorld's #2) in the format; the missing piece is the
  one-liner that names what the item teaches — which is also exactly what the
  selector, the coverage auditor, and the Anki export want as a card front/back
  seed.
- **Why it works:** Forces the author (human or AI) to know why the item exists;
  gives the learner a compressed retrieval cue; makes "two items teach the same
  thing" machine-detectable.
- **Cost:** One additive field (`OBJ-SENTENCE:` or reuse/extend `why`), one lint
  rule (present, one sentence, no letter references). Small.
- **Phase:** 03.1 format + 11 lint (LESSON-STYLE.md should mandate it).
  **Tag:** FORMAT + CONVENTION.

### Amboss — D1's direct prior art
- **What:** Qbank + 25k-source medical library, fully integrated: while
  answering, hover any highlighted term → concise definition; click → the full
  library article opens side-by-side without leaving the session. Extends into
  Anki (add-on) and the whole web (Chrome extension). [CITED: amboss.com/us/anki, amboss.com/us/chrome]
- **ONE pattern:** **Two-level gloss: hover snippet → click-through to the
  canonical article section.** The tooltip is a teaser; the term's real home is
  a `## LESSON` anchor, and the gloss carries the link. Community even built a
  "require click for tooltip" Anki add-on — reveal-on-intent matters to real
  users. [CITED: ankiweb.net/shared/info/354696931]
- **Why it works:** Reinforces reasoning at the moment of need without context
  switch; the same term object serves item, lesson, and export — which is D1's
  thesis, now with proof the market wants it.
- **Cost:** D1 is already scoped; this adds "gloss must link to lesson anchor"
  and an optional side-panel render. Small increment on 03.1.
- **Phase:** 03.1. **Tag:** RENDERER + FORMAT (anchor link in `## TERMS`).

### Sketchy — visual mnemonics as content
- **What:** Method-of-loci videos: symbols for facts placed in a persistent
  scene; fMRI and meta-analytic evidence supports loci over rote for serial
  recall. [CITED: sketchy.com/blog "visual memory and elaborative encoding"; PubMed 33535926]
- **ONE pattern:** **Mnemonic as a first-class optional field**, not prose
  buried in a rationale. A `MNEMONIC:` line on an item or term renders as its
  own styled block, exports to the Anki card, and the lesson voice contract can
  regulate its register.
- **Why it works:** Elaborative encoding with spatial/visual hooks measurably
  beats rote for list-heavy material — EMT protocols and drug lists are exactly
  that shape.
- **Cost:** One additive field + one render style + Anki column. Trivial. (We do
  text mnemonics; Sketchy's illustrated scenes are out of scope.)
- **Phase:** 03.1 (format/render), 10 (enters review queue via D2 path).
  **Tag:** FORMAT.

### AnKing / med-school Anki ecosystem
- **What:** The de-facto-standard community deck for USMLE; its real innovation
  is a maintained **hierarchical tag taxonomy** — students don't study linearly,
  they filter by tags synced to their curriculum block. Image occlusion is the
  gold standard for anatomy/diagram recall. [CITED: studycardsai.com guides; zhighley.com]
- **ONE pattern:** **Tags are the curriculum sync layer.** Our objective
  coverage map (03.2) should emit/consume a hierarchical tag scheme
  (`emt::airway::obstruction`) that flows through to Anki TSV export, so the
  bank, the selector, and the exported deck all filter by the same taxonomy.
- **Why it works:** Decouples authoring order from study order; makes "study
  what this week's block covers" a query, not a re-authoring job.
- **Cost:** Tag column in export + convention doc. Small. Image occlusion as an
  item type: real but heavy (image pipeline, occlusion editor) — backlog with
  999.1 visual items.
- **Phase:** 03.2 + 2.1 export surface. **Tag:** CONVENTION + FORMAT.

### NREMT-specific prep (Pocket Prep, Limmer, MedicTests)
- **What:** Commodity qbanks differentiated by (a) alignment to the NREMT
  blueprint domains (airway/respiration, cardiology, medical, trauma, EMS
  operations), (b) mock exams shaped like the real (adaptive, ~60-110 item)
  test, and (c) a per-domain **readiness/confidence projection**. [CITED: app-store
  listings, community roundups; the "Exam Readiness Score" branding is Pocket
  Prep's — ASSUMED on exact name]
- **ONE pattern:** **Blueprint-weighted readiness.** Store the official exam
  blueprint (domains + weights) as data; report evidence against it; the
  coverage auditor answers "am I NREMT-shaped ready," not just "what % correct."
  Directly answers blind spot B11.
- **Why it works:** Training distribution should match test distribution;
  every serious exam-prep product converges on this because generic accuracy
  over-weights whatever the bank happens to contain.
- **Cost:** A blueprint file (markdown table, additive), domain tags on items
  (the AnKing taxonomy above), a report view. Moderate-small.
- **Phase:** 03.2 (blueprint as data) + 10 (readiness trend) + 9 (EMT profile).
  **Tag:** FORMAT + RUNTIME.

(Osmosis reviewed: video platform with built-in SRS; nothing it does that
Amboss+Anki don't do better for our shape. No pattern taken.)

---

## 3. CS Practice

### Exercism
- **What:** Free practice tracks with async human mentoring: solve locally →
  tests pass → submit → mentor comments → iterate. [CITED: exercism.org]
- **ONE pattern:** **Iteration after passing.** The loop's genius is that
  feedback arrives on a *working* solution — "it works; now make it better."
  For us: after a correct answer, the tutor may offer an optional deepening
  pass ("your loop is O(n²); can you see why?") — runtime-gated like everything
  else, and only ever *after* the verdict.
- **Why it works:** Feedback on working code is received as craft, not rescue;
  zero answer-leak risk because the answer already happened.
- **Cost:** A post-verdict tutor mode flag; no new scorer. Small.
- **Phase:** 6 (mode) / 8 (model call). **Tag:** RUNTIME + CONVENTION.

### NeetCode / LeetCode pattern curricula
- **What:** 150-problem roadmap organized so problems within a category build
  on one another; the thesis is ~20 reusable patterns cover most problems.
  [CITED: neetcode roadmap coverage; educative.io/blog/neetcode-roadmap]
- **ONE pattern:** **Pattern tags + interleaved pattern practice.** Tag CS items
  with the technique they exercise (two-pointer, accumulation, recursion base
  case…); the selector interleaves across patterns; "which pattern applies?" is
  itself an askable mc item generated from the tag.
- **Why it works:** Interleaving by underlying structure (not surface topic) is
  the strongest transfer result in the practice literature; patterns are the
  right granularity for CSCI 1100 problem solving.
- **Cost:** A tag vocabulary per subject profile + selector awareness. Small.
- **Phase:** 9 (CS profile), 7 (interleave). **Tag:** FORMAT + RUNTIME.

### CodeCrafters
- **What:** "Build your own Redis/Git/SQLite" — one project, ordered stages,
  each stage gated by automated checks. [CITED: codecrafters.io via exercism.org/partners]
- **ONE pattern:** **Staged project = chained check items.** A sequence of
  check-type items sharing one workspace, each unlocking the next — the
  "bottom-up CS style" Weibao named, expressible in our existing session model
  (ordered items, cursor) with a persistent scratch dir.
- **Why it works:** Milestone visibility converts a big build into a ladder of
  small wins; every stage is objectively testable, which suits our one-scorer rule.
- **Cost:** Shared-workspace semantics for check items; moderate. Design in
  Phase 5, ship the chaining in 9.
- **Phase:** 5 (check item design) / 9. **Tag:** FORMAT + RUNTIME.

### SQLZoo / Regex Crossword micro-drills [ASSUMED — training knowledge]
- **ONE pattern:** **The sub-30-second drill rep.** Tiny input, instant verdict,
  dozens of reps a session. A "drill mode" over check/mc items with a stripped
  UI (no lesson, no explanation until the set ends) is a different consumption
  mode of the same items — end-of-set review preserves the no-leak rule.
- **Phase:** 9/10. **Tag:** CONVENTION (mode, not new type).

### Zed / Warp editor UX
- **What:** Warp renders every command+output as a navigable, bookmarkable
  **block**; both are keyboard-first with a universal command palette.
  [CITED: warp.dev/modern-terminal; zed.dev/docs]
- **ONE pattern:** **Session-as-blocks.** Render an attempt review as blocks —
  item, answer, verdict, hints consumed, explanation — each addressable,
  collapsible, linkable. Our append-only evidence store is already block-shaped;
  this is its natural UI. Second (cheap): a command palette across all surfaces.
- **Why it works:** Blocks make history scannable and referenceable ("the
  airway question I missed Tuesday" is a link, not a memory).
- **Cost:** Report/study surface render pattern; palette is a shell feature on
  Phase 4's shipped tokens. Moderate-small.
- **Phase:** 10 (trends/report render); palette can ride any surface phase.
  **Tag:** RENDERER.

---

## 4. Language/SRS Deep Cuts — What They Teach Phase 10 Beyond FSRS Math

### WaniKani
- **What:** Kanji SRS with named stages — Apprentice (4h/8h/23h/47h) → Guru
  (1w/2w) → Master (1mo) → Enlightened (4mo) → **Burned** (retired forever) —
  and house-voice mnemonics for every character. [CITED: knowledge.wanikani.com/wanikani/srs-stages]
- **ONE pattern:** **Named stages + a terminal "burned" state.** Two ideas:
  (a) show the learner a *name*, not an interval — "Guru" communicates standing;
  raw "due in 13.2 days" communicates nothing; (b) items can *graduate out of
  the queue entirely*. Retirement is the strongest non-punitive motivator in
  the SRS world: the pile visibly shrinks forever.
- **Why it works:** Legible progress states give the scheduler a narrative;
  burn gives it an ending. Anti-treadmill, which is our anti-punitive mandate
  in mechanism form.
- **Cost:** Naming layer over FSRS stability thresholds + a retirement rule.
  Small. (Also: their mnemonic *voice* — consistent, irreverent, second-person —
  is prior art for LESSON-STYLE.md's register section.)
- **Phase:** 10. **Tag:** CONVENTION + RENDERER.

### jpdb.io
- **What:** SRS whose scheduler is frequency-aware: words are prioritized by
  how often they occur in the specific media you're about to consume; the
  algorithm models the full forgetting curve from review history. [CITED: jpdb.io/faq]
- **ONE pattern:** **Utility-weighted scheduling.** Due date is not the only
  sort key — multiply by the item's weight in the target corpus. For us the
  "corpus" is the NREMT blueprint / course syllabus: two items equally due,
  the one in a heavier blueprint domain surfaces first.
- **Why it works:** SRS optimizes memory per review; utility weighting
  optimizes *exam outcome* per review. Different objective, better fit.
- **Cost:** A priority multiplier in the Phase 10 queue fed by 03.2 blueprint
  weights. Small once weights exist.
- **Phase:** 10 (consumes 03.2). **Tag:** RUNTIME.

### Bunpro [ASSUMED — training knowledge; verify before quoting]
- **ONE pattern:** **Ghost reviews:** a failed item spawns temporary extra
  reviews that shadow the main schedule until re-stabilized, then vanish.
  FSRS post-lapse stability covers the math; the UX idea is that *lapses get a
  visibly separate, visibly temporary track* so the learner sees the system
  responding to the miss. **Phase:** 10. **Tag:** CONVENTION.

### Clozemaster [ASSUMED — training knowledge]
- **ONE pattern:** **Cloze-in-context as the review form.** Review a fact
  inside the sentence it lives in, not as an isolated Q/A pair. For us: a
  `[!KEY]` block reviews as a cloze *of itself* — the block is the context,
  one masked span per review. Strengthens D2: one authoring act now yields
  styled block, Anki card, and in-app cloze review. **Phase:** 03.1 grammar +
  10 review mode. **Tag:** FORMAT + RENDERER.

(Migaku already in brief section 2; nothing new taken.)

---

## 5. AI-Tutor Products 2025-2026 — Refusal and Hint Pacing

The landscape moved under the brief: between July and August 2025 **every**
major lab shipped a Socratic study mode — OpenAI Study Mode (2025-07-29),
Google Gemini Guided Learning on LearnLM (early Aug 2025), Anthropic Learning
Mode for Claude.ai and Claude Code (2025-08-14 GA). [CITED: morningbrew 2025-07-31;
securityonline.info; winbuzzer 2025-08-14] Duolingo made Explain My Answer free
to all users 2026-01-01. [CITED: blog.duolingo.com/explain-my-answer-now-free]

**Strategic implication:** "has a tutor that won't just answer" is now table
stakes. All of them enforce it with a system prompt; all are therefore
arguable-with (press coverage of Study Mode notes students "can still easily
cheat" by leaving the mode). Our D4 structural gate is the differentiator —
but only if the UI makes the mechanism *visible*.

### Refusal copy — what the best of it does
- **Khanmigo** (still the best-documented copy): asked "Give me the answer,"
  it replies **"Hey, I'm here to help you. I'm your tutor. What do you think
  the next step is?"** or **"How do you want to approach this question?"**
  [CITED: CBS 60 Minutes transcript via cbsnews.com] — Formula: warm
  acknowledgment → role restatement → redirect to a question the learner CAN
  answer. Never "I can't," never policy language, never a lecture on academic
  integrity.
- **ChatGPT Study Mode:** refuses the direct ask, then immediately asks a
  smaller diagnostic question — the refusal is *replaced by* a next step, not
  followed by silence. [CITED: eesel.ai study-mode writeup]
- **Duolingo Explain My Answer:** the inverse lesson — explanation is
  **post-verdict and learner-pulled** (a button, not a push), delivered "at the
  moment when learners are most receptive, immediately after the error."
  [CITED: blog.duolingo.com]
- **ONE pattern (for Phase 6/8):** **Refusal = redirect + visible mechanism.**
  Copy follows Khanmigo's three-part formula, and — our structural advantage —
  the UI shows the gate as state: the hint-tier ladder with locked rungs, and
  copy that says *"Tier 3 unlocks after another attempt"* / *"Reveal is locked
  in exam mode"* rather than first-person model reluctance ("I can't tell
  you"). The model is never the one refusing, and the copy should never
  pretend it is: the runtime is, and honestly saying so is both truthful and
  argue-proof. Post-verdict, add a Duolingo-style learner-pulled "explain my
  answer" affordance.
- **Cost:** Copywriting + tier-ladder UI on existing gate state. Small.
- **Phase:** 6 (ladder UX + copy), 8 (adapter surfaces gate state to the model
  so it narrates truthfully). **Tag:** RENDERER + CONVENTION.

---

## 6. Local-First / PKM Adjacents

### Obsidian SR plugins / Logseq flashcards
- **What:** Logseq: any block becomes a flashcard natively (SM-5-era algorithm);
  Obsidian: plugin-assembled SRS with `::`-style inline card syntax; both suffer
  the same split — cards and prose drift, and plugin stacks demand maintenance.
  [CITED: fabric.so and knodegraph comparisons; obsidian forum threads]
- **ONE pattern:** Mostly **validation of D2/D6**: block-as-card in plain
  markdown is what users of both keep trying to assemble from parts; we ship it
  with a scorer and a scheduler attached, which neither has. The takeable
  detail: Obsidian's `front :: back` inline syntax is the ergonomic floor for
  quick memorizables — worth supporting inside `[!KEY]` blocks as shorthand.
- **Phase:** 03.1. **Tag:** FORMAT.
- **Anti-lesson:** plugin-assembled learning stacks decay. Ship the whole loop
  in-product; do not build a plugin API for the core loop.

### SiYuan
- **What:** Local-first notes app: TypeScript frontend + **Go kernel as a
  separate process**, packaged with electron-builder on desktop and gomobile on
  mobile. [CITED: deepwiki.com/siyuan-note/siyuan build docs]
- **ONE pattern:** **Shipped proof of the sidecar architecture.** A web
  frontend talking HTTP to a native-language kernel process, packaged as one
  desktop app, is exactly the "keep the Python runtime, add a real frontend
  under Tauri" recommendation in brief §1 — SiYuan is evidence it holds up in
  production across platforms.
- **Why it matters:** De-risks the Phase 12 decision; also a warning from the
  same research: Electron→Tauri migration later "is closer to a rewrite than a
  refactor" [CITED: codecentric.de comparison] — pick the shell once.
- **Phase:** 12. **Tag:** PACKAGING.

### Anytype [ASSUMED — training knowledge]
- Object-model everything + CRDT sync machinery. The sync machinery is the
  product and the burden; we have no sync, deliberately. Nothing taken except
  the reminder that **backup (B7) is the local-first tax**: a one-command
  zip-export of banks+evidence is the honest replacement for sync. **Phase:**
  2.1/12. **Tag:** RUNTIME.

---

## 7. Open Standards — Verdict

| Standard | What | Verdict | Why |
|---|---|---|---|
| **QTI 3.0** | 1EdTech item/test interchange XML (web-component-friendly since 3.0) | **No.** | Built for vendor↔LMS interop with a conformance/certification program; 2.2 was admitted-by-1EdTech too complex and 3.0 is still a vendor spec [CITED: 1edtech.org "Finally Final: The QTI 3.0 Release"]. Our markdown IS the format contract; a second parser violates the one-parser rule. |
| **xAPI / cmi5** | Actor-verb-object learning-record statements + LRS | **No LRS; steal the vocabulary.** | Adoption ~17% (2022), stalled on "complexity, cost, lack of guidance"; cmi5 is 0.2% of SCORM Cloud imports [CITED: xapi.com adoption posts]. But the statement shape (actor/verb/object/result/context, ISO timestamps) is a good discipline for our append-only evidence JSON — name fields compatibly and a future `export --xapi` is a mapping, not a migration. |
| **Caliper** | 1EdTech analytics telemetry | **No.** | It is a telemetry spec; we forbid telemetry. |
| **LTI** | LMS tool launch/grade passback | **No.** | One learner, no institution. Canvas integration already parked in 999.1; LTI would only matter there. |

**Conclusion: Anki TSV + JSON is enough.** One cheap action now: align evidence
field naming with xAPI verb/result vocabulary (verbs like `answered`,
`experienced`; result `{score, success, duration}`). Cost: a naming review in
the next evidence-touching phase. **Phase:** 10 (evidence fields) / 2.1 (export
later, optional). **Tag:** CONVENTION.

---

## 8. Genuinely Novel 2025-2026 UX (No Brief Category)

1. **AI-generated course-on-demand apps** (Morso, Chunks, NerdSip — the
   fastest-growing microlearning category in 2026 [CITED: morso.app / chunks.app
   roundups, LOW confidence on category framing]). Generate a course on any
   topic instead of shipping a catalog. **Matters to us — this is the B1 cold
   start answer:** first-run flow = "point me at a syllabus/textbook chapter →
   generate a draft bank → lint gates it → you review the diff in git." Their
   weakness (unreviewed generated slop) is exactly what our linter + provenance
   tags + git-diff review fix. **Phase:** 11, but pull a thin slice into the
   first-run story (B5). **Tag:** RUNTIME + CONVENTION.
2. **Study modes as an OS-level default** (covered in §5): being "the tutor
   that won't reveal" is commoditized at the prompt layer; the runtime-enforced
   version must be *demonstrably* different in UI. **Phase:** 6/8 messaging.
3. **Depth-over-catalog turn:** 2026 microlearning coverage converges on
   "fewer, better-crafted lessons" (Brilliant, Chunks) [CITED: chunks.app blog,
   LOW]. Validates one-idea-per-screen and our small hand-tended banks; no work.
4. **Block-based session transcripts** (Warp, §3): treated by devtools as the
   modern replacement for scrollback soup; no learning product does it yet for
   *attempt history*. Cheap differentiation for our report surface. **Phase:** 10.
5. **Not-novel-but-newly-loud:** scroll-feed "TikTok learning" interfaces and
   AR/3D lesson gimmicks appear in every 2025-26 trend list [CITED: lollypop/
   thefinch trend posts, LOW]. Noted so we can decline them deliberately (see
   NOT-copy list).

---

## 9. What Section 2 Missed — Explicit List

1. **Sequencing engines as a category.** Phase 7 is the roadmap's most
   algorithmic phase and section 2 gave it zero prior art. Math Academy's
   short-menu, ALEKS's fringe, DreamBox's score-the-how now cover it.
2. **Medical education entirely** — for an EMT-first product. UWorld is the
   industry's best rationale writing (and our DA field's missing sibling, the
   Educational Objective sentence); Amboss had built D1 before we named it;
   Sketchy proves mnemonics are content, not garnish.
3. **Exam-blueprint fidelity** (B11 had no prior art): NREMT domain weights as
   data, readiness as a per-domain projection — every serious prep app does it.
4. **SRS UX above the math.** Section 2 says "FSRS as the Phase 10 scheduler"
   and stops. Stage names, burn/retirement, utility-weighted priority, lapse
   ghosts, cloze-in-context are the parts learners actually feel.
5. **The 2025 study-mode wave.** Brief lists Khanmigo/Synthesis/Exercism; the
   three frontier labs all shipped Socratic modes since — the competitive
   claim needs updating from "we have a tutor" to "ours cannot be talked out."
6. **Micro-drill mode** as a distinct consumption loop over existing items.
7. **The sidecar packaging precedent** (SiYuan) — §1's open recommendation had
   no shipped comparable; now it does.
8. **The standards question** — never asked; now answered (no, with one cheap
   naming alignment).
9. **Curriculum-tag taxonomy as the sync layer** (AnKing) between bank,
   selector, coverage map, and Anki export.
10. **Cold-start via gated generation** — the AI-course-generator category is
    section 2-invisible but is the shape of the B1 answer.

---

## 10. Five Patterns I Would Fight For

1. **ALEKS fringe selection on prerequisite edges** (Phase 7, RUNTIME+FORMAT) —
   the single biggest pedagogical upgrade available to the selector; everything
   else in Phase 7 is ordering, this is correctness.
2. **UWorld's Educational Objective sentence as a mandatory, lintable field**
   (03.1/11, FORMAT) — one sentence per item that improves authoring, selection,
   dedup, export, and the auditor simultaneously. Cheapest leverage in this file.
3. **Refusal = redirect + visible mechanism** (Phase 6/8, RENDERER+CONVENTION) —
   Khanmigo's warm redirect copy on top of a UI that shows the lock as runtime
   state. This is D4 made legible; it is the product's identity on screen.
4. **Named stages + burned/retired items** (Phase 10, CONVENTION) — legible
   scheduler standing and a queue that visibly ends; the non-punitive
   motivation mechanism B8 was missing.
5. **Blueprint-weighted coverage and readiness** (03.2/10, FORMAT+RUNTIME) —
   NREMT domains and syllabus weights as data, so "ready" is reported against
   the exam's shape, not the bank's shape.

## 11. Five Fashionable Things to Deliberately NOT Copy

1. **Streaks, leagues, XP leaderboards** (Duolingo, and Math Academy's league
   layer). Take Math Academy's XP-as-effort-meter at most; competition and
   guilt mechanics are banned by spec and unnecessary for one learner.
2. **Chat as the primary surface.** The 2025 study modes are chatbots wearing a
   tutor hat; a chat transcript is where session state, gating, and evidence go
   to die. Chat stays one surface among several; the runtime owns the state.
3. **Full-course AI generation without a gate.** The Morso-category ships
   unreviewed generated content at catalog scale. We generate only into the
   linter + provenance tags + git review; never straight to the learner.
4. **Standards conformance (QTI/LTI/LRS).** Vendor interop theater for a
   one-learner local tool; violates one-parser and telemetry principles for
   zero user value. TSV + JSON + xAPI-compatible naming is the whole answer.
5. **Scroll-feed microlearning and AR/3D lesson gimmicks.** The engagement
   pattern optimizes session length, not retention; our loop optimizes the
   opposite. Also declines canvas-heavy content, which our accessibility gates
   forbid anyway.

---

## Sources

**Sequencing:** [mathacademy.com/how-it-works](https://www.mathacademy.com/how-it-works) · [nor's Math Academy review](https://nor-blog.pages.dev/posts/2025-04-16-mathacademy/) · [Andy Matuschak's notes](https://notes.andymatuschak.org/Math_Academy) · [ALEKS KST](https://www.aleks.com/about_aleks/knowledge_space_theory) · [Matayoshi et al., JMP 2021 preprint](https://jmatayoshi.github.io/publications/JMP2021_KST_ALEKS_preprint.pdf) · [DreamBox how-it-works](https://dreamboxlearning.zendesk.com/hc/en-us/articles/27281843188243-How-Does-DreamBox-Math-Work) · [Polypad](https://polypad.amplify.com/)
**Medical:** [UWorld Step 1](https://medical.uworld.com/usmle/usmle-step-1/) · [MedBoardTutors UWorld review](https://www.medboardtutors.com/blog/uworld-for-usmle-step-1-honest-review-and-how-to-use-it) · [AMBOSS Qbank](https://blog.amboss.com/us/get-ready-usmle-step-exams-amboss-qbank) · [AMBOSS Anki add-on](https://www.amboss.com/us/anki) · [AMBOSS Chrome](https://www.amboss.com/us/chrome) · [Sketchy method](https://blog.sketchy.com/visual-memory-and-elaborative-encoding) · [Loci meta-analysis, PubMed 33535926](https://pubmed.ncbi.nlm.nih.gov/33535926/) · [StudyCards AnKing guide](https://studycardsai.com/blog/anki-decks-for-med-school) · [Zach Highley Anki add-ons](https://zhighley.com/article/anki-addons/)
**CS:** [exercism.org](https://exercism.org/) · [Exercism × CodeCrafters](https://exercism.org/partners/codecrafters) · [educative NeetCode roadmap](https://www.educative.io/blog/neetcode-roadmap) · [Warp modern terminal](https://www.warp.dev/modern-terminal) · [Zed vs Warp](https://www.implicator.ai/zed-and-warp-both-ship-ai-coding-they-bet-on-opposite-surfaces-2/)
**SRS:** [WaniKani SRS stages](https://knowledge.wanikani.com/wanikani/srs-stages/) · [Wanilog SRS explained](https://wanilog.com/guides/wanikani-srs-explained) · [jpdb FAQ](https://jpdb.io/faq)
**AI tutors:** [Morning Brew, Study Mode](https://www.morningbrew.com/stories/2025/07/31/chatgpt-is-shifting-into-study-mode) · [eesel Study Mode guide](https://www.eesel.ai/blog/chatgpt-study-mode) · [Gemini Guided Learning](https://securityonline.info/google-geminis-new-guided-learning-mode-aims-to-revolutionize-student-learning/) · [LearnLM](https://cloud.google.com/solutions/learnlm) · [Claude Learning Modes](https://www.datastudios.org/post/anthropic-introduces-learning-modes-in-claude-to-rival-chatgpt-and-gemini) · [60 Minutes Khanmigo transcript](https://www.cbsnews.com/news/khanmigo-ai-powered-tutor-teaching-assistant-tested-at-schools-60-minutes-transcript/) · [Khanmigo prompt engineering](https://blog.khanacademy.org/khan-academys-7-step-approach-to-prompt-engineering-for-khanmigo/) · [Duolingo EMA free](https://blog.duolingo.com/explain-my-answer-now-free)
**Local-first:** [SiYuan build/deploy (DeepWiki)](https://deepwiki.com/siyuan-note/siyuan/6-building-and-deployment) · [codecentric Electron vs Tauri](https://www.codecentric.de/en/knowledge-hub/blog/electron-tauri-building-desktop-apps-web-technologies) · [Obsidian vs Logseq](https://knodegraph.com/vs/obsidian-vs-logseq/)
**Standards:** [1EdTech "Finally Final: QTI 3.0"](https://www.1edtech.org/blog/finally-final-the-qti-30-release) · [QTI 3.0 overview](https://www.imsglobal.org/spec/qti/v3p0/oview) · [xAPI/cmi5 adoption](https://xapi.com/blog/an-exciting-time-to-watch-xapi-and-cmi5-adoption-numbers/) · [cmi5 adoption stats](https://aicc.github.io/CMI-5_Spec_Current/adoption/)
**Trends (LOW):** [Lollypop 2025 edu design trends](https://lollypop.design/blog/2025/august/top-education-app-design-trends-2025/) · [Morso microlearning roundup](https://www.morso.app/blog/best-microlearning-apps-in-2026-ranked-for-real-learners) · [Chunks roundup](https://chunks.app/blog/best-microlearning-apps-2026)
