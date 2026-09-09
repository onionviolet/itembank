"""Loopback-only, read-only demonstration of source-grounded selection.

This serves a fixed synthetic source. It does not read learner files, call a
model, write evidence, or accept course content.
"""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from grounding import build_grounded_payload, source_fingerprint

SOURCE = (
    "A rain gauge measures rainfall depth in millimeters.\n\n"
    "Compare readings over equal time intervals. Gauge A collected 12 mm "
    "in 24 hours and gauge B collected 18 mm in 24 hours. B received 6 mm more.\n\n"
    "Equal time intervals make these readings comparable. A reading over "
    "one hour and a reading over one day describe different intervals."
)
REVISION = source_fingerprint(SOURCE)
ROOT = Path(__file__).parent


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, value, kind="application/json"):
        raw = value.encode() if isinstance(value, str) else json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", kind + "; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/":
            return self.reply(200, (ROOT / "index.html").read_text(), "text/html")
        if self.path == "/api/source":
            return self.reply(200, {"text": SOURCE, "revision": REVISION})
        self.reply(404, {"code": "not_found"})

    def do_POST(self):
        if self.path != "/api/ground":
            return self.reply(404, {"code": "not_found"})
        origin = self.headers.get("Origin")
        expected_origin = "http://127.0.0.1:" + str(self.server.server_port)
        if origin and origin != expected_origin:
            return self.reply(403, {"code": "origin_not_allowed"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 32000:
                return self.reply(413, {"code": "request_too_large"})
            body = json.loads(self.rfile.read(size))
            if not isinstance(body, dict) or not all(
                isinstance(body.get(key), str) for key in ("selection", "revision")
            ):
                return self.reply(400, {"code": "invalid_request"})
            result = build_grounded_payload(
                trusted_text=SOURCE, source_id="synthetic-rainfall",
                locator="section:measurement", revision=REVISION,
                expected_fingerprint=body["revision"], selection=body["selection"],
                allow_read=True,
                selection_start=body.get("selection_start"),
                selection_end=body.get("selection_end"),
            )
            self.reply(200 if result.ok else 422, {"code": result.code, "payload": result.payload})
        except (ValueError, TypeError, UnicodeError):
            self.reply(400, {"code": "invalid_request"})

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8769)
    args = parser.parse_args()
    print(f"Source grounding prototype: http://127.0.0.1:{args.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
