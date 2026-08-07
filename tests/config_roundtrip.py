#!/usr/bin/env python3
"""DEL-04/DEL-05 coverage: the settings schema is complete, the numeric
bounds are exact, `itembank config` prints the contract the way `spec`
prints the format contract, and an invalid `config set` never touches
`itembank.json` on disk.

Drives the real CLI via subprocess against a temp `--base` directory, the
same way a learner or agent does, so nothing writes into the checkout and
every assertion is on exit code plus the dotted code in the captured
output -- never on the English prose after it.

Standard library only, runnable as `python tests/config_roundtrip.py`.
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
ITEMBANK = os.path.join(ROOT, "itembank.py")
SCHEMA_PATH = os.path.join(ROOT, "schemas", "settings.schema.json")
SETTINGS_ON_DISK = os.path.join(ROOT, "itembank.json")

sys.path.insert(0, ROOT)
from surfaces import settings                              # noqa: E402

CODES_SEEN = set()


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def fresh_base():
    """A temp directory holding a copy of the repository's own itembank.json,
    so every test starts from the real shipped defaults rather than a
    hand-typed fixture that could drift from the schema.
    """
    tmp = tempfile.mkdtemp()
    shutil.copyfile(SETTINGS_ON_DISK, os.path.join(tmp, "itembank.json"))
    return tmp


def run(args, base):
    return subprocess.run(
        [sys.executable, ITEMBANK, "config"] + list(args) + ["--base", base],
        capture_output=True, text=True, encoding="utf-8")


def settings_file(base):
    return os.path.join(base, "itembank.json")


def sha(base):
    return hashlib.sha256(open(settings_file(base), "rb").read()).hexdigest()


def code_in(text):
    """Return the one SETTINGS_CODES member present in `text`, recording it
    seen for the reachability check, or fail if none of them is.
    """
    for code in settings.SETTINGS_CODES:
        if code in text:
            CODES_SEEN.add(code)
            return code
    fail("no SETTINGS_CODES member found in: %r" % (text,))


def assert_rejected(base, args, expected_code):
    before = sha(base)
    r = run(args, base)
    if r.returncode == 0:
        fail("config %r exited 0, expected a rejection" % (args,))
    output = r.stdout + r.stderr
    code = code_in(output)
    if code != expected_code:
        fail("config %r reported %r, expected %r (output: %r)" %
             (args, code, expected_code, output))
    after = sha(base)
    if before != after:
        fail("config %r mutated itembank.json on a rejected set" % (args,))


# ---- Task 2: the schema is complete, the validator's bounds are exact ------

def test_schema_names_every_project_key():
    """PROJECT.md's six named settings plus the daemon's own group -- no
    fewer, no more, each with a default, a phase and a description.
    """
    schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
    keys = set(schema["properties"])
    expected = {"theme", "daily_cap", "selection_weights", "auditor_autonomy",
                "model_backend", "update_policy", "daemon"}
    if keys != expected:
        fail("schema properties %r do not equal the expected key set %r" % (keys, expected))
    for name, sub in schema["properties"].items():
        for annotation in ("default", "x-itembank-phase", "description"):
            if annotation not in sub:
                fail("%s is missing %r" % (name, annotation))


def test_boundary_values_exact():
    """minimum/maximum are inclusive; one step outside either is rejected
    with settings.out_of_range and the file is left untouched.
    """
    base = fresh_base()
    for value in ("1", "65535"):
        r = run(["set", "daemon.port", value], base)
        if r.returncode != 0:
            fail("daemon.port %s (a boundary value) was rejected: %s" % (value, r.stdout + r.stderr))
    assert_rejected(base, ["set", "daemon.port", "0"], "settings.out_of_range")
    assert_rejected(base, ["set", "daemon.port", "65536"], "settings.out_of_range")
    shutil.rmtree(base, ignore_errors=True)


# ---- Task 3: itembank config's three tiers ---------------------------------

def test_config_no_args_prints_table():
    base = fresh_base()
    r = run([], base)
    if r.returncode != 0:
        fail("itembank config exited %d: %s" % (r.returncode, r.stderr))
    for name in ("theme", "daily_cap", "selection_weights", "auditor_autonomy",
                 "model_backend", "update_policy", "daemon"):
        if name not in r.stdout:
            fail("config table is missing key %r" % name)
    if r.stdout.count("inert") < 5:
        fail("config table names fewer than 5 inert keys: %r" % r.stdout.count("inert"))
    for line in r.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("daemon") and "inert" in line:
            fail("daemon is marked inert, but this phase's own code reads it: %r" % line)
    shutil.rmtree(base, ignore_errors=True)


def test_config_schema_byte_identical():
    base = fresh_base()
    r = run(["schema"], base)
    if r.returncode != 0:
        fail("itembank config schema exited %d: %s" % (r.returncode, r.stderr))
    on_disk = open(SCHEMA_PATH, encoding="utf-8").read()
    if r.stdout != on_disk:
        fail("itembank config schema is not byte-identical to schemas/settings.schema.json")
    shutil.rmtree(base, ignore_errors=True)


def test_config_set_idempotent():
    base = fresh_base()
    r = run(["set", "daemon.port", "9000"], base)
    if r.returncode != 0:
        fail("first config set daemon.port 9000 failed: %s" % (r.stdout + r.stderr))
    data = json.load(open(settings_file(base), encoding="utf-8"))
    if data["daemon"]["port"] != 9000:
        fail("daemon.port did not read back as 9000: %r" % data["daemon"]["port"])
    h1 = sha(base)
    r2 = run(["set", "daemon.port", "9000"], base)
    if r2.returncode != 0:
        fail("second config set daemon.port 9000 failed: %s" % (r2.stdout + r2.stderr))
    h2 = sha(base)
    if h1 != h2:
        fail("repeating config set with the same value did not leave itembank.json "
             "byte-identical")
    shutil.rmtree(base, ignore_errors=True)


def test_config_set_type_errors():
    base = fresh_base()
    assert_rejected(base, ["set", "daemon.port", "abc"], "settings.invalid_type")
    assert_rejected(base, ["set", "daemon.port", "3.5"], "settings.invalid_type")
    # 3.5 must never be silently truncated to 3 on the rejection path.
    data = json.load(open(settings_file(base), encoding="utf-8"))
    if data["daemon"]["port"] == 3:
        fail("a rejected float was truncated and written as an integer")
    shutil.rmtree(base, ignore_errors=True)


def test_config_set_bool_stored_as_bool():
    base = fresh_base()
    r = run(["set", "daemon.lan", "true"], base)
    if r.returncode != 0:
        fail("config set daemon.lan true failed: %s" % (r.stdout + r.stderr))
    data = json.load(open(settings_file(base), encoding="utf-8"))
    if data["daemon"]["lan"] is not True:
        fail("daemon.lan did not store the JSON boolean true: %r" % (data["daemon"]["lan"],))
    shutil.rmtree(base, ignore_errors=True)


def test_config_set_invalid_value():
    base = fresh_base()
    assert_rejected(base, ["set", "theme", "neon"], "settings.invalid_value")
    shutil.rmtree(base, ignore_errors=True)


def test_config_set_unknown_key():
    base = fresh_base()
    assert_rejected(base, ["set", "nope", "1"], "settings.unknown_key")
    assert_rejected(base, ["set", "daemon.nope", "1"], "settings.unknown_key")
    shutil.rmtree(base, ignore_errors=True)


def test_config_set_missing_key():
    """Setting a whole nested object with one of its own required keys
    omitted is settings.missing_key -- the object schemas (daemon,
    selection_weights, model_backend) each declare `required` over their own
    properties, the same 'required is not a silent fallback' rule the
    top-level document uses.
    """
    base = fresh_base()
    partial = json.dumps({"port": 8000, "lan": False})
    assert_rejected(base, ["set", "daemon", partial], "settings.missing_key")
    shutil.rmtree(base, ignore_errors=True)


def test_config_malformed_file():
    base = fresh_base()
    open(settings_file(base), "w", encoding="utf-8").write("{not valid json")
    r = run([], base)
    if r.returncode == 0:
        fail("itembank config against a malformed itembank.json exited 0")
    code = code_in(r.stdout + r.stderr)
    if code != "settings.malformed_file":
        fail("malformed itembank.json reported %r, expected settings.malformed_file" % code)
    # no write: the file on disk is exactly what we wrote, untouched.
    if open(settings_file(base), encoding="utf-8").read() != "{not valid json":
        fail("a malformed itembank.json was rewritten instead of left alone")
    shutil.rmtree(base, ignore_errors=True)


def test_unknown_key_preserved():
    base = fresh_base()
    data = json.load(open(settings_file(base), encoding="utf-8"))
    data["legacy_extra_key"] = "preserve-me"
    json.dump(data, open(settings_file(base), "w", encoding="utf-8"), indent=2)

    r = run([], base)
    if r.returncode != 0:
        fail("itembank config against a file with an unknown key exited %d" % r.returncode)
    if "legacy_extra_key" not in r.stdout:
        fail("config's table does not report the unknown key")

    r = run(["set", "daemon.port", "9001"], base)
    if r.returncode != 0:
        fail("config set failed against a file carrying an unknown key: %s" %
             (r.stdout + r.stderr))
    after = json.load(open(settings_file(base), encoding="utf-8"))
    if after.get("legacy_extra_key") != "preserve-me":
        fail("the unknown key was dropped on the next write, not preserved")
    shutil.rmtree(base, ignore_errors=True)


def test_missing_schema_key_reads_as_default():
    """A schema key absent from itembank.json reads as its schema default
    rather than as missing (the planner_assumptions resolution)."""
    base = fresh_base()
    data = json.load(open(settings_file(base), encoding="utf-8"))
    del data["theme"]
    json.dump(data, open(settings_file(base), "w", encoding="utf-8"), indent=2)

    r = run([], base)
    if r.returncode != 0:
        fail("itembank config against a file missing a schema key exited %d: %s" %
             (r.returncode, r.stderr))
    if "'system'" not in r.stdout:
        fail("theme's missing value did not read back as its schema default 'system'")
    shutil.rmtree(base, ignore_errors=True)


# ---- structural: SETTINGS_CODES is sorted, deduped, and every code is ------
# reachable from at least one input this test itself supplies.

def test_settings_codes_declared():
    codes = settings.SETTINGS_CODES
    if list(codes) != sorted(codes):
        fail("SETTINGS_CODES is not sorted")
    if len(set(codes)) != len(codes):
        fail("SETTINGS_CODES has duplicates")
    for code in codes:
        if not code.startswith("settings."):
            fail("code %r is not in the settings.* namespace" % code)


def test_all_codes_reachable():
    missing = set(settings.SETTINGS_CODES) - CODES_SEEN
    if missing:
        fail("SETTINGS_CODES has codes no test input reaches: %r" % sorted(missing))


def main():
    test_schema_names_every_project_key()
    test_boundary_values_exact()
    test_config_no_args_prints_table()
    test_config_schema_byte_identical()
    test_config_set_idempotent()
    test_config_set_type_errors()
    test_config_set_bool_stored_as_bool()
    test_config_set_invalid_value()
    test_config_set_unknown_key()
    test_config_set_missing_key()
    test_config_malformed_file()
    test_unknown_key_preserved()
    test_missing_schema_key_reads_as_default()
    test_settings_codes_declared()
    # Reachability is checked last, after every other test has had a chance
    # to record the codes its own inputs triggered via assert_rejected/code_in.
    test_all_codes_reachable()
    print("config contract: ok (schema completeness, exact numeric bounds, "
          "config/schema/set's three tiers, idempotent writes, unknown-key "
          "preservation, missing-key-reads-as-default, all %d dotted codes "
          "reachable)" % len(settings.SETTINGS_CODES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
