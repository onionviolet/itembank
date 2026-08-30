#!/usr/bin/env python3
"""Learner notes: the NOTE-01 record, its closed vocabularies, its
multi-selector provenance, and its anchor resolution.

Notes are learner-owned artifacts. They are never annotations baked into an
accepted lesson, never source truth, never answer keys, never scores, and
never mastery. Nothing in this module settles anything: the runtime owns
correctness, session state, evidence, and keyed disclosure, and this module
deliberately cannot reach it. It imports `model` for two pure helpers and
nothing else from the project.

Placement follows the `evidence.py` rule: a runtime-tier peer at the
repository root, importable by any surface, importing no surface.

Naming, per D-16C-6 and D15: the per-action states in
`STRATEGY_ACTION_STATES` are strategy-action states, which are learner task
states (lowercase activity). The Activity view (capitalized) is the 16B IA
area for durable agent and maintenance jobs and is not this module's subject.

What this module does NOT do, by plan: no promotion, review, or deletion
(16C-06 owns NOTE-02 and NOTE-03), no evidence event of any kind, no trio
projection (16C-07), no rendering, route, or command.
"""
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone

import model


NOTE_SCHEMA_VERSION = 1

# The default note root, a sibling of the private bank in the same way
# `evidence.EVIDENCE_DIRNAME` is (D-16C-2). Root governance itself belongs to
# the 16B settings surface; this is a documented path constant, not an
# enforcement point.
NOTES_DIRNAME = "_notes"

# The closed vocabularies, transcribed from 16C-DECISIONS.md D-16C-8. Sorted
# by meaning rather than alphabetically, because each is a documented order a
# surface renders in. Adding a member is an additive registration; renaming
# one after notes exist is a migrate operation, never an edit.
EPISTEMIC_ROLES = ("quote", "learner_claim", "learner_question",
                   "learner_example", "calculation", "diagram",
                   "accepted_reference_link")
STRATEGY_ACTION_STATES = ("not_started", "draft", "completed",
                          "skipped_optional", "equivalent_completed",
                          "needs_review")
RELOCATION_STATES = ("resolved", "relocated_exact", "relocated_probable",
                     "orphaned")
NOTE_STATUS = ("draft", "learner_accepted", "disputed", "superseded",
               "deleted")
TARGET_KINDS = ("source", "lesson_step", "media", "item_public", "concept")
AUTHORSHIP_TYPES = ("learner", "authored")

# Copy, transcribed verbatim from 16C-UI-SPEC.md's Copywriting Contract. No
# executor may substitute wording here; a change is a UI-SPEC change.
ANCHOR_STATE_LABELS = {
    "resolved": "Anchored",
    "relocated_exact": "Anchor moved with the lesson",
    "relocated_probable": "Anchor probably moved: review needed",
    "orphaned": "Anchor lost. Still linked to {objective name}.",
}

# D6: a probable relocation is offered to the learner with both ways out. It
# is never applied for them.
PROBABLE_CONTROLS = ("Confirm new location", "Keep unanchored")

CAPTURE_COPY = {
    "affordance": "Add a note",
    "anchor_prompt": "What is this note about?",
    "anchor_choices": ("This selection", "This block", "This whole section",
                       "This objective (no anchor)"),
    "keyboard_picker": "Use arrow keys to choose a block, then Enter to select. Shift plus arrows extends the selection.",
    "role_prompt": "This note is:",
    # The seven role_choices map positionally to EPISTEMIC_ROLES: index i of
    # this tuple is the learner-facing word for EPISTEMIC_ROLES[i]. Storage
    # keeps the vocabulary member; only the UI shows the phrase (D4).
    "role_choices": ("A quotation", "My claim", "My question", "My example",
                     "A calculation", "A diagram",
                     "A link to an accepted reference"),
    "privacy_line": "Private to you. Nothing is shared unless you request review.",
    "save": "Save to my notes",
    "submit": "Submit activity",
    "submit_clarifier": "Submitting shares this response with the course. Your saved notes stay private.",
    "saved_status": "Saved to your notes.",
    "draft_restored": "Your draft note was restored.",
    "empty_state": "No notes yet for this course. Add one from any lesson in Learn.",
}


def _now():
    """One ISO-8601 UTC timestamp shape for every record this module writes,
    matching the `Z`-suffixed form the evidence log already uses."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (
        now.microsecond // 1000)


def hash_quoted_context(text):
    """The one quoted-context identity helper, shared by this module, the
    fixture generator, and the trio.

    Two implementations of "is this the same quoted text" disagree the first
    time one of them collapses whitespace and the other does not, and every
    relocation fixture built on the disagreeing pair is vacuous. So there is
    one, and it routes through `model.collapse`, the same normalization the
    canonical response uses.

    This is change detection, never security (ID-02). The truncation to
    sixteen hex characters is deliberate and the prefix says which algorithm
    produced it, so a later widening is a readable migration rather than a
    guess.
    """
    digest = hashlib.sha256(model.collapse(text).encode("utf-8")).hexdigest()
    return "sha256:" + digest[:16]


def new_note_id():
    """A note, document, or revision id, in `model.new_item_id`'s shape."""
    return uuid.uuid4().hex[:16]


def target_record(target_kind, stable_id, content_fingerprint, locator,
                  quoted_context_hash):
    """One anchor target: what a note points at, and what it looked like.

    Carries exactly five keys and no sixth. In particular it records NOTHING
    about which capture path produced it: D13 ships three equivalent capture
    paths (pointer selection, keyboard block-and-range picker, structured
    block-choice list) and they must produce identical records, or the
    interaction path leaks into the note's provenance and a keyboard user's
    notes become distinguishable from a mouse user's.

    `stable_id` is scheme-agnostic on purpose. Today it is a heading slug from
    `model.lesson_slug` (D-16C-7); the D-14A-2 component-ID upgrade replaces
    the values without touching this record, and no 16C code parses meaning
    out of it.
    """
    if target_kind not in TARGET_KINDS:
        raise ValueError("unknown target kind: %r" % (target_kind,))
    return {"target_kind": target_kind,
            "stable_id": stable_id,
            "content_fingerprint": content_fingerprint,
            "locator": locator,
            "quoted_context_hash": quoted_context_hash}


def note_record(course_id, objective_ids, epistemic_role, learner_wording,
                targets, strategy_id="", authorship="learner", owner="local",
                privacy_scope="private", status="draft"):
    """One NOTE-01 note record.

    Every closed vocabulary is validated here rather than at write time,
    because a record that never existed is easier to reason about than one
    that exists and is quietly invalid. An unknown member raises and names
    itself.

    `objective_ids` is the relation NOTE-01's degraded contract leans on: when
    an anchor breaks, the note stays attached to its objective and the broken
    selector is flagged. Nothing in this module removes an objective id.
    """
    if epistemic_role not in EPISTEMIC_ROLES:
        raise ValueError("unknown epistemic role: %r" % (epistemic_role,))
    if authorship not in AUTHORSHIP_TYPES:
        raise ValueError("unknown authorship type: %r" % (authorship,))
    if status not in NOTE_STATUS:
        raise ValueError("unknown note status: %r" % (status,))
    stamp = _now()
    return {"note_id": new_note_id(),
            "note_document_id": new_note_id(),
            "revision_id": new_note_id(),
            "owner": owner,
            "privacy_scope": privacy_scope,
            "course_id": course_id,
            "objective_ids": list(objective_ids),
            "strategy_id": strategy_id,
            "epistemic_role": epistemic_role,
            "learner_wording": learner_wording,
            "targets": list(targets),
            "derivations": [],
            "status": status,
            "authorship": authorship,
            "created_at": stamp,
            "updated_at": stamp}


def resolve_anchor(target, headings):
    """Where `target` points after the lesson changed, as one of the four
    closed relocation states plus its candidate slugs.

    `headings` is `model.parse_lesson(path)["headings"]`.

    This function reads and returns. It mutates nothing, writes nothing, and
    re-anchors nothing, because D6 and Do-Not-Re-Open row 5 both say a
    probable relocation needs review and is never auto-applied. Only
    `relocated_exact` may be re-anchored by a caller, and even that is the
    caller's decision made through the atomic writer, not this function's.

    The order of the branches is the contract:

    - slug matches AND content hash matches: `resolved`, nothing moved.
    - exactly one heading's content hash matches: `relocated_exact`. The text
      is where it went; the heading was renamed or reordered.
    - the slug matches but the content changed, or two or more headings carry
      the same content: `relocated_probable`, with the slug match first in
      the candidate list because it is the strongest single hint.
    - nothing matches: `orphaned`, with no candidates. The note keeps its
      objective ids either way; that is NOTE-01's degraded contract and it is
      the caller's record, not this return value.
    """
    wanted = target.get("quoted_context_hash", "")
    slug = target.get("stable_id", "")
    by_slug = None
    hash_matches = []
    for heading in headings:
        body_hash = hash_quoted_context(heading.get("body", ""))
        if heading.get("slug") == slug:
            by_slug = (heading, body_hash)
        if wanted and body_hash == wanted:
            hash_matches.append(heading.get("slug"))
    if by_slug is not None and by_slug[1] == wanted and wanted:
        return {"state": "resolved", "candidates": [slug]}
    if len(hash_matches) == 1:
        return {"state": "relocated_exact", "candidates": list(hash_matches)}
    if by_slug is not None or len(hash_matches) > 1:
        candidates = []
        if by_slug is not None:
            candidates.append(slug)
        candidates += [s for s in hash_matches if s != slug]
        return {"state": "relocated_probable", "candidates": candidates}
    return {"state": "orphaned", "candidates": []}


def authored_prehighlight(region_label, target):
    """An authored emphasis region: orientation, and nothing else.

    Clause C107 and D14: authored pre-highlighting is sparse orientation with
    one concise screen-reader label per emphasized region. It produces zero
    evidence events and zero note ownership, and it is never visually
    confusable with a learner highlight. The empty `owner` is the structural
    half of that promise; this module gives the returned record no path into
    a note document's learner notes at all, which is the other half.
    """
    return {"authorship": "authored",
            "owner": "",
            "region_label": region_label,
            "target": target}


def _document_paths(dir_path):
    return (os.path.join(dir_path, "notes.md"),
            os.path.join(dir_path, "notes.md.json"))


def write_note_document(dir_path, course_id, markdown, sidecar):
    """Write the note document pair with the compare-and-swap discipline.

    The Markdown is the human and export truth for wording; the JSON sidecar
    is the machine truth for anchors, fingerprints, and states (D-16C-2).
    Both are written to `<path>.tmp` and then `os.replace`d, the
    `runtime.write_session` shape, so any fault leaves the old or the new
    valid state and never a half-written one.

    The sidecar is written FIRST and the Markdown second. The order matters
    on a fault: a reader that finds a new sidecar and an old Markdown sees
    machine state describing text it can still read, whereas the reverse
    would show wording no anchor record accounts for.
    """
    os.makedirs(dir_path, exist_ok=True)
    md_path, side_path = _document_paths(dir_path)
    sidecar = dict(sidecar)
    sidecar.setdefault("schema_version", NOTE_SCHEMA_VERSION)
    sidecar.setdefault("course_id", course_id)
    tmp = side_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(sidecar, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, side_path)
    tmp = md_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(markdown)
    os.replace(tmp, md_path)
    return {"markdown_path": md_path, "sidecar_path": side_path}


def read_note_document(dir_path, course_id=None):
    """The one reader. Returns `{"markdown", "sidecar"}` or None when absent.

    A leftover `.tmp` beside a valid pair is ignored rather than repaired or
    reported, so an interrupted write leaves the last accepted state readable
    with no recovery step. `course_id` is accepted for symmetry with the
    writer and is not used to locate the file: one document per course
    directory (D-16C-2), so the directory already says which course this is.
    """
    md_path, side_path = _document_paths(dir_path)
    if not (os.path.exists(md_path) and os.path.exists(side_path)):
        return None
    try:
        with open(side_path, encoding="utf-8") as fh:
            sidecar = json.load(fh)
        with open(md_path, encoding="utf-8") as fh:
            markdown = fh.read()
    except (OSError, ValueError):
        return None
    return {"markdown": markdown, "sidecar": sidecar}
