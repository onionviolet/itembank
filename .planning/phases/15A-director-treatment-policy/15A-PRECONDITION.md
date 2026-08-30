# 15A precondition check

## Why this check exists

`15A-RESEARCH.md`'s Critical Caveat: every 14A and 14B signature in the 15A
research document and pattern map was read from **plan text, not from source**,
because neither module existed when Phase 15A was planned on 2026-08-18. Plans
15A-01 through 15A-06 therefore assert constants they had no way to verify, and
this task exists to find out where the landed surface differs before an
executor writes a line of `director.py` against a number that was never true.
The caveat arrived exactly on schedule: one assertion diverged, it was the one
whose plan-text source had itself been superseded, and taking the plan
literally would have deleted a frozen key.

## What was checked

Run 2026-08-30 on Darwin 27.0.0 arm64, Python 3.14.6.

**Step 1, the five dependency modules import.**

- `identity`, `journal`, `discovery`, `graph`, `course`, `course_package` all import: **ok**

**Step 2, the frozen 14A constants.**

- `identity.OBJECT_KINDS` is the six-member tuple in order: **ok**
- `identity.RIGHTS_OPERATIONS` is the seven-member tuple in order: **ok**
- `identity.RIGHTS_STATES` equals `("granted", "denied", "unknown")`: **ok**
- `identity.rights_state(None, "transform")` returns `"unknown"`: **ok**
- `identity.rights_granted({"transform": "GRANTED"}, "transform")` returns `False`, exact ASCII, no case folding: **ok**
- `journal.OPERATION_TYPES` has exactly six members: **ok**
- `"reconcile"` and `"migrate"` are in `journal.RECORD_TYPES`, `"agent_operation"` is not yet: **ok**
- `len(journal.ENTRY_KEYS)` equals the plan's asserted count, and `"agent"` is not in it: **divergent** (see Deviations found)
- All nine named callables are callable on their modules: **ok**

**Step 3, the frozen 14B constants.**

- `graph.TREATMENT_KINDS` is the eleven-member tuple in the exact order given: **ok**
- `graph.BINDING_STATES` equals `("covered", "thin", "missing", "conflicting", "unknown")`: **ok**
- `len(graph.TREATMENT_RIGHTS)` equals `11` and every value is a member of `identity.RIGHTS_OPERATIONS`: **ok**
- `graph.EDGE_CONFIDENCES` equals `("high", "medium", "low", "unknown")`: **ok**
- `graph.EDGE_TYPES` equals the four-member tuple in order: **ok**
- `graph.COURSE_GRAPH_VERSION` equals `1`: **ok**
- `course.COURSE_SIDECAR_FILENAME` equals `"course-graph.md"`, which is what the recorded `D-14B-1` option-a implies: **ok**
- All ten named callables are callable on their modules: **ok**

**Step 4, the shipped Phase 8 surface.**

- `model_adapter.ADAPTER_CODES` count and `TRANSPORT_REGISTRY` keys: **ok**

**Step 5, both freeze records exist.**

- `14A-FREEZE.md` contains `## Frozen at 14A`: **ok**
- `14B-FREEZE.md` contains `## Frozen at 14B`: **ok**

## Deviations found

One, in step 2. It is a divergence between **two planning records**, not
between the plan and the code, and the code was correct throughout.

| | Value | Source |
|---|---|---|
| Plan text 15A-01 asserted | `len(journal.ENTRY_KEYS) == 22`, last key `message` | `14A-02-PLAN.md`, "Artifacts this phase produces" |
| Landed and frozen | `len(journal.ENTRY_KEYS) == 23`, last key `rights` | `14A-FREEZE.md`, "The twenty-three journal entry keys" |

`ENTRY_KEYS` has held twenty-three members since `77b27e9`, the only commit
that ever touched it. So there was never a regression and never a moment when
the tuple had twenty-two members: `14A-02-PLAN.md` is simply the older of two
records and 14A shipped a key its own plan text did not list. `14A-FREEZE.md`
is the authority, and it names `rights` explicitly among the frozen twenty-three.

**Why this was a halt and not a rounding error.** 15A-01's acceptance criteria
required `ENTRY_KEYS` to end at exactly twenty-three with `"agent"` last, and
its `must_have` claimed the phase's whole `journal.py` diff is two lines.
Against a landed twenty-three-key tuple, an executor working literally could
satisfy "exactly twenty-three, `agent` last" only by **deleting `rights`**, the
key 14A-03 records the rights state of every journal entry through. A frozen
key would have been removed to satisfy a stale count. The first run of this
task on 2026-08-30 halted here and wrote nothing, which was the correct
outcome.

**Resolution, recorded 2026-08-30 by a planning pass over 15A-01 through
15A-06 against `14A-FREEZE.md` and `14B-FREEZE.md`.** `rights` stays. Every
15A number shifts by one and nothing else changes:

| File | Was | Now |
|---|---|---|
| `15A-01-PLAN.md` step 2 | precondition asserts `22` | asserts `23` |
| `15A-01-PLAN.md` verify block | `len(journal.ENTRY_KEYS)==22` | `==23` |
| `15A-01-PLAN.md` acceptance | `23` members, first `22` unchanged | `24` members, first `23` unchanged, ending in `rights` |
| `15A-01-PLAN.md` Task read_first | points at `14A-02-PLAN.md` for a "twenty-two-member" tuple | points at `14A-FREEZE.md` for the twenty-three-member tuple |
| `15A-05-PLAN.md` behavior block | `ENTRY_KEYS` still `23` | still `24` |
| `15A-05-PLAN.md` journal coupling check | "exactly twenty-three members" | "exactly twenty-four members" |
| `15A-VALIDATION.md` 15A-01 row | `len(journal.ENTRY_KEYS)==22` | `==23` |

**The two-line diff claim survives untouched.** 15A-01's `must_have` says
`journal.py`'s whole-phase diff is exactly two lines: one new `RECORD_TYPES`
member and one new `ENTRY_KEYS` member. That claim was never about the total
count, so a pre-state of 23 rather than 22 does not touch it. `OPERATION_TYPES`
still stays at exactly six, and `agent_operation` remains a record type rather
than a file operation.

**The root cause, so it does not recur.** 15A-01's `read_first` block directed
the planner to `14A-02-PLAN.md`, and step 2 was written from that file exactly
as instructed. The instruction was the defect: a plan is a proposal and a
freeze record is the accepted truth, and where they disagree the freeze record
wins. The read_first pointer has been repointed. Plans 15A-02, 15A-03, 15A-04
and 15A-06 were grepped for the same numbers and carry none.

## Dated result line

**2026-08-30.** Steps 1 through 5 were re-run in full after the planning pass
and every one passes.

```
step 1: modules present
step 2: 14A surface matches
step 3: 14B surface matches; COURSE_SIDECAR_FILENAME = course-graph.md
```

```
python3 -c "import model_adapter; print(len(model_adapter.ADAPTER_CODES), sorted(model_adapter.TRANSPORT_REGISTRY))"
14 ['hosted_cli', 'openai_compatible']
```

```
python3 -c "import identity, journal, graph, course; assert len(graph.TREATMENT_KINDS)==11 and len(graph.BINDING_STATES)==5 and len(journal.ENTRY_KEYS)==23 and 'agent_operation' not in journal.RECORD_TYPES; print('15A preconditions match')"
15A preconditions match
```

The one deviation found is resolved in the plan text rather than worked around
in code, `director.py` still does not exist, and **Phase 15A may proceed** from
15A-01 Task 2.
