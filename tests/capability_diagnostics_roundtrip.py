#!/usr/bin/env python3
"""EXT-03 checks for the manifest's explicit capability status projection."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools import capabilities_manifest as manifest


def fail(message):
    print("FAIL: " + message)
    sys.exit(1)


def main():
    rows = manifest.capability_diagnostics(
        (("demo", {"alpha": object(), "beta": object()}),),
        configured=("demo:alpha",), available=("demo:alpha",),
        disabled=("demo:beta",))
    if rows != [
            {"name": "alpha", "family": "demo", "registered": True,
             "configured": True, "available": True, "disabled": False},
            {"name": "beta", "family": "demo", "registered": True,
             "configured": False, "available": False, "disabled": True}]:
        fail("explicit states were not kept separate: %r" % rows)
    rows = manifest.capability_diagnostics((("demo", {"alpha": object()}),))
    if rows[0]["registered"] is not True or any(
            rows[0][key] is not None for key in
            ("configured", "available", "disabled")):
        fail("descriptor metadata inferred a non-registration state")
    print("ok: capability diagnostics")
    return 0


if __name__ == "__main__":
    sys.exit(main())
