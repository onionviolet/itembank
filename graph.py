"""The typed course graph kernel: the pure transform layer over one course
sidecar's readable tables.

`graph.py` is to the course graph what `model.py` is to a bank: the one place
that turns text into records and records back into text. It is a peer of
`model.py` and `identity.py` in the model tier, not an extension of either,
and it performs no file input or output of any kind. It never imports
`model`, `runtime`, `journal`, or `evidence`. A runtime-tier caller
(`course.py`) supplies the text and takes the bytes back.

This module reads and writes only this phase's own course sidecar tables and
never bank or lesson bytes, so `model.py` stays the one parser of assessment
and lesson content. Reading pipe-table records outside `model.py` is already
shipped precedent: `surfaces/day.py:129 parse_lanes` reads `lanes.md` the same
way. A sidecar reader is additive machinery over a records file, not a second
document model.

This module computes no completion, mastery, readiness, or progress value of
any kind. That tuple belongs to GRAPH-03, is owned by Phase 16C, and is read
over the graph rather than stored in it.

The format is additive by construction rather than by promise: a section this
build does not recognize and a column this build does not recognize both
survive a parse and re-serialize byte for byte, so an older build rewriting a
newer build's file never destroys what it could not read.
"""
import identity

COURSE_GRAPH_VERSION = 1

# The frozen four-name edge vocabulary from D-14A-1. An edge is identified by
# the tuple (source, edge_type, target) and is never given a minted id and
# never identified by a hash of its own record: hashing the record would make
# editing an edge's rationale look like a different edge.
EDGE_TYPES = ("prerequisite-of", "covers-objective", "source-supports",
              "treatment-of")

# The name a later plan degrades an unverifiable prerequisite claim to. Named
# here so the vocabulary is complete in one place; plan 14B-02 owns the
# degrade path itself.
DEGRADED_EDGE_TYPE = "recommended-before"

EDGE_AUTHORITIES = ("authored", "imported", "proposed")

EDGE_CONFIDENCES = ("high", "medium", "low", "unknown")

# `hard-gate` is the exceptional value GRAPH-02 names. It is never a default,
# a human has to write it explicitly, and it is never reachable from an
# unrecognized edge type: an edge this build cannot understand can only ever
# be advisory. Blocking a learner is not something a typo may do.
EDGE_OVERRIDES = ("advisory", "recommended-before", "hard-gate")

# Every default is the least-blocking value in its set, so an unrecognized or
# missing cell can only ever move a field away from blocking, never toward it.
EDGE_FIELD_DEFAULTS = {
    "authority": "proposed",
    "confidence": "unknown",
    "override": "advisory",
}

EDGE_CLOSED_SETS = {
    "authority": EDGE_AUTHORITIES,
    "confidence": EDGE_CONFIDENCES,
    "override": EDGE_OVERRIDES,
}

# The authority an edge reads as once its type has been downgraded. It sits
# deliberately outside EDGE_AUTHORITIES: a relation this build does not
# recognize is not making any of the three authority claims, and saying so in
# a distinct word is more honest than picking the least wrong one.
DEGRADED_AUTHORITY = "advisory"

# Documentation only. This tuple is never used in a membership test and no
# other tuple, frozenset, or comparison in this module restricts a container
# label, because GRAPH-01 requires a local structural label to be accepted
# without a schema change. A course that calls its unit a fortnight is not
# wrong, and finding out would cost a release.
CONTAINER_LABEL_EXAMPLES = ("program", "semester", "module", "week", "unit",
                            "chapter")


# TREAT-01's vocabulary, canonical in `.planning/REQUIREMENTS.md`. It is closed
# and this phase adds no twelfth value. Phase 14B owns only the record shape;
# choosing which treatment an objective gets is Phase 15A's director work.
TREATMENT_KINDS = ("direct-reading", "excerpt", "guided-lesson",
                   "notes-or-terms", "worked-example",
                   "visual-or-demonstration", "practice", "formal-test",
                   "assessment-first-diagnostic", "learner-artifact",
                   "human-review")

# Which rights operation each treatment consumes. Every value is a member of
# `identity.RIGHTS_OPERATIONS`. This mapping is the plan's decision and not the
# executor's: leaving it open would have produced eleven separate judgement
# calls at eleven call sites. Reading a source is `read`; reproducing part of
# it is `quote`; making something new out of it is `transform`.
TREATMENT_RIGHTS = {
    "direct-reading": "read",
    "excerpt": "quote",
    "guided-lesson": "transform",
    "notes-or-terms": "transform",
    "worked-example": "transform",
    "visual-or-demonstration": "transform",
    "practice": "transform",
    "formal-test": "transform",
    "assessment-first-diagnostic": "transform",
    "learner-artifact": "read",
    "human-review": "read",
}

BINDING_KINDS = ("source", "treatment")

# TREAT-02's vocabulary. There is deliberately no `verified` and no `assumed`
# member: coverage is reported, never claimed, and heading or name similarity
# alone can never produce `covered`. Making `covered` unreachable by
# degradation is how that rule is enforced rather than merely stated.
BINDING_STATES = ("covered", "thin", "missing", "conflicting", "unknown")

# A coverage claim points at a locator and reproduces nothing, so it consumes
# `read`. Quoting is what `excerpt` does. Even so a freshly minted source
# refuses, because `read` also defaults to unknown and unknown is restrictive.
SOURCE_BINDING_RIGHT = "read"

OBJECTIVE_ORIGINS = ("local", "imported")

# GRAPH-04's five triggers. A split, a merge, a rename, a changed demand, and
# an overlay are all the same shape of fact: identity moved, and a reviewer
# has to be able to see why. "demand-change" is carried as a kind and nothing
# more: no artifact this phase read defines a demand vocabulary, so none is
# invented here.
MIGRATION_KINDS = ("split", "merge", "rename", "demand-change", "overlay")

# Phase 14B records proposals only. "accepted" and "rejected" are named so
# the vocabulary is complete in one place and a later reviewer surface does
# not invent a second spelling; no code path in this phase produces either.
MIGRATION_STATES = ("proposed", "accepted", "rejected")

MIGRATION_PROPOSED = "proposed"

# The only two things this module will ever say about evidence. Two state
# words, never a count, a percentage, a completion, or a mastery value:
# GRAPH-03 forbids the graph from producing an aggregate, and a vocabulary of
# exactly two words is how that is enforced rather than merely intended.
EVIDENCE_CLAIM_STATES = ("unknown", "present")


SECTION_ORDER = ("Course", "Structure", "Objectives", "Sources", "Edges",
                 "Bindings", "Migrations", "Log")

HEADER_FIELDS = ("graph_schema_version", "course_object_id", "title")

# The known column set per section. A column in the source text that is not
# named here is preserved on the record under `extra` and re-emitted in its
# original position, which is what makes the round trip byte-stable.
SECTION_COLUMNS = {
    "Structure": ("id", "label", "parent", "order", "title"),
    "Objectives": ("id", "container", "order", "statement", "origin",
                   "import_version", "overlays"),
    "Sources": ("source_object_id", "title", "note"),
    "Edges": ("source", "edge_type", "target", "authority", "rationale",
              "confidence", "override"),
    "Bindings": ("binding_kind", "objective", "source_object_id",
                 "treatment_kind", "locator", "state", "confidence",
                 "rights_snapshot"),
    "Migrations": ("migration_id", "kind", "from", "to", "rationale",
                   "state", "actor", "timestamp"),
    "Log": ("timestamp", "note"),
}

# The document key each section's records live under.
SECTION_KEYS = {
    "Structure": "structure",
    "Objectives": "objectives",
    "Sources": "sources",
    "Edges": "edges",
    "Bindings": "bindings",
    "Migrations": "migrations",
    "Log": "log",
}

TITLE_LINE = "# Course graph"

PREAMBLE = (
    "This file is the durable cross-object course graph for this course. It is",
    "plain Markdown on purpose: it stays readable and diffable by hand, and it",
    "never becomes the only understandable copy of anything it records. Edges",
    "that relate two independently identified objects are written here.",
)


class GraphError(Exception):
    """A typed course-graph failure: machine-readable `code` plus message,
    the same two-argument shape `identity.IdentityError` uses."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def split_row(line):
    """One pipe-table row into stripped cells, the shape
    `surfaces/day.py:86 split_row` already uses."""
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_rule_row(cells):
    return bool(cells) and all(
        c == "" or set(c) <= set("-:") and "-" in c for c in cells)


def _blank(line):
    return line.strip() == ""


def new_course(title, course_object_id):
    """A fresh, empty course document. Every section is empty and no edge
    exists: structural order mints no prerequisite edge (GRAPH-01)."""
    doc = {
        "header": {
            "graph_schema_version": COURSE_GRAPH_VERSION,
            "course_object_id": course_object_id,
            "title": title,
        },
    }
    for section in SECTION_ORDER[1:]:
        doc[SECTION_KEYS[section]] = []
    doc["unknown_sections"] = []
    doc["upgraded_from"] = None
    return doc


def new_record(section, values):
    """One record carrying its own column layout, so an unrecognized column
    is re-emitted in the position it was read from rather than appended."""
    known = SECTION_COLUMNS[section]
    record = {col: values.get(col, "") for col in known}
    record["extra"] = {}
    record["columns"] = list(known)
    return record


def _sections(lines):
    """Split the document body into (name, body_lines) pairs, with the
    preamble under the name None. Trailing blank lines are trimmed from each
    body so re-serialization can supply the separators itself."""
    out, name, body = [], None, []
    for line in lines:
        if line.startswith("## "):
            while body and _blank(body[-1]):
                body.pop()
            out.append((name, body))
            name, body = line[3:].strip(), []
        else:
            body.append(line)
    while body and _blank(body[-1]):
        body.pop()
    out.append((name, body))
    return out


def _parse_table(section, body):
    """Records from one section's body, or a raise if the body is not a
    table. Returns (columns, records)."""
    rows = [ln for ln in body if not _blank(ln)]
    for line in rows:
        if not line.lstrip().startswith("|"):
            raise GraphError(
                "graph.malformed_section",
                "the section %s is not a table and cannot be read as "
                "records; the file is preserved unchanged and no write is "
                "attempted" % section)
    if not rows:
        return list(SECTION_COLUMNS[section]), []
    columns = split_row(rows[0])
    known = SECTION_COLUMNS[section]
    records = []
    for line in rows[1:]:
        cells = split_row(line)
        if is_rule_row(cells):
            continue
        record, extra = {}, {}
        for i, col in enumerate(columns):
            value = cells[i] if i < len(cells) else ""
            if col in known:
                record[col] = value
            else:
                extra[col] = value
        for col in known:
            record.setdefault(col, "")
        record["extra"] = extra
        record["columns"] = list(columns)
        records.append(record)
    return columns, records


def parse_course(text):
    """Text into a course document. Performs no file input or output: the
    caller supplies the text and the file on disk is never opened here, which
    is why a malformed section can be refused with the file provably
    unchanged."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if not lines or lines[0] != TITLE_LINE:
        raise GraphError(
            "graph.malformed_section",
            "the section %s is not a table and cannot be read as records; "
            "the file is preserved unchanged and no write is attempted"
            % "Course")

    parts = _sections(lines)
    preamble = parts[0][1]

    header, header_seen = {}, False
    for line in preamble:
        if line.lstrip().startswith("|"):
            cells = split_row(line)
            if is_rule_row(cells):
                continue
            if not header_seen:
                header_seen = True
                continue
            if len(cells) >= 2:
                header[cells[0]] = cells[1]
    if "graph_schema_version" not in header:
        raise GraphError(
            "graph.malformed_section",
            "the section %s is not a table and cannot be read as records; "
            "the file is preserved unchanged and no write is attempted"
            % "Course")
    try:
        declared = int(header["graph_schema_version"])
    except (TypeError, ValueError):
        raise GraphError(
            "graph.malformed_section",
            "the section %s is not a table and cannot be read as records; "
            "the file is preserved unchanged and no write is attempted"
            % "Course")
    if declared > COURSE_GRAPH_VERSION:
        raise GraphError(
            "graph.future_schema_version",
            "this course graph declares schema version %d and this build "
            "understands version %d; refusing to read it rather than "
            "silently dropping fields it does not know"
            % (declared, COURSE_GRAPH_VERSION))
    header["graph_schema_version"] = declared

    doc = {"header": header}
    doc["upgraded_from"] = None
    for section in SECTION_ORDER[1:]:
        doc[SECTION_KEYS[section]] = []
    doc["unknown_sections"] = []

    for name, body in parts[1:]:
        if name in SECTION_KEYS:
            _columns, records = _parse_table(name, body)
            doc[SECTION_KEYS[name]] = records
        else:
            doc["unknown_sections"].append({"name": name, "body": list(body)})

    # The version check above happens before a single section is read, and
    # deliberately so: an older build that partially reads a newer sidecar and
    # then rewrites it destroys the fields it did not understand. Refusing
    # first is what makes that impossible rather than merely unlikely.
    if declared < COURSE_GRAPH_VERSION:
        doc = upgrade_document(doc, declared)
        doc["upgraded_from"] = declared
    return doc


def _emit_table(section, records):
    columns = list(records[0]["columns"]) if records \
        else list(SECTION_COLUMNS[section])
    known = SECTION_COLUMNS[section]
    out = ["| " + " | ".join(columns) + " |",
           "|" + "|".join(["---"] * len(columns)) + "|"]
    for record in records:
        cells = []
        for col in record["columns"]:
            if col in known:
                cells.append(str(record.get(col, "")))
            else:
                cells.append(str(record["extra"].get(col, "")))
        out.append("| " + " | ".join(cells) + " |")
    return out


def serialize_course(doc):
    """A course document back to plain Markdown. Unknown sections and unknown
    columns are re-emitted verbatim, so a build that does not understand a
    later build's fields still cannot destroy them."""
    out = [TITLE_LINE, ""]
    out.extend(PREAMBLE)
    out.append("")
    out.append("| field | value |")
    out.append("|---|---|")
    for field in HEADER_FIELDS:
        out.append("| %s | %s |" % (field, doc["header"].get(field, "")))
    for field, value in doc["header"].items():
        if field not in HEADER_FIELDS:
            out.append("| %s | %s |" % (field, value))

    for section in SECTION_ORDER[1:]:
        out.append("")
        out.append("## " + section)
        out.append("")
        out.extend(_emit_table(section, doc[SECTION_KEYS[section]]))

    for unknown in doc["unknown_sections"]:
        out.append("")
        out.append("## " + unknown["name"])
        out.extend(unknown["body"])

    return "\n".join(out) + "\n"


def add_container(doc, label, title, parent="", order=None):
    """Add one structural container and return it. Adds zero edges: a
    container's position in the outline is structure, not a prerequisite
    claim (GRAPH-01)."""
    if order is None:
        order = len(doc["structure"]) + 1
    record = new_record("Structure", {
        "id": identity.new_object_id(), "label": label, "parent": parent,
        "order": str(order), "title": title})
    doc["structure"].append(record)
    return record


def add_objective(doc, statement, container="", order=None, origin="local",
                  import_version="", objective_id=None):
    """Add one objective and return it. Adds zero edges, for the same reason
    `add_container` does.

    Passing `objective_id` for a row that already exists is refused when that
    row was imported: GRAPH-01 binds an imported scope as an immutable
    version, so a revision is a sibling overlay record and never a rewrite.
    """
    if objective_id is not None:
        existing = _objective_by_id(doc, objective_id)
        if existing is not None and existing.get("origin") == "imported":
            raise GraphError(
                "graph.imported_objective_immutable",
                "objective %s was imported at version %s and is never edited "
                "in place; record a local overlay with "
                "graph.overlay_objective instead"
                % (objective_id, existing.get("import_version", "")))
    if order is None:
        order = len(doc["objectives"]) + 1
    record = new_record("Objectives", {
        "id": objective_id or identity.new_object_id(), "container": container,
        "order": str(order), "statement": statement, "origin": origin,
        "import_version": import_version, "overlays": ""})
    doc["objectives"].append(record)
    return record


def add_edge(doc, source, edge_type, target, authority="proposed",
             rationale="", confidence="unknown", override="advisory"):
    """Add one edge and return it.

    An edge is deliberately given no minted id: its identity is the tuple
    (source, edge_type, target), so editing its rationale edits that edge
    rather than creating a different one.

    A duplicate key is refused rather than merged or recorded twice, a self
    edge is refused, and an endpoint this graph does not know is refused. All
    three are refusals by name: a graph that quietly absorbs a contradiction
    is a graph nobody can trust to answer a question.
    """
    if source == target:
        raise GraphError(
            "graph.self_edge",
            "an edge cannot point an object at itself: %s %s %s"
            % (source, edge_type, target))
    known = _endpoint_ids(doc)
    for endpoint in (source, target):
        if endpoint not in known:
            raise GraphError(
                "graph.unknown_objective",
                "%s is not a recorded objective or source in this course "
                "graph" % endpoint)
    key = (source, edge_type or "", target)
    for existing in doc["edges"]:
        if edge_key(existing) == key:
            raise GraphError(
                "graph.duplicate_edge",
                "an edge %s %s %s is already recorded; a duplicate edge is "
                "refused, never merged and never recorded twice"
                % (source, edge_type, target))
    record = new_record("Edges", {
        "source": source, "edge_type": edge_type, "target": target,
        "authority": authority, "rationale": rationale,
        "confidence": confidence, "override": override})
    doc["edges"].append(record)
    return record


def _depth(containers_by_id, container_id):
    depth, seen = 0, set()
    current = container_id
    while current and current in containers_by_id and current not in seen:
        seen.add(current)
        current = containers_by_id[current].get("parent", "")
        if current:
            depth += 1
    return depth


def outline_projection(doc):
    """The course as plain Markdown, in authored order.

    This is a projection and never a second source of truth: it is rebuilt
    from the sidecar every time and nothing reads it back.
    """
    out = ["# " + str(doc["header"].get("title", ""))]
    objectives = doc["objectives"]
    if not objectives:
        out.append("")
        out.append("No objectives are recorded yet.")
        return "\n".join(out) + "\n"

    superseded = set(o["overlays"] for o in objectives if o.get("overlays"))
    objectives = [o for o in objectives if o["id"] not in superseded]
    if not objectives:
        out.append("")
        out.append("No objectives are recorded yet.")
        return "\n".join(out) + "\n"

    containers_by_id = {c["id"]: c for c in doc["structure"]}
    by_container = {}
    unplaced = []
    for index, obj in enumerate(objectives):
        container = obj.get("container", "")
        if container and container in containers_by_id:
            by_container.setdefault(container, []).append((_order_key(obj, index), obj))
        else:
            unplaced.append((_order_key(obj, index), obj))
    for group in by_container.values():
        group.sort(key=lambda pair: pair[0])
    unplaced.sort(key=lambda pair: pair[0])

    ordered_containers = sorted(
        ((_order_key(c, i), c) for i, c in enumerate(doc["structure"])),
        key=lambda pair: pair[0])
    for _key, container in ordered_containers:
        level = 2 + _depth(containers_by_id, container["id"])
        out.append("")
        out.append("%s %s (%s)" % ("#" * level, container["title"],
                                   container["label"]))
        out.append("")
        for _k, obj in by_container.get(container["id"], []):
            out.append("- %s [%s]" % (obj["statement"], obj["id"]))

    if unplaced:
        out.append("")
        out.append("## Unplaced")
        out.append("")
        for _k, obj in unplaced:
            out.append("- %s [%s]" % (obj["statement"], obj["id"]))

    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + "\n"


def validate_edge(record):
    """The effective reading of one edge row, as a NEW dict. Never mutates
    its input and never returns None.

    The four-name vocabulary is frozen by D-14A-1, and this plan adds no
    fifth. An unrecognized edge type is kept and downgraded rather than
    dropped, which is exactly where this function differs from
    `evidence.events`: that reader drops an unrecognized record, and GRAPH-02
    requires the opposite, because a relation a human wrote down is evidence
    about the course even when this build cannot act on it.

    An unrecognized value can only ever move a field toward its
    least-blocking default. Nothing here can reach `hard-gate`.
    """
    original_type = record.get("edge_type") or ""
    known = original_type in EDGE_TYPES

    out = {
        "source": record.get("source", ""),
        "target": record.get("target", ""),
        "rationale": record.get("rationale", "") or "",
        "effective_type": original_type if known else DEGRADED_EDGE_TYPE,
        "original_type": original_type,
    }
    for field, closed in EDGE_CLOSED_SETS.items():
        raw = record.get(field, "") or ""
        out["original_" + field] = raw
        out[field] = raw if raw in closed else EDGE_FIELD_DEFAULTS[field]
    if not known:
        # An edge this build cannot read never carries authority and never
        # blocks, whatever the row said.
        out["authority"] = DEGRADED_AUTHORITY
        out["override"] = EDGE_FIELD_DEFAULTS["override"]
    return out


def edge_key(record):
    """The identity of one edge: the tuple (source, edge_type, target), read
    from the ORIGINAL type rather than the effective one, so two different
    unregistered relations between the same pair stay distinct instead of
    collapsing into one downgraded edge."""
    return (record.get("source", ""), record.get("edge_type") or "",
            record.get("target", ""))


def _endpoint_ids(doc):
    ids = set(o["id"] for o in doc["objectives"])
    ids.update(s["source_object_id"] for s in doc["sources"])
    ids.update(c["id"] for c in doc["structure"])
    return ids


def _order_key(record, index):
    """Sort by the authored `order` cell, falling back to authored list
    position. Both are what the human wrote; neither is inferred."""
    raw = record.get("order", "")
    try:
        return (0, int(raw), index)
    except (TypeError, ValueError):
        return (1, 0, index)


def validate_order(doc):
    """Warnings about the authored order, one string per violated
    prerequisite, plus one line naming a prerequisite cycle if one exists.

    This reports and never corrects: the authored sequence is left exactly as
    the human wrote it, because authored order is primary and a projection
    that silently reorders makes every future diff unreadable. Only edges
    whose effective type is `prerequisite-of` are considered, so an advisory
    downgraded relation cannot be violated at all.
    """
    positions = {}
    for index, objective in enumerate(doc["objectives"]):
        positions[objective["id"]] = index

    warnings, pairs = [], []
    for record in doc["edges"]:
        edge = validate_edge(record)
        if edge["effective_type"] != "prerequisite-of":
            continue
        prereq, dependent = edge["source"], edge["target"]
        if prereq not in positions or dependent not in positions:
            continue
        pairs.append((prereq, dependent))
        if positions[prereq] > positions[dependent]:
            warnings.append(
                "prerequisite %s appears after dependent %s in the authored "
                "order; the authored order is unchanged and this is reported "
                "for review" % (prereq, dependent))
    if pairs:
        try:
            propose_order(list(positions), pairs)
        except GraphError as err:
            if err.code == "graph.prerequisite_cycle":
                warnings.append(err.message)
            else:
                raise
    return warnings


def propose_order(objective_ids, prerequisite_edges):
    """A proposed order over `objective_ids` satisfying every prerequisite.

    This is a fallback, not the normal path. The normal path reads the
    authored order verbatim; this runs only when a set of objectives carries
    prerequisite edges and no authored container placement to read instead.

    Kahn's algorithm with the ready set sorted ascending by object id before
    each pop, and successors sorted before each decrement. The tie-break is
    not decoration: without it two runs over one unchanged graph can differ
    wherever a topological tie exists, and every diff becomes noise. Dict
    iteration order is not a specification.
    """
    ids = list(objective_ids)
    known = set(ids)
    successors = {i: set() for i in ids}
    indegree = {i: 0 for i in ids}
    for edge in prerequisite_edges:
        if isinstance(edge, dict):
            prereq, dependent = edge.get("source", ""), edge.get("target", "")
        else:
            prereq, dependent = edge
        if prereq not in known or dependent not in known:
            continue
        if dependent in successors[prereq]:
            continue
        successors[prereq].add(dependent)
        indegree[dependent] += 1

    ready = sorted(i for i in ids if indegree[i] == 0)
    out = []
    while ready:
        current = ready.pop(0)
        out.append(current)
        for nxt in sorted(successors[current]):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
        ready.sort()

    if len(out) != len(ids):
        remaining = sorted(i for i in ids if i not in set(out))
        raise GraphError(
            "graph.prerequisite_cycle",
            "a prerequisite cycle involves at least these objectives: %s; "
            "reported for review, never silently broken"
            % ", ".join(remaining))
    return out


def public_api():
    """This module's public callable names, sorted.

    The test asserts this against an explicit expected list, so the module's
    surface cannot grow without a plan edit that also edits that list. That
    is what keeps a completion, mastery, or readiness computation from ever
    appearing here quietly: GRAPH-03's honest-progress tuple is read over the
    graph and is never stored in it.
    """
    out = []
    for name, value in globals().items():
        if name.startswith("_") or not callable(value):
            continue
        if isinstance(value, type):
            continue
        if getattr(value, "__module__", None) != __name__:
            continue
        out.append(name)
    return sorted(out)


def treatment_right(treatment_kind):
    """The rights operation `treatment_kind` consumes."""
    if treatment_kind not in TREATMENT_RIGHTS:
        raise GraphError(
            "graph.unknown_treatment_kind",
            "%s is not one of the eleven treatment kinds in TREAT-01; the "
            "vocabulary is closed and this phase adds no twelfth"
            % treatment_kind)
    return TREATMENT_RIGHTS[treatment_kind]


def add_source(doc, source_object_id, title, note=""):
    """Record a reference to a source object in the sidecar.

    The row's `title` is a derived, regenerable annotation for a human reader:
    the source file owns its own title, and nothing is ever validated against
    this copy (D-12.6-8). A source's rights live on the source object in the
    operation journal, never here.
    """
    record = new_record("Sources", {
        "source_object_id": source_object_id, "title": title, "note": note})
    doc["sources"].append(record)
    return record


def add_binding(doc, binding_kind, objective, source_object_id,
                treatment_kind="", locator="", state="unknown",
                confidence="unknown", rights_snapshot=""):
    """Record one source or treatment binding, in authored order.

    A binding is not identified by its endpoints: two bindings of the same
    objective to the same source at two different locators are two rows,
    because they are two claims about two different places.

    This function records. It enforces no rights, because it is pure and has
    no registry to read; `course.bind_source` and `course.bind_treatment` are
    the gated entry points, and they are the only ones a caller should use to
    create a binding.
    """
    if binding_kind not in BINDING_KINDS:
        raise GraphError(
            "graph.unknown_treatment_kind",
            "%s is not one of the eleven treatment kinds in TREAT-01; the "
            "vocabulary is closed and this phase adds no twelfth"
            % binding_kind)
    if treatment_kind:
        treatment_right(treatment_kind)
    known = _endpoint_ids(doc)
    if objective not in known:
        raise GraphError(
            "graph.unknown_objective",
            "%s is not a recorded objective or source in this course graph"
            % objective)
    record = new_record("Bindings", {
        "binding_kind": binding_kind, "objective": objective,
        "source_object_id": source_object_id,
        "treatment_kind": treatment_kind, "locator": locator, "state": state,
        "confidence": confidence, "rights_snapshot": rights_snapshot})
    doc["bindings"].append(record)
    return record


def validate_binding(record):
    """The effective reading of one binding row, as a NEW dict.

    An unrecognized state degrades to `unknown` and never to `covered`: a
    value this build cannot read is not evidence that an objective is
    covered, and TREAT-02 forbids inferring coverage from resemblance. The
    source string is preserved, the same way an unrecognized edge value is.
    """
    out = dict(record)
    raw_state = record.get("state", "") or ""
    out["original_state"] = raw_state
    out["state"] = raw_state if raw_state in BINDING_STATES else "unknown"
    raw_conf = record.get("confidence", "") or ""
    out["original_confidence"] = raw_conf
    out["confidence"] = raw_conf if raw_conf in EDGE_CONFIDENCES else "unknown"
    return out


def _objective_by_id(doc, objective_id):
    for record in doc["objectives"]:
        if record["id"] == objective_id:
            return record
    return None


def overlay_objective(doc, imported_objective_id, statement, actor):
    """Record a local revision of an objective as a sibling record.

    GRAPH-01 requires an imported scope to bind as an immutable version. That
    is true here by construction rather than by care: an overlay is a new row
    with its own minted id, joined to the import by an `overlays` reference
    and a recorded migration, so no code path targets the import's bytes at
    all. Nothing in an overlay chain is ever deleted; the superseded rows stay
    in the file and stop being projected.
    """
    target = _objective_by_id(doc, imported_objective_id)
    if target is None:
        raise GraphError(
            "graph.unknown_objective",
            "%s is not a recorded objective or source in this course graph"
            % imported_objective_id)

    record = new_record("Objectives", {
        "id": identity.new_object_id(),
        "container": target.get("container", ""),
        "order": str(len(doc["objectives"]) + 1),
        "statement": statement,
        "origin": "local",
        "import_version": target.get("import_version", ""),
        "overlays": imported_objective_id})
    doc["objectives"].append(record)

    doc["migrations"].append(new_record("Migrations", {
        "migration_id": identity.new_object_id(),
        "kind": "overlay",
        "from": imported_objective_id,
        "to": record["id"],
        "rationale": "a local revision recorded as an overlay, never an edit "
                     "to the import",
        "state": "proposed",
        "actor": actor,
        "timestamp": identity.utc_now()}))
    return record


def migration_proposal(kind, from_ids, to_ids, rationale, actor):
    """One reviewed migration proposal, as a plain dict of eight fields.

    A proposal is reviewed and never automatic. It carries the same
    recorded-human-decision posture `journal.reconcile` uses: the record
    names who proposed it and why, so a reviewer reading the sidecar months
    later can evaluate it without the conversation that produced it.

    Nothing in Phase 14B accepts a proposal. This function takes no `state`
    argument at all, so `state="accepted"` is a `TypeError` rather than a
    value that has to be checked, and the returned `state` is always
    `proposed`. Acceptance belongs to a reviewer and is Phase 15B's work.

    A proposal moves identity. It does not move, copy, relink, or rewrite a
    single evidence event, and this module cannot: `graph.py` imports no
    `evidence` module and performs no file input or output.
    """
    if kind not in MIGRATION_KINDS:
        raise GraphError(
            "graph.unknown_migration_kind",
            "%s is not one of the migration kinds split, merge, rename, "
            "demand-change, or overlay" % kind)
    if not str(rationale).strip():
        raise GraphError(
            "graph.empty_rationale",
            "a migration proposal needs a rationale a reviewer can evaluate; "
            "an empty rationale is refused")
    return {
        "migration_id": identity.new_object_id(),
        "kind": kind,
        "from": _id_cell(from_ids),
        "to": _id_cell(to_ids),
        "rationale": rationale,
        "state": MIGRATION_PROPOSED,
        "actor": actor,
        "timestamp": identity.utc_now(),
    }


def _id_cell(ids):
    """Several object ids in one table cell, space separated, in the order
    given. Never sorted: the order a split was proposed in is part of what
    was proposed."""
    if isinstance(ids, str):
        return ids
    return " ".join(ids)


def add_migration(doc, proposal):
    """Append one proposal to the `## Migrations` table, in authored order.

    Rows are never sorted and never rewritten, so the migration table reads
    as the history it is.
    """
    record = new_record("Migrations", dict(proposal))
    doc["migrations"].append(record)
    return record


def set_migration_state(doc, migration_id, state):
    """Refuse, by name, every attempt to settle a proposal in this phase.

    This function exists so the refusal has somewhere to live: a caller
    reaching for a way to accept a proposal finds a named refusal that says
    where acceptance actually belongs, rather than an absent function it
    might be tempted to add.
    """
    raise GraphError(
        "graph.migration_state_not_settable",
        "a migration state is set by a reviewer at acceptance time, and "
        "Phase 14B implements no acceptance path; a proposal is recorded as "
        "proposed and stays proposed")


def _require_objective(doc, objective_id):
    record = _objective_by_id(doc, objective_id)
    if record is None:
        raise GraphError(
            "graph.unknown_objective",
            "%s is not a recorded objective or source in this course graph"
            % objective_id)
    return record


def _successor(doc, source, statement):
    """One new local objective row succeeding `source`, in the same
    container. The source row is never touched."""
    return add_objective(doc, statement, container=source.get("container", ""),
                         origin="local")


def split_objective(doc, objective_id, statements, rationale, actor):
    """Split one objective into several, as a reviewed proposal.

    Returns `(records, proposal)`. The original row is left exactly as it
    was: a split adds rows and deletes none, which is the same append-only
    discipline PLANNING-DIRECTIVES section 3a requires of the rejection
    ledger, applied to objective identity. An objective the learner's
    evidence was recorded against has to stay in the file, or that evidence
    stops naming anything.

    This function takes no evidence log, no event, and no event count, and it
    cannot reach one: `graph.py` imports no `evidence` module. Historical
    evidence stays where it was recorded, and each new identity reads
    `unknown` until real evidence is recorded against it.
    """
    source = _require_objective(doc, objective_id)
    records = [_successor(doc, source, statement) for statement in statements]
    proposal = migration_proposal("split", [objective_id],
                                  [r["id"] for r in records], rationale, actor)
    add_migration(doc, proposal)
    return records, proposal


def rename_objective(doc, objective_id, statement, rationale, actor):
    """Restate one objective, as a reviewed proposal.

    Returns `(record, proposal)`. A rename is a new row plus a migration
    relation and never an edit to the original row, for the reason
    `split_objective` gives: the identity evidence was recorded against
    stays in the file.
    """
    source = _require_objective(doc, objective_id)
    record = _successor(doc, source, statement)
    proposal = migration_proposal("rename", [objective_id], [record["id"]],
                                  rationale, actor)
    add_migration(doc, proposal)
    return record, proposal


def merge_objectives(doc, objective_ids, statement, rationale, actor):
    """Merge several objectives into one, as a reviewed proposal.

    Returns `(record, proposal)`. Every merged-from row stays in the file,
    for the reason `split_objective` gives.
    """
    sources = [_require_objective(doc, oid) for oid in objective_ids]
    record = _successor(doc, sources[0], statement)
    proposal = migration_proposal("merge", list(objective_ids), [record["id"]],
                                  rationale, actor)
    add_migration(doc, proposal)
    return record, proposal


def objective_evidence_state(doc, objective_id, event_count):
    """One of exactly two words about whether an objective has any evidence.

    This function takes the count as an argument rather than reading the
    evidence store, because `graph.py` performs no file input or output and
    imports no `evidence` module.

    It returns one of two state words and never a number, because GRAPH-03
    forbids the graph from producing a completion, mastery, readiness, or
    progress value. That tuple is Phase 16C's and is read over the graph,
    never stored in it.

    It exists so GRAPH-04's degraded clause has a named function to assert
    against: unmigrated evidence stays on the original objective identity and
    reads `unknown` on the new one. `unknown` is the honest answer for a
    freshly split identity. It does not mean zero progress; it means nothing
    has been recorded here yet.
    """
    return "present" if event_count else "unknown"


def upgrade_0_to_1(doc):
    """The single step from course graph version 0 to version 1.

    Version 1 introduced the edge `override` column. This step supplies
    `advisory` for every edge that has none, which is the least-blocking
    value in the set: an upgrade never guesses a `hard-gate`, because a guess
    that blocks a learner is the one guess that costs something.
    """
    for record in doc["edges"]:
        if not record.get("override"):
            record["override"] = "advisory"
        if "override" not in record["columns"]:
            record["columns"].append("override")
    doc["header"]["graph_schema_version"] = 1
    return doc


# Keyed by the version being upgraded FROM. A named, testable step per version
# is what makes the version migration a prototype rather than a promise, which
# PLANNING-DIRECTIVES section 3a asks for by name before any course schema
# freeze.
UPGRADES = {0: upgrade_0_to_1}


def upgrade_document(doc, from_version):
    """Apply every registered upgrade step from `from_version` forward until
    the document is at `COURSE_GRAPH_VERSION`.

    A gap in the chain is refused by name rather than skipped: skipping a step
    would leave the document claiming a version whose fields it does not
    actually carry.
    """
    version = from_version
    while version < COURSE_GRAPH_VERSION:
        step = UPGRADES.get(version)
        if step is None:
            raise GraphError(
                "graph.unknown_upgrade_path",
                "no upgrade step is registered from course graph version %d; "
                "the chain to version %d is incomplete and this build refuses "
                "to guess" % (version, COURSE_GRAPH_VERSION))
        doc = step(doc)
        version += 1
    if version > COURSE_GRAPH_VERSION:
        raise GraphError(
            "graph.unknown_upgrade_path",
            "no upgrade step is registered from course graph version %d; "
            "the chain to version %d is incomplete and this build refuses to "
            "guess" % (from_version, COURSE_GRAPH_VERSION))
    return doc
