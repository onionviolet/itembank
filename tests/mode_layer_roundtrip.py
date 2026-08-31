#!/usr/bin/env python3
"""Assert that the mode-layer precedence contract is one rule, that a lower
layer never beats a higher one, and that the two fixed layers are rendered as
text a learner can read rather than as a control that cannot take effect.

The failure this guards against is an affordance that lies: a toggle for
something the runtime decides looks like a choice, and a learner who flips it
and sees no change has been told something false about who is in charge. The
second failure is a second precedence implementation, which is why the
collector that reads live state is Phase 16C's and is asserted absent here.

`mode_layer_resolve` is the pure half: it reads only its arguments. The
collector that populates its `requests` mapping from live strategy,
accommodation, and instructor records is Phase 16C's under D8 and D-16B-12.

Standard library only, no test framework, runnable as
`python tests/mode_layer_roundtrip.py`.
"""
import hashlib, inspect, io, os, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                             # noqa: E402
from surfaces import daemon, ia, settings, theme            # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from daemon_roundtrip import start_daemon, get              # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")

# Taken 2026-08-28, before plan 16B-07 added theme_page's `sections` argument,
# with:
#   python3 -c "import sys,hashlib; sys.path.insert(0,'.');
#     from surfaces import theme, settings;
#     print(hashlib.sha256(theme.theme_page(
#       settings.load_settings('.')).encode('utf-8')).hexdigest())"
# If this value changes for an unrelated reason, the test names the drift
# instead of hiding it.
# Re-taken 2026-08-31 with the same command, after plan 17A-04's driven
# browser measured the shared `details summary` disclosure at 32px and
# SHARED_CSS gave both summary rules min-height:44px (the button.go
# precedent). theme_page embeds SHARED_CSS through surface_shell, so its
# bytes moved with it. The pre-change value was
# f198e3d7d15f7033d0fa028df13c3d7449eadce5ae77a0220dc43114925f799b.
THEME_PAGE_BASELINE = \
    "8f9678185b188b63a04df95302c2d0823efc0f33c1901d7853a87c3fc866ece9"

# Phase 16C appends rows here rather than creating a second fixture. Each row
# is (setting_name, requests, expected_winning_layer, expected_value).
CONFLICT_CASES = [
    ("Timed test mode",
     {"learner_preference": "off", "instructor_policy": "on"},
     "instructor_policy", "on"),
    ("Reader view",
     {"learner_preference": "guided", "author_strategy": "continuous"},
     "author_strategy", "continuous"),
    ("Retry after a wrong answer",
     {"learner_preference": "unlimited", "runtime_authority": "one"},
     "runtime_authority", "one"),
    ("Reduced motion",
     {"learner_preference": "off", "accommodation_override": "on"},
     "accommodation_override", "on"),
    ("Show the answer key now",
     {"learner_preference": "yes", "instructor_policy": "yes",
      "runtime_authority": "no"},
     "runtime_authority", "no"),
    ("Read outside the approved roots",
     {"learner_preference": "yes", "system_safety": "no"},
     "system_safety", "no"),
    # Phase 16C strategy rows (plan 16C-05): STRATEGY-02 conflict matrix.
    ("Learning strategy",
     {"learner_preference": "retrieval_first",
      "accommodation_override": "continuous_reading"},
     "accommodation_override", "continuous_reading"),
    ("Learning strategy",
     {"learner_preference": "retrieval_first",
      "instructor_policy": "guided_note_spine"},
     "instructor_policy", "guided_note_spine"),
    ("Change strategy during a test sitting",
     {"learner_preference": "guided_note_spine",
      "runtime_authority": "locked"},
     "runtime_authority", "locked"),
]

# The three cases above in which a learner preference loses to a layer the
# runtime fixes. Non-negotiable number 1 is what each of them protects.
AUTHORITY_CASES = (2, 4, 5)


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def temp_dir_with_bank():
    workdir = tempfile.mkdtemp(prefix="mode_layer_")
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    return workdir


def check_layer_table_shape():
    """Seven layers, in one order, with exactly the last two fixed."""
    rows = ia.MODE_LAYER_ROWS
    if len(rows) != 7:
        fail("MODE_LAYER_ROWS has %d rows, expected 7" % len(rows))
    if [r["layer"] for r in rows] != list(ia.MODE_LAYERS):
        fail("MODE_LAYER_ROWS is not in MODE_LAYERS order")
    fixed = [i for i, r in enumerate(rows) if r["fixed"]]
    if fixed != [5, 6]:
        fail("the fixed rows are at %r, expected the final two" % fixed)
    if {rows[i]["layer"] for i in fixed} != set(ia.MODE_LAYERS_FIXED):
        fail("the fixed rows are not MODE_LAYERS_FIXED")

    labels = []
    for row in rows:
        for field in ("label", "controller", "example"):
            if not isinstance(row[field], str) or not row[field].strip():
                fail("%s carried an empty %s" % (row["layer"], field))
        labels.append(row["label"])
    if len(set(labels)) != len(labels):
        fail("two mode layers share a label: %r" % labels)

    returned = ia.mode_layer_rows()
    returned[0]["label"] = "mutated"
    if ia.MODE_LAYER_ROWS[0]["label"] == "mutated":
        fail("mode_layer_rows() exposed the module constant for mutation")


def check_instructor_beats_preference():
    """The worked example, the no-conflict case, and the empty case."""
    result = ia.mode_layer_resolve(
        "Timed test mode",
        {"learner_preference": "off", "instructor_policy": "on"})
    if result["value"] != "on" or result["winning_layer"] != "instructor_policy":
        fail("instructor policy did not win: %r" % result)
    if result["conflict"] is not True:
        fail("a contradicted preference did not report a conflict")
    expected = ia.mode_layer_conflict_copy("Timed test mode",
                                           "instructor_policy")
    if result["copy"] != expected:
        fail("the conflict copy was %r" % result["copy"])

    quiet = ia.mode_layer_resolve("Reader view",
                                  {"learner_preference": "guided"})
    if quiet["conflict"] is not False or quiet["copy"] != "":
        fail("a single request reported a conflict: %r" % quiet)
    if quiet["winning_layer"] != "learner_preference":
        fail("a single request did not win its own value: %r" % quiet)

    try:
        empty = ia.mode_layer_resolve("Anything", {})
    except Exception as exc:
        fail("an empty request mapping raised %s" % exc)
    if empty != {"value": None, "winning_layer": None, "conflict": False,
                 "copy": ""}:
        fail("the empty case returned %r" % empty)

    try:
        ia.mode_layer_resolve("x", {"not_a_layer": 1})
    except ValueError as exc:
        if "not_a_layer" not in str(exc):
            fail("the unknown-layer error did not name the layer: %s" % exc)
    else:
        fail("an unknown mode layer was silently ignored")


def check_fixed_layers_always_win():
    """Every ordered pair of distinct layers resolves to the higher one."""
    layers = list(ia.MODE_LAYERS)
    pairs = 0
    for i, lower in enumerate(layers):
        for higher in layers[i + 1:]:
            pairs += 1
            result = ia.mode_layer_resolve(
                "Setting", {lower: "lower-value", higher: "higher-value"})
            if result["winning_layer"] != higher:
                fail("%s did not beat %s" % (higher, lower))
            if result["value"] != "higher-value":
                fail("%s over %s produced %r" % (higher, lower, result))
            if result["conflict"] is not True:
                fail("%s over %s reported no conflict" % (higher, lower))
            if higher in ia.MODE_LAYERS_FIXED and result["value"] != "higher-value":
                fail("a fixed layer lost to %s, breaking non-negotiable "
                     "number 1: the runtime owns correctness, session state, "
                     "evidence, and keyed disclosure" % lower)
    if pairs != 21:
        fail("checked %d ordered pairs, expected 21" % pairs)


def check_fixed_rows_are_read_only():
    """The settings page shows all seven layers and offers no control for the
    two it cannot honour."""
    workdir = temp_dir_with_bank()
    proc = None
    try:
        proc, url, lines = start_daemon(workdir)
        status, body = get(url + "settings")
        if status != 200:
            fail("GET /settings returned %d" % status)
        if ia.MODE_LAYER_FIXED_HEADING not in body:
            fail("the settings page lost the fixed-layer heading")
        for row in ia.MODE_LAYER_ROWS:
            if row["label"] not in body:
                fail("the settings page omitted the layer %r" % row["label"])
            if row["controller"] not in body:
                fail("the settings page omitted %r's controller"
                     % row["label"])
        if 'data-section="theme"' not in body:
            fail("the shipped Theme section is gone from /settings")

        start = body.find('data-mode-layers="read-only"')
        if start < 0:
            fail("the mode-layer disclosure carried no stable data hook")
        end = body.find("</details>", start)
        region = body[start:end]
        for banned in ("<input", "<select", "<button", "<textarea",
                       "contenteditable", "<form"):
            if banned in region:
                fail("the read-only mode-layer region carried %r, which is an "
                     "affordance that cannot take effect" % banned)
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)


def check_theme_page_unchanged_by_default():
    """theme_page with no sections argument is byte-identical to before."""
    page = theme.theme_page(settings.load_settings(ROOT))
    digest = hashlib.sha256(page.encode("utf-8")).hexdigest()
    if digest != THEME_PAGE_BASELINE:
        fail("theme_page(cfg) with no sections argument changed: %s, "
             "baseline %s" % (digest, THEME_PAGE_BASELINE))


def check_conflict_fixture():
    """One conflict per interesting pair, each with the exact locked
    sentence, and a learner preference never beating a fixed layer."""
    for index, (setting, requests, winner, value) in enumerate(CONFLICT_CASES):
        result = ia.mode_layer_resolve(setting, requests)
        if result["winning_layer"] != winner:
            fail("case %d (%s) resolved to %r, expected %r"
                 % (index, setting, result["winning_layer"], winner))
        if result["value"] != value:
            fail("case %d (%s) produced value %r, expected %r"
                 % (index, setting, result["value"], value))
        if result["conflict"] is not True:
            fail("case %d (%s) reported no conflict" % (index, setting))

        expected = ia.mode_layer_conflict_copy(setting, winner)
        if result["copy"] != expected:
            fail("case %d (%s) copy was %r, expected %r"
                 % (index, setting, result["copy"], expected))
        if setting not in result["copy"]:
            fail("case %d's copy did not name the setting" % index)
        if ia.MODE_LAYER_DISPLAY_PHRASES[winner] not in result["copy"]:
            fail("case %d's copy did not name the winning layer's phrase"
                 % index)
        if winner in result["copy"] or "_" in result["copy"]:
            fail("case %d's copy leaked an internal layer key: %r"
                 % (index, result["copy"]))

        if index in AUTHORITY_CASES:
            if winner not in ia.MODE_LAYERS_FIXED:
                fail("case %d was recorded as an authority case but %r is not "
                     "a fixed layer" % (index, winner))
            if requests.get("learner_preference") == result["value"]:
                fail("case %d let a learner preference decide a layer the "
                     "runtime fixes, breaking non-negotiable number 1: the "
                     "runtime owns correctness, session state, evidence, and "
                     "keyed assessment disclosure" % index)

    # D8 and D-16B-12: the collector that reads live state is Phase 16C's. A
    # collector appearing in 16B would mean this phase built 16C's half.
    for banned in ("collect_mode_layers", "live_mode_state",
                   "mode_layer_state"):
        if hasattr(ia, banned):
            fail("surfaces/ia.py defines %r; the collector that populates the "
                 "mode-layer mapping from live state is Phase 16C's under D8"
                 % banned)

    source = inspect.getsource(ia.mode_layer_resolve)
    for banned in ("import ", "open("):
        if banned in source:
            fail("mode_layer_resolve reads more than its arguments: %r found"
                 % banned)


CHECKS = (check_layer_table_shape,
          check_instructor_beats_preference,
          check_fixed_layers_always_win,
          check_fixed_rows_are_read_only,
          check_theme_page_unchanged_by_default,
          check_conflict_fixture)


def main():
    for check in CHECKS:
        check()
    print("MODE LAYERS: %d passed, 0 failed" % len(CHECKS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
