# API Coverage - remote origin fetch (HTTP/HTTPS via stdlib urllib) and ASR backends

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
> Written 2026-08-21 by the Phase 14C planning pass.

Phase 14C touches two external surfaces. Neither is a vendor SDK, so this
matrix is scoped to the capability set each surface actually exposes.

## Surface 1: remote origin fetch (roster item 3, web capture)

The web-capture adapter fetches a learner-supplied URL with stdlib
`urllib.request` and stores a snapshot (D-04). The external surface is plain
HTTP, so the capability list below is HTTP's own semantics rather than a
vendor's method list. Owner: `source_adapters.py`, plan `14C-04`.

| capability | decision | reason |
|---|---|---|
| GET with an explicit timeout | INTEGRATE | |
| Explicit User-Agent header | INTEGRATE | |
| Redirect following, scheme-locked to http and https | INTEGRATE | |
| Redirect following, auth-header stripping across origins | INTEGRATE | reuses `surfaces/update.py:458` `AuthStrippingRedirectHandler` |
| Redirect hop cap | INTEGRATE | |
| Content-Type sniffing and charset selection | INTEGRATE | |
| Content-Length and streamed-read byte cap | INTEGRATE | |
| ETag capture at fetch time | INTEGRATE | stored in the sidecar `origin.http_etag`, read back by `source recheck` |
| Last-Modified capture at fetch time | INTEGRATE | stored in the sidecar `origin.http_last_modified` |
| Conditional GET (`If-None-Match`, `If-Modified-Since`) | INTEGRATE | the `source recheck` staleness path, plan `14C-04` |
| HEAD request for a cheap reachability probe | OPT-OUT | Moved from INTEGRATE on 2026-08-28 by plan `14C-04`, which built the recheck. A HEAD answers only "is it reachable", and the no-validator fallback has to answer "did it change", which needs the body: `recheck_origin` fetches, re-extracts, and compares the derived fingerprint. Adding a HEAD first would be a second round trip that answers a question the GET already answers. Revisit if a reachability-only probe is ever wanted on its own. |
| Private, loopback, and link-local destination refusal | INTEGRATE | default deny, liftable by the `source.allow_private_origins` setting |
| HTTP error status to a typed refusal | INTEGRATE | `source.fetch_failed` carrying the status code |
| Proxy configuration | OPT-OUT | stdlib `urllib` already honors the environment proxy variables; itembank adds no proxy settings surface and no proxy authentication of its own. |
| Cookie jar and session state | OPT-OUT | a snapshot is a one-shot capture of a public page; carrying learner cookies to a third-party origin is egress this phase has no rights grant for (RIGHTS-02). |
| HTTP authentication (Basic, Bearer, form login) | OPT-OUT | no credential store exists for arbitrary origins and creating one is a rights and secrets surface out of this phase's scope; a paywalled origin returns `source.fetch_failed` with its status. |
| Client TLS certificates | OPT-OUT | no learner-supplied client certificate exists in any settings surface today. |
| JavaScript rendering of the fetched page | OPT-OUT | requires a browser engine; a JS-only page yields no readable text and returns `source.unsupported` by name rather than silently empty. |
| POST, PUT, PATCH, DELETE | OPT-OUT | capture is read-only by construction; a source fetch never mutates a remote origin. |
| HTTP/2 and HTTP/3 | OPT-OUT | stdlib `urllib` speaks HTTP/1.1 only; every origin in scope negotiates down. |
| Range requests and resumable partial fetch | OPT-OUT | a partial snapshot cannot be fingerprinted as the captured bytes; a truncated fetch is a failure, not a resumable state. |
| Robots.txt evaluation | OPT-OUT | a single learner-initiated fetch of a page the learner is already reading is not crawling; revisit if batch or agent auto-fetch ever walks link graphs. |

## Surface 2: ASR backend (roster item 5)

No external API integration in this phase: roster item 5 is registered and
not built, so plan `14C-08` adds only the `"asr"` registry key and its typed
`source.backend_unconfigured` refusal. No whisper.cpp binding, no hosted
speech endpoint, and no request is constructed. The capability matrix for a
real ASR backend is owed by the plan that actually builds one, after the
7900 XTX machine exists or a hosted endpoint is chosen.

## Surface 3: local Ollama vision model (roster item 6, OCR)

No new external API integration: plan `14C-07` wraps the already-shipped
`scripts/ocr_lib.py` bridge, which owns the entire Ollama HTTP surface
(`/api/tags` probe, `/api/chat` transcribe). The adapter adds zero new calls
and converts the bridge's two documented `RuntimeError` shapes into typed
refusals. Building a second OCR path is refused by CONTEXT.md roster item 6.
