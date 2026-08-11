#!/usr/bin/env python3
"""The subprocess-level fixtures for the packaged-app sidecar contract
(phase 13, plan 13-01): the stdout handshake the Tauri shell parses, the
per-launch token gate on the shell-used API routes, the single-instance
attach/refuse behaviour, and the kill-the-parent lifecycle proof the shell's
job object will rely on.

The sidecar is not a new program. It is `itembank daemon --sidecar`: the
existing probe()/start_server() three-case startup, with a fixed stdout
handshake (bound port + per-launch token + version) and a loopback-only
token gate bolted on. Everything the shell needs to find and trust its
runtime crosses these stdout lines -- never a fixed-port assumption, never a
port scan (D-03, D-04). The framing constants are imported from
`surfaces.daemon`, so the shell parser and these tests read the same strings.

Standard library only, no test framework, runnable as
`python tests/packaging_shell_roundtrip.py`.
"""
import http.server, json, os, re, shutil, socket, socketserver, subprocess, sys
import tempfile, threading, time
import urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402
from surfaces import daemon                                # noqa: E402
from surfaces.daemon import SIDECAR_HANDSHAKE              # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def free_port():
    """A currently-free TCP port, found by binding a throwaway server on
    port 0 and reading the OS-assigned number back before closing it."""
    srv = socketserver.TCPServer(("127.0.0.1", 0), socketserver.BaseRequestHandler)
    port = srv.server_address[1]
    srv.server_close()
    return port


def parse_handshake(output):
    """Parse the sidecar handshake from its stdout using the SAME framing
    constants the shell's parser reads (SIDECAR_HANDSHAKE) -- a framing
    change is one edit in daemon.py, not a second protocol maintained here.
    Returns {port, token, version} with whatever lines have been seen.
    """
    hs = {}
    for line in output.splitlines():
        for field, prefix in SIDECAR_HANDSHAKE.items():
            if line.startswith(prefix + ":"):
                hs[field] = line[len(prefix) + 1:]
    return hs


def spawn_sidecar(workdir, *extra_args, wait=True):
    """Launch `itembank daemon <workdir> --sidecar --no-open --port 0`,
    drain stdout on a background thread, and return `(proc, handshake,
    lines)` once the fixed handshake has been parsed. `wait=True` also polls
    the bound port until the marker answers, so attach/lifecycle fixtures
    never race a still-starting server. Extra args are appended after the
    default `--port 0`; argparse keeps the last `--port`, so a caller can
    pin a known port.
    """
    args = [sys.executable, "-u", os.path.join(ROOT, "itembank.py"),
            "daemon", workdir, "--sidecar", "--no-open", "--port", "0"]
    args += list(extra_args)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    hs = None
    for _ in range(100):                       # up to ~10s for bind + handshake
        time.sleep(0.1)
        parsed = parse_handshake("".join(lines))
        if parsed:
            hs = parsed
            break
    if hs is None:
        proc.terminate()
        fail("sidecar never printed the handshake. Output was:\n" + "".join(lines))
    if wait:
        wait_serving(int(hs["port"]))
    return proc, hs, lines


def run_sidecar_once(workdir, *extra_args, timeout=15):
    """Launch the sidecar mode and wait for it to exit on its own -- for the
    attach and refusal cases, which are expected to terminate instead of
    serving. Returns `(returncode, output)`.
    """
    result = subprocess.run(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"),
         "daemon", workdir, "--sidecar", "--no-open"] + list(extra_args),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
    return result.returncode, result.stdout


def start_daemon(workdir, *extra_args):
    """Launch `itembank daemon <workdir> --no-open --port 0` -- the existing
    CLI daemon entry, no --sidecar -- and return `(proc, url, lines)` once
    the URL banner has been scraped (the CLI-path control for the token
    gate, and the daemon twin for the lifecycle fixture).
    """
    args = [sys.executable, "-u", os.path.join(ROOT, "itembank.py"),
            "daemon", workdir, "--no-open", "--port", "0"]
    args += list(extra_args)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    url = None
    for _ in range(60):                        # up to ~6s for the bind and banner
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            url = m.group(0)
            break
    if not url:
        proc.terminate()
        fail("daemon never printed a URL. Output was:\n" + "".join(lines))
    return proc, url, lines


def start_decoy(port, body=b"plain text, not itembank"):
    """A throwaway HTTP listener on a known port that responds but is
    definitely not an itembank daemon -- the squatter the sidecar's
    three-case startup falls back around (same fixture as
    tests/daemon_roundtrip.py's start_decoy).
    """
    class Decoy(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    srv = socketserver.TCPServer(("127.0.0.1", port), Decoy)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def start_silent_holder(port):
    """A raw TCP listener that accepts connections and then holds them open
    without ever sending a byte -- the "running instance is not reachable"
    fixture: a process owns the port but does not answer the itembank
    marker. Returns a handle with `.close()`.
    """
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(8)
    conns = []
    stop = threading.Event()

    def loop():
        srv.settimeout(0.2)
        while not stop.is_set():
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            conns.append(conn)                # hold it; never read, never reply

    threading.Thread(target=loop, daemon=True).start()

    def close():
        stop.set()
        for c in conns:
            try:
                c.close()
            except OSError:
                pass
        try:
            srv.close()
        except OSError:
            pass

    return {"close": close}


def get(url, timeout=5):
    with urllib.request.urlopen(url, timeout=timeout) as res:
        return res.status, res.read()


def request(url, payload=None, method="POST", headers=None, timeout=5):
    """A JSON request helper returning `(status, body)` for any HTTP
    outcome -- a non-2xx is not raised; the caller asserts the code.
    """
    body = b"" if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method=method,
                                 headers={"Content-Type": "application/json"})
    if headers:
        for name, value in headers.items():
            req.add_header(name, value)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, res.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except urllib.error.URLError as exc:
        return None, str(exc.reason).encode()


def wait_serving(port, host="127.0.0.1", timeout=8):
    """Poll until the marker at (host, port) answers 200 -- the socket is
    accepting *and* the server loop is dispatching, so a second launch can
    never race a bound-but-not-yet-serving instance.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                    "http://%s:%d/__itembank__" % (host, port), timeout=0.5) as res:
                if res.status == 200:
                    return
        except Exception:
            pass
        time.sleep(0.1)
    fail("port %d never served the marker within %.1fs" % (port, timeout))


def port_accepts(port, host="127.0.0.1", timeout=0.3):
    """True when a TCP connect to (host, port) succeeds -- a listener is
    accepting there, whatever it is. A refused connection means the port is
    free.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def pid_alive(pid):
    """True when a process with this pid still exists. Windows cannot use
    os.kill(pid, 0) (it terminates instead of querying), so liveness is read
    from `tasklist` there and from a signal-0 probe on POSIX.
    """
    if sys.platform == "win32":
        out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid],
                             capture_output=True, text=True).stdout
        return str(pid) in out
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def force_kill(pid):
    """Kill a process unconditionally -- taskkill /F on Windows (the
    semantics the shell's job object backstop will make unnecessary in the
    real app), SIGKILL elsewhere.
    """
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                       capture_output=True, text=True)
    else:
        os.kill(pid, 9)


# ---------------------------------------------------------------------------
# Task 1: the stdout handshake and the per-launch token
# ---------------------------------------------------------------------------

def check_sidecar_handshake():
    """Test 1 (task 1): launching the sidecar mode prints exactly the fixed
    handshake lines on stdout -- itembank-port:<bound>, itembank-token:<hex>,
    itembank-version:<version> -- after binding, and the bound port is the
    OS-assigned one when the requested port is taken by a non-itembank
    listener (the free-port fallback, reusing the three-case startup).
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, hs, lines = spawn_sidecar(workdir, "--port", "0")
    try:
        if set(hs) != set(SIDECAR_HANDSHAKE):
            fail("handshake keys %r != framing constants %r. Output was:\n%s"
                 % (sorted(hs), sorted(SIDECAR_HANDSHAKE), "".join(lines)))
        port = hs["port"]
        if not re.fullmatch(r"[1-9]\d{0,4}", port):
            fail("handshake port is not a real port: %r" % port)
        if not re.fullmatch(r"[0-9a-f]{32}", hs["token"]):
            fail("handshake token is not 32 hex chars: %r" % hs["token"])
        if hs["version"] != itembank.__version__:
            fail("handshake version %r != %r" % (hs["version"], itembank.__version__))
        # Exactly the fixed framing: no other `itembank-` line on stdout.
        for line in "".join(lines).splitlines():
            if line.startswith("itembank-") and not any(
                    line == prefix + ":" + hs[field]
                    for field, prefix in SIDECAR_HANDSHAKE.items()):
                fail("unexpected itembank- line on sidecar stdout: %r" % line)
        wait_serving(int(port))
        status, body = get("http://127.0.0.1:%d/__itembank__" % int(port))
        if status != 200 or json.loads(body.decode("utf-8")) != {"itembank": True}:
            fail("the bound sidecar port does not serve the itembank marker")
    finally:
        force_kill(proc.pid)

    # The requested port is taken by a non-itembank responder: the sidecar
    # falls back to an OS-assigned port and reports that one, never the held
    # one.
    port = free_port()
    decoy = start_decoy(port)
    try:
        proc, hs, lines = spawn_sidecar(workdir, "--port", str(port))
        try:
            if int(hs["port"]) == port:
                fail("sidecar served on the requested port %d even though a "
                     "non-itembank listener held it -- no free-port fallback"
                     % port)
            wait_serving(int(hs["port"]))
        finally:
            force_kill(proc.pid)
    finally:
        decoy.shutdown()
        decoy.server_close()


def check_sidecar_token_gate():
    """Test 2 (task 1): a request to a token-gated route without the
    per-launch token is refused (401); with the token it succeeds; page
    navigation and the probe marker stay open; and the CLI daemon path (no
    token) is byte-compatible -- the gate exists only in sidecar mode.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, hs, lines = spawn_sidecar(workdir, "--port", "0")
    try:
        base = "http://127.0.0.1:%s" % hs["port"]
        wait_serving(int(hs["port"]))

        status, body = request(base + "/api/start",
                               {"bank": "sample_bank", "count": 1})
        if status != 401:
            fail("POST /api/start without the per-launch token returned %r, "
                 "expected 401 (body %r)" % (status, body[:200]))

        status, body = request(base + "/api/start",
                               {"bank": "sample_bank", "count": 1},
                               headers={daemon.SIDECAR_TOKEN_HEADER: hs["token"]})
        if status != 200:
            fail("POST /api/start with the per-launch token returned %r, "
                 "expected 200 (body %r)" % (status, body[:200]))

        status, _ = get(base + "/")
        if status != 200:
            fail("GET / (a page navigation) was token-gated: %d" % status)
        status, _ = get(base + "/__itembank__")
        if status != 200:
            fail("GET /__itembank__ (the probe marker) was token-gated: %d" % status)
    finally:
        force_kill(proc.pid)

    # CLI daemon path: no sidecar, no token configured, /api/* open.
    proc2, url2, lines2 = start_daemon(workdir)
    try:
        status, _ = request(url2.rstrip("/") + "/api/start",
                            {"bank": "sample_bank", "count": 1})
        if status != 200:
            fail("the CLI daemon path served /api/start without a token with "
                 "HTTP %r -- the sidecar gate leaked into the CLI path" % status)
    finally:
        proc2.terminate()


def check_handshake_framing_shared():
    """Test 3 (task 1): the handshake lines are stable and parseable -- the
    shell's parser and this test share the same framing constants, and a
    handshake line parses as exactly `prefix:value`.
    """
    if set(SIDECAR_HANDSHAKE) != {"port", "token", "version"}:
        fail("SIDECAR_HANDSHAKE framing keys changed: %r" % SIDECAR_HANDSHAKE)
    for field, prefix in SIDECAR_HANDSHAKE.items():
        if not prefix or not prefix.startswith("itembank-"):
            fail("handshake prefix for %r is not a stable itembank- line: %r"
                 % (field, prefix))
    token_header = getattr(daemon, "SIDECAR_TOKEN_HEADER", None)
    if not token_header or not isinstance(token_header, str) or not token_header:
        fail("SIDECAR_TOKEN_HEADER is not a non-empty shared constant")
    sample = "\n".join("%s:value-%s" % (prefix, field)
                       for field, prefix in SIDECAR_HANDSHAKE.items())
    parsed = parse_handshake(sample)
    if parsed != {"port": "value-port", "token": "value-token",
                  "version": "value-version"}:
        fail("parse_handshake does not read the shared framing constants: %r"
             % parsed)


def main():
    checks = (
        check_sidecar_handshake,
        check_sidecar_token_gate,
        check_handshake_framing_shared,
    )
    for check in checks:
        check()
    print("ok: packaging shell roundtrip served %d checks -- handshake, token "
          "gate, shared framing" % len(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
