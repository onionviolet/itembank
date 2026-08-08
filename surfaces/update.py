"""The updater's decision half: what version is out there, is it actually
newer, and are its bytes the bytes GitHub says they are.

Two invariants hold across every function in this module, the same way
`surfaces/day.py`'s Anki handling already keeps "a closed dependency degrades
to an omitted badge, never an error": the currently-running file is never
opened for writing here (the install half, which lands a downloaded artifact
beside it, is a sibling plan), and every network failure -- unreachable,
timed out, rate-limited, a bad HTTP status -- returns `None` rather than
raising. Nothing on this path may reach a caller (daemon startup, `itembank
update`) as an exception; being unreachable is a normal outcome, not a bug.

The release tag format this module's version comparison depends on is locked
by CONTEXT.md D-07: plain `vX.Y.Z`, never a pre-release or build suffix. A
tag this module cannot parse is skipped as "no update offered" rather than
crashing the check -- the one-way-door consequence of publishing a suffixed
tag is a re-cut release, never a broken client.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import resources
import schema_validate
from surfaces import settings


MANIFEST_SCHEMA_RESOURCE = "schemas/update_manifest.schema.json"

# Relative to update_root() (see below). Forward-slash so the same string
# works as both a schema-document path (via resources.read_text) and, split
# on "/", an os.path.join() argument list on every platform.
MANIFEST_REL = "updates/current.json"
VERSIONS_REL = "versions"

# The published dotted error-code namespace, following SETTINGS_CODES'
# set-then-sorted construction (surfaces/settings.py) so sortedness is
# structural rather than maintained by eye.
UPDATE_CODES = tuple(sorted({
    "update.checksum_mismatch", "update.downgrade_rejected",
    "update.malformed_manifest", "update.missing_asset",
    "update.rate_limited", "update.unreachable",
}))

# vX.Y.Z or X.Y.Z, exactly three dot-separated integer components. Anything
# else -- a pre-release suffix, build metadata, a two-component version --
# does not match, and parse_version returns None rather than raising.
_VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")

_GITHUB_API = "https://api.github.com/repos/%s/releases/latest"


def parse_version(text):
    """Parse a plain `vX.Y.Z` (or `X.Y.Z`) tag into a 3-tuple of integers,
    or return `None` for anything that does not match exactly -- a suffix,
    a wrong component count, or a non-string. `None` is a skip signal, never
    an exception: D-07's one-way-door means an unparseable published tag
    must degrade to "no update offered", not crash the check.
    """
    if not isinstance(text, str):
        return None
    m = _VERSION_RE.match(text.strip())
    if not m:
        return None
    return tuple(int(g) for g in m.groups())


def is_newer(offered, running):
    """True only when both `offered` and `running` parse and `offered`'s
    tuple sorts strictly above `running`'s. Equal is not newer -- Success
    Criterion 4 stated as one function. Deliberately takes no checksum
    argument: a downgrade is rejected on version alone, independent of and
    prior to any checksum verification, so a validly-checksummed old release
    can never be accepted by reordering arguments.
    """
    o = parse_version(offered)
    r = parse_version(running)
    if o is None or r is None:
        return False
    return o > r


def verify_digest(data, expected):
    """Three distinct outcomes, never conflated. `expected` absent or empty
    returns `None` -- "no expectation available, use the SHA256SUMS.txt
    fallback" -- which is not a pass and must never be treated as one; the
    `digest` field is null for any GitHub release asset uploaded before the
    feature's mid-2025 GA, and a transient partial API response can produce
    the same shape. A non-`sha256` algorithm prefix returns `False`.
    Otherwise the SHA-256 of `data` is compared against the hex half.
    """
    if not expected:
        return None
    algo, sep, hexval = expected.partition(":")
    if not sep or algo != "sha256":
        return False
    return hashlib.sha256(data).hexdigest() == hexval


def parse_sha256sums(text, name):
    """Scan a `SHA256SUMS.txt`-shaped document (one `<64 hex>  <filename>`
    line per artifact, the shape `build.py:sha256sums()` already writes) for
    the entry naming `name`, returning its hex digest or `None`. Shares
    `verify_digest`'s comparison; this function only locates the expected
    value the digest-field primary path could not supply.
    """
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        digest, fname = parts
        fname = fname.strip()
        if fname.startswith("*"):
            # sha256sum's binary-mode marker; the filename is what follows.
            fname = fname[1:]
        if fname == name:
            return digest
    return None


def _writable(path):
    """A permission bit can be present while the filesystem underneath it is
    read-only (a mounted USB stick, a locked-down install directory), so
    update_root() probes by writing and removing a real temporary file
    rather than trusting os.access() alone.
    """
    probe = os.path.join(path, ".itembank_write_probe")
    try:
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write("")
        os.remove(probe)
        return True
    except OSError:
        return False


def _user_data_dir():
    """The platform per-user data directory, reusing exactly the
    win32/darwin/else branch surfaces/day.py's `_anki_addon_port` already
    implements (D-12 forbids a second copy of this selection).
    """
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
    elif sys.platform == "darwin":
        base = os.path.join(home, "Library", "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME", os.path.join(home, ".local", "share"))
    target = os.path.join(base, "itembank")
    try:
        os.makedirs(target, exist_ok=True)
    except OSError:
        pass
    return target


def update_root():
    """The base directory the versions directory and the manifest live
    under. Prefers the directory holding the running `.pyz` (from
    `resources.archive_path()`) when that directory is writable, so a copy
    carried on a USB stick or sitting in a Downloads folder stays
    self-contained. Falls back to the platform per-user data directory
    otherwise -- including when this process is not running from a `.pyz`
    at all, since a checkout has no artifact to sit beside.
    """
    archive = resources.archive_path()
    if archive is not None:
        candidate = os.path.dirname(os.path.abspath(archive))
        if _writable(candidate):
            return candidate
    return _user_data_dir()


def _manifest_path(base):
    return os.path.join(base, *MANIFEST_REL.split("/"))


def read_manifest(base):
    """Load and schema-validate the update manifest, returning `None` on a
    missing file, unparseable JSON, or a document that fails validation
    against schemas/update_manifest.schema.json -- never raising. A corrupt
    pointer must degrade to "no newer version installed", never to a crash
    on startup.
    """
    path = _manifest_path(base)
    try:
        raw = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return None
    schema = json.loads(resources.read_text(MANIFEST_SCHEMA_RESOURCE))
    if schema_validate.validate(raw, schema):
        return None
    return raw


def write_manifest(base, version, path, sha256, checked_at=None):
    """Write the update manifest with the exact tmp-then-os.replace sequence
    `surfaces/settings.py:write_settings()` uses -- no second atomic-write
    helper. `checked_at` defaults to now (UTC, ISO-8601) so a caller that
    just completed a release check, whether or not it found anything newer,
    can record both "what we currently trust" and "when we last verified
    that" in the one write should_check() later reads.
    """
    if checked_at is None:
        checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {
        "schema_version": 1,
        "version": version,
        "path": path,
        "sha256": sha256,
        "checked_at": checked_at,
    }
    target = _manifest_path(base)
    target_dir = os.path.dirname(os.path.abspath(target))
    os.makedirs(target_dir, exist_ok=True)
    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, target)


def check_latest(repo, timeout=5, token=None, status=None):
    """Fetch GitHub's releases/latest document for `repo` (an `owner/name`
    string -- the caller's job to source from settings, never hardcoded or
    read from any file here). Returns the parsed JSON document, or `None` on
    anything short of a clean 200: unreachable, DNS failure, timeout, an
    HTTP error status, or a rate-limited response. Nothing here raises.

    `token`, when not passed explicitly, is read from the
    `ITEMBANK_GITHUB_TOKEN` environment variable and from nowhere else
    (D-09) -- never from the checked-in settings file, and never written
    to the manifest, a printed line, or a log.

    `status`, when passed a dict, is populated with `status["rate_limited"]`
    so an explicit `itembank update` invocation can print the rate-limit
    line while a background check -- which never inspects `status` -- stays
    silent, per DEL-07's split between the two call sites.
    """
    if status is None:
        status = {}
    status["rate_limited"] = False
    if token is None:
        token = os.environ.get("ITEMBANK_GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "itembank-updater",
    }
    if token:
        headers["Authorization"] = "Bearer %s" % token
    req = urllib.request.Request(_GITHUB_API % repo, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.headers.get("X-RateLimit-Remaining") == "0":
                status["rate_limited"] = True
                return None
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        remaining = exc.headers.get("X-RateLimit-Remaining") if exc.headers else None
        if remaining == "0":
            status["rate_limited"] = True
        return None
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def should_check(base, interval_hours):
    """The rate-limit guard behind DEL-07/RESEARCH Pitfall 2: `True` only
    when no manifest exists yet (never checked) or at least
    `interval_hours` have elapsed since the manifest's own `checked_at`.
    `check_on_launch` expresses an intent to check on every launch; this
    function decides whether an actual request is made, so a shared campus
    or dorm network does not exhaust a 60-per-hour budget across every
    learner's every launch.
    """
    manifest = read_manifest(base)
    if manifest is None:
        return True
    try:
        checked_at = datetime.strptime(manifest["checked_at"], "%Y-%m-%dT%H:%M:%SZ")
        checked_at = checked_at.replace(tzinfo=timezone.utc)
    except (KeyError, ValueError):
        return True
    elapsed = datetime.now(timezone.utc) - checked_at
    return elapsed.total_seconds() >= interval_hours * 3600


def may_check(policy, explicit):
    """The mechanical half of the consent prohibition: a request is
    permitted only when the policy is `check_on_launch` or the learner
    explicitly ran the update command. Under `opt_in` with `explicit=False`
    -- a fresh install that was never asked to update -- this is always
    `False`, and no caller may make a network request without consulting it
    first.
    """
    return bool(explicit) or policy == "check_on_launch"


# ---- request plumbing: one opener, one seam -------------------------------

def _origin_of(url):
    """The (scheme, host, port) triple identifying where a request is aimed,
    with a missing port resolved to the scheme's default so a url that
    spells its default port out does not read as a different origin. An
    unparseable port degrades to a port of `None` -- different from any real
    origin -- so the caller treats the target as foreign and strips the
    credential, failing closed.
    """
    parts = urllib.parse.urlsplit(url)
    scheme = parts.scheme.lower()
    host = (parts.hostname or "").lower()
    try:
        port = parts.port
    except ValueError:
        port = None
    if port is None:
        port = 443 if scheme == "https" else (80 if scheme == "http" else None)
    return (scheme, host, port)


class AuthStrippingRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Remove the Authorization header the instant a redirect crosses to a
    different origin -- scheme, host or port. stdlib's own
    `redirect_request` copies every header except content-length and
    content-type onto the follow-up request and never compares hosts,
    which is exactly how 02.1-VERIFICATION.md's CR-01 leaked the update
    token onto GitHub's separately-hosted CDN origin. This subclass does
    not second-guess whether a redirect is legal -- `super()` decides that
    -- and the stripped state is sticky: each hop's Request is built from
    the previous hop's headers, so once the header is gone it cannot return
    on a later hop that happens to come back to the original host
    (T-02.1-39).
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is None:
            return None
        if _origin_of(req.full_url) != _origin_of(newurl):
            # Request capitalises keys it is given, but a caller-built dict
            # may not have, so delete case-insensitively over a copy.
            for key in list(new.headers):
                if key.lower() == "authorization":
                    del new.headers[key]
            for key in list(new.unredirected_hdrs):
                if key.lower() == "authorization":
                    del new.unredirected_hdrs[key]
        return new


def _redirect_safe_opener():
    """A fresh opener carrying the module's AuthStrippingRedirectHandler.
    `build_opener` substitutes a passed instance for the default handler of
    the same family, so the default HTTPRedirectHandler is not in the
    chain. Built per call rather than cached in a module global -- this
    project holds no module-level mutable state (CLAUDE.md), and the
    at-most-two requests an update check makes cost nothing.
    """
    return urllib.request.build_opener(AuthStrippingRedirectHandler())


def _open_request(req, timeout):
    """The module's single outbound-request seam: every request an update
    check makes opens through the redirect-safe opener, so no call site can
    bypass the Authorization-stripping handler. Returns the opener's
    response context manager; callers keep their own existing except
    clauses, which is why the module-wide failure contract (every error
    class returns `None`, nothing raises) is unchanged.
    """
    return _redirect_safe_opener().open(req, timeout=timeout)


# ---- install half: download, verify-then-position, the relaunch handoff --

# The artifact shape this project's own `build.py` emits: a fixed prefix, a
# plain vX.Y.Z-shaped version with no leading "v" (build.py names the file
# from `itembank.__version__` directly), and the archive suffix. Anything
# else -- a differently-prefixed name, a script, a `SHA256SUMS.txt`, or a
# path-traversal attempt reduced to its basename -- is not a match.
_ASSET_RE = re.compile(r"^itembank-\d+\.\d+\.\d+\.pyz$")

# The checksum-file asset name `build.py:sha256sums()` writes -- the
# fallback source of an artifact's expected digest when the release asset's
# own `digest` field is absent or null.
CHECKSUMS_ASSET_NAME = "SHA256SUMS.txt"

# An order of magnitude above the real artifact's size (well under 10MB),
# generous and still bounded -- a hostile or broken response cannot exhaust
# memory through `download_asset`.
_MAX_ASSET_BYTES = 100 * 1024 * 1024


def pick_asset(release):
    """Choose the release asset to fetch from a parsed GitHub releases/latest
    document, or return `None` when nothing qualifies. The API's `name`
    field is never trusted as a path component: it is reduced to its
    basename first, and only a basename matching this project's own build
    shape is accepted, so a maliciously named asset can never carry a
    parent-directory segment into a later filesystem path. The first
    qualifying asset wins when several are present. Returns
    `(name, download_url, digest)`, with `digest` explicitly `None` (never
    substituted) when the asset's own `digest` field is absent or null.
    """
    if not isinstance(release, dict):
        return None
    for asset in release.get("assets") or []:
        if not isinstance(asset, dict):
            continue
        raw_name = asset.get("name")
        if not isinstance(raw_name, str) or not raw_name:
            continue
        name = os.path.basename(raw_name)
        if not _ASSET_RE.match(name):
            continue
        url = asset.get("browser_download_url")
        if not isinstance(url, str) or not url:
            continue
        digest = asset.get("digest")
        if not isinstance(digest, str) or not digest:
            digest = None
        return (name, url, digest)
    return None


def download_asset(url, token=None, timeout=30):
    """Fetch `url`'s bytes over https, or return `None` on any failure --
    unreachable, timed out, a bad HTTP status -- the same failure handling
    `check_latest` uses; nothing here raises. `token`, when not passed
    explicitly, is read from `ITEMBANK_GITHUB_TOKEN` (D-09), same as
    `check_latest`. The read is capped at `_MAX_ASSET_BYTES` so a hostile or
    stalled response cannot exhaust memory (T-02.1-33).
    """
    if token is None:
        token = os.environ.get("ITEMBANK_GITHUB_TOKEN")
    headers = {
        "Accept": "application/octet-stream",
        "User-Agent": "itembank-updater",
    }
    if token:
        headers["Authorization"] = "Bearer %s" % token
    req = urllib.request.Request(url, headers=headers)
    try:
        with _open_request(req, timeout=timeout) as resp:
            return resp.read(_MAX_ASSET_BYTES)
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def install(base, version, name, data, expected):
    """Verify `data` against `expected` first; only a verified artifact is
    ever written to disk, and nothing is written at all when verification
    fails or cannot be completed (`verify_digest`'s `False` or `None`) --
    this is what makes Success Criterion 3 structural rather than merely
    careful. On success, `data` is written to a `.part`-suffixed name under
    `base`'s versions directory and `os.replace`d onto the version-qualified
    final name, so an interrupted write can never leave a partial artifact
    at a path anything reads. The pointer manifest is written last, naming
    the version, the artifact's path relative to `base`, its digest, and the
    check time.

    Idempotent by construction: when the target already exists with the
    same digest under a manifest that already records these exact values,
    nothing is written a second time and the manifest is rewritten to
    byte-identical content (its own `checked_at` reused, not refreshed) --
    a second `install` call of the same version adds no second copy.

    Never opens the currently-running artifact for writing: the target name
    always carries the version being installed, and a version equal to the
    running one never reaches here because `is_newer` refuses it upstream,
    so no code path in this function can collide with the running file.
    """
    verified = verify_digest(data, expected)
    if not verified:
        return None

    versions_dir = os.path.join(base, *VERSIONS_REL.split("/"))
    os.makedirs(versions_dir, exist_ok=True)
    target = os.path.join(versions_dir, name)
    rel_path = "/".join([VERSIONS_REL, name])
    digest_hex = hashlib.sha256(data).hexdigest()

    existing_manifest = read_manifest(base)
    matches_manifest = (
        existing_manifest is not None
        and existing_manifest.get("version") == version
        and existing_manifest.get("path") == rel_path
        and existing_manifest.get("sha256") == digest_hex
    )
    checked_at = existing_manifest.get("checked_at") if matches_manifest else None

    if not matches_manifest:
        needs_write = True
        if os.path.exists(target):
            with open(target, "rb") as fh:
                on_disk = fh.read()
            needs_write = hashlib.sha256(on_disk).hexdigest() != digest_hex
        if needs_write:
            partial = target + ".part"
            with open(partial, "wb") as fh:
                fh.write(data)
            os.replace(partial, target)

    write_manifest(base, version, rel_path, digest_hex, checked_at=checked_at)
    return target


def handoff(argv):
    """Read the pointer manifest under `update_root()` and, only when every
    guard passes, spawn the newer artifact as a fresh process and exit this
    one -- otherwise return with no effect. The guards, in order: a missing
    or invalid manifest; a manifest version that is not strictly newer than
    the running `itembank.__version__` (the same `is_newer` comparison, not
    a second one); a target that resolves to the artifact this process is
    already running from (the loop guard); a missing target file; and a
    target whose digest no longer matches what the manifest recorded (a
    pointer to changed bytes is not trustworthy).

    Spawns with `subprocess.Popen([sys.executable, target, *argv],
    close_fds=True)` and `sys.exit(0)` on every platform -- never a
    platform branch on the `exec` family, which has no real
    process-replacing implementation on Windows (Choice Point 6). The whole
    decision body is wrapped so any unexpected exception returns instead of
    propagating: a broken updater must never stop the tool from starting.
    """
    try:
        base = update_root()
        manifest = read_manifest(base)
        if manifest is None:
            return None

        import itembank  # local: avoid a module-load-order cycle through
                          # surfaces.cli, which this module's own caller
                          # (build.py's generated __main__.py) may import
                          # immediately after calling this function.
        if not is_newer(manifest.get("version"), itembank.__version__):
            return None

        rel_path = manifest.get("path")
        if not isinstance(rel_path, str) or not rel_path:
            return None
        target = os.path.abspath(os.path.join(base, *rel_path.split("/")))

        running = resources.archive_path()
        if running is not None and os.path.abspath(running) == target:
            return None

        if not os.path.exists(target):
            return None
        with open(target, "rb") as fh:
            data = fh.read()
        if hashlib.sha256(data).hexdigest() != manifest.get("sha256"):
            return None

        subprocess.Popen([sys.executable, target] + list(argv), close_fds=True)
    except SystemExit:
        raise
    except Exception:
        return None
    sys.exit(0)


def _checksum_fallback(release, name, timeout=30):
    """When a picked asset's `digest` field is absent, resolve its expected
    SHA-256 from the release's own `SHA256SUMS.txt` asset instead --
    `install()` itself stays network-free; its caller (`cmd_update`)
    resolves `expected` before calling it. Returns a `sha256:<hex>` string
    matching `verify_digest`'s expected shape, or `None` when the checksum
    asset is missing, unreachable, or does not name `name`. The fetch goes
    through `download_asset` and therefore through the module's single
    redirect-safe opener -- the same Authorization-stripping fix that
    covers the artifact fetch covers this one (CR-01 named both call
    sites; one seam covers both).
    """
    for asset in release.get("assets") or []:
        if not isinstance(asset, dict):
            continue
        if os.path.basename(str(asset.get("name") or "")) != CHECKSUMS_ASSET_NAME:
            continue
        url = asset.get("browser_download_url")
        if not isinstance(url, str) or not url:
            return None
        data = download_asset(url, timeout=timeout)
        if data is None:
            return None
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            return None
        digest = parse_sha256sums(text, name)
        return ("sha256:" + digest) if digest else None
    return None


def _digest_display(value):
    """The first twelve hex characters of a `sha256:<hex>`-shaped value, for
    the deliberately truncated mismatch line -- readable in a narrow
    terminal rather than a 64-character wall of hex.
    """
    if not value:
        return "unavailable"
    _, sep, hexval = value.partition(":")
    return (hexval if sep else value)[:12]


def cmd_update(a):
    """The explicit, talkative surface: `itembank update`. Branches to
    exactly one of six locked outcomes (UI-SPEC's Copywriting Contract) and
    never prints two. Exit codes: 0 when nothing was refused (up to date,
    installed, unreachable, rate-limited); 1 when a candidate was offered
    and rejected (a checksum mismatch or a version that is not newer) --
    a rejection is a result a script should be able to see.
    """
    cfg = settings.load_settings(".")
    repo = a.repo if a.repo else cfg["update"]["repo"]
    status = {}
    release = check_latest(repo, timeout=a.timeout, status=status)
    if release is None:
        if status.get("rate_limited"):
            print("GitHub rate-limited this check -- try again later.")
        else:
            print("Could not reach GitHub to check for updates (offline, or "
                  "the connection failed). Try again later.")
        return 0

    import itembank
    running = itembank.__version__
    running_parsed = parse_version(running)
    running_display = "v%d.%d.%d" % running_parsed if running_parsed else running

    tag = release.get("tag_name") if isinstance(release, dict) else None
    offered = parse_version(tag)
    asset = pick_asset(release)

    if offered is not None and running_parsed is not None and offered < running_parsed:
        latest_display = "v%d.%d.%d" % offered
        print("%s is not newer than the version you're running (%s) -- not "
              "installing it." % (latest_display, running_display))
        return 1

    if (asset is None or offered is None or running_parsed is None
            or offered == running_parsed):
        print("itembank is up to date (%s)." % running_display)
        return 0

    latest_display = "v%d.%d.%d" % offered
    if a.check:
        print("A new itembank version is available: %s (you're on %s). Run "
              "'itembank update' to install it." % (latest_display, running_display))
        return 0

    name, url, digest = asset
    print("Downloading itembank %s..." % latest_display)
    data = download_asset(url, timeout=a.timeout)
    if data is None:
        print("Could not reach GitHub to check for updates (offline, or "
              "the connection failed). Try again later.")
        return 0

    print("Verifying checksum...")
    expected = digest if digest is not None else _checksum_fallback(release, name,
                                                                     timeout=a.timeout)

    installed_path = install(update_root(), tag, name, data, expected)
    if installed_path is None:
        got_hex = hashlib.sha256(data).hexdigest()[:12]
        exp_hex = _digest_display(expected)
        print("Downloaded update failed checksum verification -- discarding "
              "it. Nothing was installed. (expected sha256:%s..., got "
              "sha256:%s...)" % (exp_hex, got_hex))
        return 1

    print("Installed %s at %s. Run itembank again to use it." %
          (latest_display, installed_path))
    return 0


def background_check(root, cfg):
    """The silent counterpart to `cmd_update`: informs, never installs, and
    is silent on every failure -- offline, unreachable, rate-limited are all
    indistinguishable from "nothing to say" here, per DEL-07's own
    "fails silently when offline". `root` is the base directory the
    manifest and versions directory live under (ordinarily
    `update_root()`'s return value; passed explicitly, like every other
    `base`-taking function in this module, so a caller -- and a test -- can
    point it at an isolated directory).

    Returns immediately unless `cfg["update_policy"]` permits an unconsented
    background request (`may_check`), and again unless `should_check` says
    the interval has elapsed -- an intent to check every launch does not
    become a request every launch. The whole body is wrapped so any
    exception is swallowed: a failing update check must never reach the
    daemon's startup path as a traceback.
    """
    try:
        cfg = cfg or {}
        policy = cfg.get("update_policy")
        if not may_check(policy, False):
            return
        update_cfg = cfg.get("update") or {}
        interval = update_cfg.get("check_interval_hours", 24)
        if not should_check(root, interval):
            return
        repo = update_cfg.get("repo")
        if not repo:
            return

        release = check_latest(repo)
        if release is None:
            return

        # A completed check (whether or not it found anything newer) resets
        # should_check's clock so a shared network is not asked again until
        # the interval elapses -- only when there is already a manifest to
        # refresh; a background check installs nothing, so it has no
        # version/path/sha256 of its own to record one for the first time.
        existing = read_manifest(root)
        if existing is not None:
            write_manifest(root, existing.get("version"), existing.get("path"),
                           existing.get("sha256"))

        import itembank
        running_parsed = parse_version(itembank.__version__)
        offered = parse_version(release.get("tag_name") if isinstance(release, dict)
                                else None)
        if offered is None or running_parsed is None or offered <= running_parsed:
            return

        print("A new itembank version is available: %s (you're on %s). Run "
              "'itembank update' to install it."
              % ("v%d.%d.%d" % offered, "v%d.%d.%d" % running_parsed))
    except Exception:
        return
