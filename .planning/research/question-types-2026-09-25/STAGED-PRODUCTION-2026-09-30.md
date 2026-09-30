# Staged production runtime evidence, 2026-09-30

The user authorized parallel implementation of the staged answer/reason and
polynomial checker lanes. This record covers the staged runtime lane. Human
interaction acceptance, packaging and installed application acceptance remain
separate gates.

## Implemented behavior

Staged declarations bind two stable MC child identities to the exact bank bytes,
accepted declaration revision and adjacent selected positions. Selection validates
complete units and restores authored answer/reason order before the selection
event is emitted. Filters, count and focus that split a case refuse with a
recovery action. PAIR does not imply a staged activity.

The existing cursor and response list remain authoritative. A committed wrong
answer advances to reason exactly once. Both children require the current
activity, child identity and deterministic submission token; malformed options,
forged stage and stale commitment are refused. Practice exposes the committed
answer at reason and releases two separate feedback entries after reason.
Formal submissions preserve the existing deferred-feedback policy. Report and
learner-evidence projections withhold active case outcomes, and each completed
case retains its own release state when another case opens.

Session v4 upgrades v1/v2/v3 without inferring a case. Verified response events
carry additive activity/revision/child/stage linkage and exact event identity in
the resumable row. Thread and process owner locks serialize canonical next,
action and report operations. Reconciliation repairs an exact durable child
event after a failed session write without scoring again. Missing binding,
changed bank, divergent session/evidence rows and ambiguous event histories
freeze mutation and preserve the accepted files.

## Paths and verification

Lane changes: `runtime.py`, `selection.py`, `surfaces/session.py`, `evidence.py`,
`schemas/session.schema.json`, `schemas/response.schema.json`,
`tests/staged_production_roundtrip.py`, and the current-version assertion in
`tests/subject_loop_roundtrip.py`. Runtime/session/evidence/schema ownership
was explicitly transferred to the polynomial lane after its initial tests
passed, so those files contain both lanes' additive integration.

Initial stable verification on 2026-09-30:

- `python3 tests/staged_production_roundtrip.py`: seven tests passed, including
  separate concurrent processes with identical and conflicting commitments,
  injected failures before append and after append/before session replace,
  legacy upgrades, schema validation and formal disclosure.
- `python3 tests/agent_roundtrip.py`: passed.
- `python3 tests/lesson_run_roundtrip.py`: passed.
- `python3 tests/subject_loop_roundtrip.py`: passed.

The staged suite was then extended to ten tests for completed case feedback
while a second case opens, all hint entry points, stale reason replay into a
following ordinary item, preceding ordinary practice retries and whole-case
exclusion. Its final verification result is recorded below after integration.
Schema checks assert an empty validation-error list, rather than relying on an
exception.

## Recovery and remaining gates

Restore the accepted bank/session/evidence revision to resolve a binding or
ambiguous-history conflict. Reload `next` after an interrupted exact event
append to repair the resumable cursor and response row; a stale replay remains
refused and cannot create a second attempt. Changes are uncommitted and confined
to source and synthetic test data. Baseline source snapshots are stored outside
the scanned Python trees as `.py.txt` files.

No commit, push, package/build, installation, real learner file access or full
preflight ran in this lane. Large modules were read by symbol and function
windows, rather than whole-file inspection. Browser detours, live daemon
restart and broader route integration belong to the client/root lanes. This
record does not claim human accessibility or installed-application acceptance.

## Final staged lane verification

`python3 tests/staged_production_roundtrip.py`: eleven tests passed after shared
checker integration, final lane run 0.262 seconds. This includes ordinary
practice retries before a case, ordinary items after it, two cases, per-case
released evidence, all hint entry points, whole-case exclusion, actual asserted
schema validation, both concurrent-process scenarios, and exact crash recovery
with the scorer patched to fail if called again. The expired timed case test
confirms changed binding freezes `next`, `action` and `report` without writing
the timeout transition first.

Independent symbol-window review caught two additional integration edges and
returned them to the shared runtime owner: stale reason replay into a following
ordinary item, and timeout mutation before binding validation. Both fixes now
pass the production suite. Direct model-hint binding validation was also
identified and assigned to the shared runtime owner; broader final verification
is recorded by that lane and the coordinator.

## Recoverable lane snapshots

S-start snapshots preserve the dirty source bytes observed before this lane
edited them. These are recovery evidence, not clean upstream versions. Restore
only a reviewed diff against them because shared runtime files subsequently
received the checker lane's changes. Local copies use `.py.txt` extensions to
avoid discovery by the Python suite scanner.

```text
b7e9729478756e5aa79da80145156a5558f70b9c497c4fafd5f816bfce52170b  .reasonix/staged-checker-production-20260930/staged-baseline/evidence.py.txt
6d08c7ebc6f6588bfccb8d409c1e67267f334401223f4ec01b2580fee8b7a797  .reasonix/staged-checker-production-20260930/staged-baseline/runtime.py.txt
e52ce8a3bb0c40d934b6ba2df2499a09eba4bdeff8ba4fd8ad85d35a93bc9d94  .reasonix/staged-checker-production-20260930/staged-baseline/selection.py.txt
f58965936ac0a04daf205142591a3699f1c8e4f7d69d6f804bdfffcff8e1c2a4  .reasonix/staged-checker-production-20260930/staged-baseline/session.py.txt
```

S-final lane-owned files at release:

```text
9c059b75b2c92f9c9c803c26ebf56cdf525e29d947c7701bdb1e7c109eac2612  tests/staged_production_roundtrip.py
5cccdbd34ecf852a83c4dd6e434f0fbaea7b009080a68a62312dc1bb4a6bb8be  selection.py
```

The coordinator owns final combined runtime, session, evidence and schema
fingerprints. After the checker owner's final hint/timeout hardening,
`python3 tests/staged_production_roundtrip.py` again passed all eleven tests
(0.272 seconds). No production edits occurred during this evidence follow-up.
