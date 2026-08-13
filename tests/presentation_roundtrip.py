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
import html.parser, hashlib, json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.error, urllib.request


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMBANK = os.path.join(ROOT, "itembank.py")
BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
PLAN = os.path.join(ROOT, "fixtures", "sample_plan.md")


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


# ---- plan 04-04 Task 2: shared daemon/presentation harness helpers --------

def start_theme_daemon(workdir):
    """Launch `itembank daemon <workdir> --no-open --port 0` and return
    `(proc, url, lines)` once the banner's URL is scraped -- the same
    subprocess pattern `tests/daemon_roundtrip.py` uses, kept local so this
    harness stays self-contained.
    """
    args = [sys.executable, "-u", ITEMBANK, "daemon", workdir,
            "--no-open", "--port", "0"]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    url = None
    for _ in range(60):
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            url = m.group(0)
            break
    if not url:
        proc.terminate()
        fail("presentation daemon never printed a URL:\n" + "".join(lines))
    return proc, url, lines


def theme_get(url):
    with urllib.request.urlopen(url, timeout=5) as res:
        return res.status, res.read().decode("utf-8")


def theme_json_post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def write_settings_file(base, overrides):
    """Write itembank.json into `base` from the schema defaults merged over
    `overrides`, through the existing validated settings writer.
    """
    sys.path.insert(0, ROOT)
    from surfaces import settings
    data = settings.load_settings(base)
    for dotted, value in overrides.items():
        node = data
        parts = dotted.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    settings.write_settings(base, data)


def style_css(html):
    """Every `<style>` block's content concatenated, in document order."""
    return "\n".join(re.findall(r"<style>(.*?)</style>", html, re.S))


def token_value(css, name):
    """The first `--name: value` token in a CSS string (`:root`'s block for
    a system/light document, the only block for a forced-mode document)."""
    m = re.search(r"--%s\s*:\s*([^;]+);" % re.escape(name), css)
    return m.group(1).strip() if m else None


# ---- plan 04-04 Task 2 tests ----------------------------------------------

def test_shared_accent_tokens_across_routes():
    """Test 1: index, report, settings, and served quiz all carry the same
    accent token values generated from the daemon root's settings.
    """
    sys.path.insert(0, ROOT)
    from surfaces.theme import derive_theme
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    shutil.copy(PLAN, os.path.join(workdir, "sample_plan.md"))
    write_settings_file(workdir, {"accent.source": "#c00040"})
    expected_light = derive_theme("#c00040")["light"]["accent"]
    expected_dark = derive_theme("#c00040")["dark"]["accent"]
    proc, url, lines = start_theme_daemon(workdir)
    try:
        pages = {}
        for route, path in (("/", ""), ("/settings", "settings"),
                            ("/quiz/sample_bank", "quiz/sample_bank")):
            status, body = theme_get(url + path)
            if status != 200:
                fail("GET %s returned %d, expected 200" % (route, status))
            pages[route] = body
        started = theme_json_post(url + "api/start",
                                  {"bank": "sample_bank", "count": 1, "seed": 0})
        if started[0] != 200:
            fail("api/start for the shared-token report failed: %r" % started)
        status, body = theme_get(url + "report?session=%s"
                                 % started[1]["session_id"])
        if status != 200:
            fail("GET /report returned %d, expected 200" % status)
        pages["/report"] = body
        for route, body in pages.items():
            css = style_css(body)
            light = token_value(css, "accent")
            if light != expected_light:
                fail("%s does not carry the shared light accent %s (got %r)"
                     % (route, expected_light, light))
            dark_m = re.search(r"prefers-color-scheme:dark", css)
            if not dark_m:
                fail("%s carries no system dark-mode branch" % route)
            dark = token_value(css[dark_m.end():], "accent")
            if dark != expected_dark:
                fail("%s does not carry the shared dark accent %s (got %r)"
                     % (route, expected_dark, dark))
    finally:
        proc.terminate()


def test_reload_after_save_updates_tokens():
    """Test 2: saving a new source then reloading each route returns the new
    tokens; already-open tabs are not asserted to update automatically.
    """
    sys.path.insert(0, ROOT)
    from surfaces.theme import derive_theme
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_theme_daemon(workdir)
    try:
        _, body = theme_get(url)
        before = token_value(style_css(body), "accent")
        status, resp = theme_json_post(url + "api/theme",
                                       {"action": "save", "source": "#c00040"})
        if status != 200 or resp.get("saved") is not True:
            fail("theme save failed: %r %r" % (status, resp))
        expected = derive_theme("#c00040")["light"]["accent"]
        for route, path in (("index", ""), ("settings", "settings"),
                            ("quiz", "quiz/sample_bank")):
            _, body = theme_get(url + path)
            got = token_value(style_css(body), "accent")
            if got != expected:
                fail("%s did not pick up the saved accent on reload "
                     "(got %r, expected %r)" % (route, got, expected))
        if before == expected:
            fail("sanity: the saved token must differ from the default")
    finally:
        proc.terminate()


def test_static_build_uses_settings_beside_bank():
    """Test 3: static `itembank build` reads settings beside the bank and
    uses the same generator; a missing settings file uses schema defaults.
    """
    sys.path.insert(0, ROOT)
    from surfaces.theme import derive_theme
    tmp = tempfile.mkdtemp()
    bank = os.path.join(tmp, "bank.md")
    shutil.copy(BANK, bank)
    write_settings_file(tmp, {"accent.source": "#123abc"})
    out = os.path.join(tmp, "quiz.html")
    r = subprocess.run([sys.executable, ITEMBANK, "build", bank, out],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True)
    if r.returncode != 0:
        fail("itembank build with settings failed: %s" % r.stdout)
    page = open(out, encoding="utf-8").read()
    expected = derive_theme("#123abc")["light"]["accent"]
    if token_value(style_css(page), "accent") != expected:
        fail("static build ignored the settings beside the bank")

    tmp2 = tempfile.mkdtemp()
    bank2 = os.path.join(tmp2, "bank.md")
    shutil.copy(BANK, bank2)
    out2 = os.path.join(tmp2, "quiz.html")
    r = subprocess.run([sys.executable, ITEMBANK, "build", bank2, out2],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True)
    if r.returncode != 0:
        fail("itembank build without settings failed: %s" % r.stdout)
    page2 = open(out2, encoding="utf-8").read()
    default = derive_theme("#0e6e62")["light"]["accent"]
    if token_value(style_css(page2), "accent") != default:
        fail("build without a settings file did not use schema defaults")


def test_forced_modes_preserve_semantic_tokens():
    """Test 4: forced light/dark and OS-system modes select the correct token
    blocks without changing semantic-state tokens.
    """
    sys.path.insert(0, ROOT)
    from surfaces.theme import SEMANTIC_TOKENS
    for mode, expected_bg in (("light", "#f3f5f4"), ("dark", "#0e1413")):
        workdir = tempfile.mkdtemp()
        shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
        write_settings_file(workdir, {"theme": mode, "accent.source": "#c00040"})
        proc, url, lines = start_theme_daemon(workdir)
        try:
            _, body = theme_get(url)
            css = style_css(body)
            if token_value(css, "bg") != expected_bg:
                fail("forced %s mode does not select the %s token block "
                     "(bg %r)" % (mode, mode, token_value(css, "bg")))
            for tok in ("ok", "bad", "warn"):
                got = token_value(css, tok)
                if got != SEMANTIC_TOKENS[mode][tok]:
                    fail("forced %s page changed semantic token %s: "
                         "got %r expected %r" % (mode, tok, got,
                                                 SEMANTIC_TOKENS[mode][tok]))
        finally:
            proc.terminate()

    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    write_settings_file(workdir, {"theme": "system", "accent.source": "#c00040"})
    proc, url, lines = start_theme_daemon(workdir)
    try:
        _, body = theme_get(url)
        css = style_css(body)
        if "prefers-color-scheme:dark" not in css:
            fail("system mode does not carry the dark-mode media branch")
    finally:
        proc.terminate()


def test_default_adapter_structure_and_alternate_adapter():
    """Test 5: the default adapter emits one h1, landmarks, native
    controls, visible-focus hooks, a persistent polite status region, and
    intact fallback content; a dummy alternate adapter receives the same
    behavior-free view data without any scorer/session/path object.
    """
    sys.path.insert(0, ROOT)
    from surfaces import presentation
    view = {
        "title": "Synthetic step",
        "back": {"href": "/", "label": "itembank"},
        "context": ["Alpha bank", "Item 1 of 2"],
        "step": {"label": "Read and answer", "prompt": "Choose one.",
                 "body": "Body prose here.",
                 "status": "Ready.",
                 "action": {"label": "Submit answer", "href": "/next"},
                 "details": [{"summary": "More details", "body": "Detail body"}]},
        "state": {"kind": "ok", "status": "Recorded."},
    }
    html = presentation.render_surface(view)
    dom = Dom(html)
    assert_single_h1(dom)
    assert_landmark(dom, "main")
    assert_status_region(dom)
    assert_native_controls(dom, minimum=3)
    assert_heading_order(dom)
    if not dom.find("nav", **{"data-surface-context": None}):
        fail("default adapter emits no data-surface-context nav")
    css = style_css(html)
    if not focus_visible_rules(css):
        fail("default adapter CSS carries no visible-focus hooks")
    if reduced_motion_block(css) is None:
        fail("default adapter CSS carries no reduced-motion block")
    for needle in ("Body prose here.", "Detail body", "Submit answer",
                   "Recorded."):
        if needle not in html:
            fail("default adapter dropped fallback content %r" % needle)

    received = {}

    def alt(view_data):
        received["view"] = view_data
        return "<main>alternate</main>"

    out = presentation.render_surface(view, adapter=alt)
    if out != "<main>alternate</main>":
        fail("an alternate adapter's output was not honored: %r" % out)
    if received.get("view") is not view:
        fail("the alternate adapter did not receive the same view data")
    for banned in ("score", "key", "session_id", "path", "writer"):
        if banned in json.dumps(view):
            fail("view data carries a behavior object field: %r" % banned)


def test_index_and_report_state_copy():
    """Test 6: index distinguishes no configured banks/plans; report renders
    the exact empty and partial-review copy with plain labels, tabular
    numbers, and visible evidence/provenance.
    """
    workdir = tempfile.mkdtemp()
    proc, url, lines = start_theme_daemon(workdir)
    try:
        status, body = theme_get(url)
        if status != 200:
            fail("empty index returned %d" % status)
        if "Nothing to serve here yet" not in body:
            fail("empty index lost its documented empty-state heading")
    finally:
        proc.terminate()

    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_theme_daemon(workdir)
    try:
        started = theme_json_post(url + "api/start",
                                  {"bank": "sample_bank", "count": 1, "seed": 8})
        if started[0] != 200:
            fail("api/start for the report states failed: %r" % started)
        session_id = started[1]["session_id"]
        status, body = theme_get(url + "report?session=%s" % session_id)
        if "Nothing has been answered yet." not in body:
            fail("empty report does not render the exact empty copy")
        if "<table" in body:
            fail("empty report renders an objective table")
        resp = theme_json_post(url + "api/submit",
                               {"session_id": session_id, "answer": "prose"})
        if resp[0] != 200:
            fail("short-answer submit for the partial report failed: %r" % resp)
        status, body = theme_get(url + "report?session=%s" % session_id)
        if "Some responses still need review. Auto-graded totals exclude them." not in body:
            fail("partial report is missing the exact partial-review copy")
        if 'data-field="pending_manual"' not in body:
            fail("partial report lost the pending-manual tabular figure")
        if 'data-field="pct"' not in body:
            fail("populated report lost its plain tabular headline")
        if "data-provenance" not in body:
            fail("populated report has no visible evidence/provenance marker")
    finally:
        proc.terminate()


def test_lesson_compatible_prose_view():
    """Test 7: a synthetic lesson-compatible prose view uses the same 720px
    shell, heading/link/code/table overflow rules and disclosures without
    adding lesson parsing, media, subject rendering, or Phase 3 behavior.
    """
    sys.path.insert(0, ROOT)
    from surfaces import presentation
    lesson = lesson_view_fixture()
    html = presentation.render_surface({
        "title": lesson["title"],
        "back": {"href": "/", "label": "itembank"},
        "step": {"label": lesson["title"], "body": lesson["body"],
                 "action": {"label": "Start studying questions",
                            "href": "/quiz/sample_bank"},
                 "details": [{"summary": lesson["headings"][0]["text"],
                              "body": "Heading prose"}]},
    })
    css = style_css(html)
    if not re.search(r"\.surface\{[^}]*max-width:720px", css):
        fail("lesson-compatible shell does not use the 720px measure")
    if "overflow-wrap:anywhere" not in css:
        fail("lesson-compatible shell has no long-content overflow protection")
    if "overflow-x:auto" not in css:
        fail("lesson-compatible shell has no code/table overflow rules")
    if "<details" not in html:
        fail("lesson-compatible view has no native disclosure")
    for banned in ("<canvas", "<video", "<audio", "parse_lesson",
                   "lesson_parser"):
        if banned in html:
            fail("lesson-compatible adapter added %r behavior" % banned)


def test_responsive_zoom_and_noscript_fallback():
    """Test 8: the shell, settings preview, report table wrapper, context
    line, and recovery panels stay usable at 320px/200% zoom without
    page-level horizontal scroll; reduced-motion and no-script cases retain
    the semantic fallback.
    """
    sys.path.insert(0, ROOT)
    from surfaces import presentation
    html = presentation.render_surface({
        "title": "Responsive",
        "back": {"href": "/", "label": "itembank"},
        "context": ["A very long context line value that must wrap",
                    "Item 12 of 120"],
        "step": {"label": "Prompt", "body": "Body", "status": "Ready",
                 "action": {"label": "Go", "href": "/go"}},
        "state": {"kind": "bad",
                  "status": "Couldn't check that answer. Your selection is still here."},
        "noscript": ("This page uses JavaScript only for enhanced "
                     "interaction; the served content remains available."),
    })
    css = style_css(html)
    if "@media (max-width:767px)" not in css:
        fail("no narrow-width breakpoint for 320px usability")
    if "min-width:0" not in css:
        fail("no overflow-safe layout rule for 320px/200% zoom")
    if reduced_motion_block(css) is None:
        fail("no reduced-motion fallback")
    if "<noscript>" not in html:
        fail("no no-script semantic fallback")
    if "Your selection is still here." not in html:
        fail("recovery panel copy was dropped")


def test_teaching_step_primary_action_contract():
    """Test 9: synthetic quiz/study/lesson views express a concise
    step/prompt, immediate status slot, optional progressive details, and
    exactly one primary next action; secondary actions cannot acquire the
    primary marker and the adapter adds no sequencing/pedagogy behavior.
    """
    sys.path.insert(0, ROOT)
    from surfaces import presentation
    html = presentation.render_surface({
        "title": "Step",
        "step": {"label": "A concise step", "prompt": "Choose one.",
                 "body": "Body.", "status": "Ready.",
                 "action": {"label": "Primary", "href": "/go"},
                 "secondary": [{"label": "Secondary one", "href": "/s1"},
                               {"label": "Secondary two"}]},
    })
    if html.count("data-action-primary") != 1:
        fail("teaching_step renders %d primary markers, expected exactly one"
             % html.count("data-action-primary"))
    if html.count("data-action-secondary") != 2:
        fail("teaching_step renders %d secondary markers, expected 2"
             % html.count("data-action-secondary"))
    if "role=\"status\"" not in html:
        fail("teaching_step has no immediate status slot")
    if "<script" in html:
        fail("the adapter generated sequencing/pedagogy script")
    m = re.search(r'<a[^>]*data-action-primary[^>]*>(.*?)</a>', html, re.S)
    if not m or "Primary" not in m.group(1):
        fail("the primary marker is attached to the wrong action")
    for sec in re.findall(r'<a[^>]*data-action-secondary[^>]*>(.*?)</a>',
                          html, re.S):
        if "Primary" in sec:
            fail("a secondary action acquired the primary marker")
    if "Choose one." not in html:
        fail("the concise prompt was dropped")


# ---- plan 03.1-01 Task 1: reading-surface voice/measure/leading tokens ----

def test_voice_measure_leading_tokens_ship_in_shared_css():
    """Test 1: the reading surface's five new design tokens land in
    SHARED_CSS with the exact values 03.1-UI-SPEC §2 / §7.1 lock, as
    RETUNED by 14-UI-SPEC §4.3 against the faces that now actually render.

    The two measures moved from 66ch/90ch to 59ch/80ch and this fixture
    moved with them, deliberately and not by weakening: `1ch` is the advance
    of `0` (0.500 em in Source Serif 4) while the frequency-weighted average
    character in running prose is 0.447 em, so the old `66ch` set 74 real
    characters per line -- past the 72-character ceiling `.planning/UI-SPEC.md`
    §8 states. The token names and their stated intent are unchanged; only
    the numbers that express that intent moved. `--leading-lesson:1.65` is
    re-confirmed by measurement (§4.5) and does NOT move.
    """
    sys.path.insert(0, ROOT)
    from surfaces.presentation import SHARED_CSS
    for want in ("--font-paper", "--font-ledger", "--measure-prose:59ch",
                 "--measure-wide:80ch", "--leading-lesson:1.65"):
        if want not in SHARED_CSS:
            fail("SHARED_CSS must carry %r (03.1-UI-SPEC §2, §7.1)" % want)


def test_font_tokens_name_fallbacks_and_only_presentation_names_families():
    """Test 2: the fallback stacks name Georgia and ui-monospace, and the
    vendored face names exist only inside surfaces/presentation.py — every
    other surface references fonts by token, never by literal family."""
    sys.path.insert(0, ROOT)
    from surfaces.presentation import SHARED_CSS
    if "Georgia" not in SHARED_CSS or "ui-monospace" not in SHARED_CSS:
        fail("--font-paper/--font-ledger must carry the no-vendor fallbacks "
             "Georgia and ui-monospace")
    for name in ("Source Serif 4", "iA Writer Quattro"):
        for root, _dirs, files in os.walk(os.path.join(ROOT, "surfaces")):
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(root, fn)
                if os.path.basename(path) == "presentation.py":
                    continue
                src = open(path, encoding="utf-8").read()
                if name in src:
                    fail("vendored face %r must be named only by "
                         "presentation.py, found in %s" % (name, path))


def test_no_hex_literal_added_to_shared_css():
    """Test 3: the token additions introduce no color literal — a hex in
    presentation.py would be a second palette (03.1-UI-SPEC §5)."""
    sys.path.insert(0, ROOT)
    from surfaces.presentation import SHARED_CSS
    if re.search(r"#[0-9a-fA-F]{3,8}\b", SHARED_CSS):
        fail("SHARED_CSS must contain no hex color literal")


# ---- plan 03.1-06 Task 1: vendored font records (supply chain) -------------

FONT_DIRS = ("source-serif", "ia-writer-quattro")


def load_manifest():
    """fonts/MANIFEST.json, the phase's supply-chain gate: the four
    Registry-Safety preconditions live here or the vendoring did not
    happen."""
    path = os.path.join(ROOT, "fonts", "MANIFEST.json")
    if not os.path.exists(path):
        fail("fonts/MANIFEST.json is missing -- the vendoring records are "
             "the supply-chain gate (plan 03.1-06 Task 1)")
    return json.load(open(path, encoding="utf-8"))


def test_font_vendoring_records_and_staging():
    """Test 1 + Test 3: each vendored font directory carries its OFL 1.1
    license, a RESERVED-NAMES note naming the reserved font names, and a
    MANIFEST row with the pinned tag and sha256; build.py STAGE_DIRS
    includes fonts/ so the artifact ships the families."""
    man = load_manifest()
    families = man.get("families") or {}
    for key in FONT_DIRS:
        d = os.path.join(ROOT, "fonts", key)
        if not os.path.isdir(d):
            fail("fonts/%s must exist with license and reserved-names "
                 "records beside the vendored files" % key)
        if not os.path.exists(os.path.join(d, "LICENSE.md")):
            fail("fonts/%s must carry the OFL 1.1 license text" % key)
        if not os.path.exists(os.path.join(d, "RESERVED-NAMES.md")):
            fail("fonts/%s must carry a RESERVED-NAMES note" % key)
        rn = open(os.path.join(d, "RESERVED-NAMES.md"),
                  encoding="utf-8").read()
        row = families.get(key)
        if not row:
            fail("MANIFEST must have a family row for %s" % key)
        if not row.get("tag"):
            fail("MANIFEST row %s must record the pinned tag" % key)
        for name in row.get("reserved_font_names") or []:
            if name not in rn:
                fail("RESERVED-NAMES note must name %r for %s" % (name, key))
        if not row.get("files"):
            fail("MANIFEST row %s must list its woff2 files" % key)
        for fr in row["files"]:
            if not fr.get("name") or not fr.get("url"):
                fail("MANIFEST file row %r must name the file and its "
                     "pinned URL" % fr)
    rs = man.get("registry_safety") or {}
    for want in ("preconditions_recorded", "cleartype_render_check"):
        if want not in rs:
            fail("MANIFEST must record Registry-Safety precondition %r"
                 % want)
    src = open(os.path.join(ROOT, "build.py"), encoding="utf-8").read()
    if re.search(r"STAGE_DIRS\s*=\s*\([^)]*fonts", src) is None:
        fail("build.py STAGE_DIRS must include fonts/ so the artifact ships "
             "the families")


def test_font_sha256_matches_bytes_or_defers_honestly():
    """Test 2: when the woff2 is on disk, the recorded SHA-256 must equal
    the recomputed digest of the fetched bytes; a deferred fetch must be
    recorded in MANIFEST with a re-run pointer and the no-vendor fallback
    (Georgia/ui-monospace) kept -- never a silent byte, never an unofficial
    URL."""
    man = load_manifest()
    fetch = man.get("fetch") or {}
    if fetch.get("status") == "deferred":
        if not fetch.get("rerun"):
            fail("a deferred fetch must record a re-run pointer in "
                 "MANIFEST (plan 03.1-06 Task 1 acceptance)")
        return
    for key in FONT_DIRS:
        for fr in man["families"][key]["files"]:
            p = os.path.join(ROOT, "fonts", key, fr["name"])
            if not os.path.isfile(p):
                fail("woff2 %s is missing from fonts/%s" % (fr["name"], key))
            digest = hashlib.sha256(open(p, "rb").read()).hexdigest()
            if digest != fr.get("sha256"):
                fail("sha256 for fonts/%s/%s recorded %r but bytes compute "
                     "%r" % (key, fr["name"], fr.get("sha256"), digest))


# ---- plan 03.1-06 Task 2: @font-face rules in the token layer -------------

def font_faces(css):
    """The `@font-face{...}` declaration bodies in a CSS string."""
    return re.findall(r"@font-face\{([^{}]*)\}", css)


# The daemon's font asset route prefix. `@font-face` srcs are root-absolute
# under it so a nested page route (`/lesson/<stem>`) cannot resolve them
# against the route and 404; the same constant is asserted against
# `surfaces.daemon.FONT_ASSET_PREFIX` by tests/stylesheet_roundtrip.py.
FONT_URL_PREFIX = "/assets/fonts/"


def test_at_font_face_rules_in_token_layer():
    """Test 1: SHARED_CSS carries @font-face rules whose family names are
    exactly the faces --font-paper/--font-ledger resolve to, each src points
    at a MANIFEST-recorded woff2 under fonts/, and every face ships
    font-display:swap."""
    sys.path.insert(0, ROOT)
    from surfaces.presentation import SHARED_CSS
    faces = font_faces(SHARED_CSS)
    if not faces:
        fail("SHARED_CSS must contain @font-face rules for the vendored "
             "faces (plan 03.1-06 Task 2)")
    families = set()
    srcs = []
    for body in faces:
        fm = re.search(r"font-family:\s*\"([^\"]+)\"", body)
        sm = re.search(r"url\(\s*\"([^\"]+)\"\s*\)\s*format\(\s*\"woff2\"\s*\)",
                       body)
        if not fm or not sm:
            fail("each @font-face must declare a quoted family and a woff2 "
                 "url: %r" % body)
        if "font-display:swap" not in body:
            fail("each @font-face must ship font-display:swap: %r" % body)
        families.add(fm.group(1))
        srcs.append(sm.group(1))
    if families != {"Source Serif 4", "iA Writer Quattro"}:
        fail("@font-face families must be exactly the two vendored faces, "
             "got %r" % families)
    paper = token_value(SHARED_CSS, "font-paper")
    ledger = token_value(SHARED_CSS, "font-ledger")
    if not paper.startswith('"Source Serif 4",'):
        fail("--font-paper must prefer the vendored face first: %r" % paper)
    if not ledger.startswith('"iA Writer Quattro",'):
        fail("--font-ledger must prefer the vendored face first: %r" % ledger)
    # The srcs are root-absolute under the daemon's font asset prefix (the
    # fix for the nested-route 404: a relative url resolved against
    # /lesson/<stem> rather than against the site root). The expected set is
    # built in that form from the same MANIFEST rows the daemon's closed
    # FONT_ASSETS map is built from.
    man = load_manifest()
    recorded = set()
    for key in FONT_DIRS:
        for fr in man["families"][key]["files"]:
            recorded.add(FONT_URL_PREFIX + "%s/%s" % (key, fr["name"]))
    for s in srcs:
        if s not in recorded:
            fail("@font-face src %r does not match a MANIFEST-recorded file "
                 "under %r" % (s, FONT_URL_PREFIX))


def test_font_faces_degrade_when_fonts_absent():
    """Test 2: with the vendored font files absent (temporarily hidden),
    the token stack still carries the Georgia/ui-monospace fallback after
    the vendored face -- the @font-face rules degrade (their srcs resolve
    to nothing) and no literal family lives outside presentation.py. Only
    the font FILES are hidden, never the whole fonts/ directory, so the
    test also runs on mounts where the vendoring directory itself is held
    open by another process."""
    sys.path.insert(0, ROOT)
    from surfaces.presentation import SHARED_CSS
    faces = font_faces(SHARED_CSS)
    if not faces:
        fail("no @font-face rules to test for absence degradation")
    srcs = [re.search(r"url\(\s*\"([^\"]+)\"", f).group(1) for f in faces]
    for s in srcs:
        if not s.startswith(FONT_URL_PREFIX):
            fail("font-face src escapes the font asset route %r: %r"
                 % (FONT_URL_PREFIX, s))
    # The url is root-absolute, so the checked-in file it names is the same
    # last path segments under fonts/ -- the shape the daemon's closed map
    # also resolves.
    paths = [os.path.join(ROOT, "fonts", *s[len(FONT_URL_PREFIX):].split("/"))
             for s in srcs]
    moved = []
    try:
        for p in paths:
            if os.path.exists(p):
                os.rename(p, p + ".absent-plan-03-1-06")
                moved.append(p)
        for p in paths:
            if os.path.exists(p):
                fail("font file present during the absence test: %r" % p)
        paper = token_value(SHARED_CSS, "font-paper")
        ledger = token_value(SHARED_CSS, "font-ledger")
        if not paper.startswith('"Source Serif 4",') or "Georgia" not in paper:
            fail("--font-paper must keep the Georgia fallback after the "
                 "vendored face: %r" % paper)
        if not ledger.startswith('"iA Writer Quattro",') \
                or "ui-monospace" not in ledger:
            fail("--font-ledger must keep the ui-monospace fallback after "
                 "the vendored face: %r" % ledger)
    finally:
        for p in moved:
            os.rename(p + ".absent-plan-03-1-06", p)


def test_no_family_literal_in_surface_templates():
    """Test 3: lesson.py, study.py, day.py and quiz_page.py carry no
    font-family literal naming a vendored family after this task; family
    names exist only inside the token layer (03.1-UI-SPEC §2, §7.4)."""
    for fn in ("lesson.py", "study.py", "day.py", "quiz_page.py"):
        path = os.path.join(ROOT, "surfaces", fn)
        if not os.path.exists(path):
            continue
        src = open(path, encoding="utf-8").read()
        for decl in re.findall(r"font-family:\s*([^;}\"\n]+)", src):
            if "Source Serif" in decl or "iA Writer" in decl:
                fail("%s declares a vendored family literally: %r"
                     % (fn, decl.strip()))


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
    test_shared_accent_tokens_across_routes()
    test_reload_after_save_updates_tokens()
    test_static_build_uses_settings_beside_bank()
    test_forced_modes_preserve_semantic_tokens()
    test_default_adapter_structure_and_alternate_adapter()
    test_index_and_report_state_copy()
    test_lesson_compatible_prose_view()
    test_responsive_zoom_and_noscript_fallback()
    test_teaching_step_primary_action_contract()
    test_voice_measure_leading_tokens_ship_in_shared_css()
    test_font_tokens_name_fallbacks_and_only_presentation_names_families()
    test_font_vendoring_records_and_staging()
    test_font_sha256_matches_bytes_or_defers_honestly()
    test_at_font_face_rules_in_token_layer()
    test_font_faces_degrade_when_fonts_absent()
    test_no_family_literal_in_surface_templates()
    test_no_hex_literal_added_to_shared_css()
    print("ok: presentation Wave 0 harness -- semantic DOM parser, landmark/"
          "heading/status/native-control/focus/reduced-motion assertions, "
          "long-content/320px/state fixtures, behavior-free adapter probes, "
          "lesson-compatible synthetic data, and the plan 04-04 shared "
          "palette/adapter contract all self-check green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
