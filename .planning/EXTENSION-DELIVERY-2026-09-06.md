# Extension delivery: measured improvements at existing seams

Status: EXT-01 through EXT-03 are committed. Three follow-up repair edits are
present in the shared worktree and still require isolated verification and
publication. EXT-04 is routed to the UI foundation, 19B, and 19E. EXT-05
remains deferred.
Owner: the extension maintainer for the repair packet. The UI foundation, 19B,
and 19E own their EXT-04 proofs.
Origin: the 2026-09-06 DSH comparison and implementation-plan request in
`USER-VISION-INBOX.md`. This extends IL-20260816-01, whose standing pattern
already adopted feature plugins at named seams. It does not reopen the
swappable-authority rejection IL-20260815-04.

## Decision and evidence

D1. Use first-party registration as the next delivery improvement. Do not
introduce Cordis, dynamic imports, an event bus, a package manager, or a new
frontend to standardize a registry. Benefit is an inference until EXT-01 passes.
The target is lower extension maintenance cost, not faster scoring or inference.

F1. DSH composes services, typed events, and reversible registrations through
Cordis. Its core services are replaceable through configuration. This is current
primary-source evidence, checked 2026-09-06:
[DSH architecture](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md).
DSH is a design reference, not a dependency or a compatibility target.

F2. The repository already supports a third model transport through
`model_adapter.TRANSPORT_REGISTRY` and `invoke`. The existing
`test_stub_third_backend_registration` in `tests/model_adapter_roundtrip.py`
exercises that claim. Do not rebuild this extension point.

F3. Source adapter functions and versions are declared separately in
`source_adapters.ADAPTER_REGISTRY` and `ADAPTER_VERSIONS`. CLI choices and daemon
validation consume the function dictionary. The frozen source-locator schema
enumerates adapter identities. Adding a registry entry alone therefore does not
make an arbitrary new medium publishable. Existing exception-injection tests
temporarily replace a dictionary entry, so compatibility requires preserving it.

F4. `capabilities.register` already validates semantic capability profiles and
returns a new registry. It owns richer learning metadata. A transport descriptor
must not become a second capability catalogue. The two selected UI compositions
already have a shared-foundation owner in `UI-CHARACTER-AUDIT-2026-09-06.md`.

## Next packet and order

Finish and verify the three known EXT repair edits as one isolated packet after
live-tree ownership is clear. EXT-01 through EXT-03 already proved the shared
first-party descriptor across source and model seams and published accurate
capability diagnostics. The next architectural proof is EXT-04 through its
existing owners. Reach proves Agent-tab and MCP composition. The post-Reach UI
slice proves both selected presentation profiles plus one capability adapter
over the same semantic foundation. Do not edit shared source files while
another writer owns them.

EXT-04 becomes executable only through the bounded 19B, 19E, and future UI
packets. EXT-05 remains a seed because its package and isolation decisions are
unsettled. This follows AGENT-WORKFLOW section 9 and avoids inventing generic
loader machinery before real compositions expose a shared need.

| ID | Result and owner | Dependencies and promotion gate |
|---|---|---|
| EXT-01 | Validated first-party registration pilot, extension maintainer | Existing source adapters. Pass the exact packet gates before adoption. |
| EXT-02 | Reuse the proven descriptor for model transports, model-adapter owner | EXT-01 proves a useful common shape. Preserve the existing third-backend test and zero-network defaults. Stop if adapting the shape requires special cases or breaks mutation-based test isolation. |
| EXT-03 | Extension author guide and accurate capability diagnostics, capability-manifest owner | EXT-02 proves reuse across two seams. Reuse `tools/capabilities_manifest.py` and existing capability disclosure. Separate registered, configured, available, and disabled. Do not create a second discovery catalogue or claim a provider is installed from metadata alone. |
| EXT-04 | Presentation profiles, appearance themes, UI capability adapters, Agent-tab composition, and MCP projection use their existing owners | The two selected profiles exercise shared semantic roles and primitives. UI adapters declare fallback, unavailable behavior, accessibility behavior, migration, and recovery. Agent and MCP tools derive from existing operation and parity maps. Generalize machinery only after two registrations at one seam prove a missing shared primitive. |
| EXT-05 | Installable external packages, supply-chain and runtime-maintenance owners | Deferred until there is a concrete external package need and accepted isolation, compatibility, acquisition, and recovery design. First prototype metadata-only inspection without importing package code. |

Each promoted packet must state exact symbols, exclusions, a narrow acceptance
command, migration impact, and an undo path. Do not expand all seeds at once.

## External-package design questions retained for EXT-05

External Python code executes with process privileges. A manifest field that
claims read-only or no-network behavior is not enforcement. Do not describe
trusted in-process first-party registration as a sandbox.

Before external execution, settle package identity, pinned version and digest,
host API compatibility, dependency conflicts, exact grants, enforcement boundary,
activation failure, and installed versus enabled state. Installation and update
need expected-base comparison, validated atomic acceptance, a journal, rollback,
and a recovery mode that can start without the package. Discovery must read
metadata without executing code. Runtime fetching is prohibited by the current
SUPPLY-CHAIN-POLICY section 6. Changing that policy requires its own decision.

Active sittings retain their implementation and authority for their lifetime.
Do not implement hot replacement during an assessment. Preserve package-version
provenance without making an unreviewed evidence-schema change. An exported
course must disclose missing capabilities and remain study-usable offline.
Packaging is not complete until clean offline restore identifies every loss.

## Scope, authority, and recovery

The user authorized plans, not implementation in this session. Planning reads
are this repository and public DSH documentation. No learner material is sent
to DSH. Planning writes are this document, EXT-01, the inbox capture, and the
append-only ledger update. Existing uncommitted edits belong to their writers.

EXT-01 changes first-party code declarations only. Canonical source files,
banks, courses, settings, sessions, evidence, accepted revisions, and grants
retain their owners and formats. Registry maps are process-local derived data.
The existing import path continues to validate and journal accepted content.
Metadata does not grant reading, execution, egress, or assessment authority.
Removing the pilot restores the prior declarations without data migration.

## Readiness and review

The review sampled AGENT-WORKFLOW, SOURCE-TO-COURSE, the active Reach state,
PLANNING-DIRECTIVES, the named ledger entries, the UI foundation section,
SUPPLY-CHAIN-POLICY, and the source/model/capability symbols cited above.
It did not read the complete source, model, daemon, or test modules.

The bounded readiness check passes for planning EXT-01: one owner, no cycle,
no new schema or dependency, a synthetic extension tracer, preserved authority,
explicit degradation, and a removable implementation. Full external-plugin
readiness remains unproved. No performance or token saving is claimed.

The user-vision drift check routes both exact statements to the existing plugin
decision. The ledger retains external packages and live reload as future work.
No rejection is deleted or reopened. Skills are unchanged. Execution evidence
belongs in the existing packet, not a second status system.

## Planning verification

Checks run on 2026-09-06 against the shared working tree:

- `python3 tests/model_adapter_roundtrip.py`: exit 0, including the existing
  synthetic third transport and no-score envelope check.
- `python3 tests/source_adapters_roundtrip.py`: exit 0, including source
  schema compatibility, rights refusals, CLI and route parity, and ASR
  unavailability. OCR used stubs. No live OCR verification is claimed.
- `python3 scripts/preflight.py --quick`: exit 0. All selected gates passed.
  The broad Python suite, dirty-tree gate, and JS suite were explicitly skipped.
- `python3 scripts/vision_audit.py`: exit 0. No missing interpretation,
  planning-effect field, named path, downstream reference, or inbox disposition.
  It reports ten older relationship-field soft findings, outside this packet.
- `git diff --check`: exit 0. New plan prose contains no em dash, semicolon,
  or machine-specific path. This is a bounded planning check, not verification
  of the unimplemented registry helper.
