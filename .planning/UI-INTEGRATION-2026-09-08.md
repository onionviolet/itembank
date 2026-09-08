# Accepted learner UI integration, 2026-09-08

## Decision and scope

The accepted greenfield prototype is now the product identity for Itembank's
normal learner-facing app. The production daemon remains the app. The prototype
directory remains design evidence and is not copied in as a second frontend.

## Reconciliation

| Prototype experience | Production owner retained | Production route |
|---|---|---|
| Personal desk and course library | course shelf read model | `/` |
| Objective-led course path | course outline and area state | `/course/<id>` |
| Source-grounded reading | accepted lesson and source bindings | `/course/<id>/learn`, `/lesson/<bank>` |
| Practice and feedback | runtime public item and scorer | `/course/<id>/practice`, `/quiz/<bank>` |
| Evidence and exact resume | evidence log and session files | `/course/<id>/evidence`, `/report` |
| Proposal review and undo | agent operation and journal | `/course/<id>/agent` |

The old narrow gray card presentation and plain course shelf styling are
superseded. Their routes, semantic HTML, native controls, typed unavailable
states, and working actions are retained beneath one new shared shell. The two
Phase 20 presentation recipes remain behavior-free composition adapters. They
no longer define competing product identities because both render inside the
accepted shell.

No prototype localStorage records, answer keys, demo scores, source revisions,
model availability, or progress were imported. No parser, scorer, evidence
store, route family, or mutation path was added.

## Responsive workflow boundary

One responsive product serves both layouts from the same canonical state. Wide
desktop windows use a persistent navigation rail and multi-column workspace.
Narrow windows use bottom navigation, a focused single-column activity, and
stacked secondary context. CSS presentation changes do not create a second
session, note store, scorer, or disclosure policy.

The narrow layout proves reflow in the desktop-local browser only. It does not
prove phone access to desktop-local data, secure remote connectivity, offline
packaging, or cross-device synchronization. Those remain separate architecture
and are not authorized by this UI integration.

## Verification record

Automated checks and visual evidence belong to the implementation return for
this task. Human touch-device, screen-reader, 200 percent text, 400 percent
zoom, and aesthetic acceptance remain owed until a person performs them. Live
local-model proposal success and the four-subject parity backend are separate
deferred gates and are not claimed by this integration.
