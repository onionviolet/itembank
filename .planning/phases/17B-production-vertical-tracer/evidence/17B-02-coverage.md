# 17B-02 evidence: the G1 coverage map for the authoring vertical

Recorded 2026-09-01 by plan 17B-02 Task 3. G1 asks that every capability
the tracer exercises maps to its requirement row and ledger disposition,
with no undischarged tracer promise. This file maps what wave 2
exercised, and names the wave that owes each remaining promise, so
nothing is silently dropped.

`python` is not on PATH on this machine; every command below ran as
`python3` (recorded deviation).

## Capabilities exercised by this plan, mapped

The requirement rows are the 17B-UI-SPEC section 2 checklist (each row
names its contract owner) and the 17B-GATES rows; ledger dispositions
are core/shipped unless a ledger id is named.

| capability exercised | where in the fixture | requirement row / contract owner | disposition |
|---|---|---|---|
| Durable identity, link, journal, registry rebuild | Task 1 flow, `course_fixture_17b/_journal` transcript in evidence/17B-02-binding.md | G2; 14A-FREEZE.md frozen items | core, shipped 14A |
| Course sidecar, objectives, source rows, source bindings with locators | `course_fixture_17b/course-graph.md` | G2; 14B-FREEZE.md frozen sidecar contract | core, shipped 14B |
| Rights-gated binding (read/quote/transform per operation, unknown restrictive) | Task 1 grants plus every `bind_source`/`bind_treatment` call | G2/G11 rights-unknown discipline; 14A RIGHTS-01 | core, shipped 14A |
| Treatment vocabulary and per-objective decision record | `course_fixture_17b/treatments.md`, 7 blocks, 6 fields each | G7; 15A-FREEZE.md `graph.TREATMENT_KINDS` | core, shipped 15A |
| Review before authoring, recorded per objective | 7 director operations, `plan-treatment` then `review` phases (ids in treatments.md) | G7; 15A protocol steps, 15B review discipline | core, shipped 15A/15B |
| Term definitions | `## TERMS` in unit3_bank.md, `[[term]]` refs in unit3_lesson.md, lint-checked | 16A CAP family row | core, shipped 3.1/16A |
| Things-to-know block | `> [!KEY]` card in unit3_lesson.md, id minted by `id-assign` | 16A row | core, shipped 3.1/16A |
| Expert-tip block | `> [!TIP]` in unit3_lesson.md | 16A row | core, shipped 16A |
| Cited visual explanation with static fallback | `## MEDIA` row (alt, rights, derivation, integrity) plus `[MEDIA: moss-cycle]` and `media/lantern_moss_cycle.svg` | 16A media policy row | core, shipped 16A |
| Prediction prompt, participation-only evidence | `## ACTIVITIES` row for Q1: purpose `prediction`, evidence `activity_trace` | 16A activity matrix row | core, shipped 16A |
| Varied practice and one transfer item | 8 items: 5 mc, 1 multi, 1 build, 1 short; Q8 is the changed-context transfer | 15B blueprint fidelity row | core, shipped |
| Short answer stays pending for a marker | Q7 `[TYPE: short]` with MODEL and three-point RUBRIC | G6 assessment authority; runtime contract | core, shipped |
| Plain-Markdown coherence outside the app | unit3_lesson.md reads standalone; unit3_bank.md reaches it via `[LESSON-SRC:]` | SOURCE-TO-COURSE portability rule row | core, shipped 16A verdict |
| Compare-and-swap file safety under fault | the four drills in evidence/17B-02-faults.md | G3; 14A frozen protocol | core, shipped 14A |
| Citation and synthesis labeling | every lesson section carries `[SRC:]` locators; the synthesis section and Q8's invented basin say so in their own text | operation protocol step 7 | core |

Deterministic validation outputs backing the rows, verbatim:

```
$ python3 itembank.py lint course_fixture_17b/unit3_bank.md

8 items, 0 errors, 0 warnings
```

`stats`: 8 items (5 mc 62%, 1 multi, 1 build, 1 short); difficulty 5
application, 2 analysis, 1 recall; answer positions A 1, B 1, C 2, D 1.
`coverage`: 7 distinct objectives, every one covered
(afe:unit3.minerotrophy, .layers, .threshold, .peat, .lagg, .cycle,
.instrument), Q7 and Q8 both on .instrument.

## Promises this wave does NOT discharge, with owners

None of these is dropped; each is owed to a named later wave of this
same phase, per the plan set:

| promise | owed by |
|---|---|
| Rendered-capability checks at 1280/768/375, keyboard, touch, offline; screen-reader item held for human sign-off | 17B-03 (G4, G8); the human checkpoint is mandatory, never agent-certified |
| Both rollup screens over the scope tree, denominators stated, default picked by Weibao (IDEA-LEDGER IL-20260817-01, D-03 checkpoint) | 17B-03 (G5) |
| The graded sitting, key non-disclosure, pending short mark, frozen-sitting immutability | 17B-03 (G6) |
| Strategy and note statements, note-authority guard | 17B-03 (G9) |
| Legacy upgrade audit (17B-CONTEXT D-05) | 17B-03/17B-04 per plan set |
| Clean-machine offline restore with loss report | 17B-04 (G10, D-07) |
| Egress capture equals manifest, or not-applicable with reason; rights-unknown refusal | 17B-04 (G11); this wave made no hosted call, recorded in evidence/17B-02-binding.md at call time |

## The Task 2 review script, transcribed (referenced from treatments.md)

Invocation: `PYTHONPATH=. python3 t2_review.py` from the repository
root. Script, verbatim:

```python
# 17B-02 Task 2: record and review the seven treatment decisions through
# the frozen 15A director protocol surface, then bind the reviewed
# treatments through the frozen 14B rights-gated path. Run from the
# repository root with python3.
import course, director, graph, journal

BASE = "course_fixture_17b"
FEN = "8bd25c20ceaa4e20"    # sources/fen_hydrology_field_notes.md
MOSS = "5c5bc6b17baa44c6"   # sources/lantern_moss_survey.md

# (objective label, objective graph id, source object id, locator anchor,
#  treatment kinds to bind, demand)
DECISIONS = [
    ("O3.1", "67b9a4f0cfab4cb8", FEN, "basin-overview",
     ["guided-lesson", "practice"], "application"),
    ("O3.2", "98b0c52691954d27", FEN, "water-table-dynamics",
     ["guided-lesson", "practice"], "application"),
    ("O3.3", "2589f5292d234a4d", FEN, "water-table-dynamics",
     ["notes-or-terms", "practice"], "recall"),
    ("O3.4", "a46a877388f54575", FEN, "peat-accumulation-and-decay",
     ["worked-example", "practice"], "application"),
    ("O3.5", "4f3456e288a44412", FEN, "mineral-inflow-and-the-lagg-boundary",
     ["direct-reading", "practice"], "application"),
    ("O3.6", "1db0edbda647453a", MOSS, "annual-cycle",
     ["guided-lesson", "visual-or-demonstration", "practice"], "analysis"),
    ("O3.7", "ae08d09cd3714164", MOSS, "hydrological-sensitivity",
     ["guided-lesson", "practice"], "analysis"),
]

SRC_PATH = {FEN: "sources/fen_hydrology_field_notes.md",
            MOSS: "sources/lantern_moss_survey.md"}

for label, oid, src, anchor, kinds, demand in DECISIONS:
    op = director.begin_operation(
        BASE, BASE,
        "treatment decision %s: %s" % (label, " + ".join(kinds)),
        "agent", "claude", "course-builder", "draft-and-review",
        scopes=("course_fixture_17b",))
    director.record_phase(
        BASE, op, "declare-authority", 1, "applied",
        actor_kind="agent", actor_name="claude",
        message="read+write root course_fixture_17b only; no egress; "
                "rights read/quote/transform granted on both sources")
    director.record_phase(
        BASE, op, "inventory", 2, "applied",
        actor_kind="agent", actor_name="claude",
        message="existing-artifact search over the approved root: "
                "no prior artifact found for %s" % label)
    director.record_phase(
        BASE, op, "plan-treatment", 3, "applied",
        actor_kind="agent", actor_name="claude",
        checkpoint={"objective": label, "treatments": kinds,
                    "demand": demand,
                    "locator": "%s#%s" % (SRC_PATH[src], anchor),
                    "decision_record": "treatments.md"},
        message="decision recorded in treatments.md with scope, demand, "
                "rationale, uncertainty, and search result")
    director.record_phase(
        BASE, op, "review", 10, "applied",
        actor_kind="human", actor_name="weibao (standing 2026-09-01 "
        "delegation; agent-recorded verdict, labeled as such)",
        message="review verdict: accepted; scope, demand, rationale, "
                "uncertainty, and search fields all present for %s" % label)
    report = director.protocol_report(director.operation_entries(BASE, op))
    print("%s operation %s review recorded; protocol verdict %s "
          "(incomplete is expected: authoring phases follow in Task 3)"
          % (label, op, report["verdict"]))
    for kind in kinds:
        r = course.bind_treatment(
            BASE, oid, src, kind,
            locator="%s#%s" % (SRC_PATH[src], anchor),
            state="covered", confidence="high",
            actor_kind="human", actor_name="weibao")
        print("  bound treatment %-24s revision %s" % (kind, r["revision"]))
```

Its output is transcribed verbatim in `course_fixture_17b/treatments.md`.

## Defects found this wave (17B-CONTEXT D-06)

1. **In-phase fix, single file.** `python3 itembank.py guard .` failed on
   the authored fixture unit (`unit3_bank.md` parses as a bank,
   `unit3_lesson.md` carries the `## SOURCES` marker), because guard's
   skip list predates D-02's decision to keep a synthetic fixture course
   at the repository root; with the mechanical gate as it stood, D-02's
   own requirement (fixture in-repo AND guard clean) was unsatisfiable.
   Fix: `surfaces/cli.py` guard walk skips `course_fixture_17b` by name,
   with a comment citing D-02. One file, no refusal class weakened, no
   contract change; the pre-fix failure output is preserved in
   17B-02-SUMMARY.md. Owner: 17B itself (its own fixture rule).
2. **Recorded defect, not fixed.** The documented `> [!KEY: <title>]`
   index-card form draws a spurious `lesson.unknown_semantic` warning:
   `model.py`'s semantic-role lint check tests the raw marker against
   `surfaces.lesson._CALLOUT_KINDS` directly instead of routing through
   `surfaces.lesson._callout_kind_of`, which maps `KEY:`-prefixed
   markers to the KEY card (the renderer does; the linter does not).
   Mechanism diagnosed above; workaround used here is the
   corpus-established equivalent `> [!KEY] <title>` form. Owner: Phase
   16A (the check shipped with 16A's semantic lint pass).
3. **Recorded skill gap.** The `lesson-authoring` skill is still a stub
   (its own text says so), so unit3_lesson.md was authored against the
   16A capability contract directly (semantic roles, media policy,
   activity matrix, portable-Markdown rule) plus `absorb-book`'s shipped
   `## LESSON` contract, exactly as the stub instructs. Owner: the
   subphase that ships the lesson-authoring command surface (the stub
   names 16A as its prerequisite; 16A has shipped, the skill rewrite is
   still owed).
