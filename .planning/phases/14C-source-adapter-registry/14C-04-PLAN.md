---
phase: 14C-source-adapter-registry
plan: 04
type: execute
wave: 4
depends_on: ["14C-03"]
files_modified:
  - source_adapters.py
  - surfaces/daemon.py
  - surfaces/cli.py
  - fixtures/audit/web_capture_fidelity_cases.py
  - tests/source_adapters_roundtrip.py
  - tests/daemon_roundtrip.py
autonomous: true
requirements: [D-03, D-04, D-05, OQ-4, ROSTER-3-WEB, BUILD-BOTH-BIND-POLICY, BUILD-BOTH-SNAPSHOT, RIGHTS-01, RIGHTS-02, TREAT-02]
estimate:
  tokens: 200000
  raw_tokens: 100000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "A remote page is bound as a captured snapshot, never as a URL: the fingerprint is taken over the derived Markdown of the capture, the URL and the capture timestamp are recorded as provenance in the sidecar origin block, and the bound material reads offline afterwards with the network unplugged."
    - "A redirect whose target scheme is not http or https is refused with source.redirect_refused, and the Authorization header is stripped the moment a redirect crosses to a different origin, reusing the AuthStrippingRedirectHandler precedent rather than a second implementation."
    - "A URL whose host resolves to a loopback, private, link-local, or unique-local address is refused with source.origin_refused by default, and the refusal is liftable only by the source.allow_private_origins setting, never by a request body field."
    - "Both snapshot storage paths ship: inline copy for a capture under source.snapshot_inline_max_bytes and reference plus cache above it. The derived Markdown fingerprint is identical either way, so a citation cannot tell which was used."
    - "Both bind policies ship behind one setting. Under approve_before_bind, an agent actor importing without confirm: true is refused with source.approval_required and nothing is written; under auto_fetch the same call proceeds. Preview extracts and returns without writing under both policies, so searching and reading stay free."
    - "A changed or vanished remote origin surfaces as a read-time advisory. itembank source recheck reports origin_unchanged, origin_changed, or origin_unreachable, appends nothing to the journal, and changes no fingerprint, so a citation issued against the captured revision stays exactly as valid as it was when it was made."
    - "A recheck against an unreachable network reports origin_unreachable and exits 0 with a named state, not a traceback and not a failure, so the core loop degrades and never blocks."
    - "Every web locator carries a CSS selector to its containing block plus a text quote with prefix and suffix, so a citation survives a minor DOM change rather than breaking on a shifted XPath index."
    - "No test in this phase makes a real network request. Every fetch assertion runs against a loopback http.server fixture."
  prohibitions:
    - statement: "No second parser, scorer, or evidence store. Readable-text extraction produces Markdown that auditor.normalize_source then spans; the adapter computes no spans of its own."
      status: flagged-unverified
      verification: "check_no_second_parser is re-run; git diff --stat model.py runtime.py auditor.py reports no change."
    - statement: "No rewrite of itembank in TypeScript and no plugin kernel reimplemented in Python."
      status: flagged-unverified
      verification: "files_modified contains six Python files, none of them a loader or kernel module."
    - statement: "No hosted multi-tenant anything. Snapshots and evidence stay on disk under the caller-supplied approved root."
      status: flagged-unverified
      verification: "check_snapshot_containment asserts an inline snapshot lands under base/_sources and that a reference-mode capture writes its cache under base/_sources/cache, both refused outside base by discovery.inside_any_root."
    - statement: "PyMuPDF and ebooklib are not adopted, and trafilatura is not adopted."
      status: flagged-unverified
      verification: "grep -i -E 'pymupdf|fitz|ebooklib|trafilatura' source_adapters.py deps/source-adapter-pins.txt finds no import and no pin line for any of the four."
    - statement: "An unresolved rights grant is never treated as permissive. A remote capture with no prior rights record carries identity.rights_default(), all seven unknown."
      status: flagged-unverified
      verification: "check_remote_capture_rights asserts the sidecar rights block of a fresh capture has every one of the seven operations set to unknown, and that a later import from that capture is refused with journal.rights_unknown."
  artifacts:
    - "_extract_web, _fetch_url, SchemeLockedRedirectHandler, _host_is_private, _store_snapshot, and _readable_html in source_adapters.py"
    - "recheck_origin in source_adapters.py, the read-time staleness advisory"
    - "POST /api/source/recheck in daemon.API_ROUTES, ROUTE_CLI, and SURFACE_PARITY"
    - "itembank source recheck in surfaces/cli.py"
    - "fixtures/audit/web_capture_fidelity_cases.py with static HTML cases"
    - "check_web_gold_cases, check_redirect_hardening, check_private_origin_refused, check_snapshot_both_ways, check_bind_policy_gate, check_recheck_states in tests/source_adapters_roundtrip.py"
  key_links:
    - "journal.commit_operation defaults a kind=source object with no rights argument to identity.rights_default(), all seven unknown. A remote capture has no pre-existing local file to link, so source_object_id is None, the RIGHTS-01 transform gate does not fire, and the capture is minted with unknown rights. That is correct and deliberate: unknown rights stay restrictive by construction, and any later import derived from the capture is refused until a grant is recorded."
    - "journal.detect_external_edits re-hashes an on-disk file against its accepted fingerprint. There is no on-disk file for a URL, so none of that machinery can fire for remote staleness. recheck_origin must therefore be a pure read that appends nothing; wiring it into the journal would make a citation's validity depend on network reachability, which breaks D-04 and the degrade-never-block rule at the same time."
    - "The ROUTE_CLI value for the recheck route must be the single word source, matching the import route, because tests/daemon_roundtrip.py:check_route_cli_inventory greps surfaces/cli.py for add_parser(\"<value>\") and there is exactly one source parser. Both API routes map to the same CLI command name, exactly as three day routes already map to day."
---

<objective>
Bring remote sources in. `14C-CONTEXT.md` D-03 records that treating sources as
learner-owned local files was interpretation drift rather than language from
`USER-VISION.md`: online courses, video, and web material are first-class source
types. D-04 records how they bind, which is as a captured snapshot rather than a
URL, because the whole binding model runs on fingerprints and a URL has no
stable bytes.

This plan also settles both of the "build both" items in `14C-CONTEXT.md` and
closes open question 4.

Decisions already made, cited, and never re-litigated here:

- **D-03** (`14C-CONTEXT.md` lines 36 to 39, recorded in
  `USER-VISION-INBOX.md` 2026-08-20): remote sources are in scope.
- **D-04** (lines 40 to 45): bind a snapshot, not a URL. Capture on bind,
  fingerprint the capture, record the URL and capture timestamp as provenance.
- **D-05**: the adapter never touches the scorer.
- **D-14C-1** (`14C-DECISIONS.md`): the frozen sidecar contract, whose `origin`
  block already carries `fetched_at`, `http_etag`, `http_last_modified`, and
  `snapshot_rel_path`, and whose `body_web` row already carries `css_selector`
  and `text_quote`. Nothing in the schema changes here; plan `14C-01` froze
  these fields precisely so this plan would not need to.
- **OQ-4, locked in `14C-01-PLAN.md`**: remote staleness is a read-time advisory
  and never a mutation of the accepted revision. This plan builds it.
- **`PLANNING-DIRECTIVES.md` section 3**, the conflict rule: where two designs
  are both defensible, implement both behind one interface and make the choice a
  setting. `14C-CONTEXT.md` names two such pairs and this plan builds all four
  paths.
- **`.claude/CLAUDE.md` Network constraint**: the core loop degrades, never
  blocks. Sitting a quiz, scoring, lessons, the hint ladder, evidence, and
  reports all work with the network unplugged, and so must reading a source that
  was already captured.
- **RESEARCH Pitfall 4 and the Security Domain SSRF row**: the redirect and
  private-address hardening this plan owes.

Purpose: make a web page a citable source that stays readable offline.
Output: the web adapter, both snapshot paths, both bind policies, the staleness
advisory, and its route and command.
</objective>

<execution_context>
@$HOME/.claude/gsd-core/workflows/execute-plan.md
@$HOME/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/phases/14C-source-adapter-registry/14C-CONTEXT.md
@.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md
@.planning/phases/14C-source-adapter-registry/14C-PATTERNS.md
@.planning/phases/14C-source-adapter-registry/14C-VALIDATION.md
@.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md
@.planning/phases/14C-source-adapter-registry/14C-01-PLAN.md
@.planning/phases/14C-source-adapter-registry/COVERAGE.md
@.planning/SUPPLY-CHAIN-POLICY.md
@surfaces/update.py
@source_adapters.py
@journal.py
</context>

## Artifacts this phase produces (plan 14C-04 share)

- `source_adapters.py`
  - New class `SchemeLockedRedirectHandler(urllib.request.HTTPRedirectHandler)`.
  - New functions: `_host_is_private(host)`, `_fetch_url(url, options)`,
    `_readable_html(raw, encoding)`, `_extract_web(raw_bytes, options)`,
    `_store_snapshot(base, source_id, raw, content_type, options)`,
    `capture_url(base, url, actor_kind, actor_name, options=None)`,
    `recheck_origin(base, source_object_id, options=None)`.
  - New constants: `MAX_REDIRECTS = 5`, `RECHECK_STATES`, `SNAPSHOT_DIRNAME`,
    `SNAPSHOT_CACHE_DIRNAME`, `USER_AGENT`.
  - `ADAPTER_REGISTRY` gains `"web"`; `ADAPTER_VERSIONS` gains `"web": "1.0.0"`.
- `surfaces/daemon.py`
  - New constant `SOURCE_RECHECK_ALLOWED_FIELDS`.
  - New handler `handle_api_source_recheck(handler)`.
  - One new row each in `API_ROUTES` (fourteenth), `ROUTE_CLI`, and
    `SURFACE_PARITY`.
- `surfaces/cli.py`
  - New `recheck` subcommand under the existing `source` parser, plus `--url`
    handling on the existing `import` subcommand.
- `fixtures/audit/web_capture_fidelity_cases.py`
  - `sha256`, `CASE_TABLE`, `materialize`, plus `serve_cases(port)` returning a
    configured `http.server` handler class for the loopback fixture.
- `tests/source_adapters_roundtrip.py` and `tests/daemon_roundtrip.py`
  - The check functions named in `must_haves.artifacts`.

New refusal codes used by this plan, all already present in
`SOURCE_ADAPTER_CODES` from plan `14C-01`: `source.fetch_failed`,
`source.redirect_refused`, `source.origin_refused`, `source.oversized`,
`source.unsupported`, `source.approval_required`, `source.dependency_missing`.
No new code is added.

New non-refusal state vocabulary: `RECHECK_STATES = ("origin_unchanged",
"origin_changed", "origin_unreachable")`. These are advisory report states, not
error codes, and they never appear in a journal entry.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: static HTML gold cases plus the loopback fetch fixture</name>
  <files>fixtures/audit/web_capture_fidelity_cases.py, tests/source_adapters_roundtrip.py</files>
  <read_first>
- `fixtures/audit/locator_fidelity_cases.py` lines 1 to 30 and 613 to 626, for
  the stdlib-only, deterministic, repository-independent fixture contract and
  the `materialize` shape.
- `fixtures/audit/pptx_fidelity_cases.py` as built by plan `14C-03`, the most
  recent example of this file family.
- `tests/daemon_roundtrip.py`, whichever function starts a loopback server for a
  test. Grep for `http.server`, `TCPServer`, and `start_daemon` and reuse the
  existing idiom for binding a throwaway loopback port and tearing it down in a
  `finally`. Do not invent a second server-fixture pattern.
- `.planning/phases/14C-source-adapter-registry/14C-VALIDATION.md`, the
  "Roster 3 web capture" row, which specifies static HTML fixtures for the
  parsing half and a separate loopback integration case for the redirect
  hardening.
  </read_first>
  <behavior>
Write these assertions first, watch them fail, then build.

- `check_web_fixture_determinism`: every case's `build()` is byte-stable across
  two calls in one process and hashes to its recorded `gold["sha256"]`;
  `materialize()` writes only inside the temporary directory it is given.
- `check_loopback_fixture_serves`: the loopback server started from
  `serve_cases` returns the expected status, body, and headers for each of its
  routes, including the redirect routes, before any adapter code touches it.
  This proves the fixture itself is correct so a later adapter failure is
  unambiguous.
  </behavior>
  <action>
1. Create `fixtures/audit/web_capture_fidelity_cases.py` with a module docstring
   in the register of the two existing fixture files: name the phase and plan
   (14C, plan `14C-04`), state that the case table is immutable data, that the
   builders are pure functions, that nothing reads or writes the repository, and
   that imports are stdlib only (`hashlib`, `http.server`, `io`, `os`). State
   in one sentence that no case makes a real network request, and that the
   loopback server exists so the redirect and private-address refusals are
   proven against a real socket rather than a mocked one.

2. Build these six static HTML cases, each a `bytes` payload with its recorded
   sha256, `structures`, `reading_order`, `unsupported`, and
   `adapter_expectation`:
   - `web-article-simple`: an HTML document with a `<h1>`, two `<p>` elements
     inside an `<article>`, plus a navigation bar and a footer that the readable
     extraction must drop. `reading_order` is `["w.0", "w.1", "w.2"]`.
     `adapter_expectation` `"supported"`.
   - `web-article-nested-sections`: two `<section>` blocks each with a heading
     and a paragraph, so the CSS selector in each locator names a different
     containing block. `adapter_expectation` `"supported"`.
   - `web-duplicate-text`: a document containing the same sentence twice in two
     different sections. This is the case that proves the text quote carries a
     prefix and a suffix: a bare exact quote cannot disambiguate the two, so the
     gold records two locators whose `text_quote.exact` values are identical and
     whose `prefix` values differ. `adapter_expectation` `"supported"`.
   - `web-nonutf8-charset`: a document declaring `charset=iso-8859-1` in a meta
     tag with a byte in the high range, so the decode path is exercised rather
     than assumed. `adapter_expectation` `"supported"`.
   - `web-script-only`: a document whose `<body>` contains only a `<script>`
     block and an empty `<div id="root">`, the shape of a client-rendered page.
     `structures` and `reading_order` are empty; `unsupported` is
     `["no readable text: the page renders its content with JavaScript"]`;
     `adapter_expectation` `"unsupported"`.
   - `web-malformed-truncated`: an HTML document cut off mid-tag.
     `adapter_expectation` records whatever the readable extraction actually
     produces on it, recorded once from a real run rather than guessed; if it
     extracts text, mark it `"supported"` with the produced reading order, and
     if it produces nothing, `"unsupported"` with the message
     `no readable text: malformed document`.

3. Implement `serve_cases(port)` returning a `http.server.BaseHTTPRequestHandler`
   subclass configured with a route table. The routes, all `GET`:
   - `/article` returns `web-article-simple`'s bytes with
     `Content-Type: text/html; charset=utf-8`, an `ETag` of `"fixture-etag-1"`,
     and a `Last-Modified` header.
   - `/article-changed` returns the same path's bytes with one paragraph altered
     and an `ETag` of `"fixture-etag-2"`, used by the recheck test.
   - `/redirect-to-article` returns 302 with `Location: /article`.
   - `/redirect-to-file` returns 302 with a `Location` of a `file:` scheme URL.
   - `/redirect-loop` returns 302 pointing at itself.
   - `/redirect-cross-origin` returns 302 with an absolute `Location` on a
     different loopback port, used by the header-stripping test.
   - `/slow` sleeps past a one-second timeout before responding, used by the
     timeout test.
   - `/huge` returns a `Content-Length` above a test-supplied cap, used by the
     oversize test.
   - `/notfound` returns 404.
   The handler suppresses its own request logging so a passing test prints
   nothing, matching how the daemon test harness handles its server.

4. Implement `materialize(dest_dir)` in the same shape the other two fixture
   files use, writing each static case's bytes as a `.html` file.

5. Add `check_web_fixture_determinism` and `check_loopback_fixture_serves` to
   `tests/source_adapters_roundtrip.py` and to its `__main__` sequence. Bind the
   loopback server on port 0 and read back the assigned port, so a busy port on
   the developer's machine never makes the suite flaky.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py</automated>
Expected: exit 0. The degraded state this task must prove is that the whole
fixture works with no external network at all: run the check with the machine's
network interface unavailable if possible, and in any case assert that no case
resolves a hostname other than `127.0.0.1` or `localhost`.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 -c "import sys,os; sys.path.insert(0,os.path.join('fixtures','audit')); import web_capture_fidelity_cases as g; assert len(g.CASE_TABLE)==6; assert callable(g.serve_cases); print('web fixtures ok')"` prints `web fixtures ok`.
- `grep -c -E "http://(?!127\.0\.0\.1|localhost)" fixtures/audit/web_capture_fidelity_cases.py` returns 0, or the equivalent check confirms no absolute non-loopback URL is present outside the deliberate `file:` redirect target.
- `python3 itembank.py guard .` exits 0.
- The new fixture file contains no em dash character.
  </acceptance_criteria>
  <precondition>tests/daemon_roundtrip.py already contains a loopback server harness whose idiom this fixture follows.</precondition>
  <reversibility rating="reversible">A new fixture file with no consumers until Task 2.</reversibility>
  <done>Six deterministic static HTML cases and one loopback server fixture exist, and the fixture is proven correct before any adapter is tested against it.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the web capture adapter, both snapshot paths, and both bind policies</name>
  <files>source_adapters.py, surfaces/cli.py, tests/source_adapters_roundtrip.py</files>
  <read_first>
- `surfaces/update.py` lines 440 to 490 in full: `_origin_of` and
  `AuthStrippingRedirectHandler`, the shipped precedent for hardening a stdlib
  redirect. Its docstring records the exact defect it fixed (CR-01, a token
  leaked onto GitHub's separately-hosted CDN origin) and the stickiness property
  the new handler must preserve.
- `.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md`, Pitfall 4 in
  full, the Code Examples section headed "Web capture fetch with redirect
  hardening", and the Security Domain SSRF row, which records that full
  DNS-rebinding-safe hardening is judged disproportionate for a single-user
  local product while the scheme lock is worth taking regardless.
- `.planning/phases/14C-source-adapter-registry/COVERAGE.md`, surface 1, the
  full capability matrix. Every `INTEGRATE` row is owed by this task and every
  `OPT-OUT` row is deliberately absent; do not add an opted-out capability.
- `journal.py` lines 330 to 356 (`commit_operation`), 415 to 421 (the
  `kind == "source"` rights default), and 432 to 450 (the RIGHTS-01 gate, which
  does not fire when `source_object_id` is `None`).
- `source_adapters.py` as landed by plans `14C-01` through `14C-03`: the
  four-tuple extraction contract, `import_source`'s ten-step order,
  `build_sidecar`, `write_sidecar_atomic`, and the lazy per-adapter import
  discipline.
- `surfaces/settings.py` lines 154 to 195 (`load_settings`), for how the
  `source` settings group added by plan `14C-01` reaches this code.
- The frozen `body_web` and `origin` rows in `14C-01-PLAN.md`'s "The frozen
  sidecar contract" section.
  </read_first>
  <behavior>
Write these assertions first, watch them fail, then implement. Every one runs
against the loopback fixture from Task 1; none makes a real network request.

- `check_web_gold_cases`: each static case's bytes extract to its recorded
  reading order, or to the recorded refusal message.
- `check_redirect_hardening`, four scenarios: `/redirect-to-article` follows and
  captures the article; `/redirect-to-file` is refused with
  `source.redirect_refused` and its message names the rejected scheme;
  `/redirect-loop` is refused after at most `MAX_REDIRECTS` hops with
  `source.fetch_failed`; `/redirect-cross-origin` arrives at the second server
  with no `Authorization` header present, asserted by having that second server
  record the headers it received.
- `check_private_origin_refused`: a capture of a URL whose host is `127.0.0.1`
  is refused with `source.origin_refused` when
  `options["allow_private_origins"]` is `False`, and succeeds when it is `True`.
  The whole test suite therefore runs with the setting lifted, which is itself
  the proof that the default is deny and that lifting it is what makes loopback
  fetching possible at all.
- `check_fetch_limits`: `/slow` with a one-second timeout returns
  `source.fetch_failed` naming a timeout; `/huge` with a small cap returns
  `source.oversized`; `/notfound` returns `source.fetch_failed` whose message
  contains `404`.
- `check_snapshot_both_ways`: capturing the same page twice, once with
  `snapshot_storage` `"inline"` and once with `"reference"`, produces two
  sidecars whose `fingerprint` values are identical and whose
  `origin.snapshot_rel_path` differs, one being a path under `_sources` and the
  other `None`. In reference mode the raw bytes land under
  `_sources/cache` and the sidecar records the cache path in
  `origin.value`-adjacent provenance rather than inline. Assert that both modes
  read back offline: after the loopback server is stopped, the derived Markdown
  is still readable from disk.
- `check_bind_policy_gate`, four cases: under `approve_before_bind` an
  `actor_kind` of `"agent"` with no `confirm` is refused with
  `source.approval_required` and writes nothing; the same call with
  `confirm: True` proceeds; an `actor_kind` of `"human"` proceeds without
  `confirm`; under `auto_fetch` the agent call proceeds without `confirm`.
  Additionally, `preview_source` returns an extraction result and writes nothing
  under both policies, for both actor kinds, which is the assertion that
  searching and reading stay free.
- `check_remote_capture_rights`: a fresh capture's sidecar `rights` block has
  all seven operations set to `"unknown"`, and a later `import_source` naming
  that capture as `source_object_id` is refused with `journal.rights_unknown`.
- `check_snapshot_containment`: a `base` plus a crafted `source_id` cannot place
  a snapshot outside `base`; the write is refused.
- `check_web_locator_anchors`: in the `web-duplicate-text` case, the two
  locators sharing an identical `text_quote.exact` have different `prefix`
  values and different `css_selector` values, so a citation into either
  resolves unambiguously.
  </behavior>
  <action>
1. Add `SchemeLockedRedirectHandler` to `source_adapters.py`, subclassing
   `urllib.request.HTTPRedirectHandler`. Its `redirect_request` calls
   `super().redirect_request(...)` first so stdlib still decides whether a
   redirect is legal at all, then: refuses when the new URL's scheme is not
   `http` or `https` by raising `urllib.error.URLError` with a message naming
   the refused scheme; and strips any `Authorization` header case-insensitively
   from both `headers` and `unredirected_hdrs` when
   `_origin_of(req.full_url) != _origin_of(newurl)`, copying the sticky-strip
   behavior `surfaces/update.py`'s handler documents. Import and reuse
   `surfaces.update._origin_of` rather than writing a second origin comparator;
   if importing across the surfaces boundary is awkward, copy the three-line
   function and state in a comment that it is a deliberate duplicate of
   `surfaces/update.py`'s and must stay in step with it.

2. Add `_host_is_private(host)`. Resolve the host with
   `socket.getaddrinfo`, then for each resolved address build an
   `ipaddress.ip_address` and return `True` when any of `is_loopback`,
   `is_private`, `is_link_local`, `is_reserved`, `is_multicast`, or
   `is_unspecified` holds. Return `True` on a resolution failure, because an
   unresolvable host is refused rather than attempted. State in the docstring
   that this is a best-effort check that does not close DNS rebinding, that
   `identity.py`'s own recorded threat model is a single local user with no
   attacker, and that the check exists because it is cheap and correct for the
   real case (an agent handed a URL that points at the learner's own network),
   not because it claims to be a security boundary.

3. Add `_fetch_url(url, options)`. In order: parse the URL and refuse a scheme
   other than `http` or `https` with `source.redirect_refused`; call
   `_host_is_private` and refuse with `source.origin_refused` unless
   `options["allow_private_origins"]` is `True`; build an opener with
   `SchemeLockedRedirectHandler` and a redirect cap of `MAX_REDIRECTS`; issue a
   `GET` with a `User-Agent` of `USER_AGENT` and a timeout of
   `options["fetch_timeout_seconds"]`; refuse a `Content-Length` above
   `options["max_input_bytes"]` before reading the body, and refuse again after
   a bounded read of at most that many bytes plus one, because a chunked
   response declares no length; return the four-tuple `(raw_bytes,
   content_type, etag, last_modified)`. Convert every `urllib.error.URLError`,
   `urllib.error.HTTPError`, `socket.timeout`, and `OSError` into
   `source.fetch_failed` carrying the status code or the error text. Nothing
   raises.

4. Add `_readable_html(raw, encoding)`. Import `readability` inside the function
   body; on `ImportError` return `source.dependency_missing` whose message ends
   with the literal `run: pip install readability-lxml==0.8.4.1`. Decode the
   bytes using the charset from the `Content-Type` header when present,
   otherwise from a `meta charset` declaration, otherwise UTF-8 with
   `errors="replace"` as the last resort; record which path was taken so the
   sidecar `confidence` can be `"medium"` rather than `"high"` when a fallback
   decode was used. Run readability's summary extraction, then walk the
   resulting fragment to produce, per block-level element with non-empty text:
   the Markdown line, the CSS selector to that element built from tag names,
   ids, and nth-of-type positions from the fragment root, and the text quote
   object with `exact` set to the element's text, `prefix` set to the last 32
   characters of text preceding it in document order, and `suffix` set to the
   first 32 characters following it. A page whose readable fragment yields no
   block with text returns the refusal message
   `no readable text: the page renders its content with JavaScript` when the
   original document contained a `<script>` element and a body with no text, and
   `no readable text: malformed document` otherwise.

5. Add `_extract_web(raw_bytes, options)` conforming to the four-tuple
   extraction contract, delegating to `_readable_html` and emitting locators with
   id `"w.%d" % index`, `kind` `"block"`, and body
   `{"medium": "web", "css_selector": ..., "text_quote": {"exact": ..., "prefix": ..., "suffix": ...}}`.
   Register `"web"` in `ADAPTER_REGISTRY` and `"web": "1.0.0"` in
   `ADAPTER_VERSIONS`.

6. Add `_store_snapshot(base, source_id, raw, content_type, options)`
   implementing both storage paths, which is the `PLANNING-DIRECTIVES.md`
   section 3 "build both" answer to `14C-CONTEXT.md`'s snapshot question:
   - Resolve the effective mode from `options["snapshot_storage"]`. `"auto"`
     picks `"inline"` when `len(raw) <= options["snapshot_inline_max_bytes"]`
     and `"reference"` otherwise.
   - `"inline"` writes the raw bytes to
     `<base>/_sources/<source_id>.snapshot<ext>` through
     `write_sidecar_atomic`'s same temp-plus-replace helper, and returns that
     relative path for `origin.snapshot_rel_path`.
   - `"reference"` writes the raw bytes to
     `<base>/_sources/cache/<source_id>.snapshot<ext>` and returns `None` for
     `origin.snapshot_rel_path`, so the sidecar records that the capture is
     cached rather than owned. State in the docstring that the cache directory
     is disposable derived state that a future cleanup may evict, while an
     inline snapshot is not.
   - Both paths check `discovery.inside_any_root(target, [base])` before
     writing, so a crafted `source_id` cannot escape the root.
   - The derived Markdown fingerprint is computed from the extraction, never
     from the snapshot bytes, which is why both modes produce the identical
     fingerprint and a citation cannot tell which was used. State that sentence
     in the docstring; it is the property `check_snapshot_both_ways` asserts.

7. Add `capture_url(base, url, actor_kind, actor_name, options=None)`, the
   remote sibling of `import_source`. It follows the same ten-step order with
   three differences, each stated in a comment: the bytes come from
   `_fetch_url` rather than from a registry row; `md_rel_path` is
   `_sources/<source_id>.md` and the sidecar is
   `_sources/<source_id>.locator.json`, both derived from the minted id and
   never from the URL, because a URL is attacker-shaped input and a path is not
   built from it; and `journal.commit_operation` is called with
   `source_object_id=None`, so the RIGHTS-01 transform gate does not fire and
   `commit_operation` defaults the new `kind="source"` object to
   `identity.rights_default()`, all seven rights unknown. That default is the
   point, not an oversight: a captured page carries no rights record until the
   learner records one, and any later import derived from it is refused by name
   until they do.

8. Implement the bind policy gate, the `PLANNING-DIRECTIVES.md` section 3
   answer to `14C-CONTEXT.md`'s auto-fetch question. In both `import_source` and
   `capture_url`, before any write: when
   `options["bind_policy"] == "approve_before_bind"` and `actor_kind` is
   `"agent"` and the caller did not pass `confirm=True`, return
   `source.approval_required` with the message
   `an agent bind requires explicit approval under the approve_before_bind policy; pass confirm to proceed, or set source.bind_policy to auto_fetch`.
   Under `"auto_fetch"` the gate does not fire. `preview_source` never consults
   the gate at all, under either policy and for either actor kind, because
   searching and reading are free in both and only the bind step is gated. State
   that sentence in `preview_source`'s docstring.

9. In `surfaces/cli.py`, extend the existing `source import` subcommand with a
   `--url` argument that routes to `capture_url` instead of `import_source`, and
   with `--snapshot-storage` (choices `auto`, `inline`, `reference`) and
   `--confirm` (a `store_true`). `--file` and `--url` are mutually exclusive and
   argparse enforces it; supplying neither exits 1 with the message
   `source import needs one of --file or --url`.

10. Add every check named in the `behavior` block to
    `tests/source_adapters_roundtrip.py` and to its `__main__` sequence. Every
    one binds the loopback fixture on port 0 and tears it down in a `finally`.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py</automated>
Expected: exit 0. The degraded states this task must prove, all asserted inside
the checks above rather than described: a redirect to a non-http scheme is
refused by name; a cross-origin redirect arrives with no Authorization header; a
timeout, a 404, and an oversize response each return a typed code rather than
raising; a private-address host is refused by default; and a captured page reads
back from disk after the server that served it has been stopped.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 -c "import source_adapters as s; assert 'web' in s.ADAPTER_REGISTRY; assert issubclass(s.SchemeLockedRedirectHandler, __import__('urllib.request',fromlist=['x']).HTTPRedirectHandler); print('web registered')"` prints `web registered`.
- `python3 -c "import source_adapters as s; assert s._host_is_private('127.0.0.1') is True; assert s._host_is_private('10.0.0.1') is True; assert s._host_is_private('169.254.1.1') is True; print('private hosts refused')"` prints `private hosts refused`.
- `python3 -c "import source_adapters as s; assert s.MAX_REDIRECTS==5; assert s.RECHECK_STATES==('origin_unchanged','origin_changed','origin_unreachable'); print('constants ok')"` prints `constants ok`.
- `grep -c "an agent bind requires explicit approval" source_adapters.py` returns
  at least 1, the mechanical proof that the approve-before-bind copy is written
  out in full rather than left as an appropriate message.
- `python3 itembank.py source import --help` exits 0 and its output contains
  `--url`, `--snapshot-storage`, and `--confirm`.
- `python3 schema_validate.py --all` exits 0.
- `for t in tests/*.py; do python3 "$t" || exit 1; done` exits 0.
- `python3 itembank.py guard .` exits 0.
- `git diff --stat runtime.py model.py auditor.py journal.py` reports no change.
- No file changed by this task contains an em dash character.
  </acceptance_criteria>
  <precondition>readability-lxml 0.8.4.1 is installed from deps/source-adapter-pins.txt, and Task 1's loopback fixture exists.</precondition>
  <reversibility rating="costly">The snapshot directory layout under _sources and _sources/cache becomes the place captured bytes live; moving it later means relocating every captured snapshot and rewriting the origin block of every sidecar that names one.</reversibility>
  <done>A remote page is captured, snapshotted both ways, fingerprinted once, and refused by name on every hostile input, with no test touching the real network.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: the staleness advisory, its route, and its command</name>
  <files>source_adapters.py, surfaces/daemon.py, surfaces/cli.py, tests/source_adapters_roundtrip.py, tests/daemon_roundtrip.py</files>
  <read_first>
- `14C-01-PLAN.md`'s objective table, the OQ-4 row, which locks the design this
  task implements. Read it before writing a line.
- `.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md`, Open Question 4
  in full, including the three-step recommendation and the explicit note that
  the mechanism is tagged `[ASSUMED]` at MEDIUM confidence because no identical
  pattern exists elsewhere in the repository.
- `journal.py` lines 1150 to 1210 (`detect_external_edits`) and 1210 onward
  (`reconcile`), so it is concrete why neither can fire for a URL: both re-hash
  an on-disk file against its accepted fingerprint, and a URL has no on-disk
  file to re-hash.
- `journal.py` lines 936 to 946 (`op_edit_in_place`), the operation a learner's
  explicit re-capture would use. This task does not build re-capture; it names
  the operation so a later plan does not invent a different one.
- `surfaces/daemon.py` lines 214 to 335 as amended by plan `14C-01`, and the
  `handle_api_source_import` handler that plan added, which this handler mirrors.
- `tests/daemon_roundtrip.py` `check_api_route_scope` as amended by plan
  `14C-01` to assert 13; it becomes 14 here.
  </read_first>
  <behavior>
Write these assertions first, watch them fail, then implement.

- `check_recheck_states`, three scenarios against the loopback fixture, each
  starting from a page already captured through `capture_url`:
  1. The server still serves the identical bytes with the identical `ETag`.
     `recheck_origin` reports `origin_unchanged`.
  2. The server is switched to `/article-changed`, which serves different bytes
     with a different `ETag`. `recheck_origin` reports `origin_changed`.
  3. The server is stopped. `recheck_origin` reports `origin_unreachable`.
  In all three, assert afterwards that `journal.entries(base)` has exactly the
  same length it had before the recheck, that the registry row's `fingerprint`
  is unchanged, and that the sidecar file on disk is byte-identical. This is the
  whole point: a recheck is a read.
- `check_recheck_preserves_citation`: build an `auditor.citation(source_id,
  fingerprint, span_id)` record against the captured source before the recheck,
  run scenario 2 above, and assert the citation record is still exactly equal to
  itself afterwards and still resolves against the on-disk sidecar. A changed
  remote origin never invalidates an issued citation.
- `check_recheck_no_validator_falls_back`: a capture whose response carried
  neither an `ETag` nor a `Last-Modified` header rechecks by fetching and
  comparing the derived Markdown fingerprint, and still reports one of the three
  states rather than failing.
- In `tests/daemon_roundtrip.py`: extend `check_api_route_scope` to assert
  `len(daemon.API_ROUTES) == 14` and that
  `daemon.ROUTE_CLI[("POST", "/api/source/recheck")] == "source"`; add
  `check_api_source_recheck_route` asserting a cross-origin POST returns 403, an
  unknown field returns 400, and an unknown `source_object_id` returns 404; and
  extend `check_cross_origin_gate_on_mutating_routes`'s route tuple with the new
  endpoint.
  </behavior>
  <action>
1. Add `RECHECK_STATES = ("origin_unchanged", "origin_changed",
   "origin_unreachable")` to `source_adapters.py` and record in a comment above
   it that these are advisory report states, never journal entry states and
   never `SOURCE_ADAPTER_CODES` members, because the two vocabularies must not
   be confused by a later reader.

2. Add `recheck_origin(base, source_object_id, options=None)`. In order: read
   the registry row and refuse an unknown id with `source.malformed_input`; read
   the sidecar beside the object's recorded path and refuse a missing sidecar
   with `source.malformed_input`; return early with a report of
   `origin_unchanged` and a note when `origin.kind` is `"local_file"`, because a
   local file's drift is `journal.detect_external_edits`'s job and this function
   must not duplicate it; when `origin.http_etag` or
   `origin.http_last_modified` is present, issue a conditional `GET` with
   `If-None-Match` or `If-Modified-Since` through the same `_fetch_url`
   hardening and report `origin_unchanged` on a 304; otherwise fetch, run the
   same extraction, compute
   `identity.object_fingerprint(md_bytes, "source")` over the fresh derived
   Markdown, and report `origin_unchanged` when it equals the recorded
   fingerprint and `origin_changed` when it does not; report
   `origin_unreachable` on any `source.fetch_failed`.

3. Make the read-only property structural rather than promised. `recheck_origin`
   must not call `journal.commit_operation`, `journal.append_entry`,
   `write_sidecar_atomic`, or `_store_snapshot`, and its docstring states that.
   Assert it in the test by comparing `len(journal.entries(base))` before and
   after, and by comparing the sidecar bytes before and after. Also state in the
   docstring that a learner who chooses to re-capture does so through a separate,
   explicit operation that commits a new revision with
   `journal.op_edit_in_place`, keeping the same `object_id` and leaving the
   previous bytes recoverable as a before-image, and that no plan in Phase 14C
   builds that re-capture command; naming it here is what stops a later plan
   from inventing a different mechanism.

4. The report shape returned by `recheck_origin` is a dict with
   `schema_version`, `source_id`, `state` (one of `RECHECK_STATES`),
   `checked_at` (from `identity.utc_now()`), `origin` (the sidecar's origin
   block verbatim), and `note`, a plain sentence written out in full. The three
   notes, verbatim:
   - `origin_unchanged`: `The remote origin still matches the captured snapshot. Nothing needs to change.`
   - `origin_changed`: `The remote origin has changed since it was captured. The captured snapshot and every citation into it are still valid; re-capture only if you want the newer version.`
   - `origin_unreachable`: `The remote origin could not be reached. The captured snapshot is still readable offline and every citation into it is unaffected.`

5. Add `SOURCE_RECHECK_ALLOWED_FIELDS = ("source_object_id",)` and
   `handle_api_source_recheck(handler)` to `surfaces/daemon.py`, modeled on
   `handle_api_source_import`. It is a read, not a write, so it uses
   `_reject_cross_origin(handler)` rather than `_reject_cross_origin_write`,
   matching how `/api/report` and the other read routes are gated; state that
   difference in the handler docstring so the looser gate is a recorded choice
   and not an omission. An unknown `source_object_id` is a 404 through
   `handler.send_not_found`.

6. Add the three table rows: `("POST", "/api/source/recheck",
   "handle_api_source_recheck")` as the fourteenth `API_ROUTES` entry,
   `("POST", "/api/source/recheck"): "source"` in `ROUTE_CLI`, and
   `(("POST", "/api/source/recheck"), "source", "source_recheck")` in
   `SURFACE_PARITY`. Update the `API_ROUTES` comment block to say fourteen and
   to name the new route.

7. Add the `recheck` subcommand under the existing `source` parser in
   `surfaces/cli.py`: arguments `--base` defaulting to `"."`, a positional
   `object_id`, and `--json`. Human output is three lines: the state, the origin
   value, and the note. Exit code is 0 for all three states, including
   `origin_unreachable`, because an unreachable network is a reported state and
   not a command failure; that is the degrade-never-block rule applied to this
   command. State the exit-code decision in the subcommand's help text.

8. Update `tests/daemon_roundtrip.py` per the `behavior` block and add the
   recheck checks to `tests/source_adapters_roundtrip.py`.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py &amp;&amp; python3 tests/daemon_roundtrip.py</automated>
Expected: both exit 0. The degraded state this task must prove is scenario 3:
with the origin server stopped, `itembank source recheck` prints
`origin_unreachable` with its note and exits 0, and the captured Markdown is
still readable from disk.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 tests/daemon_roundtrip.py` exits 0.
- `python3 -c "import sys; sys.path.insert(0,'surfaces'); import daemon; assert len(daemon.API_ROUTES)==14; assert ('POST','/api/source/recheck','handle_api_source_recheck') in daemon.API_ROUTES; assert daemon.ROUTE_CLI[('POST','/api/source/recheck')]=='source'; print('recheck route registered')"` prints `recheck route registered`.
- `python3 -c "import inspect, source_adapters as s; src=inspect.getsource(s.recheck_origin); assert 'commit_operation' not in src and 'append_entry' not in src and 'write_sidecar_atomic' not in src; print('recheck is a read')"` prints `recheck is a read`.
- `grep -c "The remote origin has changed since it was captured" source_adapters.py` returns at least 1.
- `grep -c "The captured snapshot is still readable offline" source_adapters.py` returns at least 1.
- `python3 itembank.py source recheck --help` exits 0.
- `for t in tests/*.py; do python3 "$t" || exit 1; done` exits 0.
- `python3 itembank.py guard .` exits 0.
- No file changed by this task contains an em dash character.
  </acceptance_criteria>
  <precondition>Task 2 landed capture_url and _fetch_url, and plan 14C-01 landed the thirteen-entry API_ROUTES table.</precondition>
  <reversibility rating="costly">A second published route literal and a second published CLI subcommand name are a contract for any external harness that uses them, so renaming later needs a deprecation window. It is rated costly rather than one-way, and carries no checkpoint of its own, because the naming pattern is not a new decision: plan `14C-01`'s OQ-3 answer already locked one fixed-literal route per capability with opaque identifiers in the body, and already named `POST /api/source/recheck` as the one additional route this phase would add. This task implements that locked answer rather than opening a new door.</reversibility>
  <done>A changed or vanished remote origin is a reported state that touches nothing, an issued citation survives it, and an unreachable network is a state rather than a failure.</done>
</task>

</tasks>

<threat_model>
ASVS level 1. Block on `high`.

## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Learner or agent supplied URL to itembank's own process | An arbitrary URL is fetched from inside the learner's own network position. |
| Remote origin to redirect handler | A remote server controls the `Location` header on every hop. |
| Remote response body to the readable-text extractor | Arbitrary HTML reaches `lxml` inside itembank's process. |
| Extracted remote text to a downstream agent | Content authored by a third party becomes context a model later reads. |
| Adapter to durable disk | A snapshot, a derived Markdown file, and a sidecar are written under the approved root using a server-influenced content type. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14C-20 | Information Disclosure | `_fetch_url` reaching an internal address | high | mitigate | `_host_is_private` resolves the host and refuses any loopback, private, link-local, reserved, multicast, or unspecified address, and refuses an unresolvable host, with `source.origin_refused`. Default deny, liftable only by the `source.allow_private_origins` setting in `itembank.json`, never by a request body field. Asserted by `check_private_origin_refused`. |
| T-14C-21 | Tampering | redirect to a non-http scheme | high | mitigate | `SchemeLockedRedirectHandler.redirect_request` refuses any target whose scheme is not `http` or `https`, so a `file:` or `ftp:` redirect cannot make the fetcher read a local file. Asserted against a real loopback server issuing a `file:` redirect. |
| T-14C-22 | Information Disclosure | header leak across a redirect origin | high | mitigate | The `Authorization` header is stripped case-insensitively from both `headers` and `unredirected_hdrs` the moment the origin changes, and the strip is sticky across later hops, copying the shipped `surfaces/update.py` handler that exists because this defect already happened once (CR-01). Asserted by a second loopback server recording the headers it received. |
| T-14C-23 | Denial of Service | unbounded or slow response | high | mitigate | `Content-Length` is checked against `source.max_input_bytes` before reading; the body read is bounded to that many bytes plus one so a chunked response with no declared length is caught too; the request carries `source.fetch_timeout_seconds`; the redirect chain is capped at `MAX_REDIRECTS`. All four asserted by `check_fetch_limits`. |
| T-14C-24 | Tampering | snapshot path built from a URL | high | mitigate | The snapshot, derived Markdown, and sidecar paths are all built from the minted `object_id` and never from any part of the URL. `discovery.inside_any_root` is checked before every write. Asserted by `check_snapshot_containment`. |
| T-14C-25 | Tampering | remote content read as instructions | medium | mitigate | Extracted remote text is data. `capture_url` and `recheck_origin` construct no prompt, no tool call, and no shell command from it; the daemon serializes the result and returns it. The route and module docstrings state this boundary explicitly so a later phase that hands this text to a model does so knowing it is third-party authored. |
| T-14C-26 | Elevation of Privilege | an agent binding unvetted material unattended | medium | mitigate | The `approve_before_bind` default refuses an agent bind without explicit `confirm`, by name, with copy that tells the learner both ways forward. Preview stays free under both policies, so the gate costs an agent nothing except the write. Asserted by `check_bind_policy_gate`. |
| T-14C-27 | Spoofing | a captured page claiming rights it does not have | medium | mitigate | A remote capture is minted with `source_object_id=None`, so `commit_operation` defaults it to `identity.rights_default()`, all seven unknown. Any later import derived from it is refused with `journal.rights_unknown` until the learner records a grant. Asserted by `check_remote_capture_rights`. |
| T-14C-28 | Denial of Service | entity expansion or a billion-laughs payload in remote HTML | medium | mitigate | `readability-lxml` parses HTML rather than XML, and `lxml`'s HTML parser does not resolve external entities. The response is size-capped before it reaches the parser, which bounds the input regardless. `_parse_xml_safely` is not used here because the input is HTML, not an OOXML part; recorded so the difference is deliberate. |
| T-14C-29 | Repudiation | a recheck silently mutating an accepted revision | high | mitigate | `recheck_origin` calls none of `commit_operation`, `append_entry`, `write_sidecar_atomic`, or `_store_snapshot`, asserted mechanically by an `inspect.getsource` grep in the acceptance criteria and by a before-and-after journal length comparison in the test. A changed origin never invalidates an issued citation, asserted by `check_recheck_preserves_citation`. |
| T-14C-30 | Information Disclosure | fetching discloses the learner's interest to a third party | low | accept | Fetching a page the learner asked for reveals to that origin that the page was fetched, which is what fetching means. No credential, no cookie, and no referrer chain is sent; the `User-Agent` is a fixed constant. Recorded so it is known rather than discovered. |
| T-14C-SC | Tampering | npm/pip/cargo installs | high | mitigate | No new package. readability-lxml was reviewed and pinned by plan `14C-01` Task 2's blocking human checkpoint; trafilatura is refused on dependency weight and appears in no pin line. `deps/source-adapter-pins.txt` is not edited here. |
</threat_model>

<out_of_scope>
- **Every `OPT-OUT` row in `COVERAGE.md` surface 1.** Proxy authentication,
  cookies, HTTP authentication, client TLS certificates, JavaScript rendering,
  non-GET methods, HTTP/2 and HTTP/3, range requests, and robots.txt are each
  refused with a recorded reason there. Do not add one because it seems useful.
- **Re-capture.** `recheck_origin` reports; it never re-captures. The learner's
  explicit re-capture through `journal.op_edit_in_place` is named so a later
  plan does not invent a different mechanism, and is not built here.
- **Automatic or scheduled rechecking.** A recheck is always explicit. Making
  citation resolution depend on network reachability would break both D-04 and
  the degrade-never-block rule.
- **Video and audio capture.** A URL pointing at media is roster item 5, ASR,
  registered and planned last. This adapter captures readable text.
- **trafilatura.** Refused on dependency weight in `14C-RESEARCH.md`'s
  Alternatives table. The reconsideration condition is recorded there: revisit
  if readability-lxml's extraction quality proves inadequate on real course
  material.
- **DNS rebinding hardening.** `_host_is_private` resolves once and does not
  pin the resolved address for the connection. Closing that gap means a custom
  connection factory, which `14C-RESEARCH.md` judges disproportionate for a
  single-user local product. Recorded as a known limit in the function
  docstring rather than silently absent.
- **Any change to `runtime.py`, `model.py`, `auditor.py`, or `journal.py`.**
</out_of_scope>

<verification>
1. `python3 tests/source_adapters_roundtrip.py` (exit 0)
2. `python3 tests/daemon_roundtrip.py` (exit 0)
3. `python3 schema_validate.py --all` (exit 0)
4. `for t in tests/*.py; do python3 "$t" || exit 1; done` (exit 0)
5. `python3 itembank.py guard .` (exit 0)
6. `git diff --stat runtime.py model.py auditor.py journal.py` (no output)
</verification>

<success_criteria>
- A page is captured, fingerprinted, and readable offline afterwards.
- Every hostile fetch input is refused by a named code, proven against a real
  loopback socket and never a mock.
- Both snapshot paths and both bind policies ship, with the same fingerprint and
  the same free preview.
- A recheck reports one of three states, writes nothing, and leaves every issued
  citation exactly as valid as it was.
- Zero em dash characters in any file this plan created or changed.
</success_criteria>

<summary_obligations>
`.planning/phases/14C-source-adapter-registry/14C-04-SUMMARY.md` records:

- Whether `surfaces.update._origin_of` was imported or duplicated, and if
  duplicated, why the import was awkward, so a later cleanup knows.
- The actual readability-lxml API surface used, since the plan describes it from
  documentation. Record the exact call and the shape it returned.
- Whether the `web-malformed-truncated` case extracted text or produced nothing,
  since the plan deliberately left that gold value to be recorded from a real
  run rather than guessed.
- Any capability from `COVERAGE.md` surface 1 marked `INTEGRATE` that could not
  be built, with the reason. Move it to `OPT-OUT` with that reason in the same
  commit; an undecided hole is not acceptable.
- Which truth was verified by which command and which `check_*` function.
</summary_obligations>

<output>
Create `.planning/phases/14C-source-adapter-registry/14C-04-SUMMARY.md` when done.
</output>
