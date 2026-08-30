#!/usr/bin/env python3
"""The learning-strategy registry (STRATEGY-01): four strategies as versioned
data records, one shared contract shape, one code-owned fallback, and the
picker row contract.

Strategies are data, never Python subclasses. That is the `subjects.py`
D-01/D-02 precedent and it is the reason a fifth strategy is a registry entry
plus a fixture rather than a class hierarchy. The fallback is code-owned and
is never replaced by settings data (the D-03 precedent): a settings file that
could redefine what happens when everything else is unavailable is a settings
file that can break the degraded path.

This module is deliberately surface-free and runtime-free. A strategy
influences selection and presentation. It never touches scoring, keyed
disclosure, or evidence settlement, and the import list is the structural
proof: standard library and nothing else.

Naming, per D-16C-6 and D15: the per-action states this registry's contracts
reference are strategy-action states, which are learner task states
(lowercase activity). The Activity view (capitalized) is the 16B IA area for
durable agent and maintenance jobs and is not this module's subject.

What this module does NOT do, by plan: no precedence resolution (16C-05 adds
`composed_resolve` here and owns every use of `ia.mode_layer_resolve`), no
evidence events (16C-06), no sitting logic, and no rendering.
"""
import copy


STRATEGY_SCHEMA_VERSION = 1

# The closed set (D-16C-4). Report 12 section 10.2's remaining modes are the
# catalog runway, not omissions: Minimal lesson folds into continuous
# reading, and Close reading stays deferred until provenance relocation
# works. No fifth strategy registers in 16C.
STRATEGY_IDS = ("continuous_reading", "guided_note_spine",
                "worked_reasoning", "retrieval_first")

# Code-owned forever, the subjects.DEFAULT_PROFILE precedent.
FALLBACK_STRATEGY = "continuous_reading"

# Locked copy, transcribed verbatim from the 16C-UI-SPEC Copywriting
# Contract. Never re-worded here; a change is a UI-SPEC change.
STRATEGY_NAMES = {
    "continuous_reading": "Continuous reading",
    "guided_note_spine": "Guided note spine",
    "worked_reasoning": "Worked reasoning",
    "retrieval_first": "Retrieval first",
}
STRATEGY_PURPOSES = {
    "continuous_reading": "Read straight through, with optional highlights and notes.",
    "guided_note_spine": "Prompted selection and restatement as you go.",
    "worked_reasoning": "Predict, explain, and self-check worked steps.",
    "retrieval_first": "Try questions first, then read what you missed.",
}

# The two lifecycle event types D-16C-1 locks. Every contract's
# `evidence_effects` names only these. A lifecycle event carries at most a
# note ID reference, never note content, never learner wording, never
# selected text: deletable learner content inside an append-only store is a
# contradiction, so the append-only half records only that something
# happened.
LIFECYCLE_EVENT_TYPES = ("activity_completed", "activity_skipped")

# The eleven contract keys, the report 12 section 10.1 list as locked by
# D-16C-4. Declared as a tuple so the completeness check reads one source.
CONTRACT_KEYS = ("strategy_id", "version", "learning_purpose", "eligibility",
                 "required_actions", "optional_actions", "skip_resume",
                 "evidence_effects", "accommodations", "offline_behavior",
                 "tests")

STRATEGY_CONTRACTS = {
    "continuous_reading": {
        "strategy_id": "continuous_reading",
        "version": STRATEGY_SCHEMA_VERSION,
        "learning_purpose": "Build a continuous mental model of the material "
                            "before breaking it into tasks.",
        # Always eligible: it is the fallback, so an eligibility rule that
        # could exclude it would leave the degraded path with nowhere to go.
        "eligibility": "always",
        "required_actions": (),
        "optional_actions": ("highlight", "add_note"),
        "skip_resume": "resumes at the last read heading; skipping is always "
                       "allowed",
        # An abandoned reading emits nothing. There is no started event and
        # no partial-completion event, because presence in a document is not
        # an achievement and recording it would put presence in a denominator.
        "evidence_effects": ("activity_completed",),
        "accommodations": {
            "highlight": "keyboard block-and-range picker and structured "
                         "block-choice list, both equivalent to pointer "
                         "selection (D13)",
            "add_note": "reachable in the normal tab order at the end of "
                        "each block's controls; 44px touch target; never "
                        "hover-only",
        },
        "offline_behavior": "fully available offline",
        "tests": ("tests/strategy_registry_roundtrip.py",),
    },
    "guided_note_spine": {
        "strategy_id": "guided_note_spine",
        "version": STRATEGY_SCHEMA_VERSION,
        "learning_purpose": "Turn reading into selection and restatement, so "
                            "the learner's own wording exists to review.",
        "eligibility": "any lesson carrying headings a note can anchor to",
        "required_actions": ("select_target", "restate_in_own_words"),
        "optional_actions": ("add_question",),
        "skip_resume": "each prompted block may be skipped as "
                       "skipped_optional; resume returns to the first block "
                       "without a strategy-action state of completed or "
                       "skipped_optional",
        "evidence_effects": ("activity_completed", "activity_skipped"),
        "accommodations": {
            "select_target": "structured block-choice list, the D13 "
                             "keyboard and touch equivalent of pointer "
                             "selection; drag-only highlighting is forbidden",
            "restate_in_own_words": "plain text entry reachable by keyboard "
                                    "with a labeled field; no drag, hover, "
                                    "or pointer-only path exists",
            "add_question": "the same labeled text entry, optional",
        },
        "offline_behavior": "fully available offline",
        "tests": ("tests/strategy_registry_roundtrip.py",
                  "tests/note_trio_roundtrip.py"),
    },
    "worked_reasoning": {
        "strategy_id": "worked_reasoning",
        "version": STRATEGY_SCHEMA_VERSION,
        "learning_purpose": "Make the reasoning between steps explicit, so a "
                            "wrong prediction is visible before the answer "
                            "is.",
        "eligibility": "any lesson carrying worked steps or an example order",
        "required_actions": ("predict_next_step", "explain_step",
                             "self_check"),
        "optional_actions": (),
        "skip_resume": "a step may be skipped as skipped_optional; resume "
                       "returns to the first unresolved step",
        "evidence_effects": ("activity_completed", "activity_skipped"),
        "accommodations": {
            "predict_next_step": "labeled text entry or structured choice, "
                                 "both keyboard reachable",
            "explain_step": "labeled text entry, keyboard reachable, no "
                            "pointer-only path",
            "self_check": "a labeled control in the normal tab order with a "
                          "44px touch target; never hover-only",
        },
        "offline_behavior": "fully available offline",
        "tests": ("tests/strategy_registry_roundtrip.py",
                  "tests/note_trio_roundtrip.py"),
    },
    "retrieval_first": {
        "strategy_id": "retrieval_first",
        "version": STRATEGY_SCHEMA_VERSION,
        "learning_purpose": "Attempt before reading, so the reading answers "
                            "a question the learner already has.",
        "eligibility": "only where objective policy permits an "
                       "assessment-first route (STRATEGY-01)",
        "required_actions": ("attempt_items_first",),
        "optional_actions": ("read_after",),
        "skip_resume": "skipping the attempt falls back to continuous "
                       "reading; resume returns to the unattempted items",
        # The item responses themselves flow through the shipped response
        # events and the one scorer, never through this registry. What this
        # strategy contributes to evidence is the lifecycle fact that its
        # activity was completed or skipped, and nothing about the answers.
        "evidence_effects": ("activity_completed", "activity_skipped"),
        "accommodations": {
            "attempt_items_first": "the shipped item surfaces, whose "
                                   "keyboard, touch, and screen-reader paths "
                                   "are the runtime's and are unchanged by "
                                   "this strategy",
            "read_after": "the ordinary reader, keyboard reachable",
        },
        "offline_behavior": "fully available offline",
        "tests": ("tests/strategy_registry_roundtrip.py",),
    },
}

# Locked copy, transcribed verbatim from the UI-SPEC Strategy Picker
# Contract.
PICKER_HEADING = "How do you want to work through this?"
UNAVAILABLE_COPY = "{Strategy name} isn't available right now. Continuing with continuous reading."
MID_SITTING_LOCK_COPY = "Strategy changes are paused during a test sitting."

PICKER_ROW_CLASSES = ("choosable", "fallback", "locked")


def strategy_contract(strategy_id):
    """A deep copy of one strategy's contract record.

    A copy, so a caller that annotates a contract for its own rendering
    cannot edit the registry for every later caller in the same process.

    Raises on an unknown id rather than returning an empty contract, because
    a silently tolerated unknown read is exactly how a fifth mode rides in
    unregistered.
    """
    if strategy_id not in STRATEGY_IDS:
        raise ValueError("unknown strategy: %r" % (strategy_id,))
    return copy.deepcopy(STRATEGY_CONTRACTS[strategy_id])


def resolve_strategy(requested, available, allowed):
    """The one availability rule: the requested strategy when it is
    registered, available, and allowed; otherwise `FALLBACK_STRATEGY`.

    STRATEGY-01's degraded contract is a fallback, not an error, so this
    raises nothing at all. An unknown id, an unavailable id, and a disallowed
    id all return continuous reading, and the picker explains which case it
    was rather than this function signalling it.

    Pure: no I/O, no settings read, no clock.
    """
    if requested in STRATEGY_IDS and requested in available \
            and requested in allowed:
        return requested
    return FALLBACK_STRATEGY


def picker_rows(available, allowed, locked_copy_by_id=None):
    """One row per registered strategy, in registry order, in one of the
    three D8 row classes.

    The picker renders what the resolver returns and never computes its own
    availability: two availability rules drift, and the fallback fixture then
    proves whichever one it happened to call.

    Disallowed strategies are SHOWN and explained, not hidden (D8), so a
    learner can see why a choice is absent rather than wondering whether it
    is missing.

    `locked_copy_by_id` supplies the 16B conflict sentence per strategy. It
    is an argument rather than a lookup because
    `ia.mode_layer_conflict_copy` is the single source of that sentence and
    plan 16C-05's composed resolver is the only caller allowed to produce it.
    Until then a locked row may carry the empty string; the 16C-09 tracer
    asserts that interim state never reaches a learner surface blank.
    """
    locked_copy_by_id = locked_copy_by_id or {}
    degraded = any(sid in allowed and sid not in available
                   for sid in STRATEGY_IDS)
    rows = []
    for strategy_id in STRATEGY_IDS:
        name = STRATEGY_NAMES[strategy_id]
        row = {"strategy_id": strategy_id,
               "name": name,
               "purpose": STRATEGY_PURPOSES[strategy_id],
               "row_class": "choosable",
               "copy": "",
               "preselected": False}
        if strategy_id not in allowed:
            row["row_class"] = "locked"
            row["copy"] = locked_copy_by_id.get(strategy_id, "")
        elif strategy_id not in available:
            row["row_class"] = "fallback"
            row["copy"] = UNAVAILABLE_COPY.replace("{Strategy name}", name)
        rows.append(row)

    # When any allowed strategy is unavailable, continuous reading is
    # preselected: the degraded path made visible rather than inferred.
    # Otherwise the first choosable row is preselected.
    if degraded:
        for row in rows:
            if row["strategy_id"] == FALLBACK_STRATEGY:
                row["preselected"] = True
                break
    else:
        for row in rows:
            if row["row_class"] == "choosable":
                row["preselected"] = True
                break
    return rows
