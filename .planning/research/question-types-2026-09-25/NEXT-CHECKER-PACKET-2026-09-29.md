# A5 bounded polynomial checker successor packet

Status: implementation proposal, not an accepted grammar or implemented checker.
Owner route: BACKLOG.md F2/F8/F9 and WORKFLOW-AUDIT-2026-09-29.md A5. Keep these
family dispositions; one checker cannot close symbolic math or diagnostics.

GOAL: One synthetic univariate polynomial-equivalence task with rational
coefficients and an authored expanded-form requirement, followed by named
misconception tests. Use exact arithmetic, preserve original input and keep
every verdict and diagnostic disclosure inside the runtime.

## Existing facilities and the actual gap

`runtime.fill_number` parses bounded decimals, fractions and scientific notation
into `Fraction` without evaluating code. `_fill_quantity` supports authored
multiplicative unit factors. `fill_spec_errors` and `fill_response_error`
validate authored fields and learner entry; `score_response` owns text/numeric
verdicts and tolerances. This covers equivalent numeric spellings and declared
units, not symbolic expressions or required algebraic form. The ordinary
submission route rejects fill entry errors before scoring. Reuse this lifecycle.

`public_item` and the hint/report release functions own disclosure. Existing
visual misconception mapping is a bounded representation precedent, not a
generic F9 diagnostic tree. `surfaces.agent_operation` already owns reviewed
drafts, expected fingerprints and acceptance through `journal.commit_operation`.
Reuse it for authored checker/test revisions, not a separate authoring queue.

## Proposed smallest contract, requiring review before implementation

Recommended domain: one variable `x`, rational numeric literals, parentheses,
explicit `+`, `-`, `*` and powers with nonnegative integer exponent. Fix limits
before coding: maximum input length, token/AST size, degree (suggest at most 4),
coefficient numerator/denominator bounds and intermediate expansion work.
No variable division, functions, implicit multiplication, Unicode algebra,
complex numbers or arbitrary evaluation in this slice. Recognizable out-of-domain
constructs return unsupported, malformed grammar returns invalid; neither
silently becomes an ordinary wrong answer.

Use a bounded grammar and coefficient-vector canonicalization in the runtime.
Compare exact rational vectors for equivalence. Inspect parsed syntax separately
for authored `required_form=expanded`: `2*(x+1)` and `2*x+2` are equivalent,
but only the latter satisfies this task's declared form. Do not use string
matching to establish semantic equivalence or accept a sampled numeric check.

Review an additive versioned checker specification alongside existing fill
fields, with domain ID/version, variable, limits, required form, private teacher
answer and private named diagnostic rules. Existing text/numeric field kinds
and old evidence keep their current meaning. The UI receives the response
grammar and required form, never the teacher coefficient vector or hidden
misconception tests. Decide the exact item schema/grammar before implementation;
an arbitrary extra `kind` value is not already supported.

Private outcome states must distinguish correct, mathematically wrong,
equivalent-but-wrong-form, invalid, unsupported, unavailable and checker error.
`score_response` still settles valid responses; a failed checker never records
`False`. Preserve entered bytes and supply an actionable correction/retry path
without exposing the key. Settle how unresolved outcomes fit existing session
and evidence schemas before adding them. Do not overload pending prose marking
or turn an unsupported input into mastery evidence.

For F9, author at most two named rational-polynomial misconception answers,
for example distribution omission and a sign error. Rules compare exact
canonical outcomes, not model guesses. Declare deterministic precedence and
reject ambiguous overlapping rules. Diagnostic text uses the existing practice
disclosure gate; exam/diagnostic quiz, Home, Activity, reports and JSON withhold
it until the normal release point. No partial credit or dependent inputs yet.

## Acceptance and readiness gates

Author a private question-test table beside the checker specification: learner
input, expected outcome, expected permitted diagnostic ID and checker version.
For target `2*x+2`, include equivalent reordered/decimal/rational coefficients,
`2*(x+1)` wrong form, `2*x+1` misconception, `2*x-2` sign error, malformed
`2*(`, unsupported `sin(x)` or `1/x`, over-limit exponent/expansion, invalid
teacher answer and injected checker failure. Assert originals survive refusal,
unresolved states append no settled incorrect score, and test order is stable.

Before acceptance, run authored tests for teacher answer and every diagnostic,
lint both plain Markdown and serialized schema, show preview and bounded diff,
accept atomically through existing journal controls and verify undo. Pin checker
version in response evidence and report it without inventing variant equivalence.
No random variants in this slice; F8 still needs seed plus checker version,
validity and difficulty assurance before parameterization.
Existing regression anchors: `tests/fill_roundtrip.py`,
`tests/fill_surface_roundtrip.py`, `tests/check_disclosure_roundtrip.py`,
`tests/agent_roundtrip.py` and authoring-operation acceptance/undo checks.

Readiness gaps: reviewed grammar/limits, required-form AST rule, schema/version
migration, unresolved-state/evidence semantics, authored test storage/acceptance
validation, diagnostic precedence and exact teaching release policy. These are
contract decisions to settle before production edits, not implemented facilities.

Prove a normal author-to-lint-to-preview-to-sitting-to-feedback-to-report journey,
reload/restart with original response, and backward compatibility. Verify fresh
package bytes and the same candidate journey separately. Native labelled text
input/static examples must work without enhancement; keyboard, touch,
screen-reader and installed-app acceptance remain explicit human gates.

EXCLUDES: CAS library/runtime dependency, arbitrary Python/executable check code,
sets/intervals/matrices/vectors, affine or dimensional units, significant figures,
proof grading, generic graph construction, partial credit, dependent inputs,
multi-file workspaces, whole-course rewrites, donor code and external egress.
F2/F8 remain bounded prototypes; F9 remains a prototype depending on a reviewed
checker. Wider capabilities retain their existing dependencies and triggers.

RETURN: reviewed decisions, changed paths, authored cases and exact source/package
fingerprints, failed and unrun gates, acceptance/undo evidence. Update the existing
backlog/audit/STATE owners. This packet grants no commit, push or install authority.
