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


# Prototype-only plumbing, excluded from the parity claim: the direction
# switcher, and the `direction=` query parameter the prototype threads through
# every link. In the product a route names a screen, never a visual direction.
SEMANTIC_STRIP = re.compile(
    r'<nav class="vf-chrome".*?</nav>'
    r'|direction=[a-z-]+&amp;nav=[a-z-]+&amp;'
    r'|direction=[a-z-]+&amp;'
    r'|\sdata-direction="[^"]*"|\sclass="[^"]*"|<style>.*?</style>', re.S)


def semantic_fingerprint(html):
    body = html.split("<main>", 1)[1].rsplit("</main>", 1)[0]
    return SEMANTIC_STRIP.sub("", body)


def check_semantic_parity():
    """Every screen must be byte-identical across directions once prototype
    chrome and styling hooks are stripped."""
    from surfaces import visual_fixture
    data = load()
    for sid in visual_fixture.stage_ids(data):
        prints = {d: semantic_fingerprint(visual_fixture.page(data, d, stage_id=sid))
                  for d in DIRECTIONS}
        base = prints[DIRECTIONS[0]]
        for d in DIRECTIONS[1:]:
            if prints[d] != base:
                fail("direction %s forked the markup on screen %s" % (d, sid))
    ok("check_semantic_parity")


def check_directions_differ():
    from surfaces import visual_fixture
    data = load()
    pages = {d: visual_fixture.page(data, d, stage_id="long_lesson")
             for d in DIRECTIONS}
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


def check_multi_page_flow():
    """The prototype is a sequence of screens, not one scroll. Each screen
    renders exactly one stage and links to its neighbours."""
    from surfaces import visual_fixture
    data = load()
    ids = visual_fixture.stage_ids(data)
    if len(ids) < 2:
        fail("fixture has too few stages to form a flow")
        return
    for index, sid in enumerate(ids):
        html = visual_fixture.page(data, "structured-studio", stage_id=sid)
        body = html.split("<main>", 1)[1].rsplit("</main>", 1)[0]
        stages_rendered = re.findall(r'<section class="vf-stage" data-stage="([^"]+)"', body)
        if stages_rendered != [sid]:
            fail("screen %s rendered %d stages, expected exactly one"
                 % (sid, len(stages_rendered)))
        if "Step %d of %d" % (index + 1, len(ids)) not in body:
            fail("screen %s does not state its position in the flow" % sid)
        if index > 0 and ("stage=" + ids[index - 1]) not in body:
            fail("screen %s has no link back" % sid)
        if index < len(ids) - 1 and ("stage=" + ids[index + 1]) not in body:
            fail("screen %s has no link forward" % sid)
    ok("check_multi_page_flow")


def check_all_directions_reachable():
    """Weibao asked to keep all three rather than freeze one, so every screen
    offers every direction."""
    from surfaces import visual_fixture
    data = load()
    for sid in visual_fixture.stage_ids(data):
        html = visual_fixture.page(data, "quiet-workbench", stage_id=sid)
        for d in DIRECTIONS:
            if ("direction=" + d) not in html:
                fail("screen %s cannot reach direction %s" % (sid, d))
    ok("check_all_directions_reachable")


def check_hover_definitions():
    """Confusing terms carry a definition that ships with the page and works
    with no network and no JavaScript, and it comes from the one shipped
    glossary in surfaces/lesson.py rather than a second implementation."""
    from surfaces import visual_fixture
    data = load()
    terms = {t["slug"] for t in data.get("terms", [])}
    if "inspiration" not in terms:
        fail("the fixture does not define inspiration, the term that prompted this")
    html = visual_fixture.page(data, "structured-studio", stage_id="long_lesson")
    body = html.split("<main>", 1)[1].rsplit("</main>", 1)[0]
    if 'popovertarget="gloss-inspiration"' not in body:
        fail("inspiration is not marked as a hover term in the lesson")
    if "Breathing in" not in body:
        fail("the definition text does not ship with the page")
    for slug in ("inspiration", "patent"):
        if ('id="gloss-%s"' % slug) not in body:
            fail("term %s has no popover panel in the page" % slug)
        if ('id="term-%s"' % slug) not in body:
            fail("term %s is missing from the glossary appendix" % slug)
    if "aria-label" in body.split('popovertarget="gloss-inspiration"')[0][-160:]:
        fail("a definition rode in on the trigger accessible name")
    src = open(os.path.join(ROOT, "surfaces", "visual_fixture.py"), encoding="utf-8").read()
    if "_gloss_trigger_html" not in src or "_gloss_panel_html" not in src:
        fail("visual_fixture built its own glossary instead of reusing lesson.py")
    ok("check_hover_definitions")


def check_no_raw_term_markers():
    """A [[term]] with no glossary entry must never reach the page as literal
    brackets."""
    from surfaces import visual_fixture
    data = load()
    for sid in visual_fixture.stage_ids(data):
        html = visual_fixture.page(data, "structured-studio", stage_id=sid)
        body = html.split("<main>", 1)[1].rsplit("</main>", 1)[0]
        if "[[" in body or "]]" in body:
            fail("screen %s leaked a raw term marker" % sid)
    ok("check_no_raw_term_markers")


def check_nav_shapes():
    """The navigation shape is a second axis from the visual direction, and it
    is CSS over identical markup. 16B-UI-SPEC settles which areas exist; it is
    silent on whether they are a sidebar, a tab row, or a bottom bar, so all
    three ship until Weibao picks."""
    from surfaces import visual_fixture
    data = load()
    shapes = visual_fixture.NAV_SHAPES
    if len(shapes) < 3:
        fail("fewer than three navigation shapes are offered")
    bodies = {}
    for shape in shapes:
        html = visual_fixture.page(data, "structured-studio",
                                   stage_id="long_lesson", nav_shape=shape)
        if ('data-nav="%s"' % shape) not in html:
            fail("shape %s did not reach the shell" % shape)
        for other in shapes:
            if ("nav=" + other) not in html:
                fail("shape %s cannot reach shape %s" % (shape, other))
        body = html.split("<main>", 1)[1].rsplit("</main>", 1)[0]
        bodies[shape] = SEMANTIC_STRIP.sub("", body).replace(
            'data-nav="%s"' % shape, "")
    base = bodies[shapes[0]]
    for shape in shapes[1:]:
        if bodies[shape] != base:
            fail("nav shape %s forked the markup instead of restyling it" % shape)
    ok("check_nav_shapes")


def check_app_shell_matches_16b():
    """Every course-level area in 16B-UI-SPEC's route contract appears in the
    shell, so the prototype and the contract can be diffed rather than trusted."""
    from surfaces import visual_fixture
    data = load()
    areas = [a["label"] for a in (data.get("app") or {}).get("course_areas", [])]
    for expected in ("Overview", "Learn", "Practice", "Test", "Map", "Sources",
                     "Build", "Evidence"):
        if expected not in areas:
            fail("course area %s from the 16B route contract is missing" % expected)
    html = visual_fixture.page(data, "structured-studio", stage_id="shelf_resume")
    for route in ("/activity", "/settings", "/course/&lt;id&gt;/learn"):
        if route not in html:
            fail("route %s is not shown in the app shell" % route)
    ok("check_app_shell_matches_16b")


def check_home_screen():
    """Home is a real screen: a justified next action, the course list, and the
    activity queue, with no invented percentage anywhere."""
    from surfaces import visual_fixture
    data = load()
    html = visual_fixture.page(data, "structured-studio", stage_id="shelf_resume")
    body = html.split("<main>", 1)[1].rsplit("</main>", 1)[0]
    for needed in ("Pick up where you stopped", "All courses", "Activity"):
        if needed not in body:
            fail("home screen is missing the %s region" % needed)
    if "vf-resume" not in body:
        fail("home screen has no resume card")
    if re.search(r"\d+\s*%", body):
        fail("home screen invented a percentage")
    if "DIR" in body or "NAV" in body:
        fail("home screen leaked an unsubstituted template placeholder")
    ok("check_home_screen")


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
    check_multi_page_flow()
    check_all_directions_reachable()
    check_hover_definitions()
    check_no_raw_term_markers()
    check_nav_shapes()
    check_app_shell_matches_16b()
    check_home_screen()
    if failures:
        print("\n%d failure(s)" % len(failures))
        return 1
    print("\nall visual-system contract checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
