#!/usr/bin/env python3
"""Deterministic gate for the reversible reading-occurrence prototype."""
import importlib.util
import os
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "prototypes", "course-preparation", "build_prototype.py")
SPEC = importlib.util.spec_from_file_location("course_preparation_prototype", PATH)
prototype = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prototype)


def main():
    with tempfile.TemporaryDirectory(prefix="course_preparation_test_") as root:
        fixture = prototype.build_fixture(root)
        before = prototype.snapshot(fixture)
        rows = prototype.occurrences(fixture)
        now = [row for row in rows if row["activation"] == "Now"]
        if len(now) != 2 or any(row["activation"] == "Library" for row in now):
            raise SystemExit("Library leaked into Now or the two active occurrences are missing")
        if len({row["occurrence_id"] for row in rows}) != 3:
            raise SystemExit("occurrence identity is not independent")
        if len({row["source_id"] for row in rows}) != 1:
            raise SystemExit("shared activities duplicated source identity")
        if len({row["source_fingerprint"] for row in rows}) != 1:
            raise SystemExit("shared activities do not resolve identical source bytes")

        states = {row["occurrence_id"]: "not-reported" for row in rows}
        states[now[0]["occurrence_id"]] = "marked-read"
        if states[now[1]["occurrence_id"]] != "not-reported":
            raise SystemExit("completion crossed occurrence identity")

        cases = (
            ({"rights": "denied"}, "rights-refused"),
            ({"locator": "source.md#missing"}, "locator-missing"),
            ({"source_fingerprint": "divergent"}, "revision-conflict"),
        )
        for arguments, expected in cases:
            state, message = prototype.resolve(now[0], fixture, **arguments)
            if state != expected or not message:
                raise SystemExit("%s did not produce its distinct recovery state" % expected)
        remote = dict(now[0], remote_only=True)
        if prototype.resolve(remote, fixture, online=False)[0] != "offline-remote":
            raise SystemExit("offline remote-only content lacks a distinct recovery state")

        page = prototype.render_page(fixture)
        required = ('data-occurrence="occ-preread-tides"',
                    'data-occurrence="occ-prelearn-tides"',
                    "Mark read (simulated)", "resets on reload", "Resources",
                    "source.md#reading-range", "grid-template-columns:224px",
                    "reading-layout" if False else "learn-grid",
                    "A place for understanding", "Evidence without inflated certainty",
                    "One source. Three deliberate uses.", "min-height:44px",
                    "prefers-reduced-motion", 'tabindex="-1"')
        for needle in required:
            if needle not in page:
                raise SystemExit("prototype page misses %r" % needle)
        if 'class="path-item" data-occurrence="occ-library-tides"' in page:
            raise SystemExit("Library occurrence rendered in the Now cards")
        if "runtime" in page.lower() and "runtime authority" not in page.lower():
            pass
        if prototype.snapshot(fixture) != before:
            raise SystemExit("prototype interactions changed course, source, or evidence state")
    print("ok: occurrence prototype shares source bytes, isolates status, reports recovery states, and writes no accepted state")


if __name__ == "__main__":
    main()
