# Checker production evidence, 2026-09-30

Implemented production behavior under the user request to implement in parallel. The runtime is the sole comparison and scoring authority. Existing unrelated dirty changes were preserved. This record describes sampled functions and scoped checks, not an exhaustive module audit.

## Changes

`kind: polynomial` extends existing FIELDS JSON. Private checker configuration and pinned authored test rows participate in the existing item fingerprint. Lint replays required teacher, diagnostic, wrong-form and refusal cases. Strict bounded parsing and exact Fraction expansion live inside runtime.py. Configuration errors precede learner syntax; typed PolynomialRefusal preserves unresolved invalid, unsupported, unavailable and internal-error states. Refusals use the existing entry-error route without appending a response or changing session bytes. Canonical response identity includes pinned version, exact coefficient vector and expanded-form bit. Raw strings remain in evidence.

Public labelled inputs expose only the declared domain, version, variable, form, grammar and fixed limits. Evidence pins checker_outcomes privately. Active formal projections withhold the whole outcome, and practice diagnostic identity waits for the existing trap tier. No new diagnostic explanation text is released outside the authored hint ladder. Numeric and text fill behavior remains covered by existing regressions.

Optional fixed STAGED-CASES metadata uses the existing bank parser through a list-compatible BankQuestions object. Structural lint rejects unsupported versions, duplicate/overlapping/missing child identities, unsupported types and changed stage order. Existing PAIR does not imply a case. `surfaces.agent_operation.propose_staged_cases` supplies a local bounded bank-header proposal and reuses existing reject, journal-backed CAS acceptance, revision and byte-exact undo. Item block bytes are preserved. Tests prove cancellation, stale refusal and accept/undo.

## Verification

These commands passed after integration:

- `python3 tests/polynomial_production_roundtrip.py`: eight production checks, including exact semantics, config overlap/version/test rejection, typed refusals, real-session injected error without mutation, diagnostic-tier boundary, raw evidence and reviewed author acceptance with stale refusal and undo.
- `python3 tests/staged_parser_roundtrip.py`: five declaration and reviewed header authoring checks.
- `python3 tests/staged_production_roundtrip.py`: eleven integrated sitting checks at the final local run; worker may add further adversarial cases.
- `python3 tests/staged_checker_disclosure_roundtrip.py`: four independent real-session disclosure checks.
- `python3 tests/fill_roundtrip.py`, `python3 tests/fill_surface_roundtrip.py`, `python3 tests/agent_roundtrip.py`, `python3 tests/agent_operation_roundtrip.py`, and the existing synthetic `polynomial_checker_contract_roundtrip.py` passed.

Root owns broad preflight after the coordinated freeze. Served browser journeys and human accessibility acceptance belong to the UI worker/root record. No commit, push, package, build, install or real course mutation occurred in this worker scope.

## Recovery and limits

Accepted staged header edits use the existing proposal undo route. Runtime session submissions refuse unsupported entries and preserve the previous durable session/evidence; the native/JSON UI owns the recoverable draft. Staged binding is validated before timed expiry and direct model invocation. A learner-owned session with every staged identification field deliberately removed is indistinguishable from an ordinary legacy sitting; preserved `staged_binding_required` detects missing cases. This is a recovery contract, not hostile-file tamper security.

Module reads were symbol windows only: model parser/lint/fingerprint/spec; runtime fill/scorer/public/projection/staged binding/hint paths; evidence response constructor; session action/recovery; existing agent proposal/accept/reject/undo. The full large modules were not read.

## Fingerprints

Initial observed SHA-256 before worker mutations: model.py `2170d336e5161428a78e184de8327d0001c69970d7ea6f0c5a9d6ac36f164752`; runtime.py `6d08c7ebc6f6588bfccb8d409c1e67267f334401223f4ec01b2580fee8b7a797`; item schema `0bf7c46a1fda484d8137a69bb24f6b7666a4bef11bee5955a726b55339cb1411`; lint schema `c648ec733475947771e8b9d23e52245d03fbb8900f1852caf03a1e98564cb4aa`. Runtime/evidence/session were transferred from the staged worker after its first passing integration; these initial hashes are not repository-clean baselines.

Final worker snapshot before root preflight (later coordinated edits supersede this snapshot):

| Path | SHA-256 |
| --- | --- |
| `model.py` | `3b37b486fd46d8c30b087d72740b9c92e5b048bea4e00b35d5bce0b57d504095` |
| `runtime.py` | `27e06b1c0053000e45178864b0de9ecc394b55003652223955972c10ef194846` |
| `evidence.py` | `130fd4d13592d2fc0a93013dec619316a1887447cad85e48500a1203a9b82aa4` |
| `surfaces/session.py` | `a95af8bb83ab40c16f1f704252d5b44a3701156f6212aa11c63fa129e82205c9` |
| `surfaces/agent_operation.py` | `2bb85f91e640d3f3e4f6b2680489ead445cf2d9eb2303c3aa92a6a2820427482` |
| `schemas/item.schema.json` | `19deb0e0e7a288356b077d9b39bbab196fb8ba1fcad077de15f748f98a3db61b` |
| `schemas/response.schema.json` | `f9e9aef6ad940d3e13d3a413360bd454f10f5328d8ff77deb3c61bb3ac5c5fa6` |
| `schemas/lint_error.schema.json` | `f11f128cb79ec6bdb7d6af3ca2a56339c4d551a6fa30d24cc697851d49ff8a42` |
| `tests/polynomial_production_roundtrip.py` | `a8dca22c95bf0ed8900cf08a22e9e355894f4514b0cffd55981d5a22e1f9bd8b` |
| `tests/staged_parser_roundtrip.py` | `9040f1dcc2beaac0370d472ffc4f375ccdd4dfc89cd5dc11f6ab81a4e5796d50` |

Recovery snapshots supplied by the staged worker are at `/tmp/itembank-staged-baseline/`: runtime.py.txt, evidence.py.txt, session.py.txt and selection.py.txt. These are temporary local files, not durable accepted revisions. Their SHA-256 values:

- `runtime.py.txt`: `6d08c7ebc6f6588bfccb8d409c1e67267f334401223f4ec01b2580fee8b7a797`.
- `evidence.py.txt`: `b7e9729478756e5aa79da80145156a5558f70b9c497c4fafd5f816bfce52170b`.
- `session.py.txt`: `f58965936ac0a04daf205142591a3699f1c8e4f7d69d6f804bdfffcff8e1c2a4`.
- `selection.py.txt`: `e52ce8a3bb0c40d934b6ba2df2499a09eba4bdeff8ba4fd8ad85d35a93bc9d94`.

Worker-modified paths: model.py, runtime.py, evidence.py, surfaces/session.py, surfaces/agent_operation.py, schemas/item.schema.json, schemas/response.schema.json, schemas/lint_error.schema.json. New paths: tests/polynomial_production_roundtrip.py, tests/staged_parser_roundtrip.py and this evidence record. The parser/schema/agent-operation baseline was fingerprinted but not copied before mutation; bounded undo for those source edits requires the root coordinator baseline or selective reviewed diff, never resetting inherited dirty work. This gap is explicit.
