# Reference patterns for answer entry and checking

**Status:** research evidence and proposed patterns, 2026-09-25.
**Scope:** official documentation from Moodle, STACK, PrairieLearn, nbgrader,
and SQLite, accessed 2026-09-25. Documentation was inspected without installing
software, running fetched code, or testing these products. This report does not
claim that any cited capability is implemented in Itembank.

## Prior research and the new contribution

The response-family table in
`../phase-16/03-question-activity-matrix.md`, section 5, already distinguishes
response form from scoring authority. It registers numeric, symbolic, short
text, code, audio, and performance responses. Its open questions include safe
short-text normalization and bounded symbolic equivalence.

`../code-question-depth-audit-2026-09-16.md` already separates code reading,
tracing, manipulation, and construction. `../overhaul-2026-09-18/QUESTION-PATTERNS.md`
already covers response behavior and several mature product references.

This report adds current checker contracts and failure cases. It does not
repeat the full activity taxonomy or replace prior dispositions.

## F1. A blank is an entry control, not a grading algorithm

Moodle cloze embeds several independently weighted responses in one passage.
Each can be short text, numeric, or a choice control. Its short-text variants
explicitly distinguish case-sensitive and case-insensitive answers. Numeric
blanks accept an authored tolerance. This supports a composite question with
typed subresponses rather than a separate monolithic checker for every visual
layout. [Moodle cloze documentation](https://docs.moodle.org/502/en/Embedded_Answers_%28Cloze%29_question_type)

| Response pattern | Verified reference behavior | Proposed Itembank contract |
|---|---|---|
| One term or phrase | Moodle compares declared acceptable answers and optionally respects case. Wildcards can accept unintended phrases, including negated answers. | Declare accepted alternatives and a named normalization policy. Require false-positive examples before accepting wildcard or pattern rules. |
| Text normalization | PrairieLearn exposes separate case, whitespace, and ASCII-normalization controls. Its regular-expression mode matches the entire submission. | Keep the original response. Record the normalized comparison value and rule version separately. Do not strip accents, punctuation, or case globally because those may be the assessed skill. |
| Several blanks | Moodle cloze supports distinct child types and weights. | Give every blank a stable ID, input label, checker, and weight. Declare whether scoring is per blank, all-or-nothing, or dependent on other blanks. |
| Open explanation | A textbox can hold a short exact answer or unrestricted prose. Its appearance does not establish a valid equivalence rule. | Use exact checking only for an explicitly bounded answer set. Leave reasoning, translation quality, and open explanations pending review unless a separate approved rubric applies. |

Sources: [Moodle short answer](https://docs.moodle.org/502/en/Short-Answer_question_type),
[PrairieLearn string input](https://docs.prairielearn.com/elements/pl-string-input/).
The proposed contract is synthesis, not a claim about either product.

Acceptance examples should include extra surrounding text, empty input,
Unicode variants, preserved diacritics, punctuation, deliberate negation,
case-sensitive identifiers, and an unlisted but defensible answer routed for
review. Multi-blank checks must prevent one blank's feedback from disclosing
another still-active answer.

## F2. Numeric checking needs separate magnitude, unit, and precision rules

Moodle numerical questions support accepted error ranges and alternate units
with conversion multipliers. Calculated questions add generated variable
values and distinguish nominal, relative, and geometric tolerance. These are
reference patterns, not justification for copying defaults or assuming random
variants are equally difficult.
[Moodle numerical](https://docs.moodle.org/502/en/Numerical_question_type),
[Moodle calculated](https://docs.moodle.org/502/en/Calculated_question_type).

PrairieLearn number input distinguishes relative-plus-absolute tolerance,
significant digits, and decimal digits. Fractions and complex numbers have
separate parsing options. Its units input distinguishes convertible units,
exact requested units, and units-only checking. It can allocate partial credit
between magnitude and units when the author enables that policy.
[PrairieLearn number input](https://docs.prairielearn.com/elements/pl-number-input/),
[PrairieLearn units input](https://docs.prairielearn.com/elements/pl-units-input/).

STACK explicitly separates written significant figures, numerical accuracy,
and conversion versus strict unit matching. Its documented unit syntax accepts
abbreviations rather than localized full names.
[STACK scientific units](https://docs.stack-assessment.org/en/Topics/Units/).

**Proposed pattern:** one quantity response contains raw input, parsed value,
unit, and written precision. The item declares allowed notation, quantity
dimension, required or convertible unit, absolute and relative tolerance,
rounding or significant-figure rule, and the partial-credit policy. A displayed
unit suffix alone does not prove units were checked. A blank is not silently
zero. Parse errors, a wrong dimension, a wrong magnitude, and an unavailable
checker need distinct results.

Useful applications include physics, chemistry, engineering, economics,
statistics, and clinical calculations. The latter still require authoritative
course rules for units and rounding. This report does not establish those
subject-specific rules.

## F3. Symbolic equivalence and the requested mathematical form are separate

STACK documents several meanings of equality. Algebraic equivalence, equality
of parse trees, equality up to allowed operations, and matching a required form
are different tests. Its algebraic checker treats expressions, equations,
sets, and other objects differently. It documents unrecognized equivalent
expressions, root-multiplicity behavior, assumptions that do not filter roots,
and operations that may time out. Floating-point comparison should use a
numeric test instead.
[STACK equivalence tests](https://docs.stack-assessment.org/en/Authoring/Answer_Tests/Equivalence/).

STACK's polynomial factoring test checks both equivalence and factored form
over a declared field. Other form tests address expanded, partial-fraction, or
lowest-terms representations.
[STACK algebraic form](https://docs.stack-assessment.org/en/Authoring/Answer_Tests/Form/).

**Proposed pattern:** begin with a bounded symbolic capability whose contract
names variables, allowed grammar, domain, assumptions, object type, desired
form, and checker version. An instruction to factor requires more than
equivalence to the original expression. An equation-answer task must say
whether it checks an equation, a solution set, or a derivation. Undefined
points and introduced or lost roots need explicit treatment. A checker timeout
or inability to establish equivalence must remain unresolved rather than
automatically becoming an incorrect learner answer.

Do not claim a general proof checker from these references. A proof with
arbitrary prose still needs an approved rubric and review. Exact finite logic
or structured derivation tasks can be separate bounded capabilities.

## F4. A code interpreter is an execution service within an assessment contract

PrairieLearn external grading defines a container image, submitted files,
question tests, optional shared resources, a timeout, and structured results.
The same execution path can receive an editor submission, uploaded files, or
ordered code blocks. It distinguishes a gradable result from an invalid,
ungradable submission. This demonstrates that input form and execution can be
independent.
[PrairieLearn external grading](https://docs.prairielearn.com/externalGrading/).

Its Python grader separately names variables provided to learner code and
variables read by tests. Course libraries and setup code are explicit inputs.
Published grader images cover Python, C/C++, Java, and R. These references do
not establish that arbitrary learner execution is safe in Itembank.
[PrairieLearn Python grader](https://docs.prairielearn.com/python-grader/),
[PrairieLearn Docker images](https://docs.prairielearn.com/dockerImages/).

| Task family | Proposed checker evidence | Limit of the claim |
|---|---|---|
| Output prediction and tracing | Expected output or state against a fixed program and environment | Running the program before a committed prediction may remove the intended reasoning task. |
| Fill missing code, repair a bug, or implement a function | Public examples plus private edge-case and property tests under the declared runtime | Passing finite tests is evidence against those tests. It does not establish correctness for every input. |
| Arrange code blocks | Structural ordering constraints or execution of the assembled program | Multiple valid orders and independent statements need explicit equivalence rules. |
| Data analysis or notebook | Results from a clean execution, structured values, and declared test cells | Plots, interpretation, and the suitability of a method may need review beyond numeric output. |
| Code quality or algorithm choice | Declared static checks, focused behavioral probes, and a separate rubric | A lint pass does not establish readable design, sound explanation, or the intended algorithm. |

nbgrader separates test cells from manually graded answers and tasks. Hidden
test sections are removed from the learner release and restored for grading.
Notebook-wide tasks can remain manually graded. Its guidance explicitly uses
combined automatic and manual grading when passing tests cannot establish the
required implementation approach. The command documentation warns that grading
without re-execution cannot guarantee saved output is correct.
[nbgrader assignment workflow](https://nbgrader.readthedocs.io/en/latest/user_guide/creating_and_grading_assignments.html),
[nbgrader testing guidance](https://nbgrader.readthedocs.io/en/latest/user_guide/autograding_resources.html),
[nbgrader autograde](https://nbgrader.readthedocs.io/en/latest/command_line_tools/nbgrader-autograde.html).

**Proposed Itembank boundary:** the runtime owns the score and disclosure.
A registered local runner returns versioned execution evidence for runtime
interpretation. It needs fixed environment and test fingerprints, reproducible
seeds where used, declared capabilities, bounded resources, cancellation,
clean temporary state, and explicit unavailable/error outcomes. Hidden tests
must stay outside learner-writable authority. Sensitive test output is released
only under the active feedback policy. A familiar interpreter UI is not proof
of any of these guarantees.

## F5. SQL and AI checking need distinct extension contracts

### SQL as a proposed local deterministic checker

No native PrairieLearn SQL checker was verified in this bounded search. SQLite
is the primary reference for this proposed extension. Its SELECT documentation
states that row order is undefined without ORDER BY and that duplicate removal
and NULL comparison follow specific rules. It also documents SQLite-specific
behavior that differs from other SQL engines.
[SQLite SELECT semantics](https://www.sqlite.org/lang_select.html).

**Proposed pattern:** run a submitted query against an isolated synthetic
fixture database. Compare result schema and rows with explicit ordered or
unordered semantics. Preserve multiplicity when duplicates matter. Declare
NULL, numeric tolerance, column-name, and collation rules. Use several fixture
datasets to expose hardcoded results and accidental joins. Separate read-only
query tasks from mutation tasks that compare final database state. Pin the SQL
dialect and version. This is a checker design proposal, not a shipped Itembank
capability or a claim that result equality proves universal query equivalence.

SQLite recommends defensive configuration, reduced input limits, an authorizer
to restrict statements, progress handling or interruption for long-running
queries, and memory limits for untrusted SQL.
[SQLite untrusted-input guidance](https://www.sqlite.org/security.html).
These inform implementation acceptance gates. They do not replace process
isolation or prove that an existing runner enforces them.

### Advisory AI as a separate path

PrairieLearn distinguishes AI rubric grading from executable test grading. Its
AI path sends source text without executing it and recommends instructor review
before relying on the result. It exposes rubric decisions and explanations for
comparison with human grading.
[PrairieLearn AI grading](https://docs.prairielearn.com/aiGrading/).

**Itembank application:** AI may explain a released test failure, propose a
rubric assessment, or identify a likely defect. Those are advisory outputs.
They must not masquerade as executed tests, successful proofs, or settled prose
marks. Record the rubric, model, relevant inputs, uncertainty, and review state.
Do not copy another product's grade-settlement behavior into Itembank's runtime
authority model. A hosted AI route additionally needs declared egress and rights.

## Suggested research-to-implementation order

1. **A1:** Specify typed text and multi-blank checking with conservative,
   explicit normalization and representative false-positive tests.
2. **A2:** Specify quantity checking with tolerance, units, notation, and
   precision handled independently.
3. **A3:** Audit the existing executable-check contract against code-completion,
   function, tracing, and ordered-block tasks before adding a new runner.
4. **A4:** Prototype one bounded symbolic domain and one isolated SQL task only
   after each has a declared equivalence and failure policy.
5. **A5:** Keep notebook artifacts, code-quality rubrics, and advisory AI as
   separate capability proposals with explicit review and recovery gates.

This ordering is synthesis from the references and prior repository research.
It is not an accepted roadmap or an implementation estimate.
