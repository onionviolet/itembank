#!/usr/bin/env python3
"""Deterministic static HTML fixtures plus a loopback fetch server
(Phase 14C, plan 14C-04).

Roster item 3 in `14C-CONTEXT.md`: a web page becomes a citable source by
being captured, not by being pointed at (D-04). This module carries the
parsing half of that acceptance corpus as static bytes, and the fetching
half as a real `http.server` bound to loopback.

No case makes a real network request. The loopback server exists so the
redirect refusal, the header stripping, the timeout, the oversize cap, and
the private-origin refusal are proven against a real socket rather than a
mocked one: a mock proves that the code calls what the test expects it to
call, and these are exactly the behaviours where that is not the question.

Stdlib only (hashlib, http.server, io, os, threading, time) and
repository-independent: the case table is immutable data, the builders are
pure functions, and nothing here reads or writes the repository.

`expectation` is absent here for the same reason it is absent from
`pptx_fidelity_cases.py`: that key belongs to the Phase 11 auditor gate,
which enumerates `locator_fidelity_cases.CASE_TABLE` only. This file
carries `adapter_expectation`, `unsupported` exactly when `reading_order`
is empty.
"""
import hashlib
import http.server
import os
import socketserver
import threading
import time


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------------------
# static HTML builders
# ---------------------------------------------------------------------------

def _page(body, charset="utf-8", head_extra=""):
    return ('<!DOCTYPE html><html><head><meta charset="%s">%s'
            '<title>itembank fixture</title></head><body>%s</body></html>'
            % (charset, head_extra, body))


def article_html():
    return _page(
        '<nav><a href="/">Home</a><a href="/about">About</a></nav>'
        '<article><h1>Airway Management</h1>'
        '<p>Assess responsiveness first.</p>'
        '<p>Then open the airway.</p></article>'
        '<footer>Copyright the fixture.</footer>').encode("utf-8")


def article_changed_html():
    """The same document with one paragraph altered. Used by the recheck
    scenario, which needs the same URL to serve different bytes."""
    return _page(
        '<nav><a href="/">Home</a><a href="/about">About</a></nav>'
        '<article><h1>Airway Management</h1>'
        '<p>Assess responsiveness first.</p>'
        '<p>Then open the airway with a jaw thrust.</p></article>'
        '<footer>Copyright the fixture.</footer>').encode("utf-8")


def nested_sections_html():
    return _page(
        '<article>'
        '<section><h2>Oxygen delivery</h2>'
        '<p>A nasal cannula delivers a variable concentration.</p></section>'
        '<section><h2>Ventilation</h2>'
        '<p>A bag valve mask delivers a fixed volume.</p></section>'
        '</article>').encode("utf-8")


def duplicate_text_html():
    """The same sentence twice, in two different sections. A bare exact
    quote cannot tell the two apart, which is why every web locator carries
    a prefix and a suffix beside the exact text."""
    return _page(
        '<article>'
        '<section><h2>Adult</h2>'
        '<p>Reassess every five minutes.</p>'
        '<p>An adult airway is straight.</p></section>'
        '<section><h2>Paediatric</h2>'
        '<p>Reassess every five minutes.</p>'
        '<p>A child airway is narrower.</p></section>'
        '</article>').encode("utf-8")


def nonutf8_html():
    """Declared iso-8859-1 with a byte no UTF-8 decoder accepts on its own,
    so the charset path is exercised rather than assumed."""
    body = ('<article><h1>Pr\xe9paration</h1>'
            '<p>Le patient est stabilis\xe9.</p></article>')
    return _page(body, charset="iso-8859-1").encode("iso-8859-1")


def script_only_html():
    """The shape of a client-rendered page: a script and an empty mount."""
    return _page(
        '<div id="root"></div>'
        '<script>window.render();</script>').encode("utf-8")


def truncated_html():
    """An HTML document cut off mid-tag."""
    return article_html()[:120]


def huge_body(size):
    return b"<html><body><p>" + (b"x" * size) + b"</p></body></html>"


# ---------------------------------------------------------------------------
# the immutable case table
# ---------------------------------------------------------------------------

CASE_TABLE = [
    {
        "id": "web-article-simple",
        "kind": "web",
        "filename": "web-article.html",
        "build": article_html,
        "gold": {
            "sha256": "d77aee192b43b9f6e52a6273e1fef90b2a642c554c85e592f0357c931b5e2bae",
            "structures": [
                {"kind": "block", "index": 0, "text": "Airway Management"},
                {"kind": "block", "index": 1,
                 "text": "Assess responsiveness first."},
                {"kind": "block", "index": 2,
                 "text": "Then open the airway."},
            ],
            "reading_order": ["w.0", "w.1", "w.2"],
            "unsupported": [],
            "adapter_expectation": "supported",
        },
    },
    {
        "id": "web-article-nested-sections",
        "kind": "web",
        "filename": "web-nested.html",
        "build": nested_sections_html,
        "gold": {
            "sha256": "cdfaabeae2e604f89ec7761503e63a17e0e4923cad1d7f789b1e9451320b2739",
            "structures": [
                {"kind": "block", "index": 0, "text": "Oxygen delivery"},
                {"kind": "block", "index": 1,
                 "text": "A nasal cannula delivers a variable concentration."},
                {"kind": "block", "index": 2, "text": "Ventilation"},
                {"kind": "block", "index": 3,
                 "text": "A bag valve mask delivers a fixed volume."},
            ],
            "reading_order": ["w.0", "w.1", "w.2", "w.3"],
            "unsupported": [],
            "adapter_expectation": "supported",
        },
    },
    {
        "id": "web-duplicate-text",
        "kind": "web",
        "filename": "web-duplicate.html",
        "build": duplicate_text_html,
        "gold": {
            "sha256": "a28de87500e878b7b91f76bc2b5c6ec1a2123a554da7cbd7011fd5baa3a03101",
            "structures": [
                {"kind": "block", "index": 0, "text": "Adult"},
                {"kind": "block", "index": 1,
                 "text": "Reassess every five minutes."},
                {"kind": "block", "index": 2,
                 "text": "An adult airway is straight."},
                {"kind": "block", "index": 3, "text": "Paediatric"},
                {"kind": "block", "index": 4,
                 "text": "Reassess every five minutes."},
                {"kind": "block", "index": 5,
                 "text": "A child airway is narrower."},
            ],
            "reading_order": ["w.0", "w.1", "w.2", "w.3", "w.4", "w.5"],
            "unsupported": [],
            "adapter_expectation": "supported",
            # The two locators whose exact text is identical. Their prefixes
            # and their CSS selectors must differ or a citation into either
            # is ambiguous.
            "duplicate_pair": ["w.1", "w.4"],
        },
    },
    {
        "id": "web-nonutf8-charset",
        "kind": "web",
        "filename": "web-latin1.html",
        "build": nonutf8_html,
        "gold": {
            "sha256": "70cb8a1bd92b38204611d888e1f0842de0acb510ec59593ce748d9cdf8c4cf00",
            "structures": [
                {"kind": "block", "index": 0, "text": "Préparation"},
                {"kind": "block", "index": 1,
                 "text": "Le patient est stabilisé."},
            ],
            "reading_order": ["w.0", "w.1"],
            "unsupported": [],
            "adapter_expectation": "supported",
        },
    },
    {
        "id": "web-script-only",
        "kind": "web",
        "filename": "web-script.html",
        "build": script_only_html,
        "gold": {
            "sha256": "7a2cc34794465cac99dde81c562947f05f29b42340ed694a587b4208fc9af77b",
            "structures": [],
            "reading_order": [],
            "unsupported": ["no readable text: the page renders its content "
                            "with JavaScript"],
            "adapter_expectation": "unsupported",
        },
    },
    {
        "id": "web-malformed-truncated",
        "kind": "web",
        "filename": "web-truncated.html",
        "build": truncated_html,
        # The gold below was recorded from a real run rather than guessed;
        # the plan deliberately left it open. lxml's HTML parser recovers,
        # so a truncated document still parses, but this one is cut inside
        # the head before any content, so the readable fragment holds no
        # block with text and the honest gold is a refusal. It carries no
        # script element, which is what separates its message from the
        # client-rendered case's. See 14C-04-SUMMARY.md.
        "gold": {
            "sha256": "44ad71485838f4dc22f15c259f5eaf4d60df1a44708d3ccd4857a477cb5fc816",
            "structures": [],
            "reading_order": [],
            "unsupported": ["no readable text: malformed document"],
            "adapter_expectation": "unsupported",
        },
    },
]


def materialize(dest_dir):
    """Write every static case into `dest_dir` and return a list of
    (case_id, path, sha256_of_bytes) records."""
    os.makedirs(dest_dir, exist_ok=True)
    records = []
    for case in CASE_TABLE:
        raw = case["build"]()
        path = os.path.join(dest_dir, case["filename"])
        with open(path, "wb") as fh:
            fh.write(raw)
        records.append((case["id"], path, sha256(raw)))
    return records


# ---------------------------------------------------------------------------
# the loopback fetch fixture
# ---------------------------------------------------------------------------

ARTICLE_ETAG = '"fixture-etag-1"'
CHANGED_ETAG = '"fixture-etag-2"'
LAST_MODIFIED = "Wed, 01 Jan 2020 00:00:00 GMT"

HUGE_BYTES = 100000
SLOW_SECONDS = 3.0


def serve_cases():
    """Return a `BaseHTTPRequestHandler` subclass carrying the fixture route
    table. Class attributes the caller may set before or during a test:

    `article` -- the (bytes, etag) pair `/article` serves, so one URL can
    serve different bytes on a later request, which is what a staleness
    recheck actually faces.
    `cross_origin_url` -- the absolute URL `/redirect-cross-origin` points
    at, normally a second server on a different loopback port.
    `received_headers` -- every request's headers, appended, so a test can
    assert what a redirected request carried.

    The handler logs nothing, so a passing test prints nothing.
    """

    class FixtureHandler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"
        article = (article_html(), ARTICLE_ETAG)
        cross_origin_url = None
        received_headers = []

        def log_message(self, *args):
            return

        def _send(self, status, body, content_type="text/html; charset=utf-8",
                  extra=()):
            self.send_response(status)
            if content_type is not None:
                self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            for key, value in extra:
                self.send_header(key, value)
            self.end_headers()
            if body:
                self.wfile.write(body)

        def do_GET(self):
            type(self).received_headers.append(dict(self.headers.items()))
            path = self.path
            if path == "/article":
                body, etag = type(self).article
                if self.headers.get("If-None-Match") == etag:
                    self._send(304, b"", content_type=None,
                               extra=[("ETag", etag)])
                    return
                self._send(200, body,
                           extra=[("ETag", etag),
                                  ("Last-Modified", LAST_MODIFIED)])
                return
            if path == "/article-no-validator":
                self._send(200, type(self).article[0])
                return
            if path == "/article-changed":
                self._send(200, article_changed_html(),
                           extra=[("ETag", CHANGED_ETAG),
                                  ("Last-Modified", LAST_MODIFIED)])
                return
            if path == "/redirect-to-article":
                self._send(302, b"", extra=[("Location", "/article")])
                return
            if path == "/redirect-to-file":
                self._send(302, b"",
                           extra=[("Location", "file:///etc/passwd")])
                return
            if path == "/redirect-loop":
                self._send(302, b"",
                           extra=[("Location", "/redirect-loop")])
                return
            if path == "/redirect-cross-origin":
                self._send(302, b"",
                           extra=[("Location",
                                   type(self).cross_origin_url or "/article")])
                return
            if path == "/slow":
                time.sleep(SLOW_SECONDS)
                self._send(200, article_html())
                return
            if path == "/huge":
                self._send(200, huge_body(HUGE_BYTES))
                return
            self._send(404, b"<html><body>not found</body></html>")

    return FixtureHandler


class LoopbackServer(object):
    """A loopback `http.server` on an OS-assigned port, started in a daemon
    thread and stopped in a `finally`. Port 0 is deliberate: a busy port on
    the developer's machine must never make the suite flaky."""

    def __init__(self, handler_class=None):
        self.handler = handler_class or serve_cases()
        self.httpd = socketserver.TCPServer(("127.0.0.1", 0), self.handler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever,
                                       daemon=True)

    @property
    def url_base(self):
        return "http://127.0.0.1:%d" % self.port

    def url(self, path):
        return self.url_base + path

    def start(self):
        self.thread.start()
        return self

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc_info):
        self.stop()
        return False
