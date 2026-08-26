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
    for section in SECTION_ORDER[1:]:
        doc[SECTION_KEYS[section]] = []
    doc["unknown_sections"] = []

    for name, body in parts[1:]:
        if name in SECTION_KEYS:
            _columns, records = _parse_table(name, body)
            doc[SECTION_KEYS[name]] = records
        else:
            doc["unknown_sections"].append({"name": name, "body": list(body)})
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


def add_objective(doc, statement, container="", order=None, origin="local"):
    """Add one objective and return it. Adds zero edges, for the same reason
    `add_container` does."""
    if order is None:
        order = len(doc["objectives"]) + 1
    record = new_record("Objectives", {
        "id": identity.new_object_id(), "container": container,
        "order": str(order), "statement": statement, "origin": origin,
        "import_version": "", "overlays": ""})
    doc["objectives"].append(record)
    return record


def add_edge(doc, source, edge_type, target, authority="proposed",
             rationale="", confidence="unknown", override="advisory"):
    """Add one edge and return it.

    An edge is deliberately given no minted id: its identity is the tuple
    (source, edge_type, target), so editing its rationale edits that edge
    rather than creating a different one.
    """
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

    containers_by_id = {c["id"]: c for c in doc["structure"]}
    by_container = {}
    unplaced = []
    for obj in objectives:
        container = obj.get("container", "")
        if container and container in containers_by_id:
            by_container.setdefault(container, []).append(obj)
        else:
            unplaced.append(obj)

    for container in doc["structure"]:
        level = 2 + _depth(containers_by_id, container["id"])
        out.append("")
        out.append("%s %s (%s)" % ("#" * level, container["title"],
                                   container["label"]))
        out.append("")
        for obj in by_container.get(container["id"], []):
            out.append("- %s [%s]" % (obj["statement"], obj["id"]))

    if unplaced:
        out.append("")
        out.append("## Unplaced")
        out.append("")
        for obj in unplaced:
            out.append("- %s [%s]" % (obj["statement"], obj["id"]))

    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + "\n"
