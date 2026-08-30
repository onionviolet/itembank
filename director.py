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

# What exactly left, recorded per operation (RIGHTS-02). `spans` is the exact
# list that was sent, `omitted` is what was available and deliberately not
# sent, and `evidence_included` is always False by construction: no code path
# in this module can put learner evidence in a payload, and recording the field
# anyway is what makes that claim auditable rather than merely true.
EGRESS_KEYS = ("destination", "backend_class", "profile", "spans", "omitted",
               "payload_bytes", "evidence_included")

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
    "director.backend_unavailable",
    "director.evidence_forbidden",
    "director.recommendation_invalid",
    "director.duplicate_coverage_claim",
    "director.empty_treatment_bind",
    "director.rights_not_granted",
    "director.unknown_match_kind",
    "director.unknown_treatment_kind",
}))

# Field names that would carry learner evidence into a payload. A span is a
# locator into a source; anything on this list means a caller reached for the
# learner's side of the runtime and put it in a request bound for a provider.
# Refusing by name is cheaper than auditing every call site.
EVIDENCE_FIELDS = ("score", "verdict", "attempt_number", "session_id", "mark",
                   "response", "canonical", "note")

# The operation phases, in order. `phase_index` is the position, so a reader
# of the journal can tell how far an interrupted operation got without knowing
# the vocabulary.
OPERATION_PHASES = ("declare-intent", "plan-treatment", "review", "accept")


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


def _append(base, entry):
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
    with journal._journal_lock(base):
        return journal.append_entry(base, entry)


def _origin(actor_kind, actor_name):
    """One origin record, built by the journal's own builder. See `_append`."""
    return journal._origin(actor_kind, actor_name, AGENT_RECORD_TYPE)


def begin_operation(base, course_root, intent, actor_kind, actor_name,
                    actor_role, autonomy, scopes=()):
    """Declare an operation's intent and scope before it does anything.

    The first phase of the operation protocol is a durable record that says
    what is about to be attempted, written before the attempt. An operation
    that crashes after this entry and before any other is legible as an
    operation that declared and then stopped, which is the state the protocol
    is designed to leave behind.

    Returns the operation id, which every later phase entry carries.
    """
    operation_id = new_operation_id()
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
                             scopes, "declare-intent", 0),
    })
    return operation_id


def record_phase(base, operation_id, phase, phase_index, state,
                 actor_kind="agent", actor_name="", intent="", actor_role="",
                 autonomy="", scopes=(), checkpoint=None, proposal=None,
                 egress=None, code="", message=""):
    """Append one further entry for an operation already begun.

    Every phase of an operation is its own append. A phase is never recorded by
    editing the entry that declared the intent, because the journal is
    append-only and an operation's history is the sequence, not a mutable row.
    """
    if state not in journal.ENTRY_STATES:
        raise DirectorError(
            "director.recommendation_invalid",
            "%s is not a journal entry state; known states are: %s"
            % (state, ", ".join(journal.ENTRY_STATES)))
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
                             scopes, phase, phase_index, checkpoint, proposal,
                             egress),
    })


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

    A placeholder, deliberately narrow: only the one literal level permits a
    write, so the default for every other value is to propose and stop. Plan
    15A-04 replaces this with the settings-side autonomy policy and its
    over-declaration refusal; until then, a level this function does not
    recognize is a level that may not write.
    """
    return autonomy == "approved-bounded-write"


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
    for objective_id in objective_ids or ():
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

        if not _autonomy_permits_write(autonomy):
            entries.append({"objective_id": objective_id,
                            "outcome": "untreated",
                            "reason": "no-recommendation" if not chosen
                            else "reviewer-rejected",
                            "treatment_kind": chosen,
                            "code": "",
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
                                 operation_id=result.get("operation_id") or "")
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


def _spans_for_objective(doc, objective_id):
    """The approved source spans for one objective, from its existing source
    bindings.

    An objective with no source bindings yields an empty list, and that is a
    legitimate request: a provider asked about an objective with nothing behind
    it should answer `missing` coverage, which is more useful than a refusal.
    """
    spans = []
    for row in doc.get("bindings") or ():
        if row.get("binding_kind") != "source":
            continue
        if row.get("objective") != objective_id:
            continue
        spans.append({"source_object_id": row.get("source_object_id") or "",
                      "locator": row.get("locator") or ""})
    return spans


def _egress_record(request, profile_name, backend_class, spans, omitted=()):
    """What exactly left this machine, for one operation.

    `payload_bytes` is measured on the same serialization the transport sends,
    so the figure is the real one rather than an estimate of it.
    """
    return {
        "destination": "hosted" if backend_class == "hosted" else "local",
        "backend_class": backend_class,
        "profile": profile_name,
        "spans": [dict(s) for s in (spans or ())],
        "omitted": list(omitted or ()),
        "payload_bytes": len(json.dumps(request, ensure_ascii=False,
                                        sort_keys=True).encode("utf-8")),
        "evidence_included": False,
    }


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
    spans = _spans_for_objective(doc, objective_id)
    request = recommendation_request(
        doc, objective_id, spans, profile_name,
        interaction_id or new_operation_id())
    result = model_adapter.invoke(request, settings)

    if result.get("status") != "ok":
        error = result.get("error") or {}
        record_phase(
            base, operation_id, "plan-treatment", 1, "refused",
            actor_kind=actor_kind, actor_name=actor_name,
            intent="recommend a treatment", actor_role=actor_role,
            autonomy=autonomy, scopes=scopes,
            code=error.get("code") or "director.backend_unavailable",
            message=error.get("message") or "")
        return {"status": "unavailable", "code": error.get("code") or "",
                "record": None}

    provider = result.get("provider") or {}
    record = validate_recommendation(result.get("candidate"))
    record_phase(
        base, operation_id, "plan-treatment", 1, "applied",
        actor_kind=actor_kind, actor_name=actor_name,
        intent="recommend a treatment", actor_role=actor_role,
        autonomy=autonomy, scopes=scopes,
        proposal={"objective_id": objective_id,
                  "treatment_kind": record["treatment_kind"]},
        egress=_egress_record(request, provider.get("profile") or profile_name,
                              provider.get("backend_class") or "local", spans),
        message="a recommendation was received and validated")
    return {"status": "ok", "code": "", "record": record,
            "operation_id": operation_id}


def apply_recommendation(base, course_root, record, source_object_id,
                         actor_kind, actor_name, operation_id="",
                         profile_name="", backend_class="hosted"):
    """Bind an accepted recommendation, or refuse it against the live rights.

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
    result = course.bind_treatment(
        base, record["objective_id"], source_object_id, treatment_kind,
        locator=coverage.get("locator") or "",
        state=coverage.get("state") or "unknown",
        confidence=coverage.get("confidence") or "unknown",
        actor_kind=actor_kind, actor_name=actor_name)
    record_phase(
        base, operation_id, "accept", 3, "applied",
        actor_kind=actor_kind, actor_name=actor_name,
        proposal={"objective_id": record["objective_id"],
                  "treatment_kind": treatment_kind},
        egress=_egress_record({}, profile_name, backend_class,
                              record.get("citations") or ()),
        message="the recommendation was bound")
    return result
