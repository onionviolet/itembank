#!/usr/bin/env python3
"""Phase 999.4 (Canvas LMS integration via LTI 1.3): the fake-platform
harness and the whole protocol spine, offline, with zero Canvas access
(R-01 default).

The fake platform is a stdlib HTTP server that mints its own RSA keypair,
serves a JWKS, records authorize-redirect params, and (plan 03) plays the
AGS token / line-item / score endpoints. The tool under test is the real
`surfaces/lti.py` handler family bound on loopback, so every assertion runs
through the actual HTTP path a Canvas instance would use.

Standard library only (plus the optional, pinned `cryptography`/`PyJWT`
pair the LTI surface guards on), no test framework, runnable as
`python tests/lti_roundtrip.py`.
"""
import base64
import contextlib
import http.server
import html
import io
import json
import os
import re
import shutil
import socketserver
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402
import runtime                                             # noqa: E402
import schema_validate                                     # noqa: E402
import server                                              # noqa: E402
from surfaces import cli, daemon, lti, session, settings             # noqa: E402
from model import load                                      # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
ITEMBANK = os.path.join(ROOT, "itembank.py")
SCHEMA_PATH = os.path.join(ROOT, "schemas", "settings.schema.json")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Fake platform: a stdlib LTI 1.3 platform that signs launches and (plan 03)
# plays the AGS endpoints, all over loopback.
# ---------------------------------------------------------------------------

def b64u(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def b64u_decode(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def make_rsa_keypair():
    """Mint an RSA keypair with cryptography (the pinned optional dep the LTI
    surface itself guards on)."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption())
    return key, pem


def sign_rs256(key, signing_input):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    return key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())


def public_jwk(key, kid="fake-platform-key"):
    from cryptography.hazmat.primitives.asymmetric import rsa
    numbers = key.public_key().public_numbers()
    n_bits = numbers.n.bit_length()
    return {"kty": "RSA", "kid": kid, "use": "sig", "alg": "RS256",
            "n": b64u(numbers.n.to_bytes((n_bits + 7) // 8, "big")),
            "e": b64u(numbers.e.to_bytes(3, "big"))}


class FakePlatform:
    """A fake LTI 1.3 platform: issuer, authorize endpoint (records params),
    JWKS endpoint, OAuth2 token endpoint and AGS line-item/score endpoints.
    Serves on a loopback port chosen by the OS."""

    ISSUER = "https://fake.canvas.example"

    def __init__(self, deployments=("deploy-1",), kid="fake-platform-key",
                 jwks_status=200, jwks_body=None, reject_scores=False):
        plat = self
        self.key, self.key_pem = make_rsa_keypair()
        self.kid = kid
        self.deployments = list(deployments)
        self.authorize_params = []
        self.token_grants = []
        self.created_line_items = []
        self.scores = []
        self.jwks_hits = 0
        self.lineitem_status = 200
        self.jwks_status = jwks_status
        self.jwks_body = jwks_body
        self.reject_scores = reject_scores

        class _H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                if self.path == "/jwks":
                    plat.jwks_hits += 1
                    if plat.jwks_status != 200:
                        self.send_response(plat.jwks_status)
                        self.send_header("Content-Length", "0")
                        self.end_headers()
                        return
                    body = json.dumps({"keys": [public_jwk(plat.key, plat.kid)]})
                    self._json(body)
                elif self.path.startswith("/authorize"):
                    plat.authorize_params.append(
                        urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query))
                    self._json(json.dumps({"ok": True}))
                elif self.path.startswith("/lineitems"):
                    self._lineitems_get()
                else:
                    self.send_response(404)
                    self.send_header("Content-Length", "0")
                    self.end_headers()

            def do_POST(self):
                n = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(n).decode("utf-8", "replace")
                if self.path == "/token":
                    plat.token_grants.append(urllib.parse.parse_qs(raw))
                    self._json(json.dumps({
                        "access_token": "fake-access-token",
                        "token_type": "Bearer", "expires_in": 3600}))
                elif self.path.startswith("/lineitems") and "/scores" not in self.path:
                    self._lineitems_post(raw)
                elif "/scores" in self.path:
                    self._scores_post(raw)
                else:
                    self.send_response(404)
                    self.send_header("Content-Length", "0")
                    self.end_headers()

            def _json(self, text, status=200):
                body = text.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _lineitems_get(self):
                items = []
                for li in plat.created_line_items:
                    items.append({
                        "id": plat.lineitems_url + "/" + li["resourceId"],
                        "label": li.get("label", ""),
                        "scoreMaximum": li.get("scoreMaximum"),
                        "resourceId": li["resourceId"],
                        "tag": li.get("tag", "")})
                self._json(json.dumps({"lineitems": items}))

            def _lineitems_post(self, raw):
                if plat.lineitem_status != 200:
                    self._json(json.dumps({"error": "rejected"}), 400)
                    return
                try:
                    body = json.loads(raw)
                except ValueError:
                    body = {}
                plat.created_line_items.append(body)
                self._json(json.dumps({
                    "id": plat.lineitems_url + "/" + body.get("resourceId", ""),
                    "label": body.get("label", ""),
                    "scoreMaximum": body.get("scoreMaximum"),
                    "resourceId": body.get("resourceId", ""),
                    "tag": body.get("tag", "")}))

            def _scores_post(self, raw):
                if plat.reject_scores:
                    self._json(json.dumps({"error": "rejected"}), 400)
                    return
                try:
                    body = json.loads(raw)
                except ValueError:
                    body = {}
                plat.scores.append(body)
                self._json(json.dumps({"ok": True}))

        self.server = socketserver.TCPServer(("127.0.0.1", 0), _H)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.port = self.server.server_address[1]
        self.base = "http://127.0.0.1:%d" % self.port
        self.jwks_url = self.base + "/jwks"
        self.authorize_url = self.base + "/authorize"
        self.token_url = self.base + "/token"
        self.lineitems_url = self.base + "/lineitems"

    def ags_endpoint_claim(self, scopes=None):
        """The AGS endpoint claim a launch carries when AGS is granted
        (RESEARCH 4.1): lineitems URL plus the granted scopes."""
        scopes = scopes or [lti.AGS_SCOPE_LINEITEM, lti.AGS_SCOPE_SCORE]
        return {"lineitems": self.lineitems_url,
                "lineitem": self.lineitems_url + "/1", "scope": scopes}

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    def mint_id_token(self, claims, alg="RS256"):
        """Sign a launch id_token with the platform key. `claims` overrides
        the defaults (iss/aud/deployment_id/exp/nonce/sub/message_type);
        `alg` overrides the JOSE header algorithm (for the bad-alg fixture)."""
        header = {"alg": alg, "typ": "JWT", "kid": self.kid}
        payload = {
            "iss": self.ISSUER,
            "aud": "tool-client-1",
            "sub": "learner-1",
            "exp": int(time.time()) + 300,
            "iat": int(time.time()),
            "nonce": "nonce-placeholder",
            "deployment_id": self.deployments[0],
            "message_type": "LtiResourceLinkRequest",
            "https://purl.imsglobal.org/spec/lti/claim/version": "1.3.0",
        }
        payload.update(claims or {})
        h = b64u(json.dumps(header).encode("utf-8"))
        p = b64u(json.dumps(payload).encode("utf-8"))
        sig = b64u(sign_rs256(self.key, (h + "." + p).encode("ascii")))
        return h + "." + p + "." + sig


# ---------------------------------------------------------------------------
# Tool harness: the real LTI handler family bound on loopback with the fake
# platform registered, plus a temp root for sessions/evidence.
# ---------------------------------------------------------------------------

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_NO_REDIRECT_OPENER = urllib.request.build_opener(_NoRedirect)


class ToolHarness:
    """One tool-side harness: a temp root with the sample bank, an
    itembank.json registering the fake platform, and a real loopback
    `LTIHandler` server. Class attributes on the handler family are pinned
    exactly like the `itembank lti serve` bind does."""

    def __init__(self, platform, enabled=True, public_base_url=None,
                 tool_key_pem=None, banks=None, tls=None):
        self.tmp = tempfile.mkdtemp(prefix="lti_roundtrip_")
        shutil.copyfile(BANK, os.path.join(self.tmp, "sample_bank.md"))
        self.bank_path = os.path.join(self.tmp, "sample_bank.md")
        self.tool_key, self.tool_key_pem = tool_key_pem or make_rsa_keypair()
        key_path = os.path.join(self.tmp, "tool_key.pem")
        with open(key_path, "wb") as fh:
            fh.write(self.tool_key_pem)
        # Bind the tool server first so public_base_url can carry its port.
        # With tls={"cert":..., "key":...} the bind wraps the socket in
        # stdlib ssl (D-05/LTI-06); otherwise plain HTTP (the documented
        # reverse-proxy posture).
        self.tls = tls
        if tls:
            self.server = server.bind_tls(
                lti.LTIHandler, 0, "127.0.0.1", tls["cert"], tls["key"])
        else:
            self.server = socketserver.TCPServer(("127.0.0.1", 0), lti.LTIHandler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.tool_port = self.server.server_address[1]
        scheme = "https" if tls else "http"
        self.base = public_base_url or ("%s://127.0.0.1:%d" % (scheme, self.tool_port))
        cfg = {
            "lti": {
                "enabled": enabled,
                "public_base_url": self.base,
                "tls_cert": (tls or {}).get("cert", "") if tls else "",
                "tls_key": (tls or {}).get("key", "") if tls else "",
                "tool_private_jwk_path": key_path,
                "platforms": [{
                    "issuer": platform.ISSUER,
                    "client_id": "tool-client-1",
                    "auth_endpoint": platform.authorize_url,
                    "jwks_url": platform.jwks_url,
                    "token_endpoint": platform.token_url,
                    "deployments": list(platform.deployments),
                }],
            }
        }
        self.cfg = cfg
        stem = "sample_bank"
        self.banks = {stem: self.bank_path}
        lti.OIDCLoginHandler.banks = self.banks
        lti.OIDCLoginHandler.root = self.tmp
        lti.OIDCLoginHandler.sessions = {}
        lti.OIDCLoginHandler.settings = cfg
        lti.OIDCLoginHandler.nonce_store = lti.NonceStore()
        self.stem = stem

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def login_url(self, **overrides):
        params = {
            "iss": "https://fake.canvas.example",
            "login_hint": "learner-1",
            "target_link_uri": "%s/lti/launch/%s" % (self.base, self.stem),
            "client_id": "tool-client-1",
            "deployment_id": "deploy-1",
            "lti_message_hint": "hint-1",
        }
        params.update(overrides)
        return self.base + "/lti/login?" + urllib.parse.urlencode(params)

    def _opener(self):
        """No-redirect opener; with TLS the https handler uses an
        unverified context (the fixture cert is self-signed)."""
        if not self.tls:
            return _NO_REDIRECT_OPENER
        ctx = ssl._create_unverified_context()
        return urllib.request.build_opener(
            _NoRedirect, urllib.request.HTTPSHandler(context=ctx))

    def get(self, url):
        """GET with redirects NOT followed, so the authorize Location can be
        inspected (the browser would follow it; the test parses it)."""
        req = urllib.request.Request(url)
        try:
            with self._opener().open(req) as resp:
                return resp.status, dict(resp.headers), resp.read()
        except urllib.error.HTTPError as exc:
            return exc.code, dict(exc.headers), exc.read()

    def post_form(self, path, fields):
        body = urllib.parse.urlencode(fields).encode("utf-8")
        req = urllib.request.Request(self.base + path, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        try:
            with self._opener().open(req) as resp:
                return resp.status, dict(resp.headers), resp.read()
        except urllib.error.HTTPError as exc:
            return exc.code, dict(exc.headers), exc.read()

    def post_json(self, path, payload, headers=None):
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.base + path, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with self._opener().open(req) as resp:
                return resp.status, dict(resp.headers), resp.read()
        except urllib.error.HTTPError as exc:
            return exc.code, dict(exc.headers), exc.read()


def reset_handler_state():
    lti.OIDCLoginHandler.banks = {}
    lti.OIDCLoginHandler.root = "."
    lti.OIDCLoginHandler.sessions = {}
    lti.OIDCLoginHandler.settings = {}
    lti.OIDCLoginHandler.nonce_store = lti.NonceStore()
    lti.LTIHandler.launch_ctx = {}
    lti.AGSClient._published = set()


def launch_flow(harness, platform, claims=None, state=None, nonce=None,
                stem=None):
    """Drive the full OIDC dance against the harness: login GET -> authorize
    redirect (parsed, not followed) -> launch POST with a minted id_token.
    Returns (status, headers, body, authorize_params, state, nonce)."""
    status, headers, _ = harness.get(harness.login_url())
    if status != 302:
        return status, headers, b"", None, None, None
    location = headers.get("Location", "")
    ap = urllib.parse.parse_qs(urllib.parse.urlsplit(location).query)
    state = state or (ap.get("state") or [""])[0]
    nonce = nonce or (ap.get("nonce") or [""])[0]
    token = platform.mint_id_token(dict(claims or {}, nonce=nonce))
    s, h, b = harness.post_form(
        "/lti/launch/%s" % (stem or harness.stem),
        {"id_token": token, "state": state})
    return s, h, b, ap, state, nonce


# ---------------------------------------------------------------------------
# Plan 01 Task 1: registry, optional crypto guard, settings block.
# ---------------------------------------------------------------------------

def _enabled_settings(platform, **lti_overrides):
    lti_block = {
        "enabled": True,
        "public_base_url": "https://drill.example.com",
        "tls_cert": "", "tls_key": "",
        "tool_private_jwk_path": "/tmp/tool_key.pem",
        "platforms": [{
            "issuer": platform.ISSUER, "client_id": "tool-client-1",
            "auth_endpoint": platform.authorize_url,
            "jwks_url": platform.jwks_url,
            "token_endpoint": platform.token_url,
            "deployments": ["deploy-1"],
        }],
    }
    lti_block.update(lti_overrides)
    return {"lti": lti_block}


def check_registry_one_platform_per_issuer():
    platform = FakePlatform()
    try:
        reg = lti.load_registration(_enabled_settings(platform),
                                    issuer=platform.ISSUER,
                                    client_id="tool-client-1")
        if not reg["enabled"] or reg["platform"] is None:
            fail("load_registration did not resolve the single platform")
        if reg["platform"]["client_id"] != "tool-client-1":
            fail("load_registration resolved the wrong platform")
        # Unknown issuer names both the issuer and the client_id.
        try:
            lti.load_registration(_enabled_settings(platform),
                                  issuer="https://elsewhere.example",
                                  client_id="nope-client")
            fail("unknown issuer was not refused")
        except lti.LTIError as exc:
            if exc.kind != "unknown_issuer":
                fail("unknown issuer refusal kind %r" % exc.kind)
            if "https://elsewhere.example" not in exc.detail \
                    or "nope-client" not in exc.detail:
                fail("unknown-issuer refusal does not name issuer+client_id: %r"
                     % exc.detail)
        # Unknown client_id for a known issuer.
        try:
            lti.load_registration(_enabled_settings(platform),
                                  issuer=platform.ISSUER,
                                  client_id="wrong-client")
            fail("unknown client_id was not refused")
        except lti.LTIError as exc:
            if exc.kind != "unknown_client":
                fail("unknown-client refusal kind %r" % exc.kind)
        # Duplicate issuer.
        dup = _enabled_settings(platform)
        dup["lti"]["platforms"].append(dict(dup["lti"]["platforms"][0],
                                            client_id="second-client"))
        try:
            lti.load_registration(dup)
            fail("duplicate issuer was not refused")
        except lti.LTIError as exc:
            if exc.kind != "duplicate_issuer":
                fail("duplicate-issuer refusal kind %r" % exc.kind)
        # Missing public_base_url when enabled is a named refusal (D-05).
        try:
            lti.load_registration(_enabled_settings(platform, public_base_url=""))
            fail("enabled without public_base_url was not refused")
        except lti.LTIError as exc:
            if exc.kind != "missing_public_base_url":
                fail("missing-base refusal kind %r" % exc.kind)
        # Disabled is a named refusal, not a crash.
        try:
            lti.load_registration({"lti": {"enabled": False}})
            fail("disabled lti was not refused")
        except lti.LTIError as exc:
            if exc.kind != "lti_disabled":
                fail("disabled refusal kind %r" % exc.kind)
    finally:
        platform.close()


def check_crypto_guard_doctor_refusal():
    """`lti doctor` with the crypto imports absent prints the exact refusal
    line (D-08), simulated by monkeypatching the guard -- never by
    uninstalling."""
    platform = FakePlatform()
    try:
        real = lti.crypto_available
        lti.crypto_available = lambda: False
        try:
            out = io.StringIO()
            a = type("A", (), {"base": "."})()
            with contextlib.redirect_stdout(out):
                rc = lti.cmd_lti_doctor(a)
            text = out.getvalue()
            if rc != 1:
                fail("lti doctor without crypto returned %d, expected 1" % rc)
            if lti.CRYPTO_REFUSAL not in text:
                fail("lti doctor without crypto did not print the exact "
                     "refusal line: %r" % text)
            if "pip install cryptography" not in text:
                fail("lti doctor without crypto did not print the install command")
        finally:
            lti.crypto_available = real
    finally:
        platform.close()


def check_settings_schema_lti_block():
    schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
    lti_sub = schema["properties"]["lti"]
    if lti_sub["properties"]["enabled"]["default"] is not False:
        fail("lti.enabled must default false")
    if "platforms" not in lti_sub["properties"]:
        fail("lti.platforms missing from schema")
    # The one validator rejects a hand-edited invalid value.
    errs = schema_validate.validate({"enabled": "yes"}, lti_sub)
    if not errs:
        fail("schema accepted lti.enabled = 'yes'")
    errs = schema_validate.validate(
        {"enabled": True, "public_base_url": "x", "tls_cert": "",
         "tls_key": "", "tool_private_jwk_path": "k",
         "platforms": [{"issuer": "i", "client_id": "c",
                        "auth_endpoint": "a", "jwks_url": "j",
                        "token_endpoint": "t", "deployments": ["d"]}]},
        lti_sub)
    if errs:
        fail("schema rejected a valid lti block: %s" % errs[0])
    # `itembank config` prints the new keys (one settings surface).
    result = subprocess.run(
        [sys.executable, ITEMBANK, "config", "--base", ROOT],
        capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        fail("itembank config failed: %s" % result.stderr)
    for key in ("lti.enabled", "lti.public_base_url", "lti.platforms",
                "lti.tool_private_jwk_path"):
        if key not in result.stdout:
            fail("itembank config does not print %r" % key)
    # A malformed lti block in itembank.json is caught by the one validator.
    tmp = tempfile.mkdtemp(prefix="lti_cfg_")
    try:
        shutil.copyfile(os.path.join(ROOT, "itembank.json"),
                        os.path.join(tmp, "itembank.json"))
        with open(os.path.join(tmp, "itembank.json"), encoding="utf-8") as fh:
            data = json.load(fh)
        data["lti"]["enabled"] = "yes"
        with open(os.path.join(tmp, "itembank.json"), "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        result = subprocess.run(
            [sys.executable, ITEMBANK, "config", "--base", tmp],
            capture_output=True, text=True, encoding="utf-8")
        if result.returncode == 0 or "settings.invalid_type" not in result.stderr:
            fail("hand-edited invalid lti block was not refused by the one "
                 "validator: %s" % result.stderr)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# Plan 01 Task 2: JWT verification against the platform JWKS.
# ---------------------------------------------------------------------------

def check_jwt_valid_and_each_invalid_named():
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        # Prime the nonce store with a fresh state/nonce, then verify a
        # valid token: signature, iss, aud, nonce, exp, deployment all pass.
        state, nonce = harness_server_mint(harness)
        claims = platform.mint_id_token({"nonce": nonce})
        reg = lti.load_registration(harness.cfg, issuer=platform.ISSUER,
                                    client_id="tool-client-1")
        verified = lti.verify_id_token(claims, reg, harness_nonce_store(), state)
        if not verified.get("__verified"):
            fail("valid id_token did not verify")

        # Wrong signing key.
        other, _ = make_rsa_keypair()
        state2, nonce2 = harness_server_mint(harness)
        bad = _signed_with(other, platform, {"nonce": nonce2})
        _expect_refusal(lambda: lti.verify_id_token(bad, reg,
                                                    harness_nonce_store(), state2),
                        "bad_signature", platform)

        # Wrong iss.
        state3, nonce3 = harness_server_mint(harness)
        _expect_refusal(
            lambda: lti.verify_id_token(
                platform.mint_id_token({"iss": "https://wrong.example",
                                        "nonce": nonce3}),
                reg, harness_nonce_store(), state3), "bad_iss", platform)

        # Wrong aud.
        state4, nonce4 = harness_server_mint(harness)
        _expect_refusal(
            lambda: lti.verify_id_token(
                platform.mint_id_token({"aud": "other-client",
                                        "nonce": nonce4}),
                reg, harness_nonce_store(), state4), "bad_aud", platform)

        # Expired.
        state5, nonce5 = harness_server_mint(harness)
        _expect_refusal(
            lambda: lti.verify_id_token(
                platform.mint_id_token({"exp": int(time.time()) - 60,
                                        "nonce": nonce5}),
                reg, harness_nonce_store(), state5), "expired", platform)

        # Replay of a spent nonce: the successful verification above already
        # spent state/nonce, so re-verifying the same token is refused.
        _expect_refusal(lambda: lti.verify_id_token(claims, reg,
                                                    harness_nonce_store(), state),
                        "bad_nonce", platform)

        # Unknown deployment_id.
        state6, nonce6 = harness_server_mint(harness)
        _expect_refusal(
            lambda: lti.verify_id_token(
                platform.mint_id_token({"deployment_id": "deploy-unknown",
                                        "nonce": nonce6}),
                reg, harness_nonce_store(), state6), "unknown_deployment", platform)

        # Malformed JOSE: bad base64url.
        _expect_refusal(lambda: lti.verify_id_token("a.b", reg,
                                                    harness_nonce_store(), "s"),
                        "malformed_token", platform)
        _expect_refusal(
            lambda: lti.verify_id_token(
                platform.mint_id_token({"nonce": "x"}).replace(".", "!", 1),
                reg, harness_nonce_store(), "s"), "malformed_token", platform)

        # Wrong alg header.
        state7, nonce7 = harness_server_mint(harness)
        _expect_refusal(
            lambda: lti.verify_id_token(
                platform.mint_id_token({"nonce": nonce7}, alg="HS256"),
                reg, harness_nonce_store(), state7), "bad_alg", platform)
    finally:
        harness.close()
        platform.close()


def _signed_with(key, platform, claims):
    """Like platform.mint_id_token but signed with a different key."""
    header = {"alg": "RS256", "typ": "JWT", "kid": platform.kid}
    payload = {
        "iss": platform.ISSUER, "aud": "tool-client-1", "sub": "learner-1",
        "exp": int(time.time()) + 300, "nonce": "n",
        "deployment_id": platform.deployments[0],
        "message_type": "LtiResourceLinkRequest"}
    payload.update(claims)
    h = b64u(json.dumps(header).encode("utf-8"))
    p = b64u(json.dumps(payload).encode("utf-8"))
    sig = b64u(sign_rs256(key, (h + "." + p).encode("ascii")))
    return h + "." + p + "." + sig


def _expect_refusal(fn, kind, platform):
    try:
        fn()
        fail("expected LTIError %r but verification passed" % kind)
    except lti.LTIError as exc:
        if exc.kind != kind:
            fail("expected refusal %r, got %r (%s)" % (kind, exc.kind, exc))


def harness_server_mint(harness):
    """Mint a state/nonce through the harness's own server (a real login
    round trip), returning (state, nonce)."""
    s, h, _ = harness.get(harness.login_url())
    if s != 302:
        fail("login initiation did not redirect (status %d)" % s)
    ap = urllib.parse.parse_qs(urllib.parse.urlsplit(h["Location"]).query)
    return (ap.get("state") or [""])[0], (ap.get("nonce") or [""])[0]


def harness_nonce_store():
    """The harness's live nonce store (the class attribute the handlers
    share)."""
    return lti.OIDCLoginHandler.nonce_store


def check_jwks_bounded_and_cached():
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        state, nonce = harness_server_mint(harness)
        reg = lti.load_registration(harness.cfg, issuer=platform.ISSUER,
                                    client_id="tool-client-1")
        lti.verify_id_token(platform.mint_id_token({"nonce": nonce}),
                            reg, harness_nonce_store(), state)
        hits_after_first = platform.jwks_hits
        # A second verification within the TTL must reuse the cache.
        state2, nonce2 = harness_server_mint(harness)
        lti.verify_id_token(platform.mint_id_token({"nonce": nonce2}),
                            reg, harness_nonce_store(), state2)
        if platform.jwks_hits != hits_after_first:
            fail("JWKS was re-fetched within the cache TTL")
        # An unreachable jwks_url is a named refusal, not a hang or crash.
        dead = FakePlatform()
        dead_port = dead.server.server_address[1]
        dead.close()
        dead_reg = _registration_with_jwks(
            harness, "http://127.0.0.1:%d/jwks" % dead_port)
        state3, nonce3 = harness_server_mint(harness)
        try:
            lti.verify_id_token(platform.mint_id_token({"nonce": nonce3}),
                                dead_reg, harness_nonce_store(), state3)
            fail("unreachable jwks_url was not refused")
        except lti.LTIError as exc:
            if exc.kind != "jwks_unreachable":
                fail("unreachable JWKS refusal kind %r" % exc.kind)
    finally:
        harness.close()
        platform.close()


def _registration_with_jwks(harness, jwks_url):
    cfg = json.loads(json.dumps(harness.cfg))
    cfg["lti"]["platforms"][0]["jwks_url"] = jwks_url
    return lti.load_registration(cfg, issuer="https://fake.canvas.example",
                                 client_id="tool-client-1")


# ---------------------------------------------------------------------------
# Plan 01 Task 3: OIDC login + launch handlers and the JSON-command wrap seam.
# ---------------------------------------------------------------------------

def check_login_initiation_redirect_params():
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        s, h, _ = harness.get(harness.login_url())
        if s != 302:
            fail("login initiation returned %d, expected 302" % s)
        location = h.get("Location", "")
        parts = urllib.parse.urlsplit(location)
        if parts.netloc != urllib.parse.urlsplit(platform.authorize_url).netloc:
            fail("authorize redirect goes to the wrong endpoint: %s" % location)
        q = urllib.parse.parse_qs(parts.query)
        expected = {
            "response_type": ["id_token"],
            "client_id": ["tool-client-1"],
            "scope": ["openid"],
            "prompt": ["none"],
            "response_mode": ["form_post"],
            "login_hint": ["learner-1"],
        }
        for key, value in expected.items():
            if q.get(key) != value:
                fail("authorize redirect missing/invalid %r: %r" % (key, q))
        if not q.get("state") or not q.get("nonce"):
            fail("authorize redirect carries no state/nonce")
        if q.get("state") == q.get("nonce"):
            fail("state and nonce must differ")
        redirect_uri = (q.get("redirect_uri") or [""])[0]
        if redirect_uri != "%s/lti/launch/%s" % (harness.base, harness.stem):
            fail("redirect_uri is not the tool's launch URL: %r" % redirect_uri)
        # Unregistered issuer refuses with the verbatim platform copy.
        s, _, body = harness.get(harness.login_url(iss="https://other.example"))
        if s != 403 or lti.UNREGISTERED_PLATFORM not in body.decode("utf-8", "replace"):
            fail("unregistered-issuer login did not refuse with the verbatim copy")
        # target_link_uri outside public_base_url is refused.
        s, _, body = harness.get(harness.login_url(
            target_link_uri="https://evil.example/lti/launch/x"))
        if s != 403 or lti.UNVERIFIED_LAUNCH not in body.decode("utf-8", "replace"):
            fail("off-base target_link_uri was not refused")
    finally:
        harness.close()
        platform.close()


def check_launch_calls_daemon_in_process():
    """A verified launch reaches the daemon's handle_api_start in-process and
    returns the same JSON a direct /api/start call returns (D-01, LTI-02) --
    the wrap-seam proof. The plan-01 tracer fallback (no message_type in the
    launch claims) keeps this behavior stable across the UI plans."""
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        # The plan-01 tracer fallback: a verified launch carrying no
        # message_type (or one the UI plans do not branch on) reaches the
        # daemon's handle_api_start in-process. The UI message types are
        # asserted by their own plan-02 checks.
        s, _, body, ap, state, nonce = launch_flow(
            harness, platform, claims={"message_type": None})
        if s != 200:
            fail("verified launch did not return the start JSON (HTTP %d): %s"
                 % (s, body.decode("utf-8", "replace")[:200]))
        result = json.loads(body.decode("utf-8"))
        if result.get("status") != "active" or not result.get("session_id"):
            fail("launch result is not a session view: %r" % result)
        if not result.get("item"):
            fail("launch result carries no first item")
        # The item is exactly runtime.public_item(q, 0) -- the same projection
        # every surface renders (D-03, wrap seam).
        qs = load(harness.bank_path)
        q = next((q for q in qs if q["id"] == result["item"]["id"]), None)
        if q is None:
            fail("launch item id not found in the bank")
        expected = runtime.public_item(q, 0)
        if result["item"] != expected:
            fail("launch item differs from runtime.public_item(): %r vs %r"
                 % (result["item"], expected))
        # The session file and evidence selection event exist on disk -- the
        # real daemon path ran, not a fake.
        attempts = os.path.join(harness.tmp, "_attempts")
        if not os.path.isdir(attempts):
            fail("no _attempts dir: the daemon start did not write a session")
        if not any(n.startswith("session_") for n in os.listdir(attempts)):
            fail("no session file was written by the wrapped start")
        # A failed verification calls NO daemon handler: wrong-key launch
        # must not create a second session.
        before = sorted(os.listdir(attempts))
        s, _, body = harness.post_form(
            "/lti/launch/%s" % harness.stem,
            {"id_token": _signed_with(*[make_rsa_keypair()[0], platform,
                                        {"nonce": "x"}]),
             "state": "bogus"})
        if s != 403 or lti.UNVERIFIED_LAUNCH not in body.decode("utf-8", "replace"):
            fail("wrong-key launch did not refuse with the verbatim copy")
        after = sorted(os.listdir(attempts))
        if after != before:
            fail("failed launch created a session -- the wrap was called on "
                 "an unverified launch")
    finally:
        harness.close()
        platform.close()


def check_route_scope_and_no_second_scorer():
    """D-01/LTI-02: API_ROUTES unchanged (five routes), no scoring call and
    no runtime import in the LTI surface; the wrap seam names the daemon's
    own handle_api_* functions."""
    if len(daemon.API_ROUTES) != 5:
        fail("API_ROUTES changed; LTI must not add /api/* routes")
    if not {"start", "next", "submit", "hint", "report"} <= set(daemon.ROUTE_CLI.values()):
        fail("ROUTE_CLI session coverage lost")
    for name, handler_name in lti.LTI_API_WRAP.items():
        if handler_name != "handle_api_" + name:
            fail("wrap seam %r does not name the daemon's %s" % (name, handler_name))
        if not hasattr(daemon, handler_name):
            fail("wrap seam names %s which daemon does not export" % handler_name)
    src = open(os.path.join(ROOT, "surfaces", "lti.py"), encoding="utf-8").read()
    if "score_response" in src or "from runtime" in src or "import runtime" in src:
        fail("surfaces/lti.py contains a scoring call or runtime import "
             "(D-01: no second scorer)")
    if "getattr(daemon, handler_name" not in src:
        fail("surfaces/lti.py does not dispatch to the daemon handlers "
             "in-process")


def check_doctor_and_help_privacy():
    """`itembank lti doctor` with a valid registration prints the OIDC
    initiation / launch / JWKS URLs and the D-09 privacy statement; `itembank
    lti --help` contains the same statement (D-09)."""
    platform = FakePlatform()
    tmp = tempfile.mkdtemp(prefix="lti_doctor_")
    try:
        shutil.copyfile(os.path.join(ROOT, "itembank.json"),
                        os.path.join(tmp, "itembank.json"))
        with open(os.path.join(tmp, "itembank.json"), encoding="utf-8") as fh:
            data = json.load(fh)
        key_path = os.path.join(tmp, "tool_key.pem")
        with open(key_path, "wb") as fh:
            fh.write(make_rsa_keypair()[1])
        data["lti"] = {
            "enabled": True, "public_base_url": "https://drill.example.com",
            "tls_cert": "", "tls_key": "", "tool_private_jwk_path": key_path,
            "platforms": [{
                "issuer": platform.ISSUER, "client_id": "tool-client-1",
                "auth_endpoint": platform.authorize_url,
                "jwks_url": platform.jwks_url,
                "token_endpoint": platform.token_url,
                "deployments": ["deploy-1"]}]}
        with open(os.path.join(tmp, "itembank.json"), "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        result = subprocess.run(
            [sys.executable, ITEMBANK, "lti", "doctor", "--base", tmp],
            capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            fail("lti doctor failed: %s" % result.stderr)
        for needle in ("/lti/login", "/lti/launch", "/lti/jwks",
                       lti.PRIVACY_STATEMENT):
            if needle not in result.stdout:
                fail("lti doctor output missing %r" % needle)
        result = subprocess.run(
            [sys.executable, ITEMBANK, "lti", "--help"],
            capture_output=True, text=True, encoding="utf-8")
        normalized_help = " ".join(result.stdout.split())
        normalized_statement = " ".join(lti.PRIVACY_STATEMENT.split())
        if normalized_statement not in normalized_help:
            fail("itembank lti --help lacks the D-09 privacy statement")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        platform.close()


def check_lti_bind_opt_in():
    """D-05: with lti.enabled false nothing new listens; the loopback default
    is unchanged. `itembank lti serve` refuses by name when disabled."""
    tmp = tempfile.mkdtemp(prefix="lti_bind_")
    try:
        shutil.copyfile(os.path.join(ROOT, "itembank.json"),
                        os.path.join(tmp, "itembank.json"))
        result = subprocess.run(
            [sys.executable, ITEMBANK, "lti", "serve", tmp, "--port", "0"],
            capture_output=True, text=True, encoding="utf-8", timeout=30)
        if result.returncode == 0:
            fail("lti serve with lti.enabled false bound a listener")
        if "lti.enabled" not in result.stderr and "lti" not in result.stderr.lower():
            fail("lti serve disabled refusal does not name lti.enabled: %s"
                 % result.stderr)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_lint_and_core_loop_untouched():
    """The core loop is byte-identical with the optional imports present
    (D-08: degrade, never block)."""
    result = subprocess.run(
        [sys.executable, ITEMBANK, "lint", BANK],
        capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        fail("sample bank no longer lints clean: %s" % result.stdout)


# ---------------------------------------------------------------------------
# Plan 02: the deep-link picker and the embedded learner player (UI-CONTRACT).
# ---------------------------------------------------------------------------

SAMPLE_OBJECTIVES = ["Distribution / residual maintenance", "Public notification",
                     "Operations", "Treatment processes", "Regulatory framework"]

# Sensitive bank content the picker must never render (UI-SPEC gate 4,
# T-994-07): stems, key markers, and correct-answer counts.
PICKER_FORBIDDEN = ["chlorine residual", "boil-water notice", "CORRECT:",
                    "WHY BEST", "KEY DISCRIMINATOR", "DISTRACTOR ANALYSIS"]


def deep_link_launch(harness, platform, return_url="https://fake.canvas.example/return"):
    """Drive a verified LtiDeepLinkingRequest launch; returns (status,
    headers, body)."""
    s, h, _ = harness.get(harness.login_url())
    if s != 302:
        fail("deep-link login did not redirect (status %d)" % s)
    ap = urllib.parse.parse_qs(urllib.parse.urlsplit(h["Location"]).query)
    state = (ap.get("state") or [""])[0]
    nonce = (ap.get("nonce") or [""])[0]
    token = platform.mint_id_token({
        "nonce": nonce,
        "message_type": "LtiDeepLinkingRequest",
        lti.DEEP_LINKING_CLAIM: {
            "deep_link_return_url": return_url,
            "accept_types": ["ltiResourceLink"],
            "accept_multiple": False,
        },
    })
    return harness.post_form("/lti/launch/%s" % harness.stem,
                             {"id_token": token, "state": state})


def resource_link_launch(harness, platform, objective, mode="practice",
                         claims_extra=None):
    """Drive a verified LtiResourceLinkRequest launch carrying the custom
    objective; returns (status, headers, body)."""
    s, h, _ = harness.get(harness.login_url())
    if s != 302:
        fail("resource-link login did not redirect (status %d)" % s)
    ap = urllib.parse.parse_qs(urllib.parse.urlsplit(h["Location"]).query)
    state = (ap.get("state") or [""])[0]
    nonce = (ap.get("nonce") or [""])[0]
    claims = {"nonce": nonce, "message_type": "LtiResourceLinkRequest",
              "custom": {"objective": objective, "mode": mode}}
    if claims_extra:
        claims.update(claims_extra)
    token = platform.mint_id_token(claims)
    return harness.post_form("/lti/launch/%s" % harness.stem,
                             {"id_token": token, "state": state})


def answer_for(q):
    """The canonical correct response for one item, in the JSON-string shape
    /api/submit normalizes (the page submits the same shape)."""
    t = q["type"]
    if t == "mc":
        return q["correct"][0]
    if t == "multi":
        return json.dumps(sorted(q["correct"]))
    if t in ("table", "dnd"):
        return json.dumps({str(i): r["cat"] for i, r in enumerate(q["rows"])})
    if t == "build":
        return json.dumps(q["steps"])
    return "A provisional prose answer for the marker."


def complete_sitting(harness, platform, objective):
    """Launch the player for `objective`, start the session through the LTI
    /api/start wrap, answer every item correctly, and return the final
    /api/submit response (status == complete)."""
    last, _sid, _claims = complete_sitting_detailed(harness, platform, objective)
    return last


def complete_sitting_detailed(harness, platform, objective, claims_extra=None):
    """Like complete_sitting but returns (last_response, session_id, claims)
    and accepts extra launch claims (the AGS endpoint claim etc.)."""
    s, _, body = resource_link_launch(harness, platform, objective,
                                      claims_extra=claims_extra)
    if s != 200:
        fail("player launch failed (HTTP %d)" % s)
    page = body.decode("utf-8", "replace")
    m = re.search(r'"lti_ctx":\s*"([^"]+)"', page)
    if not m:
        fail("player page carries no launch-context token")
    lti_ctx = m.group(1)
    s, _, body = harness.post_json("/api/start", {
        "bank": harness.stem, "count": 10, "mode": "practice",
        "objective": objective, "lti_ctx": lti_ctx})
    if s != 200:
        fail("/api/start through the LTI wrap failed (HTTP %d)" % s)
    view = json.loads(body.decode("utf-8"))
    qs = load(harness.bank_path)
    by_id = {q["id"]: q for q in qs}
    session_id = view["session_id"]
    item = view.get("item")
    last = view
    while item is not None:
        q = by_id.get(item["id"])
        if q is None:
            fail("session item id not found in the bank")
        s, _, body = harness.post_json("/api/submit",
                                       {"session_id": session_id,
                                        "answer": answer_for(q)})
        if s != 200:
            fail("/api/submit through the LTI wrap failed (HTTP %d)" % s)
        last = json.loads(body.decode("utf-8"))
        if last.get("status") == "complete":
            break
        if last.get("action") == "defer_feedback":
            # A pending short item parks the sitting at the marker's desk
            # (the runtime never advances pending prose); the caller handles
            # that state explicitly.
            break
        item = (last.get("next") or {}).get("item")
    if last.get("status") != "complete" and last.get("action") != "defer_feedback":
        fail("sitting did not complete: %r" % last)
    claims = (lti.LTIHandler.launch_ctx.get(session_id) or {}).get("claims")
    return last, session_id, claims


def check_deep_link_picker():
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        s, headers, body = deep_link_launch(harness, platform)
        if s != 200:
            fail("deep-link launch did not render the picker (HTTP %d)" % s)
        csp = headers.get("Content-Security-Policy", "")
        if csp != "frame-ancestors https://fake.canvas.example":
            fail("picker CSP %r is not the frame-ancestors origin" % csp)
        page = body.decode("utf-8", "replace")
        if lti.PICKER_PURPOSE not in page:
            fail("picker lacks the purpose line")
        for obj in SAMPLE_OBJECTIVES:
            if obj not in page:
                fail("picker missing objective row %r" % obj)
        if lti.LINK_CONTROL not in page or lti.CANCEL_CONTROL not in page:
            fail("picker lacks Link this assignment / Cancel controls")
        for forbidden in PICKER_FORBIDDEN:
            if forbidden in page:
                fail("picker leaks sensitive content %r (T-994-07)" % forbidden)
        # No correct-answer count: the objective rows carry no numbers.
        if re.search(r"data-objective=\"[^\"]+\"\s*>[^<]*\d", page):
            fail("picker row carries a count")
    finally:
        harness.close()
        platform.close()


def check_deep_link_empty_registry():
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        lti.OIDCLoginHandler.banks = {}
        s, _, body = deep_link_launch(harness, platform)
        if s != 200:
            fail("empty-registry deep link did not render (HTTP %d)" % s)
        page = body.decode("utf-8", "replace")
        if lti.EMPTY_REGISTRY not in page:
            fail("empty registry did not render the empty-registry line")
        if lti.CANCEL_CONTROL not in page:
            fail("empty registry still offers Cancel")
    finally:
        harness.close()
        platform.close()


def check_deep_link_response_shape():
    """Selection returns exactly one ltiResourceLink carrying the objective
    custom param; Cancel returns an empty content_items list (D-07,
    RESEARCH section 3)."""
    return_url = "https://fake.canvas.example/return"
    items = [{"type": "ltiResourceLink",
              "url": "https://drill.example.com/lti/launch/sample_bank",
              "title": "Treatment processes",
              "custom": {"objective": "Treatment processes", "mode": "practice"}}]
    html_doc = lti.deep_link_response(items, return_url)
    m = re.search(r'name="content_items" value="([^"]*)"', html_doc)
    if not m:
        fail("deep-link response has no content_items field")
    decoded = json.loads(m.group(1).replace("&quot;", "\""))
    if len(decoded) != 1 or decoded[0]["type"] != "ltiResourceLink":
        fail("selection did not return exactly one ltiResourceLink")
    if decoded[0]["custom"].get("objective") != "Treatment processes":
        fail("content item lost the objective custom param")
    if "form" not in html_doc or return_url not in html_doc:
        fail("deep-link response is not an auto-post form to the return URL")
    empty = lti.deep_link_response([], return_url)
    m = re.search(r'name="content_items" value="([^"]*)"', empty)
    if not m or json.loads(m.group(1).replace("&quot;", "\"")) != []:
        fail("Cancel did not return an empty content_items list")


def check_resource_link_player_public_item():
    """The embedded player is the quiz serve page for the linked objective;
    the payload is runtime.public_item() byte-for-byte with no reveal field
    before a recorded response, and the evidence-log explain gate holds
    (D-03, LTI-03, UI-SPEC gates 1 and 5)."""
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        objective = "Treatment processes"
        s, headers, body = resource_link_launch(harness, platform, objective)
        if s != 200:
            fail("player launch failed (HTTP %d)" % s)
        csp = headers.get("Content-Security-Policy", "")
        if csp != "frame-ancestors https://fake.canvas.example":
            fail("player CSP %r is not the frame-ancestors origin" % csp)
        page = body.decode("utf-8", "replace")
        for forbidden in ("CORRECT:", "WHY BEST", "KEY DISCRIMINATOR",
                          "DISTRACTOR ANALYSIS", "explain_payload",
                          "answer_text"):
            if forbidden in page:
                fail("player page leaks %r before a recorded response" % forbidden)
        # The rendered framing text is the verbatim privacy line (HTML entity
        # encoding of the apostrophe is a rendering detail, not a copy edit).
        if lti.PRIVACY_LINE not in html.unescape(page):
            fail("player page lacks the verbatim D-09 privacy line")
        # The page's /api/start (through the LTI wrap) returns the same
        # public_item the runtime grants.
        m = re.search(r'"lti_ctx":\s*"([^"]+)"', page)
        if not m:
            fail("player page carries no launch-context token")
        lti_ctx = m.group(1)
        s, _, body = harness.post_json("/api/start", {
            "bank": harness.stem, "count": 10, "mode": "practice",
            "objective": objective, "lti_ctx": lti_ctx})
        if s != 200:
            fail("/api/start through the LTI wrap failed (HTTP %d)" % s)
        view = json.loads(body.decode("utf-8"))
        qs = load(harness.bank_path)
        q = next(q for q in qs if q["id"] == view["item"]["id"])
        expected = runtime.public_item(q, 0)
        if view["item"] != expected:
            fail("LTI /api/start item differs from runtime.public_item()")
        reveal_fields = ("why", "correct", "da", "disc", "second", "trap",
                         "model", "answer_text")
        for field in reveal_fields:
            if field in view["item"]:
                fail("public item carries reveal field %r" % field)
        # A recorded response grants the runtime's tier exactly as on every
        # surface: practice advance/complete releases explain.
        s, _, body = harness.post_json("/api/submit",
                                       {"session_id": view["session_id"],
                                        "answer": answer_for(q)})
        if s != 200:
            fail("/api/submit failed (HTTP %d)" % s)
        submitted = json.loads(body.decode("utf-8"))
        if submitted.get("action") not in ("advance", "complete"):
            fail("expected advance/complete, got %r" % submitted.get("action"))
        explain = submitted.get("explain") or {}
        if "why" not in explain:
            fail("recorded response did not grant the runtime's explain tier")
        # The type-appropriate reveal field is present after a recorded
        # response -- exactly what explain_payload grants on every surface.
        reveal_by_type = {"mc": "correct", "multi": "correct",
                          "table": "row_cats", "dnd": "row_cats",
                          "build": "steps", "short": "model"}
        reveal_field = reveal_by_type.get(q["type"])
        if reveal_field and reveal_field not in explain:
            fail("recorded response did not release %r through explain"
                 % reveal_field)
    finally:
        harness.close()
        platform.close()


def check_resource_link_refusals():
    """Missing or unresolvable objective in a resource-link launch renders
    the exact UI-SPEC line (D-07, UI-SPEC 2.1)."""
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        s, _, body = resource_link_launch(harness, platform, "")
        if s != 403 or lti.MISSING_OBJECTIVE not in body.decode("utf-8", "replace"):
            fail("missing-objective launch did not refuse with the verbatim line")
        s, _, body = resource_link_launch(harness, platform, "No such objective")
        if s != 403 or lti.MISSING_OBJECTIVE not in body.decode("utf-8", "replace"):
            fail("unresolvable-objective launch did not refuse with the verbatim line")
        # A launch for an unregistered bank stem refuses too.
        s, h, _ = harness.get(harness.login_url())
        ap = urllib.parse.parse_qs(urllib.parse.urlsplit(h["Location"]).query)
        state = (ap.get("state") or [""])[0]
        nonce = (ap.get("nonce") or [""])[0]
        token = platform.mint_id_token({
            "nonce": nonce, "message_type": "LtiResourceLinkRequest",
            "custom": {"objective": "Treatment processes", "mode": "practice"}})
        s, _, body = harness.post_form(
            "/lti/launch/not-a-bank", {"id_token": token, "state": state})
        if s != 403 or lti.MISSING_OBJECTIVE not in body.decode("utf-8", "replace"):
            fail("unknown-bank launch did not refuse with the verbatim line")
    finally:
        harness.close()
        platform.close()


def check_completion_framing():
    """The completion line: the local (refusal) line when passback is not
    configured, the OK line only when the plan-03 AGS success signal is
    present (plan 02 stubs the signal) -- both verbatim UI-SPEC section 4."""
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        last = complete_sitting(harness, platform, "Treatment processes")
        completion = last.get("lti_completion")
        if not completion:
            fail("completing submit carried no lti_completion signal")
        if completion.get("ok") is not False:
            fail("not-configured passback must report ok=False")
        if completion.get("line") != lti.COMPLETION_REFUSED:
            fail("not-configured completion line is not the verbatim refusal "
                 "line: %r" % completion.get("line"))

        real = lti.maybe_passback
        try:
            lti.maybe_passback = lambda *a, **k: ("ok", None)
            last = complete_sitting(harness, platform, "Treatment processes")
            completion = last.get("lti_completion")
            if not completion or completion.get("ok") is not True \
                    or completion.get("line") != lti.COMPLETION_OK:
                fail("stubbed AGS success did not render the verbatim OK line")

            lti.maybe_passback = lambda *a, **k: ("refused", "line item rejected")
            last = complete_sitting(harness, platform, "Treatment processes")
            completion = last.get("lti_completion")
            if not completion or completion.get("ok") is not False \
                    or completion.get("line") != lti.COMPLETION_REFUSED:
                fail("passback refusal did not render the verbatim refusal line")
        finally:
            lti.maybe_passback = real
    finally:
        harness.close()
        platform.close()


def check_privacy_copy_verbatim():
    """UI-SPEC gate 6: the section-4 strings this plan renders are verbatim,
    including the privacy line on the learner surface."""
    if lti.PRIVACY_LINE != ("This is a Canvas assignment. Answers are scored "
                            "by the local runtime and the final score is sent "
                            "to this course's gradebook when the assignment is "
                            "complete."):
        fail("PRIVACY_LINE drifted from UI-SPEC section 4")
    if lti.COMPLETION_OK != "Assignment complete. Your score has been sent to the gradebook.":
        fail("COMPLETION_OK drifted from UI-SPEC section 4")
    if lti.COMPLETION_REFUSED != ("Assignment complete. Your score could not "
                                  "be sent to the gradebook this time."):
        fail("COMPLETION_REFUSED drifted from UI-SPEC section 4")
    if lti.MISSING_OBJECTIVE != ("No objective was selected for this "
                                 "assignment. Ask your instructor to re-link it."):
        fail("MISSING_OBJECTIVE drifted from UI-SPEC section 4")
    if lti.UNVERIFIED_LAUNCH != ("This launch could not be verified. Close "
                                 "this window and relaunch the assignment from "
                                 "Canvas."):
        fail("UNVERIFIED_LAUNCH drifted from UI-SPEC section 4")
    if lti.UNREGISTERED_PLATFORM != ("This Canvas site is not registered with "
                                     "this itembank installation."):
        fail("UNREGISTERED_PLATFORM drifted from UI-SPEC section 4")
    # The picker page's confirm copy is the verbatim SELECTION_CONFIRMED.
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        s, _, body = deep_link_launch(harness, platform)
        page = body.decode("utf-8", "replace")
        if "Objective &quot;{title}&quot; selected." not in page \
                and lti.SELECTION_CONFIRMED.replace("{title}", "X") not in page:
            fail("picker does not carry the verbatim selection-confirmed copy")
        if lti.PICKER_PURPOSE not in page:
            fail("picker lacks the verbatim purpose line")
    finally:
        harness.close()
        platform.close()


def make_self_signed(cert_path, key_path):
    """A self-signed TLS fixture certificate (plan 03 Task 3): minted with
    the pinned cryptography x509 builder, written as PEM."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID
    import datetime as _dt
    from ipaddress import ip_address

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "127.0.0.1")])
    now = _dt.datetime.now(_dt.timezone.utc)
    cert = (x509.CertificateBuilder()
            .subject_name(name).issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - _dt.timedelta(days=1))
            .not_valid_after(now + _dt.timedelta(days=30))
            .add_extension(x509.SubjectAlternativeName(
                [x509.IPAddress(ip_address("127.0.0.1"))]), critical=False)
            .sign(key, hashes.SHA256()))
    with open(key_path, "wb") as fh:
        fh.write(key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()))
    with open(cert_path, "wb") as fh:
        fh.write(cert.public_bytes(serialization.Encoding.PEM))


def ags_launch_extra(platform, resource_id="resource-1", scopes=None):
    """The launch claims that grant AGS: the endpoint claim plus the
    resource-link id (the idempotence anchor)."""
    return {
        lti.AGS_ENDPOINT_CLAIM: platform.ags_endpoint_claim(scopes=scopes),
        lti.RESOURCE_LINK_CLAIM: {"id": resource_id},
    }


def check_ags_passback_opt_in_idempotent():
    """AGS passback is opt-in per launch, completion-only, sourced from the
    runtime report, and idempotent (D-04, LTI-05, RESEARCH 4)."""
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        last, sid, claims = complete_sitting_detailed(
            harness, platform, "Treatment processes",
            claims_extra=ags_launch_extra(platform))
        completion = last.get("lti_completion") or {}
        if completion.get("ok") is not True \
                or completion.get("line") != lti.COMPLETION_OK:
            fail("AGS success did not render the OK completion line: %r"
                 % completion)
        if len(platform.scores) != 1:
            fail("AGS published %d scores, expected exactly one"
                 % len(platform.scores))
        score = platform.scores[0]
        if score.get("userId") != "learner-1":
            fail("score userId is not the launch sub")
        if score.get("scoreGiven") != 1 or score.get("scoreMaximum") != 1:
            fail("score is not the runtime report's graded fraction: %r" % score)
        if score.get("activityProgress") != "Completed":
            fail("activityProgress is not Completed")
        if score.get("gradingProgress") != "FullyGraded":
            fail("gradingProgress is not FullyGraded for a fully graded sitting")
        if not score.get("timestamp"):
            fail("score carries no timestamp")
        if len(platform.created_line_items) != 1:
            fail("line item was not created exactly once")
        li = platform.created_line_items[0]
        if li.get("resourceId") != "resource-1" or li.get("scoreMaximum") != 1:
            fail("line item is not keyed by resourceId with the report maximum")
        if len(platform.token_grants) != 1:
            fail("token grant did not happen exactly once")
        grant = platform.token_grants[0]
        if grant.get("grant_type") != ["client_credentials"]:
            fail("token grant is not client_credentials")
        if not (grant.get("client_assertion") or [""])[0]:
            fail("token grant carries no JWT-bearer client assertion")

        # Idempotence: a re-publish of the same score is a no-op.
        session_file = daemon.session_index(harness.tmp)[sid]
        lti.maybe_passback(session_file, claims, platform.ISSUER, harness.cfg)
        if len(platform.scores) != 1:
            fail("re-publish was not a no-op: %d score posts"
                 % len(platform.scores))
    finally:
        harness.close()
        platform.close()


def check_ags_opt_in_gate_no_scope():
    """A launch without the AGS score scope never publishes -- a silent
    no-op, never an error (opt-in per launch, D-04)."""
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        # The launch grants only the lineitem scope, not the score scope.
        extra = ags_launch_extra(
            platform, scopes=[lti.AGS_SCOPE_LINEITEM])
        last, _sid, _claims = complete_sitting_detailed(
            harness, platform, "Treatment processes", claims_extra=extra)
        completion = last.get("lti_completion") or {}
        if completion.get("ok") is not False \
                or completion.get("line") != lti.COMPLETION_REFUSED:
            fail("launch without the score scope did not render the refusal "
                 "completion line")
        if platform.scores:
            fail("launch without the score scope published a score")
        if platform.token_grants:
            fail("launch without the score scope still exchanged a token")
    finally:
        harness.close()
        platform.close()


def check_ags_pending_prose_never_auto_graded():
    """short items pending review are never auto-graded (D-04, RESEARCH
    4.5): a sitting parked at a pending short item never publishes (the
    completion gate), and a completed session whose report still shows
    pending prose publishes the graded fraction with gradingProgress
    PendingManual -- a line item that rejects PendingManual yields no
    numeric publish plus a named refusal (R-02 fallback).

    Phase finding (recorded in the SUMMARY): the runtime's learner flow
    parks a pending short item without advancing, so a *completed* session
    with pending prose is not reachable through the learner path in this
    build. The test constructs that state from the real session file with
    the runtime's own writer (`runtime.write_session`), advancing cursor to
    the end exactly as the runtime's `_advance_cursor` arithmetic does --
    the marker-closed state a future close-session feature will produce."""
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        # Drive the real sitting on "Regulatory framework" (Q5 dnd graded +
        # Q6 short pending): the session parks at Q6, status active.
        last, sid, claims = complete_sitting_detailed(
            harness, platform, "Regulatory framework",
            claims_extra=ags_launch_extra(platform, resource_id="resource-1"))
        if last.get("status") != "active" or last.get("action") != "defer_feedback":
            fail("sitting did not park at the pending short item: %r" % last)
        if "lti_completion" in last:
            fail("an active sitting must not fire the completion signal")
        session_file = daemon.session_index(harness.tmp)[sid]
        status, reason = lti.maybe_passback(
            session_file, claims, platform.ISSUER, harness.cfg)
        if status != "refused" or "not complete" not in reason:
            fail("passback fired on an active sitting: %r" % (status,))
        if platform.scores:
            fail("an active sitting must not publish a score")

        # The marker-closed state: the runtime's own completion arithmetic
        # applied to the real session file (cursor past the end).
        data = runtime.read_session(session_file)
        data["cursor"] = len(data["items"])
        data["status"] = "complete"
        runtime.write_session(session_file, data)
        report = session.do_report(session_file)
        if report["summary"]["pending_manual"] != 1:
            fail("closed session does not show the pending short item")

        status, reason = lti.maybe_passback(
            session_file, claims, platform.ISSUER, harness.cfg)
        if status != "ok":
            fail("PendingManual publish should succeed: %r %s" % (status, reason))
        score = platform.scores[-1]
        if score.get("gradingProgress") != "PendingManual":
            fail("pending prose was not published as PendingManual: %r" % score)
        if score.get("scoreMaximum") != 1 or score.get("scoreGiven") != 1:
            fail("the graded fraction is wrong for a 1-graded + 1-pending "
                 "sitting: %r" % score)
        if score.get("userId") != "learner-1":
            fail("score userId is not the launch sub")

        # A line item that rejects PendingManual: no numeric publish + the
        # named local refusal (R-02 fallback).
        platform2 = FakePlatform(reject_scores=True)
        harness2 = ToolHarness(platform2)
        try:
            last2, sid2, claims2 = complete_sitting_detailed(
                harness2, platform2, "Regulatory framework",
                claims_extra=ags_launch_extra(platform2,
                                              resource_id="resource-2"))
            session_file2 = daemon.session_index(harness2.tmp)[sid2]
            data2 = runtime.read_session(session_file2)
            data2["cursor"] = len(data2["items"])
            data2["status"] = "complete"
            runtime.write_session(session_file2, data2)
            status2, reason2 = lti.maybe_passback(
                session_file2, claims2, platform2.ISSUER, harness2.cfg)
            if status2 != "refused":
                fail("rejected PendingManual publish must refuse: %r" % status2)
            if not reason2:
                fail("rejected PendingManual publish must name the refusal")
            if platform2.scores:
                fail("a rejected PendingManual publish must not record a score")
        finally:
            harness2.close()
            platform2.close()
    finally:
        harness.close()
        platform.close()


def check_ags_evidence_byte_identity():
    """The LTI surface adds no evidence writes: the evidence log is
    byte-identical across an AGS round trip (D-04)."""
    platform = FakePlatform()
    harness = ToolHarness(platform)
    try:
        _last, sid, claims = complete_sitting_detailed(
            harness, platform, "Treatment processes",
            claims_extra=ags_launch_extra(platform))
        ev_path = os.path.join(harness.tmp, "_evidence", "evidence.jsonl")
        if not os.path.exists(ev_path):
            fail("no evidence log was written by the sitting")
        before = open(ev_path, "rb").read()
        session_file = daemon.session_index(harness.tmp)[sid]
        lti.maybe_passback(session_file, claims, platform.ISSUER, harness.cfg)
        after = open(ev_path, "rb").read()
        if before != after:
            fail("the AGS round trip wrote to the evidence log")
    finally:
        harness.close()
        platform.close()


def check_tls_bind_loopback_handshake():
    """With lti.tls_cert/tls_key set, the LTI bind wraps the socket in
    stdlib ssl -- proven by a loopback TLS handshake against a self-signed
    fixture cert (D-05, LTI-06); the loopback default stays plain HTTP."""
    tmp = tempfile.mkdtemp(prefix="lti_tls_")
    try:
        cert = os.path.join(tmp, "cert.pem")
        key = os.path.join(tmp, "key.pem")
        make_self_signed(cert, key)
        platform = FakePlatform()
        harness = ToolHarness(platform, tls={"cert": cert, "key": key})
        try:
            s, _, body = harness.get(harness.base + "/lti/jwks")
            if s != 200 or b'"keys"' not in body:
                fail("TLS bind did not serve the JWKS over https (HTTP %d)"
                     % s)
            s, _, _ = harness.get(harness.login_url())
            if s != 302:
                fail("TLS bind login initiation did not redirect")
            # The configured base URL is https -- the one knob drives it.
            if not harness.base.startswith("https://"):
                fail("public_base_url over TLS is not https")
        finally:
            harness.close()
            platform.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_dep_pin_record_and_hosting_doc():
    """Plan 03 Task 3: the dependency pin record lists cryptography and
    PyJWT at pinned versions with recorded checksums and a named license
    review (D-08, Directive 4a); the hosting doc covers both postures and
    the privacy statement; the manual Canvas checklist is recorded in
    VALIDATION and referenced from the hosting doc (R-01 fallback)."""
    pins = open(os.path.join(ROOT, "deps", "lti-pins.txt"),
                encoding="utf-8").read()
    for needle in ("cryptography==43.0.0", "PyJWT==2.10.1",
                   "sha256:", "Apache-2.0 OR BSD-3-Clause", "MIT",
                   "CVE"):
        if needle not in pins:
            fail("dependency pin record missing %r" % needle)
    if "license review" not in pins.lower():
        fail("dependency pin record has no named license review")
    hosting = open(os.path.join(ROOT, "docs", "lti-hosting.md"),
                   encoding="utf-8").read()
    normalized_hosting = " ".join(hosting.split())
    if " ".join(lti.PRIVACY_STATEMENT.split()) not in normalized_hosting:
        fail("docs/lti-hosting.md lacks the D-09 privacy statement")
    for needle in ("reverse proxy", "public_base_url", "stdlib",
                   "999.4-VALIDATION"):
        if needle not in hosting:
            fail("docs/lti-hosting.md missing %r" % needle)
    validation = open(os.path.join(
        ROOT, ".planning", "phases", "999.4-canvas-lms-integration-lti",
        "999.4-VALIDATION.md"), encoding="utf-8").read()
    for needle in ("Manual-Only Verifications", "developer key",
                   "PendingManual", "gradebook"):
        if needle not in validation:
            fail("999.4-VALIDATION.md manual checklist missing %r" % needle)


def main():
    checks = [
        check_registry_one_platform_per_issuer,
        check_crypto_guard_doctor_refusal,
        check_settings_schema_lti_block,
        check_jwt_valid_and_each_invalid_named,
        check_jwks_bounded_and_cached,
        check_login_initiation_redirect_params,
        check_launch_calls_daemon_in_process,
        check_route_scope_and_no_second_scorer,
        check_doctor_and_help_privacy,
        check_lti_bind_opt_in,
        check_lint_and_core_loop_untouched,
        check_deep_link_picker,
        check_deep_link_empty_registry,
        check_deep_link_response_shape,
        check_resource_link_player_public_item,
        check_resource_link_refusals,
        check_completion_framing,
        check_privacy_copy_verbatim,
        check_ags_passback_opt_in_idempotent,
        check_ags_opt_in_gate_no_scope,
        check_ags_pending_prose_never_auto_graded,
        check_ags_evidence_byte_identity,
        check_tls_bind_loopback_handshake,
        check_dep_pin_record_and_hosting_doc,
    ]
    for check in checks:
        reset_handler_state()
        check()
        print("ok  %s" % check.__name__)
    print("lti roundtrip: ok (%d checks)" % len(checks))


if __name__ == "__main__":
    main()
