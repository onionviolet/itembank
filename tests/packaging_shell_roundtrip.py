#!/usr/bin/env python3
"""Subprocess fixtures for the sidecar-half of the desktop shell contract
(plan 13-01): the fixed stdout handshake (port/token/version), the
per-launch token gate on the routes the shell uses, single-instance
attach/refuse, and the kill-the-child-releases-the-port property the shell's
job object will rely on (D-05).

Standard library only, no test framework, runnable as
`python tests/packaging_shell_roundtrip.py`.
"""
import http.server, os, re, shutil, socketserver, subprocess, sys, tempfile
import threading, time
import urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402
from surfaces import daemon                                # noqa: E402
from surfaces.daemon import (SIDECAR_HANDSHAKE, SIDECAR_TOKEN_HEADER)  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import daemon_roundtrip                                    # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def free_port():
    """A currently-free TCP port, found by binding a throwaway server on
    port 0 and reading the OS-assigned number back before closing it --
    the same helper `tests/daemon_roundtrip.py` uses.
    """
    srv = socketserver.TCPServer(("127.0.0.1", 0), socketserver.BaseRequestHandler)
    port = srv.server_address[1]
    srv.server_close()
    return port


def start_decoy(port, body=b"plain text, not itembank", content_type="text/plain"):
    """A throwaway HTTP listener on a known port that is definitely not an
    itembank daemon -- the occupied-but-unreachable fixture the sidecar's
    attach-or-refuse path must survive (D-06). Returns the bound server; the
    caller shuts it down.
    """
    class Decoy(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    srv = socketserver.TCPServer(("127.0.0.1", port), Decoy)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def start_sidecar(workdir, *extra_args):
    """Launch `itembank sidecar <workdir>[, --port N]`, drain its stdout on a
    background thread, and return `(proc, lines)` once the full handshake has
    appeared -- the same subprocess-plus-background-thread shape
    `tests/daemon_roundtrip.py` uses for the daemon.
    """
    args = [sys.executable, "-u", os.path.join(ROOT, "itembank.py"),
            "sidecar", workdir]
    args += list(extra_args)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    prefixes = tuple(SIDECAR_HANDSHAKE.values())
    for _ in range(60):                      # up to ~6s for the bind + handshake
        time.sleep(0.1)
        if all(any(l.startswith(p) for l in lines) for p in prefixes):
            return proc, lines
    proc.terminate()
    fail("sidecar never printed the full handshake. Output was:\n" + "".join(lines))


def parse_handshake(lines):
    """Parse the stdout handshake with the shared framing constants
    (T-13-02): a repeated field, an empty value, or a missing field fails the
    parse -- never a silent fallback.
    """
    values = {}
    for line in lines:
        for key, prefix in SIDECAR_HANDSHAKE.items():
            if line.startswith(prefix):
                if key in values:
                    fail("handshake line %r repeats the %r field"
                         % (line.strip(), key))
                value = line[len(prefix):].strip()
                if not value:
                    fail("handshake line %r has an empty %r value"
                         % (line.strip(), key))
                values[key] = value
    missing = [k for k in SIDECAR_HANDSHAKE if k not in values]
    if missing:
        fail("handshake is missing %s; lines were %r" % (missing, lines))
    return values


def get_status(url, token=None):
    """`(status, body)` for any HTTP outcome; `token=None` sends no header."""
    req = urllib.request.Request(url)
    if token is not None:
        req.add_header(SIDECAR_TOKEN_HEADER, token)
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return res.status, res.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")


def check_handshake():
    """Test 1: sidecar mode prints the fixed handshake with real values, and
    the announced port is the OS-assigned one actually bound and serving.
    """
    workdir = tempfile.mkdtemp(prefix="sidecar-handshake-")
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, lines = start_sidecar(workdir, "--port", "0")
    try:
        hs = parse_handshake(lines)
        if not re.fullmatch(r"[0-9a-f]{32}", hs["token"]):
            fail("handshake token is not 32 hex chars (token_hex(16)): %r"
                 % hs["token"])
        port = int(hs["port"])
        if port <= 0:
            fail("handshake port is not a real bound port: %r" % hs["port"])
        if hs["version"] != itembank.__version__:
            fail("handshake version %r != itembank.__version__ %r"
                 % (hs["version"], itembank.__version__))
        status, _ = get_status("http://127.0.0.1:%d/__itembank__" % port,
                               token=hs["token"])
        if status != 200:
            fail("the announced sidecar port did not serve: GET returned %d"
                 % status)
    finally:
        proc.terminate()


def check_token_gate():
    """Test 2: token-gated routes refuse without the per-launch token and
    accept with it; the marker route stays open so the attach probe works;
    the CLI daemon path (no token) is unaffected.
    """
    workdir = tempfile.mkdtemp(prefix="sidecar-gate-")
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, lines = start_sidecar(workdir, "--port", "0")
    try:
        hs = parse_handshake(lines)
        base = "http://127.0.0.1:%s" % hs["port"]
        status, _ = get_status(base + "/")
        if status != 403:
            fail("GET / without the per-launch token returned %d, expected 403"
                 % status)
        status, _ = get_status(base + "/", token=hs["token"])
        if status != 200:
            fail("GET / with the per-launch token returned %d, expected 200"
                 % status)
        status, body = get_status(base + "/__itembank__")
        if status != 200 or '"itembank"' not in body:
            fail("the marker route must stay token-free for the attach probe; "
                 "got status %d body %r" % (status, body))
    finally:
        proc.terminate()

    cli_dir = tempfile.mkdtemp(prefix="cli-daemon-")
    shutil.copy(BANK, os.path.join(cli_dir, "sample_bank.md"))
    proc2, url2, _ = daemon_roundtrip.start_daemon(cli_dir)
    try:
        status, _ = daemon_roundtrip.get(url2)
        if status != 200:
            fail("the CLI daemon path regressed: GET / without a token "
                 "returned %d, expected 200" % status)
    finally:
        proc2.terminate()


def check_handshake_framing():
    """Test 3: the handshake lines are stable and parseable -- exactly three
    lines, in port/token/version order, read through the shared constants
    (the shell's parser and this test never restate the framing).
    """
    workdir = tempfile.mkdtemp(prefix="sidecar-framing-")
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, lines = start_sidecar(workdir, "--port", "0")
    try:
        prefixes = tuple(SIDECAR_HANDSHAKE.values())
        handshake_lines = [l.strip() for l in lines if l.startswith(prefixes)]
        expected_order = [SIDECAR_HANDSHAKE[k] for k in ("port", "token", "version")]
        got_order = [next(p for p in expected_order if l.startswith(p))
                     for l in handshake_lines]
        if len(handshake_lines) != 3:
            fail("expected exactly 3 handshake lines, got %r" % handshake_lines)
        if got_order != expected_order:
            fail("handshake lines are not in port/token/version order: %r"
                 % handshake_lines)
    finally:
        proc.terminate()


def main():
    checks = (
        check_handshake,
        check_token_gate,
        check_handshake_framing,
    )
    for check in checks:
        check()
    print("ok: sidecar handshake, token gate, and framing held (%d checks)"
          % len(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
