"""One loopback HTTP server, shared by the surfaces that put a page in a browser.

Two surfaces serve a local page and take POSTs back: the graded sitting and the
day cockpit. Each carried its own socket bind, its own port fallback, its own
silenced request log and its own JSON reply. The duplication mattered more than
its line count: a port fallback that exists in two places is one that gets fixed
in one of them.

Nothing here listens on an external interface unless a surface asks for it, and
nothing leaves the machine.
"""
import http.server, json, socketserver, urllib.parse


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

    def send_html(self, body):
        self.send_bytes(body, "text/html; charset=utf-8")

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
