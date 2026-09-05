# What the vision still needs: a measured gap pass and four forks

**Date:** 2026-09-05

**Prompt:** Weibao, in chat, 2026-09-05: consider what we truly want and need
to fulfil the user vision, look online as needed, and look for options.

**Scope:** a measured reading of shipped state against the verbatim vision
record, then four decision forks with options and a recommendation each. This
is input, not a plan and not a requirement. `USER-VISION.md` remains the record
of intent; nothing here reinterprets it, and every quotation below is already
in that file.

**Method.** Read `SOURCE-TO-COURSE.md` whole, the `USER-VISION.md` entries for
2026-08-20, 08-21, 08-24, 08-26 and 08-27, the roadmap phase checklist, and
`STATE.md` current position. Then measured the shipped surface directly rather
than reading about it: the CLI subparser table, `surfaces/daemon.ROUTES` and
`API_ROUTES`, `SURFACE_PARITY`, module sizes, the settings file, and the import
graph of the agent seam. Every number below came from running something.

## 1. The finding, in one sentence

What the vision still needs is not more contracts. It is **doors and use**: the
source-to-course engine is built and almost entirely unreachable, the agent
seam is built and unplugged, the in-product model backend is switched off, and
two of the three real courses do not exist while the semester runs.

## 2. What was measured

### 2.1 The engine is real

387 KB of Python across `blueprint.py`, `course.py`, `course_package.py`,
`director.py`, `discovery.py`, `graph.py`, `identity.py`, `journal.py`,
`notes.py`, `progress_claims.py`, and `strategies.py`, under 107 test files.
Phases 14A through 17A are frozen. 17B's gates pass except the human legs, and
17C's restore drill passes. None of that is in doubt and none of it is the
problem.

### 2.2 The engine has almost no door

- **The JSON API is 15 routes.** All fifteen are assessment, lesson, source
  import, or first-run shelf actions: `start`, `next`, `submit`, `hint`,
  `teach`, `interact`, `report`, `override`, `lesson-complete`,
  `rubric-review`, `export_audio`, `lesson/run`, `source/import`,
  `source/recheck`, `shelf`.
- **Every `/course/` route is a GET.** `/course/<id>`, its six areas
  (`learn|practice|test|map|sources|build|evidence`), and one lesson view.
  There is no POST anywhere under `/course/`. The Build and review area, which
  `SOURCE-TO-COURSE.md` defines as where AI proposals, diffs, citations,
  approval, rejection, and undo live, is read-only over HTTP.
- **The CLI has 47 top-level commands and not one is course-shaped.** There is
  no `course`, `discover`, `bind`, `objective`, `treatment`, `blueprint`,
  `package`, `graph`, `accept`, or `agent`. `shelf` turns out to be four
  first-run walkthrough actions (`advance_walkthrough`,
  `remove_sample_course`, `replay_walkthrough`, `skip_walkthrough`).
  `source import` extracts one file to Markdown plus a locator sidecar, which
  is step one of binding and stops there.

**Inference.** You cannot create, bind, or accept anything in a course from
either surface a person or an agent client can reach. The 17B tracer drove the
Python modules directly, which is why it could pass while this remains true: a
tracer proves a seam, and it says nothing about whether the seam has a door.
This is the same class of defect as the 2026-08-21 sitting, where
`/lesson/<stem>` returned 200 and nothing linked to it, scaled up from one
route to a milestone.

### 2.3 The agent seam is built and unplugged

`surfaces/agent_operation.py` implements the run, propose, accept state
machine that 17A-07 owed: four states, one sentence of copy for each of the
fourteen adapter codes, exactly one `journal.commit_operation` per accepted
proposal, and an undo path, with `tests/agent_operation_roundtrip.py` passing.

Its only importer outside itself is `surfaces/visual_fixture.py`, the
screenshot generator. It is bound to no HTTP route and no CLI command.

**Inference.** Weibao wrote on 2026-08-21 that the Agent tab and
`journal.commit_operation` were "two programs in one window" and that "the
skill buttons on that page run nothing". 17A-07 built the machine that joins
them and did not connect it to a door either. The claim moved from
"unimplemented" to "implemented and unreachable", which is better but is not
what was asked for.

### 2.4 The in-product model backend is off

`itembank.json` sets `model_backend.active` to `""`. Per
`schemas/settings.schema.json`, an empty `active` "disables model calls
entirely". The single registered profile is a local Ollama endpoint naming a
model that reads as a placeholder.

**Inference.** Every AI action in this project's history has been an external
agent (Claude Code, Codex) editing files in a repository, which is a different
thing from the operation protocol the product defines: declare intent, inventory,
plan treatment, draft, validate, preview, bounded diff, review, accept
atomically, journal. The product's own AI path has never been run in anger in
this working copy. `seed` refuses by name without a backend, and so would the
director.

### 2.5 The use record has not moved

`STATE.md`: one real sitting, 2026-08-24, EMT unit 1, in a course root outside
this repository. No Math 1400 course. No CSCI 1100 course. "Every other session
in the record is a fixture or an agent." The 2026-08-14 entry noted the live
fall courses begin "within weeks"; that was three weeks ago.

**Inference.** This is the condition Weibao already diagnosed on 2026-08-20,
still true: "the reason it reads as nothing is that no phase output ever
reached the learner: twelve phases closed without the product being used on
real material once." Twelve has become thirty-two.

## 3. Fork 1: how the course engine gets a door

**The question.** Nothing in section 2.2 is a design disagreement. The engine
needs an operating surface, and the only real question is which surface comes
first.

**Option A, HTTP POST routes plus CLI twins.** Extend `API_ROUTES` with the
course operations and mirror each into `ROUTE_CLI` and `SURFACE_PARITY`, whose
existing test already fails on a route without a twin. Cost is bounded because
the handlers exist; what is missing is dispatch, request schemas, and the
parity rows. Serves the learner, the CLI user, and an agent client at once.

**Option B, the MCP surface first (Phase 999.3, promoted 2026-08-17, zero
plans).** Its success criterion 1 is decisive and is easy to miss: the MCP
server exposes **one tool per `API_ROUTES` entry**, with `inputSchema` read off
disk from the same `schemas/*.json` the CLI uses. That means 999.3 built today
would expose fifteen assessment tools and no course tools. **999.3 is not
blocked on MCP work. It is blocked on there being routes worth exposing.**
Option A is its prerequisite, and once A lands, B is close to free.

**Option C, leave it to skills and file edits.** The status quo: an external
agent reads and writes course files directly. It works, it is how everything
got built, and it is exactly the second-authority shape the architecture
exists to prevent, because a file edit bypasses `journal.commit_operation`,
the expected-base-fingerprint check, the bounded diff, and the undo record.

**Online check.** The MCP specification's current revision is still
**2026-07-28**, the revision 999.3 was designed against, so that design basis
has not gone stale. That revision removed the initialize handshake in favour of
a stateless core, which 999.3's success criterion 6 already anticipates by
retaining a legacy `initialize` path. Two extensions in it are worth knowing
about but not chasing: Tasks, for long-running work, which maps onto the
existing durable-jobs and Activity view; and MCP Apps, server-rendered UI
inside an agent client, which is interesting only after there is something to
render. Precedent already exists in-repo: `scripts/ocr_mcp.py` is a working MCP
server, so the transport is not new ground here.

**Recommendation.** A, then B, in that order, and treat B as the acceptance
test for A rather than as separate work. If the tool table generated from
`API_ROUTES` can build a course, the routes are right.

## 4. Fork 2: turn on a backend, and which one

**The question.** Section 2.4 leaves the product's AI path untested. Weibao's
cost constraint is on the record twice, "costing me erxtra $$$" and "how to get
more per token", and so is the measured answer: 5.1 billion tokens for
25.33 dollars, 99.24 percent of it cache-hit input.

**Option A, local first.** The 7900 XTX is already the recorded local path.
What has changed since that config was written is that ROCm 7.2 (March 2026)
reached parity with CUDA out of the box for Ollama, LM Studio, llama.cpp, and
vLLM on RDNA 3, so the setup cost that made this a someday item is largely
gone. Reported throughput on 24 GB at Q4: roughly 40 tok/s for a 27B, roughly
72 tok/s for a 26B mixture model, roughly 96 tok/s for an 8B. Qwen 3 32B is the
quality pick that still fits.

**Option B, a hosted profile.** One profile with `secret_env`, already
supported by the adapter, no new code. Better reasoning, per-token cost, and
the recorded accepted risk that hosted models see item text.

**Option C, both, active by workload.** The adapter already normalizes
transports behind one `invoke`, and switching is a settings change.

**Inference.** The work the product's AI path actually needs to do is
high-volume and mostly mechanical: extract objectives from a chapter, propose a
treatment per objective, draft a bank, run the lint and fix loop, propose a
next action. That profile is a good fit for a local model and a poor use of
paid tokens, and it is the half that must "degrade, never block". The judgment
work, which is planning and review, is where a hosted model earns its price,
and that half is already being done by an external agent and does not need the
in-product path at all.

**Recommendation.** A, and set `active` to it. The immediate value is not
quality, it is that turning it on is the only way to discover what the director
and the seeding loop actually do on real material, which no test has told
anyone. Keep B registered as a profile so the comparison is a settings change.

## 5. Fork 3: the two courses that do not exist

**The question.** EMT has real material. Math 1400 and CSCI 1100 have none, and
the semester is running.

**Math 1400.** Already dispositioned this morning as `IL-20260905-05`: bind an
OpenStax or LibreTexts algebra title, read the licence per title rather than
assuming it from the publisher, and use direct reading as the treatment where
the source is clear. This is the cheapest real course to stand up because the
source is open, machine-readable, and needs no scraping.

**CSCI 1100.** The AI-use ban is an accepted risk already on the books and
applies to hosted and local paths alike. That does not make the course
impossible; it constrains what the course is for. A CSCI course built as
reading, `check` items the learner writes themselves, and retrieval practice
over concepts is not AI assistance on graded coursework. A course that drafts
answers to assignments is. The line is worth stating before the course exists
rather than after.

**Inference.** Standing up Math 1400 is also the highest-value test of Fork 1
and Fork 2 that exists, because it exercises discovery, binding, objective
mapping, treatment choice, generation, and blueprint in one pass on material
nobody has hand-fitted to the tracer.

**Recommendation.** Build Math 1400 with the doors from Fork 1 and the backend
from Fork 2, in that order, and let the defects come from that rather than from
another design session. Weibao's ten minutes of clicking on 2026-08-16
produced a defect twelve phases of framework tests had not.

## 6. Fork 4: what ends the next milestone

**The question.** Weibao's own open question from 2026-08-20, still unanswered:
"whether the roadmap's remaining phases should be re-ordered so that each one
ends in something the learner can open, rather than in a freeze gate that can
go green without anyone using the product."

**Observed fact.** 17B is the milestone exit and it is a gate record, G1 to
G11, over a fixture course. It went green while section 2.2 was true.

**Option A, keep gate-shaped exits.** They are auditable, an agent can run
them, and they caught real defects, including the five silent losses 17C found.

**Option B, exits measured in use.** A milestone closes when a stated amount of
real use has happened: a course a person built with the shipped doors, N
sittings across the real subjects, defects logged from those sittings.

**Option C, both, with different jobs.** Gates stay as the correctness floor.
The milestone exit becomes a use threshold, so a green gate over a fixture can
never again be the last word before the next milestone opens.

**Recommendation.** C. Concretely: the next milestone exits on a real Math 1400
course built through the product's own doors, sat at least once, with its
defects recorded, and the existing gate machinery kept underneath it unchanged.

## 7. A recommended shape, if one milestone follows

Not a plan. The order is what matters, and it is the order Fork 1 implies.

1. **Doors.** Course operations as POST routes with CLI twins under the
   existing `SURFACE_PARITY` discipline. Nothing new is designed; what exists
   gets an entrance.
2. **Plug the seam.** `surfaces/agent_operation.py` behind one of those doors,
   so an accepted agent proposal is one `journal.commit_operation` with a
   visible undo, from the Agent tab and from an agent client alike.
3. **Backend on.** A local profile made active, and the director and seeding
   loop run against real material for the first time.
4. **Math 1400, for real**, built through 1 to 3.
5. **The MCP tool table**, generated from the routes 1 created, as the proof
   that "an agent can operate everything the learner can operate" is true
   rather than aspirational.
6. **Exit on use**, per Fork 4 option C.

Steps 1, 2 and 5 add no new durable object, no second parser, no second
scorer, and no second evidence store. Step 3 is a settings change plus whatever
the first real run exposes. Step 4 is content work. That is a milestone whose
every step ends in something openable, which is what the 2026-08-20 entry asked
for.

## 8. What this pass deliberately does not recommend

- **More research.** The Phase 16 corpus is fourteen streams and a synthesis,
  and section 2 found nothing it got wrong. The gap is not knowledge.
- **New format surface.** Nothing above needs a change to the bank format, the
  lesson contract, the item types, or the scorer.
- **Revisiting the visual system.** 17A is frozen and its owed leg is a human
  accessibility pass, not a redesign.
- **A second frontend.** The 2026-08-20 open question about a TypeScript
  component library over the same daemon routes is not answered here and does
  not need to be: routes that do not exist cannot be consumed by any frontend,
  so Fork 1 comes first either way.
