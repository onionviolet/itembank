#!/usr/bin/env python3
"""Responsive product contract for the accepted learner workspace.

Desktop and phone share routes and runtime state, but they do not share one
shrunken composition. This test guards the wide persistent workspace, narrow
touch navigation, activity framing, and resize-safe response ownership.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from surfaces import lesson, presentation, quiz_page  # noqa: E402


def fail(message):
    raise AssertionError(message)


def check_desktop_workspace():
    page = presentation.surface_shell(
        "Courses",
        '<nav class="app-nav" aria-label="Application"></nav>'
        '<section class="desk-heading"><h2>A little further, today.</h2></section>'
        '<section class="desk-hero"></section><div class="desk-below"></div>')
    required = (
        'class="product-shell"', 'class="product-sidebar"',
        'class="product-workspace"', 'class="product-topbar"',
        'class="product-nav"', 'class="desk-below"',
    )
    for token in required:
        if token not in page:
            fail("desktop workspace omitted %r" % token)
    if page.count('class="product-sidebar"') != 1:
        fail("desktop workspace rendered duplicate persistent navigation")
    css = presentation.PRODUCT_CSS
    for rule in ("grid-template-columns:224px 1fr",
                 "grid-template-columns:1.05fr .95fr",
                 "grid-template-columns:1.55fr 1fr"):
        if rule not in css:
            fail("desktop composition lost %r" % rule)
    print("ok: desktop has one persistent rail and three intentional multi-column work areas")


def check_phone_workflow():
    css = presentation.PRODUCT_CSS
    phone = css[css.index("@media(max-width:767px)"):]
    required = (
        ".product-shell{display:block}", "position:fixed", "bottom:0",
        "height:66px", ".desk-hero{min-height:0;grid-template-columns:1fr}",
        ".desk-below{grid-template-columns:1fr", ".ib-palette-open{display:none}",
    )
    for token in required:
        if token not in phone:
            fail("phone composition omitted %r" % token)
    if "min-height:44px" not in css:
        fail("phone navigation lost its 44px minimum touch target")
    print("ok: phone swaps the rail for fixed touch navigation and stacks primary work")


def check_reading_and_practice_share_the_frame():
    if "__PRODUCT_NAV__" not in lesson.LESSON_TEMPLATE:
        fail("reader does not mount the responsive product navigation")
    if "__PRODUCT_NAV__" not in quiz_page.TEMPLATE:
        fail("practice does not mount the responsive product navigation")
    if "standalone_product_nav()" not in open(
            os.path.join(ROOT, "surfaces", "quiz.py"), encoding="utf-8").read():
        fail("quiz renderer does not supply the shared responsive navigation")
    if "addEventListener(\"resize\"" in quiz_page.TEMPLATE or \
            "addEventListener('resize'" in quiz_page.TEMPLATE:
        fail("practice owns resize behavior that could reset runtime or draft state")
    quiz_source = open(os.path.join(ROOT, "surfaces", "quiz_page.py"),
                       encoding="utf-8").read()
    for token in ("itembank.draft.", "localStorage", "dataset.itemId"):
        if token not in quiz_source:
            fail("practice lost resize/reload-safe draft token %r" % token)
    print("ok: reader and practice share the frame; CSS resize cannot replace runtime or draft state")


def check_accessibility_contract():
    nav = presentation.standalone_product_nav()
    for token in ('aria-label="Main navigation"', "Your desk", "Courses",
                  "Activity", "Settings"):
        if token not in nav:
            fail("responsive navigation omitted %r" % token)
    css = presentation.PRODUCT_CSS
    if "focus-visible" not in presentation.SHARED_CSS:
        fail("shared keyboard focus treatment is absent")
    if "overflow-x:hidden" in css or "white-space:nowrap" in css:
        fail("responsive product hides overflow or prevents meaningful wrapping")
    print("ok: keyboard focus, labelled navigation, wrapping, and touch target contracts remain visible")


def check_secondary_destinations():
    nav = presentation._product_sidebar("activity")
    required = ('href="/courses"', 'href="/activity" aria-current="page"',
                'href="/settings"')
    for token in required:
        if token not in nav:
            fail("secondary navigation is missing %s" % token)
    source = open(os.path.join(ROOT, "surfaces", "daemon.py"),
                  encoding="utf-8").read()
    for token in ('("GET", "/courses", "handle_courses_get")',
                  "def handle_courses_get(handler):", "No activity yet"):
        if token not in source:
            fail("Courses destination is not independently routed")
    settings_source = open(os.path.join(ROOT, "surfaces", "daemon.py"),
                           encoding="utf-8").read()
    if "palette=True, product=True" not in settings_source:
        fail("served Settings still bypasses the accepted product frame")
    print("ok: Courses, Activity, and Settings are distinct framed destinations")


def main():
    check_desktop_workspace()
    check_phone_workflow()
    check_reading_and_practice_share_the_frame()
    check_accessibility_contract()
    check_secondary_destinations()
    print("responsive product: 5 passed, 0 failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
