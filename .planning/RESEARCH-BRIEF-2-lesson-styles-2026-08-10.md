# Research Brief 2 — Lesson Styles, Genre Fit & Round-One Gaps

- **Created:** 2026-08-10
- **Status:** **research COMPLETE (2026-08-10)** — all five slices landed, five
  artifacts written, verdicts in §4. Next action is the `/gsd-phase` fold per §5.
- **Predecessor:** `.planning/RESEARCH-BRIEF-learning-platform-2026-08-09.md` (round
  one, findings in its §7). This brief covers what round one answered too narrowly
  or not at all.
- **Binding on this research:** `.planning/PLANNING-DIRECTIVES.md`, all six sections.
- **Purpose:** one research pass whose findings are embedded into Phases 3.1, 3.2, 5,
  6, 6.2, 7, 9, 10, and 11. Findings land in `.planning/research/2026-08-10-*.md`
  and are summarized in §4 of this file.
- **Execution split:** Claude researches and plans. DeepSeek V4 executes. Never run
  `/gsd-execute-phase` from a research or planning session.

---

## 1. Why a second pass

Round one was comprehensive on landscape, differentiators, packaging, and blind
spots. It under-answered one thing and left five threads loose.

**The under-answer.** Q3 asked how to hold an authoring model to a house style, and
answered with **one** `LESSON-STYLE.md`. Weibao asked for lesson **styles** —
plural, "inspired by that's already up there and more." One house voice is a
different product decision from a menu of pedagogies, and the roadmap currently
encodes the narrow reading.

This matters more than it sounds. The three subjects are not stylistically
compatible. Weibao's own framing in `PROJECT.md`: *"something fitting for each
genre, from readings and questions for EMT, LaTeX and ??? for math, The bottom up
or other styles for CS."* One voice across all three is the wrong shape, and the
`??? for math` has never been filled in.

Per Planning Directive §3, the expected answer is **not** "pick the best style." It
is a style **registry** with several good ones shipped and the choice left to the
learner and the authoring model.

---

## 2. Research questions

### R1 — The lesson style registry (the main question)

**R1.1** What are the genuinely distinct, named pedagogical formats for written
lesson material? Go past the obvious. At minimum characterize: the Execute Program
short-prose-then-check loop; Brilliant's one-idea-per-screen with prediction;
Runestone's worked-example-then-variation; the classic textbook expository chapter;
the Feynman/explain-simply narrative; the cookbook/recipe reference; the
question-first Socratic sequence; the annotated-worked-example (Math Academy
style); the case-narrative used in medical education; "The Bottom Up" /
Wienand-style runnable-artifact-first for CS. For each: what it is good for, what
it is bad for, and **what structural blocks it requires** from a format.

**R1.1a** For every format in R1.1, answer the two-sided question separately and
explicitly: **what does the product that pioneered it get right that we should take,
and what does it get wrong that our version must fix?** Round one produced
fight-for/do-not-copy lists per product; this is the same discipline per *style*.
Worked examples of the shape wanted: Brilliant's one-idea-per-screen loop is worth
taking and its walled garden is not, so our version must keep the loop while the
content stays a plain markdown file the learner owns. Execute Program's forced
gating is worth taking and its language lock-in is not. Anki's FSRS is worth taking
and its authoring UX is not. Duolingo's pacing is worth taking and its streak guilt
is not. Do this for every style, and name the weakness that has **no** cheap fix —
those are the styles we should not ship.

**R1.2** What is the **minimum shared block vocabulary** that lets all of these be
expressed in one markdown grammar? Where does a style need a genuinely new block
versus a different arrangement of blocks Phase 3.1 already defines
(`## LESSON`, `## TERMS`, `[[term]]`, `[!KEY]`, callout, figure, fenced code)? Name
every new block a style needs, and reject styles whose cost is a second parser.

**R1.3** What is the right **shape of a style definition file**? Round one's answer
was a prose voice zone plus a machine-parsed `## Rules` pipe table. Does that shape
hold for a registry of N styles — one file per style in a `styles/` directory, one
file with named sections, or a style that declares a parent and overrides it?
Answer with the maintenance cost of each, not aesthetics.

**R1.4** Which rules are **style-specific** and which are **house-wide**? A house
rule (no second-person hectoring, no fabricated citations, sentence-length ceiling)
applies to every style; a style rule (worked examples must precede variations,
maximum one idea before a check) is per style. What is the split, and how does a
style file inherit the house set without restating it?

**R1.5** How does the **authoring model** consume a style? Is the style file
prompt-context verbatim, a distilled instruction set, or a set of few-shot
exemplars? What does the literature and current practice say about which actually
produces adherence? Adherence is the whole claim of D3 — a style contract nobody
follows is decoration.

**R1.6** How does the **learner** choose? Per bank, per subject profile, per
lesson, or per reading session? Can the same source content be re-rendered in a
second style without re-authoring it, and if so what is the boundary between
content and style? Be concrete about what is impossible: a case narrative cannot be
mechanically derived from an expository chapter.

**R1.7** What does **`??? for math`** turn out to be? Weibao left it blank. Given
KaTeX is already vendored (Phase 9) and the 6.1 SVG protocol is the manipulable
path, what is the actual written form of a math lesson that works — worked example
plus variation, exploration-then-formalization, or something else? Name it.

### R2 — Style enforcement without a second quality gate

Round one gave 18 machine-checkable rules (8 error, 10 warning) and 5 model-judged.
With a registry, that count multiplies. **R2.1** Which checks are cheap enough in
pure stdlib to run on every lint, and which belong to the Phase 11 report-only
manual pass? **R2.2** Is there prior art for linting *prose structure* — heading
cadence, example-before-abstraction ordering, idea density per section — as opposed
to linting style at the sentence level (Vale, textlint, write-good, proselint)?
Name what those tools can and cannot do for us, and what we would have to write.
**R2.3** What is the false-positive posture? A style linter that cries wolf gets
disabled, which is worse than not having it.

### R3 — Threads round one left loose

**R3.1** Round one's Q9 found that **no success criterion anywhere measures actual
use**. What should? Propose 3–5 measurable adherence/usage criteria that read from
the existing evidence log, are not vanity metrics, and are not punitive (the
anti-streak rule in `UI-SPEC.md` holds). Which phase owns each?

**R3.2** The `## SCENARIO` staged-reveal container (Phase 9, EMT) was named but
never specified. What is its grammar, and how does the runtime stage a reveal
without the model choosing the pace? Compare against how medical-education products
actually phase a case.

**R3.3** The **executable textbook gate** (Phase 6.2) — what does current practice
say about *mandatory* gating versus a recorded skip? Weibao's rule says build both
and let the learner choose; confirm that is right here, or find the evidence that a
soft gate destroys the loop's value.

**R3.4** **Lesson generation at length.** D3 assumes a model writes lessons. What
is the state of the art on keeping a long generated lesson coherent, correctly
scoped to one objective, and free of invented facts — chunked generation, outline-
first, retrieval against `[SRC:]` passages? This is Phase 11's authoring loop and
Phase 3.2's seeding loop, and neither has a written answer.

**R3.5** **The 7900 XTX local model.** Given the hardware arrives, which local
open-weight models are actually good enough for lesson authoring and hint
generation at 24GB VRAM, and what does that imply for the Phase 8 adapter's
prompt-size and latency assumptions?

### R4 — Tiered verdicts: one scorer, several strategies, three authority levels

**The shape Weibao asked for (2026-08-10):** *"standard questions that are multiple
choice can be standardly graded but for code and other stuff they need a checker, but
for text things maybe ai scoring? making sure everything is adaptable."*

That is three tiers, and the design that delivers it without breaking the one-scorer
rule is: **`runtime.score_response()` stays the only entry point, and dispatches to a
registered verdict strategy per item type. The strategy declares its own authority
level, and the runtime honors that declaration.**

| Tier | Method | Item types | Authority | Reproducible? |
|---|---|---|---|---|
| 1 | Canonical-form equality | `mc`, `multi`, `table`, `dnd`, `build` | `accepted` | Yes — item + response alone |
| 2 | Executable / computed checker | `check` (code), Math equivalence, `visual` tolerance | `accepted` | Yes — deterministic given the same bounds |
| 3 | Model judgement against a rubric | `short`, and any future open-text type | **`pending`** until an explicit human accept | No |

Tier 3 is where the project's core claim lives, so state it precisely: a model **may**
read the rubric, the key, and the learner's text and produce a per-criterion verdict.
That verdict is evidence *that a suggestion was made*, never evidence that the learner
was right or wrong, until accepted. This is not a new restriction — Phase 8 already
specifies `review_state: pending` — but tiering makes it a structural property of the
strategy rather than a rule Phase 8 remembers to follow.

**Context the researcher must not get wrong.** `runtime.score_response()`
(`runtime.py:120`) is today a canonical-string equality: reduce the response to a
canonical form, compare against the key's canonical form, return the boolean.
Letter for `mc`, set for `multi`, field-separated tuple for `table`/`dnd`/`build`.
Constructed response returns **`None`, never `False`** — not-yet-marked and
marked-wrong are distinct states. **No model participates in any verdict.** Phase 8
lets a model mark a `short` answer against a rubric, and every point it produces
lands as `review_state: pending` — a suggestion, never accepted evidence. This is
the project's core claim, not an implementation detail, and any finding that
proposes a model deciding correctness is rejected outright under
`PLANNING-DIRECTIVES.md` §4.1.

**Research the design, do not assume the table above is right.** It is the working
hypothesis, and every question below can overturn part of it.

**R4.1 — the interface.** What is the right shape for a registered verdict strategy?
Candidates: one `Strategy` interface per item type returning
`(verdict, authority, detail)`; a normalization step in front of the existing equality
(so every tier still ends at one comparison); or a two-stage pipeline of normalize
then compare. Answer with which keeps "one scorer" **literally** true rather than
rhetorically true — a reviewer must be able to point at one function and say every
verdict passes through it. Say explicitly what stops a strategy from becoming a second
scorer by accretion.

**R4.2 — the authority rule.** Give one testable sentence separating a verdict that
may be `accepted` from one that must be `pending`. Candidate to beat: *a verdict may
be accepted only if it is reproducible from the item and the response alone, with no
model in the loop and no clock.* Check it against each tier-2 case: does a `check`
verdict that depends on a timeout, or a Math verdict that depends on random sample
points, still qualify? If not, the rule or the tier assignment is wrong — say which.

**R4.3 — tier 2, the checkers.** `check` code output (Phase 5), Math numeric/symbolic
equivalence (Phase 9), and visual tolerance (Phase 6.1, already a private versioned
tolerance policy). Do these three share enough to be one interface, or are they three
unrelated things that only look alike? For Math specifically: does WeBWorK-style
random-point evaluation count as deterministic when it samples? What makes a checker's
result **reproducible across machines** — pinned sample points, a fixed seed recorded
in the evidence, or a tolerance stated in the item?

**R4.4 — tier 3, the model.** For open text — an EMT scenario narrative, a written
rationale — what do assessment systems actually do, and which approaches beat "hand
the whole thing to a model"? Cover at minimum: rubric decomposition into
independently-checkable claims (so the model answers several small closed questions
instead of one open one), self-assessment against a revealed model answer, and
deferred human marking. Rank them on reliability and on how much of the verdict can be
promoted from `pending` to `accepted` without a human. What does the current
literature say about LLM-as-judge agreement with human markers on short constructed
response, and how much does rubric decomposition improve it?

**R4.5 — presentation.** How is a `pending` model suggestion shown so it never reads
as a grade? Round one's rule that a model gets no typographic voice of its own applies
directly. Answer: what the learner sees before accepting, what the accept action is,
what happens to a suggestion never accepted, and whether a pending mark may influence
selection or scheduling before acceptance (default: no).

**R4.6 — adaptability, which is the point.** Prove the design absorbs change without a
rewrite. Walk each of these through the proposed interface and say what changes:
(a) `sympy` replaces the hand-rolled Math checker; (b) a local model on the 7900 XTX
replaces a hosted one for tier 3; (c) a new item type needs a checker nobody has
written yet; (d) a tier-3 strategy becomes reliable enough that Weibao wants its
output auto-accepted — is that a config change, and **should** it even be possible?
Any answer requiring an edit to `score_response()` itself has failed the question.

**R4.7 — partial credit.** Do partial credit and confidence-weighted verdicts belong
here at all? The evidence log is append-only and dichotomous today, so this is a
one-way door. Note that tier 3 rubric decomposition produces per-criterion results
naturally, which is partial credit arriving through the back door — decide whether
that is stored as N boolean claims or as one fractional score, and cost each. Default
to no unless the case is strong.

### R5 — Lesson and question: what couples, what separates

**Context.** A bank today is one markdown file holding `## LESSON` and its items,
with `LESSON-REF` linking item to heading and backlinks rendering both ways.
`[LESSON-SRC:]` (shipped in 03-02) already allows the lesson to live in a **separate
file**, with the external source winning over an inline section when both exist. So
both shapes are buildable now. Nobody has decided which is the default, and the
research should decide it rather than leaving it to taste.

**R5.1** Which shape should be normal, and does the answer differ by subject? An EMT
chapter teaches forty items across many objectives; a CS lesson may own its three
exercises entirely. If the answer is per-subject, it is a subject-profile field, not
a global ruling.

**R5.2** **The lifecycle argument.** Lessons get rewritten for style; item identity
must survive edits (Phase 1's entire purpose — `[ID:]` plus a `[HASH:]` content
fingerprint, where `lesson_ref` is deliberately excluded from the fingerprint). Does
holding prose and items in one file cause churn, review noise, or accidental hash
drift in practice? What do documentation and courseware systems that separate
content from assessment do, and what breaks when they do?

**R5.3** What must stay **coupled** no matter which file things live in? Candidates:
the objective, the `[SRC:]` provenance, the `[[term]]` glossary scope, a `[!KEY]`
block's identity, and the LESSON-REF backlink. Name each as coupled or separable, and
say what the linter must check when the two sides live apart and drift.

**R5.4** If they separate, what is the **unit** on each side? Is a lesson file one
objective, one chapter, or one session's reading? Does an item belong to exactly one
lesson, and what breaks if it belongs to two?

**R5.5** Does separation help or hurt the **authoring loop**? A model writing a lesson
and a model writing items are arguably different jobs with different context needs
(Phase 3.2 seeding, Phase 11 authoring). Does splitting the files make generation
more reliable, or does it lose the coupling that keeps generated items on-topic?

---

## 3. Rules for this research pass

1. **Reject on the five non-negotiables** (`PLANNING-DIRECTIVES.md` §4), not on
   dependency cost. Round one's constraint relaxation is in force: dependencies, a
   build step, and non-Python components are all permitted where they earn it.
2. **Answer with verdicts, not surveys.** Every question gets a named recommendation
   and the reason it beat the runner-up. A comparison table with no verdict is an
   unfinished answer.
3. **Cost every recommendation** in plans, new lint codes, new blocks, and new
   dependencies. "It would be nice to have" is not a finding.
4. Where two answers are both good, **say so explicitly and recommend shipping both**
   behind one interface, per Directive §3 — with the interface named.
5. Verify claims about this codebase against `model.py`, `runtime.py`, `ROADMAP.md`,
   and `UI-SPEC.md` before asserting them.
6. **Name what you could not determine.** A confident wrong answer costs a phase.

---

## 4. Findings

### 4.1 Artifact index and slice status

The pass ran as five concurrent slices, one per question cluster.

| Slice | Questions | Artifact | Status |
|---|---|---|---|
| 1 | R1.1, R1.1a | `research/2026-08-10-lesson-style-catalogue.md` | **done** |
| 2 | R1.2 - R1.7 | `research/2026-08-10-style-registry-mechanics.md` | **done** |
| 3 | R2.1 - R2.3, R3.1 - R3.5 | `research/2026-08-10-enforcement-and-loose-threads.md` | **done** |
| 4 | R4.1 - R4.7 | `research/2026-08-10-tiered-verdicts.md` | **done** |
| 5 | R5.1 - R5.5 | `research/2026-08-10-lesson-item-coupling.md` | **done** |

Full verdicts live in the artifacts. This section records only what binds other
phases, the cross-slice reconciliations, and the rulings left open.

### 4.2 Cross-slice reconciliations

Two slices answered overlapping questions and did not agree. Recorded here rather
than smoothed over, because the winner is what the phases inherit.

**New blocks — one parse path, not three.** Slice 1 costed the registry at one new
block; slice 2 at three. Both independently arrived at `[!CHECK: <id>]`, an inline
placement anchor carrying no key and no scoring path, so `score_response()` is
untouched. The other two are not parse paths: `[!EXAMPLE]` is a callout *kind*, and
`## SCENARIO` is owed by Phase 9 (R3.2) whether or not any style uses it. **Ruled:
one new parse path, two additive entries against existing containers.**

**Check registry — closed, not open.** Slice 2 proposed six parameterized rule kinds
so style number eleven costs zero new lint codes. Slice 3 reached the same goal by a
tighter route: the check catalogue is **closed**, and a style file may enable,
disable, re-severity and parameterize checks but may never define one. `LINT_CODES`
is a published API and sprawl is the real scale risk. **Slice 3 wins; slice 2's rule
kinds are the runner-up and the parameterization vocabulary survives.**

**Prose-structure linting — the gap slice 2 flagged is closed.** Slice 2 could find
no prior art and marked its ordering rules unvalidated. Slice 3 confirmed the absence
(Vale, textlint, write-good and proselint lint sentences; they can only scope to
structure) and then supplied the mechanism: **markdownlint MD043**, a declared
heading structure. A style's declared section skeleton moves "worked examples precede
variations" out of model-judged and into a deterministic structural count.

### 4.3 Verdicts that bind other phases

**Styles (R1.1, R1.1a).** Ship five, in this order: `expository` (the parent every
other style inherits from, cost zero), `worked-example`, `checked-prose` (Execute
Program and Brilliant merged behind `predict_first` and a prose budget - Directive §3
done properly), `artifact-first` (Bottom Up ordering plus PRIMM pacing, which are
orthogonal and compose), `case-narrative` (ranked last only because it depends on
`## SCENARIO`). Four styles rejected with the no-cheap-fix reason named: Feynman
(every rule it contributes is semantic, so the contract is uncheckable), cookbook (its
weakness is its purpose; keep the Diátaxis split as a house rule), written Socratic
(branching is a second parser, Directive §4.2; unbranched it collapses into rhetorical
questions already banned by W7), explorable explanations (per-lesson bespoke
JavaScript is bank-authored executable code, refused by `VIS-01` and
`UI-SPEC.md:609`; it is also a renderer fork against Directive §4.2). Two reclassifications:
the atomic prompt sheet already ships as `[!KEY]` plus Anki export, and productive
failure is not a style but the `predict_first` flag.

**Registry mechanics (R1.2 - R1.7).** One file per style at `styles/<id>.md`, exactly
one inheritance level, `[STYLE-PARENT:]` other than `house` is an error. House
constrains the artifact, style constrains the sequence; the test is that a rule is
house iff violating it would still be wrong in every other style. A `lock` column on
house rows encodes the five non-negotiables and cannot be overridden, which is what
makes the registry safely model-writable. The authoring model receives **distilled
imperatives capped at seven, placed last**, plus one exemplar - not the style file
verbatim; adherence collapses past roughly ten simultaneous instructions and shows a
recency bias, and the `## Voice` zone is for the human and is never sent. Precedence
for style selection: lesson, then bank, then subject profile, then house. Two
operations must never be conflated: `render_style` (runtime, no model, permutation of
existing blocks only) and `restyle` (Phase 11, model, human-gated, produces a new
file). Mechanically impossible transforms are named: expository to case-narrative, to
Socratic, to worked-example, anything to Bottom-Up, and case-narrative to anything.

**`??? for math` is answered (R1.7).** It is **Worked Example → Variation →
Formalization** (`math-worked`): section equals one knowledge point, claim, then
`[!EXAMPLE]` annotated, then `[!CHECK]` varying one dimension, then `[!KEY]` stating
the formal result *after* the example. `math-explore` (Experience First, Formalize
Later) is the same four blocks inverted and costs one extra file, zero blocks, zero
codes, zero parser change - the cleanest Directive §3 case in the project.
`math-worked` is the default for first exposure. KaTeX is delivery, not form; the 6.1
SVG is a figure inside a section, not a style.

**Enforcement (R2).** Three cost classes, not two: structural counts over the parsed
heading tree and one shared lexical metrics pass both run on every lint, and only
discourse judgement is Phase 11. Severity is earned by construction - `error` only for
structural counts or author-controlled literal lists, a ceiling a style cannot raise,
and all eight of round one's errors survive. Every warning is calibrated against the
Phase 3.2 corpus before shipping enabled, with its false-positive rate recorded; above
roughly 20% it ships disabled by default. Local `<!-- style-ignore: -->` suppression
must exist, because the failure mode is that an unsuppressable warning gets its whole
category globally disabled, and suppression counts are themselves a report that
retires bad checks. Style `error` blocks a machine-authored write, never a human's
lint. Budget: the whole style pass under 50ms for a 5000-word lesson, asserted by test.

**Usage criteria (R3.1).** Five, each a property of the system rather than the person,
each a ratio with a stated denominator, none shown to the learner with a target:
corpus reach (Phase 3.2), return rate (10), gate outcome split (6.2), hint-ladder
depth distribution (6), style adherence density (11). Lesson-to-item transfer is the
most interesting measure and is not computable today; deferred with its cost recorded.

**`## SCENARIO` (R3.2).** Ordered `[STAGE:]` blocks with a **closed two-value advance
vocabulary**, `on-ack` and `on-item`. `on-elapsed` rejected against `UI-SPEC.md:105`;
`on-correct` rejected because it gates on a verdict. The reveal position is a derived
integer replayed from existing evidence, so a model authors the file but never moves
the pointer. No un-reveal, no answer locking. Five codes, zero new item types, zero
scorer change.

**The 6.2 gate (R3.3).** Build both, per Directive §3, but for a stronger reason than
the mastery-learning literature: a hard gate is theater on a plaintext file the learner
owns, so it is a claim the product cannot keep. The loop's value is the return, not the
wall, and a recorded skip preserves it *better* - skipped-and-unclear can be
prioritized, while a hard gate learns nothing. `[GATE: required|recommended|off]`. Skip
is a new `gate_skip` event type, verified additive against `evidence.py`, and
explicitly not a `response` carrying a null score.

**Long-lesson generation (R3.4).** Six stages: deterministic source selection,
outline-only, per-section drafting, **deterministic checks before any model critique**,
independent CoVe-style verification, human accept. Roughly nine model calls per lesson,
so authoring is a batch operation and the UI must say so. The cheapest real
anti-fabrication guard is a new `style.unsourced_specific` check - numerals, units and
doses require a `[SRC:]`. No benchmark for single-objective adherence exists as of
mid-2026; named as a gap rather than papered over.

**File layout (R5).** **Two-file is the default**, with a `lesson_layout:
"separate"|"inline"` subject-profile override - EMT and Math separate, CS inline,
because a Bottom-Up CS lesson *is* its exercises. The field governs scaffolding, the
authoring prompt and one warning; no parser, renderer or scorer branch. The brief's
stated worry was false and had to be re-argued: `content_fingerprint()`
(`model.py:259-294`) excludes `lesson_ref`, `objective` and every rationale field, so
rewriting a lesson for style **cannot** drift an item hash in either layout. The real
argument is concurrent writers - Phase 11 SC4 commits each autonomous write separately
and SC5 demands one-action reversibility, which is impossible without hunk surgery when
a style pass shares a file with seeding. The rule: **separate the prose, never the
item.** `[LESSON-SRC:]`'s arrow runs many banks to one lesson; reversing it imports the
Canvas item-bank failure, where editing an answered item breaks the bank-to-quiz link.
Unit: a lesson file is one chapter and one reading session, subdivided by `###`
headings which are the objective-sized, LESSON-REF-targeted generation unit. An item
belongs to exactly one lesson, true by construction today. Migration is `itembank
lesson split|inline`, pure text transforms, item chunks byte-identical, no id or hash
reminted.

**Tiered verdicts (R4).** The working hypothesis in §2 is **partially overturned**, and
the overturn is the finding. Reject `(verdict, authority, detail)`: it hands every
strategy the power to decide and then asks it not to. Adopt instead **two registries of
normalizers** with signature `(q, answer) -> str | None`, feeding the **unchanged**
`score_response()`. All three tier-2 checkers reduce to normalization - code to a
per-case outcome vector, math to an agreement vector at pinned points, visual to
tolerance-as-quantization - so the single `==` survives *literally*, not rhetorically.
Four accretion guards, strongest first: the return type has no channel for a verdict;
**authority is a property of the code path, not a declaration**; **tier 3 is not a
scorer strategy at all** but a peer of the human marker, outside `score_response()`
entirely; and a source-hash test pins the function.

Three facts the brief itself got wrong, verified against the code and changing the
answers: a mark is *already* a separate append-only event about a response,
`review_state` is *already* computed at read time, and `mark_event(rubric=...)`
*already* stores per-criterion results as N booleans. The one-way door of R4.7 was
built correctly in Phase 1 and does not need opening. The three claims the brief made
*do* hold: `score_response()` (`runtime.py:120-130`) is three lines ending in one `==`,
`short` returns `None`, and no model participates in any verdict - enforced at runtime
by `mark_event`'s `ValueError` on `marker != "human"` (`evidence.py:1058`).

**R4.2 - the candidate rule is right, its wording is wrong; tier assignments stand.** A
timeout is *not a verdict*: return `None` plus an `error_category`, the same
None-not-False discipline already in place. Sampling qualifies once the seed is derived
from the existing `content_hash`, making the sample points a pure function of the item.
Adopted wording: *re-running on another machine, from the recorded item version and the
response alone, must produce the same verdict; no model, and no input not derivable
from the item.*

**R4.3.** One thin interface, three implementations, no shared base class.
Reproducibility ranking: bounds stated in the item (primary), strategy name and version
in the evidence (interpretability, not reproducibility), recorded seed (weakest, avoid).
Phase 6.1's private tolerance policy needs its **version in the event**, or a bump
silently reinterprets history.

**R4.4 - promotability is a constant zero, not a spectrum.** Two decisive findings: LLM
judges are non-reproducible even at temperature 0, so tier 3 fails R4.2 on physics
*independently* of Directive §4.1; and judge bias survives explicit anti-bias prompting
(d=4.25). Ofqual (14 Jan 2026) independently forbids AI as a sole marker. Ranked
approaches: **self-assessment against a revealed model answer first** (g=0.55/0.664, and
a learner self-mark *is* a human accept, which dissolves the pending state rather than
managing it), deferred human marking second, rubric decomposition third - justified on
**accept ergonomics, not accuracy**, since the within-task A/B does not exist and the
one prompt-controlled study finds holistic matches atomic.

**R4.5 - presentation.** Self-mark first; the model suggestion sits behind a disclosure
control (`suggestion_reveal`, default `after-self-mark`, all three values shipped per
Directive §3). Never a number, never a fraction, never a check or cross glyph - a
`--pending` token only. Accept is the existing `mark_event`. Phase 8 adds a
`mark_proposal` event type and **must not widen the human-only guard**. A suggestion
never accepted stays pending forever. A pending mark influences nothing, but is not
nothing: it counts as an attempt, grants no mastery, and never advances an interval.

**R4.6 - adaptability.** (a) sympy is a config key plus a module; (b) swapping the tier-3
backend involves the scorer **not at all**, which is the proof the design is right; (c) a
registry miss leaves the item permanently pending and human-markable - it degrades to a
human, never to a false verdict, at zero cost; (d) auto-accepting tier 3 **must be
impossible, not off by default**, on four independent grounds including that no valid
gate variable exists, since model confidence is uncalibrated. Batch accept is the right
concession to ergonomics.

**R4.7 - partial credit.** N booleans. No fractional score, no confidence weighting. A
derived "4 of 5" computed at read time is fine.

**R4 costs:** 2 registries, 2 lint codes (`item.tolerance_unstated` as error,
`item.no_normalizer` as warning), 2 tests, 1 optional dependency (sympy), 1 config key,
1 event type. No new blocks, no parser change, no edit to `score_response()`.

### 4.4 Open rulings added by round two

Round one's rulings 1 - 6 stand (see `POST-RESEARCH-PROMPTS-2026-08-10.md`). Round two
adds:

| # | Ruling | Blocks | Default if unruled |
|---|---|---|---|
| 7 | `subject_profiles` is a *closed* object per `09-02-PLAN.md`, so adding `lesson_layout` is a registry version bump unless folded into 09-02 before 9 is planned | 9, 3.1 | fold into 09-02 |
| 8 | Is `[!KEY]` legal inside item rationales, or lesson-only? Changes `key.duplicate_id` scope | 3.1 | lesson-only |
| 9 | May `[!CHECK:]` reference an item in another bank? | 3.1, 6.2 | no - narrower, additive later |
| 10 | Does the style exemplar earn its prompt tokens? Untested | 11 | ship toggleable, measure |

### 4.5 What the research could not determine

Recorded so no phase inherits a confident wrong answer.

- **No verified 7900 XTX throughput figure exists** for any candidate model. Phase 8
  therefore owes an `itembank bench` command, and the roadmap must not carry an
  invented latency number. Recommendation is Qwen3-30B-A3B-Instruct-2507 Q4_K_M with
  gpt-oss-20b as a second backend, Vulkan over ROCm on gfx1100.
- No trustworthy open-weight **prose-quality** benchmark, so model choice must be
  settled by running our own 18-rule check over generated lessons.
- No benchmark for **single-objective adherence** in long generation (R3.4).
- executeprogram.com is JS-rendered and could not be read directly; its mechanics are
  sourced secondhand. Brilliant publishes no pedagogy document. Feynman has no primary
  source at all.
- The **Runestone Parsons-to-`build` mapping is inference**, and `artifact-first`'s
  rank-4 placement partly rests on it. Falsify early at plan time.
- The PreTeXt label-stability claim is inference from the PreTeXt Guide;
  runestone.academy returned 403.
- The seven-imperative prompt cap is extrapolated from format-compliance research, not
  measured on pedagogical structure.
- There is no real bank yet, so the R5.2 argument is structural against Phase 11's
  criteria, not observed churn.

---

## 5. Embedding plan — where round-two findings land

| Phase | Expected to absorb |
|---|---|
| **3.1** Lesson Rich Blocks, Glossary & Style | R1 in full — the style registry, the style-file shape, the house/style rule split, the new blocks any shipped style needs. R2 enforcement split. |
| **3.2** Seeding, Import & Provenance | R3.4 long-lesson generation, applied to the human-gated seeding loop. |
| **5** Check Item Type & Code Editor | R1.1 "Bottom Up" CS format, if it needs anything the `check` type does not have. |
| **6** Hint Ladder & Feedback Modes | R3.3 gate-versus-skip, if it changes cursor-hold semantics. |
| **6.2** Executable Textbook Loop | R3.3 in full; R1.1 Execute Program / Runestone loop structure. |
| **7** Selection Engine | R3.1 usage criteria that read from selection evidence. |
| **9** Subject-Invariant Loop | R1.7 the math lesson form; R3.2 `## SCENARIO` grammar. |
| **10** Retention, Pacing & Trends | R3.1 usage/adherence measures that are not streaks. |
| **11** Authoring Loop & Curriculum Auditor | R2 model-judged rules at registry scale; R3.4 generation; R3.5 local-model implications. |
| **8** Model Adapter | R3.5 local-model VRAM/latency implications; R4.3/R4.4 how a model-suggested mark is produced and presented without becoming a grade. |
| **1**-derived, cross-cutting | R4.1/R4.2 the comparison-strategy interface and the deterministic/judgement line — lands as an Extensibility Rule and as acceptance criteria on Phases 5, 6.1 and 9 rather than as its own phase. R4.5 partial credit touches the response schema and is one-way; if adopted it needs a `checkpoint:decision` at plan time. |
| **3**/**3.1**/**3.2** file layout | R5 in full — whichever way it lands is a format and lint decision, so it must be settled before 3.1 plans are written. |

---

## 6. Run sequence

1. `/gsd-explore` with §2 as the prompt. Findings land in
   `.planning/research/2026-08-10-*.md`.
2. Append verdicts to §4 of this file.
3. `/gsd-phase` to fold the verdicts into the affected phases (additive edits only,
   no renumbering).
4. Per phase, in roadmap order: `/gsd-discuss-phase <n>` → `/gsd-ui-phase <n>` if it
   has a surface → `/gsd-plan-phase <n>`.
5. **Stop.** Hand to DeepSeek V4 for `/gsd-execute-phase`, sequentially.
