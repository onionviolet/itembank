#!/usr/bin/env python3
"""A minimal, hand-rolled JSON Schema validator -- and only that.

There is no JSON Schema implementation in the Python standard library, and this
is not a Draft 2020-12 reimplementation either. It is a subset validator scoped
to the exact keywords the documents under `schemas/` use: `type`,
`properties`, `required`, `additionalProperties`, `enum`, `const`, `items`,
`minItems`, `minLength`, `pattern`, `minimum`, `maximum`, `$defs`, `$ref`
(local `#/$defs/<name>` only), and `oneOf`. Nothing more.

The one decision that makes this worth trusting: a schema that uses a keyword
outside that set is refused, not partially checked. `check_schema` walks the
whole document before a single instance is examined and raises `SchemaError`
on anything it does not implement. A validator that silently ignored
`patternProperties` or `allOf` would report a green build while checking half
the contract -- which is worse than no check at all, because it looks like one.
A green result from this validator means the whole document was checked.
"""
import json
import re
import sys


SUPPORTED = frozenset([
    "type", "properties", "required", "additionalProperties", "enum", "const",
    "items", "minItems", "minLength", "pattern", "minimum", "maximum",
    "$defs", "$ref", "oneOf",
])

# Accepted and ignored: they describe the schema to a human reader but impose
# no constraint this validator checks.
ANNOTATIONS = frozenset([
    "$schema", "$id", "title", "description", "x-itembank-version",
    "default", "x-itembank-phase",
])


class SchemaError(Exception):
    """A problem with the *schema* itself -- an unsupported keyword, a
    malformed $ref -- as distinct from a problem with the instance being
    validated. The CLI exits 2 for this, 1 for an instance that fails
    validation, so "the schema is broken" is distinguishable from "the data
    is wrong" by exit code alone.
    """


def check_schema(schema, path="#", root=None):
    """Walk `schema` recursively and raise SchemaError on any keyword this
    validator does not implement. Called once at the top of `validate` so an
    unsupported keyword is reported before a single instance is examined.

    `root` carries the top-level document so a `$ref` can resolve and be
    recursed into, the same way `validate()` threads `root` down for
    instance checking -- a caller never passes it; it is set to `schema`
    itself on the first (non-recursive) call. Without this, a malformed or
    dangling `$ref` (e.g. `{"$ref": "#/$defs/typo"}`) would pass
    `check_schema()` silently and only surface later inside `validate()`,
    and only if an instance happened to exercise that exact branch --
    exactly the "looks green while checking half the contract" failure mode
    this function otherwise exists to prevent.
    """
    if root is None:
        root = schema
    if not isinstance(schema, dict):
        raise SchemaError("schema at %s is not an object: %r" % (path, schema))
    for kw, value in schema.items():
        if kw not in SUPPORTED and kw not in ANNOTATIONS:
            raise SchemaError("unsupported keyword %r at %s" % (kw, path))
        if kw == "$ref":
            if not (isinstance(value, str) and value.startswith("#/$defs/")):
                raise SchemaError("unsupported $ref target %r at %s" % (value, path))
            name = value[len("#/$defs/"):]
            defs = root.get("$defs", {}) if isinstance(root, dict) else {}
            if name not in defs:
                raise SchemaError("$ref %r at %s does not resolve" % (value, path))
            check_schema(defs[name], path + ".$ref(" + name + ")", root)
        elif kw == "properties":
            if not isinstance(value, dict):
                raise SchemaError("properties at %s is not an object" % path)
            for name, subschema in value.items():
                check_schema(subschema, path + ".properties." + name, root)
        elif kw == "$defs":
            if not isinstance(value, dict):
                raise SchemaError("$defs at %s is not an object" % path)
            for name, subschema in value.items():
                check_schema(subschema, path + ".$defs." + name, root)
        elif kw == "items":
            check_schema(value, path + ".items", root)
        elif kw == "oneOf":
            if not isinstance(value, list):
                raise SchemaError("oneOf at %s is not an array" % path)
            for i, subschema in enumerate(value):
                check_schema(subschema, path + ".oneOf[%d]" % i, root)


def _matches_type(instance, type_name):
    # A bool is an int in Python, and would otherwise validate as an integer
    # or a number -- exactly the kind of silent pass this validator exists to
    # avoid, so bool is excluded from both explicitly.
    if type_name == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if type_name == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if type_name == "null":
        return instance is None
    if type_name == "boolean":
        return isinstance(instance, bool)
    if type_name == "object":
        return isinstance(instance, dict)
    if type_name == "array":
        return isinstance(instance, list)
    if type_name == "string":
        return isinstance(instance, str)
    return False


def validate(instance, schema, root=None, path="$"):
    """Validate `instance` against `schema`, returning a list of error
    strings, one per failure, each shaped "%s: %s" % (path, message) so a
    caller can print them the way `cmd_lint` prints lint entries.

    `root` carries the top-level document so `$ref` can resolve; a caller
    never passes it -- it is set on the first (non-recursive) call, which is
    also where `check_schema` runs.
    """
    if root is None:
        check_schema(schema)
        root = schema

    if "$ref" in schema:
        ref = schema["$ref"]
        if not (isinstance(ref, str) and ref.startswith("#/$defs/")):
            raise SchemaError("unsupported $ref target %r at %s" % (ref, path))
        name = ref[len("#/$defs/"):]
        defs = root.get("$defs", {})
        if name not in defs:
            raise SchemaError("$ref %r at %s does not resolve" % (ref, path))
        return validate(instance, defs[name], root, path)

    errors = []

    if "type" in schema:
        t = schema["type"]
        types = t if isinstance(t, list) else [t]
        if not any(_matches_type(instance, tt) for tt in types):
            errors.append("%s: expected type %s, got %s" %
                          (path, t, type(instance).__name__))
            # Further structural checks (required/properties/items) assume the
            # type already matches; skip them rather than risk a spurious
            # crash on the wrong shape.
            return errors

    if "enum" in schema:
        allowed = schema["enum"]
        if not any(instance == a for a in allowed):
            errors.append("%s: %r is not one of %r" % (path, instance, allowed))

    if "const" in schema:
        if instance != schema["const"]:
            errors.append("%s: %r does not equal const %r" % (path, instance, schema["const"]))

    if "required" in schema and isinstance(instance, dict):
        for key in schema["required"]:
            if key not in instance:
                errors.append("%s: missing required key %r" % (path, key))

    if "properties" in schema and isinstance(instance, dict):
        for key, subschema in schema["properties"].items():
            if key in instance:
                errors.extend(validate(instance[key], subschema, root, path + "." + key))

    ap = schema.get("additionalProperties")
    if ap is not None and ap is not True and isinstance(instance, dict):
        allowed_keys = set(schema.get("properties", {}).keys())
        for key in instance:
            if key in allowed_keys:
                continue
            if ap is False:
                errors.append("%s: additional property %r is not allowed"
                              % (path, key))
            else:
                errors.extend(validate(instance[key], ap, root,
                                       path + "." + key))

    if "items" in schema and isinstance(instance, list):
        for i, el in enumerate(instance):
            errors.extend(validate(el, schema["items"], root, path + "[%d]" % i))

    if "minItems" in schema and isinstance(instance, list):
        if len(instance) < schema["minItems"]:
            errors.append("%s: has %d items, fewer than minItems %d" %
                          (path, len(instance), schema["minItems"]))

    if "minLength" in schema and isinstance(instance, str):
        if len(instance) < schema["minLength"]:
            errors.append("%s: has length %d, shorter than minLength %d" %
                          (path, len(instance), schema["minLength"]))

    if "pattern" in schema and isinstance(instance, str):
        if re.search(schema["pattern"], instance) is None:
            errors.append("%s: %r does not match pattern %r" %
                          (path, instance, schema["pattern"]))

    # A bool is never a number here, matching _matches_type's exclusion -- True
    # would otherwise satisfy `minimum: 0` as if it were 1.
    if "minimum" in schema and isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if instance < schema["minimum"]:
            errors.append("%s: %r is less than minimum %r" %
                          (path, instance, schema["minimum"]))

    if "maximum" in schema and isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if instance > schema["maximum"]:
            errors.append("%s: %r is greater than maximum %r" %
                          (path, instance, schema["maximum"]))

    if "oneOf" in schema:
        branches = schema["oneOf"]
        results = [validate(instance, b, root, path) for b in branches]
        matches = sum(1 for r in results if not r)
        if matches != 1:
            first_errors = results[0] if results else []
            errors.append(
                "%s: oneOf matched %d of %d branches (need exactly 1); "
                "first branch errors: %s" %
                (path, matches, len(branches),
                 "; ".join(first_errors) if first_errors else "(none)"))

    return errors


def _report(total, error_count):
    print("%d instances, %d errors" % (total, error_count))


def main(argv):
    if not argv:
        print("usage: schema_validate.py <schema.json> <instance.json | ->", file=sys.stderr)
        print("       schema_validate.py <schema.json> --jsonl <path>", file=sys.stderr)
        print("       schema_validate.py <schema.json> --array <path> <key>", file=sys.stderr)
        return 2

    schema_path = argv[0]
    rest = argv[1:]
    try:
        schema = json.load(open(schema_path, encoding="utf-8"))
    except Exception as exc:
        print("cannot read schema %s: %s" % (schema_path, exc))
        return 2

    try:
        if rest and rest[0] == "--jsonl":
            if len(rest) < 2:
                print("--jsonl requires a path")
                return 2
            lines = open(rest[1], encoding="utf-8").read().splitlines()
            total = error_count = 0
            for i, line in enumerate(lines, start=1):
                if not line.strip():
                    continue
                total += 1
                errs = validate(json.loads(line), schema)
                for e in errs:
                    print("line %d: %s" % (i, e))
                    error_count += 1
            _report(total, error_count)
            return 1 if error_count else 0

        if rest and rest[0] == "--array":
            if len(rest) < 3:
                print("--array requires a path and a key")
                return 2
            data = json.load(open(rest[1], encoding="utf-8"))
            items = data[rest[2]]
            total = error_count = 0
            for i, instance in enumerate(items):
                total += 1
                errs = validate(instance, schema)
                for e in errs:
                    print("%s[%d]: %s" % (rest[2], i, e))
                    error_count += 1
            _report(total, error_count)
            return 1 if error_count else 0

        if not rest:
            print("missing instance path")
            return 2
        instance_path = rest[0]
        instance = json.load(sys.stdin) if instance_path == "-" \
            else json.load(open(instance_path, encoding="utf-8"))
        errs = validate(instance, schema)
        for e in errs:
            print(e)
        _report(1, len(errs))
        return 1 if errs else 0
    except SchemaError as exc:
        print("schema error: %s" % exc)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
