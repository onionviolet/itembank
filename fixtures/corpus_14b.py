"""The synthetic course corpus Phase 14B's graph kernel is proven against.

`build_three_domains(dest)` builds course roots under `dest` and returns a
dict describing what it built. Plan 14B-01 needs only the first domain; plan
14B-02 widens this to three so the freeze gate's three-domain tracer has a
corpus. `build_stub_course(dest)` writes a Phase 13.9 shaped `course.md` so
the non-destructive migration path has a real stub to read.

Every file's content is fictional and generated from a fixed seed, so a
rebuild is byte-identical and this corpus names no real course, book, learner,
or bank (project content rule). It is built into temp directories at test
time, so `python itembank.py guard .` never sees it.

`teardown(dest)` removes a built corpus.
"""
import os
import shutil

# Fictional throughout. Every course name, container title, objective
# statement, and source title below is invented. None names a real course,
# book, learner, bank, or lesson, which the project content rule requires and
# `python itembank.py guard .` enforces.
#
# The three domains are shaped differently on purpose: `module` containers,
# `week` containers plus one invented `fortnight` label, and `chapter`
# containers. The invented label is the one that proves GRAPH-01's clause
# that a local structural label needs no schema change.
DOMAINS = (
    {
        "slug": "meridian-field-response",
        "title": "Meridian Field Response",
        "label": "module",
        "containers": ("Scene Size Up", "Primary Assessment"),
        "objectives": (
            "Identify scene hazards on arrival",
            "Choose a body substance isolation level",
            "State the number of patients before approaching",
            "Form a general impression in one sentence",
            "Rank the three findings that change transport priority",
            "Hand off using a fixed report order",
        ),
        # Three prerequisite edges and one covers-objective edge, all
        # satisfied by the authored order.
        "prerequisites": ((0, 1), (1, 2), (3, 4)),
        "covers": (5, 3),
        "supports": None,
        "treatments": None,
        "unregistered": None,
        "source_title": "Field response unit one, working notes",
        "source_rights": {},
    },
    {
        "slug": "orrery-algebra",
        "title": "Orrery Algebra",
        "label": "week",
        "containers": ("Rates of Change", "Reading a Graph"),
        "extra_container": ("fortnight", "Consolidation Fortnight"),
        "objectives": (
            "Read a rate of change from a table",
            "Relate a rate of change to its graph",
            "Predict a value between two measured points",
            "Name the units a rate of change carries",
            "Decide when a straight line model stops being honest",
        ),
        # The second pair is deliberately violated by the authored order: the
        # prerequisite sits after its dependent, so validate_order has a real
        # violation to report and the outline has a real chance to wrongly
        # correct it.
        "prerequisites": ((0, 1), (3, 2)),
        "covers": None,
        "supports": 4,
        "treatments": None,
        "unregistered": None,
        "imported_objectives": 2,
        "import_version": "orrery-scope-2026.1",
        "source_title": "Orrery algebra, worked graph readings",
        "source_rights": {"quote": "granted"},
    },
    {
        "slug": "lantern-computing",
        "title": "Lantern Computing Foundations",
        "label": "chapter",
        "containers": ("Values and Names", "Repetition"),
        "objectives": (
            "Predict the value a name is bound to",
            "Trace a rebinding through a short program",
            "State the condition a loop ends on",
            "Rewrite a counted loop as a conditional loop",
            "Explain why an off by one error reads as correct",
        ),
        "prerequisites": (),
        "covers": None,
        "supports": None,
        "treatments": (1, 0),
        # An unregistered relation carrying an explicit hard gate. The point
        # of keeping it in the corpus is that a regression which lets an
        # unknown type block a learner fails a test instead of shipping.
        "unregistered": (4, 2),
        "source_title": "Lantern computing, chapter exercises",
        "source_rights": {"transform": "granted", "package": "denied"},
    },
)

SOURCE_BODY = (
    "# %s\n\nThis synthetic passage exists only to give the graph kernel a\n"
    "source object to bind against. It names no real course, book, or\n"
    "learner, and its content is generated from a fixed seed so a rebuild is\n"
    "byte-identical.\n"
)

STUB_HEADER = (
    "# Course manifest (DRAFT STUB, 2026-08-14)",
    "",
    "This file is a hand-authored draft manifest for one walking-skeleton",
    "course. It records what was discovered, what was bound, and what was",
    "decided, in the smallest readable form. Phase 14B owns the durable",
    "course schema and supersedes this format.",
)

STUB_SOURCES = (
    ("s1", "sources/field-response-unit-1.md", "markdown", "18402",
     "0f1e2d3c4b5a6978"),
    ("s2", "sources/field-response-figures.md", "markdown", "4110",
     "1a2b3c4d5e6f7081"),
)

STUB_OBJECTIVES = (
    ("o1", "Identify scene hazards on arrival",
     "field-response-unit-1.md section 1.2", "lesson plus practice",
     "the source explains it but never drills it"),
    ("o2", "Choose a body substance isolation level",
     "field-response-unit-1.md section 1.4", "direct source reading",
     "the source is already clear and worked"),
    ("o3", "Sequence the first ninety seconds on scene",
     "field-response-unit-1.md section 2.1", "lesson plus practice",
     "the ordering is the whole difficulty"),
)


def _table(columns, rows):
    out = ["| " + " | ".join(columns) + " |",
           "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(row) + " |")
    return out


def build_stub_course(dest):
    """Write a Phase 13.9 shaped `course.md` into `dest` and return its path.

    This is the file `course.migrate_stub` reads and, under D-14B-1, never
    writes. The test asserts its bytes are identical before and after the
    migration, which is the whole point of having a real one here.
    """
    os.makedirs(dest, exist_ok=True)
    lines = list(STUB_HEADER)
    lines.append("")
    lines.append("## Sources")
    lines.append("")
    lines.extend(_table(("id", "path", "format", "size", "sha256"),
                        STUB_SOURCES))
    lines.append("")
    lines.append("## Objectives")
    lines.append("")
    lines.extend(_table(("id", "objective", "citation", "treatment", "reason"),
                        STUB_OBJECTIVES))
    lines.append("")
    lines.append("## Log")
    lines.append("")
    lines.append("- 2026-08-14 drafted by hand from the unit 1 reading.")
    path = os.path.join(dest, "course.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def build_three_domains(dest):
    """Build the corpus's three course roots under `dest` and describe them.

    Every authored string is fixed, so a rebuild produces byte-identical
    content. Object ids are not fixed and cannot be: D-14A-2 requires a
    minted opaque id that is never derived from content, so two builds mint
    two different id sets on purpose. What is stable is everything a human
    wrote.
    """
    import course
    import graph
    import identity
    import journal

    built = []
    for domain in DOMAINS:
        root = os.path.join(dest, domain["slug"])
        os.makedirs(root, exist_ok=True)

        # One real source object per domain, minted through the 14A path so
        # its rights record is a recorded grant rather than a claim in a
        # comment. Rights default to all unknown, which is restrictive.
        source_rel = "sources/%s.md" % domain["slug"]
        os.makedirs(os.path.join(root, "sources"), exist_ok=True)
        rights = identity.rights_default()
        rights.update(domain["source_rights"])
        source_object_id = identity.new_object_id()
        with open(os.path.join(root, source_rel), "w", encoding="utf-8") as fh:
            fh.write(SOURCE_BODY % domain["source_title"])
        # `link` records where a file already lives and writes nothing, so the
        # file is written first and the recorded fingerprint is the fingerprint
        # of the bytes actually on disk.
        journal.commit_operation(
            base=root, object_id=source_object_id, kind="source",
            rel_path=source_rel, operation="link", new_bytes=None,
            expected_fingerprint=None, actor_kind="agent",
            actor_name="corpus-14b", create_if_missing=True,
            write_target=False, rights=rights)

        course.create_course(root, domain["title"], "agent", "corpus-14b")
        read = course.read_course(root)
        doc = read["doc"]

        containers = [graph.add_container(doc, domain["label"], title)
                      for title in domain["containers"]]
        if domain.get("extra_container"):
            label, title = domain["extra_container"]
            containers.append(graph.add_container(doc, label, title))

        objective_ids = []
        imported = domain.get("imported_objectives", 0)
        for n, statement in enumerate(domain["objectives"]):
            container = containers[n % len(containers)]
            if n < imported:
                record = graph.add_objective(
                    doc, statement, container=container["id"],
                    origin="imported",
                    import_version=domain["import_version"])
            else:
                record = graph.add_objective(doc, statement,
                                             container=container["id"])
            objective_ids.append(record["id"])

        doc["sources"].append(graph.new_record("Sources", {
            "source_object_id": source_object_id,
            "title": domain["source_title"],
            "note": "rights are recorded on the source object, never here"}))

        prerequisite_edges = 0
        for a, b in domain["prerequisites"]:
            graph.add_edge(doc, objective_ids[a], "prerequisite-of",
                           objective_ids[b], authority="authored",
                           confidence="medium",
                           rationale="the first is read before the second")
            prerequisite_edges += 1
        if domain["covers"] is not None:
            a, b = domain["covers"]
            graph.add_edge(doc, objective_ids[a], "covers-objective",
                           objective_ids[b], authority="authored")
        if domain["supports"] is not None:
            graph.add_edge(doc, source_object_id, "source-supports",
                           objective_ids[domain["supports"]],
                           authority="imported")
        if domain["treatments"] is not None:
            a, b = domain["treatments"]
            graph.add_edge(doc, objective_ids[a], "treatment-of",
                           objective_ids[b], authority="proposed")
        if domain["unregistered"] is not None:
            a, b = domain["unregistered"]
            graph.add_edge(doc, objective_ids[a], "alternate-path",
                           objective_ids[b], override="hard-gate",
                           rationale="an unregistered relation, kept and "
                                     "downgraded rather than dropped")

        course.write_course(root, doc, read["fingerprint"], "agent",
                            "corpus-14b")
        built.append({
            "slug": domain["slug"], "root": root, "title": domain["title"],
            "label": domain["label"],
            "containers": [c["id"] for c in containers],
            "objectives": objective_ids,
            "source_object_id": source_object_id,
            "source_rel": source_rel,
            "prerequisite_edges": prerequisite_edges,
            "edges": len(doc["edges"]),
        })
    return {"dest": dest, "domains": built, "built": len(built),
            "declared": len(DOMAINS)}


def sidecar_text_with_unknowns():
    """A sidecar carrying a section and a column this build does not know.

    This is the fixture behind the additive-by-construction claim: an older
    build must be able to rewrite a newer build's file without dropping what
    it could not read, and a promise in prose is not evidence.
    """
    import graph
    import identity

    doc = graph.new_course("Unknown Field Survivor", identity.new_object_id())
    container = graph.add_container(doc, "module", "Only Module")
    graph.add_objective(doc, "Survive an older build's rewrite",
                        container=container["id"])
    graph.add_objective(doc, "Keep a column nobody here understands",
                        container=container["id"])
    text = graph.serialize_course(doc)

    out, inside, index = [], False, 0
    for line in text.split("\n"):
        if line.startswith("## "):
            inside = (line == "## Objectives")
            index = 0
            out.append(line)
            continue
        if inside and line.startswith("|"):
            if index == 0:
                out.append(line + " owner |")
            elif index == 1:
                out.append(line + "---|")
            else:
                out.append(line + " weibao |")
            index += 1
            continue
        out.append(line)
    return "\n".join(out) + \
        "\n## Cohorts\n\n| cohort | term |\n|---|---|\n| alpha | fall |\n"


def sidecar_text_with_cycle():
    """A sidecar whose edges form a three-node prerequisite cycle.

    A cycle has to exist in the corpus so that a regression which loops, or
    which silently truncates the order, fails a test rather than shipping.
    """
    import graph
    import identity

    doc = graph.new_course("Cyclic Prerequisites", identity.new_object_id())
    container = graph.add_container(doc, "module", "Only Module")
    ids = [graph.add_objective(doc, "Cyclic objective %d" % n,
                               container=container["id"])["id"]
           for n in (1, 2, 3)]
    graph.add_edge(doc, ids[0], "prerequisite-of", ids[1])
    graph.add_edge(doc, ids[1], "prerequisite-of", ids[2])
    graph.add_edge(doc, ids[2], "prerequisite-of", ids[0])
    return graph.serialize_course(doc)



def _set_right(root, source_object_id, operation, value):
    """Record a new rights state for one source object through the 14A path.

    This is a fixture helper, not a product surface. It exists so a test can
    revoke a right that was previously granted and prove that a stale
    snapshot row in a binding never authorizes anything.
    """
    import identity
    import journal

    registry = journal.read_registry(root)
    record = registry[source_object_id]
    rights = dict(record.get("rights") or identity.rights_default())
    rights[operation] = value
    journal.commit_operation(
        base=root, object_id=source_object_id, kind="source",
        rel_path=record["path"], operation="edit_in_place", new_bytes=None,
        expected_fingerprint=record["fingerprint"], actor_kind="human",
        actor_name="weibao", write_target=False, rights=rights)


def grant_right(root, source_object_id, operation):
    _set_right(root, source_object_id, operation, "granted")


def revoke_right(root, source_object_id, operation):
    _set_right(root, source_object_id, operation, "denied")


def sidecar_text_version_0():
    """A sidecar declaring course graph version 0.

    Version 1 introduced the edge `override` column, so this fixture's edges
    table lacks it entirely. It also carries a section this build does not
    know, because an upgrade that quietly dropped an unknown section would be
    exactly the destructive rewrite the version check exists to prevent.
    """
    import graph
    import identity

    doc = graph.new_course("Version Zero Course", identity.new_object_id())
    container = graph.add_container(doc, "module", "Only Module")
    ids = [graph.add_objective(doc, "Version zero objective %d" % n,
                               container=container["id"])["id"]
           for n in (1, 2)]
    graph.add_edge(doc, ids[0], "prerequisite-of", ids[1])
    text = graph.serialize_course(doc)

    out = []
    inside = False
    for line in text.split("\n"):
        if line.startswith("## "):
            inside = (line == "## Edges")
            out.append(line)
            continue
        if inside and line.startswith("|"):
            cells = line.strip().strip("|").split("|")
            out.append("|" + "|".join(cells[:-1]) + "|")
            continue
        out.append(line)
    text = "\n".join(out)
    text = text.replace("| graph_schema_version | 1 |",
                        "| graph_schema_version | 0 |")
    return text + "\n## Cohorts\n\n| cohort | term |\n|---|---|\n| alpha | fall |\n"


def seed_objective_evidence(course_root, objective_id):
    """Record one synthetic response event against `objective_id` and return
    its event id.

    The event is built by calling `evidence.response_event` and appended
    through `evidence.append_event`, so its key set is the shipped builder's
    key set and nothing is hand-assembled. Everything it names is invented:
    the bank, the item, and the session are fixture strings, the objective is
    a minted opaque id, and the whole store is written into a temp directory.

    This fixture is the only place Phase 14B imports `evidence` outside a
    test. It is a fixture, not a module under test: `graph.py` and
    `course.py` import no `evidence` module at all, which is what makes
    "a migration never transfers evidence" structural rather than careful.
    """
    import evidence

    q = {
        "id": "Q1",
        "item_id": "fixture-item-" + objective_id,
        "type": "mc",
        "stem": "A fictional fixture stem that names nothing real.",
        "opts": {"A": "the first invented option",
                 "B": "the second invented option"},
        "correct": "A",
        "objective": objective_id,
    }
    event = evidence.response_event(
        session_id="fixture-session-" + objective_id, q=q, answer="A",
        score=True, mode="quiz", attempt_num=1,
        bank="fixture-synthetic-bank")
    log = evidence.log_path(course_root)
    os.makedirs(os.path.dirname(log), exist_ok=True)
    evidence.append_event(log, event)
    return event["event_id"]


def register_source(root, slug, rights=None, operation="mint", body=None):
    """Write one synthetic source file into `root` and register it through the
    frozen 14A compare-and-swap path.

    `rights` records exactly what the caller states and nothing more, so a
    test can build a source that is granted one right and not another and
    prove that one grant never implies a second.
    """
    import identity
    import journal

    rel_path = "sources/%s.md" % slug
    body = body if body is not None else SOURCE_BODY % ("Source " + slug)
    # The bytes are written by `commit_operation` and not beforehand: writing
    # them first and then committing the same bytes is a no-change refusal,
    # which is the journal doing its job rather than a fixture problem.
    record = identity.rights_default()
    record.update(rights or {})
    object_id = identity.new_object_id()
    journal.commit_operation(
        base=root, object_id=object_id, kind="source", rel_path=rel_path,
        operation=operation, new_bytes=body.encode("utf-8"),
        expected_fingerprint=None, actor_kind="agent",
        actor_name="corpus-14b", create_if_missing=True, rights=record)
    return object_id


def packaged_source(root, slug, rights=None):
    """Register one source whose `package` right is granted, so a package
    has something it may legitimately carry."""
    grants = {"package": "granted"}
    grants.update(rights or {})
    return register_source(root, slug, grants)


def linked_source(root, slug):
    """Register one source through `journal.op_link` and grant its `package`
    right.

    The grant is the point: a linked file stays out of a package because
    linking preserves external identity and location, not because nobody
    granted permission. Granting the right first is what makes the
    `external-link` loss row mean what it says.
    """
    import journal

    rel_path = "sources/%s.md" % slug
    target = os.path.join(root, rel_path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(SOURCE_BODY % ("Linked source " + slug))
    record = journal.op_link(root, "source", rel_path, "agent", "corpus-14b")
    grant_right(root, record["object_id"], "package")
    return record["object_id"]


def component_object(root, slug):
    """Register one `component` object, a kind no package carries.

    `component` is a real member of `identity.OBJECT_KINDS`, so this is a
    genuine unsupported kind rather than an invented one, and the export has
    to name it rather than skip it.
    """
    import identity
    import journal

    rel_path = "components/%s.md" % slug
    body = "# %s\n\nA synthetic component block that names nothing real.\n" % slug
    object_id = identity.new_object_id()
    journal.commit_operation(
        base=root, object_id=object_id, kind="component", rel_path=rel_path,
        operation="mint", new_bytes=body.encode("utf-8"),
        expected_fingerprint=None, actor_kind="agent",
        actor_name="corpus-14b", create_if_missing=True)
    return object_id


def unreachable_root_case(dest):
    """Register a packageable source and then remove the file it names.

    The rights are granted on purpose: an unreachable source must be reported
    as unreachable, not misreported as rights-restricted, so the export has to
    get past the rights gate before it discovers the file is gone.
    """
    object_id = packaged_source(dest, "vanished-source")
    os.remove(os.path.join(dest, "sources/vanished-source.md"))
    return object_id


def duplicate_fingerprint_sources(root):
    """Two byte-identical sources registered under two ids.

    Two ids are two objects (ID-02), so a package carries two payloads and
    two manifest entries for these. Deduplicating them into one payload would
    quietly merge two objects a copy report is supposed to surface.
    """
    body = SOURCE_BODY % "Byte identical twin"
    first = register_source(root, "twin-a", {"package": "granted"}, body=body)
    second = register_source(root, "twin-b", {"package": "granted"}, body=body)
    return first, second


def clean_machine_dest(tmp):
    """An empty restore destination plus the environment overrides that point
    a restore away from the exporting machine's home directory.

    A restore drill that quietly read the exporting machine's registry,
    settings, or evidence store would pass while proving nothing, so the
    destination shares nothing and `HOME`, `APPDATA`, and `XDG_DATA_HOME` all
    point at a second empty directory for the duration.
    """
    dest = os.path.join(tmp, "clean_machine_dest")
    home = os.path.join(tmp, "clean_machine_home")
    os.makedirs(dest, exist_ok=True)
    os.makedirs(home, exist_ok=True)
    return {"dest": dest, "home": home,
            "env": {"HOME": home, "APPDATA": home, "XDG_DATA_HOME": home}}


def build_traversing_archive(path, name="../escape.md"):
    """A zip carrying one entry whose literal name escapes its root.

    Hand-built with `writestr`, because an ordinary zip writer will not
    produce such a name. This is the Zip Slip probe: the extractor must
    refuse it, and must not clamp it to a safe name.
    """
    import zipfile

    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(name, "this file must never be written\n")
    return path


def build_symlink_archive(path, name="payload/link.md", target="../../etc"):
    """A zip carrying one symbolic-link entry, or None when this platform
    cannot express one.

    Returns None rather than a file when the entry cannot be written, so the
    caller skips that one assertion by name instead of passing silently.
    """
    import zipfile

    try:
        info = zipfile.ZipInfo(name)
        info.create_system = 3
        info.external_attr = (0o120777 << 16)
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr(info, target)
    except Exception:                                        # noqa: BLE001
        return None
    return path


def teardown(dest):
    shutil.rmtree(dest, ignore_errors=True)


def platform_capabilities(dest):
    """What this machine can express, measured rather than assumed.

    A tracer that cannot create a symbolic link must print a named skip line
    instead of passing, so the capability is measured once here and carried
    in the built corpus rather than rediscovered at each assertion.
    """
    probe = os.path.join(dest, "_platform_probe")
    os.makedirs(probe, exist_ok=True)
    target = os.path.join(probe, "target.md")
    with open(target, "w", encoding="utf-8") as fh:
        fh.write("probe\n")
    symlink = False
    try:
        os.symlink(target, os.path.join(probe, "link.md"))
        symlink = True
    except (OSError, NotImplementedError, AttributeError):
        symlink = False
    archive = build_symlink_archive(os.path.join(probe, "symlink.zip"))
    return {"symlink": symlink, "archive_symlink_entry": archive is not None}


def build_all(dest):
    """Build the whole Phase 14B corpus in one call and describe it.

    The freeze-gate tracer sets up in one statement so that what it proves is
    the graph and the package, not a page of fixture wiring. Returned keys:

    - `domains`, the three built domain descriptors, each carrying its
      course root path plus the container, objective, and source ids the
      tracer asserts against.
    - `roots`, the same three course-root paths alone, in the same order.
    - `stub_root`, a root carrying a Phase 13.9 shaped `course.md`.
    - `evidence_seeds`, one recorded event id per seeded objective, keyed by
      domain slug, so a migration scenario has real evidence to leave alone.
    - `platform`, what this machine can express, so a fallback is recorded
      as a named skip rather than passing silently.
    """
    built = build_three_domains(dest)
    stub_root = os.path.join(dest, "stub-course")
    build_stub_course(stub_root)

    seeds = {}
    for domain in built["domains"]:
        if domain["slug"] != "lantern-computing":
            continue
        seeds[domain["slug"]] = [
            seed_objective_evidence(domain["root"], domain["objectives"][0])]

    return {
        "dest": dest,
        "domains": built["domains"],
        "roots": [d["root"] for d in built["domains"]],
        "stub_root": stub_root,
        "evidence_seeds": seeds,
        "platform": platform_capabilities(dest),
        "built": built["built"],
        "declared": built["declared"],
    }


# The four objectives plan 15A-02 recommends over, in authored order. The
# fourth deliberately gets no source binding: an objective with nothing behind
# it is the case TREAT-01's degraded clause is about, and a corpus that never
# produces one cannot prove the untreated report works.
RECOMMENDATION_OBJECTIVES = (
    "Describe the meridian field response intake sequence.",
    "Classify a lantern computing loop by its termination condition.",
    "Solve an orrery algebra system by elimination.",
    "Summarize the meridian field response handoff record.",
)

RECOMMENDATION_SOURCE_BODY = (
    "# %s\n\nA synthetic passage for the Phase 15A recommendation fixture.\n"
    "It names no real course, book, or learner, and its content is fixed so a\n"
    "rebuild is byte-identical.\n"
)


def build_recommendation_fixture(dest):
    """One course root with four objectives, two sources, and one real gap.

    Built on the corpus's first domain rather than beside it, so the
    recommendation pass runs over a course that already carries containers,
    edges, and an authored objective order rather than a bare shell.

    Two sources, deliberately unequal: the first grants `transform`, which is
    what a guided lesson consumes, and the second grants nothing at all, so a
    rights refusal is reachable without editing the fixture. The fourth
    objective is bound to no source, so `no-source-bound` is reachable too.
    """
    import course
    import graph
    import identity
    import journal

    built = build_three_domains(dest)
    domain = built["domains"][0]
    root = domain["root"]

    source_object_ids = []
    for slug, rights_grant in (("recommendation-granted",
                                {"transform": "granted", "read": "granted"}),
                               ("recommendation-unknown", {})):
        rel = "sources/%s.md" % slug
        os.makedirs(os.path.join(root, "sources"), exist_ok=True)
        with open(os.path.join(root, rel), "w", encoding="utf-8") as fh:
            fh.write(RECOMMENDATION_SOURCE_BODY % slug)
        rights = identity.rights_default()
        rights.update(rights_grant)
        entry = journal.op_link(root, "source", rel, "agent", "corpus-15a",
                                rights=rights)
        source_object_ids.append(entry["object_id"])

    read = course.read_course(root)
    doc = read["doc"]
    container = domain["containers"][0]
    objective_ids = [graph.add_objective(doc, statement, container=container)["id"]
                     for statement in RECOMMENDATION_OBJECTIVES]
    for object_id, title in zip(source_object_ids,
                                ("Recommendation source, granted",
                                 "Recommendation source, unknown rights")):
        doc["sources"].append(graph.new_record("Sources", {
            "source_object_id": object_id, "title": title,
            "note": "rights are recorded on the source object, never here"}))
    course.write_course(root, doc, read["fingerprint"], "agent", "corpus-15a")

    # The first three objectives get a source binding; the fourth gets none.
    # Bound through course.bind_source so the rights gate runs, which is why
    # only the granted source can be bound.
    for objective_id in objective_ids[:3]:
        course.bind_source(root, objective_id, source_object_ids[0],
                           locator="section 1", state="unknown",
                           confidence="unknown", actor_kind="agent",
                           actor_name="corpus-15a")

    return {
        "dest": dest,
        "course_root": root,
        "objective_ids": objective_ids,
        "unbound_objective_id": objective_ids[3],
        "source_object_ids": source_object_ids,
        "granted_source_object_id": source_object_ids[0],
        "unknown_source_object_id": source_object_ids[1],
        "domain_objectives": domain["objectives"],
    }


# The five coverage objectives, in authored order. Fictional, fixed, and
# chosen so each one lands on exactly one of the five TREAT-02 states.
COVERAGE_OBJECTIVES = (
    "State the meridian field response intake order.",
    "Name the two checks that precede transport.",
    "Recall the handoff record fields.",
    "Decide when a second responder is called.",
    "Describe the equipment check cadence.",
)

# The decoy's objective. Its statement is reproduced verbatim as a heading in
# the source text, so a similarity matcher would call it a perfect match. It
# must still classify unknown, because the match kind says heading-similarity.
COVERAGE_DECOY_OBJECTIVE = "Summarize the equipment check cadence."


def _passage(seed, length):
    """A deterministic fictional passage of exactly `length` characters.

    Built by repeating a fixed sentence and truncating, so the length is exact
    and a rebuild is byte-identical. The exact length is what matters: the thin
    boundary is asserted at 239 and 240 characters, and a fixture that could
    not hit those two numbers could not prove the boundary.
    """
    sentence = ("The %s procedure is recorded here for the field response "
                "fixture and names no real course, book, or learner. " % seed)
    return (sentence * (length // len(sentence) + 1))[:length]


def build_coverage_fixture(dest):
    """One course root plus one claim group per TREAT-02 state, and a decoy.

    Every state is produced by real claim data rather than by writing the state
    string, so a classifier regression fails here instead of passing against a
    hand-written expectation.
    """
    import course
    import director
    import graph
    import identity
    import journal

    built = build_three_domains(dest)
    root = built["domains"][0]["root"]

    covered_locator = _passage("intake", 240)
    thin_locator = _passage("transport", 239)
    unknown_locator = _passage("handoff", 300)
    conflict_locator_a = _passage("second-responder", 260)
    conflict_locator_b = _passage("equipment", 260)
    decoy_locator = COVERAGE_DECOY_OBJECTIVE + " " + _passage("cadence", 260)

    source_body = "\n\n".join([
        "# Field response coverage fixture",
        covered_locator,
        thin_locator,
        unknown_locator,
        conflict_locator_a,
        conflict_locator_b,
        "## " + COVERAGE_DECOY_OBJECTIVE,
        decoy_locator,
        "",
    ])

    rel = "sources/coverage-fixture.md"
    os.makedirs(os.path.join(root, "sources"), exist_ok=True)
    with open(os.path.join(root, rel), "w", encoding="utf-8") as fh:
        fh.write(source_body)
    rights = identity.rights_default()
    rights.update({"read": "granted", "transform": "granted"})
    entry = journal.op_link(root, "source", rel, "agent", "corpus-15a",
                            rights=rights)
    source_object_id = entry["object_id"]

    read = course.read_course(root)
    doc = read["doc"]
    container = built["domains"][0]["containers"][0]
    objective_ids = [
        graph.add_objective(doc, statement, container=container)["id"]
        for statement in COVERAGE_OBJECTIVES]
    decoy_objective_id = graph.add_objective(
        doc, COVERAGE_DECOY_OBJECTIVE, container=container)["id"]
    doc["sources"].append(graph.new_record("Sources", {
        "source_object_id": source_object_id,
        "title": "Coverage fixture source",
        "note": "rights are recorded on the source object, never here"}))
    course.write_course(root, doc, read["fingerprint"], "agent", "corpus-15a")

    for objective_id, locator in zip(objective_ids,
                                     (covered_locator, thin_locator,
                                      unknown_locator, conflict_locator_a,
                                      conflict_locator_b)):
        course.bind_source(root, objective_id, source_object_id,
                           locator=locator, state="unknown",
                           confidence="high", actor_kind="agent",
                           actor_name="corpus-15a")

    def claim(objective_id, source_id, locator, match_kind, confidence,
              assertion=""):
        return director.coverage_claim(
            [], objective_id, source_id, locator, match_kind, confidence,
            assertion, source_body)[0]

    claims = {
        # A resolving locator, a 240-character span, high confidence.
        "covered": [claim(objective_ids[0], source_object_id, covered_locator,
                          "locator", "high")],
        # The same shape one character shorter. The boundary, from below.
        "thin": [claim(objective_ids[1], source_object_id, thin_locator,
                       "locator", "high")],
        # No source at all. Nothing to be covered by.
        "missing": [claim(objective_ids[2], "", "", "none", "high")],
        # Two resolving claims that say different things about one objective.
        "conflicting": [
            claim(objective_ids[3], source_object_id, conflict_locator_a,
                  "locator", "high",
                  "The intake sequence begins with scene safety."),
            claim(objective_ids[3], source_object_id, conflict_locator_b,
                  "locator", "high",
                  "The intake sequence begins with airway assessment.")],
        # A resolving locator whose confidence is unknown. Unverifiable reads
        # unknown, never covered.
        "unknown": [claim(objective_ids[4], source_object_id, unknown_locator,
                          "locator", "unknown")],
    }

    decoy_claim = claim(decoy_objective_id, source_object_id, decoy_locator,
                        "heading-similarity", "high")

    return {
        "dest": dest,
        "course_root": root,
        "source_texts": {source_object_id: source_body},
        "source_object_id": source_object_id,
        "objective_ids": objective_ids,
        "decoy_objective_id": decoy_objective_id,
        "claims": claims,
        "decoy_claim": decoy_claim,
    }
