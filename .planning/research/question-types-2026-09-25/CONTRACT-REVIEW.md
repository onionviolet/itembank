# Native typed-answer contract review

Date: 2026-09-26. Scope: independent read-only contract and readiness review.
The only write in this packet is this report. Large modules were inspected by
symbol and narrow windows. Concurrent edits in `runtime.py` and
`surfaces/session.py` were left untouched.

## Recommendation

Adopt one additive `fill` response form with stable named fields. Do not split
text and numeric answers into top-level item types. A passage can then mix one
or several text and numeric fields without inventing a composite type, while
renderers, sessions, evidence, and exports gain one response shape:

```text
[TYPE: fill]
[FIELDS: [{"id":"term","label":"Term","kind":"text",...},
          {"id":"dose","label":"Dose","kind":"number",...}]]
```

The learner response is exactly `{field_id: original_string}`. The first
vertical slice should render labeled fields after the stem. Inline placement
inside prose is a separate presentation grammar and should not overload the
existing lesson `{{cloze}}` syntax.

Use closed per-field objects:

- Text: `id`, `label`, `kind: "text"`, nonempty `accepted`,
  `case_sensitive` (default `true`), and `whitespace` (`exact`, `trim`, or
  `collapse`, default `exact`). Normalize only to Unicode NFC. A
  case-insensitive field uses Unicode `casefold`, then NFC again. Punctuation,
  accents, compatibility characters, and synonyms remain significant unless
  the author lists another accepted form.
- Number: `id`, `label`, `kind: "number"`, one private `answer`, and explicit
  nonnegative `atol` and `rtol` with zero defaults. Define the boundary formula
  in the contract. Recommended: `abs(given - answer) <= atol + rtol *
  abs(answer)`, inclusive.
- Optional units: `unit` names the base unit and `units` maps each authored
  alias to a positive scale relative to that base. Require the base alias in
  the map with scale `1`. A response with units must carry one declared suffix.
  Do not infer dimensions, prefixes, plurals, affine conversions, or global
  aliases. Unit matching is case-sensitive unless a later explicit field
  policy changes it.

Parse decimal, fraction, and scientific notation into an exact bounded
`Fraction` or equivalent Decimal-backed rational. Reject `NaN`, infinity, a
zero denominator, multiple slashes, trailing junk, and values outside declared
digit and exponent limits before arithmetic. Split a quantity as one bounded
number token followed by one exact authored unit suffix. This avoids float
rounding and ambiguous unit guessing. The specification must publish the
maximum response bytes, field count, digits, exponent magnitude, and unit alias
length.

Scoring stays Boolean and all-or-nothing. Per-field comparison results may
later support practice feedback, but they are disclosure data, not partial
credit, and must remain absent in active exam and diagnostic responses.

## Material contract corrections

**C1. `fill` needs dedicated runtime scoring.** `runtime.canonical_key()`
cannot represent accepted text alternatives or a tolerance interval. Add a
`fill` branch in `score_response()` before the ordinary key comparison, like
the existing `visual` branch. `canonical_response()` should still produce a
stable learner-response canonical form for deduplication. It must not decide
correctness. Do not add `fill` to `NORMALIZERS` while leaving it absent from
`KEYS`, because that silently yields a pending score. Replace the lint test
against `NORMALIZERS` with a registry of actually auto-scored forms. This also
closes the audit's existing false warning for `visual`.

**C2. Empty and malformed submissions need refusal, not a wrong mark.** A
valid response is an object with exactly the authored field ids, every value a
string, and every value nonempty after that field's whitespace policy. Missing,
extra, non-string, oversized, or empty fields should return a named submission
refusal before `teaching_transition()` and before evidence append. Reuse one
runtime-owned response validator from CLI, form, and JSON paths. The browser
may disable Submit, but browser checks are not authority. If
`canonical_response()` sees an invalid fill response outside a submission
adapter, it should return the existing empty canonical sentinel so it cannot
unlock hints or count as genuine.

**C3. Malformed authoring must survive parsing long enough to lint.** Follow
the `visual_raw` pattern. Store `fields_raw` and the parsed value separately.
A missing marker, malformed JSON, non-array value, or empty array must produce
a field-addressed lint error, not make `parse_question()` return `None` and
silently drop the item. Reject unknown keys, duplicate ids, invalid ids,
empty labels, unknown kinds, empty or non-string accepted forms, accepted
forms that collide after normalization, invalid number literals, negative or
non-finite tolerances, incomplete unit declarations, duplicate unit aliases,
and nonpositive or invalid scales.

**C4. Private rules must never enter the public item.** `public_item()` should
construct a fresh field projection containing only id, label, kind, visible
text policy, notation help, whether a unit is required, and allowed unit names.
It must omit `accepted`, `answer`, `atol`, `rtol`, and unit scales recursively.
Use `additionalProperties: false` in the public JSON schema and add recursive
leak tests. The raw `[FIELDS:]` object must never be copied into the public
projection.

**C5. Fingerprints must cover every grading rule.** Add `[FIELDS:]` to
`model.MARKERS` so stem termination and ID/hash insertion stay synchronized.
`content_fingerprint()` must include field order, stable ids, labels, kinds,
accepted forms, text policies, expected number, tolerances, base unit, aliases,
and scales through canonical sorted JSON. Changing any of these changes the
content hash while preserving the opaque item id. Evidence retains the raw
response map, whose stable field ids preserve field identity across display
reordering.

## End-to-end choke points

| Area | Required integration |
|---|---|
| Parser and author contract | `model.MARKERS`, `parse_question`, `_json_or_none`, `content_fingerprint`, `RESPONSE_FORMS`, `lint`, `SPEC`, and the no-normalizer diagnostic. Add a synthetic fixture only. |
| Runtime authority | `runtime.public_item`, fill authoring and response validators, `canonical_response`, `score_response`, `answer_text`, `response_text`, `explain_payload`, and `glossable`. `glossable` must treat every accepted text form and expected numeric answer as keyed material or pre-answer glossary/static fallback text can disclose the answer. |
| Public and durable schemas | Add a closed `fill_item` branch to `schemas/item.schema.json`; add `fill` to the response-event enum in `schemas/response.schema.json` and the session response enum in `schemas/session.schema.json`. Review `schemas/selection.schema.json`, subject-profile defaults in `subjects.py` and `schemas/settings.schema.json`, and any authoring request schema deliberately rather than leaving the new type unreachable. |
| Served UI and no-script path | Add field controls and response collection in both JS dispatch tables in `surfaces/quiz_page.py`, plus `_form_controls` and `surfaces.daemon._form_answer`. Use text inputs, not HTML number inputs, because fractions and scientific notation are valid. Labels, help, unit choices, keyboard order, prefill, focus, and draft restore must use stable field ids. |
| Session and API | Validate the exact map before `runtime.teaching_transition` in `surfaces/session.do_action`. `/api/submit`, CLI `submit`, and the legacy form wrapper must receive the same refusal. Ensure silent-mode recursive projection withholds any future per-field verdicts. |
| Evidence and reports | `evidence.response_event` can store the raw object after the enum update. Add a `fill` branch to `response_text` and attempt rendering so a dict is readable rather than shown as an empty selection. Confirm resume, dedupe, retraction, reports, and auto-attempt totals. |
| Selection and course profiles | Add `fill` to `selection.select_items` type-count validation, course mock-form discovery in `surfaces/daemon.py`, the default subject profiles that should permit it, and their schemas/tests. Keep it out of profiles only through an explicit capability decision. |
| Static build | In `runtime.page_item`, mark offline `fill` as `served_required` before adding any key or explanation. Add an offline renderer with the same clear served-session refusal used by `visual` and `check`. `cmd_build` should report that fill checking is unavailable offline. Do not implement a JavaScript copy of text, numeric, or unit scoring. |
| Study and export | Study can reveal a labeled accepted-answer summary through `answer_text`. Generic Anki basic/cloze export must not silently flatten several fields into one misleading blank. Either define a lossless per-field card mapping or skip/refuse `fill` with a named diagnostic. GIFT should explicitly refuse until a tested mapping preserves normalization, tolerance, unit, and multi-field semantics. |
| Other closed registries | Audit `capabilities.py`, activity declaration checks, CLI help/mix text, `surfaces/migrate.py`, import paths, and tests that assert the old eight-form tuple. Do not broaden migration or import behavior without a defined external mapping. |

## Minimum acceptance tests

1. Parser/lint tests cover one and several fields, mixed kinds, every malformed
   shape above, marker/hash insertion, deterministic fingerprints, and drift
   after every private scoring-rule change.
2. Runtime tests cover NFC equivalence without accent or compatibility
   folding, casefold behavior, all whitespace modes, exact variants, tolerance
   boundaries, expected zero, negative values, fractions, scientific notation,
   unit conversion, unknown or missing units, and resource bounds.
3. Protocol tests validate the public schema, recursively search every
   pre-answer payload and static build for private keys and values, submit a
   field map through CLI/API/no-script routes, and prove malformed or empty
   maps create no response event.
4. Surface tests verify keyboard labels, raw-value preservation, failure
   prefill, local draft restore by field id, served scoring, silent-mode
   withholding, post-release answer display, and explicit offline refusal.
5. Evidence and export tests validate response/session schemas, readable
   attempt output, dedupe of equivalent normalized entries, distinct retries,
   report totals, and named Anki/GIFT fallback behavior.

This contract is additive, keeps one markdown parser and one runtime scorer,
matches the user's typed-blank and exam-fidelity direction, and leaves symbolic
math, inline cloze layout, affine units, and partial credit for separately
accepted capabilities.

## Implementation decision

The root implementation uses `kind: "numeric"`, trim as the text default,
and `max(atol, rtol*abs(answer))` for the inclusive tolerance bound.
These resolve the review's suggested alternatives explicitly. The public
field announces its text policy, and the spec states the numeric formula.
The examples above are review sketches, not parser examples to copy.
