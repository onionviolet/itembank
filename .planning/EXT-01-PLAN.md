# EXT-01: validated first-party source registration

Status: ready implementation packet, not executed.
Depends on: the existing source-adapter registry, not a future plugin framework.
Context: `EXTENSION-DELIVERY-2026-09-06.md`, D1 and F2 to F4.

## Handoff contract

GOAL: a maintainer declares a built-in source adapter's function, version,
purpose, fallback, and check in one row. Invalid declarations fail before use.
The CLI, daemon, extraction results, and accepted source format behave as before.

OWNER: the extension maintainer resolves material contract contradictions.
BUILDER: one coding agent using this packet and `.planning/EXEC-CONTEXT.md`.
VERIFIER: a reviewer inspects the diff and test evidence instead of trusting
the builder's completion sentence. Independent delegation is not required.

SCOPE: new `extension_registry.py`, registration declarations in
`source_adapters.py`, new `tests/extension_registry_roundtrip.py`, and a short
extension recipe in the README source-adapter section. Record results below.

DO NOT TOUCH: model.py, runtime.py, evidence.py, journal.py, schemas, settings,
CLI or daemon dispatch, model transports, capability profiles, UI, dependencies,
real banks, and other writers' edits. Do not rename or move extraction functions.
Do not add plugin installation commands or imply any exist.

TOOLS NEEDED: Python 3 and Git for inspection. No network, model call, external
package, or learner data is required by the new test. Existing required suites
may report missing optional dependencies under their established rules.

RETURN: exact changed paths, command exit codes and skipped legs, a diff-based
comparison with the baseline, unresolved failures, and the next action.
Do not commit or push unless the user explicitly requests it. When authorized,
use one atomic commit for this packet with only its named files.

## Precondition checks

Run `git status --short` and identify concurrent edits before writing. Read
symbol windows, not whole modules:

```text
source_adapters.py: ADAPTER_REGISTRY, ADAPTER_VERSIONS, _extract, build_sidecar
tests/source_adapters_roundtrip.py: the ADAPTER_REGISTRY assignments and finally cleanup
surfaces/cli.py: choices=sorted(source_adapters.ADAPTER_REGISTRY)
surfaces/daemon.py: adapter membership validation
schemas/source_locator.schema.json: adapter enum and adapter_version pattern
capabilities.py: register, only to avoid duplicating its semantic ownership
```

Run `python3 tests/source_adapters_roundtrip.py` before editing. Preserve that
baseline exit status and any skipped optional-dependency checks. Do not repair
unrelated failures. If source_adapters.py has another writer, use an isolated
checkout with its dependency state preserved or return the exact conflict.

## Settled implementation

T1. Add a small stdlib-only helper in extension_registry.py. It is an internal
code API, not a published manifest or a loader. Define `RegistrationError`
as a ValueError subclass and `build_registry(entries)` returning three ordinary
fresh dictionaries: handlers, versions, and descriptions. Preserve entry order.

Each entry is a dictionary with exactly these fields:

| Field | Required value |
|---|---|
| name | Lowercase identifier matching `[a-z][a-z0-9_]*` |
| version | String matching `[0-9]+\.[0-9]+\.[0-9]+` with a full match |
| handler | A callable already imported by repository code |
| capability | A nonempty, non-whitespace plain string describing purpose |
| fallback | A nonempty, non-whitespace string naming degraded behavior |
| check | A nonempty, non-whitespace string naming the owning test command |

Reject non-dictionary entries, missing or extra fields, duplicate names,
invalid types, malformed versions, non-callable handlers, and blank metadata.
Raise RegistrationError with the entry index and offending field or duplicate
name. Never invoke a handler or evaluate the check string during registration.
Build local dictionaries and return only after every entry passes. Do not
mutate inputs or global state. An empty input produces three empty maps.
Descriptions contain copied metadata excluding handler. Keep only scalar string
metadata, so copies cannot share a mutable nested object. Do not add generic
dependency injection, priorities, events, hot reload, imports from strings,
filesystem discovery, or permission enforcement claims.

T2. Replace only the current registry declaration block in source_adapters.py
with ordered SOURCE_ADAPTER_ENTRIES and one build_registry call producing
ADAPTER_REGISTRY, ADAPTER_VERSIONS, and SOURCE_ADAPTER_DESCRIPTIONS.
Preserve the exact ten names, order, and function identities. Preserve version
1.0.0 for existing adapters and 0.0.0 for ASR. Describe ASR as registered but
unimplemented. Its fallback is supplying a transcript through the existing
transcript adapter. Read each other adapter's refusal behavior before describing
its fallback. A missing dependency must remain unavailable, never successful
empty extraction. Use the existing source-adapter suite as the check value.

Leave _extract and build_sidecar unchanged. Preserve ADAPTER_REGISTRY as a
mutable dict because tests inject failures through it. Do not expose that test
technique as an external installation mechanism. Handler and version maps are
derived at module import from one declaration list. Production code must not
mutate those maps later. This pilot intentionally avoids immutable-map churn.

T3. Add the standalone roundtrip test. Use the repository's stdlib executable
script pattern and a nonzero exit on failure. Test behavior, not source text.

| Case | Observable acceptance |
|---|---|
| Valid entries | Name order, function identity, versions, and copied descriptions agree with input. |
| Malformed entries | Each T1 rejection class raises RegistrationError with useful location. |
| Atomic construction | A valid row followed by a bad row leaves inputs and a previously built registry unchanged. |
| No execution | A handler that raises if called is never invoked by build_registry. |
| Registration extension | A synthetic `stub` provider is added by appending one row to a local entry list. A fixed helper dispatches `handlers[name](raw_bytes, options)` before and after the addition without edits. |
| Actual adapter | Invoke the registered built-in text handler on synthetic bytes and compare its complete tuple with the existing text extractor on the same bytes. |
| Compatibility | All ten built-in names, order, callable identities, and versions match the captured baseline. Existing failure injection and source roundtrips still pass. |

The stub proves registration and dispatch only. It must not write a locator
sidecar under an unknown adapter ID. The published schema is a separate gate.
Do not weaken that schema to make the synthetic tracer look production-ready.

T4. Add a short README recipe beside source adapter documentation: implement
the existing extraction callable, add a declaration row, add fidelity and
refusal tests, and inspect the existing schema before proposing a new medium.
Explain first-party registration and the lack of an external loader. Do not
advertise performance savings, sandboxing, or arbitrary drop-in media support.

## Verification and falsifiers

Run the new test first:

```bash
python3 tests/extension_registry_roundtrip.py
python3 tests/source_adapters_roundtrip.py
python3 scripts/preflight.py
```

A full preflight at the final revision may supply the source and extension suite
results instead of a redundant second run. Record whether optional adapters were
actually exercised. A skipped live OCR call is not verified OCR compatibility.
The full preflight is required for implementation handoff, not for authoring
this Markdown plan. Existing dirty-tree failures must be attributed explicitly.

Inspect the final diff. There must be zero edits to consumer dispatch, schemas,
accepted-content writes, scoring, disclosure, or evidence. Compare old and new
registry keys, ordering, function identities, and versions. The new helper must
contain no project-domain imports and no I/O. Reject any new dependency.

Adopt only if declaration metadata has one owner, invalid declarations are
caught, and the synthetic addition requires no helper or consumer edits. If
these gates require compatibility shims, custom branches per provider, or more
than this one small registration helper, return the concrete failed criterion
and keep the prior production declarations. Do not widen the design yourself.
Elapsed time and retry counts may be recorded as measurements. Do not infer
cost savings from fewer lines or a passing stub test.

## Recovery and completion

No durable learner object changes and no migration is needed. Restore only this
packet's source-adapter declaration hunk and README hunk, then remove the two
new files if they are still exclusively owned by this packet. Never reset an
entire shared file or checkout. If committed with authorization, revert that
single packet commit after checking for dependent work.

Completion updates this section with the exact commands and results. A separate
SUMMARY.md is unnecessary. EXT-02 remains a seed until the verifier confirms
the helper earned reuse. No learner UI or accessibility claim is made here.

Execution evidence: targeted verification passed after recovery. `python3
tests/extension_registry_roundtrip.py` exited 0. `python3
tests/source_adapters_roundtrip.py` exited 0, with the existing PDF
FontBBox warning. `git diff --check` exited 0. Full `python3
scripts/preflight.py` was run before recovery and failed on pre-existing
summary-contract violations, stale capabilities/config state, daemon timeout
flakiness, and its clean-tree gate removed untracked EXT-01 files and
uncommitted EXT-01 hunks. The full preflight therefore is not evidence against
the restored implementation and was not rerun. No optional live OCR call was
exercised.
