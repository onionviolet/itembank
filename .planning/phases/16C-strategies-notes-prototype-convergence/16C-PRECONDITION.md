# 16C precondition check

## Why this check exists

`16C-RESEARCH.md`'s Critical caveat records that Phase 16C was planned three
unexecuted phases deep: `identity.py`, `journal.py`, `discovery.py`,
`graph.py`, `course.py`, `course_package.py`, `capabilities.py`, and
`surfaces/ia.py` all read MISSING at the repository root, no `*-FREEZE.md` of
any kind existed, and `.planning/phases/13.9-walking-skeleton/` held no
SUMMARY. Every 14A, 14B, 16A, and 16B signature this phase cites was read from
plan text, never from source. This check is the only place that boundary is
tested before any 16C code is written. It is one degree stricter than
16B-01's: it distrusts three freeze records, reads three upstream precondition
dated result lines, and confirms Phase 13.9's A9 closure directly.

## What was checked

Run 2026-08-29. Every command was run with `python3` substituted for `python`;
see Deviations found, item 3.

| Step | Check | Result |
|---|---|---|
| 1 | The eight dependency modules import (`identity`, `journal`, `discovery`, `graph`, `course`, `course_package`, `capabilities`, `surfaces.ia`) | ok, `modules present` |
| 2 | 14A surface: `journal.OBJECT_STATES`, `journal.ENTRY_STATES`, five callables, `identity.OBJECT_KINDS` carrying `lesson` and `bank`, `identity.object_fingerprint` | ok, `14A surface matches` |
| 2 | 14A carve-out sentence quoted from `14A-FREEZE.md` | ok, quoted below |
| 3 | 16A surface: `capabilities.RENDERER_AVAILABILITY`, `model.SEMANTIC_PROFILE_VERSION == 1`, the four callout kinds | ok, `16A surface matches` |
| 3 | 16A shared note or activity schema hooks (CAP-03) | activity vocabularies published, note hooks `none published`; see below |
| 4 | 16B surface: seven `MODE_LAYERS`, two fixed layers, `mode_layer_resolve` and `mode_layer_conflict_copy` callable, instructor_policy wins with `conflict` true | ok on every structural assertion; the copy string differs from the plan's expected line, see Deviations found item 2 |
| 4 | `CONFLICT_CASES` extension point present in `tests/mode_layer_roundtrip.py` | ok, `16B conflict fixture present` |
| 5 | `14B-FREEZE.md`, `16A-FREEZE.md`, `16B-FREEZE.md` each carry `## Frozen at`, none carries `## Freeze withheld` | ok, 1 and 0 on all three |
| 6 | The three upstream `*-PRECONDITION.md` dated result lines each state the phase may proceed | ok on all three |
| 6 | `16B-PRECONDITION.md` Deviations found section, checked for unresolved deviations | ok, two deviations, both carrying recorded resolutions, neither a halt |
| 7 | `.planning/phases/13.9-walking-skeleton/13.9-03-SUMMARY.md` exists | ok |
| 8 | Shipped surface: `KNOWN_EVENT_TYPES` fourteen members, `EVENT_SCHEMA_VERSION == 2`, ten dotted `STYLE_CHECK_CATALOGUE` keys, `parse_terms` key set, `lesson_slug` idempotent | ok on every leg except `parse_lesson`, which returns a superset; see Deviations found item 1 |
| 8 | `mark_event` refuses a non-human marker | ok, `marker gate holds` |
| 9 | `tests/evidence_roundtrip.py`, `tests/lesson_roundtrip.py`, `itembank.py guard .` | ok, exit 0, exit 0, `0 offending files` |

**The 14A carve-out, quoted from `14A-FREEZE.md`:** "line endings (`\r\n` and
bare `\r`) normalized to `\n` for every kind; trailing whitespace stripped from
every line for every kind except `bank` and `lesson`; no reflow, mid-content
whitespace collapsing, or Unicode normalization added. The `bank`/`lesson`
carve-out (`identity.TRAILING_WS_EXEMPT_KINDS`) holds regardless of the reflow
answer and stays exempt from trailing-whitespace normalization under both
options." Recorded `ok`. Plan 16C-08's keyed-meaning halt rests on it.

**The 16A shared-hook check.** `16A-FREEZE.md` publishes the activity
vocabularies `model.ACTIVITY_COLUMNS`, `ACTIVITY_PURPOSES`, `ACTIVITY_RETRY`,
`ACTIVITY_FEEDBACK`, `ACTIVITY_EVIDENCE_STATES`, and the `activity.*` lint
codes, and it states in its own words: "Not a notes or strategy freeze. There
is no learner-note durable object." So for notes the answer is `none
published`, and plans 16C-02 and 16C-06 create the note store rather than
composing with a 16A hook. For activities the names above exist and are the
registration seam any 16C activity reference must use rather than duplicating.

## Additivity baseline

Plan 16C-06 asserts the evidence surface unchanged for every pre-16C event
against these values. A changed value means the event extension was not
additive.

```
fixtures/selection_evidence.jsonl 55fd52b56d66438778d8ea0d6c94929c7a65c39763e0acf12c8ad12b876861ce
fixtures/lesson_retention_events.jsonl a9338eb7d0a5f2603501163e4bb60e972063f86b843291cdf7d576217ca5f831
schemas/settings.schema.json b6e5b15484ce247f96b69f18df73da45e109a38e0c29aa0d6ad63093e54edc2a
[40, 0]
a9f88a0388669ae89a49b5d16d54c684e3d6d325af960a1c37d0521e29b492d7
```

The `0` in the captured-view counts is correct and is recorded here so plan
16C-06 does not read it as a broken baseline:
`fixtures/lesson_retention_events.jsonl` holds exactly two events, one
`lesson_complete` and the `retraction` that compensates it, so
`evidence.capture_events` returns zero live events by design. The file hash
still proves the bytes unchanged, and the captured-view hash still proves the
reader's output unchanged.

Both commands were run before any file outside `.planning/` was touched. No
file outside `.planning/` was created or modified by plan 16C-01.

## Deviations found

Three. None is a missing module, an absent or withheld freeze, an upstream
freeze resting on an unresolved divergence, or an unwalked 13.9.

**1. `model.parse_lesson` returns a superset of the key set the plan asserts.**
Reconciled rather than pinned, on Weibao's answer of 2026-08-29.

| | Value |
|---|---|
| Plan text (16C-01 step 8) | `{'source', 'body', 'intro', 'headings', 'error', 'detail'}`, six keys, asserted by set equality |
| Landed 2026-08-29 | the same six keys plus `lang`, `lang_raw`, `dir`, `dir_raw`, `dir_declared`, `gate`, `semantic_profile`, `semantic_profile_raw`, `example_order`, `example_order_reason`, sixteen in all |
| Added by | `aa14114` feat(16A-02): the parse layer, three additive lesson directives; `53dd3cf` feat(16A-03): six semantic roles, the role catalog, and two degradation paths |

All six planned keys are present, so the change is a pure superset from a
frozen dependency, not a moved contract. The one 16C decision that reads
`parse_lesson` is D-16C-7, whose input contract is the pair of dicts
`parse_lesson` and `parse_terms` return, read by key. The reconciliation is
therefore: the assertion becomes "the six planned keys are present", not "the
key set equals six keys", and every later 16C plan reading `parse_lesson`
reads by key and never by key count. This is the same recorded-and-compared
rather than pinned move `16B-PRECONDITION.md` made for its route and settings
counts, with the drift attributed by `git log` to an upstream that has since
frozen.

**Authority for the reconciliation.** Plan 16C-01 step 11 rates a moved lesson
surface a halt, and forbids an executor working a failed check around on its
own judgment. The check was therefore not worked around: the wave stopped, the
divergence was put to Weibao with the halt option named and costed, and he
chose reconcile-and-proceed on 2026-08-29. The decision is his, recorded here,
not an executor default.

**2. The 16B conflict copy carries a clause the plan's step 4 expected line
omits.** Not a divergence in the landed code; a stale line in the plan.

| | Value |
|---|---|
| Plan text (16C-01 step 4, expected stdout) | `Timed test mode is set by your instructor's policy and can't be changed here.` |
| Landed 2026-08-29 | `Timed test mode is set by your instructor's policy for this course and can't be changed here.` |
| Plan text (16C-01 D-16C-5, the locked template) | `{Setting name} is set by {higher layer name} for this course and can't be changed here.` |

The landed string matches D-16C-5's own template verbatim, including `for this
course`. It is the plan's step 4 expected line that dropped the clause, so the
two halves of 16C-01 disagreed with each other and the landed code agrees with
the half that binds. D-16C-5 is transcribed into `16C-DECISIONS.md` unchanged
and the landed string is the one 16C composes over. Plans 16C-03 and 16C-05
must read the copy from `ia.mode_layer_conflict_copy` and never re-type it.

**3. The interpreter is invoked as `python3`, not `python`.** Every command in
plan 16C-01 is written as `python ...`. No `python` executable exists on this
machine; `python3` is at `/opt/homebrew/bin/python3`. Every command recorded
here was run verbatim with `python3` substituted and nothing else changed.
`16B-PRECONDITION.md` records the identical deviation.

## Dated result line

**2026-08-29. Phase 16C may proceed.** Steps 1 through 3 and 5 through 7
returned `ok` with no divergence. Step 4 returned `ok` on every structural
assertion and surfaced a stale expected line in the plan rather than a moved
16B contract. Step 8 surfaced one additive superset from frozen 16A, halted the
wave, and was resolved by Weibao rather than by an executor default. Step 9's
two suites passed and the guard reported `0 offending files`. The additivity
baseline was recorded before any file outside `.planning/` was touched.

Because Deviations found is non-empty, plans 16C-02 through 16C-09 read this
section before execution. The two consequences that carry forward are named
above: read `parse_lesson` by key, never by key count; and read the mode-layer
conflict copy from `ia.mode_layer_conflict_copy`, never re-typed.

Verbatim stdout of steps 1, 2, 3, 4, 8, and 10:

```
modules present
14A surface matches
16A surface matches
Timed test mode is set by your instructor's policy for this course and can't be changed here.
16B conflict fixture present
shipped surface matches
marker gate holds
fixtures/selection_evidence.jsonl 55fd52b56d66438778d8ea0d6c94929c7a65c39763e0acf12c8ad12b876861ce
fixtures/lesson_retention_events.jsonl a9338eb7d0a5f2603501163e4bb60e972063f86b843291cdf7d576217ca5f831
schemas/settings.schema.json b6e5b15484ce247f96b69f18df73da45e109a38e0c29aa0d6ad63093e54edc2a
[40, 0]
a9f88a0388669ae89a49b5d16d54c684e3d6d325af960a1c37d0521e29b492d7
```

The step 8 line above is the stdout of the reconciled command, in which the
`parse_lesson` leg asserts `{'source', 'body', 'intro', 'headings', 'error',
'detail'} <= set(L)` rather than set equality. The command exactly as the plan
wrote it exits non-zero with
`AssertionError: {'lang', 'dir_raw', 'gate', 'error', 'example_order_reason',
'dir', 'dir_declared', 'semantic_profile', 'source', 'semantic_profile_raw',
'headings', 'body', 'detail', 'example_order', 'intro', 'lang_raw'}`, which is
the raw evidence for Deviations found item 1 and is recorded here rather than
replaced by the passing run.
