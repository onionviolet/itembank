"""Serve only the disposable CS Dojo assets on their own loopback origin."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/dojo.css": ("dojo.css", "text/css; charset=utf-8"),
    "/lessons.js": ("lessons.js", "text/javascript; charset=utf-8"),
    "/dojo.js": ("dojo.js", "text/javascript; charset=utf-8"),
    "/runner.js": ("runner.js", "text/javascript; charset=utf-8"),
    "/source.md": ("source.md", "text/plain; charset=utf-8"),
}
PAGE_CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; "
    "worker-src 'self'; connect-src 'none'; img-src 'none'; "
    "base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
)
WORKER_CSP = (
    "default-src 'none'; script-src 'unsafe-eval'; connect-src 'none'; "
    "worker-src 'none'; child-src 'none'; object-src 'none'"
)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        expected_host = f"127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host") != expected_host:
            self.send_error(403, "Open this prototype on its own loopback address")
            return
        asset = ASSETS.get(self.path)
        if asset is None:
            self.send_error(404)
            return
        filename, content_type = asset
        data = (ROOT / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("Content-Security-Policy", WORKER_CSP if filename == "runner.js" else PAGE_CSP)
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8774)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"CS Dojo: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
