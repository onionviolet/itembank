"""The LTI 1.3 surface (phase 999.4): Canvas LMS integration via LTI 1.3.

This module is an adapter over the existing JSON commands -- it calls the
daemon's `handle_api_*` functions in-process through `call_json_api`, never
parses a bank a second way, never decides correctness, and changes none of
`API_ROUTES` or the route-scope test (D-01). LTI 1.3's own OIDC launch is the
only authentication surface: no accounts, no passwords, no login page (D-02).

The launch spine (plan 01, wave 1):

1. Login initiation (platform -> tool, browser GET `/lti/login`): the tool
   validates `iss`/`client_id`/`target_link_uri` against the one platforms
   registration store (D-06), mints a one-time `nonce`+`state` pair, stores
   them briefly, and redirects to the platform's authorize endpoint.
2. Launch (platform -> tool, browser form POST `/lti/launch[/<stem>]`): the
   tool verifies the signed `id_token` against the platform's JWKS
   (signature, `iss`, `aud`, `nonce` one-time spend, `exp`,
   `deployment_id`) and only then hands the session to the wrapped daemon
   handlers (LTI-01).

`cryptography` (Apache-2.0 OR BSD-3-Clause) and `PyJWT` (MIT) are optional,
pinned, checksummed, license-reviewed imports (D-08): without them the LTI
surface refuses by name with the install command, and every non-LTI command
stays byte-identical. JOSE framing (base64url, JWS assembly) is hand-rolled
stdlib over `cryptography`'s primitives per 999.4-RESEARCH.md section 5;
PyJWT is the pinned, reviewed companion of the same supply-chain unit.

The LTI bind is opt-in: nothing listens publicly unless `lti.enabled` is
true, and the loopback default of every other surface is unchanged (D-05).
TLS is stdlib `ssl` with user-supplied cert/key paths; the documented
reverse-proxy posture is the alternative (`docs/lti-hosting.md`, plan 03).
"""
import base64
import html
import json
import os
import re
import secrets
import sys
import time
import urllib.parse
import urllib.request

from model import load, parse_lesson
from surfaces import daemon
from surfaces import presentation, quiz, theme
from surfaces import settings as settings_surface

import server


# ---------------------------------------------------------------------------
# Copy contract (999.4-UI-SPEC.md section 4, verbatim -- do not edit the
# strings; tests assert them byte-for-byte).
# ---------------------------------------------------------------------------

PRIVACY_LINE = ("This is a Canvas assignment. Answers are scored by the "
                "local runtime and the final score is sent to this course's "
                "gradebook when the assignment is complete.")
COMPLETION_OK = "Assignment complete. Your score has been sent to the gradebook."
COMPLETION_REFUSED = ("Assignment complete. Your score could not be sent to "
                      "the gradebook this time.")
UNVERIFIED_LAUNCH = ("This launch could not be verified. Close this window and "
                     "relaunch the assignment from Canvas.")
UNREGISTERED_PLATFORM = ("This Canvas site is not registered with this itembank "
                         "installation.")
MISSING_OBJECTIVE = ("No objective was selected for this assignment. Ask your "
                     "instructor to re-link it.")
CRYPTO_REFUSAL = ('The LTI surface needs its cryptography dependency. Run '
                  '"itembank lti doctor" for the install command.')
PICKER_PURPOSE = "Choose the itembank objective this assignment will run."
BANK_NO_OBJECTIVES = "This bank has no objectives."
SELECTION_CONFIRMED = 'Objective "{title}" selected.'
LINK_CONTROL = "Link this assignment"
CANCEL_CONTROL = "Cancel"
EMPTY_REGISTRY = ("No itembank banks are registered. Add a bank to this "
                  "installation first.")
DEEP_LINK_RETURN_FAILED = "Could not return the selection to Canvas."

# The D-09 network/privacy honesty statement: what leaves the machine. It
# lives in this module so the learner surface, `itembank lti` help/doctor and
# `docs/lti-hosting.md` can all render the same statement (D-09).
PRIVACY_STATEMENT = (
    "Privacy: item text travels to the learner's browser through the LMS, and "
    "the final score is copied to the course gradebook when the assignment is "
    "complete. itembank stores no gradebook, hosts nothing, and sends no "
    "telemetry and no learner evidence beyond the score."
)

# The pinned, license-reviewed optional dependencies (D-08, Directive 4a).
# The pin record with checksums lands in deps/lti-pins.txt (plan 03); the
# versions are kept in sync here so `lti doctor` can print the exact install
# command without reading another file.
CRYPTO_PINS = {"cryptography": "43.0.0", "PyJWT": "2.10.1"}

# Claim URIs from the LTI 1.3 / LTI Advantage namespaces.
AGS_ENDPOINT_CLAIM = "https://purl.imsglobal.org/spec/lti-ags/claim/endpoint"
AGS_SCOPE_LINEITEM = "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem"
AGS_SCOPE_SCORE = "https://purl.imsglobal.org/spec/lti-ags/scope/score"
AGS_SCOPE_RESULT = "https://purl.imsglobal.org/spec/lti-ags/scope/result"
DEEP_LINKING_CLAIM = "https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings"

LTI_LOGIN_PATH = "/lti/login"
LTI_LAUNCH_RE = re.compile(r"^/lti/launch(?:/(?P<stem>[^/]+))?$")
LTI_JWKS_PATH = "/lti/jwks"

# The five `/api/*` session routes the LTI handler family answers by calling
# the daemon's own handlers in-process (D-01). This is NOT `daemon.API_ROUTES`
# and changes nothing there: the daemon's route table, SURFACE_PARITY
# equivalent and `check_api_route_scope` stay byte-unchanged; this tuple only
# names which paths the *separate LTI handler family* wraps to the same
# functions.
LTI_API_WRAP = {
    "start": "handle_api_start",
    "next": "handle_api_next",
    "submit": "handle_api_submit",
    "hint": "handle_api_hint",
    "report": "handle_api_report",
}

# The D-05/D-06 named refusals use these copies.
ENABLED_REQUIRES_BASE_URL = (
    "LTI is enabled but lti.public_base_url is not set. Every URL the platform "
    "calls is derived from it; set it in itembank.json first."
)
ENABLED_REQUIRES_KEY = (
    "LTI is enabled but lti.tool_private_jwk_path is not set. The tool's RSA "
    "keypair is what the platform verifies launches against; generate one and "
    "register its public half with Canvas (see docs/lti-hosting.md)."
)
LTI_NOT_ENABLED = (
    "The LTI surface is disabled (lti.enabled is false). Set lti.enabled true "
    "and configure lti.platforms in itembank.json, then run "
    "`itembank lti serve` to bind the LTI handler family."
)


class LTIError(Exception):
    """A named refusal (D-06 discipline): `kind` is the stable machine name,
    `copy` the verbatim UI-SPEC line a learner/instructor page may render,
    and the message text carries the concrete detail for the operator log.
    """

    def __init__(self, kind, copy=None, detail=""):
        super().__init__(detail or copy or kind)
        self.kind = kind
        self.copy = copy
        self.detail = detail


# ---------------------------------------------------------------------------
# Optional dependency guard (D-08).
# ---------------------------------------------------------------------------

def crypto_available():
    """True when the optional, pinned `cryptography` and `PyJWT` imports are
    importable. The LTI surface refuses by name without them; every non-LTI
    command is byte-identical either way (degrade, never block). Tests
    simulate absence by monkeypatching this guard, never by uninstalling.
    """
    try:
        import cryptography  # noqa: F401
        import jwt          # noqa: F401
        return True
    except Exception:
        return False


def require_crypto():
    if not crypto_available():
        raise LTIError("crypto_missing", CRYPTO_REFUSAL,
                       "cryptography/PyJWT not installed")


# ---------------------------------------------------------------------------
# The one platforms registration store (D-06).
# ---------------------------------------------------------------------------

def load_registration(cfg, issuer=None, client_id=None):
    """Resolve the LTI settings block to one verified registration.

    Returns a dict with `enabled`, `public_base_url`, `tool_private_jwk_path`,
    `registry` (issuer -> platform record, at most one entry per issuer) and
    `platform` (the record matching `issuer`, or None when no issuer was
    asked for). Raises `LTIError` (a named refusal, D-06) on: lti disabled,
    enabled without `public_base_url` (D-05), enabled without the tool
    keypair path, a duplicate issuer, or an issuer/client_id the registry
    does not carry -- the refusal names both the issuer and the client_id.
    """
    lti = cfg.get("lti") if isinstance(cfg, dict) else None
    if not isinstance(lti, dict):
        raise LTIError("lti_missing", LTI_NOT_ENABLED, "settings has no lti block")
    if not lti.get("enabled"):
        raise LTIError("lti_disabled", LTI_NOT_ENABLED, "lti.enabled is false")
    base = lti.get("public_base_url")
    if not isinstance(base, str) or not base:
        raise LTIError("missing_public_base_url", ENABLED_REQUIRES_BASE_URL,
                       "lti.enabled is true but lti.public_base_url is empty")
    key_path = lti.get("tool_private_jwk_path")
    if not isinstance(key_path, str) or not key_path:
        raise LTIError("missing_tool_key", ENABLED_REQUIRES_KEY,
                       "lti.enabled is true but lti.tool_private_jwk_path is empty")
    platforms = lti.get("platforms")
    if not isinstance(platforms, list):
        raise LTIError("bad_platforms", UNREGISTERED_PLATFORM,
                       "lti.platforms is not an array")
    registry = {}
    for i, p in enumerate(platforms):
        if not isinstance(p, dict) or not p.get("issuer"):
            raise LTIError("bad_platform_record", UNREGISTERED_PLATFORM,
                           "lti.platforms[%d] has no issuer" % i)
        iss = p["issuer"]
        if iss in registry:
            raise LTIError("duplicate_issuer", UNREGISTERED_PLATFORM,
                           "issuer %r registered more than once" % iss)
        registry[iss] = p
    platform = None
    if issuer is not None:
        platform = registry.get(issuer)
        if platform is None:
            raise LTIError(
                "unknown_issuer", UNREGISTERED_PLATFORM,
                "no LTI platform registered for issuer %r with client_id %r"
                % (issuer, client_id if client_id is not None else ""))
        if client_id is not None and platform.get("client_id") != client_id:
            raise LTIError(
                "unknown_client", UNREGISTERED_PLATFORM,
                "client_id %r is not registered for issuer %r (registered: %r)"
                % (client_id, issuer, platform.get("client_id")))
    return {"enabled": True, "public_base_url": base,
            "tool_private_jwk_path": key_path,
            "registry": registry, "platform": platform}


# ---------------------------------------------------------------------------
# JOSE framing and JWKS verification (LTI-01). Hand-rolled stdlib over
# cryptography's primitives (RESEARCH section 5).
# ---------------------------------------------------------------------------

_JWKS_CACHE = {"url": None, "ts": 0.0, "keys": None}
JWKS_TTL_SECONDS = 300.0
JWKS_FETCH_TIMEOUT = 10


def _b64u_decode(s):
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _b64u_encode(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _jwk_to_public_key(jwk):
    """Build a `cryptography` RSAPublicKey from an RSA JWK (kty/n/e)."""
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    n = int.from_bytes(_b64u_decode(jwk["n"]), "big")
    e = int.from_bytes(_b64u_decode(jwk["e"]), "big")
    return rsa.RSAPublicNumbers(e, n).public_key(default_backend())


def _fetch_jwks(jwks_url):
    """Fetch the platform's JWKS with a bounded cache (TTL, one URL). An
    unreachable or malformed JWKS is a named refusal, never a hang or crash
    (T-994-06).
    """
    now = time.time()
    cached = _JWKS_CACHE
    if cached["url"] == jwks_url and cached["keys"] is not None \
            and now - cached["ts"] < JWKS_TTL_SECONDS:
        return cached["keys"]
    try:
        with urllib.request.urlopen(jwks_url, timeout=JWKS_FETCH_TIMEOUT) as resp:
            doc = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        raise LTIError("jwks_unreachable", UNVERIFIED_LAUNCH,
                       "could not fetch platform JWKS from %s: %s"
                       % (jwks_url, exc.__class__.__name__))
    keys = doc.get("keys") if isinstance(doc, dict) else None
    if not isinstance(keys, list) or not keys:
        raise LTIError("jwks_empty", UNVERIFIED_LAUNCH,
                       "JWKS at %s carried no keys" % jwks_url)
    cached.update({"url": jwks_url, "ts": now, "keys": keys})
    return keys


def _verify_rs256(signing_input, signature, public_key):
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    try:
        public_key.verify(signature, signing_input,
                          padding.PKCS1v15(), hashes.SHA256())
    except InvalidSignature:
        raise LTIError("bad_signature", UNVERIFIED_LAUNCH,
                       "id_token signature did not verify against the JWKS")


class NonceStore:
    """The in-memory, short-TTL, one-time nonce/state store for the OIDC
    dance (D-02: a protocol countermeasure, not an account system). Keyed by
    `state`; a nonce is spent on first successful `take`, so a replay of a
    spent state is refused by name (T-994-02). Capped and pruned so an
    attacker flooding login initiations cannot grow it without bound
    (T-994-06).
    """

    def __init__(self, ttl=300, max_entries=4096):
        self.ttl = ttl
        self.max_entries = max_entries
        self._entries = {}

    def mint(self, issuer="", client_id=""):
        state = secrets.token_urlsafe(24)
        nonce = secrets.token_urlsafe(24)
        self._prune()
        if len(self._entries) >= self.max_entries:
            raise LTIError("nonce_store_full", UNVERIFIED_LAUNCH,
                           "nonce store is full; refusing new logins")
        self._entries[state] = {"nonce": nonce,
                                "issuer": issuer, "client_id": client_id,
                                "expires": time.time() + self.ttl}
        return state, nonce

    def peek(self, state):
        """The platform identity recorded when `state` was minted, or None.
        The launch handler resolves the registration from THIS (the state the
        tool itself issued at login), never from an unverified `iss` claim."""
        entry = self._entries.get(state)
        if entry is None:
            return None
        return {"issuer": entry.get("issuer", ""),
                "client_id": entry.get("client_id", "")}

    def take(self, state, nonce):
        entry = self._entries.get(state)
        if entry is None or entry["nonce"] != nonce:
            return False
        del self._entries[state]             # one-time spend
        if time.time() > entry["expires"]:
            return False
        return True

    def _prune(self):
        now = time.time()
        self._entries = {s: e for s, e in self._entries.items()
                         if e["expires"] > now}
        if len(self._entries) >= self.max_entries:
            oldest = sorted(self._entries, key=lambda s: self._entries[s]["expires"])
            for s in oldest[:max(0, len(self._entries) - self.max_entries + 1)]:
                del self._entries[s]


def verify_id_token(token, registration, nonce_store, state):
    """Verify a launch `id_token` against the registered platform, in order:
    JOSE framing -> RS256 signature against the platform JWKS -> `iss` ->
    `aud` -> `nonce` (one-time spend) -> `exp` -> `deployment_id`. Returns
    the claims dict on success; every failure is a named `LTIError` naming
    the first failed check (LTI-01).
    """
    platform = registration["platform"]
    if platform is None:
        raise LTIError("no_platform", UNREGISTERED_PLATFORM,
                       "no platform resolved for this launch")
    if not isinstance(token, str) or token.count(".") != 2:
        raise LTIError("malformed_token", UNVERIFIED_LAUNCH,
                       "id_token is not a three-part JOSE token")
    header_b64, payload_b64, sig_b64 = token.split(".")
    try:
        header = json.loads(_b64u_decode(header_b64))
        claims = json.loads(_b64u_decode(payload_b64))
        signature = _b64u_decode(sig_b64)
    except Exception as exc:
        raise LTIError("malformed_token", UNVERIFIED_LAUNCH,
                       "id_token JOSE framing could not be decoded: %s"
                       % exc.__class__.__name__)
    if not isinstance(header, dict) or not isinstance(claims, dict):
        raise LTIError("malformed_token", UNVERIFIED_LAUNCH,
                       "id_token header/payload are not JSON objects")
    if header.get("alg") != "RS256":
        raise LTIError("bad_alg", UNVERIFIED_LAUNCH,
                       "id_token alg must be RS256, got %r" % header.get("alg"))
    keys = _fetch_jwks(platform.get("jwks_url") or "")
    kid = header.get("kid")
    key = next((k for k in keys if k.get("kid") == kid), None) if kid else None
    if key is None:
        key = keys[0] if keys else None
    if key is None or key.get("kty") != "RSA":
        raise LTIError("unknown_key", UNVERIFIED_LAUNCH,
                       "no RSA JWKS key matches the id_token kid %r" % kid)
    try:
        public_key = _jwk_to_public_key(key)
    except Exception as exc:
        raise LTIError("bad_jwk", UNVERIFIED_LAUNCH,
                       "JWKS key could not be parsed: %s" % exc.__class__.__name__)
    signing_input = (header_b64 + "." + payload_b64).encode("ascii")
    _verify_rs256(signing_input, signature, public_key)

    # Claim checks, in order, first failure names itself.
    if claims.get("iss") != platform.get("issuer"):
        raise LTIError("bad_iss", UNVERIFIED_LAUNCH,
                       "iss %r does not match registered issuer %r"
                       % (claims.get("iss"), platform.get("issuer")))
    aud = claims.get("aud")
    allowed_aud = platform.get("client_id")
    aud_ok = aud == allowed_aud or \
        (isinstance(aud, list) and allowed_aud in aud)
    if not aud_ok:
        raise LTIError("bad_aud", UNVERIFIED_LAUNCH,
                       "aud %r does not match registered client_id %r"
                       % (aud, allowed_aud))
    if not nonce_store.take(state, claims.get("nonce")):
        raise LTIError("bad_nonce", UNVERIFIED_LAUNCH,
                       "nonce missing, unknown, expired, or already spent")
    exp = claims.get("exp")
    if not isinstance(exp, (int, float)) or time.time() > exp:
        raise LTIError("expired", UNVERIFIED_LAUNCH,
                       "id_token is expired (exp=%r)" % exp)
    deployments = platform.get("deployments") or []
    if claims.get("deployment_id") not in deployments:
        raise LTIError("unknown_deployment", UNREGISTERED_PLATFORM,
                       "deployment_id %r is not in the registration allowlist %r"
                       % (claims.get("deployment_id"), deployments))
    if not claims.get("sub"):
        raise LTIError("missing_sub", UNVERIFIED_LAUNCH,
                       "id_token carries no sub claim")
    claims["__verified"] = True
    return claims


def sign_jwt_rs256(claims, private_key_pem):
    """Hand-rolled RS256 JWT signing over cryptography (RESEARCH section 5):
    used for the tool-side AGS client-credentials assertion (plan 03) and
    nothing else. Returns the compact JOSE string."""
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    header = {"alg": "RS256", "typ": "JWT"}
    header_b64 = _b64u_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = _b64u_encode(json.dumps(claims).encode("utf-8"))
    signing_input = (header_b64 + "." + payload_b64).encode("ascii")
    key = serialization.load_pem_private_key(private_key_pem, password=None)
    signature = key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    return header_b64 + "." + payload_b64 + "." + _b64u_encode(signature)


def tool_public_jwk(private_key_pem):
    """The public JWK half of the tool's RSA keypair, for the JWKS endpoint
    and for pasting into the platform's developer-key configuration."""
    from cryptography.hazmat.primitives import serialization
    key = serialization.load_pem_private_key(private_key_pem, password=None)
    pub = key.public_key()
    numbers = pub.public_numbers()
    return {"kty": "RSA", "kid": "itembank-tool",
            "n": _b64u_encode(numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")),
            "e": _b64u_encode(numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")),
            "alg": "RS256", "use": "sig"}


def load_tool_private_key(cfg):
    """Read the tool's RSA private key (PEM) from `lti.tool_private_jwk_path`.
    A missing/unreadable key is a named refusal."""
    registration = load_registration(cfg)
    path = registration["tool_private_jwk_path"]
    try:
        with open(path, "rb") as fh:
            return fh.read(), registration
    except OSError as exc:
        raise LTIError("tool_key_unreadable", LTI_NOT_ENABLED,
                       "cannot read tool_private_jwk_path %s: %s"
                       % (path, exc))


# ---------------------------------------------------------------------------
# The in-process JSON-command wrap (D-01).
# ---------------------------------------------------------------------------

class _HeaderDict(dict):
    def get(self, key, default=None):
        return dict.get(self, key, default)


class _ShimHandler:
    """The smallest object that satisfies what the daemon's `handle_api_*`
    functions read off a `BaseHTTPRequestHandler`: `read_json`, `headers`,
    `banks`, `root`, `sessions`, `client_address`, and the `send_*` capture
    methods. `call_json_api` builds one per call, so the LTI surface is an
    adapter over the daemon's own handlers -- the same functions
    `API_ROUTES` names -- never a second implementation (D-01, LTI-02).
    """

    def __init__(self, payload, ctx, headers=None,
                 client_address=("127.0.0.1", 0)):
        self._payload = payload if isinstance(payload, dict) else {}
        self.banks = ctx.get("banks") or {}
        self.root = ctx.get("root") or "."
        self.sessions = ctx.get("sessions") or {}
        self.headers = _HeaderDict(headers or {})
        self.client_address = client_address
        self.status_code = 200
        self.json_value = None
        self.error_status = None
        self.error_message = ""
        self.body = b""

    def read_json(self):
        return self._payload

    def send_bytes(self, body, content_type, status=200):
        self.status_code = status
        self.body = body if isinstance(body, bytes) else str(body).encode("utf-8")
        if self.json_value is None and content_type.startswith("application/json"):
            try:
                self.json_value = json.loads(self.body.decode("utf-8"))
            except ValueError:
                self.json_value = None

    def send_json(self, payload):
        self.json_value = payload
        self.status_code = 200

    def send_error(self, status, message=None):
        self.status_code = status
        self.error_status = status
        self.error_message = message or ""

    def send_not_found(self, name):
        self.status_code = 404
        self.error_status = 404
        self.error_message = "not found: %s" % name

    def send_server_error(self, exc):
        self.status_code = 500
        self.error_status = 500
        self.error_message = "internal error"


def call_json_api(name, payload, ctx, headers=None):
    """Call one daemon JSON-command handler in-process and return its JSON
    payload. `name` is one of `LTI_API_WRAP`'s keys; `ctx` carries the
    allowlists (`banks`, `root`, `sessions`) exactly like the daemon handler
    class does. A handler-level refusal (4xx) raises `LTIError("api_refused")`
    naming the status; the JSON value of a successful call is returned.
    """
    handler_name = LTI_API_WRAP.get(name)
    if handler_name is None:
        raise LTIError("unknown_api", detail="no wrapped api command %r" % name)
    fn = getattr(daemon, handler_name, None)
    if fn is None:
        raise LTIError("unknown_api", detail="daemon has no %s" % handler_name)
    shim = _ShimHandler(payload, ctx, headers=headers)
    fn(shim)
    if shim.status_code >= 400:
        raise LTIError("api_refused", detail="%s refused: HTTP %d %s"
                       % (name, shim.status_code, shim.error_message))
    return shim.json_value


# ---------------------------------------------------------------------------
# The OIDC login + launch handler family (D-02, LTI-01). A sibling family on
# server.py's Handler base -- no new /api/* route, no change to API_ROUTES.
# ---------------------------------------------------------------------------

class OIDCLoginHandler(server.Handler):
    """Step 1 of the OIDC dance: `GET /lti/login` (login initiation). The
    platform's query params (`iss`, `login_hint`, `target_link_uri`,
    `client_id`, `deployment_id`) are validated against the registration; a
    registered launch is redirected to the platform authorize endpoint with
    a freshly minted nonce+state (D-02).

    State is pinned as class attributes before the bind starts, the same
    closure-over-startup-state shape `DaemonHandler` uses: `banks` (stem ->
    path allowlist), `root`, `sessions`, `settings` (the loaded settings
    dict) and `nonce_store`. The LTIHandler subclass shares them through
    inheritance, so a login initiated by one is spent by the other.
    """

    banks = {}
    root = "."
    sessions = {}
    settings = {}
    nonce_store = NonceStore()

    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path
        if path == LTI_LOGIN_PATH:
            self._login_initiation()
        elif path == LTI_JWKS_PATH:
            self._tool_jwks()
        else:
            self.send_error(404)

    # -- helpers ------------------------------------------------------------

    def _send_refusal(self, exc):
        """The UI-SPEC 2.1 refusal: the verbatim copy line, no page, no
        redirect, no hint beyond the named failure class (D-06)."""
        body = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
                "<title>Launch refused</title></head><body><p>%s</p></body></html>"
                % html.escape(exc.copy or exc.kind))
        self.send_bytes(body.encode("utf-8"), "text/html; charset=utf-8",
                        status=403)

    def _resolve_registration(self, params):
        cfg = self.settings if isinstance(self.settings, dict) else {}
        return load_registration(
            cfg, issuer=params.get("iss"), client_id=params.get("client_id"))

    def _login_initiation(self):
        params = {}
        for key, values in urllib.parse.parse_qs(
                urllib.parse.urlsplit(self.path).query).items():
            params[key] = values[0] if values else ""
        try:
            require_crypto()
            registration = self._resolve_registration(params)
            target = params.get("target_link_uri", "")
            base = registration["public_base_url"].rstrip("/")
            if not target or not target.startswith(base):
                raise LTIError(
                    "bad_target_link_uri", UNVERIFIED_LAUNCH,
                    "target_link_uri %r is not under public_base_url %s"
                    % (target, base))
            state, nonce = self.nonce_store.mint(
                issuer=registration["platform"]["issuer"],
                client_id=registration["platform"]["client_id"])
            location = _authorize_redirect(registration, params, target,
                                           state, nonce)
            self.send_response(302)
            self.send_header("Location", location)
            self.send_header("Content-Length", "0")
            self.end_headers()
        except LTIError as exc:
            print("  lti login refused: %s (%s)" % (exc.kind, exc))
            self._send_refusal(exc)

    def _tool_jwks(self):
        """`GET /lti/jwks` -- the tool's own public JWK as a JWKS document,
        for pasting into (or serving to) the platform's developer-key
        configuration (D-06)."""
        try:
            require_crypto()
            pem, _registration = load_tool_private_key(self.settings)
            jwk = tool_public_jwk(pem)
            self.send_bytes(json.dumps({"keys": [jwk]}).encode("utf-8"),
                            "application/json")
        except LTIError as exc:
            self._send_refusal(exc)


def _authorize_redirect(registration, params, target_link_uri, state, nonce):
    """The step-2 authorize redirect URL (RESEARCH section 1): the tool bounces
    the browser to the platform's authorize endpoint carrying the minted
    nonce/state so the launch cannot be forged or replayed. `params` carries
    the login-initiation query values as plain strings (what
    `_login_initiation` normalizes them to)."""
    query = urllib.parse.urlencode({
        "response_type": "id_token",
        "client_id": registration["platform"]["client_id"],
        "redirect_uri": target_link_uri,
        "login_hint": params.get("login_hint", ""),
        "scope": "openid",
        "state": state,
        "nonce": nonce,
        "prompt": "none",
        "response_mode": "form_post",
    })
    sep = "&" if "?" in registration["platform"]["auth_endpoint"] else "?"
    return registration["platform"]["auth_endpoint"] + sep + query


class LTIHandler(OIDCLoginHandler):
    """The full LTI handler family: the OIDC login initiation and tool JWKS
    (inherited), plus the launch POSTs and the in-process `/api/*` JSON wrap.
    The learner/instructor pages served by this family are the SAME pages
    every other surface renders -- this handler never reimplements a renderer
    or a scorer (D-01/D-03).

    `launch_ctx` maps a one-time token (embedded in a rendered player page's
    BOOT) to the verified launch's claims + platform issuer, and then -- once
    the page's `/api/start` has run -- maps the created session_id to the
    same entry, so a later completion can reach plan 03's passback. Tokens
    are one-use; session ids are server-minted and random, so nothing here is
    learner-controllable.
    """

    launch_ctx = {}

    def do_POST(self):
        path = urllib.parse.urlsplit(self.path).path
        m = LTI_LAUNCH_RE.match(path)
        if m:
            self._launch(m.group("stem") or "")
            return
        # The embedded player posts to the same relative /api/* paths the
        # daemon serves; this family wraps them to the daemon's own handlers
        # in-process (D-01). LTI_API_WRAP keys are the bare command names.
        if path.startswith("/api/") \
                and path.rsplit("/", 1)[-1] in LTI_API_WRAP:
            self._api_wrap(path)
            return
        self.send_error(404)

    def _read_form(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode("utf-8", "replace")
        return urllib.parse.parse_qs(raw)

    def _launch(self, stem):
        """Step 3 of the dance: verify the posted `id_token` and hand the
        launch to the wrapped daemon commands. The plan-01 tracer behavior
        (verified launch -> in-process `/api/start` JSON) is the fallback for
        every message type the UI plans do not branch on; plan 02 adds the
        LtiDeepLinkingRequest and LtiResourceLinkRequest branches."""
        try:
            require_crypto()
            form = self._read_form()
            token = (form.get("id_token") or [""])[0]
            state = (form.get("state") or [""])[0]
            entry = self.nonce_store.peek(state)
            if entry is None:
                raise LTIError("bad_nonce", UNVERIFIED_LAUNCH,
                               "no login initiation recorded for this state")
            registration = load_registration(
                self.settings, issuer=entry["issuer"],
                client_id=entry["client_id"])
            claims = verify_id_token(token, registration, self.nonce_store, state)
            ctx = {"banks": self.banks, "root": self.root,
                   "sessions": self.sessions}
            message_type = claims.get("message_type")
            if message_type == "LtiDeepLinkingRequest":
                page = handle_deep_link_request(claims, registration, ctx)
                self._send_page(page, registration)
            elif message_type == "LtiResourceLinkRequest":
                page, _token = handle_resource_link(
                    claims, registration, stem, ctx, self.launch_ctx)
                self._send_page(page, registration)
            else:
                # The plan-01 tracer fallback, kept for message types the UI
                # plans do not branch on: a verified launch reaches the
                # daemon's /api/start in-process and returns its JSON.
                result = call_json_api(
                    "start",
                    {"bank": stem, "count": 10, "mode": "practice"},
                    ctx, headers={k: v for k, v in self.headers.items()})
                self.send_json(result)
        except LTIError as exc:
            print("  lti launch refused: %s (%s)" % (exc.kind, exc))
            self._send_refusal(exc)

    def _send_page(self, body, registration):
        """A learner/instructor page with the frame-ancestors CSP derived
        from the registration issuer (UI-SPEC section 1): the LMS origin may
        frame the tool and no other origin may (T-994-11)."""
        body = body.encode("utf-8") if isinstance(body, str) else body
        csp = frame_ancestors_csp(registration)
        name, _, value = csp.partition(": ")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _api_wrap(self, path):
        """The embedded learner page's `/api/*` POSTs, answered by calling the
        daemon's own handlers in-process (D-01) -- the page is the same quiz
        surface, so it posts to the same relative paths. On `/api/start` the
        launch-context token from BOOT is bound to the created session; on a
        completing `/api/submit` the passback signal is attached so the page
        renders the verbatim completion line (plan 02 stub, plan 03 real)."""
        try:
            payload = self.read_json()
        except (ValueError, TypeError) as exc:
            self.send_error(400, "malformed JSON body: %s" % exc)
            return
        name = path.rsplit("/", 1)[-1]
        headers = {k: v for k, v in self.headers.items()}
        try:
            result = call_json_api(name, payload,
                                   {"banks": self.banks, "root": self.root,
                                    "sessions": self.sessions},
                                   headers=headers)
        except LTIError as exc:
            self.send_error(400, exc.detail or exc.kind)
            return
        if name == "start" and isinstance(result, dict) \
                and result.get("session_id"):
            token = payload.get("lti_ctx") if isinstance(payload, dict) else None
            entry = self.launch_ctx.pop(token, None) if isinstance(token, str) \
                else None
            if entry is not None:
                self.launch_ctx[result["session_id"]] = entry
        elif name == "submit" and isinstance(result, dict) \
                and result.get("status") == "complete":
            sid = payload.get("session_id") if isinstance(payload, dict) else None
            entry = self.launch_ctx.get(sid) if isinstance(sid, str) else None
            if entry is not None:
                session_file = daemon.session_index(self.root).get(sid)
                if session_file:
                    try:
                        pb = maybe_passback(
                            session_file, entry.get("claims") or {},
                            entry.get("issuer") or "", self.settings)
                    except LTIError as exc:
                        pb = ("refused", exc.detail or exc.kind)
                    result["lti_completion"] = {
                        "ok": pb[0] == "ok", "line": completion_line(pb)}
        self.send_json(result)


# ---------------------------------------------------------------------------
# The two real surfaces (plan 02, UI-CONTRACT): the instructor deep-link
# picker and the embedded learner player. Both render through the existing
# pages (presentation.surface_shell / quiz.page_for) -- no new renderer, no
# second projection (D-01/D-03).
# ---------------------------------------------------------------------------

def frame_ancestors_csp(registration):
    """`Content-Security-Policy: frame-ancestors <lms-origin>` derived from
    the registration's issuer (UI-SPEC section 1, T-994-11): the LMS origin
    may frame the tool and no other origin may. The issuer is a URL
    (`https://canvas.instructure.com`); the CSP value is its origin."""
    issuer = (registration.get("platform") or {}).get("issuer") or ""
    if "://" not in issuer:
        issuer = "https://" + issuer
    parts = urllib.parse.urlsplit(issuer)
    origin = parts.scheme + "://" + parts.netloc
    return "Content-Security-Policy: frame-ancestors " + origin


def objective_rows(banks):
    """The picker's data: one `(bank_stem, [distinct objective values])`
    entry per registered bank, in stem order. The objective values are
    exactly what `handle_api_start`/`selection.select` resolve (D-07: "the
    same objective ids handle_api_start resolves") -- the bank's
    `[OBJECTIVE:]` references -- never stems, keys, or counts (T-994-07).
    """
    rows = []
    for stem in sorted(banks or {}):
        path = banks[stem]
        try:
            qs = load(path)
        except Exception:
            continue
        seen = []
        for q in qs:
            obj = q.get("objective")
            if obj and obj not in seen:
                seen.append(obj)
        rows.append((stem, seen))
    return rows


PICKER_JS = r"""const RETURN_URL = "__DL_RETURN__";
const LINK_BASE = "__DL_BASE__";
const FAILED_COPY = "__DL_FAILED__";
const RETRY_COPY = "__DL_RETRY__";
const CANCEL_COPY = "__DL_CANCEL__";
const CONFIRM_COPY = '__DL_CONFIRM__';
let selected = null;
const rows = document.querySelectorAll(".prow");
const confirmEl = document.getElementById("lti-confirm");
const linkBtn = document.getElementById("lti-link");
rows.forEach(r => r.addEventListener("click", () => {
  rows.forEach(x => x.classList.remove("sel"));
  r.classList.add("sel");
  selected = {bank: r.dataset.bank, objective: r.dataset.objective};
  confirmEl.hidden = false;
  confirmEl.textContent = CONFIRM_COPY.replace("{title}", selected.objective);
  linkBtn.hidden = false;
}));
function postResponse(contentItems){
  const form = document.createElement("form");
  form.method = "POST"; form.action = RETURN_URL; form.hidden = true;
  const input = document.createElement("input");
  input.type = "hidden"; input.name = "content_items";
  input.value = JSON.stringify(contentItems);
  form.appendChild(input);
  document.body.appendChild(form);
  try { form.submit(); }
  catch(err){
    const host = document.getElementById("lti-picker") || document.body;
    const box = document.createElement("p");
    box.className = "status"; box.textContent = FAILED_COPY;
    host.appendChild(box);
    const retry = document.createElement("button");
    retry.type = "button"; retry.className = "go";
    retry.textContent = RETRY_COPY;
    retry.onclick = () => { location.reload(); };
    host.appendChild(retry);
    const cancel = document.createElement("button");
    cancel.type = "button"; cancel.className = "go ghost";
    cancel.textContent = CANCEL_COPY;
    cancel.onclick = () => { location.href = "about:blank"; };
    host.appendChild(cancel);
  }
}
document.getElementById("lti-link").addEventListener("click", () => {
  if(!selected) return;
  postResponse([{type: "ltiResourceLink",
                 url: LINK_BASE + "/lti/launch/" + selected.bank,
                 title: selected.objective,
                 custom: {objective: selected.objective, mode: "practice"}}]);
});
document.getElementById("lti-cancel").addEventListener("click", () => {
  postResponse([]);
});
"""


def picker_page(rows, return_url, public_base_url):
    """The instructor deep-link picker (UI-SPEC section 3): one 44px row per
    objective in the local bank registry (id + title only -- no stems, no
    keys, no counts, T-994-07), the purpose line, `Link this assignment`,
    and `Cancel`. Empty registry renders the empty-registry line; a bank
    with no objectives is refused by name. Every string is verbatim
    UI-SPEC section 4."""
    body = ['<p class="lti-purpose">%s</p>' % html.escape(PICKER_PURPOSE)]
    body.append("<style>"
                ".lti-picker{display:flex;flex-direction:column;gap:8px;"
                "margin:0 0 14px}"
                ".prow{min-height:44px;display:flex;align-items:center;"
                "justify-content:space-between;gap:12px;text-align:left;"
                "background:var(--card);border:1px solid var(--line);"
                "border-radius:10px;padding:0 14px;font:inherit;cursor:pointer}"
                ".prow:hover{border-color:var(--accent)}"
                ".prow.sel{border-color:var(--accent);"
                "box-shadow:0 0 0 2px var(--accent-soft)}"
                ".pbank{color:var(--mut);font-size:13px}"
                ".lti-purpose{margin-bottom:12px}"
                "</style>")
    body.append('<div class="lti-picker" id="lti-picker">')
    if not rows:
        body.append('<p class="status">%s</p>' % html.escape(EMPTY_REGISTRY))
    else:
        for stem, objectives in rows:
            if not objectives:
                body.append('<p class="status">%s &mdash; %s</p>'
                            % (html.escape(stem), html.escape(BANK_NO_OBJECTIVES)))
                continue
            for obj in objectives:
                body.append(
                    '<button type="button" class="prow" data-bank="%s" '
                    'data-objective="%s">%s <span class="pbank">%s</span></button>'
                    % (html.escape(stem, quote=True),
                       html.escape(obj, quote=True),
                       html.escape(obj), html.escape(stem)))
    body.append('</div>')
    body.append('<p class="status" id="lti-confirm" data-field="lti-confirm" '
                'hidden></p>')
    body.append('<div class="act">')
    body.append('<button type="button" class="go" id="lti-link" hidden>%s</button>'
                % html.escape(LINK_CONTROL))
    body.append('<button type="button" class="go ghost" id="lti-cancel">%s</button>'
                % html.escape(CANCEL_CONTROL))
    body.append('</div>')
    script = (PICKER_JS
              .replace("__DL_RETURN__", html.escape(return_url, quote=True))
              .replace("__DL_BASE__", html.escape(public_base_url.rstrip("/"),
                                                  quote=True))
              .replace("__DL_FAILED__", html.escape(DEEP_LINK_RETURN_FAILED))
              .replace("__DL_RETRY__", "Retry")
              .replace("__DL_CANCEL__", html.escape(CANCEL_CONTROL))
              .replace("__DL_CONFIRM__",
                       html.escape(SELECTION_CONFIRMED, quote=True)))
    body.append("<script>" + script + "</script>")
    page = presentation.surface_shell(
        "Link an itembank objective", "\n".join(body),
        back=None, wide=False)
    return page


def deep_link_response(content_items, return_url):
    """The LtiDeepLinkingResponse as an auto-submitting HTML form POST to the
    platform's deep_link_return_url (RESEARCH section 3): exactly the
    `content_items` the selection produced -- one ltiResourceLink carrying
    the objective custom param, or an empty list for Cancel. The response is
    an unsigned form POST by design; the trust anchor is the verified
    LtiDeepLinkingRequest launch that carried deep_linking_settings
    (T-994-09)."""
    items_json = json.dumps(content_items, ensure_ascii=False)
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<title>Returning selection to Canvas</title></head><body>'
            '<form id="dl-return" method="post" action="%s">'
            '<input type="hidden" name="content_items" value="%s">'
            '</form><script>document.getElementById("dl-return").submit();'
            '</script></body></html>'
            % (html.escape(return_url, quote=True),
               html.escape(items_json, quote=True)))


def handle_deep_link_request(claims, registration, ctx):
    """A verified LtiDeepLinkingRequest launch -> the picker page (D-07,
    LTI-04). The return URL comes from the signed deep_linking_settings
    claim, never from an unsigned source (T-994-09)."""
    dls = claims.get(DEEP_LINKING_CLAIM) or {}
    if not isinstance(dls, dict):
        dls = {}
    return_url = dls.get("deep_link_return_url")
    if not isinstance(return_url, str) or not return_url:
        raise LTIError("no_deep_link_return", DEEP_LINK_RETURN_FAILED,
                       "deep_linking_settings carries no deep_link_return_url")
    rows = objective_rows(ctx.get("banks"))
    return picker_page(rows, return_url, registration["public_base_url"])


def player_page(bank_path, stem, objective, mode, registration, ctx,
                launch_token=""):
    """The embedded learner player (UI-SPEC section 2): the existing quiz
    serve page for one bank/objective, rendered by the same `page_for`
    projection the daemon serves (D-01 -- no new renderer), with the D-09
    privacy line as the session framing and the objective + one-time launch
    token riding in BOOT so the page's own `/api/start` starts the sitting
    on that objective. The page carries no key, why-best, distractor
    analysis, or tier content: `serve=True` is what makes `page_for` omit
    them (D-03, LTI-03)."""
    qs = load(bank_path)
    lesson = parse_lesson(bank_path)
    lesson_slugs = set(h["slug"] for h in lesson["headings"]) if lesson else set()
    theme_block = theme.theme_css(settings_surface.load_settings(ctx["root"]))
    framing = ('<div class="lti-framing" data-field="lti-framing">'
               '<p class="status">%s</p></div>' % html.escape(PRIVACY_LINE))
    boot_extra = {"objective": objective}
    if launch_token:
        boot_extra["lti_ctx"] = launch_token
    _mix, page = quiz.page_for(
        bank_path, qs, serve=True, reveal=False,
        bank_stem=stem, mode=mode,
        lesson_base="", lesson_slugs=lesson_slugs, theme_css=theme_block,
        lti_framing=framing, boot_extra=boot_extra)
    return page


def handle_resource_link(claims, registration, stem, ctx, launch_store):
    """A verified LtiResourceLinkRequest launch -> the embedded player
    (D-07, LTI-04): resolve the custom objective through the bank's item
    allowlist (never a path, T-994-10), refuse unresolvable objectives with
    the exact UI-SPEC line, and render the quiz serve page for that
    objective. Returns (page, launch_token); the token binds the verified
    claims to the session once the page starts it."""
    custom = claims.get("custom") or {}
    if not isinstance(custom, dict):
        custom = {}
    objective = custom.get("objective")
    if not isinstance(objective, str) or not objective:
        raise LTIError("missing_objective", MISSING_OBJECTIVE,
                       "resource-link launch carries no custom objective")
    path = (ctx.get("banks") or {}).get(stem)
    if path is None:
        raise LTIError("unknown_bank", MISSING_OBJECTIVE,
                       "no registered bank stem %r" % stem)
    qs = load(path)
    if not any(q.get("objective") == objective for q in qs):
        raise LTIError("unresolvable_objective", MISSING_OBJECTIVE,
                       "objective %r is not in bank %s" % (objective, stem))
    mode = custom.get("mode") or "practice"
    if mode not in daemon.SESSION_MODES:
        mode = "practice"
    token = secrets.token_urlsafe(24)
    launch_store[token] = {
        "claims": claims, "issuer": registration["platform"]["issuer"]}
    return player_page(path, stem, objective, mode, registration, ctx,
                       launch_token=token), token


def maybe_passback(session_file, claims, issuer, cfg):
    """The plan-02 stub of the completion-time passback interface, with a
    clear contract plan 03 fills in without touching the copy: returns a
    `(status, reason)` pair -- `("not_configured", None)` when the launch
    carried no AGS scope (the opt-in gate, D-04), `("ok", None)` on a
    successful gradebook copy, `("refused", reason)` on any refusal (plan
    03). `completion_line` maps the pair to the verbatim UI-SPEC line."""
    return ("not_configured", None)


def completion_line(passback):
    """The UI-SPEC section-4 completion line for a passback outcome: the
    OK line only when the gradebook copy actually succeeded, the refusal
    line otherwise (not configured, refused, unreachable, pending prose --
    all mean the score was not sent, so the refusal line is the truthful
    one in every case, D-09/T-994-18)."""
    status, _reason = passback
    return COMPLETION_OK if status == "ok" else COMPLETION_REFUSED


# ---------------------------------------------------------------------------
# The opt-in LTI bind (D-05): nothing listens unless lti.enabled is true.
# ---------------------------------------------------------------------------

def _lti_context(root, banks, plans=None):
    """The handler state for one LTI bind: the scanned bank allowlist and the
    session bookkeeping, shaped exactly like the daemon's."""
    sessions = {}
    for stem, path in (banks or {}).items():
        bank_dir = os.path.dirname(os.path.abspath(path)) or "."
        sessions[stem] = {
            "session_id": secrets.token_hex(16),
            "log": os.path.join(bank_dir, "_evidence", "evidence.jsonl"),
            "out": os.path.join(bank_dir, "_attempts",
                                "%s_attempt_lti.md" % stem),
            "mode": "practice",
        }
    return sessions


def cmd_lti_serve(a):
    """`itembank lti serve [dir]` -- the opt-in LTI bind (D-05): scans the
    bank allowlist, validates the registration, and serves the LTI handler
    family on the configured host/port. TLS (stdlib `ssl`, user-supplied
    cert/key) when both lti.tls_cert and lti.tls_key are set; plain HTTP
    otherwise for the documented reverse-proxy posture (docs/lti-hosting.md).
    The loopback default of every other surface is unchanged; with
    lti.enabled false this command refuses by name.
    """
    from surfaces import settings as _settings
    root = a.dir
    cfg = _settings.load_settings(root)
    try:
        registration = load_registration(cfg)
    except LTIError as exc:
        sys.exit("lti: %s" % (exc.detail or exc.copy or exc.kind))
    banks, plans, _collisions = daemon.scan_dir(root)
    sessions = _lti_context(root, banks, plans)
    OIDCLoginHandler.banks = banks
    OIDCLoginHandler.root = root
    OIDCLoginHandler.sessions = sessions
    OIDCLoginHandler.settings = cfg

    lti = cfg.get("lti") or {}
    host = a.host or "127.0.0.1"
    port = a.port if a.port is not None else 8732
    cert, key = lti.get("tls_cert") or "", lti.get("tls_key") or ""
    if bool(cert) != bool(key):
        sys.exit("lti: tls_cert and tls_key must both be set or both empty")
    if cert and key:
        if not os.path.exists(cert) or not os.path.exists(key):
            sys.exit("lti: tls_cert/tls_key paths do not exist (%s, %s)" % (cert, key))
        srv = server.bind_tls(LTIHandler, port, host, cert, key)
        scheme = "https"
    else:
        srv = server.bind(LTIHandler, port, host)
        scheme = "http"

    base = registration["public_base_url"].rstrip("/")
    print("itembank lti serve")
    print("  dir     %s" % os.path.abspath(root))
    print("  banks   %d" % len(banks))
    print("  public  %s" % base)
    print("  local   %s://%s:%d (loopback / reverse-proxy upstream)"
          % (scheme, host, srv.server_address[1]))
    print("  login   %s/lti/login" % base)
    print("  launch  %s/lti/launch/<bank-stem>" % base)
    print("  jwks    %s/lti/jwks" % base)
    print(PRIVACY_STATEMENT)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    return 0


def cmd_lti_status(a):
    """`itembank lti status` -- the registration state, the D-09 privacy
    statement, nothing more."""
    cfg = settings_surface.load_settings(a.base)
    lti = cfg.get("lti") or {}
    print("itembank lti status")
    if lti.get("enabled"):
        print("  enabled    yes")
        print("  public     %s" % (lti.get("public_base_url") or "(unset)"))
        platforms = lti.get("platforms") or []
        for p in platforms:
            if isinstance(p, dict):
                print("  platform   issuer=%s client_id=%s deployments=%d"
                      % (p.get("issuer"), p.get("client_id"),
                         len(p.get("deployments") or [])))
    else:
        print("  enabled    no (loopback default unchanged; the LTI surface "
              "listens nowhere)")
    print("  crypto     %s" % ("available" if crypto_available() else "MISSING"))
    print()
    print(PRIVACY_STATEMENT)
    return 0


def cmd_lti_doctor(a):
    """`itembank lti doctor` -- validates the registration and prints the
    URLs to paste into the platform's developer-key configuration, the
    install command for the optional dependencies, and the D-09 privacy
    statement (the statement lives in the command's own output, not only in
    planning documents)."""
    if not crypto_available():
        print(CRYPTO_REFUSAL)
        print("  install: pip install cryptography==%s PyJWT==%s"
              % (CRYPTO_PINS["cryptography"], CRYPTO_PINS["PyJWT"]))
        print("  (pinned + checksummed + license-reviewed: deps/lti-pins.txt)")
        return 1
    cfg = settings_surface.load_settings(a.base)
    try:
        registration = load_registration(cfg)
    except LTIError as exc:
        print("LTI registration error: %s" % (exc.detail or exc.copy or exc.kind))
        return 1
    platform = registration["platform"]
    base = registration["public_base_url"].rstrip("/")
    print("itembank lti doctor")
    print("  registration  OK -- issuer %s" % (platform or {}).get("issuer"))
    print("  OIDC initiation URL   %s/lti/login" % base)
    print("  launch URL            %s/lti/launch/<bank-stem>" % base)
    print("  tool JWKS URL         %s/lti/jwks" % base)
    if platform is not None:
        print("  platform auth_endpoint  %s" % platform.get("auth_endpoint"))
        print("  platform jwks_url       %s" % platform.get("jwks_url"))
        print("  platform token_endpoint %s" % platform.get("token_endpoint"))
        print("  deployments allowed     %s"
              % (", ".join(platform.get("deployments") or []) or "(none)"))
    print()
    print(PRIVACY_STATEMENT)
    return 0
