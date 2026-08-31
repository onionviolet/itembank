#!/usr/bin/env python3
"""One mock provider, reachable three ways, so backend parity is proven rather
than asserted.

AGENT-02 requires the same operation to run through a hosted backend and a
local one and produce identical artifacts and journals. That claim is only
worth something if both backends compute the same answer, so this fixture
defines the candidate builder exactly once and exposes it through a stdin CLI
(the `hosted_cli` transport) and an HTTP POST handler (the
`openai_compatible` transport). A parity test that used two different builders
would be testing its own fixtures.

`candidate_for` is a fixed rule over the request: no randomness, no clock read,
no environment read. Two calls with the same request return equal dicts, which
is what lets a tracer assert byte-identical artifacts across transports.

All content is fictional. No real course, book, learner, or bank content of any
kind appears here.
"""
import json
import sys


def candidate_for(request):
    """One recommendation candidate, valid against
    `schemas/treatment_recommendation.schema.json`, built by a fixed rule.

    The rule is arbitrary but total: it must produce a valid candidate for
    every well-formed request, including one with no source spans, because the
    no-spans case is how a `missing` coverage state gets exercised.
    """
    inner = (request.get("payload") or {}).get("recommendation_request") or {}
    kinds = list(inner.get("treatment_kinds") or ())
    statement = inner.get("objective_statement") or ""
    spans = list(inner.get("source_spans") or ())

    index = len(statement) % 11 if kinds else 0
    treatment_kind = kinds[index] if kinds else ""

    # One deterministic per-subject branch. A blueprint objective's best
    # treatment is reading the blueprint, so this provider recommends
    # direct-reading for the blueprint course and the index rule for every
    # other. Keyed on the objective statement rather than a course id, because
    # course ids are minted per build and a fixture that keyed on one could
    # never be deterministic across two builds.
    if "Beacon" in statement and "direct-reading" in kinds:
        treatment_kind = "direct-reading"
        index = kinds.index("direct-reading")
    alternatives = [
        {"treatment_kind": kinds[(index + n) % len(kinds)],
         "confidence": "low"}
        for n in (1, 2)] if kinds else []

    if spans:
        first = spans[0]
        coverage = {"state": "covered",
                    "locator": first.get("locator") or "",
                    "confidence": "medium",
                    "source_object_id": first.get("source_object_id") or "",
                    "match_kind": "locator"}
    else:
        coverage = {"state": "missing", "locator": "", "confidence": "medium",
                    "source_object_id": "", "match_kind": "none"}

    return {
        "schema_version": 1,
        "objective_id": inner.get("objective_id") or "",
        "treatment_kind": treatment_kind,
        "rationale": ("Recommended from the supplied source spans. This "
                      "rationale is model synthesis, not a source passage."),
        "synthesis": True,
        "confidence": "medium",
        "coverage": coverage,
        "alternatives": alternatives,
        "citations": [{"source_object_id": s.get("source_object_id") or "",
                       "locator": s.get("locator") or ""} for s in spans],
    }


def main_cli():
    """The `hosted_cli` transport's shape: one JSON object on stdin, one JSON
    object on stdout, exit 0."""
    request = json.loads(sys.stdin.read())
    sys.stdout.write(json.dumps(candidate_for(request), ensure_ascii=False,
                                sort_keys=True))
    return 0


def serve(host="127.0.0.1", port=0):
    """The `openai_compatible` transport's shape: POST a request, get the
    candidate back. Returns `(httpd, port)` with port 0 resolved to the bound
    port, so a caller never guesses a free one.
    """
    import http.server
    import socketserver

    class Handler(http.server.BaseHTTPRequestHandler):

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            request = json.loads(self.rfile.read(length).decode("utf-8"))
            body = json.dumps(candidate_for(request), ensure_ascii=False,
                              sort_keys=True).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            """Silence per-request logging; a fixture that prints to stderr
            makes a green test look noisy and a red one hard to read."""

    httpd = socketserver.TCPServer((host, port), Handler)
    return httpd, httpd.server_address[1]


if __name__ == "__main__":
    # --refuse is checked first: a profile whose command carries both flags is
    # a refusing profile, and a refusal that could be overridden by argument
    # order would not be a reliable fixture for adapter.provider_refused.
    if "--refuse" in sys.argv:
        sys.exit(3)
    if "--cli" in sys.argv:
        sys.exit(main_cli())
    sys.exit("usage: mock_backends.py --cli | --refuse")
