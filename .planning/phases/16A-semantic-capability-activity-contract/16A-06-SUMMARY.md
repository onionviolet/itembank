# 16A-06 summary: ten purposes over eight shipped forms, and a declaration proven not to be an authority

**Executed 2026-08-28.** Darwin arm64, Python 3.14.6. Plan
`16A-06-PLAN.md`, three tasks, all complete.

Output: one `## ACTIVITIES` registry, five closed vocabularies, eleven lint
codes, one real fallback surface, and no ninth item type.

---

## 1. The eleven `ACTIVITY_COLUMNS` and the five closed vocabularies

```python
ACTIVITY_COLUMNS = ("item", "purpose", "demand", "objective", "stimulus",
                    "response_schema", "retry", "feedback", "evidence",
                    "a11y_equivalent", "static_fallback")

ACTIVITY_PURPOSES = ("prediction", "noticing", "retrieval", "explanation",
                     "comparison", "diagnosis", "practice", "transfer",
                     "reflection", "formal_assessment")

ACTIVITY_RETRY = ("none", "unlimited", "until_correct", "mode_controlled")

ACTIVITY_FEEDBACK = ("immediate", "after_commitment", "staged",
                     "withheld_until_submit", "non_evaluative")

ACTIVITY_EVIDENCE_STATES = ("not_recorded", "activity_trace",
                            "scored_by_runtime", "pending_human_mark")

RESPONSE_FORMS = ("mc", "multi", "table", "dnd", "build", "short", "check",
                  "visual")
```

The column order is this plan's own choice: `item` prepended as the key, then
ACTIVITY-01's ten fields in the order the requirement's own sentence names
them. Recorded here so a later phase finds the choice rather than assuming it
was handed down.

**Cognitive demand gets no tuple, deliberately.** Research stream 03 section
4.1's "Useful demand range" column gives per-purpose verb ranges
(`anticipate, estimate, hypothesize, commit a model` for prediction;
`recall, recognize, reconstruct, produce` for retrieval) rather than an enum.
Fixing a five-member Bloom-shaped tuple here would be Phase 16A inventing a
taxonomy the research deliberately left open. The `demand` column is free prose
validated as non-empty, which is what can honestly be checked. A comment in
`model.py` says so where the tuple would have gone.

**`ACTIVITY_EVIDENCE_STATES` names what `evidence.py` can produce.** Research
stream 03's evidence-status column carries `Mixed, deterministic for fixed
matches, pending for justification` and `Stronger evidence, but claim limited
to sampled contexts`. Those describe an inference a reader draws, not a state
the store records. Adopting them would have put members in a closed tuple that
nothing can ever reach, and a state nothing can reach is a lie. The four chosen
map onto what the store actually does: no event, a non-scoring trace event, a
scored response event, and a response awaiting a human mark.

## 2. `activity.empty_block`'s severity, and which shipped code was checked

**Warning.** The shipped code checked is `terms.empty_block`, which the plan
names as the precedent and which is appended to `warnings` in the shipped
`lint`. `activity.unsupported_response_form` is the only other warning of the
eleven; the remaining nine are errors.

`activity.unsupported_response_form` is a warning for a different and stated
reason: ACTIVITY-01's Degraded clause makes falling back the **declared
behavior**, so an unsupported form is a documented state and not a defect. The
unit check asserts the split rather than the codes alone, so flipping a
severity fails by name.

## 3. Whether the shipped objective-namespace rule exposed a reusable helper

**It did not.** `model.py`'s `item.objective_unnamespaced` check is an inline
two-line test (`objective = q.get("objective") or ""` then
`if objective and ":" not in objective:`) inside `lint`'s per-item loop, with
no extracted helper. Following Task 2 step 2's own instruction for that branch,
**nothing was extracted and no activity-specific objective check was added.**

Recorded so a later plan does not assume one exists. An activity row's
`objective` column is parsed, carried, and asserted non-empty by the tracer's
completeness leg, and is not namespace-checked. If a later phase wants that
check, it should extract the shipped rule into one helper and call it from both
places rather than writing a second copy.

## 4. The ten purpose-to-response-form pairings, and their matrix rows

Each pairing is drawn from research stream 03 section 4.1's "Suitable response
families" column for that purpose. All eight shipped forms appear, which is the
demonstration ACTIVITY-01 asks for.

| Item | Purpose | Form | Matrix row's suitable families, quoted in part |
|---|---|---|---|
| q1 | prediction | `mc` | "choice plus reason, numeric estimate, sketch, rank, forecast" |
| q2 | noticing | `visual` | "select span/region, mark feature, table observation, describe change" |
| q3 | retrieval | `short` | "free recall, cue completion, selected response, label" |
| q4 | explanation | `short` | "short/extended prose, equation derivation, proof" |
| q5 | comparison | `table` | "matrix, paired annotation, sorting, selected claim plus evidence" |
| q6 | diagnosis | `check` | "error highlight, fault tree, next-test choice, corrected step, debugging action" |
| q7 | practice | `build` | "any construct-aligned response with scaffolding and variation" |
| q8 | transfer | `dnd` | "novel scenario, case, design, simulation decision, source synthesis" |
| q9 | reflection | `short` | "journal, confidence plus reason, error log, study plan" |
| q10 | formal_assessment | `multi` | "blueprint-constrained selected, constructed, performance, oral, practical, or mixed" |

The eleventh row, q11, declares `response_schema` as `oral_explanation`, which
research stream 03 lists under explanation's suitable families and which is not
one of the eight shipped forms. Its item is a `short` item, referenced by a
`> [!CHECK: q11]` block in the lesson body, so the fallback reaches the render
path through the shipped inline-check slot rather than through a new block.

Its declared static fallback, verbatim:

```
Say your answer out loud, then compare it to the worked explanation below.
```

`python itembank.py lint` on the generated bank: `11 items, 0 errors, 17
warnings`, with exactly one activity finding:

```
warn   BANK: item q11 declares response form oral_explanation, which is not one of the eight shipped forms; the activity falls back to its declared static equivalent
```

The seventeen warnings are the unminted-id warnings every fixture bank carries
plus the shipped `item.no_normalizer` note on each `short` and `visual` item.

## 5. The declaration-is-not-authority result

**Both halves pass.** `scenario_unsupported_response_form` rewrites every
`## ACTIVITIES` row's `feedback` cell to `withheld_until_submit` and every
`evidence` cell to `not_recorded`, confirms the rewrite took (the set of
feedback values across all eleven rows is exactly
`{"withheld_until_submit"}`), and then asserts two things:

- The rendered page is **byte identical** to the original render.
- `runtime.public_item` returns an **equal dict** for every one of the eleven
  items, compared item by item across the two copies.

A declared policy that moved either output would be a second authority over
what a learner sees. Nothing in this plan reads the `feedback`, `retry`, or
`evidence` column outside `model.lint`'s membership check, and the only column
any renderer reads is `static_fallback`, and only through
`capabilities.activity_fallback`, which returns the empty string for every one
of the eight shipped forms.

The no-ninth-type claim is asserted in the same scenario: the set of `type`
values across all eleven parsed items is a subset of `model.RESPONSE_FORMS`.

## 6. The tracer's final summary line, verbatim

```
scenario thin_slice: pass
scenario additivity_golden_parse: pass
scenario fourteen_roles: pass
scenario unknown_semantics: pass
scenario example_order: pass
scenario capability_profiles: pass
scenario unavailable_renderer: pass
scenario media_metadata: pass
scenario activity_declarations: pass
scenario unsupported_response_form: pass
TRACER: 10 passed, 0 skipped, 0 failed
```

Exit 0. `16A-VALIDATION.md`'s expected count after 16A-06 is 10.

`tests/activity_declaration_check.py` prints `activity declarations ok` and
exits 0.

## 7. The additivity proof, re-verified

```
fixtures/lesson_golden_phase3_parse.json 4078e7532ed33b341a6d551791d8ecc72175e1e479c63420b56db2b635a8e5aa
fixtures/lesson_golden_phase3_content.txt 800edb4cc180cda67885dc558e6784e713e9d636f9ebf8336919c1df93318a3c
fixtures/lesson_bank.md e34d5c9d3c2c16115257d5b1640f8aa9386e037ff6a15bc1eb6480d82c64398e
```

Unchanged. `check_absent_section` additionally asserts that passing activity
data for a bank that declares none produces lint output identical to passing
none, so the addition is additive at the call site and not only at the parser.

`python itembank.py guard .` reports `0 offending files`.
`grep -c '_preamble_section(head, "ACTIVITIES")' model.py` reports `1`.
`grep -cE "^import model|^from model" capabilities.py` reports `0`, so the
`model` import inside `activity_fallback` stayed function-local.
`git diff -U0 | grep '^+' | grep -c "—"` returns `0`.

**Full suite.** The same three pre-existing red files and no others:
`tests/day_roundtrip.py`, `tests/phase_062_audit.py`, and
`tests/retention_ui_roundtrip.py`.

## 8. Which truth was verified by which command

| Truth | Command | Result |
|---|---|---|
| ten fields, five vocabularies, one boundary rule | `check_vocabularies`, `grep -c '_preamble_section(head, "ACTIVITIES")'` | all six tuples exact; `1` |
| no ninth item type | `scenario_unsupported_response_form`'s type leg | every item type is in `RESPONSE_FORMS` |
| a declaration is not an authority | the same scenario's authority leg | page byte identical; eleven equal `public_item` dicts |
| adjacency probe: two rows, one item | `check_duplicate_item` | first registration wins, no merge, `activity.duplicate_item` fires |
| empty probe: absent vs empty section | `check_absent_section`, `check_empty_block` | `None`; `empty` True with the warning and no error |
| ordering probe: document order never sorted | `check_document_order` and the tracer's order leg | `['q9', 'q1']`; order matches the fixture's own constant |
| idempotency probe and concurrency backstop | `check_idempotent_and_pure` | two equal dicts, no file written |
| a malformed registry never raises | `check_malformed_never_raises` | four shapes parse and lint without an exception |
| each of eleven codes fires on its own row | `check_every_code_fires` | nine one-code cases, plus the two warnings |
| an unsupported form falls back on a real surface | `scenario_unsupported_response_form` | the declared text is in the page with `activities` and absent without |

## 9. Deviations from the plan, with reasons

Four.

**D1. `surfaces/cli.py`, `surfaces/daemon.py`, `schemas/lint_error.schema.json`,
`tests/protocol_roundtrip.py`, and `model.SPEC` were edited beyond the plan's
`files_modified` list.** All five are the same class as 16A-05's D1 through D3
and land for the same reasons: `cmd_lint` and the daemon lesson route are the
two call sites that must pass `parse_activities` for the checks and the
fallback to run at all; `LINT_PREFIXES` is the declared namespace list a new
prefix must join; the schema's `code` enum is asserted to cover `LINT_CODES`;
and the SPEC lint table names every published code.

**D2. No activity-specific objective-namespace check was added.** Recorded in
full in section 3 above. This follows Task 2 step 2's own branch for the case
where the shipped rule exposes no reusable helper, which is the case.

**D3. `_row` and `GOOD_CELLS` in `tests/activity_declaration_check.py` build
every test bank from one well-formed row with exactly one cell broken.** The
plan says "one temporary bank per lint code producing exactly that code and no
other activity code". Writing eleven separate literal rows would have made each
case's difference from a valid row invisible, and would have made a shared
mistake in all eleven silently pass. Building from one constant and overriding
one cell by column name means a finding can only come from the thing that was
broken, and the assertion checks the whole finding list rather than membership.

**D4. `fixtures/lesson_capability_corpus.ACTIVITY_SET_ORDER`,
`UNSUPPORTED_ACTIVITY_ITEM`, `UNSUPPORTED_ACTIVITY_FORM`, and
`UNSUPPORTED_ACTIVITY_FALLBACK` are module-level constants the tracer reads.**
Task 3 step 2 asks for the expected order to be "built in the fixture module and
exported as a module-level constant, so the test compares against the fixture's
own declared order rather than against a copy that can drift". The other three
constants exist for the same reason: the fallback string appears in the bank
text, in the tracer's assertion, and in this summary, and a literal copy in the
test would drift the first time the fixture's wording changed.

## 10. Open items recorded rather than filled

- **The `objective` column is not namespace-checked.** Section 3. A later phase
  that wants it should extract the shipped `item.objective_unnamespaced` rule
  into one helper and call it from both places.
- **`.capability-static` still has no CSS rule.** The activity fallback reuses
  the class plan 16A-04 introduced; Phase 17A owns appearance.
- **The `stimulus` column is free prose and is not resolved against anything.**
  A row may name a stimulus that does not exist, and nothing notices. Linking it
  to the `## MEDIA` registry or to a `## SOURCES` row is a real option and is
  recorded here rather than done, because ACTIVITY-01 asks for a declaration and
  not for a resolution.
- **ACTIVITY-01's concurrency probe is answered as a backstop, not a test.**
  `parse_activities` is a pure read with no cache and no durable write, so an
  interruption or a parallel run has no durable failure mode to check.
  `check_idempotent_and_pure` asserts the two facts that make that true: two
  calls return equal dicts, and the directory is unchanged afterward.
