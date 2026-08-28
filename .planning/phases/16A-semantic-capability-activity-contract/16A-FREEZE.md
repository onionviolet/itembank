# Phase 16A freeze record

## Freeze withheld

**Dated 2026-08-28.** Four of the five freeze legs hold. One does not, and it is
the one a machine cannot supply.

---

## The failing leg

**The contract-legibility review is unsigned.**

Plan `16A-10` Task 2 is a blocking human checkpoint. Its own prohibition is the
reason it cannot be closed here:

> An agent must not sign its own contract; the judgment that fourteen roles,
> fifteen capability profiles, eleven activity fields, eight backburner
> triggers, and two degraded paths are legible and honest is a human's, and a
> green tracer is not that judgment.

`16A-REVIEW.md` exists and is a fully prepared review packet: every table is
laid out, every command a reviewer needs is written out, and plan `16A-09`'s
three findings are summarized with the agent's reading offered as input. It
carries **no verdict word and no signature**, deliberately. Plan `16A-10`
Task 3 step 2 makes an unsigned review a failing leg, so this record is a
withholding and not a freeze.

**What would close it.** A human reads `16A-TRACER-REPORT.md`, runs both suites,
reads the fifteen capability profiles and the eight backburner entries as prose,
reads the three copy strings as a learner, judges the seven role labels, reads
the built corpus in a plain text editor, rules on the three findings, and
records `accept`, `accept-with-findings`, or `reject` in `16A-REVIEW.md` with a
signature and a date. Then plan `16A-10` Task 3 is re-run: on `accept` or
`accept-with-findings` it rewrites this file as a freeze; on `reject` it rewrites
the withholding with the reviewer's reason.

**Phase 16A stays open.**

---

## The four legs that do hold

Re-run on 2026-08-28, Darwin arm64, Python 3.14.6, in this task rather than
trusted from plan 16A-10 Task 1, because a record must describe the tree it is
describing.

### Leg 1: the stress-corpus tracer is green

```
TRACER: 18 passed, 0 skipped, 0 failed
```

Exit 0. All eighteen scenarios pass; none skipped, none failed. All nine of
`ROADMAP.md`'s freeze-gate legs are marked `passed` in
`16A-TRACER-REPORT.md`, with none marked `weaker proof` or `not run`.

### Leg 2: the adversarial suite is green

```
ADVERSARIAL: 18 attempted, 18 refused, 0 succeeded
```

Exit 0. Three attackers, four attacks each, plus two probes and four attacks on
Phase 16A's own new grammar. Every gate under attack is the real shipped
function; the suite contains no stand-in of any kind.

### Leg 4: no unresolved leak in this phase's own new grammar

Plan `16A-09`'s summary records three findings and **no successful attack**. All
three are recorded in `16A-TRACER-REPORT.md` section 5 and are carried into the
open-items list below. None is an unresolved leak in the sense this leg tests:

- **F1** is an over-strictness in `runtime.glossable`, not a permissiveness. It
  refuses more than it needs to and leaks nothing.
- **F2** is that `glossable` **correctly classifies** the three new surfaces as
  keyed and nothing yet consumes that verdict. The classification is right and
  unread.
- **F3** is that an `[!EXCERPT]` publishes what it quotes, which is what a
  lesson page is.

**This leg is judged to hold, and that judgment is offered to the reviewer
rather than settled here.** F2 is the one worth arguing about, and step 8 of
`16A-REVIEW.md` puts it to the reviewer by name. If the reviewer decides F2 is
a disclosure hole rather than a recorded handoff, this leg fails too and the
withholding stands on two legs instead of one.

### Leg 5: the full suite is green and the format growth is additive

```
$ python itembank.py guard .
0 offending files
```

The three baseline SHA-256 values from `16A-PRECONDITION.md`, re-verified:

```
fixtures/lesson_golden_phase3_parse.json 4078e7532ed33b341a6d551791d8ecc72175e1e479c63420b56db2b635a8e5aa
fixtures/lesson_golden_phase3_content.txt 800edb4cc180cda67885dc558e6784e713e9d636f9ebf8336919c1df93318a3c
fixtures/lesson_bank.md e34d5c9d3c2c16115257d5b1640f8aa9386e037ff6a15bc1eb6480d82c64398e
```

All three unchanged. Four lesson directives, seven callout kinds, four preamble
registries, twenty lint codes, and three new `lesson_page` keywords were added,
and a bank using none of them parses and renders byte for byte as it did before
any of it existed.

The full suite leaves exactly three red files:
`tests/day_roundtrip.py`, `tests/phase_062_audit.py`, and
`tests/retention_ui_roundtrip.py`. All three are **pre-existing**, were re-run
against a clean stash of this phase's work and failed there too, and none is
caused by Phase 16A. `tests/day_roundtrip.py` fails on this machine because a
live Anki instance is reachable, so the "Anki closed" locked copy it asserts is
not what `day --check` prints here.

**This leg is recorded as holding for Phase 16A's own work and as carrying a
named pre-existing exception**, rather than as unconditionally green, because
saying the suite is green when three files are red would be the kind of claim
this record exists to not make.

---

## What WOULD be frozen, if the review closes

Enumerated here so the reviewer can see the exact surface the signature would
freeze, and so a later reader of a withholding is not left guessing what was
nearly published.

**Semantic roles.** The eleven `surfaces.lesson._CALLOUT_KINDS` members: `KEY`,
`EXAMPLE`, `NOTE`, `WARNING`, `PREREQUISITE`, `MISCONCEPTION`, `TIP`,
`COUNTEREXAMPLE`, `EXCERPT`, `UNCERTAINTY`, `SUMMARY`, with their seven new
`(slug, label)` pairs. `capabilities.SEMANTIC_ROLE_CATALOG`, fourteen entries,
and `capabilities.role_mechanism`. The trailing `!` required marker,
`surfaces.lesson.UNSUPPORTED_SEMANTIC_COPY`, and the two unknown-semantic
degradation paths.

**Lesson directives.** `[SEMANTIC-PROFILE:]` defaulting to `1`,
`[LESSON-LANG:]` defaulting to `en`, `[LESSON-DIR:]` defaulting to `auto`, and
`[EXAMPLE-ORDER:]` defaulting to `example-first` with an empty reason.
`model.parse_lesson`'s nine added keys, including `dir_declared`.

**Capabilities.** `capabilities.py`'s full symbol list:
`CAPABILITY_PROFILE_KEYS`, `RENDERER_AVAILABILITY`, `CAPABILITY_CONTEXT_KEYS`,
`MEDIA_RIGHTS_STATES`, `MEDIA_AVAILABILITY`, `OUTPUT_MODES`,
`BACKBURNER_MODES`, `OUTPUT_MODE_KEYS`, `BACKBURNER_KEYS`,
`SEMANTIC_ROLE_CATALOG`, `CapabilityError`, `profile`, `profiles`, `register`,
`static_path`, `resolved_availability`, `validate_profile`, `role_mechanism`,
`catalog_profile_name`, `activity_fallback`, `compose_outline`,
`compose_glossary`, `backburner_entry`, `backburner_catalog`. The fifteen
profile names, in registry order: `callout_key`, `callout_warning`,
`callout_prerequisite`, `callout_misconception`, `callout_tip`,
`callout_example`, `callout_counterexample`, `callout_excerpt`,
`glossary_definition`, `callout_uncertainty`, `callout_summary`,
`inline_check`, `hint_ladder`, `visual_interaction`, `guided_mode`.

**Published schema.** `schemas/capability_profile.schema.json`.

**Media.** `model.MEDIA_COLUMNS`, the `[MEDIA: id]` reference form,
`model.parse_media`, `surfaces.lesson.MEDIA_MISSING_COPY` and
`MEDIA_REMOTE_COPY`.

**Activities.** `model.ACTIVITY_COLUMNS`, `ACTIVITY_PURPOSES`,
`ACTIVITY_RETRY`, `ACTIVITY_FEEDBACK`, `ACTIVITY_EVIDENCE_STATES`,
`RESPONSE_FORMS`, `model.parse_activities`.

**Render surface.** `lesson_page`'s `mode`, `media`, and `activities` keyword
arguments and their defaults.

**Lint codes**, the twenty this phase added:
`lesson.unknown_semantic`, `lesson.unknown_required_semantic`,
`lesson.definition_before_example`, `lesson.example_order_no_reason`,
`media.duplicate_id`, `media.missing_alt`, `media.unknown_rights`,
`media.unknown_availability`, `media.ref_unknown`,
`activity.duplicate_item`, `activity.empty_block`, `activity.item_unknown`,
`activity.unknown_purpose`, `activity.demand_empty`, `activity.unknown_retry`,
`activity.unknown_feedback`, `activity.unknown_evidence_state`,
`activity.missing_static_fallback`, `activity.missing_a11y_equivalent`,
`activity.unsupported_response_form`. Plus the new `media` and `activity`
namespace prefixes.

---

## What is NOT frozen, in any case

Stated explicitly, following the prototype-before-freeze coupling clause the
15A and 15B freeze records use. Nothing below is settled by anything in
Phase 16A, and a later phase must not read this record as having settled it.

- **Not a visual system freeze and not a token freeze.** No color, spacing,
  typography, motion, or token decision was made anywhere in Phase 16A. Every
  class name this phase introduced is unstyled on purpose.
  **Owner: Phase 17A.**
- **Not an information architecture or navigation freeze.** Guided mode is a
  data contract and a minimally rendered proof; nothing persists across a stage
  boundary and reading position does not exist. **Owner: Phase 16B.**
- **Not a notes or strategy freeze.** There is no learner-note durable object.
  The adversarial suite's note attacker is a stand-in for a store that does not
  exist. **Owner: Phase 16C.**
- **Not a learner-facing surface freeze.** No composed output-mode record
  reaches any surface; both composers return dicts and nothing renders them.
  **Owner: Phase 16B.**
- **Not a course schema freeze.** `compose_outline`'s graph path is exercised
  by no fixture, because the corpus has lessons and not courses.
  **Owner: whichever phase first composes a course.**

## The canonical format verdict

The canonical lesson stays **UTF-8 Markdown** with an additive versioned
semantic profile. A proprietary or open-package canonical format stays
rejected, and **none of the eight criteria** in research report 04 section 8's
proprietary-format gate was met, per `16A-RESEARCH.md`'s Code Examples section.

Phase 16A is the strongest test that verdict has had: fourteen semantic roles,
four preamble registries, ten localization cases including a bidi override and
a precomposed/decomposed pair, and a delete-and-rebuild portability cycle over
seventeen banks all ride on plain Markdown, and `scenario_portability` proves
every capability's meaning, caption, citation, definition, static instruction,
and media alternative is findable in the canonical bytes with every derived view
deleted.

---

## Open items, with owners

Carried forward from `16A-TRACER-REPORT.md` section 5. This list stands whether
the freeze closes or not.

| Item | Owner |
|---|---|
| F1: `runtime.glossable` refuses any definition containing an mc key's bare letter | whichever phase next touches disclosure |
| F2: `glossable`'s verdict is unread for the media alt, the activity fallback, and the excerpt body | whichever phase first gates authored text inside a sitting |
| F3: an `[!EXCERPT]` publishes what it quotes | authoring guidance, or a later lint plan |
| Media rights enforcement, deferred by `D-16A-8` | whichever subphase first packages or exports a media asset |
| Media integrity recomputation, declared and never verified | the same subphase |
| A media row's rights are coarser than every other rights record in the tree | the enforcement subphase, which inherits the question |
| The annotated worked-example structure, per `D-16A-6` | a later capability-profile version bump |
| A structured `effective_date` or `jurisdiction` field, per `D-16A-7` | contingent on 15B's staleness machinery |
| Interface localization of the seven role labels and three copy strings | whichever phase introduces an interface language setting |
| Every Phase 17A CSS handoff: `.capability-static`, `.media`, `.media-unavailable`, `.media-remote`, `.callout-unsupported`, the seven new `callout-<slug>` classes, `.stage`, `data-stage`, `data-stage-open`, `data-required` | Phase 17A |
| CJK and Arabic font coverage, and the layout of an unbroken 318-character token | Phase 17A |
| `dir="auto"` is not emitted on `<th>` cells | Phase 17A or a later A11Y plan |
| A `[MEDIA:]` reference in the lesson intro renders nothing | recorded narrow spot, pre-16A behavior |
| `> [!KEY!]` renders the generic callout rather than the index card | recorded narrow spot, unused |
| An activity's `stimulus` is free prose resolved against nothing | whichever phase links activities to sources |
| An activity's `objective` is not namespace-checked | whichever phase extracts the shipped rule into a helper |
| `compose_outline`'s graph path is exercised by no fixture | whichever phase first composes a course |
| No composed output-mode record reaches a surface | Phase 16B |
| Three pre-existing red suites: `day_roundtrip`, `phase_062_audit`, `retention_ui_roundtrip` | pre-existing, not Phase 16A's |

---

## Evidence, verbatim

```
$ python tests/capability_stress_corpus_tracer.py
TRACER: 18 passed, 0 skipped, 0 failed

$ python tests/assessment_authority_adversarial.py
ADVERSARIAL: 18 attempted, 18 refused, 0 succeeded

$ python itembank.py guard .
0 offending files
```

Full suite: three pre-existing red files, named above, none caused by this
phase.

Golden SHA-256 values: all three unchanged, quoted in Leg 5 above.

Review verdict: **none recorded.** `16A-REVIEW.md` is unsigned.
