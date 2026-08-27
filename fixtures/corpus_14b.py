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
