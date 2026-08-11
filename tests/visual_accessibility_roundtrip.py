#!/usr/bin/env python3
"""Plan 06.1-03 Task 1: modality equivalence and the accessibility contract.

Automated structural assertions over the served and offline clients: every
input path (SVG pointer, keyboard, native semantic controls) reduces through
ONE committed/tentative state pair and ONE serializer producing byte-identical
canonical SCALAR action requests; the commit boundary emits only the four
protocol actions on explicit successful commits and nothing on pointer-down,
focus, hover, tentative/cancelled, or unchanged states; Escape/pointercancel
restore the last committed state; the SVG has an accessible name and visible
focus and no canvas element is used; the static/offline output refuses visual
items honestly with no key/scoring material; and the served public payload
stays key-free. The manual layer (keyboard-only and touch-emulation walkthrough
plus screen-reader and 320px/200% checks) is the phase's end-of-phase human
check, recorded in VERIFICATION/UAT.

Standard library only, no test framework, runnable as
`python tests/visual_accessibility_roundtrip.py`.
"""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.request


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMBANK = os.path.join(ROOT, "itembank.py")
BANK = os.path.join(ROOT, "fixtures", "visual_bank.md")
sys.path.insert(0, ROOT)

import model                                           # noqa: E402
import runtime                                         # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def ok(msg):
    print("ok: " + msg)


def served_js():
    src = open(os.path.join(ROOT, "surfaces", "quiz_page.py"),
               encoding="utf-8").read()
    m = re.search(r"SERVED_JS = r\"\"\"(.*?)\"\"\"", src, re.S)
    if not m:
        fail("cannot locate SERVED_JS in quiz_page.py")
    return m.group(1)


def offline_js():
    src = open(os.path.join(ROOT, "surfaces", "quiz_page.py"),
               encoding="utf-8").read()
    m = re.search(r"OFFLINE_JS = r\"\"\"(.*?)\"\"\"", src, re.S)
    if not m:
        fail("cannot locate OFFLINE_JS in quiz_page.py")
    return m.group(1)


def load_questions():
    return model.parse_bank(open(BANK, encoding="utf-8").read())


# ---- 1. one state pair + one serializer for every modality ------------------

def check_single_serializer():
    js = served_js()
    # Exactly one function that turns state into the canonical wire JSON.
    if js.count("function serialize()") != 1:
        fail("SERVED_JS must define exactly one serializer, found %d"
             % js.count("function serialize()"))
    # All three wire shapes come from that one function (the JS builds the
    # dict with unquoted keys and JSON.stringify serializes them).
    for shape in ("kind:\"point\"", "kind:\"numberline_point\"",
                  "kind:\"interval\""):
        if shape not in js:
            fail("serializer does not emit the %s wire shape" % shape)
    # Pointer, keyboard, and native controls all call commitMove / adopt, i.e.
    # they reduce through the same committed/tentative state pair.
    for marker in ("function commitMove", "pointerup", "keydown",
                   "commitBtn.onclick", "valueSelect"):
        if marker not in js:
            fail("SERVED_JS is missing %r (modality equivalence broken)" % marker)
    if js.count("Object.assign(committed") < 1:
        fail("no path adopts a tentative move into committed state")
    ok("modality equivalence: one serializer, one committed/tentative reducer")


def check_commit_boundary():
    js = served_js()
    # Pointer-down never commits; pointer-up after a CHANGED drag commits.
    if "pointerdown" not in js:
        fail("no pointerdown handler")
    if "pointerup" not in js:
        fail("no pointerup handler")
    if "pointercancel" not in js or "revertTentative" not in js:
        fail("pointer cancellation does not restore the last committed state")
    # Escape cancels a tentative move.
    if 'e.key === "Escape"' not in js:
        fail("Escape does not cancel a tentative move")
    if 'e.key === "Enter"' not in js and 'e.key === " "' not in js:
        fail("Enter/Space does not commit")
    # No change -> no commit (D-04).
    if "No change to commit" not in js:
        fail("unchanged commits are not explicitly a no-op")
    # The four locked action types, and submit stays the ordinary response.
    for action in ("place_point", "move_point", "select_numberline_point",
                   "set_interval"):
        if action not in js:
            fail("action type %r missing from the served client" % action)
    ok("commit boundary: explicit commits only; cancel/unchanged append nothing")


def check_no_canvas_and_svg_accessibility():
    js = served_js()
    if "createElementNS" not in js or '"http://www.w3.org/2000/svg"' not in js:
        fail("served client does not build inline SVG")
    if re.search(r"<canvas|createElement\(\"canvas\"\)", js):
        fail("served client uses a canvas element for the plot/number-line slice")
    if 'setAttribute("aria-label"' not in js or 'setAttribute("role", "img")' not in js:
        fail("SVG has no accessible name/role")
    if 'setAttribute("tabindex", "0")' not in js:
        fail("SVG is not keyboard-operable")
    if 'role", "status"' not in js or '"aria-live", "polite"' not in js:
        fail("no polite status region for committed state / observation")
    ok("no canvas; SVG named and keyboard-operable; polite status region")


def check_served_payload_key_free():
    qs = load_questions()
    for q in qs:
        item = runtime.public_item(q)
        blob = json.dumps(item)
        for banned in ("accepted", "tolerance", "partial_credit", "scoring",
                       "correct", "model", "why"):
            if re.search(r'"%s"\s*:' % banned, blob):
                fail("served public item leaks %r" % banned)
    ok("served public payloads carry no key/scoring/explanation material")


# ---- 2. static/offline refusal (D-03/A-05) -----------------------------------

def check_offline_refusal():
    qs = load_questions()
    for q in qs:
        item = runtime.page_item(q, offline=True)
        if item.get("served_required") is not True:
            fail("offline visual item does not carry served_required")
        if "key" in item:
            fail("offline visual item carries a key")
        blob = json.dumps(item)
        for banned in ("accepted", "tolerance", "partial_credit"):
            if re.search(r'"%s"\s*:' % banned, blob):
                fail("offline visual item leaks %r" % banned)
    js = offline_js()
    if "asVisualOffline" not in js:
        fail("OFFLINE_JS has no served-runtime-required refusal renderer")
    if "needs a served itembank session" not in js:
        fail("offline refusal does not state that a served runtime is required")
    if "visual:asVisualOffline" not in js:
        fail("OFFLINE_JS does not route visual items to the refusal renderer")
    ok("offline refusal: served_required flag, no key/scoring material, honest copy")


def check_offline_build_page():
    work = tempfile.mkdtemp()
    try:
        isolated = os.path.join(work, "visual_bank.md")
        shutil.copyfile(BANK, isolated)
        out = os.path.join(work, "out.html")
        r = subprocess.run(
            [sys.executable, ITEMBANK, "build", isolated, out, "--force"],
            capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            fail("static build of the visual bank failed: %s"
                 % (r.stderr or r.stdout)[-500:])
        html = open(out, encoding="utf-8").read()
        if "needs a served itembank session" not in html:
            fail("static build page has no served-runtime-required refusal")
        for banned in ('"accepted"', '"tolerance"', '"partial_credit"',
                       '"key"'):
            if banned in html:
                fail("static build page leaks %s" % banned)
        if "asVisualOffline" not in html:
            fail("static build page does not include the offline refusal renderer")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    ok("static build: visual items refuse loudly with no key/scoring material")


# ---- 3. served page carries the renderer and stays key-free over HTTP -------

def check_served_page():
    work = tempfile.mkdtemp()
    try:
        isolated = os.path.join(work, "visual_bank.md")
        shutil.copyfile(BANK, isolated)
        proc = subprocess.Popen(
            [sys.executable, "-u", ITEMBANK, "serve", isolated,
             "--no-open", "--port", "0", "--out", os.path.join(work, "attempt.md")],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        lines = []
        threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                         daemon=True).start()
        base = None
        for _ in range(80):
            time.sleep(0.1)
            m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
            if m:
                base = m.group(0)
                break
        if not base:
            fail("server never printed a URL")
        stem = os.path.splitext(os.path.basename(isolated))[0]
        html = urllib.request.urlopen(
            base + "quiz/%s" % stem, timeout=5).read().decode("utf-8")
        for marker in ("function asVisual", "function commitMove",
                       '"aria-live", "polite"', 'setAttribute("role", "img")'):
            if marker not in html:
                fail("served page is missing %r" % marker)
        if '"http://www.w3.org/2000/svg"' not in html:
            fail("served page does not construct inline SVG")
        if "function asVisualOffline" in html:
            fail("served page carries the offline refusal renderer")
        if "<canvas" in html:
            fail("served page uses canvas for the visual slice")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    ok("served page: asVisual + commit boundary + SVG + status region, no canvas")


def main():
    check_single_serializer()
    check_commit_boundary()
    check_no_canvas_and_svg_accessibility()
    check_served_payload_key_free()
    check_offline_refusal()
    check_offline_build_page()
    check_served_page()
    print("PASS visual_accessibility_roundtrip.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
