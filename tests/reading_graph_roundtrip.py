#!/usr/bin/env python3
"""Permanent reading binding, occurrence revision, and placement contract."""
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import graph  # noqa: E402
import identity  # noqa: E402
import schema_validate  # noqa: E402


def fail(message):
    raise AssertionError(message)


def eq(got, want, label):
    if got != want:
        fail("%s: want %r, got %r" % (label, want, got))


def raises(call, code, label):
    try:
        call()
    except graph.GraphError as error:
        eq(error.code, code, label + " code")
        return error
    fail(label + ": expected GraphError")


def fingerprint(marker="a"):
    return "sha256:" + marker * 64


def build():
    course_id = identity.new_object_id()
    doc = graph.new_course("Reading graph", course_id)
    objective = graph.add_objective(doc, "Read the selected section")
    source_id = identity.new_object_id()
    graph.add_source(doc, source_id, "Synthetic source")
    graph.add_binding(
        doc, "treatment", objective["id"], source_id,
        treatment_kind="direct-reading", locator="section 1",
        state="covered", confidence="high", rights_snapshot="granted")
    return doc, objective["id"], source_id


def occurrence_values(binding, objective_id, source_id, marker="a"):
    return {
        "objective_ids": [objective_id],
        "binding_ref": {
            "binding_id": binding["binding_id"],
            "binding_revision_id": binding["binding_revision_id"],
        },
        "source_ref": {
            "source_object_id": source_id,
            "source_fingerprint": fingerprint(marker),
            "locator": binding["locator"],
            "range": {
                "span_id": "span-1",
                "locator_id": None,
                "locator_sidecar_fingerprint": None,
            },
        },
        "purpose": "Read for the main distinction | then compare examples.",
        "preparation_mode": "preread",
        "path_role": "required-instructor-work",
        "learning_phase": "Ahead",
        "sequence_evidence": {
            "status": "Published",
            "citation": "syllabus p. 1",
        },
        "assignment_provenance": {
            "authority": "instructor",
            "citation": "syllabus p. 1",
        },
        "assistance_policy": {
            "status": "unknown",
            "citation": None,
            "instruction": None,
        },
    }


def clean_record(row, section):
    return {key: row[key] for key in graph.SECTION_COLUMNS[section]}


def legacy_binding_fixture(populated=False, unknowns=False):
    path = os.path.join(ROOT, "fixtures", "golden_sidecar_pre_15b.md")
    text = open(path, encoding="utf-8").read()
    if populated:
        rule = "|---|---|---|---|---|---|---|---|"
        row = ("| treatment | 93abf6bff28e4d22 | 86ead446d33843f8 | "
               "direct-reading | section 1 | covered | high | granted |")
        text = text.replace(rule, rule + "\n" + row, 1)
    if unknowns:
        header = ("| binding_kind | objective | source_object_id | "
                  "treatment_kind | locator | state | confidence | "
                  "rights_snapshot |")
        text = text.replace(header, header + " future_note |", 1)
        text = text.replace("|---|---|---|---|---|---|---|---|",
                            "|---|---|---|---|---|---|---|---|---|", 1)
        if populated:
            text = text.replace(
                "| direct-reading | section 1 | covered | high | granted |",
                "| direct-reading | section 1 | covered | high | granted | keep |",
                1)
        text += ("\n## Future reading view\n\n| mode | value |\n"
                 "|---|---|\n| experimental | visible |\n")
    return text


def check_legacy_and_enrollment():
    for label, text in (
            ("empty", legacy_binding_fixture()),
            ("populated", legacy_binding_fixture(populated=True)),
            ("unknown metadata",
             legacy_binding_fixture(populated=True, unknowns=True))):
        parsed = graph.parse_course(text)
        eq(graph.serialize_course(parsed), text,
           "pre-change %s graph remains byte-identical" % label)
        if "## Reading occurrences" in text or "## Reading placement" in text:
            fail("empty optional reading sections must not enter a legacy graph")

    old = graph.parse_course(legacy_binding_fixture(populated=True))
    objective_id = old["objectives"][1]["id"]
    source_id = old["sources"][0]["source_object_id"]
    graph.add_binding(old, "treatment", objective_id, source_id,
                      treatment_kind="direct-reading", locator="section 2")
    mixed = graph.serialize_course(old)
    reparsed = graph.parse_course(mixed)
    eq(len(reparsed["bindings"]), 2,
       "an unversioned row joins a pre-change binding table")
    eq(reparsed["bindings"][1]["locator"], "section 2",
       "the mixed legacy table reparses without semantic loss")

    extended = graph.parse_course(legacy_binding_fixture(populated=True, unknowns=True))
    graph.enroll_binding(extended, 0, fingerprint())
    graph.add_binding(extended, "treatment", objective_id, source_id,
                      treatment_kind="direct-reading", locator="section 3")
    reloaded = graph.parse_course(graph.serialize_course(extended))
    eq(reloaded["bindings"][0]["extra"]["future_note"], "keep",
       "enrollment retains the original unknown-column content")
    eq(reloaded["bindings"][1]["locator"], "section 3",
       "new unversioned row aligns with the enrolled unknown-column table")
    eq(reloaded["bindings"][1]["binding_id"], "",
       "adding a row does not accidentally enroll it through shifted columns")

    duplicate, _, _ = build()
    duplicate["bindings"].append(copy.deepcopy(duplicate["bindings"][0]))
    before_other = copy.deepcopy(duplicate["bindings"][1])
    first = graph.enroll_binding(duplicate, 0, fingerprint())
    if first["binding_id"] == "" or first["binding_revision_id"] == "":
        fail("enrollment must mint both permanent identities")
    eq(duplicate["bindings"][1]["binding_id"], "",
       "exact selection leaves the duplicate row unversioned")
    eq({key: duplicate["bindings"][1][key] for key in before_other
        if key not in ("columns",)},
       {key: before_other[key] for key in before_other if key not in ("columns",)},
       "enrollment preserves the duplicate row metadata")

    for bad_index in (-1, True):
        doc, _, _ = build()
        before = copy.deepcopy(doc)
        raises(lambda: graph.enroll_binding(doc, bad_index, fingerprint()),
               "graph.unknown_binding_row", "unsafe row index")
        eq(doc, before, "unsafe row index leaves the graph unchanged")


def check_occurrence_and_d3():
    doc, objective_id, source_id = build()
    binding = graph.enroll_binding(doc, 0, fingerprint())
    for malformed_values in (
            {"objective_ids": [{}]},
            {"source_ref": {
                "source_object_id": source_id,
                "source_fingerprint": fingerprint(),
                "locator": 7,
                "range": {"span_id": "span-1", "locator_id": None,
                          "locator_sidecar_fingerprint": None}}}):
        values = occurrence_values(binding, objective_id, source_id)
        values.update(malformed_values)
        before = copy.deepcopy(doc)
        raises(lambda: graph.add_reading_occurrence(
            doc, values, "Reading", "Now"),
            "graph.malformed_reading_record", "malformed occurrence input")
        eq(doc, before, "malformed occurrence input leaves the graph unchanged")
    occurrence = graph.add_reading_occurrence(
        doc, occurrence_values(binding, objective_id, source_id),
        "Read section 1", "Now")
    root_revision = occurrence["revision_id"]
    serialized = graph.serialize_course(doc)
    parsed = graph.parse_course(serialized)
    eq(graph.serialize_course(parsed), serialized,
       "versioned reading graph remains byte-identical")
    decoded = json.loads(parsed["reading_occurrences"][0]["document"])
    eq(decoded["purpose"],
       "Read for the main distinction | then compare examples.",
       "escaped table pipe returns as authored JSON text")

    graph.update_reading_placement(doc, occurrence["occurrence_id"],
                                   "Renamed section 1", "Library")
    eq(len(doc["reading_occurrences"]), 1,
       "placement edit appends no occurrence revision")
    eq(json.loads(doc["reading_occurrences"][0]["document"])["revision_id"],
       root_revision, "D3 preserves the occurrence revision")
    graph.update_reading_placement(doc, occurrence["occurrence_id"],
                                   "Renamed section 1", "Future shelf")
    placement = graph.validate_reading_placement(doc["reading_placement"][0])
    eq(placement["activation"], "Future shelf",
       "unknown activation remains visible")
    eq(placement["effective_activation"], "unsupported",
       "unknown activation grants no scheduling authority")

    second = graph.append_reading_revision(
        doc, occurrence["occurrence_id"], {"purpose": "Read again for causality."})
    eq(second["supersedes_revision_id"], root_revision,
       "material revision pins its parent")
    eq(len(doc["reading_occurrences"]), 2,
       "material revision retains its ancestor")
    eq(len(doc["reading_placement"]), 1,
       "material revision keeps one occurrence placement")

    for title, activation in ((" title", "Now"), ("title", "Library "),
                              ("title\rbreak", "Now")):
        before = copy.deepcopy(doc)
        raises(lambda: graph.update_reading_placement(
            doc, occurrence["occurrence_id"], title, activation),
            "graph.malformed_reading_placement", "unsafe placement")
        eq(doc, before, "unsafe placement leaves the graph unchanged")


def check_shared_reading_identity():
    doc, objective_id, source_id = build()
    binding = graph.enroll_binding(doc, 0, fingerprint())
    values = occurrence_values(binding, objective_id, source_id)
    first = graph.add_reading_occurrence(doc, values, "Prepare", "Now")
    second_values = copy.deepcopy(values)
    second_values["preparation_mode"] = "prelearn"
    second = graph.add_reading_occurrence(doc, second_values, "Deepen", "Now")
    before_source = copy.deepcopy(doc["sources"])
    before_binding = copy.deepcopy(doc["bindings"])
    for activation in ("Library", "Now"):
        graph.update_reading_placement(doc, first["occurrence_id"], "Renamed", activation)
        doc = graph.parse_course(graph.serialize_course(doc))
    eq(graph.validate_reading_graph(doc)["occurrences"], [first, second],
       "rename and Now/Library/Now preserve both independent revision identities")
    for changes in ({}, {"purpose": first["purpose"]}):
        before = copy.deepcopy(doc)
        raises(lambda: graph.append_reading_revision(doc, first["occurrence_id"], changes),
               "graph.invalid_reading_revision", "unchanged reading task")
        eq(doc, before, "saving unchanged task content does not mint a revision")
    successor = graph.append_reading_revision(
        doc, first["occurrence_id"], {"purpose": "Compare the two explanations."})
    doc = graph.parse_course(graph.serialize_course(doc))
    eq(graph.validate_reading_graph(doc)["occurrences"], [first, second, successor],
       "revising one reading retains its ancestor and leaves the other unchanged")
    eq(doc["sources"], before_source, "reading edits leave shared source references intact")
    eq(doc["bindings"], before_binding, "task-demand revision retains shared binding")

    for change, code in (("fingerprint", "graph.reading_binding_mismatch"),
                         ("revision", "graph.missing_binding_revision")):
        wrong = copy.deepcopy(values)
        if change == "fingerprint":
            wrong["source_ref"]["source_fingerprint"] = fingerprint("b")
        else:
            wrong["binding_ref"]["binding_revision_id"] = identity.new_object_id()
        before = copy.deepcopy(doc)
        raises(lambda: graph.add_reading_occurrence(doc, wrong, "Wrong", "Now"),
               code, "mismatched source or binding reference")
        eq(doc, before, "reference mismatch preserves the graph")


def check_binding_revision_and_conflicts():
    doc, objective_id, source_id = build()
    binding = graph.enroll_binding(doc, 0, fingerprint())
    binding["extra"]["review_note"] = "keep me"
    binding["columns"].insert(2, "review_note")
    revised = graph.append_binding_revision(
        doc, binding["binding_id"],
        {"locator": "section 2", "source_fingerprint": fingerprint("b")})
    eq(revised["extra"]["review_note"], "keep me",
       "binding successor preserves unknown metadata")
    eq(revised["supersedes_binding_revision_id"],
       binding["binding_revision_id"], "binding successor pins its parent")
    eq(len(doc["bindings"]), 2, "binding history retains its ancestor")

    for bad in ({"locator": "bad|cell"}, {"locator": "bad\ncell"},
                {"locator": " padded "}, {"locator": 4}):
        before = copy.deepcopy(doc)
        raises(lambda: graph.append_binding_revision(
            doc, binding["binding_id"], bad),
            "graph.invalid_binding_revision_change", "unsafe binding revision")
        eq(doc, before, "unsafe binding revision leaves the graph unchanged")

    duplicate_binding = copy.deepcopy(doc)
    duplicate_binding["bindings"].append(
        copy.deepcopy(duplicate_binding["bindings"][0]))
    raises(lambda: graph.validate_reading_graph(duplicate_binding),
           "graph.duplicate_binding_revision", "duplicate binding identity")

    divergent_binding = copy.deepcopy(doc)
    conflict = copy.deepcopy(divergent_binding["bindings"][0])
    conflict["locator"] = "different locator"
    divergent_binding["bindings"].append(conflict)
    raises(lambda: graph.validate_reading_graph(divergent_binding),
           "graph.divergent_binding_revision", "divergent binding identity")

    cyclic_binding = copy.deepcopy(doc)
    cyclic_binding["bindings"][0]["supersedes_binding_revision_id"] = \
        cyclic_binding["bindings"][1]["binding_revision_id"]
    raises(lambda: graph.validate_reading_graph(cyclic_binding),
           "graph.cyclic_binding_revisions", "cyclic binding history")

    occurrence_doc, objective_id, source_id = build()
    enrolled = graph.enroll_binding(occurrence_doc, 0, fingerprint())
    occurrence = graph.add_reading_occurrence(
        occurrence_doc,
        occurrence_values(enrolled, objective_id, source_id),
        "Reading", "Now")
    row = occurrence_doc["reading_occurrences"][0]

    missing_placement = copy.deepcopy(occurrence_doc)
    missing_placement["reading_placement"] = []
    raises(lambda: graph.validate_reading_graph(missing_placement),
           "graph.missing_reading_placement", "missing placement")

    duplicate_placement = copy.deepcopy(occurrence_doc)
    duplicate_placement["reading_placement"].append(
        copy.deepcopy(duplicate_placement["reading_placement"][0]))
    raises(lambda: graph.validate_reading_graph(duplicate_placement),
           "graph.duplicate_reading_placement", "duplicate placement")

    duplicate_revision = copy.deepcopy(occurrence_doc)
    duplicate_revision["reading_occurrences"].append(copy.deepcopy(row))
    raises(lambda: graph.validate_reading_graph(duplicate_revision),
           "graph.duplicate_reading_revision", "duplicate occurrence identity")

    missing_parent = copy.deepcopy(occurrence_doc)
    altered = copy.deepcopy(occurrence)
    altered["revision_id"] = identity.new_object_id()
    altered["supersedes_revision_id"] = identity.new_object_id()
    missing_parent["reading_occurrences"].append(
        graph.new_record("Reading occurrences", {
            "occurrence_id": altered["occurrence_id"],
            "revision_id": altered["revision_id"],
            "document": graph._canonical_json(altered)}))
    raises(lambda: graph.validate_reading_graph(missing_parent),
           "graph.missing_reading_revision", "missing occurrence parent")

    branched = copy.deepcopy(occurrence_doc)
    for purpose in ("branch one", "branch two"):
        child = copy.deepcopy(occurrence)
        child["revision_id"] = identity.new_object_id()
        child["supersedes_revision_id"] = occurrence["revision_id"]
        child["purpose"] = purpose
        branched["reading_occurrences"].append(
            graph.new_record("Reading occurrences", {
                "occurrence_id": child["occurrence_id"],
                "revision_id": child["revision_id"],
                "document": graph._canonical_json(child)}))
    raises(lambda: graph.validate_reading_graph(branched),
           "graph.branching_reading_revisions", "branching occurrence history")

    cyclic = copy.deepcopy(occurrence_doc)
    cyclic_doc = copy.deepcopy(occurrence)
    cyclic_doc["supersedes_revision_id"] = cyclic_doc["revision_id"]
    cyclic["reading_occurrences"][0]["document"] = \
        graph._canonical_json(cyclic_doc)
    raises(lambda: graph.validate_reading_graph(cyclic),
           "graph.cyclic_reading_revisions", "cyclic occurrence history")


def check_schema():
    schema = json.load(open(os.path.join(
        ROOT, "schemas", "course_graph.schema.json"), encoding="utf-8"))
    schema_validate.check_schema(schema)
    doc, objective_id, source_id = build()
    binding = graph.enroll_binding(doc, 0, fingerprint())
    occurrence = graph.add_reading_occurrence(
        doc, occurrence_values(binding, objective_id, source_id),
        "Reading", "Now")
    for row in doc["bindings"]:
        errors = schema_validate.validate(
            clean_record(row, "Bindings"), schema["$defs"]["binding"])
        eq(errors, [], "versioned binding schema")
    errors = schema_validate.validate(
        clean_record(doc["reading_occurrences"][0], "Reading occurrences"),
        schema["$defs"]["reading_occurrence_row"])
    eq(errors, [], "occurrence table row schema")
    instance = {
        "header": dict(doc["header"]),
        "bindings": [clean_record(row, "Bindings")
                     for row in doc["bindings"]],
        "reading_occurrences": [
            clean_record(row, "Reading occurrences")
            for row in doc["reading_occurrences"]],
        "reading_placement": [
            clean_record(row, "Reading placement")
            for row in doc["reading_placement"]],
    }
    errors = schema_validate.validate(instance, schema)
    eq(errors, [], "full reading graph schema")
    errors = schema_validate.validate(
        clean_record(doc["reading_placement"][0], "Reading placement"),
        schema["$defs"]["reading_placement"])
    eq(errors, [], "reading placement schema")
    eq(schema_validate.validate(
        occurrence, schema["$defs"]["reading_occurrence_document"], root=schema),
       [], "decoded occurrence schema with resolved nested references")
    malformed = copy.deepcopy(occurrence)
    malformed["unexpected"] = True
    if not schema_validate.validate(
            malformed, schema["$defs"]["reading_occurrence_document"],
            root=schema):
        fail("closed occurrence schema must reject an unknown property")


def main():
    check_legacy_and_enrollment()
    check_occurrence_and_d3()
    check_shared_reading_identity()
    check_binding_revision_and_conflicts()
    check_schema()
    print("OK reading_graph_roundtrip")


if __name__ == "__main__":
    main()
