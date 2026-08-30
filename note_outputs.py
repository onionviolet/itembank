#!/usr/bin/env python3
"""The note-output trio: notebook page, Cornell notes, and concept map, as
three validated projections of one parsed content instance.

The rule this module exists to obey, quoted from `STYLE-DISCIPLINE-16A`: a
semantic style is a validator plus a projection over the one parsed content
model. Not a second parser, not a second content truth, not a per-style fork
of the same material. Three views of one thing.

So this module never opens the bank file. The caller parses once with
`model.parse_lesson` and `model.parse_terms`, hands both dicts to
`content_instance`, and every projection reads that instance. The
parse-once claim is proven in `tests/note_trio_roundtrip.py` by counting
calls through the real parsers, which is only meaningful because no
projection can reach around it to a file.

Each projection returns plain Markdown, and that text IS the contract rather
than a fallback for it. A rich rendering is 17A's, and it must carry
everything the plain form carries: the concept map's accessible form is the
textual adjacency structure, not a description of a picture. Nothing renders
that the plain form does not.

A validator failure never takes the content down with it. `render_mode`
returns the locked refusal sentence naming the failing check in the
validator's own words, and the plain projection anyway, because a derived
view must never become the only understandable copy.
"""
import os

import model
import notes


OUTPUT_MODES = ("notebook_page", "cornell_notes", "concept_map")

MODE_NAMES = {"notebook_page": "Notebook page",
              "cornell_notes": "Cornell notes",
              "concept_map": "Concept map"}

# The closed relation vocabulary. Edges come from the fixture's declared
# typed relations plus `[[term]]` refs, and from nothing else: an inline edge
# grammar would be a second parser (D-16C-7).
RELATION_TYPES = ("part_of", "causes", "contrasts_with", "requires")

# Locked copy, transcribed verbatim from the 16C-UI-SPEC Copywriting
# Contract.
VALIDATOR_FAILURE_COPY = "The {mode} view can't be built from this content: {check}. Showing plain Markdown instead."
TEXTUAL_FALLBACK_LINE = "relates to {node}: {relation}"

# The closed check catalogue, in `model.STYLE_CHECK_CATALOGUE`'s shape.
# Adding a check is a code change here. No style file, fixture, or note can
# add one, which is what keeps the set of ways a view may refuse knowable.
NOTE_OUTPUT_CHECKS = {
    "note_output.ownership_missing": "error",
    "note_output.anchor_moved": "error",
    "note_output.provenance_missing": "error",
    "note_output.cue_without_notes": "error",
    "note_output.edge_untyped": "error",
}

# The words each check speaks in. The refusal sentence interpolates one of
# these, so a refusal can never go generic.
_CHECK_WORDS = {
    "note_output.ownership_missing": "a note block has no owner",
    "note_output.anchor_moved": "an anchor points to a block that moved",
    "note_output.provenance_missing": "an anchored block has no locator",
    "note_output.cue_without_notes": "a cue has no matching notes",
    "note_output.edge_untyped": "a relation has no type",
}

# Role id to the learner-facing word, positional per notes.CAPTURE_COPY.
_ROLE_LABELS = dict(zip(notes.EPISTEMIC_ROLES,
                        notes.CAPTURE_COPY["role_choices"]))


def content_instance(lesson, terms, relations, notes_list):
    """The one seam between the parser and every projection.

    Takes what `model.parse_lesson` and `model.parse_terms` returned, the
    declared typed relations, and the learner's notes. Reads no file and
    calls no parser: the caller parses once and passes the dicts in, which
    is what makes the parse-once proof possible (D-16C-7).
    """
    return {"lesson": lesson, "terms": terms,
            "relations": list(relations), "notes": list(notes_list)}


def _heading_by_slug(instance):
    return dict((h["slug"], h)
                for h in (instance["lesson"].get("headings") or []))


def _notes_for(instance, slug):
    out = []
    for note in instance["notes"]:
        for target in note.get("targets") or []:
            if target.get("stable_id") == slug:
                out.append(note)
                break
    return out


def _role_label(note):
    return _ROLE_LABELS.get(note.get("epistemic_role", ""),
                            note.get("epistemic_role", ""))


def project_notebook_page(instance):
    """The learner's notes in document order under their anchored headings.

    Every block states three things a note is worthless without: whose it is,
    what role it plays, and where it came from. Ownership is on every block
    rather than in a document header, because a block copied out of the page
    that loses its owner is how a learner's claim becomes anonymous course
    material.

    Locators render basename-only: an absolute path in a shared page is an
    accidental disclosure of a directory tree.
    """
    headings = instance["lesson"].get("headings") or []
    lines = ["# Notebook page", ""]
    for heading in headings:
        anchored = _notes_for(instance, heading["slug"])
        if not anchored:
            continue
        lines.append("## %s" % heading["text"])
        lines.append("")
        for note in anchored:
            lines.append("**%s** (owner: %s)" % (_role_label(note),
                                                 note.get("owner") or
                                                 "unattributed"))
            lines.append("")
            lines.append(note.get("learner_wording", ""))
            lines.append("")
            for target in note.get("targets") or []:
                state = notes.resolve_anchor(target, headings)
                label = notes.ANCHOR_STATE_LABELS.get(state["state"], "")
                locator = os.path.basename(str(target.get("locator") or ""))
                lines.append("Provenance: %s (%s)" % (label, locator))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def project_cornell(instance):
    """Cues, then notes, then a summary, linear and readable top to bottom.

    The two-column page is a visual arrangement; the meaning is the pairing
    of a cue with the notes that answer it, which survives linearization
    intact. That is why the plain form is the contract: a learner reading
    this in Obsidian loses the columns and loses nothing else.
    """
    headings = instance["lesson"].get("headings") or []
    lines = ["# Cornell notes", ""]
    for heading in headings:
        anchored = _notes_for(instance, heading["slug"])
        questions = [n for n in anchored
                     if n.get("epistemic_role") == "learner_question"]
        cue = questions[0]["learner_wording"] if questions else heading["text"]
        lines.append("## Cue: %s" % cue)
        lines.append("")
        body = [n for n in anchored
                if n.get("epistemic_role") != "learner_question"]
        for note in body or questions:
            lines.append("- %s: %s" % (_role_label(note),
                                       note.get("learner_wording", "")))
        if not (body or questions):
            lines.append("- (no notes yet)")
        lines.append("")
    lines.append("## Summary")
    lines.append("")
    claims = [n for n in instance["notes"]
              if n.get("epistemic_role") == "learner_claim"]
    for note in claims:
        lines.append("- %s" % note.get("learner_wording", ""))
    if not claims:
        lines.append("- (no claims recorded yet)")
    return "\n".join(lines).rstrip() + "\n"


def _edges(instance):
    """Every edge, from the two permitted sources and no third.

    Declared typed relations, plus one `requires` edge from each heading to
    each term it references. A `[[term]]` reference IS a stated dependency;
    reading it as one avoids inventing a grammar to say the same thing
    twice.
    """
    edges = list(instance["relations"])
    headings = instance["lesson"].get("headings") or []
    for heading in headings:
        # `model._term_refs` is the one `[[term]]` reference reader and the
        # one slugifier behind it. Calling it is deliberate: a local regex
        # here would be the second grammar this module exists to avoid, and
        # a reference that resolved differently in the concept map than in
        # the glossary would be worse than an underscore.
        for ref in model._term_refs(heading.get("body", "")):
            edges.append((heading["slug"], "requires", ref["slug"]))
    return edges


def project_concept_map(instance):
    """The concept map as textual adjacency.

    This is not a description of a diagram, it is the map. A rich rendering
    may draw it later and must keep this structure as its accessible
    equivalent, because a graphic whose meaning lives only in position and
    hover is a graphic a keyboard cannot read.
    """
    edges = _edges(instance)
    nodes = []
    for source, _, target in edges:
        for node in (source, target):
            if node not in nodes:
                nodes.append(node)
    lines = ["# Concept map", ""]
    for node in nodes:
        lines.append("## %s" % node)
        lines.append("")
        for source, relation, target in edges:
            if source == node:
                lines.append(TEXTUAL_FALLBACK_LINE
                             .replace("{node}", target)
                             .replace("{relation}", relation))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


PROJECTIONS = {"notebook_page": project_notebook_page,
               "cornell_notes": project_cornell,
               "concept_map": project_concept_map}


def validate_mode(mode, instance, headings):
    """What this mode cannot honestly render, in the validator's own words.

    Returns a list of `{"code", "check"}` dicts, empty when the instance is
    sound. Each mode checks what it alone depends on: the notebook page on
    ownership and provenance, Cornell on the cue-to-notes pairing, the
    concept map on typed edges.

    The anchor check calls `notes.resolve_anchor`, never a local relocation
    rule, so a moved block means the same thing here and in the note schema.
    """
    if mode not in OUTPUT_MODES:
        raise ValueError("unknown output mode: %r" % (mode,))
    failures = []

    def add(code):
        failures.append({"code": code, "check": _CHECK_WORDS[code]})

    if mode == "notebook_page":
        for note in instance["notes"]:
            if not (note.get("owner") or "").strip():
                add("note_output.ownership_missing")
            for target in note.get("targets") or []:
                if not (target.get("locator") or "").strip():
                    add("note_output.provenance_missing")
                state = notes.resolve_anchor(target, headings)
                if state["state"] not in ("resolved", "relocated_exact"):
                    add("note_output.anchor_moved")
    elif mode == "cornell_notes":
        # The projection emits one cue per heading, so a heading nothing is
        # anchored to IS a cue with no matching notes. Checking the rendered
        # shape rather than a separate cue list keeps the validator and the
        # projection from disagreeing about what a cue is.
        for heading in headings:
            if not _notes_for(instance, heading["slug"]):
                add("note_output.cue_without_notes")
    elif mode == "concept_map":
        for edge in _edges(instance):
            if len(edge) != 3 or edge[1] not in RELATION_TYPES:
                add("note_output.edge_untyped")
    return failures


def render_mode(mode, instance, headings):
    """One mode, validated, and rendered either way.

    On failure the refusal names the mode and the failing check in the
    validator's own words, and `text` still carries the plain projection.
    The content is never lost and never blocked (D11): `--warn`, not
    `--bad`, because a named fault that needs fixing is not the same as an
    unreadable document.
    """
    failures = validate_mode(mode, instance, headings)
    text = PROJECTIONS[mode](instance)
    if not failures:
        return {"ok": True, "text": text, "failures": []}
    return {"ok": False,
            "text": text,
            "failures": failures,
            "copy": VALIDATOR_FAILURE_COPY
            .replace("{mode}", MODE_NAMES[mode])
            .replace("{check}", failures[0]["check"])}
