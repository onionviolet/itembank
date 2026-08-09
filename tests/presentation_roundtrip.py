#!/usr/bin/env python3
"""Wave 0 harness for Phase 4's semantic presentation layer (plans 04-04
through 04-06): stdlib HTML parsing into a semantic DOM, landmark /
native-control / heading / status / focus-marker assertions, long-content,
320px and state fixtures, behavior-free adapter probes, and
lesson-compatible synthetic view data.

Deliberately imports no presentation module -- the shared presentation
adapter does not exist yet. The harness's self-checks run against synthetic
HTML and its own fixtures, so it is green from Wave 0 and later TDD tasks
add their failing feature assertions here first.

Standard library only, no test framework, runnable as
`python tests/presentation_roundtrip.py`.
"""
import html.parser, os, re, sys


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


# ---- stdlib HTML parsing into a semantic DOM --------------------------------

class Dom:
    """A parsed HTML document with semantic accessors used by every
    Phase 4 structural assertion. Built from `html.parser` only.
    """
    def __init__(self, markup):
        self._nodes = []
        self._stack = []
        self._text = []
        parser = _DomParser(self)
        try:
            parser.feed(markup)
            parser.close()
        except Exception as exc:
            fail("Dom could not parse markup: %r" % exc)

    def add(self, node):
        self._nodes.append(node)

    def push(self, node):
        self._stack.append(node)

    def pop(self):
        self._stack.pop()

    def current(self):
        return self._stack[-1] if self._stack else None

    def record_text(self, text):
        if self._stack:
            self._stack[-1]["text"] += text
        else:
            self._text.append(text)

    def all(self, name=None):
        if name is None:
            return list(self._nodes)
        return [n for n in self._nodes if n["tag"] == name]

    def find(self, name, **attrs):
        for n in self._nodes:
            if n["tag"] == name and all(n["attrs"].get(k) == v for k, v in attrs.items()):
                return n
        return None

    def headings(self):
        """`(level, text)` pairs for every h1-h6, in document order."""
        return [(int(n["tag"][1]), n["text"].strip())
                for n in self._nodes if re.match(r"^h[1-6]$", n["tag"])]

    def landmarks(self):
        """Semantic landmark nodes: main/nav/header/footer or role-marked."""
        out = []
        for n in self._nodes:
            role = n["attrs"].get("role")
            if n["tag"] in ("main", "nav", "header", "footer") or role in (
                    "main", "navigation", "banner", "contentinfo", "complementary"):
                out.append(n)
        return out

    def native_controls(self):
        """Native interactive controls (button/input/select/textarea/details)."""
        return [n for n in self._nodes
                if (n["tag"] in ("button", "input", "select", "textarea",
                                 "details", "summary")
                    or (n["tag"] == "a" and n["attrs"].get("href")))]

    def status_regions(self):
        """Persistent polite live regions: role=status or aria-live=polite."""
        out = []
        for n in self._nodes:
            role = n["attrs"].get("role")
            live = n["attrs"].get("aria-live")
            if role == "status" or live == "polite":
                out.append(n)
        return out

    def alert_regions(self):
        return [n for n in self._nodes if n["attrs"].get("role") == "alert"
                or n["attrs"].get("aria-live") == "assertive"]

    def details(self):
        return self.all("details")

    def buttons(self):
        return self.all("button")


class _DomParser(html.parser.HTMLParser):
    def __init__(self, dom):
        super().__init__(convert_charrefs=True)
        self._dom = dom

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "text": ""}
        self._dom.add(node)
        parent = self._dom.current()
        if parent is not None:
            parent.setdefault("children", []).append(node)
        if tag not in ("br", "img", "input", "hr", "meta", "link"):
            self._dom.push(node)

    def handle_startendtag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "text": ""}
        self._dom.add(node)

    def handle_endtag(self, tag):
        if self._dom.current() is not None and self._dom.current()["tag"] == tag:
            self._dom.pop()

    def handle_data(self, data):
        self._dom.record_text(data)


# ---- reusable structural assertions -----------------------------------------

def assert_single_h1(dom):
    hs = dom.headings()
    h1s = [h for h in hs if h[0] == 1]
    if len(h1s) != 1:
        fail("expected exactly one h1, found %d: %r" % (len(h1s), hs))


def assert_landmark(dom, kind=None):
    landmarks = dom.landmarks()
    if not landmarks:
        fail("no semantic landmark found")
    if kind is not None:
        tags = [n["tag"] for n in landmarks]
        roles = [n["attrs"].get("role") for n in landmarks]
        if kind not in tags and kind not in roles:
            fail("no %r landmark found; got tags=%r roles=%r"
                 % (kind, tags, roles))


def assert_status_region(dom):
    if not dom.status_regions():
        fail("no persistent role=status / aria-live=polite region found")


def assert_native_controls(dom, minimum=1):
    controls = dom.native_controls()
    if len(controls) < minimum:
        fail("expected at least %d native controls, found %d"
             % (minimum, len(controls)))
    for n in controls:
        tag = n["tag"]
        if tag not in ("button", "input", "select", "textarea", "details",
                       "summary", "a"):
            fail("non-native interactive element found: %r" % n)


def assert_heading_order(dom):
    """Headings descend without skipping levels (a11y contract)."""
    last = 0
    for level, _ in dom.headings():
        if last and level > last + 1:
            fail("heading level skipped from h%d to h%d" % (last, level))
        last = level


def focus_visible_rules(css):
    """Every `:focus-visible { ... }` declaration block in a CSS string."""
    return re.findall(r"[^{}]*:focus-visible[^{}]*\{[^{}]*\}", css)


def reduced_motion_block(css):
    """The `@media (prefers-reduced-motion: reduce) { ... }` block, or None."""
    m = re.search(r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{", css)
    if not m:
        return None
    return css[m.end():]


# ---- long-content / 320px / state fixtures ----------------------------------

def long_text_fixture(kind):
    """Deterministic long stems/objectives/options for overflow backstops."""
    word = "content"
    text = " ".join("%s-%d" % (word, i) for i in range(60))
    return {"stem": text, "objective": text, "option": text, "context": text}[kind]


def state_fixture(state):
    """Synthetic view-model data for the quiz states the UI-SPEC matrix names.
    Data only -- no presentation module, no scorer, no keys.
    """
    fixtures = {
        "loading": {"status": "loading", "label": "Loading…",
                    "controls_enabled": False},
        "checking": {"status": "checking", "label": "Checking answer…",
                     "controls_enabled": False, "submitted": True},
        "completed": {"status": "completed", "summary": {"correct": 4, "total": 5},
                      "action": {"label": "View report", "href": "/report"}},
        "empty": {"status": "empty", "label": "No items match this sitting.",
                  "action": {"label": "Filters / settings"}},
        "error": {"status": "error", "label":
                  "Couldn't check that answer. Your selection is still here.",
                  "action": {"label": "Try again"}},
        "unavailable": {"status": "unavailable", "label":
                        "This session has no question ready.",
                        "action": {"label": "View report", "href": "/report"}},
    }
    if state not in fixtures:
        fail("state_fixture has no %r entry" % state)
    return fixtures[state]


def lesson_view_fixture():
    """Lesson-compatible synthetic view data (Phase 3 shapes only -- no lesson
    behavior is added by this harness).
    """
    return {
        "title": "Synthetic lesson",
        "headings": [{"slug": "introduction", "text": "Introduction"},
                     {"slug": "practice", "text": "Practice"}],
        "links": [{"slug": "practice", "item_id": "sentinel-mc-0001"}],
        "code": {"language": "python", "text": "print('hello')"},
        "table": {"headers": ["A", "B"], "rows": [["1", "2"]]},
        "body": long_text_fixture("stem"),
    }


def probe_adapter(adapter, data):
    """Behavior-free adapter probe: run `adapter(data)` and return
    `(ok, output)` -- captures whether a presentation adapter runs and what
    it produces, without asserting semantics (later plans supply the real
    adapters and the semantic assertions).
    """
    try:
        output = adapter(data)
    except Exception as exc:
        return False, exc
    return True, output


# ---- self-checks ------------------------------------------------------------

def check_parser_and_assertions():
    markup = (
        "<!doctype html><html><head><title>t</title></head><body>"
        "<header><h1>Stem</h1></header>"
        "<nav aria-label=\"Context\"><span>bank</span></nav>"
        "<main><form>"
        "<fieldset><legend>Choose</legend>"
        "<input type=\"radio\" name=\"a\" id=\"a\">"
        "<button type=\"submit\">Submit answer</button>"
        "<details><summary>Session details</summary><p>meta</p></details>"
        "</fieldset>"
        "<div role=\"status\" aria-live=\"polite\"></div>"
        "<div role=\"alert\"></div>"
        "</form></main></body></html>")
    dom = Dom(markup)
    assert_single_h1(dom)
    assert_landmark(dom, "main")
    assert_landmark(dom, "nav")
    assert_status_region(dom)
    assert_native_controls(dom, minimum=4)
    assert_heading_order(dom)
    if not dom.find("input", type="radio"):
        fail("parser did not retain input attrs")
    if len(dom.details()) != 1:
        fail("parser did not find the details element")
    if len(dom.alert_regions()) != 1:
        fail("parser did not find the role=alert region")
    hs = dom.headings()
    if hs != [(1, "Stem")]:
        fail("headings() returned %r, expected [(1, 'Stem')]" % hs)

    # A two-h1 document must trip the single-h1 assertion.
    try:
        assert_single_h1(Dom("<h1>a</h1><h1>b</h1>"))
    except SystemExit:
        pass
    else:
        fail("assert_single_h1 accepted a two-h1 document")


def check_css_hooks():
    css = ("a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}"
           "@media (prefers-reduced-motion:reduce){*{transition:none!important}}")
    rules = focus_visible_rules(css)
    if not any(":focus-visible" in r and "outline" in r for r in rules):
        fail("focus_visible_rules found no focus ring rule: %r" % rules)
    block = reduced_motion_block(css)
    if block is None or "transition" not in block:
        fail("reduced_motion_block did not capture the transition kill rule")
    if reduced_motion_block("p{color:red}") is not None:
        fail("reduced_motion_block matched a document without the media query")


def check_fixtures():
    for state in ("loading", "checking", "completed", "empty", "error",
                  "unavailable"):
        fixture = state_fixture(state)
        if not isinstance(fixture, dict) or "status" not in fixture:
            fail("state fixture %r is malformed: %r" % (state, fixture))
    lesson = lesson_view_fixture()
    if len(lesson["headings"]) < 1 or "slug" not in lesson["headings"][0]:
        fail("lesson fixture is malformed: %r" % lesson)
    for kind in ("stem", "objective", "option", "context"):
        if len(long_text_fixture(kind)) < 300:
            fail("long-text fixture %r is not long: %d chars"
                 % (kind, len(long_text_fixture(kind))))


def check_adapter_probe():
    ok, output = probe_adapter(lambda data: {"viewed": data["status"]},
                               state_fixture("loading"))
    if not ok or output != {"viewed": "loading"}:
        fail("probe_adapter failed on a working adapter: %r" % (output,))
    ok, output = probe_adapter(lambda data: 1 / 0, {})
    if ok or not isinstance(output, ZeroDivisionError):
        fail("probe_adapter did not capture an adapter exception")


def main():
    check_parser_and_assertions()
    check_css_hooks()
    check_fixtures()
    check_adapter_probe()
    print("ok: presentation Wave 0 harness -- semantic DOM parser, landmark/"
          "heading/status/native-control/focus/reduced-motion assertions, "
          "long-content/320px/state fixtures, behavior-free adapter probes "
          "and lesson-compatible synthetic data all self-check green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
