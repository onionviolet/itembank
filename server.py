"""One loopback HTTP server, shared by the surfaces that put a page in a browser.

Two surfaces serve a local page and take POSTs back: the graded sitting and the
day cockpit. Each carried its own socket bind, its own port fallback, its own
silenced request log and its own JSON reply. The duplication mattered more than
its line count: a port fallback that exists in two places is one that gets fixed
in one of them.

Nothing here listens on an external interface unless a surface asks for it, and
nothing leaves the machine.
"""
import http.server, json, os, socketserver, urllib.parse

# The 17A visual-direction tracer (plan 17A-01). It renders a synthetic fixture
# and nothing else: no bank, no session, no key, no evidence. It stays behind an
# explicit environment opt in so a learner running the app can never reach a
# prototype by guessing a URL, which is what 17A-UI-SPEC means by keeping the
# prototypes off the production surface.
VISUAL_FIXTURE_PREFIX = "/_visual-fixture"
VISUAL_FIXTURE_ENV = "ITEMBANK_VISUAL_FIXTURE"


def visual_fixture_enabled():
    return os.environ.get(VISUAL_FIXTURE_ENV, "") == "1"


def maybe_visual_fixture(handler, path):
    """Serve one direction of the 17A tracer, or return False and let the real
    router handle the path. Returns True only when it has written a response.

    The page is built by `visual_fixture.page`, which goes through
    `presentation.surface_shell`, so this route adds a URL and never a second
    document shell.
    """
    if not visual_fixture_enabled():
        return False
    parsed = urllib.parse.urlparse(path)
    if parsed.path != VISUAL_FIXTURE_PREFIX:
        return False

    from surfaces import visual_fixture

    query = urllib.parse.parse_qs(parsed.query)
    direction = (query.get("direction") or [visual_fixture.DEFAULT_DIRECTION])[0]
    nav_shape = (query.get("nav") or [visual_fixture.DEFAULT_NAV])[0]
    stage_id = (query.get("stage") or [None])[0]
    tokens = {k: v[0] for k, v in query.items()
              if k not in ("direction", "nav", "stage")}
    base = os.path.dirname(os.path.abspath(__file__))
    body = visual_fixture.page(visual_fixture.load_fixture(), direction, tokens,
                               stage_id=stage_id, nav_shape=nav_shape, base=base)
    handler.send_html(body.encode("utf-8"))
    return True


class Handler(http.server.BaseHTTPRequestHandler):
    """Base for a local surface. Subclasses add `do_GET` and `do_POST`."""

    def log_message(self, *args):
        pass                    # each surface prints its own progress line instead

    def read_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    def read_form(self):
        """A form-encoded POST body as {field: [values]} -- repeated keys
        (multi-select checkboxes in a gate band) keep every value, exactly
        like `urllib.parse.parse_qs`. Used by the gate band's
        `<form method="post">` (06.2-UI-SPEC section 6.1: one form, two
        named submit buttons, no JavaScript)."""
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode("utf-8") if n else ""
        return urllib.parse.parse_qs(raw, keep_blank_values=True)

    def send_redirect(self, location):
        """A 303 See Other to `location` -- the post-redirect-get pattern
        the gate routes use so a reload or a back-button press never
        re-submits a check or a skip (06.2-UI-SPEC section 7.1)."""
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def send_bytes(self, body, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, body, status=200):
        """`status` is for the pages that are a real HTTP failure and still
        need a usable body: a refused quiz submit comes back as the quiz page
        carrying the learner's own answer, under the status that says it did
        not go through."""
        self.send_bytes(body, "text/html; charset=utf-8", status)

    def send_json(self, payload):
        self.send_bytes(json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                        "application/json; charset=utf-8")


def bind(handler, port, host="127.0.0.1"):
    """Bind a server, falling back to an OS-assigned port.

    Windows reserves scattered port ranges for Hyper-V and WSL, so a fixed
    default can fail with a permission error that reads as a bug in this tool.
    Taking a free port beats making somebody diagnose WinError 10013.
    """
    try:
        return socketserver.TCPServer((host, port), handler)
    except OSError as exc:
        print("  port %d unavailable (%s), using a free one instead"
              % (port, exc.__class__.__name__))
        return socketserver.TCPServer((host, 0), handler)


def bind_tls(handler, port, host, certfile, keyfile):
    """Bind a server wrapped in stdlib `ssl` with a user-supplied cert/key
    (D-05, phase 999.4): the LTI surface's built-in TLS posture. Falls back
    to an OS-assigned port exactly like `bind`. The caller supplies the PEM
    cert and key paths; this function never generates, downloads, or holds a
    certificate itself (the tool never owns a domain or a CA account -- that
    is the reverse proxy's job).
    """
    import ssl

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile, keyfile)

    class _TLSServer(socketserver.TCPServer):
        def get_request(self):
            sock, addr = super().get_request()
            return context.wrap_socket(sock, server_side=True), addr

    try:
        return _TLSServer((host, port), handler)
    except OSError as exc:
        print("  port %d unavailable (%s), using a free one instead"
              % (port, exc.__class__.__name__))
        return _TLSServer((host, 0), handler)
