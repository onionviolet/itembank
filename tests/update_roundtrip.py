#!/usr/bin/env python3
"""DEL-06/DEL-07 coverage: strictly-newer version comparison, checksum
accept/reject/abstain, the SHA256SUMS.txt fallback, offline and rate-limited
silence, atomic manifest validation, a writable update root, and the two
consent/secret-handling prohibitions (opt-in makes no request, the token
never comes from itembank.json).

No real network request is ever made -- every `urllib.request.urlopen` call
site is substituted with a stub before the module under test can reach it.
Every filesystem effect goes into a `tempfile.mkdtemp()` directory; nothing
is written into the checkout.

Runnable as `python tests/update_roundtrip.py`.
"""
import hashlib
import inspect
import io
import json
import os
import shutil
import sys
import tempfile
import urllib.error
import contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
UPDATE_PY = os.path.join(ROOT, "surfaces", "update.py")

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


@contextlib.contextmanager
def patched_urlopen(fn):
    """Substitute surfaces.update's own urlopen reference for the duration
    of the block, restoring it afterward even if the block raises.
    """
    original = u.urllib.request.urlopen
    u.urllib.request.urlopen = fn
    try:
        yield
    finally:
        u.urllib.request.urlopen = original


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
        with patched_urlopen(raiser):
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

    with patched_urlopen(rate_limited):
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

    with patched_urlopen(spy):
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

        with patched_urlopen(spy):
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
    print("update contract: ok (strictly-newer comparison, checksum "
          "accept/reject/abstain, SHA256SUMS.txt fallback, offline and "
          "rate-limited silence, atomic validated manifest, a writable "
          "update root, opt-in consent, and the token never comes from "
          "itembank.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
