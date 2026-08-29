# Plan 14C-04 summary

Executed 2026-08-28 on Darwin arm64, Python 3.14.6. All three tasks ran. The
plan is `autonomous: true` and carries no blocking human checkpoint.

## What landed

- `fixtures/audit/web_capture_fidelity_cases.py`: six static HTML cases with
  recorded gold, a routed loopback `http.server` fixture, and a
  `LoopbackServer` context manager that binds on port 0.
- In `source_adapters.py`: `_origin_of`, `SchemeLockedRedirectHandler`,
  `_host_is_private`, `_fetch_url`, `_decode_html`, `_css_selector`,
  `_readable_html`, `_extract_web`, `_write_bytes_atomic_under`,
  `_store_snapshot`, `_bind_gate`, `capture_url`, `recheck_origin`, plus the
  `MAX_REDIRECTS`, `USER_AGENT`, `SNAPSHOT_DIRNAME`,
  `SNAPSHOT_CACHE_DIRNAME`, `RECHECK_STATES`, and `SOURCE_OPTION_DEFAULTS`
  constants. `web` is registered at `1.0.0`.
- `POST /api/source/recheck` in the daemon's three parity tables with
  `handle_api_source_recheck` and `SOURCE_RECHECK_ALLOWED_FIELDS`.
- `itembank source import --url|--snapshot-storage|--confirm` and
  `itembank source recheck` in `surfaces/cli.py`.
- Fifteen new check functions across `tests/source_adapters_roundtrip.py` and
  `tests/daemon_roundtrip.py`.

## `surfaces.update._origin_of`: duplicated, not imported

**Duplicated**, with the reason written into the copy's docstring. The import
is not merely awkward, it is upward layering: `source_adapters` is a
model-tier module, and `import surfaces.update` pulls in the whole updater,
its settings surface, and its manifest schema so that three strings can be
compared. The copy is three lines and is marked as a deliberate duplicate that
must stay in step with the original. A later cleanup that wants one copy
should move `_origin_of` down into a shared model-tier module rather than
move the adapter up.

## The readability-lxml API surface actually used

The plan describes it from documentation. Measured:

- `readability.Document(text_str).summary()` takes a **str**, not bytes, and
  returns an **HTML string**, not an element tree. The adapter therefore
  decodes first and parses the returned string with
  `lxml.html.fromstring(summary)`.
- The returned fragment is wrapped: `<html><body><div><body
  id="readabilityBody">...`. Every CSS selector this adapter emits is
  therefore relative to that fragment root and starts at `body > div > ...`,
  not at the original document's root. That is a real property of the anchor
  and is worth knowing before a later phase tries to resolve one of these
  selectors against a freshly fetched page.
- **readability does not remove every piece of chrome.** On the
  `web-article-simple` fixture its summary kept the `<nav>` block and dropped
  the `<footer>`. The adapter therefore applies its own `WEB_SKIP_TAGS` skip
  list (nav, footer, aside, script, style, noscript, form) rather than
  trusting the library, and emits only whitelisted block tags whose ancestors
  are neither skipped nor themselves blocks.

## The `web-malformed-truncated` verdict, recorded from a real run

**It produced nothing**, so its gold is `adapter_expectation: "unsupported"`
with the message `no readable text: malformed document`. lxml's HTML parser
does recover from a truncated document, so it parses; but this fixture is cut
at 120 bytes, inside the head, before any content exists, so the readable
fragment holds no text-bearing block. It carries no `<script>` element, which
is exactly what separates its message from the client-rendered page's. Both
the finding and its reasoning are written into the fixture beside the case.

## COVERAGE.md surface 1: one INTEGRATE row moved to OPT-OUT

**`HEAD request for a cheap reachability probe`** could not be built as
specified and is moved to `OPT-OUT` in the same commit, with its reason in the
table. A HEAD answers only "is it reachable"; the no-validator fallback has to
answer "did it change", which needs the body. `recheck_origin` fetches,
re-extracts, and compares the derived fingerprint, so a HEAD first would be a
second round trip answering a question the GET already answers. The
reconsideration condition is recorded there.

Every other `INTEGRATE` row is built, including both conditional-GET headers,
ETag and Last-Modified capture, the streamed byte cap, the redirect hop cap,
and the private-destination refusal. No `OPT-OUT` row was added.

## Which truth was verified by which command and which check

| Truth | Command | `check_*` |
|---|---|---|
| The adapter's own option defaults equal the shipped settings defaults, and both are restrictive | `python3 tests/source_adapters_roundtrip.py` | `check_option_defaults_match_schema` |
| Six deterministic static cases, materialize contained | same | `check_web_fixture_determinism` |
| The loopback fixture serves the statuses, bodies, and headers the adapter checks rely on, including a real 304 | same | `check_loopback_fixture_serves` |
| All six gold cases resolve as recorded | same | `check_web_gold_cases` |
| Two identical sentences on one page stay distinguishable by prefix and by selector | same | `check_web_locator_anchors` |
| Loopback is refused by default and only the setting lifts it | same | `check_private_origin_refused` |
| Scheme-locked, loop-capped, and Authorization stripped across origins but kept same-origin | same | `check_redirect_hardening` |
| A timeout, an oversize body, and a 404 are typed codes | same | `check_fetch_limits` |
| Both storage modes, one fingerprint, both readable with the origin stopped | same | `check_snapshot_both_ways` |
| A crafted id cannot place a snapshot outside the root | same | `check_snapshot_containment` |
| Both bind policies, an unconfirmed agent bind refused by name, preview free under both | same | `check_bind_policy_gate` |
| A fresh capture is all seven rights unknown and deriving from it refuses by name | same | `check_remote_capture_rights` |
| Three recheck states, each appending nothing and changing no fingerprint or sidecar byte | same | `check_recheck_states` |
| A changed origin leaves an issued citation exactly equal to itself | same | `check_recheck_preserves_citation` |
| A capture with no validator still rechecks, by fingerprint | same | `check_recheck_no_validator_falls_back` |
| The recheck route is gated, field-limited, and 404s an unknown source | `python3 tests/daemon_roundtrip.py` | `check_api_source_recheck_route` |
| Fifteen API routes, both source routes mapped to the one `source` CLI twin | same | `check_api_route_scope` |
| The new route is covered by the cross-origin gate sweep | same | `check_cross_origin_gate_on_mutating_routes` |
| `recheck_origin` calls no writer | `python3 -c "import inspect, source_adapters ..."` | prints `recheck is a read` |
| Private hosts refused | `python3 -c "... _host_is_private ..."` | prints `private hosts refused` |
| The approve-before-bind copy is written out in full | `grep -c "an agent bind requires explicit approval" source_adapters.py` | 1 |
| Both recheck notes are in source | `grep -c` for each | 1, 1 |
| The CLI carries the three new flags and the recheck command | `itembank source import --help`, `itembank source recheck --help` | exit 0 |
| A capture and two rechecks driven end to end through the real CLI | live run against a loopback server | `origin_unchanged`, then `origin_unreachable` after stopping it, both exit 0, and the Markdown still read back |
| No repository-authored em dash | `python3 itembank.py guard .` | exit 0 |
| `runtime.py`, `model.py`, `auditor.py`, `journal.py` untouched | `git diff --stat` on the four | empty |
| The whole suite | `for t in tests/*.py; do python3 "$t" || exit 1; done` | 88 of 88 pass |

## Deviations from the plan, each with its reason

1. **The scheme lock sits in `http_error_302`, not in `redirect_request`.**
   Measured, not assumed. stdlib checks the redirect scheme itself, inside
   `http_error_302`, before `redirect_request` is ever called, and its allowed
   set is http, https, **and ftp**. An unpatched run against the fixture's
   `file:` redirect came back as stdlib's own `HTTPError 302` and never
   entered the subclass at all. The lock therefore sits one level up, where it
   also closes the ftp hole stdlib leaves open, and `http_error_301`, `303`,
   `307`, and `308` are re-bound explicitly because stdlib aliases them to its
   own function on the base class.

2. **`MAX_REDIRECTS` is enforced by setting `max_redirections`.** As first
   written the constant was declared and unused, with stdlib's cap of 10 doing
   the work. It is now a class attribute on the handler, so the declared five
   is the real cap.

3. **`origin.kind` is `remote_url`, not `url`.** The frozen schema's enum is
   `("local_file", "remote_url")`; the plan's prose says the origin block
   already carries what this plan needs, and it does, under that name. Caught
   by the sidecar failing its own schema validation on the first capture,
   which is the check working.

4. **`API_ROUTES` goes to fifteen, not fourteen.** The plan was written when
   the table held thirteen; 16B-09 has since added `POST /api/shelf`. The
   recheck route is the fifteenth. `check_api_route_scope`'s message names
   both 14C routes and shelf so the arithmetic is legible next time.

5. **`--adapter` became optional on `source import`.** It is required with
   `--file` and meaningless with `--url`, which always captures through the
   web adapter. `--file` and `--url` are a required mutually exclusive group,
   so argparse enforces exactly one; `source import --file` without
   `--adapter` exits 1 naming what is missing.

6. **The daemon passes `confirm` and settings-derived options through.** The
   route already accepted `confirm` in `SOURCE_IMPORT_ALLOWED_FIELDS` and
   dropped it on the floor. It now reaches `import_source`, which matters
   because the daemon is an agent actor and the shipped default is
   `approve_before_bind`: without this, every route import would be refused.
   `check_cli_and_route_parity` was updated to pass `confirm=True` in its
   route-shaped call for the same reason, with the reason in a comment.

7. **A found defect fixed: `journal_entry_id` was always null.** Plan
   `14C-01`'s `ok_result` reads `record.get("last_entry_id")` from
   `journal.commit_operation`'s return, which is a registry-row-shaped dict
   carrying no entry id at all; the published field has therefore been `null`
   on every successful import since. Found by driving a real capture through
   the CLI and reading the JSON. Fixed inside `source_adapters` with
   `_last_entry_id`, since this phase does not modify `journal.py`, and
   `check_thin_slice` now asserts the returned id equals the applied entry's.

8. **`recheck_origin`'s docstring spells its forbidden calls around rather
   than quoting them.** The plan asks the docstring to name
   `commit_operation`, `append_entry`, `write_sidecar_atomic`, and
   `_store_snapshot`, and the acceptance criterion greps the function's source
   for exactly those names. Both cannot hold: a docstring naming them would
   satisfy the grep while the code did whatever it liked. The docstring says
   what it must and says why it spells the names around, so the grep stays a
   proof about code.

9. **`SOURCE_OPTION_DEFAULTS` is new and not in the plan's artifact list.**
   The plan reads `options["bind_policy"]` and the rest without saying where
   they come from when a caller passes nothing. They now come from a
   module-level dict mirroring the settings schema's own `source` default,
   asserted equal to it by `check_option_defaults_match_schema`, so an
   options-less call is governed by the same restrictive policy a surface
   would load. Surfaces read `itembank.json` and pass the group down;
   `source_adapters` does not reach up into `surfaces.settings`.

10. **The Authorization strip is asserted twice.** The loopback integration
    can only prove the absence of a header this adapter never sends, so
    `check_redirect_hardening` also drives `redirect_request` directly with a
    Request carrying `Authorization`, asserting it is stripped across origins
    and **kept** same-origin.

## What this plan did not do

It did not open plan `14C-05`. It built no re-capture command, no automatic or
scheduled recheck, and no `OPT-OUT` capability from `COVERAGE.md` surface 1.
It adopted no package, edited no pin file, and left `runtime.py`, `model.py`,
`auditor.py`, and `journal.py` untouched. `transcript`, `ocr`, `epub`, and
`asr` remain plans 05 through 08.
