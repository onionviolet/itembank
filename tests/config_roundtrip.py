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


def run_theme(args, base):
    return subprocess.run(
        [sys.executable, ITEMBANK, "theme"] + list(args) + ["--base", base],
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


def assert_rejected_theme(base, args, expected_code):
    before = sha(base)
    r = run_theme(args, base)
    if r.returncode == 0:
        fail("itembank theme %r exited 0, expected a rejection" % (args,))
    output = r.stdout + r.stderr
    code = code_in(output)
    if code != expected_code:
        fail("itembank theme %r reported %r, expected %r (output: %r)" %
             (args, code, expected_code, output))
    after = sha(base)
    if before != after:
        fail("itembank theme %r mutated itembank.json on a rejected action" % (args,))


# ---- Task 2: the schema is complete, the validator's bounds are exact ------

def test_schema_names_every_project_key():
    """PROJECT.md's named settings plus the daemon's own group plus the
    update group plus the Phase 4 accent group plus plan 08-02's
    suggestion_reveal -- each top-level key with a default, a phase and a
    description.
    """
    schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
    keys = set(schema["properties"])
    expected = {"theme", "daily_cap", "selection_weights", "selection",
                "auditor_autonomy", "model_backend", "suggestion_reveal",
                "update_policy", "daemon", "update", "accent", "reader",
                "teaching", "style", "paraphrase", "lti", "check",
                "subject_profiles", "retention", "audio",
                # plan 17A-08: the home shape key (shelf default).
                "home"}
    if keys != expected:
        fail("schema properties %r do not equal the expected key set %r" % (keys, expected))
    for name, sub in schema["properties"].items():
        for annotation in ("default", "x-itembank-phase", "description"):
            if annotation not in sub:
                fail("%s is missing %r" % (name, annotation))


def test_theme_schema_additive_accent():
    """The persisted contract is exactly the existing theme string plus one
    required top-level accent object whose only persisted field is the
    normalized opaque source, defaulting to #0e6e62 (04-UI-SPEC / 04-RESEARCH
    binding resolution of the additive-schema open question).
    """
    schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
    theme = schema["properties"]["theme"]
    if theme["enum"] != ["system", "light", "dark", "oled"] or theme["default"] != "system":
        fail("theme property changed; it must stay system|light|dark|oled default system")
    accent = schema["properties"].get("accent")
    if not accent:
        fail("schema has no top-level accent group")
    if accent.get("type") != "object" or accent.get("required") != ["source"]:
        fail("accent must be an object with required ['source']")
    if accent.get("additionalProperties") is not False:
        fail("accent must reject unknown keys")
    src = accent.get("properties", {}).get("source")
    if not src or src.get("default") != "#0e6e62":
        fail("accent.source default is not #0e6e62")
    if "accent" not in schema.get("required", []):
        fail("accent is not a top-level required key")


def test_accent_source_hex_pattern():
    """WR-03 regression: the schema itself enforces the exact six-digit hex
    pattern -- `config set accent.source` rejects a non-hex value with
    settings.invalid_value and never touches itembank.json, while valid hex
    values still pass.
    """
    import schema_validate
    schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
    src = schema["properties"]["accent"]["properties"]["source"]
    if src.get("pattern") != "^#[0-9a-fA-F]{6}$":
        fail("accent.source has no exact #RRGGBB pattern: %r"
             % src.get("pattern"))
    for value in ("#0e6e62", "#123abc", "#ABCDEF"):
        if schema_validate.validate(value, src):
            fail("valid hex accent.source %r failed the schema pattern" % value)
    for value in ("zzzzzzz", "#12345g", "1234567"):
        if not schema_validate.validate(value, src):
            fail("non-hex accent.source %r passed the schema pattern" % value)
    base = fresh_base()
    try:
        assert_rejected(base, ["set", "accent.source", "zzzzzzz"],
                        "settings.invalid_value")
        r = run(["set", "accent.source", "#123abc"], base)
        if r.returncode != 0:
            fail("a valid hex accent.source was rejected: %s"
                 % (r.stdout + r.stderr))
    finally:
        shutil.rmtree(base, ignore_errors=True)


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
    for name in ("theme", "daily_cap", "selection_weights", "selection",
                 "auditor_autonomy", "model_backend", "update_policy", "daemon",
                 "update", "retention"):
        if name not in r.stdout:
            fail("config table is missing key %r" % name)
    # At THIS_PHASE 10 only phase-11+ keys are inert: auditor_autonomy
    # (phase 11). daily_cap/model_backend/retention/selection_weights all
    # became read-by-this-phase; subject_profiles (phase 9) is read too.
    if "auditor_autonomy" not in r.stdout or "inert" not in r.stdout:
        fail("config table must still mark phase-11 auditor_autonomy inert")
    for line in r.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("daemon") and "inert" in line:
            fail("daemon is marked inert, but this phase's own code reads it: %r" % line)
    shutil.rmtree(base, ignore_errors=True)


def test_phase_10_keys_read_not_inert():
    """Phase 10 reads the retention group, daily_cap, model_backend and the
    two Phase 10 selection weights, so their table rows may not say 'inert';
    only phase-11+ keys stay inert."""
    base = fresh_base()
    r = run([], base)
    if r.returncode != 0:
        fail("itembank config exited %d: %s" % (r.returncode, r.stderr))
    read_by_this_phase = ("selection", "selection.cooldown_responses",
                          "selection_weights.recency_decay",
                          "selection_weights.objective_miss_rate",
                          "selection_weights.difficulty_spread",
                          "daily_cap", "model_backend", "retention",
                          "retention.review_interval_days",
                          "retention.at_risk_after_days",
                          "retention.focused_session_count")
    inert_by_later_phase = ("auditor_autonomy",)
    for line in r.stdout.splitlines():
        stripped = line.strip()
        first_token = stripped.split()[0] if stripped.split() else ""
        if first_token in read_by_this_phase and "inert" in line:
            fail("%r is marked inert, but this phase reads it: %r" %
                 (first_token, line))
        if first_token in inert_by_later_phase and "inert" not in line:
            fail("%r must be inert until Phase 11: %r" %
                 (first_token, line))
    shutil.rmtree(base, ignore_errors=True)


def test_phase_2_1_keys_read_not_inert():
    """RESEARCH Pitfall 8: update_policy, daemon.window, update.repo and
    update.check_interval_hours are read by this phase (2.1), so none of
    their table rows may say 'inert' -- the exact bug that motivated D-10.
    """
    base = fresh_base()
    r = run([], base)
    if r.returncode != 0:
        fail("itembank config exited %d: %s" % (r.returncode, r.stderr))
    read_by_this_phase = ("update_policy", "daemon.window", "update.repo",
                          "update.check_interval_hours")
    for line in r.stdout.splitlines():
        stripped = line.strip()
        first_token = stripped.split()[0] if stripped.split() else ""
        if first_token in read_by_this_phase and "inert" in line:
            fail("%r is marked inert, but this phase's own code reads it: %r" %
                 (first_token, line))
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


# ---- plan 04-03 Task 2: additive source-only accent persistence ------------

def test_old_file_missing_accent_loads_with_default():
    """A pre-Phase-4 settings file (no accent key at all) remains loadable:
    settings loading merges schema defaults before validation, so the source
    reads back as #0e6e62 rather than absent.
    """
    base = fresh_base()
    data = json.load(open(settings_file(base), encoding="utf-8"))
    data.pop("accent", None)
    json.dump(data, open(settings_file(base), "w", encoding="utf-8"), indent=2)
    r = run([], base)
    if r.returncode != 0:
        fail("an old settings file missing accent no longer loads: %s" %
             (r.stdout + r.stderr))
    if "#0e6e62" not in r.stdout:
        fail("accent.source did not read back as the schema default #0e6e62")
    shutil.rmtree(base, ignore_errors=True)


def test_theme_set_persists_only_source():
    """`itembank theme set` persists exactly one normalized source; unknown
    top-level user keys survive the write; no derived pair, ratio, correction
    notice, or per-mode override ever lands in itembank.json (D-05).
    """
    base = fresh_base()
    data = json.load(open(settings_file(base), encoding="utf-8"))
    data["legacy_extra_key"] = "preserve-me"
    json.dump(data, open(settings_file(base), "w", encoding="utf-8"), indent=2)

    r = run_theme(["set", "#123ABC"], base)
    if r.returncode != 0:
        fail("theme set failed: %s" % (r.stdout + r.stderr))
    after = json.load(open(settings_file(base), encoding="utf-8"))
    if after.get("accent") != {"source": "#123abc"}:
        fail("theme set persisted %r; expected exactly {'source': '#123abc'}"
             % after.get("accent"))
    if after.get("legacy_extra_key") != "preserve-me":
        fail("theme set dropped an unknown top-level user key")
    shutil.rmtree(base, ignore_errors=True)


def test_theme_set_reset_contract():
    base = fresh_base()
    r = run_theme(["set", "#c00040"], base)
    if r.returncode != 0:
        fail("theme set #c00040 failed: %s" % (r.stdout + r.stderr))
    data = json.load(open(settings_file(base), encoding="utf-8"))
    if data["accent"]["source"] != "#c00040":
        fail("theme set did not persist the normalized source: %r" %
             data["accent"])
    h1 = sha(base)
    r2 = run_theme(["set", "#c00040"], base)
    if r2.returncode != 0:
        fail("repeated theme set failed: %s" % (r2.stdout + r2.stderr))
    if sha(base) != h1:
        fail("repeating theme set with the same source is not byte-idempotent")

    r3 = run_theme(["reset", "--confirm-reset", "RESET"], base)
    if r3.returncode != 0:
        fail("theme reset with confirmation failed: %s" % (r3.stdout + r3.stderr))
    data = json.load(open(settings_file(base), encoding="utf-8"))
    if data["accent"]["source"] != "#0e6e62":
        fail("theme reset did not restore the schema default #0e6e62")

    before = sha(base)
    r4 = run_theme(["reset"], base)
    if r4.returncode == 0:
        fail("theme reset without confirmation exited 0")
    r5 = run_theme(["reset", "--confirm-reset", "WRONG"], base)
    if r5.returncode == 0:
        fail("theme reset with a wrong confirmation exited 0")
    if sha(base) != before:
        fail("theme reset with absent/wrong confirmation wrote itembank.json")
    shutil.rmtree(base, ignore_errors=True)


def test_theme_set_invalid_colors_rejected():
    base = fresh_base()
    for bad in ("notacolor", "#12345", "#12345g", "#gggggg"):
        assert_rejected_theme(base, ["set", bad], "settings.invalid_value")
    data = json.load(open(settings_file(base), encoding="utf-8"))
    if data.get("accent", {}).get("source") not in (None, "#0e6e62"):
        fail("a rejected color still mutated accent.source")
    shutil.rmtree(base, ignore_errors=True)


def test_theme_preview_readonly_reports_tokens():
    base = fresh_base()
    r = run_theme(["preview", "#0e6e62"], base)
    if r.returncode != 0:
        fail("theme preview exited %d: %s" % (r.returncode, r.stdout + r.stderr))
    for needle in ("#0e6e62", "light", "dark", "accent", "ratio"):
        if needle not in r.stdout:
            fail("theme preview is missing %r: %r" % (needle, r.stdout))
    before = sha(base)
    adj = run_theme(["preview", "#ffff00"], base)
    if adj.returncode != 0:
        fail("adjusted theme preview exited %d: %s"
             % (adj.returncode, adj.stdout + adj.stderr))
    if "Adjusted for readable contrast" not in adj.stdout:
        fail("adjusted theme preview carries no correction notice")
    if sha(base) != before:
        fail("theme preview wrote itembank.json")
    shutil.rmtree(base, ignore_errors=True)


def test_phase_4_theme_keys_read_not_inert():
    """Phase 4's own theme/accent settings read as active through `itembank
    config`, while later-phase groups (daily_cap, selection_weights,
    auditor_autonomy, model_backend) keep their inert labeling -- the
    discovery contract the settings UI relies on.
    """
    base = fresh_base()
    r = run([], base)
    if r.returncode != 0:
        fail("itembank config exited %d: %s" % (r.returncode, r.stderr))
    rows = []
    for line in r.stdout.splitlines():
        stripped = line.strip()
        if stripped.split():
            rows.append((stripped.split()[0], stripped))
    active = ("theme", "accent.source")
    for token, line in rows:
        if token in active and "inert" in line:
            fail("%r is marked inert, but Phase 4's own code reads it: %r"
                 % (token, line))
    # selection_weights left the inert list when phase 7 started reading
    # its recency_decay key (D-15); the group row is active at THIS_PHASE 7.
    # At THIS_PHASE 10, daily_cap and model_backend are also read; only
    # phase-11+ keys (auditor_autonomy) stay inert.
    inert_groups = ("auditor_autonomy",)
    for group in inert_groups:
        if not any(token == group and "inert" in line for token, line in rows):
            fail("%r is no longer marked inert" % group)
    for group in ("model_backend", "suggestion_reveal"):
        if any(token == group and "inert" in line for token, line in rows):
            fail("%r must be read (active) by THIS_PHASE 9: %r"
                 % (group, [line for token, line in rows if token == group]))
    shutil.rmtree(base, ignore_errors=True)


# ---- structural: SETTINGS_CODES is sorted, deduped, and every code is ------
# reachable from at least one input this test itself supplies.

def test_check_group_contract():
    """The four check keys are typed, bounded, defaulted in the schema and in
    the shipped itembank.json,  accepts valid values and rejects
    out-of-range/unknown/wrong-typed ones, and a file with no check key reads
    back with every check default present (plan 05-03 Task 1)."""
    schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
    c = schema["properties"]["check"]
    if c.get("x-itembank-phase") != 5:
        fail("check group x-itembank-phase is %r, expected 5" % c.get("x-itembank-phase"))
    if c.get("additionalProperties") is not False:
        fail("check group must reject unknown keys")
    if sorted(c.get("required", [])) != ["allow_lan", "languages",
                                         "max_output_bytes", "timeout_seconds"]:
        fail("check required list is %r" % c.get("required"))
    if c["properties"]["timeout_seconds"]["default"] != 5:
        fail("timeout_seconds default is not 5")
    if c["properties"]["max_output_bytes"]["default"] != 65536:
        fail("max_output_bytes default is not 65536")
    if c["properties"]["allow_lan"]["default"] is not False:
        fail("allow_lan default is not false")
    langs = c["properties"]["languages"]["default"]
    if not isinstance(langs, dict) or "python" not in langs:
        fail("check.languages default is %r, expected a map carrying python" % langs)
    if "check" not in schema.get("required", []):
        fail("check is not a top-level required key")

    # The shipped itembank.json agrees with the schema's computed defaults.
    shipped = json.load(open(SETTINGS_ON_DISK, encoding="utf-8"))
    if shipped.get("check") != c.get("default"):
        fail("shipped itembank.json check group %r disagrees with schema "
             "defaults %r" % (shipped.get("check"), c.get("default")))

    base = fresh_base()
    try:
        for args in (["set", "check.timeout_seconds", "30"],
                     ["set", "check.max_output_bytes", "1024"],
                     ["set", "check.allow_lan", "true"]):
            r = run(args, base)
            if r.returncode != 0:
                fail("config %r failed: %s" % (args, r.stdout + r.stderr))
        data = json.load(open(settings_file(base), encoding="utf-8"))
        ck = data["check"]
        if ck["timeout_seconds"] != 30 or ck["max_output_bytes"] != 1024                 or ck["allow_lan"] is not True:
            fail("check values did not read back: %r" % ck)
        assert_rejected(base, ["set", "check.timeout_seconds", "0"], "settings.out_of_range")
        assert_rejected(base, ["set", "check.timeout_seconds", "601"], "settings.out_of_range")
        assert_rejected(base, ["set", "check.max_output_bytes", "0"], "settings.out_of_range")
        assert_rejected(base, ["set", "check.allow_lan", '"yes"'], "settings.invalid_type")
        assert_rejected(base, ["set", "check.nope", "1"], "settings.unknown_key")

        # A file with no check key at all reads back with every default present.
        nodata = json.load(open(settings_file(base), encoding="utf-8"))
        nodata.pop("check", None)
        json.dump(nodata, open(settings_file(base), "w", encoding="utf-8"), indent=2)
        loaded = settings.load_settings(base)
        if set(loaded["check"]) != {"timeout_seconds", "max_output_bytes",
                                    "languages", "allow_lan"}:
            fail("a file with no check key did not read back all four defaults: %r"
                 % loaded["check"])
        if "python" not in loaded["check"]["languages"]:
            fail("check.languages default does not carry python")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_teaching_group_contract():
    """The two Phase 13.5 teaching keys are enumerated, defaulted and required
    in the schema; `itembank config` prints both rows; an out-of-enum value is
    refused by the existing settings.invalid_value code; and a settings file
    with no `teaching` object at all loads both defaults rather than raising
    (plan 14-03 Task 1).

    The names are the inherited 06-UI-SPEC interface restated in 14-UI-SPEC
    section 16, not invented here -- which is what makes a published settings
    key safe to ship without a migration.
    """
    schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
    t = schema["properties"]["teaching"]
    # 13.5, not 14: this phase was planned as 14 on 2026-08-12 and renumbered on
    # 2026-08-13 when the source-to-course reframe took that number for Course
    # Workspace & Source Binding. A decimal is the existing convention here --
    # `update_policy` already carries 2.1.
    if t.get("x-itembank-phase") != 13.5:
        fail("teaching group x-itembank-phase is %r, expected 13.5"
             % t.get("x-itembank-phase"))
    if t.get("additionalProperties") is not False:
        fail("teaching group must reject unknown keys")
    if sorted(t.get("required", [])) != ["hint_display", "hint_locked_preview"]:
        fail("teaching required list is %r" % t.get("required"))
    if "teaching" not in schema.get("required", []):
        fail("teaching is not a top-level required key")
    if t["properties"]["hint_display"]["enum"] != ["rail", "slot"]:
        fail("hint_display enum is %r, expected rail|slot"
             % t["properties"]["hint_display"]["enum"])
    if t["properties"]["hint_display"]["default"] != "slot":
        fail("hint_display default is not slot (14-UI-SPEC section 9.2)")
    if t["properties"]["hint_locked_preview"]["enum"] != ["full", "next"]:
        fail("hint_locked_preview enum is %r, expected full|next"
             % t["properties"]["hint_locked_preview"]["enum"])
    if t["properties"]["hint_locked_preview"]["default"] != "full":
        fail("hint_locked_preview default is not full")
    if t.get("default") != {"hint_display": "slot",
                            "hint_locked_preview": "full"}:
        fail("the teaching group's whole-object default is %r" % t.get("default"))
    # The module accessor and the schema agree: one set of numbers, not two.
    if settings.teaching_defaults() != t.get("default"):
        fail("settings.teaching_defaults() %r disagrees with the schema's "
             "group default %r" % (settings.teaching_defaults(), t.get("default")))

    base = fresh_base()
    try:
        r = run([], base)
        if r.returncode != 0:
            fail("itembank config exited %d after the teaching group landed: %s"
                 % (r.returncode, r.stdout + r.stderr))
        for row in ("teaching.hint_display", "teaching.hint_locked_preview"):
            if row not in r.stdout:
                fail("itembank config does not print the %s row" % row)

        for args in (["set", "teaching.hint_display", "rail"],
                     ["set", "teaching.hint_locked_preview", "next"]):
            r = run(args, base)
            if r.returncode != 0:
                fail("config %r failed: %s" % (args, r.stdout + r.stderr))
        data = json.load(open(settings_file(base), encoding="utf-8"))
        if data["teaching"] != {"hint_display": "rail",
                                "hint_locked_preview": "next"}:
            fail("teaching values did not read back: %r" % data.get("teaching"))

        # Out of enum, wrong type and unknown nested key all go through the
        # one existing validator and its one existing code namespace.
        assert_rejected(base, ["set", "teaching.hint_display", "column"],
                        "settings.invalid_value")
        assert_rejected(base, ["set", "teaching.hint_locked_preview", "all"],
                        "settings.invalid_value")
        assert_rejected(base, ["set", "teaching.hint_display", "3"],
                        "settings.invalid_type")
        assert_rejected(base, ["set", "teaching.nope", '"x"'],
                        "settings.unknown_key")

        # A file with no teaching object at all reads back both defaults.
        nodata = json.load(open(settings_file(base), encoding="utf-8"))
        nodata.pop("teaching", None)
        json.dump(nodata, open(settings_file(base), "w", encoding="utf-8"),
                  indent=2)
        loaded = settings.load_settings(base)
        if loaded["teaching"] != {"hint_display": "slot",
                                  "hint_locked_preview": "full"}:
            fail("a file with no teaching object did not read back both "
                 "schema defaults: %r" % loaded.get("teaching"))
    finally:
        shutil.rmtree(base, ignore_errors=True)


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
    test_theme_schema_additive_accent()
    test_accent_source_hex_pattern()
    test_boundary_values_exact()
    test_config_no_args_prints_table()
    test_phase_2_1_keys_read_not_inert()
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
    test_old_file_missing_accent_loads_with_default()
    test_theme_set_persists_only_source()
    test_theme_set_reset_contract()
    test_theme_set_invalid_colors_rejected()
    test_theme_preview_readonly_reports_tokens()
    test_phase_4_theme_keys_read_not_inert()
    test_check_group_contract()
    test_teaching_group_contract()
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
