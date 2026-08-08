#!/usr/bin/env python3
"""DEL-06/DEL-07 coverage: strictly-newer version comparison, checksum
accept/reject/abstain, the SHA256SUMS.txt fallback, offline and rate-limited
silence, atomic manifest validation, a writable update root, and the two
consent/secret-handling prohibitions (opt-in makes no request, the token
never comes from itembank.json) -- plus the install half added in plan
02.1-07: verify-then-position, idempotency, the versions-directory escape
guard, the relaunch handoff's every refusal case, and the update command's
and background check's own surface contracts.

No real network request is ever made -- every request the module makes is
substituted at its single `_open_request` seam (or, for the redirect
tests, at the opener's transport handler) before the module under test can
reach the network. No real process is ever spawned -- `subprocess.Popen`
is substituted the same way for every `handoff` test. Every filesystem
effect goes into a `tempfile.mkdtemp()` directory; nothing is written into
the checkout.

Runnable as `python tests/update_roundtrip.py`.
"""
import builtins
import contextlib
import email.message
import hashlib
import inspect
import io
import json
import os
import shutil
import sys
import tempfile
import types
import urllib.error
import urllib.request
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
UPDATE_PY = os.path.join(ROOT, "surfaces", "update.py")

import itembank                                             # noqa: E402
from surfaces import update as u                          # noqa: E402
from surfaces import settings                              # noqa: E402
import schema_validate                                      # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


class FakeResponse:
    """A minimal stand-in for the object `urllib.request.urlopen` returns:
    a context manager exposing `.headers.get(...)` and `.read()`.
    """
    def __init__(self, headers=None, body=b"{}"):
        self.headers = headers or {}
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeRedirectResponse(io.BytesIO):
    """The response shape urllib's redirect chain asks of the object it
    processes: `.code`/`.status`/`.msg`, an `email.message.Message`
    `.headers` (so `Location` is found case-insensitively), an `.info()`
    returning that object -- and, from `io.BytesIO`, `.read()`, `.close()`
    and context-manager support (`HTTPRedirectHandler.http_error_302` reads
    and closes the 302 response before following it).
    """
    def __init__(self, code, msg, headers, body=b""):
        super().__init__(body)
        self.code = code
        self.status = code
        self.msg = msg
        self.headers = headers

    def info(self):
        return self.headers


class FakeRedirectTransport(urllib.request.BaseHandler):
    """A substituted https transport: answers `https_open` itself, records
    every request it sees as `(full_url, headers)`, and serves responses
    from a queue. `handler_order` below the real https handler's 500 so it
    answers first. Only the network is substituted -- the opener and its
    redirect handler are the real ones `download_asset` runs through.
    """
    handler_order = 100

    def __init__(self, responses, recorded):
        self.responses = list(responses)
        self.recorded = recorded

    def https_open(self, req):
        self.recorded.append((req.full_url, dict(req.header_items())))
        return self.responses.pop(0)


@contextlib.contextmanager
def patched_opener_transport(transport):
    """Build the module's real redirect-safe opener and inject a fake
    transport handler into it for the duration of the block. Only the
    network is substituted -- the opener, its AuthStrippingRedirectHandler
    and the redirect chain are the real ones `download_asset` runs through.
    Restores the module's opener factory afterward even if the block raises.
    """
    real = u._redirect_safe_opener

    def opener_with_transport():
        opener = real()
        opener.add_handler(transport)
        return opener

    u._redirect_safe_opener = opener_with_transport
    try:
        yield
    finally:
        u._redirect_safe_opener = real


@contextlib.contextmanager
def patched_transport(fn):
    """Substitute surfaces.update's own `_open_request` seam for the
    duration of the block, restoring it afterward even if the block
    raises. The seam is the module's only outbound-request path, so a
    stub left on the old `urlopen` name would intercept nothing and the
    suite would begin making real requests to GitHub -- which this file
    promises it never does.
    """
    original = u._open_request
    u._open_request = fn
    try:
        yield
    finally:
        u._open_request = original


# ---- strictly-newer comparison, independent of any checksum ---------------

def test_strictly_newer_only():
    cases = [
        ("v1.0.0", "v1.0.0", False),          # equal is not newer
        ("v1.0.1", "v1.0.0", True),           # one patch above
        ("v1.0.0", "v1.0.1", False),          # one patch below
        ("v1.10.0", "v1.9.0", True),          # two-digit minor over one-digit
        ("v1.9.0", "v1.10.0", False),         # reverse of the above
        ("v1.3.0-rc1", "v1.2.0", False),      # a suffixed offered tag is skipped
        ("v1.2.0", "v1.3.0-rc1", False),      # a suffixed running tag is skipped
    ]
    for offered, running, expected in cases:
        got = u.is_newer(offered, running)
        if got is not expected:
            fail("is_newer(%r, %r) == %r, expected %r" % (offered, running, got, expected))

    # Success Criterion 4's own sentence: is_newer takes no checksum argument
    # at all, so a caller combining a valid checksum with a non-newer version
    # cannot accidentally pass verification through as newness.
    params = list(inspect.signature(u.is_newer).parameters)
    if params != ["offered", "running"]:
        fail("is_newer's signature is %r, expected exactly (offered, running)" % params)

    data = b"release-asset-bytes"
    good_digest = "sha256:" + hashlib.sha256(data).hexdigest()
    checksum_ok = u.verify_digest(data, good_digest) is True
    version_ok = u.is_newer("v1.0.0", "v1.0.0")
    if not checksum_ok:
        fail("setup error: the known-good checksum did not verify")
    if version_ok:
        fail("a caller combining a valid checksum with an equal (non-newer) "
             "version must still refuse, per Success Criterion 4")


# ---- checksum verification: three outcomes, never conflated ---------------

def test_checksum_accepts_rejects_and_abstains():
    data = b"known-good-bytes"
    good = "sha256:" + hashlib.sha256(data).hexdigest()
    altered = bytearray(data)
    altered[0] ^= 0xFF
    altered = bytes(altered)

    if u.verify_digest(data, good) is not True:
        fail("verify_digest did not accept matching bytes")
    if u.verify_digest(altered, good) is not False:
        fail("verify_digest did not reject bytes altered by one byte")
    if u.verify_digest(data, None) is not None:
        fail("verify_digest did not abstain (None) on an absent expected value")
    if u.verify_digest(data, "") is not None:
        fail("verify_digest did not abstain (None) on an empty expected value")
    if u.verify_digest(data, "md5:" + ("0" * 32)) is not False:
        fail("verify_digest did not reject a non-sha256 algorithm prefix")

    # The failure mode this guards: conflating "no expectation" with "passed".
    if u.verify_digest(data, None) == u.verify_digest(data, good):
        fail("the absent-digest outcome must not equal the accepted outcome")


# ---- SHA256SUMS.txt fallback -----------------------------------------------

def test_sha256sums_fallback_finds_the_named_artifact():
    d1 = hashlib.sha256(b"one").hexdigest()
    d2 = hashlib.sha256(b"two").hexdigest()
    d3 = hashlib.sha256(b"three").hexdigest()
    text = (
        "%s  itembank-0.3.0.pyz\n"
        "%s  itembank-0.3.0.pyz.sig\n"
        "%s  SHA256SUMS.txt\n"
    ) % (d1, d2, d3)

    got = u.parse_sha256sums(text, "itembank-0.3.0.pyz")
    if got != d1:
        fail("parse_sha256sums did not find the exact-named entry: got %r" % got)

    if u.parse_sha256sums(text, "itembank-9.9.9.pyz") is not None:
        fail("parse_sha256sums found a digest for a name that is not present")

    # Not confused by a filename that is a prefix of another entry's name.
    got_sig = u.parse_sha256sums(text, "itembank-0.3.0.pyz.sig")
    if got_sig != d2:
        fail("parse_sha256sums matched the prefix entry instead of the "
             "exact-named one: got %r, expected %r" % (got_sig, d2))


# ---- offline / unreachable is silent ---------------------------------------

def test_offline_check_is_silent():
    def raise_url_error(*a, **kw):
        raise urllib.error.URLError("no route to host")

    def raise_timeout(*a, **kw):
        raise TimeoutError("timed out")

    def raise_http_error(*a, **kw):
        raise urllib.error.HTTPError("https://api.github.com/x", 500,
                                      "Internal Server Error", None, None)

    for raiser, label in ((raise_url_error, "URLError"),
                          (raise_timeout, "TimeoutError"),
                          (raise_http_error, "HTTPError")):
        buf = io.StringIO()
        with patched_transport(raiser):
            with contextlib.redirect_stdout(buf):
                result = u.check_latest("onionviolet/itembank")
        if result is not None:
            fail("check_latest returned %r instead of None under a simulated "
                 "%s" % (result, label))
        if buf.getvalue():
            fail("check_latest printed %r under a simulated %s -- DEL-07 "
                 "requires silence" % (buf.getvalue(), label))


# ---- rate-limited is silent to the return value, but distinguishable ------

def test_rate_limited_check_is_silent_but_distinguishable():
    def rate_limited(*a, **kw):
        return FakeResponse(headers={"X-RateLimit-Remaining": "0"})

    with patched_transport(rate_limited):
        result = u.check_latest("onionviolet/itembank")
        if result is not None:
            fail("check_latest returned %r under a rate-limited response, "
                 "expected None" % (result,))

        status = {}
        result2 = u.check_latest("onionviolet/itembank", status=status)
        if result2 is not None:
            fail("check_latest (with status passed) returned %r, expected None" %
                 (result2,))
        if status.get("rate_limited") is not True:
            fail("check_latest did not report rate_limited=True in the status "
                 "dict, so an explicit invocation could not print the "
                 "rate-limit line")


# ---- manifest: atomic write, schema-validated, corrupt-file-safe ----------

def test_manifest_write_is_atomic_and_validated():
    base = tempfile.mkdtemp()
    try:
        u.write_manifest(base, "v0.3.0", "itembank-0.3.0.pyz", "a" * 64)

        manifest_path = os.path.join(base, *u.MANIFEST_REL.split("/"))
        if not os.path.exists(manifest_path):
            fail("write_manifest did not write %s" % manifest_path)
        if os.path.exists(manifest_path + ".tmp"):
            fail("write_manifest left a .tmp file beside the manifest")

        written = json.load(open(manifest_path, encoding="utf-8"))
        schema = json.load(open(os.path.join(ROOT, "schemas",
                                              "update_manifest.schema.json"),
                                 encoding="utf-8"))
        errs = schema_validate.validate(written, schema)
        if errs:
            fail("the written manifest fails its own schema: %r" % errs)

        got = u.read_manifest(base)
        if got != written:
            fail("read_manifest did not read back what write_manifest wrote")

        # Corrupt the file; read_manifest must degrade to None, not raise.
        open(manifest_path, "w", encoding="utf-8").write("{not valid json")
        if u.read_manifest(base) is not None:
            fail("read_manifest did not return None for a corrupted manifest")
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- update_root() is a real, writable directory ---------------------------

def test_update_root_is_writable():
    root = u.update_root()
    if not isinstance(root, str) or not root:
        fail("update_root() did not return a non-empty string: %r" % (root,))
    probe = os.path.join(root, ".update_roundtrip_probe")
    try:
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write("x")
    except OSError as exc:
        fail("update_root() returned a non-writable directory: %s" % exc)
    finally:
        if os.path.exists(probe):
            os.remove(probe)

    # This test process is running from a checkout, not a .pyz, so
    # update_root() must fall back to the per-user directory rather than
    # returning a path inside the repository.
    if os.path.commonpath([os.path.abspath(root), ROOT]) == ROOT:
        fail("update_root() returned a path inside the checkout (%r) while "
             "not running from a .pyz" % (root,))


# ---- consent: opt_in with no explicit invocation makes no request ---------

def test_opt_in_policy_makes_no_request():
    calls = []

    def spy(*a, **kw):
        calls.append((a, kw))
        raise AssertionError("urlopen must never be called under this gate")

    with patched_transport(spy):
        if u.may_check("opt_in", False):
            u.check_latest("onionviolet/itembank")

    if calls:
        fail("a request was made under update_policy=opt_in with no explicit "
             "invocation: %r" % (calls,))

    # The mirror case: an explicit invocation, or check_on_launch, does open
    # the gate -- proving the recorder itself is capable of catching a call.
    if not u.may_check("opt_in", True):
        fail("may_check('opt_in', True) (an explicit itembank update) must be True")
    if not u.may_check("check_on_launch", False):
        fail("may_check('check_on_launch', False) (a background check) must be True")


# ---- secret handling: the token never comes from itembank.json ------------

def test_token_never_comes_from_the_settings_file():
    src = open(UPDATE_PY, encoding="utf-8").read()
    if "ITEMBANK_GITHUB_TOKEN" not in src:
        fail("surfaces/update.py does not name the ITEMBANK_GITHUB_TOKEN "
             "environment variable")
    if "itembank.json" in src:
        fail("surfaces/update.py names the settings filename itembank.json "
             "directly -- the token must never be read from a checked-in file")

    base = tempfile.mkdtemp()
    had_env_token = "ITEMBANK_GITHUB_TOKEN" in os.environ
    saved_env_token = os.environ.pop("ITEMBANK_GITHUB_TOKEN", None)
    try:
        data = settings.load_settings(base)
        data["itembank_github_token"] = "should-never-be-read"
        settings.write_settings(base, data)
        reloaded = settings.load_settings(base)

        captured = {}

        def spy(req, timeout=None):
            captured["headers"] = dict(req.header_items())
            raise urllib.error.URLError("offline (expected, no assertion on this)")

        with patched_transport(spy):
            u.check_latest(reloaded["update"]["repo"])

        if "Authorization" in captured.get("headers", {}):
            fail("check_latest sent an Authorization header without an "
                 "ITEMBANK_GITHUB_TOKEN environment variable set, despite a "
                 "token-looking key sitting in the settings file -- the "
                 "settings file must never be a token source")
    finally:
        shutil.rmtree(base, ignore_errors=True)
        if had_env_token:
            os.environ["ITEMBANK_GITHUB_TOKEN"] = saved_env_token


def _redirect_to(url):
    headers = email.message.Message()
    headers["Location"] = url
    return FakeRedirectResponse(302, "Found", headers)


def test_authorization_is_stripped_on_a_cross_host_redirect():
    """CR-01's end-to-end proof: drive `download_asset`'s real opener
    through a substituted transport and inspect what every hop actually
    carried. GitHub's asset endpoint 302s to `objects.githubusercontent.com`;
    the follow-up request must carry no Authorization header and no
    occurrence of the token string in any header value, while the first hop
    must carry both (the control assertion that the token was set at all).
    The chain then returns to api.github.com -- the header must not come
    back (sticky stripping, T-02.1-39).
    """
    sentinel = "sentinel-update-token-4b1e"
    hop1 = ("https://api.github.com/repos/onionviolet/itembank/releases/"
            "download/itembank-0.3.0.pyz")
    cdn = ("https://objects.githubusercontent.com/github-production-release-"
           "asset/2e1c6a/abc?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Signature=deadbeef")
    home = "https://api.github.com/repos/onionviolet/itembank/releases/latest"

    recorded = []
    transport = FakeRedirectTransport(
        [_redirect_to(cdn),
         _redirect_to(home),
         FakeRedirectResponse(200, "OK", email.message.Message(),
                              b"redirect-safe-artifact-bytes")],
        recorded)

    had_env_token = "ITEMBANK_GITHUB_TOKEN" in os.environ
    saved_env_token = os.environ.get("ITEMBANK_GITHUB_TOKEN")
    try:
        os.environ["ITEMBANK_GITHUB_TOKEN"] = sentinel
        with patched_opener_transport(transport):
            data = u.download_asset(hop1)
    finally:
        if had_env_token:
            os.environ["ITEMBANK_GITHUB_TOKEN"] = saved_env_token
        else:
            os.environ.pop("ITEMBANK_GITHUB_TOKEN", None)

    if data != b"redirect-safe-artifact-bytes":
        fail("download_asset did not return the final hop's bytes after "
             "the redirect chain: %r" % (data,))
    if len(recorded) != 3:
        fail("the redirected exchange made %d request(s), expected 3 "
             "(api.github.com -> objects.githubusercontent.com -> "
             "api.github.com): %r" % (len(recorded), recorded))

    first_url, first_headers = recorded[0]
    if first_url != hop1:
        fail("the first hop went to %r, expected %r" % (first_url, hop1))
    if first_headers.get("Authorization") != "Bearer " + sentinel:
        fail("the first hop did not carry the Authorization header -- the "
             "cross-host assertion would pass vacuously if the token were "
             "never set: %r" % (first_headers,))

    cdn_url, cdn_headers = recorded[1]
    if cdn_url != cdn:
        fail("the second hop went to %r, expected the CDN %r" % (cdn_url, cdn))
    lower = {k.lower(): v for k, v in cdn_headers.items()}
    if "authorization" in lower:
        fail("the cross-host hop carried an Authorization header: %r" % (cdn_headers,))
    for name, value in lower.items():
        if sentinel in value:
            fail("the cross-host hop carried the token string under header "
                 "%r: %r" % (name, value))
    if lower.get("accept") != "application/octet-stream":
        fail("the cross-host hop lost the Accept header: %r" % (cdn_headers,))
    if lower.get("user-agent") != "itembank-updater":
        fail("the cross-host hop lost the User-Agent header: %r" % (cdn_headers,))

    home_url, home_headers = recorded[2]
    if home_url != home:
        fail("the return-to-origin hop went to %r, expected %r" % (home_url, home))
    lower_home = {k.lower(): v for k, v in home_headers.items()}
    if "authorization" in lower_home:
        fail("the Authorization header came back on the return-to-origin "
             "hop: %r" % (home_headers,))
    for name, value in lower_home.items():
        if sentinel in value:
            fail("the return-to-origin hop carried the token string under "
                 "header %r: %r" % (name, value))


def test_same_host_redirect_keeps_authorization():
    """A redirect that stays on the same scheme, host and port must keep the
    Authorization header -- the fix removes the cross-origin leak, not the
    private-repo capability D-09 built (CR-01's same-host must_have).
    """
    sentinel = "sentinel-update-token-4b1e"
    first = ("https://api.github.com/repos/onionviolet/itembank/releases/"
             "download/itembank-0.3.0.pyz")
    second = ("https://api.github.com/repos/onionviolet/itembank/releases/"
              "download/itembank-0.3.0.pyz/relocated")

    recorded = []
    transport = FakeRedirectTransport(
        [_redirect_to(second),
         FakeRedirectResponse(200, "OK", email.message.Message(),
                              b"same-host-artifact-bytes")],
        recorded)

    had_env_token = "ITEMBANK_GITHUB_TOKEN" in os.environ
    saved_env_token = os.environ.get("ITEMBANK_GITHUB_TOKEN")
    try:
        os.environ["ITEMBANK_GITHUB_TOKEN"] = sentinel
        with patched_opener_transport(transport):
            data = u.download_asset(first)
    finally:
        if had_env_token:
            os.environ["ITEMBANK_GITHUB_TOKEN"] = saved_env_token
        else:
            os.environ.pop("ITEMBANK_GITHUB_TOKEN", None)

    if data != b"same-host-artifact-bytes":
        fail("download_asset did not return the same-host redirect's "
             "bytes: %r" % (data,))
    if len(recorded) != 2:
        fail("the same-host exchange made %d request(s), expected 2: %r" %
             (len(recorded), recorded))
    if recorded[0][1].get("Authorization") != "Bearer " + sentinel:
        fail("the first hop did not carry the Authorization header: %r" %
             (recorded[0][1],))
    if recorded[1][1].get("Authorization") != "Bearer " + sentinel:
        fail("a same-origin redirect dropped the Authorization header, "
             "breaking private-repo downloads: %r" % (recorded[1][1],))


def test_token_is_never_attached_to_a_non_github_host():
    """A release document's `browser_download_url` is API-supplied data
    that decides the host of the very first request, before any redirect
    exists -- so the credential must be host-gated before the header is
    even built (T-02.1-38). The github.com case is the control proving the
    token is not simply never set. The structural assertion closes
    T-02.1-40: both network functions must route through the one
    `_open_request` seam, so a future call site added beside them shows up
    as a failing assertion rather than as a silent second, unguarded
    request path.
    """
    sentinel = "sentinel-host-gate-token-9c27"
    foreign = ("https://example.invalid/onionviolet/itembank/releases/"
               "download/itembank-0.3.0.pyz")
    github = ("https://github.com/onionviolet/itembank/releases/download/"
              "itembank-0.3.0.pyz")

    for fn_name in ("check_latest", "download_asset"):
        src = inspect.getsource(getattr(u, fn_name))
        if "_open_request" not in src:
            fail("%s does not route through the module's single "
                 "_open_request seam (T-02.1-40):\n%s" % (fn_name, src))

    recorded = []
    transport = FakeRedirectTransport(
        [FakeRedirectResponse(200, "OK", email.message.Message(),
                              b"foreign-host-bytes"),
         FakeRedirectResponse(200, "OK", email.message.Message(),
                              b"github-host-bytes")],
        recorded)

    had_env_token = "ITEMBANK_GITHUB_TOKEN" in os.environ
    saved_env_token = os.environ.get("ITEMBANK_GITHUB_TOKEN")
    try:
        os.environ["ITEMBANK_GITHUB_TOKEN"] = sentinel
        with patched_opener_transport(transport):
            foreign_data = u.download_asset(foreign)
            github_data = u.download_asset(github)
    finally:
        if had_env_token:
            os.environ["ITEMBANK_GITHUB_TOKEN"] = saved_env_token
        else:
            os.environ.pop("ITEMBANK_GITHUB_TOKEN", None)

    if foreign_data != b"foreign-host-bytes":
        fail("download_asset did not fetch the foreign-host url: %r" %
             (foreign_data,))
    if github_data != b"github-host-bytes":
        fail("download_asset did not fetch the github.com url: %r" %
             (github_data,))
    if len(recorded) != 2:
        fail("the host-gate exchange made %d request(s), expected 2: %r" %
             (len(recorded), recorded))

    foreign_url, foreign_headers = recorded[0]
    if foreign_url != foreign:
        fail("the first request went to %r, expected the foreign url %r" %
             (foreign_url, foreign))
    lower_foreign = {k.lower(): v for k, v in foreign_headers.items()}
    if "authorization" in lower_foreign:
        fail("a non-GitHub host received an Authorization header on its "
             "very first request: %r" % (foreign_headers,))
    for name, value in lower_foreign.items():
        if sentinel in value:
            fail("a non-GitHub host received the token string under header "
                 "%r: %r" % (name, value))

    github_url, github_headers = recorded[1]
    if github_url != github:
        fail("the second request went to %r, expected the github.com url "
             "%r" % (github_url, github))
    if github_headers.get("Authorization") != "Bearer " + sentinel:
        fail("a github.com url did not receive the Authorization header -- "
             "the refusal assertion would pass vacuously if the token were "
             "never set: %r" % (github_headers,))


# ---- install: never writes the path this process is running from ---------

def test_install_never_writes_the_running_artifact():
    base = tempfile.mkdtemp()
    try:
        writes = []
        real_open = builtins.open

        def spy_open(path, mode="r", *args, **kwargs):
            if any(c in mode for c in ("w", "a", "+")):
                writes.append(os.path.abspath(os.fspath(path)))
            return real_open(path, mode, *args, **kwargs)

        data = b"install-tracking-bytes"
        digest = "sha256:" + hashlib.sha256(data).hexdigest()
        running = os.path.abspath(sys.argv[0])

        with mock.patch("builtins.open", spy_open):
            p = u.install(base, "9.9.5", "itembank-9.9.5.pyz", data, digest)

        if p is None:
            fail("install() with a matching digest returned None")
        if any(os.path.normcase(w) == os.path.normcase(running) for w in writes):
            fail("install() opened the running artifact's own path for "
                 "writing: %r" % running)
        if not os.path.basename(p).startswith("itembank-9.9.5"):
            fail("the installed artifact's name does not carry the version "
                 "being installed: %r" % p)
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- install: an interrupted/failed download leaves nothing readable ------

def test_partial_download_leaves_nothing_readable():
    base = tempfile.mkdtemp()
    try:
        good = b"good-artifact-bytes"
        good_digest = "sha256:" + hashlib.sha256(good).hexdigest()
        bad = b"corrupted-bytes-not-matching"

        before_manifest = u.read_manifest(base)
        result = u.install(base, "9.9.6", "itembank-9.9.6.pyz", bad, good_digest)
        if result is not None:
            fail("install() accepted bytes that failed checksum verification")

        versions_dir = os.path.join(base, *u.VERSIONS_REL.split("/"))
        target = os.path.join(versions_dir, "itembank-9.9.6.pyz")
        if os.path.exists(target):
            fail("a failed install left a readable artifact at the target path")
        if os.path.isdir(versions_dir) and any(
                n.endswith(".part") for n in os.listdir(versions_dir)):
            fail("a failed install left a partial-suffixed file behind")
        if u.read_manifest(base) != before_manifest:
            fail("a failed install changed the manifest")

        ok = u.install(base, "9.9.6", "itembank-9.9.6.pyz", good, good_digest)
        if ok is None or not os.path.exists(ok):
            fail("a subsequent successful install did not land the artifact")
        if any(n.endswith(".part") for n in os.listdir(versions_dir)):
            fail("a successful install left a partial-suffixed file behind")
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- install: a repeat call is a no-op, not a second copy -----------------

def test_install_is_idempotent():
    base = tempfile.mkdtemp()
    try:
        data = b"idempotent-artifact-bytes"
        digest = "sha256:" + hashlib.sha256(data).hexdigest()
        manifest_path = os.path.join(base, *u.MANIFEST_REL.split("/"))

        p1 = u.install(base, "9.9.7", "itembank-9.9.7.pyz", data, digest)
        m1 = open(manifest_path, "rb").read()
        versions_dir = os.path.dirname(p1)
        before = sorted(os.listdir(versions_dir))

        p2 = u.install(base, "9.9.7", "itembank-9.9.7.pyz", data, digest)
        m2 = open(manifest_path, "rb").read()
        after = sorted(os.listdir(versions_dir))

        if p1 != p2:
            fail("install() did not return the same path on a repeat call")
        if before != after:
            fail("a repeat install added a second artifact: %r vs %r" % (before, after))
        if m1 != m2:
            fail("a repeat install changed the manifest bytes")
        count = sum(1 for n in after if n.startswith("itembank-9.9.7"))
        if count != 1:
            fail("the versions directory does not hold exactly one artifact "
                 "for the repeated version: %r" % after)
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- pick_asset/install: an asset name can never escape the versions dir --

def test_asset_name_cannot_escape_the_versions_directory():
    data = b"escape-attempt-bytes"
    digest = "sha256:" + hashlib.sha256(data).hexdigest()
    hostile_names = [
        "../../etc/itembank-9.9.9.pyz",
        "..\\..\\itembank-9.9.9.pyz",
        "/etc/itembank-9.9.9.pyz",
    ]
    for hostile in hostile_names:
        release = {"assets": [{"name": hostile,
                               "browser_download_url": "https://example.invalid/x",
                               "digest": digest}]}
        result = u.pick_asset(release)
        if result is None:
            continue
        name = result[0]
        if name != os.path.basename(name):
            fail("pick_asset kept a path separator in the asset name: %r" % name)
        if ".." in name or name.startswith(("/", "\\")):
            fail("pick_asset's returned name still carries a traversal "
                 "sequence: %r" % name)

    base = tempfile.mkdtemp()
    try:
        p = u.install(base, "9.9.9", "itembank-9.9.9.pyz", data, digest)
        versions_dir = os.path.realpath(os.path.join(base, *u.VERSIONS_REL.split("/")))
        installed = os.path.realpath(p)
        if os.path.commonpath([installed, versions_dir]) != versions_dir:
            fail("install() wrote outside the versions directory: %r not "
                 "under %r" % (installed, versions_dir))
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- handoff: every unsafe case refuses; the one safe case spawns once ----

def test_handoff_refuses_every_unsafe_case():
    spawn_calls = []

    def spy_popen(*a, **kw):
        spawn_calls.append((a, kw))
        return object()

    def run_handoff():
        with mock.patch.object(u.subprocess, "Popen", spy_popen):
            try:
                return u.handoff([])
            except SystemExit:
                return "exited"

    # 1. No manifest at all.
    base = tempfile.mkdtemp()
    try:
        with mock.patch.object(u, "update_root", return_value=base):
            result = run_handoff()
        if result is not None:
            fail("handoff() did not return None with no manifest present")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    # 2. A malformed manifest.
    base = tempfile.mkdtemp()
    try:
        manifest_path = os.path.join(base, *u.MANIFEST_REL.split("/"))
        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as fh:
            fh.write("{not valid json")
        with mock.patch.object(u, "update_root", return_value=base):
            result = run_handoff()
        if result is not None:
            fail("handoff() did not return None with a malformed manifest")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    # 3. Manifest version not newer than the running one.
    base = tempfile.mkdtemp()
    try:
        u.write_manifest(base, itembank.__version__, "versions/itembank-x.pyz", "a" * 64)
        with mock.patch.object(u, "update_root", return_value=base):
            result = run_handoff()
        if result is not None:
            fail("handoff() did not return None when the manifest version "
                 "is not newer")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    # 4. Manifest names a missing target.
    base = tempfile.mkdtemp()
    try:
        u.write_manifest(base, "v99.0.0", "versions/itembank-99.0.0.pyz", "a" * 64)
        with mock.patch.object(u, "update_root", return_value=base):
            result = run_handoff()
        if result is not None:
            fail("handoff() did not return None when the manifest's target is missing")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    # 5. Target exists but its digest does not match the manifest.
    base = tempfile.mkdtemp()
    try:
        versions_dir = os.path.join(base, "versions")
        os.makedirs(versions_dir, exist_ok=True)
        target = os.path.join(versions_dir, "itembank-99.0.0.pyz")
        with open(target, "wb") as fh:
            fh.write(b"not-the-recorded-bytes")
        u.write_manifest(base, "v99.0.0", "versions/itembank-99.0.0.pyz", "a" * 64)
        with mock.patch.object(u, "update_root", return_value=base):
            result = run_handoff()
        if result is not None:
            fail("handoff() did not return None when the target's digest "
                 "does not match")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    # 6. Manifest points at the artifact this process is already running from.
    base = tempfile.mkdtemp()
    try:
        versions_dir = os.path.join(base, "versions")
        os.makedirs(versions_dir, exist_ok=True)
        target = os.path.join(versions_dir, "itembank-99.0.0.pyz")
        data = b"self-referential-bytes"
        with open(target, "wb") as fh:
            fh.write(data)
        digest_hex = hashlib.sha256(data).hexdigest()
        u.write_manifest(base, "v99.0.0", "versions/itembank-99.0.0.pyz", digest_hex)
        with mock.patch.object(u, "update_root", return_value=base), \
             mock.patch.object(u.resources, "archive_path", return_value=target):
            result = run_handoff()
        if result is not None:
            fail("handoff() did not return None when the target is the "
                 "artifact already running")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    if spawn_calls:
        fail("handoff() spawned a process in a case that should have "
             "refused: %r" % (spawn_calls,))

    # 7. The one case where every guard passes: spawn is called exactly once.
    base = tempfile.mkdtemp()
    try:
        versions_dir = os.path.join(base, "versions")
        os.makedirs(versions_dir, exist_ok=True)
        target = os.path.join(versions_dir, "itembank-99.0.0.pyz")
        data = b"a-genuinely-newer-artifact"
        with open(target, "wb") as fh:
            fh.write(data)
        digest_hex = hashlib.sha256(data).hexdigest()
        u.write_manifest(base, "v99.0.0", "versions/itembank-99.0.0.pyz", digest_hex)
        with mock.patch.object(u, "update_root", return_value=base), \
             mock.patch.object(u.resources, "archive_path", return_value=None):
            result = run_handoff()
        if len(spawn_calls) != 1:
            fail("handoff() did not spawn exactly once when every guard "
                 "passed: %r" % (spawn_calls,))
        if result != "exited":
            fail("handoff() did not sys.exit(0) after a successful spawn")
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---- cmd_update: exactly one of the six locked outcome lines --------------

def test_update_command_prints_one_locked_outcome():
    running_parsed = u.parse_version(itembank.__version__)
    higher_tag = "v%d.%d.%d" % (running_parsed[0], running_parsed[1] + 1, running_parsed[2])
    lower_tag = "v0.0.1"
    same_tag = "v" + itembank.__version__

    def make_args():
        return types.SimpleNamespace(check=False, repo="onionviolet/itembank", timeout=5)

    def release_for(tag):
        payload = ("scenario-artifact-" + tag).encode("ascii")
        good_digest = "sha256:" + hashlib.sha256(payload).hexdigest()
        release = {
            "tag_name": tag,
            "assets": [{
                "name": "itembank-%s.pyz" % tag.lstrip("v"),
                "browser_download_url": "https://example.invalid/itembank.pyz",
                "digest": good_digest,
            }],
        }
        return release, payload

    def run(check_latest_fn, download_fn=None):
        if download_fn is None:
            download_fn = lambda url, token=None, timeout=30: None      # noqa: E731
        base = tempfile.mkdtemp()
        buf = io.StringIO()
        try:
            with mock.patch.object(u, "check_latest", check_latest_fn), \
                 mock.patch.object(u, "update_root", return_value=base), \
                 mock.patch.object(u, "download_asset", download_fn):
                with contextlib.redirect_stdout(buf):
                    code = u.cmd_update(make_args())
        finally:
            shutil.rmtree(base, ignore_errors=True)
        return buf.getvalue(), code

    def assert_outcome(out, code, must_contain, expected_code, label):
        if must_contain not in out:
            fail("the %s outcome did not print its locked line: %r" % (label, out))
        if code != expected_code:
            fail("the %s outcome exited %r, expected %r" % (label, code, expected_code))
        if label != "up-to-date" and "up to date" in out:
            fail("the %s outcome must never also print the up-to-date line" % label)

    def offline(repo, timeout=5, token=None, status=None):
        return None
    out, code = run(offline)
    assert_outcome(out, code, "Could not reach GitHub", 0, "offline")

    def rate_limited(repo, timeout=5, token=None, status=None):
        if status is not None:
            status["rate_limited"] = True
        return None
    out, code = run(rate_limited)
    assert_outcome(out, code, "rate-limited", 0, "rate-limited")

    lower_release, _ = release_for(lower_tag)
    out, code = run(lambda repo, timeout=5, token=None, status=None: lower_release)
    assert_outcome(out, code, "not newer than the version you're running", 1,
                   "downgrade-rejected")

    same_release, _ = release_for(same_tag)
    out, code = run(lambda repo, timeout=5, token=None, status=None: same_release)
    assert_outcome(out, code, "up to date", 0, "up-to-date")

    higher_release, payload = release_for(higher_tag)
    tampered = lambda url, token=None, timeout=30: b"tampered-does-not-match"  # noqa: E731
    out, code = run(lambda repo, timeout=5, token=None, status=None: higher_release,
                    download_fn=tampered)
    assert_outcome(out, code, "checksum verification", 1, "checksum-failure")

    higher_release, payload = release_for(higher_tag)
    honest = lambda url, token=None, timeout=30: payload                     # noqa: E731
    out, code = run(lambda repo, timeout=5, token=None, status=None: higher_release,
                    download_fn=honest)
    assert_outcome(out, code, "Installed", 0, "installed")


# ---- background_check: silent on every failure, one line when newer ------

def test_background_check_is_silent_on_every_failure():
    cfg = {"update_policy": "check_on_launch",
           "update": {"repo": "onionviolet/itembank", "check_interval_hours": 0}}

    def run_bg(check_latest_fn):
        base = tempfile.mkdtemp()
        try:
            buf = io.StringIO()
            with mock.patch.object(u, "check_latest", check_latest_fn), \
                 mock.patch.object(u, "download_asset",
                                   lambda *a, **k: fail("background_check downloaded "
                                                        "something; it must only inform")):
                with contextlib.redirect_stdout(buf):
                    u.background_check(base, cfg)
            return buf.getvalue()
        finally:
            shutil.rmtree(base, ignore_errors=True)

    def none_result(repo, timeout=5, token=None, status=None):
        return None

    def rate_limited_result(repo, timeout=5, token=None, status=None):
        if status is not None:
            status["rate_limited"] = True
        return None

    for label, fn in (("offline", none_result), ("timeout", none_result),
                      ("http-error", none_result),
                      ("rate-limited", rate_limited_result)):
        out = run_bg(fn)
        if out:
            fail("background_check printed %r under a simulated %s outcome" % (out, label))

    def raising(repo, timeout=5, token=None, status=None):
        raise urllib.error.URLError("unexpected")

    try:
        out = run_bg(raising)
    except Exception as exc:
        fail("background_check propagated an exception instead of degrading: %r" % exc)
    if out:
        fail("background_check printed something when check_latest raised "
             "unexpectedly: %r" % out)

    running_parsed = u.parse_version(itembank.__version__)
    higher_tag = "v%d.%d.%d" % (running_parsed[0], running_parsed[1] + 1, running_parsed[2])
    download_calls = []

    def newer_release(repo, timeout=5, token=None, status=None):
        return {"tag_name": higher_tag, "assets": []}

    def spy_download(url, token=None, timeout=30):
        download_calls.append(url)
        return b"should never be downloaded by a background check"

    base = tempfile.mkdtemp()
    try:
        buf = io.StringIO()
        with mock.patch.object(u, "check_latest", newer_release), \
             mock.patch.object(u, "download_asset", spy_download):
            with contextlib.redirect_stdout(buf):
                u.background_check(base, cfg)
        out = buf.getvalue()
        lines = [ln for ln in out.splitlines() if ln.strip()]
        if len(lines) != 1:
            fail("background_check printed %d line(s) for a genuine newer "
                 "version, expected exactly 1: %r" % (len(lines), out))
        if higher_tag not in lines[0]:
            fail("background_check's one line does not name the new "
                 "version: %r" % lines[0])
        if download_calls:
            fail("background_check downloaded something; it must only "
                 "inform: %r" % download_calls)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    test_strictly_newer_only()
    test_checksum_accepts_rejects_and_abstains()
    test_sha256sums_fallback_finds_the_named_artifact()
    test_offline_check_is_silent()
    test_rate_limited_check_is_silent_but_distinguishable()
    test_manifest_write_is_atomic_and_validated()
    test_update_root_is_writable()
    test_opt_in_policy_makes_no_request()
    test_token_never_comes_from_the_settings_file()
    test_authorization_is_stripped_on_a_cross_host_redirect()
    test_same_host_redirect_keeps_authorization()
    test_token_is_never_attached_to_a_non_github_host()
    test_install_never_writes_the_running_artifact()
    test_partial_download_leaves_nothing_readable()
    test_install_is_idempotent()
    test_asset_name_cannot_escape_the_versions_directory()
    test_handoff_refuses_every_unsafe_case()
    test_update_command_prints_one_locked_outcome()
    test_background_check_is_silent_on_every_failure()
    print("update contract: ok (strictly-newer comparison, checksum "
          "accept/reject/abstain, SHA256SUMS.txt fallback, offline and "
          "rate-limited silence, atomic validated manifest, a writable "
          "update root, opt-in consent, the token never comes from "
          "itembank.json, install/handoff safety, the update command's "
          "and background check's surface coverage, and redirect-safe "
          "authorization stripping plus the token host gate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
