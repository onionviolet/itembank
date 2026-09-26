# Question types and answer checking audit

Date: 2026-09-25, America/New_York.
Source baseline: `ee23d88`.
Status: research and verified gap inventory. Recommendations are not accepted
format changes or an implementation plan.

## Result

Itembank already has eight assessment response forms and a Python execution
checker. Its largest format gaps are graded text blanks, numeric and unit
answers, and bounded symbolic mathematics. A richer editor does not supply
those checking rules. The existing execution checker also needs correctness
and isolation work before expansion to less trusted programs.

The audit covers source, synthetic tests, and current primary documentation.
It does not establish installed-app behavior, human accessibility acceptance,
learning benefit, or complete competitive parity.

## Request, scope, and evidence

> audit types of quiestions from fill in the blank to other stuff and more? Like code interpretor based answer checking for cs and other stuff and more?

Interpretation: audit both the learner's response and the mechanism that can
check it across subjects. Preserve broader possibilities without treating every
widget or subject as a new parser type.

The [capture](../../USER-VISION-INBOX.md#2026-09-25-question-types-and-programmatic-answer-checking-audit)
routes this request. Existing direction includes
[code-question depth](../../USER-VISION.md#2026-09-16-beneficial-depth-levels-and-code-question-audit),
[learner LaTeX entry](../../USER-VISION.md#2026-09-20-latex-answer-input), and
the [Phase 16 response-family research](../phase-16/03-question-activity-matrix.md#5-response-form-design-space).
The current product contract and runtime authority take precedence over old
research descriptions of what had shipped.

| Evidence owner | Scope |
|---|---|
| [Current types](01-current-types.md) | Registry, parser, response semantics, scorer, selected renderers, cloze scope, and focused tests |
| [Execution and math](02-execution-math.md) | Native checker, prototype execution, runtime authority, isolation, math input, and synthetic bug probes |
| [Reference patterns](03-reference-patterns.md) | Current official documentation, reusable patterns, and explicit limits |

The three lanes own separate reports. The root agent owns this synthesis and
the request and disposition records. No production code, real banks, learner
evidence, settings, dependencies, or accepted schemas are changed. No commit
or push is part of this audit.

## F1: Existing types provide a useful structured foundation

The live registry contains `mc`, `multi`, `table`, `dnd`, `build`, `short`,
`check`, and `visual`. That is eight response contracts, not eight teaching
strategies. Prediction, debugging, a case study, a timed sitting, and a shared
passage can use these contracts without each becoming a new type.

| Learner task | Current fit | Audit conclusion |
|---|---|---|
| Single choice and multiple selection | `mc`, `multi` | Present. Author the construct and distractors, not just the control. |
| True or false | A two-option `mc` is rejected by the current minimum-option lint | A small explicit format-policy gap. Do not claim clean support through ordinary MC authoring. |
| Row classification and matching | `table`, `dnd` within their declared mappings | Present with bounded semantics. Free numeric or prose table cells need their own contracts. |
| Ordering and code-block rearrangement | `build` | Present for authored sequences. Arbitrary valid alternative orders need a declared rule. |
| Plots, number lines, regions, timelines, diagrams, traces | `visual` with family-specific semantics | Present families do not imply arbitrary drawing, circuit, graph, or chemistry validation. |
| Explanation, essay, proof, design rationale | `short` | Text submission exists. Settled scoring remains reviewed. |
| Program implementation or repair | `check` | Native Python execution checking exists. See F3. |

Per-component diagnostic feedback is not automatically fractional credit.
Any new weighting or partial-credit rule must extend the runtime contract and
evidence semantics explicitly. The current-type report records the actual
normalization and aggregation for each family.

## F2: Fill-in-the-blank spans several missing checker contracts

Cloze markers in lesson key points and Anki export support retrieval. They do
not provide a graded assessment blank. The existing Registered inline-select
proposal, [IL-20260828-04](../../IDEA-LEDGER.md#il-20260828-04-an-inline-select-cloze-as-a-teaching-checkpoint-form),
also remains distinct from free text entry.

| Completion family | Proposed response and checker | Important authoring decision |
|---|---|---|
| Single term or phrase | Original text plus explicit accepted forms and normalization | Case, whitespace, Unicode, accents, punctuation, and synonyms must be deliberate. |
| Several blanks in one passage | Stable blank IDs and a per-blank response contract | Define whether blanks are independent and how their results aggregate. |
| Dropdown or word-bank completion | Choice IDs placed into named blanks | Recognition and recall are different demands. Reuse mapping semantics when they fit. |
| Number, estimate, or measurement | Parsed numeric value with declared absolute or relative tolerance | Define boundary inclusion, fractions, scientific notation, locale, and non-finite input. |
| Number with units | Value and unit with explicit conversion and dimension rules | Distinguish the right quantity from the requested unit or significant figures. |

Do not make `short` silently switch between prose review and guessed string
matching. Keep the submitted text and the versioned normalization rule so a
learner can understand why an equivalent spelling was accepted or refused.

For a first vertical slice, one accepted-form text blank and one numeric blank
would expose more useful gaps than another decorative question layout. This
is a prioritization inference, not a measured learning result.

## F3: Interpreter checking exists, with material defects and limits

Native `check` items already support Python execution, stdout comparison, and
function harnesses. A checker can test return values and numeric tolerance.
The runtime retains verdict and evidence authority. The served submission path
runs the submitted source rather than accepting a client's claimed pass vector.

The [execution report](02-execution-math.md) owns exact source locations and
reproductions. Its verified findings must be read before designing an expanded
code workspace.

One reproduced correctness defect is that stdout matching ignores a nonzero
process exit. A synthetic program that prints the expected result and then
raises an exception can receive a correct verdict. Passing existing checker
tests does not cover that case.

The native runner explicitly is not a hostile-code sandbox. Its subprocess can
access the user's files and network. Time and output limits do not remove those
permissions. This is a current implementation boundary, not a claim that code
checking is absent. Browser JavaScript and Pyodide in CS Dojo remain a separate
prototype path and do not establish production scoring or isolation parity.

A second reproduced defect affects active exam sessions. The API removes the
top-level score but returns nested `interaction_result` and `run_result` data.
The synthetic response included the verdict, case input, expected output,
actual output, and pass flag while the exam was still active. Repair must cover
nested JSON disclosure as well as what the visible quiz happens to render.

There is also a smaller authoring defect. A bank mixing `visual` and `check`
items produces a warning that visual answers will remain pending, despite the
visual scorer accepting the same response. The current-type report reproduces
this discrepancy.

| CS task | Useful checking approach | Claim boundary |
|---|---|---|
| Write or repair a function | Visible examples plus runtime-owned test cases | Passing a finite suite supports the tested behavior, not arbitrary correctness. |
| Predict output or reconstruct state | Typed output or structured trace checked after commitment | Running or revealing the answer first changes the task. |
| Rearrange a program | Existing sequence response or a bounded structural checker | Several working orders may exist. One model order need not be uniquely correct. |
| Write tests for a function | Evaluate tests against authored correct and faulty implementations | Mutation coverage is a proposed capability, not current general support. |
| SQL or data analysis | A resettable fixture and a typed result comparator | Define row order, duplicates, NULL, numeric tolerance, and permitted side effects. |

Execution adapters should return observations to the runtime, including engine
version, source and test fingerprints, exit status, timeouts, capped output, and
test outcomes. The runtime decides the grade, disclosure, and durable evidence.
An unavailable engine or infrastructure error must remain distinguishable from
a valid incorrect answer. Existing timeout behavior remains pending unless a
later accepted scoring contract changes it.

Hidden test details need a separate disclosure policy from the learner's own
stdout. An assessment result must not reveal hidden input, expected output, or
pass counts just because a code pane can display them.

## F4: Math input and mathematical checking are different capabilities

LaTeX entry and preview exist on `short` items. Those answers remain pending
review. They do not establish numeric, algebraic, logical, or chemical
equivalence grading.

A useful progression is numeric value, units, bounded symbolic expressions,
then specialized structured objects. Each needs an explicit rule. For example,
`2*(x+1)` and `2*x+2` can represent the same polynomial, while an item asking for
factored form may deliberately distinguish them. Simplifying `(x*x-1)/(x-1)`
also requires preserving its original domain restriction at `x=1`.

Graph sketches, matrices, vectors, sets, intervals, and equations require
different response semantics. Truth tables or finite-state tasks can sometimes
use a deterministic structured checker. A written proof or explanation still
needs review of its reasoning even when its final expression is equivalent.

The reference report identifies current primary examples for tolerance, units,
symbolic equivalence, required form, and failure states. No CAS dependency or
new parser grammar is selected by this audit.

Moodle provides a useful reference for mixing text, choice, and numeric blanks
inside a passage. STACK demonstrates why algebraic equivalence and requested
form need distinct rules. These are design references, not dependencies chosen
for Itembank. [Moodle cloze](https://docs.moodle.org/502/en/Embedded_Answers_%28Cloze%29_question_type),
[STACK equivalence](https://docs.stack-assessment.org/en/Authoring/Answer_Tests/Equivalence/).

## F5: Preserve broader subjects through explicit capability boundaries

| Subject or response | Useful candidate | Proposed route and promotion trigger |
|---|---|---|
| Language | Dictation, spelling, inflection, short translation, pronunciation | Text rules may be deterministic when accepted variants are bounded. Open translation and speech remain reviewed. Prototype only after objective and input requirements are clear. |
| Science and chemistry | Measurements, balanced equations, labeled structures, model prediction | Prototype units and structured balance rules first. Backburner molecular equivalence until a named course needs it and a domain checker can be validated. |
| History, politics, and source analysis | Timeline order, evidence selection, source comparison, argument | Reuse structured selection where appropriate. Keep interpretations and argument quality reviewed. |
| Data, spreadsheets, and notebooks | Query results, formulas, transformations, plots, multi-cell work | Backburner adapters behind pinned fixtures, durable file state, execution isolation, and recoverable exports. Revisit for a concrete course task. |
| Audio, music, art, and physical performance | Recorded performance or a submitted artifact with a rubric | Backburner capture and reviewer workflows behind purpose, privacy, accessibility, and domain validation. A proxy choice question does not prove performance. |

These candidates remain available. No family is rejected just because it would
cost more to maintain. Automatic final grading of open prose is outside the
current contract. Advisory AI can explain a diagnostic or propose a rubric
assessment, while the permitted review process settles the mark.

## Recommended order

| Code | Proposed next work | Owner and acceptance gate |
|---|---|---|
| A1 | Repair reproduced checker and disclosure defects, plus misleading type diagnostics | Runner, runtime, session, and lint owners. Regression tests must demonstrate the original failure and the corrected behavior. |
| A2 | Prototype text blanks, multi-blank composition, numeric entry, and units in a narrow sequence | Parser, runtime, and quiz owners. Preserve raw responses, explicit rules, useful errors, exact resume, and matching keyboard behavior. |
| A3 | Make the existing code checker suitable for a complete production coding task | Execution and CS Dojo owners. Isolated files and network, versioned tests, cancellation, unavailable states, durable drafts, and controlled disclosure must pass. |
| A4 | Prototype a bounded math checker | Runtime and math owner. Define domain, equivalence, required form, parse errors, unsupported expressions, and timeout behavior before accepting marks. |
| A5 | Add subject adapters when an actual course needs them | Course and capability owners. SQL, notebooks, chemistry, speech, and artifact review retain the dependencies and triggers above. |

Use the least complex checker that measures the intended objective. An exact
accepted-term rule does not need a code interpreter. A programming task benefits
from executing tests. A proof still needs reasoning review. This selection rule
extends the earlier code-depth audit without turning every activity into an IDE.

## Verification and recovery

Six distinct focused suites passed: scoring, check execution, visual scoring,
visual authoring, LaTeX input, and study/export surfaces. The evidence reports
record commands and coverage. Independent synthetic probes reproduced the
active-exam leak, crash-as-correct result, and false visual pending warning.
Existing passing tests do not close these defects.

`python3 scripts/preflight.py --quick` passed all ten executed gates. It skipped
the full Python suite, clean-tree gate, and JavaScript suite. `git diff --check`
passed. Authored audit prose contains no em dashes. No installed-app, new visual
browser, or human accessibility acceptance is claimed. The loopback API probe
was synthetic and temporary.

The vision audit is advisory and exits zero even with findings. Its existing
missing-path, ambiguous-path, and legacy traceability backlog remains open.
This pass retains those limits rather than treating a zero exit as complete
vision traceability.

The request is routed without changing its wording. Existing proposals retain
their owners. New breadth is recorded in the
[disposition ledger](../../IDEA-LEDGER.md#il-20260925-02-question-types-and-answer-checking-breadth).
This is a bounded audit of relevant vision and code sections, not a whole-vision
audit. Large modules were inspected by symbol and targeted windows.

Recovery removes this research directory and only the uniquely titled inbox
and ledger additions from this pass. Preserve any later or concurrent edits.
