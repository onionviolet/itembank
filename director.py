#!/usr/bin/env python3
"""The agent-client tier: recommend a treatment, and never settle one.

A peer module beside `evidence.py`, `journal.py`, and `course.py`, importable
on its own, holding no state between calls and reaching the network only
through `model_adapter.invoke`.

What this module is, stated as the boundaries it does not cross:

This module drafts and validates. It never owns accepted truth and never owns
assessment authority. A recommendation it produces is a proposal until a rights
check permits the bind and `course.py` records it, and a rationale it relays is
labeled synthesis by the contract's own `synthesis: true` constant rather than
by a convention a reader has to remember.

Every durable write reaches disk through `course.py`, which reaches
`journal.commit_operation`. This module opens no file for writing and adds no
second write path, so the compare-and-swap discipline, the before-image, and
the undo record are inherited rather than reimplemented. The one exception is
`journal.append_entry`, which is how an operation records what it did; that is
the journal's own writer, not a second one.

Every rights decision reaches `identity.rights_granted` against the live
registry at the moment of the operation. A rights value carried on a
recommendation record, or on a binding row's `rights_snapshot`, is display
context and history. It never authorizes anything. `apply_recommendation`'s
signature deliberately does not take a rights argument, so there is no
parameter a caller could pass that would substitute for the live read.

This module deliberately does not import `tier_gate`. That gate protects a
learner from over-disclosure mid-sitting, by session mode and hint tier. A
course-builder recommendation has no learner and no disclosure boundary, so
routing it through a gate that cannot mean anything for it would be worse than
not routing it: it would make the gate look like it had an opinion here.

This module deliberately does not import `evidence`, `runtime`, or `model`. A
recommendation never touches learner evidence, never reaches the one scorer,
and never parses a bank. Because those imports are absent rather than merely
unused, the rule is structural: `hasattr(director, "evidence")` is False, and a
future edit that reached for one would have to add an import a test asserts
against.
"""
import json
import os
import unicodedata

import graph
import identity
import journal
import model_adapter
import resources
import schema_validate

DIRECTOR_SCHEMA_VERSION = 1

RECOMMENDATION_OPERATION = "treatment_recommend"
RECOMMENDATION_SCHEMA_RESOURCE = "schemas/treatment_recommendation.schema.json"

# The journal record type Phase 15A adds. An agent operation is a record of
# what an agent did; it is not a file operation, which is why it is a member of
# journal.RECORD_TYPES and never of journal.OPERATION_TYPES.
AGENT_RECORD_TYPE = "agent_operation"

# The key set of the `agent` dict on a journal entry, fixed in this order.
# journal.ENTRY_KEYS owns the entry's own key order; this tuple owns the one
# nested dict's, the same way identity.REVISION_KEYS owns a revision record's.
AGENT_ENTRY_KEYS = ("operation_id", "intent", "actor_role", "autonomy",
                    "scopes", "phase", "phase_index", "checkpoint",
                    "proposal", "egress")

# Where a payload went. "local" never left the machine; "hosted" reached a
# third party; "registered-local" reached a local backend that is a separate
# process but not a separate party. The three are distinct because the
# disclosure a learner is owed differs between them.
EGRESS_DESTINATIONS = ("local", "hosted", "registered-local")

# Minimization needs a number to be checkable. A cap that drops a span names
# it in the operation's `omitted` list with the reason, so what did not go is
# disclosed just as exactly as what did; no span is ever truncated mid-text,
# because half a passage is a disclosure nobody can verify. Raising either
# number widens what leaves this machine, which makes it a decision about
# egress rather than a tuning knob.
MAX_EGRESS_SPANS = 8
MAX_EGRESS_BYTES = 16384

# Why a span did not go. Every one is a fact a reviewer can act on: a missing
# right is fixed by recording one, a cap by splitting the operation, an
# unreadable source by finding the file.
OMISSION_REASONS = ("rights-not-granted", "span-cap", "byte-cap",
                    "source-unreadable")

# What exactly left, recorded per operation (RIGHTS-02). `spans` is the exact
# list that was sent, `omitted` is what was available and deliberately not
# sent, and `evidence_included` is always False by construction: no code path
# in this module can put learner evidence in a payload, and recording the field
# anyway is what makes that claim auditable rather than merely true.
EGRESS_KEYS = ("destination", "backend_class", "profile", "spans", "omitted",
               "payload_bytes", "evidence_included")

# The three autonomy levels in ASCENDING authority order, so a comparison is
# an index comparison and the order is the vocabulary rather than a lookup
# table beside it. Mirrors settings.agent_policy.autonomy_level exactly; if the
# two ever disagree the settings schema wins, because that is where a human
# sets the value.
AUTONOMY_LEVELS = ("recommend-only", "draft-and-review",
                   "approved-bounded-write")

# What a settings document with no agent_policy block means. Both values grant
# nothing: unknown authority is restrictive for the same reason unknown rights
# are, and a fresh install that granted write authority by omission would be a
# fresh install that writes without anyone having said it could.
AGENT_POLICY_DEFAULTS = {"autonomy_level": "recommend-only",
                         "max_bindings_per_operation": 0}

RECOMMENDATION_KEYS = ("schema_version", "objective_id", "treatment_kind",
                       "rationale", "synthesis", "confidence", "coverage",
                       "alternatives", "citations")

# Why an objective came out of a recommendation pass untreated. Every reason is
# a fact about what happened, not a severity: "no-source-bound" is not a worse
# "no-recommendation", it is a different thing to fix.
UNTREATED_REASONS = ("no-recommendation", "backend-unavailable",
                     "rights-not-granted", "reviewer-rejected",
                     "no-source-bound")

# The three outcomes a pass can give one objective. There is no fourth, and an
# objective that reached none of them is a bug rather than a state.
RECOMMENDATION_OUTCOMES = ("bound", "untreated", "refused")

# How a coverage claim was matched to its source. Only the FIRST member can
# ever lead to a `covered` classification: `heading-similarity` and `none` are
# classified `unknown` by rule 2 of `classify_coverage`, before any rule that
# could reach `covered` runs. That is TREAT-02's similarity rule made
# structural rather than maintained by care, and it is why the classifier's
# rule order is fixed in its docstring.
MATCH_KINDS = ("locator", "heading-similarity", "none")

# Roughly one substantive paragraph. A resolved span shorter than this is a
# `thin` claim rather than a `covered` one: pointing at two sentences is not
# the same as pointing at a treatment of the objective. This is the single
# place the threshold is tuned, and changing it changes what the course claims
# about itself, so it changes a claim rather than a formatting detail.
THIN_SPAN_CHARS = 240

# One coverage claim's key set, in this order. `proposed_state` is what the
# provider suggested the coverage was; it is history only, and no code path
# reads it to decide anything. `state` is what `classify_coverage` computed
# from the claim's own checkable fields. Keeping both side by side is what lets
# a reviewer see when a provider overclaimed, which a single merged field
# would hide.
COVERAGE_CLAIM_KEYS = ("objective_id", "source_object_id", "locator",
                       "match_kind", "confidence", "assertion", "span_chars",
                       "proposed_state", "state")

# The keys whose values legitimately differ between two runs of the same
# operation: minted ids, wall-clock stamps, and measured durations. Plan
# 15A-06's backend-parity assertion removes exactly these before comparing two
# runs, so a parity failure means the two backends disagreed about something
# that matters rather than that time passed between them. Sorted, so the tuple
# reads as a set and a reader never wonders whether the order carries meaning.
PARITY_VOLATILE_KEYS = ("elapsed_ms", "entry_id", "interaction_id",
                        "operation_id", "provider", "timestamp")

# The typed failures this module can raise. Built from a set-then-sorted tuple
# so sortedness is structural, following ADAPTER_CODES's construction.
DIRECTOR_CODES = tuple(sorted({
    "director.already_recorded",
    "director.acceptance_blocked",
    "director.autonomy_exceeded",
    "director.backend_unavailable",
    "director.bind_cap_exceeded",
    "director.evidence_forbidden",
    "director.proposal_self_accept",
    "director.recommendation_invalid",
    "director.duplicate_coverage_claim",
    "director.duplicate_phase",
    "director.operation_unknown",
    "director.egress_unapproved",
    "director.empty_treatment_bind",
    "director.rights_not_granted",
    "director.unknown_match_kind",
    "director.unknown_phase",
    "director.unknown_treatment_kind",
}))

# Field names that would carry learner evidence into a payload. A span is a
# locator into a source; anything on this list means a caller reached for the
# learner's side of the runtime and put it in a request bound for a provider.
# Refusing by name is cheaper than auditing every call site.
EVIDENCE_FIELDS = ("score", "verdict", "attempt_number", "session_id", "mark",
                   "response", "canonical", "note")

# One token per numbered step of the one operation protocol in
# `.agents/skills/OPERATION-CONTRACT.md`. The tuple is frozen and closed, and
# comparison against it is exact ASCII: no case folding, no prefix matching, no
# separator normalization, and no synonym table. A vocabulary that accepts
# near-misses is a checklist that cannot fail, because every misspelling
# quietly becomes a pass.
#
# A fourteenth step is a change to the shared contract that Claude, Codex and
# every other client reads, not a change to this module. Adding one here
# without adding it there would make this module's checklist disagree with the
# contract it exists to check.
PROTOCOL_STEPS = ("declare-intent", "declare-authority", "inventory",
                  "plan-treatment", "checkpoint", "draft", "cite", "validate",
                  "preview", "diff", "review", "accept", "report")

# `not-applicable` counts as present, and requires a stated reason. Recording
# `recorded` for a surface that does not ship would be a false claim; recording
# `missing` would make every operation permanently incomplete for a step
# nothing can satisfy yet. A named exemption is the honest third option, and it
# is reviewable in a way that a silent pass is not.
PHASE_OUTCOMES = ("recorded", "not-applicable", "missing")

PROTOCOL_VERDICTS = ("complete", "incomplete")

PROTOCOL_REPORT_KEYS = ("operation_id", "steps", "out_of_order", "verdict",
                        "resumable", "reason")

# The step that ships no surface in this phase, and the reason it does not.
# AGENT-02 forbids an agent self-certifying accessibility, and Phase 15A ships
# no learner-facing surface at all, so `recorded` here would be a claim about
# something that does not exist.
PREVIEW_NOT_APPLICABLE = ("no learner-facing preview surface ships before 16B; "
                          "accessibility is never self-certified")


class DirectorError(Exception):
    """A typed director failure: machine-readable `code` plus `message`, the
    same two-argument shape `graph.GraphError` and `course.CourseError` use.

    Every message names the next safe action, because a refusal a caller
    cannot act on is a dead end rather than a boundary.
    """

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def _load_recommendation_schema():
    return json.loads(resources.read_text(RECOMMENDATION_SCHEMA_RESOURCE))


def new_operation_id():
    """One opaque operation id, minted the same way every other object id in
    this project is minted (D-14A-2: never derived from content)."""
    return identity.new_object_id()


def _agent_dict(operation_id, intent, actor_role, autonomy, scopes, phase,
                phase_index, checkpoint=None, proposal=None, egress=None):
    """The `agent` value, always carrying exactly AGENT_ENTRY_KEYS.

    Absent values are explicit None rather than missing keys, so
    `set(entry["agent"])` is an assertable contract and a reader never has to
    distinguish "not applicable" from "this writer forgot".
    """
    return {"operation_id": operation_id,
            "intent": intent,
            "actor_role": actor_role,
            "autonomy": autonomy,
            "scopes": list(scopes or ()),
            "phase": phase,
            "phase_index": phase_index,
            "checkpoint": checkpoint,
            "proposal": proposal,
            "egress": egress}


def _append(base, entry, lock_held=False):
    """Append one journal entry under the journal's own lock.

    `journal.append_entry` documents that the caller must already hold the
    lock. This module takes it here rather than at each call site, so no
    director path can append unlocked.

    Two deliberate reaches for underscore-prefixed names, against the
    project's no-private-functions convention, both for the same reason
    16C-07 recorded for `model._term_refs`: the alternative is a second
    implementation of something that must have exactly one. `_journal_lock` is
    the lock, and a second lock would not serialize against the first.
    `_origin` builds the origin record, and a local dict literal would be a
    second origin grammar that could drift from the one every other entry
    uses. Neither could be made public without growing `journal.py`'s
    whole-phase diff past the two lines plan 15A-01 fixes it at.
    """
    if lock_held:
        return journal.append_entry(base, entry)
    with journal._journal_lock(base):
        return journal.append_entry(base, entry)


def _origin(actor_kind, actor_name):
    """One origin record, built by the journal's own builder. See `_append`."""
    return journal._origin(actor_kind, actor_name, AGENT_RECORD_TYPE)


def begin_operation(base, course_root, intent, actor_kind, actor_name,
                    actor_role, autonomy, scopes=(), operation_id="",
                    checkpoint=None, lock_held=False):
    """Declare an operation's intent and scope before it does anything.

    The first phase of the operation protocol is a durable record that says
    what is about to be attempted, written before the attempt. An operation
    that crashes after this entry and before any other is legible as an
    operation that declared and then stopped, which is the state the protocol
    is designed to leave behind.

    Returns the operation id, which every later phase entry carries.

    Trusted domain callers may supply a checkpoint and hold the existing
    journal lock across validation and receipt creation. Neither argument
    is exposed by the begin-operation request schema.
    """
    operation_id = operation_id or new_operation_id()
    _append(base, {
        "schema_version": None, "entry_id": None, "timestamp": None,
        "operation": AGENT_RECORD_TYPE, "state": "applied",
        "resolves_entry": None, "object_id": None, "kind": None,
        "revision": None, "parent_revision": None, "path": None,
        "expected_fingerprint": None, "before_fingerprint": None,
        "after_fingerprint": None, "before_image": None, "undo": None,
        "source_object_id": None, "source_revision": None,
        "restores_revision": None,
        "origin": _origin(actor_kind, actor_name),
        "code": "", "message": intent, "rights": None,
        "agent": _agent_dict(operation_id, intent, actor_role, autonomy,
                             scopes, PROTOCOL_STEPS[0], 0,
                             _checkpoint_with_outcome(checkpoint, "recorded", "")),
    }, lock_held=lock_held)
    return operation_id


# `AGENT_ENTRY_KEYS` is frozen at ten members by plan 15A-01, and its test
# asserts the exact tuple. A step's outcome and reason therefore ride inside
# the existing `checkpoint` slot rather than as two new top-level keys: the
# checkpoint is the free-form durable state a different client resumes from,
# and "which protocol step this was, and whether it applied" is exactly that.
# Widening a frozen key set to avoid one level of nesting would be the wrong
# trade.
CHECKPOINT_OUTCOME_KEYS = ("outcome", "reason")


def _checkpoint_with_outcome(checkpoint, outcome, reason):
    """The checkpoint dict carrying this step's outcome and its reason."""
    merged = dict(checkpoint or {})
    merged["outcome"] = outcome
    merged["reason"] = reason
    return merged


def _step_outcome(entry):
    """One entry's recorded outcome and reason, defaulting to `recorded`.

    An entry written before this plan carried no outcome, and reads as
    `recorded`, which is what it was.
    """
    checkpoint = ((entry.get("agent") or {}).get("checkpoint")) or {}
    outcome = checkpoint.get("outcome") or "recorded"
    if outcome not in PHASE_OUTCOMES:
        outcome = "recorded"
    return outcome, checkpoint.get("reason") or ""


def operation_entries(base, operation_id):
    """Every journal entry belonging to one operation, in append order.

    Never sorted. Append order is the operation's real history, and sorting by
    timestamp would hide the out-of-order case the replay report exists to
    name, as well as merging two phases written inside one clock tick.
    """
    found = []
    for entry in journal.entries(base):
        agent = entry.get("agent") or {}
        if agent.get("operation_id") == operation_id:
            found.append(entry)
    return found


def record_phase(base, operation_id, phase, phase_index, state,
                 actor_kind="agent", actor_name="", intent="", actor_role="",
                 autonomy="", scopes=(), checkpoint=None, proposal=None,
                 egress=None, code="", message="", outcome="recorded",
                 reason=""):
    """Append one further entry for an operation already begun.

    Every phase of an operation is its own append. A phase is never recorded by
    editing the entry that declared the intent, because the journal is
    append-only and an operation's history is the sequence, not a mutable row.

    Three outcomes for a repeated call, and the difference between them
    matters. The same phase at the same index is an idempotent replay: it
    returns `already_recorded` and appends nothing, the discipline
    `evidence.py` already applies to a replayed response. The same phase at a
    DIFFERENT index is a real conflict and is refused, because it means two
    callers disagree about where in the protocol this operation is. A phase
    name outside the frozen thirteen is refused before either check.

    Each case is decided by reading `journal.entries` afresh, never a cached
    list: a cache would let a phase recorded by another process in the meantime
    go unseen, which is the one thing the duplicate check exists to catch.
    """
    if phase not in PROTOCOL_STEPS:
        raise DirectorError(
            "director.unknown_phase",
            "%s is not one of the thirteen operation protocol steps; the "
            "vocabulary is frozen and comparison is exact, with no case "
            "folding and no synonyms" % phase)
    if state not in journal.ENTRY_STATES:
        raise DirectorError(
            "director.recommendation_invalid",
            "%s is not a journal entry state; known states are: %s"
            % (state, ", ".join(journal.ENTRY_STATES)))
    if outcome not in PHASE_OUTCOMES:
        raise DirectorError(
            "director.recommendation_invalid",
            "%s is not one of the three phase outcomes: %s"
            % (outcome, ", ".join(PHASE_OUTCOMES)))
    if outcome == "not-applicable" and not reason:
        raise DirectorError(
            "director.recommendation_invalid",
            "a not-applicable phase must state why; an unexplained exemption "
            "is indistinguishable from a skipped step")

    for entry in operation_entries(base, operation_id):
        agent = entry.get("agent") or {}
        if agent.get("phase") != phase:
            continue
        if agent.get("phase_index") == phase_index:
            return "already_recorded"
        raise DirectorError(
            "director.duplicate_phase",
            "the phase %s is already recorded for operation %s at a different "
            "index; a protocol step is recorded once per operation and a "
            "second recording is refused rather than appended"
            % (phase, operation_id))

    return _append(base, {
        "schema_version": None, "entry_id": None, "timestamp": None,
        "operation": AGENT_RECORD_TYPE, "state": state,
        "resolves_entry": None, "object_id": None, "kind": None,
        "revision": None, "parent_revision": None, "path": None,
        "expected_fingerprint": None, "before_fingerprint": None,
        "after_fingerprint": None, "before_image": None, "undo": None,
        "source_object_id": None, "source_revision": None,
        "restores_revision": None,
        "origin": _origin(actor_kind, actor_name),
        "code": code, "message": message, "rights": None,
        "agent": _agent_dict(operation_id, intent, actor_role, autonomy,
                             scopes, phase, phase_index,
                             _checkpoint_with_outcome(checkpoint, outcome,
                                                      reason),
                             proposal, egress),
    })


def protocol_report(entries):
    """The thirteen-step report over one operation's entries. Pure.

    Walks `PROTOCOL_STEPS` in index order and matches by exact phase-name
    equality. It sorts nothing: a step whose recorded `phase_index` disagrees
    with its position in the contract is named in `out_of_order` rather than
    quietly moved, because sorting would hide the defect the report exists to
    find.

    `verdict` is `complete` only when no step is `missing`. An empty entry list
    yields thirteen missing steps and `incomplete`, never an empty report that
    a reader could mistake for success.
    """
    recorded = {}
    for entry in entries or ():
        agent = entry.get("agent") or {}
        phase = agent.get("phase")
        if phase in PROTOCOL_STEPS and phase not in recorded:
            recorded[phase] = entry

    steps = []
    out_of_order = []
    for index, step in enumerate(PROTOCOL_STEPS):
        entry = recorded.get(step)
        if entry is None:
            steps.append({"step": step, "index": index, "outcome": "missing",
                          "reason": "", "entry_id": ""})
            continue
        outcome, reason = _step_outcome(entry)
        steps.append({"step": step, "index": index, "outcome": outcome,
                      "reason": reason, "entry_id": entry.get("entry_id") or ""})
        if (entry.get("agent") or {}).get("phase_index") != index:
            out_of_order.append(step)

    missing = [s["step"] for s in steps if s["outcome"] == "missing"]
    operation_id = ""
    for entry in entries or ():
        operation_id = (entry.get("agent") or {}).get("operation_id") or ""
        break
    return {"operation_id": operation_id,
            "steps": steps,
            "out_of_order": out_of_order,
            "verdict": "incomplete" if missing else "complete",
            "resumable": bool(entries) and bool(missing),
            "reason": "" if not missing
                      else "%d of thirteen protocol steps are unrecorded: %s"
                           % (len(missing), ", ".join(missing))}


def replay_operation(base, operation_id):
    """One recorded operation, replayed step by step against the contract.

    This function reads the journal and nothing else. It takes a root and an
    operation id, and there is no parameter through which an in-memory
    operation object could be handed to it. That is the whole point: if it
    accepted one, a passing test would prove that a process can remember its
    own work, rather than that the journal is the durable job record, which is
    the claim RELIABILITY-02 actually makes.
    """
    entries = operation_entries(base, operation_id)
    if not entries:
        raise DirectorError(
            "director.operation_unknown",
            "no journal entry carries operation id %s; the journal is the "
            "durable job record and there is nothing to replay" % operation_id)
    return protocol_report(entries)


def resume_point(base, operation_id):
    """Where an interrupted operation stopped, and what comes next.

    Reads the journal and nothing else. An operation resumes because its
    history is on disk, not because a conversation is still open: that is the
    whole of RELIABILITY-02's claim that the journal is the durable job record
    rather than a chat transcript.
    """
    entries = operation_entries(base, operation_id)
    if not entries:
        raise DirectorError(
            "director.operation_unknown",
            "no journal entry carries operation id %s; the journal is the "
            "durable job record and there is nothing to replay" % operation_id)

    last_phase = ""
    for entry in entries:
        phase = (entry.get("agent") or {}).get("phase")
        if phase in PROTOCOL_STEPS:
            last_phase = phase

    if not last_phase:
        return {"last_phase": "", "next_phase": "", "resumable": False,
                "reason": "no-checkpoint-recorded"}
    index = PROTOCOL_STEPS.index(last_phase)
    if index == len(PROTOCOL_STEPS) - 1:
        return {"last_phase": last_phase, "next_phase": "", "resumable": False,
                "reason": "operation-complete"}
    return {"last_phase": last_phase,
            "next_phase": PROTOCOL_STEPS[index + 1],
            "resumable": True, "reason": ""}


def reverse_operation(base, operation_id, actor_kind, actor_name):
    """Undo an operation's durable writes, newest first, through journal.undo.

    Calls `journal.undo` and adds no restore path of its own. A second way to
    put bytes back would make the guarantee that any fault leaves the old or
    the new valid state depend on two implementations agreeing about what the
    old state was, and the moment they disagreed there would be no way to tell
    which one was right.

    Catches no `JournalError`. A missing before-image is a real failure and
    surfaces as one; swallowing it and reconstructing the content some other
    way is exactly the second path this function refuses to have.
    """
    entries = operation_entries(base, operation_id)
    if not entries:
        raise DirectorError(
            "director.operation_unknown",
            "no journal entry carries operation id %s; the journal is the "
            "durable job record and there is nothing to replay" % operation_id)

    reversed_entries = []
    restored_revisions = []
    complete = True
    history = list(journal.entries(base))
    resolved = {e.get("resolves_entry") for e in history
                if e.get("resolves_entry")}
    already = {e["undo"]["reverses_entry"] for e in history
               if e.get("state") == "applied" and
               (e.get("undo") or {}).get("reverses_entry")}
    checked = set()
    for entry in entries:
        if entry["entry_id"] in already and entry.get("object_id") not in checked:
            journal.undo(base, entry["entry_id"], actor_kind, actor_name)
            checked.add(entry.get("object_id"))
    for entry in reversed(entries):
        if entry.get("operation") == AGENT_RECORD_TYPE or entry.get("state") == "refused":
            continue
        if entry.get("state") == "prepared" and entry["entry_id"] in resolved:
            continue
        if entry["entry_id"] in already:
            continue
        undo_record = entry.get("undo") or {}
        if entry.get("operation") == "move" or (undo_record.get("kind") not in ("restore_before_image", "remove_created") and not (
                entry.get("operation") in ("mint", "import", "copy") and
                entry.get("before_fingerprint") is None)):
            complete = False
            continue
        result = journal.undo(base, entry["entry_id"], actor_kind, actor_name)
        reversed_entries.append(entry["entry_id"])
        restored_revisions.append((result or {}).get("revision"))

    return {"reversed_entries": reversed_entries,
            "restored_revisions": restored_revisions,
            "complete": complete}


def _objective_statement(doc, objective_id):
    """The objective's authored statement, or the empty string.

    A provider reads the goal rather than an id, and an objective whose
    statement cannot be found is still a legitimate request: the empty string
    is missing data, not an error, following the project's `""` convention.
    """
    for record in doc.get("objectives") or ():
        if record.get("id") == objective_id:
            return record.get("statement") or ""
    return ""


def _check_spans(spans):
    """Refuse any span carrying learner evidence, naming the field.

    This runs before a request is built rather than before it is sent, so a
    forbidden field cannot exist in a request object at all, not even
    transiently.
    """
    for span in spans or ():
        for field in EVIDENCE_FIELDS:
            if field in span:
                raise DirectorError(
                    "director.evidence_forbidden",
                    "a recommendation payload may not carry learner "
                    "evidence, attempts, scores, marks, or session state; "
                    "the field %s was refused" % field)


def recommendation_request(doc, objective_id, spans, profile, interaction_id,
                           attempt=1):
    """Build the bounded adapter request for one objective.

    The closed vocabularies travel with the request. Sending
    `graph.TREATMENT_KINDS` and `graph.BINDING_STATES` rather than trusting a
    provider to remember them is what makes a twelfth kind a validation failure
    at a known boundary instead of a surprise at bind time.
    """
    _check_spans(spans)
    return model_adapter.request_from_operation(
        RECOMMENDATION_OPERATION, interaction_id, profile,
        recommendation_request={
            "schema_version": DIRECTOR_SCHEMA_VERSION,
            "course_object_id": doc["header"].get("course_object_id", ""),
            "objective_id": objective_id,
            "objective_statement": _objective_statement(doc, objective_id),
            "treatment_kinds": list(graph.TREATMENT_KINDS),
            "binding_states": list(graph.BINDING_STATES),
            "source_spans": [dict(s) for s in (spans or ())],
            "attempt": attempt,
        })


def validate_recommendation(candidate):
    """A provider candidate into a normalized record, or a typed refusal.

    The schema call comes first and no field of `candidate` is read until it
    returns clean. That ordering is the whole discipline: provider output is
    untrusted input, and reading a field to decide whether to validate would
    make the read the thing the validation was supposed to protect.
    """
    errors = schema_validate.validate(candidate, _load_recommendation_schema())
    if errors:
        # A twelfth treatment kind is a schema failure like any other, because
        # the schema's own enum is closed. Plan 15A-01 asks for a distinct
        # `director.unknown_treatment_kind` for that case anyway, and it is
        # right to: "flashcards is not one of the eleven treatment kinds"
        # tells a provider author what to fix, and "enum matched none of 12"
        # does not. So the failure is classified after validation returns
        # rather than pre-empted before it runs. The ordering discipline is
        # intact: nothing is read to decide WHETHER to validate, only to
        # describe a validation that already failed.
        #
        # Only when the treatment kind is the SOLE failure. A candidate that is
        # malformed in some other way as well gets the general refusal, because
        # naming the vocabulary would describe one symptom of a broken
        # candidate as though it were the whole diagnosis, and an author would
        # fix the kind and be surprised again.
        if all(e.startswith("$.treatment_kind") for e in errors):
            _raise_for_unknown_kind(candidate)
        raise DirectorError(
            "director.recommendation_invalid",
            "the provider candidate does not validate against the "
            "recommendation contract: %s; nothing was applied" % errors[0])
    _raise_for_unknown_kind(candidate)
    return {key: candidate[key] for key in RECOMMENDATION_KEYS}


def _raise_for_unknown_kind(candidate):
    """Refuse a candidate naming a treatment kind outside the closed eleven.

    Called on both the failing and the clean path. On the clean path it is a
    belt-and-braces check that can only fire if the schema's enum and
    `graph.TREATMENT_KINDS` ever disagree, which is exactly the drift worth
    catching: two records of one closed vocabulary is the condition, not the
    fix.
    """
    if not isinstance(candidate, dict):
        return
    treatment_kind = candidate.get("treatment_kind")
    if not isinstance(treatment_kind, str) or not treatment_kind:
        return
    if treatment_kind not in graph.TREATMENT_KINDS:
        raise DirectorError(
            "director.unknown_treatment_kind",
            "%s is not one of the eleven treatment kinds in TREAT-01; the "
            "vocabulary is closed and this phase adds no twelfth"
            % treatment_kind)


def locator_key(text):
    """The one normalization a locator ever gets before it is compared.

    Unicode NFC and line endings only. No case folding, no whitespace
    collapsing, no stripping, no prefix or fuzzy matching, because every one of
    those would reopen the similarity path TREAT-02 closes: a comparison that
    treats "Section 2" as "Section 2.1", or "SECTION" as "Section", is a
    similarity match wearing the clothes of an exact one, and it would let a
    near-miss reach the `covered` branch.

    NFC and line endings are safe because neither changes which passage a
    locator names. They are the same two normalizations this project already
    applies before fingerprinting.
    """
    return unicodedata.normalize("NFC", text or "") \
        .replace("\r\n", "\n").replace("\r", "\n")


def resolve_locator(source_text, locator):
    """Whether `locator` names a real span of `source_text`, and how long.

    Pure, and the caller supplies the source text rather than a path: a
    classifier that opened files would be a classifier that could be slow, could
    fail, and could read something the operation was never scoped to.

    An empty locator never resolves. Every string contains the empty string, so
    an empty-locator claim would resolve against any source at all, and a claim
    with no locator is not a claim.
    """
    if not locator or not source_text:
        return {"resolved": False, "span_chars": 0}
    key = locator_key(locator)
    if key in locator_key(source_text):
        return {"resolved": True, "span_chars": len(key)}
    return {"resolved": False, "span_chars": 0}


def coverage_claim(claims, objective_id, source_object_id, locator,
                   match_kind, confidence, assertion, source_text,
                   proposed_state=""):
    """Append one coverage claim to `claims`, returning a NEW list.

    Never mutates its argument. A caller that held the old list keeps a stable
    value, which is what makes two classification passes comparable.

    A repeated `(objective_id, source_object_id, locator)` triple is refused
    rather than overwritten. Two claims about different passages of one source
    are two real claims and both are kept; the same claim recorded twice is a
    bug, and a bug that overwrites silently is a bug nobody finds.

    `proposed_state` is recorded and never adopted. `state` is left empty here
    and filled by `classify_coverage`, because a claim's state is a property of
    the whole group for that objective (rule 3 needs siblings) and not of the
    claim alone.
    """
    if match_kind not in MATCH_KINDS:
        raise DirectorError(
            "director.unknown_match_kind",
            "%s is not one of the three match kinds (locator, "
            "heading-similarity, none); an unrecognized match kind is refused "
            "rather than treated as a locator match" % match_kind)

    key = (objective_id, source_object_id, locator_key(locator))
    for existing in claims or ():
        if (existing.get("objective_id"), existing.get("source_object_id"),
                locator_key(existing.get("locator") or "")) == key:
            raise DirectorError(
                "director.duplicate_coverage_claim",
                "a coverage claim for objective %s against source %s at "
                "locator %s is already recorded; a repeated claim is refused "
                "rather than overwriting the first"
                % (objective_id, source_object_id, locator))

    resolved = resolve_locator(source_text, locator)
    return list(claims or ()) + [{
        "objective_id": objective_id,
        "source_object_id": source_object_id,
        "locator": locator,
        "match_kind": match_kind,
        "confidence": confidence,
        "assertion": assertion,
        "span_chars": resolved["span_chars"],
        "proposed_state": proposed_state,
        "state": "",
    }]


def coverage_claims_for(doc, source_texts):
    """Every objective's coverage claims, in authored order, each classified.

    Objectives in the document's authored order, and within one objective the
    `## Bindings` rows in the order they appear. Two passes over an unchanged
    document return equal lists, because nothing here reads a clock, a random
    source, or a registry.

    A source id absent from `source_texts` yields a claim whose `match_kind` is
    `none` and whose `span_chars` is `0`, never an exception. A source that
    cannot be read is an unknown claim: the honest state is "we could not
    check", and crashing would turn a readable gap into an unusable report.
    """
    claims = []
    for record in doc.get("objectives") or ():
        objective_id = record.get("id")
        group = []
        for row in doc.get("bindings") or ():
            if row.get("binding_kind") != "source":
                continue
            if row.get("objective") != objective_id:
                continue
            source_object_id = row.get("source_object_id") or ""
            source_text = source_texts.get(source_object_id)
            match_kind = "locator" if source_text is not None else "none"
            try:
                group = coverage_claim(
                    group, objective_id, source_object_id,
                    row.get("locator") or "", match_kind,
                    row.get("confidence") or "unknown", "",
                    source_text or "", proposed_state=row.get("state") or "")
            except DirectorError as exc:
                if exc.code != "director.duplicate_coverage_claim":
                    raise
                # A sidecar carrying the same triple twice is a document
                # defect, not a reason to refuse the whole report. The first
                # claim stands and the repeat is dropped from the report
                # rather than overwriting it.
                continue
        state = classify_coverage(group)
        claims.extend(dict(claim, state=state) for claim in group)
    return claims


def classify_coverage(claims):
    """The coverage state for ONE objective, by six ordered rules.

    First match wins, in exactly this order. The order is the contract, so it
    is written here as well as in the code: a later edit that reorders the
    branches without reordering this list makes the docstring wrong, which is
    the point.

    1. `claims` is empty, or every claim has an empty `source_object_id`:
       `missing`. Nothing is bound, so there is nothing to be covered by.
    2. No claim has `match_kind` equal to `locator`: `unknown`. This is
       TREAT-02's rule. Heading or name similarity alone can never produce
       `covered`, and it cannot here because rule 2 fires before any rule that
       could reach `covered`.
    3. Two or more locator claims carry non-empty `assertion` values that are
       not all equal: `conflicting`. The classifier compares the assertions; it
       never interprets them, and an assertion is agent-supplied and labeled
       synthesis.
    4. No locator claim has a `confidence` other than `unknown`: `unknown`. An
       unverifiable claim reads as unknown, not as covered.
    5. No locator claim has both `span_chars` at least `THIN_SPAN_CHARS` and a
       confidence of `high` or `medium`: `thin`.
    6. Otherwise: `covered`.

    `covered` is reachable only by falling through all five earlier rules,
    which is what makes every degradation path land somewhere else. There is no
    branch that reaches `covered` by default, by unrecognized value, or by
    failure.
    """
    for claim in claims or ():
        if claim.get("match_kind") not in MATCH_KINDS:
            raise DirectorError(
                "director.unknown_match_kind",
                "%s is not one of the three match kinds (locator, "
                "heading-similarity, none); an unrecognized match kind is "
                "refused rather than treated as a locator match"
                % claim.get("match_kind"))

    claims = list(claims or ())
    if not claims or not any(c.get("source_object_id") for c in claims):
        return "missing"

    located = [c for c in claims if c.get("match_kind") == "locator"]
    if not located:
        return "unknown"

    assertions = set(c.get("assertion") for c in located if c.get("assertion"))
    if len(assertions) > 1:
        return "conflicting"

    if not any(c.get("confidence") != "unknown" for c in located):
        return "unknown"

    strong = ("high", "medium")
    if not any((c.get("span_chars") or 0) >= THIN_SPAN_CHARS
               and c.get("confidence") in strong for c in located):
        return "thin"

    return "covered"


def parity_view(obj):
    """`obj` with every volatile key removed at every depth.

    Pure and recursive. Lists and scalars pass through untouched; only mapping
    keys are dropped, so a volatile value that is itself meaningful data at a
    non-key position is never lost.
    """
    if isinstance(obj, dict):
        return {key: parity_view(value) for key, value in obj.items()
                if key not in PARITY_VOLATILE_KEYS}
    if isinstance(obj, list):
        return [parity_view(value) for value in obj]
    return obj


def treatment_candidates(record):
    """Every treatment this record puts forward, chosen first.

    The record's own `treatment_kind` leads, then its alternatives. A record
    naming no treatment contributes no candidate rather than a blank one: an
    empty string is a provider declining to recommend, and ranking it against
    real candidates would let "no recommendation" win a tie.
    """
    candidates = []
    if record.get("treatment_kind"):
        candidates.append({"treatment_kind": record["treatment_kind"],
                           "confidence": record.get("confidence") or "unknown"})
    for alternative in record.get("alternatives") or ():
        candidates.append({"treatment_kind": alternative.get("treatment_kind"),
                           "confidence": alternative.get("confidence")
                           or "unknown"})
    return candidates


def _confidence_rank(confidence):
    """Where `confidence` sits in `graph.EDGE_CONFIDENCES`, high first.

    Derived from the tuple by index rather than from a literal map here, so
    there is one confidence vocabulary. An unrecognized token sorts last, which
    is the least-preferring position: an unreadable confidence must never
    promote a candidate.
    """
    try:
        return graph.EDGE_CONFIDENCES.index(confidence)
    except ValueError:
        return len(graph.EDGE_CONFIDENCES)


def rank_candidates(candidates):
    """Candidates best first, ties broken by vocabulary order.

    The tie-break reads `graph.TREATMENT_KINDS.index(kind)` rather than any
    ordering this module holds, which is what keeps one vocabulary. Two
    candidates that tie on confidence resolve by the order 14B authored, and
    the loser is kept: a reviewer needs to see what was passed over, and a
    dropped alternative is a decision made invisibly.

    Pure. Reads no file, takes no lock, and consults no registry.
    """
    seen = set()
    unique = []
    for candidate in candidates or ():
        kind = candidate.get("treatment_kind")
        if kind not in graph.TREATMENT_KINDS:
            raise DirectorError(
                "director.unknown_treatment_kind",
                "%s is not one of the eleven treatment kinds in TREAT-01; the "
                "vocabulary is closed and this phase adds no twelfth" % kind)
        key = (kind, candidate.get("confidence"))
        if key in seen:
            continue
        seen.add(key)
        unique.append({"treatment_kind": kind,
                       "confidence": candidate.get("confidence") or "unknown"})
    return sorted(unique,
                  key=lambda c: (_confidence_rank(c["confidence"]),
                                 graph.TREATMENT_KINDS.index(c["treatment_kind"])))


def untreated_objectives(doc):
    """Every objective with no treatment bound, in authored order, with why.

    Reads `doc["objectives"]`, `doc["bindings"]`, and `doc["log"]`, and
    nothing else. In particular it does not read recommendation records, and
    that is the whole point of the function rather than an implementation
    detail: a proposal is not a treatment. A gap report that counted proposals
    would go empty the moment drafting began, which is exactly the silent
    generation TREAT-01 exists to prevent. An objective is treated when a
    binding row says so, and at no earlier moment.

    Pure. Takes one argument, reads no journal, opens no file, and takes no
    lock, so it can be called from a report, a test, or a surface without any
    of them needing a course root.
    """
    treated = set()
    sourced = set()
    for row in doc.get("bindings") or ():
        objective = row.get("objective")
        if row.get("binding_kind") == "treatment":
            treated.add(objective)
        elif row.get("binding_kind") == "source":
            sourced.add(objective)

    refused_rights = set()
    for row in doc.get("log") or ():
        text = " ".join(str(v) for v in row.values() if isinstance(v, str))
        if "rights" not in text:
            continue
        for record in doc.get("objectives") or ():
            if record.get("id") and record["id"] in text:
                refused_rights.add(record["id"])

    report = []
    for record in doc.get("objectives") or ():
        objective_id = record.get("id")
        if objective_id in treated:
            continue
        # First match wins, and the order is deliberate: an objective with no
        # source behind it needs a source before it needs a recommendation, so
        # naming the missing recommendation first would send a reader to fix
        # the wrong thing.
        if objective_id not in sourced:
            reason = "no-source-bound"
        elif objective_id in refused_rights:
            reason = "rights-not-granted"
        else:
            reason = "no-recommendation"
        report.append({"objective_id": objective_id,
                       "statement": record.get("statement") or "",
                       "reason": reason})
    return report


def _autonomy_permits_write(autonomy):
    """Whether this autonomy level may write without a further review.

    Only the highest of the three levels writes. `recommend-only` proposes and
    `draft-and-review` drafts for a reviewer; neither writes a binding. This
    reads the declared level, and it is safe to do so only because
    `authorize_write` has already refused a declaration the policy does not
    grant, so by this point the declared level is at or below the configured
    one.
    """
    return autonomy == AUTONOMY_LEVELS[-1]


def recommend_treatments(base, course_root, objective_ids, settings,
                         profile_name, actor_kind, actor_name, actor_role,
                         autonomy, scopes=()):
    """One recommendation pass over many objectives, one entry each.

    Returns one entry per objective id, in the order given, each carrying one
    of the three outcomes in `RECOMMENDATION_OUTCOMES`. There is no fourth
    outcome and no objective is skipped: a pass that returned fewer entries
    than it was given objectives would be a pass whose gaps are invisible,
    which is the failure this whole surface exists to prevent.

    Never raises for a backend that did not answer. Backend loss is an
    expected state, the objective stays untreated with the reason recorded,
    and the core loop is unaffected. A candidate that arrives and fails its
    contract still raises, because that is a broken provider and not an
    absent one.
    """
    import course

    entries = []
    objective_ids = list(objective_ids or ())
    # Checked once, before the first objective, and not once per objective. An
    # over-declaring operation is refused before any binding is written rather
    # than after the first one has already landed.
    write_permitted = True
    refusal = None
    if objective_ids:
        try:
            authorize_write(settings, autonomy, len(objective_ids))
        except DirectorError as exc:
            if exc.code not in ("director.autonomy_exceeded",
                                "director.bind_cap_exceeded"):
                raise
            write_permitted = False
            refusal = exc

    for objective_id in objective_ids:
        result = recommend_once(base, course_root, objective_id, settings,
                                profile_name, actor_kind, actor_name,
                                actor_role, autonomy, scopes=scopes)
        if result["status"] != "ok":
            entries.append({"objective_id": objective_id,
                            "outcome": "untreated",
                            "reason": "backend-unavailable",
                            "treatment_kind": "",
                            "code": result["code"],
                            "record": None})
            continue

        record = result["record"]
        ranked = rank_candidates(treatment_candidates(record))
        chosen = ranked[0]["treatment_kind"] if ranked else ""
        record = dict(record, treatment_kind=chosen)

        if not write_permitted or not _autonomy_permits_write(autonomy):
            entries.append({"objective_id": objective_id,
                            "outcome": "untreated",
                            "reason": "no-recommendation" if not chosen
                            else "reviewer-rejected",
                            "treatment_kind": chosen,
                            "code": refusal.code if refusal else "",
                            "record": record})
            continue

        read = course.read_course(course_root)
        source_object_id = ""
        for row in read["doc"].get("bindings") or ():
            if row.get("binding_kind") == "source" and \
                    row.get("objective") == objective_id:
                source_object_id = row.get("source_object_id") or ""
                break
        if not source_object_id:
            entries.append({"objective_id": objective_id,
                            "outcome": "untreated",
                            "reason": "no-source-bound",
                            "treatment_kind": chosen,
                            "code": "",
                            "record": record})
            continue

        try:
            apply_recommendation(base, course_root, record, source_object_id,
                                 actor_kind, actor_name,
                                 operation_id=result.get("operation_id") or "",
                                 source_texts=source_texts_for(base,
                                                               read["doc"]))
        except DirectorError as exc:
            if exc.code == "director.rights_not_granted":
                entries.append({"objective_id": objective_id,
                                "outcome": "refused",
                                "reason": "rights-not-granted",
                                "treatment_kind": chosen,
                                "code": exc.code,
                                "record": record})
                continue
            if exc.code == "director.empty_treatment_bind":
                entries.append({"objective_id": objective_id,
                                "outcome": "untreated",
                                "reason": "no-recommendation",
                                "treatment_kind": "",
                                "code": exc.code,
                                "record": record})
                continue
            raise
        entries.append({"objective_id": objective_id, "outcome": "bound",
                        "reason": "", "treatment_kind": chosen, "code": "",
                        "record": record})
    return entries


def autonomy_level(settings):
    """The autonomy level this installation grants, from settings.

    Never from the operation. An agent that could report its own authority
    could raise it, which is the self-expansion AGENT-02 forbids by name, so
    the declared level is an input to be checked and this is the value checked
    against. A missing block or a missing key reads as `recommend-only`: the
    absence of a grant is not a grant.
    """
    block = (settings or {}).get("agent_policy") or {}
    return block.get("autonomy_level") or AGENT_POLICY_DEFAULTS["autonomy_level"]


def max_bindings_per_operation(settings):
    """How many bindings one operation may write, from settings. Zero when
    absent, so raising the level alone still writes nothing."""
    block = (settings or {}).get("agent_policy") or {}
    value = block.get("max_bindings_per_operation")
    if not isinstance(value, int):
        return AGENT_POLICY_DEFAULTS["max_bindings_per_operation"]
    return value


def authorize_write(settings, declared_level, bindings_requested=0):
    """Refuse unless the declared authority is within policy. Returns None.

    Returns None on success, deliberately and not a level. There is no value a
    caller could mistake for a granted authority, and nothing to accidentally
    pass along as though it were permission.

    An over-declaration is REFUSED, never narrowed to the permitted level.
    Narrowing would let an agent that asked for more than it may have proceed
    quietly at what it may have, and the attempt, which is the thing worth
    seeing, would never surface. An unrecognized level is refused for the same
    reason rather than treated as the lowest: an authority nobody recognizes is
    not a small authority.
    """
    granted = autonomy_level(settings)
    if declared_level not in AUTONOMY_LEVELS:
        raise DirectorError(
            "director.autonomy_exceeded",
            "%s is not one of the three autonomy levels (%s); an unrecognized "
            "authority is refused rather than treated as the lowest level"
            % (declared_level, ", ".join(AUTONOMY_LEVELS)))
    if granted not in AUTONOMY_LEVELS:
        raise DirectorError(
            "director.autonomy_exceeded",
            "the configured autonomy level %s is not one of the three levels "
            "(%s); the operation is refused rather than run at a guessed level"
            % (granted, ", ".join(AUTONOMY_LEVELS)))
    if AUTONOMY_LEVELS.index(declared_level) > AUTONOMY_LEVELS.index(granted):
        raise DirectorError(
            "director.autonomy_exceeded",
            "this operation declares the autonomy level %s but the configured "
            "policy grants %s, so it is refused rather than narrowed; next "
            "safe action: raise agent_policy.autonomy_level deliberately, or "
            "run the operation at %s"
            % (declared_level, granted, granted))
    cap = max_bindings_per_operation(settings)
    if bindings_requested > cap:
        raise DirectorError(
            "director.bind_cap_exceeded",
            "this operation requests %d bindings but the configured policy "
            "permits %d per operation, so it is refused; next safe action: "
            "raise agent_policy.max_bindings_per_operation, or split the "
            "operation" % (bindings_requested, cap))
    return None


def approved_spans(base, doc, objective_id, treatment_kind, source_texts):
    """The spans an agent may receive for this objective, and what was held
    back and why. Returns `(spans, omissions)`.

    Takes no rights parameter, deliberately, and caches no registry read. The
    current registry is read through `course.rights_for_binding` on every call
    for every source, so a right revoked a second ago takes effect now. A
    rights value observed earlier in this same process is history, and so is a
    binding row's `rights_snapshot` column: neither authorizes anything. That
    is the difference between a permission and a memory of one.

    Every excluded source is disclosed rather than silently absent. A span that
    does not go is as much a fact about the operation as a span that does, and
    a reviewer who cannot see what was held back cannot tell minimization from
    a bug.
    """
    import course

    right = graph.treatment_right(treatment_kind)
    spans = []
    omissions = []
    for row in doc.get("bindings") or ():
        if row.get("binding_kind") != "source":
            continue
        if row.get("objective") != objective_id:
            continue
        source_object_id = row.get("source_object_id") or ""
        state = course.rights_for_binding(base, source_object_id, right)
        registry = journal.read_registry(base)
        current = (registry.get(source_object_id) or {}).get("rights")
        if not identity.rights_granted(current, right):
            omissions.append({"source_object_id": source_object_id,
                              "locator": row.get("locator") or "",
                              "reason": "rights-not-granted",
                              "detail": "the %s right reads %s"
                                        % (right, state)})
            continue
        source_text = source_texts.get(source_object_id)
        if source_text is None:
            omissions.append({"source_object_id": source_object_id,
                              "locator": row.get("locator") or "",
                              "reason": "source-unreadable",
                              "detail": "no text was supplied for this source"})
            continue
        locator = row.get("locator") or ""
        spans.append({"source_object_id": source_object_id,
                      "locator": locator,
                      "text": locator,
                      "bytes": len(locator.encode("utf-8"))})

    # Dedupe on the same key the coverage classifier uses, so a span and a
    # coverage claim can never disagree about whether two locators are one.
    seen = set()
    unique = []
    for span in spans:
        key = (span["source_object_id"], locator_key(span["locator"]))
        if key in seen:
            continue
        seen.add(key)
        unique.append(span)

    sort_key = lambda s: (s["source_object_id"], locator_key(s["locator"]))
    unique.sort(key=sort_key)

    kept = []
    budget = MAX_EGRESS_BYTES
    for span in unique:
        if len(kept) >= MAX_EGRESS_SPANS:
            omissions.append({"source_object_id": span["source_object_id"],
                              "locator": span["locator"],
                              "reason": "span-cap",
                              "detail": "the operation already carries %d spans"
                                        % MAX_EGRESS_SPANS})
            continue
        if span["bytes"] > budget:
            omissions.append({"source_object_id": span["source_object_id"],
                              "locator": span["locator"],
                              "reason": "byte-cap",
                              "detail": "%d bytes would exceed the %d byte cap"
                                        % (span["bytes"], MAX_EGRESS_BYTES)})
            continue
        budget -= span["bytes"]
        kept.append(span)

    omissions.sort(key=sort_key)
    return kept, omissions


# Assembling spans for a recommendation request consumes `read`: the operation
# reads a passage in order to describe it, and reproduces nothing. This names
# the treatment kind whose right IS `read` rather than passing a bare right
# string around, so there stays one vocabulary and `graph.TREATMENT_RIGHTS`
# stays the single place a right is resolved from a treatment.
RECOMMENDATION_SPAN_TREATMENT = "direct-reading"


def source_texts_for(base, doc, right=graph.SOURCE_BINDING_RIGHT):
    """The text of every bound source whose `right` reads granted right now.

    Reads the registry live, per source, and reads a file only after that
    source's right has been checked. `approved_spans` checks the same right
    again over the result, which is deliberate: this function decides what may
    be opened, that one decides what may be sent, and a bug in either is
    caught by the other rather than by a reviewer.

    A source whose file is missing or undecodable is simply absent from the
    mapping, which `approved_spans` reports as `source-unreadable`. A course
    whose file moved is a course with a gap, not a crash.
    """
    registry = journal.read_registry(base)
    texts = {}
    for row in doc.get("bindings") or ():
        if row.get("binding_kind") != "source":
            continue
        source_object_id = row.get("source_object_id") or ""
        if not source_object_id or source_object_id in texts:
            continue
        record = registry.get(source_object_id) or {}
        if not identity.rights_granted(record.get("rights"), right):
            continue
        path = os.path.join(os.path.abspath(base), record.get("path") or "")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                texts[source_object_id] = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
    return texts


# Which destination a transport reaches. `hosted_cli` leaves for a third
# party; `openai_compatible` reaches a separate process that is still the
# learner's own machine or network. The two are disclosed differently because
# the disclosure a learner is owed differs between them. There is no fourth
# string: a transport this map does not name records `local`, which is the
# claim that nothing left.
TRANSPORT_DESTINATIONS = {"hosted_cli": "hosted",
                          "openai_compatible": "registered-local"}


def egress_record(destination, backend_class, profile_name, spans, omissions,
                  payload_bytes):
    """The exact disclosure of what left this machine, for one operation.

    Names every span and every omission individually. It does not summarize,
    round, or elide: a count, a phrase such as "the objective text", or a
    truncated list in place of the identifiers and byte counts would be a
    disclosure nobody can check, which is worse than none because it reads as
    one.

    The `text` of each span is deliberately stripped. This record says WHAT was
    sent, by source and locator and byte count; it is not a second copy of the
    content, and duplicating the passage here would put the same bytes in the
    append-only journal that the learner may later want deleted.

    `evidence_included` is `False` unconditionally, and it is recorded anyway.
    No code path in this module can reach the evidence store, because
    `director.py` does not import `evidence`. Writing the field regardless is
    what makes the claim auditable rather than merely true: a reader of the
    journal sees the assertion instead of having to know about an absent
    import.
    """
    for entry in list(spans or ()) + list(omissions or ()):
        for field in EVIDENCE_FIELDS:
            if field in entry:
                raise DirectorError(
                    "director.evidence_forbidden",
                    "a recommendation payload may not carry learner evidence, "
                    "attempts, scores, marks, or session state; the field %s "
                    "was refused" % field)

    sort_key = lambda e: (e.get("source_object_id") or "",
                          locator_key(e.get("locator") or ""))
    clean_spans = sorted(
        ({"source_object_id": s.get("source_object_id") or "",
          "locator": s.get("locator") or "",
          "bytes": s.get("bytes") or 0} for s in (spans or ())),
        key=sort_key)
    clean_omissions = sorted(
        ({"source_object_id": o.get("source_object_id") or "",
          "locator": o.get("locator") or "",
          "reason": o.get("reason") or "",
          "detail": o.get("detail") or ""} for o in (omissions or ())),
        key=sort_key)
    return {"destination": destination,
            "backend_class": backend_class,
            "profile": profile_name,
            "spans": clean_spans,
            "omitted": clean_omissions,
            "payload_bytes": payload_bytes,
            "evidence_included": False}


def recommend_once(base, course_root, objective_id, settings, profile_name,
                   actor_kind, actor_name, actor_role, autonomy,
                   interaction_id="", scopes=()):
    """One objective, one recommendation attempt, end to end.

    Returns a dict rather than raising on an unavailable backend, because
    backend loss is an expected state and not an error: the objective stays
    untreated, the core loop is unaffected, and the caller decides whether to
    retry, hand-author, or move on. A candidate that arrives and fails its
    contract does raise, because that is a broken provider rather than an
    absent one.
    """
    import course

    operation_id = begin_operation(base, course_root, "recommend a treatment",
                                   actor_kind, actor_name, actor_role,
                                   autonomy, scopes)
    read = course.read_course(course_root)
    doc = read["doc"]
    texts = source_texts_for(base, doc)
    spans, omissions = approved_spans(base, doc, objective_id,
                                      RECOMMENDATION_SPAN_TREATMENT, texts)
    request = recommendation_request(
        doc, objective_id, spans, profile_name,
        interaction_id or new_operation_id())

    # Measured on the same serialization model_adapter._invoke builds, so the
    # disclosed figure is the one that actually crossed the boundary rather
    # than an estimate of it. Computed here from the request director itself
    # built, so the two cannot disagree without the request having changed.
    request_bytes = len(json.dumps(request, ensure_ascii=False,
                                   sort_keys=True).encode("utf-8"))

    resolved, _reason = model_adapter.resolve_profile(
        settings, profile_name or None)
    transport = (resolved or {}).get("transport")
    destination = TRANSPORT_DESTINATIONS.get(transport, "local")
    if resolved is None:
        # No profile resolved, so nothing was ever sent.
        destination, request_bytes, spans = "local", 0, []

    result = model_adapter.invoke(request, settings)

    if result.get("status") != "ok":
        error = result.get("error") or {}
        # An unavailable result may or may not have reached the wire. The
        # honest disclosure for a failure that never sent anything is `local`
        # with zero bytes; for one that did, it is what was sent. The adapter
        # tells the two apart by its code: the four below fail before any byte
        # leaves the process.
        never_sent = error.get("code") in (
            "adapter.executable_missing", "adapter.profile_disabled",
            "adapter.profile_invalid", "adapter.profile_unknown",
            "adapter.transport_unknown", "adapter.request_invalid")
        record_phase(
            base, operation_id, "plan-treatment", 1, "refused",
            actor_kind=actor_kind, actor_name=actor_name,
            intent="recommend a treatment", actor_role=actor_role,
            autonomy=autonomy, scopes=scopes,
            egress=egress_record(
                "local" if never_sent else destination,
                "local" if never_sent else (transport or "local"),
                profile_name,
                [] if never_sent else spans, omissions,
                0 if never_sent else request_bytes),
            code=error.get("code") or "director.backend_unavailable",
            message=error.get("message") or "")
        return {"status": "unavailable", "code": error.get("code") or "",
                "record": None, "operation_id": operation_id}

    provider = result.get("provider") or {}
    record = validate_recommendation(result.get("candidate"))
    record_phase(
        base, operation_id, "plan-treatment", 1, "applied",
        actor_kind=actor_kind, actor_name=actor_name,
        intent="recommend a treatment", actor_role=actor_role,
        autonomy=autonomy, scopes=scopes,
        proposal={"objective_id": objective_id,
                  "treatment_kind": record["treatment_kind"]},
        egress=egress_record(destination,
                             provider.get("backend_class") or "local",
                             provider.get("profile") or profile_name,
                             spans, omissions, request_bytes),
        message="a recommendation was received and validated")

    # Protocol step 9 is preview, and this phase ships no learner-facing
    # surface to preview. Recorded as not-applicable with its reason rather
    # than left missing, because a step nothing can satisfy yet would make
    # every operation permanently incomplete, and rather than recorded,
    # because claiming a preview that does not exist would be a false claim
    # about the one step AGENT-02 forbids an agent to self-certify.
    record_phase(
        base, operation_id, "preview", PROTOCOL_STEPS.index("preview"),
        "applied", actor_kind=actor_kind, actor_name=actor_name,
        outcome="not-applicable", reason=PREVIEW_NOT_APPLICABLE,
        message="no preview surface ships in this phase")

    return {"status": "ok", "code": "", "record": record,
            "operation_id": operation_id}


def apply_recommendation(base, course_root, record, source_object_id,
                         actor_kind, actor_name, operation_id="",
                         profile_name="", backend_class="hosted",
                         source_texts=None):
    """Bind an accepted recommendation, or refuse it against the live rights.

    The coverage state written to the binding is computed by
    `classify_coverage`, never copied from the record. The provider's own
    `coverage.state` is a proposal and is kept as `proposed_state` on the
    claim; adopting it would let a model certify its own coverage, which is
    what AGENT-02 forbids and what 15A-03 decided against by name. Supplying
    `source_texts` lets the locator actually resolve; omitting them means the
    claim is unverifiable and can never reach `covered`.

    The rights read happens here and against the current registry, not against
    anything on `record`. That is why this function takes no rights argument:
    there is no parameter a caller could pass that would let a stale value
    authorize a write.

    A refusal is recorded. An operation that was refused is a fact about what
    happened, and dropping it would make the journal a log of successes.
    """
    import course

    operation_id = operation_id or new_operation_id()
    treatment_kind = record["treatment_kind"]
    if not treatment_kind:
        # Before the rights lookup, deliberately. A record naming no treatment
        # has nothing to check a right against, and asking for the right of ""
        # would raise a vocabulary error that misnames what went wrong.
        record_phase(
            base, operation_id, "review", 2, "refused",
            actor_kind=actor_kind, actor_name=actor_name,
            proposal={"objective_id": record["objective_id"],
                      "treatment_kind": ""},
            code="director.empty_treatment_bind",
            message="the recommendation names no treatment kind")
        raise DirectorError(
            "director.empty_treatment_bind",
            "the recommendation for objective %s names no treatment kind, so "
            "there is nothing to bind; the objective stays untreated with "
            "reason no-recommendation" % record["objective_id"])
    right = graph.treatment_right(treatment_kind)
    state = course.rights_for_binding(base, source_object_id, right)
    registry = journal.read_registry(base)
    current = (registry.get(source_object_id) or {}).get("rights")

    if not identity.rights_granted(current, right):
        record_phase(
            base, operation_id, "review", 2, "refused",
            actor_kind=actor_kind, actor_name=actor_name,
            proposal={"objective_id": record["objective_id"],
                      "treatment_kind": treatment_kind},
            code="director.rights_not_granted",
            message="the %s right for source %s is %s"
                    % (right, source_object_id, state))
        raise DirectorError(
            "director.rights_not_granted",
            "the %s right for source %s is %s, so this recommendation is "
            "refused; next safe action: record %s: granted on that source's "
            "rights record, or choose a treatment that does not consume that "
            "right" % (right, source_object_id, state, right))

    coverage = record.get("coverage") or {}

    # The state written to the binding is computed here, never adopted from
    # the provider. A model asserting its own coverage is the self-certification
    # AGENT-02 forbids, and 15A-03 recorded the decision in as many words: the
    # provider's `coverage.state` is a proposal, and `classify_coverage` is
    # what decides.
    #
    # Without the source text the locator cannot be resolved, so the claim is
    # unverifiable, and TREAT-02 says an unverifiable claim reads as unknown
    # rather than covered. Passing `source_texts` is what lets a caller earn a
    # stronger state; not passing it can never earn `covered`, which is the
    # conservative direction.
    text = (source_texts or {}).get(source_object_id, "")
    claim = coverage_claim(
        [], record["objective_id"], source_object_id,
        coverage.get("locator") or "", coverage.get("match_kind") or "none",
        coverage.get("confidence") or "unknown", "", text,
        proposed_state=coverage.get("state") or "")[0]
    computed_state = classify_coverage([claim])

    result = course.bind_treatment(
        base, record["objective_id"], source_object_id, treatment_kind,
        locator=coverage.get("locator") or "",
        state=computed_state,
        confidence=coverage.get("confidence") or "unknown",
        actor_kind=actor_kind, actor_name=actor_name,
        applied_agent=_agent_dict(
            operation_id, "", "", "", (), "accept", 3,
            _checkpoint_with_outcome(None, "recorded", ""),
            {"objective_id": record["objective_id"],
             "treatment_kind": treatment_kind},
            egress_record("local", "local", profile_name, [], [], 0)))
    return result


# ---------------------------------------------------------------------------
# accepted revisions (15B-04, RELIABILITY-03 and ACTIVITY-02)
# ---------------------------------------------------------------------------

ACCEPT_RECORD_TYPE = "accept_revision"


ACCEPT_DECISIONS = ("accept", "reject")


def accept_revision(base, course_root, migration_id, settings, reviewer_kind,
                    reviewer_name, rationale, staleness_rows=(),
                    dispositions=(), operation_id="", decision="accept"):
    """Accept one recorded migration proposal, or refuse and record why.

    Takes `settings` and reads the autonomy policy from them AT CALL TIME. It
    takes no autonomy argument and reads none off the proposal, which is the
    same discipline `authorize_write` was built with: a snapshot that
    authorizes is a revoked permission that stays effective forever.

    The three checks run in a fixed order, and the order carries meaning:

    1. **Staleness first.** A dependent whose dependency changed is blocked
       before the policy question is even asked, so a blocked acceptance never
       reaches the authorization step.
    2. **Authority second.** A policy-refused acceptance never reaches the
       disk.
    3. **The write last**, through `course.accept_migration` and therefore
       through `journal.commit_operation`.

    Reordering them would let an authorization failure mask a staleness failure
    or the reverse, and the journal would then record the wrong reason for the
    refusal, which is worse than recording none.

    Every outcome is journaled, refusals included. A refusal that was not
    recorded is indistinguishable from a revision nobody ever proposed.
    """
    import blueprint
    import course

    operation_id = operation_id or new_operation_id()

    def _refuse(code, message, phase="review", index=2):
        record_phase(base, operation_id, phase, index, "refused",
                     actor_kind=reviewer_kind, actor_name=reviewer_name,
                     proposal={"migration_id": migration_id},
                     code=code, message=message)

    # 1. Staleness, before anything else.
    refusals = blueprint.acceptance_block(staleness_rows, dispositions)
    if refusals:
        message = "; ".join(r["message"] for r in refusals)
        _refuse("director.acceptance_blocked", message)
        raise DirectorError(
            "director.acceptance_blocked",
            "this acceptance is blocked by %d stale dependency check(s): %s; "
            "next safe action: record a rebind, migrate, supersede, or retain "
            "review for each, then accept again"
            % (len(refusals), message))

    # 2. Authority, read live.
    #
    # The DECLARED level is the write level, not whatever the policy happens
    # to grant. Passing `autonomy_level(settings)` here would compare the
    # policy against itself and could never refuse, which is a check that
    # looks like a check and is not one. An acceptance writes, so it declares
    # the level a write needs and the policy either grants it or does not.
    try:
        authorize_write(settings, AUTONOMY_LEVELS[-1], 1)
    except DirectorError as exc:
        _refuse(exc.code, exc.message)
        raise

    if decision not in ACCEPT_DECISIONS:
        raise DirectorError(
            "director.acceptance_blocked",
            "%s is not one of the two settlement decisions (%s)"
            % (decision, ", ".join(ACCEPT_DECISIONS)))

    # 3. The write, through the one path. Both decisions are settlements and
    # both are journaled: a rejection is a recorded reviewer decision, not an
    # absence of one.
    settle = (course.accept_migration if decision == "accept"
              else course.reject_migration)
    try:
        result = settle(course_root, migration_id, reviewer_kind,
                        reviewer_name, rationale)
    except Exception as exc:
        _refuse(getattr(exc, "code", "director.acceptance_blocked"),
                getattr(exc, "message", str(exc)))
        raise

    record_phase(base, operation_id, "accept", 3, "applied",
                 actor_kind=reviewer_kind, actor_name=reviewer_name,
                 proposal={"migration_id": migration_id,
                           "decision": decision},
                 message="the migration proposal was %sed" % decision)
    return result
