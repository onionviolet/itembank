# 16A-09 summary: eighteen attacks, eighteen refusals, and two findings recorded rather than assumed away

**Executed 2026-08-28.** Darwin arm64, Python 3.14.6. Plan
`16A-09-PLAN.md`, three tasks, all complete.

Output: three scripted attackers, two probes, four attacks on Phase 16A's own
new grammar, zero mocks, and two honest findings about the shipped gate that
this suite surfaced rather than hid.

---

## 1. The final line, verbatim

```
ADVERSARIAL: 18 attempted, 18 refused, 0 succeeded
```

Exit 0. `tests/capability_stress_corpus_tracer.py` reports
`TRACER: 14 passed, 0 skipped, 0 failed`, which is
`16A-VALIDATION.md`'s expected count after 16A-09.

The eighteen, in the order `main()` runs them:

| # | Attack | Gate that refused it |
|---|---|---|
| 1 | `agent_leak_key` | `runtime.public_item` |
| 2 | `agent_invent_score` | `evidence.marks_by_event` reports no mark |
| 3 | `agent_auto_grade` | `evidence.mark_event`'s `marker != "human"` |
| 4 | `agent_edit_frozen` | `surfaces/session.py`'s completed-session refusal |
| 5 | `note_leak_key` | `runtime.public_item`, byte identical before and after |
| 6 | `note_invent_score` | no reader consults the note; the log is unchanged |
| 7 | `note_auto_grade` | `runtime.score_response` returns `None`; no mark exists |
| 8 | `note_edit_frozen` | `evidence.render_attempt_md` is byte identical |
| 9 | `import_leak_key` | `runtime.public_item` |
| 10 | `import_invent_score` | no mark without a human marker |
| 11 | `import_auto_grade` | `evidence.mark_event`, the one mark constructor |
| 12 | `import_edit_frozen` | D-11 structurally, plus the append-only log |
| 13 | `boundary_public_item` | `runtime.public_item` at three points |
| 14 | `precision_pending_mark` | the marker gate firing before verdict coercion |
| 15 | `16a_excerpt_leak` | `runtime.glossable` classifies it as keyed |
| 16 | `16a_media_alt_leak` | `runtime.glossable` |
| 17 | `16a_activity_fallback_leak` | `runtime.glossable` |
| 18 | `16a_composed_glossary_leak` | `runtime.glossable`, plus a no-second-detector grep |

## 2. No mocks, proven by grep

```
$ grep -cE "class Mock|def fake_|monkeypatch|setattr\((runtime|evidence)" tests/assessment_authority_adversarial.py
0
$ grep -cE "^import (pytest|unittest)|^from (pytest|unittest)" tests/assessment_authority_adversarial.py
0
```

The module docstring states the rule without spelling the grep patterns, so
the count is genuinely zero rather than counting the paragraph that forbids
them. The suite imports `runtime`, `evidence`, `model`, `capabilities`,
`surfaces.session`, and `surfaces.lesson` directly and calls
`runtime.public_item`, `runtime.score_response`, `runtime.glossable`,
`evidence.append_event`, `evidence.mark_event`, `evidence.marks_by_event`, and
`evidence.render_attempt_md` by name.

`build_synthetic_sitting` builds a real sitting through the shipped path:
`session.do_start`, `session.do_next`, `session.do_submit`. It leaves the prose
response **pending on purpose**, because several attacks assert its mark is
still `None` and marking it during setup would make them vacuous.
`_freeze` completes a sitting the way a sitting actually completes: a real
human `mark_event` on the pending response, then one more `do_next`, which is
what releases a sitting parked on a marker's desk.

## 3. The frozen-sitting refusal, side by side

| Source | String |
|---|---|
| `surfaces/session.py:850` (shipped) | `session is already complete` |
| `tests/assessment_authority_adversarial.py`'s `FROZEN_REFUSAL` | `session is already complete` |

Transcribed rather than paraphrased, and asserted with `==` rather than with
`in`, so a rewording of the shipped message fails here instead of passing.

## 4. The two frozen-sitting refusals are different in kind

`attack_import_edit_frozen` asserts both, because only one of them is an
active check.

**Route one is structural.** The session JSON is rewritten on disk to claim
`score: True` on every response and `status: active`, and the rendered attempt
is then byte identical to the render taken before the edit. Phase 1's D-11 made
the session file stop being an input to its own render, so an edited session
file changes nothing a report says. The two SHA-256 digests:

```
before  a8c5... (recomputed each run; the assertion compares them directly)
after   identical
```

The digests are compared in the test rather than pinned as literals, because a
literal would need re-recording every time the fixture's prose changed and the
assertion is about equality, not about a particular value.

**Route two is the append-only store.** An event carrying an existing
`event_id` is appended, and the log afterward carries **both** records for that
id. Correction happens through a recorded retraction, never through an edit.

Testing only the active refusal would have missed that the structural one is
what actually makes the freeze hold.

## 5. The precision probe, and why the ordering test is behavioral

`evidence.mark_event` performs its `marker != "human"` refusal at
`evidence.py:1509` and coerces `verdict = bool(verdict)` at
`evidence.py:1516`, seven lines later. The suite proves that order **without
reading the source**: it calls `mark_event` with `marker="model"` and
`verdict="probably correct"`, a value that is neither `True` nor `False`, and
asserts the raised `ValueError` is the marker's. If coercion ran first, the
non-boolean verdict would have been silently accepted as truthy before the
marker was ever examined.

`runtime.score_response` for the prose item returns `None`, not `False`, so a
not-yet-marked answer stays distinguishable from a wrong one. Asserted twice,
in `attack_note_auto_grade` and in `attack_precision_pending_mark`.

## 6. The boundary probe asserts at three points

`attack_boundary_public_item` calls the real `runtime.public_item` for the same
item before any response exists, after one response exists, and after the
sitting is complete, and applies the same absence check at each. Asserting only
the pre-response case would test the easy side of the threshold.

**What `_assert_no_key` checks, and what it deliberately does not.** The
rationale, discriminator, second-best, trap, and every distractor-analysis line
are checked against the whole serialized payload, so a future field smuggling
one into a nested structure is caught. The correct option's **letter** and its
**text** are not checked that way, because a learner sees every letter and
every option text and a check that refused them would be asserting the item
cannot be displayed. What must be absent is anything naming **which** option is
right: thirteen forbidden top-level field names, plus a completeness check that
the served option set equals the item's full option set, because a payload
returning only the correct option would leak the key by omission.

## 7. Which of the plan's two outcomes the excerpt attack found

Plan Task 3 asked the excerpt attack to state which of two results this
codebase produces. **It is the second one.**

The rendered lesson page **does** contain the quoted rationale. A lesson page
is authored reading material and is not gated on a response, so an author who
quotes their own rationale into an `[!EXCERPT]` has published it, exactly as
they would by typing it into a paragraph. That is not a defect in the excerpt
callout; it is what a lesson page is.

What the attack asserts, and what holds, is the other half: `runtime.public_item`
for the item carries none of it, and `runtime.glossable` classifies the quoted
text as keyed material. That classification is the signal a later phase needs
in order to suppress such an excerpt inside a sitting, and the finding here is
that **the signal exists and nothing consumes it yet**. Recorded in section 10.

## 8. Two findings about the shipped gate, recorded rather than worked around

**F1. `runtime.glossable` is extremely over-strict for multiple-choice items.**
`runtime.canonical_key` for an `mc` item returns the bare correct option
letter, and `glossable` tests whether any keyed fragment appears as a substring
of the collapsed, lowercased definition. For this fixture the key is `B`, so
**any definition containing the letter `b` is refused**:

```
>>> runtime.glossable(qs, {"def": "A chamber is a basin."})
False
>>> runtime.glossable(qs, {"def": "The water rises."})
True
```

This is not a bug the suite introduced and this plan changes no runtime code.
It is a real property of the shipped gate, and it matters here for one concrete
reason: without a benign control term, the glossary attack could not tell a
real catch from the gate refusing everything. The fixture therefore carries a
second, benign term, `slack-water`, whose definition contains no keyed text
**and no letter `b`**, and the attack asserts the leaky term is refused and the
benign one is not. The letter-avoidance is documented in the fixture with its
reason, so a later reader does not take it for style.

The follow-up this deserves is a decision, not a patch: either
`canonical_key`'s single-letter output should not be used as a substring
fragment for `mc` items, or `glossable` should match option letters on a token
boundary. Both are runtime changes and belong to whichever phase next touches
disclosure. Recorded here so plan 16A-10's freeze gate can weigh it.

**F2. `glossable`'s signal has no consumer for the three new mouths.** The
media `alt`, the activity `static_fallback`, and the `[!EXCERPT]` body are all
classified as keyed material by the gate, and nothing reads that classification
before rendering them. The shipped glossary path does consult `glossable`; the
three new surfaces do not, because Phase 16A's plans do not ask them to and
adding a consumer would be inventing runtime enforcement this phase is
explicitly out of scope for. The attacks assert the classification is correct,
which is the precondition for a later phase to act on it.

Neither finding is an attack that succeeded. Both are things the suite learned
by attacking honestly, and both are named here rather than smoothed over.

## 9. The suite fails loudly, proven twice

Both degraded-state proofs the plan asks for were run and then reverted.

**An inverted assertion.** `attack_agent_auto_grade`'s refusal was temporarily
inverted. Output:

```
attack agent_invent_score: refused
FAIL: agent, auto grade: DELIBERATE INVERSION for the degraded-state check; this line is removed immediately after.
```

The run stopped and named the attack.

**An unexpected exception.** A `RuntimeError` was temporarily raised inside the
attack dispatch. Output:

```
FAIL: attack agent_leak_key raised an unexpected RuntimeError: DELIBERATE unexpected exception probe
```

An unexpected exception counts as neither refused nor succeeded and fails the
run by name, because reading it as a refusal would be generous in the wrong
direction.

Both edits were reverted from a backup and the suite re-runs at
`ADVERSARIAL: 18 attempted, 18 refused, 0 succeeded`.

**The with-no-model clause.** ACTIVITY-03's Degraded sentence says formal
sittings run unchanged under runtime authority with no model. Every gate this
suite attacks is a pure function of the bank, the session, and the log; none
consults a model backend, and the suite imports no adapter. The refusals are
therefore identical with any model configuration absent, which the suite
demonstrates by never reaching for one.

## 10. Which truth was verified by which command

| Truth | Command | Result |
|---|---|---|
| twelve attacks from three attackers, all refused | `python tests/assessment_authority_adversarial.py` | `18 attempted, 18 refused, 0 succeeded` |
| no mock anywhere | the two greps in section 2 | `0` and `0` |
| the boundary holds on both sides and at the threshold | `attack_boundary_public_item` | three assertions, all clean |
| pending is not False and is uncoercible | `attack_precision_pending_mark` | `None`; the marker `ValueError` fires first |
| a frozen sitting stays frozen through both routes | `attack_import_edit_frozen` | identical render; both records in the log |
| 16A's four new mouths are classified as keyed | four `attack_16a_*` | all four refused |
| no second leak detector exists | the regex grep inside `attack_16a_composed_glossary_leak` | no match in `capabilities.py`, `model.py`, `surfaces/lesson.py` |
| the adversarial bank lints clean | `python itembank.py lint` | `2 items, 0 errors, 3 warnings` |
| the tracer records the suite passed | `python tests/capability_stress_corpus_tracer.py` | `TRACER: 14 passed, 0 skipped, 0 failed` |
| additivity holds | the three golden SHA-256 values | unchanged |

`python itembank.py guard .` reports `0 offending files`.
`git diff -U0 | grep '^+' | grep -c "—"` returns `0`.

**The adversarial bank's lint findings**, recorded because the plan asks which
its deliberate hostility produces: `2 items, 0 errors, 3 warnings`. Two
unminted-id warnings and one `activity.unsupported_response_form` warning, from
the `oral_explanation` declaration that makes the static fallback render at all.
**None of the four hostile strings produces a lint finding**, which is itself
worth stating: lint does not detect authored disclosure, and the gate that does
is `runtime.glossable`, which is what the four attacks call.

**Full suite.** The same three pre-existing red files and no others:
`tests/day_roundtrip.py`, `tests/phase_062_audit.py`, and
`tests/retention_ui_roundtrip.py`.

## 11. Deviations from the plan, with reasons

Four.

**D1. The import attacker builds its records through `evidence.response_event`
and `evidence.mark_event` rather than through `surfaces/import_anki.py` or
`surfaces/migrate.py`.** Task 2 step 1 says to "run it through whichever real
import path the repository exposes". The shipped import surfaces import
**cards and legacy attempts**, not assessment evidence claiming verdicts, so
there is no import path that reaches `mark_event` at all. Routing through the
one constructor every writer uses is the stronger assertion in any case: the
refusal is asserted at the single place any import would have to pass through,
and `attack_import_auto_grade`'s docstring records that there is no second
constructor an import could reach instead. Recorded as the plan's own step
instructs ("record in the summary which path was taken").

**D2. The learner note is a plain file beside the bank, and the suite says so.**
Task 1 step 5's own fallback: there is no learner-note store in this repository
yet, and the durable object and its source of truth are Phase 16C's. The
attacks assert that no shipped reader consults the file. The distinction the
test docstring makes explicitly is that this is a stand-in for a store that
does not exist, not a mock of one that does, and the assertion, that nothing
reads learner-authored text from disk, is exactly what must stay true when the
real store lands.

**D3. Each attacker group builds its own sitting.** The plan passes one
`sitting` to everything. Three of the twelve attacks complete and freeze a
sitting, and a frozen sitting cannot then serve the attacks that need a live
one; sharing a single sitting would have made the suite order-dependent in a
way that a later reordering would silently break. Each of the three attacker
groups, the two probes, and the four new-mouth attacks gets a freshly built
sitting, and `_freeze` is called by the attacks that need one.

**D4. The fixture's benign control term avoids the letter `b`.** Finding F1's
consequence, documented at length in section 8 and in the fixture itself. The
alternative was to assert only on the leaky term, which would have passed even
if `glossable` refused every definition it was ever shown.

## 12. Open items and follow-ups

- **F1's follow-up: `canonical_key`'s single-letter `mc` output used as a
  substring fragment.** Named in section 8. A runtime change, out of scope
  here, and one plan 16A-10's freeze gate should see.
- **F2's follow-up: nothing consumes `glossable`'s verdict for the media alt,
  the activity fallback, or the excerpt body.** Also named in section 8. The
  classification is correct and unread.
- **The excerpt callout publishes what it quotes.** Section 7. This is what a
  lesson page is, and the honest mitigation is authoring guidance rather than a
  render gate: an author who does not want a rationale published should not
  quote it into an excerpt. Whether the linter should warn on an excerpt whose
  body matches an item's rationale is a real option and is recorded rather than
  built.
- **The suite runs eighteen attacks and asserts that count in two places**, in
  its own `ATTACKS` tuple and in the tracer's floor. A shrinking suite is a
  silently narrowed one, so both go red rather than quietly reporting fewer.
