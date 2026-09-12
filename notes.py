#!/usr/bin/env python3
"""Learner notes: the NOTE-01 record, its closed vocabularies, its
multi-selector provenance, and its anchor resolution.

Notes are learner-owned artifacts. They are never annotations baked into an
accepted lesson, never source truth, never answer keys, never scores, and
never mastery. Nothing in this module settles anything: the runtime owns
correctness, session state, evidence, and keyed disclosure, and this module
deliberately cannot reach it. It imports `model` for pure helpers and uses
the existing journal for recoverable private document acceptance.

Placement follows the `evidence.py` rule: a runtime-tier peer at the
repository root, importable by any surface, importing no surface.

Naming, per D-16C-6 and D15: the per-action states in
`STRATEGY_ACTION_STATES` are strategy-action states, which are learner task
states (lowercase activity). The Activity view (capitalized) is the 16B IA
area for durable agent and maintenance jobs and is not this module's subject.

It imports `evidence` (plan 16C-06) to append strategy lifecycle facts
through the one evidence writer, the `surfaces/migrate.py` precedent: the
builder lives outside `evidence.py` and `evidence.append_event` stays the
only door. It still imports no `runtime` and nothing from `surfaces/`.

What this module does NOT do: no trio projection (16C-07 owns
`note_outputs.py`), no rendering, no route, and no command.
"""
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone

import evidence
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


_UNSET = object()


def _pair_fingerprint(markdown, sidecar):
    import hashlib
    return hashlib.sha256(json.dumps([markdown, sidecar], ensure_ascii=False).encode()).hexdigest()


def _valid_sidecar(sidecar, schema):
    """Validate NOTE-01 plus the existing delete_note tombstone extension."""
    import schema_validate
    base = dict(sidecar)
    tombstones = base.pop("tombstones", [])
    tombstone_schema = {"type": "array", "items": {"type": "object",
        "additionalProperties": False, "required": ["note_id", "status", "deleted_at"],
        "properties": {"note_id": {"type": "string", "minLength": 1},
                       "status": {"const": "deleted"}, "deleted_at": {"type": "string", "minLength": 1}}}}
    return not schema_validate.validate(base, schema) and not schema_validate.validate(tombstones, tombstone_schema)


def _read_pair(dir_path, course_id=None):
    import journal
    import resources
    import schema_validate
    import discovery
    md_path, side_path = _document_paths(dir_path)
    if any(not discovery.inside_any_root(path, [dir_path]) for path in (md_path, side_path)):
        raise journal.JournalError("notes.outside_root", "Restore the note pair inside its private root.")
    raw = [journal._read_optional(path) for path in (md_path, side_path)]
    report = journal.replay(dir_path)
    if any(report[key] for key in ("interrupted", "recoverable", "mixed", "conflicts")):
        raise journal.JournalError("notes.recovery_required", "Recover the private note journal before saving. Keep your draft.")
    if raw == [None, None]:
        if any(row.get("path") == "notes.md.json" and row.get("fingerprint") is not None
               for row in journal._compute_registry(dir_path).values()):
            raise journal.JournalError("notes.missing_document", "Restore the missing accepted note pair before saving.")
        return None
    if None in raw:
        raise journal.JournalError("notes.incomplete_pair", "Restore the missing note document companion. Keep your draft.")
    try:
        markdown, side_text = [value.decode("utf-8") for value in raw]
        sidecar = json.loads(side_text)
        if not isinstance(sidecar, dict):
            raise ValueError()
        schema = json.loads(resources.read_text("schemas/note.schema.json"))
        if (sidecar.get("schema_version") != NOTE_SCHEMA_VERSION or
                not _valid_sidecar(sidecar, schema) or
                (course_id and sidecar.get("course_id") != course_id)):
            raise ValueError()
    except (ValueError, UnicodeError):
        raise journal.JournalError("notes.invalid_document", "Note document is unsupported or invalid. Preserve it for recovery.") from None
    registry = journal._compute_registry(dir_path)
    row = registry.get(sidecar["note_document_id"])
    if not row and any(item.get("path") == "notes.md.json" for item in registry.values()):
        raise journal.JournalError("notes.identity_conflict", "The note document identity changed. Reconcile the private note journal.")
    if row:
        entry = next(e for e in journal.entries(dir_path) if e["entry_id"] == row["last_entry_id"])
        descriptors = {f["path"]: f for f in entry["undo"].get("files", [])}
        if any(name not in descriptors or descriptors[name]["after_digest"] != journal._raw_digest(value)
               for name, value in zip(("notes.md", "notes.md.json"), raw)):
            raise journal.JournalError("notes.conflict", "The accepted note pair changed outside its writer. Reconcile before saving.")
    return {"markdown": markdown, "sidecar": sidecar,
            "fingerprint": _pair_fingerprint(markdown, side_text)}


def write_note_document(dir_path, course_id, markdown, sidecar, expected_fingerprint=_UNSET):
    """Accept the existing NOTE-01 pair through a private journal transaction.

    The document is a journal component, with Markdown as its companion.
    Journal entries contain hashes and identity only. Private before-images
    remain beneath the note root. Readers refuse unresolved pair recovery.
    Existing Python callers capture their base here. Interactive callers must
    supply the fingerprint returned by read_note_document, or None for create.
    """
    import identity
    import journal
    import resources
    import schema_validate
    os.makedirs(dir_path, mode=0o700, exist_ok=True)
    sidecar = dict(sidecar)
    sidecar.setdefault("schema_version", NOTE_SCHEMA_VERSION)
    sidecar.setdefault("course_id", course_id)
    schema = json.loads(resources.read_text("schemas/note.schema.json"))
    if (sidecar.get("schema_version") != NOTE_SCHEMA_VERSION or
            sidecar.get("course_id") != course_id or not _valid_sidecar(sidecar, schema)):
        raise journal.JournalError("notes.invalid_document", "The note document is invalid. Keep your draft.")
    old = read_note_document(dir_path, course_id)
    current = old["fingerprint"] if old else None
    if expected_fingerprint is not _UNSET and expected_fingerprint != current:
        raise journal.JournalError("notes.stale", "Notes changed since you opened them. Keep your draft and reload.")
    if old and old["sidecar"]["note_document_id"] != sidecar["note_document_id"]:
        raise journal.JournalError("notes.identity_conflict", "Keep the existing note document identity.")
    md_path, side_path = _document_paths(dir_path)
    old_side = journal._read_optional(side_path)
    old_md = journal._read_optional(md_path)
    new_side = (json.dumps(sidecar, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    new_md = markdown.encode("utf-8")
    def validate_base():
        found = _read_pair(dir_path, course_id)
        if (found["fingerprint"] if found else None) != current:
            raise journal.JournalError("notes.stale", "Notes changed before acceptance. Keep your draft.")
    revision = journal.commit_operation(
        dir_path, sidecar["note_document_id"], "component", "notes.md.json",
        "edit_in_place" if old else "mint", new_side,
        identity.object_fingerprint(old_side, "component") if old_side is not None else None,
        "human", "local", create_if_missing=not old,
        companions=({"path": "notes.md", "expected_digest": journal._raw_digest(old_md), "new_bytes": new_md},),
        precommit=validate_base)
    return {"markdown_path": md_path, "sidecar_path": side_path,
            "fingerprint": _pair_fingerprint(markdown, new_side.decode()), "revision": revision}


def read_note_document(dir_path, course_id=None):
    """Read a coherent accepted pair, or refuse with private recovery guidance."""
    import journal
    if not os.path.isdir(dir_path):
        return None
    with journal._journal_lock(dir_path):
        return _read_pair(dir_path, course_id)


# ---------------------------------------------------------------------------
# Strategy lifecycle facts (plan 16C-06, D-16C-1)
# ---------------------------------------------------------------------------

STRATEGY_LIFECYCLE_EVENT_TYPES = ("activity_completed", "activity_skipped")

# The four registry ids, validated here as a local constant so this module
# does not import `strategies`. `strategies.STRATEGY_IDS` is the source of
# truth and plan 16C-09's tracer asserts the two tuples equal; the local copy
# exists to keep the note store free of a dependency on the strategy layer,
# not to become a second registry.
_REGISTERED_STRATEGY_IDS = ("continuous_reading", "guided_note_spine",
                            "worked_reasoning", "retrieval_first")


def strategy_lifecycle_event(log, event_type, session_id, strategy_id,
                             action_state, note_ref=""):
    """Append one strategy lifecycle fact, and nothing about its content.

    The event's key set is closed and carries no content-bearing field: no
    learner wording, no selected text, no note body, at most a note ID
    reference (D-16C-1). That is not a privacy nicety, it is the only way the
    two halves can both keep their contracts: the evidence log is append-only
    and the note store is deletable, and deletable content inside an
    append-only log is a contradiction. So the append-only half records that
    something happened, and the deletable half holds what was said.

    Written through `evidence.append_event` and never through
    `append_line_checked`, the `surfaces/migrate.py` precedent: the builder
    may live outside `evidence.py`, the writer may not be duplicated.
    Returns that function's own answer, `recorded` or `already_recorded`,
    unchanged, because those are different facts and a caller that collapses
    them loses one.
    """
    if event_type not in STRATEGY_LIFECYCLE_EVENT_TYPES:
        raise ValueError("unknown lifecycle event type: %r" % (event_type,))
    if strategy_id not in _REGISTERED_STRATEGY_IDS:
        raise ValueError("unknown strategy: %r" % (strategy_id,))
    if action_state not in STRATEGY_ACTION_STATES:
        raise ValueError("unknown strategy-action state: %r"
                         % (action_state,))
    raw = "%s|%s|%s|%s|%s" % (session_id, strategy_id, action_state,
                              note_ref or "", event_type)
    event = {
        "schema_version": evidence.EVENT_SCHEMA_VERSION,
        "event_id": evidence.new_event_id(),
        "event_type": event_type,
        "ts": evidence.utc_now(),
        "session_id": session_id,
        "strategy_id": strategy_id,
        "action_state": action_state,
        "note_ref": note_ref or "",
        "dedupe_key": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }
    return evidence.append_event(log, event)


# ---------------------------------------------------------------------------
# Promotion and review (plan 16C-06, NOTE-02)
# ---------------------------------------------------------------------------

PROMOTION_STATES = ("private", "review_requested", "accepted", "declined")

PROMOTION_COPY = {
    "private_badge": "Private note. Not part of the course.",
    "requested_badge": "Review requested. Awaiting source-backed review.",
    "request_control": "Request review for course use",
    "flow_heading": "Review for course use",
    "source_check": "Every keyed or factual claim needs an accepted source. {N} claims have no accepted source yet.",
    "conflict_stop": "A source conflict was found. Promotion is stopped until the conflict is resolved.",
    "accept_control": "Accept into course",
    "accept_confirmation": "Accept this note into the course? The original note stays yours; the course gets a cited copy with its derivation recorded.",
    "decline_control": "Decline",
    "decline_reason_label": "Reason (recorded with the decision)",
    "accepted_badge": "Accepted into the course on {date}.",
    "declined_badge": "Not accepted: {reason}. Your note is unchanged.",
}

# accept and decline map onto the journal's applied and refused (D7), so 14A
# journaling reconciles one review grammar rather than two.
PROMOTION_OUTCOMES = ("blocked", "conflict_stop", "applied", "refused")


def promotion_state(note):
    """A note's promotion state, defaulting to private.

    Absent means private. A note nobody has done anything about is not in an
    unknown state; it is in the state every note starts in and most stay in.
    """
    state = note.get("promotion_state", "private")
    return state if state in PROMOTION_STATES else "private"


def request_review(note):
    """A copy of `note` asking for source-backed review.

    Changes the promotion state and nothing else: not the wording, not the
    anchors, not the privacy scope. Asking for review is a request, not a
    transfer of ownership, and the note stays the learner's until a reviewer
    accepts a derived copy (NOTE-02, D3).
    """
    asked = dict(note)
    asked["promotion_state"] = "review_requested"
    return asked


def review_promotion(note, claims, accepted_sources, conflicts, decision,
                     reviewer, reason="", annotations=None):
    """The one path from a learner note into course use, and its two gates.

    There is no other. A note becomes course content only when a named human
    reviewer accepts it, past both gates, and acceptance produces a NEW cited
    record carrying a derivation edge back to the note's revision. The
    learner's note is never mutated by acceptance: the course gets a copy,
    the learner keeps the original, and the derivation says where it came
    from.

    Gate 1, unsupported claims. Every keyed or factual claim needs an
    accepted source. When any lacks one the outcome is `blocked` and the
    sentence states the count, because a silently disabled accept control
    tells the reviewer nothing about what to fix (UI-SPEC gate 9).

    Gate 2, source conflict. When sources disagree, promotion stops. It never
    proceeds by preferring the note, the newest source, or a model's opinion.

    `annotations` may carry labeled generated synthesis for the reviewer to
    read. There is deliberately no code path from an annotation to an
    outcome: a model may inform the human and settles nothing.
    """
    if decision not in ("accept", "decline"):
        raise ValueError("unknown review decision: %r" % (decision,))
    if not (reviewer or "").strip():
        raise ValueError("review_promotion requires a named human reviewer")

    unsupported = [c for c in claims
                   if c.get("source_id") not in accepted_sources]
    if unsupported:
        return {"outcome": "blocked",
                "note": note,
                "copy": PROMOTION_COPY["source_check"].replace(
                    "{N}", str(len(unsupported)))}
    if conflicts:
        return {"outcome": "conflict_stop",
                "note": note,
                "copy": PROMOTION_COPY["conflict_stop"]}

    if decision == "decline":
        if not (reason or "").strip():
            raise ValueError("a declined promotion requires a recorded "
                             "reason")
        return {"outcome": "refused",
                "note": note,
                "badge": PROMOTION_COPY["declined_badge"].replace(
                    "{reason}", reason)}

    derived = note_record(
        note["course_id"], note["objective_ids"], note["epistemic_role"],
        note["learner_wording"], note["targets"],
        strategy_id=note.get("strategy_id", ""),
        authorship=note.get("authorship", "learner"),
        owner=note.get("owner", "local"),
        privacy_scope=note.get("privacy_scope", "private"),
        status="learner_accepted")
    derived["derivations"] = [{"from_note_revision": note["revision_id"],
                               "from_note_id": note["note_id"],
                               "accepted_by": reviewer}]
    if annotations:
        derived["annotations"] = list(annotations)
    return {"outcome": "applied",
            "note": note,
            "derived": derived,
            "badge": PROMOTION_COPY["accepted_badge"].replace(
                "{date}", _now()[:10])}


# ---------------------------------------------------------------------------
# Learner artifacts and honest deletion (plan 16C-06, NOTE-03, D16)
# ---------------------------------------------------------------------------

ARTIFACT_KINDS = ("proof", "program", "diagram", "explanation", "project",
                  "observation")

ARTIFACT_COPY = {
    "pending_badge": "Pending review",
    "pending_explainer": "Recorded as pending by itembank. A reviewer settles this. A model never settles it.",
    "proposal_line": "A model has proposed a mark. It settles nothing until a reviewer accepts it.",
    "settled_line": "Reviewed by {reviewer} on {date}.",
}

DELETE_COPY = {
    "confirmation": "Delete this note? This removes the note and its private index. Evidence the runtime is required to keep is not affected.",
    "confirm_button": "Delete note",
}


def artifact_record(kind, course_id, objective_ids, rubric, content_path=""):
    """One learner artifact's machine descriptor.

    The artifact itself (the proof, the program, the diagram) is
    learner-owned and lives in the note root. This record describes it.

    An empty rubric is valid. An artifact submitted before anyone wrote
    criteria is a real state, and refusing to record it would lose the
    submission to protect a form.
    """
    if kind not in ARTIFACT_KINDS:
        raise ValueError("unknown artifact kind: %r" % (kind,))
    return {"artifact_id": new_note_id(),
            "kind": kind,
            "course_id": course_id,
            "objective_ids": list(objective_ids),
            "rubric": list(rubric or []),
            "content_path": content_path,
            "submitted_at": _now()}


def artifact_evidence_view(artifact, response_event_id, log):
    """How a learner artifact reads: pending until a human settles it.

    Settlement is READ from mark events through `evidence.marks_by_event`.
    This function computes no verdict, because a second thing that could
    decide whether an artifact passed would be a second settlement
    mechanism, and there is one.

    A model proposal adds a line and changes nothing: the state stays
    pending, which is the honest description of a suggestion nobody has
    accepted.

    Per-criterion states render as separate lines and are never summed into
    a number or a grade. That is GRAPH-03's no-aggregate rule applied
    locally: three passed criteria out of four is four facts, not a score.
    """
    marks = evidence.marks_by_event(log)
    mark = marks.get(response_event_id)
    proposals = [e for e in evidence.live_events(log)
                 if e.get("event_type") == "mark_proposal"
                 and e.get("response_event_id") == response_event_id]
    if mark is None:
        lines = [ARTIFACT_COPY["pending_explainer"]]
        if proposals:
            lines.append(ARTIFACT_COPY["proposal_line"])
        return {"state": "pending",
                "badge": ARTIFACT_COPY["pending_badge"],
                "lines": lines}
    lines = [ARTIFACT_COPY["settled_line"]
             .replace("{reviewer}", mark.get("marker", "human"))
             .replace("{date}", str(mark.get("ts", ""))[:10])]
    for point in mark.get("rubric") or []:
        lines.append("%s: %s" % (point.get("point", ""),
                                 "met" if point.get("pass") else "not met"))
    return {"state": "settled",
            "badge": ARTIFACT_COPY["settled_line"]
            .replace("{reviewer}", mark.get("marker", "human"))
            .replace("{date}", str(mark.get("ts", ""))[:10]),
            "lines": lines}


def delete_note(sidecar, note_id):
    """Remove one note from a document, and say honestly what that does not
    reach.

    Deletion covers the note and its private index. It does not claw back
    lifecycle facts already in the append-only evidence store, and the
    confirmation copy says so rather than implying total erasure (D16,
    report 12 section 11.2). Copy that promised total erasure would be a
    promise this architecture cannot keep, and a learner who later found the
    lifecycle facts would be right to distrust everything else it said.

    A tombstone carrying the `deleted` status is kept in place of the note,
    so a document that referenced it reads a deletion rather than a gap.
    """
    kept, tombstones = [], []
    for note in sidecar.get("notes") or []:
        if note.get("note_id") == note_id:
            tombstones.append({"note_id": note_id, "status": "deleted",
                               "deleted_at": _now()})
        else:
            kept.append(note)
    updated = dict(sidecar)
    updated["notes"] = kept
    updated["tombstones"] = list(sidecar.get("tombstones") or []) + tombstones
    return {"sidecar": updated,
            "deleted": len(tombstones),
            "copy": DELETE_COPY["confirmation"],
            "confirm_button": DELETE_COPY["confirm_button"]}
