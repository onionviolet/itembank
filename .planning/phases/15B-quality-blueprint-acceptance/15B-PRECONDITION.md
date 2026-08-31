# 15B precondition check

## Why this check exists

`15B-RESEARCH.md`'s Critical Caveat: **Phase 15B's entire dependency chain was
unexecuted when 15B was researched and planned.** `identity.py`, `journal.py`,
`discovery.py`, `graph.py`, `course.py`, `course_package.py`, `director.py`,
and `fixtures/corpus_14b.py` all read MISSING at the repository root, and no
`*-FREEZE.md` file existed for 14A, 14B, or 15A. Every signature this phase
imports was therefore read from **plan text, never from source**, and 15B is
fourth in a chain of four phases planned that way.

That is exactly how the 15A halt happened: 15A was planned against
`14A-02-PLAN.md`, which lists a twenty-two-key `journal.ENTRY_KEYS` tuple that
never landed, and taking the plan literally would have deleted a frozen key.
This check exists so the same class of error surfaces by name before any 15B
module exists rather than mid-task as a vocabulary drift.

## What was checked

Run 2026-08-30 on Darwin 27.0.0 arm64, Python 3.14.6.

**Step 1, the seven dependency modules import.**

- `identity`, `journal`, `discovery`, `graph`, `course`, `course_package`, `director` all import: **ok**

**Step 2, the frozen 14A constants.**

- `identity.OBJECT_KINDS` is the six-member tuple in order: **ok**
- `identity.RIGHTS_OPERATIONS` is the seven-member tuple in order: **ok**
- `identity.RIGHTS_STATES` equals `("granted", "denied", "unknown")`: **ok**
- All ten named 14A callables are callable on their modules: **ok**
- `journal.OPERATION_TYPES` has exactly six members: **ok**
- `journal.ENTRY_KEYS` member count, and its last member is `"agent"`: **divergent on the count, ok on the last member** (see Deviations found)
- `"reconcile"`, `"migrate"` and `"agent_operation"` are all in `journal.RECORD_TYPES`: **ok**

**Step 3, the frozen 14B constants.**

- `graph.TREATMENT_KINDS` has exactly eleven members: **ok**
- `graph.BINDING_STATES` equals the five-member tuple: **ok**
- `graph.BINDING_KINDS` equals `("source", "treatment")`: **ok**
- `graph.MIGRATION_KINDS` equals the five-member tuple: **ok**
- `graph.MIGRATION_STATES` equals `("proposed", "accepted", "rejected")`: **ok**
- `graph.COURSE_GRAPH_VERSION` equals `1`: **ok**
- `graph.SECTION_ORDER` is a tuple and `"Blueprint"` is NOT in it: **ok**. Plan 15B-02 adds it; it is not there yet.
- All twelve named 14B callables are callable: **ok**
- `course.COURSE_SIDECAR_FILENAME` equals `"course-graph.md"`, which the recorded `D-14B-1` option-a implies: **ok**
- `hasattr(graph, "accept_migration")` is `False`: **ok**
- `hasattr(graph, "reject_migration")` is `False`: **ok**. Phase 14B refused to build the acceptance path and named 15B as its owner; the gap plan 15B-04 was written to close is still open, which is what this assertion is for.
- `graph.migration_state_not_settable` is still live: **ok**, the literal string is present in `graph.py`.

**Step 4, the frozen 15A constants.**

- `len(director.PROTOCOL_STEPS)` is `13`, first `declare-intent`, last `report`: **ok**
- `director.AUTONOMY_LEVELS` equals the three-member tuple in ascending order: **ok**
- `len(director.AGENT_ENTRY_KEYS)` is `10`, `len(director.EGRESS_KEYS)` is `7`, `len(director.RECOMMENDATION_KEYS)` is `9`: **ok**
- `director.autonomy_level({})` returns `"recommend-only"`: **ok**
- `director.authorize_write({}, "recommend-only", 0)` returns `None`: **ok**
- All eight named 15A callables are callable: **ok**
- `hasattr(director, "evidence")` is `False`: **ok**

**Step 5, the shipped Phase 11 surface this phase composes.**

- `authoring.DETECTOR_VERSIONS` has four members; the `gates` object requires exactly `lint_errors`, `lint_warnings`, `quality_findings`; `blueprint_findings` is not yet a property; all three named lint codes are in `model.LINT_CODES`: **ok**

**Step 6, all three freeze records exist and are real freezes.**

- `14A-FREEZE.md` contains `## Frozen at 14A` and no `## Freeze withheld`: **ok**
- `14B-FREEZE.md` contains `## Frozen at 14B` and no `## Freeze withheld`: **ok**
- `15A-FREEZE.md` contains `## Frozen at 15A` and no `## Freeze withheld`: **ok**

## Deviations found

One, in step 2. It is the same divergence the 15A precondition found, arriving
one phase later for the same reason, and it is a disagreement between **two
planning records** rather than between a plan and the code.

| | Value | Source |
|---|---|---|
| Plan text 15B-01 asserted | `len(journal.ENTRY_KEYS) == 23`, described as "twenty-two from plan 14A-02 plus the one member plan 15A-01 appended" | `14A-02-PLAN.md`, plus 15A-01 |
| Landed | `len(journal.ENTRY_KEYS) == 24`, last member `agent` | `14A-FREEZE.md`'s twenty-three keys, plus 15A's one |

`14A-02-PLAN.md` lists twenty-two keys ending in `message`. `14A-FREEZE.md`
lists twenty-three ending in `rights`, and the code has matched the freeze
record since `77b27e9`, the only commit that ever touched the tuple. 15B-01
step 2 was written from the plan text, arriving at 22 plus 1, and the landed
answer is 23 plus 1.

**Resolution, recorded 2026-08-30.** The number is corrected to 24 in
`15B-01-PLAN.md` step 2 and its verify block, in `15B-VALIDATION.md`'s
precondition row, and the two other 15B plans that describe the tuple in prose
(`15B-01` read_first and `15B-04` read_first) now point at `14A-FREEZE.md` and
say twenty-three rather than twenty-two. **Nothing else changes**: `rights`
stays, `agent` stays last, `OPERATION_TYPES` stays at six, and no 15B plan
depends on the total in any other way.

**The root cause is the same one, and it is now recorded twice.** A plan's
`read_first` block pointed an executor at plan text for a value a freeze record
owns. A plan is a proposal and a freeze record is accepted truth; where they
disagree the freeze record wins. Every 15B pointer to `14A-02-PLAN.md` for this
tuple has been repointed.

## Dated result line

**2026-08-30.** Steps 1 through 6 were re-run in full after the correction and
every one passes.

```
python3 -c "import identity, journal, discovery, graph, course, course_package, director; print('modules present')"
modules present
```

```
14A surface matches
14B surface matches
15A surface matches
```

```
python3 -c "import authoring, model, json; ..."
4 ['lint_errors', 'lint_warnings', 'quality_findings'] False True
```

```
python3 -c "import identity, journal, graph, course, director; assert len(graph.MIGRATION_STATES)==3 and len(graph.BINDING_STATES)==5 and len(director.PROTOCOL_STEPS)==13 and len(journal.ENTRY_KEYS)==24 and not hasattr(graph,'accept_migration'); print('15B preconditions match')"
15B preconditions match
```

All three freeze records carry their own `## Frozen at` heading and none
carries `## Freeze withheld`. The one deviation found is resolved in the plan
text rather than worked around in code, `blueprint.py` does not exist, and
**Phase 15B may proceed** from 15B-01 Task 2.
