#!/usr/bin/env python3
"""Plan 17A-01 contract tests: one semantic flow, three reversible directions.

VISUAL-01 says the three directions project the same semantic flow rather than
three products, so the load-bearing assertion here is a fingerprint of the
semantic body markup with every direction hook stripped. If two directions
disagree on that fingerprint, one of them forked the markup and the direction
comparison is measuring two variables instead of one.

VISUAL-02 splits configurable tokens from fixed rules. The abuse cases below
push density, measure, and accent past their safe range and assert the clamp,
because a token that does not clamp is a fixed rule pretending to be a token.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "surfaces"))

FIXTURE = os.path.join(ROOT, "fixtures", "visual_system_flow.json")

REQUIRED_STAGES = ["shelf_resume", "source_linked_objective", "long_lesson",
                   "wrong_answer_retry", "evidence_review", "ai_proposed_change",
                   "agent_offline_status"]
REQUIRED_FORMS = ["definition", "warning", "table", "cited_image",
                  "inline_prediction", "inline_check"]
DIRECTIONS = ["structured-studio", "quiet-workbench", "guided-canvas"]

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL: " + msg)


def ok(msg):
    print("OK   " + msg)


def load():
    with open(FIXTURE, encoding="utf-8") as fh:
        return json.load(fh)


def check_fixture_shape():
    data = load()
    if not data.get("synthetic"):
        fail("fixture does not declare itself synthetic")
    ids = [s["id"] for s in data["stages"]]
    for stage in REQUIRED_STAGES:
        if stage not in ids:
            fail("fixture is missing required stage %s" % stage)
    lesson = [s for s in data["stages"] if s["id"] == "long_lesson"][0]
    forms = [b["form"] for b in lesson["blocks"]]
    for form in REQUIRED_FORMS:
        if form not in forms:
            fail("long_lesson is missing content form %s" % form)
    ok("check_fixture_shape")


def check_no_em_dash():
    raw = open(FIXTURE, encoding="utf-8").read()
    if "—" in raw:
        fail("fixture prose contains an em dash")
    ok("check_no_em_dash")


def check_no_keyed_leak():
    """The inline check is not released, so no key may exist in the fixture or
    in any rendered direction. A locked hint tier is absent from the DOM, never
    merely collapsed."""
    from surfaces import visual_fixture
    data = load()
    raw = open(FIXTURE, encoding="utf-8").read()
    lesson = [s for s in data["stages"] if s["id"] == "long_lesson"][0]
    check = [b for b in lesson["blocks"] if b["form"] == "inline_check"][0]
    if check.get("released"):
        fail("fixture inline_check is released, so this test proves nothing")
    for field in ("correct_option", "answer_key", "correct_index"):
        if field in raw:
            fail("fixture carries a key field %s" % field)
    practice = [s for s in data["stages"] if s["id"] == "wrong_answer_retry"][0]
    locked = [t for t in practice["hint_tiers"] if not t.get("released")]
    for direction in DIRECTIONS:
        html = visual_fixture.page(data, direction)
        for tier in locked:
            if tier.get("text") and tier["text"] in html:
                fail("locked hint tier %d leaked into %s" % (tier["tier"], direction))
    ok("check_no_keyed_leak")


SEMANTIC_STRIP = re.compile(r'\sdata-direction="[^"]*"|\sclass="[^"]*"'
                            r'|<style>.*?</style>', re.S)


def semantic_fingerprint(html):
    body = html.split("<main>", 1)[1].rsplit("</main>", 1)[0]
    return SEMANTIC_STRIP.sub("", body)


def check_semantic_parity():
    from surfaces import visual_fixture
    data = load()
    prints = {d: semantic_fingerprint(visual_fixture.page(data, d)) for d in DIRECTIONS}
    base = prints[DIRECTIONS[0]]
    for d in DIRECTIONS[1:]:
        if prints[d] != base:
            fail("direction %s forked the semantic markup" % d)
    ok("check_semantic_parity")


def check_directions_differ():
    from surfaces import visual_fixture
    data = load()
    pages = {d: visual_fixture.page(data, d) for d in DIRECTIONS}
    if len(set(pages.values())) != len(DIRECTIONS):
        fail("two directions rendered byte-identical pages, so no comparison exists")
    ok("check_directions_differ")


def check_tokens_resolve():
    """Every custom property the page references must be defined in the page,
    or the prototype renders against silent browser defaults."""
    from surfaces import visual_fixture
    data = load()
    for direction in DIRECTIONS:
        html = visual_fixture.page(data, direction)
        used = set(re.findall(r"var\((--[a-z0-9-]+)", html))
        defined = set(re.findall(r"(--[a-z0-9-]+)\s*:", html))
        missing = sorted(used - defined)
        if missing:
            fail("%s references undefined tokens: %s" % (direction, ", ".join(missing)))
    ok("check_tokens_resolve")


def check_abuse_clamp():
    from surfaces import visual_fixture
    data = load()
    abusive = {"density": "9999", "measure": "10000px",
               "accent": "javascript:alert(1)", "leading": "-4"}
    html = visual_fixture.page(data, "structured-studio", tokens=abusive)
    if "9999" in html or "10000px" in html:
        fail("an out-of-bounds token reached the page unclamped")
    if "javascript:" in html:
        fail("an unsafe accent value reached the page")
    for fixed in ("focus-visible", "prefers-reduced-motion"):
        if fixed not in html:
            fail("fixed rule %s is missing under token abuse" % fixed)
    ok("check_abuse_clamp")


def check_degraded_states():
    """Missing upstream 16B or 16C data renders an explicit unavailable state
    and never invents runtime authority."""
    from surfaces import visual_fixture
    stripped = {"fixture_version": 1, "synthetic": True, "stages": []}
    html = visual_fixture.page(stripped, "structured-studio")
    if "unavailable" not in html.lower():
        fail("an empty flow did not render an explicit unavailable state")
    body = html.split("<main>", 1)[1].rsplit("</main>", 1)[0]
    if re.search(r"\d+\s*%", body):
        fail("an invented percentage appeared in a degraded state")
    ok("check_degraded_states")


def check_route_is_dev_only():
    import server
    if not hasattr(server, "maybe_visual_fixture"):
        fail("server.py does not expose the visual fixture route")
        return
    os.environ.pop("ITEMBANK_VISUAL_FIXTURE", None)
    if server.visual_fixture_enabled():
        fail("the fixture route is reachable without an explicit opt in")
    os.environ["ITEMBANK_VISUAL_FIXTURE"] = "1"
    if not server.visual_fixture_enabled():
        fail("the fixture route did not enable under its opt in")
    os.environ.pop("ITEMBANK_VISUAL_FIXTURE", None)
    ok("check_route_is_dev_only")


def check_one_shell():
    src = open(os.path.join(ROOT, "surfaces", "visual_fixture.py"),
               encoding="utf-8").read()
    if "<!doctype" in src.lower():
        fail("visual_fixture.py builds its own document shell instead of surface_shell")
    if "surface_shell" not in src:
        fail("visual_fixture.py does not route through presentation.surface_shell")
    ok("check_one_shell")


def check_directions_are_deletable():
    """D-04 reversibility: each direction's CSS lives in its own file, so one
    can be removed without touching the other two or the shipped surfaces."""
    for direction in DIRECTIONS:
        path = os.path.join(ROOT, "prototypes", "17a", direction + ".css")
        if not os.path.exists(path):
            fail("direction %s has no separate deletable stylesheet" % direction)
    ok("check_directions_are_deletable")


def main():
    check_fixture_shape()
    check_no_em_dash()
    check_no_keyed_leak()
    check_semantic_parity()
    check_directions_differ()
    check_tokens_resolve()
    check_abuse_clamp()
    check_degraded_states()
    check_route_is_dev_only()
    check_one_shell()
    check_directions_are_deletable()
    if failures:
        print("\n%d failure(s)" % len(failures))
        return 1
    print("\nall visual-system contract checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
