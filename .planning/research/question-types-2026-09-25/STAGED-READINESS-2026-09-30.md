# Staged answer/reason readiness, 2026-09-30

Status: concrete synthetic tracer and proposed production contract. F3 remains
prototype. This file records the bounded successor packet result; it does not
accept a grammar, authorize publication, or establish another progress queue.

## Contract decisions proposed for parent review

| Code | Decision | Concrete behavior |
|---|---|---|
| D1 | Fixed authored case declaration | Optional `STAGED-CASES:` JSON array beside the existing bank metadata. Version 1 objects name `activity_id`, plain `stimulus`, `children` (two stable existing MC identities) and `order:["answer","reason"]`. Accepted revision and bank fingerprints are server-derived when binding the sitting, not typed by an author into a self-referential bank hash. Missing, duplicate, overlapping, unsupported, or reordered children fail lint. Existing PAIR metadata never implies a case. |
| D2 | Complete selection units | Select the two-child unit in authored order, with count measured in child attempts. A count/filter/focus request that cannot retain both refuses with an explicit recovery action; exclude a whole case explicitly rather than sampling one child. Do this before the selection evidence event is written. |
| D3 | One genuine commitment per child | An accepted MC response opens the next child regardless of correctness. No practice retries or hints inside the unfinished case. Invalid options, client stage, stale token, replay and Back never advance. No correctness branch or composite verdict. |
| D4 | Release barrier | Practice holds both children's outcomes, rationales and answer-specific diagnostics until reason commitment, then releases each child's feedback separately. Exam/diagnostic retain the existing whole-sitting release policy, including when a case is followed by ordinary items. Committed answer is visible at reason; outcome is not. |
| D5 | Forward compatibility and recovery | Use session v4 for the production transition because old v3 readers would silently ignore a case field and permit early practice feedback. Upgrade ordinary v3 sittings without an inferred case. Optional case fields are additive in public/evidence payloads, with absent fields preserving legacy bytes. Missing/changed binding freezes mutations and preserves evidence. |

Proposed private sitting shape:

```json
{"schema_version":4,"staged_cases":[{
  "activity_id":"case-id","case_revision":"sha256:accepted-declaration",
  "bank_fingerprint":"sha256:accepted-bank",
  "stimulus":"Plain static stimulus.",
  "children":["answer-child-id","reason-child-id"],
  "positions":[0,1],"order":["answer","reason"]
}]}
```

Existing `items`, `cursor`, `responses` and `status` remain canonical. There is
no stored second stage cursor. Public `activity` contains activity identity,
case revision, stimulus, derived `stage`, current child identity and committed
answer when available. Public payloads never expose binding keys or raw score
before release. Response events gain optional `activity_id`, `case_revision`,
`child_id` and `stage`, emitted by the existing evidence builder from verified
session binding. Keep each original item objective and attempt denominator.

## Implemented evidence and exact limits

`prototypes/audit-question-families/staged_v2.py` calls the shipped parser,
public item projection, session adapter, scorer, disclosure projection and
evidence writer. It binds a synthetic declaration inside the existing sitting
and derives stage from its cursor. `tests/staged_activity_contract_roundtrip.py`
contains six tests for wrong-answer advancement, invalid/forged/unopened entry,
replay refusal, fresh-process reload at reason, changed bank/case, unavailable
binding, duplicate/conflicting threaded commitments, two distinct linked child
events, complete-unit refusal, malformed declarations and schema compatibility.

The requested practice mode uses a labelled **exam transport** for a dedicated
two-child sitting. Raw events remain `mode=exam`. This proves the post-reason
barrier without falsely claiming that current practice semantics implement it.
Only after runtime `assessment_feedback_released` verifies closure does this
synthetic practice view call runtime `explain_payload` for both children.
Formal views do not add that practice explanation. No real grade is settled.

Linkage is a disposable projection of existing events through the bound sitting;
raw events do not yet contain case linkage. The tracer normalizes selected item
order after `do_start`; its original selection event is not a production
complete-unit selection trace. Production must choose the unit before writing
that event. Optional prototype fields validate under today's v3 schema, which
is syntactic compatibility only: an old production reader can bypass this
adapter, so this binding is unsafe to register as a production route.

The tracer reuses the journal's root lock to serialize its own guarded
submissions. Concurrent duplicate and conflicting thread tests each produce one
response event and one refused request. Other production writers do not acquire
this prototype lock. An injected failure after evidence append but before
session write preserves the old sitting and detects/fails closed on the durable
event/session mismatch. It does not repair that window. Fresh-process resume is
verified; actual daemon restart, browser detour, Home/Activity/report route
inspection and cross-process simultaneous commitment remain unrun.

The existing Markdown fixture supplies coherent static stimulus and both
ordered prompts. The tracer renders labelled native controls, committed answer
and transport disclosure as a preview. It has no served submit handler, and no
human keyboard/touch/screen-reader/narrow-width acceptance is claimed. Package,
installed-app and clean-machine restore checks remain unrun.

## Minimal production patch and acceptance gates

1. `model.py` and relevant item/format schemas: parse/lint only the optional
   declaration through the existing parser; validate stable children, membership,
   version, allowed form and fixed order. Route acceptance through existing
   reviewed proposals/journal with expected fingerprint, undo and accepted
   declaration revision. No runtime scoring changes are needed for MC.
2. `selection.py`, `surfaces/session.py`, `runtime.py` and session schema:
   select indivisible units before `do_start` persists selection; bind accepted
   revision, add v4 upgrade, derive public stage from cursor, and implement one
   genuine child submission plus D4 in `teaching_transition` and runtime
   disclosure. Audit every reader of session versions and feedback, including
   direct CLI, served quiz, agent JSON, reports and evidence projections.
3. `evidence.response_event` plus existing session owner: add optional verified
   linkage only for staged children. Acquire a session-owner lock across
   load/revision/token check, transition, evidence append and atomic session
   write. Reconcile response rows/cursor from exact durable event identities
   under that lock before accepting another response; do not re-score or infer
   a branch. Ambiguous/different revisions stay conflict, never last-writer-wins.
4. Native quiz/activity clients: use current MC controls, bind the request to
   current item and session revision, display the committed answer, and omit
   keyed fields from unopened views. Verify real desk detour and daemon restart,
   case followed by ordinary MC, ordinary MC before case, and two cases.
5. Gates: legacy v1/v2/v3 upgrade without inferred cases; future-version refusal;
   public/session/evidence schema validation; original ordinary-MC/lesson-run
   regressions; concurrent identical and conflicting **processes**; injected
   crash at each evidence/session boundary; formal/practice leak scans across all
   routes; packaged source parity; separate human interaction acceptance.

Readiness decision: syntax, selection and release choices are concrete and
reviewable. Production implementation needs parent acceptance of D1-D5, then
the named patches and recovery gates. This packet's tracer is complete within
its assigned paths, while F3 product acceptance remains open.

## Verification record

All commands ran on 2026-09-30 against the shared working tree. No commit,
push, build, installation, full preflight or learner-file mutation ran.

- `python3 -W ignore::ResourceWarning tests/staged_activity_contract_roundtrip.py`: six tests pass, final run 0.247 seconds.
- `python3 -W ignore::ResourceWarning tests/a2_question_families_roundtrip.py`: twelve tests pass.
- `python3 -W ignore::ResourceWarning tests/agent_roundtrip.py`: pass.
- `python3 -W ignore::ResourceWarning tests/lesson_run_roundtrip.py`: pass.

SHA-256 snapshots after the final tracer edit:

```text
a3efcef51415ac7e10a0cc5c8a277fbd2cd96e47238fb7d5ed1435debc501033  prototypes/audit-question-families/staged_v2.py
afe2fe84f396745618cde2cac6f42881e80150f195eafcf2455b88c4ec3cb1fc  tests/staged_activity_contract_roundtrip.py
aa6ab9c72be3a7ecdc37845412b32dcb3cada315e2dbace0d603539517c08584  prototypes/audit-question-families/fixtures/bank.md
9b1347ac82bf65091666f7c26a294b26b8fbe9f0a1241e4ca31841ccc2ff6f9c  runtime.py
f58965936ac0a04daf205142591a3699f1c8e4f7d69d6f804bdfffcff8e1c2a4  surfaces/session.py
296d169e5ea43ea30021df3918eed0014b1eceb5d783e2a007a6877639d4b682  schemas/session.schema.json
```

Large production modules were sampled by symbol and function windows, not read
whole. Scope included session start/submit, teaching reconciliation, runtime
session view/versioning/disclosure/atomic writer, response event builder/writer,
pair filtering, and the session schema. This is not an exhaustive route audit.
