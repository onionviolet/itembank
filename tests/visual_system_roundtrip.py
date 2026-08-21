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


def check_harness_never_becomes_authority():
    """The agent console proposes; the runtime accepts. Every write is gated by
    an approval or an autonomy level, every commit is journalled with an undo,
    and egress is stated per backend. A harness that could settle a score or
    release a key would be the second authority the runtime invariant forbids."""
    from surfaces import visual_fixture
    data = load()
    stage = [s for s in data["stages"] if s["id"] == "agent_harness"]
    if not stage:
        fail("no agent harness stage in the fixture")
        return
    stage = stage[0]
    levels = [lv["id"] for lv in stage["autonomy"]["levels"]]
    for shipped in ("report_only", "draft_and_approve", "audit_draft_lint_fix_commit"):
        if shipped not in levels:
            fail("autonomy level %s is not offered, but the setting ships it" % shipped)
    for backend in stage["backends"]:
        if not backend.get("egress"):
            fail("backend %s does not state what leaves the machine" % backend["id"])
    html = visual_fixture.page(data, "structured-studio", stage_id="agent_harness")
    body = html.split("<main>", 1)[1].rsplit("</main>", 1)[0]
    for control in ("Accept", "Reject", "Undo"):
        if control not in body:
            fail("the harness offers no %s control" % control)
    for banned in ("score", "mark as correct", "reveal the answer", "answer key"):
        if banned in body.lower():
            fail("the harness surfaces a scoring or disclosure control: %s" % banned)
    if not any(e.get("undo") for e in stage["journal"]):
        fail("no journalled operation is undoable")
    if "spent" not in body.lower():
        fail("the harness does not show what it has spent")
    ok("check_harness_never_becomes_authority")


def check_nav_sections():
    """Eight flat areas do not say that Learn is daily and Sources is
    occasional. Three named sections do."""
    from surfaces import visual_fixture
    data = load()
    sections = (data.get("app") or {}).get("sections", [])
    if len(sections) < 3:
        fail("the navigation is not sectioned")
        return
    known = set()
    for section in sections:
        if not section.get("hint"):
            fail("section %s does not say what it is for" % section["id"])
        known.update(section.get("areas", []))
    app = data.get("app") or {}
    defined = {a["id"] for a in app.get("course_areas", [])}
    defined |= {a["id"] for a in app.get("app_areas", [])}
    for area_id in defined:
        if area_id not in known and area_id != "home":
            fail("area %s belongs to no section" % area_id)
    for area_id in known:
        if area_id not in defined:
            fail("section names area %s, which is defined nowhere" % area_id)
    html = visual_fixture.page(data, "structured-studio", stage_id="long_lesson")
    for label in ("Study", "Build", "Operate"):
        if label not in html:
            fail("section %s is not rendered in the shell" % label)
    ok("check_nav_sections")


def check_harness_live_wiring():
    """The harness reads the shipped journal and the shipped settings, and says
    per panel which it got. Fixture data must never be presented as real."""
    from surfaces import visual_fixture
    data = load()
    stage = [st for st in data["stages"] if st["id"] == "agent_harness"][0]

    synthetic = visual_fixture.page(data, "structured-studio",
                                    stage_id="agent_harness")
    if "Synthetic sample" not in synthetic:
        fail("unwired harness does not declare itself synthetic")

    live = visual_fixture.page(data, "structured-studio",
                               stage_id="agent_harness", base=ROOT)
    if "Synthetic sample" in live:
        fail("wired harness still claims a panel is synthetic")

    state = visual_fixture.harness_state(stage, ROOT)
    if not state.get("journal_live") or not state.get("backends_live"):
        fail("a wired panel did not report itself live")
    fixture_names = {b["label"] for b in stage["backends"]}
    live_names = {b["label"] for b in state["backends"]}
    if live_names and live_names == fixture_names:
        fail("live backends are the fixture list, so the read did nothing")
    if not state["backends"] and not state.get("backends_note"):
        fail("no backends and no explanation of why")
    for row in state["journal"]:
        if row.get("op") and row["op"] not in visual_fixture.OPERATION_PHRASE                 and row["op"] not in visual_fixture.UNDOABLE:
            fail("journal row %s is neither phrased nor classified" % row["op"])

    missing = visual_fixture.live_journal(os.path.join(ROOT, "no-such-dir"))
    if missing[0]:
        fail("a missing journal produced rows instead of a note")
    if not missing[1]:
        fail("a missing journal produced neither rows nor a note")
    ok("check_harness_live_wiring")


def check_harness_undo_classification():
    """A read is not undoable and an external edit was never ours to reverse.
    Every write is."""
    from surfaces import visual_fixture
    for write in ("mint", "edit_in_place", "supersede", "restore"):
        if write not in visual_fixture.UNDOABLE:
            fail("write operation %s is not marked undoable" % write)
    if "external_edit" in visual_fixture.UNDOABLE:
        fail("an external edit is marked undoable, but it was never ours to undo")
    try:
        import journal
    except ImportError:
        ok("check_harness_undo_classification (journal absent, skipped)")
        return
    for record in journal.RECORD_TYPES:
        if record not in visual_fixture.OPERATION_PHRASE:
            fail("journal record type %s has no learner-facing phrase" % record)
    ok("check_harness_undo_classification")


def check_single_file_is_self_contained():
    """The multi-file export links each screen to a sibling file, which is dead
    anywhere the siblings are absent, such as a preview pane handed one file.
    The single-file build must carry every screen, look and nav shape inline and
    switch without script or navigation."""
    from surfaces import visual_fixture
    data = load()
    html = visual_fixture.single_file(data)
    if "<script" in html.lower():
        fail("the single file contains script, which a sandbox may block")
    if 'href="?' in html or "../" in html:
        fail("the single file still links to something that is not in it")
    ids = visual_fixture.stage_ids(data)
    for sid in ids:
        if ('data-screen="%s"' % sid) not in html:
            fail("screen %s is missing from the single file" % sid)
        if ('for="screen-%s"' % sid) not in html:
            fail("screen %s has no switch control" % sid)
    for d in visual_fixture.DIRECTIONS:
        if ('for="look-%s"' % d) not in html:
            fail("look %s has no switch control" % d)
    for n in visual_fixture.NAV_SHAPES:
        if ('for="nav-%s"' % n) not in html:
            fail("nav shape %s has no switch control" % n)
    if html.count('type="radio"') < len(ids) + len(visual_fixture.DIRECTIONS)             + len(visual_fixture.NAV_SHAPES):
        fail("fewer radio switches than screens plus looks plus nav shapes")
    ok("check_single_file_is_self_contained")


def check_gloss_positioning_degrades():
    """The shipped glossary panel positions itself with CSS anchor positioning,
    which is recent. Without it the panel lands somewhere arbitrary, which is
    most of what "looks broken" means. The base must work everywhere and anchor
    positioning must be the upgrade."""
    from surfaces import visual_fixture
    html = visual_fixture.single_file(load())
    fallback = visual_fixture.GLOSS_FALLBACK_CSS
    if "@supports (position-area" not in fallback:
        fail("anchor positioning is not gated behind an @supports upgrade")
    if "position: fixed" not in fallback:
        fail("there is no positioning fallback for a browser without anchors")
    if ".gloss:target" not in fallback:
        fail("a definition is unreachable where the Popover API is absent")
    if "@supports (position-area" not in html:
        fail("the fallback did not reach the rendered page")
    ok("check_gloss_positioning_degrades")


def check_nav_entries_are_uniform():
    """Every navigation entry, whether it links, switches, or is unavailable,
    carries one entry class. An entry that missed it was styled by nothing, so
    in the horizontal shapes it collapsed below its own word width and rendered
    one letter per line. This is the bug Weibao photographed."""
    from surfaces import visual_fixture
    data = load()
    for nav_shape in visual_fixture.NAV_SHAPES:
        html = visual_fixture.page(data, "structured-studio",
                                   stage_id="shelf_resume", nav_shape=nav_shape)
        for block in re.findall(r'<nav class="vf-appnav".*?</nav>', html, re.S):
            if "<span>" in block:
                fail("%s nav contains an unclassed span, which nothing styles"
                     % nav_shape)
            for entry in re.findall(r"<li[^>]*>(.*?)</li>", block, re.S):
                if "vf-area-entry" not in entry and "<a " not in entry                         and "<label " not in entry:
                    fail("%s nav has an entry with no entry class" % nav_shape)
    single = visual_fixture.single_file(data)
    for block in re.findall(r'<nav class="vf-appnav".*?</nav>', single, re.S):
        if "<span>" in block:
            fail("the single-file nav contains an unclassed span")
    ok("check_nav_entries_are_uniform")


def check_horizontal_shapes_cannot_stack_text():
    """A shape that lays entries out in a row must stop them shrinking below
    their own word, and must hide the route line that doubles their height."""
    from surfaces import visual_fixture
    for shape in ("tabs", "bottom"):
        css = visual_fixture.overlay_css("nav-" + shape)
        if "white-space: nowrap" not in css:
            fail("nav-%s lets an entry wrap inside a row" % shape)
        if ".vf-area-route { display: none; }" not in css:
            fail("nav-%s shows the route line in a horizontal row" % shape)
    bottom = visual_fixture.overlay_css("nav-bottom")
    hidden = re.search(r"\.vf-nav-brand[^{]*\{[^}]*display:\s*none", bottom)
    if not hidden:
        fail("nav-bottom does not hide the chrome that does not fit a thumb bar")
    for should_hide in (".vf-courses", ".vf-nav-label", ".vf-nav-course-name"):
        if should_hide not in hidden.group(0) and should_hide not in                 bottom[:hidden.end()]:
            fail("nav-bottom does not hide %s, which stacked letter by letter"
                 % should_hide)
    ok("check_horizontal_shapes_cannot_stack_text")


def check_course_selector():
    """The vision is one learner across three subjects at once, so the shell
    offers the switch rather than hiding it on Home."""
    from surfaces import visual_fixture
    data = load()
    courses = (data.get("app") or {}).get("courses", [])
    if len(courses) < 3:
        fail("the course selector offers fewer than three courses")
    current = [c for c in courses if c.get("current")]
    if len(current) != 1:
        fail("exactly one course must be current, found %d" % len(current))
    for course in courses:
        if not course.get("resume"):
            fail("course %s does not say where you stopped" % course.get("id"))
    for nav_shape in ("sidebar", "tabs"):
        html = visual_fixture.page(data, "structured-studio",
                                   stage_id="shelf_resume", nav_shape=nav_shape)
        if "vf-courses" not in html:
            fail("%s does not render the course selector" % nav_shape)
        for course in courses:
            if course["label"] not in html:
                fail("course %s is missing from the %s shell"
                     % (course["id"], nav_shape))
    ok("check_course_selector")


def check_controls_never_break_midword():
    """SHARED_CSS grants p overflow-wrap:anywhere so a long path in prose can
    wrap. That inherits into any control inside a paragraph, which is how a
    one-word button ends up stacking one letter per line in a narrow column.
    Every control must opt back out."""
    from surfaces import visual_fixture
    css = visual_fixture.CHROME_CSS
    rule = [block for sel, block in
            re.findall(r"([^{}]+)\{([^}]*)\}", css)
            if "overflow-wrap: normal" in block]
    if not rule:
        fail("no rule returns controls to normal word wrapping")
        return
    guarded = ""
    for sel, block in re.findall(r"([^{}]+)\{([^}]*)\}", css):
        if "overflow-wrap: normal" in block:
            guarded += sel
    for control in (".vf-next", ".vf-prev", ".vf-appnav a", "button"):
        if control not in guarded:
            fail("control %s can still break mid-word" % control)
    if "word-break: keep-all" not in css:
        fail("controls do not forbid a mid-word break")
    ok("check_controls_never_break_midword")


def check_accent_is_swappable():
    """The accent is a real setting, not a hard-coded green: itembank theme
    preview/set/reset/pick ships, and theme.derive_theme raises a colour that
    fails contrast rather than accepting it. The prototype offers four so the
    question answers itself by looking."""
    from surfaces import visual_fixture, theme
    if len(visual_fixture.ACCENTS) < 3:
        fail("fewer than three accents are offered")
    html = visual_fixture.single_file(load())
    for name, hexcode in visual_fixture.ACCENTS:
        if ('id="accent-%s"' % name) not in html:
            fail("accent %s has no switch" % name)
        if ("body:has(#accent-%s:checked)" % name) not in html:
            fail("accent %s has no scoped palette" % name)
        derived = theme.derive_theme(hexcode)
        for mode in ("light", "dark"):
            if not derived[mode].get("accent"):
                fail("accent %s derives no %s token" % (name, mode))
    ok("check_accent_is_swappable")


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
    check_harness_never_becomes_authority()
    check_nav_sections()
    check_harness_live_wiring()
    check_harness_undo_classification()
    check_single_file_is_self_contained()
    check_gloss_positioning_degrades()
    check_nav_entries_are_uniform()
    check_horizontal_shapes_cannot_stack_text()
    check_course_selector()
    check_controls_never_break_midword()
    check_accent_is_swappable()
    if failures:
        print("\n%d failure(s)" % len(failures))
        return 1
    print("\nall visual-system contract checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
