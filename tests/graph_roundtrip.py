#!/usr/bin/env python3
"""Proves the thinnest real path through Phase 14B end to end: one synthetic
objective is minted into a course sidecar, related by one edge, written
through the frozen 14A compare-and-swap path, projected to a plain-Markdown
outline, exported as a package, and restored on a destination that never saw
the original.

The point of this test is that the whole path is proven before any layer is
widened. Every degraded state the path can reach is asserted here too: a
future schema version, a malformed section, a stale compare-and-swap write, an
interrupted export, a corrupted payload, and a traversing package entry.

Standard library only, runnable as `python tests/graph_roundtrip.py`.
"""
import json, os, random, shutil, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import identity                                              # noqa: E402
import journal                                               # noqa: E402
import graph                                                 # noqa: E402
import course                                                # noqa: E402
import course_package                                        # noqa: E402
import model                                                 # noqa: E402
import schema_validate                                       # noqa: E402
import fixtures.corpus_14b as corpus_14b                     # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def eq(got, want, what):
    if got != want:
        fail("%s: want %r, got %r" % (what, want, got))


def raises(fn, exc_type, code, what):
    """Assert `fn()` raises `exc_type` carrying `.code == code`, and return
    the raised exception so the caller can assert on its message."""
    try:
        fn()
    except exc_type as err:
        if getattr(err, "code", None) != code:
            fail("%s: want code %r, got %r (%s)"
                 % (what, code, getattr(err, "code", None), err))
        return err
    except Exception as err:                                 # noqa: BLE001
        fail("%s: want %s, got %s: %s"
             % (what, exc_type.__name__, type(err).__name__, err))
    fail("%s: nothing was raised" % what)


def _inject_unknown_column(text, section, column, value):
    """Add one unrecognized column to the end of one section's table, the way
    a later build of this format would. Used to prove an older build rewrites
    a newer build's file without dropping what it does not understand."""
    out, inside, idx = [], False, 0
    for line in text.split("\n"):
        if line.startswith("## "):
            inside = (line == "## " + section)
            idx = 0
            out.append(line)
            continue
        if inside and line.startswith("|"):
            if idx == 0:
                out.append(line + " " + column + " |")
            elif idx == 1:
                out.append(line + "---|")
            else:
                out.append(line + " " + value + " |")
            idx += 1
            continue
        out.append(line)
    return "\n".join(out)


def check_thin_slice():
    # ---------------------------------------------------------------- shape
    cid = identity.new_object_id()
    doc = graph.new_course("Meridian Field Response", cid)
    for key in ("header", "structure", "objectives", "sources", "edges",
                "bindings", "migrations", "log", "unknown_sections"):
        if key not in doc:
            fail("new_course document is missing the key %r" % key)

    text = graph.serialize_course(doc)
    if not text.startswith("# Course graph"):
        fail("serialize_course must open with the line '# Course graph'")
    if "| graph_schema_version | 1 |" not in text:
        fail("the header table must carry a graph_schema_version row of 1")
    eq(graph.parse_course(text), doc, "parse(serialize(doc)) round trip")

    # An older build rewriting a newer build's file drops nothing: an
    # unrecognized section and an unrecognized column both survive byte for
    # byte. This is what makes the format additive by construction.
    rich = graph.new_course("Meridian Field Response", cid)
    mod = graph.add_container(rich, "module", "Scene Size Up")
    o1 = graph.add_objective(rich, "Identify scene hazards on arrival",
                             container=mod["id"])
    o2 = graph.add_objective(rich, "Choose a body substance isolation level",
                             container=mod["id"])
    graph.add_edge(rich, o1["id"], "prerequisite-of", o2["id"])
    rich_text = graph.serialize_course(rich)
    rich_text = _inject_unknown_column(rich_text, "Objectives", "owner", "weibao")
    rich_text = rich_text + "\n## Cohorts\n\n| cohort | term |\n|---|---|\n| alpha | fall |\n"
    eq(graph.serialize_course(graph.parse_course(rich_text)), rich_text,
       "byte-identical round trip with an unknown section and column")

    future = text.replace("| graph_schema_version | 1 |",
                          "| graph_schema_version | 2 |")
    err = raises(lambda: graph.parse_course(future), graph.GraphError,
                 "graph.future_schema_version", "a future schema version")
    if "2" not in err.message or "1" not in err.message:
        fail("the future-version refusal must name both versions: %s" % err.message)

    prose = text.replace("## Edges\n\n| source",
                         "## Edges\n\nThere are no edges yet.\n\n| source")
    raises(lambda: graph.parse_course(prose), graph.GraphError,
           "graph.malformed_section", "a prose section where a table belongs")

    # ------------------------------------------------- empty and single edge
    empty = graph.outline_projection(graph.new_course("Empty Course", cid))
    eq(empty, "# Empty Course\n\nNo objectives are recorded yet.\n",
       "the empty-course outline projection")

    one = graph.new_course("One Objective", cid)
    c1 = graph.add_container(one, "module", "Scene Size Up")
    j1 = graph.add_objective(one, "Identify scene hazards on arrival",
                             container=c1["id"])
    eq(graph.outline_projection(one),
       "# One Objective\n\n## Scene Size Up (module)\n\n- Identify scene hazards on arrival [%s]\n"
       % j1["id"], "the single-objective outline projection")

    # GRAPH-01: structural order mints no prerequisite edge.
    struct = graph.new_course("Structure Only", cid)
    for n in range(3):
        cn = graph.add_container(struct, "module", "Module %d" % (n + 1))
        graph.add_objective(struct, "Objective %d" % (n + 1),
                            container=cn["id"])
    eq(len(struct["edges"]), 0, "containers and objectives mint zero edges")

    # ------------------------------------------- compare-and-swap lifecycle
    tmp = tempfile.mkdtemp(prefix="graph_roundtrip_")
    try:
        root = os.path.join(tmp, "course_root")
        os.makedirs(root)

        rec = course.create_course(root, "Meridian Field Response",
                                   "human", "weibao")
        eq(list(rec.keys()), list(identity.REVISION_KEYS),
           "create_course returns a 14A revision record")
        eq(rec["kind"], "course", "the sidecar is a kind=course object")
        eq(rec["revision"], 1, "a fresh course is revision 1")
        eq(rec["parent_revision"], None, "revision 1 has no parent")

        registry = journal.read_registry(root)
        eq(len(registry), 1, "one registry entry after create_course")
        eq(list(registry.values())[0]["kind"], "course",
           "the one registry entry is a course")

        raises(lambda: course.create_course(root, "Second", "human", "weibao"),
               course.CourseError, "course.sidecar_exists",
               "creating a second course in one root")
        raises(lambda: course.read_course(os.path.join(tmp, "no_course")),
               course.CourseError, "course.no_sidecar",
               "reading a root with no sidecar")

        read = course.read_course(root)
        for key in ("doc", "text", "fingerprint", "revision", "object_id",
                    "state"):
            if key not in read:
                fail("read_course result is missing the key %r" % key)
        eq(read["state"], "clean", "a freshly written sidecar reads clean")
        eq(read["revision"], 1, "read_course reports revision 1")

        before_bytes = open(course.sidecar_path(root), "rb").read()
        widened = read["doc"]
        wc = graph.add_container(widened, "module", "Scene Size Up")
        graph.add_objective(widened, "Identify scene hazards on arrival",
                            container=wc["id"])
        raises(lambda: course.write_course(root, widened, "sha256:" + "0" * 64,
                                           "human", "weibao"),
               journal.JournalError, "journal.stale_preflight",
               "a write against a wrong expected fingerprint")
        eq(open(course.sidecar_path(root), "rb").read(), before_bytes,
           "a refused compare-and-swap write moves no bytes on disk")

        rec2 = course.write_course(root, widened, read["fingerprint"],
                                   "human", "weibao")
        eq(rec2["revision"], 2, "an accepted edit is revision 2")
        eq(rec2["parent_revision"], 1, "revision 2's parent is revision 1")
        eq(rec2["object_id"], rec["object_id"], "the object id is stable")

        # 14B mints no new object kind.
        eq(len(identity.OBJECT_KINDS), 6, "14B mints no new object kind")
        if "edge" in identity.OBJECT_KINDS:
            fail("an edge must never become an object kind")

        # ------------------------------------ the Phase 13.9 supersession
        stub_root = os.path.join(tmp, "stub_root")
        os.makedirs(stub_root)
        corpus_14b.build_stub_course(stub_root)
        stub_path = os.path.join(stub_root, course.STUB_FILENAME)
        stub_before = open(stub_path, "rb").read()
        if not stub_before.startswith(b"# Course manifest (DRAFT STUB"):
            fail("the stub fixture must carry the 13.9 header")

        report = course.migrate_stub(stub_root, "agent", "claude-code")
        eq(report["objectives"], 3, "the stub's three objectives migrated")
        if not os.path.exists(course.sidecar_path(stub_root)):
            fail("migrate_stub must create the course-graph sidecar")
        eq(open(stub_path, "rb").read(), stub_before,
           "migrate_stub leaves the hand-authored stub byte-identical")
        if not list(journal.entries(stub_root)):
            fail("migrate_stub must append a journal entry")
        raises(lambda: course.migrate_stub(os.path.join(tmp, "no_course"),
                                           "agent", "claude-code"),
               course.CourseError, "course.stub_absent",
               "migrating a root with no stub")

        # -------------------------------------- package and clean restore
        pkg = os.path.join(tmp, "package")
        manifest = course_package.export_package(root, root, pkg)
        eq(manifest["state"], "applied", "a finished export is applied")
        if not manifest["entries"]:
            fail("the manifest must carry at least one entry")
        entry = manifest["entries"][0]
        eq(set(entry.keys()), set(course_package.MANIFEST_ENTRY_KEYS),
           "the manifest entry key set")
        if not os.path.exists(os.path.join(pkg, course_package.MANIFEST_FILENAME)):
            fail("the package must carry a manifest.json")
        payload = os.path.join(pkg, course_package.PAYLOAD_DIRNAME,
                               entry["object_id"] + ".md")
        if not os.path.exists(payload):
            fail("the package must carry payload/<object id>.md")
        sidecar_raw = open(course.sidecar_path(root), "rb").read()
        eq(entry["fingerprint"],
           identity.object_fingerprint(sidecar_raw, "course"),
           "the manifest fingerprint is the sidecar's own")

        clean = os.path.join(tmp, "clean_dest")
        os.makedirs(clean)
        restored = course_package.restore_package(pkg, clean, "human", "weibao")
        eq(restored["entries_verified"], len(manifest["entries"]),
           "every manifest entry was verified on restore")
        eq(restored["complete"], True, "the restore reports itself complete")
        eq(open(os.path.join(clean, course.COURSE_SIDECAR_FILENAME), "rb").read(),
           sidecar_raw, "the restored sidecar is byte-identical")

        # A restore verifies by recomputation, never by trusting the manifest.
        raw = open(payload, "rb").read()
        corrupt = raw.replace(b"Meridian", b"Meridiam", 1)
        if corrupt == raw:
            fail("the corruption probe changed nothing; the fixture drifted")
        open(payload, "wb").write(corrupt)
        clean2 = os.path.join(tmp, "clean_dest_2")
        os.makedirs(clean2)
        err = raises(lambda: course_package.restore_package(pkg, clean2,
                                                            "human", "weibao"),
                     course_package.PackageError,
                     "package.fingerprint_mismatch",
                     "a corrupted payload byte")
        if entry["fingerprint"] not in err.message:
            fail("the mismatch refusal must name the expected fingerprint")
        open(payload, "wb").write(raw)

        # An interrupted export is refused rather than restored as complete.
        import json as _json
        mpath = os.path.join(pkg, course_package.MANIFEST_FILENAME)
        saved = open(mpath, "r", encoding="utf-8").read()
        broken = _json.loads(saved)
        broken["state"] = "prepared"
        open(mpath, "w", encoding="utf-8").write(_json.dumps(broken, indent=2))
        clean3 = os.path.join(tmp, "clean_dest_3")
        os.makedirs(clean3)
        raises(lambda: course_package.restore_package(pkg, clean3, "human",
                                                      "weibao"),
               course_package.PackageError, "package.not_applied",
               "a manifest left in the prepared state")
        open(mpath, "w", encoding="utf-8").write(saved)

        # A traversing entry is refused, never clamped to a safe path.
        for bad in ("../escape.md", "payload/../../escape.md",
                    os.path.join(tmp, "escape.md")):
            raises(lambda bad=bad: course_package.safe_target(clean, bad),
                   course_package.PackageError, "package.path_escape",
                   "the traversing package entry %r" % bad)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ------------------------------------------- tier and boundary asserts
    for name in ("model", "journal", "os", "evidence"):
        if hasattr(graph, name):
            fail("graph.py must not reach %s; it is the model tier and does "
                 "no file input or output" % name)
    if hasattr(course, "evidence"):
        fail("course.py must not import evidence; a migration never "
             "transfers evidence, and that must be structural")
    for name in ("urllib", "socket", "subprocess"):
        if hasattr(course_package, name):
            fail("course_package.py must not reach %s; a restore is an "
                 "offline operation" % name)



# ------------------------------------------------------------------ 14B-02

EXPECTED_PUBLIC_API = [
    "add_container", "add_edge", "add_objective", "edge_key", "is_rule_row",
    "new_course", "new_record", "outline_projection", "parse_course",
    "propose_order", "public_api", "serialize_course", "split_row",
    "treatment_right", "upgrade_0_to_1", "upgrade_document", "validate_binding",
    "validate_edge", "validate_order", "add_binding", "add_source",
    "overlay_objective",
]
EXPECTED_PUBLIC_API = sorted(EXPECTED_PUBLIC_API)

SCHEMA_PATH = os.path.join(ROOT, "schemas", "course_graph.schema.json")


def _schema_instance(doc):
    """Project a document to the shape the published schema describes: known
    columns only, with the round-trip bookkeeping keys dropped."""
    out = {"header": dict(doc["header"])}
    for section, key in (("Structure", "structure"), ("Objectives", "objectives"),
                         ("Sources", "sources"), ("Edges", "edges")):
        rows = []
        for record in doc[key]:
            rows.append({c: record[c] for c in graph.SECTION_COLUMNS[section]})
        out[key] = rows
    return out


def check_edges():
    eq(len(graph.EDGE_TYPES), 4, "the frozen edge vocabulary has four names")
    eq(graph.EDGE_TYPES, ("prerequisite-of", "covers-objective",
                          "source-supports", "treatment-of"),
       "the frozen edge vocabulary")
    eq(graph.EDGE_AUTHORITIES, ("authored", "imported", "proposed"),
       "the edge authority vocabulary")
    eq(graph.EDGE_CONFIDENCES, ("high", "medium", "low", "unknown"),
       "the edge confidence vocabulary")
    eq(graph.EDGE_OVERRIDES, ("advisory", "recommended-before", "hard-gate"),
       "the edge override vocabulary")

    bare = graph.validate_edge({"source": "a", "edge_type": "prerequisite-of",
                                "target": "b"})
    eq(bare["authority"], "proposed", "the default authority")
    eq(bare["confidence"], "unknown", "the default confidence")
    eq(bare["override"], "advisory", "the default override")
    eq(bare["rationale"], "", "the default rationale")

    for known in graph.EDGE_TYPES:
        got = graph.validate_edge({"source": "a", "edge_type": known,
                                   "target": "b"})
        eq(got["effective_type"], known, "a known type is not downgraded")
        eq(got["original_type"], known, "a known type keeps its original")

    for unknown in ("alternate-path", "", None):
        record = {"source": "a", "target": "b", "override": "hard-gate"}
        if unknown is not None:
            record["edge_type"] = unknown
        got = graph.validate_edge(record)
        if not isinstance(got, dict):
            fail("an unrecognized edge type must be kept, never dropped")
        eq(got["effective_type"], "recommended-before",
           "an unrecognized edge type degrades")
        eq(got["authority"], "advisory",
           "an unrecognized edge type cannot carry authority")
        eq(got["override"], "advisory",
           "an unrecognized edge type can never hard-block")
        eq(got["original_type"], unknown or "",
           "the original type string is preserved")
        eq(got["original_override"], "hard-gate",
           "the original override string is preserved")

    degraded = graph.validate_edge({"source": "a", "edge_type": "covers-objective",
                                    "target": "b", "authority": "decreed",
                                    "confidence": "certain",
                                    "override": "block-everything"})
    eq(degraded["authority"], "proposed", "an unrecognized authority degrades")
    eq(degraded["original_authority"], "decreed", "the authority string is kept")
    eq(degraded["confidence"], "unknown", "an unrecognized confidence degrades")
    eq(degraded["original_confidence"], "certain",
       "the confidence string is kept")
    eq(degraded["override"], "advisory", "an unrecognized override degrades")
    eq(degraded["original_override"], "block-everything",
       "the override string is kept")

    # The file records what the human wrote; only the reading is downgraded.
    cid = identity.new_object_id()
    doc = graph.new_course("Degrade Round Trip", cid)
    a = graph.add_objective(doc, "First")
    b = graph.add_objective(doc, "Second")
    graph.add_edge(doc, a["id"], "alternate-path", b["id"],
                   override="hard-gate")
    text = graph.serialize_course(doc)
    if "alternate-path" not in text or "hard-gate" not in text:
        fail("the sidecar must record what the human wrote, not the downgrade")
    eq(graph.serialize_course(graph.parse_course(text)), text,
       "a downgraded edge round trips byte for byte")

    eq(graph.edge_key(doc["edges"][0]),
       (a["id"], "alternate-path", b["id"]),
       "edge_key uses the original type so two unknown types stay distinct")

    raises(lambda: graph.add_edge(doc, a["id"], "alternate-path", b["id"]),
           graph.GraphError, "graph.duplicate_edge", "a duplicate edge")
    eq(len(doc["edges"]), 1, "a refused duplicate is never recorded twice")
    raises(lambda: graph.add_edge(doc, a["id"], "prerequisite-of", a["id"]),
           graph.GraphError, "graph.self_edge", "an edge pointing at itself")
    raises(lambda: graph.add_edge(doc, a["id"], "prerequisite-of", "0" * 16),
           graph.GraphError, "graph.unknown_objective", "an unknown endpoint")

    shared = graph.new_course("Shared Endpoints", cid)
    s1 = graph.add_objective(shared, "One")
    s2 = graph.add_objective(shared, "Two")
    s3 = graph.add_objective(shared, "Three")
    graph.add_edge(shared, s1["id"], "prerequisite-of", s2["id"])
    graph.add_edge(shared, s1["id"], "prerequisite-of", s3["id"])
    eq(len(shared["edges"]), 2, "two edges sharing a source stay separate")
    shared2 = graph.new_course("Shared Targets", cid)
    t1 = graph.add_objective(shared2, "One")
    t2 = graph.add_objective(shared2, "Two")
    t3 = graph.add_objective(shared2, "Three")
    graph.add_edge(shared2, t1["id"], "prerequisite-of", t3["id"])
    graph.add_edge(shared2, t2["id"], "prerequisite-of", t3["id"])
    eq(len(shared2["edges"]), 2, "two edges sharing a target stay separate")

    # GRAPH-02 empty edge.
    lone = graph.new_course("No Edges", cid)
    lone_id = graph.add_objective(lone, "Only")["id"]
    eq(graph.validate_order(lone), [], "a zero-edge document warns about nothing")
    if "Only" not in graph.outline_projection(lone):
        fail("a zero-edge document still projects every objective")
    eq(graph.propose_order([], []), [], "propose_order over nothing")
    eq(graph.propose_order([lone_id], []), [lone_id],
       "propose_order over one objective")


def check_structure_and_outline():
    cid = identity.new_object_id()

    # GRAPH-01: any local label, including an invented one, needs no schema
    # change.
    labels = ("program", "semester", "module", "week", "unit", "chapter",
              "fortnight", "quarter", "sprint")
    doc = graph.new_course("Every Label", cid)
    for label in labels:
        made = graph.add_container(doc, label, "Container " + label)
        graph.add_objective(doc, "Objective under " + label,
                            container=made["id"])
    text = graph.serialize_course(doc)
    eq(graph.serialize_course(graph.parse_course(text)), text,
       "every container label round trips")
    outline = graph.outline_projection(doc)
    for label in labels:
        if "(%s)" % label not in outline:
            fail("the outline must render the local label %r" % label)

    # Structural order mints no prerequisite status.
    bare = graph.new_course("Structure Only", cid)
    for n in range(3):
        cn = graph.add_container(bare, "module", "Module %d" % (n + 1))
        graph.add_objective(bare, "Objective %d" % (n + 1), container=cn["id"])
    eq(bare["edges"], [], "containers and objectives alone mint no edge")

    # Authored order is read verbatim, and a reorder moves exactly two lines.
    ordered = graph.new_course("Ordered", cid)
    oc = graph.add_container(ordered, "module", "Only Module")
    ids = [graph.add_objective(ordered, "Objective %d" % n,
                               container=oc["id"])["id"] for n in (1, 2, 3)]
    before = graph.outline_projection(ordered)
    eq(before, graph.outline_projection(ordered),
       "the outline is byte-identical across two runs")
    eq(graph.outline_projection(
        graph.parse_course(graph.serialize_course(ordered))), before,
       "the outline survives a serialize and parse round trip")
    ordered["objectives"][0]["order"], ordered["objectives"][1]["order"] = \
        ordered["objectives"][1]["order"], ordered["objectives"][0]["order"]
    after = graph.outline_projection(ordered)
    changed = [(x, y) for x, y in zip(before.split("\n"), after.split("\n"))
               if x != y]
    eq(len(changed), 2, "reversing two order values moves exactly two lines")
    ordered["objectives"][0]["order"], ordered["objectives"][1]["order"] = \
        ordered["objectives"][1]["order"], ordered["objectives"][0]["order"]

    # The outline is plain Markdown and never reorders around an edge.
    without = graph.outline_projection(ordered)
    graph.add_edge(ordered, ids[2], "prerequisite-of", ids[0])
    eq(graph.outline_projection(ordered), without,
       "a violated prerequisite never reorders the authored sequence")
    for line in without.split("\n"):
        if not line.strip():
            continue
        if line[0] not in "#-" and not line[0].isalpha():
            fail("the outline must be plain Markdown, saw %r" % line)
        if "<" in line or line.lstrip().startswith("{"):
            fail("the outline must carry no HTML or JSON, saw %r" % line)
        if "\u2014" in line:
            fail("the outline must carry no em dash, saw %r" % line)

    # Order validation reports, it does not correct.
    warnings = graph.validate_order(ordered)
    eq(len(warnings), 1, "one violated prerequisite gives one warning")
    if ids[2] not in warnings[0] or ids[0] not in warnings[0]:
        fail("the warning must name both objectives: %s" % warnings[0])
    if "appears after" not in warnings[0]:
        fail("the warning must say 'appears after': %s" % warnings[0])

    satisfied = graph.new_course("Satisfied", cid)
    sc = graph.add_container(satisfied, "module", "Only")
    s1 = graph.add_objective(satisfied, "First", container=sc["id"])
    s2 = graph.add_objective(satisfied, "Second", container=sc["id"])
    graph.add_edge(satisfied, s1["id"], "prerequisite-of", s2["id"])
    eq(graph.validate_order(satisfied), [],
       "an order that satisfies every prerequisite warns about nothing")

    for other in ("covers-objective", "source-supports", "treatment-of"):
        quiet = graph.new_course("Quiet " + other, cid)
        q1 = graph.add_objective(quiet, "First")
        q2 = graph.add_objective(quiet, "Second")
        graph.add_edge(quiet, q2["id"], other, q1["id"])
        eq(graph.validate_order(quiet), [],
           "a %s edge never produces an order warning" % other)

    advisory = graph.new_course("Advisory", cid)
    a1 = graph.add_objective(advisory, "First")
    a2 = graph.add_objective(advisory, "Second")
    graph.add_edge(advisory, a2["id"], "alternate-path", a1["id"])
    eq(graph.validate_order(advisory), [],
       "a downgraded advisory edge cannot be violated")

    # The topological fallback and its tie-break.
    roots = sorted([identity.new_object_id() for _ in range(4)])
    eq(graph.propose_order(list(roots), []), roots,
       "independent roots come back in object_id ascending order")
    shuffled = list(roots)
    random.Random(1400).shuffle(shuffled)
    eq(graph.propose_order(shuffled, []), graph.propose_order(list(roots), []),
       "shuffling the input does not change the proposed order")
    chain = [(roots[0], roots[1]), (roots[1], roots[2])]
    got = graph.propose_order(list(roots), chain)
    for prereq, dependent in chain:
        if got.index(prereq) >= got.index(dependent):
            fail("the proposed order must satisfy every prerequisite edge")
    cyc = [(roots[0], roots[1]), (roots[1], roots[2]), (roots[2], roots[0])]
    err = raises(lambda: graph.propose_order(list(roots), cyc),
                 graph.GraphError, "graph.prerequisite_cycle",
                 "a prerequisite cycle")
    for member in roots[:3]:
        if member not in err.message:
            fail("the cycle refusal must list its members")

    cycle_doc = graph.parse_course(corpus_14b.sidecar_text_with_cycle())
    projected = graph.outline_projection(cycle_doc)
    if not projected.startswith("# "):
        fail("a cyclic graph must still project its authored outline")
    if not graph.validate_order(cycle_doc):
        fail("a cycle must surface through validate_order as a warning")

    # Encoding and identity: no Unicode normalization, ever.
    if hasattr(graph, "unicodedata"):
        fail("graph.py must apply no Unicode normalization")
    pre = graph.new_course("Accents", cid)
    graph.add_objective(pre, "Mesure la r\u00e9ponse")
    comb = graph.new_course("Accents", cid)
    graph.add_objective(comb, "Mesure la re\u0301ponse")
    fa = identity.object_fingerprint(graph.serialize_course(pre).encode("utf-8"),
                                     "course")
    fb = identity.object_fingerprint(graph.serialize_course(comb).encode("utf-8"),
                                     "course")
    if fa == fb:
        fail("two accent compositions must fingerprint differently")

    same = graph.new_course("Same Statement", cid)
    d1 = graph.add_objective(same, "Identical statement")
    d2 = graph.add_objective(same, "Identical statement")
    eq(len(same["objectives"]), 2,
       "two objectives with one statement stay two records")
    if d1["id"] == d2["id"]:
        fail("identity is minted, never derived from a statement")

    eq(graph.public_api(), EXPECTED_PUBLIC_API,
       "the module's public surface must not grow without a plan edit")

    # The three-domain corpus.
    tmp = tempfile.mkdtemp(prefix="graph_corpus_")
    try:
        built = corpus_14b.build_three_domains(tmp)
        eq(len(built["domains"]), 3, "the corpus builds three domains")
        seen_labels = set()
        for domain in built["domains"]:
            doc = course.read_course(domain["root"])["doc"]
            eq(len([e for e in doc["edges"]
                    if e["edge_type"] == "prerequisite-of"]),
               domain["prerequisite_edges"],
               "%s has exactly the prerequisite edges it wrote" % domain["slug"])
            for container in doc["structure"]:
                seen_labels.add(container["label"])
        for label in ("module", "week", "fortnight", "chapter"):
            if label not in seen_labels:
                fail("the corpus must exercise the container label %r" % label)
    finally:
        corpus_14b.teardown(tmp)


def check_schema_file():
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        schema = json.load(fh)
    schema_validate.check_schema(schema)
    eq(schema["x-itembank-version"], 1, "the schema's itembank version")
    eq(schema["$defs"]["edge"]["properties"]["edge_type"]["enum"],
       list(graph.EDGE_TYPES), "the published frozen edge vocabulary")
    if "enum" in schema["$defs"]["container"]["properties"]["label"]:
        fail("the container label must carry no enum; GRAPH-01 requires a "
             "local label to be accepted without a schema change")
    if "\u2014" in json.dumps(schema, ensure_ascii=False):
        fail("the schema must contain no em dash character")

    tmp = tempfile.mkdtemp(prefix="graph_schema_")
    try:
        built = corpus_14b.build_three_domains(tmp)
        root = built["domains"][0]["root"]
        instance = _schema_instance(course.read_course(root)["doc"])
        errors = schema_validate.validate(instance, schema)
        if errors:
            fail("the meridian domain must validate: %s" % errors[:3])
        instance["edges"][0].pop("target")
        if not schema_validate.validate(instance, schema):
            fail("an edge missing its target must be rejected")
    finally:
        corpus_14b.teardown(tmp)


def check_format_additivity():
    if hasattr(graph, "model"):
        fail("graph.py must never reach the one parser")
    golden_path = os.path.join(ROOT, "fixtures", "lesson_golden_phase3_parse.json")
    bank = os.path.join(ROOT, "fixtures", "lesson_bank.md")
    golden = json.load(open(golden_path, encoding="utf-8"))
    qs = model.load(bank)
    if json.dumps(qs, sort_keys=True) != json.dumps(golden["qs"],
                                                    sort_keys=True):
        fail("this phase changed the shipped parse; it must be additive")
    text = corpus_14b.sidecar_text_with_unknowns()
    eq(graph.serialize_course(graph.parse_course(text)), text,
       "an unknown section and column survive byte for byte")



def _objective_line(text, objective_id):
    for line in text.split("\n"):
        if line.startswith("| " + objective_id + " "):
            return line
    fail("no objectives row for %s" % objective_id)


def check_bindings_and_rights():
    eq(len(graph.TREATMENT_KINDS), 11, "TREAT-01 has eleven treatment kinds")
    eq(graph.TREATMENT_KINDS,
       ("direct-reading", "excerpt", "guided-lesson", "notes-or-terms",
        "worked-example", "visual-or-demonstration", "practice",
        "formal-test", "assessment-first-diagnostic", "learner-artifact",
        "human-review"), "the TREAT-01 treatment vocabulary")
    eq(graph.BINDING_KINDS, ("source", "treatment"), "the binding kinds")
    eq(graph.BINDING_STATES,
       ("covered", "thin", "missing", "conflicting", "unknown"),
       "the TREAT-02 binding states")
    for forbidden in ("verified", "assumed"):
        if forbidden in graph.BINDING_STATES:
            fail("coverage is reported, never claimed: %r must not be a "
                 "binding state" % forbidden)
    eq(len(graph.TREATMENT_RIGHTS), 11, "every treatment maps to a right")
    for kind, right in graph.TREATMENT_RIGHTS.items():
        if right not in identity.RIGHTS_OPERATIONS:
            fail("%s maps to %r, which is not a rights operation"
                 % (kind, right))
    eq(graph.treatment_right("excerpt"), "quote", "excerpt consumes quote")
    eq(graph.treatment_right("guided-lesson"), "transform",
       "a guided lesson consumes transform")
    eq(graph.treatment_right("direct-reading"), "read",
       "direct reading consumes read")
    raises(lambda: graph.treatment_right("flashcards"), graph.GraphError,
           "graph.unknown_treatment_kind", "a twelfth treatment kind")

    cid = identity.new_object_id()
    doc = graph.new_course("Bindings", cid)
    obj = graph.add_objective(doc, "An objective")
    src_id = identity.new_object_id()
    graph.add_source(doc, src_id, "A source")
    err = raises(lambda: graph.add_binding(doc, "treatment", obj["id"], src_id,
                                           treatment_kind="flashcards"),
                 graph.GraphError, "graph.unknown_treatment_kind",
                 "binding an unknown treatment kind")
    if "eleven" not in err.message:
        fail("the refusal must name the closed vocabulary: %s" % err.message)

    # An unrecognized state degrades to unknown, never to covered.
    degraded = graph.validate_binding({"binding_kind": "source",
                                       "objective": obj["id"],
                                       "state": "looks-fine"})
    eq(degraded["state"], "unknown", "an unrecognized binding state degrades")
    eq(degraded["original_state"], "looks-fine", "the source string is kept")
    if degraded["state"] == "covered":
        fail("similarity alone must never produce covered")

    # An empty bindings table parses to a list, never to None.
    empty = graph.parse_course(graph.serialize_course(doc))
    eq(empty["bindings"], [], "an empty bindings table parses to a list")

    # Two bindings differing only by locator are two rows.
    graph.add_binding(doc, "source", obj["id"], src_id, locator="page 1")
    graph.add_binding(doc, "source", obj["id"], src_id, locator="page 2")
    eq(len(doc["bindings"]), 2,
       "a binding is not identified by its endpoints alone")

    tmp = tempfile.mkdtemp(prefix="graph_rights_")
    try:
        built = corpus_14b.build_three_domains(tmp)
        domains = {d["slug"]: d for d in built["domains"]}

        # Every right unknown: every binding refuses, and names the fix.
        mer = domains["meridian-field-response"]
        root = mer["root"]
        before_bytes = open(course.sidecar_path(root), "rb").read()
        before_entries = len(list(journal.entries(root)))
        err = raises(lambda: course.bind_source(
            root, mer["objectives"][0], mer["source_object_id"],
            locator="section 1.2", actor_kind="human", actor_name="weibao"),
            course.CourseError, "course.rights_not_granted",
            "binding against a source whose rights are all unknown")
        for token in (mer["source_object_id"], "read", "unknown",
                      "next safe action: record"):
            if token not in err.message:
                fail("the refusal must contain %r: %s" % (token, err.message))
        eq(open(course.sidecar_path(root), "rb").read(), before_bytes,
           "a refused binding writes no bytes")
        eq(len(list(journal.entries(root))), before_entries,
           "a refused binding appends no journal entry")

        # A granted right does not imply another.
        orr = domains["orrery-algebra"]
        raises(lambda: course.bind_source(
            orr["root"], orr["objectives"][0], orr["source_object_id"],
            locator="week 1", actor_kind="human", actor_name="weibao"),
            course.CourseError, "course.rights_not_granted",
            "a granted quote right does not grant read")

        corpus_14b.grant_right(orr["root"], orr["source_object_id"], "read")
        before_rev = course.read_course(orr["root"])["revision"]
        rec = course.bind_source(orr["root"], orr["objectives"][0],
                                 orr["source_object_id"], locator="week 1",
                                 actor_kind="human", actor_name="weibao")
        eq(rec["revision"], before_rev + 1, "an accepted binding is one revision")
        bound = course.read_course(orr["root"])["doc"]
        rows = [b for b in bound["bindings"] if b["binding_kind"] == "source"]
        eq(len(rows), 1, "the sidecar gains exactly one source binding row")
        eq(rows[0]["rights_snapshot"], "granted",
           "the binding records the rights state at bind time")

        # A stale snapshot never authorizes: revoke, then bind again.
        corpus_14b.revoke_right(orr["root"], orr["source_object_id"], "read")
        err = raises(lambda: course.bind_source(
            orr["root"], orr["objectives"][1], orr["source_object_id"],
            locator="week 2", actor_kind="human", actor_name="weibao"),
            course.CourseError, "course.rights_not_granted",
            "binding after the right was revoked")
        if "denied" not in err.message:
            fail("the refusal must name the current state: %s" % err.message)
        still = course.read_course(orr["root"])["doc"]
        eq([b for b in still["bindings"]][0]["rights_snapshot"], "granted",
           "the earlier snapshot row is untouched and still reads granted")

        # A treatment consumes the right its kind maps to.
        lan = domains["lantern-computing"]
        course.bind_treatment(lan["root"], lan["objectives"][0],
                              lan["source_object_id"],
                              treatment_kind="guided-lesson",
                              actor_kind="human", actor_name="weibao")
        err = raises(lambda: course.bind_treatment(
            lan["root"], lan["objectives"][1], lan["source_object_id"],
            treatment_kind="excerpt", actor_kind="human", actor_name="weibao"),
            course.CourseError, "course.rights_not_granted",
            "an excerpt consumes quote, which is not granted")
        if "quote" not in err.message:
            fail("the refusal must name the right: %s" % err.message)
        raises(lambda: course.bind_treatment(
            lan["root"], lan["objectives"][2], lan["source_object_id"],
            treatment_kind="direct-reading", actor_kind="human",
            actor_name="weibao"),
            course.CourseError, "course.rights_not_granted",
            "direct reading is a treatment, not a free pass")
        raises(lambda: course.bind_source(
            lan["root"], lan["objectives"][0], "0" * 16,
            actor_kind="human", actor_name="weibao"),
            course.CourseError, "course.unknown_source",
            "binding an object the registry does not know")

        # The derived title cell is not load-bearing.
        read = course.read_course(lan["root"])
        doc2 = read["doc"]
        doc2["sources"][0]["title"] = "a deliberately wrong derived title"
        course.write_course(lan["root"], doc2, read["fingerprint"], "human",
                            "weibao")
        course.bind_treatment(lan["root"], lan["objectives"][3],
                              lan["source_object_id"],
                              treatment_kind="practice",
                              actor_kind="human", actor_name="weibao")
    finally:
        corpus_14b.teardown(tmp)


def check_overlays():
    eq(graph.OBJECTIVE_ORIGINS, ("local", "imported"), "the objective origins")
    cid = identity.new_object_id()
    doc = graph.new_course("Imported Scope", cid)
    container = graph.add_container(doc, "module", "Only")
    imported = graph.add_objective(doc, "An imported statement",
                                   container=container["id"],
                                   origin="imported",
                                   import_version="scope-2026.1")
    eq(imported["origin"], "imported", "an imported objective says so")
    eq(imported["import_version"], "scope-2026.1", "the import version is kept")

    before = _objective_line(graph.serialize_course(doc), imported["id"])
    local = graph.overlay_objective(doc, imported["id"], "a revised statement",
                                    "weibao")
    after = _objective_line(graph.serialize_course(doc), imported["id"])
    eq(after, before, "the imported row is byte-identical after an overlay")
    eq(local["origin"], "local", "an overlay is a local record")
    eq(local["overlays"], imported["id"], "the overlay names what it overlays")
    if local["id"] == imported["id"]:
        fail("an overlay carries its own minted id")

    migrations = [m for m in doc["migrations"] if m["kind"] == "overlay"]
    eq(len(migrations), 1, "an overlay records one migration row")
    eq(migrations[0]["from"], imported["id"], "the migration names the import")
    eq(migrations[0]["to"], local["id"], "the migration names the overlay")
    eq(migrations[0]["state"], "proposed", "an overlay is proposed, not applied")

    raises(lambda: graph.add_objective(doc, "a rewrite", origin="imported",
                                       objective_id=imported["id"]),
           graph.GraphError, "graph.imported_objective_immutable",
           "rewriting an imported objective in place")

    second = graph.overlay_objective(doc, local["id"], "a second revision",
                                     "weibao")
    eq(second["overlays"], local["id"], "an overlay of an overlay chains")
    eq(_objective_line(graph.serialize_course(doc), imported["id"]), before,
       "the import is still untouched after a second overlay")
    eq(len(doc["objectives"]), 3, "nothing in the chain is deleted")

    outline = graph.outline_projection(doc)
    eq(outline.count("a second revision"), 1, "the newest row is rendered")
    if "An imported statement" in outline or "a revised statement" in outline:
        fail("a superseded row must not be rendered twice")


def check_version_migration():
    eq(graph.COURSE_GRAPH_VERSION, 1, "the current course graph version")
    if not isinstance(graph.UPGRADES, dict):
        fail("UPGRADES must be a dict keyed by from-version")
    if 0 not in graph.UPGRADES:
        fail("UPGRADES must carry a step from version 0")
    for key, value in graph.UPGRADES.items():
        if not isinstance(key, int) or not callable(value):
            fail("UPGRADES maps an integer version to a callable step")

    text = corpus_14b.sidecar_text_version_0()
    if "| graph_schema_version | 0 |" not in text:
        fail("the version-0 fixture must declare version 0")
    if "| source | edge_type | target | authority | rationale | confidence |" \
            not in text:
        fail("the version-0 fixture's edges table must lack the override column")

    doc = graph.parse_course(text)
    eq(doc["header"]["graph_schema_version"], 1, "a version-0 sidecar upgrades")
    eq(doc["upgraded_from"], 0, "the document records where it came from")
    for edge in doc["edges"]:
        eq(edge["override"], "advisory",
           "the upgrade supplies the least-blocking default, never a hard gate")

    out = graph.serialize_course(doc)
    if "| graph_schema_version | 1 |" not in out:
        fail("an upgraded document is written back at the current version")
    if "| source | edge_type | target | authority | rationale | confidence | override |" \
            not in out:
        fail("the upgraded edges table must carry the override column")
    if "## Cohorts" not in out or "| alpha | fall |" not in out:
        fail("an unknown section must survive the upgrade untouched")

    future = text.replace("| graph_schema_version | 0 |",
                          "| graph_schema_version | 2 |")
    future = future.replace("## Edges\n", "## Edges\n\nnot a table at all\n")
    err = raises(lambda: graph.parse_course(future), graph.GraphError,
                 "graph.future_schema_version",
                 "a future version with a malformed section")
    if "2" not in err.message or "1" not in err.message:
        fail("the refusal must name both versions: %s" % err.message)

    raises(lambda: graph.upgrade_document(graph.new_course("x", "0" * 16), 7),
           graph.GraphError, "graph.unknown_upgrade_path",
           "a gap in the upgrade chain")


def main():
    started = time.time()
    check_thin_slice()
    check_edges()
    check_structure_and_outline()
    check_schema_file()
    check_format_additivity()
    check_bindings_and_rights()
    check_overlays()
    check_version_migration()
    elapsed = time.time() - started
    print("OK graph_roundtrip (%.2fs)" % elapsed)


if __name__ == "__main__":
    main()
