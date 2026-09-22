"""Serve only the disposable CS Dojo assets on their own loopback origin."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENDORED_EDITOR = ROOT.parent.parent / "assets" / "vendor" / "codemirror" / "codemirror.bundle.js"
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/dojo.css": ("dojo.css", "text/css; charset=utf-8"),
    "/lessons.js": ("lessons.js", "text/javascript; charset=utf-8"),
    "/dojo.js": ("dojo.js", "text/javascript; charset=utf-8"),
    "/runner.js": ("runner.js", "text/javascript; charset=utf-8"),
    "/python-runner.js": ("python-runner.js", "text/javascript; charset=utf-8"),
    "/source.md": ("source.md", "text/plain; charset=utf-8"),
    "/codemirror.bundle.js": (VENDORED_EDITOR, "text/javascript; charset=utf-8"),
}
PYODIDE_FILES = {
    "pyodide.mjs": "text/javascript; charset=utf-8",
    "pyodide.asm.mjs": "text/javascript; charset=utf-8",
    "pyodide.asm.wasm": "application/wasm",
    "python_stdlib.zip": "application/zip",
    "pyodide-lock.json": "application/json; charset=utf-8",
    "LICENSE": "text/plain; charset=utf-8",
}
for name, content_type in PYODIDE_FILES.items():
    ASSETS[f"/vendor/pyodide/{name}"] = (f"vendor/pyodide/{name}", content_type)
PAGE_CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
    "worker-src 'self'; connect-src 'none'; img-src 'none'; "
    "base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
)
WORKER_CSP = (
    "default-src 'none'; script-src 'unsafe-eval'; connect-src 'none'; "
    "worker-src 'none'; child-src 'none'; object-src 'none'"
)
PYTHON_WORKER_CSP = (
    "default-src 'none'; script-src 'self' 'unsafe-eval' 'wasm-unsafe-eval'; "
    "connect-src 'self'; worker-src 'none'; child-src 'none'; object-src 'none'"
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
        data = (filename if isinstance(filename, Path) else ROOT / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        policy = PYTHON_WORKER_CSP if filename == "python-runner.js" else WORKER_CSP if filename == "runner.js" else PAGE_CSP
        self.send_header("Content-Security-Policy", policy)
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
