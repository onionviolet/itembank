"""One loopback HTTP server, shared by the surfaces that put a page in a browser.

Two surfaces serve a local page and take POSTs back: the graded sitting and the
day cockpit. Each carried its own socket bind, its own port fallback, its own
silenced request log and its own JSON reply. The duplication mattered more than
its line count: a port fallback that exists in two places is one that gets fixed
in one of them.

Nothing here listens on an external interface unless a surface asks for it, and
nothing leaves the machine.
"""
import http.server, json, socketserver


class Handler(http.server.BaseHTTPRequestHandler):
    """Base for a local surface. Subclasses add `do_GET` and `do_POST`."""

    def log_message(self, *args):
        pass                    # each surface prints its own progress line instead

    def read_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

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
