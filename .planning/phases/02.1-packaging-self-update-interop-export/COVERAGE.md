# API Coverage — GitHub Releases (read-only, `api.github.com`)

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
>
> The deterministic detector returned `detected: false` over the ROADMAP phase section alone (no
> PLAN.md existed when it ran). This matrix is produced anyway because the phase genuinely consumes an
> external API — DEL-06 reads GitHub Releases — and because the seal-time gate re-runs the detector
> over the PLAN bodies, which do name the API explicitly. Deciding the surface now is cheaper than
> being blocked at seal.
>
> Scope note: itembank is a **consumer** of GitHub Releases, never a publisher. Publishing a release
> is a human act performed with `gh` or the web UI as part of the release process (`build.py` emits
> the artifacts; it does not upload them). Every write capability below is opted out for that reason,
> not for convenience.

| capability | decision | reason |
|---|---|---|
| `GET /repos/{owner}/{repo}/releases/latest` | INTEGRATE | The one request the updater makes. `surfaces/update.py:check_latest()` (plan 02.1-05) |
| asset object `digest` field (`sha256:<64 hex>`) | INTEGRATE | Primary checksum source. Live-verified 2026-08-07 against a real response; resolves the ROADMAP's flagged open decision. `verify_digest()` |
| asset `browser_download_url` (asset download) | INTEGRATE | Fetching the artifact bytes. `download_asset()` (plan 02.1-07) |
| `SHA256SUMS.txt` release asset (checksum fallback) | INTEGRATE | Required whenever `digest` is null — a pre-GA asset or a partial response must never read as verified. `parse_sha256sums()` |
| `tag_name` parsing and version comparison | INTEGRATE | Strictly-newer refusal, Success Criterion 4. `parse_version()` / `is_newer()` |
| Authenticated requests (`Authorization` header) | INTEGRATE | Optional, from `ITEMBANK_GITHUB_TOKEN` only. Enables a private repository and raises the 60-per-hour unauthenticated limit (D-09) |
| Rate-limit response headers (`X-RateLimit-*`) | INTEGRATE | Distinguishes rate-limited from unreachable so an explicit invocation can print the right line while the background check stays silent |
| `GET /repos/{owner}/{repo}/releases` (list all) | OPT-OUT | The `latest` endpoint answers the only question the updater asks. Listing spends rate-limit budget for a capability nothing consumes; an unparseable `latest` tag is skipped as no-update. |
| Draft and pre-release releases | OPT-OUT | D-07 forbids suffixed tags, so a pre-release has no representable version. Revisit only if the project ever adopts release candidates (`## Deferred Ideas`) |
| Release `body` / release notes rendering | OPT-OUT | The UI-SPEC scopes the updater to CLI text plus one background startup line; there is no surface that would display notes. A browser affordance for the updater is explicitly a later-phase idea |
| `POST /repos/{owner}/{repo}/releases` (create) | OPT-OUT | itembank never publishes a release. Publishing is a human step in the release process |
| `PATCH` / `DELETE` on a release | OPT-OUT | Same — the tool is a consumer, not a publisher |
| Asset upload (`uploads.github.com`) | OPT-OUT | Same — `build.py` emits artifacts locally; uploading them is a human step |
| `POST .../releases/generate-notes` | OPT-OUT | No consumer; release notes are written by hand |
| Reactions on releases | OPT-OUT | No consumer; not a capability a local study tool has any use for |
| Git tags / refs API | OPT-OUT | Version identity comes from the release's own `tag_name`; a second source for the same fact is a second thing that can disagree |
| Webhooks / event subscriptions | OPT-OUT | Requires a reachable endpoint and a persistent service. Contradicts the local-first, no-server constraint outright |
| GraphQL API | OPT-OUT | The one REST call needed is simpler and needs no schema knowledge; a second API surface for one query is not proportionate |
