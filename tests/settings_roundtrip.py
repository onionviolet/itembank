#!/usr/bin/env python3
"""Phase 20 settings migration, independence, and adapter contracts."""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from surfaces import home, looks, presentation, settings, theme


def fail(message):
    raise AssertionError(message)


def check_profile_migration_and_recovery():
    with tempfile.TemporaryDirectory() as root:
        old = {"home": "split", "look": "console", "theme": "dark",
               "accent": {"source": "#336699"},
               "accessibility": {"reduced_motion": "on",
                                 "high_contrast": "on"}}
        settings.write_settings(root, old)
        loaded = settings.load_settings(root)
        active, notice = settings.resolve_presentation_profile(loaded)
        if active != "field-guide" or notice is not None:
            fail("old settings did not migrate additively")
        before = open(settings.settings_path(root), "rb").read()
        theme.theme_page(loaded)
        if open(settings.settings_path(root), "rb").read() != before:
            fail("preview or migration wrote settings")
        old["presentation_profile"] = "renamed-profile"
        settings.write_settings(root, old)
        loaded = settings.load_settings(root)
        active, notice = settings.resolve_presentation_profile(loaded)
        if active != "field-guide" or "renamed-profile" not in (notice or ""):
            fail("renamed or removed profile did not recover visibly")
        page = theme.theme_page(loaded)
        if ('data-presentation-profile="field-guide"' not in page or
                "renamed-profile" not in page or "Showing Field Guide" not in page):
            fail("Settings did not render its active fallback profile and notice")


def check_axis_independence_and_shipped_values():
    if tuple(home.MODES) != ("shelf", "next-action", "agent", "split"):
        fail("the four shipped home modes changed")
    if tuple(looks.LOOK_IDS) != ("classic", "editorial", "neo", "cash",
                                "console", "soft", "contrast"):
        fail("the seven shipped looks changed")
    with tempfile.TemporaryDirectory() as root:
        cfg = settings.load_settings(root)
        cfg.update({"home": "agent", "look": "soft", "theme": "oled",
                    "density": "compact"})
        cfg["accent"]["source"] = "#445566"
        cfg["accessibility"].update({"reduced_motion": "on",
                                     "high_contrast": "on"})
        settings.write_settings(root, cfg)
        before = settings.load_settings(root)
        theme.persist_presentation_profile(root, "trajectory-deck")
        after = settings.load_settings(root)
        for axis in ("home", "look", "theme", "accent", "density",
                     "accessibility"):
            if after[axis] != before[axis]:
                fail("profile save changed independent axis %s" % axis)


def check_adapter_manifest_and_no_loader():
    manifest = presentation.surface_adapter_manifest()
    required = {"identity", "version", "roles", "operations", "modes",
                "input", "fallback", "unavailable", "migration", "tests",
                "removal_recovery", "disposition"}
    if manifest != presentation.surface_adapter_manifest():
        fail("adapter manifest export is not deterministic")
    if manifest["version"] != 1 or manifest["external_loader"] is not False:
        fail("adapter export version or EXT-05 boundary changed")
    identities = {row["identity"] for row in manifest["adapters"]}
    if identities != {"question-response", "course-areas", "settings",
                      "authoring-export-integrations"}:
        fail("learner-facing adapter coverage is incomplete: %r" % identities)
    for row in manifest["adapters"]:
        if required - set(row):
            fail("adapter %s lacks %r" % (row.get("identity"), required - set(row)))
    sources = "\n".join(open(os.path.join(ROOT, path), encoding="utf-8").read()
                         for path in ("surfaces/presentation.py", "surfaces/settings.py",
                                      "surfaces/theme.py", "surfaces/looks.py"))
    for token in ("importlib.import_module", "exec_module(",
                  "spec_from_file_location(", "watchdog", "hot_reload",
                  "live_reload"):
        if token in sources:
            fail("Phase 20 UI foundation contains prohibited EXT-05 behavior %r" % token)


def main():
    check_profile_migration_and_recovery()
    check_axis_independence_and_shipped_values()
    check_adapter_manifest_and_no_loader()
    print("all settings checks passed")


if __name__ == "__main__":
    main()
