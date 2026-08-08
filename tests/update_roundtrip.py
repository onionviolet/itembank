#!/usr/bin/env python3
"""DEL-06/DEL-07 coverage: strictly-newer version comparison, checksum
accept/reject/abstain, the SHA256SUMS.txt fallback, offline and rate-limited
silence, atomic manifest validation, a writable update root, and the two
consent/secret-handling prohibitions (opt-in makes no request, the token
never comes from itembank.json) -- plus the install half added in plan
02.1-07: verify-then-position, idempotency, the versions-directory escape
guard, the relaunch handoff's every refusal case, and the update command's
and background check's own surface contracts.

No real network request is ever made -- every `urllib.request.urlopen` call
site is substituted with a stub before the module under test can reach it.
No real process is ever spawned -- `subprocess.Popen` is substituted the
same way for every `handoff` test. Every filesystem effect goes into a
`tempfile.mkdtemp()` directory; nothing is written into the checkout.

Runnable as `python tests/update_roundtrip.py`.
"""
import builtins
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
import contextlib
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
          "itembank.json, install/handoff safety, and the update command's "
          "and background check's surface coverage)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
