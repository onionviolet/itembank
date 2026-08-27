# Decision packet: the four Phase 14B answers

Drafted 2026-08-27 by the orchestrating session so that Phase 14B waves 4 to 6
can start the moment Weibao decides. Nothing is executed until he does.

Three of these are blocking checkpoints already written into the 14B plans, with
their options and recommended defaults authored at planning time. This packet
does not invent options; it lifts each plan's own option set, states the cost,
and puts the four together so they can be answered in one sitting. The fourth is
a confirmation of a stand-in an agent already made on his behalf.

**Why an agent is not answering these.** Each plan carries the same sentence:
"Do not proceed with a silent default. An unanswered checkpoint stops the wave."
One stand-in was made on 2026-08-26 under a standing overnight authorization and
was recorded as **provisional**, because the call is rated one-way and no agent
may quietly convert a one-way call into a settled one. Two stand-ins on one
phase would be the pattern that rule exists to prevent.

**How to answer.** Reply with four lines, for example
`D-14B-1 confirm / 04 a / 05 a / 06 a`. Any answer that differs from the
recommended default has its exact plan-edit consequence listed below, so no
answer is more work to act on than another.

---

## 1. D-14B-1: confirm or overturn the provisional sidecar decision

**Status:** already acted on. Waves 1 to 3 are built on it. This asks whether it
stands.

**The recorded answer, option-a.** Phase 14B writes
`<course-root>/course-graph.md` as a separate file and never opens the Phase
13.9 `<course-root>/course.md` stub for writing. `course.migrate_stub()` reads
the stub, emits the new sidecar, journals the operation, and leaves the stub
byte-identical, which `tests/graph_roundtrip.py` asserts by comparing bytes
before and after.

**Why the agent chose it.** `13.9-CALIBRATION.md` records the walking
skeleton's course root as `~/Documents/itembank-courses/emt-unit-1`, outside
this repository, with `course.md` holding a real hand-approved objective map for
a live autumn course, covered by no fixture and no repository backup. The
in-place upgrade path would have a tool rewrite exactly that file. The refusal
path is safe but forces the map to be retyped by hand, which is the manual
re-entry the phase exists to remove.

**What it costs.** Two course-shaped files sit in the course root until a later
phase retires the stub, and each needs a header line pointing at the other.

**If you confirm:** nothing changes; the provisional marker is replaced with
your answer and the plans proceed as written.
**If you overturn:** waves 1 to 3 are already built on it, so this is a rework
of shipped code and should be said explicitly rather than implied.

**Recommended: confirm.**

---

## 2. 14B-04 Task 1: is `migrate` an operation type or a record type?

**Rated one-way.** A migration proposal is appended to an append-only journal
and written into a sidecar that later subphases read.

**The apparent conflict, which the plan asks be explained rather than left to
decide the answer.** `OPERATION-CONTRACT.md` lists link, import, copy, move,
edit-in-place, supersede, migrate, and synchronize as distinct operations. That
sentence is about the operations being **distinct**, not about the membership of
`journal.OPERATION_TYPES`. Option-a keeps both true.

| | Effect |
|---|---|
| **option-a** RECOMMENDED | `migrate` joins `RECORD_TYPES` with an eight-field proposal (`migration_id`, `kind`, `from`, `to`, `rationale`, `state`, `actor`, `timestamp`, which is the `## Migrations` column set plan 14B-01 already writes, so no sidecar column changes). `OPERATION_TYPES` stays at exactly six, so the 14A freeze is untouched. `RECORD_TYPES` grows the way it already grew twice in 14A. |
| **option-b** | `migrate` becomes a seventh `OPERATION_TYPES` member. One flat vocabulary, but `14A-FREEZE.md` names "the six operation names" in its Frozen list, so this is a **freeze amendment**: every assertion expecting six must be updated and an amendment section appended to the 14A freeze record. |
| **option-c** | No journal record; the sidecar row is the only record. Smallest change, but a migration becomes the only durable course operation `journal.replay` cannot reconstruct. |

**Recommended: option-a.** It is the only one that adds the capability without
either amending a freeze or putting a durable operation outside the journal.

---

## 3. 14B-05: what is in `manifest.json`, and is a package a directory or an archive?

| | Effect |
|---|---|
| **option-a** RECOMMENDED | Plain directory tree, `zip` as optional transport. `manifest.json` carries `schema_version`, `package_id`, `created`, `course_object_id`, `state`, `entries`, `loss_report`; each entry carries `object_id`, `kind`, `revision`, `relpath`, `fingerprint`. A human can open and read the package without this tool. |
| **option-b** | Archive by default. One file to hand over, but the traversal guard becomes load-bearing on every restore rather than on an opt-in path, and a human cannot read a package without unpacking it. |
| **option-c** | BagIt proper, with the `bagit` dependency. **This one stops the plan:** `14B-RESEARCH.md`'s Package Legitimacy Audit was skipped because the phase proposes zero external packages, and that audit must exist before any package is installed. Answering option-c means recording the answer and re-running the gate protocol, not proceeding. |

**Recommended: option-a.** It matches the standing rule that a package is a
plain directory tree first and an archive only as optional transport, which
`course_package.py`'s docstring already states as shipped behaviour.

---

## 4. 14B-06 Task 3: which 14B interfaces freeze?

Asked only if the three freeze legs are green. If a leg is red the freeze is
withheld on that ground and this is not asked at all.

| | Effect |
|---|---|
| **option-a** RECOMMENDED | Freeze the vocabularies **and** the record shapes: sidecar file name and section order, the seven table column sets, the four-name edge vocabulary and its three closed field sets, the unknown-type downgrade rule, the eleven treatment kinds and their rights mapping, the five migration kinds and three states. Copy and layout stay changeable. |
| **option-b** | Freeze vocabularies only; record shapes stay open through Phase 15A. Cheaper to change when a real course first exercises them, but 15A and 16A would compose onto shapes that may still move. |
| **option-c** | Withhold the freeze deliberately even on three green legs, until a real course has run through the graph. Phase 15A depends on 14B in the ROADMAP subphase table, so this blocks 15A by choice. |

**Recommended: option-a**, with one caveat worth weighing. The 2026-08-26
teardown work found that plan text written against an unbuilt tree goes stale
fast, and option-a freezes seven column sets before Phase 15A has run a real
course through them. Option-b is the more honest answer if you expect the
column sets to move. The recommendation stays option-a only because 15A and 16A
both compose onto these shapes and would otherwise build on sand.

---

## The fifth decision, unrelated and still waiting

`.planning/DECISIONS-17A04-DRIVER-2026-08-25.md`, the Playwright browser-harness
supply-chain approval for `tools/visual_qa.py`. Independent of 14B, drafted two
days ago, and blocking the last of 17A's eight plans. Worth answering in the
same sitting since it is one yes or no.

---

## What happens after the answers

`.planning/NEXT-2026-08-27.md` has the sequencing. In short: 14B waves 4 to 6
execute, 14B freezes, and 14C, 15A and 16A unblock. Phase 16B, and with it the
course shelf that has been mocked up twice this week, sits behind 16A and does
not move until then.

Phase 14C planning does **not** depend on any of these four answers and can
proceed in parallel; it depends on 14A only, which is frozen, and it shortens
the critical path because it blocks the source-binding half of 14B.
