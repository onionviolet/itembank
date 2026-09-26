# Question and checker implementation

Date: 2026-09-26. Base: `ee23d88`.
Status: implementation in progress on `codex/question-types-checking-20260926`.

## Authorization and vision

> setup and implement accordingl, atomic commits and consider other advancements and more, reflecting upon user vision and more

This advances the [audit](README.md) into implementation. The earlier audit
remains a historical record. The scope follows the
[code-depth direction](../../USER-VISION.md#2026-09-16-beneficial-depth-levels-and-code-question-audit)
and [LaTeX input direction](../../USER-VISION.md#2026-09-20-latex-answer-input).
Use the smallest response that measures the objective. Preserve useful plain
Markdown, keyboard controls, raw learner work, pending prose, and runtime-owned
scoring and disclosure.

## D1: One typed completion form

Add `fill` for one or several labeled fields with stable IDs. The bank's
`[FIELDS: JSON]` array declares each text or numeric field and its private
checking policy. The public projection contains only entry instructions.
Answers map field IDs to original strings. One runtime verdict covers the
whole item. This deliberately preserves the existing Boolean evidence model.

Text fields declare accepted strings, case sensitivity, and whitespace policy.
Unicode NFC is applied without removing accents or punctuation. Numeric fields
use bounded exact rational parsing for decimal, fraction, and scientific input.
Absolute and relative tolerance are explicit. Optional units use authored
positive conversion factors to a named base unit. There is no global unit
database, affine conversion, expression evaluation, or guessed synonym rule.
Malformed and missing answers must not become zero or a successful attempt.

This composes single blanks, multiple blanks, measurement answers, and numeric
tables without making prose automatically graded. A label may identify a blank
in the stem. Inline graphical placement remains optional future presentation.
Offline static quizzes show a runtime-required state instead of introducing
another checker in JavaScript. Source files remain study-usable.

## Atomic work packets

| Packet | Owned change | Gate |
|---|---|---|
| answers-00 | Preserve the research and exact request | Audit's completed source checks and scoped diff |
| answers-01 | Close premature check disclosure | Serialized active exam/diagnostic and practice regression tests |
| answers-02 | Reject execution failure despite matching output | Real harmless crash probes, harness, success, timeout and output bounds |
| answers-03 | Parser, lint, public schema, score, identity, evidence, and author contract for fill | Synthetic text, numbers, units, invalid input, key exclusion and schema tests |
| answers-04 | Served and script-free entry, retries, drafts, export boundaries and static fallback | CLI/API and browser journeys, keyboard inputs, exact resume, no key in served page |
| answers-05 | Adjacent authoring defects and readiness review | Mixed visual/check warning, binary-choice decision, focused and full repository gates |

Each packet gets one commit after its verification. Files are staged by name.
Independent changes use separate owners. The root agent integrates and owns
the final records. New response schemas are additive and do not migrate old
evidence. Existing banks and accepted course artifacts remain unchanged.

## Further advancements and limits

Bounded symbolic algebra remains Prototype until grammar, domains, requested
form, and uncertainty behavior have an independently reviewed checker.
Production hostile-code isolation remains Deferred pending a selected portable
execution boundary and resource/escape tests. Native execution remains honestly
documented as trusted local code. SQL, notebooks, chemistry structures, speech,
and physical performance retain the audit ledger's course-specific triggers.
Partial credit needs a separate evidence contract and is not inferred from
multiple fields. These are retained capabilities, not discarded ideas.

## Readiness and recovery

The audit provides primary-source comparisons and reproduced defects.
`CONTRACT-REVIEW.md` records the independent schema and integration review.
Synthetic fixtures and focused tests are the executable contract prototype.
Promotion to the branch requires their gates plus full integration checks.
No new dependency, remote service, or learner-data egress is introduced.
Banks are parsed only in model.py and verdicts remain in runtime.py.
Reverting an individual packet restores the prior behavior. No real bank is
rewritten and no installed application is replaced by this source work.

## Results

Pending implementation and integration.
