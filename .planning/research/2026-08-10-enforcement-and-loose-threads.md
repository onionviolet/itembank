# Style Enforcement at Registry Scale, and Round One's Loose Threads

- **Created:** 2026-08-10
- **Covers:** Research Brief 2 questions **R2.1, R2.2, R2.3** and **R3.1 through R3.5**
- **Binding:** `.planning/PLANNING-DIRECTIVES.md` all six sections; brief §3 rules
- **Verified against:** `model.py` (lint, `LINT_CODES`, `parse_lesson`), `evidence.py`
  (event shapes, `KNOWN_EVENT_TYPES`, `response_event`), `.planning/ROADMAP.md`
  (Phases 3.1, 3.2, 6.2, 7, 8, 9, 10, 11 and the Extensibility Rules),
  `.planning/UI-SPEC.md` line 105 (calm progress, LOCKED),
  `.planning/research/2026-08-09-differentiators-d1-d2-d3.md` (the 18 + 5 rule split)

---

## 0. Verdict index

| # | Question | Verdict in one line |
|---|---|---|
| R2.1 | Cheap vs report-only | Three cost classes. Class A structural and Class B lexical both run on **every** lint; only discourse-level judgement is Phase 11. Registry scale costs nothing per lesson because **exactly one style applies to a lesson**; the real scale risk is code sprawl, killed by a **closed check registry**. |
| R2.2 | Prior art for structural prose linting | **None of Vale, textlint, write-good, proselint can do what we need.** They lint sentences and can *scope* to structure; they cannot reason over our block tree. Steal three named mechanisms, write ~250 stdlib lines ourselves, add zero dependencies. |
| R2.3 | False-positive posture | Severity is earned, not asserted: `error` only for checks with zero false positives **by construction**. Every warning is measured against the Phase 3.2 corpus before it ships enabled. Local suppression must exist, and **suppression counts are themselves a report** that retires bad checks. |
| R3.1 | Usage criteria | Five, all ratios with stated denominators, all read from the existing log, none shown to the learner as a goal. Owners: 3.2, 6.2, 6, 10, 11. |
| R3.2 | `## SCENARIO` grammar | Ordered `[STAGE:]` blocks with a **closed two-value advance vocabulary** (`on-item`, `on-ack`) the runtime evaluates. No clock. No un-reveal. No answer locking in v1. Five lint codes, no new item type, no scorer change. |
| R3.3 | Gate vs recorded skip | Weibao is right, and for a reason stronger than the pedagogy literature: **a hard gate is theater on a plaintext file the learner owns.** Soft gate plus a recorded skip is the only honest mechanism, and it is better instrumented. New `gate_skip` event type. |
| R3.4 | Long lesson generation | Outline-first with per-section objective anchoring, section-by-section generation, **deterministic checks before any model critique**, then an *independent* verification pass, then human accept. 2 + N + 1 calls. Batch, never interactive. |
| R3.5 | Local model at 24GB | **Qwen3-30B-A3B-Instruct-2507 Q4_K_M** default, **gpt-oss-20b** second registered backend, **no dense 32B on this card**. Vulkan over ROCm on gfx1100. Phase 8 must **measure** and store tok/s rather than assume it. |

---

## 1. R2.1 — What runs on every lint, and what waits for Phase 11

### 1.1 The three cost classes

Every one of the 23 rules D3 identified falls into one of three classes. The class,
not the rule's importance, decides where it runs.

**Class A: structural.** Computed from the already-parsed lesson tree. Heading text
and heading bodies are parsed today (`model.py` heading parse, cited in D3 as
`model.py:236-250`), so these are counts over data already in memory. Zero
additional parsing. D3's E2, E3, E6, E7, E8 and all of the `## SCENARIO` checks in
§5 below are Class A.

**Class B: lexical.** One pass over the prose text of each section producing a
shared metrics record: sentence spans, word counts, paragraph blocks, syllable
counts, code-span masks. Every regex and every count then reads that record rather
than re-scanning. D3's E1, E4, E5 and W1 through W10 are Class B. The whole class
costs **one** tokenization pass, not eighteen.

**Class C: discourse.** Requires understanding what a section *claims*, whether an
example illustrates it, whether ordering runs familiar to new. D3's M1 through M5.
These are Phase 11, report-only, and they stay report-only permanently.

### 1.2 Verdict

**Class A and Class B both run on every `itembank lint`. Only Class C waits.**

This is a change from the natural reading of D3, which implies the 8 errors run
cheaply and the 10 warnings are somehow more expensive. They are not. The warnings
are more *false-positive-prone*, which is a severity question (§3), not a cost
question. Splitting the run by cost when the real split is by confidence would put
the linter's most useful signal behind an opt-in flag nobody sets.

Costing, for a 5000-word lesson: Class A is O(sections), Class B is O(characters)
with a constant of roughly a dozen compiled regexes. Both are microseconds to low
milliseconds in CPython. **Budget: the entire style pass must stay under 50ms for a
5000-word lesson**, asserted by a test with a generated fixture. If a future check
cannot meet that, it is Class C by definition.

### 1.3 The registry-scale answer, which is the part the question is really asking

At N styles the naive fear is N times the work. That fear is wrong, and the real
risk is elsewhere.

**Per-lesson cost does not scale with N.** A lesson declares exactly one style. The
linter resolves house rules plus that one style's overrides and runs one check set.
Ten styles cost the same per lesson as one.

**Registry validation does scale with N, and is trivial.** Every style file's
`## Rules` table must be checked for rows naming a check the linter does not
implement (D3 already has `style.unknown_rule` for this). That is O(total rows)
over files of a few dozen lines each, and it runs once per lint invocation, not per
lesson. Cache it keyed on file mtime if it ever shows up in a profile. It will not.

**The thing that actually breaks at registry scale is lint-code sprawl.** If style
authors can invent checks, `LINT_CODES` grows unboundedly, and `LINT_CODES` is a
published API namespace an authoring agent branches on (`model.py`: "adding a code
is additive, renaming one is a breaking change for every consumer"). Ten styles
each inventing four codes is forty codes nobody can consume.

**Verdict: the check registry is closed. A style file may enable, disable,
re-severity, and parameterize checks from a fixed catalogue. It may not define
one.** Adding a check is a code change in `model.py` plus a `LINT_CODES` entry,
reviewed once, available to every style. Adding a *style* is a file, with no code
change, no new lint code, and no renderer change, which is exactly what Phase 3.1
success criterion 3a demands.

Three new codes are needed to police the registry itself:

| Code | Severity | Meaning |
|---|---|---|
| `style.unknown_rule` | error | already specified in D3: a row names a check the linter does not implement |
| `style.unknown_parameter` | error | a row sets a `k=v` the named check does not accept |
| `style.parameter_out_of_range` | error | e.g. `max=0` on a sentence-length check |

A style may not raise a check above the severity ceiling the check declares in code
(§3.1). Attempting to is `style.parameter_out_of_range`.

**Cost of R2.1's recommendation:** roughly 250 lines in `model.py` (one shared
metrics builder, a check catalogue as a table of callables, a resolver that merges
house plus style), 3 new lint codes on top of D3's 18 plus `style.unknown_rule`,
zero new dependencies, one performance test. No new plan; it lands inside Phase 3.1's
existing style plan.

---

## 2. R2.2 — Prior art for linting prose *structure*

### 2.1 What the four named tools actually do

Verified this session against tool documentation and repositories:

**Vale** (Go, markup-aware). Its extension points are token-level and
occurrence-level: `existence`, `substitution`, `occurrence`, `sequence`,
`readability`, `conditional`. Its genuinely relevant capability is **scoping**: a
rule can be restricted to headings only, or to paragraphs, or a section can be
ignored entirely, and it can flag paragraphs exceeding a word count. That is
structure-*aware sentence linting*, not structure linting. Vale cannot express
"this section introduces an abstraction before any example."

**markdownlint** (Node). This is the closest real prior art for structure, and it is
closer than Vale. `MD001` enforces heading-increment cadence. `MD024` catches
duplicate heading content, with a `siblings_only` option. **`MD043` enforces a
required heading structure** against a declared list. That last one is the shape a
style's declared section skeleton should take, and it is worth naming as the model.
markdownlint explicitly does not touch spelling, grammar, or sentence structure.

**textlint** (Node, pluggable, AST-based). More flexible than markdownlint, and its
AST access means a plugin *could* in principle walk document structure. In practice
its rule ecosystem is sentence-level. Writing the checks we need as textlint plugins
is not cheaper than writing them in Python; it is the same work in a second language.

**write-good** and **proselint** are sentence-level only. proselint is Python, which
is the one point in its favour, but its rules are a curated set of usage advisories
and it offers nothing structural.

### 2.2 What none of them can do for us

Four of our wanted checks are unreachable from any of the above, because they depend
on **our** block semantics, not on general markdown:

1. **Example-before-abstraction ordering.** Requires knowing which blocks are
   examples. We will know, because `[!EXAMPLE]` and `[!KEY]` are our own callout
   markers. No general tool knows this.
2. **Idea density per section.** D3's W10 is a structural proxy (a long section must
   contain an example marker). That proxy is only computable against our callout
   vocabulary.
3. **Term-introduction discipline** (D3 W9: first prose use of a `## TERMS` term must
   be a `[[term]]` reference). Depends on D1's glossary block.
4. **Every style rule that is parameterized by the style registry**, since no external
   tool knows about our style resolution.

### 2.3 The disqualifying constraint, which is not dependency cost

Brief §3.1 relaxed dependency cost, so "it is Go/Node" is not by itself a rejection.
The disqualifying facts are two others:

- **A second lint reporting channel.** `lint()` returns `(errors, warnings)` as
  `LintError` records with dotted codes, and `schemas/lint_error.schema.json` publishes
  that shape. An external linter produces its own findings in its own vocabulary,
  which either gets translated (a mapping layer that goes stale) or shown separately
  (two lint outputs, and the authoring agent in Phase 11 now has two contracts to
  satisfy). Phase 11 success criterion 1 requires a model to complete the cycle
  "from the contract alone." Two contracts breaks that.
- **The offline and packaging posture.** Phase 2.1 ships a `.pyz`; Phase 13 a Tauri
  shell over a Python sidecar. Bundling a Go or Node binary per platform to run a
  check we can write in 250 lines is a poor trade even under relaxed constraints.

### 2.4 Verdict

**Write our own. Zero external prose linters. Steal three named mechanisms:**

1. **From Vale: the minimum alert level.** A configurable severity floor so a project
   can run at errors-only without editing rules. This is the single most important
   anti-fatigue affordance any of these tools has.
2. **From markdownlint MD043: the declared section skeleton.** A style may declare an
   expected heading structure and the linter checks the lesson against it. This is how
   a style like case-narrative or worked-example-then-variation enforces its *shape*
   without any semantic understanding at all, and it is the answer to "how does a
   style enforce ordering cheaply." Worked example then variation becomes a skeleton,
   not a discourse judgement, and moves from Class C to Class A.
3. **From proselint: curation posture.** Ship only rules with a defensible basis;
   resist the temptation to add a rule because it was easy.

**Cost:** included in the ~250 lines of R2.1. The skeleton check is a further ~40
lines plus two codes, `style.section_skeleton_mismatch` (severity declared by the
style, default warning) and `style.section_skeleton_malformed` (error).

**This is a genuine finding for Phase 3.1:** the declared-skeleton mechanism moves
part of D3's M4 and M5 (ordering rules, previously model-judged) into deterministic
territory for any style willing to declare its shape. Not all of it. A skeleton
cannot tell you an analogy maps correctly. But "worked examples precede variations"
is a skeleton, and skeletons are free.

---

## 3. R2.3 — The false-positive posture

The research consensus on static analysis is unambiguous and directly transferable:
high false-positive rates produce alert fatigue, and fatigued users **ignore or
disable the tool entirely** rather than tuning it. Reported figures for SAST tools
run to roughly half of findings being non-actionable when unconfigured, and a
majority of warnings in studied corpora were never addressed. Warning
*actionability* correlates strongly with fix rate. A style linter is a worse case
than a code linter, because the ground truth is a matter of taste and the author is
one person who can delete the rules file.

Five rules, in force from Phase 3.1.

### 3.1 Severity is earned by construction, not asserted

**A check may declare `error` only if its false positives are impossible by
construction**, meaning it counts structure or matches an author-controlled literal
list. Everything that pattern-matches natural language caps at `warning`, and the
cap is a property of the check in code that a style file cannot raise.

Checked against D3's split: E1 (sentence over 28 words), E2, E3, E6, E7, E8 are
structural counts and qualify. E4 (filler blocklist) matches a list the author
writes in `## Blocklists`, so a false positive is the author's own list being wrong,
which is actionable and correct. E5 (no exclamation marks in prose) is a literal
character check with a code-span exclusion. **All eight D3 errors survive the rule.**
W1 (passive-voice heuristic regex) and W6 (Flesch) are exactly the checks that must
never be errors, and D3 already had them as warnings for the right reason. The
existing split is sound; this rule makes it a law rather than a judgement call.

### 3.2 Every warning is measured before it ships enabled

Phase 3.2 lands a real EMT/Math/CS corpus before Phase 5. **Phase 3.1 owes a
one-time calibration run**: execute all checks over that corpus, record per-code hit
counts, hand-adjudicate a sample of 30 hits per code, and record the false-positive
rate in the phase artifact.

- FP rate above ~20 percent: the check ships **disabled by default**, present in the
  catalogue, opt-in per style.
- Hit count near zero across the corpus: the check is not earning its place; note it,
  keep it if cheap.
- The recorded numbers go in the phase artifact so a later disagreement argues with
  data instead of taste.

This costs one task in Phase 3.1 and is the difference between eighteen rules and
eighteen defensible rules.

### 3.3 Suppression must be local, cheap, and reasoned

Steal markdownlint's inline disable. Syntax:

```
<!-- style-ignore: style.passive_voice — quoted from the protocol verbatim -->
```

Scoped to the next block. Line-scoped and file-scoped variants exist; a file-scoped
suppression of a check is allowed but reported (§3.4).

The failure mode this prevents is precise: **an unsuppressable warning gets the whole
category disabled.** A learner or author with no local escape hatch reaches for the
global switch, and then a hundred good findings die with the one bad one.

### 3.4 Suppressions are evidence, and they retire bad checks

`itembank lint --style-report` prints per-code finding counts **and per-code
suppression counts** across a bank. A check suppressed more often than it is heeded
is a check that is wrong, and the report says so without anyone needing to notice.
This is the self-correcting loop that keeps the registry honest at N styles, and it
is about 30 lines because the data is already being collected.

### 3.5 Style severity never blocks a human

D3 proposed style errors blocking DIFF in the authoring loop. Keep that, and bound it:

**Style `error` severity blocks a machine-authored write (Phase 11's gate). It never
blocks a human's own lint run, which reports and exits zero.**

The asymmetry is the point. A generating model should be held to the contract
strictly because it costs nothing to regenerate. A human writing a lesson at 11pm
should not be stopped by a 29-word sentence. Phase 11 already owns an autonomy
ladder; this is the same idea applied to style. Cost: one flag on the lint call
already threaded through the authoring loop.

---

## 4. R3.1 — Five usage criteria read from the evidence log

Constraints: read from the log that exists (`response`, `retraction`, `mark`,
`day_tick`, plus Phase 3.1's `term_lookup` and `key_review`); not vanity; not
punitive; `UI-SPEC.md` line 105 is LOCKED (no points, badges, levels,
streak-recovery prompts, countdown pressure, celebratory motion).

**The design rule that makes all five non-punitive: every criterion is a property of
the system, not of the person.** Each is a ratio with a stated denominator; none is a
consecutive-day count; none decays; none is displayed to the learner with a target
line. They live in the auditor and report surfaces, not the cockpit. A criterion the
learner can fail by taking a week off is a streak wearing a lab coat.

| # | Criterion | Definition | Reads | Owner |
|---|---|---|---|---|
| **U1** | **Corpus reach** | Fraction of distinct `item_id`s in the bank with at least one `response` event, and fraction of distinct `objective`s likewise. | `response.item_id`, `response.objective` | **3.2** |
| **U2** | **Return rate** | Of objectives whose first `response` is older than 14 days, the fraction with any `response` in the last 30 days. | `response.objective`, `response.ts` | **10** |
| **U3** | **Gate outcome split** | Share of declared inline gates cleared versus explicitly skipped, and mean accuracy on the gated objective's later items in each arm. | `response`, `gate_skip` (§6) | **6.2** |
| **U4** | **Ladder depth distribution** | Distribution of `hint_tier` at the first correct response per objective. | `response.hint_tier`, `response.score` | **6** (computed), reported by **10** |
| **U5** | **Style adherence density** | Style findings per 1000 words of lesson prose, per code, across the bank, trended by commit. | lint output over the bank, not the log | **11** |

### Why each one is not vanity

**U1** measures whether the bank we spent Phase 3.2 building is being used at all.
The failure it detects is real and likely: a 2000-item corpus where 200 items carry
every attempt. It is the direct answer to round one's Q9 finding that no criterion
anywhere measures actual use.

**U2** is the only criterion that tests the *retention claim*. Phase 6.2 criterion 4
asserts that an idea returns through the normal queue. U2 is that assertion measured
rather than promised. Low return rate means the scheduler is not surfacing old work,
which is a system defect.

**U3** is a design measure, not a learner measure. It answers the question §6 leaves
open: does a soft gate work. If skipped ideas show materially worse later accuracy,
the default gate strength should change. If they do not, the gate was decorative.
Either answer is worth having, and neither is about the learner's virtue.

**U4** is a health signal for the hint ladder. Everything resolving at tier 0 means
the ladder is decoration and the items are too easy. Everything bottoming out at the
last tier means the material is mis-scoped against the lesson. This is the cheapest
diagnostic for the teaching loop we have and it needs no new field.

**U5** is the only one that measures **adherence**, which is D3's entire claim. A
style contract nobody follows is decoration. It reads from lint over the bank rather
than the log, which is a deliberate exception: adherence is a property of content,
and content is not in the evidence store.

### Optional sixth, costed and not recommended for v1

**U6, lesson-to-item transfer:** share of responses on items with a `lesson_ref`
where the lesson was opened in the same `session_id`. This is the most interesting
measure on the list and it is **not currently computable**: no lesson-view event
exists. Cost is one new event type plus a write on reader render, which is a write
on a read path and needs care about noise. Recommend deferring to Phase 10 and
deciding then, rather than adding a write path in Phase 3.

---

## 5. R3.2 — The `## SCENARIO` staged-reveal container

### 5.1 How medical education actually phases a case

Verified: the pattern is called **progressive disclosure** or an **unfolding case
study**, and it is well established in pharmacy therapeutics and nursing simulation
curricula. Two properties matter for us, and both are load-bearing:

1. **The phasing is authored, and it advances at decision points, not on a clock.**
   Disclosures follow the learner's action. The rhythm is a property of the case
   design, fixed before the learner arrives.
2. **Earlier information stays available.** The case unfolds forward; it does not
   hide what was already given. Progressive disclosure is a reasoning exercise, not
   a memory test.

A third pattern exists in high-stakes testing, where sequential items lock prior
answers once the next reveal occurs. We should **not** copy it (§5.5).

### 5.2 Grammar

A `## SCENARIO` is a lesson heading subtype. Its body is a sequence of `[STAGE:]`
blocks. Everything inside a stage is ordinary lesson content already in the grammar:
prose, tables, callouts, figures, `[[term]]` references.

```
## SCENARIO: Chest pain at a construction site
[SCENARIO-ID: emt-scn-014]

[STAGE: dispatch]
You are dispatched to a construction site for a 54-year-old male
complaining of chest pain.

[STAGE: on-scene | advance: on-ack]
The patient is seated, diaphoretic, and speaking in short sentences.

| Vital | Value |
|---|---|
| BP | 148/92 |
| HR | 112 |

[STAGE: after-assessment | advance: on-item Q7 Q8]
The patient reports the pain began at rest and radiates to the jaw.

[STAGE: reassessment | advance: on-item Q9]
Five minutes after nitroglycerin the pain is unchanged.
```

Rules of the grammar:

- Stages are **ordered by position in the file**. There is no jump, no branch, no
  conditional next-stage in v1. Branching is a second traversal model and would be a
  second reader; if it is ever wanted it is a later additive field on the stage, not
  a v1 feature.
- `advance:` on a stage declares the condition for revealing **the next** stage. The
  first stage is always revealed on open, so its `advance` governs stage two.
- The final stage takes no `advance`; one is an error.
- `advance` defaults to `on-ack` when omitted.

### 5.3 The advance vocabulary is closed, and has exactly two values

| Value | Runtime condition |
|---|---|
| `on-ack` | The learner activates a labeled continue control. The activation is recorded. |
| `on-item <item-ref>...` | Every listed item has a scored `response` event in the current session. |

**Rejected: `on-elapsed`.** A clock-based reveal is countdown pressure, which
`UI-SPEC.md` line 105 forbids as LOCKED, and it makes the reveal position
irreproducible across a resumed session. Rejected on the accessibility gate
(Directive §4.5), not on preference.

**Rejected: `on-correct`.** Advancing only on a *correct* answer makes the scenario a
gate on verdict rather than on engagement, and pairs badly with the honest-skip
posture of §6. `on-item` requires an attempt, not a success. A learner who gets Q7
wrong still learns what happened next, which is what a case is for.

### 5.4 How the runtime stages the reveal without a model choosing the pace

This is the Directive §4.1 argument, stated so it can be checked:

1. The stage list and every `advance` condition are **authored text in the bank
   file**, parsed once by the one parser at read time.
2. The runtime holds a single integer, the highest revealed stage index for this
   scenario in this session, and derives it from evidence that already exists:
   `response` events for `on-item`, an ack record for `on-ack`. **The reveal position
   is derived, never stored**, satisfying Extensibility Rule 5, and a resumed session
   reproduces it exactly by replay.
3. A model may **author** a scenario. Authoring is human-gated by Phase 3.2 criterion
   2. Once the file exists it is fixed text. **No model is consulted at read time and
   no model can move the pointer.**
4. The reveal condition is not a verdict and produces no evidence of correctness. It
   consumes verdicts; it never creates one. `score_response()` is untouched.

Non-JS degradation, which the accessibility gate requires: with JavaScript off, all
stages render in document order with each `advance` condition rendered as a labeled
marker ("continues after Q7, Q8"). The reveal is an enhancement over a document that
is already complete and readable. This is also what print CSS gets for free.

### 5.5 Two deliberate non-features

**No un-reveal.** A revealed stage stays visible and scrollable. Hiding earlier
information turns a reasoning exercise into a memory test, matches the progressive
disclosure literature, and is required for the no-JS and print paths to be coherent.

**No answer locking in v1.** High-stakes sequential testing locks prior answers once
the case advances. We should not: the evidence log is append-only with an existing
`retraction` event type, and a lock would be a second mechanism for a problem that
mechanism already handles. Record it as a possible later per-scenario flag.

### 5.6 Lint codes and cost

| Code | Severity | Meaning |
|---|---|---|
| `scenario.no_stages` | error | a `## SCENARIO` containing no `[STAGE:]` block |
| `scenario.unknown_advance` | error | an `advance:` value outside the closed vocabulary |
| `scenario.advance_item_unknown` | error | `on-item` names an item that is not in this bank (mirrors `item.lesson_ref_unknown`) |
| `scenario.advance_on_last_stage` | error | the final stage declares an `advance` that can never fire |
| `scenario.single_stage` | warning | a one-stage scenario is a lesson section wearing a costume |

**Cost:** one additive block in the parser, 5 lint codes, one reader affordance, one
derived-pointer helper in `runtime.py`. **Zero new item types** (Phase 9 criterion 7
already asserts the six existing types cover the widget shapes), **zero scorer
changes**, one byte-identical no-op fixture per Extensibility Rule 3. Lands whole
inside Phase 9's existing plan set.

---

## 6. R3.3 — The executable textbook gate

### 6.1 What the pedagogy literature supports, and its limit

Mastery learning is well evidenced: a learner demonstrates competence on prerequisite
material before advancing, and falls back into support when they do not. Content
gating is a standard self-paced course mechanism. That is real, and it is the case
*for* a gate.

The literature's limit for us is that essentially all of it studies settings where
the *institution controls access to the material*. That is not our setting.

### 6.2 The decisive argument, which is a property of this product

**A bank is a markdown file the learner owns, on their own disk, with no telemetry
and no cloud (Directive §4.3).** A hard gate can be defeated by opening the file in
any text editor. So a hard gate is not a constraint; it is a **claim of a constraint
that the product cannot keep**. Shipping one would mean shipping a lie, in a product
whose entire differentiator is that the lock is honest structural state rather than
model reluctance (Phase 8 criterion 6).

That reframes the question. It is not "hard gate versus soft gate." It is "an
unenforceable lock versus an honest default."

### 6.3 Does a soft gate destroy the loop's value?

**No, and the roadmap already says why.** Phase 6.2 criterion 4 locates the loop's
value in the *return*: an idea cleared inside a lesson reappears later through the
normal retention queue. The value is the queue, not the wall.

A recorded skip preserves that entirely. A skipped idea still produces an event, so
it still enters the scheduler, and it can enter with **higher** priority than a
cleared one, because unclear-and-skipped is exactly the state most in need of return.
A hard gate cannot express that state at all: a learner who cannot proceed simply
stops, and the system learns nothing.

**So the soft gate is not a weakened hard gate here. It is a strictly better
instrumented mechanism**, and this is the finding rather than a restatement of
Directive §3.

### 6.4 Verdict, and the shape

Weibao's rule is right here. Ship both, behind one declaration:

```
[GATE: required]      # the default gate is presented and skipping requires confirmation
[GATE: recommended]   # the default; presented, one-click continue, skip recorded
[GATE: off]           # no gate on this block
```

Declared per gated block, defaulting per lesson, defaulting per subject profile.
`required` is honest because the copy is honest: it says the check is expected, not
that continuing is impossible. Phase 6.2 criterion 5 already mandates that a learner
can always read ahead by explicit recorded choice, so `required` **must not** mean
locked. It means confirm-and-record.

### 6.5 The skip must be its own event type, not a response

**New event type `gate_skip`, added to `KNOWN_EVENT_TYPES`.** Verified additive:
`evidence.py` line 428 already skips unknown event types with a warning rather than
failing, and every consumer filters on `event_type != RESPONSE_EVENT_TYPE`
explicitly (lines 461, 594, 785, 877, 1107). `EVENT_SCHEMA_VERSION` does not need to
change.

It must not be a `response` event with a null score. A skip is not an attempt.
Recording it as one would corrupt `attempt_number` (which `dedupe_key` depends on),
pollute accuracy denominators, and make `score: None` ambiguous against the existing
and load-bearing meaning of `None` for an unmarked constructed response.

Fields: `event_id`, `ts`, `session_id`, `item_id`, `item_ref`, `bank`, `objective`,
`subject`, `lesson_ref`, `gate_strength`. **No `score` field at all**, so no consumer
can accidentally average it.

**Non-punitive by construction:** a skip is never rendered as a failure, never
reduces any displayed number, and produces no prompt to come back. Its only effect is
to raise the objective's scheduling priority, which the learner sees as the idea
returning sooner, framed as a return and not as a penalty.

**Cost:** 1 event type, 1 additive block attribute, 1 scheduler input, 1 lint code
(`lesson.gate_without_item`, error, a gate declaring no check). Lands in Phase 6.2.

---

## 7. R3.4 — Lesson generation at length

Evidence gathered this session, with the caveat that several figures came from search
summaries rather than primary tables and are marked below.

### 7.1 What the literature actually supports

**Outline-first works, but the outline alone is not what works.** LongWriter and its
AgentWrite pipeline (arXiv 2408.07055, ICLR 2025) establish plan-then-write for very
long output. DOC (Yang et al., ACL 2023, arXiv 2212.10077) is the more useful result
for us: its gain over a coarser-outline baseline comes from a **controller that
re-checks generation against the outline mid-stream**, not from having an outline.
STORM (NAACL 2024) is the closest non-fiction analogue, doing research then outline
then grounded section writing. *Reported percentage-point gains for DOC and STORM
came from search summaries, not primary tables; treat the direction as established
and the magnitudes as unverified.*

**Carry-forward has no clean winner, and at our length it does not matter much.**
AgentWrite carries full prior text; "Lost-in-the-Middle in Long-Text Generation"
(arXiv 2503.06868, 2025) shows that degrades as prior text grows. At 1500 to 3000
words we are below the regime where that bites.

**Retrieval alone does not stop fabrication.** The best-evidenced mitigation is a
**separate, independent verification pass**: Chain-of-Verification (Dhuliawala et
al., ACL Findings 2024, arXiv 2309.11495) generates verification questions and
answers them independently of the draft, specifically so the model cannot re-confirm
its own error. LLMRefine (2024) supports separate-model critique over same-model
self-critique for factuality. Self-Refine (NeurIPS 2023) shows real gains but with
documented self-bias on factual tasks. FActScore (EMNLP 2023) and ALCE (EMNLP 2023)
are the measurement instruments.

**Scope drift is the least-benchmarked area of the five.** There is no benchmark for
single-learning-objective adherence as of mid-2026. The one direct hit found,
"Human-in-the-Loop Control of Objective Drift in LLM-Assisted CS Education" (arXiv
2604.00281, 2026), treats human checkpoints as the current answer rather than an
automated fix. Bloom's-taxonomy prompt conditioning alone was found insufficient.
**Name this as a genuine gap rather than papering over it.**

**A bespoke style contract needs its own deterministic checker.** IFEval, FollowBench
and IFBench (Pyatkin et al., NeurIPS 2025) all show instruction-following degrading
on constraint types outside a model's tuned set. Our 18 rules are exactly such a set.
This is independent confirmation that D3's linter, not prompt trust, is the
enforcement mechanism.

### 7.2 The recommended pipeline

Stages, with what is deterministic marked, because the deterministic stages are free
and catch a different error class than any model pass.

**Stage 0, source selection (deterministic, human or retrieval).** The objective and
the `[SRC:]` passages are chosen before any generation. **The model never selects its
own sources.** Phase 3.2's `## SOURCES` registry is the input.

**Stage 1, outline only (1 call).** Output is a section skeleton: N headings, one
claim sentence per section, and per section the `[SRC:]` locators that section will
use. Small, cheap, and human-reviewable. This is where scope drift dies, because the
whole lesson's scope is visible on one screen before a word of prose exists.

**Stage 2, section-by-section generation (N calls).** Each call receives: the resolved
style contract, the full outline, the section's claim and its assigned `[SRC:]`
passages, and the previous section's text. Full prior text while the draft is under
roughly 2000 words, previous section plus outline beyond that.

**Stage 3, deterministic checks (0 calls).** Run before any model critique, because
they are free:
- the 18 style checks plus the declared skeleton (§2.4)
- Phase 3.2's paraphrase winnowing at 8 consecutive words and Jaccard 0.25
- **outline conformance**: the draft's headings match the approved outline
- **source conformance**: the draft cites only `[SRC:]` entries the outline declared
- **objective scope proxy**: each section's claim sentence contains at least one term
  from the objective's `## TERMS` scope
- **`style.unsourced_specific`** (new, warning): a sentence containing a numeral,
  a unit, or a dose must carry a `[SRC:]` locator. This is the cheapest real
  anti-fabrication check available to us, because invented specifics are the
  fabrication class that actually harms an EMT learner, and it is a regex plus a
  locator lookup.

**Stage 4, independent verification (1 call).** CoVe-shaped. Each factual sentence
becomes a question answered **only from the supplied passages**, by a call that does
not see the draft's reasoning. Mismatches are flagged, never auto-corrected.

**Stage 5, human accept, section at a time.** Phase 3.2 criterion 2 already requires
this. Nothing above changes it.

### 7.3 Verdict and cost

**2 + N calls plus 1 verification call. At N of 6, roughly 9 calls per lesson.** At
the local-model throughput in §8, that is minutes, not seconds.

**Therefore: the authoring loop is a batch mode, not an interactive one, and the UI
must say so.** A progress surface with per-section state, resumable, that never
pretends a lesson appears on a keystroke. This is a Phase 11 UI consequence that
falls straight out of the arithmetic and should be recorded there.

Same pipeline serves Phase 3.2's seeding loop with N of 1 and a shorter Stage 2,
which is why it is one pipeline and not two.

**What I could not verify:** exact DOC and STORM improvement magnitudes; a claimed
"100 percent hallucination elimination" result (arXiv 2412.05223) that should be
treated as oversold until read; the existence of any benchmark for single-objective
adherence, which appears genuinely not to exist.

---

## 8. R3.5 — The 7900 XTX at 24GB, and what Phase 8 must assume

### 8.1 Verdict

**Default: Qwen3-30B-A3B-Instruct-2507 at Q4_K_M** (MoE, 30.5B total, ~3.3B active,
roughly 17 to 19GB of weights, IFEval 84.7 per its own model card). MoE is not a
preference here, it is the requirement: a 9-call authoring pipeline and interactive
hint generation on the same card are both bounded by decode speed, and ~3B active
parameters is the only way either is tolerable.

**Second registered backend: gpt-oss-20b** (OpenAI, August 2025, arXiv 2508.10925),
native MXFP4 at roughly 12 to 13GB, with KV cache small enough that a 128K context
fits inside 24GB. This is the long-prompt backend: it has the headroom the authoring
pipeline's style-contract-plus-passages prompt wants.

**Do not ship a dense 32B on this card.** Qwen3-32B at Q4_K_M is 19 to 20GB of
weights, leaving under 5GB for KV at a 12K prompt. It will OOM at the worst moment
and it decodes slowest of the candidates.

**Backend: Vulkan, not ROCm, by default on gfx1100.** An open llama.cpp issue
(#20934, filed around March 2026) documents ROCm decode throughput materially below
Vulkan on the 7900 XTX with no parity reached. This inverts the usual assumption and
should be written down before someone "fixes" it the wrong way. vLLM's ROCm support
did become first-class in January 2026 (AMD CI pass rate 37 percent in November 2025
to 93 percent in January 2026, blessed pip wheel, no Docker required), but its
advantage is batching, which a single-user sequential workload does not use. Stay on
llama.cpp or Ollama.

Gemma 3 27B Q4_K_M (~15 to 16GB) is the reasonable dense fallback if MoE output
quality disappoints on prose.

### 8.2 What Phase 8 must change

**1. Phase 8 owes a measured benchmark, not an assumed one.** No verified tokens per
second figure exists for any of these models on a 7900 XTX. The only solid anchor
found was roughly 100 tok/s decode for a 7B Q4 model on that card. Everything for the
20 to 32B class is extrapolation. **Add an acceptance criterion: `itembank bench`
measures prefill and decode on the configured backend and records the result into
settings; every latency-dependent behaviour reads that recorded number.** This is
cheap, it is honest, and it means the roadmap never carries a made-up figure.

**2. Cap adapter prompts at 8K tokens by policy.** The tier-gate hint prompt (item,
key, rationale, learner answer, tier instruction) is 1 to 2K, comfortably inside. The
cap exists so a future prompt-assembly change cannot silently walk into the VRAM
ceiling. Assert it in a test.

**3. Hint latency is the binding constraint, and the fix is three specific things.**
A hint is interactive. A 200-token hint at a plausible 20 to 40 tok/s is 5 to 10
seconds, which is too slow. Therefore, as Phase 8 acceptance criteria:
   - **stream tokens** to first paint,
   - **keep the model resident** (Ollama `keep_alive`), since cold load of a 17GB
     model dwarfs generation,
   - **cap hint length at roughly 80 tokens in the tier contract.** A tier-bounded
     hint should be short anyway. The constraint and the pedagogy agree, which is the
     good case.

**4. Authoring and hinting cannot be concurrent on one card.** Both want the same
VRAM and Ollama serves one model at a time. **Config declares one active local model;
the authoring loop is a foreground mode that pauses model-generated hinting**, which
degrades exactly the way Phase 8 criterion 3 already specifies for an unreachable
model. Per Directive §3, ship the alternative too: a hosted backend for authoring
while the local model serves hints is a config combination, not a code path, and
Phase 8 criterion 2 already requires backend switching to be a one-line change.

**5. The adversarial tier-gate test runs per registered backend.** Phase 8 criterion
1 requires the runtime to drop model output that reaches past the unlocked tier.
Smaller local models leak more than hosted ones, so a gate proven against a hosted
backend proves nothing about the local one. Make the adversarial fixture part of the
stub-backend test that Extensibility Rule 6 already demands.

### 8.3 What could not be verified

- Any real tokens-per-second benchmark on a 7900 XTX for any model in the shortlist.
  Every specific figure found was for a 7B model or for an RTX 4090.
- Whether the ROCm-versus-Vulkan regression on gfx1100 has been closed since March
  2026. "Still open" is an inference from recency.
- gpt-oss-20b's exact active parameter count (sources give 3.6B and 5.1B).
- Qwen3.6-27B (April 2026, hybrid attention, 27B) exists and is confirmed, but no
  GGUF quant file sizes or community VRAM reports were found, so its 24GB fit is an
  estimate only. Re-check it before Phase 8 plans, since it may be the better default.
- **Any trustworthy public benchmark for open-weight long-form prose quality.**
  EQ-Bench's creative writing leaderboard is dominated by closed frontier models and
  none of the candidates placed. This is the largest gap in the answer. The
  implication is concrete: **prose-quality model selection must be settled by running
  our own 18-rule style check plus a human read over generated lessons from the
  Phase 3.2 corpus**, not by citing a leaderboard. That is a Phase 11 evaluation
  fixture, and it is cheap because the linter is the eval harness.

---

## 9. Consolidated cost of this artifact's recommendations

| Item | Where | New deps | New lint codes | New events | New blocks | Rough size |
|---|---|---|---|---|---|---|
| Shared metrics builder + closed check catalogue + style resolver | 3.1 | 0 | 3 (registry policing) | 0 | 0 | ~250 lines |
| Declared section skeleton (markdownlint MD043 shape) | 3.1 | 0 | 2 | 0 | 0 | ~40 lines |
| FP calibration run over the 3.2 corpus | 3.1 | 0 | 0 | 0 | 0 | 1 task |
| Inline `style-ignore` + suppression report | 3.1 | 0 | 0 | 0 | 0 | ~60 lines |
| `style.unsourced_specific` anti-fabrication check | 3.1 | 0 | 1 | 0 | 0 | ~25 lines |
| Five usage criteria | 3.2, 6, 6.2, 10, 11 | 0 | 0 | 0 | 0 | report code only |
| `## SCENARIO` + `[STAGE:]` | 9 | 0 | 5 | 0 | 2 | ~150 lines + reader |
| `[GATE:]` strengths + `gate_skip` event | 6.2 | 0 | 1 | 1 | 1 attribute | ~80 lines |
| Outline-first authoring pipeline | 11, 3.2 | 0 | 0 | 0 | 0 | pipeline, batch UI |
| `itembank bench` + prompt cap + streaming hints | 8 | 0 | 0 | 0 | 0 | ~120 lines |

**Total: zero new dependencies, 12 new lint codes, 1 new event type, 2 new blocks and
1 new block attribute.** Nothing here requires a second parser, a second scorer, or a
second evidence store. Every format addition owes its byte-identical no-op fixture
per Extensibility Rule 3.

## 10. What this artifact does not answer

- **Whether the 18 warnings survive contact with real content.** §3.2's calibration
  run is the answer and it cannot be run before Phase 3.2 lands a corpus. Any style
  rule tuning done before then is guesswork.
- **The best local model for prose specifically.** No public benchmark exists. §8.3
  proposes measuring it ourselves with machinery we are building anyway.
- **Whether `on-item` is the right scenario advance granularity for Math and CS**, or
  whether scenarios are an EMT-only construct. The grammar is subject-invariant; the
  usefulness may not be. Phase 9's integration matrix will show it.
- **U6, lesson-to-item transfer**, which needs a lesson-view event that does not
  exist and would add a write to a read path. Deferred to Phase 10 with the cost
  recorded.
