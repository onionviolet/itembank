# Current question forms and scoring audit

Date: 2026-09-25. Source checkout: `ee23d88`, with concurrent work possible.
Scope: the live parser, public item and evidence schemas, sole scorer,
selected rendering branches, and focused synthetic tests. This is a source
audit, not installed-app, accessibility, or human acceptance.

## Findings

**F1. Eight assessment response forms exist, including executable code checks.**
The registry and public schema agree on `mc`, `multi`, `table`, `dnd`, `build`,
`short`, `check`, and `visual`. A ninth form is warranted only when existing
response structure or scoring semantics cannot express the task safely.
Evidence: `model.py:2672-2679`, `schemas/item.schema.json:28-39`.

**F2. Cloze exists for lesson keys, print drills, and Anki export, but not as a
native automatically checked text-response assessment form.** A blank in a
stem can be answered through `short`, but it remains pending review. That is
different from a checker accepting specified words, equivalent numbers, or
several independently scored blanks.

**F3. All settled machine verdicts are Boolean.** The response score is
`true`, `false`, or `null`. Per-selection, per-case, and per-rubric feedback do
not imply fractional credit. Evidence: `runtime.py:306-326`,
`runtime.py:1901-1910`, `schemas/response.schema.json:291-296,818-850`.

**F4. One authoring warning is wrong for a mixed visual/code bank.** When any
`check` item is present, lint checks every type against `NORMALIZERS`. It
incorrectly warns that `visual` will be pending, even though visuals have a
separate dispatch inside the sole scorer. This was reproduced with the
synthetic visual and check fixtures. It is a warning defect, not evidence that
visual scoring fails. Evidence: `model.py:3906-3912`, `runtime.py:275-279,306-326`.

## Current capability matrix

| Form | Authored and learner response | Actual checker | Limits and evidence |
|---|---|---|---|
| `mc` | Option letters and one correct letter. Learner submits a string. | Trims and uppercases the string, then compares the canonical letter. A one-element list is also accepted by the scorer. | Lint requires at least three options, so an ordinary two-option true/false item is not lint-clean. `model.py:109-129,3800-3811`, `runtime.py:49-52,178-181,234-235`. |
| `multi` | Several options with a fixed selection count. Learner submits an array of letters. | Trims and uppercases selections, sorts them, and compares the full collection. | All required choices and no extra choices must match. Duplicate selections are not silently deduplicated. Partial selection feedback is disclosure, not partial credit. `model.py:115-127`, `runtime.py:184-186,238-239,1901-1939`. |
| `table` | Named categories and ordered rows. Learner assigns one category to every row. | Compares the complete row-to-category assignment. | Useful for classification, matching-style questions, and multiple true/false statements. It does not enforce a one-to-one matching rule or score rows fractionally. Category text is exact. `model.py:131-143`, `runtime.py:53-56,189-195,242-244`. |
| `dnd` | Named buckets and items. It uses the same response structure as `table`. | Same full-assignment checker as `table`. | The distinction is interaction and display order, not a different scoring capability. It is not arbitrary free-position dragging. `model.py:131-143,2279-2283`, `runtime.py:189-195,242-244`. |
| `build` | Author supplies steps in the correct order. Learner returns an ordered array of step texts. | Exact comparison of the complete sequence. | Supports procedure or proof-step ordering. Only one complete order is encoded. There is no alternate valid ordering or dependency-graph checker. The sampled renderer requires all steps. `model.py:145-150,2273-2277`, `runtime.py:57-62,198-199,247-248`, `surfaces/quiz_page.py:1599-1638`. |
| `short` | Free response with a model answer and rubric. Plain or LaTeX input. | No automatic correctness comparison. The response is pending until marking. | Supports explanations, proofs, interpretations, and reflective responses. It does not supply exact-word, numeric, unit, spelling, or algebraic-equivalence grading. The public schema declares minimum length two, so it is not an ideal single-character blank input. `model.py:181-192,3696-3701,3857-3874`, `runtime.py:63-67,280-283,318-320`. |
| `check` | Source string, language, cases, optional starter, optional harness, match policy, and optional numeric tolerance. | Runner outcomes become a canonical per-case vector. The sole scorer compares it with an all-pass vector. Any timed-out case makes the response pending. | This is already interpreter-based answer checking. The source-response editor and execution/result contract are distinct from the central verdict. Hidden test inputs and expected output are absent from the public pre-answer item. Execution details are audited in the companion execution report. `model.py:152-179`, `runtime.py:68-91,202-219,251-259,306-326`, `schemas/item.schema.json:542-624`. |
| `visual` | A declarative scene and semantic response. Current families are plot, number line, hotspot, timeline, diagram connection, and trace path. | Canonicalizes and validates semantic state, then compares against accepted states and authored tolerances. | Exact rational coordinates avoid pixel or browser-float scoring. Hotspot and diagram families compare IDs. Timeline and trace use bounded coordinates. No partial credit. `runtime.py:329-358,887-936`, `runtime.py:1159-1164`. |

These are response forms, not eight pedagogies. The activity metadata already
separates prediction, noticing, retrieval, explanation, comparison, diagnosis,
practice, transfer, reflection, and formal assessment. It also separates
feedback, retry, evidence, accessible equivalent, and static fallback.
Evidence: `model.py:2636-2679`. The binding research contract explicitly asks
for learning moment, objective verb, cognitive demand, subject, response form,
feedback, authenticity, accessibility, and scoring authority, rather than more
widgets alone: `.planning/SOURCE-TO-COURSE.md:290-295`.

## Fill-in-the-blank and cloze boundary

| Existing path | Verified behavior | What it does not establish |
|---|---|---|
| Lesson `[!KEY]` containing `{{text}}` | Shows the enclosed answer in the normal lesson. Drill print replaces the marker with `____` and collects answers separately. | No native typed-response field, accepted-answers policy, or runtime correctness event for each blank. `surfaces/lesson.py:1045-1058,1086-1124`. |
| Lesson key export | Converts `{{text}}` to Anki `{{c1::text}}`, with sequential numbering. Explicit `{{n::text}}` keeps its number. | Exporting a cloze does not add an Itembank assessment checker. `surfaces/anki.py:27-41,69-83`. |
| Generic bank export with `--format cloze` | The existing surface test checks Anki Cloze notetype output and `{{c1::` syntax. | This is an export representation, not an extra member of the public item-type schema. `tests/surface_roundtrip.py:181-188`. |
| `short` stem with a visible blank | Can collect text, subject to the short-input contract. | No automatic accepted text, aliases, per-blank normalization, or partial credit. `runtime.py:63-67,280-283,318-320`. |

The bounded capability gap is a typed-answer contract. A candidate contract
would need stable blank IDs, authored accepted responses, explicit
case/whitespace/Unicode rules, separate display and canonical forms, and a
declared policy for multiple blanks. Numeric tolerance, units, and symbolic
equivalence need their own checker semantics. They should not be inferred from
the fact that a text box can hold those strings.

LaTeX is specifically presentation and input. The live spec states that it
changes the answer control and preserves source while the response stays
pending. The focused test asserts that `(x+1)^2` receives `None`.
Evidence: `model.py:2285-2301`, `tests/latex_input_roundtrip.py:35-45`.

## Normalization and authority

The generic entry point first attempts JSON decoding for a string and otherwise
strips outer whitespace. Each response form then decides its canonical form.
That does not provide a general linguistic normalizer. MC letters get case and
whitespace handling, while row category strings and ordered step texts compare
exactly. Evidence: `runtime.py:159-199`.

The visual checker supports multiple accepted semantic states and rational
coordinate tolerances. That does not establish a standalone numeric-answer or
computer-algebra checker. Likewise, numeric tolerance inside a code harness is
not a numeric text-entry question format.

`short` intentionally lacks a machine key. The separate human mark event has a
Boolean verdict and individual rubric-point pass values. A model proposal is
pending advice, not a settled score. Evidence:
`schemas/response.schema.json:818-863,1051-1053`. This agrees with
`.planning/SOURCE-TO-COURSE.md:110-114`, which preserves runtime authority and
human or human-approved marking.

## Classification of gaps and defect

| ID | Classification | Finding | Bounded next step |
|---|---|---|---|
| G1 | Missing capability | Native automatically checked text blanks are absent from the parser/type/schema/scoring registry. | Prototype a typed-response contract with explicit accepted-answer and normalization policies. Preserve manual `short` marking. |
| G2 | Missing capability | Standalone numeric/unit and symbolic-equivalence checkers are absent from the inspected form contracts. | Define what counts as equivalent before selecting a checker. Distinguish an algebraic answer from an explanation or proof. |
| G3 | Current contract restriction | Two-option true/false fails MC lint. Multi-row binary classification is possible through `table`. | Decide whether two-option MC is an allowed authored specialization before changing lint. |
| G4 | Current contract restriction | Machine response verdicts and settled human marks are Boolean. | Design evidence and aggregation changes before promising per-blank, per-row, per-test, or rubric-weighted credit. |
| B1 | Reproduced authoring bug | Mixed visual/check banks falsely warn that visual responses land pending. | Have lint consult supported scoring capability, including the visual dispatch, rather than only the normalizer registry. |

Other possible response forms, such as file submissions, SQL editors, circuit
builders, audio, handwriting, and external artifact checking, are not claimed
absent from every repository subsystem. They were outside this bounded parser
and scorer inspection. Their suitability belongs in the wider question and
execution research.

## Verification

Every command below completed with exit code 0 in this source checkout.

| Command | Observed result |
|---|---|
| `python3 tests/scoring_roundtrip.py` | `scoring contract: ok (6 items, one scorer)`. Covers the legacy fixture types, malformed assignments, offline canonical-key parity, served key exclusion, and the one-scorer invariant. It does not alone cover all eight forms. |
| `python3 tests/visual_roundtrip.py` | Pass. Key-free public contract, exact scalar grammar, accepted decimal aliases, discrete and tolerance boundaries, invalid-state refusals, and served submission/evidence flow. |
| `python3 tests/visual_authoring_roundtrip.py` | Pass. Visual grammar, field-addressed lint, public schema, and a consumer using the contract without renderer implementation. |
| `python3 tests/latex_input_roundtrip.py` | Pass. LaTeX metadata, pending authority, input fallback, and local preview contract. |
| `python3 tests/surface_roundtrip.py` | `study and export surfaces + Phase 4 question hierarchy: ok`. Includes basic and cloze export checks. |

Additional synthetic reproduction for B1:

```python
from pathlib import Path
import model, runtime

visual = model.parse_bank(Path("fixtures/visual_bank.md").read_text())[0]
check = model.parse_bank(Path("fixtures/check_bank.md").read_text())[0]
check["id"] = "q99"
errors, warnings = model.lint([visual, check])
print([str(w) for w in warnings if w.code == "item.no_normalizer"])
print(runtime.score_response(visual, {"kind": "point", "x": "2", "y": "3"}))
```

Observed output was a warning that visual responses land pending, followed by
`True`. The probe changed only in-memory synthetic item dictionaries.

Inspection limits: large modules were sampled by symbol and relevant windows.
No whole-file read of `model.py`, `runtime.py`, or quiz/lesson renderers was
performed. Advanced visual families were confirmed in live dispatch and
contracts, but their dedicated hotspot/diagram/timeline/trace test suites were
not rerun here. No browser or installed package was exercised. Code execution
tests and full quick preflight belong to the coordinating audit and are not
claimed by this report. No application code, real banks, or commits changed.
