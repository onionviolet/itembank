---
phase: 16B-ia-modes-recovery-contract
plan: 03
type: execute
wave: 3
depends_on: ["16B-02"]
files_modified:
  - surfaces/ia.py
  - surfaces/daemon.py
  - surfaces/cli.py
  - tests/ia_route_roundtrip.py
autonomous: true
requirements: [APP-03]
estimate:
  tokens: 62000
  raw_tokens: 62000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "Every named error code this phase can produce routes to a help page stating its cause and its next safe action, and the whole path is offline: surfaces/ia.py imports no networking module, the help text is a literal table inside the module, and the page renders with the model backend unset and with no network reachable (APP-03 fixture, OfflineHelpPanel populated consideration)."
    - "An unknown or unrecognized error code renders the exact fallback sentence 'No additional help is available for this yet.' with HTTP 200, never a broken link, never a 404, and never a traceback (OfflineHelpPanel error consideration)."
    - "Help bodies are fixed pre-written sentences with no dynamic truncation, so no help text is ever shortened, elided, or cut mid-word by the surface that renders it (OfflineHelpPanel long-text consideration)."
    - "Each of the twelve ia.* codes routes to exactly one help page and each help page names exactly one code, asserted as a bijection over IA_HELP_CODES rather than spot-checked."
    - "A code that is syntactically outside the ia.* namespace, contains a path separator, or exceeds the bounded pattern never reaches the lookup: HELP_GET_RE's character class refuses it at dispatch and the daemon answers 404 without the handler running."
    - "The help route is one new stem-parameterised entry in the shipped ROUTES tuple with its ROUTE_CLI twin, so the shipped check_route_cli_inventory passes unchanged and no second router exists."
  prohibitions:
    - statement: "Help must not require a network connection, a hosted model, or a configured agent; a help path that fails exactly when connectivity fails is help that is absent when it is needed."
      status: kept
      verification: flagged-unverified
    - statement: "A model-generated elaboration must not be presented as the baseline help text or shown before it; the offline entry is always first and always complete on its own."
      status: kept
      verification: flagged-unverified
    - statement: "A help page must not state that generated help is unavailable when nothing ever tried to generate it, because a status line nobody measured is a fabricated status line."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "surfaces/ia.py gains HELP_TABLE, HELP_FALLBACK_COPY, and help_entry"
    - "surfaces/daemon.py gains HELP_GET_RE, the ('GET', HELP_GET_RE, 'handle_help_get') route entry, its ROUTE_CLI twin, and handle_help_get"
    - "surfaces/cli.py gains add_parser('help-code') with set_defaults(fn=cmd_help_code)"
    - "tests/ia_route_roundtrip.py gains check_help_route_bijection, check_help_unknown_code, and check_help_is_offline"
  key_links:
    - "HELP_GET_RE's character class is the security boundary, not a convenience. The pattern r'^/help/(?P<code>[a-z0-9_.]{1,64})$' cannot match a path separator, a percent escape, or an unbounded string, so a traversal attempt is refused by the dispatcher before handle_help_get runs and before any lookup key is constructed."
    - "The bijection assertion has to run over IA_HELP_CODES rather than over a hand-written list in the test, or a code added to the tuple later without a help entry passes the test that exists to catch exactly that."
    - "The offline proof must assert the absence of networking imports structurally as well as behaviourally. A behavioural test on a machine that happens to be offline proves nothing about a machine that is online, and a machine that is online cannot prove the negative by observation."
---

<objective>
Give every named error state this phase can produce a local, offline page that
says what happened and what to do next.

`REQUIREMENTS.md` APP-03 requires that "help is offline and routes from named
error codes". `16B-RESEARCH.md` Pitfall 5 names the failure mode by name: a
help path that reaches for the model adapter becomes unavailable exactly when
network or model access is the thing that broke. The baseline built here is a
literal table inside `surfaces/ia.py`, read with no file open and no socket, and
the whole route is proven with the model backend unset.

Decisions already made, cited, and never re-derived here:

- **`16B-DECISIONS.md` `## D-16B-1`**: `HELP_GET_RE = re.compile(r"^/help/(?P<code>[a-z0-9_.]{1,64})$")`,
  appended to the trailing stem-parameterised block of `ROUTES`.
- **`16B-DECISIONS.md` `## D-16B-3`**: `/help/<code>` maps to a new CLI command
  named `help-code`.
- **`16B-UI-SPEC.md` "Offline Help and Error-Code Routing Contract"**, the whole
  four-row table, binding verbatim, including the exact fallback sentence.
- **`16B-RESEARCH.md` Don't Hand-Roll**, the "Offline help content" row: a
  bundled local error-code-keyed lookup table following the shipped
  `SETTINGS_CODES` and `LINT_CODES` dotted-code precedent, never a hosted help
  site or a network-fetched FAQ.
- **`16B-PATTERNS.md`**, the "Offline help lookup table" pattern assignment:
  build the code list the same set-then-sorted-tuple way `SETTINGS_CODES` does,
  provably sorted and duplicate-free.

Purpose: make every error in this phase's surface end at a sentence a learner
can act on, with no dependency that can be down.
Output: one help table, one route, one CLI command, three tests.
</objective>

<context>
@.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-PATTERNS.md
@.planning/PLANNING-DIRECTIVES.md
@surfaces/ia.py
@surfaces/daemon.py
@surfaces/settings.py
@tests/ia_route_roundtrip.py
</context>

## Artifacts this phase produces (plan 16B-03 share)

New symbols introduced by this plan, and by nothing earlier:

- `surfaces/ia.py`: `HELP_TABLE`, `HELP_FALLBACK_COPY`, `help_entry`,
  `cmd_help_code`.
- `surfaces/daemon.py`: `HELP_GET_RE`, the route entry
  `("GET", HELP_GET_RE, "handle_help_get")`, the `ROUTE_CLI` entry
  `("GET", HELP_GET_RE): "help-code"`, and `handle_help_get`.
- `surfaces/cli.py`: `add_parser("help-code")` with
  `set_defaults(fn=cmd_help_code)`.
- `tests/ia_route_roundtrip.py`: `check_help_route_bijection`,
  `check_help_unknown_code`, `check_help_is_offline`.

The phase-wide symbol union is repeated in `16B-01-PLAN.md`.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the twelve help entries and the unknown-code fallback</name>
  <files>surfaces/ia.py, tests/ia_route_roundtrip.py</files>
  <behavior>
    - `help_entry("ia.activity_unavailable")` returns a dict with keys `code`,
      `title`, `cause`, `next_action`, and `known`, with `known` True.
    - `help_entry("ia.not_a_real_code")` returns the same key set with `known`
      False, `cause` equal to `HELP_FALLBACK_COPY`, and `next_action` an empty
      string.
    - `help_entry("")` and `help_entry(None)` both return the unknown shape and
      raise nothing.
    - Every member of `IA_HELP_CODES` has an entry in `HELP_TABLE` and every key
      of `HELP_TABLE` is a member of `IA_HELP_CODES`.
  </behavior>
  <read_first>
- `surfaces/ia.py` as it stands after plan 16B-02, in full, in particular
  `IA_HELP_CODES` and `DEGRADED_STATES`.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the
  "Degraded-State Matrix" table in full (its eight rows are the cause and
  next-action text for eight of the twelve codes) and the "Offline Help and
  Error-Code Routing Contract" table in full.
- `surfaces/settings.py` lines 34 to 42, `SETTINGS_CODES`, for the
  set-then-sorted-tuple shape.
- `tests/ia_route_roundtrip.py` as it stands after plan 16B-02.
  </read_first>
  <action>
1. Add `HELP_FALLBACK_COPY` to `surfaces/ia.py` as the exact literal string
   `No additional help is available for this yet.`

2. Add `HELP_TABLE`, a dict whose keys are exactly the twelve members of
   `IA_HELP_CODES` and whose values are dicts with exactly the keys `title`,
   `cause`, and `next_action`. Use these values verbatim; the `cause` text for
   the eight degraded-state codes is the Degraded-State Matrix's own copy, so it
   is transcribed rather than rewritten.

   - `ia.activity_unavailable`: title `Activity is not available yet`; cause
     `Activity isn't available yet in this build. Check back after your next update.`;
     next_action `Keep using Learn, Practice, Test, and Evidence. Nothing else is affected.`
   - `ia.agent_unavailable`: title `Generated help is unavailable`; cause
     `Generated help is unavailable. You can keep learning with the lesson and authored hints.`;
     next_action `Continue the authored loop. Reading, scoring, hints, evidence, and reports do not need a model.`
   - `ia.cancelled`: title `You cancelled this`; cause
     `Cancelled. Partial results are marked below and were not saved as final.`;
     next_action `Resume the same operation, or discard the partial results explicitly.`
   - `ia.course_corrupted`: title `A course record could not be read`; cause
     `This course's full record couldn't be loaded. Showing its last valid overview.`;
     next_action `Open the last valid overview, or open the course's files directly.`
   - `ia.crash_recovered`: title `Your last position was restored`; cause
     `Restored your last saved position. Nothing was lost since your last saved step.`;
     next_action `Continue where the resume cue points.`
   - `ia.disk_full`: title `A save could not complete`; cause
     `This save could not complete (disk full or interrupted). Your previous version is intact. Free up space and try again.`;
     next_action `Free disk space, then retry the save. The previous accepted version stays open and usable meanwhile.`
   - `ia.future_schema`: title `A file came from a newer version`; cause
     `This file was saved by a newer version of itembank. The parts itembank recognizes are shown below; nothing is changed or deleted.`;
     next_action `Continue viewing the recognized parts, or update itembank to see the rest.`
   - `ia.offline`: title `You are offline`; cause
     `You're offline. Reading, practice, scoring, hints, and evidence keep working. Anything that needs a network connection is marked unavailable below.`;
     next_action `Keep working. Nothing local is blocked by being offline.`
   - `ia.permission_denied`: title `A folder could not be read`; cause
     `itembank could not access a folder it was given. Check that the folder is still shared with itembank, then try again.`;
     next_action `Re-grant access to that folder, or continue with the rest of the course, which is unaffected.`
   - `ia.route_not_found`: title `That link does not resolve`; cause
     `That address does not name anything itembank can open. The thing it pointed at may have been renamed, moved, or removed.`;
     next_action `Go back to the course overview, or open the course shelf and pick the course again.`
   - `ia.sample_course_removed`: title `The sample course was removed`; cause
     `The sample course and its bundled files were removed from this install.`;
     next_action `Bind a source to create your first real course, or replay the walkthrough from Help.`
   - `ia.walkthrough_unavailable`: title `The walkthrough could not start`; cause
     `The walkthrough content could not be read on this install. Everything else works normally.`;
     next_action `Use the course shelf directly. The walkthrough can be replayed from Help after the next update.`

   Note in a comment above the table that the `ia.permission_denied` cause here
   is the code-page form with no path in it at all, and that the banner form
   which substitutes a bank-author-written basename is built by
   `degraded_banner` in plan 16B-08, per D9. Neither form ever carries a
   resolved absolute path.

3. Add `def help_entry(code):` with a docstring stating that it is a pure
   in-memory lookup, that it never reads a file and never opens a socket, and
   that an unrecognized code is answered rather than refused. Behavior:

   - When `code` is a string and a key of `HELP_TABLE`, return
     `{"code": code, "known": True, "title": ..., "cause": ..., "next_action": ...}`.
   - Otherwise return
     `{"code": code if isinstance(code, str) else "", "known": False,
       "title": "No help entry yet", "cause": HELP_FALLBACK_COPY,
       "next_action": ""}`.
   - Raise nothing for any input, including `None`, an integer, or an empty
     string.

4. Add `def cmd_help_code(a):` printing
   `json.dumps(help_entry(a.code), ensure_ascii=False, indent=2)`.

5. Add `check_help_table_shape()` to `tests/ia_route_roundtrip.py` asserting the
   four behaviors in this task's `<behavior>` block, plus:
   - `sorted(ia.HELP_TABLE) == list(ia.IA_HELP_CODES)`, so the table is provably
     complete and duplicate-free against the tuple rather than against a list
     written in the test.
   - Every `cause` and every `next_action` string is non-empty for every known
     code.
   - `ia.HELP_FALLBACK_COPY` equals the literal
     `No additional help is available for this yet.`
   - Every one of the eight `ia.DEGRADED_STATES` members has a corresponding
     help code in `IA_HELP_CODES`, mapped by the rule that `crash` maps to
     `ia.crash_recovered` and every other state `s` maps to `"ia." + s`.

   Update `main()` to run seven checks and print
   `"IA ROUTES: 7 passed, 0 failed"`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_route_roundtrip.py</automated>
Expected: final line `IA ROUTES: 7 passed, 0 failed`, exit 0. The degraded state
this task proves is the unknown-code path: `help_entry` answers rather than
raises for `None`, `""`, `0`, and an unrecognized dotted string.
  </verify>
  <acceptance_criteria>
- `python tests/ia_route_roundtrip.py` exits 0 with final line
  `IA ROUTES: 7 passed, 0 failed`.
- `python -c "import sys; sys.path.insert(0,'.'); from surfaces import ia; print(len(ia.HELP_TABLE), sorted(ia.HELP_TABLE)==list(ia.IA_HELP_CODES), ia.help_entry('nope')['cause'])"`
  prints exactly
  `12 True No additional help is available for this yet.`
- `ia.help_entry(None)["known"]` is `False` and the call raises nothing.
- Every `HELP_TABLE` value has exactly the keys `title`, `cause`, and
  `next_action`.
- The eight degraded-state codes carry the Degraded-State Matrix copy verbatim,
  spot-asserted for `ia.offline` and `ia.disk_full` with a literal string
  comparison in the test.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">A literal table and a pure lookup. The code
  namespace is additive and no consumer exists outside this phase yet.</reversibility>
  <done>Twelve codes each have a cause sentence and a next safe action, and an
  unknown code has a sentence too.</done>
</task>

<task type="auto">
  <name>Task 2: GET /help/&lt;code&gt; and its CLI twin</name>
  <files>surfaces/daemon.py, surfaces/cli.py, tests/ia_route_roundtrip.py</files>
  <read_first>
- `surfaces/daemon.py` lines 180 to 260, the existing `*_RE` regex constants and
  the `ROUTES` tuple as it stands after plan 16B-02, so the new regex is defined
  beside its siblings and the new entry is appended to the trailing block.
- `surfaces/daemon.py`, `handle_activity_get` as written by plan 16B-02, the
  exact handler shape this one copies.
- `surfaces/daemon.py`, `send_not_found` and `send_error`, for the shipped
  no-path-in-an-error-body discipline.
- `surfaces/presentation.py` lines 281 to 342, `surface_shell` and
  `state_panel`.
- `surfaces/cli.py`, the `add_parser("activity")` registration written by plan
  16B-02, the exact shape this one copies.
  </read_first>
  <action>
1. Add to `surfaces/daemon.py`, beside the other `*_RE` constants:

```
HELP_GET_RE = re.compile(r"^/help/(?P<code>[a-z0-9_.]{1,64})$")
```

   With a comment stating that the bounded character class is the path-traversal
   refusal: a code cannot contain a separator, a percent escape, or an unbounded
   run, so a traversal attempt never reaches the handler.

2. Append exactly one entry to the trailing stem-parameterised block of
   `ROUTES`, after `("POST", DAY_EDIT_RE, "handle_day_edit"),`:

```
    ("GET", HELP_GET_RE, "handle_help_get"),
```

   And exactly one entry to `ROUTE_CLI`:

```
    ("GET", HELP_GET_RE): "help-code",
```

3. Add `handle_help_get(handler, code)` immediately after
   `handle_activity_get`. Its docstring states that the whole lookup is local
   and in memory and that an unknown code is a 200 with the fallback sentence,
   never a 404. Behavior:

   - `entry = ia.help_entry(code)`.
   - Body is `<p class="help-cause">` with the escaped `cause`, then, only when
     `entry["next_action"]` is non-empty, `<p class="help-next">` with the
     escaped `next_action`, then a `<p class="help-code">` carrying
     `Error code: {code}` with the code escaped.
   - Render through
     `presentation.surface_shell(entry["title"], body, theme_css=..., back={"href": "/", "label": "Back to courses"})`
     and send with `handler.send_html`.
   - Return status 200 in every case, including an unknown code.

4. Register the CLI twin in `surfaces/cli.py` beside the `activity`
   registration:

```
    s = sub.add_parser("help-code", help="print the offline help entry for one "
                       "named error code")
    s.add_argument("code")
    s.set_defaults(fn=cmd_help_code)
```

   Add `cmd_help_code` to the `from surfaces.ia import ...` import.

5. Add `check_help_route_bijection()` to `tests/ia_route_roundtrip.py`. It
   starts one real daemon and, for every member of `ia.IA_HELP_CODES`:
   - `GET /help/<code>` returns 200.
   - The body contains the entry's exact `cause` string.
   - The body contains the literal `Error code: <code>`.
   - The body contains no other member of `IA_HELP_CODES` in an
     `Error code:` line, so each page names exactly one code.

   It then asserts the reverse direction: the set of codes reachable through the
   route equals `set(ia.IA_HELP_CODES)`.

6. Add `check_help_unknown_code()`. Against the same daemon:
   - `GET /help/ia.no_such_code` returns 200 and its body contains
     `No additional help is available for this yet.`
   - `GET /help/UPPERCASE` returns 404, because the regex character class
     refuses it at dispatch.
   - `GET /help/..%2fetc%2fpasswd` returns 404.
   - `GET /help/a/b` returns 404.
   - No 404 body contains a filesystem path, asserted by checking the response
     body contains neither `os.sep` runs of length two nor the string
     `Traceback`.

7. Update `main()` to run nine checks and print
   `"IA ROUTES: 9 passed, 0 failed"`. Run:

```
python tests/ia_route_roundtrip.py
python tests/daemon_roundtrip.py
python itembank.py help-code ia.offline
```

   Expected: exit 0, exit 0, and the third printing a JSON object whose `cause`
   begins `You're offline.`

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_route_roundtrip.py && python tests/daemon_roundtrip.py</automated>
Expected: `IA ROUTES: 9 passed, 0 failed` and exit 0, then exit 0. The degraded
state this task proves is the unknown and malformed code path: an unrecognized
dotted code is a 200 carrying the fallback sentence, and an uppercase, nested,
or escaped-traversal path is a 404 whose body carries no filesystem path.
  </verify>
  <acceptance_criteria>
- `python tests/ia_route_roundtrip.py` exits 0 with final line
  `IA ROUTES: 9 passed, 0 failed`.
- `python tests/daemon_roundtrip.py` exits 0, proving
  `check_route_cli_inventory` still passes with the new route and its twin.
- Every one of the twelve codes returns 200 and its page carries that code's
  exact `cause` string and the line `Error code: <code>`.
- `GET /help/ia.no_such_code` returns 200 with
  `No additional help is available for this yet.`
- `GET /help/UPPERCASE`, `GET /help/..%2fetc%2fpasswd`, and `GET /help/a/b` each
  return 404 and no 404 body contains `Traceback`.
- `python itembank.py help-code ia.offline` exits 0 and prints a JSON object
  whose `cause` value begins with `You're offline.`
- `python itembank.py help-code not.a.code` exits 0 and prints `"known": false`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="costly">The `/help/<code>` route literal and the
  `ia.*` code namespace become a published surface that banners, summaries, and
  later phases link to. The pattern shape was settled by D-16B-1 and the
  namespace by the shipped dotted-code precedent, so neither is decided
  here.</reversibility>
  <done>Twelve codes each resolve to their own page over HTTP, an unknown code
  resolves to a sentence, and a malformed one resolves to a path-free 404.</done>
</task>

<task type="auto">
  <name>Task 3: prove the help path is offline, structurally and behaviourally</name>
  <files>tests/ia_route_roundtrip.py</files>
  <read_first>
- `surfaces/ia.py` in full as it stands after Task 1.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md`, Pitfall 5
  in full, including its Warning signs line.
- `.planning/REQUIREMENTS.md`, `APP-03`'s Fixture sentence verbatim, in
  particular "with no roots granted, no agent configured, and the network
  disabled, asserting offline help routes from named error codes".
- `schemas/settings.schema.json`, the `model_backend` property, for the value
  that means no backend is configured.
  </read_first>
  <action>
1. Add `check_help_is_offline()` to `tests/ia_route_roundtrip.py`. It proves the
   claim two ways, because neither way is sufficient alone.

   Structurally, by reading `surfaces/ia.py`'s source text with the comment
   lines stripped first (so a comment naming a module cannot invalidate the
   check):
   - None of the literal substrings `import urllib`, `import http.client`,
     `import socket`, `import requests`, `from urllib`, `urlopen`, or
     `model_adapter` appears in the stripped source.
   - Fail with
     `"surfaces/ia.py reached for a networking or model module: %s" % found`.

   Behaviourally, with a real daemon started in a temp directory prepared so
   that no source root is granted and no model backend is configured:
   - Write an `itembank.json` into the temp directory containing only
     `{"model_backend": "none"}` if the schema's `model_backend` enum admits
     `"none"`; otherwise write no `itembank.json` at all and record in the
     summary which of the two was used and why.
   - Start the daemon with the environment variable `ITEMBANK_NO_NETWORK=1`
     set, and assert that `GET /help/ia.offline` still returns 200 with its
     exact cause sentence. The variable is not read by any shipped code; it is
     set so that a future networking addition to this path fails a test that
     already exists rather than passing unnoticed.
   - Assert the same request succeeds with the process's default proxy
     environment cleared (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY` removed from
     the child environment).

2. Add one negative-control assertion, so the structural check is known to be
   able to fail: construct the stripped-source scan as a helper
   `_scan_for_network(text)` and assert in the test that
   `_scan_for_network("import socket")` returns a non-empty list. A check that
   has never been observed failing is a check nobody has tested.

3. Update `main()` to run ten checks and print
   `"IA ROUTES: 10 passed, 0 failed"`.

4. Run the full suite and the guard:

```
python tests/ia_route_roundtrip.py
for t in tests/*.py; do python "$t" || exit 1; done
python itembank.py guard .
```

   Expected: `IA ROUTES: 10 passed, 0 failed` and exit 0; exit 0; and
   `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/ia_route_roundtrip.py</automated>
Expected: final line `IA ROUTES: 10 passed, 0 failed`, exit 0. The degraded
state this task proves is the whole point of the task: help resolves with no
network, no proxy, and no configured model backend, and the structural scan is
demonstrated able to fail through its negative control.
  </verify>
  <acceptance_criteria>
- `python tests/ia_route_roundtrip.py` exits 0 with final line
  `IA ROUTES: 10 passed, 0 failed`.
- `_scan_for_network` returns a non-empty list for the input `import socket`,
  proving the structural check can fail.
- `_scan_for_network` returns an empty list for `surfaces/ia.py`'s
  comment-stripped source.
- `GET /help/ia.offline` returns 200 with its exact cause sentence in a daemon
  started with no granted root, no configured model backend, and the proxy
  environment cleared.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` reports `0 offending files`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Test coverage only.</reversibility>
  <done>The offline claim is proven by a scan that is demonstrated able to fail
  and by a request served with nothing configured.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| URL path segment to lookup key | `<code>` is attacker-influenced input under `--lan` and is used to select content. |
| help content to learner | Help text is what a learner acts on during a failure, so a wrong or absent sentence has real cost. |
| error body to client | A 404 or 500 on this route must not carry a path or a traceback. |
| module import graph to availability claim | The offline promise is only as good as what the module can reach. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16B-03-01 | Tampering | path traversal through the `<code>` segment | high | mitigate | `HELP_GET_RE`'s class is `[a-z0-9_.]{1,64}`, which admits no separator, no percent escape, and no unbounded run; the dispatcher refuses a non-matching path with 404 before `handle_help_get` runs, and Task 2 asserts three traversal shapes return 404. |
| T-16B-03-02 | Information Disclosure | a filesystem path or traceback in a help 404 or 500 body | high | mitigate | The route uses the shipped `send_error` and `send_not_found`, whose docstrings state they never emit a path or a traceback (T-2-05); Task 2 asserts no 404 body contains `Traceback`. |
| T-16B-03-03 | Denial of Service | help becoming unavailable exactly when network or model access fails | high | mitigate | `help_entry` is a pure in-memory lookup; `check_help_is_offline` asserts structurally that `surfaces/ia.py` imports no networking or model-adapter module and behaviourally that the route serves with no backend configured and the proxy environment cleared, with a negative control proving the scan can fail. |
| T-16B-03-04 | Repudiation | a help page stating that generated help is unavailable when nothing tried to generate it | medium | mitigate | 16B renders the offline baseline only and renders no generated-synthesis container at all; the `ia.agent_unavailable` sentence is a code page a real degraded state links to, and the banner that states it is built by plan 16B-08 where a model-dependent surface actually degrades. |
| T-16B-03-05 | Spoofing | a route added outside the four parallel structures | high | mitigate | One `ROUTES` entry plus one `ROUTE_CLI` entry; `check_route_cli_inventory` and `check_route_order_is_load_bearing` both run in this plan's verify. |
| T-16B-03-06 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; the help table is literal strings in a standard-library-only module. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
| T-16B-03-07 | Information Disclosure | help copy echoing a resolved absolute path | medium | mitigate | The `ia.permission_denied` code page carries no path at all; only the banner form substitutes a bank-author-written basename, and that substitution lives in plan 16B-08 under D9. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- **No model-backed elaboration layer.** No call to `model_adapter`, no
  generated-synthesis container, no `Generated synthesis` label rendered by this
  plan. The UI-SPEC reserves that layer as an optional enhancement; building it
  needs a backend call this plan is forbidden to make, and rendering an empty
  labelled container would assert a status nothing measured.
- No help content for codes outside the `ia.*` namespace. `SETTINGS_CODES`,
  `LINT_CODES`, and `GIFT_CODES` keep their own existing surfaces; wiring them
  into `/help/<code>` is a later phase's choice and is not assumed here.
- No search over help text, no help index page, no `/help` without a code.
- No degraded-state banner. Plan 16B-08 owns `degraded_banner` and the eight
  banner renderings; this plan owns only the code pages they link to.
- No new settings key. `network_egress` is plan 16B-06's.
- No new visual constant.
</out_of_scope>

<flagged_assumptions>
- **`ITEMBANK_NO_NETWORK=1` is read by no shipped code today.** It is set in the
  behavioural offline check as a tripwire for the future: if a later change
  makes this path reach the network, a test that already exists is the place
  that notices. If a reviewer prefers a real network sandbox, the substitute is
  running the check under a process with no route to a network, and the freeze
  record then states which form was used.

- **Whether `model_backend` admits a literal `"none"` value is read from the
  shipped schema at execution time, not asserted here.** Task 3 step 1 branches
  on it and requires the executor to record which branch ran and why, rather
  than guessing a value that may not validate.
</flagged_assumptions>

<summary_obligations>
`16B-03-SUMMARY.md` records: the final line of every command in every verify
block, verbatim; which of the two `model_backend` branches Task 3 step 1 took
and why; the observed non-empty result of the `_scan_for_network("import
socket")` negative control; the twelve codes confirmed reachable and the exact
count; whether any 404 body was found to contain a path; which truth was
verified by which command, with the command's actual stdout; and any deviation
from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16B-ia-modes-recovery-contract/16B-03-SUMMARY.md`
when done.
</output>
