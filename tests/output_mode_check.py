#!/usr/bin/env python3
"""The Phase 16A output-mode unit check (plan 16A-07 Task 1).

CAP-03 names ten output modes and says an unregistered one stays a backburner
catalog entry naming its shared primitive, dependency, cost, and trigger. This
file asserts the shape of both halves: the four closed tuples, the two
composers over shared schemas, and the eight-entry catalog whose every entry
carries a route back.

The check that matters most here is the smallest-looking one:
`backburner_entry` must refuse an entry whose trigger is empty. A parked
capability with a primitive, a dependency, and a cost but no revisit condition
looks documented and is functionally deleted, which is what
`PLANNING-DIRECTIVES.md` section 3a's append-only rule exists to prevent.

Standard library only, no test framework, runnable as
`python tests/output_mode_check.py`.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import capabilities                                          # noqa: E402
import model                                                 # noqa: E402

LESSON_BANK = os.path.join(ROOT, "fixtures", "lesson_bank.md")
TERMS_BANK = os.path.join(ROOT, "fixtures", "terms_above_lesson_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def check_vocabularies():
    if capabilities.OUTPUT_MODES != ("outline", "glossary"):
        fail("OUTPUT_MODES is %r" % (capabilities.OUTPUT_MODES,))
    want = ("notebook_page", "cornell_notes", "concept_map", "formula_sheet",
            "timeline", "comparison_table", "study_guide",
            "source_extracted_notes")
    if capabilities.BACKBURNER_MODES != want:
        fail("BACKBURNER_MODES is %r" % (capabilities.BACKBURNER_MODES,))
    if capabilities.OUTPUT_MODE_KEYS != ("mode", "title", "entries",
                                         "provenance", "derived_from"):
        fail("OUTPUT_MODE_KEYS is %r" % (capabilities.OUTPUT_MODE_KEYS,))
    if capabilities.BACKBURNER_KEYS != ("mode", "shared_primitive",
                                        "dependency", "cost", "trigger"):
        fail("BACKBURNER_KEYS is %r" % (capabilities.BACKBURNER_KEYS,))

    registered = set(capabilities.OUTPUT_MODES)
    parked = set(capabilities.BACKBURNER_MODES)
    both = registered & parked
    if both:
        fail("modes %r are in both lists; a mode is registered or parked, "
             "never both" % sorted(both))
    if len(registered | parked) != 10:
        fail("the two lists cover %d modes, expected CAP-03's ten; a mode "
             "that fell out of both would vanish with nothing noticing"
             % len(registered | parked))


def _outline():
    return capabilities.compose_outline(model.parse_lesson(LESSON_BANK))


def check_compose_outline():
    lesson = model.parse_lesson(LESSON_BANK)
    record = _outline()
    if tuple(sorted(record)) != tuple(sorted(capabilities.OUTPUT_MODE_KEYS)):
        fail("the outline record carries the key set %s, expected exactly "
             "OUTPUT_MODE_KEYS" % sorted(record))
    if record["mode"] != "outline":
        fail("the outline record's mode is %r" % record["mode"])
    if len(record["entries"]) != len(lesson["headings"]):
        fail("the outline has %d entries for %d headings"
             % (len(record["entries"]), len(lesson["headings"])))
    for entry, heading in zip(record["entries"], lesson["headings"]):
        if entry["slug"] != heading["slug"]:
            fail("outline entry slug %r does not equal the parse_lesson slug "
                 "%r; a composer that recomputed a slug would drift from "
                 "every anchor in the tree" % (entry["slug"],
                                               heading["slug"]))
        if entry["text"] != heading["text"]:
            fail("outline entry text %r does not equal the heading text %r"
                 % (entry["text"], heading["text"]))
    if not record["provenance"].strip():
        fail("the outline record carries an empty provenance")
    if "headings alone" not in record["provenance"]:
        fail("the no-graph path's provenance does not say the outline came "
             "from the lesson headings alone: %r" % record["provenance"])
    if _outline() != record:
        fail("two compose_outline calls returned different records")


def check_compose_glossary():
    terms = model.parse_terms(TERMS_BANK)
    if terms is None:
        fail("the terms fixture no longer carries a ## TERMS section, so "
             "this check would prove nothing")
    record = capabilities.compose_glossary(terms, source=TERMS_BANK)
    if tuple(sorted(record)) != tuple(sorted(capabilities.OUTPUT_MODE_KEYS)):
        fail("the glossary record carries the key set %s, expected exactly "
             "OUTPUT_MODE_KEYS" % sorted(record))
    if record["mode"] != "glossary":
        fail("the glossary record's mode is %r" % record["mode"])
    if len(record["entries"]) != len(terms["terms"]):
        fail("the glossary has %d entries for %d registered terms"
             % (len(record["entries"]), len(terms["terms"])))
    slugs = [entry["slug"] for entry in record["entries"]]
    if slugs != sorted(slugs):
        fail("the glossary entries are not sorted by slug, so the reading "
             "order depends on authored row order")
    for entry in record["entries"]:
        if entry["slug"] not in terms["terms"]:
            fail("glossary entry slug %r is not a parse_terms key; a "
                 "composer that recomputed a slug would drift from every "
                 "[[term]] reference" % entry["slug"])
        record_for = terms["terms"][entry["slug"]]
        if entry["term"] != record_for["canonical"]:
            fail("glossary entry term %r does not equal the registered "
                 "canonical %r" % (entry["term"], record_for["canonical"]))
    if not record["provenance"].strip():
        fail("the glossary record carries an empty provenance")
    if capabilities.compose_glossary(terms, source=TERMS_BANK) != record:
        fail("two compose_glossary calls returned different records")


def check_glossary_degrades():
    """A lesson with no glossary is a normal lesson, not an error."""
    for empty in (None, {}, {"terms": {}}):
        record = capabilities.compose_glossary(empty)
        if record["entries"] != []:
            fail("compose_glossary(%r) produced entries" % (empty,))
        if tuple(sorted(record)) \
                != tuple(sorted(capabilities.OUTPUT_MODE_KEYS)):
            fail("the empty glossary record carries the key set %s"
                 % sorted(record))
        if not record["provenance"].strip():
            fail("the empty glossary record carries an empty provenance")


def check_backburner_catalog():
    catalog = capabilities.backburner_catalog()
    if len(catalog) != 8:
        fail("backburner_catalog returned %d entries, expected 8"
             % len(catalog))
    modes = [entry["mode"] for entry in catalog]
    if tuple(modes) != capabilities.BACKBURNER_MODES:
        fail("the catalog's modes are %r but BACKBURNER_MODES is %r"
             % (modes, list(capabilities.BACKBURNER_MODES)))
    for entry in catalog:
        capabilities.backburner_entry(entry)
        if "when needed" in entry["trigger"].lower():
            fail("%r's trigger is a vague phrase; a trigger a reader cannot "
                 "test is the same as no trigger" % entry["mode"])


def check_backburner_refuses_empty_trigger():
    """The check that keeps breadth from turning into silent cutting."""
    valid = dict(capabilities.backburner_catalog()[0])
    for field in capabilities.BACKBURNER_KEYS:
        broken = dict(valid)
        broken[field] = "   "
        try:
            capabilities.backburner_entry(broken)
        except capabilities.CapabilityError as exc:
            if field not in str(exc):
                fail("the refusal for an empty %s does not name the field: "
                     "%s" % (field, exc))
        else:
            fail("a backburner entry with an empty %s was accepted; a parked "
                 "capability missing that field looks documented and is "
                 "functionally deleted" % field)
    extra = dict(valid, colour="blue")
    try:
        capabilities.backburner_entry(extra)
    except capabilities.CapabilityError:
        pass
    else:
        fail("a backburner entry carrying an extra key was accepted")


CHECKS = (check_vocabularies, check_compose_outline, check_compose_glossary,
          check_glossary_degrades, check_backburner_catalog,
          check_backburner_refuses_empty_trigger)


def main():
    for check in CHECKS:
        check()
    print("output modes ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
