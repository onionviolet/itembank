#!/usr/bin/env python3
"""Focused checks for bounded public typed-field schemas and validator caps."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import schema_validate                                      # noqa: E402


ITEM_SCHEMA_PATH = os.path.join(ROOT, "schemas", "item.schema.json")
with open(ITEM_SCHEMA_PATH, encoding="utf-8") as handle:
    ITEM_SCHEMA = json.load(handle)


def fail(message):
    print("FAIL: " + message)
    sys.exit(1)


def field_id(index):
    return "field_%d" % index


def public_fill():
    fields = [
        {"id": "term", "label": "术语", "kind": "text",
         "case_sensitive": False, "whitespace": "trim"},
        {"id": "dose", "label": "Dose", "kind": "numeric",
         "units": ["μg", "mg"]},
    ]
    return {
        "schema_version": 1,
        "id": "q1",
        "number": 1,
        "type": "fill",
        "stem": "Complete every field.",
        "difficulty": "recall",
        "lesson_slug": "",
        "fields": fields,
        "response_schema": {
            "type": "object",
            "required": [field["id"] for field in fields],
            "values": "string",
            "additional_properties": False,
        },
    }


def expect_valid(instance, message):
    errors = schema_validate.validate(instance, ITEM_SCHEMA)
    if errors:
        fail("%s: %s" % (message, "; ".join(errors)))


def expect_invalid(instance, message):
    if not schema_validate.validate(instance, ITEM_SCHEMA):
        fail(message)


def check_validator_max_keywords():
    schema = {
        "type": "array",
        "minItems": 1,
        "maxItems": 2,
        "items": {"type": "string", "minLength": 1, "maxLength": 3},
    }
    schema_validate.check_schema(schema)
    if schema_validate.validate(["one", "二"], schema):
        fail("maxItems/maxLength schema rejected values at their bounds")
    too_many = schema_validate.validate(["a", "b", "c"], schema)
    if not any("maxItems 2" in error for error in too_many):
        fail("maxItems did not reject a three-element array: %r" % too_many)
    too_long = schema_validate.validate(["four"], schema)
    if not any("maxLength 3" in error for error in too_long):
        fail("maxLength did not reject a four-character string: %r" % too_long)


def check_valid_public_fill():
    expect_valid(public_fill(),
                 "multilingual labels and printable Unicode units must validate")
    without_units = public_fill()
    del without_units["fields"][1]["units"]
    expect_valid(without_units, "numeric units are optional")


def check_field_and_required_caps():
    item = public_fill()
    item["fields"] = [
        {"id": field_id(i), "label": "Field %d" % i, "kind": "numeric"}
        for i in range(17)
    ]
    item["response_schema"]["required"] = [field["id"]
                                               for field in item["fields"]]
    expect_invalid(item, "a public fill item exposed more than 16 fields")

    item = public_fill()
    item["response_schema"]["required"] = [field_id(i) for i in range(17)]
    expect_invalid(item, "response_schema.required accepted more than 16 IDs")


def check_field_ids_and_labels():
    for bad_id in ("constructor", "prototype", "Upper", "1field",
                   "x" * 33, "field\n"):
        item = public_fill()
        item["fields"][0]["id"] = bad_id
        item["response_schema"]["required"][0] = bad_id
        expect_invalid(item, "invalid public field ID validated: %r" % bad_id)

    for bad_label in ("   ", "x" * 201, "line\nbreak", "bad\x00label",
                      "bad\x85label", "bad\u2028label", "bad\u2029label"):
        item = public_fill()
        item["fields"][0]["label"] = bad_label
        expect_invalid(item, "invalid public label validated: %r" % bad_label)


def check_unit_alias_bounds():
    for bad_units in (
            ["u%d" % i for i in range(17)],
            ["x" * 25],
            ["m s"],
            ["m\n"],
            ["bad\x85"],
            ["bad\u2028"],
            ["bad\u2029"],
    ):
        item = public_fill()
        item["fields"][1]["units"] = bad_units
        expect_invalid(item, "invalid public unit aliases validated: %r"
                       % bad_units)


def check_private_rules_and_runtime_diagnostic_shape():
    for private, value in (("accepted", ["secret"]), ("answer", "2"),
                           ("atol", "0.1"), ("rtol", "0.1"),
                           ("unit", "mg")):
        item = public_fill()
        item["fields"][1][private] = value
        expect_invalid(item, "public field accepted private member %r" % private)

    observation = {
        "case_index": 1,
        "passed": False,
        "reason": "runtime_error",
        "actual": "42\n",
        "stderr": "RuntimeError: boom\n",
        "exit_code": 1,
        "expected": "42",
        "expected_kind": "output",
        "input": "",
    }
    observation_schema = ITEM_SCHEMA["$defs"]["case_observation"]
    errors = schema_validate.validate(observation, observation_schema)
    if errors:
        fail("bounded runtime-error observation failed schema: %s"
             % "; ".join(errors))
    bad = dict(observation, exit_code="1")
    if not schema_validate.validate(bad, observation_schema):
        fail("case observation accepted a non-integer exit_code")


def main():
    checks = [
        check_validator_max_keywords,
        check_valid_public_fill,
        check_field_and_required_caps,
        check_field_ids_and_labels,
        check_unit_alias_bounds,
        check_private_rules_and_runtime_diagnostic_shape,
    ]
    for check in checks:
        check()
    print("schema_bounds_roundtrip: %d checks passed" % len(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
