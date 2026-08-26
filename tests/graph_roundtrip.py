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
import os, shutil, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import identity                                              # noqa: E402
import journal                                               # noqa: E402
import graph                                                 # noqa: E402
import course                                                # noqa: E402
import course_package                                        # noqa: E402
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
        if not journal.entries(stub_root):
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


def main():
    started = time.time()
    check_thin_slice()
    elapsed = time.time() - started
    print("OK graph_roundtrip (%.2fs)" % elapsed)


if __name__ == "__main__":
    main()
