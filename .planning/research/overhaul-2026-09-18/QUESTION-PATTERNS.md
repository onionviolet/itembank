# Question interaction patterns and testing UI

Research and access date: 2026-09-18. Status: proposed experiments, not a
production gap inventory. This lane owns competitor patterns. Root and the
sibling audit own current Itembank code mapping and installed UI observations.
No production code, real bank, score, installation or commit changed here.

## Findings

**F1. Better multiple choice requires better reasoning and feedback, not just
more attractive options.** A useful option encodes a plausible misconception.
The learner should understand the response rule, commit deliberately, retain
their original response and see only feedback the active mode permits. A richer
display earns its cost when it makes evidence or reasoning easier to inspect.

**F2. Response shape and assessment behavior are separate decisions.** Radio
buttons versus checkboxes do not decide retry allowance, partial credit,
confidence weighting or when explanations become available. Those belong to
the authored assessment policy and Itembank runtime. A UI redesign must not
change them accidentally.

**F3. Several supposedly new ideas are already in the research backlog.** The
[September 5 absorption](../2026-09-05-open-source-absorption.md) covered
confidence diagnostics, reusable stimulus and variants. The current
[LMS report](LMS-FLOWS.md) retains those ideas. The
[interactive report](INTERACTIVE-TEACHING.md) already covers code prediction,
Parsons, linked representations and transfer. This pass adds more precise
question-level experiments and semantics. It does not claim exhaustive novelty
against every historical note or current implementation.

## Primary-source evidence register

Every source below was fetched or returned as primary search evidence on
2026-09-18. None was operated in a live competitor sitting during this lane.
Documentation proves documented behavior, not accessibility acceptance,
integration success or learning efficacy.

| ID | Primary source and evidence class | Concrete documented behavior |
|---|---|---|
| S1 | [Moodle question behaviors](https://docs.moodle.org/502/en/Question_behaviours), official docs, page edited July 16, 2025 | Distinguishes deferred, immediate, adaptive and interactive retries. Describes certainty-based scoring. Additional explanation plugins collect reasons without automatically grading the prose. |
| S2 | [Moodle multiple choice](https://docs.moodle.org/502/en/Multiple_Choice_question_type), official docs, page edited May 22, 2024 | Single and multiple answer controls, option-specific feedback, weighted responses and configurable review disclosure. These docs distinguish Quiz from the differently behaving Lesson module. |
| S3 | [Moodle using Quiz](https://docs.moodle.org/502/en/Using_Quiz), official docs | Flagging, navigation, unanswered summary, final submission and conditional review. This is a mature reference for the full sitting, not just the answer card. |
| S4 | [PrairieLearn multiple choice](https://docs.prairielearn.com/elements/pl-multiple-choice/), official docs | Option feedback, display configuration and answer scoring are independently configured. Its no-built-in-grading mode further illustrates that a selection widget need not itself produce a score. |
| S5 | [PrairieLearn checkbox](https://docs.prairielearn.com/elements/pl-checkbox/), official docs | Several partial-credit methods, explicit selected-option feedback, selection bounds and a configurable correct-option count. The visible count is a pedagogical choice, not harmless chrome. |
| S6 | [PrairieLearn concepts](https://docs.prairielearn.com/concepts/) and [question server](https://docs.prairielearn.com/question/server/), official docs/search evidence | Parameterized instances are variants. Homework supports repeated attempts with changed variants. Generation creates parameters and corresponding answers. This is not evidence that unreviewed randomization preserves difficulty. |
| S7 | [H5P Multiple Choice](https://h5p.org/multichoice), official product documentation | Describes immediate feedback and single or multiple correct options. Its default product behavior cannot override Itembank exam policy. |
| S8 | [H5P Image Choice release](https://h5p.org/node/1352868) and [May 2023 release](https://h5p.org/may-2023-release-note), official release evidence | Image alternatives and use within several composite content types. This establishes a visual-choice pattern, not a requirement to embed H5P. |
| S9 | [Runestone multiple choice](https://runestone.academy/ns/books/published/authorguide/directives/choice.html), official author docs | Radio/checkbox forms, option-specific feedback and a list format allowing rich option content. Authors still need to make options pedagogically meaningful. |
| S10 | [Runestone peer instruction](https://guide.runestone.academy/peer_instruction-3.html) and [assignment setup](https://guide.runestone.academy/peer_instruction-4.html), official instructor docs | Vote, discussion and a second vote are separate steps. Participation grading can depend on both votes and discussion. This is not equivalent to correctness or an AI simulating a peer. |
| S11 | [W3C dragging movements guidance](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html), normative-standard companion guidance | A dragging task needs a single-pointer alternative that does not require dragging. Keyboard accessibility is a separate obligation. |

H5P's [content-type accessibility matrix](https://help.h5p.com/hc/en-us/articles/7505649072797-Content-types-recommendations)
was refreshed in the earlier lane. It distinguishes versions and content types.
Do not generalize one accessible specimen to the ecosystem. Brilliant's current
public marketing was also refreshed in that lane. It does not document enough
private assessment mechanics to attribute the patterns below to Brilliant.

## Five prioritized experiments

Priority is proposed and conditional on the sibling's current implementation
audit. If a capability already exists, test and improve its real journey rather
than adding a parallel version. Each experiment begins with synthetic content.

| ID / priority | Experiment and learner task | Practice versus exam and authority | Observable gate and stop condition |
|---|---|---|---|
| E1 / first | Clear MC/multi decision surface with option-specific misconception feedback. Compare a radio question and a checkbox question on the same objective. Use explicit selection instructions, persistent selected state, a separate submit action and authorized explanation adjacent to the relevant option. | Both modes need unambiguous response rules. Practice can disclose reviewed feedback after submission. Exam preserves its release rules. Runtime supplies correctness, partial-credit policy and disclosure. Do not reveal how many answers are correct unless the item intentionally does so. | Learner predicts whether one or several responses are allowed, edits before submitting and explains their selected distractor after feedback. Reflow, keyboard and screen-reader checks preserve option order and labels. Fail on selection-as-submit, accidental double submission, guessed status or hidden changed scoring. |
| E2 / second | Review flag plus reversible elimination notes. Learner crosses out a doubtful option, restores it, flags the item, leaves and returns through a review summary. Show answered, unanswered and flagged as independent states. | Useful in practice and exams that permit review. Elimination is a learner annotation, not a response or correctness claim. Flags never select remedial items without the learner's action or an existing policy. Persistence needs an explicit owner and session/item revision binding. | Return preserves the actual response and separate annotation. Selecting a crossed-out option prompts a clear reversible state change rather than silently preventing selection. The summary never says “wrong” before disclosure. Fail on loss after restart or a flag being mistaken for submitted/complete. |
| E3 / third | Answer plus reason, with optional confidence. Commit a prediction and one-sentence justification before feedback. A separate variant uses reviewed reason choices to contrast a correct answer reached by a faulty rule with a justified answer. | Start in diagnostic practice. Prose remains pending or advisory. Structured reason choices can be scored only through an explicit runtime-owned composite rule. Confidence is descriptive first. Do not import Moodle's certainty-weighted marks by implication. | Preserve initial answer and reason before any reveal. Use a fresh transfer question to test whether the apparent misconception recurs. Fail if reason options reveal the first-stage answer early, free prose gets a settled automatic mark or confidence changes points without an announced contract. |
| E4 / fourth | Visual contrast under a shared stimulus. Keep a graph, short passage or small case visible while the learner chooses between plausible interpretations. Use matched image/graph options with equal scale, labels and enlargement behavior. Ask which single changed assumption would make a distractor valid. | Appropriate in practice and an exam only when its blueprint calls for the construct. Shared stimulus revision and child-item relationships must be explicit. Feedback on one child may reveal another, so runtime release must consider the group. | Complete two questions without losing the source or hiding essential values on a narrow screen. A text/table equivalent preserves the reasoning where feasible. Fail on visual styling cues, differing scales that accidentally signal the key or cross-question feedback leakage. |
| E5 / fifth | Retry followed by a changed transfer variant. After an incorrect commitment, show a permitted targeted hint and allow a bounded retry. Then present a reviewed variant that changes values or context while preserving the objective. | Practice experiment, not a default exam behavior. Record first response, help used and subsequent response separately. Runtime owns retry limits, any penalty and variant identity. If answers become correct by elimination, that result is assisted success, not independent mastery. | The learner solves a new example without the previous answer visible. Replay yields the same accepted variant and never mutates an in-progress sitting. Fail on infinite guessing, shifted difficulty, duplicate evidence or final correctness erasing first-attempt evidence. |

E1 is partly presentation and partly feedback routing. E2 requires an explicit
annotation persistence decision. E3 and E5 may require assessment contract
changes. They are experiments, not authorization to implement all five.

## Broader candidates retained

The following is a disposition catalogue, not an additional action list.

| Candidate | Teaching purpose and scope | Disposition, trigger and cost |
|---|---|---|
| Answer-until-correct / scratch-off metaphor | Makes successive hypotheses explicit after partial feedback. Useful for practice where retry itself teaches. An exam use requires a declared scoring model. | Prototype within E5. Preserve attempt history and assistance. Avoid a decorative scratch gesture or celebratory completion that hides guessing. |
| True/false decision for every statement | Separates an omitted correct choice from an explicit rejection. Better than checkbox ambiguity for some diagnostic constructs. | Registered. Trigger is an objective requiring judgment of every claim. It changes response demand and scoring, so it needs a new reviewed contract rather than relabeling `multi`. |
| Explicit “insufficient information” | Tests when evidence cannot settle a claim. | Registered authoring pattern. The option must be defensible under the stated assumptions. It is not a universal escape option. |
| Two-stage reason selection | Distinguishes lucky answer from an appropriate rule. | Prototype E3. Show the second stage after the first commitment and audit cueing. Combined score and independent subscore semantics need explicit decisions. |
| Counterexample construction | Learner repairs a claim or gives a case where the tempting option becomes true. | Registered treatment. Start with pending short response or existing structured forms. Symbolic/general proof checking is a separate capability, not an MC UI feature. |
| Compare two solutions / locate first divergence | Focuses on a step where reasoning changes rather than choosing the final result. | Registered. Trigger is a concrete misconception that final-answer feedback obscures. Preserve code/math fidelity and equivalent linear reading. |
| Confidence calibration review | Shows confident errors and unsure successes with denominators. | Existing registered idea, retained. Requires actual confidence input and enough evidence. No automatic confidence-weighted grade or psychological inference. |
| Peer discussion and revote | Distinguishes independent commitment from reconsideration after another argument. | Backburner for a genuine multi-learner context. Runestone is a reference, not justification for simulated peer chat. Coordination, privacy and participation evidence add cost. |
| Image hotspot / diagram labeling | Tests identifying a meaningful structure or relation. | Registered when location is the construct. Provide named regions or coordinate inputs as appropriate. A text equivalent must not simply name the answer. |
| Ordering / matching / Parsons | Tests dependencies, categories or process order. | Existing registered families. Provide select-item/select-destination or Move up/down controls for pointer and keyboard users. Accept multiple valid orders when the reviewed semantics permit. |
| Partial-credit multi-select policy | Distinguishes omissions from false positives. | Deferred to a named assessment need and runtime contract. No generic “fairer” scoring claim. Show the rule before the sitting and test select-all and select-none behavior. |
| Optional reveal of correct-choice count | Reduces uncertainty in practice or matches a target exam format. | Registered only as intentional item policy. Counting correct options changes the task, so it is not a display preference. |

## What this pass adds to earlier evidence

| Topic | Earlier record | New contribution in this pass |
|---|---|---|
| Confidence | September 5 already proposed diagnostics without changing marks. | Distinguishes optional confidence from two-stage reasoning and explicitly tests that UI never imports CBM scoring. |
| Variants and shared stimulus | September 5 and current LMS report retain both. | Adds cross-child feedback leakage, variant replay, and first-attempt versus assisted success gates. |
| MC feedback | Existing project authoring contract requires distractor analysis. | Proposes testing its learner-facing placement and tier-correct release rather than treating author prose as automatically displayed feedback. Current visibility is for sibling audit. |
| Flags and eliminations | Flagging is mature Moodle documentation. Elimination is a proposed learner-owned annotation here, not an attributed Moodle capability. | Names orthogonal state and recovery semantics. This is new detail relative to the sampled overhaul reports, not a claim of novel invention. |
| Two-tier answer/reason | Moodle documents optional explanation plugins. Runestone documents revoting. | A structured two-tier diagnostic is this report's synthesis. Neither source proves a native equivalent with the exact proposed score semantics. |
| Contrast/counterexamples | Interactive lane already requires transfer and counterexamples. | Turns them into concrete option authoring and question-display tasks. |

## Testing UI acceptance floor

Keep stem, stimulus, selected response, feedback and next action distinguishable
without relying on color. State whether an answer is a draft, submitted,
pending review or withheld. State the active practice/exam rules before the
first response. Preserve feedback until explicit Next. Do not jump the page
when feedback expands or mark unseen options correct before release.

Use native radio and checkbox semantics with meaningful group labels where
possible. Long options, code, formulas and images need coherent reading order
and touch targets. Option IDs remain stable even when displayed letters shuffle.
Elimination controls must not sit inside a nested clickable option in a way that
accidentally submits or selects it. An enlarged image returns focus to its
origin and exposes the same information to alternative representations.

Keyboard support does not by itself satisfy drag accessibility. A tap/click
alternative must also exist. For matched or ordered tasks, an explicit item
and destination selector often covers both needs. See S11.

Distinguish local annotation saving from runtime response saving. Test Back,
reload, duplicate submit, interrupted save, restart, stale item revision and
completion with unanswered or pending items. Show known save state rather than
optimistic success. A summary page can support final review only where the
existing assessment mode permits changes. It must not create retroactive edits
to already-settled attempts.

For learning-quality experiments, compare the same objective and source scope
against the simpler interface. Record unassisted transfer, misconceptions,
interaction mistakes, time and navigation separately. A small usability sample
can find problems. It cannot establish broad learning efficacy. Automated
checks, rendered UI observations and human accessibility review remain separate
evidence classes.

## Limits and handoff

Official documentation and prior reports were inspected. No competitor task
was completed live, no existing Itembank display was independently verified,
and no new bank was authored. Direct H5P image-choice and PrairieLearn generic
question URLs failed, so this report uses the official release and specific
documentation routes that resolved. Root reconciles these patterns with the
current implementation before selecting one ready packet. Remove this new file
to undo the research addition.
