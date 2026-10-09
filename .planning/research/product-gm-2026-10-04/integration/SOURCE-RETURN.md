# Shared source-review returns

STATUS: source released for integration.

The bounded worker releases its exclusive `surfaces/daemon.py` writer lease
to the integration root. Inherited input was SHA-256
`d53164f53a439368eac97b6510c78d9e8fd6ab38ef8813337f7c500b35db1c2b` at shared
dirty HEAD `28bf561865cf0696a8beb42dd6f356b8bf6ec648`. No Git, provider,
private learner, package, installation or broad preflight operation was run.

## Source and authority

S1: `_course_source_return(handler, course_id, query=None)` accepts exactly
one nonempty bounded `return_source` identifier and resolves it against the
current clean admitted course's `doc.sources`. The helper requires exactly
one matching row and derives the current accepted course ID and source index.
It returns exactly `{href, label, source_id, course_id}` with the label
`Back to source review`. It never accepts a return URL or reads source text.
Unknown, removed, duplicated, cross-course and unclean memberships retain
the task's existing origin. The optional internal `query` parameter applies
the same validation inside an already admitted exact saved-sitting return.

S2: Map back controls, lesson context navigation and guided/continuous mode
switches carry the derived source identity. Saved-sitting returns retain the
existing bank membership, selection, mode, session, revision-time and schema
admissions. Invalid optional nested source context is discarded while the
valid exact sitting return remains usable. Quiz home destinations, form
actions, PRG redirects, next-question links and symbol detours preserve the
source context. Explicit practice opening retains its existing runtime door.

S3: After the root's reader repair lease, `handle_course_reading_get` passes
`source_return` only for a valid mapping. Ordinary and unadmitted reading
calls omit the keyword. The current root-owned reader support was checked at
SHA-256 `beacbb86c2959cc644bc6c5ce0a7eb6e0a14e6d745f6e8f28fc13e62a0f39e71`.
Source-return assignment links survive reload and restart without releasing
changed-source bytes or changing notes, evidence, accepted courses or sources.

S4: The root-requested compact-frame repair retains whether overview
activities existed before deduplication. When the primary saved sitting was
the sole path activity, the empty additional path section is omitted. A truly
empty course retains its original missing-activity copy. Native checks cover
both cases and preserve all sitting and evidence bytes.

## Checks and release hashes

| Path | SHA-256 |
| --- | --- |
| `surfaces/daemon.py` | `5146101bd20782c87474d8ba53e2686e010d56a36e3743244d6ed54de34cd0b6` |
| `tests/product_gm_integration_source_return_roundtrip.py` | `596d4ac33da6e2394eab0bf8e15f2595824a5033e850861df6391243e9789945` |

The new suite passes 11 targeted checks: current identity/index derivation,
invalid and ambiguous identity fallback, native map/lesson restart and mode
continuity, native malformed fallback, native reading restart continuity,
ordinary reading compatibility, native practice restart and exact sitting,
native quiz invalid fallback, PRG/symbol continuity, nested sitting validation,
and sole-practice versus truly-empty course framing.
`tests/product_gm_integration_course_roundtrip.py` passes four existing checks;
`tests/quiz_symbol_return_roundtrip.py` passes default/practice/exam continuity;
`tests/course_shell_roundtrip.py` passes. Scoped `git diff --check` passes.

Receipts and complete before-images are under
`.reasonix/product-gm-20261004/integration/source-return/`. `attempt-1.log`
retains five passes, two failures and one error from harness assumptions:
the native shell prefixes its back label with an arrow, MC forms use
`option`, and runtime session writes may create an empty lock file.
`attempt-2.log` passes 16 checks because seven imported ReadingDesk tests
were inadvertently discovered too. The import was changed to a module;
`attempt-3.log` passes ten owned checks and `attempt-4.log` passes the final
11. All earlier receipts remain. Practice inspections preserve exact session,
bank, mode, item selection, cursor, responses, status, teaching state, profile
and timing. Only the existing runtime-served timestamp and empty session lock
are allowed to change. Symbol lookup records its existing `term_lookup`
event and no answer; the explicit tested submission advances once through
the runtime scorer.

## Remaining integration gate and recovery

R1: The native quiz's existing `cx-home` anchor now reaches the derived source
review, but its visible text is still the bank title because `quiz.page_for`
has no back-label parameter. The integration root owns the later presentation
lease. Add an optional `home_label` parameter with a default preserving existing
calls, render the explicit supplied label on this anchor, and pass the derived
label from `_send_quiz_page` only when the source mapping is valid. These
targeted tests intentionally assert the quiz destination while leaving its
wording to that final integration repair. No unsupported renderer keyword is
currently passed.

R2: The full changed-source Sources -> emitted reading/lesson/map/practice
journey, 320px/script-free browser checks, final current lane-release pins and
the sole combined preflight remain root-owned. This worker does not close
parity I1 or the whole programme. Packaged, installed, human accessibility and
learning-equivalence gates remain unrun or open.

Recovery: review `daemon.task.patch` and reverse only the worker's current
matching hunks against `daemon.before.py.txt`, preserving the inherited
compact-frame work and later root changes. Source/test/report writes used
expected-base validation, atomic publication and the existing integration
`operations.jsonl`. Removing the new owned test is safe only after checking
for later edits. No learner-data undo is required for read-only inspections.
The daemon was sampled by symbol and changed windows rather than read whole.
