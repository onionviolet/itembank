# 16B-01 precondition check, dry run 2026-08-27

**This is not `16B-PRECONDITION.md` and must not be renamed to it.** Plan
16B-01 step 9 creates that file **on success only**. This run does not succeed,
so the deliverable is deliberately not written. This record exists because
Weibao asked for the check to be re-run against the current tree, and because
the answer is useful now rather than whenever 16B is executed.

Run by an agent, read-only. No module was created, no import was stubbed, no
check was skipped, and nothing outside `.planning/` was touched.

## Result

**HALT.** Steps 1, 3, 4 and 5 are divergent. The halt line plan 16B-01 step 8
prescribes, with the failing item substituted:

```
HALT 16B-01 precondition: Phase 14A or Phase 16A has not landed, its frozen
surface differs from what Phase 16B was planned against, 16A froze on an
unresolved divergence, Phase 13.9 was not walked, or the shipped daemon route
table and settings surface moved. Re-verify every 16B plan against
.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md and
.planning/phases/16A-semantic-capability-activity-contract/16A-FREEZE.md before
writing any code. Divergent or missing: Phase 16A has not landed (capabilities
module absent, 16A-FREEZE.md absent, 16A-PRECONDITION.md absent,
model.SEMANTIC_PROFILE_VERSION absent)
```

**The blocker is Phase 16A, not Phase 14B.** This corrects the expectation the
2026-08-26 shelf reconciliation note set. That note flagged 16B-PATTERNS.md's
`(14B, unbuilt, confirmed MISSING)` annotation as stale, which it is, but stale
in the harmless direction: 14B's modules are all present and the check passes on
them. What actually stops 16B is that 16A has never executed.

## What was checked

| Step | Check | Result |
|---|---|---|
| 1 | Seven dependency modules import | **divergent** |
| 2 | 14A journal surface matches plan text | ok |
| 3 | 16A surface matches plan text | **divergent** |
| 4 | Both freeze records exist and are real freezes | **divergent** |
| 5 | What those freezes rest on | **divergent** |
| 6 | Shipped daemon and settings surface unmoved | ok, with two recorded deviations |
| 7 | Additivity baseline captured, shipped suites green | ok |

### Step 1, dependency modules

```
OK      identity
OK      journal
OK      discovery
OK      graph
OK      course
OK      course_package
MISSING capabilities
```

Six of seven present. `capabilities` is a Phase 16A module and does not exist.
`graph`, `course` and `course_package` are Phase 14B's and all landed on
2026-08-26.

### Step 2, 14A journal surface

Output: `14A journal surface matches`

`journal.OBJECT_STATES` is `("clean", "conflict", "interrupted", "missing",
"unavailable")`; `journal.ENTRY_STATES` is `("prepared", "applied",
"refused")`; `entries`, `replay`, `object_state` and `undo` are all callable;
`identity.OBJECT_KINDS` is a tuple containing `"lesson"`. Every 14A fact plan
16B-02's Activity read model composes over is intact.

### Step 3, 16A surface

Divergent on two of three legs.

- `capabilities.RENDERER_AVAILABILITY`: **unreachable**, module absent.
- `model.SEMANTIC_PROFILE_VERSION`: **absent** from `model.py`. Planned value
  was `1`.
- `lesson._CALLOUT_KINDS`: **ok**. Four kinds present, `KEY`, `EXAMPLE`, `NOTE`,
  `WARNING`, matching the shipped-four requirement.

### Step 4, freeze records

- `14A-FREEZE.md`: **present**, contains `## Frozen at 14A`, contains no
  `## Freeze withheld`. Real freeze.
- `16A-FREEZE.md`: **absent**. The `16A-semantic-capability-activity-contract`
  directory holds thirteen entries, all `16A-NN-PLAN.md` and supporting text,
  with no summary, no precondition record, and no freeze record. Phase 16A is
  planned and unexecuted.

### Step 5, what the freezes rest on

- `16A-PRECONDITION.md`: **absent**, so there is no dated result line to read.
  This is not the `16A froze on an unresolved precondition divergence` case;
  16A simply never ran.
- `13.9-03-SUMMARY.md`: **present**. Phase 13.9 was walked, so the
  `13.9 unwalked behind a frozen 16A` divergence does not apply.

### Step 6, shipped surface

```
found:   12 36 True 12 6 21 False 18
planned: 12 34 True 12 6 20 False 18
```

Both halt-triggering fields are clean: the third field is `True`, so
`daemon.ROUTE_CLI` still covers every route, `additionalProperties` is still
`False`, and `len(settings.SETTINGS_CODES)` is still `6`. Two deviations are
recorded below rather than halting.

### Step 7, additivity baseline and shipped suites

Captured before any 16B change exists, per the plan's ordering requirement.

```
schemas/settings.schema.json e156adf40ec6f9f9fba1c7c7748524cbe11039e1cec10bfd0d13e8bf8d6587d9
itembank.json be2c916a9670f3b8f81a08c7b600f29e8906344c4aab9c066aed0aa7c60e228b
21
3af78f069337172d49477f410158ff1827a7977f87447c9ee9d1e31fd4c2885b
```

Plan 16B-06 asserts every pre-existing settings key unchanged against these
values. A changed pre-existing key means the settings change was not additive.

**Caution on reuse.** These are today's values, taken during a dry run while
16A has not landed. Phase 16A may legitimately add settings keys before 16B
runs. Whoever executes 16B-01 must **retake this baseline** rather than copying
these lines forward, or 16B-06's additivity proof will be measured from the
wrong instant.

Shipped suites, both green:

```
python tests/daemon_roundtrip.py   exit 0   (75 checks)
python tests/config_roundtrip.py   exit 0
```

## Deviations found

| Item | Plan text | Landed | Halt? |
|---|---|---|---|
| `capabilities` module | present | absent | yes, step 1 |
| `capabilities.RENDERER_AVAILABILITY` | `("available", "degraded", "unavailable")` | unreachable | yes, step 3 |
| `model.SEMANTIC_PROFILE_VERSION` | `1` | absent | yes, step 3 |
| `16A-FREEZE.md` | present with `## Frozen at 16A` | absent | yes, step 4 |
| `16A-PRECONDITION.md` | present with a dated result line | absent | yes, step 5 |
| `len(daemon.ROUTES)` | 34 | **36** | no, named non-halt in step 6 |
| `len(settings.schema.json properties)` | 20 | **21** | see note below |
| `16B-PATTERNS.md` line 381 annotation | `14B, unbuilt, confirmed MISSING` | 14B landed 2026-08-26 | no, stale in the harmless direction |
| `16B-01` D-16B-3 rationale | "`course.py` does not exist" | `course.py` exists | no, but see below |

**On `len(properties)` 21 versus 20.** Step 6's prose names three halt
conditions and this is not among them, so by the prose this is a recorded
deviation. But plan 16B-01's own automated verification command asserts
`len(s['properties'])==20` literally, so that command **will fail** on the
current tree even once 16A lands, unless the assertion is updated. This is a
plan-text defect rather than a tree defect: a settings key was added
legitimately after 16B-01 was written. Flag for whoever executes 16B-01.

**On D-16B-3.** The decision reasons that a `course` CLI verb would be "a
command with nothing behind it" because "`course.py` does not exist". That
premise is now false. The decision may still be right for other reasons, since
course pages remain browser renderings the `daemon` command already serves, but
it should be re-derived rather than inherited.

## What must not happen next

Plan 16B-01 is explicit and it is restated here because the temptation is
obvious now that six of seven modules import: a failed precondition must not be
worked around by stubbing `capabilities`, by wrapping its import in a try or
except, by continuing with a reduced check set, or by recording the divergence
and proceeding anyway. **The halt is the correct outcome.** 16B runs after 16A
lands and freezes, and not before.

## Sequencing note

`ROADMAP.md` makes 16B depend on 14A and 16A. 14A is executed and frozen; 14B
waves 1 to 3 are executed with waves 4 to 6 blocked on human checkpoints; 16A is
planned and unexecuted. So the path to a real course shelf is 14B waves 4 to 6,
then 16A, then 16B, and the shelf itself is plan 16B-04, four plans into 16B.
The 2026-08-26 mockup illustrates a surface that is several phases out.
