# Bounded polynomial checker readiness, 2026-09-30

Status: executable synthetic contract prototype. Production readiness and
acceptance remain the coordinating agent's decision. This report does not close
F2, F8 or F9 or grant an accepted bank/checker revision.

## R1. Scope and measured result

The successor packet left grammar, limits, required form and refusal semantics
open. Existing `prototypes/audit-question-families/polynomial.py` used Python AST
syntax and hard-coded misconception outcomes. New `polynomial_v2.py` implements
a dedicated bounded expression grammar and configurable private teacher/rules.
It does not import or execute authored code, sample numeric values, create a
session, settle a learner grade, write evidence or change production behavior.
Exact coefficient comparison delegates to existing numeric fill fields through
`runtime.score_response`. Every result has `settled_score: null` and synthetic
advisory authority, including correct and wrong-form outcomes.

The private authored table in
`tests/polynomial_checker_contract_roundtrip.py::AUTHORED_CASES` pins the version
per row. Six tests passed over 48 authored inputs. They include equivalent
reordering, decimal/rational coefficients, equivalent wrong form, both named
misconceptions, malformed input, unsupported functions/division/Unicode,
exponent/degree/coefficient/nesting/token/AST/work limits, original preservation,
teacher failure, diagnostic overlap, error injection and deferred disclosure.

Execution sampled the existing prototype in full and symbol windows around
`runtime.public_item`, `normalize_answer`, `canonical_response`, `score_response`,
`fill_response_error`, `assessment_feedback_released`, `_idempotent_canon` and
the submit transition, plus fill schema and model parse/spec/lint references.
It did not read those large production modules in full or claim exhaustive
assessment coverage.

## R2. Exact grammar and limits proposal

Version: `a5-rational-polynomial-v2`, domain `rational-polynomial`, variable `x`.
The only supported required form is `expanded`.

```text
expression := term (("+" | "-") term)*
term       := unary ("*" unary)*
unary      := ("+" | "-") unary | power
power      := primary ["^" exponent]
primary    := number | "x" | "(" expression ")"
number     := integer | integer "." integer | "." integer
            | integer "/" integer
integer    := ASCII digit+
exponent   := exactly one ASCII digit from 0 through 4
```

Space and tab may separate tokens, including rational numerator/slash/denominator.
Integer rational numerator and denominator are unsigned literals; unary signs
apply outside them. Decimals and rationals become `Fraction` from their source
digits. No binary float is used. Unary minus binds outside a power, so `-x^2`
means `-(x^2)`. Parentheses preserve grouping but create no separate AST node.
`2.` is invalid; `.5` is valid. Chained powers, leading-zero exponents,
scientific notation, `**`, implicit multiplication, functions, other variables,
Unicode algebra and division of expressions are outside this grammar. `2x` is
invalid missing explicit multiplication; `1/x` is recognizable unsupported
division. Negative/fractional exponents are unsupported. `1/0` is invalid.

| Resource | Fixed bound |
| --- | --- |
| Original input | 160 characters, one line |
| Tokens / constructed AST nodes | 96 / 64 |
| Nested parenthesis or unary-sign parsing | 16 |
| Digits in each numeric literal / rational denominator | 12 / 12 |
| Degree of every intermediate polynomial | 4 |
| Absolute numerator / denominator of every intermediate coefficient | 1,000,000 / 1,000,000 |
| Coefficient arithmetic work | 64 steps |

One coefficient addition/subtraction counts one step; each multiply-accumulate
counts one step. Unary sign changes are bounded by AST/coefficient limits;
they do not consume an arithmetic step. Power expands through repeated bounded
products, including the initial multiplication by one. Bounds apply before
cancellation can conceal oversized intermediates: `1000000+1-1` is refused.
Limits are fixed by the version, not mutable author or learner options.

Expanded form is an AST rule, independent of coefficient equivalence. Top-level
sums/differences recursively contain monomial terms. A term is a number, `x`,
`x^n`, unary signs on a term, or a scalar product with at most one variable
factor. A sum underneath multiplication, power or unary sign needs distribution
and fails form. `x*x` needs power reduction and fails form. Parenthesized terms,
`2*3*x` and additive like terms `x+x+2` pass. This contract requires distribution,
not combination of like terms or coefficient simplification.

## R3. Specification, outcomes and diagnostic precedence proposal

Private specification is exactly:

```json
{"domain":"rational-polynomial","checker_version":"a5-rational-polynomial-v2",
 "variable":"x","required_form":"expanded","target":"2*x+2",
 "diagnostics":[{"id":"distribution-omission","answer":"2*x+1"},
                {"id":"sign-error","answer":"2*x-2"}]}
```

Public projection includes only domain, checker version, variable, required
form, response grammar and fixed limits. It excludes teacher answers,
coefficients, private test rows, diagnostic answers and diagnostic IDs.
No executable checker string, callable or configurable Python expression exists.

Author validation requires a valid expanded teacher answer and at most two
diagnostic answers with unique bounded ASCII IDs. Canonically equal diagnostic
answers, duplicate IDs and overlap with the teacher answer are unavailable,
not an order-dependent priority choice. For a valid configuration the evaluation
order is fixed: author configuration, learner syntax/resources, exact equivalence,
equivalent required form, then diagnostic match for mathematically wrong only.
Different orderings of the authored rules give the same output. Algebraically
wrong and non-expanded input may still match a diagnostic; diagnostic rules
operate on the canonical polynomial, not string spelling or a guessed process.

Lexical scanning runs before grammar parsing. Unsupported lexical constructs
take precedence over a later missing parenthesis. Lexical/resource checks run
before bounded grammar, then canonical expansion. Configuration errors take
precedence over all learner entry issues. Unknown modes fail closed as
unavailable. Exceptions from checker internals or runtime comparisons yield
error, not an incorrect answer.

| Private state | Proposed production effect |
| --- | --- |
| correct | Valid settled `True`, exclusively from `score_response` |
| mathematically_wrong | Valid settled `False` |
| wrong_form | Valid settled `False`, equivalent but fails declared form |
| invalid | Refuse entry, preserve original draft, no attempt/evidence advancement |
| unsupported | Refuse entry, show domain/limit correction, no attempt/evidence advancement |
| unavailable | Refuse entry, author review needed, preserve draft and session |
| error | Refuse entry, retry path, preserve draft and session |

Unresolved states do not reuse pending prose marking or emit incorrect/mastery
evidence. A checker failure on a direct scorer path must propagate a typed
failure; returning `None` would manufacture pending prose evidence and returning
`False` would manufacture a wrong grade. Capture raw field strings before any
normalization and keep them in the existing recoverable draft route.

The prototype uses `assessment_feedback_released` to withhold all settled
outcome/comparison/diagnostic fields in active exam or diagnostic sittings.
Only matching-mode completed sessions release them. This tests policy behavior
with synthetic dictionaries; it does not prove real session authenticity.
Production diagnostic explanation text must additionally use existing hint-tier
release machinery. Practice mode alone is not permission to expose all keyed
teaching text. Invalid/unsupported corrections remain key-free.

## R4. Minimal additive production patch plan

1. P1, `model.py`, `runtime.py`, `schemas/item.schema.json` and lint schema:
   retain `[FIELDS: ...]` JSON parsing and add `kind: polynomial` with private
   `checker` above and adjacent private `checker_tests` rows. Reuse one parser;
   expose the existing labelled string response envelope. Require pinned
   authored tests for the teacher, every diagnostic, wrong form and refusals.
   Lint rejects missing/mismatched versions, unknown properties, overlaps and
   any authored expectation that the bounded checker does not reproduce.
   Keep old numeric/text field meanings unchanged and update format help.
2. P2, runtime fill/transition paths: place bounded helpers inside runtime's
   existing scoring authority, remove prototype runtime coefficient delegation
   there, and dispatch polynomial fields additively in `score_response`.
   Preflight invalid/unsupported/unavailable/error through `fill_response_error`
   and typed scorer failure before mutation. Update `canonical_response` with
   version, exact vector and required-form bit so equivalent wrong-form and
   corrected expanded responses are not falsely deduped. Preserve raw originals.
3. P3, `evidence.py`, response/session schema and release projections: settled
   events pin checker version and field outcome, and optional private diagnostic
   ID. Extend the existing event schema additively; do not alter historical
   evidence. Withhold diagnostic/outcome fields in public JSON, reports, Home
   and Activity under the same owning-session release rule. Refused submissions
   retain drafts without appending an attempt; errors cannot increment counters.
4. P4, `surfaces/agent_operation.py` and fill UI: authored tests remain private
   canonical bank data, so checker/test edits use existing expected fingerprints,
   `journal.commit_operation`, revision acceptance and undo. Preview plain source
   and native labelled text input with static grammar/form examples. Never send
   hidden tests or keys to a served learner client. Validate authoring, lint,
   preview, sitting, feedback, report, reload, rejection and undo end to end.
5. P5, focused regression and fresh package journey: run fill, fill surface,
   disclosure, JSON session and acceptance/undo suites plus new checker journey
   tests. Prove no resolved score on refusals and no disclosure before permitted
   tier/session closure. Build the coordinated candidate once, fingerprint it,
   exercise the same journey in fresh package bytes, and preserve explicit human
   keyboard/touch/screen-reader/installed-app acceptance gates.

P1-P4 are implementation gates, not reasons to produce another successor packet.
The existing broad instruction permits implementation; this task's narrower
ownership forbids production edits and leaves the parent to assign those paths.
Do not claim accepted production behavior from the synthetic contract tests.

## R5. Evidence, limitations and recovery

Commands run from the repository root:

```text
python3 tests/polynomial_checker_contract_roundtrip.py
python3 prototypes/audit-question-families/polynomial_v2.py '2*(x+1)'
python3 prototypes/audit-question-families/polynomial_v2.py '2*x+1' --mode exam
shasum -a 256 prototypes/audit-question-families/polynomial.py prototypes/audit-question-families/polynomial_v2.py tests/polynomial_checker_contract_roundtrip.py .planning/research/question-types-2026-09-25/NEXT-CHECKER-PACKET-2026-09-29.md
shasum -a 256 prototypes/audit-question-families/polynomial_v2.py tests/polynomial_checker_contract_roundtrip.py
```

First test run exited 1: malformed `2..0*x+2` was classified unsupported.
The lexer now classifies a decimal point without following digits as invalid.
Final run exited 0, 48 authored cases, six tests, 0.031 seconds. CLI wrong-form
case exited 0 with `runtime_comparison: true`, `settled_score: null`; exam case
exited 0 with state withheld, null comparison and no diagnostic ID.

SHA-256 source fingerprints:

| Path | SHA-256 |
| --- | --- |
| `prototypes/audit-question-families/polynomial.py` | `f92372bbe73a7ca48c3c0c6600e1f8937ee3cc75ce5be6ab36d1079d303bcb79` |
| `prototypes/audit-question-families/polynomial_v2.py` | `a975956ad1764bc968b0af8f0fc32df8fe628da1749068626898c0724901c2e3` |
| `tests/polynomial_checker_contract_roundtrip.py` | `8090e58f4a70107e498162b92b2c81b948396a7c510327907f5dcd2317c56974` |
| `NEXT-CHECKER-PACKET-2026-09-29.md` | `26c5a0417557a0bffc9e4c8c289ea1a81a7db54aa2b68581d8e1a92857c0b817` |

No package was built or fingerprinted. Production regression, serialized item
schema/Markdown lint, accepted revision, CAS/undo, real session/evidence journey,
restart, fresh package and human accessibility gates were not run. There is no
acceptance or undo evidence for a production checker revision. The three new
owned files can be removed to undo this isolated experiment; existing v1 and
production files remain untouched. No commit, push or install ran.
