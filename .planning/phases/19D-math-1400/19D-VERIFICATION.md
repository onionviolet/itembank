# Phase 19D verification

**Status:** closed by explicit scope waiver on 2026-09-08. The failed Agent
proposal, new Math 1400 sitting, and dependent recovery observations remain
deferred and unclaimed.

## Observed acceptance results

- PASS: exact OpenStax title and section read on 2026-09-07. Current licence, attribution, and model-ingestion restriction recorded per title.
- PASS: external course `math-1400-openstax`, object `95dbccc7716142cc`, created through the published 19A dispatcher. The captured source, two objectives, source bindings, and one justified direct-reading treatment are durable.
- PASS: visible shelf to course to Agent navigation used opaque route identity and visible controls. Current-area and back-home controls were present.
- FAIL: the repaired local backend did not produce a parseable Agent proposal. No stored proposal, reviewed diff, acceptance journal entry, undo proof, or retained generated treatment exists.
- NOT RUN: Learn, Practice, Test, evidence, next activity, private note, source return, changed-context item, exact resume, real sitting, export, isolated restore, and F-LOSS replay. These depend on the failed proposal gate and are not claimed.

## Focused code gates

`python3 tests/model_adapter_roundtrip.py`: PASS after the bounded transport changes.

`python3 tests/agent_operation_roundtrip.py`: PASS, including configured instruction transit, the bounded lesson contract, strict proposal response shape, proposal identity, conflict refusal, acceptance, and byte-identical undo against the loopback fixture.

The live provider still returned `adapter.malformed_response`. Deterministic fixtures passing does not convert the live result to green.

## Evidence and denominators

- Source capture: 1 of 1 required titles verified.
- Objectives: 2 of 2 created and source-bound.
- Direct readings: 1 of 1 justified.
- Live Agent proposals accepted: 0 of 1.
- Real sittings completed for this OpenStax course: 0 of 1.
- Assessment responses, unanswered, and pending prose: not applicable because no sitting began.
- Recommendation: unavailable. No AGENT-03 next activity is inferred from zero responses.
- Uncertainty: backend malformed-output cause remains unresolved after three bounded attempts. Human visual, screen-reader, and instructional acceptance remains owed.

## Scope decision recorded 2026-09-08

The user deferred local AI and said, "we can skip the sitting for now." Reach
may therefore close for sequencing purposes without converting any NOT RUN or
FAIL result above into PASS. Resume the sitting only when the user reopens that
validation leg. The runtime remains the sole scorer and disclosure authority.

## Gate decision

The task-level suites, quick preflight, full preflight, export, and restore gates were not run after the live blocker. Running broad gates cannot prove the missing proposal or sitting. Phase 20 may proceed, but these results stay deferred until their named triggers are met.

Large modules were sampled symbol-first: `surfaces/daemon.py`, `surfaces/agent_operation.py`, `model_adapter.py`, and `tests/course_ops_roundtrip.py`. No whole-file claim is made for them.
