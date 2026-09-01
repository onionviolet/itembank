# 17B-02 evidence: binding, inventory, and the object and authority record (G2)

Recorded 2026-09-01 by plan 17B-02 Task 1, run from the repository root.
`python` is not on PATH on this machine, so every command uses `python3`
(the recorded 16C-precedent deviation). One further recorded deviation:
the flow is driven through the frozen 14A and 14B module surfaces
(`journal.op_link`, `course.create_course`, `course.bind_source`,
`journal.rebuild_registry`) invoked by a transcribed python3 script,
because neither freeze record freezes a CLI command for discovery or
binding and `OPERATION-CONTRACT.md` lists that command surface as pending
(14A/14B). The module functions used below are the frozen items those
records name; no command was invented.

## The command and its script, verbatim

Invocation, from the repository root (`PYTHONPATH=.` because the script
file lives outside the repository tree; the modules imported are this
repository's own):

```
PYTHONPATH=. python3 t1_binding.py
```

Script contents, verbatim:

```python
# 17B-02 Task 1: the frozen 14A/14B discovery and binding flow over the
# fixture course. Run from the repository root with python3 (python is not
# on PATH; recorded deviation). Every call below is a frozen 14A or 14B
# module surface named in 14A-FREEZE.md or 14B-FREEZE.md / 15B-FREEZE.md.
import json
import course, graph, identity, journal

BASE = "course_fixture_17b"
GRANTED = dict(identity.rights_default(),
               read="granted", quote="granted", transform="granted")

# 1. Mint the course object and its sidecar through the frozen
#    compare-and-swap path (14B course.create_course -> journal.commit_operation).
rec = course.create_course(BASE, "Aldrasse Fen Ecology 101", "human", "weibao")
print("course minted:", rec["object_id"], "revision", rec["revision"])

# 2. Link the four fixture artifacts (scope, objectives, two sources) as
#    durable objects. op_link mints identity without touching bytes
#    (14A journal.op_link, write_target=False). The two sources carry an
#    explicit rights declaration by their owner (Weibao authored them for
#    this repository); unknown rights stay restrictive on everything else.
links = {}
for rel, kind, rights in (
        ("scope.md", "course", None),
        ("objectives.md", "objective", None),
        ("sources/fen_hydrology_field_notes.md", "source", GRANTED),
        ("sources/lantern_moss_survey.md", "source", GRANTED)):
    r = journal.op_link(BASE, kind, rel, "human", "weibao", rights=rights)
    links[rel] = r["object_id"]
    print("linked %-40s kind=%-9s object_id=%s fingerprint=%s..."
          % (rel, kind, r["object_id"], r["fingerprint"][:16]))

# 3. Build the graph: the unit container, the seven objectives with their
#    cited statements, and the two source rows (14B graph.* + course.write_course).
read = course.read_course(BASE)
doc = read["doc"]
unit = graph.add_container(doc, "unit",
                           "Unit 3: Peat Hydrology and the Lantern Moss Cycle")
OBJECTIVES = [
    ("O3.1 Explain why the Aldrasse fen is minerotrophic and how lateral mineral inflow sets its porewater chemistry and plant community",
     "sources/fen_hydrology_field_notes.md", "basin-overview"),
    ("O3.2 Describe the acrotelm and catotelm structure and predict water table response to a storm versus seasonal recharge",
     "sources/fen_hydrology_field_notes.md", "water-table-dynamics"),
    ("O3.3 State the drought threshold (water table more than 25 cm below surface) and how vegetation registers an excursion",
     "sources/fen_hydrology_field_notes.md", "water-table-dynamics"),
    ("O3.4 Explain why peat accumulation tracks water table position and estimate profile age from an accumulation rate",
     "sources/fen_hydrology_field_notes.md", "peat-accumulation-and-decay"),
    ("O3.5 Describe the lagg zone's two roles and the station A1 conductance condition that triggers a resample",
     "sources/fen_hydrology_field_notes.md", "mineral-inflow-and-the-lagg-boundary"),
    ("O3.6 Sequence the four phases of the lantern moss annual cycle and the early-summer hinge",
     "sources/lantern_moss_survey.md", "annual-cycle"),
    ("O3.7 Use lantern moss vitality scores as a hydrological instrument tied to the dipwell threshold",
     "sources/lantern_moss_survey.md", "hydrological-sensitivity"),
]
obj_ids = []
for statement, src, anchor in OBJECTIVES:
    o = graph.add_objective(doc, statement, container=unit["id"])
    obj_ids.append((o["id"], src, anchor))
    print("objective", o["id"], statement.split(" ", 1)[0])
for rel in ("sources/fen_hydrology_field_notes.md",
            "sources/lantern_moss_survey.md"):
    graph.add_source(doc, links[rel], rel)
w = course.write_course(BASE, doc, read["fingerprint"], "human", "weibao")
print("sidecar written: revision", w["revision"])

# 4. Bind each objective to its cited source section. bind_source consumes
#    the read right and refuses on unknown (RIGHTS-01); these succeed only
#    because step 2 granted read on the two sources.
for oid, src, anchor in obj_ids:
    r = course.bind_source(BASE, oid, links[src],
                           locator="%s#%s" % (src, anchor),
                           state="covered", confidence="high",
                           actor_kind="human", actor_name="weibao")
    print("bound", oid, "->", "%s#%s" % (src, anchor),
          "revision", r["revision"])

# 5. Derived views rebuild from canonical files.
#    (a) objects.json is a disposable projection: delete it, rebuild from
#        the append-only journal log alone, compare.
import os
reg_path = journal.registry_path(BASE)
before = json.load(open(reg_path))
os.remove(reg_path)
journal.rebuild_registry(BASE)
after = json.load(open(reg_path))
print("registry rebuild from journal log alone: identical =", before == after)
#    (b) the outline projection re-derives from the sidecar bytes.
outline = graph.outline_projection(course.read_course(BASE)["doc"])
print("outline projection rebuilt, %d lines, first: %r"
      % (len(outline.splitlines()), outline.splitlines()[0]))

# 6. The object table for the evidence record.
registry = journal.read_registry(BASE)
for oid, row in sorted(registry.items(), key=lambda kv: kv[1]["path"]):
    print("object %s kind=%-9s rev=%s path=%s"
          % (oid, row["kind"], row["revision"], row["path"]))
```

## Output, verbatim

```
course minted: ba070378d35d44e7 revision 1
linked scope.md                                 kind=course    object_id=d035bddef2d84eff fingerprint=sha256:25120a059...
linked objectives.md                            kind=objective object_id=95abc1ccd3e241f9 fingerprint=sha256:6f1d1de83...
linked sources/fen_hydrology_field_notes.md     kind=source    object_id=8bd25c20ceaa4e20 fingerprint=sha256:1161d0819...
linked sources/lantern_moss_survey.md           kind=source    object_id=5c5bc6b17baa44c6 fingerprint=sha256:2d9284081...
objective 67b9a4f0cfab4cb8 O3.1
objective 98b0c52691954d27 O3.2
objective 2589f5292d234a4d O3.3
objective a46a877388f54575 O3.4
objective 4f3456e288a44412 O3.5
objective 1db0edbda647453a O3.6
objective ae08d09cd3714164 O3.7
sidecar written: revision 2
bound 67b9a4f0cfab4cb8 -> sources/fen_hydrology_field_notes.md#basin-overview revision 3
bound 98b0c52691954d27 -> sources/fen_hydrology_field_notes.md#water-table-dynamics revision 4
bound 2589f5292d234a4d -> sources/fen_hydrology_field_notes.md#water-table-dynamics revision 5
bound a46a877388f54575 -> sources/fen_hydrology_field_notes.md#peat-accumulation-and-decay revision 6
bound 4f3456e288a44412 -> sources/fen_hydrology_field_notes.md#mineral-inflow-and-the-lagg-boundary revision 7
bound 1db0edbda647453a -> sources/lantern_moss_survey.md#annual-cycle revision 8
bound ae08d09cd3714164 -> sources/lantern_moss_survey.md#hydrological-sensitivity revision 9
registry rebuild from journal log alone: identical = True
outline projection rebuilt, 11 lines, first: '# Aldrasse Fen Ecology 101'
object ba070378d35d44e7 kind=course    rev=9 path=course-graph.md
object 95abc1ccd3e241f9 kind=objective rev=1 path=objectives.md
object d035bddef2d84eff kind=course    rev=1 path=scope.md
object 8bd25c20ceaa4e20 kind=source    rev=1 path=sources/fen_hydrology_field_notes.md
object 5c5bc6b17baa44c6 kind=source    rev=1 path=sources/lantern_moss_survey.md
```

The journal itself (`course_fixture_17b/_journal/`) is durable local
record, gitignored per the repository's standing rule; this transcript is
the repository-side evidence, and the flow above is re-runnable from the
canonical files alone.

## The object and authority record (G2)

One row per fixture artifact, plus the sidecar the flow minted and the two
authored-unit files plan Task 3 adds (their rows recorded here once minted;
see the addendum at the bottom). Ownership vocabulary is
`AGENTS.md` section "Object and authority model" / `OPERATION-CONTRACT.md`.

| artifact | durable object (id, kind) | owner | authority over its content | source of truth |
|---|---|---|---|---|
| `scope.md` | `d035bddef2d84eff`, `course` | course builder (Weibao) | course builder defines scope within source and rights limits; reviewer accepts | the file's own bytes; fingerprint `sha256:25120a059...` in the journal registry |
| `objectives.md` | `95abc1ccd3e241f9`, `objective` | course builder (Weibao) | course builder; every objective statement cites a source locator, so the cited source constrains it | the file's own bytes plus its `[SRC:]` locators into the two sources |
| `sources/fen_hydrology_field_notes.md` | `8bd25c20ceaa4e20`, `source` | learner/owner (Weibao; synthetic, authored for this repository) | the source itself; nothing downstream may alter it; rights read/quote/transform granted, all other operations unknown and restrictive | the file's own bytes |
| `sources/lantern_moss_survey.md` | `5c5bc6b17baa44c6`, `source` | learner/owner (Weibao; synthetic) | same as above | the file's own bytes |
| `course-graph.md` (minted by this flow) | `ba070378d35d44e7`, `course` | course builder | every durable write goes through `journal.commit_operation` with an expected fingerprint; the runtime and agents never own it | the sidecar's own bytes; the journal holds its revision history |

Derived and disposable, never a second source of truth:
`_journal/objects.json` (rebuilt from the log alone above, `identical =
True`) and the outline projection (re-derived from the sidecar bytes
above). Both demonstrations are in the transcript.

## Egress record (17B-CONTEXT D-09)

No step of this task made a hosted-model call. Nothing left this machine:
the flow is module calls over local files. G11's egress row will record
not-applicable with this reason unless a later wave makes a hosted call at
call time.

## Addendum after Task 3 (authored unit objects)

Recorded after Task 3 minted the unit files through the same frozen path:

| artifact | durable object (id, kind) | owner | authority | source of truth |
|---|---|---|---|---|
| `unit3_lesson.md` | `36157b3e10cb46e5`, `lesson` | course builder (drafted by an agent under draft-and-review; accepted state is the committed file) | lesson truth never derives from learner notes; keyed material excluded by authoring rule and checked by `lesson.authored_key_disclosure` | the file's own bytes |
| `unit3_bank.md` | `1672ba231fd446ee`, `bank` | course builder | the runtime alone settles scoring and disclosure of its keyed fields; `id-assign` is the only direct bank writer | the file's own bytes; item `[ID:]`/`[HASH:]` lines carry item identity |
