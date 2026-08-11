---
date: 2026-08-10
topic: "R1.1 / R1.1a — the catalogue of named pedagogical formats for written lesson material, with take/fix verdicts per style and a ship/reject shortlist"
brief: .planning/RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md §2 R1.1, R1.1a (§3 rules binding)
directives: .planning/PLANNING-DIRECTIVES.md, all six sections
scope: R1.1 and R1.1a only. R1.2 (shared block vocabulary), R1.3 (style-file shape),
  R1.4 (house/style rule split), R1.5 (model consumption), R1.6 (learner choice),
  R1.7 (math form) are other slices; this artifact hands them a costed input, not an answer.
confidence:
  style_taxonomy: HIGH          # the formats are stable named things, cross-checked
  execute_program: MEDIUM-HIGH  # gating verified via Matuschak's notes; executeprogram.com is JS-rendered and returned no text to WebFetch
  brilliant: MEDIUM             # lesson shape from secondary reviews + official About page; no primary authoring doc is public
  runestone: HIGH               # official author guide + overview book
  math_academy: HIGH            # official how-it-works + Skycak interview + independent reviews
  bottom_up_wienand: MEDIUM     # book and its stated approach verified; it is a book, not a product, so "what it gets wrong" is my reading
  case_based_medical: HIGH      # peer-reviewed scoping reviews on unfolding / progressive-disclosure cases
  primm: HIGH                   # ACM papers + Sentance/Waite provenance
  productive_failure: HIGH      # Kapur 2014 Cognitive Science; Sinha & Kapur 2021 RER meta-analysis
  explorable_explanations: MEDIUM # Victor's essay primary; the negative evidence is a real but thin literature
  feynman: LOW-MEDIUM           # no primary pedagogy source exists; it is folk method, and that is itself the finding
  cookbook_diataxis: HIGH       # diataxis.fr is the primary source and is explicit
---

# Lesson Style Catalogue — R1.1 / R1.1a

Fourteen named formats. Five ship in v1. Four are named as **structurally
unfixable** and rejected. Five collapse into the five that ship, or into a
parameter, and the collapse is the main finding.

**The load-bearing claim of this artifact, stated first so the rest can be
checked against it:**

> A lesson style is almost never a new block. It is an **ordering constraint plus
> a budget** over blocks Phase 3/3.1 already defines. The whole registry costs
> **one new block**, **nine lint codes**, **zero parser changes**, **zero renderer
> forks**, and **zero dependencies**. Any style that costs more than that is a
> style whose weakness has no cheap fix, and this artifact names all four of them.

That is what makes Directive §3 affordable here. A style is a registration
(§Extensibility Rule 1), and the thing registered is a rule set, not code.

---

## 0. The vocabulary a style may draw on

Verified against `.planning/research/2026-08-09-differentiators-d1-d2-d3.md` and
ROADMAP Phase 3 / 3.1 success criteria. Everything below already exists or is
already committed for 3.1:

`## LESSON` · `### <section>` · lesson intro prose · `## TERMS` + `[[term]]` ·
`[!KEY]` (memorizable, `[ID:]`/`[HASH:]`, `{{cloze}}`) · `[!NOTE]` / `[!EXAMPLE]` /
`[!WARNING]` (decorative siblings) · figure · fenced code · `[SRC:]` provenance ·
`[LESSON-REF:]` item→heading link · `[LESSON-SRC:]` external lesson file ·
Educational Objective line (3.1 criterion 5) · item types `mc` `multi` `table`
`dnd` `build` `short`, and `check` from Phase 5.

**Exactly one block is missing, and five separate styles want it.** See §2.

---

## 1. The catalogue

Each entry: what it is → good for → bad for → structural blocks required → **TAKE**
→ **FIX** → verdict. "No cheap fix" is stated explicitly where it applies.

---

### 1. Execute Program — short-prose-then-check loop
**Pioneer:** executeprogram.com (Gary Bernhardt).

**What it is.** Very short prose (a paragraph or two), then an interactive problem
the learner must actually complete, then the next paragraph. Lessons are short and
unfold responsively. Spaced review sits over the top, and — the part that matters —
*"lessons don't unlock until you've successfully reviewed their prerequisites"*
[VERIFIED: Matuschak's notes on Execute Program]. Missed review answers do not
penalize unless the learner gives up.

**Good for.** Procedural, compositional material where each step is independently
testable: syntax, APIs, regex, SQL, protocols. Excellent for a learner who
overestimates comprehension, because the check arrives before the illusion sets.

**Bad for.** Anything whose unit of understanding is larger than a paragraph.
Conceptual synthesis, clinical judgement, proof strategy. Chopping those into
checkable paragraphs destroys the thing being taught. Also bad for reference: you
cannot skim a gated lesson.

**Blocks required.** `### section` · short prose · **an inline check anchor**
(the missing block) · budget: max N words of prose before a check.

**TAKE — three things.**
1. The **check is inline, in the prose flow**, not an exercise set at the end.
   Position is the pedagogy; moving the questions to the bottom makes it an
   expository chapter with homework.
2. **Prerequisite-gated unlock**, which is ALEKS fringe selection wearing a
   lesson's clothes and already blessed for Phase 7.
3. **Missing a review costs nothing unless you give up.** This is a
   non-punitive design our anti-streak rule should copy verbatim.

**FIX — three things.**
1. **Language and content lock-in.** Their lessons only exist inside their
   product and only for their four languages. Our fix is structural and free:
   the lesson is a markdown file the learner owns, and the check is a
   `[LESSON-REF:]`-linked item in the same bank.
2. **No reference mode.** A gated lesson is unreadable as a lookup surface. Our
   fix: the gate is a *session mode*, not a property of the file. The same
   lesson read outside a gated sitting renders every check as a visible,
   answerable, ungated item. This costs nothing because Phase 6.2 already owns
   the gate and R3.3 already owns the gate-versus-skip ruling.
3. **Prose density is set by the author's taste, unchecked.** Our fix is
   `style.prose_before_check_too_long` as a hard error with a per-style
   parameter. The style file finally makes the loop's contract machine-real,
   which is exactly D3's claim.

**Verdict: SHIP.** Registry name `checked-prose`, merged with Brilliant — see §3.

---

### 2. Brilliant — one idea per screen, prediction before explanation
**Pioneer:** brilliant.org.

**What it is.** Each lesson is one concept; a short sequence of problems and
visualizations, typically 5-15 minutes; the architecture forces the learner to
predict or manipulate *before* the explanation appears, and a wrong answer opens
an interactive explanation rather than a text one [CITED: brilliant.org/about;
beginnersinai.org Brilliant explainer; ustwo case study].

**Good for.** Building intuition on a single idea where a prediction is
meaningful and cheap to state. Math, physics, probability, logic, algorithms.
Outstanding first-contact format.

**Bad for.** Volume. It is the most expensive format per unit of content in this
catalogue, and it does not scale to a 40-item EMT chapter. Also bad for material
where the learner has no basis to predict — a drug dose, a protocol step — where
"predict first" is a guessing game that teaches the wrong answer first.

**Blocks required.** Same as Execute Program plus one flag: the check must render
**before** the prose that resolves it. No new block; an ordering rule.

**TAKE — two things.**
1. **Predict before explain**, which is the productive-failure result (§12) in
   product form and has the strongest evidence base in this document.
2. **One idea per screen as a hard budget**, not an aspiration. Round one already
   proposed E2 (250-word section cap) and M1 (one idea per section, model-judged).
   Brilliant proves the budget should be a *ship* constraint, not a `manual` row.

**FIX — three things.**
1. **Walled garden.** Named in the brief, and the fix is the whole project:
   the content is a markdown file the learner owns. Free.
2. **Non-transferable content.** Their one-idea unit is welded to a bespoke
   interactive widget per lesson. Our fix, and it is a *reduction* in scope on
   purpose: our predict step is an ordinary `mc`/`short`/`check` item. We lose
   the manipulable; we keep the loop. Phase 6.1's SVG protocol and Polypad's
   shared-primitive rule are where manipulables come back, once, as a component
   library — never as per-lesson JS.
3. **Prediction is mandatory even where it is meaningless.** Our fix:
   `predict_first` is a style parameter, defaulted per subject profile, and the
   EMT profile turns it off. This is exactly the expertise-reversal /
   prior-knowledge boundary (§12) and it must be a knob for that reason.

**Verdict: SHIP, merged.** Brilliant and Execute Program are the **same style
with two parameter settings** — `predict_first: true|false` and a prose budget.
Shipping them as two registry entries would be two names for one rule set.
Directive §3 says ship both; the honest reading of §3 here is that both settings
ship behind one interface, which is what a parameterised style *is*.

---

### 3. Runestone — active-reading textbook with runnable code and Parsons problems
**Pioneer:** runestone.academy / RunestoneInteractive.

**What it is.** A real textbook chapter whose examples are executable in place
(ActiveCode) and whose exercises include Parsons problems (reorder given code
blocks), multiple choice, fill-in, clickable-area [VERIFIED: Runestone author
guide, Parsons directive page; overview book]. CSCI 1100's own book runs on it.

**Good for.** Exactly our CS lane. Runnable examples inside prose is the natural
home of the `check` type, and Parsons problems are **already expressible as our
`build` item type** — an ordering of given steps. That is a free win nobody has
noticed: `build` is a Parsons problem.

**Bad for.** Non-code subjects; the format's whole differentiator is the runtime
in the page. Also bad at pacing — a Runestone chapter is chapter-length, and the
active-reading elements are sprinkled, not budgeted.

**Blocks required.** `### section` · prose · fenced code · inline check anchor ·
`build` items for Parsons. **No new block beyond the shared anchor.**

**TAKE — two things.**
1. **Parsons problems as a first-class exercise**, and the recognition that
   `build` already is one. Cost: a CS subject-profile note and possibly a
   `build` render variant for code. Near zero.
2. **Runnable example inside the prose**, which Phase 5's `check` type plus the
   inline anchor delivers.

**FIX — two things.**
1. **No pacing contract.** Interactives are decoration in most Runestone books;
   nothing enforces density. Our fix: the style file's budget rules, and
   `style.idea_budget_exceeded` as a warning.
2. **Server-dependent execution.** Runestone runs code against its infrastructure
   and a book is only fully alive online. Our fix is already the architecture:
   `check` runs the learner's own code locally, and the lesson degrades to
   readable prose with plain code blocks when nothing can execute — the
   "degrade, never block" constraint.

**Verdict: SHIP, merged into `artifact-first` (CS) and `worked-example`.**
Runestone is not one style; it is an expository textbook that adopted two
techniques. The techniques ship; the container does not need its own name.

---

### 4. Math Academy — annotated worked example then variation ("knowledge point")
**Pioneer:** mathacademy.com.

**What it is.** Lessons are scaffolded into 3-4 **knowledge points**; *"every
knowledge point starts with a fully worked out example for students to follow
along with,"* immediately followed by practice problems in a slightly different
context [VERIFIED: mathacademy.com/how-it-works; Skycak, Chalk and Talk #42;
independent reviews]. Sits over a prerequisite knowledge graph.

**Good for.** Procedural mastery where a correct solution has visible steps:
math, stoichiometry, dosage calculation, proof technique, algorithm tracing. The
worked-example effect is one of the best-replicated results in instructional
psychology for novices.

**Bad for.** Expert learners — this is the **expertise reversal effect**
[VERIFIED]: guidance that helps a novice becomes redundant load for someone who
already has the schema. Also bad for material with no canonical procedure
(clinical judgement, design).

**Blocks required.** A **worked example container with per-step annotation**, then
a variation item. Verdict on the container: **no new block.** An `[!EXAMPLE]`
callout containing an ordered list, with `[!KEY]` for the step that generalizes,
carries it. Fading (dropping annotations on later examples) is an author choice,
not a grammar.

**TAKE — three things.**
1. **The example→variation adjacency as a hard ordering rule.** Machine-checkable
   and cheap: a section whose first item is not preceded by an example in the
   same section is a lint finding. This is round one's M4/M5 promoted from
   `manual` to a real check, which is the single most valuable thing in this
   catalogue for R2.
2. **The knowledge point as the section unit** — 3-4 per lesson gives the
   `### section` a defensible size, which E2's 250-word cap was guessing at.
3. **Prerequisite unlock** (same as Execute Program, same as ALEKS fringe).

**FIX — three things.**
1. **Total opacity.** You cannot read Math Academy's knowledge graph, edit a
   lesson, or export anything. Our fix is the file on disk plus `PREREQ:` edges
   already scoped for Phase 7/3.2.
2. **XP.** Even as an effort meter it is a score, and scores are Out of Scope in
   `PROJECT.md`. Take the *short pre-decided menu* (round one already did); leave
   the number.
3. **No exit ramp for the expert.** Expertise reversal is real and their format
   has no fading. Our fix: `faded: true` as a style parameter, and — better —
   the Phase 7 selector can skip the worked example for an objective whose
   evidence already shows mastery. That is a selection decision, not a style one,
   and it is the honest place for it.

**Verdict: SHIP.** Registry name `worked-example`. This is also the leading half
of the answer to `??? for math` (R1.7's slice, flagged not answered here).

---

### 5. Classic expository textbook chapter
**Pioneer:** everyone; no product to credit.

**What it is.** Headed sections, definitions, prose exposition, worked examples,
figures, end-of-chapter exercises, summary.

**Good for.** Coverage, reference, breadth, and *rereading*. It is the only
format in this catalogue that survives being skimmed, printed, and consulted
non-linearly — which matters more than it sounds given our print CSS and paper-
study goal (blind spot B4). It is also the only format an authoring model
reliably produces without heavy steering, which is a real consideration for D3.

**Bad for.** Retrieval. Nothing forces the learner to do anything, so the
illusion of comprehension is maximal. Exercises at the end are answered by
scrolling up.

**Blocks required.** Nothing new whatsoever. It is the format the current
`## LESSON` grammar already is.

**TAKE.** Its **survivability**. It degrades gracefully to print, to plain text,
to a screen reader, to a skim. Every other style in this catalogue is a
constrained specialisation of it.

**FIX.** The passivity, with the cheapest possible intervention: require at least
one `[!KEY]` per section and at least one `[LESSON-REF:]`-linked item per
objective. That converts "read this" into "read this, and something checks it,"
without the file becoming a gated loop.

**Verdict: SHIP, and make it the base.** Registry name `expository`. It is the
**parent every other style inherits from** and the fallback for an unstyled bank.
This is what makes R1.4's house/style inheritance concrete: the house rules are
`expository`'s rules, and a named style is a delta.

---

### 6. Feynman / explain-simply narrative
**Pioneer:** folk method attributed to Feynman; no product, no primary source.

**What it is.** Explain the idea in plain words as if to a novice, notice where
the explanation breaks, go back to the source, simplify again.

**Good for.** It is a **study technique**, and a good one — it is the
self-explanation effect wearing a name. As a *learner activity* it is valuable.

**Bad for.** Being a written lesson style. Two documented failure modes:
oversimplification that deletes required complexity in technical fields, and the
"Feynman effect" — a lucid explanation producing an *illusion of understanding*
in the reader precisely because it was so easy to follow [CITED: multiple
secondary sources; note this is folk literature, not a controlled result, and I
am flagging the confidence as LOW-MEDIUM].

**Blocks required.** None. That is the tell.

**TAKE.** The activity, not the format: a `short` item that asks the learner to
explain the concept, marked against a rubric under tier-3 `pending` authority.
That is Phase 8's job and it is already scoped.

**FIX — and there is no cheap one.** The quality of a Feynman lesson is
*entirely* the fidelity of its analogy and the correctness of what it chose to
omit. Both are irreducibly semantic. Every rule this style could contribute lands
in the `manual` bucket (round one's M2 and M3 verbatim). A style file whose rules
are all `manual` enforces nothing, and D3's honesty rule would force every row to
be labelled aspirational. **A style contract nobody can check is decoration**,
which is the brief's own test.

**Verdict: REJECT as a style. NO CHEAP FIX.** Its one good idea — plain, calm,
declarative register, mechanism before drill — is already a **house rule** in
round one's `## Voice` zone. Keep it there.

---

### 7. Cookbook / recipe reference
**Pioneer:** the O'Reilly Cookbook series; every "Problem / Solution / Discussion"
reference.

**What it is.** Task-indexed entries: here is a problem, here is the code or
procedure that solves it, here is why it works.

**Good for.** Someone who already knows the domain and needs the incantation.
Lookup speed. It is genuinely the best format for what it does.

**Bad for.** Learning. Diátaxis is explicit and primary on this: how-to guides
serve a user *"focused on completing the task rather than learning,"* and
*"the number one mistake is mixing the types on the same page"* — a tutorial that
also explains theory helps no one [VERIFIED: diataxis.fr/start-here].

**Blocks required.** A per-entry problem/solution/discussion triple. Would be a
new repeating container.

**TAKE.** The Diátaxis discipline itself, as a **house-wide governance rule**:
one lesson serves one of {teach, explain, look up}, and a lesson that tries to be
a reference gets a lint warning. This is a genuinely distinct finding the brief
did not have, and it costs one warning code.

**FIX — no cheap one.** To make a cookbook teach, you have to add the thing that
makes it not a cookbook. Its weakness *is* its purpose.

**Verdict: REJECT as a lesson style. NO CHEAP FIX.** But adopt the Diátaxis split
as a house rule, and note for R1.3/R5: reference material belongs in a
`[LESSON-SRC:]` file that a lesson *cites*, not in `## LESSON`. That is a free
answer to a question R5 is otherwise going to have to invent.

---

### 8. Question-first Socratic sequence
**Pioneer:** as a *written* form, nobody credible. As an interactive form,
Khanmigo, ChatGPT Study Mode, StudyBro.

**What it is.** The lesson advances by asking rather than telling; each answer
determines the next question.

**Good for.** Live dialogue with an interlocutor who can read the answer. This is
the single strongest teaching format that exists, and it is **not a document
format**.

**Bad for.** Being written down. A written Socratic sequence has no interlocutor,
so every branch must either be pre-authored (combinatorial explosion) or
collapsed to one path — at which point the questions are rhetorical. Round one
already banned rhetorical questions in lesson prose as warning **W7**. The style
would be at war with the house rules on its first line.

**Blocks required.** Branching. A conditional traversal grammar. That is a
**second parser** in everything but name, and Directive §4.2 kills it on sight.

**TAKE.** All of it — into the right layer. Socratic pacing is the **hint ladder**
(Phase 6) and the **tutoring model** (Phase 8), where a real interlocutor exists
and the runtime gates the tier. Round one's Khanmigo refusal formula is already
recorded there.

**FIX — no cheap one at the document layer.** Branching prose needs a traversal
engine and a state store; the state store we have is the evidence log and it is
append-only for good reasons.

**Verdict: REJECT as a lesson style. NO CHEAP FIX.** It is a *mode of the tutor*,
already scoped, and confusing the two would put lesson content on a code path
that has to become interactive.

---

### 9. Case narrative — unfolding / progressive disclosure (medical education)
**Pioneer:** case-based learning in medical and nursing education; UWorld and
Amboss as commercial expressions.

**What it is.** A patient presents. Some information is given. The learner
commits to an interpretation or action. **Then** more information arrives —
vitals change, a lab returns, the patient deteriorates. Repeat. The literature
distinguishes this from a traditional case (all information at once) and finds
in favour of unfolding: better knowledge acquisition, better theory-to-practice
integration, better long-term retention [VERIFIED: ScienceDirect S147159532200035X
on unfolding CBL in nursing; PubMed 30025772 progressive-disclosure cases in
therapeutics; 2026 scoping review in Medical Science Educator]. One practical
finding worth copying exactly: in resource-constrained settings, **short cases
with progressive disclosure beat lengthy narratives** [CITED: Adams et al.,
Medical Education 2026].

**Good for.** EMT, and nothing else in this project as strongly. Clinical
judgement, triage, sequencing under uncertainty, and the specific skill of
*revising* a judgement when new information arrives — which no other format in
this catalogue teaches at all.

**Bad for.** Foundational fact acquisition. A case assumes you already know what
a blood pressure means. Also bad for coverage: a case teaches deeply and narrowly,
and you cannot cover a 40-objective chapter in cases.

**Blocks required.** **A staged-reveal container.** This is `## SCENARIO`, named
in Phase 9 and never specified; its grammar is R3.2's slice, not mine. What this
slice contributes is the requirement: stages, a commit point per stage, and
**the runtime — not the model and not the learner's scroll position — controls
the reveal.** That is Directive §4.1 applied to a container.

**TAKE — three things.**
1. **Commit before reveal.** The learner must answer before the next stage
   appears. This is the same gate as Execute Program's, and it should be the
   *same implementation*.
2. **Short cases over long ones**, per the 2026 finding. A budget rule, cheap.
3. **UWorld's per-distractor rationale plus the closing Educational Objective
   sentence** — already taken in round one, already Phase 3.1 criterion 5.

**FIX — two things.**
1. **Cases are unschedulable.** A medical-ed case is a one-shot artifact; nothing
   in that industry brings it back three weeks later. Our fix is nearly free:
   each stage's commit point is a `[LESSON-REF:]`-linked item, so a case's
   decision points enter the same evidence log and the same Phase 7/10 selection
   as everything else. **The case becomes a source of scheduled items.** This is
   the best single idea in this artifact and it costs nothing beyond `## SCENARIO`.
2. **Cases hide their coverage.** A narrative does not announce which objectives
   it touches, so the curriculum auditor cannot see it. Fix: objectives are
   declared per stage, same as any item, and the Phase 11 auditor reads them.

**Verdict: SHIP.** Registry name `case-narrative`. **Blocked on R3.2** for the
`## SCENARIO` grammar — flag this as the one hard dependency in this artifact.

---

### 10. "The Bottom Up" / Wienand — runnable-artifact-first, mechanism from the substrate
**Pioneer:** *Computer Science from the Bottom Up*, Ian Wienand (bottomupcs.com,
CC BY-SA, sources on GitHub) [VERIFIED: LibreTexts mirror, archive.org, official PDF].

**What it is.** The deliberate inversion of the top-down curriculum: start at
binary and logic gates, then OS internals, then toolchain, then libraries. It is
*language-independent* and aims at a *practical, realistic* understanding rather
than a theoretical one.

**Good for.** CSCI 1100's actual problem — students who can write code and cannot
say what it does. Anything where the abstraction leaks and the leak is the lesson:
memory, pointers, encodings, file descriptors, the linker.

**Bad for.** Motivation ordering. Bottom-up delays the payoff, and a learner who
has not yet seen the problem does not know why the substrate matters. It is also
bad for anything where the substrate genuinely does not leak — you should not
teach SQL from B-trees up.

**Blocks required.** Fenced code · figure · `check` items · a rule that **the
runnable artifact precedes the abstraction that names it.** No new block.

**TAKE — one thing, and it is the important one.** The **ordering rule**:
concrete artifact → observed behaviour → the name for it. This is
machine-checkable in a way nothing about Feynman is: a section whose first
non-prose element is a definition rather than an example or a code block is a
lint finding (`style.example_before_abstraction`).

**FIX — three things.**
1. **It is a book, not a loop.** Zero exercises, zero checks, zero scheduling.
   Our fix is the whole product. This is the cheapest fix in the catalogue: the
   ordering rule is the entire style, and everything it lacks we already have.
2. **No pacing.** Chapters are chapter-sized. Fix: the same section budget.
3. **Bottom-up ordering with no motivating hook.** Fix: borrow PRIMM's Predict
   step (§11) as the opener, which is why the two merge.

**Verdict: SHIP, merged with PRIMM.** Registry name `artifact-first`.

---

### 11. PRIMM — Predict, Run, Investigate, Modify, Make
**Pioneer:** Sue Sentance and Jane Waite, King's College London, 2017. Built on
Use-Modify-Create, levels of abstraction, and code-tracing research; now widely
used for structuring programming lessons [VERIFIED: ACM WiPSCE 2017 10.1145/3137065.3137084;
SIGCSE 2019 teacher-experience paper; teachcomputing.org].

**What it is.** A five-stage lesson: **predict** what given code does, **run** it,
**investigate** why, **modify** it to change behaviour, **make** something new.
"Reading before writing."

**Good for.** The brief missed this and it is the most directly applicable named
format in the CS literature. It is also the only style here whose stages map
one-to-one onto item types we already have: Predict = `mc` or `short`, Run =
`check` (no assertion), Investigate = `mc`/`short`, Modify = `check`, Make =
`check`.

**Bad for.** Non-code. It is unapologetically a programming pedagogy. Also
somewhat slow for a confident learner — the same expertise-reversal caveat.

**Blocks required.** **Nothing new.** Five ordered sections with declared roles.
This is the cleanest proof of this artifact's central claim: a well-known
five-stage pedagogy costs us a *lint rule about section order*.

**TAKE.** The stage sequence as a required section ordering, and **Predict as the
opening move** — which is the same rule as Brilliant's `predict_first` and the
same underlying result as productive failure. Three independent traditions
converge on it; that is as close to a settled answer as this catalogue gets.

**FIX — two things.**
1. **Classroom-shaped.** PRIMM assumes discussion in pairs and a teacher at the
   Investigate stage. Our fix: Investigate becomes the tutoring-model turn
   (Phase 8), runtime-gated, and it is the honest use of the model.
2. **The Make stage is unassessable in the literature** and is usually just
   "build something." Fix: Make is a `check` item with a real output comparison,
   or it is not in the lesson. Our one-scorer rule improves on the source here.

**Verdict: SHIP, merged into `artifact-first`.** PRIMM supplies the *pacing*
(five stages, predict first); Bottom Up supplies the *ordering* (substrate before
abstraction). They are orthogonal and compose. Shipping them separately would be
two registry entries whose lint rules never conflict — the definition of a
false split.

---

### 12. Productive failure / exploration-then-formalization
**Pioneer:** Manu Kapur (Kapur 2014, *Cognitive Science*; Sinha & Kapur 2021
meta-analysis in *Review of Educational Research*).

**What it is.** Learners attempt a problem targeting a concept they have **not**
been taught, generate (and fail with) their own representations, and *then*
receive the canonical instruction that consolidates the attempt.

**Good for.** Conceptual knowledge specifically. The meta-analytic effect sizes
for conceptual knowledge acquisition are large (d ≈ 0.6-2.3) versus
instruction-then-practice [VERIFIED]. This is the strongest evidence base in
this document by a wide margin, and it is the **counterweight to Math Academy**:
worked-example-first wins on procedural fluency, problem-solving-first wins on
conceptual understanding.

**Bad for.** Novices with insufficient prior knowledge — the expertise-reversal
literature is explicit that low-knowledge learners overwhelmed without guidance
resort to inefficient strategies [VERIFIED]. And for procedural material where
there is nothing to invent.

**Blocks required.** **Nothing new.** An item placed before the section that
teaches it, with the reveal gated. That is the inline check anchor plus one flag.

**TAKE.** The evidence-backed ordering, and the crucial nuance: failure is
productive only when the *consolidation* follows and explicitly addresses the
failed attempt. That is what our hint ladder plus per-option `da` rationale is
already built to do — arguably the single best fit between this project's
existing machinery and an outside result.

**FIX — one thing.** The literature's own boundary condition is unmanaged in
practice: it stops working for the under-prepared. Our fix is a parameter, not a
style, and the Phase 7 selector can set it from evidence.

**Verdict: NOT A STYLE — it is the `predict_first` / `open_first` parameter**
already required by Brilliant (§2) and PRIMM (§11). Shipping it as a fourteenth
registry entry would create three names for one flag. **This is the finding that
justifies parameterised styles over a flat list**, and it should be recorded as
such for R1.3.

---

### 13. Explorable explanation / reactive document
**Pioneer:** Bret Victor, *Explorable Explanations* (2011). Descendants: Nicky
Case, Distill, Mathigon.

**What it is.** Prose whose parameters are live: drag a number in a sentence and
the rest of the document updates. Victor's aim was *"text as an environment to
think in."*

**Good for.** Building intuition about parameterised systems — anything with a
dial. When it works it is the best format in this list.

**Bad for.** Everything else, and possibly for its own claim. The honest read of
the evidence: there is a **scarcity of rigorous large-scale studies** showing
consistent superiority over static explanations, Victor himself flagged the risk
of opacity and simplification, and in surveyed practice most "interactive"
explanations offer only click-through-a-sequence interactivity [CITED: Victor,
worrydream.com; Wikipedia "Explorable explanation"; arXiv 2606.31012 on
evaluating interactivity — MEDIUM confidence, this literature is thin].

**Blocks required.** Per-lesson bespoke JavaScript, a reactive binding grammar,
and a canvas. A **renderer fork**.

**FIX — no cheap one, and it fails a non-negotiable.** Per-lesson bespoke
JavaScript is **bank-authored executable code, which `VIS-01` and `UI-SPEC.md:609`
refuse outright**. It also breaks the one-renderer story, which is a second
renderer against Directive §4.2. Round one already declined canvas-heavy content
on exactly this ground.

**Verdict: REJECT. NO CHEAP FIX — and it is bank-authored JavaScript, which
`VIS-01` refuses.** The
salvageable 10% is Phase 6.1's SVG protocol with Polypad's shared-primitive rule:
a *small fixed library* of manipulables with one accessibility story, used by
items, never a per-lesson widget. That is already scoped.

---

### 14. Atomic prompt sheet (Anki-native / Matuschak "how to write good prompts")
**Pioneer:** the SRS authoring tradition; Matuschak's prompt-writing essay.

**What it is.** The lesson *is* the card set. Each fact is an atomic
question/answer pair; prose exists only as connective tissue.

**Good for.** Dense memorization: drug names, anatomy, protocol numbers, kanji.

**Bad for.** Understanding. Atomization destroys the relations between facts,
which is the well-known complaint about med-school Anki monoculture.

**Blocks required.** None new — **this already exists as `[!KEY]` plus the Anki
TSV export** (D2, Phase 3.1 criterion 2).

**Verdict: REJECT as a style, because we already shipped it as a block.**
Registering `atomic-prompts` as a style would create a **second path to the same
artifact** — a lesson whose entire content is memorizables versus a lesson
containing memorizables — and two paths to one artifact is how a second parser
gets born by accretion. A style file may instead *raise the `[!KEY]` budget*.
That is one number, not a style.

---

## 2. The one new block

Five styles (Execute Program, Brilliant, Runestone, PRIMM, productive failure)
want the same thing and it does not exist: **a way to say "an item goes here, in
the prose flow."**

**Recommendation: one inline anchor block, name it once.**

```markdown
[!CHECK: 3f9a2c1d0e8b7a64]
```

- Line-anchored, resolves to an item `[ID:]` in the same bank (or a `q<n>` ref,
  same resolution `[LESSON-REF:]` already uses in reverse).
- The renderer substitutes the item's public form at that position; the runtime
  decides whether it is gated, ungated, or reveal-locked, by session mode.
- **It is a placement instruction, not content.** It carries no key, no answer,
  no new scoring path. `runtime.score_response()` is untouched.
- Additivity: a bank with no `[!CHECK:]` line is byte-identical.
- It reuses the `[!TYPE]` callout family grammar already committed in D2, so it
  is a new *marker*, not a new *shape* — and an old renderer degrades it to a
  visible literal line, never hidden content.

**Why it beat the runner-up.** The runner-up was "no new block: express inline
checks purely by section ordering, with items always rendered at the section
end." That is cheaper by one code and it loses the pedagogy — Execute Program,
Brilliant and PRIMM are all *about* the check's position. Ordering-only would
ship five styles that are all secretly `expository`.

**Cost of the whole registry:**

| Item | Count |
|---|---|
| New blocks | **1** (`[!CHECK:]`) |
| New parsers | 0 |
| New scorers | 0 |
| New evidence stores | 0 |
| Renderer forks | 0 |
| Dependencies | 0 |
| New lint codes | **9** (below) |
| Hard external dependency | `## SCENARIO` grammar (R3.2) — blocks `case-narrative` only |

Nine codes: `style.unknown` (error, named style not in registry) ·
`style.inheritance_cycle` (error) · `style.required_block_missing` (error) ·
`style.block_order` (error, style declares an ordering the lesson violates) ·
`style.check_ref_unknown` (error, `[!CHECK:]` names no item) ·
`style.check_orphan` (warning, item referenced by no `[!CHECK:]` in a style that
requires inline checks) · `style.prose_before_check_too_long` (error, parameterised) ·
`style.idea_budget_exceeded` (warning) ·
`style.example_before_abstraction` (warning, Bottom-Up ordering rule).

All nine extend `LINT_CODES` additively, all nine are pure-stdlib structural
counts over already-parsed headings and markers. None is a readability metric,
none is semantic. That is the honest answer to R2.1 from this slice's side.

---

## 3. Ranked shortlist — ship in v1

Ranked by (evidence strength × subject fit × marginal cost).

| # | Registry name | Collapses | Subject | New cost beyond the shared anchor | Why it ranks here |
|---|---|---|---|---|---|
| **1** | `expository` | §5 | all (default/parent) | 0 | It is the parent every other style inherits from and the fallback for an unstyled bank. Shipping the registry without it means the house rules have nowhere to live. Zero cost, and it makes R1.4's inheritance question answerable. |
| **2** | `worked-example` | §4 Math Academy, §3 Runestone (partly) | Math, EMT procedures | 1 ordering rule | Best-replicated result for novice procedural learning; maps onto the `[!EXAMPLE]` + variation pattern with no new grammar; leading candidate for `??? for math`. |
| **3** | `checked-prose` | §1 Execute Program, §2 Brilliant, §12 productive failure (as `predict_first`) | CS, Math, EMT facts | 2 params (`predict_first`, prose budget) | Weibao named Execute Program as "perfect." Three traditions converge on predict-first. Parameterisation is what lets two products ship as one interface per Directive §3. |
| **4** | `artifact-first` | §10 Bottom Up, §11 PRIMM, §3 Runestone (Parsons via `build`) | CS | 1 ordering rule | The CS answer Weibao asked for by name, plus the strongest named CS pedagogy in the literature. Discovers that `build` already *is* a Parsons problem — free. |
| **5** | `case-narrative` | §9 medical CBL | EMT | `## SCENARIO` (R3.2) | Only format that teaches judgement revision; strong peer-reviewed evidence for progressive disclosure. **Ranked last only because it is the one entry with an external dependency.** If R3.2 slips, this slips; the other four do not. |

**Reject in v1 — four styles, all with weaknesses that have NO cheap fix:**

| Style | Why unfixable | What we keep instead |
|---|---|---|
| **Feynman / explain-simply** (§6) | Every rule it could contribute is semantic and lands in the `manual` bucket. A style whose contract is entirely aspirational is decoration, which is the brief's own disqualifying test. | Its register survives as a **house rule** in `## Voice`; its activity survives as a `short` item under tier-3 `pending`. |
| **Cookbook / recipe** (§7) | Its weakness *is* its purpose. Diátaxis is primary and explicit that mixing reference into a tutorial helps no one. | The **Diátaxis split as a house rule** (one lesson serves one of teach/explain/look up, one warning code), and reference material lives in a `[LESSON-SRC:]` file the lesson cites. |
| **Written Socratic** (§8) | Needs branching traversal = a second parser (Directive §4.2). Unbranched, it collapses to rhetorical questions, which round one's W7 already bans. | All of it, in the **hint ladder (Phase 6) and tutoring model (Phase 8)**, where a real interlocutor exists and the runtime gates the tier. |
| **Explorable explanation** (§13) | Per-lesson bespoke JavaScript is **bank-authored executable code, refused outright by `VIS-01` and `UI-SPEC.md:609`**. It is also a renderer fork against Directive §4.2. Evidence base is thin. | **Phase 6.1's SVG protocol** with Polypad's shared-primitive rule: one small manipulable library, one accessibility story, used by items. |

**Rejected as a style for a different reason (not unfixable — already shipped):**
**atomic prompt sheet** (§14) is `[!KEY]` plus the Anki TSV export. Registering it
would create a second path to one artifact. A style may raise the `[!KEY]` budget
instead — one number.

**Not a style at all:** **productive failure** (§12) is the `predict_first`
parameter. Its evidence is the best in this document and its correct home is a
flag on `checked-prose`, defaulted by subject profile and overridable by the
Phase 7 selector when evidence shows the learner is under-prepared (expertise
reversal).

---

## 4. What I could not verify

- **executeprogram.com's own pages returned no text** to WebFetch (JS-rendered).
  The gating and non-penalty claims are sourced from Andy Matuschak's notes,
  which are a careful secondary source but secondary. Do not quote Execute
  Program's mechanics in product copy without a fresh check.
- **Brilliant has no public authoring or pedagogy document.** The one-idea and
  predict-first claims come from its About page plus consistent secondary
  reviews. Confidence MEDIUM; the *pattern* is safe to adopt, the *attribution*
  should stay soft.
- **The Feynman technique has no primary pedagogical source at all.** Everything
  is folk literature. That absence is itself part of the rejection.
- **The negative evidence on explorable explanations is thin** — an absence of
  strong positive studies rather than positive negative results. I am rejecting
  it on `VIS-01` (bank-authored JavaScript is refused), not on the evidence.
- **"Runestone Parsons problems map cleanly onto our `build` type"** is my
  reading of both grammars, not a tested claim. It is cheap to falsify at plan
  time and worth doing early, because rank 4 partly rests on it.

---

## Sources

**Execute Program:** [Andy Matuschak's notes on Execute Program](https://notes.andymatuschak.org/zSsjk5UvNPGrYp8B6DEFCMS) · [Execute Program spaced repetition](https://www.executeprogram.com/spaced-repetition) · [mike.place on Execute Program](https://mike.place/2020/executeprogram/)
**Brilliant:** [About Brilliant](https://brilliant.org/about/) · [Brilliant explained (2026)](https://beginnersinai.org/brilliant-explained/) · [ustwo × Brilliant](https://ustwo.com/work/brilliant/)
**Runestone:** [Parsons Problems — Runestone Author Guide](https://runestone.academy/ns/books/published/authorguide/directives/parsons.html) · [Overview of Runestone Interactive](https://runestone.academy/ns/books/published/overview/index.html) · [RunestoneServer](https://github.com/RunestoneInteractive/RunestoneServer)
**Math Academy:** [How it works](https://www.mathacademy.com/how-it-works) · [Chalk and Talk #42 with Justin Skycak](https://www.justinmath.com/chalk-and-talk-podcast-42/) · [Book review: The Math Academy Way](https://ijfen.substack.com/p/book-review-the-math-academy-way)
**Bottom Up:** [Computer Science from the Bottom Up (PDF)](https://www.bottomupcs.com/csbu.pdf) · [LibreTexts mirror](https://eng.libretexts.org/Bookshelves/Computer_Science/Programming_and_Computation_Fundamentals/Computer_Science_from_the_Bottom_Up_(Wienand)) · [Internet Archive](https://archive.org/details/bottomupcs)
**PRIMM:** [PRIMM, WiPSCE 2017](https://dl.acm.org/doi/10.1145/3137065.3137084) · [Teachers' experiences of PRIMM, SIGCSE 2019](https://dl.acm.org/doi/10.1145/3287324.3287477) · [Using PRIMM to structure programming lessons](https://teachcomputing.org/blog/using-primm-to-structure-programming-lessons/) · [PRIMM project page](https://computingeducationresearch.org/projects/primm/)
**Case-based / progressive disclosure:** [Unfolding case-based learning, nursing health assessment](https://www.sciencedirect.com/science/article/abs/pii/S147159532200035X) · [Progressive disclosure cases in therapeutics, PubMed 30025772](https://pubmed.ncbi.nlm.nih.gov/30025772/) · [CBL framework scoping review, Med Sci Educ 2025](https://link.springer.com/article/10.1007/s40670-025-02583-6) · [Making case-based learning work, Medical Education 2026](https://asmepublications.onlinelibrary.wiley.com/doi/full/10.1111/medu.70205) · [Unfolding case-study scoping review](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12858445/)
**Productive failure / expertise reversal:** [Kapur, Productive Failure in Learning Math, Cognitive Science 2014](https://onlinelibrary.wiley.com/doi/abs/10.1111/cogs.12107) · [Sinha & Kapur, RER 2021](https://journals.sagepub.com/doi/10.3102/00346543211019105) · [Expertise reversal effect](https://en.wikipedia.org/wiki/Expertise_reversal_effect) · [Prior achievement predicts learning from productive failure, npj Science of Learning](https://www.nature.com/articles/s41539-023-00165-y)
**Diátaxis:** [diataxis.fr](https://diataxis.fr/) · [Start here — Diátaxis in five minutes](https://diataxis.fr/start-here/) · [What is Diátaxis (I'd Rather Be Writing)](https://idratherbewriting.com/blog/what-is-diataxis-documentation-framework)
**Explorable explanations:** [Bret Victor, Explorable Explanations](https://worrydream.com/ExplorableExplanations/) · [Explorable explanation (Wikipedia)](https://en.wikipedia.org/wiki/Explorable_explanation) · [Evaluating Interactivity, arXiv 2606.31012](https://arxiv.org/pdf/2606.31012)
**Feynman technique:** [The Feynman Effect — illusion of understanding](https://memeinnovation.wordpress.com/2022/05/19/the-feynman-effect-aka-the-illusion-of-understanding/) · [ModelThinkers: Feynman Technique](https://modelthinkers.com/mental-model/the-feynman-technique)
