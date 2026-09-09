#!/usr/bin/env python3
"""The capability support profile registry (Phase 16A, CAP-02, D-16A-2).

A capability profile answers one question: does a renderer for this authored
capability exist here, and what does a learner see when it does not. It
records the accessible behavior, the offline fallback, the renderer
availability, the profile version, how the capability is validated, and its
known limits, so an authored block's degradation is a published fact rather
than a discovery made at render time.

**A capability profile never decides disclosure.** Renderer availability
describes whether a renderer exists; it never describes whether a learner may
see an answer, a key, a rationale, or a hint tier. That decision belongs to
`runtime.public_item` and `runtime.glossable` and to no other module, and
nothing here may be read as widening it. A capability that is `available`
grants a rendering path and grants nothing else.

A profile answers two questions and no others: does a renderer for this
capability exist here, and what does a learner see when it does not. It never
answers whether a learner may see an answer. `runtime.glossable`'s own
docstring states the boundary this module stays behind: "the runtime, not the
author and not a model, decides what reaches the learner".

`activity_fallback` follows the same boundary: it reports WHICH declared
fallback text applies to an activity whose response form this build does not
have, and never decides whether a learner may respond, retry, or see a mark.
That is the runtime's call and this module cannot reach it.

An output-mode record is DERIVED and DISPOSABLE. The canonical Markdown stays
complete with every composed outline, glossary, rendered page, index, and
cache deleted, and every string in a composed record can be found in that
file. That is PORT-01's clause, "derived HTML, index, or cache is never the
sole understandable copy", and not a convention of this module: a composer
that invented content would make the view the only place the content existed.

**This module is pure.** It reads no file, writes no file, holds no session
state, and imports neither `evidence` nor `runtime`. Every public function
returns a value computed from its arguments and this module's own constants,
so calling one twice with the same arguments returns the same answer and
calling one never changes what another sees.

Adding a capability is a one-entry registration in the module-level dict
below, the pattern `model.GATE_VALUES` and `surfaces/lesson.py`'s
`_CALLOUT_KINDS` already establish. `register()` returns a new dict rather
than mutating the module's own, so a fixture or a test that registers a
synthetic capability cannot leak it into another caller's view.

`SEMANTIC_ROLE_CATALOG` is a catalog and not a source of truth (D-16A-1
option-a): `surfaces.lesson._CALLOUT_KINDS` and the seven shipped mechanisms
outside it remain authoritative for what a role means, and the catalog exists
only so CAP-01's fourteen-role completeness claim is machine checkable rather
than prose that can quietly go stale.
"""

import identity


# The exact key set every capability profile carries, in this order. A profile
# missing a key or carrying an extra one is refused by `register`, so a
# half-described capability cannot enter the registry and be discovered later
# by a renderer that assumed the field was there.
CAPABILITY_PROFILE_KEYS = ("name", "accessible_behavior", "offline_fallback",
                           "renderer_availability", "version", "validation",
                           "known_limits")

# The closed renderer-availability vocabulary (D-16A-5), in GATE_VALUES' exact
# shape. Three members rather than two: the binary present-or-absent split
# cannot describe a renderer that works partially, and a partial renderer
# reported as `available` is how a learner meets a half-drawn block with no
# warning.
RENDERER_AVAILABILITY = ("available", "degraded", "unavailable")

# The closed set of facts a CALLER may state about its own situation when it
# asks what a capability resolves to. Every one is a fact about the caller, not
# about this module, which is why `resolved_availability` takes them as an
# argument instead of discovering them: a module that read the environment
# itself would make a static CLI render and a served render disagree for
# reasons neither could inspect.
CAPABILITY_CONTEXT_KEYS = ("serving_runtime", "gate_context", "scripting",
                           "math_assets", "network")

# The media rights vocabulary, BY REFERENCE and never by value (D-16A-8).
# Retyping the three strings here would mint a second rights vocabulary, which
# is the exact failure `16A-RESEARCH.md` Pitfall 4 names. `identity` is a pure
# module with no import-time side effect, so a top-level import is safe.
MEDIA_RIGHTS_STATES = identity.RIGHTS_STATES

# Whether an asset's bytes sit beside the lesson, are absent, or are reachable
# only over a network. This is an availability vocabulary, not a rights one:
# `present` says nothing about whether the asset may be used, and `remote` is
# not a denial.
MEDIA_AVAILABILITY = ("present", "missing", "remote")


# The two output modes registered in Phase 16A (CAP-03). Both are registered
# because both already have a shared primitive that ships: the outline's spine
# is `model.parse_lesson`'s headings list plus, where a course is in play,
# `graph.outline_projection`; the glossary's spine is `model.parse_terms`,
# which has shipped since Phase 3.1. Neither gets a private extractor.
OUTPUT_MODES = ("outline", "glossary")

# The other eight modes CAP-03 names. PARKED, NOT CUT.
# `PLANNING-DIRECTIVES.md` section 3a: "A capability is not dropped merely
# because it is optional, expensive, specialized, or absent from the next
# wave. Simplicity alone is not a rejection reason." Each carries a shared
# primitive, a dependency, a cost, and a revisit trigger in
# `backburner_catalog()`, which is CAP-03's Degraded clause and is the route
# back. An entry with an empty trigger is a deletion wearing a catalog entry's
# clothes, which is why `backburner_entry` refuses one.
#
# Together with OUTPUT_MODES this must equal CAP-03's ten named modes exactly.
# If a mode fell out of both lists it would vanish with nothing noticing.
BACKBURNER_MODES = ("notebook_page", "cornell_notes", "concept_map",
                    "formula_sheet", "timeline", "comparison_table",
                    "study_guide", "source_extracted_notes")

# The key set every composed output-mode record carries. `derived_from` is the
# list of source identifiers the record was built from, and it is what makes
# the record honest about being a view: a reader holding one can always find
# its way back to the canonical file.
OUTPUT_MODE_KEYS = ("mode", "title", "entries", "provenance", "derived_from")

# The key set every backburner entry carries, from CAP-03's Degraded clause's
# own four field names plus the mode.
BACKBURNER_KEYS = ("mode", "shared_primitive", "dependency", "cost",
                   "trigger")


class CapabilityError(Exception):
    """A malformed capability registration: a wrong key set, an availability
    value outside the closed vocabulary, or a name already registered."""


# The fifteen capability profiles (CAP-02). The first fourteen are in
# `SEMANTIC_ROLE_CATALOG`'s order, so the two lists read the same way down the
# page; `guided_mode` is last because it is the one capability that is not a
# teaching role.
#
# `offline_fallback` is never empty: a capability with no fallback fails
# CAP-02's Degraded clause by construction, and `validate_profile` refuses it.
# `known_limits` never says "none": every one of these fifteen has at least one
# real limitation, and a profile that hides it is worse than no profile.
_CAPABILITY_PROFILES = {
    "callout_key": {
        "name": "callout_key",
        "accessible_behavior": (
            "Renders as a labelled section carrying a visible text label and "
            "an aria-hidden decorative glyph, reachable in document order by "
            "keyboard and by screen reader with no interaction required. The "
            "id anchor and the add-to-review control are ordinary focusable "
            "elements."),
        "offline_fallback": (
            "The card renders as a labelled section with its title and body "
            "intact and no script; the add-to-review control is replaced by "
            "the locked unavailable copy rather than by a dead button."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports a card with no title and no cloze marker as "
            "key.no_front, an unminted card as key.missing_id, and two cards "
            "sharing an id as key.duplicate_id."),
        "known_limits": (
            "Cloze markers blank only in the drill print sheet, never in "
            "the reader, so a learner reading on screen sees every answer "
            "the card was written to hide. The Key point label is not "
            "translated and carries the lesson's document language."),
    },
    "callout_warning": {
        "name": "callout_warning",
        "accessible_behavior": (
            "Renders as a labelled section with a visible text label; "
            "reachable in document order by keyboard and by screen reader "
            "with no interaction required."),
        "offline_fallback": (
            "The block renders as a labelled section with no script and no "
            "network."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports an unknown callout kind as "
            "lesson.unknown_semantic."),
        "known_limits": (
            "A warning whose force depends on a date or a jurisdiction "
            "carries that in free prose; D-16A-7 mints no structured "
            "effective_date or jurisdiction field in Phase 16A, so nothing "
            "detects a warning that has gone stale."),
    },
    "callout_prerequisite": {
        "name": "callout_prerequisite",
        "accessible_behavior": (
            "Renders as a labelled section with a visible text label; "
            "reachable in document order by keyboard and by screen reader "
            "with no interaction required."),
        "offline_fallback": (
            "The block renders as a labelled paragraph with no script and no "
            "network."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports an unknown callout kind as "
            "lesson.unknown_semantic."),
        "known_limits": (
            "The block names a prerequisite in prose and is not linked to "
            "the course graph's prerequisite edges, so a lesson can claim a "
            "prerequisite the graph does not carry and nothing notices. The "
            "label is not translated and carries the lesson's document "
            "language."),
    },
    "callout_misconception": {
        "name": "callout_misconception",
        "accessible_behavior": (
            "Renders as a labelled section with a visible text label; "
            "reachable in document order by keyboard and by screen reader "
            "with no interaction required."),
        "offline_fallback": (
            "The block renders as a labelled section with no script and no "
            "network."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports an unknown callout kind as "
            "lesson.unknown_semantic."),
        "known_limits": (
            "Nothing links a stated misconception to the distractor "
            "analysis of any item, so a lesson and a bank can describe the "
            "same error in two unrelated ways and drift apart as either is "
            "edited. The Common mistake label is not translated."),
    },
    "callout_tip": {
        "name": "callout_tip",
        "accessible_behavior": (
            "Renders as a labelled section with a visible text label; "
            "reachable in document order by keyboard and by screen reader "
            "with no interaction required."),
        "offline_fallback": (
            "The block renders as a labelled section with no script and no "
            "network."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports an unknown callout kind as "
            "lesson.unknown_semantic."),
        "known_limits": (
            "Nothing distinguishes a tip that is a shortcut from a tip "
            "that is a safety practice, so a reader cannot tell which one is "
            "safe to skip. The Expert tip label is not translated."),
    },
    "callout_example": {
        "name": "callout_example",
        "accessible_behavior": (
            "Renders as a labelled section with a visible text label; "
            "reachable in document order by keyboard and by screen reader "
            "with no interaction required. The parallel reader setting "
            "changes the layout class and never the reading order. Explicit "
            "COMPARE examples add a labelled native slider, reset button, "
            "text status and labelled meters. Human accessibility review is owed."),
        "offline_fallback": (
            "The block renders as a labelled section with no script and no "
            "network; the parallel layout degrades to the stacked default. "
            "COMPARE retains the authored static explanation and starting "
            "difference when JavaScript is absent or when printed."),
        "renderer_availability": "available",
        "version": 2,
        "validation": (
            "model.lint reports a heading placing a definition before its "
            "first worked example as lesson.definition_before_example, and "
            "an override with no reason as lesson.example_order_no_reason. "
            "parse_lesson_comparison owns bounded whole-number parameters. "
            "Invalid declarations report lesson.invalid_comparison."),
        "known_limits": (
            "COMPARE uses runtime.glossable over the complete authored block "
            "and respects required lesson gates. No authored "
            "code, scoring, persistence or model call is supported. The "
            "static explanation's educational adequacy needs author review."),
    },
    "callout_counterexample": {
        "name": "callout_counterexample",
        "accessible_behavior": (
            "Renders as a labelled section with a visible text label; "
            "reachable in document order by keyboard and by screen reader "
            "with no interaction required."),
        "offline_fallback": (
            "The block renders as a labelled section with no script and no "
            "network."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports an unknown callout kind as "
            "lesson.unknown_semantic."),
        "known_limits": (
            "Nothing pairs a counterexample with the example it contrasts, "
            "so the relationship lives only in the author's prose and an "
            "edit to either can leave the pair incoherent. The "
            "Counterexample label is not translated."),
    },
    "callout_excerpt": {
        "name": "callout_excerpt",
        "accessible_behavior": (
            "Renders as a labelled section with a visible text label; "
            "reachable in document order by keyboard and by screen reader "
            "with no interaction required."),
        "offline_fallback": (
            "The block renders as a labelled section with no script and no "
            "network."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports an unknown callout kind as "
            "lesson.unknown_semantic, an unresolvable [SRC:] as "
            "prov.src_unknown, and an excerpt body reproducing keyed "
            "material as lesson.authored_key_disclosure."),
        "known_limits": (
            "The callout carries no structural link to a ## SOURCES row, so "
            "an excerpt can name its source in prose while citing nothing "
            "the provenance pass can check. Quoting rights are declared "
            "elsewhere and are not enforced here (D-16A-8)."),
    },
    "glossary_definition": {
        "name": "glossary_definition",
        "accessible_behavior": (
            "Every [[term]] reference is a real focusable control: the "
            "definition opens on hover, on keyboard focus and activation, "
            "and on touch activation, and the panel is reachable in document "
            "order by a screen reader. The reader page ships every "
            "definition inline, so no network request is needed to read one, "
            "and the trigger's navigation href remains a real fallback."),
        "offline_fallback": (
            "With no network and no scripting the definitions are still on "
            "the page and every trigger still navigates to its panel; the "
            "in-sitting fetch enhancement is inert and never leaves a "
            "spinner or a dead control."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports an unresolvable [[term]] as "
            "terms.unknown_ref, two terms slugifying alike as "
            "terms.duplicate_slug, and an empty entry as terms.empty_block."),
        "known_limits": (
            "A term whose definition could disclose keyed answer material is "
            "suppressed by runtime.glossable, and the served route returns a "
            "bare 404 that a caller cannot distinguish from an unknown term. "
            "That is deliberate and is recorded in the Phase 03.1 decision "
            "log, but it means a learner meeting a suppressed term is told "
            "nothing about why."),
    },
    "callout_uncertainty": {
        "name": "callout_uncertainty",
        "accessible_behavior": (
            "Renders as a labelled section with a visible text label; "
            "reachable in document order by keyboard and by screen reader "
            "with no interaction required."),
        "offline_fallback": (
            "The block renders as a labelled section with no script and no "
            "network."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports an unknown callout kind as "
            "lesson.unknown_semantic."),
        "known_limits": (
            "The block records that something is unsettled in prose only. "
            "Nothing marks the objectives or the items downstream of an "
            "uncertainty, so a disputed claim can still be assessed as "
            "though it were settled."),
    },
    "callout_summary": {
        "name": "callout_summary",
        "accessible_behavior": (
            "Renders as a labelled section with a visible text label; "
            "reachable in document order by keyboard and by screen reader "
            "with no interaction required."),
        "offline_fallback": (
            "The block renders as a labelled section with no script and no "
            "network."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports an unknown callout kind as "
            "lesson.unknown_semantic."),
        "known_limits": (
            "Nothing checks that a summary agrees with the section it "
            "summarizes, so an edited section can leave a stale summary "
            "standing under it."),
    },
    "inline_check": {
        "name": "inline_check",
        "accessible_behavior": (
            "With a session, the gate band is a labelled section whose "
            "controls are ordinary focusable form elements in document "
            "order. Without one, the reserved slot is a labelled section "
            "carrying static text, with no form, no key, and no control to "
            "focus."),
        "offline_fallback": (
            "This check is available when you are reading with a session."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports a [!CHECK: <id>] naming no item in its own "
            "bank as lesson.check_ref_unknown, and an invalid gate policy as "
            "lesson.invalid_gate."),
        "known_limits": (
            "The slot resolves only against items in its own bank; a check "
            "referencing an item in another bank cannot be expressed. An "
            "unresolvable check never gates, so a typo silently loosens the "
            "gate rather than tightening it."),
    },
    "hint_ladder": {
        "name": "hint_ladder",
        "accessible_behavior": (
            "Each tier is requested by an ordinary focusable control and "
            "arrives as text in document order; an unavailable tier keeps "
            "its numbered slot and says it is unavailable rather than "
            "disappearing and shifting later tiers forward."),
        "offline_fallback": (
            "Without a serving runtime the ladder is not offered at all and "
            "the item renders with its stem and options only; no tier is "
            "ever rendered from the bank file directly, because the runtime "
            "and not the page decides what a tier discloses."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports the authored fields each tier reads: "
            "item.lesson_ref_unknown for tier 0, "
            "item.objective_unnamespaced for tier 1, item.missing_trap for "
            "tier 2, item.distractor_missing for tier 3, and "
            "item.missing_why_best for tier 5."),
        "known_limits": (
            "All six tiers are authored rather than generated, so an item "
            "whose author wrote no trap has a permanently unavailable tier 2 "
            "and nothing fills it. Tier order is fixed and cannot be "
            "reordered per item or per subject."),
    },
    "visual_interaction": {
        "name": "visual_interaction",
        "accessible_behavior": (
            "Every visual item carries a required non-empty "
            "accessibility.description naming the scene and the task in "
            "words, and every committed action is expressible as semantic "
            "domain data rather than as a pointer trajectory, so the item is "
            "answerable without seeing or dragging anything."),
        "offline_fallback": (
            "The stem and the accessibility description render as text and "
            "the item states that the interactive scene needs a session; no "
            "scene is drawn and no action is accepted."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "model.lint reports a malformed contract as "
            "item.visual_json_malformed, an unknown interaction as "
            "item.visual_unknown_interaction, an empty description as "
            "item.visual_empty_accessibility, and a script-bearing member as "
            "item.visual_executable_member."),
        "known_limits": (
            "Scoring is dichotomous: partial_credit must be false, so a "
            "nearly correct scene scores the same as an empty one. The "
            "accessibility description is required to be non-empty and is "
            "not checked for actually describing the scene."),
    },
    "guided_mode": {
        "name": "guided_mode",
        "accessible_behavior": (
            "Every stage is server rendered into one document in reading "
            "order, so the whole lesson is reachable by keyboard and by "
            "screen reader with no interaction and no script; only the first "
            "stage carries the open marker."),
        "offline_fallback": (
            "The same document is the fallback: with no script and no "
            "network every stage is already present and readable in order, "
            "and the continuous mode renders the identical containers."),
        "renderer_availability": "available",
        "version": 1,
        "validation": (
            "tests/capability_stress_corpus_tracer.py asserts every callout "
            "container is character for character identical across "
            "continuous and guided mode, so guided mode grouping a block "
            "cannot re-render it."),
        "known_limits": (
            "Nothing persists across a stage boundary in Phase 16A: reading "
            "position and resume are Phase 16B's (D-16A-9). A stage boundary "
            "falls at each callout, so a heading with no callouts is one "
            "stage however long it is."),
    },
}


def _registry_or_default(registry):
    return _CAPABILITY_PROFILES if registry is None else registry


def profile(name, registry=None):
    """The profile registered under `name`, as a shallow copy, or `None`.

    A copy rather than the stored dict, so a caller that edits what it was
    handed cannot silently rewrite the registry for every later caller. An
    unregistered name returns `None` rather than raising and rather than
    returning a partial dict: an absent capability is an ordinary answer here,
    and the caller decides what to do about it.
    """
    entry = _registry_or_default(registry).get(name)
    return dict(entry) if entry is not None else None


def profiles(registry=None):
    """Every registered profile, as shallow copies, in insertion order, which
    for the module's own registry is its literal source order."""
    return tuple(dict(entry)
                 for entry in _registry_or_default(registry).values())


def register(entry, registry=None):
    """Return a NEW registry carrying `entry` alongside the existing ones.

    Mutates nothing. `register` is the only way a capability enters a
    registry, so its three refusals are the only place a malformed profile can
    be caught: a key set that is not exactly `CAPABILITY_PROFILE_KEYS`, a
    `renderer_availability` outside the closed vocabulary, and a name already
    present. Each raises `CapabilityError` naming the offending value, because
    a registration is code and not authored content, so it fails loudly rather
    than falling back.
    """
    if not isinstance(entry, dict):
        raise CapabilityError(
            "a capability profile must be a dict, got %s"
            % type(entry).__name__)
    keys = tuple(sorted(entry))
    if keys != tuple(sorted(CAPABILITY_PROFILE_KEYS)):
        raise CapabilityError(
            "a capability profile carries exactly the keys %s; got %s"
            % (", ".join(CAPABILITY_PROFILE_KEYS), ", ".join(keys)))
    availability = entry["renderer_availability"]
    if availability not in RENDERER_AVAILABILITY:
        raise CapabilityError(
            "renderer_availability %r is not one of %s"
            % (availability, ", ".join(RENDERER_AVAILABILITY)))
    current = _registry_or_default(registry)
    name = entry["name"]
    if name in current:
        raise CapabilityError(
            "a capability named %r is already registered; registering a "
            "second one would make which profile a renderer reads depend on "
            "registration order" % name)
    merged = dict(current)
    merged[name] = dict(entry)
    return merged


def static_path(name, registry=None):
    """The profile's `offline_fallback` sentence, or the empty string for an
    unregistered name.

    The empty string rather than an exception on purpose: an unregistered
    capability degrades to nothing, which is the same shape as a capability
    that declares no fallback, and a caller rendering a fallback should not
    have to branch on which of those two it met.
    """
    entry = _registry_or_default(registry).get(name)
    return entry["offline_fallback"] if entry is not None else ""


# CAP-01's fourteen semantic teaching roles, in the order the requirement
# lists them, each pointing at the concrete mechanism that renders it. Seven
# of the fourteen shipped before Phase 16A and are catalogued here rather than
# rebuilt; the seven carrying `shipped_in` "16A" are this phase's own.
#
# This tuple is a catalog, never an authority. Nothing renders from it and
# nothing gates on it. It exists so a test can walk CAP-01's completeness
# claim and fail by name when an entry stops resolving, which prose in a
# requirements file cannot do.
SEMANTIC_ROLE_CATALOG = (
    {"role": "key idea",
     "mechanism": "the [!KEY] index card",
     "module": "surfaces.lesson",
     "shipped_in": "3.1",
     "reachable_by": "> [!KEY]"},
    {"role": "warning",
     "mechanism": "the [!WARNING] callout",
     "module": "surfaces.lesson",
     "shipped_in": "3.1",
     "reachable_by": "> [!WARNING]"},
    {"role": "prerequisite",
     "mechanism": "the [!PREREQUISITE] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!PREREQUISITE]"},
    {"role": "misconception",
     "mechanism": "the [!MISCONCEPTION] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!MISCONCEPTION]"},
    {"role": "expert tip",
     "mechanism": "the [!TIP] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!TIP]"},
    {"role": "worked example",
     "mechanism": "the [!EXAMPLE] callout",
     "module": "surfaces.lesson",
     "shipped_in": "3.1",
     "reachable_by": "> [!EXAMPLE]"},
    {"role": "counterexample",
     "mechanism": "the [!COUNTEREXAMPLE] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!COUNTEREXAMPLE]"},
    {"role": "source excerpt",
     "mechanism": "the [!EXCERPT] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!EXCERPT]"},
    {"role": "term and definition",
     "mechanism": "the ## TERMS registry and [[term]] references",
     "module": "model",
     "shipped_in": "3.1",
     "reachable_by": "model.parse_terms"},
    {"role": "uncertainty",
     "mechanism": "the [!UNCERTAINTY] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!UNCERTAINTY]"},
    {"role": "summary",
     "mechanism": "the [!SUMMARY] callout",
     "module": "surfaces.lesson",
     "shipped_in": "16A",
     "reachable_by": "> [!SUMMARY]"},
    {"role": "inline check",
     "mechanism": "the [!CHECK: <id>] reserved slot and its gate band",
     "module": "surfaces.lesson",
     "shipped_in": "6.2",
     "reachable_by": "surfaces.lesson._gate_band_html"},
    {"role": "hint",
     "mechanism": "the six-tier authored hint ladder",
     "module": "runtime",
     "shipped_in": "6",
     "reachable_by": "runtime.authored_hint"},
    {"role": "accessible visual interaction",
     "mechanism": "the visual item type and its interaction contract",
     "module": "runtime",
     "shipped_in": "06.1",
     "reachable_by": "runtime.public_item"},
)


# Which capability profile describes which CAP-01 role. The two lists cannot
# be derived from each other: "key idea" is rendered by `callout_key` and
# "term and definition" by `glossary_definition`, and no naming rule connects
# those. Written out once here so the cross-check in
# `tests/capability_profile_check.py` can prove every catalogued role has a
# profile and that exactly one profile, `guided_mode`, describes something
# that is not a teaching role. Without this map, adding a role in a later
# phase would leave a profile-less capability nothing notices.
_ROLE_PROFILE_NAMES = {
    "key idea": "callout_key",
    "warning": "callout_warning",
    "prerequisite": "callout_prerequisite",
    "misconception": "callout_misconception",
    "expert tip": "callout_tip",
    "worked example": "callout_example",
    "counterexample": "callout_counterexample",
    "source excerpt": "callout_excerpt",
    "term and definition": "glossary_definition",
    "uncertainty": "callout_uncertainty",
    "summary": "callout_summary",
    "inline check": "inline_check",
    "hint": "hint_ladder",
    "accessible visual interaction": "visual_interaction",
}


def catalog_profile_name(role):
    """The capability profile name describing one CAP-01 role, or `None` for
    a role CAP-01 does not list."""
    return _ROLE_PROFILE_NAMES.get(role)


def role_mechanism(role):
    """The `SEMANTIC_ROLE_CATALOG` entry for `role`, as a shallow copy, or
    `None` for a name CAP-01 does not list.

    A copy for `profile()`'s reason: a caller that edits what it was handed
    must not be able to rewrite the catalog every later caller reads.
    """
    for entry in SEMANTIC_ROLE_CATALOG:
        if entry["role"] == role:
            return dict(entry)
    return None


# How far each capability can be lowered by the caller's own situation. The
# declared `renderer_availability` is a ceiling; these rules are the floor.
#
# These rules are Phase 16A's policy, not CAP-02's: the requirement names the
# six fields and the Degraded clause, and says nothing about which context
# fact lowers which capability. They are written out as data so a later phase
# extends them additively instead of reinventing them in a caller.
_AVAILABILITY_ORDER = {"unavailable": 0, "degraded": 1, "available": 2}


def _lowered_by_context(name, context):
    """The floor `name` is lowered to by `context`, as an availability
    string. Pure: reads no file, no environment variable, and no global. An
    unknown key in `context` is ignored rather than refused, so a caller from
    a later phase supplying a sixth fact does not break this function."""
    if name == "inline_check":
        return "available" if context.get("gate_context") else "unavailable"
    if name == "visual_interaction":
        if not context.get("scripting"):
            return "unavailable"
        return "available" if context.get("serving_runtime") else "degraded"
    if name == "glossary_definition":
        # Never unavailable: the shipped page ships every definition inline
        # and every panel stays reachable, so a scriptless reader is reduced
        # and not cut off.
        return "available" if context.get("scripting") else "degraded"
    if name == "hint_ladder":
        return "available" if context.get("serving_runtime") else "unavailable"
    # guided_mode and every callout_* capability are server rendered and need
    # nothing, so no context fact lowers them.
    return "available"


def resolved_availability(name, context, registry=None):
    """What `name` actually resolves to for a caller in `context`.

    The lower of two answers: the profile's own declared
    `renderer_availability`, which is a ceiling a caller cannot raise, and
    the floor `context` lowers it to. An unregistered name resolves to
    `unavailable`, because a capability nothing declares is a capability
    nothing can render.
    """
    entry = _registry_or_default(registry).get(name)
    if entry is None:
        return "unavailable"
    declared = entry.get("renderer_availability")
    if declared not in RENDERER_AVAILABILITY:
        return "unavailable"
    floor = _lowered_by_context(name, context or {})
    return min((declared, floor), key=lambda v: _AVAILABILITY_ORDER[v])


def validate_profile(entry):
    """Every way one capability profile is malformed, as a list of
    human-readable finding strings, in a stable order. An empty list means
    the profile is well formed.

    Findings rather than an exception, and never raising on any input: this
    is the function a test, a schema-coupling check, and a future authoring
    surface all call to ask "what is wrong with this", and each wants the
    whole list rather than the first problem. `register` is where a
    malformed profile is refused loudly.
    """
    findings = []
    if not isinstance(entry, dict):
        return ["a capability profile must be a dict, got %s"
                % type(entry).__name__]
    keys = tuple(sorted(entry))
    if keys != tuple(sorted(CAPABILITY_PROFILE_KEYS)):
        findings.append(
            "key set is %s; a capability profile carries exactly %s"
            % (", ".join(keys), ", ".join(CAPABILITY_PROFILE_KEYS)))
    availability = entry.get("renderer_availability")
    if availability not in RENDERER_AVAILABILITY:
        findings.append(
            "renderer_availability %r is not one of %s"
            % (availability, ", ".join(RENDERER_AVAILABILITY)))
    version = entry.get("version")
    if not isinstance(version, int) or isinstance(version, bool) \
            or version < 1:
        findings.append("version %r is not a positive integer" % (version,))
    for field in ("name", "accessible_behavior", "offline_fallback",
                  "validation", "known_limits"):
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            findings.append(
                "%s is empty; CAP-02 requires every profile field to say "
                "something, and an empty offline_fallback fails its "
                "Degraded clause by construction" % field)
    return findings


def activity_fallback(activity):
    """The `static_fallback` text of an activity whose declared response form
    is not one of the eight shipped ones, or the empty string.

    ACTIVITY-01's Degraded clause verbatim: "an unsupported response form
    falls back to its declared static equivalent". This function answers only
    which text that is. It never decides whether a learner may respond, how
    many attempts they get, or what a mark means: those belong to
    `runtime.score_response` and `runtime.public_item`, and nothing here may
    be read as widening them.

    `model` is imported inside the function on purpose, so this module keeps
    its no-top-level-dependency-on-the-parser property and stays importable
    on its own. Pure: no file read, no global, no side effect.
    """
    import model

    if not isinstance(activity, dict):
        return ""
    form = (activity.get("response_schema") or "").strip()
    if form in model.RESPONSE_FORMS:
        return ""
    return (activity.get("static_fallback") or "").strip()


def _outline_entry(text, slug, depth):
    return {"text": text, "slug": slug, "depth": depth}


def _graph_outline_entries(graph_doc):
    """The objective spine `graph.outline_projection` produces, normalized
    into outline entries.

    `graph` and `model` are imported inside the function, so this module gains
    no top-level dependency on a Phase 14B module and stays importable on its
    own.

    The landed `outline_projection(doc)` returns the course as a plain
    Markdown STRING rather than a list of records, so the normalization here
    is a read of its heading lines. It computes NO objective ordering of its
    own: the order is whatever that projection emitted, which is the whole
    reason this delegates instead of walking the graph. A second outline
    generator here would be the duplicated-truth pattern CAP-03 rejects.
    """
    import re

    import graph
    import model

    projected = graph.outline_projection(graph_doc)
    entries = []
    for line in (projected or "").split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        if m is None:
            continue
        text = m.group(2)
        entries.append(_outline_entry(text, model.lesson_slug(text),
                                      len(m.group(1))))
    return entries


def compose_outline(lesson, graph_doc=None):
    """The `outline` output mode, composed from one parsed lesson (CAP-03).

    Pure: no file read, no write, no global. Two calls on the same lesson dict
    return equal dicts.

    `entries` is `lesson["headings"]` in DOCUMENT order, each carrying the
    heading's own `text` and the `slug` `parse_lesson` already computed. The
    slug is not recomputed: `parse_lesson` is the one place a heading becomes
    a slug, and a composer that computed a second one would drift from every
    anchor and every `[LESSON-REF:]` in the tree. `depth` is `1` for every
    lesson heading because the shipped grammar has exactly one heading level
    under `## LESSON`.

    When `graph_doc` is supplied, the objective spine from
    `graph.outline_projection` is prepended and this function computes no
    objective ordering of its own.

    Nothing here is authoritative. The record is a view of the canonical
    Markdown, and `derived_from` names what it is a view of.
    """
    if not isinstance(lesson, dict):
        lesson = {}
    source = lesson.get("source") or ""
    entries = []
    if graph_doc is not None:
        entries.extend(_graph_outline_entries(graph_doc))
    for heading in lesson.get("headings") or []:
        entries.append(_outline_entry(heading.get("text") or "",
                                      heading.get("slug") or "", 1))
    derived_from = [source] if source else []
    if graph_doc is not None:
        provenance = ("Composed from the lesson headings and the course graph "
                      "outline projection of %s." % (source or "no source"))
        course_id = ""
        if isinstance(graph_doc, dict):
            header = graph_doc.get("header") or {}
            course_id = str(header.get("course_id")
                            or header.get("title") or "")
        if course_id:
            derived_from.append(course_id)
    else:
        provenance = ("Composed from the lesson headings alone of %s."
                      % (source or "no source"))
    return {"mode": "outline",
            "title": "Outline",
            "entries": entries,
            "provenance": provenance,
            "derived_from": derived_from}


def compose_glossary(terms, source=""):
    """The `glossary` output mode, composed from one parsed `## TERMS`
    registry (CAP-03).

    Pure, for `compose_outline`'s reasons. `entries` are sorted by slug so the
    glossary has one stable reading order regardless of authored row order.

    A term is never re-extracted from the lesson body and a slug is never
    recomputed: `model.parse_terms` is the one term extractor and has been
    since Phase 3.1.

    `terms` of `None` is a normal lesson with no glossary, not an error, so it
    returns an empty record rather than raising.

    `source` is optional and names the canonical file the terms came from.
    `model.parse_terms` does not carry a path in its return, unlike
    `parse_sources`, `parse_media`, and `parse_activities`, so a caller that
    wants the provenance sentence to name the file passes it. Omitting it
    yields a record that is still correct and simply less specific about what
    it is a view of.
    """
    if not isinstance(terms, dict) or not (terms.get("terms") or {}):
        return {"mode": "glossary",
                "title": "Glossary",
                "entries": [],
                "provenance": ("No ## TERMS registry was present, so this "
                               "glossary is empty."),
                "derived_from": []}
    source = source or terms.get("path") or ""
    entries = []
    for slug in sorted(terms["terms"]):
        record = terms["terms"][slug]
        entries.append({"term": record.get("canonical") or "",
                        "slug": slug,
                        "definition": record.get("def") or ""})
    return {"mode": "glossary",
            "title": "Glossary",
            "entries": entries,
            "provenance": ("Composed from the ## TERMS registry of %s."
                           % (source or "the parsed bank")),
            "derived_from": [source] if source else []}


def backburner_entry(entry):
    """One validated backburner catalog record, as a shallow copy.

    Raises `CapabilityError` naming the offending field when the key set is
    not exactly `BACKBURNER_KEYS` or when any value is empty after stripping.

    The `trigger` field is the one that gets left empty, which is why all four
    are refused rather than only the key set: a parked capability with a
    primitive, a dependency, and a cost but no revisit condition looks
    documented and is functionally deleted. That is the failure
    `PLANNING-DIRECTIVES.md` section 3a's append-only rule exists to prevent.
    """
    if not isinstance(entry, dict):
        raise CapabilityError(
            "a backburner entry must be a dict, got %s"
            % type(entry).__name__)
    keys = tuple(sorted(entry))
    if keys != tuple(sorted(BACKBURNER_KEYS)):
        raise CapabilityError(
            "a backburner entry carries exactly the keys %s; got %s"
            % (", ".join(BACKBURNER_KEYS), ", ".join(keys)))
    for field in BACKBURNER_KEYS:
        value = entry[field]
        if not isinstance(value, str) or not value.strip():
            raise CapabilityError(
                "backburner entry %r has an empty %s; a parked capability "
                "with no %s is a deletion wearing a catalog entry's clothes"
                % (entry.get("mode"), field, field))
    return dict(entry)


_BACKBURNER_CATALOG = (
    {"mode": "notebook_page",
     "shared_primitive": (
         "The parsed lesson headings list plus the ## ACTIVITIES registry, "
         "interleaved in document order."),
     "dependency": (
         "Phase 16B's reading position, because a notebook page is a place a "
         "learner returns to and a page with no position is a second copy of "
         "the reader."),
     "cost": (
         "Small once reading position exists: one composer over two schemas "
         "that already parse, plus a decision about where a learner's own "
         "note attaches without becoming source truth."),
     "trigger": (
         "Register it when Phase 16B has landed a durable reading position "
         "and the learner-note object has a recorded source of truth.")},
    {"mode": "cornell_notes",
     "shared_primitive": (
         "The lesson headings list for the cue column and the ## TERMS "
         "registry for the recall column."),
     "dependency": (
         "The learner-note durable object, because the summary band is "
         "learner-authored and must never become lesson truth."),
     "cost": (
         "Small as a composer, real as a contract: the layout is three "
         "regions and the hard part is that one of them is the learner's and "
         "two are the course's."),
     "trigger": (
         "Register it when a learner note has a source of truth and an "
         "accepted-revision path, so the summary band cannot silently become "
         "the lesson.")},
    {"mode": "concept_map",
     "shared_primitive": (
         "The course graph's prerequisite and objective edges, "
         "graph.outline_projection's spine, and the ## TERMS registry's "
         "see-also links."),
     "dependency": (
         "A non-visual equivalent that is genuinely equivalent, not a "
         "consolation: a map whose only readable form is a picture fails the "
         "authored-output accessibility gate."),
     "cost": (
         "The largest of the eight. Layout, an accessible traversal order, "
         "and a keyboard path through a graph are three problems, and none "
         "of them is a composer over an existing schema."),
     "trigger": (
         "Register it when Phase 17A has a component foundation and an "
         "accessible node-and-edge traversal has passed the authored-output "
         "accessibility review.")},
    {"mode": "formula_sheet",
     "shared_primitive": (
         "The lesson's fenced math blocks, which lesson_fence_languages "
         "already enumerates, plus the ## TERMS registry for symbol "
         "definitions."),
     "dependency": (
         "A symbol-to-meaning link the format does not currently carry: a "
         "formula sheet whose symbols are undefined is a picture of "
         "notation."),
     "cost": (
         "Small for the extraction, moderate for the symbol table, because "
         "the symbol table is authored content that does not exist yet."),
     "trigger": (
         "Register it when a lesson can declare what a symbol means in a "
         "form parse_terms or a successor can read.")},
    {"mode": "timeline",
     "shared_primitive": (
         "The ## SOURCES registry's locators and the visual item type's "
         "timeline interaction family, which shipped in Phase 999.1."),
     "dependency": (
         "A dated-claim field the format does not have. D-16A-7 deferred a "
         "structured effective_date, so a timeline today would order prose "
         "by guessing."),
     "cost": (
         "Moderate. The rendering primitive exists; the dated, cited claim "
         "it would render does not."),
     "trigger": (
         "Register it when a structured date or effective-period field lands "
         "with 15B's staleness machinery, which is the phase D-16A-7 names.")},
    {"mode": "comparison_table",
     "shared_primitive": (
         "The shipped table and dnd item types' categories and rows, and the "
         "## ACTIVITIES registry's comparison purpose."),
     "dependency": (
         "A surface that renders a composed output-mode record. No composed "
         "mode reaches one today: compose_outline and compose_glossary "
         "return dicts and nothing displays them, so a third composer would "
         "have nowhere to appear either."),
     "cost": (
         "The smallest of the eight to compose: one composer over row and "
         "category data that already parses, plus a decision about how a "
         "table with no keyed answer differs from a table item. The surface "
         "it needs is not its cost and is shared with the other seven."),
     "trigger": (
         "Register it when Phase 16B lands a surface that renders a composed "
         "output-mode record, which is the same condition the other seven "
         "wait on and the first one that will actually be met.")},
    {"mode": "study_guide",
     "shared_primitive": (
         "Every other mode's output: the outline's spine, the glossary's "
         "entries, the activity registry's purposes, and the evidence "
         "store's per-objective record."),
     "dependency": (
         "The two registered modes and the retention and evidence readers, "
         "because a study guide that does not know what the learner has "
         "already shown is a table of contents with a longer name."),
     "cost": (
         "Moderate, and almost all of it is selection policy rather than "
         "composition: deciding what to leave out is the whole feature."),
     "trigger": (
         "Register it when a per-objective evidence read is available to a "
         "composer and Phase 15A's treatment policy can say what a learner "
         "should study next.")},
    {"mode": "source_extracted_notes",
     "shared_primitive": (
         "The ## SOURCES registry, the [SRC:] locator directives, and the "
         "14C source adapter registry's normalized document."),
     "dependency": (
         "The quote and transform rights grants, because extracting a note "
         "from a source is exactly the operation D-16A-8 says 16A declares "
         "and does not enforce."),
     "cost": (
         "Moderate for the extraction, high for the rights path: this is the "
         "one parked mode whose blocker is authority rather than code."),
     "trigger": (
         "Register it when the subphase that owns rights enforcement can "
         "re-check a quote grant live at the moment of extraction, which is "
         "the discipline D-16A-8 already names.")},
)


def backburner_catalog():
    """The eight parked output modes, each validated (CAP-03's Degraded
    clause).

    Validated on the way out rather than trusted: a catalog entry that lost
    its trigger in an edit would raise here instead of quietly reading as a
    documented capability with no route back.
    """
    return tuple(backburner_entry(entry) for entry in _BACKBURNER_CATALOG)
