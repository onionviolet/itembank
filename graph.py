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
import copy
import json
import re

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

READING_ACTIVATIONS = ("Now", "Library")
READING_SEQUENCE_STATUSES = ("Published", "Bounded", "unknown")
READING_ASSIGNMENT_AUTHORITIES = ("instructor", "learner", "proposed",
                                  "unknown")
READING_ASSISTANCE_STATUSES = ("specified", "unknown")

READING_OCCURRENCE_FIELDS = (
    "occurrence_id", "revision_id", "supersedes_revision_id", "course_id",
    "objective_ids", "binding_ref", "source_ref", "purpose",
    "preparation_mode", "path_role", "learning_phase", "sequence_evidence",
    "assignment_provenance", "assistance_policy")

_OPAQUE_ID_RE = re.compile(r"^[0-9a-f]{16}$")
_FINGERPRINT_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

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


# "Blueprint" is Phase 15B's one additive member (ACTIVITY-02's durable
# blueprint object, D-15B-2 option-a). It sits before "Log", so no existing
# member changes position and a sidecar carrying no ## Blueprint section
# serializes byte-identically to what it did before. `14B-FREEZE.md` carries a
# dated amendment recording the addition.
SECTION_ORDER = ("Course", "Structure", "Objectives", "Sources", "Edges",
                 "Bindings", "Migrations", "Blueprint", "Reading occurrences",
                 "Reading placement", "Log")

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
                 "rights_snapshot", "binding_id", "binding_revision_id",
                 "supersedes_binding_revision_id", "source_fingerprint"),
    # `reviewer` and `rationale_review` are Phase 15B's two additive columns
    # (RELIABILITY-03). A row written before 15B carries them as empty
    # strings, exactly as every other unfilled column reads, so a pre-15B
    # sidecar round-trips unchanged. The review rationale is a SEPARATE column
    # from the proposal's own `rationale`: the reason a change was proposed and
    # the reason it was granted are two different statements, and one column
    # would let the second overwrite the first.
    "Migrations": ("migration_id", "kind", "from", "to", "rationale",
                   "state", "actor", "timestamp", "reviewer",
                   "rationale_review"),
    # One row per accepted blueprint version. The blueprint's own eight
    # declared fields live in the document `blueprint.py` validates, not in
    # these columns: the sidecar records WHICH blueprint is bound and where it
    # came from, and duplicating its contents here would create a second copy
    # that could disagree with the first.
    "Blueprint": ("blueprint_id", "version", "construct", "citation",
                  "document"),
    "Reading occurrences": ("occurrence_id", "revision_id", "document"),
    "Reading placement": ("occurrence_id", "title", "activation"),
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
    "Blueprint": "blueprint",
    "Reading occurrences": "reading_occurrences",
    "Reading placement": "reading_placement",
    "Log": "log",
}

# Sections emitted only when they carry rows. Every section added AFTER the
# 14B freeze belongs here, because non-negotiable 4 requires a sidecar written
# before the addition to serialize byte-identically afterwards, and a section
# header emitted into a document that never had one is not byte-identical.
#
# The 14B sections are deliberately NOT optional: they emit their header and
# column row even when empty, exactly as they did at the freeze, and changing
# that would break the additivity guarantee in the other direction.
#
# One consequence, recorded rather than discovered later: a sidecar carrying an
# EMPTY `## Blueprint` section round-trips without it. No data is lost, because
# an empty section carries none, but the bytes differ. Emitting an empty
# optional section would break the pre-15B additivity proof, and that proof is
# the one non-negotiable 4 actually asks for.
OPTIONAL_SECTIONS = ("Blueprint", "Reading occurrences", "Reading placement")

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
    doc["section_columns"] = {
        section: list(SECTION_COLUMNS[section]) for section in SECTION_ORDER[1:]}
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
    doc["section_columns"] = {
        section: list(SECTION_COLUMNS[section]) for section in SECTION_ORDER[1:]}
    doc["unknown_sections"] = []

    for name, body in parts[1:]:
        if name in SECTION_KEYS:
            columns, records = _parse_table(name, body)
            doc[SECTION_KEYS[name]] = records
            doc["section_columns"][name] = columns
        else:
            doc["unknown_sections"].append({"name": name, "body": list(body)})

    # The version check above happens before a single section is read, and
    # deliberately so: an older build that partially reads a newer sidecar and
    # then rewrites it destroys the fields it did not understand. Refusing
    # first is what makes that impossible rather than merely unlikely.
    if declared < COURSE_GRAPH_VERSION:
        doc = upgrade_document(doc, declared)
        doc["upgraded_from"] = declared
    validate_reading_graph(doc)
    return doc


def _emit_table(section, records, authored_columns=None):
    columns = list(records[0]["columns"]) if records \
        else list(authored_columns or SECTION_COLUMNS[section])
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
        rows = doc[SECTION_KEYS[section]]
        if section in OPTIONAL_SECTIONS and not rows:
            continue
        out.append("")
        out.append("## " + section)
        out.append("")
        out.extend(_emit_table(
            section, rows, (doc.get("section_columns") or {}).get(section)))

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
    authored_columns = (doc.get("section_columns") or {}).get("Bindings")
    if authored_columns:
        record["columns"] = list(authored_columns)
    doc["bindings"].append(record)
    return record


def add_blueprint(doc, blueprint):
    """Record one accepted blueprint version in the sidecar.

    The whole blueprint document is stored in the row's `document` column as
    canonical JSON, and the four other columns are a human-readable projection
    of it. The document is the record; the columns are for a person reading
    the file in a diff, and nothing reads them back for a decision.

    Refuses a document that fails `schemas/blueprint.schema.json`. A sidecar
    row naming a blueprint that is not a blueprint would be a durable claim
    with nothing behind it.
    """
    import json as _json

    import blueprint as blueprint_module

    try:
        blueprint_module.validate_blueprint(blueprint)
    except blueprint_module.BlueprintError as exc:
        raise GraphError(
            "graph.blueprint_invalid",
            "the blueprint does not validate against the blueprint contract, "
            "so it is not recorded: %s" % exc.message)

    record = new_record("Blueprint", {
        "blueprint_id": blueprint["blueprint_id"],
        "version": str(blueprint["version"]),
        "construct": (blueprint.get("construct") or {}).get("statement", ""),
        "citation": (blueprint.get("citations") or [{}])[0].get("locator", ""),
        "document": _json.dumps(blueprint, ensure_ascii=False, sort_keys=True,
                                separators=(",", ":")),
    })
    doc.setdefault("blueprint", []).append(record)
    return record


def blueprints(doc):
    """Every recorded blueprint row, in authored order."""
    return list(doc.get("blueprint") or ())


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


def _reading_error(code, message):
    raise GraphError(code, message + "; the course graph is unchanged")


def _opaque_id(value, field):
    if not isinstance(value, str) or not _OPAQUE_ID_RE.fullmatch(value):
        _reading_error("graph.malformed_reading_record",
                       "%s must be a minted opaque id" % field)


def _fingerprint(value, field):
    if not isinstance(value, str) or not _FINGERPRINT_RE.fullmatch(value):
        _reading_error("graph.malformed_reading_record",
                       "%s must be a sha256 fingerprint" % field)


def _canonical_json(value):
    # A literal pipe would split the Markdown table cell. JSON permits the
    # equivalent escape, so canonical reading documents use it consistently.
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).replace("|", "\\u007c")


def _record_payload(record, section):
    payload = {key: record.get(key, "") for key in SECTION_COLUMNS[section]}
    payload["extra"] = dict(record.get("extra") or {})
    return payload


def _safe_table_cell(value):
    return (isinstance(value, str) and value == value.strip() and
            "|" not in value and "\n" not in value and "\r" not in value)


def _validate_binding_revisions(doc):
    by_pair = {}
    by_binding = {}
    objective_ids = {row.get("id") for row in doc.get("objectives") or ()}
    source_ids = {row.get("source_object_id") for row in doc.get("sources") or ()}
    for row in doc.get("bindings") or ():
        fields = (row.get("binding_id", ""), row.get("binding_revision_id", ""),
                  row.get("supersedes_binding_revision_id", ""),
                  row.get("source_fingerprint", ""))
        if not any(fields):
            continue
        if not fields[0] or not fields[1] or not fields[3]:
            _reading_error("graph.partial_binding_identity",
                           "a versioned binding row must carry both ids and "
                           "its source fingerprint")
        _opaque_id(fields[0], "binding_id")
        _opaque_id(fields[1], "binding_revision_id")
        if fields[2]:
            _opaque_id(fields[2], "supersedes_binding_revision_id")
        _fingerprint(fields[3], "source_fingerprint")
        if (row.get("binding_kind") not in BINDING_KINDS or
                row.get("objective") not in objective_ids or
                row.get("source_object_id") not in source_ids or
                (row.get("binding_kind") == "treatment" and
                 row.get("treatment_kind") not in TREATMENT_KINDS)):
            _reading_error("graph.malformed_binding_revision",
                           "a versioned binding must name known graph endpoints "
                           "and a supported binding kind")
        if any(not _safe_table_cell(row.get(field, ""))
               for field in SECTION_COLUMNS["Bindings"]):
            _reading_error("graph.malformed_binding_revision",
                           "a versioned binding contains an unsafe table value")
        pair = fields[:2]
        if pair in by_pair:
            code = ("graph.duplicate_binding_revision" if
                    _record_payload(by_pair[pair], "Bindings") ==
                    _record_payload(row, "Bindings") else
                    "graph.divergent_binding_revision")
            _reading_error(code, "binding revision %s/%s occurs more than once"
                           % pair)
        by_pair[pair] = row
        by_binding.setdefault(fields[0], []).append(row)

    for binding_id, rows in by_binding.items():
        revisions = {row["binding_revision_id"]: row for row in rows}
        children = {}
        roots = []
        for row in rows:
            parent = row.get("supersedes_binding_revision_id", "")
            if not parent:
                roots.append(row)
                continue
            if parent not in revisions:
                _reading_error("graph.missing_binding_revision",
                               "binding %s names missing revision %s"
                               % (binding_id, parent))
            children.setdefault(parent, []).append(row)
        if not roots and rows:
            _reading_error("graph.cyclic_binding_revisions",
                           "binding %s contains a revision cycle" % binding_id)
        if len(roots) != 1:
            _reading_error("graph.binding_revision_chain",
                           "binding %s must have exactly one root" % binding_id)
        if any(len(group) > 1 for group in children.values()):
            _reading_error("graph.branching_binding_revisions",
                           "binding %s has competing successor revisions"
                           % binding_id)
        seen = set()
        current = roots[0]
        while current:
            revision_id = current["binding_revision_id"]
            if revision_id in seen:
                _reading_error("graph.cyclic_binding_revisions",
                               "binding %s contains a revision cycle" % binding_id)
            seen.add(revision_id)
            next_rows = children.get(revision_id, ())
            current = next_rows[0] if next_rows else None
        if len(seen) != len(rows):
            _reading_error("graph.cyclic_binding_revisions",
                           "binding %s contains a disconnected revision cycle"
                           % binding_id)
    return by_pair


def validate_reading_occurrence(document, doc):
    """Validate one closed occurrence document against graph-known facts.

    This checks structure and pinned cross-references. It does not verify
    source bytes, locator sidecars, rights, journal acceptance, or accepted
    heads, which belong to successor operation units.
    """
    if (not isinstance(document, dict) or
            set(document) != set(READING_OCCURRENCE_FIELDS)):
        _reading_error("graph.malformed_reading_record",
                       "a reading occurrence must have exactly the published fields")
    for field in ("occurrence_id", "revision_id", "course_id"):
        _opaque_id(document[field], field)
    parent = document["supersedes_revision_id"]
    if parent is not None:
        _opaque_id(parent, "supersedes_revision_id")
    if document["course_id"] != doc["header"].get("course_object_id"):
        _reading_error("graph.reading_course_mismatch",
                       "the occurrence course_id does not match this graph")

    objective_ids = document["objective_ids"]
    if (not isinstance(objective_ids, list) or not objective_ids or
            any(not isinstance(value, str) for value in objective_ids) or
            len(set(objective_ids)) != len(objective_ids)):
        _reading_error("graph.malformed_reading_record",
                       "objective_ids must be a nonempty unique list")
    for objective_id in objective_ids:
        _opaque_id(objective_id, "objective_ids entry")
    known_objectives = {row["id"] for row in doc.get("objectives") or ()}
    if any(value not in known_objectives for value in objective_ids):
        _reading_error("graph.unknown_objective",
                       "a reading occurrence names an objective absent from the graph")

    binding_ref = document["binding_ref"]
    if (not isinstance(binding_ref, dict) or
            set(binding_ref) != {"binding_id", "binding_revision_id"}):
        _reading_error("graph.malformed_reading_record",
                       "binding_ref must be a closed binding revision reference")
    _opaque_id(binding_ref["binding_id"], "binding_ref.binding_id")
    _opaque_id(binding_ref["binding_revision_id"],
               "binding_ref.binding_revision_id")
    binding = None
    for row in doc.get("bindings") or ():
        if (row.get("binding_id") == binding_ref["binding_id"] and
                row.get("binding_revision_id") ==
                binding_ref["binding_revision_id"]):
            binding = row
            break
    if binding is None:
        _reading_error("graph.missing_binding_revision",
                       "the occurrence pins a binding revision absent from the graph")
    if (binding.get("binding_kind") != "treatment" or
            binding.get("treatment_kind") != "direct-reading"):
        _reading_error("graph.reading_binding_not_direct",
                       "a reading occurrence must pin a direct-reading treatment")
    if binding.get("objective") not in objective_ids:
        _reading_error("graph.reading_objective_mismatch",
                       "the pinned binding objective is absent from the occurrence")

    source_ref = document["source_ref"]
    if (not isinstance(source_ref, dict) or
            set(source_ref) != {"source_object_id", "source_fingerprint",
                               "locator", "range"}):
        _reading_error("graph.malformed_reading_record",
                       "source_ref must be a closed pinned source reference")
    _opaque_id(source_ref["source_object_id"], "source_ref.source_object_id")
    _fingerprint(source_ref["source_fingerprint"],
                 "source_ref.source_fingerprint")
    if not isinstance(source_ref["locator"], str):
        _reading_error("graph.malformed_reading_record",
                       "source_ref.locator must be authored text")
    if source_ref["source_object_id"] not in {
            row["source_object_id"] for row in doc.get("sources") or ()}:
        _reading_error("graph.unknown_source",
                       "the occurrence source is absent from this graph")
    for field in ("source_object_id", "source_fingerprint", "locator"):
        if source_ref[field] != binding.get(field, ""):
            _reading_error("graph.reading_binding_mismatch",
                           "source_ref.%s disagrees with the pinned binding" % field)

    reading_range = source_ref["range"]
    if (not isinstance(reading_range, dict) or
            set(reading_range) != {"span_id", "locator_id",
                                  "locator_sidecar_fingerprint"} or
            not isinstance(reading_range["span_id"], str) or
            not reading_range["span_id"]):
        _reading_error("graph.malformed_reading_record",
                       "range must be one closed nonempty span")
    locator_id = reading_range["locator_id"]
    sidecar_fp = reading_range["locator_sidecar_fingerprint"]
    if (locator_id is None) != (sidecar_fp is None):
        _reading_error("graph.malformed_reading_record",
                       "adapted range locator fields must both be present or both null")
    if locator_id is not None:
        if not isinstance(locator_id, str) or not locator_id:
            _reading_error("graph.malformed_reading_record",
                           "range.locator_id must be nonempty when present")
        _fingerprint(sidecar_fp, "range.locator_sidecar_fingerprint")

    for field in ("purpose", "preparation_mode", "path_role", "learning_phase"):
        if not isinstance(document[field], str) or not document[field].strip():
            _reading_error("graph.malformed_reading_record",
                           "%s must be nonempty authored text" % field)
    sequence = document["sequence_evidence"]
    if (not isinstance(sequence, dict) or
            set(sequence) != {"status", "citation"} or
            sequence["status"] not in READING_SEQUENCE_STATUSES or
            (sequence["citation"] is not None and
             not isinstance(sequence["citation"], str))):
        _reading_error("graph.malformed_reading_record",
                       "sequence_evidence is not a closed supported record")
    if (sequence["status"] == "Published" and
            (not sequence["citation"] or not sequence["citation"].strip())):
        _reading_error("graph.malformed_reading_record",
                       "Published sequence evidence requires a citation")
    provenance = document["assignment_provenance"]
    if (not isinstance(provenance, dict) or
            set(provenance) != {"authority", "citation"} or
            provenance["authority"] not in READING_ASSIGNMENT_AUTHORITIES or
            (provenance["citation"] is not None and
             not isinstance(provenance["citation"], str))):
        _reading_error("graph.malformed_reading_record",
                       "assignment_provenance is not a closed supported record")
    if (provenance["authority"] == "instructor" and
            (not provenance["citation"] or not provenance["citation"].strip())):
        _reading_error("graph.malformed_reading_record",
                       "instructor assignment provenance requires a citation")
    policy = document["assistance_policy"]
    if (not isinstance(policy, dict) or
            set(policy) != {"status", "citation", "instruction"} or
            policy["status"] not in READING_ASSISTANCE_STATUSES or
            any(value is not None and not isinstance(value, str)
                for value in (policy["citation"], policy["instruction"]))):
        _reading_error("graph.malformed_reading_record",
                       "assistance_policy is not a closed supported record")
    if (policy["status"] == "specified" and
            (not policy["citation"] or not policy["citation"].strip() or
             not policy["instruction"] or not policy["instruction"].strip())):
        _reading_error("graph.malformed_reading_record",
                       "specified assistance policy requires citation and instruction")
    return copy.deepcopy(document)


def _reading_documents(doc):
    documents = []
    for row in doc.get("reading_occurrences") or ():
        try:
            document = json.loads(row.get("document", ""))
        except (TypeError, ValueError):
            _reading_error("graph.malformed_reading_record",
                           "a reading occurrence document is not JSON")
        if row.get("document") != _canonical_json(document):
            _reading_error("graph.noncanonical_reading_document",
                           "a reading occurrence document is not canonical JSON")
        validate_reading_occurrence(document, doc)
        if (row.get("occurrence_id") != document["occurrence_id"] or
                row.get("revision_id") != document["revision_id"]):
            _reading_error("graph.reading_projection_mismatch",
                           "reading occurrence projections disagree with the document")
        documents.append(document)
    return documents


def validate_reading_placement(record):
    """Return authored placement plus its supported scheduling interpretation."""
    occurrence_id = record.get("occurrence_id", "")
    _opaque_id(occurrence_id, "reading placement occurrence_id")
    title = record.get("title", "")
    activation = record.get("activation", "")
    if (not _safe_table_cell(title) or not title.strip() or title != title.strip() or
            not _safe_table_cell(activation) or not activation.strip() or
            activation != activation.strip()):
        _reading_error("graph.malformed_reading_placement",
                       "reading title and activation must be nonempty table text")
    return {"occurrence_id": occurrence_id, "title": title,
            "activation": activation,
            "effective_activation": (activation if activation in
                                     READING_ACTIVATIONS else "unsupported")}


def validate_reading_graph(doc):
    """Validate versioned bindings, occurrence chains, and placement joins."""
    _validate_binding_revisions(doc)
    documents = _reading_documents(doc)
    by_pair = {}
    by_occurrence = {}
    for document in documents:
        pair = (document["occurrence_id"], document["revision_id"])
        if pair in by_pair:
            code = ("graph.duplicate_reading_revision" if
                    by_pair[pair] == document else
                    "graph.divergent_reading_revision")
            _reading_error(code, "reading revision %s/%s occurs more than once"
                           % pair)
        by_pair[pair] = document
        by_occurrence.setdefault(document["occurrence_id"], []).append(document)
    for occurrence_id, rows in by_occurrence.items():
        revisions = {row["revision_id"]: row for row in rows}
        roots = [row for row in rows if row["supersedes_revision_id"] is None]
        children = {}
        for row in rows:
            parent = row["supersedes_revision_id"]
            if parent is None:
                continue
            if parent not in revisions:
                _reading_error("graph.missing_reading_revision",
                               "occurrence %s names missing revision %s"
                               % (occurrence_id, parent))
            children.setdefault(parent, []).append(row)
        if not roots and rows:
            _reading_error("graph.cyclic_reading_revisions",
                           "occurrence %s contains a revision cycle"
                           % occurrence_id)
        if len(roots) != 1:
            _reading_error("graph.reading_revision_chain",
                           "occurrence %s must have exactly one root"
                           % occurrence_id)
        if any(len(group) > 1 for group in children.values()):
            _reading_error("graph.branching_reading_revisions",
                           "occurrence %s has competing successor revisions"
                           % occurrence_id)
        seen = set()
        current = roots[0]
        while current:
            revision_id = current["revision_id"]
            if revision_id in seen:
                _reading_error("graph.cyclic_reading_revisions",
                               "occurrence %s contains a revision cycle"
                               % occurrence_id)
            seen.add(revision_id)
            successors = children.get(revision_id, ())
            current = successors[0] if successors else None
        if len(seen) != len(rows):
            _reading_error("graph.cyclic_reading_revisions",
                           "occurrence %s contains a disconnected revision cycle"
                           % occurrence_id)

    placements = {}
    for row in doc.get("reading_placement") or ():
        placement = validate_reading_placement(row)
        occurrence_id = placement["occurrence_id"]
        if occurrence_id in placements:
            _reading_error("graph.duplicate_reading_placement",
                           "occurrence %s has more than one placement"
                           % occurrence_id)
        if occurrence_id not in by_occurrence:
            _reading_error("graph.missing_reading_occurrence",
                           "placement %s has no reading occurrence"
                           % occurrence_id)
        placements[occurrence_id] = placement
    missing = set(by_occurrence) - set(placements)
    if missing:
        _reading_error("graph.missing_reading_placement",
                       "occurrence %s has no placement" % sorted(missing)[0])
    return {"occurrences": copy.deepcopy(documents),
            "placements": copy.deepcopy(placements)}


def enroll_binding(doc, binding_index, source_fingerprint):
    """Assign permanent identity to one exactly selected legacy binding row."""
    if (not isinstance(binding_index, int) or isinstance(binding_index, bool) or
            binding_index < 0):
        _reading_error("graph.unknown_binding_row",
                       "the selected binding row index must be a nonnegative integer")
    candidate = copy.deepcopy(doc)
    try:
        row = candidate["bindings"][binding_index]
    except (KeyError, IndexError, TypeError):
        _reading_error("graph.unknown_binding_row",
                       "the selected binding row does not exist")
    if any(row.get(field, "") for field in
           ("binding_id", "binding_revision_id",
            "supersedes_binding_revision_id", "source_fingerprint")):
        _reading_error("graph.binding_already_versioned",
                       "the selected binding row already carries identity")
    _fingerprint(source_fingerprint, "source_fingerprint")
    row["binding_id"] = identity.new_object_id()
    row["binding_revision_id"] = identity.new_object_id()
    row["supersedes_binding_revision_id"] = ""
    row["source_fingerprint"] = source_fingerprint
    for binding in candidate["bindings"]:
        for field in SECTION_COLUMNS["Bindings"]:
            if field not in binding["columns"]:
                binding["columns"].append(field)
    candidate.setdefault("section_columns", {})["Bindings"] = \
        list(candidate["bindings"][0]["columns"])
    validate_reading_graph(candidate)
    doc.clear()
    doc.update(candidate)
    return doc["bindings"][binding_index]


def append_binding_revision(doc, binding_id, changes):
    """Append one immutable successor to the unique head of a binding chain."""
    candidate = copy.deepcopy(doc)
    rows = [row for row in candidate.get("bindings") or ()
            if row.get("binding_id") == binding_id]
    if not rows:
        _reading_error("graph.unknown_binding_revision",
                       "the binding identity is absent from this graph")
    parent_ids = {row.get("supersedes_binding_revision_id") for row in rows
                  if row.get("supersedes_binding_revision_id")}
    heads = [row for row in rows
             if row.get("binding_revision_id") not in parent_ids]
    if len(heads) != 1:
        _reading_error("graph.binding_revision_chain",
                       "the binding has no unique head")
    forbidden = {"binding_id", "binding_revision_id",
                 "supersedes_binding_revision_id"}
    if (not isinstance(changes, dict) or forbidden.intersection(changes) or
            any(key not in SECTION_COLUMNS["Bindings"] for key in changes)):
        _reading_error("graph.invalid_binding_revision_change",
                       "binding revision changes may alter only binding content")
    if (not changes or any(not _safe_table_cell(value)
                           for value in changes.values())):
        _reading_error("graph.invalid_binding_revision_change",
                       "binding revision changes must be safe Markdown table strings")
    values = {field: heads[0].get(field, "")
              for field in SECTION_COLUMNS["Bindings"]}
    values.update(changes)
    if all(values[field] == heads[0].get(field, "") for field in changes):
        _reading_error("graph.invalid_binding_revision_change",
                       "a binding revision must change binding content")
    values["binding_id"] = binding_id
    values["binding_revision_id"] = identity.new_object_id()
    values["supersedes_binding_revision_id"] = heads[0]["binding_revision_id"]
    record = copy.deepcopy(heads[0])
    for field, value in values.items():
        record[field] = value
        if field not in record["columns"]:
            record["columns"].append(field)
    candidate["bindings"].append(record)
    validate_reading_graph(candidate)
    doc.clear()
    doc.update(candidate)
    return doc["bindings"][-1]


def add_reading_occurrence(doc, values, title, activation):
    """Mint and append one occurrence root and its placement atomically."""
    if (not isinstance(values, dict) or
            any(key in values for key in ("occurrence_id", "revision_id",
                                          "supersedes_revision_id", "course_id"))):
        _reading_error("graph.malformed_reading_record",
                       "new occurrence values must omit graph-owned identity fields")
    candidate = copy.deepcopy(doc)
    document = dict(values)
    document.update({"occurrence_id": identity.new_object_id(),
                     "revision_id": identity.new_object_id(),
                     "supersedes_revision_id": None,
                     "course_id": candidate["header"]["course_object_id"]})
    validate_reading_occurrence(document, candidate)
    candidate["reading_occurrences"].append(
        new_record("Reading occurrences", {
            "occurrence_id": document["occurrence_id"],
            "revision_id": document["revision_id"],
            "document": _canonical_json(document)}))
    candidate["reading_placement"].append(new_record("Reading placement", {
        "occurrence_id": document["occurrence_id"], "title": title,
        "activation": activation}))
    validate_reading_graph(candidate)
    doc.clear()
    doc.update(candidate)
    return copy.deepcopy(document)


def append_reading_revision(doc, occurrence_id, changes):
    """Append one immutable material revision while retaining all ancestors."""
    candidate = copy.deepcopy(doc)
    documents = [item for item in _reading_documents(candidate)
                 if item["occurrence_id"] == occurrence_id]
    if not documents:
        _reading_error("graph.unknown_reading_occurrence",
                       "the reading occurrence is absent from this graph")
    parent_ids = {item["supersedes_revision_id"] for item in documents
                  if item["supersedes_revision_id"] is not None}
    heads = [item for item in documents
             if item["revision_id"] not in parent_ids]
    forbidden = {"occurrence_id", "revision_id", "supersedes_revision_id",
                 "course_id"}
    if (len(heads) != 1 or not isinstance(changes, dict) or
            forbidden.intersection(changes) or
            any(key not in READING_OCCURRENCE_FIELDS for key in changes)):
        _reading_error("graph.invalid_reading_revision",
                       "the occurrence needs one head and material field changes only")
    if not changes or all(heads[0][key] == value for key, value in changes.items()):
        _reading_error("graph.invalid_reading_revision",
                       "a reading revision must change the reading task")
    document = copy.deepcopy(heads[0])
    document.update(changes)
    document["revision_id"] = identity.new_object_id()
    document["supersedes_revision_id"] = heads[0]["revision_id"]
    validate_reading_occurrence(document, candidate)
    candidate["reading_occurrences"].append(
        new_record("Reading occurrences", {
            "occurrence_id": occurrence_id,
            "revision_id": document["revision_id"],
            "document": _canonical_json(document)}))
    validate_reading_graph(candidate)
    doc.clear()
    doc.update(candidate)
    return copy.deepcopy(document)


def update_reading_placement(doc, occurrence_id, title, activation):
    """Change display and placement without minting an occurrence revision."""
    candidate = copy.deepcopy(doc)
    rows = [row for row in candidate.get("reading_placement") or ()
            if row.get("occurrence_id") == occurrence_id]
    if len(rows) != 1:
        _reading_error("graph.missing_reading_placement",
                       "the occurrence must have exactly one placement to update")
    rows[0]["title"] = title
    rows[0]["activation"] = activation
    validate_reading_graph(candidate)
    doc.clear()
    doc.update(candidate)
    return validate_reading_placement(
        [row for row in doc["reading_placement"]
         if row["occurrence_id"] == occurrence_id][0])


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


def _migration_row(doc, migration_id):
    for record in doc.get("migrations") or ():
        if record.get("migration_id") == migration_id:
            return record
    raise GraphError(
        "graph.migration_unknown",
        "%s is not a recorded migration proposal in this course graph"
        % migration_id)


def _settle_migration(doc, migration_id, state, reviewer, rationale):
    """The one transition both acceptance paths go through.

    Every refusal fires BEFORE any field is written, so a refused settlement
    leaves the row byte-identical. That ordering is the whole reason this is
    one function rather than two: two copies of five checks is two chances to
    get the order wrong in one of them.
    """
    row = _migration_row(doc, migration_id)

    if row.get("state") != "proposed":
        raise GraphError(
            "graph.migration_already_settled",
            "migration %s is already %s; a settled proposal is settled in "
            "either direction and is not settled again"
            % (migration_id, row.get("state")))

    # Exact ASCII, no case folding. An actor that could grant its own proposal
    # by changing one letter's case would not be a check.
    if reviewer == row.get("actor"):
        raise GraphError(
            "graph.migration_self_accept",
            "%s proposed this migration, so it may not settle it; the actor "
            "that proposed a revision is never the actor that grants it, and "
            "no autonomy setting makes it so" % reviewer)

    if not str(rationale or "").strip():
        raise GraphError(
            "graph.empty_rationale",
            "a migration proposal needs a rationale a reviewer can evaluate; "
            "an empty one records a decision nobody can review")

    row["state"] = state
    row["reviewer"] = reviewer
    row["rationale_review"] = rationale
    return doc


def accept_migration(doc, migration_id, reviewer, rationale):
    """Move one recorded proposal from proposed to accepted.

    One of exactly two paths permitted to settle a migration; the 14B
    `set_migration_state` refusal stays in place and still refuses, so the
    number of ways to settle a proposal went from zero to two rather than
    becoming unbounded.

    Not idempotent, deliberately. Accepting an already-accepted proposal
    raises, because an acceptance is an EVENT and not a desired state: a second
    accept means two reviewers each believe they granted it, and quietly
    succeeding would hide that.

    Mutates and returns the doc, the convention `add_binding` and
    `add_migration` already use in this module.
    """
    return _settle_migration(doc, migration_id, "accepted", reviewer,
                             rationale)


def reject_migration(doc, migration_id, reviewer, rationale):
    """Move one recorded proposal from proposed to rejected.

    The row is recorded as rejected rather than removed, so a later reader can
    see that a revision was proposed and declined instead of finding no record
    at all. A deleted proposal and a proposal that was never made look the
    same, and they are not the same.

    The self-accept refusal fires here too, so an agent cannot quietly withdraw
    its own proposal through the reviewer path either.
    """
    return _settle_migration(doc, migration_id, "rejected", reviewer,
                             rationale)


def set_migration_state(doc, migration_id, state):
    """Refuse, by name, every attempt to settle a proposal in this phase.

    This function exists so the refusal has somewhere to live: a caller
    reaching for a way to accept a proposal finds a named refusal that says
    where acceptance actually belongs, rather than an absent function it
    might be tempted to add.
    """
    raise GraphError(
        "graph.migration_state_not_settable",
        "a migration state is set by a reviewer at acceptance time, through "
        "graph.accept_migration or graph.reject_migration and through no "
        "other path; this function refuses so a caller reaching for a way to "
        "settle a proposal finds the two that exist rather than adding a third")


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
