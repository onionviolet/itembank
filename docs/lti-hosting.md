# Hosting the itembank LTI surface (phase 999.4)

The LTI 1.3 surface makes the item player reachable inside Canvas. LTI
mandates an HTTPS endpoint the platform can reach, so this is the one place
the local-first tool explicitly goes public -- and only when you turn it on
(`lti.enabled: true`). Nothing listens publicly by default; every other
surface keeps its loopback default unchanged (D-05, LTI-06).

**The one knob:** `lti.public_base_url` drives every URL the platform calls --
the OIDC initiation URL, the launch URL, the tool JWKS URL, and the
deep-link return. Set it to the public origin (`https://drill.example.com`)
whether you terminate TLS in the tool or at a reverse proxy. `itembank lti
doctor` prints the exact URLs to paste into Canvas's developer-key
configuration.

## Posture A -- reverse proxy in front (recommended for most installs)

Run the tool behind an existing nginx/Caddy/Traefik instance. The tool stays
on loopback; the proxy terminates TLS and forwards to it.

1. Leave `lti.tls_cert` / `lti.tls_key` empty (both must be empty together).
2. Start the bind: `itembank lti serve <dir> --port 8732` (it binds
   127.0.0.1 and prints the loopback URL).
3. Configure the proxy: TLS certificate for the public hostname, `proxy_pass
   http://127.0.0.1:8732` for the paths `/lti/`, and standard HTTPS headers.
4. Set `lti.public_base_url` to the public origin, e.g.
   `https://drill.example.com`.

This posture keeps the tool itself reachable only from the proxy -- an
operator who prefers the tool to see only the proxy (never the open
internet) picks this one (999.4-RESEARCH A5).

## Posture B -- built-in TLS (stdlib `ssl`, no dependency)

The tool terminates TLS itself with a certificate you supply. No ACME, no
domain ownership, no CA account -- the tool never holds a certificate
authority credential; that stays with your operator (999.4-RESEARCH
section 6).

1. Obtain a certificate for the public hostname (e.g. from your CA or a
   DNS-01 ACME flow) and store cert + key as PEM files.
2. Set `lti.tls_cert` / `lti.tls_key` to those paths (both must be set
   together; exactly one set is a named refusal).
3. Start the bind: `itembank lti serve <dir>`. It wraps the socket in
   stdlib `ssl.SSLContext.load_cert_chain` (server.py `bind_tls`).
4. Set `lti.public_base_url` to the public origin.

## DNS / certificate guidance

- The public hostname must resolve to the machine that terminates TLS.
- The certificate must cover exactly that hostname; the tool does not
  redirect or rewrite it.
- `public_base_url` must be reachable from the learners' browsers (it is
  the URL Canvas frames and posts to).

## Registration (the platform side, manual)

1. Canvas Admin → Developer Keys → "+ LTI Key" → paste the tool's public
   JWK (fetch it from `<public_base_url>/lti/jwks`) and the OIDC initiation
   URL `<public_base_url>/lti/login`; set the target link URI to
   `<public_base_url>/lti/launch/<bank-stem>`.
2. Install the tool by client id; Canvas grants a `deployment_id`. Record
   it in `itembank.json`'s `lti.platforms[].deployments` allowlist.
3. `itembank lti doctor` re-validates the registration and prints the URLs.

## The manual Canvas verification checklist

A real install → launch → deep-link → learner completion → AGS passback →
gradebook inspection run against a live Canvas instance is recorded as
**manual-only** in `.planning/phases/999.4-canvas-lms-integration-lti/
999.4-VALIDATION.md` (the R-01 fallback). The automated suite
(`tests/lti_roundtrip.py`) proves the whole spine against a fake platform
with zero Canvas access; it never fakes a live Canvas result.

## What leaves the machine

Privacy: item text travels to the learner's browser through the LMS, and the
final score is copied to the course gradebook when the assignment is
complete. itembank stores no gradebook, hosts nothing, and sends no telemetry
and no learner evidence beyond the score.

The evidence store stays the local record; the published score is a copy to
the LMS gradebook, outbound-only, at session completion, only when the
launch granted the AGS score scope (D-04). Pending prose is never
auto-graded (`gradingProgress: PendingManual` or no numeric publish).
