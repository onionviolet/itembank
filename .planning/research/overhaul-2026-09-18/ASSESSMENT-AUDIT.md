# Assessment and question UI audit

Date: 2026-09-18. Owner: assessment audit lane. Read-only source/test audit.
Only this report was written. No production edits or commits were made.

## Outcome and scope

The current assessment foundation has real depth: separate MC and multiple
response controls, one scoring authority, mode-gated hints and disclosure,
pending prose review, several structured response types, and persistent
feedback before explicit advance. The key gap is behavioral parity across its
three rendering paths. Some tests assert source text or runtime transitions
without operating the question controls that join them.

The paths must be distinguished before reporting defects:

| Path | Source seam | Meaning |
|---|---|---|
| Server baseline, with or without JavaScript | `surfaces/quiz_page.py:981` `baseline_for`, `:3840` start adoption | Native forms and server transitions. JavaScript adopts the baseline instead of replacing it. This is not the same control implementation as API-driven rendering. |
| API-driven served JavaScript | `surfaces/quiz_page.py:1784` verify, `:1855` renderItem, `:1900` asChoice | Used when no server baseline is present. Runtime still owns verdicts, but client code owns control replacement and result projection. Reachability of each deployment is root's route/browser audit. |
| Static offline build | `surfaces/quiz_page.py:1243` render, `:1290` asChoice | Embeds Python-produced keys for local comparison and records nothing. It is not equivalent to a protected served exam or durable offline sitting. |

Large modules were sampled by symbol, not read completely. Sources sampled:
`runtime.py` public_item, feedback policies, selection_feedback, transition,
and marker_close context. `surfaces/quiz.py` page_for and record_answer.
`surfaces/quiz_page.py` baseline, controls, assist, rich text adapters, API
projection, feedback, summary, and boot. Also sampled daemon response filtering
and named tests below. No fresh competitor research was needed for this audit.

## What is actually enhanced

| ID | Verified source behavior | Evidence and remaining boundary |
|---|---|---|
| E1 | MC uses a radio group. Multi uses checkboxes and a selection-count legend. Native labels and fieldsets preserve a usable HTML control baseline. | `_form_controls` at quiz_page.py:836 and JS asChoice at :1900. `tests/surface_roundtrip.py:278` checks source markers and target-size CSS. It does not exercise native arrow keys or selection limits in a browser. |
| E2 | Runtime permits practice/remediation feedback about only the learner's selected multi options while retaining all-or-nothing scoring. Baseline displays that feedback. | runtime.py:1896 and quiz_page.py:1003. `tests/hint_roundtrip.py:129,178` cover policy and withheld unpicked options. `tests/serve_roundtrip.py:601` covers the served own-selection card. API-driven JS differs, see F2. |
| E3 | Help has a runtime-owned ladder. Disclosed cues augment the unchanged prompt in a collapsible assisted-question layer. Locked help is separate. | quiz_page.py:3530 and baseline helper calls. Hint tests cover entitlement, duplicate/empty attempts, mode restrictions, and unrevealed content. JS hint tests mostly inspect source strings, not dynamic focus or failure. |
| E4 | Feedback persists before explicit Next. API-driven new questions focus the prompt. Next names the upcoming position and total. Baseline uses an explicit continuation link. | quiz_page.py:1855, :1037, :3731. Surface/serve tests assert the contract. Root owns installed and browser verification. Static render has a focusable heading but no corresponding heading.focus call in its sampled render body. |
| E5 | Richer presentation includes exact-symbol definitions, a structure adapter, and local KaTeX enhancement of backtick expressions in stems/options/row text with raw fallback. | quiz_page.py:484, :551 and quiz.py:207. Content initially escapes HTML. This is bounded enhancement, not evidence of a general rich Markdown or arbitrary-media option format. |
| E6 | Public response contracts cover mc, multi, table, dnd, build, short, check, and visual. Check/visual have declarative public interaction contracts. Short remains pending. | runtime.py:44. Native baseline offers selects/textareas and explicitly refuses visual interaction without JS. Type presence does not establish equal usability, feature depth, or static support. |

## Specific findings and verification gaps

These are source-established behavior gaps or testable defect candidates.
They are not claims that the installed baseline screen exhibits every defect.

| ID / priority | Finding and exact seam | Required falsification or acceptance test |
|---|---|---|
| F1 / P1 | API-driven `asChoice.go` removes Submit at quiz_page.py:1957. `close` clears actions and the hold branch only re-enables inputs at :3608. `revert` does not recreate Submit. Source implies a wrong practice answer strands the retry action. | No-baseline page: select wrong MC, submit, change selection, then submit again without reload. Repeat with multi. A functioning retry control would falsify the predicted dead end. Test ordinary baseline separately. |
| F2 / P1 | API `verify` at :1784 projects only action, score, explain, and next. It drops selection_feedback, refused, refused_reason, and interaction_result. The JS hold branch also does not render own-picks feedback. Some downstream branches expect dropped fields. | Feed synthetic runtime envelopes through verify/settle. Check multi feedback, code refusal, and per-case observations survive without leaking withheld content. Compare with baseline. |
| F3 / P1 | Network failure re-enables controls, but Try again closes over the original response at :1831. A changed selection may be visible while the old response is resubmitted. | Reject first fetch, change MC and multi choices, then retry. Assert the submitted payload matches the visible state, or keep inputs locked and explicitly retry the original operation. Also test accepted-on-server/lost-response recovery. |
| F4 / P1 | API-driven MC sets `submit.disabled = multi` at :1948, so MC begins enabled with no choice. Runtime empty submissions hold without a real verdict, while JS hold copy says Not correct. Multi silently rejects choices above the requested count. | Empty MC must not be presented as wrong. Over-limit multi interaction should produce understandable feedback and preserve valid choices. Exercise keyboard as well as pointer. Baseline has no required attribute or client selection-count limit, so test its server validation separately. |
| F5 / P1 | JS shuffles original-key options, assigns new letters, and pins text matching Both A and B or all/none above at :1901. It does not rewrite letter references within option text. Pinning a Both A and B option does not preserve its referents. | Synthetic cross-referential option with controlled shuffle must retain meaning or be rejected from shuffle. Also verify displayed letters and feedback labels match across retries. No claim that current real banks contain this pattern. |
| F6 / P1 | Runtime exam/diagnostic responses defer without advancing the cursor in sampled transition branches. JS non-short defer branch offers Check again and says verdicts wait until the sitting closes. A normal explicit learner finish/advance sequence was not established in this sampled path. | Root should walk a two-item synthetic exam from start through final review. Determine the intended close authority and reachable UI. Do not infer exam completeness from a passing transition test or implement a client bypass. |
| F7 / P2 | JS summary uses in-memory miss list to say Clean sweep when empty at :3774. Miss list is not an authoritative summary of a resumed or deferred-feedback session. Summary does show runtime auto counts and pending count separately. | Resume/finish with a runtime summary containing wrong or pending work but empty client history. Copy must remain truthful and not imply all correct. Test zero auto-marked items as a distinct state. |
| F8 / P2 | Short-answer JS offers self-mark buttons through the runtime API. Baseline pending copy directs the person to a terminal command. These are materially different completion journeys at :1013 and :3638. | Compare pending prose completion through baseline, no-JS, API-driven, and intended formal assessment roles. Confirm self-mark authority is appropriate per deployment. This audit does not establish a permission defect. |
| F9 / P2 | Confidence exists outside this renderer, but no learner confidence input was found in quiz_page.py. quiz.py:460 records confidence=None and the sampled legacy daemon path also passes None. No question flag/review-later control was found in these quiz renderers. | Treat confidence capture and flagging as absent in the inspected UI, not absent everywhere. Root should map protocol/CLI support before proposing additive UI. No current verification of a whole-product flag store. |
| F10 / P2 | Baseline options render escaped text. API/static options escape text then use presentation adapters. General images, tables, code blocks, shared stimuli, and rich option semantics are not demonstrated by these functions. | Build a synthetic corpus with multiline code, equations, long choices, references, and accessible media. Define supported semantics before extending rendering. Do not reuse arbitrary authored HTML or a second parser. |

## Test evidence and what it does not prove

Executed once: `python3 tests/hint_roundtrip.py`, exit 0 on 2026-09-18.
It reports passing transitions, tiers, modes, evidence, outcomes, and CLI/API/
browser-surface contracts. That label does not mean this audit drove a browser.
Its sampled cases establish wrong hold, correct retry transition, own-picks
gating, mode immutability, pending short, and crash-window reconciliation.

Read but not run: surface_roundtrip's native-control/source assertions,
serve_roundtrip's baseline feedback and focus cases, and
`tests/js/hint_ladder.test.mjs`. Root owns surface/serve gates and live UI checks.
The JS ladder suite uses regex on emitted source. It cannot catch a removed
Submit button or a retry closure sending an old answer. No full-suite,
screen-reader, touch, installed-app, or exam end-to-end pass is claimed here.

## Useful additions beyond visual polish

| ID / disposition | Bounded proposal | Authority and acceptance |
|---|---|---|
| A1 / Core | A reusable rendered transition test harness for the three quiz paths, driven by synthetic public envelopes. | Test wrong-change-retry, count limits, network ambiguity, held hints, pending review, exam closure, and summary. Harness asserts control behavior and transmitted payloads without deciding correctness. |
| A2 / Prototype | Selection count and option elimination as learner-owned scratch state. | Announce selected N of required M. Elimination must not remove answer choices from the authored item or alter scoring. Keep reversible keyboard controls and distinguish scratch from a submitted answer. |
| A3 / Registered | Optional confidence plus local flag/review-later state. | Confidence is a recorded learner report, never a score multiplier. Flags attach to stable item/revision and session identity. A final review queue must obey the assessment's navigation policy. |
| A4 / Prototype | Shared stimulus and rich-option authoring profile with portable fallback. | Preserve one parser, source provenance, explicit semantic blocks, static meaning, and objective alignment. Test reading burden, long choices, code, math, and accessible media before claiming MC parity with richer platforms. |
| A5 / Registered | Answer receipt and recovery status next to the response. | Distinguish edited locally, sending, recorded, retrying acknowledgement, and not recorded. Bind retry to one intended item/action. A receipt describes runtime acknowledgement and never supplies a second verdict. |

These proposals are local audit dispositions for root synthesis, not accepted
schema changes. Confidence, flags, scratch state, and rich options require
existing-owner checks before implementation. The smallest useful next step is
to reproduce F1-F4 in the no-baseline client and contrast the baseline, then
close the tested differences through existing runtime and renderer seams.
