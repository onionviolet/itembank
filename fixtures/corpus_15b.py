#!/usr/bin/env python3
"""The Phase 15B corpus: one cited blueprint, drafted question sets, and the
golden sidecar that proves the format change was additive.

Every string is fictional and fixed. No real course, book, learner, exam, or
bank content of any kind appears here, and nothing is a paraphrase of any. The
"Beacon" exam is invented; its only relationship to any real standardized exam
is its shape.

Fixed seed throughout: no randomness and no clock read, so a rebuild is
byte-identical and two runs of a gate over one fixture produce the same
findings in the same order.
"""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The golden sidecar captured BEFORE Phase 15B added the Blueprint section.
# Non-negotiable 4 requires the additive claim be proven by a byte-identical
# fixture rather than promised, and a fixture generated after the change could
# not prove anything: it would carry whatever the new code produces.
GOLDEN_SIDECAR = os.path.join(ROOT, "fixtures", "golden_sidecar_pre_15b.md")

BLUEPRINT_CONSTRUCT = ("Readiness to apply the Beacon field response protocol "
                       "under time pressure.")
BLUEPRINT_FEEDBACK = {"disclosure": "end-of-form",
                      "retry": "not-permitted"}


def build_blueprint(item_count=3, count_tolerance=0, share_tolerance=5,
                    tolerance_seconds=60):
    """One cited, versioned blueprint matching the conforming draft set.

    Every share and tolerance is an integer percentage point, and every time is
    an integer of seconds, because the blueprint schema admits no float.

    The declared shares are the conforming set's ACTUAL shares, computed the
    same way the gate computes them: two of three items in Scene assessment is
    67 points, one of three in Handoff reporting is 33. A fixture whose
    declared shares did not match its own conforming draft would make the
    conforming case fail and would prove the gate works by accident.
    """
    return {
        "schema_version": 1,
        "blueprint_id": "beacon-field-response-v1",
        "version": 1,
        "construct": {"statement": BLUEPRINT_CONSTRUCT,
                      "citation": "Beacon blueprint, section 1"},
        "domain_weight": {
            "shares": [{"domain": "Scene assessment",
                        "objective_prefix": "Scene assessment", "share": 67},
                       {"domain": "Handoff reporting",
                        "objective_prefix": "Handoff reporting",
                        "share": 33}],
            "tolerance": share_tolerance},
        "demand": {
            "permitted": ["recall", "application"],
            "shares": [{"level": "recall", "share": 33},
                       {"level": "application", "share": 67}],
            "tolerance": share_tolerance,
            "citation": "Beacon blueprint, section 2"},
        "format": {"permitted_types": ["mc", "multi"],
                   "item_count": item_count,
                   "count_tolerance": count_tolerance},
        "difficulty": {
            "permitted_bands": ["recall", "application"],
            "shares": [{"band": "recall", "share": 33},
                       {"band": "application", "share": 67}],
            "tolerance": share_tolerance},
        "timing": {"total_seconds": 360, "per_item_seconds": 180,
                   "tolerance_seconds": tolerance_seconds,
                   "citation": "Beacon blueprint, section 3"},
        "tools": {"permitted": ["none"],
                  "citation": "Beacon blueprint, section 4"},
        "feedback_conditions": {"disclosure": "end-of-form",
                                "retry": "not-permitted",
                                "citation": "Beacon blueprint, section 5"},
        "citations": [{"source": "Beacon standards blueprint",
                       "locator": "published weights, 2026 form"}],
    }


DRAFT_HEADER = (
    "# Beacon drafted practice (synthetic)\n"
    "\n"
    "Fully invented content for a fictional field response protocol. It\n"
    "exists to exercise the Phase 15B blueprint gate. It is not derived from\n"
    "any real course, exam, or textbook.\n"
    "\n")

# The shipped bank format, written out rather than paraphrased: a numbered
# stem line carrying its difficulty, an ID and a HASH, an OBJECTIVE, lettered
# options, a CORRECT letter, and the rationale blocks lint expects.
DRAFT_ITEM = """Q%(n)d. %(stem)s   (difficulty: %(difficulty)s)
[ID: %(item_id)s]
[HASH: sha256:%(hash)s]
[OBJECTIVE: %(objective)s]

A) %(a)s
B) %(b)s
C) %(c)s
D) %(d)s

CORRECT: %(correct)s

WHY BEST: %(why)s

KEY DISCRIMINATOR: %(disc)s

SECOND-BEST: %(second)s

DISTRACTOR ANALYSIS:
- A) %(na)s
- B) %(nb)s
- C) %(nc)s
- D) %(nd)s

TRAP: %(trap)s

CONFIDENCE: high

"""

_DRAFTS = (
    {"objective": "Scene assessment", "difficulty": "recall",
     "item_id": "15b0000000000001", "hash": "15b0000000000001",
     "stem": "Which action is recorded first on arrival at a Beacon scene?",
     "a": "Count the patients present",
     "b": "Confirm the scene is safe to enter",
     "c": "Request a second responder",
     "d": "Begin the handoff report",
     "correct": "B",
     "why": "The Beacon protocol records scene safety before any other step, "
            "because every later step is taken inside the scene.",
     "disc": "The word first. Every option is a real Beacon step; only one "
             "opens the sequence.",
     "second": "A. Counting patients is the next recorded step, and it would "
               "be right if the question asked what follows the safety call.",
     "na": "Counting patients follows the safety confirmation; this would be correct if the question asked what is recorded second.",
     "nb": "Correct: this is the recorded first action.",
     "nc": "A second responder is requested after the count; this would be correct if the scene had already been declared safe.",
     "nd": "The handoff report closes the encounter; this would be correct if the question asked what is recorded last.",
     "trap": "Reading the most urgent-sounding action as the first recorded "
             "one."},
    {"objective": "Scene assessment", "difficulty": "application",
     "item_id": "15b0000000000002", "hash": "15b0000000000002",
     "stem": "A responder arrives to find a downed line, a fuel spill, and a "
             "single casualty. What does the Beacon log record?",
     "a": "One hazard and one patient",
     "b": "Two hazards and one patient",
     "c": "Two hazards only",
     "d": "One patient only",
     "correct": "B",
     "why": "Every observed hazard and every patient is logged individually, "
            "because the log is a record of observations and not a summary.",
     "disc": "Whether the log summarizes or enumerates. It enumerates.",
     "second": "C. Recording both hazards is half right, and it would be "
               "correct if the scene had no patient.",
     "na": "Logging one hazard discards an observed hazard; this would be correct if only one hazard had been observed.",
     "nb": "Correct: this records everything observed.",
     "nc": "Omitting the patient loses the reason for the response; this would be correct if the scene held no patient.",
     "nd": "Omitting the hazards loses the safety record; this would be correct if the scene held no hazards.",
     "trap": "Treating the log as a summary of the scene rather than a list "
             "of observations."},
    {"objective": "Handoff reporting", "difficulty": "application",
     "item_id": "15b0000000000003", "hash": "15b0000000000003",
     "stem": "In a Beacon handoff, which field is stated before the findings?",
     "a": "The receiving responder's name",
     "b": "The transport priority",
     "c": "The opening field of the fixed report order",
     "d": "The time of arrival",
     "correct": "C",
     "why": "The Beacon handoff uses a fixed order and opens with its first "
            "field, so the receiver always hears the same thing first.",
     "disc": "The handoff order is fixed, so the answer is positional rather "
             "than a judgement about importance.",
     "second": "B. Transport priority is stated early, and it would be "
               "correct if the order were arranged by urgency.",
     "na": "The receiving name is recorded on the sheet, not stated first; this would be correct if the handoff opened with an address.",
     "nb": "Transport priority follows the findings; this would be correct if the order were arranged by urgency.",
     "nc": "Correct: this is the opening field of the fixed order.",
     "nd": "Arrival time is recorded rather than spoken first; this would be correct if the report opened with a timestamp.",
     "trap": "Choosing the most urgent field instead of the first field."},
)

_EXTRA_DRAFT = {
    "objective": "Handoff reporting", "difficulty": "recall",
    "item_id": "15b0000000000004", "hash": "15b0000000000004",
    "stem": "Which record closes a Beacon encounter?",
    "a": "The scene safety call",
    "b": "The patient count",
    "c": "The hazard log",
    "d": "The completed handoff report",
    "correct": "D",
    "why": "The completed handoff report is the last record written, because "
           "it is what transfers responsibility to the receiver.",
    "disc": "Which record ends the encounter rather than which begins it.",
    "second": "C. The hazard log is written late, and it would be correct if "
              "the question asked what closes the scene assessment.",
    "na": "The safety call opens the encounter; this would be correct if the question asked what is recorded first.",
    "nb": "The patient count is taken early; this would be correct if the question asked what follows the safety call.",
    "nc": "The hazard log is written during the encounter; this would be correct if the question asked what closes the scene assessment.",
    "nd": "Correct: the handoff report closes it.",
    "trap": "Reading closes as most important rather than as last.",
}


def build_draft_set(variant="conforming"):
    """The drafted bank text, in the shipped bank format.

    `variant` selects a deliberate defect, so every gate outcome is reachable
    from data rather than by editing a dict in a test:

    - `conforming`: three items, both permitted types, shares on target.
    - `wrong_type`: the third item retyped `short`, which the blueprint does
      not permit.
    - `too_many`: four items against an item_count of three at zero tolerance.
    """
    drafts = list(_DRAFTS)
    if variant == "too_many":
        drafts = drafts + [_EXTRA_DRAFT]
    text = DRAFT_HEADER
    for n, draft in enumerate(drafts, 1):
        values = dict(draft)
        values["n"] = n
        text += DRAFT_ITEM % values
    if variant == "wrong_type":
        text = text.replace("[OBJECTIVE: Handoff reporting]",
                            "[TYPE: short]\n[OBJECTIVE: Handoff reporting]", 1)
    return text


def build_item_facts(questions, variant="conforming"):
    """The five facts the bank format does not carry.

    `variant` selects a deliberate defect in the SUPPLIED facts rather than in
    the draft, which is the other half of the gate's surface: three of the
    eight fields can only ever be wrong in what the operator supplied.

    - `conforming`: every fact supplied and matching.
    - `none`: nothing supplied, which is how the unverifiable path is
      exercised by data rather than by deleting a key in a test.
    - `partial`: set facts supplied, item facts not, so a run can carry some
      checked fields and some unverifiable ones at once.
    - `demand_skew`, `timing_over`, `tool_forbidden`, `construct_mismatch`,
      `feedback_mismatch`: one field wrong, the rest conforming.
    """
    if variant == "none":
        return {}

    set_facts = {"construct": BLUEPRINT_CONSTRUCT,
                 "feedback_conditions": dict(BLUEPRINT_FEEDBACK)}
    if variant == "construct_mismatch":
        set_facts["construct"] = ("Readiness to recite the Beacon field "
                                  "response protocol from memory.")
    if variant == "feedback_mismatch":
        set_facts["feedback_conditions"] = {"disclosure": "per-item",
                                            "retry": "not-permitted"}

    facts = {"SET": set_facts}
    if variant == "partial":
        return facts

    for n, q in enumerate(questions):
        demand = q.get("difficulty") or "recall"
        seconds = 120
        tools = ["none"]
        if variant == "demand_skew":
            demand = "recall"
        if variant == "timing_over" and n == 0:
            seconds = 600
        if variant == "tool_forbidden" and n == 0:
            tools = ["calculator"]
        facts[q["item_id"]] = {"demand": demand, "timing_seconds": seconds,
                               "tools": tools}
    return facts


def build_blueprint_fixture(dest):
    """One course root with a bound blueprint, one drafted bank, and its
    facts, in one call."""
    import course
    import model

    os.makedirs(dest, exist_ok=True)
    import corpus_14b
    built = corpus_14b.build_three_domains(os.path.join(dest, "corpus"))
    course_root = built["domains"][0]["root"]

    bank_path = os.path.join(dest, "beacon_draft.md")
    bank_text = build_draft_set("conforming")
    with open(bank_path, "w", encoding="utf-8") as fh:
        fh.write(bank_text)

    state_dir = os.path.join(dest, "_state")
    os.makedirs(state_dir, exist_ok=True)

    bp = build_blueprint()
    course.bind_blueprint(course_root, bp, "human", "weibao")

    questions = model.parse_bank(bank_text)
    return {"dest": dest, "course_root": course_root, "blueprint": bp,
            "bank_path": bank_path, "bank_text": bank_text,
            "state_dir": state_dir, "questions": questions,
            "item_facts": build_item_facts(questions)}


def build_golden_sidecar():
    """The stored pre-15B sidecar text, read from disk rather than generated.

    Generated bytes would prove nothing: they would carry whatever the current
    code emits. These bytes were captured before the Blueprint section existed.
    """
    with open(GOLDEN_SIDECAR, encoding="utf-8") as fh:
        return fh.read()


def teardown(dest):
    shutil.rmtree(dest, ignore_errors=True)


STALENESS_SOURCE = (
    "# Beacon field response, working notes (%s)\n\n"
    "A synthetic passage for the Phase 15B staleness fixture. It names no real\n"
    "course, book, or learner, and its content is fixed so a rebuild is\n"
    "byte-identical.\n")


def build_staleness_fixture(dest):
    """One source object with three dependents recording its fingerprint.

    Three dependents rather than one, because `acceptance_block` reports every
    blocked dependent at once and a one-dependent fixture could not tell that
    from reporting only the first.
    """
    import identity
    import journal

    os.makedirs(dest, exist_ok=True)
    import corpus_14b
    built = corpus_14b.build_three_domains(os.path.join(dest, "corpus"))
    course_root = built["domains"][0]["root"]

    rel = "sources/staleness-fixture.md"
    os.makedirs(os.path.join(course_root, "sources"), exist_ok=True)
    source_path = os.path.join(course_root, rel)
    with open(source_path, "w", encoding="utf-8") as fh:
        fh.write(STALENESS_SOURCE % "original")
    rights = identity.rights_default()
    rights.update({"read": "granted", "transform": "granted"})
    entry = journal.op_link(course_root, "source", rel, "agent", "corpus-15b",
                            rights=rights)
    source_object_id = entry["object_id"]

    with open(source_path, "rb") as fh:
        base_fingerprint = identity.object_fingerprint(fh.read(), "source")

    dependents = [
        {"object_id": "dependent-%d" % n, "object_kind": "bank",
         "dependency_object_id": source_object_id,
         "dependency_kind": "source",
         "base_fingerprint": base_fingerprint,
         "current_fingerprint": base_fingerprint}
        for n in (1, 2, 3)]

    return {"dest": dest, "course_root": course_root,
            "source_path": source_path, "source_object_id": source_object_id,
            "base_fingerprint": base_fingerprint, "dependents": dependents,
            "bank_path": os.path.join(dest, "beacon_draft.md")}


def edit_source(fixture, marker):
    """Rewrite the synthetic source so its fingerprint changes, and return the
    new one.

    The edit is a real byte change to a real file, so the new fingerprint is
    computed the same way the first one was rather than fabricated. A fixture
    that simply handed back a different string would prove the comparison
    works on strings, not that it notices a source changing.
    """
    import identity

    with open(fixture["source_path"], "w", encoding="utf-8") as fh:
        fh.write(STALENESS_SOURCE % marker)
    with open(fixture["source_path"], "rb") as fh:
        return identity.object_fingerprint(fh.read(), "source")


def build_acceptance_fixture(dest):
    """One course root carrying two proposed migrations and one stale
    dependent.

    Two proposals rather than one, so settling one can be shown to leave the
    other proposed. The stale dependent exists so the acceptance path's first
    check has something real to block on.
    """
    import course
    import graph
    import identity
    import journal

    os.makedirs(dest, exist_ok=True)
    import corpus_14b
    built = corpus_14b.build_three_domains(os.path.join(dest, "corpus"))
    course_root = built["domains"][0]["root"]
    objectives = built["domains"][0]["objectives"]

    read = course.read_course(course_root)
    doc = read["doc"]
    first = graph.migration_proposal(
        "rename", [objectives[0]], [objectives[0]],
        "the published wording changed in the new edition", "agent:director")
    second = graph.migration_proposal(
        "split", [objectives[1]], [objectives[1], objectives[2]],
        "the objective covers two separable skills", "agent:director")
    graph.add_migration(doc, first)
    graph.add_migration(doc, second)
    course.write_course(course_root, doc, read["fingerprint"], "agent",
                        "corpus-15b")

    rel = "sources/acceptance-fixture.md"
    os.makedirs(os.path.join(course_root, "sources"), exist_ok=True)
    path = os.path.join(course_root, rel)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(STALENESS_SOURCE % "acceptance")
    rights = identity.rights_default()
    rights.update({"read": "granted", "transform": "granted"})
    entry = journal.op_link(course_root, "source", rel, "agent", "corpus-15b",
                            rights=rights)
    with open(path, "rb") as fh:
        base_fingerprint = identity.object_fingerprint(fh.read(), "source")

    return {"dest": dest, "course_root": course_root,
            "migration_ids": [first["migration_id"], second["migration_id"]],
            "proposer": "agent:director",
            "source_path": path,
            "source_object_id": entry["object_id"],
            "base_fingerprint": base_fingerprint,
            "dependents": [{"object_id": "dependent-1", "object_kind": "bank",
                            "dependency_object_id": entry["object_id"],
                            "dependency_kind": "source",
                            "base_fingerprint": base_fingerprint,
                            "current_fingerprint": base_fingerprint}]}


def build_audit_signals(stale=False):
    """The four signals a course audit aggregates, already computed.

    Returns them the way a caller would hand them over, plus the
    `vocabulary_members` mapping the membership check reads. The mapping is
    built by importing each vocabulary's OWNING module, so the fixture never
    holds a copy either: if `graph.BINDING_STATES` gains a member, this fixture
    follows it without an edit.
    """
    import auditor
    import graph

    treatment_rows = [
        {"objective_id": "obj-1", "treatment_kind": "guided-lesson"},
        {"objective_id": "obj-2", "treatment_kind": "direct-reading"},
        {"objective_id": "obj-3", "treatment_kind": ""},
    ]
    coverage_rows = [
        {"objective_id": "obj-1", "vocabulary": "graph.BINDING_STATES",
         "state": "covered", "source_object_id": "src-1",
         "base_fingerprint": "fp-a",
         "current_fingerprint": "fp-b" if stale else "fp-a"},
        # The same state string under a DIFFERENT vocabulary, so the report has
        # to keep two rows distinguishable by provenance alone.
        {"objective_id": "obj-1", "vocabulary": "auditor.coverage_report",
         "state": "covered", "source_object_id": "src-2",
         "base_fingerprint": "fp-c", "current_fingerprint": "fp-c"},
        {"objective_id": "obj-2", "vocabulary": "graph.BINDING_STATES",
         "state": "thin", "source_object_id": "src-1",
         "base_fingerprint": "fp-a",
         "current_fingerprint": "fp-b" if stale else "fp-a"},
        {"objective_id": "obj-3", "vocabulary": "auditor.coverage_report",
         "state": "gap", "source_object_id": "src-3",
         "base_fingerprint": "fp-d", "current_fingerprint": "fp-d"},
    ]
    quality_findings = [
        {"item": "obj-1", "code": "quality.answer_skew", "severity": "block"},
        {"item": "obj-2", "code": "quality.answer_leak", "severity": "warn"},
    ]
    blueprint_findings = [
        {"item": "obj-1", "code": "blueprint.unverifiable", "severity": "warn"},
    ]
    vocabulary_members = {
        "graph.BINDING_STATES": list(graph.BINDING_STATES),
        # auditor.py's own five-state vocabulary, read from its source rather
        # than copied, so the fixture cannot drift from the module it cites.
        "auditor.coverage_report": ["covered", "partial", "gap",
                                    "conflicting", "unknown"],
        "audit_report.coverage_row": ["covered", "partial", "gap",
                                      "conflicting", "unknown"],
    }
    return {"treatment_rows": treatment_rows, "coverage_rows": coverage_rows,
            "quality_findings": quality_findings,
            "blueprint_findings": blueprint_findings,
            "vocabulary_members": vocabulary_members}


PROPOSAL_WINDOW = {"start": "2026-08-01T00:00:00.000Z",
                   "end": "2026-08-08T00:00:00.000Z",
                   "boundary": "half-open"}

# A second window abutting the first, sharing the boundary value. The pair
# exists so a test can prove the two partition a row set exactly: no row
# counted twice and none dropped.
PROPOSAL_WINDOW_NEXT = {"start": "2026-08-08T00:00:00.000Z",
                        "end": "2026-08-15T00:00:00.000Z",
                        "boundary": "half-open"}

PROPOSAL_OBJECTIVE = "Identify scene hazards on arrival"


def build_sparse_evidence():
    """AGENT-03's own fixture case: two attempts on one objective.

    Two, deliberately. The requirement's Fixture sentence is about what a
    system does with almost no evidence, and two is almost none.
    """
    return [{"ts": "2026-08-01T00:00:00.000Z",
             "objective": PROPOSAL_OBJECTIVE, "score": True},
            {"ts": "2026-08-02T09:30:00.000Z",
             "objective": PROPOSAL_OBJECTIVE, "score": False}]


def build_dense_evidence(count=24):
    """`count` rows spread across two abutting windows, with two landing
    exactly on the shared boundary.

    The two boundary rows are the point: they are what makes the partition
    claim checkable rather than assumed.
    """
    rows = []
    for n in range(count - 2):
        day = 1 + (n % 6)
        rows.append({"ts": "2026-08-0%dT%02d:00:00.000Z" % (day, n % 24),
                     "objective": PROPOSAL_OBJECTIVE,
                     "score": (n % 3 != 0)})
    for n in range(2):
        rows.append({"ts": PROPOSAL_WINDOW["end"],
                     "objective": PROPOSAL_OBJECTIVE, "score": n == 0})
    return rows


def build_reconciliation_case(dest, marker="revised"):
    """A staleness fixture whose source has already been edited.

    Returns the fixture plus the rebuilt rows, so a caller exercising a
    disposition does not have to repeat the edit-and-rebuild dance and cannot
    get it subtly different between two cases.
    """
    import blueprint

    fixture = build_staleness_fixture(dest)
    moved = edit_source(fixture, marker)
    rows = blueprint.staleness_report(
        [dict(d, current_fingerprint=moved) for d in fixture["dependents"]])
    return {"fixture": fixture, "moved": moved, "rows": rows}


def build_all_15b(dest):
    """The whole Phase 15B freeze-gate corpus in one call.

    The tracer sets up in one statement so what it proves is the acceptance
    path, not a page of fixture wiring.
    """
    import course
    import graph
    import identity
    import journal
    import model

    os.makedirs(dest, exist_ok=True)
    import corpus_14b
    built = corpus_14b.build_three_domains(os.path.join(dest, "corpus"))
    course_root = built["domains"][0]["root"]
    objectives = built["domains"][0]["objectives"]
    source_object_id = built["domains"][0]["source_object_id"]

    # A source the drafted treatment can be bound against.
    corpus_14b.grant_right(course_root, source_object_id, "read")
    corpus_14b.grant_right(course_root, source_object_id, "transform")

    blueprint_doc = build_blueprint()
    course.bind_blueprint(course_root, blueprint_doc, "human", "weibao")

    bank_path = os.path.join(dest, "beacon_draft.md")
    bank_text = build_draft_set("conforming")
    with open(bank_path, "w", encoding="utf-8") as fh:
        fh.write(bank_text)
    state_dir = os.path.join(dest, "_state")
    os.makedirs(state_dir, exist_ok=True)

    questions = model.parse_bank(bank_text)

    # Three migration proposals: one to accept, one to reject, and one whose
    # proposer IS the reviewer so the self-accept refusal has a real subject.
    read = course.read_course(course_root)
    doc = read["doc"]
    to_accept = graph.migration_proposal(
        "rename", [objectives[0]], [objectives[0]],
        "the published wording changed in the new edition", "agent:director")
    to_reject = graph.migration_proposal(
        "split", [objectives[1]], [objectives[1], objectives[2]],
        "the objective covers two separable skills", "agent:director")
    self_proposed = graph.migration_proposal(
        "rename", [objectives[3]], [objectives[3]],
        "a proposal whose author is also the reviewer", "weibao")
    for proposal in (to_accept, to_reject, self_proposed):
        graph.add_migration(doc, proposal)
    course.write_course(course_root, doc, read["fingerprint"], "agent",
                        "corpus-15b")

    # A source whose dependents go stale mid-flow.
    rel = "sources/tracer-dependency.md"
    os.makedirs(os.path.join(course_root, "sources"), exist_ok=True)
    source_path = os.path.join(course_root, rel)
    with open(source_path, "w", encoding="utf-8") as fh:
        fh.write(STALENESS_SOURCE % "original")
    rights = identity.rights_default()
    rights.update({"read": "granted", "transform": "granted"})
    entry = journal.op_link(course_root, "source", rel, "agent", "corpus-15b",
                            rights=rights)
    with open(source_path, "rb") as fh:
        base_fingerprint = identity.object_fingerprint(fh.read(), "source")

    return {
        "dest": dest,
        "course_root": course_root,
        "objectives": objectives,
        "source_object_id": source_object_id,
        "blueprint": blueprint_doc,
        "bank_path": bank_path,
        "bank_text": bank_text,
        "state_dir": state_dir,
        "questions": questions,
        "item_facts": build_item_facts(questions, "conforming"),
        "treatment_objective": objectives[4],
        "migration_accept": to_accept["migration_id"],
        "migration_reject": to_reject["migration_id"],
        "migration_self": self_proposed["migration_id"],
        "self_proposer": "weibao",
        "dependency_path": source_path,
        "dependency_object_id": entry["object_id"],
        "dependency_base_fingerprint": base_fingerprint,
        "dependents": [{"object_id": "tracer-dependent-1",
                        "object_kind": "bank",
                        "dependency_object_id": entry["object_id"],
                        "dependency_kind": "source",
                        "base_fingerprint": base_fingerprint,
                        "current_fingerprint": base_fingerprint}],
    }


def current_fingerprint(path):
    """The live fingerprint of a file's bytes, recomputed rather than read back
    from any stored value."""
    import identity

    with open(path, "rb") as fh:
        return identity.object_fingerprint(fh.read(), "source")

