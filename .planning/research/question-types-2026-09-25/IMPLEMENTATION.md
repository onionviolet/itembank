# Question and checker implementation

Date: 2026-09-26. Base: `ee23d88`.
Status: verified source candidate on `codex/question-types-checking-20260926`.
The [vision entry](../../USER-VISION.md#2026-09-26-implement-question-types-and-answer-checking)
preserves the exact implementation direction. This record owns its bounded
requirements, decisions, and verification.

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
| answers-05 | Restore drafts over starters and stale invalid-response echoes | Actual native-form and dynamic-client JS regressions |
| answers-06 | Accurate structured-scoring lint | Mixed visual/check/fill bank retains only the prose pending warning |
| answers-07 | Bound public field schemas and diagnostic schema | Validator bounds, malformed public payloads, and protocol checks |
| answers-08 | Single-line text parity | Controls, labels, accepted values, and submissions share entry limits |
| answers-09 | Disclosure and crash diagnostics | Equivalent text blocked, numeric glossary withheld, released stderr only |
| answers-10 | User and agent authoring documentation | Format and export limits match implemented behavior |
| answers-11 | Retryable routes and clear runtime errors | Two real HTTP routes, no invalid evidence, escaped diagnostics, network recovery |
| answers-12 | Response and default-profile snapshots | Exact additive fill delta preserves every prior setting value |
| answers-13 | Privacy test specificity | Public numeric prose allowed, nested credential sentinels refused |
| answers-14 | Single-scorer structural gate | Capability helper is distinct from scorer, justified source pin with behavioral tests |
| answers-15 | Lesson shared-field contract | New type-count heading preserves lesson tags and reader declarations |
| answers-16 | Existing runner and schema contracts | Additive process diagnostics and enum deltas preserve previous guarantees |
| answers-17 | Shared response presentation | Typed fields have shared labels, instructions, and real fixture coverage |
| answers-18 | Complete capability corpus | Ten activity purposes include a real typed completion, with all 18 tracer scenarios exercised |

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

### Implemented behavior

`fill` provides 1 to 16 labeled fields with original strings in evidence.
Text supports explicit accepted variants, NFC, case policy, and whitespace
policy. Numeric values use exact bounded rational parsing, inclusive absolute
or relative tolerance, and authored unit scales. The parser retains malformed
FIELDS metadata so lint reports it instead of silently dropping the question.
Public items expose entry rules but no answer, tolerance, or conversion factors.
Default subject profiles, authoring requests, selection, sessions, and response
schemas admit the additive form. Existing restrictive custom profiles remain
restrictive. The schema version stays compatible with existing payloads.

Every blank must pass for the item to pass. Invalid, missing, and oversized
entries produce no response evidence and remain editable. Runtime/API/native
form and JavaScript paths share the authority boundary. Saved code replaces a
starter on reload, including an intentionally empty draft. Saved fill edits
replace stale invalid-response echoes. Acknowledged submissions clear drafts.
Static fill pages explain that checking needs a running session. Anki and GIFT
refuse conversion rather than silently losing rules.

Python checks now require successful process exit for stdout and function
harness cases. Crashes show an escaped diagnostic and exit status when feedback
is released. Active exam/diagnostic bodies strip nested verdicts and case data,
including replayed responses. Timeouts retain their existing pending semantics.

### Independent review and verification

The initial contract review is retained in [CONTRACT-REVIEW.md](CONTRACT-REVIEW.md).
A second implementation review found route refusal, draft, entry parity,
schema, diagnostic, and glossary gaps. All were repaired and a closure review
reported no remaining actionable finding in that bounded scope.

The final full preflight passed all 147 Python test scripts, the JavaScript
suite, and every other local gate, including the clean-tree gate. A temporary
logging wrapper invoked the unchanged preflight gates and retained complete
subprocess diagnostics. No remote CI run is claimed. The two CI-only steps
remain the preflight's documented exclusions.

Focused regressions cover 8 fill contract tests, 6 public-schema checks,
4 process-verdict probes, both actual submission routes, evidence replay,
native/dynamic draft recovery, invalid input, uncertain network delivery,
and escaped stderr. The first full run exposed stale snapshots, a privacy
false positive caused by public numeric prose, and nested single-scorer test
failures. Later output also exposed obsolete lesson heading and runner-shape
assertions, an additive schema snapshot, and a missing shared presentation
registration. The capability corpus now includes a real typed retrieval item
while preserving all ten purposes. Its tracer passes 18 scenarios with no
skips. The corresponding fixes preserve the old setting snapshot after
removing only the intended additive fill entries. Credential sentinels still
fail the privacy guard. The sole scorer retains its structural and source pin.

A fresh temporary `.pyz` ran from outside the checkout. Its exam sitting
accepted BLUE with 5/2, an accented answer, and 100 cm, completed at 3/3, and
withheld scoring fields in submission bodies. This is packaged CLI evidence,
not an installed desktop-app check.

Chrome on a disposable synthetic bank verified two correct answers, malformed
numeric refusal, Unicode draft restoration, and the desktop field layout.
It exposed stale invalid-entry restoration, subsequently repaired and covered
by the actual native-form JS regression. Browser automation then timed out
during the narrow-viewport attempt, so no mobile-browser completion or final
live-browser retest is claimed. The preview server was stopped.

Large modules were sampled around affected symbols, not read in full.
Automated assertions and bounded review do not establish human accessibility,
learning transfer, installed parity, or full competitive parity.

### Atomic implementation history

| Packet | Commit |
|---|---|
| Audit and implementation gates | `f4f2f94`, `d46151b` |
| Silent check feedback | `761ecc3` |
| Successful process exit | `765c8ee` |
| Typed field core | `6fb8cab` |
| Entry surfaces and exports | `a7d165b` |
| Draft recovery | `043b79f` |
| Structured scoring capability | `2416cf3` |
| Public schema bounds | `264d03a` |
| Single-line entry parity | `2ccf7b8` |
| Runtime feedback semantics | `e663c2f` |
| Authoring documentation | `1cfdbd7` |
| Retry and crash UI | `eea2275` |
| Profile and type snapshots | `eb2bae7` |
| Privacy regression specificity | `3023801` |
| Single-scorer verification | `cf240c4` |
| Lesson shared-field verification | `69250cf` |
| Runner and schema verification | `bffd2f3` |
| Shared presentation | `1939b98` |
| Typed completion capability corpus | `309728e` |

### Retained advancements and practical limits

Two-option MC is not promoted in this slice. The existing table supports
binary classification, while ordinary MC retains its current option-count
policy. Inline blanks, partial credit, and ordered alternative solutions need
their own response or evidence rules. Revisit them for a named objective.
Symbolic algebra and subject adapters retain the statuses and triggers above.

Numeric fill suppresses automatic glossary definitions for any unopened set
containing a numeric field, including unrelated definitions. This conservative
boundary avoids revealing equivalent quantities or answers inside a tolerance
interval. Text-only fill uses the declared normalization for glossary screening.
Units support positive multiplicative scales, not affine temperatures,
dimensional inference, locale commas, or significant-figure grading.

Native Python remains trusted local execution with time and output bounds.
It is not an isolation boundary for hostile programs. There is no new runtime
dependency, hosted processing, or learner-data migration. No real question bank
was modified. Source commits remain on their candidate branch. No push, merge,
installation, or release is implied by these results.
