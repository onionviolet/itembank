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
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

import resources
import schema_validate


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

    `status`, when passed a dict, is populated with `status["rate_limited"]`
    so an explicit `itembank update` invocation can print the rate-limit
    line while a background check -- which never inspects `status` -- stays
    silent, per DEL-07's split between the two call sites.
    """
    if status is None:
        status = {}
    status["rate_limited"] = False
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
