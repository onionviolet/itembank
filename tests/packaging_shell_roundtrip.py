#!/usr/bin/env python3
"""Subprocess fixtures for the sidecar-half of the desktop shell contract
(plan 13-01): the fixed stdout handshake (port/token/version), the
per-launch token gate on the shell-used API routes, single-instance
attach/refuse, and the kill-the-child-releases-the-port property the shell's
job object will rely on (D-05).

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
from surfaces.daemon import (SIDECAR_HANDSHAKE, SIDECAR_TOKEN_HEADER,
                             SIDECAR_PORT_HELD_COPY)       # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def free_port():
    """A currently-free TCP port, found by binding a throwaway server on
    port 0 and reading the OS-assigned number back before closing it.
    """
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
    """Launch `itembank sidecar <workdir> --no-open --port 0`,
    drain stdout on a background thread, and return `(proc, handshake,
    lines)` once the fixed handshake has been parsed. `wait=True` also polls
    the bound port until the marker answers, so attach/lifecycle fixtures
    never race a still-starting server. Extra args are appended after the
    default `--port 0`; argparse keeps the last `--port`, so a caller can
    pin a known port.
    """
    args = [sys.executable, "-u", os.path.join(ROOT, "itembank.py"),
            "sidecar", workdir, "--no-open", "--port", "0"]
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
         "sidecar", workdir, "--no-open"] + list(extra_args),
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
    """GET returning (status, body) for any HTTP outcome -- a non-2xx is not
    raised; the caller asserts the code.
    """
    try:
        with urllib.request.urlopen(url, timeout=timeout) as res:
            return res.status, res.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def get_with_header(url, token, timeout=5):
    """GET with the sidecar token header, returning (status, body) for any
    HTTP outcome.
    """
    req = urllib.request.Request(url)
    req.add_header(SIDECAR_TOKEN_HEADER, token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, res.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


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
    per-launch token is refused (401); with the token it succeeds; the probe
    marker stays open so the attach probe works; and the CLI daemon path (no
    token) is byte-compatible -- the gate exists only in sidecar mode.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, hs, lines = spawn_sidecar(workdir, "--port", "0")
    try:
        base = "http://127.0.0.1:%s" % hs["port"]
        wait_serving(int(hs["port"]))

        status, body = get(base + "/")
        if status != 401:
            fail("GET / without the per-launch token returned %r, expected 401"
                 % status)

        status, _ = get_with_header(base + "/", hs["token"])
        if status != 200:
            fail("GET / with the per-launch token returned %d, expected 200"
                 % status)

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

        status, body = get(base + "/__itembank__")
        if status != 200:
            fail("GET /__itembank__ (the probe marker) was token-gated: %d" % status)
    finally:
        force_kill(proc.pid)

    # CLI daemon path: no sidecar, no token configured, /api/* open.
    proc2, url2, lines2 = start_daemon(workdir)
    try:
        status, _ = get(url2)
        if status != 200:
            fail("the CLI daemon path served GET / without a token with HTTP "
                 "%r -- the sidecar gate leaked into the CLI path" % status)
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


# ---------------------------------------------------------------------------
# Task 2: single-instance attach/refuse in the sidecar launch path
# ---------------------------------------------------------------------------

def check_second_launch_attaches():
    """Test 1 (task 2): a second sidecar launch against a running instance
    prints the already-running line with the running URL and exits 0
    (attach), never starting a competing server (D-06).
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    port = free_port()
    proc, hs, lines = spawn_sidecar(workdir, "--port", str(port))
    try:
        wait_serving(port)
        code, output = run_sidecar_once(workdir, "--port", str(port))
        if code != 0:
            fail("a second sidecar on a held port exited %d, expected 0" % code)
        if ("itembank is already running at http://127.0.0.1:%d/" % port) not in output:
            fail("a second sidecar did not print the already-running line: %r"
                 % output)
        if any(line.startswith("itembank-") for line in output.splitlines()):
            fail("a second sidecar printed a handshake -- it started a "
                 "competing server: %r" % output)
        status, _ = get("http://127.0.0.1:%d/__itembank__" % port)
        if status != 200:
            fail("the first sidecar stopped answering after the second launch")
    finally:
        force_kill(proc.pid)


def check_attach_failure_refuses():
    """Test 2 (task 2): when attach fails (the running instance is not
    reachable -- the port is held by a listener that never answers the
    marker), the launch refuses with the 13-UI-SPEC 3.3(e) port-held copy
    and does not start a competing sidecar.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    port = free_port()
    holder = start_silent_holder(port)
    try:
        code, output = run_sidecar_once(workdir, "--port", str(port))
        if code == 0:
            fail("a sidecar that refused to launch exited 0; expected non-zero")
        if SIDECAR_PORT_HELD_COPY not in output:
            fail("the refusal did not carry the 3.3(e) port-held copy "
                 "verbatim: %r" % output)
        if any(line.startswith("itembank-") for line in output.splitlines()):
            fail("a refusing sidecar printed a handshake -- it started a "
                 "competing server: %r" % output)
        if not port_accepts(port):
            fail("the silent holder lost the port -- a competing server may "
                 "have bound it")
    finally:
        holder["close"]()


def check_port_held_copy_verbatim():
    """Test 3 (task 2): the port-held copy is the 13-UI-SPEC 3.3(e)
    attach-failed copy verbatim -- the daemon refuses by name; the pid the
    full copy carries is the shell's to fill in its window document (13-02).
    """
    expected = (
        "itembank is already running, but this window could not attach to it. "
        "Close the other itembank window, or end the process named itembank, "
        "then start itembank again."
    )
    if SIDECAR_PORT_HELD_COPY != expected:
        fail("SIDECAR_PORT_HELD_COPY drifted from the 3.3(e) copy: %r"
             % SIDECAR_PORT_HELD_COPY)


# ---------------------------------------------------------------------------
# Task 3: the lifecycle subprocess fixture (kill the child, port is released)
# ---------------------------------------------------------------------------

def check_lifecycle_sidecar():
    """Test 1 (task 3): force-killing the sidecar process -- the same
    TerminateProcess semantics the shell's job object applies (D-05) --
    releases its port within a bounded poll, and the fixture logs the
    measured teardown time.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, hs, lines = spawn_sidecar(workdir, "--port", "0")
    port = int(hs["port"])
    try:
        wait_serving(port)
        killed_at = time.time()
        force_kill(proc.pid)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            fail("sidecar did not exit within 10s of taskkill /F")
        if pid_alive(proc.pid):
            fail("sidecar pid %d is still alive after taskkill /F" % proc.pid)
        deadline = time.time() + 5.0
        while time.time() < deadline:
            if not port_accepts(port):
                break
            time.sleep(0.1)
        if port_accepts(port):
            fail("sidecar port %d still accepts after the process died" % port)
        print("  sidecar teardown (kill-to-port-release): %.3fs"
              % (time.time() - killed_at))
    finally:
        force_kill(proc.pid)


def check_lifecycle_daemon():
    """Test 2 (task 3): the same property holds when the sidecar was
    launched with the existing daemon entry -- proving the shell needs only
    the job object on top, not a new cleanup mechanism in the daemon.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    proc, url, lines = start_daemon(workdir)
    port = int(re.search(r"127\.0\.0\.1:(\d+)", url).group(1))
    try:
        wait_serving(port)
        killed_at = time.time()
        force_kill(proc.pid)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            fail("daemon did not exit within 10s of taskkill /F")
        if pid_alive(proc.pid):
            fail("daemon pid %d is still alive after taskkill /F" % proc.pid)
        deadline = time.time() + 5.0
        while time.time() < deadline:
            if not port_accepts(port):
                break
            time.sleep(0.1)
        if port_accepts(port):
            fail("daemon port %d still accepts after the process died" % port)
        print("  daemon teardown (kill-to-port-release): %.3fs"
              % (time.time() - killed_at))
    finally:
        force_kill(proc.pid)


def main():
    checks = (
        check_sidecar_handshake,
        check_sidecar_token_gate,
        check_handshake_framing_shared,
        check_second_launch_attaches,
        check_attach_failure_refuses,
        check_port_held_copy_verbatim,
        check_lifecycle_sidecar,
        check_lifecycle_daemon,
    )
    for check in checks:
        check()
    print("ok: packaging shell roundtrip served %d checks -- handshake, token "
          "gate, single-instance attach/refuse, and kill-releases-the-port"
          % len(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
