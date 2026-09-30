# A2 question-family implementation evidence

Date: 2026-09-29. Owner: A2 under `PARALLEL-IMPLEMENTATION-2026-09-29.md`.
Status: executable synthetic prototypes, ready for A5 integration review.
Production grammar, staged practice, symbolic marking and whole-family
acceptance remain open. No shared parser, runtime, schema, quiz, backlog or
STATE file was edited by this lane.

## Changed paths and recovery

- `prototypes/audit-question-families/families.py`: disposable loopback native
  form client, formal sitting projection, inline fields, fixed evidence spans,
  runtime submission, journaled drafts and static branch/checkpoint presentation.
- `prototypes/audit-question-families/polynomial.py` and `acceptance.json`:
  bounded advisory polynomial analysis and 16 authored acceptance inputs.
- `prototypes/audit-question-families/fixtures/bank.md` and `README.md`:
  four synthetic items, static prompts, launch recipe, authority and gate limits.
- `tests/a2_question_families_roundtrip.py`: 12 executable tests, including a
  fresh-process stage reopening, invalid unsaved draft recovery and journal undo.
- `prototypes/audit-question-families/blank-refusal.png`, `staged-complete.png`
  and `verification.json`, plus this dated evidence file: proof and fingerprints.

All final lane paths were absent at entry. Base HEAD was
`8ccd45832b66b0b86bb406d6232ef0633ef71dc3`. Before editing, copied dirty inputs
and their SHA-256 manifest into the OS temporary directory named
`itembank-a2-before-ysgt8he_`. Its `manifest.json` records absent initial lane
paths and the exact dirty parser/runtime/session/journal/schema/backlog bytes.
The final `verification.json` records before/after hashes and concurrent drift.
The temporary snapshot is local recovery evidence, not a portable package.
Undo this lane by removing only its new named paths; never restore shared
inputs from that snapshot over another writer's changes.

## What the executable slices establish

F1 reuses the existing fill field contract and semantic answer, adding only a
prototype rendering convention: each `{{field_id}}` occurs once. Both native
inline inputs have persistent field IDs and visible labels. Original unfinished
bytes survive runtime refusal and a fresh client; repeated identical draft
saves write nothing, and stale expected fingerprints refuse through the journal.

F3 reuses the existing whole-PAIR selection in bank order and two ordinary MC
children. Only exam/diagnostic modes are supported. The runtime commits a valid
wrong first response and advances; invalid, duplicate, forged-stage and stale
submissions cannot open another stage. Cursor and commitment come from the
ordinary sitting, not the sidecar. Two ordinary runtime evidence events retain
distinct opaque child IDs and objectives. Their parent activity/revision is not
yet attached to evidence. Practice is refused before creating files because its
current runtime holds wrong responses and does not implement the required
answer-then-reason commitment/release policy.

Fixed evidence selection maps three stable source anchor IDs to exact offsets,
quotes and a passage fingerprint. Multi options use the ordinary runtime
scorer. Changed passage or bank revision refuses recovery instead of guessing.
This is predefined whole-span selection, not free annotation or first-error
grading. A predefined source passage is visible before selection; correctness
and explanations stay behind the normal formal-sitting disclosure gate.

F2/F9 polynomial analysis is explicitly advisory. It accepts one variable `x`,
explicit arithmetic and numeric rational literals, powers zero through four,
at most 160 characters and 64 syntax nodes, and rational numerator/denominator
bounds of one million. It uses no eval, donor library or dependency. Exact
coefficient equivalence calls existing `runtime.score_response` on numeric fill
fields. Expanded-form syntax inspection and the two hardcoded synthetic
misconception rules produce advisory outcomes only, never session marks or
evidence. Correct, wrong, equivalent/wrong form, invalid, unsupported,
unavailable teacher and injected error remain distinct. Formal analysis hides
comparison and diagnosis through `assessment_feedback_released`; production
attachment must supply the actual runtime-owned session, never a client flag.

F6 branch content is a post-case teaching projection of the committed choice,
not correctness. Route A supplies a changed-start transfer example; route B
supplies a trace example. Neither transcript opens before both children commit.
The static observation's simulated position and completion persist through
`journal.commit_operation` with CAS, and undo goes through `journal.undo`.
No video is played and no reading duration, learning gain or assessment graph
is certified. The native checkpoint controls are independently labelled.

## Verification and observed failures

Successful commands on this lane:

```text
python3 tests/a2_question_families_roundtrip.py
python3 itembank.py lint prototypes/audit-question-families/fixtures/bank.md
python3 itembank.py guard prototypes/audit-question-families
python3 -W ignore::ResourceWarning tests/fill_roundtrip.py
python3 -W ignore::ResourceWarning tests/check_disclosure_roundtrip.py
```

Results: 12 A2 tests pass; four authored items have zero lint errors/warnings;
the scoped guard has zero offenders; eight existing fill tests pass; existing
JSON/CLI replay/API/practice/completion disclosure checks pass. The final A2
command log is retained locally as `itembank-a2-question-families-final.log` in
the OS temporary directory. ResourceWarnings originate in sampled existing
file readers; this lane did not change them. No combined full preflight ran.

The first A2 run rejected two-option MC fixtures. They now have four options.
Later failures were test assumptions: response events use `event_type`, formal
reports retain null correctness fields, and persistent child IDs require
authored `[ID:]` directives. Those assertions and synthetic IDs were corrected.
The scoped guard initially refused `bank.md` outside a fixture directory; moved
it into this lane's `fixtures/` and reran lint/guard successfully. Initial lint
warnings prompted valid distractor syntax, SECOND-BEST and runtime-generated
content hashes. None of these failures was waived or patched in shared code.

Browser proof used a disposable in-app tab against a serial loopback server.
The final tested bank bytes match `fixtures/bank.md`. Native keyboard Space and
Enter committed a wrong prediction, reload restored the unopened reason, reason
commitment closed the case at 1/2 and opened only its permitted static branch.
A checkpoint saved at position 60. Inline blanks kept unsaved `blue` and `oops`
after refusal and reopening; Tab moved from field `color` to `count`; correction
to `5/2` completed at 1/1. Fixed evidence checkboxes completed at 1/1 through
ordinary multi scoring. Screenshots capture staged completion and blank refusal.
Some browser AX observations preceded navigation completion; subsequent
screenshots verified the settled view. Prototype processes and tabs were closed.

Source proof only. No fresh package, installed app, real learner sitting,
human screen-reader/touch/reflow review or learning-transfer trial was run.
No commit, push, branch switch, installation, release or external account write
occurred. Server/test session, journal and evidence files were synthetic and
temporary. The formal session is authoritative for cursor/evidence; the
sidecar is presentation only. The serial server does not prove concurrent
submissions, daemon restart or crash-window reconciliation.

## Exact A5 wiring requests after A1 releases shared files

| Ref | Minimal request and authority | Required promotion gate |
| --- | --- | --- |
| P1 | In `surfaces/quiz_page.py:_form_controls`, `asFill` and `asFillOffline`, review/adopt one escaped inline marker convention referencing existing `public_item.fields` IDs. Reuse current draft restoration and ordinary fill submit; no new field kind or scorer. Put marker validity in the existing fill lint path only after syntax review. | Each field appears exactly once; missing/duplicate/unknown marker fails visibly; plain Markdown stays coherent; native/rich responses agree; invalid unsaved entry and refused-submit recovery survive reload; source/package tests share fingerprints. |
| P2 | Settle the existing `NEXT-STAGED-PACKET` readiness choices. Extend `model.py` declaration validation and `runtime.teaching_transition` additively for immutable case revision, whole-unit selection and practice commitment independent of correctness. Keep `surfaces/session.py:do_action` and the existing evidence writer as the only durable submission path. | Withhold first-child practice feedback until reason commitment. Bind actual child evidence to activity/revision/stage, and test forged stage, duplicate/conflicting concurrent submissions, missing/changed revision and crash reconciliation. Inspect quiz/Home/report/agent projections; review schema compatibility. |
| P3 | Review a predefined span-selection declaration binding stable anchor ID, source revision, offsets, quote and passage fingerprint to existing multi responses. Put accepted validation in `model.py`, public projection in `runtime.public_item`, and native controls in existing quiz renderers. | Source edits refuse stale anchors and preserve original selection. Reopen same IDs. No feedback leak. Authored acceptance through the existing proposal/journal owner and package journey. Free span/first-error formats stay separate. |
| P4 | Resolve `NEXT-CHECKER-PACKET` grammar, limits, expanded AST rule, outcome/evidence semantics and authored test storage. Move reviewed canonical analysis into existing runtime helpers, then let `score_response` settle valid supported inputs. Do not import this advisory module as a production scorer or merely add an unsupported fill kind. | Validate teacher and diagnostic rules; reject ambiguous precedence; invalid/unsupported/unavailable/error never become False evidence. Bind checker revision, preserve original input, gate diagnostics with the actual runtime session, prove proposal acceptance/undo and source/package formal/practice journeys. |
| P5 | Review an activity graph declaration with immutable node/edge/ending identities. Use runtime-owned committed children for assessment progression and existing lesson/presentation authorities for reading/checkpoint state. Extend media only with accepted transcript/recovery semantics. | Reject cycles/missing destinations/unauthorized skips; branch policy never discloses unopened answers. Resume same branch and checkpoint, preserve transcript/keyboard routes, and distinguish presentation completion from settled assessment evidence. |

P1 is a presentation slice with existing scoring and can be reviewed first.
P2-P5 require the named contract gates; their prototypes are not accepted
schemas or production implementations. Shared-file ownership remains with
A1/A5. Do not edit a production file until that transfer is recorded.

F4 stays backburner until a named objective, validated checker and isolation
gate exist. F5 stays backburner until a named objective, media consent/storage
and review rubric exist. F7 executable Parsons needs indentation/distractors,
declared isolated runner and prediction commitment. F8 variants/workspaces and
graphical domains need checker/seed revision, model validity and difficulty
review. F10 needs a scientifically validated objective/model and an interaction
trial. No trigger was established by this synthetic work; broader F1-F10
dispositions remain owned by the existing backlog.

Context sampled: workflow reading/authority/prototype rules, current STATE,
backlog and successor packets, source-to-course North Star and operation
authority, UI-SPEC section 8, parser/fill/PAIR symbols, runtime public/scoring/
disclosure/session symbols, session adapter and journal CAS/undo signatures.
Large parser/runtime/session/quiz modules were sampled by symbol, not read in
full. No exhaustive codebase, product or human accessibility audit is claimed.
